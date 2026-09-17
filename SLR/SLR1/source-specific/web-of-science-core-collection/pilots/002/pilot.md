# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py`

## Objective

Test raw `LA=(English)`, the candidate report-type union, and a shorter A1 wildcard translation through the 2026-08-29 diagnostic cutoff.

## Runs

- [`test1.json`](searches/test1.json): complete A1 diagnostic with `LA=(English)` and `DT=(Article OR Proceedings Paper OR Book Chapter)`.
- [`A1.json`](searches/A1.json): complete literal A1 with `PY=(2011-2026) AND LA=(English)`.
- [`test2.json`](searches/test2.json): complete 10-wildcard A1 candidate under the same controls.
- [`coverage-receipt.json`](searches/coverage-receipt.json): deterministic coverage and stable-ID set receipt.

## Result

- [x] Change source controls or controlled vocabulary
- [x] Change the source translation or schedule
- [x] Document a source limitation

Both completed A1 runs read back the exact raw English clause and returned one record, `WOS:001027247800008`. The type test retained the full DT OR clause and returned that Proceedings Paper. It does not prove a lossless type and assignment path for every shared eligible report type, including institutional technical reports. No type control is accepted.

The wildcard candidate covers all 22 replaced literals with 10 wildcard atoms. It reduced the raw query from 3,396 to 3,141 characters. Its complete stable-ID set equals the literal set, so it is accepted for A1 only. The source may return extra completions in later runs. These are diagnostic artifacts, not final-search results.
