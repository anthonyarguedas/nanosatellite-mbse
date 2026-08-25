# Shared CfT live-phase checklist — S-D05-P03

## 1. Offline and authorization

- [x] Pilot/phase ID: `S-D05-P03-20260825T103818-0400`
- [x] Campaign and decision class: `S-D05-C01-20260824T161325-0400` (`controller_technical`)
- [x] Offline reading complete.
- [x] Exact query/operation and source-free adapter tests complete.
- [x] Artifact, rights, cleanup, and reporting plan complete.
- [x] OWNER: `S-D05-P03-20260825T103818-0400`
- [x] SOURCE: `wiley-online-library`
- [x] Immutable receipt PATH: `live-phase-receipt.json`
- [x] Global domain-pacing decision: one exclusive shared-CfT lease; three seconds between completed Wiley adapter invocations; no busy reissue.
- [x] Predeclared finite wait/readiness policy: 30-second lease wait; no source passive wait; retry policy `RP-D05-BUSY-01` has zero retries.

The source-free gate passed before attempt allocation: the focused Wiley suite passed 29 tests and 20 subtests, the current adapter and test hashes matched the P03 plan, CLI help passed, all nine existing query files passed exact byte/hash/LF checks, the shared validator passed, and `git diff --check` passed.

## 2. Lease command and shared-browser boundary

- [x] The phase will run only through `run_with_browser_lease.py` with `caffeinate -dims` around the complete command.
- [x] COMMAND is the Wiley adapter client shell only; it does not launch or control Chrome.
- [x] The only endpoint is `http://127.0.0.1:9222`.
- [x] The only profile is the supervisor's canonical shared `chrome-automation` profile; no profile or port override is present.
- [x] Read-only preflight reports one CfT process/epoch, one protected inert anchor, matching runtime/disk version `152.0.7977.54`, and a free lease.
- [x] The protected broker anchor will not be navigated, closed, or mutated.
- [x] The adapter may create and close only its own page; generic `browser_harness new_tab` is not used.
- [x] macOS power state and assertions were checked before the phase; the lid remains open and actual Sleep/Wake/DarkWake events will be checked across the phase window.

## 3. Provenance and health record

| Field | Before | After | Evidence |
| --- | --- | --- | --- |
| Lease acquired/released and release verified | free/released | released; `verified-clean`; no orphan; lock free | `live-phase-receipt.json`, `shared-lease-release-receipt.json` |
| Browser epoch | `5ASpPQYHIFJh_uD--zoyM7LG5u6fCcKh` | unchanged | `preflight.json`, `live-phase-receipt.json`, `postflight.json` |
| Profile identity/path and single-process assertion | canonical shared `chrome-automation`; supervisor status healthy | unchanged; one protected inert page | `preflight.json`, `live-phase-receipt.json`, `postflight.json` |
| CfT bundle provenance and runtime/on-disk version | CfT; `152.0.7977.54` / `152.0.7977.54` | unchanged and matching | `preflight.json`, `postflight.json` |
| Endpoint and broker-anchor health | `127.0.0.1:9222`; one protected inert anchor | healthy; anchor preserved | `preflight.json`, `live-phase-receipt.json`, `postflight.json` |
| Sleep protection, power, and Sleep/Wake result | `caffeinate -dims` required; power/assertions recorded; no preflight event | process-scoped caffeinate applied; zero actual phase events | `preflight.json`, `postflight.json`, `power-sleep-check.json` |
| Hashed adapter-owned target identities and closure | no adapter page before lease | three owned pages closed and cleanup verified; none survived | `live-phase-receipt.json`, `postflight.json` |

## 4. Busy, challenge, cancellation, and cleanup

- [x] Condition policy is fail-closed: `challenge` is never solved or retried; ordinary `busy` has no authorized reissue in this phase.
- [x] A challenge, login, verification, service error, rewrite, or unresolved busy state stops source work on the same owned page.
- [x] No source operation is reissued after failure.
- [x] On operator termination, the attached child must be cancelled and collected, source writing stopped, only the owned page closed, the anchor preserved, and lease release verified before supervision ends.
- [x] If cleanup cannot be verified, supervision remains active and the attempt is reported unresolved.

## 5. Outcome and handoff

- [x] Immutable receipt/evidence retained with acquisition, source actions, pacing/wait policy, health, target cleanup, and verified release.
- [x] Campaign checkpoint updated, hash-bound, and validated by the shared validator.
- [x] Unaffected prior gates remain bound to their exact prior evidence paths and SHA-256 values.
- [x] Terminal status: `completed` for the bounded phase; campaign remains technically blocked at completeness.
- [x] No pilot screening/import occurred; no partial prefix was imported.
