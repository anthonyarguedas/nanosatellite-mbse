import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { loadScriptCatalog } from '../python.mjs';

const definitions = await loadScriptCatalog();
const python = process.env.VERIFICATION_PYTHON || 'python3';
const power = {
  source_voltage_V: 8, rail_voltage_V: 5, efficiency: 0.8, idle_power_W: 0.1,
  steady_current_A: 1, pulse_current_A: 2, pulse_replaces_steady: false, pulse_duration_s: 0.5,
  path_resistance_ohm: 0.1, diode_drop_V: 0.2, load_min_V: 4.4, load_max_V: 5.1,
  input_min_V: 6, input_max_V: 10, startup_min_V: 7, dropout_V: 0.2, topology_code: 0,
  duty_min: 0.05, duty_max: 0.95, battery_cont_A: 1, battery_pulse_A: 3,
  converter_in_cont_A: 1, converter_in_pulse_A: 3, converter_out_cont_A: 1.2,
  converter_out_pulse_A: 4, switch_cont_A: 1.2, switch_pulse_A: 4,
  pulse_rating_duration_s: 1, startup_time_s: 0.1, startup_limit_s: 0.2,
  connection_cont_A: 1.2, connection_pulse_A: 4,
};
const protection = {
  nominal_voltage_V: 4, fault_voltage_V: 2.5, recovery_voltage_V: 4,
  legitimate_current_A: 1, fault_current_A: 4, recovery_current_A: 1,
  nominal_duration_s: 1, fault_duration_s: 1, recovery_duration_s: 1, step_s: 0.1,
  uv_trip_V: 3, uv_reset_V: 3.5, ov_trip_V: 5.5, ov_reset_V: 5,
  oc_trip_A: 2, oc_reset_A: 1.5, trip_delay_s: 0.2, reset_delay_s: 0.3,
  nominal_command_on: true, fault_command_on: true, recovery_command_on: true,
  nominal_inhibited: false, fault_inhibited: false, recovery_inhibited: false,
  processor_available: true, autonomous_protection: true, autonomous_inhibit: true,
  processor_off_output_on: true, auto_reset: true,
  i2t_limit_A2s: 4, peak_limit_A: 5, interruption_limit_s: 0.25,
};
const battery = {
  capacity_C: 3600, initial_soc: 0.8, current_A: -1, ocv_at_zero_V: 3, ocv_slope_V: 1,
  r0_ohm: 0.05, r1_ohm: 0.1, c1_F: 100, initial_polarization_V: 0, duration_s: 60,
  voltage_limits_known: true, voltage_min_V: 2.5, voltage_max_V: 4.5,
  soc_limits_known: true, soc_min: 0.2, soc_max: 1,
};
const thermal = {
  initial_temp_K: 280, ambient_temp_K: 260, dissipation_W: 2, heater_W: 3,
  heat_capacity_J_K: 100, conductance_W_K: 0.5, duration_s: 200,
  temp_limits_known: true, temp_min_K: 270, temp_max_K: 300,
  charge_active: true, charge_limits_known: true, charge_min_K: 273, charge_max_K: 290,
};
const examples = { eps_power_path: power, eps_protection: protection, eps_battery_step: battery, eps_thermal: thermal };
const close = (actual, expected, tolerance = 1e-9) => assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);
function execute(id, inputs) {
  return spawnSync(python, ['-I', '-B', fileURLToPath(new URL(`../scripts/${id}.py`, import.meta.url))], {
    cwd: tmpdir(), input: JSON.stringify({ inputs, requirements: {}, mode: null }), encoding: 'utf8', timeout: 10000,
  });
}
function simulate(id, inputs) {
  const result = execute(id, inputs);
  assert.equal(result.error, undefined);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '');
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
function rejected(id, inputs, message) {
  const result = execute(id, inputs);
  assert.equal(result.status, 1, `${id}: ${result.stderr}`);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, message);
}

