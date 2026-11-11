import assert from 'node:assert/strict';
import { test } from 'node:test';
import { emptyWorkspace, parameterExpression, parseTSV, rewriteRowReferences, validateWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { createEvaluator, evaluateChecks } from './helpers.mjs';
import { readWorkspace, validateCalculations as renderExport, serializeWorkspace as renderManaged } from './helpers.mjs';

function fixture() {
  return {
    ...emptyWorkspace(),
    variables: [{ name: 'x', type: 'float' }, { name: 'y', type: 'float' }, { name: 'count', type: 'integer' }, { name: 'z', type: 'float' }],
    statements: [
      { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'A quantity of {x}.', sources: [], affected: [], condition: '',
        parameters: { x: '1.2e3', y: 'x / 1000 + 1.3', count: '2 ** 3', z: null } },
      { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: '', sources: ['r1'], affected: [], condition: 'x == 600 and y == 602.5 and count == 2',
        parameters: { x: 'REQ001.x / 2', y: 'x + REQ001.y', count: 'math.floor(REQ001.y)', z: '3 * count' } },
    ],
  };
}

test('all parameter cells evaluate the same expression representation, even without a verification condition', () => {
  const workspace = validateWorkspace(fixture()), original = structuredClone(workspace);
  const [first, second] = evaluateChecks(workspace);
  assert.deepEqual(first.values, { x: 1200, y: 2.5, count: 8, z: null });
  assert.equal(first.state, 'unset');
  assert.equal(first.parameters.y.state, 'value');
  assert.equal(first.parameters.z.state, 'unset');
  assert.deepEqual(second.values, { x: 600, y: 602.5, count: 2, z: 6 });
  assert.equal(second.state, 'pass');
  assert.deepEqual(workspace, original);
  workspace.statements[0].parameters.x = '600 + 600';
  assert.equal(evaluateChecks(workspace)[1].state, 'pass');
  workspace.statements[1].parameters.count = '1 + 2';
  assert.equal(evaluateChecks(workspace)[1].values.count, 3);
  assert.equal(evaluateChecks(workspace)[1].state, 'fail');
});

test('parameter cells report syntax, reference, type and arithmetic errors independently', () => {
  for (const expression of ['1 +', 'missing + 1', 'XYZ999.x', 'true', 'sqrt(-1)', '1 / 0', '1e999', 'globalThis.fetch("/")', 'x = 1']) {
    const workspace = fixture(); workspace.statements[0].parameters.y = expression;
    assert.doesNotThrow(() => validateWorkspace(workspace));
    const result = evaluateChecks(workspace)[0];
    assert.equal(result.state, 'unset');
    assert.equal(result.parameters.y.state, 'error', expression);
    assert.equal(result.values.y, null);
    assert.throws(() => renderExport(workspace), /REQ001.y/);
    assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
  }
});

test('empty cells stay unset and dependent expressions stay pending', () => {
  const workspace = fixture();
  workspace.statements[0].parameters.x = null;
  const [first, second] = evaluateChecks(workspace);
  assert.equal(first.parameters.x.state, 'unset');
  assert.equal(first.parameters.y.state, 'pending');
  assert.equal(first.values.y, null);
  assert.equal(second.parameters.x.state, 'pending');
  assert.equal(second.state, 'pending');
  assert.doesNotThrow(() => renderExport(workspace));
  workspace.statements[0].parameters.x = '  ';
  assert.equal(evaluateChecks(workspace)[0].parameters.x.state, 'unset');
});

test('cycles in local or cross-row parameter expressions give errors without a source-link cycle', () => {
  for (const expressions of [['y + 1', 'x + 1'], ['REQ002.x', 'x + 1']]) {
    const workspace = fixture();
    [workspace.statements[0].parameters.x, workspace.statements[0].parameters.y] = expressions;
    assert.doesNotThrow(() => validateWorkspace(workspace));
    assert.match(evaluateChecks(workspace)[0].parameters.x.message, /Cyclic parameter expression/);
    assert.throws(() => renderExport(workspace), /Cyclic parameter expression/);
  }
});

test('Integer evaluation preserves integrality across JSON round trips', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.parameters.count = 'x / 200';
  assert.equal(createEvaluator(workspace).parameter(row, 'count'), 6);
  const source = renderExport(workspace);
  assert.equal(JSON.parse(source).statements[0].parameters.count, 'x / 200');
  assert.equal(JSON.parse(source).variables.find(variable => variable.name === 'count').type, 'integer');
  row.parameters.count = 'x / 201';
  assert.equal(evaluateChecks(workspace)[0].parameters.count.state, 'error');
  assert.throws(() => renderExport(workspace), /safe integer/);
  row.parameters.count = '9007199254740992';
  assert.equal(evaluateChecks(workspace)[0].parameters.count.state, 'error');
  row.parameters.x = null; row.parameters.count = 'x / 2';
  assert.equal(evaluateChecks(workspace)[0].parameters.count.state, 'pending');
  assert.doesNotThrow(() => renderExport(workspace));
});

