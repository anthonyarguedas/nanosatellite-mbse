# ProQuest Dissertations & Theses Global

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`

Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Record capture

Each retained row must save the complete rendered Abstract/Details text in `abstract`, with `abstract_source`, `abstract_detail_verified`, `abstract_is_truncated`, and `abstract_not_available` states. A source that renders no abstract must remain explicit. Each row must also save the visible source-native type in `sourcePublicationType` and `documentType`, with source and availability fields. These are source metadata. Do not infer the reviewer `publication_type` screening code.

## Fixed source configuration

- Source or collection: ProQuest Dissertations & Theses Global
- URL: https://www.proquest.com/pqdtglobal/commandline
- Field: Command Line Search `NOFT`
- Evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen cutoff year records against the exact common cutoff.
- Language: Apply exact `LA(English)` and confirm report language during screening.
- Publication type: Apply no degree, completion, peer review, access, or full text filter.
- Collection: Select exactly one PQDT Global database label. Do not select ATAI.
- Results: Use `DateAsc`, 20 records per page, and turn duplicate exclusion, spelling variants, form variants, Show variants, and Full text off.

## Source translation

Use the concepts, compounds, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Use uppercase Boolean operators and full parentheses. Use no proximity or pair expansion.

- Literal atom `A(s)`: `NOFT(L(s))`, where `L(s)` is one straight double quoted token or phrase.
- Family atom: `NOFT(stem[*n])`, using the shortest safe common stem and smallest bound that covers the declared suffixes. Quote a multiword pattern.
- Controlled vocabulary decision: Add no `PSUB.EXACT` or `IF.EXACT` supplement. Validated assigned labels added no document ID to any complete free text partition. Free text remains mandatory.
- Wildcard decision: Use the accepted 128 bounded families. Complete literal and wildcard document ID sets and source order were equal in every partition. Keep singleton terms, punctuation forms, spacing forms, and unsafe stems literal.

## Execution

Run one full expression per partition. Keep every query below the adapter's 50,000 character limit. Require two complete ordered passes and a marker bound JSON. Recheck cutoff year records against the exact date during screening. See [the readiness audit](../readiness-audit.md) for the exact family evidence and result bound.
