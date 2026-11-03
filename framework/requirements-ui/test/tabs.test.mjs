import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { catalogFromSource, indexDefinitions, loadCatalog } from '../catalog.mjs';
import { addElementChildren, allowedDefinitions, assignableElements, availableSources, contextForRow, emptyWorkspace, migrateWorkspace, nextId, tabsFor, validateWorkspace } from '../model.mjs';
import { evaluateChecks } from '../verification.mjs';
import { readWorkspace, renderManaged } from '../sysml.mjs';

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

test('structural index ignores comments and strings and preserves definition scopes', () => {
  const definitions = indexDefinitions('package P { doc /* part def Fake; */ attribute label : String = "part def Wrong;"; part def Outer { assert constraint c { true } part def Inner; } part def Sibling; }');
  assert.deepEqual(definitions.map(row => row.model), ['P::Outer', 'P::Outer::Inner', 'P::Sibling']);
  assert.deepEqual(indexDefinitions('package P { part /* note */ def A; }').map(row => row.model), ['P::A']);
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
  const source = await readFile(new URL('../../mission.sysml', import.meta.url), 'utf8');
  const extended = catalogFromSource(source.replace('        part def PowerSubsystem :>', '        part def ExperimentalSubsystem;\n        part def PowerSubsystem :>'));
  const workspace = emptyWorkspace(extended);
  assert.ok(workspace.elements.some(row => row.definition === 'SpaceSegment::CubeSat::ExperimentalSubsystem'));
  assert.doesNotThrow(() => validateWorkspace(workspace, extended));
});

test('new generic EPS component definitions are discovered without UI changes', async () => {
  const source = await readFile(new URL('../../mission.sysml', import.meta.url), 'utf8');
  const extended = catalogFromSource(source.replace('            part def Batteries :>', '            part def Fuse;\n            part def Batteries :>'));
  const workspace = emptyWorkspace(extended), power = powerFor(workspace);
  assert.ok(workspace.elements.some(row => row.definition === `${powerModel}::Fuse` && row.owner === power.key));
  assert.equal(allowedDefinitions(workspace, power.key, extended).length, 7);
  assert.doesNotThrow(() => validateWorkspace(workspace, extended));
});

