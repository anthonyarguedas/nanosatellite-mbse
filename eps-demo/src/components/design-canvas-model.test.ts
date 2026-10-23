import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { createExampleWorkspace, createWorkspace, emptyInputs } from '../state/model';
import { NODE_DEFINITIONS } from '../workflow';
import { ACTIVITY_GROUPS, ACTIVITY_ROLES, ACTIVITY_TITLES, activityEdges, activityPositions, activityValue, allocationGroups, CSRM_SUBSYSTEMS, ROLE_NODES, savedPrefix, selectionRoles, variationPoints } from './design-canvas-model';
import { ROLES } from './ui';

describe('graphical EPS presentation contract', () => {
  it('draws exactly the controller dependencies and optional evidence without inventing execution edges', () => {
    const edges = activityEdges();
    const expected = NODE_DEFINITIONS.flatMap(node => [
      ...node.dependencies.map(source => `${source}-${node.id}:dependency`),
      ...(node.evidenceDependencies ?? []).map(source => `${source}-${node.id}:evidence`),
    ]);
    expect(edges.map(edge => `${edge.id}:${edge.kind}`)).toEqual(expected);
    expect(edges.find(edge => edge.id === 'simulation-assessment')?.kind).toBe('evidence');
    expect(edges.some(edge => edge.source === 'assessment')).toBe(false);
    expect(edges.some(edge => edge.id === 'mission-scenarios')).toBe(false);
  });
  it('positions all ten activities distinctly in every responsive graph layout', () => {
    for (const layout of ['wide', 'compact', 'narrow'] as const) {
      const positions = activityPositions(layout);
      expect(Object.keys(positions).sort()).toEqual(NODE_DEFINITIONS.map(node => node.id).sort());
      expect(new Set(Object.values(positions).map(point => `${point.x},${point.y}`)).size).toBe(10);
    }
  });
  it('counts distinct retained products rather than matching logical roles', () => {
    const workspace = createExampleWorkspace();
    workspace.analysis.suggestions = [
      { productId: 'shared', role: 'conditioning', quantity: 1, outcome: 'incomplete', reason: '', checks: [], missing: [] },
      { productId: 'shared', role: 'distribution', quantity: 1, outcome: 'incomplete', reason: '', checks: [], missing: [] },
      { productId: 'rejected', role: 'solar', quantity: 1, outcome: 'rejected', reason: '', checks: [], missing: [] },
    ];
    expect(activityValue('candidates', workspace)).toBe('1 product, including incomplete');
  });
  it('prioritizes an explicit role or topology axis over broad activity associations', () => {
    const topology = createExampleWorkspace().inputs.topology;
    expect(selectionRoles({ node: 'topology', role: 'conditioning' }, topology)).toEqual(['conditioning']);
    expect(selectionRoles({ node: 'topology', variation: 'bus' }, topology)).toEqual(['battery', 'conditioning']);
    expect(selectionRoles({ node: null }, topology)).toEqual([]);
  });
  it('keeps every controller activity reachable once, without inventing lifecycle gates', () => {
    const shown = ACTIVITY_GROUPS.flatMap(group => group.nodes);
    expect(new Set(shown).size).toBe(NODE_DEFINITIONS.length);
    expect([...shown].sort()).toEqual(NODE_DEFINITIONS.map(node => node.id).sort());
    for (const id of shown) {
      expect(ACTIVITY_TITLES[id]).toBeTruthy();
      expect(ACTIVITY_ROLES[id].every(role => ROLES.includes(role))).toBe(true);
    }
    expect(ACTIVITY_GROUPS.find(group => group.nodes.includes('solar'))?.nodes).toContain('battery');
  });
  it('keeps all six roles and the nine-category reference context distinct', () => {
    expect(Object.keys(ROLE_NODES).sort()).toEqual([...ROLES].sort());
    expect(CSRM_SUBSYSTEMS).toHaveLength(9);
    expect(CSRM_SUBSYSTEMS.filter(name => name === 'Power (EPS)')).toHaveLength(1);
  });
  it('groups integrated board roles as one usage and never infers installation counts from screening', () => {
    const workspace = createWorkspace(emptyInputs());
    const board = catalog.products.find(product => product.roles.includes('conditioning') && product.roles.includes('distribution'))!;
    workspace.selections = { conditioning: board.id, distribution: board.id, processor: board.id };
    workspace.analysis.suggestions = [{ productId: board.id, role: 'conditioning', quantity: 99, outcome: 'incomplete', reason: 'Screen only', checks: [], missing: ['Installation evidence'] }];
    const groups = allocationGroups(workspace, catalog);
    expect(groups).toHaveLength(1);
    expect(groups[0].roles).toEqual(['conditioning', 'distribution', 'processor']);
    expect(groups[0].quantity).toBeNull();
    expect(groups[0].ref).toBe('U01');
  });
  it('shows frozen concept quantities independently of a changed screening proposal', () => {
    const workspace = createExampleWorkspace();
    const solarId = workspace.selections.solar!;
    workspace.analysis.suggestions!.find(suggestion => suggestion.productId === solarId)!.quantity = 99;
    expect(allocationGroups(workspace, catalog).find(group => group.id === solarId)).toMatchObject({ quantity: 3, receipt: { origin: 'bundled-example' } });
  });
  it('labels missing cell characterization without rendering a null count', () => {
    const workspace = createExampleWorkspace();
    workspace.analysis.solar!.cellCount = null;
    expect(activityValue('solar', workspace)).toContain('cell count unresolved');
    expect(activityValue('solar', workspace)).not.toContain('null');
  });
  it('retains unknown catalog references rather than silently dropping their allocations', () => {
    const workspace = createWorkspace(emptyInputs());
    workspace.selections.solar = 'unavailable-revision';
    expect(allocationGroups(workspace, catalog)[0]).toMatchObject({ id: 'unavailable-revision', product: undefined, roles: ['solar'] });
  });
  it('does not reinterpret regulated intent as fully regulated rails', () => {
    const topology = createExampleWorkspace().inputs.topology;
    const points = variationPoints({ ...topology, bus: 'regulated' });
    const bus = points.find(point => point.id === 'bus')!;
    expect(bus.options.filter(option => option.selected).map(option => option.label)).toEqual(['Regulated intent']);
    expect(bus.note).toContain('does not specify');
    expect(bus.options.find(option => option.label === 'Partially regulated')?.represented).toBe(false);
    expect(bus.options.find(option => option.label === 'Fully regulated')?.selected).toBe(false);
    expect(points.flatMap(point => point.options).filter(option => !option.represented).every(option => !option.selected)).toBe(true);
  });
  it('shows direct and converted supply as coexisting but unrepresented per-output alternatives', () => {
    const outputs = variationPoints(createExampleWorkspace().inputs.topology).find(point => point.id === 'outputs')!;
    expect(outputs.options.map(option => option.label)).toEqual(['Direct bus', 'DC–DC converted']);
    expect(outputs.options.every(option => !option.selected && !option.represented)).toBe(true);
    expect(outputs.note).toContain('Can coexist');
  });
  it('keeps DET selectable as intent without implying a supported energy model', () => {
    const conditioning = variationPoints({ ...createExampleWorkspace().inputs.topology, conditioning: 'DET' })[0];
    expect(conditioning.options.find(option => option.label === 'DET')?.selected).toBe(true);
    expect(conditioning.note).toContain('I–V');
  });
  it('marks saved calculated values historical independently of outcomes', () => {
    expect(savedPrefix('stale', true)).toBe('Saved · ');
    expect(savedPrefix('locked', true)).toBe('Saved · ');
    expect(savedPrefix('complete', true)).toBe('');
    expect(savedPrefix('stale', false)).toBe('');
  });
});
