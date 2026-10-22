"""Reusable BIRDS-4 Chrome actions. Run with chrome_probe.py --actions workflow.py.
EPS_TEST_PHASE selects smoke, scenarios, energy, catalog, io, blank, or all.
All authored changes use visible controls and native CDP input. Export content is
captured at the owned page's Blob anchor sink, not a native Chrome file-save test.
"""
import json
import math
import os
import time
from pathlib import Path


def read(expression):
    probe.guard()
    return js(expression)


def statuses():
    return read("""(() => Object.fromEntries([...document.querySelectorAll('.react-flow__node')]
      .map(e => { const c=e.querySelector('.workflow-node');return [e.dataset.id,
      ['complete','ready','locked','stale'].find(s=>c?.classList.contains(s))]; })))()""")


def dismiss():
    for selector in ['[aria-label="Dismiss error"]','[aria-label="Dismiss notification"]']:
        if read(f'!!document.querySelector({json.dumps(selector)})'):
            probe.click(selector)


def button(text, scope=''):
    return read("""(() => {const root=SCOPE?document.querySelector(SCOPE):document;
      const all=[...root.querySelectorAll('button')];const e=all.find(e=>e.textContent.trim()===TEXT);
      if(!e)throw Error('No button '+TEXT);return SCOPE+' button:nth-of-type('+([...e.parentElement.children].filter(x=>x.tagName==='BUTTON').indexOf(e)+1)+')';})()"""
      .replace('SCOPE',json.dumps(scope)).replace('TEXT',json.dumps(text)))


def field(label, scope='.sheet'):
    return read("""(() => {const root=SCOPE?document.querySelector(SCOPE):document;
      const labels=[...root.querySelectorAll('label')].filter(e=>e.textContent.trim()===LABEL);
      if(labels.length!==1)throw Error('Field label not unique: '+LABEL);
      return '#'+CSS.escape(labels[0].htmlFor);})()""".replace('SCOPE',json.dumps(scope)).replace('LABEL',json.dumps(label)))


def value(selector):
    return read('document.querySelector('+json.dumps(selector)+').value')


def fill(selector, val, commit='Enter'):
    probe.fill(selector,str(val),commit)
    actual=value(selector)
    try:
        ok=float(actual)==float(val)
    except (ValueError,TypeError):
        ok=actual==str(val)
    probe.check('input readback '+selector,ok,{'expected':val,'actual':actual})


def select_value(selector, wanted):
    options=read('[...document.querySelector('+json.dumps(selector)+').options].map(e=>({value:e.value,disabled:e.disabled}))')
    index=next(i for i,e in enumerate(options) if e['value']==wanted)
    probe.point(selector)
    # Native macOS popup keyboard selection is unavailable in this background CDP
    # session. Use the native select value + ordinary UI change events, equivalent
    # to browser automation selectOption. Never call application state methods.
    read("""(() => {const e=document.querySelector(SELECTOR);e.focus();
      Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,WANTED);
      e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));
      return e.value;})()""".replace('SELECTOR',json.dumps(selector)).replace('WANTED',json.dumps(wanted)))
    probe.wait_js('document.querySelector('+json.dumps(selector)+').value==='+json.dumps(wanted))


def close_sheet():
    if read("!!document.querySelector('.sheet')"):
        press_key('Escape')
        probe.wait_js("!document.querySelector('.sheet')")


def node(node_id):
    close_sheet()
    probe.click(f'.react-flow__node[data-id="{node_id}"] .workflow-node')
    probe.wait_js("!!document.querySelector('.sheet[role=dialog]')")


def tab(tab_id):
    close_sheet()
    probe.click('#tab-'+tab_id)
    probe.wait_js('!!document.querySelector("#panel-'+tab_id+'")')


def reset(run=True):
    probe.click('.topbar .load-example')
    probe.wait_js("document.querySelector('.mission-breadcrumb').innerText.includes('BIRDS-4 / Tsuru concept study')")
    dismiss()
    if read("document.querySelector('.architecture-view button:first-child').classList.contains('active')") is False:
        probe.click('.architecture-view button:first-child')
    if run:
        run_ready()


def run_ready():
    close_sheet()
    if not read("document.querySelector('.topbar .run-all').disabled"):
        probe.click('.topbar .run-all')
    dismiss()


