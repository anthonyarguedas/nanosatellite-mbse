import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { request as httpRequest } from 'node:http';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { createServer } from '../server.mjs';
import { declareRequirementVariables, emptyWorkspace } from '../model.mjs';
import { createStore, readWorkspace } from '../sysml.mjs';

async function start(t) {
  const dir = await mkdtemp(join(tmpdir(), 'requirements-ui-test-'));
  const modelPath = join(dir, 'mission.sysml');
  const original = 'package Existing { part def Satellite; }\n';
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
  return { base, modelPath, original, get, put };
}

function populated() {
  const workspace = emptyWorkspace();
  workspace.stakeholders.push({ key: 's1', id: 'REG', name: 'Agência espacial', type: 'Regulatory Agency' });
  workspace.statements.push({ key: 'r1', id: 'REQ001', context: 'external', affected: [], kind: 'Requirement', text: 'Operate for {x} months.', sources: ['s1'], condition: 'x >= 12', parameters: { x: '12', y: null, z: '0', a: null } });
  return workspace;
}

test('the server refuses to use a generic framework file as mission storage', () => {
  for (const name of ['external', 'mission', 'eps', 'catalog', 'cad', 'requirements']) {
    const modelPath = fileURLToPath(new URL(`../../${name}.sysml`, import.meta.url));
    assert.throws(() => createServer({ modelPath }), /Generic framework models are read only/);
  }
});

test('serves the UI with a CSP and rejects unknown files and methods', async t => {
  const { base } = await start(t);
  const response = await fetch(base);
  assert.equal(response.status, 200);
  assert.match(await response.text(), /Stakeholder Requirements/);
  assert.match(response.headers.get('content-security-policy'), /frame-ancestors 'none'/);
  assert.doesNotMatch(response.headers.get('content-security-policy'), /unsafe-eval/);
  for (const path of ['/app.js', '/requirement-editor.js', '/style.css', '/model.mjs', '/verification.mjs', '/verification-worker.js']) assert.equal((await fetch(base + path)).status, 200);
  assert.equal((await fetch(base + '/server.mjs')).status, 404);
  assert.equal((await fetch(base + '/api/workspace', { method: 'DELETE' })).status, 405);
});

test('saves and reloads typed SysML without changing the existing model', async t => {
  const { modelPath, original, get, put } = await start(t);
  const before = await get();
  const workspace = populated();
  const response = await put(workspace, before.revision);
  assert.equal(response.status, 200);
  const after = await get();
  assert.deepEqual(after.workspace, workspace);
  assert.notEqual(before.revision, after.revision);
  const source = await readFile(modelPath, 'utf8');
  assert.ok(source.startsWith(original));
  assert.deepEqual(readWorkspace(source), workspace);
});

