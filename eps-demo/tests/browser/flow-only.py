"""Flow-only regression actions for chrome_probe.py. Use a fresh isolated loopback origin.
Example: python3 chrome_probe.py --url http://127.0.0.1:5198 --viewport 1280x800 --actions flow-only.py --no-screenshots
All mutations use visible controls. No app hooks, injected workspace state or direct storage writes.
"""
import json
import time

measurements = []

def read(expression):
    probe.guard()
    return js(expression)

def fit(label):
    value = read("""(() => {
      const e=document.querySelector('.sheet-content');if(!e)return null;
      const r=e.getBoundingClientRect();
      const controls=[...e.querySelectorAll('input:not([type=file]),select,textarea,button')].filter(x=>x.getClientRects().length&&getComputedStyle(x).visibility!=='hidden'&&!x.closest('details:not([open])'));
      return {task:document.querySelector('[data-pane-task]')?.dataset.paneTask,height:e.clientHeight,scroll:e.scrollHeight,
        documentWidth:document.documentElement.scrollWidth,viewport:innerWidth,overflow:getComputedStyle(e).overflowY,
        clippedControls:controls.filter(x=>{const b=x.getBoundingClientRect();return b.left<r.left-1||b.right>r.right+1||b.top<r.top-1||b.bottom>r.bottom+1}).map(x=>x.getAttribute('aria-label')||x.type||x.tagName)};
    })()""")
    measurements.append({'label':label,**value})
    probe.save('pane-fit.json',measurements)
    if read('innerWidth>900'):
        probe.check(label+' pane fits',value['scroll']<=value['height']+2 and not value['clippedControls'],value)
    probe.check(label+' has no horizontal document overflow',value['documentWidth']<=value['viewport']+1,value)
    return value

def click_task(key):
    if read("matchMedia('(max-width:900px)').matches&&!!document.querySelector('[role=dialog]')"):
        probe.click('[data-action=context-close]')
    selector='[data-task='+json.dumps(key)+']'
    read('document.querySelector('+json.dumps(selector)+').focus({preventScroll:true})')
    probe.wait_js("""(() => {const e=document.querySelector(SEL);if(!e)return false;const r=e.getBoundingClientRect(),b=e.closest('.activity-workspace').getBoundingClientRect();return r.left>=b.left-1&&r.right<=b.right+1&&r.top>=b.top-1&&r.bottom<=b.bottom+1;})()""".replace('SEL',json.dumps(selector)))
    p=read("(()=>{const r=document.querySelector(SEL).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()".replace('SEL',json.dumps(selector)))
    click_at_xy(p['x'],p['y'])
    probe.wait_js('document.querySelector("[data-pane-task]")?.dataset.paneTask==='+json.dumps(key))
    time.sleep(.08)
    # Fit acceptance concerns the primary pane. Supplemental help is tested open separately.
    for _ in range(5):
        opened=read('document.querySelector(".task-help[open]")?.dataset.help')
        if not opened:break
        probe.click('[data-help='+json.dumps(opened)+'] > summary')
    read('document.querySelector(".sheet-content").scrollTo({top:0,behavior:"instant"})')
    fit(key)
    return key

def child(parent,kind):
    key=read("""(()=>{const prefix=PARENT+'/'+KIND+':';return [...document.querySelectorAll('[data-task]')].map(e=>e.dataset.task).find(k=>k.startsWith(prefix)&&!k.slice(prefix.length).includes('/'));})()""".replace('PARENT',json.dumps(parent)).replace('KIND',json.dumps(kind)))
    if not key:raise AssertionError('Missing graphical child '+kind+' under '+parent)
    return click_task(key)

def select_option(label,value):
    selector=read("""(()=>{const label=[...document.querySelectorAll('.sheet label')].find(e=>e.innerText.trim()===LABEL);if(!label||!label.htmlFor)throw Error('Missing '+LABEL);return '#'+CSS.escape(label.htmlFor);})()""".replace('LABEL',json.dumps(label)))
    probe.point(selector)
    read("""(()=>{const e=document.querySelector(SEL);Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,VALUE);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));})()""".replace('SEL',json.dumps(selector)).replace('VALUE',json.dumps(value)))
    time.sleep(.1)

def node_keys(kind):
    return read('[...document.querySelectorAll('+json.dumps('[data-task-kind='+json.dumps(kind)+']')+')].map(e=>e.dataset.task)')

def open_help(kind):
    selector='details[data-help='+json.dumps(kind)+']'
    if not read('document.querySelector('+json.dumps(selector)+').open'):
        probe.click(selector+' > summary')
    probe.wait_js('document.querySelector('+json.dumps(selector)+').open')
    return selector

