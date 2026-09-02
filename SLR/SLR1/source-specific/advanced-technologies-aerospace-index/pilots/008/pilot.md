# Pilot 008: bounded wildcard schedule

Required changes were applied in commit: NA

Export method: adapter version 6 at `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

Pilot 008 is diagnostic. It is not a final search. It uses the labelled 2011-01-01 through 2026-08-29 pilot window. Every source artifact is nonmergeable.

## Objectives

1. Pilot all nine schedule partitions from commit `3194156e90497186664260a8e86435e78d2e2aa1` without proximity or pair expansion.
2. Use bounded ProQuest wildcards for every ordinary variant family with one safe common source stem.
3. Compare complete literal and wildcard stable ID sets.
4. Confirm that the adapter saves one configured search screenshot and one first results screenshot beside every successful JSON.

The [event plan](searches/event-plan.json) declared all 18 events before source execution. It pairs one strict literal event and one strict wildcard event for each partition.

## Translation

The literal baseline is the accepted Pilot 007 translation. Every ordinary term uses:

```text
(NOFT("literal") OR IF.EXACT("literal"))
```

The candidate uses the smallest ProQuest `[*n]` suffix bound that covers each declared variant family in `NOFT`. It preserves every replaced exact `IF` alternative. For example:

```text
(NOFT(CubeSat[*1]) OR IF.EXACT("CubeSat") OR IF.EXACT("CubeSats"))
```

Multiword entries remain ordered quoted phrases, such as `NOFT("power system[*1]")` and `NOFT("state[*1] of charge")`. The map includes regular number forms and bounded inflection groups such as `nanosat[*7]`, `tailor[*3]`, and `instantiat[*3]`. Singleton terms and variants without one safe common stem stay literal.

The [query module](../../../../scripts/atai_pilot008/queries.py) declares 128 wildcard families covering 292 explicit term occurrences across the ordinary blocks. Exact `IF.EXACT` terms remain literal because Pilot 006 proved that `IF` adds records outside `NOFT`. The candidate does not assume wildcard behavior inside the exact indexed term operator.

All complete expressions preserve the current compound definitions:

- `G_model_fixed OR G_mission_exact OR (G_mission AND M_B)`
- `G_structure_fixed OR G_product_exact OR G_variation OR (G_product AND M_B)`
- `C1_fixed OR G_DSL`
- `P AND M_B AND T_precise` for `BT2`

## Complete comparison

Each source event used ATAI alone, exact `LA(English)`, the inclusive publication date window, oldest first ordering, and spelling, form, and display variants off. It applied no type, peer review, full text, access, or controlled vocabulary restriction. Each successful event completed the adapter's strict two full record pass contract.

| Partition | Literal total | Wildcard total | Literal characters | Wildcard characters | Reduction | Wildcard operators | Ordered stable IDs |
|---|---:|---:|---:|---:|---:|---:|---|
| `A1` | 0 | 0 | 7,662 | 6,523 | 1,139 | 38 | equal |
| `A2` | 5 | 5 | 9,528 | 8,038 | 1,490 | 48 | equal |
| `A3` | 1 | 1 | 6,012 | 4,656 | 1,356 | 45 | equal |
| `B1` | 25 | 25 | 5,177 | 4,541 | 636 | 20 | equal |
| `B2` | 34 | 34 | 6,242 | 4,639 | 1,603 | 47 | equal |
| `BG1` | 2 | 2 | 6,092 | 4,733 | 1,359 | 42 | equal |
| `BG2` | 7 | 7 | 4,898 | 3,798 | 1,100 | 36 | equal |
| `BC1` | 2 | 2 | 3,439 | 2,755 | 684 | 25 | equal |
| `BT2` | 2 | 2 | 5,240 | 3,772 | 1,468 | 34 | equal |

Every wildcard partition has the same total, stable ID set, and source order as its adjacent literal partition. No literal ID is missing. No wildcard only record exists. The literal and wildcard unions each contain the same 60 distinct ATAI IDs.

The [assessment](searches/assessment.json) records every ordered set and accepts the bounded wildcard translation.

## Mandatory screenshots

Adapter version 6 exposes no screenshot opt out. It derives `<stem>.search-page.png` and `<stem>.results-page.png` from every JSON output path. The JSON stores both filenames, SHA-256 values, dimensions, and privacy state.

All 18 successful events have both sibling PNGs. The assessment verifies 36 successful event screenshots. The screenshots remain generated local evidence under the repository image ignore rule.

## Retained failures

The [failure history](searches/failure-history.json) preserves six stopped attempts and five nonmergeable source error artifacts:

- one literal `B2` event reached the results page, then a record detail did not become ready before timeout. Its search and results screenshots are retained.
- three fresh shared browser events stopped before source execution because concurrent Chrome target identity evidence was unavailable.
- one local fresh browser command used an incorrect executable path and stopped before browser start.
- one corrected isolated fresh browser opened Chrome but did not reach a normal ProQuest page before timeout.

Fresh unchanged shared browser events later completed. No failed attempt contributes a source total, stable ID, or translation decision. The final [run receipt](searches/run-receipt.json) covers exactly the 18 successful planned events. The [nonmergeable marking receipt](searches/nonmergeable-marking.json) covers those 18 successes and all five retained source error artifacts.

## Decision

Accept and prefer the bounded wildcard family map for all nine ATAI schedule partitions. Keep every exact `IF.EXACT` alternative literal. Keep singleton and unsafe stem alternatives literal. Use one direct fully parenthesized query per partition.

This decision is bounded to the tested schedule and controls. A later corpus update can produce a new suffix completion. Normal screening remains authoritative, and future unexpected wildcard only records require concept review.

## Validation and reproduction

The [validation report](searches/validation-report.json) checks protocol membership, the predeclared query plan, exact source readback, complete records, ordered set equality, mandatory screenshots, retained failures, nonmergeable status, and guideline synchronization.

Run from the repository root:

```bash
PYTHONPATH=SLR/SLR1/scripts/atai_pilot008 \
python3 SLR/SLR1/scripts/atai_pilot008/build_plan.py

caffeinate -dims uv run \
  "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  python3 SLR/SLR1/scripts/atai_pilot008/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008 \
  --receipt SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008/searches/run-receipt.json

PYTHONPATH=SLR/SLR1/scripts/atai_pilot008 \
python3 SLR/SLR1/scripts/atai_pilot008/mark_source_artifacts_nonmergeable.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008 \
  --receipt SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008/searches/nonmergeable-marking.json

PYTHONPATH=SLR/SLR1/scripts/atai_pilot008 \
python3 SLR/SLR1/scripts/atai_pilot008/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008 \
  --output SLR/SLR1/source-specific/advanced-technologies-aerospace-index/pilots/008/searches/assessment.json

PYTHONPATH=SLR/SLR1/scripts/atai_pilot008 \
python3 SLR/SLR1/scripts/atai_pilot008/validate_pilot.py
```
