# Pilot 007: feasible hybrid metadata-anchored route

Pilot 007 is diagnostic. It is not a final search. It uses 2011-01-01 through 2026-08-29 and retains only non-mergeable source artifacts.

## Objective

Test a search route that keeps the screening corpus feasible while retaining body-sensitive EPS, relationship, central-asset, and tailoring terms where needed.

The predeclared [event plan](searches/event-plan.json) used:

| ID | Hybrid construction |
|---|---|
| A1 | `META(P) AND META(M_H) AND Anywhere(E_H)` |
| A2 | `META(P) AND META(M_H OR M_B) AND Anywhere(E_F)` |
| A3 | `META(P) AND META(M_B) AND Anywhere(E_H)` |
| B1 | `META(P) AND META(M_H)` |
| B2 | `META(P) AND META(M_B) AND Anywhere(R)` |
| BG1 | Direct `Anywhere(P AND G_model)` |
| BG2 | Factor-wise metadata `G_structure` route |
| BC1 | `META(P) AND Anywhere(C1)` |
| BT2 | `META(P) AND META(M_B) AND Anywhere(T_precise)` |

`META(X)` is the union of Title, Keywords, and Abstract at factor level. ARC rows are `AND` clauses, so each metadata field assignment was executed as a separate source cell and reconciled by stable DOI.

BG1 remains direct Anywhere because its current result contains only 45 source events. BG2 remains metadata-restricted because direct Anywhere returned 3,584.

## Results

All 94 cells completed. The largest cell returned 45 records. Every cell was captured completely.

| ID | Cells | Cell-event sum | DOI union |
|---|---:|---:|---:|
| A1 | 9 | 42 | 18 |
| A2 | 9 | 119 | 40 |
| A3 | 9 | 33 | 12 |
| B1 | 9 | 87 | 37 |
| B2 | 9 | 56 | 23 |
| BG1 | 1 | 45 | 44 |
| BG2 | 36 | 4 | 2 |
| BC1 | 3 | 52 | 36 |
| BT2 | 9 | 34 | 11 |

The deduplicated nine-partition union contains **119 canonical DOIs**. This is a feasible full-text screening workload compared with the 3,584-result BG2 Anywhere partition alone.

The factor-wise Pilot 006 union contained 47 DOIs. All 47 are present in the hybrid union. The hybrid route adds 72 records by allowing the designated third factors to match Anywhere.

## Known-item recall

Known eligible DOI `10.2514/6.2015-4474` is source-located in A2, B1, B2, and BC1. Pilot 007 retrieved it in all four applicable partitions.

ARC also returned the DOI in A1 and A3 through hidden or full-text indexing. Those source events do not change its source-located applicable partition set.

The observed known-item recall gate passed. This gate covers one eligible report and does not prove recall for unknown reports.

## Decision

- Accept the hybrid route as the prospective canonical AIAA screening translation.
- Screen all 119 records from the deduplicated hybrid union.
- Retain the factor-wise metadata result as a priority tag within that union.
- Retain complete Anywhere totals as sensitivity evidence. Do not treat the 3,584-result BG2 set as a screening corpus.
- Keep BG1 in direct Anywhere because 45 source events are feasible.
- Keep BG2 metadata-restricted because its direct Anywhere result is infeasible.
- Apply no language, publication type, Topic, wildcard, access, peer-review, or full-text-availability filter.

## Screenshots and failures

Adapter v5 produced both mandatory screenshots for every successful JSON. Pilot 007 verified 188 required screenshots for 94 source cells. One failed attempt retained a search-page screenshot, giving 189 local PNGs. Project `.gitignore` excludes images under `SLR/SLR1/source-specific/`.

Three source failures remain as `NON_MERGEABLE_FAILURE` artifacts. Exact retries recovered every cell. No failure was converted to zero.

## Limits

- The known-item gate is observed evidence for one report.
- BG2 metadata restriction can miss a report whose population or reusable-artifact evidence occurs only in full text.
- Citation chasing and the other planned direct sources remain necessary recall safeguards.
- Source bounds are inclusive ARC months before exact-day exclusions.
- Pilot cards cannot enter the final corpus.
- Final execution still requires complete source-month treatment, exact-day handling, native export, and final-search artifacts.

## Reproduction

Review scripts are under [`SLR/SLR1/scripts/aiaa_arc_pilot007`](../../../../scripts/aiaa_arc_pilot007). The offline assessment and validation commands are:

```bash
PYTHONPATH=SLR/SLR1/scripts/aiaa_arc_pilot007 \
python3 SLR/SLR1/scripts/aiaa_arc_pilot007/build_assessment.py \
  --pilot-root SLR/SLR1/source-specific/aiaa-arc/pilots/007 \
  --pilot006-root SLR/SLR1/source-specific/aiaa-arc/pilots/006 \
  --output SLR/SLR1/source-specific/aiaa-arc/pilots/007/searches/assessment.json

PYTHONPATH=SLR/SLR1/scripts/aiaa_arc_pilot007 \
python3 SLR/SLR1/scripts/aiaa_arc_pilot007/validate_pilot.py \
  --pilot-root SLR/SLR1/source-specific/aiaa-arc/pilots/007 \
  --pilot006-root SLR/SLR1/source-specific/aiaa-arc/pilots/006 \
  --guideline SLR/SLR1/source-specific/aiaa-arc/source-specific-guidelines.md \
  --pilot-document SLR/SLR1/source-specific/aiaa-arc/pilots/007/pilot.md \
  --output SLR/SLR1/source-specific/aiaa-arc/pilots/007/searches/validation-report.json
```

Live events must run through the shared browser launcher. Source receipts, retries, local screenshots, and reconciliation artifacts are under `searches/`.
