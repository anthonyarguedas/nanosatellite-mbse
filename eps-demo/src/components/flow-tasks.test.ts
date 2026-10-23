import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { createExampleWorkspace } from '../state/model';
import { NODE_DEFINITIONS } from '../workflow';
import { DEFAULT_CATALOG_FILTERS } from './CatalogView';
import { activatePath, child, COLLECTION_KINDS, entries, presentationEdges, related, roots, textParts, visibleTasks, type FlowTask, type TaskContext } from './flow-tasks';
import { activityEdges } from './design-canvas-model';
import { helpSections } from './flow-task-help';

function context():TaskContext{return {workspace:createExampleWorkspace(),catalog,picks:{},filters:DEFAULT_CATALOG_FILTERS,missionResult:null,ruleWarnings:[],verdict:'all'};}
const root=(id:string)=>roots.find(t=>t.key===id)!;
const sub=(parent:FlowTask,kind:string,c:TaskContext)=>related(parent,c).find(t=>t.kind===kind)!;

describe('presentation task registry',()=>{
  it('has exactly the canonical engine roots and independent detail identities',()=>{
    expect(roots.map(t=>t.key)).toEqual(NODE_DEFINITIONS.map(n=>n.id));
    for(const r of roots)for(const t of related(r,context())){expect(t.key).toContain(`${r.key}/`);expect(roots.some(r=>r.key===t.key)).toBe(false);expect(t.owner).toBe(r.owner);}
  });
  it('keeps navigation, selection and branch expansion pure',()=>{
    const c=context(),before=JSON.stringify(c.workspace);let path=activatePath([],root('battery'));
    path=activatePath(path,sub(path[0],'pack',c));visibleTasks(path,c);presentationEdges(visibleTasks(path,c));
    expect(JSON.stringify(c.workspace)).toBe(before);expect(path).toHaveLength(2);
  });
  it('replaces root branches and selects parents without creating a Back stack',()=>{
    const c=context(),battery=root('battery'),pack=sub(battery,'pack',c),charge=sub(battery,'charge',c);
    expect(activatePath([battery,pack],charge)).toEqual([battery,charge]);expect(activatePath([battery,pack],root('solar'))).toEqual([root('solar')]);expect(activatePath([battery,pack],battery)).toEqual([battery]);
    expect(visibleTasks([],c)).toHaveLength(10);
  });
  it('does not add UI edges to the exact controller dependency/evidence set',()=>{
    const c=context(),before=activityEdges();const details=presentationEdges(visibleTasks([root('simulation')],c));
    expect(details.every(e=>e.kind==='detail')).toBe(true);expect(activityEdges()).toEqual(before);
    expect(before.find(e=>e.id==='simulation-assessment')?.kind).toBe('evidence');expect(before.some(e=>e.id==='mission-scenarios')).toBe(false);
  });
  it('keeps branch growth bounded and materializes one collection record',()=>{
    const c=context(),cat=sub(root('candidates'),'catalog',c);expect(entries(cat,c)).toHaveLength(catalog.products.length);expect(related(cat,c).filter(t=>t.kind==='product')).toHaveLength(1);
    const paths=[root('candidates'),cat,related(cat,c)[0]];const shown=visibleTasks(paths,c);expect(new Set(shown.map(t=>t.key)).size).toBe(shown.length);expect(shown.length).toBeLessThan(30);
  });
  it('makes every catalog record reachable with all source properties and citations',()=>{
    const c=context(),cat=sub(root('candidates'),'catalog',c);
    for(const e of entries(cat,c)){
      const p=catalog.products.find(p=>p.id===e.id)!;const specs=sub(e.task,'specs',c),sources=sub(e.task,'sources',c);
      expect(entries(specs,c).map(e=>e.id)).toEqual(Object.keys(p.specs));expect(entries(sources,c).map(e=>e.id)).toEqual(p.sources.map(s=>s.id));
      for(const spec of entries(specs,c)){const facets=helpSections(spec.task,c).flatMap(s=>s.fields??[]);expect(facets.map(t=>t.label)).toEqual(expect.arrayContaining(['Property value','Original representation','Operating conditions','Rationale','Source location']));}
    }
  });
  it('keeps every load and window reachable without changing independent schedules',()=>{
    const c=context(),before=JSON.stringify(c.workspace.inputs.scenarios);
    for(const scenario of c.workspace.inputs.scenarios){c.workspace.inputs.activeScenarioId=scenario.id;const loads=sub(root('scenarios'),'loads',c);expect(entries(loads,c).map(e=>e.id)).toEqual(scenario.loads.map(l=>l.id));for(const e of entries(loads,c)){const windows=sub(e.task,'windows',c);expect(entries(windows,c).map(e=>e.id)).toEqual(scenario.loads.find(l=>l.id===e.id)!.windows.map(w=>w.id));}}
    expect(JSON.stringify(c.workspace.inputs.scenarios)).toBe(before);
  });
  it('covers all EPS and supplementary assessment checks exactly once',()=>{
    const c=context(),groups=related(root('assessment'),c).filter(t=>t.kind==='check-group');const all=groups.flatMap(t=>entries(t,c));expect(all).toHaveLength(c.workspace.analysis.checks!.length);expect(all.map(e=>JSON.parse(e.task.text!).id).sort()).toEqual(c.workspace.analysis.checks!.map(c=>c.id).sort());
  });
  it('preserves verdict filtering without losing access when cleared',()=>{
    const c=context(),groups=related(root('assessment'),c).filter(t=>t.kind==='check-group');c.verdict='fail';expect(groups.flatMap(t=>entries(t,c)).every(e=>JSON.parse(e.task.text!).verdict==='fail')).toBe(true);c.verdict='all';expect(groups.flatMap(t=>entries(t,c))).toHaveLength(c.workspace.analysis.checks!.length);
  });
  it('keeps parameter provenance and full text lossless',()=>{
    const c=context(),basis=sub(root('simulation'),'basis',c);expect(entries(basis,c).map(e=>e.id)).toEqual(c.workspace.provenance!.map(r=>r.parameter));
    const text='Exact original text, including whitespace.\n'.repeat(100);expect(textParts(text).join('')).toBe(text);expect(textParts(text).every(t=>t.length<=620)).toBe(true);
    const task=child(root('mission'),'text','Long record',{text});expect(related(task,c)).toEqual([]);
  });
  it('exposes separate battery limits, installed generation and all topology alternatives',()=>{
    const c=context();expect(related(root('battery'),c).map(t=>t.kind)).toEqual(expect.arrayContaining(['pack','charge','discharge']));expect(related(root('solar'),c).map(t=>t.kind)).toEqual(expect.arrayContaining(['cell','installed']));expect(related(root('topology'),c).map(t=>t.kind)).toEqual(expect.arrayContaining(['conditioning','transfer','bus','resources']));
  });
  it('keeps review export, approved rule import and warnings reachable',()=>{
    const c=context(),kicad=sub(root('candidates'),'kicad',c),rules=sub(kicad,'rules',c);expect(related(kicad,c).map(t=>t.kind)).toEqual(['kicad-blockers','physical-gates','rules','kicad-warnings']);expect(sub(rules,'rule-warnings',c)).toBeTruthy();
  });
  it('bounds line-heavy and Unicode records without losing their content',()=>{
    const text=('Short line\n\n'+'🛰️'.repeat(40)+'\n').repeat(40);
    const parts=textParts(text);expect(parts.join('')).toBe(text);expect(parts.every(p=>p.length<=620&&p.split('\n').length<=14)).toBe(true);
    expect(parts.every(p=>!/[\uD800-\uDBFF]$/.test(p))).toBe(true);
  });
  it('retains all text parts as homogeneous editable graph records',()=>{
    const c=context(),scenario=c.workspace.inputs.scenarios.find(s=>s.id===c.workspace.inputs.activeScenarioId)!;scenario.description='a'.repeat(2000);const t=sub(root('scenarios'),'case-description',c);expect(COLLECTION_KINDS.has(t.kind)).toBe(true);expect(entries(t,c).map(e=>e.task.text).join('')).toBe(scenario.description);expect(entries(t,c).every(e=>e.task.kind==='edit-passage')).toBe(true);
  });
});
