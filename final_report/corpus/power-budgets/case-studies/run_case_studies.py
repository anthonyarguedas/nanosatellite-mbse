#!/usr/bin/env python3
"""Execute unchanged public framework Properties, Requirements and functions.

Run from any directory with PYTHONDONTWRITEBYTECODE=1. All outputs stay here
unless --output is explicitly supplied. The independent module never imports
framework code. Custom expressions and requirements are labelled as authored.
"""
import sys
sys.dont_write_bytecode = True
import argparse
from pathlib import Path
import copy
import csv
import hashlib
import json
import math
import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent


def repository_root():
    """Explicit CLI/environment selection, then bundle/cwd ancestor discovery."""
    bootstrap=argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument('--framework-root',type=Path)
    options,_=bootstrap.parse_known_args()
    explicit=options.framework_root or os.environ.get('EPS_FRAMEWORK_ROOT')
    if explicit:
        candidates=[Path(explicit).expanduser().resolve()]
    else:
        cwd=Path.cwd().resolve()
        candidates=[HERE,*HERE.parents,cwd,*cwd.parents]
    for root in candidates:
        if (root/'framework/models/eps.py').is_file() and (root/'framework/scripts/sizing.py').is_file():
            return root
    raise RuntimeError('Set EPS_FRAMEWORK_ROOT or --framework-root to the repository containing framework/models/eps.py.')


ROOT = repository_root()
sys.path.insert(0, str(ROOT))
from framework.models import (Mission, CubeSatBus, Property, Component, ComponentMode,
                             SpacecraftMode, StateAllocation, VerificationCondition,
                             CotsBattery, Battery, Protection, Pointing, Face, TransferMethod)
from framework.scripts import sizing as actual_sizing
import independent_reference as ref
from case_inputs import BASELINES, SOURCES, SI, LI, LFP, FOUR_CELL_DEPLOYMENT, clone

ROWS=[]
CONFIGS={}
BINDINGS={}
CONVERGENCE=[]
ENGINEERING=[]
REFERENCE_CHECKS=[]
MOP_ORDER=['12','14a','14b','15','16','17','18','19','20']


def clean(x):
    if hasattr(x,'value') and not isinstance(x,Property):
        return clean(x.value)
    if isinstance(x,dict):
        return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):
        return [clean(v) for v in x]
    if isinstance(x,float) and not math.isfinite(x):
        return repr(x)
    return x


def save_config(key,c,m):
    CONFIGS[key]=copy.deepcopy(c)
    BINDINGS[key]={o.path:{n:{'expression':p.expression,'unit':str(p.unit)}
                         for n,p in o.properties.items()} for o in m.walk() if o.properties}


def add_row(mission,scenario,mop,quantity,unit,expected,actual,rule,provider,
            status='value',expected_status='value',basis='independent',source='A',detail=None):
    error=None
    if status != expected_status:
        ok=False
    elif expected_status in ('pending','error'):
        ok=True
    elif rule=='numeric':
        if expected==0:
            ok=(actual==0)
        else:
            try:
                error=abs(actual-expected)/abs(expected)
                ok=math.isfinite(error) and error <= .01
            except (TypeError,ValueError):
                ok=False
    else:
        ok=(clean(actual)==clean(expected) and (type(actual) is type(expected) or rule=='structure'))
    # Invalid-domain cases expect ValueError specifically. A driver binding
    # AttributeError or another unrelated failure must never masquerade as a pass.
    error_messages=[]
    if status=='error':
        error_messages=([detail.get('message','')] if isinstance(detail,dict) else
                        [x.get('message','') for x in (detail or []) if x.get('status')=='error'])
    if expected_status=='error':
        ok=ok and bool(error_messages) and all(x.startswith('ValueError:') for x in error_messages)
    outcome='match' if ok else 'mismatch'
    if ok and expected_status=='error': outcome='expected error'
    if ok and expected_status=='pending': outcome='expected unknown'
    ROWS.append(dict(id=f'{mission}:{scenario}:{mop}:{quantity}',mission=mission,mop='MOP-'+mop,
                     scenario=scenario,quantity=quantity,units=unit,reference_basis=basis,
                     source_locator_or_assumption=source,expected=clean(expected),actual=clean(actual),
                     relative_error=error,comparison_rule='1% per nonzero value, exact zero' if rule=='numeric' else rule,
                     expected_status=expected_status,actual_status=status,
                     expected_error_type='ValueError' if expected_status=='error' else None,
                     actual_error_types=sorted({x.split(':',1)[0] for x in error_messages}),outcome=outcome,
                     actual_provider=provider,detail=clean(detail or {})))


def pcheck(c,s,mop,label,p,expected,rule='numeric',basis='independent',source='A',expected_status='value',mode=None):
    r=p.assess(mode=mode)
    add_row(c['mission'],s,mop,label,str(p.unit),expected,r.value,rule,
            dict(kind='public Property',path=p.reference,expression=p.expression,mode=getattr(mode,'path',None)),
            r.status.value,expected_status,basis,source,{'message':r.message})


def direct(c,s,mop,label,fn,kwargs,field,expected,unit='',expected_status='value',source='A'):
    try:
        result=fn(**kwargs)
        actual=getattr(result,field) if field else result
        status='value'; message=''
    except Exception as e:
        actual=None;status='error';message=f'{type(e).__name__}: {e}'
    add_row(c['mission'],s,mop,label,unit,expected,actual,'numeric' if expected_status=='value' else 'exact',
            dict(kind='direct public numerical function',function=fn.__module__+'.'+fn.__name__,inputs=clean(kwargs),field=field),
            status,expected_status,'independent',source,{'message':message})


def rcheck(c,s,mop,label,r,expected,status='value',mode=None):
    report=r.verify(mode=mode)
    details=[dict(condition=x.condition.path,status=x.status.value,value=x.value,measure=clean(x.measure),
                  target=clean(x.target),message=x.message,predicate=x.condition.expression,
                  dependency_paths=[[p.reference for p in path] for path in x.paths]) for x in report.results]
    add_row(c['mission'],s,mop,label,'verdict',expected,report.verified,'exact',
            dict(kind='public Requirement.verify',path=r.path,mode=getattr(mode,'path',None)),
            report.status.value,status,'independent predicate','A; linked measures and limits',details)
    ENGINEERING.append(dict(mission=c['mission'],scenario=s,mop='MOP-'+mop,check=label,
                            verdict=report.verified,status=report.status.value,
                            expected=expected,configuration_correctness=ROWS[-1]['outcome']))


