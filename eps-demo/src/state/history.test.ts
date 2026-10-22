import { describe, expect, it } from 'vitest';
import { changeInputs, createExampleWorkspace, evaluateNode, evaluateReady } from './model';
import { nodeStatuses } from '../workflow';

 describe('historical plot context', () => {
  it('keeps the original budget timing after only the upstream orbit is recomputed', () => {
    const original = evaluateReady(createExampleWorkspace());
    const oldPeriod = original.analysis.orbit!.periodS;
    const changed = changeInputs(original, inputs => { inputs.mission.altitudeKm = 700; return inputs; });
    const next = evaluateNode(evaluateNode(changed, 'mission'), 'orbit');
    expect(nodeStatuses(next).budget).toBe('stale');
    expect(next.analysis.orbit!.periodS).not.toBe(oldPeriod);
    expect(next.analysis.budget!.orbitPeriodS).toBe(oldPeriod);
    expect(next.analysis.budget!.sunlightFraction).toBe(original.analysis.orbit!.sunlightFraction);
  });
  it('retains the evaluated reserve instead of relabeling an old energy curve with an edited criterion', () => {
    const original = evaluateReady(createExampleWorkspace());
    const oldSimulation = original.analysis.simulation!;
    expect(oldSimulation.reserveWh).toBeCloseTo(1.6);
    const changed = changeInputs(original, inputs => {
      inputs.scenarios[0].minimumEnergyFraction = 0.5;
      inputs.scenarios[0].revision += 1;
      return inputs;
    });
    expect(nodeStatuses(changed).simulation).toBe('stale');
    expect(changed.analysis.simulation!.reserveWh).toBeCloseTo(1.6);
    expect(changed.analysis.simulation!.scenarioRevision).toBe(1);
    const next = evaluateReady(changed);
    expect(next.analysis.simulation!.reserveWh).toBeCloseTo(3.2);
    expect(next.analysis.simulation!.scenarioRevision).toBe(2);
    expect(next.analysis.simulation!.durationS).toBe(next.analysis.orbit!.periodS);
  });
});
