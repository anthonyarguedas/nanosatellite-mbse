# S-D01 Scopus P06 corrected-adapter record-retrieval retry observations

- **Pilot ID:** `S-D01-P06-20260822T124848-0400`
- **Status:** `failed` focused diagnostic pilot; not accepted and not report-ready.
- **Execution window:** 2026-08-22T12:54:14-0400 to 2026-08-22T12:59:23-0400.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** One bounded record-bearing A1 adapter command only. No screening, candidate import, final event, source fallback, full-text retrieval, sign-in, challenge handling, access-control bypass, or user-tab mutation occurred.

Basis labels: **[observed]** is a command, saved artifact, or narrow current-interface observation. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved. The protocol requirements are not source-behavior claims.

## 1. Current adapter and browser/power preflight

- **[observed]** The current unmodified `search_scopus.py` SHA-256 was `3f012831c62eca638635be69da9e3d4bcc78b2aa477b4e542a43d55dc2114e7e`. Its focused current browser suite ran once before live use and passed: **21 passed in 0.04s**. The academic-search worktree was clean before and after; this pilot did not edit adapter code or tests.
- **[observed]** The launcher read-only check passed. Loopback CDP was healthy at protocol 1.3; runtime and on-disk Chrome were both 151.0.7922.174. The controller anchor `C02CA183D7757FFA07F9FFE63511DE8B` was the sole preflight page target and remained the sole postflight page target.
- **[observed]** AC power was active, AC idle sleep was disabled, a `PreventSystemSleep` assertion and active `caffeinate -dims` process were present, and each adapter/probe process was additionally run under its own `caffeinate -dims` assertion. The pilot did not launch or restart Chrome.

## 2. Record-bearing corrected-adapter execution

- **[observed]** `P06-A1-RECORD-01` used the immutable A1 file (`queries/A1.scopus-advanced.txt`, 2,096 bytes, SHA-256 `8fd3fb75d5e963df0d11a667bc865fac6aa611173dff266ba595f7e20667be88`) with `--limit 10 --max-pages 1 --timeout 60 --page-delay-seconds 1` and the default native **Show all abstracts** mode.
- **[observed]** It exited 1 at 2026-08-22T12:54:16-0400. Its complete restricted saved JSON was read in full. It reports `ScopusRequestError` at controlled `error_stage: form_readiness`, `total: null`, zero pages, zero source entries, zero results, and `completion_status: error`. There is no retained partial prefix and this is not a source zero.
- **[protocol]** The first record-bearing prerequisite was unreconciled; therefore P06 ran no second source query. It did not attempt an A1 repeat, A2 pagination, BT2-03 zero, export, controlled-vocabulary, broad-cap, or final-schedule test.

## 3. Minimal no-query diagnosis

- **[observed]** A first local auxiliary-probe invocation lacked its declared Playwright dependency and terminated before a browser action. It is retained only as a local instrumentation failure and is not source or adapter evidence.
- **[observed]** A second owned-tab, no-query current-UI probe attached to the same local Chrome, navigated only to the normal public Advanced Search route, and observed the exact expected form shape: advanced mode; one visible `.native-edit-context` `Editor content` textbox; one `advanced-search-button`; no blocked, login, or syntax state. It submitted no query and closed only its own page.
- **[observed]** A separate no-query probe then used the current adapter's own `open_chrome_connection`, `new_owned_chrome_page`, `navigate`, and `wait_for_advanced_form` functions. It also reached `status: ready` with the same valid form state and closed only its own page.
- **[inferred]** The later successful no-query adapter-path probe means the P06 form-readiness failure was not reproduced during minimal diagnosis, while the current rendered interface was available and did not display an access wall. It does **not** identify a cause or make the failed record-bearing route successful.
- **[inferred]** `code_issue` is **unresolved**, not true: there is no reproducible code defect evidence from P06 and no code change is justified. The result is also not proof that the failure was source-side or transient; it remains unclassified.

## 4. Browser, sleep, and side-effect postflight

- **[observed]** The controller anchor persisted; no non-anchor page target remained; runtime/disk browser versions still matched; AC power and the active sleep assertion remained present.
- **[observed]** The refined exact-window kernel/powerd query found zero actual `Entering Sleep state`, `System Sleep`, `System Wake`, `Wake reason`, or message-start `DarkWake` events. Four `vm.darkwake_mode: 0 -> 0` configuration lines in the broader candidate log were excluded as non-events.
- **[observed]** The exact-window loginwindow query found zero `_handleAppleEvent` or `AboutThisMac event received` lines. This does not turn the failed source route into a successful route.

## 5. Disposition and remaining requirements

- **[protocol]** This pilot cannot accept S-D01 or authorize a final search. `P-001`, `S-C01`, the remaining source pilots, and `S-002` remain dependencies.
- **[untested]** Corrected-adapter record retrieval, native abstract evidence, repeatability, pagination, export/cap and identity reconciliation, controlled-vocabulary hierarchy/scope/explosion, W/n counting, all planned cells and BT2 union, common date/language implementation, and the broad-query cap condition remain untested in the current P06 execution.
- **[inferred]** Recommend `repeat`, not acceptance or a speculative code patch. A supervising reviewer should inspect the restricted A1 failure and no-query probe receipts, then authorize at most a separately scoped fresh bounded A1 retry. Escalate a code issue only if an equivalent current failure becomes reproducible with a minimally controlled diagnosis.

No protocol semantic change is proposed. The draft guideline is amended only to record the P06 operational uncertainty.
