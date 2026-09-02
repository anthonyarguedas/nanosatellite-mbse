# Pilot 006: native Year and rendered-state investigation

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Pilot 006 is diagnostic. It is not a final search. It uses native inclusive Publication Year `2011_2026_Year`. The 2026-08-29 diagnostic cutoff remains separate from that year precision window.

## Objective

Investigate the Pilot 005 native Year failures and the `BG1` strict rendered-state failure. Test two bounded hypotheses:

1. IEEE disables Apply when the complete available result interval already lies inside the requested window, so filling broader values is an unnecessary interaction.
2. Strict pass one can expose a contained result interval while the explicit verification route exposes the exact requested token. These are equivalent forms of evidence for one requested window.

## Repairs under test

Adapter v9 performs one passive check before touching the Year widget. It accepts no Apply transition only when one visible disabled widget reports a valid interval fully contained in the requested inclusive window. It records the requested window and result interval separately. An uncontained interval, enabled staged control, ambiguous widget, retained-value mismatch, or changed native token remains fatal.

Strict reconciliation now compares semantic controls after each pass independently validates its native representation. The pass representation remains descriptive evidence and cannot replace the requested window.

The [predeclared plan](searches/event-plan.json) contains six count events and four changed-partition strict events. Strict events skipped full document pages to isolate rendered controls, pagination, and Article Numbers. No failed event was retried.

## Native Year findings

Five events that had failed during Year fill or Apply in Pilot 005 completed without filling either Year input or clicking Apply:

| Event | Total | Contained complete result interval |
|---|---:|---|
| `A1` pass 2 | 5 | `2013_2024_Year` |
| `B1` | 74 | `2012_2026_Year` |
| `BG2` | 11 | `2014_2026_Year` |
| `BC1` | 28 | `2011_2026_Year` |
| `BT2` | 9 | `2015_2026_Year` |

Each interval lies inside `2011_2026_Year`. The source left Apply disabled. The adapter retained the exact query, total, cards, sort, scope, access state, and contained interval. It never relabelled the interval as an applied native token.

This confirms that the Pilot 005 start resets and disabled Apply state were no-op control interactions. They did not show that IEEE rejected the requested scientific window.

## Strict findings

| Partition | Outcome | Article Numbers |
|---|---:|---|
| `BG1` | complete, 1 | `6161179` |
| `BG2` | rendered-state failure, `null` | `null` |
| `BC1` | rendered-state failure, `null` | `null` |
| `BT2` | complete, 9 | `7119221`, `9172720`, `10516429`, `10534509`, `10822287`, `10786913`, `11357143`, `11370070`, `11519874` |

`BG1` completed both strict passes after semantic year reconciliation. This repairs the Pilot 005 failure after one pass.

`BG2` and `BC1` passed the Year check, then failed before strict pass one. Their final source states retained valid native 25-row paging. `BG2` already showed all 11 records. `BC1` showed rows 1 through 25 of 28. The adapter had forced a preferred 100-row transition even though current native pagination fit the declared 20-page bound. Pilot 007 tests this separate rendered-state diagnosis.

## A1 failure classification

`A1` pass 1 failed before an adapter-owned page opened. It recorded no navigation, query echo, source route, cards, or Year state. Cleanup was `not_needed`. The historical fallback labelled this `rendered_state`, but no rendered source state existed. Adapter v9 now classifies this condition as `browser_open`. The independent `A1` pass 2 reached IEEE and returned the expected total of 5.

## Receipt correction

The [raw run receipt](searches/run-receipt-raw.json) counted five successes because its local classifier expected detailed strict fields that safe output compaction removed. The [reconciled receipt](searches/run-receipt.json) uses the retained source status, complete record count, PRISMA completion state, and valid terminal marker. It records seven successful source events and three explicit failures. This reconciliation performed no source execution.

The [assessment](searches/assessment.json) hashes all ten source artifacts and records the failure evidence used above.

## Result

Change the native Year handling and strict control reconciliation.

Accept a disabled contained result interval as proof that Year Apply would be a no-op. Keep the requested window and result interval distinct. Preserve every fail-closed boundary for a real narrowing request.

Classify the `A1` event as a browser-open failure. Keep `BG2` and `BC1` null in Pilot 006. Their page-size diagnosis requires the separately predeclared Pilot 007 evidence.

Pilot 006 does not authorize a final search. It uses year precision and leaves the exact publication-day window untested.

## Reproduction

```bash
python3 SLR/SLR1/scripts/ieee_xplore_pilot006/build_plan.py \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/006/searches/event-plan.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot006/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/ieee-xplore/pilots/006/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/006 \
  --receipt SLR/SLR1/source-specific/ieee-xplore/pilots/006/searches/run-receipt.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot006/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/006 \
  --raw-run-receipt SLR/SLR1/source-specific/ieee-xplore/pilots/006/searches/run-receipt-raw.json \
  --run-receipt-output SLR/SLR1/source-specific/ieee-xplore/pilots/006/searches/run-receipt.json \
  --assessment-output SLR/SLR1/source-specific/ieee-xplore/pilots/006/searches/assessment.json
```
