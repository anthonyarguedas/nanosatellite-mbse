# Developer checks

Executed on 2026-10-17 with Node.js 24.12.0, local Chrome for Testing and KiCad 10.0.7. These checks concern the prototype. They establish no framework qualification, orbit suitability, hardware conformity or flight readiness.

## Automated checks

- **214 Vitest tests passed.** Equations, exact event integration, missing evidence, catalog semantics, stale dependency closure, product replacement, historical plot context, accepted mission provenance, ZIPs and reviewed geometric rules.
- **6 Python protocol tests passed.** Local semantic-service origin restrictions, payload bounds, unavailable-model behavior and health checks.
- **2,839 catalog assertions passed.** Six products and 200 sourced specification records. Missing and inapplicable values remain distinct.
- TypeScript and production build passed. Largest JavaScript chunk is 361 kB. `npm audit` reported zero vulnerabilities.
- The LaTeX report compiled successfully with both concise additions. The existing report PDF was left unchanged.

```sh
cd eps-demo
npm test
npm run build
npm run test:catalog
(cd src/mission-assist && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_semantic_service.py)
```

## Real browser checks

The final focused pass recorded **135 passing assertion evaluations across 11 runs**, at 1440×1000 and 1280×900, on development and production builds. These counts include repeated viewport checks.

Confirmed:

- Narrow CAM windows move and resize through real pointer input. Numeric and keyboard alternatives work.
- Long check IDs remain separate from titles. N/A wording, freshness badges and guidance readability are correct.
- Mission edits and scenario changes invalidate the expected dependency closure. Historical plots retain their evaluated reserve and orbit timing.
- Actual local Qwen requests returned Proba-V, 820 km and cosine 0.664 for the vegetation example. Its non-CubeSat identity and historical orbit context remain explicit. Similarity is not a suitability probability.
- Scalar acceptance requires a checkbox and an explicit action. Only the numerical altitude changes. ConOps and its source receipt survive JSON export/import. Manual context edits clear the previous receipt.
- Lexical retrieval is explicitly labeled. Ranges remain ranges. Unrelated input abstains. Query edits cancel pending semantic results.
- Actual UI-generated KiCad ZIPs pass CRC checks and retain sources, quantities and shared physical usages. Stale or absent allocations block export.
- Null/unapproved rule templates, malformed profiles, wrong fingerprints and missing fabrication minima are rejected. Explicitly synthetic approved fixtures exercise sidecar generation. A changed fingerprint blocks stale rule downloads.
- Production chunks, charts and both lazy feature panels load without console errors or missing chunks.

The original five UI findings were fixed and verified again. The standard BIRDS-4 example was restored after testing.

### Reuse the browser regressions

Scripts are in `tests/browser/`. They use the existing local browser skill at `~/agent-tools/internet/skills/browser/scripts`, own newly created tabs, and constrain file output to their test directory. No additional app dependency or browser download is needed.

These tests replace the app's own authored test design through UI controls. Export work you want to keep before running them. They do not clear unrelated browser storage or call application hooks directly.

```sh
cd eps-demo/tests/browser
python3 chrome_probe.py --url http://127.0.0.1:5173 --viewport 1280x900 --label narrow-window --actions narrow-window.py
EPS_FINAL_PHASE=regressions python3 chrome_probe.py --url http://127.0.0.1:5173 --viewport 1280x900 --label regressions --actions final-actions.py
EPS_FINAL_PHASE=mission python3 chrome_probe.py --url http://127.0.0.1:5173 --viewport 1440x1000 --label mission --actions final-actions.py
EPS_FINAL_PHASE=kicad python3 chrome_probe.py --url http://127.0.0.1:5173 --viewport 1440x1000 --label kicad --actions final-actions.py
```

Start the app and optional semantic service first. `EPS_FINAL_PHASE=preview` tests the production preview on port 4173.

Raw local browser observations are retained in the repository's ignored `.web-content/eps-demo/ui-verification/` directory. This includes final reports, screenshots, exported inputs, ZIPs and native KiCad validation of an actual UI export.

## Native KiCad checks

The installed CLI parsed and rendered five review sheets and exported a netlist containing **zero physical components**. Six dangling hierarchical-label ERC findings are expected on the opaque logical ports and remain recorded. This is structural drawing validation, not an electrical pass. No COTS PCB exists and physical DRC was not run.

The separate synthetic rule regression deliberately creates violating geometry. KiCad reports 12 violations and one unconnected item. Eight findings name all five generated rule types. This proves that the generated syntax is applied to the fixture. It proves no real EPS rule derivation or PCB suitability.

See [KiCad commands and scope](KICAD.md).

## Unexecuted checks

Native Chrome save completion was not tested. Browser tests captured the bytes from actual UI download handlers and suppressed only the native save sink. Physical PCB routing/DRC, complete product compatibility, model credibility and qualification remain outside this demo. Semantic outage UI and artificially reordered successful replies were not exercised in the final browser pass. Protocol failures and legacy plot fallbacks have focused automated tests.
