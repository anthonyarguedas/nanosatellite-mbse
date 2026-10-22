#!/usr/bin/env node
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { buildKiCadExport, createKiCadZip } from '../src/kicad/index.ts';

const [snapshotPath, catalogPath, outputPath] = process.argv.slice(2);
if (!snapshotPath || !catalogPath || !outputPath) {
  console.error('Usage: node scripts/kicad-export.mjs WORKSPACE.json CATALOG.json OUTPUT_DIRECTORY');
  process.exit(2);
}
try {
  const input = JSON.parse(await readFile(snapshotPath, 'utf8'));
  const catalog = JSON.parse(await readFile(catalogPath, 'utf8'));
  const result = buildKiCadExport(input.workspace ?? input, catalog);
  const output = path.resolve(outputPath);
  await mkdir(output, { recursive: true });
  for (const file of result.files) await writeFile(path.join(output, file.name), file.content, { flag: 'wx' });
  await writeFile(path.join(output, 'orbitwork-review.zip'), createKiCadZip(result.files), { flag: 'wx' });
  console.log(JSON.stringify({ output, scope: result.scope, warnings: result.warnings, files: result.files.map(file => file.name) }, null, 2));
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
}
