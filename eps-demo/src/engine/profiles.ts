import type { OrbitResult, Scenario } from '../types';

/** All changes in a piecewise constant profile. No sampling-based duty estimate. */
export function phaseEvents(scenario: Scenario, orbit: OrbitResult): number[] {
  const events = new Set([0, 1, orbit.sunlightFraction]);
  for (const load of scenario.loads) {
    for (const window of load.windows) {
      if (window.start < window.end) {
        events.add(window.start);
        events.add(window.end);
      }
    }
  }
  return [...events].sort((a, b) => a - b);
}

/** Active replaces idle. Membership in the union prevents overlap double counting. */
export function demandAtPhase(scenario: Scenario, phase: number): number {
  let power = 0;
  for (const load of scenario.loads) {
    const active = load.windows.some(window => phase >= window.start && phase < window.end);
    power += active ? load.activePowerW : load.idlePowerW;
  }
  return power;
}
