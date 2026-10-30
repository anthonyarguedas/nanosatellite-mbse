import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { catalogFromSource, indexDefinitions, loadCatalog } from '../catalog.mjs';
import { addElementChildren, allowedDefinitions, assignableElements, availableSources, emptyWorkspace, migrateWorkspace, tabsFor, validateWorkspace } from '../model.mjs';
import { evaluateChecks } from '../verification.mjs';
import { readWorkspace, renderManaged } from '../sysml.mjs';

const catalog = await loadCatalog();
const requirement = (id, context, affected = [], sources = []) => ({
  key: id.toLowerCase(), id, context, affected, sources, kind: 'Requirement', text: '', condition: '',
  parameters: { x: null, y: null, z: null, a: null },
});

function mission() {
  const workspace = emptyWorkspace(catalog);
  workspace.statements = [
    requirement('REQ001', 'external'),
    requirement('MIS001', 'mission', ['domain-orbit', 'domain-bus'], ['req001']),
    requirement('BUS001', 'domain-bus', [workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem')).key], ['mis001']),
    requirement('PAY001', 'domain-payload', [workspace.elements.find(row => row.definition.endsWith('::Instrument')).key], ['mis001']),
    requirement('GND001', 'domain-ground', [workspace.elements.find(row => row.definition.endsWith('::NetworkSubsystem')).key], ['mis001']),
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
});

test('new generic subsystem definitions are discovered without UI changes', async () => {
  const source = await readFile(new URL('../../mission.sysml', import.meta.url), 'utf8');
  const extended = catalogFromSource(source.replace('        part def PowerSubsystem :>', '        part def ExperimentalSubsystem;\n        part def PowerSubsystem :>'));
  const workspace = emptyWorkspace(extended);
  assert.ok(workspace.elements.some(row => row.definition === 'SpaceSegment::CubeSat::ExperimentalSubsystem'));
  assert.doesNotThrow(() => validateWorkspace(workspace, extended));
});

test('default workbook has five tabs, four mission domains and no Orbit tab', () => {
  const workspace = emptyWorkspace(catalog);
  assert.deepEqual(tabsFor(workspace, catalog).map(tab => tab.label), ['External', 'Mission', 'CubeSat Bus', 'Payload', 'Ground Station']);
  assert.deepEqual(workspace.elements.filter(row => row.owner === 'mission').map(row => row.name), ['Orbit', 'CubeSat Bus', 'Payload', 'Ground Station']);
  assert.equal(workspace.elements.length, 22);
  assert.equal(tabsFor(workspace, catalog).some(tab => tab.key === 'domain-orbit'), false);
  assert.equal(new Set(workspace.elements.map(row => row.id)).size, 22);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('requirements can be traced across tabs and assigned to multiple local elements', () => {
  const workspace = mission();
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
  assert.equal(assignableElements(workspace, workspace.statements[1]).length, 4);
  assert.equal(assignableElements(workspace, workspace.statements[2]).length, 8);
  assert.ok(availableSources(workspace, 'bus001').some(row => row.key === 'mis001'));
  assert.equal(availableSources(workspace, 'req001').some(row => row.key === 'bus001'), false);
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

test('another domain instance reuses the same table and subsystem catalog', () => {
  const workspace = mission();
  const duplicate = { key: 'backup-bus', id: 'BAK', name: 'Backup Bus', owner: 'mission', definition: 'SpaceSegment::CubeSat' };
  workspace.elements.push(duplicate); addElementChildren(workspace, duplicate, catalog);
  assert.equal(workspace.elements.filter(row => row.owner === duplicate.key).length, 8);
  assert.equal(tabsFor(workspace, catalog).length, 6);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog));
});

test('version 2 upgrades into External while preserving values and avoiding ID collisions', () => {
  const old = { version: 2, variables: [{ name: 'mass', type: 'float' }],
    stakeholders: [{ key: 'stakeholder', id: 'BUS', name: 'Existing stakeholder', type: 'Partner' }],
    statements: [{ key: 'original', id: 'REQ001', kind: 'Requirement', text: 'Original', sources: ['stakeholder'], verified: true, condition: 'mass > 0', parameters: { mass: 2 } }] };
  const upgraded = migrateWorkspace(old, catalog);
  assert.doesNotThrow(() => validateWorkspace(upgraded, catalog));
  assert.equal(upgraded.statements[0].context, 'external');
  assert.equal(upgraded.statements[0].parameters.mass, 2);
  assert.equal(Object.hasOwn(upgraded.statements[0], 'verified'), false);
  assert.equal(upgraded.statements[0].condition, 'mass > 0');
  assert.deepEqual(upgraded.statements[0].sources, ['stakeholder']);
  assert.deepEqual(upgraded.statements[0].affected, []);
  assert.notEqual(upgraded.elements.find(row => row.key === 'domain-bus').id, 'BUS');
});

test('expressions read variable values across all tab contexts', () => {
  const workspace = mission();
  workspace.statements[1].parameters.x = 25;
  workspace.statements[2].parameters.x = 20;
  workspace.statements[2].condition = 'x <= MIS001.x';
  assert.equal(evaluateChecks(workspace).find(row => row.key === 'bus001').state, 'pass');
  workspace.statements[1].parameters.x = 10;
  assert.equal(evaluateChecks(workspace).find(row => row.key === 'bus001').state, 'fail');
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
  assert.deepEqual(readWorkspace(source, catalog), workspace);
});
