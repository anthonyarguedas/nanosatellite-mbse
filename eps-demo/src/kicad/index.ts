import type { Catalog, NodeId, Product, Role, Workspace } from '../types';

export interface KiCadFile { name: string; content: string }
export interface KiCadExport { files: KiCadFile[]; warnings: string[]; scope: string }
export interface KiCadReadiness {
  ready: boolean;
  blockers: string[];
  warnings: string[];
  physicalRouting: 'blocked';
  physicalGates: string[];
  scope: string;
}

export const KICAD_SCOPE = 'Review-only logical COTS interconnect drawing. Named sheet ports express proposed functional associations, not manufacturer terminals, electrical nets or an approved harness. No PCB, internal COTS circuit reconstruction, electrical compatibility, manufacturing or flight-readiness claim.';
const ROLES: Role[] = ['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software'];
// Transitive prerequisites of candidates in the canonical workflow. Simulation is not needed for a logical drawing.
const REQUIRED: NodeId[] = ['mission', 'orbit', 'scenarios', 'budget', 'solar', 'battery', 'topology', 'candidates'];
export const PHYSICAL_GATES = [
  'Engineer-reviewed exact connector variants and terminal, return, isolation and inhibit pin maps, bound to each product revision.',
  'Engineer-reviewed installed quantities and supported assembly configurations. Cell counts alone do not define series/parallel wiring.',
  'Verified connector footprints, pad-to-terminal mapping, orientation, mounting and keep-out geometry.',
  'Approved pin-level netlist, load-to-channel assignments and auxiliary circuits or harnesses with their ratings.',
  'Board outline, layer stack, installation constraints, net current and voltage limits, copper widths and clearances.',
  'A configured external router, followed by unresolved-net review and applicable electrical and physical rule checks.',
];

/** Inspect revision records and current suggestions. Incomplete evidence permits a review drawing only. */
export function getKiCadReadiness(workspace: Workspace, catalog: Catalog): KiCadReadiness {
  const blockers: string[] = [];
  const warnings = [KICAD_SCOPE, 'Product hardware revisions that are unstated in the catalog remain unknown. Catalog record revisions are preserved verbatim.',
    'Candidate records do not bind a catalog revision. Reevaluate candidates after catalog changes. This export freezes the supplied catalog and selected entries.'];
  if (workspace.schemaVersion !== 1) blockers.push('Unsupported workspace schema.');
  for (const id of REQUIRED) {
    const record = workspace.records?.[id];
    if (!record || !Number.isSafeInteger(record.revision) || record.revision < 0 || record.evaluatedRevision !== record.revision || !record.evaluatedAt) {
      blockers.push(`${id} is uncomputed or stale. Reevaluate COTS suggestions and their prerequisites.`);
    }
  }
  for (const key of ['orbit', 'budget', 'solar', 'battery', 'suggestions'] as const) {
    if (!workspace.analysis?.[key]) blockers.push(`Current ${key} output is missing.`);
  }
  if (!workspace.inputs.scenarios.some(item => item.id === workspace.inputs.activeScenarioId)) blockers.push('The active scenario is missing.');
  if (!catalog.revision.trim()) blockers.push('The catalog revision is missing.');
  const ids = catalog.products.map(item => item.id);
  if (new Set(ids).size !== ids.length) blockers.push('Catalog product identifiers must be unique.');
  const allocated = ROLES.filter(role => workspace.selections[role]);
  if (!allocated.length) blockers.push('Allocate at least one current COTS product before exporting.');
  for (const key of Object.keys(workspace.selections)) {
    if (!ROLES.includes(key as Role)) blockers.push(`Unsupported role allocation: ${key}.`);
  }
  for (const role of allocated) {
    const id = workspace.selections[role]!;
    const product = catalog.products.find(item => item.id === id);
    if (!product || !product.roles.includes(role)) {
      blockers.push(`${role}: selected product is absent or does not provide this role.`);
      continue;
    }
    if (!product.revision.trim()) blockers.push(`${product.name}: exact catalog record revision is missing.`);
    const suggestions = workspace.analysis.suggestions?.filter(item => item.productId === id) ?? [];
    const suggestion = role === 'solar' || role === 'battery' || role === 'conditioning'
      ? suggestions.find(item => item.role === role)
      : suggestions.find(item => product.roles.includes(item.role));
    if (!suggestion || suggestion.outcome === 'rejected' || suggestion.checks.some(item => item.verdict === 'fail')) {
      blockers.push(`${product.name}: no applicable non-rejected current suggestion for ${role}.`);
    } else {
      if (!Number.isSafeInteger(suggestion.quantity) || suggestion.quantity < 1) blockers.push(`${product.name}: suggested quantity must be a positive integer.`);
      if (suggestion.outcome === 'incomplete') warnings.push(`${product.name}: preliminary match is incomplete. ${suggestion.missing.join(' ')}`);
    }
    if (new Set(suggestions.map(item => item.quantity)).size > 1) blockers.push(`${product.name}: inconsistent suggested quantities require review.`);
    if (!product.sources.length) warnings.push(`${product.name}: no source URL supplied.`);
    const overlapping = product.roles.filter(provided => workspace.selections[provided] && workspace.selections[provided] !== id);
    if (overlapping.length) warnings.push(`${product.name}: also provides ${overlapping.join(', ')} allocated to other products. Review assembly accounting and installed configuration. Only explicit role allocations are drawn.`);
  }
  const missingRoles = ROLES.filter(role => !workspace.selections[role]);
  if (missingRoles.length) warnings.push(`Unallocated roles: ${missingRoles.join(', ')}. No COTS hardware is invented for these roles.`);
  return { ready: blockers.length === 0, blockers: [...new Set(blockers)], warnings: [...new Set(warnings)], physicalRouting: 'blocked', physicalGates: [...PHYSICAL_GATES], scope: KICAD_SCOPE };
}

