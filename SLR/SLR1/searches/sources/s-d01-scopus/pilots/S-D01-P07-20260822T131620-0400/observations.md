# S-D01 Scopus P07 bounded A1 retry observations

- **Pilot ID:** `S-D01-P07-20260822T131620-0400`
- **Status:** `partial` focused diagnostic pilot; not accepted and not report-ready.
- **Execution window:** 2026-08-22T13:24:39-04:00 to 2026-08-22T13:27:00-04:00.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** Exactly one bounded record-bearing A1 command. No screening, candidate import, final event, source fallback, full-text retrieval, sign-in, challenge handling, access-control bypass, or user-tab mutation occurred.

Basis labels: **[observed]** is a saved command, receipt, or current local/browser observation. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved. Protocol requirements are not source-behavior claims.

## 1. Adapter and browser/power preflight

- **[observed]** The unmodified current `search_scopus.py` SHA-256 matched the authorized value before the live command and at postflight: `3f012831c62eca638635be69da9e3d4bcc78b2aa477b4e542a43d55dc2114e7e`. The relevant adapter/test worktree paths were clean; no code or test was edited.
- **[observed]** The focused Scopus browser suite ran exactly once and passed: **21 passed in 0.04s**. Its complete output is retained in `focused-test.txt`.
- **[observed]** The immutable tracked A1 input remained 2,096 bytes with SHA-256 `8fd3fb75d5e963df0d11a667bc865fac6aa611173dff266ba595f7e20667be88`.
- **[observed]** Read-only launcher checks passed before and after the command. Runtime and on-disk Chrome were both 151.0.7922.174. The sole page target was controller anchor `C02CA183D7757FFA07F9FFE63511DE8B` before and after the adapter-owned-tab command.
- **[observed]** AC power was active, AC idle sleep was disabled, the controller `caffeinate -dims` wrapper and `PreventSystemSleep` assertion were observed, and the live command itself was process-scoped with `caffeinate -dims`.

## 2. Sole record-bearing A1 execution

- **[observed]** `P07-A1-RECORD-01` was the only source query. It used the immutable A1 file by hash only with `--limit 10 --max-pages 1 --timeout 60 --page-delay-seconds 1`, the authorized local Chrome context, and default native **Show all abstracts** mode.
- **[observed]** The command exited 0. The complete restricted saved JSON and complete stderr were read. The saved artifact reports exact total 4, one page, four source entries and retained records, one native abstract-expansion page, four full abstracts, zero missing full abstracts, `retrieval_complete=true`, and `completion_status=complete` for this bounded result. No error stage is present.
- **[protocol]** P07 issued no second source query. Because the first command succeeded, it also ran no no-query form-readiness probe, repeat pass, A2 pagination, explicit-zero, export, cap, controlled-vocabulary, candidate-terminology, or final-schedule test.

## 3. Classification and limits

- **[observed]** `code_issue=false` for this retry: the current tested adapter completed the authorized bounded record-bearing route under the matching healthy preflight.
- **[inferred]** This success does not explain P06's intermittent `form_readiness` failure, prove that no intermittent robustness issue exists, or justify a code change.
- **[untested]** Repeatability, multi-page reconciliation, export/cap behavior, stable-identity repeat passes, all remaining partitions and BT2 union, exact `W/n` behavior, controlled-vocabulary hierarchy/scope, date/language implementation, S-C01, P-001, and S-002 remain outside this retry.

## 4. Postflight and disposition

- **[observed]** The controller anchor remained the sole page target; runtime/disk versions still matched; AC and the sleep assertion remained active; and no non-anchor page target remained.
- **[observed]** The exact execution-window checks found zero actual `Entering Sleep state`, `System Sleep`, `System Wake`, `Wake reason`, or message-start `DarkWake` markers, and zero loginwindow `_handleAppleEvent` or `AboutThisMac event received` markers.
- **[protocol]** This successful bounded diagnostic is not a candidate set or final event. All record-bearing content remains only in the ignored restricted P07 directory; tracked artifacts retain hashes, counts, controls, and safe conclusions only.
- **[inferred]** Recommend `revise`, not acceptance. Preserve this successful prerequisite evidence, then seek separately authorized validation of the remaining method/completeness requirements; do not rerun another source query under P07.

No protocol semantic change is proposed. The draft guideline is updated only to record the bounded P07 success and its limit.