def export_ui(name):
    read("""(() => {const p=HTMLAnchorElement.prototype;
      window.__owOriginalAnchorClick=p.click;window.__owExport=null;
      p.click=function(...args){if(this.download&&this.href.startsWith('blob:')){
        window.__owExport={filename:this.download,promise:fetch(this.href).then(r=>r.text())};return;}
        return window.__owOriginalAnchorClick.apply(this,args);};return true;})()""")
    try:
        probe.click('[aria-label="Export design JSON"]')
        probe.wait_js('!!window.__owExport')
        captured=read('(async()=>({filename:window.__owExport.filename,text:await window.__owExport.promise}))()')
        path=probe.output/(name+'.json')
        path.write_text(captured['text'],encoding='utf-8')
        probe.save(name+'-sink.json',{'suggestedFilename':captured['filename'],'nativeSaveTested':False})
        return json.loads(captured['text']),path
    finally:
        read('HTMLAnchorElement.prototype.click=window.__owOriginalAnchorClick;delete window.__owOriginalAnchorClick;delete window.__owExport')
        dismiss()


def import_ui(path):
    path=Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError('Import fixture outside owned directory')
    cdp('DOM.enable')
    cdp('Page.setInterceptFileChooserDialog',enabled=True)
    frame=cdp('Page.getFrameTree')['frameTree']['frame']['id']
    try:
        probe.click('[aria-label="Import design JSON"]')
        deadline=time.monotonic()+4
        chooser=None
        while time.monotonic()<deadline and chooser is None:
            events=drain_events()
            probe.browser_log.extend(e for e in events if e.get('method') in {'Log.entryAdded','Runtime.exceptionThrown','Network.loadingFailed'})
            chooser=next((e['params'] for e in events if e.get('method')=='Page.fileChooserOpened' and e['params'].get('frameId')==frame),None)
            if chooser is None:
                time.sleep(.05)
        if chooser is None:
            raise RuntimeError('Owned file chooser event not received')
        cdp('DOM.setFileInputFiles',backendNodeId=chooser['backendNodeId'],files=[str(path)])
    finally:
        cdp('Page.setInterceptFileChooserDialog',enabled=False)


def authored():
    return read("JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1'))")


def smoke():
    reset(False)
    initial=statuses()
    probe.check('sample status counts',list(initial.values()).count('complete')==7 and initial.get('candidates')=='ready' and list(initial.values()).count('locked')==2,initial)
    probe.check('ten nodes and nineteen edges',read("document.querySelectorAll('.react-flow__node').length===10&&document.querySelectorAll('.react-flow__edge').length===19"))
    probe.check('six persistent roles',read("document.querySelectorAll('.architecture-role').length===6"))
    probe.snapshot('birds4-sample')
    node('orbit')
    probe.check('graph selection opens inspector',read("document.querySelector('.sheet-heading').innerText.includes('Orbit geometry')"))
    probe.snapshot('orbit-inspector')
    close_sheet();run_ready()
    probe.check('all ten current',set(statuses().values())=={'complete'},statuses())
    probe.snapshot('all-current')
    node('mission');fill(field('Orbit altitude'),'450');close_sheet()
    probe.check('actual altitude 450',authored()['inputs']['mission']['altitudeKm']==450)
    s=statuses()
    probe.check('mission stale closure',s.get('scenarios')=='complete' and sum(v=='stale' for v in s.values())==9,s)
    node('candidates')
    probe.check('stale selectors disabled',read("document.querySelectorAll('.candidate-selects select').length>0&&[...document.querySelectorAll('.candidate-selects select')].every(e=>e.disabled)"))
    probe.snapshot('stale-candidate-gate')
    close_sheet();run_ready()
    probe.check('recompute restores all current',set(statuses().values())=={'complete'})
    reset()


