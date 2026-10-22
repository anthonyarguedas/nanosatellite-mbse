#!/usr/bin/env node
/** Dependency-free runtime check of the Catalog contract and reviewed-data invariants. */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const file = process.argv[2] ?? fileURLToPath(new URL('./catalog.json', import.meta.url));
const catalog = JSON.parse(readFileSync(file, 'utf8'));
const units = {
  powerBolW: 'W', powerEolW: 'W', vmpBolV: 'V', impBolA: 'A',
  vmpEolV: 'V', impEolA: 'A', vocV: 'V', iscA: 'A', energyWh: 'Wh',
  chargeAh: 'Ah', voltageMinV: 'V', voltageNominalV: 'V', voltageMaxV: 'V',
  massKg: 'kg', widthM: 'm', heightM: 'm', depthM: 'm', inputMinV: 'V',
  inputMaxV: 'V', maxInputW: 'W', maxChargeA: 'A', maxDischargeA: 'A',
  efficiency: '1', priceUsd: 'USD', cycleLife: 'cycles',
};
const roles = new Set(['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software']);
const levels = new Set(['cell', 'panel', 'pack', 'board', 'software']);
const meanings = new Set(['minimum', 'typical', 'maximum', 'nominal', 'estimated', 'specified']);
const statuses = new Set(['available', 'missing', 'not-applicable']);
const manufacturers = new Set(['www.azurspace.com', 'www.cesi.it', 'gomspace.com', 'isispace.nl']);
const counts = { available: 0, missing: 0, 'not-applicable': 0 };
let assertions = 0;
function check(test, message) { assertions++; assert.ok(test, message); }
function text(value, label) { check(typeof value === 'string' && value.trim().length > 0, label); }
function strings(value, label) {
  check(Array.isArray(value) && value.length > 0, label);
  value.forEach((x) => text(x, label));
}
function number(product, key) {
  const s = product.specs[key];
  return s?.status === 'available' && typeof s.value === 'number' ? s.value : null;
}
function close(actual, expected, relative = 1e-10) {
  return Math.abs(actual - expected) <= Math.max(1e-12, Math.abs(expected) * relative);
}

