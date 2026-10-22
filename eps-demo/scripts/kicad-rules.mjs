#!/usr/bin/env node
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { buildReviewedKiCadRules, getKiCadArchitectureFingerprint, getKiCadReadiness } from '../src/kicad/index.ts';

const [architectureDirectory, reviewedRulesPath, outputPath] = process.argv.slice(2);
if (!architectureDirectory || !reviewedRulesPath || !outputPath) {
  console.error('Usage: node scripts/kicad-rules.mjs UNZIPPED_ARCHITECTURE_EXPORT REVIEWED_RULES.json NEW_OUTPUT_DIRECTORY');
  process.exit(2);
}
try {
  const architecture = JSON.parse(await readFile(path.join(architectureDirectory, 'architecture-snapshot.json'), 'utf8'));
  const manifest = JSON.parse(await readFile(path.join(architectureDirectory, 'manifest.json'), 'utf8'));
  const input = JSON.parse(await readFile(reviewedRulesPath, 'utf8'));
  const catalog = { revision: architecture.catalogRevision, products: architecture.selectedCatalogEntries };
  const readiness = getKiCadReadiness(architecture.workspace, catalog);
  if (!readiness.ready) throw new Error(readiness.blockers.join(' '));
  const fingerprint = getKiCadArchitectureFingerprint(architecture.workspace, catalog);
  if (manifest.architectureFingerprint !== fingerprint || input.catalogRevision !== catalog.revision) throw new Error('Architecture/catalog evidence has changed. Reexport and review the rules again.');
  const result = buildReviewedKiCadRules(input, fingerprint);
  await mkdir(outputPath, { recursive: true });
  for (const file of result.files) await writeFile(path.join(outputPath, file.name), file.content, { flag: 'wx' });
  console.log(JSON.stringify({ output: path.resolve(outputPath), files: result.files.map(file => file.name), warnings: result.warnings }, null, 2));
} catch (error) { console.error(error instanceof Error ? error.message : error); process.exit(1); }
