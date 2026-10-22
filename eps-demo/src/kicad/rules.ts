import type { KiCadExport } from './index';

export type EpsRequirementId = `EPS-${string}`;
export interface RuleSource { id: string; url: string; revision: string; location: string }
export interface ApprovedDimension {
  minimumMm: number;
  preferredMm?: number;
  maximumMm?: number;
  requirementIds: EpsRequirementId[];
  sourceIds: string[];
  rationale: string;
  derivation: { method: string; conditions: string; margin: string };
}
export interface ReviewedPhysicalRules {
  schemaVersion: 1;
  architectureFingerprint: string;
  catalogRevision: string;
  physicalNetlistRevision: string;
  approval: { status: 'approved'; engineer: string; date: string };
  sources: RuleSource[];
  /** Exact engineer-reviewed physical net names. These are never inferred from logical sheet ports. */
  knownNets: string[];
  fabrication: {
    sourceIds: string[];
    minimumTrackWidthMm: number;
    minimumClearanceMm: number;
    minimumViaDiameterMm: number;
    minimumDrillMm: number;
    minimumAnnularWidthMm: number;
    minimumEdgeClearanceMm: number;
  };
  classes: {
    name: string;
    nets: string[];
    trackWidth: ApprovedDimension;
    clearance: ApprovedDimension;
    viaDiameter: ApprovedDimension;
    /** A reviewed maximum is required to check worst-case annular geometry. */
    viaDrill: ApprovedDimension;
  }[];
  edgeClearance: ApprovedDimension;
}

const SCOPE = 'Engineer-approved physical rule sidecars for KiCad 10. These enforce only supplied geometric bounds. No current-to-width or voltage-to-clearance derivation is performed. No PCB is generated. No complete EPS predicate, electrical compatibility or flight qualification is established.';
const BASE = 'orbitwork-physical-rules';
const positive = (n: unknown): n is number => typeof n === 'number' && Number.isFinite(n) && n > 0;
const nonempty = (s: unknown): s is string => typeof s === 'string' && s.trim().length > 0;
const literalNet = (s: string) => typeof s === 'string' && s.length > 0 && !/[^A-Za-z0-9_+:/.-]/.test(s) && !(s.startsWith('/') && s.endsWith('/'));
const quote = (s: string) => JSON.stringify(s);
const FABRICATION_KEYS = ['minimumTrackWidthMm', 'minimumClearanceMm', 'minimumViaDiameterMm', 'minimumDrillMm', 'minimumAnnularWidthMm', 'minimumEdgeClearanceMm'] as const;

/** CLI and browser imports are untrusted JSON, even though the public API is typed. */
function validateStructure(input: ReviewedPhysicalRules): void {
  const record = (value: unknown): boolean => Boolean(value && typeof value === 'object' && !Array.isArray(value));
  const fail = (message: string): never => { throw new Error(`KiCad physical rules blocked: ${message}`); };
  const list = (value: unknown, label: string, maximum: number): void => {
    if (!Array.isArray(value) || value.length > maximum) fail(`${label} must be a list of at most ${maximum} items.`);
  };
  if (!record(input)) fail('The profile must be a JSON object.');
  if (!record(input.approval)) fail('An approval record is required.');
  if (!record(input.fabrication)) fail('Fabrication limits are required.');
  list(input.sources, 'Sources', 256);
  list(input.knownNets, 'Known physical nets', 2048);
  list(input.classes, 'Netclasses', 64);
  list(input.fabrication.sourceIds, 'Fabrication source references', 256);
  for (const source of input.sources) if (!record(source)) fail('Each source must be an object.');
  const dimension = (value: ApprovedDimension, label: string): void => {
    if (!record(value)) fail(`${label} requires an approved dimension record.`);
    list(value.requirementIds, `${label} requirement references`, 20);
    list(value.sourceIds, `${label} source references`, 256);
  };
  for (const c of input.classes) {
    if (!record(c)) fail('Each netclass must be an object.');
    list(c.nets, 'Netclass physical nets', 2048);
    for (const key of ['trackWidth', 'clearance', 'viaDiameter', 'viaDrill'] as const) dimension(c[key], key);
  }
  dimension(input.edgeClearance, 'Board edge clearance');
}

/**
 * Generate a NEW project and same-basename custom rules, with no assumed electrical conversions.
 * expectedFingerprint must come from the current architecture export. This is a traceability gate, not a digital approval signature.
 */
