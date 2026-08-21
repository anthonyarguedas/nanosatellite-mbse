# S-D13 NTRS diagnostic pilot observations

- **Pilot ID:** `S-D13-P01-20260821T034216+0000`
- **Task/source:** `S-D13` / NASA Technical Reports Server (NTRS)
- **Protocol commit:** `7d564870a36d049716b66c9f9770554ecb04e414`
- **Operator model:** `openai-codex/gpt-5.6-terra`
- **Evidence index:** [`evidence-index.json`](evidence-index.json)

> **Claim labels:** **[observed]**, **[official_documentation]**, **[inferred]**, and **[untested]**. This packet is diagnostic only.

## Scope guard and disposition

- **[observed]** Every machine-readable pilot summary declares `diagnostic_only=true`, `screening_performed=false`, and `candidate_import_permitted=false`; no record was screened, judged for relevance, imported, or treated as a candidate. See `E-07`, `E-08`, and `E-12`.
- **[inferred]** Recommendation: `revise`, not accept. The source-native method is drafted and evidence-backed, but P-001 has not supplied the common cutoff and several source-wide limits remain untested.
- **[observed]** The prior 2026-08-20 interface note is retained as `E-00` only; its syntax claims were independently retested.

## Boundary, route, fields, and types

- **[official_documentation]** The public landing page distinguishes the public repository from authenticated NTRS Registered content and describes the public repository as broad NASA STI, not only one report type. See `E-02`.
- **[observed]** Anonymous `POST https://ntrs.nasa.gov/api/citations/search` returned `stats`, `results`, and aggregations with `stats.estimate=false`; no API key or authentication was used. See `E-03` and `E-04`.
- **[observed]** The unfiltered default-scope probe returned multiple current index buckets without an `index` restriction. See `E-06`.
- **[inferred]** The draft source boundary is the default anonymous public `citations` scope with no index/type/access restriction; NTRS Registered and the separately surfaced `/pubspace/search` route are not part of this method.
- **[official_documentation]** NASA describes global search across metadata and document full text and documents Title, Author, Organization, Publication Date, Date Acquired, Type, Center, Subject Category, Report Numbers, Funding Numbers, and Keyword filters. See `E-01`.
- **[observed]** Returned search/detail metadata includes citation `id`, title, abstract, author affiliations, date arrays, identifiers, downloads, distribution, dissemination, STI type, and related records; the bounded probe observed multiple STI types. See `E-04`, `E-10`, and `E-13`.

## Syntax and transport observations

| Topic | Bounded observation | Classification/evidence |
|---|---|---|
| AND | `nanosatellite+CubeSat` and `nanosatellite CubeSat` each returned 55. | **[official_documentation] [observed]** `E-01`, `E-07` |
| OR | `nanosatellite|CubeSat` returned 1,230. | **[official_documentation] [observed]** `E-01`, `E-07` |
| NOT | `nanosatellite+-CubeSat` returned 78 versus 133 for the base probe. | **[official_documentation] [observed]** `E-01`, `E-07` |
| Phrase | `"CubeSat model"` returned 2 versus 98 for `CubeSat+model`. | **[official_documentation] [observed]** `E-01`, `E-07` |
| Grouping | `(CubeSat|nanosatellite)+MBSE` returned 5; `CubeSat|(nanosatellite+MBSE)` returned 1,152. | **[official_documentation] [observed]** `E-01`, `E-07` |
| Malformed grouping | An unmatched opening parenthesis returned HTTP 200 and total 1,230. | **[observed]** `E-17`; local query structure/hash preflight is required. |
| Hyphens/punctuation | Quoted hyphenated and spaced phrases were accepted; quoted report-number forms with/without escaped hyphens both returned 2. | **[official_documentation] [observed]** `E-01`, `E-07` |
| Literal escaping | NASA documents backslash escaping; broader literal-escape semantics were not corpus-proven. | **[official_documentation] [untested]** `E-01`, `E-07` |
| Case/acronyms | Controlled `CubeSat`/`cubesat`, `MBSE`/`mbse`, and `EPS`/`eps` totals matched. | **[observed]** `E-07` |
| Morphology | Controlled `battery` and `batteries` totals differed (8 versus 2). | **[observed]** `E-07`; no expansion is relied on. |
| Wildcard | `nanosat*` was accepted, but finite P totalled 1,587 versus 1,590 with the substitution. | **[official_documentation] [observed]** `E-01`, `E-07`; wildcard is unsafe and excluded. |
| POST/GET transport | POST JSON was successful for all current cells; URL-encoded GET returned a total but did not honor the diagnostic JSON-shaped page control. | **[observed]** `E-05`, `E-07`; final route is POST JSON. |
| Length | Current largest cell was 1,021 q characters/1,200 request bytes and succeeded; 2,068 synthetic q characters succeeded; 8,212 returned HTTP 504 HTML. | **[observed]** `E-07`, `E-17`; no fixed limit is claimed. |

## Translation validation

