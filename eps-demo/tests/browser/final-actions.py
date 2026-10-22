"""Focused final GUI follow-up. EPS_FINAL_PHASE=regressions|mission|kicad|preview.
Only browser UI controls modify the app. Binary Blob sinks are target-local.
Synthetic physical-rule fixtures are explicitly not engineering evidence.
"""
import ast
import base64
import copy
import json
import math
import os
import re
import time
import zipfile
from pathlib import Path

# Reuse previously live-validated UI primitives without executing old workflows.
_tree=ast.parse((ROOT/'workflow.py').read_text())
exec(compile(ast.Module(body=[n for n in _tree.body if isinstance(n,(ast.FunctionDef,ast.Import,ast.ImportFrom))],type_ignores=[]),'workflow-helpers','exec'),globals())


def has(selector): return read('!!document.querySelector('+json.dumps(selector)+')')

def actual_origin(): return read('location.origin')


def click_text(text, scope='.sheet'):
    selector=read("""(() => {const root=document.querySelector(SCOPE);
      const e=[...root.querySelectorAll('button,summary')].find(e=>e.textContent.trim()===TEXT);
      if(!e)throw Error('No visible control '+TEXT);return {tag:e.tagName,index:[...root.querySelectorAll(e.tagName.toLowerCase())].indexOf(e)};})()""".replace('SCOPE',json.dumps(scope)).replace('TEXT',json.dumps(text)))
    # Build a unique selector from semantic discovery, without changing DOM attributes.
    tag=selector['tag'].lower()
    matches=read("[...document.querySelector("+json.dumps(scope)+").querySelectorAll("+json.dumps(tag)+")].map(e=>e.textContent.trim())")
    # Prefer :has text via exact matched DOM index represented by a full CSS ancestry.
    css=read("""(() => {const root=document.querySelector(SCOPE),e=[...root.querySelectorAll(TAG)][INDEX];
      const path=[];let p=e;while(p!==root){const tag=p.tagName.toLowerCase();const i=[...p.parentElement.children].filter(x=>x.tagName===p.tagName).indexOf(p)+1;path.unshift(tag+':nth-of-type('+i+')');p=p.parentElement;}return SCOPE+' > '+path.join(' > ');})()""".replace('SCOPE',json.dumps(scope)).replace('TAG',json.dumps(tag)).replace('INDEX',str(selector['index'])))
    probe.click(css)


def snapshot(label):
    dismiss();probe.snapshot(label)


def open_assist():
    node('mission')
    if not read("document.querySelector('.mission-helper-entry').open"):
        probe.click('.mission-helper-entry > summary')
    probe.wait_js("!!document.querySelector('.mission-assist textarea')")


def open_kicad():
    close_sheet();probe.click('[aria-label="Open KiCad handoff"]')
    probe.wait_js("!!document.querySelector('.kicad-panel__footer')",timeout=10)


def get_blob(selector, filename):
    read("""(() => {const p=HTMLAnchorElement.prototype;window.__owClick=p.click;window.__owBlob=null;
      p.click=function(...args){if(this.download&&this.href.startsWith('blob:')){
        const href=this.href;window.__owBlob={name:this.download,promise:fetch(href).then(async r=>{
          const blob=await r.blob(),a=new Uint8Array(await blob.arrayBuffer());let s='';
          for(let i=0;i<a.length;i+=32768)s+=String.fromCharCode(...a.subarray(i,i+32768));
          return {mime:blob.type,bytes:a.length,base64:btoa(s)};})};return;}
        return window.__owClick.apply(this,args);};return true;})()""")
    try:
        probe.click(selector);probe.wait_js('!!window.__owBlob',timeout=10)
        data=read('(async()=>({name:window.__owBlob.name,...await window.__owBlob.promise}))()')
        path=probe.output/filename;path.write_bytes(base64.b64decode(data.pop('base64')))
        probe.save(filename+'-sink.json',dict(data,nativeSaveTested=False))
        return path
    finally:
        read('HTMLAnchorElement.prototype.click=window.__owClick;delete window.__owClick;delete window.__owBlob')


