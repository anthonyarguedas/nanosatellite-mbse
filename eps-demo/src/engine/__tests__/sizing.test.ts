import { describe, expect, it } from 'vitest';
import { calculateBudget, calculateOrbit, simulateOrbit, sizeBattery, sizeSolar } from '../index';
import { inputs, load, orbit, scenario } from './fixtures';

describe('orbit geometry from the proposal', () => {
  it('uses the given Earth constants and closes sun + eclipse exactly', () => {
    const result = calculateOrbit(500);
    expect(result.periodS).toBeCloseTo(2 * Math.PI * Math.sqrt(6878 ** 3 / 398601), 10);
    expect(result.psiRad).toBeCloseTo(Math.acos(6378 / 6878), 12);
    expect(result.sunlightS + result.eclipseS).toBe(result.periodS);
    expect(result.eclipseS).toBeCloseTo((0.5 - result.psiRad / Math.PI) * result.periodS, 10);
    expect(result.orbitsPerDay).toBeCloseTo(86400 / result.periodS, 12);
  });
  it('has a half-orbit eclipse at the mathematical zero-altitude boundary', () => {
    expect(calculateOrbit(0).sunlightFraction).toBe(0.5);
  });
  it.each([-1, NaN, Infinity, -Infinity, 1e200])('rejects invalid/overflow altitude %s', value => {
    expect(() => calculateOrbit(value)).toThrow();
  });
});

describe('exact load-window budget', () => {
  it('integrates exact fractions and splits a window at sunlight/eclipse', () => {
    const s = scenario({ loads: [load({ activePowerW: 10, idlePowerW: 2, windows: [{ id: 'one', start: 0.2, end: 0.8 }] })] });
    const result = calculateBudget(s, orbit);
    expect(result.sunlightWh).toBeCloseTo((2 * 20 + 10 * 40) / 3600, 14);
    expect(result.eclipseWh).toBeCloseTo((10 * 20 + 2 * 20) / 3600, 14);
    expect(result.totalWh).toBeCloseTo(6.8 * 100 / 3600, 14);
    expect(result.averageW).toBeCloseTo(6.8, 14);
    expect(result.peakW).toBe(10);
    expect(result.samples.map(p => p.phase)).toContain(0.6);
  });
  it('unions overlapping, adjacent, nested and duplicate windows, replacing idle', () => {
    const s = scenario({ loads: [load({ activePowerW: 10, idlePowerW: 2, windows: [
      { id: 'a', start: 0.1, end: 0.4 }, { id: 'b', start: 0.3, end: 0.6 },
      { id: 'c', start: 0.2, end: 0.3 }, { id: 'd', start: 0.1, end: 0.4 },
      { id: 'e', start: 0.6, end: 0.7 },
    ] })] });
    expect(calculateBudget(s, orbit).totalWh).toBeCloseTo((10 * 60 + 2 * 40) / 3600, 14);
  });
  it('finds simultaneous peaks including arbitrarily narrow pulses', () => {
    const s = scenario({ loads: [load({ id: 'a', activePowerW: 3 }), load({ id: 'b', activePowerW: 1000, idlePowerW: 0,
      windows: [{ id: 'pulse', start: 0.234567, end: 0.234568 }] })] });
    const result = calculateBudget(s, orbit);
    expect(result.peakW).toBe(1003);
    expect(result.totalWh).toBeCloseTo((300 + 1000 * 0.0001) / 3600, 12);
  });
  it('handles empty loads, zero-length windows and active below idle', () => {
    expect(calculateBudget(scenario({ loads: [] }), orbit).totalWh).toBe(0);
    const s = scenario({ loads: [load({ activePowerW: 0, idlePowerW: 10,
      windows: [{ id: 'empty', start: 0.1, end: 0.1 }, { id: 'off', start: 0.2, end: 0.4 }] })] });
    expect(calculateBudget(s, orbit).totalWh).toBeCloseTo(800 / 3600, 14);
  });
  it.each([
    { start: -0.1, end: 0.5 }, { start: 0.5, end: 1.1 }, { start: 0.9, end: 0.2 }, { start: NaN, end: 0.5 },
  ])('rejects unsupported windows %s', window => {
    expect(() => calculateBudget(scenario({ loads: [load({ windows: [{ id: 'bad', ...window }] })] }), orbit)).toThrow();
  });
  it('rejects nonfinite or negative power and inconsistent orbit partitions', () => {
    expect(() => calculateBudget(scenario({ loads: [load({ activePowerW: -1 })] }), orbit)).toThrow(/active power/);
    expect(() => calculateBudget(scenario({ loads: [load({ idlePowerW: Infinity })] }), orbit)).toThrow(/idle power/);
    expect(() => calculateBudget(scenario(), { ...orbit, sunlightS: 50 })).toThrow(/close/);
  });
});

