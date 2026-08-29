# ProQuest Dissertations & Theses Global

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: ProQuest Dissertations & Theses Global (PQDT Global)
- Interface: Web
- Platform: ProQuest
- URL: https://www.proquest.com/pqdtglobal/commandline
- Search field or local route: Command Line Search `NOFT` field.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen records in the cutoff year against the exact common cutoff.
- Language: Apply no source language filter. Determine English full text during screening.
- Publication type: Apply no publication type, peer review, access, or full-text availability filter beyond the stated source route.
- Database or collection selection: Select exactly one PQDT Global database label. Do not select ATAI or another ProQuest database.
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
- Source limitation: `NOFT` searches anywhere except full text. This reduces bias toward dissertations with searchable full text, while uneven bibliographic metadata can still affect retrieval. Validate `NOFT` field coverage and pair behavior. Resolve degree subtype, availability, and completion status during screening.
- Pilot 001 accepted complete `A1` and `BG1` count-only expressions with the exact PQDT Global scope, 2011-2026 `YR` bounds, and frozen spelling/form variant controls. The totals were `1` and `1`. Count-only diagnostics do not test pair no-loss or complete capture.

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

- [x] [Pilot 001](pilots/001/pilot.md): complete `A1` and `BG1` count-only diagnostics succeeded with totals `1` and `1`. The adapter's uncommitted strict cap guard was tested before the live runs. These are not final searches.
