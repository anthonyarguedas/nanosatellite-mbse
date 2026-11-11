import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

// The editor has no browser dependencies beyond these rendering/draft seams.
// Resolve its browser-root import without adding a DOM or build dependency.
const workbook = new URL('../public/workbook.js', import.meta.url).href;
const source = (await readFile(new URL('../public/editors/power.js', import.meta.url), 'utf8'))
  .replace("from '/workbook.js'", `from '${workbook}'`);
const { createPowerEditor } = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);

class Surface {
  listeners = new Map();
  innerHTML = '';
  hidden = true;
  inert = false;
  addEventListener(type, callback) { this.listeners.set(type, callback); }
  replaceChildren() { this.innerHTML = ''; }
  querySelector() { return { focus() {}, textContent: '' }; }
  async emit(type, target) { await this.listeners.get(type)?.({ target }); }
}

function fixture() {
  const section = new Surface(), panel = new Surface();
  const element = { key: 'radio', id: 'RAD', name: 'Radio', owner: 'com', definition: 'Radio' };
  let workspace = {
    elements: [element],
    power: {
      modes: [{ key: 'standby', name: 'Standby' }, { key: 'pass', name: 'Pass' }],
      loads: [{
        element: 'radio', quantity: 1, accounting: 'counted', host: '', rationale: '',
        states: [{ key: 'on', name: 'On', watts: 0.72, basis: 'estimated', source: '', conditions: '' }],
        assignments: { standby: 'on', pass: 'on' },
      }],
      links: [],
    },
    _native: { metadata: {
      limits: { modes: 24, states: 32 },
      powerScopes: [{ key: 'com', kind: 'subsystem' }],
      powerComponents: ['radio'],
      accountingOptions: { radio: ['counted', 'excluded'] },
    } },
  };
  const errors = [];
  globalThis.document = {
    body: { classList: { add() {}, remove() {} } },
    querySelector() { return { focus() {} }; },
  };
  globalThis.window = { confirm() { return true; } };
  const editor = createPowerEditor({
    section, panel,
    getWorkspace: () => workspace,
    getActive: () => 'com',
    onChange: async candidate => { workspace = candidate; },
    onCommand: async () => {},
    onError: message => errors.push(message),
    beforeOpen: () => true,
  });
  return { editor, section, panel, errors, workspace: () => workspace };
}

function stateInput(value) {
  return {
    dataset: { stateField: 'watts' }, value,
    closest() { return { dataset: { stateKey: 'on' } }; },
  };
}

test('allocation matrix shows a separate duty control with continuous default', () => {
  const f = fixture();
  f.editor.render();
  assert.match(f.section.innerHTML, /data-power-assignment="radio"/);
  assert.match(f.section.innerHTML, /data-power-duty="radio" data-mode="standby" value="100"/);
  assert.match(f.section.innerHTML, /aria-label="RAD duty percentage in Standby"/);
});

test('editing duty preserves the selected state and other modes', async () => {
  const f = fixture();
  await f.section.emit('change', { dataset: { powerDuty: 'radio', mode: 'pass' }, value: '85' });
  const load = f.workspace().power.loads[0];
  assert.equal(load.duties.pass, 85);
  assert.equal(load.duties.standby, undefined);
  assert.equal(load.assignments.pass, 'on');
  assert.deepEqual(f.errors, []);
});

test('zero duty is retained and clearing duty restores the native default', async () => {
  const f = fixture();
  await f.section.emit('change', { dataset: { powerDuty: 'radio', mode: 'pass' }, value: '0' });
  assert.equal(f.workspace().power.loads[0].duties.pass, 0);
  await f.section.emit('change', { dataset: { powerDuty: 'radio', mode: 'pass' }, value: '' });
  assert.equal(f.workspace().power.loads[0].duties.pass, undefined);
});

test('clearing an assignment also clears its duty and disables the control', async () => {
  const f = fixture();
  await f.section.emit('change', { dataset: { powerDuty: 'radio', mode: 'pass' }, value: '85' });
  await f.section.emit('change', { dataset: { powerAssignment: 'radio', mode: 'pass' }, value: '' });
  f.editor.render();
  const load = f.workspace().power.loads[0];
  assert.equal(load.assignments.pass, undefined);
  assert.equal(load.duties.pass, undefined);
  assert.match(f.section.innerHTML, /data-power-duty="radio" data-mode="pass"[^>]*disabled/);
});

test('component power accepts expression text and preserves live matrix duty edits', async () => {
  const f = fixture();
  f.editor.open('radio');
  assert.match(f.panel.innerHTML, /type="text" data-state-field="watts"/);
  await f.panel.emit('input', stateInput('REQ001.current_A * REQ001.voltage_V'));
  assert.equal(f.editor.isDirty(), true);
  await f.section.emit('change', { dataset: { powerDuty: 'radio', mode: 'pass' }, value: '85' });
  assert.equal(await f.editor.save(), true);
  const load = f.workspace().power.loads[0];
  assert.equal(load.states[0].watts, 'REQ001.current_A * REQ001.voltage_V');
  assert.equal(load.duties.pass, 85);
  assert.equal(f.editor.isOpen(), false);
});

test('component editor escapes expression text inside the input attribute', () => {
  const f = fixture();
  f.workspace().power.loads[0].states[0].watts = '1 if mode == "Pass" else 0';
  f.editor.open('radio');
  assert.match(f.panel.innerHTML, /value="1 if mode == &quot;Pass&quot; else 0"/);
});

test('blank power is submitted as unset without parsing or calculating in JavaScript', async () => {
  const f = fixture();
  f.editor.open('radio');
  await f.panel.emit('input', stateInput('  '));
  assert.equal(await f.editor.save(), true);
  assert.equal(f.workspace().power.loads[0].states[0].watts, null);
});
