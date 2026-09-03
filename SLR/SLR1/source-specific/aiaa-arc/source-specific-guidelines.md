# AIAA Aerospace Research Central

Final searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`

Save final JSON files in `final-searches/` by query ID. Every CLI event automatically saves sibling `.search-page.png` and `.results-page.png` files. No option disables them. A successful event requires both images and their receipt in the JSON.

## Fixed source configuration

- Source or collection: AIAA Aerospace Research Central
- URL: https://arc.aiaa.org/search/advanced
- Fields: Title, Keywords, Abstract, and selected Anywhere rows
- Evidence window: Use `--date-start 2011-01-01 --date-end <cutoff>`. Reconcile source month controls with exact retained dates.
- Language: Apply no source filter. ARC exposes no usable language control. Confirm English during screening.
- Publication type: Apply no type, peer review, access, Topic, or full text filter. The visible facets do not prove a lossless eligible union.
- Collection: Search all ARC content.

## Source translation

Use the concepts and compound definitions in [the discovery protocol](../../protocol-discovery-and-screening.md#search-streams-and-set-construction). ARC combines visible rows with `AND`.

- Literal `L(s)`: One straight double quoted token or ordered phrase.
- Field block `F_f(S)`: Join all literals in field `f` with `OR`.
- Metadata block `META(S)`: `F_Title(S) OR F_Keywords(S) OR F_Abstract(S)`. Implement each outer field `OR` as a declared union of field assignment cells.
- Anywhere block `ANY(S)`: Put the complete block in Anywhere.
- Controlled vocabulary decision: Apply no Topic filter or supplement. ARC exposes labels and numeric concept IDs without preferred term, scope, hierarchy, version, or expansion evidence. The least restrictive mapped Topic union removed records with unresolved eligibility.
- Wildcard decision: In every population block, replace only the adjacent literals `"nanosatellite" OR "nanosatellites"` with unquoted `nanosatellit*`. Every tested cell retained the same source total, stable ID set, and DOI set. Keep all other terms literal.

## Accepted cells

| ID | Construction |
|---|---|
| `A1` | `META(P) AND META(M_H) AND ANY(E_H)` |
| `A2` | `META(P) AND (META(M_H) OR META(M_B)) AND ANY(E_F)` |
| `A3` | `META(P) AND META(M_B) AND ANY(E_H)` |
| `B1` | `META(P) AND META(M_H)` |
| `B2` | `META(P) AND META(M_B) AND ANY(R)` |
| `BG1` | `ANY(P AND G_model)` |
| `BG2` | Factor wise metadata expansion of `P AND G_structure` |
| `BC1` | `META(P) AND ANY(C1)` |
| `BT2` | `META(P) AND META(M_B) AND ANY(T_precise)` |

Retain every cell query, source total, stable ID, screenshot, failure, and retry. Reconcile each partition and the complete source union by canonical DOI. Use no full Anywhere alternative as the screening corpus. The metadata only route is a priority subset. See [the readiness audit](../readiness-audit.md) for the accepted 94 cell plan and result bound.