test('EPS components and parametric requirements save and reload through the API', async t => {
  const { modelPath, get, put } = await start(t);
  const { workspace, revision, catalog } = await get();
  const power = workspace.elements.find(row => row.definition === 'SpaceSegment::CubeSat::PowerSubsystem');
  const battery = workspace.elements.find(row => row.owner === power.key && row.name === 'Batteries');
  assert.equal(catalog.filter(type => type.parent === power.definition).length, 6);
  workspace.statements.push({ key: 'eps-capacity', id: 'EPS101', context: power.key, affected: [battery.key],
    sources: [power.key], kind: 'Requirement', text: 'Battery capacity shall be at least {x} Wh.',
    condition: 'x >= 12', parameters: { ...Object.fromEntries(workspace.variables.map(variable => [variable.name, null])), x: '15' } });
  assert.equal((await put(workspace, revision)).status, 200);
  assert.deepEqual((await get()).workspace, workspace);
  const source = await readFile(modelPath, 'utf8');
  assert.match(source, /attribute tableName : String = "EPS"/);
  assert.match(source, /: SpaceSegment::CubeSat::PowerSubsystem::Batteries \{/);
  assert.match(source, /require constraint verificationCondition \{ \('x' >= 12\) \}/);
  assert.deepEqual(readWorkspace(source, catalog), workspace);
});

test('marker-created parameter columns save and export through the API', async t => {
  const { get, put, modelPath } = await start(t);
  const { workspace, revision, catalog } = await get();
  const row = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  row.text = 'The orbit shall have altitude $$altitude_km$$ km with uncertainty $$altitude_uncertainty_km$$ km.';
  declareRequirementVariables(workspace, row);
  row.parameters.altitude_km = '500'; row.parameters.altitude_uncertainty_km = '0.5 * 2';
  assert.equal((await put(workspace, revision)).status, 200);
  assert.deepEqual((await get()).workspace, workspace);
  const source = await readFile(modelPath, 'utf8');
  assert.match(source, /attribute 'altitude_uncertainty_km' : Real\[0\.\.1\] = \(0.5 \* 2\)/);
  assert.deepEqual(readWorkspace(source, catalog), workspace);
});

test('the API stores editable expressions in every parameter cell and retains invalid drafts safely', async t => {
  const { base, modelPath, get, put } = await start(t);
  const { workspace, revision, catalog } = await get();
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = '300 + 350';
  const period = `(${orbit.parameters.orbit_period_s}) * 1`;
  orbit.parameters.orbit_period_s = period;
  assert.equal((await put(workspace, revision)).status, 200);
  let loaded = await get();
  assert.equal(loaded.workspace.statements.find(row => row.key === orbit.key).parameters.orbit_period_s, period);
  assert.deepEqual(readWorkspace(await readFile(modelPath, 'utf8'), catalog), workspace);
  assert.ok(workspace.statements.every(row => !Object.hasOwn(row, 'formulas')));
  orbit.parameters.altitude_km = '1; package Injected {}';
  assert.equal((await put(workspace, loaded.revision)).status, 200);
  loaded = await get();
  assert.deepEqual(loaded.workspace, workspace);
  const source = await readFile(modelPath, 'utf8');
  assert.match(source, /Invalid parameter expression for altitude_km/);
  const download = await fetch(`${base}/api/sysml`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace }) });
  assert.equal(download.status, 400);
  orbit.parameters.altitude_km = 650;
  const rejected = await put(workspace, loaded.revision);
  assert.equal(rejected.status, 400);
  assert.match((await rejected.json()).error, /SysML expression text/);
});

test('opening an existing version 4 mission adds EPS components without writing until save', async t => {
  const { modelPath, get, put } = await start(t);
  const { workspace } = await get();
  const power = workspace.elements.find(row => row.definition === 'SpaceSegment::CubeSat::PowerSubsystem');
  workspace.version = 4;
  workspace.elements = workspace.elements.filter(row => row.owner !== power.key);
  const original = `// <requirements-ui>\n/* requirements-ui:data\n${JSON.stringify(workspace)}\nrequirements-ui:end-data */\n// </requirements-ui>\n`;
  await writeFile(modelPath, original);
  const loaded = await get();
  assert.equal(loaded.workspace.version, 8);
  assert.equal(loaded.workspace.elements.filter(row => row.owner === power.key).length, 6);
  assert.equal(await readFile(modelPath, 'utf8'), original);
  assert.equal((await put(loaded.workspace, loaded.revision)).status, 200);
  assert.deepEqual((await get()).workspace, loaded.workspace);
});