test('four registered standalone typed scalar interfaces exactly match protocol and bounds', async () => {
  for (const [id, inputs] of Object.entries(examples)) {
    const definition = definitions.find(item => item.id === id);
    assert.ok(definition, id);
    assert.ok(definition.inputs.length <= 32 && definition.outputs.length <= 32);
    assert.deepEqual(Object.keys(inputs).sort(), definition.inputs.map(input => input.name).sort());
    const names = [...definition.inputs, ...definition.outputs].map(field => field.name);
    assert.equal(new Set(names).size, names.length);
    assert.ok(names.every(name => name.length <= 40));
    for (const field of definition.inputs) {
      assert.equal(typeof inputs[field.name], field.type === 'boolean' ? 'boolean' : 'number');
      if (field.type === 'integer') assert.ok(Number.isSafeInteger(inputs[field.name]));
    }
    const source = await readFile(new URL(`../scripts/${id}.py`, import.meta.url), 'utf8');
    assert.match(source, /if __name__ == "__main__":/);
    assert.doesNotMatch(source, /^from \./m);
    simulate(id, inputs);
    rejected(id, { ...inputs, unexpected: 0 }, /exactly/);
    const missing = { ...inputs }; delete missing[definition.inputs[0].name];
    rejected(id, missing, /exactly/);
    const bool = definition.inputs.find(field => field.type === 'boolean');
    rejected(id, { ...inputs, [bool.name]: 1 }, /boolean/);
    const number = definition.inputs.find(field => field.type === 'float');
    rejected(id, { ...inputs, [number.name]: true }, /numeric/);
  }
});

test('rail loss propagation uses simultaneous demand and independent energy accounting', () => {
  const v = simulate('eps_power_path', power);
  close(v.steady_input_W, 5 / 0.8 + 0.1);
  close(v.pulse_input_W, 15 / 0.8 + 0.1);
  close(v.steady_source_A, 6.35 / 8);
  close(v.pulse_source_A, 18.85 / 8);
  close(v.steady_load_V, 4.7); close(v.pulse_load_V, 4.5);
  close(v.steady_path_loss_W, 0.3); close(v.pulse_path_loss_W, 1.5);
  close(v.pulse_input_W, v.pulse_terminal_W + v.pulse_converter_loss_W + v.pulse_path_loss_W);
  close(v.duty_required, 5 / 7.8);
  assert.equal(v.path_ok, true);
  const replace = simulate('eps_power_path', { ...power, pulse_replaces_steady: true });
  close(replace.pulse_rail_W, 10); close(replace.pulse_load_V, 4.6);
  assert.ok(replace.pulse_source_A < v.pulse_source_A);
});

test('all three topology codes expose unbounded duty and dropout violations, never clip them', () => {
  const boost = simulate('eps_power_path', { ...power, source_voltage_V: 3, topology_code: 1 });
  close(boost.duty_required, 1 - 2.8 / 5);
  assert.equal(boost.envelope_ok, true); assert.equal(boost.input_ok, false);
  const wrongBoost = simulate('eps_power_path', { ...power, topology_code: 1 });
  assert.ok(wrongBoost.duty_required < 0); assert.equal(wrongBoost.envelope_ok, false);
  const buckboost = simulate('eps_power_path', { ...power, topology_code: 2 });
  close(buckboost.duty_required, 5 / 12.8);
  const scaled = simulate('eps_power_path', { ...power, topology_code: 2, source_voltage_V: 1e308,
    rail_voltage_V: 1e308, steady_current_A: 0, pulse_current_A: 0 });
  close(scaled.duty_required, 0.5);
  const wrongBuck = simulate('eps_power_path', { ...power, rail_voltage_V: 10 });
  assert.ok(wrongBuck.duty_required > 1); assert.equal(wrongBuck.envelope_ok, false);
  const dropout = simulate('eps_power_path', { ...power, dropout_V: 8 });
  assert.equal(dropout.duty_required, null); assert.equal(dropout.envelope_ok, false);
  assert.equal(dropout.path_ok, false);
});

