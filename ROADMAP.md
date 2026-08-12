# Roadmap

Small, paced to real use. The big arcs (a quantified token layer, then a companion
that turns a review into a starter design spec) live in the README. These are the
near-term, high-signal improvements, each roughly one or two sessions.

- [x] **Reproducible triggering eval.** A runner that executes `trigger-evals.json`
  through an LLM judge and prints a pass/fail table, so the "18/18" result is
  runnable, not just asserted. → `evals/run_trigger_evals.py`.
- [x] **Full-path usefulness pass (v1.2).** Quick/Full modes, mid-run confirm,
  prompt cookbook, named-competitor guarantee, UX copy matrix, share summary /
  finding cards, `parse_figma_metadata.py`, slim SKILL.md, Pages gallery +
  surgically updated sample (recreate-from-tokens wording).
- [x] **Landing page.** `docs/index.html` gallery linking the sample and the repo.
- [ ] **A second sample (degraded path).** No-Mobbin / link-based evidence report
  to show graceful degradation (secondary for Mobbin+Figma primary audience).
- [x] **Golden-report regression check.** Snapshot assertions on the committed
  sample (finding IDs, headings, contrast numbers) → `evals/check_golden_report.py`.
- [x] **`contrast.py` unit test.** → `skills/ux-proofsheet/scripts/test_contrast.py`.
- [ ] **Fallback-recipes reference.** Concrete no-Mobbin web-search path guidance.
- [ ] **A minimal token-layer slice (v2 seed).** Pull the type ramp and spacing scale
  from Figma and flag non-conforming jumps against a Material/HIG baseline.
