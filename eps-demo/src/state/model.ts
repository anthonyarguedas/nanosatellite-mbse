import { catalog } from '../data/catalog';
import { EXAMPLE_SCENARIOS } from '../data/scenarios';
import { assessDesign, calculateBudget, calculateOrbit, simulateOrbit, sizeBattery, sizeSolar, suggestProducts } from '../engine';
import { descendants, missingForNodes, NODE_DEFINITIONS, NODE_IDS, nodeStatuses } from '../workflow';
import type { DesignInputs, NodeId, NodeRecord, Product, Role, Scenario, Workspace } from '../types';

export function exampleInputs(): DesignInputs {
  return {
    mission: { name: 'BIRDS-4 / Tsuru concept study', altitudeKm: 400, lifetimeYears: 1 },
    scenarios: structuredClone(EXAMPLE_SCENARIOS), activeScenarioId: EXAMPLE_SCENARIOS[0]?.id ?? '',
    solar: { sunlightEfficiency: 0.85, eclipseEfficiency: 0.7, cellEolV: 2.25, cellEolA: 0.45, installedPowerW: 2 },
    battery: { dod: 0.3, margin: 0.2, capacityWh: 8, retainedEnergy: 0.8, chargeEfficiency: 0.95, dischargeEfficiency: 0.95, maxChargeW: 3, maxDischargeW: 6 },
    topology: { conditioning: 'MPPT', distribution: 'centralized', bus: 'regulated', efficiency: 0.9, idlePowerW: 0.08, massAllocationKg: 0.5 },
  };
}

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

/** Detect actual changed input groups, even if a caller names the wrong originating node. */
export function changeInputs(workspace: Workspace, updater: (inputs: DesignInputs) => DesignInputs): Workspace {
  const inputs = updater(structuredClone(workspace.inputs));
  const origin = inputs.mission.orbitSuggestion;
  if (origin && (origin.altitudeKm !== inputs.mission.altitudeKm || origin.query !== (inputs.mission.conOps ?? ''))) delete inputs.mission.orbitSuggestion;
  const before = workspace.inputs;
  const roots: NodeId[] = [];
  for (const group of ['mission', 'solar', 'battery', 'topology'] as const) {
    if (JSON.stringify(before[group]) !== JSON.stringify(inputs[group])) roots.push(group);
  }
  if (before.activeScenarioId !== inputs.activeScenarioId || JSON.stringify(before.scenarios) !== JSON.stringify(inputs.scenarios)) roots.push('scenarios');
  return roots.length ? invalidate({ ...workspace, inputs }, roots) : workspace;
}

export function evaluateNode(workspace: Workspace, id: NodeId): Workspace {
  const missing = missingForNodes(workspace)[id];
  if (missing.length) throw new Error(missing.join(' '));
  const inputs = workspace.inputs;
  const analysis = { ...workspace.analysis };
  const scenario = activeScenario(workspace);
  switch (id) {
    case 'mission': case 'scenarios': case 'topology': break;
    case 'orbit': analysis.orbit = calculateOrbit(inputs.mission.altitudeKm!); break;
    case 'budget': analysis.budget = calculateBudget(scenario!, analysis.orbit!); break;
    case 'solar': analysis.solar = sizeSolar(inputs, analysis.budget!, analysis.orbit!); break;
    case 'battery': analysis.battery = sizeBattery(inputs, analysis.budget!, analysis.orbit!); break;
    case 'candidates': analysis.suggestions = suggestProducts(catalog, inputs, analysis); break;
    case 'simulation': analysis.simulation = simulateOrbit(inputs, scenario!, analysis.orbit!); break;
    case 'assessment': analysis.checks = assessDesign(inputs, analysis, catalog, workspace.selections); break;
  }
  return {
    ...workspace, analysis,
    records: { ...workspace.records, [id]: { ...workspace.records[id], evaluatedRevision: workspace.records[id].revision, evaluatedAt: new Date().toISOString() } },
  };
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

export function createExampleWorkspace(): Workspace {
  return evaluateReady(createWorkspace(exampleInputs()), ['mission', 'orbit', 'scenarios', 'budget', 'solar', 'battery', 'topology']);
}

function numeric(product: Product, key: string): number | null {
  const spec = product.specs[key];
  return spec?.status === 'available' && typeof spec.value === 'number' && Number.isFinite(spec.value) ? spec.value : null;
}

/** An explicit engineer allocation. It never converts an incomplete suggestion into a feasible design. */
export function applyProduct(workspace: Workspace, role: Role, productId: string): Workspace {
  const product = catalog.products.find(item => item.id === productId);
  if (!product) throw new Error('This product is absent from the current catalog revision.');
  if (!product.roles.includes(role)) throw new Error('This catalog entry does not provide the selected CSRM role.');
  if (nodeStatuses(workspace).candidates !== 'complete') throw new Error('COTS suggestions are stale or missing. Reevaluate COTS suggestions before applying a product.');
  const suggestion = workspace.analysis.suggestions?.find(item => item.productId === productId);
  if (!suggestion || suggestion.outcome === 'rejected') throw new Error('This product has no applicable current suggestion or has a known violation.');
  const existingBoard = catalog.products.find(item => item.id === workspace.selections.conditioning);
  if (role === 'battery' && existingBoard?.roles.includes('battery') && existingBoard.id !== productId) {
    throw new Error('The selected integrated EPS includes its fixed battery. Replace that EPS board before allocating a separate pack.');
  }
  const selections = { ...workspace.selections };
  if (role === 'conditioning') {
    // The same physical usage supplies each documented role of an integrated board.
    for (const [existingRole, existingId] of Object.entries(selections)) {
      const previous = catalog.products.find(item => item.id === existingId);
      if (previous?.level === 'board' && previous.roles.includes('conditioning')) delete selections[existingRole as Role];
    }
    for (const providedRole of product.roles) selections[providedRole] = productId;
  } else selections[role] = productId;

  let next = changeInputs({ ...workspace, selections }, inputs => {
    if (role === 'battery' || (role === 'conditioning' && product.roles.includes('battery'))) {
      // Unknown replacement capacity cannot inherit a previous product's known rating.
      // Finished pack properties remain fixed. No pack series/parallel resizing is inferred.
      inputs.battery.capacityWh = numeric(product, 'energyWh');
    }
    if (role === 'solar') {
      if (product.level === 'cell') {
        inputs.solar.cellEolV = numeric(product, 'vmpEolV');
        inputs.solar.cellEolA = numeric(product, 'impEolA');
      }
      const power = numeric(product, 'powerEolW');
      if (product.level === 'panel' && power !== null) inputs.solar.installedPowerW = power * suggestion.quantity;
    }
    return inputs;
  });
  // Even a product substitution with identical numerical ratings changes the assessment subject.
  next = invalidate(next, ['simulation', 'assessment']);
  return next;
}