def scenarios():
    reset();tab('scenarios')
    probe.check('routine demand preview',read("document.querySelector('.scenario-preview-stats').innerText.includes('0.66')&&document.querySelector('.scenario-preview-stats').innerText.includes('3.34')"))
    move='[aria-label="Move CAM imaging window 1"]'
    end='[aria-label="End of CAM imaging window 1"]'
    start='[aria-label="Start of CAM imaging window 1"]'
    width=read('document.querySelector('+json.dumps(move)+').closest("[data-scenario-track]").getBoundingClientRect().width')
    move_method='pointer'
    try:
        probe.point(move)
    except RuntimeError as error:
        # Confirmed app defect at 1280px: resize handles cover the baseline 3% window.
        # Preserve the failed case, then exercise the real keyboard alternative.
        probe.save('baseline-pointer-blocked.json',{'finding':'R1','error':str(error),'trackWidth':width})
        move_method='keyboard workaround for R1'
    probe.snapshot('cam-before-drag')
    if move_method=='pointer':
        probe.drag(move,width*.05)
    else:
        read('document.querySelector('+json.dumps(move)+').focus()')
        for _ in range(5):press_key('ArrowRight')
    probe.check('CAM move to 21-24 percent',read('Number(document.querySelector('+json.dumps(move)+').getAttribute("aria-valuenow"))')==21 and read('Number(document.querySelector('+json.dumps(end)+').getAttribute("aria-valuenow"))')==24,{'method':move_method})
    probe.drag(end,width*.03)
    probe.check('CAM resize end 27',read('Number(document.querySelector('+json.dumps(end)+').getAttribute("aria-valuenow"))')==27)
    probe.click('[aria-label="CAM imaging load"] .scenario-numeric-summary')
    fill('[aria-label="CAM imaging window 1 start (%)"]',20)
    fill('[aria-label="CAM imaging window 1 end (%)"]',26)
    probe.point(move);read('document.querySelector('+json.dumps(move)+').focus()');press_key('ArrowRight')
    probe.check('window keyboard 1 percent',read('Number(document.querySelector('+json.dumps(move)+').getAttribute("aria-valuenow"))')==21)
    press_key('ArrowLeft',modifiers=8)
    probe.check('window keyboard shift tenth percent',math.isclose(read('Number(document.querySelector('+json.dumps(move)+').getAttribute("aria-valuenow"))'),20.9,abs_tol=.01))
    probe.snapshot('cam-pointer-numeric-keyboard')
    # Empty numeric draft restores previous committed value with visible guidance.
    before=value('[aria-label="CAM imaging window 1 start (%)"]')
    probe.fill('[aria-label="CAM imaging window 1 start (%)"]','',commit='Enter')
    probe.check('empty draft retained previous timing',value('[aria-label="CAM imaging window 1 start (%)"]')==before)
    probe.check('empty numeric guidance',read("document.querySelector('[aria-label=\"CAM imaging load\"]').innerText.includes('Previous value kept')"))
    # Draft cancellation, both resize handles, and geometric bounds.
    probe.fill('[aria-label="CAM imaging window 1 start (%)"]','23',commit=None);press_key('Escape')
    probe.check('Escape cancels numeric draft',value('[aria-label="CAM imaging window 1 start (%)"]')==before)
    probe.point(start);read('document.querySelector('+json.dumps(start)+').focus()');press_key('ArrowRight')
    probe.check('start handle keyboard resize',math.isclose(float(value('[aria-label="CAM imaging window 1 start (%)"]')),21.9,abs_tol=.01))
    press_key('End')
    probe.check('minimum window width tenth percent',math.isclose(float(value('[aria-label="CAM imaging window 1 end (%)"]'))-float(value('[aria-label="CAM imaging window 1 start (%)"]')),.1,abs_tol=.01))
    fill('[aria-label="CAM imaging window 1 start (%)"]',20.9)
    probe.point(move);read('document.querySelector('+json.dumps(move)+').focus()');press_key('Home')
    probe.check('move Home reaches zero',float(value('[aria-label="CAM imaging window 1 start (%)"]'))==0)
    press_key('End')
    probe.check('move End reaches orbit end',float(value('[aria-label="CAM imaging window 1 end (%)"]'))==100)
    fill('[aria-label="CAM imaging window 1 start (%)"]',20.9)
    fill('[aria-label="CAM imaging window 1 end (%)"]',26.9)
    p=probe.point(move)
    cdp('Input.dispatchMouseEvent',type='mousePressed',x=p['x'],y=p['y'],button='left',buttons=1,clickCount=1)
    cdp('Input.dispatchMouseEvent',type='mouseMoved',x=p['x']+width*.02,y=p['y'],button='left',buttons=1)
    press_key('Escape')
    cdp('Input.dispatchMouseEvent',type='mouseReleased',x=p['x']+width*.02,y=p['y'],button='left',buttons=0,clickCount=1)
    probe.check('Escape cancels pointer drag',math.isclose(float(value('[aria-label="CAM imaging window 1 start (%)"]')),20.9,abs_tol=.01))
    probe.drag(move,0,dy=100)
    probe.check('outside release ends drag',read("!document.querySelector('.scenario-is-dragging')"))
    tab('graph');s=statuses()
    probe.check('scenario edit stale closure',s.get('mission')==s.get('orbit')=='complete' and sum(v=='stale' for v in s.values())==8,s)
    run_ready();probe.check('scenario recompute current',set(statuses().values())=={'complete'})
    # Author a separate load to verify overlapping windows union correctly.
    tab('scenarios');probe.click('.scenario-editor-header .scenario-button-primary')
    fill('[aria-label="New load 8 active power (W)"]',10)
    fill('[aria-label="New load 8 idle power (W)"]',2)
    probe.click('[aria-label="New load 8 load"] .scenario-numeric-summary')
    fill('[aria-label="New load 8 window 1 end (%)"]',40)
    fill('[aria-label="New load 8 window 1 start (%)"]',20)
    probe.click('[aria-label="Add New load 8 window"]')
    fill('[aria-label="New load 8 window 2 start (%)"]',30)
    fill('[aria-label="New load 8 window 2 end (%)"]',50)
    text=read("document.querySelector('[aria-label=\"New load 8 load\"]').innerText")
    probe.check('union duty thirty percent and 4.40W', '30%' in text and '4.40 W avg' in text,text)
    probe.snapshot('overlapping-windows')
    run_ready();union,_=export_ui('union-budget')
    probe.check('engine budget agrees with union preview',math.isclose(union['analysis']['budget']['averageW'],5.1092,abs_tol=1e-8),union['analysis']['budget']['averageW'])
    probe.click('[aria-label="Remove New load 8 load"]')
    reset()


