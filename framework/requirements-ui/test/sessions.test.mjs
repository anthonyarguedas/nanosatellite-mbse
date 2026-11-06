import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { createServer } from '../server.mjs';
import { createSessions } from '../sessions.mjs';
import { loadCatalog } from '../catalog.mjs';
import { emptyWorkspace, tabsFor, validateWorkspace } from '../model.mjs';

async function start(t) {
  const directory = await mkdtemp(join(tmpdir(), 'requirements-sessions-'));
  const modelPath = join(directory, 'mission.json'), original = JSON.stringify(emptyWorkspace(await loadCatalog()), null, 2) + '\n';
  await writeFile(modelPath, original);
  const server = createServer({ modelPath });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(async () => {
    await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    await rm(directory, { recursive: true, force: true });
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  const get = async (id = 'current') => (await fetch(`${base}/api/workspace?session=${encodeURIComponent(id)}`)).json();
  const create = data => fetch(base + '/api/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
  const put = (id, workspace, revision) => fetch(`${base}/api/workspace?session=${encodeURIComponent(id)}`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace, revision }),
  });
  return { base, directory, modelPath, original, get, create, put };
}

test('the existing mission remains available without creating or changing session files', async t => {
  const { base, directory, modelPath, original, get } = await start(t);
  const response = await fetch(base + '/api/sessions');
  assert.equal(response.status, 200);
  const { sessions } = await response.json();
  assert.equal(sessions.length, 1);
  assert.equal(sessions[0].id, 'current');
  assert.equal((await get()).workspace.statements.length, 27);
  assert.deepEqual(await readdir(directory), ['mission.json']);
  assert.equal(await readFile(modelPath, 'utf8'), original);
});

test('Blank and Generic EPS create independent, persistent workspaces', async t => {
  const { create, get, modelPath, original, directory, base } = await start(t);
  const blankResponse = await create({ name: 'Blank study', template: 'blank' });
  assert.equal(blankResponse.status, 201);
  const blank = await blankResponse.json();
  assert.equal(blank.workspace.statements.length, 0);
  assert.equal(blank.workspace.elements.length, 0);
  assert.equal(blank.workspace.stakeholders.length, 0);
  assert.equal(blank.workspace.components.length, 0);
  assert.equal(tabsFor(blank.workspace, blank.catalog).length, 2);
  assert.doesNotThrow(() => validateWorkspace(blank.workspace, blank.catalog, blank.products));
  const genericResponse = await create({ name: 'Generic EPS study', template: 'generic-eps' });
  assert.equal(genericResponse.status, 201);
  const generic = await genericResponse.json();
  assert.equal(generic.workspace.statements.length, 27);
  const orbit = generic.workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  assert.equal(orbit.parameters.altitude_km, null);
  assert.equal(orbit.parameters.earthRadius_km, '6378');
  assert.equal(generic.workspace.variables.find(variable => variable.name === 'gravitationalParameter_km3_s2').unit, 'km^3/s^2');
  assert.equal(orbit.rationale, orbit.origin);
  assert.notEqual(blank.session.id, generic.session.id);
  assert.deepEqual((await get(blank.session.id)).workspace, blank.workspace);
  assert.deepEqual((await get(generic.session.id)).workspace, generic.workspace);
  assert.equal((await (await fetch(base + '/api/sessions')).json()).sessions.length, 3);
  assert.equal(await readFile(modelPath, 'utf8'), original);
  const restarted = createSessions(modelPath, { catalog: await loadCatalog() });
  assert.deepEqual((await (await restarted.get(generic.session.id)).store.read()).workspace, generic.workspace);
  assert.equal((await readdir(join(directory, 'sessions'))).length, 2);
});

