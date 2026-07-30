#!/usr/bin/env python3
"""
embed_images.py — make a ux-proofsheet report durable.

Mobbin thumbnail URLs and Figma asset URLs are short-lived: a saved HTML report
will show broken images once they expire. This script downloads every remote
<img src="..."> in an HTML file and rewrites it as an inlined base64 data URI, so
the report is fully self-contained and survives forever.

It deliberately leaves anchor hrefs (e.g. the permanent mobbin.com/screens/...
"View" links) untouched — those don't expire and should stay clickable.

Usage:
    python embed_images.py report.html                 # writes report.embedded.html
    python embed_images.py report.html -o final.html   # explicit output
    python embed_images.py report.html --in-place       # overwrite input

No third-party dependencies — standard library only.
"""
import argparse
import base64
import mimetypes
import re
import sys
import urllib.request

IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc\s*=\s*)(["\'])(.*?)\2', re.IGNORECASE)

# content-type -> extension fallback when the URL has no useful suffix
CT_EXT = {
    "image/webp": ".webp", "image/jpeg": ".jpg", "image/png": ".png",
    "image/gif": ".gif", "image/svg+xml": ".svg",
}


def fetch_as_data_uri(url, timeout=30):
    """Download url and return a base64 data: URI, or None on failure."""
    if url.startswith("data:"):
        return None  # already inline
    if not url.startswith(("http://", "https://")):
        return None  # local/relative path — leave it alone
    req = urllib.request.Request(url, headers={"User-Agent": "ux-proofsheet/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ctype = resp.headers.get("Content-Type", "").split(";")[0].strip()
    if not ctype or not ctype.startswith("image/"):
        guessed, _ = mimetypes.guess_type(url)
        ctype = guessed or "image/webp"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{ctype};base64,{b64}"


def embed(html):
    stats = {"embedded": 0, "skipped": 0, "failed": 0}

    def repl(m):
        prefix, quote, url = m.group(1), m.group(2), m.group(3)
        try:
            data_uri = fetch_as_data_uri(url)
        except Exception as e:  # noqa: BLE001 - report and keep the original URL
            sys.stderr.write(f"  ! failed: {url[:70]}... ({e})\n")
            stats["failed"] += 1
            return m.group(0)
        if data_uri is None:
            stats["skipped"] += 1
            return m.group(0)
        stats["embedded"] += 1
        sys.stderr.write(f"  + embedded: {url[:70]}...\n")
        return f"{prefix}{quote}{data_uri}{quote}"

    return IMG_SRC.sub(repl, html), stats


def main():
    ap = argparse.ArgumentParser(description="Inline remote <img> sources as base64 for durable HTML reports.")
    ap.add_argument("input", help="HTML file to process")
    ap.add_argument("-o", "--output", help="output path (default: <input>.embedded.html)")
    ap.add_argument("--in-place", action="store_true", help="overwrite the input file")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        html = f.read()

    out_html, stats = embed(html)

    if args.in_place:
        out_path = args.input
    elif args.output:
        out_path = args.output
    else:
        out_path = re.sub(r"\.html?$", "", args.input) + ".embedded.html"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    sys.stderr.write(
        f"\nDone. embedded={stats['embedded']} skipped={stats['skipped']} "
        f"failed={stats['failed']}\nWrote {out_path}\n"
    )
    if stats["failed"]:
        sys.stderr.write("Note: failed images kept their original (expiring) URLs.\n")


if __name__ == "__main__":
    main()
