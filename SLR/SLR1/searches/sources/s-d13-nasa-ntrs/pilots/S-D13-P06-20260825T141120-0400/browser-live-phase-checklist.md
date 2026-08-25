# S-D13-P06 shared-CfT live-phase checklist

- Pilot/phase ID: `S-D13-P06-20260825T141120-0400`
- Campaign and decision class: `S-D13-C01-20260824T161325-0400` (`controller_technical`)
- Offline reading, exact query-byte checks, adapter tests, output reservations, and evidence planning: complete before lease.
- OWNER: `S-D13-P06-20260825T141120-0400`
- SOURCE: `ntrs`
- Immutable lease receipt: `.searches-d13-ntrs/S-D13-P06-20260825T141120-0400/browser-lease-receipt.json`
- Global pacing: one serialized full live phase; no source retry/reissue policy.
- Finite wait policy: lease wait 30 seconds; lease timeout 600 seconds; source-health stabilization 30 seconds with 0.2-second interval; no challenge/busy retry; three-second passive pacing between distinct operations.

## Lease boundary

- [x] Complete phase runs through `run_with_browser_lease.py` with owner, source, and a new receipt.
- [x] The adapter/probe client uses only `http://127.0.0.1:9222` supplied by the canonical lease.
- [x] The canonical shared Chrome for Testing profile and one protected inert broker anchor are used; no profile, port, launcher, or browser override is supplied.
- [x] The health probe and adapter each create/close only their own page; no baseline target is navigated or closed.
- [x] The outer command is process-scoped `caffeinate -dims`; lid remains open and AC power/Sleep-Wake evidence is recorded.

## Exact operations

1. One record-free NTRS root source-health navigation. No query and no records.
2. Only after a passing health receipt, one exact 13-byte `nanosatellite`
   count-only rendered adapter invocation: limit 1, max pages 1, skip full
   abstracts, timeout 90, zero page/detail delays, no date/year, no retry,
   fallback, detail, export, completeness, or partition.

## Cleanup and terminal rules

- [ ] Preserve immutable receipts and compact safe summaries only inside the P06 packet/restricted namespace.
- [ ] Verify every owned page is closed, the broker anchor is preserved, the lease is released, and no child/group remains.
- [ ] On any technical failure, investigate immediately source-free after verified cleanup; no failed source operation is reissued.
- [ ] `total=null` and no records are mandatory for unreconciled failures; no screening/import/prefix/final event occurs.
