import { BaseEdge, type Edge, type EdgeProps } from '@xyflow/react';
import { routePath, type RoutedRelation } from './flow-routing';
import type { PlacedLabel } from './flow-labels';
export type InformationEdge=Edge<{route:RoutedRelation;label?:PlacedLabel;accessibleLabel?:string},'information'>;
export function FlowInformationEdge({id,data,style,markerEnd}:EdgeProps<InformationEdge>) {
  if(!data)return null;
  const {route,label,accessibleLabel}=data;
  return <g data-route-source={route.source} data-route-target={route.target} aria-label={accessibleLabel}><title>{accessibleLabel}</title><BaseEdge id={id} path={routePath(route.points)} style={style} markerEnd={markerEnd}/>{route.junction&&<circle className="detail-junction" cx={route.junction.x} cy={route.junction.y} r={2.2} fill={style?.stroke}/>} {label&&<g className="flow-edge-label" transform={`translate(${label.center.x},${label.center.y})`}><rect x={-label.rect.width/2} y={-label.rect.height/2} width={label.rect.width} height={label.rect.height} rx={4}/><text textAnchor="middle" dominantBaseline="central">{label.text}</text></g>}</g>;
}
