import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const workbook = new URL('../public/workbook.js', import.meta.url).href;
const referenceView = new URL('../public/reference-view.js', import.meta.url).href;
const preview = new URL('../public/requirement-preview.js', import.meta.url).href;
const moduleURL = source => `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
const native = moduleURL((await readFile(new URL('../public/native-client.js', import.meta.url), 'utf8'))
  .replace("from '/workbook.js'", `from '${workbook}'`));
const cotsView = moduleURL((await readFile(new URL('../public/cots-view.js', import.meta.url), 'utf8'))
  .replace("from '/workbook.js'", `from '${workbook}'`)
  .replace("from '/reference-view.js'", `from '${referenceView}'`));
const { mergeCotsDraft, cotsUses } = await import(cotsView);
const editorSource = (await readFile(new URL('../public/editors/cots.js', import.meta.url), 'utf8'))
  .replace("from '/cots-view.js'", `from '${cotsView}'`)
  .replace("from '/native-client.js'", `from '${native}'`)
  .replace("from '/workbook.js'", `from '${workbook}'`)
  .replace("from '/requirement-preview.js'", `from '${preview}'`);
const { createCotsEditor } = await import(moduleURL(editorSource));

const component = () => ({ key: 'battery', id: 'CMP001', product: 'test', requirements: ['requirement'], facts: [], quantity: 2 });

test('COTS property drafts merge quantity and pins without replacing newer unrelated fields', () => {
  const original = component(), edited = structuredClone(original), current = structuredClone(original);
  edited.quantity = 4;
  current.requirements = ['requirement', 'other'];
  const merged = mergeCotsDraft({ components: [current] }, original, edited).components[0];
  assert.equal(merged.quantity, 4);
  assert.deepEqual(merged.requirements, ['requirement', 'other']);
  assert.equal(current.quantity, 2);
  const newerQuantity = { ...current, quantity: 3 };
  assert.throws(() => mergeCotsDraft({ components: [newerQuantity] }, original, edited), /changed/);
  const pinEdit = structuredClone(original);
  pinEdit.facts = [{ name: 'rated_energy' }];
  const mergedPins = mergeCotsDraft({ components: [newerQuantity] }, original, pinEdit).components[0];
  assert.equal(mergedPins.quantity, 3);
  assert.deepEqual(mergedPins.facts, pinEdit.facts);
});

test('COTS navigation shows assignment uses without inventing qualified property references', () => {
  const selected = component();
  const workspace = { scripts: [], statements: [{ key: 'requirement', id: 'CNT001', parameters: {},
    condition: 'count_assigned("Battery", cots_only=True) <= max_batteries' }] };
  assert.deepEqual(cotsUses(workspace, selected), [{ key: 'requirement', id: 'CNT001', kind: 'requirement', fields: ['assignment'] }]);
  assert.deepEqual(cotsUses(workspace, selected, 'rated_energy'), []);
});

class Surface {
  listeners = new Map();
  elements = new Map();
  innerHTML = '';
  hidden = true;
  addEventListener(type, callback) { this.listeners.set(type, callback); }
  querySelector(selector) {
    if (!this.elements.has(selector)) this.elements.set(selector, { innerHTML: '', textContent: '', value: '', hidden: false });
    return this.elements.get(selector);
  }
  emit(type, target) { this.listeners.get(type)?.({ target }); }
}

test('COTS pane renders typed sources and edits the quantity used by assignment sums', async t => {
  const previousDocument = globalThis.document;
  globalThis.document = { body: { classList: { add() {}, remove() {} } } };
  t.after(() => { globalThis.document = previousDocument; });
  const selected = component();
  const fact = { id: 'fact', revision: 'revision', element: 'battery', name: 'battery_energy', type: 'float', unit: 'Wh', value: 45,
    valueKind: 'nominal', condition: { id: '', values: {}, parameters: [] }, source: { id: 'source', locator: 'page=1', revision: 'A', url: '' } };
  selected.facts = [{ key: 'pin', name: 'rated_energy', fact: fact.id, revision: fact.revision, type: fact.type, unit: fact.unit }];
  t.mock.method(globalThis, 'fetch', async () => ({ ok: true, json: async () => ({ facts: [fact] }) }));
  const workspace = { components: [selected], statements: [], scripts: [], _native: { metadata: {
    limits: { facts: 64 }, objects: { battery: { componentProperties: [
      { name: 'rated_energy', factName: 'battery_energy', element: 'battery', type: 'float', unit: 'Wh' },
      { name: 'chemistry', factName: '<script>', element: 'battery', type: 'string', unit: '' },
    ] } },
  } } };
  const panel = new Surface();
  const editor = createCotsEditor({
    panel, getWorkspace: () => workspace, getReferenceWorkspace: () => workspace,
    getProducts: () => [], validate: value => value, onCommit: async () => {},
    beforeOpen: () => true, onReturn() {}, onOpenRequirement() {}, onInsert() {},
    canInsert: () => false, returnLabel: () => '',
  });
  assert.equal(editor.open('battery'), true);
  await new Promise(resolve => setImmediate(resolve));
  assert.match(panel.innerHTML, /Quantity for assignment sums/);
  assert.match(panel.querySelector('[data-cots-typed-properties]').innerHTML, /battery\.battery_energy/);
  assert.match(panel.querySelector('[data-cots-typed-properties]').innerHTML, /45\.00/);
  assert.match(panel.querySelector('[data-cots-typed-properties]').innerHTML, /&lt;script&gt;/);
  assert.doesNotMatch(panel.querySelector('[data-cots-typed-properties]').innerHTML, /<script>/);
  assert.equal(editor.isDirty(), false);
  panel.emit('input', { value: '4', matches: selector => selector === '[data-cots-quantity]' });
  assert.equal(editor.isDirty(), true);
  assert.equal(editor.snapshot().components[0].quantity, 4);
  assert.equal(selected.quantity, 2);
});

test('verification editor documents count, universal and quantity weighted assignment checks', async () => {
  const html = await readFile(new URL('../public/index.html', import.meta.url), 'utf8');
  assert.match(html, /all_assigned\("Battery"/);
  assert.match(html, /sum_assigned\("SolarArray"/);
  assert.match(html, /count_assigned\("Battery", cots_only=True\) &lt;= max_batteries/);
  assert.match(html, /by_quantity=True/);
});
