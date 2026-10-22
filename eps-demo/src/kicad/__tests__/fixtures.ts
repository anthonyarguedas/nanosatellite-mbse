import type { Catalog, NodeId, Product, Workspace } from '../../types';

export function fixture(): { workspace: Workspace; catalog: Catalog } {
  const source = { id: 'test-source', title: 'Synthetic test evidence', url: 'https://example.org/test', revision: 'test-document-1', location: 'Fixture only', retrievedAt: '2026-10-17' };
  const common = { revision: 'test-record-1; hardware revision unknown', manufacturer: 'Synthetic test maker', partNumber: 'TEST', description: 'Authored unit test data, no real product claim', specs: {}, sources: [source], supportedConfigurations: ['Unselected test configuration'], accountingBoundary: 'Whole test item, excludes harness', caveats: ['No pin maps'] };
  const products: Product[] = [
    { ...common, id: 'test-solar', name: 'Test solar source', level: 'cell', roles: ['solar'] },
    { ...common, id: 'test-pack', name: 'Test battery', level: 'pack', roles: ['battery'] },
    { ...common, id: 'test-board', name: 'Test integrated EPS', level: 'board', roles: ['conditioning', 'distribution', 'processor'] },
    { ...common, id: 'unused', name: 'Unallocated product', level: 'board', roles: ['conditioning'] },
  ];
  const records = Object.fromEntries(['mission', 'orbit', 'scenarios', 'budget', 'solar', 'battery', 'topology', 'candidates', 'simulation', 'assessment'].map(id => [id, { revision: 2, evaluatedRevision: 2, evaluatedAt: '2026-10-17T00:00:00Z' }])) as Workspace['records'];
  const workspace: Workspace = {
    schemaVersion: 1,
    inputs: {
      mission: { name: 'Synthetic review fixture', altitudeKm: 550, lifetimeYears: 1 },
      scenarios: [{ id: 'test-scenario', name: 'Synthetic scenario', kind: 'nominal', description: 'Test only', revision: 1,
        illuminationFactor: 1, initialEnergyFraction: 0.5, minimumEnergyFraction: 0.1, durationOrbits: 1,
        loads: [{ id: 'load', name: 'Test load', subsystem: 'test', color: '#ffffff', activePowerW: 1, idlePowerW: 0.2, railV: 5, essential: true, windows: [] }], provenance: 'Authored test assumptions' }],
      activeScenarioId: 'test-scenario', solar: { sunlightEfficiency: 0.8, eclipseEfficiency: 0.7, cellEolV: 2, cellEolA: 0.5, installedPowerW: 10 },
      battery: { dod: 0.3, margin: 0.2, capacityWh: 20, retainedEnergy: 0.8, chargeEfficiency: 0.9, dischargeEfficiency: 0.9, maxChargeW: 5, maxDischargeW: 10 },
      topology: { conditioning: 'MPPT', distribution: 'centralized', bus: 'regulated', efficiency: 0.9, idlePowerW: 0.1, massAllocationKg: 1 },
    }, records,
    analysis: {
      orbit: { periodS: 6000, sunlightS: 4000, eclipseS: 2000, orbitsPerDay: 14.4, sunlightFraction: 2 / 3, psiRad: Math.PI / 6 },
      budget: { sunlightWh: 1, eclipseWh: 0.5, totalWh: 1.5, averageW: 0.9, peakW: 1, samples: [] },
      solar: { minimumPowerW: 2, cellPowerW: 1, cellCount: 2, rawCellCount: 2 },
      battery: { requiredWh: 2, cycles: 5000, eolCapacityWh: 16, dod: 0.3 },
      suggestions: [
        { productId: 'test-solar', role: 'solar', outcome: 'incomplete', quantity: 2, reason: 'Test only', checks: [], missing: ['installed array wiring'] },
        { productId: 'test-pack', role: 'battery', outcome: 'incomplete', quantity: 1, reason: 'Test only', checks: [], missing: ['pin mapping'] },
        { productId: 'test-board', role: 'conditioning', outcome: 'incomplete', quantity: 1, reason: 'Test only', checks: [], missing: ['pin mapping'] },
      ],
    },
    selections: { solar: 'test-solar', battery: 'test-pack', conditioning: 'test-board', distribution: 'test-board', processor: 'test-board' },
  };
  return { workspace, catalog: { revision: 'synthetic-catalog-1', products } };
}
export const REQUIRED_NODES: NodeId[] = ['mission', 'orbit', 'scenarios', 'budget', 'solar', 'battery', 'topology', 'candidates'];
