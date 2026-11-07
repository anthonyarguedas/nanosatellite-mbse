import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { createEvaluationWorker, evaluationRequest } from '../evaluation-worker.mjs';
import { expressionReferences, modeReferences, rewriteReferences } from '../expression-metadata.mjs';
import { addPowerLimits, blankWorkspace, emptyWorkspace, renamePowerMode, removePowerMode, rewriteRowReferences, validateWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { parameterStates, stateExpression } from '../parameter-states.mjs';
import { isPowerRequirement, powerFor, spacecraftComponents } from '../power.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { createServer } from '../server.mjs';
import { serializeWorkspace as renderManaged } from './helpers.mjs';
import { evaluateChecks } from './helpers.mjs';
import { scriptContext, scriptInstance } from '../verification-methods.mjs';

const pythonAvailable = !spawnSync('python3', ['--version']).error;
function fixture() {
  return { ...blankWorkspace(), variables: [{ name: 'x', type: 'float' }, { name: 'y', type: 'float' }, { name: 'count', type: 'integer' }], statements: [
    { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'The quantity shall exceed $$x$$.', sources: [], affected: [], condition: 'x > 0', parameters: { x: '3', y: null, count: '4' } },
    { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: '', sources: [], affected: [], condition: '', parameters: { x: '4', y: null, count: null } },
  ] };
}
function workerFor(t, options) { const worker = createEvaluationWorker(options); t.after(() => worker.close()); return worker; }
async function directoryFor(t) { const dir = await mkdtemp(join(tmpdir(), 'python-evaluator-test-')); t.after(() => rm(dir, { recursive: true, force: true })); return dir; }
const first = async (worker, workspace, options) => (await worker.evaluate(workspace, options)).results[0];

test('one persistent interpreter evaluates native Python and isolates all request values and caches', { skip: !pythonAvailable }, async t => {
  const worker = workerFor(t), workspace = fixture();
  const start = await worker.request({ operation: 'ping' });
  const examples = [
    ['math.sqrt(9) + statistics.mean([1, 2, 3])', 5],
    ['sum(i ** 2 for i in range(5))', 30],
    ['sum(x ** 2 for x in range(5))', 30],
    ['statistics.median([7, 1, 4])', 4],
    ['sum([i for i in range(10) if i % 2 == 0])', 20],
    ['11 // 2 + 11 % 2', 6],
    ['round(math.pi, 2)', 3.14],
    ['REQ002.x * 2', 8],
  ];
  for (const [source, value] of examples) {
    workspace.statements[0].parameters.x = source;
    assert.equal((await first(worker, workspace)).values.x, value, source);
  }
  workspace.statements[0].condition = '0 < x < 20 and all(i >= 0 for i in range(3)) and math.isclose(math.sqrt(2) ** 2, 2, rel_tol=1e-12) and any(True if i == 0 else 1 / 0 == 0 for i in range(2))';
  assert.equal((await first(worker, workspace)).state, 'pass');
  workspace.variables.push({ name: '_margin', type: 'float' });
  for (const row of workspace.statements) row.parameters._margin = '1';
  workspace.statements[0].parameters.x = 'REQ002.x + _margin';
  assert.equal((await first(worker, workspace)).values.x, 5);
  workspace.statements[0].parameters.x = null;
  const pending = await first(worker, workspace);
  assert.equal(pending.values.x, null); assert.equal(pending.state, 'pending');
  workspace.statements[0].parameters.x = '2';
  assert.equal((await first(worker, workspace)).values.x, 2);
  assert.equal((await worker.request({ operation: 'ping' })).pid, start.pid);
  await assert.rejects(() => worker.request({ operation: 'missing' }), /Unknown Python worker operation/);
  assert.equal((await worker.request({ operation: 'ping' })).pid, start.pid);
});

test('native Python preserves typed Integer and Boolean rules, pending branches, dependency errors and mode aggregation', { skip: !pythonAvailable }, async t => {
  const worker = workerFor(t), workspace = fixture(), row = workspace.statements[0];
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'science', name: 'Science', sunlight: 0, eclipse: 0 }];
  row.parameters.x = '18 if mode == "Science" else 3';
  row.parameters.y = 'REQ002.x * x';
  row.condition = 'y <= 72';
  let result = await first(worker, workspace);
  assert.equal(result.state, 'pass');
  assert.deepEqual(result.modes.map(mode => mode.values.y), [12, 72]);
  assert.deepEqual(result.parameters.x.branches, { values: { nominal: '3', science: '18' }, lastEdited: 'science' });
  row.parameters.x = 'None if mode == "Science" else 3';
  result = await first(worker, workspace); assert.equal(result.state, 'pending');
  assert.equal(result.modes[0].values.y, 12);
  row.parameters.x = 'True'; assert.equal((await first(worker, workspace)).parameters.x.state, 'error');
  row.parameters.x = '2'; row.parameters.count = 'x / 2'; row.parameters.y = 'sum(range(count))';
  assert.equal((await first(worker, workspace)).values.y, 0);
  row.parameters.count = 'x / 3'; assert.equal((await first(worker, workspace)).parameters.count.state, 'error');
  row.parameters.count = '2'; row.parameters.x = 'y'; row.parameters.y = 'x';
  assert.match((await first(worker, workspace)).parameters.x.message, /Cyclic parameter expression/);
  row.parameters.x = '1 if True else unknown'; assert.equal((await first(worker, workspace)).parameters.x.state, 'error');
  row.parameters.x = '1 if mode == "Missing" else 2'; assert.match((await first(worker, workspace)).parameters.x.message, /Unknown spacecraft mode/);
});

