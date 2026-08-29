# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_wiley_online_library.py`

## Objective

Validate complete source-native `A1` and `BG1` translations in Wiley Anywhere count-only mode. The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54` for `A1`, plus `G_model: 14` fixed literals and `16` declared pairs for `BG1`. Use 2011-01-01 through the diagnostic upper bound 2026-08-29.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

Wiley accepted both complete Anywhere expressions with exact query readback in two count-only passes. Source totals were `A1: 21` and `BG1: 8`. The requested upper bound was retained as a client date boundary, while the source applied the enclosing 2011-01 through 2026-08 month range. No cards were retained, so exact-day accounting and local exact pair checking remain final-run requirements. These are diagnostic artifacts, not final searches.
