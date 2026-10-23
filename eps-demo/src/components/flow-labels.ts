import type { Rect, Point } from './flow-layout';
import { inflate, type RoutedRelation } from './flow-routing';
import { rectsOverlap } from './flow-layout';

export const LABEL_HEIGHT=20, LABEL_CHARACTER_WIDTH=6.2, LABEL_PADDING_X=7;
export interface PlacedLabel {text:string;rect:Rect;center:Point}
export function labelExtent(text:string) {return {width:text.length*LABEL_CHARACTER_WIDTH+2*LABEL_PADDING_X,height:LABEL_HEIGHT};}
/** Labels reserve their complete renderer footprint. Omission never changes a route. */
export function placeRouteLabels(routes:RoutedRelation[],nodes:Record<string,Rect>,name:(route:RoutedRelation)=>string):Record<string,PlacedLabel> {
  const placed:Record<string,PlacedLabel>={},reserved:Rect[]=[];
  for(const route of [...routes].filter(r=>r.kind!=='detail').sort((a,b)=>a.id.localeCompare(b.id))){
    const text=name(route),size=labelExtent(text);
    const segments=route.points.slice(1).map((b,i)=>({a:route.points[i],b,index:i,length:Math.abs(b.x-route.points[i].x)+Math.abs(b.y-route.points[i].y)})).sort((a,b)=>b.length-a.length||a.index-b.index);
    let found:PlacedLabel|undefined;
    for(const segment of segments){
      const horizontal=segment.a.y===segment.b.y,extent=horizontal?size.width:size.height;
      if(segment.length<extent+8)continue;
      for(const ratio of [.5,.25,.75,0,1]){
        const distance=extent/2+4+(segment.length-extent-8)*ratio;
        const center={x:horizontal?Math.min(segment.a.x,segment.b.x)+distance:segment.a.x,y:horizontal?segment.a.y:Math.min(segment.a.y,segment.b.y)+distance};
        const rect={x:center.x-size.width/2,y:center.y-size.height/2,...size};
        if(Object.values(nodes).some(node=>rectsOverlap(rect,inflate(node,4)))||reserved.some(other=>rectsOverlap(rect,inflate(other,4))))continue;
        found={text,rect,center};break;
      }
      if(found)break;
    }
    if(found){placed[route.id]=found;reserved.push(found.rect);}
  }
  return placed;
}
export function labelFullyVisible(rect:Rect,size:{width:number;height:number},viewport:{x:number;y:number;zoom:number},padding=4){
  return viewport.x+rect.x*viewport.zoom>=padding&&viewport.y+rect.y*viewport.zoom>=padding&&viewport.x+(rect.x+rect.width)*viewport.zoom<=size.width-padding&&viewport.y+(rect.y+rect.height)*viewport.zoom<=size.height-padding;
}