test('rail operational violations preserve raw currents, voltage, losses and false findings', () => {
  for (const [change, finding] of [
    [{ battery_cont_A: 0.1 }, 'battery_current_ok'],
    [{ converter_in_pulse_A: 0.1 }, 'converter_current_ok'],
    [{ converter_out_pulse_A: 2.9 }, 'converter_current_ok'],
    [{ switch_pulse_A: 2.9 }, 'switch_current_ok'],
    [{ connection_pulse_A: 2.9 }, 'connection_current_ok'],
    [{ pulse_rating_duration_s: 0.4 }, 'pulse_duration_ok'],
    [{ startup_min_V: 9 }, 'startup_ok'],
    [{ startup_time_s: 0.3 }, 'startup_time_ok'],
    [{ duty_max: 0.5 }, 'envelope_ok'],
    [{ load_min_V: 4.6 }, 'pulse_voltage_ok'],
  ]) {
    const v = simulate('eps_power_path', { ...power, ...change });
    assert.equal(v[finding], false, finding); assert.equal(v.path_ok, false);
    close(v.pulse_source_A, 18.85 / 8);
  }
  const collapse = simulate('eps_power_path', { ...power, path_resistance_ohm: 10 });
  assert.ok(collapse.pulse_load_V < 0 && collapse.pulse_terminal_W < 0);
  assert.equal(collapse.pulse_voltage_ok, false);
  close(collapse.pulse_input_W, collapse.pulse_terminal_W + collapse.pulse_path_loss_W + collapse.pulse_converter_loss_W);
});

test('MIL trip/reset times, state transitions and stress match independent rectangular-current calculation', () => {
  const v = simulate('eps_protection', protection);
  assert.equal(v.sample_count, 30); assert.equal(v.trip_count, 1); assert.equal(v.reset_count, 1);
  assert.equal(v.transition_count, 2); assert.equal(v.final_output_on, true);
  close(v.first_trip_time_s, 1.2); close(v.first_reset_time_s, 2.3);
  close(v.fault_interruption_s, 0.2); close(v.recovery_time_s, 0.3);
  close(v.fault_i2t_A2s, 4 ** 2 * 0.2); close(v.fault_peak_A, 4);
  close(v.recovery_unserved_s, 0.3); close(v.fault_output_on_s, 0.2);
  assert.equal(v.nuisance_free, true); assert.equal(v.protection_ok, true);
});

test('MIL UV/OV/OC equality trips, zero delay and quantized noninteger delays are explicit', () => {
  for (const changes of [
    { fault_voltage_V: 3, fault_current_A: 1 },
    { fault_voltage_V: 5.5, fault_current_A: 1 },
    { fault_voltage_V: 4, fault_current_A: 2 },
  ]) {
    const v = simulate('eps_protection', { ...protection, ...changes });
    close(v.fault_interruption_s, 0.2); assert.equal(v.fault_seen, true);
  }
  const immediate = simulate('eps_protection', { ...protection, trip_delay_s: 0, reset_delay_s: 0 });
  close(immediate.fault_interruption_s, 0); close(immediate.recovery_time_s, 0);
  close(immediate.fault_i2t_A2s, 0); close(immediate.fault_peak_A, 0);
  const tinyDelay = simulate('eps_protection', { ...protection, trip_delay_s: 1e-12 });
  close(tinyDelay.fault_interruption_s, 0.1);
  const delayed = simulate('eps_protection', { ...protection, trip_delay_s: 0.21 });
  close(delayed.fault_interruption_s, 0.3); close(delayed.fault_i2t_A2s, 4.8);
  assert.equal(delayed.interruption_ok, false); assert.equal(delayed.stress_ok, false);
  assert.equal(delayed.protection_ok, false);
});

test('MIL hysteresis, nonresetting faults and latched reset retain unrecovered outcomes', () => {
  for (const change of [
    { recovery_voltage_V: 3.25 }, { recovery_voltage_V: 5.25 },
    { recovery_current_A: 1.75 }, { recovery_voltage_V: 2.5 }, { auto_reset: false },
  ]) {
    const v = simulate('eps_protection', { ...protection, ...change });
    assert.equal(v.recovery_time_s, null); assert.equal(v.reset_count, 0);
    assert.equal(v.final_latched, true); assert.equal(v.recovery_observed, false);
    assert.equal(v.final_output_on, false);
  }
  for (const recovery_voltage_V of [3.5, 5]) {
    const v = simulate('eps_protection', { ...protection, recovery_voltage_V, recovery_current_A: 1.5 });
    close(v.recovery_time_s, 0.3);
  }
  const neverTrips = simulate('eps_protection', { ...protection, trip_delay_s: 2 });
  assert.equal(neverTrips.fault_interruption_s, null);
  assert.equal(neverTrips.interruption_ok, false); assert.equal(neverTrips.trip_count, 0);
});