- **[observed]** `translation-spec.json` defines one UTF-8 query cell for every required partition; the integrity check found valid UTF-8, no BOM, matching SHA-256 values, no omitted serialized protocol terms, no wildcard, and no prohibited SmallSat term. File hashes include one terminal LF; diagnostics removed exactly that LF before setting `q` in POST JSON. See [`translation-integrity.json`](translation-integrity.json).
- **[inferred]** Pair rules are represented by parenthesized same-record Boolean conjunctions, not by a source-proximity assertion.
- **[inferred]** If a later fixed limit requires cells, every cell must complete independently and the final stable-ID union must retain cell provenance; a failed cell makes the partition `total=null`.

## All-partition bounded diagnostics

**[observed]** The following used the exact query file, POST JSON, `published.gte=2011-01-01`, a **diagnostic-only** `published.lte=2100-12-31` sentinel, explicit `published asc`, and no screening/import. The sentinel is not the P-001 cutoff. See [`partition-matrix.json`](partition-matrix.json) / `E-12`.

| Partition | Cell | HTTP | Source total | Results retrieved | Diagnostic status |
|---|---:|---:|---:|---:|---|
| A1 | A1-C1 | 200 | 0 | 0 | explicit_zero |
| A2 | A2-C1 | 200 | 1 | 1 | success |
| A3 | A3-C1 | 200 | 0 | 0 | explicit_zero |
| B1 | B1-C1 | 200 | 5 | 1 | success |
| B2 | B2-C1 | 200 | 3 | 0 | success count check |
| BG1 | BG1-C1 | 200 | 0 | 0 | explicit_zero |
| BG2 | BG2-C1 | 200 | 3 | 0 | success count check |
| BC1 | BC1-C1 | 200 | 0 | 0 | explicit_zero |
| BT2 | BT2-C1 | 200 | 0 | 0 | explicit_zero |
| V1 | V1-C1 | 200 | 0 | 0 | explicit_zero |
| O1 | O1-C1 | 200 | 0 | 0 | explicit_zero |

## Date, language, fields, and ordering

- **[observed]** `published` POST controls accepted the 2011-to-future-sentinel range (133 to 80 in the controlled probe), accepted a same-day range returning 1, and rejected malformed `gte` with HTTP 400. See `E-07` and `E-17`.
- **[untested]** The exact final upper date cannot be tested until P-001 sets the common cutoff; `2100-12-31` is only a future-bound transport/date sentinel.
- **[observed]** The English POST property left the controlled total at 133, and a sampled detail object had no `language` property. See `E-14`.
- **[inferred]** The final discovery event must apply no language filter and must defer language determination to the protocol's later screening process.
- **[observed]** A POST title property changed the controlled total from 133 to 55, while displayed/lowercase title values had the same total. See `E-14`.
- **[inferred]** No title/abstract/other field filter is needed or adopted for the direct translations; only the validated publication-date payload control is used.
- **[official_documentation] [observed]** NASA documents Best Match as default and published-date sorting; explicit `sort:{field:"published",order:"asc"}` produced repeatable IDs in the bounded test. See `E-01`, `E-08`, `E-11`.

## Pagination, identity, export, and completeness

- **[official_documentation] [observed]** NASA documents 25/50/100 UI page choices, and POST size 100 returned all five records in the small diagnostic. See `E-01`, `E-11`.
- **[observed]** Offset pages 0/2/4 returned 2/2/1 IDs under a stable source total of 5; all sampled IDs were nonempty and unique. See `E-08`, `E-09`.
- **[observed]** The same five ordered IDs recurred in a second full pass with `published asc`; each pass reconciled to total 5. See `E-08`.
- **[observed]** Search, detail, and JSON export exposed matching citation IDs; export returned five unique IDs despite a submitted page size of two. See `E-13`.
- **[inferred]** A future final event must use paged search responses for two complete passes, not export as the completeness channel. It must require unchanged `stats.total`/`estimate:false`, exact page counts, unique nonempty IDs, exact pass-order equality, and total/row reconciliation.
- **[untested]** A source-wide API/export cap and source-wide ordering stability were not established; a cap indicator, short page, changed total, duplicate/missing ID, export mismatch, or pass drift must force `total=null` and no partial import.

## Required failure/zero rule

- **[observed]** Valid HTTP 200 `total:0`, `estimate:false`, and `results:[]` occurred for several full translation diagnostics. See `E-12`.
- **[inferred]** Only that complete shape is an explicit zero. Access, HTTP, timeout, non-JSON, invalid controls, missing/estimated total, parse, page, ID, duplicate, export, or two-pass failure must be recorded as `total:null`; no prefix may be imported.

## Unresolved items for human review

- **[untested]** Set P-001's exact common cutoff and repeat an exact-date preflight before a final event.
- **[untested]** Recheck current public scope, response envelope, page cap, export cap, and order immediately before R-002.
- **[inferred]** Review and accept/reject the draft guideline only after the above checks; this subagent did not accept the pilot or modify protocol semantics.
