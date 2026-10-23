import { memo, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { Background, BackgroundVariant, Handle, MarkerType, Position, ReactFlow, type Node, type NodeProps, type ReactFlowInstance } from '@xyflow/react';
import { Activity, BatteryCharging, Focus, Home, Minus, Orbit, PackageSearch, Plus, ShieldCheck, SlidersHorizontal, Sun, Workflow, FileText, ChevronRight } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { NodeId, NodeStatus, Workspace } from '../types';
import { ACTIVITY_LABELS, activityEdges, activityValue, hasResult, savedPrefix } from './design-canvas-model';
import { presentationEdges, taskPurpose, type FlowTask } from './flow-tasks';
import { layoutFlow, NODE_HEIGHT, NODE_WIDTH, ownerOf, type FlowLayout } from './flow-layout';
import { routeFlow, type Port } from './flow-routing';
import { ensureVisibleViewport, focusViewport, frameViewport, type CanvasSize } from './flow-camera';
import { FlowInformationEdge, type InformationEdge } from './FlowInformationEdge';
import { engineeringExchange } from './engineering-exchanges';
import { labelFullyVisible, placeRouteLabels } from './flow-labels';
import { STATUS_LABELS } from './ui';
import '@xyflow/react/dist/style.css';

const ICONS: Record<NodeId, LucideIcon> = { mission: Orbit, orbit: Orbit, scenarios: SlidersHorizontal, budget: Activity, solar: Sun, battery: BatteryCharging, topology: Workflow, candidates: PackageSearch, simulation: Activity, assessment: ShieldCheck };
const SIDES={left:Position.Left,right:Position.Right,top:Position.Top,bottom:Position.Bottom};
type Data={task:FlowTask;workspace:Workspace;status:NodeStatus;active:boolean;ports:Port[];origin:{x:number;y:number};onSelect:(t:FlowTask)=>void;reveal:(key:string)=>void};
type FlowNode=Node<Data,'epsActivity'>;
const TaskView=memo(function TaskView({data}:NodeProps<FlowNode>){
  const t=data.task,root=t.kind==='activity',purpose=taskPurpose(t.kind),Icon=root?ICONS[t.owner]:purpose==='work'?SlidersHorizontal:FileText;
  const historical=root?savedPrefix(data.status,hasResult(t.owner,data.workspace)):'';
  const review=root&&t.owner==='candidates'&&Boolean(data.workspace.catalogReview?.length);
  return <>{data.ports.map(port=><Handle key={port.id} id={port.id} type={port.type} position={SIDES[port.side]} isConnectable={false} className="information-anchor" style={{left:port.x-data.origin.x,top:port.y-data.origin.y}}/>)}
    <button className={`graph-activity nodrag nopan ${root?data.status:'detail-task'} ${data.active?'is-selected':''}`} data-activity={root?t.owner:undefined} data-task={t.key} data-task-kind={t.kind}
      aria-pressed={data.active} aria-label={`${t.title}${root?`. ${STATUS_LABELS[data.status]}. ${review?'Catalog review needed. ':''}${historical}${activityValue(t.owner,data.workspace)}`:`. ${purpose==='work'?'Work task':'Review record'}`}`}
      onClick={()=>data.onSelect(t)} onFocus={()=>data.reveal(t.key)}>
      <span className="graph-node-top"><Icon size={21} strokeWidth={1.6}/>{root?<span className={`graph-freshness ${data.status}`} title={STATUS_LABELS[data.status]}/>:<ChevronRight size={13}/>}</span>
      <strong>{root?ACTIVITY_LABELS[t.owner]:t.title}</strong><span className={`graph-node-value ${historical?'historical':''}`}>{review?`Catalog review needed · ${data.workspace.catalogReview!.length} reasons`:root?`${historical}${activityValue(t.owner,data.workspace)}`:purpose==='work'?'Edit / decide':'Review'}</span>
    </button></>;
});
const NODE_TYPES={epsActivity:TaskView},EDGE_TYPES={information:FlowInformationEdge};
function overviewViewport(layout:FlowLayout,size:CanvasSize){
  const frame=frameViewport(layout.bounds,size,1.04);
  if(layout.mode==='vertical'&&frame.zoom<.85)return {x:Math.max(16,(size.width-layout.bounds.width*.85)/2),y:32,zoom:.85};
  return frame;
}
/** Calculation/evidence relations come only from the controller. Detail is containment. */
export function WorkbenchGraph({workspace,statuses,tasks,selected,onSelect,onHome}:{workspace:Workspace;statuses:Record<NodeId,NodeStatus>;tasks:FlowTask[];selected:string|null;onSelect:(task:FlowTask)=>void;onHome:()=>void}){
  const container=useRef<HTMLDivElement>(null);
  const [size,setSize]=useState({width:0,height:0}),[windowWidth,setWindowWidth]=useState(()=>typeof window==='undefined'?1440:window.innerWidth);
  const [flow,setFlow]=useState<ReactFlowInstance<FlowNode,InformationEdge>|null>(null),[zoom,setZoom]=useState(100),[showAll,setShowAll]=useState(false);
  const [viewport,setViewport]=useState({x:0,y:0,zoom:1});
  const mode=windowWidth>=1000?'horizontal':'vertical';
  const structure=JSON.stringify(tasks.map(t=>[t.key,t.parent,t.kind,t.owner,t.role]));
  const layout=useMemo(()=>layoutFlow(tasks,mode),[structure,mode]);
  const relations=useMemo(()=>[...activityEdges(),...presentationEdges(tasks)],[structure]);
  const routes=useMemo(()=>routeFlow(layout,relations),[layout,relations]);
  const labels=useMemo(()=>placeRouteLabels(routes,layout.rects,r=>engineeringExchange(r.source as NodeId,r.target as NodeId).label),[routes,layout]);
  useEffect(()=>{
    const update=()=>setWindowWidth(window.innerWidth);window.addEventListener('resize',update);
    const observer=new ResizeObserver(([entry])=>setSize({width:entry.contentRect.width,height:entry.contentRect.height}));
    if(container.current)observer.observe(container.current);
    return ()=>{observer.disconnect();window.removeEventListener('resize',update);};
  },[]);
  const fit=useCallback(()=>{if(flow&&size.width&&size.height)void flow.setViewport(selected?focusViewport(layout,tasks,selected,size):overviewViewport(layout,size));},[flow,layout,selected,size.width,size.height]);
  const previous=useRef<{selected:string|null;mode:string;width:number;height:number}|null>(null);
  useLayoutEffect(()=>{
    if(!flow||!size.width||!size.height)return;
    const measured=container.current?{width:container.current.clientWidth,height:container.current.clientHeight}:size;
    const before=previous.current;
    previous.current={selected,mode,width:measured.width,height:measured.height};
    if(!before||before.selected!==selected||before.mode!==mode){
      void flow.setViewport(selected?focusViewport(layout,tasks,selected,measured):overviewViewport(layout,measured));
    }else if(selected&&(before.width!==measured.width||before.height!==measured.height)){
      void flow.setViewport(ensureVisibleViewport(layout.rects[selected],measured,flow.getViewport(),32));
    }
  },[flow,selected,mode,layout.signature,size.width,size.height]);
  const reveal=(key:string)=>{const rect=layout.rects[key];if(flow&&rect)void flow.setViewport(ensureVisibleViewport(rect,size,flow.getViewport()));};
  const ports=new Map<string,Port[]>();for(const r of routes)for(const p of [r.sourcePort,r.targetPort])ports.set(p.node,[...ports.get(p.node)??[],p]);
  const nodes:FlowNode[]=tasks.map(task=>{const r=layout.rects[task.key],pp=ports.get(task.key)??[];return {id:task.key,type:'epsActivity',position:{x:r.x,y:r.y},width:NODE_WIDTH,height:NODE_HEIGHT,draggable:false,connectable:false,selectable:false,focusable:false,
    handles:pp.map(p=>({id:p.id,type:p.type,position:SIDES[p.side],x:p.x-r.x,y:p.y-r.y,width:1,height:1})),data:{task,workspace,status:statuses[task.owner],active:selected===task.key,ports:pp,origin:r,onSelect,reveal}};});
  const owner=ownerOf(tasks,selected),selectedPath=new Set<string>();let current=tasks.find(t=>t.key===selected);while(current){selectedPath.add(current.key);current=tasks.find(t=>t.key===current?.parent);}
  const edges:InformationEdge[]=routes.filter(e=>e.kind==='detail'||e.primary||showAll||e.source===owner||e.target===owner).map<InformationEdge>(route=>{
    const detail=route.kind==='detail',evidence=route.kind==='evidence',linked=detail?selectedPath.has(route.target):selected===owner&&(route.source===owner||route.target===owner);
    const exchange=detail?undefined:engineeringExchange(route.source as NodeId,route.target as NodeId),label=labels[route.id];
    const color=detail?(linked?'#e8bc95':'#a8b9c5'):evidence?'#85cbd0':linked?'#efb183':'#9caebb';
    return {id:route.id,source:route.source,target:route.target,type:'information',sourceHandle:route.sourcePort.id,targetHandle:route.targetPort.id,focusable:false,selectable:false,
      className:`information-edge ${route.kind}`,markerEnd:detail?undefined:{type:MarkerType.ArrowClosed,width:13,height:13,color},
      style:{stroke:color,strokeWidth:linked?2:1.3,strokeDasharray:detail?'2 4':evidence?'7 5':undefined,opacity:!detail&&selected&&selected!==owner ? .55 : 1},
      data:{route,accessibleLabel:detail?'Task detail, no calculation dependency':`${exchange!.label}: ${exchange!.description}`,label:linked&&!detail&&label&&labelFullyVisible(label.rect,size,viewport)?label:undefined}};
  }).sort((a,b)=>Number(a.style?.strokeWidth)-Number(b.style?.strokeWidth));
  return <section className="mission-flow" aria-label="Engineering flow">
    <div className="graph-toolbar"><h1 id="canvas-heading" tabIndex={-1}>Engineering flow</h1><div className="graph-tools" role="group" aria-label="Canvas view">
      <button className="icon-button" aria-label="Engineering overview" data-action="flow-home" onClick={()=>{onHome();if(flow)void flow.setViewport(overviewViewport(layoutFlow(tasks.filter(t=>t.kind==='activity'),mode),size));}}><Home size={16}/></button>
      <button className="icon-button" aria-label="Zoom out" onClick={()=>void flow?.zoomOut()}><Minus size={15}/></button><span className="graph-zoom">{zoom}%</span><button className="icon-button" aria-label="Zoom in" onClick={()=>void flow?.zoomIn()}><Plus size={15}/></button>
      <button className="graph-fit" aria-label={selected?'Fit focused branch':'Fit engineering overview'} onClick={fit}><Focus size={15}/>Fit</button>
    </div></div>
    {selected&&<div className="graph-branch-context" aria-label="Focused branch">{[...selectedPath].reverse().map(key=><button key={key} onClick={()=>onSelect(tasks.find(t=>t.key===key)!)}>{tasks.find(t=>t.key===key)?.title}</button>)}</div>}
    <div className="activity-workspace" ref={container} tabIndex={0} aria-label="Engineering graph. Drag to pan. Tab to nodes. Arrow keys pan when the canvas is focused." data-layout={mode} onKeyDown={event=>{
      if(event.target!==event.currentTarget||!flow||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
      event.preventDefault();const v=flow.getViewport();void flow.setViewport({...v,x:v.x+(event.key==='ArrowLeft'?70:event.key==='ArrowRight'?-70:0),y:v.y+(event.key==='ArrowUp'?70:event.key==='ArrowDown'?-70:0)});
    }}>
      <ReactFlow<FlowNode,InformationEdge> nodes={nodes} edges={edges} nodeTypes={NODE_TYPES} edgeTypes={EDGE_TYPES} onInit={setFlow} onMove={(_,v)=>{setZoom(Math.round(v.zoom*100));setViewport(v);}}
        nodesDraggable={false} nodesConnectable={false} edgesReconnectable={false} connectOnClick={false} elementsSelectable={false} edgesFocusable={false} nodesFocusable={false}
        deleteKeyCode={null} selectionKeyCode={null} multiSelectionKeyCode={null} panActivationKeyCode={null} zoomActivationKeyCode={null} minZoom={.3} maxZoom={1.6} zoomOnDoubleClick={false} preventScrolling={false} proOptions={{hideAttribution:true}}>
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#35424e"/>
      </ReactFlow>
    </div>
    <div className="information-legend"><span><i/>Calculation input</span><span><i className="optional"/>Optional evidence</span><span><i className="detail"/>Task detail</span><button className="relationship-toggle" aria-pressed={showAll} onClick={()=>setShowAll(v=>!v)}>Show all relationships</button><span>Information, not power wiring</span></div>
    <ul className="sr-only" aria-label="Engineering relationships">{relations.map(e=><li key={e.id} data-edge={e.id} data-edge-kind={e.kind}>{e.source} → {e.target}: {e.kind==='detail'?'task detail, no calculation dependency':e.kind==='evidence'?'optional evidence, not a required dependency':'calculation input'}{e.kind!=='detail'&&` · ${engineeringExchange(e.source as NodeId,e.target as NodeId).label}: ${engineeringExchange(e.source as NodeId,e.target as NodeId).description}`}</li>)}</ul>
  </section>;
}