test('MIL nuisance evidence covers the nominal legitimate step, including boundary trips', () => {
  const nuisance = simulate('eps_protection', { ...protection, legitimate_current_A: 2 });
  assert.equal(nuisance.nuisance_free, false); assert.equal(nuisance.nominal_trip_count, 1);
  close(nuisance.nominal_unserved_s, 0.8);
  const boundary = simulate('eps_protection', { ...protection, legitimate_current_A: 2, nominal_duration_s: 0.2 });
  assert.equal(boundary.nominal_trip_count, 1); close(boundary.nominal_unserved_s, 0);
  assert.equal(boundary.nuisance_free, false);
  const short = simulate('eps_protection', { ...protection, legitimate_current_A: 2, nominal_duration_s: 0.1 });
  assert.equal(short.nuisance_free, true); close(short.fault_interruption_s, 0.1);
});

test('MIL command shedding, logical inhibits and unavailable processor policies are not assumed', () => {
  const healthy = { ...protection, fault_voltage_V: 4, fault_current_A: 1 };
  const shed = simulate('eps_protection', { ...healthy, fault_command_on: false });
  assert.equal(shed.trip_count, 0); close(shed.fault_interruption_s, 0);
  close(shed.recovery_time_s, 0); assert.equal(shed.protection_ok, null);
  const inhibited = simulate('eps_protection', { ...healthy, fault_inhibited: true });
  assert.equal(inhibited.inhibited_outputs_off, true); close(inhibited.fault_i2t_A2s, 0);
  const autonomous = simulate('eps_protection', { ...protection, processor_available: false });
  assert.equal(autonomous.protection_ok, true);
  const disabled = simulate('eps_protection', { ...protection, processor_available: false, autonomous_protection: false });
  assert.equal(disabled.trip_count, 0); assert.equal(disabled.fault_interruption_s, null);
  close(disabled.fault_i2t_A2s, 16); assert.equal(disabled.protection_ok, false);
  const inhibitLost = simulate('eps_protection', { ...healthy, processor_available: false, autonomous_inhibit: false, fault_inhibited: true });
  assert.equal(inhibitLost.inhibited_outputs_off, false); close(inhibitLost.inhibited_on_s, 1);
  const off = simulate('eps_protection', { ...healthy, processor_available: false, processor_off_output_on: false });
  assert.equal(off.total_on_s, 0); assert.equal(off.final_output_on, false);
  const peak = simulate('eps_protection', { ...protection, peak_limit_A: 3 });
  assert.equal(peak.stress_ok, false); close(peak.fault_peak_A, 4);
});

function batteryAnalytic(p) {
  const tau = p.r1_ohm * p.c1_F, a = p.current_A * p.r1_ohm;
  const b = p.initial_polarization_V - a, e = Math.exp(-p.duration_s / tau);
  const z = p.initial_soc + p.current_A * p.duration_s / p.capacity_C;
  const u = a + b * e;
  const ocv0 = p.ocv_at_zero_V + p.ocv_slope_V * p.initial_soc;
  const integralOCV = ocv0 * p.duration_s + p.ocv_slope_V * p.current_A / p.capacity_C * p.duration_s ** 2 / 2;
  const net = p.current_A * (integralOCV + p.current_A * p.r0_ohm * p.duration_s + a * p.duration_s + b * tau * (1 - e));
  const branch = (a ** 2 * p.duration_s + 2 * a * b * tau * (1 - e) + b ** 2 * tau / 2 * (1 - e ** 2)) / p.r1_ohm;
  return { z, u, voltage: p.ocv_at_zero_V + p.ocv_slope_V * z + p.current_A * p.r0_ohm + u, net, branch, integralOCV };
}

test('battery charge SOC, polarization, terminal energy and dissipated heat are independent exact integrals', () => {
  for (const current_A of [-1, 1, 0]) {
    const p = { ...battery, current_A }, v = simulate('eps_battery_step', p), expected = batteryAnalytic(p);
    close(v.end_soc, expected.z); close(v.end_polarization_V, expected.u);
    close(v.end_voltage_V, expected.voltage); close(v.terminal_energy_J, expected.net);
    close(v.polarization_loss_J, expected.branch); close(v.ohmic_loss_J, current_A ** 2 * 0.05 * 60);
    close(v.terminal_energy_J, current_A * expected.integralOCV + v.total_loss_J + v.polarization_energy_change_J);
    close(v.terminal_energy_J, v.accepted_energy_J - v.delivered_energy_J);
    assert.ok(v.avg_loss_W >= v.min_loss_W && v.avg_loss_W <= v.max_loss_W);
    assert.equal(v.step_ok, true);
  }
});

