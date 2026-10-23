import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { catalog } from '../data/catalog';
import { createExampleWorkspace, createWorkspace, emptyInputs } from '../state/model';
import type { Workspace } from '../types';
import { missingForNodes, nodeStatuses } from '../workflow';
import { DesignCanvas, ReferenceContext } from './DesignCanvas';
import { AllocationAccounting } from './Architecture';
import { CatalogView, DEFAULT_CATALOG_FILTERS } from './CatalogView';
import { TopologyChoices } from './TopologyChoices';
import { Sheet, SheetNavigationContext } from './ui';
import type { WorkspaceController } from './ui';
import { roots, related, visibleTasks, type TaskContext } from './flow-tasks';

function controller(workspace:Workspace):WorkspaceController {
  return {workspace,statuses:nodeStatuses(workspace),missing:missingForNodes(workspace),activeScenario:workspace.inputs.scenarios.find(s=>s.id===workspace.inputs.activeScenarioId),runNode:vi.fn(),runAll:vi.fn(),updateInputs:vi.fn(),updateScenario:vi.fn(),setActiveScenario:vi.fn(),selectProduct:vi.fn(),loadExample:vi.fn(),reset:vi.fn(),download:vi.fn(),restore:vi.fn(),error:null,clearError:vi.fn()};
}
function context(workspace=createExampleWorkspace()):TaskContext {return {workspace,catalog,picks:{},filters:DEFAULT_CATALOG_FILTERS,missionResult:null,ruleWarnings:[],verdict:'all'};}
function renderCanvas(c=context(),path:typeof roots=[]){return renderToStaticMarkup(createElement(DesignCanvas,{api:controller(c.workspace),tasks:visibleTasks(path,c),selected:path.at(-1)?.key??null,onSelect:vi.fn(),onHome:vi.fn()}));}

describe('flow only presentation',()=>{
  it('initially renders exactly ten activities and only the engineering canvas',()=>{
    const html=renderCanvas();
    expect(html.match(/data-activity=/g)).toHaveLength(10);
    expect(html).toContain('react-flow');
    for(const removed of ['mission-composition-context','data-role=','data-variation=','canvas-findings','canvas-welcome','design-canvas-heading','role="dialog"','architecture-pane','workspace-tabs','icon-rail'])expect(html).not.toContain(removed);
    for(const control of ['Zoom in','Zoom out','Engineering overview'])expect(html).toContain(`aria-label="${control}"`);
  });
  it('reveals battery task granularity as actual graph nodes',()=>{
    const html=renderCanvas(context(),[roots.find(t=>t.owner==='battery')!]);
    for(const label of ['Installed pack','Charge model','Discharge model','Input basis','Readiness'])expect(html).toContain(label);
    expect(html).toContain('data-edge-kind="detail"');
    expect(html).toContain('task detail, no calculation dependency');
  });
  it('retains exact optional evidence semantics',()=>{
    const html=renderCanvas();expect(html).toContain('data-edge="simulation-assessment" data-edge-kind="evidence"');expect(html).toContain('optional evidence, not a required dependency');
  });
  it('retains empty states on the relevant activity nodes',()=>{
    const html=renderCanvas(context(createWorkspace(emptyInputs())));
    expect(html).toContain('Set altitude');expect(html).toContain('not evaluated');expect(html).not.toContain('0 fail');
  });
  it('marks saved activity values historical independently of verdict',()=>{
    const c=context();c.workspace.records.solar.revision++;
    expect(renderCanvas(c)).toContain('Saved ·');
  });
  it('keeps editable variation tasks under topology and per-output scope in help',()=>{
    const c=context(), tasks=related(roots.find(t=>t.owner==='topology')!,c);
    expect(tasks.map(t=>t.kind)).toEqual(expect.arrayContaining(['conditioning','transfer','bus']));
    const editor=renderToStaticMarkup(createElement(TopologyChoices,{topology:c.workspace.inputs.topology,onChange:vi.fn()}));
    expect(editor.match(/type="radio"/g)).toHaveLength(6);expect(editor).not.toContain('value="fully-regulated"');expect(editor).not.toContain('value="direct-bus"');
  });
  it('keeps all six roles in the candidates subflow',()=>{
    const c=context(), candidates=roots.find(t=>t.owner==='candidates')!, roles=related(candidates,c).find(t=>t.kind==='roles')!;
    expect(related(roles,c).map(t=>t.role)).toEqual(['solar','battery','conditioning','distribution','processor','software']);
  });
  it('preserves shared usage accounting without inferring installation quantities',()=>{
    const workspace=createWorkspace(emptyInputs()), board=catalog.products.find(p=>p.roles.includes('conditioning')&&p.roles.includes('distribution'))!;
    workspace.selections={conditioning:board.id,distribution:board.id,processor:board.id};workspace.analysis.suggestions=[{productId:board.id,role:'conditioning',quantity:99,outcome:'incomplete',reason:'Screen only',checks:[],missing:[]}];
    const html=renderToStaticMarkup(createElement(AllocationAccounting,{workspace,catalog,onInspect:vi.fn()}));
    expect(html.match(/One physical usage shared across these logical roles/g)).toHaveLength(1);expect(html).not.toContain('×99');expect(html).toContain('not established installation counts');
  });
  it('exposes catalog review in the candidate branch while preserving authored work',()=>{
    const c=context();c.workspace.catalogReview=['Changed source record'];
    expect(related(roots.find(t=>t.owner==='candidates')!,c).some(t=>t.kind==='migration')).toBe(true);
    expect(c.workspace.catalogReview).toEqual(['Changed source record']);
    expect(renderCanvas(c)).toContain('Catalog review needed');
  });
  it('retains the reference categories and ground scope',()=>{
    const html=renderToStaticMarkup(createElement(ReferenceContext));expect(html).toContain('Ground Segment [1]');expect(html).toContain('nine subsystem categories');expect(html).toContain('CC BY 4.0');
  });
  it('supports controlled catalog filters for contextual return',()=>{
    const c=context();const html=renderToStaticMarkup(createElement(CatalogView,{api:controller(c.workspace),catalog,onInspect:vi.fn(),onCandidates:vi.fn(),filters:{...DEFAULT_CATALOG_FILTERS,search:'no-such-product-xyz',role:'battery'},onFiltersChange:vi.fn()}));
    expect(html).toContain('value="no-such-product-xyz"');expect(html).toContain('No products in this view');expect(html).not.toContain('class="product-card');
  });
  it('uses one nonmodal desktop pane without an expand action',()=>{
    const html=renderToStaticMarkup(createElement(SheetNavigationContext.Provider,{value:{modal:false,nested:false}},createElement(Sheet,{title:'Inputs',onClose:vi.fn(),children:'Inputs'})));
    expect(html).toContain('aria-modal="false"');expect(html).not.toContain('sheet-scrim');expect(html).not.toContain('Expand inspector');expect(html).not.toContain('data-action="context-back"');expect(html).toContain('data-action="context-close"');
  });
  it('retains mobile modal and contextual Back semantics in one dialog',()=>{
    const html=renderToStaticMarkup(createElement(SheetNavigationContext.Provider,{value:{modal:true,nested:true,backLabel:'Back to catalog'}},createElement(Sheet,{title:'Product',onClose:vi.fn(),children:'Evidence'})));
    expect(html).toContain('aria-modal="true"');expect(html).toContain('Back to catalog');expect(html.match(/role="dialog"/g)).toHaveLength(1);
  });
});
