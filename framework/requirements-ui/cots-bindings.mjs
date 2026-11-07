// COTS selections and editor metadata. Only the trusted Python worker reads values.
import { expressionReferences } from './expression-metadata.mjs';
import { mapWorkspaceExpressions, validVariableName } from './model.mjs';
import { verificationMethods } from './verification-methods.mjs';

export function cotsBinding(fact, { key, name }) {
  return { key, name, fact: fact.id, revision: fact.revision, type: fact.type, unit: fact.unit };
}

export function cotsBindingState(binding, facts) {
  const fact = facts.find(fact => fact.id === binding.fact);
  if (!fact) return { state: 'pending', fact: null, message: 'Record unavailable for this product. Select another record.' };
  if (binding.revision !== fact.revision || binding.type !== fact.type || binding.unit !== fact.unit) {
    return { state: 'pending', fact, message: 'Catalogue record changed. Review and update this reference.' };
  }
  return { state: 'value', fact, message: '' };
}

export function suggestedFactName(component, fact) {
  const names = new Set((component.facts ?? []).map(binding => binding.name));
  const base = fact.name.slice(0, 35);
  const candidates = [base, `${base.slice(0, 28)}_${fact.valueKind.slice(0, 10)}`];
  for (let index = 2; index <= 999; index++) candidates.push(`${base}_${index}`);
  return candidates.find(name => validVariableName(name) && !name.startsWith('__') && !names.has(name)) ?? '';
}

export function cotsUses(workspace, component, name = null) {
  const references = source => expressionReferences(source).filter(reference => reference.id === component.id && (name === null || reference.name === name));
  const uses = [];
  for (const row of workspace.statements) {
    const fields = Object.entries(row.parameters).filter(([, source]) => references(source).length).map(([field]) => field);
    for (const method of verificationMethods(row)) if (references(method.condition).length || name === null && method.component === component.key) fields.push('verification');
    if (fields.length) uses.push({ key: row.key, id: row.id, kind: 'requirement', fields: [...new Set(fields)] });
  }
  for (const script of workspace.scripts) {
    const fields = Object.entries(script.parameters).filter(([, source]) => references(source).length).map(([field]) => field);
    if (fields.length) uses.push({ key: script.key, id: script.id, kind: 'script', fields });
  }
  for (const link of workspace.power.links) {
    if (Object.values(link.previous).some(source => references(source).length)) uses.push({ key: link.eps, id: 'Saved manual load inputs', kind: 'power', fields: [] });
  }
  return uses;
}

export function cotsRenames(original, updated) {
  const renames = new Map();
  for (const before of original.facts ?? []) {
    const after = updated.facts?.find(fact => fact.key === before.key);
    if (after && before.name !== after.name) renames.set(before.name, after.name);
  }
  return renames;
}

export function rewriteCotsReferences(workspace, componentId, renames) {
  mapWorkspaceExpressions(workspace, source => {
    for (const reference of expressionReferences(source).filter(reference => reference.id === componentId && renames.has(reference.name)).reverse()) {
      source = source.slice(0, reference.start) + `${componentId}.${renames.get(reference.name)}` + source.slice(reference.fieldEnd);
    }
    return source;
  });
  return workspace;
}

export function mergeCotsDraft(base, original, edited) {
  const workspace = structuredClone(base), current = workspace.components.find(component => component.key === edited.key);
  if (!current || current.id !== original.id || current.product !== original.product
      || JSON.stringify(current.facts) !== JSON.stringify(original.facts) && JSON.stringify(current.facts) !== JSON.stringify(edited.facts)) {
    throw new Error('This COTS component or its references changed. Reopen its pane before saving.');
  }
  for (const fact of original.facts ?? []) {
    if (!edited.facts?.some(after => after.key === fact.key) && cotsUses(workspace, current, fact.name).length) {
      throw new Error(`Remove expression references to ${current.id}.${fact.name} before deleting it.`);
    }
  }
  current.facts = structuredClone(edited.facts ?? []);
  return rewriteCotsReferences(workspace, current.id, cotsRenames(original, edited));
}
