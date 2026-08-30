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

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use literal expansions. Pilot 003's 10-wildcard A1 candidate meets the source cap but remains unaccepted without a date-controlled stable-ID comparison.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `("All Metadata":L(s))`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `(A(a) NEAR/6 A(b))`. This unordered form allows no more than five intervening token positions under the source distance convention.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Do not use a grouped field wrapper around a Boolean block. Expand every atom before combining it.
- Pilots 001 and 002 accepted the complete `A1` All Metadata expression before submission. Pilot 001 records a requested-range mismatch after Apply and three contradictory polls. Pilot 002 repeats the same count-only diagnostic with the `2011` through `2026` year control. Its artifact records source-observed query and year-control readback, then ends with `status: error` and no source total. No reconciled date-controlled `A1` result exists. This leaves an unresolved source-control limitation. Do not replace it with an unbounded query or local date filtering. The exact publication-day window is unavailable in count-only mode because the adapter requires strict complete mode for that control.
- Pilot 004 reran the complete literal schedule as a **pilot only**. Its native-Year control receipts distinguish the requested `2011_2026_Year` window from a contained result-page refinement interval; the latter is never relabelled as the applied search window. Some cells have reconciled Article Number captures, while failures remain `total: null`; see [Pilot 004](pilots/004/pilot.md). The pilot used no wildcard, language, type, access, Date Added, or controlled-vocabulary supplement. A pilot-local percent-component encoding compatibility wrapper left every decoded adapter-generated query unchanged after IEEE rejected some equivalent form-style routes. It does not alter this source configuration or authorize a final search.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators above. `F(G_model)`, `F(G_structure)`, `F(C1)`, and `F(T2)` include fixed phrases and expanded pairs.

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
| `BT2` | `F(P) AND F(M_B) AND F(T2)` |

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` count-only attempt preserved an explicit year-control failure. `BG1` was stopped before execution. Do not use this source run as a final search until the control reconciles.
- [x] [Pilot 002](pilots/002/pilot.md): repeat count-only diagnostic used the same complete `A1` expression and `2011` through `2026` control. It ended with `status: error`, `total: null`, and no reconciled source result. `BG1` was not run. Do not use this source run as a final search.
- [x] [Pilot 003](pilots/003/pilot.md): Language remains unavailable and no type union is accepted. The 10-wildcard candidate is shorter but has no date-controlled stable-ID comparison. No third year-control request was made.
- [x] [Pilot 004](pilots/004/pilot.md): all nine literal partitions and cells were attempted with native inclusive `2011`–`2026` Year Apply. Complete unions are limited to reconciled cells; incomplete unions remain null, including the B2 >100 investigation. This is not a final search and does not change the source completion state.
