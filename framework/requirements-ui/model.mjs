import { parseExpression } from './verification.mjs';

export const WORKSPACE_VERSION = 8;
export const stakeholderTypes = [
  { name: 'Regulatory Agency', model: 'External::RegulatoryAgencyStakeholders::RegulatoryAgencyStakeholder' },
  { name: 'Mission Stakeholder', model: 'External::MissionStakeholders::MissionStakeholder' },
  { name: 'Launch Provider', model: 'External::LaunchProviders::LaunchProvider' },
  { name: 'Partner', model: 'External::Partners::Partner' },
];
export const domainTypes = [
  { model: 'Orbit', name: 'Orbit', category: 'Orbit', role: 'orbit', id: 'ORB', expandable: false },
  { model: 'SpaceSegment::CubeSat', name: 'CubeSat Bus', category: 'Space Segment', role: 'bus', id: 'BUS', prefix: 'BUS', expandable: true },
  { model: 'SpaceSegment::CubeSat::PayloadSubsystem', name: 'Payload', category: 'Space Segment', role: 'payload', id: 'PAY', prefix: 'PAY', expandable: true },
  { model: 'GroundSegment::GroundStation', name: 'Ground Station', category: 'Ground Segment', role: 'ground', id: 'GND', prefix: 'GND', expandable: true },
];
export const statementKinds = ['Requirement', 'Need', 'Objective', 'Concern', 'Constraint'];
export const defaultVariables = () => ['x', 'y', 'z', 'a'].map(name => ({ name, type: 'float' }));
const prefixes = { Requirement: 'REQ', Need: 'NED', Objective: 'OBJ', Concern: 'CON', Constraint: 'CST', Component: 'CMP' };
const reserved = new Set('pi sqrt arccos floor abs min max true false and or xor implies not if then else null constructor prototype __proto__ id key name type text kind verified sources source condition parameters formulas origin rationale sourceReference acceptance externalId displayName statementKind statementText manualVerification verificationExpression verificationCondition tableName subject stakeholder context owner definition affected affectedElements product requirements components'.split(' '));
export const allRows = workspace => [...workspace.stakeholders, ...(workspace.elements ?? []), ...workspace.statements, ...(workspace.components ?? [])];

export function nextId(workspace, kind = 'Stakeholder', hint = '') {
  const ids = new Set(allRows(workspace).map(row => row.id));
  if (kind === 'Stakeholder' || kind === 'Element') {
    const preferred = hint.replace(/[^a-z]/gi, '').slice(0, 3).toUpperCase().padEnd(3, 'X');
    const first = hint ? preferred : 'STK';
    if (!ids.has(first)) return first;
    for (let i = 0; i < 26 ** 3; i++) {
      const id = [Math.floor(i / 676), Math.floor(i / 26) % 26, i % 26].map(n => String.fromCharCode(65 + n)).join('');
      if (!ids.has(id)) return id;
    }
    throw new Error('All three-letter element IDs are in use.');
  }
  const prefix = /^[A-Z]{3}$/.test(hint) ? hint : prefixes[kind] ?? 'REQ';
  for (let number = 1; number <= 999; number++) {
    const id = `${prefix}${String(number).padStart(3, '0')}`;
    if (!ids.has(id)) return id;
  }
  throw new Error(`All ${prefix} IDs are in use. Enter a different three-letter prefix.`);
}

function elementKey(workspace, hint) {
  const keys = new Set(allRows(workspace).map(row => row.key));
  const base = hint.slice(0, 70);
  let key = base, suffix = 1;
  while (keys.has(key)) key = `${base}_${suffix++}`;
  return key;
}
export function addElementChildren(workspace, parent, catalog = domainTypes, seed = true) {
  if (catalog.find(type => type.model === parent.definition)?.expandable
      && !workspace.elements.some(row => row.owner === parent.key)) {
    for (const type of catalog.filter(type => type.parent === parent.definition)) {
      const child = { key: elementKey(workspace, `${parent.key}-${type.model.split('::').at(-1)}`),
        id: nextId(workspace, 'Element', type.id ?? type.name), name: type.name, owner: parent.key, definition: type.model };
      workspace.elements.push(child);
      addElementChildren(workspace, child, catalog, false);
    }
  }
  if (seed && workspace.version === WORKSPACE_VERSION) {
    const descendants = new Set([parent.key]);
    for (const row of workspace.elements) if (descendants.has(row.owner)) descendants.add(row.key);
    seedRequirements(workspace, catalog, workspace.elements.filter(row => descendants.has(row.key)));
  }
}
function seedElements(workspace, catalog) {
  for (const type of catalog.filter(type => !type.parent)) {
    const row = { key: elementKey(workspace, `domain-${type.role}`), id: nextId(workspace, 'Element', type.id), name: type.name, owner: 'mission', definition: type.model };
    workspace.elements.push(row);
    addElementChildren(workspace, row, catalog, false);
  }
  return workspace;
}

