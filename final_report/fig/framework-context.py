#!/usr/bin/env python3
"""Reproduce the black-box framework context with labeled boundary ports.

python3 final_report/fig/framework-context.py --jobdir /absolute/external/check-dir
Requires Times New Roman, librsvg and Poppler. This is an authored illustration.
Each summary arrow groups recorded flows with the same interface and direction.
No model checking or simulation occurs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from diagram_style import (Figure, LIGHT, LINE_PATTERNS, render_figure,
                           require, sha, shared_port, validate_port_labels)

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
BASE = FIG / 'framework-context'
W, H = 690, 606
FRAME = (300, 49, 105, 550)
ACTOR_H = 86

# Exchange groups stay at the system requirements level. Logical ownership
# remains in the separate architecture figure.
INTERFACES = [
    {'id': 'IF-01', 'port': 'p01', 'side': 'left', 'y': 84,
     'name': ['Engineering use'], 'actor': 'engineers',
     'actor_labels': ['Engineers and', 'stakeholders'],
     'in_y': 108, 'out_y': 158,
     'in_labels': ['Engineering submissions', 'Authorized decisions'],
     'in_label_y': 79,
     'out_labels': ['Guidance and products'], 'out_label_y': 149},
    {'id': 'IF-03', 'port': 'p03', 'side': 'right', 'y': 188,
     'name': ['Spacecraft simulation', 'coupling'], 'actor': 'tools',
     'actor_labels': ['NVIDIA', 'Omniverse', 'spacecraft and', 'subsystem', 'simulations'],
     'in_y': 270, 'out_y': 212,
     'out_labels': ['Spacecraft models and', 'simulation requests', 'EPS states and', 'feasibility findings'],
     'out_label_y': 150,
     'in_labels': ['Spacecraft conditions', 'Feasibility findings', 'Histories and status'],
     'in_label_y': 228},
    {'id': 'IF-02', 'port': 'p02', 'side': 'left', 'y': 292,
     'name': ['Knowledge and', 'supplied data'], 'actor': 'sources',
     'actor_labels': ['Knowledge and', 'data sources'],
     'in_y': 316, 'out_y': 366,
     'in_labels': ['Sources and methods', 'Component properties', 'Reference data'],
     'in_label_y': 270,
     'out_labels': ['Source queries'], 'out_label_y': 356},
    {'id': 'IF-04', 'port': 'p04', 'side': 'right', 'y': 396,
     'name': ['Host software', 'execution'], 'actor': 'software',
     'actor_labels': ['F Prime', 'host toolchain'],
     'in_y': 474, 'out_y': 420,
     'out_labels': ['Authorized design', 'and interfaces', 'Coding/build/SIL', 'requests'],
     'out_label_y': 358,
     'in_labels': ['Host products and logs', 'Raw SIL responses'], 'in_label_y': 442},
    {'id': 'IF-06', 'port': 'p06', 'side': 'left', 'y': 500,
     'name': ['Technical review'], 'actor': 'reviewers',
     'actor_labels': ['Reviewers and', 'review', 'authority'],
     'in_y': 524, 'out_y': 578,
     'in_labels': ['Findings and authorized', 'review decisions'], 'in_label_y': 495,
     'out_labels': ['Review packages'], 'out_label_y': 566},
]


def create_figure():
    figure = Figure('Framework boundary and external exchanges', W, H)
    figure.el('desc').text = (
        'The EPS engineering framework is an opaque black box. Five labeled '
        'port rectangles straddle its boundary. Engineers, knowledge sources, '
        'reviewers, NVIDIA Omniverse spacecraft and subsystem simulations, and the F Prime host toolchain '
        'remain outside. Each directed exchange has one head at its destination. '
        + ' '.join(f'{entry["id"]}: {" ".join(entry["name"])}.' for entry in INTERFACES))
    figure.text('Framework boundary and external exchanges', 8, 20, size=18, weight='bold')
    frame = figure.el('g', data_system='Framework')
    figure.rect(*FRAME, parent=frame, data_enclosure='Framework')
    figure.lines(['EPS', 'engineering', 'framework'], FRAME[0]+FRAME[2]/2, 65,
                 size=16, leading=18, weight='bold', anchor='middle',
                 parent=frame, width=FRAME[2]-12)
    inventory = json.loads((FIG / 'logical-architecture.inventory.json').read_text())
    by_id = {entry['id']: entry for entry in inventory['interfaces']}
    for entry in INTERFACES:
        identifier, y = entry['id'], entry['y']
        native = by_id[identifier]
        require((entry['actor'], entry['port']) == (native['actor'], native['port']),
                'Changed context participant or port')
        left = entry['side'] == 'left'
        actor_x, actor_w = (8, 105) if left else (575, 107)
        actor = figure.el('g', data_actor=entry['actor'])
        figure.rect(actor_x, y, actor_w, ACTOR_H, actor, fill=LIGHT)
        actor_labels = entry['actor_labels']
        first_line = y+(ACTOR_H-16*(len(actor_labels)-1))/2+5
        figure.lines(actor_labels, actor_x+actor_w/2, first_line, parent=actor,
                     weight='bold', anchor='middle', width=actor_w-8)

        outer_x = actor_x+actor_w if left else actor_x
        boundary_x = FRAME[0] if left else FRAME[0]+FRAME[2]
        port = shared_port(figure, frame, identifier, entry['port'], boundary_x,
                    [entry['in_y'], entry['out_y']], [flow['feature'] for flow in native['flows']],
                    label_size=14)
        port_x, port_w = float(port.attrib['x']), float(port.attrib['width'])
        inner_x = port_x+port_w if left else port_x
        label_x, label_w = (132, 146) if left else (430, 136)
        for direction in ('in', 'out'):
            line_y = entry[direction+'_y']
            source, target = (outer_x, inner_x) if direction == 'in' else (inner_x, outer_x)
            flows = [flow for flow in native['flows'] if flow['direction'] == direction]
            require(flows, 'Empty directed context exchange')
            exchange = figure.el('g', data_exchange_interface=identifier,
                data_direction=direction, data_flow_ids=','.join(flow['id'] for flow in flows))
            # The upper and lower routes use different patterns, even when
            # both represent information such as authorized human decisions.
            style = 'solid' if line_y == min(entry['in_y'], entry['out_y']) else 'dotted'
            figure.arrow(f'M{source:g} {line_y} H{target:g}', exchange, style=style,
                         data_line_style=style)
            figure.lines(entry[direction+'_labels'], label_x, entry[direction+'_label_y'],
                         parent=exchange, width=label_w)
    return figure, inventory


def context_check(figure, inventory):
    """Check enclosure, external participants, coverage, ports and directions."""
    frame = figure.root.find('./{*}g[@data-system="Framework"]')
    require(frame is not None, 'Missing framework boundary')
    require(not frame.findall('.//{*}g[@data-interface]') and
            not frame.findall('.//{*}g[@data-component]'),
            'Black-box context must not show internal interface blocks or components')
    fx, fy, fw, fh = FRAME
    actors = figure.root.findall('./{*}g[@data-actor]')
    require(len(actors) == 5 and not frame.findall('.//{*}g[@data-actor]'),
            'External participant inside framework')
    actor_bounds = {}
    for actor in actors:
        box = actor.find('./{*}rect')
        x, y, w, h = [float(box.attrib[a]) for a in ('x', 'y', 'width', 'height')]
        require(x+w < fx or x > fx+fw, 'External participant overlaps framework')
        actor_bounds[actor.attrib['data-actor']] = (x, y, w, h)
    ports = frame.findall('./{*}rect[@data-port]')
    require(len(ports) == len(inventory['interfaces']) == 5 and
            len(frame.findall('.//{*}rect')) == len(ports)+1,
            'Black-box context must contain only its boundary and five shared ports')
    validate_port_labels(figure.root)
    all_flows = {flow['id']: (interface['id'], flow['direction'])
                 for interface in inventory['interfaces'] for flow in interface['flows']}
    covered = set()
    entries = {entry['id']: entry for entry in INTERFACES}
    for group in figure.root.findall('./{*}g[@data-exchange-interface]'):
        identifier, direction = group.attrib['data-exchange-interface'], group.attrib['data-direction']
        ids = set(group.attrib['data-flow-ids'].split(','))
        require(not covered.intersection(ids), 'Repeated context flow')
        require(all(all_flows.get(i) == (identifier, direction) for i in ids),
                'Mixed interface or direction in context summary')
        covered.update(ids)
        entry = entries[identifier]
        left = entry['side'] == 'left'
        ax, ay, aw, ah = actor_bounds[entry['actor']]
        matches = [port for port in ports if port.attrib['data-port'] == entry['port']]
        require(len(matches) == 1, 'Missing/duplicate shared interface port')
        port = matches[0]
        px, py, pw, ph = [float(port.attrib[a]) for a in ('x', 'y', 'width', 'height')]
        outer, inner = (ax+aw, px+pw) if left else (ax, px)
        origin, destination = (outer, inner) if direction == 'in' else (inner, outer)
        line_y = entry[direction+'_y']
        arrow = group.find('./{*}path')
        require(arrow.attrib['d'] == f'M{origin:g} {line_y} H{destination:g}'
                and arrow.attrib['data-end-marker'] == 'url(#arrow)'
                and arrow.attrib['data-terminal-head'] == 'true' and 'marker-end' not in arrow.attrib
                and ay <= line_y <= ay+ah and py <= line_y <= py+ph,
                'Disconnected/reversed context route')
        style = 'solid' if line_y == min(entry['in_y'], entry['out_y']) else 'dotted'
        require(arrow.attrib['data-line-style'] == style and
                arrow.attrib.get('stroke-dasharray') == LINE_PATTERNS[style],
                'Lost context exchange line pattern')
        require(port.attrib['data-interface'] == identifier and
                px+pw/2 == (fx if left else fx+fw) and py < line_y < py+ph,
                'Context route does not pass through its shared port')
        require(all(float(text.attrib['y']) <= line_y-8
                    for text in group.findall('./{*}text')),
                'Context exchange label overlaps its route')
        native = next(interface for interface in inventory['interfaces'] if interface['id'] == identifier)
        require(set(port.attrib['data-features'].split(',')) ==
                {flow['feature'] for flow in native['flows']}, 'Shared context port omits a flow feature')
    require(covered == set(all_flows), 'Missing context exchange coverage')
    return {'black_box_has_no_internal_interface_blocks': True, 'five_external_participants_outside': True,
            'all_17_flows_grouped_once_by_interface_and_direction': True,
            'shared_ports_and_directed_actor_boundary_endpoints_checked': True,
            'one_rectangular_port_per_interface': True,
            'distinct_neighboring_exchange_patterns': True,
            'exchange_labels_clear_their_routes': True,
            'native_model_check': 'Not performed. Illustration only.',
            'simulation_execution': 'Not performed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', required=True, type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(job != ROOT and ROOT not in job.parents, 'Check artifacts must remain outside the checkout')
    figure, inventory = create_figure()
    checks = context_check(figure, inventory)
    provenance = render_figure(figure, BASE, job)
    provenance.update(kind='Authored illustrative black-box framework context with labeled boundary ports',
        producer='framework-context.py using the shared monochrome serif diagram style',
        native_syside_render=False, executed_simulation=False,
        generator_sha256=sha(Path(__file__)), style_sha256=sha(FIG / 'diagram_style.py'),
        source_contract_status=inventory.get('source_contract_status', 'Native-derived figure inventory'),
        interface_counterparts={entry['native_id']: {
            'label': entry['id'], 'type': 'BoundaryViews::'+entry['type'],
            'framework_port': entry['port'], 'port_type': 'BoundaryViews::'+entry['port_type'],
            'external_port': entry['actor']+'.p',
            'in': [flow['feature'] for flow in entry['flows'] if flow['direction'] == 'in'],
            'out': [flow['feature'] for flow in entry['flows'] if flow['direction'] == 'out']}
            for entry in inventory['interfaces']},
        reproduction=['python3 final_report/fig/framework-context.py --jobdir /absolute/external/check-dir'])
    provenance['checks'].update(checks)
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps({'checks': provenance['checks'], 'dimensions': provenance['dimensions']}, indent=2))


if __name__ == '__main__':
    main()
