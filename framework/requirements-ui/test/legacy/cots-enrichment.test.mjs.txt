import assert from 'node:assert/strict';
import { after, test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { cotsBinding } from '../cots-bindings.mjs';
import { loadCotsFacts } from '../cots.mjs';
import { createEvaluationWorker } from '../evaluation-worker.mjs';
import { emptyWorkspace } from '../model.mjs';
import { setVerificationMethods } from '../verification-methods.mjs';

const expected = [
  ['isispace_iceps2_type_a', 'iceps2', 9, 'ebc07b06bb9a64f32a59e052e46f0ba0158f293c59f7f84903702fbf895a68ff'],
  ['isispace_imeps2_base_4s1p', 'imeps2', 8, '67e545caad43559f3e22243e57db998bbecd7995cbf5557996f5df7ce3632eeb'],
  ['ti_bq24650rvar', 'bq24650', 19, 'c62393dc9b5fc3d2da0391c018d46c97886b828c47990b2526fb5c881f78602e'],
  ['ti_bq25798rqmr', 'bq25798', 14, '163e45683f62f208545920e1470054b352b4a4b0cdc201e1f19fcb1007f1e222'],
  ['ti_tps63802dlar', 'tps63802', 18, 'be07deca1231c5493957bc64c2dc1cad5543bff330e49ae41caf3286fd80dca6'],
];
const evaluator = createEvaluationWorker();
after(() => evaluator.close());
const products = new Map(await Promise.all(expected.map(async ([id]) => [id, (await loadCotsFacts(id, { evaluator })).facts])));
const fact = (product, name, element = 'self', valueKind) => {
  const matches = products.get(product).filter(item => item.name === name && item.element === element && (!valueKind || item.valueKind === valueKind));
  assert.equal(matches.length, 1, `${product}.${element}.${name}.${valueKind ?? ''}`);
  return matches[0];
};
const added = product => products.get(product).filter(item => item.source.id.startsWith('enrichment_'));

test('fresh manufacturer evidence retains exact source digests, retrieval times, typed facts and distinct identities', () => {
  for (const [product, document, count, sha256] of expected) {
    const facts = products.get(product), additions = added(product);
    assert.equal(additions.length, count);
    assert.equal(new Set(facts.map(item => item.id)).size, facts.length);
    for (const item of additions) {
      assert.equal(item.source.id, `enrichment_${document}_20261110`);
      assert.equal(item.source.sha256, sha256);
      assert.match(item.source.retrievedUtc, /^2026-11-10T06:13:\d{2}\.\d{3}Z$/);
      assert.match(item.source.url, /^https:\/\/(www\.ti\.com|(?:www\.)?isispace\.nl)\//);
      assert.match(item.source.locator, /page=\d+/);
      assert.ok(item.source.revision);
      assert.match(item.revision, /^[a-f0-9]{64}$/);
      assert.equal(typeof item.value, { float: 'number', integer: 'number', boolean: 'boolean', string: 'string' }[item.type]);
    }
  }
});

test('board protection stays scoped to battery paths or TVS-protected output domains', () => {
  const iceps = 'isispace_iceps2_type_a', imeps = 'isispace_imeps2_base_4s1p';
  for (const name of ['autonomous_charge_overcurrent_protection', 'autonomous_discharge_overcurrent_protection',
    'autonomous_overvoltage_protection', 'autonomous_undervoltage_protection']) assert.equal(fact(iceps, name, 'battery').value, true);
  assert.match(fact(iceps, 'control_input_semantics', 'battery').value, /three_separation_switch_option/);
  assert.match(fact(iceps, 'undervoltage_recovery_policy', 'battery').value, /trickle_bypass/);
  for (const rail of ['vd0_vbat', 'vd1_5v', 'vd2_3v3']) {
    assert.equal(fact(imeps, 'autonomous_overvoltage_protection', rail).value, true);
    assert.equal(fact(imeps, 'overvoltage_action', rail).value, 'tvs_transient_clamp');
  }
  assert.match(fact(imeps, 'watchdog_action', 'battery').value, /without_interrupting_power/);
  assert.equal(fact(iceps, 'series_cell_count', 'battery').value, 2);
  assert.equal(fact(imeps, 'series_cell_count', 'battery').value, 4);
  assert.ok(!products.get(imeps).some(item => item.element === 'battery' && ['autonomous_undervoltage_protection', 'charge_temperature_min', 'charge_temperature_max'].includes(item.name)));
});

test('charger capabilities preserve external-circuit and configuration gates instead of claiming complete pack protection', () => {
  const fixed = 'ti_bq24650rvar', programmable = 'ti_bq25798rqmr';
  assert.equal(fact(fixed, 'autonomous_undervoltage_protection').value, true);
  assert.match(fact(fixed, 'undervoltage_action').value, /^VCC_UVLO_/);
  assert.match(fact(fixed, 'charge_temperature_policy').value, /VLTF_to_VHTF_to_start_or_resume_and_VLTF_to_VTCO_to_continue/);
  const ocp = fact(fixed, 'charge_overcurrent_sense_voltage');
  assert.equal(ocp.value, 0.08);
  assert.equal(ocp.valueKind, 'typical');
  assert.equal(ocp.condition.values.operating_mode, 'synchronous_charge_current_rising');
  assert.match(fact(programmable, 'overcurrent_action', 'battery').value, /external_ship_FET_and_SFET_PRESENT=1_and_EN_BATOC=1/);
  assert.match(fact(programmable, 'overcurrent_recovery_policy').value, /host_clear_EN_HIZ_and_DIS_ACDRV_or_adapter/);
  assert.match(fact(programmable, 'charge_temperature_policy').value, /TS_IGNORE=1.*without_battery_NTC_temperature_qualification/);
  assert.match(fact(programmable, 'startup_policy').value, /CELL_writes_reset_ICHG_VSYSMIN_VREG/);
  assert.match(fact(programmable, 'output_voltage_choices').value, /CELL_4s:14_to_18\.8V/);
  const reset = fact(programmable, 'system_power_reset_off_time');
  assert.equal(reset.value, 0.35);
  assert.equal(reset.valueKind, 'typical');
  assert.match(reset.condition.values.operating_mode, /external_ship_fet_present/);
  assert.equal(fact(programmable, 'watchdog_timeout_max').valueKind, 'nominal');
  assert.match(fact(programmable, 'watchdog_action').value, /only_register_bits_marked_WATCHDOG/);
  assert.ok(!products.get(programmable).some(item => item.element === 'battery' && item.name === 'autonomous_discharge_overcurrent_protection'));
});

test('converter protection thresholds keep input/output scope, tolerance and operating limits separate', () => {
  const product = 'ti_tps63802dlar';
  assert.equal(fact(product, 'autonomous_overvoltage_protection').value, true);
  for (const element of ['input_supply', 'output_supply']) {
    assert.deepEqual(['minimum', 'typical', 'maximum'].map(kind => fact(product, 'overvoltage_threshold', element, kind).value), [5.5, 5.7, 5.9]);
  }
  assert.match(fact(product, 'overvoltage_action', 'input_supply').value, /interrupts_negative_current/);
  assert.equal(fact(product, 'overvoltage_action', 'output_supply').value, 'output_OVP_stops_switching');
  assert.equal(fact(product, 'input_voltage_max').value, 5.5);
  assert.equal(fact(product, 'thermal_shutdown_temperature').value, 423.15);
  assert.equal(fact(product, 'thermal_shutdown_temperature').valueKind, 'typical');
  assert.equal(fact(product, 'operating_temperature_max').value, 398.15);
  assert.equal(fact(product, 'undervoltage_threshold', 'self', 'minimum').condition.values.operating_mode, 'once_started_vout_ge_1p8_vin_falling');
});

test('representative pre-existing fact identities and revisions remain pinned', () => {
  for (const [product, id, revision] of [
    ['isispace_iceps2_type_a', '7c2cb5f9d7065c9dce04e8499ecce60bba71e8b0488da43a941c3594d5dc8797', '491c003c672f19dd549decd2281bc5edc417d39c60877d964f4d245e8cb4d85a'],
    ['isispace_imeps2_base_4s1p', 'ec7f6414710b660474ce9fc7a36843c3e3d8d94e145e7f90fa33c5cfedcff296', '53b36efb8b1d29b4062158e55bd189557fddb73683353911a21476e3a07cd212'],
    ['ti_bq24650rvar', 'b5a0fc153a79317653171ede7291d1da41d706e41bb411caa8f057bbf9713732', '8bc1825e176b5228b6430277686286aeefe4a43df8bc035b85eeb47481950e9f'],
    ['ti_bq25798rqmr', '5fc682b7150a186eca5c01b4bbb091c9dea0f2e0ac2a2f60367ba3b2036cf485', '7211aa71673cf02ca1b9339c4bd407ee888fcdfcacfc89712a0cb5fe9c733bae'],
    ['ti_tps63802dlar', 'e96bb483b86bba5be41ea4497b70face5e9488b0fc1b8aae8eaa8b366db4bb7d', '9e77a76759ff158048a7aecdba3a00041c12bb640ebfe154dc5c9f3c2ec0aad2'],
  ]) assert.equal(products.get(product).find(item => item.id === id)?.revision, revision);
});

test('the Python worker resolves every enriched product and all new bindings, with stale selections pending', async () => {
  const catalog = (await loadCatalog()).map(({ requirements, ...type }) => type);
  for (const [product] of expected) {
    const workspace = emptyWorkspace(catalog), owner = workspace.elements.find(element => element.definition.endsWith('::PowerSubsystem')).key;
    const row = { key: 'protection', id: 'EPS001', context: owner, kind: 'Requirement', text: 'Manufacturer evidence.', condition: '', sources: [], affected: [], parameters: {} };
    workspace.statements = [row];
    workspace.components = [{ key: 'selected', id: 'CMP001', owner, product, requirements: [row.key],
      facts: added(product).map((item, index) => cotsBinding(item, { key: `new_${index}`, name: `new_${index}` })) }];
    setVerificationMethods(row, [{ key: 'manufacturer', component: 'selected', condition: 'True' }]);
    assert.equal((await evaluator.evaluate(workspace)).results[0].state, 'pass', product);
    workspace.components[0].facts.at(-1).revision = '0'.repeat(64);
    assert.equal((await evaluator.evaluate(workspace)).results[0].state, 'pending', product);
  }
});
