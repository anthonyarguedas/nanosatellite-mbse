# EPS case studies

These cases execute the public framework with BIRDS-derived and OreSat-derived verification inputs. They assess calculation agreement under explicit conditions. They do not reconstruct either flown mission or qualify hardware.

## Run

Use Python 3.12 and NumPy 2.5.4 (`requirements.txt`). From this directory:

```sh
python3 -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 python3 run_case_studies.py
PYTHONDONTWRITEBYTECODE=1 python3 audit_execution.py
PYTHONDONTWRITEBYTECODE=1 python3 render_evidence.py
```

After reviewing the generated values, refresh the report appendix with:

```sh
cp case-study-evidence.tex ../../../case-studies-appendix.tex
```

The driver locates the framework through its repository ancestors. For a separate evidence bundle, set `EPS_FRAMEWORK_ROOT` or pass `--framework-root /path/to/nanosatellite-mbse`. `--output` selects another output directory. The default is `executed/`.

The audit performs a second full execution in `rerun/`, checks six result files byte for byte and observes a bounded public-API probe without modifying the framework. `--reuse-replay` checks an existing replay. Source hashes identify the tested implementation. No browser, GUI or screenshots are required.

## Inputs and references

- `case_inputs.py` supplies the electrical baselines, alternatives and provenance.
- `run_case_studies.py` constructs models, binds inputs, evaluates requirements and records actual outputs.
- `independent_reference.py` contains separate decimal arithmetic and uniformly sampled Cartesian orbital references. It imports no framework code.
- `sources/oresat-solar-sweep.xlsx` retains the original published spreadsheet used by the partial-curve and power-product checks. Its source URL, worksheet, units and original order are retained in the input record.
- Manufacturer and mission report URLs are given in the source register. Their PDFs are not needed to execute the retained cases.

The BIRDS load profile approximates three published power levels: 428 mW for OBC/EPS/FAB, 144 mW for UHF reception and 280 mW for CW transmission. The executed voltage/current pairs give 429, 145.2 and 280 mW. The separate sunlight/eclipse duty fractions are assumptions. The published consumption table is on presentation page 9. Original execution locator strings referring to page 5 for these load products are inaccurate. Numerical inputs and execution records are unchanged by this reporting correction.

The mass cases and electrical cases have separate boundaries. BIRDS first checks the published 162 g cell sum, then a supplied EPS estimate. OreSat mass uses the historical 2016 modules. Its solar occupied volume uses eight assumed 100 × 100 × 3 mm module envelopes, including boards and components, rather than a thin-cell-only volume. Together with the other supplied volumes, the EPS estimate is 450 cm³ against a 500 cm³ allocation. Those estimates are assumptions, not published mission volumes or mechanical qualification results.

The electrical cases assess representative sections. BOL and EOL array runs share their mission/load conditions. Increased-series and silicon alternatives have explicitly deployed layouts. OreSat storage retains separate branch current limits and sums stored energy. A separate charger-endpoint check preserves the 4.20 V per-cell versus 4.10 V nominal protection conflict.

## Records

`executed/` contains the complete inputs, numerical comparisons, engineering verdicts, model bindings and summary. Each comparison identifies its reference basis, actual framework provider, units, numerical rule or exact status rule, and outcome. The distinction between an infeasible design and an incorrect calculation is retained.

`audit.json` records deterministic replay and live-call checks. `findings.md` gives a detailed working account. `report_fragment.py` renders the report-facing appendix, while `render_evidence.py` also renders an expanded working appendix. The report-facing fragment groups evidence by FR-12 and FR-14 to FR-20. It gives essential inputs, maximum per-requirement deviations and selected reference/framework comparisons. Repeated outputs, expected failure records and the full OreSat sweep are omitted from the report. The complete records, original sweep and expanded working appendix remain available for audit. No local audit paths or source hashes appear in the report.

The case studies use declared three-anchor PV approximations and supplied lifetime fits, efficiencies, allocations, receiving limits and some protection settings. BIRDS' published 1.575 W measured peak remains unreconstructed. No chronological energy delivery, tracker dynamics, detector tolerance qualification or complete flight architecture is inferred.
