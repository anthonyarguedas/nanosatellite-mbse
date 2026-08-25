# Shared CfT browser live-phase checklist — S-D08-P01-20260825T132822-0400

## 1. Offline and authorization

- [x] Pilot/phase ID: `S-D08-P01-20260825T132822-0400`
- [x] Campaign and decision class: `S-D08-C01-20260825T132822-0400` / `controller_technical`
- [x] Offline reading, exact query/operation planning, source-free tests, output planning, and rights/cleanup planning complete.
- [x] OWNER: `S-D08-P01-20260825T132822-0400`
- [x] SOURCE: `proquest-pqdt`
- [x] Immutable receipt PATH: `SLR/SLR1/searches/sources/s-d08-proquest-pqdt/pilots/S-D08-P01-20260825T132822-0400/receipts/shared-lease.json`
- [x] Global pacing: sequential; no busy reissue; no challenge reissue.
- [x] Finite wait/readiness policy: adapter finite 30-second readiness/interaction timeout; no wrapper `--wait`; no source-operation retry.

## 2. Lease and browser boundary

- [x] Whole phase used the required `run_with_browser_lease.py` wrapper with `--lease-timeout 600`.
- [x] Only endpoint: `http://127.0.0.1:9222`.
- [x] Only supervisor profile: `~/agent-tools/.browser-profiles/chrome-automation`; no override.
- [x] One CfT process, one protected inert broker anchor; anchor not navigated, closed, or mutated.
- [x] Adapter/probe-owned page only; generic `browser_harness new_tab` not used.
- [x] macOS phase wrapped by process-scoped `caffeinate -dims`; AC power, 100% battery, no observed sleep/wake event.

## 3. Provenance and health

| Field | Before | After | Evidence |
| --- | --- | --- | --- |
| Lease | free; acquisition attempted | released; `verified-clean` | `receipts/shared-lease.json`, `browser-postflight.json` |
| Browser epoch | `uaShS7G1rXVB9KQFA1A6iw6LznsLaesk` | `uaShS7G1rXVB9KQFA1A6iw6LznsLaesk` | `preflight.json`, `browser-postflight.json` |
| Profile/process | canonical profile; one CfT process | canonical profile; one CfT process | `preflight.json`, `browser-postflight.json` |
| CfT version | runtime/disk `152.0.7977.54` | runtime/disk `152.0.7977.54` | `preflight.json`, `browser-postflight.json` |
| Endpoint/anchor | `127.0.0.1:9222`; one inert anchor | same; anchor preserved | `preflight.json`, `browser-postflight.json` |
| Sleep protection | `caffeinate -dims` planned/wrapped | no sleep/wake observed | `browser-postflight.json` |
| Owned target cleanup | no identity retained | wrapper `verified-clean`; anchor preserved | `browser-cleanup-receipt.json`, `browser-postflight.json` |

## 4. Condition, cancellation, and cleanup

- [x] Terminal condition: `technical_observability_failure`.
- [x] Challenge: `unknown`; busy: `unknown`. No access-control action or automatic retry.
- [x] Source operation cap: 16 predeclared; O01 performed and failed; O02–O16 not run.
- [x] No source-operation reissue, screening, candidate import, or final event.
- [x] No operator cancellation; all child processes collected.
- [x] Adapter-owned cleanup, broker-anchor preservation, and shared-lease release verified.

## 5. Outcome and handoff

- [x] Immutable operation/incident evidence retained with safe hashes; no page or record content retained.
- [x] Campaign checkpoint records null source total and zero retrieved/imported records.
- [x] Terminal summary: P01 failed at O01; the runner discarded the child diagnostic; no successor reissued O01 within P01.
- [x] Code issue recorded; no methodological change proposed.
