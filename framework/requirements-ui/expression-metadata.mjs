// Lexical editor metadata only. Python on the server validates and evaluates
// expressions. This scanner never interprets operators or calls user code.
function tokens(source) {
  if (typeof source !== 'string' || source.length > 5000) return [];
  const result = [];
  for (let index = 0; index < source.length;) {
    const start = index, char = source[index];
    if (/\s/.test(char)) { index++; continue; }
    if (char === '#') break;
    if (char === '"' || char === "'") {
      const quote = source.startsWith(char.repeat(3), index) ? char.repeat(3) : char;
      index += quote.length;
      while (index < source.length) {
        if (source[index] === '\\') { index += 2; continue; }
        if (source.startsWith(quote, index)) { index += quote.length; break; }
        index++;
      }
      result.push({ kind: 'string', value: source.slice(start, index), start, end: index, quote });
    } else {
      const name = source.slice(index).match(/^[A-Za-z_][A-Za-z0-9_]*/)?.[0];
      const value = name ?? source.slice(index).match(/^(?:==|!=|<=|>=|\*\*)/)?.[0] ?? char;
      index += value.length;
      result.push({ kind: name ? 'name' : 'operator', value, start, end: index });
    }
  }
  return result;
}

function stringValue(token, raw = false) {
  const text = token.value.slice(token.quote.length, -token.quote.length);
  if (raw) return text;
  return text.replace(/\\(?:U[0-9a-fA-F]{8}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[0-7]{1,3}|[\s\S])/g, escape => {
    const value = escape.slice(1), special = { n: '\n', r: '\r', t: '\t', b: '\b', f: '\f', v: '\v', a: '\x07', '\\': '\\', '"': '"', "'": "'" };
    if (Object.hasOwn(special, value)) return special[value];
    if (/^[Uux]/.test(value)) { try { return String.fromCodePoint(parseInt(value.slice(1), 16)); } catch { return escape; } }
    if (/^[0-7]+$/.test(value)) return String.fromCodePoint(parseInt(value, 8));
    return escape;
  });
}

export function expressionIdentifiers(source) {
  const list = tokens(source);
  return list.filter((token, index) => token.kind === 'name' && list[index - 1]?.value !== '.' && list[index + 1]?.value !== '.' && list[index + 1]?.value !== '(')
    .map(token => token.value);
}

export function expressionReferences(source) {
  const list = tokens(source), references = [];
  for (let index = 0; index < list.length - 2; index++) {
    const [id, dot, name] = list.slice(index, index + 3);
    if (id.kind === 'name' && dot.value === '.' && name.kind === 'name' && list[index - 1]?.value !== '.') references.push({ id: id.value, name: name.value, start: id.start, end: id.end, fieldEnd: name.end });
  }
  return references;
}

export function rewriteReferences(source, renames) {
  for (const reference of expressionReferences(source).filter(reference => renames.has(reference.id)).reverse()) {
    source = source.slice(0, reference.start) + renames.get(reference.id) + source.slice(reference.end);
  }
  return source;
}

export function modeReferences(source) {
  const list = tokens(source), references = [];
  for (let index = 0; index < list.length; index++) {
    const token = list[index];
    if (token.kind !== 'string') continue;
    let start = token.start, prefix = '';
    if (/^[ru]{1,2}$/i.test(list[index - 1]?.value ?? '') && list[index - 1].end === start) { prefix = list[index - 1].value; start = list[index - 1].start; }
    const before = prefix ? index - 2 : index - 1;
    const left = ['==', '!='].includes(list[before]?.value) && list[before - 1]?.value === 'mode' && list[before - 2]?.value !== '.';
    const right = ['==', '!='].includes(list[index + 1]?.value) && list[index + 2]?.value === 'mode' && list[index + 3]?.value !== '.';
    if (left || right) references.push({ value: stringValue(token, /r/i.test(prefix)), start, end: token.end });
  }
  return references;
}

export function rewriteModeReferences(source, before, after) {
  for (const reference of modeReferences(source).filter(reference => reference.value === before).reverse()) {
    source = source.slice(0, reference.start) + JSON.stringify(after) + source.slice(reference.end);
  }
  return source;
}