test('Save as retains edits, expressions, units and rationale without changing the source session', async t => {
  const { create, get, modelPath, original } = await start(t);
  const generic = await (await create({ name: 'EPS baseline', template: 'generic-eps' })).json();
  const workspace = structuredClone(generic.workspace);
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = '300 + 300';
  orbit.rationale += '\nUse the selected mission altitude.';
  orbit.condition = '1 +';
  workspace.variables.find(variable => variable.name === 'altitude_km').unit = 'km';
  const copiedResponse = await create({ name: 'EPS mission study', template: 'copy', workspace });
  assert.equal(copiedResponse.status, 201);
  const copy = await copiedResponse.json();
  assert.notEqual(copy.session.id, generic.session.id);
  assert.deepEqual(copy.workspace, workspace);
  assert.deepEqual((await get(copy.session.id)).workspace, workspace);
  assert.deepEqual((await get(generic.session.id)).workspace, generic.workspace);
  assert.equal(await readFile(modelPath, 'utf8'), original);
});

test('autosave revisions and conflicts are isolated by session', async t => {
  const { create, get, put } = await start(t);
  const first = await (await create({ name: 'First', template: 'generic-eps' })).json();
  const second = await (await create({ name: 'Second', template: 'generic-eps' })).json();
  first.workspace.statements[0].rationale = 'First study rationale.';
  assert.equal((await put(first.session.id, first.workspace, first.revision)).status, 200);
  assert.equal((await put(first.session.id, first.workspace, first.revision)).status, 409);
  assert.equal((await put(second.session.id, second.workspace, first.revision)).status, 409);
  second.workspace.statements[0].rationale = 'Second study rationale.';
  assert.equal((await put(second.session.id, second.workspace, second.revision)).status, 200);
  assert.equal((await get(first.session.id)).workspace.statements[0].rationale, 'First study rationale.');
  assert.equal((await get(second.session.id)).workspace.statements[0].rationale, 'Second study rationale.');
});

test('session creation validates names, templates, workspaces and concurrent duplicate names', async t => {
  const { create, get } = await start(t);
  for (const name of ['', '  ', 'a'.repeat(81), 'two\nlines', null]) assert.equal((await create({ name, template: 'blank' })).status, 400);
  assert.equal((await create({ name: 'Unknown', template: 'missing' })).status, 400);
  assert.equal((await create({ name: 'Invalid copy', template: 'copy', workspace: {} })).status, 400);
  assert.equal((await create({ name: 'Not a copy', template: 'blank', workspace: (await get()).workspace })).status, 400);
  const results = await Promise.all([create({ name: 'Same name', template: 'blank' }), create({ name: 'same name', template: 'blank' })]);
  assert.deepEqual(results.map(result => result.status).sort(), [201, 409]);
});

test('session IDs cannot traverse paths and missing files are never regenerated', async t => {
  const { base, create, directory, get } = await start(t);
  for (const id of ['../mission', '/tmp/other', 'missing', '../../requirements.sysml']) {
    assert.equal((await fetch(`${base}/api/workspace?session=${encodeURIComponent(id)}`)).status, 400);
  }
  assert.equal((await fetch(base + '/api/workspace?session=00000000-0000-0000-0000-000000000000')).status, 404);
  const created = await (await create({ name: '../Display name only', template: 'blank' })).json();
  assert.match(created.session.id, /^[a-f0-9-]{36}$/);
  const file = join(directory, 'sessions', created.session.id, `${created.session.id}.json`);
  await rm(file);
  assert.equal((await fetch(`${base}/api/workspace?session=${created.session.id}`)).status, 404);
  assert.ok(!(await readdir(join(directory, 'sessions', created.session.id))).includes(`${created.session.id}.json`));
  assert.equal((await get()).session.id, 'current');
  assert.equal((await fetch(base + '/sessions.mjs')).status, 404);
  assert.equal((await fetch(base + '/api/sessions', { method: 'DELETE' })).status, 405);
});

