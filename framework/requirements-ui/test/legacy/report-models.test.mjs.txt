import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { blankWorkspace } from '../model.mjs';
import { loadScriptCatalog, runScripts } from '../python.mjs';
import { runKey, scriptInstance } from '../verification-methods.mjs';

const definitions = await loadScriptCatalog();
const python = process.env.VERIFICATION_PYTHON || 'python3';
const ids = ['eps_sizing', 'eps_geometry', 'eps_fit', 'eps_ram'];
const sizing = {
  sun_energy_Wh: 4, eclipse_energy_Wh: 2, sunlight_s: 3600, sun_path_eff: 0.8, eclipse_path_eff: 0.5,
  sizing_margin: 0.2, depth_of_discharge: 0.4, pv_cell_power_W: 2, pv_retained_factor: 0.8,
  pv_operating_factor: 0.75, pv_series: 4, pv_parallel: 2, pv_fixed: false, pv_cell_area_m2: 0.003,
  usable_face_area_m2: 0.04, packing_fraction: 0.8, bat_cell_energy_Wh: 3, bat_cell_charge_Ah: 0.8,
  bat_series: 2, bat_parallel: 2, bat_fixed: false, energy_retained_factor: 0.8, charge_retained_factor: 0.8,
  required_retained_charge_Ah: 1, source_low_V: 12, source_high_V: 16, receiver_low_V: 10,
  receiver_high_V: 20, interval_known: true, conversion_kind: 1, output_low_V: 5, output_high_V: 6,
};
const geometry = {
  size_x_m: 2, size_y_m: 1, size_z_m: 1, center_x_m: 0, center_y_m: 0, center_z_m: 0,
  roll_deg: 0, pitch_deg: 0, yaw_deg: 0,
  install_min_x_m: -3, install_min_y_m: -3, install_min_z_m: -3,
  install_max_x_m: 3, install_max_y_m: 3, install_max_z_m: 3,
  keep_size_x_m: 1, keep_size_y_m: 1, keep_size_z_m: 1,
  keep_center_x_m: 4, keep_center_y_m: 0, keep_center_z_m: 0,
  keep_roll_deg: 0, keep_pitch_deg: 0, keep_yaw_deg: 0, touching_allowed: false, tolerance_m: 1e-12,
};
const fit = {
  model_kind: 1, sample_count: 5, valid_mask: 31, asymptote: 0,
  rmse_limit: 1e-10, max_error_limit: 1e-10, min_x_span: 0.1,
  x1: 0, y1: 4.2, x2: 1, y2: 4.1, x3: 2, y3: 4, x4: 3, y4: 3.9, x5: 4, y5: 3.8,
};
const ram = {
  value_kind: 0, exposure_h: 100, independence_confirmed: true, common_cause_resolved: true,
  term_count: 4, term1: 3, term2: 5, term3: 7, term4: 3,
  event1_value: 0.1, event2_value: 0.2, event3_value: 0.3, event4_value: 0.4,
  conditional_failed_mask: 2, conditional_healthy_mask: 0,
};
const samples = { eps_sizing: sizing, eps_geometry: geometry, eps_fit: fit, eps_ram: ram };
const close = (actual, expected, tolerance = 1e-10) => {
  assert.equal(typeof actual, 'number');
  assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);
};
function execute(id, inputs, payload = {}) {
  return spawnSync(python, ['-I', '-B', fileURLToPath(new URL(`../scripts/${id}.py`, import.meta.url))], {
    input: JSON.stringify({ inputs, requirements: {}, mode: null, ...payload }), encoding: 'utf8', timeout: 5000,
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

test('four bounded standard-library definitions load; picker instances start entirely unset', async () => {
  for (const id of ids) {
    const definition = definitions.find(item => item.id === id);
    assert.ok(definition, id);
    assert.ok(definition.inputs.length <= 32 && definition.outputs.length <= 32);
    const parameters = [...definition.inputs, ...definition.outputs];
    assert.equal(new Set(parameters.map(p => p.name)).size, parameters.length);
    assert.ok(parameters.every(p => p.name.length <= 40 && ['float', 'integer', 'boolean'].includes(p.type)));
    assert.deepEqual(Object.keys(samples[id]).sort(), definition.inputs.map(p => p.name).sort());
    const workspace = blankWorkspace(), script = scriptInstance(definition, { key: id, id: 'SCR001' });
    workspace.scripts.push(script);
    assert.ok(Object.values(script.parameters).every(value => value === null));
    const evidence = await runScripts(workspace, script.key);
    assert.equal(evidence.runs[runKey(script.key, null)].state, 'pending');
    assert.equal(evidence.runs[runKey(script.key, null)].executedAt, undefined);
    simulate(id, samples[id]);
  }
});

test('documented exact JSON examples remain synchronized with the executed synthetic fixtures', async () => {
  const doc = await readFile(new URL('../analyses/MODELS.md', import.meta.url), 'utf8');
  const examples = [...doc.matchAll(/```json\n([\s\S]*?)\n```/g)].map(match => JSON.parse(match[1]));
  assert.equal(examples.length, ids.length);
  ids.forEach((id, index) => assert.deepEqual(examples[index], samples[id]));
});

test('sizing matches independent preliminary power, integer rounding, energy/charge and packing equations', () => {
  const v = simulate('eps_sizing', sizing);
  close(v.required_generation_W, 9);
  close(v.pv_cell_eol_W, 1.2);
  assert.equal(v.pv_min_cells, 8);
  assert.equal(v.pv_installed_cells, 8);
  assert.equal(v.pv_proposed_series, 4);
  assert.equal(v.pv_proposed_parallel, 2);
  close(v.pv_generation_bol_W, 12);
  close(v.pv_generation_eol_W, 9.6);
  close(v.generation_margin_W, 0.6);
  close(v.active_area_m2, 0.024);
  close(v.required_area_m2, 0.03);
  close(v.installed_area_m2, 0.03);
  close(v.packing_margin_m2, 0.008);
  close(v.required_bol_energy_Wh, 6);
  close(v.required_retained_energy_Wh, 5); // M is NOT reapplied to EOL.
  close(v.required_bol_charge_Ah, 1.25);
  close(v.battery_energy_bol_Wh, 12);
  close(v.battery_energy_eol_Wh, 9.6);
  close(v.battery_charge_bol_Ah, 1.6);
  close(v.battery_charge_eol_Ah, 1.28);
  close(v.retained_charge_margin_Ah, 0.28);
  assert.equal(v.bat_proposed_parallel, 2);
  close(v.input_voltage_margin_V, 2);
  close(v.conversion_margin_V, 6);
  assert.equal(v.voltage_screen_ok, true);
  assert.equal(v.interface_feasible, null); // No absolute/current/startup ratings.
  assert.equal(v.sizing_ok, true);
});

test('sizing preserves configured/fixed products, failures, unknown voltage and dark source evidence', () => {
  const failed = simulate('eps_sizing', { ...sizing, pv_parallel: 1, bat_parallel: 1, usable_face_area_m2: 0.01 });
  close(failed.generation_margin_W, -4.2);
  close(failed.retained_energy_margin_Wh, -0.2);
  close(failed.retained_charge_margin_Ah, -0.36);
  assert.equal(failed.sizing_ok, false);
  assert.equal(failed.pv_installed_cells, 4);
  assert.equal(failed.pv_proposed_parallel, 2);
  const fixed = simulate('eps_sizing', { ...sizing, pv_parallel: 1, pv_fixed: true, bat_parallel: 1, bat_fixed: true });
  assert.equal(fixed.pv_proposed_parallel, 1);
  assert.equal(fixed.bat_proposed_parallel, 1);
  assert.equal(fixed.sizing_ok, false);
  const aggregate = simulate('eps_sizing', { ...sizing, pv_series: 1, pv_parallel: 1, pv_fixed: true,
    pv_cell_power_W: 16, pv_cell_area_m2: 0.024, bat_series: 1, bat_parallel: 1, bat_fixed: true,
    bat_cell_energy_Wh: 12, bat_cell_charge_Ah: 1.6 });
  assert.equal(aggregate.sizing_ok, true);
  assert.equal(aggregate.pv_proposed_parallel, 1);
  const unknown = simulate('eps_sizing', { ...sizing, interval_known: false, source_low_V: 0, source_high_V: 0 });
  assert.equal(unknown.voltage_screen_ok, null);
  assert.equal(unknown.input_voltage_margin_V, null);
  assert.equal(unknown.interface_feasible, null);
  const badVoltage = simulate('eps_sizing', { ...sizing, receiver_high_V: 15 });
  close(badVoltage.input_voltage_margin_V, -1);
  assert.equal(badVoltage.interface_feasible, false);
  const badBuck = simulate('eps_sizing', { ...sizing, output_high_V: 13 });
  assert.equal(badBuck.voltage_screen_ok, false);
  close(badBuck.conversion_margin_V, -1);
  assert.equal(simulate('eps_sizing', { ...sizing, conversion_kind: 3 }).voltage_screen_ok, null);
  const boost = simulate('eps_sizing', { ...sizing, conversion_kind: 2, output_low_V: 18, output_high_V: 20 });
  close(boost.conversion_margin_V, 2);
  const direct = simulate('eps_sizing', { ...sizing, conversion_kind: 0, output_low_V: 11, output_high_V: 17 });
  assert.equal(direct.voltage_screen_ok, true);
  const dark = simulate('eps_sizing', { ...sizing, pv_operating_factor: 0 });
  assert.equal(dark.pv_min_cells, null);
  assert.equal(dark.pv_proposed_parallel, null);
  assert.equal(dark.required_area_m2, null);
  assert.equal(dark.sizing_ok, false);
  const bounded = simulate('eps_sizing', { ...sizing, pv_cell_power_W: 1e-8 });
  assert.equal(bounded.pv_proposed_parallel, null);
  assert.equal(bounded.proposal_within_bounds, false);
  assert.ok(bounded.generation_margin_W < 0);
  const lost = simulate('eps_sizing', { ...sizing, pv_retained_factor: 0,
    energy_retained_factor: 0, charge_retained_factor: 0 });
  assert.equal(lost.sizing_ok, false);
  assert.equal(lost.bat_proposed_parallel, null);
  assert.equal(lost.required_bol_charge_Ah, null);
  close(lost.retained_energy_margin_Wh, -5);
  close(lost.retained_charge_margin_Ah, -1);
  const noDemand = simulate('eps_sizing', { ...sizing, sun_energy_Wh: 0, eclipse_energy_Wh: 0,
    required_retained_charge_Ah: 0, pv_retained_factor: 0, energy_retained_factor: 0, charge_retained_factor: 0 });
  assert.equal(noDemand.sizing_ok, true);
  assert.equal(noDemand.pv_proposed_parallel, 1);
  assert.equal(noDemand.bat_proposed_parallel, 1);
  close(noDemand.required_bol_charge_Ah, 0);
});

test('geometry matches analytic transformed bounds, containment and contact policy', () => {
  const v = simulate('eps_geometry', geometry);
  close(v.volume_m3, 2);
  close(v.bound_min_x_m, -1);
  close(v.bound_max_y_m, 0.5);
  close(v.containment_margin_m, 2);
  close(v.keepout_gap_m, 2.5);
  assert.equal(v.accommodation_ok, true);
  const rotated = simulate('eps_geometry', { ...geometry, yaw_deg: 90, center_z_m: 0.25 });
  close(rotated.bound_max_x_m, 0.5);
  close(rotated.bound_min_y_m, -1);
  close(rotated.bound_min_z_m, -0.25);
  const composed = simulate('eps_geometry', { ...geometry, size_z_m: 0.5, roll_deg: 90, yaw_deg: 90 });
  close(composed.bound_max_x_m, 0.25);
  close(composed.bound_max_y_m, 1);
  close(composed.bound_max_z_m, 0.5);
  const outside = simulate('eps_geometry', { ...geometry, center_x_m: 2.5 });
  close(outside.containment_margin_m, -0.5);
  assert.equal(outside.contained, false);
  for (const touching_allowed of [true, false]) {
    const touching = simulate('eps_geometry', { ...geometry, keep_center_x_m: 1.5, touching_allowed });
    close(touching.keepout_gap_m, 0);
    assert.equal(touching.keepout_clear, touching_allowed);
    assert.equal(touching.overlap, !touching_allowed);
  }
  const overlap = simulate('eps_geometry', { ...geometry, keep_center_x_m: 1.25, touching_allowed: true });
  close(overlap.keepout_gap_m, -0.25);
  assert.equal(overlap.accommodation_ok, false);
});

test('SAT distinguishes AABB overlap and separates skew boxes on an edge-cross-edge axis', () => {
  const parallel = simulate('eps_geometry', { ...geometry, size_x_m: 4, size_y_m: 0.2, size_z_m: 0.2,
    yaw_deg: 45, keep_size_x_m: 4, keep_size_y_m: 0.2, keep_size_z_m: 0.2,
    keep_yaw_deg: 45, keep_center_x_m: 0, keep_center_y_m: 1 });
  assert.ok(parallel.bound_max_x_m > parallel.keep_bound_min_x_m);
  assert.ok(parallel.bound_max_y_m > parallel.keep_bound_min_y_m);
  close(parallel.keepout_gap_m, Math.SQRT1_2 - 0.2);
  assert.equal(parallel.keepout_clear, true);
  // Rod directions a=(1,0,0), b=(1,1,1)/sqrt(3). All six face-axis
  // projections overlap. n=(0,-1,1)/sqrt(2) is their separating cross axis.
  const skew = simulate('eps_geometry', { ...geometry, size_x_m: 4, size_y_m: 0.2, size_z_m: 0.2,
    keep_size_x_m: 4, keep_size_y_m: 0.2, keep_size_z_m: 0.2,
    keep_yaw_deg: 45, keep_pitch_deg: -Math.asin(1 / Math.sqrt(3)) * 180 / Math.PI,
    keep_center_x_m: 0, keep_center_y_m: -0.5 * Math.SQRT1_2, keep_center_z_m: 0.5 * Math.SQRT1_2 });
  const separatingGap = 0.5 - 0.1 * Math.SQRT2 - 0.1 * (0.5 + Math.sqrt(3) / 2);
  assert.ok(skew.keepout_gap_m >= separatingGap - 1e-12);
  assert.ok(skew.axes_tested > 6 && skew.axes_tested <= 15);
  assert.equal(skew.keepout_clear, true);
});

test('affine battery/PV and exponential fits reproduce independently generated parameters and domains', () => {
  const battery = simulate('eps_fit', fit);
  close(battery.battery_ocv_V, 4.2);
  close(battery.battery_resistance_ohm, 0.1);
  close(battery.residual_rmse, 0);
  close(battery.r_squared, 1);
  assert.equal(battery.used_samples, 5);
  assert.equal(battery.residual_dof, 3);
  assert.equal(battery.domain_x_min, 0);
  assert.equal(battery.domain_x_max, 4);
  assert.equal(battery.model_valid, true);
  assert.equal(battery.time_constant_s, null);
  const pv = { ...fit, model_kind: 0, y1: 1, y2: 0.9, y3: 0.8, y4: 0.7, y5: 0.6 };
  const solar = simulate('eps_fit', pv);
  close(solar.pv_intercept_A, 1);
  close(solar.pv_slope_A_V, -0.1);
  assert.equal(solar.battery_ocv_V, null);
  const exponential = { ...fit, model_kind: 2, asymptote: 10 };
  for (let i = 1; i <= 5; i++) exponential[`y${i}`] = 10 + 4 * Math.exp(-(i - 1) / 2);
  const dynamics = simulate('eps_fit', exponential);
  close(dynamics.exp_amplitude, 4);
  close(dynamics.time_constant_s, 2);
  close(dynamics.fit_intercept, Math.log(4));
  close(dynamics.fit_slope, -0.5);
  assert.equal(dynamics.model_valid, true);
  const rising = { ...exponential };
  for (let i = 1; i <= 5; i++) rising[`y${i}`] = 10 - 4 * Math.exp(-(i - 1) / 2);
  close(simulate('eps_fit', rising).exp_amplitude, -4);
});

test('mask quality checks exclude rejected samples; poor residuals and unphysical trends do not silently pass', () => {
  const masked = simulate('eps_fit', { ...fit, valid_mask: 15, x5: -999, y5: -999 });
  close(masked.battery_resistance_ohm, 0.1);
  assert.equal(masked.used_samples, 4);
  assert.equal(masked.domain_x_max, 3);
  const poor = simulate('eps_fit', { ...fit, y3: 3.5 });
  close(poor.residual_rmse, 0.2);
  close(poor.residual_max, 0.4);
  assert.equal(poor.fit_quality_ok, false);
  assert.equal(poor.model_valid, false);
  const unphysical = simulate('eps_fit', { ...fit, y1: 3.8, y2: 3.9, y3: 4, y4: 4.1, y5: 4.2 });
  close(unphysical.battery_resistance_ohm, -0.1);
  assert.equal(unphysical.fit_quality_ok, true);
  assert.equal(unphysical.physical_model_ok, false);
  const constant = simulate('eps_fit', { ...fit, y1: 4, y2: 4, y3: 4, y4: 4, y5: 4 });
  assert.equal(constant.r_squared, null);
});

test('RAM minimal cuts and overlapping terms match inclusion-exclusion and analytic importance', () => {
  const v = simulate('eps_ram', ram);
  close(v.top_failure_probability, 0.044);
  close(v.mission_reliability, 0.956);
  assert.equal(v.states_enumerated, 16);
  assert.equal(v.minimal_cut_count, 2);
  assert.equal(v.cut1_mask, 3);
  assert.equal(v.cut2_mask, 5);
  assert.equal(v.cut3_mask, null);
  close(v.cut1_probability, 0.02);
  close(v.cut2_probability, 0.03);
  close(v.conditional_failure_probability, 0.1);
  close(v.evidence_probability, 0.2);
  close(v.top_given_event1, 0.44);
  close(v.top_given_no_event1, 0);
  close(v.birnbaum1, 0.44);
  close(v.birnbaum2, 0.07);
  close(v.birnbaum3, 0.08);
  close(v.birnbaum4, 0);
  close(v.criticality1, 1);
  close(v.criticality2, 0.014 / 0.044);
  const fourCuts = simulate('eps_ram', { ...ram, term1: 1, term2: 2, term3: 4, term4: 8 });
  assert.equal(fourCuts.minimal_cut_count, 4);
  assert.equal(fourCuts.cut4_mask, 8);
  close(fourCuts.top_failure_probability, 1 - 0.9 * 0.8 * 0.7 * 0.6);
  const allAnd = simulate('eps_ram', { ...ram, term_count: 1, term1: 15, term2: 0, term3: 0, term4: 0 });
  assert.equal(allAnd.minimal_cut_count, 1);
  close(allAnd.top_failure_probability, 0.1 * 0.2 * 0.3 * 0.4);
  const evidence = simulate('eps_ram', { ...ram, conditional_failed_mask: 1, conditional_healthy_mask: 2 });
  close(evidence.evidence_probability, 0.08);
  close(evidence.conditional_failure_probability, 0.3);
  const result = execute('eps_ram', ram);
  assert.match(result.stderr, /TOP = \(event1 AND event2\) OR \(event1 AND event3\)/);
  assert.match(result.stderr, /semantics\/sources: engineer requirement rationale/);
});

test('RAM rates, explicit common-cause event, zero-probability conditioning and certain events', () => {
  const rates = simulate('eps_ram', { ...ram, value_kind: 1, exposure_h: 10,
    event1_value: 0.001, event2_value: 0.002, event3_value: 0.003, event4_value: 0 });
  const [a, b, c] = [0.001, 0.002, 0.003].map(rate => -Math.expm1(-10 * rate));
  close(rates.top_failure_probability, a * (b + c - b * c));
  const cc = simulate('eps_ram', { ...ram, term_count: 2, term1: 3, term2: 8, term3: 0, term4: 0 });
  close(cc.top_failure_probability, 0.4 + 0.6 * 0.02);
  const impossible = simulate('eps_ram', { ...ram, event2_value: 0 });
  assert.equal(impossible.conditional_failure_probability, null);
  assert.equal(impossible.top_given_event2, null);
  const zero = simulate('eps_ram', { ...ram, value_kind: 1, exposure_h: 0 });
  close(zero.top_failure_probability, 0);
  close(zero.mission_reliability, 1);
  assert.equal(zero.criticality1, null);
  const certain = simulate('eps_ram', { ...ram, event1_value: 1, event2_value: 1 });
  close(certain.top_failure_probability, 1);
  close(certain.mission_reliability, 0);
  assert.equal(certain.top_given_no_event1, null);
});

test('invalid domains, masks, unsupported dependencies and bounded work reject with stderr and no stdout', () => {
  const cases = [
    ['eps_sizing', { pv_series: 0 }, /positive integer/],
    ['eps_sizing', { pv_parallel: 0.5 }, /integer/],
    ['eps_sizing', { pv_series: 1000001 }, /1000000/],
    ['eps_sizing', { depth_of_discharge: 0 }, /depth_of_discharge/],
    ['eps_sizing', { energy_retained_factor: 1.1 }, /energy_retained_factor/],
    ['eps_sizing', { source_low_V: 17 }, /ordered/],
    ['eps_geometry', { size_x_m: 0 }, /positive/],
    ['eps_geometry', { tolerance_m: -1 }, /nonnegative/],
    ['eps_geometry', { install_max_x_m: -3 }, /ordered/],
    ['eps_geometry', { touching_allowed: 1 }, /boolean/],
    ['eps_fit', { valid_mask: 32 }, /valid_mask/],
    ['eps_fit', { valid_mask: 3 }, /at least 3/],
    ['eps_fit', { sample_count: 6 }, /3 through 5/],
    ['eps_fit', { x1: 1, x2: 1, x3: 1, x4: 1, x5: 1 }, /Unidentifiable/],
    ['eps_fit', { min_x_span: 5 }, /excitation/],
    ['eps_fit', { model_kind: 2, asymptote: 4 }, /transformed domain/],
    ['eps_fit', { model_kind: 2, asymptote: 0, y1: 1, y2: 2, y3: 3, y4: 4, y5: 5 }, /negative transformed slope/],
    ['eps_fit', { x1: -1 }, /nonnegative/],
    ['eps_ram', { term_count: 0 }, /empty tree/],
    ['eps_ram', { term_count: 5 }, /1 through 4/],
    ['eps_ram', { term1: 0 }, /Active term/],
    ['eps_ram', { term2: 16 }, /Active term/],
    ['eps_ram', { event1_value: -0.01 }, /probabilities/],
    ['eps_ram', { independence_confirmed: false }, /Unsupported dependence/],
    ['eps_ram', { common_cause_resolved: false }, /common-cause/],
    ['eps_ram', { conditional_failed_mask: 2, conditional_healthy_mask: 2 }, /disjoint/],
  ];
  for (const [id, changes, message] of cases) {
    const result = execute(id, { ...samples[id], ...changes });
    assert.equal(result.status, 1, `${id}: ${JSON.stringify(changes)}\n${result.stderr}`);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, message);
  }
  for (const id of ids) {
    const missing = { ...samples[id] };
    delete missing[Object.keys(missing)[0]];
    for (const input of [missing, { ...samples[id], undeclared: 1 }, { ...samples[id], [Object.keys(samples[id])[0]]: null }]) {
      const result = execute(id, input);
      assert.equal(result.status, 1);
      assert.equal(result.stdout, '');
      assert.ok(result.stderr.length > 0);
    }
    const nonfiniteName = definitions.find(d => d.id === id).inputs.find(p => p.type === 'float').name;
    const nonfinite = execute(id, { ...samples[id], [nonfiniteName]: 'NaN' });
    assert.equal(nonfinite.status, 1);
    assert.equal(nonfinite.stdout, '');
    assert.match(nonfinite.stderr, /finite/);
  }
});

test('existing public runner executes all models without mission mutation and respects per-mode bindings', async () => {
  for (const [index, id] of ids.entries()) {
    const workspace = blankWorkspace();
    const script = scriptInstance(definitions.find(d => d.id === id), { key: id, id: `SCR00${index + 1}` });
    for (const [name, value] of Object.entries(samples[id])) script.parameters[name] = typeof value === 'boolean' ? (value ? 'True' : 'False') : String(value);
    workspace.scripts.push(script);
    workspace.power.modes = [{ key: 'nom', name: 'Nominal', sunlight: 1, eclipse: 1 }, { key: 'test', name: 'Test', sunlight: 1, eclipse: 1 }];
    if (id === 'eps_sizing') script.parameters.sunlight_s = '3600 if mode == "Nominal" else 1800';
    const before = structuredClone(workspace), evidence = await runScripts(workspace, script.key);
    assert.deepEqual(workspace, before);
    for (const mode of workspace.power.modes) {
      const result = evidence.runs[runKey(script.key, mode.key)];
      assert.equal(result.state, 'value', result.message);
    }
    if (id === 'eps_sizing') {
      close(evidence.runs[runKey(script.key, 'nom')].values.required_generation_W, 9);
      close(evidence.runs[runKey(script.key, 'test')].values.required_generation_W, 18);
      assert.equal(evidence.runs[runKey(script.key, 'test')].values.sizing_ok, false);
    }
  }
});
