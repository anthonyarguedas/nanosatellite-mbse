# Pilot 009: B1 set reconciliation and wildcard adoption

**Status:** passed diagnostic. This is not a final search.

## B1 rerun

The [predeclared plan](searches/event-plan.json) ran two complete literal B1 events and two complete wildcard B1 events. It required repeat totals and stable-ID sets to agree. It retained source order as separate evidence and made no final-search readiness claim.

All four events completed with 165 records each. The literal repeats had equal sets and different tied Date (oldest) order. The wildcard repeats had equal sets and order. Literal and wildcard sets were exactly equal. All four JSON artifacts have both mandatory sibling screenshots. The [assessment](searches/assessment.json) passed with eight verified PNGs.

## Combined main-schedule result

The [combined assessment](searches/combined-assessment.json) and [validation report](searches/validation-report.json) use:

- strict paired A1, A2, and A3 evidence from Pilot 006
- complete repeated B2, BG1, BG2, BC1, and BT2 evidence from Pilot 008
- the complete repeated B1 evidence from this pilot

All nine fresh literal sets were exactly equal to their ten-wildcard counterparts. No literal ID was missing. No wildcard-only ID was present.

| Partition | Literal | Wildcard |
|---|---:|---:|
| `A1` | 6 | 6 |
| `A2` | 33 | 33 |
| `A3` | 11 | 11 |
| `B1` | 165 | 165 |
| `B2` | 180 | 180 |
| `BG1` | 8 | 8 |
| `BG2` | 14 | 14 |
| `BC1` | 32 | 32 |
| `BT2` | 11 | 11 |

The combined evidence uses 30 successful source JSON events and verifies their 60 required screenshots. It also validates all four compound partitions introduced by protocol commit `3194156e90497186664260a8e86435e78d2e2aa1` without proximity operators or pair expansions.

## Decision and limitation

Adopt the ten trailing-wildcard population atoms in every main partition. They replace 22 population literals and shorten each complete query by 375 characters. Retain the four explicit spaced `small satellite(s)` and `small sat(s)` forms. Keep all non-population blocks literal.

This decision is bounded to the nine main partitions with the tested 2011-2026 and English controls. PSR queries remain literal until separately compared. B1 source order varied among same-year records under Date (oldest). The two strict B1 attempts in Pilots 006 and 007 failed during result reconciliation. At this pilot stage, the successful one-owner diagnostics established wildcard set safety without final-search readiness. [Pilot 012](../012/pilot.md) later validated complete-set strict reconciliation and the accepted wildcard B1 query.
