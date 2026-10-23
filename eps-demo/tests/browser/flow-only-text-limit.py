"""Native whole-field text boundary regression. Use a fresh owned loopback origin.
Run with chrome_probe.py --actions flow-only-text-limit.py --no-screenshots.
No hooks, direct workspace writes or synthetic textarea value changes.
"""
import json
exec((ROOT/'flow-only.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
exec((ROOT/'canvas_helpers.py').read_text())

observations=[]

def units(value):
    return len(value.encode('utf-16-le'))//2

def query():
    return authored()['inputs']['mission'].get('conOps','')

def observe(label,expected=None):
    value=query()
    item={'label':label,'completeLength':units(value),'expectedLength':units(expected) if expected is not None else None}
    if has('textarea[aria-label^="Edit text part"]'):
        item.update(read("(()=>{const e=document.querySelector('textarea');return {partLength:e.value.length,maxLength:e.maxLength}})()"))
    observations.append(item)
    probe.save('text-limit-observations.json',observations)
    probe.check(label+' complete query stays within canonical limit',units(value)<=2000,item)
    if expected is not None:probe.check(label+' preserves the exact complete query',value==expected,item)
    return value

def end_of_part():
    probe.click('textarea')
    read("(()=>{const e=document.querySelector('textarea');e.setSelectionRange(e.value.length,e.value.length)})()")

def blur():
    probe.click('.sheet-heading')


def open_query_parts():
    click_task('mission')
    search=child('mission','mission-search')
    return child(search,'query-text')

def choose_part(parent,index):
    click_task(parent)
    selector=read("'#'+CSS.escape(document.querySelector('.record-picker select').id)")
    select_value(selector,str(index))
    return child(parent,'edit-passage')

def max_consistent(label):
    # Wait for the controlled editor to settle after a blur repartitions text.
    try:
        probe.wait_js('document.querySelector("textarea").value.length<=document.querySelector("textarea").maxLength',timeout=3)
    except TimeoutError:
        detail=read("(()=>{const e=document.querySelector('textarea');return {partLength:e.value.length,maxLength:e.maxLength,completeLength:JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1')).inputs.mission.conOps.length}})()")
        probe.check(label+' controlled draft synchronizes after blur',False,detail)
    actual=read("(()=>{const e=document.querySelector('textarea');return {part:e.value.length,max:e.maxLength}})()")
    expected=2000-units(query())+actual['part']
    probe.check(label+' maxlength accounts for every other part',actual['max']==expected,{'actual':actual,'expected':expected,'complete':units(query())})

probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
project_action('New design')
probe.click('[data-action=confirm-new-design]')
dismiss_notifications()
click_task('mission')
probe.fill('input[aria-label="Design name"]','Text boundary QA')
parts_node=open_query_parts()
child(parts_node,'edit-passage')
max_consistent('empty first part')
probe.check('empty query permits the full 2000-character input',read('document.querySelector("textarea").maxLength')==2000)

# CDP insertText follows Chrome's native editing/maxlength boundary, like paste.
attempt=('ConOps boundary '+('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ '*60))[:2001]
probe.click('textarea')
cdp('Input.insertText',text=attempt)
admitted=read('document.querySelector("textarea").value')
probe.save('native-paste.json',{'attemptedLength':len(attempt),'admittedLength':units(admitted),'nativeAcceptedPrefix':admitted==attempt[:len(admitted)]})
probe.check('native 2001-character paste admits exactly 2000 before blur',len(attempt)==2001 and units(admitted)==2000 and admitted==attempt[:2000])
observe('uncommitted paste','')
blur()
probe.wait_js('JSON.parse(localStorage.getItem("orbitwork.eps-demo.v1")).inputs.mission.conOps.length===2000')
full=observe('committed native paste',admitted)
max_consistent('resegmented first part')
fit('bounded first query part after paste')

# Inspect actual UI parts, then exercise a nonfirst part at a full-field boundary.
click_task(parts_node)
indices=read('[...document.querySelector(".record-picker select").options].map(o=>o.value)')
probe.check('2000-character query materializes multiple parts',len(indices)>1)
parts=[]
for index in indices:
    choose_part(parts_node,int(index))
    parts.append(read('document.querySelector("textarea").value'))
probe.check('all displayed parts reconstruct the complete stored query', ''.join(parts)==full)
choose_part(parts_node,1)
max_consistent('full nonfirst part')
original_part=read('document.querySelector("textarea").value')
end_of_part()
cdp('Input.insertText',text='Z')
probe.check('native append is blocked at the total limit',read('document.querySelector("textarea").value')==original_part)
blur()
observe('blocked nonfirst append',full)
fit('nonfirst part at total limit')

# Shortening frees one character globally. Later insertion keeps all other text.
end_of_part()
press_key('Backspace')
shortened=''.join([parts[0],parts[1][:-1],*parts[2:]])
blur()
probe.wait_js('JSON.parse(localStorage.getItem("orbitwork.eps-demo.v1")).inputs.mission.conOps.length===1999')
observe('shortened nonfirst part',shortened)
max_consistent('shortened field')
offset=len(parts[0])
expected=shortened[:offset]+'Ω'+shortened[offset:]
probe.click('textarea')
read("document.querySelector('textarea').setSelectionRange(0,0)")
cdp('Input.insertText',text='Ω')
blur()
probe.wait_js('JSON.parse(localStorage.getItem("orbitwork.eps-demo.v1")).inputs.mission.conOps.length===2000')
observe('legitimate later Unicode edit',expected)
max_consistent('refilled complete field')
fit('edited nonfirst part')

# Export/import uses the real canonical boundary. Reload must retain the new design.
archive=capture_download(lambda:project_action(r'^Export.*JSON'),'boundary-2000.json')
exported=json.loads(archive.read_text())
probe.check('JSON export retains all 2000 characters',exported['inputs']['mission']['conOps']==expected)
project_action('New design')
probe.click('[data-action=confirm-new-design]')
dismiss_notifications()
observe('replacement before canonical import','')
import_file(lambda:project_action(r'^Import.*JSON'),archive)
probe.wait_js('document.querySelector(".canvas-mission-name").innerText==="Text boundary QA"')
observe('canonical JSON import',expected)
probe.check('canonical import preserves new-design inputs',authored()['inputs']['mission']['altitudeKm'] is None and authored()['selections']=={})
probe.save('pre-reload-diagnostics.json',read('window.__orbitworkProbeDiagnostics'))
cdp('Page.reload',ignoreCache=True)
probe.wait_js('document.querySelectorAll("[data-activity]").length===10&&document.querySelector(".canvas-mission-name").innerText==="Text boundary QA"')
observe('reload without example fallback',expected)
probe.check('reload keeps the new design instead of loading the example',authored()['inputs']['mission']['altitudeKm'] is None and authored()['selections']=={} and not has('[role=alert]'))
parts_node=open_query_parts()
choose_part(parts_node,1)
max_consistent('restored nonfirst part')
fit('restored 2000-character query part')
probe.check('text boundary actions have clean diagnostics',read('window.__orbitworkProbeDiagnostics')=={'console':[],'errors':[]})
probe.save('pane-fit-summary.json',{'count':len(measurements),'maxOverflow':max(m['scroll']-m['height'] for m in measurements),'measurements':measurements})

# Also require a committed tail insertion to resynchronize the visible part.
# Repartitioning can leave its bounded prefix unchanged while moving the new
# character into the next node. The controlled draft must still match that part.
click_task(parts_node)
choose_part(parts_node,0)
first_length=read('document.querySelector("textarea").value.length')
choose_part(parts_node,1)
before_tail=query()
part_before_tail=read('document.querySelector("textarea").value')
end_of_part()
press_key('Backspace')
blur()
probe.wait_js('JSON.parse(localStorage.getItem("orbitwork.eps-demo.v1")).inputs.mission.conOps.length===1999')
short_tail=before_tail[:first_length]+part_before_tail[:-1]+before_tail[first_length+len(part_before_tail):]
observe('tail edit setup preserves all other text',short_tail)
max_consistent('tail edit setup')
tail_offset=first_length+read('document.querySelector("textarea").value.length')
expected_tail=short_tail[:tail_offset]+'Q'+short_tail[tail_offset:]
end_of_part()
cdp('Input.insertText',text='Q')
blur()
probe.wait_js('JSON.parse(localStorage.getItem("orbitwork.eps-demo.v1")).inputs.mission.conOps.length===2000')
observe('committed tail insertion preserves complete text',expected_tail)
probe.save('tail-insertion-draft.json',read("(()=>{const e=document.querySelector('textarea');return {draft:e.value,partLength:e.value.length,maxLength:e.maxLength,completeLength:JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1')).inputs.mission.conOps.length}})()"))
max_consistent('committed tail insertion')
