# OATD visible-composer exploration

- **Session ID:** `S-D09-X01-20260825T200356-0400`
- **Source:** Open Access Theses and Dissertations (OATD)
- **Started / ended:** 2026-08-25T20:05:26-04:00 / 2026-08-25T20:15:26-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `cc458a378fd01e2cb076d6cf05b7746f6ec941c0dedcf610261a0c06bb6eb10c`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** technically blocked before submission; the lease deadline later stopped the agent after owned-page cleanup, and the receipt records `cleanup=verified-clean` and `state=released`

## Question and starting state

X00 showed that the hidden home-page advanced form was the wrong target. This session tested the normal visible `/oatd/search-composer` route and the permitted untouched challenge transition before attempting the `CubeSat` title-field sentinel.

## Real-page observations

One distinct owned page navigated directly to the composer route. A restricted screenshot showed a visible verification challenge. No access-control element was clicked, reloaded, solved, or bypassed. The challenge cleared without interaction almost immediately after passive polling began, but the same page entered OATD's ordinary **Please slow down** busy rendering instead of exposing the composer.

The busy state was then observed passively for 30 seconds at 0.2-second cadence (143 polls). It did not expose one visible composer form, `box1`, `field1`, or native submitter. The bounded projection retained only route categories, booleans, and counts; no raw DOM or page/result text was retained. Source submits and reissues were both zero. No result card, Record Details page, record, or candidate datum was inspected.

The phase ran under process-scoped `caffeinate -dims`; the exact phase window contained zero Sleep/Wake/DarkWake events. The protected one-page baseline remained intact, the owned page was closed without switching targets, and the lease runner independently reported verified cleanup and release.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---|---:|---|---|
| 1 | Opened the normal visible composer route on one owned page and captured the initial state. | no | none | Verification challenge visible. |
| 2 | Left the page untouched and passively polled under the 30-second challenge allowance. | no | none | Challenge transitioned without interaction to an ordinary busy page. |
| 3 | Passively observed the same busy page for 30 seconds; no reissue was made. | no | none | Composer controls remained absent; route could not be exercised. |
| 4 | Replaced the probe's home-page navigation and home-route safety invariant with the canonical visible composer route; updated its focused tests and durable domain note. | no | review commit `f51f81293153dfbaa8526e9393677908497f2263`; agent-tools commit `1d7474ccf4fa94958e85bf765734adc6fb7372b9` | The focused 46-test probe suite passed, but the live busy state prevented form or submission validation. |

## Working interaction recipe

No working submission recipe was established. The route boundary is now explicit: open `https://oatd.org/oatd/search-composer` directly, allow at most 30 seconds of untouched passive challenge polling, and classify a subsequent **Please slow down** page as busy rather than a form-mapping failure or zero. The intended visible selectors remain `box1`, `field1`, and one visible native submitter inside the canonical GET form, but this session did not observe them and therefore does not freeze them as live-proven selectors.

## Implementation

- **Proposed probe commit:** `f51f81293153dfbaa8526e9393677908497f2263` (`oatd_advanced_form_probe.py` schema v4)
- **Durable browser-note commit:** `1d7474ccf4fa94958e85bf765734adc6fb7372b9`
- **Minimal changed-path check:** `python3 SLR/SLR1/scripts/test_oatd_advanced_form_probe.py` — 46 tests passed; `git diff --check` passed
- **Live validation status:** blocked before the composer appeared; the patch is not evidence-ready
- **Remaining unknowns:** visible title-field value, unique submitter, native readback/submission, aggregate result reconciliation, and any busy reissue behavior

## Proposed evidence attempt

**Not frozen.** The held P05 design must not be allocated from this session because exploration did not demonstrate a working form or aggregate result. After a later exploration reaches and live-validates the visible composer, the candidate deterministic plan remains one title-field count-only operation using the exact held sentinel, a 30-second untouched challenge maximum, and only the already declared 30/60-second same-page busy policy. It must require exact form/query/field readback, one guarded native submit, a reconciled aggregate total or explicit native zero, zero retained records, and null failure on any challenge, busy exhaustion, control, route, total, or cleanup discrepancy.
