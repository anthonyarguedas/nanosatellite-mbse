import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe,expect,it } from 'vitest';
import { catalog } from '../data/catalog';
import { createExampleWorkspace } from '../state/model';
import { NODE_DEFINITIONS } from '../workflow';
import { DEFAULT_CATALOG_FILTERS,specValue } from './CatalogView';
import { legacyArrayForm } from '../catalog/validation';
import { child,DOCUMENTATION_KINDS,entries,GRAPH_TASK_PURPOSE,related,roots,taskPurpose,visibleTasks,type TaskContext } from './flow-tasks';
import { helpSections,PROJECT_HELP } from './flow-task-help';
import { FlowTaskHelp } from './FlowTaskHelp';
import { SCOPES } from './NodeInspector';
import { stepsFor } from './CalculationTrace';
import { BIRDS4_EXAMPLE_BASIS } from '../data/birds4';
const context=():TaskContext=>({workspace:createExampleWorkspace(),catalog,picks:{},filters:DEFAULT_CATALOG_FILTERS,missionResult:null,ruleWarnings:['Warning'],verdict:'all'});
describe('semantic graph classification and lossless contextual help',()=>{
  it('classifies every reachable task explicitly and never generates a documentation node',()=>{
    const c=context(),queue=[...roots],visited=new Set<string>();while(queue.length){const t=queue.shift()!;if(visited.has(t.key))continue;visited.add(t.key);expect(DOCUMENTATION_KINDS.has(t.kind),t.key).toBe(false);expect(taskPurpose(t.kind)).toBeTruthy();const children=[...related(t,c),...entries(t,c).map(e=>e.task)];for(const k of children)expect(k.parent).toBe(t.key);queue.push(...children);}for(const r of roots){const shown=visibleTasks([r],c);for(const t of shown)if(t.parent)expect(shown.some(p=>p.key===t.parent)).toBe(true);}
    expect(()=>taskPurpose('accidentally-added-kind')).toThrow();expect(taskPurpose('finding')).toBe('review');expect(taskPurpose('run-assumption')).toBe('review');
  });
  it('retains full methods, traces, scope, requirements, exchanges and reference context',()=>{
    const c=context(),before=JSON.stringify(c.workspace);for(const r of roots){const sections=helpSections(r,c),text=JSON.stringify(sections),n=NODE_DEFINITIONS.find(n=>n.id===r.owner)!;expect(text).toContain(JSON.stringify(SCOPES[r.owner]).slice(1,-1));expect(text).toContain(JSON.stringify(n.equation).slice(1,-1));for(const s of stepsFor(r.owner,c.workspace)){expect(text).toContain(JSON.stringify(s.inputs).slice(1,-1));expect(text).toContain(JSON.stringify(s.relation).slice(1,-1));expect(text).toContain(JSON.stringify(s.output).slice(1,-1));}expect(sections[0].upstream).toEqual(n.dependencies);for(const req of n.requirements)expect(text).toContain(req);}
    const mission=helpSections(roots[0],c),text=JSON.stringify(mission);for(const fact of BIRDS4_EXAMPLE_BASIS.missionFacts)expect(text).toContain(JSON.stringify(fact).slice(1,-1));expect(text).toContain('CubeSats [1..*]');expect(text).toContain('CubeSat Orbits [1..*]');expect(text).toContain('GNSS');expect(text).toContain('creativecommons.org');expect(JSON.stringify(c.workspace)).toBe(before);
  });
  it('preserves every catalog property representation, conditions, sources and full record',()=>{
    const c=context();for(const p of catalog.products){const pt=child(roots.find(t=>t.key==='candidates')!,'product',p.name,{ref:p.id});const product=JSON.stringify(helpSections(pt,c));expect(product).toContain(JSON.stringify(p.description).slice(1,-1));if(p.accountingBoundary)expect(product).toContain(JSON.stringify(p.accountingBoundary).slice(1,-1));for(const text of [...p.caveats??[],...p.supportedConfigurations??[]])expect(product).toContain(JSON.stringify(text).slice(1,-1));
      for(const [key,s] of Object.entries(p.specs)){const spec=child(pt,'spec',key,{ref:key,field:p.id}),fields=helpSections(spec,c)[0].fields!,get=(label:string)=>fields.find(f=>f.label===label)!.value;expect(get('Property value')).toBe(specValue({...s,valueForm:s.valueForm??legacyArrayForm(p,key)}));expect(JSON.parse(get('Complete property record'))).toEqual(s);expect(get('Source references')).toBe([s.sourceId,...s.additionalSourceIds??[]].filter(Boolean).join(', '));}
      for(const s of p.sources){const source=child(pt,'source',s.title,{ref:s.id,field:JSON.stringify(s)});expect(JSON.parse(helpSections(source,c)[0].fields![0].value)).toEqual(s);}
    }
  });
  it('renders accessible disclosures with full selectable content and original links',()=>{
    const c=context(),sections=helpSections(roots[0],c),html=renderToStaticMarkup(createElement(FlowTaskHelp,{sections,onRoot:()=>{}}));expect(html).toContain('<summary>Method &amp; evidence</summary>');expect(html).toContain('data-help-field="Scope"');expect(html).toContain(BIRDS4_EXAMPLE_BASIS.source.url);expect(html).not.toContain('associated detail nodes');expect(PROJECT_HELP[0].fields).toHaveLength(4);
  });
});
