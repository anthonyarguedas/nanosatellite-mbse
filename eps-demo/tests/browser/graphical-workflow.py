"""Graphical EPS regression through real UI controls.

Run with chrome_probe.py --actions graphical-workflow.py.
EPS_CANVAS_PHASE=graph|workflow|battery|io|kicad|mission|narrow|all.
Use a fresh isolated loopback origin. These tests replace its authored design.
The owned tab is closed by the driver. Native file-save completion is untested.
"""
import copy
import math
import os
import zipfile

exec(compile((ROOT / 'canvas_helpers.py').read_text(), str(ROOT / 'canvas_helpers.py'), 'exec'), globals())

SOLAR = 'azur-3g30c-advanced-81780'
PACK = 'gomspace-bp8-100wh-8s1p'
BOARD = 'gomspace-p80-config1'
INTEGRATED = 'isis-iceps2-type-a'


def states():
    return read("""Object.fromEntries([...document.querySelectorAll('[data-activity]')].map(e=>
      [e.dataset.activity,['complete','ready','stale','locked'].find(s=>e.classList.contains(s))]))""")


def load_example():
    before = copy.deepcopy(authored())
    project_action(r'^Load BIRDS-4')
    probe.wait_js("!!document.querySelector('[data-action=confirm-load-example]')")
    probe.check('example confirmation preserves the design until acceptance', authored() == before)
    probe.click('[data-action="confirm-load-example"]')
    probe.wait_js("document.querySelectorAll('.graph-activity.complete').length===10")
    dismiss_notifications()
    probe.check('example has ten current activities', set(states().values()) == {'complete'}, states())


def activity(node):
    close_context()
    point = activity_point(node)
    click_at_xy(point['x'], point['y'])
    probe.wait_js("document.querySelectorAll('[role=dialog]').length===1")
    time.sleep(0.15)  # Settle the dock resize/Fit before measuring edit stability.


def role(name):
    close_context()
    probe.click('.composition-role[data-role=' + json.dumps(name) + ']')
    probe.wait_js("document.querySelectorAll('[role=dialog]').length===1")


def product(role_name, product_id, query):
    role(role_name)
    click_control('Compare products for this role', '.sheet', exact=True)
    probe.wait_js("!!document.querySelector('[aria-label=\"Search catalog products\"]')")
    probe.fill('[aria-label="Search catalog products"]', query, commit=None)
    selector = '[data-inspect-product=' + json.dumps(product_id) + ']'
    probe.wait_js('!!document.querySelector(' + json.dumps(selector) + ')')
    probe.click(selector)
    probe.wait_js("!!document.querySelector('.allocation-controls')")
    probe.check('product evidence replaces the prior surface', read("document.querySelectorAll('[role=dialog]').length===1"))


def apply_product(role_name):
    select_value(field('Selection role'), role_name)
    probe.click('.allocation-controls .button.primary')
    dismiss_notifications()


def active_case(case):
    close_context()
    select_value(field('Active scenario', '.canvas-header'), case)
    recalculate()


def composition_geometry(label):
    geometry = read("""(() => {
      const failures=[],cells=[...document.querySelectorAll('.composition-role,.variation-point')];
      const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width}};
      for(const cell of cells){
        const b=rect(cell),walker=document.createTreeWalker(cell,NodeFilter.SHOW_TEXT);
        while(walker.nextNode()){
          if(!walker.currentNode.textContent.trim())continue;
          const range=document.createRange();range.selectNodeContents(walker.currentNode);
          for(const r of range.getClientRects())if(r.width&&r.height&&
            (r.left<b.left-1.5||r.right>b.right+1.5||r.top<b.top-1.5||r.bottom>b.bottom+1.5))
            failures.push({text:walker.currentNode.textContent,button:b,textBounds:rect(range)});
        }
      }
      for(let i=0;i<cells.length;i++)for(let j=i+1;j<cells.length;j++){
        const a=rect(cells[i]),b=rect(cells[j]);
        if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)
          failures.push({overlap:[i,j]});
      }
      return {failures,canvasWidth:document.querySelector('.canvas-background').getBoundingClientRect().width,
        roleColumns:getComputedStyle(document.querySelector('.composition-roles')).gridTemplateColumns,
        areaColumns:getComputedStyle(document.querySelector('.eps-design-layout')).gridTemplateColumns};
    })()""")
    probe.check(label + ' role/variation labels fit with no neighboring overlap', not geometry['failures'], geometry)
    assert_no_overflow(label)
    return geometry


