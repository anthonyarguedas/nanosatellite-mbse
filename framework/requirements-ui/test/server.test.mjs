import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { request as httpRequest } from 'node:http';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { createServer } from '../server.mjs';
import { loadCatalog } from '../catalog.mjs';
import { addResourceBudgets, declareRequirementVariables, emptyWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { isResourceRequirement } from '../resource-budgets.mjs';
import { createStore } from '../storage.mjs';

async function start(t) {
  const dir = await mkdtemp(join(tmpdir(), 'requirements-ui-test-'));
  const modelPath = join(dir, 'mission.json');
  const original = JSON.stringify(emptyWorkspace(await loadCatalog()), null, 2) + '\n';
  await writeFile(modelPath, original);
  const server = createServer({ modelPath });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(async () => {
    await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); });
    await rm(dir, { recursive: true, force: true });
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  const get = async () => (await fetch(`${base}/api/workspace`)).json();
  const put = (workspace, revision, headers = {}) => fetch(`${base}/api/workspace`, {
    method: 'PUT', headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ workspace, revision }),
  });
  return { base, modelPath, storagePath: join(dir, 'mission.json'), original, get, put };
}

function populated() {
  const workspace = { ...emptyWorkspace(), expressionLanguage: 'python' };
  workspace.stakeholders.push({ key: 's1', id: 'REG', name: 'Agência espacial', type: 'Regulatory Agency' });
  workspace.statements.push({ key: 'r1', id: 'REQ001', context: 'external', affected: [], kind: 'Requirement', text: 'Operate for {x} months.', sources: ['s1'], condition: 'x >= 12', parameters: { x: '12', y: null, z: '0', a: null } });
  return { ...addResourceBudgets(workspace), resourceBudgets: true };
}

test('the server refuses to use application code as workspace storage', () => {
  for (const name of ['server.mjs', 'worker/catalog_data.py']) {
    const modelPath = fileURLToPath(new URL(`../${name}`, import.meta.url));
    assert.throws(() => createServer({ modelPath }), /Choose a .json workspace/);
  }
});

test('serves the UI with a CSP and rejects unknown files and methods', async t => {
  const { base } = await start(t);
  const response = await fetch(base);
  assert.equal(response.status, 200);
  assert.match(await response.text(), /Stakeholder Requirements/);
  assert.match(response.headers.get('content-security-policy'), /frame-ancestors 'none'/);
  assert.doesNotMatch(response.headers.get('content-security-policy'), /unsafe-eval/);
  for (const path of ['/app.js', '/requirement-editor.js', '/requirement-preview.js', '/style.css', '/model.mjs', '/resource-budgets.mjs', '/parameter-states.mjs', '/verification-worker.js']) assert.equal((await fetch(base + path)).status, 200);
  assert.equal((await fetch(base + '/server.mjs')).status, 404);
  assert.equal((await fetch(base + '/api/workspace', { method: 'DELETE' })).status, 405);
});

test('saves and reloads plain JSON as the sole source of truth', async t => {
  const { modelPath, storagePath, original, get, put } = await start(t);
  const before = await get();
  const workspace = populated();
  const response = await put(workspace, before.revision);
  assert.equal(response.status, 200);
  const after = await get();
  assert.deepEqual(after.workspace, workspace);
  assert.notEqual(before.revision, after.revision);
  const source = await readFile(storagePath, 'utf8');
  assert.deepEqual(JSON.parse(source), workspace);
});

test('EPS components and parametric requirements save and reload through the API', async t => {
  const { storagePath, get, put } = await start(t);
  const { workspace, revision, catalog } = await get();
  const power = workspace.elements.find(row => row.definition === 'SpaceSegment::CubeSat::PowerSubsystem');
  const battery = workspace.elements.find(row => row.owner === power.key && row.name === 'Batteries');
  assert.equal(catalog.filter(type => type.parent === power.definition).length, 6);
  workspace.statements.push({ key: 'eps-capacity', id: 'EPS101', context: power.key, affected: [battery.key],
    sources: [power.key], kind: 'Requirement', text: 'Battery capacity shall be at least {x} Wh.',
    condition: 'x >= 12', parameters: { ...Object.fromEntries(workspace.variables.map(variable => [variable.name, null])), x: '15' } });
  assert.equal((await put(workspace, revision)).status, 200);
  assert.deepEqual((await get()).workspace, workspace);
  const stored = JSON.parse(await readFile(storagePath, 'utf8'));
  assert.equal(stored.statements.at(-1).context, power.key);
  assert.deepEqual(stored.statements.at(-1).affected, [battery.key]);
  assert.equal(stored.statements.at(-1).condition, 'x >= 12');
  assert.deepEqual(stored, workspace);
});

