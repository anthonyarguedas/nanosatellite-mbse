#!/usr/bin/env python3
"""Render the report's four logical components and users in one view.

python3 final_report/fig/logical-architecture.py --jobdir /absolute/external/check-dir
Requires Times New Roman, librsvg and Poppler. SVG and PNG checks stay in jobdir.
The published PDF is an authored illustration. No simulation is executed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
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
W, H, FONT = 760, 620, 12
CANONICAL_NAMES = {
    'L01': 'MBSE Workspace',
    'L02': 'COTS Database',
    'L03': 'Simulation and Analysis',
    'L04': 'Configuration Management',
}
NAME_LINES = {
    'L01': ['L01 MBSE', 'Workspace'],
    'L02': ['L02 COTS', 'Database'],
    'L03': ['L03 Simulation', 'and Analysis'],
    'L04': ['L04 Configuration', 'Management'],
}
FRAME = (230, 35, 522, 577)
COMPONENT_BOXES = {
    'L01': (260, 75, 150, 120),
    'L02': (600, 75, 142, 120),
    'L03': (600, 335, 142, 105),
    'L04': (260, 480, 150, 120),
}
USER_BOX = (10, 265, 65, 80)


def exchange(identifier, name, source, target, path, labels, x, y, width,
             style='solid'):
    return dict(id=identifier, name=name, source=source, target=target,
                kind='information', path=path, labels=labels,
                label_region=[x, y, width], line_style=style, page=1)


PEER_EXCHANGES = [
    exchange('E01', 'cotsParameterLinkRequests', 'L01', 'L02', 'M410 100 H600',
             ['COTS parameter', 'link requests'], 427, 80, 159),
    exchange('E02', 'cotsParameterIdentifiers', 'L02', 'L01', 'M600 140 H410',
             ['COTS parameter', 'identifiers'], 427, 120, 159, 'dotted'),
    exchange('E03', 'computationInputs', 'L01', 'L03', 'M410 165 H465 V365 H600',
             ['MBSE models,', 'parameters, states', '& computation', 'requests'],
             480, 313, 108),
    exchange('E04', 'numericalResultIdentifiers', 'L03', 'L01',
             'M600 420 H445 V185 H410', ['Numerical result', 'identifiers'],
             480, 393, 108, 'dotted'),
    exchange('E05', 'linkedCotsParameterRequests', 'L03', 'L02', 'M616 335 V195',
             ['Linked COTS', 'parameter', 'requests'], 630, 235, 88),
    exchange('E06', 'cotsParameterValues', 'L02', 'L03', 'M730 195 V335',
             ['COTS parameter', 'values'], 630, 294, 88, 'dotted'),
    exchange('E07', 'changeRequests', 'L04', 'L01', 'M275 480 V195',
             ['Change', 'requests'], 288, 245, 97),
    exchange('E08', 'engineeringRecordsAndImpactFindings', 'L01', 'L04',
             'M395 195 V480', ['Engineering records', '& impact findings'],
             284, 437, 105, 'dashdot'),
]
INTERFACES = [
    dict(id='IF-01', name='Engineering use', actor='users', component='L01',
         port='p01', flows=[
             dict(exchange('X01.1', 'engineeringSubmission', 'users', 'L01',
                           'M25 265 V110 H260', ['Requirements &', 'parameters'],
                           90, 89, 125), direction='in'),
             dict(exchange('X01.2', 'engineeringResponse', 'L01', 'users',
                           'M260 175 H60 V265',
                           ['Validity checks,', 'computed values,',
                            'updated requirements', '& next activity'],
                           90, 128, 125, 'dotted'), direction='out'),
         ]),
    dict(id='IF-02', name='Configuration management', actor='users', component='L04',
         port='p02', flows=[
             dict(exchange('X02.1', 'configurationSubmission', 'users', 'L04',
                           'M60 345 V520 H260',
                           ['Change & history', 'requests, authorized', 'decisions'],
                           90, 486, 125), direction='in'),
             dict(exchange('X02.2', 'configurationResponse', 'L04', 'users',
                           'M260 580 H25 V345',
                           ['Impact findings,', 'revision histories', '& baselines'],
                           90, 546, 125, 'dotted'), direction='out'),
         ]),
]


def report_allocations():
    requirements = set(re.findall(r'^(FR-\d\d) &',
                                 (REPORT / 'requirements.tex').read_text(), re.M))
    allocations = {}
    for cid, name, numbers in re.findall(r'^(L\d\d) ([^&]+) & ([^&]+) &',
                                        (REPORT / 'logical.tex').read_text(), re.M):
        require(cid in CANONICAL_NAMES and name.strip() == CANONICAL_NAMES[cid],
                'Report component name differs from diagram')
        require(cid not in allocations, 'Duplicate logical component')
        assigned = []
        for token in numbers.split(','):
            match = re.fullmatch(r'\s*(\d\d)(?:--(\d\d))?\s*', token)
            require(match, 'Invalid FR allocation: '+token)
            first, last = int(match[1]), int(match[2] or match[1])
            require(first <= last, 'Reversed FR allocation: '+token)
            assigned.extend(f'FR-{number:02}' for number in range(first, last+1))
        allocations[cid] = assigned
    assigned = [fr for values in allocations.values() for fr in values]
    require(set(allocations) == set(CANONICAL_NAMES) and
            Counter(assigned) == Counter(requirements),
            'Logical allocation must cover each current requirement exactly once')
    return requirements, allocations


def requirement_label(requirements):
    numbers = sorted(int(fr[-2:]) for fr in requirements)
    ranges = []
    for number in numbers:
        if ranges and number == ranges[-1][-1]+1:
            ranges[-1].append(number)
        else:
            ranges.append([number])
    return 'FR-'+', '.join(f'{group[0]:02}' if len(group) == 1
                          else f'{group[0]:02}\u2013{group[-1]:02}' for group in ranges)


def inventory_counts(inv):
    return dict(framework_requirements=len(inv['requirements']),
                logical_components=len(inv['components']),
                peer_exchange_groups=len(inv['peer_exchanges']),
                external_interfaces=len(inv['interfaces']),
                external_directed_flows=sum(len(i['flows']) for i in inv['interfaces']))


def inventory():
    requirements, allocations = report_allocations()
    inv = dict(schema=6, requirements=sorted(requirements),
        components=[dict(id=cid, name=name, requirements=allocations[cid])
                    for cid, name in CANONICAL_NAMES.items()],
        actors=[dict(id='users', name='Users')],
        peer_exchanges=copy.deepcopy(PEER_EXCHANGES), interfaces=copy.deepcopy(INTERFACES),
        panels=[dict(page=1)],
        source_contract_status='Authored report illustration. No simulation is executed.',
        report_source_sha256={str(p.relative_to(ROOT)): sha(p)
                              for p in (REPORT / 'requirements.tex', REPORT / 'logical.tex')})
    inv['counts'] = inventory_counts(inv)
    inventory_check(inv)
    return inv


def inventory_check(inv):
    requirements, allocations = report_allocations()
    require({c['id']: c['name'] for c in inv['components']} == CANONICAL_NAMES and
            len(inv['components']) == len(CANONICAL_NAMES), 'Canonical component name mismatch')
    require({c['id']: c['requirements'] for c in inv['components']} == allocations and
            inv['requirements'] == sorted(requirements), 'Diagram FR allocations differ from report')
    require(inv['actors'] == [dict(id='users', name='Users')], 'Only users are external')
    require(inv['peer_exchanges'] == PEER_EXCHANGES, 'Changed internal exchange')
    require(inv['interfaces'] == INTERFACES, 'Changed user interface')
    require(inv['panels'] == [dict(page=1)], 'Expected one architecture view')
    require(inv['counts'] == inventory_counts(inv), 'Diagram coverage mismatch')


def bounds(rect):
    return tuple(float(rect.attrib[key]) for key in ('x', 'y', 'width', 'height'))


def within(point, box):
    x, y, width, height = box
    return x-.1 <= point[0] <= x+width+.1 and y-.1 <= point[1] <= y+height+.1


def on_edge(point, box):
    x, y, width, height = box
    return within(point, box) and min(abs(point[0]-x), abs(point[0]-x-width),
                                    abs(point[1]-y), abs(point[1]-y-height)) < .1


def path_points(d):
    return orthogonal_points(d)


def all_exchanges(inv):
    return inv['peer_exchanges']+[flow for i in inv['interfaces'] for flow in i['flows']]


def create_figure(inv, metrics=None):
    figure = Figure('Logical architecture', W, H, metrics)
    frame = figure.el('g', data_system='Framework')
    figure.rect(*FRAME, frame, data_enclosure='Framework')
    figure.text('Framework', FRAME[0]+12, FRAME[1]+20,
                size=13, weight='bold', parent=frame)
    for component in inv['components']:
        cid = component['id']
        group = figure.el('g', frame, data_component=cid)
        box = COMPONENT_BOXES[cid]
        figure.rect(*box, group)
        x, y, width, height = box
        first = y+height/2-12
        figure.lines(NAME_LINES[cid], x+width/2, first, leading=15,
                     size=13, weight='bold', anchor='middle', width=width-16, parent=group)
        figure.text(requirement_label(component['requirements']), x+width/2, first+38,
                    size=11, anchor='middle', width=width-16, parent=group,
                    data_requirements=cid)
    actor = figure.el('g', data_actor='users')
    figure.rect(*USER_BOX, actor, fill=LIGHT)
    figure.text('Users', USER_BOX[0]+USER_BOX[2]/2, USER_BOX[1]+USER_BOX[3]/2+4,
                size=13, weight='bold', anchor='middle', parent=actor)
    for interface in inv['interfaces']:
        levels = [next(point[1] for point in path_points(flow['path'])
                       if point[0] == COMPONENT_BOXES[interface['component']][0])
                  for flow in interface['flows']]
        shared_port(figure, frame, interface['id'], interface['port'], FRAME[0],
                    levels, [flow['name'] for flow in interface['flows']], label_size=12)
    for item in all_exchanges(inv):
        external = item['source'] == 'users' or item['target'] == 'users'
        group = figure.el('g', None if external else frame, id=item['id'],
                          data_source=item['source'], data_target=item['target'],
                          data_kind=item['kind'],
                          **{'data_flow' if external else 'data_exchange': item['name']})
        if external:
            interface = next(i for i in inv['interfaces'] if item in i['flows'])
            group.set('data-interface', interface['id'])
            group.set('data-component-endpoint', interface['component'])
        figure.arrow(item['path'], group, id='arrow-'+item['id'],
                     style=item['line_style'], data_line_style=item['line_style'])
        x, y, width = item['label_region']
        figure.lines(item['labels'], x, y, leading=13, size=FONT, width=width, parent=group)
    return figure


def segments_intersect(a, b):
    (ax, ay), (bx, by) = a
    (cx, cy), (dx, dy) = b
    if ay == by and cy == dy:
        return ay == cy and max(min(ax, bx), min(cx, dx)) <= min(max(ax, bx), max(cx, dx))
    if ax == bx and cx == dx:
        return ax == cx and max(min(ay, by), min(cy, dy)) <= min(max(ay, by), max(cy, dy))
    if ax == bx:
        return segments_intersect(b, a)
    return min(ax, bx) <= cx <= max(ax, bx) and min(cy, dy) <= ay <= max(cy, dy)


def layout_check(root, metrics):
    routes = []
    for path in root.findall('.//{*}path[@data-terminal-head="true"]'):
        points = path_points(path.attrib['d'])
        routes.append((path.attrib['id'], list(zip(points, points[1:]))))
    for index, (identifier, segments) in enumerate(routes):
        for other, other_segments in routes[index+1:]:
            require(not any(segments_intersect(a, b) for a in segments for b in other_segments),
                    'Crossing exchange routes: '+identifier+' / '+other)
    for text in root.findall('.//{*}text'):
        if 'transform' in text.attrib:
            continue
        size, x, y = (float(text.attrib[key]) for key in ('font-size', 'x', 'y'))
        width = metrics.measure(text.text or '', size, text.attrib['font-weight'])
        anchor = text.attrib['text-anchor']
        left = x-width/2 if anchor == 'middle' else x-width if anchor == 'end' else x
        # Conservative text bounds also keep labels clear of neighboring routes.
        edges = [((left-2, y-size-2), (left+width+2, y-size-2)),
                 ((left+width+2, y-size-2), (left+width+2, y+4)),
                 ((left+width+2, y+4), (left-2, y+4)),
                 ((left-2, y+4), (left-2, y-size-2))]
        for identifier, segments in routes:
            require(not any(segments_intersect(a, b) for a in edges for b in segments),
                    'Exchange route overlaps label: '+identifier+' / '+(text.text or ''))
    return dict(exchange_routes_do_not_cross=True, exchange_labels_clear_routes=True)


def display_check(inv, path, metrics=None):
    inventory_check(inv)
    metrics = metrics or SerifMetrics()
    root = ET.parse(path).getroot()
    checks = {**validate_style(root), **validate_arrowheads(root), **validate_port_labels(root)}
    frame = root.find('./{*}g[@data-system="Framework"]')
    require(frame is not None and not frame.findall('.//{*}g[@data-actor]'),
            'External participant inside Framework')
    require(bounds(frame.find('./{*}rect[@data-enclosure="Framework"]')) == FRAME,
            'Changed Framework boundary')
    components = frame.findall('./{*}g[@data-component]')
    require(Counter(g.attrib['data-component'] for g in components) == Counter(CANONICAL_NAMES.keys()),
            'Missing or duplicate logical component')
    for group in components:
        cid = group.attrib['data-component']
        rect = group.find('./{*}rect')
        require(bounds(rect) == COMPONENT_BOXES[cid] and rect.attrib['fill'] == 'white',
                'Changed component containment or fill')
        x, y, width, height = bounds(rect)
        require(within((x, y), FRAME) and within((x+width, y+height), FRAME),
                'Logical component outside Framework')
        labels = group.findall('./{*}text')
        require(' '.join(t.text or '' for t in labels[:2]) == cid+' '+CANONICAL_NAMES[cid],
                'Changed logical component name')
        allocation = next(c['requirements'] for c in inv['components'] if c['id'] == cid)
        require(len(labels) == 3 and labels[2].text == requirement_label(allocation),
                'Changed displayed FR allocation')
    actors = root.findall('.//{*}g[@data-actor]')
    require(len(actors) == 1 and actors[0].attrib['data-actor'] == 'users' and
            actors[0].find('./{*}text').text == 'Users', 'Only users are external')
    rect = actors[0].find('./{*}rect')
    require(bounds(rect) == USER_BOX and rect.attrib['fill'] == LIGHT and
            USER_BOX[0]+USER_BOX[2] < FRAME[0], 'Users must be outside Framework')
    ports = frame.findall('./{*}rect[@data-port]')
    require(Counter(p.attrib['data-interface'] for p in ports) ==
            Counter(i['id'] for i in inv['interfaces']), 'Expected one shared port per user interface')
    groups = root.findall('.//{*}g[@data-exchange]')+root.findall('./{*}g[@data-flow]')
    require(Counter(g.attrib['id'] for g in groups) ==
            Counter(e['id'] for e in all_exchanges(inv)), 'Missing or duplicate exchange')
    boxes = dict(COMPONENT_BOXES, users=USER_BOX)
    for item in all_exchanges(inv):
        group = next(g for g in groups if g.attrib['id'] == item['id'])
        require(all(group.attrib['data-'+key] == item[key] for key in ('source', 'target', 'kind')),
                'Changed exchange endpoint or kind')
        route = group.find('./{*}path')
        require(route.attrib['d'] == item['path'] and
                route.attrib.get('stroke-dasharray') == LINE_PATTERNS[item['line_style']],
                'Reversed or disconnected exchange: '+item['id'])
        points = path_points(route.attrib['d'])
        require(on_edge(points[0], boxes[item['source']]) and
                on_edge(points[-1], boxes[item['target']]), 'Exchange misses its participant')
        require([t.text for t in group.findall('./{*}text')] == item['labels'],
                'Changed exchange label')
        for text in group.findall('./{*}text'):
            require(float(text.attrib['font-size']) >= FONT, 'Unreadable exchange label')
    for interface in inv['interfaces']:
        port = next(p for p in ports if p.attrib['data-interface'] == interface['id'])
        require(float(port.attrib['data-boundary-x']) == FRAME[0] and
                port.attrib['data-features'].split(',') == [f['name'] for f in interface['flows']],
                'Changed shared boundary port')
        for flow in interface['flows']:
            group = next(g for g in groups if g.attrib['id'] == flow['id'])
            require(group.attrib['data-interface'] == interface['id'] and
                    group.attrib['data-component-endpoint'] == interface['component'],
                    'Changed user interface ownership')
            points = path_points(flow['path'])
            horizontal = next((a, b) for a, b in zip(points, points[1:])
                              if a[1] == b[1] and min(a[0], b[0]) < FRAME[0] < max(a[0], b[0]))
            crossing = (FRAME[0], horizontal[0][1])
            require(on_edge(crossing, FRAME) and within(crossing, bounds(port)),
                    'User exchange misses its shared boundary port')
    checks.update(layout_check(root, metrics))
    checks.update(four_components_checked=True, only_users_external=True,
                  all_eight_internal_exchanges_displayed=True,
                  all_four_user_flows_displayed=True, two_shared_ports_checked=True,
                  report_requirement_allocations_checked=True,
                  component_names_containment_and_directed_endpoints_checked=True,
                  terminal_heads_skip_intermediate_ports=True)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', type=Path, required=True)
    parser.add_argument('--coverage', type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(job != ROOT and ROOT not in job.parents, 'Check artifacts must remain outside the checkout')
    metrics, inv = SerifMetrics(), inventory()
    figure = create_figure(inv, metrics)
    rendered = job / BASE.name
    rendering = render_figure(figure, rendered, job)
    checks = display_check(inv, rendered.with_suffix('.svg'), metrics)
    require(re.search(r'^Pages:\s+1\s*$', run(['pdfinfo', str(rendered.with_suffix('.pdf'))]), re.M),
            'Expected one PDF page')
    checks.update(rendering['checks'], pdf_pages=1)
    BASE.with_suffix('.pdf').write_bytes(rendered.with_suffix('.pdf').read_bytes())
    inv.update(checks=checks, generator_sha256=sha(Path(__file__)),
               style_sha256=sha(FIG / 'diagram_style.py'),
               semantics='Four logical components inside Framework. Only users are external. '
                         'L02 returns COTS parameter identifiers to L01 and values to L03. '
                         'L03 returns numerical result identifiers to L01.')
    BASE.with_suffix('.inventory.json').write_text(json.dumps(inv, indent=2)+'\n')
    if args.coverage:
        args.coverage.resolve().write_text(json.dumps(inv, indent=2)+'\n')
    provenance = dict(artifact='logical-architecture', kind='Authored illustrative logical architecture',
        producer='logical-architecture.py, four components in one view',
        native_syside_render=False, executed_simulation=False,
        basis=inv['source_contract_status'], inventory=BASE.with_suffix('.inventory.json').name,
        counts=inv['counts'], checks=checks,
        dimensions=dict(pdf_pt=[W, H], pdf_pages=1), font=metrics.provenance(),
        generator_sha256=inv['generator_sha256'], style_sha256=inv['style_sha256'],
        report_source_sha256=inv['report_source_sha256'],
        artifact_sha256=dict(pdf=sha(BASE.with_suffix('.pdf'))),
        rendering_sha256=rendering['artifact_sha256'],
        reproduction=['python3 final_report/fig/logical-architecture.py --jobdir /absolute/external/check-dir'])
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(dict(counts=inv['counts'], checks=checks), indent=2))


if __name__ == '__main__':
    main()
