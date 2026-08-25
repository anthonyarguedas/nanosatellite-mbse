# Shared CfT live-phase checklist

Use this checklist for both exploration and evidence phases. Copy it into the session/attempt receipt or safe evidence index. Do not include credentials, cookies, session values, profile contents, or private URLs.

## 1. Offline and authorization

- [ ] Mode: `exploration` / `evidence`
- [ ] Exploration session or pilot/phase ID: `REPLACE`
- [ ] Campaign and decision class: `not_applicable_for_exploration` / `REPLACE`
- [ ] Offline reading complete.
- [ ] Minimum launch gate complete: exact query, command startup, create-only outputs, manifest/receipt shape, and browser health. No broad suite required.
- [ ] Artifact, rights, cleanup, and reporting plan complete.
- [ ] `OWNER`: `REPLACE` (unique supervised pilot/phase)
- [ ] `SOURCE`: `REPLACE` (source ID)
- [ ] Immutable receipt `PATH`: `REPLACE`
- [ ] Global domain-pacing decision: `REPLACE`
- [ ] Predeclared finite wait/readiness policy, or `none`: `REPLACE`

Only source-free work may be concurrent. Require the minimum launch gate above, not a large fixture or regression suite. Patch a technical preflight failure with the smallest direct check and proceed to real-page validation. If an attempt ID was already allocated but no source phase began, record `allocation.source_phase_started=false`; it does not consume the enacted source-phase budget. Technical real-page observation, finite passive waits, and bounded logged retests are controller-authorized; only a methodological change affecting the review requires human authorization.

## 2. Lease command and shared-browser boundary

Run the whole browser-backed phase through exactly:

```text
uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser_lease.py --owner OWNER --source SOURCE --receipt PATH [--wait SECONDS] [--lease-timeout SECONDS] -- COMMAND...
```

- [ ] `COMMAND...` is a trusted owned-page exploration runner or frozen evidence adapter, not a browser launcher/controller.
- [ ] The only endpoint is `127.0.0.1:9222`.
- [ ] The only profile is `~/agent-tools/.browser-profiles/chrome-automation`; no profile or port override is present.
- [ ] The supervisor asserts that exactly one CfT process uses that profile.
- [ ] One protected broker anchor is healthy before the phase. It will not be mutated.
- [ ] The runner creates/closes only its own page. It does not reuse or navigate a baseline page; generic `browser_harness new_tab` is not used.
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

- [ ] Receipt retained with acquisition, source actions, waits, health, target cleanup, and verified release.
- [ ] Terminal status: `completed` / `blocked` / `failed` / `cancelled`.
- [ ] No screening/import/final event occurred.

For **exploration**:

- [ ] One concise exploration log records real-page states, screenshots/DOM references, patches, and what works.
- [ ] No campaign gate or pilot acceptance is claimed.
- [ ] A frozen interaction recipe, implementation commit, and proposed evidence plan are ready—or remaining unknowns are explicit.

For **evidence**:

- [ ] Immutable evidence packet is complete.
- [ ] Controller can checkpoint passed/failed/dependent gates and carry forward unaffected exact-hash evidence.
- [ ] A technical failure returns the source to exploration rather than triggering selector debugging inside evidence mode.
- [ ] Only a review-affecting methodological decision is sent to the owner.
