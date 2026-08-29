# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_scopus.py`

## Objective

Validate the complete source-native `A1` and `BG1` translations. Validate `PSR1` only for the supporting-search route after the two primary pilot runs succeed. Use count-only diagnostics with the 2011 through 2026 source year bound.

The temporary deterministic generator audited these expansions before execution: `P` 26 literals, `E_H` 38, `M_H` 54, `G_model` 14 fixed literals plus 16 pairs, `X` 39, and `Q` 16.

## Runs

- [`A1.json`](searches/A1.json)
- [`BG1.json`](searches/BG1.json)
- [`PSR1.json`](searches/PSR1.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

Scopus accepted the exact query readback, year control, Documents scope, and oldest-first ordering for all three runs. The source totals were 6 for `A1`, 8 for `BG1`, and 53 for `PSR1`. The count-only runs retained no records, so they did not prove pair no-loss or allow local pair checking. Keep `W/6` as the documented conservative fallback and check pairs locally when final records provide the required fields. These are diagnostic counts, not final-search results.
