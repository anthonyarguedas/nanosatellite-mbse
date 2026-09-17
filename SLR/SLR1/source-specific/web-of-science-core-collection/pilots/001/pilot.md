# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_web_of_science.py`

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

Web of Science accepted the exact raw query echo, all current Core Collection editions, and oldest-first ordering for all three runs. The source totals were 1 for `A1`, 3 for `BG1`, and 22 for `PSR1`. The raw queries carried source-native `PY` clauses because the adapter does not combine typed year controls with `--raw-query`. The primary runs used `PY=(2011-2026)`. `PSR1` used the current Core Collection source-inception bound `PY=(1900-2026)` with no narrower review date limit. Count-only retained no records, so the `NEAR/6` fallback still requires local pair checking in a retained final set. These are diagnostic counts, not final-search results.
