#!/usr/bin/env python3
"""
check_golden_report.py — assert committed sample HTML matches golden expectations.

Does not re-run Mobbin/Figma. Validates structure, recomputes contrast numbers
cited in the sample via contrast.py, and re-runs token_check.py on the committed
Figma fixture to confirm the sample's token-layer numbers match the tool.

Usage:
    python check_golden_report.py
    python check_golden_report.py --assertions golden/example-assertions.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "ux-proofsheet" / "scripts"))
import contrast  # noqa: E402
import token_check  # noqa: E402


def _x(r):
    return f"×{r}"


def check_tokens(repo: Path, label: str, html: str, spec: dict) -> list:
    """Re-run token_check on the fixture; the sample must quote its numbers."""
    errors = []
    result = token_check.check([repo / spec["fixture"]], baseline=spec.get("baseline", "auto"))
    t, s = result["type"], result["spacing"]
    cited = {
        "type ramp": " · ".join(str(v) for v in t["ramp"]),
        "overall ratio": _x(t["overall_ratio"]),
        "spacing scale": " · ".join(str(v) for v in s["scale"]),
        "share on 4dp grid": f"{round(s['share_on_4'] * 100)}% of uses sit on the 4dp grid",
    }
    for what, text in cited.items():
        if text not in html:
            errors.append(f"{label}: token {what} {text!r} not quoted in sample")
    if t["baseline"] != spec["expected_baseline"]:
        errors.append(f"{label}: token baseline {t['baseline']}, expected {spec['expected_baseline']}")
    got = [(f["id"], f["kind"], f["severity"]) for f in result["findings"]]
    exp = [tuple(x) for x in spec["expected_findings"]]
    if got != exp:
        errors.append(f"{label}: token findings {got}, expected {exp}")
    for f in result["findings"]:
        sev = {"medium": "s-med", "low": "s-low", "high": "s-high", "info": "s-info"}[f["severity"]]
        head = f'<span class="id">{f["id"]}</span><span class="title">'
        i = html.find(head)
        if i < 0 or sev not in html[i:i + 400]:
            errors.append(f"{label}: finding {f['id']} missing or wrong severity in sample")
        if f.get("node") and f"node-id={f['node'].replace(':', '-')}" not in html:
            errors.append(f"{label}: finding {f['id']} Figma node {f['node']} not linked")
    return errors


def check_sample(repo: Path, spec: dict) -> list[str]:
    errors = []
    path = repo / spec["path"]
    if not path.exists():
        return [f"missing file: {spec['path']}"]
    html = path.read_text(encoding="utf-8")
    for h in spec.get("required_headings", []):
        if h not in html:
            errors.append(f"{spec['path']}: missing heading {h!r}")
    for fid in spec.get("required_finding_ids", []):
        if f">{fid}</" not in html and f">{fid} ·" not in html and f'class="id">{fid}</' not in html:
            # findings use <span class="id">C1</span>
            if f">{fid}</span>" not in html:
                errors.append(f"{spec['path']}: missing finding id {fid}")
    for s in spec.get("required_substrings", []):
        if s not in html:
            errors.append(f"{spec['path']}: missing substring {s!r}")
    for c in spec.get("contrast_checks", []):
        got = contrast.ratio(c["fg"], c["bg"])
        exp = c["expected_ratio"]
        tol = c.get("tolerance", 0.15)
        if abs(got - exp) > tol:
            errors.append(
                f"{spec['path']}: contrast {c['fg']} on {c['bg']} = {got}, expected ~{exp}"
            )
    if "token_check" in spec:
        errors.extend(check_tokens(repo, spec["path"], html, spec["token_check"]))
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--assertions",
        type=Path,
        default=Path(__file__).parent / "golden" / "example-assertions.json",
    )
    args = ap.parse_args()
    data = json.loads(args.assertions.read_text(encoding="utf-8"))
    errors = []
    for sample in data["samples"]:
        errors.extend(check_sample(ROOT, sample))
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"PASS: {len(data['samples'])} sample(s) match golden assertions")


if __name__ == "__main__":
    main()
