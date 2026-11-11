import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, readdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { blankWorkspace, mergeRequirementDraft, nextId, removePowerMode, renamePowerMode,
  rewriteRowReferences, validateWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { createServer } from '../server.mjs';
import { canonicalWorkspace } from '../storage.mjs';
import { createEvaluationWorker } from '../evaluation-worker.mjs';
import { readWorkspace, validateCalculations as renderExport, serializeWorkspace as renderManaged } from './helpers.mjs';
import { createEvaluator, evaluateChecks } from './helpers.mjs';
import { runKey, scriptContext, scriptInstance, setVerificationMethods, verificationMethods } from '../verification-methods.mjs';

const hasPython = !spawnSync('python3', ['--version']).error;
const definitions = await loadScriptCatalog();
function fixture() {
  const workspace = { ...blankWorkspace(), variables: [{ name: 'x', type: 'float' }, { name: 'limit', type: 'float' }],
    statements: [
      { key: 'r1', id: 'REQ001', context: 'external', kind: 'Requirement', text: 'The value shall exceed $$x$$.', sources: [], affected: [],
        condition: 'x > 0', parameters: { x: '8 if mode == "Downlink" else 3', limit: null } },
      { key: 'r2', id: 'REQ002', context: 'external', kind: 'Requirement', text: 'The value shall stay below $$limit$$.', sources: [], affected: [],
        condition: 'limit > 0', parameters: { x: null, limit: '12' } },
    ] };
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'downlink', name: 'Downlink', sunlight: 0, eclipse: 0 }];
  const script = scriptInstance(definitions.find(definition => definition.id === 'normal_interval'), { key: 'analysis', id: 'SCR001' });
  Object.assign(script.parameters, { mean: 'REQ001.x', standard_deviation: '2', confidence: '0.95' });
  workspace.scripts.push(script);
  setVerificationMethods(workspace.statements[0], [
    { key: 'positive', condition: 'x > 0' }, { key: 'interval', script: script.key, condition: 'SCR001.upper <= REQ002.limit' },
  ]);
  return workspace;
}
async function temporary(t) {
  const directory = await mkdtemp(join(tmpdir(), 'verification-methods-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  return directory;
}
async function customScript(directory, id, source, { inputs = [{ name: 'input', type: 'float' }], outputs = [{ name: 'value', type: 'float' }], timeoutMs = 3000 } = {}) {
  await writeFile(join(directory, `${id}.json`), JSON.stringify({ id, name: id, description: 'Test analysis', inputs, outputs, timeoutMs }));
  await writeFile(join(directory, `${id}.py`), source);
  const definition = (await loadScriptCatalog(directory)).find(definition => definition.id === id);
  return scriptInstance(definition, { key: id, id: `SCR${String((await readdir(directory)).filter(file => file.endsWith('.json')).length).padStart(3, '0')}` });
}
const double = 'import json, sys\ndata = json.load(sys.stdin)\njson.dump({"value": data["inputs"]["input"] * 2}, sys.stdout)\n';

function rawEvidence(workspace, values = { lower: 0, upper: 10 }) {
  return { signature: scriptContext(workspace), runs: Object.fromEntries(workspace.power.modes.map(mode =>
    [runKey('analysis', mode.key), { revision: workspace.scripts[0].revision, state: 'value', values }])) };
}

test('verification tables require every configured method in every mode', () => {
  const workspace = fixture(), row = workspace.statements[0];
  assert.equal(row.condition, '');
  assert.equal(verificationMethods(row).length, 2);
  assert.equal(evaluateChecks(workspace)[0].state, 'pending');
  let scriptResults = rawEvidence(workspace);
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pass');
  scriptResults.runs['analysis:downlink'].values = { lower: 0, upper: 13 };
  const failed = evaluateChecks(workspace, { scriptResults })[0];
  assert.equal(failed.state, 'fail');
  assert.deepEqual(failed.methods.map(method => method.state), ['pass', 'fail']);
  assert.deepEqual(failed.modes.map(mode => mode.state), ['pass', 'fail']);
  row.verifications.push({ key: 'unfinished', condition: '' });
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'fail');
  row.verifications[1].condition = 'SCR001.upper < 100';
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pending');
  row.verifications[2].condition = 'true and 1';
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'error');
  setVerificationMethods(row, [{ key: 'remaining', condition: 'x > 1' }]);
  assert.equal(row.verifications, undefined);
  assert.equal(row.condition, 'x > 1');
  assert.equal(evaluateChecks(workspace)[0].state, 'pass');
  setVerificationMethods(row, []);
  assert.equal(evaluateChecks(workspace)[0].state, 'unset');
});