def graph():
    load_example()
    initial = (read('innerWidth'), read('innerHeight'))
    probe.check('all activities and roles are native buttons', read("document.querySelectorAll('button.graph-activity[data-activity]').length===10&&document.querySelectorAll('button.composition-role[data-role]').length===6"))
    read("document.querySelector('.activity-workspace').scrollIntoView({block:'center',behavior:'instant'});document.querySelector('.activity-workspace').focus({preventScroll:true})")
    expected = read("[...document.querySelectorAll('.graph-activity')].map(e=>e.dataset.activity)")

    def assert_native_focus(node, direction):
        # Observe the result of native Tab only. Calling focus_activity here would
        # replace the action under test and can hide a broken keyboard reveal.
        geometry = probe.wait_js("""(() => {
          const e=document.activeElement;if(e?.dataset.activity!==NODE)return false;
          const r=e.getBoundingClientRect(),b=e.closest('.activity-workspace').getBoundingClientRect();
          const flow=e.closest('.react-flow');
          if(flow.scrollTop||flow.scrollLeft||r.left<b.left-1||r.right>b.right+1||
            r.top<b.top-1||r.bottom>b.bottom+1||r.top<0||r.bottom>innerHeight)return false;
          return {node:e.dataset.activity,rect:r.toJSON(),bounds:b.toJSON(),
            transform:document.querySelector('.react-flow__viewport').style.transform};
        })()""".replace('NODE', json.dumps(node)))
        probe.check(direction + ' native Tab reveals ' + node, True, geometry)

    for node in expected:
        press_key('Tab')
        assert_native_focus(node, 'forward')
    probe.check('all ten activities reachable by native Tab with focus reveal', len(expected) == 10, expected)
    press_key('Tab')  # Leave the graph through its ordinary next control.
    for node in reversed(expected):
        press_key('Tab', modifiers=8)
        assert_native_focus(node, 'reverse')
    for node in expected:
        activity(node)
        probe.check(node + ' opens one root inspector without accidental Back', not has('[data-action=context-back]'))
    close_context()
    before = read("document.querySelector('.react-flow__viewport').style.transform")
    read("document.querySelector('.activity-workspace').focus()")
    press_key('ArrowRight')
    probe.wait_js("document.querySelector('.react-flow__viewport').style.transform!==" + json.dumps(before))
    probe.check('focused graph arrow key pans the camera', True)
    # Use a clear corner of the actual pane, without selecting a node.
    corner = read("(() => {const r=document.querySelector('.activity-workspace').getBoundingClientRect();return {x:r.right-15,y:r.bottom-35};})()")
    before = read("document.querySelector('.react-flow__viewport').style.transform")
    cdp('Input.dispatchMouseEvent', type='mouseMoved', **corner)
    cdp('Input.dispatchMouseEvent', type='mousePressed', button='left', buttons=1, clickCount=1, **corner)
    cdp('Input.dispatchMouseEvent', type='mouseMoved', x=corner['x']-65, y=corner['y']-20, button='left', buttons=1)
    cdp('Input.dispatchMouseEvent', type='mouseReleased', x=corner['x']-65, y=corner['y']-20, button='left', buttons=0, clickCount=1)
    probe.wait_js("document.querySelector('.react-flow__viewport').style.transform!==" + json.dumps(before))
    probe.check('native pointer drag pans the graph', True)
    before = read("document.querySelector('.graph-zoom').textContent")
    probe.click('[aria-label="Zoom in"]')
    probe.wait_js("document.querySelector('.graph-zoom').textContent!==" + json.dumps(before))
    probe.click('[aria-label="Zoom out"]')
    probe.click('.graph-fit')
    probe.wait_js("Number(document.querySelector('.graph-zoom').textContent.replace('%',''))>=85")
    probe.check('zoom controls and Fit retain a readable scale', True)
    for name in ['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software']:
        role(name)
        close_context()
        probe.check(name + ' role association persists after dismissal', read("document.querySelector('[data-role='+" + json.dumps(name) + "+']').dataset.linked==='true'"))
    for axis in ['conditioning', 'transfer', 'bus', 'outputs']:
        probe.click('[data-variation=' + json.dumps(axis) + ']')
        probe.check(axis + ' variation focuses its matching inspector axis', read("document.activeElement?.dataset.topologyAxis===" + json.dumps(axis)))
        close_context()
        probe.check(axis + ' variation selection persists after dismissal', read("document.querySelector('[data-variation='+" + json.dumps(axis) + "+']').getAttribute('aria-pressed')==='true'"))
    if initial[0] > 900:
        activity('mission')
        probe.check('desktop inspector leaves background operable', read("!document.querySelector('.canvas-background').inert&&!document.querySelector('.canvas-header').inert&&document.querySelector('.sheet').getAttribute('aria-modal')==='false'&&!document.querySelector('.sheet-scrim')"))
        allocations = copy.deepcopy(authored()['allocations'])
        probe.fill(field('Orbit altitude'), '420')
        probe.check('dock edit leaves nine activities stale', sum(v == 'stale' for v in states().values()) == 9)
        probe.click('[data-action=recalculate]')
        probe.check('global Recalculate works without dismissing the desktop dock', has('[role=dialog]') and set(states().values()) == {'complete'})
        probe.check('recalculation keeps frozen allocation receipts', authored()['allocations'] == allocations)
        read("document.querySelector('.activity-workspace').focus()")
        press_key('Escape')
        probe.check('Escape on desktop background leaves context open', has('[role=dialog]'))
        probe.click('[data-role=conditioning]')
        probe.check('background root switch replaces inspector without Back history', not has('[data-action=context-back]'))
        probe.click('.role-evidence-button')
        press_key('Escape')
        probe.wait_js("!!document.querySelector('.role-evidence-button')")
        probe.check('nested Escape restores role evidence focus', read("document.activeElement.matches('.role-evidence-button')"))
        close_context()
        for width, height in [(1440,900),(1280,900),(1024,768)]:
            cdp('Emulation.setDeviceMetricsOverride', width=width, height=height, deviceScaleFactor=1, mobile=False)
            role('conditioning')
            composition_geometry('normal dock ' + str(width))
            if width == 1440:
                click_control('Compare products for this role', '.sheet', exact=True)
                probe.wait_js("document.querySelector('.context-host').dataset.expanded==='true'")
                geometry = composition_geometry('expanded catalog 1440')
                probe.check('expanded catalog uses two role columns in its 480px canvas', abs(geometry['canvasWidth']-480)<2 and len(geometry['roleColumns'].split())==2, geometry)
                probe.fill('[aria-label="Search catalog products"]', 'P80', commit=None)
                probe.click('[data-inspect-product="gomspace-p80-config1"]')
                probe.click('[data-action=context-back]')
                probe.wait_js("!!document.querySelector('[aria-label=\"Search catalog products\"]')")
                probe.check('product Back preserves catalog filter and focus', read("document.querySelector('[aria-label=\"Search catalog products\"]').value==='P80'&&document.activeElement?.dataset.inspectProduct==='gomspace-p80-config1'"))
                probe.click('[data-action=context-back]')
                probe.check('catalog Back retains expanded role context and trigger focus', read("document.querySelector('.context-host').dataset.expanded==='true'&&document.activeElement?.dataset.focusKey==='role-catalog'"))
                composition_geometry('expanded Back-to-role 1440')
            close_context()
        cdp('Emulation.setDeviceMetricsOverride', width=initial[0], height=initial[1], deviceScaleFactor=1, mobile=False)
    composition_geometry('graph final')
    load_example()