def make(c,method='MPPT',bus_voltage=None,setpoint=None,interpolation='linear'):
    m=Mission(lifetime=c['lifetime'],days_per_year=c['days_per_year'])
    o=m.orbit
    for key,value in [('altitude',c['altitude']),('eccentricity',c['eccentricity']),
                      ('beta_angle',c['beta']),('sun_projection_angle',c['sun_angle']),
                      ('earth_radius',c['earth_radius']),('gravitational_parameter',c['mu'])]:
        setattr(o,key,value)
    bus=m.add(CubeSatBus('BUS',units=c['units']))
    adcs=bus.AttitudeDeterminationAndControl
    adcs.pointing=Pointing.SUN_POINTING if c['pointing']=='sun_pointing' else Pointing.NADIR
    adcs.pointing_face=Face.POS_Z if c['pointing']=='sun_pointing' else Face.NEG_Z
    adcs.clocking_angle=0
    eps=bus.EPS; a=c['array']; b=c['battery']; panel=eps.SolarArray; bat=eps.Battery
    for target,key in [('series_count','series'),('parallel_count','parallel'),('cell_eol_voltage','vmp'),
                       ('cell_eol_current','imp'),('cell_open_circuit_voltage','voc'),('cell_short_circuit_current','isc'),
                       ('cell_active_area','area'),('packing_fraction','packing'),('usable_area','usable'),
                       ('pv_reference_irradiance','reference_irradiance')]:
        setattr(panel,target,a[key])
    points=((0.,a['isc']),(a['vmp'],a['imp']),(a['voc'],0.))
    panel.cell_iv_curve=repr(points if a['curve'] else ())
    # The selected curve carries its declared BOL or EOL condition. These
    # factors expose a scalar comparison and are not applied to the curve twice.
    panel.bol_efficiency=ref.quotient(ref.product(a['bol_vmp'],a['bol_imp']),ref.product(a['area'],a['reference_irradiance']))
    panel.lifetime_retention=ref.quotient(ref.product(a['vmp'],a['imp']),ref.product(a['bol_vmp'],a['bol_imp']))
    panel.temperature_factor=1
    panel.irradiance=c['irradiance'];panel.inherent_retention=c['inherent'];panel.assembly_efficiency=c['assembly']
    panel.mounting_face=Face.POS_Z
    panel.sunlight_path_efficiency=c['sun_path'];panel.eclipse_path_efficiency=c['eclipse_path']
    panel.iv_interpolation=repr(interpolation)
    panel.define('assessment_age',Property(repr(c.get('solar_age','EOL'))))
    if 'deployment' in c:
        d=c['deployment']
        for key,value in d.items():
            if key=='source':continue
            unit='m2' if key.endswith('_m2') else 'm' if key.endswith('_m') else 'count'
            panel.define('layout_'+key,Property(value,unit))
        panel.define('layout_width',Property('self.layout_columns.value*(self.layout_package_width_m.value+self.layout_package_dimension_tolerance_m.value)+(self.layout_columns.value-1)*self.layout_gap_m.value+2*self.layout_edge_clearance_m.value','m'))
        panel.define('layout_length',Property('self.layout_rows.value*(self.layout_package_length_m.value+self.layout_package_dimension_tolerance_m.value)+(self.layout_rows.value-1)*self.layout_gap_m.value+2*self.layout_edge_clearance_m.value','m'))
        panel.define('layout_footprint',Property('self.layout_width.value*self.layout_length.value','m2'))
        panel.define('deployed_plate_area',Property('self.layout_plate_width_m.value*self.layout_plate_length_m.value','m2'))
        eps.add_requirement('array_deployment_layout',rationale='Supplied rectangular grid and clearances on an explicit deployed plate. No mechanical qualification.',conditions=(
            VerificationCondition('count',panel.cell_count,Property('self.parent.context.SolarArray.layout_columns.value*self.parent.context.SolarArray.layout_rows.value','cell'),'type(measure) is int and measure == target'),
            VerificationCondition('width',panel.layout_width,panel.layout_plate_width_m,'0 < measure <= target'),
            VerificationCondition('length',panel.layout_length,panel.layout_plate_length_m,'0 < measure <= target'),
            VerificationCondition('usable',panel.layout_usable_area_m2,panel.deployed_plate_area,'0 < measure <= target'),
            VerificationCondition('footprint',panel.layout_footprint,panel.layout_usable_area_m2,'0 < measure <= target'),
            VerificationCondition('packing_estimate',panel.layout_footprint,panel.panel_area,'0 < measure <= target')))
    paths={ 'MPPT':eps.RegulatorAndConverter, 'FIXED_VOLTAGE':eps.RegulatorAndConverter,'DET':eps.PowerCircuit}
    path=paths.get(method,eps.PowerCircuit)
    panel.power_path=path.path
    path.transfer_method=repr(method)
    path.bus_voltage=bat.nominal_voltage if bus_voltage is None else bus_voltage
    path.voltage_drop=.2
    path.input_voltage_setpoint=ref.product(a['series'],a['vmp']) if setpoint is None else setpoint
    if 'efficiency' not in path.properties:
        path.define('efficiency',Property(c['converter_efficiency'],'1'))
    else: path.efficiency=c['converter_efficiency']
    panel.define('bus_power',Property(
        'self.power_path.value.bus_voltage.value * self.operating_current.value * '
        'self.available_power.value / self.operating_power.value if '
        "self.power_path.value.selected_transfer_method.value == 'DET' else "
        'self.power_path.value.efficiency.value * self.available_power.value','W'))
    for pack in [bat]+([eps.add(Battery('IndependentPackB'))] if b['independent_packs']==2 else []):
        for target,key in [('series_count','series'),('parallel_count','parallel'),('cell_nominal_voltage','nominal'),
                           ('cell_minimum_voltage','minimum'),('cell_maximum_voltage','maximum'),
                           ('cell_rated_capacity','cell_ah'),('cell_rated_energy','cell_wh'),
                           ('cell_maximum_charge_current','charge_limit'),('cell_maximum_discharge_current','discharge_limit'),
                           ('cycle_coefficient','fit_a'),('cycle_exponent','fit_b'),('fit_dod_min','fit_min'),('fit_dod_max','fit_max'),
                           ('degradation_margin','margin'),('energy_retention','energy_retention'),('capacity_retention','capacity_retention')]:
            setattr(pack,target,b[key])
    for pack in [bat]+([eps.IndependentPackB] if b['independent_packs']==2 else []):
        pack.define('cell_occupied_volume',Property(b['cell_volume_m3'],'m3'))
        pack.define('packaging_occupied_volume',Property(b['packaging_volume_m3'],'m3'))
        pack.volume='self.cell_count.value*self.cell_occupied_volume.value+self.packaging_occupied_volume.value'
    eps.define('storage_volume',Property('self.Battery.volume.value+self.IndependentPackB.volume.value' if b['independent_packs']==2 else 'self.Battery.volume','m3'))
    eps.add_requirement('battery_installation',conditions=(VerificationCondition('volume',eps.storage_volume,Property(c['battery_usable_volume_m3'],'m3'),'0 <= measure <= target'),),rationale='Supplied occupied envelopes and allocation, scalar volume screen only')
    if b['independent_packs']==2:
        eps.define('independent_storage_energy',Property('self.Battery.rated_energy.value+self.IndependentPackB.rated_energy.value','Wh'))
        eps.define('independent_storage_capacity_bookkeeping',Property('self.Battery.rated_capacity.value+self.IndependentPackB.rated_capacity.value','Ah'))
    smodes={}
    for phase in ('sunlight','eclipse'):
        smodes[phase]=bus.add(SpacecraftMode(phase+'_mode'))
        smodes[phase].allocation.fraction=.6 if phase=='sunlight' else .4  # explicit, unused in energy equations
    for x in c['loads']['states']:
        load=bus.Payload.add(Component(x['name']))
        for phase,dkey in [('sunlight','sun_duty'),('eclipse','eclipse_duty')]:
            cm=load.add(ComponentMode(phase))
            cm.on.voltage=x['voltage'];cm.on.current=x['current']
            cm.off.voltage=0;cm.off.current=0
            cm.add(StateAllocation('on_share',cm.on,x[dkey]))
            cm.add(StateAllocation('off_share',cm.off,1-x[dkey]))
            expr=f'self.{phase}.on.power.value*self.{phase}.on_share.fraction.value+self.{phase}.off.power.value*self.{phase}.off_share.fraction.value'
            load.define(phase+'_mean',Property(expr,'W'))
            load.power.bind(smodes[phase],expr)
    for phase in ('sunlight','eclipse'):
        getattr(eps,phase+'_energy').average_power=Property(
            f'sum(c.{phase}_mean.value for c in self.context.parent.Payload.components)','W')
    eps.available_sunlight_energy=c['available_sunlight'];eps.available_eclipse_energy=c['available_eclipse']
    eps.RegulatorAndConverter.power=0;eps.PowerCircuit.power=0
    eps.solar_voltage.minimum_allowed=c['tracker_min'];eps.solar_voltage.maximum_allowed=c['tracker_max']
    eps.solar_open_circuit_voltage.required=c['absolute_max'];eps.solar_short_circuit_current.required=c['source_current_limit']
    eps.battery_voltage.minimum_allowed=c['battery_receiving_min'];eps.battery_voltage.maximum_allowed=c['battery_receiving_max']
    eps.battery_charge_current.required=c['required_charge'];eps.battery_discharge_current.required=c['required_discharge']
    conv=eps.RegulatorAndConverter
    conv.minimum_input_voltage=c['converter_in_min'];conv.maximum_input_voltage=c['converter_in_max']
    conv.maximum_output_current=c['converter_current'];conv.output_voltage=3.3;conv.efficiency=c['converter_efficiency']
    eps.bus_voltage.available=conv.output_voltage;eps.bus_voltage.required=3.3;eps.bus_voltage.tolerance=c['bus_tolerance']
    eps.bus_current.available=conv.maximum_output_current;eps.bus_current.required=.5
    ch=c['charger']
    for name in ('chemistry','series','set_voltage','allowed_min','allowed_max','current','current_limit','termination','required_termination'):
        value=ch[name]
        eps.define('charger_'+name,Property(repr(value) if isinstance(value,str) else value))
    bat.define('chemistry',Property(repr(b['chemistry'])))
    charger_conditions=(
        VerificationCondition('chemistry',eps.charger_chemistry,bat.chemistry,'measure == target'),
        VerificationCondition('series',eps.charger_series,bat.series_count,'type(measure) is int and measure == target'),
        VerificationCondition('voltage',eps.charger_set_voltage,Property('(self.parent.context.charger_allowed_min.value,self.parent.context.charger_allowed_max.value)','V'),'target[0] <= measure <= target[1]'),
        VerificationCondition('current',eps.charger_current,Property('min(self.parent.context.charger_current_limit.value,self.parent.context.Battery.maximum_charge_current.value)','A'),'0 <= measure <= target'),
        VerificationCondition('termination',eps.charger_termination,eps.charger_required_termination,'measure == target'))
    eps.add_requirement('charger_compatibility',rationale='Supplied product-specific compatibility conditions. No charger dynamics.',conditions=charger_conditions)
    return m


def geometry(c,s,m):
    o=m.orbit;p=m.BUS.EPS.SolarArray
    a=c['earth_radius']+c['altitude'];l=c['sun_angle'] if c['eccentricity'] else 0.
    args=(a,c['eccentricity'],c['earth_radius'],c['mu'],c['beta'],l,c['pointing'])
    coarse=ref.orbit(*args,131072);fine=ref.orbit(*args,262144)
    CONVERGENCE.append(dict(mission=c['mission'],scenario=s,coarse=coarse,fine=fine,
                            eclipse_relative_change=abs(fine['eclipse']-coarse['eclipse'])/fine['eclipse'] if fine['eclipse'] else 0,
                            projection_relative_change=abs(fine['projection']-coarse['projection'])/fine['projection'] if fine['projection'] else 0))
    for label,prop,expected in [('period',o.period,fine['period']),('sunlight',o.sunlight_duration,fine['sunlight']),
                                ('eclipse',o.eclipse_duration,fine['eclipse']),('projection',p.sunlight_projection,fine['projection']),
                                ('projected_duration',p.projected_sunlight_duration,fine['projected_duration'])]:
        pcheck(c,s,'14a' if label in ('period','sunlight','eclipse') else '14b',label,prop,expected,source='Independent uniform-time Cartesian orbit, N262144, declared geometry')
    return fine


