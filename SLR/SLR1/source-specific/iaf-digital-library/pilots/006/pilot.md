# Pilot 006: population wildcards across all partitions

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`, invoked through the shared browser wrapper and strict complete-run contract.

Pilot 006 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 window. Every source artifact is non-mergeable.

## Objective

Test the positive Pilot 005 population wildcard candidate in every current partition. Compare each complete raw and diagnostic-window stable-ID union with the explicit schedule. Approve wildcard use only when every explicit ID is retained and every wildcard-only ID is inspected.

## Candidate translation

The [cell plan](searches/cell-plan.json) replaces the 26 explicit population terms with these eight source atoms:

```text
CubeSat* OR "cube sat*" OR cube-sat* OR nanosat* OR nano-sat* OR
"nano sat*" OR SmallSat* OR "small sat*"
```

All other concept blocks retain their explicit ordinary terms. The plan uses the same branch distribution and lossless packing method as Pilot 004. Every branch certificate covers each candidate and ordinary factor tuple exactly once below the 500-character source limit.

The explicit schedule needs 551 cells. The wildcard candidate needs 158 cells.

| ID | Explicit cells | Wildcard cells | Reduction |
|---|---:|---:|---:|
| `A1` | 132 | 37 | 95 |
| `A2` | 173 | 48 | 125 |
| `A3` | 76 | 21 | 55 |
| `B1` | 11 | 4 | 7 |
| `B2` | 73 | 20 | 53 |
| `BG1` | 17 | 6 | 11 |
| `BG2` | 14 | 6 | 8 |
| `BC1` | 7 | 3 | 4 |
| `BT2` | 48 | 13 | 35 |
| **Total** | **551** | **158** | **393** |

Pilot 003 supplies the current explicit baselines for `A1` through `B2`. Pilot 004 supplies the current explicit baselines for `BG1`, `BG2`, `BC1`, and `BT2`. All comparisons use the same diagnostic window and exact stable paper IDs.

## Live run

The [run receipt](searches/run-receipt.json) records 158 complete cells from 161 source attempts. Every successful cell used exact query readback and two complete ordered capture passes. No source date, language, event, type, access, peer-review, or full-text-availability restriction was applied. No proximity operator, pair expansion, controlled-vocabulary supplement, or filter based on results was used.

Three first attempts stopped before exact executed query observation at `A1/cell-0015`, `A2/cell-0028`, and `B2/cell-0001`. Exact unchanged retries completed all three cells. The three non-mergeable failure artifacts remain in `searches/failures/`.

## Stable-ID comparison

| ID | Wildcard cells | Raw source-event total | Raw union | Window union | Explicit window union | Missing | Wildcard-only |
|---|---:|---:|---:|---:|---:|---:|---:|
| `A1` | 37 | 5 | 2 | 2 | 2 | 0 | 0 |
| `A2` | 48 | 24 | 12 | 11 | 11 | 0 | 0 |
| `A3` | 21 | 8 | 7 | 7 | 7 | 0 | 0 |
| `B1` | 4 | 72 | 42 | 39 | 39 | 0 | 0 |
| `B2` | 20 | 154 | 57 | 53 | 53 | 0 | 0 |
| `BG1` | 6 | 4 | 4 | 4 | 4 | 0 | 0 |
| `BG2` | 6 | 4 | 4 | 2 | 2 | 0 | 0 |
| `BC1` | 3 | 9 | 9 | 6 | 6 | 0 | 0 |
| `BT2` | 13 | 8 | 6 | 5 | 5 | 0 | 0 |

The [assessment](searches/assessment.json) confirms exact equality for every raw union and every diagnostic-window union. Across all nine partitions, the wildcard candidate missed no explicit ID and added no wildcard-only ID.

The [threshold report](searches/threshold-investigations.json) records a largest raw union of 57 and a largest diagnostic-window union of 53. No partition exceeded the 100-record investigation threshold.

## Result

Approve the wildcard translation with eight atoms for the IAF population block.

Use the wildcard population block in all nine IAF partitions. Keep explicit ordinary terms in every other block. The accepted plan reduces the schedule by 393 cells, from 551 to 158, a 71.32% reduction. It preserves every explicit raw and diagnostic-window stable-ID union in this pilot.

The explicit Pilot 004 plan remains the audit baseline and fallback. Pilot 006 changes the prospective source translation. It does not execute the final search. Final searches must create new artifacts under `final-searches/` with the accepted 158-cell plan and the final evidence cutoff.

## Validation and reproduction

Review-specific scripts are under [`SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006`](../../scripts/iaf_digital_library_pilot006). The main commands are:

```bash
PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006/build_plan.py \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/006/searches/cell-plan.json

uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser.py -- \
  python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006/run_cells.py

PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006/assess.py \
  --pilot-root SLR/SLR1/source-specific/iaf-digital-library/pilots/006 \
  --plan SLR/SLR1/source-specific/iaf-digital-library/pilots/006/searches/cell-plan.json \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/006/searches/assessment.json \
  --threshold-output SLR/SLR1/source-specific/iaf-digital-library/pilots/006/searches/threshold-investigations.json

PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot006/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/iaf-digital-library/pilots/006 \
  --guideline SLR/SLR1/source-specific/iaf-digital-library/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/006/searches/validation-report.json
```
