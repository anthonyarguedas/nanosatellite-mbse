"""Two bounded screenshots with DOM geometry preserved by chrome_probe."""
import json
probe.wait_js("document.querySelectorAll('[data-activity]').length===10")
probe.check('initial view contains only the ten engineering activities',js("document.querySelectorAll('[data-task]').length===10&&!document.querySelector('.context-host')"))
js("document.querySelector('[data-activity=battery]').focus({preventScroll:true})")
p=js("(()=>{const r=document.querySelector('[data-activity=battery]').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
click_at_xy(p['x'],p['y'])
probe.wait_js("document.querySelector('[data-pane-task]')?.dataset.paneTask==='battery'")
probe.snapshot('battery-sizing-and-detail-nodes')
