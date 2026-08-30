# Pilot 003: complete lossless schedule-cell diagnostic

Required changes were applied in commit: NA (no source-guideline acceptance change)

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`, invoked through the shared browser wrapper and its strict complete-run contract.

## Objective

Run every direct-schedule partition as deterministic, lossless IAF cells below the source's 500-character cap. The diagnostic window was 2011-01-01 through 2026-08-29, applied locally only after each complete raw traversal. This is not a final search.

## Method

- The [cell plan](searches/cell-plan.json) imports the normative literals and declared pairs from the shared [pilot schedule module](../../../../scripts/pilot_schedule/queries.py). It retains whitespace conjunction, uppercase `OR`, source parentheses, all pair atoms, and no wildcard.
- Nested contiguous packing reduced the shared equal-budget baseline from 1,467 to 1,077 cells without dropping or overlapping any Cartesian alternative tuple. Each plan entry records an exactly-once coverage certificate.
- Every cell was run with two rendered passes, a 5,000-record complete-run ceiling, full retained-detail capture, exact query readback, and the local inclusive date window. [Cell artifacts and raw-ID sidecars](searches/cells/) are hash-bound to the adapter's marker-gated compact result.
- No `language:`, event/year, type, access, peer-review, or full-text-availability restriction was submitted. IAF's conference-paper scope was retained. No wildcard was used, so no wildcard acceptance was inferred.

## Runs

- [Cell construction, cap, membership, and coverage certificates](searches/cell-plan.json)
- [Complete partition unions and source-event reconciliation](searches/assessment.json)
- [Local title/abstract exact-pair checks, including uncertainty](searches/local-pair-checks.json)
- [Threshold investigations](searches/union-investigations.json) (empty because no deduplicated raw or diagnostic union exceeded 100)
- [Plan, collection, reconciliation, and validation helpers](../../../../scripts/iaf_digital_library_pilot003/)

## Result

| ID | Complete cells | Raw source-event total | Raw paper-ID union | Diagnostic-window union |
|---|---:|---:|---:|---:|
| A1 | 132 | 9 | 2 | 2 |
| A2 | 173 | 36 | 12 | 11 |
| A3 | 76 | 14 | 7 | 7 |
| B1 | 11 | 93 | 42 | 39 |
| B2 | 73 | 246 | 57 | 53 |
| BG1 | 8 | 7 | 5 | 5 |
| BG2 | 6 | 16 | 10 | 7 |
| BC1 | 23 | 11 | 9 | 6 |
| BT2 | 575 | 39 | 15 | 13 |

All 1,077 cells completed; no partition has a failure total. The table's raw total is the sum of overlapping source events; the two union columns are deduplicated stable paper-ID unions. Date exclusions were 1 (A2), 4 (B1), 9 (B2), 4 (BG2), 4 (BC1), and 4 (BT2); all other partitions had none. No union exceeded 100, so the required over-100 investigation trigger did not apply.

The local exact-pair check confirmed no pair-bearing metadata record in BG1 (0/5), three in BG2 (3/7), none in BC1 (0/6), and one in BT2 (1/13). A missing visible confirmation remains explicitly uncertain rather than a source false match, because the source's broader same-Any-keyword pair fallback can match other indexed text.

- [x] No guideline change needed
- [x] Document a source limitation

The 500-character source cap requires the saved lossless cell plan. The adapter's compact persisted output omits repeated raw-ID/capture fields, so the pilot records a create-only, hash-bound complete-ID sidecar for each strict cell. This is an audit-output limitation, not a source-semantic or eligibility-filter change. The source guideline completion state and `final-searches/` remain unchanged.
