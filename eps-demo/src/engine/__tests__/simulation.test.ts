import { describe, expect, it } from 'vitest';
import { simulateOrbit } from '../index';
import { inputs, load, orbit, scenario } from './fixtures';

const verdict = (result: ReturnType<typeof simulateOrbit>, id: string) => result.checks.find(check => check.id === id)?.verdict;

describe('event-aware energy propagation', () => {
  it('applies conditioning and internal battery efficiencies at their boundaries exactly once', () => {
    const s = scenario();
    const i = inputs(s);
    const result = simulateOrbit(i, s, orbit);
    // Source 10 W * conditioning .8 = 8 W, load 4 W. Charge 4 W for 60 s, discharge 4 W for 40 s.
    const expected = 40 + 0.9 * 4 * 60 / 3600 - 4 / 0.8 * 40 / 3600;
    expect(result.startEnergyWh).toBe(40);
    expect(result.capacityWh).toBe(80);
    expect(result.endEnergyWh).toBeCloseTo(expected, 13);
    expect(result.closureWh).toBeCloseTo(expected - 40, 13);
    expect(result.points[0].generationW).toBe(8);
    expect(result.points[0].demandW).toBe(4);
    expect(verdict(result, 'ENERGY-RESERVE')).toBe('pass');
    expect(verdict(result, 'ENERGY-CLOSURE')).toBe('pass');
    expect(verdict(result, 'EPS-10')).toBe('unassessed');
    expect(verdict(result, 'EPS-11')).toBe('unassessed');
    i.battery.margin = 99;
    i.battery.dod = 0.9;
    i.solar.sunlightEfficiency = 0.01;
    i.solar.eclipseEfficiency = 0.02;
    expect(simulateOrbit(i, s, orbit).endEnergyWh).toBe(result.endEnergyWh);
  });
  it('multiplies illumination once and counts EPS idle once', () => {
    const s = scenario({ illuminationFactor: 0.5 });
    const i = inputs(s);
    i.topology.idlePowerW = 1;
    const result = simulateOrbit(i, s, orbit);
    expect(result.points[0].generationW).toBe(4);
    expect(result.points[0].demandW).toBe(5);
    expect(result.endEnergyWh).toBeCloseTo(40 - (1 * 60 + 5 * 40) / (0.8 * 3600), 13);
  });
  it('caps accepted charging at user maxChargeW and records numerical surplus', () => {
    const s = scenario({ loads: [] });
    const i = inputs(s);
    i.battery.maxChargeW = 2;
    const result = simulateOrbit(i, s, orbit);
    expect(result.endEnergyWh).toBeCloseTo(40 + 0.9 * 2 * 60 / 3600, 13);
    expect(result.curtailedWh).toBeCloseTo((8 - 2) * 60 / 3600, 13);
    expect(verdict(result, 'EPS-14')).toBe('unassessed');
  });
  it('integrates exact full-capacity arrival and never overfills', () => {
    const s = scenario({ loads: [], initialEnergyFraction: 0.999 });
    const i = inputs(s);
    i.battery.capacityWh = 1;
    i.battery.retainedEnergy = 1;
    const result = simulateOrbit(i, s, orbit);
    const fullAt = 0.001 / (0.9 * 8) * 3600;
    expect(Math.max(...result.points.map(point => point.batteryWh))).toBe(1);
    expect(result.endEnergyWh).toBe(1);
    expect(result.curtailedWh).toBeCloseTo(8 * 60 / 3600 - 0.001 / 0.9, 13);
    expect(result.points.some(point => Math.abs(point.timeS - fullAt) < 1e-10)).toBe(true);
  });
  it('curtails all surplus when initially full and supports disabled charging', () => {
    const s = scenario({ loads: [], initialEnergyFraction: 1 });
    const i = inputs(s);
    const full = simulateOrbit(i, s, orbit);
    expect(full.curtailedWh).toBeCloseTo(8 * 60 / 3600, 14);
    expect(full.closureWh).toBe(0);
    s.initialEnergyFraction = 0.5;
    i.battery.maxChargeW = 0;
    expect(simulateOrbit(i, s, orbit).endEnergyWh).toBe(40);
  });
  it('supports fractional durations and emits the exact endpoint', () => {
    const s = scenario({ durationOrbits: 0.735 });
    const i = inputs(s);
    const result = simulateOrbit(i, s, orbit);
    expect(result.points.at(-1)?.timeS).toBe(73.5);
    expect(result.points.at(-1)?.orbit).toBe(0.735);
    expect(result.endEnergyWh).toBeCloseTo(40 + 0.9 * 4 * 60 / 3600 - 4 / 0.8 * 13.5 / 3600, 13);
    expect(verdict(result, 'ENERGY-CLOSURE')).toBe('unassessed');
  });
  it('checks completed nominal intervals while excluding a fractional tail', () => {
    const s = scenario({ durationOrbits: 1.5 });
    const result = simulateOrbit(inputs(s), s, orbit);
    expect(result.points.at(-1)?.timeS).toBe(150);
    expect(verdict(result, 'ENERGY-CLOSURE')).toBe('pass');
  });
  it('does not alias a pulse between all regular plot ticks', () => {
    const start = 0.234567;
    const end = 0.234568;
    const s = scenario({ loads: [load({ activePowerW: 1000, idlePowerW: 0, windows: [{ id: 'pulse', start, end }] })] });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    i.battery.maxDischargeW = 2000;
    const result = simulateOrbit(i, s, orbit);
    expect(result.endEnergyWh).toBeCloseTo(40 - 1000 / 0.8 * (end - start) * 100 / 3600, 12);
    expect(result.points.some(point => point.timeS === start * 100 && point.demandW === 1000)).toBe(true);
    expect(result.points.some(point => point.timeS === end * 100)).toBe(true);
  });
  it('splits a pulse exactly at eclipse and unions overlapping intervals in simulation', () => {
    const s = scenario({ loads: [load({ activePowerW: 10, idlePowerW: 2, windows: [
      { id: 'a', start: 0.55, end: 0.65 }, { id: 'b', start: 0.6, end: 0.7 },
    ] })] });
    const i = inputs(s);
    const result = simulateOrbit(i, s, orbit);
    // 55 sunlight seconds charging 6 W, 5 sunlight seconds discharging 2 W, then 10 eclipse seconds at 10 W and 30 at 2 W.
    expect(result.endEnergyWh).toBeCloseTo(40 + 0.9 * 6 * 55 / 3600 - (2 * 5 + 10 * 10 + 2 * 30) / (0.8 * 3600), 12);
    expect(result.points.filter(point => point.timeS === 60).map(point => point.sunlight)).toEqual([true, false]);
    for (let time = 0; time <= 100; time += 10) expect(result.points.some(point => point.timeS === time)).toBe(true);
  });
  it('is pure and deterministic', () => {
    const s = scenario();
    const i = inputs(s);
    const before = JSON.stringify({ s, i, orbit });
    expect(simulateOrbit(i, s, orbit)).toEqual(simulateOrbit(i, s, orbit));
    expect(JSON.stringify({ s, i, orbit })).toBe(before);
  });
});

