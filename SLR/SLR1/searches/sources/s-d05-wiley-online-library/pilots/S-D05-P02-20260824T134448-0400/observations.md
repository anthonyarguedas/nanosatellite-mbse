# Wiley Online Library diagnostic observations — S-D05-P02-20260824T134448-0400

**Status:** blocked before the first Wiley request; diagnostic only; `code_issue=false` for P02's source-free corrective-adapter verification. P01 remains immutable with its separate `code_issue=true` finding for the older adapter.

## Stop rule and timeline

1. **[observed] 2026-08-24T13:43:41-04:00 — corrective implementation gate passed source-free.** The assigned worktree was clean at required branch/commit `c8be56c87fe17f413de7c083b49f3bfebfca5bc7`; the adapter and focused test hashes matched exactly. The focused no-clobber suite passed 8 tests and 2 subtests, including existing destination, symlink, race, error-artifact, and rollback behavior. Pinned `--help` also exited 0 with the explicit dedicated CDP argument. No browser page or Wiley request was made. See [`adapter-verification.json`](adapter-verification.json).
2. **[observed] 2026-08-24T13:47:50-04:00 — v4 query regeneration passed source-free.** All nine exact root expressions were regenerated in memory from the current dictionary and reconciled to their root files. Literal, pair-cross-product, candidate-term, wildcard, hash, byte-length, and terminal-LF checks passed. This proves construction only, not Wiley syntax or source behavior. See [`query-regeneration-audit.json`](query-regeneration-audit.json).
3. **[observed] 2026-08-24T13:48:47-04:00 — required fresh dedicated browser gate failed.** The controller's earlier `preflight.ok` had recorded a healthy endpoint and sole `chrome://newtab/` anchor. P02 then ran the exact read-only launcher check before H-001. It reported `Chrome DevTools endpoint is not live: http://127.0.0.1:9236`. The assigned Chrome listener/process was not observed after that failure. A timestamped actual Sleep/Wake/DarkWake filter since P02 allocation was empty, but this does not cure the stale endpoint. See [`browser-preflight-failure.json`](browser-preflight-failure.json).
4. **[observed] 2026-08-24T13:48:47-04:00 onward — live work stopped.** Per the explicit stop rule, P02 did not rerun the launcher, relaunch/repair Chrome, inspect or navigate a browser page, invoke the adapter for a source query, run H-001, or make any Wiley request. It created no owned page, result, DOI ledger, RIS, raw JSON/CSV, screenshot, DOM/page-text capture, screening decision, candidate import, final event, retry, patch, or commit. See [`source-request-ledger.json`](source-request-ledger.json) and [`restricted-capture-ledger.json`](restricted-capture-ledger.json).

## Requirement disposition

| Area | Status | Basis | Evidence / consequence |
|---|---|---|---|
| Pinned corrective commit, clean worktree, exact adapter/test hashes, focused tests, and source-free no-clobber behavior | verified | observed | `adapter-verification.json`; no new P02 code issue demonstrated. |
| P01 immutability | verified | observed | `p01-immutability-receipt.json`; no P01 file changed. |
| All nine v4 query constructions, literals, pair cross-products, hashes, bytes, and LF | verified narrowly | observed | `query-regeneration-audit.json`; no source parser behavior follows. |
| Controller preflight evidence | verified historically | observed | Controller receipts were inspected; they are superseded for live use by the failed fresh check. |
| Fresh dedicated endpoint, matching runtime/on-disk version, current anchor, current AC/assertions/clamshell state, and final postflight | blocked | observed | The first required P02 launcher check found a stale endpoint; later assertions cannot be claimed. No postfailure browser retry was attempted. |
| H-001 normal rendered health gate and method-set ladder item a | blocked before invocation | observed | `source-request-ledger.json`; no query, total, record, or owned adapter page. |
| Advanced Search / known-record inspection; boundary; routes/totals; fields; help; echo/rewrite; controlled/indexed terms | blocked | untested | No Wiley page was requested. |
| Parser, precedence, phrases, punctuation/hyphen, case, acronym, wildcard, expansion, length, and proximity contrasts | blocked | untested | No Wiley query was submitted. |
| Explicit native zero, date/month and exact-day handling, language, ordering, page size, total semantics, and convenience-limit check | blocked | untested | No Wiley query was submitted. |
| Supported final-cell count-only submissions | blocked | untested | No Wiley query was submitted; all totals remain `null`. |
| Method-set selection, page transition, two-pass DOI reconciliation, and RIS export | blocked | untested | No Wiley query was submitted; no restricted source file exists. |
| No screening, import, final event, or retained source material | verified | observed | `manifest.json`; `source-request-ledger.json`; `restricted-capture-ledger.json`. |

## Translation and pair disposition

- **[observed]** P02 did not alter any root query byte because current root files exactly equal fresh v4 regeneration.
- **[untested]** No source parser, field, or source-length gate was reached. A1, A2, A3, B1, and B2 are not source-supported merely because their source-free construction audit passed.
- **[blocked]** BG1, BG2, BC1, and BT2 remain final-use-prohibited. No Wiley-native unordered <=5-token proximity or compliant broader same-field fallback was observed. BT2 was neither sent nor split.

## Interface, controlled-vocabulary, and documentation disposition

- **[untested]** No current normal Advanced Search, help/operator text, route, field, query echo, known record, keyword surface, descriptor, hierarchy, scope, narrower term, or explosion control was inspected.
- **[protocol]** Free text remains mandatory. A generic systems-engineering label cannot substitute for MBSE, and visible keywords cannot be called controlled vocabulary without source evidence.

## Rights and protocol separation

- **[observed]** The authorized restricted root is `.searches/s-d05-wiley-restricted/S-D05-P02-20260824T134448-0400/`; it contains zero files because P02 made zero Wiley requests.
- **[observed]** Only the D05 source packet and authorized ignored restricted root were written. P02 did not edit `TASKS.md`, `search-log.md`, protocol files, dictionaries, crosswalks, schemas/templates, shared scripts, final events, another source packet, agent tools, the Git index, or history.
- **[protocol]** P02 proposes no semantic/protocol change. `P-001` remains unresolved, and the planned 2026-08-24 diagnostic bound was never used as a source control or called a final cutoff.

## Human/controller handoff and smallest next action

**[observed]** P02 is not accepted and cannot authorize itself or a retry. The minimal next action is controller-owned graceful recovery/relaunch of the dedicated `9236` browser, followed by a new controller preflight that verifies the endpoint, version, sole anchor, AC, four active assertions, open-lid limitation, and no actual Sleep/Wake/DarkWake event. Only then may the review owner authorize a new immutable corrective Wiley pilot; that pilot must still execute every live requirement blocked here.