def energy():
    reset();tab('assessments')
    probe.check('all twenty EPS requirements present',read("[...document.querySelectorAll('.check-id')].filter(e=>/^EPS-\\d\\d$/.test(e.textContent)).length===20"))
    checks=read("[...document.querySelectorAll('.check-item')].map(e=>({id:e.querySelector('.check-id').textContent,verdict:e.className}))")
    probe.check('EPS10 and EPS11 missing-charge unassessed',all('unassessed' in next(e['verdict'] for e in checks if e['id']==i) for i in ['EPS-10','EPS-11']),checks)
    probe.snapshot('routine-requirement-report')
    probe.click('.report-tabs button:nth-child(2)')
    probe.check('stored energy model warning',read("document.querySelector('.energy-report').innerText.includes('not charge-based state of charge')"))
    probe.point('.stored-energy-plot');probe.snapshot('routine-energy-percent')
    probe.click('[aria-label="Stored energy units"] button:nth-child(2)')
    probe.snapshot('routine-energy-wh')
    data,_=export_ui('routine-export')
    sim=data['analysis']['simulation']
    probe.check('routine physical initial energy',math.isclose(sim['capacityWh'],6.4) and math.isclose(sim['startEnergyWh'],4.608),sim['startEnergyWh'])
    probe.check('energy percent mapping',all(math.isclose(p['energyPercent'],100*p['batteryWh']/sim['capacityWh'],abs_tol=1e-6) for p in sim['points']))
    # Use the actual scenario select and require historic/current separation.
    select_value(field('Active scenario','.assessment-context'),'birds4-stress')
    probe.wait_js("document.querySelector('.assessment-page').innerText.includes('Saved report is out of date')")
    probe.check('stress switch explicitly stale',read("document.querySelector('.assessment-page').innerText.includes('Saved report is out of date')"))
    probe.snapshot('stress-stale-history')
    run_ready()
    stress,_=export_ui('stress-export')
    sim=stress['analysis']['simulation']
    probe.check('stress average and peak',math.isclose(stress['analysis']['budget']['averageW'],2.8165,abs_tol=1e-8) and math.isclose(stress['analysis']['budget']['peakW'],5.2,abs_tol=1e-8))
    probe.check('stress known energy failure',any(c['verdict']=='fail' and c['id'] in ['EPS-10','EPS-11'] for c in stress['analysis']['checks']),stress['analysis']['checks'])
    probe.check('stress result identity',sim['scenarioId']=='birds4-stress')
    probe.point('.stored-energy-plot');probe.snapshot('stress-failed-energy')
    select_value(field('Active scenario','.assessment-context'),'birds4-survival');run_ready()
    survival,_=export_ui('survival-export')
    probe.check('survival three orbit reduced-generation inputs',survival['inputs']['activeScenarioId']=='birds4-survival' and next(s for s in survival['inputs']['scenarios'] if s['id']=='birds4-survival')['durationOrbits']==3)
    probe.point('.stored-energy-plot');probe.snapshot('reduced-generation-energy')
    reset()


