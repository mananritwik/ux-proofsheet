#!/usr/bin/env python3
"""
token_check.py: measure a design's type ramp and spacing scale against
Material 3 and Apple HIG baselines.

ux-proofsheet already reads the design from Figma. This script turns that read
into numbers: the type ramp the design actually uses, its step ratio, the spacing
scale and its base unit, plus findings for off-scale values, crowded steps, and
jumps. Deterministic and offline. Baseline numbers come from
../references/token-baselines.json (each one cited in token-baselines.md).

Accepted input (save the Figma MCP output to a file first):
  - get_variable_defs  flat JSON: {"Body/Large": "Font(... size: 16, lineHeight: 24 ...)",
                                   "spacing/md": "12", "color/brand": "#1069CF"}
  - node tree JSON     Figma REST / plugin shape: TEXT nodes with style.fontSize,
                       auto-layout frames with itemSpacing / padding*
  - get_design_context code (TSX/HTML with Tailwind or CSS): text-[16px],
                       leading-[24px], gap-[12px], p-4, font-size: 16px, ...
  - get_metadata       XML with x/y/width/height: spacing only, inferred from the
                       gaps between sibling layers (no font sizes in metadata)
Pass several files to merge them (e.g. variables + design context).

Usage:
    python token_check.py fixtures/home-nodes.json
    python token_check.py vars.json context.tsx --baseline hig_ios --json
    python token_check.py nodes.json --file-url "https://www.figma.com/design/KEY/Name"

No third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINES_PATH = HERE.parent / "references" / "token-baselines.json"

# Tool heuristics (not baseline values; see token-baselines.md).
CROWDED_RATIO = 1.07
BASE_UNIT_SHARE = 0.8
SPACING_GAP_RATIO = 2.0
NAMED_RATIOS = [
    ("Minor Second", 1.067), ("Major Second", 1.125), ("Minor Third", 1.2),
    ("Major Third", 1.25), ("Perfect Fourth", 1.333), ("Augmented Fourth", 1.414),
    ("Perfect Fifth", 1.5), ("Golden", 1.618),
]
SPACING_NAME = re.compile(r"(?i)spac|gap|padding|margin|inset|gutter|space")
FONT_SIZE_NAME = re.compile(r"(?i)font.?size|text.?size|type.?size")
SPACING_KEYS = ("itemSpacing", "counterAxisSpacing", "paddingLeft", "paddingRight",
                "paddingTop", "paddingBottom")


def load_baselines(path: Path = BASELINES_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _num(v):
    try:
        f = float(str(v).strip().rstrip("px").rstrip("pt"))
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, 2)


def _clean(v: float):
    """16.0 -> 16, 15.5 -> 15.5 (for display)."""
    return int(v) if float(v).is_integer() else v


# --------------------------------------------------------------------------- #
# Extraction: every reader returns (text_samples, spacing_samples).
# text sample:    {"size": float, "line_height": float|None, "name": str, "node": str}
# spacing sample: {"value": float, "name": str, "node": str, "source": str}
# --------------------------------------------------------------------------- #

FONT_RE = re.compile(r"Font\((?P<body>[^)]*)\)")


def _parse_font_string(s: str):
    m = FONT_RE.search(s)
    if not m:
        return None
    fields = dict(
        (k.strip(), v.strip().strip('"'))
        for k, v in (p.split(":", 1) for p in m.group("body").split(",") if ":" in p)
    )
    size = _num(fields.get("size"))
    if not size:
        return None
    lh = _num(fields.get("lineHeight"))
    # Figma sometimes reports line height as a percent of the font size.
    if lh is not None and lh > size * 3:
        lh = round(size * lh / 100, 2)
    return size, lh


def from_variable_defs(data: dict):
    texts, spacing = [], []
    for name, value in data.items():
        if isinstance(value, str) and "Font(" in value:
            parsed = _parse_font_string(value)
            if parsed:
                texts.append({"size": parsed[0], "line_height": parsed[1],
                              "name": name, "node": ""})
            continue
        n = _num(value)
        if n is None:
            continue
        if FONT_SIZE_NAME.search(name):
            texts.append({"size": n, "line_height": None, "name": name, "node": ""})
        elif SPACING_NAME.search(name) and n > 0:
            spacing.append({"value": n, "name": name, "node": "", "source": "variable"})
    return texts, spacing


def _line_height(node: dict, style: dict, size: float):
    if "lineHeightPx" in style:
        return _num(style["lineHeightPx"])
    lh = node.get("lineHeight") or style.get("lineHeight")
    if isinstance(lh, dict):
        unit = str(lh.get("unit", "")).upper()
        val = _num(lh.get("value"))
        if val is None:
            return None
        if unit == "PERCENT":
            return round(size * val / 100, 2)
        if unit == "PIXELS":
            return val
        return None
    return _num(lh)


def from_node_tree(root):
    texts, spacing = [], []

    def walk(node, parent_name=""):
        if isinstance(node, list):
            for item in node:
                walk(item, parent_name)
            return
        if not isinstance(node, dict):
            return
        ntype = str(node.get("type", "")).upper()
        nid = str(node.get("id", ""))
        name = str(node.get("name", "")) or parent_name
        style = node.get("style") if isinstance(node.get("style"), dict) else {}
        if ntype == "TEXT":
            size = _num(style.get("fontSize", node.get("fontSize")))
            if size:
                texts.append({"size": size, "line_height": _line_height(node, style, size),
                              "name": name, "node": nid})
        layout = str(node.get("layoutMode", "")).upper()
        if layout in ("HORIZONTAL", "VERTICAL"):
            kids = node.get("children") or []
            for key in SPACING_KEYS:
                v = _num(node.get(key))
                if not v or v <= 0:
                    continue
                if key == "itemSpacing" and len(kids) < 2:
                    continue  # a gap with nothing to separate never renders
                if key == "counterAxisSpacing" and node.get("layoutWrap") != "WRAP":
                    continue
                spacing.append({"value": v, "name": f"{name} · {key}", "node": nid,
                                "source": "auto-layout"})
        for child in node.get("children") or []:
            walk(child, name)

    for key in ("document", "nodes", "result"):
        if isinstance(root, dict) and isinstance(root.get(key), (dict, list)):
            root = root[key]
            break
    if isinstance(root, dict) and all(isinstance(v, dict) and "document" in v for v in root.values()):
        root = [v["document"] for v in root.values()]  # REST /nodes response
    walk(root)
    return texts, spacing


ARBITRARY = r"\[(-?\d+(?:\.\d+)?)px\]"
TW_SPACING = re.compile(
    r"(?<![\w-])(gap|gap-x|gap-y|space-x|space-y|p|px|py|pt|pb|pl|pr|ps|pe|"
    r"m|mx|my|mt|mb|ml|mr)-(?:" + ARBITRARY + r"|(\d+(?:\.5)?))(?![\w\[])"
)
TW_TEXT = re.compile(r"(?<![\w-])text-" + ARBITRARY)
TW_LEADING = re.compile(r"(?<![\w-])leading-" + ARBITRARY)
CSS_DECL = re.compile(
    r"(font-size|fontSize|line-height|lineHeight|gap|row-gap|column-gap|rowGap|columnGap|"
    r"padding(?:-\w+)?|padding(?:Top|Bottom|Left|Right)?|margin(?:-\w+)?|"
    r"margin(?:Top|Bottom|Left|Right)?)\s*:\s*['\"]?([\d.\spx]+)",
)
CLASS_ATTR = re.compile(r"class(?:Name)?\s*=\s*[{]?[\"'`]([^\"'`]+)[\"'`]")
DATA_NODE = re.compile(r"data-node-id\s*=\s*[\"']([^\"']+)[\"']")


def from_design_context(code: str):
    """Pull type and spacing values out of get_design_context code."""
    texts, spacing = [], []
    # Pair text size with leading inside the same class string.
    for m in CLASS_ATTR.finditer(code):
        classes = m.group(1)
        tail = code[m.end():m.end() + 200]
        head = code[max(0, m.start() - 200):m.start()]
        node_m = DATA_NODE.search(tail) or (list(DATA_NODE.finditer(head)) or [None])[-1]
        node = node_m.group(1) if node_m else ""
        sizes = [_num(x) for x in TW_TEXT.findall(classes)]
        leads = [_num(x) for x in TW_LEADING.findall(classes)]
        for s in sizes:
            if s:
                texts.append({"size": s, "line_height": leads[0] if leads else None,
                              "name": "class", "node": node})
        for prop, arb, scale in TW_SPACING.findall(classes):
            v = _num(arb) if arb else _num(float(scale) * 4)  # Tailwind: 1 unit = 4px
            if v and v > 0:
                spacing.append({"value": v, "name": prop, "node": node, "source": "code"})
    # Plain CSS / style objects.
    pending_size = None
    for prop, raw in CSS_DECL.findall(code):
        vals = [v for v in (_num(x) for x in raw.replace("px", " ").split()) if v]
        if not vals:
            continue
        p = prop.lower()
        if p in ("font-size", "fontsize"):
            pending_size = vals[0]
            texts.append({"size": vals[0], "line_height": None, "name": prop, "node": ""})
        elif p in ("line-height", "lineheight"):
            if pending_size and texts and texts[-1]["line_height"] is None and vals[0] > 3:
                texts[-1]["line_height"] = vals[0]
        else:
            for v in vals:
                if v > 0:
                    spacing.append({"value": v, "name": prop, "node": "", "source": "code"})
    return texts, spacing


def from_metadata_xml(text: str):
    """get_metadata XML: infer spacing from gaps between sibling layers."""
    spacing = []
    try:
        root = ET.fromstring(f"<root>{text}</root>")
    except ET.ParseError:
        return [], []

    def box(el):
        try:
            return tuple(float(el.attrib[k]) for k in ("x", "y", "width", "height"))
        except (KeyError, ValueError):
            return None

    def gaps(kids, axis):
        # axis 1 = vertical stack (sort by y), 0 = horizontal row (sort by x)
        ordered = sorted(kids, key=lambda kb: kb[1][axis])
        out = []
        for (ea, a), (eb, b) in zip(ordered, ordered[1:]):
            gap = b[axis] - (a[axis] + a[axis + 2])
            if gap < 0:
                return []  # overlap: not a clean stack along this axis
            out.append((round(gap, 2), eb))
        return out

    for parent in root.iter():
        kids = [(el, box(el)) for el in parent]
        kids = [(el, b) for el, b in kids if b]
        if len(kids) < 2:
            continue
        for axis in (1, 0):
            for gap, el in gaps(kids, axis):
                if gap > 0:
                    spacing.append({"value": gap, "name": el.attrib.get("name", ""),
                                    "node": el.attrib.get("id", ""), "source": "geometry"})
    return [], spacing


def read_inputs(paths):
    texts, spacing, kinds = [], [], []
    for path in paths:
        raw = Path(path).read_text(encoding="utf-8", errors="replace")
        stripped = raw.lstrip()
        data = None
        if stripped[:1] in "{[":
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                data = None
        if isinstance(data, dict) and isinstance(data.get("code"), str):
            t, s = from_design_context(data["code"]); kind = "design_context"
        elif isinstance(data, dict) and data and not any(
                isinstance(v, (dict, list)) for v in data.values()):
            t, s = from_variable_defs(data); kind = "variable_defs"
        elif data is not None:
            t, s = from_node_tree(data); kind = "node_tree"
        elif stripped.startswith("<") and re.search(r"\bx=\"", raw) and not CLASS_ATTR.search(raw):
            t, s = from_metadata_xml(raw); kind = "metadata_xml"
        else:
            t, s = from_design_context(raw); kind = "design_context"
        texts += t
        spacing += s
        kinds.append({"path": str(path), "kind": kind, "text_samples": len(t),
                      "spacing_samples": len(s)})
    return texts, spacing, kinds


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #

def nearest_named_ratio(r):
    if not r:
        return None
    return min(NAMED_RATIOS, key=lambda nr: abs(nr[1] - r))[0]


def baseline_sizes(b):
    return sorted({row["size"] for row in b["type_scale"]})


def max_step(sizes):
    return max(b / a for a, b in zip(sizes, sizes[1:]))


def nearest_styles(b, size):
    """Baseline styles at the closest size(s) below and above."""
    sizes = baseline_sizes(b)
    below = max((s for s in sizes if s < size), default=None)
    above = min((s for s in sizes if s > size), default=None)
    out = []
    for s in (below, above):
        if s is None:
            continue
        styles = [r["style"] for r in b["type_scale"] if r["size"] == s]
        out.append({"size": _clean(s), "styles": styles})
    return out


def analyze_type(texts, baselines, choice):
    if not texts:
        return None, []
    counts = Counter(t["size"] for t in texts)
    ramp = sorted(counts)
    lh = defaultdict(Counter)
    nodes = defaultdict(list)
    for t in texts:
        if t["line_height"]:
            lh[t["size"]][t["line_height"]] += 1
        if t["node"] and t["node"] not in nodes[t["size"]]:
            nodes[t["size"]].append(t["node"])
    steps = [round(b / a, 3) for a, b in zip(ramp, ramp[1:])]
    overall = round((ramp[-1] / ramp[0]) ** (1 / (len(ramp) - 1)), 3) if len(ramp) > 1 else None
    median = round(statistics.median(steps), 3) if steps else None

    fit = {}
    for key, b in baselines.items():
        bs = set(baseline_sizes(b))
        hits = sum(1 for s in ramp if s in bs)
        fit[key] = {"name": b["name"], "matched": hits, "of": len(ramp),
                    "share": round(hits / len(ramp), 2)}
    chosen = choice if choice in baselines else max(
        fit, key=lambda k: (fit[k]["share"], k == "material3"))
    b = baselines[chosen]
    bs = baseline_sizes(b)

    summary = {
        "ramp": [_clean(s) for s in ramp],
        "usage": {str(_clean(s)): counts[s] for s in ramp},
        "line_heights": {str(_clean(s)): [_clean(v) for v in sorted(lh[s])] for s in ramp if lh[s]},
        "steps": steps,
        "overall_ratio": overall,
        "median_step": median,
        "nearest_named_ratio": nearest_named_ratio(overall),
        "baseline_fit": fit,
        "baseline": chosen,
        "baseline_ratio": b.get("type_ratio"),
    }

    findings = []
    off = [s for s in ramp if s not in bs]
    if off:
        detail = []
        for s in off:
            detail.append({"size": _clean(s), "uses": counts[s], "nodes": nodes[s][:5],
                           "nearest": nearest_styles(b, s)})
        findings.append({
            "kind": "type_off_baseline",
            "severity": "medium" if len(off) >= 3 or sum(counts[s] for s in off) >= 5 else "low",
            "title": f"{len(off)} of {len(ramp)} text sizes are not {b['name']} sizes",
            "values": [_clean(s) for s in off],
            "detail": detail,
            "fix": "Snap each to the nearest baseline style: " + "; ".join(
                f"{_clean(d['size'])} -> " + " or ".join(
                    f"{n['size']} ({'/'.join(n['styles'])})" for n in d["nearest"])
                for d in detail),
            "source": b["type_source"],
        })

    crowded = []
    for (a, c), r in zip(zip(ramp, ramp[1:]), steps):
        if (r < CROWDED_RATIO or c - a <= 1) and not (a in bs and c in bs):
            crowded.append([_clean(a), _clean(c)])
    if crowded:
        chain = sorted({v for pair in crowded for v in pair})
        findings.append({
            "kind": "type_crowded",
            "severity": "medium" if len(chain) >= 3 else "low",
            "title": f"Crowded type steps: {' / '.join(str(v) for v in chain)} are too close "
                     "to read as different levels",
            "values": chain,
            "pairs": crowded,
            "nodes": [n for v in chain if v not in bs for n in nodes[v]][:5],
            "fix": "Collapse to fewer, clearly different sizes; keep the baseline sizes in this "
                   f"range ({', '.join(str(_clean(s)) for s in bs if chain[0] <= s <= chain[-1]) or 'none'}).",
            "source": baselines["material3"]["type_source"],
            "heuristic": f"adjacent sizes 1pt apart or under x{CROWDED_RATIO}, not both baseline "
                         "(tool threshold; M3 advises avoiding small differences)",
        })

    limit = max_step(bs)
    jumps = []
    for (a, c), r in zip(zip(ramp, ramp[1:]), steps):
        if r > limit + 1e-9 and not (a in bs and c in bs):  # a baseline subset is fine
            missing = [s for s in bs if a < s < c]
            jumps.append({"from": _clean(a), "to": _clean(c), "ratio": r,
                          "baseline_sizes_between": [_clean(s) for s in missing]})
    if jumps:
        j = jumps[0] if len(jumps) == 1 else None
        findings.append({
            "kind": "type_jump",
            "severity": "low",
            "title": (f"Type ramp jumps {j['from']} -> {j['to']} (x{j['ratio']:.2f}), a bigger step "
                      f"than anywhere in {b['name']}" if j else
                      f"{len(jumps)} jumps in the type ramp are bigger than any {b['name']} step"),
            "values": [[x["from"], x["to"]] for x in jumps],
            "nodes": [n for x in jumps for n in nodes[x["to"]]][:5],
            "detail": jumps,
            "fix": "Add an intermediate style or move the outlier onto the baseline: " + "; ".join(
                f"{x['from']} -> {x['to']}: baseline has "
                f"{', '.join(str(s) for s in x['baseline_sizes_between']) or 'nothing'} between"
                for x in jumps),
            "source": b["type_source"],
            "heuristic": f"step ratio > {limit:.3f}, the largest adjacent step in {b['name']}, "
                         "with at least one size off the baseline",
        })

    if chosen == "material3":
        bad_lh = sorted({(_clean(s), _clean(v)) for s in ramp for v in lh[s] if v % 4})
        if bad_lh:
            findings.append({
                "kind": "line_height_off_grid",
                "severity": "low",
                "title": f"{len(bad_lh)} line heights are off the 4dp baseline grid",
                "values": [f"{s}/{v}" for s, v in bad_lh],
                "fix": "Round line heights to a multiple of 4 (every M3 line height is).",
                "source": baselines["material3"]["spacing"]["source"],
            })
    return summary, findings


def analyze_spacing(spacing, baselines):
    if not spacing:
        return None, []
    grid_rule = baselines["material3"]["spacing"]
    grid = grid_rule["grid"]
    counts = Counter(s["value"] for s in spacing)
    scale = sorted(counts)
    total = sum(counts.values())
    share = {u: round(sum(c for v, c in counts.items() if v % u == 0) / total, 2)
             for u in (8, 4)}
    if share[8] >= BASE_UNIT_SHARE:
        base = 8
    elif share[4] >= BASE_UNIT_SHARE:
        base = 4
    else:
        base = None
    nodes = defaultdict(list)
    for s in spacing:
        if s["node"] and s["node"] not in nodes[s["value"]]:
            nodes[s["value"]].append(s["node"])
    summary = {
        "scale": [_clean(v) for v in scale],
        "usage": {str(_clean(v)): counts[v] for v in scale},
        "base_unit": base,
        "closest_unit": base or (4 if share[4] >= share[8] else 8),
        "share_on_8": share[8],
        "share_on_4": share[4],
        "sources": dict(Counter(s["source"] for s in spacing)),
        "hig_note": baselines.get("hig_ios", {}).get("spacing_note"),
    }

    findings = []
    off = [v for v in scale if v % grid]
    if off:
        on = [v for v in scale if v % grid == 0]
        detail = []
        for v in off:
            lo, hi = math.floor(v / grid) * grid, math.ceil(v / grid) * grid
            cands = [c for c in (lo, hi) if c > 0]
            used = [c for c in cands if c in on]
            suggest = min(used or cands, key=lambda c: (abs(c - v), -c))  # ties round up
            detail.append({"value": _clean(v), "uses": counts[v], "nodes": nodes[v][:5],
                           "suggest": _clean(suggest), "suggest_in_use": suggest in on})
        n_uses = sum(counts[v] for v in off)
        findings.append({
            "kind": "spacing_off_grid",
            "severity": "medium" if n_uses >= 3 else "low",
            "title": f"{len(off)} spacing values sit off the {grid}dp grid "
                     f"({n_uses} of {total} uses)",
            "values": [_clean(v) for v in off],
            "detail": detail,
            "nodes": [n for d in sorted(detail, key=lambda d: -d["uses"]) for n in d["nodes"]][:5],
            "fix": "; ".join(
                f"{d['value']} -> {d['suggest']}" + (" (already in use)" if d["suggest_in_use"] else "")
                for d in detail),
            "source": grid_rule["source"],
        })

    gaps = []
    for a, c in zip(scale, scale[1:]):
        if a >= 16 and c / a > SPACING_GAP_RATIO:
            gaps.append([_clean(a), _clean(c)])
    if gaps:
        findings.append({
            "kind": "spacing_gap",
            "severity": "info",
            "title": "Spacing scale skips steps: " + ", ".join(f"{a} -> {c}" for a, c in gaps),
            "values": gaps,
            "fix": "Fine if intentional (e.g. section breaks); otherwise add the missing step.",
            "source": grid_rule["source"],
            "heuristic": f"adjacent values more than {SPACING_GAP_RATIO:g}x apart above 16",
        })
    return summary, findings


SOURCE_NAMES = {
    "https://m3.material.io/styles/typography/type-scale-tokens": "Material 3 type scale",
    "https://m2.material.io/design/layout/spacing-methods.html": "Material 4dp/8dp grid",
    "https://developer.apple.com/design/human-interface-guidelines/typography": "Apple HIG text styles",
}
SEV_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
KIND_ORDER = ["spacing_off_grid", "type_crowded", "type_off_baseline", "type_jump",
              "line_height_off_grid", "spacing_gap"]


def node_url(file_url, node):
    if not file_url or not node:
        return None
    sep = "&" if "?" in file_url else "?"
    return f"{file_url}{sep}node-id={node.replace(':', '-')}"


def check(paths, baseline="auto", file_url=None, baselines=None):
    baselines = baselines or load_baselines()
    texts, spacing, kinds = read_inputs(paths)
    type_summary, tf = analyze_type(texts, baselines, baseline)
    spacing_summary, sf = analyze_spacing(spacing, baselines)
    findings = sorted(tf + sf, key=lambda f: (SEV_ORDER[f["severity"]], KIND_ORDER.index(f["kind"])))
    for i, f in enumerate(findings, 1):
        f["id"] = f"T{i}"
        f["source_name"] = SOURCE_NAMES.get(f["source"], "baseline")
        first = (f.get("nodes") or [None])[0] or next(
            (n for d in f.get("detail", []) if isinstance(d, dict) for n in d.get("nodes", [])), None)
        f["node"] = first
        f["figma_url"] = node_url(file_url, first)
    notes = []
    if type_summary is None:
        notes.append("No font sizes found. get_metadata has none; pass get_variable_defs "
                     "or get_design_context output for the type ramp.")
    if spacing_summary is None:
        notes.append("No spacing values found.")
    return {"inputs": kinds, "type": type_summary, "spacing": spacing_summary,
            "findings": findings, "notes": notes}


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

def card(f):
    """Pasteable finding card, same shape as critique-rubric.md."""
    lines = [f"[{f['id']} · {f['severity'].upper()}] {f['title']}", f"Fix: {f['fix']}"]
    if f.get("figma_url"):
        lines.append(f"Figma: {f['figma_url']}")
    lines.append(f"Backs: {SOURCE_NAMES.get(f['source'], 'baseline')} · {f['source']}" + (f" · heuristic: {f['heuristic']}" if f.get("heuristic") else ""))
    return "\n".join(lines)


def render_text(r):
    out = []
    t, s = r["type"], r["spacing"]
    if t:
        out.append("Type ramp: " + " · ".join(str(v) for v in t["ramp"]))
        if t["overall_ratio"]:
            out.append(f"  ratio: x{t['overall_ratio']} overall (nearest {t['nearest_named_ratio']}), "
                       f"median step x{t['median_step']}, steps {t['steps']}")
        fit = ", ".join(f"{v['name']} {v['matched']}/{v['of']}" for v in t["baseline_fit"].values())
        out.append(f"  baseline fit: {fit} -> using {t['baseline']}")
    if s:
        out.append("Spacing scale: " + " · ".join(str(v) for v in s["scale"]))
        unit = s["base_unit"] or f"irregular, closest {s['closest_unit']}"
        out.append(f"  base unit: {unit} "
                   f"(on 8: {s['share_on_8']:.0%}, on 4: {s['share_on_4']:.0%})")
    for n in r["notes"]:
        out.append("Note: " + n)
    out.append(f"\nFindings: {len(r['findings'])}")
    for f in r["findings"]:
        out.append("")
        out.append(card(f))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Type ramp + spacing check vs Material 3 / Apple HIG.")
    ap.add_argument("paths", nargs="+", help="Figma MCP output saved to file(s)")
    ap.add_argument("--baseline", default="auto", choices=["auto", "material3", "hig_ios"],
                    help="type baseline (default: best fit)")
    ap.add_argument("--file-url", help="Figma file URL, to build Open-in-Figma links")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)
    result = check(args.paths, args.baseline, args.file_url)
    print(json.dumps(result, indent=2) if args.json else render_text(result))


if __name__ == "__main__":
    main()
