import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import {
  declareRequirementVariables, emptyWorkspace, interpolateRequirement, requirementMarkers,
  requirementParameterNames, validateWorkspace,
} from '../model.mjs';
import { evaluateChecks } from '../verification.mjs';
import { readWorkspace, renderExport, renderManaged } from '../sysml.mjs';
import { createServer } from '../server.mjs';

function fixture() {
  const workspace = emptyWorkspace();
  workspace.statements.push({ key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement',
    text: '', condition: '', sources: [], affected: [], parameters: { x: null, y: null, z: null, a: null } });
  return workspace;
}

test('double-dollar markers create one named column for each valid identifier', () => {
  assert.deepEqual(requirementMarkers('At least $$energy_J$$ J, with $$energy_J$$ repeated and $$ _margin $$.'), {
    names: ['energy_J', '_margin'], errors: [],
  });
  assert.deepEqual(requirementMarkers('No variables.'), { names: [], errors: [] });
  for (const text of ['$$bad-name$$', '$$two words$$', '$$2mass$$', '$$true$$', '$$REQ001$$', '$$$$', '$$__proto__$$', '$$mass']) {
    assert.ok(requirementMarkers(text).errors.length, text);
  }
  assert.deepEqual(requirementMarkers('$$mass$$ and $$unfinished').names, ['mass']);
});

test('declared columns reuse types, keep per-row values and initialize the other rows', () => {
  const workspace = fixture();
  workspace.variables.push({ name: 'cell_count', type: 'integer' });
  workspace.statements[0].parameters.cell_count = '3';
  workspace.statements.push({ ...workspace.statements[0], key: 'r2', id: 'REQ002', parameters: { ...workspace.statements[0].parameters, cell_count: '5' } });
  workspace.statements[0].text = 'Use $$cell_count$$ cells with $$energy_J$$ J.';
  const markers = declareRequirementVariables(workspace, workspace.statements[0]);
  assert.deepEqual(markers.names, ['cell_count', 'energy_J']);
  assert.equal(workspace.variables.find(variable => variable.name === 'cell_count').type, 'integer');
  assert.equal(workspace.variables.filter(variable => variable.name === 'energy_J').length, 1);
  assert.equal(workspace.statements[0].parameters.cell_count, '3');
  assert.equal(workspace.statements[1].parameters.cell_count, '5');
  assert.equal(workspace.statements[1].parameters.energy_J, null);
  assert.doesNotThrow(() => validateWorkspace(workspace));
  declareRequirementVariables(workspace, workspace.statements[0]);
  assert.equal(workspace.variables.filter(variable => variable.name === 'energy_J').length, 1);
});

test('a requirement editor shows its markers and retained inputs, not all workbook columns', () => {
  const workspace = fixture(), row = workspace.statements[0];
  assert.deepEqual(requirementParameterNames(workspace, row), []);
  row.text = 'At least $$energy_J$$ J.';
  declareRequirementVariables(workspace, row);
  assert.deepEqual(requirementParameterNames(workspace, row), ['energy_J']);
  row.parameters.energy_J = 'x * REQ002.y';
  assert.deepEqual(requirementParameterNames(workspace, row), ['energy_J', 'x']);
  row.condition = 'energy_J >= a';
  assert.deepEqual(requirementParameterNames(workspace, row), ['energy_J', 'x', 'a']);
  row.text = 'Legacy {z}.'; row.parameters.x = '12';
  assert.deepEqual(requirementParameterNames(workspace, row), ['x', 'z', 'a', 'energy_J']);
});

test('existing generic requirements retain all their relevant inputs when opened', async () => {
  const catalog = await loadCatalog(), workspace = emptyWorkspace(catalog);
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  assert.deepEqual(new Set(requirementParameterNames(workspace, orbit, catalog)),
    new Set(['altitude_km', 'earthRadius_km', 'gravitationalParameter_km3_s2', 'orbit_period_s']));
  const generation = workspace.statements.find(row => row.definition === 'FrameworkRequirements::EPS02');
  assert.deepEqual(requirementParameterNames(workspace, generation, catalog), ['panel_min_W', 'sunlight_generation_J', 'sunlight_s']);
});

test('unknown, invalid and incomplete markers cannot silently become saved requirements', () => {
  for (const text of ['At least $$unknown$$.', 'At least $$invalid-name$$.', 'At least $$unfinished']) {
    const workspace = fixture(); workspace.statements[0].text = text;
    assert.throws(() => validateWorkspace(workspace), /declare each|variable name|Close each/);
  }
  const workspace = fixture();
  workspace.variables = Array.from({ length: 64 }, (_, index) => ({ name: `v${index}`, type: 'float' }));
  workspace.statements[0].text = '$$extra$$';
  assert.throws(() => declareRequirementVariables(workspace, workspace.statements[0]), /64 variable names/);
  assert.equal(workspace.variables.length, 64);
});

