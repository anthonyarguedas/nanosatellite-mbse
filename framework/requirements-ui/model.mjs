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
const prefixes = { Requirement: 'REQ', Need: 'NED', Objective: 'OBJ', Concern: 'CON', Constraint: 'CST' };
const reserved = new Set('true false and or xor implies not if then else null constructor prototype __proto__ id key name type text kind verified sources source condition parameters externalId displayName statementKind statementText manualVerification verificationExpression verificationCondition tableName subject stakeholder context owner definition affected affectedElements'.split(' '));
export const allRows = workspace => [...workspace.stakeholders, ...(workspace.elements ?? []), ...workspace.statements];

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
export function addElementChildren(workspace, parent, catalog = domainTypes) {
  if (parent.owner !== 'mission' || !catalog.find(type => type.model === parent.definition)?.expandable) return;
  if (workspace.elements.some(row => row.owner === parent.key)) return;
  for (const type of catalog.filter(type => type.parent === parent.definition)) {
    workspace.elements.push({ key: elementKey(workspace, `${parent.key}-${type.model.split('::').at(-1)}`),
      id: nextId(workspace, 'Element', type.id ?? type.name), name: type.name, owner: parent.key, definition: type.model });
  }
}
function seedElements(workspace, catalog) {
  for (const type of catalog.filter(type => !type.parent)) {
    const row = { key: elementKey(workspace, `domain-${type.role}`), id: nextId(workspace, 'Element', type.id), name: type.name, owner: 'mission', definition: type.model };
    workspace.elements.push(row);
    addElementChildren(workspace, row, catalog);
  }
  return workspace;
}
export function emptyWorkspace(catalog = domainTypes) {
  return seedElements({ version: 4, variables: defaultVariables(), stakeholders: [], elements: [], statements: [] }, catalog);
}
export function validVariableName(name) {
  return typeof name === 'string' && /^[A-Za-z_][A-Za-z0-9_]{0,39}$/.test(name)
    && !reserved.has(name) && !/^[A-Z]{3}\d{3}$/.test(name);
}

export function tabsFor(workspace, catalog = domainTypes) {
  const tabs = [
    { key: 'external', label: 'External', leftTitle: 'Stakeholders and Third Parties', requirementsTitle: 'Stakeholder Requirements', prefix: 'REQ' },
    { key: 'mission', label: 'Mission', leftTitle: 'Mission Domain Elements', requirementsTitle: 'Mission Requirements', affectedLabel: 'Affected domain elements', prefix: 'MIS' },
  ];
  for (const element of workspace.elements.filter(row => row.owner === 'mission')) {
    const type = catalog.find(type => type.model === element.definition);
    if (!type?.expandable) continue;
    const label = element.name || type.name;
    const duplicate = workspace.elements.some(row => row.key !== element.key && row.owner === 'mission' && row.name === label);
    tabs.push({ key: element.key, label: duplicate ? `${label} (${element.id})` : label,
      leftTitle: `${label} ${type.role === 'payload' ? 'Elements' : 'Subsystems'}`,
      requirementsTitle: `${label} Requirements`, affectedLabel: type.role === 'payload' ? 'Affected elements' : 'Affected subsystems', prefix: type.prefix });
  }
  return tabs;
}
export function allowedDefinitions(workspace, owner, catalog = domainTypes) {
  if (owner === 'mission') return catalog.filter(type => !type.parent);
  const parent = workspace.elements.find(row => row.key === owner && row.owner === 'mission');
  return parent && catalog.find(type => type.model === parent.definition)?.expandable
    ? catalog.filter(type => type.parent === parent.definition) : [];
}
export const contextForRow = row => row.context ?? row.owner ?? 'external';

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
  if (data?.version !== 3) return data;
  return { ...data, version: 4, statements: data.statements.map(row => {
    const { verified, ...rest } = row;
    if (typeof verified !== 'boolean') throw new Error(`${row.id}: invalid legacy verification flag.`);
    // Preserve old checked rows as an explicit SysML literal. Unchecked rows
    // without a condition remain unverified, with no inferred false constraint.
    return { ...rest, condition: !row.condition.trim() && verified ? 'true' : row.condition };
  }) };
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
export function numeric(value, variable, id = 'This row') {
  if (value === null || value === undefined || String(value).trim() === '') return null;
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(String(value).trim()) || !Number.isFinite(Number(value))) throw new Error(`${id}: ${variable.name} must be a finite number or empty.`);
  const number = Number(value);
  if (variable.type === 'integer' && !Number.isSafeInteger(number)) throw new Error(`${id}: ${variable.name} must be a safe integer or empty.`);
  return number;
}
export function validateWorkspace(workspace, catalog = domainTypes) {
  const fail = message => { throw new Error(message); };
  if (!workspace || workspace.version !== 4 || !Array.isArray(workspace.stakeholders) || !Array.isArray(workspace.elements)
      || !Array.isArray(workspace.statements) || !Array.isArray(workspace.variables)) fail('Invalid workspace format.');
  if (workspace.variables.length > 64) fail('A workspace can contain up to 64 variable columns.');
  const variableNames = new Set();
  for (const variable of workspace.variables) {
    if (!variable || !validVariableName(variable.name)) fail('Variable names must start with a letter or underscore and contain letters, digits or underscores. Reserved names and row IDs are excluded.');
    if (variableNames.has(variable.name)) fail(`The variable ${variable.name} already exists.`);
    if (!['integer', 'float'].includes(variable.type)) fail(`${variable.name}: choose Integer or Float.`);
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
  for (const row of workspace.statements) {
    if (!/^[A-Z]{3}\d{3}$/.test(row.id)) fail('Statement IDs must be three uppercase letters and three digits, such as REQ001.');
    if (!contexts.has(row.context)) fail(`${row.id}: the tab does not exist.`);
    if (!statementKinds.includes(row.kind)) fail(`${row.id}: choose a statement type.`);
    if (typeof row.text !== 'string' || row.text.length > 50000) fail(`${row.id}: invalid statement.`);
    if (Object.hasOwn(row, 'verified')) fail(`${row.id}: verification is computed from a SysML condition. Manual flags are not supported.`);
    if (typeof row.condition !== 'string' || row.condition.length > 5000 || /[\r\n]/.test(row.condition)) fail(`${row.id}: verification must be a single line of SysML (up to 5,000 characters).`);
    if (!Array.isArray(row.sources) || new Set(row.sources).size !== row.sources.length || row.sources.some(source => !keys.has(source))) fail(`${row.id}: choose existing source rows without duplicates.`);
    const assignable = new Set(assignableElements(workspace, row).map(element => element.key));
    if (!Array.isArray(row.affected) || new Set(row.affected).size !== row.affected.length || row.affected.some(key => !assignable.has(key))) fail(`${row.id}: affected elements must belong to the left table of this tab.`);
    if (!row.parameters || typeof row.parameters !== 'object' || Object.keys(row.parameters).some(name => !variableNames.has(name))) fail(`${row.id}: invalid variables.`);
    for (const variable of workspace.variables) {
      const value = row.parameters[variable.name];
      if (value !== null && (typeof value !== 'number' || !Number.isFinite(value))) fail(`${row.id}: variables must be finite numbers or empty.`);
      numeric(value, variable, row.id);
    }
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
