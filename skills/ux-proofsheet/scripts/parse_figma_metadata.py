#!/usr/bin/env python3
"""
parse_figma_metadata.py — triage large Figma get_metadata dumps.

Figma MCP get_metadata on a real board can be hundreds of KB and overflow
context. When the tool saves that payload to a file, run this script instead
of dumping the raw tree into the chat.

Extracts:
  - top-level / near-top FRAME and COMPONENT sets (id, name, type, depth)
  - text-layer annotations that look like designer notes (short strings,
    questions, TBD, "Old"/"New", etc.)

Usage:
    python parse_figma_metadata.py metadata.json
    python parse_figma_metadata.py metadata.json --max-depth 3 --json
    python parse_figma_metadata.py metadata.xml   # also accepts XML-ish dumps

No third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NOTE_HINT = re.compile(
    r"(?i)\b(tbd|todo|note|old|new|popup|mobile|wip|fix|question|\?)\b|"
    r"not ideal|needs? review"
)
FRAME_TYPES = {"FRAME", "COMPONENT", "COMPONENT_SET", "SECTION", "GROUP"}


def _load(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    # JSON object/array
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Sometimes the dump is JSONL or wrapped; try first {...} block
    m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # XML-ish / HTML-ish node dump: <frame id="..." name="...">
    nodes = []
    for tag, attrs in re.findall(r"<(\w+)([^>]*)>", text):
        id_m = re.search(r'\bid=["\']([^"\']+)["\']', attrs)
        name_m = re.search(r'\bname=["\']([^"\']+)["\']', attrs)
        if id_m or name_m:
            nodes.append({
                "type": tag.upper(),
                "id": id_m.group(1) if id_m else "",
                "name": name_m.group(1) if name_m else "",
            })
    if nodes:
        return {"document": {"children": nodes}}
    sys.exit(f"Could not parse {path} as JSON or simple node XML.")


def _walk(node, depth, max_depth, frames, notes, parent_name=""):
    if not isinstance(node, dict):
        return
    ntype = str(node.get("type") or node.get("typeName") or "").upper()
    nid = str(node.get("id") or node.get("nodeId") or "")
    name = str(node.get("name") or "")
    if depth <= max_depth and (ntype in FRAME_TYPES or (depth <= 2 and nid)):
        frames.append({
            "id": nid,
            "name": name,
            "type": ntype or "UNKNOWN",
            "depth": depth,
            "parent": parent_name,
        })
    if ntype == "TEXT" or (name and NOTE_HINT.search(name)):
        chars = node.get("characters") or node.get("text") or name
        if isinstance(chars, str) and chars.strip():
            snippet = chars.strip().replace("\n", " ")
            if len(snippet) <= 240 and (NOTE_HINT.search(snippet) or ntype == "TEXT"):
                notes.append({"id": nid, "name": name, "text": snippet[:240]})
    kids = node.get("children") or node.get("nodes") or []
    if isinstance(kids, dict):
        kids = list(kids.values())
    for child in kids:
        _walk(child, depth + 1, max_depth, frames, notes, name or parent_name)


def parse(data, max_depth=4):
    frames, notes = [], []
    root = data
    if isinstance(data, dict):
        for key in ("document", "nodes", "result", "metadata"):
            if key in data and isinstance(data[key], (dict, list)):
                root = data[key]
                break
    if isinstance(root, list):
        for item in root:
            _walk(item, 0, max_depth, frames, notes)
    else:
        _walk(root, 0, max_depth, frames, notes)
    # de-dupe notes by text
    seen, uniq_notes = set(), []
    for n in notes:
        key = n["text"]
        if key in seen:
            continue
        seen.add(key)
        uniq_notes.append(n)
    return {"frames": frames, "annotations": uniq_notes[:40]}


def main():
    ap = argparse.ArgumentParser(description="Triage large Figma metadata dumps.")
    ap.add_argument("path", type=Path, help="metadata JSON/XML file from get_metadata")
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    result = parse(_load(args.path), max_depth=args.max_depth)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Frames/components (depth ≤ {args.max_depth}): {len(result['frames'])}")
    for f in result["frames"][:80]:
        pad = "  " * min(f["depth"], 6)
        print(f"{pad}[{f['type']}] {f['name'] or '(unnamed)'}  id={f['id']}")
    if len(result["frames"]) > 80:
        print(f"  … +{len(result['frames']) - 80} more")
    print(f"\nAnnotation-like text layers: {len(result['annotations'])}")
    for n in result["annotations"]:
        print(f"  · {n['text'][:120]}  (id={n['id']})")


if __name__ == "__main__":
    main()
