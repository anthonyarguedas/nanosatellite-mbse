# S-D01 Scopus P04 keyboard-side-effect regression retry observations

- **Pilot ID:** `S-D01-P04-20260821T231756-0400`
- **Status:** `failed` focused diagnostic pilot; not accepted and not report-ready.
- **Execution window:** 2026-08-21T23:23:24-04:00 to 2026-08-21T23:25:28-04:00 (2026-08-22T03:23:24Z to 2026-08-22T03:25:28Z).
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** No screening, candidate import, final event, full-text retrieval, source fallback, sign-in, challenge handling, or user-tab mutation occurred. P01–P03 remain unchanged.

Basis labels: **[observed]** records this pilot's commands, saved artifacts, or local system observations. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved. Protocol requirements are marked **[protocol]**.

## 1. Corrected-adapter and browser preflight

- **[observed]** The supplied adapter had SHA-256 `da7c56065d8a3caa0f987134bd8415ee7e24d6dd2d40a9ad51808f5fbedc750c`, matching the required corrected fingerprint. Its focused offline browser suite passed: **17 passed in 0.03s**. No adapter source or test was edited.
- **[observed]** Loopback CDP at `127.0.0.1:9222` reported protocol 1.3. Runtime Chrome and the on-disk application were both 151.0.7922.174. The intentional pre-existing page targets were the blank anchor `7B621E45F2FEF186E84F410B917A89E0` and New Tab anchor `1727BDDC892F887D89AF0DBDE4B072C9`.
- **[observed]** No browser-harness daemon process was present. AC power was active; AC idle sleep was disabled in the observed settings. A process-scoped `caffeinate -dims` assertion was active on behalf of Pi. No browser, daemon, power setting, or anchor tab was restarted, launched, navigated, or closed by this pilot.

## 2. A1 count-only execution and stopping rule

- **[observed]** P04 verified the existing A1 query unchanged at 2,096 bytes and SHA-256 `8fd3fb75d5e963df0d11a667bc865fac6aa611173dff266ba595f7e20667be88`.
- **[observed]** `P04-A1-COUNT-01` used that immutable input with `--count-only --limit 10 --max-pages 1` in one adapter-owned page. Its complete restricted artifact was read in full after execution.
- **[observed]** The execution failed as `ScopusRequestError`, with `total: null`, zero pages, zero retained records, and no partial prefix. This is neither a source zero nor a successful source state.
- **[protocol]** Because the prerequisite A1 count-only route failed, P04 did not run BT2-03 or any other live source query. It did not attempt a manual/user-tab fallback or query variation.

## 3. About This Mac regression result

- **[observed]** Before the retry, P04 queried the macOS unified log for loginwindow `_handleAppleEvent` or `AboutThisMac event received` messages.
- **[observed]** The immediate post-A1 query and a final query spanning the exact execution window each returned zero matching lines. This is the required acceptance test; the conclusion is based on the log query, not on whether a window was noticed.
- **[inferred]** The corrected adapter did not reproduce the prior macOS About This Mac keyboard side effect in this execution. This observation does not make the failed A1 source route successful.

## 4. Sleep and browser health

- **[observed]** At postflight both pre-existing anchor IDs remained, no non-anchor page target remained, and runtime/disk Chrome versions still matched.
- **[observed]** The power source remained AC. The exact-window kernel/powerd unified-log query found no matching actual Sleep or Wake event.

## 5. Code assessment and remaining uncertainty

- **[inferred]** The keyboard-side-effect regression is not observed for the corrected SHA in this exact window. However, the generic A1 `ScopusRequestError` does not distinguish source/UI/access/transient behavior from an adapter-stage defect. Therefore `code_issue` is **unresolved**, not false.
- **[inferred]** Another code-fix subagent is not warranted yet: first obtain a non-mutating diagnosis or reproducible failure classification. Do not make speculative adapter changes or spray additional live queries.
- **[untested]** BT2-03 under the corrected SHA; corrected-adapter successful count/retrieval/pagination; controlled-vocabulary hierarchy/scope/explosion; exact `W/n` counting; export/cap and export-to-identity reconciliation; all final cells and BT2 union; `S-C01`; and `P-001` remain unresolved.

No protocol semantic change is proposed, and this pilot does not accept S-D01.
