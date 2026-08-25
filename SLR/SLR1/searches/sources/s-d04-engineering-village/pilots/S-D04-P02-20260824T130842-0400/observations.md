# S-D04-P02 observations

**Status:** blocked. **Scope:** corrective diagnostic only; no screening, eligibility coding, candidate import, final event, query-family work, export, thesaurus work, or `S-C01` work occurred.

## Scope and preflight

- **[observed]** The controller-authorized P02 browser was the dedicated loopback endpoint on port 9237. The immediate read-only launcher recheck passed its runtime/on-disk version and page-target health checks. [`launcher-read-only-check-prelive-recheck.txt`](launcher-read-only-check-prelive-recheck.txt)
- **[observed]** The controller's caffeinate receipt was inspected. The immediate recheck observed AC power, the required system-sleep assertion, and the current P02 runner's `caffeinate` process. [`prelive-safety-recheck.json`](prelive-safety-recheck.json)
- **[observed]** An earlier pre-live shell check stopped before G01 because its `grep -q`/`pipefail` construction yielded a conservative false assertion result. It performed no browser/source action. The succeeding recheck reads complete command output before matching and is the pre-live decision record. [`prelive-safety.json`](prelive-safety.json), [`prelive-safety-recheck.json`](prelive-safety-recheck.json)
- **[observed]** The current Engineering Village adapter and wrappers were pinned before source work, and their postflight hashes were unchanged. [`adapter-provenance-preflight.txt`](adapter-provenance-preflight.txt), [`adapter-provenance-postflight.txt`](adapter-provenance-postflight.txt)

## G01 — one owned-page non-query route probe

- **[observed]** G01 confirmed one browser context, one private controller new-tab anchor, a distinct `context.new_page()` target, and one normal route navigation on that owned page. The anchor was never navigated by the script.
- **[observed]** The navigation response status was 200. The script then failed at its required safe post-navigation projection; it retained neither page text/HTML/screenshot nor an inferred route/control/access state. The gate is therefore blocked, not healthy. [`g01-safe-receipt.json`](g01-safe-receipt.json)
- **[observed]** The owned page was closed in `finally`. The original anchor again was the sole page, matched the private input in memory, and remained in the new-tab URL class. [`g01-safe-receipt.json`](g01-safe-receipt.json)
- **[inferred]** A response status alone cannot establish Expert controls, query-field availability, access state, or source availability. No such conclusion is claimed.

## G02 decision and accounting

- **[observed]** G02 was not run: its fixed condition was a healthy G01, which was not met. The combined current adapter was invoked zero times. No title-phrase query, source query, record, source total, database-provenance arithmetic, export, or partial prefix exists. [`g02-safe-receipt.json`](g02-safe-receipt.json)
- **[observed]** Accounting is failure/null accounting: paired total = `null`; Compendex total = `null`; Inspec total = `null`; records retrieved = `0`. This is not an explicit zero. [`g02-safe-receipt.json`](g02-safe-receipt.json), [`restricted-capture-ledger.json`](restricted-capture-ledger.json)
- **[observed]** The ignored restricted root has zero source artifacts. The public packet contains only the zero-capture inventory checksum and safe metadata. [`restricted-capture-ledger.json`](restricted-capture-ledger.json)

## Postflight and adapter assessment

- **[observed]** The postflight launcher health check passed. A read-only Playwright inspection verified the same sole private controller anchor and new-tab class, without retaining a raw target ID, URL, title, or page content. [`launcher-read-only-check-postflight.txt`](launcher-read-only-check-postflight.txt), [`browser-postflight.json`](browser-postflight.json)
- **[observed]** AC power and the P02 `caffeinate` assertion were present at postflight. Timestamp-bounded `pmset` and `loginwindow` checks found zero Sleep/Wake markers during the G01 window. [`system-postflight-recheck.json`](system-postflight-recheck.json)
- **[observed]** `code_issue=unresolved` for the Engineering Village adapter. With no permitted G02 invocation, P02 cannot classify P01 E01 as reproduced or non-reproduced. The G01 safe-inspection failure does not directly demonstrate an adapter defect or source/access failure. [`adapter-assessment.json`](adapter-assessment.json)
- **[observed]** The final validation pass confirmed Draft 2020-12 format validation, JSON parsing, evidence checksums, null/zero accounting, ignored restricted storage, anchor continuity, no raw target/session leakage, unchanged Part 2 context, unchanged tracked-diff set, and untouched final-events. Earlier validator receipts that reported a leakage failure were detector false positives from their own literal patterns/local CDP-session variable, not retained source data; the final receipt uses the corrected narrow detector. [`validation-receipt-final6.json`](validation-receipt-final6.json)

## Untested and disposition

The paired source controls and their checked states, source boundary/access state, parser/syntax behavior, title/phrase/token/stemming/proximity behavior, A1–BT2, date/language behavior, thesauri/indexed terms, row provenance, separate database totals, pagination, export, stable identity, completeness, explicit zero, and `S-C01` remain untested. No source guideline or P01 outcome is accepted, and no protocol semantic change is proposed.

**[inferred]** The smallest next action is controller/human review of this blocked P02. Any further technical diagnosis must have a new immutable, explicitly authorized scope; this pilot must not retry or proceed to G02.
