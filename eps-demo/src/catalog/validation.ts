import type { Catalog, Product, Source, Specification } from '../types.ts';
import { ROLES, SPEC_DEFINITIONS } from './profiles.ts';

export const PRODUCT_LIMIT = 128;
export function legacyArrayForm(product: Product, key: string): Specification['valueForm'] | undefined {
  if (typeof product.revision !== 'string' || !product.revision.startsWith('catalog-record-1;')) return undefined;
  if (product.id === 'cesi-ctj30-26p5' && key === 'massKg') return 'interval';
  if (product.id === 'isis-iceps2-type-a' && ['sourcedChargeCurrentMinTypMaxA', 'sourcedDischargeCurrentMinTypMaxA'].includes(key)) return 'min-typ-max';
  return undefined;
}
const text = (x: unknown): x is string => typeof x === 'string' && x.trim().length > 0;
export function sourceIssues(source: Source): string[] {
  const issues: string[] = [];
  if (!source || typeof source !== 'object' || Array.isArray(source)) return ['invalid source object'];
  for (const key of ['id', 'title', 'url', 'revision', 'location', 'retrievedAt'] as const) if (!text(source?.[key])) issues.push(`source.${key} is missing`);
  try { if (!['https:', 'http:'].includes(new URL(source.url).protocol)) throw new Error(); } catch { issues.push('source URL must be HTTP(S)'); }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(source.retrievedAt ?? '')) issues.push('source retrieval date must be an ISO calendar date');
  else { const d = new Date(`${source.retrievedAt}T00:00:00Z`); if (!Number.isFinite(d.getTime()) || d.toISOString().slice(0, 10) !== source.retrievedAt) issues.push('source retrieval date is invalid'); }
  if (source.publisher !== undefined && !text(source.publisher)) issues.push('source publisher is empty');
  if (source.kind !== undefined && !['manufacturer', 'maintainer', 'test-report'].includes(source.kind)) issues.push('source kind is invalid');
  if (source.sha256 !== undefined && !/^[a-f0-9]{64}$/i.test(source.sha256)) issues.push('source SHA-256 is invalid');
  return issues;
}
export function specificationIssues(product: Product, key: string, spec: Specification | undefined): string[] {
  if (!spec || typeof spec !== 'object' || Array.isArray(spec)) return ['no specification record'];
  const issues: string[] = [];
  for (const field of ['unit', 'original', 'conditions', 'location'] as const) if (!text(spec[field])) issues.push(`${field} is missing`);
  if (!['minimum', 'typical', 'maximum', 'nominal', 'estimated', 'specified', 'measured'].includes(spec.meaning)) issues.push('invalid meaning');
  if (!['available', 'missing', 'not-applicable'].includes(spec.status)) issues.push('invalid status');
  if (!Object.hasOwn(spec, 'value') || !Object.hasOwn(spec, 'sourceId')) issues.push('explicit nullable value/sourceId required');
  if (spec.valueForm !== undefined && !['scalar', 'interval', 'min-typ-max', 'set'].includes(spec.valueForm)) issues.push('invalid valueForm');
  const definition = SPEC_DEFINITIONS[key];
  if (definition && spec.unit !== definition.unit) issues.push(`expected unit ${definition.unit}`);
  if (spec.sourceId !== null && !product.sources?.some(s => s && s.id === spec.sourceId)) issues.push('unresolved source reference');
  if (spec.additionalSourceIds !== undefined && (!Array.isArray(spec.additionalSourceIds)
    || new Set(spec.additionalSourceIds).size !== spec.additionalSourceIds.length
    || spec.additionalSourceIds.some(id => typeof id !== 'string' || id === spec.sourceId || !product.sources.some(s => s && s.id === id)))) issues.push('invalid additional source references');
  if (spec.status !== 'available') {
    if (spec.value !== null || !text(spec.rationale)) issues.push('unavailable value must be null with rationale');
    return issues;
  }
  if (!spec.sourceId) issues.push('available value needs source');
  const source = product.sources?.find(s => s && s.id === spec.sourceId);
  if (source) issues.push(...sourceIssues(source));
  const value = spec.value;
  if (value === null || (!text(value) && typeof value !== 'number' && !Array.isArray(value))) issues.push('invalid available value');
  if (definition?.type === 'text' && !text(value)) issues.push('expected nonempty text');
  if (definition?.type === 'number' && typeof value !== 'number' && !Array.isArray(value)) issues.push('expected numeric value');
  const numbers = Array.isArray(value) ? value : typeof value === 'number' ? [value] : [];
  // Signed coefficients, Celsius and signed absolute limits are valid source facts.
  // Known physical magnitudes retain explicit domains. Unknown signed quantities remain finite.
  const physicalMagnitudeUnit = ['kg', 'g', 'm', 'mm', 'm²', 'Wh', 'Ah', 'count', 'byte', 'Hz', 's', 'cycles', 'USD'].includes(spec.unit);
  if (numbers.some(v => typeof v !== 'number' || !Number.isFinite(v)
    || ((definition?.nonnegative ?? physicalMagnitudeUnit) && v < 0)
    || (definition?.positive && v <= 0) || ((definition?.integer || ['count', 'byte'].includes(spec.unit)) && !Number.isSafeInteger(v))
    || (definition?.fraction && (v <= 0 || v > 1)))) issues.push('invalid numerical domain');
  if (Array.isArray(value)) {
    const form = spec.valueForm ?? legacyArrayForm(product, key);
    if (!value.length || !form || form === 'scalar') issues.push('array requires explicit valueForm');
    if (form === 'interval' && (value.length !== 2 || value[0] > value[1])) issues.push('invalid interval');
    if (form === 'min-typ-max' && (value.length !== 3 || value[0] > value[1] || value[1] > value[2])) issues.push('invalid min/typ/max tuple');
    if (form === 'set' && new Set(value).size !== value.length) issues.push('duplicate set values');
  } else if (spec.valueForm && spec.valueForm !== 'scalar') issues.push('non-array cannot have array valueForm');
  return issues;
}
export function validateCatalog(catalog: Catalog): string[] {
  const issues: string[] = [];
  if (!text(catalog?.revision)) issues.push('catalog revision required');
  if (!Array.isArray(catalog?.products) || !catalog.products.length || catalog.products.length > PRODUCT_LIMIT) return [...issues, `catalog requires 1..${PRODUCT_LIMIT} products`];
  const ids = new Set<string>(); const sources = new Map<string, string>();
  for (const p of catalog.products) {
    if (!p || typeof p !== 'object') { issues.push('invalid product object'); continue; }
    const add = (message: string) => issues.push(`${p.id}: ${message}`);
    for (const key of ['id', 'revision', 'manufacturer', 'name', 'partNumber', 'description', 'accountingBoundary'] as const) if (!text(p[key])) add(`${key} required`);
    if (ids.has(p.id)) add('duplicate product ID'); ids.add(p.id);
    if (!['cell', 'panel', 'pack', 'board', 'component', 'assembly', 'software'].includes(p.level)) add('invalid product level');
    if (p.catalogUse !== undefined && !['comparison-option', 'reference-only'].includes(p.catalogUse)) add('invalid catalog use');
    if (!Array.isArray(p.roles) || !p.roles.length || new Set(p.roles).size !== p.roles.length || p.roles.some(r => !ROLES.includes(r))) { add('invalid roles'); continue; }
    for (const key of ['supportedConfigurations', 'caveats'] as const) if (!Array.isArray(p[key]) || p[key].some(v => !text(v)) || (key === 'supportedConfigurations' && !p[key].length)) add(`invalid ${key}`);
    if (!Array.isArray(p.sources) || !p.sources.length) { add('sources required'); continue; }
    const local = new Set<string>();
    for (const source of p.sources) {
      sourceIssues(source).forEach(add);
      if (!source || typeof source !== 'object') continue;
      if (local.has(source.id)) add(`duplicate source ${source.id}`); local.add(source.id);
      const identity = JSON.stringify(Object.entries(source).sort(([a], [b]) => a.localeCompare(b)));
      if (sources.has(source.id) && sources.get(source.id) !== identity) add(`source ID collision ${source.id}`);
      sources.set(source.id, identity);
    }
    if (!p.specs || typeof p.specs !== 'object' || Array.isArray(p.specs)) { add('specs object required'); continue; }
    for (const [key, spec] of Object.entries(p.specs)) specificationIssues(p, key, spec).forEach(message => add(`${key}: ${message}`));
    const num = (key: string) => p.specs[key]?.status === 'available' && typeof p.specs[key].value === 'number' ? p.specs[key].value as number : undefined;
    for (const [lo, hi] of [['voltageMinV', 'voltageNominalV'], ['voltageNominalV', 'voltageMaxV'], ['inputMinV', 'inputMaxV'], ['distributionSupplyMinV', 'distributionSupplyMaxV'], ['processorSupplyMinV', 'processorSupplyMaxV'], ['chargeTemperatureMinK', 'chargeTemperatureMaxK'], ['dischargeTemperatureMinK', 'dischargeTemperatureMaxK']]) if (num(lo) !== undefined && num(hi) !== undefined && num(lo)! > num(hi)!) add(`${lo} exceeds ${hi}`);
    if (p.specs.priceUsd?.status === 'available' && !/date|quote|\d{4}/i.test(p.specs.priceUsd.conditions)) add('price requires dated procurement conditions');
    // Reviewed snapshot regressions are revision-scoped, never universal supplier constraints.
    if (typeof p.revision === 'string' && p.revision.startsWith('catalog-record-1;')) {
      if (p.id === 'azur-3g30c-advanced-81780' && Math.abs((num('powerEolW') ?? 0) - 2.15118) > 1e-10) add('AZUR bare-cell endpoint changed without record revision');
      if (p.id === 'isis-iceps2-type-a' && (p.specs.energyWh?.status !== 'missing' || num('inputMaxV') !== 7.5 || num('absoluteInputMaxV') !== 15)) add('ICEPS2 unresolved energy/tracking/absolute snapshot changed without record revision');
      if (p.id === 'gomspace-p80-config1' && (p.roles.includes('battery') || num('massKg') !== .3608)) add('P80 configuration-1 battery/mass boundary changed without record revision');
    }
    if (p.roles.includes('solar')) for (const suffix of ['Bol', 'Eol']) {
      const v = num(`vmp${suffix}V`), a = num(`imp${suffix}A`), w = num(`power${suffix}W`);
      if (v !== undefined && a !== undefined && w !== undefined && p.specs[`vmp${suffix}V`].conditions === p.specs[`imp${suffix}A`].conditions) {
        const tolerance = p.id === 'cesi-ctj30-26p5' ? .02 : .0000000001;
        if (Math.abs(w - v * a) > Math.max(1e-12, w * tolerance)) add(`incoherent ${suffix} MPP (retain rounded source columns with reviewed rationale)`);
      }
      if (suffix === 'Bol' && ((v !== undefined && num('vocV') !== undefined && num('vocV')! < v) || (a !== undefined && num('iscA') !== undefined && num('iscA')! < a))) add('incoherent open/short circuit ratings');
    }
  }
  return issues;
}
