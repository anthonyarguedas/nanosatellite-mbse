import { describe, expect, it } from "vitest";
import type {
  BudgetResult,
  OrbitResult,
  Scenario,
  SimulationResult,
} from "../types";
import {
  budgetPlotBasis,
  savedCaseLabel,
  simulationPlotBasis,
} from "./result-history";

const orbit: OrbitResult = {
  periodS: 6000,
  sunlightS: 4200,
  eclipseS: 1800,
  orbitsPerDay: 14.4,
  sunlightFraction: 0.7,
  psiRad: 0,
};
const budget: BudgetResult = {
  sunlightWh: 0.6,
  eclipseWh: 0.4,
  totalWh: 1,
  averageW: 0.6,
  peakW: 3,
  samples: [],
  orbitPeriodS: 5550,
  sunlightFraction: 0.61,
  scenarioId: "birds4-routine",
  scenarioRevision: 1,
};
const scenario: Scenario = {
  id: "birds4-routine",
  name: "Edited case name",
  kind: "nominal",
  revision: 2,
  description: "Authored assumptions",
  illuminationFactor: 1,
  initialEnergyFraction: 0.4,
  minimumEnergyFraction: 0.9,
  durationOrbits: 3,
  loads: [],
  provenance: "Test fixture",
};
const simulation: SimulationResult = {
  scenarioId: "birds4-routine",
  scenarioRevision: 1,
  reserveWh: 1.6,
  durationS: 5550,
  points: [],
  minEnergyWh: 3,
  startEnergyWh: 4.608,
  endEnergyWh: 4.7,
  capacityWh: 6.4,
  closureWh: 0.092,
  shortageWh: 0,
  curtailedWh: 0,
  stoppedAtS: null,
  checks: [],
  assumptions: [],
};

describe("saved result presentation basis", () => {
  it("retains original orbit mapping after the orbit inputs are edited", () => {
    expect(budgetPlotBasis(budget, orbit)).toEqual({
      periodS: 5550,
      sunlightFraction: 0.61,
      legacyTiming: false,
    });
  });
  it("retains the original reserve, initial energy, duration and revision after scenario edits", () => {
    const basis = simulationPlotBasis(simulation, scenario);
    expect(basis.reserveWh).toBe(1.6);
    expect(basis.reservePercent).toBeCloseTo(25);
    expect(basis.initialPercent).toBeCloseTo(72);
    expect(basis.durationS).toBe(5550);
    expect(basis.legacyReserve).toBe(false);
    expect(
      savedCaseLabel(simulation.scenarioId, simulation.scenarioRevision),
    ).toBe("birds4-routine · revision 1");
  });
  it("keeps the full requested interval even when the history stopped early", () => {
    const stopped = {
      ...simulation,
      stoppedAtS: 2000,
      points: [
        {
          timeS: 2000,
          orbit: 0,
          sunlight: false,
          generationW: 0,
          demandW: 2,
          batteryWh: 0,
          energyPercent: 0,
          surplusW: -2,
        },
      ],
    };
    expect(simulationPlotBasis(stopped, scenario).durationS).toBe(5550);
  });
  it("uses explicit legacy flags when old fixtures need current-prop fallbacks", () => {
    expect(
      budgetPlotBasis(
        { ...budget, orbitPeriodS: undefined, sunlightFraction: undefined },
        orbit,
      ),
    ).toEqual({ periodS: 6000, sunlightFraction: 0.7, legacyTiming: true });
    const basis = simulationPlotBasis(
      { ...simulation, reserveWh: undefined, durationS: undefined },
      scenario,
    );
    expect(basis.reservePercent).toBeCloseTo(90);
    expect(basis.legacyReserve).toBe(true);
  });
  it("keeps a stored zero reserve rather than replacing it with a new criterion", () => {
    expect(
      simulationPlotBasis({ ...simulation, reserveWh: 0 }, scenario)
        .reservePercent,
    ).toBe(0);
  });
  it("leaves missing history criteria explicit when no fallback exists", () => {
    expect(
      simulationPlotBasis({ ...simulation, reserveWh: undefined }).reserveWh,
    ).toBeUndefined();
    expect(savedCaseLabel()).toContain("not recorded");
  });
});
