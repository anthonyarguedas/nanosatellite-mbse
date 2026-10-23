import { describe, expect, it } from 'vitest';
import { catalog } from './catalog';
import { productCoverage } from '../catalog/coverage';

const get = (id: string) => catalog.products.find(p => p.id === id)!;
describe('approved final source corrections', () => {
  it('keeps HP radiation-axis conditions at 28 C and 82921 at 25 C', () => {
    const hp = get('azur-3g30c-advanced-hp-82645');
    expect(hp.specs.radiationFluencesPerCm2.conditions).toContain('28 °C');
    expect(hp.specs.radiationFluencesPerCm2.conditions).not.toContain('25 °C');
    expect(get('azur-4g32c-advanced-82921').specs.radiationFluencesPerCm2.conditions).toContain('25 °C');
    expect(hp.sources[0].sha256).toBe('60f8232edda3e0d5c6ce19ebb95f98770668930c94fb4b1ab0cde13bb2015ef9');
  });
  it.each([
    ['saft-mp144350xlr-cell', 5], ['saft-mp174865xlr-cell', 10], ['saft-mp176065xlr-cell', 13.6],
  ] as const)('preserves %s conditional discharge ceilings and the simultaneous-maxima warning', (id, ceiling) => {
    const p = get(id); const current = p.specs.maxDischargeA;
    expect(current.value).toBe(ceiling);
    expect(current.conditions).toContain('Other temperatures require derating');
    expect(current.conditions).toContain('maximum voltage, current and temperature conditions may not be mutually inclusive');
    expect(current.conditions).toContain('not a guaranteed rectangular operating envelope');
    expect([current.sourceId, ...current.additionalSourceIds ?? []]).toContain('saft-a0018-10-public-manual');
    expect(current.location).toContain('section 4.4 footnote [3]');
    expect(productCoverage(p, 'battery').comparisonCovered).toBe(true);
  });
  it('uses the correct larger-cell descriptions and removes false NA aliases only', () => {
    expect(get('saft-mp174865xlr-cell').description).toContain('MP 174865 xlr');
    expect(get('saft-mp176065xlr-cell').description).toContain('MP 176065 xlr');
    const p = get('saft-mp144350xlr-cell');
    expect(p.specs).not.toHaveProperty('nameplateEnergyWh');
    expect(p.specs).not.toHaveProperty('nameplateChargeAh');
    expect(p.specs.energyWh).toMatchObject({ value: 9.4, meaning: 'nominal' });
    expect(p.specs.chargeAh).toMatchObject({ value: 2.6, meaning: 'typical' });
  });
  it('keeps real electrical SKUs and P31U library scope distinct from cosmetic variants or internal firmware', () => {
    const mp = get('pololu-2812-big-mp'); const hp = get('pololu-2813-big-hp');
    expect(mp.partNumber).not.toBe(hp.partNumber);
    const lv = get('pololu-astar-32u4-mini-lv-3103'); const sv = get('pololu-astar-32u4-mini-sv-3145');
    expect(lv.specs.processorSupplyMinV.value).toBe(2.7);
    expect(sv.specs.processorSupplyMinV.value).toBe(5);
    expect(sv.partNumber).toContain('3145'); expect(sv.partNumber).not.toContain('3104');
    const api = get('kubos-gomspace-p31u-api');
    expect(api.description).toMatch(/external|Linux/i);
    expect(api.specs.requiredDataBytes.status).toBe('missing');
    expect(api.specs.executionBoundsS.status).toBe('missing');
    expect(api.specs.deadlinesS.status).toBe('missing');
    expect(productCoverage(api, 'software').comparisonCovered).toBe(true);
  });
});
