import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, copyFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { loadCotsFacts, loadProducts } from '../cots.mjs';
import { cotsBinding, cotsBindingState, cotsRenames, cotsUses, mergeCotsDraft, rewriteCotsReferences } from '../cots-bindings.mjs';
import { emptyWorkspace, mergeRequirementDraft, rewriteRowReferences, validateWorkspace } from '../model.mjs';
import { createEvaluationWorker } from '../evaluation-worker.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { createSessions } from '../sessions.mjs';
import { scriptContext, scriptInstance, setVerificationMethods } from '../verification-methods.mjs';
import { evaluateChecks } from './helpers.mjs';
import { createServer } from '../server.mjs';

const product = 'ablic_s_8252aag_m6t1u';
const { facts } = await loadCotsFacts(product);
const products = await loadProducts(), catalog = (await loadCatalog()).map(({ requirements, ...type }) => type);
const select = (name, alias = name, predicate = () => true) => cotsBinding(facts.find(fact => fact.name === name && predicate(fact)), { key: alias, name: alias });
function fixture() {
  const workspace = emptyWorkspace(catalog), eps = workspace.elements.find(element => element.definition.endsWith('::PowerSubsystem'));
  workspace.variables = [{ name: 'voltage_V', type: 'float', unit: 'V' }, { name: 'count', type: 'integer' }];
  const row = (id, condition) => ({ key: id.toLowerCase(), id, context: eps.key, kind: 'Requirement', text: 'The input shall support $$voltage_V$$.',
    condition, sources: [], affected: [], parameters: { voltage_V: '8', count: 'CMP001.series_cell_count' } });
  workspace.statements = [row('EPS001', ''), row('EPS002', 'not CMP001.autonomous_thermal_shutdown and CMP001.package_id == "SOT-23-6"')];
  workspace.components = [{ key: 'protector', id: 'CMP001', owner: eps.key, product, requirements: ['eps001', 'eps002'], facts: [
    select('input_voltage_min'), select('input_voltage_max'), select('autonomous_overcurrent_protection'),
    select('autonomous_thermal_shutdown'), select('package_id'), select('series_cell_count'),
  ] }];
  setVerificationMethods(workspace.statements[0], [{ key: 'cots', component: 'protector', condition: 'CMP001.input_voltage_min <= voltage_V <= CMP001.input_voltage_max and CMP001.autonomous_overcurrent_protection' }]);
  return validateWorkspace(workspace, catalog, products);
}
async function temporary(t) {
  const directory = await mkdtemp(join(tmpdir(), 'cots-facts-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  return directory;
}

test('trusted COTS facts retain types, value meaning, conditions, internal elements and source provenance', async () => {
  const maximum = facts.find(fact => fact.name === 'input_voltage_max');
  assert.equal(maximum.value, 10); assert.equal(maximum.type, 'float'); assert.equal(maximum.unit, 'V');
  assert.equal(maximum.valueKind, 'maximum'); assert.equal(maximum.element, 'self');
  assert.match(maximum.id, /^[a-f0-9]{64}$/); assert.match(maximum.revision, /^[a-f0-9]{64}$/);
  assert.equal(maximum.source.locator, 'page=11'); assert.ok(maximum.source.url.startsWith('https://'));
  assert.equal(facts.find(fact => fact.name === 'autonomous_overcurrent_protection').value, true);
  assert.equal(facts.find(fact => fact.name === 'autonomous_thermal_shutdown').value, false);
  assert.equal(facts.find(fact => fact.name === 'series_cell_count').type, 'integer');
  const delays = facts.filter(fact => fact.name === 'overcurrent_delay');
  assert.deepEqual(new Set(delays.map(fact => fact.valueKind)), new Set(['minimum', 'typical', 'maximum']));
  assert.ok(delays.every(fact => fact.condition.id && (Object.keys(fact.condition.values).length || fact.condition.parameters.length)));
  const internal = (await loadCotsFacts('adi_ltc4368ims_2_pbf')).facts;
  assert.ok(internal.some(fact => fact.element !== 'self'));
  assert.equal(new Set(facts.map(fact => fact.id)).size, facts.length);
  await assert.rejects(() => loadCotsFacts('../secrets'), /product ID/);
  await assert.rejects(() => loadCotsFacts('missing_product'), /existing COTS product/);
});

test('COTS numeric, Integer, Boolean and String references share the restricted evaluator across modes', () => {
  const workspace = fixture();
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'high', name: 'High voltage', sunlight: 0, eclipse: 0 }];
  workspace.statements[0].parameters.voltage_V = '8 if mode == "Nominal" else 12';
  const checks = evaluateChecks(workspace);
  assert.equal(checks[0].state, 'fail');
  assert.deepEqual(checks[0].modes.map(mode => mode.state), ['pass', 'fail']);
  assert.equal(checks[1].state, 'pass'); assert.equal(checks[1].values.count, 2);
  workspace.statements[1].condition = 'CMP001.autonomous_thermal_shutdown';
  assert.equal(evaluateChecks(workspace)[1].state, 'fail');
  workspace.statements[1].condition = 'CMP001.autonomous_overcurrent_protection + 1 > 0';
  assert.equal(evaluateChecks(workspace)[1].state, 'error');
});

