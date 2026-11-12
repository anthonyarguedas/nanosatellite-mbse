// Browser projections and editor drafts only. Python owns the domain model.
export const allRows = state => [...state.stakeholders, ...state.elements, ...state.statements, ...state.components];
export const metadata = state => state?._native?.metadata ?? {};
export const objectMetadata = (state, key) => metadata(state).objects?.[key] ?? {};
export const tabsFor = state => metadata(state).tabs ?? [];
export const allowedDefinitions = (state, owner) => metadata(state).allowedDefinitions?.[owner] ?? [];
export const contextForRow = row => row.context ?? row.owner ?? 'external';
export const parameterExpression = value => value === null || value === undefined || value === '' ? null : value;
export const parameterUnit = value => value;
export const linkedInput = (state, row, name) => objectMetadata(state, row.key).linkedInputs?.[name];
export const parameterSource = (state, row, name) => {
  const link = linkedInput(state, row, name);
  return link && row.parameters[name] === link.reference
    ? state.modelState?.componentBudgets?.[link.component]?.[link.name] ?? null : row.parameters[name];
};
export const calculatedParameter = (state, row, name) => {
  const binding = objectMetadata(state, row.key).calculatedParameters?.[name];
  return binding && parameterSource(state, row, name) === binding.reference ? binding : null;
};
export const nativeParameter = (state, row, name) => {
  const link = linkedInput(state, row, name);
  return state.modelState?.parameters?.[link?.component ?? row.key]?.[link?.name ?? name]?.callable;
};
export const nativeCondition = (state, row, key) => state.modelState?.verificationBindings?.[row.key]?.[key];
export const parameterInfo = (state, row, name) => ({ name,
  ...(state.variables.find(variable => variable.name === name) ?? { type: 'float', unit: '' }),
  ...(state.modelState?.parameters?.[row.key]?.[name] ?? {}),
});
export const requirementParameterNames = (state, row) => [...new Set([
  ...(objectMetadata(state, row.key).parameterNames ?? []),
  ...Object.keys(state.modelState?.parameters?.[row.key] ?? {}),
  ...requirementMarkers(row.text).names,
  ...Object.entries(row.parameters).filter(([, value]) => value !== null && value !== '').map(([name]) => name),
])];
export function requirementMarkers(text) {
  // A provisional row layout. Python validates names and declares real parameters.
  const segments = text.split('$$');
  return { names: [...new Set(segments.filter((_, index) => index % 2 && index < segments.length - 1).map(name => name.trim()).filter(name => /^[A-Za-z_][A-Za-z0-9_]*$/.test(name)))], errors: [] };
}
export function declareRequirementVariables(state, row) {
  const markers = requirementMarkers(row.text);
  for (const name of markers.names) {
    if (!Object.hasOwn(row.parameters, name)) Object.defineProperty(row.parameters, name, { value: null, enumerable: true, writable: true, configurable: true });
  }
  return markers;
}
export function verificationMethods(row, state) {
  if (row.verifications) return row.verifications;
  return row.condition?.trim() || nativeCondition(state ?? {}, row, 'condition') ? [{ key: 'condition', condition: row.condition ?? '' }] : [];
}
export function setVerificationMethods(row, methods, state) {
  const populated = methods.filter(method => method.condition?.trim() || method.script || method.component || nativeCondition(state, row, method.key));
  row.condition = '';
  if (populated.length) row.verifications = structuredClone(populated);
  else delete row.verifications;
}
export const runKey = (key, mode) => `${key}:${mode ?? ''}`;
export const availableSources = (state, key) => (objectMetadata(state, key).sources ?? []).map(key => allRows(state).find(row => row.key === key)).filter(Boolean);
export const assignableElements = (state, row) => (objectMetadata(state, row.key).affected ?? []).map(key => state.elements.find(row => row.key === key)).filter(Boolean);
export const componentRequirements = (state, row) => (objectMetadata(state, row.key).requirements ?? []).map(key => state.statements.find(row => row.key === key)).filter(Boolean);
export const hasFixedBudgetScope = (state, row) => Boolean(objectMetadata(state, row.key).powerRequirement || objectMetadata(state, row.key).resourceRequirement);
export const managedPowerInput = (state, row, name) => (objectMetadata(state, row.key).managedParameters ?? []).includes(name);
export const formatParameterValue = value => Math.abs(value) > 999
  ? value.toLocaleString('en-US', { useGrouping: false, maximumFractionDigits: 0 }) : value.toPrecision(4);
export function interpolateRequirement(text, values = {}, renderParameter = (name, value) => value === null ? name : formatParameterValue(value)) {
  return text.replace(/\$\$([\s\S]*?)\$\$/g, (token, marked) => {
    const name = marked.trim(), value = values?.[name];
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) return token;
    return renderParameter(name, typeof value === 'number' && Number.isFinite(value) ? value : null);
  });
}
export function used(row, table) {
  if (table === 'components') return Boolean(row.id || row.product || row.requirements?.length || row.facts?.length);
  if (table === 'stakeholders' || table === 'elements') return Boolean(row.id || row.name || row.type || row.definition);
  return Boolean(row.id || row.sources?.length || row.affected?.length || row.text || row.condition || row.verifications?.length || row.rationale || row.kind !== 'Requirement'
    || Object.values(row.parameters ?? {}).some(value => value !== null && value !== ''));
}
export function snapshot(state) {
  const result = structuredClone(state);
  delete result._native;
  for (const table of ['stakeholders', 'elements', 'statements', 'components']) result[table] = result[table].filter(row => used(row, table));
  return result;
}

