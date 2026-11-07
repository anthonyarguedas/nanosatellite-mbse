import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { emptyWorkspace, parameterExpression, removePowerMode, renamePowerMode, validateWorkspace } from '../model.mjs';
import { mergedStateExpression, parameterStates, splitParameterStates, stateExpression } from '../parameter-states.mjs';
import { createServer } from '../server.mjs';
import { readWorkspace, validateCalculations as renderExport, serializeWorkspace as renderManaged } from './helpers.mjs';
import { evaluateChecks } from './helpers.mjs';

const modes = [
  { key: 'nominal', name: 'Nominal', sunlight: 70, eclipse: 100 },
  { key: 'downlink', name: 'Downlink', sunlight: 30, eclipse: 0 },
  { key: 'science', name: 'Science "A"', sunlight: 0, eclipse: 0 },
];
function fixture() {
  return {
    ...emptyWorkspace(),
    variables: [{ name: 'x', type: 'float', unit: 'W' }, { name: 'y', type: 'integer' }],
    power: { modes: structuredClone(modes), loads: [], links: [] },
    statements: [
      { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'The draw shall be at least $$x$$.',
        sources: [], affected: [], condition: 'x >= 5', parameters: { x: '2 * 3', y: '2' } },
      { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: 'The input shall equal $$x$$.',
        sources: [], affected: [], condition: 'x == 4', parameters: { x: '4', y: null } },
    ],
  };
}

test('splitting copies a shared expression to every global state and retains one native parameter', () => {
  const workspace = fixture(), row = workspace.statements[0];
  const states = splitParameterStates(row.parameters.x, modes, 'downlink');
  assert.deepEqual(states.values, { nominal: '2 * 3', downlink: '2 * 3', science: '2 * 3' });
  const source = stateExpression(states, modes);
  assert.deepEqual(parameterStates(source, modes), states);
  assert.match(source, /if mode == "Downlink" else/);
  row.parameters.x = source;
  assert.doesNotThrow(() => validateWorkspace(workspace));
  assert.deepEqual(evaluateChecks(workspace)[0].modes.map(mode => mode.values.x), [6, 6, 6]);
  const exported = renderExport(workspace);
  assert.equal(JSON.parse(exported).statements.length, 2);
  assert.equal(JSON.parse(exported).statements[0].parameters.x, source);
  assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
  assert.throws(() => splitParameterStates('1', modes, 'missing'), /existing spacecraft state/);
});

test('last edited expressions survive encoding and merge from any row, including an empty expression', () => {
  const states = { values: { nominal: '  2 * (3 + 4)  ', downlink: '(REQ002.x + 1)', science: null }, lastEdited: 'downlink' };
  const restored = parameterStates(stateExpression(states, modes), modes);
  assert.deepEqual(restored, states);
  for (const mode of modes) assert.equal(mergedStateExpression(restored, mode.key), '(REQ002.x + 1)');
  restored.lastEdited = 'science';
  const empty = parameterStates(stateExpression(restored, modes), modes);
  assert.equal(mergedStateExpression(empty, 'nominal'), null);
  assert.equal(parameterStates('12', modes), null);
  assert.equal(parameterStates(null, modes), null);
  assert.equal(parameterStates('1 if True else 2', modes), null);
  assert.deepEqual(splitParameterStates(null, modes, 'nominal').values, { nominal: null, downlink: null, science: null });
});

test('existing conditional expressions expose their branch text without evaluating or simplifying arithmetic', () => {
  for (const [source, expected] of [
    ['REQ002.x * 2 if mode == "Downlink" else 2 * 3', { nominal: '2 * 3', downlink: 'REQ002.x * 2', science: '2 * 3' }],
    ['(x) + (2) if "Nominal" != mode else (4 if y > 0 else 5)',
      { nominal: '4 if y > 0 else 5', downlink: '(x) + (2)', science: '(x) + (2)' }],
    ['None if mode == "Nominal" else min(4, y) if mode == "Downlink" else -2 ** 3',
      { nominal: null, downlink: 'min(4, y)', science: '-2 ** 3' }],
  ]) {
    const workspace = fixture(); workspace.statements[0].parameters.x = source;
    assert.deepEqual(evaluateChecks(workspace)[0].parameters.x.branches.values, expected, source);
  }
  const source = '2 * (3 if mode == "Downlink" else 4)';
  assert.equal(parameterStates(source, modes), null);
  assert.deepEqual(Object.values(splitParameterStates(source, modes, 'nominal').values), [source, source, source]);
});

