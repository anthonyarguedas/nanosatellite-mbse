import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import type { Product, Role, Specification } from '../types';
import { product, spec } from '../engine/__tests__/fixtures';
import { catalogCoverage, optionIdentity, productCoverage } from './coverage';
import { ROLE_PROFILES, ROLES, SPEC_DEFINITIONS } from './profiles';
import { specificationIssues, validateCatalog } from './validation';

/** Synthetic complete comparison evidence. Never a real product or feasibility fixture. */
export function coveredProduct(role: Role): Product {
  const p = product({ id: `synthetic-${role}`, partNumber: `TEST-${role}`, level: role === 'software' ? 'software' : 'board', roles: [role], specs: {} });
  p.sources[0] = { ...p.sources[0], publisher: 'Synthetic maker', kind: role === 'software' ? 'maintainer' : 'manufacturer', sha256: 'a'.repeat(64) };
  for (const r of ROLE_PROFILES[role].core) for (const key of r.anyOf[0]) {
    const def = SPEC_DEFINITIONS[key];
    p.specs[key] = { ...spec(1, def.unit), value: def.type === 'text' ? 'Documented test function and configuration' : 1,
      conditions: 'BOL or EOL fluence 1E14 electrons/cm², AM0 1367 W/m², 28 °C; 2 V to 4 V window. Duration not stated.' };
  }
  if (p.specs.outputRails) p.specs.outputRails.value = '5 V output, 2 A continuous per channel, one shared 2 A group';
  if (p.specs.serviceDefinitions) p.specs.serviceDefinitions.value = 'Implemented EPS battery telemetry and power output control';
  return p;
}

describe('frozen sourced comparison profiles', () => {
  it('separates valid integrity from reached comparison targets', () => {
    const report = catalogCoverage(catalog);
    expect(report.integrityIssues).toEqual([]);
    expect(report.roles.map(r => r.records)).toEqual([5, 10, 7, 8, 9, 5]);
    expect(report.roles.map(r => r.coveredOptions)).toEqual([3, 3, 3, 3, 3, 3]);
    expect(report.roles.every(r => r.coveredOptions >= 3 && r.deficit === 0)).toBe(true);
    expect(report).not.toHaveProperty('feasible');
    expect(Object.isFrozen(ROLE_PROFILES.battery.core)).toBe(true);
  });
  it.each(ROLES)('covers %s comparison with richer characterization still missing', role => {
    const p = coveredProduct(role);
    const report = productCoverage(p, role);
    expect(report.comparisonCovered, JSON.stringify(report.core.filter(r => !r.covered))).toBe(true);
    expect(report.richer.some(r => !r.covered)).toBe(true);
    expect(report.scope).toMatch(/does not establish.*feasibility/);
    expect(validateCatalog({ revision: 'test', products: [p] })).toEqual([]);
  });
  it.each(['missing', 'not-applicable'] as const)('never counts mandatory %s as covered', status => {
    const p = coveredProduct('software');
    p.specs.softwareRelease = { ...p.specs.softwareRelease, status, value: null, rationale: 'Unavailable, not hidden.' };
    expect(productCoverage(p, 'software').comparisonCovered).toBe(false);
  });
  it('counts rename and record revisions as one real option', () => {
    const p = coveredProduct('software');
    const renamed = { ...structuredClone(p), id: 'different-id', revision: 'new-record', name: 'Renamed product' };
    const report = catalogCoverage({ revision: 'test', products: [p, renamed] });
    expect(optionIdentity(p)).toBe(optionIdentity(renamed));
    expect(report.roles.find(r => r.role === 'software')).toMatchObject({ records: 2, distinctOptions: 1, coveredOptions: 1, deficit: 2 });
  });
  it('requires source identity and genuine EPS services, not a generic platform label', () => {
    const p = coveredProduct('software');
    p.specs.serviceDefinitions.value = 'Generic operating system and SDK';
    expect(productCoverage(p, 'software').comparisonCovered).toBe(false);
    p.sources[0].sha256 = undefined;
    expect(productCoverage(p, 'software').core.every(r => !r.covered)).toBe(true);
  });
  it('requires stated solar temperature, explicit charger policy and stable software identity', () => {
    const solar = coveredProduct('solar'); solar.specs.powerEolW.conditions = 'AM0 1367 W/m²; EOL fluence 1E14; temperature not stated';
    expect(productCoverage(solar, 'solar').comparisonCovered).toBe(false);
    const charger = coveredProduct('conditioning'); charger.specs.conditioningMode.value = 'MPPT and battery charger';
    delete charger.specs.chargeTermination;
    expect(productCoverage(charger, 'conditioning').comparisonCovered).toBe(false);
    const software = coveredProduct('software'); software.partNumber = 'maintainer/eps@v1.2.3';
    expect(optionIdentity(software)).toBe(optionIdentity({ ...software, partNumber: 'maintainer/eps@v2.3.4' }));
  });
  it('does not substitute a different rating for EOL or a trip threshold for current', () => {
    const p = coveredProduct('solar'); delete p.specs.powerEolW;
    expect(productCoverage(p, 'solar').core.find(r => r.id === 'eol')?.covered).toBe(false);
    const battery = coveredProduct('battery'); battery.specs.maxChargeA.original = 'Overcurrent protection trip threshold';
    expect(productCoverage(battery, 'battery').comparisonCovered).toBe(false);
  });
});

