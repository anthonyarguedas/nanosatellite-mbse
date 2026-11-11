import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { loadCotsFacts } from '../cots.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { blankWorkspace, MAX_VARIABLES, requirementMarkers, validateWorkspace } from '../model.mjs';
import { createSessions } from '../sessions.mjs';
import { canonicalWorkspace } from '../storage.mjs';
import { verificationMethods } from '../verification-methods.mjs';
import { createReportWorkspace, reportProfiles } from '../analyses/report-workspaces.mjs';
import { evaluateChecks } from './helpers.mjs';

const catalog = await loadCatalog(), definitions = await loadScriptCatalog();
const cotsFacts = { ti_tps63802dlar: (await loadCotsFacts('ti_tps63802dlar')).facts };
const reportRows = workspace => workspace.statements.filter(row => row.origin?.includes('REPORT-COVERAGE.md'));
const checks = workspace => evaluateChecks(workspace).filter(result => reportRows(workspace).some(row => row.key === result.key));

test('the audit accounts for all 23 framework and 20 EPS report requirements', async () => {
  const report = await readFile(new URL('../../../final_report/requirements.tex', import.meta.url), 'utf8');
  const eps = await readFile(new URL('../../../final_report/eps-requirements.tex', import.meta.url), 'utf8');
  const audit = await readFile(new URL('../analyses/REPORT-COVERAGE.md', import.meta.url), 'utf8');
  const frameworkIds = new Set([...report.matchAll(/^(FR-\d+) &/gm)].map(match => match[1]));
  const epsIds = new Set([...eps.matchAll(/^EPS-\d+.*?label\{epsreq:(EPS-\d+)\}/gm)].map(match => match[1]));
  assert.equal(frameworkIds.size, 23); assert.equal(epsIds.size, 20);
  assert.deepEqual(new Set([...audit.matchAll(/^\| (FR-\d+) \|/gm)].map(match => match[1])), frameworkIds);
  assert.deepEqual(new Set([...audit.matchAll(/^\| (EPS-\d+) \|/gm)].map(match => match[1])), epsIds);
});

test('all optional profiles are ordinary bounded version 14 workspaces with meaningful parameters and pending evidence', async () => {
  const originalCatalog = structuredClone(catalog), originalDefinitions = structuredClone(definitions);
  for (const profile of reportProfiles()) {
    const workspace = createReportWorkspace(catalog, definitions, profile.id, { cotsFacts });
    assert.equal(workspace.version, 14); assert.equal(workspace.expressionLanguage, 'python');
    assert.ok(workspace.variables.length <= MAX_VARIABLES, profile.id);
    const rows = reportRows(workspace);
    assert.ok(rows.length, profile.id);
    for (const row of rows) {
      const markers = requirementMarkers(row.text);
      assert.equal(markers.errors.length, 0); assert.ok(markers.names.length, row.id);
      assert.equal(row.text.split('.').length, 2, row.text);
      assert.ok(verificationMethods(row).length); assert.ok(row.rationale);
    }
    for (const script of workspace.scripts) {
      assert.ok(rows.some(row => verificationMethods(row).some(method => method.script === script.key)));
      for (const input of script.inputs) {
        if (input.type === 'boolean') {
          const binding = script.parameters[input.name];
          if (binding !== null) assert.match(binding, /^INP\d{3}\.current_A > 0$/);
        } else assert.match(script.parameters[input.name], /^INP\d{3}\./);
      }
    }
    const errors = checks(workspace).filter(result => !['pending'].includes(result.state));
    assert.deepEqual(errors, [], `${profile.id}: ${JSON.stringify(errors)}`);
    const canonical = await canonicalWorkspace(workspace, { catalog });
    assert.deepEqual(canonical.workspace, workspace, profile.id);
    validateWorkspace(JSON.parse(JSON.stringify(workspace)), catalog);
    assert.equal(Object.hasOwn(workspace, 'scriptResults'), false);
  }
  assert.deepEqual(catalog, originalCatalog); assert.deepEqual(definitions, originalDefinitions);
  assert.throws(() => createReportWorkspace(catalog, definitions, 'unknown'), /Choose a report assessment/);
  assert.throws(() => createReportWorkspace(catalog, [], 'energy'), /Register eps_energy_segment/);
  assert.throws(() => createReportWorkspace(catalog, definitions, 'cots-protection'), /Load the current COTS facts/);
});

