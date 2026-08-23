# S-D01 Scopus P10 cap-classification retry observations

- **Pilot ID:** `S-D01-P10-20260822T154458-0400`
- **Status:** `partial` diagnostic pilot; the expected controlled source error is a successful cap diagnostic, not a final search or method acceptance.
- **Execution window:** 2026-08-22T15:44:58-0400 to 2026-08-22T15:45:04-0400.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** P10 ran one focused offline test suite and **exactly one** source query. It performed no screening, candidate import, final event, second source query, source fallback, full-text retrieval, sign-in, challenge action, access-control bypass, native export, user-tab mutation, browser launch/restart, adapter edit, test edit, shared-file edit, or commit.

Basis labels: **[observed]** is a saved P10 command, receipt, or current-interface result. **[inferred]** is a constrained conclusion. **[untested]** remains unresolved. Protocol requirements are not source-behavior claims.

## 1. Reviewed implementation and preflight

- **[observed]** P10 verified the expected adapter SHA `10bbf79baec56208820be9463a853582880c4fa92b480a6ebd177730d71d936d`, test SHA `8a7a3674a96c0601e93ddbe7d76be9b67cd23c67b97260623eaafe2864b7f2ca`, the exact two-file dirty-diff scope, and a clean diff check. The binary-safe reviewed-diff hash was `696d51c483c785852ed03016d1109087dfd0cca2ac096a64d9894ed3efdaf0a2`.
- **[observed]** The one focused suite passed **27 tests and 2 subtests in 0.06 seconds**. The reviewed parser change accepts only visible result-list layouts, treats one unique range reconciled to current rows as trusted cap evidence, classifies a range total at or above the rendered display cap before requiring one aggregate total, and leaves conflicting/uncapped evidence generic and fail-closed.
- **[observed]** Preflight passed with Chrome `151.0.7922.174`, a successful runtime/disk equality check, AC power, active `caffeinate -dims` assertions, and the preserved controller anchor `C02CA183D7757FFA07F9FFE63511DE8B` as the only page target. The anchor was observed only and was not supplied as `--target-id`.
- **[observed]** The absolute requested output path was verified before execution under the project restricted P10 directory and did not exist before the command.

## 2. Sole source diagnostic

- **[observed]** P10 submitted exactly one normal rendered Scopus Advanced Search command: `TITLE-ABS-KEY("CubeSat")`, count-only, `--limit 20`, `--max-pages 2`, `--timeout 60`, and `--page-delay-seconds 1`. It used the adapter's normal default local CDP route, supplied no `--target-id`, and let the adapter create and close its own Scopus page.
- **[observed]** The command exited `1` after **3.667 seconds** with `ScopusDisplayCapError` at `result_reconciliation`. The restricted JSON reports `total=null`, `total_is_exact=false`, zero pages, zero source entries, zero records, an empty result list, and non-mergeable accounting. Its stderr was read in full; stdout was empty. No partial prefix was retained.
- **[observed]** The restricted output JSON SHA-256 is `993185881fe5d24871c127da07735e331749350de0b586f464c4bb1da21b152a`; stderr SHA-256 is `e4a6ae6fde85ad35a1fc111ac6e18756b027a1f8ec3e7f575bff509a12505233`; empty stdout has the standard SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. All remain in restricted storage.

## 3. P06 and P09 disposition

- **[observed]** P09's same broad diagnostic ended as generic `ScopusProtocolError` at `result_reconciliation` after approximately **61.425 seconds**. Its safe artifact could not distinguish a visible history total from current result-list evidence, so it did not prove a display-cap class or a source total.
- **[observed]** P10 completed approximately **57.758 seconds faster** (94.0% less P09-to-P10 command wall time) and returned the specific controlled display-cap class. This is materially faster than the prior generic 60-second timeout behavior.
- **[inferred]** The P09 cap-classification incident is now closed for the reviewed adapter SHA: current, visible, structurally unique result-list range evidence can win over conflicting broad aggregate evidence without retaining a prefix. The result still does not establish a broad Scopus source total or disclose the rendered count.
- **[inferred]** This result is separate from P06. P06's readiness-budget control-flow defect was already patched and bounded-validated; P06's original underlying Playwright trigger remains unidentified by its safe artifact. P10 neither identifies that trigger nor changes P06's evidence limit.

## 4. Postflight and readiness

- **[observed]** Postflight browser health/version checks passed. The sole remaining page target was the preserved controller anchor; no non-anchor target remained. AC power and active sleep assertions remained present, with zero matching actual Sleep/Wake markers and zero matching About This Mac markers in the exact pilot window.
- **[observed]** The adapter SHA remained unchanged postflight. The pilot did not activate native export, mutate a user tab, or take login/challenge action.
- **[inferred]** The cap issue is closed as a bounded adapter/source-interface diagnostic. The Scopus source-interface packet is ready for **human review** pending `S-C01` and `P-001`; it is not accepted, report-ready, or authorized for a final event. `S-002`, final boundary/control recording, all-cell two-pass completeness, and `R-002` authorization remain required.
- **[untested]** P10 did not execute the final partition set under a common cutoff, validate final two-pass identities, resolve W/n endpoint semantics, or complete the separate S-C01 terminology work.

No protocol semantic change is proposed. The translation specification is unchanged because P10 validates cap classification and failure accounting, not source query translation.
