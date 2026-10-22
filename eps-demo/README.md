# Orbitwork

A local proof of concept for the EPS design methods in [`final_report/design-proposal.tex`](../final_report/design-proposal.tex).

![EPS dependency graph and evolving COTS architecture](docs/images/workbench.png)

Illustrative catalog allocations, with unresolved assessments and known resource-budget failures. This is not the BIRDS-4 flight architecture. [View the graphical scenario editor](docs/images/scenarios.png).

## Run

Requires Node.js 22.12+ or 24+ and npm.

```sh
cd eps-demo
npm ci
npm run dev
```

Open **http://127.0.0.1:5173**. EPS calculations, the catalog, KiCad exports and lexical retrieval run in the browser. No account or API key is needed. Manufacturer links open external source documents.

For real semantic mission retrieval, run this in a second terminal:

```sh
npm run assist:serve
```

The optional loopback service uses the existing research Python environment and cached Qwen model. It downloads no model and sends no text to a cloud service. `EPS_PYTHON` and `HF_HOME` can select another prepared environment. Explicitly choose **Lexical TF-IDF** in the GUI for immediate offline retrieval without Python. See [mission assistance](docs/MISSION-ASSIST.md).

```sh
npm test         # numerical, data and workflow checks
npm run build    # TypeScript and production build
npm run preview  # preview the build locally
```

## Try the demo

1. Load the example. Mission, orbit, scenario, and preliminary sizing nodes are evaluated. COTS screening is ready.
2. Open **Scenarios**. Drag or resize a component's active interval. Numeric window controls provide an alternative. Active power replaces idle power. Overlapping intervals count once.
3. Return to **Design graph**. Changed dependencies turn amber. Previously computed values remain visible as stale history. Run ready nodes to recompute in dependency order.
4. Inspect **COTS catalog** suggestions and their evidence gaps. Allocate a product to the architecture. A sourced battery pack rating updates the battery capacity. Published cell EOL data, where available, updates preliminary cell sizing. Reevaluate after a substitution.
5. Open the energy-balance node. Compare generation, demand, stored energy, reserve, and orbital replenishment. Try the BIRDS-4 overlapping-mission and reduced-generation scenarios.
6. Open **Assessments**. Each EPS requirement has a scoped pass, fail, or unassessed verdict. Missing characterization remains visible.
7. If orbit is unknown, open the mission node and **Explore mission analogues from ConOps**. Searching leaves numerical inputs unchanged. Explicit acceptance transfers a sourced scalar altitude and retains its evidence. Editing ConOps is an authored context change and marks dependent calculations stale.
8. Use **KiCad review & design rules** in the architecture pane. Current COTS allocations can produce a native, automatically placed and logically routed review project. Physical PCB routing remains blocked until reviewed pin maps, footprints, connectivity and board constraints exist.

The right pane keeps all six CSRM EPS groups visible on every tab. An integrated board can cover several logical roles. It remains one physical usage.

**New design** clears the authored model. **Load example** replaces it with demonstration inputs. Export JSON before replacing work you want to keep. Inputs and allocations persist locally in this browser. Calculations are deliberately recalculated after reload and JSON import. Invalid files leave the current design intact.

## Implemented scope

- Circular orbit period and the proposal's fixed sunlight/eclipse geometry.
- Phase-resolved energy from constant-power load modes and graphical schedules.
- Preliminary array power, integer cell lower bound, battery energy, and mission cycle count.
- Explicit MPPT/DET, transfer and bus choices. These are logical architecture choices. The energy demo uses a constant-efficiency MPPT model.
- Bounded screening of a small, revisioned manufacturer catalog. Fixed panels and packs keep their purchased properties. Missing evidence and known violations have distinct outcomes.
- An energy-only time history with exact schedule/eclipse boundaries, battery efficiencies, charge acceptance, retained capacity, curtailed surplus and retained shortages.
- Transitive stale marking, dependency gating, snapshot-aware historical plots, explicit product allocation and a six-role architecture view.
- Eight sourced mission analogues, local Qwen semantic embeddings and cosine similarity, explicit lexical mode, acceptance receipts and JSON persistence.
- Native KiCad review-project ZIP export with automatic logical wire routing and deduplicated COTS usages.
- Gated translation of engineer-approved physical dimensions into five KiCad rule types, with requirement and source traceability. No current-to-width or voltage-to-clearance conversion is invented.
- A scoped review of EPS-01 through EPS-20. Partial calculations never establish complete requirement conformity or qualification.

See [model scope and equation traceability](docs/SCOPE.md), [catalog sources](src/data/CATALOG-SOURCES.md), [mission retrieval](docs/MISSION-ASSIST.md), [KiCad feasibility and pipeline](docs/KICAD.md), and [developer checks and browser regressions](docs/TESTING.md).

Local KiCad commands (Node.js 24+, installed KiCad CLI):

```sh
npm run kicad:export -- exported-design.json src/data/catalog.json new-kicad-export
npm run kicad:validate -- new-kicad-export
npm run kicad:rules -- new-kicad-export reviewed-rules.json new-rule-files
```

The GUI rule-input template deliberately contains null physical values and no approval. The example rule-regression geometry is synthetic test data, not EPS engineering evidence.

## Important boundaries

Example activities are based on BIRDS-4. Their load powers, schedules and default efficiencies, EOL source power, battery retention, DoD, reserve and power limits are **editable engineering assumptions**. They are not flight telemetry or datasheet evidence. See the [BIRDS-4 scenario basis](src/data/BIRDS4-SCENARIOS.md). Selecting a catalog product does not supply its missing characterization. Only available published cell EOL values and pack energy are transferred automatically. Conditioning losses, EPS idle demand, battery efficiencies, retention and operating-state applicability remain explicit engineer inputs. Review them against the chosen products.

The graph plots **stored energy**, not charge-based state of charge. Charge SoC, voltage-dependent battery behavior and cycle-life compliance remain unassessed without applicable data. A known energy shortage can still fail a requirement. Margin is applied once in preliminary sizing. The physical EOL simulation uses retained energy directly.

Only the selected scenario is evaluated at a time. Separate scenario revisions are retained in the authored model. The demo makes no claim that all mission scenarios pass together.

No SysML execution, flight verification, thermal solver, full installation geometry, physical PCB generation, detailed protection, software synthesis, hardware control, live procurement, global optimization or future framework integrations are implemented. The CSRM view and KiCad drawing show logical allocations. Developer tests do not establish framework qualification or flight readiness.

The CSRM role structure is adapted from the INCOSE Space Systems Working Group and OMG Space Domain Task Force reference model, licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The report retains the source citations.

## Code layout

- `src/engine/`: pure calculations and bounded catalog evaluation.
- `src/workflow.ts`: graph definitions, input gates and dependency traversal.
- `src/state/`: revisioned workspace, safe JSON boundary and local persistence.
- `src/components/`: graph, inspectors, catalog, timeline editor and architecture view.
- `src/data/`: sourced COTS and mission catalogs, plus BIRDS-4-inspired scenario assumptions.
- `src/mission-assist/`: vector retrieval, acceptance boundary and optional local semantic service.
- `src/kicad/`, `scripts/kicad*.mjs`: native review drawings, ZIPs, reviewed rule translation and local validation.

The report and existing research artifacts are unchanged by this demo.
