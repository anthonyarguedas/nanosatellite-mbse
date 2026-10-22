import type { BatteryResult, BudgetResult, DesignInputs, OrbitResult, Scenario, SolarResult } from '../types';
import { demandAtPhase, phaseEvents } from './profiles';
import { efficiency, finiteResult, numberInRange, validateBudget, validateOrbit, validateScenario } from './validation';

export { suggestProducts } from './catalog';
export { simulateOrbit } from './simulation';
export { assessDesign } from './assessment';

/** El Hachimi model in design-proposal.tex. Circular orbit, fixed maximum eclipse geometry. */
export function calculateOrbit(altitudeKm: number): OrbitResult {
  numberInRange(altitudeKm, 'Altitude (km)');
  const radiusKm = 6378 + altitudeKm;
  const periodS = finiteResult(2 * Math.PI * Math.sqrt(radiusKm ** 3 / 398601), 'Orbit period');
  const psiRad = Math.acos(6378 / radiusKm);
  const sunlightFraction = 0.5 + psiRad / Math.PI;
  const sunlightS = sunlightFraction * periodS;
  // Subtraction makes the partition close at machine precision.
  const eclipseS = periodS - sunlightS;
  return { periodS, sunlightS, eclipseS, orbitsPerDay: 86400 / periodS, sunlightFraction, psiRad };
}

export function calculateBudget(scenario: Scenario, orbit: OrbitResult): BudgetResult {
  validateOrbit(orbit);
  validateScenario(scenario);
  const events = phaseEvents(scenario, orbit);
  let sunlightWh = 0;
  let eclipseWh = 0;
  let peakW = 0;
  const samples: BudgetResult['samples'] = [];
  for (let i = 0; i + 1 < events.length; i++) {
    const start = events[i];
    const end = events[i + 1];
    const phase = start + (end - start) / 2;
    const powerW = finiteResult(demandAtPhase(scenario, phase), 'Aggregate load power');
    const wh = powerW * (end - start) * orbit.periodS / 3600;
    if (phase < orbit.sunlightFraction) sunlightWh += wh;
    else eclipseWh += wh;
    peakW = Math.max(peakW, powerW);
    // Duplicate event phases represent the two sides of an instantaneous mode change.
    samples.push({ phase: start, powerW }, { phase: end, powerW });
  }
  const totalWh = finiteResult(sunlightWh + eclipseWh, 'Load energy');
  return { sunlightWh, eclipseWh, totalWh, averageW: finiteResult(totalWh / (orbit.periodS / 3600), 'Average load power'), peakW, samples,
    orbitPeriodS: orbit.periodS, sunlightFraction: orbit.sunlightFraction, scenarioId: scenario.id, scenarioRevision: scenario.revision };
}

export function sizeSolar(inputs: DesignInputs, budget: BudgetResult, orbit: OrbitResult): SolarResult {
  validateOrbit(orbit);
  validateBudget(budget);
  const xs = efficiency(inputs.solar.sunlightEfficiency, 'Sunlight path efficiency Xs');
  const xe = efficiency(inputs.solar.eclipseEfficiency, 'Eclipse path efficiency Xe');
  const v = numberInRange(inputs.solar.cellEolV, 'Cell EOL maximum power voltage', 0, Infinity, true);
  const a = numberInRange(inputs.solar.cellEolA, 'Cell EOL maximum power current', 0, Infinity, true);
  const minimumPowerW = finiteResult((budget.sunlightWh / xs + budget.eclipseWh / xe)
    / (orbit.sunlightS / 3600), 'Preliminary solar power');
  const cellPowerW = finiteResult(v * a, 'Cell EOL power');
  const rawCellCount = finiteResult(minimumPowerW / cellPowerW, 'Preliminary cell count');
  const cellCount = Math.ceil(rawCellCount);
  if (!Number.isSafeInteger(cellCount)) throw new Error('Solar cell count exceeds the supported integer range.');
  return { minimumPowerW, cellPowerW, cellCount, rawCellCount };
}

export function sizeBattery(inputs: DesignInputs, budget: BudgetResult, orbit: OrbitResult): BatteryResult {
  validateOrbit(orbit);
  validateBudget(budget);
  const dod = efficiency(inputs.battery.dod, 'Preliminary charge DoD assumption');
  const margin = numberInRange(inputs.battery.margin, 'Preliminary battery margin M');
  const capacity = numberInRange(inputs.battery.capacityWh, 'Battery BOL capacity (Wh)', 0, Infinity, true);
  const retained = efficiency(inputs.battery.retainedEnergy, 'Retained energy factor fE');
  const lifetime = numberInRange(inputs.mission.lifetimeYears, 'Mission lifetime (years)', 0, Infinity, true);
  return {
    requiredWh: finiteResult(budget.eclipseWh / dod * (1 + margin), 'Preliminary battery energy'),
    cycles: finiteResult(lifetime * 365.25 * orbit.orbitsPerDay, 'Mission cycle count'),
    eolCapacityWh: finiteResult(capacity * retained, 'Battery EOL capacity'),
    dod,
  };
}
