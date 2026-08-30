# arXiv

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_arxiv.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`.

The script artifact is authoritative for per-event query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records only fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: arXiv
- Interface: Web
- Platform: arXiv
- URL: https://arxiv.org/search/advanced
- Search field or local route: Repeatable structured rows in the rendered Advanced Search form.
- Main evidence window: Use submitted-date bounds from 2011-01-01 through the common cutoff with day precision. Preserve linked publication dates for later version decisions.
- Language: No usable Language control is exposed. Apply no source language filter. Determine English from the full text during screening.
- Publication type: This source is bounded to arXiv submissions/e-prints (preprints). Apply no additional type, peer-review, access, or full-text-availability filter.
- Database or collection selection: All classifications with cross-lists included and no category restriction.
- Other shared limits: None.

## Source translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Exact literals remain normative. A trailing wildcard may be tested only as a labelled diagnostic cell. Preserve punctuation, spacing, phrase, and spelling forms outside its replacement, and do not accept it from totals alone.

- Literal `L(s)`: Use one source term. Quote every multiword phrase.
- Atom `A(s)`: one structured `all` field row containing `L(s)`.
- Boolean: Join rows with the visible `AND` control. Do not rely on raw All fields grouping.
- Block `F(S)`: a lossless union of cells, one cell per alternative in `S`.
- Pair `PAIR(a,b)`: two `all` rows joined by `AND`. This is the broader fallback candidate.
- Paired blocks: retain every fixed phrase and expand every declared pair into its own cell.
- Controlled vocabulary: Add no supplement initially. Free text remains mandatory. Add a category only after a pilot proves its mapping and assignment.
- Source limitation: Materialize each partition as the Cartesian union of its block alternatives. Preserve every cell total and arXiv ID union. Apply exact pair checking to retained title and abstract text. Pilot 001 tested one structured-row `A1` cell and one `BG1` pair cell only. Both returned exact zero totals. Pilot 002's `CubeSat*` A1 cell was also count-only zero. No stable-ID comparison or full-partition coverage exists, so wildcard use remains unaccepted.

## Query schedule

The table is semantic. Execute each row as the lossless union of structured-row Cartesian cells. `F(G_model)`, `F(G_structure)`, `F(C1)`, and `F(T2)` include fixed phrases and expanded pair cells.

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

- [x] [Pilot 001](pilots/001/pilot.md): one representative structured-row `A1` cell and one `BG1` pair cell returned exact zero totals. These are not full-partition or final-search results.
- [x] [Pilot 002](pilots/002/pilot.md): the `CubeSat*` representative A1 cell was a count-only zero. Language and type controls remain unavailable, and the wildcard is unaccepted.
