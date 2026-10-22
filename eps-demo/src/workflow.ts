import type { DesignInputs, NodeDefinition, NodeId, NodeStatus, Workspace } from './types';

export const NODE_DEFINITIONS: NodeDefinition[] = [
  { id: 'mission', title: 'Mission definition', subtitle: 'Orbit & lifetime', stage: '01 / Mission', dependencies: [], requirements: [], equation: 'h [km], N_lifetime [years]' },
  { id: 'orbit', title: 'Orbit geometry', subtitle: 'Sunlight & eclipse', stage: '01 / Mission', dependencies: ['mission'], requirements: [], equation: 'Tₒ = 2π √((6378 + h)³ / 398601)' },
  { id: 'scenarios', title: 'Operating scenarios', subtitle: 'Load modes & duty cycles', stage: '01 / Mission', dependencies: [], requirements: ['EPS-07', 'EPS-10'], equation: 'E = ∫ P(mode, t) dt' },
  { id: 'budget', title: 'Power budget', subtitle: 'Phase-resolved demand', stage: '02 / Sizing', dependencies: ['orbit', 'scenarios'], requirements: ['EPS-07'], equation: 'Eₛ = ∫sun P dt, Eₑ = ∫eclipse P dt' },
  { id: 'solar', title: 'Solar array sizing', subtitle: 'EOL power & integer cells', stage: '02 / Sizing', dependencies: ['budget'], requirements: ['EPS-02'], equation: 'Pmin = (Eₛ/Xₛ + Eₑ/Xₑ) / Tₛ' },
  { id: 'battery', title: 'Battery sizing', subtitle: 'Capacity & mission cycles', stage: '02 / Sizing', dependencies: ['budget', 'mission'], requirements: ['EPS-08', 'EPS-09'], equation: 'Ebat = Eₑ / DoD × (1 + M)' },
  { id: 'topology', title: 'Power architecture', subtitle: 'Conditioning & transfer', stage: '03 / Architecture', dependencies: ['solar', 'battery'], requirements: ['EPS-01', 'EPS-04'], equation: 'Pᵢₙ = Pₒᵤₜ + Ploss' },
  { id: 'candidates', title: 'COTS suggestions', subtitle: 'Bounded catalog screening', stage: '03 / Architecture', dependencies: ['solar', 'battery', 'topology'], requirements: ['EPS-01', 'EPS-03', 'EPS-05'], equation: 'Enumerate → screen → retain evidence gaps' },
  { id: 'simulation', title: 'Orbital energy balance', subtitle: 'Stored energy over time', stage: '04 / Assessment', dependencies: ['orbit', 'scenarios', 'solar', 'battery', 'topology', 'candidates'], requirements: ['EPS-10', 'EPS-11', 'EPS-12'], equation: 'Eₖ₊₁ = Eₖ + (ηc Pch − Pdis / ηd) Δt' },
  { id: 'assessment', title: 'Requirement review', subtitle: 'Evidence & unresolved checks', stage: '04 / Assessment', dependencies: ['candidates', 'simulation'], requirements: ['EPS-01…20'], equation: 'Criterion → pass / fail / unassessed' },
];

export const NODE_IDS = NODE_DEFINITIONS.map(node => node.id);
export const NODE_BY_ID = Object.fromEntries(NODE_DEFINITIONS.map(node => [node.id, node])) as Record<NodeId, NodeDefinition>;

function bounded(value: unknown, name: string, lo: number, hi: number, exclusiveLo = false): string[] {
  return typeof value !== 'number' || !Number.isFinite(value) || (exclusiveLo ? value <= lo : value < lo) || value > hi
    ? [`${name} must be ${exclusiveLo ? 'greater than' : 'at least'} ${lo} and at most ${hi}.`]
    : [];
}

