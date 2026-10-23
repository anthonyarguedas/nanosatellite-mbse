import { BatteryCharging, Boxes, ChevronRight, CircuitBoard, Code2, Cpu, Sun, Workflow, Zap } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { Catalog, NodeId, NodeStatus, Product, Role, Workspace } from '../types';
import { allocationGroups, ROLE_NODES, roleValue, savedPrefix } from './design-canvas-model';
import { ROLE_NAMES, ROLES } from './ui';

const ICONS: Record<Role, LucideIcon> = { solar: Sun, battery: BatteryCharging, conditioning: Zap, distribution: Workflow, processor: Cpu, software: Code2 };

/** Six logical groups. Shared usage references are accounting, never electrical connections. */
export function Architecture({ workspace, statuses, catalog, highlighted, onRole, onKiCad, onPreview, onAccounting }: {
  workspace: Workspace; statuses: Record<NodeId, NodeStatus>; catalog: Catalog; highlighted: readonly Role[];
  onRole: (role: Role) => void; onInspect: (product: Product) => void; onKiCad: () => void; onAccounting?: () => void; onPreview: (roles: Role[] | null) => void;
}) {
  const groups = allocationGroups(workspace, catalog);
  return <section className="eps-composition" aria-labelledby="eps-composition-title">
    <header className="composition-header"><h2 id="eps-composition-title"><Boxes size={15} />EPS logical composition <small>6 groups</small></h2>
      <button className="canvas-text-action" data-action="kicad" onClick={onKiCad}><CircuitBoard size={14} />KiCad<ChevronRight size={12} /></button></header>
    <div className="composition-roles">{ROLES.map(role => {
      const Icon = ICONS[role], group = groups.find(item => item.roles.includes(role));
      const historical = savedPrefix(statuses[ROLE_NODES[role]], (role === 'solar' && Boolean(workspace.analysis.solar)) || (role === 'battery' && Boolean(workspace.analysis.battery)));
      return <button key={role} className={`composition-role ${highlighted.includes(role) ? 'linked' : ''}`} data-role={role} data-linked={highlighted.includes(role) || undefined}
        aria-label={`Inspect ${ROLE_NAMES[role]}. ${historical}${roleValue(role, workspace)}. ${group ? `${group.ref}: ${group.product?.name ?? group.id}${group.quantity !== null ? `, concept count ${group.quantity}` : ', count unrecorded'}` : 'Not allocated'}`}
        title={`${ROLE_NAMES[role]} · ${historical}${roleValue(role, workspace)}${group ? `\n${group.product?.name ?? group.id}` : '\nNot allocated'}`}
        onClick={() => onRole(role)} onPointerEnter={() => onPreview(group?.roles ?? [role])} onPointerLeave={() => onPreview(null)}>
        <Icon size={17} strokeWidth={1.6} /><span><strong>{ROLE_NAMES[role]}</strong><small>{group ? <><span className="allocation-ref">{group.ref}</span>{group.quantity !== null ? ` ×${group.quantity}` : ' count unknown'}{group.roles.length > 1 ? ' · shared usage' : ''}</> : role === 'software' ? 'Software not allocated' : 'Product not allocated'}</small></span>
      </button>;
    })}</div>
    <footer className="composition-footer"><span>Reference [1] = one category, not one installed item.</span><button className="canvas-text-action" data-action="accounting" onClick={onAccounting}>Product usages & accounting <span>{groups.length}</span><ChevronRight size={12} /></button></footer>
  </section>;
}

export function AllocationAccounting({ workspace, catalog, onInspect }: { workspace: Workspace; catalog: Catalog; onInspect: (product: Product) => void }) {
  const groups = allocationGroups(workspace, catalog);
  return <div className="allocation-accounting"><p className="body-copy">Six logical roles can share one product usage. Screening quantities are sizing counts, not established installation counts. Confirmed concept counts stay fixed when scenarios change.</p>
    <div className="allocation-list">{groups.map(group => <div key={group.id}><span className="allocation-ref">{group.ref}</span><div>
      <strong>{group.product?.name ?? group.id}{group.quantity !== null ? ` · ×${group.quantity}` : ' · count unrecorded'}</strong><p>{group.roles.map(role => ROLE_NAMES[role]).join(' · ')}</p>
      {group.receipt && <p>{group.receipt.rationale}</p>}<small>{group.product?.level === 'software' ? 'Software record. Physical resources belong to its host.' : group.roles.length > 1 ? 'One physical usage shared across these logical roles.' : 'One product usage in the allocation model.'}</small>
      {group.product && <button className="text-button" data-focus-key={`accounting-${group.id}`} onClick={() => onInspect(group.product!)}>Inspect sources & allocation<ChevronRight size={13} /></button>}
    </div></div>)}</div>
    {!groups.length && <p className="body-copy">No products allocated.</p>}
    <p className="body-copy">Installed arrangements, harnesses, packaging and actual wiring need their own design evidence. No physical resource total is inferred from role coverage.</p>
  </div>;
}