def workflow():
    load_example()
    probe.check('one canvas without legacy navigation or sidebar', read("!!document.querySelector('.design-canvas')&&!document.querySelector('.icon-rail,.workspace-tabs,.architecture-pane')"))
    probe.check('six CSRM logical groups and four topology variation points', read("document.querySelectorAll('.composition-role').length===6&&document.querySelectorAll('[data-variation]').length===4"))
    probe.check('compact reference breadcrumbs preserve mission hierarchy', read("['mission','space-segment','cubesat'].every(id=>!!document.querySelector('[data-testid=reference-context] [data-reference='+id+']'))"))
    probe.check('software stays visibly unallocated', read("document.querySelector('[data-role=software]').innerText.includes('Software not allocated')"))
    probe.snapshot('evaluated-birds4-canvas')
    point = activity_point('solar')
    cdp('Input.dispatchMouseEvent', type='mouseMoved', x=point['x'], y=point['y'])
    probe.wait_js("document.querySelectorAll('.composition-role[data-linked=true]').length===1&&document.querySelector('[data-role=solar]').dataset.linked==='true'")
    probe.check('activity hover links the corresponding CSRM group', read("document.querySelector('[data-role=solar]').dataset.linked==='true'"))
    data, _ = export_design('default-birds4')
    probe.check('export contains ten evaluated records', len(current_records(data)) == 10)
    probe.check('sourced typical pack energy transferred without nameplate substitution', data['inputs']['battery']['capacityWh'] == 86)
    probe.check('default required array power', math.isclose(data['analysis']['solar']['minimumPowerW'], 4.320456, abs_tol=1e-6))
    probe.check('default required battery energy', math.isclose(data['analysis']['battery']['requiredWh'], 4.759773, abs_tol=1e-6))
    probe.check('EPS idle demand appears in the budget once', math.isclose(data['analysis']['budget']['averageW'], 2.0745, abs_tol=1e-9))
    checks = {c['id']: c for c in data['analysis']['checks']}
    probe.check('known mass failure and full charge-model gaps retained', checks['EPS-19']['verdict'] == 'fail' and all(checks[x]['verdict'] == 'unassessed' for x in ['EPS-10', 'EPS-11']))
    probe.check('routine energy subchecks pass in their scope', all(checks[x]['verdict'] == 'pass' for x in ['ENERGY-DEMAND', 'ENERGY-RESERVE', 'ENERGY-CLOSURE']))
    activity('mission')
    probe.check('focused inspector has viewport-appropriate modality', read("document.querySelectorAll('[role=dialog]').length===1&&document.querySelector('.sheet').contains(document.activeElement)&&document.querySelector('.canvas-background').inert===matchMedia('(max-width:900px)').matches&&document.querySelector('.sheet').getAttribute('aria-modal')===String(matchMedia('(max-width:900px)').matches)"))
    probe.fill(field('Orbit altitude'), '450')
    close_context()
    changed = states()
    probe.check('mission edit keeps only scenarios current', changed['scenarios'] == 'complete' and sum(v == 'stale' for v in changed.values()) == 9, changed)
    probe.check('stale activities identify saved values', read("document.querySelector('[data-activity=orbit]').innerText.includes('Saved')"))
    recalculate()
    probe.check('recalculation follows dependencies to completion', set(states().values()) == {'complete'})
    load_example()
    allocations = copy.deepcopy(authored()['allocations'])
    activity('scenarios')
    camera = read("document.querySelector('.react-flow__viewport').style.transform")
    move = '[aria-label="Move CAM imaging window 1"]'
    width = read('document.querySelector(' + json.dumps(move) + ').closest("[data-scenario-track]").getBoundingClientRect().width')
    probe.drag(move, width * 0.05)
    probe.check('real pointer moves the camera window five percent', math.isclose(float(read('document.querySelector(' + json.dumps(move) + ').getAttribute("aria-valuenow")')), 21, abs_tol=0.1))
    probe.click('[aria-label="CAM imaging load"] .scenario-numeric-summary')
    probe.fill('[aria-label="CAM imaging window 1 start (%)"]', '20')
    probe.fill('[aria-label="CAM imaging window 1 end (%)"]', '26')
    probe.check('numeric scheduling alternative commits', math.isclose(authored()['inputs']['scenarios'][0]['loads'][2]['windows'][0]['start'], 0.2))
    read('document.querySelector(' + json.dumps(move) + ').focus()')
    press_key('ArrowRight')
    press_key('ArrowLeft', modifiers=8)
    probe.check('schedule keyboard arrows support one-percent and fine steps', math.isclose(authored()['inputs']['scenarios'][0]['loads'][2]['windows'][0]['start'], 0.209, abs_tol=1e-9))
    probe.check('ordinary schedule edits preserve the graph camera', read("document.querySelector('.react-flow__viewport').style.transform") == camera)
    probe.snapshot('graphical-load-schedule')
    close_context()
    probe.check('schedule edits retain mission and orbit results', states()['mission'] == states()['orbit'] == 'complete' and sum(v == 'stale' for v in states().values()) == 8, states())
    recalculate()
    active_case('birds4-stress')
    stress, _ = export_design('overlapping-case')
    probe.check('overlapping missions retain an energy-closure failure', next(c for c in stress['analysis']['checks'] if c['id'] == 'EPS-11')['verdict'] == 'fail')
    probe.check('scenario change has not changed installed source availability', stress['inputs']['solar']['installedPowerW'] == data['inputs']['solar']['installedPowerW'])
    probe.check('scenario change retains frozen physical usages and concept counts', stress['allocations'] == allocations)
    activity('assessment')
    probe.check('all twenty EPS requirement rows remain reachable', read("[...document.querySelectorAll('.check-id')].filter(e=>/^EPS-\\d\\d$/.test(e.textContent)).length===20"))
    click_control('Energy timeline', '.report-tabs', exact=False)
    probe.wait_js("!!document.querySelector('.energy-plots')")
    probe.snapshot('overlapping-energy-findings')
    active_case('birds4-survival')
    reduced, _ = export_design('reduced-generation-case')
    probe.check('reduced-generation case evaluates three orbits', reduced['analysis']['simulation']['scenarioId'] == 'birds4-survival' and next(s for s in reduced['inputs']['scenarios'] if s['id'] == 'birds4-survival')['durationOrbits'] == 3)
    load_example()
    probe.click('[data-variation="conditioning"]')
    probe.click('.topology-editor input[name="conditioning"][value="DET"]')
    recalculate()
    probe.check('graphical DET choice persists while unsupported propagation stays gated', authored()['inputs']['topology']['conditioning'] == 'DET' and states()['simulation'] != 'complete' and states()['assessment'] == 'complete')
    activity('simulation')
    probe.check('unsupported DET has an actionable operating-point explanation', read("document.querySelector('.sheet').innerText.includes('I–V operating point')"))
    probe.check('DET retains historical energy plots and charge-SoC distinction', read("!!document.querySelector('.energy-plots')&&document.querySelector('.sheet').innerText.includes('Historical')&&document.querySelector('.sheet').innerText.includes('not charge-based state of charge')"))
    close_context()
    probe.click('[data-variation="conditioning"]')
    for selector in ['input[name="conditioning"][value="MPPT"]', 'input[name="transfer"][value="distributed"]', 'input[name="bus"][value="unregulated"]']:
        probe.click('.topology-editor ' + selector)
    recalculate()
    topology = authored()['inputs']['topology']
    probe.check('represented variation choices mutate their authored intent', topology['conditioning'] == 'MPPT' and topology['distribution'] == 'distributed' and topology['bus'] == 'unregulated' and set(states().values()) == {'complete'})
    load_example()


