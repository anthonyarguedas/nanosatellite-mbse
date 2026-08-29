# Source Name

Last pilot saved in commit: NA
PSR final searches saved in commit: NA
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_<source>.py`

Save primary final searches and, where applicable, forward citation searches in `final-searches/`. Save PSR final searches in `psr-searches/` for Scopus and Web of Science only. Name artifacts with the query ID (`A1.json`, `PSR1.json`) or citation seed report ID (`<paperID>.json`).

The search script records the exact query, controls, source and interface identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. Record only fixed methodological decisions and pilot conclusions here.

## Fixed source configuration

- Source or collection:
- Interface: Web
- Platform:
- URL:
- Search field or local route:
- Main evidence window: 2011-01-01 through the common cutoff set by `P-001`.
- Language:
- Publication type:
- Database or collection selection:
- Other shared limits:

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Define the source literal, field atom, Boolean operators, and pair form here. Expand every listed literal and declared pair. Do not use implicit stemming, wildcards, or omitted variants.

- Literal `L(s)`:
- Atom `A(s)`:
- Boolean:
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with the source OR operator.
- Pair `PAIR(a,b)`:
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary:
- Source limitation:

## Query schedule

`F(G_model)`, `F(G_structure)`, `F(C1)`, and `F(T2)` include their fixed phrases and expanded pairs.

| ID | Source-native construction |
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

Scopus and Web of Science only. Define `F(X)` and `F(Q)` from [the supporting protocol](../../protocol-prior-secondary-reviews.md#additional-concept-blocks).

| ID | Source-native construction |
|---|---|
| `PSR1` | `F(X) AND F(M_H) AND F(Q)` |
| `PSR2` | `F(X) AND F(M_B) AND F(R) AND F(Q)` |
| `PSR3` | `F(P) AND (F(E_H) OR F(E_F)) AND (F(M_H) OR F(M_B)) AND F(Q)` |
| `PSR4` | `F(X) AND (F(G_model) OR F(G_structure) OR F(C1)) AND F(Q)` |

PSR searches have no lower date limit and no language, document type, subject, access, or peer review filter.

## Pilots

Create each pilot from [the pilot template](pilots/template/pilot.md). Start with one pilot. Use a second or third only for a specific unresolved issue. More may exist when justified. ESA Indico may start with up to three focused pilots.
