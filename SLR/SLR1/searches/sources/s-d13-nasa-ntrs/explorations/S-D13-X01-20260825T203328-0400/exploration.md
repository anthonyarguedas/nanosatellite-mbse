# NTRS rendered-control exploration

- **Session ID:** `S-D13-X01-20260825T203328-0400`
- **Source:** NASA Technical Reports Server (NTRS)
- **Started / ended:** 2026-08-25T20:34:12-04:00 / 2026-08-25T20:44:12-04:00
- **Controller / interactive agent:** Pi controller / Terra interactive browser agent
- **Lease and cleanup receipt:** [`browser-lease-receipt.json`](browser-lease-receipt.json), SHA-256 `b830854307007efda04912d2849432ab4e5914ba418869e5724a8427d25c720a`
- **Diagnostic only:** yes; no screening, import, gate claim, or final event
- **Terminal status:** lease timeout after one submit attempt and before post-submit reconciliation; lease-runner cleanup was verified

## Question and starting state

P05/P06 had collapsed all pre-submit control-parser failures into `ordering`, even though the parser also checked page size. X01 inspected the actual visible controls, patched their projection and error staging, then used the exact 13-byte `nanosatellite` sentinel once.

## Real-page observations

The normal public root exposed one `Search all fields` input and one visible **Search** button. The page already rendered an unfiltered result set before any query. Its actual default ordering was one Angular Material combobox labelled **Best Match**. The control's technical descriptors did not contain `sort` or `order`, so the previous selector omitted it. This—not a duplicate page-size state—explains the pre-submit failure reproduced from the current interface.

The page-size surface was one visible Angular Material **Items per page** combobox selected at `25`. Adjacent paginator buttons carried page/item accessibility text but were not comboboxes. No duplicate semantic page-size control was observed. A bounded projection retained control categories/counts only; screenshots remain restricted because the unfiltered page contained record metadata.

The patched form projection was evaluated on the same page before submission. It returned one canonical `Relevance` ordering (the adapter's existing canonical name for native Best Match) and page size 25; `parse_visible_controls` accepted both as verified. The sentinel was then filled with exact readback and the visible Search control was clicked once. Two seconds later the page still showed the prior unfiltered range/cards beside the nonempty input. No post-submit projection was completed before the ten-minute lease deadline, so query delivery, exact result echo, and a changed aggregate total remain unproven; the source total is `null`, not the stale unfiltered total.

The guardian stopped the attached child at the finite deadline. The lease runner closed the new target, preserved the broker anchor, reported no orphan, and released the lease with `cleanup=verified-clean`. The exact phase contained zero Sleep/Wake/DarkWake events under `caffeinate -dims`.

A later controller review found that macOS System Information launched at 20:43:58, inside this phase, and remained open until the user closed it. The generic browser helper then in use populated CDP `nativeVirtualKeyCode` with Windows key values, the same defect class previously known to open About This Mac. The discarded Terra log prevents binding the launch to one recovered call, so this is a controller-technical side effect rather than a source claim. [`controller-side-effect-review.json`](controller-side-effect-review.json) records the repair commits and focused regression check.

## Iterations

| Iteration | Visible action or observation | Source submit? | Technical change | Live result |
|---|---|---:|---|---|
| 1 | Opened the public rendered root and projected all visible input/combobox/paginator roles. | no | none | Best Match and one page-size-25 combobox identified. |
| 2 | Opened the ordering surface only to classify its native selected label/options, then dismissed it. | no | none | Best Match confirmed as the default ordering label. |
| 3 | Patched semantic ordering/page-size projection and separate error stages; reevaluated the updated form script and parser on the same page. | no | agent-tools commit `027f4e2d350e69074584edd2c28f66a92c06337f` | Ordering and page size both verified pre-submit. |
| 4 | Filled exact `nanosatellite` and clicked visible Search once. | yes—one attempted submit | none | Input remained exact, but changed query result/total was not reconciled before timeout. |

## Working interaction recipe

The live-proven pre-submit recipe is: open the normal public root; locate the unique `Search all fields` input and Search button; treat native **Best Match** as the normal default ordering; and require one semantic numeric page-size value, currently 25. Native/framework duplicates may collapse only when their selected values agree. Conflicting ordering or page sizes fail closed, and page-size failures now report `page_size`, not `ordering`.

A complete search recipe is not yet proven because the post-submit transition was not projected. A retained input value beside the prior unfiltered range/cards is not query-echo or count evidence.

## Implementation

- **Adapter/helper commit:** `027f4e2d350e69074584edd2c28f66a92c06337f`
- **Changes:** Best Match recognition; duplicate-equal page-size projection; conflict preservation; distinct ordering/page-size exception stages; NTRS domain note
- **Minimal changed-path check:** three targeted NTRS tests passed; adapter `py_compile` and `git diff --check` passed
- **Live validation:** updated form projection and parser passed on the owned pre-submit page; post-submit parser was not run
- **Remaining unknowns:** submit transition, exact query echo, nanosatellite total/range or explicit zero, and post-submit control reconciliation

## Proposed evidence attempt

**Not frozen.** The later two-operation health-plus-sentinel evidence plan remains held because X01 did not reconcile a post-submit aggregate result. A future exploration must use the same visible recipe, submit exact `nanosatellite` once, wait through the bounded SPA transition, and require an exact query echo, native Best Match/default ordering, one semantic page size, and a changed reconciled total/range or explicit zero. A stale unfiltered page, timeout, control conflict, or missing echo remains `total=null`; no prefix may be retained.
