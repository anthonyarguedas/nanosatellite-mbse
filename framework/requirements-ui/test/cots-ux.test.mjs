import assert from 'node:assert/strict';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { blankWorkspace } from '../model.mjs';
import { createServer } from '../server.mjs';

const product = 'ablic_s_8252aag_m6t1u';
function fixture() {
  const workspace = blankWorkspace();
  workspace.variables = [{ name: 'voltage_V', type: 'float', unit: 'V' }];
  workspace.elements = [
    { key: 'bus', id: 'BUS', name: 'Bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' },
    { key: 'eps', id: 'EPS', name: 'Power', owner: 'bus', definition: 'SpaceSegment::CubeSat::PowerSubsystem' },
  ];
  workspace.statements = ['EPS001', 'EPS002'].map(id => ({ key: id.toLowerCase(), id, context: 'eps', kind: 'Requirement',
    text: 'The input shall support $$voltage_V$$.', rationale: '', condition: 'voltage_V > 0', sources: [], affected: [], parameters: { voltage_V: '8' } }));
  workspace.components = [{ key: 'protector', id: 'CMP001', owner: 'eps', product, requirements: ['eps001', 'eps002'] }];
  return workspace;
}
async function browserFixture(t) {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await mkdtemp(join(tmpdir(), 'cots-ux-')), modelPath = join(directory, 'mission.json');
  await writeFile(modelPath, JSON.stringify(fixture(), null, 2) + '\n');
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => { await browser.close(); await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }); await rm(directory, { recursive: true, force: true }); });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 } });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  await page.goto(base + '/#eps');
  const req = page.locator('#requirement-editor'), cots = page.locator('#cots-editor');
  const saved = () => page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const read = async (id = '') => (await (await page.request.get(`${base}/api/workspace${id ? `?session=${id}` : ''}`)).json()).workspace;
  const openCots = async () => { await page.locator('[data-cots-edit="protector"]').click(); await cots.locator('[data-cots-fact]').first().waitFor(); };
  const useFact = async name => {
    await cots.getByRole('searchbox', { name: 'Search COTS facts', exact: true }).fill(name);
    await cots.getByRole('table', { name: 'COTS catalogue facts', exact: true }).getByRole('button', { name: 'Use fact', exact: true }).click();
  };
  const check = state => page.waitForFunction(state => document.querySelector('#requirement-check').dataset.state === state, state);
  return { page, req, cots, read, saved, openCots, useFact, check, errors };
}

test('COTS pane centralizes facts, preserves requirement drafts and shares named references across requirements', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { page, req, cots, read, saved, openCots, useFact, check, errors } = await browserFixture(t);
  await openCots();
  assert.equal(await req.isVisible(), false);
  assert.equal(await cots.getByRole('table', { name: 'COTS catalogue facts', exact: true }).locator('input,textarea,select').count(), 0);
  await useFact('input_voltage_max');
  await useFact('autonomous_overcurrent_protection');
  assert.equal((await read()).components[0].facts, undefined);
  await cots.getByRole('button', { name: 'Save COTS', exact: true }).click(); await cots.waitFor({ state: 'hidden' }); await saved();
  let state = await read(); assert.equal(state.components[0].facts.length, 2);
  assert.ok(state.components[0].facts.every(binding => !Object.hasOwn(binding, 'value')));
  await page.locator('[data-requirement-edit="eps001"]').click();
  assert.equal(await req.getByRole('table', { name: 'COTS catalogue facts', exact: true }).count(), 0);
  await req.getByLabel('Values for verification method 1', { exact: true }).selectOption('cots:protector');
  await req.getByLabel('Verification condition', { exact: true }).fill('CMP001.input_voltage_max >= voltage_V and CMP001.autonomous_overcurrent_protection');
  await req.getByLabel('Rationale', { exact: true }).fill('Unsaved requirement draft.');
  await check('pass');
  await req.getByRole('button', { name: 'CMP001.input_voltage_max', exact: true }).click();
  await cots.locator('[data-cots-fact]').first().waitFor();
  assert.equal(await req.isVisible(), false);
  const named = cots.getByRole('table', { name: 'COTS fact references', exact: true });
  const voltage = named.locator('[data-cots-binding]').filter({ has: page.getByLabel('Reference name input_voltage_max', { exact: true }) });
  assert.equal(await voltage.getByRole('button', { name: 'EPS001', exact: true }).count(), 1);
  await cots.getByLabel('Reference name input_voltage_max', { exact: true }).fill('supported_max_V');
  await cots.getByRole('button', { name: 'Save COTS', exact: true }).click(); await cots.waitFor({ state: 'hidden' }); await saved();
  assert.equal(await req.isVisible(), true);
  assert.match(await req.getByLabel('Verification condition', { exact: true }).inputValue(), /CMP001.supported_max_V/);
  assert.equal(await req.getByLabel('Rationale', { exact: true }).inputValue(), 'Unsaved requirement draft.');
  state = await read(); assert.equal(state.statements[0].rationale, ''); assert.equal(state.statements[0].verifications, undefined);
  await req.getByRole('button', { name: 'Save requirement', exact: true }).click(); await req.waitFor({ state: 'hidden' }); await saved();
  await page.locator('[data-requirement-edit="eps002"]').click();
  await req.getByLabel('Values for verification method 1', { exact: true }).selectOption('cots:protector');
  await req.getByLabel('Verification condition', { exact: true }).fill('CMP001.supported_max_V >= voltage_V'); await check('pass');
  await req.getByRole('button', { name: 'Save requirement', exact: true }).click(); await req.waitFor({ state: 'hidden' }); await saved();
  await openCots();
  const shared = named.locator('[data-cots-binding]').filter({ has: page.getByLabel('Reference name supported_max_V', { exact: true }) });
  assert.deepEqual(await shared.locator('[data-cots-requirement]').allTextContents(), ['EPS001', 'EPS002']);
  await shared.getByRole('button', { name: 'Remove', exact: true }).click();
  assert.match(await cots.locator('[data-cots-error]').textContent(), /Remove expression references/);
  await cots.getByRole('button', { name: 'Cancel', exact: true }).click();
  await page.locator('[data-table="components"] [data-field="id"]').first().fill('COT099'); await saved();
  assert.match((await read()).statements[0].verifications[0].condition, /COT099.supported_max_V/);
  assert.match((await read()).statements[1].verifications[0].condition, /COT099.supported_max_V/);
  await openCots();
  assert.equal(await cots.getByRole('heading', { name: 'COTS COT099', exact: true }).count(), 1);
  await page.locator('[data-table="components"] [data-field="product"]').first().selectOption('adi_ltc4359ims8_pbf'); await saved();
  await page.waitForFunction(() => document.querySelector('tr[data-key="eps001"] .checkbox-cell').dataset.state === 'pending');
  await cots.locator('.cots-reference-status').first().filter({ hasText: 'Record unavailable' }).waitFor();
  assert.equal(await named.locator('[data-cots-binding] .cell-text').filter({ hasText: /^Pending$/ }).count(), 2);
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  assert.deepEqual(errors, []);
});

