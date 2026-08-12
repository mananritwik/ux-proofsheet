#!/usr/bin/env python3
"""
check_golden_report.py — assert committed sample HTML matches golden expectations.

Does not re-run Mobbin/Figma. Validates structure + recomputes contrast numbers
cited in the sample via contrast.py.

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
    print(f"PASS — {len(data['samples'])} sample(s) match golden assertions")


if __name__ == "__main__":
    main()
