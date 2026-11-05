import { allocationParameter, allocationReference, budgetParameter, powerReference } from './power.mjs';

const binaryOperators = new Set(['+', '-', '*', '/', '^', '**', '<', '<=', '>', '>=', '==', '!=', 'and', 'or', 'xor', 'implies']);
const functions = {
  sqrt: { arity: 1, evaluate: Math.sqrt, model: 'RealFunctions::sqrt' },
  arccos: { arity: 1, evaluate: Math.acos, model: 'TrigFunctions::arccos' },
  floor: { arity: 1, evaluate: Math.floor, model: 'RealFunctions::floor' },
  abs: { arity: 1, evaluate: Math.abs, model: 'RealFunctions::abs' },
  min: { arity: 2, evaluate: Math.min, model: 'RealFunctions::min' },
  max: { arity: 2, evaluate: Math.max, model: 'RealFunctions::max' },
};

// A deliberately small SysML expression grammar. No JavaScript is executed.
export function parseExpression(source, { ranges } = {}) {
  if (typeof source !== 'string' || source.length > 5000) throw new Error('Expressions can contain up to 5,000 characters.');
  const tokens = [];
  let position = 0;
  while (position < source.length) {
    const rest = source.slice(position);
    const space = rest.match(/^\s+/);
    if (space) { position += space[0].length; continue; }
    const match = rest.match(/^"(?:[^"\\\r\n]|\\["\\nrt])*"/)
      ?? rest.match(/^(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/)
      ?? rest.match(/^[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*/)
      ?? rest.match(/^(?:<=|>=|==|!=|\*\*|[+*/^,<>()!?\-.])/);
    if (!match) throw new Error(`Unexpected character at position ${position + 1}.`);
    tokens.push({ value: match[0], position: position + 1 });
    position += match[0].length;
    if (tokens.length > 2048) throw new Error('The expression has too many tokens.');
  }
  tokens.push({ value: '', position: position + 1 });
  let cursor = 0, depth = 0;
  const peek = () => tokens[cursor]?.value ?? '';
  const take = () => tokens[cursor++]?.value ?? '';
  const expect = value => { if (take() !== value) throw new Error(`Expected “${value}”.`); };
  const locate = (node, start) => {
    ranges?.set(node, [start, tokens[cursor - 1].position - 1 + tokens[cursor - 1].value.length]);
    return node;
  };
  function primary() {
    if (++depth > 64) throw new Error('The expression is nested too deeply.');
    let node;
    const start = tokens[cursor].position - 1, value = take();
    if (value === '(') { node = conditional(); expect(')'); }
    else if (value === 'if') {
      const condition = conditional(); expect('?');
      const consequent = conditional(); expect('else');
      node = { kind: 'conditional', condition, consequent, alternate: conditional() };
    } else if (value === 'mode') node = { kind: 'mode' };
    else if (value === 'null') node = { kind: 'literal', value: null };
    else if (value.startsWith('"')) node = { kind: 'literal', value: JSON.parse(value), start: tokens[cursor - 1].position - 1, end: tokens[cursor - 1].position - 1 + value.length };
    else if (value === 'true' || value === 'false') node = { kind: 'literal', value: value === 'true' };
    else if (/^(?:\d|\.\d)/.test(value)) {
      if (!Number.isFinite(Number(value))) throw new Error('Numeric literals must be finite.');
      node = { kind: 'literal', value: Number(value) };
    } else if (/^[A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*$/.test(value) && !binaryOperators.has(value) && !['not', 'else', 'then'].includes(value)) {
      if (value === 'pi' || value === 'TrigFunctions::pi') node = { kind: 'constant', name: 'pi' };
      else if (peek() === '(') {
        const name = Object.hasOwn(functions, value) ? value : Object.keys(functions).find(name => functions[name].model === value);
        if (!name) throw new Error(`Unsupported function “${value}”.`);
        take();
        const args = [conditional()];
        while (peek() === ',') { take(); args.push(conditional()); }
        expect(')');
        if (args.length !== functions[name].arity) throw new Error(`${value} requires ${functions[name].arity} argument(s).`);
        node = { kind: 'call', name, args };
      } else if (peek() === '.') {
        take();
        const name = take();
        if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) throw new Error('Expected a variable name after the row ID.');
        node = { kind: 'reference', id: value, name };
      } else node = { kind: 'variable', name: value };
    } else throw new Error(`Expected a number, variable or parenthesized expression near “${value || 'end'}”.`);
    depth--;
    return locate(node, start);
  }
  function unary() {
    if (['+', '-', 'not'].includes(peek())) {
      if (++depth > 64) throw new Error('The expression is nested too deeply.');
      const start = tokens[cursor].position - 1;
      const node = { kind: 'unary', operator: take(), operand: unary() };
      depth--;
      return locate(node, start);
    }
    return power();
  }
  const chain = (next, operators) => () => {
    const start = tokens[cursor].position - 1;
    let node = next();
    while (operators.includes(peek())) node = locate({ kind: 'binary', operator: take(), left: node, right: next() }, start);
    return node;
  };
  function power() {
    const start = tokens[cursor].position - 1, left = primary();
    if (!['^', '**'].includes(peek())) return left;
    const operator = take();
    if (++depth > 64) throw new Error('The expression is nested too deeply.');
    const node = { kind: 'binary', operator, left, right: unary() };
    depth--;
    return locate(node, start);
  }
  const multiply = chain(unary, ['*', '/']);
  const add = chain(multiply, ['+', '-']);
  const compare = chain(add, ['<', '<=', '>', '>=', '==', '!=']);
  const and = chain(compare, ['and']);
  const xor = chain(and, ['xor']);
  const or = chain(xor, ['or']);
  function implies() {
    const start = tokens[cursor].position - 1, left = or();
    if (peek() !== 'implies') return left;
    take();
    if (++depth > 64) throw new Error('The expression is nested too deeply.');
    const node = { kind: 'binary', operator: 'implies', left, right: implies() };
    depth--;
    return locate(node, start);
  }
  // A conditional may also appear as an operand or function argument.
  const conditional = () => implies();
  const ast = conditional();
  if (peek() !== '') throw new Error(`Unsupported syntax “${peek()}” at position ${tokens[cursor]?.position ?? source.length + 1}.`);
  return ast;
}

export function expressionNodes(ast) {
  const nodes = [], stack = [ast];
  while (stack.length) {
    const node = stack.pop(); nodes.push(node);
    if (node.kind === 'conditional') stack.push(node.condition, node.consequent, node.alternate);
    else if (node.kind === 'binary') stack.push(node.left, node.right);
    else if (node.kind === 'unary') stack.push(node.operand);
    else if (node.kind === 'call') stack.push(...node.args);
  }
  return nodes;
}

// Mode names are string literals paired with the built-in mode input.
export function modeReferences(source) {
  const references = [];
  for (const node of expressionNodes(parseExpression(source))) {
    if (node.kind !== 'binary' || !['==', '!='].includes(node.operator)) continue;
    const literal = node.left.kind === 'mode' ? node.right : node.right.kind === 'mode' ? node.left : null;
    if (literal?.kind === 'literal' && typeof literal.value === 'string') references.push(literal);
  }
  return references;
}

export function rewriteModeReferences(source, before, after) {
  let references;
  try { references = modeReferences(source); } catch { return source; }
  for (const node of references.filter(node => node.value === before).sort((a, b) => b.start - a.start)) {
    source = source.slice(0, node.start) + JSON.stringify(after) + source.slice(node.end);
  }
  return source;
}

export function validateReferences(ast, workspace) {
  const variables = new Set(workspace.variables.map(variable => variable.name));
  const ids = new Set(workspace.statements.map(row => row.id));
  for (const node of expressionNodes(ast)) {
    if (node.kind === 'binary' && ['==', '!='].includes(node.operator)) {
      const literal = node.left.kind === 'mode' ? node.right : node.right.kind === 'mode' ? node.left : null;
      if (literal?.kind === 'literal' && typeof literal.value === 'string'
          && !workspace.power?.modes.some(mode => mode.name === literal.value)) throw new Error(`Unknown spacecraft mode “${literal.value}”.`);
    }
    if (node.kind === 'variable' || node.kind === 'reference') {
      if (node.kind === 'reference' && (powerReference(node.id, node.name) || allocationReference(node.id, node.name))) continue;
      if (!variables.has(node.name)) throw new Error(`Unknown variable “${node.name}”.`);
      if (node.kind === 'reference' && !ids.has(node.id)) throw new Error(`Unknown row “${node.id}”.`);
    }
  }
  return ast;
}

export function expressionType(ast) {
  if (ast.kind === 'literal') return ast.value === null ? 'null' : typeof ast.value;
  if (ast.kind === 'mode') return 'string';
  if (ast.kind === 'conditional') {
    if (expressionType(ast.condition) !== 'boolean') throw new Error('A conditional requires a Boolean condition.');
    const consequent = expressionType(ast.consequent), alternate = expressionType(ast.alternate);
    if (consequent !== alternate && consequent !== 'null' && alternate !== 'null') throw new Error('Conditional branches must have the same type.');
    return consequent === 'null' ? alternate : consequent;
  }
  if (ast.kind === 'variable' || ast.kind === 'reference' || ast.kind === 'constant') return 'number';
  if (ast.kind === 'call') {
    if (!Object.hasOwn(functions, ast.name) || ast.args.length !== functions[ast.name].arity) throw new Error('Unsupported function.');
    for (const arg of ast.args) if (expressionType(arg) !== 'number') throw new Error('Functions require numeric operands.');
    return 'number';
  }
  const requireType = (node, type) => {
    if (expressionType(node) !== type) throw new Error(`This operator requires ${type === 'number' ? 'numeric' : 'Boolean'} operands.`);
  };
  if (ast.kind === 'unary') {
    const type = ast.operator === 'not' ? 'boolean' : 'number';
    requireType(ast.operand, type);
    return type;
  }
  if (ast.kind !== 'binary' || !binaryOperators.has(ast.operator)) throw new Error('Unsupported expression.');
  if (['and', 'or', 'xor', 'implies'].includes(ast.operator)) {
    requireType(ast.left, 'boolean'); requireType(ast.right, 'boolean');
    return 'boolean';
  }
  if (['==', '!='].includes(ast.operator)) {
    if (expressionType(ast.left) !== expressionType(ast.right)) throw new Error('Equality operands must have the same type.');
    return 'boolean';
  }
  requireType(ast.left, 'number'); requireType(ast.right, 'number');
  return ['<', '<=', '>', '>='].includes(ast.operator) ? 'boolean' : 'number';
}

export function evaluateExpression(ast, workspace, row, resolving = new Set(), cache = new Map(), mode = null) {
  validateReferences(ast, workspace);
  expressionType(ast);
  const variables = new Map(workspace.variables.map(variable => [variable.name, variable]));
  const rows = new Map(workspace.statements.map(item => [item.id, item]));
  const typed = (value, type) => {
    if (typeof value !== type) throw new Error(`This operator requires ${type === 'number' ? 'numeric' : 'Boolean'} operands.`);
    return value;
  };
  const valueOf = (target, name) => {
    const key = `${target.id}.${name}`, cached = cache.get(key);
    if (cached) {
      if (cached.error) throw cached.error;
      return cached.value;
    }
    if (resolving.has(key)) throw new Error(`Cyclic parameter expression at ${key}.`);
    if (resolving.size >= 64) throw new Error('Parameter expressions are nested too deeply.');
    resolving.add(key);
    try {
      const raw = target.parameters[name];
      if (raw === null || raw === undefined || (typeof raw === 'string' && !raw.trim())) {
        const error = new Error(`${key} is unset.`);
        error.pending = true;
        throw error;
      }
      if (typeof raw !== 'string') throw new Error(`${key} must contain SysML expression text.`);
      const ast = parseExpression(raw);
      if (!['number', 'null'].includes(expressionType(ast))) throw new Error(`${key} must produce a number.`);
      const value = evaluateExpression(ast, workspace, target, resolving, cache, mode);
      if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error(`${key} must produce a finite number.`);
      if (variables.get(name).type === 'integer' && !Number.isSafeInteger(value)) throw new Error(`${key} must produce a safe integer.`);
      cache.set(key, { value });
      return value;
    } catch (error) {
      cache.set(key, { error });
      throw error;
    } finally { resolving.delete(key); }
  };
  function visit(node) {
    if (node.kind === 'literal') {
      if (node.value === null) { const error = new Error('The expression is unset in this mode.'); error.pending = true; throw error; }
      return node.value;
    }
    if (node.kind === 'mode') {
      const selected = workspace.power?.modes.find(item => item.key === mode);
      if (!selected) { const error = new Error('Select a spacecraft mode.'); error.pending = true; throw error; }
      return selected.name;
    }
    if (node.kind === 'conditional') return visit(node.condition) ? visit(node.consequent) : visit(node.alternate);
    if (node.kind === 'constant') return Math.PI;
    if (node.kind === 'call') {
      const result = functions[node.name].evaluate(...node.args.map(visit));
      if (!Number.isFinite(result)) throw new Error(`${node.name} is outside its finite domain.`);
      return result;
    }
    if (node.kind === 'variable') return valueOf(row, node.name);
    if (node.kind === 'reference') {
      if (powerReference(node.id, node.name)) return budgetParameter(workspace, row, node.name);
      if (allocationReference(node.id, node.name)) return allocationParameter(workspace, row, node.name, valueOf, mode);
      return valueOf(rows.get(node.id), node.name);
    }
    if (node.kind === 'unary') {
      const value = visit(node.operand);
      if (node.operator === 'not') return !typed(value, 'boolean');
      return node.operator === '-' ? -typed(value, 'number') : typed(value, 'number');
    }
    if (node.kind !== 'binary' || !binaryOperators.has(node.operator)) throw new Error('Unsupported expression.');
    const left = visit(node.left);
    if (node.operator === 'and') return typed(left, 'boolean') && typed(visit(node.right), 'boolean');
    if (node.operator === 'or') return typed(left, 'boolean') || typed(visit(node.right), 'boolean');
    if (node.operator === 'implies') return !typed(left, 'boolean') || typed(visit(node.right), 'boolean');
    const right = visit(node.right);
    if (node.operator === 'xor') return typed(left, 'boolean') !== typed(right, 'boolean');
    if (node.operator === '==' || node.operator === '!=') {
      if (typeof left !== typeof right) throw new Error('Equality operands must have the same type.');
      return node.operator === '==' ? left === right : left !== right;
    }
    typed(left, 'number'); typed(right, 'number');
    if (node.operator === '<') return left < right;
    if (node.operator === '<=') return left <= right;
    if (node.operator === '>') return left > right;
    if (node.operator === '>=') return left >= right;
    let result;
    if (node.operator === '+') result = left + right;
    if (node.operator === '-') result = left - right;
    if (node.operator === '*') result = left * right;
    if (node.operator === '/') result = left / right;
    if (node.operator === '^' || node.operator === '**') result = left ** right;
    if (!Number.isFinite(result)) throw new Error('Arithmetic must produce a finite number.');
    return result;
  }
  return visit(ast);
}

// One evaluation pass shares cached results across parameter cells and checks.
// A fresh evaluator is created whenever the workspace changes.
export function createEvaluator(workspace, { mode = null } = {}) {
  const resolving = new Set(), cache = new Map();
  const expression = (ast, row) => evaluateExpression(ast, workspace, row, resolving, cache, mode);
  const parameter = (row, name) => expression({ kind: 'variable', name }, row);
  const checkParameter = (row, name) => {
    const raw = row.parameters[name];
    if (raw === null || (typeof raw === 'string' && !raw.trim())) return { state: 'unset', value: null, message: 'No SysML parameter expression.' };
    try {
      const value = parameter(row, name);
      return { state: 'value', value, message: `= ${value}` };
    } catch (error) {
      return { state: error.pending ? 'pending' : 'error', value: null, message: String(error.message).slice(0, 300) };
    }
  };
  return { expression, parameter, checkParameter };
}

export function evaluateChecks(workspace, { mode } = {}) {
  if (mode === undefined && workspace.power?.modes.length) {
    const modes = workspace.power.modes;
    const checks = modes.map(mode => evaluateChecks(workspace, { mode: mode.key }));
    const priority = ['error', 'fail', 'pending', 'unset', 'pass', 'varying', 'value'];
    const stateOf = results => priority.find(state => results.some(result => result.state === state));
    return workspace.statements.map((row, index) => {
      const results = checks.map(check => check[index]);
      const describe = results => results.map((result, index) => `${modes[index].name}: ${result.message}`).join('\n');
      const parameters = Object.fromEntries(workspace.variables.map(variable => {
        const cells = results.map(result => result.parameters[variable.name]);
        const same = cells.every(cell => cell.state === 'value' && cell.value === cells[0].value);
        return [variable.name, same ? cells[0] : { state: cells.every(cell => cell.state === 'value') ? 'varying' : stateOf(cells), value: null, message: describe(cells) }];
      }));
      return { key: row.key, state: stateOf(results), message: describe(results), parameters,
        values: Object.fromEntries(Object.entries(parameters).map(([name, result]) => [name, result.value])),
        modes: results.map((result, index) => ({ mode: modes[index].key, ...result })) };
    });
  }
  const evaluator = createEvaluator(workspace, { mode });
  return workspace.statements.map(row => {
    const parameters = Object.fromEntries(workspace.variables.map(variable => [variable.name, evaluator.checkParameter(row, variable.name)]));
    const values = Object.fromEntries(Object.entries(parameters).map(([name, result]) => [name, result.value]));
    const computed = { values, parameters };
    if (!row.condition.trim()) return { key: row.key, ...computed, state: 'unset', message: 'No SysML condition. Enter a Boolean expression to verify this row.' };
    try {
      const result = evaluator.expression(parseExpression(row.condition), row);
      if (typeof result !== 'boolean') throw new Error('The condition must produce true or false.');
      return { key: row.key, ...computed, state: result ? 'pass' : 'fail', message: row.condition };
    } catch (error) {
      return { key: row.key, ...computed, state: error.pending ? 'pending' : 'error', message: String(error.message).slice(0, 300) };
    }
  });
}

// Print only parsed nodes. User text is never inserted into executable model syntax.
export function printExpression(ast, reference = (id, name) => `${id}.'${name}'`, modeReference = 'spacecraft_mode.display_name') {
  const print = node => printExpression(node, reference, modeReference);
  if (ast.kind === 'literal') return JSON.stringify(ast.value);
  if (ast.kind === 'mode') return modeReference;
  if (ast.kind === 'conditional') return `(if ${print(ast.condition)} ? ${print(ast.consequent)} else ${print(ast.alternate)})`;
  if (ast.kind === 'constant') return 'TrigFunctions::pi';
  if (ast.kind === 'call') {
    const args = ast.args.map(print);
    if (ast.name === 'arccos') args[0] = `(${args[0]} as TrigFunctions::UnitBoundedReal)`;
    return `${functions[ast.name].model}(${args.join(', ')})`;
  }
  if (ast.kind === 'variable') return `'${ast.name}'`;
  if (ast.kind === 'reference') return reference(ast.id, ast.name);
  if (ast.kind === 'unary') return `(${ast.operator} ${print(ast.operand)})`;
  if (ast.kind === 'binary') return `(${print(ast.left)} ${ast.operator} ${print(ast.right)})`;
  throw new Error('Unsupported expression.');
}
