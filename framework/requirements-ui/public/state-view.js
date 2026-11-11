// Read-only projection of canonical mode branches. Python creates/merges them.
function closingParenthesis(source) {
  let depth = 0, quote = '', escaped = false;
  for (let index = 0; index < source.length; index++) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === '\\') escaped = true;
      else if (source.startsWith(quote, index)) { index += quote.length - 1; quote = ''; }
    } else if (char === '"' || char === "'") { quote = source.startsWith(char.repeat(3), index) ? char.repeat(3) : char; index += quote.length - 1; }
    else if (char === '(') depth++;
    else if (char === ')' && --depth === 0) return index;
  }
  return -1;
}
export function parameterStates(source, modes) {
  if (!source?.trim() || !modes.length) return null;
  const values = Object.create(null), keys = [];
  let rest = source.trim();
  while (rest !== 'None') {
    if (!rest.startsWith('(')) return null;
    const end = closingParenthesis(rest);
    if (end < 0) return null;
    const value = rest.slice(1, end), suffix = rest.slice(end + 1);
    const match = suffix.match(/^ if mode == ("(?:[^"\\]|\\.)*") else /);
    if (!match) return null;
    let name;
    try { name = JSON.parse(match[1]); } catch { return null; }
    const mode = modes.find(mode => mode.name === name);
    if (!mode || Object.hasOwn(values, mode.key)) return null;
    values[mode.key] = value.trim() === 'None' ? null : value;
    keys.push(mode.key); rest = suffix.slice(match[0].length);
  }
  return keys.length ? { values: Object.fromEntries(modes.map(mode => [mode.key, values[mode.key] ?? null])), lastEdited: keys[0] } : null;
}