def import_file(selector,path):
    path=Path(path).resolve()
    if ROOT not in path.parents:raise ValueError('Fixture outside owned directory')
    cdp('DOM.enable');cdp('Page.setInterceptFileChooserDialog',enabled=True)
    frame=cdp('Page.getFrameTree')['frameTree']['frame']['id']
    try:
        probe.click(selector);deadline=time.monotonic()+4;chooser=None
        while time.monotonic()<deadline and chooser is None:
            events=drain_events();probe.browser_log.extend(events)
            chooser=next((e['params'] for e in events if e.get('method')=='Page.fileChooserOpened' and e['params'].get('frameId')==frame),None)
            if chooser is None:time.sleep(.05)
        if chooser is None:raise RuntimeError('No owned chooser event')
        cdp('DOM.setFileInputFiles',backendNodeId=chooser['backendNodeId'],files=[str(path)])
    finally:cdp('Page.setInterceptFileChooserDialog',enabled=False)


def safe_unzip(path,label):
    dest=probe.output/label;dest.mkdir()
    with zipfile.ZipFile(path) as z:
        probe.check(label+' ZIP CRC integrity',z.testzip() is None)
        for name in z.namelist():
            target=(dest/name).resolve()
            if dest.resolve() not in target.parents:raise ValueError('Unsafe ZIP path')
        z.extractall(dest)
        probe.save(label+'-file-list.json',z.namelist())
    return dest


def numerical_model():
    inputs=copy.deepcopy(authored()['inputs'])
    inputs['mission'].pop('conOps',None);inputs['mission'].pop('orbitSuggestion',None)
    return inputs


def semantic_count():
    return read("performance.getEntriesByType('resource').filter(e=>e.name==='http://127.0.0.1:8767/embed').length")


def regressions():
    reset();snapshot('corrected-graph')
    styles=read("""(() => {return ['.graph-hint','.role-state','.architecture-explainer'].map(selector=>{
      const e=document.querySelector(selector),s=getComputedStyle(e);let p=e,bg;
      while(p){bg=getComputedStyle(p).backgroundColor;if(!bg.startsWith('rgba')&&bg!=='transparent')break;p=p.parentElement;}
      return {selector,text:e.innerText,color:s.color,fontSize:parseFloat(s.fontSize),background:bg,display:s.display};});})()""")
    def rgb(s):return list(map(float,re.findall(r'[\d.]+',s)))[:3]
    def lum(c):return sum(w*(v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4) for v,w in zip(c,[.2126,.7152,.0722]))
    for x in styles:
        a,b=sorted([lum(rgb(x['color'])),lum(rgb(x['background']))],reverse=True);x['contrast']=(a+.05)/(b+.05)
    probe.save('corrected-guidance-styles.json',styles)
    probe.check('R5 guidance readable contrast and size',all(x['contrast']>=4.5 and x['fontSize']>=10 for x in styles),styles)
    tab('assessments')
    badge=read("getComputedStyle(document.querySelector('.report-freshness .status-badge')).display")
    probe.check('R4 freshness badge visible',badge!='none',badge)
    snapshot('corrected-freshness-badge')
    probe.click('.report-tabs button:nth-child(2)');probe.point('.check-list')
    geometry=read("""(() => [...document.querySelectorAll('.energy-report .check-item.long-id')].map(e=>{
      const id=e.querySelector('.check-id'),title=e.querySelector('.check-title');const r=document.createRange();r.selectNodeContents(id);
      const a=r.getBoundingClientRect(),b=title.getBoundingClientRect();return {id:id.textContent,idBottom:a.bottom,titleTop:b.top,
      overlap:Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left))*Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top))};}))()""")
    probe.check('R2 long IDs use nonoverlapping rows',len(geometry)>=4 and all(x['overlap']==0 and x['titleTop']>=x['idBottom'] for x in geometry),geometry)
    probe.save('long-id-geometry.json',geometry);snapshot('corrected-long-check-ids')
    inspect_product('BP8')
    rows=read("[...document.querySelectorAll('.specification.not-applicable summary')].map(e=>e.innerText)")
    probe.check('R3 N/A values distinct from missing',len(rows)>0 and all('Not applicable' in x and 'Not published' not in x for x in rows),rows)
    probe.point('.specification-list > .specification:first-child');snapshot('corrected-not-applicable')
    # Saved energy criteria must remain attached to the historical run.
    reset();tab('assessments');probe.click('.report-tabs button:nth-child(2)')
    old=read("({reserve:Number(document.querySelector('.energy-plots').dataset.reserveWh),duration:Number(document.querySelector('.energy-plots').dataset.durationS)})")
    probe.check('old routine reserve is 1.6 Wh',math.isclose(old['reserve'],1.6))
    tab('scenarios');probe.click('.scenario-settings > summary');fill('[aria-label="Minimum energy reserve fraction (%)"]',50)
    tab('assessments');probe.click('.report-tabs button:nth-child(2)')
    saved=read("Number(document.querySelector('.energy-plots').dataset.reserveWh)")
    probe.check('historical reserve remains old 1.6 Wh before compute',math.isclose(saved,1.6))
    probe.point('.stored-energy-plot');snapshot('historical-reserve-unchanged')
    run_ready();probe.wait_js("Number(document.querySelector('.energy-plots').dataset.reserveWh)===3.2")
    probe.check('new reserve after compute is 3.2 Wh',read("Number(document.querySelector('.energy-plots').dataset.reserveWh)===3.2"))
    probe.point('.stored-energy-plot');snapshot('recomputed-reserve-3.2Wh')
    reset();node('mission');fill(field('Orbit altitude'),820);close_sheet()
    # Recompute mission/orbit only, leaving the old budget historical.
    probe.click('.react-flow__node[data-id="mission"] .workflow-node');probe.click('.node-run-footer .button');close_sheet()
    node('orbit');probe.click('.node-run-footer .button');close_sheet();node('budget')
    basis=read("document.querySelector('.demand-plot')?.closest('.plot-card')?.outerHTML")
    probe.save('historical-budget-ui.html.json',basis);probe.point('.demand-plot');snapshot('historical-budget-timing')
    cached,_=export_ui('historical-budget-export')
    probe.check('budget retains its old orbit timing',cached['analysis']['budget']['orbitPeriodS']!=cached['analysis']['orbit']['periodS'])
    reset()


