import type { AllocationReceipt, Analysis, Catalog, Check, DesignInputs, Product, Role } from '../types';
import { allocationIssues, EPS_ROLES, getAllocationQuantity } from './allocations';
import { lowerBound, numericEvidence, suggestProducts, upperBound } from './catalog';
import { activeScenario, finiteResult, numberInRange } from './validation';

const REQUIREMENTS: [string, string, string][] = [
  ['EPS-01', 'Supported configurations', 'Installed usages, supported settings, external circuitry and adapters are not fully declared. Finished products remain fixed.'],
  ['EPS-02', 'Preliminary array generation', 'Attainable DET/MPPT operating points, installed illumination geometry and conservative EOL bounds are not characterized.'],
  ['EPS-03', 'Solar input compatibility', 'Installed series/parallel counts, temperature extrema, tracking/startup, open-circuit voltage and permissible source-current bounds are missing.'],
  ['EPS-04', 'Converter envelopes', 'Rail assignments, converter conversion envelopes, startup and dropout bounds are missing.'],
  ['EPS-05', 'Charger and battery compatibility', 'Chemistry, series count, charger policy, termination and temperature rules are not matched.'],
  ['EPS-06', 'Load voltage and startup service', 'Load voltage tolerances, actual battery/rail voltages, returns, harness drops and startup timing are missing.'],
  ['EPS-07', 'Simultaneous path ratings', 'Battery, rail, switch and connection current/temperature/pulse ratings and path allocations are missing.'],
  ['EPS-08', 'Preliminary battery capacity', 'A scalar BOL screen is available separately. Sourced lifetime energy/charge applicability and installed pack evidence are incomplete.'],
  ['EPS-09', 'Nominal cycle life', 'No applicable sourced cycle-life versus DoD/temperature model is established. No coefficients or fit are invented.'],
  ['EPS-10', 'Nominal service and reserve', 'No complete nominal energy and charge assessment. Charge-based SoC and a characterized Q/v mapping are unsupported.'],
  ['EPS-11', 'Nominal replenishment', 'Energy closure alone cannot establish charge closure. Charge-based state and a characterized Q/v mapping are unsupported.'],
  ['EPS-12', 'Survival and recovery', 'Survival charge/reserve limits, essential-service interfaces and authorized recovery transitions are incomplete.'],
  ['EPS-13', 'Operating temperatures', 'Component temperature histories, charging/discharging limits and heater requirements are missing.'],
  ['EPS-14', 'Supported surplus disposal', 'Numerical surplus is not verification of curtailment/shunt voltage, current, termination or thermal capability.'],
  ['EPS-15', 'Protection and no-trip behavior', 'Fault envelopes, threshold tolerances, trip curves, safe operating area and legitimate-pulse no-trip evidence are missing.'],
  ['EPS-16', 'Battery cutoff and recovery', 'Battery voltage model, cutoff/hysteresis thresholds, trip/reset timing and safe-state service policy are missing.'],
  ['EPS-17', 'Power-on and inhibited states', 'IF-C truth tables, source/startup conditions, default states and processor-independent inhibit/protection evidence are missing.'],
  ['EPS-18', 'Service and control interfaces', 'Endpoint/pin mappings, directed service semantics, signal levels, protocol versions, addresses and timing bounds are missing.'],
  ['EPS-19', 'Physical resource allocations', 'A known mass subtotal is separate. Harnesses, adapters, packaging/protection, complete installed quantities and volume allocations are not fully declared.'],
  ['EPS-20', 'Installation and array geometry', 'Installed frames, envelopes, packing, keep-outs, mounting, connector access and deployment states are missing.'],
];

