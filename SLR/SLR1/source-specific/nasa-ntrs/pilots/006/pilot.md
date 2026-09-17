# Pilot 006: maximal wildcard rejection

Required changes were applied in commit: NA

Pilot 006 is diagnostic. It is not a final search. It uses Pilot 005's fresh complete literal sets as the pinned baseline.

## Objective

Test whether NTRS term-prefix wildcards can compress every compatible morphology family. The [predeclared plan](searches/event-plan.json) replaces 284 literals with 114 wildcard atoms. It includes quoted phrase terms with one or more wildcarded components. Acronyms remain literal.

Every partition used the same inclusive 2011-01-01 through 2026-08-29 window and controls as Pilot 005. Each accepted event completed two ordered source passes and saved both mandatory screenshots.

## Result

The [run receipt](searches/run-receipt.json) records nine accepted events from 12 attempts. Two result-reconciliation failures and one owned-page allocation failure remain null, empty, and non-mergeable. Exact retries succeeded.

| Partition | Literal baseline | Maximal wildcard | Relation | Missing occurrences |
|---|---:|---:|---|---:|
| `A1` | 0 | 0 | equal | 0 |
| `A2` | 2 | 1 | strict subset | 1 |
| `A3` | 0 | 0 | equal | 0 |
| `B1` | 11 | 7 | strict subset | 4 |
| `B2` | 4 | 3 | strict subset | 1 |
| `BG1` | 0 | 0 | equal | 0 |
| `BG2` | 2 | 2 | equal | 0 |
| `BC1` | 0 | 0 | equal | 0 |
| `BT2` | 0 | 0 | equal | 0 |

The maximal schedule union has 9 IDs. The literal union has 14. Five literal IDs are missing:

- `20160007475`
- `20190025644`
- `20205006035`
- `20230005355`
- `20260000453`

No wildcard-only ID is present. The [assessment](searches/assessment.json) verifies all nine accepted artifacts and 18 screenshots. It records six missing partition occurrences.

## Decision

Reject the maximal wildcard translation. It is shorter, but it is not recall safe. The combined phrase and multi-term wildcard substitutions cannot replace exact phrases in this schedule.

Retain Pilot 005's 26 standalone wildcard atoms. Keep all phrase terms and acronym variants literal. Equal zero partitions do not validate their unobserved wildcard substitutions.
