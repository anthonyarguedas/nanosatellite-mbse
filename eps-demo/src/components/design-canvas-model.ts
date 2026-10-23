import type { Catalog, DesignInputs, NodeId, NodeStatus, Role, Workspace } from '../types';
import { number, ROLES } from './ui';
import { getAllocationQuantity } from '../engine/allocations';
import { NODE_DEFINITIONS } from '../workflow';

export type VariationId = 'conditioning' | 'transfer' | 'bus' | 'outputs';
export interface CanvasSelection { node: NodeId | null; role?: Role; variation?: VariationId }
export type GraphLayout = 'wide' | 'compact' | 'narrow';
export const ACTIVITY_LABELS: Record<NodeId, string> = {
  mission: 'Define mission', orbit: 'Reference orbit', scenarios: 'Schedule loads', budget: 'Power budget',
  solar: 'Size solar arrays', battery: 'Size batteries', topology: 'Power topology', candidates: 'Compare products',
  simulation: 'Orbital energy', assessment: 'Assess evidence',
};
/** A sparse visual backbone. Every edge still comes from the controller definitions. */
const BACKBONE = new Set(['mission-orbit', 'orbit-budget', 'scenarios-budget', 'budget-solar', 'budget-battery',
  'solar-topology', 'battery-topology', 'topology-candidates', 'candidates-simulation', 'candidates-assessment']);
export function activityEdges() {
  return NODE_DEFINITIONS.flatMap(node => [
    ...node.dependencies.map(source => ({ id: `${source}-${node.id}`, source, target: node.id, kind: 'dependency' as const, primary: BACKBONE.has(`${source}-${node.id}`) })),
    ...(node.evidenceDependencies ?? []).map(source => ({ id: `${source}-${node.id}`, source, target: node.id, kind: 'evidence' as const, primary: true })),
  ]);
}
export function activityPositions(layout: GraphLayout): Record<NodeId, { x: number; y: number }> {
  const points: Record<GraphLayout, Record<NodeId, [number, number]>> = {
    wide: { mission: [0, 74], orbit: [190, 0], scenarios: [190, 170], budget: [380, 74], solar: [570, 0], battery: [570, 170], topology: [760, 74], candidates: [950, 74], simulation: [1140, 0], assessment: [1140, 170] },
    compact: { mission: [0, 0], orbit: [190, 0], scenarios: [0, 150], budget: [380, 75], solar: [570, 0], battery: [570, 150], topology: [760, 75], candidates: [760, 300], simulation: [570, 300], assessment: [380, 300] },
    narrow: { mission: [0, 0], orbit: [184, 0], scenarios: [0, 140], budget: [184, 140], solar: [0, 280], battery: [184, 280], topology: [0, 420], candidates: [184, 420], simulation: [0, 560], assessment: [184, 560] },
  };
  return Object.fromEntries(Object.entries(points[layout]).map(([id, [x, y]]) => [id, { x, y }])) as Record<NodeId, { x: number; y: number }>;
}
export function selectionRoles(selection: CanvasSelection, topology: DesignInputs['topology']): readonly Role[] {
  if (selection.role) return [selection.role];
  if (selection.variation) return variationPoints(topology).find(point => point.id === selection.variation)?.roles ?? [];
  return selection.node ? ACTIVITY_ROLES[selection.node] : [];
}

/** Presentation associations, not electrical connectivity or evaluation dependencies. */
export const ACTIVITY_ROLES: Record<NodeId, readonly Role[]> = {
  mission: ROLES, orbit: ['solar', 'battery'], scenarios: ['distribution', 'processor', 'software'],
  budget: ['solar', 'battery', 'distribution'], solar: ['solar'], battery: ['battery'],
  topology: ['solar', 'battery', 'conditioning', 'distribution'], candidates: ROLES,
  simulation: ['solar', 'battery', 'conditioning', 'distribution'], assessment: ROLES,
};
export const ROLE_NODES: Record<Role, NodeId> = {
  solar: 'solar', battery: 'battery', conditioning: 'topology', distribution: 'topology', processor: 'candidates', software: 'candidates',
};
export const ACTIVITY_GROUPS: { title: string; exchange: string; nodes: NodeId[] }[] = [
  { title: 'Define the mission', exchange: 'Orbit & operating context', nodes: ['mission', 'orbit'] },
  { title: 'Model demand', exchange: 'Sunlight & eclipse energy', nodes: ['scenarios', 'budget'] },
  { title: 'Size generation & storage', exchange: 'Preliminary sizing bounds', nodes: ['solar', 'battery'] },
  { title: 'Configure alternatives', exchange: 'Topology & allocations', nodes: ['topology', 'candidates'] },
  { title: 'Assess the design', exchange: 'Findings return to inputs', nodes: ['simulation', 'assessment'] },
];
export const ACTIVITY_TITLES: Record<NodeId, string> = {
  mission: 'Define mission & ConOps', orbit: 'Analyze reference orbit', scenarios: 'Schedule mission loads', budget: 'Construct power budget',
  solar: 'Size solar arrays', battery: 'Size batteries', topology: 'Define power topology', candidates: 'Compare COTS products',
  simulation: 'Simulate orbital energy', assessment: 'Assess margins & evidence',
};
export const CSRM_SUBSYSTEMS = [
  'Mission Payload', 'Command and Data Handling', 'Communication', 'Attitude Determination and Control',
  'Guidance Navigation and Control', 'Structures and Mechanisms', 'Power (EPS)', 'Propulsion', 'Thermal',
] as const;

