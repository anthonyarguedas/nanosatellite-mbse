# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py`

## Objective

Validate the Inspec projection of complete source-native `A1` and `BG1` translations in the paired Engineering Village event with the 2011-2026 Published range. The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54` for `A1`, plus `G_model: 14` fixed literals and `16` declared pairs for `BG1`.

## Runs

- [`A1.json`](../../../compendex/pilots/001/searches/A1.json)
- [`BG1.json`](../../../compendex/pilots/001/searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

The paired event accepted both complete expressions with exact source query readback, the Published range read back as 2011-2026, and `Date (Oldest)` was observed. Its Inspec projection exposed `3` rendered rows for `A1` and `2` for `BG1`. The bounded export retained one record and is not a complete Inspec capture or a pair no-loss test. These are diagnostic artifacts, not final searches.
