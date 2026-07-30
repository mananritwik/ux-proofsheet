---
name: ux-proofsheet
description: >-
  Benchmark a UI/UX design against how real apps actually ship. Give it a Figma
  URL, screenshot, or a description of an interaction; it reads the design, pulls
  real competitor screens from Mobbin for the same patterns, and produces a
  scored, evidence-backed HTML review — a competitive-position scorecard, findings
  tied to Figma nodes, and a grid of real competitor screenshots to borrow from.
  Use whenever the user wants design feedback grounded in real competitor
  examples, or says things like "how do others handle this?", "review my design vs
  competitors", "compare my wireframe to similar products", "find examples of how
  [app] does X", "is this pattern conventional or novel?", "benchmark my UX", or
  "competitive design review", or shares a Figma link about UX quality or patterns.
  Works for iOS, web app, and web marketing screens. Not for pure visual/brand
  critique with no competitive angle, accessibility-only audits, or generating new
  UI — this evaluates an existing design against the market.
---

# ux-proofsheet

Turn a design into a **proofsheet**: your screen held up against a grid of real
competitor screens, with a scored critique that says what's working, what to
fix, and what the market does differently — every claim backed by a real
screenshot or a cited source.

The output is an **HTML report** (a self-contained artifact), because the value
is visual and the user will want to keep, share, and revisit it.

**What this is — and isn't.** ux-proofsheet is a **UX / pattern benchmark, not a
pixel-perfect comparison.** It evaluates structure, hierarchy, flows, patterns,
and copy against how real competitors ship the same thing. The screens in the
report are clean HTML recreations built from the design's own tokens — faithful to
the layout, not pixel-exact renders — and every finding links to the exact layer
in Figma for anyone who wants the real pixels. Optimize for insight about the UX,
not fidelity of the screenshot.

**What it's for, and who reads it.** This is a **first-pass** benchmark. Its job is
to compress the research a product leader would otherwise do by hand — signing up
for apps, screenshotting, cataloguing how others solve a pattern — and to reach the
apps you *can't* sign up for or that live in other markets. It casts a wide net:
**same-industry and, on every run, deliberately cross-industry**, at the screen,
flow, and element level, so you stay current and can challenge your own
assumptions. The scored judgment is a **starting point for a conversation, not a
ruling**: a junior designer can take it as guidance, a senior can use it to
pressure-test taste and stay lock-step with the market, and the reader always
decides how much to take. Write findings so they work both as a personal digest
*and* as discussion-ready feedback to a designer. **UX copy is one of the
highest-value axes here** — comparing real wording across many apps is exactly the
thing intuition alone can't keep current on.

## Tools this skill uses

- **Figma MCP** (`get_metadata`, `get_design_context`, `get_screenshot`) — read
  the design being reviewed: structure, node IDs, labels, tokens, and the
  rendered image.
- **Mobbin MCP** (`search_screens`, `search_flows`, `search_sections`) — find
  real competitor screens, flows, and website sections. This is the primary
  evidence source.
- **Web search** — the fallback evidence source when Mobbin is unavailable, and
  a supplement for competitor context (who competes with whom, recent redesigns).

If neither Figma nor a design artifact is available, ask the user for a Figma
node URL, a screenshot, or a written description before proceeding.

## Step 0 — Preflight: check what's connected, degrade gracefully

Before doing anything, establish which evidence sources you have. **A missing
Mobbin connection must not silently gut the review** — it changes the evidence
source, not the rigor.

- **Mobbin connected** → full path. Real screenshots, image-rich benchmark grid.
- **Mobbin NOT connected** → fallback path. Web-search for real competitor
  patterns and cite/link them; run the Figma-only token + heuristic pass in full.
  State plainly in the report header: *"Mobbin not connected — competitor
  evidence is link-based, not screenshot-based."* The review is still
  evidence-based; it's just link-rich rather than image-rich. Do not fabricate
  screenshots or pretend a pattern is universal without a source.
