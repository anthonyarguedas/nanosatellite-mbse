#!/usr/bin/env node
/** Integrity is independent of coverage and architecture feasibility. Node 22 needs --experimental-strip-types. */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { validateCatalog } from '../catalog/validation.ts';

const file = process.argv[2] ?? fileURLToPath(new URL('./catalog.json', import.meta.url));
const catalog = JSON.parse(readFileSync(file, 'utf8'));
const issues = validateCatalog(catalog);
console.log(JSON.stringify({ products: catalog.products?.length, integrity: issues.length ? 'FAIL' : 'PASS', issues, scope: 'Record integrity only. Coverage and architecture feasibility are separate.' }, null, 2));
if (issues.length) process.exitCode = 1;
