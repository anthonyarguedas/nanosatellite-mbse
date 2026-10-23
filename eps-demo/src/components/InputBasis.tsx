import type { Catalog, NodeId, NumericInputPath, Workspace } from '../types';
import { number } from './ui';

export const LABELS: Record<NumericInputPath, [string, string]> = {
  'mission.altitudeKm': ['Reference altitude', 'km'],
  'mission.lifetimeYears': ['Design lifetime', 'years'],
  'solar.sunlightEfficiency': ['Sunlight sizing efficiency', ''],
  'solar.eclipseEfficiency': ['Eclipse sizing efficiency', ''],
  'solar.cellEolV': ['Cell EOL MPP voltage', 'V'],
  'solar.cellEolA': ['Cell EOL MPP current', 'A'],
  'solar.installedPowerW': ['Available EOL source power', 'W'],
  'battery.dod': ['Preliminary DoD', ''],
  'battery.margin': ['Sizing margin', ''],
  'battery.capacityWh': ['BOL pack energy', 'Wh'],
  'battery.retainedEnergy': ['Retained energy factor', ''],
  'battery.chargeEfficiency': ['Charging energy efficiency', ''],
  'battery.dischargeEfficiency': ['Discharging energy efficiency', ''],
  'battery.maxChargeW': ['Terminal charge power bound', 'W'],
  'battery.maxDischargeW': ['Terminal discharge power bound', 'W'],
  'topology.efficiency': ['Conditioning efficiency', ''],
  'topology.idlePowerW': ['Additional EPS baseline', 'W'],
  'topology.massAllocationKg': ['EPS mass allocation', 'kg'],
};

export function relevant(node: NodeId, path: NumericInputPath): boolean {
  if (node === 'assessment' || node === 'simulation') return true;
  if (node === 'budget') return path === 'topology.idlePowerW';
  if (node === 'candidates') return path.startsWith('solar.') || path.startsWith('battery.');
  return path.startsWith(`${node}.`);
}

/** Authored provenance stays separate from the immutable manufacturer catalog. */
export function InputBasis({ workspace, catalog, node }: { workspace: Workspace; catalog: Catalog; node: NodeId }) {
  if (node === 'orbit' || node === 'scenarios') return null;
  const records = workspace.provenance?.filter(record => relevant(node, record.parameter)) ?? [];
  const sources = [...new Map([...catalog.products.flatMap(product => product.sources), ...workspace.inputs.mission.orbitSuggestion?.sources ?? []].map(source => [source.id, source])).values()];
  return <details className="disclosure input-basis" data-testid="input-basis">
    <summary>Input basis & assumptions</summary>
    <p className="body-copy">Study inputs support the declared calculation. Sourced typical values retain their conditions and establish no guaranteed operating bound. Manual inputs remain engineering assumptions.</p>
    {records.length ? records.map(record => <article className="input-basis-record" key={record.parameter} data-input-parameter={record.parameter} data-basis-kind={record.kind}>
      <header><strong>{LABELS[record.parameter][0]}: {number(record.value, 4)} {LABELS[record.parameter][1]}</strong><span className="assumption-label">{record.kind === 'catalog-value' ? 'Catalog value' : 'Study assumption'}</span></header>
      <p>{record.rationale}</p><small>{record.conditions}</small>
      {sources.filter(source => record.sourceIds.includes(source.id)).map(source => <a href={source.url} target="_blank" rel="noreferrer" key={source.id}>{source.title} · {source.revision} · {source.location}</a>)}
    </article>) : <p className="body-copy">This design has no recorded provenance for these inputs. Review their basis before using the results. No source or product rating is inferred from a legacy selection.</p>}
  </details>;
}