def battery():
    load_example()
    product('conditioning', INTEGRATED, 'ICEPS2')
    apply_product('conditioning')
    recalculate()
    partial, _ = export_design('missing-pack-energy')
    probe.check('unknown integrated pack energy remains null', partial['inputs']['battery']['capacityWh'] is None)
    probe.check('missing pack energy no longer blocks requirement sizing or catalog screening', states()['battery'] == states()['candidates'] == states()['assessment'] == 'complete', states())
    probe.check('installed battery data still gates propagation', states()['simulation'] != 'complete')
    checks = {c['id']: c for c in partial['analysis']['checks']}
    probe.check('partial review excludes the saved simulation as current evidence', checks['ENERGY-RESERVE']['verdict'] == 'unassessed')
    activity('battery')
    probe.check('pack field is visibly unresolved while required energy is available', read('document.querySelector(' + json.dumps(field('BOL pack energy')) + ').value') == '' and partial['analysis']['battery']['requiredWh'] > 0)
    probe.snapshot('battery-sizing-with-unresolved-pack')
    # Replace the integrated board while capacity is unresolved. No made-up
    # capacity is needed to escape the selection path.
    product('conditioning', BOARD, 'P80')
    apply_product('conditioning')
    recalculate()
    product('battery', PACK, 'BP8')
    apply_product('battery')
    recalculate()
    probe.check('published pack alternative restores a complete energy path', authored()['inputs']['battery']['capacityWh'] == 86 and set(states().values()) == {'complete'})
    # A separately authored assumption can support a study, while the product
    # record itself keeps its unresolved usable-energy field.
    product('conditioning', INTEGRATED, 'ICEPS2')
    apply_product('conditioning')
    recalculate()
    activity('battery')
    probe.fill(field('BOL pack energy'), '8')
    recalculate()
    assumed, _ = export_design('explicit-pack-study-assumption')
    entry = next(p for p in assumed['selectedCatalogEntries'] if p['id'] == INTEGRATED)
    probe.check('manual study input is preserved without repairing catalog evidence', assumed['inputs']['battery']['capacityWh'] == 8 and entry['specs']['energyWh']['status'] == 'missing' and entry['specs']['energyWh']['value'] is None)
    probe.check('explicit capacity permits the scoped simulation', states()['simulation'] == 'complete')
    activity('battery')
    probe.fill(field('BOL pack energy'), '-1')
    recalculate()
    probe.check('invalid installed capacity blocks consumers without discarding independent sizing', states()['battery'] == states()['candidates'] == 'complete' and states()['assessment'] != 'complete' and not has('[role=alert]'), states())
    load_example()


