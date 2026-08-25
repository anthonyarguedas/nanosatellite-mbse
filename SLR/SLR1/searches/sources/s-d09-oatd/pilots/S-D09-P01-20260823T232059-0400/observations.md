# OATD diagnostic observations — S-D09-P01-20260823T232059-0400

**Status:** blocked; diagnostic only. No screening, eligibility classification, candidate import, final event, full-text download, or retry occurred.

## Scope and stop rule

- **[observed]** This pilot reserved the source packet before any packet write. Its only successful OATD query was a deliberately non-candidate native-zero diagnostic through the normal basic GET route.
- **[observed]** A blank advanced-composer navigation displayed `Server Too Busy - Please slow down`; no total was accepted and no advanced retry occurred.
- **[observed]** A later custom aggregate-only basic-parser suite failed at browser-harness CDP IPC `Page.navigate` with `TimeoutError`. Its redirected stdout is zero bytes, so neither source progress nor a source total can be reconstructed. It is `null`, not zero. The suite was not retried.
- **[observed]** Static inspection then demonstrated a candidate-adapter no-clobber/strict-completeness safety defect. `code_issue=true`; the pilot stopped all further live OATD querying.

## Browser, power, and anchor preflight

- **[observed]** Pilot start: `2026-08-23T23:20:59-04:00`. Controller preflight had completed at the dedicated endpoint `http://127.0.0.1:9234` and profile `/Users/antho/agent-tools/.browser-profiles/oatd-pilot-9234`.
- **[observed]** Controller evidence recorded Chrome runtime `151.0.7922.174`, a passed runtime/on-disk version check, and one controller anchor `chrome://newtab/` (`C3EC0E94B554ED22BC3AAA41DE8EB358`). Owned probes first created a new blank page and closed only that page; the anchor was never navigated or closed.
- **[observed]** At `2026-08-23T23:20:50-04:00`, AC power was active and the controller's process-scoped `caffeinate -dims pi` had all four required sleep-related assertions. Evidence is summarized in [`environment-preflight.json`](environment-preflight.json).
- **[observed]** Postflight at `2026-08-23T23:42:19-04:00` passed the read-only launcher check using the exact dedicated endpoint/profile environment, retained Chrome `151.0.7922.174`, and retained the same `chrome://newtab/` anchor. AC power and the pilot's `caffeinate` assertions remained active; filtered `pmset` output contained no actual Sleep, Wake, or DarkWake event in the pilot window. See [`postflight-receipt.json`](postflight-receipt.json).

## Source boundary and source-owned documentation

- **[official_documentation]** OATD's rendered FAQ says it indexes more than 7.3 million ETDs, seeks to limit the index to freely available graduate-level records, harvests mostly through OAI-PMH from contributing repositories/consortia, and leaves full text at the originating host. It says it offers no bulk download or OAI-PMH metadata export.
- **[official_documentation]** The same FAQ says originating sites control record quality/availability and update timing, and distinguishes PQDT as a separate, commercial, institutionally restricted service. The home About section reports metadata from more than 1,100 organizations. URLs and concise rights-safe summaries are in [`official-source-documentation-receipt.json`](official-source-documentation-receipt.json).
- **[inferred]** OATD is the source-wide aggregation event required by the protocol, not a substitute for each linked repository and not PQDT. These source statements do not prove global ETD coverage, record currency, degree completion, metadata accuracy, or a resource's current full-text availability.

## Current interface observations