test('automatic Python evaluation rejects arbitrary code, unbounded collections and nonfinite arithmetic', { skip: !pythonAvailable }, async t => {
  const worker = workerFor(t), workspace = fixture(), row = workspace.statements[0], directory = await directoryFor(t);
  const marker = join(directory, 'executed.txt');
  const sources = [
    `__import__('pathlib').Path(${JSON.stringify(marker)}).write_text('bad')`,
    'open("/etc/passwd").read()', 'eval("1 + 1")', 'exec("x = 2")',
    'REQ001.__class__', '(1).__class__.__base__.__subclasses__()', '(lambda: 2)()', '(x := 2)',
    'globals()', 'getattr(REQ001, "x")', '{"x": 1}', '[1] * 1000000000', '"a" * 1000000000',
    'sum(range(1000000000))', '10 ** (10 ** 308)', '1e999', '1 / 0', 'math.sqrt(-1)',
    'sum(i for i in range(1024) for j in range(1024))', 'sum(math for math in range(2))', '1 # use rationale instead',
  ];
  for (const source of sources) {
    row.parameters.x = source;
    assert.equal((await first(worker, workspace)).parameters.x.state, 'error', source);
  }
  row.parameters.x = '('.repeat(80) + '1' + ')'.repeat(80);
  // Python discards grouping parentheses. A deeply nested AST still stays bounded.
  row.parameters.x = '-'.repeat(100) + '1';
  assert.equal((await first(worker, workspace)).parameters.x.state, 'error');
  await assert.rejects(() => readFile(marker), /ENOENT/);
  row.parameters.x = 'sum(i for i in range(10))';
  assert.equal((await first(worker, workspace)).values.x, 45);
});

test('Python retains sizing, component draws, allocations and weighted power budgets', { skip: !pythonAvailable }, async t => {
  const worker = workerFor(t), catalog = await loadCatalog(), workspace = emptyWorkspace(catalog);
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 75, eclipse: 100 }, { key: 'downlink', name: 'Downlink', sunlight: 25, eclipse: 0 }];
  for (const element of spacecraftComponents(workspace)) {
    const load = structuredClone(powerFor(workspace, element));
    if (load.accounting !== 'counted') continue;
    load.states = [{ key: 'active', name: 'Active', watts: 1, basis: 'estimated', source: 'Test', conditions: '' }];
    load.assignments = { nominal: 'active', downlink: 'active' }; workspace.power.loads.push(load);
  }
  addPowerLimits(workspace);
  for (const row of workspace.statements.filter(isPowerRequirement)) row.parameters.power_limit_W = '100 if mode == "Downlink" else 50';
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod'); orbit.parameters.altitude_km = '500';
  const expected = evaluateChecks(workspace), actual = (await worker.evaluate(workspace)).results;
  for (let index = 0; index < expected.length; index++) {
    assert.equal(actual[index].state, expected[index].state, workspace.statements[index].id);
    for (const name of Object.keys(expected[index].parameters)) {
      const before = expected[index].parameters[name], after = actual[index].parameters[name];
      assert.equal(after.state, before.state, `${workspace.statements[index].id}.${name}`);
      if (before.value !== null) assert.ok(Math.abs(after.value - before.value) < Math.max(1e-10, Math.abs(before.value) * 1e-12));
    }
  }
});

test('script input expressions and script output references use the same Python interpreter and discard stale evidence', { skip: !pythonAvailable }, async t => {
  const worker = workerFor(t), workspace = fixture(), definition = (await loadScriptCatalog()).find(definition => definition.id === 'normal_interval');
  const script = scriptInstance(definition, { key: 'analysis', id: 'SCR001' });
  Object.assign(script.parameters, { mean: 'statistics.mean([REQ001.x, REQ002.x])', standard_deviation: '1', confidence: '0.95' });
  workspace.scripts.push(script);
  workspace.statements[0].condition = 'SCR001.upper < 6';
  assert.equal((await first(worker, workspace)).state, 'pending');
  const evidence = await runScripts(workspace, script.key, { evaluator: worker });
  assert.equal(evidence.runs['analysis:'].state, 'value');
  const result = await worker.evaluate(workspace, { scriptResults: evidence });
  assert.equal(result.results[0].state, 'pass');
  assert.equal(result.scripts[0].values.mean, 3.5);
  workspace.statements[1].parameters.x = '40';
  assert.equal((await first(worker, workspace, { scriptResults: evidence })).state, 'pending');
});

