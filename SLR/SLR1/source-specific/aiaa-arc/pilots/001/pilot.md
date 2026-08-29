# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_aiaa_arc.py`

## Objective

Validate complete source-native `A1` and `BG1` Anywhere count-only translations with the diagnostic upper bound 2026-08-29. This date is not `P-001` or the common evidence cutoff.

The deterministic audit confirmed `P: 26`, `E_H: 38`, `M_H: 54`, and `G_model: 14` fixed literals plus `16` declared pairs. No wildcard or controlled-vocabulary terms were added.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)
- [BG1 first-100 preview](../../diagnostics/BG1-first-100.md)

## Result

- [x] Change the source translation or schedule
- [x] Document a source limitation

ARC accepted both Anywhere expressions with exact query and control readback. Diagnostic totals were `492` for `A1` and `8,088` for `BG1`. The later non-mergeable preview found a population term in only 10 of 100 titles and a complete artifact phrase in none. Anywhere may match abstracts or hidden indexed content, so this does not classify records as false matches. It shows inadequate visible precision and leaves the field strategy unaccepted. Reconsider narrower fields or a lossless field union before another search.
