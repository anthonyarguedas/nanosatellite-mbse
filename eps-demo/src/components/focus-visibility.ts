/** Native details can retain descendant layout boxes while their content is hidden.
 * A closed disclosure's own direct summary remains visible and focusable. */
export function hiddenByClosedDisclosure(item:Element):boolean {
  for(let parent=item.parentElement;parent;parent=parent.parentElement){
    if(parent.tagName!=='DETAILS'||parent.hasAttribute('open'))continue;
    const summary=Array.from(parent.children).find(child=>child.tagName==='SUMMARY');
    if(!summary?.contains(item))return true;
  }
  return false;
}
