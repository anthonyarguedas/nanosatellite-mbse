import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { blankWorkspace } from '../model.mjs';
import { loadScriptCatalog } from '../python.mjs';
import { createServer } from '../server.mjs';
import { serializeWorkspace as renderManaged } from './helpers.mjs';
import { scriptInstance, verificationMethods } from '../verification-methods.mjs';

function fixture() {
  const workspace = blankWorkspace();
  workspace.variables = [{ name: 'x', type: 'float' }, { name: 'limit', type: 'float' }];
  workspace.statements = [
    { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'The quantity shall exceed $$x$$.', sources: [], affected: [],
      condition: 'x > 0', parameters: { x: '8 if mode == "Downlink" else 3', limit: null } },
    { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: 'The quantity shall stay below $$limit$$.', sources: [], affected: [],
      condition: 'limit > 0', parameters: { x: null, limit: '12' } },
  ];
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'downlink', name: 'Downlink', sunlight: 0, eclipse: 0 }];
  return workspace;
}
async function browserFixture(t, workspace = fixture(), options = {}) {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await mkdtemp(join(tmpdir(), 'verification-ux-')), modelPath = join(directory, 'mission.json');
  await writeFile(modelPath, renderManaged(workspace));
  const server = createServer({ modelPath, ...options });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => {
    await browser.close(); await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    await rm(directory, { recursive: true, force: true });
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 }, acceptDownloads: true });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  const read = async (session = '') => (await (await page.request.get(`${base}/api/workspace${session ? `?session=${session}` : ''}`)).json()).workspace;
  const saved = () => page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const check = state => page.waitForFunction(state => document.querySelector('#requirement-check').dataset.state === state, state);
  const pane = page.locator('#requirement-editor'), open = () => page.locator('[data-requirement-edit="r1"]').click();
  await page.goto(base); await open();
  return { page, pane, base, server, modelPath, read, saved, check, open, errors };
}

