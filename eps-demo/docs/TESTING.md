# Developer checks

Flow UI verified on 2026-10-23 (UTC) with Node.js 24.12.0 and local Chrome for Testing. Earlier native validation used KiCad 10.0.7. These checks concern the prototype. They establish no framework qualification, hardware conformity or flight readiness. `final_report/` remains unchanged.

## Automated checks

- **390 Vitest tests passed across 39 files.** Numerical integration, independent sizing, stale evidence, catalog coverage, exact-role allocation, source identity, frozen quantities, catalog upgrades, serialization and KiCad exports/rules. Flow tests cover task/help classification, complete live evidence, branch replacement, session invalidation and lossless editable text. Geometry fixtures cover local trees, deterministic camera framing, obstacle-aware orthogonal routes, safe label footprints and nested disclosure focus visibility.
- **Catalog integrity passed:** 34 records and 1,620 specification records.
- **Strict comparison coverage passed:** three distinct covered choices for every six-role CSRM group. Membership alone never satisfies the target.
- The reviewed register contains 156 contextual source identities and 129 distinct content hashes. Source researchers and integration checks matched the referenced local bytes. Independent reviews checked the six strongest solar/storage records and four final electronics additions against primary evidence.
- TypeScript and the production build passed. The detailed catalog is a separate asset (about 848 kB minified, 107 kB gzip). Vite reports its intentional large-data-chunk warning. Raw source PDFs and archives are not bundled.
- All six Python semantic-service protocol tests passed again with a fake embedder. They load no model and access no corpus. Actual semantic retrieval was not rerun for this UI acceptance.

```sh
cd eps-demo
npm test
npm run test:catalog
npm run catalog:coverage:strict
npm run build
(cd src/mission-assist && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_semantic_service.py)
```

Coverage checks preserve source meanings, missing/NA distinctions, units, conditions, source references, actual document/repository revisions and reviewed hashes. They accept signed coefficients and explicit interval/tuple forms. They do not manufacture battery efficiencies, retained energy, chip/module mass, supported firmware hosts or guaranteed bounds.

The comparison set distinguishes bare cells, complete modules, integrated assemblies, controller boards, firmware, external services and a callable EPS API. Load converters do not become solar MPPT receivers. The published BIRDS assembly remains reference-only. One-cell nominal energy does not become a characterized multi-cell pack.

## Browser checks

### Final flow refinement acceptance

Independent final QA reran the current actions in installed shared local Chrome with owned tabs, fresh preview origins on ports 5591–5611 and `caffeinate -dims`. **1,241 checks passed across eleven runs.** Every run had empty console/runtime diagnostics. Bulk runs used `--no-screenshots`. The user's `127.0.0.1:5173` storage was untouched. All owned tabs and preview servers were closed. The user's app and shared Chrome remained running.

| Run | Checks | Measured result | Artifact directory under `tests/browser/artifacts/` |
| --- | ---: | --- | --- |
| 1280 × 800 compact fit | 245 | 119 primary pane visits | `20261023T044927.943465Z-qa-refine-final-compact-1280x800` |
| 390 × 844 narrow fit | 126 | 119 primary pane visits | `20261023T044927.957056Z-qa-refine-final-narrow-390x844` |
| 1280 × 800 integration | 160 | 64 primary pane visits, real edits and exports | `20261023T044927.930639Z-qa-refine-final-integration-1280x800` |
| 1440 × 900 review regressions | 162 | 69 primary pane visits, live evidence and session reset | `20261023T044927.933518Z-qa-refine-final-review-1440x900` |
| 1280 × 800 text boundary | 97 | 30 primary pane visits, native 2,000-character boundary | `20261023T044927.912362Z-qa-refine-final-text-limit-1280x800` |
| Mounted graph geometry | 106 | 23 geometry visits, zero node overlaps or path/node intersections | `20261023T044927.915175Z-qa-refine-final-geometry-1440x900` |
| Rendered labels | 144 | 23 label visits, 45 rendered labels, zero collisions or clipping | `20261023T044927.919613Z-qa-refine-final-labels-1440x900` |
| 390 × 844 modal keyboard | 21 | Completed and missing-input budgets, help open and closed | `20261023T044927.923355Z-qa-refine-final-modal-390x844` |
| 1280 × 800 native keyboard | 32 | Tab/Shift+Tab reveal, form keys, Escape and focus restoration | `20261023T044927.910952Z-qa-refine-final-keyboard-1280x800` |
| 1280 × 480 fallback | 2 | 257 px body, 439 px content, accessible `overflow:auto` | `20261023T044927.944245Z-qa-refine-final-short-1280x480` |
| 1440 × 900 help invariants and visual review | 146 | 24 disclosures, fresh overview/battery/window captures | `20261023T045043.535343Z-qa-refine-final-help-visual-1440x900` |

