import type {
  BudgetResult,
  OrbitResult,
  Scenario,
  SimulationResult,
} from "../types";

/** Presentation basis belongs to the saved result, not the next run's edited inputs. */
export function budgetPlotBasis(budget: BudgetResult, orbit?: OrbitResult) {
  return {
    periodS: budget.orbitPeriodS ?? orbit?.periodS,
    sunlightFraction: budget.sunlightFraction ?? orbit?.sunlightFraction,
    legacyTiming: budget.orbitPeriodS === undefined,
  };
}

export function simulationPlotBasis(
  simulation: SimulationResult,
  scenario?: Scenario,
) {
  const reserveWh =
    simulation.reserveWh ??
    (scenario
      ? scenario.minimumEnergyFraction * simulation.capacityWh
      : undefined);
  return {
    reserveWh,
    reservePercent:
      reserveWh !== undefined && simulation.capacityWh > 0
        ? (reserveWh / simulation.capacityWh) * 100
        : undefined,
    initialPercent:
      simulation.capacityWh > 0
        ? (simulation.startEnergyWh / simulation.capacityWh) * 100
        : undefined,
    durationS: simulation.durationS ?? simulation.points.at(-1)?.timeS ?? 0,
    legacyReserve: simulation.reserveWh === undefined,
  };
}

export function savedCaseLabel(id?: string, revision?: number) {
  return `${id ?? "Case identity not recorded"} · ${revision === undefined ? "revision not recorded" : `revision ${revision}`}`;
}