test('marker-created parameter columns save and export through the API', async t => {
  const { get, put, storagePath } = await start(t);
  const { workspace, revision, catalog } = await get();
  const row = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  row.text = 'The orbit shall have altitude $$altitude_km$$ km with uncertainty $$altitude_uncertainty_km$$ km.';
  declareRequirementVariables(workspace, row);
  row.parameters.altitude_km = '500'; row.parameters.altitude_uncertainty_km = '0.5 * 2';
  workspace.variables.find(variable => variable.name === 'altitude_uncertainty_km').unit = 'km';
  assert.equal((await put(workspace, revision)).status, 200);
  assert.deepEqual((await get()).workspace, workspace);
  const stored = JSON.parse(await readFile(storagePath, 'utf8'));
  assert.equal(stored.statements.find(statement => statement.key === row.key).parameters.altitude_uncertainty_km, '0.5 * 2');
  assert.deepEqual(stored, workspace);
});

test('rationale saves, exports and clears without changing the original provenance', async t => {
  const { base, get, put } = await start(t);
  const { workspace, revision } = await get();
  const row = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  assert.equal(row.rationale, row.origin);
  row.rationale = `${row.origin}\nUse the sourced Earth constants.`;
  assert.equal((await put(workspace, revision)).status, 200);
  const saved = await get();
  assert.deepEqual(saved.workspace, workspace);
  const exported = await fetch(base + '/api/json', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace }) });
  assert.equal(exported.status, 200);
  assert.equal((await exported.json()).statements.find(statement => statement.key === row.key).rationale, row.rationale);
  row.rationale = '';
  assert.equal((await put(workspace, saved.revision)).status, 200);
  const cleared = (await get()).workspace.statements.find(statement => statement.key === row.key);
  assert.equal(cleared.rationale, '');
  assert.equal(cleared.origin, row.origin);
});

test('the API stores editable expressions in every parameter cell and retains invalid drafts safely', async t => {
  const { base, storagePath, get, put } = await start(t);
  const { workspace, revision, catalog } = await get();
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = '300 + 350';
  const period = `(${orbit.parameters.orbit_period_s}) * 1`;
  orbit.parameters.orbit_period_s = period;
  assert.equal((await put(workspace, revision)).status, 200);
  let loaded = await get();
  assert.equal(loaded.workspace.statements.find(row => row.key === orbit.key).parameters.orbit_period_s, period);
  assert.deepEqual(JSON.parse(await readFile(storagePath, 'utf8')), workspace);
  assert.ok(workspace.statements.every(row => !Object.hasOwn(row, 'formulas')));
  orbit.parameters.altitude_km = '1; package Injected {}';
  assert.equal((await put(workspace, loaded.revision)).status, 200);
  loaded = await get();
  assert.deepEqual(loaded.workspace, workspace);
  const source = JSON.parse(await readFile(storagePath, 'utf8'));
  assert.equal(source.statements.find(row => row.key === orbit.key).parameters.altitude_km, '1; package Injected {}');
  const download = await fetch(`${base}/api/json`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace }) });
  assert.equal(download.status, 200);
  assert.equal((await download.json()).statements.find(row => row.key === orbit.key).parameters.altitude_km, '1; package Injected {}');
  orbit.parameters.altitude_km = 650;
  const rejected = await put(workspace, loaded.revision);
  assert.equal(rejected.status, 400);
  assert.match((await rejected.json()).error, /expression text/);
});

test('unsupported stored schemas fail without migration or replacement', async t => {
  const { base, modelPath, get } = await start(t);
  const { workspace } = await get(); workspace.version = 4;
  const source = JSON.stringify(workspace); await writeFile(modelPath, source);
  const response = await fetch(base + '/api/workspace');
  assert.equal(response.status, 400); assert.match((await response.json()).error, /differs from app format/);
  assert.equal(await readFile(modelPath, 'utf8'), source);
});

