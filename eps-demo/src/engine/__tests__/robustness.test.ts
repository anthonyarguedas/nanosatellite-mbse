import { describe, expect, it } from 'vitest';
import type { Load, Scenario } from '../../types';
import { assessDesign, calculateBudget, simulateOrbit, suggestProducts } from '../index';
import { inputs, load, orbit, product, scenario, spec } from './fixtures';

/** Independent interval-length oracle, without event sampling or engine profile helpers. */
function loadEnergyWs(s: Scenario): number {
  let ws = 0;
  for (const item of s.loads) {
    ws += item.idlePowerW * s.durationOrbits * orbit.periodS;
    for (let cycle = 0; cycle < Math.ceil(s.durationOrbits); cycle++) {
      const tail = Math.min(1, s.durationOrbits - cycle);
      const intervals = item.windows.map(w => [Math.max(0, w.start), Math.min(tail, w.end)])
        .filter(([start, end]) => end > start).sort((a, b) => a[0] - b[0]);
      let unionLength = 0;
      let end = 0;
      for (const [start, nextEnd] of intervals) {
        unionLength += Math.max(0, nextEnd - Math.max(start, end));
        end = Math.max(end, nextEnd);
      }
      ws += (item.activePowerW - item.idlePowerW) * unionLength * orbit.periodS;
    }
  }
  return ws;
}

