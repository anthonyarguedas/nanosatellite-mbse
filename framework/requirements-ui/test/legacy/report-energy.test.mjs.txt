import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { createReportWorkspace } from '../analyses/report-workspaces.mjs';
import { runKey } from '../verification-methods.mjs';
import { evaluateChecks } from './helpers.mjs';

const catalog = await loadCatalog(), definitions = await loadScriptCatalog();
const definition = definitions.find(item => item.id === 'eps_energy_segment');
const sample = {
  duration_s: 100, source_power_W: 0, source_efficiency: 1, load_power_W: 2, load_efficiency: 1,
  battery_voltage_V: 1, energy_capacity_J: 1000, charge_capacity_C: 1000, energy_initial_J: 500,
  soc_initial: 0.5, energy_reserve_J: 200, soc_min: 0.2, charge_efficiency: 1, discharge_efficiency: 1,
  coulomb_charge_efficiency: 1, coulomb_discharge_efficiency: 1, charge_current_limit_A: 10,
  discharge_current_limit_A: 10, charge_allowed: true, temperature_C: 20, charge_temp_min_C: 0,
  charge_temp_max_C: 45, discharge_temp_min_C: -20, discharge_temp_max_C: 60, surplus_capacity_W: 10,
  shunt_surplus: false,
};
function execute(inputs) {
  return spawnSync(process.env.VERIFICATION_PYTHON || 'python3', ['-I', '-B', fileURLToPath(new URL('../scripts/eps_energy_segment.py', import.meta.url))], {
    input: JSON.stringify({ inputs, requirements: {}, mode: null }), encoding: 'utf8', timeout: 5000,
  });
}
function simulate(changes = {}) {
  const input = { ...sample, ...changes }, result = execute(input);
  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout);
  assert.deepEqual(Object.keys(output).sort(), definition.outputs.map(item => item.name).sort());
  for (const item of definition.outputs) {
    assert.equal(typeof output[item.name], item.type === 'boolean' ? 'boolean' : 'number', item.name);
    if (item.type !== 'boolean') assert.ok(Number.isFinite(output[item.name]), item.name);
  }
  close(input.energy_initial_J + output.source_energy_J,
    output.energy_end_J + output.served_energy_J + output.loss_energy_J + output.curtailed_energy_J);
  return output;
}
function close(value, expected, tolerance = 1e-9) { assert.ok(Math.abs(value - expected) <= tolerance, `${value} != ${expected}`); }
function bind(workspace, script, name, expression) {
  const input = script.inputs.find(item => item.name === name);
  assert.ok(input, name);
  if (input.type === 'boolean') script.parameters[name] = expression;
  else {
    const [id, variable] = script.parameters[name].split('.');
    workspace.statements.find(row => row.id === id).parameters[variable] = expression;
  }
}
function populated(profile = 'energy') {
  const workspace = createReportWorkspace(catalog, definitions, profile);
  for (const [index, script] of workspace.scripts.entries()) {
    for (const [name, value] of Object.entries({ ...sample, source_power_W: index ? 4 : 0 })) {
      if (index && ['energy_initial_J', 'soc_initial', 'energy_capacity_J', 'charge_capacity_C'].includes(name)) continue;
      bind(workspace, script, name, typeof value === 'boolean' ? value ? 'True' : 'False' : String(value));
    }
  }
  for (const row of workspace.statements) {
    for (const [name, value] of Object.entries({ required_service_s: '100', closure_tolerance_J: '0', dod_max: '0.8' })) {
      if (row.text.includes(`$$${name}$$`)) row.parameters[name] = value;
    }
  }
  return workspace;
}
const assessmentChecks = (workspace, evidence) => evaluateChecks(workspace, { scriptResults: evidence })
  .filter(result => workspace.statements.find(row => row.key === result.key).origin?.includes('REPORT-COVERAGE.md'));

test('energy and coulomb balances remain separate and conserve energy at declared boundaries', () => {
  const eclipse = simulate();
  close(eclipse.energy_end_J, 300); close(eclipse.soc_end, 0.3);
  close(eclipse.service_duration_s, 100); close(eclipse.unserved_energy_J, 0);
  assert.ok(eclipse.energy_reserve_ok && eclipse.soc_reserve_ok);
  const inefficient = simulate({ source_power_W: 1, source_efficiency: 0.8, load_efficiency: 0.8,
    discharge_efficiency: 0.9, coulomb_discharge_efficiency: 0.95 });
  close(inefficient.energy_end_J, 500 - 170 / 0.9);
  close(inefficient.soc_end, 0.5 - 170 / 0.95 / 1000);
  assert.notEqual(inefficient.soc_end, inefficient.energy_end_J / 1000);
  const charging = simulate({ source_power_W: 6, charge_efficiency: 0.9, coulomb_charge_efficiency: 0.95 });
  close(charging.energy_end_J, 860); close(charging.soc_end, 0.88);
});

