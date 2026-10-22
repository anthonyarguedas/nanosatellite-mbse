import type { DesignInputs, Load, MissionAnalogueReceipt, Role, Scenario, Source, Workspace } from '../types';

const ROLES: Role[] = ['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software'];
type Dict = Record<string, unknown>;
function object(value: unknown, label: string): Dict {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} must be an object.`);
  return value as Dict;
}
function text(value: unknown, label: string, max = 2000): string {
  if (typeof value !== 'string' || value.length > max) throw new Error(`${label} must be text (up to ${max} characters).`);
  return value;
}
function number(value: unknown, label: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error(`${label} must be a finite number.`);
  return value;
}
function nullable(value: unknown, label: string): number | null { return value === null ? null : number(value, label); }
function enumeration<T extends string>(value: unknown, options: readonly T[], label: string): T {
  if (!options.includes(value as T)) throw new Error(`${label} must be one of ${options.join(', ')}.`);
  return value as T;
}
function array(value: unknown, label: string, max: number): unknown[] {
  if (!Array.isArray(value) || value.length > max) throw new Error(`${label} must be a list of at most ${max} items.`);
  return value;
}
function unique(ids: string[], label: string) {
  if (ids.some(id => !id) || new Set(ids).size !== ids.length) throw new Error(`${label} must have unique, nonempty identifiers.`);
}
function orbitReceipt(value: unknown): MissionAnalogueReceipt {
  const item = object(value, 'Accepted orbit source');
  const sources: Source[] = array(item.sources, 'Orbit evidence sources', 20).map(value => {
    const source = object(value, 'Orbit evidence source');
    const url = text(source.url, 'Orbit source URL');
    try { if (!['http:', 'https:'].includes(new URL(url).protocol)) throw new Error(); }
    catch { throw new Error('Orbit evidence sources require valid HTTP(S) URLs.'); }
    return {
      id: text(source.id, 'Source ID', 200), title: text(source.title, 'Source title'), url,
      revision: text(source.revision, 'Source revision'), location: text(source.location, 'Source location'),
      retrievedAt: text(source.retrievedAt, 'Source retrieval date', 100),
    };
  });
  unique(sources.map(source => source.id), 'Orbit evidence sources');
  if (!sources.length || sources.some(source => !source.title.trim() || !source.revision.trim() || !source.location.trim())) throw new Error('The accepted orbit needs complete source identity, revision and location.');
  const parameterSourceIds = array(item.parameterSourceIds, 'Altitude source references', 20).map(value => text(value, 'Altitude source ID', 200));
  unique(parameterSourceIds, 'Altitude source references');
  if (!parameterSourceIds.length || parameterSourceIds.some(id => !sources.some(source => source.id === id))) throw new Error('The accepted altitude source reference is unresolved.');
  const cosine = number(item.cosine, 'Analogue cosine');
  const altitudeKm = number(item.altitudeKm, 'Accepted altitude');
  const acceptedAt = text(item.acceptedAt, 'Acceptance time', 100);
  if (cosine < -1 || cosine > 1 || altitudeKm <= 0 || altitudeKm > 100000 || Number.isNaN(Date.parse(acceptedAt))) throw new Error('The accepted orbit receipt has an invalid score, altitude or date.');
  return {
    missionId: text(item.missionId, 'Analogue mission ID', 200), missionName: text(item.missionName, 'Analogue mission name', 200),
    missionRevision: text(item.missionRevision, 'Analogue revision'), missionStatus: enumeration(item.missionStatus, ['flown', 'study'], 'Analogue status'),
    missionEpoch: text(item.missionEpoch, 'Parameter epoch'), catalogueRevision: text(item.catalogueRevision, 'Mission catalogue revision'),
    method: enumeration(item.method, ['semantic-qwen', 'lexical-tfidf'], 'Analogue retrieval method'), cosine, altitudeKm,
    parameterOriginal: text(item.parameterOriginal, 'Original altitude representation'), parameterMeaning: text(item.parameterMeaning, 'Altitude interpretation'), parameterSourceIds,
    acceptedAt, query: text(item.query, 'Accepted ConOps'), sources,
  };
}
function load(value: unknown): Load {
  const item = object(value, 'Load');
  const windows = array(item.windows, 'Load windows', 100).map(value => {
    const window = object(value, 'Active window');
    return { id: text(window.id, 'Window ID', 100), start: number(window.start, 'Window start'), end: number(window.end, 'Window end') };
  });
  unique(windows.map(item => item.id), 'Load windows');
  if (typeof item.essential !== 'boolean') throw new Error('Essential-load flag must be Boolean.');
  return {
    id: text(item.id, 'Load ID', 100), name: text(item.name, 'Load name', 200),
    subsystem: text(item.subsystem, 'Subsystem name', 200), color: /^#[\da-fA-F]{6}$/.test(String(item.color)) ? String(item.color) : '#7fa9c6',
    activePowerW: number(item.activePowerW, 'Active power'), idlePowerW: number(item.idlePowerW, 'Idle power'),
    railV: number(item.railV, 'Supply rail'), essential: item.essential, windows,
  };
}
function scenario(value: unknown): Scenario {
  const item = object(value, 'Scenario');
  const loads = array(item.loads, 'Scenario loads', 100).map(load);
  unique(loads.map(item => item.id), 'Scenario loads');
  return {
    id: text(item.id, 'Scenario ID', 100), name: text(item.name, 'Scenario name', 200),
    kind: enumeration(item.kind, ['nominal', 'survival'], 'Scenario kind'),
    description: text(item.description, 'Scenario description'), revision: number(item.revision, 'Scenario revision'),
    illuminationFactor: number(item.illuminationFactor, 'Illumination factor'),
    initialEnergyFraction: number(item.initialEnergyFraction, 'Initial energy'),
    minimumEnergyFraction: number(item.minimumEnergyFraction, 'Minimum energy'),
    durationOrbits: number(item.durationOrbits, 'Duration'), loads, provenance: text(item.provenance, 'Scenario provenance'),
  };
}

/** Reconstruct known fields only. Imported calculation caches are deliberately discarded. */
export function parseWorkspace(raw: unknown): { inputs: DesignInputs; selections: Partial<Record<Role, string>> } {
  const root = object(raw, 'Design file');
  if (root.schemaVersion !== 1) throw new Error('Unsupported design file. Expected Orbitwork schemaVersion 1.');
  const inputs = object(root.inputs, 'Design inputs');
  const mission = object(inputs.mission, 'Mission');
  const solar = object(inputs.solar, 'Solar inputs');
  const battery = object(inputs.battery, 'Battery inputs');
  const topology = object(inputs.topology, 'Topology inputs');
  const parsedMission: DesignInputs['mission'] = { name: text(mission.name, 'Mission name', 200), altitudeKm: nullable(mission.altitudeKm, 'Altitude'), lifetimeYears: nullable(mission.lifetimeYears, 'Lifetime') };
  if (mission.conOps !== undefined) parsedMission.conOps = text(mission.conOps, 'Mission ConOps');
  if (mission.orbitSuggestion !== undefined) {
    parsedMission.orbitSuggestion = orbitReceipt(mission.orbitSuggestion);
    if (parsedMission.orbitSuggestion.altitudeKm !== parsedMission.altitudeKm || parsedMission.orbitSuggestion.query !== (parsedMission.conOps ?? '')) throw new Error('The accepted orbit receipt does not match the mission altitude or ConOps. Review the source before importing.');
  }
  const scenarios = array(inputs.scenarios, 'Scenarios', 20).map(scenario);
  unique(scenarios.map(item => item.id), 'Scenarios');
  const activeScenarioId = text(inputs.activeScenarioId, 'Active scenario ID', 100);
  if (activeScenarioId && !scenarios.some(item => item.id === activeScenarioId)) throw new Error('Active scenario is absent from the scenario list.');
  const selection = object(root.selections ?? {}, 'Product selections');
  const selections: Partial<Record<Role, string>> = {};
  for (const role of ROLES) if (selection[role] !== undefined) selections[role] = text(selection[role], 'Product ID', 200);
  return {
    inputs: {
      mission: parsedMission,
      scenarios, activeScenarioId,
      solar: {
        sunlightEfficiency: nullable(solar.sunlightEfficiency, 'Sunlight efficiency'), eclipseEfficiency: nullable(solar.eclipseEfficiency, 'Eclipse efficiency'),
        cellEolV: nullable(solar.cellEolV, 'Cell EOL voltage'), cellEolA: nullable(solar.cellEolA, 'Cell EOL current'), installedPowerW: nullable(solar.installedPowerW, 'Installed EOL power'),
      },
      battery: {
        dod: nullable(battery.dod, 'Design DoD'), margin: nullable(battery.margin, 'Sizing margin'), capacityWh: nullable(battery.capacityWh, 'Battery capacity'),
        retainedEnergy: nullable(battery.retainedEnergy, 'Retained energy'), chargeEfficiency: nullable(battery.chargeEfficiency, 'Charging efficiency'),
        dischargeEfficiency: nullable(battery.dischargeEfficiency, 'Discharging efficiency'), maxChargeW: nullable(battery.maxChargeW, 'Charge limit'), maxDischargeW: nullable(battery.maxDischargeW, 'Discharge limit'),
      },
      topology: {
        conditioning: enumeration(topology.conditioning, ['MPPT', 'DET'], 'Conditioning'), distribution: enumeration(topology.distribution, ['centralized', 'distributed'], 'Transfer'),
        bus: enumeration(topology.bus, ['regulated', 'unregulated'], 'Bus regulation'), efficiency: nullable(topology.efficiency, 'Conditioning efficiency'),
        idlePowerW: nullable(topology.idlePowerW, 'EPS idle power'), massAllocationKg: nullable(topology.massAllocationKg, 'Mass allocation'),
      },
    },
    selections,
  };
}

export function serializeWorkspace(workspace: Workspace, catalogRevision: string): string {
  return JSON.stringify({
    ...workspace,
    exportedAt: new Date().toISOString(),
    catalogRevision,
    application: 'Orbitwork EPS proof of concept / 0.1.0',
    scope: 'Active scenario. Preliminary sizing, bounded catalog screening and energy-only propagation. Charge SoC, qualification and flight verification are unassessed. Inputs marked as assumptions require engineering review. Imported calculation caches are discarded.',
  }, null, 2);
}
