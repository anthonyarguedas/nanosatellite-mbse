# EPS framework design report

`solucion.tex` develops the framework through OOSEM stakeholder analysis, black-box requirements, logical architecture, five physical alternatives, and a selected physical design. Its sections live in `sections/`.

## Baseline and decision

The problem statement and reported as-is facts come from commit `b826d9915407bbd861d8d39b2558048f3d534bdc`. `intro.tex` is unchanged. The concern presentation preserves all 144 source occurrences, 30 roots, 114 causal links and seven legacy aliases. Nested lists make the causal hierarchy visible.

The design specifies 11 mission needs, 40 framework requirements, nine logical capabilities and 40 planned verification cases. `traceability/framework-baseline.json` is the complete trace register. The report's 30 root paths are representative paths through that larger register.

PA-VS (Capella and Valispace with controlled analysis and evidence) is selected for detailed design under an explicit analyst priority to reuse documented requirements, engineering-data and verification-procedure services. This is a conditional design decision. Access, licenses, cost, exports, synchronization and independent reconstruction can reopen it. Stakeholder preference, affordability and empirical superiority are unconfirmed.

The custom PA-CDT remains the main alternative for local semantic authority and portable evidence. It retains CSRM, textual SysML v2, Python, EPS/battery models and FMI. OpenUSD, Omniverse and Isaac are activated extensions rather than requirements for every case.

All five complete allocations are in `candidates/*.json`. Their native implementation languages remain free. The SysML v2 files describe the common OOSEM study.

## Scope and evidence

Framework verification, EPS acceptance and project deliverable assessment are separate. The report specifies a design and its verification plan. No framework implementation, successful case study, flight qualification, physical safety authorization or measured cost/effort benefit is asserted.

The OOSEM chapter and the Handbook's Part One were reviewed. Central candidate claims were checked in local paper texts. Jev returned no new retrieval results. Available attempts failed with HTTP 402 or a search-helper error. The literature register preserves exact source identifiers, locations and maturity limits. Existing CSRM conversion checks establish language consistency rather than runtime evaluation or completeness.

Independent method review found seven issues. The final sources clarify mandatory exchange verification, proposed solver profiles, variation and constraint review, qualitative criteria, explicit observation/result inputs, named components and consistent verification fixtures.

## Report build

```sh
cd final_report
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Use fresh auxiliary files for a clean bibliography check. The supplied `main.pdf` is the built report. Generated LaTeX auxiliaries and the PDF are ignored by Git.

## Native models and figures

The source tree is `sysml/`. It contains the common domain, concerns, needs, requirements, logical responsibilities and planned verification. `sysml/candidates/` contains all five physical realizations and named allocations. No satisfaction assertion represents an unverified implementation.

Only three native views are included in the report:

- `ReportViews::contextView`
- `ReportViews::logicalView`
- `ReportViews::selectedPhysicalView`

The logical view is a filtered structure view. Detailed exchanges remain in the model and tables. The physical view separates workstation, hosted service and evidence storage from external specialist services. Logical responsibility groups can share hosts.

SVG and PNG are native Syside Modeler outputs. Each PDF comes from its exact native SVG through `rsvg-convert`. The manifests in `figures/sysml/` retain artifact provenance. Main labels are at least about 9 pt at report size. Compact inherited port labels are smaller and use the adjacent interface table for meaning. The logical image has a height bound to keep its caption on the page.

Recheck and render using the installed skill tool:

```sh
TOOL="$HOME/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py"
MODEL="$PWD/final_report/sysml"
CONFIG="$MODEL/syside.toml"
BUILD=$(mktemp -d)
uv run "$TOOL" doctor --json
uv run "$TOOL" check "$MODEL" --config "$CONFIG" --warnings-as-errors --json
uv run "$TOOL" inspect "$MODEL" --config "$CONFIG" \
  --max-elements 0 --max-relationships 0 --json > "$BUILD/inspect.json"
python3 final_report/tools/audit_report.py --report final_report \
  --inspect "$BUILD/inspect.json"

for entry in context:contextView:2 logical:logicalView:1 physical:selectedPhysicalView:2
do
  IFS=: read -r folder view depth <<< "$entry"
  uv run "$TOOL" render "$MODEL" --config "$CONFIG" \
    --defined-view "ReportViews::$view" --native-depth "$depth" \
    --native-expose flat --formats svg,png,pdf \
    --output-dir "final_report/figures/sysml/$folder" --json
done
```

Run these commands from the repository root. Syside 0.10.3, a working license, `uv` and `rsvg-convert` were used. No alternate renderer or SVG restyling was used.

## Checks

`tools/audit_report.py` checks source fidelity, planned concern/requirement/logical/physical/verification coverage, citation keys, the three-figure limit and optional native semantic inspection. These are document/model checks. They are not framework acceptance tests.

`validation/` records the final check summaries and provenance. Full semantic inspection output is retained outside the repository because it is large. Two existing bookmark hierarchy warnings originate in the theory/results template. The final report has no undefined citations/references or overfull boxes.
