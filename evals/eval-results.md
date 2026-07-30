# Eval results — ux-proofsheet v1.1

Two evals run with independent subagents. The skill's full output depends on the
Mobbin + Figma MCPs, which can't be driven in an automated harness, so these test
the two things that don't need them: **triggering accuracy** and
**instruction-followability**.

## 1. Triggering (18 queries · 3 independent judges)

Each judge picked the single best skill per query from a realistic catalog that
included ux-proofsheet **and its sibling design skills** (design-critique,
accessibility-review, design-system, ux-copy, user-research, research-synthesis,
design-handoff, dataviz), so the test measures discrimination against near-misses,
not just recall.

**Result: 18/18 correct, unanimous across all 3 judges.**

- All 9 should-trigger prompts → `ux-proofsheet` (incl. "compare my wireframe",
  "find examples of how [app] does X", "is this conventional?", multi-screen).
- All 9 near-misses routed to the right sibling instead — including the tricky
  "review this mockup … no need to compare to anyone" → `design-critique`, and
  "design me a login screen from scratch" → none/generation.

No description changes needed. Query set: `trigger-evals.json`.

## 2. Instruction-followability dry-run

A fresh agent read the SKILL.md + references and simulated a run on a **text-only**
design description with **Mobbin and Figma both disconnected** (the hardest
degraded path), then QA'd the skill itself.

**Result:** followable; produced all 9 required sections as a valid degraded
report. It surfaced one real issue, now fixed:

- **Problem:** the degradation rules lived only in Step 0 + `evidence-tiers.md`,
  while Step 5's section spec, the finding anatomy, and the output rules were
  written in full-path (Mobbin+Figma) terms and never locally re-qualified. A
  literal reader could feel obligated to produce a cropped screenshot, an "Open in
  Figma" link, a `mobbin_url`, or a computed contrast ratio when the source was
  absent — risking **fabrication** (an invented node ID, a fake `mobbin_url`, an
  eyeballed contrast presented as measured). It also noted that "the design under
  review" assumed an image and didn't cover text-only input.

- **Fix applied (v1.1):**
  - Added a **degraded-path substitution table** right before the Step 5 section
    spec (missing source → what it removes → non-fabricating substitute).
  - Added in-place fallback clauses to the finding spec, the benchmark spec, and
    the contrast step ("no tokens → print 'contrast not computed', never fake it").
  - Covered **text-only input** in "the design under review" (reconstruct as a
    labelled structural list).
  - Mirrored the no-Figma / no-token branches into the rubric.

Net: the "never fabricate" guardrail is now reinforced at the point of use, not
only in Step 0.