def mission():
    reset();before=numerical_model();open_assist();click_text('Vegetation imaging','.mission-assist')
    probe.wait_js("document.querySelector('.mission-assist textarea').value.includes('vegetation')")
    probe.check('ConOps draft changes no numerical inputs',numerical_model()==before)
    probe.check('ConOps authored edit marks nine stale',sum(v=='stale' for v in statuses().values())==9,statuses())
    probe.click('.ma-search')
    probe.wait_js("document.querySelectorAll('.ma-card').length>0 || !!document.querySelector('.ma-error')",timeout=115)
    probe.check('real Qwen semantic search succeeds',not has('.ma-error') and read("document.querySelector('.ma-result-label').innerText.includes('Semantic Qwen cosine')"))
    cards=read("[...document.querySelectorAll('.ma-card')].map(e=>({name:e.querySelector('h4').textContent,text:e.innerText,score:e.querySelector('.ma-score').textContent}))")
    probe.save('semantic-visible-matches.json',cards)
    index=next(i for i,x in enumerate(cards) if x['name']=='Proba-V')+1
    card=f'.ma-card:nth-of-type({index})'
    probe.check('Proba V source and non-CubeSat context', '820' in cards[index-1]['text'] and 'not a cubesat' in cards[index-1]['text'].lower(),cards[index-1])
    probe.check('search alone leaves orbit parameters unchanged',numerical_model()==before)
    probe.check('explicit acceptance disabled before checkbox',read(f"document.querySelector('{card} .ma-accept button').disabled"))
    probe.point(card);snapshot('real-Qwen-Proba-V-result')
    # Recompute the authored query revision first, then prove accepting altitude stales it anew.
    probe.click('.topbar .run-all');dismiss();probe.wait_js("document.querySelectorAll('.workflow-node.complete').length===10")
    probe.click(card+' .ma-accept input');probe.click(card+' .ma-accept button')
    probe.wait_js("JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1')).inputs.mission.altitudeKm===820")
    receipt=authored()['inputs']['mission'].get('orbitSuggestion');probe.save('accepted-orbit-receipt.json',receipt)
    after=numerical_model();expected=copy.deepcopy(before);expected['mission']['altitudeKm']=820
    probe.check('acceptance changes only sourced altitude',after==expected)
    probe.check('accepted source marks exact nine-node closure',sum(v=='stale' for v in statuses().values())==9 and statuses()['scenarios']=='complete',statuses())
    keys=['missionId','missionRevision','missionStatus','missionEpoch','catalogueRevision','method','cosine','parameterOriginal','parameterMeaning','parameterSourceIds','sources','acceptedAt','query']
    probe.check('receipt preserves complete source context',all(receipt.get(k) is not None for k in keys) and receipt['method']=='semantic-qwen' and receipt['missionId']=='proba-v')
    probe.point(field('Orbit altitude'));snapshot('accepted-820km-source-receipt')
    saved,path=export_ui('accepted-design');probe.click('.topbar .load-example');dismiss();import_file('[aria-label="Import design JSON"]',path)
    probe.wait_js("JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1')).inputs.mission.altitudeKm===820")
    probe.check('receipt and query round trip exactly',authored()['inputs']['mission']['orbitSuggestion']==receipt and authored()['inputs']['mission']['conOps']==receipt['query'])
    probe.check('accepted import discards result caches',all(v!='complete' for v in statuses().values()))
    open_assist();probe.check('reopened query persists',value('.mission-assist textarea')==receipt['query']);snapshot('reopened-accepted-query')
    fill(field('Orbit altitude'),821)
    probe.check('manual altitude clears prior receipt','orbitSuggestion' not in authored()['inputs']['mission'])
    close_sheet();import_file('[aria-label="Import design JSON"]',path);probe.wait_js("JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1')).inputs.mission.altitudeKm===820")
    open_assist();click_text('Ionosphere radar','.mission-assist')
    probe.check('manual ConOps clears prior receipt','orbitSuggestion' not in authored()['inputs']['mission'])
    before_count=semantic_count();select_value('.mission-assist select','lexical-tfidf');probe.click('.ma-search')
    probe.wait_js("!!document.querySelector('.ma-result-label')")
    probe.check('lexical mode visibly separate',read("document.querySelector('.ma-result-label').innerText.includes('Lexical TF-IDF')"))
    probe.check('lexical mode makes no semantic call',semantic_count()==before_count)
    range_cards=read("[...document.querySelectorAll('.ma-card')].map(e=>({name:e.querySelector('h4').textContent,text:e.innerText,apply:!!e.querySelector('.ma-accept')}))")
    probe.save('lexical-range-results.json',range_cards)
    probe.check('altitude ranges cannot be averaged or applied',any('range retained' in x['text'].lower() and not x['apply'] for x in range_cards),range_cards)
    probe.point('.mission-assist');snapshot('offline-lexical-range-gate')
    select_value('.mission-assist select','semantic-qwen');click_text('Unrelated input','.mission-assist');probe.click('.ma-search')
    probe.wait_js("!!document.querySelector('.ma-result-label') || !!document.querySelector('.ma-error')",timeout=115)
    probe.check('unrelated recipe abstains without fallback',not has('.ma-error') and not has('.ma-card') and read("document.querySelector('.ma-result-label').innerText.includes('Semantic Qwen')"))
    snapshot('semantic-unrelated-abstention')
    # Actual service request cancellation, not a fabricated delayed response.
    click_text('Vegetation imaging','.mission-assist');probe.click('.ma-search')
    busy=read("document.querySelector('.ma-search').disabled")
    busy_text=read("document.querySelector('.mission-assist').innerText")
    if busy:probe.check('busy message preserves orbit-parameter truth','Orbit parameters have not changed.' in busy_text)
    click_text('Unrelated input','.mission-assist')
    time.sleep(.5)
    probe.check('query edit removes old matches and application controls',not has('.ma-card') and not read("document.querySelector('.ma-search').disabled"))
    probe.save('query-currency.json',{'busyObservedBeforeEdit':busy,'busyText':busy_text,'query':value('.mission-assist textarea'),'nativeLateResponseInjected':False})
    snapshot('query-edit-cancels-inflight-result')
    reset()