describe('catalog integrity without snapshot-only restrictions', () => {
  it('accepts new publishers, HTML/software, real dates, aging facts and prices', () => {
    const p = coveredProduct('software');
    p.sources[0].url = 'https://new-maintainer.org/releases/v1'; p.sources[0].retrievedAt = '2026-10-22';
    p.specs.priceUsd = { ...spec(10, 'USD'), conditions: 'Dated quote 2026-10-22' };
    p.specs.cycleLife = spec(1000, 'cycles');
    expect(validateCatalog({ revision: 'test', products: [p] })).toEqual([]);
  });
  it('accepts direct EOL power at a different radiation endpoint without synthesizing a pair', () => {
    const p = coveredProduct('solar');
    expect(p.specs.vmpEolV).toBeUndefined();
    expect(validateCatalog({ revision: 'new', products: [p] })).toEqual([]);
  });
  it.each(['original', 'conditions', 'location', 'sourceId', 'unit'] as const)('rejects a broken %s', key => {
    const p = coveredProduct('battery'); p.specs.energyWh[key] = '';
    expect(validateCatalog({ revision: 'test', products: [p] }).length).toBeGreaterThan(0);
  });
  it('rejects shared source IDs with differing evidence and invalid calendar dates', () => {
    const a = coveredProduct('solar'); const b = coveredProduct('battery'); b.sources[0].revision = 'other';
    expect(validateCatalog({ revision: 'test', products: [a, b] }).join(' ')).toMatch(/collision/);
    b.sources[0].retrievedAt = '2026-02-30';
    expect(validateCatalog({ revision: 'test', products: [b] }).join(' ')).toMatch(/date/);
  });
  it('requires explicit array semantics and keeps numerical evidence scalar', () => {
    const p = coveredProduct('battery');
    const value: Specification = { ...spec(1, 'kg'), value: [1, 2] };
    expect(specificationIssues(p, 'massKg', value).join(' ')).toMatch(/valueForm/);
    expect(specificationIssues(p, 'massKg', { ...value, valueForm: 'interval' })).toEqual([]);
    expect(specificationIssues(p, 'massKg', { ...value, valueForm: 'min-typ-max' }).join(' ')).toMatch(/tuple/);
  });
  it('preserves named manufacturer snapshot regressions', () => {
    for (const id of ['azur-3g30c-advanced-81780', 'isis-iceps2-type-a', 'gomspace-p80-config1']) {
      const p = structuredClone(catalog.products.find(p => p.id === id)!);
      if (id.startsWith('azur')) p.specs.powerEolW.value = 9;
      if (id.startsWith('isis')) p.specs.inputMaxV.value = 15;
      if (id.includes('p80')) p.roles.push('battery');
      expect(validateCatalog({ revision: 'test', products: [p] }).length).toBeGreaterThan(0);
    }
  });
});
