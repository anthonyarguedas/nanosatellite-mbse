import { createHash } from 'node:crypto';
import { componentCheck, tabsFor, validateWorkspace } from './model.mjs';
import { evaluateChecks } from './verification.mjs';

const quote = value => JSON.stringify(String(value));
const number = value => Number(value.toFixed(4));
const uuid = value => {
  const hex = createHash('sha256').update(value).digest('hex');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-5${hex.slice(13, 16)}-a${hex.slice(17, 20)}-${hex.slice(20, 32)}`;
};
const effects = '(effects (font (size 1.27 1.27)))';
const property = (name, value, x, y, hidden = false) =>
  `(property ${quote(name)} ${quote(value)} (at ${number(x)} ${number(y)} 0) (effects (font (size 1.27 1.27))${hidden ? ' (hide yes)' : ''}))`;
const pinType = pin => pin.kind === 'no_connect' ? 'no_connect'
  : ['power_input', 'ground'].includes(pin.kind) ? 'power_in'
    : pin.kind === 'power_output' ? 'power_out'
      : pin.direction === 'inout' ? 'bidirectional' : pin.direction === 'in' ? 'input' : pin.direction === 'out' ? 'output' : 'passive';

function symbolFor(product) {
  const pins = [...new Map((product.pins ?? []).map(pin => [pin.number, pin])).values()]
    .sort((a, b) => a.number.localeCompare(b.number, undefined, { numeric: true }));
  const rows = Math.ceil(pins.length / 2);
  const halfHeight = Math.max(5.08, (rows + 1) * 1.27);
  const halfWidth = Math.max(15.24, Math.max(0, ...pins.map(pin => pin.name.length)) * 0.7 + 4);
  const libId = `RequirementsUI:${product.id}`;
  const lines = [`(symbol ${quote(libId)} (pin_names (offset 1.016)) (exclude_from_sim yes) (in_bom yes) (on_board no)`,
    property('Reference', 'CMP', 0, halfHeight + 2.54), property('Value', product.partNumber, 0, -halfHeight - 2.54),
    property('Footprint', '', 0, 0, true), property('Datasheet', product.datasheetUrl, 0, 0, true),
    `(symbol ${quote(`${product.id}_0_1`)} (rectangle (start ${-halfWidth} ${halfHeight}) (end ${halfWidth} ${-halfHeight}) (stroke (width 0.254) (type default)) (fill (type background))))`,
    `(symbol ${quote(`${product.id}_1_1`)}`];
  pins.forEach((pin, index) => {
    const right = index >= rows, row = right ? index - rows : index;
    const y = number((rows - 1) * 1.27 - row * 2.54);
    lines.push(`(pin ${pinType(pin)} line (at ${number((halfWidth + 5.08) * (right ? 1 : -1))} ${y} ${right ? 180 : 0}) (length 5.08) (name ${quote(pin.name)} ${effects}) (number ${quote(pin.number)} ${effects}))`);
  });
  lines.push('))');
  return { libId, pins, halfHeight, halfWidth, source: lines.join('\n') };
}

// Self-contained architecture symbols. Catalog pins remain unwired. Missing
// pin data produces a black box, with no invented pins or PCB footprint.
export function renderSchematic(workspace, context, { catalog, products, projectName = 'eps' }) {
  validateWorkspace(workspace, catalog, products);
  const owner = workspace.elements.find(row => row.key === context);
  if (!owner || catalog.find(type => type.model === owner.definition)?.role !== 'eps') throw new Error('Choose an EPS tab to export.');
  const components = workspace.components.filter(row => row.owner === context);
  if (!components.length) throw new Error('Add at least one COTS component before exporting.');
  const byId = new Map(products.map(product => [product.id, product]));
  const symbols = new Map(components.map(row => [row.product, symbolFor(byId.get(row.product))]));
  const root = uuid(`requirements-ui:${context}`);
  const checks = new Map(evaluateChecks(workspace).map(check => [check.key, check]));
  const statements = new Map(workspace.statements.map(row => [row.key, row.id]));
  const label = tabsFor(workspace, catalog).find(tab => tab.key === context).label;
  const cellWidth = Math.max(95, ...[...symbols.values()].map(symbol => symbol.halfWidth * 2 + 25));
  const placements = [];
  let top = 35;
  for (let index = 0; index < components.length; index += 4) {
    const batch = components.slice(index, index + 4);
    const height = Math.max(...batch.map(row => symbols.get(row.product).halfHeight * 2 + 25));
    batch.forEach((row, column) => placements.push({ row, x: 15 + cellWidth * (column + 0.5), y: top + height / 2 }));
    top += height;
  }
  const lines = ['(kicad_sch (version 20260306) (generator "requirements_ui") (generator_version "1.0")',
    `(uuid ${quote(root)}) (paper "User" ${number(cellWidth * 4 + 30)} ${number(Math.max(297, top + 25))})`,
    `(title_block (title ${quote(`${label} COTS components`)}) (comment 1 "Architecture review only. Unconnected symbols, no PCB footprints or simulation."))`,
    '(lib_symbols', ...[...symbols.values()].map(symbol => symbol.source), ')',
    `(text "Unconnected architecture symbols. Catalog pin lists may be partial. Review datasheets before wiring." (at 15 15 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid ${quote(uuid(`${context}:notice`))}))`];
  for (const { row, x, y } of placements) {
    const product = byId.get(row.product), symbol = symbols.get(row.product);
    lines.push(`(symbol (lib_id ${quote(symbol.libId)}) (at ${number(x)} ${number(y)} 0) (unit 1) (exclude_from_sim yes) (in_bom yes) (on_board no) (dnp no) (uuid ${quote(uuid(row.key))})`,
      property('Reference', row.id, x, y - symbol.halfHeight - 5.08),
      property('Value', product.partNumber, x, y - symbol.halfHeight - 2.54),
      property('Footprint', '', x, y, true), property('Datasheet', product.datasheetUrl, x, y, true),
      property('Manufacturer', product.manufacturer, x, y, true), property('Catalog product ID', product.id, x, y, true),
      property('Affected requirements', row.requirements.map(key => statements.get(key)).join(', '), x, y, true),
      property('Verified', componentCheck(row, checks).state === 'pass' ? 'true' : 'false', x, y, true),
      property('Representation', symbol.pins.length ? 'Architecture symbol with catalog pin subset' : 'Architecture black box without pin mapping', x, y, true));
    for (const pin of symbol.pins) lines.push(`(pin ${quote(pin.number)} (uuid ${quote(uuid(`${row.key}:pin:${pin.number}`))}))`);
    lines.push(`(instances (project ${quote(projectName)} (path ${quote(`/${root}`)} (reference ${quote(row.id)}) (unit 1)))))`);
  }
  lines.push('(sheet_instances (path "/" (page "1"))) (embedded_fonts no))');
  return lines.join('\n') + '\n';
}
