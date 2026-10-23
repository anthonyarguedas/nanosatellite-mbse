import type { NodeId } from '../types';
import type { HelpSection } from './flow-task-help';
import { ACTIVITY_LABELS } from './design-canvas-model';

export function FlowTaskHelp({sections,onRoot,open=false}:{sections:HelpSection[];onRoot:(id:NodeId)=>void;open?:boolean}) {
  return <>{sections.map(section=><details className="task-help" data-help={section.id} key={section.id} open={open||undefined}>
    <summary>{section.title}</summary><div className="task-help-content">
      {section.paragraphs?.map((text,i)=><p className="record-text" key={i}>{text}</p>)}
      {section.fields?.map((field,i)=><section data-help-field={field.label} key={i}><h3>{field.label}</h3><p className="record-text">{field.value}</p></section>)}
      {!!section.items?.length&&<ul className="task-list">{section.items.map((item,i)=><li key={i}>{item}</li>)}</ul>}
      {section.links?.map((link,i)=><a key={i} href={link.url} target="_blank" rel="noreferrer">{link.label} ↗</a>)}
      {!!section.upstream?.length&&<div className="task-actions">{section.upstream.map(id=><button className="button secondary" key={id} onClick={()=>onRoot(id)}>Inspect {ACTIVITY_LABELS[id]}</button>)}</div>}
    </div>
  </details>)}</>;
}
