"""Owned-tab UI helpers for graphical-workflow.py.

Loaded into chrome_probe's action namespace. These helpers use ordinary controls,
CDP pointer/keyboard input, and file chooser events. They never call app hooks.
Download checks inspect bytes from the page's real Blob sink, not native saving.
"""
import base64
import json
import re
import time
from pathlib import Path


def read(expression):
    probe.guard()
    return js(expression)


def has(selector):
    return read("!!document.querySelector(" + json.dumps(selector) + ")")


def authored():
    return read("JSON.parse(localStorage.getItem('orbitwork.eps-demo.v1'))")


def control(pattern, scope="body", tags="button,summary", exact=False):
    """Discover a unique visible control and return its ordinary CSS path."""
    return read("""(() => {
      const root=document.querySelector(SCOPE);
      if(!root)throw Error('Missing control scope: '+SCOPE);
      const visible=e=>e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden';
      const name=e=>(e.getAttribute('aria-label')||e.innerText||e.title||'').replace(/\\s+/g,' ').trim();
      const regex=new RegExp(PATTERN,'i');
      const all=[...root.querySelectorAll(TAGS)].filter(visible);
      const matches=all.filter(e=>EXACT?name(e)===PATTERN:regex.test(name(e)));
      if(matches.length!==1)throw Error('Expected one control matching '+PATTERN+', got '+matches.length+
        '. Available: '+all.map(name).join(' | '));
      const parts=[];
      for(let e=matches[0];e&&e!==document.documentElement;e=e.parentElement){
        if(e.id){parts.unshift('#'+CSS.escape(e.id));break;}
        const tag=e.tagName.toLowerCase();
        const index=[...e.parentElement.children].filter(n=>n.tagName===e.tagName).indexOf(e)+1;
        parts.unshift(tag+':nth-of-type('+index+')');
      }
      return parts.join(' > ');
    })()""".replace("SCOPE", json.dumps(scope)).replace("PATTERN", json.dumps(pattern))
       .replace("TAGS", json.dumps(tags)).replace("EXACT", "true" if exact else "false"))


def click_control(pattern, scope="body", tags="button,summary", exact=False):
    selector = control(pattern, scope, tags, exact)
    probe.click(selector)
    return selector


def dismiss_notifications():
    for selector in ['[aria-label="Dismiss error"]', '[aria-label="Dismiss notification"]']:
        if has(selector):
            probe.click(selector)


def close_context():
    # The explicit close clears the complete inspector trail. Escape is scoped
    # to inspector focus on desktop and means Back inside a nested surface.
    if has('[role="dialog"]'):
        probe.click('[data-action="context-close"]')
        probe.wait_js("!document.querySelector('[role=dialog]')")
    dismiss_notifications()


def focus_activity(node):
    # Ordinary DOM focus invokes the graph's public focus/reveal behavior.
    # scrollIntoView alone cannot reveal a clipped React Flow node.
    selector = '.graph-activity[data-activity=' + json.dumps(node) + ']'
    time.sleep(0.1)  # Let the dock's ResizeObserver/Fit settle before focus reveal.
    read("document.querySelector('.activity-workspace').scrollIntoView({block:'center',behavior:'instant'});"
         'document.querySelector(' + json.dumps(selector) + ').focus({preventScroll:true})')
    probe.wait_js("""(() => {
      const e=document.querySelector(SELECTOR),r=e.getBoundingClientRect();
      const b=e.closest('.activity-workspace').getBoundingClientRect();
      return r.left>=b.left-1&&r.right<=b.right+1&&r.top>=b.top-1&&r.bottom<=b.bottom+1;
    })()""".replace('SELECTOR', json.dumps(selector)))
    return selector


def activity_point(node):
    selector = focus_activity(node)
    # probe.point's generic scrollIntoView scrolls the clipped flow wrapper,
    # which React Flow immediately resets. Measure the already revealed button
    # without that extra scroll, so the native pointer uses lasting coordinates.
    return read("""(() => {
      const e=document.querySelector(SELECTOR),r=e.getBoundingClientRect();
      const x=r.x+r.width/2,y=r.y+r.height/2,hit=document.elementFromPoint(x,y);
      if(e.disabled||x<0||y<0||x>=innerWidth||y>=innerHeight||!(hit===e||e.contains(hit)))
        throw Error('Activity clipped or occluded: '+SELECTOR);
      return {x,y};
    })()""".replace('SELECTOR', json.dumps(selector)))


def project_action(pattern):
    close_context()
    probe.click('.project-menu > summary')
    return click_control(pattern)


