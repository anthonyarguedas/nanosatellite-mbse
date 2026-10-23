import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { allocationIssues, productSnapshot } from '../engine/allocations';
import { nodeStatuses } from '../workflow';
import { createExampleWorkspace, evaluateReady } from './model';
import { parseWorkspace, restoreWorkspace, serializeWorkspace } from './serialization';

function expanded() {
  const next = structuredClone(catalog); next.revision = 'additive-catalog-revision';
  next.products.push({ ...structuredClone(next.products[0]), id: 'unrelated-new-product', partNumber: 'different-ordering-identity' });
  return next;
}
describe('catalog additions preserve authored history', () => {
  it('admits exact unchanged selected records across a global catalog revision', () => {
    const original = createExampleWorkspace(); const next = expanded();
    const restored = restoreWorkspace(JSON.parse(serializeWorkspace(original, catalog.revision)), next);
    expect(restored.inputs).toEqual(original.inputs);
    expect(restored.allocations).toEqual(original.allocations);
    expect(restored.provenance).toEqual(original.provenance);
    expect(restored.allocations!.every(r => r.catalogRevision === catalog.revision)).toBe(true);
    expect(allocationIssues(restored, next)).toEqual([]);
    expect(restored.analysis).toEqual({});
    expect(restored.catalogReview).toBeUndefined();
  });
  it('captures current legacy receipts without inferring a legacy count', () => {
    const raw = JSON.parse(serializeWorkspace(createExampleWorkspace(), catalog.revision));
    raw.allocations.forEach((r: { productSnapshot?: string }) => delete r.productSnapshot);
    const parsed = parseWorkspace(raw);
    expect(parsed.allocations!.every(r => r.productSnapshot === productSnapshot(catalog.products.find(p => p.id === r.productId)!))).toBe(true);
    delete raw.allocations;
    expect(parseWorkspace(raw).allocations).toBeUndefined();
  });
  it('keeps old unsnapshotted decisions for explicit review instead of adopting the example', () => {
    const original = createExampleWorkspace(); const raw = JSON.parse(serializeWorkspace(original, catalog.revision));
    raw.allocations.forEach((r: { productSnapshot?: string }) => delete r.productSnapshot);
    const next = expanded();
    expect(() => restoreWorkspace(raw, next)).toThrow(/snapshot/);
    const restored = restoreWorkspace(raw, next, true);
    expect(restored.inputs).toEqual(original.inputs);
    expect(restored.selections).toEqual(original.selections);
    expect(restored.allocations).toEqual(raw.allocations);
    expect(restored.catalogReview!.length).toBeGreaterThan(0);
    expect(nodeStatuses(evaluateReady(restored)).simulation).toBe('locked');
  });
  it.each(['removed-product', 'removed-role'] as const)('preserves %s changes for local review', mutation => {
    const original = createExampleWorkspace(); const next = expanded();
    const selected = next.products.find(p => p.id === original.selections.battery)!;
    if (mutation === 'removed-product') next.products.splice(next.products.indexOf(selected), 1);
    else selected.roles = ['processor'];
    const restored = restoreWorkspace(JSON.parse(serializeWorkspace(original, catalog.revision)), next, true);
    expect(restored.inputs).toEqual(original.inputs);
    expect(restored.selections).toEqual(original.selections);
    expect(restored.catalogReview!.length).toBeGreaterThan(0);
    expect(nodeStatuses(restored).simulation).toBe('locked');
  });
  it.each(['revision', 'same-revision-fact'] as const)('flags changed %s without rebinding provenance or erasing decisions', mutation => {
    const original = createExampleWorkspace(); const next = expanded();
    const changed = next.products.find(p => p.id === original.selections.battery)!;
    if (mutation === 'revision') changed.revision = 'new-product-record';
    else changed.specs.energyWh.value = 85;
    const raw = JSON.parse(serializeWorkspace(original, catalog.revision));
    expect(() => restoreWorkspace(raw, next)).toThrow(/mismatched|provenance/);
    const restored = restoreWorkspace(raw, next, true);
    expect(restored.inputs.battery.capacityWh).toBe(86);
    expect(restored.allocations).toEqual(original.allocations);
    expect(restored.provenance).toEqual(original.provenance);
    expect(restored.catalogReview!.length).toBeGreaterThan(0);
    expect(restored.records.simulation.evaluatedRevision).toBeNull();
  });
});
