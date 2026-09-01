# Pilot 005: schedule without proximity operators

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

Pilot 005 is diagnostic. It is not a final search. It uses the native inclusive Publication Year `2011` through `2026` control. The diagnostic cutoff is 2026-08-29 and remains separate from that year precision window. Every source artifact is non-mergeable.

## Objective

Test the direct IEEE Xplore translation of the schedule of nine partitions introduced in commit `3194156e90497186664260a8e86435e78d2e2aa1`. Submit every complete expression without proximity syntax or pair expansion. Repeat every source total and attempt strict two-pass capture for `BG1`, `BG2`, `BC1`, and `BT2`.

## Translation

Every ordinary term uses one quoted All Metadata atom:

```text
("All Metadata":"literal")
```

The changed blocks preserve the protocol's nested Boolean definitions:

| Block or partition | Source construction |
|---|---|
| `G_model` | `F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))` |
| `G_structure` | `F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))` |
| `C1` | `F(C1_fixed) OR F(G_DSL)` |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` |

The [predeclared event plan](searches/event-plan.json) contains every expression, term count, query hash, and control. Each partition uses one source expression. The queries range from 2,169 to 5,947 characters. They contain no proximity operator, pair expansion, wildcard, language control, type control, access restriction, Date Added control, or controlled-vocabulary supplement.

## Runs

The plan contains 22 source events:

- two independent count-only events for each of the nine partitions
- one strict complete event for each changed partition

Every event requested Documents, All Results, oldest-first ordering, and native Publication Year `2011_2026_Year`. The adapter was allowed one visible Apply transition. No failed event was retried, forced through the DOM, or replaced by an unbounded search.

The [raw run receipt](searches/run-receipt-raw.json) misclassified the six successful compact artifacts because its local classifier expected fields removed by safe output compaction and expected terminal markers on failed artifacts. This classifier defect did not affect an adapter command or source artifact. The [reconciled run receipt](searches/run-receipt.json) was built by reusing all 22 existing artifacts with no source execution. The [assessment](searches/assessment.json) records both receipt hashes and the zero-rerun boundary.

## Query acceptance and totals

IEEE produced an exact query echo for every complete direct expression at least once. This supports one direct source expression per partition. It does not establish a complete date-controlled result.

| Partition | Pass 1 | Pass 2 | Repeated total |
|---|---:|---:|---:|
| `A1` | `null` | `null` | `null` |
| `A2` | `null` | `null` | `null` |
| `A3` | 6 | 6 | 6 |
| `B1` | `null` | `null` | `null` |
| `B2` | 131 | 131 | 131 |
| `BG1` | 1 | 1 | 1 |
| `BG2` | `null` | `null` | `null` |
| `BC1` | `null` | `null` | `null` |
| `BT2` | `null` | `null` | `null` |

The unchanged `A3` and `B2` totals match Pilot 004. The current `BG1` total equals the superseded Pilot 004 total of one. Pilot 005 captured no current `BG1` Article Number, so that equal total does not prove set equality.

## Changed partition strict outcomes

| Partition | Strict passes completed before failure | Outcome |
|---|---:|---|
| `BG1` | 1 | rendered-state failure, `total: null` |
| `BG2` | 0 | native Year start readback failure, `total: null` |
| `BC1` | 0 | both Year inputs matched but Apply remained disabled, `total: null` |
| `BT2` | 0 | native Year start readback failure, `total: null` |

No changed partition has a current stable-ID union. Pilot 004 also had null complete unions for `BG2`, `BC1`, and `BT2`. Its partial cell captures remain historical evidence and cannot be compared with a null current partition.

## Failure accounting and artifact integrity

The 22 events produced six successful count artifacts and 16 explicit failures. Twelve failures occurred at Year fill or Apply enable readback. Two `A2` failures occurred during initial result-form readiness. Two failures occurred at rendered state, including the `BG1` strict event after its first complete pass.

All 22 JSON artifacts have `do_not_merge: true` and are hashed in the assessment. The six successful artifacts have valid adapter-generated `IEEE_COMMIT` sidecars. The adapter failure path retained the 16 failure JSON files without terminal sidecars. This did not turn a failure into a result. The missing failure sidecars mean the plan's all-artifact marker check was not met.

## Result

Change the source translation and schedule.

Use one direct All Metadata expression for each partition in the schedule without proximity operators. Render the shared compound blocks with nested `AND` and `OR`. Use no proximity operator, pair expansion, wildcard, or split based on results.

Document the source control limitation. Pilot 005 did not validate a complete date-controlled schedule. Only `A3`, `B2`, and `BG1` returned repeated totals. All four changed strict events remain null. IEEE Xplore is unresolved and no Pilot 005 artifact belongs in `final-searches/`.

## Validation and reproduction

The [validation report](searches/validation-report.json) checks the canonical term counts, predeclared queries, all 22 source artifacts, six successful commit markers, retained failures, repeated totals, strict nulls, documentation links, and guideline synchronization.

Review-specific scripts are under [`SLR/SLR1/scripts/ieee_xplore_pilot005`](../../../../scripts/ieee_xplore_pilot005). The core commands are:

```bash
python3 SLR/SLR1/scripts/ieee_xplore_pilot005/build_plan.py \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/event-plan.json

python3 SLR/SLR1/scripts/ieee_xplore_pilot005/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/005 \
  --receipt SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/run-receipt.json

PYTHONPATH=SLR/SLR1/scripts/ieee_xplore_pilot005 \
python3 SLR/SLR1/scripts/ieee_xplore_pilot005/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/005 \
  --plan SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/event-plan.json \
  --raw-run-receipt SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/run-receipt-raw.json \
  --run-receipt SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/run-receipt.json \
  --pilot004-union SLR/SLR1/source-specific/ieee-xplore/pilots/004/searches/union-receipt.json \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/assessment.json

PYTHONPATH=SLR/SLR1/scripts/ieee_xplore_pilot005 \
python3 SLR/SLR1/scripts/ieee_xplore_pilot005/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/ieee-xplore/pilots/005 \
  --guideline SLR/SLR1/source-specific/ieee-xplore/source-specific-guidelines.md \
  --output SLR/SLR1/source-specific/ieee-xplore/pilots/005/searches/validation-report.json
```
