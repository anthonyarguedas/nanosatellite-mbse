# Shared CfT live-phase checklist

Copy this checklist into the phase receipt or its source-safe evidence index. Complete the offline section before acquiring the lease. Do not include credentials, cookies, session values, profile contents, or private URLs.

## 1. Offline and authorization

- [ ] Pilot/phase ID: `REPLACE`
- [ ] Campaign and decision class: `REPLACE` (`none`, `controller_technical`, or `human_methodological`)
- [ ] Offline reading complete.
- [ ] Exact query/operation and source-free adapter tests complete.
- [ ] Artifact, rights, cleanup, and reporting plan complete.
- [ ] `OWNER`: `REPLACE` (unique supervised pilot/phase)
- [ ] `SOURCE`: `REPLACE` (source ID)
- [ ] Immutable receipt `PATH`: `REPLACE`
- [ ] Global domain-pacing decision: `REPLACE`
- [ ] Predeclared finite wait/readiness policy, or `none`: `REPLACE`

Only source-free offline work may be concurrent. Every deterministic source-free query-byte, CLI, adapter, output-path, and infrastructure check must pass before lease acquisition. Patch a technical preflight failure rather than treating its safe stop as success. If an attempt ID was already allocated but no source phase began, record `allocation.source_phase_started=false`; it does not consume the enacted source-phase budget. A technical corrective source action must be within the campaign's controller-authorized finite bounds; only a methodological change affecting the review requires human authorization. A prospectively authorized finite passive wait or internal readiness retry may remain in this phase.

## 2. Lease command and shared-browser boundary

Run the whole browser-backed phase through exactly:

```text
uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py --owner OWNER --source SOURCE --receipt PATH [--wait SECONDS] [--lease-timeout SECONDS] -- COMMAND...
```

- [ ] `COMMAND...` is an adapter client command, not a browser launcher/controller.
- [ ] The only endpoint is `127.0.0.1:9222`.
- [ ] The only profile is `~/agent-tools/.browser-profiles/chrome-automation`; no profile or port override is present.
- [ ] The supervisor asserts that exactly one CfT process uses that profile.
- [ ] One protected broker anchor is healthy before the phase. It will not be mutated.
- [ ] The adapter creates/closes only its own page. `browser_harness new_tab` is not used.
- [ ] On macOS, the controller records process-scoped `caffeinate -dims`, power state, and actual Sleep/Wake checks; the lid stays open.

## 3. Provenance and health record

Record before/after values and safe evidence paths:

| Field | Before | After | Evidence |
| --- | --- | --- | --- |
| Lease acquired/released and release verified | `REPLACE` | `REPLACE` | `REPLACE` |
| Browser epoch | `REPLACE` | `REPLACE` | `REPLACE` |
| Profile identity/path and single-process assertion | `REPLACE` | `REPLACE` | `REPLACE` |
| CfT bundle identity/provenance and runtime/on-disk version | `REPLACE` | `REPLACE` | `REPLACE` |
| Endpoint and broker-anchor health | `REPLACE` | `REPLACE` | `REPLACE` |
| Sleep protection, power, and Sleep/Wake result | `REPLACE` | `REPLACE` | `REPLACE` |
| Hashed adapter-owned target identities and closure | `REPLACE` | `REPLACE` | `REPLACE` |

A failed version, anchor, sleep, or profile/process health check stops source work. Outside any lease, the supervisor—or the assigned controller using only README's bounded canonical reconciliation after proving the OS lease free and no guardian/orphan alive—may restore this dedicated CfT; record the resulting new browser epoch and recheck the complete launch gate.

## 4. Busy, challenge, cancellation, and cleanup

- [ ] Condition classified: `none` / `busy` / `challenge` / `other`.
- [ ] For **busy**, keep the same owned page and record global pacing plus the finite policy ID, maximum wait, delays, request limit, and attempted/completed retry counts. Reissue only when that predeclared policy explicitly permits it.
- [ ] For **challenge** (CAPTCHA, login, verification, anti-automation), do not solve, evade, bypass, rotate a profile, create a new page, or retry automatically. Keep the page and request human action unless a preauthorized passive wait applies.
- [ ] On user/operator termination, record `cancelled`, cancel and collect every live child, stop source-writing, close only the owned page, preserve the anchor, and verify lease release.
- [ ] If cleanup is not verified, continue controller supervision and report unresolved cleanup; never leave an orphan source writer.

## 5. Outcome and handoff

- [ ] Immutable receipt/evidence retained with acquisition, source actions, pacing/wait policy, health, target cleanup, and verified release.
- [ ] Campaign checkpoint updated with passed, failed, and invalidated dependent gates.
- [ ] Unaffected prior gates are carried forward by exact evidence path and SHA-256.
- [ ] Terminal status: `completed` / `blocked` / `failed` / `cancelled`.
- [ ] A late optional/technical failure is described narrowly; it does not erase successful gates or make the provider wholly inaccessible.
- [ ] `controller_technical` work requests no human authorization; only a review-affecting `human_methodological` decision does.
- [ ] No pilot screening/import occurred. A final blocked, failed, or cancelled event imports no partial prefix.
