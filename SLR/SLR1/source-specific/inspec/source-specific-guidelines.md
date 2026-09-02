# Inspec

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, screenshots, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Inspec
- Interface: Web
- Platform: Elsevier Engineering Village
- URL: https://www.engineeringvillage.com/search/expert.url?database=1
- Search field or local route: Expert Search `ALL` field in one paired Compendex and Inspec event.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen records in the cutoff year against the exact common cutoff.
- Language: Append `(English WN LA)` with `AND` to each raw Expert expression. This metadata limiter does not replace English full-text screening.
- Publication type: Apply no `DT`/facet limiter: conference article, journal article, preprint, conference proceeding, dissertation, and article in press can hold eligible reports, and assignment can be missing. Do not apply peer-review, access, or full-text-availability limits.
- Database or collection selection: Select Compendex and Inspec together. Retain the Inspec records and count separately.
- Other shared limits: None.
- Screenshots: Adapter v16 automatically saves `<query-id>.search-page.png` and `<query-id>.results-page.png` beside each JSON artifact. The first image shows the configured Expert form. The second shows the verified first results page. This behavior has no opt-out. A missing or mismatched screenshot fails the event. The bounded single-pass and strict paired checks are recorded in the shared [adapter validation](../compendex/pilots/005/searches/adapter-v16-screenshot-validation.json).

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction), as revised by protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`. Every listed term is an ordinary token or ordered phrase. Use no proximity operator, token distance rule, same field pair, or pair expansion. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted token or ordered phrase.
- Atom `A(s)`: `(L(s) WN ALL)`.
- Wildcard usage: **Approved for every schedule entry.** In every `F(P)` block, replace the literal `CubeSat` and `CubeSats` atoms with `(CubeSat* WN ALL)`. Replace `nanosat`, `nanosats`, `nanosatellite`, and `nanosatellites` with `(nanosat* WN ALL)`. Replace `SmallSat` and `SmallSats` with `(SmallSat* WN ALL)`. Keep wildcard tokens unquoted. Preserve every other population term and every term in the other blocks. [Pilot 004](pilots/004/pilot.md) links the complete equal Inspec literal and wildcard A1 sets and all nine strict current-schedule executions. Use no other `*`, `?`, or manual `$` form.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join `A(s)` for every member of `S` with source `OR`. Fully parenthesize the result.
- `F(G_model)`: `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))`.
- `F(G_structure)`: `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))`.
- `F(C1)`: `F(C1_fixed) OR F(G_DSL)`.
- `F(T_precise)`: Use the ordinary union of every precise tailoring term.
- Controlled vocabulary: Add no Inspec Thesaurus supplement. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping, assignment, and marginal value.
- Source limitation: The paired artifact covers both databases. Preserve its source-specific Inspec projection and never combine the two source totals.
- Pilot 001 used the paired event recorded under [Compendex Pilot 001](../compendex/pilots/001/pilot.md). The source echo accepted the complete historical `A1` and `BG1` expressions and the 2011-2026 Published range. The paired event exposed `A1: 3` and `BG1: 2` Inspec rows. Its bounded one-record export is partial.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source rules and current compound definitions above. Use the approved wildcard-compressed `F(P)` block in every row.

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

- [x] [Pilot 001](pilots/001/pilot.md): the paired `A1` and `BG1` diagnostics succeeded. Inspec projections were `A1: 3` and `BG1: 2` rendered rows. The bounded one-record export is diagnostic only and is not a final search.
- [x] [Pilot 002](pilots/002/pilot.md): links the paired Compendex failure receipt. The shared event stopped before source submission when the start Published-year control was hidden. No Inspec count or wildcard comparison exists.
- [x] [Pilot 004](pilots/004/pilot.md): the source-specific assessment links the existing paired events without repeating them. Literal and three-wildcard A1 produced equal complete three-accession Inspec sets. All nine current wildcard partitions passed with 18 strict source passes and 18 mandatory screenshots. The Inspec union contains 162 unique accessions from 236 partition occurrences. The three population wildcards are approved for every schedule entry.

## Pilot 003 record (pilot only, completion state unchanged)

[Linked Pilot 003](pilots/003/pilot.md) preserves the Inspec projection of the same repaired paired Engineering Village events. It does not duplicate them. Eight strict two-pass captures succeeded and its B2 remains an explicit null failure. The historical pairs use marker v2. Pilot 004 links a fresh current-query B2 projection without changing the historical artifact. Keep Inspec totals and accessions separate in every paired reconciliation. Pilot 003 supports no current wildcard, controlled-term supplement, or final-search claim.