export function seedRequirements(workspace, catalog, owners = workspace.elements) {
  const created = [];
  for (const owner of owners) {
    for (const template of catalog.find(type => type.model === owner.definition)?.requirements ?? []) {
      const context = template.context === 'mission' ? 'mission' : owner.key;
      if (workspace.statements.some(row => row.definition === template.model && row.context === context
          && (context !== 'mission' || row.affected.includes(owner.key)))) continue;
      for (const name of Object.keys(template.parameters)) {
        const type = template.integers?.includes(name) ? 'integer' : 'float';
        const existing = workspace.variables.find(variable => variable.name === name);
        if (existing && existing.type !== type) throw new Error(`Generic parameter ${name} requires a ${type} column. Rename the existing column before upgrading.`);
        if (!existing) workspace.variables.push({ name, type, ...(template.units?.[name] ? { unit: template.units[name] } : {}) });
      }
      const row = { key: elementKey(workspace, `generic-${owner.id}-${template.name}`),
        id: allRows(workspace).some(row => row.id === template.id) ? nextId(workspace, 'Requirement', template.id.slice(0, 3)) : template.id,
        context, kind: 'Requirement', definition: template.model, origin: template.origin, rationale: template.origin ?? '',
        text: template.text, condition: template.condition, sources: [],
        affected: context === 'mission' ? [owner.key] : workspace.elements.filter(element => element.owner === owner.key
          && template.affected.includes(element.definition.split('::').at(-1))).map(element => element.key),
        parameters: { ...template.parameters } };
      workspace.statements.push(row);
      created.push({ row, derivesFrom: template.derivesFrom ?? [] });
    }
  }
  for (const { row, derivesFrom } of created) {
    const substitute = expression => expression.replace(/@([A-Za-z_][A-Za-z0-9_]*)\./g, (_, name) => {
      const matches = workspace.statements.filter(other => other.definition === `FrameworkRequirements::${name}`);
      const local = matches.filter(other => other.context === row.context
        && (row.context !== 'mission' || other.affected.some(key => row.affected.includes(key))));
      const mission = matches.filter(other => other.context === 'mission');
      const target = local.length === 1 ? local[0] : mission.length === 1 ? mission[0] : null;
      if (!target) return 'UNBOUND.';
      if (!row.sources.includes(target.key) && row.key !== target.key) row.sources.push(target.key);
      return `${target.id}.`;
    });
    for (const name of derivesFrom) substitute(`@${name}.`);
    row.condition = substitute(row.condition);
    for (const [name, value] of Object.entries(row.parameters)) {
      if (value === null) continue;
      const expression = substitute(String(value));
      // Ambiguous upstream instances stay unset until an engineer chooses a
      // value or expression in the cell.
      row.parameters[name] = expression.includes('UNBOUND.') ? null : expression;
    }
  }
  for (const row of workspace.statements) {
    for (const variable of workspace.variables) if (!Object.hasOwn(row.parameters, variable.name)) row.parameters[variable.name] = null;
  }
  return workspace;
}

export function blankWorkspace() {
  return { version: WORKSPACE_VERSION, variables: defaultVariables(), stakeholders: [], elements: [], statements: [], components: [] };
}
export function emptyWorkspace(catalog = domainTypes) {
  return seedRequirements(seedElements(blankWorkspace(), catalog), catalog);
}
export function validVariableName(name) {
  return typeof name === 'string' && /^[A-Za-z_][A-Za-z0-9_]{0,39}$/.test(name)
    && !reserved.has(name) && !Object.hasOwn(Object.prototype, name) && !/^[A-Z]{3}\d{3}$/.test(name);
}

