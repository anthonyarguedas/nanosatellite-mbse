# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py`

## Objective

Validate the complete source-native `A1` translation and the requested publication-year control in count-only diagnostic mode.

The temporary deterministic generator audited these expansions before execution: `P` 26 literals, `E_H` 38, and `M_H` 54. The `BG1` run was not attempted after the explicit source-control failure.

## Runs

- [`A1.json`](searches/A1.json)

## Result

- [x] Document a source limitation

IEEE accepted the exact All Metadata query readback and the year control inputs, but the rendered range remained mismatched after Apply and three contradictory polls. The artifact records `total: null` and no accepted source result. This is a source-control failure, not a zero or a query-syntax result. Per the stop rule, no `BG1` request was made. Do not substitute an unbounded query or local date filtering. The adapter's exact day publication window also requires strict complete mode and was not used in this count-only pilot.
