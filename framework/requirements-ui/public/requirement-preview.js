import { formatParameterValue, interpolateRequirement } from '../model.mjs';

const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
})[char]);

export function parameterValueHTML(value, unit = '') {
  const powers = escape(unit.trim()).replace(/(?:\^|\*\*)\s*(?:\(\s*([+-]?\d+(?:\.\d+)?)\s*\)|\{\s*([+-]?\d+(?:\.\d+)?)\s*\}|([+-]?\d+(?:\.\d+)?))/g,
    (_, parenthesized, braced, exponent) => `<sup>${parenthesized ?? braced ?? exponent}</sup>`);
  return `<code class="parameter-number">${formatParameterValue(value)}</code>` + (powers ? ` <code class="parameter-unit">${powers}</code>` : '');
}

export function requirementHTML(text, values = {}, variables = []) {
  const units = new Map(variables.map(variable => [variable.name, variable.unit]));
  return interpolateRequirement(escape(text), values, (name, value) => value === null
    ? `<code class="parameter-name">${escape(name)}</code>`
    : parameterValueHTML(value, units.get(name)));
}
