#!/usr/bin/env python3
"""Render the three-component logical architecture as two compact views.

python3 final_report/fig/logical-architecture.py --jobdir /absolute/external/check-dir
Requires Times New Roman, librsvg and Poppler. These are authored illustrations.
Requirements and allocations come from the report. No simulation is executed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from diagram_style import (Figure, LIGHT, LINE_PATTERNS, SerifMetrics,
    orthogonal_points, render_figure, require, run, sha, shared_port,
    validate_arrowheads, validate_port_labels, validate_style)

FIG = Path(__file__).resolve().parent
REPORT, ROOT = FIG.parent, FIG.parent.parent
BASE = FIG / 'logical-architecture'
W, FONT = 690, 11
CANONICAL_NAMES = {
    'L01': 'Engineering Interface',
    'L03': 'Simulation and Analysis',
    'L06': 'Configuration Management',
}
NAME_LINES = {
    'L01': ['L01 Engineering', 'Interface'],
    'L03': ['L03 Simulation', 'and Analysis'],
    'L06': ['L06 Configuration', 'Management'],
}
ACTORS = {'engineers': 'Engineers and stakeholders', 'sources': 'Knowledge and data sources',
          'tools': 'Simulation tools', 'reviewers': 'Reviewers'}
INTERFACE_SPECS = [
    ('IF-01', 'EngineeringUse', 'engineers', 'L01', [
        ('X01.1', 'engineeringSubmission', 'EngineeringSubmission', 'in'),
        ('X01.2', 'engineeringResponse', 'EngineeringResponse', 'out')]),
    ('IF-02', 'Knowledge', 'sources', 'L01', [
        ('X02.1', 'sourceSubmission', 'SourceSubmission', 'in'),
        ('X02.2', 'sourceQuery', 'SourceQuery', 'out')]),
    ('IF-03', 'Analysis', 'tools', 'L03', [
        ('X03.1', 'simulationInputs', 'SpacecraftSimulationInputs', 'out'),
        ('X03.4', 'analysisResults', 'NumericalAnalysisResults', 'in')]),
    ('IF-06', 'TechnicalReview', 'reviewers', 'L01', [
        ('X06.1', 'reviewSubmission', 'ReviewFindings', 'in'),
        ('X06.2', 'reviewResponse', 'ReviewPackage', 'out')]),
]
EXTERNAL_LABELS = {
    'X01.1': 'Expectations, mission, drafts, parameters & changes',
    'X01.2': 'Requirement checks, computed parameters & updated requirements',
    'X02.1': 'Components, parameters, models & reference data',
    'X02.2': 'Source queries',
    'X03.1': 'Spacecraft models, parameters & states',
    'X03.4': 'Numerical analysis results',
    'X06.1': 'Review findings',
    'X06.2': 'Baseline review package',
}
# Retain every producer/consumer relation. New owners determine whether each
# relation crosses a component boundary or stays inside a merged component.
LINK_GROUPS = [
    ('Requirements and allocations', [(1, 14), (17, 15)]),
    ('Mission and budget inputs', [(25, 17), (20, 17)]),
    ('Models and scenarios', [(15, 16), (25, 16), (15, 19), (15, 34), (15, 26)]),
    ('Design study results', [(16, 14), (16, 20), (27, 14)]),
    ('Calibration histories', [(16, 22)]),
    ('Estimated parameters', [(22, 15)]),
    ('Requirement views', [(1, 37), (4, 37)]),
    ('Design views', [(15, 37), (25, 37)]),
    ('Evidence gaps', [(11, 39)]),
    ('Engineering records', [(1, 7), (17, 7), (3, 7)]),
    ('Design records', [(15, 7), (25, 7), (20, 9)]),
    ('Analysis records', [(16, 9), (19, 9), (27, 9), (34, 7), (10, 7)]),
    ('Parameter records', [(22, 7), (22, 9)]),
    ('Evidence records', [(37, 7), (11, 7)]),
    ('Current engineering basis', [(7, 1), (5, 1), (7, 3), (7, 39)]),
    ('Analysis inputs', [(9, 10)]),
    ('Design basis', [(7, 15), (5, 15)]),
    ('Model basis', [(7, 22)]),
    ('Evidence basis', [(7, 37), (9, 11)]),
]
PEER_SPECS = [
    ('E01', 'engineeringAnalysisInputs', 'L01', 'L03', 'information'),
    ('E02', 'analysisResponses', 'L03', 'L01', 'information'),
    ('E03', 'engineeringRecords', 'L01', 'L06', 'information'),
    ('E04', 'analysisRecords', 'L03', 'L06', 'information'),
    ('E05', 'engineeringContext', 'L06', 'L01', 'control'),
    ('E06', 'controlledAnalysisInputs', 'L06', 'L03', 'control'),
]
PEER_LABELS = {
    'E01': ['Models, mission inputs', '& analysis requests'],
    'E02': ['Results, budgets', '& run histories'],
    'E03': ['Engineering records', '& change requests'],
    'E04': ['Analysis, mapping', '& reconstruction records'],
    'E05': ['Current baselines', '& change impacts'],
    'E06': ['Controlled inputs', '& dependencies'],
}
BOUNDARY_ROUTES = [
    ('requirementSubmission', 'IF-01', 'in', 'L01', [1], None),
    ('missionSubmission', 'IF-01', 'in', 'L01', [25], None),
    ('designSubmission', 'IF-01', 'in', 'L01', [15], None),
    ('changeSubmission', 'IF-01', 'in', 'L06', [5], 'E03'),
    ('guidanceResponse', 'IF-01', 'out', 'L01', [1, 2, 3], None),
    ('referenceSubmission', 'IF-02', 'in', 'L01', [22], None),
    ('sourceMethods', 'IF-02', 'in', 'L01', [3], None),
    ('componentProperties', 'IF-02', 'in', 'L03', [13], 'E01'),
    ('boundedSourceQuery', 'IF-02', 'out', 'L01', [3, 13], None),
]
PEER_GEOMETRY = {
    'E01': ('M248 103 H442', 263, 78, 164),
    'E02': ('M442 134 H248', 263, 159, 164),
    'E03': ('M50 150 V270', 61, 185, 145),
    'E04': ('M474 150 V270', 487, 185, 143),
    'E05': ('M216 270 V150', 61, 235, 145),
    'E06': ('M640 270 V150', 487, 235, 143),
}
PEER_BOXES = {'L01': (18, 80, 230, 70), 'L03': (442, 80, 230, 70),
              'L06': (18, 270, 654, 46)}
BOUNDARY_FRAME = (258, 49, 174, 365)
BOUNDARY_BOXES = {'L01': (268, 80, 154, 233), 'L03': (268, 338, 154, 65)}
ACTOR_BOXES = {'engineers': (8, 80, 112, 200), 'sources': (578, 80, 104, 150),
               'reviewers': (578, 247, 104, 65), 'tools': (8, 328, 112, 75)}
FLOW_LEVELS = {'X01.1': 140, 'X01.2': 260, 'X02.1': 140, 'X02.2': 220,
               'X03.1': 350, 'X03.4': 390, 'X06.1': 255, 'X06.2': 305}


def report_allocations():
    requirements = set(re.findall(r'^(FR-\d\d) &',
                                 (REPORT / 'requirements.tex').read_text(), re.M))
    allocations = {}
    for cid, name, numbers in re.findall(r'^(L\d\d) ([^&]+) & ([^&]+) &',
                                        (REPORT / 'logical.tex').read_text(), re.M):
        require(cid in CANONICAL_NAMES and name.strip() == CANONICAL_NAMES[cid],
                'Report component name differs from diagram')
        assigned = []
        for token in numbers.split(','):
            match = re.fullmatch(r'\s*(\d\d)(?:--(\d\d))?\s*', token)
            require(match, 'Invalid FR allocation: '+token)
            assigned.extend(f'FR-{number:02}'
                            for number in range(int(match[1]), int(match[2] or match[1])+1))
        allocations[cid] = assigned
    assigned = [fr for values in allocations.values() for fr in values]
    require(set(allocations) == set(CANONICAL_NAMES) and
            len(assigned) == len(set(assigned)) and set(assigned) == requirements,
            'Logical allocation must cover each current requirement exactly once')
    return requirements, allocations


def inventory_counts(inv):
    return {'framework_requirements': len(inv['requirements']),
            'logical_components': len(inv['components']),
            'peer_exchange_groups': len(inv['peer_exchanges']),
            'peer_requirement_links': sum(len(e['mappings']) for e in inv['peer_exchanges']),
            'internal_requirement_links': len(inv['internal_exchanges']),
            'black_box_interfaces': len(inv['interfaces']),
            'black_box_directed_flows': sum(len(i['flows']) for i in inv['interfaces']),
            'boundary_refinement_routes': len(inv['boundary_routes'])}


def inventory():
    requirements, allocations = report_allocations()
    owners = {fr: cid for cid, assigned in allocations.items() for fr in assigned}
    peers = [dict(id=identifier, name=name, source_component=source,
                  target_component=target, kind=kind, mappings=[])
             for identifier, name, source, target, kind in PEER_SPECS]
    by_pair = {(e['source_component'], e['target_component']): e for e in peers}
    internal = []
    for meaning, pairs in LINK_GROUPS:
        for producer, consumer in pairs:
            source, target = f'FR-{producer:02}', f'FR-{consumer:02}'
            require(source in owners and target in owners, 'Removed requirement in exchange')
            mapping = dict(source_requirement=source, target_requirement=target, mapping=meaning)
            if owners[source] == owners[target]:
                internal.append(dict(mapping, component=owners[source]))
            else:
                by_pair[(owners[source], owners[target])]['mappings'].append(mapping)
    interfaces = []
    for identifier, typ, actor, component, specs in INTERFACE_SPECS:
        port = 'p'+identifier[-2:]
        flows = []
        for fid, feature, payload, direction in specs:
            actor_endpoint, framework_endpoint = f'{actor}.p.{feature}', f'framework.{port}.{feature}'
            source, target = ((actor_endpoint, framework_endpoint) if direction == 'in'
                              else (framework_endpoint, actor_endpoint))
            flows.append(dict(id=fid, name=feature, feature=feature, type=payload,
                              qualified_type=payload, source=source, target=target,
                              direction=direction, kind='information'))
        interfaces.append(dict(id=identifier, native_id=identifier.replace('-', ''),
            type=typ+'Interface', port=port, port_type=typ+'Port', actor=actor,
            actor_label=ACTORS[actor], component=component,
            delegation=component+'.'+port, flows=flows))
    routes = [dict(id=f'B{number:02}', name=name, interface=interface, direction=direction,
                   component=component, fr_basis=[f'FR-{fr:02}' for fr in basis],
                   via_exchange=via)
              for number, (name, interface, direction, component, basis, via)
              in enumerate(BOUNDARY_ROUTES, 1)]
    inv = dict(schema=5, requirements=sorted(requirements),
        components=[dict(id=cid, name=name, requirements=allocations[cid])
                    for cid, name in CANONICAL_NAMES.items()],
        peer_exchanges=peers, internal_exchanges=internal, interfaces=interfaces,
        boundary_routes=routes,
        source_contract_status='Authored report illustration. No native model validation or simulation.',
        report_source_sha256={str(p.relative_to(ROOT)): sha(p)
                              for p in (REPORT / 'requirements.tex', REPORT / 'logical.tex')})
    inv['counts'] = inventory_counts(inv)
    inventory_check(inv)
    return inv


def inventory_check(inv):
    requirements, allocations = report_allocations()
    require({c['id']: c['name'] for c in inv['components']} == CANONICAL_NAMES,
            'Canonical component name mismatch')
    require({c['id']: c['requirements'] for c in inv['components']} == allocations and
            set(inv['requirements']) == requirements, 'Diagram FR allocations differ from report')
    require(inv['counts'] == inventory_counts(inv), 'Report diagram coverage mismatch')
    expected = {s[0]: s[1:] for s in PEER_SPECS}
    require(len(inv['peer_exchanges']) == len(expected) and
            {e['id'] for e in inv['peer_exchanges']} == set(expected), 'Missing/extra peer exchange')
    covered = []
    for exchange in inv['peer_exchanges']:
        actual = tuple(exchange[key] for key in ('name', 'source_component', 'target_component', 'kind'))
        require(actual == expected[exchange['id']] and exchange['mappings'], 'Changed peer exchange')
        for mapping in exchange['mappings']:
            require(mapping['source_requirement'] in allocations[exchange['source_component']] and
                    mapping['target_requirement'] in allocations[exchange['target_component']],
                    'Removed or misallocated requirement in peer exchange')
            covered.append((mapping['source_requirement'], mapping['target_requirement']))
    for mapping in inv['internal_exchanges']:
        require(mapping['component'] in allocations and
                mapping['source_requirement'] in allocations[mapping['component']] and
                mapping['target_requirement'] in allocations[mapping['component']],
                'Misallocated internal exchange')
        covered.append((mapping['source_requirement'], mapping['target_requirement']))
    original = [(f'FR-{source:02}', f'FR-{target:02}')
                for _, pairs in LINK_GROUPS for source, target in pairs]
    require(Counter(covered) == Counter(original), 'Lost or duplicated producer/consumer relation')
    declared = set(re.findall(r'\\item\[(IF-\d\d):', (REPORT / 'requirements.tex').read_text()))
    by_interface = {i['id']: i for i in inv['interfaces']}
    require(set(by_interface) == declared == {s[0] for s in INTERFACE_SPECS}, 'Changed external interfaces')
    for identifier, typ, actor, component, specs in INTERFACE_SPECS:
        interface = by_interface[identifier]
        require(interface['component'] == component and interface['actor'] == actor and
                interface['delegation'] == component+'.'+interface['port'], 'Changed interface ownership')
        require([(f['id'], f['feature'], f['type'], f['direction']) for f in interface['flows']] == specs,
                'Changed external flow definition')
    require(len(inv['boundary_routes']) == len(BOUNDARY_ROUTES), 'Missing boundary refinement')
    peer_by_id = {e['id']: e for e in inv['peer_exchanges']}
    for route in inv['boundary_routes']:
        require(route['fr_basis'] and set(route['fr_basis']) <= requirements,
                'Removed requirement in boundary refinement')
        interface = by_interface[route['interface']]
        if route['via_exchange']:
            peer = peer_by_id[route['via_exchange']]
            require(route['direction'] == 'in' and peer['source_component'] == interface['component'] and
                    peer['target_component'] == route['component'], 'Disconnected boundary refinement')
        else:
            require(route['component'] == interface['component'], 'Wrong direct boundary owner')


def information_style(identifier):
    if identifier in ('E05', 'E06'):
        return 'dashed'
    if identifier == 'E04':
        return 'dashdot'
    return 'dotted' if identifier in ('E02', 'X01.2', 'X02.2', 'X03.4', 'X06.2') else 'solid'


def path_points(d):
    return orthogonal_points(d)


def bounds(rect):
    return tuple(float(rect.attrib[key]) for key in ('x', 'y', 'width', 'height'))


def within(point, box):
    x, y, width, height = box
    return x-.1 <= point[0] <= x+width+.1 and y-.1 <= point[1] <= y+height+.1


def on_edge(point, box):
    x, y, width, height = box
    return within(point, box) and min(abs(point[0]-x), abs(point[0]-x-width),
                                    abs(point[1]-y), abs(point[1]-y-height)) < .1


def wrapped(figure, value, width):
    lines = ['']
    for word in value.split():
        candidate = (lines[-1]+' '+word).strip()
        if figure.metrics.measure(candidate, FONT) > width:
            require(lines[-1], 'Word exceeds exchange label region: '+word)
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def framework(figure, box):
    group = figure.el('g', data_system='Framework')
    figure.rect(*box, group, data_enclosure='Framework')
    figure.text('Framework', box[0]+8, box[1]+15, size=12, weight='bold', parent=group)
    return group


def component_box(figure, parent, cid, box):
    group = figure.el('g', parent, data_component=cid)
    figure.rect(*box, group)
    labels = NAME_LINES[cid]
    x, y, width, height = box
    first = y+(height-14*(len(labels)-1))/2+4
    figure.lines(labels, x+width/2, first, leading=14, size=12, weight='bold',
                 anchor='middle', width=width-16, parent=group)


def arrow(figure, group, identifier, d):
    style = information_style(identifier)
    return figure.arrow(d, group, id='arrow-'+identifier, style=style, data_line_style=style)


def internal_page(inv, metrics=None):
    figure = Figure('Logical architecture: component cooperation', W, 330, metrics)
    figure.text('Logical architecture: component cooperation', 8, 20, size=16, weight='bold')
    frame = framework(figure, (8, 49, 674, 273))
    for cid, box in PEER_BOXES.items():
        component_box(figure, frame, cid, box)
    for exchange in inv['peer_exchanges']:
        identifier = exchange['id']
        d, x, y, width = PEER_GEOMETRY[identifier]
        group = figure.el('g', frame, id=identifier, data_exchange=exchange['name'],
                          data_source=exchange['source_component'],
                          data_target=exchange['target_component'], data_kind=exchange['kind'])
        arrow(figure, group, identifier, d)
        figure.lines(PEER_LABELS[identifier], x, y, leading=12, size=FONT, width=width, parent=group)
    return figure


def external_geometry(identifier, direction):
    interface_id = 'IF-'+identifier[1:3]
    _, _, actor, cid, _ = next(spec for spec in INTERFACE_SPECS if spec[0] == interface_id)
    ax, _, aw, _ = ACTOR_BOXES[actor]
    cx, _, cw, _ = BOUNDARY_BOXES[cid]
    left = actor in ('engineers', 'tools')
    outside, inside = (ax+aw, cx) if left else (ax, cx+cw)
    start, end = (outside, inside) if direction == 'in' else (inside, outside)
    return f'M{start:g} {FLOW_LEVELS[identifier]} H{end:g}'


def boundary_page(inv, metrics=None):
    figure = Figure('Logical architecture: external interfaces', W, 420, metrics)
    figure.text('Logical architecture: external interfaces', 8, 20, size=16, weight='bold')
    frame = framework(figure, BOUNDARY_FRAME)
    for cid, box in BOUNDARY_BOXES.items():
        component_box(figure, frame, cid, box)
    actor_lines = {'engineers': ['Engineers and', 'stakeholders'],
                   'sources': ['Knowledge and', 'data sources'],
                   'reviewers': ['Reviewers'], 'tools': ['Simulation', 'tools']}
    for actor, box in ACTOR_BOXES.items():
        group = figure.el('g', data_actor=actor)
        figure.rect(*box, group, fill=LIGHT)
        x, y, width, height = box
        labels = actor_lines[actor]
        first = y+(height-12*(len(labels)-1))/2+4
        figure.lines(labels, x+width/2, first, leading=12, size=FONT, weight='bold',
                     anchor='middle', width=width-8, parent=group)
    for interface in inv['interfaces']:
        left = interface['actor'] in ('engineers', 'tools')
        boundary_x = BOUNDARY_FRAME[0] if left else BOUNDARY_FRAME[0]+BOUNDARY_FRAME[2]
        shared_port(figure, frame, interface['id'], interface['port'], boundary_x,
                    [FLOW_LEVELS[f['id']] for f in interface['flows']],
                    [f['feature'] for f in interface['flows']])
        x, width = (132, 106) if left else (450, 114)
        for flow in interface['flows']:
            group = figure.el('g', id=flow['id'], data_flow=flow['name'],
                data_source=flow['source'], data_target=flow['target'], data_kind='information',
                data_interface=interface['id'], data_component_endpoint=interface['component'],
                data_delegation=interface['delegation'])
            arrow(figure, group, flow['id'], external_geometry(flow['id'], flow['direction']))
            labels = wrapped(figure, EXTERNAL_LABELS[flow['id']], width)
            y = FLOW_LEVELS[flow['id']]-8-12*(len(labels)-1)
            figure.lines(labels, x, y, leading=12, size=FONT, width=width, parent=group)
    return figure


def exchange_label_check(root, metrics):
    """Keep boundary exchange labels clear of their port, actor and route."""
    for identifier, _, actor, _, flows in INTERFACE_SPECS:
        port = root.find(f'.//{{*}}rect[@data-interface="{identifier}"][@data-port]')
        actor_rect = root.find(f'./{{*}}g[@data-actor="{actor}"]/{{*}}rect')
        require(port is not None and actor_rect is not None, 'Missing boundary port or actor')
        px, _, pw, _ = bounds(port)
        ax, _, aw, _ = bounds(actor_rect)
        left, right = ((ax+aw+.4, px-.4) if actor in ('engineers', 'tools')
                       else (px+pw+.4, ax-.4))
        for fid, _, _, _ in flows:
            group = root.find(f'./{{*}}g[@id="{fid}"]')
            require(group is not None, 'Missing boundary exchange')
            for text in group.findall('./{*}text'):
                size = float(text.attrib['font-size'])
                require(size >= FONT and 'transform' not in text.attrib, 'Unreadable exchange label')
                x = float(text.attrib['x'])
                width = metrics.measure(text.text or '', size)
                require(x-left >= 6-1e-6 and right-x-width >= 6-1e-6,
                        'Exchange label does not clear port or actor: '+fid)
                require(float(text.attrib['y']) <= FLOW_LEVELS[fid]-8,
                        'Exchange label overlaps its route: '+fid)
    return {'boundary_exchange_label_clearance_checked': True}


def display_check(inv, paths, metrics=None):
    inventory_check(inv)
    metrics = metrics or SerifMetrics()
    roots = [ET.parse(path).getroot() for path in paths]
    require(len(roots) == 2, 'Expected two coordinated architecture views')
    components = {}
    for page, root in enumerate(roots, 1):
        validate_style(root)
        validate_arrowheads(root)
        validate_port_labels(root)
        frame = root.find('./{*}g[@data-system="Framework"]')
        require(frame is not None and not frame.findall('.//{*}g[@data-actor]'),
                'Missing Framework containment or internal external participant')
        enclosure = bounds(frame.find('./{*}rect[@data-enclosure="Framework"]'))
        for group in frame.findall('./{*}g[@data-component]'):
            cid = group.attrib['data-component']
            require(cid in CANONICAL_NAMES, 'Removed component in diagram')
            labels = ' '.join(text.text or '' for text in group.findall('./{*}text'))
            require(labels == cid+' '+CANONICAL_NAMES[cid], 'Changed component name')
            box = bounds(group.find('./{*}rect'))
            require(within((box[0], box[1]), enclosure) and
                    within((box[0]+box[2], box[1]+box[3]), enclosure), 'Component outside Framework')
            require((page, cid) not in components, 'Duplicate component occurrence')
            components[(page, cid)] = box
        expected_ports = 0 if page == 1 else 4
        ports = root.findall('.//{*}rect[@data-port]')
        require(len(ports) == expected_ports and
                len({p.attrib['data-interface'] for p in ports}) == expected_ports,
                'Expected one shared rectangle per interface')
    require({cid for page, cid in components if page == 1} == set(CANONICAL_NAMES),
            'Missing component responsibility')
    peer_groups = {g.attrib['id']: g for g in roots[0].findall('.//{*}g[@data-exchange]')}
    require(set(peer_groups) == {e['id'] for e in inv['peer_exchanges']}, 'Missing/extra peer route')
    for exchange in inv['peer_exchanges']:
        group = peer_groups[exchange['id']]
        for attribute, key in (('source', 'source_component'), ('target', 'target_component'), ('kind', 'kind')):
            require(group.attrib['data-'+attribute] == exchange[key], 'Changed peer endpoint or kind')
        path = group.find('./{*}path')
        points = path_points(path.attrib['d'])
        require(path.attrib['d'] == PEER_GEOMETRY[exchange['id']][0] and
                on_edge(points[0], components[(1, exchange['source_component'])]) and
                on_edge(points[-1], components[(1, exchange['target_component'])]),
                'Reversed/disconnected peer route: '+exchange['id'])
        style = information_style(exchange['id'])
        require(path.attrib.get('stroke-dasharray') == LINE_PATTERNS[style], 'Changed peer line style')
        require([t.text for t in group.findall('./{*}text')] == PEER_LABELS[exchange['id']],
                'Changed peer exchange label')
        exchange['display'] = dict(page=1, arrow=path.attrib['id'], label=' '.join(PEER_LABELS[exchange['id']]))
    flow_groups = {g.attrib['id']: g for g in roots[1].findall('./{*}g[@data-flow]')}
    require(set(flow_groups) == set(EXTERNAL_LABELS), 'Missing/extra external flow')
    for interface in inv['interfaces']:
        actor_group = roots[1].find(f'./{{*}}g[@data-actor="{interface["actor"]}"]')
        require(actor_group is not None and
                ' '.join(t.text or '' for t in actor_group.findall('./{*}text')) == interface['actor_label'],
                'Changed external participant')
        actor = bounds(actor_group.find('./{*}rect'))
        fx, fy, fw, fh = BOUNDARY_FRAME
        require(actor[0]+actor[2] < fx or actor[0] > fx+fw, 'External actor overlaps Framework')
        for flow in interface['flows']:
            group = flow_groups[flow['id']]
            require(group.attrib['data-delegation'] == interface['delegation'] and
                    group.attrib['data-component-endpoint'] == interface['component'] and
                    group.attrib['data-source'] == flow['source'] and
                    group.attrib['data-target'] == flow['target'], 'Changed external delegation')
            path = group.find('./{*}path')
            require(path.attrib['d'] == external_geometry(flow['id'], flow['direction']),
                    'Reversed/disconnected external route')
            points = path_points(path.attrib['d'])
            outside, inside = ((points[0], points[-1]) if flow['direction'] == 'in'
                               else (points[-1], points[0]))
            require(on_edge(outside, actor) and on_edge(inside, components[(2, interface['component'])]),
                    'External route does not reach its actor and component')
            port = roots[1].find(f'.//{{*}}rect[@data-interface="{interface["id"]}"][@data-port]')
            px, py, pw, ph = bounds(port)
            _, cy, _, ch = components[(2, interface['component'])]
            require(cy <= py and py+ph <= cy+ch, 'Boundary port extends beyond its owning component')
            crossing = (float(port.attrib['data-boundary-x']), FLOW_LEVELS[flow['id']])
            require(on_edge(crossing, BOUNDARY_FRAME) and within(crossing, bounds(port)) and
                    min(points[0][0], points[-1][0]) <= crossing[0] <= max(points[0][0], points[-1][0]),
                    'External route misses its shared port')
            require(' '.join(t.text or '' for t in group.findall('./{*}text')) == EXTERNAL_LABELS[flow['id']],
                    'Changed external exchange label')
            flow['display'] = dict(page=2, arrow=path.attrib['id'],
                                   component=interface['component'], boundary_port_crossing=list(crossing))
    caption = (REPORT / 'logical.tex').read_text()
    require('Engineers authorize baseline decisions.' in caption and
            'Record retention confers no engineering approval.' in caption,
            'Missing engineering authority note')
    return {**exchange_label_check(roots[1], metrics),
        'three_components_checked': True, 'all_six_peer_exchanges_displayed': True,
        'all_internal_requirement_relations_retained': True,
        'all_eight_external_flows_displayed': True, 'all_four_shared_ports_checked': True,
        'component_names_containment_and_directed_endpoints_checked': True,
        'terminal_heads_skip_intermediate_ports': True}


def normalize_document_id(path):
    data = path.read_bytes()
    pattern = rb'/ID\s*\[(?:\((?:\\.|[^\\)])*\)\s*){2}\]'
    matches = list(re.finditer(pattern, data, re.S))
    require(len(matches) == 1, 'Expected one Poppler trailer document ID')
    match = matches[0]
    digest = hashlib.sha256(data[:match.start()]+data[match.end():]).hexdigest()[:32].encode()
    path.write_bytes(data[:match.start()]+b'/ID [<'+digest+b'> <'+digest+b'>]'+data[match.end():])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', type=Path, required=True)
    parser.add_argument('--coverage', type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(job != ROOT and ROOT not in job.parents, 'Check artifacts must remain outside the checkout')
    metrics, inv = SerifMetrics(), inventory()
    figures = [internal_page(inv, metrics), boundary_page(inv, metrics)]
    paths, pdfs, artifacts, renderings = [], [], {}, []
    for index, figure in enumerate(figures, 1):
        stem = BASE if index == 1 else BASE.with_name(BASE.name+'-panel-02')
        rendering = render_figure(figure, stem, job)
        renderings.append(rendering)
        svg, pdf = stem.with_suffix('.svg'), stem.with_suffix('.pdf')
        if index == 1:
            overview = BASE.with_name(BASE.name+'-overview.pdf')
            overview.write_bytes(pdf.read_bytes())
            pdf = overview
        paths.append(svg)
        pdfs.append(pdf)
        for path in (svg, stem.with_suffix('.png'), pdf):
            artifacts[path.name] = sha(path)
    run(['pdfunite', *map(str, pdfs), str(BASE.with_suffix('.pdf'))])
    normalize_document_id(BASE.with_suffix('.pdf'))
    checks = display_check(inv, paths, metrics)
    for rendering in renderings:
        checks.update(rendering['checks'])
    checks.update(pdf_pages=2, native_semantic_validation='Not performed. Authored report illustration.')
    inv.update(checks=checks, generator_sha256=sha(Path(__file__)), style_sha256=sha(FIG / 'diagram_style.py'),
               panels=[dict(page=number, svg=str(path.relative_to(ROOT)))
                       for number, path in enumerate(paths, 1)],
               semantics='Three logical components. Merged producer/consumer relations remain internal. '
                         'Information uses solid, dotted and dash-dot routes. L06 control uses dashed routes.')
    BASE.with_suffix('.inventory.json').write_text(json.dumps(inv, indent=2)+'\n')
    if args.coverage:
        args.coverage.resolve().write_text(json.dumps(inv, indent=2)+'\n')
    artifacts[BASE.with_suffix('.pdf').name] = sha(BASE.with_suffix('.pdf'))
    provenance = dict(artifact='logical-architecture', kind='Authored illustrative logical architecture',
        producer='logical-architecture.py, three components and two coordinated views',
        native_syside_render=False, executed_simulation=False,
        basis=inv['source_contract_status'], inventory=BASE.with_suffix('.inventory.json').name,
        counts=inv['counts'], checks=checks, dimensions={'panels_pt': [[f.width, f.height] for f in figures], 'pdf_pages': 2},
        font=metrics.provenance(), generator_sha256=inv['generator_sha256'], style_sha256=inv['style_sha256'],
        report_source_sha256=inv['report_source_sha256'],
        artifact_sha256={kind: sha(BASE.with_suffix('.'+kind)) for kind in ('svg', 'pdf', 'png')},
        coordinated_panel_sha256=artifacts,
        reproduction=['python3 final_report/fig/logical-architecture.py --jobdir /absolute/external/check-dir'])
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps({'counts': inv['counts'], 'checks': checks}, indent=2))


if __name__ == '__main__':
    main()