test('unbound, missing, stale and substituted COTS evidence stays pending without inventing false values', () => {
  const workspace = fixture(), component = workspace.components[0];
  component.facts.find(fact => fact.name === 'input_voltage_max').revision = '0'.repeat(64);
  assert.equal(cotsBindingState(component.facts.find(fact => fact.name === 'input_voltage_max'), facts).state, 'pending');
  assert.equal(evaluateChecks(workspace)[0].state, 'pending');
  component.product = 'adi_ltc4359ims8_pbf';
  assert.ok(evaluateChecks(workspace).every(result => result.state === 'pending'));
  component.facts = [];
  workspace.statements[0].verifications[0].condition = 'True';
  assert.equal(evaluateChecks(workspace)[0].state, 'pending');
  workspace.statements[1].condition = 'CMP001.unknown_reference > 0';
  assert.equal(evaluateChecks(workspace)[1].state, 'error');
});

test('storage accepts only named pinned selections and mutually exclusive verification sources', () => {
  for (const mutate of [
    state => { state.components[0].facts[0].value = 12; },
    state => { state.components[0].facts[0].name = 'True'; },
    state => { state.components[0].facts[1].name = state.components[0].facts[0].name; },
    state => { state.components[0].facts[0].revision = 'bad'; },
    state => { state.components[0].facts[0].type = 'object'; },
    state => { state.components[0].facts[0].unit = 'V\n'; },
    state => { state.components[0].values = { input_voltage_max: 10 }; },
    state => { state.components[0].facts = Array.from({ length: 65 }, () => state.components[0].facts[0]); },
    state => { state.statements[0].verifications[0].component = 'missing'; },
  ]) {
    const state = fixture(); mutate(state);
    assert.throws(() => validateWorkspace(state, catalog, products));
  }
  const workspace = fixture();
  assert.deepEqual(validateWorkspace(JSON.parse(JSON.stringify(workspace)), catalog, products), workspace);
  const script = scriptInstance({ id: 'fake', name: 'Fake', revision: 'a'.repeat(64), inputs: [], outputs: [{ name: 'value', type: 'float' }] }, { key: 'script', id: 'SCR001' });
  workspace.scripts.push(script); workspace.statements[0].verifications[0].script = 'script';
  assert.throws(() => validateWorkspace(workspace, catalog, products), /one value source/);
});

test('COTS aliases have one owner, rewrite shared expressions and preserve concurrent requirement edits', () => {
  const workspace = fixture(), before = structuredClone(workspace.components[0]), edited = structuredClone(before);
  edited.facts.find(fact => fact.name === 'input_voltage_max').name = 'supported_max_V';
  const current = structuredClone(workspace); current.statements[1].rationale = 'Concurrent note.';
  const merged = mergeCotsDraft(current, before, edited);
  assert.match(merged.statements[0].verifications[0].condition, /CMP001.supported_max_V/);
  assert.equal(merged.statements[1].rationale, 'Concurrent note.');
  assert.ok(evaluateChecks(merged).every(result => result.state === 'pass'));
  const renames = cotsRenames(before, edited);
  const reqDraft = structuredClone(workspace); reqDraft.statements[0].parameters.voltage_V = '9';
  const original = structuredClone(workspace);
  rewriteCotsReferences(original, before.id, renames); rewriteCotsReferences(reqDraft, before.id, renames);
  const savedReq = mergeRequirementDraft(merged, original, reqDraft, 'eps001');
  assert.equal(savedReq.statements[0].parameters.voltage_V, '9');
  assert.equal(savedReq.components[0].facts.find(fact => fact.name === 'supported_max_V').fact, before.facts[1].fact);
  assert.ok(cotsUses(merged, merged.components[0], 'supported_max_V').some(use => use.id === 'EPS001'));
  const removed = structuredClone(before); removed.facts = removed.facts.filter(fact => fact.name !== 'input_voltage_max');
  assert.throws(() => mergeCotsDraft(workspace, before, removed), /Remove expression references/);
  current.components[0].product = 'adi_ltc4359ims8_pbf';
  assert.throws(() => mergeCotsDraft(current, before, edited), /changed/);
  rewriteRowReferences(merged, new Map([['CMP001', 'COT099']])); merged.components[0].id = 'COT099';
  assert.match(merged.statements[0].verifications[0].condition, /COT099.supported_max_V/);
});

