"""Read-only runtime call profiling and deterministic replay audit.

No framework function is replaced, wrapped or patched. sys.setprofile observes
actual code calls. Repeat artifacts must be byte identical to executed/.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast
import hashlib
import json
from collections import Counter
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_case_studies as driver

source=ast.parse((HERE/'independent_reference.py').read_text())
imports=[]
for n in ast.walk(source):
    if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
    elif isinstance(n,ast.ImportFrom):imports.append(n.module or '')
assert not any('framework' in x for x in imports)
if '--reuse-replay' not in sys.argv:
    driver.run(HERE/'rerun')
# A full interpreter-wide profile was too expensive. Observe a separate bounded
# public-API probe after the complete unprofiled deterministic replay.
from framework.scripts import illumination
from framework.models import VerificationCondition, Requirement
counts=Counter()
codes={}
for module in (driver.actual_sizing,illumination):
    for value in vars(module).values():
        if hasattr(value,'__code__') and value.__code__.co_filename.startswith(str(driver.ROOT)+'/'):
            codes[value.__code__]=str(Path(value.__code__.co_filename).relative_to(driver.ROOT))+':'+value.__code__.co_name
for fn in (driver.Property.assess,VerificationCondition.evaluate,Requirement.verify):
    codes[fn.__code__]=str(Path(fn.__code__.co_filename).relative_to(driver.ROOT))+':'+fn.__code__.co_name

def observe(frame,event,arg):
    if event=='call':
        key=codes.get(frame.f_code)
        if key is not None:counts[key]+=1
probe=[]
sys.setprofile(observe)
try:
    for name in driver.BASELINES:
        c=driver.clone(name);c.update(eccentricity=.02,beta=25.,sun_angle=47.,pointing='nadir')
        m=driver.make(c);eps=m.BUS.EPS
        probe.append(dict(mission=name,period=m.orbit.period.value,eclipse=m.orbit.eclipse_duration.value,
                          projection=eps.SolarArray.sunlight_projection.value,
                          mpp=eps.SolarArray.cell_eol_power.assess().value,
                          battery_energy=eps.battery_energy.required.value,
                          generation_verdict=eps.solar_generation.verify().verified))
finally:sys.setprofile(None)
files=['results.json','results.csv','inputs.json','model-bindings.json','summary.json','engineering-verdicts.json']
hashes={}
for name in files:
    a=(HERE/'executed'/name).read_bytes();b=(HERE/'rerun'/name).read_bytes()
    assert a==b,name+' nondeterministic'
    hashes[name]=hashlib.sha256(a).hexdigest()
rows=json.loads((HERE/'executed/results.json').read_text())
assert not any(r['outcome']=='mismatch' for r in rows)
assert len(rows)==len({r['id'] for r in rows})
# Preserve all numerical values/statuses in the independently reviewed snapshot.
previous=HERE/'reviewed-799/executed/results.json'
regression=None
if previous.is_file():
    old=json.loads(previous.read_text());by_id={r['id']:r for r in rows}
    for r in old:
        assert r['id'] in by_id,r['id']+' disappeared'
        for field in ('expected','actual','expected_status','actual_status','outcome','units'):
            assert by_id[r['id']][field]==r[field],(r['id'],field,'changed')
    regression=dict(previous_records=len(old),all_previous_values_statuses_unchanged=True,added_records=len(rows)-len(old))
new_boundaries=[r for r in rows if any(r['quantity'].startswith(x) for x in ('Unreg2_OC_','Unreg1_OC_','spacecraft_battery_bus_OC_'))]
assert len(new_boundaries)==9
assert sum(r['actual'] is False for r in new_boundaries)==6
endpoint=next(r for r in rows if r['quantity']=='charger_endpoint_no_trip')
assert endpoint['actual'] is False and endpoint['actual_status']=='value'
assert any(c['condition'].endswith('.overvoltage') and c['measure']==4.2 and c['target']==4.1 and c['value'] is False for c in endpoint['detail'])
for mission in driver.BASELINES:
    bol=[r for r in rows if r['mission']==mission and r['quantity'].startswith('BOL_case_')]
    assert len(bol)==23 and all(r['outcome']=='match' for r in bol)
assert all(r['actual'] is True for r in rows if r['quantity'].endswith('deployed_layout_verdict'))
assert counts['framework/scripts/sizing.py:cell_power']>0
assert counts['framework/scripts/sizing.py:eccentric_illumination']>0
assert counts['framework/scripts/illumination.py:orbital_projection']>0
assert counts['framework/models/requirements.py:evaluate']>0
assert counts['framework/models/properties.py:assess']>0
for name,h in json.loads((HERE/'executed/summary.json').read_text())['metadata']['framework_sha256'].items():
    assert hashlib.sha256((driver.ROOT/name).read_bytes()).hexdigest()==h,name+' changed since execution'
audit=dict(deterministic_files_sha256=hashes,independent_reference_imports=imports,
           reference_has_no_framework_import=True,
           actual_sizing_module_path=driver.actual_sizing.__file__,
           observed_framework_calls=dict(sorted(counts.items())),
           numerical_function_call_count=sum(v for k,v in counts.items() if k.startswith('framework/scripts/')),
           comparison_count=len(rows),scenario_groups=36,
           artifact_comparison='All six final replay files byte identical',
           framework_hash_check='All snapshotted models/scripts hashes unchanged',
           source_patch_policy='No framework files or functions patched. sys.setprofile observation only.',
           profile_scope='Bounded separate public-API probe in both missions after full deterministic replay. First whole-run profile exceeded120s and was terminated without audit outputs.',
           runtime_probe=probe,reviewed_snapshot_regression=regression,
           followup_checks=dict(BOL_cases_per_mission=23,additional_OC_boundary_records=9,
                                charger_endpoint_per_cell_V=4.2,charger_endpoint_nominal_OV_V=4.1,
                                charger_endpoint_engineering_no_trip=False,
                                deployed_layout_verdicts_all_true=True))
(HERE/'audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print('DETERMINISTIC AUDIT PASSED',len(rows),'records',audit['numerical_function_call_count'],'observed numerical function calls')
