import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import {
  calculatedParameter, linkedInput, managedPowerInput, nativeParameter,
  parameterExpression, parameterInfo, parameterSource,
} from '../public/workbook.js';

const editor = await readFile(new URL('../public/editors/requirement.js', import.meta.url), 'utf8');

function fixture() {
  const binding = {
    reference: 'MISSION.budget.mass_kg', label: 'Total installed mass · MISSION',
    description: 'Sum of installed component inputs.', scope: ['mission'],
    sources: [{ key: 'cpu', reference: 'CPU.mass_kg', label: 'Processor', expression: '0.3' }],
  };
  const row = { key: 'mass-mission', id: 'MAS001', context: 'mission', parameters: { mass_kg: binding.reference } };
  const state = {
    variables: [{ name: 'mass_kg', type: 'float', unit: 'kg' }],
    statements: [row],
    power: { modes: [{ key: 'nominal', name: 'Nominal' }, { key: 'downlink', name: 'Downlink' }], links: [] },
    modelState: { parameters: { 'mass-mission': { mass_kg: { type: 'float', unit: 'kg' } } } },
    _native: { metadata: { objects: { 'mass-mission': { calculatedParameters: { mass_kg: binding } } } } },
  };
  return { binding, row, state };
}

function dependencies(state, row) {
  return {
    draft: { workspace: state }, row: () => row, calculatedParameter, linkedInput,
    managedPowerInput, nativeParameter, parameterExpression, parameterInfo,
    escape: value => String(value ?? ''),
  };
}

// Exercise the actual editor functions without a browser or a duplicate renderer.
function editorFunction(name, scope) {
  const match = editor.match(new RegExp(`  function ${name}\\(([^)]*)\\) \\{([\\s\\S]*?)\\n  \\}`));
  assert.ok(match, `Find ${name} in the editor`);
  return Function(...Object.keys(scope), `return function(${match[1]}) {${match[2]}}`)(...Object.values(scope));
}

function renderRow(state, row) {
  const match = editor.match(/rows\.map\(\(\{ variable, mode, expression \}\) => \{([\s\S]*?)\n      \}\)\.join/);
  assert.ok(match, 'Find the parameter row renderer');
  const scope = { ...dependencies(state, row), modes: state.power.modes,
    variable: parameterInfo(state, row, 'mass_kg'), mode: '', expression: parameterSource(state, row, 'mass_kg') };
  return Function(...Object.keys(scope), match[1])(...Object.values(scope));
}

test('MAS001.mass_kg uses the ordinary editable expression, mode and unit controls', () => {
  const { state, row, binding } = fixture();
  const html = renderRow(state, row);
  assert.match(html, />MISSION\.budget\.mass_kg<\/textarea>/);
  assert.match(html, /data-parameter-state="mass_kg"/);
  assert.match(html, /data-parameter-unit="mass_kg"/);
  assert.doesNotMatch(html, /readonly|disabled|data-calculated-binding|<details/);
  assert.equal(html.includes(binding.label), false);
});

test('aggregate expressions can be edited without changing their component inputs', () => {
  const { state, row } = fixture(), view = { states: null };
  const edit = editorFunction('editExpression', { ...dependencies(state, row), stateView: () => view, queueStates: () => {} });
  edit('mass_kg', '', 'MISSION.budget.mass_kg * 1.1');
  assert.equal(row.parameters.mass_kg, 'MISSION.budget.mass_kg * 1.1');
  assert.equal(parameterSource(state, row, 'mass_kg'), row.parameters.mass_kg);
  assert.equal(calculatedParameter(state, row, 'mass_kg'), null);
});

test('aggregate expressions use the existing per-mode editing path', () => {
  const { state, row } = fixture(), view = { states: { values: { nominal: row.parameters.mass_kg } } };
  const queued = [];
  const edit = editorFunction('editExpression', { ...dependencies(state, row), stateView: () => view, queueStates: (...args) => queued.push(args) });
  edit('mass_kg', 'nominal', 'MISSION.budget.mass_kg * 1.2');
  assert.equal(view.states.values.nominal, 'MISSION.budget.mass_kg * 1.2');
  assert.equal(view.states.lastEdited, 'nominal');
  assert.deepEqual(queued, [['mass_kg', view.states]]);
});

test('aggregate unit labels use the normal unit editing path', () => {
  const { state, row } = fixture();
  const setUnit = editorFunction('setUnit', { ...dependencies(state, row), draft: { workspace: state, key: row.key } });
  setUnit('mass_kg', 'g');
  assert.equal(state.modelState.parameters[row.key].mass_kg.unit, 'g');
});

test('native Python callable bindings retain their existing read-only protection', () => {
  const { state, row } = fixture();
  state.modelState.parameters[row.key].mass_kg.callable = { label: 'module:mass' };
  const html = renderRow(state, row);
  assert.match(html, /readonly data-native-binding/);
  assert.match(html, /disabled/);
  const edit = editorFunction('editExpression', { ...dependencies(state, row), stateView: () => ({}), queueStates: () => {} });
  assert.throws(() => edit('mass_kg', '', '1'), /Native Python bindings are read only/);
});

test('linked component inputs retain canonical units while their expressions stay editable', () => {
  const { state, row } = fixture();
  row.parameters.mass_kg = 'CPU.mass_kg';
  state._native.metadata.objects[row.key].linkedInputs = { mass_kg: { component: 'cpu', name: 'mass_kg', id: 'CPU', reference: 'CPU.mass_kg' } };
  state.modelState.componentBudgets = { cpu: { mass_kg: '0.3' } };
  const html = renderRow(state, row);
  assert.match(html, />0\.3<\/textarea>/);
  assert.doesNotMatch(html, /<textarea[^>]*readonly/);
  assert.match(html, /data-parameter-unit="mass_kg"[^>]*readonly/);
});

test('budget source metadata is informational and only matches the current expression', () => {
  const { state, row, binding } = fixture();
  assert.equal(calculatedParameter(state, row, 'mass_kg'), binding);
  row.parameters.mass_kg = 'CPU.mass_kg + 1';
  assert.equal(calculatedParameter(state, row, 'mass_kg'), null);
});

test('special aggregate widgets and editing guards have been removed', async () => {
  const preview = await readFile(new URL('../public/requirement-preview.js', import.meta.url), 'utf8');
  const css = await readFile(new URL('../public/style.css', import.meta.url), 'utf8');
  assert.doesNotMatch(editor, /data-calculated-binding|calculationSourcesHTML|Boolean\(calculated\)|binding \|\| calculated/);
  assert.doesNotMatch(preview, /calculationSourcesHTML/);
  assert.doesNotMatch(css, /calculation-sources|calculation-reference/);
});
