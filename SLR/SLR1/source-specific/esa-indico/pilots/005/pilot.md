# Pilot 005

Required changes were applied in commit: NA

Export method: fixed read-only `search_esa_indico.py` adapter, version 7, through the shared local browser runner.

## Objective

Bind all nine direct partitions to the repaired category-0 deterministic local route at the 2026-08-29 diagnostic cutoff. Make one shared root attempt, then run all local matchers only if the root universe, every event export, every public attachment, and the confirming root snapshot are complete.

## Runs

- [`schedule-plan.json`](searches/schedule-plan.json): no-clobber `pilot_schedule` plan with all nine exact local expressions.
- [`root-local-harvest-A1.json`](searches/root-local-harvest-A1.json): the one live A1-anchored root attempt. Its commit marker is retained alongside it.
- [`shared-root-failure-receipt.json`](searches/shared-root-failure-receipt.json): concise interpretation of the live route failure.
- [`root-restart-checkpoint.json`](searches/root-restart-checkpoint.json): safe route-restart checkpoint.
- [`schedule-status.json`](searches/schedule-status.json) and the nine exact-query receipts (`A1.json` through `BT2.json`): schedule binding and null accounting.

## Result

- Document a source limitation
- Bind every required partition

The repaired root route passed its former timeout boundary far enough to reach attachment collection, then the live adapter ended with `attachment_content_retrieval_failed`. The saved compact adapter artifact has `total: null`, no records, and no local-match total. It does not retain the candidate snapshot's count, ID ledger, or attachment identity, so Pilot 005 does not infer any of them. In particular, the first snapshot is **not** called complete and the source total is not zero.

The adapter performs attachment collection before the confirming root snapshot and before the query-specific local matcher. Therefore the one shared pre-match failure is explicitly projected to nine exact-query null receipts. Each receipt carries the unmodified `pilot_schedule` expression, expression hash, Boolean form, and `NEAR/5` count, and links the same live evidence. No stable-ID reconciliation or over-100 investigation started.

No rendered `q`, wildcard, language/date/type/access filter, vocabulary supplement, or final search was used. ESA has no source language or date limiter, no lossless eligible-type filter, no rendered phrase/proximity control, no usable controlled vocabulary, and no native complete search-export control. The local public category/event/attachment route remains the only exact Boolean and same-field-proximity route, but it currently covers Events, Contributions, and Materials only. Notes and Categories remain outside it.

The retained restart checkpoint deliberately restarts the root universe rather than pretending to resume from an unpersisted candidate ID list. A future approved continuation must obtain fresh first and confirming ordered root snapshots, complete every attachment-content check, run all nine exact matchers, reconcile type-prefixed stable IDs, and investigate any match set over 100.