// Three-way projection merge protects newer local typing while installing a
// canonical native response. It makes no domain decisions or default values.
export function rebase(local, before, canonical) {
  const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  if (equal(local, before)) return structuredClone(canonical);
  if (canonical === undefined) return structuredClone(local);
  if (Array.isArray(local) && Array.isArray(before) && Array.isArray(canonical)) {
    const identity = value => value && typeof value === 'object' ? value.key ?? value.element ?? value.name : undefined;
    if ([...local, ...before, ...canonical].some(value => identity(value) === undefined)) return structuredClone(local);
    const old = new Map(before.map(value => [identity(value), value]));
    const fresh = new Map(canonical.map(value => [identity(value), value]));
    const result = local.map(value => rebase(value, old.get(identity(value)), fresh.get(identity(value)))).filter(value => value !== undefined);
    for (const value of canonical) if (!old.has(identity(value)) && !local.some(item => identity(item) === identity(value))) result.push(structuredClone(value));
    return result;
  }
  if (local && before && canonical && !Array.isArray(local) && typeof local === 'object' && typeof before === 'object' && typeof canonical === 'object') {
    const result = {};
    for (const key of new Set([...Object.keys(local), ...Object.keys(canonical)])) {
      if (key === '_native') continue;
      if (!Object.hasOwn(local, key) && Object.hasOwn(before, key)) continue;
      result[key] = !Object.hasOwn(local, key) ? structuredClone(canonical[key]) : rebase(local[key], before[key], canonical[key]);
    }
    return result;
  }
  return structuredClone(local);
}

export function mergeRequirementDraft(state, original, edited, key) {
  const candidate = structuredClone(state);
  const before = original.statements.find(row => row.key === key), after = edited.statements.find(row => row.key === key);
  const current = candidate.statements.find(row => row.key === key);
  if (!before || !after || !current) throw new Error('This requirement changed. Reopen its editor.');
  const merge = (previous, updated, actual, apply) => {
    if (JSON.stringify(previous) === JSON.stringify(updated)) return;
    if (JSON.stringify(actual) !== JSON.stringify(previous) && JSON.stringify(actual) !== JSON.stringify(updated)) throw new Error('This requirement or its bindings changed while you were editing. Reopen it before saving.');
    apply(structuredClone(updated));
  };
  for (const field of ['id', 'kind', 'text', 'condition', 'verifications', 'rationale']) merge(before[field], after[field], current[field], value => {
    if (value === undefined) delete current[field]; else current[field] = value;
  });
  for (const [name, value] of Object.entries(after.parameters)) merge(before.parameters[name], value, current.parameters[name], value => { current.parameters[name] = value; });
  for (const variable of edited.variables) {
    const previous = original.variables.find(item => item.name === variable.name), actual = candidate.variables.find(item => item.name === variable.name);
    if (!actual) candidate.variables.push(structuredClone(variable));
    else merge(previous, variable, actual, value => Object.assign(actual, value));
  }
  for (const script of [...original.scripts, ...edited.scripts.filter(row => !original.scripts.some(item => item.key === row.key))]) {
    const previous = original.scripts.find(item => item.key === script.key), updated = edited.scripts.find(item => item.key === script.key), actual = candidate.scripts.find(item => item.key === script.key);
    merge(previous, updated, actual, value => { candidate.scripts = candidate.scripts.filter(item => item.key !== script.key); if (value) candidate.scripts.push(value); });
  }
  const connection = value => value.power.links.find(link => link.eps === after.context);
  merge(connection(original), connection(edited), connection(candidate), value => { candidate.power.links = candidate.power.links.filter(link => link.eps !== after.context); if (value) candidate.power.links.push(value); });
  if (edited.modelState) {
    candidate.modelState ??= {};
    const componentKeys = new Set(Object.values(objectMetadata(edited, key).linkedInputs ?? {}).map(link => link.component));
    candidate.modelState.componentBudgets ??= {};
    for (const component of componentKeys) {
      const previous = original.modelState?.componentBudgets?.[component] ?? {}, updated = edited.modelState.componentBudgets?.[component] ?? {};
      const actual = candidate.modelState.componentBudgets[component] ??= {};
      for (const name of new Set([...Object.keys(previous), ...Object.keys(updated)])) merge(previous[name], updated[name], actual[name], value => { actual[name] = value; });
    }
    for (const field of ['parameters', 'verificationBindings', 'verificationNames']) {
      candidate.modelState[field] ??= {};
      const keys = new Set([key, ...edited.scripts.map(script => script.key)]);
      for (const rowKey of keys) merge(original.modelState?.[field]?.[rowKey], edited.modelState[field]?.[rowKey], candidate.modelState[field][rowKey], value => {
        if (value === undefined) delete candidate.modelState[field][rowKey]; else candidate.modelState[field][rowKey] = value;
      });
    }
  }
  candidate._native = structuredClone(edited._native ?? state._native);
  return candidate;
}

export function parseTSV(text) {
  const rows = [], row = []; let value = '', quoted = false;
  for (let index = 0; index < text.length; index++) {
    const char = text[index];
    if (char === '"' && (quoted || !value)) {
      if (quoted && text[index + 1] === '"') { value += '"'; index++; } else quoted = !quoted;
    } else if (!quoted && ['\t', '\r', '\n'].includes(char)) {
      row.push(value); value = '';
      if (char !== '\t') { rows.push(row.splice(0)); if (char === '\r' && text[index + 1] === '\n') index++; }
    } else value += char;
  }
  row.push(value); if (row.some(Boolean) || !rows.length) rows.push(row);
  return rows;
}
