# Pilot 008: consolidated current-schedule readiness

**Status:** passed. This is not a final search.

Required changes were applied in commit: NA

Export method: the strict Python API of adapter v16 at `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py` through the shared authorized browser.

## Objective

Establish one complete readiness result before the Compendex final search. Run all nine current partitions with:

- the approved `(CubeSat* WN ALL)`, `(nanosat* WN ALL)`, and `(SmallSat* WN ALL)` population atoms
- every other population term kept literal
- the current Boolean definitions from protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`
- no proximity operator or pair expansion
- strict paired Compendex and Inspec capture
- both mandatory adapter v16 screenshots for every accepted event

The [event plan](searches/event-plan.json) was saved before source use. It pinned the query renderer, runner, reviewed term snapshot, adapter entry point, and adapter implementation. It reused no source result from Pilots 003, 006, or 007.

## Fresh-attempt rule

Pilots 006 and 007 showed two safe transient failures. Pilot 006 stopped on an unverified `B2` page transition. Pilot 007 completed `B2`, `BG1`, and `BG2`, then stopped before `BC1` source submission during owned-page setup.

Pilot 008 therefore predeclared at most three fresh whole attempts per partition. A failed attempt retained null totals and no records. Each retry used the exact query on a new adapter-owned page. No pass, record, count, screenshot, or browser page was resumed or reused.

Nine partitions passed in ten attempts. The first `A2` attempt failed during owned-page setup before source submission. Its [null failure receipt](searches/attempts/A2/attempt-01.NON_MERGEABLE_FAILURE.json) has no records or screenshots. The exact second attempt passed.

## Strict paired results

Every accepted event completed two independent source-exhaustive passes. Native RIS reconciled every record in each pass. The paired total always equals its separate Compendex and Inspec projections.

| Partition | Paired | Compendex | Inspec | Accepted attempt |
|---|---:|---:|---:|---:|
| `A1` | 9 | 6 | 3 | 1 |
| `A2` | 43 | 29 | 14 | 2 |
| `A3` | 10 | 6 | 4 | 1 |
| `B1` | 244 | 153 | 91 | 1 |
| `B2` | 263 | 173 | 90 | 1 |
| `BG1` | 8 | 6 | 2 | 1 |
| `BG2` | 21 | 13 | 8 | 1 |
| `BC1` | 51 | 32 | 19 | 1 |
| `BT2` | 14 | 9 | 5 | 1 |

The [run receipt](searches/run-receipt.json) records 18 accepted strict source passes. The [assessment](searches/assessment.json) independently validates all query hashes, controls, stable accessions, pass receipts, and image receipts.

## Screenshot verification

All nine accepted JSON artifacts retain a configured-search screenshot and a verified-first-results screenshot. All 18 PNGs exist beside their JSON artifacts. Their SHA-256 hashes and dimensions match the adapter receipts. The configured-search images show the Expert form. The results images come from the verified first result page. Adapter v16 captured them during strict pass 1 and completed the independent pass 2 without reusing them.

## B2 confirmation

Pilot 003's `B2` remains an immutable explicit null failure. Pilot 008 completed the current wildcard `B2` query twice independently and captured all 263 paired records. The separate projections contain 173 Compendex accessions and 90 Inspec accessions. Both mandatory screenshots passed. This confirms current `B2` for Compendex readiness.

## Changed definitions

The four definitions changed after Pilot 003 and each passed live:

| Partition | Current definition | Paired | Compendex | Inspec |
|---|---|---:|---:|---:|
| `BG1` | `F(P) AND [F(G_model_fixed) OR F(G_mission_exact) OR (F(G_mission) AND F(M_B))]` | 8 | 6 | 2 |
| `BG2` | `F(P) AND [F(G_structure_fixed) OR F(G_product_exact) OR F(G_variation) OR (F(G_product) AND F(M_B))]` | 21 | 13 | 8 |
| `BC1` | `F(P) AND [F(C1_fixed) OR F(G_DSL)]` | 51 | 32 | 19 |
| `BT2` | `F(P) AND F(M_B) AND F(T_precise)` | 14 | 9 | 5 |

Every live query has exactly the three approved population wildcards and zero proximity operators.

## Reconciliation and decision

The database-scoped [reconciliation](searches/reconciliation.json) retains every accession with partition provenance. Compendex has 305 unique accessions from 427 partition occurrences. Inspec has 162 unique accessions from 236 occurrences. Both unions exceed 100, so the complete accession ledgers remain explicit. The two database sets remain separate.

The current Compendex translation and adapter route are ready for a separate final search. Pilot 008 is diagnostic and every artifact is non-mergeable. No final-search artifact was created. The paired Inspec projection is retained as diagnostic evidence. This Compendex pilot does not approve the wildcard translation for an Inspec final search.

## Reproduction

Run from the repository root with a fresh pilot output root. The checked-in Pilot 008 paths are create-only and refuse overwrite.

```bash
PYTHONPATH=SLR/SLR1/scripts/compendex_pilot008 \
python3 -m unittest -v \
  SLR/SLR1/scripts/compendex_pilot008/test_queries.py

PYTHONPATH=SLR/SLR1/scripts/compendex_pilot008 \
caffeinate -dims uv run \
  "$HOME/agent-tools/internet/skills/browser/scripts/run_with_browser.py" -- \
  uv run SLR/SLR1/scripts/compendex_pilot008/run_pilot.py \
  --event-plan SLR/SLR1/source-specific/compendex/pilots/008/searches/event-plan.json \
  --pilot-root SLR/SLR1/source-specific/compendex/pilots/008 \
  --receipt SLR/SLR1/source-specific/compendex/pilots/008/searches/run-receipt.json
```