def reference_count_stability(c,s,orb,r):
    coarse=ref.orbit(c['earth_radius']+c['altitude'],c['eccentricity'],c['earth_radius'],c['mu'],c['beta'],
                     c['sun_angle'] if c['eccentricity'] else 0.,c['pointing'],131072)
    rc=ref.sizing(c,coarse)
    names=('required_count','minimum_solar_parallel','minimum_battery_parallel')
    record=dict(mission=c['mission'],scenario=s,age=c.get('solar_age','EOL'),
                fine_counts={k:r[k] for k in names},coarse_counts={k:rc[k] for k in names})
    record['stable']=record['fine_counts']==record['coarse_counts']
    REFERENCE_CHECKS.append(record)
    assert record['stable'],f'Independent count bound changes with grid refinement: {record}'


def configure_four_cell_deployment(c):
    c['array'].update(series=4,parallel=1,usable=.016)
    c['deployment']=copy.deepcopy(FOUR_CELL_DEPLOYMENT[c['mission']])


def deployment_checks(c,s,m,mop,prefix=''):
    d=c['deployment'];r=ref.rectangular_layout(d);p=m.BUS.EPS.SolarArray
    for label,prop,expected in [('width',p.layout_width,r['width']),('length',p.layout_length,r['length']),
                                ('footprint',p.layout_footprint,r['footprint']),('plate_area',p.deployed_plate_area,r['plate_area'])]:
        pcheck(c,s,mop,prefix+'deployed_'+label,prop,expected,source=d['source'])
    panel_area=ref.quotient(ref.product(c['array']['series'],c['array']['parallel'],c['array']['area']),c['array']['packing'])
    expected=(d['columns']*d['rows']==c['array']['series']*c['array']['parallel'] and
              0<r['width']<=d['plate_width_m'] and 0<r['length']<=d['plate_length_m'] and
              0<r['footprint']<=d['usable_area_m2']<=r['plate_area'] and r['footprint']<=panel_area)
    rcheck(c,s,mop,prefix+'deployed_layout_verdict',m.BUS.EPS.array_deployment_layout,bool(expected))


def bol_solar_checks(c):
    s='05-baseline-sizing';v=copy.deepcopy(c);v['solar_age']='BOL'
    a=v['array']
    a.update(vmp=a['bol_vmp'],imp=a['bol_imp'],voc=a['bol_voc'],isc=a['bol_isc'],
             retention_kind='BOL anchors, no solar lifetime reduction')
    m=make(v);eps=m.BUS.EPS;p=eps.SolarArray
    orb=ref.orbit(v['earth_radius']+v['altitude'],v['eccentricity'],v['earth_radius'],v['mu'],v['beta'],
                  v['sun_angle'] if v['eccentricity'] else 0.,v['pointing'])
    r=ref.sizing(v,orb)
    reference_count_stability(v,s+':BOL',orb,r)
    pairs=[('minimum_panel_power',eps.solar_power.required,'required_power'),
           ('fractional_count',eps.solar_cell_count.fractional_count,'fractional_count'),
           ('required_count',eps.solar_cell_count.required,'required_count'),
           ('minimum_solar_parallel',eps.solar_cell_count.minimum_parallel_count,'minimum_solar_parallel'),
           ('cell_power',p.cell_eol_power,'cell_power'),('array_mpp',p.eol_power,'array_mpp'),
           ('array_voltage',p.eol_voltage,'array_voltage'),('array_current',p.eol_current,'array_current'),
           ('array_voc',p.open_circuit_voltage,'array_voc'),('array_isc',p.short_circuit_current,'array_isc'),
           ('generation_efficiency',p.generation_efficiency,'generation_efficiency'),
           ('active_area',p.active_area,'active_area'),('panel_area',p.panel_area,'panel_area'),
           ('required_area',eps.solar_area.required,'required_area'),('effective_area',eps.solar_area.effective_area,'effective_area'),
           ('density',p.eol_power_density,'density'),('available_power',p.available_power,'available_power'),('source_energy',p.source_energy,'source_energy')]
    for label,prop,key in pairs:
        pcheck(v,s,'14b','BOL_case_'+label,prop,r[key],rule='exact' if key in ('required_count','minimum_solar_parallel') else 'numeric',
               source=a['source']+' documented BOL anchors; all mission/load/geometry inputs fixed to baseline')
    for label,req,expected in [('solar_power',eps.solar_power,r['array_mpp']>=r['required_power']),
                               ('solar_count',eps.solar_cell_count,2>=r['required_count']),
                               ('area_fit',eps.solar_area_fit,r['panel_area']<=a['usable']),
                               ('active_area',eps.solar_area,r['active_area']>=r['required_area']),
                               ('generation',eps.solar_generation,r['available_power']>=r['required_power'])]:
        rcheck(v,s,'14b','BOL_case_'+label+'_verdict',req,bool(expected))
    save_config(c['mission']+':'+s+':BOL',v,m)


def sizing_checks(c,s,m,mop='14b'):
    a=c['array'];b=c['battery']; eps=m.BUS.EPS; p=eps.SolarArray;bat=eps.Battery
    orb=ref.orbit(c['earth_radius']+c['altitude'],c['eccentricity'],c['earth_radius'],c['mu'],c['beta'],
                  c['sun_angle'] if c['eccentricity'] else 0.,c['pointing'])
    r=ref.sizing(c,orb)
    reference_count_stability(c,s,orb,r)
    pairs=[('cell_power',p.cell_eol_power,'W'),('array_mpp',p.eol_power,'W'),('array_voltage',p.eol_voltage,'V'),
           ('array_current',p.eol_current,'A'),('array_voc',p.open_circuit_voltage,'V'),('array_isc',p.short_circuit_current,'A'),
           ('active_area',p.active_area,'m2'),('panel_area',p.panel_area,'m2'),('required_area',eps.solar_area.required,'m2'),
           ('effective_area',eps.solar_area.effective_area,'m2'),('tumbling_area',eps.solar_area.tumbling_panel_area,'m2'),
           ('generation_efficiency',p.generation_efficiency,'1'),('density',p.eol_power_density,'W/m2'),
           ('available_power',p.available_power,'W'),('source_energy',p.source_energy,'J'),
           ('fractional_count',eps.solar_cell_count.fractional_count,'cell'),('required_count',eps.solar_cell_count.required,'cell'),
           ('minimum_solar_parallel',eps.solar_cell_count.minimum_parallel_count,'string'),
           ('cycles',eps.battery_energy.required_cycles,'cycle'),('dod',eps.battery_energy.maximum_dod,'1'),
           ('required_battery_energy',eps.battery_energy.required,'J'),('minimum_battery_parallel',eps.battery_energy.minimum_parallel_count,'string'),
           ('pack_wh',bat.rated_energy,'Wh'),('pack_ah',bat.rated_capacity,'Ah'),('pack_j',bat.bol_energy,'J'),
           ('eol_j',bat.eol_energy,'J'),('eol_ah',bat.eol_capacity,'Ah'),('battery_voltage',bat.nominal_voltage,'V'),
           ('battery_min',bat.minimum_voltage,'V'),('battery_max',bat.maximum_voltage,'V'),
           ('charge_limit',bat.maximum_charge_current,'A'),('discharge_limit',bat.maximum_discharge_current,'A')]
    for label,prop,_ in pairs:
        pcheck(c,s,mop,label,prop,r[label],rule='exact' if 'parallel' in label or label=='required_count' else 'numeric',source=a['source']+'; '+b['source']+'; A for supplementary inputs')
    for label,req,expected in [
        ('solar_power',eps.solar_power,r['array_mpp']>=r['required_power']),
        ('solar_count',eps.solar_cell_count,a['series']*a['parallel']>=r['required_count']),
        ('battery_energy',eps.battery_energy,r['pack_j']>=r['required_battery_energy']),
        ('solar_configuration',eps.solar_configuration,True),('battery_configuration',eps.battery_configuration,True),
        ('area_fit',eps.solar_area_fit,r['panel_area']<=a['usable']),
        ('active_area',eps.solar_area,r['active_area']>=r['required_area']),
        ('generation',eps.solar_generation,r['available_power']>=r['required_power']),
        ('tracking_voltage',eps.solar_voltage,c['tracker_min']<=r['array_voltage']<=c['tracker_max']),
        ('absolute_voltage',eps.solar_open_circuit_voltage,r['array_voc']<=c['absolute_max']),
        ('source_current',eps.solar_short_circuit_current,r['array_isc']<=c['source_current_limit']),
        ('battery_receiving',eps.battery_voltage,c['battery_receiving_min']<=r['battery_min']<=r['battery_max']<=c['battery_receiving_max']),
        ('charge_current',eps.battery_charge_current,r['charge_limit']>=c['required_charge']),
        ('discharge_current',eps.battery_discharge_current,r['discharge_limit']>=c['required_discharge'])]:
        rcheck(c,s,mop,label+'_verdict',req,bool(expected))
    volume=ref.product(b['independent_packs'],ref.total([ref.product(b['series'],b['parallel'],b['cell_volume_m3']),b['packaging_volume_m3']]))
    pcheck(c,s,mop,'storage_occupied_volume',eps.storage_volume,volume,source='A per-cell occupied envelope, packaging allowance and storage allocation, no mechanical fit claim')
    rcheck(c,s,mop,'battery_installation_verdict',eps.battery_installation,volume<=c['battery_usable_volume_m3'])
    if b['independent_packs']==2:
        pcheck(c,s,mop,'independent_packs_energy',eps.independent_storage_energy,ref.product(r['pack_wh'],2),source='Two independent identical packs, energy sum only. Baseline O-pack card boundary. Alternative is a verification storage group.')
        pcheck(c,s,mop,'independent_packs_Ah_bookkeeping',eps.independent_storage_capacity_bookkeeping,ref.product(r['pack_ah'],2),source='Arithmetic bookkeeping, no direct parallel topology claim')
    return r