test('worker supervision restarts after a crash, timeout, cancellation and invalid output, and bounds its queue', { skip: !pythonAvailable }, async t => {
  const directory = await directoryFor(t), path = join(directory, 'protocol.py');
  await writeFile(path, `import json, os, sys, time
for line in sys.stdin:
    request = json.loads(line)
    operation = request.get("operation")
    if operation == "hang": time.sleep(10)
    if operation == "crash": os._exit(1)
    if operation == "bad":
        print("not JSON", flush=True)
        continue
    if operation == "large":
        print("x" * 10000, flush=True)
        continue
    print(json.dumps({"id": request["id"], "result": {"pid": os.getpid()}}), flush=True)
`);
  const worker = workerFor(t, { path, timeoutMs: 1000, maxResponseBytes: 1000, maxQueue: 2 });
  let pid = (await worker.request({ operation: 'ping' })).pid;
  for (const [operation, pattern] of [['hang', /timed out/], ['crash', /exited unexpectedly/], ['bad', /invalid JSON/], ['large', /size limit/]]) {
    await assert.rejects(() => worker.request({ operation }, { timeout: 100 }), pattern);
    const replacement = await worker.request({ operation: 'ping' }); assert.notEqual(replacement.pid, pid); pid = replacement.pid;
  }
  const controller = new AbortController(), active = worker.request({ operation: 'hang' }, { signal: controller.signal });
  const firstQueued = worker.request({ operation: 'ping' }), secondQueued = worker.request({ operation: 'ping' });
  await assert.rejects(() => worker.request({ operation: 'ping' }), /queue is full/);
  controller.abort(); await assert.rejects(() => active, /cancelled/);
  assert.equal((await firstQueued).pid, (await secondQueued).pid);
  worker.close(); await assert.rejects(() => worker.request({ operation: 'ping' }), /closed/);
});

test('missing Python is actionable and never falls back to JavaScript calculation', async t => {
  const worker = workerFor(t, { python: '/missing/requirements-python' });
  await assert.rejects(() => worker.evaluate(fixture()), /Could not start Python evaluation.*VERIFICATION_PYTHON/);
});

test('older workspace versions require explicit rejection, with no legacy adapter', () => {
  const old = fixture(); old.version = 12;
  assert.throws(() => validateWorkspace(old), /differs from app format/);
});

test('Python editor metadata preserves quoted text during reference and mode renames', () => {
  const source = `REQ001.x + (1 if mode == 'Science "A"' else 2) + len('REQ001.x')`;
  assert.deepEqual(expressionReferences(source).map(reference => reference.id), ['REQ001']);
  assert.equal(rewriteReferences(source, new Map([['REQ001', 'NEW001']])), `NEW001.x + (1 if mode == 'Science "A"' else 2) + len('REQ001.x')`);
  assert.equal(modeReferences(source)[0].value, 'Science "A"');
  const workspace = fixture(); workspace.power.modes = [{ key: 'science', name: 'Science "A"', sunlight: 100, eclipse: 100 }];
  workspace.statements[0].parameters.x = `18 if mode == 'Science "A"' else 3`;
  renamePowerMode(workspace, 'science', 'Science B');
  assert.match(workspace.statements[0].parameters.x, /"Science B"/);
  assert.throws(() => removePowerMode(workspace, 'science'), /expression references/);
  rewriteRowReferences(workspace, new Map([['REQ002', 'NEW002']]));
  const states = { values: { science: '1 +', nominal: null }, lastEdited: 'science' };
  const modes = [...workspace.power.modes, { key: 'nominal', name: 'Nominal' }];
  const encoded = stateExpression(states, modes, 'python');
  assert.deepEqual(parameterStates(encoded, modes), states);
});

