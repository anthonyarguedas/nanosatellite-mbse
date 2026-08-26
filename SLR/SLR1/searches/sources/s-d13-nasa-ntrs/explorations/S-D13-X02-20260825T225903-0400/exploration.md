# NTRS post-submit reconciliation exploration

- **Session ID:** `S-D13-X02-20260825T225903-0400`
- **Source:** NASA Technical Reports Server (NTRS)
- **Started / ended:** 2026-08-25T22:59:03-04:00 / 2026-08-25T23:09:04-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `cc781ab2ed9120f6b2ade0181641da0b94f792db3dce4af8e2579600ce105fbc`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** live route completed; the documentation child later reached the finite lease deadline, after which guardian cleanup preserved the anchor and released the lease

## Question and starting state

X01 live-validated the patched Best Match and page-size-25 control projection but stopped after one submit before proving query delivery or a changed result. X02 tested the same exact 13-byte `nanosatellite` sentinel through the complete rendered SPA transition.

## Real-page observations

One fresh owned page opened the normal public NTRS root. Before submission, the page was normal and complete with one visible `Search all fields` input, one Search button, native **Best Match** normalized to canonical `Relevance`, and one semantic **Items per page** value of 25. The unfiltered state had range 1–25 of 646,789 with 25 visible result cards; no card text or identity was retained in a projection.

The agent filled exact `nanosatellite`, required exact visible readback, installed a bounded result-state mutation monitor, and clicked the visible Search button once. The first post-click sample retained the stale unfiltered range while the page was loading and rendered zero cards. The second sample, 1.52 seconds after the click, had loading clear, exact query readback, a changed range of 1–25 of **134**, 25 cards, enabled Next, native Best Match/canonical Relevance, and page size 25. Those aggregate facts reconciled internally. The operation retained no record fields or IDs and did not visit a citation.

The phase ran under process-scoped `caffeinate -dims` on AC power with no Sleep/Wake/DarkWake event. The Terra child completed the live summary but reached the 600-second guardian deadline while drafting documentation. The outer runner closed the lease-new page, preserved the single inert broker anchor, reported `cleanup=verified-clean`, found no orphan, and released the lease. This operator timeout occurred after the source transition was already recorded; it is not a provider failure.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---|---:|---|---|
| 1 | Opened the public root and reconciled Best Match/Relevance plus page size 25. | no | none | Patched pre-submit controls passed on the real page. |
| 2 | Filled exact `nanosatellite`, verified readback, and installed a bounded mutation monitor. | no | none | Ready for one guarded visible submit. |
| 3 | Clicked Search once and polled the same page at 0.5-second maximum cadence. | yes—exactly 1 | none | Loading retained the stale range with zero cards, then changed to a reconciled 1–25 of 134 with 25 cards. |
| 4 | Added the reusable transition finding to the restricted worktree domain note. | no | agent-tools commit `4abae7c2c8f06630a3a13bac66c21b251d5360ca` | No adapter behavior changed. |

## Working interaction recipe

1. Open `https://ntrs.nasa.gov/` on one owned page and wait for a normal complete root.
2. Require one visible all-fields input and Search button; native Best Match/canonical Relevance; and one semantic page size of 25.
3. Record the unfiltered aggregate, fill exact `nanosatellite`, require exact input readback, and click Search once.
4. Poll the same page for at most 90 seconds. Treat old range plus loading/zero cards as transitional.
5. Accept only after the query readback remains exact and a changed range/total, card count, Next state, ordering, and page size reconcile together, or after an exact native zero. Never read cards in count-only mode.

## Implementation

- **Frozen worktree commit:** `4abae7c2c8f06630a3a13bac66c21b251d5360ca`
- **NTRS control implementation introduced by:** `027f4e2d350e69074584edd2c28f66a92c06337f`
- **Frozen adapter SHA-256:** `a870b87473e2fd46e0b7081726e7c5a811342c4595b8713b5225d284e3460d0c`
- **Session change:** durable note only; `git diff --check` passed
- **Remaining unknowns:** deterministic adapter publication of the same aggregate receipt, partitions, dates, fields, details, stable IDs, pagination, and completeness

## Proposed evidence attempt

Freeze the held two-operation plan against the commit and adapter hash above: (1) one record-free rendered source-health operation; then (2) exact `nanosatellite` count-only with one submit, 90-second finite readiness, and zero retained records. Require exact visible query readback, native Best Match/canonical Relevance, page size 25, and one internally reconciled changed aggregate range/total or native zero. The current freshness comparator is total 134, but the evidence invariant is source-internal reconciliation rather than an assumption that a live database cannot grow. Any stale unfiltered state, missing/changed controls, conflicting range/total, challenge, timeout, cleanup failure, or adapter publication failure is `total=null` and returns the source to exploration. This exploration itself passes no gate.
