# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py`

## Objective

Validate complete source-native `A1` and `BG1` count-only translations in Advanced Technologies & Aerospace Index with the exact 2011-01-01 through 2026-08-29 publication range.

The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54` literal members for `A1`. `BG1` used `P: 26`, `G_model: 14` fixed literals, and `16` declared pairs. No wildcards or controlled vocabulary terms were added.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

Both complete expressions were accepted with exact query readback, the Advanced Technologies & Aerospace Index selected alone, the publication range applied, and `Oldest first` observed. The count-only totals were `0` for `A1` and `2` for `BG1`. No records were retained, so the pilot does not test pair no-loss or complete capture. These are diagnostic artifacts, not final searches.
