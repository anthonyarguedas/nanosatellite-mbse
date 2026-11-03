import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { loadCatalog, requirementsFromSource } from '../catalog.mjs';
import { addElementChildren, emptyWorkspace, migrateWorkspace, requirementMarkers, rewriteRowReferences, validateWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { evaluateChecks, evaluateExpression, parseExpression } from '../verification.mjs';
import { readWorkspace, renderExport, renderManaged } from '../sysml.mjs';

const catalog = await loadCatalog();
const templates = catalog.flatMap(type => type.requirements ?? []);
const find = (workspace, name, context) => workspace.statements.find(row => row.definition === `FrameworkRequirements::${name}` && (!context || row.context === context));
const set = (workspace, name, parameters) => Object.assign(find(workspace, name).parameters,
  Object.fromEntries(Object.entries(parameters).map(([key, value]) => [key, value === null ? null : String(value)])));
const values = workspace => new Map(evaluateChecks(workspace).map(result => [workspace.statements.find(row => row.key === result.key).definition.split('::').at(-1), result]));
const close = (actual, expected) => assert.ok(Math.abs(actual - expected) <= 1e-10 * Math.max(1, Math.abs(expected)), `${actual} != ${expected}`);

function populated() {
  const workspace = emptyWorkspace(catalog);
  set(workspace, 'OrbitPeriod', { altitude_km: 500 });
  set(workspace, 'LoadEnergy', { sunlight_power_W: 10, eclipse_power_W: 8, sunlight_duty: 0.6, eclipse_duty: 0.5 });
  set(workspace, 'MinimumPanelPower', { sunlight_efficiency: 0.8, eclipse_efficiency: 0.65 });
  set(workspace, 'SolarCellPower', { cell_eol_V: 2.4, cell_eol_A: 0.5 });
  set(workspace, 'SolarCellCount', { installed_cells: 100 });
  set(workspace, 'MissionCycles', { lifetime_years: 2, days_per_year: 365.25 });
  set(workspace, 'CycleLife', { cycle_a: 5000, cycle_b: -1, dod_max: 0.3, fit_dod_min: 0.05, fit_dod_max: 0.8 });
  set(workspace, 'MinimumBatteryEnergy', { degradation_margin: 0.2 });
  set(workspace, 'BatteryCapacityScreen', { pack_bol_J: 100000, retained_energy_factor: 0.8 });
  set(workspace, 'EPS11', { energy_start_J: 50000, energy_end_J: 50000, closure_tolerance_J: 1, soc_start: 0.9, soc_end: 0.9 });
  set(workspace, 'EPS19', { mass_kg: 0.9, mass_allocation_kg: 1, volume_m3: 0.002, volume_allocation_m3: 0.003 });
  set(workspace, 'EPS21', { required_data_bytes: 256, available_data_bytes: 512, required_program_bytes: 1024,
    available_program_bytes: 2048, required_utilization: 0.4, allocated_utilization: 0.6 });
  return validateWorkspace(workspace, catalog);
}

test('generic definitions retain only parameterized report requirements and sizing equations', async () => {
  const report = await readFile(new URL('../../../final_report/eps-requirements.tex', import.meta.url), 'utf8');
  const ids = [...report.matchAll(/label\{epsreq:EPS-(\d\d)\}/g)].map(match => match[1]);
  assert.equal(ids.length, 20);
  for (const id of ['02', '08', '09', '11', '19']) {
    assert.ok(ids.includes(id));
    const template = templates.find(row => row.model === `FrameworkRequirements::EPS${id}`);
    assert.ok(template, `Missing EPS-${id}`);
    assert.match(template.origin, new RegExp(`EPS-${id}$|EPS-${id};`));
    assert.match(template.text, new RegExp(`^EPS-${id}\\.`));
  }
  assert.equal(templates.length, 27);
  assert.ok(templates.every(template => Object.keys(template.parameters).length > 0 && !Object.hasOwn(template, 'formulas')
    && Object.values(template.parameters).every(value => value === null || typeof value === 'string')));
  for (const name of ['OrbitPeriod', 'IlluminationPeriods', 'LoadEnergy', 'MinimumPanelPower', 'SolarCellPower', 'SolarCellCount', 'MissionCycles', 'CycleLife', 'MinimumBatteryEnergy', 'BatteryCapacityScreen']) {
    const template = templates.find(row => row.name === name);
    assert.ok(template && template.condition);
    for (const parameter of Object.keys(template.parameters)) assert.ok(template.attributes[parameter]);
  }
  assert.match(templates.find(row => row.name === 'EPS21').origin, /eq:software-resource-screen/);
  assert.equal(templates.some(row => row.name === 'EPS22'), false);
  for (const template of templates) {
    const markers = requirementMarkers(template.text);
    assert.deepEqual(markers.errors, [], template.id);
    assert.ok(markers.names.every(name => Object.hasOwn(template.parameters, name)), template.id);
    assert.ok(markers.names.length, template.id);
    assert.doesNotMatch(template.text, /\{[A-Za-z_][A-Za-z0-9_]*\}/);
  }
  assert.throws(() => requirementsFromSource('package Missing {}'), /no requirements/);
});

test('generic requirements contain one requirement sentence without advisory notes', () => {
  const sentences = new Intl.Segmenter('en', { granularity: 'sentence' });
  for (const template of templates) {
    const text = template.text.replace(/^EPS-\d+\.\s*/, '');
    assert.equal([...sentences.segment(text)].length, 1, template.id);
    assert.match(text, /\bshall\b/, template.id);
    assert.doesNotMatch(text, /requires? (?:a separate|separate|additional) assessment|This screen|Convert Wh|No universal|Flight heritage alone/i, template.id);
  }
});

test('decomposed requirements retain their local derivation sources and parameter bindings', () => {
  const workspace = populated();
  for (const template of templates.filter(template => template.derivesFrom?.length)) {
    const row = find(workspace, template.name);
    for (const name of template.derivesFrom) assert.ok(row.sources.includes(find(workspace, name).key), `${row.id}: ${name}`);
  }
  assert.equal(find(workspace, 'EPS88').parameters.required_program_bytes, `${find(workspace, 'EPS21').id}.required_program_bytes`);
  assert.equal(values(workspace).get('EPS88').values.required_program_bytes, 1024);
  assert.equal(values(workspace).get('EPS78').values.volume_m3, 0.002);
  assert.equal(values(workspace).get('OrbitPeriodClosure').state, 'pass');
  assert.equal(values(workspace).get('EnergyPathEfficiencyBounds').state, 'pass');
});

test('generic table markers and numeric types must match their native parameters', async () => {
  const source = await readFile(new URL('../../requirements.sysml', import.meta.url), 'utf8');
  assert.throws(() => requirementsFromSource(source.replace('$$orbit_period_s$$', () => '$$undeclared$$')), /declared table parameter/);
  assert.throws(() => requirementsFromSource(source.replace('$$orbit_period_s$$', () => '$$invalid-name$$')), /declared table parameter/);
  assert.throws(() => requirementsFromSource(source.replace('attribute minimum_cells : Integer', 'attribute minimum_cells : Real')), /types must match/);
  assert.throws(() => requirementsFromSource(source.replace('"derivesFrom":["IlluminationPeriods"]', '"derivesFrom":["Missing"]')), /derivation sources/);
});

test('generic annotations require at least one numeric parameter referenced in their text', () => {
  const source = template => `requirement def Example { doc /* @requirements-ui\n${JSON.stringify({ id: 'EPS001', context: 'eps', affected: ['Batteries'], condition: '', ...template })}\n*/ attribute mass_kg : Real[0..1]; attribute assessed : Boolean[0..1]; }`;
  assert.throws(() => requirementsFromSource(source({ text: 'The pack shall be assessed.', parameters: {} })), /at least one numeric parameter/);
  assert.throws(() => requirementsFromSource(source({ text: 'The pack shall be assessed.', parameters: { mass_kg: null } })), /declared table parameter/);
  assert.throws(() => requirementsFromSource(source({ text: 'The pack shall satisfy $$assessed$$.', parameters: { assessed: null } })), /types must match/);
  assert.equal(requirementsFromSource(source({ text: 'The pack shall weigh at most $$mass_kg$$ kg.', parameters: { mass_kg: null } })).length, 1);
});

test('preloaded units seed parameter fields and stay out of requirement prose', () => {
  const workspace = emptyWorkspace(catalog);
  const units = new Map(workspace.variables.map(variable => [variable.name, variable.unit]));
  for (const template of templates) for (const [name, unit] of Object.entries(template.units ?? {})) {
    assert.equal(units.get(name), unit, `${template.id}.${name}`);
    assert.equal(template.text.includes(`$$${name}$$ ${unit}`), false, `${template.id}.${name}`);
  }
  assert.equal(units.get('gravitationalParameter_km3_s2'), 'km^3/s^2');
  assert.equal(units.get('volume_m3'), 'm^3');
  assert.equal(units.get('required_data_bytes'), 'bytes');
  assert.equal(units.get('days_per_year'), 'days/year');
  assert.equal(units.get('sunlight_efficiency'), undefined);
  assert.deepEqual(readWorkspace(renderManaged(workspace, { catalog }), catalog), workspace);
});

test('generic units must name declared parameters and agree across requirements', async () => {
  const source = await readFile(new URL('../../requirements.sysml', import.meta.url), 'utf8');
  assert.throws(() => requirementsFromSource(source.replace('"units":{"altitude_km":"km"', '"units":{"undeclared":"km"')), /units must name a declared parameter/);
  assert.throws(() => requirementsFromSource(source.replace('"units":{"altitude_km":"km"', '"units":{"altitude_km":""')), /contain a label/);
  assert.throws(() => requirementsFromSource(source.replace('"units":{"altitude_km":"km"', '"units":{"altitude_km":"m"')), /same units/);
});

test('a new mission seeds only sourced Earth constants as literal parameter values', () => {
  const workspace = emptyWorkspace(catalog);
  assert.equal(workspace.components.length, 0);
  const literals = [];
  for (const row of workspace.statements) for (const [name, expression] of Object.entries(row.parameters)) {
    if (expression !== null && parseExpression(expression).kind === 'literal') literals.push([row.id, name, expression]);
  }
  assert.deepEqual(literals, [['ORB001', 'earthRadius_km', '6378'], ['ORB001', 'gravitationalParameter_km3_s2', '398601']]);
});

test('a new mission starts with generic, assigned requirements and unset mission inputs', () => {
  const workspace = emptyWorkspace(catalog);
  assert.equal(workspace.statements.length, 27);
  assert.equal(workspace.stakeholders.length, 0);
  assert.equal(workspace.statements.filter(row => row.context === 'mission').length, 3);
  assert.ok(workspace.statements.every(row => row.affected.length && row.origin && row.definition));
  assert.ok(workspace.statements.every(row => row.rationale === row.origin));
  assert.equal(find(workspace, 'OrbitPeriod').parameters.altitude_km, null);
  assert.equal(find(workspace, 'OrbitPeriod').parameters.earthRadius_km, '6378');
  assert.equal(find(workspace, 'OrbitPeriod').parameters.gravitationalParameter_km3_s2, '398601');
  const checks = values(workspace);
  assert.equal(checks.get('OrbitPeriod').state, 'pending');
  assert.equal(checks.get('MinimumPanelPower').state, 'pending');
  assert.equal(checks.get('MinimumBatteryEnergy').state, 'pending');
  assert.ok([...checks.values()].every(row => !['pass', 'error'].includes(row.state)));
});

test('orbit parameters drive panel and battery sizing with consistent seconds, watts and joules', () => {
  const workspace = populated(), checks = values(workspace);
  const period = 2 * Math.PI * Math.sqrt((6378 + 500) ** 3 / 398601);
  const angle = Math.acos(6378 / (6378 + 500));
  const sunlight = (0.5 + angle / Math.PI) * period, eclipse = period - sunlight;
  const panel = (10 * 0.6 * sunlight / 0.8 + 8 * 0.5 * eclipse / 0.65) / sunlight;
  close(checks.get('OrbitPeriod').values.orbit_period_s, period);
  close(checks.get('IlluminationPeriods').values.sunlight_s, sunlight);
  close(checks.get('IlluminationPeriods').values.eclipse_s, eclipse);
  close(checks.get('LoadEnergy').values.sunlight_energy_J, 10 * 0.6 * sunlight);
  close(checks.get('MinimumPanelPower').values.panel_min_W, panel);
  close(checks.get('SolarCellPower').values.cell_eol_W, 1.2);
  close(checks.get('SolarCellCount').values.required_cells, panel / 1.2);
  assert.equal(checks.get('SolarCellCount').values.minimum_cells, Math.ceil(panel / 1.2));
  close(checks.get('MissionCycles').values.required_cycles, 2 * 365.25 * 86400 / period);
  close(checks.get('CycleLife').values.supported_cycles, 5000 * 0.3 ** -1);
  close(checks.get('MinimumBatteryEnergy').values.battery_min_J, 8 * 0.5 * eclipse / 0.3 * 1.2);
  close(checks.get('BatteryCapacityScreen').values.pack_eol_J, 80000);
  close(checks.get('EPS08').values.battery_min_J, checks.get('MinimumBatteryEnergy').values.battery_min_J);
  for (const [name, result] of checks) assert.equal(result.state, templates.find(template => template.name === name).condition ? 'pass' : 'unset', name);
  assert.equal(find(workspace, 'MinimumBatteryEnergy').parameters.battery_min_J, 'eclipse_energy_J / dod_max * (1 + degradation_margin)');
  set(workspace, 'OrbitPeriod', { altitude_km: 1000 });
  assert.notEqual(values(workspace).get('MinimumBatteryEnergy').values.battery_min_J, checks.get('MinimumBatteryEnergy').values.battery_min_J);
});

test('missing data, invalid domains, fit limits, integer counts and insufficient products stay visible', () => {
  let workspace = populated();
  set(workspace, 'MinimumPanelPower', { eclipse_efficiency: null });
  assert.equal(values(workspace).get('MinimumPanelPower').state, 'pending');
  workspace = populated();
  set(workspace, 'MinimumPanelPower', { sunlight_efficiency: 0 });
  assert.equal(values(workspace).get('MinimumPanelPower').state, 'fail');
  assert.equal(values(workspace).get('SolarCellCount').state, 'error');
  workspace = populated();
  set(workspace, 'CycleLife', { cycle_a: 1000 });
  assert.equal(values(workspace).get('CycleLife').state, 'fail');
  assert.equal(values(workspace).get('MinimumBatteryEnergy').state, 'fail');
  workspace = populated();
  set(workspace, 'CycleLife', { fit_dod_min: 0.4 });
  assert.equal(values(workspace).get('CycleLife').state, 'fail');
  workspace = populated();
  set(workspace, 'BatteryCapacityScreen', { pack_bol_J: 1 });
  assert.equal(values(workspace).get('BatteryCapacityScreen').state, 'fail');
  set(workspace, 'SolarCellCount', { installed_cells: 1 });
  assert.equal(values(workspace).get('SolarCellCount').state, 'fail');
  set(workspace, 'SolarCellCount', { installed_cells: 1.5 });
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  assert.equal(values(workspace).get('SolarCellCount').parameters.installed_cells.state, 'error');
  assert.throws(() => renderExport(workspace, { catalog }), /safe integer/);
  workspace = populated();
  set(workspace, 'MinimumPanelPower', { panel_min_W: '900 + 99' });
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  assert.equal(values(workspace).get('MinimumPanelPower').values.panel_min_W, 999);
});

test('edited derived expressions must still satisfy the generic sizing equations', () => {
  for (const [name, parameter, expression] of [
    ['OrbitPeriod', 'orbit_period_s', '1000'],
    ['IlluminationPeriods', 'horizon_angle_rad', '0.1'],
    ['IlluminationPeriods', 'sunlight_s', '1000'],
    ['LoadEnergy', 'sunlight_energy_J', '1'],
    ['MinimumPanelPower', 'panel_min_W', '999'],
    ['SolarCellPower', 'cell_eol_W', '5'],
    ['SolarCellCount', 'required_cells', '1'],
    ['SolarCellCount', 'minimum_cells', '1'],
    ['MissionCycles', 'orbits_per_day', '1'],
    ['MissionCycles', 'required_cycles', '1'],
    ['CycleLife', 'dod_cycle_limit', '1'],
    ['CycleLife', 'supported_cycles', '1000000'],
    ['MinimumBatteryEnergy', 'battery_min_J', '1'],
    ['BatteryCapacityScreen', 'pack_eol_J', '1'],
  ]) {
    const workspace = populated();
    set(workspace, name, { [parameter]: expression });
    assert.equal(values(workspace).get(name).state, 'fail', `${name}.${parameter}`);
    assert.doesNotThrow(() => renderExport(workspace, { catalog }));
  }
});

test('derived formulas are safe, numeric, bounded and detect cycles', () => {
  const workspace = populated(), row = find(workspace, 'OrbitPeriod');
  row.parameters.orbit_period_s = 'ORB001.orbit_period_s';
  assert.equal(values(workspace).get('OrbitPeriod').state, 'error');
  assert.throws(() => renderExport(workspace, { catalog }), /Cyclic parameter expression/);
  row.parameters.orbit_period_s = 'sqrt(-1)';
  assert.equal(values(workspace).get('OrbitPeriod').state, 'error');
  row.parameters.orbit_period_s = 'globalThis.fetch("/api/workspace")';
  assert.throws(() => renderExport(workspace, { catalog }), /ORB001.orbit_period_s/);
  assert.match(renderManaged(workspace, { catalog }), /Invalid parameter expression/);
  assert.equal(evaluateExpression(parseExpression('min(2, max(3, 4)) + abs(-2) + 2 ^ 3 ^ 2'), workspace, row), 516);
  assert.throws(() => parseExpression('sqrt(1, 2)'), /requires 1/);
  assert.throws(() => parseExpression('unknown(1)'), /Unsupported function/);
});

test('version 6 upgrades once and preserves mission data, IDs, components and source links', () => {
  const old = emptyWorkspace(catalog.map(({ requirements, ...type }) => type));
  old.version = 6;
  old.statements.push({ key: 'existing', id: 'ORB001', context: 'external', kind: 'Requirement', text: 'Existing orbit constraint',
    condition: 'x >= 300', parameters: { x: 500, y: null, z: null, a: null }, sources: ['domain-orbit'], affected: [] });
  old.components.push({ key: 'rtc', id: 'CMP001', owner: old.elements.find(row => row.definition.endsWith('::PowerSubsystem')).key,
    product: 'abracon_ab1805_t3', requirements: [] });
  const original = structuredClone(old), upgraded = migrateWorkspace(old, catalog);
  assert.deepEqual(old, original);
  assert.equal(upgraded.version, WORKSPACE_VERSION);
  assert.equal(upgraded.statements.length, 28);
  assert.deepEqual(upgraded.components, old.components);
  assert.deepEqual(upgraded.elements, old.elements);
  assert.deepEqual(upgraded.statements[0].sources, ['domain-orbit']);
  assert.equal(upgraded.statements[0].parameters.x, '500');
  assert.notEqual(find(upgraded, 'OrbitPeriod').id, 'ORB001');
  assert.match(find(upgraded, 'IlluminationPeriods').parameters.orbit_period_s, new RegExp(`^${find(upgraded, 'OrbitPeriod').id}\\.`));
  assert.doesNotThrow(() => validateWorkspace(upgraded, catalog));
  assert.equal(migrateWorkspace(upgraded, catalog), upgraded);
  upgraded.statements = upgraded.statements.filter(row => row.definition !== 'FrameworkRequirements::EPS89');
  assert.deepEqual(readWorkspace(renderManaged(upgraded, { catalog }), catalog), upgraded);
  assert.equal(upgraded.statements.length, 27);
});

test('ID changes preserve equation references, including simultaneous swaps', () => {
  const workspace = populated();
  const period = find(workspace, 'OrbitPeriod'), illumination = find(workspace, 'IlluminationPeriods');
  const periodId = period.id, illuminationId = illumination.id;
  rewriteRowReferences(workspace, new Map([[periodId, illuminationId], [illuminationId, periodId]]));
  period.id = illuminationId; illumination.id = periodId;
  assert.match(illumination.parameters.orbit_period_s, new RegExp(`^${period.id}\\.`));
  assert.match(find(workspace, 'LoadEnergy').parameters.sunlight_s, new RegExp(`^${illumination.id}\\.`));
  assert.equal(values(workspace).get('MinimumPanelPower').state, 'pass');
  assert.doesNotThrow(() => renderExport(workspace, { catalog }));
});

test('a second EPS gets independent inputs, formulas, assignments and local dependencies', () => {
  const workspace = populated();
  const power = { key: 'backup-power', id: 'PWR', name: 'Backup power', owner: 'domain-bus', definition: 'SpaceSegment::CubeSat::PowerSubsystem' };
  workspace.elements.push(power);
  addElementChildren(workspace, power, catalog);
  const count = workspace.statements.length;
  addElementChildren(workspace, power, catalog);
  assert.equal(workspace.statements.length, count);
  const energy = find(workspace, 'LoadEnergy', power.key), panel = find(workspace, 'MinimumPanelPower', power.key);
  assert.equal(workspace.statements.filter(row => row.context === power.key).length, 24);
  for (const name of ['EPS47', 'EPS52', 'EPS88']) {
    const child = find(workspace, name, power.key);
    assert.ok(child.sources.every(key => workspace.statements.find(row => row.key === key).context === power.key));
  }
  assert.ok(energy.affected.every(key => workspace.elements.find(row => row.key === key).owner === power.key));
  assert.equal(energy.parameters.sunlight_power_W, null);
  assert.match(panel.parameters.sunlight_energy_J, new RegExp(`^${energy.id}\\.`));
  assert.ok(panel.sources.includes(energy.key));
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  assert.deepEqual(readWorkspace(renderManaged(workspace, { catalog }), catalog), workspace);
});

test('another Orbit gets its own geometry and an ambiguous new EPS leaves orbit inputs unset', () => {
  const workspace = populated();
  const orbit = { key: 'second-orbit', id: 'ALT', name: 'Alternative orbit', owner: 'mission', definition: 'Orbit' };
  workspace.elements.push(orbit); addElementChildren(workspace, orbit, catalog);
  const period = workspace.statements.find(row => row.definition.endsWith('::OrbitPeriod') && row.affected.includes(orbit.key));
  const geometry = workspace.statements.find(row => row.definition.endsWith('::IlluminationPeriods') && row.affected.includes(orbit.key));
  assert.equal(geometry.parameters.orbit_period_s, `${period.id}.orbit_period_s`);
  const power = { key: 'alternative-power', id: 'PWR', name: 'Alternative power', owner: 'domain-bus', definition: 'SpaceSegment::CubeSat::PowerSubsystem' };
  workspace.elements.push(power); addElementChildren(workspace, power, catalog);
  const energy = find(workspace, 'LoadEnergy', power.key);
  assert.equal(energy.parameters.sunlight_s, null);
  assert.equal(Object.hasOwn(energy, 'formulas'), false);
  assert.doesNotThrow(() => renderExport(workspace, { catalog }));
});

test('mission export binds native generic requirements, orbit attributes, formulas and traceability', () => {
  const workspace = populated(), source = renderExport(workspace, { catalog, packageName: 'ExampleMission' });
  assert.doesNotMatch(source, /requirements-ui:data|<requirements-ui>|@OrbitPeriod/);
  assert.match(source, /package ExampleMission/);
  assert.match(source, /requirement .* : FrameworkRequirements::OrbitPeriod/);
  assert.match(source, /requirement .* : FrameworkRequirements::EPS02/);
  assert.match(source, /requirement .* : FrameworkRequirements::EPS21/);
  assert.match(source, /requirement .* : FrameworkRequirements::EPS89/);
  assert.doesNotMatch(source, /: FrameworkRequirements::(?:EPS01|EPS20|EPS22|EPS92)\s*\{/);
  assert.match(source, /attribute :>> 'required_data_bytes' = 256/);
  assert.match(source, /attribute :>> 'energy_end_J' = 50000/);
  assert.match(source, /attribute :>> 'mass_allocation_kg' = 1/);
  assert.match(source, /attribute :>> altitude_km = statement_generic_hORB_hOrbitPeriod\.'altitude_km'/);
  assert.match(source, /attribute :>> 'altitude_km' = 500/);
  assert.match(source, /attribute :>> 'orbit_period_s' = .*RealFunctions::sqrt/);
  assert.match(source, /TrigFunctions::arccos/);
  assert.match(source, /RealFunctions::floor/);
  assert.match(source, /attribute sourceReference/);
  assert.match(source, /dependency from statement_generic_hEPS_hMinimumPanelPower to statement_generic_hEPS_hLoadEnergy/);
  assert.deepEqual(readWorkspace(renderManaged(workspace, { catalog }), catalog), workspace);
  find(workspace, 'OrbitPeriod').condition = 'alert(1)';
  assert.throws(() => renderExport(workspace, { catalog }), /ORB001/);
});

test('draft and populated mission exports validate with the native SysML checker when available', async t => {
  if (spawnSync('syside', ['--version']).error) return t.skip('syside is not installed');
  const dir = await mkdtemp(join(tmpdir(), 'eps-sizing-sysml-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const framework = fileURLToPath(new URL('../../', import.meta.url));
  const libraries = (await readdir(framework)).filter(name => name.endsWith('.sysml')).map(name => join(framework, name));
  const draft = join(dir, 'draft.sysml'), filled = join(dir, 'filled.sysml');
  await writeFile(draft, renderExport(emptyWorkspace(catalog), { catalog, packageName: 'DraftMission' }));
  await writeFile(filled, renderExport(populated(), { catalog, packageName: 'FilledMission' }));
  const result = spawnSync('syside', ['check', ...libraries, draft, filled], { encoding: 'utf8', timeout: 120000 });
  assert.equal(result.status, 0, result.stdout + result.stderr);
});