def io():
    load_example()
    original, path = export_design('roundtrip-original')
    before = copy.deepcopy(authored())
    before_states = states()
    bad = probe.output / 'malformed.json'
    bad.write_text('{not valid json')
    import_design(bad)
    probe.wait_js("!!document.querySelector('[role=alert]')")
    probe.check('invalid import preserves authored inputs and result currency', authored() == before and states() == before_states)
    dismiss_notifications()
    tampered = copy.deepcopy(original)
    next(record for record in tampered['provenance'] if record['parameter'] == 'topology.idlePowerW')['sourceIds'] = ['unresolved-test-source']
    tampered_path = probe.output / 'dangling-assumption-source.json'
    tampered_path.write_text(json.dumps(tampered))
    import_design(tampered_path)
    probe.wait_js("!!document.querySelector('[role=alert]')")
    probe.check('dangling assumption sources are rejected without replacing the design', authored() == before and states() == before_states and read("document.querySelector('[role=alert]').innerText.includes('source references are unresolved')"))
    dismiss_notifications()
    project_action(r'^New design$')
    probe.wait_js("!!document.querySelector('[data-action=confirm-new-design]')")
    probe.click('[data-action="confirm-new-design"]')
    dismiss_notifications()
    probe.check('new design has explicit missing inputs and no allocations', set(states().values()) == {'locked'} and authored()['selections'] == {}, states())
    probe.check('empty design cannot recalculate missing inputs', read("document.querySelector('[data-action=recalculate]').disabled"))
    import_design(path)
    probe.wait_js("document.querySelector('.canvas-mission-name').innerText.includes('BIRDS-4')")
    probe.check('JSON import restores the authored model including allocation metadata', authored() == before)
    probe.check('JSON import discards calculation caches', len(states()) == 10 and all(v != 'complete' for v in states().values()), states())
    recalculate()
    restored, _ = export_design('roundtrip-recomputed')
    probe.check('recomputed results equal the exported analysis', restored['analysis'] == original['analysis'])
    time_origin = read('performance.timeOrigin')
    cdp('Page.reload', ignoreCache=True)
    probe.wait_js("performance.timeOrigin!==" + json.dumps(time_origin) + "&&document.readyState==='complete'&&!!document.querySelector('.canvas-header')&&document.querySelectorAll('[data-activity]').length===10", timeout=15)
    probe.check('reload retains authored inputs and discards caches', authored() == before and len(states()) == 10 and all(v != 'complete' for v in states().values()))
    recalculate()
    probe.check('reloaded example recomputes end to end', set(states().values()) == {'complete'})
    probe.snapshot('json-roundtrip-recomputed')
    legacy = copy.deepcopy(original)
    legacy.pop('allocations', None)
    legacy.pop('provenance', None)
    legacy_path = probe.output / 'legacy-selected-products.json'
    legacy_path.write_text(json.dumps(legacy))
    import_design(legacy_path)
    recalculate()
    probe.check('legacy selections gain no invented allocation metadata', not authored().get('allocations'))
    product('battery', PACK, 'BP8')
    probe.check('already selected legacy product can confirm its missing count', not read("document.querySelector('.allocation-controls .button.primary').disabled") and read("document.querySelector('.allocation-controls').innerText.includes('Update allocation')"))
    apply_product('battery')
    recalculate()
    receipts = authored().get('allocations', [])
    probe.check('legacy confirmation freezes only the explicitly applied product', len(receipts) == 1 and receipts[0]['productId'] == PACK and receipts[0]['quantity'] == 1)
    load_example()


