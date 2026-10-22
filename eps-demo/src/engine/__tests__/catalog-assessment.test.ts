import { describe, expect, it } from 'vitest';
import type { Analysis, Catalog, Check } from '../../types';
import { assessDesign, calculateBudget, simulateOrbit, sizeBattery, sizeSolar, suggestProducts } from '../index';
import { inputs, orbit, product, scenario, spec } from './fixtures';

const catalog = (...products: Catalog['products']): Catalog => ({ revision: 'test', products });
const check = (checks: Check[], id: string) => checks.find(item => item.id === id)!;
function sizedAnalysis(): Analysis {
  const i = inputs();
  const budget = calculateBudget(i.scenarios[0], orbit);
  return { orbit, budget, solar: sizeSolar(i, budget, orbit), battery: sizeBattery(i, budget, orbit) };
}

describe('finite catalog evaluation', () => {
  it('selects whole fixed panels without mutating or resizing their physical properties', () => {
    const p = product();
    const before = JSON.stringify(p);
    const results = suggestProducts(catalog(p), inputs(), sizedAnalysis());
    expect(results).toHaveLength(1);
    expect(results[0].quantity).toBe(2);
    expect(results[0].outcome).toBe('preliminary-match');
    expect(results[0].checks[0].verdict).toBe('pass');
    expect(p.specs.massKg.value).toBe(0.2);
    expect(p.specs.widthM.value).toBe(0.1);
    expect(p.specs.powerEolW.value).toBe(5);
    expect(JSON.stringify(p)).toBe(before);
  });
  it('is deterministic and independent of catalog order and missing prices', () => {
    const a = product({ id: 'a' });
    const b = product({ id: 'b', specs: { ...a.specs, priceUsd: spec(1000, 'USD') } });
    const c = catalog(a, b);
    expect(suggestProducts(c, inputs(), sizedAnalysis())).toEqual(suggestProducts(catalog(b, a), inputs(), sizedAnalysis()));
    expect(suggestProducts(c, inputs(), sizedAnalysis()).map(item => item.productId)).toEqual(['a', 'b']);
    expect(suggestProducts(c, inputs(), sizedAnalysis())[0].missing.join(' ')).toMatch(/priceUsd/);
    expect(suggestProducts(c, inputs(), sizedAnalysis())[0].reason).toMatch(/No cost ranking/);
  });
  it('keeps BOL-only solar data unknown instead of inventing EOL power', () => {
    const p = product({ specs: { powerBolW: spec(100, 'W'), powerEolW: spec(null, 'W') } });
    const result = suggestProducts(catalog(p), inputs(), sizedAnalysis())[0];
    expect(result.outcome).toBe('incomplete');
    expect(result.checks[0].verdict).toBe('unassessed');
    expect(result.missing.join(' ')).toMatch(/BOL power is not an EOL substitute/);
  });
  it.each(['typical', 'nominal', 'estimated'] as const)('does not turn %s EOL power into a guaranteed pass or failure', meaning => {
    for (const watts of [0.01, 100]) {
      const result = suggestProducts(catalog(product({ specs: { powerEolW: spec(watts, 'W', meaning) } })), inputs(), sizedAnalysis())[0];
      expect(result.outcome).toBe('incomplete');
      expect(result.checks[0].verdict).toBe('unassessed');
    }
  });
  it('rejects a known power shortfall at the finite panel bound', () => {
    const result = suggestProducts(catalog(product({ specs: { powerEolW: spec(0.1, 'W') } })), inputs(), sizedAnalysis())[0];
    expect(result.quantity).toBe(8);
    expect(result.outcome).toBe('rejected');
    expect(result.checks[0].verdict).toBe('fail');
  });
  it('uses EOL MPP voltage/current only with matching source conditions', () => {
    const p = product({ specs: { vmpEolV: spec(4, 'V'), impEolA: spec(0.5, 'A') } });
    expect(suggestProducts(catalog(p), inputs(), sizedAnalysis())[0].outcome).toBe('preliminary-match');
    p.specs.impEolA.conditions = 'A different temperature';
    expect(suggestProducts(catalog(p), inputs(), sizedAnalysis())[0].outcome).toBe('incomplete');
  });
  it('keeps bare solar and battery cell arrays incomplete despite scalar capacity', () => {
    const p = product({ level: 'cell', roles: ['solar', 'battery'], specs: { powerEolW: spec(1, 'W'), energyWh: spec(1, 'Wh') } });
    const results = suggestProducts(catalog(p), inputs(), sizedAnalysis());
    expect(results).toHaveLength(2);
    for (const result of results) {
      expect(result.outcome).toBe('incomplete');
      expect(Number.isInteger(result.quantity)).toBe(true);
      expect(result.quantity).toBeLessThanOrEqual(256);
      expect(result.missing.join(' ')).toMatch(/protection/);
      expect(result.missing.join(' ')).toMatch(/installation/);
    }
  });
  it('does not scale an inadequate finished battery pack or invent EOL capacity', () => {
    const p = product({ id: 'pack', level: 'pack', roles: ['battery'], specs: { energyWh: spec(0.01, 'Wh') } });
    const result = suggestProducts(catalog(p), inputs(), sizedAnalysis())[0];
    expect(result.quantity).toBe(1);
    expect(result.outcome).toBe('rejected');
    expect(result.reason).toMatch(/BOL energy never establishes guaranteed EOL/);
  });
  it('accepts only a scoped BOL battery match and leaves cycle-life data explicit', () => {
    const p = product({ id: 'pack', level: 'pack', roles: ['battery'], specs: { energyWh: spec(100, 'Wh') } });
    const result = suggestProducts(catalog(p), inputs(), sizedAnalysis())[0];
    expect(result.outcome).toBe('preliminary-match');
    expect(result.checks.every(item => item.id !== 'EPS-09' && item.id !== 'EPS-10')).toBe(true);
    expect(result.missing).toContain('cycleLife');
    expect(result.checks[0].scope).toMatch(/not a guaranteed EOL/);
  });
  it('keeps unknown converter ratings separate from known input-power failures', () => {
    const missing = product({ id: 'missing', level: 'board', roles: ['conditioning'], specs: { maxInputW: spec(null, 'W') } });
    const weak = product({ id: 'weak', level: 'board', roles: ['conditioning'], specs: { maxInputW: spec(5, 'W') } });
    const adequate = product({ id: 'adequate', level: 'board', roles: ['conditioning'], specs: { maxInputW: spec(10, 'W') } });
    const results = suggestProducts(catalog(missing, weak, adequate), inputs(), sizedAnalysis());
    expect(results.find(item => item.productId === 'missing')?.outcome).toBe('incomplete');
    expect(results.find(item => item.productId === 'weak')?.outcome).toBe('rejected');
    expect(results.find(item => item.productId === 'adequate')?.outcome).toBe('incomplete');
    expect(results.find(item => item.productId === 'adequate')?.checks[0].verdict).toBe('pass');
  });
  it('does not use a typical converter rating as a maximum or reapply conditioning efficiency upstream', () => {
    const p = product({ level: 'board', roles: ['conditioning'], specs: { maxInputW: spec(9, 'W', 'typical') } });
    const i = inputs();
    i.topology.efficiency = 0.1;
    const result = suggestProducts(catalog(p), i, sizedAnalysis())[0];
    expect(result.checks[0].verdict).toBe('unassessed');
    p.specs.maxInputW.meaning = 'maximum';
    expect(suggestProducts(catalog(p), i, sizedAnalysis())[0].outcome).toBe('rejected');
  });
  it('exposes absent, invalid-unit, unsourced and missing-condition fields', () => {
    for (const invalid of [
      { ...spec(100, 'mW') }, { ...spec(100, 'W'), sourceId: 'unknown' },
      { ...spec(100, 'W'), conditions: '' }, { ...spec(NaN, 'W') },
    ]) {
      const result = suggestProducts(catalog(product({ specs: { powerEolW: invalid } })), inputs(), sizedAnalysis())[0];
      expect(result.outcome).toBe('incomplete');
      expect(result.checks[0].verdict).toBe('unassessed');
    }
    const result = suggestProducts(catalog(product()), inputs(), {})[0];
    expect(result.missing).toContain('analysis.solar.minimumPowerW');
  });
  it('returns only actual source IDs and rejects duplicate identities', () => {
    const p = product();
    expect(suggestProducts(catalog(p), inputs(), sizedAnalysis())[0].checks[0].sourceIds).toEqual(['source']);
    expect(() => suggestProducts(catalog(p, p), inputs(), sizedAnalysis())).toThrow(/duplicate product/);
  });
});

