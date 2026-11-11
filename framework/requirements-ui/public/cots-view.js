// Read-only catalogue presentation and local editor merging.
import { expressionReferences } from '/reference-view.js';
import { verificationMethods } from '/workbook.js';

export const cotsBinding = (fact, { key, name }) => ({ key, name, fact: fact.id, revision: fact.revision, type: fact.type, unit: fact.unit });
export function cotsBindingState(binding, facts) {
  const fact = facts.find(fact => fact.id === binding.fact);
  if (!fact) return { state: 'pending', fact: null, message: 'Record unavailable for this product. Select another record.' };
  if (binding.revision !== fact.revision || binding.type !== fact.type || binding.unit !== fact.unit) return { state: 'pending', fact, message: 'Catalogue record changed. Review and update this reference.' };
  return { state: 'value', fact, message: '' };
}
export function cotsUses(workspace, component, name = null) {
  const references = source => expressionReferences(source).filter(reference => reference.id === component.id && (name === null || reference.name === name));
  const uses = [];
  for (const row of workspace.statements) {
    const fields = Object.entries(row.parameters).filter(([, source]) => references(source).length).map(([field]) => field);
    for (const method of verificationMethods(row, workspace)) if (references(method.condition).length || name === null && method.component === component.key) fields.push('verification');
    if (fields.length) uses.push({ key: row.key, id: row.id, kind: 'requirement', fields: [...new Set(fields)] });
  }
  for (const script of workspace.scripts) {
    const fields = Object.entries(script.parameters).filter(([, source]) => references(source).length).map(([field]) => field);
    if (fields.length) uses.push({ key: script.key, id: script.id, kind: 'script', fields });
  }
  return uses;
}
export function mergeCotsDraft(base, original, edited) {
  const workspace = structuredClone(base), current = workspace.components.find(component => component.key === edited.key);
  if (!current || current.id !== original.id || current.product !== original.product
      || JSON.stringify(current.facts) !== JSON.stringify(original.facts) && JSON.stringify(current.facts) !== JSON.stringify(edited.facts)) throw new Error('This COTS component changed. Reopen its pane before saving.');
  current.facts = structuredClone(edited.facts ?? []);
  return workspace;
}
