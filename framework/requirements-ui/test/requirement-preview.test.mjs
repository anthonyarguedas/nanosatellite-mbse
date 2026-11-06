import assert from 'node:assert/strict';
import { test } from 'node:test';
import { formatParameterValue } from '../model.mjs';
import { parameterValueHTML, requirementHTML } from '../public/requirement-preview.js';

test('numeric previews use four significant figures up to 999 and whole numbers above it', () => {
  for (const [value, expected] of [
    [0, '0.000'], [-0, '0.000'], [5, '5.000'], [12.3456, '12.35'],
    [0.0123456, '0.01235'], [-0.0123456, '-0.01235'], [999, '999.0'],
    [999.1, '999'], [1000, '1000'], [12345.67, '12346'], [-12345.67, '-12346'],
    [1e21, '1000000000000000000000'], [1.23456e-8, '1.235e-8'],
  ]) assert.equal(formatParameterValue(value), expected, String(value));
});

test('unset, pending and invalid values display bare variable names in monospace without units', () => {
  const variables = [{ name: 'mass', type: 'float', unit: 'kg' }];
  for (const value of [undefined, null, NaN, Infinity, -Infinity, '12']) {
    assert.equal(requirementHTML('At least $$ mass $$.', { mass: value }, variables),
      'At least <code class="parameter-name">mass</code>.');
  }
  assert.equal(requirementHTML('Literal {mass} and $$unknown$$.', {}, variables),
    'Literal {mass} and <code class="parameter-name">unknown</code>.');
});

test('numeric values and units use monospace with superscript unit powers', () => {
  assert.equal(requirementHTML('At least $$mass$$ and $$mass$$.', { mass: 12.3456 }, [{ name: 'mass', unit: 'kg' }]),
    'At least <code class="parameter-number">12.35</code> <code class="parameter-unit">kg</code> and <code class="parameter-number">12.35</code> <code class="parameter-unit">kg</code>.');
  assert.equal(parameterValueHTML(398601, 'km^3/s^2'), '<code class="parameter-number">398601</code> <code class="parameter-unit">km<sup>3</sup>/s<sup>2</sup></code>');
  assert.equal(parameterValueHTML(0.125, 'm**2 s^(-2)'), '<code class="parameter-number">0.1250</code> <code class="parameter-unit">m<sup>2</sup> s<sup>-2</sup></code>');
  assert.equal(parameterValueHTML(2, 'm^{0.5} s^(-1.5)'), '<code class="parameter-number">2.000</code> <code class="parameter-unit">m<sup>0.5</sup> s<sup>-1.5</sup></code>');
  assert.equal(parameterValueHTML(0, 'V'), '<code class="parameter-number">0.000</code> <code class="parameter-unit">V</code>');
  assert.equal(parameterValueHTML(5, '  '), '<code class="parameter-number">5.000</code>');
});

test('requirement prose and unit text remain escaped while invalid markers stay visible', () => {
  assert.equal(requirementHTML('<img src=x onerror=alert(1)> $$mass$$ $$bad-name$$', { mass: 2 }, [{ name: 'mass', unit: '<svg onload="alert(1)">m^2 & s' }]),
    '&lt;img src=x onerror=alert(1)&gt; <code class="parameter-number">2.000</code> <code class="parameter-unit">&lt;svg onload=&quot;alert(1)&quot;&gt;m<sup>2</sup> &amp; s</code> $$bad-name$$');
});
