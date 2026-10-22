#!/usr/bin/env node
// All dimensions, nets and approval records in this probe are SYNTHETIC TEST DATA.
// This regression proves that five generated constraints actually fire. It designs no EPS board.
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { buildReviewedKiCadRules } from '../src/kicad/index.ts';

const directory = path.resolve(process.argv[2] || 'kicad/rule-probe');
const cli = process.env.KICAD_CLI || '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli';
const python = process.env.KICAD_PYTHON || '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3';
const dimension = (minimumMm, requirementId = 'EPS-07') => ({ minimumMm, requirementIds: [requirementId], sourceIds: ['synthetic'],
  rationale: 'Arbitrary regression test value. No actual EPS derivation or approval.',
  derivation: { method: 'SYNTHETIC TEST ONLY', conditions: 'SYNTHETIC TEST ONLY', margin: 'SYNTHETIC TEST ONLY' } });
const input = {
  schemaVersion: 1, architectureFingerprint: 'synthetic-rule-probe', catalogRevision: 'synthetic-test-only', physicalNetlistRevision: 'synthetic-nets-only',
  approval: { status: 'approved', engineer: 'SYNTHETIC TEST ONLY, no engineering authority', date: '2026-10-17' },
  sources: [{ id: 'synthetic', url: 'https://example.org/synthetic-test', revision: 'test-1', location: 'Regression fixture, no manufacturer evidence' }],
  knownNets: ['EPS_BUS', 'GND'], fabrication: { sourceIds: ['synthetic'], minimumTrackWidthMm: 0.1, minimumClearanceMm: 0.1,
    minimumViaDiameterMm: 0.4, minimumDrillMm: 0.2, minimumAnnularWidthMm: 0.1, minimumEdgeClearanceMm: 0.1 },
  classes: [{ name: 'EPS_POWER', nets: ['EPS_BUS'], trackWidth: { ...dimension(0.8), preferredMm: 0.8 }, clearance: dimension(0.5, 'EPS-03'),
    viaDiameter: { ...dimension(0.8), preferredMm: 0.8 }, viaDrill: { ...dimension(0.4), preferredMm: 0.4, maximumMm: 0.4 } }],
  edgeClearance: dimension(0.5, 'EPS-20'),
};
const pythonScript = `
import pcbnew as p
import sys
board = p.BOARD()
board.SetCopperLayerCount(2)
nets = {}
for name in ('EPS_BUS', 'GND'):
    net = p.NETINFO_ITEM(board, name)
    board.Add(net)
    nets[name] = net
def point(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))
for a, b in [((0,0),(40,0)), ((40,0),(40,30)), ((40,30),(0,30)), ((0,30),(0,0))]:
    line = p.PCB_SHAPE()
    line.SetShape(p.SHAPE_T_SEGMENT)
    line.SetStart(point(*a))
    line.SetEnd(point(*b))
    line.SetWidth(p.FromMM(0.05))
    line.SetLayer(p.Edge_Cuts)
    board.Add(line)
for net, a, b, layer in [('EPS_BUS',(5,5),(15,5),p.F_Cu), ('GND',(5,5.5),(15,5.5),p.F_Cu), ('EPS_BUS',(15,5),(20,5),p.B_Cu), ('EPS_BUS',(0.3,10),(10,10),p.F_Cu)]:
    track = p.PCB_TRACK(board)
    track.SetStart(point(*a))
    track.SetEnd(point(*b))
    track.SetWidth(p.FromMM(0.2))
    track.SetLayer(layer)
    track.SetNet(nets[net])
    board.Add(track)
via = p.PCB_VIA(board)
via.SetPosition(point(15,5))
via.SetWidth(p.FromMM(0.6))
via.SetDrill(p.FromMM(0.3))
via.SetViaType(p.VIATYPE_THROUGH)
via.SetLayerPair(p.F_Cu, p.B_Cu)
via.SetNet(nets['EPS_BUS'])
board.Add(via)
p.SaveBoard(sys.argv[1], board)
print('Synthetic, deliberately violating geometry. KiCad', p.GetBuildVersion())
`;
try {
  await mkdir(directory, { recursive: true });
  const result = buildReviewedKiCadRules(input, input.architectureFingerprint);
  for (const file of result.files) await writeFile(path.join(directory, file.name), file.content, { flag: 'wx' });
  await writeFile(path.join(directory, 'approved-test-input.json'), JSON.stringify(input, null, 2) + '\n', { flag: 'wx' });
  const board = path.join(directory, 'orbitwork-physical-rules.kicad_pcb');
  const generated = spawnSync(python, ['-c', pythonScript, board], { encoding: 'utf8', timeout: 30_000 });
  await writeFile(path.join(directory, 'python.log'), `${generated.stdout ?? ''}${generated.stderr ?? ''}${generated.error?.message ?? ''}`);
  if (generated.status !== 0) throw new Error('Synthetic board generation failed. Read python.log.');
  const args = ['pcb', 'drc', '--format', 'json', '--severity-all', '--all-track-errors', '--exit-code-violations', '--output', path.join(directory, 'drc.json'), board];
  const checked = spawnSync(cli, args, { encoding: 'utf8', timeout: 60_000 });
  await writeFile(path.join(directory, 'drc.log'), `${checked.stdout ?? ''}${checked.stderr ?? ''}${checked.error?.message ?? ''}`);
  if (checked.status !== 5) throw new Error(`Expected deliberate DRC violations, received ${checked.status}. Read drc.log.`);
  const report = JSON.parse(await readFile(path.join(directory, 'drc.json'), 'utf8'));
  const names = ['EPS_POWER_track_width', 'EPS_POWER_via_diameter', 'EPS_POWER_via_drill', 'EPS_POWER_clearance', 'board_edge_clearance'];
  const coverage = Object.fromEntries(names.map(name => [name, report.violations.filter(v => v.description.includes(`rule '${name}'`)).length]));
  if (Object.values(coverage).some(count => count < 1)) throw new Error(`Generated rule coverage is incomplete: ${JSON.stringify(coverage)}`);
  const summary = { scope: 'SYNTHETIC REGRESSION ONLY. No COTS PCB was generated or routed. All geometry intentionally violates arbitrary test bounds.',
    kicadVersion: report.kicad_version, exitCode: checked.status, generatedRuleViolationCoverage: coverage,
    violations: report.violations.length, unconnectedItems: report.unconnected_items?.length ?? 0, ignoredChecks: report.ignored_checks,
    electricalValidation: 'not-applicable, no component circuit', physicalRouting: 'not-performed',
    invocation: ['kicad-cli', ...args.map(a => a.startsWith(directory) ? path.relative(directory, a) : a)] };
  await writeFile(path.join(directory, 'probe-validation.json'), JSON.stringify(summary, null, 2) + '\n');
  console.log(JSON.stringify(summary, null, 2));
} catch (error) { console.error(error instanceof Error ? error.message : error); process.exit(1); }
