import { catalog } from '../data/catalog';
import { birds4Inputs, BIRDS4_DEFAULT_ALLOCATIONS, BIRDS4_DEFAULT_PROVENANCE } from '../data/birds4';
import { assessDesign, calculateBudget, calculateOrbit, simulateOrbit, sizeBattery, sizeSolar, suggestProducts } from '../engine';
import { allocationIssues, EPS_ROLES, productSnapshot } from '../engine/allocations';
import { numericEvidence } from '../engine/catalog';
import { descendants, missingForNodes, NODE_DEFINITIONS, NODE_IDS, nodeStatuses } from '../workflow';
import type { AllocationReceipt, DesignInputs, NodeId, NodeRecord, NumericInputPath, ParameterProvenance, Product, Role, Scenario, Workspace } from '../types';
import { catalogProvenance, manualProvenance, NUMERIC_INPUT_PATHS, numericInput, provenanceIssues, provenanceSourceIds, setNumericInput } from './provenance';

export function exampleInputs(): DesignInputs { return birds4Inputs(); }

export function emptyInputs(): DesignInputs {
  return {
    mission: { name: 'Untitled mission', altitudeKm: null, lifetimeYears: null }, scenarios: [], activeScenarioId: '',
    solar: { sunlightEfficiency: null, eclipseEfficiency: null, cellEolV: null, cellEolA: null, installedPowerW: null },
    battery: { dod: null, margin: null, capacityWh: null, retainedEnergy: null, chargeEfficiency: null, dischargeEfficiency: null, maxChargeW: null, maxDischargeW: null },
    topology: { conditioning: 'MPPT', distribution: 'centralized', bus: 'regulated', efficiency: null, idlePowerW: null, massAllocationKg: null },
  };
}

export function createWorkspace(inputs = emptyInputs()): Workspace {
  const records = Object.fromEntries(NODE_IDS.map(id => [id, { revision: 1, evaluatedRevision: null, evaluatedAt: null }])) as Record<NodeId, NodeRecord>;
  return { schemaVersion: 1, inputs: structuredClone(inputs), records, analysis: {}, selections: {} };
}

export function activeScenario(workspace: Workspace): Scenario | undefined {
  return workspace.inputs.scenarios.find(item => item.id === workspace.inputs.activeScenarioId);
}

export function invalidate(workspace: Workspace, roots: NodeId[]): Workspace {
  const records = { ...workspace.records };
  const affected = new Set(roots.flatMap(descendants));
  for (const id of affected) records[id] = { ...records[id], revision: records[id].revision + 1 };
  return { ...workspace, records };
}

/** Detect actual changed inputs, including the direct EPS-baseline input to budget (not a cyclic node dependency). */
export function changeInputs(workspace: Workspace, updater: (inputs: DesignInputs) => DesignInputs): Workspace {
  const inputs = updater(structuredClone(workspace.inputs));
  const origin = inputs.mission.orbitSuggestion;
  if (origin && (origin.altitudeKm !== inputs.mission.altitudeKm || origin.query !== (inputs.mission.conOps ?? ''))) delete inputs.mission.orbitSuggestion;
  const before = workspace.inputs;
  const roots: NodeId[] = [];
  for (const group of ['mission', 'solar', 'battery', 'topology'] as const) {
    if (JSON.stringify(before[group]) !== JSON.stringify(inputs[group])) roots.push(group);
  }
  if (before.topology.idlePowerW !== inputs.topology.idlePowerW) roots.push('budget');
  if (before.activeScenarioId !== inputs.activeScenarioId || JSON.stringify(before.scenarios) !== JSON.stringify(inputs.scenarios)) roots.push('scenarios');
  if (!roots.length) return workspace;
  let provenance = [...workspace.provenance ?? []];
  for (const parameter of NUMERIC_INPUT_PATHS) {
    const value = numericInput(inputs, parameter);
    if (value === numericInput(before, parameter)) continue;
    provenance = provenance.filter(record => record.parameter !== parameter);
    if (value !== null && Number.isFinite(value)) provenance.push(manualProvenance(parameter, value));
  }
  const priorMissionSources = new Set(before.mission.orbitSuggestion?.sources.map(source => source.id) ?? []);
  if (priorMissionSources.size) {
    const currentSources = provenanceSourceIds(inputs, catalog);
    provenance = provenance.map(record => {
      const detached = record.sourceIds.filter(id => priorMissionSources.has(id) && !currentSources.has(id));
      if (!detached.length) return record;
      return { ...record, sourceIds: record.sourceIds.filter(id => !detached.includes(id)),
        conditions: `Mission evidence changed. Source references detached (${detached.join(', ')}). Review this retained study assumption. ${record.conditions}` };
    });
  }
  const catalogReview = workspace.catalogReview ? [...allocationIssues(workspace, catalog), ...provenanceIssues(inputs, provenance, workspace.selections, catalog)] : undefined;
  return invalidate({ ...workspace, inputs, provenance, catalogReview }, roots);
}