def mass_cases(name):
    c=clone(name);s='01-mass-boundaries';m=Mission();eps=m.add(CubeSatBus('BUS',units=1)).EPS
    isb=name=='BIRDS-4'
    masses=[.240,.018,.025,.017] if isb else [.416,.252,.035,.025]
    volumes=[.000080,.000006,.000020,.000015] if isb else [.000160,.000240,.000030,.000020]
    for comp,ma,vo in zip(eps.components,masses,volumes):comp.mass=ma;comp.volume=vo
    if isb:
        class Cell(CotsBattery):
            mass=Property(.027,'kg')
            volume=Property('math.pi*(.01435/2)**2*.0504','m3')
        for i in range(6):eps.Battery.add(Cell('cell'+str(i+1)))
        eps.Battery.mass='sum(c.mass.value for c in self.cots)'
        eps.Battery.volume='sum(c.volume.value for c in self.cots)'
        eps.Battery.define('source',Property(repr('B-cell Fig.1-1 p.21, cell-only')))
        pcheck(c,s,'12','published_cell_only_mass',eps.Battery.mass,.162,basis='published',source='B-cell Fig.1-1 p.21,27gx6=162g')
        pcheck(c,s,'12','cylindrical_cell_volume',eps.Battery.volume,6*math.pi*(.01435/2)**2*.0504,source='B-cell dimensions; independent ideal cylinder, excludes all packaging')
        pcheck(c,s,'12','cell_source',eps.Battery.source,'B-cell Fig.1-1 p.21, cell-only',rule='exact')
        eps.Battery.mass='sum(c.mass.value for c in self.cots)+.078'
        eps.Battery.volume=volumes[0]
    else:
        class Module(CotsBattery):mass=Property(.104,'kg')
        for i in range(4):eps.Battery.add(Module('historical_module'+str(i+1)))
        eps.Battery.mass='sum(c.mass.value for c in self.cots)'
        pcheck(c,s,'12','published_battery_module_mass',eps.Battery.mass,.416,basis='published',source='O-mass,2016fourmodules')
        eps.SolarArray.define('module_masses',Property(repr((.0315,)*8),'kg'))
        eps.SolarArray.mass='sum(self.module_masses.value)'
        pcheck(c,s,'12','published_solar_module_mass',eps.SolarArray.mass,.252,basis='published',source='O-mass,2016eightmodules')
        for prop_name,value in [('module_count',8),('module_width',.10),('module_length',.10),('module_height',.003)]:
            eps.SolarArray.define(prop_name,Property(value,'1' if prop_name=='module_count' else 'm'))
        eps.SolarArray.volume='self.module_count.value*self.module_width.value*self.module_length.value*self.module_height.value'
        pcheck(c,s,'12','assumed_solar_module_volume',eps.SolarArray.volume,ref.product(8,.10,.10,.003),
               source='A: eight 0.10 x 0.10 x 0.003 m occupied module envelopes, including boards and components')
    eps.define('mass_allocation',Property(.35 if isb else .8,'kg'))
    eps.define('volume_allocation',Property(.00015 if isb else .00050,'m3'))
    eps.define('mass_margin',Property('self.mass_allocation.value-self.mass.value','kg'))
    eps.define('volume_margin',Property('self.volume_allocation.value-self.volume.value','m3'))
    for q in ('mass','volume'):
        eps.add_requirement(q+'_allocation_check',conditions=(VerificationCondition('maximum',getattr(eps,q),getattr(eps,q+'_allocation'),'0 <= measure <= target'),),rationale='Supplied EPS-only allocation')
    for q,expected in [('mass',ref.total(masses)),('volume',ref.total(volumes)),('mass_margin',ref.total([.35 if isb else .8,-ref.total(masses)])),('volume_margin',ref.total([.00015 if isb else .00050,-ref.total(volumes)]))]:
        pcheck(c,s,'12',q,getattr(eps,q),expected)
    rcheck(c,s,'12','mass_allocation',eps.mass_allocation_check,True)
    rcheck(c,s,'12','volume_allocation',eps.volume_allocation_check,True)
    # Aggregate replaces child sum, children remain nested and never enter EPS sum independently.
    eps.Battery.mass=masses[0]
    eps.Battery.add(eps.Battery.cots[0])
    pcheck(c,s,'12','aggregate_replacement_no_double_count',eps.mass,ref.total(masses))
    eps.mass_allocation=ref.total(masses)
    rcheck(c,s,'12','zero_margin_passes',eps.mass_allocation_check,True)
    eps.mass_allocation=.1
    rcheck(c,s,'12','negative_margin_fails',eps.mass_allocation_check,False)
    eps.SolarArray.mass=None
    pcheck(c,s,'12','unknown_mass_total',eps.mass,None,expected_status='pending')
    pcheck(c,s,'12','unknown_mass_margin',eps.mass_margin,None,expected_status='pending')
    pcheck(c,s,'12','volume_unaffected_by_unknown_mass',eps.volume,ref.total(volumes))
    rcheck(c,s,'12','unknown_mass_allocation',eps.mass_allocation_check,None,status='pending')
    eps.SolarArray.volume=None
    pcheck(c,s,'12','unknown_volume_total',eps.volume,None,expected_status='pending')
    pcheck(c,s,'12','unknown_volume_margin',eps.volume_margin,None,expected_status='pending')
    rcheck(c,s,'12','unknown_volume_allocation',eps.volume_allocation_check,None,status='pending')
    pcheck(c,s,'12','mass_unit_record',eps.define('mass_unit_record',Property(repr(str(eps.mass.unit)))), 'kg',rule='exact')
    pcheck(c,s,'12','volume_unit_record',eps.define('volume_unit_record',Property(repr(str(eps.volume.unit)))), 'm3',rule='exact')
    save_config(name+':'+s,dict(mission=name,masses_kg=masses,volumes_m3=volumes,
                mass_allocation_initial_kg=.35 if isb else .8,volume_allocation_m3=.00015 if isb else .00050,
                assumed_solar_module_envelope_m=None if isb else [.10,.10,.003],
                solar_module_count=None if isb else 8,
                mass_allocation_variations=['exact total',.1],unknown=['SolarArray.mass','SolarArray.volume'],
                source='B-cell; all complete EPS masses/volumes A' if isb else 'O-mass historical2016; all volumes and converter/distribution masses A',
                BIRDS_pack_overhead_assumed_kg=.078 if isb else None),m)


def budget_cases(c):
    s='02-states-modes-circular';m=make(c);eps=m.BUS.EPS;orb=geometry(c,s,m);r=ref.sizing(c,orb)
    for x,power in zip(c['loads']['states'],r['state_powers']):
        comp=m.BUS.Payload.child(x['name'])
        pcheck(c,s,'14a',x['name']+'_state_power',comp.sunlight.on.power,power)
    for phase,key in [('sunlight','sun_power'),('eclipse','eclipse_power')]:
        pcheck(c,s,'14a',phase+'_mode_aggregation',m.BUS.Payload.power,r[key],mode=m.BUS.child(phase+'_mode'))
        pcheck(c,s,'14a',phase+'_EPS_consumption_boundary',eps.power,0.,mode=m.BUS.child(phase+'_mode'),source='A separate EPS consumption0, total representative loads include it. Storage/generation excluded from default EPS demand sum.')
        pcheck(c,s,'14a',phase+'_mean',getattr(eps,phase+'_energy').average_power,r[key])
        pcheck(c,s,'14a',phase+'_energy',getattr(eps,phase+'_energy').required,r[phase+'_energy'])
        rcheck(c,s,'14a',phase+'_delivery',getattr(eps,phase+'_energy'),c['available_'+phase]>=r[phase+'_energy'])
    pcheck(c,s,'14a','minimum_panel_power',eps.solar_power.required,r['required_power'])
    if c['mission']=='BIRDS-4':
        benchmarks=[('main_energy','.428*1.5',.642,'Wh','B-budget p.5'),('receiver_energy','.144*1',.144,'Wh','B-budget p.5'),
                    ('CW_energy','.280*.5',.140,'Wh','B-budget p.5'),
                    ('external_free_rotation_BCR','(2173-240)*.8',1546.,'mWh','B-budget p.8 beta30,35min;external generation,not geometric prediction'),
                    ('external_free_rotation_load','(2507-240)*.8-210',1604.,'mWh','B-budget p.13 beta0;separate revision')]
    else:
        benchmarks=[('standby_surplus','1634-623',1011.,'mWh','O-budget2019,external generation'),
                    ('flight_computer_10min','3.6*.300/6',.180,'Wh','O2016 D.15,distinct historical scalar'),
                    ('heater_6V','6*.245',1.47,'W','O-protect2025 roundedstate')]
    for label,expr,expected,unit,src in benchmarks:
        prop=eps.define('published_'+label,Property(expr,unit))
        pcheck(c,s,'14a',label,prop,expected,basis='published',source=src)
    save_config(c['mission']+':'+s,c,m)
    for s,changes in [('03-eccentric-nadir',dict(eccentricity=.02 if c['mission']=='BIRDS-4' else .04,beta=25.,sun_angle=47.,pointing='nadir')),
                      ('04-eclipse-free',dict(beta=90.))]:
        v=copy.deepcopy(c);v.update(changes);mm=make(v);e=mm.BUS.EPS;oo=geometry(v,s,mm);rr=ref.sizing(v,oo)
        if s.startswith('04'):
            e.eclipse_energy.average_power=None;e.SolarArray.eclipse_path_efficiency=None
            rcheck(v,s,'14a','zero_eclipse_demand',e.eclipse_energy,True)
            pcheck(v,s,'14a','zero_eclipse_energy',e.eclipse_energy.required,0.)
            pcheck(v,s,'14a','unused_eclipse_efficiency_identity',e.solar_power.effective_eclipse_efficiency,1.)
        pcheck(v,s,'14a','minimum_panel_power',e.solar_power.required,rr['required_power'])
        if s.startswith('03'):
            pcheck(v,s,'14b','nontrivial_projection_generation',e.SolarArray.available_power,rr['available_power'])
            rcheck(v,s,'14b','nadir_generation_verdict',e.solar_generation,rr['available_power']>=rr['required_power'])
        save_config(c['mission']+':'+s,v,mm)


