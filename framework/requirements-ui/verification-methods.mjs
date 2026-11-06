export function verificationMethods(row) {
  return row.verifications ?? (row.condition?.trim() ? [{ key: 'condition', condition: row.condition }] : []);
}

// Retain the original single-condition format when it represents the whole table.
export function setVerificationMethods(row, methods) {
  const populated = methods.filter(method => method.condition.trim() || method.script);
  if (populated.length === 1 && !populated[0].script) {
    row.condition = populated[0].condition;
    delete row.verifications;
  } else {
    row.condition = '';
    if (populated.length) row.verifications = structuredClone(populated);
    else delete row.verifications;
  }
}

export const runKey = (key, mode) => `${key}:${mode ?? ''}`;

// Exact context comparison invalidates execution evidence when any calculation
// input changes. Prose, check expressions and table placeholders are excluded.
export function scriptContext(workspace) {
  const sorted = rows => [...(rows ?? [])].sort((a, b) => a.key.localeCompare(b.key));
  return JSON.stringify({
    expressionLanguage: workspace.expressionLanguage ?? 'python',
    variables: workspace.variables,
    statements: sorted(workspace.statements.filter(row => row.id)).map(({ key, id, parameters, definition, context, powerScope }) =>
      ({ key, id, parameters, definition, context, powerScope })),
    elements: sorted(workspace.elements?.filter(row => row.id)), power: workspace.power,
    scripts: sorted(workspace.scripts),
  }, (_, value) => value && typeof value === 'object' && !Array.isArray(value)
    ? Object.fromEntries(Object.keys(value).sort().map(key => [key, value[key]])) : value);
}

export function scriptInstance(definition, { key, id }) {
  return { key, id, name: definition.name, definition: definition.id, revision: definition.revision,
    inputs: structuredClone(definition.inputs), outputs: structuredClone(definition.outputs),
    parameters: Object.fromEntries(definition.inputs.map(input => [input.name, null])) };
}
