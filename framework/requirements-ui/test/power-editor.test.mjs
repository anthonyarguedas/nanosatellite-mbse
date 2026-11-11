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
  addEventListener(type, callback) { this.listeners.set(type, callback); }
  replaceChildren() { this.innerHTML = ''; }
  querySelector() { return { focus() {} }; }
  async emit(type, target) { await this.listeners.get(type)?.({ target }); }
}

function fixture() {
  const section = new Surface();
  const element = { key: 'radio', id: 'RAD', name: 'Radio', owner: 'com', definition: 'Radio' };
  let workspace = {
    elements: [element],
    power: {
      modes: [{ key: 'standby', name: 'Standby' }, { key: 'pass', name: 'Pass' }],
      loads: [{
        element: 'radio', quantity: 1, accounting: 'counted', host: '', rationale: '',
        states: [{ key: 'rx', name: 'Receive', watts: .72 }, { key: 'tx', name: 'Transmit', watts: 7.2 }, { key: 'off', name: 'Off', watts: 0 }],
        assignments: { standby: 'rx', pass: 'tx' },
      }],
      links: [],
    },
    _native: { metadata: {
      limits: { modes: 24, states: 32 },
      powerScopes: [{ key: 'com', kind: 'subsystem' }],
      powerComponents: ['radio'],
      powerLossDefinitions: { com: 'Communication::PowerLoss' },
      accountingOptions: { radio: ['counted', 'excluded'] },
      objects: { radio: { className: 'ReceiveAntennaAndEquipment' } },
    } },
  };
  const errors = [], commands = [];
  const table = createPowerTable({
    section,
    getWorkspace: () => workspace,
    getActive: () => 'com',
    onChange: async candidate => { workspace = candidate; },
    onCommand: async operation => {
      commands.push(operation);
      if (operation.name === 'add_element') {
        workspace.elements.push({ key: operation.key, id: 'LOS', name: 'Power Loss', owner: operation.owner, definition: operation.definition });
        workspace.power.loads.push({ element: operation.key, quantity: 1, accounting: 'counted', host: '', rationale: '', states: [], assignments: {}, allocations: {} });
        workspace._native.metadata.powerComponents.push(operation.key);
        workspace._native.metadata.objects[operation.key] = { className: 'PowerLoss' };
        workspace._native.metadata.accountingOptions[operation.key] = ['counted', 'excluded'];
      }
    },
    onError: message => errors.push(message),
  });
  return { table, section, errors, commands, workspace: () => workspace };
}

const dutyInput = (state, mode, value) => ({ dataset: { powerDuty: 'radio', state, mode }, value });
const action = (selector, dataset = {}) => ({ closest(actual) { return actual === selector ? { dataset } : null; } });
const draftKey = (f, component = 'radio') => f.section.innerHTML.match(new RegExp(`data-power-name="${component}" data-state="([^"]+)" value=""`))[1];

test('all state fields are inline and component names have no drawer action', () => {
  const f = fixture();
  f.table.render();
  assert.match(f.section.innerHTML, /Component State Allocation/);
  assert.match(f.section.innerHTML, /rowspan="3"/);
  assert.match(f.section.innerHTML, /data-power-name="radio" data-state="rx"/);
  assert.match(f.section.innerHTML, /data-power-watts="radio" data-state="rx"/);
  assert.match(f.section.innerHTML, /data-power-duty="radio" data-mode="standby" data-state="rx" value="100"/);
  assert.match(f.section.innerHTML, /data-power-load="radio" data-load-field="quantity"/);
  assert.match(f.section.innerHTML, /Add state/);
  assert.doesNotMatch(f.section.innerHTML, /data-open-power|Meaning|Conditions|Source/);
  assert.equal(f.table.open, undefined);
  assert.equal(f.table.snapshot, undefined);
});

test('editing duties converts one legacy mode to multiple state entries', async () => {
  const f = fixture();
  await f.section.emit('change', dutyInput('rx', 'standby', '99'));
  await f.section.emit('change', dutyInput('tx', 'standby', '1'));
  const load = f.workspace().power.loads[0];
  assert.deepEqual(load.allocations.standby, [{ state: 'rx', duty: 99 }, { state: 'tx', duty: 1 }]);
  assert.equal(load.assignments.standby, undefined);
  assert.equal(load.assignments.pass, 'tx');
  assert.deepEqual(f.errors, []);
});

test('zero duty is retained and clearing removes only that state contribution', async () => {
  const f = fixture();
  await f.section.emit('change', dutyInput('tx', 'pass', '0'));
  assert.deepEqual(f.workspace().power.loads[0].allocations.pass, [{ state: 'tx', duty: 0 }]);
  await f.section.emit('change', dutyInput('tx', 'pass', ''));
  assert.deepEqual(f.workspace().power.loads[0].allocations.pass, []);
});

test('inline power preserves expression text without JavaScript evaluation', async () => {
  const f = fixture();
  await f.section.emit('change', { dataset: { powerWatts: 'radio', state: 'rx' }, value: 'REQ001.current_A * REQ001.voltage_V' });
  assert.equal(f.workspace().power.loads[0].states[0].watts, 'REQ001.current_A * REQ001.voltage_V');
  assert.equal(f.workspace().power.loads[0].assignments.pass, 'tx');
});

test('state names and quantities are edited in the same table', async () => {
  const f = fixture();
  await f.section.emit('change', { dataset: { powerName: 'radio', state: 'rx' }, value: ' Receiving ' });
  await f.section.emit('change', { dataset: { powerLoad: 'radio', loadField: 'quantity' }, value: '2' });
  assert.equal(f.workspace().power.loads[0].states[0].name, 'Receiving');
  assert.equal(f.workspace().power.loads[0].quantity, 2);
  assert.equal(f.workspace().power.loads[0].assignments.standby, 'rx');
});

