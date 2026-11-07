import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { addScenarioAnalysis, createAnalysisTestWorkspace, createMPPTWorkspace } from '../analyses/workspaces.mjs';
import { loadCatalog } from '../catalog.mjs';
import { addPowerLimits, blankWorkspace, emptyWorkspace, requirementMarkers, rewriteRowReferences, validateWorkspace } from '../model.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { createSessions } from '../sessions.mjs';
import { runKey, verificationMethods } from '../verification-methods.mjs';
import { evaluateChecks } from './helpers.mjs';

const catalog = await loadCatalog(), definitions = await loadScriptCatalog();
const python = process.env.VERIFICATION_PYTHON || 'python3';
const period = 2 * Math.PI * Math.sqrt((6378 + 500) ** 3 / 398601);
const scenario = {
  altitude_km: 500, earth_radius_km: 6378, mu_km3_s2: 398601, inclination_deg: 0,
  raan_deg: 0, argument_latitude_deg: 0, epoch_jd: 2460754.5, duration_s: 2 * period, step_s: 2,
  earth_j2: 0, solar_constant_W_m2: 1361, panel_normal_radial: 1, panel_normal_along: 0,
  panel_normal_cross: 0, sun_tracking: true,
};
const mppt = {
  voc_ref_V: 8, isc_ref_A: 1.1, vmp_ref_V: 6.4, imp_ref_A: 1,
  reference_irradiance_W_m2: 1361, reference_temperature_C: 28,
  voltage_temp_coeff_V_C: -0.02, current_temp_coeff_per_C: 0.0005, voltage_log_coefficient_V: 0.25,
  irradiance_start_W_m2: 1361, irradiance_end_W_m2: 680.5, temperature_start_C: 28, temperature_end_C: 50,
  change_time_s: 60, duration_s: 120, sample_period_s: 0.1, voltage_step_V: 0.05, initial_voltage_V: 3,
  tracking_min_V: 2, tracking_max_V: 8, conversion_efficiency: 0.9, settling_relative_band: 0.02, settling_hold_s: 5,
};
function execute(id, inputs) {
  return spawnSync(python, ['-I', '-B', fileURLToPath(new URL(`../scripts/${id}.py`, import.meta.url))], {
    input: JSON.stringify({ inputs, requirements: {}, mode: null }), encoding: 'utf8', timeout: 15000,
  });
}
function simulate(id, inputs) {
  const result = execute(id, inputs);
  assert.equal(result.error, undefined);
  assert.equal(result.status, 0, result.stderr);
  const values = JSON.parse(result.stdout), definition = definitions.find(item => item.id === id);
  assert.deepEqual(Object.keys(values).sort(), definition.outputs.map(output => output.name).sort());
  for (const output of definition.outputs) {
    const value = values[output.name];
    if (value === null) continue;
    assert.equal(typeof value, output.type === 'boolean' ? 'boolean' : 'number', output.name);
    if (typeof value === 'number') assert.ok(Number.isFinite(value), output.name);
    if (output.type === 'integer') assert.ok(Number.isSafeInteger(value), output.name);
  }
  return values;
}
const close = (actual, expected, tolerance = 1e-9) => assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);

function populatedMPPT() {
  const workspace = createMPPTWorkspace(catalog, definitions), script = workspace.scripts[0];
  for (const [name, value] of Object.entries(mppt)) {
    const [id, field] = script.parameters[name].split('.');
    workspace.statements.find(row => row.id === id).parameters[field] = String(value);
  }
  for (const [name, value] of Object.entries({ input_absolute_max_V: 9, source_current_limit_A: 1.2,
    tracking_efficiency_min: 0.95, settling_limit_s: 15, delivered_energy_min_J: 400 })) {
    const row = workspace.statements.find(row => requirementMarkers(row.text).names.includes(name));
    row.parameters[name] = String(value);
  }
  return workspace;
}

