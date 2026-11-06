import assert from 'node:assert/strict';
import { cp, mkdir, mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { createEvaluationWorker } from '../evaluation-worker.mjs';
import { emptyWorkspace, requirementMarkers, validateWorkspace } from '../model.mjs';

async function directory(t) {
  const path = await mkdtemp(join(tmpdir(), 'python-catalog-test-'));
  t.after(() => rm(path, { recursive: true, force: true }));
  return path;
}
const templates = catalog => catalog.flatMap(type => type.requirements ?? []);

test('Python owns the same domain hierarchy, parameterized requirements, units, sources and allocations', async () => {
  const current = await loadCatalog();
  assert.equal(current.length, 52); assert.equal(templates(current).length, 27);
  assert.equal(new Set(current.map(type => type.model)).size, 52);
  for (const type of current) if (type.parent) assert.ok(current.some(parent => parent.model === type.parent));
  assert.deepEqual(templates(current).map(template => template.id).sort(), ['ORB001','ORB002','ORB003','SIZ001','SIZ002','SIZ003','SIZ004','SIZ005','SIZ006','SIZ007','SIZ008','SIZ011','SIZ013','SIZ014','SIZ016','EPS002','EPS008','EPS009','EPS011','EPS019','EPS021','EPS047','EPS052','EPS053','EPS078','EPS088','EPS089'].sort());
  for (const after of templates(current)) {
    assert.ok(after.origin && after.affected.length && Object.keys(after.parameters).length);
    assert.equal(requirementMarkers(after.text).errors.length, 0);
    assert.ok(after.assessment.condition);
    for (const input of after.assessment.inputs) {
      assert.equal(input.value, null, 'Assessment evidence must never default to true.');
      assert.equal(input.type, 'boolean'); assert.equal(after.attributes[input.name], 'Boolean');
    }
    for (const source of [after.condition, ...Object.values(after.parameters)].filter(Boolean)) assert.doesNotMatch(source, /\^|RealFunctions::|TrigFunctions::|\?/, after.id);
  }
  assert.deepEqual(Object.keys(templates(current).find(template => template.name === 'EPS09').parameters), ['required_cycles','supported_cycles','dod_max','nominal_dod']);
  const instance = emptyWorkspace(current);
  assert.doesNotThrow(() => validateWorkspace(instance, current));
  assert.equal(instance.statements.length, 27);
  const props = current.find(type => type.role === 'eps').properties;
  assert.deepEqual(props.map(property => property.name), ['power_consumption_W', 'power_consumption']);
  assert.ok(props.every(property => property.unit === 'W' && property.value === null));
  // A caller editing its projection cannot mutate the reusable definitions.
  current[0].name = 'Local edit'; assert.equal((await loadCatalog())[0].name, 'Orbit');
});

test('Python sizing expressions reproduce the reference equations across the complete calculation chain', async t => {
  const current = await loadCatalog();
  const worker = createEvaluationWorker(); t.after(() => worker.close());
  const inputs = {
    OrbitPeriod: { altitude_km: 500 }, LoadEnergy: { sunlight_power_W: 10, eclipse_power_W: 8, sunlight_duty: 0.6, eclipse_duty: 0.5 },
    MinimumPanelPower: { sunlight_efficiency: 0.8, eclipse_efficiency: 0.65 }, SolarCellPower: { cell_eol_V: 2.4, cell_eol_A: 0.5 },
    SolarCellCount: { installed_cells: 100 }, MissionCycles: { lifetime_years: 2, days_per_year: 365.25 },
    CycleLife: { cycle_a: 5000, cycle_b: -1, dod_max: 0.3, fit_dod_min: 0.05, fit_dod_max: 0.8 },
    MinimumBatteryEnergy: { degradation_margin: 0.2 }, BatteryCapacityScreen: { pack_bol_J: 100000, retained_energy_factor: 0.8 },
  };
  const workspace = emptyWorkspace(current); workspace.expressionLanguage = 'python';
  for (const [name, parameters] of Object.entries(inputs)) {
    const row = workspace.statements.find(row => row.definition === `FrameworkRequirements::${name}`);
    Object.assign(row.parameters, Object.fromEntries(Object.entries(parameters).map(([name, value]) => [name, String(value)])));
  }
  const after = await worker.evaluate(workspace);
  const period = 2 * Math.PI * Math.sqrt((6378 + 500) ** 3 / 398601);
  const sunlight = (0.5 + Math.acos(6378 / (6378 + 500)) / Math.PI) * period;
  const expectedBattery = 8 * 0.5 * (period - sunlight) / 0.3 * 1.2;
  const batteries = after.results.find(row => row.key.endsWith('MinimumBatteryEnergy'));
  assert.equal(batteries.state, 'pass');
  assert.ok(Math.abs(batteries.values.battery_min_J - expectedBattery) < 1e-8);
  assert.equal(after.results.find(row => row.key.endsWith('BatteryCapacityScreen')).state, 'pass');
});

test('Python requirement models retain executable acceptance predicates and leave evidence unbound', async t => {
  const worker = createEvaluationWorker(); t.after(() => worker.close());
  const assess = (definition, values) => worker.request({ operation: 'catalog_assessment', definition, values });
  assert.equal((await assess('EPS08', { battery_min_J: 100, pack_bol_J: 120 })).state, 'pass');
  assert.equal((await assess('EPS08', { battery_min_J: 100, pack_bol_J: 80 })).state, 'fail');
  assert.equal((await assess('EPS08', { battery_min_J: 100 })).state, 'pending');
  const numeric = { sunlight_s: 10, panel_min_W: 2, sunlight_generation_J: 30 };
  assert.equal((await assess('EPS02', numeric)).state, 'pending');
  assert.equal((await assess('EPS02', { ...numeric, applicable_conditions_assessed: false })).state, 'fail');
  assert.equal((await assess('EPS02', { ...numeric, applicable_conditions_assessed: true })).state, 'pass');
  assert.equal((await assess('EPS02', { ...numeric, applicable_conditions_assessed: 1 })).state, 'error');
  assert.equal((await assess('EPS21', { required_data_bytes: 1, available_data_bytes: 2, all_hosts_and_tasks_assessed: true, required_program_bytes: 2.5 })).state, 'error');
  await assert.rejects(() => assess('Unknown', {}), /existing Python requirement/);
});

test('Python catalog validation rejects invalid declarations, unresolved references and conflicting units', async t => {
  const root = await directory(t), copied = join(root, 'worker');
  await cp(new URL('../worker/', import.meta.url), copied, { recursive: true });
  const path = join(copied, 'catalog_data.py'), original = await readFile(path, 'utf8');
  const cases = [
    ['REQUIREMENTS = (replace(REQUIREMENTS[0], text="No numeric marker."), *REQUIREMENTS[1:])', /prose must reference/],
    ['REQUIREMENTS = (replace(REQUIREMENTS[0], condition="unknown_value > 0"), *REQUIREMENTS[1:])', /Unknown variable/],
    ['REQUIREMENTS = (replace(REQUIREMENTS[0], derives_from=("Missing",)), *REQUIREMENTS[1:])', /invalid derivation/],
    ['REQUIREMENTS = (replace(REQUIREMENTS[0], parameters=(replace(REQUIREMENTS[0].parameters[0], kind="boolean"), *REQUIREMENTS[0].parameters[1:])), *REQUIREMENTS[1:])', /must be numeric/],
    ['REQUIREMENTS = (replace(REQUIREMENTS[0], parameters=(replace(REQUIREMENTS[0].parameters[0], unit="m"), *REQUIREMENTS[0].parameters[1:])), *REQUIREMENTS[1:])', /inconsistent catalog units/],
    ['ELEMENTS = (replace(ELEMENTS[0], parent="Missing"), *ELEMENTS[1:])', /missing catalog parent/],
  ];
  for (const [change, expected] of cases) {
    await writeFile(path, original + '\nfrom dataclasses import replace\n' + change + '\n');
    const worker = createEvaluationWorker({ path: join(copied, 'main.py') });
    try { await assert.rejects(() => worker.request({ operation: 'catalog' }), expected); }
    finally { worker.close(); }
  }
});

test('the app starts, edits, evaluates and saves Generic EPS without any framework SysML files', async t => {
  const root = await directory(t), target = join(root, 'requirements-ui');
  const original = fileURLToPath(new URL('../', import.meta.url));
  await cp(original, target, { recursive: true, filter: source => !source.startsWith(join(original, 'test')) && !source.includes('__pycache__') });
  await mkdir(join(root, 'cots'));
  for (const name of ['products.tsv', 'pins.tsv']) await cp(new URL(`../../cots/${name}`, import.meta.url), join(root, 'cots', name));
  assert.equal((await readdir(root)).some(name => name.endsWith('.sysml')), false);
  const { createServer } = await import(pathToFileURL(join(target, 'server.mjs')));
  const modelPath = join(root, 'missions', 'mission.json');
  const server = createServer({ modelPath }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }));
  const base = `http://127.0.0.1:${server.address().port}`;
  const initial = await (await fetch(base + '/api/workspace')).json();
  assert.equal(initial.workspace.expressionLanguage, 'python'); assert.equal(initial.workspace.statements.length, 27);
  assert.equal(initial.catalog.length, 52); assert.equal(initial.modelName, 'mission.json');
  assert.ok(initial.products.length); assert.equal(initial.error, undefined);
  const orbit = initial.workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod');
  orbit.parameters.altitude_km = '500';
  const evaluated = await fetch(base + '/api/evaluate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace: initial.workspace }) });
  const results = await evaluated.json(); assert.equal(evaluated.status, 200);
  const result = results.results.find(row => row.key === orbit.key); assert.equal(result.state, 'pass'); assert.ok(result.values.orbit_period_s > 5000);
  const saved = await fetch(base + '/api/workspace', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ workspace: initial.workspace, revision: initial.revision }) });
  assert.equal(saved.status, 200);
  assert.equal(JSON.parse(await readFile(modelPath, 'utf8')).statements.find(row => row.key === orbit.key).parameters.altitude_km, '500');
  assert.deepEqual(await readdir(dirname(modelPath)), ['mission.json']);
  const created = await fetch(base + '/api/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: 'EPS copy', template: 'generic-eps' }) });
  const data = await created.json(); assert.equal(created.status, 201);
  const folder = join(root, 'missions', 'sessions', data.session.id);
  assert.deepEqual((await readdir(folder)).sort(), [`${data.session.id}.json`, 'session.json'].sort());
  assert.equal(data.workspace.statements.length, 27);
});
