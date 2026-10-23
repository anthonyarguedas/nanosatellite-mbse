import { describe, expect, it } from 'vitest';
import { buildKiCadExport, createKiCadZip, getKiCadReadiness } from '../index';
import { fixture, REQUIRED_NODES } from './fixtures';
import type { Workspace } from '../../types';

const manifest = (files: { name: string; content: string }[]) => JSON.parse(files.find(f => f.name === 'manifest.json')!.content);

describe('KiCad logical review export', () => {
  for (const id of REQUIRED_NODES) {
    it(`blocks a stale ${id} even when candidates look current`, () => {
      const { workspace, catalog } = fixture();
      workspace.records[id].revision++;
      expect(getKiCadReadiness(workspace, catalog).ready).toBe(false);
      expect(() => buildKiCadExport(workspace, catalog)).toThrow(/stale/);
    });
    it(`blocks uncomputed ${id}`, () => {
      const { workspace, catalog } = fixture();
      workspace.records[id].evaluatedRevision = null;
      expect(() => buildKiCadExport(workspace, catalog)).toThrow(/uncomputed/);
    });
  }
  it('checks canonical input validity rather than trusting current-looking revision records', () => {
    const { workspace, catalog } = fixture();
    workspace.inputs.mission.altitudeKm = null;
    expect(workspace.records.candidates.evaluatedRevision).toBe(workspace.records.candidates.revision);
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(false);
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/uncomputed or stale/);
  });
  it('reports malformed dependency records without crashing readiness inspection', () => {
    const { workspace, catalog } = fixture();
    delete (workspace.records as Partial<Workspace['records']>).mission;
    const readiness = getKiCadReadiness(workspace, catalog);
    expect(readiness.ready).toBe(false);
    expect(readiness.blockers.join(' ')).toContain('malformed');
  });
  it('needs current output and an applicable non-rejected suggestion', () => {
    const { workspace, catalog } = fixture();
    delete workspace.analysis.suggestions;
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/missing/);
    const next = fixture();
    next.workspace.analysis.suggestions![0].outcome = 'rejected';
    expect(() => buildKiCadExport(next.workspace, next.catalog)).toThrow(/rejected/);
  });
  it('requires a role-specific primary suggestion rather than borrowing another screen', () => {
    const { workspace, catalog } = fixture();
    workspace.analysis.suggestions![0].role = 'conditioning';
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/non-rejected current suggestion for solar/);
  });
  it('rejects a failed check even if its outcome is incorrectly marked incomplete', () => {
    const { workspace, catalog } = fixture();
    workspace.analysis.suggestions![0].checks.push({ id: 'test', title: 'Test failure', verdict: 'fail', detail: 'Known violation' });
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(false);
  });
  it('rejects absent, unsupported and zero-quantity allocations', () => {
    const { workspace, catalog } = fixture();
    workspace.selections.solar = 'absent';
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/absent/);
    workspace.selections.solar = 'test-pack';
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/does not provide/);
    workspace.selections.solar = 'test-solar';
    workspace.analysis.suggestions![0].quantity = 0;
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/positive integer/);
  });
  it('requires explicit counts for legacy selections instead of installing current suggestions', () => {
    const { workspace, catalog } = fixture();
    delete workspace.allocations;
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(false);
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/frozen concept allocation quantity/);
  });
  it('freezes allocation counts independently of subsequent screening quantities', () => {
    const { workspace, catalog } = fixture();
    workspace.analysis.suggestions![0].quantity = 99;
    const result = buildKiCadExport(workspace, catalog);
    const usage = manifest(result.files).usages.find((item: { productId: string }) => item.productId === 'test-solar');
    expect(usage.quantity).toBe(2);
    expect(usage.allocationReceipt.quantity).toBe(2);
    expect(result.warnings.join(' ')).toContain('differs from current screening count 99');
  });
  it('rejects an allocation receipt bound to a different catalog revision', () => {
    const { workspace, catalog } = fixture();
    workspace.allocations![0].catalogRevision = 'superseded';
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/revision is absent or mismatched/);
  });
  it('exports selected usages only, deduplicates an integrated board and preserves source evidence', () => {
    const { workspace, catalog } = fixture();
    const result = buildKiCadExport(workspace, catalog);
    const m = manifest(result.files);
    expect(m.usages).toHaveLength(3);
    const board = m.usages.find((u: { productId: string }) => u.productId === 'test-board');
    expect(board.allocatedRoles).toEqual(['conditioning', 'distribution', 'processor']);
    expect(board.quantity).toBe(1);
    expect(board.product.sources[0].url).toBe('https://example.org/test');
    expect(board.catalogEntryRevision).toContain('hardware revision unknown');
    expect(m.usages.some((u: { productId: string }) => u.productId === 'unused')).toBe(false);
    expect(m.drawing.associations.filter((a: { internal: boolean }) => a.internal)).toHaveLength(2);
    expect(m.drawing.unresolvedLogicalAssociations).toEqual([]);
    expect(result.files.some(f => /\.kicad_pcb$/.test(f.name))).toBe(false);
    expect(m.physicalRouting.status).toBe('blocked');
    expect(m.physicalRouting.unresolvedPhysicalNets).toMatch(/Unknown/);
    expect(result.warnings.join(' ')).toContain('incomplete');
  });
  it('makes real schematic wires between abstract named sheet ports with no component pins', () => {
    const { workspace, catalog } = fixture();
    const result = buildKiCadExport(workspace, catalog);
    const root = result.files.find(f => f.name === 'orbitwork-review.kicad_sch')!.content;
    expect(root).toContain('(wire ');
    expect(root).toContain('(pin "L_SOLAR_POWER" passive');
    expect(root).not.toMatch(/\(pin "\d+"/);
    expect(root).not.toContain('(symbol ');
    expect(root).not.toContain('(lib_id ');
    expect(root).toContain('REVIEW ONLY');
    for (const edge of manifest(result.files).drawing.associations) {
      if (!edge.points) continue;
      for (let i = 1; i < edge.points.length; i++) {
        const a = edge.points[i - 1], b = edge.points[i];
        expect(a.x === b.x || a.y === b.y).toBe(true);
      }
    }
  });
  it('marks unallocated roles and does not fabricate links to missing COTS modules', () => {
    const { workspace, catalog } = fixture();
    workspace.selections = { solar: 'test-solar' };
    workspace.allocations = workspace.allocations?.filter(receipt => receipt.productId === 'test-solar');
    const m = manifest(buildKiCadExport(workspace, catalog).files);
    expect(m.usages).toHaveLength(1);
    expect(m.drawing.associations).toHaveLength(0);
    expect(m.unallocatedRoles).toContain('conditioning');
    workspace.selections = {};
    workspace.allocations = [];
    expect(() => buildKiCadExport(workspace, catalog)).toThrow(/at least one/);
  });
  it('is deterministic and safely quotes authored text', () => {
    const { workspace, catalog } = fixture();
    workspace.inputs.mission.name = 'Quote " / slash \\ / newline\nwith unicode Ω';
    const first = buildKiCadExport(workspace, catalog);
    expect(buildKiCadExport(workspace, catalog)).toEqual(first);
    expect(first.files.find(f => f.name === 'orbitwork-review.kicad_sch')!.content).toContain('\\"');
    const zip = createKiCadZip(first.files);
    expect(new DataView(zip.buffer).getUint32(0, true)).toBe(0x04034b50);
    expect(new DataView(zip.buffer).getUint32(zip.length - 22, true)).toBe(0x06054b50);
    expect(createKiCadZip(first.files)).toEqual(zip);
  });
  it('does not require a simulation or assessment cache for a logical review', () => {
    const { workspace, catalog } = fixture();
    workspace.records.simulation.evaluatedRevision = null;
    workspace.records.assessment.evaluatedRevision = null;
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(true);
  });
  it('blocks ZIP traversal and duplicate file names', () => {
    expect(() => createKiCadZip([{ name: '../evil', content: '' }])).toThrow(/safe/);
    expect(() => createKiCadZip([{ name: 'a', content: '' }, { name: 'a', content: '' }])).toThrow(/unique/);
  });
});
