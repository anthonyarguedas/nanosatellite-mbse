# Wiley Online Library

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`

Save final JSON files in `final-searches/` by query ID and source cell. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full Wiley Online Library Articles & Chapters route
- URL: https://onlinelibrary.wiley.com/search/advanced
- Field: One Anywhere row
- Evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. Reconcile source months with visible First published dates.
- Language: Apply no source filter. Wiley exposes no language field or facet on this route. Confirm English during screening.
- Publication type: Use the Articles & Chapters record family. Apply no `PubType`, peer review, access, Collections, or full text filter.
- Ordering: Earliest first.

## Source translation

Use the concepts, compounds, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Use uppercase Boolean operators and full parentheses. Use no proximity or pair expansion.

- Literal `L(s)`: One straight double quoted token or ordered phrase.
- Controlled vocabulary decision: Add no supplement. This route exposes no validated controlled descriptor field, mapping, or hierarchy.
- Wildcard decision: Replace only the `CubeSat`, `nanosat`, and `SmallSat` population families with unquoted `CubeSat*`, `nanosat*`, and `SmallSat*`. Literal and wildcard source ID sets and order were equal in every partition. Keep every other punctuation, spacing, phrase, and spelling form literal.

## Execution

Use one direct query for every partition except A2. Implement A2 as the union of `P AND E_F AND M_H` and `P AND E_F AND M_B`. Keep each accepted source cell at or below 2,700 characters.

Each event starts from a fresh Advanced Search page and performs two complete matching DOI passes. Reconcile page scoped native RIS downloads to the exact target query, source total, and DOI ledger. Do not reuse a prior page, pass, ledger, download, screenshot, or staging state. Retain unresolved exact days and exclude only proved out of window dates. Retry only isolated source total or ordered ID snapshot changes. See [the readiness audit](../readiness-audit.md) for the result bound.