/** Only implemented model inputs are required here. Missing characterization remains an assessment gap. */
export function inputIssues(id: NodeId, inputs: DesignInputs): string[] {
  const scenario = inputs.scenarios.find(item => item.id === inputs.activeScenarioId);
  switch (id) {
    case 'mission': return [
      ...(!inputs.mission.name.trim() ? ['Enter a mission name.'] : []),
      ...bounded(inputs.mission.altitudeKm, 'Circular orbit altitude (km)', 0, 100000, true),
      ...bounded(inputs.mission.lifetimeYears, 'Mission lifetime (years)', 0, 100, true),
    ];
    case 'scenarios': {
      if (!scenario) return ['Create or select an operating scenario.'];
      const issues = [
        ...(!scenario.name.trim() ? ['Name the operating scenario.'] : []),
        ...bounded(scenario.initialEnergyFraction, 'Initial stored energy fraction', 0, 1),
        ...bounded(scenario.minimumEnergyFraction, 'Energy reserve fraction', 0, 1),
        ...bounded(scenario.illuminationFactor, 'Illumination factor', 0, 1),
        ...bounded(scenario.durationOrbits, 'Assessment duration (orbits)', 0, 10, true),
        ...(scenario.loads.length === 0 ? ['Add at least one load.'] : []),
      ];
      for (const load of scenario.loads) {
        issues.push(...bounded(load.activePowerW, `${load.name} active power (W)`, 0, 10000));
        issues.push(...bounded(load.idlePowerW, `${load.name} idle power (W)`, 0, 10000));
        issues.push(...bounded(load.railV, `${load.name} supply rail (V)`, 0, 1000, true));
        for (const window of load.windows) {
          if (!Number.isFinite(window.start) || !Number.isFinite(window.end) || window.start < 0 || window.end > 1 || window.end <= window.start) {
            issues.push(`${load.name} has an invalid active window. Use 0 ≤ start < end ≤ 1.`);
          }
        }
      }
      return issues;
    }
    case 'solar': return [
      ...bounded(inputs.solar.sunlightEfficiency, 'Sunlight path efficiency Xs', 0, 1, true),
      ...bounded(inputs.solar.eclipseEfficiency, 'Eclipse path efficiency Xe', 0, 1, true),
      ...bounded(inputs.solar.cellEolV, 'Cell EOL maximum-power voltage (V)', 0, 1000, true),
      ...bounded(inputs.solar.cellEolA, 'Cell EOL maximum-power current (A)', 0, 1000, true),
    ];
    case 'battery': return [
      ...bounded(inputs.battery.dod, 'Preliminary design DoD fraction', 0, 1, true),
      ...bounded(inputs.battery.margin, 'Preliminary degradation margin', 0, 10),
      ...bounded(inputs.battery.capacityWh, 'BOL battery capacity (Wh)', 0, 100000, true),
      ...bounded(inputs.battery.retainedEnergy, 'Retained energy fraction', 0, 1, true),
      ...bounded(inputs.battery.chargeEfficiency, 'Battery charging energy efficiency', 0, 1, true),
      ...bounded(inputs.battery.dischargeEfficiency, 'Battery discharging energy efficiency', 0, 1, true),
      ...bounded(inputs.battery.maxChargeW, 'Charge acceptance limit (W)', 0, 100000),
      ...bounded(inputs.battery.maxDischargeW, 'Discharge power limit (W)', 0, 100000),
    ];
    case 'topology': return [
      ...bounded(inputs.topology.efficiency, 'Conditioning efficiency', 0, 1, true),
      ...bounded(inputs.topology.idlePowerW, 'Aggregate EPS idle power (W)', 0, 10000),
      ...bounded(inputs.topology.massAllocationKg, 'EPS mass allocation (kg)', 0, 1000, true),
    ];
    case 'simulation': return [
      ...bounded(inputs.solar.installedPowerW, 'Installed source EOL power (W)', 0, 100000),
      ...(inputs.topology.conditioning === 'DET' ? ['DET simulation needs a characterized array I–V operating point. Select MPPT for this demo energy model.'] : []),
    ];
    default: return [];
  }
}

export function nodeStatuses(workspace: Workspace): Record<NodeId, NodeStatus> {
  const statuses = {} as Record<NodeId, NodeStatus>;
  for (const definition of NODE_DEFINITIONS) {
    const record = workspace.records[definition.id];
    const hasEvaluation = record.evaluatedRevision !== null;
    const dependenciesCurrent = definition.dependencies.every(id => statuses[id] === 'complete');
    const valid = inputIssues(definition.id, workspace.inputs).length === 0;
    if (hasEvaluation && (record.evaluatedRevision !== record.revision || !dependenciesCurrent || !valid)) statuses[definition.id] = 'stale';
    else if (!valid || !dependenciesCurrent) statuses[definition.id] = 'locked';
    else statuses[definition.id] = hasEvaluation ? 'complete' : 'ready';
  }
  return statuses;
}

export function missingForNodes(workspace: Workspace, statuses = nodeStatuses(workspace)): Record<NodeId, string[]> {
  return Object.fromEntries(NODE_DEFINITIONS.map(node => [node.id, [
    ...inputIssues(node.id, workspace.inputs),
    ...node.dependencies.filter(id => statuses[id] !== 'complete').map(id => `${NODE_BY_ID[id].title} is ${statuses[id]}. Evaluate it first.`),
  ]])) as Record<NodeId, string[]>;
}

export function descendants(id: NodeId): NodeId[] {
  const affected = new Set<NodeId>([id]);
  for (const node of NODE_DEFINITIONS) {
    if (node.dependencies.some(dependency => affected.has(dependency))) affected.add(node.id);
  }
  return [...affected];
}
