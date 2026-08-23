# S-D01 Scopus P03 focused live-adapter retry observations

- **Pilot ID:** `S-D01-P03-20260821T183926-0400`
- **Status:** `partial` diagnostic pilot; not accepted and not report-ready.
- **Live-execution window:** 2026-08-21T18:39:26-04:00 to 2026-08-21T18:44:13-04:00.
- **Protocol commit:** `38ab61287443693ddabdd4bb855d535a4585ae35`.
- **Boundary:** No screening, candidate import, final event, source fallback, full-text retrieval, sign-in, challenge handling, or user-tab mutation occurred. P01 and P02 are unchanged historical evidence.

Basis labels: **[observed]** records this retry's commands and saved artifacts; **[inferred]** is a constrained conclusion; **[untested]** remains unresolved. Protocol requirements are marked **[protocol]**.

## 1. Supplied adapter and local-browser preflight

- **[observed]** The supplied dirty `search_scopus.py` had SHA-256 `af14a53013eb446cc9c605dcda1623d22476fb1aa724f0b224d3d03330b5d7c3`. Its focused browser suite passed before live use: `16 passed in 0.04s`. The supplied worktree was not edited, cleaned, reset, stashed, committed, or otherwise disturbed.
- **[observed]** Loopback CDP was reachable at protocol 1.3 with zero pre-existing page targets. The preflight only read local CDP metadata; it did not select, navigate, or close a user tab. The adapter used its own tab.
- **[observed]** The P02 A1 input was reused byte-for-byte: `queries/A1.scopus-advanced.txt`, 2,096 bytes, SHA-256 `8fd3fb75d5e963df0d11a667bc865fac6aa611173dff266ba595f7e20667be88`.

## 2. Successful bounded live checks

- **[observed]** A1 count-only completed through the current normal rendered Advanced Search route with `total=4`, `total_is_exact=true`, one rendered page, and zero retained records by count-only design.
- **[observed]** Two bounded A1 full-abstract passes each completed with `total=4`, four retained records, one page, and four native rendered abstracts. Their ordered rank-plus-publication-identity sequence hashes matched. Record-bearing artifacts remain only in the restricted P03 directory.
- **[observed]** Two bounded A2 pagination passes each completed with `total=14`, 14 retained records, and two pages. Their ordered rank-plus-publication-identity sequence hashes matched. The pagination-specific runs used `--skip-full-abstracts`; they validate bounded page traversal and identity stability, not A2 full-abstract availability.
- **[observed]** The known BT2-03 diagnostic completed as an explicit source zero: `total=0`, `total_is_exact=true`, zero retained records, and no partial prefix.

## 3. Broad-query fail-closed diagnostic

- **[observed]** The single broad `TITLE-ABS-KEY("CubeSat")` count-only diagnostic saved an error artifact with `total=null`, zero pages, zero records, and `ScopusProtocolError`. No partial prefix was retained.
- **[inferred]** The adapter therefore failed closed for the broad diagnostic, but the rights-safe error artifact does not identify a rendered cap, UI drift, or another reconciliation condition. This retry does **not** establish that the explicit `>=2,000` display-cap branch was reached, and it does not establish an underlying broad total. No repeat or additional broad query was run.

## 4. Code and access assessment

- **[observed]** Unlike P02, the current supplied adapter successfully submitted A1, retrieved its native full abstracts, and completed a two-page A2 route in the same authorized rendered interface.
- **[inferred]** This evidence does not identify the exact transient/request-stage cause of P02's `ScopusRequestError`. It does not establish an adapter/code defect. The broad diagnostic's generic `ScopusProtocolError` remains an unresolved source/UI-or-reconciliation classification, not a demonstrated code fault.
- **[observed]** No login, CAPTCHA, challenge, or access-denial state was observed in any successful P03 route.

## 5. Remaining conditions and disposition

- **[protocol]** This pilot cannot accept S-D01 or authorize a final event. `P-001`, `S-C01`, all other required source pilots, and `S-002` remain dependencies.
- **[untested]** Current controlled-vocabulary hierarchy/scope/explosion and descriptor mapping; `W/n` endpoint counting; actual export/cap and export-to-identity reconciliation; full-abstract behavior beyond bounded A1; every remaining partition; BT2 cross-cell identity union; common cutoff and language handling; and a human resolution of the broad-query cap/reconciliation behavior remain unresolved.
- **[inferred]** Recommend `revise`, not acceptance. The draft guideline may describe the now-observed bounded adapter route, while retaining all unresolved limitations and human-verification requirements.
