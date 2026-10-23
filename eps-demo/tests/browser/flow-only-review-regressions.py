"""Independent-review regressions. Run only on a fresh owned isolated origin."""
import copy
import json
import time
exec((ROOT/'flow-only.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
exec((ROOT/'canvas_helpers.py').read_text())

def project_open_action(selector):
    if not read("document.querySelector('.project-menu').open"):probe.click('.project-menu > summary')
    probe.click(selector)

def run_open():
    project_open_action('[data-action=recalculate]')
    time.sleep(.15)
    dismiss_notifications()

def export_open(name):
    path=capture_download(lambda:project_open_action('[data-action=export]'),name+'.json')
    return json.loads(path.read_text()),path

def choose_record(term,value=False):
    target=read("""(()=>{const s=document.querySelector('.sheet .record-picker select');if(!s)throw Error('Missing record picker');const o=[...s.options].find(o=>EXACT?o.value===TERM:o.textContent.includes(TERM));if(!o)throw Error('Missing record '+TERM);return {selector:'#'+CSS.escape(s.id),value:o.value};})()""".replace('EXACT','true' if value else 'false').replace('TERM',json.dumps(term)))
    select_value(target['selector'],target['value'])

def title_child(parent,title):
    key=read("""(()=>{const prefix=PARENT+'/';return [...document.querySelectorAll('[data-task]')].find(e=>e.dataset.task.startsWith(prefix)&&!e.dataset.task.slice(prefix.length).includes('/')&&e.querySelector('strong')?.textContent===TITLE)?.dataset.task;})()""".replace('PARENT',json.dumps(parent)).replace('TITLE',json.dumps(title)))
    if not key:raise AssertionError('Missing child '+title)
    return click_task(key)

def solar_screen():
    click_task('assessment');group=title_child('assessment','Model screens');choose_record('SOLAR-POWER');return child(group,'check')

def role_node(roles,role):
    key=read('[...document.querySelectorAll("[data-task-kind=role]")].find(e=>e.dataset.task.startsWith('+json.dumps(roles+'/')+')&&e.dataset.task.endsWith('+json.dumps(':'+role)+'))?.dataset.task')
    return click_task(key)

probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
original_power=authored()['inputs']['solar']['installedPowerW']
# Keep the saved passing check open while the existing controller recalculates.
click_task('solar');child('solar','installed');probe.fill(field('Available source EOL power'),'0')
check=solar_screen()
probe.check('saved passing solar screen is visibly historical',read("document.querySelector('.verdict').textContent==='pass'&&document.querySelector('.task-freshness').innerText.includes('historical')"))
run_open()
probe.wait_js("document.querySelector('.verdict')?.textContent==='fail'")
probe.check('selected check refreshes to current fail without reselecting',read('document.querySelector("[data-pane-task]").dataset.paneTask==='+json.dumps(check)+"&&!document.querySelector('.task-freshness.historical')"))
fail_export,_=export_open('solar-fail')
failed=next(c for c in fail_export['analysis']['checks'] if c['id']=='SOLAR-POWER')
probe.check('current check pane displays the recomputed detail',failed['detail'] in read("document.querySelector('.task-body').innerText"))
# Recompute while a text descendant is selected, not just the verdict pane.
click_task('solar');child('solar','installed');probe.fill(field('Available source EOL power'),str(original_power))
check=solar_screen();open_help('criterion')
old_text=help_field('Criterion detail')
run_open();restored,_=export_open('solar-restored')
passed=next(c for c in restored['analysis']['checks'] if c['id']=='SOLAR-POWER')
probe.wait_js('document.querySelector("[data-help-field=\\\"Criterion detail\\\"] .record-text")?.textContent==='+json.dumps(passed['detail']))
probe.check('open criterion refreshes with its live parent',passed['verdict']=='pass' and passed['detail']!=old_text)
probe.check('live scope and equation preserved',help_field('Scope & equation')==(passed.get('equation') or 'No numerical equation.')+'\n'+(passed.get('scope') or 'Scope not recorded.'))
probe.check('live evidence references preserved',help_field('Evidence references')==(', '.join(passed.get('sourceIds',[])) or 'No source references recorded.'))
# The real long P60 property has distinct value/original nodes and complete parts.
click_task('candidates');cat=child('candidates','catalog');choose_record('gomspace-p60-one-acu-one-pdu-16v',True)
p60=child(cat,'product');specs=child(p60,'specs');choose_record('historicalEfficiencyCurvePoints',True);spec=child(specs,'spec')
open_help('property')
complete=help_field('Property value')
value='Property value';parts=['in-pane complete property']
probe.check('complete P60 formatted value is reachable',len(complete)==626 and complete.endswith('structured'))
probe.save('p60-property-value.json',{'characters':len(complete),'value':complete,'parts':parts})
original=help_field('Original representation')
probe.check('property facets have distinct stable section identities',read('document.querySelectorAll("[data-help-field=\\\"Property value\\\"]").length===1&&document.querySelectorAll("[data-help-field=\\\"Original representation\\\"]").length===1'))
# A selected override belongs only to the current product branch.
click_task('candidates');roles=child('candidates','roles');conditioning=role_node(roles,'conditioning');choose_record('gomspace-p60-one-acu-one-pdu-16v',True)
p60=child(conditioning,'product');allocation=child(p60,'allocation');select_option('Selection role','distribution')
click_task(p60);screen=child(p60,'screen');screen_export,_=export_open('distribution-screen')
expected=next(s for s in screen_export['analysis']['suggestions'] if s['productId']=='gomspace-p60-one-acu-one-pdu-16v' and s['role']=='distribution')
probe.check('screen is explicitly labeled for distribution',read("document.querySelector('.task-body').innerText.includes('Power Circuits & Switches evidence')"))
open_help('screen')
probe.check('role-specific reason remains consistent',help_field('Screen reason')==expected['reason'])
click_task(screen);checks=child(screen,'check-group');product_count=read("document.querySelector('.record-picker select').options.length")
probe.check('role-specific check collection matches current distribution',product_count==len(expected['checks']))
if expected['checks']:
    current=child(checks,'check');probe.check('role-specific check criterion is current',expected['checks'][0]['detail'] in read("document.querySelector('.task-body').innerText"))
click_task(screen);gaps=child(screen,'gaps');probe.check('gaps retain the selected role label',read("document.querySelector('.task-body').innerText.includes('Power Circuits & Switches evidence')"))
click_task('candidates');roles=child('candidates','roles');conditioning=role_node(roles,'conditioning');choose_record('gomspace-p60-one-acu-one-pdu-16v',True)
# Same branch intentionally retains its explicit override. A distribution branch has its own selection.
distribution=role_node(roles,'distribution');choose_record('gomspace-p60-one-acu-one-pdu-16v',True);other=child(distribution,'product');other_alloc=child(other,'allocation')
probe.check('fresh role branch starts with its own role',read("document.querySelector('.sheet select').value==='distribution'"))
# Assessment filtering never reaches product or simulation check collections.
click_task('simulation');simulation_group=child('simulation','check-group');simulation_count=read("document.querySelector('.record-picker select').options.length")
click_task('assessment');select_option('Filter check outcomes','pass')
click_task('simulation');simulation_group=child('simulation','check-group')
probe.check('assessment Pass filter leaves all simulation checks visible',read("document.querySelector('.record-picker select').options.length")==simulation_count)
click_task('candidates');roles=child('candidates','roles');conditioning=role_node(roles,'conditioning');choose_record('gomspace-p60-one-acu-one-pdu-16v',True);p60=child(conditioning,'product');screen=child(p60,'screen');checks=child(screen,'check-group')
probe.check('assessment Pass filter leaves all distribution product checks visible',read("document.querySelector('.record-picker select').options.length")==product_count)
# Mission results/consent survive child navigation, but never workspace replacement.
click_task('mission');search=child('mission','mission-search');select_option('Choose a query example','0')
click_task(search);select_option('Retrieval method','lexical-tfidf');probe.click('[data-action=search-missions]')
probe.wait_js("document.querySelector('.task-body').innerText.includes('matches')")
analogues=child(search,'analogues');analogue=child(analogues,'analogue');accept=child(analogue,'accept-altitude');probe.click('.checkbox-label input')
click_task(analogue);open_help('analogue');click_task(accept)
probe.check('navigation retains current query consent',read("document.querySelector('.checkbox-label input').checked&&!document.querySelector('[data-action=accept-altitude]').disabled"))
saved,path=export_open('same-query-before-replacement');before=copy.deepcopy(authored())
invalid=probe.output/'invalid-design.json';invalid.write_text('{ invalid')
import_file(lambda:project_open_action('[data-action=import]'),invalid)
probe.wait_js("!!document.querySelector('[role=alert]')")
probe.check('failed import keeps workspace and acceptance context',authored()==before and read("document.querySelector('.checkbox-label input').checked"))
dismiss_notifications()
# Valid import has exactly the same query string, so query-only invalidation cannot satisfy this regression.
import_file(lambda:project_open_action('[data-action=import]'),path)
probe.wait_js("!document.querySelector('.context-host')&&document.querySelectorAll('[data-task]').length===10")
probe.check('successful same-query import preserves authored inputs',authored()['inputs']['mission']['conOps']==before['inputs']['mission']['conOps'])
click_task('mission');search=child('mission','mission-search');analogues=child(search,'analogues')
probe.check('same-query replacement clears old results and consent',read("document.querySelector('.record-picker select').options.length===1&&document.querySelector('.record-picker select').options[0].value===''&&!document.querySelector('[data-task-kind=accept-altitude]')"))
# New/example replacement also cannot recover previous transient results.
project_open_action('[data-action=new-design]');probe.click('[data-action=confirm-new-design]');dismiss_notifications()
click_task('mission');search=child('mission','mission-search');analogues=child(search,'analogues')
probe.check('New design keeps no previous mission results',read("document.querySelector('.record-picker select').options[0].value===''") and authored()['inputs']['mission'].get('conOps','')=='')
project_open_action('[data-action=load-example]');probe.click('[data-action=confirm-load-example]');dismiss_notifications()
click_task('mission');search=child('mission','mission-search');analogues=child(search,'analogues')
probe.check('Example replacement keeps no previous mission results',read("document.querySelector('.record-picker select').options[0].value===''") )
# Approved rule state survives child navigation but is cleared even by an equal-input import.
click_task('candidates');ki=child('candidates','kicad');rules=child(ki,'rules')
template_path=capture_download(lambda:click_control('Input template','.sheet',exact=True),'review-rule-template.json')
profile=json.loads(template_path.read_text())
profile['physicalNetlistRevision']='synthetic-review-regression'
profile['approval']={'status':'approved','engineer':'SYNTHETIC TEST ONLY, no engineering authority','date':'2026-10-23'}
profile['sources']=[{'id':'reviewed-source','url':'https://example.org/synthetic-test','revision':'test-1','location':'Synthetic browser fixture, not design evidence'}]
profile['knownNets']=['EPS_BUS']
profile['fabrication'].update(minimumTrackWidthMm=.1,minimumClearanceMm=.1,minimumViaDiameterMm=.4,minimumDrillMm=.2,minimumAnnularWidthMm=.1,minimumEdgeClearanceMm=.1)
def dimension(value,ids):
    return {'minimumMm':value,'requirementIds':ids,'sourceIds':['reviewed-source'],'rationale':'Synthetic regression only','derivation':{'method':'Synthetic test','conditions':'Synthetic test','margin':'Synthetic test'}}
profile['classes']=[{'name':'EPS_POWER','nets':['EPS_BUS'],'trackWidth':dimension(.8,['EPS-07']),'clearance':dimension(.5,['EPS-03']),'viaDiameter':dimension(.8,['EPS-07']),'viaDrill':{**dimension(.4,['EPS-07']),'maximumMm':.4}}]
profile['edgeClearance']=dimension(.5,['EPS-20'])
profile_path=probe.output/'synthetic-review-rules.json';profile_path.write_text(json.dumps(profile))
import_file(lambda:probe.click('.file-action'),profile_path)
probe.wait_js("!!document.querySelector('[data-action=rule-sidecars-download]')")
child(rules,'rule-warnings');click_task(rules)
probe.check('rule import survives corresponding child navigation',read("!!document.querySelector('[data-action=rule-sidecars-download]')"))
_,replacement=export_open('same-input-rules-replacement')
import_file(lambda:project_open_action('[data-action=import]'),replacement)
probe.wait_js("!document.querySelector('.context-host')")
click_task('candidates');ki=child('candidates','kicad');child(ki,'rules')
probe.check('workspace replacement clears imported physical rule session',read("!document.querySelector('[data-action=rule-sidecars-download]')"))
probe.save('pane-fit-summary.json',{'count':len(measurements),'maxOverflow':max(m['scroll']-m['height'] for m in measurements),'measurements':measurements})
