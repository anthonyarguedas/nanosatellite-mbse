const binaryOperators = new Set(['+', '-', '*', '/', '<', '<=', '>', '>=', '==', '!=', 'and', 'or', 'xor', 'implies']);

// A deliberately small SysML expression grammar. No JavaScript is executed.
export function parseExpression(source) {
  if (typeof source !== 'string' || source.length > 5000) throw new Error('Expressions can contain up to 5,000 characters.');
  const tokens = [];
  let position = 0;
  while (position < source.length) {
    const rest = source.slice(position);
    const space = rest.match(/^\s+/);
    if (space) { position += space[0].length; continue; }
    const match = rest.match(/^(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/)
      ?? rest.match(/^[A-Za-z_][A-Za-z0-9_]*/)
      ?? rest.match(/^(?:<=|>=|==|!=|[+*/<>()!\-.])/);
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
  function primary() {
    if (++depth > 64) throw new Error('The expression is nested too deeply.');
    let node;
    const value = take();
    if (value === '(') { node = implies(); expect(')'); }
    else if (value === 'true' || value === 'false') node = { kind: 'literal', value: value === 'true' };
    else if (/^(?:\d|\.\d)/.test(value)) {
      if (!Number.isFinite(Number(value))) throw new Error('Numeric literals must be finite.');
      node = { kind: 'literal', value: Number(value) };
    } else if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(value) && !binaryOperators.has(value) && value !== 'not') {
      if (peek() === '.') {
        take();
        const name = take();
        if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) throw new Error('Expected a variable name after the row ID.');
        node = { kind: 'reference', id: value, name };
      } else node = { kind: 'variable', name: value };
    } else throw new Error(`Expected a number, variable or parenthesized expression near “${value || 'end'}”.`);
    depth--;
    return node;
  }
  function unary() {
    if (['+', '-', 'not'].includes(peek())) {
      if (++depth > 64) throw new Error('The expression is nested too deeply.');
      const node = { kind: 'unary', operator: take(), operand: unary() };
      depth--;
      return node;
    }
    return primary();
  }
  const chain = (next, operators) => () => {
    let node = next();
    while (operators.includes(peek())) node = { kind: 'binary', operator: take(), left: node, right: next() };
    return node;
  };
  const multiply = chain(unary, ['*', '/']);
  const add = chain(multiply, ['+', '-']);
  const compare = chain(add, ['<', '<=', '>', '>=', '==', '!=']);
  const and = chain(compare, ['and']);
  const xor = chain(and, ['xor']);
  const or = chain(xor, ['or']);
  function implies() {
    const left = or();
    if (peek() !== 'implies') return left;
    take();
    if (++depth > 64) throw new Error('The expression is nested too deeply.');
    const node = { kind: 'binary', operator: 'implies', left, right: implies() };
    depth--;
    return node;
  }
  const ast = implies();
  if (peek() !== '') throw new Error(`Unsupported syntax “${peek()}” at position ${tokens[cursor]?.position ?? source.length + 1}.`);
  return ast;
}

export function validateReferences(ast, workspace) {
  const variables = new Set(workspace.variables.map(variable => variable.name));
  const ids = new Set(workspace.statements.map(row => row.id));
  const stack = [ast];
  while (stack.length) {
    const node = stack.pop();
    if (node.kind === 'variable' || node.kind === 'reference') {
      if (!variables.has(node.name)) throw new Error(`Unknown variable “${node.name}”.`);
      if (node.kind === 'reference' && !ids.has(node.id)) throw new Error(`Unknown row “${node.id}”.`);
    } else if (node.kind === 'binary') stack.push(node.left, node.right);
    else if (node.kind === 'unary') stack.push(node.operand);
  }
  return ast;
}

export function expressionType(ast) {
  if (ast.kind === 'literal') return typeof ast.value;
  if (ast.kind === 'variable' || ast.kind === 'reference') return 'number';
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

export function evaluateExpression(ast, workspace, row) {
  validateReferences(ast, workspace);
  expressionType(ast);
  const variables = new Map(workspace.variables.map(variable => [variable.name, variable]));
  const rows = new Map(workspace.statements.map(item => [item.id, item]));
  const typed = (value, type) => {
    if (typeof value !== type) throw new Error(`This operator requires ${type === 'number' ? 'numeric' : 'Boolean'} operands.`);
    return value;
  };
  const valueOf = (target, name) => {
    const raw = target.parameters[name];
    if (raw === null || raw === undefined || String(raw).trim() === '') {
      const error = new Error(`${target.id}.${name} is unset.`);
      error.pending = true;
      throw error;
    }
    const value = Number(raw);
    if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(String(raw).trim()) || !Number.isFinite(value)) throw new Error(`${target.id}.${name} must be a finite number.`);
    if (variables.get(name).type === 'integer' && !Number.isSafeInteger(value)) throw new Error(`${target.id}.${name} must be a safe integer.`);
    return value;
  };
  function visit(node) {
    if (node.kind === 'literal') return node.value;
    if (node.kind === 'variable') return valueOf(row, node.name);
    if (node.kind === 'reference') return valueOf(rows.get(node.id), node.name);
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
    if (!Number.isFinite(result)) throw new Error('Arithmetic must produce a finite number.');
    return result;
  }
  return visit(ast);
}

export function evaluateChecks(workspace) {
  return workspace.statements.map(row => {
    if (!row.condition.trim()) return { key: row.key, state: 'unset', message: 'No SysML condition. Enter a Boolean expression to verify this row.' };
    try {
      const result = evaluateExpression(parseExpression(row.condition), workspace, row);
      if (typeof result !== 'boolean') throw new Error('The condition must produce true or false.');
      return { key: row.key, state: result ? 'pass' : 'fail', message: row.condition };
    } catch (error) {
      return { key: row.key, state: error.pending ? 'pending' : 'error', message: String(error.message).slice(0, 300) };
    }
  });
}

// Print only parsed nodes. User text is never inserted into executable model syntax.
export function printExpression(ast, reference = (id, name) => `${id}.'${name}'`) {
  if (ast.kind === 'literal') return String(ast.value);
  if (ast.kind === 'variable') return `'${ast.name}'`;
  if (ast.kind === 'reference') return reference(ast.id, ast.name);
  if (ast.kind === 'unary') return `(${ast.operator} ${printExpression(ast.operand, reference)})`;
  if (ast.kind === 'binary') return `(${printExpression(ast.left, reference)} ${ast.operator} ${printExpression(ast.right, reference)})`;
  throw new Error('Unsupported expression.');
}
