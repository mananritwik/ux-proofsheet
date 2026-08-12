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
  [app] does X", "is this pattern conventional or novel?", "benchmark my UX",
  "competitive design review", "quick proofsheet", or shares a Figma link about UX
  quality or patterns. Works for iOS, web app, and web marketing screens. Not for
  pure visual/brand critique with no competitive angle, accessibility-only audits,
  or generating new UI — this evaluates an existing design against the market.
---

# ux-proofsheet

Turn a design into a **proofsheet**: scored critique + competitor evidence.
Output a self-contained **HTML report**. This is a UX/pattern benchmark, not a
pixel diff — recreate UI from tokens; cite permanent Mobbin + Figma links for
real pixels. **First-pass** for judgment; junior guidance / senior pressure-test.
**UX copy is a high-value axis** — always include a copy matrix when copy is in scope.

Paste-ready prompts: `references/prompt-cookbook.md`.

## Tools

- **Figma MCP** — `get_metadata`, `get_design_context`, `get_screenshot`
- **Mobbin MCP** — `search_screens`, `search_flows`, `search_sections` (primary evidence)
- **Web search** — fallback when Mobbin is missing; competitor context

No design artifact? Ask for a Figma URL, screenshot, or description before proceeding.

## Step 0 — Preflight + mode

**Preflight (full path):** confirm Mobbin can return a search and Figma can
`get_design_context` / `get_screenshot`. If Mobbin is down, use the degraded path
(below) — do not silently gut the review.

**Mode** (ask once if unclear; default Full when a Figma board is attached):

| | **Quick** | **Full** |
|---|---|---|
| Scope | 1 screen / 1 pattern | All provided screens + key states |
| Evidence | 4–6 cards, 3+ apps | ~10–20 screens, 6+ apps |
| Report | Scorecard, what's working, top findings, thin grid, next steps | All sections below incl. prevalence, copy matrix, share summary |

## Step 0b — Degrade gracefully

| Missing | Behavior |
|---|---|
| **Mobbin** | Web-search + cite links. Header: *"Mobbin not connected — competitor evidence is link-based."* Never invent `mobbin_url`. |
| **Figma** / pasted image | Critique from image; no node IDs / tokens. Say so. No fake contrast. |
| **Text only** | Reconstruct layout as a labelled structural list. |

**Never fabricate** a `mobbin_url`, node ID, token, or contrast number.

## Step 1 — Read the design

1. `get_metadata` — node IDs + structure. Large dumps → save to file and run
   `scripts/parse_figma_metadata.py` (do not paste the raw tree).
2. `get_design_context` — labels, hierarchy, **tokens** (for HTML recreations + hygiene).
3. `get_screenshot` — study the image yourself; report visuals are recreations.

**Large boards:** list candidate frames from the parser, pick primary flows
(annotations, Old/New, named screens), and **state what you skip**.

Inventory: sections/patterns, category, platform, user goals, **every screen
provided**, states (empty/loading/error/first-run/roles), canvas annotations.

## Step 2 — Mid-run confirm (mandatory)

Before searching, send **one short confirm**:

```
Scope: [screens/frames] · Mode: Quick|Full
Direct: [apps] · Cross-industry: [apps]
Annotations I'll address: […]
OK to search?
```

If the user already named competitors and screens tightly, confirm in one line
and proceed. Always include **both** same-industry and cross-industry.

## Step 3 — Search evidence

2–3 searches per section from different angles. Tool pick: screens / flows /
`search_sections` (marketing; no platform param). See `references/search-recipes.md`.

**Retry ladder:** add context → narrow element → drop category (cross-industry) →
`exclude_screen_ids` → disclose weakness (never invent).

**Named-competitor guarantee:** app-name search → pattern search → closest
analogue + disclose *"X not found — used Y"*. Look at every screenshot before citing.

## Step 4 — Evidence tiers

Tag sources. Tier 1 (Mobbin / live) = pattern authority. Tier 2 (systems) = light
in v1. See `references/evidence-tiers.md`. Resolve either/or choices with a
recommendation + evidence (`references/critique-rubric.md`).

## Step 5 — Scored HTML report

Use `assets/report-template.html`. Theme with extracted tokens. **Recreate**
screens/elements in HTML/CSS — never hotlink expiring Figma/Mobbin image URLs.
Always pair recreations with permanent **View ↗** (Mobbin) and **Open in Figma ↗**.

### Degraded substitutions (never invent)

| Missing | Substitute |
|---|---|
| Figma | No crop/link/node ID; label *source: description*. Contrast: *"not computed — no tokens"*. |
| Mobbin | Cited web link per card; *"link, not embedded"*. |
| Text-only | Labelled structural list for "design under review". |

### Sections (Full; Quick = ★ only)

1. ★ **Header + scorecard** — verdict (structural vs cosmetic), position, dimension scores, severity tally. Rubric for scoring.
2. ★ **Design under review** — HTML recreation of every in-scope screen (Old→New if two states).
3. ★ **What's working** — protect differentiators.
4. ★ **Findings by dimension** — Nav & IA, UX copy, Visual & tokens, Placeholder ("Fix before share"), Accessibility. Each: recreated crop, ID, Figma deep link, severity, quoted string, Fix, Backs. Run `scripts/contrast.py` when tokens exist.
5. **UX copy matrix** — your string vs 3–5 apps (required on Full when copy is in scope). See rubric.
6. ★ **Benchmark grid** — recreated element mock + permanent `mobbin_url`, same- + cross-industry labels, "Backs: [finding]", counter-evidence.
7. **Prevalence** — pattern \| apps \| in-industry \| cross-industry.
8. ★ **Prioritized next steps**
9. **Share summary** — pasteable Slack/Notion block (verdict, position, High/Med IDs, top 3 steps) + pasteable finding cards for High/Med.
10. **Follow-ups** — sibling skills + **continue commands**: dig into `N1`, only `[app]`, re-run copy, Quick on `[screen]`.
11. **Footer** — methodology, tokens used, limits, mode (Quick/Full).

## Output rules

1. Scorecard first; every claim backed by a real pull or linked source.
2. One search per claim — never cite an app you didn't retrieve.
3. Show recreations + clickable Figma/Mobbin links (not bare IDs).
4. Quote exact strings/tokens.
5. Popularity ≠ correctness; convention = majority of **direct** set only.
6. No fabrication.
7. Durable HTML — recreate; never hotlink expiring image URLs.
8. Balance: name what's working; protect differentiators.
9. Cover every in-scope screen + key states.
10. Resolve either/ors with a recommendation.
11. Confirm scope before searching (Step 2).

## Reference files

- `references/critique-rubric.md` — dimensions, severity, scoring, copy matrix, finding cards
- `references/evidence-tiers.md` — tiers + degradation
- `references/search-recipes.md` — queries, retry ladder, named-competitor guarantee
- `references/prompt-cookbook.md` — paste-ready prompts

## Scripts

- `scripts/contrast.py` — measured WCAG ratios from token pairs
- `scripts/parse_figma_metadata.py` — triage large `get_metadata` dumps
- `scripts/embed_images.py` — optional; only if you truly have durable local assets (not the default path)
