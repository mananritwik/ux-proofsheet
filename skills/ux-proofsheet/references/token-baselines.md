# Token baselines (Material 3 and Apple HIG)

`scripts/token_check.py` compares a design's type ramp and spacing against these
baselines. The numbers live in `token-baselines.json`; this file says where each one
comes from. All values were read from the official pages on 2026-10-26. If a page
changes, update both files together and re-run `scripts/test_token_check.py`.

Rule: no value goes in without a source URL. Where a system publishes nothing, the
baseline says so instead of filling the gap.

## Material 3: type scale

Source: <https://m3.material.io/styles/typography/type-scale-tokens>
(baseline type style tokens; sizes in sp, line heights in sp)

| Style | Size | Line height | Weight |
|---|---|---|---|
| Display Large | 57 | 64 | 400 |
| Display Medium | 45 | 52 | 400 |
| Display Small | 36 | 44 | 400 |
| Headline Large | 32 | 40 | 400 |
| Headline Medium | 28 | 36 | 400 |
| Headline Small | 24 | 32 | 400 |
| Title Large | 22 | 28 | 400 |
| Title Medium | 16 | 24 | 500 |
| Title Small | 14 | 20 | 500 |
| Body Large | 16 | 24 | 400 |
| Body Medium | 14 | 20 | 400 |
| Body Small | 12 | 16 | 400 |
| Label Large | 14 | 20 | 500 |
| Label Medium | 12 | 16 | 500 |
| Label Small | 11 | 16 | 500 |

Same page, on the ratio: Material uses the "Major Second type scale with 14 as its
key base size" (1.125), and sizes should give "impactful contrast between sizes by
avoiding small differences." Every M3 line height above is a multiple of 4.

## Material: spacing grid

Source: <https://m2.material.io/design/layout/spacing-methods.html>

- All components align to an 8dp square baseline grid.
- Icons, type, and some elements within components can align to a 4dp grid.
- Padding is measured in increments of 8dp or 4dp.

The current M3 layout pages
(<https://m3.material.io/foundations/layout/grids-spacing/spacing>) describe
spacing qualitatively and do not restate the grid. M3 density guidance still steps
padding by 4dp (<https://m3.material.io/foundations/layout/grids-spacing/density>).
So the grid is cited from the Material spacing-methods page, and the report should
say "Material 4dp/8dp grid", not "M3 spacing tokens".

## Apple HIG: iOS text styles

Source: <https://developer.apple.com/design/human-interface-guidelines/typography>
(iOS/iPadOS Dynamic Type sizes, "Large (default)" column; points)

| Style | Weight | Size | Leading |
|---|---|---|---|
| Large Title | Regular | 34 | 41 |
| Title 1 | Regular | 28 | 34 |
| Title 2 | Regular | 22 | 28 |
| Title 3 | Regular | 20 | 25 |
| Headline | Semibold | 17 | 22 |
| Body | Regular | 17 | 22 |
| Callout | Regular | 16 | 21 |
| Subhead | Regular | 15 | 20 |
| Footnote | Regular | 13 | 18 |
| Caption 1 | Regular | 12 | 16 |
| Caption 2 | Regular | 11 | 13 |

Apple publishes no scale ratio and no base size, so the tool reports none for HIG.

## Apple HIG: spacing (none published)

The HIG Layout page (<https://developer.apple.com/design/human-interface-guidelines/layout>)
tells you to respect safe areas, system margins, and layout guides. It gives no iOS
spacing increment. The "8pt grid" many iOS teams use is a community convention, not
an Apple rule. The tool therefore checks spacing against the Material grid only and
never labels an off-grid value as "violates HIG".

## What the tool adds on top (heuristics, not baseline values)

These thresholds are the tool's own judgment calls. Reports must present them as
such, never as Material or Apple rules.

- **Crowded step:** two adjacent sizes 1pt apart or with a ratio under 1.07
  (smaller than a minor-second step), unless both are baseline sizes. Backs M3's
  "avoid small differences" guidance.
- **Jump:** a step larger than the biggest adjacent step inside the chosen baseline
  (Material 16 to 22 = 1.375; HIG 22 to 28 = 1.27), where at least one of the two
  sizes is off the baseline. Using a subset of baseline sizes is fine (M3 says no
  product needs all 15 styles), so a gap between two baseline sizes never flags.
- **Off-baseline severity:** Medium when 3 or more sizes are off, or off sizes are
  used 5 or more times; otherwise Low. Off-grid spacing is Medium at 3 or more uses.
- **Spacing gap:** adjacent spacing values more than 2x apart above 16. Info only.
- **Base unit:** 8 if at least 80% of spacing values are multiples of 8, else 4 if
  at least 80% are multiples of 4, else "irregular".
- **Named ratios** for the inferred scale (Minor Second 1.067, Major Second 1.125,
  Minor Third 1.2, Major Third 1.25, Perfect Fourth 1.333, Augmented Fourth 1.414,
  Perfect Fifth 1.5, Golden 1.618) are standard interval ratios used in type-scale
  tools, listed for orientation only.
