# Pilot 005: native RIS final readiness

**Status:** passed diagnostic. This is not a final search.

Required changes were applied in commit: NA

Export method: adapter version 12 at `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py` plus the Pilot 005 collector.

## Objective

Validate the adopted current Wiley schedule with page-scoped native RIS. Require two complete ordered DOI passes, exact-date accounting, and both mandatory screenshots for all ten source cells.

## Method

The [event plan](searches/event-plan.json) fixed the ten source cells before each adapter revision. The plan uses the accepted population wildcards, one direct query per partition except the two-cell A2 union, and the diagnostic window from 2011-01-01 through 2026-08-29.

Every successful event began from a fresh owned page and page zero. The first pass exported every source page through Wiley's visible RIS-with-abstracts flow. The second pass repeated the complete rendered DOI traversal. Each event reconciled its source total, page arithmetic, ordered DOI ledger, native RIS record order, visible `First published` dates, and two sibling screenshots.

Raw RIS bytes were validated and hashed in memory, then discarded. All normalized records remain diagnostic and nonmergeable.

## Results

| Cell | Source total | Pages per pass | Native RIS downloads | Change from Pilot 004 |
|---|---:|---:|---:|---:|
| `A1` | 21 | 2 | 3 | 0 |
| `A2-mh` | 34 | 2 | 3 | 0 |
| `A2-mb` | 106 | 6 | 7 | 0 |
| `A3` | 60 | 3 | 4 | 0 |
| `B1` | 86 | 5 | 6 | 0 |
| `B2` | 236 | 12 | 13 | 0 |
| `BG1` | 8 | 1 | 2 | 0 |
| `BG2` | 32 | 2 | 3 | 0 |
| `BC1` | 60 | 3 | 4 | 0 |
| `BT2` | 137 | 7 | 8 | 0 |

The ten cells contain 780 source records. The two passes produced 1,560 DOI observations. All 780 first-pass source records were normalized from 53 reconciled native RIS downloads containing 1,394,283 bytes. The two A2 cells form an ordered union of 129 DOIs.

All source IDs received an exact-date disposition. No record fell outside the exact cutoff. DOI `10.1049/el.2013.1237` exposed only month precision and remains retained as unresolved. The assessment validates 20 mandatory PNGs.

The [assessment](searches/assessment.json) passes with no errors. The [run receipt](searches/run-receipt.json) records all ten completed events.

## Adapter repairs and runtime

Early attempts exposed current Wiley and attached-Chrome timing behavior. Fourteen failed event attempts remain as null, nonmergeable receipts. Event-plan snapshots record the adapter revisions and are separate from those failed attempts.

The final adapter revision made these bounded changes:

- Unmatched Playwright worker wrappers are telemetry. Chromium child targets still receive target-scoped CDP gates when exposed.
- Ordinary HTTPS background subresources may continue during exact control activation. Top-level navigation, popup, WebSocket, and citation-download route checks remain active.
- A stale visible no-results shell is ignored only when the positive total, complete expected card count, and stable IDs reconcile.
- The exact `sortBy=Earliest` URL remains authoritative when Wiley omits its cosmetic Date menu. A newly exposed Oldest or Earliest option still stops the run for review.
- A completed in-memory CDP response is consumed before filesystem fallbacks. The private filesystem fallback is capped at five seconds.

The response-order repair removed repeated 90-second waits after successful downloads. After B2 completed, the final four cells completed in about 14 minutes. BC1 tolerated three unmatched worker wrappers while retaining complete source and RIS reconciliation.

The first five successful cells used an earlier version-12 adapter revision. B2 and the final four cells used the final relaxed revision. The revisions changed browser timing and containment only. Queries, controls, source pages, DOI checks, RIS validation, date accounting, screenshots, and output acceptance stayed unchanged.

## Decision

The adopted current Wiley schedule passes native RIS final-readiness validation. Pilot 004 remains the wildcard and rendered DOI equivalence record. Pilot 005 establishes native page-scoped RIS readiness for every current source cell, including B2 and BT2.

Future final searches still require fresh final events and the common final cutoff. Pilot records must not be promoted into final-search results.

## Reproduction

```bash
PYTHONPATH=SLR/SLR1/scripts/wiley_online_library_pilot005 \
python3 SLR/SLR1/scripts/wiley_online_library_pilot005/build_plan.py --check

WILEY_AUTHORIZED_TARGET_ID=<caller-authorized-target> \
PYTHONPATH=SLR/SLR1/scripts/wiley_online_library_pilot005 \
uv run SLR/SLR1/scripts/wiley_online_library_pilot005/run_pilot.py

PYTHONPATH=SLR/SLR1/scripts/wiley_online_library_pilot005 \
python3 SLR/SLR1/scripts/wiley_online_library_pilot005/build_assessment.py

PYTHONPATH=SLR/SLR1/scripts/wiley_online_library_pilot005 \
python3 SLR/SLR1/scripts/wiley_online_library_pilot005/validate_pilot.py
```
