# Pilot 006: shared-browser strict complete readiness

Required changes were applied in commit: NA

Export method: adapter version 12 at `~/agent-tools/internet/skills/browser/scripts/search_springer_link.py`. This is a readiness pilot. Its normal complete outputs remain pilot evidence and must not enter the review corpus.

## Objective

Run the adapter end to end in strict complete mode for three fixed date outcomes while other tabs remain open in the shared Chrome window:

1. an included Link 10.1038 article with Nature canonical metadata
2. a retained record with an unresolved exact day
3. a record excluded by a proved post-cutoff day

Each event must complete two card-path passes, publish a terminal marker, and save both mandatory screenshots.

## Concurrency investigation

The first shared-browser attempts failed before source navigation. Playwright connected to Chrome's browser WebSocket, then waited for every pre-existing page to initialize. A long-running tab owned by another adapter prevented that browser-level connection from completing. Springer query, context, page-count, and ownership checks had not run yet.

A browser-harness probe created an independent Springer tab in the same shared window while the foreign job remained active. This isolated the problem to Playwright's browser-level connection bootstrap.

Adapter version 12 now uses the browser harness's target-scoped CDP transport for target-less rendered runs. Each invocation-local daemon:

- creates one background target in shared Chrome
- attaches only to that target
- leaves every pre-existing tab untouched
- closes only its owned target

Explicit `--target-id` and native CSV workflows retain the Playwright transport. Native download handling is outside the target-scoped rendered backend.

The [final plan](searches/event-plan-v4.json) repeated all events through the target-scoped shared-browser transport. Earlier [attached](searches/event-plan.json), [fresh-browser](searches/event-plan-v2.json), and [dedicated-browser](searches/event-plan-v3.json) plans remain diagnostic history. Four null failure receipts contributed no source total or record.

## Strict complete results

All three final events completed in the active shared Chrome window.

| Event | Source total | Retained results | Date result | Canonical result |
|---|---:|---:|---|---|
| `nature-included-shared` | 1 | 1 | Included, `2026-05-26` | Exact Nature mapping retained |
| `unresolved-retained-shared` | 1 | 1 | Unresolved exact day retained | Book-to-reference-work route retained |
| `post-cutoff-excluded-shared` | 1 | 0 | Excluded, `2026-09-01` | Exact Link canonical retained |

Every compact JSON records `target_scoped_shared_cdp`, a complete PRISMA-S receipt, one route-evidence entry, and `retrieval_complete: true`. Each normal JSON has a verified terminal Springer marker. The six sibling PNGs passed filename, hash, dimension, and privacy checks.

The included Nature record stayed on its exact Link card route with zero redirects. Its `www.nature.com/articles/<DOI suffix>` canonical metadata URL persisted in the normalized record and compact route evidence. The adapter made no request to Nature and did not use final response status as an acceptance condition.

The unresolved `Encyclopedia of GIS` record stayed in normalized results with `exactDateFilterStatus: unresolved`. The post-cutoff article stayed in source and route accounting with `date_status: excluded` and was absent from normalized results.

## Decision

Accept adapter version 12's target-scoped shared-browser transport for rendered Springer searches. Accept strict complete publication, the Nature canonical mapping, exact-day inclusion, unresolved-day retention, and post-cutoff exclusion.

Springer has no pending source pilot. It is ready for final rendered searches with the accepted Pilot 004 schedule and wildcard translation. Native CSV remains an optional separate workflow and retains its existing Playwright boundary.

## Reproduction

```bash
PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot006 \
uv run SLR/SLR1/scripts/springer_nature_link_pilot006/run_pilot.py

PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot006 \
python3 SLR/SLR1/scripts/springer_nature_link_pilot006/build_assessment.py

PYTHONPATH=SLR/SLR1/scripts/springer_nature_link_pilot006 \
python3 SLR/SLR1/scripts/springer_nature_link_pilot006/validate_pilot.py
```
