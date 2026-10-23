import { describe, expect, it } from 'vitest';
import { catalog } from './catalog';
import register from './evidence/source-register.json';
import oldCatalog from '../state/__fixtures__/pre-enrichment-catalog.json';
import { catalogCoverage, isLoadConverter, productCoverage } from '../catalog/coverage';
import { specificationIssues, validateCatalog } from '../catalog/validation';
import { numericEvidence } from '../engine/catalog';
import { spec } from '../engine/__tests__/fixtures';

const get = (id: string) => catalog.products.find(p => p.id === id)!;
const solar = ['azur-3g30c-advanced-81780', 'azur-4g32c-advanced-82921', 'azur-3g30c-advanced-hp-82645'];
const batteries = ['saft-mp144350xlr-cell', 'saft-mp174865xlr-cell', 'saft-mp176065xlr-cell'];
const converters = ['pololu-2843-d24v5f5', 'pololu-3786-d36v28f12', 'pololu-4083-s13v10f5'];

describe('reviewed data targets and preserved source identity', () => {
  it('enforces all six real comparison targets without membership padding', () => {
    const report = catalogCoverage(catalog);
    expect(report.integrityIssues).toEqual([]);
    expect(report.roles.map(r => [r.records, r.distinctOptions, r.coveredOptions, r.deficit])).toEqual([
      [5, 5, 3, 0], [10, 9, 3, 0], [7, 7, 3, 0], [8, 8, 3, 0], [9, 9, 3, 0], [5, 5, 3, 0],
    ]);
    for (const [role, ids] of [
      ['solar', solar], ['battery', batteries], ['conditioning', converters],
      ['distribution', ['pololu-2808-mini-lv', 'pololu-2813-big-hp', 'pololu-2812-big-mp']],
      ['processor', ['pololu-astar-32u4-micro-3101', 'pololu-astar-32u4-mini-lv-3103', 'pololu-astar-32u4-mini-sv-3145']],
      ['software', ['quetzal1-eps-firmware-dbfb67a', 'kubos-clyde-3g-eps-service', 'kubos-gomspace-p31u-api']],
    ] as const) {
      expect(new Set(ids.map(id => get(id).partNumber)).size).toBe(3);
      for (const id of ids) expect(productCoverage(get(id), role).comparisonCovered, id).toBe(true);
    }
  });
  it('retains every original fact and all six original Source identity strings verbatim', () => {
    expect(catalog.revision).not.toBe(oldCatalog.revision);
    for (const old of oldCatalog.products) {
      const now = get(old.id);
      expect(now.revision).toBe(old.revision);
      for (const [key, value] of Object.entries(old.specs)) expect(now.specs[key], `${old.id}/${key}`).toEqual(value);
      for (const source of old.sources) expect(now.sources.find(s => s.id === source.id)).toMatchObject(source);
    }
  });
  it('registers exact reviewed source bytes and preserves contextual source identities', () => {
    const sources = new Map(catalog.products.flatMap(p => p.sources).map(s => [s.id, s]));
    expect(sources.size).toBe(156);
    expect(new Set([...sources.values()].map(s => s.sha256)).size).toBe(129);
    expect(register.catalogRevision).toBe(catalog.revision);
    expect(register.sources).toHaveLength(sources.size);
    for (const source of sources.values()) {
      expect(source.publisher).toBeTruthy(); expect(source.kind).toBeTruthy(); expect(source.sha256).toMatch(/^[a-f0-9]{64}$/);
      const row = register.sources.find(s => s.id === source.id)!;
      expect(row).toMatchObject(source);
      expect(row.byteAudit.status).toBe('verified-local-bytes');
      expect(row.usedBy.length).toBeGreaterThan(0);
    }
  });
  it('keeps genuine solar and battery characterization limits visible', () => {
    expect(get(solar[2]).specs.widthM.value).toBe(.1459);
    expect(get(solar[2]).caveats.join(' ')).toMatch(/1U|body.mounted/i);
    expect(get('spectrolab-xte-sf-27cm2').specs.widthM.status).toBe('missing');
    for (const id of batteries) {
      const p = get(id);
      expect(p.level).toBe('cell'); expect(p.specs.energyWh.meaning).toBe('nominal');
      for (const key of ['retainedEnergyFraction', 'retainedChargeFraction', 'chargeEfficiency', 'dischargeEfficiency', 'coulombicChargeEfficiency', 'coulombicDischargeEfficiency']) expect(p.specs[key].status, `${id}/${key}`).toBe('missing');
    }
    expect(get('saft-mp176065xlr-cell').specs.maxDischargeA.value).toBe(13.6);
    expect(get('saft-mp176065xlr-cell').specs.maxDischargeA.conditions).toMatch(/10|60/);
  });
  it('preserves both published high-current wiring alternatives for the MP switch', () => {
    const wiring = get('pololu-2812-big-mp').specs.requiredExternalItems;
    expect(wiring.value).toMatch(/large power holes or both small holes/);
    expect(wiring.original).toContain('either use the large holes or both');
  });
  it('deduplicates EnduroSat and keeps the BIRDS assembly as reference context only', () => {
    const entries = catalog.products.filter(p => /endurosat/i.test(p.manufacturer));
    expect(entries).toHaveLength(1);
    expect(entries[0].roles).toEqual(['conditioning', 'distribution', 'battery', 'processor']);
    expect(entries[0].specs.maxChargeA.status).toBe('missing');
    expect(entries[0].specs.chargerFastModeMaxA.value).toBe(.49);
    expect(entries[0].specs.pvSourceProtectionThresholdA.value).toBe(1.8);
    expect(entries[0].specs.maxPvInputCurrentA.status).toBe('missing');
    const birds = get('birds-bk3mcce-3s2p-published-assembly');
    expect(birds.catalogUse).toBe('reference-only'); expect(birds.specs.energyWh.value).toBe(14.4);
    expect(birds.specs.energyWh.meaning).toBe('nominal'); expect(birds.specs.massKg.status).toBe('missing');
    expect(productCoverage(birds, 'battery').comparisonCovered).toBe(false);
  });
});

