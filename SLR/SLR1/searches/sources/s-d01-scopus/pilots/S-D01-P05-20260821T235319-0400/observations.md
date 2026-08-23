# S-D01 Scopus P05 staged A1 count-only regression retry observations

- **Pilot ID:** `S-D01-P05-20260821T235319-0400`
- **Status:** `partial` diagnostic-only pilot; not accepted and not report-ready.
- **Execution window:** 2026-08-21T23:55:09-0400 to 2026-08-21T23:58:42-0400 (2026-08-22T03:55:09Z to 2026-08-22T03:58:42Z).
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** One live A1 count-only command only. No screening, candidate import, final event, fallback, sign-in, challenge handling, full-text work, or user-tab mutation occurred.

Basis labels: **[observed]** records this pilot's commands or saved local evidence. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved.

## 1. Staged adapter and preflight

- **[observed]** The supplied adapter SHA-256 was `3f012831c62eca638635be69da9e3d4bcc78b2aa477b4e542a43d55dc2114e7e`, matching the required fingerprint. Its focused offline browser suite was run once and reported **21 passed in 0.04s**. No adapter source or test was edited.
- **[observed]** Loopback CDP reported protocol 1.3. Runtime Chrome and the existing on-disk dedicated local application both reported 151.0.7922.174. The browser-harness daemon was absent. AC power, a `caffeinate -dims` wrapper, and a PreventSystemSleep assertion were active.
- **[observed]** The two specified P04 anchor IDs (`7B621E45F2FEF186E84F410B917A89E0`, `1727BDDC892F887D89AF0DBDE4B072C9`) were already absent from the CDP page-target list at P05 preflight. P05 did not create, restart, navigate, or close either ID. This prevents an anchor-continuity claim for P05.
- **[observed]** An initial non-source preflight version lookup used a non-existent system application path after the one focused test had completed. It issued no CDP or Scopus action; the existing dedicated local application was then inspected without launch or restart.

## 2. One immutable A1 count-only execution

- **[observed]** `P05-A1-COUNT-01` used the unchanged A1 file `queries/A1.scopus-advanced.txt` (2,096 bytes, SHA-256 `8fd3fb75d5e963df0d11a667bc865fac6aa611173dff266ba595f7e20667be88`) with `--count-only --limit 10 --max-pages 1`.
- **[observed]** The sole live command ran from 2026-08-21T23:56:06-0400 to 23:56:19-0400 and exited 0. Its saved restricted artifact was read in full and its complete stderr was read.
- **[observed]** It returned `status: count_only`, `total: 4`, `total_is_exact: true`, one rendered page, and zero retained records by count-only design. `output_metadata.error_stage` and `error_type` were absent because the run succeeded.
- **[protocol]** No second Scopus query was run regardless of the successful result. No records were screened, retained as candidates, or copied into a final event.

## 3. About This Mac and browser health

- **[observed]** The loginwindow query for `_handleAppleEvent` or `AboutThisMac event received` returned zero lines from the exact start through postflight. The nativeVirtualKeyCode regression was not observed in this window.
- **[observed]** At postflight, runtime and disk Chrome still matched at 151.0.7922.174; the browser daemon remained absent; AC and sleep protection remained active; and no extra page target remained. The page-target list was empty both before and after P05, so the expected anchors were not preserved/verified because they were already absent.
- **[observed]** The exact-window kernel/powerd check found zero actual Sleep/Wake markers (`Entering Sleep state`, `System Sleep`, `System Wake`, `Wake reason`, or `DarkWake`).

## 4. Assessment and stopping point

- **[inferred]** The P04 cold/stale generic A1 failure was not reproduced: the staged adapter completed the same immutable A1 count-only route and reconciled an exact total of 4. No code defect is evidenced by P05 (`code_issue: false`); no adapter change is warranted.
- **[untested]** P05 does not establish full A1 retrieval, repeatability, pagination, export/capture reconciliation, controlled-vocabulary behavior, the other partitions or BT2 union, `S-C01`, or `P-001`. It does not accept S-D01.
- **[inferred]** The narrow next action is for a supervising human to restore or verify the intended pre-existing anchors without automated mutation, then review P05 before authorizing any separate diagnostic scope. Do not edit code in response to P04's non-reproduced failure.

No protocol semantic change is proposed.