def kicad():
    reset();open_kicad()
    probe.check('no COTS blocks review download',read("document.querySelector('.kicad-panel__footer .button').disabled") and read("document.querySelector('.sheet').innerText.includes('Allocate at least one')"))
    snapshot('kicad-no-COTS-prerequisite')
    close_sheet();tab('assessments');select_value(field('Active scenario','.assessment-context'),'birds4-stress');run_ready()
    # Sourced changes require fresh candidates after each substitution.
    inspect_product('3G30C');apply();close_sheet();open_kicad()
    probe.check('stale sourced cell change gates review export',read("document.querySelector('.kicad-panel__footer .button').disabled") and read("document.querySelector('.sheet').innerText.includes('stale')"))
    snapshot('kicad-stale-source-prerequisite');close_sheet();run_ready()
    inspect_product('BP8');apply();close_sheet();run_ready()
    inspect_product('P80');apply();close_sheet()
    # Candidates remain current after P80, simulation is stale. Review export is allowed.
    open_kicad();probe.check('review permits simulation-stale current allocations',not read("document.querySelector('.kicad-panel__footer .button').disabled"))
    before=authored();state_before,_=export_ui('pre-review-workspace')
    archive=get_blob('.kicad-panel__footer .button','review.zip');dest=safe_unzip(archive,'review')
    manifest=json.loads((dest/'manifest.json').read_text());probe.save('review-manifest-summary.json',manifest)
    probe.check('review contains real project and child schematics',(dest/'orbitwork-review.kicad_pro').is_file() and len(list(dest.glob('*.kicad_sch')))>=5)
    usages=manifest['usages'];probe.check('integrated P80 is one physical usage',len(usages)==3 and len({u['productId'] for u in usages})==3 and len(next(u for u in usages if 'p80' in u['productId'])['allocatedRoles'])==3)
    source_catalog=json.loads((ROOT.parents[1] / 'src/data/catalog.json').read_text())
    canonical={p['id']:p for p in source_catalog['products']}
    probe.check('exact source revisions URLs and quantities retained',all(u['product']==canonical[u['productId']] and u['catalogEntryRevision']==canonical[u['productId']]['revision'] and u['quantity']>=1 for u in usages))
    probe.check('physical routing blocked and no PCB',manifest['physicalRouting']['status']=='blocked' and manifest['physicalRouting']['boardGenerated'] is False and not list(dest.glob('*.kicad_pcb')))
    after_export,_=export_ui('post-review-workspace')
    probe.check('drawing changes no EPS results or authored design',after_export['analysis']==state_before['analysis'] and authored()==before)
    probe.check('known failure and unknown evidence retained',any(c['verdict']=='fail' for c in after_export['analysis']['checks']) and any(c['verdict']=='unassessed' for c in after_export['analysis']['checks']))
    snapshot('kicad-current-review-export')
    click_text('Import an approved rule profile')
    template_path=get_blob('.kicad-panel__actions button:first-child','rule-template.json');template=json.loads(template_path.read_text())
    probe.check('template contains null physical values and no approval',template['approval']['status']=='unreviewed' and all(v is None for k,v in template['fabrication'].items() if k!='sourceIds'))
    synthetic=json.loads((ROOT.parents[1] / 'kicad/rule-probe/approved-test-input.json').read_text())
    synthetic['architectureFingerprint']=template['architectureFingerprint'];synthetic['catalogRevision']=template['catalogRevision']
    synthetic['scope']='SYNTHETIC TEST ONLY. No physical EPS evidence, derivation or engineering approval.'
    bad_fingerprint=copy.deepcopy(synthetic);bad_fingerprint['architectureFingerprint']='SYNTHETIC-WRONG-FINGERPRINT'
    missing_min=copy.deepcopy(synthetic);del missing_min['fabrication']['minimumTrackWidthMm']
    fixtures=[('unreviewed-template',template_path,None),('malformed',None,'{bad JSON'),('wrong-fingerprint',None,json.dumps(bad_fingerprint)),('missing-fabrication-minimum',None,json.dumps(missing_min))]
    for name,path,text in fixtures:
        if path is None:path=probe.output/(name+'.json');path.write_text(text)
        import_file('.kicad-panel__actions button:nth-child(2)',path)
        probe.wait_js("!!document.querySelector('.sheet [role=alert]')")
        msg=read("document.querySelector('.sheet [role=alert]').innerText")
        probe.save(name+'-rule-error.json',msg)
        probe.check(name+' profile rejected without model overwrite',not has('.kicad-panel__rule-result') and authored()==before,msg)
    snapshot('kicad-invalid-rule-profile-error')
    valid=probe.output/'SYNTHETIC-APPROVED-TEST-PROFILE.json';valid.write_text(json.dumps(synthetic,indent=2))
    import_file('.kicad-panel__actions button:nth-child(2)',valid)
    probe.wait_js("!!document.querySelector('.kicad-panel__rule-result')")
    snapshot('SYNTHETIC-rule-profile-generated')
    sidecar=get_blob('.kicad-panel__rule-result > button','SYNTHETIC-sidecars.zip');side=safe_unzip(sidecar,'SYNTHETIC-sidecars')
    rules=json.loads((side/'physical-rules-manifest.json').read_text());probe.save('SYNTHETIC-rule-manifest.json',rules)
    constraints={r['constraint'] for r in rules['rules']}
    probe.check('sidecar contains exactly three files and five rule types',len(list(side.iterdir()))==3 and constraints=={'track_width','clearance','via_diameter','hole_size','edge_clearance'})
    probe.check('sidecar rules retain source and requirement trace',all(r['approvedDimension']['sourceIds'] and r['approvedDimension']['requirementIds'] for r in rules['rules']) and 'SYNTHETIC' in rules['approval']['engineer'])
    probe.check('sidecar does not generate or validate PCB',rules['generatedBoard'] is False and rules['ruleApplicationValidated'] is False and rules['drc']=='not-run' and not list(side.glob('*.kicad_pcb'))) 
    # Keep panel open. Reevaluation changes the fingerprint of already-generated files.
    old_fingerprint=read("document.querySelector('.kicad-panel__fingerprint').innerText")
    probe.click('.topbar .run-all');dismiss()
    probe.wait_js("document.querySelector('.kicad-panel__fingerprint').innerText!=="+json.dumps(old_fingerprint))
    probe.check('old generated sidecars hidden and explicitly stale',not has('.kicad-panel__rule-result') and read("document.querySelector('.sheet').innerText.includes('Generated rule files are stale')"))
    snapshot('generated-sidecars-stale-after-reevaluation')
    reset()


