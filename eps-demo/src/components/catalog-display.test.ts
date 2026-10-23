import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { specValue } from './CatalogView';

 describe('catalog value meaning in the GUI', () => {
  it('keeps inapplicable values distinct from missing evidence', () => {
    const pack = catalog.products.find(product => product.id === 'gomspace-bp8-100wh-8s1p')!;
    expect(pack.specs.powerBolW.status).toBe('not-applicable');
    expect(specValue(pack.specs.powerBolW)).toBe('Not applicable');
    expect(pack.specs.cycleLife.status).toBe('missing');
    expect(specValue(pack.specs.cycleLife)).toBe('Missing evidence');
  });
  it('does not truncate trailing zeroes from whole scalar ratings', () => {
    const base = catalog.products[0].specs.powerBolW;
    expect(specValue({ ...base, value: 100 })).toBe('100 W');
    expect(specValue({ ...base, value: 0 })).toBe('0 W');
    expect(specValue({ ...base, value: 2.15118 })).toBe('2.15 W');
    expect(specValue({ ...base, value: -0.0067, unit: 'V/K' })).toBe('-0.0067 V/K');
    expect(specValue({ ...base, value: 0.00015, unit: 'm' })).toBe('0.00015 m');
  });
});
