# arXiv

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Validated pilot route: [`../../scripts/arxiv_pilot003/atom_pilot.py`](../../scripts/arxiv_pilot003/atom_pilot.py), using the documented arXiv Atom API. It writes pilot-only, non-mergeable artifacts; do not use its output as a final search.

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`. A future final runner must retain the Atom API route, exact query/cell ledger, controls, source totals, complete stable-ID capture, and failures demonstrated by Pilot 003.

The event artifact is authoritative for query, controls, source identity, timestamps, behavior, totals, pagination, ordering, identifiers, export, completeness, and failures. This file records fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: arXiv.
- Interface and platform: documented arXiv Atom API on arXiv. The rendered Advanced Search route remains separately documented and is not assigned Atom grammar.
- Endpoint and method: `GET https://export.arxiv.org/api/query` with `search_query`, `start`, `max_results`, `sortBy=submittedDate`, and `sortOrder=ascending`.
- Search field: documented Atom `all:` field for every normative free-text literal. `all:` searches the API's fields; it is not a rendered Advanced Search row.
- Main evidence window: encode the inclusive calendar window as `submittedDate:[YYYYMMDD0000 TO YYYYMMDD2359]` (minute GMT syntax). Pilot 003 observed a known record in its 2017 `<published>`/v1 interval despite a later `<updated>` timestamp, so this route is recorded as original-submission/v1 behavior. Preserve `<published>` and `<updated>` for later report-version decisions.
- Ordering, pagination, and identity: use native `submittedDate` ascending order, `start` offsets, and no more than 2,000 records per API call. Exhaust every source total twice and require equal ordered bare and versioned arXiv-ID ledgers. Retain both the bare stable ID and the returned versioned manifestation ID.
- Language: no usable API Language control. Apply no language filter; determine English from full text during screening.
- Publication type: this source is bounded to arXiv submissions/e-prints (preprints). No API document-type, peer-review, access, or full-text-availability filter is available or applied.
- Database or collection selection: all arXiv classifications; no category restriction. The Category Taxonomy is not a content thesaurus supplement for this route.

## Prospective Atom translation

Use the exact concept membership and pair declarations in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed literal and declared pair. Exact literals remain normative. A trailing wildcard may be tested only as a labelled diagnostic cell; it is not accepted from totals alone.

- Literal `L(s)`: render `all:s` for a single token and `all:"s"` for a multiword phrase. Preserve the listed punctuation, spelling, and spacing in the source query.
- Boolean: use documented Atom `AND`, `OR`, and parenthesized groups. This grammar is validated only for the Atom API; never attribute it to a browser Advanced Search raw All-fields row.
- Block `F(S)`: one parenthesized Atom OR group over all alternatives in `S`.
- Pair `PAIR(a,b)`: `(all:a AND all:b)`. This is a deliberately broader candidate fallback for the unavailable same-field, either-order, no-more-than-five-token predicate. Check retained title and abstract locally for the exact pair where those fields permit it, but do **not** discard a broader API candidate on that local check.
- Paired blocks: retain every fixed phrase and every declared pair. The pilot's transport control demonstrated the fallback on declared `reusable`/`model` pair evidence in the abstract of `1102.2933`; this does not turn the fallback into an API proximity feature.
- Controlled vocabulary: add no supplement. The arXiv Category Taxonomy has textual classifications and editorial scope notes, not a proved controlled-vocabulary mapping for these concept blocks.

The direct full expressions for `A2`, `BC1`, and `BT2` exceeded the live proxy request-line limit and failed with `total: null` (`A2` and `BC1`: HTTP 400; `BT2`: HTTP 414). Pilot 003 replaced only one parenthesized OR factor at a time, which is a lossless distribution of the unchanged conjunction:

| Partitions | Atom cell route |
|---|---|
| `A1`, `A3`, `B1`, `B2`, `BG1`, `BG2` | One complete parenthesized Atom expression. |
| `A2` | Two cells: unchanged `P AND E_F`, with the final factor separately `M_H` and `M_B`. |
| `BC1` | Two cells: unchanged `P`, with the 62 `C1` alternatives split as 1–31 and 32–62. |
| `BT2` | Six cells: unchanged `P AND M_B`, with the 224 declared `T2` pairs split as 1–38, 39–76, 77–114, 115–152, 153–190, and 191–224. |

Every replacement URI was at most 3,791 encoded characters. Preserve each cell total and reconcile its complete bare arXiv-ID union; a source failure remains `null`, never zero.

## Query schedule

The table is semantic. Implement each row as the full Atom Boolean expression or the documented lossless cell union above. `F(G_model)`, `F(G_structure)`, `F(C1)`, and `F(T2)` include fixed phrases and expanded pair fallbacks.

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

## Controls and limitations

- No language, document-type, proximity, focus, major-topic, or API-side export-selection control is available. Atom XML is captured and normalized locally; pagination is the available complete-capture control.
- API `all:` matching and analyzer behavior remain source-native. Title/abstract local evidence is an audit aid, not a no-loss source filter.
- No category, cross-list, access, or peer-review restriction was applied. Category Taxonomy aliases, hierarchy, and source scope notes do not establish a discovery-vocabulary mapping.
- Wildcards are unaccepted for every partition. Pilots 001–002 gave no stable-ID equality/superset evidence, and Pilot 003 used none.
- The direct Atom API route is validated separately from the browser route: fields, grouping, phrases, dates, ordering, pagination, stable IDs, and pair fallback are recorded in [Pilot 003](pilots/003/pilot.md). The official [API User's Manual](https://info.arxiv.org/help/api/user-manual.html) is the syntax reference.

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): one representative structured-row `A1` cell and one `BG1` pair cell returned exact zero totals. These are not full-partition or final-search results.
- [x] [Pilot 002](pilots/002/pilot.md): the `CubeSat*` representative A1 cell was a count-only zero. Language and type controls remain unavailable, and the wildcard is unaccepted.
- [Pilot 003](pilots/003/pilot.md): validated the separate Atom route, repaired overlong expressions with lossless cells, and captured all nine bounded partition unions. These are diagnostic pilot artifacts, not final searches.
