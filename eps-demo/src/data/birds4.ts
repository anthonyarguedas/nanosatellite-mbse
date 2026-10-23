import type { DesignInputs, ParameterProvenance, Role } from '../types';
import { BIRDS4_SOURCE, EXAMPLE_SCENARIOS } from './scenarios';

/** Sourced mission context is deliberately separate from editable numerical study assumptions. */
export const BIRDS4_EXAMPLE_BASIS = {
  title: 'BIRDS-4-inspired EPS concept study (illustrative COTS substitutions)',
  source: BIRDS4_SOURCE,
  missionFacts: [
    'GuaraniSat-1, Maya-2 and Tsuru were three 1U CubeSats deployed from the ISS on 14 March 2021 (§§1–2).',
    'Camera, APRS, store-and-forward, Hentenna, radiation/latch-up, perovskite-cell and attitude experiments are mission activities (§3).',
    'Camera discussion uses 400 km (§5.1). The precise orbital epoch remains unspecified. SF-WARD flight exchange failed (§5.3).',
    'Reported generation shortfall motivates a degraded case. Its reported mWh figures are not a reconstructed simulation interval.',
  ],
  limits: 'Numerical load powers, schedules, rails, lifetime, generation availability and energy criteria are editable assumptions. COTS substitutions are not the BIRDS-4 flight EPS. No installation, charge-SoC, cycle-life, thermal, protection or flight qualification is established.',
};

export const BIRDS4_DEFAULT_ALLOCATIONS: { role: Role; productId: string; quantity: number; rationale: string }[] = [
  { role: 'solar', productId: 'azur-3g30c-advanced-81780', quantity: 3, rationale: 'Three bare cells at the routine preliminary lower bound. This is an illustrative substitution. No series/parallel, packing, pointing or harness arrangement is established.' },
  { role: 'conditioning', productId: 'gomspace-p80-config1', quantity: 1, rationale: 'One fixed P80 configuration-1 assembly provides conditioning, distribution and processor roles. Battery is external. Software remains unallocated. Not BIRDS-4 flight hardware.' },
  { role: 'battery', productId: 'gomspace-bp8-100wh-8s1p', quantity: 1, rationale: 'One fixed BP8 8S1P pack uses published 86 Wh typical recommended-range energy, not the 100 Wh nameplate. Oversized illustrative substitution with a retained mass violation, not a feasible 1U flight selection.' },
];

export function birds4Inputs(): DesignInputs {
  return {
    mission: {
      name: 'BIRDS-4 / Tsuru concept study', altitudeKm: 400, lifetimeYears: 1,
      conOps: 'BIRDS-4-inspired 1U concept: maintain housekeeping and CW beacon service, schedule camera imaging, planned APRS/store-and-forward activities and attitude/technology experiments, then inspect overlapping demand and reduced-generation essential service. Activity context is sourced from Shrestha et al. (2022), §§3–5.6. SF-WARD flight exchange failed. The 400 km circular orbit is representative, not an epoch reconstruction. One-year lifetime and all numerical powers, schedules, rails and energy criteria are editable study assumptions. AZUR/BP8/P80 are illustrative COTS substitutions, not BIRDS-4 flight hardware.',
    },
    scenarios: structuredClone(EXAMPLE_SCENARIOS), activeScenarioId: EXAMPLE_SCENARIOS[0].id,
    solar: { sunlightEfficiency: 0.85, eclipseEfficiency: 0.7, cellEolV: 2.22, cellEolA: 0.969, installedPowerW: 6.45354 },
    battery: { dod: 0.3, margin: 0.2, capacityWh: 86, retainedEnergy: 0.8, chargeEfficiency: 0.95, dischargeEfficiency: 0.95, maxChargeW: 3, maxDischargeW: 6 },
    topology: { conditioning: 'MPPT', distribution: 'centralized', bus: 'regulated', efficiency: 0.9, idlePowerW: 1.41, massAllocationKg: 0.5 },
  };
}

const assumption = (parameter: ParameterProvenance['parameter'], value: number, rationale: string, conditions = 'Editable concept study assumption. Product and flight performance remain uncharacterized.', sourceIds: string[] = []): ParameterProvenance =>
  ({ parameter, value, kind: 'engineering-assumption', rationale, conditions, sourceIds });

export const BIRDS4_DEFAULT_PROVENANCE: ParameterProvenance[] = [
  assumption('mission.altitudeKm', 400, 'Representative circular reference based on the camera discussion at 400 km (§5.1), not a precise flight orbit/epoch.'),
  assumption('mission.lifetimeYears', 1, 'One-year demonstration design lifetime. This is a study assumption.'),
  assumption('solar.sunlightEfficiency', 0.85, 'Preliminary sunlight path efficiency Xs, applied in sizing only.'),
  assumption('solar.eclipseEfficiency', 0.7, 'Preliminary eclipse energy path efficiency Xe, applied in sizing only.'),
  assumption('solar.installedPowerW', 6.45354, '3 × (2.22 V × 0.969 A) = 6.45354 W. Assuming simultaneous constant availability is illustrative, not established installation/illumination performance.', 'Conditional typical AZUR radiation endpoint 1E15 1 MeV electrons/cm², AM0, 1367 W/m², 28 °C. Mission fluence, pointing, temperature, wiring and guaranteed extrema are unassessed.', ['azur-3g30-2025']),
  assumption('battery.dod', 0.3, 'Preliminary assumed DoD. No applicable cycle-life fit exists. The allowable DoD remains unassessed.'),
  assumption('battery.margin', 0.2, 'Preliminary degradation margin M, applied once to the requirement, not again to physical retained capacity.'),
  assumption('battery.retainedEnergy', 0.8, 'Study retained-energy factor, not BP8 EOL evidence or ICEPS2 storage recoverability.'),
  assumption('battery.chargeEfficiency', 0.95, 'Assumed internal battery charging energy efficiency, not a catalog specification.'),
  assumption('battery.dischargeEfficiency', 0.95, 'Assumed internal battery discharging energy efficiency, not a catalog specification.'),
  assumption('battery.maxChargeW', 3, 'Engineer-declared terminal charge-power bound, not inferred from current × nominal voltage.'),
  assumption('battery.maxDischargeW', 6, 'Engineer-declared terminal discharge-power bound, not a sourced continuous/pulse rating.'),
  assumption('topology.efficiency', 0.9, 'Constant conditioning efficiency for the MPPT energy model. P80 curves are not flattened into a catalog scalar.'),
  assumption('topology.idlePowerW', 1.41, 'Additional EPS baseline: P80 1.25 W + BP8 0.005 A × 32 V = 0.16 W. Applying these different cited idle states continuously is an explicit applicability assumption, not a loaded-system measurement.', 'P80 PMU/ACU features enabled and PDU outputs disabled. BP8 ENA-active standby at 32 V. Assumes heaters off. Enabled-output increments, actual battery voltage, temperature and heater demand remain unassessed. Excludes scenario OBC/loads and is added once.', ['gomspace-p80-2.3.0', 'gomspace-bp8-1.2.0']),
  assumption('topology.massAllocationKg', 0.5, 'EPS study allocation retained despite a known board-plus-pack mass excess. No relaxation to make the example pass.'),
];
