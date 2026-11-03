import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  availableSources, emptyWorkspace, migrateWorkspace, nextId, parameterExpression, parameterUnit, parseTSV,
  stakeholderTypes, statementKinds, validVariableName, validateWorkspace, WORKSPACE_VERSION,
} from '../model.mjs';
import { readWorkspace, renderManaged, updateSource } from '../sysml.mjs';
import { createEvaluator } from '../verification.mjs';

function example() {
  return {
    ...emptyWorkspace(),
    elements: [],
    stakeholders: [{ key: 's1', id: 'OPS', name: 'Mission team', type: 'Mission Stakeholder' }],
    statements: [
      { key: 'n1', id: 'NED001', context: 'external', affected: [], sources: ['s1'], kind: 'Need', text: 'Observe for {x} months.', condition: '', parameters: { x: '12', y: null, z: null, a: null } },
      { key: 'r1', id: 'REQ001', context: 'external', affected: [], sources: ['n1', 's1'], kind: 'Requirement', text: 'The mission shall last {x} months.', condition: 'true', parameters: { x: '12', y: '-1.5', z: '0', a: null } },
    ],
  };
}

test('empty and populated workspaces validate', () => {
  assert.equal(validateWorkspace(emptyWorkspace()).version, WORKSPACE_VERSION);
  assert.deepEqual(validateWorkspace(example()), example());
});

test('IDs follow the two formats and are unique', () => {
  const workspace = example();
  assert.equal(nextId(workspace, 'Stakeholder', 'Launch provider'), 'LAU');
  assert.equal(nextId(workspace, 'Requirement'), 'REQ002');
  assert.equal(nextId(workspace, 'Objective'), 'OBJ001');
  workspace.statements[0].id = 'REQ001';
  assert.throws(() => validateWorkspace(workspace), /already in use/);
  for (const id of ['OP', 'OPSS', 'ops', 'OP1']) {
    const invalid = example(); invalid.stakeholders[0].id = id;
    assert.throws(() => validateWorkspace(invalid), /three uppercase letters/);
  }
  for (const id of ['REQ1', 'REQ-001', 'req001', 'REQ0001', 'RE1001']) {
    const invalid = example(); invalid.statements[0].id = id;
    assert.throws(() => validateWorkspace(invalid), /three digits/);
  }
});

test('renaming a visible ID preserves all source links', () => {
  const workspace = example();
  workspace.stakeholders[0].id = 'MIS'; workspace.statements[0].id = 'MIS001';
  assert.doesNotThrow(() => validateWorkspace(workspace));
  assert.deepEqual(workspace.statements[1].sources, ['n1', 's1']);
});

test('source choices are rows and exclude self and descendants', () => {
  assert.deepEqual(availableSources(example(), 'n1').map(row => row.key), ['s1']);
  assert.deepEqual(availableSources(example(), 'r1').map(row => row.key), ['s1', 'n1']);
});

test('missing, duplicate, self-referential and cyclic source rows are rejected', () => {
  for (const sources of [['missing'], ['n1'], ['r1'], ['s1', 's1'], ['stakeholders']]) {
    const workspace = example(); workspace.statements[0].sources = sources;
    assert.throws(() => validateWorkspace(workspace), /source/);
  }
});

test('multiple source paths in an acyclic graph validate', () => {
  const workspace = example();
  workspace.statements.push({ ...workspace.statements[1], key: 'r2', id: 'REQ002', sources: ['r1', 'n1'] });
  assert.doesNotThrow(() => validateWorkspace(workspace));
});

test('every parameter stores expression text, including literals, equations and invalid drafts', () => {
  assert.deepEqual(validateWorkspace(example()).statements[1].parameters, { x: '12', y: '-1.5', z: '0', a: null });
  const variable = { name: 'count', type: 'integer' };
  for (const expression of ['1.2e3', 'NED001.x * 2', '  2 + 3  ', 'invalid(', '1.5']) assert.equal(parameterExpression(expression, variable), expression);
  assert.equal(parameterExpression('', variable), null);
  assert.equal(parameterExpression('  ', variable), null);
  for (const value of [12, NaN, Infinity, undefined, {}, '1\n+2', ' '.repeat(5001)]) {
    const workspace = example(); workspace.statements[0].parameters.x = value;
    assert.throws(() => validateWorkspace(workspace), /SysML expression text/);
  }
});