text(catalog.revision, 'catalog.revision');
check(Array.isArray(catalog.products) && catalog.products.length >= 6 && catalog.products.length <= 9, '6–9 products');
const ids = new Set();
for (const p of catalog.products) {
  const id = p.id;
  for (const key of ['id', 'revision', 'manufacturer', 'name', 'partNumber', 'description', 'accountingBoundary']) text(p[key], `${id}.${key}`);
  check(!ids.has(id), `${id}: duplicate product ID`); ids.add(id);
  check(levels.has(p.level), `${id}: level`);
  strings(p.roles, `${id}.roles`);
  check(new Set(p.roles).size === p.roles.length && p.roles.every((x) => roles.has(x)), `${id}: valid unique roles`);
  strings(p.supportedConfigurations, `${id}.supportedConfigurations`);
  strings(p.caveats, `${id}.caveats`);
  check(Array.isArray(p.sources) && p.sources.length > 0, `${id}: sources`);
  const sourceIds = new Set();
  for (const s of p.sources) {
    for (const key of ['id', 'title', 'url', 'revision', 'location', 'retrievedAt']) text(s[key], `${id}.source.${key}`);
    check(!sourceIds.has(s.id), `${id}: duplicate source ID`); sourceIds.add(s.id);
    const url = new URL(s.url);
    check(url.protocol === 'https:' && manufacturers.has(url.hostname) && url.pathname.endsWith('.pdf'), `${id}: direct manufacturer PDF`);
    check(/^\d{4}-\d{2}-\d{2}$/.test(s.retrievedAt) && Number.isFinite(Date.parse(s.retrievedAt)), `${id}: ISO retrieval date`);
    check(s.retrievedAt === '2026-10-17', `${id}: reviewed shell-date retrieval`);
  }
  check(p.specs && typeof p.specs === 'object' && !Array.isArray(p.specs), `${id}: specs object`);
  for (const [key, unit] of Object.entries(units)) check(p.specs[key]?.unit === unit, `${id}.${key}: explicit field and normalized unit`);
  for (const [key, s] of Object.entries(p.specs)) {
    check(s && typeof s === 'object', `${id}.${key}: specification object`);
    for (const field of ['unit', 'meaning', 'status', 'original', 'conditions', 'location']) text(s[field], `${id}.${key}.${field}`);
    check(meanings.has(s.meaning) && statuses.has(s.status), `${id}.${key}: enums`);
    check(Object.hasOwn(s, 'value') && Object.hasOwn(s, 'sourceId'), `${id}.${key}: explicit nullable fields`);
    check(s.sourceId === null || sourceIds.has(s.sourceId), `${id}.${key}: valid local source reference`);
    if (s.status === 'available') {
      check(s.value !== null && s.sourceId !== null, `${id}.${key}: available has value and source`);
      check(typeof s.value === 'string' || (typeof s.value === 'number' && Number.isFinite(s.value)) ||
        (Array.isArray(s.value) && s.value.length > 0 && s.value.every((v) => typeof v === 'number' && Number.isFinite(v))), `${id}.${key}: typed finite value`);
    } else {
      check(s.value === null, `${id}.${key}: unavailable is null, never zero`);
      text(s.rationale, `${id}.${key}: unavailable rationale`);
    }
    counts[s.status]++;
  }
  for (const key of ['widthM', 'heightM', 'depthM']) check(number(p, key) === null || number(p, key) > 0, `${id}: positive ${key}`);
  const eff = number(p, 'efficiency');
  check(eff === null || (eff > 0 && eff <= 1), `${id}: efficiency fraction`);
  const lo = number(p, 'voltageMinV'), nom = number(p, 'voltageNominalV'), hi = number(p, 'voltageMaxV');
  check(lo === null || nom === null || lo <= nom, `${id}: voltage min ≤ nominal`);
  check(hi === null || nom === null || nom <= hi, `${id}: voltage nominal ≤ max`);
  if (p.roles.includes('solar')) {
    const v = number(p, 'vmpBolV'), i = number(p, 'impBolA');
    check(v > 0 && i > 0 && number(p, 'vocV') >= v && number(p, 'iscA') >= i, `${id}: coherent BOL MPP`);
    // CESI independently rounded average density and MPP columns differ by 1.18%, documented in caveats.
    check(close(number(p, 'powerBolW'), v * i, id === 'cesi-ctj30-26p5' ? .02 : 1e-10), `${id}: coherent BOL power`);
    const ve = number(p, 'vmpEolV'), ie = number(p, 'impEolA'), pe = number(p, 'powerEolW');
    if (ve !== null || ie !== null || pe !== null) {
      check(ve > 0 && ie > 0 && close(pe, ve * ie), `${id}: EOL uses sourced MPP pair`);
      check(ve <= v && ie <= i && pe <= number(p, 'powerBolW'), `${id}: radiation endpoint coherence`);
      check(p.specs.vmpEolV.meaning === 'typical' && /1E15|10\^15/.test(p.specs.vmpEolV.original), `${id}: conditional, typical EOL case`);
    }
  }
  if (p.roles.includes('battery')) {
    for (const key of ['cycleLife', 'cycleLifeModel', 'retainedEnergyFraction', 'retainedChargeFraction', 'chargeEfficiency', 'dischargeEfficiency', 'coulombicChargeEfficiency', 'coulombicDischargeEfficiency']) {
      check(p.specs[key]?.status === 'missing' && p.specs[key].value === null, `${id}: explicit aging/charge-model gap ${key}`);
    }
    const energy = number(p, 'energyWh'), charge = number(p, 'chargeAh');
    if (energy !== null && charge !== null && nom !== null) check(close(energy, nom * charge, .03), `${id}: energy/charge/voltage sanity, not a battery model`);
  }
  if (p.roles.includes('processor')) check(p.specs.processorDescription?.status === 'available', `${id}: processor role has explicit evidence`);
  check(!p.roles.includes('software'), `${id}: no unsupported software allocation in this catalog`);
  if (p.roles.length > 1) check(/once/.test(p.accountingBoundary), `${id}: integrated physical boundary counted once`);
  check(p.specs.priceUsd.status === 'missing' && p.specs.priceUsd.value === null, `${id}: no unsupported prices`);
}
for (const role of ['solar', 'battery', 'conditioning']) check(catalog.products.filter((p) => p.roles.includes(role)).length >= 2, `two alternatives for ${role}`);
const azur = catalog.products.find((p) => p.id === 'azur-3g30c-advanced-81780');
check(close(number(azur, 'powerEolW'), 2.15118), 'AZUR bare-cell endpoint, not CIC current');
const isis = catalog.products.find((p) => p.id === 'isis-iceps2-type-a');
check(isis.specs.energyWh.status === 'missing', 'ICEPS2 conflicting energy remains unresolved');
check(number(isis, 'inputMaxV') === 7.5 && number(isis, 'absoluteInputMaxV') === 15, 'tracking/absolute input limits kept separate');
const p80 = catalog.products.find((p) => p.id === 'gomspace-p80-config1');
check(!p80.roles.includes('battery') && close(number(p80, 'massKg'), .3608), 'P80 configuration-1 boundary excludes battery');
console.log(JSON.stringify({ products: catalog.products.length, specifications: Object.values(counts).reduce((a, b) => a + b, 0), counts, assertions, result: 'PASS' }, null, 2));
