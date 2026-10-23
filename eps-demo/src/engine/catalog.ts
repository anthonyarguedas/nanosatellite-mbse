import type { Analysis, Catalog, Check, DesignInputs, Product, Specification, Suggestion } from '../types';
import { activeScenario, numberInRange } from './validation';
import { isLoadConverter, productCoverage } from '../catalog/coverage';

export interface NumericEvidence { value?: number; spec?: Specification; sourceIds: string[]; issue?: string }
const UNITS: Record<string, string> = {
  powerEolW: 'W', powerBolW: 'W', vmpEolV: 'V', impEolA: 'A', energyWh: 'Wh', massKg: 'kg',
  maxInputW: 'W', inputMinV: 'V', inputMaxV: 'V', maxChargeA: 'A', maxDischargeA: 'A', priceUsd: 'USD', cycleLife: 'cycles',
};

/** A number without traceable meaning, units and conditions is not usable evidence. */
export function numericEvidence(product: Product, key: string): NumericEvidence {
  const spec = product.specs[key];
  const missing = (why: string): NumericEvidence => ({ spec, sourceIds: [], issue: `${key}: ${why}` });
  if (!spec || spec.status !== 'available' || spec.value === null) return missing('missing or not applicable');
  if (typeof spec.value !== 'number' || !Number.isFinite(spec.value) || spec.value < 0) return missing('no valid nonnegative scalar');
  if (UNITS[key] && spec.unit !== UNITS[key]) return missing(`expected ${UNITS[key]}, received ${spec.unit || 'no unit'}`);
  const sourceIds = [spec.sourceId, ...spec.additionalSourceIds ?? []];
  if (!spec.sourceId || sourceIds.some(id => !product.sources.some(source => source.id === id && source.url && source.revision))
    || !spec.original.trim() || !spec.conditions.trim() || !spec.location.trim()) {
    return missing('source ID, revision, original value, conditions or document location is missing');
  }
  return { value: spec.value, spec, sourceIds: [...new Set(sourceIds as string[])] };
}

export const lowerBound = (spec?: Specification): boolean => spec?.meaning === 'minimum' || spec?.meaning === 'specified';
export const upperBound = (spec?: Specification): boolean => spec?.meaning === 'maximum' || spec?.meaning === 'specified';

function atLeast(id: string, title: string, evidence: NumericEvidence, required: number | undefined, quantity: number, factor = 1): Check {
  if (required === undefined || evidence.value === undefined) {
    return { id, title, verdict: 'unassessed', detail: required === undefined ? 'Sizing analysis is missing.' : evidence.issue!, sourceIds: evidence.sourceIds };
  }
  const available = evidence.value * quantity * factor;
  if (!Number.isFinite(available)) return { id, title, verdict: 'unassessed', detail: 'Derived available rating exceeds the numerical range.', sourceIds: evidence.sourceIds };
  const verdict = available >= required && lowerBound(evidence.spec) ? 'pass'
    : available < required && upperBound(evidence.spec) ? 'fail' : 'unassessed';
  return {
    id, title, verdict, sourceIds: evidence.sourceIds,
    detail: `${quantity} whole product(s) × ${evidence.value} × illumination ${factor} = ${available.toPrecision(7)}, required ${required.toPrecision(7)}. Meaning: ${evidence.spec!.meaning}. ${verdict === 'unassessed' ? 'The supplied meaning does not establish the required conservative bound.' : 'Applies only at the cited specification conditions.'}`,
    scope: 'Scalar preliminary screen. No complete architecture feasibility or EOL qualification claim.',
  };
}

function solarEvidence(product: Product): NumericEvidence {
  const power = numericEvidence(product, 'powerEolW');
  if (power.value !== undefined) return power;
  const v = numericEvidence(product, 'vmpEolV');
  const a = numericEvidence(product, 'impEolA');
  if (v.value === undefined || a.value === undefined) {
    return { sourceIds: [], issue: 'powerEolW or both vmpEolV and impEolA are missing. BOL power is not an EOL substitute.' };
  }
  // Independent bounds may only be multiplied as bounds at the same declared conditions.
  if (v.spec!.conditions !== a.spec!.conditions) {
    return { sourceIds: [], issue: 'vmpEolV and impEolA have different conditions. No common EOL operating point is established.' };
  }
  if (!Number.isFinite(v.value * a.value)) return { sourceIds: [], issue: 'Derived EOL cell power exceeds the numerical range.' };
  const meaning = lowerBound(v.spec) && lowerBound(a.spec) ? 'minimum'
    : upperBound(v.spec) && upperBound(a.spec) ? 'maximum' : 'estimated';
  return {
    value: v.value * a.value,
    spec: { ...v.spec!, meaning: v.spec!.meaning === 'specified' && a.spec!.meaning === 'specified' ? 'specified' : meaning },
    sourceIds: [...new Set([...v.sourceIds, ...a.sourceIds])],
  };
}