def kicad():
    load_example()
    active_case('birds4-stress')
    probe.click('[data-action="kicad"]')
    probe.wait_js("!!document.querySelector('.kicad-panel__footer')", timeout=10)
    probe.check('logical export is reachable for the current illustrative allocation', not read("document.querySelector('.kicad-panel__footer .button').disabled"))
    probe.check('physical routing remains an explicit separate gate', read("document.querySelector('.sheet').innerText.includes('Missing physical design inputs')"))
    archive = capture_download(lambda: probe.click('.kicad-panel__footer .button'), 'birds4-logical-review.zip')
    destination = probe.output / 'birds4-logical-review'
    destination.mkdir()
    with zipfile.ZipFile(archive) as source:
        probe.check('UI-generated review ZIP has valid CRCs', source.testzip() is None)
        for name in source.namelist():
            if destination.resolve() not in (destination / name).resolve().parents:
                raise ValueError('Unsafe review archive path')
        source.extractall(destination)
    manifest = json.loads((destination / 'manifest.json').read_text())
    usages = manifest['usages']
    probe.check('three unique physical allocations preserve shared P80 roles', len(usages) == 3 and len(next(u for u in usages if u['productId'] == BOARD)['allocatedRoles']) == 3)
    probe.check('review freezes three allocated cells despite a larger stress-case suggestion', next(u for u in usages if u['productId'] == SOLAR)['quantity'] == 3)
    probe.check('review retains exact catalog source records', all(u['catalogEntryRevision'] == u['product']['revision'] and u['product']['sources'] for u in usages))
    probe.check('review has a real native project and no physical PCB', (destination / 'orbitwork-review.kicad_pro').is_file() and len(list(destination.glob('*.kicad_sch'))) >= 5 and not list(destination.glob('*.kicad_pcb')))
    probe.check('review manifest retains physical routing block', manifest['physicalRouting']['status'] == 'blocked' and manifest['physicalRouting']['boardGenerated'] is False)
    probe.snapshot('logical-kicad-handoff')
    before = copy.deepcopy(authored())
    click_control('Import an approved rule profile', '.sheet', exact=True)
    template_path = capture_download(lambda: probe.click('.kicad-panel__actions button:first-child'), 'unapproved-rule-template.json')
    template = json.loads(template_path.read_text())
    probe.check('physical rule template supplies no approval or fabricated dimensions', template['approval']['status'] == 'unreviewed' and all(value is None for key, value in template['fabrication'].items() if key != 'sourceIds'))
    import_file(lambda: probe.click('.kicad-panel__actions button:nth-child(2)'), template_path)
    probe.wait_js("!!document.querySelector('.sheet [role=alert]')")
    probe.check('unapproved physical rules are rejected without changing EPS evidence', not has('.kicad-panel__rule-result') and authored() == before)
    load_example()


