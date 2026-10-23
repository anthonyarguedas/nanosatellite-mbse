import type { WorkspaceController } from './ui';
import type { FlowTask } from './flow-tasks';
import { WorkbenchGraph } from './WorkbenchGraph';
import { CSRM_SUBSYSTEMS } from './design-canvas-model';
import { BIRDS4_EXAMPLE_BASIS } from '../data/birds4';

export function ReferenceContext() {
  return <div><p>Static reference view. Mission / Space Segment / CubeSat / EPS.</p><p>CubeSat · nine subsystem categories [1] each.</p><ul>{CSRM_SUBSYSTEMS.map(name=><li key={name}>{name}</li>)}</ul><p>Ground Segment [1]. This demo models one spacecraft EPS and one circular reference orbit. Logical categories establish no installed quantities or electrical connections.</p><a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CSRM attribution · CC BY 4.0</a></div>;
}
export function StudyBasis() {
  return <div><p>{BIRDS4_EXAMPLE_BASIS.limits}</p><ul>{BIRDS4_EXAMPLE_BASIS.missionFacts.map(f=><li key={f}>{f}</li>)}</ul><a href={BIRDS4_EXAMPLE_BASIS.source.url}>{BIRDS4_EXAMPLE_BASIS.source.title}</a></div>;
}
export function DesignCanvas({api,tasks,selected,onSelect,onHome}:{api:WorkspaceController;tasks:FlowTask[];selected:string|null;onSelect:(task:FlowTask)=>void;onHome:()=>void}) {
  return <div className="design-canvas" data-testid="design-canvas"><WorkbenchGraph workspace={api.workspace} statuses={api.statuses} tasks={tasks} selected={selected} onSelect={onSelect} onHome={onHome}/></div>;
}
