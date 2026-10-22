"""Real-pointer repro for the 1280px CAM window move target. No app-state injection."""
probe.click('.topbar .load-example')
probe.click('#tab-scenarios')
selector='[aria-label="Move CAM imaging window 1"]'
geometry=js("""(() => {const e=document.querySelector('[aria-label="Move CAM imaging window 1"]');
 e.scrollIntoView({block:'center',behavior:'instant'});const r=e.getBoundingClientRect();
 const x=r.x+r.width/2,y=r.y+r.height/2;const hit=document.elementFromPoint(x,y);
 return {x,y,width:r.width,track:e.closest('[data-scenario-track]').getBoundingClientRect().width,
 hit:hit?.getAttribute('aria-label'),before:{start:Number(e.getAttribute('aria-valuenow')),
 end:Number(document.querySelector('[aria-label="End of CAM imaging window 1"]').getAttribute('aria-valuenow'))}};})()""")
probe.save('middle-hit-target.json',geometry)
probe.snapshot('before-middle-drag')
cdp('Input.dispatchMouseEvent',type='mousePressed',x=geometry['x'],y=geometry['y'],button='left',buttons=1,clickCount=1)
for i in range(1,13):
 cdp('Input.dispatchMouseEvent',type='mouseMoved',x=geometry['x']+geometry['track']*.05*i/12,y=geometry['y'],button='left',buttons=1)
cdp('Input.dispatchMouseEvent',type='mouseReleased',x=geometry['x']+geometry['track']*.05,y=geometry['y'],button='left',buttons=0,clickCount=1)
after=js("({start:Number(document.querySelector('[aria-label=\"Move CAM imaging window 1\"]').getAttribute('aria-valuenow')),end:Number(document.querySelector('[aria-label=\"End of CAM imaging window 1\"]').getAttribute('aria-valuenow'))})")
probe.save('middle-drag-result.json',{'before':geometry['before'],'after':after,'expected':{'start':21,'end':24}})
probe.snapshot('after-middle-drag')
probe.check('middle drag moves whole window',after=={'start':21,'end':24},after)
