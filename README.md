<div align="center">

# ux-proofsheet

### Benchmark a UI/UX design against how real apps actually ship, in your industry and outside it.

A Claude [Agent Skill](https://github.com/anthropics/skills). Point it at a design; it pulls real competitor screens for the same patterns and returns a scored, evidence-backed review. A UX benchmark, not a pixel diff.

**[See a sample review →](https://mananritwik.github.io/ux-proofsheet/example-review.html)**  ·  [gallery](https://mananritwik.github.io/ux-proofsheet/) ·  works with the [Mobbin](https://mobbin.com/mcp) and [Figma](https://www.figma.com/blog/design-systems-ai-mcp/) MCPs

</div>

## What it does

Give it a Figma frame, a screenshot, or a plain description. It:

- reads the design and its own on-canvas notes,
- pulls real competitor screens from [Mobbin](https://mobbin.com) for each pattern, deliberately mixing **same-industry and cross-industry** examples,
- returns a self-contained HTML report: a competitive-position **scorecard**, **findings by dimension** (navigation, UX copy, visual, accessibility) each tied to a real example and the exact Figma layer, a **cross-industry prevalence** table, and **prioritized fixes**,
- and, new in v1.3, measures the design's **type ramp and spacing scale** against Material 3 and Apple's HIG (the token layer, below).

It's a **first pass**. It compresses the "sign up for apps, screenshot, catalog how others solve this" research so your time goes to judgment, not gathering. You decide how much of the score to take: a junior designer can read it as guidance, a senior as a currency check.

## Why it's different

Most design-review tooling does one of two things: it critiques a screen in isolation, or it generates UI from a spec. Neither answers the question you have before shipping, which is how this compares to what real competitors already do. ux-proofsheet grounds every finding in a real shipped screen, and it looks *across industries* on purpose, because a pattern that holds in fintech, travel, and social is a stronger signal than one that's just common in your niche.

## How I use it in practice

I lead product and came up through design. The way I stay sharp is hands-on: I use apps in our space, screenshot them, and keep my own library. This skill extends that to the apps I can't sign up for and to completely different industries, and it goes down to the element level (every good navigation in the database, not just whole flows). I feed its first pass into my own design reviews, layer my hands-on research and product intuition on top, and make the call. It keeps me current and lock-step with designers who research full-time, and it lets me turn around specific, detailed feedback fast, which unblocks engineering and gives sales something to show. The judgment stays human. This compresses the part a machine does better.

## How it thinks (the guardrails)

- **Evidence over opinion.** Every finding points to a real competitor screen or a cited source. No "I think."
- **Convention isn't the goal, and popular isn't correct.** It separates "you match the market" from "you deviate, and that's your edge" from "you deviate, reconsider," and it only calls something a convention when the direct set agrees.
- **Never fake it.** If it can't source a screen, a token, or a contrast number, it says so instead of inventing one.
- **UX, not pixels.** Screens in the report are clean recreations from the design's own tokens, self-contained and permanent; the exact pixels are one click away in Figma.

## The token layer (v1.3)

Patterns are half of a design review. The other half is the system underneath: is the type ramp an actual scale, and does the spacing sit on a grid? Screenshots show that but can't measure it. v1.3 measures it.

[`scripts/token_check.py`](skills/ux-proofsheet/scripts/token_check.py) reads what the Figma MCP returns (`get_variable_defs`, `get_design_context` code, a node tree, or `get_metadata` geometry) and reports:

- the **type ramp** the design uses, its step ratio, and how many of its sizes match Material 3 and Apple's iOS text styles,
- the **spacing scale** and its base unit (8, 4, or irregular),
- findings for spacing off the 4dp grid, type sizes too close to tell apart, sizes that aren't baseline styles, and jumps that skip a step. Each one comes out in the same finding-card format as the rest of the review: severity, fix, the cited baseline, and an Open in Figma link.

It runs offline on the bundled fixture, no Figma account needed:

```bash
python skills/ux-proofsheet/scripts/token_check.py skills/ux-proofsheet/scripts/fixtures/home-nodes.json
```

```
Type ramp: 11 · 12 · 13 · 14 · 15 · 16 · 20 · 32
  ratio: x1.165 overall (nearest Minor Third), median step x1.083, ...
  baseline fit: Material 3 5/8, Apple HIG (iOS, Large default) 6/8 -> using hig_ios
Spacing scale: 2 · 4 · 6 · 8 · 10 · 12 · 14 · 16 · 24
  base unit: irregular, closest 4 (on 8: 28%, on 4: 63%)

[T1 · MEDIUM] 4 spacing values sit off the 4dp grid (26 of 71 uses)
Fix: 2 -> 4 (already in use); 6 -> 8 (already in use); 10 -> 12 (already in use); 14 -> 16 (already in use)
...
```

In a Full review the skill runs it for you and the results land in the report's [Token layer section](https://mananritwik.github.io/ux-proofsheet/example-review.html#token-layer), which is this exact output.

Limits, plainly:

- **Two baselines.** Material 3 and Apple HIG (iOS, default text size). Every number is copied from the official pages, with links in [`references/token-baselines.md`](skills/ux-proofsheet/references/token-baselines.md).
- **Apple publishes no iOS spacing grid.** The "8pt grid" is a community habit, not an Apple rule, so spacing is checked against Material's 4dp/8dp grid only. The tool never cites an Apple rule that doesn't exist.
- **Some thresholds are mine.** What counts as "crowded" or a "jump" is a heuristic, and the report labels it that way rather than pinning it on Material or Apple.
- **Type and spacing only.** Color roles, radius, elevation, and light/dark modes are not covered yet.
- **Canonical systems, not competitors.** A competitor's real tokens live in their private Figma files, so this compares you to Material and HIG, not to Jobber.
- **Fixture-tested.** This release is tested on hand-written Figma fixtures, not yet on a live Figma file. `get_metadata` carries no font sizes, so give it variables or design-context output for the type ramp.

## How I know it works

- **Triggering eval.** 18 realistic prompts against the skill next to its sibling design skills; it fired on the competitive-review asks and stayed out of the near-misses. Reproduce it live: `python evals/run_trigger_evals.py`. ([`evals/`](evals))
- **A real run.** Pointed at an actual design refresh, which surfaced real problems in the skill (fragile image handling, scope on large boards); fixed, and written up.
- **Unit tests and a golden check.** 33 offline tests across the token check and the contrast checker. `python evals/check_golden_report.py` re-runs the token check on the fixture and fails if the sample report's numbers drift from the tool.

## Requirements

Best with the [Mobbin](https://mobbin.com/mcp) and [Figma](https://www.figma.com/blog/design-systems-ai-mcp/) MCPs connected. No Mobbin? It falls back to web research for real examples, so you still get evidence, just links instead of screenshots.

### Preflight (Mobbin + Figma)

Before your first real review, confirm both MCPs respond:

1. **Figma**: open a frame URL; the agent can `get_screenshot` / `get_design_context`.
2. **Mobbin**: a simple `search_screens` (e.g. `"ios home dashboard"`) returns results.

Paste-ready prompts live in [`skills/ux-proofsheet/references/prompt-cookbook.md`](skills/ux-proofsheet/references/prompt-cookbook.md). Ask for **Quick** (one screen, top findings) or **Full** (complete proofsheet).

## Install

```
/plugin marketplace add mananritwik/ux-proofsheet
/plugin install ux-proofsheet
```

Or drop `skills/ux-proofsheet/` into your skills directory, or upload the packaged `.skill` file to Claude.

## What's in here

- [`skills/ux-proofsheet/SKILL.md`](skills/ux-proofsheet/SKILL.md): the workflow.
- [`references/`](skills/ux-proofsheet/references): critique rubric, evidence model, Mobbin search recipes, prompt cookbook, cited token baselines.
- [`scripts/`](skills/ux-proofsheet/scripts): token check (type ramp and spacing), WCAG contrast checker, Figma metadata triage, image helper, tests and fixtures.
- [`evals/`](evals): triggering set, golden sample check, and results.

## Roadmap

Small, paced to real use. Near-term steps are tracked in [`ROADMAP.md`](ROADMAP.md). The larger arcs: the quantified design-token layer (first slice shipped in v1.3: type ramp and spacing; color roles and competitor systems next), then a companion that turns a review into a starter design spec. Ship a sharp small thing, improve it in public.

## Honest notes

Built with Claude Code. It's a benchmark of patterns, not a full audit, and its competitor evidence leans on Mobbin. Use the reports for your own design work rather than to republish competitor screenshots (see [Mobbin's terms](https://mobbin.com)).

[MIT](LICENSE).
