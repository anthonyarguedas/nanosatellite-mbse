# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_iaf_digital_library.py`

## Objective

Validate one representative `A1` cell and one representative broad `BG1` pair cell below IAF's 500-character limit. Use 2026-08-29 only as a diagnostic upper bound. It is not `P-001`.

The deterministic audit confirmed `P: 26`, `E_H: 38`, `M_H: 54`, and `G_model: 14` fixed literals plus `16` declared pairs. The live cells used `CubeSat` with the two named `A1` terms, then `CubeSat` with the `mission-agnostic` and `model` pair.

## Runs

- [`test1.json`](searches/test1.json)
- [`test2.json`](searches/test2.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

The 69-character `A1` cell and 38-character pair cell had exact query readback, normal rendered result state, and source totals of `0`. The date bound was recorded as local post-filter evidence. No complete traversal or unproved event/year partition route was invoked. Full searches still require deterministic sub-500-character cells, stable-ID union reconciliation, and local exact pair checks. These are not final searches.
