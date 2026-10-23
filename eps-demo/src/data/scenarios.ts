import type { Load, Scenario } from '../types';

export const BIRDS4_SOURCE = {
  title: 'BIRDS-4 1U CubeSat Missions and On-Orbit Results',
  authors: 'H. R. Shrestha, BIRDS-4 Project Members et al.',
  year: 2022,
  url: 'https://nanosat11th.itu.edu.tr/assets/papers/BIRDS-4.pdf',
  locations: 'Sections 2–5.6, pp. 1–5',
};
const provenance = 'BIRDS-4 activities: Shrestha et al. (2022), §§3–5.6, https://nanosat11th.itu.edu.tr/assets/papers/BIRDS-4.pdf. All mode powers, phase placements, rail assignments, illumination factors and energy criteria below are authored demo assumptions. This is a BIRDS-4-inspired study, not a reconstruction of its flight power system or operational timeline. SF-WARD is a planned activity whose on-orbit communication failure is reported in §5.3.';
function windows(...pairs: [number, number][]) { return pairs.map(([start, end], i) => ({ id: `window-${i + 1}`, start, end })); }
const routineLoads: Load[] = [
  { id: 'obc', name: 'OBC & housekeeping', subsystem: 'BIRDS bus / MainPIC', color: '#89b9cf', activePowerW: 0.18, idlePowerW: 0.12, railV: 3.3, essential: true, windows: windows([0, 1]) },
  { id: 'com', name: 'COM / CW beacon', subsystem: 'Communications', color: '#c6a1d5', activePowerW: 0.8, idlePowerW: 0.1, railV: 3.3, essential: true, windows: windows([0.08, 0.10], [0.71, 0.73]) },
  { id: 'cam', name: 'CAM imaging', subsystem: 'Mission Board 2', color: '#f1aa73', activePowerW: 1.5, idlePowerW: 0.01, railV: 5, essential: false, windows: windows([0.16, 0.19], [0.42, 0.45]) },
  { id: 'aprs', name: 'APRS / SF-WARD', subsystem: 'Mission Board 2 / planned service', color: '#88c9af', activePowerW: 1.1, idlePowerW: 0.05, railV: 5, essential: false, windows: windows([0.29, 0.34], [0.82, 0.88]) },
  { id: 'adcs', name: 'ADCS sensing', subsystem: 'Attitude demonstration', color: '#a9b8ee', activePowerW: 0.3, idlePowerW: 0.02, railV: 3.3, essential: false, windows: windows([0.39, 0.50]) },
  { id: 'actuators', name: 'Reaction wheel / MTQ', subsystem: 'Attitude demonstration', color: '#e39caa', activePowerW: 1.2, idlePowerW: 0, railV: 5, essential: false, windows: windows([0.44, 0.462]) },
  { id: 'experiments', name: 'PSC / radiation monitors', subsystem: 'Technology experiments', color: '#b5c589', activePowerW: 0.12, idlePowerW: 0.01, railV: 3.3, essential: false, windows: windows([0.12, 0.14], [0.53, 0.55]) },
];
const stressLoads = structuredClone(routineLoads).map(load => {
  const byId: Record<string, [number, number][]> = {
    com: [[0.15, 0.40], [0.72, 0.84]], cam: [[0.10, 0.85]], aprs: [[0.20, 0.90]],
    adcs: [[0.15, 0.45]], actuators: [[0.25, 0.45]], experiments: [[0.25, 0.35]],
  };
  return byId[load.id] ? { ...load, windows: windows(...byId[load.id]) } : load;
});
const survivalLoads = structuredClone(routineLoads).map(load => load.essential
  ? { ...load, windows: load.id === 'com' ? windows([0.08, 0.09]) : load.windows }
  : { ...load, activePowerW: 0, idlePowerW: 0, windows: [] });

/** Activity names are sourced. Numerical schedules and power laws are explicit illustrative assumptions. */
export const EXAMPLE_SCENARIOS: Scenario[] = [
  {
    id: 'birds4-routine', name: 'BIRDS-4 · Routine operations', kind: 'nominal', revision: 1,
    description: 'BIRDS-4-inspired housekeeping, CW beacon, camera, APRS and attitude experiments. Editable demonstration powers and duty cycles, not flight telemetry.',
    illuminationFactor: 1, initialEnergyFraction: 0.72, minimumEnergyFraction: 0.25, durationOrbits: 1,
    loads: routineLoads, provenance,
  },
  {
    id: 'birds4-stress', name: 'BIRDS-4 · Overlapping missions', kind: 'nominal', revision: 1,
    description: 'A hypothetical two-orbit stress case. Extended camera, APRS and actuator operation coincide. With the illustrative default COTS allocation, generation and replenishment fail even though the oversized pack avoids depletion during this interval. Not a historical BIRDS-4 schedule.',
    illuminationFactor: 1, initialEnergyFraction: 0.72, minimumEnergyFraction: 0.35, durationOrbits: 2,
    loads: stressLoads, provenance,
  },
  {
    id: 'birds4-survival', name: 'BIRDS-4 · Reduced generation', kind: 'survival', revision: 1,
    description: 'A three-orbit illustrative survival interval inspired by the reported BIRDS-4 generation shortfall. Only housekeeping and a short CW beacon remain scheduled. No automatic recovery is modeled.',
    illuminationFactor: 0.15, initialEnergyFraction: 0.6, minimumEnergyFraction: 0.25, durationOrbits: 3,
    loads: survivalLoads, provenance,
  },
];