test('dynamic variable columns validate names, types and values', () => {
  const workspace = example();
  workspace.variables.push({ name: 'cell_count', type: 'integer' });
  workspace.statements.forEach(row => { row.parameters.cell_count = 'x / 4'; });
  assert.doesNotThrow(() => validateWorkspace(workspace));
  assert.equal(createEvaluator(workspace).parameter(workspace.statements[0], 'cell_count'), 3);
  workspace.statements[0].parameters.cell_count = '3.2';
  assert.doesNotThrow(() => validateWorkspace(workspace));
  assert.throws(() => createEvaluator(workspace).parameter(workspace.statements[0], 'cell_count'), /safe integer/);
  for (const name of ['and', 'not', 'REQ001', 'id', 'text', 'rationale', '__proto__', 'bad-name', '2mass']) assert.equal(validVariableName(name), false);
  for (const name of ['mass', 'cell_count', '_margin']) assert.equal(validVariableName(name), true);
  workspace.variables.push({ name: 'x', type: 'float' });
  assert.throws(() => validateWorkspace(workspace), /already exists/);
});

test('optional units persist without changing expressions or numeric evaluation', () => {
  const workspace = example(), variable = workspace.variables[0];
  variable.unit = 'm^2/s^2';
  assert.equal(parameterUnit('  m^2/s^2  ', variable), 'm^2/s^2');
  assert.equal(parameterUnit('', variable), '');
  assert.doesNotThrow(() => validateWorkspace(workspace));
  assert.equal(createEvaluator(workspace).parameter(workspace.statements[0], 'x'), 12);
  assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
  for (const unit of [null, 1, {}, 'm\ns', 'm\rs', 'm'.repeat(101)]) {
    variable.unit = unit;
    assert.throws(() => validateWorkspace(workspace), /units must be a single line/);
  }
});

test('rationale supports multiline text, empty values and lossless SysML storage', () => {
  const workspace = example(), row = workspace.statements[0];
  row.origin = 'final_report/design-proposal.tex#eq:orbit-period';
  row.rationale = `${row.origin}\nUse the sourced constants with \"documented margins\" and */.`;
  assert.doesNotThrow(() => validateWorkspace(workspace));
  const generated = renderManaged(workspace);
  assert.deepEqual(readWorkspace(generated), workspace);
  assert.match(generated, /attribute rationale : String =/);
  assert.match(generated, /attribute sourceReference : String =/);
  row.rationale = '';
  assert.deepEqual(readWorkspace(renderManaged(workspace)).statements[0].rationale, '');
  for (const rationale of [null, 42, {}, 'a'.repeat(10001)]) {
    row.rationale = rationale;
    assert.throws(() => validateWorkspace(workspace), /rationale must be text/);
  }
});

test('invalid kinds, manual flags and duplicate keys are rejected', () => {
  for (const edit of [w => { w.stakeholders[0].type = 'Deployer'; }, w => { w.statements[0].kind = 'Unknown'; },
    w => { w.statements[0].verified = 'true'; }, w => { w.statements[0].key = 's1'; }]) {
    const workspace = example(); edit(workspace); assert.throws(() => validateWorkspace(workspace));
  }
});

test('TSV accepts quoted multiline cells, escaped quotes, CRLF and trailing cells', () => {
  assert.deepEqual(parseTSV('A\t"line 1\nline 2"\tTRUE\r\nB\t"a ""quote"""\t\r\n'), [
    ['A', 'line 1\nline 2', 'TRUE'], ['B', 'a "quote"', ''],
  ]);
  assert.deepEqual(parseTSV('one\ttwo\t'), [['one', 'two', '']]);
});

test('old data preserves checked status as a SysML literal while retaining values and links', () => {
  const old = { version: 1, stakeholders: [{ key: 's1', id: 'STK-001', name: 'Team', type: 'Mission Stakeholder' }],
    statements: [{ key: 'r1', id: 'REQ-001', kind: 'Requirement', text: 'Original text', source: 's1', verified: true, parameters: { x: 2, y: null, z: 0, a: null } }] };
  const upgraded = validateWorkspace(migrateWorkspace(old));
  assert.equal(upgraded.stakeholders[0].id, 'STK');
  assert.equal(upgraded.statements[0].id, 'REQ001');
  assert.deepEqual(upgraded.statements[0].sources, ['s1']);
  assert.equal(Object.hasOwn(upgraded.statements[0], 'verified'), false);
  assert.equal(upgraded.statements[0].parameters.x, '2');
  assert.equal(upgraded.statements[0].condition, 'true');
  assert.deepEqual(readWorkspace(`// <requirements-ui>\n/* requirements-ui:data\n${JSON.stringify(old)}\nrequirements-ui:end-data */\n// </requirements-ui>`), upgraded);
});

