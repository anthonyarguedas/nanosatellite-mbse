# OATD corrective diagnostic observations — S-D09-P02-20260824T105026-0400

**Status:** blocked; diagnostic only. No screening, eligibility classification, candidate import, final event, full-text download, direct advanced-form submission, Record Details traversal, or retry occurred.

## Scope and terminal stop

- **[observed]** P02 began after the controller's fresh-browser restart preflight. It independently verified the pinned external implementation commit `5ad2a3158b404cc1bafa3df473bf9755d9cd2eef`, clean implementation worktree, adapter version `2`, SHA-256 `9dacff622fb27f2b04c19c2fa91b86e86ef5c5e53b77d20718e3397b56fdd66d`, and 24 focused offline OATD tests before live work. See [`implementation/`](../../../../../../../.searches/s-d09-oatd-restricted/S-D09-P02-20260824T105026-0400/implementation/) in the restricted evidence location.
- **[observed]** Six serial repaired `--count-only` basic queries completed through the normal public rendered route. Each saved output has `results=[]`, `results_retrieved=0`, `detail_records_retrieved=0`, `status="count_only"`, `merge_eligible=false`, and a terminal OATD marker sidecar. These are aggregate diagnostics only.
- **[observed]** E-007 was the first strict `--require-complete` attempt. It was prospectively selected after the maximum three count-only selection probes produced 8, 8, and 85, not a safe 31–60 total. The source state immediately produced the repaired adapter's `OATDMetadataAccessError` (access challenge or Server Too Busy), with `total=null`, zero pages, zero records, and no prefix. No CSV or terminal marker was published.
- **[observed]** The access/busy result required the no-retry stop. No more OATD source request was made. In particular, P02 did not submit `NOT`, case, punctuation/hyphen, acronym, expansion, wildcard, proximity, malformed, advanced-field, control, partition-cell, or positive-detail diagnostics.

## Browser, power, and anchor

- **[observed]** P02 start evidence at `2026-08-24T10:51:20-04:00` records AC power with an internal battery charged to 100%, active `caffeinate -dims` assertions on behalf of this `pi` process, Chrome `151.0.7922.174`, a successful runtime/on-disk launcher equality check, and the controller anchor `DE53021723E8E6CED2311290D731B1A4` at `chrome://newtab/`.
- **[observed]** Postflight at `2026-08-24T11:04:01-04:00` preserved that exact anchor and Chrome version, passed the same read-only launcher check at `http://127.0.0.1:9234`, retained AC and all four relevant sleep assertions, and found no actual Sleep/Wake/DarkWake event in the pilot window. The postflight CDP list has no surviving OATD-owned page.
- **[observed]** P02 used only `http://127.0.0.1:9234` and did not navigate or close the anchor. The external adapter received explicit `--cdp-url http://127.0.0.1:9234` on every source execution.

## Basic parser/count matrix completed before the stop

| Execution | Exact diagnostic | Total | Observed conclusion |
|---|---|---:|---|
| E-001 | `CubeSat AND SysML` | 8 | Basic route, uppercase `AND`, exact query echo, fixed controls, and count-only/no-details behavior accepted for this narrow diagnostic. |
| E-002 | `(CubeSat OR CubeSats) AND SysML` | 8 | Uppercase `OR` within explicit parentheses was accepted. Equal totals do not prove identical record sets. |
| E-003 | `(CubeSat OR nanosatellite) AND SysML` | 8 | A second parenthesized expression was accepted. It was selection probe 2. |
| E-004 | `CubeSat OR (nanosatellite AND SysML)` | 1,332 | Parenthesized right-side grouping was accepted. |
| E-005 | `CubeSat OR nanosatellite AND SysML` | 2 | The unparenthesized contrast was accepted but non-equivalent to E-004. Keep explicit parentheses; general precedence remains unresolved. |
| E-006 | `CubeSat AND "systems engineering"` | 85 | Straight quotes were accepted. This is syntax evidence only, not proof of ordered-phrase semantics. It was selection probe 3. |
| E-007 | `CubeSat AND SysML`, strict two-pass with finite bounds | `null` | Adapter-detected access/busy state; no record/detail traversal or partial prefix; terminal stop. |

**[observed]** Every next distinct source query started at least 20 seconds after the preceding completed query: E-001 ended 10:58:21 and E-002 started 10:58:55; E-002 ended 10:58:56 and E-003 started 11:00:21; E-003 ended 11:00:22 and E-004 started 11:00:54; E-004 ended 11:00:57 and E-005 started 11:01:29; E-005 ended 11:01:30 and E-006 started 11:02:02; E-006 ended 11:02:06 and E-007 started 11:02:46 (all local EDT).

## Advanced route, pairs, terms, controls, and detail records

- **[official_documentation]** P01's source-owned FAQ/About evidence remains the current boundary context. P02 did not re-fetch it unnecessarily.
- **[blocked]** The blank advanced-composer route was not opened. No nonempty advanced title/abstract/subject/discipline diagnostic was submitted after E-007, so field syntax and semantics remain unresolved.
- **[blocked]** No valid unordered same-field `<=5`-intervening-token proximity operator, broader same-field construction, or local exact-pair route was demonstrated. All pair-bearing draft cells remain final-use-prohibited; record-level `(left AND right)` is not accepted.
- **[blocked]** No positive Record Details page was reached. Repository/publisher provenance, resource URL/format, Record ID, title/detail stability, abstract missingness, subject/keyword labels, degree metadata, and controlled-vocabulary behavior remain untested.
- **[blocked]** Visible year, language, country, CC, sort, and page-size controls were not submitted in P02. Retain the protocol's local date/language/degree/retrieval handling; P-001 remains unresolved.
- **[blocked]** No planned A1/A2/A3/B1/B2/BG1/BG2/BC1/BT2 cell was submitted after the stop. Their source totals remain `null`, not zero.

## Translation and repaired-adapter assessment

- **[observed]** The P02 offline regeneration is byte-for-byte identical to all 12 existing UTF-8 query files. It preserves all finite literals, 292 pair clauses, terminal LFs, and BT2's four-cell OR algebra. See [`translation-audit.json`](translation-audit.json). This is an offline rendering check, not source validation.
- **[observed]** E-001–E-006 establish repaired count-only behavior with no Record Details and marker-gated no-clobber publication for unique destinations. E-007 establishes fail-closed error accounting for an access/busy response: `total=null`, no results, and no marker or CSV.
- **[observed]** `code_issue=false` for P02's bounded implementation assessment. The focused offline tests passed, the marker/no-details/error behavior observed here matches the repaired design, and pre/postflight anchor evidence shows no surviving adapter page. A live strict two-pass traversal, collision race, CSV transaction, detail pacing, and source completeness proof remain **[untested]**, not assumed successful.

## Protocol impact and disposition

- **[protocol]** OATD remains one separate required indexed-online-resource event; its PRISMA classification, the nine normative partitions, degree-work eligibility, and local limit rules are unchanged.
- **[inferred]** No semantic or protocol change is supported. P02 supplies a conservative parser observation (explicit parentheses required) and an access/busy limitation only.
- **[inferred]** Recommend `repeat`, not acceptance, only if a controller and the review owner separately authorize a new narrowly scoped pilot after considering the access/busy state. P02 cannot self-accept, start P03, or reissue E-007.