test('illumination agrees with circular beta-zero geometry within sampling and finite solar disk effects', () => {
  const values = simulate('scenario_illumination', scenario);
  const cylindrical = period * Math.asin(6378 / 6878) / Math.PI;
  close(values.orbit_period_s, period);
  close(values.sunlight_s + values.eclipse_s, scenario.duration_s, 1e-7);
  assert.ok(Math.abs(values.longest_eclipse_s - cylindrical) < 20);
  assert.ok(values.penumbra_s > 0);
  assert.ok(values.sunlit_fraction > 0.6 && values.sunlit_fraction < 0.65);
  close(values.incident_energy_J_m2, values.mean_irradiance_W_m2 * scenario.duration_s, 1e-6);
  assert.ok(values.min_irradiance_W_m2 === 0 && values.max_irradiance_W_m2 > 1300);
  const refined = simulate('scenario_illumination', { ...scenario, step_s: 1 });
  assert.ok(Math.abs(refined.longest_eclipse_s - values.longest_eclipse_s) <= 2);
  assert.ok(Math.abs(refined.mean_irradiance_W_m2 - values.mean_irradiance_W_m2) < 1);
});

test('high beta orbit has continuous sunlight, while panel orientation still determines received flux', () => {
  const highBeta = { ...scenario, inclination_deg: 90, raan_deg: 90 };
  const tracking = simulate('scenario_illumination', highBeta);
  assert.equal(tracking.eclipse_s, 0);
  assert.equal(tracking.sunlit_fraction, 1);
  assert.ok(tracking.min_beta_deg > 89);
  const back = simulate('scenario_illumination', { ...highBeta, sun_tracking: false, panel_normal_radial: 0, panel_normal_cross: -1 });
  assert.equal(back.mean_irradiance_W_m2, 0);
  assert.equal(back.sunlight_s, tracking.sunlight_s);
  const front = simulate('scenario_illumination', { ...highBeta, sun_tracking: false, panel_normal_radial: 0, panel_normal_cross: 1 });
  assert.ok(front.mean_irradiance_W_m2 > 1300);
});

test('solar distance, epoch and optional J2 node drift affect the assessed environment', () => {
  const january = simulate('scenario_illumination', { ...scenario, epoch_jd: 2460679.5 });
  const july = simulate('scenario_illumination', { ...scenario, epoch_jd: 2460860.5 });
  assert.ok(january.max_irradiance_W_m2 / july.max_irradiance_W_m2 > 1.06);
  const input = { ...scenario, inclination_deg: 98, raan_deg: 30, duration_s: 86400, step_s: 20 };
  const unperturbed = simulate('scenario_illumination', input);
  const perturbed = simulate('scenario_illumination', { ...input, earth_j2: 0.00108263 });
  assert.ok(Math.abs(unperturbed.min_beta_deg - perturbed.min_beta_deg) > 0.5);
});

test('P&O approaches the MPP, reacquires after an environmental step and conserves energy', () => {
  const values = simulate('mppt_po', mppt);
  assert.ok(values.tracking_efficiency > 0.95 && values.tracking_efficiency <= 1 + 1e-12);
  assert.ok(values.delivered_energy_J > 400);
  assert.ok(values.settled);
  assert.ok(values.settling_time_s < 15);
  assert.ok(values.voltage_reversals > 0);
  assert.ok(values.tracked_energy_J <= values.attainable_energy_J + 1e-8);
  assert.ok(values.attainable_energy_J <= values.available_energy_J + 1e-8);
  close(values.delivered_energy_J, values.tracked_energy_J * 0.9);
  close(values.max_mpp_voltage_V, 6.4);
  close(values.min_mpp_voltage_V, 6.4 - 0.02 * 22 + 0.25 * Math.log(0.5));
  close(values.max_open_circuit_voltage_V, 8);
  close(values.max_short_circuit_current_A, 1.1);
  const expected = 60 * 6.4 + 60 * values.min_mpp_voltage_V * (0.5 * 1.011);
  close(values.available_energy_J, expected, 1e-8);
  assert.equal(values.sample_count, 1200);
});

test('tracking-window losses and failure to settle stay visible', () => {
  const clipped = simulate('mppt_po', { ...mppt, tracking_max_V: 4 });
  assert.ok(clipped.attainable_energy_J < clipped.available_energy_J);
  assert.ok(clipped.capture_efficiency < 0.85);
  assert.equal(clipped.settled, false);
  assert.equal(clipped.settling_time_s, null);
  assert.ok(clipped.max_operating_voltage_V <= 4);
  const oscillating = simulate('mppt_po', { ...mppt, voltage_step_V: 0.5, settling_relative_band: 0.00001 });
  assert.equal(oscillating.settled, false);
});

