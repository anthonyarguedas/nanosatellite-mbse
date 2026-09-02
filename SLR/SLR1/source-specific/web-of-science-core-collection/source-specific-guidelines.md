# Web of Science Core Collection

Last pilot saved in commit: NA
PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py`

Save primary final searches and forward citation searches in `final-searches/`. Save PSR final searches in `psr-searches/`. Name artifacts with the query ID (`A1.json`, `PSR1.json`) or citation seed report ID (`<paperID>.json`).

Adapter version 2 always saves `<name>.search-page.png` and `<name>.results-page.png` beside each CLI JSON. The first image shows the configured Query Builder before Search. The second shows the first reconciled results page. There is no screenshot opt-out. A successful event requires both PNGs and records their filenames, hashes, dimensions, and privacy flags in the JSON.

The JSON and its sibling screenshots are authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Web of Science Core Collection
- Interface: Web
- Platform: Clarivate Web of Science
- URL: https://www.webofscience.com/wos/woscc/advanced-search
- Search field or local route: Core Collection Query Builder `TS` Topic field across all current editions.
- Main evidence window: Add raw `PY=(2011-<cutoff-year>)`. Screen records in the cutoff year against the exact common cutoff.
- Language: Main-review raw queries include `LA=(English)`. Confirm full-report English during screening. PSR searches remain all-language.
- Publication type: Apply no type control. Pilot 002 proved the candidate DT OR syntax. Lossless assignment coverage remains unproved for the shared eligible report types. Never apply peer-review, access, or full-text availability filters.
- Database or collection selection: Web of Science Core Collection with all current editions selected.
- Other shared limits: None.

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction), as revised by commit `3194156e90497186664260a8e86435e78d2e2aa1`. Every listed term is an ordinary token or ordered phrase. Use no proximity operator, token-distance rule, same-field pair, pair expansion, or local pair filter.

- Literal `L(s)`: Use one straight double-quoted literal. Multiword literals remain ordered phrases.
- Atom `A(s)`: `TS=(L(s))`.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join `A(s)` for every ordinary member of `S` with source `OR`. Fully parenthesize the result.
- Compound `G_model^S`: `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))`.
- Compound `G_structure^S`: `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))`.
- Compound `C1^S`: `F(C1_fixed) OR F(G_DSL)`.
- `T_precise`: Use the ordinary block `F(T_precise)`.
- Controlled vocabulary: Add no supplement. The source exposes searchable classification fields, but no descriptor mapping has been accepted for this review.
- Raw controls: Append `PY=(2011-<cutoff-year>) AND LA=(English)` to each main expression. Raw mode requires date and language clauses inside the query.

### Accepted main-review population wildcard block

Use `F*(P)` in every main partition. It contains these ten quoted trailing-wildcard atoms:

- `TS=("CubeSat*")`
- `TS=("cube sat*")`
- `TS=("cube-sat*")`
- `TS=("cube satellite*")`
- `TS=("nanosat*")`
- `TS=("nano-sat*")`
- `TS=("nano sat*")`
- `TS=("nano-satellite*")`
- `TS=("nano satellite*")`
- `TS=("SmallSat*")`

Join those atoms with source `OR`, then add the four unchanged literal atoms for `small satellite`, `small satellites`, `small sat`, and `small sats`. Fully parenthesize the 14-atom result.

The ten wildcards replace 22 declared population literals and shorten every affected query by 255 characters. Pilot 004 found exact literal-wildcard ordered WOS-ID equality in all nine main partitions. Use this shorter rendering for the main schedule. This main-search decision is bounded to the 2011 through 2026 English-controlled route.

Pilot 006 found exact literal-wildcard ordered WOS-ID equality in all four PSR partitions. Use the same ten atoms for `P` and for the `P` members nested inside `X`. Keep every additional `X` term literal. This PSR decision is bounded to the source-inception through 2026 all-language route.

Pilot 005 tested a broader map of 128 `$` and `*` variant families. Broad `A1` matched its literal set. Broad `A2` timed out at submit in three direct attempts, and its split `M_B` branch timed out in three more attempts. Keep all additional wildcard patterns unaccepted. The ten-atom map is the widest wildcard translation supported by complete schedule evidence.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render ordinary and compound blocks with the source rules above.

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

Use the same `L`, `A`, `F`, and Boolean rules for `X` and `Q` from [the supporting protocol](../../protocol-prior-secondary-reviews.md#additional-concept-blocks).

| ID | Source construction |
|---|---|
| `PSR1` | `F*(X) AND F(M_H) AND F(Q)` |
| `PSR2` | `F*(X) AND F(M_B) AND F(R) AND F(Q)` |
| `PSR3` | `F*(P) AND (F(E_H) OR F(E_F)) AND (F(M_H) OR F(M_B)) AND F(Q)` |
| `PSR4` | `F*(X) AND (G_model^S OR G_structure^S OR C1^S) AND F(Q)` |

For PSR, `F*(X)` applies the accepted ten population substitutions only to the `P` members within `X`. Every additional `X` term stays literal.

PSR searches have no lower date limit and no language, document type, subject, access, or peer review filter. Apply the common upper cutoff without narrowing the source-native topic fields.

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): historical `A1`, pair-based `BG1`, and supporting `PSR1` count diagnostics completed. Raw `PY` date clauses were required.
- [x] [Pilot 002](pilots/002/pilot.md): raw `LA=(English)` was read back. No DT union was accepted. The ten-wildcard population candidate was accepted for historical `A1`.
- [Pilot 003](pilots/003/pilot.md): all nine historical pair-based main events and four PSR events completed. Commit `3194156e90497186664260a8e86435e78d2e2aa1` superseded its `BG1`, `BG2`, `BC1`, and `BT2` translations. Its cutoff and known-item evidence remains diagnostic history.
- [x] [Pilot 004](pilots/004/pilot.md): all 18 successful current-schedule literal and wildcard events completed strict two-pass capture with 36 mandatory screenshots. Every partition had exact ordered WOS-ID equality and no wildcard-only record. The ten-wildcard population block is accepted and preferred in all nine main partitions. One pre-query connection failure remains preserved with `total: null` and was recovered by an unchanged retry.
- [x] [Pilot 005](pilots/005/pilot.md): the broader 128-family wildcard candidate stopped at `A2`. Broad `A1` and the split `A2` `M_H` cell succeeded. Six unchanged `A2` direct or `M_B` attempts timed out at submit with `total: null`. The broader map is rejected for schedule use. Ten screenshots document the two successes and pre-submit failure states.
- [x] [Pilot 006](pilots/006/pilot.md): all eight PSR literal and population-wildcard events completed on their first attempt with 16 mandatory screenshots. Partition totals were 22, 60, 0, and 27. Every ordered WOS-ID set was equal, both unions contained 102 IDs, and Buruso et al. was retrieved by both versions of `PSR1` and `PSR2`. The ten population wildcard atoms are accepted and preferred across the PSR schedule.

## Current source limitations

`PY` is year-level. Screen cutoff-year records against the exact common cutoff. Clarivate does not universally document whether `DOP` follows Early Access or final publication.

Topic can match title, abstract, author keywords, Keywords Plus, or source-normalized variants. The normalized JSON retains complete records and a native RIS receipt. The adapter keeps its internal two-pass ledger private under the shared compact-output policy.

A screenshot failure makes the event fail. A source or adapter failure retains `total: null` and any screenshots captured before failure. Never treat a missing result state as zero.