- **Figma NOT connected / design is a pasted image** → work from the screenshot.
  You can still critique hierarchy, copy, and pattern choices; you just can't
  cite node IDs or extract tokens. Say so.

Never invent a `mobbin_url`, a competitor claim, or a token value you didn't
actually retrieve. Overclaiming is the one thing that destroys this skill's
credibility.

## Step 1 — Read the design (and its own notes)

If a Figma URL is provided:

1. `get_metadata(fileKey, nodeId)` — get the structure and the **node IDs**. You
   will cite these on every finding so the designer can click straight to the layer.
   For a real board this response can be **huge** (hundreds of KB) and overflow
   context — when it does, it's saved to a file. Don't dump it: parse it with
   jq/python (or a subagent), pulling the top-level frames + their names/ids and
   any text-layer annotations. Screen-title and "Old"/"New" group labels live in
   the node `name`s.
2. `get_design_context(nodeId, fileKey)` — labels, layout, component hierarchy,
   and the **design tokens** (colors, type, spacing). Extract the palette and
   type — you'll **recreate the screens in HTML on these tokens** (see "Rendering
   the visuals") and audit token hygiene.
3. `get_screenshot(nodeId, fileKey)` — the rendered image, **for you to read and
   analyse**. Look at it carefully (never describe a screen from metadata alone) —
   but render the report from a faithful HTML recreation, not the raw export, since
   the screenshot URL expires (see "Rendering the visuals"). Screenshot individual
   finding nodes too when it helps you study the detail.

**Large exploration boards:** a real refresh board can hold dozens of frames
across many themes. Reviewing all of them exhaustively is rarely useful — pick the
primary flows/screens (the anchor change, the ones the annotations call out),
review those well, and **state plainly what you did and didn't cover** rather than
implying full coverage.

A node ID by itself is not something a reader can see or click to. So for every
finding, do two things: show the element's cropped screenshot, and turn the node
into a **clickable Figma deep link** by appending `?node-id=<nodeId>` (hyphenated,
e.g. `575-4638`) to the file URL — `https://figma.com/design/<fileKey>/<name>?node-id=575-4638`.
That's what "traceable" actually means: seeable and one click from the layer.

Then build a short inventory of the design's own choices:

- Every distinct section / interaction pattern (nav, hero, list, primary CTA,
  empty states, etc.).
- Product category (fintech, field service, productivity, social…) and platform
  (iOS / web app / web marketing).
- The user goal for each section.
- **Every screen provided — cover them all.** If the user shares several screens
  (home, menu, switcher, profile…), review *all* of them, not just the first.
  When there are several, organize the report by screen with the dimensions
  nested inside.
- **States and variants, not just the happy path.** For each screen note which
  states exist and should be reviewed — empty, loading, error, first-run /
  onboarding, and role / permission variants (owner vs member). These are where
  designs and competitors differ most; a design that nails the full screen but
  has no empty state is not done. Benchmark the states too (Mobbin has empty
  states and onboarding flows).
- **Read any annotations on the canvas.** Designers leave notes in text layers
  ("popups not ideal for mobile", "TBD"). Extract them and address them directly
  in the review — answering the team's own open questions is high-value.

If the input is a screenshot or description only, extract the same inventory from
what you can see.

## Step 2 — Define the comparison set (same-industry AND cross-industry)

Before searching, name **who** you're benchmarking against. Always build the set
from **both** — the cross-industry half is required on every run, not optional:

- **Direct / same-industry** — same category and audience (the apps the user names
  plus obvious rivals). This tells you the *local convention*.
- **Cross-industry / analogous** — the *same pattern done well in a different
  industry* (e.g. a nav from a travel app, an empty state from a social app, a
  money-owed hero from consumer fintech for a B2B invoicing tool). A pattern that
  holds across fintech, travel, and social is a far stronger signal than one that's
  merely common in your niche, and cross-industry examples break you out of the
  blind spots a whole industry can share. This is the half a busy product leader
  rarely has time to gather by hand, so make it count.