test('sourced protection capability, threshold tolerance and recommended temperature criteria execute without script source', () => {
  const workspace = createReportWorkspace(catalog, definitions, 'cots-protection', { cotsFacts });
  assert.equal(workspace.scripts.length, 0); assert.equal(workspace.components.length, 1);
  const values = { ovp_trip_ceiling_V: '6', uvlo_trip_floor_V: '1.1', startup_source_V: '2', junction_temperature_K: '300' };
  for (const row of reportRows(workspace)) for (const [name, value] of Object.entries(values)) {
    if (row.text.includes(`$$${name}$$`)) row.parameters[name] = value;
  }
  assert.ok(checks(workspace).every(result => result.state === 'pass'));
  const ovp = reportRows(workspace).find(row => row.text.includes('$$ovp_trip_ceiling_V$$'));
  ovp.parameters.ovp_trip_ceiling_V = '5.5';
  assert.equal(checks(workspace).find(result => result.key === ovp.key).state, 'fail');
  workspace.components[0].facts[0].revision = '0'.repeat(64);
  assert.ok(checks(workspace).every(result => result.state === 'pending'));
  assert.ok(workspace.components[0].facts.every(fact => !Object.hasOwn(fact, 'value')));
});

test('charger and service port criteria reject violated numeric bounds', () => {
  const charger = createReportWorkspace(catalog, definitions, 'charger');
  const counts = reportRows(charger)[0];
  Object.assign(counts.parameters, { battery_series_count: '3', series_min: '1', series_max: '4' });
  assert.equal(checks(charger).find(result => result.key === counts.key).state, 'pass');
  counts.parameters.battery_series_count = '5';
  assert.equal(checks(charger).find(result => result.key === counts.key).state, 'fail');
  const ports = createReportWorkspace(catalog, definitions, 'interfaces');
  const logic = reportRows(ports).find(row => row.text.includes('$$output_low_max_V$$'));
  Object.assign(logic.parameters, { output_low_max_V: '0.4', output_high_min_V: '2.4', input_low_max_V: '0.8', input_high_min_V: '2' });
  assert.equal(checks(ports).find(result => result.key === logic.key).state, 'pass');
  logic.parameters.output_high_min_V = '1.5';
  assert.equal(checks(ports).find(result => result.key === logic.key).state, 'fail');
});

