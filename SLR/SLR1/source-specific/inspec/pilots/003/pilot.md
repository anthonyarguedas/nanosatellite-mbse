# Pilot 003: linked Inspec projection of the paired schedule

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

## Objective

Retain Inspec's separate projection of one paired Compendex+Inspec Engineering Village event for each direct-query partition, without creating a second Inspec event. This is a pilot, not a final search.

## Runs and outcomes

The authoritative paired event, exact expressions, controls, strict-capture state, Compendex projection, and stable accession ledger are recorded in [Compendex Pilot 003](../../../compendex/pilots/003/pilot.md). The linked Inspec projection is:

| ID | Inspec total | Outcome |
|---|---:|---|
| A1 | 3 | strict two-pass paired capture |
| A2 | 14 | strict two-pass paired capture |
| A3 | 4 | strict two-pass paired capture |
| B1 | 91 | strict two-pass paired capture |
| B2 | null | linked explicit strict null failure |
| BG1 | 2 | strict two-pass paired capture |
| BG2 | 9 | strict two-pass paired capture |
| BC1 | 19 | strict two-pass paired capture |
| BT2 | 9 | strict two-pass paired capture |

Inspec's successful-event stable-accession union is 116 from 151 event occurrences. It is above 100 and is fully retained with partition provenance in the paired [over-100 investigation](../../../compendex/pilots/003/searches/over-100-investigation.json). It is not a final or full-schedule total because B2 has no strict capture.

The linked historical pairs use the captured v2 marker protocol. [Compendex Pilot 008](../../../compendex/pilots/008/pilot.md) later completed the fresh current-query B2 event with adapter v16, strict paired capture, and both mandatory screenshots. Its Inspec projection contains 90 records. That diagnostic result leaves this historical null failure unchanged and does not approve an Inspec wildcard translation.

## Decision

The paired event used literal free text, raw `(English WN LA)`, Published 2011–2026, autostemming off, and `Date (Oldest)` without a document-type or Open Access limiter. No Inspec controlled-term supplement or wildcard is accepted. Do not duplicate the event, turn B2 into zero, or move this pilot into `final-searches/`.
