import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { loadCatalog } from '../catalog.mjs';
import { loadProducts } from '../cots.mjs';
import { componentCheck, componentRequirements, emptyWorkspace, nextId, validateWorkspace, WORKSPACE_VERSION } from '../model.mjs';
import { evaluateChecks } from './helpers.mjs';
import { readWorkspace, serializeWorkspace as renderManaged } from './helpers.mjs';
import { renderSchematic } from '../kicad.mjs';
import { renderFprimeArchive, renderFprimeFiles } from '../fprime.mjs';

// Keep these component fixtures independent of the sizing templates.
const catalog = (await loadCatalog()).map(({ requirements, ...type }) => type), products = await loadProducts();
function fixture() {
  const workspace = emptyWorkspace(catalog);
  const power = workspace.elements.find(row => row.definition.endsWith('::PowerSubsystem'));
  const requirement = (id, context, condition) => ({ key: id.toLowerCase(), id, context, kind: 'Requirement', text: '',
    sources: [], affected: [], condition, parameters: { x: '12', y: null, z: null, a: null } });
  workspace.statements = [requirement('EPS001', power.key, 'x >= 10'), requirement('EPS002', power.key, 'True'), requirement('BUS001', power.owner, 'True')];
  workspace.components = [
    { key: 'rtc', id: 'CMP001', owner: power.key, product: 'abracon_ab1805_t3', requirements: ['eps001', 'eps002'] },
    { key: 'battery', id: 'CMP002', owner: power.key, product: 'molicel_inr_18650_p28a', requirements: [] },
  ];
  return { workspace, context: power.key, options: { catalog, products } };
}
const checks = workspace => new Map(evaluateChecks(workspace).map(row => [row.key, row]));

test('COTS dropdown catalog comes from product records and uses only catalog self pins', () => {
  assert.equal(products.length, 99);
  assert.equal(new Set(products.map(product => product.id)).size, products.length);
  const rtc = products.find(product => product.id === 'abracon_ab1805_t3');
  assert.equal(rtc.name, 'AB1805-T3 · Abracon');
  assert.ok(rtc.pins.some(pin => pin.number === '13' && pin.name === 'VCC'));
  assert.equal(products.find(product => product.id === 'isispace_iceps2_type_a').pins.length, 0);
});

test('COTS data is required by the current schema', () => {
  const { workspace } = fixture(); delete workspace.components;
  assert.throws(() => validateWorkspace(workspace, catalog, products), /Invalid workspace/);
});

test('COTS rows validate and share the global ID and key namespaces', () => {
  const { workspace } = fixture();
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog, products));
  assert.equal(nextId(workspace, 'Component'), 'CMP003');
  workspace.components[0].id = 'EPS001';
  assert.throws(() => validateWorkspace(workspace, catalog, products), /already in use/);
  workspace.components[0].id = 'CMP001'; workspace.components[0].key = 'eps001';
  assert.throws(() => validateWorkspace(workspace, catalog, products), /keys must be unique/);
});

test('COTS rows require an EPS owner, known product and read-only verification', () => {
  for (const [field, value, message] of [['owner', 'domain-bus', /EPS tab/], ['product', 'missing', /COTS catalog/],
    ['id', 'bad', /Component IDs/], ['verified', true, /computed/]]) {
    const { workspace } = fixture(); workspace.components[0][field] = value;
    assert.throws(() => validateWorkspace(workspace, catalog, products), message);
  }
  const { workspace } = fixture(); workspace.version = 5;
  assert.throws(() => validateWorkspace(workspace, catalog, products), /Restart the requirements UI server/);
});

test('affected requirements must be unique requirements in the same EPS', () => {
  const { workspace } = fixture(), row = workspace.components[0];
  assert.deepEqual(componentRequirements(workspace, row).map(row => row.id), ['EPS001', 'EPS002']);
  for (const requirements of [['missing'], ['bus001'], ['eps001', 'eps001'], ['rtc']]) {
    row.requirements = requirements;
    assert.throws(() => validateWorkspace(workspace, catalog, products), /choose requirements/);
  }
  row.requirements = ['eps001']; workspace.statements[0].kind = 'Need';
  assert.throws(() => validateWorkspace(workspace, catalog, products), /choose requirements/);
});

test('component verification requires at least one link and every requirement to pass', () => {
  const { workspace } = fixture(), row = workspace.components[0];
  assert.equal(componentCheck(row, checks(workspace)).state, 'pass');
  assert.equal(componentCheck(workspace.components[1], checks(workspace)).state, 'unset');
  workspace.statements[0].parameters.x = '2';
  assert.equal(componentCheck(row, checks(workspace)).state, 'fail');
  workspace.statements[0].parameters.x = null;
  assert.equal(componentCheck(row, checks(workspace)).state, 'pending');
  workspace.statements[0].condition = 'bad()';
  assert.equal(componentCheck(row, checks(workspace)).state, 'error');
  workspace.statements[0].condition = '';
  assert.equal(componentCheck(row, checks(workspace)).state, 'unset');
  assert.equal(componentCheck(row, new Map()).state, 'pending');
});