def help_field(label):
    return read('document.querySelector('+json.dumps('[data-help-field='+json.dumps(label)+'] .record-text')+').textContent')

probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
probe.check('initial graph has only ten activities and no inspector',read("document.querySelectorAll('[data-task]').length===10&&!document.querySelector('.context-host')&&!document.querySelector('.mission-composition-context,.canvas-findings,.canvas-welcome,.design-canvas-heading')"))
probe.snapshot('flow-only-initial')
# Root activity panes and immediate task families.
for root in ['mission','orbit','scenarios','budget','solar','battery','topology','candidates','simulation','assessment']:
    click_task(root)
    keys=read('[...document.querySelectorAll("[data-task]")].map(e=>e.dataset.task).filter(k=>k.startsWith('+json.dumps(root+'/')+')&&k.split("/").length===2)')
    for key in keys:
        click_task(key)
    if root=='battery':probe.snapshot('battery-focused')
# Detailed families with formerly oversized content.
click_task('battery');open_help('method')
probe.check('method trace remains in the activity pane', 'Erequired' in read('document.querySelector(".task-help[open]").innerText'))
click_task('battery');basis=child('battery','basis');record=child(basis,'provenance');open_help('provenance')
click_task('mission');open_help('reference');probe.check('complete reference context retained','Ground Segment [1]' in read('document.querySelector("[data-help=reference]").innerText'))
click_task('scenarios');loads=child('scenarios','loads');load=child(loads,'load');child(load,'load-power');click_task(load);windows=child(load,'windows');window=child(windows,'window')
# Keyboard editing uses the visible slider, commits through the shared editor controller.
probe.click('[aria-label="Move selected window"]');press_key('ArrowRight');fit('window after keyboard edit')
click_task('scenarios');description=child('scenarios','case-description');child(description,'edit-passage')
# Recalculate via normal Project menu after schedule changes.
if read("!!document.querySelector('[role=dialog]')"):probe.click('[data-action=context-close]')
probe.click('.project-menu > summary');probe.click('[data-action=recalculate]');time.sleep(.15)
click_task('candidates');cat=child('candidates','catalog');product=child(cat,'product')
open_help('product');probe.check('product scope is in its pane', 'Accounting boundary' in read('document.querySelector("[data-help=product]").innerText'))
for family in ['specs','screen','allocation','sources']:
    click_task(product);branch=child(product,family)
    if family=='specs':
        spec=child(branch,'spec');open_help('property')
    if family=='screen':
        checks=child(branch,'check-group')
        if node_keys('check'):child(checks,'check')
    if family=='sources':
        source=child(branch,'source');open_help('source')
click_task('candidates');ki=child('candidates','kicad');rules=child(ki,'rules');fit('reviewed rules before import')
click_task('assessment');groups=node_keys('check-group')
for group in groups:
    click_task(group)
    if node_keys('check'):child(group,'check')
# Offline mission retrieval and graphical explicit acceptance.
click_task('mission');search=child('mission','mission-search')
select_option('Choose a query example','0')
click_task(search);select_option('Retrieval method','lexical-tfidf');probe.click('[data-action=search-missions]')
probe.wait_js("document.querySelector('.task-body').innerText.includes('matches')")
fit('offline mission results')
analogues=child(search,'analogues');analogue=child(analogues,'analogue')
open_help('analogue');probe.check('orbit parameters remain in mission evidence','altitudeKm' in read('document.querySelector("[data-help=analogue]").innerText'))
for family in ['analogue-sources','accept-altitude']:
    click_task(analogue);leaf=child(analogue,family)
    if family=='analogue-sources':child(leaf,'source')
    if family=='accept-altitude' and read("!!document.querySelector('[data-action=accept-altitude]')"):
        probe.click('.checkbox-label input');probe.click('[data-action=accept-altitude]')
        probe.check('explicit mission acceptance writes the receipt',read("!!JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1')).inputs.mission.orbitSuggestion"))
# Home resets branch, never workspace.
if read("!!document.querySelector('[role=dialog]')"):probe.click('[data-action=context-close]')
probe.click('[data-action=flow-home]')
probe.wait_js("document.querySelectorAll('[data-task]').length===10&&!document.querySelector('.context-host')")
probe.check('Home returns to ten-node overview',True)
probe.save('pane-fit-summary.json',{'count':len(measurements),'maxOverflow':max(m['scroll']-m['height'] for m in measurements),'measurements':measurements})
