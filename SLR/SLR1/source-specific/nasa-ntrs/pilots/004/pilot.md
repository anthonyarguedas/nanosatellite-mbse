# Pilot 004: screenshot rollout and stale-state finding

Required changes were applied in commit: NA

Pilot 004 is diagnostic. It is not a final search.

## Objective

Run the schedule from protocol commit `3194156e90497186664260a8e86435e78d2e2aa1` in literal and wildcard forms. Require a configured-search screenshot and a first-results screenshot beside every successful JSON.

## Result

The [initial plan](searches/event-plan.json) stopped on literal A1 with `total: null` at result reconciliation. The [predeclared continuation](searches/continuation-plan.json) retained three unchanged A1 attempts. One failed during owned-page allocation. Two reached result reconciliation and also retained `total: null`. No failed artifact contains a row prefix or supports a source count.

All three result-reconciliation failures wrote both automatic PNGs. The allocation failure occurred before a source page existed and wrote no screenshot.

A bounded diagnostic exposed the cause. NTRS briefly rendered the date-only baseline total of `90,395` between query submission and the requested result. The adapter could accept this intermediate state after a loading transition. Long A1 made the race easy to reproduce.

## Repair

Adapter v13 now requires a stable rendered baseline before entering the query. It also requires a stable changed result state after submission. A result signature equal to the baseline always remains stale. This prevents the date-only result from being promoted to query evidence.

Pilot 005 validates the repair and completes the schedule comparison. Pilot 004 remains an immutable null-failure record.
