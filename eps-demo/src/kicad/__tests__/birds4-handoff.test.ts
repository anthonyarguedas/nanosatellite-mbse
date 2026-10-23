import { describe, expect, it } from 'vitest';
import { catalog } from '../../data/catalog';
import { applyProduct, changeInputs, createExampleWorkspace, evaluateReady } from '../../state/model';
import { nodeStatuses } from '../../workflow';
import { buildKiCadExport, getKiCadReadiness } from '../index';

function manifest(workspace: ReturnType<typeof createExampleWorkspace>) {
  const result = buildKiCadExport(workspace, catalog);
  return JSON.parse(result.files.find(file => file.name === 'manifest.json')!.content);
}

const solarId = 'azur-3g30c-advanced-81780';

describe('BIRDS-4 concept study through the logical handoff', () => {
  it('exports the evaluated example while retaining known failures and hardware evidence gaps', () => {
    const workspace = createExampleWorkspace();
    expect(Object.values(nodeStatuses(workspace)).every(status => status === 'complete')).toBe(true);
    expect(workspace.analysis.checks?.find(check => check.id === 'EPS-19')?.verdict).toBe('fail');
    for (const id of ['EPS-10', 'EPS-11']) {
      expect(workspace.analysis.checks?.find(check => check.id === id)?.verdict).toBe('unassessed');
    }
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(true);
    const output = manifest(workspace);
    expect(output.usages).toHaveLength(3);
    expect(output.usages.find((usage: { productId: string }) => usage.productId === solarId).quantity).toBe(3);
    expect(output.unallocatedRoles).toContain('software');
    expect(output.physicalRouting.status).toBe('blocked');
    expect(output.physicalRouting.boardGenerated).toBe(false);
  });

  it('keeps allocated quantities fixed when a new scenario suggests more hardware', () => {
    const original = createExampleWorkspace();
    const next = evaluateReady(changeInputs(original, inputs => {
      inputs.activeScenarioId = 'birds4-stress';
      return inputs;
    }));
    expect(next.analysis.suggestions?.find(suggestion => suggestion.productId === solarId)?.quantity).toBeGreaterThan(3);
    const output = manifest(next);
    expect(output.usages.find((usage: { productId: string }) => usage.productId === solarId).quantity).toBe(3);
    expect(next.analysis.checks?.find(check => check.id === 'EPS-11')?.verdict).toBe('fail');
    expect(next.analysis.checks?.find(check => check.id === 'EPS-19')?.verdict).toBe('fail');
  });

  it('permits a scoped logical drawing when installed pack energy is unresolved', () => {
    const workspace = evaluateReady(applyProduct(createExampleWorkspace(), 'conditioning', 'isis-iceps2-type-a'));
    expect(workspace.inputs.battery.capacityWh).toBeNull();
    expect(nodeStatuses(workspace).battery).toBe('complete');
    expect(nodeStatuses(workspace).candidates).toBe('complete');
    expect(nodeStatuses(workspace).simulation).not.toBe('complete');
    expect(workspace.analysis.battery?.requiredWh).toBeGreaterThan(0);
    expect(workspace.analysis.checks?.find(check => check.id === 'ENERGY-RESERVE')?.verdict).toBe('unassessed');
    expect(getKiCadReadiness(workspace, catalog).ready).toBe(true);
    const output = manifest(workspace);
    expect(output.usages).toHaveLength(2);
    expect(output.usages.find((usage: { productId: string }) => usage.productId === 'isis-iceps2-type-a').allocatedRoles).toEqual([
      'battery', 'conditioning', 'distribution', 'processor',
    ]);
    expect(output.physicalRouting.boardGenerated).toBe(false);
  });
});
