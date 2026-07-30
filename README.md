<div align="center">

# ux-proofsheet

### Benchmark a UI/UX design against how real apps actually ship, in your industry and outside it.

A Claude [Agent Skill](https://github.com/anthropics/skills). Point it at a design; it pulls real competitor screens for the same patterns and returns a scored, evidence-backed review. A UX benchmark, not a pixel diff.

**[See a sample review →](https://mananritwik.github.io/ux-proofsheet/example-review.html)**  ·  works with the [Mobbin](https://mobbin.com/mcp) and [Figma](https://www.figma.com/blog/design-systems-ai-mcp/) MCPs

<!-- Add a screenshot of the sample here once Pages is live: ![sample](docs/example.png) -->

</div>

## What it does

Give it a Figma frame, a screenshot, or a plain description. It:

- reads the design and its own on-canvas notes,
- pulls real competitor screens from [Mobbin](https://mobbin.com) for each pattern, deliberately mixing **same-industry and cross-industry** examples,
- returns a self-contained HTML report: a competitive-position **scorecard**, **findings by dimension** (navigation, UX copy, visual, accessibility) each tied to a real example and the exact Figma layer, a **cross-industry prevalence** table, and **prioritized fixes**.

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

## How I know it works

- **Triggering eval.** 18 realistic prompts against the skill next to its sibling design skills; it fired on the competitive-review asks and stayed out of the near-misses. Reproduce it live: `python evals/run_trigger_evals.py`. ([`evals/`](evals))
- **A real run.** Pointed at an actual design refresh, which surfaced real problems in the skill (fragile image handling, scope on large boards); fixed, and written up.

## Requirements

Best with the [Mobbin](https://mobbin.com/mcp) and [Figma](https://www.figma.com/blog/design-systems-ai-mcp/) MCPs connected. No Mobbin? It falls back to web research for real examples, so you still get evidence, just links instead of screenshots.

## Install

```
/plugin marketplace add mananritwik/ux-proofsheet
/plugin install ux-proofsheet
```

Or drop `skills/ux-proofsheet/` into your skills directory, or upload the packaged `.skill` file to Claude.

## What's in here

- [`skills/ux-proofsheet/SKILL.md`](skills/ux-proofsheet/SKILL.md): the workflow.
- [`references/`](skills/ux-proofsheet/references): the critique rubric, the evidence model, and the Mobbin search recipes. Useful as a design-review method on their own.
- [`scripts/`](skills/ux-proofsheet/scripts): a WCAG contrast checker and an image helper.
- [`evals/`](evals): the triggering set and the results.

## Roadmap

Small, paced to real use. Near-term steps are tracked in [`ROADMAP.md`](ROADMAP.md); the larger arcs are a quantified design-token layer next, then a companion that turns a review into a starter design spec. Ship a sharp small thing, improve it in public.

## Honest notes

Built with Claude Code. It's a benchmark of patterns, not a full audit, and its competitor evidence leans on Mobbin. Use the reports for your own design work rather than to republish competitor screenshots (see [Mobbin's terms](https://mobbin.com)).

[MIT](LICENSE).