def trade_cases(c):
    s='05-baseline-sizing';m=make(c);r=sizing_checks(c,s,m)
    eps=m.BUS.EPS;p=eps.SolarArray;a=c['array'];b=c['battery']
    pcheck(c,s,'14b','BOL_cell_power',p.define('bol_cell_power',Property(f'{a["bol_vmp"]!r}*{a["bol_imp"]!r}','W')),ref.product(a['bol_vmp'],a['bol_imp']),source=a['source'])
    pcheck(c,s,'14b','EOL_efficiency_once',p.eol_efficiency,r['generation_efficiency'])
    if c['mission']=='OreSat':
        pp=p.define('published_BOL_module_power',Property('2*2.43*.483','W'))
        pcheck(c,s,'14b','published_BOL_module_power',pp,2.34,basis='published',source='O-solar 28C AM0, source2.34W rounded, separate from assumedEOL')
        pp=p.define('published_hot_module_power',Property('4.35*.483','W'))
        pcheck(c,s,'14b','published_hot_module_power',pp,2.10,basis='published',source='O-solar70C using source-rounded4.35V,.483A')
    rcheck(c,s,'15','baseline_charger',eps.charger_compatibility,True)
    save_config(c['mission']+':'+s,c,m)
    bol_solar_checks(c)
    s='06-silicon-technology';v=copy.deepcopy(c);v['array']=copy.deepcopy(SI);mm=make(v)
    sizing_checks(v,s,mm,'15')
    save_config(c['mission']+':'+s,v,mm)
    s='07-battery-chemistry';v=copy.deepcopy(c);v['battery']=copy.deepcopy(LI if c['mission']=='BIRDS-4' else LFP)
    if c['mission']=='BIRDS-4':
        v['charger'].update(allowed_min=4.1,allowed_max=4.2,required_termination='CC_CV')
    else:
        v['charger'].update(allowed_min=14.2,allowed_max=14.4,required_termination='CC_CV')
    mm=make(v);sizing_checks(v,s,mm,'15');rcheck(v,s,'15','unchanged_charger_incompatible',mm.BUS.EPS.charger_compatibility,False)
    save_config(c['mission']+':'+s+':incompatible',v,mm)
    vv=copy.deepcopy(v);bb=vv['battery']
    vv['charger'].update(chemistry=bb['chemistry'],series=bb['series'],set_voltage=bb['maximum']*bb['series'],
                         current_limit=bb['charge_limit']*bb['parallel'],termination='CC_CV')
    mm=make(vv);rcheck(vv,s,'15','explicit_new_charger_compatible',mm.BUS.EPS.charger_compatibility,True)
    save_config(c['mission']+':'+s+':selected-new-charger',vv,mm)
    s='08-integer-configurations';v=copy.deepcopy(c)
    configure_four_cell_deployment(v)
    v['battery'].update(series=2 if c['mission']=='BIRDS-4' else 3,parallel=1)
    mm=make(v);sizing_checks(v,s,mm,'16')
    deployment_checks(v,s,mm,'16')
    if c['mission']=='BIRDS-4':
        pcheck(c,s,'16','published_pack_capacity',make(c).BUS.EPS.Battery.rated_capacity,3.8,basis='published',source='B-cell3800mAh minimum convention')
        pcheck(c,s,'16','published_pack_energy',make(c).BUS.EPS.Battery.rated_energy,13.68,basis='published',source='B-budget3.6Vx3.8Ah')
    else:
        pcheck(c,s,'16','published_card_energy',make(c).BUS.EPS.independent_storage_energy,37.4,basis='published',source='O-pack rounded37.4Wh')
        prop=mm.BUS.EPS.define('historical_2019_energy',Property('4*7.2*3.3','Wh'))
        pcheck(c,s,'16','historical_2019_energy',prop,95.04,basis='published',source='O-budget2019,four2Spacks,not2021card')
    save_config(c['mission']+':'+s,v,mm)
    for value in (0,-1,2.5,True):
        mm=make(c);mm.BUS.EPS.SolarArray.series_count=value
        rcheck(c,s,'16','invalid_solar_series_'+repr(value),mm.BUS.EPS.solar_configuration,False)
        mm.BUS.EPS.Battery.parallel_count=value
        rcheck(c,s,'16','invalid_battery_parallel_'+repr(value),mm.BUS.EPS.battery_configuration,False)
    mm=make(c);mm.BUS.EPS.SolarArray.cell_count=99
    rcheck(c,s,'16','inconsistent_total_count',mm.BUS.EPS.solar_configuration,False)
    CONFIGS[c['mission']+':'+s]['additional_mutations']={'SolarArray.series_count':[0,-1,2.5,True], 'Battery.parallel_count':[0,-1,2.5,True],'SolarArray.cell_count':99}


def rail_cases(c):
    s='09-converter-rails';m=make(c);eps=m.BUS.EPS;conv=eps.RegulatorAndConverter;b=c['battery']
    eps.define('rail_power',Property(unit='W'))
    eps.define('battery_current',Property('self.rail_power.value/self.RegulatorAndConverter.efficiency.value/self.Battery.nominal_voltage.value','A'))
    eps.add_requirement('converter_input',conditions=(VerificationCondition('range',Property('(self.parent.context.Battery.minimum_voltage.value,self.parent.context.Battery.maximum_voltage.value)','V'),
        Property('(self.parent.context.RegulatorAndConverter.minimum_input_voltage.value,self.parent.context.RegulatorAndConverter.maximum_input_voltage.value)','V'),
        '0 < target[0] <= measure[0] <= measure[1] <= target[1]'),),rationale='Explicit selected converter source interval, no topology inference')
    lo=b['series']*b['minimum'];hi=b['series']*b['maximum'];vnom=b['series']*b['nominal']
    for voltage,current in [(3.3,.5),(5.,.4)]:
        conv.output_voltage=voltage;eps.bus_voltage.required=voltage;eps.bus_current.required=current
        selected_min,selected_max=(1.8,5.5) if c['mission']=='BIRDS-4' and voltage==3.3 else (c['converter_in_min'],c['converter_in_max'])
        conv.minimum_input_voltage=selected_min;conv.maximum_input_voltage=selected_max
        eps.rail_power=Property('self.RegulatorAndConverter.output_voltage.value*self.bus_current.required.value','W')
        suffix=str(voltage)
        pcheck(c,s,'17','rail_power_'+suffix,eps.rail_power,ref.product(voltage,current))
        pcheck(c,s,'17','terminal_battery_current_'+suffix,eps.battery_current,ref.quotient(ref.product(voltage,current),ref.product(c['converter_efficiency'],vnom)))
        rcheck(c,s,'17','input_interval_'+suffix,eps.converter_input,selected_min<=lo<=hi<=selected_max)
        rcheck(c,s,'17','output_voltage_'+suffix,eps.bus_voltage,True)
        rcheck(c,s,'17','output_current_'+suffix,eps.bus_current,True)
    conv.output_voltage=5.06;eps.bus_voltage.required=5.
    rcheck(c,s,'17','voltage_outside_tolerance',eps.bus_voltage,False)
    eps.bus_current.required=c['converter_current']+.1
    rcheck(c,s,'17','over_output_current',eps.bus_current,False)
    conv.minimum_input_voltage=3.1 if c['mission']=='BIRDS-4' else 1.8
    conv.maximum_input_voltage=17. if c['mission']=='BIRDS-4' else 5.5
    rcheck(c,s,'17','incompatible_converter_input',eps.converter_input,False)
    conv.efficiency=None
    pcheck(c,s,'17','uncharacterized_efficiency_current_unknown',eps.battery_current,None,expected_status='pending')
    if c['mission']=='OreSat':
        # ST SPV1040 maximum output5.2V, independent of switching topology.
        eps.define('spv_maximum_output',Property(5.2,'V'))
        eps.add_requirement('spv_2S_charging',conditions=(VerificationCondition('output',eps.spv_maximum_output,eps.Battery.maximum_voltage,'measure >= target'),))
        rcheck(c,s,'17','historical_SPV1040_rejection',eps.spv_2S_charging,False)
    save_config(c['mission']+':'+s,dict(c,rail_cases=[{'V':3.3,'A':.5},{'V':5.,'A':.4}],
                voltage_tolerance=.05,alternative_output_V=5.06,alternative_current_A=c['converter_current']+.1,
                alternative_converter_interval_V=[3.1,17.] if c['mission']=='BIRDS-4' else [1.8,5.5],
                alternative_converter_product='TPS62111 (3S NiMH lower bound3.0V fails3.1V)' if c['mission']=='BIRDS-4' else 'TPS63020-Q1 (2S Li-ion upper bound8.4V exceeds5.5V)',
                selected_3p3V_product='TPS63020-Q1 input1.8-5.5V' if c['mission']=='BIRDS-4' else 'TPS62111 input3.1-17V',
                selected_5V_product='LTC3119 input2.5-18V' if c['mission']=='BIRDS-4' else 'TPS62112 input3.1-17V',unknown='converter.efficiency'),m)


