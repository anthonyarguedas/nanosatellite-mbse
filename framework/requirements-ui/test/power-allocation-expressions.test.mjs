import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { addElementChildren, addPowerLimits, emptyWorkspace, rewriteRowReferences, validateWorkspace } from '../model.mjs';
import { parameterStates, stateExpression } from '../parameter-states.mjs';
import { expandPowerAllocations, isPowerRequirement, powerAllocationExpression, powerFor, powerLimitFor, powerScopes, spacecraftComponents } from '../power.mjs';
import { createServer } from '../server.mjs';
import { canonicalWorkspace, createStore } from '../storage.mjs';
import { evaluateChecks } from './helpers.mjs';

const catalog = await loadCatalog();
const alias = 'PowerAllocation.allocated_power_W';
function fixture() {
  const workspace = emptyWorkspace(catalog);
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 },
    { key: 'downlink', name: 'Downlink', sunlight: 0, eclipse: 0 }];
  for (const component of spacecraftComponents(workspace)) {
    const load = structuredClone(powerFor(workspace, component));
    if (load.accounting !== 'counted') continue;
    load.states = [{ key: 'idle', name: 'Idle', watts: 0, basis: 'estimated', source: 'Test', conditions: '' }];
    load.assignments = { nominal: 'idle', downlink: 'idle' };
    workspace.power.loads.push(load);
  }
  addPowerLimits(workspace);
  for (const row of workspace.statements.filter(isPowerRequirement)) row.parameters.power_limit_W = '3 if mode == "Downlink" else 1';
  const subsystem = workspace.elements.find(element => element.definition.endsWith('::CommunicationSubsystem'));
  return { workspace, subsystem, parent: powerLimitFor(workspace, subsystem.key) };
}
function children(workspace, parent) {
  return powerScopes(workspace).filter(scope => scope.parent === parent.powerScope).sort((a, b) => a.key.localeCompare(b.key))
    .map(scope => powerLimitFor(workspace, scope.key)).filter(Boolean);
}
function addReceiver(workspace, subsystem) {
  const component = { key: 'backup-receiver', id: 'BKR', name: 'Backup receiver', owner: subsystem.key,
    definition: 'SpaceSegment::CubeSat::CommunicationSubsystem::ReceiveAntennaAndEquipment' };
  workspace.elements.push(component);
  addPowerLimits(workspace, { scopes: [component.key] });
  return powerLimitFor(workspace, component.key);
}

