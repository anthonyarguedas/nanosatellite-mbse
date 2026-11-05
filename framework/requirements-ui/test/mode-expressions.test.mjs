import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import {
  addPowerLimits, emptyWorkspace, migrateWorkspace, removePowerMode, renamePowerMode,
  requirementParameterNames, validateWorkspace, WORKSPACE_VERSION,
} from '../model.mjs';
import { isPowerRequirement, powerFor, powerLimitFor, spacecraftComponents } from '../power.mjs';
import { createEvaluator, evaluateChecks, parseExpression, printExpression } from '../verification.mjs';
import { readWorkspace, renderExport, renderManaged } from '../sysml.mjs';
import { createServer } from '../server.mjs';
import { parameterStates } from '../parameter-states.mjs';

function fixture() {
  return {
    ...emptyWorkspace(),
    variables: [{ name: 'x', type: 'float' }, { name: 'y', type: 'float' }, { name: 'count', type: 'integer' }],
    power: { modes: [{ key: 'nominal', name: 'Nominal', sunlight: 75, eclipse: 100 },
      { key: 'downlink', name: 'Downlink', sunlight: 25, eclipse: 0 }], loads: [], links: [] },
    statements: [
      { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'The draw shall not exceed $$x$$.',
        condition: 'y <= x', sources: [], affected: [], parameters: { x: 'if mode == "Downlink" ? 18 else 3', y: '2', count: '4' } },
      { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: '', condition: 'x > 0', sources: ['r1'], affected: [],
        parameters: { x: 'REQ001.x * 2', y: null, count: null } },
    ],
  };
}
const check = (workspace, mode) => evaluateChecks(workspace, mode === undefined ? {} : { mode })[0];

test('conditional expressions support ordinary conditions, nested branches, functions and arithmetic', () => {
  const workspace = fixture(), row = workspace.statements[0];
  const examples = [
    ['if y > 1 ? 3 else 4', 3],
    ['(if y < 1 ? 3 else 4) * 2', 8],
    ['max(1, if y == 2 ? 3 else 4)', 3],
    ['if y < 1 ? 3 else if y > 1 ? 4 else 5', 4],
    ['if true ? 2 + 3 * 4 else 5', 14],
  ];
  for (const [source, value] of examples) {
    row.parameters.x = source;
    assert.equal(check(workspace, 'nominal').values.x, value, source);
  }
  for (const source of ['if true then 1 else 2', 'if true ? 1', 'if ? 1 else 2', 'if true ? 1 else', 'if 1 ? 2 else 3', 'if true ? 1 else false']) {
    row.parameters.x = source;
    assert.equal(check(workspace, 'nominal').parameters.x.state, 'error', source);
  }
  assert.throws(() => parseExpression('if true ? '.repeat(80) + '1' + ' else 0'.repeat(80)), /nested|5,000/);
});

test('one requirement evaluates across all modes with isolated cross-row caches and a shared expression option', () => {
  const workspace = validateWorkspace(fixture());
  const evaluator = mode => createEvaluator(workspace, { mode });
  assert.equal(evaluator('nominal').parameter(workspace.statements[1], 'x'), 6);
  assert.equal(evaluator('downlink').parameter(workspace.statements[1], 'x'), 36);
  const result = check(workspace);
  assert.equal(result.state, 'pass');
  assert.equal(result.parameters.x.state, 'varying');
  assert.equal(result.values.x, null);
  assert.equal(result.values.y, 2);
  assert.deepEqual(result.modes.map(mode => mode.values.x), [3, 18]);
  workspace.statements[0].parameters.x = '5';
  assert.equal(check(workspace).values.x, 5);
  assert.equal(workspace.statements.length, 2);
});

test('all-mode verification retains failures, pending branches and errors in any configured mode', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.parameters.y = '4';
  assert.equal(check(workspace).state, 'fail');
  assert.equal(check(workspace, 'downlink').state, 'pass');
  row.parameters.x = 'if mode == "Downlink" ? null else 5';
  assert.equal(check(workspace).state, 'pending');
  assert.equal(check(workspace, 'nominal').values.x, 5);
  row.parameters.x = 'if mode == "Downlink" ? sqrt(-1) else 5';
  assert.equal(check(workspace).state, 'error');
  assert.equal(check(workspace, 'nominal').state, 'pass');
  assert.throws(() => renderExport(workspace), /REQ001.x/);
  row.parameters.x = 'if mode == "Downlink" ? unknown else 5';
  assert.equal(check(workspace, 'nominal').parameters.x.state, 'error');
  row.parameters.x = 'if mode == "Missing" ? 1 else 5';
  assert.match(check(workspace).parameters.x.message, /Unknown spacecraft mode/);
  row.parameters.x = 'if mode == "Nominal" ? 1 else 5';
  assert.equal(check(workspace, null).parameters.x.state, 'pending');
  row.parameters.count = 'if mode == "Downlink" ? 1.5 else 2';
  assert.equal(check(workspace).parameters.count.state, 'error');
  assert.equal(check(workspace, 'nominal').values.count, 2);
});

