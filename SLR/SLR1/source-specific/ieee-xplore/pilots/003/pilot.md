# Pilot 003

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

## Objective

Record the unavailable language and report-type controls and audit a 10-wildcard A1 candidate without weakening the required 2011 through 2026 year control.

## Runs

- [Pilot 002 literal A1](../002/searches/A1.json): required year-control diagnostic reused as read-only evidence.
- [`coverage-receipt.json`](searches/coverage-receipt.json): deterministic wildcard coverage and stop decision.

## Result

- [x] Document a source limitation

IEEE exposes no proved Language field or facet. It also does not prove a lossless content-type union. `Early Access Articles` can overlap another content type, and the current taxonomy and assignment coverage do not establish every eligible report type. No language or type control is accepted. Peer-review and access controls remain unused.

Pilot 002 already ended with the mandatory `2011_2026_Year` control read back, `status: error`, and no total. A third live request would violate the stop rule. The offline candidate has 10 wildcards, covers all 22 replaced literals, and reduces the query from 4,776 to 4,377 characters. It is not accepted without a stable-ID superset comparison. These are diagnostic artifacts, not final-search results.
