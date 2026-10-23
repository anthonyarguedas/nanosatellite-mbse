"""Rendered label footprints, route invariance, and deep-path emphasis."""
exec((ROOT/'flow-refine-geometry.py').read_text().split('\nprobe.wait_js("document.querySelectorAll')[0])
labels=[]
def label_geometry(label):
    measure(label)
    result=read('''(()=>{const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}},overlap=(a,b)=>a.x<b.x+b.width-.1&&b.x<a.x+a.width-.1&&a.y<b.y+b.height-.1&&b.y<a.y+a.height-.1;const nodes=[...document.querySelectorAll('[data-task]')].map(e=>({id:e.dataset.task,r:rect(e)})),labels=[...document.querySelectorAll('.flow-edge-label')].map(e=>({text:e.textContent,r:rect(e.querySelector('rect'))})),bounds=rect(document.querySelector('.activity-workspace')),nodeHits=[],labelHits=[],clipped=[];for(let i=0;i<labels.length;i++){for(const n of nodes)if(overlap(labels[i].r,n.r))nodeHits.push([labels[i].text,n.id]);for(let j=i+1;j<labels.length;j++)if(overlap(labels[i].r,labels[j].r))labelHits.push([labels[i].text,labels[j].text]);const r=labels[i].r;if(r.x<bounds.x||r.y<bounds.y||r.x+r.width>bounds.x+bounds.width||r.y+r.height>bounds.y+bounds.height)clipped.push(labels[i].text);}return {labels,nodeHits,labelHits,clipped};})()''')
    labels.append({'visit':label,**result});probe.save('label-geometry.json',labels)
    probe.check(label+' labels clear every mounted node',not result['nodeHits'],result)
    probe.check(label+' labels clear other labels and graph header',not result['labelHits'] and not result['clipped'],result)
probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
probe.click('.relationship-toggle')
for width,height in [(1440,900),(850,900)]:
    cdp('Emulation.setDeviceMetricsOverride',width=width,height=height,deviceScaleFactor=1,mobile=False);time.sleep(.15)
    for root in ['mission','orbit','scenarios','budget','solar','battery','topology','candidates','simulation','assessment']:
        click_task(root);label_geometry(str(width)+' '+root)
cdp('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=1,mobile=False);time.sleep(.15)
click_task('simulation');label_geometry('simulation screenshot')
if probe.screenshots:probe.snapshot('simulation-labels')
click_task('battery');label_geometry('battery screenshot')
click_task('scenarios');loads=child('scenarios','loads');load=child(loads,'load');windows=child(load,'windows');child(windows,'window');label_geometry('deep window')
probe.check('deep focus has no floating owner exchange labels',read('document.querySelectorAll(".flow-edge-label").length===0'))
probe.check('deep focus does not brighten owner-level dependencies',read('![...document.querySelectorAll(".information-edge.dependency .react-flow__edge-path")].some(p=>getComputedStyle(p).stroke==="rgb(239, 177, 131)")'))
before=measure('deep before toggle');probe.click('.relationship-toggle');after=measure('deep after toggle');probe.check('visibility toggle preserves all retained route paths',all(after['paths'][key]==value for key,value in before['paths'].items() if key in after['paths']))
if probe.screenshots:probe.snapshot('deep-path-emphasis')
probe.screenshots=False
probe.save('label-summary.json',{'visits':len(labels),'renderedLabels':sum(len(v['labels']) for v in labels),'nodeHits':sum(len(v['nodeHits']) for v in labels),'labelHits':sum(len(v['labelHits']) for v in labels),'clippedLabels':sum(len(v['clipped']) for v in labels)})
probe.check('useful root labels remain visible',sum(len(v['labels']) for v in labels)>0)