test('browser authors Python expressions, state branches and script inputs through the persistent worker', { skip: !process.env.PLAYWRIGHT_MODULE || !pythonAvailable }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE);
  const directory = await directoryFor(t), modelPath = join(directory, 'mission.json'), workspace = fixture();
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'science', name: 'Science', sunlight: 0, eclipse: 0 }];
  await writeFile(modelPath, renderManaged(workspace));
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => { await browser.close(); await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }); });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 }, acceptDownloads: true });
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  const base = `http://127.0.0.1:${server.address().port}`, pane = page.locator('#requirement-editor');
  const check = state => page.waitForFunction(state => document.querySelector('#requirement-check').dataset.state === state, state);
  await page.goto(base); await page.locator('[data-requirement-edit="r1"]').click();
  await pane.locator('#requirement-text').fill('The quantities shall exceed $$x$$ and $$y$$.');
  const expression = 'sum(i ** 2 for i in range(4))';
  await pane.getByLabel('Expression for x', { exact: true }).fill(expression);
  await pane.getByLabel('Expression for y', { exact: true }).fill('REQ002.x * 2');
  await pane.getByLabel('Verification condition', { exact: true }).fill('0 < x < 20 and math.isclose(y, 8)');
  await check('pass');
  await pane.getByLabel('State for x', { exact: true }).selectOption('science');
  await pane.getByLabel('Expression for x in Science', { exact: true }).fill('18');
  await check('pass');
  await pane.getByRole('button', { name: 'Add script', exact: true }).click();
  await pane.getByLabel('Python script definition', { exact: true }).selectOption('normal_interval');
  await pane.getByLabel('SCR001 mean expression', { exact: true }).fill('statistics.mean([REQ001.x, REQ002.x])');
  await pane.getByLabel('SCR001 standard_deviation expression', { exact: true }).fill('2');
  await pane.getByLabel('SCR001 confidence expression', { exact: true }).fill('0.95');
  const scriptKey = await pane.locator('[data-script-key]').getAttribute('data-script-key');
  await pane.getByLabel('Values for verification method 2', { exact: true }).selectOption(scriptKey);
  await pane.getByLabel('Verification condition 2', { exact: true }).fill('SCR001.upper >= 10');
  await check('pending');
  await pane.getByRole('table', { name: 'Verification methods', exact: true }).getByRole('button', { name: 'Run SCR001', exact: true }).click();
  await check('pass');
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#status').textContent === '');
  await page.waitForFunction(() => document.querySelector('tr[data-key="r1"] .verification-result').checked);
  await page.getByRole('button', { name: 'Requirements table actions', exact: true }).click();
  const [download] = await Promise.all([page.waitForEvent('download'), page.getByRole('button', { name: 'Export workspace JSON', exact: true }).click()]);
  const exported = join(directory, 'snapshot.json'); await download.saveAs(exported);
  const data = JSON.parse(await readFile(exported, 'utf8'));
  assert.equal(parameterStates(data.statements[0].parameters.x, data.power.modes).values.nominal, expression);
  assert.equal(data.scripts[0].parameters.mean, 'statistics.mean([REQ001.x, REQ002.x])');
  await page.reload(); await page.locator('[data-requirement-edit="r1"]').click(); await check('pending');
  assert.equal(await pane.getByLabel('Expression for x in Nominal', { exact: true }).inputValue(), expression);
  assert.deepEqual(errors, []);
});

test('evaluation and JSON download APIs preserve Python source and leave storage unchanged during calculation', { skip: !pythonAvailable }, async t => {
  const directory = await directoryFor(t), modelPath = join(directory, 'mission.json'), workspace = fixture();
  workspace.statements[0].parameters.x = 'statistics.mean([2, 4, 6])'; workspace.statements[0].condition = '0 < x < 5';
  const source = renderManaged(workspace); await writeFile(modelPath, source);
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
  const base = `http://127.0.0.1:${server.address().port}`;
  const post = (path, body, headers = {}) => fetch(base + path, { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body) });
  const response = await post('/api/evaluate', { workspace }); assert.equal(response.status, 200);
  const result = await response.json(); assert.equal(result.engine, 'python'); assert.equal(result.results[0].values.x, 4); assert.equal(result.results[0].state, 'pass');
  assert.equal(await readFile(modelPath, 'utf8'), source);
  assert.equal((await fetch(base + '/api/evaluate')).status, 405);
  assert.equal((await post('/api/evaluate', { workspace }, { Origin: 'https://example.com' })).status, 403);
  assert.equal((await fetch(base + '/api/evaluate', { method: 'POST', body: '{}' })).status, 415);
  assert.equal((await post('/api/evaluate', { workspace: {} })).status, 400);
  const exported = await post('/api/json', { workspace }); assert.equal(exported.status, 200); assert.deepEqual(await exported.json(), { ...workspace, expressionLanguage: 'python', resourceBudgets: true });
  assert.equal((await post('/api/sysml', { workspace })).status, 404);
  const state = await (await fetch(base + '/api/workspace')).json();
  assert.equal((await post('/api/workspace', { workspace, revision: state.revision })).status, 405);
  const saved = await fetch(base + '/api/workspace', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace, revision: state.revision }) });
  assert.equal(saved.status, 200);
  assert.deepEqual(JSON.parse(await readFile(modelPath, 'utf8')), { ...workspace, resourceBudgets: true });
});
