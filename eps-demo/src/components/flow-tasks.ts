import type { Catalog, Check, NodeId, Product, Role, Source, Workspace } from '../types';
import { NODE_DEFINITIONS, missingForNodes } from '../workflow';
import { ACTIVITY_TITLES, allocationGroups } from './design-canvas-model';
import { LABELS, relevant } from './InputBasis';
import { ROLE_NAMES } from './ui';
import { productCoverage } from '../catalog/coverage';
import { specLabel, type CatalogFilters } from './CatalogView';
import type { MissionSearchResult } from '../mission-assist/types';
import { getKiCadReadiness } from '../kicad';

/** View identity is deliberately independent of the engine's NodeId. */
export interface FlowTask {
  key: string; kind: string; title: string; owner: NodeId; parent?: string;
  ref?: string; role?: Role; index?: number; text?: string; field?: string;
  /** Stable product branch identity, independent of a descendant's record ref. */
  productKey?: string;
}
export interface TaskContext {
  workspace: Workspace; catalog: Catalog; picks: Record<string, string>;
  filters: CatalogFilters; missionResult: MissionSearchResult | null;
  ruleWarnings: string[]; verdict: string;
}
/** Semantic classification, independent of labels, text length, and controls. */
export const GRAPH_TASK_PURPOSE = {
  activity:'activity', 'case-energy':'work', loads:'work', load:'work', 'load-power':'work', windows:'work', window:'work',
  cell:'work', installed:'work', pack:'work', charge:'work', discharge:'work', conditioning:'work', transfer:'work', bus:'work', resources:'work',
  'case-description':'work', 'case-provenance':'work', 'query-text':'work', 'edit-passage':'work',
  preview:'review', demand:'review', energy:'review', power:'review', 'orbit-numbers':'review', 'run-basis':'review',
  roles:'review', role:'review', catalog:'review', product:'review', screen:'review', allocation:'work',
  'mission-search':'work', analogues:'review', analogue:'review', 'accept-altitude':'work', kicad:'work', rules:'work',
  basis:'review', provenance:'review', specs:'review', spec:'review', sources:'review', source:'review', 'analogue-sources':'review',
  usages:'review', usage:'review', 'allocation-receipt':'review', receipt:'review', prerequisites:'review', readiness:'review',
  'check-group':'review', check:'review', gaps:'review', migration:'review', 'kicad-blockers':'review', 'physical-gates':'review',
  'kicad-warnings':'review', 'rule-warnings':'review', assumptions:'review', finding:'review', 'run-assumption':'review',
} as const;
export const DOCUMENTATION_KINDS = new Set(['method','trace','trace-step','exchanges','exchange','impact','reference','reference-subsystems','reference-ground','reference-license','study','study-facts','outputs','schedule-help','mission-scope','coverage','configurations','accounting','caveats','analogue-parameters','analogue-caveats','kicad-pipeline','text','passage','query-examples']);
export function taskPurpose(kind: string) {
  if (!(kind in GRAPH_TASK_PURPOSE)) throw new Error(`Unknown graph task kind: ${kind}`);
  return GRAPH_TASK_PURPOSE[kind as keyof typeof GRAPH_TASK_PURPOSE];
}
export const roots: FlowTask[] = NODE_DEFINITIONS.map(node => ({ key: node.id, kind: 'activity', title: ACTIVITY_TITLES[node.id], owner: node.id }));
export function child(parent: FlowTask, kind: string, title: string, extra: Partial<FlowTask> = {}): FlowTask {
  const task = { owner: parent.owner, role: parent.role, ref: parent.ref, productKey: parent.productKey, ...extra, parent: parent.key,
    kind, title, key: `${parent.key}/${kind}:${encodeURIComponent(extra.ref ?? String(extra.index ?? ''))}${extra.role ? `:${extra.role}` : ''}` };
  if(kind==='product')task.productKey=task.key;
  return task;
}
export function textParts(text: string, size = 620): string[] {
  const parts: string[] = [];
  let part='', lines=1, column=0;
  for(const character of text) {
    const width=character==='\t'?4:1;
    const nextLines=character==='\n'?lines+1:column+width>44?lines+1:lines;
    if(part&&(part.length+character.length>size||nextLines>14)) {parts.push(part);part='';lines=1;column=0;}
    part+=character;
    if(character==='\n'){lines++;column=0;}
    else {if(column+width>44){lines++;column=0;}column+=width;}
  }
  if(part)parts.push(part);
  return parts.length ? parts : [''];
}
/** Apply one editable part within the canonical whole-field storage limit. */
export function replaceAuthoredPart(text: string, index: number, replacement: string, maxLength = 2000): string | null {
  const parts = textParts(text);
  if (!Number.isInteger(index) || index < 0 || index >= parts.length) return null;
  parts[index] = replacement;
  const joined = parts.join('');
  return joined.length <= maxLength ? joined : null;
}
export interface Entry { id: string; label: string; task: FlowTask }
const entry = (parent: FlowTask, kind: string, id: string, label: string, extra: Partial<FlowTask> = {}): Entry => ({ id, label, task: child(parent, kind, label, { ...extra, ref: id }) });
export function taskProduct(t: FlowTask, c: TaskContext): Product | undefined { return c.catalog.products.find(p => p.id === t.ref); }
export function productRoleKey(t: FlowTask): string { return `product-role:${t.productKey??t.key}`; }
export function selectedProductRole(t: FlowTask,c: TaskContext): Role | undefined { return c.picks[productRoleKey(t)] as Role|undefined ?? t.role; }
export function taskChecks(t: FlowTask, c: TaskContext): Check[] {
  if (t.field === 'simulation') return c.workspace.analysis.simulation?.checks ?? [];
  if (t.field === 'screen') return c.workspace.analysis.suggestions?.find(s => s.productId === t.ref && s.role === selectedProductRole(t,c))?.checks ?? [];
  return c.workspace.analysis.checks ?? [];
}
export function taskSources(t: FlowTask, c: TaskContext): Source[] {
  if(t.field==='check') { const ids=(JSON.parse(t.text??'{}') as Check).sourceIds??[];return [...new Map(c.catalog.products.flatMap(p=>p.sources).filter(s=>ids.includes(s.id)).map(s=>[s.id,s])).values()]; }
  if (t.field === 'mission-receipt') return c.workspace.inputs.mission.orbitSuggestion?.sources ?? [];
  if (t.kind === 'analogue-sources') return c.missionResult?.matches.find(m => m.mission.id === t.ref)?.mission.sources ?? [];
  const product = taskProduct(t, c);
  if (product) return product.sources;
  const record = c.workspace.provenance?.find(p => p.parameter === t.ref);
  const all = [...c.catalog.products.flatMap(p => p.sources), ...c.workspace.inputs.mission.orbitSuggestion?.sources ?? []];
  return [...new Map(all.filter(s => !record || record.sourceIds.includes(s.id)).map(s => [s.id, s])).values()];
}
export function catalogRecords(c: TaskContext): Product[] {
  const f = c.filters;
  return c.catalog.products.filter(p => {
    const query = f.search.trim().toLowerCase();
    return (!query || `${p.name} ${p.manufacturer} ${p.partNumber} ${p.description}`.toLowerCase().includes(query)) &&
      (f.role === 'all' || p.roles.includes(f.role as Role)) && (f.manufacturer === 'all' || f.manufacturer === p.manufacturer) &&
      (f.level === 'all' || f.level === p.level) && (f.coverage === 'all' || !f.coverage || p.roles.filter(r => f.role === 'all' || r === f.role).some(r => productCoverage(p, r).comparisonCovered === (f.coverage === 'covered'))) &&
      (!f.onlyCandidates || c.workspace.analysis.suggestions?.some(s => s.productId === p.id));
  });
}
export function entries(t: FlowTask, c: TaskContext): Entry[] {
  const w = c.workspace, scenario = w.inputs.scenarios.find(s => s.id === w.inputs.activeScenarioId);
  const findings=(texts:string[],label:string,kind='finding')=>texts.map((text,index)=>entry(t,kind,String(index),`${label} ${index+1}`,{text,index}));
  switch (t.kind) {
    case 'case-description': case 'case-provenance': case 'query-text': {
      const field=t.kind==='case-description'?'description':t.kind==='case-provenance'?'provenance':'conOps';
      const value=field==='conOps'?w.inputs.mission.conOps??'':scenario?.[field]??'';
      return textParts(value).map((text,index)=>entry(t,'edit-passage',String(index),`Text part ${index+1}`,{text,index,field}));
    }
    case 'prerequisites': return findings(missingForNodes(w)[t.owner],'Readiness item');
    case 'loads': return scenario?.loads.map(l => entry(t, 'load', l.id, l.name || 'Unnamed load')) ?? [];
    case 'windows': return scenario?.loads.find(l => l.id === t.ref)?.windows.map((win, index) => entry(t, 'window', win.id, `Window ${index + 1}`, { field: t.ref })) ?? [];
    case 'catalog': return catalogRecords(c).map(p => entry(t, 'product', p.id, p.name, { role: c.filters.role === 'all' ? p.roles[0] : c.filters.role as Role }));
    case 'role': return c.catalog.products.filter(p => p.roles.includes(t.role!)).map(p => entry(t, 'product', p.id, p.name, { role: t.role }));
    case 'specs': return Object.keys(taskProduct(t,c)?.specs ?? {}).map(key => entry(t, 'spec', key, specLabel(key), { field: t.ref }));
    case 'sources': case 'analogue-sources': return taskSources(t, c).map(s => entry(t, 'source', s.id, s.title, { field: JSON.stringify(s) }));
    case 'basis': return (w.provenance ?? []).filter(r => relevant(t.owner, r.parameter)).map(r => entry(t, 'provenance', r.parameter, LABELS[r.parameter][0]));
    case 'readiness': return findings(t.owner==='candidates'?w.catalogReview??[]:[],'Catalog review');
    case 'check-group': return taskChecks(t, c).map((check, index) => ({ check, index })).filter(({ check }) => {
      if (t.field === 'assessment' && c.verdict !== 'all' && check.verdict !== c.verdict) return false;
      if (t.field !== 'assessment') return true;
      const n = /^EPS-(\d+)$/.exec(check.id);
      return t.ref === 'extra' ? !n : Boolean(n && Math.floor((Number(n[1]) - 1) / 6) === Number(t.ref));
    }).map(({ check, index }) => entry(t, 'check', `${check.id}:${taskChecks(t,c).slice(0,index).filter(previous=>previous.id===check.id).length}`, `${check.id} · ${check.title}`, { index, text: JSON.stringify(check) }));
    case 'assumptions': return findings(w.analysis.simulation?.assumptions??[],'Assumption','run-assumption');
    case 'gaps': {
      const p=taskProduct(t,c);if (!p) return [];
      const coverage = productCoverage(p, selectedProductRole(t,c) ?? p.roles[0]);
      return findings([...coverage.identityIssues, ...coverage.core.filter(g => !g.covered).map(g => `${g.label}: ${g.issues.join('. ')}`), ...coverage.richer.filter(g => !g.covered).map(g => `${g.label}: ${g.issues.join('. ')}`), ...(w.analysis.suggestions?.find(s => s.productId === p.id && s.role === selectedProductRole(t,c))?.missing ?? [])],'Evidence gap');
    }
    case 'usages': return allocationGroups(w, c.catalog).map(g => entry(t, 'usage', g.id, `${g.ref} · ${g.product?.name ?? g.id}`));
    case 'migration': return findings(w.catalogReview??[],'Review reason');
    case 'kicad-blockers': return findings(getKiCadReadiness(w,c.catalog).blockers,'Prerequisite');
    case 'physical-gates': return findings(getKiCadReadiness(w,c.catalog).physicalGates,'Physical input');
    case 'kicad-warnings': return findings(getKiCadReadiness(w,c.catalog).warnings,'Export warning');
    case 'rule-warnings': return findings(c.ruleWarnings,'Rule warning');
    case 'analogues': return (c.missionResult?.matches ?? []).map(m => entry(t, 'analogue', m.mission.id, m.mission.name));
    default: return [];
  }
}
export const COLLECTION_KINDS = new Set(['case-description','case-provenance','query-text','prerequisites','loads','windows','catalog','role','specs','sources','basis','check-group','readiness','assumptions','gaps','usages','migration','kicad-blockers','physical-gates','kicad-warnings','rule-warnings','analogues','analogue-sources']);
export function related(t: FlowTask, c: TaskContext): FlowTask[] {
  const make = (kind: string, title: string, extra: Partial<FlowTask> = {}) => child(t, kind, title, extra);
  if (COLLECTION_KINDS.has(t.kind)) {
    const all = entries(t, c), chosen = all.find(e => e.id === c.picks[t.key]) ?? all[0];
    return chosen ? [chosen.task] : [];
  }
  if (t.kind === 'activity') {
    const specific: Record<NodeId, FlowTask[]> = {
      mission: [make('mission-search','Mission analogues'), make('receipt','Accepted altitude basis')],
      orbit: [make('orbit-numbers','Orbit numbers')],
      scenarios: [make('case-energy','Energy conditions'), make('loads','Loads'), make('preview','Load power preview'), make('case-description','Case description'), make('case-provenance','Case provenance')],
      budget: [make('demand','Demand history')],
      solar: [make('cell','Cell characterization'), make('installed','Installed source')],
      battery: [make('pack','Installed pack'), make('charge','Charge model'), make('discharge','Discharge model')],
      topology: [make('conditioning','Conditioning'), make('transfer','Energy transfer'), make('bus','Bus regulation'), make('resources','Resource assumptions')],
      candidates: [make('roles','Logical roles'), make('catalog','Product catalog'), make('usages','Product usages'), make('kicad','KiCad handoff'), ...(c.workspace.catalogReview?.length ? [make('migration','Catalog review')] : [])],
      simulation: [make('energy','Stored energy'), make('power','Generation & demand'), make('run-basis','Saved run basis'), make('assumptions','Run assumptions'), make('check-group','Run checks',{field:'simulation'})],
      assessment: ['EPS-01–06','EPS-07–12','EPS-13–18','EPS-19–20','Model screens'].map((title,i) => make('check-group',title,{field:'assessment',ref:i===4?'extra':String(i)})),
    };
    return [...specific[t.owner],make('basis','Input basis'),make('prerequisites','Readiness')];
  }
  switch (t.kind) {
    case 'roles': return (['solar','battery','conditioning','distribution','processor','software'] as Role[]).map(role => make('role',ROLE_NAMES[role],{role}));
    case 'load': return [make('load-power','Power states'),make('windows','Active windows')];
    case 'product': return [make('specs','Source ratings'),make('screen','Candidate screen'),make('allocation','Allocate product'),make('sources','Original sources')];
    case 'screen': return [make('gaps','Comparison gaps'),make('check-group','Screening checks',{field:'screen'})];
    case 'allocation': return [make('allocation-receipt','Frozen allocation receipt')];
    case 'usage': return taskProduct(t,c)?[make('product','Product evidence',{role:c.workspace.allocations?.find(r=>r.productId===t.ref)?.roles[0]??taskProduct(t,c)!.roles[0]})]:[];
    case 'spec': {
      const p=c.catalog.products.find(p=>p.id===t.field),s=p?.specs[t.ref!];
      return p&&s?p.sources.filter(source=>source.id===s.sourceId||s.additionalSourceIds?.includes(source.id)).map(s=>make('source',s.title,{ref:s.id,field:JSON.stringify(s)})):[];
    }
    case 'provenance': return [make('sources','Cited sources')];
    case 'check': return [make('sources','Cited evidence',{field:'check',text:t.text})];
    case 'kicad': return [make('kicad-blockers','Prerequisites'),make('physical-gates','Physical routing gates'),make('rules','Reviewed physical rules'),make('kicad-warnings','Export warnings')];
    case 'rules': return [make('rule-warnings','Rule validation warnings')];
    case 'mission-search': return [make('query-text','Query text'),make('analogues','Retrieved analogues')];
    case 'analogue': return [make('accept-altitude','Accept source altitude'),make('analogue-sources','Mission sources')];
    case 'receipt': return [make('sources','Receipt sources',{field:'mission-receipt'})];
    default: return [];
  }
}
/** Rebuild identities from live records. Never trust selected result snapshots. */
export function resolvePath(path: FlowTask[], c: TaskContext): FlowTask[] {
  const live:FlowTask[]=[];
  for(const previous of path) {
    const parent=live.at(-1);
    const candidates=parent?[...related(parent,c),...(COLLECTION_KINDS.has(parent.kind)?entries(parent,c).map(e=>e.task):[])]:roots;
    const current=candidates.find(task=>task.key===previous.key);
    if(current)live.push(current);else break;
  }
  return live;
}
export function visibleTasks(path: FlowTask[], c: TaskContext): FlowTask[] {
  const shown = new Map(roots.map(t => [t.key,t]));
  for (const task of resolvePath(path,c)) {shown.set(task.key,task);related(task,c).forEach(t=>shown.set(t.key,t));}
  for(const t of shown.values())taskPurpose(t.kind);
  return [...shown.values()];
}
export function activatePath(path: FlowTask[], task: FlowTask): FlowTask[] {
  if (task.kind === 'activity') return [task];
  const existing = path.findIndex(t=>t.key===task.key);
  if (existing>=0) return [...path.slice(0,existing),task];
  const parent = path.findIndex(t=>t.key===task.parent);
  return parent>=0 ? [...path.slice(0,parent+1),task] : path;
}
export function presentationEdges(tasks: FlowTask[]) {
  const keys=new Set(tasks.map(t=>t.key));
  return tasks.filter(t=>t.parent&&keys.has(t.parent)).map(t=>({id:`detail:${t.key}`,source:t.parent!,target:t.key,kind:'detail' as const}));
}