interface Point { x: number; y: number }
interface Port extends Point { name: string; side: 'left' | 'right' }
interface DrawingNode extends Point {
  id: string;
  file: string;
  label: string;
  roles: Role[];
  product?: Product;
  quantity?: number;
  ports: Port[];
}
interface Association { id: string; name: string; from: string; to: string; internal: boolean; points?: Point[] }
const WIDTH = 90;
const HEIGHT = 47.5;
const STEP = 2.5;
const SLOTS: Record<Role, number> = { solar: 0, battery: 3, conditioning: 1, distribution: 2, processor: 4, software: 5 };
const SLOT_X = [25, 165, 305];
const SLOT_Y = [55, 135, 215];

// A deterministic geometry router for abstract schematic wires only. It has no PCB rules or copper model.
function route(start: Point, end: Point, nodes: DrawingNode[], occupied: Set<string>): Point[] | undefined {
  const key = (p: Point) => `${p.x},${p.y}`;
  const allowed = (p: Point) => p.x >= 15 && p.x <= 405 && p.y >= 45 && p.y <= 267.5
    && !occupied.has(key(p)) && !nodes.some(n => p.x >= n.x && p.x <= n.x + WIDTH && p.y >= n.y && p.y <= n.y + HEIGHT);
  const queue: Point[] = [start];
  const parent = new Map<string, Point | null>([[key(start), null]]);
  let cursor = 0;
  while (cursor < queue.length) {
    const current = queue[cursor++];
    if (key(current) === key(end)) {
      const path: Point[] = [];
      let p: Point | null = current;
      while (p) { path.push(p); p = parent.get(key(p)) ?? null; }
      return path.reverse();
    }
    const next = [
      { x: current.x + STEP, y: current.y }, { x: current.x - STEP, y: current.y },
      { x: current.x, y: current.y + STEP }, { x: current.x, y: current.y - STEP },
    ].sort((a, b) => Math.abs(a.x - end.x) + Math.abs(a.y - end.y) - Math.abs(b.x - end.x) - Math.abs(b.y - end.y));
    for (const p of next) {
      if (!parent.has(key(p)) && allowed(p)) { parent.set(key(p), current); queue.push(p); }
    }
  }
  return undefined;
}