// Delimiters belong to requirement prose. Expressions use the bare names.
export function requirementMarkers(text) {
  const segments = text.split('$$'), names = [], errors = [];
  for (let index = 1; index < segments.length; index += 2) {
    if (index + 1 >= segments.length) { errors.push('Close each variable name with $$.'); break; }
    const name = segments[index].trim();
    if (!validVariableName(name)) errors.push(`“${name || '(empty)'}” is not a supported SysML variable name.`);
    else if (!names.includes(name)) names.push(name);
  }
  return { names, errors };
}

export function declareRequirementVariables(workspace, row) {
  const markers = requirementMarkers(row.text);
  const existing = new Set(workspace.variables.map(variable => variable.name));
  const additions = markers.names.filter(name => !existing.has(name));
  if (workspace.variables.length + additions.length > 64) throw new Error('A workspace can contain up to 64 variable names.');
  for (const name of additions) {
    workspace.variables.push({ name, type: 'float' });
    for (const statement of workspace.statements) statement.parameters[name] = null;
  }
  return markers;
}

export function requirementParameterNames(workspace, row, catalog = domainTypes) {
  const marked = requirementMarkers(row.text).names;
  const retained = new Set(Object.entries(row.parameters).filter(([, value]) => typeof value === 'string' && value.trim()).map(([name]) => name));
  const template = catalog.flatMap(type => type.requirements ?? []).find(template => template.model === row.definition);
  Object.keys(template?.parameters ?? {}).forEach(name => retained.add(name));
  // Keep old placeholders and existing equation inputs accessible without
  // exposing every shared variable in the workbook.
  for (const match of row.text.matchAll(/\{([A-Za-z_][A-Za-z0-9_]*)\}/g)) retained.add(match[1]);
  for (const expression of [row.condition, ...Object.values(row.parameters)]) {
    if (typeof expression !== 'string' || !expression.trim()) continue;
    try {
      const stack = [parseExpression(expression)];
      while (stack.length) {
        const node = stack.pop();
        if (node.kind === 'variable') retained.add(node.name);
        else if (node.kind === 'binary') stack.push(node.left, node.right);
        else if (node.kind === 'unary') stack.push(node.operand);
        else if (node.kind === 'call') stack.push(...node.args);
      }
    } catch { /* Invalid drafts keep their populated cells visible. */ }
  }
  return [...marked, ...workspace.variables.map(variable => variable.name).filter(name => retained.has(name) && !marked.includes(name))];
}

// Apply only the editor's changes so browsing and editing other tables stays safe.
export function mergeRequirementDraft(workspace, original, edited, key) {
  const candidate = structuredClone(workspace);
  const before = original.statements.find(row => row.key === key);
  const after = edited.statements.find(row => row.key === key);
  const target = candidate.statements.find(row => row.key === key);
  const fail = () => { throw new Error('This requirement or its parameters changed while you were editing. Reopen it before saving.'); };
  if (!before || !after || !target) fail();
  const merge = (previous, updated, current, apply) => {
    if (previous === updated) return;
    if (current !== previous && current !== updated) fail();
    apply(updated);
  };
  for (const field of ['id', 'kind', 'text', 'condition', 'rationale']) merge(before[field], after[field], target[field], value => { target[field] = value; });
  for (const variable of edited.variables) {
    const previous = original.variables.find(item => item.name === variable.name);
    let current = candidate.variables.find(item => item.name === variable.name);
    if (!current) {
      if (previous) fail();
      current = structuredClone(variable);
      candidate.variables.push(current);
      for (const row of candidate.statements) row.parameters[variable.name] = null;
    }
    if (current.type !== variable.type) fail();
    merge(previous?.unit, variable.unit, current.unit, unit => {
      if (unit === undefined) delete current.unit;
      else current.unit = unit;
    });
    merge(before.parameters[variable.name] ?? null, after.parameters[variable.name] ?? null, target.parameters[variable.name] ?? null,
      value => { target.parameters[variable.name] = value; });
  }
  return candidate;
}

