import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { chmod, mkdir, mkdtemp, readFile, readdir, rm, stat, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { createEvaluationWorker } from '../evaluation-worker.mjs';
import { blankWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { createSessions } from '../sessions.mjs';
import { createStore, workspacePaths } from '../storage.mjs';

function fixture() {
  return { ...blankWorkspace(), variables: [{ name: 'x', type: 'float', unit: 'W' }, { name: 'count', type: 'integer' }],
    statements: [{ key: 'r1', id: 'REQ001', kind: 'Requirement', context: 'external', sources: [], affected: [],
      text: 'The draw shall not exceed $$x$$.', condition: 'count > 0', parameters: { x: '8 if mode == "Downlink" else 3', count: '2' } }],
    power: { modes: [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'downlink', name: 'Downlink', sunlight: 0, eclipse: 0 }], loads: [], links: [] } };
}
async function directory(t) { const path = await mkdtemp(join(tmpdir(), 'json-workspace-test-')); t.after(() => rm(path, { recursive: true, force: true })); return path; }
const readJSON = async path => JSON.parse(await readFile(path, 'utf8'));

test('workspaces are plain JSON with Python expressions and reopen without changing source text', async t => {
  const root = await directory(t), path = join(root, 'nested', 'mission.json');
  const store = createStore(path, { initialWorkspace: fixture() });
  const data = await store.read();
  assert.equal(data.modelName, 'mission.json'); assert.equal(data.workspace.expressionLanguage, 'python');
  assert.equal(data.workspace.version, WORKSPACE_VERSION); assert.deepEqual(await readJSON(path), data.workspace);
  assert.deepEqual(await readdir(join(root, 'nested')), ['mission.json']);
  data.workspace.statements[0].parameters.x = '  statistics.mean([2, 4, 6])  ';
  const saved = await store.save(data.workspace, data.revision);
  assert.deepEqual((await createStore(path).read()).workspace, saved.workspace);
  assert.equal((await readJSON(path)).statements[0].parameters.x, '  statistics.mean([2, 4, 6])  ');
});

test('new file creation is atomic and stale readers cannot replace another writer', async t => {
  const root = await directory(t), path = join(root, 'shared.json');
  const first = createStore(path, { initialWorkspace: fixture() }), second = createStore(path, { initialWorkspace: fixture() });
  const [a, b] = await Promise.all([first.read(), second.read()]); assert.equal(a.revision, b.revision);
  a.workspace.statements[0].rationale = 'First save.'; b.workspace.statements[0].rationale = 'Second save.';
  const results = await Promise.allSettled([first.save(a.workspace, a.revision), second.save(b.workspace, b.revision)]);
  assert.equal(results.filter(result => result.status === 'fulfilled').length, 1);
  assert.equal(results.find(result => result.status === 'rejected').reason.status, 409);
  assert.equal((await readJSON(path)).statements[0].rationale, 'First save.');
});

test('invalid Python drafts stay editable and unsupported operators never receive another interpretation', async t => {
  const root = await directory(t), path = join(root, 'draft.json'), data = fixture();
  data.statements[0].parameters.x = '1 +';
  const store = createStore(path, { initialWorkspace: data }), original = await store.read();
  await store.save(original.workspace, original.revision);
  assert.equal((await store.read()).workspace.statements[0].parameters.x, '1 +');
  const worker = createEvaluationWorker(); t.after(() => worker.close());
  data.statements[0].parameters.x = '2 ^ 3';
  assert.equal((await worker.evaluate(data)).results[0].parameters.x.state, 'error');
  data.statements[0].condition = 'true';
  assert.equal((await worker.evaluate(data)).results[0].state, 'error');
});

test('malformed JSON, unsupported versions and non-JSON storage paths fail without changing data', async t => {
  const root = await directory(t), path = join(root, 'mission.json'); await writeFile(path, '{broken JSON');
  const store = createStore(path);
  await assert.rejects(() => store.read(), /invalid JSON/); assert.equal(await readFile(path, 'utf8'), '{broken JSON');
  await writeFile(path, JSON.stringify({ ...fixture(), version: 1 }));
  await assert.rejects(() => store.read(), /format 1 differs/);
  assert.throws(() => workspacePaths(join(root, 'mission.sysml')), /Choose a .json workspace/);
  assert.throws(() => workspacePaths(join(root, 'notes.txt')), /Choose a .json workspace/);
  const actual = join(root, 'actual.json'); await writeFile(actual, JSON.stringify(fixture()));
  await rm(path); await symlink(actual, path); await assert.rejects(() => store.read(), /regular workspace file/);
});

test('JSON saves retain permissions, reject cross-file revisions and respect external save locks', async t => {
  const root = await directory(t), firstPath = join(root, 'first.json'), secondPath = join(root, 'second.json');
  await writeFile(firstPath, JSON.stringify(fixture())); await writeFile(secondPath, JSON.stringify(fixture())); await chmod(firstPath, 0o640);
  const store = createStore(firstPath), a = await store.read(), other = createStore(secondPath), b = await other.read();
  assert.notEqual(a.revision, b.revision); await assert.rejects(() => other.save(a.workspace, a.revision), error => error.status === 409);
  const locked = `${firstPath}.lock`; await writeFile(locked, '{"pid":0}');
  await assert.rejects(() => store.save(a.workspace, a.revision), error => error.status === 409 && /locked/.test(error.message));
  assert.equal(await readFile(locked, 'utf8'), '{"pid":0}'); await rm(locked);
  a.workspace.statements[0].parameters.x = 'sum(i for i in range(5))';
  const mask = process.umask(0o077); let saved;
  try { saved = await store.save(a.workspace, a.revision); } finally { process.umask(mask); }
  assert.equal((await stat(firstPath)).mode & 0o777, 0o640);
  await writeFile(firstPath, JSON.stringify({ ...fixture(), statements: [] }));
  await assert.rejects(() => store.save(saved.workspace, saved.revision), error => error.status === 409);
  assert.deepEqual((await readJSON(firstPath)).statements, []);
  assert.equal((await readdir(root)).some(name => name.endsWith('.lock') || name.endsWith('.tmp')), false);
});

test('separate Node processes cannot overwrite each other with the same revision', async t => {
  const root = await directory(t), path = join(root, 'shared.json'), store = createStore(path, { initialWorkspace: fixture() }), current = await store.read();
  const program = `import {createStore} from ${JSON.stringify(new URL('../storage.mjs', import.meta.url).href)}; let source=''; for await (const chunk of process.stdin) source+=chunk; const data=JSON.parse(source); try { await createStore(data.path).save(data.workspace,data.revision); console.log(JSON.stringify({status:200})); } catch(error) { console.log(JSON.stringify({status:error.status})); }`;
  const save = value => new Promise((resolve, reject) => {
    const child = spawn(process.execPath, ['--input-type=module', '-e', program], { stdio: ['pipe', 'pipe', 'pipe'] });
    let output = '', errors = ''; child.stdout.on('data', chunk => { output += chunk; }); child.stderr.on('data', chunk => { errors += chunk; });
    child.on('error', reject); child.on('close', code => { if (code !== 0) reject(new Error(errors)); else { try { resolve(JSON.parse(output)); } catch (error) { reject(error); } } });
    const workspace = structuredClone(current.workspace); workspace.statements[0].parameters.x = String(value);
    child.stdin.end(JSON.stringify({ path, workspace, revision: current.revision }));
  });
  assert.deepEqual((await Promise.all([save(2), save(3)])).map(result => result.status).sort(), [200, 409]);
});

test('deleted named sessions remain missing across restarts', async t => {
  const root = await directory(t), sessions = createSessions(join(root, 'mission.json'));
  const created = await sessions.create({ name: 'Study', template: 'blank' });
  const file = join(root, 'sessions', created.session.id, `${created.session.id}.json`);
  const opened = await sessions.get(created.session.id); assert.deepEqual((await opened.store.read()).workspace, created.workspace);
  await rm(file);
  await assert.rejects(() => opened.store.read(), error => error.status === 404);
  await assert.rejects(() => createSessions(join(root, 'mission.json')).get(created.session.id), error => error.status === 404);
});