test('dark phases produce zero power and all-dark tracking evidence stays unresolved', () => {
  const dark = simulate('mppt_po', { ...mppt, irradiance_start_W_m2: 0, irradiance_end_W_m2: 0 });
  assert.equal(dark.delivered_energy_J, 0);
  assert.equal(dark.tracking_efficiency, null);
  assert.equal(dark.capture_efficiency, null);
  assert.equal(dark.min_mpp_voltage_V, null);
  assert.equal(dark.settled, false);
  for (const change_time_s of [0, mppt.duration_s]) {
    const values = simulate('mppt_po', { ...mppt, change_time_s });
    assert.ok(values.delivered_energy_J > 0);
    assert.ok(values.settled);
  }
  const recovery = simulate('mppt_po', { ...mppt, irradiance_start_W_m2: 0 });
  assert.ok(recovery.delivered_energy_J > 0);
  assert.ok(recovery.settled);
});

test('invalid physical inputs, invalid sampling and excessive work fail with diagnostics', () => {
  for (const [id, base, changes, message] of [
    ['scenario_illumination', scenario, { altitude_km: 0 }, /positive/],
    ['scenario_illumination', scenario, { inclination_deg: 181 }, /inclination/],
    ['scenario_illumination', scenario, { epoch_jd: 1 }, /1900 through 2100/],
    ['scenario_illumination', scenario, { step_s: period }, /200000 steps/],
    ['scenario_illumination', scenario, { step_s: 0.001 }, /200000 steps/],
    ['scenario_illumination', scenario, { sun_tracking: false, panel_normal_radial: 0 }, /nonzero/],
    ['mppt_po', mppt, { vmp_ref_V: 9 }, /Reference points/],
    ['mppt_po', mppt, { irradiance_start_W_m2: -1 }, /nonnegative/],
    ['mppt_po', mppt, { conversion_efficiency: 1.1 }, /Conversion efficiency/],
    ['mppt_po', mppt, { temperature_end_C: -274 }, /absolute zero/],
    ['mppt_po', mppt, { voltage_temp_coeff_V_C: -1 }, /adjusted I-V/],
    ['mppt_po', mppt, { change_time_s: 60.05 }, /integer multiple/],
    ['mppt_po', mppt, { duration_s: 1e7 }, /200000 MPPT samples/],
    ['mppt_po', mppt, { initial_voltage_V: 10 }, /initial voltage/],
  ]) {
    const result = execute(id, { ...base, ...changes });
    assert.equal(result.status, 1, `${id}: ${JSON.stringify(changes)}`);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, message);
  }
});

test('MPPT requirements bind every model input and every acceptance result through the existing interface', async () => {
  const empty = createMPPTWorkspace(catalog, definitions), script = empty.scripts[0];
  assert.equal(empty.variables.length, 28);
  assert.equal(empty.statements.length, 10);
  assert.ok(Object.values(script.parameters).every(value => /^MPT\d{3}\./.test(value)));
  assert.ok(empty.statements.every(row => requirementMarkers(row.text).names.length));
  assert.ok(evaluateChecks(empty).every(result => result.state === 'pending'));
  const pending = await runScripts(empty, script.key);
  assert.equal(pending.runs[runKey(script.key, null)].state, 'pending');
  assert.equal(pending.runs[runKey(script.key, null)].executedAt, undefined);
  const workspace = populatedMPPT(), original = structuredClone(workspace);
  const evidence = await runScripts(workspace, workspace.scripts[0].key);
  assert.equal(Object.values(evidence.runs)[0].state, 'value', Object.values(evidence.runs)[0].message);
  assert.deepEqual(workspace, original);
  assert.ok(evaluateChecks(workspace, { scriptResults: evidence }).every(result => result.state === 'pass'));
  const voltage = workspace.statements.find(row => row.id === 'MPT006');
  voltage.parameters.input_absolute_max_V = '7';
  const rerun = await runScripts(workspace, workspace.scripts[0].key);
  assert.equal(evaluateChecks(workspace, { scriptResults: rerun }).find(result => result.key === voltage.key).state, 'fail');
  const restored = JSON.parse(JSON.stringify(workspace));
  validateWorkspace(restored, catalog);
  assert.ok(evaluateChecks(restored).filter(result => ['MPT005', 'MPT006', 'MPT007', 'MPT008', 'MPT009', 'MPT010']
    .includes(restored.statements.find(row => row.key === result.key).id)).every(result => result.state === 'pending'));
});

