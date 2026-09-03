# Scopus

PSR final searches saved in commit: 8803bd5061a49a3c8c6a26bb10aaeb8ee1b43372
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_scopus.py`

Save direct and citation searches in `final-searches/`. Save prior review searches in `psr-searches/`. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full Scopus Documents scope
- URL: https://www.scopus.com/pages/search/publications?type=advanced
- Field: `TITLE-ABS-KEY`
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen cutoff year records against the exact common cutoff.
- Main language: Apply the exact English facet and confirm report language during screening.
- Prior review searches: Apply the common upper cutoff with no lower date, language, type, subject, access, or peer review filter.
- Publication type: Apply no type or full text filter. Complete eligible type assignment is not proved.
- Ordering: Date, oldest first.

## Source translation

Use the concepts and compounds in [the discovery protocol](../../protocol-discovery-and-screening.md#search-streams-and-set-construction). Use one fully parenthesized `TITLE-ABS-KEY(L(s))` atom per straight double quoted token or phrase. Use no proximity, pair expansion, or local pair filter.

- Controlled vocabulary decision: Add no supplement. Scopus exposes no searchable thesaurus or validated expansion switch for this route.
- Wildcard decision: Use the ten population suffix patterns `CubeSat*`, `cube sat*`, `cube-sat*`, `cube satellite*`, `nanosat*`, `nano-sat*`, `nano sat*`, `nano-satellite*`, `nano satellite*`, and `SmallSat*` in main `TITLE-ABS-KEY` searches. Keep the four `small satellite`, `small satellites`, `small sat`, and `small sats` atoms literal. Complete literal and wildcard stable ID sets were equal in all nine main partitions. Keep `P` and `X` literal in prior review searches because the broader all-language, source inception route lacks a no loss comparison.

## Execution

Run the nine [direct partitions](../../protocol-discovery-and-screening.md#direct-query-schedule) and four [prior review partitions](../../protocol-prior-secondary-reviews.md#additional-concept-blocks) as complete expressions. Final events require two exhaustive fresh page passes with equal totals, page accounting, controls, and stable ID sets. Preserve both source order hashes. A changed order is audit evidence. A changed set fails.

Recover abstracts only through canonical EID queries bound to accepted strict leaves. Do not carry discovery date, language, title, or facet clauses into identity recovery. An unresolved singleton remains unresolved. See the [final PSR assessment](psr-searches/assessment.json) for final PSR result bounds.
