# Scopus

Last pilot saved in commit: NA
PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_scopus.py`

Save primary final searches and forward citation searches in `final-searches/`. Save PSR final searches in `psr-searches/`. Name artifacts with the query ID (`A1.json`, `PSR1.json`) or citation seed report ID (`<paperID>.json`).

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: Scopus
- Interface: Web
- Platform: Elsevier Scopus
- URL: https://www.scopus.com/pages/search/publications?type=advanced
- Search field or local route: Advanced Search `TITLE-ABS-KEY` topic field.
- Main evidence window: Use `--year-start 2011 --year-end <cutoff-year>`. Screen records in the cutoff year against the exact common cutoff.
- Language: Apply no source language filter. Determine English full text during screening.
- Publication type: Apply no publication type, peer review, access, or full-text availability filter beyond the stated source route.
- Database or collection selection: Documents result scope and the full Scopus database. Apply no subject area.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use no wildcards and assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted loose token or ordered phrase.
- Atom `A(s)`: `TITLE-ABS-KEY(L(s))`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `TITLE-ABS-KEY(L(a) W/6 L(b))`. This conservative unordered fallback may admit one extra intervening word.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Validate the `W/6` no-loss fallback and standalone acronym behavior once. Apply exact pair checking locally where retained fields permit it.

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

### PSR query schedule

Use the same `L`, `A`, `F`, and Boolean rules for `X` and `Q` from [the supporting protocol](../../protocol-prior-secondary-reviews.md#additional-concept-blocks).

| ID | Source construction |
|---|---|
| `PSR1` | `F(X) AND F(M_H) AND F(Q)` |
| `PSR2` | `F(X) AND F(M_B) AND F(R) AND F(Q)` |
| `PSR3` | `F(P) AND (F(E_H) OR F(E_F)) AND (F(M_H) OR F(M_B)) AND F(Q)` |
| `PSR4` | `F(X) AND (F(G_model) OR F(G_structure) OR F(C1)) AND F(Q)` |

PSR searches have no lower date limit and no language, document type, subject, access, or peer review filter. Apply the common upper cutoff without narrowing the source-native topic fields.

## Pilots

Create each pilot from [the pilot template](pilots/template/pilot.md). Start with one pilot. Use a second or third only for a specific unresolved issue. More may exist when justified. ESA Indico may start with up to three focused pilots.
