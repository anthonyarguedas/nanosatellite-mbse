import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import legacy from './__fixtures__/pre-enrichment-authored.json';
import { applyProduct, changeInputs, createExampleWorkspace, evaluateReady } from './model';
import { catalogProvenance, provenanceIssues } from './provenance';
import { restoreWorkspace, serializeWorkspace } from './serialization';
import { nodeStatuses } from '../workflow';
import { getAllocationQuantity } from '../engine/allocations';

const solar = ['azur-3g30c-advanced-81780', 'azur-4g32c-advanced-82921', 'azur-3g30c-advanced-hp-82645'];
const batteries = ['saft-mp144350xlr-cell', 'saft-mp174865xlr-cell', 'saft-mp176065xlr-cell'];
const get = (id: string) => catalog.products.find(p => p.id === id)!;

describe('real enriched choices with provenance and explicit assembly limits', () => {
  it.each(solar)('allocates the actual sourced cell %s without adopting an array model', id => {
    const initial = createExampleWorkspace(); const p = get(id);
    const next = applyProduct(initial, 'solar', id);
    expect(next.inputs.solar.cellEolV).toBe(p.specs.vmpEolV.value);
    expect(next.inputs.solar.cellEolA).toBe(p.specs.impEolA.value);
    expect(provenanceIssues(next.inputs, next.provenance!, next.selections, catalog)).toEqual([]);
    expect(next.provenance!.find(x => x.parameter === 'solar.cellEolV')).toMatchObject({ kind: 'catalog-value', productId: id, conditions: p.specs.vmpEolV.conditions });
    if (id !== initial.selections.solar) expect(next.inputs.solar.installedPowerW).toBeNull();
    expect(Number.isSafeInteger(getAllocationQuantity(next, id))).toBe(true);
  });
  it.each(batteries)('allocates the one-cell nominal reference %s with no aging or efficiency upgrade', id => {
    const initial = createExampleWorkspace(); const p = get(id);
    const next = applyProduct(initial, 'battery', id);
    expect(getAllocationQuantity(next, id)).toBe(1);
    expect(next.inputs.battery.capacityWh).toBe(p.specs.energyWh.value);
    expect(next.provenance!.find(x => x.parameter === 'battery.capacityWh')).toMatchObject({ kind: 'catalog-value', productId: id, conditions: p.specs.energyWh.conditions });
    expect(next.provenance!.find(x => x.parameter === 'battery.capacityWh')!.rationale).toMatch(/One-cell reference/);
    for (const parameter of ['battery.retainedEnergy', 'battery.chargeEfficiency', 'battery.dischargeEfficiency', 'battery.maxChargeW', 'battery.maxDischargeW'] as const) expect(next.provenance!.find(x => x.parameter === parameter)?.kind).not.toBe('catalog-value');
    expect(next.inputs.battery.retainedEnergy).toBe(initial.inputs.battery.retainedEnergy);
    expect(provenanceIssues(next.inputs, next.provenance!, next.selections, catalog)).toEqual([]);
  });
  it('keeps a multi-cell count separate from installed pack energy and rejects forged transfer provenance', () => {
    const initial = evaluateReady(changeInputs(createExampleWorkspace(), inputs => {
      inputs.scenarios[0].loads.forEach(load => { load.activePowerW = 100; load.idlePowerW = 100; }); return inputs;
    }));
    const id = batteries[0];
    const next = applyProduct(initial, 'battery', id);
    expect(getAllocationQuantity(next, id)).toBeGreaterThan(1);
    expect(next.inputs.battery.capacityWh).toBeNull();
    expect(next.provenance!.some(x => x.parameter === 'battery.capacityWh')).toBe(false);
    expect(nodeStatuses(next).simulation).not.toBe('ready');
    const forged = JSON.parse(serializeWorkspace(next, catalog.revision));
    forged.inputs.battery.capacityWh = get(id).specs.energyWh.value;
    forged.provenance.push(catalogProvenance(get(id), 'battery.capacityWh'));
    expect(() => restoreWorkspace(forged)).toThrow(/multi-cell count/);
  });
  it('allocates a documented load regulator without treating array power as its input or claiming MPPT', () => {
    const next = applyProduct(createExampleWorkspace(), 'conditioning', 'pololu-2843-d24v5f5');
    const suggestion = next.analysis.suggestions!.find(x => x.productId === 'pololu-2843-d24v5f5')!;
    expect(suggestion.outcome).toBe('incomplete');
    expect(suggestion.checks.every(c => c.verdict === 'unassessed')).toBe(true);
    expect(suggestion.checks.map(c => c.id)).not.toContain('CATALOG-INPUT-POWER');
    expect(next.inputs.topology.efficiency).toBe(.9);
    expect(next.selections.processor).toBeUndefined();
    expect(next.selections.distribution).toBeUndefined();
  });
  it('keeps published BIRDS assembly context outside selectable hardware', () => {
    const workspace = createExampleWorkspace(); const id = 'birds-bk3mcce-3s2p-published-assembly';
    expect(workspace.analysis.suggestions!.some(x => x.productId === id)).toBe(false);
    expect(() => applyProduct(workspace, 'battery', id)).toThrow(/reference context/);
  });
});

describe('actual parent pre-enrichment export restoration', () => {
  it('preserves every authored decision on local reload without snapshots or fallback', () => {
    expect(legacy.allocations.every(r => !Object.hasOwn(r, 'productSnapshot'))).toBe(true);
    expect(() => restoreWorkspace(legacy)).toThrow(/mismatched/);
    const restored = restoreWorkspace(legacy, catalog, true);
    expect(restored.inputs).toEqual(legacy.inputs);
    expect(restored.selections).toEqual(legacy.selections);
    expect(restored.allocations).toEqual(legacy.allocations);
    expect(restored.provenance).toEqual(legacy.provenance);
    expect(restored.analysis).toEqual({});
    expect(restored.catalogReview!.length).toBeGreaterThan(0);
    expect(nodeStatuses(evaluateReady(restored)).simulation).toBe('locked');
  });
  it('keeps changed facts historical and permits explicit current reallocation to resolve review', () => {
    const changed = structuredClone(catalog);
    changed.products.find(p => p.id === legacy.selections.battery)!.specs.energyWh.value = 85;
    const historical = restoreWorkspace(legacy, changed, true);
    expect(historical.inputs.battery.capacityWh).toBe(86);
    expect(historical.provenance).toEqual(legacy.provenance);
    expect(historical.catalogReview!.join(' ')).toMatch(/catalog provenance/);
    let current = evaluateReady(restoreWorkspace(legacy, catalog, true));
    for (const receipt of legacy.allocations) current = evaluateReady(applyProduct(current, receipt.roles[0] as 'solar' | 'battery' | 'conditioning', receipt.productId));
    expect(current.catalogReview).toEqual([]);
    expect(current.allocations!.every(r => r.catalogRevision === catalog.revision && r.productSnapshot)).toBe(true);
    expect(current.inputs).toEqual(legacy.inputs);
    expect(nodeStatuses(current).simulation).toBe('complete');
    expect(current.analysis.checks!.find(c => c.id === 'EPS-19')!.verdict).toBe('fail');
  });
});