describe('independent conservation and edge cases', () => {
  it('conserves energy for 60 deterministic random overlapping schedules and fractional endpoints', () => {
    let state = 123456789;
    const random = () => { state = (1664525 * state + 1013904223) >>> 0; return state / 2 ** 32; };
    for (let trial = 0; trial < 60; trial++) {
      const loads: Load[] = Array.from({ length: 4 }, (_, l) => load({
        id: `load-${l}`, activePowerW: random() * 20, idlePowerW: random() * 4,
        windows: Array.from({ length: 5 }, (_, w) => {
          const a = random();
          const b = random();
          return { id: `${w}`, start: Math.min(a, b), end: Math.max(a, b) };
        }),
      }));
      const s = scenario({ loads, durationOrbits: 0.1 + random() * 3 });
      const i = inputs(s);
      i.battery.capacityWh = 1000;
      i.battery.retainedEnergy = 1;
      i.battery.chargeEfficiency = 1;
      i.battery.dischargeEfficiency = 1;
      i.solar.installedPowerW = 25;
      i.topology.efficiency = 1;
      const sunS = Math.floor(s.durationOrbits) * 60 + Math.min((s.durationOrbits % 1) * 100, 60);
      const expected = 500 + (25 * sunS - loadEnergyWs(s)) / 3600;
      const result = simulateOrbit(i, s, orbit);
      expect(result.endEnergyWh).toBeCloseTo(expected, 9);
      expect(result.stoppedAtS).toBeNull();
      expect(result.shortageWh).toBe(0);
      expect(result.curtailedWh).toBe(0);
      const whole = { ...s, durationOrbits: 1 };
      expect(calculateBudget(whole, orbit).totalWh).toBeCloseTo(loadEnergyWs(whole) / 3600, 12);
    }
  });
  it('does not turn rounding from many equivalent mode events into a false closure violation', () => {
    const s = scenario({ loads: [load({ activePowerW: 10, idlePowerW: 10,
      windows: Array.from({ length: 2000 }, (_, index) => ({ id: `${index}`, start: index * 0.6 / 2000, end: (index + 1) * 0.6 / 2000 })),
    })] });
    const i = inputs(s);
    i.topology.efficiency = 1;
    i.battery.chargeEfficiency = 1;
    i.battery.dischargeEfficiency = 1;
    i.solar.installedPowerW = 10 / orbit.sunlightFraction;
    const result = simulateOrbit(i, s, orbit);
    expect(Math.abs(result.closureWh)).toBeLessThan(32 * Number.EPSILON * result.capacityWh);
    expect(result.checks.find(c => c.id === 'ENERGY-CLOSURE')?.verdict).toBe('pass');
  });
  it('integrates repeated sub-millisecond pulses through the fractional final orbit', () => {
    const s = scenario({ durationOrbits: 2.5, loads: [load({ activePowerW: 5000, idlePowerW: 0,
      windows: [{ id: 'pulse', start: 0.234567, end: 0.234568 }] })] });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    i.battery.maxDischargeW = 5000;
    const result = simulateOrbit(i, s, orbit);
    expect(result.endEnergyWh).toBeCloseTo(40 - loadEnergyWs(s) / (0.8 * 3600), 12);
    expect(result.points.filter(p => p.demandW === 5000).length).toBeGreaterThanOrEqual(6);
  });
  it('applies terminal discharge bound before internal efficiency, including exact equality', () => {
    const i = inputs();
    i.battery.maxDischargeW = 4;
    const result = simulateOrbit(i, i.scenarios[0], orbit);
    expect(result.stoppedAtS).toBeNull();
    expect(result.checks.find(c => c.id === 'BATTERY-DISCHARGE')?.verdict).toBe('pass');
  });
  it('retains an invalid-discharge failure even before the first completed orbit', () => {
    const s = scenario({ durationOrbits: 0.5 });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    i.battery.maxDischargeW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(result.stoppedAtS).toBe(0);
    expect(result.shortageWh).toBeGreaterThan(0);
    expect(result.checks.find(c => c.id === 'EPS-11')?.verdict).toBe('fail');
  });
  it('supports exact zero-energy boundaries without manufacturing an overrun', () => {
    const s = scenario({ durationOrbits: 0.5, initialEnergyFraction: 0, minimumEnergyFraction: 0, loads: [] });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(result.endEnergyWh).toBe(0);
    expect(result.stoppedAtS).toBeNull();
    expect(result.checks.find(c => c.id === 'ENERGY-RESERVE')?.verdict).toBe('pass');
  });
  it('does not use an absolute one-Wh tolerance to hide depletion of tiny capacities', () => {
    const s = scenario({ initialEnergyFraction: 0.5, minimumEnergyFraction: 0 });
    const i = inputs(s);
    i.battery.capacityWh = 1e-20;
    i.battery.retainedEnergy = 1;
    i.solar.installedPowerW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(result.stoppedAtS).not.toBeNull();
    expect(result.shortageWh).toBeGreaterThan(0);
    expect(result.checks.find(c => c.id === 'ENERGY-DEMAND')?.verdict).toBe('fail');
  });
  it('reports reserve failure for an initial state below reserve without rejecting a valid state', () => {
    const s = scenario({ initialEnergyFraction: 0.2, minimumEnergyFraction: 0.3, loads: [] });
    const result = simulateOrbit(inputs(s), s, orbit);
    expect(result.stoppedAtS).toBeNull();
    expect(result.minEnergyWh).toBe(16);
    expect(result.checks.find(c => c.id === 'ENERGY-RESERVE')?.verdict).toBe('fail');
  });
  it('keeps assessment IDs unique and validates known malformed numerical inputs', () => {
    const i = inputs();
    const result = assessDesign(i, { simulation: simulateOrbit(i, i.scenarios[0], orbit) }, { revision: 'test', products: [] }, {});
    expect(new Set(result.map(c => c.id)).size).toBe(result.length);
    i.solar.installedPowerW = NaN;
    expect(() => assessDesign(i, {}, { revision: 'test', products: [] }, {})).toThrow(/source power/);
  });
  it('bounds the catalog explicitly instead of silently truncating it', () => {
    const products = Array.from({ length: 129 }, (_, index) => product({ id: `${index}` }));
    expect(() => suggestProducts({ revision: 'test', products }, inputs(), {})).toThrow(/128/);
  });
  it('does not upgrade overflowing derived catalog power into a guaranteed pass', () => {
    const p = product({ specs: { vmpEolV: spec(1e300, 'V'), impEolA: spec(1e300, 'A') } });
    const result = suggestProducts({ revision: 'test', products: [p] }, inputs(), {
      solar: { minimumPowerW: 10, cellPowerW: 1, rawCellCount: 10, cellCount: 10 },
    })[0];
    expect(result.outcome).toBe('incomplete');
    expect(result.checks[0].verdict).toBe('unassessed');
  });
});