test('script references have their own parameter names and types, and pending values never become zero', () => {
  const workspace = fixture(), row = workspace.statements[0], script = workspace.scripts[0];
  script.outputs.push({ name: 'valid', type: 'boolean' }, { name: 'count', type: 'integer' });
  row.verifications[1].condition = 'SCR001.valid and SCR001.count == 2';
  const scriptResults = rawEvidence(workspace, { lower: null, upper: 10, valid: true, count: 2 });
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pass');
  row.parameters.limit = 'SCR001.upper * 2';
  scriptResults.signature = scriptContext(workspace);
  assert.equal(createEvaluator(workspace, { mode: 'nominal', scriptResults }).parameter(row, 'limit'), 20);
  row.verifications[1].condition = 'SCR001.lower == 0';
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pending');
  row.verifications[1].condition = 'true or SCR001.unknown > 0';
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'error');
  row.verifications[1].condition = 'SCR001.valid + 1 > 0';
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'error');
  row.verifications[1].condition = 'SCR001.count > 0';
  scriptResults.runs['analysis:nominal'].values.count = 1.5;
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'error');
});

test('execution evidence is invalidated by inputs, modes and script definitions, and excludes prose and table placeholders', () => {
  const original = fixture(), scriptResults = rawEvidence(original);
  for (const mutate of [
    state => { state.statements[1].parameters.limit = '15'; },
    state => { state.scripts[0].parameters.confidence = '0.90'; },
    state => { state.scripts[0].revision = '0'.repeat(64); },
    state => { state.power.modes[0].sunlight = 90; },
  ]) {
    const workspace = structuredClone(original); mutate(workspace);
    assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pending');
  }
  const workspace = structuredClone(original);
  workspace.statements[0].text = 'Edited prose.';
  workspace.statements[0].verifications[0].condition = 'x > 1';
  workspace.statements.push({ key: 'empty', id: '', parameters: {} });
  assert.equal(scriptContext(workspace), scriptResults.signature);
  workspace.statements[0].parameters = { limit: null, x: workspace.statements[0].parameters.x };
  assert.equal(scriptContext(workspace), scriptResults.signature);
});

test('script instances, methods and expressions validate, merge and rewrite without losing references', () => {
  const original = fixture();
  assert.doesNotThrow(() => validateWorkspace(original));
  assert.equal(nextId(original, 'Script'), 'SCR002');
  const edited = structuredClone(original), current = structuredClone(original);
  edited.scripts[0].parameters.mean = 'REQ001.x * 2';
  edited.statements[0].verifications[0].condition = 'x > 1';
  current.statements[1].parameters.limit = '14';
  const merged = validateWorkspace(mergeRequirementDraft(current, original, edited, 'r1'));
  assert.equal(merged.statements[1].parameters.limit, '14');
  assert.equal(merged.scripts[0].parameters.mean, 'REQ001.x * 2');
  current.scripts[0].parameters.mean = '99';
  assert.throws(() => mergeRequirementDraft(current, original, edited, 'r1'), /changed while you were editing/);
  rewriteRowReferences(merged, new Map([['REQ001', 'NEW001'], ['SCR001', 'CAL001']]));
  merged.statements[0].id = 'NEW001'; merged.scripts[0].id = 'CAL001';
  assert.equal(merged.scripts[0].parameters.mean, 'NEW001.x * 2');
  assert.match(merged.statements[0].verifications[1].condition, /CAL001.upper/);
  merged.statements[0].verifications[0].condition = 'mode == "Downlink" or x > 0';
  merged.scripts[0].parameters.mean = '2 if mode == "Downlink" else NEW001.x';
  renamePowerMode(merged, 'downlink', 'Science');
  assert.match(merged.scripts[0].parameters.mean, /Science/);
  assert.match(merged.statements[0].verifications[0].condition, /Science/);
  assert.throws(() => removePowerMode(merged, 'downlink'), /expression references/);
});