def inspect_product(query):
    tab('catalog')
    fill('[aria-label="Search catalog products"]',query,commit=None)
    probe.wait_js("document.querySelectorAll('.product-card').length===1")
    probe.click('.product-card .text-button')
    probe.wait_js("!!document.querySelector('.allocation-controls')")


def apply():
    probe.click('.allocation-controls .button.primary')


def catalog_flow():
    reset();tab('catalog')
    select_value(field('CSRM role','.catalog-filters'),'battery')
    manufacturer=field('Manufacturer','.catalog-filters')
    cesi=next(v for v in read('[...document.querySelector('+json.dumps(manufacturer)+').options].map(e=>e.value)') if 'CESI' in v)
    select_value(manufacturer,cesi)
    probe.check('combined filter empty state',read("!!document.querySelector('.large-empty')"))
    probe.snapshot('catalog-empty-filter')
    probe.click('.large-empty .button')
    inspect_product('BP8')
    index=read("[...document.querySelectorAll('.specification')].findIndex(e=>e.querySelector('summary span').textContent==='Rated energy')+1")
    probe.click(f'.specification:nth-child({index}) summary')
    probe.point(f'.specification:nth-child({index})')
    probe.check('spec original conditions location source',read(f"document.querySelector('.specification:nth-child({index})').innerText.includes('Conditions')&&document.querySelector('.specification:nth-child({index})').innerText.includes('Original')&&document.querySelector('.specification:nth-child({index})').innerText.includes('Source')"))
    probe.snapshot('bp8-sourced-energy')
    probe.save('not-applicable-display.json',read("[...document.querySelectorAll('.specification.not-applicable summary')].map(e=>e.innerText)"))
    apply();close_sheet();run_ready()
    probe.check('pack sourced 86Wh',authored()['inputs']['battery']['capacityWh']==86)
    inspect_product('P80');probe.snapshot('p80-incomplete-inspector');apply();close_sheet();run_ready()
    probe.check('integrated role allocations',len(authored()['selections'])==4 and len(set(authored()['selections'].values()))==2,authored()['selections'])
    probe.click('.architecture-view button:nth-child(2)')
    probe.check('unique two physical usages',read("document.querySelectorAll('.bom-item').length===2"))
    probe.snapshot('deduplicated-physical-bom')
    data,_=export_ui('allocated-export')
    probe.check('export deduplicates selected entries',len(data['selectedCatalogEntries'])==2)
    probe.save('rejected-visual-check.json',{'status':'data-blocked' if not any(s['outcome']=='rejected' for s in data['analysis']['suggestions']) else 'available','outcomes':[s['outcome'] for s in data['analysis']['suggestions']]})
    reset();inspect_product('CTJ30');apply();close_sheet();tab('graph');node('solar')
    probe.check('CESI unknown EOL clears prior cell values',value(field('Cell EOL MPP voltage'))=='' and value(field('Cell EOL MPP current'))=='')
    probe.snapshot('cesi-missing-eol-gate')
    reset();inspect_product('ICEPS2');select_value(field('Selection role'),'conditioning');apply();close_sheet();tab('graph');node('battery')
    probe.check('ICEPS unknown capacity cleared',value(field('BOL pack energy'))=='')
    probe.snapshot('iceps-missing-capacity-gate')
    fill(field('BOL pack energy'),8);close_sheet();run_ready()
    before=authored()['selections'];inspect_product('BP8');apply()
    probe.wait_js("!!document.querySelector('[role=alert]')")
    probe.check('integrated fixed battery blocks separate pack',read("document.querySelector('[role=alert]').innerText.includes('fixed battery')") and authored()['selections']==before)
    probe.snapshot('integrated-battery-blocked-replacement')
    dismiss();reset()


