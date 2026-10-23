import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ArrowDownToLine, ArrowUpFromLine, ChevronDown, CircleHelp, FilePlus2, FolderOpen, RefreshCw, X } from 'lucide-react';
import { catalog } from './data/catalog';
import { useWorkspace } from './state/workspace';
import { restoreWorkspace } from './state/serialization';
import type { Workspace } from './types';
import { DesignCanvas } from './components/DesignCanvas';
import { FlowTaskPane } from './components/FlowTaskPane';
import { DEFAULT_CATALOG_FILTERS, type CatalogFilters } from './components/CatalogView';
import { activatePath, resolvePath, roots, visibleTasks, type FlowTask, type TaskContext } from './components/flow-tasks';
import { useMissionSession } from './components/mission-session';
import { useKiCadSession } from './components/kicad-session';
import { Sheet, SheetNavigationContext, useNarrowInspector } from './components/ui';
import './components/design-canvas.css';

export default function App() {
  const api=useWorkspace();
  const [path,setPath]=useState<FlowTask[]>([]), [open,setOpen]=useState(false);
  const [externalTask,setExternalTask]=useState<FlowTask|null>(null);
  const [picks,setPicks]=useState<Record<string,string>>({});
  const [filters,setFilters]=useState<CatalogFilters>(DEFAULT_CATALOG_FILTERS);
  const [verdict,setVerdict]=useState('all');
  const [notice,setNotice]=useState<string|null>(null);
  const [generation,setGeneration]=useState(0);
  const pendingImport=useRef<Workspace|null>(null);
  const project=useRef<HTMLDetailsElement>(null), importInput=useRef<HTMLInputElement>(null);
  const background=useRef<HTMLDivElement>(null), header=useRef<HTMLElement>(null);
  const returnFocus=useRef<HTMLElement|null>(null);
  const narrow=useNarrowInspector();
  const queryChange=useCallback((conOps:string)=>api.updateInputs('mission',current=>({...current,mission:{...current.mission,conOps}})),[api.updateInputs]);
  const mission=useMissionSession(api.workspace.inputs.mission.conOps??'',queryChange,generation);
  const kicad=useKiCadSession(api.workspace,catalog,generation);
  const context:TaskContext=useMemo(()=>({workspace:api.workspace,catalog,picks,filters,missionResult:mission.result,ruleWarnings:kicad.rules?.result.warnings??[],verdict}),[api.workspace,picks,filters,mission.result,kicad.rules,verdict]);
  const livePath=useMemo(()=>resolvePath(path,context),[path,context]);
  const tasks=useMemo(()=>visibleTasks(livePath,context),[livePath,context]);
  const selected=externalTask??livePath.at(-1);
  const select=(task:FlowTask)=>{setExternalTask(null);returnFocus.current=document.activeElement as HTMLElement;setPath(previous=>activatePath(resolvePath(previous,context),task));setOpen(true);};
  const root=(id:FlowTask['owner'])=>{setExternalTask(null);const task=roots.find(t=>t.owner===id)!;returnFocus.current=document.querySelector<HTMLElement>(`[data-activity="${id}"]`);setPath([task]);setOpen(true);};
  const home=()=>{setPath([]);setExternalTask(null);setOpen(false);};
  const close=()=>{setOpen(false);setExternalTask(null);window.setTimeout(()=>{if(returnFocus.current?.isConnected)returnFocus.current.focus();else document.querySelector<HTMLElement>(`[data-task=${JSON.stringify(selected?.key)}]`)?.focus();},0);};
  const back=()=>{if(externalTask)close();else if(livePath.length>1)setPath(livePath.slice(0,-1));else close();};
  const resetPresentation=()=>{mission.reset();kicad.reset();setGeneration(value=>value+1);home();setPicks({});setFilters(DEFAULT_CATALOG_FILTERS);setVerdict('all');};
  useEffect(()=>{
    const before=pendingImport.current;
    if(!before)return;
    if(api.error){pendingImport.current=null;return;}
    if(api.workspace!==before){pendingImport.current=null;resetPresentation();}
  },[api.workspace,api.error]);
  const importDesign=async(file:File)=>{
    // The controller catches import errors internally. Reuse its canonical
    // parser to arm replacement detection only for valid input. A failed import
    // keeps the current context and is still reported by the controller.
    pendingImport.current=null;
    try{if(file.size<=2_000_000){restoreWorkspace(JSON.parse(await file.text()));pendingImport.current=api.workspace;}}catch{/* api.restore owns error reporting. */}
    await api.restore(file);
  };
  const external=(kind:string,title:string)=>{project.current?.removeAttribute('open');returnFocus.current=project.current?.querySelector('summary')??null;setExternalTask({key:`ui:project:${kind}`,kind,title,owner:'mission'});setOpen(true);};
  useEffect(()=>{if(background.current)background.current.inert=open&&narrow;if(header.current)header.current.inert=open&&narrow;},[open,narrow]);
  useEffect(()=>{if(!notice)return;const timer=window.setTimeout(()=>setNotice(null),6000);return()=>window.clearTimeout(timer);},[notice]);
  // Removed records never leave an orphan form. Selection falls back to a surviving collection.
  useEffect(()=>{
    if(!selected)return;
    const scenario=api.activeScenario;
    const loadId=selected.kind==='window'?selected.field:selected.ref;
    const invalidLoad=['load','load-power','windows','window'].includes(selected.kind)&&!scenario?.loads.some(l=>l.id===loadId);
    const invalidWindow=selected.kind==='window'&&!scenario?.loads.find(l=>l.id===loadId)?.windows.some(w=>w.id===selected.ref);
    if(invalidLoad||invalidWindow)setPath(previous=>previous.slice(0,Math.max(1,previous.length-1)));
  },[api.activeScenario,selected]);
  const finishReplace=(example:boolean)=>{pendingImport.current=null;resetPresentation();if(example)api.loadExample();else api.reset();setNotice(example?'BIRDS-4-inspired study loaded. Numerical EPS assumptions and COTS substitutions are illustrative.':'New design created. Select Define mission to begin.');};
  const confirmation=selected?.kind==='project-new'||selected?.kind==='project-example';
  return <div className="canvas-app" data-inspector-open={open||undefined}>
    <a className="skip-to-canvas" href="#canvas-heading">Skip to engineering flow</a>
    <header className="canvas-header" ref={header}><a className="canvas-brand" href="#canvas-heading" aria-label="Orbitwork engineering flow">◉ <span>orbitwork.</span></a><span className="canvas-mission-name" title={api.workspace.inputs.mission.name}>{api.workspace.inputs.mission.name}</span>
      <details className="project-menu" ref={project} onKeyDown={e=>{if(e.key==='Escape'){e.preventDefault();project.current?.removeAttribute('open');project.current?.querySelector('summary')?.focus();}}}><summary>Project<ChevronDown size={13}/></summary><div className="project-menu-content">
        <button data-action="recalculate" onClick={()=>{api.runAll();project.current?.removeAttribute('open');setNotice('Available activities recalculated in dependency order.');}}><RefreshCw size={15}/>Recalculate available activities</button>
        <button data-action="export" onClick={()=>{api.download();project.current?.removeAttribute('open');}}><ArrowDownToLine size={15}/>Export design JSON</button>
        <button data-action="import" onClick={()=>{project.current?.removeAttribute('open');importInput.current?.click();}}><ArrowUpFromLine size={15}/>Import design JSON</button>
        <hr/><button data-action="load-example" onClick={()=>external('project-example','Load the example design?')}><FolderOpen size={15}/>Load BIRDS-4-inspired example</button><button data-action="new-design" onClick={()=>external('project-new','Start a new design?')}><FilePlus2 size={15}/>New design</button><hr/><button data-action="project-scope" onClick={()=>external('help','Scope & help')}><CircleHelp size={15}/>Scope & help</button>
      </div></details><input ref={importInput} className="sr-only" tabIndex={-1} type="file" accept=".json,application/json" aria-label="Import design file" onChange={async e=>{const file=e.target.files?.[0];e.target.value='';if(file)await importDesign(file);}}/>
    </header>
    <div className="canvas-workspace"><div className="canvas-background" ref={background}><main className="canvas-main"><DesignCanvas api={api} tasks={tasks} selected={livePath.at(-1)?.key??null} onSelect={select} onHome={home}/></main></div>
      {open&&selected&&<div className="context-host" data-modal={narrow} key={selected.key}><SheetNavigationContext.Provider value={{modal:narrow,nested:!externalTask&&livePath.length>1,backLabel:!externalTask&&livePath.length>1?`Back to ${livePath[livePath.length-2].title}`:undefined,onDismiss:close}}>
        {confirmation?<Sheet title={selected.title} eyebrow="REPLACE LOCAL WORKSPACE" onClose={back} footer={<div className="task-actions"><button className="button secondary" onClick={close}>Keep current design</button><button className="button primary" data-action={selected.kind==='project-new'?'confirm-new-design':'confirm-load-example'} onClick={()=>finishReplace(selected.kind==='project-example')}>{selected.kind==='project-new'?'Create new design':'Load example'}</button></div>}><p className="body-copy">Your local workspace will be replaced. Export first to retain authored inputs, source records, allocations and results.</p><button className="button secondary" onClick={api.download}><ArrowDownToLine size={14}/>Export current design</button><p className="body-copy">The example is a preliminary concept study. The new design begins with undefined inputs and unallocated logical roles.</p></Sheet>:<FlowTaskPane task={selected} context={context} api={api} mission={mission} kicad={kicad} onPick={(key,value)=>setPicks(previous=>({...previous,[key]:value}))} onFilters={setFilters} onVerdict={setVerdict} onRoot={root} onClose={back}/>}
      </SheetNavigationContext.Provider></div>}
    </div>
    {(api.error||notice)&&<div className={`app-notification ${api.error?'error':''}`} role={api.error?'alert':'status'}><span>{api.error??notice}</span><button className="icon-button" aria-label="Dismiss notification" onClick={()=>{api.clearError();setNotice(null);}}><X size={16}/></button></div>}
  </div>;
}