test('COTS selections, stable requirement links and source links round trip as data', () => {
  const { workspace } = fixture();
  workspace.statements[2].sources = ['rtc'];
  const source = renderManaged(workspace, { catalog, products });
  assert.equal(workspace.components[0].product, 'abracon_ab1805_t3');
  assert.equal(workspace.components[0].key, 'rtc');
  assert.deepEqual(workspace.statements[2].sources, ['rtc']);
  assert.deepEqual(workspace.components[0].requirements, ['eps001', 'eps002']);
  assert.deepEqual(readWorkspace(source, catalog, products), workspace);
  workspace.statements[0].id = 'PWR001';
  assert.deepEqual(workspace.components[0].requirements, ['eps001', 'eps002']);
  assert.doesNotThrow(() => validateWorkspace(workspace, catalog, products));
});

test('KiCad embeds symbols, preserves repeated physical instances and does not invent wiring or footprints', () => {
  const { workspace, context, options } = fixture();
  workspace.components.push({ ...workspace.components[0], key: 'second-rtc', id: 'CMP003' });
  assert.doesNotMatch(renderSchematic(workspace, context, options), /\(property "Verified" "true"/);
  options.checks = evaluateChecks(workspace);
  const source = renderSchematic(workspace, context, options);
  assert.equal((source.match(/\(lib_id /g) ?? []).length, 3);
  assert.equal((source.match(/\(symbol "RequirementsUI:abracon_ab1805_t3"/g) ?? []).length, 1);
  for (const id of ['CMP001', 'CMP002', 'CMP003']) assert.ok(source.includes(`(property "Reference" "${id}"`));
  assert.match(source, /Architecture black box without pin mapping/);
  assert.match(source, /\(property "Verified" "true"/);
  assert.match(source, /\(exclude_from_sim yes\)/);
  assert.match(source, /\(on_board no\)/);
  assert.doesNotMatch(source, /\(wire |\(junction |\(property "Footprint" "[^"\s]+"/);
  assert.equal(source, renderSchematic(workspace, context, options));
});

test('F-Prime exports a complete FPP, C++ and CMake wrapper for every selected instance', () => {
  const { workspace, context, options } = fixture();
  workspace.components.push({ ...workspace.components[0], key: 'second-rtc', id: 'CMP003' });
  const files = renderFprimeFiles(workspace, context, options), manifest = JSON.parse(files.get('components.json'));
  assert.equal(manifest.components.length, 3);
  assert.equal(files.size, 15);
  assert.equal(new Set(manifest.components.map(row => row.component)).size, 3);
  for (const row of manifest.components) {
    assert.match(row.component, /^[A-Za-z][A-Za-z0-9_]*$/);
    const fpp = files.get(`${row.path}/${row.component}.fpp`);
    assert.ok(fpp.includes(`active component ${row.component}`));
    assert.match(fpp, /command recv port cmdIn/);
    assert.match(fpp, /async command NO_OP\(\)/);
    assert.ok(files.get(`${row.path}/${row.component}.hpp`).includes(`${row.component}ComponentAc.hpp`));
    assert.match(files.get(`${row.path}/${row.component}.cpp`), /cmdResponse_out\(opCode, cmdSeq, Fw::CmdResponse::OK\)/);
    assert.match(files.get(`${row.path}/CMakeLists.txt`), /register_fprime_module\(\)/);
    assert.ok(files.get('EpsComponents/CMakeLists.txt').includes(row.component));
  }
  assert.match(files.get('README.md'), /fprime-util impl/);
  assert.match(files.get('README.md'), /performs no hardware access/);
  const zip = renderFprimeArchive(workspace, context, options);
  assert.equal(zip.readUInt32LE(0), 0x04034b50);
  assert.equal(zip.readUInt32LE(zip.length - 22), 0x06054b50);
  assert.equal(zip.readUInt16LE(zip.length - 12), files.size);
});

test('exports reject other tabs, empty tables and unknown products', () => {
  for (const render of [renderSchematic, renderFprimeFiles]) {
    const { workspace, context, options } = fixture();
    assert.throws(() => render(workspace, 'domain-bus', options), /Choose an EPS tab/);
    workspace.components = [];
    assert.throws(() => render(workspace, context, options), /at least one COTS/);
    workspace.components = [{ key: 'unknown', id: 'CMP001', owner: context, product: 'bad', requirements: [] }];
    assert.throws(() => render(workspace, context, options), /COTS catalog/);
  }
});

test('KiCad CLI opens and renders symbols for every catalog product when installed', async t => {
  const cli = [process.env.KICAD_CLI, 'kicad-cli', '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli']
    .filter(Boolean).find(path => spawnSync(path, ['version'], { encoding: 'utf8' }).status === 0);
  if (!cli) return t.skip('KiCad CLI is optional.');
  const { workspace, context, options } = fixture();
  workspace.components = products.map((product, index) => ({ key: `part-${index}`, id: `CMP${String(index + 1).padStart(3, '0')}`,
    owner: context, product: product.id, requirements: [] }));
  const dir = await mkdtemp(join(tmpdir(), 'requirements-kicad-'));
  t.after(() => rm(dir, { recursive: true, force: true }));
  const path = join(dir, 'eps.kicad_sch'), output = join(dir, 'svg');
  await writeFile(path, renderSchematic(workspace, context, options));
  const result = spawnSync(cli, ['sch', 'export', 'svg', '-o', output, path], { encoding: 'utf8', timeout: 30000 });
  assert.equal(result.status, 0, result.stderr);
  const svg = await readFile(join(output, (await readdir(output)).find(name => name.endsWith('.svg'))), 'utf8');
  for (const row of workspace.components) assert.ok(svg.includes(row.id), `Missing rendered symbol ${row.id}`);
});
