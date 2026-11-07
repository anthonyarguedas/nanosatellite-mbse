import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { addPowerLimits, emptyWorkspace, removePowerMode, renamePowerMode, requirementParameterNames, validateWorkspace } from '../model.mjs';
import { isPowerRequirement, powerFor, spacecraftComponents } from '../power.mjs';
import { parameterStates } from '../parameter-states.mjs';
import { createServer } from '../server.mjs';
import { createEvaluator, evaluateChecks, serializeWorkspace, roundTrip, validateCalculations } from './helpers.mjs';

function fixture() {
  return { ...emptyWorkspace(), variables: [{ name: 'x', type: 'float' }, { name: 'y', type: 'float' }, { name: 'count', type: 'integer' }],
    power: { modes: [{ key: 'nominal', name: 'Nominal', sunlight: 75, eclipse: 100 }, { key: 'downlink', name: 'Downlink', sunlight: 25, eclipse: 0 }], loads: [], links: [] },
    statements: [
      { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'The draw shall not exceed $$x$$.', condition: 'y <= x', sources: [], affected: [], parameters: { x: '18 if mode == "Downlink" else 3', y: '2', count: '4' } },
      { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: '', condition: 'x > 0', sources: ['r1'], affected: [], parameters: { x: 'REQ001.x * 2', y: null, count: null } },
    ] };
}
const check = (workspace, mode) => evaluateChecks(workspace, mode === undefined ? {} : { mode })[0];

test('Python conditionals support nested branches, functions and arithmetic', () => {
  const workspace = fixture(), row = workspace.statements[0];
  for (const [source, value] of [['3 if y > 1 else 4', 3], ['(3 if y < 1 else 4) * 2', 8], ['max(1, 3 if y == 2 else 4)', 3], ['3 if y < 1 else 4 if y > 1 else 5', 4], ['2 + 3 * 4 if True else 5', 14]]) {
    row.parameters.x = source; assert.equal(check(workspace, 'nominal').values.x, value, source);
  }
  for (const source of ['if true ? 1 else 2', '1 if True', '2 if 1 else 3', '1 if True else False']) {
    row.parameters.x = source; assert.equal(check(workspace, 'nominal').parameters.x.state, 'error', source);
  }
});

test('one requirement evaluates across modes with isolated caches and a shared expression option', () => {
  const workspace = validateWorkspace(fixture());
  assert.equal(createEvaluator(workspace, { mode: 'nominal' }).parameter(workspace.statements[1], 'x'), 6);
  assert.equal(createEvaluator(workspace, { mode: 'downlink' }).parameter(workspace.statements[1], 'x'), 36);
  const result = check(workspace); assert.equal(result.state, 'pass'); assert.equal(result.parameters.x.state, 'varying');
  assert.deepEqual(result.modes.map(mode => mode.values.x), [3, 18]);
  workspace.statements[0].parameters.x = '5'; assert.equal(check(workspace).values.x, 5); assert.equal(workspace.statements.length, 2);
});

test('verification retains failures, pending branches and errors in every configured mode', () => {
  const workspace = fixture(), row = workspace.statements[0]; row.parameters.y = '4';
  assert.equal(check(workspace).state, 'fail'); assert.equal(check(workspace, 'downlink').state, 'pass');
  row.parameters.x = 'None if mode == "Downlink" else 5'; assert.equal(check(workspace).state, 'pending');
  assert.equal(check(workspace, 'nominal').values.x, 5);
  row.parameters.x = 'math.sqrt(-1) if mode == "Downlink" else 5'; assert.equal(check(workspace).state, 'error');
  assert.equal(check(workspace, 'nominal').state, 'pass'); assert.throws(() => validateCalculations(workspace), /REQ001.x/);
  row.parameters.x = 'unknown if mode == "Downlink" else 5'; assert.equal(check(workspace, 'nominal').parameters.x.state, 'error');
  row.parameters.x = '1 if mode == "Missing" else 5'; assert.match(check(workspace).parameters.x.message, /Unknown spacecraft mode/);
  row.parameters.x = '1 if mode == "Nominal" else 5'; assert.equal(check(workspace, null).parameters.x.state, 'pending');
  row.parameters.count = '1.5 if mode == "Downlink" else 2'; assert.equal(check(workspace).parameters.count.state, 'error');
  assert.equal(check(workspace, 'nominal').values.count, 2);
});

test('conditional inputs remain accessible and JSON retains their expression text', () => {
  const workspace = fixture(), row = workspace.statements[0]; row.parameters.x = '(count + y) if mode == "Downlink" else 3';
  assert.deepEqual(requirementParameterNames(workspace, row), ['x', 'y', 'count']);
  assert.deepEqual(roundTrip(workspace), workspace); assert.equal(JSON.parse(validateCalculations(workspace)).statements[0].parameters.x, row.parameters.x);
});

