#!/usr/bin/env python3
"""Owned-tab Orbitwork discovery driver. No browser access until given --url.

Uses the existing shared-browser runner and its invocation-local harness.
Default: navigate once, capture the UI, close only the new owned tab.
After exploration, --actions may name an owned Python file using `probe` and
pre-imported browser-harness helpers. No app packages are installed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SCRIPTS = Path.home() / "agent-tools/internet/skills/browser/scripts"
CONTRACT = "shared-browser-owned-tabs-v1"


def owned_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if path != ROOT and ROOT not in path.parents:
        raise ValueError(f"Path must stay inside {ROOT}: {path}")
    return path


def local_url(value: str) -> str:
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.port not in {5173, 4173}
            or parsed.username is not None or parsed.password is not None):
        raise argparse.ArgumentTypeError("Use the parent-supplied local http:// ready URL.")
    try:
        parsed.port
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return value


DOM_PROJECTION = r"""(() => {
  const visible = e => e.getClientRects().length > 0 &&
    getComputedStyle(e).visibility !== 'hidden' && getComputedStyle(e).display !== 'none';
  const rect = e => { const r = e.getBoundingClientRect();
    return {x:r.x,y:r.y,width:r.width,height:r.height}; };
  const name = e => e.getAttribute('aria-label') ||
    [...(e.labels || [])].map(l => l.innerText).join(' ') || e.innerText || e.title || '';
  return {
    url:location.href, title:document.title,
    viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},
    document:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},
    text:document.body.innerText,
    controls:[...document.querySelectorAll('button,input,select,textarea,summary,[role="button"],[role="slider"],[role="tab"],a[href]')]
      .filter(visible).map(e => ({tag:e.tagName,role:e.getAttribute('role'),name:name(e).trim(),
        type:e.type || null,value:e.value ?? null,disabled:!!e.disabled,
        expanded:e.getAttribute('aria-expanded'),selected:e.getAttribute('aria-selected'),
        valueNow:e.getAttribute('aria-valuenow'),valueText:e.getAttribute('aria-valuetext'),
        href:e.getAttribute('href'),classes:e.className?.baseVal ?? e.className,rect:rect(e)})),
    panels:[...document.querySelectorAll('main,aside,[role="dialog"],.graph-panel,.workflow-node,.scenario-editor,.architecture-pane,.plot-card')]
      .filter(visible).map(e => ({tag:e.tagName,label:e.getAttribute('aria-label'),
        classes:e.className?.baseVal ?? e.className,text:e.innerText,rect:rect(e)}))
  };
})()"""

DIAGNOSTICS = r"""(() => {
  const log = window.__orbitworkProbeDiagnostics = {console:[],errors:[]};
  const append = (list, value) => { if (list.length < 100) list.push(value); };
  for (const level of ['error','warn']) {
    const original = console[level];
    console[level] = function(...args) {
      append(log.console,{level,text:args.map(a => {try {return typeof a === 'string' ? a : JSON.stringify(a);} catch {return String(a);}}).join(' ')});
      return original.apply(this,args);
    };
  }
  window.addEventListener('error',e => append(log.errors,{message:e.message || 'Resource error',
    source:e.filename || e.target?.src || e.target?.href || '',line:e.lineno || null}),true);
  window.addEventListener('unhandledrejection',e => append(log.errors,{message:String(e.reason)}));
})()"""


class Probe:
    """Small live helpers. Browser functions are supplied by browser_harness -c."""
    def __init__(self, output: Path, tab: str):
        self.output, self.tab = output, tab
        self.journal: list[dict] = []
        self.sequence = 0
        self.browser_log = []

    def guard(self):
        if current_tab()["targetId"] != self.tab:
            raise RuntimeError("Attached target changed. Refusing to touch a non-owned tab.")

    def save(self, name: str, value):
        path = owned_path(self.output / name)
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def snapshot(self, label: str):
        self.guard()
        self.sequence += 1
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", label).strip("-") or "snapshot"
        stem = f"{self.sequence:02d}-{safe}"
        # Wait only for finite UI transitions, never React Flow's infinite edge animation.
        js("""(async()=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
          await Promise.all(document.getAnimations().filter(a=>a.effect?.getComputedTiming().iterations!==Infinity)
            .map(a=>Promise.race([a.finished.catch(()=>{}),new Promise(r=>setTimeout(r,350))])));return true;})()""")
        # Viewport PNG is authoritative for clipping/overlap review.
        capture_screenshot(path=str(self.output / f"{stem}.png"))
        self.save(f"{stem}.json", js(DOM_PROJECTION))
        self.save("diagnostics.json", js("window.__orbitworkProbeDiagnostics || null"))
        self.browser_log.extend(e for e in drain_events() if e.get('method') in {
            'Log.entryAdded', 'Runtime.exceptionThrown', 'Network.loadingFailed'} or (
            e.get('method') in {'Network.requestWillBeSent', 'Network.responseReceived'} and
            (e.get('params', {}).get('request', {}).get('url', '').startswith('http://127.0.0.1:8767/') or
             e.get('params', {}).get('response', {}).get('url', '').startswith('http://127.0.0.1:8767/'))))
        self.save('browser-log.json', self.browser_log)
        print(f"CAPTURE {self.output / stem}", flush=True)

    def check(self, name: str, condition: bool, detail=None):
        item = {"name": name, "pass": bool(condition), "detail": detail}
        self.journal.append(item)
        self.save("checks.json", self.journal)
        if not condition:
            self.snapshot("assertion-failure")
            raise AssertionError(f"{name}: {detail}")

    def wait_js(self, expression: str, timeout: float = 5):
        """Bounded UI state wait, never a server-start/retry loop."""
        self.guard()
        deadline = time.monotonic() + timeout
        while True:
            value = js(expression)
            if value:
                return value
            if time.monotonic() >= deadline:
                raise TimeoutError(f"UI state did not arrive: {expression}")
            time.sleep(0.1)

    def point(self, selector: str):
        self.guard()
        return js("""(() => {
          const matches = document.querySelectorAll(SELECTOR);
          if (matches.length !== 1) throw Error('Expected one control, got '+matches.length+': '+SELECTOR);
          const e = matches[0];
          e.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'});
          const r = e.getBoundingClientRect(), s = getComputedStyle(e);
          const x = r.x+r.width/2, y = r.y+r.height/2;
          const hit = document.elementFromPoint(x,y);
          if (e.disabled || e.getAttribute('aria-disabled') === 'true' || !r.width || !r.height ||
              s.visibility === 'hidden' || s.display === 'none' || Number(s.opacity) === 0 ||
              x<0 || y<0 || x>=innerWidth || y>=innerHeight || !(hit===e || e.contains(hit)))
            throw Error('Control disabled, clipped, or occluded: '+SELECTOR);
          return {x,y,width:r.width,height:r.height};
        })()""".replace("SELECTOR", json.dumps(selector)))

    def click(self, selector: str):
        p = self.point(selector)
        click_at_xy(p["x"], p["y"])

    def fill(self, selector: str, value: str, commit: str | None = "Enter"):
        self.click(selector)
        # This CfT session does not honor the shared helper's Cmd+A in number inputs.
        # Clear with real End/Backspace events, then insert text through CDP's input path.
        expression = 'document.querySelector(' + json.dumps(selector) + ').value'
        press_key('End')
        for _ in range(min(2200, len(str(js(expression))) + 2)):
            if js(expression) == '':
                break
            press_key('Backspace')
        if js(expression) != '':
            raise RuntimeError('Native input clear failed: ' + selector)
        if str(value):
            cdp('Input.insertText', text=str(value))
        if commit:
            press_key(commit)

    def drag(self, selector: str, dx: float, dy: float = 0, steps: int = 12):
        """Real CDP mouse input. Derive deltas from the current timeline width."""
        p = self.point(selector)
        cdp("Input.dispatchMouseEvent", type="mouseMoved", x=p["x"], y=p["y"])
        cdp("Input.dispatchMouseEvent", type="mousePressed", x=p["x"], y=p["y"], button="left", buttons=1, clickCount=1)
        try:
            for step in range(1, steps + 1):
                cdp("Input.dispatchMouseEvent", type="mouseMoved", x=p["x"] + dx*step/steps,
                    y=p["y"] + dy*step/steps, button="left", buttons=1)
                time.sleep(0.015)
        finally:
            cdp("Input.dispatchMouseEvent", type="mouseReleased", x=p["x"]+dx, y=p["y"]+dy,
                button="left", buttons=0, clickCount=1)


def run_probe(config: dict):
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != CONTRACT:
        raise RuntimeError("Run through the canonical shared-browser runner.")
    output = owned_path(config["output"])
    # No context creation, target enumeration, anchor reuse, or tab activation.
    tab = new_tab()  # no URL means always create a fresh target in the default context
    probe = Probe(output, tab)
    try:
        cdp("Page.enable")
        cdp("Runtime.enable")
        cdp("Log.enable")
        cdp("Network.enable")
        cdp("Network.setCacheDisabled", cacheDisabled=True)
        cdp("Emulation.setDeviceMetricsOverride", width=config["width"], height=config["height"],
            deviceScaleFactor=1, mobile=False)
        cdp("Page.addScriptToEvaluateOnNewDocument", source=DIAGNOSTICS)
        result = cdp("Page.navigate", url=config["url"])
        if result.get("errorText"):
            raise RuntimeError(result["errorText"])
        if not wait_for_load(timeout=15):
            raise TimeoutError("Ready URL did not finish loading. No navigation retry was attempted.")
        if not wait_for_element("#root > *", timeout=10, visible=True):
            raise TimeoutError("React root did not render. Inspect the captured error state.")
        probe.snapshot("entry")
        if config.get("actions"):
            path = owned_path(config["actions"])
            namespace = {**globals(), "__name__": "__orbitwork_actions__", "probe": probe}
            exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
        probe.snapshot("exit")
    except BaseException as error:
        probe.save("failure.json", {"type": type(error).__name__, "message": str(error)})
        try:
            probe.snapshot("failure")
        except Exception as capture_error:
            print(f"Failure capture unavailable: {capture_error}", file=sys.stderr)
        raise
    finally:
        close_tab(tab)  # explicit owned target only. Invocation cleanup handles its own startup tab.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, type=local_url, help="Explicit server-ready URL from parent")
    parser.add_argument("--viewport", choices=["1440x1000", "1280x900"], default="1440x1000")
    parser.add_argument("--label", default="discovery")
    parser.add_argument("--actions", help="Owned Python action file, created after live exploration")
    args = parser.parse_args()
    if args.actions:
        try:
            actions = owned_path(args.actions)
            if not actions.is_file():
                raise ValueError(f"Action file does not exist: {actions}")
        except ValueError as error:
            parser.error(str(error))
    else:
        actions = None
    if not shutil.which("uv"):
        parser.error("Existing browser skill requires uv on PATH.")
    width, height = map(int, args.viewport.split("x"))
    label = re.sub(r"[^a-zA-Z0-9_-]+", "-", args.label).strip("-") or "discovery"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = owned_path(ROOT / "artifacts" / f"{stamp}-{label}-{args.viewport}")
    output.mkdir(parents=True, exist_ok=False)
    config = {"url": args.url, "width": width, "height": height, "output": str(output),
              "actions": str(actions) if actions else None}
    (output / "run.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["ORBITWORK_PROBE_CONFIG"] = json.dumps(config)
    # Ensure normal invocation-local cleanup, even if a legacy persistent option was inherited.
    for key in ("BH_BROWSER_PERSISTENT", "BH_BROWSER_LEASE_CONTRACT", "BH_TMP_DIR", "BH_NAME"):
        env.pop(key, None)
    code = ("import json, os, runpy; "
            f"scope = runpy.run_path({str(Path(__file__).resolve())!r}, "
            "init_globals=globals(), run_name='orbitwork_probe_payload'); "
            "scope['run_probe'](json.loads(os.environ['ORBITWORK_PROBE_CONFIG']))")
    command = ["uv", "run", str(SCRIPTS / "run_with_browser.py"), "--", "uv", "run",
               str(SCRIPTS / "browser_harness.py"), "-c", code]
    if sys.platform == "darwin" and shutil.which("caffeinate"):
        command = ["caffeinate", "-dims", *command]
    print(f"Artifacts: {output}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    (output / "process.json").write_text(json.dumps({"returncode": completed.returncode}) + "\n", encoding="utf-8")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
