# Critique rubric

How ux-proofsheet turns a design into a *scored, defensible* review instead of a
pile of opinions. Read this before writing findings.

**Frame findings as a starting point, not a ruling.** The score and the fixes are
there to *start a conversation* and *challenge an assumption*, calibrated so a
junior designer can take them as guidance and a senior can use them to pressure-
test taste and stay current. Write each finding so it works both as the reader's
own digest and as something they can hand a designer. Ground everything in real
examples so the reader can disagree with the evidence in front of them, not with
your opinion. **UX copy deserves extra weight** — real wording compared across many
apps is exactly where cross-app benchmarking beats intuition, so give copy findings
generous, concrete examples.

## The five dimensions

Every finding belongs to one dimension. Anchoring findings in a fixed set is what
makes them credible — "this violates *recognition over recall*" beats "this feels
confusing."

| Dimension | What it covers | Anchor heuristics |
|---|---|---|
| **Navigation & IA** | Structure, labels, tab/menu model, findability, consistency of mental model | Match between system & real world; consistency & standards; recognition over recall |
| **UX copy** | Microcopy, button verbs, tone, terminology drift, error/empty states | Clarity; user control; helpful, human language |
| **Visual & tokens** | Hierarchy, spacing, color use, and **design-token hygiene** (misspelled tokens, hardcoded hex, duplicate values) | Aesthetic & minimalist design; visibility of system status |
| **Placeholder data** | Dummy content that isn't a design flaw but derails stakeholder review (repeated names, lorem, trailing whitespace) | — (a "fix before share" class, see below) |
| **Accessibility** | Contrast, touch-target size, focus order, text size — a WCAG 2.1 AA quick pass | Perceivable, operable, understandable, robust |

Token hygiene is a superpower you get *only* from reading Figma — Mobbin can't
give it to you. Always check for misspelled variable names, hardcoded hex where a
token exists, and two near-identical values. These ship straight into code.

**Accessibility is measured, not guessed.** You extracted the color tokens from
Figma, so run `scripts/contrast.py` on the foreground/background pairs and report
the actual WCAG ratios (e.g. `#798087` on `#fff` = 4.0:1 — fails AA normal, borderline).
Compute contrast; don't eyeball it. Also confirm status isn't conveyed by color
alone (needs a text label too) and touch targets clear 44×44px. **If no tokens
were extractable (no Figma), do not run or fake the script** — write "contrast not
computed — no tokens; likely risk pairs X/Y; re-run with tokens." An eyeballed
ratio presented as measured is a fabrication.

## Coverage: screens and states

A review isn't done when the happy-path home screen is done. Cover:

- **Every screen** the user provides — home, menu, switcher, profile, detail. If
  they share four, review four. Organize the report by screen when there are
  several, with the dimensions nested inside.
- **Every state** of each screen — empty, loading, error, first-run / onboarding,
  and role / permission variants (owner vs member). This is where designs and
  competitors differ most: *empty ≠ blank*, a first-run home is a different screen,
  and a member sees a different set of modules than an owner. Benchmark the states
  too — Mobbin has empty states and onboarding flows.

## Severity

Rate every finding so the designer knows what to do Monday morning.

- 🔴 **High** — breaks the task, misleads the user, or ships a bug into code
  (e.g. a wrong-direction action, a misspelled token).
- 🟡 **Medium** — real friction or inconsistency, not blocking.
- 🟢 **Low** — polish; ship-safe but worth noting.
- 🔵 **Fix before share** — *not a design flaw.* Placeholder/dummy data that will
  distract reviewers. Separate class because it's about the review, not the design.

## The scorecard (this is the "benchmark")

Lead the report with a scorecard — it's what makes this a *benchmark* rather than
a critique, and it's the most shareable, portfolio-legible part of the output.

1. **Per-dimension score (0–5)** for each of the five dimensions. Anchor the score
   in the findings: mostly-Low → 4–5, a Medium or two → 3, any High → ≤2.
2. **Competitive-position line** — a one-sentence read of where the design sits
   versus the competitor set: *ahead of / on par with / behind* the market, and
   on what axis. Ground it in the benchmark evidence, not vibes.
3. **Severity tally** — counts of High / Medium / Low / Fix-before-share.

