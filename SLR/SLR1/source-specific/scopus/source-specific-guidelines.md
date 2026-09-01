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
- Language: Main-review direct searches use the exact visible `Language` facet label `English`. Confirm full-report English during screening. PSR searches remain all-language.
- Publication type: Apply no type control. Pilot 002's source query accepted `DOCTYPE(ar OR cp OR ch OR rp)`, but retained record projections did not establish complete type assignment. Never apply peer-review, access, or full-text availability filters.
- Database or collection selection: Documents result scope and the full Scopus database. Apply no subject area.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Use literal expansions. Pilot 002's 10-wildcard A1 candidate is not accepted because the required literal comparison ended in error.

- Literal `L(s)`: Use one straight double-quoted loose token or ordered phrase.
- Atom `A(s)`: `TITLE-ABS-KEY(L(s))`.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `TITLE-ABS-KEY(L(a) W/6 L(b))`. This conservative unordered fallback may admit one extra intervening word.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Validate the `W/6` no-loss fallback and standalone acronym behavior once. Apply exact pair checking locally where retained fields permit it.
- Pilot 001 accepted the full `A1`, `BG1`, and `PSR1` expressions with native query, year, scope, and sort readback. The count-only runs did not establish pair no-loss or standalone acronym behavior. Keep `W/6` as a conservative fallback and check retained final records locally.

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

- [x] [Pilot 001](pilots/001/pilot.md): `A1`, `BG1`, and supporting `PSR1` count-only diagnostics completed. No translation change. Pair checking remains a final-run limitation.
- [x] [Pilot 002](pilots/002/pilot.md): exact `English` language control was read back. The proposed type union and wildcard A1 remain unaccepted. The literal comparison ended with `status: error` and no total.
- Pilot 003 is a diagnostic-only follow-up under [`pilots/003/`](pilots/003/pilot.md). It does not change any completion state above or authorize a final search. It keeps literal queries, Documents scope, Date (oldest), the main-route visible `English` facet, no `DOCTYPE`, and PSR's unrestricted language/type/subject/access controls. Its complete ID receipts and any unresolved safe failures stay separate from final-search artifacts. EID is used only for post-retrieval abstract follow-up of an already completed stable-ID union. It is not a discovery translation. The 10-wildcard A1 proposal remains unaccepted. Any future wildcard needs a per-partition complete stable-ID superset comparison. Scopus has no searchable thesaurus or expansion switch, so no unvalidated descriptor expansion is used.
- Pilot 003 recovery keeps explicit native zero pages separate from failures. A native zero has no sort, page-size, or abstract control. It records those controls as `not_applicable` and does not make a requested native page size mandatory. Positive pages still require native range, row, ID, sort, and page-size reconciliation. Two matching complete ordered ID passes on distinct fresh adapter-owned pages remain required for any future complete artifact.
- Abstract recovery uses a canonical EID-only query, Documents scope, native page size, and an explicit authorized browser target. It does not carry discovery date, language, title, or facet clauses into the identity query. An unaccepted group larger than one is split deterministically into two children. The recovery locks its output root and journals each prepared/started/outcome action; a runner exception or interruption after start is delivery-ambiguous and is never auto-replayed. It seals its cap and other action settings before launch, rejects changed resume settings before any action, gives the child an adapter-private staging path, and publishes only after shared terminal-marker plus transaction-binding verification through no-follow descriptor-relative create-only operations. Only closed compact strict v3 two-pass leaves with exact requested/source/export totals, matching ID hashes, canonical query binding, and unique returned IDs listed in `accepted-leaf-manifest.json` may contribute new abstracts to a rebuilt union. Immutable migration manifests separately bind accepted legacy leaves and do not relabel them as v3 output. A singleton failure is unresolved and is never treated as no native abstract. This recovery does not complete PSR2 or PSR4.