test('battery analytical interior voltage extrema are not missed by endpoints', () => {
  const p = { ...battery, capacity_C: 100, current_A: 1, initial_soc: 0.2,
    initial_polarization_V: 0.5, duration_s: 30, soc_min: 0.1 };
  const v = simulate('eps_battery_step', p);
  const time = -10 * Math.log((0.01 * 10) / 0.4);
  const expected = 3.2 + 0.01 * time + 0.05 + 0.1 + 0.4 * Math.exp(-time / 10);
  close(v.min_voltage_V, expected);
  assert.ok(v.min_voltage_V < v.end_voltage_V && v.min_voltage_V < 3.75);
  const reverse = simulate('eps_battery_step', { ...p, initial_soc: 0.8, current_A: -1, initial_polarization_V: -0.5 });
  close(reverse.max_voltage_V, 7 - expected);
});

test('battery relaxation, branch zero crossing and tiny-step losses remain physical without clipping', () => {
  const relax = simulate('eps_battery_step', { ...battery, current_A: 0, initial_polarization_V: 0.5 });
  close(relax.total_loss_J, 100 * 0.5 ** 2 / 2 * (1 - Math.exp(-12)));
  close(relax.total_loss_J, -relax.polarization_energy_change_J);
  close(relax.terminal_energy_J, 0);
  const crossing = simulate('eps_battery_step', { ...battery, current_A: 1, initial_polarization_V: -0.1 });
  close(crossing.min_loss_W, 0.05);
  const tiny = simulate('eps_battery_step', { ...battery, current_A: 1, r0_ohm: 0, duration_s: 1e-6 });
  const leading = 0.1 * (1e-6) ** 3 / (3 * 10 ** 2);
  assert.ok(Math.abs(tiny.total_loss_J / leading - 1) < 1e-6);
});

test('battery signed terminal energy splits both ways when a known bad voltage crosses zero', () => {
  const p = { ...battery, current_A: 1, initial_polarization_V: -5 };
  const v = simulate('eps_battery_step', p), expected = batteryAnalytic(p);
  assert.ok(v.min_voltage_V < 0); assert.equal(v.voltage_ok, false);
  assert.ok(v.accepted_energy_J > 0 && v.delivered_energy_J > 0);
  close(v.terminal_energy_J, expected.net);
  // Independent fine midpoint quadrature, including the power-sign crossing.
  const count = 100000, h = p.duration_s / count;
  let accepted = 0, delivered = 0;
  for (let i = 0; i < count; i++) {
    const t = (i + 0.5) * h;
    const power = 3.8 + t / 3600 + 0.05 + 0.1 - 5.1 * Math.exp(-t / 10);
    accepted += Math.max(power, 0) * h; delivered += Math.max(-power, 0) * h;
  }
  close(v.accepted_energy_J, accepted, 1e-7); close(v.delivered_energy_J, delivered, 1e-7);
});

test('battery unknown limits, operational excursions, zero duration and chained intervals preserve evidence', () => {
  const unknown = simulate('eps_battery_step', { ...battery, voltage_limits_known: false, soc_limits_known: false });
  assert.equal(unknown.voltage_ok, null); assert.equal(unknown.soc_ok, null);
  assert.equal(unknown.voltage_low_margin_V, null); assert.equal(unknown.step_ok, null);
  const bad = simulate('eps_battery_step', { ...battery, initial_soc: 0.99, current_A: 1, capacity_C: 100,
    voltage_limits_known: false, soc_limits_known: false });
  assert.ok(bad.end_soc > 1); assert.equal(bad.physical_soc_ok, false); assert.equal(bad.step_ok, false);
  const badVoltage = simulate('eps_battery_step', { ...battery, voltage_min_V: 3.7, soc_limits_known: false });
  assert.ok(badVoltage.voltage_low_margin_V < 0); assert.equal(badVoltage.step_ok, false);
  const zero = simulate('eps_battery_step', { ...battery, duration_s: 0 });
  close(zero.end_soc, 0.8); close(zero.terminal_energy_J, 0); close(zero.total_loss_J, 0);
  assert.equal(zero.avg_loss_W, null);
  const first = simulate('eps_battery_step', { ...battery, duration_s: 30 });
  const second = simulate('eps_battery_step', { ...battery, duration_s: 30, initial_soc: first.end_soc, initial_polarization_V: first.end_polarization_V });
  const full = simulate('eps_battery_step', battery);
  close(second.end_voltage_V, full.end_voltage_V); close(second.end_soc, full.end_soc);
  close(first.total_loss_J + second.total_loss_J, full.total_loss_J);
  close(first.terminal_energy_J + second.terminal_energy_J, full.terminal_energy_J);
});

