# ESA Indico

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: ESA Indico
- Interface: Web
- Platform: European Space Agency Indico
- URL: https://indico.esa.int/
- Search field or local route: Complete bounded local harvest from category 0 with the deterministic local matcher. Do not use rendered `q` as a Boolean search.
- Main evidence window: Do not restrict the harvest by event date. Apply the evidence window to candidate reports after retrieval.
- Language: ESA exposes no Language filter or language parameter. Apply no source language filter and determine English from the full text during screening.
- Publication type: Apply no publication type, peer review, access, or full-text availability filter beyond the stated source route.
- Database or collection selection: Category 0 across events, contributions, and materials. Preserve all public attachment and owner routes required by complete mode.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Keep exact local expressions normative and use no wildcard in them. A diagnostic candidate may use only the local trailing one-token `*`, which adds broader recall and requires set evidence before adoption. Assume no unrequested stemming or variants.

- Literal `L(s)`: Use one straight double-quoted literal. The local matcher tokenizes it with NFKC, case folding, and lexical boundaries.
- Atom `A(s)`: `L(s)` in the local matcher expression.
- Boolean: Uppercase `AND` and `OR` with explicit parentheses.
- Block `F(S)`: join `A(s)` for every ordinary member of `S` with source OR. Fully parenthesize the result.
- Pair `PAIR(a,b)`: `L(a) NEAR/5 L(b)`. The local matcher applies this unordered rule within one record field.
- Paired blocks: retain every fixed phrase and replace every declared pair with `PAIR(a,b)`.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a descriptor only after a pilot proves its source mapping and assignment.
- Source limitation: Rendered `q` is a prefix-AND search and cannot express the Boolean schedule. ESA exposes no Language filter. Use the bounded local harvest for exact Boolean and same-field proximity matching, and use up to three focused pilots for parser, coverage, attachment, resume, and cutoff behavior before any final run.

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

- [x] [Pilot 001](pilots/001/pilot.md): exact local A1, BG1, and `NEAR/5` parsing passed. The shorter wildcard candidate remains unaccepted because it broadens recall.
- [x] [Pilot 002](pilots/002/pilot.md): rendered `q` cannot express the Boolean schedule, and ESA exposes no Language filter.
- [x] [Pilot 003](pilots/003/pilot.md): category-0 harvest timed out before event retrieval. Fixture checks passed but do not establish source coverage.
