// Read-only lexical links for editor navigation. Python owns all rewrites.
export function expressionReferences(source) {
  if (typeof source !== 'string') return [];
  const tokens = [];
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
      tokens.push({ kind: 'string' });
    } else {
      const name = source.slice(index).match(/^[A-Za-z_][A-Za-z0-9_]*/)?.[0];
      const value = name ?? char;
      index += value.length;
      tokens.push({ kind: name ? 'name' : 'operator', value, start, end: index });
    }
  }
  const result = [];
  for (let index = 0; index < tokens.length - 2; index++) {
    const [id, dot, name] = tokens.slice(index, index + 3);
    if (id.kind === 'name' && dot.value === '.' && name.kind === 'name' && tokens[index - 1]?.value !== '.') result.push({ id: id.value, name: name.value, start: id.start, end: id.end, fieldEnd: name.end });
  }
  return result;
}
