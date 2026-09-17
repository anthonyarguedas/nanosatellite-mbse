# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

## Objective

Validate complete source-native `A1` and `BG1` translations in one paired Engineering Village event with the 2011-2026 Published range. The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54` for `A1`, plus `G_model: 14` fixed literals and `16` declared pairs for `BG1`. The paired CLI has no count-only mode, so the bounded Python API path used one page and one exported record.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

Both complete expressions had exact source query readback, the Published range read back as 2011-2026, and `Date (Oldest)` was observed. The paired event exposed separate rendered rows for Compendex and Inspec: `A1` had `5` and `3`, and `BG1` had `6` and `2`, respectively. The bounded export retained one record and is not a complete capture or a pair no-loss test. These are diagnostic artifacts, not final searches.
