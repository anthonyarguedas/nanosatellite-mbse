import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { addElementChildren, allowedDefinitions, assignableElements, availableSources, contextForRow, emptyWorkspace, nextId, tabsFor, validateWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { evaluateChecks } from './helpers.mjs';
import { readWorkspace, serializeWorkspace as renderManaged, roundTrip } from './helpers.mjs';

// Hierarchy fixtures are intentionally unseeded. sizing.test.mjs covers templates.
const catalog = (await loadCatalog()).map(({ requirements, ...type }) => type);
const requirement = (id, context, affected = [], sources = []) => ({
  key: id.toLowerCase(), id, context, affected, sources, kind: 'Requirement', text: '', condition: '',
  parameters: { x: null, y: null, z: null, a: null },
});

const powerModel = 'SpaceSegment::CubeSat::PowerSubsystem';
const powerFor = workspace => workspace.elements.find(row => row.definition === powerModel);

function mission() {
  const workspace = emptyWorkspace(catalog), power = powerFor(workspace);
  workspace.statements = [
    requirement('REQ001', 'external'),
    requirement('MIS001', 'mission', ['domain-orbit', 'domain-bus'], ['req001']),
    requirement('BUS001', 'domain-bus', [workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem')).key], ['mis001']),
    requirement('PAY001', 'domain-payload', [workspace.elements.find(row => row.definition.endsWith('::Instrument')).key], ['mis001']),
    requirement('GND001', 'domain-ground', [workspace.elements.find(row => row.definition.endsWith('::NetworkSubsystem')).key], ['mis001']),
    requirement('EPS001', power.key, [workspace.elements.find(row => row.definition === `${powerModel}::Batteries`).key], ['bus001']),
  ];
  return workspace;
}

test('catalog projections use unique opaque identifiers and explicit parent relationships', () => {
  assert.equal(new Set(catalog.map(type => type.model)).size, catalog.length);
  for (const type of catalog) if (type.parent) assert.ok(catalog.some(parent => parent.model === type.parent));
});

test('catalog uses exactly the subsystem definitions in the generic mission model', () => {
  const byRole = role => catalog.filter(type => type.parent === catalog.find(type => type.role === role).model);
  assert.equal(byRole('bus').length, 8);
  assert.equal(byRole('ground').length, 8);
  assert.deepEqual(byRole('payload').map(type => type.name), ['Instrument', 'Processor and Memory']);
  assert.equal(byRole('bus').some(type => /Payload|SharedProcessor/.test(type.model)), false);
  assert.equal(catalog.some(type => type.model === 'GroundSegment::GroundStation'), true);
  assert.equal(catalog.find(type => type.model === powerModel).expandable, true);
  const components = catalog.filter(type => type.parent === powerModel);
  assert.deepEqual(components.map(type => type.name), ['Batteries', 'Solar Arrays', 'Processor and Memory', 'Regulators and Converters', 'Power Circuits and Switches', 'Software']);
  assert.ok(components.every(type => type.category === 'Component' && !type.expandable));
});

test('new generic subsystem definitions are discovered without UI changes', async () => {
  const extended = [...catalog, { model: 'SpaceSegment::CubeSat::ExperimentalSubsystem', name: 'Experimental', category: 'Subsystem', id: 'EXP', parent: 'SpaceSegment::CubeSat', role: 'subsystem', prefix: 'EXP', expandable: true }];
  const workspace = emptyWorkspace(extended);
  assert.ok(workspace.elements.some(row => row.definition === 'SpaceSegment::CubeSat::ExperimentalSubsystem'));
  assert.doesNotThrow(() => validateWorkspace(workspace, extended));
});

test('new generic EPS component definitions are discovered without UI changes', async () => {
  const extended = [...catalog, { model: `${powerModel}::Fuse`, name: 'Fuse', category: 'Component', id: 'FUS', parent: powerModel, expandable: false }];
  const workspace = emptyWorkspace(extended), power = powerFor(workspace);
  assert.ok(workspace.elements.some(row => row.definition === `${powerModel}::Fuse` && row.owner === power.key));
  assert.equal(allowedDefinitions(workspace, power.key, extended).length, 7);
  assert.doesNotThrow(() => validateWorkspace(workspace, extended));
});

test('default workbook exposes all CSRM spacecraft subsystem tabs and no Orbit tab', () => {
  const workspace = emptyWorkspace(catalog);
  assert.deepEqual(tabsFor(workspace, catalog).map(tab => tab.label), ['External', 'Mission', 'CubeSat Bus', 'CDH', 'Communications', 'ADCS', 'GNC', 'Structures', 'Thermal', 'Propulsion', 'EPS', 'Payload', 'Ground Station']);
  assert.deepEqual(workspace.elements.filter(row => row.owner === 'mission').map(row => row.name), ['Orbit', 'CubeSat Bus', 'Payload', 'Ground Station']);
  assert.equal(workspace.elements.length, 52);
  assert.equal(tabsFor(workspace, catalog).some(tab => tab.key === 'domain-orbit'), false);
  assert.equal(new Set(workspace.elements.map(row => row.id)).size, 52);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('EPS uses its Power subsystem key and the shared component and requirements tables', () => {
  const workspace = mission(), power = powerFor(workspace);
  const tab = tabsFor(workspace, catalog).find(tab => tab.key === power.key);
  assert.deepEqual(tab, { key: power.key, label: 'EPS', leftTitle: 'EPS Components',
    requirementsTitle: 'EPS Parametric Requirements', affectedLabel: 'Affected components', prefix: 'EPS' });
  assert.equal(allowedDefinitions(workspace, power.key, catalog).length, 6);
  assert.equal(assignableElements(workspace, workspace.statements[5]).length, 6);
  assert.ok(workspace.elements.filter(row => row.owner === power.key).every(row => contextForRow(row) === tab.key));
  assert.equal(nextId(workspace, 'Requirement', tab.prefix), 'EPS002');
});

test('requirements can be traced across tabs and assigned to multiple local elements', () => {
  const workspace = mission();
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  assert.equal(assignableElements(workspace, workspace.statements[1]).length, 4);
  assert.equal(assignableElements(workspace, workspace.statements[2]).length, 8);
  assert.ok(availableSources(workspace, 'bus001').some(row => row.key === 'mis001'));
  assert.equal(availableSources(workspace, 'req001').some(row => row.key === 'bus001'), false);
  assert.equal(availableSources(workspace, 'req001').some(row => row.key === 'eps001'), false);
  assert.ok(availableSources(workspace, 'eps001').some(row => row.key === 'bus001'));
  assert.equal(assignableElements(workspace, workspace.statements[0]).length, 0);
});

test('assignments and element types respect the hierarchy', () => {
  const workspace = mission();
  workspace.statements[2].affected = ['domain-bus'];
  assert.throws(() => validateWorkspace(workspace, catalog), /left table/);
  workspace.statements[2].affected = [];
  const power = workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem'));
  power.owner = 'domain-payload';
  assert.throws(() => validateWorkspace(workspace, catalog), /generic mission model/);
  assert.equal(allowedDefinitions(workspace, 'domain-orbit', catalog).length, 0);
});

test('EPS assignments stay local and its components cannot move to other tables', () => {
  const workspace = mission(), power = powerFor(workspace);
  const row = workspace.statements[5];
  for (const key of [power.key, 'domain-bus', workspace.elements.find(element => element.owner === 'domain-payload').key]) {
    row.affected = [key];
    assert.throws(() => validateWorkspace(workspace, catalog), /left table/);
  }
  row.affected = [];
  const battery = workspace.elements.find(element => element.definition === `${powerModel}::Batteries`);
  battery.owner = 'domain-bus';
  assert.throws(() => validateWorkspace(workspace, catalog), /generic mission model/);
});

test('Orbit cannot own a requirements tab or child rows', () => {
  const workspace = mission(); workspace.statements[1].context = 'domain-orbit';
  assert.throws(() => validateWorkspace(workspace, catalog), /tab does not exist/);
});

test('renaming domains preserves tab identity, source links and assignments', () => {
  const workspace = mission(), bus = workspace.elements.find(row => row.key === 'domain-bus');
  bus.name = 'Platform'; bus.id = 'PLT';
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  assert.equal(tabsFor(workspace, catalog).find(tab => tab.key === bus.key).label, 'Platform');
  assert.deepEqual(workspace.statements[1].affected, ['domain-orbit', 'domain-bus']);
  assert.equal(workspace.statements[2].context, bus.key);
});

test('renaming EPS preserves its tab, children, requirements and incoming links', () => {
  const workspace = mission(), power = powerFor(workspace);
  const before = structuredClone(workspace.statements);
  power.name = 'Flight Power'; power.id = 'PWR';
  assert.equal(tabsFor(workspace, catalog).find(tab => tab.key === power.key).label, 'Flight Power');
  assert.equal(workspace.elements.filter(row => row.owner === power.key).length, 6);
  assert.deepEqual(workspace.statements, before);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('another Power subsystem gets its own EPS tab and component instances', () => {
  const workspace = mission();
  const duplicate = { key: 'backup-power', id: 'PWR', name: 'Power', owner: 'domain-bus', definition: powerModel };
  workspace.elements.push(duplicate); addElementChildren(workspace, duplicate, catalog);
  addElementChildren(workspace, duplicate, catalog);
  assert.equal(workspace.elements.filter(row => row.owner === duplicate.key).length, 6);
  assert.equal(tabsFor(workspace, catalog).find(tab => tab.key === powerFor(workspace).key).label, 'EPS (EPS)');
  assert.equal(tabsFor(workspace, catalog).find(tab => tab.key === duplicate.key).label, 'EPS (PWR)');
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('another domain instance reuses the same table and subsystem catalog', () => {
  const workspace = mission();
  const duplicate = { key: 'backup-bus', id: 'BAK', name: 'Backup Bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' };
  workspace.elements.push(duplicate); addElementChildren(workspace, duplicate, catalog);
  assert.equal(workspace.elements.filter(row => row.owner === duplicate.key).length, 8);
  const power = workspace.elements.find(row => row.owner === duplicate.key && row.definition === powerModel);
  assert.equal(workspace.elements.filter(row => row.owner === power.key).length, 6);
  assert.equal(tabsFor(workspace, catalog).length, 22);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('new elements avoid ID collisions with existing stakeholders', () => {
  const workspace = mission(); workspace.stakeholders.push({ key: 'stakeholder', id: 'BAK', name: 'Existing stakeholder', type: 'Partner' });
  assert.notEqual(nextId(workspace, 'Element', 'Backup bus'), 'BAK');
  validateWorkspace(workspace, catalog);
});

test('current JSON reopens the hierarchy without reseeding components or requirements', () => {
  const workspace = mission(), power = powerFor(workspace);
  workspace.elements = workspace.elements.filter(row => row.owner !== power.key);
  workspace.statements = workspace.statements.filter(row => row.context !== power.key);
  assert.deepEqual(readWorkspace(renderManaged(workspace), catalog), workspace);
  assert.equal(readWorkspace(renderManaged(workspace), catalog).elements.filter(row => row.owner === power.key).length, 0);
});

test('expressions read variable values across all tab contexts', () => {
  const workspace = mission();
  workspace.statements[1].parameters.x = '25';
  workspace.statements[2].parameters.x = '20';
  workspace.statements[2].condition = 'x <= MIS001.x';
  assert.equal(evaluateChecks(workspace).find(row => row.key === 'bus001').state, 'pass');
  workspace.statements[5].parameters.x = '15';
  workspace.statements[5].condition = 'x <= BUS001.x and x <= MIS001.x';
  assert.equal(evaluateChecks(workspace).find(row => row.key === 'eps001').state, 'pass');
  workspace.statements[1].parameters.x = '10';
  assert.equal(evaluateChecks(workspace).find(row => row.key === 'bus001').state, 'fail');
  assert.equal(evaluateChecks(workspace).find(row => row.key === 'eps001').state, 'fail');
});

test('JSON snapshots preserve the complete hierarchy, assignments and traceability', () => {
  const workspace = mission(), snapshot = roundTrip(workspace), power = powerFor(snapshot);
  assert.equal(snapshot.elements.find(row => row.owner === power.key).definition, `${powerModel}::Batteries`);
  assert.deepEqual(snapshot.statements[1].affected, ['domain-orbit', 'domain-bus']);
  assert.deepEqual(snapshot.statements[5].sources, ['bus001']);
  assert.equal(snapshot.statements[5].context, power.key);
  assert.deepEqual(snapshot, workspace);
});

test('stable element references work regardless of element ordering', () => {
  const workspace = mission();
  workspace.statements[5].sources.push(workspace.statements[5].affected[0]); workspace.elements.reverse();
  const restored = roundTrip(workspace);
  assert.doesNotThrow(() => validateWorkspace(restored, catalog));
  assert.deepEqual(restored.statements[5].sources, workspace.statements[5].sources);
});
