# KiCad export and EPS rule feasibility

## Result and limits

| Scope | Feasibility and implementation |
|---|---|
| Automatically placed and wire-routed system schematic | Implemented. Real `.kicad_sch` files use hierarchical COTS usage sheets and named **logical** ports. A deterministic grid router avoids sheet bodies and existing wires. Links express proposed role associations, including software host allocation. They assert no manufacturer pin mapping or electrical compatibility. |
| Autorouted physical carrier board | Blocked by the supplied evidence. The typed architecture has no terminal/return maps, installed assembly arrangements, connector footprints, physical netlist, load channels, board outline or stackup. No COTS PCB is generated. |
| Internal COTS EPS reconstruction | Unsupported. Catalog ratings cannot reconstruct manufacturer circuits, external regulator circuitry or proprietary board copper. |
| EPS requirements informing KiCad rules | Feasible for selected geometric constraints after engineer review. A separate gated exporter emits approved bounds and provenance. All complete EPS predicates retain external assessment. |

The installed KiCad CLI and bundled Python `pcbnew` report **10.0.7**. Batch schematic rendering, netlist export, ERC and PCB DRC work locally. KiCad has no full native batch PCB autorouter. A future physical pipeline can exchange Specctra DSN/SES data with an external router, then check the imported board. `pcbnew.ExportSpecctraDSN` is present. No Freerouting installation was found in the inspected application, KiCad document or shallow home paths. Java 11 is installed. The current Freerouting README requests Java 25. Network retrieval of official documentation worked. No router or runtime was downloaded because the physical input gates already fail.

## Browser API

```ts
import {
  buildKiCadExport, createKiCadZip, getKiCadReadiness,
  getKiCadArchitectureFingerprint, buildReviewedKiCadRules,
} from './kicad';

const readiness = getKiCadReadiness(workspace, catalog);
// Show readiness.blockers if !readiness.ready.
const result = buildKiCadExport(workspace, catalog);
// result: { files: { name: string; content: string }[], warnings: string[], scope: string }
const bytes = createKiCadZip(result.files);
const blob = new Blob([bytes], { type: 'application/zip' });
```

The exporter is synchronous, pure TypeScript and browser compatible. It has no runtime dependencies or backend. The ZIP helper produces a deterministic uncompressed archive. The GUI can download the Blob and display the scope and warnings. `buildKiCadExport` throws an actionable error for stale or uncomputed prerequisites, missing outputs, absent allocations, unsupported products, rejected suggestions, known failed suggestion checks and invalid quantities.

Current records and valid inputs are required through **candidates**, including every upstream node. Simulation and assessment are unnecessary for this limited drawing. Missing pack energy can leave simulation unavailable while permitting a logical review. Incomplete product matches remain visibly incomplete. Only allocated catalog products are exported. Integrated roles share one usage and frozen concept quantity. Proposed internal role associations are recorded without fake external wires. The scenario demand sheet is explicitly authored logical demand, not another COTS product.

The manifest preserves exact catalog entry revisions, source URLs/document revisions, supported options, accounting boundaries, frozen quantities and allocation receipts, scenario provenance, missing roles, unresolved associations and all physical gates. Changing a scenario never replaces an allocated count with a new screening suggestion. Legacy selections without recorded counts block export until the engineer explicitly confirms each product allocation. Unstated hardware revisions remain unknown. A suggested cell count supplies no series/parallel arrangement. The snapshot contains the selected catalog records and calculation records for traceability.

Allocation receipts bind exact product and catalog revisions. Missing or inconsistent receipts block export. Candidate calculation records still have no separate catalog-revision field, so screening must be repeated after catalog changes. The architecture fingerprint is a deterministic traceability identifier. It provides no cryptographic signature or authenticated engineer approval.

## Local pipeline

Use Node 24 or the supported project Node version with TypeScript stripping. Run from `eps-demo/`.

```sh
# Export a current downloaded Workspace JSON. Existing output files are never overwritten.
node scripts/kicad-export.mjs workspace.json src/data/catalog.json new-export

# Parse all sheets, render SVG, export the logical netlist, retain raw ERC and a summary.
node scripts/kicad-validate.mjs new-export

# Generate an illustrative snapshot with real sizing/suggestion calculations and sourced entries.
node scripts/kicad-example.mjs src/data/catalog.json new-example

npm test -- src/kicad/__tests__
```

`KICAD_CLI` can override CLI discovery. Validation defaults to the installed macOS application, then PATH. The example script uses Vite only as a local module loader for the engine. It also accepts an explicit engine index path as its third argument.

### Current BIRDS-4 study

Load the BIRDS-4-inspired example from the canvas Project menu. Its three AZUR cells, BP8 pack and P80 assembly have explicit frozen concept counts. The overlapping-mission case proposes five cells during screening while the review drawing retains the three allocated cells. The known mass and energy findings remain separate from drawing readiness.

The current UI-generated project was parsed and rendered with KiCad 10.0.7. Its five sheets contain zero physical components and six expected dangling hierarchical-label ERC findings. No PCB or physical DRC result is produced.

### Historical review artifact

`kicad/sample/` contains the generated project, schematic and child sheets, ZIP, manifest, architecture and catalog snapshots. Its authored scenario uses actual engine calculations. It allocates three AZUR cells, one BP8 pack and one P80 configuration 1 usage. That P80 usage supplies conditioning, distribution and processor roles. This historical artifact predates frozen allocation receipts. Its count records preliminary screening data. Regenerate with the current example script to obtain explicit concept-count receipts. Neither artifact establishes a cell arrangement, selected harness or complete electrical compatibility.

