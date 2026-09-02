# ProQuest Dissertations & Theses Global

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`

Save primary final searches in `final-searches/` and name each JSON artifact with its query ID, such as `A1.json`. Adapter version 5 always saves `A1.search-page.png` and `A1.results-page.png` beside that JSON. The adapter has no screenshot opt-out. A successful CLI event requires both PNGs and their hashes, dimensions, and privacy receipt in the JSON.

The JSON and its sibling screenshots are authoritative for each event's query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, capture, completeness, and failures. This file records fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: ProQuest Dissertations & Theses Global (PQDT Global)
- Interface: Web
- Platform: ProQuest
- URL: https://www.proquest.com/pqdtglobal/commandline
- Search field or local route: Command Line Search `NOFT` field.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen records in the cutoff year against the exact common cutoff.
- Language: Apply exact `LA(English)` and record the source query readback. Full-text screening confirms report language.
- Publication type: PQDT is thesis and dissertation scoped. Apply no degree, completion, peer-review, access, or full-text-availability filter. Metadata can include incomplete, undergraduate, or abstract-only work. Resolve those statuses during screening.
- Database or collection selection: Select exactly one allowed PQDT Global database label. Do not select ATAI or another ProQuest database.
- Result controls: Use `DateAsc` (Oldest first), 20 records per page, and freeze duplicate exclusion, spelling variants, form variants, Show variants, and Full text off.
- Other shared limits: None.

## Source translation

Use the exact concept membership and Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Every current term is an ordinary token or ordered phrase. The current schedule uses no proximity operator, pair expansion, or local pair test.

- Literal `L(s)`: Use one straight double-quoted literal.
- Literal atom `A(s)`: `NOFT(L(s))`.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join every atom in `S` with source `OR` and fully parenthesize the result.
- Compound blocks: Render the protocol definitions directly. Use `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))` for `G_model`. Use `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))` for `G_structure`. Use `F(C1_fixed) OR F(G_DSL)` for `C1`.
- Accepted wildcard family atom: Use `NOFT(stem[*n])`. Quote the whole pattern when it is an ordered phrase. Use the smallest bound that covers the declared suffixes.
- Accepted wildcard scope: Replace every variant family with one safe common source stem. Keep singleton terms, punctuation alternatives, spacing alternatives, and unsafe stems literal. Pilot 004 accepted 128 bounded wildcard families covering 292 explicit term occurrences across the ordinary blocks. Prefer this shorter bounded wildcard rendering in every partition.
- Controlled vocabulary and indexed terms: Add no `PSUB.EXACT` or `IF.EXACT` supplement. Free text remains mandatory. Pilot 005 mapped and validated assigned candidates for `P`, `M_H`, `M_B`, and `R`, then found no added document ID in any complete schedule partition. A new label requires another assigned-record mapping and complete no-loss value comparison.
- Cell plan: Use one full expression per partition. Every accepted wildcard query is below the adapter's 50,000-character limit. The longest is A2 at 2,939 characters.
- Source limitation: `NOFT` searches anywhere except full text. This reduces bias toward searchable full text while remaining sensitive to uneven metadata. Resolve degree subtype, availability, completion status, and report language during screening.

Pilot 004 tested each wildcard query next to its complete literal equivalent. Every pair returned the same ordered numeric PQDT document IDs. There were no wildcard-only records. Keep the exact family declarations and bounds in the pilot plan. Any new wildcard family requires another complete literal-superset comparison.

Pilot 005 inspected two-pass field assignments on 14 selected known records. It found nine distinct PQ Subject labels and 42 distinct Index term labels. Two-pass browse validation verified 27 exact candidates and mapped them to `P`, `M_H`, `M_B`, and `R`. All nine fresh free-text and augmented partition pairs returned the same complete IDs in the same order. Both schedule unions contained 29 IDs, so the descriptor-only review frame was empty. Retain no controlled-term supplement.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators and compound definitions above.

| ID | Source construction |
|---|---|
| `A1` | `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F(P) AND F(M_H)` |
| `B2` | `F(P) AND F(M_B) AND F(R)` |
| `BG1` | `F(P) AND F(G_model)` |
| `BG2` | `F(P) AND F(G_structure)` |
| `BC1` | `F(P) AND F(C1)` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): complete A1 and historical BG1 count-only diagnostics succeeded with totals 1 and 1. These were not final searches.
- [x] [Pilot 002](pilots/002/pilot.md): English literal and population-wildcard A1 count-only checks each totaled 1. It applied no type restriction. Stable-ID evidence was unavailable, so the pilot did not adopt that candidate.
- [Pilot 003](pilots/003/pilot.md): the superseded pair-based nine-partition schedule completed as a pilot-only literal diagnostic. It returned 29 distinct document IDs and made no final-search decision.
- [x] [Pilot 004](pilots/004/pilot.md): all 18 current-schedule literal and maximally bounded-wildcard events completed under the adapter's strict two-pass contract. Literal and wildcard IDs and source order were equal in every partition. Totals were A1 1, A2 3, A3 1, B1 21, B2 13, BG1 1, BG2 3, BC1 3, and BT2 1. The all-schedule union contained 29 IDs. The pilot accepts and prefers all 128 declared bounded wildcard families. It validates 36 mandatory event PNGs plus two adapter-smoke PNGs.
- [x] [Pilot 005](pilots/005/pilot.md): assigned-term harvests found nine PQ Subject and 42 Index term labels on 14 selected known records. Exact two-pass browse validation verified 27 candidates mapped to `P`, `M_H`, `M_B`, and `R`. Every fresh free-text and augmented schedule pair had equal complete ordered IDs. Both unions contained 29 IDs and no descriptor-only record. Retain no `PSUB.EXACT` or `IF.EXACT` supplement.

## Final-search boundary

Pilots 004 and 005 are diagnostic evidence. They create no final-search union. A final run starts from fresh source state and uses the accepted wildcard schedule without a controlled-term supplement, the exact fixed controls, two complete ordered passes, a marker-bound JSON, and both mandatory screenshots. It rechecks every 2026 record against the final exact cutoff during screening.
