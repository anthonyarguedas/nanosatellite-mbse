import type { BudgetResult, OrbitResult, Scenario } from '../types';

export function numberInRange(
  value: number | null | undefined,
  name: string,
  min = 0,
  max = Infinity,
  exclusiveMin = false,
): number {
  if (typeof value !== 'number' || !Number.isFinite(value)
    || (exclusiveMin ? value <= min : value < min) || value > max) {
    throw new Error(`${name} must be a finite number ${exclusiveMin ? '>' : '>='} ${min}${max < Infinity ? ` and <= ${max}` : ''}.`);
  }
  return value;
}

export const efficiency = (value: number | null, name: string): number =>
  numberInRange(value, name, 0, 1, true);

export function finiteResult(value: number, name: string): number {
  if (!Number.isFinite(value)) throw new Error(`${name} exceeds the numerical range of this model.`);
  return value;
}

export function validateOrbit(orbit: OrbitResult): void {
  const period = numberInRange(orbit.periodS, 'Orbit period', 0, Infinity, true);
  const sun = numberInRange(orbit.sunlightS, 'Sunlight duration', 0, period, true);
  const eclipse = numberInRange(orbit.eclipseS, 'Eclipse duration', 0, period);
  numberInRange(orbit.sunlightFraction, 'Sunlight fraction', 0, 1, true);
  numberInRange(orbit.orbitsPerDay, 'Orbits per day', 0, Infinity, true);
  numberInRange(orbit.psiRad, 'Eclipse geometry angle', 0, Math.PI / 2);
  if (Math.abs(sun + eclipse - period) > 1e-9 * period
    || Math.abs(orbit.sunlightFraction - sun / period) > 1e-10) {
    throw new Error('Orbit sunlight, eclipse and fraction must close to one period.');
  }
  if (Math.abs(orbit.orbitsPerDay - 86400 / period) > 1e-9 * orbit.orbitsPerDay) {
    throw new Error('Orbit count per day must agree with the period in seconds.');
  }
}

export function validateScenario(scenario: Scenario): void {
  numberInRange(scenario.illuminationFactor, 'Scenario illumination factor', 0, 1);
  numberInRange(scenario.initialEnergyFraction, 'Initial energy fraction', 0, 1);
  numberInRange(scenario.minimumEnergyFraction, 'Minimum energy fraction', 0, 1);
  numberInRange(scenario.durationOrbits, 'Scenario duration in orbits', 0, Infinity, true);
  if (scenario.kind !== 'nominal' && scenario.kind !== 'survival') {
    throw new Error('Scenario kind must be nominal or survival.');
  }
  const ids = new Set<string>();
  for (const load of scenario.loads) {
    if (ids.has(load.id)) throw new Error(`Duplicate load id: ${load.id}.`);
    ids.add(load.id);
    numberInRange(load.activePowerW, `${load.name} active power`);
    numberInRange(load.idlePowerW, `${load.name} idle power`);
    numberInRange(load.railV, `${load.name} nominal rail voltage`, 0, Infinity, true);
    for (const window of load.windows) {
      numberInRange(window.start, `${load.name} window start`, 0, 1);
      numberInRange(window.end, `${load.name} window end`, 0, 1);
      if (window.end < window.start) {
        throw new Error(`${load.name} window end precedes its start. Split a wrapping window at phase 0/1.`);
      }
    }
  }
}

export function validateBudget(budget: BudgetResult): void {
  for (const key of ['sunlightWh', 'eclipseWh', 'totalWh', 'averageW', 'peakW'] as const) {
    numberInRange(budget[key], `Budget ${key}`);
  }
  if (Math.abs(budget.sunlightWh + budget.eclipseWh - budget.totalWh)
    > 1e-9 * Math.max(1, budget.totalWh)) {
    throw new Error('Budget sunlight and eclipse energies must sum to total energy.');
  }
}

export function activeScenario(inputs: { scenarios: Scenario[]; activeScenarioId: string }): Scenario | undefined {
  return inputs.scenarios.find(scenario => scenario.id === inputs.activeScenarioId);
}