test('schema rejects duplicate namespaces, manual results, conflicting condition formats and malformed script interfaces', () => {
  for (const mutate of [
    state => { state.scripts[0].id = 'REQ001'; },
    state => { state.scripts[0].key = 'r1'; },
    state => { state.scripts[0].definition = '../escape'; },
    state => { state.scripts[0].results = { upper: 2 }; },
    state => { state.scriptResults = { signature: 'manual', runs: {} }; },
    state => { state.scripts[0].outputs[0].name = 'execution_succeeded'; },
    state => { state.scripts[0].outputs[0].name = 'mean'; },
    state => { state.scripts[0].parameters.extra = '1'; },
    state => { state.statements[0].condition = 'true'; },
    state => { state.statements[0].verifications[0].verified = true; },
    state => { state.statements[0].verifications[1].script = 'missing'; },
    state => { state.statements[0].verifications.push({ ...state.statements[0].verifications[0] }); },
  ]) {
    const workspace = fixture(); mutate(workspace);
    assert.throws(() => validateWorkspace(workspace));
  }
});

test('JSON retains independent conditions, script interfaces and bindings without cached execution results', () => {
  const workspace = fixture();
  workspace.scripts[0].outputs.push({ name: 'valid', type: 'boolean' });
  workspace.statements[0].verifications[1].condition = 'SCR001.valid and SCR001.upper <= REQ002.limit';
  const source = renderExport(workspace);
  const snapshot = JSON.parse(source);
  assert.equal(snapshot.scripts[0].parameters.mean, 'REQ001.x');
  assert.equal(snapshot.scripts[0].outputs.find(output => output.name === 'valid').type, 'boolean');
  assert.equal(snapshot.statements[0].verifications.length, 2);
  assert.equal(snapshot.statements[0].verifications[1].script, 'analysis');
  assert.equal(snapshot.scripts[0].values, undefined);
  assert.equal(evaluateChecks(snapshot)[0].state, 'pending');
  assert.deepEqual(readWorkspace(renderManaged(workspace)), workspace);
});

test('Python receives evaluated requirement inputs per mode and returns reusable outputs without changing workspace data', { skip: !hasPython }, async () => {
  const workspace = fixture(), original = structuredClone(workspace);
  const scriptResults = await runScripts(workspace, 'analysis');
  assert.deepEqual(workspace, original);
  assert.deepEqual(Object.values(scriptResults.runs).map(run => run.state), ['value', 'value']);
  assert.ok(Math.abs(scriptResults.runs['analysis:nominal'].values.upper - 6.919927969080108) < 1e-10);
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pass');
  workspace.statements[1].parameters.limit = '10';
  assert.equal(evaluateChecks(workspace, { scriptResults })[0].state, 'pending');
  const rerun = await runScripts(workspace, 'analysis');
  assert.equal(evaluateChecks(workspace, { scriptResults: rerun })[0].state, 'fail');
});

test('script dependencies resolve through other scripts and requirement parameters, while cycles and unset inputs remain blocked', { skip: !hasPython }, async t => {
  const directory = await temporary(t), workspace = fixture();
  const first = await customScript(directory, 'first', double);
  const second = await customScript(directory, 'second', double);
  first.parameters.input = 'REQ001.x'; second.parameters.input = `${first.id}.value + 1`;
  workspace.scripts = [first, second]; workspace.statements[0].condition = ''; delete workspace.statements[0].verifications;
  let evidence = await runScripts(workspace, second.key, { directory });
  assert.equal(evidence.runs['first:nominal'].values.value, 6);
  assert.equal(evidence.runs['second:nominal'].values.value, 14);
  second.parameters.input = 'REQ002.x'; workspace.statements[1].parameters.x = `${first.id}.value + 2`;
  evidence = await runScripts(workspace, second.key, { directory });
  assert.equal(evidence.runs['second:nominal'].values.value, 16);
  first.parameters.input = `${second.id}.value`;
  evidence = await runScripts(workspace, second.key, { directory });
  assert.equal(evidence.runs['second:nominal'].state, 'error');
  assert.match(evidence.runs['second:nominal'].message, /Cyclic Python dependency/);
  first.parameters.input = null;
  evidence = await runScripts(workspace, first.key, { directory });
  assert.equal(evidence.runs['first:nominal'].state, 'pending');
  assert.equal(evidence.runs['first:nominal'].executedAt, undefined);
});