test('verification UX adds methods and reusable scripts without expanding the workbook, and retains configuration across sessions', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { page, pane, base, server, modelPath, read, saved, check, open, errors } = await browserFixture(t);
  let executions = 0; server.on('request', request => { if (request.url === '/api/scripts/run') executions++; });
  const methods = pane.getByRole('table', { name: 'Verification methods', exact: true });
  const library = pane.locator('[data-script-library]');
  assert.equal(await library.evaluate(element => element.tagName), 'SECTION');
  assert.equal(await pane.locator('summary, #requirement-preview-mode').count(), 0);
  assert.equal(await methods.locator('tbody tr').count(), 2);
  assert.equal(await pane.locator('#requirement-text-help').textContent(), 'Enclose a variable name in $$, such as $$var$$, to add its parameter row. Enter units in the Units column, using ** for powers.');
  assert.equal(await pane.locator('#requirement-text-help + p').textContent(), 'Expressions use Python. Choose a State to define one expression per mode. All states merges the rows using the last edited expression.');
  for (const section of [pane.locator('.editor-sheet').first(), methods.locator('xpath=../..'), library]) {
    assert.equal(await section.locator(':scope > .table-top').count(), 1);
    assert.equal(await section.locator(':scope > .table-frame').count(), 1);
    assert.equal(await section.locator(':scope > .table-top').evaluate(element => getComputedStyle(element).backgroundColor), 'rgb(56, 98, 84)');
  }
  await pane.getByRole('button', { name: 'Add verification method', exact: true }).click();
  assert.equal(await methods.getByLabel('Verification condition 2', { exact: true }).evaluate(element => element === document.activeElement), true);
  await methods.getByLabel('Verification condition 2', { exact: true }).fill('x < 10');
  await check('pass');
  const scripts = pane.getByRole('table', { name: 'Python scripts', exact: true });
  await pane.getByRole('button', { name: 'Add script', exact: true }).click();
  assert.equal(await pane.getByLabel('Python script definition', { exact: true }).evaluate(element => element === document.activeElement), true);
  await pane.getByLabel('Python script definition', { exact: true }).selectOption('normal_interval');
  const script = scripts.locator('[data-script-key]');
  const parameters = pane.locator('[data-script-parameters]');
  assert.equal(await scripts.locator('tbody tr').count(), 2);
  assert.equal(await scripts.locator('tbody tr').last().locator('.row-delete').isDisabled(), true);
  assert.deepEqual(await parameters.locator('tbody th').allTextContents(), ['mean', 'standard_deviation', 'confidence', 'SCR001.lower', 'SCR001.upper']);
  assert.deepEqual(await parameters.locator('tbody td:nth-child(2)').allTextContents(), ['Input', 'Input', 'Input', 'Output', 'Output']);
  assert.deepEqual(await parameters.locator('tbody td:nth-child(3)').allTextContents(), ['float', 'float', 'float', 'float', 'float']);
  assert.equal(await parameters.isVisible(), true);
  assert.equal(await library.locator('p:visible').count(), 0);
  await parameters.getByLabel('SCR001 mean expression', { exact: true }).fill('REQ001.x');
  await parameters.getByLabel('SCR001 standard_deviation expression', { exact: true }).fill('2');
  await parameters.getByLabel('SCR001 confidence expression', { exact: true }).fill('0.95');
  const key = await script.getAttribute('data-script-key');
  await methods.getByLabel('Values for verification method 3', { exact: true }).selectOption(key);
  await methods.getByLabel('Verification condition 3', { exact: true }).fill('SCR001.upper <= REQ002.limit');
  await check('pending'); assert.equal(executions, 0);
  assert.equal((await read()).scripts.length, 0);
  await methods.getByRole('button', { name: 'Run SCR001', exact: true }).click();
  await check('pass'); assert.equal(executions, 1);
  assert.equal(await parameters.locator('[data-script-output="upper"]').textContent(), 'By mode');
  assert.equal(await script.locator('[data-script-status]').textContent(), 'Completed');
  assert.match(await script.locator('[data-script-status]').getAttribute('title'), /Nominal: Python execution completed.*Downlink: Python execution completed/s);
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  const persisted = await read();
  assert.equal(persisted.scripts.length, 1);
  assert.equal(verificationMethods(persisted.statements[0]).length, 3);
  assert.equal(persisted.scriptResults, undefined);
  await page.waitForFunction(() => document.querySelector('tr[data-key="r1"] .verification-result').checked);
  await open(); await check('pass');
  await script.locator('[data-script-field="id"]').fill('CAL001');
  await script.locator('[data-script-field="id"]').press('Tab');
  assert.equal(await methods.getByLabel('Verification condition 3', { exact: true }).inputValue(), 'CAL001.upper <= REQ002.limit');
  await check('pending');
  await methods.getByRole('button', { name: 'Run CAL001', exact: true }).click(); await check('pass');
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  await open();
  await parameters.getByLabel('CAL001 mean expression', { exact: true }).fill('REQ001.x * 2');
  await check('pending');
  await methods.getByRole('button', { name: 'Run CAL001', exact: true }).click(); await check('fail');
  assert.match(await pane.locator('#requirement-mode-results').textContent(), /Nominal: TRUE.*Downlink: FALSE/);
  assert.equal(await pane.getByLabel('Preview mode', { exact: true }).count(), 0);
  assert.equal(await methods.locator('[data-method-key]').nth(2).locator('.verification-method-result').textContent(), 'FALSE');
  const exported = await page.request.post(base + '/api/json', { data: { workspace: await read() } });
  assert.equal(exported.ok(), true); assert.equal((await exported.json()).scripts[0].definition, 'normal_interval');
  await page.getByRole('button', { name: 'Save as…', exact: true }).click();
  const sessionForm = page.locator('#session-editor');
  await sessionForm.getByLabel('Session name', { exact: true }).fill('Python verification study');
  await sessionForm.getByRole('button', { name: 'Save copy', exact: true }).click(); await sessionForm.waitFor({ state: 'hidden' });
  const session = new URL(page.url()).searchParams.get('session'); assert.ok(session && session !== 'current');
  assert.equal((await read(session)).scripts[0].parameters.mean, 'REQ001.x * 2');
  assert.equal((await read()).scripts[0].parameters.mean, 'REQ001.x');
  await page.reload(); await open(); await check('pending');
  assert.equal(await methods.getByLabel('Verification condition 3', { exact: true }).inputValue(), 'CAL001.upper <= REQ002.limit');
  await script.getByRole('button', { name: 'Delete CAL001', exact: true }).click();
  assert.match(await pane.locator('#requirement-error').textContent(), /Remove expression and verification references/);
  assert.equal(await pane.locator('[data-script-key]').count(), 1);
  await methods.getByRole('button', { name: 'Delete verification method 3', exact: true }).click();
  await script.getByRole('button', { name: 'Delete CAL001', exact: true }).click();
  assert.equal(await pane.locator('[data-script-key]').count(), 0);
  await pane.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.equal((await read(session)).scripts.length, 1);
  assert.equal(verificationMethods((await read(session)).statements[0]).length, 3);
  await open(); await methods.getByLabel('Verification condition 2', { exact: true }).fill('x < 1');
  await check('fail');
  await pane.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.equal(verificationMethods((await read(session)).statements[0])[1].condition, 'x < 10');
  await page.setViewportSize({ width: 390, height: 844 }); await open();
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  const stored = JSON.parse(await readFile(modelPath, 'utf8'));
  assert.equal(stored.scripts[0].definition, 'normal_interval');
  assert.deepEqual(errors, []);
});