export function evaluateNode(workspace: Workspace, id: NodeId): Workspace {
  const statuses = nodeStatuses(workspace);
  const missing = missingForNodes(workspace, statuses)[id];
  if (missing.length) throw new Error(missing.join(' '));
  const inputs = workspace.inputs;
  const analysis = { ...workspace.analysis };
  const scenario = activeScenario(workspace);
  switch (id) {
    case 'mission': case 'scenarios': case 'topology': break;
    case 'orbit': analysis.orbit = calculateOrbit(inputs.mission.altitudeKm!); break;
    case 'budget': analysis.budget = calculateBudget(scenario!, analysis.orbit!, inputs.topology.idlePowerW!); break;
    case 'solar': analysis.solar = sizeSolar(inputs, analysis.budget!, analysis.orbit!); break;
    case 'battery': analysis.battery = sizeBattery(inputs, analysis.budget!, analysis.orbit!); break;
    case 'candidates': analysis.suggestions = suggestProducts(catalog, inputs, analysis); break;
    case 'simulation': {
      const simulation = simulateOrbit(inputs, scenario!, analysis.orbit!);
      analysis.simulation = { ...simulation, assumptions: [...simulation.assumptions,
        ...(workspace.provenance ?? []).filter(record => record.kind === 'engineering-assumption')
          .map(record => `${record.parameter} = ${record.value}: ${record.rationale} ${record.conditions}`)] };
      break;
    }
    case 'assessment': {
      // Historical curves remain visible in the workspace, but are never admitted as current evidence.
      const evidence = { ...analysis };
      if (statuses.simulation !== 'complete') delete evidence.simulation;
      analysis.checks = assessDesign(inputs, evidence, catalog, workspace.selections, workspace.allocations);
      break;
    }
  }
  const next: Workspace = {
    ...workspace, analysis,
    records: { ...workspace.records, [id]: { ...workspace.records[id], evaluatedRevision: workspace.records[id].revision, evaluatedAt: new Date().toISOString() } },
  };
  // A newly available optional result changes an earlier partial assessment even without input edits.
  const consumers = NODE_DEFINITIONS.filter(node => node.evidenceDependencies?.includes(id)).map(node => node.id);
  return consumers.length ? invalidate(next, consumers) : next;
}

export function evaluateReady(workspace: Workspace, allowed: NodeId[] = NODE_IDS): Workspace {
  let next = workspace;
  for (const node of NODE_DEFINITIONS) {
    if (!allowed.includes(node.id)) continue;
    const statuses = nodeStatuses(next);
    if (statuses[node.id] !== 'complete' && missingForNodes(next, statuses)[node.id].length === 0) next = evaluateNode(next, node.id);
  }
  return next;
}

/** Explicitly constructed, fully evaluated example. This is not the restore/import path or engineer approval. */
export function createExampleWorkspace(): Workspace {
  let workspace = evaluateReady({ ...createWorkspace(exampleInputs()), provenance: structuredClone(BIRDS4_DEFAULT_PROVENANCE) });
  for (const allocation of BIRDS4_DEFAULT_ALLOCATIONS) {
    workspace = applyProduct(workspace, allocation.role, allocation.productId);
    const receipt = workspace.allocations!.find(item => item.productId === allocation.productId)!;
    if (receipt.quantity !== allocation.quantity) throw new Error('The bundled BIRDS-4 allocation no longer matches its preliminary screen. Review the example basis.');
    workspace = { ...workspace, allocations: workspace.allocations!.map(item => item === receipt
      ? { ...item, origin: 'bundled-example', rationale: allocation.rationale } : item) };
    workspace = evaluateReady(workspace);
  }
  const source = catalog.products.find(product => product.id === workspace.selections.solar)!;
  workspace = { ...workspace, provenance: [
    ...(workspace.provenance ?? []).filter(record => record.kind === 'catalog-value'),
    ...structuredClone(BIRDS4_DEFAULT_PROVENANCE).map(record => record.parameter === 'solar.installedPowerW'
      ? { ...record, productId: source.id, productRevision: source.revision } : record),
  ] };
  return evaluateReady(invalidate(workspace, ['simulation']));
}

function numeric(product: Product, key: string): number | null { return numericEvidence(product, key).value ?? null; }

