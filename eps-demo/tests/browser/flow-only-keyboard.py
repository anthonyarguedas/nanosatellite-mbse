"""Actual Tab/Shift+Tab camera reveal and form-key isolation."""
import json
import time
probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
# Open a branch using a real pointer, then close the pane while retaining it.
js("document.querySelector('[data-activity=battery]').focus({preventScroll:true})")
p=js("(()=>{const r=document.querySelector('[data-activity=battery]').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
click_at_xy(p['x'],p['y'])
probe.wait_js("!!document.querySelector('.context-host')")
probe.click('[data-action=context-close]')
probe.wait_js("!document.querySelector('.context-host')")
js("document.querySelector('[data-activity=mission]').focus({preventScroll:true})")
results=[]
for direction in ['Tab','Shift+Tab']:
    for index in range(16):
        press_key('Tab',modifiers=8 if direction=='Shift+Tab' else 0)
        value=js("""(()=>{const e=document.activeElement;if(!e?.dataset.task)return {node:null};const r=e.getBoundingClientRect(),b=e.closest('.activity-workspace').getBoundingClientRect();return {node:e.dataset.task,left:r.left,right:r.right,top:r.top,bottom:r.bottom,bounds:b.toJSON(),transform:document.querySelector('.react-flow__viewport').style.transform};})()""")
        if not value['node']:continue
        probe.check(direction+' reveals '+value['node'],value['left']>=value['bounds']['left']-1 and value['right']<=value['bounds']['right']+1 and value['top']>=value['bounds']['top']-1 and value['bottom']<=value['bounds']['bottom']+1,value)
        results.append(value)
probe.save('keyboard-camera.json',results)
probe.check('native keyboard traversed roots and detail nodes',any('/' in item['node'] for item in results) and any('/' not in item['node'] for item in results))
# Use an existing form after Enter activates its graph node.
js("document.querySelector('[data-activity=mission]').focus({preventScroll:true})")
press_key('Enter')
probe.wait_js("document.querySelector('[data-pane-task]')?.dataset.paneTask==='mission'")
probe.click('input[aria-label="Design name"]')
before=js("document.querySelector('.react-flow__viewport').style.transform")
press_key('ArrowLeft')
probe.check('form arrow keys never pan the graph',js("document.querySelector('.react-flow__viewport').style.transform")==before)
press_key('Escape')
probe.wait_js("!document.querySelector('.context-host')")
probe.wait_js("document.activeElement?.dataset.task==='mission'",timeout=4)
probe.check('Escape restores the selected graph trigger',True)
