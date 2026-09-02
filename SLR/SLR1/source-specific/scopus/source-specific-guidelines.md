# Scopus

Last pilot saved in commit: 29738a1a064b033eca37d8728116a6fc7d087638
PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_scopus.py`

Save primary final searches and forward citation searches in `final-searches/`. Save PSR final searches in `psr-searches/`. Name artifacts with the query ID (`A1.json`, `PSR1.json`) or citation seed report ID (`<paperID>.json`).

For every CLI JSON, the adapter automatically saves `<name>.search-page.png` and `<name>.results-page.png` in the same directory. The first image shows the configured Advanced Search page before Search. The second shows the first reconciled result page after requested controls. There is no screenshot opt-out. A successful source event requires both PNGs and retains their filenames, hashes, dimensions, and privacy flags in the JSON.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, screenshots, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Scopus
- Interface: Web
- Platform: Elsevier Scopus
- URL: https://www.scopus.com/pages/search/publications?type=advanced
- Search field or local route: Advanced Search `TITLE-ABS-KEY` topic field.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen records in the cutoff year against the exact common cutoff.
- Language: Main-review direct searches use the exact visible `Language` facet label `English`. Confirm full-report English during screening. PSR searches remain all-language.
- Publication type: Apply no type control. Pilot 002's source query accepted `DOCTYPE(ar OR cp OR ch OR rp)`, but retained record projections did not establish complete type assignment. Never apply peer-review, access, or full-text availability filters.
- Database or collection selection: Documents result scope and the full Scopus database. Apply no subject area.
- Other shared limits: None.
- Query entry: The adapter uses one target-scoped browser text-entry event for every nonempty expression. It requires exact Monaco `EditContext` readback before the single Search click. This covers long schedule expressions and short EID queries without using a source API or DOM mutation.

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction), as revised by commit `3194156e90497186664260a8e86435e78d2e2aa1`. Every listed term is an ordinary token or ordered phrase. Use no proximity operator, token-distance rule, same-field pair, pair expansion, or local pair filter.

- Literal `L(s)`: Use one straight double-quoted loose token or ordered phrase.
- Literal atom `A(s)`: `TITLE-ABS-KEY(L(s))`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join `A(s)` for every ordinary member of `S` with source `OR`. Fully parenthesize the result.
- Compound `G_model^S`: `(F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B)))`.
- Compound `G_structure^S`: `(F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B)))`.
- Compound `C1^S`: `(F(C1_fixed) OR F(G_DSL))`.
- `T_precise`: Use the ordinary block `F(T_precise)`.
- Controlled vocabulary: Add no supplement. Scopus exposes no searchable thesaurus or validated expansion switch. Free text remains mandatory.

### Accepted main-review population wildcard block

Use `F*(P)` in every main partition. It contains these ten loose trailing-wildcard atoms:

- `TITLE-ABS-KEY("CubeSat*")`
- `TITLE-ABS-KEY("cube sat*")`
- `TITLE-ABS-KEY("cube-sat*")`
- `TITLE-ABS-KEY("cube satellite*")`
- `TITLE-ABS-KEY("nanosat*")`
- `TITLE-ABS-KEY("nano-sat*")`
- `TITLE-ABS-KEY("nano sat*")`
- `TITLE-ABS-KEY("nano-satellite*")`
- `TITLE-ABS-KEY("nano satellite*")`
- `TITLE-ABS-KEY("SmallSat*")`

Join those atoms with source `OR`, then add the four unchanged literal atoms for `small satellite`, `small satellites`, `small sat`, and `small sats`. Fully parenthesize the 14-atom result.

The ten wildcards replace 22 declared P literals and reduce every main query by 375 characters. Pilots 006, 008, and 009 found exact literal-wildcard stable-ID set equality in all nine main partitions. No literal ID was missing and no wildcard-only ID was present. Wildcard use is therefore preferred for the tested main route.

This adoption is bounded to the main 2011-2026 English-controlled partitions. Keep `F(P)` and `F(X)` literal in PSR queries. Repilot before applying these wildcards to PSR, another field, another result scope, or a changed concept schedule.

## Query schedule

Render every row as one fully parenthesized source query. The four expansion rows preserve the shared compound Boolean definitions introduced in commit `3194156e90497186664260a8e86435e78d2e2aa1`.

| ID | Source construction |
|---|---|
| `A1` | `F*(P) AND F(E_H) AND F(M_H)` |
| `A2` | `F*(P) AND F(E_F) AND (F(M_H) OR F(M_B))` |
| `A3` | `F*(P) AND F(E_H) AND F(M_B)` |
| `B1` | `F*(P) AND F(M_H)` |
| `B2` | `F*(P) AND F(M_B) AND F(R)` |
| `BG1` | `F*(P) AND G_model^S` |
| `BG2` | `F*(P) AND G_structure^S` |
| `BC1` | `F*(P) AND C1^S` |
| `BT2` | `F*(P) AND F(M_B) AND F(T_precise)` |

### PSR query schedule

Use literal `F` blocks for `X`, `P`, and `Q` from [the supporting protocol](../../protocol-prior-secondary-reviews.md#additional-concept-blocks). Use the same current compound definitions as the main schedule.

| ID | Source construction |
|---|---|
| `PSR1` | `F(X) AND F(M_H) AND F(Q)` |
| `PSR2` | `F(X) AND F(M_B) AND F(R) AND F(Q)` |
| `PSR3` | `F(P) AND (F(E_H) OR F(E_F)) AND (F(M_H) OR F(M_B)) AND F(Q)` |
| `PSR4` | `F(X) AND (G_model^S OR G_structure^S OR C1^S) AND F(Q)` |

PSR searches have no lower date limit and no language, document type, subject, access, or peer review filter. Apply the common upper cutoff without narrowing the source-native topic fields.

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): historical A1, BG1, and PSR1 count diagnostics completed under the superseded pair schedule.
- [x] [Pilot 002](pilots/002/pilot.md): the exact `English` facet was read back. No type union was accepted. Its deferred ten-wildcard A1 comparison did not run.
- [Pilot 003](pilots/003/pilot.md): historical literal schedule diagnostics produced the main and partial PSR ledgers. PSR2 and PSR4 remained incomplete. Commit `3194156e90497186664260a8e86435e78d2e2aa1` later superseded its BG1, BG2, BC1, BT2, and PSR4 translations.
- [Pilot 004](pilots/004/pilot.md): the first current literal A1 event stopped before Search because long individual key entry lacked exact readback. No wildcard ran.
- [Pilot 005](pilots/005/pilot.md): literal A1 completed with both screenshots. A local compact-receipt validation error stopped the runner. The event is excluded from the final combined comparison.
- [Pilot 006](pilots/006/pilot.md): strict literal and wildcard A1, A2, and A3 events completed with equal sets. Strict literal B1 failed at candidate total 165.
- [Pilot 007](pilots/007/pilot.md): strict literal B1 failed again with native page size 50. It contributes no accepted wildcard set.
- [Pilot 008](pilots/008/pilot.md): all 24 separate one-owner events completed for B1, B2, BG1, BG2, BC1, and BT2, with 48 required screenshots. All literal-wildcard sets were equal. Literal B1 violated the pilot's stricter ordered-repeat rule because same-year records changed order under Date (oldest).
- [x] [Pilot 009](pilots/009/pilot.md): four fresh complete B1 events had stable repeated sets and exact literal-wildcard equality. The combined assessment covers all nine main partitions, 30 accepted source events, and 60 verified screenshots. It adopts the ten population wildcards for the main schedule.
- [x] [Pilot 010](pilots/010/pilot.md): six exact four-EID events returned the same set in two source orders. The 2022 pair reversed once. No stable secondary Date (oldest) tie-break pattern was observed.
- [Pilot 011](pilots/011/pilot.md): the first v2 strict EID event stopped before Search when short individual key events lacked exact Monaco readback. No result was inferred.
- [x] [Pilot 012](pilots/012/pilot.md): the repaired adapter completed strict v2 captures for the four swapping papers and the accepted wildcard B1 query. Totals were 4 and 165. Both complete stable-ID sets reconciled and both events saved their required screenshots.
- [x] [Pilot 013](pilots/013/pilot.md): the requested fresh wildcard B1 strict retry completed two exhaustive passes with the same 165 IDs, matching order, and both mandatory screenshots.
- [Pilot 014](pilots/014/pilot.md): the first four-part current literal PSR attempt completed PSR1 and PSR4. PSR2 and PSR3 failed closed.
- [Pilot 015](pilots/015/pilot.md): the isolated 200-row retry completed PSR3. The larger partitions failed closed, so the 200-row route was not accepted.
- [Pilots 016](pilots/016/pilot.md), [017](pilots/017/pilot.md), [018](pilots/018/pilot.md), [019](pilots/019/pilot.md), and [020](pilots/020/pilot.md): bounded ID-free diagnostics isolated a false final-page Next state. A result title containing “Next” was being treated as a paginator candidate.
- [x] [Pilot 021](pilots/021/pilot.md): all four current literal PSR partitions completed on their first attempt with strict v2 receipts and eight verified screenshots. Totals were 53, 237, 1, and 68. Their union has 326 IDs, and Buruso et al. remains in PSR1 and PSR2.

## Current strict completion contract

Final Scopus events require two exhaustive fresh-page passes with equal exact totals, page accounting, scope, page size, Date (oldest) control, and complete unique stable-ID sets. Each pass independently retains contiguous ranges, source order, and no duplicate ID. Current compact receipts use `academic-search-scopus-strict-two-pass/v2`.

Order equality is audit evidence rather than a membership gate. The v2 receipt retains both pass-order hashes, a canonical set hash, whether order matched, and the number of changed positions. A changed complete ID set still fails closed. Historical closed v1 ordered receipts remain verifiable.

Pilots 012 and 013 establish repeated current strict readiness for the accepted wildcard B1 query. Never promote the Pilot 008 or Pilot 009 one-owner artifacts into final-search results.

Pilot 021 establishes current strict readiness for all four literal PSR queries. PSR searches retain no lower year, language, document type, subject, access, peer-review, or Search within restriction. The PSR1, PSR2, PSR3, and PSR4 totals were 53, 237, 1, and 68. Buruso et al. was retrieved in PSR1 and PSR2 as `SCOPUS-PUBLICATION:105032155734`. These remain pilot records and must not be promoted into final-search results.

Final-page Next detection uses exact control semantics. It accepts the disabled paginator's screen-reader suffix and excludes arbitrary result links whose titles contain “Next”. Pilot 020 diagnosed this distinction, and PSR2 then completed both five-page passes in Pilot 021.

Pilot 003 recovery keeps explicit native zero pages separate from failures. A native zero has no sort, page-size, or abstract control. It records those controls as `not_applicable`. Positive pages still require native range, row, ID, sort, and page-size reconciliation.

Abstract recovery uses a canonical EID-only query, Documents scope, native page size, and an explicit authorized browser target. It does not carry discovery date, language, title, or facet clauses into the identity query. Recovery accepts only marker-bound compact strict leaves with exact requested, source, and export totals, matching ID hashes, canonical query binding, and unique returned IDs. A singleton failure remains unresolved and is never treated as no native abstract. The Pilot 003 recovery itself does not complete PSR2 or PSR4. Pilot 021 supplies the later clean strict pilot evidence for those partitions.