test('a new mission file is created with generic imports and leaves generic files untouched', async t => {
  const dir = await mkdtemp(join(tmpdir(), 'new-mission-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const generic = join(dir, 'external.sysml');
  await writeFile(generic, 'package External {}\n');
  const path = join(dir, 'missions', 'demo.sysml');
  const store = createStore(path);
  const initial = await store.read();
  assert.equal(initial.modelName, 'demo.sysml');
  await store.save(populated(), initial.revision);
  const source = await readFile(path, 'utf8');
  assert.match(source, /package DemoRequirements/);
  assert.match(source, /private import External::\*/);
  assert.match(source, /require constraint verification/);
  assert.equal(await readFile(generic, 'utf8'), 'package External {}\n');
});

test('stored conditions are parsed rather than executed by the server', async t => {
  const { get, put, modelPath } = await start(t);
  const before = await get();
  const workspace = populated();
  workspace.statements[0].condition = 'globalThis.requirementsInjected = true';
  assert.equal((await put(workspace, before.revision)).status, 200);
  assert.equal(globalThis.requirementsInjected, undefined);
  assert.doesNotMatch(await readFile(modelPath, 'utf8'), /require constraint verification/);
});

test('API writes cannot set a manual verification flag', async t => {
  const { get, put, modelPath, original } = await start(t);
  const { revision } = await get();
  const workspace = populated();
  workspace.statements[0].verified = true;
  const response = await put(workspace, revision);
  assert.equal(response.status, 400);
  assert.match((await response.json()).error, /computed from a SysML condition/);
  assert.equal(await readFile(modelPath, 'utf8'), original);
});

test('COTS catalog selections and affected requirements save and reload', async t => {
  const { get, put, modelPath } = await start(t);
  const { workspace, revision, catalog, products } = await get();
  assert.equal(products.length, 99);
  assert.equal(products[0].pins, undefined);
  const power = workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem'));
  workspace.statements.push({ key: 'eps1', id: 'EPS101', context: power.key, kind: 'Requirement', text: '', sources: [], affected: [],
    condition: 'true', parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, null])) });
  workspace.components.push({ key: 'rtc1', id: 'CMP001', owner: power.key, product: 'abracon_ab1805_t3', requirements: ['eps1'] });
  assert.equal((await put(workspace, revision)).status, 200);
  assert.deepEqual((await get()).workspace, workspace);
  assert.deepEqual(readWorkspace(await readFile(modelPath, 'utf8'), catalog, products), workspace);
  workspace.components[0].verified = true;
  const response = await put(workspace, (await get()).revision);
  assert.equal(response.status, 400);
  assert.match((await response.json()).error, /computed/);
});

test('SysML downloads contain generic sizing usages and unsaved parameters without changing mission storage', async t => {
  const { base, get, modelPath, original } = await start(t);
  const { workspace } = await get();
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  assert.equal(workspace.statements.length, 27);
  orbit.parameters.altitude_km = '650';
  const genericPath = fileURLToPath(new URL('../../requirements.sysml', import.meta.url));
  const generic = await readFile(genericPath, 'utf8');
  const post = (state = workspace, headers = {}) => fetch(`${base}/api/sysml`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify({ workspace: state }),
  });
  const response = await post();
  assert.equal(response.status, 200);
  assert.match(response.headers.get('content-disposition'), /mission-export\.sysml/);
  const source = await response.text();
  assert.match(source, /: FrameworkRequirements::OrbitPeriod/);
  assert.match(source, /: FrameworkRequirements::EPS02/);
  assert.match(source, /: FrameworkRequirements::EPS21/);
  assert.match(source, /: FrameworkRequirements::OrbitPeriodClosure/);
  assert.match(source, /: FrameworkRequirements::EPS89/);
  assert.doesNotMatch(source, /: FrameworkRequirements::(?:EPS01|EPS20|EPS22|EPS92)\s*\{/);
  assert.match(source, /attribute :>> 'altitude_km' = 650/);
  assert.match(source, /attribute :>> altitude_km = statement_/);
  assert.match(source, /RealFunctions::sqrt/);
  assert.doesNotMatch(source, /requirements-ui:data|NaN|undefined/);
  assert.equal(await readFile(modelPath, 'utf8'), original);
  assert.equal(await readFile(genericPath, 'utf8'), generic);
  assert.equal((await fetch(`${base}/api/sysml`)).status, 405);
  assert.equal((await post(workspace, { Origin: 'https://example.com' })).status, 403);
  const invalid = structuredClone(workspace); invalid.statements[0].condition = 'unknown(1)';
  assert.equal((await post(invalid)).status, 400);
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