describe('retained known energy failures', () => {
  it('stops at a power-limit violation instead of clipping discharge and claiming success', () => {
    const s = scenario({ loads: [load({ activePowerW: 10, windows: [{ id: 'pulse', start: 0.234, end: 0.235 }] })] });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    i.battery.maxDischargeW = 5;
    const result = simulateOrbit(i, s, orbit);
    expect(result.stoppedAtS).toBe(23.400000000000002);
    expect(result.shortageWh).toBeCloseTo(5 * 0.1 / 3600, 14);
    expect(result.points.at(-1)?.timeS).toBe(result.stoppedAtS);
    expect(verdict(result, 'ENERGY-DEMAND')).toBe('fail');
    expect(verdict(result, 'EPS-10')).toBe('fail');
    expect(verdict(result, 'EPS-11')).toBe('fail');
  });
  it('stops at the exact depletion crossing, retains shortage and minimum, and never restarts in sunlight', () => {
    const s = scenario({ initialEnergyFraction: 0.5, minimumEnergyFraction: 0, durationOrbits: 2 });
    const i = inputs(s);
    i.battery.capacityWh = 0.02;
    i.battery.retainedEnergy = 1;
    i.solar.installedPowerW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(result.stoppedAtS).toBeCloseTo(0.01 * 0.8 / 4 * 3600, 14);
    expect(result.minEnergyWh).toBe(0);
    expect(result.endEnergyWh).toBe(0);
    expect(result.shortageWh).toBeCloseTo(4 * 60 / 3600 - 0.01 * 0.8, 14);
    expect(result.points.at(-1)?.timeS).toBe(result.stoppedAtS);
    expect(verdict(result, 'ENERGY-RESERVE')).toBe('fail');
    expect(verdict(result, 'EPS-11')).toBe('fail');
  });
  it('fails the energy reserve without clipping a valid but low state', () => {
    const s = scenario({ minimumEnergyFraction: 0.5 });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(result.stoppedAtS).toBeNull();
    expect(result.minEnergyWh).toBeLessThan(40);
    expect(result.shortageWh).toBe(0);
    expect(verdict(result, 'ENERGY-RESERVE')).toBe('fail');
    expect(verdict(result, 'EPS-10')).toBe('fail');
  });
  it('fails replenishment even when the battery supplied all demand above reserve', () => {
    const s = scenario();
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(verdict(result, 'ENERGY-DEMAND')).toBe('pass');
    expect(verdict(result, 'ENERGY-RESERVE')).toBe('pass');
    expect(verdict(result, 'ENERGY-CLOSURE')).toBe('fail');
    expect(verdict(result, 'EPS-10')).toBe('unassessed');
    expect(verdict(result, 'EPS-11')).toBe('fail');
  });
  it('keeps survival and recovery separate from nominal closure and does not shed loads silently', () => {
    const s = scenario({ kind: 'survival', minimumEnergyFraction: 0.5, loads: [load({ essential: false })] });
    const i = inputs(s);
    i.solar.installedPowerW = 0;
    const result = simulateOrbit(i, s, orbit);
    expect(result.endEnergyWh).toBeLessThan(result.startEnergyWh);
    expect(verdict(result, 'EPS-12')).toBe('fail');
    expect(verdict(result, 'EPS-10')).toBe('unassessed');
    expect(verdict(result, 'ENERGY-CLOSURE')).toBe('unassessed');
  });
});

