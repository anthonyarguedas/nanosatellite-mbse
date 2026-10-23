import type { NodeId } from '../types';
import { NODE_DEFINITIONS } from '../workflow';
import type { FlowTask } from './flow-tasks';

export type FlowMode='horizontal'|'vertical';
export interface Point {x:number;y:number}
export interface Rect extends Point {width:number;height:number}
export const NODE_WIDTH=170, NODE_HEIGHT=108, SIBLING_GAP=28, LEVEL_GAP=64, CLUSTER_GAP=48, RANK_GAP=52;
const ORDER=['mission-search','receipt','orbit-numbers','case-energy','loads','preview','case-description','case-provenance','demand','cell','installed','pack','charge','discharge','conditioning','transfer','bus','resources','roles','catalog','usages','kicad','migration','energy','power','run-basis','assumptions','check-group','basis','prerequisites','load-power','windows','specs','screen','allocation','sources','query-text','analogues','accept-altitude','analogue-sources','kicad-blockers','physical-gates','rules','kicad-warnings','rule-warnings'];
const ROLES=['solar','battery','conditioning','distribution','processor','software'];
function compare(a:FlowTask,b:FlowTask) {
  return ORDER.indexOf(a.kind)-ORDER.indexOf(b.kind)||(ROLES.indexOf(a.role??'')-ROLES.indexOf(b.role??''))||a.key.localeCompare(b.key,undefined,{numeric:true});
}
export function rectsOverlap(a:Rect,b:Rect,gap=0) {return a.x<b.x+b.width+gap&&b.x<a.x+a.width+gap&&a.y<b.y+b.height+gap&&b.y<a.y+a.height+gap;}
export function boundsOf(rects:Rect[]):Rect {
  if(!rects.length)return {x:0,y:0,width:0,height:0};
  const x=Math.min(...rects.map(r=>r.x)),y=Math.min(...rects.map(r=>r.y));
  return {x,y,width:Math.max(...rects.map(r=>r.x+r.width))-x,height:Math.max(...rects.map(r=>r.y+r.height))-y};
}
export interface FlowLayout {mode:FlowMode;rects:Record<string,Rect>;clusters:Record<string,Rect>;bounds:Rect;signature:string}
/** Reserved tidy subtrees, then variable-sized activity clusters by calculation rank. */
export function layoutFlow(tasks:FlowTask[],mode:FlowMode):FlowLayout {
  const map=new Map(tasks.map(t=>[t.key,t])),children=new Map<string,FlowTask[]>();
  for(const t of tasks)if(t.parent&&map.has(t.parent)){const list=children.get(t.parent)??[];list.push(t);children.set(t.parent,list);}
  for(const list of children.values())list.sort(compare);
  const major=mode==='horizontal'?NODE_WIDTH:NODE_HEIGHT,minor=mode==='horizontal'?NODE_HEIGHT:NODE_WIDTH;
  const spans=new Map<string,number>(),depths=new Map<string,number>();
  const measure=(t:FlowTask,ancestors=new Set<string>()):number=>{
    if(ancestors.has(t.key))throw Error('Cyclic presentation tree');
    const next=new Set(ancestors).add(t.key),kids=children.get(t.key)??[];
    const span=Math.max(minor,kids.reduce((sum,k)=>sum+measure(k,next),0)+Math.max(0,kids.length-1)*SIBLING_GAP);
    spans.set(t.key,span);depths.set(t.key,kids.length?1+Math.max(...kids.map(k=>depths.get(k.key)!)):0);return span;
  };
  const ranks:Record<string,number>={};
  for(const n of NODE_DEFINITIONS)ranks[n.id]=n.dependencies.length?1+Math.max(...n.dependencies.map(id=>ranks[id])):0;
  const groups=Array.from({length:1+Math.max(...Object.values(ranks))},()=>[] as FlowTask[]);
  for(const n of NODE_DEFINITIONS){const t=map.get(n.id);if(t){measure(t);groups[ranks[n.id]].push(t);}}
  const rects:Record<string,Rect>={},clusters:Record<string,Rect>={};
  const box=(a:number,b:number,ma=major,mi=minor):Rect=>mode==='horizontal'?{x:a,y:b,width:ma,height:mi}:{x:b,y:a,width:mi,height:ma};
  const place=(t:FlowTask,a:number,b:number)=>{rects[t.key]=box(a,b);let offset=b;for(const k of children.get(t.key)??[]){place(k,a+major+LEVEL_GAP,offset);offset+=spans.get(k.key)!+SIBLING_GAP;}};
  let start=0;
  for(const group of groups){let offset=0,maxExtent=major;for(const t of group){const extent=major+depths.get(t.key)!*(major+LEVEL_GAP);place(t,start,offset);clusters[t.key]=box(start,offset,extent,spans.get(t.key)!);offset+=spans.get(t.key)!+CLUSTER_GAP;maxExtent=Math.max(maxExtent,extent);}start+=maxExtent+RANK_GAP;}
  return {mode,rects,clusters,bounds:boundsOf(Object.values(rects)),signature:JSON.stringify([mode,...Object.entries(rects).sort(([a],[b])=>a.localeCompare(b))])};
}
export function ownerOf(tasks:FlowTask[],key:string|null):NodeId|undefined{return tasks.find(t=>t.key===key)?.owner;}