test('default workbook has six tabs, four mission domains and no Orbit tab', () => {
  const workspace = emptyWorkspace(catalog);
  assert.deepEqual(tabsFor(workspace, catalog).map(tab => tab.label), ['External', 'Mission', 'CubeSat Bus', 'EPS', 'Payload', 'Ground Station']);
  assert.deepEqual(workspace.elements.filter(row => row.owner === 'mission').map(row => row.name), ['Orbit', 'CubeSat Bus', 'Payload', 'Ground Station']);
  assert.equal(workspace.elements.length, 28);
  assert.equal(tabsFor(workspace, catalog).some(tab => tab.key === 'domain-orbit'), false);
  assert.equal(new Set(workspace.elements.map(row => row.id)).size, 28);
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
  assert.equal(tabsFor(workspace, catalog).length, 8);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('version 2 upgrades into External while preserving values and avoiding ID collisions', () => {
  const old = { version: 2, variables: [{ name: 'mass', type: 'float' }],
    stakeholders: [{ key: 'stakeholder', id: 'BUS', name: 'Existing stakeholder', type: 'Partner' }],
    statements: [{ key: 'original', id: 'REQ001', kind: 'Requirement', text: 'Original', sources: ['stakeholder'], verified: true, condition: 'mass > 0', parameters: { mass: 2 } }] };
  const upgraded = migrateWorkspace(old, catalog);
  assert.doesNotThrow(() => validateWorkspace(upgraded, catalog));
  assert.equal(upgraded.statements[0].context, 'external');
  assert.equal(upgraded.statements[0].parameters.mass, '2');
  assert.equal(Object.hasOwn(upgraded.statements[0], 'verified'), false);
  assert.equal(upgraded.statements[0].condition, 'mass > 0');
  assert.deepEqual(upgraded.statements[0].sources, ['stakeholder']);
  assert.deepEqual(upgraded.statements[0].affected, []);
  assert.notEqual(upgraded.elements.find(row => row.key === 'domain-bus').id, 'BUS');
});

test('version 4 adds EPS components once while preserving existing rows, values and links', () => {
  const old = mission(), power = powerFor(old);
  old.version = 4;
  old.elements = old.elements.filter(row => row.owner !== power.key);
  old.statements = old.statements.filter(row => row.context !== power.key);
  old.statements[2].parameters.x = '12';
  old.statements[2].condition = 'x <= 20';
  old.stakeholders.push({ key: 'battery-partner', id: 'BAT', name: 'Battery partner', type: 'Partner' });
  const original = structuredClone(old), upgraded = migrateWorkspace(old, catalog);
  assert.equal(upgraded.version, 8);
  assert.equal(upgraded.elements.filter(row => row.owner === power.key).length, 6);
  assert.deepEqual(upgraded.elements.filter(row => original.elements.some(element => element.key === row.key)), original.elements);
  assert.deepEqual(upgraded.statements, original.statements);
  assert.deepEqual(upgraded.stakeholders, original.stakeholders);
  assert.deepEqual(old, original);
  assert.doesNotThrow(() => validateWorkspace(upgraded, catalog));
  const source = `// <requirements-ui>\n/* requirements-ui:data\n${JSON.stringify(old)}\nrequirements-ui:end-data */\n// </requirements-ui>`;
  assert.deepEqual(readWorkspace(source, catalog), upgraded);
  upgraded.elements = upgraded.elements.filter(row => row.owner !== power.key);
  assert.deepEqual(readWorkspace(renderManaged(upgraded, { catalog }), catalog), upgraded);
  assert.equal(migrateWorkspace(upgraded, catalog), upgraded);
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

test('mission SysML contains typed nested parts, native assignments and all requirements', () => {
  const workspace = mission();
  const source = renderManaged(workspace, { catalog });
  assert.match(source, /private import SpaceSegment::\*/);
  assert.match(source, /private import GroundSegment::\*/);
  assert.match(source, /: Orbit \{/);
  assert.match(source, /: SpaceSegment::CubeSat \{/);
  assert.match(source, /: SpaceSegment::CubeSat::PowerSubsystem \{/);
  assert.match(source, /: GroundSegment::NetworkSubsystem \{/);
  assert.match(source, /ref part affectedElements\[0\.\.\*\] = \(element_domain_horbit, element_domain_hbus\)/);
  assert.match(source, /element_domain_hbus\.element_domain_hbus_hPowerSubsystem/);
  assert.match(source, /attribute tableName : String = "Mission"/);
  assert.match(source, /attribute tableName : String = "CubeSat Bus"/);
  assert.match(source, /attribute tableName : String = "EPS"/);
  assert.match(source, /: SpaceSegment::CubeSat::PowerSubsystem::Batteries \{/);
  assert.match(source, /ref part affectedElements\[0\.\.\*\] = \(element_domain_hbus\.element_domain_hbus_hPowerSubsystem\.element_domain_hbus_hPowerSubsystem_hBatteries\)/);
  assert.match(source, /dependency from statement_eps001 to statement_bus001/);
  assert.deepEqual(readWorkspace(source, catalog), workspace);
});

test('nested SysML source paths include all ancestors regardless of row order', () => {
  const workspace = mission();
  workspace.statements[5].sources.push(workspace.statements[5].affected[0]);
  workspace.elements.reverse();
  const source = renderManaged(workspace, { catalog });
  assert.match(source, /dependency from statement_eps001 to element_domain_hbus::element_domain_hbus_hPowerSubsystem::element_domain_hbus_hPowerSubsystem_hBatteries;/);
  assert.deepEqual(readWorkspace(source, catalog), workspace);
});
