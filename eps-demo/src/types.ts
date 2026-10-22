/** Shared contracts. Values in W, Wh, V, A, kg, m, seconds unless stated. */
export type Role = 'solar' | 'battery' | 'conditioning' | 'distribution' | 'processor' | 'software';
export type Verdict = 'pass' | 'fail' | 'unassessed' | 'not-applicable';
export type NodeId = 'mission' | 'orbit' | 'scenarios' | 'budget' | 'solar' | 'battery' | 'topology' | 'candidates' | 'simulation' | 'assessment';
export type NodeStatus = 'locked' | 'ready' | 'complete' | 'stale';
export type TabId = 'graph' | 'scenarios' | 'catalog' | 'assessments';
export interface Source {
  id: string;
  title: string;
  url: string;
  revision: string;
  location: string;
  retrievedAt: string;
}
export interface Specification {
  value: number | string | number[] | null;
  unit: string;
  meaning: 'minimum' | 'typical' | 'maximum' | 'nominal' | 'estimated' | 'specified';
  status: 'available' | 'missing' | 'not-applicable';
  original: string;
  conditions: string;
  sourceId: string | null;
  location: string;
  rationale?: string;
}
export interface Product {
  id: string;
  revision: string;
  manufacturer: string;
  name: string;
  partNumber: string;
  level: 'cell' | 'panel' | 'pack' | 'board' | 'software';
  roles: Role[];
  description: string;
  specs: Record<string, Specification>;
  sources: Source[];
  supportedConfigurations: string[];
  accountingBoundary: string;
  caveats: string[];
}
export interface Catalog {
  revision: string;
  products: Product[];
}
export interface LoadWindow { id: string; start: number; end: number }
/** Windows are fractions [0,1] of one orbit. Active power replaces idle power. */
export interface Load {
  id: string;
  name: string;
  subsystem: string;
  color: string;
  activePowerW: number;
  idlePowerW: number;
  railV: number;
  essential: boolean;
  windows: LoadWindow[];
}
export interface Scenario {
  id: string;
  name: string;
  kind: 'nominal' | 'survival';
  description: string;
  revision: number;
  illuminationFactor: number;
  initialEnergyFraction: number;
  minimumEnergyFraction: number;
  durationOrbits: number;
  loads: Load[];
  provenance: string;
}
export interface MissionAnalogueReceipt {
  missionId: string;
  missionName: string;
  missionRevision: string;
  missionStatus: 'flown' | 'study';
  missionEpoch: string;
  catalogueRevision: string;
  method: 'semantic-qwen' | 'lexical-tfidf';
  cosine: number;
  altitudeKm: number;
  parameterOriginal: string;
  parameterMeaning: string;
  parameterSourceIds: string[];
  acceptedAt: string;
  query: string;
  sources: Source[];
}
export interface DesignInputs {
  mission: { name: string; altitudeKm: number | null; lifetimeYears: number | null; conOps?: string; orbitSuggestion?: MissionAnalogueReceipt };
  scenarios: Scenario[];
  activeScenarioId: string;
  solar: {
    sunlightEfficiency: number | null;
    eclipseEfficiency: number | null;
    cellEolV: number | null;
    cellEolA: number | null;
    installedPowerW: number | null;
  };
  battery: {
    dod: number | null;
    margin: number | null;
    capacityWh: number | null;
    retainedEnergy: number | null;
    chargeEfficiency: number | null;
    dischargeEfficiency: number | null;
    maxChargeW: number | null;
    maxDischargeW: number | null;
  };
  topology: {
    conditioning: 'MPPT' | 'DET';
    distribution: 'centralized' | 'distributed';
    bus: 'regulated' | 'unregulated';
    efficiency: number | null;
    idlePowerW: number | null;
    massAllocationKg: number | null;
  };
}
export interface OrbitResult { periodS: number; sunlightS: number; eclipseS: number; orbitsPerDay: number; sunlightFraction: number; psiRad: number }
export interface BudgetResult { sunlightWh: number; eclipseWh: number; totalWh: number; averageW: number; peakW: number; samples: { phase: number; powerW: number }[]; orbitPeriodS?: number; sunlightFraction?: number; scenarioId?: string; scenarioRevision?: number }
export interface SolarResult { minimumPowerW: number; cellPowerW: number; cellCount: number; rawCellCount: number }
export interface BatteryResult { requiredWh: number; cycles: number; eolCapacityWh: number; dod: number }
export interface Check { id: string; title: string; verdict: Verdict; detail: string; equation?: string; scope?: string; sourceIds?: string[] }
export interface Suggestion {
  productId: string;
  role: 'solar' | 'battery' | 'conditioning';
  outcome: 'preliminary-match' | 'incomplete' | 'rejected';
  quantity: number;
  reason: string;
  checks: Check[];
  missing: string[];
}
export interface SimulationPoint { timeS: number; orbit: number; sunlight: boolean; generationW: number; demandW: number; batteryWh: number; energyPercent: number; surplusW: number }
export interface SimulationResult {
  scenarioId: string;
  scenarioRevision?: number;
  reserveWh?: number;
  durationS?: number;
  points: SimulationPoint[];
  minEnergyWh: number;
  startEnergyWh: number;
  endEnergyWh: number;
  capacityWh: number;
  closureWh: number;
  shortageWh: number;
  curtailedWh: number;
  stoppedAtS: number | null;
  checks: Check[];
  assumptions: string[];
}
export interface Analysis {
  orbit?: OrbitResult;
  budget?: BudgetResult;
  solar?: SolarResult;
  battery?: BatteryResult;
  suggestions?: Suggestion[];
  simulation?: SimulationResult;
  checks?: Check[];
}
export interface NodeRecord { revision: number; evaluatedRevision: number | null; evaluatedAt: string | null }
export interface Workspace {
  schemaVersion: 1;
  inputs: DesignInputs;
  records: Record<NodeId, NodeRecord>;
  analysis: Analysis;
  selections: Partial<Record<Role, string>>;
}
export interface NodeDefinition { id: NodeId; title: string; subtitle: string; stage: string; dependencies: NodeId[]; requirements: string[]; equation: string }
