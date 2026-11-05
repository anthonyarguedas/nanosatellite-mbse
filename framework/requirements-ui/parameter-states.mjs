import { parseExpression } from './verification.mjs';

// These rows are a view of one SysML expression, never separate parameters.
function closingParenthesis(source) {
  let depth = 0, quoted = false, escaped = false;
  for (let index = 0; index < source.length; index++) {
    const char = source[index];
    if (quoted) {
      if (escaped) escaped = false;
      else if (char === '\\') escaped = true;
      else if (char === '"') quoted = false;
    } else if (char === '"') quoted = true;
    else if (char === '(') depth++;
    else if (char === ')' && --depth === 0) return index;
  }
  return -1;
}
function unwrap(source) {
  return source[0] === '(' && closingParenthesis(source) === source.length - 1 ? source.slice(1, -1) : source;
}

// Recover generated rows even when a branch contains an invalid draft such as
// "1 +". The ordinary expression parser still reports its validation error.
function generatedStates(source, modes) {
  const values = Object.create(null), keys = [];
  let rest = source.trim();
  while (rest !== 'null') {
    const prefix = rest.match(/^if mode == ("(?:[^"\\]|\\.)*") \? /);
    if (!prefix) return null;
    let name;
    try { name = JSON.parse(prefix[1]); } catch { return null; }
    const mode = modes.find(mode => mode.name === name);
    if (!mode || Object.hasOwn(values, mode.key)) return null;
    rest = rest.slice(prefix[0].length);
    if (rest.startsWith('(')) {
      const end = closingParenthesis(rest);
      if (end < 0) return null;
      values[mode.key] = rest.slice(1, end);
      rest = rest.slice(end + 1);
    } else if (rest.startsWith('null')) {
      values[mode.key] = null;
      rest = rest.slice(4);
    } else return null;
    if (!rest.startsWith(' else ')) return null;
    keys.push(mode.key);
    rest = rest.slice(6);
  }
  return keys.length ? { values: Object.fromEntries(modes.map(mode => [mode.key, values[mode.key] ?? null])), lastEdited: keys[0] } : null;
}

export function parameterStates(source, modes) {
  if (!source?.trim() || !modes.length) return null;
  const generated = generatedStates(source, modes);
  if (generated) return generated;
  try {
    const ranges = new WeakMap(), ast = parseExpression(source, { ranges });
    const guard = node => {
      if (node?.kind !== 'binary' || !['==', '!='].includes(node.operator)) return null;
      const literal = node.left.kind === 'mode' ? node.right : node.right.kind === 'mode' ? node.left : null;
      const mode = literal?.kind === 'literal' && modes.find(mode => mode.name === literal.value);
      return mode ? { mode, equal: node.operator === '==' } : null;
    };
    const first = ast.kind === 'conditional' && guard(ast.condition);
    if (!first) return null;
    const branch = (node, mode) => {
      const condition = node.kind === 'conditional' && guard(node.condition);
      if (condition) return branch((condition.mode.key === mode.key) === condition.equal ? node.consequent : node.alternate, mode);
      if (node.kind === 'literal' && node.value === null) return null;
      return unwrap(source.slice(...ranges.get(node)).trim());
    };
    return { values: Object.fromEntries(modes.map(mode => [mode.key, branch(ast, mode)])), lastEdited: first.mode.key };
  } catch { return null; }
}

export function splitParameterStates(source, modes, selected) {
  if (!modes.some(mode => mode.key === selected)) throw new Error('Choose an existing spacecraft state.');
  return parameterStates(source, modes) ?? { values: Object.fromEntries(modes.map(mode => [mode.key, source])), lastEdited: selected };
}

export function stateExpression(states, modes) {
  // Put the last edited branch first. Its order preserves the merge choice
  // across saves without storing a second copy of the expressions or history.
  const ordered = [...modes].sort((a, b) => Number(b.key === states.lastEdited) - Number(a.key === states.lastEdited));
  return ordered.reduceRight((rest, mode) => {
    const source = states.values[mode.key];
    return `if mode == ${JSON.stringify(mode.name)} ? ${source?.trim() ? `(${source})` : 'null'} else ${rest}`;
  }, 'null');
}

export function mergedStateExpression(states, fallback) {
  return Object.hasOwn(states.values, states.lastEdited) ? states.values[states.lastEdited] : states.values[fallback] ?? null;
}
