# Pilot 004: rendered Advanced Search route

Required changes were applied in commit: cb6681e726b8722492d29322196c70d918c01db7

Export method: `~/agent-tools/internet/skills/browser/scripts/search_arxiv.py`

Pilot 004 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 window. Every source artifact is non-mergeable.

## Objective

Replace the prospective Atom API route with the rendered arXiv Advanced Search interface. Translate all nine post-proximity partitions without changing concept membership. Validate complete two-pass record capture and the mandatory automatic screenshots.

## Browser translation

Every ordinary block is one rendered `All fields` row. Each listed literal is enclosed in straight double quotes. Homogeneous uppercase `OR` joins the literals inside that row. Separate rows use the source's outer `AND` control.

The complete initial `A2` cell was rejected before a source total. The [original run receipt](searches/run-receipt-attempt2.json) records that failure. Its JSON was displaced during local failure-file organization. The exact unchanged cell was repeated once to retain a [failure reproduction](searches/failures/A2-direct-cell-failure-reproduction.NON_MERGEABLE_FAILURE.json). The [retention receipt](searches/failure-retention-receipt.json) records this history. The reproduction also has `total: null` and one configured-search screenshot. The [plan repair](searches/plan-repair-receipt.json) distributed only the unchanged `M_H OR M_B` factor:

```text
P AND E_F AND (M_H OR M_B)
=
(P AND E_F AND M_H) OR (P AND E_F AND M_B)
```

`BG1` and `BG2` use the same lossless distribution principle for their declared compound branches. The [revised event plan](searches/event-plan.json) contains 12 cells for the nine partitions. Every encoded request is at most 3,630 characters. It contains no Atom field prefix, proximity syntax, pair expansion, wildcard, or result-driven restriction.

## Runs and screenshots

The [completed run receipt](searches/run-receipt.json) covers all 12 cells. Each event used:

- the normal rendered Advanced Search form
- All fields for every query row
- all arXiv classifications with cross-lists included
- original submission date from 2011-01-01 through the inclusive pilot cutoff
- current result versions only
- submission date oldest-first ordering
- native rendered abstracts
- strict two-pass complete ordered-ID reconciliation

Adapter v8 automatically saved one full-page configured-search PNG before Search and one first-results PNG after exact result readback. All 24 PNGs are beside their JSON files. Their filenames, SHA-256 hashes, dimensions, and privacy flags are in each JSON and indexed in the [assessment](searches/assessment.json).

## Complete partition unions

The [union receipt](searches/partition-unions.json) deduplicates each partition on bare arXiv ID while retaining source-cell membership and visible version evidence.

| ID | Complete cells | Source events | Stable-ID union |
|---|---:|---:|---:|
| `A1` | 1 | 0 | 0 |
| `A2` | 2 | 0 | 0 |
| `A3` | 1 | 0 | 0 |
| `B1` | 1 | 6 | 6 |
| `B2` | 1 | 4 | 4 |
| `BG1` | 2 | 2 | 2 |
| `BG2` | 2 | 0 | 0 |
| `BC1` | 1 | 0 | 0 |
| `BT2` | 1 | 2 | 2 |

The nonzero unions are:

- `B1`: `1303.0881`, `1905.08839`, `2101.03035`, `2304.06482`, `2406.08342`, and `2602.16715`
- `B2`: `1108.4767`, `2203.14721`, `2309.07173`, and `2507.22198`
- `BG1`: `2406.10724` and `2411.10476`
- `BT2`: `2309.07173` and `2507.22198`

No cell exceeded the predeclared 1,000-record capacity. No precision filter was added.

## Transport comparison

The five partitions whose definitions were unchanged from Atom Pilot 003 gave the same bare-ID sets through both transports:

| ID | Browser | Atom Pilot 003 | Set result |
|---|---:|---:|---|
| `A1` | 0 | 0 | equal |
| `A2` | 0 | 0 | equal |
| `A3` | 0 | 0 | equal |
| `B1` | 6 | 6 | equal |
| `B2` | 4 | 4 | equal |

