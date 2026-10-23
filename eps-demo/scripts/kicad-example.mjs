#!/usr/bin/env node
// Reproducible demonstration using the real sizing/suggestion engine and sourced catalog.
// Vite is used only as a local TypeScript module loader for the engine's extensionless imports.
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { createServer } from 'vite';
import { buildKiCadExport, createKiCadZip } from '../src/kicad/index.ts';

const [catalogPath, outputPath, enginePath = 'src/engine/index.ts'] = process.argv.slice(2);
if (!catalogPath || !outputPath) { console.error('Usage: node scripts/kicad-example.mjs CATALOG.json OUTPUT_DIRECTORY [ENGINE_INDEX.ts]'); process.exit(2); }
const server = await createServer({ configFile: false, root: process.cwd(), server: { middlewareMode: true, fs: { allow: [process.cwd(), path.dirname(path.resolve(enginePath)), path.dirname(path.resolve(catalogPath))] } }, appType: 'custom', logLevel: 'error' });
try {
  const engine = await server.ssrLoadModule(path.resolve(enginePath));
  const catalog = JSON.parse(await readFile(catalogPath, 'utf8'));
  const inputs = {
    mission: { name: 'COTS logical review example', altitudeKm: 550, lifetimeYears: 1 },
    scenarios: [{ id: 'illustrative-nominal', name: 'Illustrative nominal', kind: 'nominal', description: 'Authored demonstration assumptions', revision: 1,
      illuminationFactor: 1, initialEnergyFraction: 0.5, minimumEnergyFraction: 0.2, durationOrbits: 1,
      loads: [{ id: 'illustrative-load', name: 'Illustrative spacecraft load', subsystem: 'aggregate', color: '#ffffff', activePowerW: 4, idlePowerW: 2, railV: 5, essential: true,
        windows: [{ id: 'active', start: 0.1, end: 0.3 }] }], provenance: 'Authored demonstration inputs. No mission or manufacturer load profile is claimed.' }],
    activeScenarioId: 'illustrative-nominal',
    solar: { sunlightEfficiency: 0.85, eclipseEfficiency: 0.7, cellEolV: 2.22, cellEolA: 0.969, installedPowerW: 12 },
    battery: { dod: 0.3, margin: 0.2, capacityWh: 86, retainedEnergy: 0.8, chargeEfficiency: 0.95, dischargeEfficiency: 0.95, maxChargeW: 10, maxDischargeW: 20 },
    topology: { conditioning: 'MPPT', distribution: 'centralized', bus: 'regulated', efficiency: 0.9, idlePowerW: 0.25, massAllocationKg: 1 },
  };
  const orbit = engine.calculateOrbit(inputs.mission.altitudeKm);
  const budget = engine.calculateBudget(inputs.scenarios[0], orbit, inputs.topology.idlePowerW);
  const analysis = { orbit, budget, solar: engine.sizeSolar(inputs, budget, orbit), battery: engine.sizeBattery(inputs, budget, orbit) };
  analysis.suggestions = engine.suggestProducts(catalog, inputs, analysis);
  const selected = { solar: 'azur-3g30c-advanced-81780', battery: 'gomspace-bp8-100wh-8s1p', conditioning: 'gomspace-p80-config1', distribution: 'gomspace-p80-config1', processor: 'gomspace-p80-config1' };
  const evaluatedAt = new Date().toISOString();
  const records = Object.fromEntries(['mission', 'orbit', 'scenarios', 'budget', 'solar', 'battery', 'topology', 'candidates', 'simulation', 'assessment'].map(id => [id,
    { revision: 1, evaluatedRevision: ['simulation', 'assessment'].includes(id) ? null : 1, evaluatedAt: ['simulation', 'assessment'].includes(id) ? null : evaluatedAt }]));
  const allocations = [...new Set(Object.values(selected))].map(productId => {
    const product = catalog.products.find(item => item.id === productId);
    const suggestion = analysis.suggestions.find(item => item.productId === productId);
    if (!product || !suggestion) throw new Error(`Missing demonstration allocation evidence for ${productId}.`);
    return { productId, productRevision: product.revision, catalogRevision: catalog.revision,
      roles: Object.keys(selected).filter(role => selected[role] === productId), quantity: suggestion.quantity,
      origin: 'engineer-allocation', allocatedAt: evaluatedAt,
      rationale: 'Explicit local demonstration allocation of the screened concept count. No installed arrangement, compatibility or engineering approval is claimed.' };
  });
  const workspace = { schemaVersion: 1, inputs, records, analysis, selections: selected, allocations };
  const result = buildKiCadExport(workspace, catalog);
  const output = path.resolve(outputPath);
  await mkdir(output, { recursive: true });
  for (const file of result.files) await writeFile(path.join(output, file.name), file.content, { flag: 'wx' });
  await writeFile(path.join(output, 'orbitwork-review.zip'), createKiCadZip(result.files), { flag: 'wx' });
  await writeFile(path.join(output, 'catalog-snapshot.json'), JSON.stringify(catalog, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ output, logicalOnly: true, engineCalculated: ['orbit', 'budget', 'solar', 'battery', 'suggestions'], warnings: result.warnings }, null, 2));
} finally { await server.close(); }
