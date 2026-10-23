import type { Catalog, DesignInputs, NumericInputPath, ParameterProvenance, Product, Role } from '../types';
import { numericEvidence } from '../engine/catalog';

export const NUMERIC_INPUT_PATHS: NumericInputPath[] = [
  'mission.altitudeKm', 'mission.lifetimeYears',
  'solar.sunlightEfficiency', 'solar.eclipseEfficiency', 'solar.cellEolV', 'solar.cellEolA', 'solar.installedPowerW',
  'battery.dod', 'battery.margin', 'battery.capacityWh', 'battery.retainedEnergy', 'battery.chargeEfficiency', 'battery.dischargeEfficiency', 'battery.maxChargeW', 'battery.maxDischargeW',
  'topology.efficiency', 'topology.idlePowerW', 'topology.massAllocationKg',
];
const CATALOG_PARAMETERS: Partial<Record<NumericInputPath, { key: string; role: Role }>> = {
  'solar.cellEolV': { key: 'vmpEolV', role: 'solar' },
  'solar.cellEolA': { key: 'impEolA', role: 'solar' },
  'battery.capacityWh': { key: 'energyWh', role: 'battery' },
};

export function numericInput(inputs: DesignInputs, path: NumericInputPath): number | null {
  const [group, field] = path.split('.') as [keyof Pick<DesignInputs, 'mission' | 'solar' | 'battery' | 'topology'>, string];
  return (inputs[group] as unknown as Record<string, number | null>)[field];
}
export function setNumericInput(inputs: DesignInputs, path: NumericInputPath, value: number | null): void {
  const [group, field] = path.split('.') as [keyof Pick<DesignInputs, 'mission' | 'solar' | 'battery' | 'topology'>, string];
  (inputs[group] as unknown as Record<string, number | null>)[field] = value;
}
export function manualProvenance(parameter: NumericInputPath, value: number): ParameterProvenance {
  return { parameter, value, kind: 'engineering-assumption', rationale: 'Manually authored numerical input. No manufacturer characterization is claimed.', conditions: 'Engineer must establish applicability to the selected architecture and scenario.', sourceIds: [] };
}
export function catalogProvenance(product: Product, parameter: NumericInputPath): ParameterProvenance | undefined {
  const mapping = CATALOG_PARAMETERS[parameter];
  if (!mapping) return undefined;
  const evidence = numericEvidence(product, mapping.key);
  if (evidence.value === undefined) return undefined;
  return { parameter, value: evidence.value, kind: 'catalog-value', productId: product.id, productRevision: product.revision,
    rationale: `Transferred ${mapping.key} (${evidence.spec!.meaning}) at its cited conditions. Typical/nominal values establish no guaranteed bound.${product.level === 'cell' && parameter === 'battery.capacityWh' ? ' One-cell reference only. This is not a characterized multi-cell pack or an included protection/assembly rating.' : ''}`,
    conditions: evidence.spec!.conditions, sourceIds: evidence.sourceIds };
}

export function provenanceSourceIds(inputs: DesignInputs, catalog: Catalog): Set<string> {
  return new Set([
    ...catalog.products.flatMap(product => product.sources),
    ...inputs.mission.orbitSuggestion?.sources ?? [],
  ].map(source => source.id));
}

export function provenanceIssues(inputs: DesignInputs, provenance: ParameterProvenance[], selections: Partial<Record<Role, string>>, catalog: Catalog): string[] {
  const issues: string[] = [];
  const sourceIds = provenanceSourceIds(inputs, catalog);
  const seen = new Set<string>();
  for (const record of provenance) {
    if (!NUMERIC_INPUT_PATHS.includes(record.parameter) || seen.has(record.parameter)
      || !Number.isFinite(record.value) || numericInput(inputs, record.parameter) !== record.value) issues.push(`Parameter provenance does not match the unique authored input ${record.parameter}.`);
    seen.add(record.parameter);
    if (!record.rationale.trim() || !record.conditions.trim()) issues.push(`${record.parameter}: provenance requires rationale and conditions.`);
    if (record.sourceIds.some(id => !sourceIds.has(id))) issues.push(`${record.parameter}: provenance source references are unresolved in the catalog and accepted mission evidence.`);
    if (record.productId || record.productRevision) {
      const subject = catalog.products.find(item => item.id === record.productId);
      if (!subject || subject.revision !== record.productRevision || !Object.values(selections).includes(subject.id)) {
        issues.push(`${record.parameter}: product-bound provenance does not identify a current selected subject.`);
      }
    }
    if (record.kind === 'catalog-value') {
      const product = catalog.products.find(item => item.id === record.productId);
      const mapping = CATALOG_PARAMETERS[record.parameter];
      const evidence = product && mapping ? numericEvidence(product, mapping.key) : undefined;
      if (!product || !mapping || selections[mapping.role] !== product.id || product.revision !== record.productRevision
        || evidence?.value !== record.value || record.sourceIds.length !== evidence.sourceIds.length
        || record.sourceIds.some(id => !evidence.sourceIds.includes(id)) || record.conditions !== evidence.spec?.conditions) {
        issues.push(`${record.parameter}: catalog provenance does not match the selected product, rating, conditions and sources.`);
      }
    } else if (record.kind !== 'engineering-assumption') issues.push(`${record.parameter}: unknown provenance kind.`);
  }
  return issues;
}
