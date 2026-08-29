# AIAA Aerospace Research Central

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: AIAA Aerospace Research Central (ARC)
- Interface: Web
- Platform: AIAA Aerospace Research Central
- URL: https://arc.aiaa.org/search/advanced
- Search field or local route: One `Anywhere` (`AllField`) Advanced Search row.
- Main evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. The script applies source month bounds and checks exact retained dates.
- Language: ARC exposes no interface language filter. Determine English full text during screening.
- Publication type: Apply no publication type, peer review, access, or full-text availability filter beyond the stated source route.
- Database or collection selection: Full ARC collection with access set to all and no publication or Topic facet.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use no wildcards and assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal.
- Atom `A(s)`: `L(s)` inside one Anywhere row.
- Boolean: Use explicit parentheses and uppercase `OR`. Whitespace is the source AND operation.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `(A(a) A(b))` in the same Anywhere row. This is the broader fallback candidate.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: ARC exposes no supported proximity operator. Apply exact pair checking to retained title, keyword, and abstract text. Pilot 001 accepted `BG1` with total `8,088`. A [100-row preview](diagnostics/BG1-first-100.md) found a population term in only 10 titles and an artifact phrase in none. `P` alone returned `9,358`, `G_model` alone returned `32,702`, and explicit `AND` left `BG1` at `8,088`. Anywhere searches hidden indexed content, so title inspection cannot prove false matches, but it confirms poor visible precision. Reconsider narrower fields or a lossless field union before the final search.

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

- [x] [Pilot 001](pilots/001/pilot.md): full `A1` and `BG1` count-only translations succeeded with diagnostic totals `492` and `8,088`. Final collection still requires source-month partitioning.