test('marker previews substitute evaluated values, preserve zero and leave unknown values visible', () => {
  assert.equal(interpolateRequirement('At least $$energy_J$$ J, margin $$margin$$.', { energy_J: 7200, margin: 0 }), 'At least 7200 J, margin 0.');
  assert.equal(interpolateRequirement('Unknown $$energy_J$$ and legacy {x}.', { x: 3 }), 'Unknown $$energy_J$$ and legacy 3.');
  assert.equal(interpolateRequirement('$$bad-name$$ $$x$$', { x: Infinity }), '$$bad-name$$ $$x$$');
});

test('marker-driven expressions round trip and export as native attributes and equations', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.text = 'The battery shall provide at least $$energy_J$$ J.';
  declareRequirementVariables(workspace, row);
  row.parameters.energy_J = '2 * 3600';
  row.condition = 'energy_J >= 7200';
  assert.equal(evaluateChecks(workspace)[0].state, 'pass');
  assert.equal(interpolateRequirement(row.text, evaluateChecks(workspace)[0].values), 'The battery shall provide at least 7200 J.');
  assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
  const exported = renderExport(workspace);
  assert.match(exported, /attribute 'energy_J' : Real\[0\.\.1\] = \(2 \* 3600\)/);
  assert.match(exported, /require constraint verificationCondition/);
});