export function buildReviewedKiCadRules(input: ReviewedPhysicalRules, expectedFingerprint: string): KiCadExport {
  validateStructure(input);
  const issues: string[] = [];
  const warnings = [SCOPE, 'Use these sidecars only after reconciling exact nets, reviewed geometry and fabrication settings in a physical KiCad project. Do not overwrite an existing project without merging its settings.',
    'Netclass width and via sizes are routing defaults. The custom rules enforce their stated limits. Later matching clearance rules have priority. This generator orders them from smaller to larger bounds.',
    'The installed CLI can silently ignore malformed custom rules. Run Check rule syntax in KiCad and verify expected rule violations on a deliberately perturbed fixture. A CLI exit code alone is insufficient.',
    'Known EPS failures remain failed after a DRC pass. Energy, operating limits, protection behavior, temperatures, full installation fit and qualification remain external assessments.'];
  if (input.schemaVersion !== 1) issues.push('Unsupported physical-rule schema.');
  if (!nonempty(expectedFingerprint) || input.architectureFingerprint !== expectedFingerprint) issues.push('Physical rules are stale or belong to another architecture fingerprint.');
  if (!nonempty(input.catalogRevision) || !nonempty(input.physicalNetlistRevision)) issues.push('Catalog and reviewed physical netlist revisions are required.');
  if (input.approval?.status !== 'approved' || !nonempty(input.approval.engineer) || !nonempty(input.approval.date) || Number.isNaN(Date.parse(input.approval.date))) issues.push('An explicit engineer approval and valid date are required.');
  const sources = new Set<string>();
  for (const source of input.sources) {
    if (!nonempty(source.id) || /[^A-Za-z0-9_.:-]/.test(source.id) || sources.has(source.id) || !/^https?:\/\//.test(source.url) || !nonempty(source.revision) || !nonempty(source.location)) issues.push('Every source needs a unique safe ID, HTTP(S) URL, revision and location.');
    sources.add(source.id);
  }
  const sourceRefs = (refs: string[], label: string) => {
    if (!refs.length || refs.some(id => !sources.has(id))) issues.push(`${label}: referenced evidence sources are missing.`);
  };
  const dimension = (d: ApprovedDimension, label: string, fabricationMin: number) => {
    if (!positive(d.minimumMm) || d.minimumMm < fabricationMin) issues.push(`${label}: minimum must be positive and at least the fabrication minimum.`);
    if (d.preferredMm !== undefined && (!positive(d.preferredMm) || d.preferredMm < d.minimumMm)) issues.push(`${label}: preferred size is below its minimum.`);
    if (d.maximumMm !== undefined && (!positive(d.maximumMm) || d.maximumMm < (d.preferredMm ?? d.minimumMm))) issues.push(`${label}: maximum is below the preferred/minimum size.`);
    if (!d.requirementIds.length || d.requirementIds.some(id => !/^EPS-(0[1-9]|1[0-9]|20)$/.test(id))) issues.push(`${label}: EPS-01 through EPS-20 traceability is required.`);
    sourceRefs(d.sourceIds, label);
    if (!nonempty(d.rationale) || !d.derivation || !nonempty(d.derivation.method) || !nonempty(d.derivation.conditions) || !nonempty(d.derivation.margin)) issues.push(`${label}: reviewed rationale, derivation method, conditions and margin are required.`);
  };
  sourceRefs(input.fabrication.sourceIds, 'Fabrication');
  for (const key of FABRICATION_KEYS) {
    if (!positive(input.fabrication[key])) issues.push(`Fabrication ${key} must be a positive millimeter value.`);
  }
  if (!input.knownNets.length || input.knownNets.some(n => !literalNet(n)) || new Set(input.knownNets).size !== input.knownNets.length) issues.push('Reviewed physical nets must be unique, nonempty literal names. Wildcards, quotes and regular expressions are unsupported.');
  if (!input.classes.length) issues.push('At least one reviewed netclass is required.');
  const usedNets = new Set<string>(), names = new Set<string>();
  for (const c of input.classes) {
    if (!/^[A-Za-z][A-Za-z0-9_-]{0,40}$/.test(c.name) || c.name === 'Default' || names.has(c.name)) issues.push('Netclass names must be unique safe identifiers distinct from Default.');
    names.add(c.name);
    if (!c.nets.length) issues.push(`${c.name}: exact net assignments are required.`);
    for (const net of c.nets) {
      if (!literalNet(net) || !input.knownNets.includes(net)) issues.push(`${c.name}: unknown or unsupported physical net ${net}.`);
      if (usedNets.has(net)) issues.push(`${net}: overlapping netclass assignments are unsupported.`);
      usedNets.add(net);
    }
    dimension(c.trackWidth, `${c.name} track width`, input.fabrication.minimumTrackWidthMm);
    dimension(c.clearance, `${c.name} clearance`, input.fabrication.minimumClearanceMm);
    dimension(c.viaDiameter, `${c.name} via diameter`, input.fabrication.minimumViaDiameterMm);
    dimension(c.viaDrill, `${c.name} via drill`, input.fabrication.minimumDrillMm);
    if (!positive(c.viaDrill.maximumMm)) issues.push(`${c.name}: a reviewed maximum drill is required for annular geometry.`);
    else if (c.viaDiameter.minimumMm < c.viaDrill.maximumMm + 2 * input.fabrication.minimumAnnularWidthMm) issues.push(`${c.name}: minimum via diameter cannot preserve the fabrication annular width at maximum drill.`);
    if (c.clearance.preferredMm !== undefined || c.clearance.maximumMm !== undefined) issues.push(`${c.name}: clearance supports a minimum only.`);
  }
  dimension(input.edgeClearance, 'Board edge clearance', input.fabrication.minimumEdgeClearanceMm);
  if (input.edgeClearance.preferredMm !== undefined || input.edgeClearance.maximumMm !== undefined) issues.push('Board edge clearance supports a minimum only.');
  if (issues.length) throw new Error(`KiCad physical rules blocked: ${[...new Set(issues)].join(' ')}`);
  const unresolvedNets = input.knownNets.filter(net => !usedNets.has(net));
  if (unresolvedNets.length) warnings.push(`No EPS-derived netclass is assigned to: ${unresolvedNets.join(', ')}. Only explicit fabrication defaults apply.`);
  const classes = [...input.classes].sort((a, b) => a.name.localeCompare(b.name, 'en'));
  const rules: string[] = ['(version 1)', '# Generated only from explicitly approved dimensions. No electrical conversion or PCB generation.'];
  const provenance: { ruleName: string; constraint: string; netclass: string | null; approvedDimension: ApprovedDimension }[] = [];
  const add = (name: string, constraint: string, d: ApprovedDimension, netclass: string | null, condition?: string) => {
    rules.push(`# ${d.requirementIds.join(', ')} | sources: ${d.sourceIds.join(', ')}`);
    rules.push(`(rule ${quote(name)}${condition ? `\n  (condition ${quote(condition)})` : ''}\n  (constraint ${constraint} (min ${d.minimumMm}mm)${d.preferredMm !== undefined ? ` (opt ${d.preferredMm}mm)` : ''}${d.maximumMm !== undefined ? ` (max ${d.maximumMm}mm)` : ''}))`);
    provenance.push({ ruleName: name, constraint, netclass, approvedDimension: d });
  };
  for (const c of classes) {
    const condition = c.nets.map(net => `A.NetName == '${net}'`).join(' || ');
    add(`${c.name}_track_width`, 'track_width', c.trackWidth, c.name, condition);
    add(`${c.name}_via_diameter`, 'via_diameter', c.viaDiameter, c.name, condition);
    add(`${c.name}_via_drill`, 'hole_size', c.viaDrill, c.name, `A.Type == 'Via' && (${condition})`);
  }
  // Any pair touching two classes receives the larger required spacing, independent of class name order.
  for (const c of [...classes].sort((a, b) => a.clearance.minimumMm - b.clearance.minimumMm || a.name.localeCompare(b.name, 'en'))) {
    const condition = c.nets.map(net => `(A.NetName == '${net}' || B.NetName == '${net}')`).join(' || ');
    add(`${c.name}_clearance`, 'clearance', c.clearance, c.name, condition);
  }
  add('board_edge_clearance', 'edge_clearance', input.edgeClearance, null);
  const defaults = input.fabrication;
  const project = {
    meta: { filename: `${BASE}.kicad_pro`, version: 3 },
    board: { design_settings: { rules: {
      min_clearance: defaults.minimumClearanceMm, min_track_width: defaults.minimumTrackWidthMm,
      min_via_diameter: defaults.minimumViaDiameterMm, min_through_hole_diameter: defaults.minimumDrillMm,
      min_via_annular_width: defaults.minimumAnnularWidthMm, min_copper_edge_clearance: defaults.minimumEdgeClearanceMm,
    } } },
    net_settings: { meta: { version: 4 }, classes: [
      { name: 'Default', priority: 2147483647, clearance: defaults.minimumClearanceMm, track_width: defaults.minimumTrackWidthMm,
        via_diameter: Math.max(defaults.minimumViaDiameterMm, defaults.minimumDrillMm + 2 * defaults.minimumAnnularWidthMm), via_drill: defaults.minimumDrillMm },
      ...classes.map((c, index) => ({ name: c.name, priority: index, clearance: c.clearance.minimumMm,
        track_width: c.trackWidth.preferredMm ?? c.trackWidth.minimumMm, via_diameter: c.viaDiameter.preferredMm ?? c.viaDiameter.minimumMm, via_drill: c.viaDrill.preferredMm ?? c.viaDrill.minimumMm })),
    ], netclass_assignments: null, netclass_patterns: classes.flatMap(c => c.nets.map(net => ({ netclass: c.name, pattern: net }))) },
  };
  const manifest = { schemaVersion: 1, supportedKiCad: '10.x, exercised with 10.0.7', scope: SCOPE,
    architectureFingerprint: input.architectureFingerprint, catalogRevision: input.catalogRevision, physicalNetlistRevision: input.physicalNetlistRevision,
    approval: input.approval, sources: input.sources, fabrication: input.fabrication, rules: provenance,
    netAssignments: classes.map(c => ({ netclass: c.name, exactNets: c.nets })), unresolvedNets,
    unresolvedDerivations: 'No missing dimensions are synthesized. This export accepts reviewed dimensions only. The engineer remains responsible for the derivations and their scope.',
    generatedBoard: false, ruleApplicationValidated: false, erc: 'not-run', drc: 'not-run', warnings };
  return { scope: SCOPE, warnings, files: [
    { name: `${BASE}.kicad_dru`, content: rules.join('\n') + '\n' },
    { name: `${BASE}.kicad_pro`, content: JSON.stringify(project, null, 2) + '\n' },
    { name: 'physical-rules-manifest.json', content: JSON.stringify(manifest, null, 2) + '\n' },
  ] };
}
