# Pilot 006: first consolidated readiness attempt

**Status:** incomplete diagnostic. This is not a final search.

Required changes were applied in commit: NA

Export method: the strict Python API of `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py` through the shared authorized browser.

## Objective

Run all nine current partitions with the approved three-wildcard Compendex `F(P)` block, the Boolean schedule from protocol commit `3194156e90497186664260a8e86435e78d2e2aa1`, no proximity operators, strict paired Compendex and Inspec capture, and both adapter v16 screenshots.

## Outcome

The [predeclared plan](searches/event-plan.json) required one fresh attempt per partition and stopped after the first failure. Four partitions completed before the stop:

| Partition | Paired | Compendex | Inspec |
|---|---:|---:|---:|
| `A1` | 9 | 6 | 3 |
| `A2` | 43 | 29 | 14 |
| `A3` | 10 | 6 | 4 |
| `B1` | 244 | 153 | 91 |

Each successful event completed two independent source and RIS passes. Each retained both mandatory screenshots with matching hashes and dimensions.

The current `B2` source page reported 263 paired records. Its first strict attempt stopped when adapter v16 could not verify one Next transition. The [failure receipt](searches/cells/B2.NON_MERGEABLE_FAILURE.json) keeps all totals and records null. It retains the two screenshots that were captured before the failure. The [run receipt](searches/run-receipt.json) then stopped the pilot as predeclared. `BG1`, `BG2`, `BC1`, and `BT2` did not run.

The [assessment](searches/assessment.json) rejects readiness from this attempt. Pilot 008 later completed the full fresh schedule.