test('adding a state uses an inline draft and submits only name, power and key', async () => {
  const f = fixture();
  await f.section.emit('click', action('[data-power-add-state]', { powerAddState: 'radio' }));
  const state = draftKey(f);
  await f.section.emit('change', { dataset: { powerWatts: 'radio', state }, value: 'REQ001.idle_W' });
  assert.equal(f.workspace().power.loads[0].states.length, 3);
  await f.section.emit('change', { dataset: { powerName: 'radio', state }, value: 'Idle' });
  assert.deepEqual(f.workspace().power.loads[0].states[3], { key: state, name: 'Idle', watts: 'REQ001.idle_W' });
  assert.deepEqual(f.errors, []);
});

test('rapid name and power edits create one state with both values', async () => {
  const f = fixture();
  await f.section.emit('click', action('[data-power-add-state]', { powerAddState: 'radio' }));
  const state = draftKey(f);
  await Promise.all([
    f.section.emit('change', { dataset: { powerName: 'radio', state }, value: 'Idle' }),
    f.section.emit('change', { dataset: { powerWatts: 'radio', state }, value: '0.05' }),
  ]);
  assert.equal(f.workspace().power.loads[0].states.length, 4);
  assert.deepEqual(f.workspace().power.loads[0].states[3], { key: state, name: 'Idle', watts: '0.05' });
});

test('deleting a state submits its removal without changing other allocations', async () => {
  const f = fixture();
  await f.section.emit('click', action('[data-power-remove-state]', { powerRemoveState: 'radio', state: 'off' }));
  assert.deepEqual(f.workspace().power.loads[0].states.map(state => state.key), ['rx', 'tx']);
  assert.equal(f.workspace().power.loads[0].assignments.standby, 'rx');
});

test('an unnamed draft can be discarded without creating model state', async () => {
  const f = fixture();
  await f.section.emit('click', action('[data-power-add-state]', { powerAddState: 'radio' }));
  const state = draftKey(f);
  await f.section.emit('click', action('[data-power-remove-state]', { powerRemoveState: 'radio', state }));
  assert.equal(f.workspace().power.loads[0].states.length, 3);
  assert.doesNotMatch(f.section.innerHTML, new RegExp(state));
});

test('excluding a component keeps its inline accounting control available', async () => {
  const f = fixture();
  await f.section.emit('change', { dataset: { powerLoad: 'radio', loadField: 'accounting' }, value: 'excluded' });
  f.table.render();
  assert.equal(f.workspace().power.loads[0].accounting, 'excluded');
  assert.match(f.section.innerHTML, /data-power-show-others checked/);
  assert.match(f.section.innerHTML, /data-load-field="accounting" aria-label="RAD accounting"/);
  await f.section.emit('change', { dataset: { powerLoad: 'radio', loadField: 'accounting' }, value: 'counted' });
  assert.equal(f.workspace().power.loads[0].accounting, 'counted');
});

test('software execution host is available inline when other components are shown', async () => {
  const f = fixture(), w = f.workspace();
  w.elements.push({ key: 'software', id: 'SFW', name: 'Software', owner: 'com' });
  w.power.loads.push({ element: 'software', quantity: 1, accounting: 'host', host: 'radio', states: [], assignments: {} });
  w._native.metadata.powerComponents.push('software');
  w._native.metadata.accountingOptions.software = ['host', 'excluded'];
  w._native.metadata.executionHosts = ['radio'];
  await f.section.emit('change', { dataset: {}, checked: true, matches: () => true });
  assert.match(f.section.innerHTML, /data-power-load="software" data-load-field="host"/);
  assert.match(f.section.innerHTML, /option value="radio" selected/);
});

test('power expressions and editable state names are HTML escaped', () => {
  const f = fixture();
  f.workspace().power.loads[0].states[0].watts = '1 if mode == "Pass" else 0';
  f.workspace().power.loads[0].states[0].name = 'Receive <test>';
  f.table.render();
  assert.match(f.section.innerHTML, /value="1 if mode == &quot;Pass&quot; else 0"/);
  assert.match(f.section.innerHTML, /value="Receive &lt;test&gt;"/);
});

test('Add loss creates a native catalog instance and starts an inline state row', async () => {
  const f = fixture();
  await f.section.emit('click', action('[data-power-add-loss]'));
  assert.equal(f.commands[0].name, 'add_element');
  assert.equal(f.commands[0].definition, 'Communication::PowerLoss');
  assert.equal(f.commands[0].owner, 'com');
  const element = f.workspace().elements[1];
  const state = draftKey(f, element.key);
  await f.section.emit('change', { dataset: { powerName: element.key, state }, value: 'Dissipation' });
  await f.section.emit('change', { dataset: { powerWatts: element.key, state }, value: '0.08' });
  const load = f.workspace().power.loads[1];
  assert.deepEqual(load.states, [{ key: state, name: 'Dissipation', watts: '0.08' }]);
  assert.doesNotMatch(f.section.innerHTML, /data-open-power/);
});

test('panel markup and lifecycle bindings are removed from the application', async () => {
  const html = await readFile(new URL('../public/index.html', import.meta.url), 'utf8');
  const app = await readFile(new URL('../public/app.js', import.meta.url), 'utf8');
  assert.doesNotMatch(html, /id="power-editor"/);
  assert.doesNotMatch(app, /powerEditor|data-open-power|#power-editor/);
});
