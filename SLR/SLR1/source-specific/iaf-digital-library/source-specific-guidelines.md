# IAF Digital Library

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed source decisions.

## Fixed source configuration

- Source or collection: IAF Digital Library
- Interface: Web
- Platform: International Astronautical Federation
- URL: https://dl.iafastro.directory/search/
- Search field or local route: Unqualified Any keyword query in the rendered search wizard.
- Main evidence window: Traverse without a lossy source date range. Apply the 2011 lower bound and exact cutoff to retained records. The source exposes year precision only.
- Language: `language:English` is an indexed wizard field, but no enumerated vocabulary or missing-assignment behavior is exposed. Do not treat it as an exhaustive source restriction. Determine English from the full text during screening.
- Publication type: This source is bounded to conference-paper records. Apply no additional type, peer-review, access, or full-text-availability filter.
- Database or collection selection: Full Digital Library with no event or conference restriction.
- Other shared limits: None.

## Source translation

Use the exact concept membership and compound Boolean definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Use no proximity operator, pair expansion, or local pair check. Use the trailing wildcard translation for the population block only. Keep every other ordinary term explicit.

- Literal `L(s)`: Use one straight double-quoted token or ordered phrase.
- Atom `A(s)`: Place `L(s)` in the unqualified Any keyword expression.
- Wildcard population `F_W(P)`: `(CubeSat* OR "cube sat*" OR cube-sat* OR nanosat* OR nano-sat* OR "nano sat*" OR SmallSat* OR "small sat*")`. These eight atoms replace the 26 explicit `P` terms for IAF searches.
- Boolean: Use uppercase `OR`, explicit parentheses, and whitespace conjunction for semantic `AND`.
- Ordinary block `F(S)`: For every block other than `P`, join `A(s)` for every member of `S` with source `OR`, then fully parenthesize the result.
- `G_model`: `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))`.
- `G_structure`: `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))`.
- `C1`: `F(C1_fixed) OR F(G_DSL)`.
- `T_precise`: `F(T_precise)`.
- Controlled vocabulary: Add no supplement. Free text remains mandatory. Add a descriptor only after its source mapping and assignment are proved.

The source accepts at most 500 query characters. Distribute each compound outer `OR` into named conjunction branches. Pack each branch into deterministic cells below the cap. Each branch plan must cover every Cartesian alternative tuple exactly once. Run all cells and reconcile the stable paper-ID union across cells and branches.

Use these expansion branches:

| Partition | Source branches |
|---|---|
| `BG1` | `F_W(P) AND F(G_model_fixed)`; `F_W(P) AND F(G_mission_exact)`; `F_W(P) AND F(G_mission) AND F(M_B)` |
| `BG2` | `F_W(P) AND F(G_structure_fixed)`; `F_W(P) AND F(G_product_exact)`; `F_W(P) AND F(G_variation)`; `F_W(P) AND F(G_product) AND F(M_B)` |
| `BC1` | `F_W(P) AND F(C1_fixed)`; `F_W(P) AND F(G_DSL)` |
| `BT2` | `F_W(P) AND F(M_B) AND F(T_precise)` |

The complete wildcard schedule contains 158 cells. Keep the source unrestricted by event, language, type, access, peer review, and full-text availability. Apply the evidence window locally after every complete raw traversal.

## Query schedule

The table uses `AND` and `OR` as semantic labels. Render them with the source operators, wildcard population block, and branch distribution above.

| ID | Source construction | Current cells |
|---|---|---:|
| `A1` | `F_W(P) AND F(E_H) AND F(M_H)` | 37 |
| `A2` | `F_W(P) AND F(E_F) AND (F(M_H) OR F(M_B))` | 48 |
| `A3` | `F_W(P) AND F(E_H) AND F(M_B)` | 21 |
| `B1` | `F_W(P) AND F(M_H)` | 4 |
| `B2` | `F_W(P) AND F(M_B) AND F(R)` | 20 |
| `BG1` | `F_W(P) AND (F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B)))` | 6 |
| `BG2` | `F_W(P) AND (F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B)))` | 6 |
| `BC1` | `F_W(P) AND (F(C1_fixed) OR F(G_DSL))` | 3 |
| `BT2` | `F_W(P) AND F(M_B) AND F(T_precise)` | 13 |
