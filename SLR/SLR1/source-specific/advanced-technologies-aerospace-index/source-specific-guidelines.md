# Advanced Technologies & Aerospace Index

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Advanced Technologies & Aerospace Index
- Interface and platform: ProQuest Command Line Search
- URL: https://www.proquest.com/ataindex/commandline
- Fields: `NOFT` plus exact `IF`
- Evidence window: Use exact `--date-start 2011-01-01 --date-end <cutoff>` bounds.
- Language: Apply exact `LA(English)`. Confirm report language during screening.
- Publication type: Apply no type, peer review, access, or full text filter. The source does not prove complete assignment to a lossless eligible type union.
- Collection: Select only Advanced Technologies & Aerospace Index.
- Ordering and page controls: Use the adapter defaults and require two complete matching passes.

## Source translation

Use the concepts, compound definitions, and nine partitions in [the discovery protocol](../../protocol-discovery-and-screening.md#direct-query-schedule). Use uppercase Boolean operators and full parentheses. Use no proximity or pair expansion.

- Literal `L(s)`: One straight double quoted token or ordered phrase.
- Literal atom `A(s)`: `(NOFT(L(s)) OR IF.EXACT(L(s)))`. The `IF` branch is required because `NOFT` can omit an assigned indexed keyword.
- Bounded family atom `W(V)`: Use the shortest safe common stem with the smallest ProQuest `[*n]` suffix bound that covers every declared variant. Quote a multiword pattern. Keep every replaced `IF.EXACT` literal explicit.
- Ordinary block `F(S)`: Join each accepted family atom and remaining literal atom with `OR` in source term order.
- Controlled vocabulary decision: Add no Technology Thesaurus supplement. Mapped descriptors added no record to the tested free text result and did not cover every selected record. Free text plus exact indexed terms remains mandatory.
- Wildcard decision: Use the accepted 128 bounded families in `NOFT` only. Complete literal and bounded wildcard sets were equal in every partition. Keep unsafe stems, punctuation variants, and all `IF.EXACT` terms literal.

## Execution

Run each direct partition as one complete expression. Record the exact accepted family map in the event plan. Reject spelling variants, form variants, hierarchy expansion, focus, and major topic controls. Keep this event separate from PQDT Global. See [the readiness audit](../readiness-audit.md) for the accepted map evidence and result bound.
