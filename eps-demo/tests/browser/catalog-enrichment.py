"""Source-enriched catalog UI regression.

Run with chrome_probe.py --actions catalog-enrichment.py.
EPS_CATALOG_PHASE=coverage|battery|roles|all. Ordinary UI controls only.
Use an isolated loopback origin. These checks replace only its authored design.
"""
import ast
import copy
import math
import os
import re

exec(compile((ROOT / 'canvas_helpers.py').read_text(), str(ROOT / 'canvas_helpers.py'), 'exec'), globals())
_tree = ast.parse((ROOT / 'graphical-workflow.py').read_text())
exec(compile(ast.Module(body=[node for node in _tree.body if isinstance(node, (ast.FunctionDef, ast.Import, ast.ImportFrom))], type_ignores=[]), 'graphical-workflow-definitions', 'exec'), globals())
SOLAR = 'azur-3g30c-advanced-81780'
PACK = 'gomspace-bp8-100wh-8s1p'
BOARD = 'gomspace-p80-config1'
CATALOG = json.loads((ROOT.parents[1] / 'src/data/catalog.json').read_text())


def open_role_catalog(role_name):
    role(role_name)
    click_control('Compare products for this role', '.sheet', exact=True)
    probe.wait_js("!!document.querySelector('[aria-label=\"Search catalog products\"]')")


def coverage_flow():
    load_example()
    for role_name in ['solar', 'battery', 'conditioning', 'distribution', 'processor', 'software']:
        open_role_catalog(role_name)
        select_value(field('Comparison data'), 'covered')
        probe.wait_js("document.querySelectorAll('.product-card').length>=3")
        rows = read("""(() => {
          return [...document.querySelectorAll('.product-card')].map(card=>{
            const match=card.innerText.match(/Comparison data\\s*(\\d+)\\/(\\d+)/);
            return {name:card.querySelector('h3').innerText,covered:match?Number(match[1]):null,required:match?Number(match[2]):null};
          });
        })()""")
        probe.check(role_name + ' has at least three covered product comparisons', len(rows) >= 3, rows)
        probe.check(role_name + ' filter excludes mandatory data gaps', all(row['covered'] == row['required'] and row['required'] for row in rows), rows)
        assert_no_overflow(role_name + ' catalog')
        if role_name in {'battery', 'software', 'processor'}:
            probe.snapshot(role_name + '-comparison-options')
    click_control(r'^Comparison profile coverage', '.sheet')
    text = read("document.querySelector('.sheet').innerText")
    probe.check('all six role targets are visibly met', len(re.findall(r'Target deficit: 0', text)) == 6, text[-3000:])
    probe.check('comparison scope stays separate from mission qualification', 'does not establish installed compatibility' in text)
    probe.snapshot('all-role-coverage-targets')
    reference = next(item for item in CATALOG['products'] if item.get('catalogUse') == 'reference-only' and 'battery' in item['roles'])
    product('battery', reference['id'], 'BK-3MCCE')
    probe.check('published BIRDS assembly stays a non-selectable nominal reference', read("document.querySelector('.allocation-controls .button.primary').disabled") and reference['specs']['energyWh']['meaning'] == 'nominal')
    close_context()


