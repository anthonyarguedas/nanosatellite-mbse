# IAF Digital Library

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

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

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Exact literals remain normative. A trailing wildcard may be tested only as a labelled diagnostic cell. Preserve punctuation, spacing, phrase, and spelling forms outside its replacement, and do not accept it from totals alone.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `L(s)` in the Any keyword expression.
- Boolean: Use uppercase `OR`, explicit parentheses, and whitespace for AND.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `(A(a) A(b))` in the same Any keyword route. This is the broader fallback candidate.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Split every partition into deterministic cells below the 500-character source limit. Run all cells and reconcile their stable paper-ID union. Apply exact pair checking to retained title and abstract text. Pilot 001 used 69-character and 38-character representative cells, both with exact zero totals. Pilot 002's 68-character `CubeSat*` A1 cell was also count-only zero. It supplies no stable-ID evidence and does not validate full partition coverage. Wildcard use remains unaccepted.

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

- [x] [Pilot 001](pilots/001/pilot.md): representative `A1` and broad pair cells stayed below 500 characters and returned exact zero totals. No complete partition route was used.
- [x] [Pilot 002](pilots/002/pilot.md): the 68-character `CubeSat*` A1 cell was a count-only zero. The indexed language field is not an exhaustive filter, no type control was added, and the wildcard is unaccepted.
