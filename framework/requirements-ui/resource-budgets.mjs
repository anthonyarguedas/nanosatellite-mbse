// Static spacecraft budgets use ordinary requirement parameters and Python sums.
import { powerScopes } from './power.mjs';

export const budgetResources = [
  { name: 'mass', unit: 'kg', value: 'mass_kg', limit: 'mass_allocation_kg', allocated: 'allocated_mass_kg', model: 'Mass', prefixes: ['MAS', 'MSS', 'MSC'] },
  { name: 'volume', unit: 'm^3', value: 'volume_m3', limit: 'volume_allocation_m3', allocated: 'allocated_volume_m3', model: 'Volume', prefixes: ['VOL', 'VLS', 'VLC'] },
];
export const resourceRequirementTemplates = budgetResources.flatMap(resource => [false, true].map(component => ({
  model: `ResourceBudgetModel::${component ? 'Component' : ''}${resource.model}Limit`,
  attributes: Object.fromEntries([resource.limit, resource.value, ...(!component ? [resource.allocated] : [])].map(name => [name, 'Real'])),
  parameters: Object.fromEntries([resource.limit, resource.value, ...(!component ? [resource.allocated] : [])].map(name => [name, null])),
})));
export const resourceForRequirement = row => budgetResources.find(resource =>
  [`ResourceBudgetModel::${resource.model}Limit`, `ResourceBudgetModel::Component${resource.model}Limit`].includes(row.definition));
export const isResourceRequirement = row => Boolean(resourceForRequirement(row));
export function resourceScopes(workspace) {
  const software = new Set(workspace.elements.filter(row => row.definition.endsWith('::Software')).map(row => row.key));
  return powerScopes(workspace).filter(scope => scope.kind === 'system' ? scope.affected.length : !software.has(scope.key));
}
export const resourceLimitFor = (workspace, scope, resource) => workspace.statements.find(row =>
  resourceForRequirement(row)?.name === resource.name && row.budgetScope === scope);
export function parentResourceLimit(workspace, row) {
  const scope = resourceScopes(workspace).find(scope => scope.key === row.budgetScope);
  return scope?.parent ? resourceLimitFor(workspace, scope.parent, resourceForRequirement(row)) : null;
}
export function resourceSumExpression(workspace, row, name, { skipMissing = false } = {}) {
  const resource = resourceForRequirement(row);
  const requirements = resourceScopes(workspace).filter(scope => scope.parent === row.budgetScope)
    .sort((a, b) => a.key.localeCompare(b.key)).map(scope => resourceLimitFor(workspace, scope.key, resource));
  if (!skipMissing && requirements.some(requirement => !requirement)) return 'None';
  const field = name === resource.allocated ? resource.limit : resource.value;
  const references = requirements.filter(Boolean).map(requirement => `${requirement.id}.${field}`);
  return references.length ? `sum([${references.join(', ')}])` : '0';
}