def preview():
    reset();snapshot('preview-graph')
    tab('scenarios');probe.check('preview scenario lazy UI loads',has('[aria-label="Move CAM imaging window 1"]'));snapshot('preview-scenario-editor')
    tab('assessments');probe.click('.report-tabs button:nth-child(2)');probe.point('.stored-energy-plot');snapshot('preview-charts')
    tab('graph');open_assist();probe.point('.mission-assist');snapshot('preview-mission-assist-lazy')
    click_text('Vegetation imaging','.mission-assist');probe.click('.ma-search')
    probe.wait_js("document.querySelectorAll('.ma-card').length>0 || !!document.querySelector('.ma-error')",timeout=115)
    probe.check('production semantic request and CORS succeed',not has('.ma-error') and read("document.querySelector('.ma-card').innerText.includes('Proba-V')"))
    probe.point('.ma-card');snapshot('preview-semantic-result')
    open_kicad();probe.check('preview KiCad lazy panel loads',has('.kicad-panel__footer'));snapshot('preview-KiCad-lazy')
    reset()


phase=os.environ.get('EPS_FINAL_PHASE','regressions')
probe.check('approved loopback app origin',actual_origin() in ['http://127.0.0.1:5173','http://127.0.0.1:4173'])
{'regressions':regressions,'mission':mission,'kicad':kicad,'preview':preview}[phase]()
probe.check('no document horizontal overflow',read('document.documentElement.scrollWidth<=innerWidth+1'))
snapshot('finished-'+phase)
