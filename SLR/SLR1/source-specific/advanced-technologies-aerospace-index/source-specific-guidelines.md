# Advanced Technologies & Aerospace Index

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Advanced Technologies & Aerospace Index
- Interface: Web
- Platform: ProQuest
- URL: https://www.proquest.com/ataindex/commandline
- Search field or local route: Command Line Search `NOFT` field.
- Main evidence window: Use exact `--date-start 2011-01-01 --date-end <cutoff>` publication-date bounds.
- Language: Apply no source language filter. Determine English full text during screening.
- Publication type: Apply no publication type, peer review, access, or full-text availability filter beyond the stated source route.
- Database or collection selection: Select only Advanced Technologies & Aerospace Index. Deselect every parent and other ProQuest database.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use no wildcards and assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `NOFT(L(s))`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `NOFT(L(a) NEAR/5 L(b))`. `NEAR/5` is unordered and counts intervening words.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Keep this source in an event separate from PQDT Global. Validate the exact product selection and one query readback.

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

Create each pilot from [the pilot template](pilots/template/pilot.md). Start with one pilot. Use a second or third only for a specific unresolved issue. More may exist when justified. ESA Indico may start with up to three focused pilots.