export function formatParameterValue(value) {
  return Math.abs(value) > 999
    ? value.toLocaleString('en-US', { useGrouping: false, maximumFractionDigits: 0 })
    : value.toPrecision(4);
}

export function interpolateRequirement(text, values = {}, renderParameter = (name, value) => value === null ? name : formatParameterValue(value)) {
  return text.replace(/\$\$([\s\S]*?)\$\$|\{([A-Za-z_][A-Za-z0-9_]*)\}/g, (token, marked, legacy) => {
    const name = marked === undefined ? legacy : marked.trim();
    if (!validVariableName(name)) return token;
    return renderParameter(name, typeof values[name] === 'number' && Number.isFinite(values[name]) ? values[name] : null);
  });
}

export function tabsFor(workspace, catalog = domainTypes) {
  const tabs = [
    { key: 'external', label: 'External', leftTitle: 'Stakeholders and Third Parties', requirementsTitle: 'Stakeholder Requirements', prefix: 'REQ' },
    { key: 'mission', label: 'Mission', leftTitle: 'Mission Domain Elements', requirementsTitle: 'Mission Requirements', affectedLabel: 'Affected domain elements', prefix: 'MIS' },
  ];
  const elements = workspace.elements.filter(row => catalog.find(type => type.model === row.definition)?.expandable);
  const labelFor = element => {
    const type = catalog.find(type => type.model === element.definition);
    return element.name && element.name !== type.name ? element.name : type.tabLabel ?? type.name;
  };
  for (const element of elements) {
    const type = catalog.find(type => type.model === element.definition), label = labelFor(element);
    const duplicate = elements.some(row => row.key !== element.key && labelFor(row) === label);
    tabs.push({ key: element.key, label: duplicate ? `${label} (${element.id})` : label,
      leftTitle: `${label} ${type.role === 'eps' ? 'Components' : type.role === 'payload' ? 'Elements' : 'Subsystems'}`,
      requirementsTitle: `${label} ${type.role === 'eps' ? 'Parametric Requirements' : 'Requirements'}`,
      affectedLabel: type.role === 'eps' ? 'Affected components' : type.role === 'payload' ? 'Affected elements' : 'Affected subsystems', prefix: type.prefix });
  }
  return tabs;
}
export function allowedDefinitions(workspace, owner, catalog = domainTypes) {
  if (owner === 'mission') return catalog.filter(type => !type.parent);
  const parent = workspace.elements.find(row => row.key === owner);
  return parent && catalog.find(type => type.model === parent.definition)?.expandable
    ? catalog.filter(type => type.parent === parent.definition) : [];
}
export const contextForRow = row => row.context ?? row.owner ?? 'external';

export function rewriteRowReferences(workspace, renames) {
  const rewrite = expression => expression.replace(/\b[A-Z]{3}\d{3}(?=\s*\.)/g, id => renames.get(id) ?? id);
  for (const row of workspace.statements) {
    row.condition = rewrite(row.condition);
    row.parameters = Object.fromEntries(Object.entries(row.parameters).map(([name, expression]) => [name,
      typeof expression === 'string' ? rewrite(expression) : expression]));
  }
}