def io_flow():
    reset()
    inspect_product('BP8');apply();close_sheet();run_ready()
    inspect_product('P80');apply();close_sheet();run_ready()
    tab('scenarios');probe.click('[aria-label="CAM imaging load"] .scenario-numeric-summary')
    fill('[aria-label="CAM imaging window 1 end (%)"]',24)
    fill('[aria-label="CAM imaging window 1 start (%)"]',21)
    run_ready();tab('graph')
    baseline,path=export_ui('roundtrip-original')
    probe.check('roundtrip fixture contains physical allocations and authored schedule edit',len(baseline['selections'])==4 and len(baseline['selectedCatalogEntries'])==2 and baseline['inputs']['scenarios'][0]['loads'][2]['windows'][0]['start']==.21)
    before=authored();before_status=statuses()
    fixtures={
      'malformed':'{this is not json',
      'unsupported':json.dumps({'schemaVersion':99}),
      'missing':json.dumps({'schemaVersion':1}),
    }
    wrong=json.loads(json.dumps(baseline));wrong['inputs']['mission']['altitudeKm']='400';fixtures['wrong-number']=json.dumps(wrong)
    unknown=json.loads(json.dumps(baseline));unknown['selections']['solar']='nonexistent-test-product';fixtures['unknown-product']=json.dumps(unknown)
    fixtures['oversized']=json.dumps(baseline)+' '*(2_000_001-len(json.dumps(baseline)))
    for name,text in fixtures.items():
        fixture=probe.output/(name+'.json');fixture.write_text(text,encoding='utf-8')
        import_ui(fixture);probe.wait_js("!!document.querySelector('[role=alert]')")
        probe.check('invalid '+name+' preserves authored state',authored()==before)
        probe.check('invalid '+name+' preserves result currency',statuses()==before_status)
        probe.save(name+'-error.json',read("document.querySelector('[role=alert]').innerText"))
        if name in {'malformed','oversized'}:probe.snapshot('import-error-'+name)
        dismiss()
    node('mission');fill('#mission-name','Round trip temporary edit');close_sheet()
    import_ui(path)
    probe.wait_js("document.querySelector('.mission-breadcrumb').innerText.includes('BIRDS-4 / Tsuru concept study')")
    probe.check('round trip authored inputs and selections',authored()==before)
    probe.check('import drops all cached current labels',sum(s=='complete' for s in statuses().values())==0 and sum(s=='ready' for s in statuses().values())==2,statuses())
    probe.snapshot('roundtrip-caches-discarded')
    run_ready();restored,_=export_ui('roundtrip-recomputed')
    probe.check('recomputed analysis equals original',restored['analysis']==baseline['analysis'])
    import_ui(path);probe.wait_js("document.querySelectorAll('.workflow-node.complete').length===0")
    probe.check('same file imports a second time',sum(s=='ready' for s in statuses().values())==2)
    run_ready()
    # Reload only this owned page. Persistence restores authored state, never cached outputs.
    cdp('Page.reload',ignoreCache=True)
    probe.wait_js("!!document.querySelector('.app-shell')")
    probe.wait_js("document.querySelectorAll('.workflow-node').length===10")
    probe.check('reload preserves authored inputs',authored()==before)
    probe.check('reload drops calculations',sum(s=='complete' for s in statuses().values())==0)
    probe.snapshot('reload-authored-only')
    reset()


