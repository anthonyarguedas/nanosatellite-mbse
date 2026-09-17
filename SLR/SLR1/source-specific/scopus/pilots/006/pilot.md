# Pilot 006: strict schedule and wildcard comparison

**Status:** partial diagnostic. This is not a final search.

The [plan](searches/event-plan.json) paired literal and ten-wildcard forms for all nine current main partitions. Every successful source event required two complete ordered stable-ID passes and both automatic screenshots.

A1, A2, and A3 completed in both forms:

| Partition | Literal | Wildcard | Stable-ID sets |
|---|---:|---:|---|
| `A1` | 6 | 6 | equal |
| `A2` | 33 | 33 | equal |
| `A3` | 11 | 11 | equal |

All six successful JSON artifacts contain strict compact receipts and two sibling screenshots. Literal B1 then failed during result reconciliation with candidate total 165. It retained `total: null` and only its configured-search screenshot. The [run receipt](searches/run-receipt.json) records the prospective stop.

The strict B1 failure does not negate the six completed source events. It prevents this pilot from completing the schedule or authorizing wildcard adoption by itself. Pilot 008 retained the completed A1-A3 evidence and used separately owned complete events for the remaining comparisons.
