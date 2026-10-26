# Roadmap

Small, paced to real use. The big arcs (a quantified token layer, started in v1.3,
then a companion that turns a review into a starter design spec) live in the README. These are the
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
- [x] **A minimal token-layer slice (v2 seed, shipped in v1.3).** Pull the type ramp
  and spacing scale from Figma and flag non-conforming jumps against a Material/HIG
  baseline. → `scripts/token_check.py`, cited baselines in
  `references/token-baselines.md`, fixtures + 26 unit tests, a Token layer section
  in the sample, and a golden check that re-runs the tool against the sample.

## Left for the full token layer (v2)

- [ ] **Live-Figma run.** Run the token check on a real file through the MCP and
  write it up, the way v1.1 was pressure-tested. v1.3 is fixture-tested only.
- [ ] **Color roles.** Map color variables to M3 color roles and feed the pairs to
  `contrast.py`, so contrast findings come from roles, not hand-picked pairs.
- [ ] **Radius, elevation, stroke.** Same treatment as spacing.
- [ ] **Modes.** Light/dark and density modes, and HIG Dynamic Type sizes beyond
  the default (Large) column.
- [ ] **Public competitor systems as Tier 2.** Where a competitor publishes its
  design system tokens (e.g. Atlassian, Shopify Polaris, GitHub Primer), compare
  against those, cited, instead of only Material and HIG.
- [ ] **HIG spacing.** Only if Apple publishes one. Until then, spacing is checked
  against Material's grid and labelled that way.
