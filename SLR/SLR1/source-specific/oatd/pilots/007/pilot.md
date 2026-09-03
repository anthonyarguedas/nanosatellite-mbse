# Pilot 007: bounded union hydration and confirmation

Required changes were applied in commit: NA

Export method: the read-only card and Record Details functions in `~/agent-tools/internet/skills/browser/scripts/search_oatd.py`, invoked by the [Pilot 007 runner](../../../../scripts/oatd_pilot007/run_pilot.py).

## Objective

Hydrate each of the 26 accepted stable OATD IDs once, checkpoint every completed record, and confirm all eight gate sets before publishing a diagnostic union. This is a pilot, not a final search.

## Method

The [event plan](searches/event-plan.json) binds the exact Pilot 006 stable-ID sets, queries, English metadata control, 2011 through 2026 year bounds, and local annotation plan. It reuses no Pilot 004 detail record.

The run followed this sequence:

1. Obtain one fresh complete card-ID snapshot and both mandatory screenshots for every gate.
2. Require every fresh set to equal the corresponding Pilot 006 set.
3. Wait three minutes before detail requests.
4. Hydrate the 26-ID union in fixed order through one separate owned Record Details page.
5. Save a path-free normalized checkpoint after every record.
6. Wait 15 seconds between ordinary detail requests and three minutes after each eight-record batch.
7. Wait five minutes after hydration.
8. Obtain one complete confirming card-ID snapshot for every gate and reconcile it with the initial pass.

The run waited two minutes between gates. It allowed two run-wide explicit-busy detail retries after 120-second waits. An HTTP 504 received no automatic retry. A failure at any stage would leave the hydrated union unpublished.

## Results

All work completed in one attempt from 2026-09-03 00:24:41 through 01:15:41 UTC.

- All eight initial gate sets equaled Pilot 006.
- All eight confirming gate sets equaled their initial sets.
- Gate totals remained 16, 2, 2, 10, 0, 0, 3, and 1.
- The 34 gate occurrences remained an exact 26-ID deduplicated union.
- All 26 Record Details pages produced complete validated normalized records.
- The checkpoint advanced from 0 to 26 records.
- No Pilot 004 detail was reused.
- No busy retry or native-order drift occurred.
- Twenty-five records expose an abstract. One explicitly lacks an abstract.
- All visible publication dates are within the source year bounds.
- One 2026 record exposes only year precision, so its exact relation to the 2026-08-29 pilot cutoff remains unresolved.

The [hydrated union](searches/hydrated-union.json) retains every normalized record, gate provenance, local annotations, date readback, and stable union hashes. It is bound by a terminal marker and remains explicitly nonmergeable. Each [gate artifact](searches/gates/) binds its initial and confirming snapshots plus two screenshots through a separate terminal marker.

The [run receipt](searches/run-receipt.json) binds all outputs and the complete checkpoint. The [assessment](searches/assessment.json) records metadata and readiness findings. The [validation report](searches/validation-report.json) revalidated 16 source passes, 26 normalized details, the checkpoint, all markers, and the exact union.

## Result

Accept the eight-gate source route and bounded detail workflow for a fresh final execution. A final event must use the final common cutoff, publish a standard merge- and report-ready multi-gate union artifact, and resolve the one year-only 2026 record during screening.

Pilot 007 creates no final-search event and contributes no record directly to screening.