describe('requirements and physical accounting', () => {
  it('always exposes EPS-01..20 and unassessed energy subchecks even with no analysis', () => {
    const result = assessDesign(inputs(), {}, catalog(), {});
    expect(result.slice(0, 20).map(item => item.id)).toEqual(Array.from({ length: 20 }, (_, n) => `EPS-${String(n + 1).padStart(2, '0')}`));
    expect(result.slice(0, 20).every(item => item.verdict === 'unassessed')).toBe(true);
    expect(check(result, 'ENERGY-RESERVE').verdict).toBe('unassessed');
    expect(check(result, 'ENERGY-CLOSURE').verdict).toBe('unassessed');
  });
  it('permits scoped energy passes without a generic EPS-10/11 pass', () => {
    const i = inputs();
    const a = sizedAnalysis();
    a.simulation = simulateOrbit(i, i.scenarios[0], orbit);
    const result = assessDesign(i, a, catalog(), {});
    expect(check(result, 'ENERGY-RESERVE').verdict).toBe('pass');
    expect(check(result, 'ENERGY-CLOSURE').verdict).toBe('pass');
    for (const id of ['EPS-02', 'EPS-08', 'EPS-09', 'EPS-10', 'EPS-11', 'EPS-14', 'EPS-19']) {
      expect(check(result, id).verdict).toBe('unassessed');
    }
  });
  it('never promotes a supplied energy-only pass into a full EPS-10/11 pass', () => {
    const i = inputs();
    const simulation = simulateOrbit(i, i.scenarios[0], orbit);
    for (const id of ['EPS-10', 'EPS-11']) check(simulation.checks, id).verdict = 'pass';
    const result = assessDesign(i, { simulation }, catalog(), {});
    expect(check(result, 'EPS-10').verdict).toBe('unassessed');
    expect(check(result, 'EPS-11').verdict).toBe('unassessed');
  });
  it('propagates known energy and power failures into the relevant requirements', () => {
    const i = inputs();
    i.solar.installedPowerW = 0;
    i.battery.maxDischargeW = 1;
    const a = sizedAnalysis();
    a.simulation = simulateOrbit(i, i.scenarios[0], orbit);
    const result = assessDesign(i, a, catalog(), {});
    for (const id of ['EPS-02', 'EPS-07', 'EPS-10', 'EPS-11']) expect(check(result, id).verdict).toBe('fail');
    expect(check(result, 'EPS-15').verdict).toBe('unassessed');
  });
  it('ignores a different scenario simulation and does not invent a cycle-life fit', () => {
    const i = inputs();
    const a = sizedAnalysis();
    a.simulation = simulateOrbit(i, scenario({ id: 'other' }), orbit);
    const result = assessDesign(i, a, catalog(), {});
    expect(check(result, 'ENERGY-RESERVE').verdict).toBe('unassessed');
    expect(check(result, 'EPS-09').verdict).toBe('unassessed');
    expect(check(result, 'EPS-09').detail).toMatch(/No fit/);
  });
  it('leaves even a sourced scalar cycle life unassessed without DoD/temperature applicability', () => {
    const p = product({ id: 'pack', level: 'pack', roles: ['battery'], specs: { cycleLife: spec(1e7, 'cycles') } });
    const result = assessDesign(inputs(), sizedAnalysis(), catalog(p), { battery: p.id });
    expect(check(result, 'EPS-09').verdict).toBe('unassessed');
    expect(check(result, 'EPS-09').sourceIds).toEqual(['source']);
  });
  it('deduplicates one integrated board allocated to four roles and leaves auxiliaries unknown', () => {
    const p = product({ id: 'board', level: 'board', roles: ['battery', 'conditioning', 'distribution', 'processor'], specs: { massKg: spec(0.2, 'kg') } });
    const result = assessDesign(inputs(), {}, catalog(p), { battery: p.id, conditioning: p.id, distribution: p.id, processor: p.id });
    expect(check(result, 'KNOWN-MASS').detail).toMatch(/subtotal 0.20000000 kg/);
    expect(check(result, 'KNOWN-MASS').verdict).toBe('pass');
    expect(check(result, 'EPS-19').verdict).toBe('unassessed');
    expect(check(result, 'EPS-19').detail).toMatch(/Auxiliaries/);
  });
  it('counts suggested whole-panel quantity without scaling product properties', () => {
    const p = product();
    const a = sizedAnalysis();
    a.suggestions = suggestProducts(catalog(p), inputs(), a);
    const result = assessDesign(inputs(), a, catalog(p), { solar: p.id });
    expect(check(result, 'KNOWN-MASS').detail).toMatch(/subtotal 0.40000000 kg/);
    expect(p.specs.massKg.value).toBe(0.2);
  });
  it('fails a known minimum/actual mass excess, but not a typical unknown bound', () => {
    const p = product({ specs: { massKg: spec(2, 'kg') } });
    expect(check(assessDesign(inputs(), {}, catalog(p), { solar: p.id }), 'EPS-19').verdict).toBe('fail');
    p.specs.massKg.meaning = 'typical';
    const result = assessDesign(inputs(), {}, catalog(p), { solar: p.id });
    expect(check(result, 'EPS-19').verdict).toBe('unassessed');
    expect(check(result, 'KNOWN-MASS').verdict).toBe('unassessed');
  });
  it('keeps missing mass explicit and fails an unsupported role allocation', () => {
    const p = product({ specs: { massKg: spec(null, 'kg') } });
    const result = assessDesign(inputs(), {}, catalog(p), { solar: p.id, battery: p.id });
    expect(check(result, 'KNOWN-MASS').verdict).toBe('unassessed');
    expect(check(result, 'KNOWN-MASS').detail).toMatch(/massKg/);
    expect(check(result, 'EPS-01').verdict).toBe('fail');
  });
});