function makeDrawing(workspace: Workspace, catalog: Catalog) {
  const nodes: DrawingNode[] = [];
  for (const role of ROLES) {
    const id = workspace.selections[role];
    if (!id || nodes.some(n => n.id === id)) continue;
    const product = catalog.products.find(item => item.id === id)!;
    const roles = ROLES.filter(item => workspace.selections[item] === id);
    const slot = Math.min(...roles.map(item => SLOTS[item]));
    const quantity = workspace.analysis.suggestions!.find(item => item.productId === id)!.quantity;
    nodes.push({ id, file: `usage-${nodes.length + 1}.kicad_sch`, label: `Usage ${nodes.length + 1}`, roles, product, quantity,
      x: SLOT_X[slot % 3], y: SLOT_Y[Math.floor(slot / 3)], ports: [] });
  }
  const scenario = workspace.inputs.scenarios.find(item => item.id === workspace.inputs.activeScenarioId)!;
  if (workspace.selections.distribution && scenario.loads.length) {
    // Prefer the middle right slot. Keep the lower right title block clear when that slot is occupied.
    const slot = nodes.some(n => n.x === SLOT_X[2] && n.y === SLOT_Y[1]) ? 7 : 5;
    nodes.push({ id: '@scenario-demand', file: 'scenario-demand.kicad_sch', label: 'Scenario demand (logical)', roles: [], x: SLOT_X[slot % 3], y: SLOT_Y[Math.floor(slot / 3)], ports: [] });
  }
  const associations: Association[] = [];
  const templates: [string, string, Role, Role | '@scenario-demand'][] = [
    ['solar-intent', 'L_SOLAR_POWER', 'solar', 'conditioning'],
    ['battery-intent', 'L_STORAGE_PATH', 'battery', 'conditioning'],
    ['bus-intent', 'L_POWER_TRANSFER', 'conditioning', 'distribution'],
    ['load-intent', 'L_LOAD_SERVICE', 'distribution', '@scenario-demand'],
    ['control-intent', 'L_CONTROL_SERVICE', 'processor', 'distribution'],
    ['host-intent', 'L_HOST_ALLOCATION', 'software', 'processor'],
  ];
  for (const [id, name, a, b] of templates) {
    const from = workspace.selections[a];
    const to = b === '@scenario-demand' ? nodes.find(n => n.id === b)?.id : workspace.selections[b];
    if (!from || !to) continue;
    associations.push({ id, name, from, to, internal: from === to });
  }
  for (const edge of associations.filter(item => !item.internal)) {
    const a = nodes.find(n => n.id === edge.from)!;
    const b = nodes.find(n => n.id === edge.to)!;
    // Distinct endpoint slots prevent accidental branches or junctions.
    const sideA = a.x <= b.x ? 'right' : 'left';
    const sideB = a.x < b.x ? 'left' : 'right';
    for (const [node, side] of [[a, sideA], [b, sideB]] as const) {
      const index = node.ports.filter(p => p.side === side).length;
      node.ports.push({ name: edge.name, side, x: node.x + (side === 'right' ? WIDTH : 0), y: node.y + 5 + index * 5 });
    }
  }
  const occupied = new Set<string>();
  // Reserve all pin escape cells before routing to avoid trapping a later port.
  const reserved = new Set(nodes.flatMap(n => n.ports.map(p => `${p.x + (p.side === 'right' ? STEP : -STEP)},${p.y}`)));
  for (const edge of associations.filter(item => !item.internal)) {
    const a = nodes.find(n => n.id === edge.from)!.ports.find(p => p.name === edge.name)!;
    const b = nodes.find(n => n.id === edge.to)!.ports.find(p => p.name === edge.name)!;
    const start = { x: a.x + (a.side === 'right' ? STEP : -STEP), y: a.y };
    const end = { x: b.x + (b.side === 'right' ? STEP : -STEP), y: b.y };
    const blocked = new Set([...occupied, ...reserved]);
    blocked.delete(`${start.x},${start.y}`); blocked.delete(`${end.x},${end.y}`);
    const path = route(start, end, nodes, blocked);
    if (path) {
      const full = [a, ...path, b];
      for (const p of full) occupied.add(`${p.x},${p.y}`);
      edge.points = full.filter((p, i) => i === 0 || i === full.length - 1 ||
        !((full[i - 1].x === p.x && full[i + 1].x === p.x) || (full[i - 1].y === p.y && full[i + 1].y === p.y)));
    }
  }
  return { nodes, associations, scenario };
}

