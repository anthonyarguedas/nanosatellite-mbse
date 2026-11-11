import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { createEvaluationWorker } from '../evaluation-worker.mjs';
import { addElementChildren, addPowerLimits, addResourceBudgets, blankWorkspace, emptyWorkspace, MAX_VARIABLES,
  requirementParameterNames, validateWorkspace } from '../model.mjs';
import { canonicalWorkspace, createStore } from '../storage.mjs';
import { createSessions } from '../sessions.mjs';

const catalog = await loadCatalog();
const templates = catalog.flatMap(type => type.requirements ?? []);
const additions = templates.filter(template => template.autoPopulate);
const models = new Set(additions.map(template => template.model));
const genericRows = workspace => workspace.statements.filter(row => models.has(row.definition));
const eps = workspace => workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem'));
const row = (workspace, name, owner = eps(workspace).key) => workspace.statements.find(row => row.definition === `FrameworkRequirements::${name}` && row.context === owner);
const legacyCatalog = catalog.map(type => ({ ...type, ...(type.requirements ? { requirements: type.requirements.filter(template => !template.autoPopulate) } : {}) }));

async function directory(t) {
  const path = await mkdtemp(join(tmpdir(), 'generic-eps-studies-'));
  t.after(() => rm(path, { recursive: true, force: true })); return path;
}
function legacyWorkspace() {
  const workspace = addResourceBudgets(emptyWorkspace(legacyCatalog)); workspace.resourceBudgets = true;
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }]; addPowerLimits(workspace);
  const orbit = workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = ' 500 + 25 '; orbit.rationale = 'Preserve this mission interpretation.';
  workspace.statements.push({ key: 'existing-custom', id: 'EPS013', kind: 'Requirement', context: eps(workspace).key,
    text: 'The existing study shall retain $$x$$.', condition: 'x > 0', sources: [orbit.key], affected: [],
    rationale: 'Existing custom requirement.', parameters: Object.fromEntries(workspace.variables.map(variable => [variable.name, variable.name === 'x' ? '72' : null])) });
  return workspace;
}

test('Generic EPS contains all report requirements and uses the requirement list itself as study guidance', async t => {
  assert.equal(templates.length, 76); assert.equal(additions.length, 49);
  const report = await readFile(new URL('../../../final_report/eps-requirements.tex', import.meta.url), 'utf8');
  for (const [, id] of report.matchAll(/label\{epsreq:EPS-(\d\d)\}/g)) {
    assert.ok(templates.some(template => template.name === `EPS${id}`), `Missing generic EPS-${id}`);
  }
  const workspace = emptyWorkspace(catalog), thermal = row(workspace, 'EPS13');
  assert.equal(genericRows(workspace).length, 49); assert.ok(thermal.affected.length);
  assert.deepEqual(new Set(requirementParameterNames(workspace, thermal, catalog)),
    new Set(['temp_limit_min_K', 'temp_limit_max_K', 'assessed_temp_min_K', 'assessed_temp_max_K']));
  assert.ok(thermal.rationale.includes('eps_thermal'));
  for (const template of additions) {
    const current = workspace.statements.find(row => row.definition === template.model);
    assert.ok(current.origin && current.affected.length && current.rationale);
    for (const [name, expression] of Object.entries(template.parameters)) {
      assert.equal(current.parameters[name], expression);
      if (expression !== null) assert.doesNotMatch(expression, /^\s*[+-]?[\d.]+\s*$/, `${current.id}.${name}`);
    }
  }
  assert.deepEqual(workspace.scripts, []); assert.deepEqual(workspace.components, []);
  const worker = createEvaluationWorker(); t.after(() => worker.close());
  const results = (await worker.evaluate(workspace)).results;
  assert.ok(results.filter(result => genericRows(workspace).some(row => row.key === result.key)).every(result => result.state === 'unset'));
  assert.ok(results.every(result => result.state !== 'error' && result.state !== 'pass'));
});

