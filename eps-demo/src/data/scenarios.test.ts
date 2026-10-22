import { describe, expect, it } from 'vitest';
import { BIRDS4_SOURCE, EXAMPLE_SCENARIOS } from './scenarios';
import { calculateBudget, calculateOrbit } from '../engine';

 describe('BIRDS-4-inspired authored cases', () => {
  it('keeps the source and assumption boundary in every scenario', () => {
    expect(BIRDS4_SOURCE.url).toBe('https://nanosat11th.itu.edu.tr/assets/papers/BIRDS-4.pdf');
    expect(EXAMPLE_SCENARIOS).toHaveLength(3);
    for (const scenario of EXAMPLE_SCENARIOS) {
      expect(scenario.name).toContain('BIRDS-4');
      expect(scenario.provenance).toMatch(/demo assumptions/);
      expect(scenario.provenance).toMatch(/not a reconstruction/);
      expect(scenario.provenance).toContain(BIRDS4_SOURCE.url);
      expect(new Set(scenario.loads.map(load => load.id)).size).toBe(scenario.loads.length);
    }
  });
  it('integrates the exact authored routine and stress powers', () => {
    const orbit = calculateOrbit(400);
    const routine = calculateBudget(EXAMPLE_SCENARIOS[0], orbit);
    expect(routine.averageW).toBeCloseTo(0.6645, 10);
    expect(routine.peakW).toBeCloseTo(3.34, 10);
    const stress = calculateBudget(EXAMPLE_SCENARIOS[1], orbit);
    expect(stress.averageW).toBeCloseTo(2.8165, 10);
    expect(stress.peakW).toBeCloseTo(5.2, 10);
  });
  it('manually schedules essential-only service without inventing a recovery controller', () => {
    const survival = EXAMPLE_SCENARIOS[2];
    expect(survival.kind).toBe('survival');
    expect(survival.durationOrbits).toBe(3);
    expect(survival.description).toContain('No automatic recovery');
    for (const load of survival.loads.filter(item => !item.essential)) {
      expect(load.activePowerW).toBe(0);
      expect(load.idlePowerW).toBe(0);
      expect(load.windows).toHaveLength(0);
    }
  });
});