test('Python scripts consume COTS facts through requirement parameters and invalidate evidence after substitutions', async () => {
  const workspace = fixture(), definitions = await loadScriptCatalog();
  const script = scriptInstance(definitions.find(definition => definition.id === 'normal_interval'), { key: 'analysis', id: 'SCR001' });
  Object.assign(script.parameters, { mean: 'EPS001.voltage_V', standard_deviation: '1', confidence: '0.95' });
  workspace.scripts.push(script); workspace.statements[0].parameters.voltage_V = 'CMP001.input_voltage_max';
  setVerificationMethods(workspace.statements[0], [{ key: 'cots', component: 'protector', condition: 'CMP001.autonomous_overcurrent_protection' },
    { key: 'script', script: script.key, condition: 'SCR001.upper > voltage_V' }]);
  const evidence = await runScripts(workspace, script.key);
  assert.equal(evidence.runs['analysis:'].state, 'value'); assert.match(evidence.cotsSignature, /^[a-f0-9]{64}$/);
  assert.equal(evaluateChecks(workspace, { scriptResults: evidence })[0].state, 'pass');
  const signature = scriptContext(workspace); workspace.components[0].product = 'adi_ltc4359ims8_pbf';
  assert.notEqual(signature, scriptContext(workspace));
  assert.equal(evaluateChecks(workspace, { scriptResults: evidence })[0].state, 'pending');
});

test('external catalogue changes invalidate cached runs even when workspace expressions remain identical', async t => {
  const directory = await temporary(t), data = join(directory, 'cots');
  const { mkdir } = await import('node:fs/promises'); await mkdir(data);
  const source = fileURLToPath(new URL('../../cots/', import.meta.url));
  for (const file of await readdir(source)) if (file.endsWith('.tsv')) await copyFile(join(source, file), join(data, file));
  const bootstrap = join(directory, 'worker.py'), workerDirectory = fileURLToPath(new URL('../worker/', import.meta.url));
  await writeFile(bootstrap, `import sys\nfrom pathlib import Path\nsys.path.insert(0, ${JSON.stringify(workerDirectory)})\nimport cots_data\ncots_data.DIRECTORY = Path(${JSON.stringify(data)})\nfrom main import main\nmain()\n`);
  const evaluator = createEvaluationWorker({ path: bootstrap }); t.after(() => evaluator.close());
  const workspace = fixture(), definition = (await loadScriptCatalog()).find(definition => definition.id === 'normal_interval');
  const script = scriptInstance(definition, { key: 'analysis', id: 'SCR001' });
  Object.assign(script.parameters, { mean: 'EPS001.voltage_V', standard_deviation: '1', confidence: '0.95' });
  workspace.scripts.push(script); workspace.statements[0].parameters.voltage_V = 'CMP001.input_voltage_max';
  setVerificationMethods(workspace.statements[0], [{ key: 'script', script: script.key, condition: 'True' }]);
  const evidence = await runScripts(workspace, script.key, { evaluator });
  assert.equal((await evaluator.evaluate(workspace, { scriptResults: evidence })).results[0].state, 'pass');
  const path = join(data, 'parameters.tsv'), original = await readFile(path, 'utf8');
  const before = `${product}\tself\tinput_voltage_max\t10\tmaximum\tV`;
  assert.ok(original.includes(before));
  await writeFile(path, original.replace(before, `${product}\tself\tinput_voltage_max\t9\tmaximum\tV`));
  const stale = await evaluator.evaluate(workspace, { scriptResults: evidence });
  assert.notEqual(stale.cotsSignature, evidence.cotsSignature);
  assert.equal(stale.results[0].state, 'pending');
  const updated = await loadCotsFacts(product, { evaluator });
  const binding = workspace.components[0].facts.find(binding => binding.name === 'input_voltage_max');
  const record = updated.facts.find(fact => fact.id === binding.fact);
  assert.equal(record.value, 9); assert.notEqual(record.revision, binding.revision);
  Object.assign(binding, cotsBinding(record, binding));
  const fresh = await runScripts(workspace, script.key, { evaluator });
  assert.equal((await evaluator.evaluate(workspace, { scriptResults: fresh })).results[0].state, 'pass');
});

test('COTS catalogue inspection is read-only and JSON sessions persist selections without copied values', async t => {
  const directory = await temporary(t), modelPath = join(directory, 'mission.json'), workspace = fixture();
  const source = JSON.stringify(workspace, null, 2) + '\n'; await writeFile(modelPath, source);
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
  const base = `http://127.0.0.1:${server.address().port}`;
  const inspected = await fetch(`${base}/api/cots?product=${product}`);
  assert.equal(inspected.status, 200); assert.deepEqual((await inspected.json()).facts, facts);
  assert.equal((await fetch(`${base}/api/cots?product=../secret`)).status, 400);
  assert.equal((await fetch(`${base}/api/cots`, { method: 'POST' })).status, 405);
  assert.equal(await readFile(modelPath, 'utf8'), source);
  const sessions = createSessions(modelPath, { catalog, products });
  const copy = await sessions.create({ name: 'COTS study', template: 'copy', workspace });
  assert.deepEqual(copy.workspace.components[0].facts, workspace.components[0].facts);
  assert.ok(copy.workspace.components[0].facts.every(binding => !Object.hasOwn(binding, 'value')));
  assert.equal(await readFile(modelPath, 'utf8'), source);
});
