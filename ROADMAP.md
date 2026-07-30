# Roadmap

Small, paced to real use. The big arcs (a quantified token layer, then a companion
that turns a review into a starter design spec) live in the README. These are the
near-term, high-signal improvements, each roughly one or two sessions.

- [x] **Reproducible triggering eval.** A runner that executes `trigger-evals.json`
  through an LLM judge and prints a pass/fail table, so the "18/18" result is
  runnable, not just asserted. → `evals/run_trigger_evals.py`.
- [ ] **Landing page + a second sample.** A small `docs/index.html` gallery linking
  the samples and the repo (the Pages root is currently bare), plus one more sample
  report from the degraded path (no Mobbin, link-based evidence) to show the range
  and prove graceful degradation produces a real report.
- [ ] **Golden-report regression check.** Snapshot the example run's key assertions
  (finding IDs, node IDs, computed contrast numbers) as a golden file, plus a check
  that a re-run still produces them. The skill applying eval-driven development to
  itself.
- [ ] **A `contrast.py` unit test + a fallback-recipes reference.** A small test for
  the one script (it has none), and a `references/fallback-recipes.md` for the
  no-Mobbin web-search path, so "degrades gracefully" is concrete guidance.
- [ ] **A minimal token-layer slice (v2 seed).** Pull the type ramp and spacing scale
  from Figma and flag non-conforming jumps against a Material/HIG baseline. A thin
  first cut of the quantified token comparison the README points at.
