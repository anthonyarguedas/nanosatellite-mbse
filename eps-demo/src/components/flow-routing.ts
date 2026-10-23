import type { FlowLayout, Point, Rect } from './flow-layout';
export type RelationKind='dependency'|'evidence'|'detail';
export interface Relation {id:string;source:string;target:string;kind:RelationKind;primary?:boolean}
export interface Port extends Point {id:string;side:'left'|'right'|'top'|'bottom';type:'source'|'target';node:string}
export interface RoutedRelation extends Relation {points:Point[];sourcePort:Port;targetPort:Port;labelPoint:Point;junction?:Point}
export const ROUTE_CLEARANCE=12, PORT_STUB=18;
export function inflate(r:Rect,amount=ROUTE_CLEARANCE):Rect{return {x:r.x-amount,y:r.y-amount,width:r.width+2*amount,height:r.height+2*amount};}
/** Strict interior intersection. Boundary travel is permitted at the clearance envelope. */
export function segmentIntersectsRect(a:Point,b:Point,r:Rect):boolean {
  if(a.x===b.x)return a.x>r.x&&a.x<r.x+r.width&&Math.max(a.y,b.y)>r.y&&Math.min(a.y,b.y)<r.y+r.height;
  if(a.y===b.y)return a.y>r.y&&a.y<r.y+r.height&&Math.max(a.x,b.x)>r.x&&Math.min(a.x,b.x)<r.x+r.width;
  throw Error('Route segment is not orthogonal');
}
export function routeIntersections(route:RoutedRelation,rects:Record<string,Rect>,clearance=ROUTE_CLEARANCE) {
  return Object.entries(rects).filter(([id,r])=>id!==route.source&&id!==route.target&&route.points.slice(1).some((p,i)=>segmentIntersectsRect(route.points[i],p,inflate(r,clearance)))).map(([id])=>id);
}
function simplify(points:Point[]):Point[] {return points.filter((p,i)=>!i||i===points.length-1||!((points[i-1].x===p.x&&p.x===points[i+1].x)||(points[i-1].y===p.y&&p.y===points[i+1].y)));}
class Heap {
  values:{id:number;cost:number}[]=[];
  push(value:{id:number;cost:number}){const a=this.values;a.push(value);let i=a.length-1;while(i){const p=(i-1)>>1;if(a[p].cost<=value.cost)break;a[i]=a[p];i=p;}a[i]=value;}
  pop(){const a=this.values,first=a[0],last=a.pop()!;if(a.length){let i=0;while(i*2+1<a.length){let c=i*2+1;if(c+1<a.length&&a[c+1].cost<a[c].cost)c++;if(a[c].cost>=last.cost)break;a[i]=a[c];i=c;}a[i]=last;}return first;}
}
function port(edge:Relation,type:'source'|'target',layout:FlowLayout,all:Relation[]):Port {
  const node=type==='source'?edge.source:edge.target,r=layout.rects[node],horizontal=layout.mode==='horizontal';
  const peers=all.filter(e=>e.kind!=='detail'&&(type==='source'?e.source:e.target)===node);
  const index=peers.findIndex(e=>e.id===edge.id);
  const fraction=edge.kind==='detail'?.82:.12+.48*(index+1)/(peers.length+1);
  const side=horizontal?(type==='source'?'right':'left'):(type==='source'?'bottom':'top');
  return {id:`${type}:${edge.id}`,node,type,side,x:horizontal?r.x+(type==='source'?r.width:0):r.x+r.width*fraction,y:horizontal?r.y+r.height*fraction:r.y+(type==='source'?r.height:0)};
}
const stub=(p:Port):Point=>({x:p.x+(p.side==='right'?PORT_STUB:p.side==='left'?-PORT_STUB:0),y:p.y+(p.side==='bottom'?PORT_STUB:p.side==='top'?-PORT_STUB:0)});
/** Visibility-grid search. The full route set is stable before visual filtering. */
export function routeFlow(layout:FlowLayout,relations:Relation[]):RoutedRelation[] {
  const all=[...relations].sort((a,b)=>(a.kind==='detail'?2:a.primary?0:1)-(b.kind==='detail'?2:b.primary?0:1)||a.id.localeCompare(b.id));
  const obstacles=Object.values(layout.rects).map(r=>inflate(r));
  const ports=all.map(edge=>({edge,source:port(edge,'source',layout,all),target:port(edge,'target',layout,all)}));
  const xs=new Set<number>(),ys=new Set<number>();
  for(const r of obstacles){xs.add(r.x);xs.add(r.x+r.width);ys.add(r.y);ys.add(r.y+r.height);}
  for(const p of ports){for(const s of [stub(p.source),stub(p.target)]){xs.add(s.x);ys.add(s.y);}}
  const bounds=layout.bounds;
  for(let i=1;i<=4;i++){xs.add(bounds.x-24*i);xs.add(bounds.x+bounds.width+24*i);ys.add(bounds.y-24*i);ys.add(bounds.y+bounds.height+24*i);}
  const xx=[...xs].sort((a,b)=>a-b),yy=[...ys].sort((a,b)=>a-b),nx=xx.length,ny=yy.length;
  const inside=(p:Point)=>obstacles.some(r=>p.x>r.x&&p.x<r.x+r.width&&p.y>r.y&&p.y<r.y+r.height);
  const points=yy.flatMap(y=>xx.map(x=>({x,y}))),valid=points.map(p=>!inside(p));
  const neighbors:number[][]=points.map(()=>[]);
  for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
    const id=y*nx+x;if(!valid[id])continue;
    for(const next of [x+1<nx?id+1:-1,y+1<ny?id+nx:-1])if(next>=0&&valid[next]&&!obstacles.some(r=>segmentIntersectsRect(points[id],points[next],r))){neighbors[id].push(next);neighbors[next].push(id);}
  }
  const result:RoutedRelation[]=[],used:{a:Point;b:Point;kind:RelationKind;source:string}[]=[];
  for(const {edge,source,target} of ports){
    const a=stub(source),b=stub(target),start=yy.indexOf(a.y)*nx+xx.indexOf(a.x),goal=yy.indexOf(b.y)*nx+xx.indexOf(b.x);
    // Reserved tree gutters support one explicit shared parent spine. Certify it
    // against every unrelated box before using it. Other routes use the grid.
    if(edge.kind==='detail') {
      const horizontal=layout.mode==='horizontal';
      const junction=horizontal?{x:source.x+32,y:target.y}:{x:target.x,y:source.y+32};
      const elbow=horizontal?{x:junction.x,y:source.y}:{x:source.x,y:junction.y};
      const points=simplify([source,elbow,junction,target]);
      const candidate={...edge,points,sourcePort:source,targetPort:target,labelPoint:junction,junction};
      if(!routeIntersections(candidate,layout.rects).length){result.push(candidate);for(let i=1;i<points.length;i++)used.push({a:points[i-1],b:points[i],kind:edge.kind,source:edge.source});continue;}
    }
    const dist=new Float64Array(points.length*2).fill(Infinity),prev=new Int32Array(points.length*2).fill(-1),heap=new Heap();
    for(const d of [0,1]){dist[start*2+d]=0;heap.push({id:start*2+d,cost:0});}
    let end=-1;
    while(heap.values.length){const item=heap.pop(),state=item.id,id=state>>1,direction=state%2;if(item.cost!==dist[state])continue;if(id===goal){end=state;break;}
      for(const next of neighbors[id]){const p=points[id],q=points[next],d=p.y===q.y?0:1,len=Math.abs(q.x-p.x)+Math.abs(q.y-p.y);let penalty=0;
        for(const s of used){if(edge.kind==='detail'&&s.kind==='detail'&&edge.source===s.source)continue;
          if(d===0&&s.a.y===s.b.y&&p.y===s.a.y&&Math.max(Math.min(p.x,q.x),Math.min(s.a.x,s.b.x))<Math.min(Math.max(p.x,q.x),Math.max(s.a.x,s.b.x)))penalty+=len*2+10;
          if(d===1&&s.a.x===s.b.x&&p.x===s.a.x&&Math.max(Math.min(p.y,q.y),Math.min(s.a.y,s.b.y))<Math.min(Math.max(p.y,q.y),Math.max(s.a.y,s.b.y)))penalty+=len*2+10;
        }
        const cost=item.cost+len+(d===direction?0:24)+penalty,s=next*2+d;
        if(cost<dist[s]){dist[s]=cost;prev[s]=state;heap.push({id:s,cost});}
      }
    }
    if(end<0)throw Error(`No obstacle-free route for ${edge.id}`);
    const path:Point[]=[];for(let s=end;s>=0;s=prev[s])path.push(points[s>>1]);path.reverse();
    const poly=simplify([source,...path,target]);
    const segments=poly.slice(1).map((p,i)=>({a:poly[i],b:p,kind:edge.kind,source:edge.source}));used.push(...segments);
    const longest=segments.reduce((a,b)=>Math.abs(a.a.x-a.b.x)+Math.abs(a.a.y-a.b.y)>Math.abs(b.a.x-b.b.x)+Math.abs(b.a.y-b.b.y)?a:b);
    result.push({...edge,points:poly,sourcePort:source,targetPort:target,labelPoint:{x:(longest.a.x+longest.b.x)/2,y:(longest.a.y+longest.b.y)/2}});
  }
  return result;
}
export function routePath(points:Point[]) {return points.map((p,i)=>`${i?'L':'M'} ${p.x} ${p.y}`).join(' ');}