test('version 3 manual checks migrate to condition-only verification without losing formulas', () => {
  const old = example();
  old.version = 3;
  old.statements[0] = { ...old.statements[0], verified: true, condition: '' };
  old.statements[1] = { ...old.statements[1], verified: false, condition: '' };
  old.statements.push({ ...old.statements[1], key: 'r2', id: 'REQ002', verified: true, condition: 'x < 0' });
  const migrated = validateWorkspace(migrateWorkspace(old));
  assert.equal(migrated.version, WORKSPACE_VERSION);
  assert.deepEqual(migrated.statements.map(row => row.condition), ['true', '', 'x < 0']);
  assert.ok(migrated.statements.every(row => !Object.hasOwn(row, 'verified')));
  assert.deepEqual(migrated.statements.map(row => row.parameters), old.statements.map(row => row.parameters));
  assert.doesNotMatch(renderManaged(migrated), /manualVerification/);
});

test('manual flags cannot be written to the current schema', () => {
  for (const value of [true, false, 'true']) {
    const workspace = example(); workspace.statements[0].verified = value;
    assert.throws(() => validateWorkspace(workspace), /computed from a SysML condition/);
  }
});

test('SysML round trips data and preserves content outside its managed section', () => {
  const workspace = example(); workspace.statements[0].text = 'A quote: "Olá". A terminator: */.\nA new line.';
  const original = 'package Existing { part def Satellite; }\n';
  const source = updateSource(original, workspace) + '\npackage After {}\n';
  assert.deepEqual(readWorkspace(source), workspace);
  const updated = updateSource(source, emptyWorkspace());
  assert.ok(updated.startsWith(original)); assert.ok(updated.endsWith('\npackage After {}\n'));
  assert.deepEqual(readWorkspace(updated), emptyWorkspace());
  assert.equal((updated.match(/package MissionRequirements/g) ?? []).length, 1);
});

test('mission SysML imports generic types and emits all source dependencies', () => {
  const generated = renderManaged(example());
  assert.match(generated, /private import External::\*/);
  assert.match(generated, /External::MissionStakeholders::MissionStakeholder/);
  assert.match(generated, /requirement statement_r1/);
  assert.match(generated, /attribute statement_n1/);
  assert.match(generated, /dependency from statement_r1 to statement_n1/);
  assert.match(generated, /dependency from statement_r1 to stakeholder_s1/);
  assert.match(generated, /attribute 'z' : Real\[0\.\.1\] = 0;/);
  assert.match(generated, /attribute 'a' : Real\[0\.\.1\];/);
});

test('valid conditions generate native SysML constraints with resolved row references', () => {
  const workspace = example(); workspace.statements[1].condition = 'x <= NED001.x and y < 0';
  const generated = renderManaged(workspace);
  assert.match(generated, /require constraint verification/);
  assert.match(generated, /statement_n1\.'x'/);
  assert.doesNotMatch(generated, /manualVerification/);
  workspace.statements[1].condition = 'alert(1)';
  const invalid = renderManaged(workspace);
  assert.doesNotMatch(invalid, /require constraint verification/);
  assert.match(invalid, /invalid or unresolved/);
  assert.deepEqual(readWorkspace(invalid), workspace);
});

test('all types and statement kinds serialize', () => {
  const workspace = emptyWorkspace();
  workspace.stakeholders = stakeholderTypes.map((type, index) => ({ key: `s${index}`, id: `AA${String.fromCharCode(65 + index)}`, name: type.name, type: type.name }));
  workspace.statements = statementKinds.map((kind, index) => ({ ...example().statements[0], key: `r${index}`, id: `REQ00${index}`, sources: ['s0'], kind }));
  const generated = renderManaged(workspace);
  for (const type of stakeholderTypes) assert.ok(generated.includes(type.model));
  assert.deepEqual(readWorkspace(generated), workspace);
});

test('Windows line endings survive reading and updating', () => {
  const original = 'package Existing {}\r\n';
  const source = updateSource(original, example());
  assert.deepEqual(readWorkspace(source), example());
  const updated = updateSource(source, emptyWorkspace());
  assert.deepEqual(readWorkspace(updated), emptyWorkspace());
  assert.ok(updated.startsWith(original)); assert.equal(updated.replaceAll('\r\n', '').includes('\n'), false);
});

test('different keys generate different SysML identifiers', () => {
  const workspace = example(); workspace.statements[0].key = 'a-b'; workspace.statements[1].key = 'a_b'; workspace.statements[1].sources = ['a-b'];
  assert.match(renderManaged(workspace), /dependency from statement_a_ub to statement_a_hb/);
});

test('malformed managed sections fail instead of discarding data', () => {
  assert.deepEqual(readWorkspace('package Existing {}'), emptyWorkspace());
  assert.throws(() => readWorkspace('// <requirements-ui>\n'), /incomplete/);
  assert.throws(() => readWorkspace('// <requirements-ui>\n// </requirements-ui>'), /missing/);
  const block = renderManaged(example());
  assert.throws(() => updateSource(`${block}\n${block}`, example()), /duplicated/);
});