test('new stores write only JSON and leave neighboring files untouched', async t => {
  const dir = await mkdtemp(join(tmpdir(), 'new-mission-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const neighbor = join(dir, 'notes.txt'); await writeFile(neighbor, 'Retain these notes.\n');
  const path = join(dir, 'missions', 'demo.json'), store = createStore(path);
  const initial = await store.read(); assert.equal(initial.modelName, 'demo.json');
  await store.save(populated(), initial.revision);
  assert.deepEqual(JSON.parse(await readFile(path, 'utf8')), populated());
  assert.equal(await readFile(neighbor, 'utf8'), 'Retain these notes.\n');
});

test('stored conditions are parsed rather than executed by the server', async t => {
  const { get, put, storagePath } = await start(t);
  const before = await get();
  const workspace = populated();
  workspace.statements[0].condition = 'globalThis.requirementsInjected = true';
  assert.equal((await put(workspace, before.revision)).status, 200);
  assert.equal(globalThis.requirementsInjected, undefined);
  assert.equal(JSON.parse(await readFile(storagePath, 'utf8')).statements[0].condition, 'globalThis.requirementsInjected = true');
});

test('API writes cannot set a manual verification flag', async t => {
  const { get, put, modelPath, original } = await start(t);
  const { revision } = await get();
  const workspace = populated();
  workspace.statements[0].verified = true;
  const response = await put(workspace, revision);
  assert.equal(response.status, 400);
  assert.match((await response.json()).error, /computed from verification methods/);
  assert.equal(await readFile(modelPath, 'utf8'), original);
});

test('COTS catalog selections and affected requirements save and reload', async t => {
  const { get, put, storagePath } = await start(t);
  const { workspace, revision, catalog, products } = await get();
  assert.equal(products.length, 99);
  assert.equal(products[0].pins, undefined);
  const power = workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem'));
  workspace.statements.push({ key: 'eps1', id: 'EPS101', context: power.key, kind: 'Requirement', text: '', sources: [], affected: [],
    condition: 'True', parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, null])) });
  workspace.components.push({ key: 'rtc1', id: 'CMP001', owner: power.key, product: 'abracon_ab1805_t3', requirements: ['eps1'] });
  assert.equal((await put(workspace, revision)).status, 200);
  assert.deepEqual((await get()).workspace, workspace);
  assert.deepEqual(JSON.parse(await readFile(storagePath, 'utf8')), workspace);
  workspace.components[0].verified = true;
  const response = await put(workspace, (await get()).revision);
  assert.equal(response.status, 400);
  assert.match((await response.json()).error, /computed/);
});

test('JSON downloads retain generic definitions, provenance and unsaved inputs without changing storage', async t => {
  const { base, get, modelPath, original } = await start(t);
  const { workspace } = await get();
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = '650';
  const post = (state = workspace, headers = {}) => fetch(`${base}/api/json`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify({ workspace: state }),
  });
  const response = await post(); assert.equal(response.status, 200);
  assert.match(response.headers.get('content-disposition'), /mission-export\.json/);
  const exported = await response.json(); assert.deepEqual(exported, workspace);
  const generic = exported.statements.filter(row => row.definition.startsWith('FrameworkRequirements::'));
  assert.equal(generic.length, 27);
  assert.ok(generic.every(row => row.origin && row.affected.length));
  assert.ok(exported.statements.some(isResourceRequirement));
  assert.equal(exported.statements.find(row => row.key === orbit.key).parameters.altitude_km, '650');
  assert.equal(await readFile(modelPath, 'utf8'), original);
  assert.equal((await fetch(`${base}/api/sysml`)).status, 404);
  assert.equal((await fetch(`${base}/api/json`)).status, 405);
  assert.equal((await post(workspace, { Origin: 'https://example.com' })).status, 403);
  const draft = structuredClone(workspace); draft.statements[0].condition = 'unknown(1)';
  assert.equal((await post(draft)).status, 200);
  assert.equal(await readFile(modelPath, 'utf8'), original);
});