test('verification UX rejects late Python results after input edits and updates pinned definitions explicitly', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const directory = await mkdtemp(join(tmpdir(), 'verification-ux-scripts-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const metadata = { id: 'delayed', name: 'Delayed calculation', description: 'Test analysis',
    inputs: [{ name: 'input', type: 'float' }], outputs: [{ name: 'value', type: 'float' }], timeoutMs: 3000 };
  await writeFile(join(directory, 'delayed.json'), JSON.stringify(metadata));
  await writeFile(join(directory, 'delayed.py'), 'import json, sys, time\ndata = json.load(sys.stdin)\ntime.sleep(0.7)\njson.dump({"value": data["inputs"]["input"]}, sys.stdout)\n');
  const workspace = fixture(); workspace.power.modes = []; workspace.statements[0].parameters.x = '1';
  const script = scriptInstance((await loadScriptCatalog(directory))[0], { key: 'delayed', id: 'SCR001' });
  script.parameters.input = 'REQ001.x'; workspace.scripts.push(script);
  workspace.statements[0].condition = '';
  workspace.statements[0].verifications = [{ key: 'calculation', script: script.key, condition: 'SCR001.value == x' }];
  const { page, pane, check, errors } = await browserFixture(t, workspace, { scriptDirectory: directory });
  const methods = pane.getByRole('table', { name: 'Verification methods', exact: true });
  const run = methods.getByRole('button', { name: 'Run SCR001', exact: true });
  const requested = page.waitForRequest(request => request.url().endsWith('/api/scripts/run'));
  await run.click(); await requested;
  await pane.getByLabel('Expression for x', { exact: true }).fill('2');
  await page.waitForFunction(() => document.querySelector('[data-script-message]').textContent.includes('inputs changed'));
  await check('pending');
  await run.click(); await check('pass');
  assert.equal(await pane.getByLabel('SCR001 input expression', { exact: true }).isVisible(), true);
  await writeFile(join(directory, 'delayed.py'), 'import json, sys\ndata = json.load(sys.stdin)\njson.dump({"value": 2 * data["inputs"]["input"]}, sys.stdout)\n');
  await run.click(); await check('error');
  assert.match(await pane.locator('#requirement-check').textContent(), /registered script changed/);
  await pane.getByRole('button', { name: 'Update definition', exact: true }).click();
  await check('pending'); await run.click(); await check('fail');
  assert.deepEqual(errors, []);
});
