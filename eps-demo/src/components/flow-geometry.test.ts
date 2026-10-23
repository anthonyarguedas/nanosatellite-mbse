import { describe,expect,it } from 'vitest';
import { catalog } from '../data/catalog';
import { createExampleWorkspace } from '../state/model';
import { DEFAULT_CATALOG_FILTERS } from './CatalogView';
import { activityEdges } from './design-canvas-model';
import { related,roots,visibleTasks,presentationEdges,type FlowTask,type TaskContext,child,entries } from './flow-tasks';
import { layoutFlow,rectsOverlap,NODE_WIDTH,NODE_HEIGHT,type FlowMode } from './flow-layout';
import { routeFlow,routeIntersections,segmentIntersectsRect } from './flow-routing';
import { ensureVisibleViewport,focusViewport,frameViewport } from './flow-camera';
const context=():TaskContext=>({workspace:createExampleWorkspace(),catalog,picks:{},filters:DEFAULT_CATALOG_FILTERS,missionResult:null,ruleWarnings:[],verdict:'all'});
function paths(c:TaskContext){
  const result:FlowTask[][]=[[],...roots.map(t=>[t])];
  for(const owner of ['scenarios','candidates']){
    const r=roots.find(t=>t.key===owner)!;
    let path=[r];
    for(const kind of owner==='scenarios'?['loads','load','windows','window']:['catalog','product','specs','spec','source']){const next=related(path.at(-1)!,c).find(t=>t.kind===kind);if(!next)break;path=[...path,next];result.push(path);}
  }
  return result;
}
describe('reserved activity trees and obstacle-free routes',()=>{
  for(const mode of ['horizontal','vertical'] as FlowMode[])it(`reserves all real root and deep branches in ${mode}`,()=>{
    const c=context();for(const path of paths(c)){
      const tasks=visibleTasks(path,c),layout=layoutFlow(tasks,mode),boxes=Object.entries(layout.rects);
      for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++)expect(rectsOverlap(boxes[i][1],boxes[j][1]),`${boxes[i][0]} / ${boxes[j][0]}`).toBe(false);
      const routes=routeFlow(layout,[...activityEdges(),...presentationEdges(tasks)]);
      expect(routes.filter(r=>r.kind!=='detail')).toHaveLength(19);
      for(const r of routes){expect(routeIntersections(r,layout.rects),r.id).toEqual([]);expect(r.points[0]).toMatchObject({x:r.sourcePort.x,y:r.sourcePort.y});expect(r.points.at(-1)).toMatchObject({x:r.targetPort.x,y:r.targetPort.y});for(let i=1;i<r.points.length;i++)expect(r.points[i].x===r.points[i-1].x||r.points[i].y===r.points[i-1].y).toBe(true);}
      expect(layoutFlow([...tasks].reverse(),mode)).toEqual(layout);
    }
  });
  it('handles deep and broad neighboring clusters with exact clearance',()=>{
    const tasks=[...roots];for(const owner of ['solar','battery']){let p=roots.find(t=>t.key===owner)!;for(let depth=0;depth<12;depth++){const kids=Array.from({length:3},(_,index)=>child(p,'finding',`Record ${index}`,{ref:String(index)}));tasks.push(...kids);p=kids[1];}}
    for(const mode of ['horizontal','vertical'] as FlowMode[]){const l=layoutFlow(tasks,mode),boxes=Object.values(l.rects);for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++)expect(rectsOverlap(boxes[i],boxes[j])).toBe(false);for(const r of routeFlow(l,[...activityEdges(),...presentationEdges(tasks)]))expect(routeIntersections(r,l.rects),r.id).toEqual([]);}
  });
  it('keeps coordinates and route allocation unchanged for values and relation visibility',()=>{
    const c=context(),p=paths(c).at(-1)!,tasks=visibleTasks(p,c),before=layoutFlow(tasks,'horizontal');
    c.workspace.inputs.mission.altitudeKm=450;c.workspace.records.solar.revision++;const after=layoutFlow(visibleTasks(p,c),'horizontal');expect(after).toEqual(before);
    const routes=routeFlow(before,[...activityEdges(),...presentationEdges(tasks)]);expect(routeFlow(after,[...activityEdges(),...presentationEdges(tasks)])).toEqual(routes);
    const cat=related(roots.find(t=>t.key==='candidates')!,c).find(t=>t.kind==='catalog')!;const a=entries(cat,c)[0].task,b=entries(cat,c)[1].task;
    expect(layoutFlow([...roots,cat,a],'horizontal').rects[a.key]).toEqual(layoutFlow([...roots,cat,b],'horizontal').rects[b.key]);
  });
  it('checks exact strict intersections',()=>{const r={x:0,y:0,width:10,height:10};expect(segmentIntersectsRect({x:-1,y:5},{x:11,y:5},r)).toBe(true);expect(segmentIntersectsRect({x:-1,y:0},{x:11,y:0},r)).toBe(false);});
  it('fits all ten desktop roots without a clipping zoom floor and minimally reveals focus',()=>{
    const l=layoutFlow(roots,'horizontal');for(const size of [{width:1440,height:780},{width:1280,height:680}]){const v=frameViewport(l.bounds,size,1.04);expect(v.zoom).toBeGreaterThan(.8);expect(v.x+l.bounds.width*v.zoom).toBeLessThan(size.width);}
    const c=context(),tasks=visibleTasks([roots.find(t=>t.key==='battery')!],c),branch=layoutFlow(tasks,'horizontal'),size={width:980,height:730};const v=focusViewport(branch,tasks,'battery',size);expect(v.zoom).toBeGreaterThanOrEqual(.85);
    const current={x:0,y:0,zoom:1.25},rect={x:900,y:100,width:NODE_WIDTH,height:NODE_HEIGHT},shown=ensureVisibleViewport(rect,size,current);expect(shown.zoom).toBe(current.zoom);expect(shown.y).toBe(0);expect(shown.x).toBeLessThan(0);
  });
});