def sweep_rows():
    path=HERE/'sources'/'oresat-solar-sweep.xlsx'
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        cells={x.attrib['r']:float(x.find('s:v',ns).text) for x in root.findall('.//s:c',ns)
               if x.find('s:v',ns) is not None and x.attrib.get('t') not in ('s','str')}
    rows=[dict(row=i,voltage=cells['G'+str(i)],current_A=cells['F'+str(i)]/1000,
               saved_power=cells['H'+str(i)],raw_B=cells['B'+str(i)]) for i in range(2,207)]
    return rows,path


def pv_cases(c):
    s='10-characteristics';m=make(c);eps=m.BUS.EPS;p=eps.SolarArray;a=c['array']
    points=((0.,a['isc']),(a['vmp'],a['imp']),(a['voc'],0.))
    sr=ref.sampled(points)
    for i,(v,cur) in enumerate(points):
        p.define('sample_v'+str(i),Property(v,'V'));p.define('sample_i'+str(i),Property(cur,'A'))
        pp=p.define('sample_power'+str(i),Property(f'self.sample_v{i}.value*self.sample_i{i}.value','W'))
        pcheck(c,s,'18','sample_VI_'+str(i),pp,sr['products'][i])
    for field,label,expect in [('maximum_power','mpp_power',sr['power']),('mpp_voltage','mpp_voltage',sr['voltage']),
                               ('mpp_current','mpp_current',sr['current']),('open_circuit_voltage','voc',sr['voc']),
                               ('short_circuit_current','isc',sr['isc'])]:
        direct(c,s,'18',label,actual_sizing.pv_characteristics,dict(pv_points=points),field,expect,
               {'maximum_power':'W','mpp_voltage':'V','mpp_current':'A','open_circuit_voltage':'V','short_circuit_current':'A'}[field])
    pcheck(c,s,'18','curve_efficiency',p.generation_efficiency,ref.quotient(sr['power'],ref.product(a['area'],a['reference_irradiance'])))
    for label,req,expect in [('tracking_limit',eps.solar_voltage,True),('absolute_limit',eps.solar_open_circuit_voltage,True),('source_limit',eps.solar_short_circuit_current,True)]:
        rcheck(c,s,'18',label,req,expect)
    # Purchased module carries its own curve as1S1P, not its internal two cells again.
    p.series_count=1;p.parallel_count=1;p.cell_iv_curve=repr(tuple((2*v,i) for v,i in points));p.cell_active_area=2*a['area']
    pcheck(c,s,'18','purchased_panel_no_internal_count_repeat',p.eol_power,ref.product(2,sr['power']))
    p.cell_iv_curve='()';p.series_count=a['series'];p.cell_active_area=a['area']
    pcheck(c,s,'18','empty_curve_scalar_fallback',p.cell_eol_power,sr['power'])
    invalid=[('partial',points[1:]),('duplicate_voltage',((0.,.5),(1.,.4),(1.,.3),(2.,0.))),
             ('negative_current',((0.,.5),(1.,-.1),(2.,0.))),('nonfinite',((0.,.5),(1.,float('nan')),(2.,0.)))]
    for label,pts in invalid:
        direct(c,s,'18','reject_'+label,actual_sizing.pv_characteristics,dict(pv_points=pts),None,None,expected_status='error')
    if c['mission']=='OreSat':
        rows,path=sweep_rows();raw=tuple((x['voltage'],x['current_A']) for x in rows)
        eps.define('published_sweep',Property(repr(raw)))
        pp=eps.define('published_sample_max',Property('max(v*i for v,i in self.published_sweep.value)','W'))
        pcheck(c,s,'18','published_sweep_max_VI',pp,1.6544324,basis='published',source='O-sweep H197; maximum selection evaluator operation')
        row2=eps.define('published_row2_VI',Property('4.77625*.06406','W'))
        pcheck(c,s,'18','published_row2_VI',row2,.305966575,basis='published',source='O-sweep H2')
        direct(c,s,'18','reject_unaltered_published_partial_sweep',actual_sizing.pv_characteristics,dict(pv_points=raw),None,None,expected_status='error',source='O-sweep205rawrows,duplicates,unordered,missingendpoints')
        CONFIGS['published_oresat_sweep']={'rows':rows,'path':str(path.relative_to(HERE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    else:
        direct(c,s,'18','reject_partial_Maya_labelled_subset',actual_sizing.pv_characteristics,
               dict(pv_points=((5.022,.100),(5.123,.05),(5.223,0.))),None,None,expected_status='error',source='B-IV Fig13 exact voltage labels and50mA axes; no short-circuit endpoint')
        for label,expr,expect in [('50mA','5.123*.05',.257),('100mA','5.022*.100',.502)]:
            pp=eps.define('published_Maya_'+label,Property(expr,'W'))
            pcheck(c,s,'18','Maya_label_'+label,pp,expect,basis='published',source='B-IV Fig13 axes50mA steps,Fig14 roundedpowerlabels')
    save_config(c['mission']+':'+s,dict(c,purchased_panel_variation='2cell module curve voltage x2, active area x2, external1S1P',
                invalid_curves=clean(invalid),source_curve_limit='Three-anchor approximation, not complete measured curve.'),m)


def transfer_case(c,s,method,ns=None,setpoint=None):
    v=copy.deepcopy(c)
    if ns:
        if ns!=4:raise ValueError('The declared deployed layout covers the four-cell variation only.')
        configure_four_cell_deployment(v)
    m=make(v,method=method,setpoint=setpoint);eps=m.BUS.EPS;p=eps.SolarArray;a=v['array'];b=v['battery']
    if ns and method=='DET':
        deployment_checks(v,s,m,'19',prefix='shared_4S_')
    pts=((0.,a['isc']),(a['vmp'],a['imp']),(a['voc'],0.))
    bus=ref.product(b['series'],b['nominal']);vm=ref.product(a['series'],a['vmp'])
    vo=bus+.2 if method=='DET' else vm if method=='MPPT' else setpoint
    pcheck(v,s,'19',method+'_operating_voltage',p.operating_voltage,vo)
    if vo > a['series']*a['voc']:
        pcheck(v,s,'19',method+'_infeasible_current',p.operating_current,None,expected_status='error')
        rcheck(v,s,'19',method+'_voltage_still_in_controller_window',eps.solar_voltage,c['tracker_min']<=vo<=c['tracker_max'])
        ENGINEERING.append(dict(mission=c['mission'],scenario=s,mop='MOP-19',check='DET outside supplied array characteristic',verdict=False,status='infeasible',expected=False,configuration_correctness='expected error'))
    else:
        current,power=ref.imposed(pts,a['series'],a['parallel'],vo)
        eff=ref.quotient(power,ref.product(a['series'],a['parallel'],a['area'],a['reference_irradiance']))
        # All transfer cases use Sun pointing, same scalar source loss factors.
        available=ref.product(power,ref.quotient(v['irradiance'],a['reference_irradiance']),v['inherent'],v['assembly'])
        bp=ref.product(available,ref.quotient(bus,vo)) if method=='DET' else ref.product(available,v['converter_efficiency'])
        for label,prop,expect in [('operating_current',p.operating_current,current),('operating_power',p.operating_power,power),
                                 ('operating_efficiency',p.operating_efficiency,eff),('mean_source_power',p.available_power,available),('mean_bus_power',p.bus_power,bp)]:
            pcheck(v,s,'19',method+'_'+label,prop,expect,source='Same EOL3anchor curve, battery nominal bus, .2VDET drop, .9converter, .95*.97source losses; A')
        # Instantaneous load at the same bus boundary, supplied .5W for pair.
        eps.add_requirement('transfer_delivery',conditions=(VerificationCondition('power',p.bus_power,Property(.5,'W'),'measure >= target'),),rationale='Common .5 W bus demand for matched transfer cases')
        rcheck(v,s,'19',method+'_bus_delivery',eps.transfer_delivery,bp>=.5)
        rcheck(v,s,'19',method+'_electrical_window',eps.solar_voltage,v['tracker_min']<=vo<=v['tracker_max'])
    save_config(c['mission']+':'+s+':'+method,dict(v,method=method,DET_drop_V=.2,converter_efficiency=.9,bus_nominal_V=bus,fixed_setpoint_V=setpoint,common_bus_demand_W=.5),m)


def transfer_cases(c):
    transfer_case(c,'11-baseline-DET','DET')
    transfer_case(c,'12-baseline-ideal-MPPT','MPPT')
    transfer_case(c,'13-baseline-fixed-voltage','FIXED_VOLTAGE',setpoint=4.0)
    for method in ('DET','MPPT','FIXED_VOLTAGE'):
        transfer_case(c,'14-unflown-4S-pair',method,ns=4,setpoint=8.0)
    if c['mission']=='OreSat':
        mm=make(c);ee=mm.BUS.EPS
        loss=ee.define('published_module_losses',Property('(.023+.294+.010+.009+.001+.050)','W'))
        net=ee.define('published_net_module_power',Property('2.10-self.published_module_losses.value','W'))
        pcheck(c,'12-baseline-ideal-MPPT','19','published_separate_loss_sum',loss,.387,basis='published',source='O-solar Power and Efficiency Apriori Analysis, separate70C scalar source2.10W')
        pcheck(c,'12-baseline-ideal-MPPT','19','published_separate_net_power',net,1.71,basis='published',source='O-solar2.10Wminus.387W=1.71Wrounded; not converter-only power')
    s='15-operating-point-contract';a=c['array'];pts=((0.,a['isc']),(a['vmp'],a['imp']),(a['voc'],0.))
    exact=a['series']*a['vmp'];mid=exact*.8
    for label,voltage,interp,expected_status in [('exact',exact,'none','value'),('interpolation',mid,'linear','value'),
                                               ('interpolation_not_accepted',mid,'none','error'),('out_of_range',a['series']*a['voc']+.01,'linear','error')]:
        current=ref.imposed(pts,a['series'],a['parallel'],voltage)[0] if expected_status=='value' else None
        direct(c,s,'19',label,actual_sizing.pv_operating_point,dict(pv_points=pts,series_count=a['series'],parallel_count=a['parallel'],operating_voltage=voltage,interpolation=interp),
               'current',current,'A',expected_status)
    m=make(c,method='WRONG');pcheck(c,s,'19','invalid_selector',m.BUS.EPS.SolarArray.operating_voltage,None,expected_status='error')
    m=make(c);m.BUS.EPS.RegulatorAndConverter.transfer_method=None
    pcheck(c,s,'19','unknown_selector',m.BUS.EPS.SolarArray.operating_voltage,None,expected_status='pending')
    save_config(c['mission']+':'+s,dict(c,sampling_voltages_V=[exact,mid,a['series']*a['voc']+.01],interpolation_cases=['none','linear'],selectors=['WRONG',None]),m)


def protection(c):
    s='16-normal-extrema';m=make(c);eps=m.BUS.EPS
    class UVOV(Protection):trip_parameters=('undervoltage_threshold','overvoltage_threshold')
    class OC(Protection):trip_parameters=('current_limit',)
    v=eps.add(UVOV('voltage_detector'));oc=eps.add(OC('rail_detector'))
    if c['mission']=='BIRDS-4':
        volts=(3.9,4.0,4.2);uv=3.5;ov=4.8;currents=(.2,.6,1.5);limit=2.;powers=(1.,3.,7.5);interval=(4.75,5.25)
        note='A battery-node UV3.5OV4.8; battery samples from Tsuru observations. OC2A at distinct5Vregulatedrail, rail currents/powers A. Additional3/4A railthresholds sourceB-rail.'
    else:
        volts=(3.0,3.6,4.0);uv=2.5;ov=4.1;currents=(.265,.314,.362);limit=.375;powers=(6.,30.);interval=(6.,8.4)
        note='O-protect nominalABLIC cellthresholds and suppliedindividualcellnormal3-4V. OC localheaterbranch .245/.294/.342+.020A electronicsassumption, enabledMOARPWR. Powercorners at separate spacecraftbatterybus6-8.4V.'
    v.undervoltage_threshold=uv;v.overvoltage_threshold=ov;v.no_trip.voltages=repr(volts)
    oc.current_limit=limit;oc.no_trip.currents=repr(currents)
    for label,prop,expected in [('Vmin',v.voltage_extrema, list((min(volts),max(volts)))),('Iminmax',oc.current_extrema,list((min(currents),max(currents))))]:
        pcheck(c,s,'20',label,prop,expected,rule='structure',source=note)
    rcheck(c,s,'20','voltage_normal_no_trip',v.no_trip,True);rcheck(c,s,'20','rail_normal_no_trip',oc.no_trip,True)
    lo,hi=ref.corners(powers,*interval)
    corner_detector=eps.add(OC('corner_detector'))
    corner_threshold=2. if c['mission']=='BIRDS-4' else 6.
    corner_detector.current_limit=corner_threshold
    cr=corner_detector.no_trip
    cr.define('powers',Property(repr(powers),'W'))
    cr.define('minimum_voltage',Property(interval[0],'V'))
    cr.define('maximum_voltage',Property(interval[1],'V'))
    cr.currents='tuple(sizing.load_current_extrema(powers=self.powers,minimum_voltage=self.minimum_voltage,maximum_voltage=self.maximum_voltage))'
    pcheck(c,s,'20','bound_current_extrema',corner_detector.current_extrema,[lo,hi],rule='structure',
           source='A independent P/V corners at the declared protected terminals. OreSat spacecraft-bus6A detector is an illustrative separate OC device, not a PTC thermal rating.')
    rcheck(c,s,'20','conservative_corner_no_trip',cr,0<=lo<=hi<corner_threshold)
    for field,expect in [('minimum',lo),('maximum',hi)]:
        direct(c,s,'20','independent_PV_corner_'+field,actual_sizing.load_current_extrema,dict(powers=powers,minimum_voltage=interval[0],maximum_voltage=interval[1]),field,expect,'A',source=note)
    if c['mission']=='OreSat':
        # A separate balanced endpoint case preserves the original normal samples.
        endpoint=eps.define('balanced_charger_cell_voltage',Property('self.charger_set_voltage.value/self.Battery.series_count.value','V'))
        pcheck(c,s,'20','charger_endpoint_per_cell',endpoint,ref.quotient(c['charger']['set_voltage'],c['battery']['series']),
               source='A supplied8.4V2S charger endpoint; O-protect nominal4.10V/cell OV detector')
        endpoint_detector=eps.add(UVOV('charger_endpoint_detector'))
        endpoint_detector.undervoltage_threshold=v.undervoltage_threshold
        endpoint_detector.overvoltage_threshold=v.overvoltage_threshold
        endpoint_detector.no_trip.voltages='(self.context.parent.balanced_charger_cell_voltage.value,)'
        rcheck(c,s,'20','charger_endpoint_no_trip',endpoint_detector.no_trip,False)
        for voltage,published in [(6.,5.),(7.2,4.17),(8.4,3.57)]:
            pp=eps.define('published_current_'+str(int(voltage*10)),Property(f'30/{voltage!r}','A'))
            pcheck(c,s,'20','published_30W_current_'+str(voltage),pp,published,basis='published',source='O-protect30Wspacecraftbatterynode,notlocalheaterOCP')
    else:
        for threshold in (2.,3.,4.):
            oc.current_limit=threshold
            rcheck(c,s,'20','source_rail_threshold_'+str(threshold),oc.no_trip,True)
    save_config(c['mission']+':'+s,dict(mission=c['mission'],sensed_voltages_V=volts,UV_V=uv,OV_V=ov,
                sensed_rail_current_A=currents,OC_A=limit,independent_corner_powers_W=powers,
                independent_corner_voltage_V=interval,independent_corner_OC_A=corner_threshold,
                independent_corner_OC_source='BIRDS2A regulatedrail setting. OreSat6A supplied separate spacecraft-bus OC device, no PTC behavior claim.',
                charger_endpoint_cross_check=dict(pack_voltage_V=8.4,balanced_series_cells=2,nominal_cell_OV_V=4.1,original_normal_cell_samples_V=volts) if c['mission']=='OreSat' else None,source=note),m)
    s='17-threshold-boundaries'
    for detector,threshold in [('UV',uv),('OV',ov),('OC',limit)]:
        for factor in (.99,1.,1.01):
            value=threshold*factor
            if detector=='UV':
                v.no_trip.voltages=repr((value,));r=v.no_trip;expected=value>uv and value<ov
            elif detector=='OV':
                v.no_trip.voltages=repr((value,));r=v.no_trip;expected=value>uv and value<ov
            else:
                oc.current_limit=limit;oc.no_trip.currents=repr((value,));r=oc.no_trip;expected=0<=value<limit
            rcheck(c,s,'20',detector+'_'+str(factor),r,expected)
    extra_settings=[('Unreg2',3.),('Unreg1',4.)] if c['mission']=='BIRDS-4' else [('spacecraft_battery_bus',6.)]
    for rail,threshold in extra_settings:
        extra=eps.add(OC(rail+'_boundary_detector'))
        extra.current_limit=threshold
        for factor in (.99,1.,1.01):
            extra.no_trip.currents=repr((threshold*factor,))
            rcheck(c,s,'20',rail+'_OC_'+str(factor),extra.no_trip,0<=factor<1.)
    v.no_trip.voltages=None;rcheck(c,s,'20','unknown_voltage_samples',v.no_trip,None,status='pending')
    v.no_trip.voltages='()';rcheck(c,s,'20','empty_voltage_samples',v.no_trip,None,status='error')
    v.no_trip.voltages="(float('nan'),)";rcheck(c,s,'20','nonfinite_voltage_samples',v.no_trip,None,status='error')
    oc.no_trip.currents='(-.01,)';rcheck(c,s,'20','negative_current_magnitude_fails',oc.no_trip,False)
    oc.no_trip.currents='()';rcheck(c,s,'20','empty_current_samples',oc.no_trip,None,status='error')
    oc.no_trip.currents=None;rcheck(c,s,'20','unknown_current_samples',oc.no_trip,None,status='pending')
    oc.current_limit=None;oc.no_trip.currents='(.1,)';rcheck(c,s,'20','unknown_threshold',oc.no_trip,None,status='pending')
    save_config(c['mission']+':'+s,dict(mission=c['mission'],UV_V=uv,OV_V=ov,OC_A=limit,
                factors=[.99,1.,1.01],additional_OC_settings=[dict(rail=rail,threshold_A=threshold) for rail,threshold in extra_settings],
                additional_OC_scope='BIRDS Unreg2 and Unreg1 are distinct unregulated rail detectors. OreSat6A is a supplied spacecraft battery-bus detector, separate from local heater OC and ABLIC cell sensing.',invalid_voltages=[None,[],['nan']],invalid_current=[[-.01],[],None],unknown_OC_threshold=True),m)


def invalid_cases(c):
    s='18-unknown-invalid-feasibility';m=make(c);eps=m.BUS.EPS
    eps.SolarArray.series_count=None;pcheck(c,s,'16','unknown_series_count',eps.SolarArray.cell_count,None,expected_status='pending')
    eps.SolarArray.series_count=c['array']['series'];eps.SolarArray.usable_area=None
    rcheck(c,s,'15','unknown_installation_allocation',eps.solar_area_fit,None,status='pending')
    eps.Battery.cycle_coefficient=None;pcheck(c,s,'14b','unknown_life_fit',eps.battery_energy.required,None,expected_status='pending')
    eps.Battery.energy_retention=None;pcheck(c,s,'14b','unknown_energy_retention',eps.Battery.eol_energy,None,expected_status='pending')
    eps.available_sunlight_energy=1.;rcheck(c,s,'14a','deliberately_inadequate_delivery',eps.sunlight_energy,False)
    m.orbit.altitude=None;pcheck(c,s,'14a','unknown_orbit',m.orbit.period,None,expected_status='pending')
    direct(c,s,'14a','invalid_perigee',actual_sizing.orbit_period,dict(semimajor_axis=6500.,eccentricity=.2,earth_radius=6378.,gravitational_parameter=398601.),None,None,expected_status='error')
    direct(c,s,'14b','unsupported_cycle_fit',actual_sizing.depth_of_discharge,dict(required_cycles=30000.,cycle_coefficient=2000.,cycle_exponent=-1.,fit_dod_min=.1,fit_dod_max=.8),None,None,expected_status='error')
    direct(c,s,'14b','invalid_retention',actual_sizing.retained_value,dict(initial=1.,retention=1.1),None,None,expected_status='error')
    direct(c,s,'14b','invalid_packing',actual_sizing.panel_area,dict(active_area=.01,packing_fraction=0.),None,None,expected_status='error')
    direct(c,s,'20','invalid_current_voltage_interval',actual_sizing.load_current_extrema,dict(powers=(1.,),minimum_voltage=0.,maximum_voltage=5.),None,None,expected_status='error')
    save_config(c['mission']+':'+s,dict(c,unknown=['SolarArray.series_count','SolarArray.usable_area','Battery.cycle_coefficient','Battery.energy_retention','orbit.altitude'],
                invalid_orbit=dict(a=6500,e=.2,R=6378),invalid_cycles=30000,invalid_retention=1.1,invalid_packing=0.,inadequate_sunlight_delivery_J=1.),m)


def run(output):
    for collection in (ROWS,CONFIGS,BINDINGS,CONVERGENCE,ENGINEERING,REFERENCE_CHECKS):
        collection.clear()
    for name in BASELINES:
        c=clone(name)
        mass_cases(name);budget_cases(c);trade_cases(c);rail_cases(c);pv_cases(c);transfer_cases(c);protection(c);invalid_cases(c)
    ids=[x['id'] for x in ROWS]
    if len(set(ids))!=len(ids):raise AssertionError('Duplicate comparison identifiers')
    for name in BASELINES:
        assert {r['mop'][4:] for r in ROWS if r['mission']==name}==set(MOP_ORDER)
        assert len({r['scenario'] for r in ROWS if r['mission']==name})==18
    assert all(x['actual_provider']['kind'] in ('public Property','public Requirement.verify','direct public numerical function') for x in ROWS)
    assert all(x['fine']['kepler_residual_rad']<1e-12 and x['eclipse_relative_change']<.001 and x['projection_relative_change']<.001 for x in CONVERGENCE)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('framework/models','framework/scripts') for p in sorted((ROOT/folder).glob('*.py'))}
    try:
        revision=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,capture_output=True)
        revision_id=revision.stdout.strip() if revision.returncode==0 else None
    except OSError:
        revision_id=None
    meta=dict(framework_revision=revision_id,framework_root=str(ROOT),
              framework_sha256=hashes,driver_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'run_case_studies.py',HERE/'independent_reference.py',HERE/'case_inputs.py']},
              python=sys.version,reference_numpy=__import__('numpy').__version__,execution_command='PYTHONDONTWRITEBYTECODE=1 python3 run_case_studies.py --framework-root <repository-root>',
              comparison_count=len(ROWS),scenario_count=36)
    local_session=HERE/'session.jsonl'
    if local_session.is_file():
        meta['saved_child_session']=str(local_session)
    accounting=dict(numerical_value_comparisons=sum(r['actual_status']=='value' and r['comparison_rule'].startswith('1%') for r in ROWS),
                    exact_or_structural_value_comparisons=sum(r['actual_status']=='value' and not r['comparison_rule'].startswith('1%') for r in ROWS),
                    expected_unknowns=sum(r['outcome']=='expected unknown' for r in ROWS),
                    expected_errors=sum(r['outcome']=='expected error' for r in ROWS),
                    false_resolved_engineering_verdicts=sum(r['status']=='value' and r['verdict'] is False for r in ENGINEERING))
    counts=[]
    for name in BASELINES:
        for mop in MOP_ORDER:
            rows=[r for r in ROWS if r['mission']==name and r['mop']=='MOP-'+mop]
            counts.append(dict(mission=name,mop='MOP-'+mop,total=len(rows),**dict(Counter(x['outcome'] for x in rows))))
    summary=dict(metadata=meta,per_mission_mop=counts,total_outcomes=dict(Counter(x['outcome'] for x in ROWS)),
                 maximum_numeric_relative_error=max((x['relative_error'] or 0 for x in ROWS)),
                 coverage_limitations=['BIRDS1.575W true measured peak not reconstructed. Only unambiguous50/100mA VI/P labels checked. Complete curves are declared3anchor approximations.',
                   'No complete flight architecture or full chronological EPS simulation. Representative sections and assumed lifetimes/efficiencies/limits.',
                   'No validated product life/DoD fits, full I-V surfaces, worst-case detector tolerances or charger/thermal dynamics.'],
                 convergence=CONVERGENCE,reference_count_stability=REFERENCE_CHECKS,comparison_accounting=accounting,
                 engineering_disclosures=['OreSat8.4V balanced2S charger endpoint is4.20V/cell, above nominal4.10V ABLIC OV. Its separate static no-trip verdict fails. Original normal3.0/3.6/4.0V samples remain unchanged.',
                   'Four-cell variants use explicit0.10x0.17m deployed plates with2x2 grids,2mm gaps,3mm edge clearances and0.1mm upper envelope allowances. Layout checks are numerical checks of sourced/supplied rectangles, not mechanical qualification.',
                   'All declared UV/OV/OC settings, including BIRDS3/4A and OreSat6A, are bracketed at0.99/1.00/1.01 of threshold on their distinct sensed nodes.'])
    output.mkdir(parents=True,exist_ok=True)
    for filename,data in [('results.json',ROWS),('inputs.json',dict(sources=SOURCES,baselines=BASELINES,executed_configurations=CONFIGS)),
                          ('model-bindings.json',BINDINGS),('summary.json',summary),('engineering-verdicts.json',ENGINEERING)]:
        (output/filename).write_text(json.dumps(clean(data),indent=2,sort_keys=True,allow_nan=False)+'\n')
    with (output/'results.csv').open('w',newline='') as f:
        fields=list(ROWS[0]);w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for row in ROWS:w.writerow({k:json.dumps(clean(v),sort_keys=True) if isinstance(v,(dict,list,tuple)) else v for k,v in row.items()})
    print(json.dumps(dict(comparisons=len(ROWS),scenario_groups=36,outcomes=summary['total_outcomes'],max_relative_error=summary['maximum_numeric_relative_error']),indent=2))
    if any(r['outcome']=='mismatch' for r in ROWS):
        print('MISMATCHES:')
        for r in ROWS:
            if r['outcome']=='mismatch': print(r['id'],r['expected'],r['actual'],r['actual_status'],r['detail'] if r['actual_status']!='value' else '')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'executed')
    parser.add_argument('--framework-root',type=Path,help='Repository root, overriding EPS_FRAMEWORK_ROOT and ancestor discovery')
    run(parser.parse_args().output)
