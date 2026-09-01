# IEEE Xplore

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: IEEE Xplore
- Interface: Web
- Platform: IEEE Xplore
- URL: https://ieeexplore.ieee.org/search/advanced
- Search field or local route: Normal search with individually fielded `All Metadata` atoms.
- Main evidence window: Use `--publication-date-start 2011-01-01 --publication-date-end <cutoff>` for final searches.
- Language: No proved Language field or facet is available. Apply no language control and determine English full text during screening.
- Publication type: Apply no type control. The current content taxonomy and assignment coverage do not prove a lossless eligible-report union. Never apply peer-review, access, or full-text availability filters.
- Database or collection selection: Documents scope with all access states and no content type facet.
- Other shared limits: None.

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed ordinary term. Use no proximity operator, pair expansion, or wildcard. Pilot 003's 10-wildcard A1 candidate remains unaccepted without a date-controlled stable-ID comparison.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `("All Metadata":L(s))`.
- Boolean: Use uppercase `AND` and `OR` with explicit parentheses.
- Ordinary block `F(S)`: Join `A(s)` for every member of `S` with source OR. Fully parenthesize the result.
- Compound `G_model`: `(F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B)))`.
- Compound `G_structure`: `(F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B)))`.
- Compound `C1`: `(F(C1_fixed) OR F(G_DSL))`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Do not use a grouped field wrapper around a Boolean block. Expand every atom before combining it.
- Pilots 001 and 002 accepted the complete `A1` All Metadata expression before submission. Pilot 001 records a requested-range mismatch after Apply and three contradictory polls. Pilot 002 repeats the same count-only diagnostic with the `2011` through `2026` year control. Its artifact records source-observed query and year-control readback, then ends with `status: error` and no source total. No reconciled date-controlled `A1` result exists. This leaves an unresolved source-control limitation. Do not replace it with an unbounded query or local date filtering. The exact publication-day window is unavailable in count-only mode because the adapter requires strict complete mode for that control.
- Pilot 004 reran the complete literal schedule as a **pilot only**. Its native-Year control receipts distinguish the requested `2011_2026_Year` window from a contained result-page refinement interval. The latter is never relabelled as the applied search window. Some cells have reconciled Article Number captures, while failures remain `total: null`. See [Pilot 004](pilots/004/pilot.md). The pilot used no wildcard, language, type, access, Date Added, or controlled-vocabulary supplement. The historical Pilot 004 evidence is immutable. It does not alter this source configuration or authorize a final search.
- The current adapter now uses percent-component route encoding with `%20` spaces and reads a hidden active native page choice under one visible Items Per Page host. Selecting 100 can repair rendered B2 rows 1 through 100, but they are first-page evidence only: the historical B2 total was 131. Both complete matching passes must then continue through contiguous rows 101 through 131 and reconcile the ordered 1 through 131 capture. These technical changes do not reinterpret the historical B2 artifact or make it mergeable.
- Exact native Year control rejection remains a source limitation. If requested `2011` resets after focus leaves the start input, or if Apply changes `2011_2026_Year` to `2011_2025_Year`, the failure remains fatal with `total: null`. Do not retry Apply, force a DOM value, or use a URL-only year substitution.
- Pilot 005 submitted one complete expression per partition from the schedule without proximity operators. IEEE echoed all nine expressions exactly at least once. The direct queries ranged from 2,169 to 5,947 characters, so the query readback gives no reason to split them. The native Year control still prevented a complete schedule. Only `A3`, `B2`, and `BG1` returned equal totals twice (`6`, `131`, and `1`). Every changed partition strict capture failed with `total: null`. See [Pilot 005](pilots/005/pilot.md). Keep these results diagnostic and do not authorize a final search.

## Query schedule

Render every row as one explicit source expression. Fully parenthesize each ordinary and compound block. The four expansion rows preserve the shared compound Boolean definitions.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` count-only attempt preserved an explicit year-control failure. `BG1` was stopped before execution. Do not use this source run as a final search until the control reconciles.
- [x] [Pilot 002](pilots/002/pilot.md): repeat count-only diagnostic used the same complete `A1` expression and `2011` through `2026` control. It ended with `status: error`, `total: null`, and no reconciled source result. `BG1` was not run. Do not use this source run as a final search.
- [x] [Pilot 003](pilots/003/pilot.md): Language remains unavailable and no type union is accepted. The 10-wildcard candidate is shorter but has no date-controlled stable-ID comparison. No third year-control request was made.
- [Pilot 004](pilots/004/pilot.md): all nine superseded pair-based partitions and cells were attempted with native inclusive `2011`–`2026` Year Apply. Complete unions are limited to reconciled cells. Incomplete unions remain null, including the B2 >100 investigation. This historical evidence remains immutable.
- [x] [Pilot 005](pilots/005/pilot.md): all nine direct expressions without proximity operators received exact query echo at least once. Only `A3`, `B2`, and `BG1` produced repeated totals. Native Year control and rendered state failures left all four changed strict captures at `total: null`, so IEEE remains unresolved.