test('renaming modes updates references and referenced modes remain protected from deletion', () => {
  const workspace = fixture(), before = workspace.statements.length; renamePowerMode(workspace, 'downlink', 'Science "A"');
  assert.equal(check(workspace, 'downlink').values.x, 18); assert.throws(() => removePowerMode(workspace, 'downlink'), /expression references/);
  workspace.statements[0].parameters.x = '3';
  workspace.statements[0].condition = 'mode != ' + JSON.stringify('Science "A"');
  assert.throws(() => removePowerMode(workspace, 'downlink'), /expression references/);
  workspace.statements[0].condition = 'True'; removePowerMode(workspace, 'downlink');
  assert.equal(workspace.statements.length, before); assert.equal(workspace.power.modes.length, 1); validateWorkspace(workspace);
});

test('adding a mode preserves existing power requirement identities and independent assigned limits', async () => {
  const catalog = await loadCatalog(), workspace = emptyWorkspace(catalog); workspace.power = fixture().power; addPowerLimits(workspace);
  const before = workspace.statements.filter(isPowerRequirement).map(row => ({ key: row.key, id: row.id }));
  for (const row of workspace.statements.filter(isPowerRequirement)) row.parameters.power_limit_W = '18 if mode == "Downlink" else 3';
  workspace.power.modes.push({ key: 'science', name: 'Science', sunlight: 0, eclipse: 0 }); addPowerLimits(workspace);
  assert.deepEqual(workspace.statements.filter(isPowerRequirement).map(row => ({ key: row.key, id: row.id })), before);
});

test('Python evaluates conditional child allocations, installed quantities and component draws', async () => {
  const catalog = await loadCatalog(), workspace = emptyWorkspace(catalog); workspace.power = fixture().power;
  for (const element of spacecraftComponents(workspace)) {
    const load = structuredClone(powerFor(workspace, element)); if (load.accounting !== 'counted') continue;
    load.states = [{ key: 'active', name: 'Active', watts: 2, basis: 'estimated', source: 'Test', conditions: '' }]; load.assignments = { nominal: 'active', downlink: 'active' }; workspace.power.loads.push(load);
  }
  addPowerLimits(workspace);
  for (const row of workspace.statements.filter(isPowerRequirement)) row.parameters.power_limit_W = '18 if mode == "Downlink" else 3';
  const subsystem = workspace.statements.find(row => row.id === 'PWS001');
  subsystem.parameters.allocated_power_W = 'PowerAllocation.allocated_power_W * 1.25'; subsystem.parameters.draw_power_W = 'PowerAllocation.draw_power_W + 1';
  const snapshot = JSON.parse(validateCalculations(workspace, { catalog })), result = evaluateChecks(snapshot, { mode: 'nominal' }).find(row => row.key === subsystem.key);
  const children = workspace.statements.filter(row => row.definition === 'PowerBudgetModel::ComponentPowerLimit' && row.context === subsystem.context);
  assert.equal(result.values.allocated_power_W, children.length * 3 * 1.25); assert.equal(result.values.draw_power_W, children.length * 2 + 1);
});

test('browser edits one conditional requirement, shows all mode results, and retains expressions after save and reload', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await mkdtemp(join(tmpdir(), 'conditional-requirement-browser-')), modelPath = join(directory, 'mission.json');
  await writeFile(modelPath, serializeWorkspace(fixture()));
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => { await browser.close(); await new Promise(resolve => server.close(resolve)); await rm(directory, { recursive: true, force: true }); });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  await page.goto(base); await page.locator('[data-requirement-edit="r1"]').click();
  const editor = page.locator('#requirement-editor');
  assert.equal(await editor.getByLabel('Preview mode', { exact: true }).count(), 0);
  const output = editor.locator('[data-parameter-row="x"][data-mode="downlink"] .parameter-result');
  await page.waitForFunction(() => document.querySelector('[data-parameter-row="x"][data-mode="downlink"] .parameter-result')?.textContent === '18.00');
  assert.match(await editor.locator('#requirement-mode-results').textContent(), /Nominal: TRUE.*Downlink: TRUE/);
  assert.equal(await output.textContent(), '18.00');
  await editor.getByLabel('Expression for x in Nominal', { exact: true }).fill('1');
  await page.waitForFunction(() => document.querySelector('#requirement-check').textContent === 'FALSE');
  assert.match(await editor.locator('#requirement-mode-results').textContent(), /Nominal: FALSE.*Downlink: TRUE/);
  assert.equal(await output.textContent(), '18.00');
  await editor.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  await page.reload(); await page.locator('[data-requirement-edit="r1"]').click();
  assert.equal(await editor.getByLabel('Expression for x in Nominal', { exact: true }).inputValue(), '1');
  await editor.getByLabel('Expression for x in Downlink', { exact: true }).fill('99'); await editor.getByRole('button', { name: 'Cancel', exact: true }).click();
  const saved = (await (await page.request.get(base + '/api/workspace')).json()).workspace;
  assert.equal(saved.statements.filter(row => row.context === 'external').length, 2);
  assert.deepEqual(parameterStates(saved.statements[0].parameters.x, saved.power.modes).values, { nominal: '1', downlink: '18' });
  assert.deepEqual(errors, []);
});
