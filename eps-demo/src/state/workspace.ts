import { useCallback, useEffect, useMemo, useReducer } from 'react';
import { catalog } from '../data/catalog';
import { missingForNodes, nodeStatuses } from '../workflow';
import type { DesignInputs, NodeId, Role, Scenario, Workspace } from '../types';
import { activeScenario, applyProduct, changeInputs, createExampleWorkspace, createWorkspace, emptyInputs, evaluateNode, evaluateReady } from './model';
import { restoreWorkspace, serializeWorkspace } from './serialization';

const STORAGE_KEY = 'orbitwork.eps-demo.v1';
interface State { workspace: Workspace; error: string | null }
type Action = { type: 'change'; apply: (workspace: Workspace) => Workspace } | { type: 'replace'; workspace: Workspace } | { type: 'error'; error: string | null };
function reducer(state: State, action: Action): State {
  if (action.type === 'error') return { ...state, error: action.error };
  if (action.type === 'replace') return { workspace: action.workspace, error: null };
  try { return { workspace: action.apply(state.workspace), error: null }; }
  catch (error) { return { ...state, error: error instanceof Error ? error.message : 'The calculation could not be completed.' }; }
}
function initialize(): State {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const workspace = restoreWorkspace(JSON.parse(saved), catalog, true);
      return { workspace, error: null };
    }
  } catch {
    return { workspace: createExampleWorkspace(), error: 'The saved local design could not be restored. The example was loaded. Your other files are unchanged.' };
  }
  return { workspace: createExampleWorkspace(), error: null };
}

/** One revisioned local design. Every mutation invalidates the transitive dependency closure. */
export function useWorkspace() {
  const [state, dispatch] = useReducer(reducer, undefined, initialize);
  const workspace = state.workspace;
  const statuses = useMemo(() => nodeStatuses(workspace), [workspace]);
  const missing = useMemo(() => missingForNodes(workspace, statuses), [workspace, statuses]);
  const scenario = useMemo(() => activeScenario(workspace), [workspace]);
  useEffect(() => {
    try {
      // Persist the authored model. Results are recalculated after reload or JSON import.
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ schemaVersion: 1, inputs: workspace.inputs, selections: workspace.selections, allocations: workspace.allocations, provenance: workspace.provenance, catalogRevision: catalog.revision, catalogReview: workspace.catalogReview }));
    } catch {
      dispatch({ type: 'error', error: 'Local storage is unavailable or full. Keep working and export JSON to save this design.' });
    }
  }, [workspace.inputs, workspace.selections, workspace.allocations, workspace.provenance, workspace.catalogReview]);

  const runNode = useCallback((id: NodeId) => dispatch({ type: 'change', apply: current => evaluateNode(current, id) }), []);
  const runAll = useCallback(() => dispatch({ type: 'change', apply: evaluateReady }), []);
  const updateInputs = useCallback((_node: NodeId, updater: (inputs: DesignInputs) => DesignInputs) => dispatch({ type: 'change', apply: current => changeInputs(current, updater) }), []);
  const updateScenario = useCallback((next: Scenario) => dispatch({ type: 'change', apply: current => changeInputs(current, inputs => {
    const exists = inputs.scenarios.some(item => item.id === next.id);
    const revision = (inputs.scenarios.find(item => item.id === next.id)?.revision ?? 0) + 1;
    const scenario = { ...structuredClone(next), revision };
    inputs.scenarios = exists ? inputs.scenarios.map(item => item.id === scenario.id ? scenario : item) : [...inputs.scenarios, scenario];
    if (!inputs.activeScenarioId) inputs.activeScenarioId = scenario.id;
    return inputs;
  }) }), []);
  const setActiveScenario = useCallback((id: string) => dispatch({ type: 'change', apply: current => changeInputs(current, inputs => {
    if (!inputs.scenarios.some(item => item.id === id)) throw new Error('Choose an existing operating scenario.');
    return { ...inputs, activeScenarioId: id };
  }) }), []);
  const selectProduct = useCallback((role: Role, productId: string) => dispatch({ type: 'change', apply: current => applyProduct(current, role, productId) }), []);
  const loadExample = useCallback(() => dispatch({ type: 'replace', workspace: createExampleWorkspace() }), []);
  const reset = useCallback(() => dispatch({ type: 'replace', workspace: createWorkspace(emptyInputs()) }), []);
  const clearError = useCallback(() => dispatch({ type: 'error', error: null }), []);
  const download = useCallback(() => {
    const data = {
      ...JSON.parse(serializeWorkspace(workspace, catalog.revision)),
      selectedCatalogEntries: [...new Set(Object.values(workspace.selections))].map(id => catalog.products.find(item => item.id === id)),
      equationSource: 'final_report/design-proposal.tex, Orbit Requirements and Power Budget; EPS Component Selection; eps-requirements.tex',
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `orbitwork-${workspace.inputs.mission.name.replace(/[^a-zA-Z0-9]+/g, '-').slice(0, 60).replace(/-+$/, '').toLowerCase() || 'design'}.json`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }, [workspace]);
  const restore = useCallback(async (file: File) => {
    try {
      if (file.size > 2_000_000) throw new Error('Design files must be smaller than 2 MB.');
      dispatch({ type: 'replace', workspace: restoreWorkspace(JSON.parse(await file.text())) });
    } catch (error) {
      dispatch({ type: 'error', error: error instanceof Error ? error.message : 'The design file could not be read.' });
    }
  }, []);

  return { workspace, statuses, missing, activeScenario: scenario, runNode, runAll, updateInputs, updateScenario, setActiveScenario, selectProduct, loadExample, reset, download, restore, error: state.error, clearError };
}

export type WorkspaceStore = ReturnType<typeof useWorkspace>;