def mission():
    load_example()
    before = copy.deepcopy(authored()['inputs'])
    activity('mission')
    click_control('Explore mission analogues from ConOps', '.sheet', exact=False)
    probe.wait_js("!!document.querySelector('.mission-assist textarea')", timeout=10)
    select_value('.mission-assist select', 'lexical-tfidf')
    click_control('Vegetation imaging', '.mission-assist', exact=True)
    probe.click('.ma-search')
    probe.wait_js("!!document.querySelector('.ma-result-label')")
    after = copy.deepcopy(authored()['inputs'])
    after['mission'].pop('conOps', None)
    after['mission'].pop('orbitSuggestion', None)
    before['mission'].pop('conOps', None)
    before['mission'].pop('orbitSuggestion', None)
    probe.check('mission retrieval changes no numerical input', after == before)
    probe.check('lexical method is explicit', read("document.querySelector('.ma-result-label').innerText.includes('Lexical TF-IDF')"))
    probe.check('scalar parameter transfer requires explicit acceptance', read("[...document.querySelectorAll('.ma-accept button')].length>0&&[...document.querySelectorAll('.ma-accept button')].every(e=>e.disabled)"))
    probe.snapshot('mission-analogue-evidence')
    card_index = read("[...document.querySelectorAll('.ma-card')].findIndex(card=>!!card.querySelector('.ma-accept input'))") + 1
    card = '.ma-card:nth-of-type(' + str(card_index) + ')'
    probe.click(card + ' .ma-accept input')
    probe.click(card + ' .ma-accept button')
    receipt = authored()['inputs']['mission']['orbitSuggestion']
    accepted_inputs = copy.deepcopy(authored()['inputs'])
    accepted_inputs['mission'].pop('conOps', None)
    accepted_inputs['mission'].pop('orbitSuggestion', None)
    expected = copy.deepcopy(before)
    expected['mission']['altitudeKm'] = receipt['altitudeKm']
    probe.check('explicit acceptance transfers only sourced altitude with its receipt', accepted_inputs == expected and receipt['method'] == 'lexical-tfidf' and bool(receipt['parameterSourceIds']))
    _, accepted_path = export_design('accepted-mission-analogue')
    import_design(accepted_path)
    probe.check('accepted mission evidence survives JSON restoration', authored()['inputs']['mission']['orbitSuggestion'] == receipt and not has('[role=alert]'))
    activity('mission')
    click_control('Explore mission analogues from ConOps', '.sheet')
    probe.wait_js("!!document.querySelector('.mission-assist textarea')", timeout=10)
    select_value('.mission-assist select', 'lexical-tfidf')
    click_control('Unrelated input', '.mission-assist', exact=True)
    probe.click('.ma-search')
    probe.wait_js("!!document.querySelector('.ma-result-label')")
    probe.check('unrelated mission description abstains', not has('.ma-card'))
    probe.check('edited ConOps clears the previous acceptance without losing altitude', 'orbitSuggestion' not in authored()['inputs']['mission'] and authored()['inputs']['mission']['altitudeKm'] == receipt['altitudeKm'])
    edited = copy.deepcopy(authored())
    _, edited_path = export_design('edited-mission-context')
    import_design(edited_path)
    probe.check('edited mission context remains safely restorable', authored() == edited and not has('[role=alert]'))
    load_example()