// Upgrade existing files without changing stable row keys, values or links.
export function migrateWorkspace(data, catalog = domainTypes) {
  if (data?.version === 1) {
    const upgraded = { version: 2, variables: defaultVariables(), stakeholders: [], statements: [] };
    for (const row of data.stakeholders) {
      const hint = String(row.id).replace(/[^a-z]/gi, '').slice(0, 3);
      upgraded.stakeholders.push({ ...row, id: nextId(upgraded, 'Stakeholder', hint || row.name) });
    }
    for (const row of data.statements) {
      const { source, ...rest } = row;
      const prefix = prefixes[row.kind] ?? 'REQ';
      const digits = String(row.id).match(/(\d{1,3})$/)?.[1]?.padStart(3, '0');
      const letters = String(row.id).replace(/[^a-z]/gi, '').toUpperCase();
      const candidate = `${letters.length === 3 ? letters : prefix}${digits ?? '001'}`;
      const id = upgraded.statements.some(other => other.id === candidate) ? nextId(upgraded, row.kind) : candidate;
      upgraded.statements.push({ ...rest, id, sources: source ? [source] : [], condition: '' });
    }
    data = upgraded;
  }
  if (data?.version === 2) data = seedElements({ ...data, version: 3, elements: [],
    statements: data.statements.map(row => ({ ...row, context: 'external', affected: [] })) }, catalog);
  if (data?.version === 3) data = { ...data, version: 4, statements: data.statements.map(row => {
    const { verified, ...rest } = row;
    if (typeof verified !== 'boolean') throw new Error(`${row.id}: invalid legacy verification flag.`);
    // Preserve old checked rows as an explicit SysML literal. Unchecked rows
    // without a condition remain unverified, with no inferred false constraint.
    return { ...rest, condition: !row.condition.trim() && verified ? 'true' : row.condition };
  }) };
  if (data?.version === 4) {
    const upgraded = { ...data, version: 5, elements: [...data.elements] };
    // Seed newly supported component tables once. Later deletions stay deleted.
    for (const parent of data.elements.filter(row => row.owner !== 'mission')) addElementChildren(upgraded, parent, catalog);
    data = upgraded;
  }
  if (data?.version === 5) data = { ...data, version: 6, components: [] };
  if (data?.version === 6) data = seedRequirements(structuredClone({ ...data, version: 7 }), catalog);
  if (data?.version === 7) {
    const upgraded = structuredClone({ ...data, version: WORKSPACE_VERSION });
    upgraded.statements = upgraded.statements.map(({ formulas, ...row }) => {
      const parameters = { ...row.parameters, ...formulas };
      for (const [name, value] of Object.entries(parameters)) {
        if (typeof value === 'number') {
          if (!Number.isFinite(value)) throw new Error(`${row.id}.${name}: legacy values must be finite.`);
          parameters[name] = String(value);
        }
      }
      return { ...row, parameters };
    });
    return upgraded;
  }
  return data;
}