This bounded equality supports the browser replacement for the unchanged core definitions. It does not establish universal analyzer equivalence.

The four expansion definitions changed after Atom Pilot 003 removed proximity and pair expansion. Their result sets are descriptive only. The current browser `BG1` set is the two-record subset shared with the older Atom set. Current `BG2` and `BC1` are zero. Current `BT2` has two records and shares `2507.22198` with the older one-record set.

## Retained failures and rate control

Three failure histories remain separate from the successful cells:

1. [Attempt 1](searches/failures/A1-cell-01-of-01-attempt1.NON_MERGEABLE_FAILURE.json) exposed an adapter row-add wait-call defect before a source result. Adapter v8 was repaired and the same A1 cell then completed at zero.
2. The initial direct A2 request was rejected before a total. The exact failure reproduction confirmed the state after the original JSON was displaced. The lossless two-cell repair then completed at zero plus zero.
3. [Attempt 3](searches/failures/B2-cell-01-of-01-attempt3.NON_MERGEABLE_FAILURE.json) stopped during an unchanged strict event after both screenshots. A contemporaneous source check returned HTTP 429. The same B2 cell later completed at four after normal cooldown. No failed attempt was recoded as zero.

The revised runner waits 10 seconds between strict passes and 30 seconds between source events. These delays change no query or source control.

## Result

Change the source translation and schedule.

Use the rendered Advanced Search browser route for future arXiv searches. Use one homogeneous quoted OR block per All-fields row and outer AND controls between factors. Use 12 source cells across the nine partitions, with the documented two-cell unions for `A2`, `BG1`, and `BG2`. Require strict complete two-pass capture and both automatic screenshots for every cell.

The Atom route remains historical pilot evidence. It is not the prospective final-search transport.

## Validation and reproduction

The [non-mergeable marking receipt](searches/nonmergeable-marking.json) covers all 12 successful source artifacts. The [assessment](searches/assessment.json) reconciles records, screenshots, partition unions, and the bounded Atom comparison. The [validation report](searches/validation-report.json) checks the canonical term plan, source completion, all 24 PNG receipts, union arithmetic, and guideline synchronization.

Review-specific scripts are under [`SLR/SLR1/scripts/arxiv_pilot004`](../../../../scripts/arxiv_pilot004). The core commands are:

```bash
python3 SLR/SLR1/scripts/arxiv_pilot004/build_plan.py \
  --output SLR/SLR1/source-specific/arxiv/pilots/004/searches/event-plan.json

python3 SLR/SLR1/scripts/arxiv_pilot004/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/arxiv/pilots/004/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/arxiv/pilots/004 \
  --receipt SLR/SLR1/source-specific/arxiv/pilots/004/searches/run-receipt.json \
  --resume

python3 SLR/SLR1/scripts/arxiv_pilot004/mark_source_artifacts_nonmergeable.py \
  --pilot-root SLR/SLR1/source-specific/arxiv/pilots/004 \
  --receipt SLR/SLR1/source-specific/arxiv/pilots/004/searches/nonmergeable-marking.json

python3 SLR/SLR1/scripts/arxiv_pilot004/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/arxiv/pilots/004 \
  --event-plan SLR/SLR1/source-specific/arxiv/pilots/004/searches/event-plan.json \
  --atom-union SLR/SLR1/source-specific/arxiv/pilots/003/searches/partition-unions.json \
  --union-output SLR/SLR1/source-specific/arxiv/pilots/004/searches/partition-unions.json \
  --assessment-output SLR/SLR1/source-specific/arxiv/pilots/004/searches/assessment.json

python3 SLR/SLR1/scripts/arxiv_pilot004/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/arxiv/pilots/004 \
  --guideline SLR/SLR1/source-specific/arxiv/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/arxiv/pilots/004/searches/validation-report.json
```
