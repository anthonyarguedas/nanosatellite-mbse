# Advanced Technologies & Aerospace Index

Last pilot saved in commit: 9ad78b53e5c95ddac07196d58485e68f059bbd58
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`. The adapter always saves `A1.search-page.png` and `A1.results-page.png` beside the JSON.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Advanced Technologies & Aerospace Index
- Interface: Web
- Platform: ProQuest
- URL: https://www.proquest.com/ataindex/commandline
- Search field or local route: Command Line Search `NOFT` and exact `IF` fields.
- Main evidence window: Use exact `--date-start 2011-01-01 --date-end <cutoff>` publication-date bounds.
- Language: Apply exact `LA(English)`. Pilot 006 compared the final indexed-term translation with and without this restriction twice. Only `B2` changed, from `36` to `34`. Both excluded records were source-labelled `Language of publication: Chinese`. This metadata restriction does not prove report language. Full-text screening remains authoritative for retrieved candidates.
- Publication type: Apply no type, peer-review, access, or full-text-availability filter. `DTYPE` and Document type vocabulary, including missing-type behavior, are tenant/corpus controlled. No lossless union for all shared eligible report types is proved.
- Database or collection selection: Select only Advanced Technologies & Aerospace Index. Deselect every parent and other ProQuest database.
- Other shared limits: None.

## Source translation

Use the exact concept membership and Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Use no proximity operator or pair expansion. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal.
- Singleton atom `A(s)`: `(NOFT(L(s)) OR IF.EXACT(L(s)))`. Pilot 006 proved that `NOFT` can omit an exact `IF` indexed keyword assignment. The supplement added nine stable IDs across `B1`, `B2`, `BC1`, and `BT2`, including six plausible review candidates.
- Bounded wildcard family `W(V)`: For an accepted family of explicit variants `V`, use the smallest ProQuest `[*n]` suffix bound that covers every member in `NOFT`. Keep every replaced `IF.EXACT(L(s))` alternative explicit. For example, render `CubeSat` and `CubeSats` as `(NOFT(CubeSat[*1]) OR IF.EXACT("CubeSat") OR IF.EXACT("CubeSats"))`.
- Ordered phrases: Keep a multiword wildcard pattern inside straight double quotes. Examples include `"power system[*1]"` and `"state[*1] of charge"`.
- Accepted family map: Use the 128 families in the [Pilot 008 query module](../../scripts/atai_pilot008/queries.py), reproduced with exact queries and hashes in its [event plan](pilots/008/searches/event-plan.json). The map compresses 292 explicit term occurrences across the ordinary blocks. It includes regular number variants and bounded inflection families such as `nanosat[*7]`, `tailor[*3]`, and `instantiat[*3]`. Terms without one safe common source stem stay as singleton atoms.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join each accepted `W(V)` and remaining `A(s)` in source term order with source OR. Fully parenthesize the result.
- Compound `G_model`: `(F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B)))`.
- Compound `G_structure`: `(F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B)))`.
- Compound `C1`: `(F(C1_fixed) OR F(G_DSL))`.
- Controlled vocabulary: Add no Technology Thesaurus supplement. Free text remains mandatory. Pilot 004 verified six assigned `SUBJECT` labels as exact descriptors, then found the same ordered 19 IDs for fresh literal and descriptor augmented `B1` runs, with no candidate only ID. The candidate controlled MBSE construction matched only five of seven selected records, so controlled terms cannot replace free text and showed no marginal recall value.
- Source limitation: Keep this source in an event separate from PQDT Global. Pilot 006 known item contrasts retained the same IDs through explicit `TI`, `AB`, and `MAINSUBJECT` fields and through `NOFT`. A separate `IF.EXACT` known item was absent from `NOFT`, so every ordinary construction includes both fields. Pilot 007 accepted each complete schedule expression as one direct query. Pilot 008 found exact ordered stable ID equality between every fresh literal partition and its bounded wildcard counterpart. Wildcard use is accepted only in `NOFT`. Keep all exact `IF` alternatives literal.

## Query schedule

Render every row as one fully parenthesized source query. The four expansion rows preserve the shared compound Boolean definitions.

| ID | Source construction |
|---|---|
| `A1` | `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F(P) AND F(M_H)` |
| `B2` | `F(P) AND F(M_B) AND F(R)` |
| `BG1` | `F(P) AND (F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B)))` |
| `BG2` | `F(P) AND (F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B)))` |
| `BC1` | `F(P) AND (F(C1_fixed) OR F(G_DSL))` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` count-only diagnostics succeeded with totals `0` and `2`. These are not final searches.
- [x] [Pilot 002](pilots/002/pilot.md): English literal/candidate `A1` count-only checks totaled `0`/`0`. Language read back, no type restriction was accepted, and the wildcard candidate was not adopted.
- [Pilot 003 record](pilots/003/pilot.md): all nine exact literal partitions have pilot-only stable-ID reconciliations. `A3` and `B1` retain their historical null-total adapter v3 strict failures. Their same-query stable-ID repairs did not establish full-record stability at that time. Pilot 005 records the repaired adapter v4 strict reruns. No deduplicated pilot union exceeded 100, and no noise refinement was applied.
- [x] [Pilot 004](pilots/004/pilot.md): seven selected records supplied 58 assigned `SUBJECT` terms. Six candidates were exact Technology Thesaurus descriptors. A context-qualified `B1` supplement added no stable ID, so no descriptor was accepted.
- [x] [Pilot 005](pilots/005/pilot.md): adapter v4 removed the transient terminal abstract `More` token, integrated exact restore-session dismissal and inventory-proven cleanup, and passed fresh strict two-full-record checks for A3 and B1. Historical and fresh abstract comparisons found no truncation.
- [x] [Pilot 006](pilots/006/pilot.md): bounded known-item checks validated `NOFT` coverage of title, abstract, and controlled subjects. `NOFT` omitted an exact `IF` assignment, so ordinary atoms now add `IF.EXACT` with `OR`. The supplement added nine stable IDs, including six plausible candidates. Repeated final language comparisons excluded only two source-labelled Chinese publications, so `LA(English)` remains accepted.
- [x] [Pilot 007](pilots/007/pilot.md): all nine complete schedule expressions ran directly without proximity operators, pair expansions, wildcards, or query splits. Two count passes agreed at `0`, `5`, `1`, `25`, `34`, `2`, `7`, `2`, and `2`. Strict complete captures passed for all four changed partitions. Every successful event retains both required full-page screenshots, so the direct Boolean translation is accepted.
- [x] [Pilot 008](pilots/008/pilot.md): strict literal and bounded wildcard captures returned the same ordered stable ID set for every schedule partition. The accepted 128-family map uses 34 to 48 bounded operators per complete query, shortens each query by 636 to 1,603 characters, and retains every exact `IF` term. All 18 successful events have both mandatory screenshots.
