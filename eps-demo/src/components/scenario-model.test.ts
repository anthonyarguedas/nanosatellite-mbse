import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { createElement } from 'react';
import type { Load, LoadWindow, OrbitResult } from '../types';
import { EXAMPLE_SCENARIOS } from './scenario-fixtures';
import { ScenarioEditor } from './ScenarioEditor';
import {
  bounded, dutyFraction, loadPowerAt, mergedWindows, MIN_WINDOW_FRACTION,
  moveWindow, nextWindow, normalizeWindow, phasePercent, phaseTime, powerPreview,
  resizeWindow, windowLanes,
} from './scenario-model';

const window = (start: number, end: number, id = 'w'): LoadWindow => ({ id, start, end });
const load = (windows: LoadWindow[], activePowerW = 10, idlePowerW = 2): Load => ({
  id: 'load', name: 'Test load', subsystem: 'Test', color: '#f28669', railV: 5,
  activePowerW, idlePowerW, essential: false, windows,
});
const orbit: OrbitResult = { periodS: 5700, sunlightS: 3600, eclipseS: 2100, sunlightFraction: 3600 / 5700, orbitsPerDay: 86400 / 5700, psiRad: 0.4 };

describe('scenario window editing', () => {
  it('bounds finite editor values', () => {
    expect(bounded(NaN, 0, 1)).toBe(0);
    expect(bounded(Infinity, 0.1, 1)).toBe(0.1);
    expect(bounded(-1, 0, 1)).toBe(0);
    expect(bounded(2, 0, 1)).toBe(1);
  });
  it('normalizes out-of-range and zero-width windows', () => {
    for (const original of [window(-2, 4), window(1, 1), window(0.9, 0.2), window(NaN, Infinity)]) {
      const normalized = normalizeWindow(original);
      expect(normalized.start).toBeGreaterThanOrEqual(0);
      expect(normalized.end).toBeLessThanOrEqual(1);
      expect(normalized.end - normalized.start).toBeGreaterThanOrEqual(MIN_WINDOW_FRACTION - 1e-12);
      expect(normalized.id).toBe(original.id);
    }
  });
  it('moves while preserving duration at both orbit boundaries', () => {
    const original = window(0.2, 0.4);
    const before = { ...original };
    expect(moveWindow(original, -10).start).toBe(0);
    expect(moveWindow(original, -10).end).toBeCloseTo(0.2);
    expect(moveWindow(original, 10).start).toBeCloseTo(0.8);
    expect(moveWindow(original, 10).end).toBe(1);
    expect(original).toEqual(before);
  });
  it('never inverts or collapses a resized window', () => {
    const original = window(0.2, 0.4);
    expect(resizeWindow(original, 'start', -1).start).toBe(0);
    expect(resizeWindow(original, 'end', 4).end).toBe(1);
    expect(resizeWindow(original, 'start', 0.9).start).toBeCloseTo(0.399);
    expect(resizeWindow(original, 'end', -1).end).toBeCloseTo(0.201);
  });
  it('merges overlap and touching endpoints without mutating authorship', () => {
    const windows = [window(0.3, 0.5, 'a'), window(0.1, 0.4, 'b'), window(0.5, 0.6, 'c')];
    expect(mergedWindows(windows)).toEqual([{ start: 0.1, end: 0.6 }]);
    expect(windows.map((item) => item.id)).toEqual(['a', 'b', 'c']);
    expect(dutyFraction(windows)).toBeCloseTo(0.5);
  });
  it('bounds unions and ignores invalid and zero-length intervals', () => {
    expect(dutyFraction([window(-1, 0.1), window(0.8, 2), window(0.5, 0.5), window(NaN, 1)])).toBeCloseTo(0.3);
    expect(dutyFraction([])).toBe(0);
    expect(dutyFraction([window(0, 1), window(0, 1, 'b')])).toBe(1);
  });
  it('adds into the largest gap and rejects a fully scheduled orbit', () => {
    const added = nextWindow([window(0, 0.2), window(0.4, 0.5, 'b')]);
    expect(added?.start).toBeGreaterThanOrEqual(0.5);
    expect((added?.end ?? 0) - (added?.start ?? 0)).toBeCloseTo(0.12);
    expect(nextWindow([window(0, 1)])).toBeNull();
    expect(nextWindow([])).toEqual({ start: 0.44, end: 0.56 });
  });
  it('keeps overlapping windows separately reachable in visual lanes', () => {
    const layout = windowLanes([window(0.1, 0.4, 'a'), window(0.2, 0.3, 'b'), window(0.4, 0.5, 'c')]);
    expect(layout.count).toBe(2);
    expect(layout.lanes.get('a')).toBe(layout.lanes.get('c'));
    expect(layout.lanes.get('a')).not.toBe(layout.lanes.get('b'));
  });
});

