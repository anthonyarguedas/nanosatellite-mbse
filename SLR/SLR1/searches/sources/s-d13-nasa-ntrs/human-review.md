# Human review: NASA NTRS corrective scope

## Decision record

On 2026-08-24, the review owner approved all three recommendations presented after blocked pilot `S-D13-P01-20260823T232536-0400`:

1. approve a separately scoped NTRS adapter correction;
2. authorize one corrective P02 after the fix was committed and the public service health route recovered; and
3. retain the protocol's exact paired-term semantics rather than accept the broad draft placeholders without live losslessness evidence.

This approval authorized corrective work and P02. It did **not** accept an NTRS source method, any draft query translation, or either pilot.

## Corrective implementation

The adapter correction was committed as `e720192855f8b5356d92fff23caeb6b8f66bbaf4` (`Harden NTRS complete search runs`) and integrated into the `agent-tools` main branch. It adds exact ISO date controls, strict two-pass raw-ID completeness, record-free/null failure output, report-readiness gating, and NTRS database accounting. Controller verification after integration passed 58 focused tests and 7 subtests.

## Corrective pilot outcome

Pilot `S-D13-P02-20260824T111634-0400` is blocked, not accepted. The public health endpoint returned HTTP 200 with `status=ok`, but the single authorized minimal anonymous search POST timed out after 45 seconds. It therefore has `total=null`, retained no records, and stopped without retrying, narrowing, running a live adapter event, or creating P03.

The exact q semantics, fields, controlled-vocabulary disposition, date and language behavior, all nine live partition translations, pagination, raw-ID stability, default ordering, strict completeness, and paired-term transport remain unvalidated. `code_issue=unresolved`: the correction passed offline tests, but the source did not return an envelope with which to validate it.

## Controller review limits

- P01 remains blocked and immutable. Its manifest start time postdates its first two recorded probes; this chronology defect is another reason P01 cannot support acceptance.
- P02 allocated its pilot ID before source requests and passed schema, JSON, link, hash, partition-coverage, privacy, chronology, and write-boundary checks.
- No source packet proposal is promoted, `accepted_pilot_ids` remains empty, and no central task, search-log, protocol, dictionary, crosswalk, schema, or final-event file is updated.

A later pilot requires fresh human authorization after source availability is demonstrated. Exact same-field paired-term semantics remain unchanged; no fallback has been accepted.
