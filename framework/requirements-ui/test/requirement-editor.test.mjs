import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import {
  declareRequirementVariables, emptyWorkspace, interpolateRequirement, mergeRequirementDraft, requirementMarkers,
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

test('marker previews format evaluated values, preserve zero and show unknown variable names', () => {
  assert.equal(interpolateRequirement('At least $$energy_J$$ J, margin $$margin$$.', { energy_J: 7200, margin: 0 }), 'At least 7200 J, margin 0.000.');
  assert.equal(interpolateRequirement('Unknown $$energy_J$$ and legacy {x}.', { x: 3 }), 'Unknown energy_J and legacy 3.000.');
  assert.equal(interpolateRequirement('$$bad-name$$ $$x$$', { x: Infinity }), '$$bad-name$$ x');
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

test('requirement drafts merge with other table edits without overwriting them', () => {
  const original = fixture(), edited = structuredClone(original), current = structuredClone(original);
  const row = edited.statements[0];
  row.text = 'The battery shall provide $$energy_J$$.';
  row.rationale = 'Capacity reference and margin assumptions.';
  declareRequirementVariables(edited, row);
  row.parameters.energy_J = '7200';
  edited.variables.find(variable => variable.name === 'energy_J').unit = 'J';
  current.stakeholders.push({ key: 's1', id: 'OPS', name: 'Mission operators', type: 'Mission Stakeholder' });
  current.statements[0].sources = ['s1']; current.statements[0].parameters.y = '9';
  const merged = validateWorkspace(mergeRequirementDraft(current, original, edited, row.key));
  assert.deepEqual(merged.stakeholders, current.stakeholders);
  assert.deepEqual(merged.statements[0].sources, ['s1']);
  assert.equal(merged.statements[0].parameters.y, '9');
  assert.equal(merged.statements[0].parameters.energy_J, '7200');
  assert.equal(merged.statements[0].rationale, row.rationale);
  assert.equal(merged.variables.find(variable => variable.name === 'energy_J').unit, 'J');
  assert.deepEqual(original, fixture());
  assert.equal(current.statements[0].text, '');
});

test('conflicting edits and deleted requirements keep drafts from overwriting current data', () => {
  const original = fixture(), edited = structuredClone(original), current = structuredClone(original);
  edited.statements[0].text = 'A draft.'; current.statements[0].text = 'Another edit.';
  assert.throws(() => mergeRequirementDraft(current, original, edited, 'r1'), /changed while you were editing/);
  current.statements[0].text = '';
  edited.statements[0].rationale = 'A draft rationale.'; current.statements[0].rationale = 'Another rationale.';
  assert.throws(() => mergeRequirementDraft(current, original, edited, 'r1'), /changed while you were editing/);
  delete edited.statements[0].rationale; delete current.statements[0].rationale;
  edited.variables[0].unit = 'm'; current.variables[0].unit = 'km';
  assert.throws(() => mergeRequirementDraft(current, original, edited, 'r1'), /changed while you were editing/);
  current.statements = [];
  assert.throws(() => mergeRequirementDraft(current, original, edited, 'r1'), /changed while you were editing/);
});

test('requirement pane browser workflow', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const dir = await mkdtemp(join(tmpdir(), 'requirement-pane-browser-'));
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
  const legacy = await get();
  legacy.workspace.statements.forEach(row => { delete row.rationale; });
  const legacySave = await page.request.put(base + '/api/workspace', { data: { workspace: legacy.workspace, revision: legacy.revision } });
  assert.equal(legacySave.ok(), true);
  await page.goto(base + '/#mission');
  await page.locator('main:not([inert])').waitFor();
  assert.equal(await page.locator('.statements td.parameter, .statements .add-variable').count(), 0);
  assert.equal(await page.locator('.statements thead th').count(), 6);
  const initial = await get();
  assert.equal(await page.locator('.statements tbody tr').count(), initial.workspace.statements.filter(row => row.context === 'mission').length + 1);
  const orbit = page.locator('tr[data-key="generic-ORB-OrbitPeriod"]');
  const orbitData = initial.workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  assert.equal(orbitData.rationale, undefined);
  assert.equal(await orbit.locator('.statement-summary').getAttribute('title'), orbitData.text);
  assert.equal(await orbit.locator('.checkbox-cell > input[type="checkbox"]').count(), 1);
  assert.equal(await orbit.locator('.checkbox-cell > button.verification-edit svg').count(), 1);
  assert.equal(await orbit.locator('.checkbox-cell').textContent(), '');
  assert.equal(await orbit.locator('.verification-result').isDisabled(), true);
  assert.equal(await page.locator('#verification-editor, #verification-condition').count(), 0);
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  const dialog = page.locator('#requirement-editor');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await dialog.evaluate(element => element.tagName), 'ASIDE');
  assert.equal(await page.locator(':modal, #requirement-preview, #requirement-origin').count(), 0);
  assert.equal(await dialog.getByLabel('Rationale', { exact: true }).inputValue(), orbitData.origin);
  await page.waitForFunction(() => document.querySelector('#requirement-check').dataset.state === 'pending');
  assert.equal(await dialog.locator('#requirement-check').textContent(), 'PENDING');
  await dialog.locator('#requirement-rationale').fill('Discard this edited rationale.');
  assert.equal(await page.locator('main').getAttribute('inert'), null);
  const paneBounds = await dialog.boundingBox(), workspaceBounds = await page.locator('main').boundingBox();
  assert.ok(workspaceBounds.x + workspaceBounds.width <= paneBounds.x);
  assert.equal(paneBounds.x + paneBounds.width, 1600);
  assert.equal(await dialog.locator('[data-parameter-unit="gravitationalParameter_km3_s2"]').inputValue(), 'km^3/s^2');
  assert.equal(await dialog.locator('[data-parameter-unit="altitude_km"]').inputValue(), 'km');
  assert.equal(await dialog.locator('[data-parameter]').count(), 4);
  assert.deepEqual(await dialog.locator('thead th').allTextContents(), ['Name', 'Expression', 'Units', 'Evaluated value']);
  assert.equal(await dialog.locator('[data-parameter-unit]').count(), 4);
  assert.equal(await dialog.locator('tbody tr').count(), 4);
  assert.equal(await dialog.locator('.requirement-parameter-frame select').count(), 0);
  await dialog.locator('#requirement-text').fill('The orbit shall have altitude $$altitude_km$$ km and $$new_quantity$$.');
  await dialog.locator('[data-parameter-unit="new_quantity"]').pressSequentially('m^2/s^2');
  assert.equal(await dialog.locator('[data-parameter-unit="new_quantity"]').inputValue(), 'm^2/s^2');
  assert.equal(await dialog.locator('[data-parameter-unit="new_quantity"]').evaluate(element => element === document.activeElement), true);
  const quantity = dialog.locator('[data-parameter-row="new_quantity"]');
  assert.equal(await quantity.locator('.parameter-result').textContent(), 'Unset');
  assert.equal(await quantity.locator('.parameter-unit').count(), 0);
  await dialog.locator('[data-parameter="new_quantity"]').fill('2 + 3');
  await dialog.locator('[data-parameter="altitude_km"]').fill('300 + 200');
  await page.waitForFunction(() => document.querySelector('[data-parameter="new_quantity"]').closest('tr').querySelector('.parameter-result').textContent === '5.000 m2/s2');
  assert.deepEqual(await quantity.locator('.parameter-unit sup').allTextContents(), ['2', '2']);
  assert.equal(await quantity.locator('.parameter-number').textContent(), '5.000');
  assert.match(await quantity.locator('.parameter-number').evaluate(element => getComputedStyle(element).fontFamily), /monospace/);
  assert.match(await quantity.locator('.parameter-unit').evaluate(element => getComputedStyle(element).fontFamily), /monospace/);
  await page.getByRole('tab', { name: 'EPS', exact: true }).click();
  assert.equal(await dialog.isVisible(), true);
  assert.equal(await dialog.locator('[data-parameter="new_quantity"]').inputValue(), '2 + 3');
  await page.getByRole('tab', { name: 'Mission', exact: true }).click();
  await page.locator('tr[data-key="generic-ORB-OrbitPeriodClosure"] [data-links="sources"] .source-edit').click();
  await page.keyboard.press('Escape');
  assert.equal(await dialog.isVisible(), true);
  assert.equal(await page.locator('#source-editor').isVisible(), false);
  page.once('dialog', prompt => prompt.dismiss());
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriodClosure"]').click();
  assert.equal(await dialog.locator('#requirement-editor-title').textContent(), 'Edit ORB001');
  assert.equal(await dialog.locator('[data-parameter="new_quantity"]').inputValue(), '2 + 3');
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
  assert.equal(await dialog.locator('#requirement-rationale').inputValue(), orbitData.origin);
  await dialog.locator('#requirement-condition').fill('false');
  await page.waitForFunction(() => document.querySelector('#requirement-check').textContent === 'FALSE');
  assert.equal(await dialog.locator('#requirement-check').evaluate(element => getComputedStyle(element).color), 'rgb(180, 63, 49)');
  await dialog.locator('#requirement-condition').fill('1 +');
  await page.waitForFunction(() => document.querySelector('#requirement-check').dataset.state === 'error');
  assert.match(await dialog.locator('#requirement-check').textContent(), /expression|expected|unexpected/i);
  assert.equal(await dialog.locator('#requirement-check').evaluate(element => getComputedStyle(element).color), 'rgb(138, 101, 0)');
  await dialog.locator('#requirement-condition').fill('');
  assert.equal(await dialog.locator('#requirement-check').isVisible(), false);
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.deepEqual((await get()).workspace, initial.workspace);
  await orbit.locator('.verification-edit').focus(); await page.keyboard.press('F2');
  await dialog.waitFor({ state: 'visible' }); await page.keyboard.press('Escape');
  await page.locator('[data-tab="external"]').click();
  assert.equal(await page.locator('.stakeholders tbody tr').count(), 1);
  assert.equal(await page.locator('.statements tbody tr').count(), 1);
  assert.equal(await page.locator('.statements .row-delete').isDisabled(), true);
  await page.locator('.statements .add-row').click();
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.equal(await page.locator('.statements tbody tr').count(), 1);
  await page.locator('.statements .statement-summary').press('Enter');
  await dialog.locator('#requirement-text').fill('The battery shall provide at least $$energy_J$$, expressed once as $$energy_J$$.');
  assert.equal(await dialog.locator('[data-parameter="energy_J"]').count(), 1);
  assert.equal(await dialog.locator('[data-parameter]').count(), 1);
  await dialog.locator('[data-parameter="energy_J"]').fill('2 * 3600');
  await dialog.locator('[data-parameter-unit="energy_J"]').fill('J');
  const rationale = 'final_report/design-proposal.tex#eq:battery-energy\nIncludes the declared energy margin.';
  await dialog.locator('#requirement-rationale').fill(rationale);
  await dialog.locator('#requirement-condition').fill('energy_J >= 7200');
  await page.waitForFunction(() => document.querySelector('#requirement-check').textContent === 'TRUE');
  assert.equal(await dialog.locator('#requirement-check').evaluate(element => getComputedStyle(element).color), 'rgb(46, 107, 60)');
  await page.getByRole('tab', { name: 'Mission', exact: true }).click();
  assert.equal(await dialog.locator('#requirement-text').inputValue(), 'The battery shall provide at least $$energy_J$$, expressed once as $$energy_J$$.');
  await page.getByRole('tab', { name: 'External', exact: true }).click();
  await page.locator('.stakeholders [data-field="name"]').fill('Mission operators');
  await dialog.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await dialog.waitFor({ state: 'hidden' });
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const saved = await get(), added = saved.workspace.statements.find(row => row.context === 'external' && row.text.startsWith('The battery shall provide'));
  assert.ok(added);
  assert.equal(saved.workspace.stakeholders[0].name, 'Mission operators');
  assert.equal(added.parameters.energy_J, '2 * 3600');
  assert.equal(added.rationale, rationale);
  assert.equal((await page.locator('.statements').textContent()).includes(rationale), false);
  assert.equal(await page.locator(`tr[data-key="${added.key}"] .statement-summary`).getAttribute('title'), added.text);
  assert.equal(saved.workspace.variables.find(variable => variable.name === 'energy_J').unit, 'J');
  assert.equal(await page.locator('.statements tbody tr').count(), 2);
  assert.equal(await page.locator('.statements tbody tr').last().locator('.row-delete').isDisabled(), true);
  assert.match(await page.locator(`tr[data-key="${added.key}"] .statement-preview`).textContent(), /7200 J/);
  assert.deepEqual(await page.locator(`tr[data-key="${added.key}"] .statement-preview .parameter-unit`).allTextContents(), ['J', 'J']);
  const numbers = page.locator(`tr[data-key="${added.key}"] .statement-preview .parameter-number`);
  assert.deepEqual(await numbers.allTextContents(), ['7200', '7200']);
  assert.match(await numbers.first().evaluate(element => getComputedStyle(element).fontFamily), /monospace/);
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
  assert.match(await page.locator('#status').textContent(), /only in the requirement pane/);
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
  await dialog.locator('[data-parameter-unit="energy_J"]').evaluate(element => {
    const clipboardData = new DataTransfer(); clipboardData.setData('text/plain', 'J\n%');
    element.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData }));
  });
  assert.equal(await dialog.locator('[data-parameter-unit="energy_J"]').inputValue(), 'J');
  assert.equal(await dialog.locator('[data-parameter-unit="margin"]').inputValue(), '%');
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
  assert.equal(await dialog.locator('#requirement-rationale').inputValue(), rationale);
  assert.equal(await dialog.locator('[data-parameter-unit="energy_J"]').inputValue(), 'J');
  assert.equal(await dialog.locator('[data-parameter-unit="margin"]').inputValue(), '%');
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
  await dialog.locator('#requirement-rationale').fill('Discard this changed rationale.');
  await dialog.locator('[data-parameter-unit="energy_J"]').fill('kg');
  await dialog.locator('[data-parameter="energy_J"]').fill('1 +');
  await page.waitForFunction(() => document.querySelector('[data-parameter="energy_J"]').getAttribute('aria-invalid') === 'true');
  assert.equal(await dialog.locator('[data-parameter-row="energy_J"] .parameter-result').textContent(), 'Error');
  assert.equal(await dialog.locator('[data-parameter-row="energy_J"] .parameter-unit').count(), 0);
  await dialog.getByRole('button', { name: 'Cancel', exact: true }).click();
  const cancelled = await get();
  assert.equal(cancelled.workspace.variables.find(variable => variable.name === 'energy_J').unit, 'J');
  assert.equal(cancelled.workspace.statements.find(row => row.key === added.key).rationale, rationale);
  const [download] = await Promise.all([page.waitForEvent('download'), page.locator('.export-sysml').click()]);
  const exported = join(dir, 'download.sysml'); await download.saveAs(exported);
  assert.match(await readFile(exported, 'utf8'), /attribute 'energy_J' : Real\[0\.\.1\] = \(3 \* 3600\)/);
  assert.match(await readFile(exported, 'utf8'), /attribute rationale : String =/);
  await addedRow.locator('.row-delete').click();
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  assert.equal(await page.locator('.statements tbody tr').count(), 1);
  assert.equal((await get()).workspace.statements.filter(row => row.context === 'external').length, 0);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole('tab', { name: 'Mission', exact: true }).click();
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  const mobileWorkspace = await page.locator('main').boundingBox(), mobilePane = await dialog.boundingBox();
  assert.ok(mobileWorkspace.height > 250 && mobilePane.height > 300);
  assert.ok(mobileWorkspace.y + mobileWorkspace.height <= mobilePane.y + 1);
  await page.keyboard.press('Escape');
  assert.equal(await dialog.isVisible(), false);
  assert.deepEqual(errors, []);
});