test('existing sessions backfill generic studies without changing entered data, identities or files on read', async t => {
  const root = await directory(t), path = join(root, 'mission.json'), original = legacyWorkspace();
  assert.equal(original.variables.length, 64);
  const source = JSON.stringify(original, null, 2) + '\n'; await writeFile(path, source);
  const store = createStore(path, { catalog }), opened = await store.read(), workspace = opened.workspace;
  assert.equal(genericRows(workspace).length, 49);
  assert.equal(await readFile(path, 'utf8'), source);
  for (const old of original.statements) {
    const actual = workspace.statements.find(row => row.key === old.key);
    assert.deepEqual({ ...actual, parameters: old.parameters }, old);
    for (const [name, value] of Object.entries(old.parameters)) assert.equal(actual.parameters[name], value);
  }
  assert.deepEqual(workspace.elements, original.elements); assert.deepEqual(workspace.power, original.power);
  assert.deepEqual(workspace.components, original.components); assert.deepEqual(workspace.scripts, original.scripts);
  assert.notEqual(row(workspace, 'EPS13').id, 'EPS013');
  assert.equal(workspace.statements.find(row => row.id === 'EPS013').key, 'existing-custom');
  assert.equal(new Set(workspace.statements.map(row => row.id)).size, workspace.statements.length);
  assert.deepEqual(new Set(workspace.requirementSeeds[eps(workspace).key]), models);
  assert.deepEqual((await store.read()).workspace, workspace);
  validateWorkspace(workspace, catalog);
});

test('edits and deliberate deletions survive saves, copies, restarts and future generic additions', async t => {
  const root = await directory(t), path = join(root, 'mission.json');
  await writeFile(path, JSON.stringify(legacyWorkspace()));
  const store = createStore(path, { catalog }), opened = await store.read(), workspace = opened.workspace;
  const thermal = row(workspace, 'EPS13'), deleted = row(workspace, 'EPS13Discharging');
  thermal.text = 'The selected thermal node shall stay below $$temp_limit_max_K$$.';
  thermal.parameters.temp_limit_max_K = '310'; thermal.rationale = 'Reviewed temperature allocation.';
  thermal.condition = 'assessed_temp_max_K <= temp_limit_max_K';
  workspace.statements = workspace.statements.filter(row => row.key !== deleted.key);
  const saved = await store.save(workspace, opened.revision);
  const restored = (await createStore(path, { catalog }).read()).workspace;
  assert.deepEqual(restored, saved.workspace); assert.equal(row(restored, 'EPS13Discharging'), undefined);
  assert.equal(row(restored, 'EPS13').parameters.temp_limit_max_K, '310');
  const sessions = createSessions(path, { catalog });
  const copy = await sessions.create({ name: 'Independent study', template: 'copy', workspace: restored });
  assert.deepEqual(copy.workspace, restored);
  const futureCatalog = structuredClone(catalog), power = futureCatalog.find(type => type.role === 'eps');
  power.requirements.push({ ...structuredClone(additions.find(template => template.name === 'EPS13')),
    name: 'FutureThermal', model: 'FrameworkRequirements::FutureThermal', id: 'FUT001' });
  const before = await readFile(path, 'utf8');
  const future = (await createStore(path, { catalog: futureCatalog }).read()).workspace;
  assert.ok(row(future, 'FutureThermal')); assert.equal(row(future, 'EPS13Discharging'), undefined);
  assert.equal(row(future, 'EPS13').text, thermal.text);
  assert.equal(await readFile(path, 'utf8'), before);
});