test('thermal exponential endpoint extrema, mean, energies and margins match independent RC solution', () => {
  const v = simulate('eps_thermal', thermal);
  const eq = 260 + 5 / 0.5, tau = 100 / 0.5, expected = eq + (280 - eq) * Math.exp(-200 / tau);
  const mean = eq + (280 - eq) * tau / 200 * (1 - Math.exp(-200 / tau));
  close(v.end_temp_K, expected); close(v.min_temp_K, expected); close(v.max_temp_K, 280);
  close(v.mean_temp_K, mean); close(v.thermal_time_constant_s, tau);
  close(v.dissipation_energy_J, 400); close(v.heater_energy_J, 600);
  close(v.stored_heat_change_J, 100 * (expected - 280));
  close(v.ambient_heat_out_J, 0.5 * 200 * (mean - 260)); close(v.energy_residual_J, 0, 1e-10);
  close(v.charge_low_margin_K, expected - 273); assert.equal(v.thermal_ok, true);
});

test('thermal adiabatic, equilibrium, tiny-conductance, zero-duration and chained cases are exact', () => {
  const adiabatic = simulate('eps_thermal', { ...thermal, conductance_W_K: 0 });
  close(adiabatic.end_temp_K, 290); close(adiabatic.mean_temp_K, 285);
  close(adiabatic.ambient_heat_out_J, 0); assert.equal(adiabatic.thermal_time_constant_s, null);
  const tiny = simulate('eps_thermal', { ...thermal, conductance_W_K: 1e-12 });
  close(tiny.end_temp_K, 290, 1e-9); close(tiny.mean_temp_K, 285, 1e-9);
  const equilibrium = simulate('eps_thermal', { ...thermal, ambient_temp_K: 270 });
  close(equilibrium.end_temp_K, 280); close(equilibrium.stored_heat_change_J, 0);
  close(equilibrium.ambient_heat_out_J, 1000);
  const boundaryHeat = simulate('eps_thermal', { ...thermal, initial_temp_K: 260, ambient_temp_K: 280, dissipation_W: 0, heater_W: 0 });
  assert.ok(boundaryHeat.ambient_heat_out_J < 0);
  close(boundaryHeat.ambient_heat_out_J, -boundaryHeat.stored_heat_change_J, 1e-10);
  const zero = simulate('eps_thermal', { ...thermal, duration_s: 0 });
  close(zero.end_temp_K, 280); close(zero.mean_temp_K, 280); close(zero.total_generated_J, 0);
  const first = simulate('eps_thermal', { ...thermal, duration_s: 100 });
  const second = simulate('eps_thermal', { ...thermal, duration_s: 100, initial_temp_K: first.end_temp_K });
  const full = simulate('eps_thermal', thermal);
  close(second.end_temp_K, full.end_temp_K); close(first.ambient_heat_out_J + second.ambient_heat_out_J, full.ambient_heat_out_J);
});

test('thermal unknown, inactive charge and known temperature violations are distinct', () => {
  const unknown = simulate('eps_thermal', { ...thermal, temp_limits_known: false, charge_limits_known: false });
  assert.equal(unknown.temp_ok, null); assert.equal(unknown.charge_ok, null); assert.equal(unknown.thermal_ok, null);
  const inactive = simulate('eps_thermal', { ...thermal, charge_active: false, charge_limits_known: false });
  assert.equal(inactive.charge_ok, true); assert.equal(inactive.charge_low_margin_K, null);
  const cold = simulate('eps_thermal', { ...thermal, heater_W: 0 });
  assert.ok(cold.end_temp_K < 273); assert.equal(cold.charge_ok, false); assert.equal(cold.thermal_ok, false);
  const hot = simulate('eps_thermal', { ...thermal, initial_temp_K: 310 });
  close(hot.max_temp_K, 310); assert.ok(hot.temp_high_margin_K < 0); assert.equal(hot.temp_ok, false);
  const partial = simulate('eps_thermal', { ...thermal, temp_max_K: 275, charge_limits_known: false });
  assert.equal(partial.temp_ok, false); assert.equal(partial.charge_ok, null); assert.equal(partial.thermal_ok, false);
});

