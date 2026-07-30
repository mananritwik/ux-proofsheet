# Evidence tiers & graceful degradation

ux-proofsheet is only as credible as its evidence. This file defines what counts
as evidence, how authoritative each source is, and how to behave when a source is
missing. Tag every finding with its source so a screenshot-backed claim and a
spec-backed claim are never conflated.

## The tiers

### Tier 1 — real competitor artifacts (v1 backbone)

Real screens of what apps **actually ship**: Mobbin screens/flows/sections, or a
competitor's live product. This is the authority for *"how do competitors really
solve this pattern?"* Descriptive truth. Everything in v1 leans on Tier 1.

- **Cite:** the permanent `mobbin_url` (never the short-lived thumbnail URL).
- **Strength:** it *is* the competitor's artifact — highest authority for patterns.
- **Limit:** shows current UI, not the underlying tokens/system.

### Tier 2 — authoritative systems (roadmap; light in v1)

Real, published design systems: a competitor's actual system via the Figma MCP
(when you have the file), or canonical references like Material 3 / Apple HIG used
as baselines. Best for the **token/visual-system layer** — exact spacing scales,
type ramps, color roles — which screenshots show but don't quantify.

- **Cite:** the system + version, tagged as "reference baseline."
- **Strength:** quantified, precise ("their scale steps 4/8/12/20; yours jumps").
- **Limit:** you rarely have a *specific competitor's* real tokens (their Figma is
  private), so this is usually canonical baselines + the user's own system.

### Tier 3 — community specs (roadmap; inspiration only)

Community-authored DESIGN.md files (designmd.ai / designmd.co registries). These
are someone's *idea* of a brand's system, not the brand's artifact.

- **Never** cite a Tier 3 spec as "how competitor X does it."
- Legitimate use is **generative** (a companion DESIGN.md-builder), not
  evaluative benchmarking. Keep it off the benchmark grid.

### Provenance is the real axis

Format doesn't determine authority — *source* does. A first-party Atlassian
DESIGN.md is Tier 2; a community "Atlassian-inspired" entry in the same registry
is Tier 3. Same file format, different authority. Always tag provenance, never the
transport (CLI vs MCP vs screenshot).

## Layered, not flat

Sources own different layers of the review:

- **Pattern / interaction layer** → Tier 1 (Mobbin, real products). "How do
  competitors structure this flow?"
- **Token / visual-system layer** → Tier 2 (Figma, canonical systems). "How do
  their color roles, type ramp, and spacing compare to mine?"

Don't merge them into one undifferentiated stream. A pattern claim and a token
claim are different kinds of evidence.

## Graceful degradation

The skill must stay useful when a source is missing — "degraded" means a
different *source*, not weaker *rigor*.

| Situation | Behavior |
|---|---|
| **Mobbin connected** | Full path: real screenshots, image-rich benchmark grid (Tier 1). |
| **Mobbin NOT connected** | Web-search for real competitor patterns; cite/link them. Run the Figma token + heuristic pass in full. Header note: *"Mobbin not connected — competitor evidence is link-based, not screenshot-based."* Still evidence-based; just link-rich, not image-rich. |
| **Figma NOT connected / pasted image** | Critique from the screenshot (hierarchy, copy, patterns). No node IDs, no token extraction — say so. |
| **Neither** | Ask for a Figma node URL, a screenshot, or a written description. |

The one unbreakable rule across every path: **never fabricate.** No invented
`mobbin_url`, no invented token, no "this is universal" without a real source. An
honest link-based fallback beats a pretty hallucinated one.