`kicad/sample/validation/validation.json` records KiCad 10.0.7 invocations. All five sheets parsed and rendered. The netlist contains **zero physical components**. ERC returned **5** with **six dangling hierarchical label errors** because opaque usages contain no pin-level circuit. There are no off-grid wire warnings. All three external logical associations routed. Physical nets remain unknown. Physical DRC was **not run**. No ERC/DRC pass is claimed.

Rendered root drawing: `kicad/sample/validation/review.png`. SVGs are retained in `validation/svg/`. Optional rendering command:

```sh
rsvg-convert -b white -w 1680 new-export/validation/svg/orbitwork-review.svg -o review.png
```

`unzip -t kicad/sample/orbitwork-review.zip` passed. TypeScript checking and the targeted unit tests passed. Generated project files remain review artifacts even when opened successfully in KiCad.

## EPS requirements to physical rules

All twenty complete requirements retain external assessment. Useful KiCad contributions are narrower:

| Requirements | KiCad contribution | Required external evidence |
|---|---|---|
| EPS-01, 05, 16–18 | Reviewed connectivity, correct pin types, ERC and schematic/PCB parity | Supported configurations, charger policy, thresholds, inhibit truth tables, protocol and service behavior |
| EPS-03, 04, 06, 07, 13–15 | Approved trace width, via geometry, electrical spacing and selected layout constraints | Current/pulse envelope, voltage drop, converter limits, thermal model and protection coordination |
| EPS-20 | Supplied board edge, keep-out and courtyard geometry | Complete 3D installation, stack height, connector access, deployment and array packing |
| EPS-02, 08–12, 19 | No equivalent generic ERC/DRC predicate | Generation, capacity, cycle life, scenario energy/charge, recovery and unique-usage resource budgets |

Current-to-width derivations require copper thickness/layers, temperature limits and rise, thermal environment, load duration, path length, accepted method, fabrication tolerances and margins. Via decisions also need plating, drill, annular geometry, count and current sharing. Voltage-to-spacing derivations require differential voltage/transients, insulation and creepage criteria, environment, material/coating assumptions and an accepted standard. The exporter performs **no amperes-to-width or volts-to-clearance conversion**. A minimum drill is no via-current rating.

### Approved rule input

`ReviewedPhysicalRules` and `ApprovedDimension` are exported TypeScript schemas in `src/kicad/rules.ts`. They require an architecture fingerprint, catalog and physical netlist revisions, engineer approval/date, exact physical nets, source URL/revision/location, fabrication minima and per-value EPS references, rationale, derivation method, conditions and margin. Five exercised constraints are supported: `track_width`, `clearance`, `via_diameter`, via-scoped `hole_size`, and `edge_clearance`.

```ts
const result = buildReviewedKiCadRules(reviewedRules, currentArchitectureFingerprint);
// NEW orbitwork-physical-rules.kicad_pro, same-basename .kicad_dru and provenance manifest.
```

```sh
node scripts/kicad-rules.mjs unzipped-architecture reviewed-rules.json new-rules-directory
```

The CLI compares the snapshot, manifest and supplied rule fingerprint. Values below supplied fabrication minima, stale bindings, unknown/overlapping nets, missing derivations and inconsistent via/drill/annular bounds block generation. Missing netclass assignments are retained as unresolved. Exact literal net names are supported, with no wildcard or regular-expression input. The generated custom rules use exact net-name conditions. Larger clearance bounds take priority where two classes meet.

Netclass width/via sizes are routing defaults. Custom rules enforce their approved limits. Sidecars share the eventual board basename and need a deliberate merge into an existing physical project. No existing project is overwritten. No approved physical values means no EPS-derived physical rule files. No PCB or route is generated by this API.

### Rule enforcement regression

```sh
node scripts/kicad-rule-probe.mjs new-probe-directory
```

The probe uses bundled KiCad Python to create **synthetic, deliberately violating geometry** and the real rule exporter. `KICAD_PYTHON` and `KICAD_CLI` are optional overrides. `kicad/rule-probe/` retains all test inputs, outputs and reports. Every numeric value and approval record there is synthetic test data, with no engineering authority.

KiCad 10.0.7 reported 12 violations and one unconnected item. Eight violations explicitly named the five generated rules: three widths, two clearances, one via diameter, one drill and one board edge. This proves rule application on the fixture. It proves no COTS PCB feasibility. Ignored checks are retained, including the default ignored missing-courtyard check.

**CLI caveat:** independent probes found that KiCad can produce a normal DRC report while silently ignoring an invalid custom-rule file. Use the GUI's **Check rule syntax**, restricted generated syntax and a perturbed-fixture coverage test. A successful process, ordinary report or exit code alone establishes no rule loading. A board DRC pass leaves known EPS failures unchanged and supplies no flight qualification.

## Sources

- Schematic grammar: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/
- KiCad 10 custom rules and precedence: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#custom-design-rules
- Netclass defaults: https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#board-setup-net-classes
- ERC scope: https://docs.kicad.org/10.0/en/eeschema/eeschema.html#erc
- DRC CLI: https://docs.kicad.org/10.0/en/cli/cli.html#_pcb_drc
- Freerouting DSN/SES and runtime: https://github.com/freerouting/freerouting

Exact product sources are preserved in the sample manifest. Retrieved schematic/Freerouting documentation is retained under `kicad/references/`. Requirement mapping and the independent rule parser probes were reviewed from the parallel KiCad rules assessment. No manufacturer pin-level data was invented.
