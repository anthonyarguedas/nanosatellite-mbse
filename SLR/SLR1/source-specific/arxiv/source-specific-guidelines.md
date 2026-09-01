# arXiv

Last pilot saved in commit: NA
PSR final searches saved in commit: NA (not applicable)
Final searches saved in commit: NA
Citation chasing searches saved in commit: NA (not applicable)
Source excluded from review due to search failure in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_arxiv.py`

Save primary final searches in `final-searches/` and name each artifact with its query ID, such as `A1.json`. The adapter always saves `A1.search-page.png` before search execution and `A1.results-page.png` after first-page result readback. Both PNGs are saved beside the JSON. There is no screenshot opt-out.

The script artifact is authoritative for each event's query, controls, source identity, timestamps, behavior, total, pagination, ordering, identifiers, capture, completeness, screenshots, and failures. This file records fixed decisions and pilot conclusions.

## Fixed source configuration

- Source or collection: the full multidisciplinary arXiv repository.
- Interface: Web.
- Platform: arXiv Search.
- URL: https://arxiv.org/search/advanced
- Search field: rendered repeatable Advanced Search rows. Select `All fields` for every normative row.
- Main evidence window: request 2011-01-01 through the common cutoff as inclusive calendar bounds. Select `Submission date (original)`. The adapter submits the following day as arXiv's upper-exclusive `US/Eastern` endpoint.
- Ordering: select `Submission date (oldest first)`. Exhaust every cell twice and require equal totals and ordered arXiv ID ledgers.
- Versions and identity: exclude older versions from discovery results. Retain the bare arXiv ID and any version suffix shown by the source. Preserve source submission metadata for later report-version decisions.
- Language: the web interface has no language limiter. Apply no language filter. Determine English from the full text during screening.
- Publication type: arXiv is bounded to submissions and e-prints. Apply no document-type, peer-review, access, or full-text-availability filter.
- Database or collection selection: search all classifications. Select no subject root or category restriction. Include cross-listed papers.

## Source translation

Use the exact concept membership and compound definitions in [the cross-source strategy](../../protocol-discovery-and-appraisal.md#search-streams-and-set-construction). Expand every listed ordinary term. Use no Atom syntax, proximity operator, pair expansion, wildcard, or controlled-vocabulary supplement.

- Literal `L(s)`: preserve the listed spelling, punctuation, and spacing inside straight double quotes.
- Ordinary block `F(S)`: join every `L(s)` in `S` with homogeneous uppercase `OR` inside one rendered All-fields row. Do not add parentheses inside the row.
- Conjunction: place each factor in a separate rendered All-fields row. Join rows with the source's outer `AND` control. The first row's ignored operator remains `AND` for exact readback.
- Combined `M` row: join every `M_H` and `M_B` literal in one homogeneous OR row when the request fits.
- Compound distribution: distribute one unchanged OR factor into separate source cells when the complete request is rejected. Preserve every cell total and reconcile the complete bare-ID union.
- Controlled vocabulary: add no Category Taxonomy terms. It is a classification hierarchy with scope notes and exact IDs. It does not provide a proved discovery thesaurus mapping for these concept blocks.
- Analyzer boundary: quoted phrases and homogeneous OR behavior are source-native. The adapter does not claim unrequested stemming, lemmatization, punctuation equivalence, acronym expansion, or cross-field equivalence.

Pilot 004 found that the direct `A2` request was rejected before a source total. Split only its unchanged `M_H OR M_B` factor. The identity is:

```text
P AND E_F AND (M_H OR M_B)
=
(P AND E_F AND M_H) OR (P AND E_F AND M_B)
```

`BG1` and `BG2` also use lossless distribution of their declared compound branches. All other partitions use one source cell.

## Query schedule

Every `F(...)` below is one rendered All-fields OR row. Each `AND` separates rendered rows.

| ID | Browser cell construction |
|---|---|
| `A1` | One cell: `F(P) AND F(E_H) AND F(M_H)` |
| `A2` | Two cells: `F(P) AND F(E_F) AND F(M_H)`, then `F(P) AND F(E_F) AND F(M_B)` |
| `A3` | One cell: `F(P) AND F(E_H) AND F(M_B)` |
| `B1` | One cell: `F(P) AND F(M_H)` |
| `B2` | One cell: `F(P) AND F(M_B) AND F(R)` |
| `BG1` | Two cells: `F(P) AND (F(G_model_fixed) OR F(G_mission_exact))`, then `F(P) AND F(G_mission) AND F(M_B)` |
| `BG2` | Two cells: `F(P) AND (F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation))`, then `F(P) AND F(G_product) AND F(M_B)` |
| `BC1` | One cell: `F(P) AND (F(C1_fixed) OR F(G_DSL))` |
| `BT2` | One cell: `F(P) AND F(M_B) AND F(T_precise)` |

The parenthesized OR notation in the table describes membership within one homogeneous row. Do not type those parentheses into the rendered term field.

## Controls and limitations

- Use the normal Advanced Search form for the first pass of every CLI event. Require exact configured-form and result-route readback.
- Capture full records through rendered result cards and native `More` controls. Do not substitute Atom metadata into a browser event.
- Use native 100-record pages when the planned limit requires them. A final cell must set `--limit` and `--max-pages` high enough to cover the exact source total.
- A complete final cell must pass the adapter's strict two-pass ordered-ID reconciliation. A count-only or one-pass artifact is not final-search evidence.
- Save the mandatory configured-search and first-results screenshots for every source cell. A screenshot failure makes the event fail.
- A source or adapter failure keeps `total: null`. It never becomes zero. Preserve the failed artifact and rerun only the unchanged event or a documented lossless repair.
- Space consecutive source events to respect live rate limits. Pilot 004 observed an HTTP 429 during an unchanged strict event. It was retained as a transient failure and was not treated as a source total.

## Pilots

- [x] [Pilot 001](pilots/001/pilot.md): one representative structured-row `A1` cell and one `BG1` marker/model cell returned exact zero totals. These were cell diagnostics.
- [x] [Pilot 002](pilots/002/pilot.md): the `CubeSat*` representative cell returned zero. The wildcard remained unaccepted. Language and type controls remained unavailable.
- [Pilot 003](pilots/003/pilot.md): the now-superseded Atom route demonstrated bounded API transport behavior and pilot-only partition unions. Its output remains historical diagnostic evidence. It is not the prospective search route.
- [x] [Pilot 004](pilots/004/pilot.md): the rendered web translation completed all nine partitions through 12 lossless cells. The unions were `0`, `0`, `0`, `6`, `4`, `2`, `0`, `0`, and `2`. Every cell passed strict two-pass capture and retained both mandatory screenshots. The five unchanged core partitions matched the Atom Pilot 003 bare-ID sets exactly.
