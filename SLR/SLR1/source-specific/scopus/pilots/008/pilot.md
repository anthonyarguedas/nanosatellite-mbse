# Pilot 008: complete one-owner schedule comparisons

**Status:** complete source events with one failed local ordered-repeat criterion. This is not a final search.

## Method

The [predeclared plan](searches/event-plan.json) covered B1, B2, BG1, BG2, BC1, and BT2. Each literal and wildcard query ran twice in separate adapter-owned events. Every event exhausted the source result, used Documents, 2011-2026, the exact visible `English` facet, Date (oldest), page size 50, no type or access limiter, and no abstract expansion. Each successful JSON saved one configured-search and one first-results screenshot.

All 24 source events completed. The [run receipt](searches/run-receipt.json) verifies 48 sibling screenshots.

## Results

| Partition | Literal | Wildcard | Literal-wildcard set result |
|---|---:|---:|---|
| `B1` | 165 | 165 | equal |
| `B2` | 180 | 180 | equal |
| `BG1` | 8 | 8 | equal |
| `BG2` | 14 | 14 | equal |
| `BC1` | 32 | 32 | equal |
| `BT2` | 11 | 11 | equal |

Both runs for every query had equal totals and stable-ID sets. Both runs also retained equal source order except literal B1. Its two complete 165-ID sets were equal, while tied Date (oldest) records changed order.

The [assessment](searches/assessment.json) failed its prospectively stricter ordered-repeat rule for B1. It accepted no post hoc exception. The other five comparisons passed their planned repeat and set checks. Pilot 009 reran B1 under a prospectively declared complete-set rule and retained order stability as a separate limitation.