test('Python math calls and constants evaluate directly', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.parameters.x = 'math.sqrt(9) + max(2, 4)'; row.parameters.y = 'math.acos(-1) / math.pi'; row.parameters.count = '2 ** 3 ** 2';
  const result = evaluateChecks(workspace)[0];
  assert.equal(result.values.x, 7); assert.equal(result.values.y, 1); assert.equal(result.values.count, 512);
});

test('current cells require expression text and reject separate formula maps', () => {
  const workspace = fixture(); workspace.statements[0].formulas = { y: 'x * 2' };
  assert.throws(() => validateWorkspace(workspace), /Separate formula maps/);
  delete workspace.statements[0].formulas; workspace.statements[0].parameters.x = 600;
  assert.throws(() => validateWorkspace(workspace), /expression text/);
});

test('storage retains expression spelling and exports equations rather than evaluated values', () => {
  const workspace = fixture(); workspace.statements[0].parameters.x = '  1.2e3 + 4  ';
  const source = renderManaged(workspace);
  assert.deepEqual(readWorkspace(source), workspace);
  const exported = renderExport(workspace);
  const stored = JSON.parse(exported);
  assert.equal(stored.statements[0].parameters.x, '  1.2e3 + 4  ');
  assert.equal(stored.statements[1].parameters.x, 'REQ001.x / 2');
  assert.equal(stored.statements[0].values, undefined);
  assert.equal(evaluateChecks(workspace)[0].values.x, 1204);
});

test('grid paste and ID renames retain parameter equations and reference identities', () => {
  const workspace = fixture(), row = workspace.statements[0];
  const cells = parseTSV('1200 / 2\tx + 1\t3 + 2\t')[0];
  workspace.variables.forEach((variable, index) => { row.parameters[variable.name] = parameterExpression(cells[index], variable, row.id); });
  assert.equal(row.parameters.x, '1200 / 2');
  assert.equal(evaluateChecks(workspace)[0].values.y, 601);
  rewriteRowReferences(workspace, new Map([['REQ001', 'NEW001']]));
  row.id = 'NEW001';
  assert.equal(workspace.statements[1].parameters.x, 'NEW001.x / 2');
  assert.equal(evaluateChecks(workspace)[1].values.x, 300);
  assert.deepEqual(workspace.statements[1].sources, ['r1']);
});

test('repeated references share evaluated results and deep recursion remains bounded', () => {
  const workspace = fixture(); workspace.statements = [];
  for (let index = 1; index <= 25; index++) {
    const id = `EXP${String(index).padStart(3, '0')}`, previous = `EXP${String(index - 1).padStart(3, '0')}`;
    workspace.statements.push({ key: id, id, condition: '', parameters: { x: index === 1 ? '1' : `${previous}.x + ${previous}.x`, y: null, count: null, z: null } });
  }
  assert.equal(evaluateChecks(workspace).at(-1).values.x, 2 ** 24);
  workspace.statements[0].parameters.x = 'x + 1';
  assert.equal(evaluateChecks(workspace).at(-1).parameters.x.state, 'error');
});

test('JSON snapshots retain pending and resolved Integer equations for Python evaluation', () => {
  const workspace = fixture(); workspace.statements[0].parameters.count = 'x / 200';
  const filled = JSON.parse(renderExport(workspace));
  assert.equal(evaluateChecks(filled)[0].values.count, 6);
  workspace.statements[0].parameters.x = null;
  const pending = JSON.parse(renderExport(workspace));
  assert.equal(evaluateChecks(pending)[0].parameters.count.state, 'pending');
});
