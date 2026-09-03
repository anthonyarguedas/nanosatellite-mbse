# Pilot 006: exact card-ID gate union

Required changes were applied in commit: 38aedc3de4731e0da5f063a053e92ebd88a84db0

Export method: the read-only card traversal in `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`, invoked by the [Pilot 006 runner](../../../../scripts/oatd_pilot006/run_pilot.py).

## Objective

Determine the exact deduplicated stable-ID union of the eight Pilot 005 gates before opening any Record Details page. This is a diagnostic pilot. It is not a final search.

## Method

The [event plan](searches/event-plan.json) retains the exact eight-gate algebraic union, English metadata control, 2011 through 2026 date bounds, native 30-record pages, and source-rendered relevance order. It imposed a 30-minute cooldown after Pilot 005, 60 seconds between each gate's passes, and 120 seconds between gates. One explicit busy response could receive one retry after 120 seconds. An HTTP 504 received no automatic retry.

Each gate used two complete rendered card traversals. The runner required equal stable-ID sets across the two passes. It persisted only rank, stable OATD Record ID, and card title. It retained no query URL, Record Details parameter, cookie, browser target, or response body. No Record Details page was requested.

The first invocation was stopped while it was still waiting for the predeclared cooldown. It made no source request and created no artifact. The unchanged plan then ran after the cooldown elapsed.

## Results

All eight gates completed both passes without a busy retry or native-order drift. Every total matched Pilot 005.

| Gate | Total | Stable set reconciled |
|---|---:|---|
| `G1-MH` | 16 | Yes |
| `G2A-MB-EF` | 2 | Yes |
| `G2B-MB-EH` | 2 | Yes |
| `G2C-MB-R` | 10 | Yes |
| `G2D-MB-T` | 0 | Yes |
| `G3-GMODEL` | 0 | Yes |
| `G4-GSTRUCTURE` | 3 | Yes |
| `G5-C1` | 1 | Yes |

The 34 gate occurrences deduplicated to 26 stable source IDs. Eight occurrences were cross-gate duplicates. This is a 97.9183% candidate reduction from the dated 1,249-record `P`-only population.

The [reconciliation](searches/reconciliation.json) preserves every ID, title, gate membership, and rank in both passes. It records stable and ordered union hashes. Nine of the 26 IDs have validated detail records in the partial Pilot 004 checkpoint. Seventeen do not. This pilot does not approve those nine earlier records for a final search.

Each gate JSON and its two screenshots are bound by a terminal marker. The [run receipt](searches/run-receipt.json) binds all eight events and the reconciliation. The [assessment](searches/assessment.json) records the decision and accounting. The [validation report](searches/validation-report.json) revalidated 16 complete source passes, 16 screenshots, eight terminal markers, all ID sets, and the exact union.

## Result

Accept the eight-gate card-ID route for a bounded detail-hydration pilot. Hydrate each of the 26 stable IDs once, then obtain fresh confirming gate snapshots before publishing any complete source artifact. Keep the nine Pilot 004 detail records diagnostic unless a later plan explicitly validates and adopts them.

Pilot 006 establishes the exact dated candidate set. It retains no full records and creates no final-search artifact.
