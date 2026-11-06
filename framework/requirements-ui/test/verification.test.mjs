import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { evaluateChecks, evaluateExpression } from './helpers.mjs';

function example(condition = '') {
  return {
    variables: [{ name: 'x', type: 'float' }, { name: 'mass', type: 'float' }, { name: 'count', type: 'integer' }],
    statements: [
      { key: 'r1', id: 'REQ001', condition, parameters: { x: '3', mass: '2.5', count: '4' } },
      { key: 'r2', id: 'REQ002', condition: 'True', parameters: { x: '6', mass: '5', count: null } },
    ],
  };
}
const check = condition => evaluateChecks(example(condition))[0];

test('Python verifies local variables, row references, arithmetic and comparisons', () => {
  assert.equal(check('x <= 10 and mass <= REQ002.mass').state, 'pass');
  assert.equal(check('x > REQ002.x').state, 'fail');
  assert.equal(check('mass * count == 10 and x / 2 == 1.5').state, 'pass');
  assert.equal(check('REQ001.mass == mass').state, 'pass');
  assert.equal(check('x + 2 * 3 == 9 and (x + 2) * 3 == 15').state, 'pass');
  assert.equal(check('0 < x < 10').state, 'pass');
});

test('Python Boolean operators retain their precedence', () => {
  for (const expression of ['not (x > 10)', 'True or False and False', 'True != False', 'not False or False', 'not True or x > 0']) assert.equal(check(expression).state, 'pass', expression);
  assert.equal(check('True and False').state, 'fail');
  assert.equal(check('True != True').state, 'fail');
});

test('numeric literals support exponents, unary signs and leading decimals', () => {
  assert.equal(check('x == +3 and -x == -3 and .5 * 1e1 == 5').state, 'pass');
});

test('math uses explicit functions, radians and finite domains', () => {
  assert.equal(check('math.sqrt(9) == 3 and math.acos(1) == 0 and math.pi > 3').state, 'pass');
  assert.equal(check('-math.floor(-2.1) == 3 and min(2, 3) == 2 and max(2, 3) == 3').state, 'pass');
  assert.equal(check('-2 ** 2 == -4 and 2 ** -2 == 0.25 and 2 ** 3 ** 2 == 512').state, 'pass');
  for (const expression of ['math.sqrt(-1) > 0', 'math.acos(2) > 0', '(-2) ** 0.5 > 0', 'math.sqrt(True) > 0', 'False and math.sqrt(True) > 0']) assert.equal(check(expression).state, 'error', expression);
});

test('verification requires Boolean results and compatible operands', () => {
  for (const expression of ['x + 1', '1 and True', 'False and 1', 'not x', 'x == True']) assert.equal(check(expression).state, 'error', expression);
});

test('missing values remain pending and never become zero', () => {
  assert.equal(check('REQ002.count == 0').state, 'pending');
  assert.match(check('REQ002.count == 0').message, /REQ002.count is unset/);
  assert.equal(check('True or REQ002.count > 0').state, 'pass');
  assert.equal(check('False and REQ002.count > 0').state, 'fail');
});

test('unknown rows and fields are rejected even in unused branches', () => {
  for (const expression of ['True or UNKNOWN.mass > 0', 'missing > 0', 'REQ002.unknown > 0']) assert.equal(check(expression).state, 'error');
});

test('invalid, nonfinite and fractional Integer values produce errors', () => {
  const workspace = example('count > 0'); workspace.statements[0].parameters.count = '1.5';
  assert.equal(evaluateChecks(workspace)[0].state, 'error');
  workspace.statements[0].parameters.count = 'invalid'; assert.equal(evaluateChecks(workspace)[0].state, 'error');
  for (const expression of ['x / 0 > 1', '1e308 * 1e308 > 0', '1e999 > 0']) assert.equal(check(expression).state, 'error');
});

test('verification is computed from conditions and ignores injected flags', () => {
  assert.equal(check('').state, 'unset'); assert.equal(check('True').state, 'pass'); assert.equal(check('False').state, 'fail');
  const workspace = example(); workspace.statements[0].verified = true;
  assert.equal(evaluateChecks(workspace)[0].state, 'unset'); assert.equal(evaluateChecks(workspace)[1].state, 'pass');
});

test('arbitrary calls, assignment, object introspection and JavaScript syntax cannot execute', () => {
  for (const expression of ['alert(1)', 'Math.max(x, 1) > 0', 'x = 1', 'x += 1', 'x === 3', 'x > 0 && True',
    'while (True): pass', '(lambda: True)()', 'return True', 'REQ002["mass"] > 0', 'REQ002.mass.__class__',
    'globalThis.fetch("/api/workspace")', '__import__("os")', 'x > 1; True']) assert.equal(check(expression).state, 'error', expression);
});

test('Python parsing is bounded and malformed expressions remain errors', () => {
  for (const source of ['(', 'x +', 'x > )', 'not', 'REQ002.', '()', '-'.repeat(100) + '1 > 0', '1+'.repeat(1100) + '1 > 0']) assert.equal(check(source).state, 'error');
  assert.equal(check(' '.repeat(5001) + 'True').state, 'error');
});

test('Python expressions evaluate directly and old syntax is rejected', () => {
  assert.equal(evaluateExpression('x + count', example(), example().statements[0]), 7);
  assert.equal(check('if true ? 1 else 2').state, 'error');
});

test('browser code and the import parser contain no dynamic code execution', async () => {
  for (const file of ['../parameter-states.mjs', '../verification-methods.mjs', '../public/verification-worker.js', '../public/app.js', '../public/requirement-editor.js', '../public/verification-editor.js']) {
    const source = await readFile(new URL(file, import.meta.url), 'utf8');
    assert.doesNotMatch(source, /\beval\s*\(|\bnew\s+Function\b/);
  }
});