def blank():
    reset();probe.click('.topbar .button.quiet');probe.click('.confirm-actions .button.primary');dismiss()
    probe.check('blank all ten locked',set(statuses().values())=={'locked'},statuses())
    probe.check('blank no allocations',authored()['selections']=={})
    probe.check('blank Run ready disabled',read("document.querySelector('.topbar .run-all').disabled"))
    probe.snapshot('blank-design')
    node('orbit')
    probe.check('locked dependency explanation',read("document.querySelector('.sheet').innerText.includes('Evaluate it first')"))
    probe.snapshot('blank-locked-orbit')
    close_sheet();node('mission');fill('#mission-name','Live test mission');fill(field('Orbit altitude'),400);fill(field('Mission lifetime'),1)
    close_sheet();run_ready()
    probe.check('new inputs unlock mission and orbit only',statuses().get('mission')==statuses().get('orbit')=='complete' and sum(s=='complete' for s in statuses().values())==2,statuses())
    tab('scenarios');probe.click('.large-empty .button.primary');probe.click('.scenario-editor-header .scenario-button-primary')
    probe.check('new scenario and load authored',len(authored()['inputs']['scenarios'])==1 and len(authored()['inputs']['scenarios'][0]['loads'])==1)
    probe.snapshot('new-mission-scenario')
    reset();node('topology');select_value(field('Conditioning strategy'),'DET');close_sheet();run_ready();node('simulation')
    probe.check('DET unsupported model gate',read("document.querySelector('.sheet').innerText.includes('I–V operating point')") and read("document.querySelector('.node-run-footer .button').disabled"))
    probe.snapshot('det-explanation')
    close_sheet();reset()


def polish():
    reset();probe.click('[aria-label="Expand graph"]');probe.snapshot('expanded-graph')
    probe.click('[aria-label="Exit expanded graph"]');probe.click('.graph-controls button[title="Fit all nodes"]')
    node('orbit')
    probe.check('dialog receives focus',read("document.querySelector('.sheet').contains(document.activeElement)"))
    press_key('Tab',modifiers=8)
    probe.check('dialog ShiftTab focus trap',read("document.querySelector('.sheet').contains(document.activeElement)"))
    close_sheet();probe.check('close leaves no modal',read("!document.querySelector('[role=dialog]')"))
    tab('assessments')
    probe.save('report-freshness-visibility.json',read("[...document.querySelectorAll('.report-freshness>span')].map(e=>({text:e.textContent,display:getComputedStyle(e).display}))"))
    probe.click('.report-tabs button:nth-child(2)');probe.point('.check-list')
    probe.snapshot('energy-check-label-overlap')
    geometry=read("""(() => [...document.querySelectorAll('.energy-report .check-summary')].map(e=>{
      const id=e.querySelector('.check-id'), title=e.querySelector('.check-title');
      const a=id.getBoundingClientRect(),b=title.getBoundingClientRect();
      const r=document.createRange();r.selectNodeContents(id);const t=r.getBoundingClientRect();
      return {id:id.textContent,title:title.textContent,idColumnRight:a.right,idTextRight:t.right,titleLeft:b.left,overlapPx:Math.max(0,t.right-b.left)};}))()""")
    probe.save('check-label-geometry.json',geometry)
    tab('graph')
    styles=read("""(() => {
      const selectors=['.graph-hint','.node-req','.node-caption','.role-value','.role-state','.architecture-explainer','.preliminary-note','.graph-panel-footer'];
      return selectors.flatMap(selector=>[...document.querySelectorAll(selector)].slice(0,2).map(e=>{
        const s=getComputedStyle(e), backgrounds=[];for(let p=e;p;p=p.parentElement){const c=getComputedStyle(p);backgrounds.push({color:c.backgroundColor,image:c.backgroundImage});}
        const r=e.getBoundingClientRect();return {selector,text:e.innerText,color:s.color,fontSize:s.fontSize,scale:e.offsetWidth?r.width/e.offsetWidth:1,backgrounds};}));})()""")
    probe.save('readability-styles.json',styles)
    probe.snapshot('readability-baseline')
    reset()


phase=os.environ.get('EPS_TEST_PHASE','smoke')
probe.check('owned origin',read('location.origin')=='http://127.0.0.1:5173')
flows={'smoke':smoke,'scenarios':scenarios,'energy':energy,'catalog':catalog_flow,'io':io_flow,'blank':blank,'polish':polish}
for name,flow in flows.items():
    if phase in {name,'all'}:
        flow()
probe.check('no document horizontal overflow',read('document.documentElement.scrollWidth<=innerWidth+1'))
probe.snapshot('finished-'+phase)