// Sources are rows anywhere in the workbook. Assignment is a separate link.
export function availableSources(workspace, statementKey) {
  const excluded = new Set([statementKey]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const row of workspace.statements) {
      if (row.sources.some(source => excluded.has(source)) && !excluded.has(row.key)) { excluded.add(row.key); changed = true; }
    }
  }
  return allRows(workspace).filter(row => !excluded.has(row.key));
}
export function assignableElements(workspace, statement) {
  return statement.context === 'external' ? [] : workspace.elements.filter(row => row.owner === statement.context);
}
export function componentRequirements(workspace, component) {
  return workspace.statements.filter(row => row.context === component.owner && row.kind === 'Requirement');
}
export function componentCheck(component, checks) {
  if (!component.requirements.length) return { state: 'unset', message: 'Link at least one requirement to verify this component.' };
  const states = component.requirements.map(key => checks.get(key)?.state ?? 'pending');
  if (states.every(state => state === 'pass')) return { state: 'pass', message: 'All affected requirements are verified.' };
  if (states.includes('error')) return { state: 'error', message: 'An affected requirement has a verification error.' };
  if (states.includes('fail')) return { state: 'fail', message: 'An affected requirement is false.' };
  if (states.includes('unset')) return { state: 'unset', message: 'An affected requirement has no verification condition.' };
  return { state: 'pending', message: 'Waiting for affected requirements to be verified.' };
}
export function parameterExpression(value, variable, id = 'This row') {
  if (value === null) return null;
  if (typeof value !== 'string' || value.length > 5000 || /[\r\n]/.test(value)) throw new Error(`${id}: ${variable.name} must be a single line of SysML expression text (up to 5,000 characters) or empty.`);
  return value.trim() ? value : null;
}
export function parameterUnit(value, variable) {
  if (typeof value !== 'string' || value.length > 100 || /[\r\n]/.test(value)) throw new Error(`${variable.name}: units must be a single line of text (up to 100 characters).`);
  return value.trim();
}
export function validateWorkspace(workspace, catalog = domainTypes, products = null) {
  const fail = message => { throw new Error(message); };
  if (workspace && workspace.version !== WORKSPACE_VERSION) fail(`Workspace format ${workspace.version} differs from app format ${WORKSPACE_VERSION}. Restart the requirements UI server and reload this page.`);
  if (!workspace || !Array.isArray(workspace.stakeholders) || !Array.isArray(workspace.elements)
      || !Array.isArray(workspace.statements) || !Array.isArray(workspace.variables) || !Array.isArray(workspace.components)) fail('Invalid workspace format.');
  if (workspace.variables.length > 64) fail('A workspace can contain up to 64 variable columns.');
  const variableNames = new Set();
  for (const variable of workspace.variables) {
    if (!variable || !validVariableName(variable.name)) fail('Variable names must start with a letter or underscore and contain letters, digits or underscores. Reserved names and row IDs are excluded.');
    if (variableNames.has(variable.name)) fail(`The variable ${variable.name} already exists.`);
    if (!['integer', 'float'].includes(variable.type)) fail(`${variable.name}: choose Integer or Float.`);
    if (variable.unit !== undefined) parameterUnit(variable.unit, variable);
    variableNames.add(variable.name);
  }
  const rows = allRows(workspace), keys = new Set(), ids = new Set();
  if (rows.length > 10000) fail('A workspace can contain up to 10,000 rows.');
  for (const row of rows) {
    if (!row || typeof row.key !== 'string' || !/^[a-zA-Z0-9_-]{1,80}$/.test(row.key)) fail('Every row needs a valid internal key.');
    if (keys.has(row.key)) fail('Row keys must be unique.');
    keys.add(row.key);
    if (typeof row.id !== 'string') fail('Every row needs a text ID.');
    if (ids.has(row.id)) fail(`The ID ${row.id} is already in use.`);
    ids.add(row.id);
  }
  for (const row of [...workspace.stakeholders, ...workspace.elements]) {
    if (!/^[A-Z]{3}$/.test(row.id)) fail('Element IDs must be three uppercase letters, such as LPR.');
    if (typeof row.name !== 'string' || row.name.length > 10000) fail(`${row.id}: invalid name.`);
  }
  for (const row of workspace.stakeholders) {
    if (!stakeholderTypes.some(type => type.name === row.type)) fail(`${row.id}: choose a stakeholder type.`);
  }
  for (const row of workspace.elements) {
    if (!allowedDefinitions(workspace, row.owner, catalog).some(type => type.model === row.definition)) fail(`${row.id}: choose a type from the generic mission model for this table.`);
  }
  const contexts = new Set(tabsFor(workspace, catalog).map(tab => tab.key));
  const templates = new Map(catalog.flatMap(type => type.requirements ?? []).map(template => [template.model, template]));
  for (const row of workspace.statements) {
    if (!/^[A-Z]{3}\d{3}$/.test(row.id)) fail('Statement IDs must be three uppercase letters and three digits, such as REQ001.');
    if (!contexts.has(row.context)) fail(`${row.id}: the tab does not exist.`);
    if (!statementKinds.includes(row.kind)) fail(`${row.id}: choose a statement type.`);
    if (typeof row.text !== 'string' || row.text.length > 50000) fail(`${row.id}: invalid statement.`);
    if (row.definition && (!templates.has(row.definition) || row.kind !== 'Requirement')) fail(`${row.id}: choose a generic requirement definition.`);
    if (row.definition) {
      const template = templates.get(row.definition);
      const owner = workspace.elements.find(element => element.key === row.context);
      if (template.context === 'mission' ? row.context !== 'mission' : catalog.find(type => type.model === owner?.definition)?.role !== 'eps') fail(`${row.id}: the generic requirement belongs to a different table.`);
    }
    if (row.origin !== undefined && (typeof row.origin !== 'string' || row.origin.length > 2000)) fail(`${row.id}: invalid requirement provenance.`);
    if (row.rationale !== undefined && (typeof row.rationale !== 'string' || row.rationale.length > 10000)) fail(`${row.id}: rationale must be text up to 10,000 characters.`);
    if (Object.hasOwn(row, 'formulas')) fail(`${row.id}: store every parameter expression in its cell. Separate formula maps are no longer supported.`);
    if (Object.hasOwn(row, 'verified')) fail(`${row.id}: verification is computed from a SysML condition. Manual flags are not supported.`);
    if (typeof row.condition !== 'string' || row.condition.length > 5000 || /[\r\n]/.test(row.condition)) fail(`${row.id}: verification must be a single line of SysML (up to 5,000 characters).`);
    if (!Array.isArray(row.sources) || new Set(row.sources).size !== row.sources.length || row.sources.some(source => !keys.has(source))) fail(`${row.id}: choose existing source rows without duplicates.`);
    const assignable = new Set(assignableElements(workspace, row).map(element => element.key));
    if (!Array.isArray(row.affected) || new Set(row.affected).size !== row.affected.length || row.affected.some(key => !assignable.has(key))) fail(`${row.id}: affected elements must belong to the left table of this tab.`);
    if (!row.parameters || typeof row.parameters !== 'object' || Object.keys(row.parameters).some(name => !variableNames.has(name))) fail(`${row.id}: invalid variables.`);
    const markers = requirementMarkers(row.text);
    if (markers.errors.length) fail(`${row.id}: ${markers.errors[0]}`);
    if (markers.names.some(name => !variableNames.has(name))) fail(`${row.id}: declare each $$variable$$ before saving.`);
    for (const variable of workspace.variables) {
      const value = row.parameters[variable.name];
      parameterExpression(value, variable, row.id);
      const nativeType = templates.get(row.definition)?.attributes?.[variable.name];
      if (nativeType === 'Integer' && variable.type !== 'integer') fail(`${row.id}: ${variable.name} must remain an Integer.`);
      if (nativeType === 'Boolean' && value !== null && value.trim()) fail(`${row.id}: ${variable.name} is a native Boolean assessment input, not a numeric column.`);
    }
  }
  for (const row of workspace.components) {
    if (!/^[A-Z]{3}\d{3}$/.test(row.id)) fail('Component IDs must be three uppercase letters and three digits, such as CMP001.');
    const owner = workspace.elements.find(element => element.key === row.owner);
    if (!owner || catalog.find(type => type.model === owner.definition)?.role !== 'eps') fail(`${row.id}: COTS components must belong to an EPS tab.`);
    if (typeof row.product !== 'string' || !/^[a-z0-9_]+$/.test(row.product) || (products && !products.some(product => product.id === row.product))) fail(`${row.id}: choose a component from the COTS catalog.`);
    if (Object.hasOwn(row, 'verified')) fail(`${row.id}: component verification is computed from its affected requirements.`);
    const requirements = new Set(componentRequirements(workspace, row).map(statement => statement.key));
    if (!Array.isArray(row.requirements) || new Set(row.requirements).size !== row.requirements.length || row.requirements.some(key => !requirements.has(key))) fail(`${row.id}: choose requirements from this EPS tab without duplicates.`);
  }
  const statements = new Map(workspace.statements.map(row => [row.key, row]));
  const visited = new Set(), visiting = new Set();
  for (const root of workspace.statements) {
    const stack = [[root.key, false]];
    while (stack.length) {
      const [key, leaving] = stack.pop();
      if (!statements.has(key)) continue;
      if (leaving) { visiting.delete(key); visited.add(key); continue; }
      if (visiting.has(key)) fail(`${root.id}: source links cannot form a cycle.`);
      if (visited.has(key)) continue;
      visiting.add(key); stack.push([key, true]);
      for (const source of statements.get(key).sources) stack.push([source, false]);
    }
  }
  return workspace;
}

// Quoted cells can contain tabs and line breaks, as in a Google Sheets copy.
export function parseTSV(text) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '"' && (quoted || cell === '')) {
      if (quoted && text[i + 1] === '"') { cell += '"'; i++; }
      else quoted = !quoted;
    } else if (!quoted && (char === '\t' || char === '\n' || char === '\r')) {
      row.push(cell); cell = '';
      if (char !== '\t') { rows.push(row); row = []; if (char === '\r' && text[i + 1] === '\n') i++; }
    } else cell += char;
  }
  if (cell !== '' || row.length || !rows.length) rows.push([...row, cell]);
  return rows;
}