test('KiCad and F-Prime downloads include draft components without writing mission storage', async t => {
  const { base, get, modelPath, original } = await start(t);
  const { workspace } = await get();
  const context = workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem')).key;
  workspace.components.push({ key: 'draft-rtc', id: 'CMP009', owner: context, product: 'abracon_ab1805_t3', requirements: [] });
  const post = (kind, body = { workspace, context }, headers = {}) => fetch(`${base}/api/${kind}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body),
  });
  const schematic = await post('kicad');
  assert.equal(schematic.status, 200);
  assert.match(schematic.headers.get('content-disposition'), /eps-eps\.kicad_sch/);
  assert.match(await schematic.text(), /\(property "Reference" "CMP009"/);
  const archive = await post('fprime');
  assert.equal(archive.status, 200);
  assert.equal(archive.headers.get('content-type'), 'application/zip');
  assert.match(archive.headers.get('content-disposition'), /-fprime\.zip/);
  const zip = Buffer.from(await archive.arrayBuffer());
  assert.equal(zip.readUInt32LE(0), 0x04034b50);
  assert.ok(zip.includes(Buffer.from('active component Component_CMP009_AB1805_T3')));
  assert.equal(await readFile(modelPath, 'utf8'), original);
  for (const kind of ['kicad', 'fprime']) {
    assert.equal((await fetch(`${base}/api/${kind}`)).status, 405);
    assert.equal((await post(kind, { workspace, context: 'domain-bus' })).status, 400);
    assert.equal((await post(kind, { workspace, context }, { Origin: 'https://example.com' })).status, 403);
    const empty = structuredClone(workspace); empty.components = [];
    assert.equal((await post(kind, { workspace: empty, context })).status, 400);
    const invalid = structuredClone(workspace); invalid.components[0].product = 'unknown';
    assert.equal((await post(kind, { workspace: invalid, context })).status, 400);
  }
});

test('UTF-8 text survives a character split across HTTP chunks', async t => {
  const { base, get } = await start(t);
  const { revision } = await get();
  const workspace = populated();
  const bytes = Buffer.from(JSON.stringify({ workspace, revision }));
  const split = bytes.indexOf(Buffer.from('ê')) + 1;
  const code = await new Promise((resolve, reject) => {
    const request = httpRequest(base + '/api/workspace', {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
    }, response => { response.resume(); response.on('end', () => resolve(response.statusCode)); });
    request.on('error', reject);
    request.write(bytes.subarray(0, split));
    setTimeout(() => request.end(bytes.subarray(split)), 20);
  });
  assert.equal(code, 200);
  assert.deepEqual((await get()).workspace, workspace);
});

test('rejects stale browser revisions and preserves external edits', async t => {
  const { modelPath, get, put } = await start(t);
  const initial = await get();
  await writeFile(modelPath, (await readFile(modelPath, 'utf8')) + '\n// External edit\n');
  const response = await put(populated(), initial.revision);
  assert.equal(response.status, 409);
  assert.ok((await readFile(modelPath, 'utf8')).endsWith('// External edit\n'));
});

test('serializes simultaneous saves so one stale tab cannot overwrite another', async t => {
  const { get, put } = await start(t);
  const { revision } = await get();
  const results = await Promise.all([put(populated(), revision), put(emptyWorkspace(), revision)]);
  assert.deepEqual(results.map(response => response.status).sort(), [200, 409]);
});

test('invalid data and cross-origin writes leave the model unchanged', async t => {
  const { base, modelPath, original, get, put } = await start(t);
  const { revision } = await get();
  const workspace = populated();
  workspace.statements[0].sources = ['missing'];
  assert.equal((await put(workspace, revision)).status, 400);
  assert.equal((await put(populated(), revision, { Origin: 'https://example.com' })).status, 403);
  const hostStatus = await new Promise((resolve, reject) => {
    const request = httpRequest(base, { headers: { Host: 'evil.example' } }, response => {
      response.resume();
      response.on('end', () => resolve(response.statusCode));
    });
    request.on('error', reject);
    request.end();
  });
  assert.equal(hostStatus, 403);
  assert.equal((await fetch(base + '/api/workspace', {
    method: 'PUT', headers: { 'Content-Type': 'text/plain' }, body: '{}',
  })).status, 415);
  assert.equal(await readFile(modelPath, 'utf8'), original);
});