// Geometry is planned in 2.5-unit cells and emitted on KiCad's 2.54 mm connection grid.
const mm = (value: number) => Number((value * 1.016).toFixed(6));
const quoted = (s: string) => JSON.stringify(s.replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, ''));
function hash(s: string, salt = 0): string {
  let value = (2166136261 ^ salt) >>> 0;
  for (let i = 0; i < s.length; i++) value = Math.imul(value ^ s.charCodeAt(i), 16777619) >>> 0;
  return value.toString(16).padStart(8, '0');
}
function identifier(s: string): string {
  const hex = [0, 1, 2, 3].map(salt => hash(s, salt)).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-4${hex.slice(13, 16)}-8${hex.slice(17, 20)}-${hex.slice(20)}`;
}
function wrap(s: string, width = 56): string[] {
  const lines: string[] = [];
  for (const paragraph of s.split(/\r?\n/)) {
    let line = '';
    for (const word of paragraph.split(/\s+/)) {
      if (line && line.length + word.length + 1 > width) { lines.push(line); line = ''; }
      // Split long URLs so they stay inside the page. Full URLs remain in the manifest.
      for (let i = 0; i < word.length; i += width) {
        const chunk = word.slice(i, i + width);
        if (i) { if (line) lines.push(line); line = chunk; }
        else line += (line ? ' ' : '') + chunk;
      }
    }
    lines.push(line);
  }
  return lines;
}

/** Traceability identifier, not a cryptographic signature or approval. Changes include quantities and selected evidence. */
export function getKiCadArchitectureFingerprint(workspace: Workspace, catalog: Catalog): string {
  const selected = [...new Set(ROLES.flatMap(role => workspace.selections[role] ? [workspace.selections[role]!] : []))];
  return `orbitwork-${identifier(JSON.stringify({ workspace, catalogRevision: catalog.revision, selectedCatalogEntries: selected.map(id => catalog.products.find(p => p.id === id)) }))}`;
}

/** Pure browser-compatible export. Throws with actionable blockers instead of exporting stale selections. */
export function buildKiCadExport(workspace: Workspace, catalog: Catalog): KiCadExport {
  const readiness = getKiCadReadiness(workspace, catalog);
  if (!readiness.ready) throw new Error(`KiCad review export blocked: ${readiness.blockers.join(' ')}`);
  const { nodes, associations, scenario } = makeDrawing(workspace, catalog);
  const warnings = [...readiness.warnings];
  const unrouted = associations.filter(item => !item.internal && !item.points);
  for (const edge of unrouted) warnings.push(`Logical association ${edge.name} could not be drawn without a crossing. Its sheet ports remain unresolved.`);
  const snapshot = { schemaVersion: 1, catalogRevision: catalog.revision, workspace, selectedCatalogEntries: nodes.flatMap(n => n.product ? [n.product] : []) };
  const seed = JSON.stringify(snapshot);
  const uuid = (s: string) => identifier(`${hash(seed)}:${s}`);
  const rootId = uuid('root');
  const project = 'orbitwork-review';
  let serial = 0;
  const text = (value: string, x: number, y: number, size = 1.27, center = false) =>
    `(text ${quoted(value)} (at ${mm(x)} ${mm(y)} 0) (effects (font (size ${size} ${size}))${center ? '' : ' (justify left)'}) (uuid ${uuid(`text-${serial++}`)}))`;
  const header = (id: string, title: string, paper = 'A4') => `(kicad_sch (version 20250114) (generator "orbitwork_eps_review")\n(uuid ${id}) (paper "${paper}")\n(title_block (title ${quoted(title)}) (rev "logical-1") (comment 1 "REVIEW ONLY - logical ports, no manufacturer pin mapping") (comment 2 "No PCB or electrical verification"))\n(lib_symbols)\n`;
  const root: string[] = [header(rootId, 'COTS architecture / logical interconnect review', 'A3')];
  root.push(text('ORBITWORK / COTS ARCHITECTURE REVIEW', 25, 18, 2));
  root.push(text(wrap(workspace.inputs.mission.name, 110).slice(0, 2).join('\n'), 25, 25, 1.5));
  root.push(text('REVIEW ONLY. Automatically placed sheets and routed LOGICAL associations. No terminal numbers, returns or electrical compatibility are inferred.', 25, 34, 1.1));
  root.push(text(`Topology intent: ${workspace.inputs.topology.conditioning}, ${workspace.inputs.topology.distribution}, ${workspace.inputs.topology.bus} bus. Scenario: ${scenario.name}`, 25, 39, 1.1));
  const files: KiCadFile[] = [];
  nodes.forEach((node, index) => {
    const sheetId = uuid(`sheet-${node.id}`);
    const pins = node.ports.map(p => `(pin ${quoted(p.name)} passive (at ${mm(p.x)} ${mm(p.y)} ${p.side === 'left' ? 180 : 0}) (effects (font (size 1.1 1.1)) (justify ${p.side === 'left' ? 'left' : 'right'})) (uuid ${uuid(`port-${node.id}-${p.name}`)}))`).join('\n');
    root.push(`(sheet (at ${mm(node.x)} ${mm(node.y)}) (size ${mm(WIDTH)} ${mm(HEIGHT)}) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid ${sheetId})\n(property "Sheetname" ${quoted(node.label)} (at ${mm(node.x)} ${mm(node.y - 2)} 0) (effects (font (size 1.27 1.27)) (justify left)))\n(property "Sheetfile" ${quoted(node.file)} (at ${mm(node.x)} ${mm(node.y + HEIGHT + 2)} 0) (effects (font (size 1 1)) (justify left)))\n${pins}\n(instances (project "${project}" (path "/${rootId}" (page "${index + 2}")))))`);
    const name = node.product ? `${node.product.manufacturer} / ${node.product.name}` : 'Scenario load group / no COTS load products';
    root.push(text(wrap(name, 48).slice(0, 3).join('\n'), node.x + WIDTH / 2, node.y + 26, 1.8, true));
    root.push(text(node.product ? `Allocated: ${node.roles.join(', ')}` : `${scenario.loads.length} authored loads, channel mapping absent`, node.x + WIDTH / 2, node.y + 38, 1.4, true));
    root.push(text(node.product ? `Quantity ${node.quantity} / configuration unassessed` : 'Aggregate service intent only', node.x + WIDTH / 2, node.y + 42, 1.27, true));
    const child: string[] = [header(uuid(`child-${node.id}`), `${node.label} / review data`)];
    const details = node.product ? [
      'REVIEW ONLY / OPAQUE COTS USAGE', name,
      `Product ID: ${node.product.id}`, `Part number: ${node.product.partNumber}`, `Revision: ${node.product.revision}`,
      `Allocated roles: ${node.roles.join(', ')}. One physical usage record. Quantity: ${node.quantity}.`,
      `Accounting boundary: ${node.product.accountingBoundary}`,
      'Supported catalog configurations (none is automatically chosen):', ...node.product.supportedConfigurations,
      'Sources (exact URLs and document revisions also in manifest.json):',
      ...node.product.sources.flatMap(s => [`${s.title} / ${s.revision}`, s.url, `Location: ${s.location}. Retrieved: ${s.retrievedAt}`]),
      'Catalog caveats:', ...node.product.caveats,
    ] : ['REVIEW ONLY / AUTHORED SCENARIO DEMAND', scenario.name, `Scenario revision: ${scenario.revision}`, scenario.provenance,
      ...scenario.loads.map(load => `${load.name}: ${load.idlePowerW} W idle / ${load.activePowerW} W active / ${load.railV} V requested. No connector or channel assignment.`)];
    const lines = details.flatMap(item => wrap(item, 100));
    // An A3 child page and a bounded summary keep source text readable. Full, untruncated records are in the manifest.
    const childText = lines.length > 66 ? [...lines.slice(0, 64), '(Further details are retained in manifest.json.)'] : lines;
    child[0] = header(uuid(`child-${node.id}`), `${node.label} / review data`, 'A3');
    child.push(text(childText.join('\n'), 25, 20 + (childText.length - 1) * 1.25, 1.5));
    child.push(text('NAMED LOGICAL PORTS ONLY. No physical pin, footprint, return or internal circuit is defined.', 25, 210, 1.2));
    node.ports.forEach((p, portIndex) => {
      const y = 225 + portIndex * 5;
      child.push(`(hierarchical_label ${quoted(p.name)} (shape passive) (at ${mm(60)} ${mm(y)} 0) (effects (font (size 1.1 1.1)) (justify left)) (uuid ${uuid(`hier-${node.id}-${p.name}`)}))`);
    });
    child.push(')');
    files.push({ name: node.file, content: child.join('\n') });
  });
  for (const edge of associations) {
    if (!edge.points) continue;
    for (let i = 1; i < edge.points.length; i++) {
      const a = edge.points[i - 1], b = edge.points[i];
      root.push(`(wire (pts (xy ${mm(a.x)} ${mm(a.y)}) (xy ${mm(b.x)} ${mm(b.y)})) (stroke (width 0) (type default)) (uuid ${uuid(`wire-${edge.id}-${i}`)}))`);
    }
  }
  root.push(text('Each Usage sheet is one catalog allocation with its quantity. Integrated roles share that usage. Lines denote intent, including software host allocation.', 25, 274, 1));
  root.push(text(`Physical routing BLOCKED. Missing pin/return maps, reviewed assembly configuration, footprints, netlist and board constraints. Logical routes unresolved: ${unrouted.length}.`, 25, 279, 1));
  root.push('(sheet_instances (path "/" (page "1")))\n)');
  const manifest = {
    schemaVersion: 1, generator: 'Orbitwork logical KiCad export 1', scope: KICAD_SCOPE, catalogRevision: catalog.revision,
    architectureFingerprint: getKiCadArchitectureFingerprint(workspace, catalog),
    freshness: { requiredCurrentNodes: REQUIRED, records: workspace.records, catalogRevisionBinding: 'Workspace records contain no catalog revision. Export freezes the supplied entries. Reevaluate candidates after catalog changes.' },
    drawing: { root: `${project}.kicad_sch`, representation: 'Hierarchical sheets with abstract named passive ports. No component symbols, pin numbers or footprints.',
      associationOrigin: 'Proposed role-to-role templates, not sourced manufacturer connectivity. All links require engineering review.',
      placement: 'Deterministic role grid. Integrated usages share one sheet.', routing: 'Orthogonal grid search avoiding sheet bodies and existing logical wires. No PCB routing.',
      coordinateUnits: 'mm', associations: associations.map(edge => ({ ...edge, points: edge.points?.map(p => ({ x: mm(p.x), y: mm(p.y) })) })), unresolvedLogicalAssociations: unrouted.map(item => item.id) },
    usages: nodes.filter(n => n.product).map(n => ({ usageId: n.label, productId: n.id, catalogEntryRevision: n.product!.revision, allocatedRoles: n.roles,
      quantity: n.quantity, installedConfiguration: null, sourceSheet: n.file, product: n.product })),
    unallocatedRoles: ROLES.filter(role => !workspace.selections[role]),
    scenario: { id: scenario.id, revision: scenario.revision, provenance: scenario.provenance, loads: scenario.loads, loadChannelAssignments: null },
    physicalRouting: { status: 'blocked', boardGenerated: false, prerequisites: PHYSICAL_GATES.map(description => ({ description, status: 'missing-in-typed-architecture' })),
      unresolvedPhysicalNets: 'Unknown. No physical netlist or terminal mapping exists. Logical associations are not physical nets.' },
    validation: { syntax: 'Run local kicad-validate.mjs on this export to parse and render it.', erc: 'Not run by browser export. ERC on abstract sheets cannot assess product electrical compatibility.', drc: 'Not applicable to this drawing. No PCB exists.' },
    warnings,
  };
  const readme = `# Orbitwork KiCad architecture review\n\n${KICAD_SCOPE}\n\nOpen ${project}.kicad_sch in KiCad. All child sheets must remain in the same directory. The project contains only hierarchical sheets, named logical ports and automatically drawn intent links. It deliberately contains no manufacturer symbol pins, footprints or PCB. An electrical netlist exported by KiCad will contain no physical components.\n\nProduct identities, exact catalog revisions, source URLs, quantities, accounting boundaries, role allocations, scenario data and missing physical-data gates are in manifest.json. Quantity does not specify an installed arrangement. One integrated board is represented by one usage sheet even when it supplies several roles. Internal role associations are recorded in the manifest and are not drawn as fake external wires.\n\nThe links are proposed functional associations derived from the role allocations. They are neither manufacturer wiring nor validated electrical connections. L_HOST_ALLOCATION is a logical software relation. L_STORAGE_PATH does not resolve charging direction, returns or isolation. No load channel mapping is invented.\n\nPhysical routing is blocked. Provide reviewed connector and return pin maps, exact footprints, supported installed configurations, an approved pin-level netlist, current and voltage constraints, board geometry and a configured router before physical design. Catalog ratings cannot reconstruct proprietary COTS circuits.\n\nLocal validation from the Orbitwork source checkout:\n\n    node scripts/kicad-validate.mjs /path/to/unzipped-export\n\nThe validator retains raw KiCad SVG, netlist and ERC reports. Any zero ERC count concerns only these abstract sheets and establishes no electrical pass. Physical DRC is not run. The supplied workspace snapshot is for traceability, not permission to trust imported calculation caches.\n\nWarnings:\n${warnings.map(w => `- ${w}`).join('\n')}\n`;
  return { files: [
    { name: `${project}.kicad_pro`, content: JSON.stringify({ meta: { filename: `${project}.kicad_pro`, version: 1 }, text_variables: { ORBITWORK_SCOPE: 'REVIEW ONLY' } }, null, 2) + '\n' },
    { name: `${project}.kicad_sch`, content: root.join('\n') + '\n' }, ...files,
    { name: 'manifest.json', content: JSON.stringify(manifest, null, 2) + '\n' },
    { name: 'architecture-snapshot.json', content: JSON.stringify(snapshot, null, 2) + '\n' },
    { name: 'README.md', content: readme },
  ], warnings, scope: KICAD_SCOPE };
}

export { createKiCadZip } from './zip.ts';
export { buildReviewedKiCadRules } from './rules.ts';
export type { ReviewedPhysicalRules, ApprovedDimension, RuleSource, EpsRequirementId } from './rules';
