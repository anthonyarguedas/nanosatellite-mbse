# S-D01 Scopus P08 patched-adapter stability continuation

- **Pilot ID:** `S-D01-P08-20260822T142211-0400`
- **Status:** `partial` diagnostic pilot; not accepted and not report-ready.
- **Execution window:** 2026-08-22T14:23:56-0400 to 2026-08-22T14:39:26-0400.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** No screening, candidate import, final event, source fallback, full-text retrieval, sign-in, challenge action, access bypass, user-tab mutation, or adapter/test edit occurred. P01–P07 remain unchanged.

Basis labels: **[observed]** is a saved command, receipt, or narrow current-interface observation. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved. Protocol requirements are not source-behavior claims.

## 1. Patch, test, and browser preflight

- **[observed]** The adapter SHA-256 was `edec4799e3e431d14d62d64d297ec03943e9b1ae829007df01a8bae830228b56` before live work and at postflight. The academic-search dirty diff contained exactly the reviewed `search_scopus.py` and `test_search_scopus_browser.py` paths; `git diff --check` passed. No adapter/test file was edited, reset, cleaned, stashed, or committed.
- **[observed]** The focused Scopus suite ran once before live use under `caffeinate -dims` and reported **24 passed, 2 subtests passed in 0.06s**.
- **[observed]** Runtime and on-disk Chrome were both 151.0.7922.174. The read-only launcher check passed before live work and at postflight. The controller anchor was the sole page target before, between, and after owned-tab operations.
- **[observed]** AC power, AC idle sleep `0`, an active controller `caffeinate -dims` wrapper, and `PreventSystemSleep` remained present. Each stress or source command was separately process-scoped with `caffeinate -dims`.

## 2. No-query readiness stress

- **[observed]** The patched adapter path `open_chrome_connection` → `new_owned_chrome_page` → `navigate` → `wait_for_advanced_form` ran sequentially ten times in adapter-owned tabs. No query was typed or submitted.
- **[observed]** All 10 passes were ready; there were zero controlled errors. Per-pass elapsed times and controlled class/stage fields are in the restricted stress receipt. The anchor was present before and after every pass.
- **[inferred]** This bounded 10/10 result does not prove that all future intermittent readiness failures are impossible, but it did not reproduce P06's form-readiness behavior under the current patched adapter and healthy controller state.

## 3. Authorized sequential diagnostics

- **[observed]** Two A1 native-full-abstract passes used the immutable tracked A1 input, `--limit 20 --max-pages 2 --timeout 60 --page-delay-seconds 1`, and the default native Show all abstracts control. Each completed with exact total 4, one page, four retained records, four native full abstracts, and zero missing full abstracts. The totals and ordered stable-identity sequence hashes matched.
- **[observed]** Two A2 pagination passes used the immutable tracked A2 input with the same bounds and timeout/delay, plus `--skip-full-abstracts`. Each completed with exact total 14, two pages, and 14 retained records. The totals and ordered stable-identity sequence hashes matched. These runs validate pagination and repeatability, not A2 full-abstract availability.
- **[observed]** One immutable BT2-03 count-only command completed as an explicit native zero: total 0, one page, zero source entries, and zero records. It is not a partial prefix or candidate set.
- **[observed]** Every restricted JSON, captured JSON standard output, command-metadata JSON, and stderr file from the stress and five diagnostics was read in full after it settled. Record content and identifiers remain only under the ignored restricted P08 directory; tracked receipts contain counts and hashes only.
- **[observed]** The controller anchor remained the sole page target before and after each adapter command. No access, transport, readiness, reconciliation, pagination, identity, or completeness failure occurred in the authorized P08 sequence.

## 4. Postflight and classification

- **[observed]** Exact-window checks found zero actual `Entering Sleep state`, `System Sleep`, `System Wake`, `Wake reason`, or message-start `DarkWake` markers. They also found zero loginwindow `_handleAppleEvent` or `AboutThisMac event received` markers.
- **[observed]** `code_issue=false` for P08: the patched adapter completed the assigned no-query stress and all five authorized source diagnostics without a controlled error.
- **[inferred]** P08 does not explain the P06 intermittent failure or establish global absence of future intermittent failures. It does not accept the adapter, source method, or guideline.

## 5. Remaining limits and disposition

- **[untested]** Export/cap behavior and export-to-identity reconciliation; broad-query display-cap classification; controlled-vocabulary hierarchy/scope/explosion; exact Scopus `W/n` counting; all planned partitions and BT2 cross-cell union; date/language final controls; and all-cell final completeness.
- **[protocol]** `S-C01`, `P-001`, `S-002`, human review, and authorization of `R-002` remain separate prerequisites. No semantic/protocol change is proposed.
- **[inferred]** Recommend `revise`, not acceptance. Preserve the bounded stability evidence and use it only after human review; do not use pilot records or counts as a final discovery event.
