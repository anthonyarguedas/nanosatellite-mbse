import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { request as httpRequest } from 'node:http';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { createServer } from '../server.mjs';
import { emptyWorkspace } from '../model.mjs';
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
  workspace.statements.push({ key: 'r1', id: 'REQ001', context: 'external', affected: [], kind: 'Requirement', text: 'Operate for {x} months.', sources: ['s1'], condition: 'x >= 12', parameters: { x: 12, y: null, z: 0, a: null } });
  return workspace;
}

test('the server refuses to use a generic framework file as mission storage', () => {
  for (const name of ['external', 'mission', 'eps', 'catalog', 'cad']) {
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
  for (const path of ['/app.js', '/style.css', '/model.mjs', '/verification.mjs', '/verification-worker.js']) assert.equal((await fetch(base + path)).status, 200);
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