describe('exact load demand preview', () => {
  it('active replaces idle, including when active is lower than idle', () => {
    expect(loadPowerAt(load([window(0.2, 0.4)]), 0.3)).toBe(10);
    expect(loadPowerAt(load([window(0.2, 0.4)]), 0.4)).toBe(2);
    expect(loadPowerAt(load([window(0.2, 0.4)], 1, 3), 0.3)).toBe(1);
  });
  it('counts overlapping windows once and integrates exact event boundaries', () => {
    const preview = powerPreview([load([window(0.1, 0.3), window(0.2, 0.4, 'b')])]);
    expect(preview.averageW).toBeCloseTo(2 + 8 * 0.3);
    expect(preview.peakW).toBe(10);
    expect(preview.segments).toEqual([
      { start: 0, end: 0.1, powerW: 2 }, { start: 0.1, end: 0.4, powerW: 10 }, { start: 0.4, end: 1, powerW: 2 },
    ]);
  });
  it('captures short peaks and coincident loads without sampling loss', () => {
    const preview = powerPreview([load([window(0.0001, 0.0002)]), { ...load([window(0, 1)], 5, 0), id: 'other' }]);
    expect(preview.peakW).toBe(15);
    expect(preview.averageW).toBeCloseTo(7.0008);
    expect(powerPreview([])).toEqual({ averageW: 0, peakW: 0, segments: [{ start: 0, end: 1, powerW: 0 }] });
  });
  it('formats fractions and actual orbit time', () => {
    expect(phasePercent(0.123)).toBe('12.3%');
    expect(phaseTime(0.25, 5700)).toBe('23:45');
  });
});

describe('synthetic authored profiles', () => {
  it('provides three distinct valid, explicitly synthetic profiles', () => {
    expect(EXAMPLE_SCENARIOS).toHaveLength(3);
    expect(new Set(EXAMPLE_SCENARIOS.map((item) => item.id)).size).toBe(3);
    for (const scenario of EXAMPLE_SCENARIOS) {
      expect(scenario.provenance).toMatch(/Synthetic, authored/);
      expect(scenario.initialEnergyFraction).toBeGreaterThan(scenario.minimumEnergyFraction);
      expect(scenario.illuminationFactor).toBeGreaterThan(0);
      expect(scenario.illuminationFactor).toBeLessThanOrEqual(1);
      const ids = scenario.loads.flatMap((item) => [item.id, ...item.windows.map((window) => window.id)]);
      expect(new Set(ids).size).toBe(ids.length);
      for (const component of scenario.loads) for (const window of component.windows) {
        expect(window.start).toBeGreaterThanOrEqual(0);
        expect(window.end).toBeLessThanOrEqual(1);
        expect(window.end).toBeGreaterThan(window.start);
      }
    }
  });
  it('has a 3–5 W nominal load budget and continuous OBC/ADCS/beacon', () => {
    const nominal = EXAMPLE_SCENARIOS[0];
    expect(powerPreview(nominal.loads).averageW).toBeCloseTo(4.214);
    expect(nominal.loads.slice(0, 3).every((load) => dutyFraction(load.windows) === 1)).toBe(true);
  });
  it('makes high demand impossible to replenish with even ideal continuous 12 W generation', () => {
    expect(powerPreview(EXAMPLE_SCENARIOS[1].loads).averageW).toBeGreaterThan(17);
  });
  it('limits the survival profile to explicitly essential low-light loads', () => {
    const survival = EXAMPLE_SCENARIOS[2];
    expect(survival.kind).toBe('survival');
    expect(survival.illuminationFactor).toBeLessThan(0.2);
    expect(survival.loads.every((load) => load.essential)).toBe(true);
    expect(powerPreview(survival.loads).averageW).toBeCloseTo(1.12);
  });
});

describe('editor contract rendering', () => {
  it('renders energy labels, accessible sliders, numeric controls and real time ticks', () => {
    const markup = renderToStaticMarkup(createElement(ScenarioEditor, { scenario: EXAMPLE_SCENARIOS[0], orbit, onChange: () => {} }));
    expect(markup).toContain('Initial energy fraction (%)');
    expect(markup).toContain('Minimum energy reserve fraction (%)');
    expect(markup).toContain('Imaging payload window 1 start (%)');
    expect(markup).toContain('role="slider"');
    expect(markup).toContain('23:45');
    expect(markup).not.toMatch(/NaN|undefined|SoC/);
  });
  it('works before orbit evaluation without inventing sunlight timing', () => {
    const markup = renderToStaticMarkup(createElement(ScenarioEditor, { scenario: EXAMPLE_SCENARIOS[0], onChange: () => {} }));
    expect(markup).toContain('evaluate orbit for sun/eclipse timing');
    expect(markup).not.toContain('scenario-sun-band');
  });
});