test('state expressions retain reference rewrites, mode guards, pending branches and Integer checks', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.parameters.x = stateExpression({ values: { nominal: 'REQ002.x * 2', downlink: '5', science: null }, lastEdited: 'nominal' }, modes);
  const checks = evaluateChecks(workspace)[0];
  assert.deepEqual(checks.modes.map(mode => mode.parameters.x.state), ['value', 'value', 'pending']);
  assert.deepEqual(checks.modes.map(mode => mode.values.x), [8, 5, null]);
  assert.equal(checks.state, 'pending');
  renamePowerMode(workspace, 'science', 'Science B');
  assert.deepEqual(parameterStates(row.parameters.x, workspace.power.modes).values, { nominal: 'REQ002.x * 2', downlink: '5', science: null });
  assert.throws(() => removePowerMode(workspace, 'science'), /expression references/);
  row.parameters.y = stateExpression({ values: { nominal: '2', downlink: '2.5', science: '3' }, lastEdited: 'downlink' }, workspace.power.modes);
  assert.equal(evaluateChecks(workspace)[0].parameters.y.state, 'error');
  assert.throws(() => renderExport(workspace), /safe integer/);
  const added = [...workspace.power.modes, { key: 'safe', name: 'Safe', sunlight: 0, eclipse: 0 }];
  assert.equal(parameterStates(row.parameters.x, added).values.safe, null);
});

test('invalid state drafts round trip as data and combined length stays bounded', () => {
  const workspace = fixture(), row = workspace.statements[0];
  const states = { values: { nominal: '1 +', downlink: '4', science: '2 if True else None' }, lastEdited: 'nominal' };
  row.parameters.x = stateExpression(states, modes);
  assert.deepEqual(parameterStates(row.parameters.x, modes), states);
  assert.equal(evaluateChecks(workspace)[0].parameters.x.state, 'error');
  assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
  assert.throws(() => renderExport(workspace), /REQ001.x/);
  states.values.nominal = '1 + '.repeat(1250) + '1';
  assert.throws(() => parameterExpression(stateExpression(states, modes), { name: 'x' }), /5,000/);
});

test('generated state branches evaluate in Python, including quoted modes and pending Integer values', () => {
  const workspace = fixture(), row = workspace.statements[0];
  row.parameters.x = stateExpression({ values: { nominal: '2 * 3', downlink: 'REQ002.x * 2', science: '9' }, lastEdited: 'science' }, modes);
  row.parameters.y = stateExpression({ values: { nominal: '2', downlink: null, science: '3' }, lastEdited: 'downlink' }, modes);
  const snapshot = JSON.parse(renderExport(workspace));
  const result = evaluateChecks(snapshot)[0];
  assert.deepEqual(result.modes.map(mode => mode.values.x), [6, 8, 9]);
  assert.deepEqual(result.modes.map(mode => mode.values.y), [2, null, 3]);
  assert.equal(result.parameters.y.state, 'pending');
});

