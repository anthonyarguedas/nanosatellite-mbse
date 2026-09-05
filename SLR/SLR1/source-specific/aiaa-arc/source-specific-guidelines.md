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
- Wildcard decision: In every population block, replace only the adjacent literals `"nanosatellite" OR "nanosatellites"` with unquoted `nanosatellit*`. Pilot 009 found equal source totals, stable ID sets, and DOI sets in all 94 paired cells, with equal 119 DOI schedule unions. Keep all other terms literal. No other wildcard use is accepted.

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

## Final capture contract

Run each cell with `--require-complete` and a native RIS export directory. Retain each source RIS `AB` or `N2` value in `abstract` and each RIS `TY` value in `documentType`. Require a nonempty source document type for every retained record. ARC can omit `AB/N2` even when its visible form submits `include=abs`. For each such record, capture the complete abstract from the normal rendered abstract page or the source-designated opening abstract block in the visible reader. Record an explicit source-unavailable state when ARC exposes no abstract. Source document types are metadata. Do not infer the reviewer's `publication_type` from them. Use one explicit, visibly loaded ARC authorization tab per cell. Pin corrective execution to Playwright 1.60.0 because the post failure diagnostic showed that 1.62.0 could not initialize the shared Chrome CDP session.

Retain every cell query, source total, stable ID, screenshot, failure, retry, native export, full abstract, and source document type. ARC can render one publication under its normal DOI and an `@virtual_collection` stable ID while both visible RIS forms export the same publication DOI. Adapter v6 retains both source stable IDs, exports one canonical publication record, and records the alias as a within-source duplicate. Reconcile each partition and the complete source union by canonical DOI. Use no full Anywhere alternative as the screening corpus. The metadata only route is a priority subset. [Pilot 007](pilots/007/pilot.md) defines the accepted 94 cell route. [Pilot 009](pilots/009/pilot.md) defines the narrow wildcard acceptance.