export function activityValue(id: NodeId, workspace: Workspace): string {
  const { inputs: i, analysis: a } = workspace;
  switch (id) {
    case 'mission': return i.mission.altitudeKm === null ? 'Set altitude & lifetime' : `${number(i.mission.altitudeKm, 0)} km · ${number(i.mission.lifetimeYears)} yr`;
    case 'orbit': return a.orbit ? `${number(a.orbit.sunlightS / 60)} min sun · ${number(a.orbit.eclipseS / 60)} min eclipse` : 'Circular reference geometry';
    case 'scenarios': return `${i.scenarios.find(s => s.id === i.activeScenarioId)?.loads.length ?? 0} scheduled loads · ${i.scenarios.length} cases`;
    case 'budget': return a.budget ? `${number(a.budget.averageW, 2)} W average · ${number(a.budget.peakW, 2)} W peak` : 'Integrate scheduled demand';
    case 'solar': return a.solar ? `${number(a.solar.minimumPowerW, 2)} W minimum · ${a.solar.cellCount === null ? 'cell count unresolved' : `${a.solar.cellCount} cells min.`}` : 'EOL generation screen';
    case 'battery': return a.battery ? `${number(a.battery.requiredWh, 2)} Wh required` : 'Eclipse storage screen';
    case 'topology': return `${i.topology.conditioning} · ${i.topology.distribution} transfer`;
    case 'candidates': {
      if (!a.suggestions) return 'Browse sourced alternatives';
      const count = new Set(a.suggestions.filter(s => s.outcome !== 'rejected').map(s => s.productId)).size;
      return `${count} ${count === 1 ? 'product' : 'products'}, including incomplete`;
    }
    case 'simulation': return a.simulation ? `${number(a.simulation.minEnergyWh, 2)} Wh minimum stored energy` : 'Energy-only time history';
    case 'assessment': return a.checks ? `${a.checks.filter(c => c.verdict === 'fail').length} fail · ${a.checks.filter(c => c.verdict === 'unassessed').length} unassessed` : 'EPS-01–20 · not evaluated';
  }
}

export function roleValue(role: Role, workspace: Workspace): string {
  const { inputs: i, analysis: a } = workspace;
  switch (role) {
    case 'solar': return a.solar ? `${number(a.solar.minimumPowerW, 2)} W minimum EOL source` : 'Generation not sized';
    case 'battery': return a.battery ? `${number(a.battery.requiredWh, 2)} Wh preliminary requirement` : 'Storage not sized';
    case 'conditioning': return `${i.topology.conditioning} · ${i.topology.bus === 'regulated' ? 'regulated-bus intent' : 'unregulated-bus intent'}`;
    case 'distribution': return `${i.topology.distribution === 'centralized' ? 'Centralized' : 'Distributed'} transfer intent`;
    case 'processor': return 'Host resources & timing unassessed';
    case 'software': return 'Services & host compatibility unassessed';
  }
}

/** A shared board is one product usage, never one board per logical role.
 * Screening counts deliberately do not enter this view: they are not installed quantities. */
export function allocationGroups(workspace: Workspace, catalog: Catalog) {
  const ids = [...new Set(ROLES.map(role => workspace.selections[role]).filter((id): id is string => Boolean(id)))];
  return ids.map((id, index) => ({
    id, ref: `U${String(index + 1).padStart(2, '0')}`,
    product: catalog.products.find(product => product.id === id),
    roles: ROLES.filter(role => workspace.selections[role] === id),
    quantity: getAllocationQuantity(workspace, id),
    receipt: workspace.allocations?.find(receipt => receipt.productId === id),
  }));
}

export interface VariationPoint {
  id: VariationId;
  title: string;
  association: string;
  roles: Role[];
  options: { label: string; selected: boolean; represented: boolean }[];
  note?: string;
}
export function variationPoints(topology: DesignInputs['topology']): VariationPoint[] {
  return [
    { id: 'conditioning', title: 'Power conditioning', association: 'Array operating point · conditioning stages', roles: ['solar', 'conditioning'], options: [
      { label: 'DET', selected: topology.conditioning === 'DET', represented: true }, { label: 'MPPT', selected: topology.conditioning === 'MPPT', represented: true },
    ], note: topology.conditioning === 'DET' ? 'DET energy propagation needs an array I–V operating-point model.' : undefined },
    { id: 'transfer', title: 'Energy transfer', association: 'Stage & circuit placement', roles: ['conditioning', 'distribution'], options: [
      { label: 'Centralized', selected: topology.distribution === 'centralized', represented: true }, { label: 'Distributed', selected: topology.distribution === 'distributed', represented: true },
    ] },
    { id: 'bus', title: 'DC bus regulation', association: 'Battery / bus coupling · regulation', roles: ['battery', 'conditioning'], options: [
      { label: 'Unregulated', selected: topology.bus === 'unregulated', represented: true },
      { label: 'Regulated intent', selected: topology.bus === 'regulated', represented: true },
      { label: 'Partially regulated', selected: false, represented: false },
      { label: 'Fully regulated', selected: false, represented: false },
    ], note: 'Regulated intent does not specify partially or fully regulated rails.' },
    { id: 'outputs', title: 'Per-output supply', association: 'Load conversion · output switching', roles: ['conditioning', 'distribution'], options: [
      { label: 'Direct bus', selected: false, represented: false }, { label: 'DC–DC converted', selected: false, represented: false },
    ], note: 'Can coexist in the report; not represented per rail in this demo.' },
  ];
}

export function savedPrefix(status: NodeStatus, calculated: boolean): string {
  return calculated && status !== 'complete' ? 'Saved · ' : '';
}
export function hasResult(id: NodeId, w: Workspace): boolean {
  return Boolean(({ orbit: w.analysis.orbit, budget: w.analysis.budget, solar: w.analysis.solar, battery: w.analysis.battery,
    candidates: w.analysis.suggestions, simulation: w.analysis.simulation, assessment: w.analysis.checks } as Partial<Record<NodeId, unknown>>)[id]);
}