test('Python execution bounds time and output, validates result types and JSON, and pins registered source revisions', { skip: !hasPython }, async t => {
  const directory = await temporary(t), workspace = fixture();
  const examples = [
    ['timeout', 'import time\ntime.sleep(10)', /timed out/, { timeoutMs: 50 }],
    ['large', 'print("x" * 1100000)', /exceeded 1 MiB/],
    ['malformed', 'print("not JSON")', /one JSON object/],
    ['wrong_type', 'print(\'{"value": true}\')', /finite float/],
    ['nonfinite', 'print(\'{"value": 1e999}\')', /finite float/],
    ['extra', 'print(\'{"value": 1, "extra": 2}\')', /exactly the declared/],
    ['failed', 'raise ValueError("test failure")', /test failure/],
  ];
  workspace.power.modes = [];
  for (const [id, source, error, options] of examples) {
    const script = await customScript(directory, id, source, options); script.parameters.input = '2'; workspace.scripts = [script];
    const result = (await runScripts(workspace, script.key, { directory })).runs[`${script.key}:`];
    assert.equal(result.state, 'error', id); assert.match(result.message, error, id);
  }
  const script = await customScript(directory, 'pinned', double); script.parameters.input = '2'; workspace.scripts = [script];
  await writeFile(join(directory, 'pinned.py'), 'print(\'{"value": 99}\')');
  const result = (await runScripts(workspace, script.key, { directory })).runs['pinned:'];
  assert.equal(result.state, 'error'); assert.match(result.message, /registered script changed/);
  const cancelled = new AbortController(); cancelled.abort();
  const abortResult = (await runScripts(workspace, script.key, { directory, signal: cancelled.signal })).runs['pinned:'];
  assert.match(abortResult.message, /cancelled/);
});

test('Python supports typed Boolean and Integer inputs and outputs alongside the evaluated requirement snapshot', { skip: !hasPython }, async t => {
  const directory = await temporary(t), workspace = fixture(); workspace.power.modes = [];
  const script = await customScript(directory, 'typed', 'import json, sys\ndata = json.load(sys.stdin)\np = data["inputs"]\njson.dump({"accepted": p["enabled"] and p["threshold"] == data["requirements"]["REQ002"]["limit"], "rounded": p["count"] + 1}, sys.stdout)\n', {
    inputs: [{ name: 'threshold', type: 'float' }, { name: 'count', type: 'integer' }, { name: 'enabled', type: 'boolean' }],
    outputs: [{ name: 'accepted', type: 'boolean' }, { name: 'rounded', type: 'integer' }],
  });
  workspace.scripts = [script];
  Object.assign(script.parameters, { threshold: 'REQ002.limit', count: '2', enabled: 'True' });
  setVerificationMethods(workspace.statements[0], [{ key: 'typed', script: script.key, condition: `${script.id}.accepted and ${script.id}.rounded == 3` }]);
  const evidence = await runScripts(workspace, script.key, { directory });
  assert.deepEqual(evidence.runs['typed:'].values, { accepted: true, rounded: 3 });
  assert.equal(evaluateChecks(workspace, { scriptResults: evidence })[0].state, 'pass');
  script.parameters.enabled = '1';
  const invalid = await runScripts(workspace, script.key, { directory });
  assert.equal(invalid.runs['typed:'].state, 'error'); assert.match(invalid.runs['typed:'].message, /boolean/);
});

