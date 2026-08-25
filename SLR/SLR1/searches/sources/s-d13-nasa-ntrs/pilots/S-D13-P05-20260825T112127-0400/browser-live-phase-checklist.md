# Shared CfT live-phase checklist — S-D13-P05

## 1. Offline and authorization

- [x] Pilot/phase ID: `S-D13-P05-20260825T112127-0400`
- [x] Campaign and decision class: `S-D13-C01-20260824T161325-0400` (`controller_technical`)
- [x] Offline reading complete.
- [x] Exact query/operation and source-free adapter tests complete.
- [x] Artifact, rights, cleanup, and reporting plan complete.
- [x] `OWNER`: `S-D13-P05-20260825T112127-0400`
- [x] `SOURCE`: `ntrs`
- [x] Immutable receipt `PATH`: `.searches-d13-ntrs/S-D13-P05-20260825T112127-0400/browser-lease-receipt.json`
- [x] Global domain-pacing decision: no busy reissue or retry; fixed three-second passive pacing between the distinct health and conditional adapter operations.
- [x] Predeclared finite wait/readiness policy: `RP-D13-BUSY-01`, maximum retries `0`; lease wait `30s`, lease child cap `600s`; inter-operation passive delay `3s` is not a retry.

## 2. Lease command and shared-browser boundary

Run the whole browser-backed phase through exactly:

```text
caffeinate -dims uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py --owner S-D13-P05-20260825T112127-0400 --source ntrs --receipt .searches-d13-ntrs/S-D13-P05-20260825T112127-0400/browser-lease-receipt.json --wait 30 --lease-timeout 600 -- COMMAND...
```

- [x] `COMMAND...` is an adapter/probe client command, not a browser launcher/controller.
- [x] The only endpoint is `127.0.0.1:9222`.
- [x] The only profile is the canonical shared CfT profile; no profile or port override is present.
- [x] The supervisor asserts exactly one CfT process owns that profile.
- [x] One protected inert broker anchor is healthy before the phase and will not be mutated.
- [x] Each client creates/closes only its own page; `browser_harness new_tab` is not used.
- [x] On macOS, the complete phase is under process-scoped `caffeinate -dims`; AC power is confirmed and the lid remains open.

## 3. Provenance and health record

| Field | Before | After | Evidence |
| --- | --- | --- | --- |
| Lease acquired/released and release verified | free before lease | acquired and released; `verified-clean` | `browser-status-sanitized.json`, restricted lease receipt, `browser-postflight-sanitized.json` |
| Browser epoch | `bldqawxcF3fqkU-S9IBNeLhNxQf0jcIT` | unchanged: `bldqawxcF3fqkU-S9IBNeLhNxQf0jcIT` | `browser-status-sanitized.json`, restricted lease receipt, `browser-postflight-sanitized.json` |
| Profile identity/path and single-process assertion | canonical shared profile; one top-level CfT owner | unchanged; one top-level CfT owner | `browser-status-sanitized.json`, restricted lease receipt, `browser-postflight-sanitized.json` |
| CfT bundle identity/provenance and runtime/on-disk version | `com.google.chrome.for.testing`; `152.0.7977.54` / `152.0.7977.54` | unchanged and matched | `browser-status-sanitized.json`, restricted lease receipt, `browser-postflight-sanitized.json` |
| Endpoint and broker-anchor health | loopback `127.0.0.1:9222`; one protected inert anchor | unchanged; one anchor; anchor preserved | `browser-status-sanitized.json`, restricted lease receipt, `browser-postflight-sanitized.json` |
| Sleep protection, power, and Sleep/Wake result | AC power; phase protection pending | process-scoped `caffeinate -dims`; AC; no transition observed in phase window | `power-preflight.json`, `power-postflight.json` |
| Hashed adapter-owned target identities and closure | no adapter target yet | health page closed; lease cleanup verified no new targets remain | restricted lease receipt; source operation receipts; `browser-postflight-sanitized.json` |

The current instance epoch is used because the independently proven current instance receipt is authoritative; the released prior lease metadata names an older, inactive generation. No source work proceeds without the lease runner's fresh epoch/health reconciliation.

## 4. Busy, challenge, cancellation, and cleanup

- [x] Condition policy: `none` initially; any challenge is terminal and is never solved, bypassed, rotated, or retried; any busy state has no reissue under `RP-D13-BUSY-01`.
- [x] Same owned page is retained for any terminal source state until normal cleanup; no fresh page is used to escape a condition.
- [x] On operator termination, the attached lease child is cancelled and collected, source writing stops, only owned pages are closed, the broker anchor is preserved, and lease release is verified before ending supervision.
- [x] If cleanup is not verified, controller supervision continues fail-closed.

## 5. Outcome and handoff

- [x] Immutable receipt/evidence retained with acquisition, source actions, pacing, health, target cleanup, and verified release.
- [ ] Campaign checkpoint updated with passed, failed, and dependent gate states.
- [x] Unaffected prior gates are hash-bound in `pre-existing-attempt-hashes.json` and will be carried forward only if unaffected.
- [x] Terminal status: `failed` at the conditional rendered operation's ordering-control gate; source writing stopped.
- [x] No screening, candidate import, partial-prefix import, relevance classification, or final event occurred.
- [x] The adapter count-only output is diagnostic only and cannot enter screening, candidate import, PRISMA identification, or a final event.
