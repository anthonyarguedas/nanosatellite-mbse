# OATD corrective diagnostic observations — S-D09-P03-20260824T130849-0400

**Status:** blocked; diagnostic only. No screening, eligibility classification, candidate import, final event, full-text download, planned partition-cell submission, Record Details traversal, strict traversal, CSV publication, or retry occurred.

## Authorization and stop rule

- **[official_documentation]** The review owner authorized exactly this P03 at 2026-08-24T13:07:07-04:00 under the staged scope in [`../../human-review.md`](../../human-review.md) and [`../../controller-review-p02.md`](../../controller-review-p02.md). P01 and P02 remain immutable and blocked.
- **[observed]** Before live work, P03 independently verified external candidate commit `adbf1a06f409aa4c00f739812f9fa0a5ccbe518a`, clean worktree, adapter version `3`, SHA-256 `2e4a403725aea006f7d41798846cc3be7317aa0ff1946eed4fd2243ada039fbc`, and one focused offline run: 39 passed tests plus 28 subtests.
- **[observed]** The mandatory first health gate succeeded. The next, permitted pair/field-first advanced diagnostic ended in a terminal unreconciled navigation timeout. Per the authorization, no later source execution was submitted.

## Executions and pacing

| Execution | Started (EDT) | Exact operation/query | Mode | Total | Records retained | Busy recovery | Outcome |
|---|---|---|---|---:|---:|---:|---|
| E-001 | 2026-08-24T13:15:51-04:00 | `CubeSat AND SysML` | Candidate v3 `--count-only`; `limit=1`, `max-pages=1` | 8 | 0 | 0 | **success** — exact echo, fixed normal basic controls, 8 first-page rows validated, marker published. |
| E-002 | 2026-08-24T13:20:00-04:00 | Normal home advanced form, nonblank `title` field attempted with `CubeSat AND SysML` | One direct local Playwright owned-page aggregate/form diagnostic | `null` | 0 | n/a | **failed/terminal** — the source form and field/control inventory were observed, but post-submit navigation timed out without a reconcilable result state. The submission/progress cannot be reconstructed and was not reissued. |

**[observed]** E-002 started 246 seconds after E-001 completed at 2026-08-24T13:15:54-04:00, exceeding the required 60-second inter-query interval. Neither execution opened Record Details or full text. E-001's `page_delay_seconds=30` and `detail_delay_seconds=10` settings were recorded even though count-only mode did not paginate or open details.

## Basic health gate and busy policy

- **[observed]** E-001 used only the normal rendered OATD basic GET route through the pinned adapter and explicit `--cdp-url http://127.0.0.1:9234`. It returned exact total 8; `results=[]`, `results_retrieved=0`, `detail_records_retrieved=0`, `count_only=true`, and `merge_eligible=false`.
- **[observed]** E-001 reconfirmed relevance (`relevanace`), fixed page size 30, blank language/country/earliest/latest, and unchecked Creative Commons control. Its terminal marker binds the exact JSON bytes. It is diagnostic and non-report-ready.
- **[untested]** Version 3's finite busy recovery was configured at the authorized defaults (two extra-request slots; 30 then 60 seconds) but was not exercised: E-001 recorded `busy_retries_performed=0`; E-002 was a separate direct advanced-form diagnostic, not a candidate-adapter busy event.

## Advanced fields, pair semantics, controls, and completeness

- **[observed]** Before E-002's attempted native submit, the normal home advanced form exposed `any field`, `title`, `author name`, `abstract`, `university/publisher`, `subjects/keywords`, and `department/discipline`; it also exposed language, country, earliest/latest, sort, page-size, and Creative Commons controls.
- **[blocked]** E-002 did not yield a source result, query echo, total, or result-page control state after the nonblank title attempt. It therefore does **not** validate title semantics, field/query mapping, advanced controls, an indexed-term field, or controlled vocabulary.
- **[blocked]** No valid unordered same-field `<=5`-intervening-token operator or recall-preserving broader same-field construction was demonstrated. No pair-bearing cell is eligible for final use; BG1, BG2, BC1, and BT2 remain explicitly final-use-prohibited.
- **[blocked]** `NOT`, case, punctuation/hyphen normalization, acronym token boundaries, expansion/stemming, wildcard, malformed/proximity, planned length, positive Record Details, stable identity, resource provenance, pagination, strict two-pass completeness, CSV, and all 12 planned cells remain unresolved.

## Browser, power, and owned-page boundary

- **[observed]** At P03 start, controller and operator preflight evidence showed AC power, active process-scoped `caffeinate -dims` assertions, healthy local endpoint, matching runtime/on-disk Chrome `151.0.7922.174`, no actual Sleep/Wake/DarkWake row since the browser launch, and both protected anchors: `25DDEE93F8D83818D177C8DB2F365647` and `DE53021723E8E6CED2311290D731B1A4`, each at `chrome://newtab/`.
- **[observed]** E-002's direct probe reported its owned page closed, but the first postflight CDP list instead showed one OATD page created after preflight and distinct from both anchors. That page only (`04B5688369EE9A6E3FEAB7837ABC2CD2`) was closed through local CDP; the final CDP list verified both anchors intact and no remaining OATD page.
- **[observed]** Final postflight again passed the exact launcher check, retained AC power and active sleep assertions, retained Chrome `151.0.7922.174`, retained the external implementation commit/hash and clean worktree, and showed no actual Sleep/Wake/DarkWake event during the pilot window.

## Query integrity, method impact, and disposition

- **[observed]** P03 did not change any query file. The offline audit reconfirmed all 12 terminal-LF, character-count, and SHA-256 values against P02's dictionary rendering; it preserves the 292 literal pair clauses and BT2's four-cell algebra only. See [`translation-audit.json`](translation-audit.json).
- **[protocol]** No protocol semantic change is proposed. OATD remains a separate indexed-online-resource event; local handling of date, language, degree completion, retrieval, and source limitations remains unchanged.
- **[inferred]** Candidate-adapter `code_issue` is **unresolved**. E-001 supports the version-3 basic count-only/marker path, but E-002's timeout came from a separate permitted direct diagnostic and contains no reconcilable post-submit source state; it neither proves nor rules out a candidate-adapter defect for advanced or strict behavior.
- **[inferred]** Recommendation: `revise`. Preserve this blocked diagnostic and obtain controller/human review before any later pilot. The smallest next action is a controller review of E-002's terminal advanced-form timeout and cleanup discrepancy; do not directly retry it or start P04.

See [`evidence-index.json`](evidence-index.json) for rights-safe evidence paths and checksums.
