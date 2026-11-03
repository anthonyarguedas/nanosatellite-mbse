import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { evaluateChecks, evaluateExpression, expressionType, parseExpression, printExpression } from '../verification.mjs';

function example(condition = '') {
  return {
    variables: [{ name: 'x', type: 'float' }, { name: 'mass', type: 'float' }, { name: 'count', type: 'integer' }],
    statements: [
      { key: 'r1', id: 'REQ001', condition, parameters: { x: '3', mass: '2.5', count: '4' } },
      { key: 'r2', id: 'REQ002', condition: 'true', parameters: { x: '6', mass: '5', count: null } },
    ],
  };
}
const check = condition => evaluateChecks(example(condition))[0];

test('local variables, row references, arithmetic and comparisons evaluate', () => {
  assert.equal(check('x <= 10 and mass <= REQ002.mass').state, 'pass');
  assert.equal(check('x > REQ002.x').state, 'fail');
  assert.equal(check('mass * count == 10 and x / 2 == 1.5').state, 'pass');
  assert.equal(check('REQ001.mass == mass').state, 'pass');
  assert.equal(check('x + 2 * 3 == 9 and (x + 2) * 3 == 15').state, 'pass');
});

test('Boolean operators and precedence use SysML syntax', () => {
  for (const expression of ['not (x > 10)', 'true or false and false', 'true xor false', 'false implies false', 'true implies x > 0']) {
    assert.equal(check(expression).state, 'pass', expression);
  }
  assert.equal(check('true implies false').state, 'fail');
  assert.equal(check('true xor true').state, 'fail');
});

test('numeric literals support exponents, unary signs and leading decimals', () => {
  assert.equal(check('x == +3 and -x == -3 and .5 * 1e1 == 5').state, 'pass');
});

test('sizing math uses a fixed function set, radians and finite domains', () => {
  assert.equal(check('sqrt(9) == 3 and arccos(1) == 0 and pi > 3').state, 'pass');
  assert.equal(check('-floor(-2.1) == 3 and min(2, 3) == 2 and max(2, 3) == 3').state, 'pass');
  assert.equal(check('-2 ^ 2 == -4 and 2 ^ -2 == 0.25 and 2 ^ 3 ^ 2 == 512').state, 'pass');
  for (const expression of ['sqrt(-1) > 0', 'arccos(2) > 0', '(-2) ^ 0.5 > 0', 'sqrt(true) > 0', 'false and sqrt(true) > 0']) {
    assert.equal(check(expression).state, 'error', expression);
  }
  assert.match(printExpression(parseExpression('arccos(x) > 0')), /as TrigFunctions::UnitBoundedReal/);
});

test('conditions must have a Boolean result and operands have matching types', () => {
  for (const expression of ['x + 1', '1 and true', 'false and 1', 'not x', 'x == true', '0 < x < 10']) {
    assert.equal(check(expression).state, 'error', expression);
  }
});

test('missing variables are pending and never coerced to zero', () => {
  const result = check('REQ002.count == 0');
  assert.equal(result.state, 'pending');
  assert.match(result.message, /REQ002.count is unset/);
  assert.equal(check('true or REQ002.count > 0').state, 'pass');
  assert.equal(check('false and REQ002.count > 0').state, 'fail');
});

test('unknown rows and columns are errors, even in an unused branch', () => {
  assert.equal(check('true or UNKNOWN.mass > 0').state, 'error');
  assert.equal(check('missing > 0').state, 'error');
  assert.equal(check('REQ002.unknown > 0').state, 'error');
});

test('invalid and nonfinite values, arithmetic and integer values are errors', () => {
  const workspace = example('count > 0');
  workspace.statements[0].parameters.count = '1.5';
  assert.equal(evaluateChecks(workspace)[0].state, 'error');
  workspace.statements[0].parameters.count = 'invalid';
  assert.equal(evaluateChecks(workspace)[0].state, 'error');
  assert.equal(check('x / 0 > 1').state, 'error');
  assert.equal(check('1e308 * 1e308 > 0').state, 'error');
  assert.equal(check('1e999 > 0').state, 'error');
});

test('verification requires a SysML condition and ignores injected manual flags', () => {
  assert.equal(check('').state, 'unset');
  assert.equal(check('true').state, 'pass');
  assert.equal(check('false').state, 'fail');
  const workspace = example();
  workspace.statements[0].verified = true;
  assert.equal(evaluateChecks(workspace)[0].state, 'unset');
  assert.equal(evaluateChecks(workspace)[1].state, 'pass');
});

test('unapproved calls, assignment, JavaScript operators and object access are rejected', () => {
  const expressions = [
    'alert(1)', 'Math.max(x, 1) > 0', 'x = 1', 'x += 1', 'x === 3', 'x > 0 && true',
    'while (true) {}', '(()=>true)()', 'return true;', 'REQ002["mass"] > 0',
    'REQ002.mass.constructor', 'globalThis.fetch("/api/workspace")', 'import("/app.js")',
    'x > 1; true', 'new Function("return true")()', 'this.constructor.constructor("return true")()',
  ];
  for (const expression of expressions) assert.equal(check(expression).state, 'error', expression);
});

test('malformed and oversized expressions fail with bounded parsing', () => {
  for (const expression of ['(', 'x +', 'x > )', 'not', 'REQ002.', '()']) assert.throws(() => parseExpression(expression));
  assert.throws(() => parseExpression('('.repeat(70) + 'true' + ')'.repeat(70)), /nested/);
  assert.throws(() => parseExpression('-'.repeat(80) + '1 > 0'), /nested/);
  assert.throws(() => parseExpression('1+'.repeat(1100) + '1'), /tokens/);
  assert.throws(() => parseExpression(' '.repeat(5001)), /5,000/);
});

test('AST printing produces SysML with explicit grouping and row bindings', () => {
  const ast = parseExpression('x <= REQ002.mass and count > 0');
  assert.equal(expressionType(ast), 'boolean');
  assert.equal(printExpression(ast, (id, name) => `mission_${id}.'${name}'`), "(('x' <= mission_REQ002.'mass') and ('count' > 0))");
  assert.equal(evaluateExpression(parseExpression('x + count'), example(), example().statements[0]), 7);
});

test('the browser interpreter and worker contain no dynamic code execution', async () => {
  for (const file of ['../verification.mjs', '../public/verification-worker.js', '../public/app.js', '../public/requirement-editor.js']) {
    const source = await readFile(new URL(file, import.meta.url), 'utf8');
    assert.doesNotMatch(source, /\beval\s*\(|\bnew\s+Function\b/);
  }
});