def battery_flow():
    load_example()
    ids = ['saft-mp144350xlr-cell', 'saft-mp174865xlr-cell', 'saft-mp176065xlr-cell']
    for product_id in ids:
        candidate = next(item for item in CATALOG['products'] if item['id'] == product_id)
        query = candidate['name'].split(' rechargeable')[0]
        product('battery', product_id, query)
        ratio = read("document.querySelector('[data-testid=\"comparison-coverage\"] h3').innerText")
        match = re.search(r'(\d+)/(\d+)', ratio)
        probe.check(product_id + ' exposes its complete comparison profile', bool(match) and match[1] == match[2], ratio)
        probe.check(product_id + ' retains richer characterization gaps', read("document.querySelector('[data-testid=\"comparison-coverage\"]').innerText.includes('Richer characterization gaps')"))
        apply_product('battery')
        recalculate()
        exported, _ = export_design(product_id)
        energy = candidate['specs']['energyWh']['value']
        basis = next(record for record in exported['provenance'] if record['parameter'] == 'battery.capacityWh')
        entry = next(item for item in exported['selectedCatalogEntries'] if item['id'] == product_id)
        probe.check(product_id + ' transfers its actual sourced nominal energy', exported['inputs']['battery']['capacityWh'] == energy and basis['kind'] == 'catalog-value' and basis['productId'] == product_id)
        probe.check(product_id + ' keeps rating meaning and source identities', entry['specs']['energyWh']['meaning'] == 'nominal' and all(source.get('publisher') and re.fullmatch(r'[a-fA-F0-9]{64}', source.get('sha256', '')) for source in entry['sources']))
        probe.check(product_id + ' evaluates the declared energy-only case', states()['simulation'] == 'complete' and math.isclose(exported['analysis']['simulation']['capacityWh'], energy * exported['inputs']['battery']['retainedEnergy']))
        probe.check(product_id + ' does not manufacture aging or efficiency facts', entry['specs']['retainedEnergyFraction']['status'] == 'missing' and entry['specs']['chargeEfficiency']['status'] == 'missing' and entry['specs']['dischargeEfficiency']['status'] == 'missing')
        probe.check(product_id + ' keeps scenario retention labeled as an assumption', next(record for record in exported['provenance'] if record['parameter'] == 'battery.retainedEnergy')['kind'] == 'engineering-assumption')
        load_example()


def role_flow():
    load_example()
    processor = 'pololu-astar-32u4-micro-3101'
    software = 'kubos-gomspace-p31u-api'
    product('processor', processor, 'A-Star')
    apply_product('processor')
    probe.check('standalone processor has an exact applicable role suggestion', authored()['selections']['processor'] == processor)
    probe.check('processor choice preserves the separately allocated EPS assembly', authored()['selections']['conditioning'] == authored()['selections']['distribution'] == BOARD)
    close_context()
    probe.check('processor allocation leaves affected energy results stale', states()['simulation'] != 'complete')
    product('software', software, 'P31U')
    apply_product('software')
    probe.check('genuine external EPS API can be allocated in its exact software role', authored()['selections']['software'] == software)
    scope_text = read("document.querySelector('.sheet').innerText").lower()
    probe.check('software declares its external Linux scope and unassessed integration', 'external' in scope_text and 'linux' in scope_text and 'unassessed' in scope_text)
    probe.snapshot('sourced-software-allocation')
    close_context()
    probe.check('software allocation does not pretend to execute flight software', states()['simulation'] != 'complete' and states()['assessment'] != 'complete')
    load_example()


phase = os.environ.get('EPS_CATALOG_PHASE', 'all')
flows = {'coverage': coverage_flow, 'battery': battery_flow, 'roles': role_flow}
if phase not in {*flows, 'all'}:
    raise ValueError('Unknown catalog phase: ' + phase)
phase_results = []
for name, flow in flows.items():
    if phase in {name, 'all'}:
        result = {'phase': name, 'status': 'running', 'firstCheck': len(probe.journal)}
        phase_results.append(result)
        probe.save('phases.json', phase_results)
        try:
            flow()
        except BaseException as error:
            result.update(status='failed', error=str(error), checks=len(probe.journal)-result['firstCheck'])
            probe.save('phases.json', phase_results)
            raise
        result.update(status='passed', checks=len(probe.journal)-result['firstCheck'])
        probe.save('phases.json', phase_results)
assert_no_overflow('final enriched catalog canvas')
diagnostics = read('window.__orbitworkProbeDiagnostics')
probe.check('enriched catalog has no console errors or unhandled exceptions', not diagnostics['errors'] and not [item for item in diagnostics['console'] if item['level'] == 'error'], diagnostics)
probe.snapshot('catalog-enrichment-finished-' + phase)
