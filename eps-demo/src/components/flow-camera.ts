import type { FlowTask } from './flow-tasks';
import { boundsOf, type FlowLayout, type Rect } from './flow-layout';
export interface Viewport {x:number;y:number;zoom:number}
export interface CanvasSize {width:number;height:number}
export function frameViewport(rect:Rect,size:CanvasSize,maxZoom=1):Viewport {
  const zoom=Math.max(.3,Math.min(maxZoom,(size.width-64)/Math.max(1,rect.width),(size.height-64)/Math.max(1,rect.height)));
  return {x:(size.width-rect.width*zoom)/2-rect.x*zoom,y:(size.height-rect.height*zoom)/2-rect.y*zoom,zoom};
}
export function focusViewport(layout:FlowLayout,tasks:FlowTask[],selected:string,size:CanvasSize):Viewport {
  const task=tasks.find(t=>t.key===selected),r=layout.rects[selected];if(!r)return frameViewport(layout.bounds,size);
  const all=[r,...tasks.filter(t=>t.key===task?.parent||t.parent===selected).map(t=>layout.rects[t.key])];
  if(frameViewport(boundsOf(all),size).zoom>=.85)return frameViewport(boundsOf(all),size);
  const nearby=[r];for(const other of all.slice(1)){if(frameViewport(boundsOf([...nearby,other]),size).zoom>=.85)nearby.push(other);}
  return frameViewport(boundsOf(nearby),size);
}
/** Minimum translation at the user's current zoom, including the focus outline. */
export function ensureVisibleViewport(rect:Rect,size:CanvasSize,current:Viewport,padding=12):Viewport {
  const left=current.x+rect.x*current.zoom,top=current.y+rect.y*current.zoom,right=left+rect.width*current.zoom,bottom=top+rect.height*current.zoom;
  return {...current,x:current.x+(left<padding?padding-left:right>size.width-padding?size.width-padding-right:0),y:current.y+(top<padding?padding-top:bottom>size.height-padding?size.height-padding-bottom:0)};
}
