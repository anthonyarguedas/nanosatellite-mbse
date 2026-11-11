// Shared editing and structural validation for the Python power model.
import { expressionReferences } from './expression-metadata.mjs';
import { MAX_VARIABLES } from './workspace-limits.mjs';

export const emptyPower = () => ({ modes: [], loads: [], links: [] });
export const powerInputNames = ['sunlight_power_W', 'eclipse_power_W', 'sunlight_duty', 'eclipse_duty'];
export const powerRequirementTemplates = [
  { model: 'PowerBudgetModel::PowerLimit', attributes: { power_limit_W: 'Real', allocated_power_W: 'Real', draw_power_W: 'Real' },
    parameters: { power_limit_W: null, allocated_power_W: null, draw_power_W: 'PowerAllocation.draw_power_W' } },
  { model: 'PowerBudgetModel::ComponentPowerLimit', attributes: { power_limit_W: 'Real', draw_power_W: 'Real' },
    parameters: { power_limit_W: null, draw_power_W: 'PowerAllocation.draw_power_W' } },
];
export const isPowerRequirement = row => powerRequirementTemplates.some(template => template.model === row.definition);
export const powerKind = element => element.definition.endsWith('::Software') ? 'host'
  : /::(?:StaticMount|ThermalSink|PropellantStorage|Batteries|SolarArrays)$/.test(element.definition) ? 'excluded' : 'counted';
export const spacecraftComponents = workspace => workspace.elements.filter(row => row.id && /^SpaceSegment::CubeSat::[^:]+::[^:]+$/.test(row.definition));
export const powerFor = (workspace, element) => workspace.power?.loads.find(load => load.element === element.key)
  ?? { element: element.key, quantity: 1, accounting: powerKind(element), host: '', rationale: '', states: [], assignments: {} };
export function powerScopes(workspace) {
  const roots = workspace.elements.filter(row => row.id && row.owner === 'mission'
    && ['SpaceSegment::CubeSat', 'SpaceSegment::CubeSat::PayloadSubsystem'].includes(row.definition));
  const subsystems = workspace.elements.filter(row => row.id && /^SpaceSegment::CubeSat::[^:]*Subsystem$/.test(row.definition));
  return [
    { key: 'mission', context: 'mission', parent: null, kind: 'system', affected: roots.map(row => row.key) },
    ...subsystems.map(row => ({ key: row.key, context: row.key, parent: 'mission', kind: 'subsystem', affected: [] })),
    ...spacecraftComponents(workspace).map(row => ({ key: row.key, context: row.owner, parent: row.owner, kind: 'component', affected: [row.key] })),
  ];
}
export const powerLimitFor = (workspace, scope) => workspace.statements.find(row => isPowerRequirement(row) && row.powerScope === scope);
export const parentPowerLimit = (workspace, row) => {
  const scope = powerScopes(workspace).find(scope => scope.key === row.powerScope);
  return scope?.parent ? powerLimitFor(workspace, scope.parent) : null;
};
export function powerAllocationExpression(workspace, row, { skipMissing = false } = {}) {
  const children = powerScopes(workspace).filter(scope => scope.parent === row.powerScope && (scope.kind !== 'component'
    || powerFor(workspace, workspace.elements.find(element => element.key === scope.key)).accounting === 'counted'
    || powerLimitFor(workspace, scope.key)));
  const requirements = children.sort((a, b) => a.key.localeCompare(b.key)).map(scope => powerLimitFor(workspace, scope.key));
  if (!skipMissing && requirements.some(requirement => !requirement)) return 'None';
  const references = requirements.filter(Boolean).map(requirement => `${requirement.id}.power_limit_W`);
  return references.length ? `sum([${references.join(', ')}])` : '0';
}

