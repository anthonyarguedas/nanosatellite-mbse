import { ArrowRight, GitBranch } from 'lucide-react';
import type { DesignInputs, Role } from '../types';
import { variationPoints, type VariationId } from './design-canvas-model';

type Topology = DesignInputs['topology'];
const ROLE_LABELS: Record<Role, string> = { solar: 'Solar', battery: 'Battery', conditioning: 'Converters', distribution: 'Switches', processor: 'Processor', software: 'Software' };

export function TopologyChoices({ topology, onChange, onOpen, onPreview, selected }: {
  topology: Topology; onChange?: (patch: Partial<Topology>) => void;
  onOpen?: (id: VariationId) => void; onPreview?: (roles: Role[] | null) => void; selected?: VariationId;
}) {
  const points = variationPoints(topology);
  if (onChange) return <div className="topology-editor" aria-label="Topology alternatives">
    <fieldset className="topology-fieldset" data-topology-axis="conditioning" tabIndex={-1}><legend>Power conditioning</legend>
      {(['DET', 'MPPT'] as const).map(value => <label key={value}><input type="radio" name="conditioning" value={value} checked={topology.conditioning === value} onChange={() => onChange({ conditioning: value })} /><strong>{value}</strong><span>{value === 'MPPT' ? 'Maximum power point tracking' : 'Direct energy transfer'}</span></label>)}
    </fieldset>
    {topology.conditioning === 'DET' && <p className="topology-warning" role="note">DET is an architecture alternative, but this demo cannot propagate its energy without a characterized array I–V operating point.</p>}
    <fieldset className="topology-fieldset" data-topology-axis="transfer" tabIndex={-1}><legend>Energy transfer</legend>
      {(['centralized', 'distributed'] as const).map(value => <label key={value}><input type="radio" name="transfer" value={value} checked={topology.distribution === value} onChange={() => onChange({ distribution: value })} /><strong>{value === 'centralized' ? 'Centralized' : 'Distributed'}</strong></label>)}
    </fieldset>
    <fieldset className="topology-fieldset" data-topology-axis="bus" tabIndex={-1}><legend>DC bus regulation intent</legend>
      {(['unregulated', 'regulated'] as const).map(value => <label key={value}><input type="radio" name="bus" value={value} checked={topology.bus === value} onChange={() => onChange({ bus: value })} /><strong>{value === 'regulated' ? 'Regulated intent' : 'Unregulated intent'}</strong></label>)}
    </fieldset>
    <p className="body-copy">Regulated intent is unspecified: it is not proof of fully regulated rails. Partially versus fully regulated buses are not distinguished by the current model.</p>
    <div className="unrepresented-outputs" data-topology-axis="outputs" tabIndex={-1}><strong>Per-output distribution · not represented</strong><p>Direct bus supply and DC–DC converted outputs can coexist in the report. No per-rail selection, conversion envelope, or verified wiring is modeled here.</p><span>Direct bus</span><span>DC–DC converted</span></div>
  </div>;
  return <aside className="variation-points" aria-labelledby="variation-title">
    <header><GitBranch size={15} /><div><h3 id="variation-title">Topology intent</h3><p>Design associations, not power wiring</p></div></header>
    <div className="variation-list">{points.map(point => <button className={`variation-point ${point.id === 'outputs' ? 'unrepresented' : ''} ${selected === point.id ? 'is-selected' : ''}`} key={point.id} data-variation={point.id}
      aria-pressed={selected === point.id} onClick={() => onOpen?.(point.id)} onPointerEnter={() => onPreview?.(point.roles)} onPointerLeave={() => onPreview?.(null)}
      aria-label={`${point.title}. ${point.options.map(option => `${option.label}${option.selected ? ', selected intent' : ''}${!option.represented ? ', not represented' : ''}`).join('; ')}. Inspect topology.`}>
      <span className="variation-label">{point.title}<ArrowRight size={12} /></span>
      <strong>{point.options.find(option => option.selected)?.label ?? 'Reference only'}</strong>
      <span className="variation-association">{point.id === 'outputs' ? 'Direct + converted · not represented' : point.id === 'bus' && topology.bus === 'regulated' ? 'Partial / full detail not represented' : point.id === 'conditioning' && topology.conditioning === 'DET' ? 'Energy propagation unsupported' : point.roles.map(role => ROLE_LABELS[role]).join(' + ')}</span>
    </button>)}</div>
  </aside>;
}
