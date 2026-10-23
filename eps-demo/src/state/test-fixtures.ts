import { createWorkspace, evaluateReady, exampleInputs } from './model';

/** Deliberately unallocated legacy-style numerical fixture, not the fully evaluated bundled example. */
export function preliminaryWorkspace() {
  const inputs = exampleInputs();
  inputs.solar = { sunlightEfficiency: 0.85, eclipseEfficiency: 0.7, cellEolV: 2.25, cellEolA: 0.45, installedPowerW: 2 };
  inputs.battery.capacityWh = 8;
  inputs.topology.idlePowerW = 0.08;
  return evaluateReady(createWorkspace(inputs), ['mission', 'orbit', 'scenarios', 'budget', 'solar', 'battery', 'topology']);
}
export function unallocatedCurrentWorkspace() { return evaluateReady(preliminaryWorkspace()); }
