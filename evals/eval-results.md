# Eval results: ux-proofsheet v1.3

Two evals run with independent subagents. The skill's full output depends on the
Mobbin + Figma MCPs, which can't be driven in an automated harness, so these test
the two things that don't need them: **triggering accuracy** and
**instruction-followability**. A third check snapshots the committed sample report.

## 1. Triggering (18 queries · 3 independent judges)

Each judge picked the single best skill per query from a realistic catalog that
included ux-proofsheet **and its sibling design skills** (design-critique,
accessibility-review, design-system, ux-copy, user-research, research-synthesis,
design-handoff, dataviz), so the test measures discrimination against near-misses,
not just recall.

**Result: 18/18 correct, unanimous across all 3 judges.** (v1.1; description still
covers the same triggers, plus "quick proofsheet".)

**Reproduce it:** `pip install -r requirements.txt && python run_trigger_evals.py`

## 2. Instruction-followability dry-run

A fresh agent read the SKILL.md + references and simulated a run on a **text-only**
design description with **Mobbin and Figma both disconnected** (the hardest
degraded path), then QA'd the skill itself.

**Result (v1.1):** followable; produced all required sections as a valid degraded
report. Fabrication risk fixed via the substitution table at Step 5.

**v1.2 note:** SKILL slimmed (~158 lines) with progressive disclosure into
references; Quick/Full modes, mid-run confirm, copy matrix, and share summary
added. Re-run a dry-run after install if you change routing/output heavily.

## 3. Golden sample check (v1.2)

`python evals/check_golden_report.py` asserts the committed
`docs/example-review.html` still contains required headings, finding IDs, recreate
wording, share/follow-up cues, and that cited contrast ratios match `contrast.py`.

**v1.3:** it also re-runs `token_check.py` on
`skills/ux-proofsheet/scripts/fixtures/home-nodes.json` and fails if the sample's
token-layer numbers (ramp, ratio, spacing scale, grid share), finding IDs,
severities, or Figma node links drift from the tool's output.

## 4. Token layer unit tests (v1.3)

`python skills/ux-proofsheet/scripts/test_token_check.py` runs 26 offline tests:

- **Baseline guard:** the Material 3 and HIG numbers match the official pages
  (sizes, line heights, 1.125 ratio), and HIG carries no spacing grid or ratio.
- **Parsing:** variable defs (`Font(...)` strings, percent line heights), REST and
  plugin node trees, Tailwind/CSS design-context code, and `get_metadata` geometry.
- **Analysis:** the fixture's ramp, ratio, spacing scale, base unit, finding order,
  round-up suggestions, Figma links; a clean Material design yields no findings; a
  run of HIG sizes 15/16/17 is not flagged as crowded.
- **CLI:** JSON output and the pasteable finding-card text.

**Triggering eval not re-run for v1.3.** The skill description did not change, so
routing is unaffected. The session that built v1.3 had no `ANTHROPIC_API_KEY`;
re-run with `python evals/run_trigger_evals.py` when one is available.