test('every numerical report profile executes its documented fixture through real requirement bindings and criteria', async () => {
  const examples = {};
  for (const [document, ids] of [
    ['MODELS.md', ['eps_sizing', 'eps_geometry', 'eps_fit', 'eps_ram']],
    ['PATHS.md', ['eps_power_path', 'eps_protection', 'eps_battery_step', 'eps_thermal']],
  ]) {
    const text = await readFile(new URL(`../analyses/${document}`, import.meta.url), 'utf8');
    const data = [...text.matchAll(/```json\n([\s\S]*?)\n```/g)].map(match => JSON.parse(match[1]));
    assert.equal(data.length, ids.length);
    ids.forEach((id, index) => { examples[id] = data[index]; });
  }
  for (const id of ['path', 'protection', 'battery', 'thermal', 'electrothermal', 'sizing', 'geometry', 'fit', 'ram']) {
    const workspace = createReportWorkspace(catalog, definitions, id);
    for (const script of workspace.scripts) for (const input of script.inputs) {
      const value = examples[script.definition][input.name];
      if (input.type === 'boolean') {
        if (script.parameters[input.name] === null) script.parameters[input.name] = value ? 'True' : 'False';
      } else {
        const [rowId, name] = script.parameters[input.name].split('.');
        const row = workspace.statements.find(row => row.id === rowId);
        if (row.parameters[name] === null) row.parameters[name] = String(value);
      }
    }
    for (const row of reportRows(workspace)) for (const [name, value] of Object.entries({
      dissipation_limit_W: '10', recovery_limit_s: '0.4', battery_loss_limit_W: '0.2',
      failure_probability_limit: '0.05', reliability_min: '0.95', conditional_probability_limit: '0.2',
    })) if (row.text.includes(`$$${name}$$`) && row.parameters[name] === null) row.parameters[name] = value;
    const original = structuredClone(workspace);
    let evidence;
    for (const script of workspace.scripts) {
      const result = await runScripts(workspace, script.key);
      assert.ok(Object.values(result.runs).every(run => run.state === 'value'), `${id}: ${JSON.stringify(result)}`);
      evidence = { ...result, runs: { ...evidence?.runs, ...result.runs } };
    }
    assert.deepEqual(workspace, original);
    const results = evaluateChecks(workspace, { scriptResults: evidence }).filter(result => reportRows(workspace).some(row => row.key === result.key));
    assert.ok(results.every(result => result.state === 'pass'), `${id}: ${JSON.stringify(results.filter(result => result.state !== 'pass'))}`);
    assert.ok(checks(JSON.parse(JSON.stringify(workspace))).every(result => result.state === 'pending'));
  }
});

test('report session creation leaves current data untouched and never runs registered source', async t => {
  const directory = await mkdtemp(join(tmpdir(), 'report-sessions-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const mission = join(directory, 'mission.json'), sentinel = join(directory, 'unexpected-execution');
  const source = JSON.stringify(blankWorkspace(), null, 2) + '\n';
  await writeFile(mission, source);
  const scriptsDirectory = join(directory, 'scripts'); await mkdir(scriptsDirectory);
  await writeFile(join(scriptsDirectory, 'eps_energy_segment.json'), await readFile(new URL('../scripts/eps_energy_segment.json', import.meta.url)));
  await writeFile(join(scriptsDirectory, 'eps_energy_segment.py'), `from pathlib import Path\nPath(${JSON.stringify(sentinel)}).write_text('unexpected')\nraise SystemExit(1)\n`);
  const tool = fileURLToPath(new URL('../tools/create-report-session.mjs', import.meta.url));
  const run = args => spawnSync(process.execPath, [tool, ...args], { encoding: 'utf8', timeout: 15000,
    env: { ...process.env, VERIFICATION_SCRIPTS_DIR: scriptsDirectory } });
  const listed = run(['--list']); assert.equal(listed.status, 0, listed.stderr); assert.match(listed.stdout, /cots-protection/);
  for (const profile of ['energy', 'charger', 'cots-protection']) {
    const result = run([profile, '--mission', mission, '--name', `${profile} test`]);
    assert.equal(result.status, 0, result.stderr); assert.match(result.stdout, /No analysis was executed/);
  }
  assert.equal(await readFile(mission, 'utf8'), source);
  await assert.rejects(() => readFile(sentinel), { code: 'ENOENT' });
  const duplicate = run(['energy', '--mission', mission, '--name', 'energy test']);
  assert.equal(duplicate.status, 1); assert.match(duplicate.stderr, /already exists/);
  const sessions = createSessions(mission, { catalog }), stored = await sessions.list();
  assert.equal(stored.length, 4);
  for (const session of stored.filter(session => session.id !== 'current')) {
    const workspace = (await (await sessions.get(session.id)).store.read()).workspace;
    assert.ok(checks(workspace).every(result => result.state === 'pending'));
    assert.equal(Object.hasOwn(workspace, 'scriptResults'), false);
  }
});
