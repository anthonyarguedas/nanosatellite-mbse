#!/usr/bin/env python3
"""Render a proposed COTS library definition view, not a selected EPS topology.

python3 final_report/fig/eps-component-models.py --jobdir /absolute/external/job

Only the six category names are carried over from the authored CSRM structure
view. Properties, shared records and interface types summarize the proposed
report schema supplied for this figure; they are not native CSRM definitions.
This illustrative SysML v2-style view is not compiled or executable SysML.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from diagram_style import (Figure, INK, LIGHT, SerifMetrics, render_figure,
                           require, sha, validate_style)

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
BASE = FIG / 'eps-component-models'
WIDTH, HEIGHT, FONT = 690, 470, 11
BOX_W, BOX_H = 192, 164

# These identifiers are reusable interface TYPE identifiers, not the report's
# framework endpoint identifiers (IF-01, etc.). Physical signs are not conveyed
# by arrows, conjugation or the left/right placement of these declarations.
INTERFACE_TYPES = {
    'IF-E': 'DC terminal pair; V across, I positive into owner; return/polarity and pins declared',
    'IF-T': 'Thermal boundary; T and heat flow positive into owner; boundary/contact and optional model',
    'IF-D': 'Provider accepts commands/configuration and emits telemetry/events; requester conjugates directed items; transport on host for software',
    'IF-C': 'Discrete hardware control/inhibit; direction, logic, defaults/faults, pins and response declared',
}
RECORDS = [
    {'id': 'catalog_identity', 'title': 'Catalog identity', 'lines': [
        'ID; manufacturer; part/revision; roles']},
    {'id': 'sourced_values', 'title': 'Sourced values', 'lines': [
        'value/unit; conditions; source; status']},
    {'id': 'hardware_data', 'title': 'Hardware data (hardware only)', 'lines': [
        'mass/envelope; pins; environment']},
]


def port(identifier, role, typ, multiplicity, side, row):
    return dict(id=identifier, role=role, type=typ, multiplicity=multiplicity,
                side=side, row=row)


def properties(*rows):
    return [dict(id=identifier, summary=summary) for identifier, summary in rows]


# Each property group has exactly one visible summary. The provenance manifest
# and tests use the same group IDs to detect omissions, duplication or drift.
COMPONENTS = [
    {'id': 'solar-arrays', 'name': 'Solar Arrays', 'properties': properties(
        ('configuration', 'cell/panel; technology; Ns/Np : Integer'),
        ('photovoltaic', 'Vmp, Imp, Voc, Isc [V, A]; area [m²]'),
        ('conditions', 'at T, irradiance, BOL/EOL'),
        ('models', 'I–V/model; temperature/degradation'),
        ('installed_usage', 'deployed/stowed geometry: usage')),
     'ports': [port('dc-output', 'dc output', 'IF-E', '1..*', 'left', 0),
               port('thermal', 'thermal', 'IF-T', '0..*', 'right', 0),
               port('monitor', 'monitor', 'IF-D', '0..*', 'right', 1)]},
    {'id': 'batteries', 'name': 'Batteries', 'properties': properties(
        ('configuration', 'cell/pack; chemistry; Ns/Np : Integer'),
        ('ratings', 'Vmin/nom/max [V]; Q [Ah]; E [Wh]'),
        ('current_limits', 'current limits [A]; pulse duration [s]'),
        ('life_limits', 'charge/discharge T limits; life/DoD'),
        ('degradation', 'resistance [Ω]; capacity retention')),
     'ports': [port('dc-bidirectional', 'bidir. dc', 'IF-E', '1..*', 'left', 0),
               port('thermal', 'thermal', 'IF-T', '0..*', 'right', 0),
               port('monitor', 'monitor', 'IF-D', '0..*', 'right', 1)]},
    {'id': 'regulators-converters', 'name': 'Regulators and Converters', 'properties': properties(
        ('role', 'role; buck/boost/buck-boost'),
        ('input', 'DET/MPPT; input/absolute/MPPT [V]'),
        ('output', 'Vout, ripple [V]; Iin,Iout [A]; pulse [s]'),
        ('losses_limits', 'η(V,I,T); idle [W]; startup/charge limits'),
        ('bidirectional', 'bidirectional capability (declared)')),
     'ports': [port('dc-input', 'input dc', 'IF-E', '1..*', 'left', 0),
               port('dc-output', 'output dc', 'IF-E', '1..*', 'left', 1),
               port('thermal', 'thermal', 'IF-T', '0..*', 'right', 0),
               port('service', 'service', 'IF-D', '0..*', 'right', 1),
               port('enable', 'enable', 'IF-C', '0..*', 'right', 2)]},
    {'id': 'power-circuits-switches', 'name': 'Power Circuits and Switches', 'properties': properties(
        ('configuration', 'role/channels; independent control'),
        ('ratings', 'ratings [V, A]; pulse [s]; Ron [Ω]'),
        ('protection', 'threshold [V,A,K]; delay [s]; hysteresis'),
        ('reset_inhibits', 'defaults/reset; reverse blocking/inhibits'),
        ('sensing', 'sensing ranges/accuracy')),
     'ports': [port('dc-input', 'input dc', 'IF-E', '1..*', 'left', 0),
               port('dc-output', 'output dc', 'IF-E', '1..*', 'left', 1),
               port('thermal', 'thermal', 'IF-T', '0..*', 'right', 0),
               port('service', 'service', 'IF-D', '0..*', 'right', 1),
               port('control-inhibit', 'control/inhibit', 'IF-C', '0..*', 'right', 2)]},
    {'id': 'processor-memory', 'name': 'Processor and Memory', 'properties': properties(
        ('processor', 'processor architecture; clock [Hz]'),
        ('memory', 'program/data memory [byte]'),
        ('supply', 'supply [V]; power by mode [W]'),
        ('data_links', 'links: protocol/version, pins, logic, rate'),
        ('peripherals', 'timers; watchdog; sensing channels')),
     'ports': [port('supply', 'supply dc', 'IF-E', '1..*', 'left', 0),
               port('thermal', 'thermal', 'IF-T', '0..*', 'right', 0),
               port('data-service', 'data service', 'IF-D', '0..*', 'right', 1),
               port('discrete-io', 'discrete I/O', 'IF-C', '0..*', 'right', 2)]},
    {'id': 'software', 'name': 'Software', 'properties': properties(
        ('compatibility', 'release; host/firmware/driver support'),
        ('resources_timing', 'memory [byte]; timing/deadlines [s]'),
        ('service', 'commands/telemetry/events'),
        ('protection_configuration', 'protection/configuration ranges'),
        ('behavior', 'mode/sequence/recovery behavior')),
     'reference': 'ref host : Processor and Memory [1..*]',
     'exclusion': 'no independent hardware mass/power',
     'ports': [port('logical-service', 'logical service', 'IF-D', '1..*', 'right', 0)]},
]
LOAD = {'id': 'load', 'name': 'Load', 'external': True, 'properties': properties(
    ('demand', 'required voltage [V]; load law: constant power/current/resistance'),
    ('transients', 'mode power/current [W, A]; inrush/pulse amplitude/duration [A, s]'),
    ('operation', 'schedule/duty; startup [s]; shedding priority/default state')),
    'ports': [port('supply', 'supply dc', 'IF-E', '1..*', 'right', 0),
              port('thermal', 'thermal', 'IF-T', '0..*', 'right', 1),
              port('data-service', 'data service', 'IF-D', '0..*', 'right', 2),
              port('enable', 'enable', 'IF-C', '0..*', 'right', 3)]}


def record_ids(component):
    return ['catalog_identity', 'sourced_values'] + ([] if component['id'] == 'software'
                                                  else ['hardware_data'])


def text(figure, parent, value, x, y, region, **attrs):
    """All visible labels declare a local containment region, never a footer."""
    return figure.text(value, x, y, size=FONT, parent=parent,
                       data_text_region=','.join(f'{v:g}' for v in region), **attrs)


def divider(figure, parent, x1, y1, x2, y2):
    figure.el('line', parent, x1=x1, y1=y1, x2=x2, y2=y2,
              stroke=INK, stroke_width='.8', data_compartment_divider='true')


def shared_records(figure):
    group = figure.el('g', data_shared_records='true')
    figure.rect(8, 8, 674, 32, group, data_record_banner='true')
    for index, record in enumerate(RECORDS):
        x, width = 8 + index * 674/3, 674/3
        if index:
            divider(figure, group, x, 8, x, 40)
        record_group = figure.el('g', group, data_record=record['id'])
        region = (x+8, 8, width-16, 32)
        text(figure, record_group, record['title'], x+8, 20, region,
             weight='bold', data_record_title=record['id'])
        for row, label in enumerate(record['lines']):
            text(figure, record_group, label, x+8, 33+13*row, region,
                 data_record_field_group=f'{record["id"]}.{row}')


def boundary_port(figure, group, component, declaration, x, cy, body, compact=False):
    """Horizontal type IDs distinguish this view from numeric framework ports.

    Use data-type-port, not the shared helper's data-port metadata: its port
    validator is specifically for rotated, numeric IF-01 framework endpoints.
    No shared helper is changed or bypassed; local type declarations have their
    own checks in addition to the normal Figure/render_figure checks.
    """
    key = component['id'] + '.' + declaration['id']
    height = 14 if compact else 16
    rect = (x-15, cy-height/2, 30, height)
    figure.rect(*rect, group, data_type_port=key, data_type_id=declaration['type'],
                data_owner=component['name'], data_role=declaration['role'],
                data_multiplicity=declaration['multiplicity'],
                data_side=declaration['side'])
    text(figure, group, declaration['type'], x, cy+3.5, rect,
         weight='bold', anchor='middle', data_type_port_label=key)
    bx, by, bw, bh = body
    label = f'{declaration["role"]} [{declaration["multiplicity"]}]'
    if declaration['side'] == 'left':
        tx, anchor, region = x+21, 'start', (x+21, by, bw-42, bh)
    else:
        inset = 8 if compact else 21
        tx, anchor, region = x-21, 'end', (bx+inset, by, bw-inset-21, bh)
    text(figure, group, label, tx, cy+3.5, region, anchor=anchor,
         data_type_port_role=key)


def component_block(figure, component, index):
    x, y = 23+(index % 3)*226, 48+(index//3)*176
    group = figure.el('g', data_definition=component['name'],
                      data_component_id=component['id'], data_external='false',
                      data_record_refs=','.join(record_ids(component)))
    figure.rect(x, y, BOX_W, BOX_H, group, data_definition_body=component['name'])
    header = (x+8, y+2, BOX_W-16, 31)
    text(figure, group, '«part def»', x+BOX_W/2, y+13, header,
         anchor='middle', data_stereotype='part def')
    # Use the common 11 pt minimum for names as well as every property/port.
    text(figure, group, component['name'], x+BOX_W/2, y+27, header,
         weight='bold', anchor='middle', data_definition_name=component['name'])
    divider(figure, group, x, y+34, x+BOX_W, y+34)
    region = (x+8, y+36, BOX_W-16, 69)
    for row, prop in enumerate(component['properties']):
        text(figure, group, prop['summary'], x+8, y+47+13*row, region,
             data_property_group=prop['id'], data_property_owner=component['name'])
    divider(figure, group, x, y+107, x+BOX_W, y+107)
    for declaration in component['ports']:
        px = x if declaration['side'] == 'left' else x+BOX_W
        boundary_port(figure, group, component, declaration, px,
                      y+118+17*declaration['row'], (x, y+108, BOX_W, 55))
    if component.get('reference'):
        region = (x+8, y+128, BOX_W-16, 35)
        text(figure, group, component['reference'], x+8, y+139, region,
             data_reference='host', data_reference_target='Processor and Memory',
             data_reference_multiplicity='1..*')
        text(figure, group, component['exclusion'], x+8, y+155, region,
             data_hardware_exclusion='true')


def external_load(figure):
    x, y, width, height = 23, 400, 644, 64
    group = figure.el('g', data_definition='Load', data_component_id='load',
                      data_external='true', data_record_refs=','.join(record_ids(LOAD)))
    figure.rect(x, y, width, height, group, fill=LIGHT, data_definition_body='Load')
    divider(figure, group, 118, y, 118, y+height)
    divider(figure, group, 550, y, 550, y+height)
    header = (x+5, y+4, 85, height-8)
    text(figure, group, '«part def»', 70.5, y+26, header,
         anchor='middle', data_stereotype='part def')
    text(figure, group, 'Load', 70.5, y+42, header,
         anchor='middle', weight='bold', data_definition_name='Load')
    region = (130, y+7, 408, height-14)
    for row, prop in enumerate(LOAD['properties']):
        text(figure, group, prop['summary'], 130, y+20+13*row, region,
             data_property_group=prop['id'], data_property_owner='Load')
    for declaration in LOAD['ports']:
        boundary_port(figure, group, LOAD, declaration, 667,
                      y+8+16*declaration['row'], (550, y, 117, height), compact=True)


def create_figure(metrics=None):
    figure = Figure('Proposed COTS EPS component part definitions', WIDTH, HEIGHT,
                    metrics or SerifMetrics())
    # No exchanges or arrows, including unused marker definitions, in this view.
    figure.root.find('./{*}defs').clear()
    figure.root.set('data-view-kind', 'proposed definition library; no selected topology')
    shared_records(figure)
    for index, component in enumerate(COMPONENTS):
        component_block(figure, component, index)
    external_load(figure)
    return figure


def text_bounds(node, metrics):
    size = float(node.attrib['font-size'])
    width = metrics.measure(node.text or '', size, node.attrib.get('font-weight', 'normal'))
    x, y = float(node.attrib['x']), float(node.attrib['y'])
    anchor = node.attrib.get('text-anchor', 'start')
    left = x-width/2 if anchor == 'middle' else x-width if anchor == 'end' else x
    # Conservative Times text extents; PDF word boxes are checked independently.
    return left, y-size*.9, left+width, y+size*.25


def validate_definition_view(figure):
    root, metrics = figure.root, figure.metrics
    validate_style(root)
    components = COMPONENTS + [LOAD]
    groups = root.findall('.//{*}g[@data-definition]')
    require([g.attrib['data-definition'] for g in groups] == [c['name'] for c in components],
            'Missing, renamed or repeated component definition')
    require(not root.findall('.//{*}path') and not root.findall('.//{*}marker'),
            'Definition view must not select paths or exchanges')
    port_count = 0
    for group, component in zip(groups, components):
        require(group.attrib['data-record-refs'].split(',') == record_ids(component),
                'Inconsistent shared property records')
        summaries = group.findall('./{*}text[@data-property-group]')
        require([(n.attrib['data-property-group'], n.text) for n in summaries] ==
                [(p['id'], p['summary']) for p in component['properties']],
                'Inconsistent diagram property groups: '+component['name'])
        body = group.find('./{*}rect[@data-definition-body]')
        bx, by, bw, bh = [float(body.attrib[a]) for a in ('x', 'y', 'width', 'height')]
        require(body.attrib['fill'] == (LIGHT if component.get('external') else 'white'),
                'Only the external Load may be gray')
        ports = group.findall('./{*}rect[@data-type-port]')
        require(len(ports) == len(component['ports']), 'Missing/repeated port declaration')
        for rectangle, declaration in zip(ports, component['ports']):
            key = component['id']+'.'+declaration['id']
            label = group.find(f'./{{*}}text[@data-type-port-label="{key}"]')
            role = group.find(f'./{{*}}text[@data-type-port-role="{key}"]')
            px, py, pw, ph = [float(rectangle.attrib[a]) for a in ('x', 'y', 'width', 'height')]
            require(rectangle.attrib['data-type-port'] == key and
                    rectangle.attrib['data-type-id'] == declaration['type'] and
                    rectangle.attrib['data-owner'] == component['name'] and
                    rectangle.attrib['data-role'] == declaration['role'] and
                    rectangle.attrib['data-multiplicity'] == declaration['multiplicity'],
                    'Changed port declaration: '+key)
            require(label is not None and label.text == declaration['type'] and
                    role is not None and role.text ==
                    f'{declaration["role"]} [{declaration["multiplicity"]}]',
                    'Port type, role or multiplicity label mismatch: '+key)
            require(px+pw/2 == (bx if declaration['side'] == 'left' else bx+bw)
                    and by <= py and py+ph <= by+bh,
                    'Port is not on its owner boundary: '+key)
            port_count += 1
        require(len(group.findall('./{*}text[@data-stereotype]')) == 1,
                'Each component must be a part definition')
    require(len(root.findall('.//{*}rect[@data-type-port]')) == port_count == 25,
            'Unexpected interface declaration count')
    software = root.find('.//{*}g[@data-definition="Software"]')
    reference = software.find('./{*}text[@data-reference="host"]')
    require(reference is not None and reference.text == 'ref host : Processor and Memory [1..*]'
            and reference.attrib.get('data-reference-target') == 'Processor and Memory'
            and reference.attrib.get('data-reference-multiplicity') == '1..*',
            'Software host must be a typed reference, not composition')
    require([p.attrib['data-type-id'] for p in software.findall('./{*}rect[@data-type-port]')]
            == ['IF-D'] and software.find('./{*}text[@data-hardware-exclusion]').text
            == 'no independent hardware mass/power',
            'Software owns logical service only, without independent hardware properties')
    labels = root.findall('.//{*}text')
    for node in labels:
        require(float(node.attrib['font-size']) >= FONT, 'Unreadably small label')
        require('transform' not in node.attrib, 'Keep definition labels horizontal')
        left, top, right, bottom = text_bounds(node, metrics)
        x, y, width, height = map(float, node.attrib['data-text-region'].split(','))
        require(0 <= left <= right <= WIDTH and 0 <= top <= bottom <= HEIGHT,
                'Text outside page: '+str(node.text))
        require(x-.01 <= left and right <= x+width+.01 and y-.01 <= top
                and bottom <= y+height+.01, 'Text outside block/compartment: '+str(node.text))
    # Also catch mutually overlapping labels (including neighboring port roles).
    for index, a in enumerate(labels):
        al, at, ar, ab = text_bounds(a, metrics)
        for b in labels[index+1:]:
            bl, bt, br, bb = text_bounds(b, metrics)
            require(min(ar, br)-max(al, bl) <= .01 or min(ab, bb)-max(at, bt) <= .01,
                    'Overlapping labels: '+str(a.text)+' / '+str(b.text))
    return {'csrm_eps_groups': 6, 'external_loads': 1, 'shared_record_types': 3,
            'property_groups': sum(len(c['properties']) for c in components),
            'boundary_port_declarations': port_count,
            'interface_type_counts': dict(sorted(Counter(p['type'] for c in components
                                                        for p in c['ports']).items())),
            'all_labels_at_least_11_pt': True, 'text_within_blocks_and_page': True,
            'no_overlapping_labels': True, 'no_connectors_or_exchange_arrows': True,
            'software_logical_service_only': True, 'host_is_reference_not_composition': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', type=Path, required=True)
    args = parser.parse_args()
    require(not args.jobdir.resolve().is_relative_to(ROOT), 'Use an external job directory')
    figure = create_figure()
    checks = validate_definition_view(figure)
    output = render_figure(figure, BASE, args.jobdir)
    provenance = {
        'basis': 'Proposed report synthesis for a reusable COTS database; only the six group names are CSRM-derived',
        'view': 'SysML v2-style part definition/library illustration; not a selected wiring topology',
        'limitations': 'No compiled/executable SysML v2 conformance, solver evaluation, selected configuration, physical path, isolation or redundancy is claimed.',
        'generator_sha256': sha(Path(__file__)),
        'shared_style_sha256': sha(FIG / 'diagram_style.py'),
        'csrm_name_basis': {name: sha(FIG / name) for name in
                            ('csrm-structure.py', 'csrm-eps-components.svg')},
        'shared_records': RECORDS, 'interface_types': INTERFACE_TYPES,
        'component_definitions': [{**c, 'shared_records': record_ids(c)} for c in COMPONENTS+[LOAD]],
        'checks': checks, 'output': output,
    }
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
