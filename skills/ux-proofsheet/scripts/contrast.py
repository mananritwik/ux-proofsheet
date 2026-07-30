#!/usr/bin/env python3
"""
contrast.py — turn the design's own hex tokens into a quantified WCAG check.

ux-proofsheet extracts color tokens from Figma. This script computes the WCAG 2.1
contrast ratio for foreground/background hex pairs and reports pass/fail so the
accessibility findings are *measured*, not guessed ("#b50012 on #ffe8ea = 4.9:1,
passes AA normal; the disabled grey #798087 on #ffffff = 4.3:1, fails AA normal").

Thresholds (WCAG 2.1 AA):
  - Normal text   >= 4.5:1
  - Large text    >= 3.0:1   (>= 18.66px bold or >= 24px regular)
  - UI / graphics >= 3.0:1

Usage:
    # one pair
    python contrast.py "#b50012" "#ffe8ea"

    # many pairs from a file (one "fg bg [label]" per line; # comments allowed)
    python contrast.py --pairs pairs.txt

    # JSON out (for the skill to consume)
    python contrast.py "#798087" "#ffffff" --json

No third-party dependencies.
"""
import argparse
import json
import sys


def _to_rgb(hex_str):
    h = hex_str.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"not a hex color: {hex_str!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rel_luminance(rgb):
    def chan(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    """WCAG contrast ratio between two hex colors (>=1.0)."""
    l1 = _rel_luminance(_to_rgb(fg))
    l2 = _rel_luminance(_to_rgb(bg))
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def assess(fg, bg, label=None):
    r = ratio(fg, bg)
    return {
        "label": label,
        "fg": fg, "bg": bg, "ratio": r,
        "aa_normal": r >= 4.5,      # body text
        "aa_large": r >= 3.0,       # large text / UI / graphics
        "borderline": 4.5 > r >= 4.0,  # worth a manual look
    }


def _fmt(a):
    verdict = "PASS AA" if a["aa_normal"] else ("PASS AA (large/UI only)" if a["aa_large"] else "FAIL AA")
    flag = "  <-- borderline" if a["borderline"] else ""
    lab = f'{a["label"]}: ' if a["label"] else ""
    return f'{lab}{a["fg"]} on {a["bg"]} = {a["ratio"]}:1  {verdict}{flag}'


def main():
    ap = argparse.ArgumentParser(description="WCAG 2.1 contrast ratio checker for hex color pairs.")
    ap.add_argument("fg", nargs="?", help="foreground hex, e.g. #b50012")
    ap.add_argument("bg", nargs="?", help="background hex, e.g. #ffffff")
    ap.add_argument("--pairs", help="file of 'fg bg [label]' lines")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    results = []
    if args.pairs:
        with open(args.pairs, encoding="utf-8") as f:
            for line in f:
                line = line.split("#", 1)[0].strip() if not line.strip().startswith("#") else ""
                if not line:
                    continue
                parts = line.split()
                fg, bg = parts[0], parts[1]
                label = " ".join(parts[2:]) or None
                results.append(assess(fg, bg, label))
    elif args.fg and args.bg:
        results.append(assess(args.fg, args.bg))
    else:
        ap.error("provide FG and BG, or --pairs FILE")

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for a in results:
            print(_fmt(a))
        fails = [a for a in results if not a["aa_normal"]]
        if fails:
            print(f"\n{len(fails)} of {len(results)} fail AA for normal text.", file=sys.stderr)


if __name__ == "__main__":
    main()
