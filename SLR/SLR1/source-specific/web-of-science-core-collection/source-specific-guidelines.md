# Web of Science Core Collection

PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py`

Save direct and citation searches in `final-searches/`. Save prior review searches in `psr-searches/`. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Web of Science Core Collection, all current editions
- URL: https://www.webofscience.com/wos/woscc/advanced-search
- Field: Query Builder `TS` Topic
- Main evidence window: Append `PY=(2011-<cutoff-year>)`. Screen cutoff year records against the exact common cutoff.
- Main language: Append `LA=(English)` and confirm report language during screening.
- Prior review searches: Apply the common upper cutoff with no lower date, language, type, subject, access, or peer review filter.
- Publication type: Apply no type or full text filter. Complete eligible type assignment is not proved.

## Source translation

Use the concepts and compounds in [the discovery protocol](../../protocol-discovery-and-screening.md#search-streams-and-set-construction). Use one fully parenthesized `TS=(L(s))` atom per straight double quoted token or phrase. Use uppercase Boolean operators. Use no proximity, pair expansion, or local pair filter.

- Controlled vocabulary decision: Add no supplement. Searchable classification fields exist, but no descriptor mapping, assignment coverage, and marginal recall gain have been validated for these review blocks.
- Wildcard decision: Use the ten population suffix patterns `CubeSat*`, `cube sat*`, `cube-sat*`, `cube satellite*`, `nanosat*`, `nano-sat*`, `nano sat*`, `nano-satellite*`, `nano satellite*`, and `SmallSat*` as quoted `TS` atoms. Keep the four `small satellite`, `small satellites`, `small sat`, and `small sats` atoms literal. Complete literal and wildcard WOS ID sets were equal in all main and prior review partitions. A broader 128 family map did not complete reliably, so no other wildcard is accepted.

## Execution

Run the nine [direct partitions](../../protocol-discovery-and-screening.md#direct-query-schedule) and four [prior review partitions](../../protocol-prior-secondary-reviews.md#additional-concept-blocks) as complete raw expressions. In `X`, apply the ten substitutions only to its population members. Require two complete passes, native RIS reconciliation, and exact query and control readback. Treat `PY` as year precision and screen cutoff year records against the exact date. A screenshot or source failure keeps `total: null`. See [the readiness audit](../readiness-audit.md) for main and prior review result bounds.