If the user hasn't said who they compete with, propose a set (a few direct + a few
cross-industry) and confirm in one line, or infer it and state the assumption.
Web search helps for the direct set; Mobbin's breadth is what makes the
cross-industry sweep cheap.

## Step 3 — Search for real competitor evidence

For each section in your inventory, run **2–3 searches from different angles**.
Pick the right Mobbin tool for the artifact:

- **Mobile screens** → `search_screens(query, platform="ios"|"web")`
- **Multi-step flows** (onboarding, checkout, signup) → `search_flows(...)`
- **Website marketing sections** (pricing, hero, footer, features) →
  `search_sections(query)` — note: `search_sections` has **no** `platform`
  parameter (it's web-only). This is the correct tool for marketing pages; do not
  use `search_screens` for them.

See `references/search-recipes.md` for the query-construction formula and worked
examples. Key rules: describe **one screen per query** in plain language, name a
specific app when you want its exact screen, avoid vague style words, and prefer
several precise searches over one broad one (4–6 results per search is plenty).

**Look at every screenshot before you describe it.** Mobbin returns the image
inline — read it. If a search is weak, rephrase with more context (category,
role, specific UI element) or use `exclude_screen_ids` to get fresh results.

Target: enough evidence to cover every section — roughly 10–20 screens across
6+ different apps, including the user's named direct competitors.

**Fallback (no Mobbin):** web-search for the same patterns, collect real,
linkable examples (app-teardown sites, competitor sites, published screenshots),
and cite them. Be honest that these are links, not embedded shots.

## Step 4 — Assign each piece of evidence a tier

Not all evidence is equal. Tag each finding's source so a screenshot-backed claim
and a spec-backed claim are never conflated. See `references/evidence-tiers.md`
for the full model. In short:

- **Tier 1 — real competitor artifacts** (Mobbin screens, live products). The
  authority for "how competitors actually solve this." This is the v1 backbone.
- **Tier 2 — authoritative systems** (a real design system via Figma; canonical
  systems like Material / HIG as reference baselines). For the token/visual layer.
  *(Roadmap — light in v1.)*
- **Tier 3 — community specs** (DESIGN.md registries). Inspiration only; never
  cite as "how competitor X does it." *(Roadmap.)*

## When the design poses a choice — answer it

If the design (or the user, or a canvas annotation) raises an **either/or** —
"dropdown or segmented pills?", "one CTA or two?" — don't just critique; **decide.**
Show both options briefly, then recommend one, grounded in competitor evidence:
*"Dropdown on the home card, pills on the full-analytics screen — mirrors Stripe:
compact on the gateway, full control on the dedicated dashboard."* A review that
resolves the open question is worth far more than one that lists trade-offs.

## Step 5 — Build the scored HTML report

Produce a self-contained HTML artifact using `assets/report-template.html` as the
structure and theming it with the tokens you extracted in Step 1. It leads with a
**scorecard** (that's the "benchmark" — a competitive-position read, not a
qualitative-only critique) and follows with evidence.

**Degraded-path substitutions — read before building.** The section spec below is
written for the full Mobbin+Figma path. When a source is missing, substitute *in
place* and never fabricate the missing artifact:

| Missing source | What it removes | Substitute — never invent |
|---|---|---|
| **Figma** (text or screenshot input) | element crops, "Open in Figma" links, node IDs, token audit, computed contrast | Omit the crop and the link; label the finding *source: description* (or *screenshot*). Do **not** invent a node ID. For contrast, do **not** run or fake `contrast.py` — write "contrast not computed — no tokens extractable; likely risk pairs X/Y; re-run with tokens." |
| **Mobbin** | benchmark screenshots, `mobbin_url` | Use a **cited web link** per card, labelled "link, not embedded — Mobbin not connected." Do **not** invent a `mobbin_url`. |
| **Text-only input** (no image at all) | the "design under review" screenshot | Reconstruct the layout as a labelled structural list marked "reconstructed from description — no render available." |

If you can't source something, say so in the report. Inventing a node ID, a
`mobbin_url`, or a contrast number is the one unforgivable failure.

Required sections, in order:

1. **Header + scorecard** — one-line verdict (say whether the issues are
   *structural* or *cosmetic*), a competitive-position score, a per-dimension
   score row, and a severity tally (High / Medium / Low + "Fix before share").
   See the rubric for how to score.
2. **The design under review** — a prominent, faithful **HTML recreation** of the
   actual screen(s), built from the extracted tokens (see "Rendering the visuals"),
   so the reader sees what's being critiqued without any expiring image link. Cover
   **every** screen provided. When there are two states, show **Old → New / current
   vs proposed** side by
   side. Handle a pasted raster gracefully ("copy not extractable"). *If the input
   is a text description with no image, reconstruct the layout as a labelled
   structural list marked "reconstructed from description — no render available"
   (per the substitution table).*
3. **What's working** — a short set of positive callouts naming the *correct*
   design decisions before the fixes. A review that's all problems is neither
   balanced nor trustworthy; name the good calls (and protect the differentiators).
4. **Findings by dimension** — Navigation & IA, UX copy, Visual & tokens,
   Placeholder data ("Fix before share"), Accessibility. Each finding carries a
   **recreated HTML mock of the specific element** (built from the tokens; embed a
   real crop only when egress allows), an ID (`N1`, `C1`…), a
   clickable **"Open in Figma ↗"** deep link (built from the node ID), a severity
   badge, the exact quoted string/token, and a concrete Fix. Show the element —
   don't just name its node. *(No Figma? Omit the crop and link, label the finding
   "source: description", and never invent a node ID — see the substitution
   table.)* For the accessibility pass, run `scripts/contrast.py` on the extracted
   token pairs so contrast findings are **measured** ("`#798087` on `#fff` =
   4.0:1, fails AA"), not guessed — but if no tokens were extractable, print the
   "contrast not computed" note rather than running or faking it. Separate
   *deviation = risk* from *deviation = differentiation* (see rubric).
5. **Benchmark grid** — the proofsheet. For each competitor: a **recreated mock of
   the relevant element** for the inline visual (embed the real screenshot only
   when egress allows), the permanent `mobbin_url` link ("View ↗"), a one-line
   pattern description, and a **"Backs: [finding]"** tag binding it to a finding.
   The grid must visibly include **both same-industry and cross-industry**
   examples, and label each so the reader sees which is which. Surface
   counter-evidence too (a competitor who disagrees with a proposed change). *(No
   Mobbin? Use a cited web link per card instead of a `mobbin_url`, labelled "link,
   not embedded"; never invent a `mobbin_url`.)*
6. **Prevalence check** — a neutral table of what the design *already* gets right:
   *pattern | apps that do it | prevalence*. Rate prevalence on **two axes**: how
   common in the *direct* set, and whether it also holds **cross-industry** —
   because a pattern that's universal across industries is a far stronger signal
   than one that's just common in your niche. This is the positive mirror of the
   fixes and the evidence behind the competitive-position score.
7. **Prioritized next steps** — a numbered list ordered by impact × effort.
8. **Recommended follow-ups** — hand off deeper passes to the sibling skills
   rather than half-doing them: `design:ux-copy` for a full voice/tone pass,
   `design:accessibility-review` for a complete WCAG audit, `design:design-system`
   for token consolidation. Name the ones this design would benefit from.
9. **Footer** — methodology + provenance + limitations. Note which tokens it was
   built on and that it's condensed, not pixel-final.

### Rendering the visuals — recreate, don't screenshot (this is the point)

Because this is a UX benchmark, not a pixel diff, you **recreate the UI in HTML/CSS
from the extracted tokens** rather than embedding raster screenshots. Recreation is
intentional, not a fallback: it's self-contained and permanent, on-brand (your
tokens), and lets you highlight the exact element a finding is about — which a flat
screenshot can't. The exact pixels are never lost: every finding links to the layer
in Figma. (It also sidesteps the fact that Figma/Mobbin screenshot URLs are
short-lived signed links that expire within minutes and would leave a delivered
file blank.) **Never hotlink those URLs in the report.**

- **The design under review + element crops:** rebuild the screen(s) and the
  specific elements as HTML from the design tokens. The Figma screenshot you
  captured is for *you* to read and analyse — render the report from a faithful
  HTML recreation, not the raw export. Label it "recreated from the frames on the
  design's tokens." (Highlight the element a finding is about — a recreation can
  do this; a screenshot can't.)
- **Competitor screens:** recreate the *relevant element* (the switcher, the
  dispute buttons, the nav bar) as a small labelled mock for the inline visual, and
  always cite the permanent `mobbin.com/screens/…` link ("View ↗") so the reader
  can open the real screen. The screen link never expires; the thumbnail URL does.
- **Embedding real screenshots is rarely needed.** The recreations plus the Figma
  and Mobbin links already carry it. If someone specifically wants pixel-exact
  frames *and* the runtime has network egress, `scripts/embed_images.py` can inline
  them at capture time — otherwise don't bother, and never hotlink and hope.

Rule: a delivered report must render with **zero dependence on expiring URLs**, and
point to Figma for anyone who wants exact pixels.

## Output rules

1. **Scorecard first, evidence always.** Lead with the score; back every claim
   with a real screenshot (`mobbin_url` cited) or a linked source.
2. **One search per claim.** Never reference an app you didn't actually pull.
3. **Show, don't just cite.** Every finding shows a cropped screenshot of the
   element and links to it via a clickable "Open in Figma ↗" deep link — a bare
   node ID is neither seeable nor clickable.
4. **Quote exact strings.** "Good Morning! Ritwik" and `outline-deafult`, not
   "the greeting" — precise and verifiable.
5. **Popularity ≠ correctness.** Mobbin shows what's common, not what's best. Call
   something a "convention" only when a clear majority of the *direct* set does it,
   and flag shared anti-patterns.
6. **No fabrication.** No invented URLs, tokens, or competitor claims. State the
   evidence source and its tier.
7. **Render durably.** Recreate the UI in HTML from the extracted tokens; never
   hotlink expiring Figma/Mobbin URLs. Embed real screenshots only when the runtime
   has egress. A delivered report must not depend on a URL that can expire.
8. **Balance.** Name what's working, not only what's broken — and protect
   deliberate differentiators instead of normalizing them toward the market.
9. **Cover everything provided.** Every screen the user shares, and its states
   (empty / error / first-run / roles) — not just the happy-path home screen.
10. **Resolve, don't just weigh.** When there's an either/or, recommend one option
    with evidence rather than only listing trade-offs.

## Reference files

- `references/critique-rubric.md` — the dimensions, heuristics, severity levels,
  the scoring method, and the convention-vs-differentiation framing. Read this
  before writing findings.
- `references/evidence-tiers.md` — the tiered source model, provenance rules, and
  the graceful-degradation behavior.
- `references/search-recipes.md` — the Mobbin query-construction formula, tool
  selection (screens vs flows vs sections), parameters, and worked examples.

## Roadmap (not in v1)

- **v2 — token layer (Tier 2):** quantified token comparison via Figma + optional
  designmd.co (`get_full_system`, `generate_css_variables`, `certify_conformance`),
  provenance-tagged.
- **v3 — companion generator:** turn a review into a starter DESIGN.md
  (benchmark → codify → generate).
