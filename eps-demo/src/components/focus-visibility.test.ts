import { describe,expect,it } from 'vitest';
import { hiddenByClosedDisclosure } from './focus-visibility';
function node(tagName:string,parent?:ReturnType<typeof element>){return element(tagName,parent);}
function element(tagName:string,parent?:{children:unknown[]}) {
  const e={tagName,parentElement:parent??null,children:[] as unknown[],open:false,hasAttribute(name:string){return name==='open'&&this.open;},contains(item:unknown):boolean{return item===this||this.children.some(c=>(c as typeof e).contains(item));}};
  parent?.children.push(e);return e;
}
const hidden=(n:unknown)=>hiddenByClosedDisclosure(n as Element);
describe('native disclosure focus visibility',()=>{
  it('keeps a closed disclosure own summary and its contents focusable',()=>{const details=node('DETAILS'),summary=node('SUMMARY',details),span=node('SPAN',summary);expect(hidden(summary)).toBe(false);expect(hidden(span)).toBe(false);});
  it('excludes content with retained rectangles and restores it on open',()=>{const details=node('DETAILS'),summary=node('SUMMARY',details),button=node('BUTTON',details);expect(hidden(summary)).toBe(false);expect(hidden(button)).toBe(true);details.open=true;expect(hidden(button)).toBe(false);});
  it('excludes nested summaries inside a closed outer disclosure',()=>{const outer=node('DETAILS');node('SUMMARY',outer);const inner=node('DETAILS',outer),summary=node('SUMMARY',inner);expect(hidden(summary)).toBe(true);outer.open=true;expect(hidden(summary)).toBe(false);});
});