Across all saved `pane-fit.json` files, **489 primary pane measurements had 0 px overflow and zero clipped controls**. Body heights were 577–638 px at compact desktop, 677–738 px at full desktop and 661–728 px at narrow width. These measurements concern primary forms with supplemental help collapsed. Open explanatory help intentionally scrolls. Closed disclosure descendants are excluded from visible-control geometry.

The starting view retains exactly ten engineering activities and no pane. Editors, plots, findings and meaningful review records retain graph nodes. Equations, scope, traces, references and read-only explanatory text live in accessible pane disclosures. They add no paragraph nodes. Child tasks form local trees, with explicit ports and orthogonal routes. The selected path and breadcrumb retain local context. Fit frames a branch. Home restores the overview. Close preserves the branch. Narrow views intentionally allow panning at readable scale.

### Geometry, help and focus

Mounted DOM/SVG measurements cover all ten roots, all nineteen core relationships, deep window and property branches, Back, repeated selection, Home and responsive orientation changes. Both backbone and full-relationship views have zero measured node overlaps and zero paths through unrelated nodes. Toggling relationship visibility preserves retained routes. The label run checks horizontal and vertical layouts, node/label and label/label clearance, and complete viewport visibility. Unsafe or clipped visible labels are omitted. Full exchange descriptions remain accessible. Full-relationship mode may contain perpendicular wire crossings.

The independent help supplement opened 24 live disclosures across activities, mission reference/study context, product/property/source evidence, provenance, findings, retrieval and scheduling. Every opening preserved exact graph identities, positions, route paths, camera transform and the complete saved workspace, including revisions. It exposed 25,850 characters in total, including a 2,644-character section. Ordinary numeric editing and recomputation also preserved exact positions, routes and camera. Review regressions independently confirmed that open criterion details refresh after recalculation and that the complete 626-character P60 property value remains accessible.

Native narrow keyboard checks cover forward/reverse modal boundaries with help closed, open and reclosed. They include a new design whose Calculate button is disabled. Enter opens the disclosure, upstream actions navigate, and Escape dismisses the modal. Desktop checks preserve graph reveal, form-key isolation and trigger restoration.

The final QA owner opened and visually inspected the fresh overview, battery and deep-window PNGs. Parent/child placement and the dotted junction spines are readable. The deep window highlights its local task path while owner-level exchanges remain subdued. The README images are exact copies of `01-entry.png` and `03-deep-window-current.png` from the help/visual directory above.

### Retained workflows and text limits

The integration run exercises numeric edits, native pointer/keyboard window editing, independent case/load/window creation and removal, lossless Unicode text, exact-role allocation, frozen receipts, JSON replay and recomputation. It inspects bytes from real UI-generated KiCad ZIP, rule-template JSON and rule-sidecar ZIP actions. Unapproved rules remain gated. Imported rule state survives child navigation. Synthetic approval fixtures are test data with no engineering authority.

Review regressions cover live check/criterion refresh, role-specific evidence, assessment-filter isolation and complete property facets. Mission consent survives child navigation and failed import. Successful same-query import, New design and example replacement clear transient results and consent. Equal-input replacement also clears imported physical-rule state.

Long editable text retains a **2,000-character whole-field limit**, shared across its connected editing parts. The unchanged native boundary action passed all 97 checks again. Paste admitted 2,000 of 2,001 characters before blur. Appending to another part at the full limit was blocked. Shortening, later Unicode edits, tail insertion, JSON export/import and reload preserved exact complete text. Read-only pane evidence has no matching display truncation. Inspect the text run's `text-limit-observations.json`, `tail-insertion-draft.json` and `boundary-2000.json`.

These are new independent final runs. The implementation handoffs separately reported 942 broad Chrome checks and 197 focused label/keyboard checks. Those earlier totals are not included in the 1,241 checks above. Current unit/build/catalog/strict-coverage checks all passed again. SHA-256 comparison found all 122 protected baseline files checked unchanged, including engine, state, data, catalog, retrieval, KiCad, workflow, types, dependencies and global styles. The report remains unchanged.

Registry tests establish record reachability. Chrome interaction covers representative catalog/source records. Native browser 200% zoom, touch hardware, native select-menu operation, native OS saving and optional live semantic retrieval remain unverified in this acceptance.

### Retained catalog evidence

Earlier browser acceptance of the prior UI confirmed the following data behaviors. These results retain their earlier scope. The changed-catalog migration was not repeated through the new graph.