test('full energy or full charge terminates charging and distinguishes shunting from foregone harvest', () => {
  const fullEnergy = simulate({ source_power_W: 12 });
  close(fullEnergy.energy_end_J, 1000); close(fullEnergy.accepted_charge_energy_J, 500);
  close(fullEnergy.curtailed_energy_J, 500); close(fullEnergy.peak_surplus_W, 10);
  const fullCharge = simulate({ source_power_W: 12, soc_initial: 0.9 });
  close(fullCharge.soc_end, 1); close(fullCharge.energy_end_J, 600);
  close(fullCharge.curtailed_energy_J, 900);
  const shunted = simulate({ source_power_W: 12, soc_initial: 0.9, shunt_surplus: true, surplus_capacity_W: 9 });
  close(shunted.shunt_energy_J, 900); close(shunted.curtailed_energy_J, 0);
  assert.equal(shunted.surplus_supported, false);
});

test('shortages, independent reserves, current limits and thermal restrictions produce explicit failed findings', () => {
  const depleted = simulate({ duration_s: 400 });
  close(depleted.energy_end_J, 0); close(depleted.soc_end, 0);
  close(depleted.service_duration_s, 250); close(depleted.unserved_energy_J, 300);
  assert.equal(depleted.energy_reserve_ok, false); assert.equal(depleted.soc_reserve_ok, false);
  const currentLimited = simulate({ discharge_current_limit_A: 1 });
  close(currentLimited.unserved_energy_J, 100); close(currentLimited.service_duration_s, 0);
  close(currentLimited.peak_discharge_current_A, 1);
  const initiallyBelowReserve = simulate({ energy_reserve_J: 600, soc_min: 0.6 });
  assert.equal(initiallyBelowReserve.energy_reserve_ok, false); assert.equal(initiallyBelowReserve.soc_reserve_ok, false);
  const cold = simulate({ source_power_W: 4, temperature_C: -10 });
  close(cold.accepted_charge_energy_J, 0); assert.equal(cold.charge_temperature_ok, false);
  const disabled = simulate({ source_power_W: 4, temperature_C: -10, charge_allowed: false });
  close(disabled.accepted_charge_energy_J, 0); assert.equal(disabled.charge_temperature_ok, true);
  assert.equal(simulate({ temperature_C: -30 }).discharge_temperature_ok, false);
  close(simulate({ load_power_W: 0, discharge_current_limit_A: 0 }).service_duration_s, 100);
});

test('invalid domains fail without emitting partial execution evidence', () => {
  for (const change of [{ duration_s: 0 }, { source_efficiency: 0 }, { energy_capacity_J: -1 },
    { energy_initial_J: 1001 }, { soc_initial: 1.1 }, { charge_capacity_C: 0 }, { charge_temp_min_C: 46 },
    { discharge_current_limit_A: -1 }, { temperature_C: -274 }, { charge_allowed: 1 }]) {
    const result = execute({ ...sample, ...change });
    assert.equal(result.status, 1, JSON.stringify(change));
    assert.equal(result.stdout, ''); assert.ok(result.stderr.trim());
  }
});

test('chronological profiles chain exact states through existing dependency execution and stay pending without fresh evidence', async () => {
  const blank = createReportWorkspace(catalog, definitions, 'energy');
  assert.ok(assessmentChecks(blank).every(result => result.state === 'pending'));
  const pending = await runScripts(blank, blank.scripts.at(-1).key);
  assert.ok(Object.values(pending.runs).every(result => result.state === 'pending'));
  for (const profile of ['energy', 'survival']) {
    const workspace = populated(profile), original = structuredClone(workspace);
    const evidence = await runScripts(workspace, workspace.scripts.at(-1).key);
    assert.deepEqual(workspace, original);
    assert.deepEqual(Object.values(evidence.runs).map(result => result.state), ['value', 'value']);
    const first = evidence.runs[runKey(workspace.scripts[0].key, null)].values;
    const last = evidence.runs[runKey(workspace.scripts[1].key, null)].values;
    close(first.energy_end_J, 300); close(last.energy_end_J, 500); close(last.soc_end, 0.5);
    assert.ok(assessmentChecks(workspace, evidence).every(result => result.state === 'pass'), JSON.stringify(assessmentChecks(workspace, evidence)));
    assert.ok(assessmentChecks(JSON.parse(JSON.stringify(workspace))).every(result => result.state === 'pending'));
    bind(workspace, workspace.scripts[0], 'load_power_W', '9');
    assert.ok(assessmentChecks(workspace, evidence).every(result => result.state === 'pending'));
    const rerun = await runScripts(workspace, workspace.scripts.at(-1).key);
    assert.ok(assessmentChecks(workspace, rerun).some(result => result.state === 'fail'));
  }
});

test('modes are independent cases with explicit chronological links inside each mode', async () => {
  const workspace = populated();
  workspace.power.modes = [{ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 },
    { key: 'fault', name: 'Fault', sunlight: 0, eclipse: 0 }];
  bind(workspace, workspace.scripts[0], 'load_power_W', '2 if mode == "Nominal" else 9');
  const evidence = await runScripts(workspace, workspace.scripts.at(-1).key);
  assert.equal(Object.values(evidence.runs).length, 4);
  assert.ok(Object.values(evidence.runs).every(result => result.state === 'value'));
  const failures = assessmentChecks(workspace, evidence).filter(result => result.state === 'fail');
  assert.ok(failures.length);
  assert.ok(failures.every(result => result.modes.find(mode => mode.mode === 'nominal').state === 'pass'));
});
