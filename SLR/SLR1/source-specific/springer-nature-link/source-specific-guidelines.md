# Springer Nature Link

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`

Save final JSON files in `final-searches/` by query ID and source cell. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full Springer Nature Link platform
- URL: https://link.springer.com/search
- Field: Raw Keywords over title, abstract, and body text
- Evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. Reconcile source years with exact visible detail dates.
- Language: Apply the `En` facet and confirm report language during screening.
- Publication type: Apply no content type, peer review, access, or full text filter. Content facets overlap and card labels do not prove a complete eligible union.
- Subject: Apply no Discipline or Subdiscipline filter. Source classifications can place aerospace records outside an aerospace category.
- Ordering: Oldest first.

## Source translation

Use the concepts, compounds, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Use uppercase Boolean operators and full parentheses. Use no proximity or pair expansion.

- Literal `L(s)`: One straight double quoted token or ordered phrase.
- Controlled vocabulary decision: Add no supplement. Link exposes subject filters, not a validated controlled vocabulary mapping with complete assignment and marginal recall evidence.
- Wildcard decision: Replace only the `CubeSat`, `nanosat`, and `SmallSat` population families with unquoted `CubeSat*`, `nanosat*`, and `SmallSat*`. Every wildcard partition retained all literal paths. The additional records had intended population meanings. Quoted stars do not expand, and the source has no bounded suffix form, so all other terms stay literal.

## Execution

Use one direct cell for A1, A3, B1, BG1, BG2, BC1, and BT2. Split A2 into one `M_H` cell and four fixed `M_B` cells. Split B2 by source year, with a fixed two by two `M_B` and `R` union in 2021, 2022, and 2024. Reconcile every partition by stable card path.

Keep the raw Link card path as identity. Accept only the proved same DOI `/book/` to `/referencework/` alias. For Link `/article/10.1038/<suffix>`, accept only the matching `https://www.nature.com/articles/<suffix>` canonical metadata URL without navigating to Nature. Read title, abstract, and date from Link. Retain unresolved days and exclude only a proved out of window date. See [the readiness audit](../readiness-audit.md) for the result bound.
