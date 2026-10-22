import type { NodeId, Workspace } from "../types";
import { number } from "./ui";

export interface EngineeringExchange {
  label: string;
  description: string;
  principal?: boolean;
}
type ExchangeKey = `${NodeId}:${NodeId}`;
const EXCHANGES: Partial<Record<ExchangeKey, EngineeringExchange>> = {
  "mission:orbit": {
    label: "h",
    description: "Mission altitude h for circular orbit geometry.",
    principal: true,
  },
  "mission:battery": {
    label: "Lifetime",
    description: "Mission lifetime for the required number of battery cycles.",
    principal: true,
  },
  "orbit:budget": {
    label: "Ts / Te",
    description:
      "Orbital period and sunlight/eclipse intervals for phase-resolved integration.",
    principal: true,
  },
  "scenarios:budget": {
    label: "Schedules",
    description:
      "Active and idle load powers, rail assumptions, and the union of active windows.",
    principal: true,
  },
  "budget:solar": {
    label: "Es / Ee",
    description:
      "Sunlight and eclipse energy demand. The orbit supplies Ts for preliminary source power sizing.",
    principal: true,
  },
  "budget:battery": {
    label: "Ee / peak",
    description:
      "Eclipse energy demand and the coincident power-budget peak. Capacity sizing uses eclipse energy.",
    principal: true,
  },
  "solar:topology": {
    label: "EOL cells",
    description:
      "Minimum source-boundary EOL power and the rounded-up cell count. No wiring is inferred.",
    principal: true,
  },
  "battery:topology": {
    label: "Wh / cycles",
    description:
      "Required battery energy, mission cycle demand, and the declared storage assumptions.",
    principal: true,
  },
  "solar:candidates": {
    label: "PV bound",
    description:
      "Preliminary generation and integer cell-count bounds for catalog screening.",
  },
  "battery:candidates": {
    label: "Storage",
    description:
      "Required energy and cycling demand for sourced battery screening.",
  },
  "topology:candidates": {
    label: "Topology",
    description:
      "Conditioning, power transfer, and bus choices to screen catalog capabilities.",
    principal: true,
  },
  "orbit:simulation": {
    label: "Orbit timing",
    description:
      "Period and illumination intervals used by the energy timeline.",
  },
  "scenarios:simulation": {
    label: "Load modes",
    description:
      "Scheduled load demand, illumination, initial energy, reserve, and assessment duration.",
  },
  "solar:simulation": {
    label: "EOL source",
    description:
      "Current solar sizing basis. Installed source power remains an explicit, separate engineer input.",
  },
  "battery:simulation": {
    label: "Energy limits",
    description:
      "Current battery sizing basis. The run uses installed capacity, retained energy, efficiencies, and power limits.",
  },
  "topology:simulation": {
    label: "Loss model",
    description:
      "Conditioning efficiency and separately accounted EPS idle consumption.",
  },
  "candidates:simulation": {
    label: "Catalog / roles",
    description:
      "Current catalog screen and explicit product role allocations. A catalog match is not qualification.",
    principal: true,
  },
  "candidates:assessment": {
    label: "Selections",
    description:
      "Sourced candidate evidence, missing properties, and selected role allocations.",
    principal: true,
  },
  "simulation:assessment": {
    label: "E(t)",
    description:
      "Stored energy histories, shortages, power-limit findings, and interval closure.",
    principal: true,
  },
};

export function engineeringExchange(
  source: NodeId,
  target: NodeId,
): EngineeringExchange {
  return (
    EXCHANGES[`${source}:${target}`] ?? {
      label: "Inputs",
      description: "Required current engineering inputs.",
    }
  );
}

/** Formats exchanged information only. All numerical results are supplied by the engine. */
export function exchangeValue(
  source: NodeId,
  target: NodeId,
  workspace: Workspace,
): string {
  const { inputs, analysis } = workspace;
  switch (source) {
    case "mission":
      return target === "battery"
        ? `${number(inputs.mission.lifetimeYears)} years`
        : `${number(inputs.mission.altitudeKm, 0)} km altitude`;
    case "orbit":
      return analysis.orbit
        ? `${number(analysis.orbit.sunlightS / 60)} min sun · ${number(analysis.orbit.eclipseS / 60)} min eclipse`
        : "Orbit intervals not calculated";
    case "scenarios": {
      const scenario = inputs.scenarios.find(
        (s) => s.id === inputs.activeScenarioId,
      );
      return scenario
        ? `${scenario.loads.length} loads · ${scenario.name} · r${scenario.revision}`
        : "No active operating case";
    }
    case "budget":
      return analysis.budget
        ? `${number(analysis.budget.sunlightWh, 2)} / ${number(analysis.budget.eclipseWh, 2)} Wh · ${number(analysis.budget.peakW, 2)} W peak`
        : "Phase energies and peak not calculated";
    case "solar":
      return analysis.solar
        ? `${number(analysis.solar.minimumPowerW, 2)} W minimum · ${analysis.solar.cellCount} cells minimum`
        : "EOL source bound not calculated";
    case "battery":
      return analysis.battery
        ? `${number(analysis.battery.requiredWh, 2)} Wh required · ${number(analysis.battery.cycles, 0)} cycles`
        : "Storage and cycle demand not calculated";
    case "topology":
      return `${inputs.topology.conditioning} · ${inputs.topology.distribution} · ${inputs.topology.bus} bus`;
    case "candidates":
      return analysis.suggestions
        ? `${analysis.suggestions.length} product screens with retained evidence gaps`
        : "Catalog screen not calculated";
    case "simulation":
      return analysis.simulation
        ? `${number(analysis.simulation.minEnergyWh, 2)} Wh minimum · ${number(analysis.simulation.closureWh, 2)} Wh closure`
        : "Energy history not calculated";
    case "assessment":
      return analysis.checks
        ? `${analysis.checks.filter((c) => c.verdict === "fail").length} failures · ${analysis.checks.filter((c) => c.verdict === "unassessed").length} unassessed`
        : "Requirement findings not calculated";
  }
}
