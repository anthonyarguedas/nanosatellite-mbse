import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const workbook = new URL('../public/workbook.js', import.meta.url).href;
const source = (await readFile(new URL('../public/editors/power.js', import.meta.url), 'utf8'))
  .replace("from '/workbook.js'", `from '${workbook}'`);
const { createPowerTable } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);

class Surface {
  listeners = new Map();
  innerHTML = '';
  hidden = true;
  focused = null;
  addEventListener(type, callback) { this.listeners.set(type, callback); }
  replaceChildren() { this.innerHTML = ''; }
  querySelector(selector) { return { focus: () => { this.focused = selector; } }; }
  async emit(type, target) { await this.listeners.get(type)?.({ target }); }
}

function fixture(active = 'mission') {
  const section = new Surface();
  const workspace = {
    power: {
      modes: [{ key: 'standby', name: 'Standby', sunlight: 60, eclipse: 20 }],
      loads: [{ element: 'radio', states: [{ key: 'rx', name: 'Receive', watts: .72 }], assignments: { standby: 'rx' } }],
      links: [],
    },
    _native: { metadata: { limits: { modes: 24 }, powerScopes: [{ key: 'cdh', kind: 'subsystem' }] } },
  };
  const errors = [], commands = [];
  const table = createPowerTable({
    section, getWorkspace: () => workspace, getActive: () => active,
    onCommand: async operation => {
      commands.push(operation);
      if (operation.name === 'add_mode') workspace.power.modes.push({ key: operation.key, name: operation.label, sunlight: operation.sunlight, eclipse: operation.eclipse });
      if (operation.name === 'rename_mode') workspace.power.modes.find(mode => mode.key === operation.target).name = operation.label;
      if (operation.name === 'configure_mode') Object.assign(workspace.power.modes.find(mode => mode.key === operation.target), Object.fromEntries(Object.entries(operation).filter(([key]) => ['sunlight', 'eclipse'].includes(key))));
      if (operation.name === 'remove_mode') workspace.power.modes = workspace.power.modes.filter(mode => mode.key !== operation.target);
    },
    onError: message => errors.push(message),
  });
  return { table, section, errors, commands, workspace, activate: value => { active = value; } };
}
const modeInput = (modeKey, modeField, value) => ({ dataset: { modeKey, modeField }, value });
const action = (selector, dataset = {}) => ({ closest(actual) { return actual === selector ? { dataset } : null; } });
const draftKey = f => f.section.innerHTML.match(/data-mode-key="([^"]+)" data-mode-field="name" value=""/)[1];

test('Mission retains spacecraft mode and illumination share inputs', () => {
  const f = fixture(); f.table.render();
  assert.equal(f.section.hidden, false);
  assert.match(f.section.innerHTML, /Spacecraft Modes/);
  assert.match(f.section.innerHTML, /data-mode-key="standby" data-mode-field="sunlight" value="60"/);
  assert.doesNotMatch(f.section.innerHTML, /Component State Allocation|data-power-load|data-power-watts|data-power-duty|Add loss/);
});

test('all subsystem tabs hide the allocation surface and preserve legacy data', () => {
  const f = fixture(), original = structuredClone(f.workspace.power);
  f.table.render();
  for (const active of ['cdh', 'eps', 'payload', 'external']) {
    f.activate(active); f.table.render();
    assert.equal(f.section.hidden, true);
    assert.equal(f.section.innerHTML, '');
  }
  assert.deepEqual(f.workspace.power, original);
});

test('mode names and shares are changed through Python commands', async () => {
  const f = fixture();
  await f.section.emit('change', modeInput('standby', 'name', ' Safe '));
  await f.section.emit('change', modeInput('standby', 'sunlight', '80'));
  await f.section.emit('change', modeInput('standby', 'eclipse', ''));
  assert.deepEqual(f.commands, [
    { name: 'rename_mode', target: 'standby', label: 'Safe' },
    { name: 'configure_mode', target: 'standby', sunlight: 80 },
    { name: 'configure_mode', target: 'standby', eclipse: null },
  ]);
});

test('adding and deleting modes retain the existing inline workflow', async () => {
  const f = fixture(); f.table.render();
  const key = draftKey(f);
  await f.section.emit('change', modeInput(key, 'sunlight', '40'));
  assert.equal(f.commands.length, 0);
  await f.section.emit('change', modeInput(key, 'name', 'Pass'));
  assert.deepEqual(f.commands[0], { name: 'add_mode', key, label: 'Pass', sunlight: 40, eclipse: null });
  assert.notEqual(draftKey(f), key);
  await f.section.emit('click', action('[data-power-remove-mode]', { powerRemoveMode: key }));
  assert.deepEqual(f.commands[1], { name: 'remove_mode', target: key });
  assert.equal(f.workspace.power.modes.length, 1);
});

test('mode limits, escaping and draft reset still work', () => {
  const f = fixture(); f.table.render();
  const before = draftKey(f); f.table.reset(); f.table.render();
  assert.notEqual(draftKey(f), before);
  f.workspace.power.modes[0].name = 'Safe <test>';
  f.workspace._native.metadata.limits.modes = 1;
  f.table.render();
  assert.match(f.section.innerHTML, /value="Safe &lt;test&gt;"/);
  assert.match(f.section.innerHTML, /title="Add row" disabled/);
  assert.doesNotMatch(f.section.innerHTML, /data-mode-field="name" value=""/);
});

test('removed component allocation bindings have no application or CSS leftovers', async () => {
  const html = await readFile(new URL('../public/index.html', import.meta.url), 'utf8');
  const app = await readFile(new URL('../public/app.js', import.meta.url), 'utf8');
  const css = await readFile(new URL('../public/style.css', import.meta.url), 'utf8');
  assert.doesNotMatch(html, /id="power-editor"/);
  assert.doesNotMatch(app, /powerEditor|data-open-power|dataset\.powerName|dataset\.powerWatts|dataset\.powerLoad|dataset\.powerDuty/);
  assert.doesNotMatch(css, /power-allocations|power-add-state|power-add-loss/);
});