test('the combined test bench executes both scripts from Run MPPT and passes all linked requirements', async () => {
  const workspace = createAnalysisTestWorkspace(catalog, definitions), original = structuredClone(workspace);
  assert.equal(workspace.variables.length, 37);
  assert.equal(workspace.statements.length, 15);
  assert.equal(workspace.scripts.length, 2);
  const mpptScript = workspace.scripts.find(script => script.definition === 'mppt_po');
  const illumination = workspace.scripts.find(script => script.definition === 'scenario_illumination');
  assert.ok(workspace.scripts.every(script => Object.values(script.parameters).every(value => typeof value === 'string' && value.trim())));
  assert.ok(Object.values(mpptScript.parameters).every(value => /^MPT\d{3}\./.test(value)));
  const environment = workspace.statements.find(row => row.id === 'MPT003');
  assert.equal(environment.parameters.irradiance_start_W_m2, `${illumination.id}.max_irradiance_W_m2`);
  assert.equal(environment.parameters.irradiance_end_W_m2, `${illumination.id}.mean_irradiance_W_m2`);
  const checksWithoutEvidence = evaluateChecks(workspace);
  assert.ok(checksWithoutEvidence.some(result => result.state === 'pending'));
  assert.ok(checksWithoutEvidence.every(result => ['pass', 'pending'].includes(result.state)));
  const evidence = await runScripts(workspace, mpptScript.key);
  assert.deepEqual(workspace, original);
  assert.deepEqual(Object.values(evidence.runs).map(run => [run.script, run.state]), [[illumination.key, 'value'], [mpptScript.key, 'value']]);
  const flux = evidence.runs[runKey(illumination.key, null)].values;
  const tracker = evidence.runs[runKey(mpptScript.key, null)].values;
  assert.ok(flux.longest_eclipse_s > 2100 && flux.longest_eclipse_s < 2200);
  assert.ok(flux.mean_irradiance_W_m2 > 850 && flux.mean_irradiance_W_m2 < 860);
  assert.ok(tracker.tracking_efficiency > 0.98 && tracker.tracking_efficiency < 1);
  assert.ok(tracker.delivered_energy_J > 530 && tracker.delivered_energy_J < 550);
  assert.ok(tracker.settled && tracker.settling_time_s < 10);
  assert.ok(evaluateChecks(workspace, { scriptResults: evidence }).every(result => result.state === 'pass'));
  const restored = JSON.parse(JSON.stringify(workspace));
  validateWorkspace(restored, catalog);
  const scriptRows = restored.statements.filter(row => verificationMethods(row).some(method => method.script));
  assert.ok(evaluateChecks(restored).filter(result => scriptRows.some(row => row.key === result.key)).every(result => result.state === 'pending'));
  workspace.statements.find(row => row.definition === 'FrameworkRequirements::OrbitPeriod').parameters.altitude_km = '600';
  assert.ok(evaluateChecks(workspace, { scriptResults: evidence }).filter(result => scriptRows.some(row => row.key === result.key)).every(result => result.state === 'pending'));
});

test('scenario configurations fit a full Generic EPS workspace, survive ID changes and leave prior equations intact', async () => {
  const original = emptyWorkspace(catalog);
  original.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 }];
  addPowerLimits(original);
  assert.equal(original.variables.length, 62);
  const orbit = original.statements.find(row => row.id === 'ORB001');
  orbit.parameters.altitude_km = '500';
  rewriteRowReferences(original, new Map([['ORB001', 'MIS099']])); orbit.id = 'MIS099';
  const before = structuredClone(original);
  const workspace = addScenarioAnalysis(original, catalog, definitions);
  assert.deepEqual(original, before);
  assert.equal(workspace.variables.length, 64);
  const script = workspace.scripts[0];
  assert.equal(script.parameters.altitude_km, 'MIS099.altitude_km');
  for (const [name, value] of Object.entries(scenario)) {
    if (!['altitude_km', 'earth_radius_km', 'mu_km3_s2'].includes(name)) script.parameters[name] = typeof value === 'boolean' ? 'True' : String(value);
  }
  workspace.statements.find(row => row.id === 'SCN001').parameters.eclipse_limit_s = '2400';
  workspace.statements.find(row => row.id === 'SCN002').parameters.irradiance_min_W_m2 = '800';
  workspace.power.modes = [{ key: 'mode-a', name: 'Nominal', sunlight: 100, eclipse: 100 }, { key: 'mode-b', name: 'Back panel', sunlight: 0, eclipse: 0 }];
  script.parameters.sun_tracking = 'mode == "Nominal"';
  script.parameters.panel_normal_radial = '0';
  script.parameters.panel_normal_cross = '-1';
  script.parameters.inclination_deg = '90';
  script.parameters.raan_deg = '90';
  const evidence = await runScripts(workspace, script.key);
  assert.ok(Object.values(evidence.runs).every(run => run.state === 'value'));
  const checks = evaluateChecks(workspace, { scriptResults: evidence });
  const eclipse = checks.find(result => result.key === workspace.statements.find(row => row.id === 'SCN001').key);
  const flux = checks.find(result => result.key === workspace.statements.find(row => row.id === 'SCN002').key);
  assert.equal(eclipse.state, 'pass');
  assert.equal(flux.state, 'fail');
  assert.deepEqual(flux.modes.map(mode => mode.state), ['pass', 'fail']);
  assert.deepEqual(workspace.statements.find(row => row.id === 'ORB002').parameters, { ...before.statements.find(row => row.id === 'ORB002').parameters,
    eclipse_limit_s: null, irradiance_min_W_m2: null });
});