test('browser splits, evaluates, pastes, persists and merges state rows using the last edited expression', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await mkdtemp(join(tmpdir(), 'parameter-states-browser-')), modelPath = join(directory, 'mission.json');
  await writeFile(modelPath, renderManaged(fixture()));
  const server = createServer({ modelPath });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => {
    await browser.close();
    await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    await rm(directory, { recursive: true, force: true });
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 } });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`;
  const read = async (session = '') => (await (await page.request.get(`${base}/api/workspace${session ? `?session=${session}` : ''}`)).json()).workspace;
  const saved = () => page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const editor = page.locator('#requirement-editor');
  const open = () => page.locator('[data-requirement-edit="r1"]').click();
  const inputs = () => editor.locator('[data-parameter="x"]');
  const expression = mode => editor.locator(`[data-parameter="x"][data-mode="${mode}"]`);
  const state = mode => editor.locator(`[data-parameter-state="x"][data-mode="${mode}"]`);
  const result = mode => editor.locator(`[data-parameter-row="x"][data-mode="${mode}"] .parameter-result`);
  await page.goto(base); await open();
  assert.equal(await state('').inputValue(), '');
  assert.deepEqual(await state('').locator('option').allTextContents(), ['All states', 'Nominal', 'Downlink', 'Science "A"']);
  await state('').selectOption('science');
  assert.equal(await inputs().count(), 3);
  assert.deepEqual(await inputs().allTextContents(), ['2 * 3', '2 * 3', '2 * 3']);
  assert.equal(await state('nominal').inputValue(), 'nominal');
  await expression('nominal').fill('REQ002.x * 2');
  await expression('science').fill('9 + 1');
  await expression('downlink').fill('3 * 3');
  await page.waitForFunction(() => document.querySelector('[data-parameter-row="x"][data-mode="downlink"] .parameter-result').textContent === '9.000 W');
  assert.equal(await result('nominal').textContent(), '8.000 W');
  assert.equal(await result('science').textContent(), '10.00 W');
  assert.equal(await editor.getByLabel('Preview mode', { exact: true }).count(), 0);
  assert.equal(await result('downlink').textContent(), '9.000 W');
  await editor.locator('[data-parameter-unit="x"][data-mode="science"]').fill('mW');
  assert.deepEqual(await editor.locator('[data-parameter-unit="x"]').evaluateAll(inputs => inputs.map(input => input.value)), ['mW', 'mW', 'mW']);
  await editor.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  const persisted = await read(), source = persisted.statements[0].parameters.x;
  assert.equal(persisted.statements.filter(row => row.context === 'external').length, 2);
  assert.equal(parameterStates(source, persisted.power.modes).lastEdited, 'downlink');
  assert.equal(JSON.parse(await readFile(join(directory, 'mission.json'), 'utf8')).statements[0].parameters.x, source);
  assert.match(source, /if mode == "Downlink" else/);
  const exportResponse = await page.request.post(base + '/api/json', { data: { workspace: persisted } });
  assert.equal(exportResponse.ok(), true);
  assert.deepEqual(await exportResponse.json(), persisted);
  await page.reload(); await open();
  assert.equal(await expression('downlink').inputValue(), '3 * 3');
  await state('science').selectOption('');
  assert.equal(await inputs().count(), 1);
  assert.equal(await expression('').inputValue(), '3 * 3');
  await editor.getByRole('button', { name: 'Cancel', exact: true }).click();
  assert.equal((await read()).statements[0].parameters.x, source);
  await open();
  await expression('nominal').evaluate(input => {
    const clipboardData = new DataTransfer(); clipboardData.setData('text/plain', '6\n7\n8');
    input.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData }));
  });
  assert.deepEqual(await inputs().evaluateAll(inputs => inputs.map(input => input.value)), ['6', '7', '8']);
  await expression('downlink').fill('');
  await state('nominal').selectOption('');
  assert.equal(await expression('').inputValue(), '');
  await state('').selectOption('nominal');
  assert.deepEqual(await inputs().evaluateAll(inputs => inputs.map(input => input.value)), ['', '', '']);
  await expression('nominal').fill('1 +');
  await page.waitForFunction(() => document.querySelector('[data-parameter="x"][data-mode="nominal"]').getAttribute('aria-invalid') === 'true');
  await editor.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  await page.reload(); await open();
  assert.equal(await expression('nominal').inputValue(), '1 +');
  await expression('science').fill('REQ002.x * 2');
  await state('downlink').selectOption('');
  assert.equal(await expression('').inputValue(), 'REQ002.x * 2');
  await editor.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  assert.equal((await read()).statements[0].parameters.x, 'REQ002.x * 2');
  await open(); await state('').selectOption('downlink');
  await expression('nominal').fill('12');
  await page.getByRole('button', { name: 'Save as…', exact: true }).click();
  const form = page.locator('#session-editor');
  await form.getByLabel('Session name').fill('State expressions copy');
  await form.getByRole('button', { name: 'Save copy', exact: true }).click();
  await form.waitFor({ state: 'hidden' });
  const session = new URL(page.url()).searchParams.get('session');
  assert.ok(session && session !== 'current');
  const copy = await read(session);
  assert.equal(parameterStates(copy.statements[0].parameters.x, copy.power.modes).values.nominal, '12');
  assert.equal((await read()).statements[0].parameters.x, 'REQ002.x * 2');
  assert.deepEqual(errors, []);
});
