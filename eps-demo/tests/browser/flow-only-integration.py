"""Mutation/download regressions for the focused task graph. Synthetic rule approval is test data only."""
import copy
import zipfile
exec((ROOT/'flow-only.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
exec((ROOT/'canvas_helpers.py').read_text())

def load_example():
    project_action('Load BIRDS-4-inspired example')
    probe.click('[data-action=confirm-load-example]')
    probe.wait_js("!document.querySelector('.context-host')")
    dismiss_notifications()

def run_available():
    project_action('Recalculate available activities')
    dismiss_notifications()

def save_design(name):
    path=capture_download(lambda:project_action(r'^Export.*JSON'),name+'.json')
    return json.loads(path.read_text()),path

load_example()
before=copy.deepcopy(authored())
# A full numeric field inventory survives navigation without losing edits.
for root,kind,label,value,path in [
 ('solar',None,'Sunlight efficiency, Xs','0.81',('solar','sunlightEfficiency')),
 ('solar','cell','Cell EOL MPP voltage','2.3',('solar','cellEolV')),
 ('solar','installed','Available source EOL power','6.1',('solar','installedPowerW')),
 ('battery',None,'Design DoD limit','0.35',('battery','dod')),
 ('battery','pack','BOL pack energy','85',('battery','capacityWh')),
 ('battery','charge','Maximum charge power','12',('battery','maxChargeW')),
 ('battery','discharge','Discharge energy efficiency','0.91',('battery','dischargeEfficiency')),
 ('topology','resources','EPS mass allocation','0.52',('topology','massAllocationKg')),
 ('budget',None,'Additional EPS baseline','0.12',('topology','idlePowerW'))]:
    click_task(root)
    if kind:child(root,kind)
    probe.fill(field(label),value)
    probe.check(label+' updates the existing authored field',authored()['inputs'][path[0]][path[1]]==float(value))
    click_task('mission');click_task(root)
    if kind:child(root,kind)
    probe.check(label+' survives graph navigation',float(read('document.querySelector('+json.dumps(field(label))+').value'))==float(value))
probe.check('numeric edits never resize frozen receipts',authored()['allocations']==before['allocations'])
# Add, edit and remove a separate case, load and windows through actual task controls.
click_task('scenarios');probe.click('[data-action=new-scenario]')
case_id=authored()['inputs']['activeScenarioId']
probe.fill('input[aria-label="Case name"]','Independent browser case')
loads=child('scenarios','loads');probe.click('[data-action=add-load]')
load=child(loads,'load');child(load,'load-power');probe.fill('input[aria-label="Active power"]','2.7')
click_task(load);windows=child(load,'windows');probe.click('[data-action=add-window]');window=child(windows,'window')
probe.fill('input[aria-label="Window start (%)"]','50')
probe.click('[aria-label="Move selected window"]');press_key('ArrowRight')
p=probe.point('[aria-label="Move selected window"]');probe.drag('[aria-label="Move selected window"]',8)
fit('window after native drag and numeric editing')
case=next(s for s in authored()['inputs']['scenarios'] if s['id']==case_id)
probe.check('separate case load and window edits persist',len(case['loads'])==1 and case['loads'][0]['activePowerW']==2.7 and len(case['loads'][0]['windows'])==2)
probe.check('other scenario schedules remain unchanged',[s for s in authored()['inputs']['scenarios'] if s['id']!=case_id]==before['inputs']['scenarios'])
probe.click('[data-action=remove-window]');probe.wait_js("document.querySelector('[data-pane-kind]')?.dataset.paneKind==='windows'")
click_task(load);probe.click('[data-action=remove-load]');probe.wait_js("document.querySelector('[data-pane-kind]')?.dataset.paneKind==='loads'")
click_task('scenarios');provenance=child('scenarios','case-provenance');child(provenance,'edit-passage')
line_heavy=('Synthetic authored line\n'*60)+'Unicode 🛰️ retained exactly.'
probe.fill('textarea',line_heavy,commit=None)
probe.click('.sheet-heading')
probe.wait_js('document.querySelector("textarea").value.length<'+str(len(line_heavy)))
fit('line-heavy authored continuation')
probe.check('continuation editing recombines the complete authored text',next(s for s in authored()['inputs']['scenarios'] if s['id']==case_id)['provenance']==line_heavy)
click_task(provenance)
probe.check('line-heavy authored text has multiple reachable graph records',read('document.querySelector(".sheet select").options.length')>1)
click_task('scenarios');probe.click('[data-action=remove-scenario]')
probe.check('case/load/window removal remains available',all(s['id']!=case_id for s in authored()['inputs']['scenarios']))
# Frozen exact-role product application is performed only from its allocation task.
load_example();click_task('candidates');cat=child('candidates','catalog')
battery_id=authored()['selections']['battery']
select_option('CSRM role','battery')
label=read("[...document.querySelectorAll('.sheet label')].find(e=>e.innerText.startsWith('Product ·')).innerText")
select_option(label,battery_id)
product=child(cat,'product');allocation=child(product,'allocation');probe.click('[data-action=allocate-product]')
probe.check('explicit product action freezes the exact battery receipt',next(r for r in authored()['allocations'] if r['productId']==battery_id)['quantity']>=1)
run_available()
# Real UI-generated KiCad ZIP and rule templates.
click_task('candidates');ki=child('candidates','kicad')
archive=capture_download(lambda:probe.click('[data-action=kicad-review-download]'),'logical-review.zip')
with zipfile.ZipFile(archive) as z:
    probe.check('focused handoff emits a valid native KiCad ZIP',z.testzip() is None and any(n.endswith('.kicad_sch') for n in z.namelist()) and not any(n.endswith('.kicad_pcb') for n in z.namelist()))
rules=child(ki,'rules')
template_path=capture_download(lambda:click_control('Input template','.sheet',exact=True),'rule-template.json')
template=json.loads(template_path.read_text())
import_file(lambda:probe.click('.file-action'),template_path)
probe.wait_js("document.querySelector('.sheet').innerText.includes('approval')")
probe.check('unapproved rule profile remains gated',not has('[data-action=rule-sidecars-download]'))
# This fixture exercises import mechanics. It is explicitly synthetic, not reviewed engineering evidence.
profile=copy.deepcopy(template)
profile['physicalNetlistRevision']='synthetic-test-netlist-1'
profile['approval']={'status':'approved','engineer':'SYNTHETIC TEST ONLY, no engineering authority','date':'2026-10-23'}
profile['sources']=[{'id':'reviewed-source','url':'https://example.org/synthetic-test','revision':'test-1','location':'Synthetic browser fixture, not design evidence'}]
profile['knownNets']=['EPS_BUS']
profile['fabrication'].update(minimumTrackWidthMm=.1,minimumClearanceMm=.1,minimumViaDiameterMm=.4,minimumDrillMm=.2,minimumAnnularWidthMm=.1,minimumEdgeClearanceMm=.1)
def dimension(minimum,ids):
    return {'minimumMm':minimum,'requirementIds':ids,'sourceIds':['reviewed-source'],'rationale':'Synthetic browser fixture only','derivation':{'method':'Synthetic test','conditions':'Synthetic test','margin':'Synthetic test'}}
profile['classes']=[{'name':'EPS_POWER','nets':['EPS_BUS'],'trackWidth':dimension(.8,['EPS-07']),'clearance':dimension(.5,['EPS-03']),'viaDiameter':dimension(.8,['EPS-07']),'viaDrill':{**dimension(.4,['EPS-07']),'maximumMm':.4}}]
profile['edgeClearance']=dimension(.5,['EPS-20'])
profile_path=probe.output/'synthetic-approved-rules.json';profile_path.write_text(json.dumps(profile))
import_file(lambda:probe.click('.file-action'),profile_path)
probe.wait_js("!!document.querySelector('[data-action=rule-sidecars-download]')")
fit('approved rule result')
child(rules,'rule-warnings');click_task(rules)
probe.check('imported rule session survives child navigation',not read("document.querySelector('[data-action=rule-sidecars-download]').disabled"))
sidecars=capture_download(lambda:probe.click('[data-action=rule-sidecars-download]'),'synthetic-rule-sidecars.zip')
with zipfile.ZipFile(sidecars) as z:probe.check('approved fixture emits rule sidecars',z.testzip() is None and any(n.endswith('.kicad_dru') for n in z.namelist()))
# JSON export/import and replacement confirmations preserve the authored model.
original,path=save_design('focused-design')
project_action('New design');probe.click('[data-action=confirm-new-design]');dismiss_notifications()
probe.check('new-design confirmation clears only the chosen workspace',authored()['selections']=={} and authored()['inputs']['mission']['altitudeKm'] is None)
import_file(lambda:project_action(r'^Import.*JSON'),path)
probe.wait_js("document.querySelector('.canvas-mission-name').innerText.includes('BIRDS-4')")
probe.check('JSON restores exact frozen receipts and source provenance',authored()['allocations']==original['allocations'] and authored()['provenance']==original['provenance'] and authored()['inputs']==original['inputs'])
run_available()
recomputed,_=save_design('recomputed-design')
probe.check('recomputed analysis survives the focused JSON round trip',recomputed['analysis']==original['analysis'])
probe.save('pane-fit-summary.json',{'count':len(measurements),'maxOverflow':max(m['scroll']-m['height'] for m in measurements),'measurements':measurements})
