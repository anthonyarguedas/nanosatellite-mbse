"""Native narrow modal boundaries with closed/open method disclosures."""
exec((ROOT/'flow-only.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
exec((ROOT/'canvas_helpers.py').read_text())
results=[]
def targets():
    return read('''(()=>{const root=document.querySelector('[role=dialog]');const all=[...root.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),summary,[tabindex="0"]')];const visible=e=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS'&&!p.open&&![...p.children].find(c=>c.tagName==='SUMMARY')?.contains(e))return false;return e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden'};return all.filter(visible).map(e=>({name:e.getAttribute('aria-label')||e.innerText,tag:e.tagName}));})()''')
def boundary(label,reverse):
    read('''(()=>{const root=document.querySelector('[role=dialog]'),all=[...root.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),summary,[tabindex="0"]')].filter(e=>{for(let p=e.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS'&&!p.open&&![...p.children].find(c=>c.tagName==='SUMMARY')?.contains(e))return false;return e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden'});(REVERSE?all[0]:all.at(-1)).focus();})()'''.replace('REVERSE','true' if reverse else 'false'))
    press_key('Tab',modifiers=8 if reverse else 0)
    value=read('''(()=>{const e=document.activeElement,root=document.querySelector('[role=dialog]');let visible=!!e?.getClientRects().length;for(let p=e?.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS'&&!p.open&&![...p.children].find(c=>c.tagName==='SUMMARY')?.contains(e))visible=false;return {inside:root.contains(e),visible,name:e?.getAttribute('aria-label')||e?.innerText};})()''')
    results.append({'label':label,'reverse':reverse,**value});probe.save('modal-boundaries.json',results)
    probe.check(label+' Tab boundary remains on a visible modal control',value['inside'] and value['visible'],value)
def check_budget(label):
    click_task('budget');probe.check(label+' method starts closed',not read('document.querySelector("[data-help=method]").open'))
    boundary(label+' closed forward',False);boundary(label+' closed reverse',True)
    read('document.querySelector("[data-help=method] > summary").focus()');press_key('Enter');probe.wait_js('document.querySelector("[data-help=method]").open')
    probe.check(label+' own closed summary was keyboard focusable',True)
    probe.click('[data-help=method] .task-actions button:last-child')
    probe.wait_js("document.querySelector('[data-pane-task]').dataset.paneTask==='scenarios'")
    probe.check(label+' last upstream action opens its activity',True)
    click_task('budget');open_help('method');boundary(label+' open forward',False);boundary(label+' open reverse',True)
    probe.click('[data-help=method] > summary');boundary(label+' reclosed forward',False)
probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
check_budget('example budget')
project_action('New design');probe.click('[data-action=confirm-new-design]');dismiss_notifications()
check_budget('missing-input budget')
press_key('Escape');probe.wait_js('!document.querySelector("[role=dialog]")')
probe.check('modal Escape still dismisses',True)