describe('simulation validation', () => {
  it.each([0, -1, 1.01, NaN, null])('rejects invalid energy efficiency %s', value => {
    const i = inputs();
    i.battery.chargeEfficiency = value;
    expect(() => simulateOrbit(i, i.scenarios[0], orbit)).toThrow(/charging efficiency/);
  });
  it.each([0, -1, NaN, Infinity])('rejects invalid duration %s', durationOrbits => {
    const s = scenario({ durationOrbits });
    expect(() => simulateOrbit(inputs(s), s, orbit)).toThrow(/duration/);
  });
  it('rejects missing power bounds, invalid states, unsupported scale and zero capacity', () => {
    const i = inputs();
    i.battery.maxDischargeW = null;
    expect(() => simulateOrbit(i, i.scenarios[0], orbit)).toThrow(/discharge power/);
    expect(() => simulateOrbit(inputs(), scenario({ initialEnergyFraction: 1.1 }), orbit)).toThrow(/Initial energy/);
    expect(() => simulateOrbit(inputs(), scenario({ durationOrbits: 1e8 }), orbit)).toThrow(/point simulation bound/);
    const empty = inputs();
    empty.battery.capacityWh = 0;
    expect(() => simulateOrbit(empty, empty.scenarios[0], orbit)).toThrow(/capacity/);
  });
});
