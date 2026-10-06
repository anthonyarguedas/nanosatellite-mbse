# Native system-context render recipe

This directory contains the **single enriched context figure** used by
`fig:framework-context`. Its model-defined target remains
`ReportViews::contextView`.

The proposal is specified in the report and SysML model, not this recipe:
- `sysml/06-system-context.sysml`: existing actors/ports/interfaces and all 19
  exact typed interface flows, plus the grouped input/output projection.
- `sysml/10-interface-views.sysml`: documented typed bundles and six detailed
  actor/responsibility/check/failure/authority metadata specifications.
- `sysml/07-report-views.sysml`: the context view. Redundant interface edges are
  filtered so that only the twelve directional bundle arrows are drawn.

Run from the repository root:

```sh
TOOL=/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py
uv run "$TOOL" doctor --json
uv run "$TOOL" check final_report/sysml --warnings-as-errors --json
uv run "$TOOL" render final_report/sysml \
  --defined-view ReportViews::contextView \
  --native-depth 1 --native-expose flat \
  --config final_report/fig/sysml/context/syside.toml --warnings-as-errors \
  --formats svg,png,pdf --output-dir final_report/fig/sysml/context --json
```

SVG and PNG are native Syside Modeler 0.10.3 output. PDF is converted by the
wrapper from the exact native SVG. The native provenance manifest records its
SHA-256 and render paths. Design specifications remain in the report and model.
The native SVG and raster files are unchanged.

Reviewed at report width: payload labels are approximately 7.6 pt. Native routing
has doglegs and small intersections with the `flow` keyword. Arrowheads and data
labels remain readable. The full report build has no undefined references or
overfull boxes. Full model validation has zero diagnostics.

This enriched view replaces the earlier overview. The report uses one context
figure with complementary interface notes.
