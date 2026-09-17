# Pilot 012: set-reconciled strict validation

**Status:** passed diagnostic. This is not a final search.

The [predeclared plan](searches/event-plan.json) validated the v2 strict contract on the four Pilot 010 EIDs, then ran the accepted wildcard B1 query. Each event required two exhaustive fresh-page passes, equal totals, page accounting, controls, and complete unique stable-ID sets. Source order remained audit evidence.

Both events passed:

| Event | Total | Order matched | Changed positions |
|---|---:|---|---:|
| Four swapping papers | 4 | yes | 0 |
| Wildcard B1 | 165 | yes | 0 |

Both events happened to retain equal order. Pilot 010 remains the evidence that order can vary under the same Date (oldest) control. Each JSON uses `academic-search-scopus-strict-two-pass/v2`, records the canonical set hash and both pass-order hashes, and has both mandatory sibling screenshots.

The [assessment](searches/assessment.json) and [validation report](searches/validation-report.json) accept complete-set reconciliation and mark wildcard B1 ready under the current strict contract. The adapter still fails on a changed ID set, total, page count, range, scope, sort, page size, duplicate ID, incomplete traversal, or screenshot failure.
