#!/usr/bin/env python3
"""
run_trigger_evals.py — reproduce the ux-proofsheet triggering eval.

Reads trigger-evals.json, and for each query asks an LLM judge to pick the single
best skill from a catalog that includes ux-proofsheet AND its sibling design skills.
Runs several independent judges per query (default 3), takes the majority vote, and
compares it to the intended routing. Prints a pass/fail table and a summary, and
exits non-zero if any query fails — so it works as a CI gate.

This makes the "18/18, unanimous across 3 judges" claim in eval-results.md
reproducible rather than asserted.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=...            # or `ant auth login`
    python run_trigger_evals.py             # 3 judges, model = $JUDGE_MODEL or claude-opus-5
    python run_trigger_evals.py --judges 5
    JUDGE_MODEL=claude-haiku-4-5 python run_trigger_evals.py   # cheaper judge

Env:
    ANTHROPIC_API_KEY   your API key (or use `ant auth login`)
    JUDGE_MODEL         judge model id (default: claude-opus-5)
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("This runner needs the Anthropic SDK. Install it with:  pip install anthropic")

DEFAULT_MODEL = os.environ.get("JUDGE_MODEL", "claude-opus-5")

# The routing catalog the judge chooses from. ux-proofsheet sits next to its real
# sibling design skills so the eval measures discrimination, not just recall.
# Descriptions are neutral (each skill's own one-liner) to avoid biasing the judge.
CATALOG = {
    "ux-proofsheet": "Benchmark an existing UI/UX design against how real competitor apps ship the same pattern; evidence-backed, scored competitive review.",
    "design:design-critique": "Structured design feedback on usability, hierarchy, and consistency for a single screen, with no competitive comparison.",
    "design:accessibility-review": "Run a WCAG 2.1 AA accessibility audit: contrast, focus order, touch targets, screen-reader behavior.",
    "design:design-system": "Audit, document, or extend a design system: naming consistency, hardcoded values, component variants.",
    "design:ux-copy": "Write or review UX copy: microcopy, button labels, error messages, empty states, CTAs.",
    "design:user-research": "Plan or conduct user research: interview guides, screeners, usability tests, surveys.",
    "design:research-synthesis": "Synthesize existing research (interviews, surveys, tickets) into themes, insights, and recommendations.",
    "design:design-handoff": "Generate developer handoff specs from a design: tokens, breakpoints, interaction states.",
    "dataviz": "Create a chart, graph, plot, dashboard, or data visualization.",
    "none/generation": "No skill fits, or the user wants to generate a brand-new UI/screen from scratch.",
}

SYSTEM = (
    "You are a strict router. Given a user request, pick the SINGLE best skill to handle it "
    "from the catalog below. Choose 'ux-proofsheet' ONLY when the user wants an existing design "
    "evaluated against how real competitors/other apps solve the same pattern. If the request is "
    "about copy, accessibility, a design system, research, handoff, a chart, a critique with no "
    "competitive angle, or generating new UI, pick the matching sibling instead.\n\nCatalog:\n"
    + "\n".join(f"- {k}: {v}" for k, v in CATALOG.items())
)

# Structured output: force the judge to return exactly one catalog id.
OUTPUT_FORMAT = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {"skill": {"type": "string", "enum": list(CATALOG)}},
        "required": ["skill"],
        "additionalProperties": False,
    },
}


def judge_once(client, model, query):
    """One judge call. Returns a catalog id, or None on refusal/parse failure."""
    resp = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": query}],
        # Passed via extra_body so this works across SDK versions (older SDKs don't
        # type output_config; the request body forwards it verbatim either way).
        extra_body={"output_config": {"format": OUTPUT_FORMAT}},
    )
    if resp.stop_reason == "refusal":
        return None
    text = next((b.text for b in resp.content if b.type == "text"), None)
    if not text:
        return None
    try:
        return json.loads(text)["skill"]
    except (json.JSONDecodeError, KeyError):
        return None


def main():
    ap = argparse.ArgumentParser(description="Reproduce the ux-proofsheet triggering eval.")
    ap.add_argument("--judges", type=int, default=3, help="independent judges per query (default 3)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"judge model id (default {DEFAULT_MODEL})")
    ap.add_argument("--evals", default=str(Path(__file__).with_name("trigger-evals.json")))
    args = ap.parse_args()

    queries = json.loads(Path(args.evals).read_text())["queries"]
    client = anthropic.Anthropic()

    print(f"Judge model: {args.model}   judges/query: {args.judges}   queries: {len(queries)}\n")
    print(f"{'id':>3}  {'expected':<28} {'majority':<28} {'votes':<9} result")
    print("-" * 88)

    passed = unanimous = 0
    failures = []
    for q in queries:
        expected = q["intended"]
        votes = [judge_once(client, args.model, q["query"]) for _ in range(args.judges)]
        tally = Counter(v for v in votes if v is not None)
        majority = tally.most_common(1)[0][0] if tally else "<no-vote>"
        ok = majority == expected
        is_unanimous = len(tally) == 1 and None not in votes
        passed += ok
        unanimous += is_unanimous
        if not ok:
            failures.append((q["id"], expected, majority))
        flag = "PASS" if ok else "FAIL"
        star = " (unanimous)" if is_unanimous and ok else ""
        print(f"{q['id']:>3}  {expected:<28} {majority:<28} {sum(tally.values())}/{args.judges:<6} {flag}{star}")

    print("-" * 88)
    print(f"\n{passed}/{len(queries)} correct   |   {unanimous}/{len(queries)} unanimous")
    if failures:
        print("\nFailures (id: expected -> majority):")
        for fid, exp, got in failures:
            print(f"  {fid}: {exp} -> {got}")
        sys.exit(1)
    print("All queries routed as intended.")


if __name__ == "__main__":
    main()
