# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_pqdt.py`

## Objective

Validate complete source-native `A1` and `BG1` count-only translations in PQDT Global with the 2011-2026 source year window and frozen native variant controls.

The deterministic audit used `P: 26`, `E_H: 38`, and `M_H: 54` literal members for `A1`. `BG1` used `P: 26`, `G_model: 14` fixed literals, and `16` declared pairs. No wildcards or controlled vocabulary terms were added.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

The current code review reproduced the missing strict total-cap guard. A mocked strict traversal reached detail collection for a total of `10,001` despite the documented `10,000` paging/export boundary. The minimal uncommitted adapter fix adds that guard and excludes above-cap results from strict recognition. Focused tests passed: `27 passed, 15 subtests passed`.

Both live count-only runs then accepted the complete expressions with exact query readback, the PQDT Global Full Text Included database selected alone, the 2011-2026 `YR` restriction applied, and `Oldest first` observed. The totals were `1` for `A1` and `1` for `BG1`. No records were retained, so the pilot does not test pair no-loss or complete capture. These are diagnostic artifacts, not final searches.