- All six roles expose at least three covered comparison options. Core coverage, richer gaps and incomplete architecture screens remain distinct.
- Each of the three Saft cells transfers its published nominal Wh with provenance. Unpublished retention and efficiencies remain missing in the catalog and assumed in the energy-only case.
- Processor/software suggestions use exact roles. Shared EPS assemblies count once. Software allocation establishes no execution or verified host compatibility. BIRDS reference data cannot become a characterized purchased battery.
- A real pre-update design retained authored inputs, selections and counts after the catalog upgrade. Review blocked simulation until the three existing products were reapplied.
- Earlier numerical acceptance preserved required array power **4.320456 W**, required battery energy **4.759773 Wh** and average budget **2.0745 W**. Existing engine/state tests continue to cover those semantics.

### Reproduce on isolated origins

Build once. Start a dedicated preview in a separate terminal. Choose a free port and keep development storage untouched.

```sh
cd eps-demo
npm run build
npm run preview -- --host 127.0.0.1 --port 4191 --strictPort
```

Start a preview on each chosen port before running its matching command below. Use fresh origins for independent suites. Sequential runs need only one server at a time. Stop each server when its run finishes. These scripts mutate the test design through real controls.

```sh
cd eps-demo/tests/browser
python3 chrome_probe.py --url http://127.0.0.1:4191 --viewport 1440x900 --label flow-fit --no-screenshots --actions flow-only.py
python3 chrome_probe.py --url http://127.0.0.1:4193 --viewport 1280x800 --label flow-fit --no-screenshots --actions flow-only.py
python3 chrome_probe.py --url http://127.0.0.1:4195 --viewport 390x844 --label flow-mobile --no-screenshots --actions flow-only.py
python3 chrome_probe.py --url http://127.0.0.1:4197 --viewport 1280x800 --label flow-integration --no-screenshots --actions flow-only-integration.py
python3 chrome_probe.py --url http://127.0.0.1:4199 --viewport 1440x900 --label flow-review --no-screenshots --actions flow-only-review-regressions.py
python3 chrome_probe.py --url http://127.0.0.1:5193 --viewport 1280x800 --label flow-keyboard --no-screenshots --actions flow-only-keyboard.py
python3 chrome_probe.py --url http://127.0.0.1:5195 --viewport 1280x480 --label flow-short --no-screenshots --actions flow-only-low-height.py
python3 chrome_probe.py --url http://127.0.0.1:5191 --viewport 1440x900 --label flow-visual --actions flow-refine-visual.py
python3 chrome_probe.py --url http://127.0.0.1:5197 --viewport 1280x800 --label text-limit --no-screenshots --actions flow-only-text-limit.py
python3 chrome_probe.py --url http://127.0.0.1:5199 --viewport 1440x900 --label geometry --no-screenshots --actions flow-refine-geometry.py
python3 chrome_probe.py --url http://127.0.0.1:5201 --viewport 1440x900 --label labels --no-screenshots --actions flow-refine-labels.py
python3 chrome_probe.py --url http://127.0.0.1:5203 --viewport 390x844 --label modal --no-screenshots --actions flow-refine-modal-keyboard.py
```

`flow-refine-visual.py` captures the overview, focused battery task and deep window editor. The final QA supplement used the same real graph controls and retained its action file as ignored `artifacts/qa-final-help-visual.py`. The old `graphical-workflow.py`, `catalog-enrichment.py` and tab-based scripts address previous UI layouts. They are historical checks, not acceptance commands for this design.

`chrome_probe.py` wraps the installed shared-browser runner in `caffeinate -dims`. It creates and closes its own tabs. URLs must use an explicit unprivileged port on `http://127.0.0.1` without credentials. Clicks, drags, text entry and keyboard traversal use native CDP input. Selects use the DOM control's standard input/change boundary because inactive macOS native menus did not commit CDP keyboard choices. Tests never call React hooks or write application state directly.

Ignored `tests/browser/artifacts/` retains checks, diagnostics, DOM projections, `pane-fit.json`, `pane-fit-summary.json` and actual export bytes. The mobile fit run records vertical geometry and asserts document width. Its saved geometry was independently checked for vertical overflow and clipping. `--no-screenshots` avoids screenshot IPC. Snapshot collection never awaits background animation frames.

## Native KiCad and limits

UI-generated review archives retain exact sources, allocation snapshots and frozen quantities. Native validation parses/renders five sheets with zero physical components. Six dangling hierarchical-label ERC findings remain expected for opaque logical usages. No physical PCB or physical DRC result is produced.

Native Chrome save completion is untested. Download checks capture bytes from real UI Blob handlers. No researched firmware was flashed, independently built or executed on hardware. Full electrical/thermal behavior, charge-based SoC, mission aging, software WCET, model credibility, MIL/SIL and qualification remain outside this demo.
