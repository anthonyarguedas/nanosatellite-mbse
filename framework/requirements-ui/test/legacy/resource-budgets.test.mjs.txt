import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import * as cotsCatalog from '../cots.mjs';
import { addElementChildren, addPowerLimits, addResourceBudgets, emptyWorkspace, MAX_VARIABLES, requirementParameterNames, rewriteRowReferences, validateWorkspace } from '../model.mjs';
import { powerFor } from '../power.mjs';
import { budgetResources, isResourceRequirement, parentResourceLimit, resourceForRequirement, resourceLimitFor, resourceScopes, resourceSumExpression } from '../resource-budgets.mjs';
import { createServer } from '../server.mjs';
import { createSessions } from '../sessions.mjs';
import { canonicalWorkspace, createStore } from '../storage.mjs';
import { evaluateChecks } from './helpers.mjs';

const catalog = await loadCatalog();
function fixture() {
  const workspace = addResourceBudgets(emptyWorkspace(catalog));
  workspace.resourceBudgets = true;
  const battery = workspace.elements.find(element => element.definition.endsWith('::Batteries'));
  return { workspace, battery };
}
function populated() {
  const { workspace, battery } = fixture();
  for (const row of workspace.statements.filter(isResourceRequirement)) {
    const resource = resourceForRequirement(row);
    row.parameters[resource.limit] = '0';
    if (row.definition.includes('::Component')) row.parameters[resource.value] = '0';
  }
  return { workspace, battery };
}
async function directory(t) {
  const path = await mkdtemp(join(tmpdir(), 'resource-budgets-'));
  t.after(() => rm(path, { recursive: true, force: true }));
  return path;
}