test('conditional inputs stay visible and expressions round trip without replacing their text with results', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.parameters.x = ' if mode == "Downlink" ? (count + y) else 3 ';
  assert.deepEqual(requirementParameterNames(workspace, row), ['x', 'y', 'count']);
  assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
  const source = renderExport(workspace);
  assert.match(source, /attribute spacecraft_mode : PowerBudgetModel::SpacecraftMode\[0\.\.1\]/);
  assert.match(source, /if \(MissionRequirements::spacecraft_mode\.display_name == "Downlink"\) \?/);
  assert.equal((source.match(/requirement statement_r1/g) ?? []).length, 1);
  assert.equal(printExpression(parseExpression('if true ? 1 else null')), '(if true ? 1 else null)');
});

test('mode renames update expression references and deletion preserves requirements and protects referenced modes', () => {
  const workspace = fixture(), before = workspace.statements.length;
  renamePowerMode(workspace, 'downlink', 'Science "A"');
  assert.match(workspace.statements[0].parameters.x, /Science \\"A\\"/);
  assert.equal(check(workspace, 'downlink').values.x, 18);
  assert.throws(() => removePowerMode(workspace, 'downlink'), /expression references/);
  workspace.statements[0].parameters.x = '3';
  workspace.statements[0].condition = 'mode != "Science \\"A\\""';
  assert.throws(() => removePowerMode(workspace, 'downlink'), /expression references/);
  workspace.statements[0].condition = 'true';
  removePowerMode(workspace, 'downlink');
  assert.equal(workspace.statements.length, before);
  assert.equal(workspace.power.modes.length, 1);
  assert.doesNotThrow(() => validateWorkspace(workspace));
});

