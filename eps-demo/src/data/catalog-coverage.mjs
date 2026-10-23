#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { catalogCoverage } from '../catalog/coverage.ts';
const args = process.argv.slice(2);
const file = args.find(arg => !arg.startsWith('--')) ?? fileURLToPath(new URL('./catalog.json', import.meta.url));
const report = catalogCoverage(JSON.parse(readFileSync(file, 'utf8')));
console.log(JSON.stringify(args.includes('--details') ? report : { ...report, roles: report.roles.map(({ products, ...role }) => ({ ...role, missingCore: products.map(p => ({ productId: p.productId, covered: p.coreCovered, required: p.coreRequired, missing: p.core.filter(r => !r.covered).map(r => r.label) })) })) }, null, 2));
if (report.integrityIssues.length || (args.includes('--strict') && report.roles.some(role => role.deficit))) process.exitCode = 1;
