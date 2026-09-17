# Pilot 002

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_scopus.py`

## Objective

Test the exact English control, the candidate report-type union, and a shorter A1 wildcard candidate through the 2026-08-29 diagnostic cutoff.

## Runs

- [`test1.json`](searches/test1.json): complete A1 diagnostic with the exact English facet and `DOCTYPE(ar OR cp OR ch OR rp)`.
- [`test2.json`](searches/test2.json): literal A1 with the exact English facet and no type control. It ended with `status: error` and no source total.
- [`coverage-receipt.json`](searches/coverage-receipt.json): deterministic wildcard coverage and the stop decision.

## Result

- [x] Change source controls or controlled vocabulary
- [x] Document a source limitation

`test1.json` completed with the visible `Language: English` control read back. The source also accepted the candidate type OR clause and reported 5 records. The retained record projections had blank document types. This does not prove complete type assignment for every eligible report type, so no type control is accepted.

`test2.json` read back the English and year controls, then ended with `status: error` and no total. The compact artifact has no error stage. The stop rule prevented a wildcard request. The offline 10-wildcard candidate is shorter, but it has no stable-ID comparison and is not accepted. These are diagnostic artifacts, not final-search results.