test('Python cancellation terminates an active process and the API bounds simultaneous runs', { skip: !hasPython }, async t => {
  const directory = await temporary(t), workspace = fixture(); workspace.power.modes = [];
  const script = await customScript(directory, 'slow', 'import time\ntime.sleep(10)\nprint(\'{"value": 1}\')', { timeoutMs: 10000 });
  script.parameters.input = '1'; workspace.scripts = [script];
  setVerificationMethods(workspace.statements[0], []);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 100);
  const evidence = await runScripts(workspace, script.key, { directory, signal: controller.signal }); clearTimeout(timer);
  assert.match(evidence.runs['slow:'].message, /cancelled/);
  await writeFile(join(directory, 'slow.py'), 'import time\ntime.sleep(0.5)\nprint(\'{"value": 1}\')');
  const definition = (await loadScriptCatalog(directory))[0]; script.revision = definition.revision;
  const modelPath = join(directory, 'mission.json'); await writeFile(modelPath, renderManaged(workspace));
  const server = createServer({ modelPath, scriptDirectory: directory }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
  const base = `http://127.0.0.1:${server.address().port}`;
  const post = signal => fetch(base + '/api/scripts/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, signal,
    body: JSON.stringify({ workspace, script: script.key }) });
  const cancelled = new AbortController();
  const first = post(cancelled.signal).catch(error => error), second = post();
  await new Promise(resolve => setTimeout(resolve, 100));
  const rejected = await post(); assert.equal(rejected.status, 429);
  cancelled.abort(); assert.equal((await first).name, 'AbortError');
  const completed = await second; assert.equal(completed.status, 200);
  assert.equal((await completed.json()).runs['slow:'].state, 'value');
});

test('registered script loading rejects directory escapes and exposes metadata without source code', async t => {
  const directory = await temporary(t), root = join(directory, 'registered');
  const { mkdir } = await import('node:fs/promises'); await mkdir(root);
  await customScript(root, 'trusted', double);
  const catalog = await loadScriptCatalog(root);
  assert.equal(catalog[0].source, undefined); assert.match(catalog[0].revision, /^[a-f0-9]{64}$/);
  await writeFile(join(directory, 'outside.py'), double);
  await rm(join(root, 'trusted.py')); await symlink(join(directory, 'outside.py'), join(root, 'trusted.py'));
  await assert.rejects(() => loadScriptCatalog(root), /inside the configured/);
});

test('the API runs only registered scripts on explicit POST, keeps results transient, and round trips multiple methods', { skip: !hasPython }, async t => {
  const directory = await temporary(t), modelPath = join(directory, 'mission.json'), workspace = fixture();
  const source = renderManaged(workspace); await writeFile(modelPath, source);
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
  const base = `http://127.0.0.1:${server.address().port}`;
  const request = (data, headers = {}) => fetch(base + '/api/scripts/run', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(data) });
  assert.equal((await fetch(base + '/api/scripts/run')).status, 405);
  assert.equal((await fetch(base + '/scripts/normal_interval.py')).status, 404);
  const library = await (await fetch(base + '/api/scripts')).json(); assert.ok(library.scripts.length);
  assert.equal(library.scripts[0].source, undefined);
  const response = await request({ workspace, script: 'analysis' }); assert.equal(response.status, 200);
  const evidence = await response.json(); assert.equal(evaluateChecks(workspace, { scriptResults: evidence })[0].state, 'pass');
  assert.equal(await readFile(modelPath, 'utf8'), source);
  assert.equal((await request({ workspace, script: '../../escape' })).status, 400);
  assert.equal((await request({ workspace, script: 'analysis' }, { Origin: 'https://example.com' })).status, 403);
  assert.equal((await fetch(base + '/api/scripts/run', { method: 'POST', body: '{}' })).status, 415);
  const get = await (await fetch(base + '/api/workspace')).json();
  workspace.statements[0].verifications[0].condition = 'x >= 2';
  const saved = await fetch(base + '/api/workspace', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace, revision: get.revision }) });
  assert.equal(saved.status, 200);
  const restored = (await (await fetch(base + '/api/workspace')).json()).workspace;
  assert.deepEqual(restored, (await canonicalWorkspace(workspace)).workspace);
  const evaluator = createEvaluationWorker(); t.after(() => evaluator.close());
  assert.equal((await evaluator.evaluate(restored)).results[0].state, 'pending');
  assert.equal(restored.scriptResults, undefined);
});