test('every EPS gets independent blank study values while sessions without EPS retain empty tables', async t => {
  const workspace = emptyWorkspace(catalog), primary = eps(workspace);
  row(workspace, 'EPS13').parameters.temp_limit_max_K = '320';
  const backup = { ...primary, key: 'backup-eps', id: 'BKP', name: 'Backup power' };
  workspace.elements.push(backup); addElementChildren(workspace, backup, catalog);
  assert.equal(genericRows(workspace).length, 98);
  assert.equal(row(workspace, 'EPS13', backup.key).parameters.temp_limit_max_K, null);
  assert.equal(row(workspace, 'EPS13').parameters.temp_limit_max_K, '320');
  assert.ok(row(workspace, 'EPS13Charging', backup.key).sources.includes(row(workspace, 'EPS13', backup.key).key));
  assert.deepEqual(new Set(workspace.requirementSeeds[backup.key]), models);
  const root = await directory(t), sessions = createSessions(join(root, 'mission.json'), { catalog });
  const blank = await sessions.create({ name: 'Blank', template: 'blank' });
  assert.deepEqual(blank.workspace.statements, []); assert.deepEqual(blank.workspace.elements, []);
  const generic = await sessions.create({ name: 'Generic', template: 'generic-eps' });
  assert.equal(genericRows(generic.workspace).length, 49);
});

test('numeric capacity and compact mode results support the full generic workbook without changing editor behavior', async t => {
  const worker = createEvaluationWorker(); t.after(() => worker.close());
  const full = blankWorkspace(); full.variables = Array.from({ length: MAX_VARIABLES }, (_, i) => ({ name: `input_${i}`, type: 'float' }));
  validateWorkspace(full, catalog); assert.deepEqual((await worker.evaluate(full)).results, []);
  full.variables.push({ name: 'one_too_many', type: 'float' });
  assert.throws(() => validateWorkspace(full, catalog), /256 variable/);
  await assert.rejects(() => worker.evaluate(full), /at most 256/);
  const workspace = addResourceBudgets(emptyWorkspace(catalog));
  workspace.power.modes = Array.from({ length: 24 }, (_, index) => ({ key: `mode${index}`, name: `Mode ${index}`, sunlight: index ? 0 : 100, eclipse: index ? 0 : 100 }));
  addPowerLimits(workspace);
  const results = await worker.evaluate(workspace), thermal = results.results.find(result => result.key === row(workspace, 'EPS13').key);
  assert.equal(thermal.parameters.assessed_temp_max_K.state, 'unset');
  assert.equal(thermal.modes.length, 24);
  assert.ok(JSON.stringify(results).length < 16 * 1024 * 1024);
  assert.ok(thermal.modes.every(result => result.state === 'unset'));
  assert.ok(results.results.every(result => result.state !== 'error'));
  const requirement = row(workspace, 'EPS13');
  requirement.parameters.assessed_temp_max_K = '300 if mode == "Mode 0" else 310';
  requirement.parameters.temp_limit_max_K = '320';
  requirement.condition = 'assessed_temp_max_K <= temp_limit_max_K';
  const populated = (await worker.evaluate(workspace)).results.find(result => result.key === requirement.key);
  assert.equal(populated.state, 'pass');
  assert.equal(populated.parameters.assessed_temp_max_K.state, 'varying');
  assert.equal(populated.modes[0].parameters.assessed_temp_max_K.value, 300);
  assert.equal(populated.modes[1].parameters.assessed_temp_max_K.value, 310);
  assert.equal(populated.parameters.temp_limit_min_K.state, 'unset');
});

test('generic thermal assessments require explicit study evidence and report known violations', async t => {
  const worker = createEvaluationWorker(); t.after(() => worker.close());
  const values = { assessed_temp_min_K: 270, assessed_temp_max_K: 300, temp_limit_min_K: 260, temp_limit_max_K: 310 };
  const assess = values => worker.request({ operation: 'catalog_assessment', definition: 'EPS13', values });
  assert.equal((await assess(values)).state, 'pending');
  assert.equal((await assess({ ...values, applicable_conditions_assessed: true })).state, 'pass');
  assert.equal((await assess({ ...values, assessed_temp_max_K: 315 })).state, 'fail');
  assert.equal((await assess({ ...values, applicable_conditions_assessed: false })).state, 'fail');
});
