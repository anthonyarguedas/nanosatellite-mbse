import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { mergeRequirementDraft, nativeParameter, parameterSource } from '../public/workbook.js';

function fixture() {
  return {
    variables: [], scripts: [], elements: [], components: [], stakeholders: [],
    power: { modes: [], loads: [], links: [] },
    statements: [{ key: 'power-cpu', context: 'cdh', id: 'PWC001', parameters: { draw_power_W: 'CPU.draw_power_W', power_limit_W: '12' } }],
    modelState: {
      componentBudgets: { cpu: { draw_power_W: '10', average_power_W: 'draw_power_W' } },
      parameters: { 'power-cpu': {}, cpu: {} },
    },
    _native: { metadata: { objects: { 'power-cpu': { linkedInputs: {
      draw_power_W: { component: 'cpu', name: 'draw_power_W', id: 'CPU', reference: 'CPU.draw_power_W' },
    } } } } },
  };
}

test('existing expression cells display component input source while preserving the requirement link', () => {
  const state = fixture(), row = state.statements[0];
  assert.equal(parameterSource(state, row, 'draw_power_W'), '10');
  assert.equal(row.parameters.draw_power_W, 'CPU.draw_power_W');
  assert.equal(parameterSource(state, row, 'power_limit_W'), '12');
  row.parameters.draw_power_W = '10 * 1.1';
  assert.equal(parameterSource(state, row, 'draw_power_W'), '10 * 1.1');
  assert.equal(state.modelState.componentBudgets.cpu.draw_power_W, '10');
});

test('canonical component edits merge without replacing newer unrelated component inputs', () => {
  const original = fixture(), edited = structuredClone(original), latest = structuredClone(original);
  edited.modelState.componentBudgets.cpu.draw_power_W = '11';
  latest.modelState.componentBudgets.cpu.average_power_W = '2';
  const merged = mergeRequirementDraft(latest, original, edited, 'power-cpu');
  assert.deepEqual(merged.modelState.componentBudgets.cpu, { draw_power_W: '11', average_power_W: '2' });
  assert.equal(merged.statements[0].parameters.draw_power_W, 'CPU.draw_power_W');
});

test('concurrent edits of the same component input report a conflict', () => {
  const original = fixture(), edited = structuredClone(original), latest = structuredClone(original);
  edited.modelState.componentBudgets.cpu.draw_power_W = '11';
  latest.modelState.componentBudgets.cpu.draw_power_W = '12';
  assert.throws(() => mergeRequirementDraft(latest, original, edited, 'power-cpu'), /changed while you were editing/);
});

test('linked native functions retain their component capability and remain read only', () => {
  const state = fixture();
  const capability = { label: 'Native input', id: 'capability' };
  state.modelState.parameters.cpu.draw_power_W = { callable: capability };
  assert.equal(nativeParameter(state, state.statements[0], 'draw_power_W'), capability);
});

test('the existing parameter table and mode selector are reused with a small owner label', async () => {
  const source = await readFile(new URL('../public/editors/requirement.js', import.meta.url), 'utf8');
  assert.match(source, /parameterSource\(draft.workspace, row\(\), name\)/);
  assert.match(source, /parameter-owner/);
  assert.match(source, /Input owned by this component/);
  assert.match(source, /data-parameter-state=/);
  assert.match(source, /binding \|\| link \? 'readonly'/);
});
