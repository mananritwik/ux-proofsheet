# Mobbin search recipes

How to turn a design's sections into precise Mobbin queries that return the right
real-world evidence. The goal is a repeatable formula, not a fixed list of apps —
so it works for any product category.

## Pick the right tool

Mobbin models UI three ways. Using the wrong tool is the most common reason a
search returns weak results.

| You're reviewing… | Tool | Platform param? |
|---|---|---|
| A mobile or web-app **screen** (home, list, settings, detail) | `search_screens` | **required** — `"ios"` or `"web"` |
| A multi-step **flow** (onboarding, checkout, signup, upgrade) | `search_flows` | **required** — `"ios"` or `"web"` |
| A **website marketing section** (pricing, hero, footer, features) | `search_sections` | **none** — it's web-only |

Reviewing a marketing/landing page? Use `search_sections`, not `search_screens`.
This is the gap most reviews miss.

## The query formula

Describe **one screen, in plain language**, as the elements you'd see and how they
relate:

```
[category / app] + [screen or pattern] + [role or context] + [key UI element]
```

Good:
- `"field service home dashboard for the business owner with a money-owed summary"`
- `"invoice list with paid and overdue status badges"`
- `"workspace switcher bottom sheet with a list of teams"`
- `"pricing page with a three-tier plan comparison table"` (→ `search_sections`)

Avoid:
- Combining multiple screens in one query (search them separately).
- Negations ("without ads").
- Vague style words ("modern", "clean", "beautiful").
- Disconnected keyword lists.

Name a **specific app** to filter to it: `"Jobber home screen owner dashboard"`,
`"Stripe now-playing date range control"`. Do this when you want a named
competitor's exact screen; search the *pattern* when you want variety.

## Parameters

```
search_screens(
  query:   "<one screen, plain language>",
  platform:"ios" | "web",        # required
  limit:   6,                     # 4–6 is plenty; run more searches, not bigger ones
  # mode defaults to "deep" (intent-aware) — no need to set it
  # image_format defaults to webp; pass "jpg" if a client can't render webp
  exclude_screen_ids: [...]       # skip screens you've already seen for fresh variety
)

search_flows(query, platform, limit: 3)      # limit small — flows are heavy
search_sections(query, limit: 6)             # no platform param
```

## Coverage target

For each section of the design, run **2–3 searches from different angles**. Across
the whole review aim for ~10–20 screens spanning **6+ apps**, and make sure the
user's named **direct competitors** are represented (search them by name).

**Always run a cross-industry sweep.** For each key pattern, search it *outside*
the design's own category too — the same element done well somewhere else entirely.
Mobbin doesn't filter by industry, so just describe the pattern without a category
word and name apps from other verticals: `"bottom navigation with a more tab"`
(you'll get travel, social, finance), `"empty state with a friendly illustration
and one CTA"`, `"account switcher in the top header"`. The point is breadth a busy
leader can't gather by hand. Screens and flows are the primary unit, but you can
also point a search at a single **element** across the whole database when that's
what the review needs (e.g. the best nav bars anywhere, regardless of app).

## When results are weak

- **Irrelevant?** Add context — category, user role, or a specific UI element.
  `"business owner revenue dashboard mobile"` beats `"dashboard"`.
- **Can't find a specific app?** Search the *pattern*, not the app. No Housecall
  Pro? Try `"field service job schedule home screen"` — you'll find equivalents.
- **Not enough variety?** Use `exclude_screen_ids` to skip screens you've shown.
- **Always look at the returned image** before describing what an app does — the
  tools return screenshots inline; read them, don't infer from metadata.

## Worked examples

```
# Owner home dashboard, money-first
search_screens("field service home dashboard owner with money owed summary", platform="ios", limit=6)

# Invoice list with status
search_screens("invoice list with paid overdue status badges fintech", platform="ios", limit=6)

# Team switcher
search_screens("workspace team switcher bottom sheet list of teams", platform="ios", limit=6)

# A named direct competitor's exact screen
search_screens("Jobber business health metrics home", platform="ios", limit=4)

# An onboarding flow
search_flows("B2B SaaS onboarding welcome business setup checklist", platform="ios", limit=3)

# A marketing pricing page (web section — no platform)
search_sections("SaaS pricing page three tier plan comparison with toggle")
```
