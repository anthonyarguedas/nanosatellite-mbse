# S-D04-P01 observations

**Status:** blocked. **Scope:** diagnostic only; no screening, eligibility decision, candidate import, final event, or final-events edit.

## Execution window and safety boundary

- **[observed]** Controller preflight reported a dedicated `http://127.0.0.1:9235` Engineering Village browser, matched Chrome `151.0.7922.174`, AC power, a controller-created new-tab anchor, and process-scoped `caffeinate -dims`. Safe summary/checksums: [`controller-preflight-summary.json`](controller-preflight-summary.json).
- **[observed]** The immediate pre-live and postflight launcher checks both reported a healthy dedicated endpoint and a passing Chrome-app version check: [`launcher-read-only-check-prelive.txt`](launcher-read-only-check-prelive.txt), [`launcher-read-only-check-postflight.txt`](launcher-read-only-check-postflight.txt).
- **[observed]** The live source window was 2026-08-24T12:36:51-04:00 to 2026-08-24T12:37:32-04:00. The postflight receipt reports AC power, current-runner caffeinate process/assertion observation, and zero Sleep/Wake log entries in that bounded window. It does **not** claim protection from manual or clamshell sleep. [`browser-postflight.json`](browser-postflight.json)
- **[observed]** The controller anchor target remained present at postflight, but its URL class was `engineering_village_expert_search` rather than the preflight new-tab class. No raw target ID, query string, session URL, cookie, or page text is retained. No attempt was made to navigate, restore, or close it after detection. This is an operational continuity failure requiring review.

## E01 — paired adapter route diagnostic

- **Started/ended:** 2026-08-24T12:36:51-04:00 / 2026-08-24T12:36:54-04:00.
- **Intent:** Invoke the pinned current Engineering Village implementation in deliberate paired Compendex+Inspec Expert mode, with normal same-origin RIS only and strict two-pass completeness, using a title-phrase probe. The exact UTF-8 string is [`queries/E01-paired-known-title.expert.txt`](queries/E01-paired-known-title.expert.txt).
- **[observed]** Exit status was 1. The adapter reported: `The adapter-created page left the authorized Engineering Village search host; refusing to continue.` It did not emit a result JSON/CSV, source-reported total, record, row provenance, identifier, or RIS body. [`E01-paired-known-title.status.txt`](E01-paired-known-title.status.txt), [`E01-paired-known-title.stderr.txt`](E01-paired-known-title.stderr.txt)
- **Accounting:** paired total = `null`; Compendex total = `null`; Inspec total = `null`; records retrieved = `0`. This was neither an explicit zero nor a retained partial prefix.
- **[observed]** Because the safe adapter error deliberately omits the final off-host/non-search URL, this result does not establish whether the cause was a native redirect/access boundary or an adapter-owned-page lifecycle issue.

## E02 — non-query route inspection

- **Started/ended:** 2026-08-24T12:37:28-04:00 / 2026-08-24T12:37:32-04:00.
- **[observed]** A normal route inspection reached the public Expert Search title. It did not submit a query, inspect source controls, read result content, or retain source metadata. [`E02-direct-route-inspection.stdout.txt`](E02-direct-route-inspection.stdout.txt)
- **[observed]** The action did not preserve the controller anchor's new-tab URL class. Following detection, all further Engineering Village interaction stopped. This title-only route observation cannot reconcile E01 or prove result access.

## Requirement ledger

| Requirement | Status | Basis / evidence |
|---|---|---|
| Intentional paired Compendex+Inspec selection, row provenance, and separate counts | blocked | E01 stopped before a reconciled page; all totals are null. |
| Current Expert field(s), syntax, phrases, punctuation, precedence, token boundaries, wildcard, stemming/expansion, proximity, length, syntax failure | untested | No parser-confirmed source result page. |
| A1, A2, A3, B1, B2, BG1, BG2, BC1, BT2 literal/Boolean draft completeness | verified offline only | [`translation-literal-audit.json`](translation-literal-audit.json): all nine present, all required literals present, no candidate term added. |
| Source execution of the nine cells | blocked | E01 terminal discrepancy; no cell submitted. |
| Date, language, prohibited limits, sort, source deduplication | untested | No reconciled controls/result page. |
| Separate Compendex and Inspec thesaurus/indexed-term mapping | untested | No thesaurus/indexed-term interface inspected. |
| Pagination, page size, RIS/export, cap, stable IDs, missing IDs, duplicates, two-pass completeness | untested | No result/export reached. |
| Explicit native zero | untested | E01 is an error, never a zero. |
| S-C01 baseline/families/audit | wholly unstarted | [`candidate-stage-status.json`](candidate-stage-status.json). |
| Screening/import prohibition | verified | No records captured; manifest flags are diagnostic-only/false. |

## Translation and terminology disposition

- **[observed]** The root [`translation-spec.json`](../../translation-spec.json) and nine root query files are exact UTF-8 **drafts** regenerated from the current dictionary. Literal preservation and candidate absence were checked offline.
- **[inferred]** Quoted literals and parenthesized Boolean grouping are a prospective Expert Search rendering, not live syntax/field validation.
- **[inferred]** BG1/BG2/BC1/BT2 use a broader co-occurrence fallback rather than accepted proximity. No semantic change is proposed and no pair literal is dropped.
- **[observed]** S-C01 did not start, so no known/contrast register was frozen locally and no Scopus judgment was used as Engineering Village evidence. [`candidate-stage-status.json`](candidate-stage-status.json)

## Adapter and rights assessment

- **[observed]** The adapter repository commit and file hashes were pinned before live work; 19 focused offline adapter tests passed. [`adapter-provenance-preflight.txt`](adapter-provenance-preflight.txt), [`focused-adapter-tests.stdout.txt`](focused-adapter-tests.stdout.txt)
- **[observed]** `code_issue=unresolved`: live source-route discrepancy exists, but a defect is not demonstrated and a clean source/access explanation is not demonstrated. No code was patched and no second source query was attempted. [`adapter-assessment.json`](adapter-assessment.json)
- **[observed]** No restricted capture exists. The designated restricted directory contains zero pilot captures because E01 failed before a result/export; the public packet retains only a zero-file ledger. [`restricted-capture-ledger.json`](restricted-capture-ledger.json)

## Disposition

**[inferred]** Do not accept this guideline or run a final Engineering Village event. First obtain controller/human review of the anchor-continuity incident and the adapter/source-boundary ambiguity. The smallest subsequent action is one separately authorized fresh-preflight paired-route diagnostic that records safe final URL class/control presence only, then stops on any discrepancy before query/export.
