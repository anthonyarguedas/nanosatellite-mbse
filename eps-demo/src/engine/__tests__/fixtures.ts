import type { DesignInputs, Load, OrbitResult, Product, Scenario, Specification } from '../../types';

export const orbit: OrbitResult = {
  periodS: 100, sunlightS: 60, eclipseS: 40, sunlightFraction: 0.6, orbitsPerDay: 864, psiRad: Math.PI * 0.1,
};

export function load(overrides: Partial<Load> = {}): Load {
  return { id: 'load', name: 'Demo load', subsystem: 'payload', color: '#abcdef', activePowerW: 4, idlePowerW: 1,
    railV: 5, essential: true, windows: [{ id: 'all', start: 0, end: 1 }], ...overrides };
}

export function scenario(overrides: Partial<Scenario> = {}): Scenario {
  return { id: 'nominal', name: 'Test nominal', description: 'Synthetic unit test', kind: 'nominal', revision: 1,
    illuminationFactor: 1, initialEnergyFraction: 0.5, minimumEnergyFraction: 0.1, durationOrbits: 1,
    loads: [load()], provenance: 'Unit test assumptions', ...overrides };
}

export function inputs(s = scenario()): DesignInputs {
  return {
    mission: { name: 'Test', altitudeKm: 500, lifetimeYears: 2 }, scenarios: [s], activeScenarioId: s.id,
    solar: { sunlightEfficiency: 0.8, eclipseEfficiency: 0.6, cellEolV: 2, cellEolA: 0.5, installedPowerW: 10 },
    battery: { dod: 0.25, margin: 0.2, capacityWh: 100, retainedEnergy: 0.8,
      chargeEfficiency: 0.9, dischargeEfficiency: 0.8, maxChargeW: 100, maxDischargeW: 100 },
    topology: { conditioning: 'MPPT', distribution: 'centralized', bus: 'regulated', efficiency: 0.8, idlePowerW: 0, massAllocationKg: 1 },
  };
}

export function spec(value: number | null, unit: string, meaning: Specification['meaning'] = 'specified'): Specification {
  return { value, unit, meaning, status: value === null ? 'missing' : 'available', original: `${value} ${unit}`,
    conditions: 'Sourced test rating at 20 C, declared configuration and lifetime', sourceId: value === null ? null : 'source', location: 'Table 1' };
}

export function product(overrides: Partial<Product> = {}): Product {
  return {
    id: 'panel', revision: '1', name: 'Fixed test panel', manufacturer: 'Test', partNumber: 'TEST', level: 'panel', roles: ['solar'],
    description: 'Synthetic product fixture, no real product claim',
    specs: { powerEolW: spec(5, 'W'), massKg: spec(0.2, 'kg'), widthM: spec(0.1, 'm'), heightM: spec(0.2, 'm') },
    sources: [{ id: 'source', title: 'Test evidence', url: 'https://example.org/test', revision: '1', location: 'Table 1', retrievedAt: '2025-01-01' }],
    supportedConfigurations: ['Fixed whole product'], accountingBoundary: 'Complete physical item, excludes harness', caveats: [], ...overrides,
  };
}
