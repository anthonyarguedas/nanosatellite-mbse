import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { nodeStatuses } from '../workflow';
import { applyProduct, changeInputs, evaluateReady } from './model';
import { preliminaryWorkspace, unallocatedCurrentWorkspace } from './test-fixtures';

const current = unallocatedCurrentWorkspace;
const azur = 'azur-3g30c-advanced-81780';
const cesi = 'cesi-ctj30-26p5';
const bp8 = 'gomspace-bp8-100wh-8s1p';
const p80 = 'gomspace-p80-config1';
const integrated = 'isis-iceps2-type-a';

 describe('explicit COTS allocation and replacement', () => {
  it('blocks application before screening and after upstream changes', () => {
    expect(() => applyProduct(preliminaryWorkspace(), 'solar', azur)).toThrow(/stale or missing/);
    const stale = changeInputs(current(), inputs => { inputs.mission.altitudeKm = 450; return inputs; });
    expect(() => applyProduct(stale, 'solar', azur)).toThrow(/stale or missing/);
  });
  it('uses the exact sourced irradiated pair and invalidates dependent outputs', () => {
    const original = current();
    const next = applyProduct(original, 'solar', azur);
    expect(next.inputs.solar.cellEolV).toBe(2.22);
    expect(next.inputs.solar.cellEolA).toBe(0.969);
    expect(next.selections.solar).toBe(azur);
    expect(nodeStatuses(next).solar).toBe('stale');
    expect(nodeStatuses(next).assessment).toBe('stale');
    expect(nodeStatuses(next).orbit).toBe('complete');
    expect(original.inputs.solar.cellEolV).toBe(2.25);
  });
  it('does not carry a previous cell EOL rating into a replacement with missing EOL data', () => {
    const withAzur = evaluateReady(applyProduct(current(), 'solar', azur));
    const next = applyProduct(withAzur, 'solar', cesi);
    expect(next.inputs.solar.cellEolV).toBeNull();
    expect(next.inputs.solar.cellEolA).toBeNull();
    expect(next.selections.solar).toBe(cesi);
    const refreshed = evaluateReady(next);
    expect(nodeStatuses(refreshed).candidates).toBe('complete');
    expect(refreshed.analysis.solar!.cellCount).toBeNull();
    expect(refreshed.analysis.solar!.minimumPowerW).toBeGreaterThan(0);
  });
  it('keeps a finished pack rating fixed and a missing integrated-pack rating missing', () => {
    const withPack = applyProduct(current(), 'battery', bp8);
    expect(withPack.inputs.battery.capacityWh).toBe(86);
    const withIntegrated = applyProduct(evaluateReady(withPack), 'conditioning', integrated);
    expect(withIntegrated.inputs.battery.capacityWh).toBeNull();
    expect(withIntegrated.selections.battery).toBe(integrated);
    expect(withIntegrated.selections.conditioning).toBe(integrated);
    expect(withIntegrated.selections.distribution).toBe(integrated);
    expect(withIntegrated.selections.processor).toBe(integrated);
    expect(withIntegrated.selections.software).toBeUndefined();
    expect(new Set(Object.values(withIntegrated.selections))).toEqual(new Set([integrated]));
  });
  it('does not allocate a separate pack over the fixed internal battery of the selected EPS', () => {
    const allocated = applyProduct(current(), 'conditioning', integrated);
    const withAssumption = changeInputs(allocated, inputs => { inputs.battery.capacityWh = 8; return inputs; });
    const refreshed = evaluateReady(withAssumption);
    expect(() => applyProduct(refreshed, 'battery', bp8)).toThrow(/fixed battery/);
    const replacement = applyProduct(refreshed, 'conditioning', p80);
    expect(replacement.selections.battery).toBeUndefined();
    expect(applyProduct(evaluateReady(replacement), 'battery', bp8).selections.battery).toBe(bp8);
  });
  it('preserves one sourced physical board across its documented logical roles', () => {
    const next = applyProduct(current(), 'conditioning', p80);
    const board = catalog.products.find(product => product.id === p80)!;
    expect(Object.keys(next.selections).sort()).toEqual([...board.roles].sort());
    expect(new Set(Object.values(next.selections)).size).toBe(1);
    expect(nodeStatuses(next).candidates).toBe('complete');
    expect(nodeStatuses(next).simulation).toBe('stale');
    expect(nodeStatuses(next).assessment).toBe('stale');
  });
  it('blocks missing products, unsupported roles and known rejected suggestions', () => {
    const workspace = current();
    expect(() => applyProduct(workspace, 'solar', 'unknown')).toThrow(/absent/);
    expect(() => applyProduct(workspace, 'software', p80)).toThrow(/does not provide/);
    const rejected = structuredClone(workspace);
    rejected.analysis.suggestions!.find(item => item.productId === azur)!.outcome = 'rejected';
    expect(() => applyProduct(rejected, 'solar', azur)).toThrow(/known violation/);
  });
});
