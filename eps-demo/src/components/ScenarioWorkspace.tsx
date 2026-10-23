import { ArrowRight, Plus } from 'lucide-react';
import type { NodeId, Scenario } from '../types';
import { BIRDS4_SOURCE } from '../data/scenarios';
import { ScenarioEditor } from './ScenarioEditor';
import { Notice, ScenarioSwitcher, StatusBadge, unit } from './ui';
import type { WorkspaceController } from './ui';

export function ScenarioWorkspace({ api, onNode }: { api: WorkspaceController; onNode: (id: NodeId) => void }) {
  const createScenario = () => {
    const scenario: Scenario = {
      id: `scenario-${crypto.randomUUID()}`, name: 'New operating case', kind: 'nominal',
      description: 'An engineer-authored mission operating case.', revision: 1, illuminationFactor: 1,
      initialEnergyFraction: 0.8, minimumEnergyFraction: 0.2, durationOrbits: 1, loads: [],
      provenance: 'Engineer-authored scenario. Initial defaults are editable study assumptions, not mission requirements.',
    };
    api.updateScenario(scenario); api.setActiveScenario(scenario.id);
  };
  return <div className="scenario-context-workspace">
    <header className="scenario-context-heading"><ScenarioSwitcher api={api} compact /><StatusBadge status={api.statuses.scenarios} /><button className="button secondary" data-action="new-scenario" onClick={createScenario}><Plus size={14} />New scenario</button></header>
    <p className="context-basis-note">{api.activeScenario?.id.startsWith('birds4-') ? <>BIRDS-4 activities are sourced. Powers, rails, schedules and energy criteria are editable study assumptions. <a href={BIRDS4_SOURCE.url} target="_blank" rel="noreferrer">Mission source §§3–5.6 ↗</a></> : 'Engineer-authored operating case. Powers, schedules and energy criteria are explicit assumptions.'}</p>
    {api.statuses.orbit !== 'complete' && <Notice kind="warning" title="Orbit timing is not current">The schedule remains editable in orbit fractions. Minute and eclipse timing is withheld until the orbit is current.<button className="text-button" onClick={() => onNode('orbit')}>Inspect orbit<ArrowRight size={12} /></button></Notice>}
    <p className="context-basis-note">The timeline shows spacecraft loads. Sizing and simulation also include the additional EPS baseline ({unit(api.workspace.inputs.topology.idlePowerW, 'W', 2)}) once. Its operating-state and heater assumptions need review.</p>
    {api.activeScenario ? <ScenarioEditor scenario={api.activeScenario} orbit={api.statuses.orbit === 'complete' ? api.workspace.analysis.orbit : undefined} onChange={api.updateScenario} /> : <div className="large-empty"><h2>No operating case yet</h2><p>Create a case, add loads and schedule their active windows.</p><button className="button primary" onClick={createScenario}>Create first scenario</button></div>}
    <p className="context-basis-note">One selected scenario is evaluated at a time. Editing it marks dependent calculations out of date. Stored energy is not charge-based state of charge.</p>
  </div>;
}
