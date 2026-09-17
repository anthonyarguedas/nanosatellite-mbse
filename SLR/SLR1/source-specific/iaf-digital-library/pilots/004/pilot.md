# Pilot 004: current schedule without proximity operators

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`, invoked through the shared browser wrapper and the strict complete-run contract.

Pilot 004 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 window. Every source artifact is non-mergeable.

## Objective

Test the IAF translation of the four partitions changed by commit `3194156e90497186664260a8e86435e78d2e2aa1`. Confirm that the five unchanged partitions retain their complete Pilot 003 source cells. Run every new cell for `BG1`, `BG2`, `BC1`, and `BT2` without proximity syntax, pair expansion, wildcards, or narrowing filters.

## Translation and plan

Every ordinary term uses one straight double-quoted token or ordered phrase. Uppercase `OR` joins alternatives. Whitespace joins required factors. The compound blocks are distributed into these branches before cell packing:

| Partition | Lossless source branches |
|---|---|
| `BG1` | `P AND G_model_fixed`, `P AND G_mission_exact`, `P AND G_mission AND M_B` |
| `BG2` | `P AND G_structure_fixed`, `P AND G_product_exact`, `P AND G_variation`, `P AND G_product AND M_B` |
| `BC1` | `P AND C1_fixed`, `P AND G_DSL` |
| `BT2` | `P AND M_B AND T_precise` |

The [cell plan](searches/cell-plan.json) packs each branch into deterministic conjunction cells below the 500-character source limit. Each branch has an exactly-once Cartesian coverage certificate. The union of its branches implements the protocol expression.

The complete current schedule needs 551 cells. The five unchanged partitions account for 465 cells. Their query strings match every strict Pilot 003 cell byte for byte, so the pilot carries that live evidence forward. The four changed partitions account for 86 newly run cells.

## Live run

The [run receipt](searches/run-receipt.json) records 86 complete source cells and no retained failure artifact. It covers 85 source attempts in the complete run and one successful cell retained from the bounded smoke run. Every cell used two full ordered passes, exact query readback, complete detail capture, stable paper IDs, and local date accounting. The source search had no date, language, event, type, access, peer-review, or full-text-availability restriction. No wildcard or controlled-vocabulary supplement was used.

| ID | Complete cells | Raw source-event total | Raw paper-ID union | Diagnostic-window union |
|---|---:|---:|---:|---:|
| `BG1` | 17 | 5 | 4 | 4 |
| `BG2` | 14 | 5 | 4 | 2 |
| `BC1` | 7 | 11 | 9 | 6 |
| `BT2` | 48 | 15 | 6 | 5 |

The totals are sums of overlapping cell events. The union columns use deduplicated stable IDs. Local date filtering excluded two event occurrences from `BG2`, four from `BC1`, and one from `BT2`. `BG1` had no date exclusion.

The fixed branch supplied every retained `BG1`, `BG2`, and `BC1` record. The mission, product, variation, and DSL expansion branches returned zero in this diagnostic window. `BT2` returned five retained IDs. The four changed partitions contain 17 record occurrences and 16 distinct retained IDs. `BG1` and `BC1` share one ID. No other changed-partition intersection occurred.

The [assessment](searches/assessment.json) compares these sets with the superseded Pilot 003 concepts. This comparison describes a protocol change. It is not a recall benchmark.

| ID | Superseded window union | Current window union | Current-only IDs |
|---|---:|---:|---:|
| `BG1` | 5 | 4 | 0 |
| `BG2` | 7 | 2 | 0 |
| `BC1` | 6 | 6 | 0 |
| `BT2` | 13 | 5 | 1 |

Current `BT2` adds `iaf-digital-library:IAC-2017:39760`. Four current `BT2` IDs also occurred under the superseded construction. The changed definition removes broad reuse, configuration, specialization, and adaptation pairs. It retains direct precise tailoring terms in the independent `M_B` context.

The [threshold report](searches/threshold-investigations.json) records raw unions of `4`, `4`, `9`, and `6`. No partition exceeded the 100-record investigation threshold.

## Result

Change the source translation and schedule.

Accept the deterministic branch and cell translation for the current schedule. Use quoted ordinary terms, uppercase `OR`, whitespace conjunction, and no proximity operator, pair expansion, wildcard, or local pair check. Preserve the 500-character cap, every cell total, and each stable-ID union.

Keep all existing filter decisions. The current complete schedule uses 551 cells. Pilot 003 supplies strict evidence for the 465 unchanged cells. Pilot 004 supplies strict evidence for the 86 changed cells. Final searches remain pending and must create new artifacts under `final-searches/`.

## Validation and reproduction

Review-specific scripts are under [`SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004`](../../scripts/iaf_digital_library_pilot004). The main commands are:

```bash
PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004/plan.py \
  --output-path SLR/SLR1/source-specific/iaf-digital-library/pilots/004/searches/cell-plan.json

uv run ~/agent-tools/internet/skills/browser/scripts/run_with_browser.py -- \
  python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004/run_cells.py

PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004/assess.py \
  --pilot-root SLR/SLR1/source-specific/iaf-digital-library/pilots/004 \
  --plan SLR/SLR1/source-specific/iaf-digital-library/pilots/004/searches/cell-plan.json \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/004/searches/assessment.json \
  --threshold-output SLR/SLR1/source-specific/iaf-digital-library/pilots/004/searches/threshold-investigations.json

PYTHONPATH=SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004 \
python3 SLR/SLR1/source-specific/iaf-digital-library/scripts/iaf_digital_library_pilot004/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/iaf-digital-library/pilots/004 \
  --guideline SLR/SLR1/source-specific/iaf-digital-library/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/iaf-digital-library/pilots/004/searches/validation-report.json
```
