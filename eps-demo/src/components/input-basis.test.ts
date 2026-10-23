import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { catalog } from '../data/catalog';
import { applyProduct, changeInputs, createExampleWorkspace, evaluateReady } from '../state/model';
import type { Workspace } from '../types';
import { missingForNodes, nodeStatuses } from '../workflow';
import { InputBasis } from './InputBasis';
import { NodeInspector } from './NodeInspector';
import { ProductInspector } from './CatalogView';
import type { WorkspaceController } from './ui';

function controller(workspace: Workspace): WorkspaceController {
  return {
    workspace, statuses: nodeStatuses(workspace), missing: missingForNodes(workspace),
    activeScenario: workspace.inputs.scenarios.find(scenario => scenario.id === workspace.inputs.activeScenarioId),
    runNode: vi.fn(), runAll: vi.fn(), updateInputs: vi.fn(), updateScenario: vi.fn(), setActiveScenario: vi.fn(),
    selectProduct: vi.fn(), loadExample: vi.fn(), reset: vi.fn(), download: vi.fn(), restore: vi.fn(), error: null, clearError: vi.fn(),
  };
}
const inspector = (workspace: Workspace, id: 'battery' | 'solar' | 'budget') => renderToStaticMarkup(createElement(NodeInspector, {
  id, api: controller(workspace), catalog, onClose: vi.fn(), onNavigate: vi.fn(), onInspect: vi.fn(), onNode: vi.fn(),
}));

describe('visible numerical basis and allocation confirmation', () => {
  it('distinguishes sourced pack energy from assumed retained energy', () => {
    const html = renderToStaticMarkup(createElement(InputBasis, { workspace: createExampleWorkspace(), catalog, node: 'battery' }));
    expect(html).toContain('data-input-parameter="battery.capacityWh" data-basis-kind="catalog-value"');
    expect(html).toContain('data-input-parameter="battery.retainedEnergy" data-basis-kind="engineering-assumption"');
    expect(html).toContain('86.0000');
    expect(html).toContain('Typical/nominal values establish no guaranteed bound');
    expect(html).toContain('gomspace.com');
    expect(html.match(/<details[^>]*>/)?.[0]).not.toContain('open=');
  });
  it('explains that unresolved pack energy gates simulation rather than sizing', () => {
    const workspace = evaluateReady(applyProduct(createExampleWorkspace(), 'conditioning', 'isis-iceps2-type-a'));
    const html = inspector(workspace, 'battery');
    expect(html).toContain('Pack usable energy is unresolved');
    expect(html).toContain('Preliminary sizing and catalog screening can continue');
    expect(html).toContain('A manual value is recorded as an engineering assumption');
    expect(nodeStatuses(workspace).battery).toBe('complete');
  });
  it('presents manual pack energy as an assumption without source attribution', () => {
    const allocated = evaluateReady(applyProduct(createExampleWorkspace(), 'conditioning', 'isis-iceps2-type-a'));
    const workspace = changeInputs(allocated, inputs => { inputs.battery.capacityWh = 8; return inputs; });
    const html = renderToStaticMarkup(createElement(InputBasis, { workspace, catalog, node: 'battery' }));
    expect(html).toContain('data-input-parameter="battery.capacityWh" data-basis-kind="engineering-assumption"');
    expect(html).toContain('No manufacturer characterization is claimed');
  });
  it('keeps a missing cell count explicit while presenting the independent power requirement', () => {
    const workspace = evaluateReady(applyProduct(createExampleWorkspace(), 'solar', 'cesi-ctj30-26p5'));
    const html = inspector(workspace, 'solar');
    expect(html).toContain('Unresolved');
    expect(html).toContain('Minimum source-boundary EOL power');
    expect(html).not.toContain('null cells');
  });
  it('exposes the additional EPS demand at the budget instead of hiding it downstream', () => {
    const html = inspector(createExampleWorkspace(), 'budget');
    expect(html).toContain('Additional EPS baseline');
    expect(html).toContain('Added once to scheduled spacecraft loads');
    expect(html).toContain('Spacecraft loads + EPS baseline');
  });
  it('allows legacy selected products to explicitly confirm their missing allocation count', () => {
    const workspace = createExampleWorkspace();
    delete workspace.allocations;
    const product = catalog.products.find(item => item.id === workspace.selections.battery)!;
    const html = renderToStaticMarkup(createElement(ProductInspector, { product, catalog, api: controller(workspace), onClose: vi.fn(), onCandidates: vi.fn(), onApplied: vi.fn() }));
    expect(html).toContain('Update allocation');
    expect(html).toContain('No frozen count is recorded');
    expect(html.match(/<button[^>]*class="button primary"[^>]*>/)?.[0]).not.toContain('disabled');
  });
  it('permits explicit reapplication of a sourced rating to the already selected product', () => {
    const workspace = createExampleWorkspace();
    const product = catalog.products.find(item => item.id === workspace.selections.battery)!;
    const html = renderToStaticMarkup(createElement(ProductInspector, { product, catalog, api: controller(workspace), onClose: vi.fn(), onCandidates: vi.fn(), onApplied: vi.fn() }));
    expect(html).toContain('Reapply allocation');
    expect(html.match(/<button[^>]*class="button primary"[^>]*>/)?.[0]).not.toContain('disabled');
  });
});