describe('preliminary sizing boundaries', () => {
  it('uses Wh/h and Xs/Xe once, then rounds a cell count upward', () => {
    const i = inputs();
    const budget = calculateBudget(i.scenarios[0], orbit);
    const result = sizeSolar(i, budget, orbit);
    const expected = (budget.sunlightWh / 0.8 + budget.eclipseWh / 0.6) / (60 / 3600);
    expect(result.minimumPowerW).toBeCloseTo(expected, 13);
    expect(result.cellPowerW).toBe(1);
    expect(result.rawCellCount).toBeCloseTo(expected, 13);
    expect(result.cellCount).toBe(Math.ceil(expected));
    i.topology.efficiency = 0.1;
    expect(sizeSolar(i, budget, orbit)).toEqual(result);
  });
  it('applies M once in sizing, fE once to physical capacity, and declares mission cycles', () => {
    const i = inputs();
    const budget = calculateBudget(i.scenarios[0], orbit);
    const result = sizeBattery(i, budget, orbit);
    expect(result.requiredWh).toBeCloseTo(budget.eclipseWh / 0.25 * 1.2, 14);
    expect(result.eolCapacityWh).toBe(80);
    expect(result.cycles).toBe(2 * 365.25 * 864);
    i.battery.margin = 0.6;
    expect(sizeBattery(i, budget, orbit).eolCapacityWh).toBe(80);
  });
  it('does not invent cycle-life coefficients to choose DoD', () => {
    const i = inputs();
    i.battery.dod = null;
    expect(() => sizeBattery(i, calculateBudget(i.scenarios[0], orbit), orbit)).toThrow(/DoD/);
  });
  it.each([0, -0.1, 1.1, NaN, null])('rejects invalid path efficiency %s', value => {
    const i = inputs();
    i.solar.sunlightEfficiency = value;
    expect(() => sizeSolar(i, calculateBudget(i.scenarios[0], orbit), orbit)).toThrow(/Xs/);
  });
  it('rejects invalid sizing inputs; physical capability is independently gated by simulation', () => {
    const i = inputs();
    i.battery.margin = -1;
    expect(() => sizeBattery(i, calculateBudget(i.scenarios[0], orbit), orbit)).toThrow(/margin/);
    i.battery.margin = 0.2;
    const expected = sizeBattery(i, calculateBudget(i.scenarios[0], orbit), orbit).requiredWh;
    for (const field of ['retainedEnergy', 'capacityWh'] as const) {
      const invalid = inputs();
      invalid.battery[field] = -1;
      const sizing = sizeBattery(invalid, calculateBudget(invalid.scenarios[0], orbit), orbit);
      expect(sizing.requiredWh).toBe(expected);
      expect(sizing.eolCapacityWh).toBeNull();
      expect(() => simulateOrbit(invalid, invalid.scenarios[0], orbit)).toThrow();
    }
    i.mission.lifetimeYears = null;
    expect(() => sizeBattery(i, calculateBudget(i.scenarios[0], orbit), orbit)).toThrow(/lifetime/);
  });
  it('sizes requirements without installed pack/cell characterization', () => {
    const i = inputs();
    const budget = calculateBudget(i.scenarios[0], orbit);
    const required = sizeBattery(i, budget, orbit);
    Object.assign(i.battery, { capacityWh: null, retainedEnergy: null, chargeEfficiency: null, dischargeEfficiency: null, maxChargeW: null, maxDischargeW: null });
    expect(sizeBattery(i, budget, orbit)).toEqual({ ...required, eolCapacityWh: null });
    i.solar.cellEolV = null;
    const solar = sizeSolar(i, budget, orbit);
    expect(solar.minimumPowerW).toBeGreaterThan(0);
    expect(solar.cellPowerW).toBeNull();
    expect(solar.cellCount).toBeNull();
    expect(solar.rawCellCount).toBeNull();
  });
  it('includes the additional EPS baseline exactly in budget energy and peaks', () => {
    const s = scenario();
    const loadsOnly = calculateBudget(s, orbit);
    const withEps = calculateBudget(s, orbit, 1.25);
    expect(withEps.sunlightWh - loadsOnly.sunlightWh).toBeCloseTo(1.25 * orbit.sunlightS / 3600, 14);
    expect(withEps.eclipseWh - loadsOnly.eclipseWh).toBeCloseTo(1.25 * orbit.eclipseS / 3600, 14);
    expect(withEps.peakW - loadsOnly.peakW).toBe(1.25);
    expect(withEps.additionalEpsPowerW).toBe(1.25);
    expect(() => calculateBudget(s, orbit, -1)).toThrow(/EPS/);
    expect(() => calculateBudget(s, orbit, null as unknown as number)).toThrow(/EPS/);
  });
});
