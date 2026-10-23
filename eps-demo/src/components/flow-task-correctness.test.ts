import { describe, expect, it } from 'vitest';
import { catalog } from '../data/catalog';
import { changeInputs, createExampleWorkspace, evaluateReady } from '../state/model';
import { DEFAULT_CATALOG_FILTERS, specValue } from './CatalogView';
import { child, entries, productRoleKey, related, resolvePath, roots, selectedProductRole, textParts, visibleTasks, type FlowTask, type TaskContext } from './flow-tasks';
import { helpSections } from './flow-task-help';
import { missionCatalogue } from './mission-session';
import { acceptAltitude, searchLexical } from '../mission-assist/retrieval';
import { applyMissionAnalogue } from '../mission-assist/integration';
function context():TaskContext{return {workspace:createExampleWorkspace(),catalog,picks:{},filters:DEFAULT_CATALOG_FILTERS,missionResult:searchLexical('Image vegetation across the Earth to monitor land cover and agriculture, then downlink camera observations.',missionCatalogue),ruleWarnings:['Original rule warning'],verdict:'all'};}
const root=(id:string)=>roots.find(t=>t.key===id)!;
const sub=(parent:FlowTask,kind:string,c:TaskContext)=>related(parent,c).find(t=>t.kind===kind)!;
const value=(task:FlowTask,c:TaskContext,label:string)=>helpSections(task,c).flatMap(s=>s.fields??[]).find(f=>f.label===label)!.value;
function selectedCheck(c:TaskContext,field='assessment') {
  const r=root(field==='simulation'?'simulation':'assessment'),group=related(r,c).find(t=>t.kind==='check-group'&&(field==='simulation'||t.ref==='extra'))!;
  return [r,group,entries(group,c).find(e=>JSON.parse(e.task.text!).id==='SOLAR-POWER')?.task??entries(group,c)[0].task];
}
describe('live task identities and contextual evidence',()=>{
  it('updates an open SOLAR-POWER verdict and its evidence after recompute',()=>{
    const c=context(),path=selectedCheck(c);expect(JSON.parse(path[2].text!).verdict).toBe('pass');
    c.workspace=evaluateReady(changeInputs(c.workspace,i=>({...i,solar:{...i.solar,installedPowerW:0}})));
    const actual=c.workspace.analysis.checks!.find(check=>check.id==='SOLAR-POWER')!,live=resolvePath(path,c);
    expect(actual.verdict).toBe('fail');expect(JSON.parse(live[2].text!)).toEqual(actual);expect(visibleTasks(path,c).find(t=>t.key===path[2].key)?.text).toBe(JSON.stringify(actual));
    expect(value(live[2],c,'Criterion detail')).toBe(actual.detail);expect(value(live[2],c,'Scope & equation')).toContain(actual.scope??'Scope not recorded.');expect(value(live[2],c,'Evidence references')).toBe(actual.sourceIds?.join(', ')||'No source references recorded.');
    c.verdict='pass';expect(resolvePath(path,c).at(-1)!.kind).toBe('check-group');
  });
  it('resolves simulation evidence, assumptions and warnings through live parents',()=>{
    const c=context(),path=selectedCheck(c,'simulation'),index=path[2].index!;
    c.workspace.analysis.simulation!.checks[index]={...c.workspace.analysis.simulation!.checks[index],verdict:'fail',detail:'Updated simulation criterion',scope:'Updated simulation scope',sourceIds:['updated-source']};
    const live=resolvePath(path,c).at(-1)!;expect(value(live,c,'Criterion detail')).toBe('Updated simulation criterion');expect(value(live,c,'Scope & equation')).toContain('Updated simulation scope');expect(value(live,c,'Evidence references')).toBe('updated-source');
    const assumptions=sub(root('simulation'),'assumptions',c),old=entries(assumptions,c)[0].task;expect(old.kind).toBe('run-assumption');c.workspace.analysis.simulation!.assumptions[0]='New live assumption';expect(resolvePath([root('simulation'),assumptions,old],c).at(-1)!.text).toBe('New live assumption');
    const ki=sub(root('candidates'),'kicad',c),rules=sub(ki,'rules',c),warnings=sub(rules,'rule-warnings',c),warning=entries(warnings,c)[0].task;expect(warning.kind).toBe('finding');c.ruleWarnings=['Updated warning'];expect(resolvePath([root('candidates'),ki,rules,warnings,warning],c).at(-1)!.text).toBe('Updated warning');
  });
  it('keeps sibling keys unique and the full P60 property in its owning evidence',()=>{
    const c=context(),queue=[...roots],visited=new Set<string>();while(queue.length){const task=queue.shift()!;if(visited.has(task.key))continue;visited.add(task.key);const children=related(task,c),records=entries(task,c).map(e=>e.task);expect(new Set(children.map(t=>t.key)).size,task.key).toBe(children.length);expect(new Set(records.map(t=>t.key)).size,task.key).toBe(records.length);queue.push(...children,...records);}
    const cat=sub(root('candidates'),'catalog',c),p=entries(cat,c).find(e=>e.id==='gomspace-p60-one-acu-one-pdu-16v')!.task,specs=sub(p,'specs',c),spec=entries(specs,c).find(e=>e.id==='historicalEfficiencyCurvePoints')!.task;
    expect(value(spec,c,'Property value')).toBe(specValue(catalog.products.find(p=>p.id===spec.field)!.specs.historicalEfficiencyCurvePoints));expect(value(spec,c,'Property value')).toHaveLength(626);expect(helpSections(spec,c)[0].fields!.map(f=>f.label)).toContain('Original representation');expect(related(spec,c).every(t=>t.kind==='source')).toBe(true);
  });
  it('applies assessment verdict filtering only to assessment collections',()=>{
    const c=context(),sim=sub(root('simulation'),'check-group',c),cat=sub(root('candidates'),'catalog',c),p=entries(cat,c).find(e=>e.task.role==='conditioning')!.task,screen=sub(p,'screen',c),checks=sub(screen,'check-group',c),counts=[entries(sim,c).length,entries(checks,c).length];c.verdict='pass';expect([entries(sim,c).length,entries(checks,c).length]).toEqual(counts);for(const group of related(root('assessment'),c).filter(t=>t.kind==='check-group'))expect(entries(group,c).every(e=>JSON.parse(e.task.text!).verdict==='pass')).toBe(true);
  });
  it('scopes role overrides to the product branch and refreshes checks/reasons/gaps',()=>{
    const c=context(),roles=sub(root('candidates'),'roles',c),conditioning=related(roles,c).find(t=>t.role==='conditioning')!,distribution=related(roles,c).find(t=>t.role==='distribution')!,productId=c.workspace.selections.conditioning!,p=entries(conditioning,c).find(e=>e.id===productId)!.task;
    for(const role of ['conditioning','distribution'] as const){const s=c.workspace.analysis.suggestions!.find(s=>s.productId===productId&&s.role===role)!;s.reason=`${role} reason`;s.missing=[`${role} gap`];s.checks=[{id:'ROLE-CHECK',title:'Role check',verdict:'unassessed',detail:`${role} criterion`}];}
    const screen=sub(p,'screen',c),checks=sub(screen,'check-group',c),oldCheck=entries(checks,c)[0].task;c.picks[productRoleKey(p)]='distribution';
    const live=resolvePath([root('candidates'),roles,conditioning,p,screen,checks,oldCheck],c).at(-1)!;expect(value(live,c,'Criterion detail')).toBe('distribution criterion');expect(value(screen,c,'Screen reason')).toBe('distribution reason');expect(entries(sub(screen,'gaps',c),c).some(e=>e.task.text==='distribution gap')).toBe(true);
    const other=entries(distribution,c).find(e=>e.id===productId)!.task;expect(selectedProductRole(other,c)).toBe('distribution');expect(productRoleKey(other)).not.toBe(productRoleKey(p));c.picks[productRoleKey(p)]='conditioning';expect(selectedProductRole(other,c)).toBe('distribution');
  });
  it('keeps empty text, long rationale, receipt values and source metadata lossless',()=>{
    expect(textParts('')).toEqual(['']);const c=context(),usages=sub(root('candidates'),'usages',c),usage=entries(usages,c)[0].task,rationale='r'.repeat(700);c.workspace.allocations!.find(r=>r.productId===usage.ref)!.rationale=rationale;
    expect(value(usage,c,'Allocation rationale')).toBe(rationale);expect(value(child(usage,'allocation-receipt','Receipt'),c,'Allocation rationale')).toBe(rationale);expect(related(usage,c).some(t=>t.kind==='product')).toBe(true);
    const analogue=c.missionResult!.matches.find(m=>typeof m.mission.orbit.altitudeKm?.value==='number')!;c.workspace.inputs=applyMissionAnalogue(c.workspace.inputs,acceptAltitude(analogue),'Original query');c.workspace.inputs.mission.orbitSuggestion!.parameterOriginal='o'.repeat(700);
    expect(JSON.parse(value(sub(root('mission'),'receipt',c),c,'Complete acceptance receipt')).parameterOriginal).toBe('o'.repeat(700));
    const source=child(root('mission'),'source','Source',{ref:'synthetic-source',field:JSON.stringify({id:'synthetic-source',title:'t'.repeat(700),url:'https://example.org',revision:'1',location:'Here',retrievedAt:'2026',quotes:['Exact 🛰️ quote\n']})});expect(JSON.parse(value(source,c,'Full source metadata')).title).toBe('t'.repeat(700));expect(value(source,c,'Quote 1')).toBe('Exact 🛰️ quote\n');
  });
});
