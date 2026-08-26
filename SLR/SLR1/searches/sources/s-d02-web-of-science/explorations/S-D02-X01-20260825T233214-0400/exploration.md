# Web of Science X01 setup incident

- **Session ID:** `S-D02-X01-20260825T233214-0400`
- **Source:** Web of Science Core Collection
- **Started / ended:** 2026-08-25T23:32:14-04:00 / 2026-08-25T23:42:15-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `c9cc38e18f38222062a13c2c97e4203304a5708b997e99d850f6426d8f264ac6`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** source-free setup failure followed by guardian timeout; no owned source page or source operation began

## Question and starting state

This was intended to be the first current-interface exploration of Core Collection Basic Search with the exact quoted sentinel `"CubeSat"`.

## Real-page observations

None. The generated exploration runner mistakenly assigned the seven-byte unquoted value `CubeSat` while asserting the controller-declared nine-byte quoted sentinel hash. That deterministic assertion failed before Playwright connected to CDP or created a page. The attached agent then inspected only local probe code and did not repair/relaunch the runner before the 600-second guardian deadline.

Accordingly, `allocation.source_phase_started=false`, owned pages created = 0, source navigations = 0, source submits = 0, and source total = `null`. This incident says nothing about WoS availability, controls, or query behavior and does not satisfy the required initial exploration.

The outer runner preserved the one inert broker anchor, found no lease-new page or orphan, recorded `cleanup=verified-clean`, and released the lease. The phase ran under process-scoped `caffeinate -dims` on AC power with no Sleep/Wake/DarkWake event.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---|---:|---|---|
| 1 | Validated local paths and drafted an owned-page runner. | no | none | Query-byte assertion was malformed. |
| 2 | Inspected local WoS projection and test code only. | no | none | No browser/source phase began before timeout. |

## Working interaction recipe

None established.

## Implementation

- **Committed change:** none
- **Failure class:** deterministic source-free query-byte mismatch in the generated exploration runner
- **Smallest correction:** use the exact nine-byte value `"CubeSat"` consistently in the runner and hash assertion before acquiring the next lease

## Proposed evidence attempt

**Not frozen.** Allocate a new exploration session after correcting the source-free runner. Do not allocate P01 from X01 and do not classify this setup incident as a WoS source failure.
