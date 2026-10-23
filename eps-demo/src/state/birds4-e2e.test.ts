import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { BIRDS4_EXAMPLE_BASIS } from '../data/birds4';
import { getAllocationQuantity } from '../engine';
import { getKiCadReadiness } from '../kicad';
import { descendants, missingForNodes, NODE_DEFINITIONS, nodeStatuses } from '../workflow';
import type { Workspace } from '../types';
import { applyProduct, changeInputs, createExampleWorkspace, createWorkspace, evaluateNode, evaluateReady, exampleInputs } from './model';
import { parseWorkspace, restoreWorkspace, serializeWorkspace } from './serialization';
import { provenanceIssues } from './provenance';
import { preliminaryWorkspace } from './test-fixtures';

const azur = 'azur-3g30c-advanced-81780';
const bp8 = 'gomspace-bp8-100wh-8s1p';
const p80 = 'gomspace-p80-config1';
const integrated = 'isis-iceps2-type-a';
const check = (workspace: Workspace, id: string) => workspace.analysis.checks!.find(item => item.id === id)!;
const numeric = (workspace: Workspace, parameter: string) => workspace.provenance!.find(item => item.parameter === parameter)!;

describe('BIRDS-4 concept → sizing → illustrative allocations → energy → review → logical handoff', () => {
  it('opens with every node evaluated, explicit substitutions and preserved evidence gaps', () => {
    const w = createExampleWorkspace();
    expect(Object.values(nodeStatuses(w)).every(status => status === 'complete')).toBe(true);
    expect(w.inputs.mission.conOps).toMatch(/SF-WARD flight exchange failed/);
    expect(w.inputs.mission.conOps).toMatch(/not BIRDS-4 flight hardware/);
    expect(BIRDS4_EXAMPLE_BASIS.source.url).toContain('BIRDS-4.pdf');
    expect(w.inputs.scenarios).toHaveLength(3);
    expect(w.allocations).toHaveLength(3);
    expect(getAllocationQuantity(w, azur)).toBe(3);
    expect(getAllocationQuantity(w, bp8)).toBe(1);
    expect(getAllocationQuantity(w, p80)).toBe(1);
    expect(w.allocations!.find(item => item.productId === p80)!.roles).toEqual(['conditioning', 'distribution', 'processor']);
    expect(w.allocations!.every(item => item.origin === 'bundled-example')).toBe(true);
    expect(w.selections.software).toBeUndefined();
    expect(provenanceIssues(w.inputs, w.provenance!, w.selections, catalog)).toEqual([]);
    expect(numeric(w, 'battery.capacityWh')).toMatchObject({ value: 86, kind: 'catalog-value', productId: bp8 });
    expect(numeric(w, 'battery.retainedEnergy')).toMatchObject({ value: 0.8, kind: 'engineering-assumption' });
    expect(numeric(w, 'topology.idlePowerW')).toMatchObject({ value: 1.41, kind: 'engineering-assumption' });
    expect(numeric(w, 'topology.idlePowerW').conditions).toMatch(/heaters off/);
    expect(numeric(w, 'solar.installedPowerW').kind).toBe('engineering-assumption');
    expect(w.analysis.orbit!.periodS).toBeCloseTo(5553.452008434545, 9);
    expect(w.analysis.budget!.additionalEpsPowerW).toBe(1.41);
    expect(w.analysis.budget!.totalWh).toBeCloseTo(3.200176719860407, 12);
    expect(w.analysis.budget!.averageW).toBeCloseTo(2.0745, 12);
    expect(w.analysis.budget!.peakW).toBeCloseTo(4.75, 12);
    expect(w.analysis.solar!.minimumPowerW).toBeCloseTo(4.320455986722694, 12);
    expect(w.analysis.solar!.cellCount).toBe(3);
    expect(w.analysis.battery!.requiredWh).toBeCloseTo(4.759773155514013, 12);
    expect(w.analysis.battery!.cycles).toBeCloseTo(5682.519620601841, 9);
    expect(w.analysis.simulation!.capacityWh).toBe(68.8);
    expect(w.analysis.simulation!.endEnergyWh).toBeCloseTo(50.88480239724659, 10);
    expect(w.analysis.simulation!.closureWh).toBeCloseTo(1.348802397246594, 10);
    expect(w.analysis.simulation!.shortageWh).toBe(0);
    expect(check(w, 'ENERGY-RESERVE').verdict).toBe('pass');
    expect(check(w, 'ENERGY-CLOSURE').verdict).toBe('pass');
    for (const id of ['EPS-09', 'EPS-10', 'EPS-11', 'EPS-14', 'EPS-20']) expect(check(w, id).verdict).toBe('unassessed');
    expect(check(w, 'EPS-19').verdict).toBe('fail');
    expect(check(w, 'KNOWN-MASS').detail).toContain('subtotal 0.86240000 kg');
    expect(w.analysis.suggestions!.filter(item => Object.values(w.selections).includes(item.productId)).every(item => item.outcome === 'incomplete')).toBe(true);
    // Readiness, not old exporter quantity inference: a logical review is possible, never physical routing.
    const readiness = getKiCadReadiness(w, catalog);
    expect(readiness.ready).toBe(true);
    expect(readiness.physicalRouting).toBe('blocked');
    expect(readiness.physicalGates).toHaveLength(6);
  });

  it('recomputes scenarios without resizing frozen allocations or concealing known failures', () => {
    const original = createExampleWorkspace();
    const edited = changeInputs(original, inputs => { inputs.activeScenarioId = 'birds4-stress'; return inputs; });
    expect(nodeStatuses(edited).assessment).toBe('stale');
    expect(edited.analysis.simulation).toEqual(original.analysis.simulation);
    const stress = evaluateReady(edited);
    expect(stress.analysis.suggestions!.find(item => item.productId === azur)!.quantity).toBe(5);
    expect(getAllocationQuantity(stress, azur)).toBe(3);
    expect(stress.allocations).toEqual(original.allocations);
    expect(stress.inputs.solar.installedPowerW).toBe(6.45354);
    expect(stress.analysis.simulation!.closureWh).toBeCloseTo(-2.7989260497981476, 10);
    for (const id of ['EPS-02', 'EPS-11', 'EPS-19']) expect(check(stress, id).verdict).toBe('fail');
    expect(check(stress, 'KNOWN-MASS').detail).toContain('subtotal 0.86240000 kg');
    const applied = applyProduct(stress, 'solar', azur);
    expect(getAllocationQuantity(applied, azur)).toBe(5);
    expect(applied.inputs.solar.installedPowerW).toBe(6.45354); // Apply does not invent improved illumination.
    expect(nodeStatuses(applied).assessment).toBe('stale');
    const survival = evaluateReady(changeInputs(original, inputs => { inputs.activeScenarioId = 'birds4-survival'; return inputs; }));
    expect(survival.analysis.simulation!.endEnergyWh).toBeCloseTo(35.60165965469135, 10);
    expect(check(survival, 'EPS-02').verdict).toBe('fail');
    expect(check(survival, 'EPS-12').verdict).toBe('unassessed');
    expect(check(survival, 'ENERGY-CLOSURE').verdict).toBe('unassessed');
    expect(getAllocationQuantity(survival, azur)).toBe(3);
  });

  it('unknown integrated-pack energy permits sizing, fresh suggestions, partial review, handoff and replacement', () => {
    const original = createExampleWorkspace();
    const withIntegrated = evaluateReady(applyProduct(original, 'conditioning', integrated));
    expect(withIntegrated.inputs.battery.capacityWh).toBeNull();
    expect(withIntegrated.analysis.battery!.requiredWh).toBeCloseTo(original.analysis.battery!.requiredWh, 12);
    expect(withIntegrated.analysis.battery!.eolCapacityWh).toBeNull();
    for (const id of ['battery', 'topology', 'candidates', 'assessment'] as const) expect(nodeStatuses(withIntegrated)[id]).toBe('complete');
    expect(nodeStatuses(withIntegrated).simulation).toBe('stale');
    expect(missingForNodes(withIntegrated).simulation.join(' ')).toMatch(/capacity/);
    expect(withIntegrated.analysis.simulation).toEqual(original.analysis.simulation); // visible history only
    expect(check(withIntegrated, 'ENERGY-RESERVE').verdict).toBe('unassessed');
    expect(check(withIntegrated, 'BATTERY-CAPACITY').verdict).toBe('unassessed');
    expect(withIntegrated.provenance!.some(item => item.parameter === 'battery.capacityWh')).toBe(false);
    expect(withIntegrated.allocations!.map(item => item.productId).sort()).toEqual([azur, integrated].sort());
    expect(withIntegrated.allocations!.find(item => item.productId === integrated)!.roles).toHaveLength(4);
    expect(getKiCadReadiness(withIntegrated, catalog).ready).toBe(true);
    const external = evaluateReady(applyProduct(withIntegrated, 'conditioning', p80));
    expect(external.selections.battery).toBeUndefined();
    expect(external.inputs.battery.capacityWh).toBeNull();
    const replaced = evaluateReady(applyProduct(external, 'battery', bp8));
    expect(nodeStatuses(replaced).simulation).toBe('complete');
    expect(replaced.allocations!.some(item => item.productId === integrated)).toBe(false);
    expect(numeric(replaced, 'battery.capacityWh')).toMatchObject({ kind: 'catalog-value', productId: bp8, value: 86 });
  });

  it('manual missing-pack capacity is persisted as an assumption, never a repaired catalog rating', () => {
    const allocated = evaluateReady(applyProduct(createExampleWorkspace(), 'conditioning', integrated));
    const authored = changeInputs(allocated, inputs => { inputs.battery.capacityWh = 8; return inputs; });
    const evaluated = evaluateReady(authored);
    expect(numeric(evaluated, 'battery.capacityWh')).toMatchObject({ kind: 'engineering-assumption', value: 8, sourceIds: [] });
    expect(catalog.products.find(item => item.id === integrated)!.specs.energyWh.status).toBe('missing');
    expect(evaluated.analysis.suggestions!.find(item => item.productId === integrated && item.role === 'battery')!.outcome).toBe('incomplete');
    expect(check(evaluated, 'EPS-08').verdict).toBe('unassessed');
    const parsed = parseWorkspace(JSON.parse(serializeWorkspace(evaluated, catalog.revision)));
    expect(parsed.provenance).toEqual(evaluated.provenance);
  });

  it('new simulation evidence invalidates a partial assessment without requiring an input change', () => {
    const partial = evaluateReady(preliminaryWorkspace(), NODE_DEFINITIONS.map(node => node.id).filter(id => id !== 'simulation'));
    expect(nodeStatuses(partial).simulation).toBe('ready');
    expect(nodeStatuses(partial).assessment).toBe('complete');
    expect(check(partial, 'ENERGY-RESERVE').verdict).toBe('unassessed');
    const simulated = evaluateNode(partial, 'simulation');
    expect(nodeStatuses(simulated).assessment).toBe('stale');
    expect(simulated.inputs).toEqual(partial.inputs);
    expect(descendants('simulation')).toEqual(['simulation', 'assessment']);
    const assessed = evaluateNode(simulated, 'assessment');
    expect(check(assessed, 'ENERGY-RESERVE').verdict).toBe('pass');
  });

  it('idle edits invalidate budget and sizing without a cycle, and EPS demand is counted once', () => {
    const original = createExampleWorkspace();
    const changed = changeInputs(original, inputs => { inputs.topology.idlePowerW = 1.61; return inputs; });
    expect(nodeStatuses(changed).orbit).toBe('complete');
    for (const id of ['budget', 'solar', 'battery', 'topology', 'candidates', 'simulation', 'assessment'] as const) expect(nodeStatuses(changed)[id]).toBe('stale');
    const next = evaluateReady(changed);
    const orbit = original.analysis.orbit!;
    expect(next.analysis.budget!.totalWh - original.analysis.budget!.totalWh).toBeCloseTo(0.2 * orbit.periodS / 3600, 12);
    expect(next.analysis.battery!.requiredWh - original.analysis.battery!.requiredWh).toBeCloseTo(0.2 * orbit.eclipseS / 3600 / 0.3 * 1.2, 12);
    expect(next.analysis.solar!.minimumPowerW - original.analysis.solar!.minimumPowerW).toBeCloseTo(0.2 * (orbit.sunlightS / 0.85 + orbit.eclipseS / 0.7) / orbit.sunlightS, 12);
    expect(next.analysis.simulation!.points[0].demandW - original.analysis.simulation!.points[0].demandW).toBeCloseTo(0.2, 12);
    expect(Object.values(nodeStatuses(next)).every(status => status === 'complete')).toBe(true);
    const missing = exampleInputs(); missing.topology.idlePowerW = null;
    const uncomputed = evaluateReady(createWorkspace(missing));
    expect(nodeStatuses(uncomputed).budget).toBe('locked');
    expect(uncomputed.analysis.budget).toBeUndefined();
    expect(missingForNodes(uncomputed).budget.join(' ')).toMatch(/EPS baseline/);
    const prior = new Set<string>();
    for (const node of NODE_DEFINITIONS) {
      expect([...node.dependencies, ...node.evidenceDependencies ?? []].every(id => prior.has(id))).toBe(true);
      prior.add(node.id);
    }
  });

  it('restores authored inputs and receipts, discards caches and waits for explicit recalculation', () => {
    const original = createExampleWorkspace();
    const raw = JSON.parse(serializeWorkspace(original, catalog.revision));
    raw.analysis.simulation.capacityWh = 999999;
    const restored = restoreWorkspace(raw);
    expect(restored.inputs).toEqual(original.inputs);
    expect(restored.allocations).toEqual(original.allocations);
    expect(restored.provenance).toEqual(original.provenance);
    expect(restored.analysis).toEqual({});
    expect(Object.values(restored.records).every(record => record.evaluatedRevision === null)).toBe(true);
    const recalculated = evaluateReady(restored);
    expect(recalculated.analysis).toEqual(original.analysis);
    expect(recalculated.analysis.simulation!.capacityWh).toBe(68.8);
    expect(check(recalculated, 'EPS-19').verdict).toBe('fail');
    raw.inputs.topology.conditioning = 'DET';
    const validButUnsupported = restoreWorkspace(raw);
    expect(validButUnsupported.inputs.topology.conditioning).toBe('DET');
    expect(validButUnsupported.analysis).toEqual({});
    expect(nodeStatuses(validButUnsupported).simulation).toBe('locked');
  });

  it('imports legacy selections without manufacturing quantity/provenance, even with old cached suggestions', () => {
    const raw = JSON.parse(serializeWorkspace(createExampleWorkspace(), catalog.revision));
    delete raw.allocations; delete raw.provenance;
    const restored = restoreWorkspace(raw);
    expect(restored.allocations).toBeUndefined();
    expect(restored.provenance).toBeUndefined();
    expect(getAllocationQuantity(restored, azur)).toBeNull();
    const evaluated = evaluateReady(restored);
    expect(check(evaluated, 'KNOWN-MASS').verdict).toBe('unassessed');
    expect(check(evaluated, 'KNOWN-MASS').detail).toMatch(/frozen allocation quantity missing/);
    const applied = applyProduct(evaluated, 'solar', azur);
    expect(getAllocationQuantity(applied, azur)).toBe(3);
    expect(getAllocationQuantity(applied, bp8)).toBeNull();
  });

  it.each(['capacity', 'mass', 'source'] as const)('keeps independent calculations when invalid %s input blocks its consumers', field => {
    const original = createExampleWorkspace();
    const edited = changeInputs(original, inputs => {
      if (field === 'capacity') inputs.battery.capacityWh = -1;
      if (field === 'mass') inputs.topology.massAllocationKg = -1;
      if (field === 'source') inputs.solar.installedPowerW = -1;
      return inputs;
    });
    expect(() => evaluateReady(edited)).not.toThrow();
    const next = evaluateReady(edited);
    expect(nodeStatuses(next).solar).toBe('complete');
    expect(nodeStatuses(next).battery).toBe('complete');
    expect(nodeStatuses(next).assessment).not.toBe('complete');
    expect(missingForNodes(next).assessment.join(' ')).toMatch(/must be/);
    expect(next.analysis.battery!.requiredWh).toBe(original.analysis.battery!.requiredWh);
    if (field === 'source') expect(nodeStatuses(next).candidates).not.toBe('complete');
    else expect(nodeStatuses(next).candidates).toBe('complete');
  });

  it.each(['duplicate', 'quantity', 'roles', 'product', 'revision', 'provenance-value', 'provenance-source', 'assumption-source', 'false-catalog-assumption'])('rejects corrupted %s metadata without accepting calculation caches', mutation => {
    const raw = JSON.parse(serializeWorkspace(createExampleWorkspace(), catalog.revision));
    if (mutation === 'duplicate') raw.allocations.push(raw.allocations[0]);
    if (mutation === 'quantity') raw.allocations.find((item: { productId: string }) => item.productId === bp8).quantity = 2;
    if (mutation === 'roles') raw.allocations[0].roles = ['battery'];
    if (mutation === 'product') raw.allocations[0].productId = 'absent';
    if (mutation === 'revision') raw.allocations[0].productRevision = 'other revision';
    if (mutation === 'provenance-value') raw.provenance[0].value += 1;
    if (mutation === 'provenance-source') raw.provenance.find((item: { parameter: string }) => item.parameter === 'battery.capacityWh').sourceIds = ['invented-source'];
    if (mutation === 'assumption-source') raw.provenance.find((item: { parameter: string }) => item.parameter === 'topology.idlePowerW').sourceIds = ['invented-source'];
    if (mutation === 'false-catalog-assumption') raw.provenance.find((item: { parameter: string }) => item.parameter === 'battery.retainedEnergy').kind = 'catalog-value';
    expect(() => restoreWorkspace(raw)).toThrow();
  });
});