Keep it honest and calibrated. A design that's genuinely good should score well;
inflation makes the tool useless. State the scoring basis in the footer.

## Convention vs differentiation (don't flatten novelty)

When the design diverges from what competitors do, it is **not automatically a
problem.** Sort every divergence into one of three buckets:

- **Conventional (safe)** — matches the market; low risk. Note it and move on.
- **Novel & good (a differentiator)** — diverges deliberately and well; a strength
  to *protect*, not fix. Say so explicitly.
- **Novel & risky (reconsider)** — diverges without a clear payoff; flag it.

A skill that pushes every deviation toward the market average makes everything
look the same. Name the differentiators.

## Popularity ≠ correctness

Mobbin shows what's *common*, not what's *best*, and competitors ship bad patterns
too. Guardrails:

- Call something a **convention** only when a clear majority of the **direct**
  competitor set does it. One example is an anecdote, not a standard.
- Flag **shared anti-patterns** — a common pattern that's actually bad — rather
  than recommending it because it's popular.
- Surface **counter-evidence**: if a strong competitor *disagrees* with a proposed
  change, show it. (E.g. "you renamed the tab to 'Jobs', but Jobber calls it
  'Schedule'.") Honest tension is more useful than false consensus.
- Look for **whitespace**: where *no* competitor does something well, that gap is
  often the highest-value finding — and no screenshot will hand it to you.

## Lead with what's working

Before the fixes, name the **correct** decisions — one line each on why they're
right. A review that's all problems is neither balanced nor trustworthy, and the
designer needs to know what *not* to touch. Call out deliberate differentiators
here too (see above) so they're protected rather than normalized away. This is
also kinder, which matters when someone's handing you their work.

## Prevalence benchmark

The neutral, positive mirror of the fix list: a table of what the design *already*
matches in the market.

| Pattern | Apps that do it | In-industry | Cross-industry |
|---|---|---|---|
| [pattern in the design] | App A (fintech), App B (travel)… | common / rare | holds / doesn't |

This is the evidence behind the competitive-position line in the scorecard, and it
tells the designer where they're already conventional (safe) — so the review isn't
only a to-do list. Rate on **two axes**: how common in the *direct* set
(*universal* = nearly everyone, *common* = a clear majority, *rare* = a few), and
whether the pattern also **holds cross-industry**. Cross-industry universality is
the strongest signal there is — it means the pattern survives outside your niche's
shared habits; something merely common in-industry might just be a local blind
spot everyone copied.

## Decision support

When the design, the user, or a canvas annotation raises an **either/or**
("dropdown or pills?", "one CTA or two?"), don't just weigh it — **resolve it.**
Show both options briefly, then recommend one grounded in competitor evidence:
*"Dropdown on the home card, pills on the analytics screen — mirrors Stripe."* A
review that answers the open question is worth far more than one that lists
trade-offs and leaves the call to the reader.

## Recommended follow-ups

Don't half-do the deep passes — hand them off to the sibling skills and say so at
the end of the report:

- `design:ux-copy` — a full voice/tone pass across the copy (the review only spots
  the worst offenders).
- `design:accessibility-review` — a complete WCAG audit (the review does a quick
  computed-contrast pass, not the full thing).
- `design:design-system` — token consolidation and naming cleanup when hygiene
  issues are widespread.

Name only the ones this particular design would actually benefit from.

## Finding anatomy

Each finding in the report should carry:

- **A cropped screenshot of the element** — `get_screenshot(nodeId)` on the
  finding's node, so the reader *sees* what's being critiqued, not just a code.
- **ID** — `N1`, `C3`, `D1`… (dimension letter + number) for easy reference.
- **A clickable "Open in Figma ↗" deep link** — built from the file URL +
  `?node-id=<hyphenated-node-id>`, so the designer jumps straight to the layer. A
  bare node ID is neither seeable nor clickable; don't rely on it alone.
- *No Figma this run?* Drop the crop and the link, label the finding *source:
  description* (or *screenshot*), and **never invent a node ID** to fill the slot.
- **Severity badge.**
- **The exact quoted string or token** — verbatim, in monospace.
- **What's wrong + why it matters** — one or two sentences, tied to a heuristic.
- **Fix** — one concrete, specific change.
- **Backs** — which competitor screenshot(s) support the point (bind evidence to
  claim).