describe('signed data and converter applicability', () => {
  it('keeps negative coefficients and Celsius facts numeric while protecting physical domains', () => {
    const p = get(solar[0]);
    expect(p.specs.tempCoefficientVmpBolVPerK.value).toBe(-.0067);
    expect(specificationIssues(p, 'tempCoefficientVmpBolVPerK', p.specs.tempCoefficientVmpBolVPerK)).toEqual([]);
    const bp8 = get('gomspace-bp8-100wh-8s1p');
    expect(bp8.specs.absoluteChargeTemperatureC.value).toEqual([-10, 45]);
    expect(bp8.specs.absoluteChargeTemperatureC.valueForm).toBe('interval');
    expect(specificationIssues(p, 'signedAbsoluteLimitV', { ...spec(-.3, 'V'), sourceId: p.sources[0].id })).toEqual([]);
    for (const [key, unit] of [['energyWh', 'Wh'], ['massKg', 'kg'], ['idlePowerW', 'W'], ['seriesCells', 'count']]) expect(specificationIssues(p, key, spec(-1, unit)).join(' ')).toMatch(/domain/);
  });
  it('branches only explicitly reviewed load converters, without repurposing switch ratings', () => {
    for (const id of converters) {
      const p = get(id); expect(isLoadConverter(p)).toBe(true);
      expect(productCoverage(p, 'conditioning').core.some(r => r.id === 'inputCurrent')).toBe(false);
      expect(p.specs.maxPvInputCurrentA.status).not.toBe('available');
    }
    const unreviewed = structuredClone(get(converters[0]));
    unreviewed.sources.find(s => s.id === unreviewed.specs.conditioningApplicability.sourceId)!.sha256 = undefined;
    expect(isLoadConverter(unreviewed)).toBe(false);
    const pv = structuredClone(get('gomspace-p80-config1'));
    pv.specs.maxPvInputCurrentA = { ...pv.specs.maxPvInputCurrentA, value: null, status: 'not-applicable', rationale: 'Invalid applicability claim.' };
    pv.specs.maxInputA.status = 'missing';
    pv.specs.conditioningApplicability = { ...spec(1, '1'), value: 'load-converter', sourceId: pv.sources[0].id };
    expect(isLoadConverter(pv)).toBe(false);
    expect(productCoverage(pv, 'conditioning').core.find(r => r.id === 'inputCurrent')?.covered).toBe(false);
  });
  it('requires every cited document for multi-source component sums and keeps intervals scalar-ineligible', () => {
    const p = get('gomspace-p60-one-acu-one-pdu-16v');
    expect(p.specs.temperatureC.value).toEqual([-35, 85]);
    expect(p.specs.temperatureC.valueForm).toBe('interval');
    expect(p.specs.temperatureC.unit).toBe('°C');
    expect(p.specs.massKg.additionalSourceIds).toHaveLength(2);
    expect(numericEvidence(p, 'massKg').sourceIds).toHaveLength(3);
    const broken = structuredClone(p); broken.specs.massKg.additionalSourceIds!.push('absent');
    expect(validateCatalog({ revision: 'test', products: [broken] }).join(' ')).toMatch(/source reference/);
    expect(numericEvidence(broken, 'massKg').value).toBeUndefined();
    expect(numericEvidence(get('gomspace-p80-config1'), 'pdu5VRegulatorEfficiencyPoint').value).toBeUndefined();
    expect(get('gomspace-p80-config1').specs.efficiency.status).toBe('missing');
  });
});
