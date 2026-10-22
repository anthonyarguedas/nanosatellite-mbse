import type { Scenario } from '../types';

const PROVENANCE = 'Synthetic, authored demonstration assumptions for Orbitwork. Powers, rail voltages, schedules, illumination and energy criteria are editable examples, not sourced mission evidence or flight hardware ratings. The illustrative comparison uses 12 W installed source power and a 20 Wh battery; actual outcomes depend on the workspace inputs.';

/** Data only. No thermal, charge-state, protection, load-shedding or recovery model is implied. */
export const EXAMPLE_SCENARIOS: Scenario[] = [
  {
    id: 'nominal',
    name: 'Nominal operations',
    kind: 'nominal',
    description: 'Synthetic repeating orbit with continuous OBC, ADCS and beacon service. Two imaging windows in sunlight and one eclipse contact give about 4.2 W average load demand. Timing and power are authored assumptions.',
    revision: 1,
    illuminationFactor: 1,
    initialEnergyFraction: 0.72,
    minimumEnergyFraction: 0.25,
    durationOrbits: 6,
    provenance: PROVENANCE,
    loads: [
      { id: 'nominal-obc', name: 'OBC', subsystem: 'Command & data', color: '#8db9a1', activePowerW: 0.9, idlePowerW: 0.15, railV: 3.3, essential: true, windows: [{ id: 'nominal-obc-on', start: 0, end: 1 }] },
      { id: 'nominal-adcs', name: 'ADCS', subsystem: 'Attitude control', color: '#80b7c8', activePowerW: 1.2, idlePowerW: 0.2, railV: 5, essential: true, windows: [{ id: 'nominal-adcs-on', start: 0, end: 1 }] },
      { id: 'nominal-beacon', name: 'Beacon', subsystem: 'Communications', color: '#a9be89', activePowerW: 0.25, idlePowerW: 0.02, railV: 3.3, essential: true, windows: [{ id: 'nominal-beacon-on', start: 0, end: 1 }] },
      { id: 'nominal-imaging', name: 'Imaging payload', subsystem: 'Payload', color: '#f28669', activePowerW: 5.8, idlePowerW: 0.1, railV: 5, essential: false, windows: [{ id: 'nominal-image-1', start: 0.12, end: 0.24 }, { id: 'nominal-image-2', start: 0.42, end: 0.48 }] },
      { id: 'nominal-contact', name: 'Downlink radio', subsystem: 'Communications', color: '#b9a1cf', activePowerW: 7.5, idlePowerW: 0.15, railV: 5, essential: false, windows: [{ id: 'nominal-contact-1', start: 0.78, end: 0.86 }] },
    ],
  },
  {
    id: 'high-demand',
    name: 'Imaging + contact stress',
    kind: 'nominal',
    description: 'Synthetic negative case with coincident imaging and downlink. Average demand exceeds 17 W, so the illustrative 12 W solar source cannot replenish it even with continuous ideal illumination. A 20 Wh battery only delays depletion. This is an authored energy-balance stress case, not a hardware claim.',
    revision: 1,
    illuminationFactor: 1,
    initialEnergyFraction: 0.85,
    minimumEnergyFraction: 0.25,
    durationOrbits: 5,
    provenance: PROVENANCE,
    loads: [
      { id: 'stress-obc', name: 'OBC', subsystem: 'Command & data', color: '#8db9a1', activePowerW: 1, idlePowerW: 0.15, railV: 3.3, essential: true, windows: [{ id: 'stress-obc-on', start: 0, end: 1 }] },
      { id: 'stress-adcs', name: 'ADCS', subsystem: 'Attitude control', color: '#80b7c8', activePowerW: 2.2, idlePowerW: 0.2, railV: 5, essential: true, windows: [{ id: 'stress-adcs-on', start: 0, end: 1 }] },
      { id: 'stress-beacon', name: 'Beacon', subsystem: 'Communications', color: '#a9be89', activePowerW: 0.3, idlePowerW: 0.02, railV: 3.3, essential: true, windows: [{ id: 'stress-beacon-on', start: 0, end: 1 }] },
      { id: 'stress-imaging', name: 'Imaging payload', subsystem: 'Payload', color: '#f28669', activePowerW: 12, idlePowerW: 0.2, railV: 5, essential: false, windows: [{ id: 'stress-image-1', start: 0.08, end: 0.6 }] },
      { id: 'stress-contact', name: 'Downlink radio', subsystem: 'Communications', color: '#b9a1cf', activePowerW: 16, idlePowerW: 0.25, railV: 5, essential: false, windows: [{ id: 'stress-contact-1', start: 0.45, end: 0.9 }] },
    ],
  },
  {
    id: 'survival',
    name: 'Low-light survival',
    kind: 'survival',
    description: 'Synthetic finite survival interval at 12% illumination with only essential OBC, reduced ADCS and beacon loads. The schedule is manually authored. Essential flags do not implement automatic shedding, and a recovery transition is outside this example.',
    revision: 1,
    illuminationFactor: 0.12,
    initialEnergyFraction: 0.65,
    minimumEnergyFraction: 0.15,
    durationOrbits: 8,
    provenance: PROVENANCE,
    loads: [
      { id: 'survival-obc', name: 'OBC · reduced mode', subsystem: 'Command & data', color: '#8db9a1', activePowerW: 0.55, idlePowerW: 0.1, railV: 3.3, essential: true, windows: [{ id: 'survival-obc-on', start: 0, end: 1 }] },
      { id: 'survival-adcs', name: 'ADCS · safe pointing', subsystem: 'Attitude control', color: '#80b7c8', activePowerW: 0.45, idlePowerW: 0.1, railV: 5, essential: true, windows: [{ id: 'survival-adcs-on', start: 0, end: 1 }] },
      { id: 'survival-beacon', name: 'Beacon · low power', subsystem: 'Communications', color: '#a9be89', activePowerW: 0.12, idlePowerW: 0.01, railV: 3.3, essential: true, windows: [{ id: 'survival-beacon-on', start: 0, end: 1 }] },
    ],
  },
];
