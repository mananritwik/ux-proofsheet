# Eval results — ux-proofsheet v1.2

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

