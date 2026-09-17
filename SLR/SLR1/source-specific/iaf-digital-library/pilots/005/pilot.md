# Pilot 005: positive trailing wildcard comparison

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`, invoked through the shared browser wrapper and strict complete-run contract.

Pilot 005 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 window. Every source artifact is non-mergeable. Pilot 006 later supersedes its prospective decision to retain the explicit schedule.

## Objective

Test documented trailing `*` on a non-zero review search. Compare complete stable-ID sets instead of count-only zero cells. Measure whether a wildcard population candidate with eight atoms retains the explicit population block with 26 terms in the positive `BG1` fixed branch.

## Predeclared comparison

The [event plan](searches/event-plan.json) uses the complete `G_model_fixed` context from Pilot 004. It groups the explicit population forms into these wildcard candidates:

| Explicit forms | Candidate |
|---|---|
| `CubeSat`, `CubeSats` | `CubeSat*` |
| `cube sat`, `cube sats`, `cube satellite`, `cube satellites` | `"cube sat*"` |
| `cube-sat`, `cube-sats` | `cube-sat*` |
| `nanosat`, `nanosats`, `nanosatellite`, `nanosatellites` | `nanosat*` |
| four `nano-sat...` forms | `nano-sat*` |
| four `nano sat...` forms | `"nano sat*"` |
| `SmallSat`, `SmallSats` | `SmallSat*` |
| four `small sat...` forms | `"small sat*"` |

Seven source events were predeclared:

- three fresh strict cells for the complete explicit baseline
- one cube family wildcard query
- one other family wildcard query
- two independent strict runs of the full wildcard query

Every event used exact query readback and two complete ordered capture passes. No source date, language, event, type, access, peer-review, or full-text-availability restriction was applied. No proximity operator, pair expansion, or controlled-vocabulary supplement was used.

## Results

The [run receipt](searches/run-receipt.json) records seven successful source attempts and no retained failure. Every wildcard event was non-zero. One of the three explicit packing cells returned zero, while its two-cell comparison union remained non-zero.

| Comparison | Explicit IDs | Wildcard IDs | Missing from wildcard | Wildcard-only |
|---|---:|---:|---:|---:|
| Cube family | 3 | 3 | 0 | 0 |
| Other population family | 2 | 2 | 0 | 0 |
| Full population | 4 | 4 | 0 | 0 |

Both full wildcard runs returned the same four IDs in the same order. The fresh explicit union also reproduced all four Pilot 004 IDs. No local date exclusion occurred.

The [assessment](searches/assessment.json) confirms exact set equality for all three positive comparisons. The full candidate shortened the unsubmitted branch expression from 773 to 447 characters. It reduced this tested branch from three source cells to one.

## Result

Document positive wildcard behavior and retain the current canonical schedule.

This pilot closes the zero-result evidence gap from Pilot 002. It confirms that the population wildcard candidate with eight atoms is a stable-ID equivalent of the explicit population block in this bounded, non-zero `BG1` fixed branch context.

The comparison does not isolate every wildcard atom and does not establish stable-ID equivalence across all nine partitions. Keep the current 551-cell explicit schedule as the canonical route. A future adoption pilot must predeclare the wildcard population block in every affected partition, run the complete candidate cell plan, and compare each partition union with the explicit plan.

## Validation and reproduction

Review-specific scripts are under [`SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005`](../../scripts/iaf_digital_library_pilot005). The main commands are:

```bash
PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005/build_plan.py \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/005/searches/event-plan.json

uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser.py -- \
  python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005/run_pilot.py

PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005/assess.py \
  --pilot-root SLR/SLR1/source-specific/iaf-digital-library/pilots/005 \
  --plan SLR/SLR1/source-specific/iaf-digital-library/pilots/005/searches/event-plan.json \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/005/searches/assessment.json

PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot005/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/iaf-digital-library/pilots/005 \
  --guideline SLR/SLR1/source-specific/iaf-digital-library/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/005/searches/validation-report.json
```