/** Apply snapshots the proposed whole count. It is an allocation, not feasibility, qualification or a wiring decision. */
export function applyProduct(workspace: Workspace, role: Role, productId: string): Workspace {
  const product = catalog.products.find(item => item.id === productId);
  if (!product) throw new Error('This product is absent from the current catalog revision.');
  if (product.catalogUse === 'reference-only') throw new Error('This published assembly is reference context only, not a selectable characterized product.');
  if (!product.roles.includes(role)) throw new Error('This catalog entry does not provide the selected CSRM role.');
  if (nodeStatuses(workspace).candidates !== 'complete') throw new Error('COTS suggestions are stale or missing. Reevaluate COTS suggestions before applying a product.');
  const suggestion = workspace.analysis.suggestions?.find(item => item.productId === productId && item.role === role);
  if (!suggestion || suggestion.outcome === 'rejected' || suggestion.checks.some(check => check.verdict === 'fail')) throw new Error('This product has no applicable current suggestion or has a known violation.');
  if (!Number.isSafeInteger(suggestion.quantity) || suggestion.quantity < 1) throw new Error('The proposed allocation quantity must be a positive whole number.');
  const existingBoard = catalog.products.find(item => item.id === workspace.selections.conditioning);
  if (role === 'battery' && !product.roles.includes('conditioning') && existingBoard?.roles.includes('battery') && existingBoard.id !== productId) {
    throw new Error('The selected integrated EPS includes its fixed battery. Replace that EPS board before allocating a separate pack.');
  }
  const selections = { ...workspace.selections };
  if (product.roles.includes('conditioning')) {
    for (const [existingRole, existingId] of Object.entries(selections)) {
      const previous = catalog.products.find(item => item.id === existingId);
      if (previous?.roles.includes('conditioning')) delete selections[existingRole as Role];
    }
    for (const providedRole of product.roles) selections[providedRole] = productId;
  } else selections[role] = productId;

  const transferred: ParameterProvenance[] = [];
  let next = changeInputs({ ...workspace, selections }, inputs => {
    // Product-bound assumptions/specifications cannot migrate to another product, even with the same number.
    for (const record of workspace.provenance ?? []) {
      if (record.productId && !Object.values(selections).includes(record.productId)) setNumericInput(inputs, record.parameter, null);
    }
    if (workspace.selections.battery !== selections.battery) inputs.battery.capacityWh = null;
    const transfer = (parameter: NumericInputPath) => {
      const record = catalogProvenance(product, parameter);
      setNumericInput(inputs, parameter, record?.value ?? null);
      if (record) transferred.push(record);
    };
    if (selections.battery === productId) {
      if (product.level === 'cell' && suggestion.quantity > 1) inputs.battery.capacityWh = null;
      else transfer('battery.capacityWh');
    }
    if (role === 'solar') {
      transfer('solar.cellEolV');
      transfer('solar.cellEolA');
      if (product.level === 'panel') {
        const power = numeric(product, 'powerEolW');
        inputs.solar.installedPowerW = power === null ? null : power * suggestion.quantity;
      }
    }
    return inputs;
  });
  const changedParameters = new Set(transferred.map(record => record.parameter));
  const provenance = (next.provenance ?? []).filter(record => !changedParameters.has(record.parameter)
    && (!record.productId || Object.values(selections).includes(record.productId)))
    .map(record => record.kind === 'engineering-assumption'
      ? { ...record, conditions: record.conditions.startsWith('Allocation changed;') ? record.conditions : `Allocation changed; review applicability. ${record.conditions}` } : record);
  provenance.push(...transferred);
  const receipt: AllocationReceipt = { productId, productRevision: product.revision, catalogRevision: catalog.revision,
    roles: EPS_ROLES.filter(item => selections[item] === productId), quantity: suggestion.quantity, origin: 'engineer-allocation', productSnapshot: productSnapshot(product),
    rationale: 'Explicit Apply action snapshots the proposed count for a concept allocation. Missing characterization remains unresolved; no hardware compatibility or qualification is approved.', allocatedAt: new Date().toISOString() };
  const allocations = (workspace.allocations ?? []).filter(item => item.productId !== productId && Object.values(selections).includes(item.productId))
    .map(item => ({ ...item, roles: EPS_ROLES.filter(provided => selections[provided] === item.productId) }));
  allocations.push(receipt);
  next = { ...next, allocations, provenance };
  const issues = allocationIssues(next, catalog);
  if (issues.length && !workspace.catalogReview?.length) throw new Error(issues.join(' '));
  next.catalogReview = workspace.catalogReview ? [...issues, ...provenanceIssues(next.inputs, provenance, selections, catalog)] : undefined;
  // Identical ratings still change the assessment subject and frozen hardware quantity.
  return invalidate(next, ['simulation', 'assessment']);
}
