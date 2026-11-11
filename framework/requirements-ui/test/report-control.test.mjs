import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { loadScriptCatalog } from '../python.mjs';

const definitions = await loadScriptCatalog();
const converter = { duration_s: 10, initial_voltage_V: 0, target_voltage_V: 5, time_constant_s: 1,
  load_current_A: 2, conversion_efficiency: 0.8, input_voltage_V: 8, required_min_V: 4.5,
  required_max_V: 5.5, regulation_tolerance_V: 0.01 };
const inventory = { goal_code: 1, activity_code: 2, component_count: 4, operating_case_count: 2,
  valid_sample_count: 5, failure_mode_count: 4, failure_dependency_count: 3, basic_event_count: 4, cut_term_count: 4,
  has_reference_limits: true, has_model_parameters: true, has_schedule: true, has_retained_capacities: true,
  has_geometry: true, has_failure_logic: true, has_failure_effects: true, has_failure_probabilities: true,
  has_independent_reference: true, results_available: false, results_current: false, validation_required: false };
function execute(id, inputs) {
  return spawnSync(process.env.VERIFICATION_PYTHON || 'python3', ['-I', '-B', fileURLToPath(new URL(`../scripts/${id}.py`, import.meta.url))], {
    input: JSON.stringify({ inputs, requirements: {}, mode: null }), encoding: 'utf8', timeout: 5000,
  });
}
function simulate(id, inputs) {
  const result = execute(id, inputs); assert.equal(result.status, 0, result.stderr);
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
const close = (value, expected, tolerance = 1e-10) => assert.ok(Math.abs(value - expected) <= tolerance, `${value} != ${expected}`);

test('first-order converter startup, settling and energy agree with independent analytic results', () => {
  const v = simulate('eps_converter_step', converter);
  close(v.voltage_end_V, 5 * (1 - Math.exp(-10))); close(v.voltage_min_V, 0);
  close(v.startup_time_s, Math.log(10)); close(v.settling_time_s, Math.log(500));
  close(v.service_duration_s, 10 - Math.log(10));
  close(v.output_energy_J, 2 * (50 - 5 * (1 - Math.exp(-10))));
  close(v.input_energy_J, v.output_energy_J / 0.8); close(v.loss_energy_J, v.input_energy_J - v.output_energy_J);
  assert.ok(v.settled && v.startup_reached && v.service_at_end);
  assert.equal(v.voltage_limits_ok, false);
  const steady = simulate('eps_converter_step', { ...converter, initial_voltage_V: 5 });
  assert.ok(steady.voltage_limits_ok); close(steady.startup_time_s, 0); close(steady.settling_time_s, 0);
  close(steady.output_energy_J, 100);
});

test('short, unattainable and overvoltage converter cases preserve failed and undefined results', () => {
  const short = simulate('eps_converter_step', { ...converter, duration_s: 0.1 });
  assert.equal(short.settled, false); assert.equal(short.settling_time_s, null);
  assert.equal(short.startup_reached, false); assert.equal(short.startup_time_s, null);
  const asymptotic = simulate('eps_converter_step', { ...converter, required_min_V: 5, duration_s: 1000 });
  assert.equal(asymptotic.startup_reached, false); assert.equal(asymptotic.startup_time_s, null);
  const over = simulate('eps_converter_step', { ...converter, initial_voltage_V: 5, target_voltage_V: 7 });
  assert.equal(over.service_at_end, false); assert.equal(over.voltage_limits_ok, false);
  close(over.service_duration_s, 0);
  const falling = simulate('eps_converter_step', { ...converter, initial_voltage_V: 8 });
  close(falling.startup_time_s, Math.log(6));
});

test('method eligibility reports named prerequisites and proposes repeated assessment from current evidence', () => {
  for (const goal_code of [1, 2, 3, 4, 5, 6, 7]) {
    const v = simulate('eps_guidance', { ...inventory, goal_code });
    assert.equal(v.method_code, goal_code); assert.equal(v.executable, true);
    assert.equal(v.unmet_prerequisite_mask, 0); assert.equal(v.recommended_activity_code, 2);
  }
  const stale = simulate('eps_guidance', { ...inventory, results_available: true });
  assert.equal(stale.repeat_analysis, true); assert.equal(stale.recommended_activity_code, 2);
  const assess = simulate('eps_guidance', { ...inventory, results_available: true, results_current: true });
  assert.equal(assess.repeat_analysis, false); assert.equal(assess.recommended_activity_code, 3);
  const validate = simulate('eps_guidance', { ...inventory, results_available: true, results_current: true, activity_code: 3, validation_required: true });
  assert.equal(validate.independent_validation_ready, true); assert.equal(validate.recommended_activity_code, 4);
  const collect = simulate('eps_guidance', { ...inventory, results_available: true, results_current: true, activity_code: 3,
    validation_required: true, has_independent_reference: false });
  assert.equal(collect.independent_validation_ready, false); assert.equal(collect.recommended_activity_code, 1);
  assert.equal(simulate('eps_guidance', { ...inventory, results_available: true, results_current: true, activity_code: 3 }).recommended_activity_code, 5);
});

test('RAM method screening distinguishes qualitative eligibility, quantitative data and model size', () => {
  const qualitative = simulate('eps_guidance', { ...inventory, goal_code: 5, has_failure_probabilities: false });
  assert.ok(qualitative.fmea_eligible && qualitative.fault_tree_eligible && qualitative.failure_propagation_eligible);
  assert.equal(qualitative.fmeca_eligible, false); assert.equal(qualitative.quantitative_fault_tree_eligible, false);
  assert.equal(qualitative.unmet_prerequisite_mask, 256); assert.equal(qualitative.executable, false);
  const large = simulate('eps_guidance', { ...inventory, goal_code: 5, basic_event_count: 5 });
  assert.equal(large.unmet_prerequisite_mask, 512); assert.equal(large.executable, false);
  const missing = simulate('eps_guidance', { ...inventory, operating_case_count: 0, has_reference_limits: false,
    has_model_parameters: false, has_schedule: false, has_retained_capacities: false });
  assert.equal(missing.unmet_prerequisite_mask, 31); assert.equal(missing.unmet_prerequisite_count, 5);
  assert.equal(missing.recommended_activity_code, 0);
  const noEffects = simulate('eps_guidance', { ...inventory, has_failure_effects: false, failure_dependency_count: 0 });
  assert.equal(noEffects.fmea_eligible, false); assert.equal(noEffects.failure_propagation_eligible, false);
});

test('invalid converter parameters and invalid inventories fail with diagnostics', () => {
  for (const [id, values, changes] of [
    ['eps_converter_step', converter, [{ duration_s: 0 }, { time_constant_s: -1 }, { conversion_efficiency: 2 }, { input_voltage_V: 0 },
      { regulation_tolerance_V: 0 }, { required_min_V: 8 }, { load_current_A: -1 }]],
    ['eps_guidance', inventory, [{ goal_code: 8 }, { activity_code: 5 }, { component_count: -1 }, { basic_event_count: 0.5 }, { has_geometry: 1 }]],
  ]) for (const change of changes) {
    const result = execute(id, { ...values, ...change });
    assert.equal(result.status, 1, `${id}: ${JSON.stringify(change)}`); assert.equal(result.stdout, ''); assert.ok(result.stderr.trim());
  }
});