def field(label, scope=".sheet"):
    return read("""(() => {
      const root=document.querySelector(SCOPE);
      const labels=[...root.querySelectorAll('label')].filter(e=>e.innerText.replace(/\\s+/g,' ').trim()===LABEL);
      if(labels.length!==1||!labels[0].htmlFor)throw Error('Field label not unique: '+LABEL);
      return '#'+CSS.escape(labels[0].htmlFor);
    })()""".replace("SCOPE", json.dumps(scope)).replace("LABEL", json.dumps(label)))


def select_value(selector, wanted):
    probe.point(selector)
    # Chrome's macOS native select popup does not commit CDP key events in an
    # inactive shared tab. Use the real DOM control's standard input/change
    # boundary, as the original regression did. No app hooks or state writes.
    read("""(() => {
      const e=document.querySelector(SELECTOR);
      const option=[...e.options].find(o=>o.value===WANTED);
      if(!option||option.disabled)throw Error('Unavailable option: '+WANTED);
      e.focus();
      Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(e,WANTED);
      e.dispatchEvent(new Event('input',{bubbles:true}));
      e.dispatchEvent(new Event('change',{bubbles:true}));
      return e.value;
    })()""".replace("SELECTOR", json.dumps(selector)).replace("WANTED", json.dumps(wanted)))
    probe.wait_js("document.querySelector(" + json.dumps(selector) + ").value===" + json.dumps(wanted))


def recalculate():
    close_context()
    selector = control(r"^Recalculate", ".canvas-header")
    if not read("document.querySelector(" + json.dumps(selector) + ").disabled"):
        probe.click(selector)
    dismiss_notifications()


def capture_download(action, filename):
    read("""(() => {
      const p=HTMLAnchorElement.prototype;
      window.__canvasOriginalClick=p.click;window.__canvasDownload=null;
      p.click=function(...args){
        if(this.download&&this.href.startsWith('blob:')){
          window.__canvasDownload={name:this.download,promise:fetch(this.href).then(async r=>{
            const blob=await r.blob(),bytes=new Uint8Array(await blob.arrayBuffer());let text='';
            for(let i=0;i<bytes.length;i+=32768)text+=String.fromCharCode(...bytes.subarray(i,i+32768));
            return {mime:blob.type,bytes:bytes.length,base64:btoa(text)};
          })};return;
        }
        return window.__canvasOriginalClick.apply(this,args);
      };return true;
    })()""")
    try:
        action()
        probe.wait_js("!!window.__canvasDownload", timeout=10)
        result = read("(async()=>({name:window.__canvasDownload.name,...await window.__canvasDownload.promise}))()")
        path = probe.output / filename
        path.write_bytes(base64.b64decode(result.pop("base64")))
        probe.save(filename + "-sink.json", {**result, "nativeSaveTested": False})
        return path
    finally:
        read("HTMLAnchorElement.prototype.click=window.__canvasOriginalClick;delete window.__canvasOriginalClick;delete window.__canvasDownload")


def export_design(label):
    path = capture_download(lambda: project_action(r"^Export.*JSON"), label + ".json")
    dismiss_notifications()
    return json.loads(path.read_text()), path


def import_file(action, path):
    path = Path(path).resolve()
    if ROOT not in path.parents:
        raise ValueError("Import fixture must remain in the browser test directory")
    cdp("DOM.enable")
    cdp("Page.setInterceptFileChooserDialog", enabled=True)
    frame = cdp("Page.getFrameTree")["frameTree"]["frame"]["id"]
    try:
        action()
        chooser = None
        deadline = time.monotonic() + 4
        while chooser is None and time.monotonic() < deadline:
            events = drain_events()
            probe.browser_log.extend(e for e in events if e.get("method") in {
                "Log.entryAdded", "Runtime.exceptionThrown", "Network.loadingFailed"})
            chooser = next((e["params"] for e in events if e.get("method") == "Page.fileChooserOpened"
                            and e["params"].get("frameId") == frame), None)
            if chooser is None:
                time.sleep(0.05)
        if chooser is None:
            raise RuntimeError("No owned file chooser event")
        cdp("DOM.setFileInputFiles", backendNodeId=chooser["backendNodeId"], files=[str(path)])
    finally:
        cdp("Page.setInterceptFileChooserDialog", enabled=False)


def import_design(path):
    import_file(lambda: project_action(r"^Import.*JSON"), path)
    # File parsing is asynchronous. Keep the bounded pause independent of the
    # animation clock, which Chrome can suspend in a background owned tab.
    time.sleep(0.2)


def current_records(data):
    return [node for node, record in data["records"].items()
            if record["evaluatedRevision"] == record["revision"] and record["evaluatedAt"]]


def assert_no_overflow(label):
    geometry = read("({viewport:innerWidth,document:document.documentElement.scrollWidth})")
    probe.check(label + " has no document horizontal overflow", geometry["document"] <= geometry["viewport"] + 1, geometry)
