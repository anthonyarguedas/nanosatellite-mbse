# Pilot 001

Required changes were applied in commit: NA

Export method: `~/agent-tools/internet/skills/browser/scripts/search_arxiv.py`

## Objective

Validate one representative structured-row `A1` Cartesian cell and one representative `BG1` pair cell. Use 2026-08-29 only as a diagnostic upper bound. It is not `P-001`.

The deterministic audit confirmed `P: 26`, `E_H: 38`, `M_H: 54`, and `G_model: 14` fixed literals plus `16` declared pairs. The live test intentionally used only `CubeSat`, `"electrical power system"`, and `"model-based systems engineering"` for `A1`, then `CubeSat` with the `mission-agnostic` and `model` pair.

## Runs

- [`test1.json`](searches/test1.json)
- [`test2.json`](searches/test2.json)

## Result

- [x] No guideline change needed
- [x] Document a source limitation

Both structured-row requests had exact source readback, the requested inclusive date bounds, and source totals of `0`. `test1.json` and `test2.json` are cell diagnostics. They do not cover the full Cartesian partitions, prove union completeness, test pair no-loss, or provide final capture. The 2026-08-29 bound is diagnostic only. These are not final searches.
