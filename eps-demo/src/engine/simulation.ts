import type { Check, DesignInputs, OrbitResult, Scenario, SimulationPoint, SimulationResult } from '../types';
import { demandAtPhase, phaseEvents } from './profiles';
import { efficiency, finiteResult, numberInRange, validateOrbit, validateScenario } from './validation';

const PLOT_STEP_S = 10;
const MAX_POINTS = 250_000;
interface Rates { sunlight: boolean; generationW: number; demandW: number }

/** Exact integration of constant-power event intervals. Plot samples never drive the physics. */
export function simulateOrbit(inputs: DesignInputs, scenario: Scenario, orbit: OrbitResult): SimulationResult {
  if (inputs.topology.conditioning !== 'MPPT') throw new Error('DET propagation needs a characterized array I–V operating point. This demo supports the constant-efficiency MPPT model only.');
  validateOrbit(orbit);
  validateScenario(scenario);
  const sourceW = numberInRange(inputs.solar.installedPowerW, 'Installed available EOL source power (W)');
  const eta = efficiency(inputs.topology.efficiency, 'Conditioning efficiency');
  const idleW = numberInRange(inputs.topology.idlePowerW, 'Additional EPS idle demand (W)');
  const bol = numberInRange(inputs.battery.capacityWh, 'Battery BOL capacity (Wh)', 0, Infinity, true);
  const retained = efficiency(inputs.battery.retainedEnergy, 'Retained energy factor fE');
  const capacityWh = numberInRange(finiteResult(bol * retained, 'Battery EOL capacity'), 'Battery EOL capacity', 0, Infinity, true);
  const etaC = efficiency(inputs.battery.chargeEfficiency, 'Battery energy charging efficiency');
  const etaD = efficiency(inputs.battery.dischargeEfficiency, 'Battery energy discharging efficiency');
  const maxChargeW = numberInRange(inputs.battery.maxChargeW, 'User terminal charge power bound (W)');
  const maxDischargeW = numberInRange(inputs.battery.maxDischargeW, 'User terminal discharge power bound (W)');
  const durationS = numberInRange(finiteResult(scenario.durationOrbits * orbit.periodS, 'Simulation duration'), 'Simulation duration', 0, Infinity, true);
  const phases = phaseEvents(scenario, orbit);
  const estimatedPoints = durationS / PLOT_STEP_S + 4 * (phases.length + 1) * Math.ceil(scenario.durationOrbits);
  if (estimatedPoints > MAX_POINTS) {
    throw new Error(`Duration and event count exceed this demo's ${MAX_POINTS} point simulation bound. Shorten the scenario.`);
  }
  const timeSet = new Set([0, durationS]);
  // Keep exact distinct events. A tolerance-based merge could erase a narrow pulse.
  for (let k = 0; k < Math.ceil(scenario.durationOrbits); k++) {
    for (const phase of phases) {
      const time = k * orbit.periodS + (phase === orbit.sunlightFraction ? orbit.sunlightS : phase * orbit.periodS);
      if (time > 0 && time < durationS) timeSet.add(time);
    }
  }
  const times = [...timeSet].sort((a, b) => a - b);
  const points: SimulationPoint[] = [];
  const startEnergyWh = capacityWh * scenario.initialEnergyFraction;
  const reserveWh = capacityWh * scenario.minimumEnergyFraction;
  // Roundoff only. This is not an engineering allowance for persistent depletion.
  const epsilonWh = 32 * Number.EPSILON * capacityWh;
  let energyWh = startEnergyWh;
  let energyRoundoff = 0;
  // Compensated summation prevents redundant mode boundaries from accumulating false closure loss.
  function sumEnergy(deltaWh: number): number {
    const corrected = deltaWh - energyRoundoff;
    const next = energyWh + corrected;
    energyRoundoff = (next - energyWh) - corrected;
    return next;
  }
  let minEnergyWh = energyWh;
  let shortageWh = 0;
  let curtailedWh = 0;
  let stoppedAtS: number | null = null;
  let dischargeViolation: string | undefined;
  let depletionViolation: string | undefined;

  function point(timeS: number, batteryWh: number, rates: Rates, surplusW: number): void {
    const next: SimulationPoint = {
      timeS, orbit: timeS / orbit.periodS, ...rates, batteryWh,
      energyPercent: 100 * batteryWh / capacityWh, surplusW,
    };
    const last = points.at(-1);
    if (last && last.timeS === timeS && last.batteryWh === batteryWh && last.sunlight === next.sunlight
      && last.generationW === next.generationW && last.demandW === next.demandW && last.surplusW === surplusW) return;
    points.push(next);
  }

  function span(start: number, end: number, fromWh: number, toWh: number, rates: Rates, surplusW: number): void {
    point(start, fromWh, rates, surplusW);
    const firstTick = Math.floor(start / PLOT_STEP_S) + 1;
    for (let tick = firstTick; tick * PLOT_STEP_S < end; tick++) {
      const time = tick * PLOT_STEP_S;
      const f = (time - start) / (end - start);
      point(time, fromWh + (toWh - fromWh) * f, rates, surplusW);
    }
    point(end, toWh, rates, surplusW);
    minEnergyWh = Math.min(minEnergyWh, toWh);
  }

  for (let i = 0; i + 1 < times.length; i++) {
    const t0 = times[i];
    const t1 = times[i + 1];
    const dtH = (t1 - t0) / 3600;
    const mid = t0 + (t1 - t0) / 2;
    const phase = (mid % orbit.periodS) / orbit.periodS;
    const sunlight = phase < orbit.sunlightFraction;
    const generationW = finiteResult(sunlight ? sourceW * scenario.illuminationFactor * eta : 0, 'Conditioned generation');
    const demandW = finiteResult(demandAtPhase(scenario, phase) + idleW, 'Total terminal-boundary demand');
    const rates: Rates = { sunlight, generationW, demandW };
    const netW = generationW - demandW;
    if (netW < 0) {
      const dischargeW = -netW;
      if (dischargeW > maxDischargeW) {
        // Stop before applying an unsupported discharge. Retain the deficit for this entire attempted event interval.
        shortageWh = finiteResult((dischargeW - maxDischargeW) * dtH, 'Power-limit shortage');
        dischargeViolation = `Required terminal discharge ${dischargeW.toPrecision(6)} W exceeds the user bound ${maxDischargeW} W at ${t0.toPrecision(8)} s. Stopped before unsupported propagation.`;
        stoppedAtS = t0;
        point(t0, energyWh, rates, 0);
        break;
      }
      const withdrawalWh = finiteResult(dischargeW / etaD * dtH, 'Battery energy withdrawal');
      if (withdrawalWh > energyWh + epsilonWh) {
        const depletionTime = Math.min(t1, t0 + energyWh * etaD / dischargeW * 3600);
        shortageWh = Math.max(0, dischargeW * dtH - energyWh * etaD);
        depletionViolation = `Battery energy is exhausted at ${depletionTime.toPrecision(8)} s. ${shortageWh.toPrecision(6)} Wh of terminal demand remains in the attempted event interval. Later intervals were not propagated.`;
        span(t0, depletionTime, energyWh, 0, rates, 0);
        energyWh = 0;
        energyRoundoff = 0;
        stoppedAtS = depletionTime;
        break;
      }
      const summed = sumEnergy(-withdrawalWh);
      const next = Math.max(0, summed); // At most machine-roundoff correction at the exact zero boundary.
      if (next !== summed) energyRoundoff = 0;
      span(t0, t1, energyWh, next, rates, 0);
      energyWh = next;
    } else {
      const acceptedW = Math.min(netW, maxChargeW);
      const timeToFullH = acceptedW > 0 ? (capacityWh - energyWh) / (etaC * acceptedW) : Infinity;
      if (timeToFullH < dtH) {
        const fullAt = Math.min(t1, t0 + Math.max(0, timeToFullH) * 3600);
        if (fullAt > t0) span(t0, fullAt, energyWh, capacityWh, rates, netW - acceptedW);
        span(fullAt, t1, capacityWh, capacityWh, rates, netW);
        curtailedWh += (netW - acceptedW) * ((fullAt - t0) / 3600) + netW * ((t1 - fullAt) / 3600);
        energyWh = capacityWh;
        energyRoundoff = 0;
      } else {
        const summed = sumEnergy(etaC * acceptedW * dtH);
        const next = Math.min(capacityWh, summed);
        if (next !== summed) energyRoundoff = 0;
        span(t0, t1, energyWh, next, rates, netW - acceptedW);
        curtailedWh += (netW - acceptedW) * dtH;
        energyWh = next;
      }
    }
  }

  const closureWh = energyWh - startEnergyWh;
  const supplied = stoppedAtS === null;
  const reservePass = supplied && minEnergyWh + epsilonWh >= reserveWh;
  // A fractional tail is not a nominal repeating interval. Check every completed orbit instead.
  const completeOrbits = Math.floor(scenario.durationOrbits);
  const orbitClosures: number[] = [];
  const energyAtTime = new Map(points.map(p => [p.timeS, p.batteryWh]));
  for (let k = 1; k <= completeOrbits; k++) {
    const end = energyAtTime.get(k * orbit.periodS);
    const start = energyAtTime.get((k - 1) * orbit.periodS);
    if (end !== undefined && start !== undefined) orbitClosures.push(end - start);
  }
  const closureVerdict = scenario.kind !== 'nominal' ? 'unassessed'
    : !supplied || orbitClosures.some(delta => delta < -epsilonWh) ? 'fail'
      : completeOrbits > 0 && orbitClosures.length === completeOrbits ? 'pass' : 'unassessed';
  const failureDetail = dischargeViolation ?? depletionViolation;
  const checks: Check[] = [
    {
      id: 'ENERGY-DEMAND', title: 'Scheduled demand supplied in the energy model', verdict: supplied ? 'pass' : 'fail',
      detail: failureDetail ?? 'All scheduled loads and the additional EPS idle demand were supplied within the user energy/power bounds.',
      scope: 'Constant power, energy only. No terminal-voltage, current, temperature or hardware guarantee.',
    },
    {
      id: 'BATTERY-DISCHARGE', title: 'User discharge power bound', verdict: dischargeViolation ? 'fail' : supplied ? 'pass' : 'unassessed',
      detail: dischargeViolation ?? (supplied ? `Required terminal discharge stayed at or below ${maxDischargeW} W.` : 'No power violation before depletion. Later demand was not evaluated.'),
      scope: 'Engineer-declared W bound, not a sourced current or pulse rating.',
    },
    {
      id: 'ENERGY-RESERVE', title: 'Stored energy reserve', verdict: reservePass ? 'pass' : 'fail',
      detail: `${minEnergyWh.toPrecision(8)} Wh minimum versus ${reserveWh.toPrecision(8)} Wh required.${failureDetail ? ` ${failureDetail}` : ''}`,
      equation: 'Emin >= minimumEnergyFraction * (capacityWh * retainedEnergy)', scope: 'Normalized energy is not charge-based state of charge.',
    },
    {
      id: 'ENERGY-CLOSURE', title: 'Nominal repeating energy closure', verdict: closureVerdict,
      detail: scenario.kind !== 'nominal' ? 'Survival reserve is evaluated. No nominal repeating closure or recovery policy is defined.'
        : `Endpoint change ${closureWh.toPrecision(8)} Wh. ${orbitClosures.length} complete orbit interval(s) checked with ${epsilonWh.toExponential(2)} Wh roundoff tolerance.${scenario.durationOrbits % 1 !== 0 ? ' Fractional tail is excluded from repeating closure.' : ''}${!supplied ? ' Run stopped before the requested duration.' : ''}`,
      equation: 'Eend >= Estart - epsilonE, at each completed nominal orbit', scope: 'Energy only. Charge closure is unsupported.',
    },
    {
      id: 'EPS-10', title: 'Nominal service and reserve',
      verdict: scenario.kind === 'nominal' && !reservePass ? 'fail' : 'unassessed',
      detail: scenario.kind !== 'nominal' ? 'No nominal scenario evaluated by this run.'
        : !reservePass ? 'Known energy service or reserve violation. See ENERGY-DEMAND and ENERGY-RESERVE.'
          : 'Energy checks pass. Charge-based state of charge, DoD, terminal voltage and characterized Q/v mapping are missing.',
    },
    {
      id: 'EPS-11', title: 'Nominal replenishment', verdict: closureVerdict === 'fail' ? 'fail' : 'unassessed',
      detail: closureVerdict === 'fail' ? 'Known energy closure violation or interrupted nominal run.'
        : 'Energy closure alone cannot establish charge closure. Charge-based state and a characterized Q/v mapping are missing.',
    },
    {
      id: 'EPS-12', title: 'Survival service and recovery',
      verdict: scenario.kind === 'survival' && !reservePass ? 'fail' : 'unassessed',
      detail: scenario.kind === 'survival' && !reservePass ? 'Known survival energy service or reserve violation.'
        : 'Charge limits, essential-service interfaces and an authorized recovery transition are not modeled. No automatic load shedding is inferred.',
    },
    {
      id: 'EPS-14', title: 'Solar surplus disposal capability', verdict: 'unassessed',
      detail: `${curtailedWh.toPrecision(8)} Wh of unused conditioned surplus recorded numerically. No curtailment/shunt circuit, termination, voltage or thermal capability was verified.`,
    },
  ];
  return {
    scenarioId: scenario.id, scenarioRevision: scenario.revision, reserveWh, durationS, points, minEnergyWh, startEnergyWh, endEnergyWh: energyWh, capacityWh, closureWh,
    shortageWh, curtailedWh: finiteResult(curtailedWh, 'Numerical surplus energy'), stoppedAtS, checks,
    assumptions: [
      'Circular fixed-eclipse orbit. Phase 0 starts in sunlight. Windows repeat each orbit and active power replaces idle over their union.',
      'Installed power is available EOL power at the solar source boundary. Illumination multiplies it once. Constant conditioning efficiency multiplies it once to the common boundary outside battery terminals.',
      'All scheduled loads plus additional EPS idle power are demanded at that common boundary. Idle power must exclude consumption already present in the load profile. Distribution losses, voltages and transients are not characterized.',
      'Battery internal energy charging/discharging efficiencies apply once. Max charge/discharge W are user bounds at the external terminal boundary, not verified catalog ratings.',
      'Fixed EOL energy capacity is BOL capacity times retainedEnergy once. Preliminary margin M, DoD and sizing path efficiencies Xs/Xe are not reused in propagation.',
      'Charging stops at fixed energy capacity. Charge-based SoC, coulomb counting, Q/v mapping, temperature and charge termination are unsupported.',
      'Integration uses exact mode/eclipse events and fractional final duration. Points every 10 s, exact events and full-charge/depletion transitions are for plotting. Orbit coordinate is elapsed fractional orbits.',
      'An invalid discharge stops the run. Shortage is terminal energy unmet in the attempted event interval only. Later intervals are unevaluated, so shortage is a lower bound for the requested duration.',
      'Unused conditioned surplus is recorded as numerical curtailment. Hardware curtailment or shunt capability remains unassessed.',
      'Nominal energy closure is checked per completed orbit with machine-roundoff tolerance. A fractional tail is not treated as a repeating interval. Survival recovery is undefined.',
    ],
  };
}
