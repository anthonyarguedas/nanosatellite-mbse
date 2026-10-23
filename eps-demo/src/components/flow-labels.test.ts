import { describe,expect,it } from 'vitest';
import { catalog } from '../data/catalog';
import { createExampleWorkspace } from '../state/model';
import { DEFAULT_CATALOG_FILTERS } from './CatalogView';
import { roots,related,visibleTasks,presentationEdges,type TaskContext } from './flow-tasks';
import { activityEdges } from './design-canvas-model';
import { engineeringExchange } from './engineering-exchanges';
import { layoutFlow,rectsOverlap } from './flow-layout';
import { routeFlow,type RoutedRelation } from './flow-routing';
import { labelExtent,labelFullyVisible,placeRouteLabels } from './flow-labels';
import type { NodeId } from '../types';
const name=(r:RoutedRelation)=>engineeringExchange(r.source as NodeId,r.target as NodeId).label;
describe('exchange label footprints',()=>{
  it('clears all nodes and other labels for all root fixtures and deep branches in both modes',()=>{
    const c:TaskContext={workspace:createExampleWorkspace(),catalog,picks:{},filters:DEFAULT_CATALOG_FILTERS,missionResult:null,ruleWarnings:[],verdict:'all'};
    const paths=roots.map(r=>[r]);let path=[roots.find(r=>r.key==='scenarios')!];for(const kind of ['loads','load','windows','window']){path=[...path,related(path.at(-1)!,c).find(t=>t.kind===kind)!];paths.push(path);}
    let count=0;for(const mode of ['horizontal','vertical'] as const)for(const path of paths){const tasks=visibleTasks(path,c),layout=layoutFlow(tasks,mode),routes=routeFlow(layout,[...activityEdges(),...presentationEdges(tasks)]),before=JSON.stringify(routes),labels=placeRouteLabels(routes,layout.rects,name),all=Object.values(labels);count+=all.length;
      for(let i=0;i<all.length;i++){expect(all[i].rect).toMatchObject(labelExtent(all[i].text));for(const node of Object.values(layout.rects))expect(rectsOverlap(all[i].rect,node)).toBe(false);for(let j=i+1;j<all.length;j++)expect(rectsOverlap(all[i].rect,all[j].rect)).toBe(false);}
      expect(JSON.stringify(routes)).toBe(before);expect(placeRouteLabels([...routes].reverse(),layout.rects,name)).toEqual(labels);
    }expect(count).toBeGreaterThan(30);
  });
  it('omits a label that cannot fit its route instead of crossing endpoint nodes',()=>{
    const layout=layoutFlow(roots,'horizontal'),routes=routeFlow(layout,activityEdges()),route=routes.find(r=>r.id==='candidates-simulation')!;
    const labels=placeRouteLabels([route],layout.rects,()=> 'Catalog / roles'.repeat(30));expect(labels[route.id]).toBeUndefined();
  });
  it('requires the entire footprint inside the measured canvas',()=>{
    const size={width:500,height:300},v={x:20,y:30,zoom:1};expect(labelFullyVisible({x:0,y:0,width:100,height:20},size,v)).toBe(true);expect(labelFullyVisible({x:0,y:-28,width:100,height:20},size,v)).toBe(false);expect(labelFullyVisible({x:450,y:0,width:100,height:20},size,v)).toBe(false);
  });
});