/** Always returns EPS-01..20 plus explicitly scoped subchecks. No complete-feasibility assertion. */
export function assessDesign(
  inputs: DesignInputs, analysis: Analysis, catalog: Catalog, selections: Partial<Record<Role, string>>, allocations?: AllocationReceipt[],
): Check[] {
  const checks = REQUIREMENTS.map(([id, title, detail]): Check => ({
    id, title, verdict: 'unassessed', detail,
    scope: 'Active-scenario concept assessment. No completed flight verification or whole-EPS feasibility claim.',
  }));
  const byId = new Map(checks.map(check => [check.id, check]));
  const set = (id: string, update: Partial<Check>): void => { Object.assign(byId.get(id)!, update); };
  const scenario = activeScenario(inputs);
  if (scenario) numberInRange(scenario.illuminationFactor, 'Scenario illumination factor', 0, 1);
  if (inputs.solar.installedPowerW !== null) numberInRange(inputs.solar.installedPowerW, 'Installed available EOL source power');
  if (inputs.battery.capacityWh !== null) numberInRange(inputs.battery.capacityWh, 'Battery BOL capacity', 0, Infinity, true);
  if (inputs.topology.massAllocationKg !== null) numberInRange(inputs.topology.massAllocationKg, 'Mass allocation');
  if (analysis.solar) numberInRange(analysis.solar.minimumPowerW, 'Required solar power');
  if (analysis.battery) {
    numberInRange(analysis.battery.requiredWh, 'Required battery energy');
    numberInRange(analysis.battery.cycles, 'Required mission cycles');
  }
  const sim = analysis.simulation?.scenarioId === scenario?.id
    && (analysis.simulation?.scenarioRevision === undefined || analysis.simulation.scenarioRevision === scenario?.revision) ? analysis.simulation : undefined;
  const extras: Check[] = [];
  if (sim) {
    for (const check of sim.checks) {
      if (byId.has(check.id)) set(check.id, {
        ...check,
        verdict: check.verdict === 'fail' ? 'fail' : 'unassessed',
        detail: check.verdict === 'pass' ? `${check.detail} The full requirement remains unassessed in this energy-only demo.` : check.detail,
      });
      else extras.push(check);
    }
    if (sim.checks.some(check => check.id === 'BATTERY-DISCHARGE' && check.verdict === 'fail')) {
      set('EPS-07', { verdict: 'fail', detail: 'Known violation of the engineer-declared battery discharge power bound. Current/voltage and other path ratings remain unassessed.' });
    }
  }
  for (const id of ['ENERGY-RESERVE', 'ENERGY-CLOSURE']) {
    if (!extras.some(check => check.id === id)) extras.push({
      id, title: id === 'ENERGY-RESERVE' ? 'Stored energy reserve' : 'Nominal repeating energy closure',
      verdict: 'unassessed', detail: 'A simulation of the active scenario is missing. Saved results for a different scenario are not used.',
    });
  }

  const solarRequired = analysis.solar?.minimumPowerW;
  const source = inputs.solar.installedPowerW;
  const solarAvailable = source !== null && scenario ? source * scenario.illuminationFactor : undefined;
  const solarVerdict = solarRequired === undefined || solarAvailable === undefined ? 'unassessed'
    : solarAvailable < solarRequired ? 'fail' : 'pass';
  extras.push({
    id: 'SOLAR-POWER', title: 'Assumed source-boundary generation screen', verdict: solarVerdict,
    detail: solarRequired === undefined || solarAvailable === undefined ? 'Preliminary solar sizing, installed power or active illumination is missing.'
      : `${solarAvailable.toPrecision(8)} W assumed available EOL source power versus ${solarRequired.toPrecision(8)} W required.`,
    scope: 'Engineer-input scalar screen only. Attainable operating point, geometry and sourced EOL guarantee are unassessed.',
  });
  if (solarVerdict === 'fail') set('EPS-02', { verdict: 'fail', detail: 'Installed source-boundary power under the active illumination is below the preliminary generation bound.' });

  const requiredWh = analysis.battery?.requiredWh;
  const bol = inputs.battery.capacityWh;
  const batteryVerdict = requiredWh === undefined || bol === null ? 'unassessed' : bol < requiredWh ? 'fail' : 'pass';
  extras.push({
    id: 'BATTERY-CAPACITY', title: 'Assumed preliminary BOL energy capacity', verdict: batteryVerdict,
    detail: requiredWh === undefined || bol === null ? 'Preliminary sizing or BOL energy capacity is missing.'
      : `${bol.toPrecision(8)} Wh BOL versus ${requiredWh.toPrecision(8)} Wh required. Margin M appears once in requiredWh. EOL capacity uses retainedEnergy once, without M.`,
    scope: 'Engineer-input preliminary energy screen only. No charge, lifetime or cycle-life guarantee.',
  });
  if (batteryVerdict === 'fail') set('EPS-08', { verdict: 'fail', detail: 'Installed BOL battery energy is below the preliminary capacity requirement.' });

  const allocationSubject = { selections, allocations };
  const receiptIssues = allocationIssues(allocationSubject, catalog);
  const selectedProducts = new Map<string, Product>();
  const missingProducts: string[] = [];
  const roleViolations: string[] = [];
  for (const role of EPS_ROLES) {
    const id = selections[role];
    if (!id) continue;
    const product = catalog.products.find(candidate => candidate.id === id);
    if (!product) { missingProducts.push(id); continue; }
    selectedProducts.set(id, product);
    if (!product.roles.includes(role)) roleViolations.push(`${id} does not declare role ${role}`);
    const quantity = getAllocationQuantity(allocationSubject, id);
    const allocatedScreens = quantity === null ? [] : suggestProducts({ revision: catalog.revision, products: [product] }, inputs, analysis, { [id]: quantity });
    for (const suggestion of allocatedScreens) {
      if (suggestion.productId !== id || suggestion.role !== role) continue;
      const failure = suggestion.checks.find(check => check.verdict === 'fail');
      if (failure && role === 'solar') set('EPS-02', { verdict: 'fail', detail: failure.detail, sourceIds: failure.sourceIds });
      if (failure && role === 'battery') set('EPS-08', { verdict: 'fail', detail: failure.detail, sourceIds: failure.sourceIds });
      if (failure && role === 'conditioning') set('EPS-03', { verdict: 'fail', detail: failure.detail, sourceIds: failure.sourceIds });
    }
  }
  if (roleViolations.length || receiptIssues.length) set('EPS-01', { verdict: 'fail', detail: [...roleViolations, ...receiptIssues].join('. ') });
  else if (missingProducts.length) set('EPS-01', { detail: `Catalog entries missing: ${missingProducts.join(', ')}. Installed usages and external circuitry remain unassessed.` });

  const battery = selections.battery ? selectedProducts.get(selections.battery) : undefined;
  const cycle = battery ? numericEvidence(battery, 'cycleLife') : undefined;
  set('EPS-09', {
    detail: `${analysis.battery ? `${analysis.battery.cycles.toPrecision(8)} nominal cycles required (365.25 days/year, one cycle/orbit). ` : 'Mission cycle count missing. '}${cycle?.value !== undefined ? `Cited cycleLife is ${cycle.value} cycles (${cycle.spec!.meaning}). Its DoD/temperature/lifetime applicability cannot be resolved from the demo inputs. ` : 'Applicable sourced cycle-life data is missing. '}No fit or DoD-to-life extrapolation is invented.`,
    sourceIds: cycle?.sourceIds,
  });

  let subtotal = 0;
  let knownLowerSubtotal = 0;
  let allMassBounds = [...selectedProducts.values()].some(product => product.level !== 'software') && missingProducts.length === 0;
  const massMissing = [...missingProducts.map(id => `${id}: catalog entry missing`)];
  const massSources = new Set<string>();
  const accounted: string[] = [];
  for (const product of selectedProducts.values()) {
    if (product.level === 'software') {
      accounted.push(`${product.id}: logical software, physical resources belong to its host (host allocation/resources unassessed)`);
      continue;
    }
    const quantity = getAllocationQuantity(allocationSubject, product.id);
    if (quantity === null) {
      allMassBounds = false;
      accounted.push(`unknown quantity × ${product.id}`);
      massMissing.push(`${product.id}: frozen allocation quantity missing (legacy selections are not resized from suggestions)`);
      continue;
    }
    const mass = numericEvidence(product, 'massKg');
    accounted.push(`${quantity} × ${product.id}`);
    if (mass.value === undefined) {
      allMassBounds = false;
      massMissing.push(`${product.id}: ${mass.issue}`);
      continue;
    }
    subtotal = finiteResult(subtotal + quantity * mass.value, 'Known mass subtotal');
    if (lowerBound(mass.spec)) knownLowerSubtotal += quantity * mass.value;
    if (!upperBound(mass.spec)) allMassBounds = false;
    mass.sourceIds.forEach(id => massSources.add(id));
  }
  const allocation = inputs.topology.massAllocationKg;
  const massFail = allocation !== null && knownLowerSubtotal > allocation;
  const massVerdict = massFail ? 'fail'
    : allocation !== null && allMassBounds && subtotal <= allocation ? 'pass' : 'unassessed';
  const massDetail = `Known selected-product mass subtotal ${subtotal.toPrecision(8)} kg${allocation !== null ? ` versus ${allocation} kg allocation` : ', allocation missing'}. Each product ID is physical once across logical roles: ${accounted.join(', ') || 'none selected'}. Quantities come only from frozen allocation receipts; current suggestions never resize allocated hardware. ${massMissing.length ? `Missing: ${massMissing.join('; ')}. ` : ''}Auxiliaries, explicit installed usages, full volume and geometry remain unknown.`;
  extras.push({
    id: 'KNOWN-MASS', title: 'Deduplicated known product mass subtotal', verdict: massVerdict, detail: massDetail,
    sourceIds: [...massSources], scope: 'Selected candidate subtotal only. No full EPS-19 pass. Typical mass is indicative and cannot establish a guaranteed limit.',
  });
  set('EPS-19', { verdict: massFail ? 'fail' : 'unassessed', detail: massDetail, sourceIds: [...massSources] });
  return [...checks, ...extras];
}