test('switching between COTS and requirement panes preserves both drafts and Save as includes both', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { page, req, cots, read, openCots, useFact, errors } = await browserFixture(t);
  await page.locator('[data-requirement-edit="eps001"]').click();
  await req.getByLabel('Rationale', { exact: true }).fill('Local requirement draft.');
  await openCots(); await useFact('input_voltage_max');
  await cots.getByLabel('Reference name input_voltage_max', { exact: true }).fill('maximum_V');
  await cots.getByRole('button', { name: 'Back to EPS001', exact: true }).click();
  assert.equal(await req.getByLabel('Rationale', { exact: true }).inputValue(), 'Local requirement draft.');
  await req.getByRole('button', { name: 'Back to CMP001', exact: true }).click();
  await cots.getByLabel('Reference name maximum_V', { exact: true }).waitFor();
  await page.getByRole('button', { name: 'Save as…', exact: true }).click();
  const form = page.locator('#session-editor');
  await form.getByLabel('Session name', { exact: true }).fill('COTS draft copy');
  await form.getByRole('button', { name: 'Save copy', exact: true }).click(); await form.waitFor({ state: 'hidden' });
  const id = new URL(page.url()).searchParams.get('session'); assert.ok(id);
  const original = await read(), copy = await read(id);
  assert.equal(original.components[0].facts, undefined); assert.equal(original.statements[0].rationale, '');
  assert.equal(copy.components[0].facts[0].name, 'maximum_V'); assert.equal(copy.statements[0].rationale, 'Local requirement draft.');
  await page.reload(); await openCots();
  assert.equal(await cots.getByLabel('Reference name maximum_V', { exact: true }).inputValue(), 'maximum_V');
  assert.deepEqual(errors, []);
});

test('Insert reference commits the COTS selection and keeps the requirement value as an unsaved expression', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { page, req, cots, read, saved, openCots, useFact, check, errors } = await browserFixture(t);
  await page.locator('[data-requirement-edit="eps001"]').click();
  await req.getByLabel('Expression for voltage_V', { exact: true }).fill('');
  await page.locator('[data-table="components"] [data-field="product"]').first().press('F2');
  await cots.locator('[data-cots-fact]').first().waitFor(); await useFact('input_voltage_max');
  await cots.getByRole('button', { name: 'Insert reference', exact: true }).click(); await cots.waitFor({ state: 'hidden' });
  assert.equal(await req.getByLabel('Expression for voltage_V', { exact: true }).inputValue(), 'CMP001.input_voltage_max');
  await check('pass'); await saved();
  assert.equal((await read()).statements[0].parameters.voltage_V, '8');
  assert.equal((await read()).components[0].facts[0].name, 'input_voltage_max');
  await req.getByRole('button', { name: 'Save requirement', exact: true }).click(); await req.waitFor({ state: 'hidden' }); await saved();
  assert.equal((await read()).statements[0].parameters.voltage_V, 'CMP001.input_voltage_max');
  await page.reload();
  await page.locator('[data-requirement-edit="eps001"]').click(); await check('pass');
  assert.equal(await req.getByRole('button', { name: 'CMP001.input_voltage_max', exact: true }).count(), 1);
  assert.deepEqual(errors, []);
});
