#!/usr/bin/env node
import { readFile, mkdir, writeFile, access } from 'node:fs/promises';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const [directory] = process.argv.slice(2);
if (!directory) { console.error('Usage: node scripts/kicad-validate.mjs UNZIPPED_EXPORT_DIRECTORY'); process.exit(2); }
try {
  const root = path.resolve(directory);
  const manifest = JSON.parse(await readFile(path.join(root, 'manifest.json'), 'utf8'));
  if (manifest.scope !== (await import('../src/kicad/index.ts')).KICAD_SCOPE || manifest.physicalRouting?.boardGenerated !== false) throw new Error('Expected an Orbitwork review-only export.');
  const schematic = manifest.drawing?.root;
  if (typeof schematic !== 'string' || !/^[a-zA-Z0-9._-]+\.kicad_sch$/.test(schematic)) throw new Error('Invalid root schematic file name.');
  const output = path.join(root, 'validation');
  await mkdir(path.join(output, 'svg'), { recursive: true });
  let cli = process.env.KICAD_CLI || 'kicad-cli';
  if (!process.env.KICAD_CLI) {
    try { await access('/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'); cli = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'; } catch { /* Use PATH. */ }
  }
  const commands = [];
  function run(args, log, acceptable = [0]) {
    const result = spawnSync(cli, args, { cwd: root, encoding: 'utf8', timeout: 120_000, maxBuffer: 10_000_000 });
    commands.push({ program: 'kicad-cli', args, exitCode: result.status, error: result.error?.message ?? null });
    return { result, log, acceptable };
  }
  async function retain(invocation) {
    const { result, log, acceptable } = invocation;
    await writeFile(path.join(output, log), `${result.stdout ?? ''}${result.stderr ?? ''}${result.error?.message ?? ''}`);
    if (!acceptable.includes(result.status)) throw new Error(`KiCad failed (${result.status}). Read validation/${log}.`);
    return result;
  }
  const version = (await retain(run(['version'], 'version.txt'))).stdout.trim();
  await retain(run(['sch', 'export', 'svg', '--black-and-white', '--output', 'validation/svg', schematic], 'svg.log'));
  await retain(run(['sch', 'export', 'netlist', '--format', 'kicadsexpr', '--output', 'validation/review.net', schematic], 'netlist.log'));
  const ercResult = await retain(run(['sch', 'erc', '--format', 'json', '--severity-all', '--exit-code-violations', '--output', 'validation/erc.json', schematic], 'erc.log', [0, 5]));
  const erc = JSON.parse(await readFile(path.join(output, 'erc.json'), 'utf8'));
  const violations = (erc.sheets ?? []).flatMap(sheet => sheet.violations ?? []);
  const netlist = await readFile(path.join(output, 'review.net'), 'utf8');
  const physicalComponents = [...netlist.matchAll(/\(comp\s+\(ref\s/g)].length;
  if (physicalComponents !== 0) throw new Error('Unexpected physical components in a logical review drawing.');
  const summary = {
    kicadVersion: version, schematicParsedAndRendered: true,
    physicalComponents, erc: { exitCode: ercResult.status, violations: violations.length, report: 'erc.json',
      interpretation: 'Structural report on abstract sheets only. Even zero violations establishes no electrical compatibility or EPS requirement pass.' },
    drc: { status: 'not-run', reason: 'No PCB or physical netlist is generated.' },
    unresolvedLogicalAssociations: manifest.drawing.unresolvedLogicalAssociations,
    unresolvedPhysicalNets: manifest.physicalRouting.unresolvedPhysicalNets,
    scope: manifest.scope, commands,
  };
  await writeFile(path.join(output, 'validation.json'), JSON.stringify(summary, null, 2) + '\n');
  console.log(JSON.stringify(summary, null, 2));
} catch (error) { console.error(error instanceof Error ? error.message : error); process.exit(1); }
