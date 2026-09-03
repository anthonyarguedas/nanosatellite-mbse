# Pilot 004: shared population hydration

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`

## Objective

Submit the complete literal population block `P` under the English metadata and 2011 through 2026 controls. Reconcile the complete source ID population, hydrate every Record Details page once, and apply the nine current expressions as local annotations. This was a diagnostic pilot, not a final search.

## Source evidence

The page-size-30 route completed a full 42-page source snapshot with exact query readback. OATD reported `1,249` records. The checkpoint retained the stable set digest and normalized each completed public detail record atomically.

The [failure history](searches/failure-history.json) records the initial busy responses, page-size change, checkpoint public-text repair, slower six-second pacing, and multiple-resource-URL repair. None changed the query, controls, source ordering, or local plan.

The resource-URL continuation resumed from record 16 and later stopped by operator interruption after 251 records. The [record-252 continuation plan](searches/event-plan.resource-url-repair.record-252.json) bound that checkpoint and unchanged source event. It advanced the checkpoint from 251 to 338 records before OATD returned HTTP 504 without a ready source state. The [continuation receipt](searches/run-receipt.resource-url-repair.record-252.json) retains the failure. No final JSON or screenshots were published.

The final Pilot 004 checkpoint contains 338 complete detail records and 911 unhydrated source IDs. Every local nonmatch remains unresolved for exclusion because source analyzer equivalence and complete visible-field coverage are unproved.

## Result

Stop the broad `P`-only hydration route. It requires 1,249 detail requests and repeats a 42-page source snapshot on every resume. [Pilot 005](../005/pilot.md) supersedes it with an exact candidate-union gate strategy whose count upper bound is 34.

Pilot 004 remains incomplete and nonmergeable. It supplies dated source-total, stable-ID, adapter-repair, and partial public-metadata evidence only. No Pilot 004 record enters screening or the final review corpus.
