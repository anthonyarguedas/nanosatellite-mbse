# S-D11 arXiv diagnostic pilot observations

- **Pilot ID:** `S-D11-P01-20260821T045351+0000`
- **Task/source:** `S-D11` / arXiv
- **Protocol commit:** `ad77460df82764312fb701f6be4ebf7eb5051c41`
- **Status/recommendation:** **blocked / `skip_for_now`**
- **Evidence index:** [`evidence-index.json`](evidence-index.json)

> Claim labels are **[observed]**, **[official_documentation]**, **[inferred]**, or **[untested]**. This is diagnostic only: no screening, relevance assessment, candidate construction/import, full-text/PDF retrieval, final event, or task/protocol/shared-file change occurred.

## Scope, boundary, and visible controls

- **[observed]** The current rendered arXiv homepage exposed top-level areas spanning Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering and Systems Science, and Economics. The Advanced Search form exposed **All fields**, visible AND/OR/NOT row controls, archive/category `all`, included cross-lists, Relevance, and native page-size choices 25/50/100/200. No category, archive, subject, content-type, language, access, peer-review, venue, or publication-type discovery restriction was applied. See `E-BOUNDARY` and `E-CONTROLS`.
- **[observed]** The rendered date controls included **Submission date (most recent)**, **Submission date (original)**, and **Announcement date**, plus Date range. The pilot used Date range from `2011-01-01`, no upper bound, and most-recent submission date only for bounded diagnostics. See `E-CONTROLS` and `E-DATE`.
- **[official_documentation]** The current arXiv help page directs users to the Advanced Search and describes arXiv identifiers. This official page was a comparison/supporting note, not a substitute for current rendered-UI observations. See `E-OFFICIAL`.

## Grammar and translation method

- **[observed]** The normal rendered one-row All fields form retained exact entered text and returned exact totals for controlled simple OR and AND probes. A raw mixed/parenthesized grouping suite did not demonstrate usable nested grouping: its distinct grouped forms had the same total. The draft translations therefore use visible multi-row AND controls with finite OR alternatives inside each row, never raw nested parentheses or mixed raw precedence. See `E-GRAMMAR`.
- **[observed]** A visible two-row All fields diagnostic retained both row values in the rendered query summary and returned an exact positive total. This validates the chosen UI-row implementation at small scale. See `E-MULTIROW`.
- **[observed]** Quoted and unquoted multiword probes differed; quoted hyphenated and spaced finite forms were accepted. Case-paired CubeSat and MBSE probes had equal bounded totals. Battery and batteries had different totals. See `E-GRAMMAR`.
- **[observed]** A finite-P versus `nanosat*` count-only comparison had equal totals, but stable-ID-set equality was not tested. **[inferred]** Retaining all finite P forms and forbidding `nanosat*` is the recall-safe draft rule. See `E-GRAMMAR`.
- **[untested]** Universal phrase, punctuation, case/acronym, stemming, lemmatization, synonym, automatic-expansion, query-length, and wildcard-set behavior remains unproved. No untested behavior supports acceptance.

## Exact partition/cell coverage

**[observed]** Local integrity checks passed for every one of the 15 UTF-8 query cells: all 11 dictionary partitions map to exact files, all scheduled finite terms are present, all rows select All fields with AND, no wildcard or prohibited SmallSat term occurs, and every query hash matches `translation-spec.json`. This is a local structural check, not source-semantic acceptance. See [`query-integrity.json`](query-integrity.json).

| Partition | Cell(s) | Current source validation |
|---|---|---|
| A1 | A1-C1 | **[observed]** explicit zero |
| A2 | A2-C1 | **[observed]** explicit zero |
| A3 | A3-C1 | **[observed]** explicit zero |
| B1 | B1-C1 | **[observed]** explicit zero |
| B2 | B2-C1 | **[observed]** explicit zero |
| BG1 | BG1-C1, BG1-C2 | **[observed]** one positive count-only cell; one explicit zero |
| BG2 | BG2-C1, BG2-C2, BG2-C3 | **[observed]** C1 explicit zero; C2 blocked before submission; **[untested]** C3 |
| BC1 | BC1-C1, BC1-C2 | **[untested]** after stop |
| BT2 | BT2-C1 | **[untested]** after stop |
| V1 | V1-C1 | **[untested]** after stop |
| O1 | O1-C1 | **[untested]** after stop |

**[observed]** BG2-C2 required a third visible UI row. After one additional row had been added, the visible **Add another term +** control was unavailable before the next row could be created. No query was submitted, `total=null`, the owned tab was closed, and all remaining source interaction stopped. This is an unresolved UI/control failure, not a demonstrated fixed arXiv row limit. See `E-UI-CONTROL-FAILURE`.

## Dates, versions, language, and report handling

- **[observed]** The rendered lower-bound diagnostic retained Date range from 2011-01-01, no upper bound, and the most-recent submission-date control. `P-001` has not supplied the common upper cutoff; no upper date was invented or tested. See `E-DATE`.
- **[inferred]** A final upper filter on Submission date (most recent) would miss a report submitted before the cutoff but revised after it. The final method must instead use unbounded discovery and complete local stable-base-ID/version-history/date handling, identify the earliest version containing a substantial completed report, and restrict later eligibility/extraction to versions available by the P-001 cutoff.
- **[observed]** One normal abstract-route diagnostic exposed a stable base-ID route, a submission-history container, a v1 date line, and a visible PDF affordance. No PDF was opened or downloaded. **[untested]** A multi-revision history and complete every-version/date capture were not observed.
- **[observed]** No Language control appeared in the visible Advanced Search control inventory. **[inferred]** No native English restriction is appropriate; full-report language remains a later screening determination.

## Pagination, identity, capture, and completeness

- **[observed]** A two-pass, two-page visible UI diagnostic with a 36-result probe reconciled exact source total = 36 unique stable base IDs = 36 rows in both passes, with identical ordered ID ledgers and ranges 1–25 and 26–36. Final-page Next controls were invisible and had no href. See `E-COMPLETENESS`.
- **[observed]** On one 25-row result page, every row exposed canonical abstract and PDF affordances; no Export or Citation control was observed. No record content was retained and no PDF was opened. See `E-CAPTURE`.
- **[inferred]** A future final cell must complete two full source passes under fixed controls, require total = unique base-ID ledger = range/page ledger, capture visible submission history for every base ID, retain raw material only in rights-controlled storage, and fail with `total=null` on changed total, short/stale page, duplicate/missing ID, missing history, control drift, source cap, or pass drift.

## Disposition and protocol impact

- **[observed]** The initial normal UI route was accessible; no login, CAPTCHA, challenge, credentials, cookies, session URL, or existing user tab was used. The later UI-control failure requires the `skip_for_now` recommendation and no retry in this pilot.
- **[observed]** An early local harness parsing defect submitted an empty title-field search. It retained no records, is quarantined in the ignored worklog, and was not used as A1 evidence. See `E-LOCAL-INVALID`.
- **[observed]** No protocol concept, Boolean relationship, source list, evidence-window rule, eligibility rule, task row, search log, dictionary, crosswalk, schema, final-event file, or commit changed.
- **[untested]** A focused human/supervisor follow-up must first reproduce the multi-row control sequence, then revalidate every blocked/untested cell, final date/version capture, source-wide caps/export behavior, and final two-pass completeness before any final event. `P-001`, `R-002`, preflight, and supervisor approval remain mandatory.
