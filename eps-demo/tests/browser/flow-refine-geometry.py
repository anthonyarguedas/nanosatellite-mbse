"""Exact mounted SVG/node geometry, navigation stability, and live help acceptance."""
import json
import time
exec((ROOT/'flow-only.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
exec((ROOT/'canvas_helpers.py').read_text())
geometry=[]
def measure(label):
    result=read(r'''(()=>{
      const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
      const nodes=[...document.querySelectorAll('[data-task]')].map(e=>({key:e.dataset.task,kind:e.dataset.taskKind,r:rect(e),world:e.closest('.react-flow__node').style.transform}));
      const overlaps=[],intersections=[];
      for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){const a=nodes[i].r,b=nodes[j].r;if(a.x<b.x+b.width-.2&&b.x<a.x+a.width-.2&&a.y<b.y+b.height-.2&&b.y<a.y+a.height-.2)overlaps.push([nodes[i].key,nodes[j].key]);}
      for(const p of document.querySelectorAll('.react-flow__edge-path')){const owner=p.closest('[data-route-source]'),m=p.getScreenCTM(),coords=p.getAttribute('d').match(/-?\d+(?:\.\d+)?(?:e[-+]?\d+)?/gi).map(Number),points=[];for(let i=0;i<coords.length;i+=2)points.push(new DOMPoint(coords[i],coords[i+1]).matrixTransform(m));
        for(const n of nodes){if(n.key===owner.dataset.routeSource||n.key===owner.dataset.routeTarget)continue;const r=n.r;for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],cross=Math.abs(a.x-b.x)<.01?a.x>r.x+.2&&a.x<r.x+r.width-.2&&Math.max(a.y,b.y)>r.y+.2&&Math.min(a.y,b.y)<r.y+r.height-.2:a.y>r.y+.2&&a.y<r.y+r.height-.2&&Math.max(a.x,b.x)>r.x+.2&&Math.min(a.x,b.x)<r.x+r.width-.2;if(cross){intersections.push({edge:p.id,node:n.key});break;}}}
      }
      return {nodes,overlaps,intersections,edges:document.querySelectorAll('.react-flow__edge-path').length,paths:Object.fromEntries([...document.querySelectorAll('.react-flow__edge-path')].map(p=>[p.id,p.getAttribute('d')])),transform:document.querySelector('.react-flow__viewport').style.transform,graph:rect(document.querySelector('.activity-workspace'))};
    })()''')
    geometry.append({'label':label,**result});probe.save('graph-geometry.json',geometry)
    probe.check(label+' has no mounted node overlaps',not result['overlaps'],result['overlaps'])
    probe.check(label+' has no SVG segment/node intersections',not result['intersections'],result['intersections'])
    return result
probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
probe.check('exactly ten initial activities and no pane',read("document.querySelectorAll('[data-task]').length===10&&!document.querySelector('.context-host')"))
initial=measure('initial backbone')
if read('innerWidth>=1000'):
    probe.check('desktop overview shows all ten nodes',all(n['r']['x']>=initial['graph']['x'] and n['r']['y']>=initial['graph']['y'] and n['r']['x']+n['r']['width']<=initial['graph']['x']+initial['graph']['width'] and n['r']['y']+n['r']['height']<=initial['graph']['y']+initial['graph']['height'] for n in initial['nodes']))
probe.click('.relationship-toggle');probe.check('all nineteen real relationships available',read("document.querySelectorAll('.react-flow__edge-path').length===19"));expanded=measure('initial all relationships')
probe.check('visibility toggle never shuffles existing routes',all(expanded['paths'][key]==value for key,value in initial['paths'].items()))
for root in ['mission','orbit','scenarios','budget','solar','battery','topology','candidates','simulation','assessment']:
    click_task(root);measure(root)
click_task('battery');before=measure('battery before help')
read('document.querySelector("[data-help=method] > summary").focus()');press_key('Enter')
probe.wait_js('document.querySelector("[data-help=method]").open')
probe.point('[data-help-field="Method sources"]')
probe.check('opened method is keyboard accessible and scrollable',read('document.querySelector(".sheet-content").scrollTop>0'))
probe.check('full equation and trace accessible in owning pane','Erequired' in read('document.querySelector("[data-help=method]").innerText'))
probe.check('help leaves graph and camera unchanged',read('document.querySelector(".react-flow__viewport").style.transform')==before['transform'] and read('document.querySelectorAll("[data-task]").length')==len(before['nodes']))
probe.click('[data-help=method] > summary')
view=read('document.querySelector(".react-flow__viewport").style.transform');probe.fill(field('Design DoD limit'),'0.31')
probe.check('real numeric edit updates the authored input',authored()['inputs']['battery']['dod']==.31)
probe.check('numeric edit leaves camera unchanged',read('document.querySelector(".react-flow__viewport").style.transform')==view)
probe.click('.project-menu > summary');probe.click('[data-action=recalculate]');time.sleep(.15)
probe.check('recompute leaves positions and camera unchanged',read('document.querySelector(".react-flow__viewport").style.transform')==view and measure('battery after recompute')['nodes']==before['nodes'])
click_task('scenarios');loads=child('scenarios','loads');load=child(loads,'load');windows=child(load,'windows');window=child(windows,'window');window_before=measure('deep window')
open_help('schedule');probe.check('timeline keyboard help reachable','Shift uses 0.1%' in read('document.querySelector("[data-help=schedule]").innerText'))
probe.click('[data-action=context-back]');measure('window Back');click_task(window);window_again=measure('repeat window selection')
probe.check('repeat selection has identical positions and camera',window_again['nodes']==window_before['nodes'] and window_again['transform']==window_before['transform'])
click_task('candidates');cat=child('candidates','catalog');product=child(cat,'product');specs=child(product,'specs');spec=child(specs,'spec');measure('deep property')
open_help('property');probe.check('complete property fields remain accessible',bool(help_field('Complete property record')))
probe.click('[data-action=context-back]');measure('property Back')
# Resize with selected branch, including switching layout direction and modal behavior.
for width,height in [(1280,800),(390,844),(1440,900)]:
    cdp('Emulation.setDeviceMetricsOverride',width=width,height=height,deviceScaleFactor=1,mobile=False);time.sleep(.25);measure('resize '+str(width))
if has('[role=dialog]'):probe.click('[data-action=context-close]')
probe.click('[data-action=flow-home]');probe.wait_js("document.querySelectorAll('[data-task]').length===10&&!document.querySelector('.context-host')")
home=measure('Home')
probe.check('Home reproduces overview positions',[n['world'] for n in home['nodes']]==[n['world'] for n in initial['nodes']])
# UI-only project help never expands a graph or moves its camera.
probe.click('.project-menu > summary');probe.click('[data-action=project-scope]')
probe.check('Project help is not a graph task',read('document.querySelectorAll("[data-task]").length===10') and read('document.querySelector(".react-flow__viewport").style.transform')==home['transform'])
probe.click('[data-action=context-close]')
probe.check('no doc-only graph task kinds',read("![...document.querySelectorAll('[data-task]')].some(e=>['method','trace','text','passage','outputs','reference','study','scope'].includes(e.dataset.taskKind))"))
probe.save('graph-summary.json',{'visits':len(geometry),'maxOverlaps':max(len(g['overlaps']) for g in geometry),'maxIntersections':max(len(g['intersections']) for g in geometry)})
