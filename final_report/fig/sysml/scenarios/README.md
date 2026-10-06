# Native OOSEM scenario action flows

Source: `final_report/sysml/09-scenarios.sysml`, package `ScenarioViews`.

| Scenario action definition | Model-defined view | Artifact stem |
| --- | --- | --- |
| `ScenarioViews::'SC01 / UC01'` | `ScenarioViews::sc01View` | `09-scenarios-defined-view-scenarioviews-sc01view` |
| `ScenarioViews::'SC02 / UC02'` | `ScenarioViews::sc02View` | `09-scenarios-defined-view-scenarioviews-sc02view` |
| `ScenarioViews::'SC03 / UC03'` | `ScenarioViews::sc03View` | `09-scenarios-defined-view-scenarioviews-sc03view` |

Each stem has native SVG and PNG, PDF converted by the wrapper from that exact
SVG, and a provenance manifest. These files are not post-processed. The scenarios
are planned behavior, not simulation/test results, accepted baselines, or proof
that physical work has been authorized or performed.

## Reproduce from the repository root

```sh
TOOL=/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py
uv run "$TOOL" check final_report/sysml --warnings-as-errors --json
uv run final_report/sysml/check_scenarios.py --tool "$TOOL"
for VIEW in sc01View sc02View sc03View; do
  uv run "$TOOL" render final_report/sysml/09-scenarios.sysml \
    --include final_report/sysml \
    --defined-view "ScenarioViews::$VIEW" --native-depth -1 \
    --config final_report/sysml/scenarios.toml \
    --formats svg,png,pdf --output-dir final_report/fig/sysml/scenarios --json
done
```

The existing context participants supply the framework, engineers, reviewers and
facility. The new safety authority is an external review role. Every system
function and external call has responsibility metadata and a matching allocation.
External calls invoke the named external action definitions rather than changing
metaclass merely to obtain a color.

## Native ownership/style bridge

`FrameworkAction` / `ExternalAction` metadata records the reflected performer and
intended fill color. The scoped `scenarios.toml` uses native metaclass style groups:

- `ActionUsage`: blue `#DCEEF8`, framework functions.
- `PerformActionUsage`: amber `#FFF0D6`, external actor behavior calls.

This is **not** selection by arbitrary metadata, and no custom `RenderStyle`
annotation is claimed to be consumed by Syside. The focused semantic check loads
the complete report model with the licensed wrapper, evaluates the metadata with
Syside's compiler, and checks 24 task kinds, colors, performer references, behavior
definitions and allocations against the native style selectors.

Syside 0.10.3 did not render implicit conditional-successions' links in the local
probe. Each conditional succession therefore explicitly names an optional
`[0..1]` succession and binds it to its inherited `transitionLink`. This is the
same guarded HappensBefore link: the Kernel library's
`TransitionPerformances::TPCGuardConstraint` still constrains it. It is not an
additional unconditional route or a display-only arrow. The semantic check also
verifies all 14 links' endpoints, optionality, bindings and guard labels against
the actual conditional expressions.

## Report-page presentation

The native CLI lays out the complete flows horizontally. The report includes
three sequential viewports of each **unchanged native PDF**, at a common scale
within each figure. Only `graphicx` clipping is used; there is no SVG recoloring,
redrawing, separate renderer, or replacement of the modeled control flow. The
captions and lead-in explain continuation between panels; `FW` and actor-role
labels preserve ownership without reliance on color.

Current viewport bounds, in native SVG coordinates (x increases left to right,
y increases top to bottom):

| View | Panel (a) x | Panel (b) x | Panel (c) x | All panels y |
| --- | --- | --- | --- | --- |
| sc01View | 40–470 | 470–950 | 950–1500 | 130–245 |
| sc02View | 40–512 | 512–1096 | 1096–1344 | 130–247 |
| sc03View | 40–513 | 513–968 | 968–1577 | 130–307 |

At the report's measured text width of 469.19 pt, native 10 px labels print at
approximately 8.53 pt, 8.03 pt and 7.70 pt respectively. Crops preserve every task,
decision, guard label and named start/done node; only diagram framing is omitted.
If a model edit changes layout, regenerate and review the LaTeX viewports rather
than assuming these coordinates remain correct. The whole native diagram remains
available in all three artifact formats.

## Checks performed

- Full report model: zero semantic warnings/errors with warnings treated as errors.
- Semantic ownership/color/guard consistency: 24 tasks and 14 guarded links.
- Negative color fixture: intentionally changed native fill rejected by the check.
- Native SVG/PNG/PDF renders and SVG/PDF-source SHA-256 provenance verified.
- Focused LaTeX build using the report preamble, bibliography and owned block;
  page-size raster review of the three printed figures.

Audit tooling, expected figure counts, and other report/model sections are outside
this task and are not changed here.
