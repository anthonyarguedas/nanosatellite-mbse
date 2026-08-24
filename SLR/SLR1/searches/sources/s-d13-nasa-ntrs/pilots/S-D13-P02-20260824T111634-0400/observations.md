# NTRS corrective diagnostic observations — S-D13-P02-20260824T111634-0400

## Status and authorization

**Status: blocked at the mandatory early gate.** This is exactly one diagnostic-only corrective pilot. `screening_performed=false`, `candidate_import_permitted=false`, no candidates were screened or imported, and no full response body was retained. Claim bases are explicitly labelled **[observed]**, **[official_documentation]**, **[inferred]**, or **[untested]**.

**[observed]** P02 was allocated at `2026-08-24T11:16:34-04:00` before any P02 source request. The preflight records the repository/protocol commit, pre-existing dirty paths, immutable root/P01 hash snapshots, pinned adapter commit and hashes, and the human authorization without calling it an acceptance: [preflight](preflight.json).

**[observed]** The review owner authorized this corrective P02 after the separately committed adapter correction `e720192855f8b5356d92fff23caeb6b8f66bbaf4` and required retention of the normative exact paired-term semantics unless live losslessness evidence supports an allowed fallback. That authorization did **not** accept P02 or promote any draft source packet.

**[observed]** Browser preflight is not applicable. No browser, Chrome process, credentials, login, cookie, session value, registered route, PubSpace route, full text, or private endpoint was used.

## Mandatory health and minimal-search gate

| Operation | Result | Total / records | Evidence |
|---|---|---:|---|
| `GET /api/health` | **[observed]** HTTP 200 JSON `{"status":"ok"}` | not a search total / 0 | [health receipt](health-receipt.json) |
| Minimal anonymous `POST /api/citations/search` | **[observed]** one 45-second `ReadTimeout`; no HTTP response or JSON envelope | `null` / 0 | [minimal search receipt](minimal-search-envelope-receipt.json) |

**[observed]** The one minimal POST sent exactly `q=nanosatellite`, `page.from=0`, `page.size=1`, `highlight=false`, and `published={gte:2011-01-01,lte:2026-08-24}`. Its exact UTF-8 query is [Q01](queries/Q01-minimal-nanosatellite.txt). The upper bound is explicitly the local P02 execution-date **diagnostic** bound, not P-001 or a final common cutoff.

**[observed]** Health did not prove search success. The failed POST had no `stats`, `stats.total`, estimate/exactness signal, results list/type, aggregation, record ID, or query/control echo/rewrite to inspect. It is a failure with `source_reported_total=null`, not a zero.

**[observed]** The pilot stopped all further live NTRS/API/static-client requests immediately after this unreconciled early-gate timeout. There was no transport retry, fallback query, adapter live run, P03, or source-request parallelism.

## Scope that is consequently blocked

**[untested]** P02 cannot newly prove the public full-NTRS versus registered/PubSpace boundary, current search envelope, q field scope, advanced properties, aggregations, controlled-vocabulary status, exact date application/precision, language metadata/filter reliability, default ordering, pagination/offset/cap behavior, public raw-ID stability, two-page traversal, strict two-pass completeness, native zero, or source export behavior.

**[untested]** The required q contrasts—OR, AND, precedence, parentheses, ordered phrases, case, punctuation/hyphen/space, acronym boundaries, wildcard, stemming/lemmatization/automatic expansion, escaping, echo/rewrite, and practical length—were not sent after the gate. Therefore P02 makes no negative semantic claim and does not infer an equivalence from a count.

**[untested]** No live descriptor, keyword, subject category, hierarchy, scope note, narrower term, or mapped controlled-vocabulary supplement could be inspected. No generic `systems engineering` term was substituted for MBSE.

**[untested]** Native unordered same-field <=5-intervening-token proximity could not be tested. The human-approved pair semantics remain unchanged; no broad all-record co-occurrence or other fallback was accepted.

**[observed]** All nine normative partitions were retained in their existing immutable root draft as an *offline integrity* subject only. The [offline partition audit](offline-partition-audit.json) verifies the current dictionary/spec/literal/Boolean/hash mapping for A1, A2, A3, B1, B2, BG1, BG2, BC1, and BT2 and records `total=null`/not sent for each P02 cell. It does not validate parser semantics or authorize a final translation.

## Adapter and failure behavior

**[observed]** The exact corrected adapter commit was used for local focused tests only. Its `search_ntrs.py`, `_output_utils.py`, and `_prisma_search_run.py` hashes are recorded without a local worktree path in [adapter hashes](pinned-adapter-file-sha256.json). The focused mocked/offline suite passed 34 tests and left the adapter worktree clean: [offline-test receipt](pinned-adapter-offline-tests.json).

**[observed]** Those focused tests exercise the committed exact-date control, NTRS-as-database descriptor, no guessed explicit sort payload, strict two-pass ordered raw-ID reconciliation, explicit strict zero, insufficient limit/page controls, changed total/order, missing/duplicate/short-ID/page failures, bounded-not-report-ready behavior, and record-free strict failure output. They are implementation evidence only, not current source behavior.

**[observed]** `code_issue=unresolved`. The prior reported adapter defects are covered by the cited correction and its focused offline tests; P02 demonstrated no new adapter defect. However, the direct minimal source request timed out before the live envelope could test the corrected adapter's exact-total assumption, date transport, raw IDs, or strict traversal. It would be unsupported to label the adapter `false` (fully cleared) from this source failure alone.

**[inferred]** For a later authorized pilot, HTTP/redirect/rate-limit/query/control/total/page/short/stale/parse/ID/duplicate/pass/order/export/completeness failures must remain `total=null` with no prefix import. A reproducible native JSON zero is still required before `total=0` is valid. P02 observed no native zero.

## Boundary, retention, and rate

**[observed]** The P02 request count is **2**: one health GET and one search POST, executed serially with a deliberate two-second pause. No response header other than content type was retained; no cookie/session/header value, raw response body, private route, or candidate corpus is stored.

**[observed]** P02 wrote only under its own directory in the assigned NTRS source packet. It did not edit the source root guideline, translation spec, root queries, P01, shared protocol, dictionaries, crosswalk, schemas, logs, scripts, final events, Git index, adapter checkout, or commits.

**[observed]** No `draft-source-packet/` proposal is created. The early-gate failure provides no supported reusable replacement for the immutable blocked root packet; copying or self-promoting its unvalidated drafts would falsely imply validation.

## P01 relationship and next decision

**[observed]** P01 remains immutable. Its P02 preflight hash snapshot is [P01 hashes](pre-existing-p01-sha256.txt); its earlier blocked source/service evidence remains separate and is not overwritten.

**[inferred]** Recommended smallest next action: a controller should record this P02 source-service failure, verify a successful public anonymous search independently **before** seeking fresh human authorization for any later pilot. Do not patch the adapter based on this P02 timeout, do not retry within P02, and do not create P03 automatically.

**[inferred]** No protocol semantic change is proposed. The source list, date policy, nine partitions, literal dictionary, S-C01 exclusion, and exact pair rule remain unchanged. The impact is an unresolved source-access/availability limitation and deferred validation, not an allowed semantic weakening.
