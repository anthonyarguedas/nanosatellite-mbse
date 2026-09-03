# IAF Digital Library

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`

Save final JSON files in `final-searches/` by query ID and cell. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: Full IAF Digital Library
- URL: https://dl.iafastro.directory/search/
- Field: Unqualified Any keyword in the rendered search wizard
- Evidence window: Traverse the unbounded source query. Apply the 2011 lower bound and exact cutoff locally. The source provides year precision only.
- Language: Apply no source filter. The indexed language field has no complete public vocabulary or proved assignment coverage.
- Publication type: The source contains conference paper records. Apply no further type, peer review, access, event, or full text filter.
- Ordering: Retain native order. No sort control is available.

## Source translation

Use the concepts and compound definitions in [the discovery protocol](../../protocol-discovery-and-screening.md#search-streams-and-set-construction). Use no proximity or pair expansion.

- Literal `L(s)`: One straight double quoted token or ordered phrase.
- Population block `F_W(P)`: `(CubeSat* OR "cube sat*" OR cube-sat* OR nanosat* OR nano-sat* OR "nano sat*" OR SmallSat* OR "small sat*")`.
- Ordinary block `F(S)`: Join every literal with source `OR` and full parentheses.
- Conjunction: Use whitespace. Use uppercase `OR` for disjunction.
- Controlled vocabulary decision: Add no supplement. IAF exposes no public subject thesaurus or controlled indexed term field. Event, country, and language values are ordinary source fields without preferred term, hierarchy, scope, or version evidence.
- Wildcard decision: Use the eight population suffix wildcards only. Their complete raw and in-window stable ID unions matched the explicit 26-term population translation in every partition. The source documents suffix `*`. Leading and internal forms and `?` remain excluded.

## Execution

IAF accepts at most 500 query characters. Distribute each compound outer `OR` into named branches and pack each branch into deterministic cells below the cap. The accepted schedule has 158 cells: A1 37, A2 48, A3 21, B1 4, B2 20, BG1 6, BG2 6, BC1 3, and BT2 13.

Every cell must cover its declared Cartesian alternatives exactly once. Run two exhaustive passes and require equal totals, ordered paper IDs, and rendered capture hashes. Reconcile partition unions by stable paper ID. See [the readiness audit](../readiness-audit.md) for the result bound.