test('requirement modal browser workflow', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const dir = await mkdtemp(join(tmpdir(), 'requirement-modal-browser-'));
  const modelPath = join(dir, 'mission.sysml'), server = createServer({ modelPath });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  t.after(async () => {
    await browser?.close();
    await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    await rm(dir, { recursive: true, force: true });
  });
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, acceptDownloads: true });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  const get = async () => (await page.request.get(base + '/api/workspace')).json();
  await page.goto(base + '/#mission');
  await page.locator('main:not([inert])').waitFor();
  assert.equal(await page.locator('.statements td.parameter, .statements .add-variable').count(), 0);
  assert.equal(await page.locator('.statements thead th').count(), 6);
  const initial = await get();
  const orbit = page.locator('tr[data-key="generic-ORB-OrbitPeriod"]');
  assert.equal(await orbit.locator('.checkbox-cell > input[type="checkbox"]').count(), 1);
  assert.equal(await orbit.locator('.checkbox-cell > button.verification-edit svg').count(), 1);
  assert.equal(await orbit.locator('.checkbox-cell').textContent(), '');
  assert.equal(await orbit.locator('.verification-result').isDisabled(), true);
  assert.equal(await page.locator('#verification-editor, #verification-condition').count(), 0);
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  const dialog = page.locator('#requirement-editor');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await dialog.locator('[data-parameter]').count(), 4);
  assert.deepEqual(await dialog.locator('thead th').allTextContents(), ['Name', 'Expression', 'Evaluated value']);
  assert.equal(await dialog.locator('tbody tr').count(), 4);
  assert.equal(await dialog.locator('.requirement-parameter-frame select').count(), 0);
  await dialog.locator('#requirement-text').fill('The orbit shall have altitude $$altitude_km$$ km and $$new_quantity$$.');
  await dialog.locator('[data-parameter="new_quantity"]').fill('2 + 3');
  await dialog.locator('[data-parameter="altitude_km"]').fill('300 + 200');
  await page.waitForFunction(() => document.querySelector('[data-parameter="new_quantity"]').closest('tr').querySelector('.parameter-result').textContent === '5');
  assert.deepEqual((await get()).workspace, initial.workspace);
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.deepEqual((await get()).workspace, initial.workspace);
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  assert.equal(await dialog.locator('[data-parameter="new_quantity"]').count(), 0);
  await page.keyboard.press('Escape');
  await orbit.locator('.verification-edit').click();
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await dialog.locator('#requirement-condition').evaluate(element => element === document.activeElement), true);
  assert.equal(await dialog.locator('#requirement-text').inputValue(), initial.workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod').text);
  await dialog.locator('#requirement-condition').fill('false');
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.deepEqual((await get()).workspace, initial.workspace);
  await orbit.locator('.verification-edit').focus(); await page.keyboard.press('F2');
  await dialog.waitFor({ state: 'visible' }); await page.keyboard.press('Escape');
  await page.locator('[data-tab="external"]').click();
  await page.locator('.statements .add-row').click();
  await dialog.locator('#requirement-text').fill('The battery shall provide at least $$energy_J$$ J, expressed once as $$energy_J$$.');
  assert.equal(await dialog.locator('[data-parameter="energy_J"]').count(), 1);
  assert.equal(await dialog.locator('[data-parameter]').count(), 1);
  await dialog.locator('[data-parameter="energy_J"]').fill('2 * 3600');
  await dialog.locator('#requirement-condition').fill('energy_J >= 7200');
  await page.waitForFunction(() => document.querySelector('#requirement-check').textContent.startsWith('True:'));
  assert.match(await dialog.locator('#requirement-preview').textContent(), /7200 J/);
  await dialog.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await dialog.waitFor({ state: 'hidden' });
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const saved = await get(), added = saved.workspace.statements.find(row => row.context === 'external' && row.text.startsWith('The battery shall provide'));
  assert.ok(added);
  assert.equal(added.parameters.energy_J, '2 * 3600');
  assert.match(await page.locator(`tr[data-key="${added.key}"] .statement-preview`).textContent(), /7200 J/);
  assert.equal(await page.locator('.statements td.parameter').count(), 0);
  const addedRow = page.locator(`tr[data-key="${added.key}"]`), summary = addedRow.locator('.statement-summary');
  assert.equal(await addedRow.locator('.statement-cell input, .statement-cell textarea, [contenteditable="true"]').count(), 0);
  assert.equal(await summary.getAttribute('contenteditable'), 'false');
  const preview = await addedRow.locator('.statement-preview').textContent();
  await summary.focus(); await page.keyboard.type('INLINE');
  assert.equal(await addedRow.locator('.statement-preview').textContent(), preview);
  await summary.evaluate(element => {
    const clipboardData = new DataTransfer(); clipboardData.setData('text/plain', 'An inline replacement.');
    element.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData }));
  });
  assert.match(await page.locator('#status').textContent(), /only in the requirement modal/);
  assert.equal((await get()).workspace.statements.find(row => row.key === added.key).text, added.text);
  assert.equal(await addedRow.locator('.statement-preview').textContent(), preview);
  await page.locator(`[data-requirement-edit="${added.key}"]`).click();
  await dialog.locator('#requirement-text').fill('Invalid $$bad-name$$.');
  assert.equal(await dialog.locator('#requirement-save').isDisabled(), true);
  assert.match(await dialog.locator('#requirement-error').textContent(), /variable name/);
  assert.equal(await dialog.locator('[data-parameter="energy_J"]').inputValue(), '2 * 3600');
  await dialog.locator('#requirement-text').fill('Only $$energy_J$$ J and $$temporary$$.');
  await dialog.locator('[data-parameter="temporary"]').waitFor();
  await dialog.locator('#requirement-text').fill('Only $$energy_J$$ J.');
  assert.equal(await dialog.locator('[data-parameter="temporary"]').count(), 0);
  await dialog.locator('#requirement-text').fill('At least $$energy_J$$ J with $$margin$$.');
  await dialog.locator('[data-parameter="energy_J"]').evaluate(element => {
    const clipboardData = new DataTransfer(); clipboardData.setData('text/plain', '3 * 3600\n0.2');
    element.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData }));
  });
  assert.equal(await dialog.locator('[data-parameter="energy_J"]').inputValue(), '3 * 3600');
  assert.equal(await dialog.locator('[data-parameter="margin"]').inputValue(), '0.2');
  await page.keyboard.press('Control+Enter');
  await dialog.waitFor({ state: 'hidden' });
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const changed = await get();
  assert.equal(changed.workspace.variables.some(variable => variable.name === 'temporary'), false);
  assert.equal(changed.workspace.statements.find(row => row.key === added.key).parameters.margin, '0.2');
  assert.ok(initial.workspace.variables.every(variable => changed.workspace.variables.find(current => current.name === variable.name).type === variable.type));
  await page.reload(); await page.locator('main:not([inert])').waitFor();
  await page.locator(`[data-verification-edit="${added.key}"]`).click();
  assert.equal(await dialog.locator('[data-parameter="energy_J"]').inputValue(), '3 * 3600');
  assert.equal(await dialog.locator('.requirement-parameter-frame select').count(), 0);
  await dialog.locator('#requirement-condition').fill('false');
  await dialog.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await dialog.waitFor({ state: 'hidden' });
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  assert.equal(await addedRow.locator('.verification-result').isChecked(), false);
  assert.equal(await page.evaluate(() => document.activeElement.dataset.verificationEdit), added.key);
  assert.equal((await get()).workspace.statements.find(row => row.key === added.key).text, changed.workspace.statements.find(row => row.key === added.key).text);
  await page.locator(`[data-verification-edit="${added.key}"]`).click();
  assert.equal(await dialog.locator('#requirement-condition').inputValue(), 'false');
  await dialog.locator('[data-parameter="energy_J"]').fill('1 +');
  await page.waitForFunction(() => document.querySelector('[data-parameter="energy_J"]').getAttribute('aria-invalid') === 'true');
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  const [download] = await Promise.all([page.waitForEvent('download'), page.locator('.export-sysml').click()]);
  const exported = join(dir, 'download.sysml'); await download.saveAs(exported);
  assert.match(await readFile(exported, 'utf8'), /attribute 'energy_J' : Real\[0\.\.1\] = \(3 \* 3600\)/);
  assert.deepEqual(errors, []);
});