def narrow():
    load_example()
    assert_no_overflow('canvas')
    probe.click('[data-testid="reference-context"]')
    probe.check('all nine reference subsystem categories are available in context', read("document.querySelectorAll('.reference-subsystems > span').length===9&&document.querySelectorAll('[role=dialog]').length===1"))
    assert_no_overflow('expanded reference context')
    probe.snapshot('reference-context')
    close_context()
    selector = focus_activity('battery')
    press_key('Enter')
    probe.wait_js("!!document.querySelector('[role=dialog]')")
    probe.check('keyboard activity activation focuses one inspector', read("document.querySelectorAll('[role=dialog]').length===1&&document.querySelector('.sheet').contains(document.activeElement)"))
    modal = read("matchMedia('(max-width:900px)').matches")
    read("document.querySelector('.sheet button').focus()")
    press_key('Tab', modifiers=8)
    probe.check('reverse Tab matches modal versus nonmodal semantics', read("document.querySelector('.sheet').contains(document.activeElement)") == modal)
    assert_no_overflow('battery context')
    read("document.querySelector('.sheet button').focus()")
    press_key('Escape')
    probe.wait_js("!document.querySelector('[role=dialog]')")
    probe.check('Escape restores focus to the originating activity', read("document.activeElement?.dataset.activity==='battery'"))
    activity('scenarios')
    probe.check('graphical scheduler remains available at this width', has('[aria-label="Move CAM imaging window 1"]'))
    probe.click('[aria-label="CAM imaging load"] .scenario-numeric-summary')
    probe.fill('[aria-label="CAM imaging window 1 start (%)"]', '17')
    probe.check('narrow schedule numeric alternative works', math.isclose(authored()['inputs']['scenarios'][0]['loads'][2]['windows'][0]['start'], 0.17))
    assert_no_overflow('schedule context')
    probe.snapshot('narrow-schedule-context')
    recalculate()
    activity('assessment')
    click_control('Energy timeline', '.report-tabs')
    probe.wait_js("!!document.querySelector('.energy-plots')")
    probe.point('.stored-energy-plot')
    chart = read("(() => {const r=document.querySelector('.stored-energy-plot').getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,viewport:innerWidth};})()")
    probe.check('energy plot fits inside the visible context', chart['left'] >= 0 and chart['right'] <= chart['viewport'] + 1 and chart['width'] >= 180, chart)
    assert_no_overflow('energy review context')
    probe.snapshot('narrow-energy-context')
    close_context()
    product('conditioning', INTEGRATED, 'ICEPS2')
    probe.check('catalog and product evidence use one contextual surface', read("document.querySelectorAll('[role=dialog]').length===1"))
    probe.click('[data-action="context-back"]')
    probe.wait_js("!!document.querySelector('[aria-label=\"Search catalog products\"]')")
    probe.check('Back restores catalog filters and originating product focus', read("document.querySelector('[aria-label=\"Search catalog products\"]').value==='ICEPS2'&&document.activeElement?.dataset.inspectProduct==='isis-iceps2-type-a'"))
    assert_no_overflow('catalog context')
    close_context()
    probe.snapshot('responsive-canvas')
    load_example()


phase = os.environ.get('EPS_CANVAS_PHASE', 'workflow')
flows = {'graph': graph, 'workflow': workflow, 'battery': battery, 'io': io, 'kicad': kicad, 'mission': mission, 'narrow': narrow}
if phase not in {*flows, 'all'}:
    raise ValueError('Unknown EPS_CANVAS_PHASE: ' + phase)
phase_results = []
for name, run in flows.items():
    if phase in {name, 'all'}:
        result = {'phase': name, 'status': 'running', 'firstCheck': len(probe.journal)}
        phase_results.append(result)
        probe.save('phases.json', phase_results)
        try:
            run()
        except BaseException as error:
            result.update(status='failed', error=str(error), checks=len(probe.journal)-result['firstCheck'])
            probe.save('phases.json', phase_results)
            raise
        result.update(status='passed', checks=len(probe.journal)-result['firstCheck'])
        probe.save('phases.json', phase_results)
assert_no_overflow('final canvas')
diagnostics = read('window.__orbitworkProbeDiagnostics')
probe.check('no browser console errors or unhandled exceptions', not diagnostics['errors'] and not [m for m in diagnostics['console'] if m['level'] == 'error'], diagnostics)
probe.snapshot('finished-' + phase)
