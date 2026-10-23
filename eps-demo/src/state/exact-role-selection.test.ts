import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { inputs, product, spec } from '../engine/__tests__/fixtures';
import { assessDesign } from '../engine';
import { applyProduct } from './model';
import { unallocatedCurrentWorkspace } from './test-fixtures';
import { getKiCadReadiness } from '../kicad';
import { fixture } from '../kicad/__tests__/fixtures';
import { productSnapshot } from '../engine/allocations';

describe('exact standalone role allocations', () => {
  it.each(['distribution', 'processor', 'software'] as const)('allocates %s without a conditioning alias or feasibility pass', role => {
    const p = product({ id: `synthetic-${role}`, roles: [role], level: role === 'software' ? 'software' : 'board' });
    catalog.products.push(p);
    try {
      const workspace = unallocatedCurrentWorkspace();
      const suggestion = workspace.analysis.suggestions!.find(s => s.productId === p.id)!;
      expect(suggestion.role).toBe(role);
      expect(suggestion.outcome).toBe('incomplete');
      expect(suggestion.checks.every(c => c.verdict === 'unassessed')).toBe(true);
      const allocated = applyProduct(workspace, role, p.id);
      expect(allocated.selections).toEqual({ [role]: p.id });
      expect(allocated.allocations![0]).toMatchObject({ roles: [role], quantity: 1, productSnapshot: productSnapshot(p) });
      const rejected = structuredClone(workspace); rejected.analysis.suggestions!.find(s => s.productId === p.id)!.checks[0].verdict = 'fail';
      expect(() => applyProduct(rejected, role, p.id)).toThrow(/known violation/);
    } finally { catalog.products.splice(catalog.products.indexOf(p), 1); }
  });
  it('never adds software mass or an invented zero-mass hardware product', () => {
    const host = product({ id: 'host', level: 'board', roles: ['processor'], specs: { massKg: spec(.2, 'kg') } });
    const software = product({ id: 'software', level: 'software', roles: ['software'], specs: {} });
    const currentCatalog = { revision: 'test', products: [host, software] };
    const selections = { processor: host.id, software: software.id };
    const allocations = [host, software].map(p => ({ productId: p.id, productRevision: p.revision, catalogRevision: 'test', roles: p.roles, quantity: 1, origin: 'engineer-allocation' as const, rationale: 'Synthetic', allocatedAt: '2026-10-17T00:00:00Z' }));
    const checks = assessDesign(inputs(), {}, currentCatalog, selections, allocations);
    expect(checks.find(c => c.id === 'KNOWN-MASS')?.detail).toContain('subtotal 0.20000000 kg');
    expect(checks.find(c => c.id === 'KNOWN-MASS')?.detail).toContain('physical resources belong to its host');
    expect(checks.find(c => c.id === 'EPS-19')?.verdict).toBe('unassessed');
  });
  it('requires exact-role readiness and keeps physical routing blocked', () => {
    const { workspace, catalog } = fixture();
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(true);
    workspace.analysis.suggestions = workspace.analysis.suggestions!.filter(s => s.role !== 'distribution');
    const readiness = getKiCadReadiness(workspace, catalog);
    expect(readiness.blockers.join(' ')).toMatch(/distribution/);
    expect(readiness.physicalRouting).toBe('blocked');
  });
  it('allows an unrelated catalog addition only with exact selected record snapshots', () => {
    const { workspace, catalog } = fixture();
    workspace.allocations!.forEach(r => { r.productSnapshot = productSnapshot(catalog.products.find(p => p.id === r.productId)!); });
    catalog.revision = 'new-additive-revision';
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(true);
    catalog.products[0].specs.massKg = { value: 1, unit: 'kg', status: 'missing', meaning: 'specified', original: 'bad', conditions: 'bad', sourceId: null, location: 'bad' };
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(false);
  });
});