test('power allocation defaults are explicit Python sums of child requirement limits in each mode', () => {
  const { workspace } = fixture();
  const results = evaluateChecks(workspace);
  for (const parent of workspace.statements.filter(row => row.definition === 'PowerBudgetModel::PowerLimit')) {
    const requirements = children(workspace, parent);
    const expected = requirements.length ? `sum([${requirements.map(row => `${row.id}.power_limit_W`).join(', ')}])` : '0';
    assert.equal(parent.parameters.allocated_power_W, expected);
    assert.equal(expected.includes('PowerAllocation'), false);
    const result = results.find(row => row.key === parent.key);
    assert.deepEqual(result.modes.map(mode => mode.parameters.allocated_power_W.value), [requirements.length, requirements.length * 3]);
  }
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('new children extend untouched sums while custom and cleared expressions remain unchanged', () => {
  const { workspace, subsystem, parent } = fixture();
  const original = parent.parameters.allocated_power_W;
  const custom = structuredClone(workspace), cleared = structuredClone(workspace);
  const customParent = powerLimitFor(custom, subsystem.key), clearedParent = powerLimitFor(cleared, subsystem.key);
  customParent.parameters.allocated_power_W = `(${original}) * 1.25`;
  clearedParent.parameters.allocated_power_W = null;
  // Table sorting and ID changes preserve the identity of generated sums.
  workspace.elements.reverse(); workspace.statements.reverse();
  const child = children(workspace, parent)[0], oldId = child.id;
  child.id = 'NEW123'; rewriteRowReferences(workspace, new Map([[oldId, child.id]]));
  const added = addReceiver(workspace, subsystem);
  assert.equal(parent.parameters.allocated_power_W, powerAllocationExpression(workspace, parent));
  assert.ok(parent.parameters.allocated_power_W.includes(`${added.id}.power_limit_W`));
  assert.ok(parent.parameters.allocated_power_W.includes('NEW123.power_limit_W'));
  added.parameters.power_limit_W = '2';
  const result = evaluateChecks(workspace).find(row => row.key === parent.key);
  assert.equal(result.modes[0].parameters.allocated_power_W.value, children(workspace, parent).length + 1);
  addReceiver(custom, subsystem); addReceiver(cleared, subsystem);
  assert.equal(customParent.parameters.allocated_power_W, `(${original}) * 1.25`);
  assert.equal(clearedParent.parameters.allocated_power_W, null);
  const bus = { key: 'second-bus', id: 'BUZ', name: 'Second bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' };
  workspace.elements.push(bus); addElementChildren(workspace, bus, catalog);
  const system = powerLimitFor(workspace, 'mission');
  assert.equal(system.parameters.allocated_power_W, powerAllocationExpression(workspace, system));
  const newSubsystem = workspace.elements.find(element => element.owner === bus.key);
  assert.ok(system.parameters.allocated_power_W.includes(`${powerLimitFor(workspace, newSubsystem.key).id}.power_limit_W`));
});

test('expanding allocation aliases retains arithmetic, quoted text, mode branches and invalid drafts', () => {
  const { workspace, parent } = fixture();
  const sum = powerAllocationExpression(workspace, parent);
  parent.parameters.allocated_power_W = ` 2 * PowerAllocation . allocated_power_W + 1 `;
  parent.condition = '';
  parent.verifications = [{ key: 'allocation', condition: `${alias} >= 0 and "${alias}" == "${alias}"` }];
  const stateWorkspace = structuredClone(workspace), stateParent = powerLimitFor(stateWorkspace, parent.powerScope);
  stateParent.parameters.allocated_power_W = stateExpression({ values: { nominal: `${alias} * 1.2`, downlink: null }, lastEdited: 'downlink' }, workspace.power.modes);
  expandPowerAllocations(workspace);
  assert.equal(parent.parameters.allocated_power_W, ` 2 * (${sum}) + 1 `);
  assert.equal(parent.verifications[0].condition, `(${sum}) >= 0 and "${alias}" == "${alias}"`);
  const result = evaluateChecks(workspace).find(row => row.key === parent.key);
  assert.equal(result.modes[0].parameters.allocated_power_W.value, 2 * children(workspace, parent).length + 1);
  expandPowerAllocations(stateWorkspace);
  assert.deepEqual(parameterStates(stateParent.parameters.allocated_power_W, workspace.power.modes), {
    values: { nominal: `(${sum}) * 1.2`, downlink: null }, lastEdited: 'downlink',
  });
  const stateResults = evaluateChecks(stateWorkspace).find(row => row.key === parent.key);
  assert.equal(stateResults.modes[1].parameters.allocated_power_W.state, 'pending');
  parent.parameters.allocated_power_W = '1 +';
  expandPowerAllocations(workspace);
  assert.equal(parent.parameters.allocated_power_W, '1 +');
  parent.parameters.allocated_power_W = null;
  expandPowerAllocations(workspace);
  assert.equal(parent.parameters.allocated_power_W, null);
});

test('missing child requirements stay pending and empty scopes have an explicit zero allocation', () => {
  const { workspace, parent } = fixture();
  const child = children(workspace, parent)[0];
  workspace.statements = workspace.statements.filter(row => row.key !== child.key);
  parent.parameters.allocated_power_W = alias;
  expandPowerAllocations(workspace);
  assert.equal(parent.parameters.allocated_power_W, 'None');
  assert.equal(evaluateChecks(workspace).find(row => row.key === parent.key).parameters.allocated_power_W.state, 'pending');
  const custom = structuredClone(workspace), customParent = powerLimitFor(custom, parent.powerScope);
  customParent.parameters.allocated_power_W = `${alias} * 1.2`;
  expandPowerAllocations(custom);
  assert.equal(customParent.parameters.allocated_power_W, '(None if True else 0) * 1.2');
  assert.equal(evaluateChecks(custom).find(row => row.key === parent.key).parameters.allocated_power_W.state, 'pending');
  assert.equal(workspace.statements.some(row => row.key === child.key), false);
  const missingScope = child.powerScope;
  addPowerLimits(workspace, { scopes: [missingScope] });
  assert.equal(parent.parameters.allocated_power_W, powerAllocationExpression(workspace, parent));
  const components = new Set(workspace.elements.filter(element => element.owner === parent.powerScope).map(element => element.key));
  workspace.elements = workspace.elements.filter(element => !components.has(element.key));
  workspace.power.loads = workspace.power.loads.filter(load => !components.has(load.element));
  workspace.statements = workspace.statements.filter(row => !components.has(row.powerScope));
  parent.parameters.allocated_power_W = alias;
  expandPowerAllocations(workspace);
  assert.equal(parent.parameters.allocated_power_W, '0');
  assert.equal(evaluateChecks(workspace).find(row => row.key === parent.key).parameters.allocated_power_W.value, 0);
});

test('existing JSON sessions expose and save explicit sums without rewriting files during reads', async t => {
  const directory = await mkdtemp(join(tmpdir(), 'explicit-allocation-storage-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const { workspace, parent } = fixture(), sum = powerAllocationExpression(workspace, parent);
  parent.parameters.allocated_power_W = alias;
  const system = powerLimitFor(workspace, 'mission'), systemSum = powerAllocationExpression(workspace, system);
  system.parameters.allocated_power_W = `${alias} * 1.1`;
  const path = join(directory, 'mission.json'), source = JSON.stringify(workspace, null, 2) + '\n';
  await writeFile(path, source);
  const store = createStore(path, { catalog }), opened = await store.read();
  assert.equal(opened.workspace.statements.find(row => row.key === parent.key).parameters.allocated_power_W, sum);
  assert.equal(opened.workspace.statements.find(row => row.key === system.key).parameters.allocated_power_W, `(${systemSum}) * 1.1`);
  assert.equal(await readFile(path, 'utf8'), source);
  assert.equal((await store.read()).revision, opened.revision);
  assert.equal(parent.parameters.allocated_power_W, alias);
  const exported = await canonicalWorkspace(workspace, { catalog });
  assert.equal(exported.workspace.statements.find(row => row.key === parent.key).parameters.allocated_power_W, sum);
  const saved = await store.save(opened.workspace, opened.revision);
  assert.deepEqual(JSON.parse(await readFile(path, 'utf8')), saved.workspace);
  assert.equal(JSON.stringify(saved.workspace).includes(alias), false);
});

test('browser shows existing allocation sums as editable Python and preserves references through rename, save and reload', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await mkdtemp(join(tmpdir(), 'explicit-allocation-browser-'));
  const { workspace, parent } = fixture(), sum = powerAllocationExpression(workspace, parent);
  parent.parameters.allocated_power_W = alias;
  const path = join(directory, 'mission.json'); await writeFile(path, JSON.stringify(workspace));
  const server = createServer({ modelPath: path });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => {
    await browser.close(); await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    await rm(directory, { recursive: true, force: true });
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 } });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  const saved = () => page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const pane = page.locator('#requirement-editor'), allocation = pane.getByLabel('Expression for allocated_power_W', { exact: true });
  const open = () => page.locator(`[data-requirement-edit="${parent.key}"]`).click();
  await page.goto(`${base}/#${parent.context}`); await open();
  assert.equal(await allocation.inputValue(), sum);
  assert.equal(await allocation.isEditable(), true);
  const custom = `(${sum}) * 1.2`;
  await allocation.fill(custom);
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  const child = children(workspace, parent)[0];
  await page.locator(`tr[data-key="${child.key}"] [data-field="id"]`).fill('ALC123');
  await saved();
  await open();
  const renamed = custom.replace(`${child.id}.`, 'ALC123.');
  assert.equal(await allocation.inputValue(), renamed);
  await allocation.fill('0'); await pane.getByRole('button', { name: 'Cancel', exact: true }).click();
  await page.reload(); await open();
  assert.equal(await allocation.inputValue(), renamed);
  const stored = JSON.parse(await readFile(path, 'utf8'));
  assert.equal(stored.statements.find(row => row.key === parent.key).parameters.allocated_power_W, renamed);
  assert.deepEqual(errors, []);
});
