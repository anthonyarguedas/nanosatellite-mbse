import { describe, expect, it } from 'vitest';
import { catalog } from './catalog';

 describe('reviewed COTS catalog', () => {
  it('has bounded, revisioned alternatives for generation, storage and conditioning', () => {
    expect(catalog.revision).toBeTruthy();
    expect(catalog.products.length).toBeGreaterThanOrEqual(6);
    expect(catalog.products.length).toBeLessThanOrEqual(12);
    expect(new Set(catalog.products.map(product => product.id)).size).toBe(catalog.products.length);
    for (const role of ['solar', 'battery', 'conditioning']) expect(catalog.products.some(product => product.roles.includes(role as 'solar' | 'battery' | 'conditioning'))).toBe(true);
  });
  it('retains source identity, revision and conditions for available specifications', () => {
    for (const product of catalog.products) {
      expect(product.revision, product.name).toBeTruthy();
      expect(product.accountingBoundary, product.name).toBeTruthy();
      expect(product.sources.length, product.name).toBeGreaterThan(0);
      const ids = new Set(product.sources.map(source => source.id));
      for (const source of product.sources) {
        expect(source.url).toMatch(/^https?:\/\//);
        expect(source.title).toBeTruthy();
        expect(source.retrievedAt).toMatch(/^\d{4}-\d{2}-\d{2}/);
        expect(source.revision).toBeTruthy();
      }
      for (const [key, spec] of Object.entries(product.specs)) {
        expect(spec.original, `${product.name}/${key}`).toBeTruthy();
        expect(spec.conditions, `${product.name}/${key}`).toBeTruthy();
        if (spec.status === 'available') {
          expect(spec.value, `${product.name}/${key}`).not.toBeNull();
          expect(ids.has(spec.sourceId!), `${product.name}/${key}`).toBe(true);
          expect(spec.location, `${product.name}/${key}`).toBeTruthy();
          if (typeof spec.value === 'number') expect(Number.isFinite(spec.value)).toBe(true);
        } else expect(spec.value, `${product.name}/${key}`).toBeNull();
      }
    }
  });
  it('does not fill missing EOL power with a BOL rating', () => {
    const hasExplicitMissing = catalog.products.filter(product => product.roles.includes('solar')).some(product => product.specs.powerEolW?.status === 'missing');
    expect(hasExplicitMissing).toBe(true);
    for (const product of catalog.products) {
      const spec = product.specs.powerEolW;
      if (spec?.status === 'available') expect(`${spec.conditions} ${spec.original}`).toMatch(/EOL|end.of.life|fluence|radiation|1[01].?1[45]/i);
    }
  });
  it('does not imply a price from missing procurement evidence', () => {
    for (const product of catalog.products) {
      const price = product.specs.priceUsd;
      if (!price || price.status !== 'available') continue;
      expect(price.sourceId).toBeTruthy();
      expect(price.conditions).toMatch(/date|quote|\d{4}/i);
    }
  });
});