function quantityFor(required: number | undefined, unitValue: number | undefined, factor: number, max: number): number {
  // Explicit finite whole-product search. Never resize a finished panel or pack.
  for (let quantity = 1; quantity <= max; quantity++) {
    if (required === undefined || unitValue === undefined || unitValue * quantity * factor >= required) return quantity;
  }
  return max;
}

function outcome(checks: Check[], structurallyIncomplete = false): Suggestion['outcome'] {
  if (checks.some(check => check.verdict === 'fail')) return 'rejected';
  if (structurallyIncomplete || checks.some(check => check.verdict === 'unassessed')) return 'incomplete';
  return 'preliminary-match';
}

/** One suggestion per product/role. Scope: panels 1..8, bare cells 1..256, finished packs/boards exactly one. */
export function suggestProducts(catalog: Catalog, inputs: DesignInputs, analysis: Analysis, frozenQuantities: Readonly<Record<string, number>> = {}): Suggestion[] {
  if (catalog.products.length > 128) throw new Error('This bounded demo supports at most 128 catalog products. Narrow the catalog explicitly.');
  const suggestions: Suggestion[] = [];
  const scenario = activeScenario(inputs);
  const illumination = scenario ? numberInRange(scenario.illuminationFactor, 'Scenario illumination factor', 0, 1) : 1;
  const requiredSolar = analysis.solar?.minimumPowerW;
  const requiredBattery = analysis.battery?.requiredWh;
  if (requiredSolar !== undefined) numberInRange(requiredSolar, 'Required solar power');
  if (requiredBattery !== undefined) numberInRange(requiredBattery, 'Required battery energy');
  const ids = new Set<string>();
  for (const product of [...catalog.products].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0)) {
    if (ids.has(product.id)) throw new Error(`Catalog contains duplicate product id ${product.id}.`);
    ids.add(product.id);
    if (product.catalogUse === 'reference-only') continue;
    const frozen = frozenQuantities[product.id];
    const maximum = product.level === 'cell' ? 256 : product.level === 'panel' ? 8 : 1;
    if (frozen !== undefined && (!Number.isSafeInteger(frozen) || frozen < 1 || frozen > maximum)) throw new Error(`${product.id}: invalid frozen allocation quantity.`);
    const commonMissing: string[] = [];
    if (!product.supportedConfigurations.length) commonMissing.push('supportedConfigurations');
    if (!product.accountingBoundary.trim()) commonMissing.push('accountingBoundary');
    if (numericEvidence(product, 'priceUsd').value === undefined) commonMissing.push('priceUsd (no cost ranking)');
    if (product.roles.includes('solar')) {
      const evidence = solarEvidence(product);
      const max = product.level === 'cell' ? 256 : 8;
      const quantity = frozen ?? quantityFor(requiredSolar, evidence.value, illumination, max);
      const check = atLeast('CATALOG-SOLAR-POWER', 'Cited EOL solar generation screen', evidence, requiredSolar, quantity, illumination);
      const missing = [...commonMissing, 'installed orientation, temperature/lifetime applicability and interconnection', 'input tracking/open-circuit/current compatibility'];
      if (evidence.issue) missing.push(evidence.issue);
      if (!scenario) missing.push('active scenario illumination');
      if (requiredSolar === undefined) missing.push('analysis.solar.minimumPowerW');
      if (check.verdict === 'unassessed' && evidence.spec) missing.push('guaranteed EOL lower bound under applicable conditions');
      const cell = product.level === 'cell';
      if (cell) missing.push('cell assembly series/parallel arrangement, interconnects, bypass/blocking protection, packaging and installation evidence');
      const incomplete = cell || !scenario || !product.supportedConfigurations.length || !product.accountingBoundary.trim();
      const result = outcome([check], incomplete);
      suggestions.push({
        productId: product.id, role: 'solar', quantity, outcome: result, checks: [check], missing,
        reason: `${result}: finite ${cell ? '1..256 cell' : '1..8 fixed whole-panel'} screen, selected quantity ${quantity}. Individual product ratings, mass and dimensions are unchanged. ${cell ? 'Bare cells require a characterized installed assembly.' : 'A match covers this scalar screen only.'} No cost ranking or global optimum claim.`,
      });
    }
    if (product.roles.includes('battery')) {
      const evidence = numericEvidence(product, 'energyWh');
      const cell = product.level === 'cell';
      const quantity = frozen ?? (cell ? quantityFor(requiredBattery, evidence.value, 1, 256) : 1);
      const check = atLeast('CATALOG-BATTERY-CAPACITY', 'Preliminary BOL energy capacity', evidence, requiredBattery, quantity);
      check.scope = 'BOL energy versus preliminary requirement with M once. This is not a guaranteed EOL capacity or charge/cycle-life pass.';
      const missing = [...commonMissing, 'temperature/lifetime applicability, charger matching, voltage mapping and installed interfaces'];
      for (const key of ['retainedEnergyFraction', 'retainedChargeFraction', 'chargeEfficiency', 'dischargeEfficiency']) {
        if (numericEvidence(product, key).value === undefined) missing.push(key);
      }
      if (evidence.issue) missing.push(evidence.issue);
      if (requiredBattery === undefined) missing.push('analysis.battery.requiredWh');
      if (check.verdict === 'unassessed' && evidence.spec) missing.push('conservative sourced BOL energy rating');
      for (const key of ['maxChargeA', 'maxDischargeA', 'cycleLife']) {
        if (numericEvidence(product, key).value === undefined) missing.push(key);
      }
      if (cell) missing.push('cell assembly series/parallel, balancing, protection, packaging and installation evidence');
      const result = outcome([check], cell || !product.supportedConfigurations.length || !product.accountingBoundary.trim());
      suggestions.push({
        productId: product.id, role: 'battery', quantity, outcome: result, checks: [check], missing,
        reason: `${result}: ${cell ? 'finite 1..256 bare-cell preliminary energy count' : 'one fixed finished pack/board with unchanged internal arrangement'}. BOL energy never establishes guaranteed EOL performance. Cycle life and charge state remain unassessed. No cost ranking.`,
      });
    }
    if (product.roles.includes('conditioning') && isLoadConverter(product)) {
      const coverage = productCoverage(product, 'conditioning');
      suggestions.push({ productId: product.id, role: 'conditioning', quantity: 1, outcome: 'incomplete',
        checks: [{ id: 'CATALOG-LOAD-CONVERTER-INTERFACES', title: 'Assigned load-converter path', verdict: 'unassessed',
          detail: 'This product regulates a DC load rail. It is not a PV receiver or charger. Assigned rail input/output, load current and installed connections are not evaluated. Array source power is not its input demand.' }],
        missing: [...coverage.core.filter(item => !item.covered).flatMap(item => item.issues), 'installed DC rail assignment, voltage/current and interface applicability'],
        reason: 'One fixed purchased load converter. Sourced comparison coverage does not establish a solar MPPT/DET or charger implementation.' });
    }
    if (product.roles.includes('conditioning') && !isLoadConverter(product)) {
      const evidence = numericEvidence(product, 'maxInputW');
      const source = inputs.solar.installedPowerW;
      if (source !== null) numberInRange(source, 'Installed available EOL source power');
      const inputW = source === null || !scenario ? undefined : source * illumination;
      const verdict = evidence.value === undefined || inputW === undefined || !upperBound(evidence.spec) ? 'unassessed'
        : inputW > evidence.value ? 'fail' : 'pass';
      const checks: Check[] = [{
        id: 'CATALOG-INPUT-POWER', title: 'Conditioning input power limit', verdict, sourceIds: evidence.sourceIds,
        detail: evidence.value === undefined ? evidence.issue! : inputW === undefined ? 'Source power or active illumination is missing.'
          : `${inputW.toPrecision(7)} W source input versus ${evidence.value} W (${evidence.spec!.meaning}). Typical or nominal values are not guaranteed limits.`,
        scope: 'Source boundary, before conditioning efficiency. Does not verify converter capability.',
      }, {
        id: 'CATALOG-CONDITIONING-INTERFACES', title: 'Installed input and conversion envelope', verdict: 'unassessed',
        detail: 'The demo has no installed series/parallel voltage interval, tracking/open-circuit/current envelope, rail assignments or complete charger interface.',
      }];
      const missing = [...commonMissing, 'installed array voltage/current extrema and channel allocation', 'conversion/startup envelope and charger compatibility'];
      for (const key of ['inputMinV', 'inputMaxV', 'maxInputW']) {
        const value = numericEvidence(product, key);
        if (value.issue) missing.push(value.issue);
      }
      if (verdict === 'unassessed' && evidence.spec) missing.push('guaranteed maxInputW limit or source input');
      const result = outcome(checks);
      suggestions.push({ productId: product.id, role: 'conditioning', quantity: 1, outcome: result, checks, missing,
        reason: `${result}: one fixed board. Any scalar power check leaves voltage, topology, current, protection and charger compatibility unresolved. No cost ranking.` });
    }
    for (const role of ['distribution', 'processor', 'software'] as const) {
      if (!product.roles.includes(role)) continue;
      const coverage = productCoverage(product, role);
      const missing = [...coverage.identityIssues, ...coverage.core.filter(item => !item.covered).flatMap(item => item.issues),
        ...coverage.richer.filter(item => !item.covered).map(item => `${item.label}: richer characterization missing`)];
      suggestions.push({ productId: product.id, role, quantity: frozen ?? 1, outcome: 'incomplete', missing,
        checks: [{ id: `CATALOG-${role.toUpperCase()}-SCOPE`, title: `${role} architecture assessment`, verdict: 'unassessed',
          detail: 'Documented role allocation only. Installed interfaces, resources, service behavior and compatibility are not evaluated by this demo.', sourceIds: product.sources.map(source => source.id) }],
        reason: 'One fixed product, exact documented role. Comparison coverage is separate from architecture feasibility. No synthetic compatibility or resource pass.' });
    }
  }
  return suggestions;
}