test('invalid physical domains and unsupported grids return only stderr with nonzero exit', () => {
  for (const [id, base, change, message] of [
    ['eps_power_path', power, { efficiency: 0 }, /efficiency/],
    ['eps_power_path', power, { efficiency: 1.1 }, /efficiency/],
    ['eps_power_path', power, { source_voltage_V: 0 }, /positive/],
    ['eps_power_path', power, { topology_code: 3 }, /topology/],
    ['eps_power_path', power, { topology_code: true }, /topology/],
    ['eps_power_path', power, { duty_min: 1, duty_max: 0 }, /duty/],
    ['eps_power_path', power, { path_resistance_ohm: -1 }, /nonnegative/],
    ['eps_protection', protection, { uv_reset_V: 2.9 }, /hysteresis/],
    ['eps_protection', protection, { oc_reset_A: 3 }, /hysteresis/],
    ['eps_protection', protection, { step_s: 0 }, /positive/],
    ['eps_protection', protection, { fault_duration_s: 0.25 }, /integer multiples/],
    ['eps_protection', protection, { fault_duration_s: 1e-12 }, /integer multiples/],
    ['eps_protection', protection, { reset_delay_s: -1 }, /nonnegative/],
    ['eps_battery_step', battery, { capacity_C: 0 }, /positive/],
    ['eps_battery_step', battery, { r1_ohm: 0 }, /positive/],
    ['eps_battery_step', battery, { c1_F: -1 }, /positive/],
    ['eps_battery_step', battery, { r0_ohm: -1 }, /nonnegative/],
    ['eps_battery_step', battery, { soc_min: 1.1 }, /bounds/],
    ['eps_battery_step', battery, { ocv_slope_V: -1 }, /nonnegative/],
    ['eps_thermal', thermal, { heat_capacity_J_K: 0 }, /positive/],
    ['eps_thermal', thermal, { conductance_W_K: -1 }, /nonnegative/],
    ['eps_thermal', thermal, { ambient_temp_K: -1 }, /nonnegative/],
    ['eps_thermal', thermal, { temp_min_K: 301 }, /bounds/],
  ]) rejected(id, { ...base, ...change }, message);
});

test('MIL rejects excessive workloads, accepts the exact bound, other models have fixed work', () => {
  rejected('eps_protection', { ...protection, nominal_duration_s: 0, fault_duration_s: 100001, recovery_duration_s: 0, step_s: 1 }, /100000 steps/);
  rejected('eps_protection', { ...protection, step_s: 1e-10 }, /100000 steps/);
  const bound = simulate('eps_protection', { ...protection, nominal_duration_s: 0, fault_duration_s: 100000, recovery_duration_s: 0, step_s: 1 });
  assert.equal(bound.sample_count, 100000);
  const endBoundary = simulate('eps_protection', { ...protection, recovery_duration_s: 0.3 });
  close(endBoundary.recovery_time_s, 0.3); assert.equal(endBoundary.final_output_on, true);
  const atFaultEnd = simulate('eps_protection', { ...protection, trip_delay_s: 1 });
  close(atFaultEnd.fault_interruption_s, 1); close(atFaultEnd.fault_i2t_A2s, 16);
  simulate('eps_power_path', { ...power, pulse_duration_s: 1e12, pulse_rating_duration_s: 1e12 });
  simulate('eps_battery_step', { ...battery, current_A: 0, duration_s: 1e12 });
  simulate('eps_thermal', { ...thermal, duration_s: 1e12 });
});

test('nonfinite intermediate arithmetic fails instead of leaking invalid JSON', () => {
  rejected('eps_power_path', { ...power, rail_voltage_V: 1e308, steady_current_A: 1e308 }, /range|compliant/);
  rejected('eps_protection', { ...protection, fault_current_A: 1e308 }, /range|too large/);
  rejected('eps_battery_step', { ...battery, capacity_C: 1e-300, current_A: 1e300 }, /finite numerical domain/);
  rejected('eps_thermal', { ...thermal, dissipation_W: 1e308, duration_s: 1e308 }, /range|compliant/);
});