test('mass and volume seed every spacecraft hardware scope without modes and retain the existing EPS inputs', () => {
  const original = emptyWorkspace(catalog), { workspace } = fixture();
  const scopes = resourceScopes(workspace), budgets = workspace.statements.filter(isResourceRequirement);
  assert.equal(budgets.length, scopes.length * 2);
  assert.equal(workspace.variables.length, original.variables.length + 2);
  assert.deepEqual(workspace.power, original.power);
  for (const old of original.statements) {
    const row = workspace.statements.find(row => row.key === old.key);
    assert.deepEqual({ ...row, parameters: old.parameters }, old);
    for (const [name, expression] of Object.entries(old.parameters)) assert.equal(row.parameters[name], expression);
  }
  for (const row of budgets) {
    const resource = resourceForRequirement(row), parent = parentResourceLimit(workspace, row);
    assert.equal(row.parameters[resource.limit], null);
    assert.ok(row.text.includes(`$$${resource.limit}$$`));
    assert.equal(row.text.split('.').length, 2);
    assert.ok(requirementParameterNames(workspace, row, catalog).includes(resource.value));
    if (parent) assert.ok(row.sources.includes(parent.key));
    if (row.definition.includes('::Component')) assert.equal(row.parameters[resource.value], null);
    else for (const name of [resource.value, resource.allocated]) assert.equal(row.parameters[name], resourceSumExpression(workspace, row, name));
  }
  for (const element of workspace.elements.filter(row => /::(?:Batteries|SolarArrays|StaticMount|ThermalSink|PropellantStorage)$/.test(row.definition))) {
    assert.equal(powerFor(workspace, element).accounting, 'excluded');
    assert.ok(budgetResources.every(resource => resourceLimitFor(workspace, element.key, resource)));
  }
  assert.ok(workspace.elements.filter(row => row.definition.endsWith('::Software')).every(element => !scopes.some(scope => scope.key === element.key)));
  assert.ok(scopes.every(scope => scope.key === 'mission' || !workspace.elements.find(row => row.key === scope.key).definition.startsWith('GroundSegment')));
  workspace.power.modes.push({ key: 'nominal', name: 'Nominal', sunlight: 100, eclipse: 100 });
  addPowerLimits(workspace);
  assert.equal(workspace.variables.length, original.variables.length + 5);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('static totals and child allocations verify independently for both resources with no spacecraft modes', () => {
  for (const resource of budgetResources) {
    const { workspace, battery } = populated();
    const system = resourceLimitFor(workspace, 'mission', resource), subsystem = resourceLimitFor(workspace, battery.owner, resource), component = resourceLimitFor(workspace, battery.key, resource);
    system.parameters[resource.limit] = '10'; subsystem.parameters[resource.limit] = '4'; component.parameters[resource.limit] = '3';
    component.parameters[resource.value] = '2 * 1';
    const check = row => evaluateChecks(workspace).find(result => result.key === row.key);
    assert.equal(check(system).values[resource.allocated], 4);
    assert.equal(check(system).values[resource.value], 2);
    assert.equal(check(subsystem).values[resource.allocated], 3);
    assert.equal(check(subsystem).values[resource.value], 2);
    assert.equal(check(system).state, 'pass'); assert.equal(check(subsystem).state, 'pass'); assert.equal(check(component).state, 'pass');
    system.parameters[resource.limit] = '3';
    assert.equal(check(system).state, 'fail'); assert.equal(subsystem.parameters[resource.limit], '4');
    system.parameters[resource.limit] = '10'; component.parameters[resource.limit] = '5';
    assert.equal(check(subsystem).state, 'fail');
    component.parameters[resource.limit] = '1'; assert.equal(check(component).state, 'fail');
    component.parameters[resource.value] = '-1'; assert.equal(check(component).state, 'fail');
    component.parameters[resource.value] = null; assert.equal(check(subsystem).state, 'pending');
    component.parameters[resource.value] = '2'; component.parameters[resource.limit] = null;
    assert.equal(check(component).state, 'pending'); assert.equal(check(subsystem).state, 'pending');
  }
});

test('seeding preserves edited and cleared expressions, extends default sums and follows new element instances and ID renames', () => {
  const { workspace, battery } = fixture(), mass = budgetResources[0], volume = budgetResources[1];
  const massParent = resourceLimitFor(workspace, battery.owner, mass), volumeParent = resourceLimitFor(workspace, battery.owner, volume);
  massParent.parameters.mass_kg = `(${massParent.parameters.mass_kg}) * 1.1`;
  massParent.parameters.allocated_mass_kg = null;
  massParent.parameters.mass_allocation_kg = '2';
  const original = structuredClone(workspace);
  addResourceBudgets(workspace); assert.deepEqual(workspace, original);
  const added = { ...battery, key: 'backup-battery', id: 'BKP' };
  workspace.elements.push(added); addElementChildren(workspace, added, catalog);
  assert.ok(volumeParent.parameters.volume_m3.includes(`${resourceLimitFor(workspace, added.key, volume).id}.volume_m3`));
  assert.equal(volumeParent.parameters.allocated_volume_m3, resourceSumExpression(workspace, volumeParent, volume.allocated));
  assert.equal(massParent.parameters.mass_kg, original.statements.find(row => row.key === massParent.key).parameters.mass_kg);
  assert.equal(massParent.parameters.allocated_mass_kg, null); assert.equal(massParent.parameters.mass_allocation_kg, '2');
  const child = resourceLimitFor(workspace, added.key, volume), previousId = child.id;
  child.id = 'NEW123'; rewriteRowReferences(workspace, new Map([[previousId, child.id]]));
  assert.ok(volumeParent.parameters.volume_m3.includes('NEW123.volume_m3'));
  workspace.elements.reverse(); workspace.statements.reverse();
  addResourceBudgets(workspace); assert.ok(volumeParent.parameters.volume_m3.includes('NEW123.volume_m3'));
  for (const [key, definition] of [['another-bus', 'SpaceSegment::CubeSat'], ['another-payload', 'SpaceSegment::CubeSat::PayloadSubsystem']]) {
    const element = { key, id: key.endsWith('bus') ? 'BUZ' : 'PAZ', name: key, owner: 'mission', definition };
    workspace.elements.push(element); addElementChildren(workspace, element, catalog);
  }
  for (const resource of budgetResources) {
    const system = resourceLimitFor(workspace, 'mission', resource);
    assert.equal(system.parameters[resource.value], resourceSumExpression(workspace, system, resource.value));
    assert.equal(system.parameters[resource.allocated], resourceSumExpression(workspace, system, resource.allocated));
  }
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('missing budget requirements stay unresolved and empty scopes have explicit zero sums', () => {
  const { workspace, battery } = fixture(), resource = budgetResources[0];
  const parent = resourceLimitFor(workspace, battery.owner, resource), child = resourceLimitFor(workspace, battery.key, resource);
  workspace.statements = workspace.statements.filter(row => row.key !== child.key);
  assert.equal(resourceSumExpression(workspace, parent, resource.value), 'None');
  parent.parameters.mass_kg = resourceSumExpression(workspace, parent, resource.value);
  assert.equal(evaluateChecks(workspace).find(row => row.key === parent.key).parameters.mass_kg.state, 'pending');
  const children = new Set(workspace.elements.filter(row => row.owner === battery.owner).map(row => row.key));
  workspace.elements = workspace.elements.filter(row => !children.has(row.key));
  workspace.statements = workspace.statements.filter(row => !children.has(row.budgetScope));
  assert.equal(resourceSumExpression(workspace, parent, resource.value), '0');
  assert.equal(resourceSumExpression(workspace, parent, resource.allocated), '0');
});

test('resource scope validation rejects duplicate limits, software budgets and detached source and assignment links', () => {
  const mutations = [
    (workspace, row) => { workspace.statements.push({ ...row, key: 'duplicate', id: 'MSC999' }); },
    (workspace, row) => { row.budgetScope = workspace.elements.find(row => row.definition.endsWith('::Software')).key; },
    (workspace, row) => { row.context = 'mission'; },
    (workspace, row) => { row.sources = []; },
    (workspace, row) => { row.affected = []; },
    (workspace, row) => { row.definition = 'ResourceBudgetModel::MassLimit'; },
    (workspace, row) => { row.definition = undefined; },
  ];
  for (const mutate of mutations) {
    const { workspace, battery } = fixture(), row = resourceLimitFor(workspace, battery.key, budgetResources[0]);
    mutate(workspace, row); assert.throws(() => validateWorkspace(workspace, catalog));
  }
  for (const mutate of [
    workspace => { workspace.variables.find(row => row.name === 'mass_kg').type = 'integer'; },
    workspace => { workspace.variables.find(row => row.name === 'volume_m3').unit = 'cm^3'; },
    workspace => { while (workspace.variables.length < MAX_VARIABLES) workspace.variables.push({ name: `unused_${workspace.variables.length}`, type: 'float' }); },
  ]) {
    const workspace = emptyWorkspace(catalog); mutate(workspace);
    const original = structuredClone(workspace);
    assert.throws(() => addResourceBudgets(workspace), /requires a Float|256 parameter limit/);
    assert.deepEqual(workspace, original);
  }
});

test('mass and volume expressions reuse pinned COTS facts, explicit quantities and dimensions without copying catalogue values', { skip: !cotsCatalog.loadCotsFacts }, async () => {
  const { cotsBinding, mergeCotsDraft } = await import('../cots-bindings.mjs');
  const { workspace, battery } = populated(), { facts } = await cotsCatalog.loadCotsFacts('isispace_iceps2_type_a');
  const selections = ['mass', 'length', 'width', 'height'].map(name => cotsBinding(facts.find(fact => fact.name === name), { key: name, name }));
  workspace.components.push({ key: 'board', id: 'CMP001', owner: battery.owner, product: 'isispace_iceps2_type_a', facts: selections, requirements: [] });
  for (const resource of budgetResources) for (const scope of ['mission', battery.owner, battery.key]) resourceLimitFor(workspace, scope, resource).parameters[resource.limit] = '1';
  const mass = resourceLimitFor(workspace, battery.key, budgetResources[0]), volume = resourceLimitFor(workspace, battery.key, budgetResources[1]);
  mass.parameters.mass_kg = '2 * CMP001.mass';
  volume.parameters.volume_m3 = '2 * CMP001.length * CMP001.width * CMP001.height';
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  let results = evaluateChecks(workspace);
  assert.equal(results.find(row => row.key === mass.key).values.mass_kg, 2 * 0.184);
  assert.ok(Math.abs(results.find(row => row.key === volume.key).values.volume_m3 - 2 * 0.096 * 0.092 * 0.0265) < 1e-12);
  assert.equal(results.find(row => row.key === mass.key).state, 'pass');
  const edited = structuredClone(workspace.components[0]); edited.facts[0].name = 'unit_mass_kg';
  const renamed = mergeCotsDraft(workspace, workspace.components[0], edited);
  assert.equal(renamed.statements.find(row => row.key === mass.key).parameters.mass_kg, '2 * CMP001.unit_mass_kg');
  workspace.components[0].facts[0].revision = '0'.repeat(64);
  results = evaluateChecks(workspace);
  assert.equal(results.find(row => row.key === mass.key).state, 'pending');
  assert.equal(results.find(row => row.key === resourceLimitFor(workspace, 'mission', budgetResources[0]).key).state, 'pending');
  workspace.components[0].product = 'pumpkin_epsm1_rev_c';
  assert.equal(evaluateChecks(workspace).find(row => row.key === volume.key).state, 'pending');
  assert.ok(workspace.components[0].facts.every(binding => !Object.hasOwn(binding, 'value')));
});

test('current and saved missions initialize budgets on read without writes and retain deletions, drafts and independent session limits', async t => {
  const root = await directory(t), path = join(root, 'mission.json'), original = emptyWorkspace(catalog);
  original.statements[0].parameters.altitude_km = '600';
  const source = JSON.stringify(original, null, 2) + '\n'; await writeFile(path, source);
  const sessions = createSessions(path, { catalog });
  const current = (await sessions.get()).store, opened = await current.read();
  assert.equal(await readFile(path, 'utf8'), source);
  assert.equal(opened.workspace.resourceBudgets, true);
  assert.ok(opened.workspace.statements.some(isResourceRequirement));
  assert.equal(original.resourceBudgets, undefined);
  const copy = await sessions.create({ name: 'Existing mission copy', template: 'copy', workspace: original });
  assert.ok(copy.workspace.statements.some(isResourceRequirement));
  const system = resourceLimitFor(opened.workspace, 'mission', budgetResources[0]);
  system.parameters.mass_allocation_kg = '5 + 1'; system.rationale = 'Independent mission mass allowance.';
  const deleted = opened.workspace.statements.find(row => row.definition === 'ResourceBudgetModel::ComponentMassLimit');
  opened.workspace.statements = opened.workspace.statements.filter(row => row.key !== deleted.key);
  const saved = await current.save(opened.workspace, opened.revision);
  assert.deepEqual((await createStore(path, { catalog }).read()).workspace, saved.workspace);
  assert.ok(!saved.workspace.statements.some(row => row.key === deleted.key));
  assert.equal(resourceLimitFor((await (await sessions.get(copy.session.id)).store.read()).workspace, 'mission', budgetResources[0]).parameters.mass_allocation_kg, null);
  assert.deepEqual((await canonicalWorkspace(saved.workspace, { catalog })).workspace, saved.workspace);
  const blank = await sessions.create({ name: 'Blank mission', template: 'blank' });
  assert.equal(blank.workspace.statements.length, 0); assert.equal(blank.workspace.elements.length, 0);
  const bus = { key: 'first-bus', id: 'BUS', name: 'Bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' };
  blank.workspace.elements.push(bus); addElementChildren(blank.workspace, bus, catalog);
  assert.ok(budgetResources.every(resource => resourceLimitFor(blank.workspace, 'mission', resource)));
  assert.doesNotThrow(() => validateWorkspace(blank.workspace, catalog));
});

test('browser edits static budgets in the existing requirement pane and preserves cancel, export, save and reload', { skip: !process.env.PLAYWRIGHT_MODULE }, async t => {
  const { chromium } = await import(process.env.PLAYWRIGHT_MODULE), root = await directory(t), path = join(root, 'mission.json');
  const { workspace, battery } = populated(), resource = budgetResources[0];
  const system = resourceLimitFor(workspace, 'mission', resource), component = resourceLimitFor(workspace, battery.key, resource);
  await writeFile(path, JSON.stringify(workspace));
  const server = createServer({ modelPath: path }); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  t.after(async () => { await browser.close(); await new Promise(resolve => { server.close(resolve); server.closeAllConnections(); }); });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1100 }, acceptDownloads: true }), errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const pane = page.locator('#requirement-editor'), base = `http://127.0.0.1:${server.address().port}`;
  const saved = () => page.waitForFunction(() => document.querySelector('#status').textContent === '');
  const open = row => page.locator(`[data-requirement-edit="${row.key}"]`).click();
  await page.goto(`${base}/#mission`); await open(system);
  const limit = pane.getByLabel('Expression for mass_allocation_kg', { exact: true });
  assert.equal(await pane.getByLabel('Expression for mass_kg', { exact: true }).inputValue(), system.parameters.mass_kg);
  assert.equal(await pane.getByLabel('Expression for allocated_mass_kg', { exact: true }).isEditable(), true);
  await limit.fill('5'); await pane.getByRole('button', { name: 'Cancel', exact: true }).click();
  await open(system); assert.equal(await limit.inputValue(), '0');
  await limit.fill('10'); await pane.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  await page.getByRole('tab', { name: 'EPS', exact: true }).click(); await open(component);
  await pane.getByLabel('Expression for mass_kg', { exact: true }).fill('2 * 0.184');
  await pane.getByLabel('Expression for mass_allocation_kg', { exact: true }).fill('0.5');
  const downloadPromise = page.waitForEvent('download'); await page.getByRole('button', { name: 'Export workspace JSON', exact: true }).click();
  const download = await downloadPromise, exported = JSON.parse(await readFile(await download.path(), 'utf8'));
  assert.equal(exported.statements.find(row => row.key === component.key).parameters.mass_kg, '2 * 0.184');
  assert.equal(JSON.parse(await readFile(path, 'utf8')).statements.find(row => row.key === component.key).parameters.mass_kg, '0');
  await pane.getByRole('button', { name: 'Save requirement', exact: true }).click(); await saved();
  await page.reload(); await open(component);
  assert.equal(await pane.getByLabel('Expression for mass_kg', { exact: true }).inputValue(), '2 * 0.184');
  assert.equal(await page.getByRole('table', { name: 'Component state allocation', exact: true }).count(), 0);
  assert.deepEqual(errors, []);
});
