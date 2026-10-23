import { describe, expect, it } from 'vitest';
import { simulateOrbit } from './engine';
import { descendants, inputIssues, missingForNodes, NODE_DEFINITIONS, nodeStatuses } from './workflow';
import { changeInputs, createExampleWorkspace, createWorkspace, emptyInputs, evaluateNode, evaluateReady } from './state/model';
import { preliminaryWorkspace } from './state/test-fixtures';

 describe('revisioned dependency graph', () => {
  it('starts a blank design with explicit missing-input explanations', () => {
    const workspace = createWorkspace(emptyInputs());
    const states = nodeStatuses(workspace);
    expect(Object.values(states).every(status => status === 'locked')).toBe(true);
    expect(missingForNodes(workspace).mission.join(' ')).toContain('altitude');
    expect(missingForNodes(workspace).budget.join(' ')).toContain('Orbit geometry');
  });
  it('unlocks catalog screening after the example preliminary nodes are evaluated', () => {
    const workspace = preliminaryWorkspace();
    expect(nodeStatuses(workspace).candidates).toBe('ready');
    expect(nodeStatuses(workspace).simulation).toBe('locked');
    expect(nodeStatuses(workspace).solar).toBe('complete');
  });
  it('marks every downstream result stale on altitude edits and keeps the old result as history', () => {
    const original = evaluateReady(createExampleWorkspace());
    const updated = changeInputs(original, inputs => ({ ...inputs, mission: { ...inputs.mission, altitudeKm: 650 } }));
    expect(nodeStatuses(updated).orbit).toBe('stale');
    expect(nodeStatuses(updated).assessment).toBe('stale');
    expect(nodeStatuses(updated).scenarios).toBe('complete');
    expect(updated.analysis.orbit).toEqual(original.analysis.orbit);
    expect(() => evaluateNode(updated, 'simulation')).toThrow(/Evaluate it first/);
    const reevaluated = evaluateReady(updated);
    expect(NODE_DEFINITIONS.every(node => nodeStatuses(reevaluated)[node.id] === 'complete')).toBe(true);
    expect(reevaluated.analysis.orbit!.periodS).toBeGreaterThan(original.analysis.orbit!.periodS);
  });
  it('invalidates only the scenario dependency closure after a window changes', () => {
    const original = evaluateReady(createExampleWorkspace());
    const updated = changeInputs(original, inputs => {
      inputs.scenarios[0].loads[0].activePowerW += 0.1;
      return inputs;
    });
    expect(nodeStatuses(updated).orbit).toBe('complete');
    expect(nodeStatuses(updated).budget).toBe('stale');
    expect(nodeStatuses(updated).candidates).toBe('stale');
    expect(nodeStatuses(original).budget).toBe('complete');
  });
  it('null inputs lock new outputs and leave computed ones visibly stale', () => {
    const original = preliminaryWorkspace();
    const updated = changeInputs(original, inputs => { inputs.solar.sunlightEfficiency = null; return inputs; });
    expect(nodeStatuses(updated).solar).toBe('stale');
    expect(nodeStatuses(updated).candidates).toBe('locked');
    expect(missingForNodes(updated).solar[0]).toContain('Xs');
    expect(() => evaluateNode(updated, 'solar')).toThrow();
  });
  it('does not invalidate a no-op input update', () => {
    const original = createExampleWorkspace();
    expect(changeInputs(original, inputs => inputs)).toBe(original);
  });
  it('bounds demo run duration and rejects uncharacterized DET propagation', () => {
    const inputs = createExampleWorkspace().inputs;
    inputs.scenarios[0].durationOrbits = 11;
    expect(inputIssues('scenarios', inputs).join(' ')).toContain('10');
    inputs.topology.conditioning = 'DET';
    expect(inputIssues('simulation', inputs).join(' ')).toContain('I–V');
  });
  it('also rejects unsupported DET at the pure engine boundary', () => {
    const workspace = createExampleWorkspace();
    workspace.inputs.topology.conditioning = 'DET';
    expect(() => simulateOrbit(workspace.inputs, workspace.inputs.scenarios[0], workspace.analysis.orbit!)).toThrow(/DET/);
  });
  it('treats zero source power as a valid negative control rather than missing data', () => {
    const workspace = createExampleWorkspace();
    workspace.inputs.solar.installedPowerW = 0;
    expect(inputIssues('simulation', workspace.inputs)).toEqual([]);
    const result = simulateOrbit(workspace.inputs, workspace.inputs.scenarios[0], workspace.analysis.orbit!);
    expect(result.checks.find(check => check.id === 'EPS-11')?.verdict).toBe('fail');
  });
  it('keeps the DAG acyclic and explicitly closes affected nodes', () => {
    const prior = new Set<string>();
    for (const node of NODE_DEFINITIONS) {
      expect(node.dependencies.every(id => prior.has(id))).toBe(true);
      prior.add(node.id);
    }
    expect(descendants('battery')).toEqual(['battery', 'topology', 'candidates', 'simulation', 'assessment']);
    expect(descendants('assessment')).toEqual(['assessment']);
  });
});