export function seedResourceBudgets(workspace, { scopes = null } = {}, identity) {
  const subjects = resourceScopes(workspace), selected = subjects.filter(scope => !scopes || scopes.includes(scope.key));
  if (!selected.length) return workspace;
  const defaults = new Map();
  for (const row of workspace.statements.filter(isResourceRequirement)) {
    const resource = resourceForRequirement(row);
    if (row.definition.includes('::Component')) continue;
    defaults.set(row.key, [resource.value, resource.allocated].filter(name =>
      [resourceSumExpression(workspace, row, name), resourceSumExpression(workspace, row, name, { skipMissing: true })].includes(row.parameters[name])));
  }
  const parameters = budgetResources.flatMap(resource => [resource.limit, resource.value, resource.allocated].map(name => ({ name, unit: resource.unit })));
  const additions = parameters.filter(parameter => !workspace.variables.some(variable => variable.name === parameter.name));
  if (workspace.variables.length + additions.length > 64) throw new Error('Mass and volume budgets need six shared parameters within the 64 parameter limit. Remove unused variable names before adding budgets.');
  for (const parameter of parameters) {
    const existing = workspace.variables.find(variable => variable.name === parameter.name);
    if (existing && (existing.type !== 'float' || (existing.unit && existing.unit !== parameter.unit && !(parameter.unit === 'm^3' && existing.unit === 'm**3')))) {
      throw new Error(`${parameter.name} requires a Float parameter in ${parameter.unit}. Rename the conflicting variable before adding budgets.`);
    }
  }
  for (const parameter of parameters) {
    const existing = workspace.variables.find(variable => variable.name === parameter.name);
    if (!existing) {
      workspace.variables.push({ ...parameter, type: 'float' });
      for (const row of workspace.statements) row.parameters[parameter.name] = null;
    } else if (!existing.unit) existing.unit = parameter.unit;
  }
  for (const resource of budgetResources) for (const scope of selected) {
    if (resourceLimitFor(workspace, scope.key, resource)) continue;
    const component = scope.kind === 'component', subject = scope.kind === 'system' ? 'spacecraft' : component ? 'installed component' : 'subsystem';
    const row = { ...identity(`${resource.name}-${scope.key}`, resource.prefixes[scope.kind === 'system' ? 0 : component ? 2 : 1]),
      context: scope.context, kind: 'Requirement', definition: `ResourceBudgetModel::${component ? 'Component' : ''}${resource.model}Limit`,
      budgetScope: scope.key, affected: [...scope.affected], sources: [],
      rationale: component ? `Enter total installed ${resource.name}, including quantity and auxiliaries, using disjoint hardware accounting boundaries.` : 'Child allocations remain independent of this limit. Totals use disjoint hardware accounting boundaries.',
      text: `The ${subject} ${resource.name} shall not exceed $$${resource.limit}$$.`,
      condition: `${resource.limit} >= 0 and ${resource.value} >= 0 and ${resource.value} <= ${resource.limit}`
        + (component ? '' : ` and ${resource.allocated} >= 0 and ${resource.allocated} <= ${resource.limit}`),
      parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, null])) };
    if (!component) defaults.set(row.key, [resource.value, resource.allocated]);
    workspace.statements.push(row);
  }
  for (const row of workspace.statements.filter(isResourceRequirement)) {
    const parent = parentResourceLimit(workspace, row);
    if (parent && !row.sources.includes(parent.key)) row.sources.push(parent.key);
    if (row.budgetScope === 'mission') row.affected = [...subjects.find(scope => scope.key === 'mission').affected];
    for (const name of defaults.get(row.key) ?? []) row.parameters[name] = resourceSumExpression(workspace, row, name);
  }
  return workspace;
}

export function validateResourceBudgets(workspace) {
  const fail = message => { throw new Error(`Mass and volume budgets: ${message}`); };
  if (workspace.resourceBudgets !== undefined && workspace.resourceBudgets !== true) fail('invalid initialization marker.');
  const scopes = new Map(resourceScopes(workspace).map(scope => [scope.key, scope])), identities = new Set();
  for (const row of workspace.statements) {
    const resource = resourceForRequirement(row);
    if (!resource) {
      if (row.budgetScope !== undefined) fail('scope references belong to resource limit requirements.');
      continue;
    }
    const scope = scopes.get(row.budgetScope), identity = `${resource.name}:${row.budgetScope}`;
    if (!scope || row.context !== scope.context) fail('requirements must belong to their hardware scope.');
    if (identities.has(identity)) fail('define each resource limit once per scope.');
    identities.add(identity);
    if ((scope.kind === 'component') !== row.definition.includes('::Component')) fail('use the resource requirement type for this scope.');
    if (row.affected.length !== scope.affected.length || scope.affected.some(key => !row.affected.includes(key))) fail('requirement assignments follow their defined scope.');
    const parent = parentResourceLimit(workspace, row);
    if (parent && !row.sources.includes(parent.key)) fail('retain the parent resource requirement as a source.');
  }
  return workspace;
}