test('session creation rejects cross-origin and non-JSON writes', async t => {
  const { base } = await start(t);
  const body = JSON.stringify({ name: 'Untrusted', template: 'blank' });
  assert.equal((await fetch(base + '/api/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: 'https://other.example' }, body })).status, 403);
  assert.equal((await fetch(base + '/api/sessions', { method: 'POST', body })).status, 415);
});

test('saved sessions are JSON and reopen with the same Python calculation inputs', async t => {
  const { create, directory, base } = await start(t);
  const blank = await (await create({ name: 'Blank', template: 'blank' })).json();
  const generic = await (await create({ name: 'Generic EPS', template: 'generic-eps' })).json();
  for (const data of [blank, generic]) {
    const file = join(directory, 'sessions', data.session.id, `${data.session.id}.json`);
    assert.deepEqual(JSON.parse(await readFile(file, 'utf8')), data.workspace);
    assert.equal(data.workspace.expressionLanguage, 'python');
    assert.equal((await readdir(join(directory, 'sessions', data.session.id))).some(name => name.endsWith('.sysml')), false);
  }
  const response = await fetch(`${base}/api/evaluate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace: generic.workspace }) });
  assert.equal(response.status, 200);
  const calculations = await response.json();
  assert.equal(calculations.results.find(row => row.key.endsWith('OrbitPeriod')).state, 'pending');
  assert.equal(calculations.results.find(row => row.key.endsWith('OrbitPeriod')).values.earthRadius_km, 6378);
});

test('session browser workflow keeps templates, saved copies and in-flight autosaves separate', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const { base, get, modelPath, original, directory } = await start(t);
  const browser = await chromium.launch({ headless: true });
  t.after(() => browser.close());
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, acceptDownloads: true });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  await page.goto(base);
  await page.locator('main:not([inert])').waitFor();
  const initial = await get();
  const select = page.locator('#session-select'), form = page.locator('#session-editor'), pane = page.locator('#requirement-editor');
  const ready = id => page.waitForFunction(id => document.querySelector('#session-select').value === id && !document.querySelector('#session-select').disabled, id);
  const saved = () => page.waitForFunction(() => document.querySelector('#status').textContent === '');
  async function createFrom(template, name) {
    await page.getByRole('button', { name: 'New session', exact: true }).click();
    await form.getByLabel('Start from').selectOption(template);
    await form.getByLabel('Session name').fill(name);
    await form.getByRole('button', { name: 'Create session', exact: true }).click();
    await form.waitFor({ state: 'hidden' });
    const id = new URL(page.url()).searchParams.get('session');
    await ready(id);
    return id;
  }
  assert.equal(await select.inputValue(), 'current');
  const blankId = await createFrom('blank', 'Blank study');
  assert.equal(await page.getByRole('tab').count(), 2);
  assert.equal(await page.locator('.statements tbody tr').count(), 1);
  assert.equal(await page.locator('.stakeholders tbody tr').count(), 1);
  await page.locator('.statements .add-row').click();
  await pane.locator('#requirement-text').fill('The bus shall have mass $$mass$$.');
  await pane.locator('[data-parameter="mass"]').fill('2');
  await pane.locator('[data-parameter-unit="mass"]').fill('kg');
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await saved();
  assert.equal((await get(blankId)).workspace.statements[0].parameters.mass, '2');
  const genericId = await createFrom('generic-eps', 'Generic EPS baseline');
  assert.equal(await page.getByRole('tab', { name: 'EPS', exact: true }).getAttribute('aria-selected'), 'true');
  assert.equal((await get(genericId)).workspace.statements.length, 27);
  await page.getByRole('tab', { name: 'Mission', exact: true }).click();
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  await pane.locator('[data-parameter="altitude_km"]').fill('600');
  await pane.locator('#requirement-rationale').fill('Mission-specific orbit rationale.');
  await page.getByRole('button', { name: 'Save as…', exact: true }).click();
  await form.getByLabel('Session name').fill('Mission copy');
  await form.getByRole('button', { name: 'Save copy', exact: true }).click();
  await form.waitFor({ state: 'hidden' });
  const copyId = new URL(page.url()).searchParams.get('session');
  await ready(copyId);
  const orbit = workspace => workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  assert.equal(orbit((await get(copyId)).workspace).parameters.altitude_km, '600');
  assert.equal(orbit((await get(copyId)).workspace).rationale, 'Mission-specific orbit rationale.');
  assert.equal(orbit((await get(genericId)).workspace).parameters.altitude_km, null);
  assert.deepEqual((await get()).workspace, initial.workspace);
  assert.equal(await readFile(modelPath, 'utf8'), original);
  await page.reload(); await page.locator('main:not([inert])').waitFor();
  assert.equal(await select.inputValue(), copyId);
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  assert.equal(await pane.locator('[data-parameter="altitude_km"]').inputValue(), '600');
  await pane.locator('[data-parameter="altitude_km"]').fill('800');
  let releaseSave, markSaving;
  const gate = new Promise(resolve => { releaseSave = resolve; });
  const saving = new Promise(resolve => { markSaving = resolve; });
  const routeURL = `**/api/workspace?session=${copyId}`;
  await page.route(routeURL, async route => {
    if (route.request().method() === 'PUT') { markSaving(); await gate; }
    await route.continue();
  });
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await saving;
  await select.selectOption(genericId);
  assert.equal(await select.isDisabled(), true);
  releaseSave();
  await ready(genericId);
  await page.unroute(routeURL);
  assert.equal(orbit((await get(copyId)).workspace).parameters.altitude_km, '800');
  assert.equal(orbit((await get(genericId)).workspace).parameters.altitude_km, null);
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  await pane.locator('[data-parameter="altitude_km"]').fill('999');
  page.once('dialog', dialog => dialog.dismiss());
  await select.selectOption(blankId);
  assert.equal(await select.inputValue(), genericId);
  assert.equal(await pane.locator('[data-parameter="altitude_km"]').inputValue(), '999');
  assert.equal(new URL(page.url()).searchParams.get('session'), genericId);
  page.once('dialog', dialog => dialog.accept());
  await select.selectOption(blankId); await ready(blankId);
  assert.equal((await get(blankId)).workspace.statements[0].parameters.mass, '2');
  await page.goBack(); await ready(genericId);
  assert.equal(orbit((await get(genericId)).workspace).parameters.altitude_km, null);
  await page.locator('[data-requirement-edit="generic-ORB-OrbitPeriod"]').click();
  await pane.locator('#requirement-text').fill('Invalid $$bad-name$$.');
  await page.getByRole('button', { name: 'Save as…', exact: true }).click();
  await form.getByLabel('Session name').fill('Invalid copy');
  await form.getByRole('button', { name: 'Save copy', exact: true }).click();
  assert.match(await form.locator('#session-error').textContent(), /Correct the requirement editor errors/);
  assert.equal(await pane.isVisible(), true);
  assert.equal((await (await page.request.get(base + '/api/sessions')).json()).sessions.length, 4);
  await form.getByRole('button', { name: 'Close session form', exact: true }).click();
  await page.keyboard.press('Escape');
  await page.getByRole('button', { name: 'New session', exact: true }).click();
  await form.getByLabel('Session name').fill('Blank study');
  await form.getByRole('button', { name: 'Create session', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#session-error').textContent.includes('already exists'));
  assert.equal(await select.inputValue(), genericId);
  await form.getByRole('button', { name: 'Close session form', exact: true }).click();
  await select.selectOption(copyId); await ready(copyId);
  const otherPage = await browser.newPage();
  await otherPage.goto(`${base}/?session=${genericId}#mission`);
  await otherPage.locator('main:not([inert])').waitFor();
  assert.equal(await otherPage.locator('#session-select').inputValue(), genericId);
  assert.equal(await select.inputValue(), copyId);
  await otherPage.close();
  const [download] = await Promise.all([page.waitForEvent('download'), page.locator('.export-json').click()]);
  assert.equal(download.suggestedFilename(), 'Mission_copy-export.json');
  const exported = join(directory, 'copy-export.json');
  await download.saveAs(exported);
  assert.deepEqual(JSON.parse(await readFile(exported, 'utf8')), (await get(copyId)).workspace);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.getByRole('button', { name: 'New session', exact: true }).isVisible(), true);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  assert.deepEqual(errors, []);
});