// Expand saved allocation aliases into ordinary, editable Python references.
export function expandPowerAllocations(workspace) {
  for (const row of workspace.statements.filter(isPowerRequirement)) {
    let sum;
    const expand = source => {
      const references = expressionReferences(source).filter(reference => reference.id === 'PowerAllocation' && reference.name === 'allocated_power_W');
      if (references.length) sum ??= powerAllocationExpression(workspace, row);
      for (const reference of references.reverse()) {
        const standalone = source.trim() === source.slice(reference.start, reference.fieldEnd);
        // An unset sum keeps its numeric type inside custom arithmetic.
        const replacement = sum === 'None' && !standalone ? 'None if True else 0' : sum;
        source = source.slice(0, reference.start) + (standalone ? replacement : `(${replacement})`) + source.slice(reference.fieldEnd);
      }
      return source;
    };
    row.condition = expand(row.condition);
    for (const method of row.verifications ?? []) method.condition = expand(method.condition);
    for (const [name, source] of Object.entries(row.parameters)) row.parameters[name] = expand(source);
  }
  return workspace;
}

export function seedPowerLimits(workspace, { scopes = null } = {}, identity) {
  const subjects = powerScopes(workspace);
  const selected = subjects.filter(scope => (!scopes || scopes.includes(scope.key)) && (scope.kind !== 'component'
    || powerFor(workspace, workspace.elements.find(row => row.key === scope.key)).accounting === 'counted'));
  if (!selected.length || !workspace.power.modes.length) return workspace;
  const defaults = new Set(workspace.statements.filter(row => row.definition === 'PowerBudgetModel::PowerLimit'
    && [powerAllocationExpression(workspace, row), powerAllocationExpression(workspace, row, { skipMissing: true })]
      .includes(row.parameters.allocated_power_W)).map(row => row.key));
  for (const name of ['power_limit_W', 'allocated_power_W', 'draw_power_W']) {
    const existing = workspace.variables.find(variable => variable.name === name);
    if (existing && (existing.type !== 'float' || (existing.unit && existing.unit !== 'W'))) throw new Error(`${name} requires a Float parameter in W.`);
    if (!existing) {
      if (workspace.variables.length >= MAX_VARIABLES) throw new Error(`Power limits need three numeric parameters within the ${MAX_VARIABLES} parameter limit.`);
      workspace.variables.push({ name, type: 'float', unit: 'W' });
      for (const row of workspace.statements) row.parameters[name] = null;
    } else existing.unit = 'W';
  }
  for (const scope of selected) {
    if (powerLimitFor(workspace, scope.key)) continue;
    const component = scope.kind === 'component';
    const row = { ...identity(`power-${scope.key}`, scope.kind === 'system' ? 'PWR' : component ? 'PWC' : 'PWS'),
      context: scope.context, kind: 'Requirement', definition: component ? 'PowerBudgetModel::ComponentPowerLimit' : 'PowerBudgetModel::PowerLimit',
      powerScope: scope.key, affected: [...scope.affected], sources: [], rationale: '',
      text: `The ${scope.kind === 'system' ? 'spacecraft' : component ? 'installed component' : 'subsystem'} power draw shall not exceed $$power_limit_W$$.`,
      condition: component ? 'power_limit_W >= 0 and draw_power_W >= 0 and draw_power_W <= power_limit_W'
        : 'power_limit_W >= 0 and allocated_power_W >= 0 and allocated_power_W <= power_limit_W and draw_power_W >= 0 and draw_power_W <= power_limit_W',
      parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, null])) };
    row.parameters.draw_power_W = 'PowerAllocation.draw_power_W';
    if (!component) defaults.add(row.key);
    const local = workspace.statements.filter(other => other.context === row.context && isPowerRequirement(other));
    const position = local.length ? workspace.statements.indexOf(local.at(-1)) + 1 : workspace.statements.findIndex(other => other.context === row.context);
    workspace.statements.splice(position < 0 ? workspace.statements.length : position, 0, row);
  }
  for (const row of workspace.statements.filter(isPowerRequirement)) {
    const parent = parentPowerLimit(workspace, row);
    if (parent && !row.sources.includes(parent.key)) row.sources.push(parent.key);
    if (row.powerScope === 'mission') row.affected = subjects[0].affected;
    if (defaults.has(row.key)) row.parameters.allocated_power_W = powerAllocationExpression(workspace, row);
  }
  return expandPowerAllocations(workspace);
}
export function defaultPowerRoots(workspace, eps) {
  const owner = workspace.elements.find(row => row.key === eps)?.owner;
  return workspace.elements.filter(row => row.key === owner || (row.owner === 'mission' && row.definition === 'SpaceSegment::CubeSat::PayloadSubsystem')).map(row => row.key);
}
export function managedPowerInput(workspace, row, name) {
  return powerInputNames.includes(name) && row.definition === 'FrameworkRequirements::LoadEnergy'
    && Boolean(workspace.power?.links.some(link => link.eps === row.context));
}
export function connectPower(workspace, eps, roots = defaultPowerRoots(workspace, eps)) {
  const row = workspace.statements.find(row => row.context === eps && row.definition === 'FrameworkRequirements::LoadEnergy');
  if (!row) throw new Error('This EPS needs the generic LoadEnergy requirement before connecting a budget.');
  if (workspace.power.links.some(link => link.eps === eps)) return;
  workspace.power.links.push({ eps, roots: [...roots], previous: Object.fromEntries(powerInputNames.map(name => [name, row.parameters[name] ?? null])) });
  Object.assign(row.parameters, { sunlight_power_W: 'LoadBudget.sunlight_power_W', eclipse_power_W: 'LoadBudget.eclipse_power_W', sunlight_duty: '1', eclipse_duty: '1' });
}
export function disconnectPower(workspace, eps) {
  const link = workspace.power.links.find(link => link.eps === eps);
  const row = workspace.statements.find(row => row.context === eps && row.definition === 'FrameworkRequirements::LoadEnergy');
  if (link && row) Object.assign(row.parameters, link.previous);
  workspace.power.links = workspace.power.links.filter(link => link.eps !== eps);
}
export function validatePower(workspace) {
  const power = workspace.power;
  const fail = message => { throw new Error(`Power budget: ${message}`); };
  if (!power || !Array.isArray(power.modes) || !Array.isArray(power.loads) || !Array.isArray(power.links)) fail('invalid format.');
  if (power.modes.length > 24 || power.loads.length > 1000) fail('use up to 24 spacecraft modes and 1,000 load profiles.');
  const text = (value, max = 2000) => typeof value === 'string' && value.length <= max;
  const key = value => typeof value === 'string' && /^[a-zA-Z0-9_-]{1,80}$/.test(value);
  const unique = (rows, field) => new Set(rows.map(row => row[field])).size === rows.length;
  if (!unique(power.modes, 'key') || !unique(power.modes.map(row => ({ name: row.name?.trim().toLowerCase() })), 'name')) fail('spacecraft mode names and keys must be unique.');
  for (const mode of power.modes) {
    if (!key(mode.key) || !text(mode.name, 80) || !mode.name.trim()) fail('name each spacecraft mode.');
    for (const period of ['sunlight', 'eclipse']) if (mode[period] !== null && (typeof mode[period] !== 'number' || !Number.isFinite(mode[period]) || mode[period] < 0 || mode[period] > 100)) fail('mode fractions must be between 0 and 100 percent.');
  }
  const elements = new Map(spacecraftComponents(workspace).map(row => [row.key, row]));
  if (!unique(power.loads, 'element')) fail('each component has one load record.');
  for (const load of power.loads) {
    const element = elements.get(load.element);
    if (!element || !['counted', 'host', 'excluded'].includes(load.accounting)) fail('choose an existing spacecraft component and accounting boundary.');
    if (powerKind(element) === 'host' && load.accounting === 'counted') fail('software demand belongs to its execution host.');
    if (!Number.isSafeInteger(load.quantity) || load.quantity < 1 || load.quantity > 1000000) fail('quantity must be an integer from 1 to 1,000,000.');
    if (!text(load.rationale) || !text(load.host, 80)) fail('invalid accounting notes.');
    if (load.host && (!elements.get(load.host)?.definition.endsWith('::ProcessorAndMemory') || load.host === load.element)) fail('choose an existing processor and memory execution host.');
    if (!Array.isArray(load.states) || load.states.length > 32 || !unique(load.states, 'key') || !unique(load.states.map(row => ({ name: row.name?.trim().toLowerCase() })), 'name')) fail('use up to 32 uniquely named component states.');
    for (const state of load.states) {
      if (!key(state.key) || !text(state.name, 80) || !state.name.trim() || !['estimated', 'typical', 'maximum', 'measured'].includes(state.basis) || !text(state.source) || !text(state.conditions)) fail('invalid component state, source or conditions.');
      if (state.watts !== null && (typeof state.watts !== 'number' || !Number.isFinite(state.watts) || state.watts < 0)) fail('power must be a finite nonnegative number of watts.');
    }
    if (!load.assignments || typeof load.assignments !== 'object' || Array.isArray(load.assignments)) fail('invalid mode mapping.');
    for (const [mode, state] of Object.entries(load.assignments)) if (!power.modes.some(row => row.key === mode) || !load.states.some(row => row.key === state)) fail('mode mappings must reference existing modes and states.');
  }
  const scopes = new Map(powerScopes(workspace).map(scope => [scope.key, scope]));
  const limits = workspace.statements.filter(isPowerRequirement), identities = new Set();
  for (const row of limits) {
    const scope = scopes.get(row.powerScope);
    if (!scope || row.context !== scope.context) fail('power requirements must belong to their scope.');
    if (row.powerMode !== undefined) fail('put mode conditions in parameter expressions.');
    if (identities.has(row.powerScope)) fail('define each power limit once per scope.');
    identities.add(row.powerScope);
    if ((scope.kind === 'component') !== (row.definition === 'PowerBudgetModel::ComponentPowerLimit')) fail('use the power requirement type for this scope.');
    if (row.affected.length !== scope.affected.length || scope.affected.some(key => !row.affected.includes(key))) fail('power requirement assignments follow their defined scope.');
    const parent = parentPowerLimit(workspace, row);
    if (parent && !row.sources.includes(parent.key)) fail('retain the parent power requirement as a source.');
  }
  if (!unique(power.links, 'eps')) fail('each EPS has one budget connection.');
  for (const link of power.links) {
    if (!workspace.elements.some(row => row.key === link.eps && row.definition.endsWith('::PowerSubsystem'))) fail('choose an existing EPS.');
    if (!Array.isArray(link.roots) || !link.roots.length || new Set(link.roots).size !== link.roots.length || link.roots.some(root => !workspace.elements.some(row => row.key === root && row.owner === 'mission' && ['SpaceSegment::CubeSat', 'SpaceSegment::CubeSat::PayloadSubsystem'].includes(row.definition)))) fail('choose a bus or payload as the budget scope.');
    const row = workspace.statements.find(row => row.context === link.eps && row.definition === 'FrameworkRequirements::LoadEnergy');
    const expected = { sunlight_power_W: 'LoadBudget.sunlight_power_W', eclipse_power_W: 'LoadBudget.eclipse_power_W', sunlight_duty: '1', eclipse_duty: '1' };
    if (!row || powerInputNames.some(name => row.parameters[name] !== expected[name])) fail('disconnect the EPS budget before changing its managed LoadEnergy inputs.');
    if (!link.previous || powerInputNames.some(name => link.previous[name] !== null && !text(link.previous[name], 5000))) fail('invalid previous EPS inputs.');
  }
  return workspace;
}