test('scenario attachment handles blank sessions, namespace collisions, ambiguous orbits and exhausted columns', () => {
  const empty = addScenarioAnalysis(blankWorkspace(), catalog, definitions);
  assert.ok(Object.values(empty.scripts[0].parameters).every(value => value === null));
  const original = emptyWorkspace(catalog), orbit = original.statements.find(row => row.id === 'ORB001');
  original.statements.push({ ...structuredClone(orbit), key: 'second-orbit', id: 'ORB099' });
  assert.throws(() => addScenarioAnalysis(original, catalog, definitions), /Several orbit/);
  const chosen = addScenarioAnalysis(original, catalog, definitions, { orbitKey: 'second-orbit' });
  assert.equal(chosen.scripts[0].parameters.altitude_km, 'ORB099.altitude_km');
  const full = blankWorkspace();
  full.variables = Array.from({ length: 64 }, (_, index) => ({ name: `value_${index}`, type: 'float' }));
  const before = structuredClone(full);
  assert.throws(() => addScenarioAnalysis(full, catalog, definitions), /64 shared parameter/);
  assert.deepEqual(full, before);
  const collision = blankWorkspace();
  collision.variables.push({ name: 'eclipse_limit_s', type: 'integer' });
  assert.throws(() => addScenarioAnalysis(collision, catalog, definitions), /conflicting variable/);
});

test('analysis CLI saves independent named sessions without executing source or modifying the current mission', async t => {
  const directory = await mkdtemp(join(tmpdir(), 'analysis-sessions-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const modelPath = join(directory, 'mission.json'), source = JSON.stringify(emptyWorkspace(catalog), null, 2) + '\n';
  await writeFile(modelPath, source);
  const tool = fileURLToPath(new URL('../tools/create-analysis-session.mjs', import.meta.url));
  for (const kind of ['demo', 'mppt', 'scenario']) {
    const result = spawnSync(process.execPath, [tool, kind, '--mission', modelPath, '--name', `${kind} study`], { encoding: 'utf8', timeout: 15000 });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /Open the Session picker/);
  }
  assert.equal(await readFile(modelPath, 'utf8'), source);
  const missingPath = join(directory, 'absent.json');
  const missing = spawnSync(process.execPath, [tool, 'scenario', '--mission', missingPath], { encoding: 'utf8', timeout: 15000 });
  assert.equal(missing.status, 1);
  assert.match(missing.stderr, /missing/);
  await assert.rejects(() => readFile(missingPath), { code: 'ENOENT' });
  const sessions = createSessions(modelPath, { catalog }), listed = await sessions.list();
  assert.equal(listed.length, 4);
  for (const session of listed.filter(session => session.id !== 'current')) {
    const { store } = await sessions.get(session.id), { workspace } = await store.read();
    assert.equal(workspace.scripts.length, session.name === 'demo study' ? 2 : 1);
    assert.ok(workspace.scripts.every(script => workspace.statements.some(row => verificationMethods(row).some(method => method.script === script.key))));
    assert.equal(workspace.scriptResults, undefined);
  }
  const invalid = spawnSync(process.execPath, [tool, 'demo', '--mission', modelPath, '--from', 'current'], { encoding: 'utf8', timeout: 15000 });
  assert.equal(invalid.status, 1);
  assert.match(invalid.stderr, /only to scenario copies/);
});
