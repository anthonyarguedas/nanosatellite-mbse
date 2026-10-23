import type { Catalog, Product, Role } from '../types.ts';
import { COMPARISON_SCOPE, PROFILE_REVISION, ROLE_PROFILES, ROLES } from './profiles.ts';
import type { CoverageRule } from './profiles.ts';
import { specificationIssues, validateCatalog } from './validation.ts';

export interface CoverageItem { id: string; label: string; covered: boolean; alternatives: readonly (readonly string[])[]; issues: string[] }
export interface ProductCoverage {
  productId: string; role: Role; profileRevision: string; scope: string;
  identityIssues: string[]; core: CoverageItem[]; richer: CoverageItem[];
  coreCovered: number; coreRequired: number; comparisonCovered: boolean;
}
/** A reviewed function classification, not an inferred PV interface or converter feasibility result. */
export function isLoadConverter(p: Product): boolean {
  const spec = p.specs.conditioningApplicability;
  const source = p.sources.find(source => source.id === spec?.sourceId);
  const mode = String(p.specs.conditioningMode?.value ?? '').replace(/\b(?:no|not)\s+(?:MPPT|DET|(?:battery\s+)?charg(?:er|ing))\b/gi, '');
  return spec?.status === 'available' && spec.value === 'load-converter'
    && Boolean(source?.publisher && source.kind && source.sha256)
    && !/\bMPPT\b|\bDET\b|\bcharger\b/i.test(mode)
    && specificationIssues(p, 'conditioningApplicability', spec).length === 0;
}
const normalized = (s: string) => s.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
/** Identity excludes display name, record ID and revision. Variants need distinct supplier ordering identities. */
export function optionIdentity(p: Product): string {
  const orderingIdentity = p.level === 'software' ? p.partNumber.replace(/(?<=.)[@#].*$/, '').replace(/\s+(?:release|version|v)\s*\d+(?:\.\d+)*(?:[-+][\w.-]+)?$/i, '') : p.partNumber;
  return `${normalized(p.manufacturer)}:${normalized(orderingIdentity)}`;
}
function evaluateRule(p: Product, rule: CoverageRule): CoverageItem {
  const choices = rule.anyOf.map(keys => {
    const issues = keys.flatMap(key => {
      const spec = p.specs[key];
      if (!spec || spec.status !== 'available') return [`${key}: ${spec?.status ?? 'missing record'}${spec?.rationale ? ` (${spec.rationale})` : ''}`];
      const issues = specificationIssues(p, key, spec).map(issue => `${key}: ${issue}`);
      const source = p.sources.find(source => source.id === spec.sourceId);
      if (!source?.publisher || !source.kind || !source.sha256) issues.push(`${key}: reviewed publisher, source kind and content hash required for comparison coverage`);
      return issues;
    });
    if (!issues.length && rule.condition) {
      const conditions = keys.map(key => p.specs[key].conditions).join(' ');
      const original = keys.map(key => `${p.specs[key].original} ${p.specs[key].value}`).join(' ');
      if (rule.condition.startsWith('solar') && (!/AM0|AM1[.,]5|spectrum/i.test(conditions) || !/\d[\d.]*\s*(?:W\s*\/\s*m|mW\s*\/\s*cm)/i.test(conditions) || !/[-+]?\d[\d.]*\s*(?:°\s*C|K\b|deg)/i.test(conditions))) issues.push(`${rule.id}: irradiance/spectrum and temperature conditions required`);
      if (rule.condition === 'battery-energy' && !/\d[\d.]*\s*V\b/i.test(`${conditions} ${original}`)) issues.push('energyWh: characterized voltage window required');
      if (rule.condition === 'battery-current' && /trip|protection threshold|activation threshold/i.test(`${conditions} ${original}`)) issues.push(`${rule.id}: protection threshold is not a permissible current rating`);
      if (rule.condition === 'rails' && (!/\d[\d.]*\s*V\b/i.test(original) || !/\d[\d.]*\s*A\b/i.test(original))) issues.push('outputRails: rail voltage and continuous-current rows required');
      if (rule.condition === 'eps-services' && (!/EPS|power|battery/i.test(original) || !/monitor|telemetry|control|recovery/i.test(original))) issues.push('serviceDefinitions: implemented EPS service evidence required, not a generic OS/SDK');
      if (rule.condition === 'solar-eol' && !/fluence|radiation|electron|proton|end.of.life|EOL|degradation/i.test(conditions)) issues.push('eol: explicit degradation/radiation endpoint required');
      if (keys.includes('vmpEolV') && keys.includes('impEolA') && p.specs.vmpEolV.conditions !== p.specs.impEolA.conditions) issues.push('eol: MPP pair conditions differ');
    }
    return issues;
  });
  return { id: rule.id, label: rule.label, covered: choices.some(issues => !issues.length), alternatives: rule.anyOf,
    issues: choices.some(issues => !issues.length) ? [] : choices.flat() };
}
export function productCoverage(p: Product, role: Role): ProductCoverage {
  const identityIssues: string[] = [];
  for (const key of ['id', 'revision', 'manufacturer', 'partNumber', 'accountingBoundary'] as const) if (!p[key]?.trim()) identityIssues.push(`${key} missing`);
  if (!p.roles.includes(role)) identityIssues.push(`product does not declare ${role}`);
  if (p.catalogUse === 'reference-only') identityIssues.push('Published mission reference, not a selectable comparison option.');
  if (!p.supportedConfigurations.length) identityIssues.push('supported configuration missing');
  if (!p.sources.length) identityIssues.push('source identity missing');
  const applicable = (rule: CoverageRule) => (!rule.branch || (rule.branch === 'load-converter') === isLoadConverter(p)) && (!rule.levels || rule.levels.includes(p.level)) && (!rule.when || `${p.specs[rule.when.key]?.value ?? ''} ${rule.when.orKey ? p.specs[rule.when.orKey]?.value ?? '' : ''}`.toLowerCase().includes(rule.when.contains));
  const core = ROLE_PROFILES[role].core.filter(applicable).map(rule => evaluateRule(p, rule));
  const richer = ROLE_PROFILES[role].richer.filter(applicable).map(rule => evaluateRule(p, rule));
  const coreCovered = core.filter(item => item.covered).length;
  return { productId: p.id, role, profileRevision: PROFILE_REVISION, scope: COMPARISON_SCOPE, identityIssues, core, richer,
    coreCovered, coreRequired: core.length, comparisonCovered: !identityIssues.length && coreCovered === core.length };
}
export function catalogCoverage(catalog: Catalog, target = 3) {
  if (!Number.isSafeInteger(target) || target < 1) throw new Error('Coverage target must be a positive integer.');
  return { profileRevision: PROFILE_REVISION, scope: COMPARISON_SCOPE, integrityIssues: validateCatalog(catalog), target,
    roles: ROLES.map(role => {
      const products = catalog.products.filter(p => p.roles.includes(role)).map(p => ({ optionIdentity: optionIdentity(p), ...productCoverage(p, role) }));
      const identities = new Set(products.filter(p => p.comparisonCovered).map(p => p.optionIdentity));
      return { role, records: products.length, distinctOptions: new Set(products.filter(p => !p.identityIssues.includes('Published mission reference, not a selectable comparison option.')).map(p => p.optionIdentity)).size, coveredOptions: identities.size, deficit: Math.max(0, target - identities.size), products };
    }) };
}