| ID | Basis | Observation | Result |
|---|---|---|---|
| I-001 | observed | First owned page to `https://oatd.org/` showed “Just a moment”. No access control was interacted with. | A later separately owned adapter page completed a basic native zero; no persistent challenge is claimed. |
| I-002 | observed | Home basic form was `GET /oatd/search` with `q` and hidden `form=basic`. | Current normal basic route observed. |
| I-003 | observed | Home advanced form exposed four rows: AND/OR/PHRASE/NOT; any field/title/author name/abstract/university-publisher/subjects-keywords/department-discipline; language/country/earliest/latest/sort/CC/page-size controls. | Current visible controls captured without record data in restricted `exec-002`. |
| I-004 | observed | Advanced default form action opened `/oatd/search-composer`, redirected to unbounded `q=*:*`, and displayed Server Too Busy. | `total=null`; advanced execution not retried. |
| I-005 | observed | Native zero query used exact normal basic GET state. | Query `oatdpilotzerotokenxqz20260823`; `total=0`, zero records, one page state, exact source result reconciliation; see restricted `exec-001`. |
| I-006 | observed | Custom aggregate parser suite attempted Boolean, precedence, phrase, punctuation, case, acronym, inflection, wildcard, proximity, length, and malformed-input diagnostics. | Browser CDP IPC timeout; stdout receipt zero bytes; progress and all totals unknown/null; see restricted `exec-003` failure receipt. |

## Controls and field/controlled-vocabulary status

- **[observed]** The advanced control values seen on the home page were Relevance (`relevanace`), Author, University, Date; 30/60/100 page sizes; any-language plus named language values; country values; blank earliest/latest inputs; and an unchecked `cc_only` checkbox.
- **[untested]** The meaning/precision of the date inputs; language reliability; country/CC/sort/page-size behavior in result pages; native basic/advanced field semantics; and source export are not established.
- **[observed]** “subjects/keywords” is a distinct visible selector.
- **[untested]** Record Details labels/values, known-record subjects, whether the selector is controlled indexing, scope notes, hierarchy, explosion, or a descriptor mapping were not observed.
- **[inferred]** No controlled-vocabulary supplement is available for this draft. Do not emulate one from the selector label.

## Parser, pair, record, and completeness status

- **[blocked]** No completed source result supports any claim about `AND`, `OR`, `NOT`, parenthesis precedence, quoted phrase semantics, punctuation/hyphen normalization, acronym boundaries, case, stemming, lemmatization, automatic expansion, wildcard behavior, source query length, or proximity.
- **[blocked]** No valid same-field proximity operator was observed. A draft record-level `(left AND right)` representation is explicitly marked final-use-prohibited in [`translation-spec.json`](../../translation-spec.json); it is not a same-field fallback.
- **[untested]** No minimally retained positive Record Details record, record identifier, resource/repository provenance, pagination transition, native export, duplicate behavior, identity absence behavior, or two-pass repeatability check exists.
- **[blocked]** No positive bounded prefix was imported or treated as complete. The only retained query had zero rows.

## Translation and adapter assessment

- **[observed]** Offline generation from `slr1-search-concepts/v4` created 12 exact UTF-8 draft cells: one each for A1, A2, A3, B1, B2, BG1, BG2, BC1 and four BT2 cells. The audit found zero missing finite terms and zero missing pair clauses. BT2's four 14-left-term cells have a documented algebraic OR union.
- **[blocked]** All cell syntax checks remain unsubmitted after I-006. Their source totals are `null`; query files remain draft and are not importable.
- **[observed]** Candidate adapter repository commit was independently verified as `3231ebddefcc3e7bc707b2a7d66fbe831d363286`; `search_oatd.py` SHA-256 is `c654b34750fa651407ab5d09baf452abec6167a625a8c1995b7e57aa4095b043`.
- **[observed]** `validate_output_paths` does not reject an existing output path, and `atomic_write_json` finishes with `os.replace`; the adapter can clobber an existing artifact. It also lacks count-only, strict two-pass/`--require-complete`, date/language/country/CC controls, and necessary Record Details fields. This is a demonstrated final-run safety defect: **`code_issue=true`**. See [`adapter-review.json`](adapter-review.json).

## Protocol impact and disposition

- **[protocol]** OATD remains a separate required source, with its existing PRISMA classification. No central protocol, dictionary, crosswalk, log, or task file was modified.
- **[inferred]** This evidence supports no semantic change. It documents incomplete source validation, OATD coverage limitations, and an adapter defect only.
- **[draft]** Recommended next action: a separately authorized code-fix subagent, then a new corrective pilot after controller review and human authorization. Do not run a final OATD event from this packet.
