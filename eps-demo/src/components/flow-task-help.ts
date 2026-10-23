import type { Check, NodeId, Source } from '../types';
import { NODE_DEFINITIONS, descendants, nodeStatuses } from '../workflow';
import { legacyArrayForm } from '../catalog/validation';
import { catalogCoverage } from '../catalog/coverage';
import { COMPARISON_SCOPE } from '../catalog/profiles';
import { BIRDS4_EXAMPLE_BASIS } from '../data/birds4';
import { ACTIVITY_LABELS, CSRM_SUBSYSTEMS } from './design-canvas-model';
import { SCOPES } from './NodeInspector';
import { stepsFor } from './CalculationTrace';
import { engineeringExchange, exchangeValue } from './engineering-exchanges';
import { specValue } from './CatalogView';
import { selectedProductRole, taskProduct, type FlowTask, type TaskContext } from './flow-tasks';
import { ROLE_NAMES, STATUS_LABELS } from './ui';

export interface HelpField { label: string; value: string }
export interface HelpSection { id: string; title: string; paragraphs?: string[]; fields?: HelpField[]; items?: string[]; links?: {label:string;url:string}[]; upstream?: NodeId[] }
const field=(label:string,value:unknown):HelpField=>({label,value:value===undefined||value===null?'Not recorded.':typeof value==='string'?value:JSON.stringify(value,null,2)});
const sourceLink=(s:Source)=>({label:s.title,url:s.url});
const METHOD_SOURCES='Orbit and preliminary sizing follow the design proposal and El Hachimi et al., Sections 2–3. CSRM composition and variation points follow the report. This prototype does not implement formal phase reviews, SysML execution, detailed circuits, MIL/SIL, F Prime or hardware qualification.';
const SCHEDULING='Drag the middle to move a window or an edge to resize. Arrow keys use 1%, Shift uses 0.1%. Home and End reach bounds. Escape cancels a drag. Numeric start/end provide exact timing. Minimum width is 0.1%. Overlapping windows form one interval. Split a window at 100% to cross the orbit boundary. Essential and rail fields are metadata. Automatic shedding, thermal behavior and charge state remain outside this model.';
export const PROJECT_HELP: HelpSection[]=[{id:'project',title:'Scope & help',fields:[
  field('Model scope','Local preliminary CubeSat EPS study. Energy-only results do not establish charge state, detailed wiring, protection, fit, formal acceptance or flight qualification.'),
  field('Freshness & evidence','Edits preserve historical results and invalidate dependent calculations. Current means evaluated inputs, not verification. Known violations fail. Missing decisive evidence stays unassessed. Only the selected scenario is evaluated.'),
  field('Local storage & JSON','Authored inputs and allocations persist locally. Export JSON before replacing work. Reload and JSON import discard calculation caches. Sources, provenance and frozen receipts are retained.'),
  field('Mission assistance scope','Optional semantic retrieval uses a local service. Lexical retrieval runs offline. Similarity is a rank. Altitude transfer requires explicit acceptance.'),
]}];
/** Live contextual content has section IDs, never graph identities or snapshots. */
export function helpSections(t:FlowTask,c:TaskContext):HelpSection[] {
  const w=c.workspace,p=taskProduct(t,c),sections:HelpSection[]=[];
  const add=(id:string,title:string,rest:Omit<HelpSection,'id'|'title'>)=>sections.push({id,title,...rest});
  if(t.kind==='activity') {
    const n=NODE_DEFINITIONS.find(n=>n.id===t.owner)!,statuses=nodeStatuses(w);
    add('method','Method & evidence',{fields:[field('Equation',n.equation),field('Scope',SCOPES[t.owner]),field('Requirements',n.requirements.join(', ')||'No direct EPS predicate'),field('Last run',w.records[t.owner].evaluatedAt??'Not evaluated'),...stepsFor(t.owner,w).flatMap(s=>[field(`${s.label} · inputs`,s.inputs),field(`${s.label} · relation`,s.relation),field(`${s.label} · ${statuses[t.owner]==='stale'?'historical output':'output'}`,s.output)]),...n.dependencies.flatMap(source=>{const e=engineeringExchange(source,t.owner);return [field(`Received from ${ACTIVITY_LABELS[source]} · ${e.label}`,`${STATUS_LABELS[statuses[source]]}\n${exchangeValue(source,t.owner,w)}\n${e.description}`)];}),field('Change impact','Edits invalidate the existing dependency/evidence closure. UI navigation changes no revision.\n'+descendants(t.owner).filter(id=>id!==t.owner).map(id=>ACTIVITY_LABELS[id]).join('\n')),field('Method sources',METHOD_SOURCES)],upstream:n.dependencies,paragraphs:statuses[t.owner]==='stale'?['Current inputs are shown. Saved outputs are historical. Recompute before deriving their current output.']:[]});
    if(t.owner==='mission'||t.owner==='topology')add('reference','Reference context',{paragraphs:['Mission / Space Segment / CubeSat / EPS','Space Segment has CubeSats [1..*] and CubeSat Orbits [1..*]. Each CubeSat has one reference orbit. This demo models one spacecraft EPS and one circular orbit. Six EPS groups are logical categories. Reference [1] establishes no installed quantities or connections.','CubeSat · nine subsystem categories [1] each','Ground Segment [1] is reference only. External context includes environment, constraints, ground station services, transport, launch and deployment, and GNSS. Ground-system and constellation behavior remain outside this demo.','CSRM structure adapted from INCOSE Space Systems Working Group / OMG Space Domain Task Force. Logical categories can be omitted, combined or refined for a mission.'],items:[...CSRM_SUBSYSTEMS],links:[{label:'Creative Commons Attribution 4.0',url:'https://creativecommons.org/licenses/by/4.0/'}]});
    if(t.owner==='mission')add('study','Study basis',{paragraphs:['BIRDS-4-inspired concept study. Mission activities are sourced. Numerical schedules, lifetime, energy assumptions and COTS substitutions are illustrative.',BIRDS4_EXAMPLE_BASIS.limits],items:[...BIRDS4_EXAMPLE_BASIS.missionFacts],links:[{label:`${BIRDS4_EXAMPLE_BASIS.source.title} · ${BIRDS4_EXAMPLE_BASIS.source.locations}`,url:BIRDS4_EXAMPLE_BASIS.source.url}]});
    if(t.owner==='topology')sections[0].fields!.push(field('Per-output scope','Direct bus and DC–DC converted supply may coexist. Per-rail choices, conversion envelopes and verified wiring are not represented in this model.'));
  }
  switch(t.kind) {
    case 'load': case 'window': add('schedule','Scheduling help',{paragraphs:[SCHEDULING]});break;
    case 'mission-search': add('retrieval','Retrieval scope',{paragraphs:['Text alone cannot determine a unique orbit. Semantic retrieval uses the optional local Qwen service. Lexical TF-IDF works offline and uses word overlap. A service failure requires explicit lexical selection. Launch, revisit, resolution and orbital suitability need independent analysis. EPS geometry remains circular with no SSO, J2, beta angle or seasonal propagation.']});break;
    case 'catalog': add('coverage','Catalog coverage',{paragraphs:[COMPARISON_SCOPE],items:catalogCoverage(c.catalog).roles.map(r=>`${ROLE_NAMES[r.role]}: ${r.coveredOptions}/${r.distinctOptions} distinct options covered. Target deficit ${r.deficit}.`)});break;
    case 'product': if(p)add('product','Product evidence & scope',{fields:[field('Complete product description',p.description),field('Accounting boundary',p.accountingBoundary)],items:[...(p.supportedConfigurations??[]).map(s=>`Configuration: ${s}`),...(p.caveats??[]).map(s=>`Caveat: ${s}`)]});break;
    case 'screen': if(p)add('screen','Screen evidence',{fields:[field('Screen reason',w.analysis.suggestions?.find(s=>s.productId===p.id&&s.role===selectedProductRole(t,c))?.reason??'No current role-specific suggestion.')]});break;
    case 'spec': {
      const product=c.catalog.products.find(p=>p.id===t.field),s=product?.specs[t.ref!];
      if(s&&product)add('property','Property evidence',{fields:[field('Property value',specValue({...s,valueForm:s.valueForm??legacyArrayForm(product,t.ref!)})),field('Status',s.status),field('Meaning',s.meaning),field('Value form',s.valueForm??legacyArrayForm(product,t.ref!)??'scalar'),field('Units',s.unit),field('Original representation',s.original||'No original value published.'),field('Operating conditions',s.conditions||'Conditions not specified.'),field('Rationale',s.rationale),field('Source location',s.location||'Not specified'),field('Source references',[s.sourceId,...s.additionalSourceIds??[]].filter(Boolean).join(', ')),field('Complete property record',s)],links:product.sources.filter(src=>src.id===s.sourceId||s.additionalSourceIds?.includes(src.id)).map(sourceLink)});
      break;
    }
    case 'source': {
      const s=JSON.parse(t.field??'{}') as Source&{quotes?:string[]};
      add('source','Source evidence',{fields:[field('Full source metadata',s),field('Full source URL',s.url),field('Source location',s.location),...(s.quotes??[]).map((quote,i)=>field(`Quote ${i+1}`,quote))],links:s.url?[sourceLink(s)]:[]});break;
    }
    case 'provenance': {
      const r=w.provenance?.find(r=>r.parameter===t.ref);
      if(r)add('provenance','Input evidence',{fields:[field('Rationale',r.rationale),field('Conditions',r.conditions),field('Evidence references',r.sourceIds.join(', ')),field('Complete provenance record',r)]});break;
    }
    case 'check': {
      const check=JSON.parse(t.text??'{}') as Check;
      add('criterion','Criterion & evidence',{fields:[field('Criterion detail',check.detail),field('Scope & equation',`${check.equation??'No numerical equation.'}\n${check.scope??'Scope not recorded.'}`),field('Evidence references',check.sourceIds?.join(', ')||'No source references recorded.'),field('Complete check record',check)]});break;
    }
    case 'allocation-receipt': case 'usage': {
      const r=w.allocations?.find(r=>r.productId===t.ref);
      add('allocation','Allocation evidence',{fields:[field('Allocation rationale',r?.rationale??'No frozen allocation receipt.'),field('Complete allocation receipt',r)]});break;
    }
    case 'receipt': {
      const r=w.inputs.mission.orbitSuggestion;
      add('receipt','Acceptance evidence',{fields:[field('Complete acceptance receipt',r??{}),field('Accepted parameter meaning',r?.parameterMeaning),field('Accepted query',r?.query)]});break;
    }
    case 'analogue': {
      const match=c.missionResult?.matches.find(m=>m.mission.id===t.ref),m=match?.mission;
      if(m&&match)add('analogue','Mission evidence',{fields:[field('Retrieval evidence',`${match.method} cosine ${match.score}\nMatched terms: ${match.matchedTerms.join(', ')}\nCatalogue ${match.catalogueRevision}\nDescription sources: ${m.descriptionSourceIds.join(', ')}`),field('Mission description',m.description),field('Mission identity & status',`${m.identity}\n${m.epoch}\n${m.statusDetail}`),...Object.entries(m.orbit).map(([key,p])=>field(key,p?`${p.original}\n${p.meaning}\nSources: ${p.sourceIds.join(', ')}\nValue: ${JSON.stringify(p.value)}`:'Missing from this reviewed record.'))],items:m.caveats,links:m.sources.map(sourceLink)});break;
    }
    case 'kicad': add('pipeline','Review pipeline',{items:['Freeze exact allocations, revisions and source records. Integrated roles share one usage.','Place sheets and route logical associations. Retain unresolved associations in the manifest.','Inspect in KiCad. The exported README supplies the local validation command.'],paragraphs:['Electrical checks on opaque sheets do not assess the actual COTS circuit. Physical routing remains gated.']});break;
  }
  return sections;
}
