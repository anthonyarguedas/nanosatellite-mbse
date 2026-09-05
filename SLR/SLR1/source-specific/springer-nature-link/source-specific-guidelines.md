# Springer Nature Link

Final searches saved in commit: b987ffa38f187f0d27badb27a1230e5f6e2a076d
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

Use one direct cell for A1, A3, B1, BG1, and BG2. Split A2 into one `M_H` cell and four fixed `M_B` cells. Split B2 by source year, with a fixed two by two `M_B` and `R` union in 2021, 2022, and 2024. The direct BC1 and BT2 final attempts repeatedly returned a card path across pages. Supersede those failed cells with one unchanged complete query per source year. Reconcile every partition by stable card path.

For every source year cell, set the Link source year separately and retain `--date-start 2011-01-01 --date-end <cutoff>` as the client evidence window. A detail date in another source year remains eligible when it is inside the common evidence window. Supersede any final B2 attempt that used its source year as the client exact date window.

Keep the raw Link card path as identity. Accept only the proved same DOI `/book/` to `/referencework/` alias. For Link `/article/10.1038/<suffix>`, accept only the matching `https://www.nature.com/articles/<suffix>` canonical metadata URL without navigating to Nature. Read title, abstract, and date from Link. Retain the complete visible abstract in `abstract`. Use an empty abstract only when the matching canonical page exposes none, and set `abstract_not_available: true`. Retain the raw rendered card content type in `documentType` for every retained record. Apply no publication type filter and do not infer the review publication type. Retain unresolved days and exclude only a date proved outside the common evidence window. See [the readiness audit](../readiness-audit.md) for the result bound.