test('version 10 merges mode copies, their inputs, source links, component links and ID references once', async () => {
  const catalog = await loadCatalog(), workspace = emptyWorkspace(catalog);
  workspace.power = fixture().power;
  addPowerLimits(workspace);
  const limits = workspace.statements.filter(isPowerRequirement), originals = limits.length;
  const copies = new Map();
  for (const row of limits) for (const [index, mode] of workspace.power.modes.entries()) {
    const copy = { ...structuredClone(row), key: `${row.key}-${mode.key}`, id: `${index ? 'CPY' : 'OLD'}${String(limits.indexOf(row) + 1).padStart(3, '0')}`, powerMode: mode.key };
    copy.parameters.power_limit_W = index ? '18' : '3';
    copies.set(`${row.key}:${mode.key}`, copy);
  }
  for (const row of limits) for (const mode of workspace.power.modes) {
    copies.get(`${row.key}:${mode.key}`).sources = row.sources.map(key => copies.get(`${key}:${mode.key}`)?.key ?? key);
  }
  const partial = copies.get(`${limits.at(-1).key}:downlink`);
  workspace.statements = [...workspace.statements.filter(row => !isPowerRequirement(row)), ...[...copies.values()].filter(row => row !== partial)];
  const first = copies.get(`${limits[0].key}:nominal`), second = copies.get(`${limits[0].key}:downlink`);
  second.rationale = 'A separate downlink assumption.';
  workspace.statements[0].sources.push(second.key);
  workspace.statements[0].parameters.orbit_period_s = `${second.id}.power_limit_W`;
  workspace.components.push({ key: 'cots', id: 'CMP001', owner: workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem')).key,
    product: 'test_product', requirements: [...copies.values()].filter(row => row.context === workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem')).key).map(row => row.key) });
  workspace.version = 10;
  const original = structuredClone(workspace), upgraded = migrateWorkspace(workspace, catalog);
  assert.deepEqual(workspace, original);
  assert.equal(upgraded.version, WORKSPACE_VERSION);
  assert.equal(upgraded.statements.filter(isPowerRequirement).length, originals);
  const merged = upgraded.statements.find(row => row.key === first.key);
  assert.equal(merged.id, first.id);
  assert.match(merged.rationale, /separate downlink assumption/);
  assert.equal(check({ ...upgraded, statements: [merged] }, 'nominal').values.power_limit_W, 3);
  assert.equal(check({ ...upgraded, statements: [merged] }, 'downlink').values.power_limit_W, 18);
  assert.ok(upgraded.statements[0].sources.includes(first.key));
  assert.equal(upgraded.statements[0].parameters.orbit_period_s, `${first.id}.power_limit_W`);
  assert.equal(upgraded.components[0].requirements.length, workspace.components[0].requirements.length / 2);
  assert.doesNotThrow(() => validateWorkspace(upgraded, catalog));
  const partialLimit = powerLimitFor(upgraded, partial.powerScope);
  assert.equal(partialLimit.parameters.draw_power_W, 'PowerAllocation.draw_power_W');
  assert.equal(createEvaluator(upgraded, { mode: 'downlink' }).checkParameter(partialLimit, 'power_limit_W').state, 'pending');
  assert.deepEqual(readWorkspace(renderManaged(upgraded, { catalog }), catalog), upgraded);
  assert.equal(migrateWorkspace(upgraded, catalog), upgraded);
  upgraded.power.modes.push({ key: 'science', name: 'Science', sunlight: 0, eclipse: 0 });
  addPowerLimits(upgraded);
  assert.equal(upgraded.statements.filter(isPowerRequirement).length, originals);
  assert.equal(createEvaluator(upgraded, { mode: 'science' }).checkParameter(merged, 'power_limit_W').state, 'pending');
});

test('native SysML accepts conditional limits, child allocations and mode-dependent component draws', async t => {
  if (spawnSync('syside', ['--version']).error) return t.skip('syside is not installed');
  const catalog = await loadCatalog(), workspace = emptyWorkspace(catalog);
  workspace.power = fixture().power;
  for (const element of spacecraftComponents(workspace)) {
    const load = structuredClone(powerFor(workspace, element));
    if (load.accounting !== 'counted') continue;
    load.states = [{ key: 'active', name: 'Active', watts: 2, basis: 'estimated', source: 'Test', conditions: '' }];
    load.assignments = { nominal: 'active', downlink: 'active' };
    workspace.power.loads.push(load);
  }
  addPowerLimits(workspace);
  for (const row of workspace.statements.filter(isPowerRequirement)) row.parameters.power_limit_W = 'if mode == "Downlink" ? 18 else 3';
  const subsystem = workspace.statements.find(row => row.id === 'PWS001');
  subsystem.parameters.allocated_power_W = 'PowerAllocation.allocated_power_W * 1.25';
  subsystem.parameters.draw_power_W = 'PowerAllocation.draw_power_W + 1';
  const source = renderExport(workspace, { catalog, packageName: 'ConditionalPowerMission' });
  assert.match(source, /if ConditionalPowerMission::spacecraft_mode == ConditionalPowerMission::spacecraft_mode_nominal/);
  assert.doesNotMatch(source, /PowerAllocation\./);
  const directory = await mkdtemp(join(tmpdir(), 'conditional-power-native-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const file = join(directory, 'mission.sysml'); await writeFile(file, source);
  const integers = fixture();
  integers.statements[0].parameters.count = 'if mode == "Downlink" ? 2 else null';
  integers.variables.push({ name: 'spacecraft_mode', type: 'float' });
  for (const row of integers.statements) row.parameters.spacecraft_mode = '1';
  const integerFile = join(directory, 'integers.sysml');
  await writeFile(integerFile, renderExport(integers, { packageName: 'ConditionalIntegerMission' }));
  const framework = fileURLToPath(new URL('../../', import.meta.url));
  const libraries = (await readdir(framework)).filter(name => name.endsWith('.sysml')).map(name => join(framework, name));
  const result = spawnSync('syside', ['check', ...libraries, file, integerFile], { encoding: 'utf8', timeout: 120000 });
  assert.equal(result.status, 0, result.stdout + result.stderr);
});

test('browser edits one conditional requirement, previews modes, and retains expressions after save and reload', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await mkdtemp(join(tmpdir(), 'conditional-requirement-browser-')), modelPath = join(directory, 'mission.sysml');
  await writeFile(modelPath, renderManaged(fixture()));
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => { await browser.close(); await new Promise(resolve => server.close(resolve)); await rm(directory, { recursive: true, force: true }); });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  await page.goto(base);
  await page.locator('[data-requirement-edit="r1"]').click();
  const editor = page.locator('#requirement-editor'), preview = editor.getByLabel('Preview mode', { exact: true });
  const output = editor.locator('[data-parameter-row="x"][data-mode="downlink"] .parameter-result');
  await page.waitForFunction(() => document.querySelector('[data-parameter-row="x"][data-mode="downlink"] .parameter-result').textContent === '18.00');
  assert.match(await editor.locator('#requirement-mode-results').textContent(), /Nominal: TRUE.*Downlink: TRUE/);
  await preview.selectOption('nominal');
  assert.equal(await output.textContent(), '18.00');
  await preview.selectOption('downlink');
  assert.equal(await output.textContent(), '18.00');
  assert.equal(await editor.getByLabel('Expression for x in Nominal', { exact: true }).inputValue(), '3');
  await editor.getByLabel('Expression for x in Nominal', { exact: true }).fill('1');
  await preview.selectOption('');
  await page.waitForFunction(() => document.querySelector('#requirement-check').textContent === 'FALSE');
  await preview.selectOption('downlink');
  assert.equal(await editor.locator('#requirement-check').textContent(), 'TRUE');
  await editor.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  await page.reload(); await page.locator('[data-requirement-edit="r1"]').click();
  assert.equal(await editor.getByLabel('Expression for x in Nominal', { exact: true }).inputValue(), '1');
  assert.equal(await editor.getByLabel('Expression for x in Downlink', { exact: true }).inputValue(), '18');
  assert.equal(await page.locator('.statements .statement-kind').count(), 0);
  await editor.getByLabel('Expression for x in Downlink', { exact: true }).fill('99');
  await editor.getByRole('button', { name: 'Cancel', exact: true }).click();
  const saved = (await (await page.request.get(base + '/api/workspace')).json()).workspace;
  assert.equal(saved.statements.length, 2);
  assert.deepEqual(parameterStates(saved.statements[0].parameters.x, saved.power.modes).values, { nominal: '1', downlink: '18' });
  assert.deepEqual(errors, []);
});
