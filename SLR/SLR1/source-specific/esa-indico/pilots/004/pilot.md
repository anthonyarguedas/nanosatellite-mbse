# Pilot 004

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_esa_indico.py` universe validators with one normal public root-category export GET.

## Objective

Make one bounded retry of Pilot 003's category-0 event-universe export from checkpoint event index 0, before any event traversal.

## Runs

- [`event-universe-retry.json`](searches/event-universe-retry.json)

## Result

- [x] Document a source limitation

The fresh root `GET /export/categ/0.json?detail=events` timed out after 15 seconds before an HTTP response. It retained a null total, did not start event traversal, request event exports or attachments, submit rendered `q`, or run a final search. With Pilot 003, this is systematic root-event-universe endpoint evidence, not zero coverage. The second snapshot and ordered-ID/count proof remain unestablished. The receipt also records unverified owned-tab cleanup after the timed-out navigation. No further live browser work was attempted.

ESA has no Language control, and event/contribution/material groups do not map losslessly to the shared eligible report types. Exact local expressions remain normative. The wildcard candidate was not used or adopted.
