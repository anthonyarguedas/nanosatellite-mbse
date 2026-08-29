# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ntrs.py`

## Objective

Validate complete source-native `A1` and `BG1` general-query count-only translations with the diagnostic upper bound 2026-08-29. This date is not `P-001` or the common evidence cutoff.

The deterministic audit confirmed `P: 26`, `E_H: 38`, `M_H: 54`, and `G_model: 14` fixed literals plus `16` declared pairs. No wildcard or controlled-vocabulary terms were added.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

NTRS accepted both full `q` expressions with exact query readback, inclusive publication-date controls, `Publication Date (Oldest)`, and the native page-size control. The count-only source totals were `0` for both `A1` and `BG1`. Count-only diagnostics retain no records, so they do not test pair no-loss or complete capture. Keep the full-text general-query translation and exact reversed-order `~5` pair clauses for final runs. These are not final searches.
