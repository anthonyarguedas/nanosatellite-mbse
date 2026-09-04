# Compendex

Final searches saved in commit: cbc2550116e3c9c530729361bd4b153506f74fbc
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

Run Compendex and Inspec in one paired Engineering Village event. Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Compendex
- Platform: Engineering Village Expert Search
- URL: https://www.engineeringvillage.com/search/expert.url?database=1
- Field: `ALL`
- Evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen cutoff year records against the exact common cutoff.
- Language: Append `(English WN LA)` to every expression. Confirm report language during screening.
- Publication type: Apply no `DT`, peer review, access, or full text filter. Assignment can be absent and no complete eligible type union is proved.
- Collection: Select Compendex and Inspec together. Keep each database count and record set separate.

## Source translation

Use the concepts, compound definitions, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Use uppercase Boolean operators and full parentheses. Use no proximity, token distance, pair expansion, or implicit variant.

- Literal atom `A(s)`: `(L(s) WN ALL)`, where `L(s)` is one straight double quoted token or phrase.
- Population wildcards: Replace the declared `CubeSat` family with `(CubeSat* WN ALL)`, the `nanosat` family with `(nanosat* WN ALL)`, and the `SmallSat` family with `(SmallSat* WN ALL)`. Keep the wildcard tokens unquoted.
- Controlled vocabulary decision: Add no Ei Thesaurus term. Exact mapped candidate descriptors produced no candidate only B1 accession. Free text remains mandatory. Use no hierarchy expansion, main heading, or major term restriction.
- Wildcard decision: Use the three population wildcards in every partition. Complete literal and wildcard A1 accession sets were equal, and the same bounded population translation was accepted for the full schedule. Use no other `*`, `?`, or `$` form.

## Execution

Run each partition as one paired expression. Require two complete passes and reconcile source rows, native exports, and accessions. Save every Compendex record's full native RIS abstract in `abstract` and source type in `documentType`. Reject an event when either field is missing. Publish only the Compendex projection here. Never combine its total with Inspec. See [the readiness audit](../readiness-audit.md) for current result bounds.
