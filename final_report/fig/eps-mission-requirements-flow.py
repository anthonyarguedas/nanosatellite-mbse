#!/usr/bin/env python3
"""Render six EPS activity and information flow panels, grouped by NASA phase.

python3 final_report/fig/eps-mission-requirements-flow.py --jobdir /absolute/external/check-dir

The combined PDF contains all six panels. The base SVG and PNG preview panel 1.
The report captions identify this decomposition as a proposed synthesis of
MR-01--06, NASA review purposes and El Hachimi et al.'s EPS activities.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil

from diagram_style import Figure, INK, orthogonal_points, render_figure, require, run, sha

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
BASE = FIG / 'eps-mission-requirements-flow'
NEEDS = FIG.parent / 'needs.tex'
APPENDIX = FIG.parent / 'eps-mission-flows.tex'
NASA = ROOT / 'SLR/SLR1/pdfs/standards/nasa-seh-2016/nasa-seh-2016.md'
EPS = ROOT / 'SLR/SLR1/pdfs/handpicked-reports/handpicked-report-0003/handpicked-report-0003.md'
W, H = 1000, 1264
NODE_FONT, FLOW_FONT = 24, 22
BOXES = {
    'input': (340, 44, 320, 64),
    'n0': (340, 200, 320, 64),
    'n1': (40, 380, 280, 64), 'n2': (680, 380, 280, 64),
    'n3': (40, 560, 280, 64), 'n4': (680, 560, 280, 64),
    'n5': (340, 740, 320, 64), 'n6': (340, 900, 320, 64),
    'output': (340, 1192, 320, 64),
}
REVIEW_BOX = (410, 1025, 180, 110)

# Activities have short verb/object labels. Engineering quantities and products
# belong to the directed exchanges, not to lists inside activity boxes.
PANELS = [
    dict(id='pre-a', phase='Pre-Phase A', mr='MR-01', review='MCR',
         title='Pre-Phase A: mission concept and EPS feasibility',
         incoming='mission-context', outgoing='concept-basis',
         source=['Mission / spacecraft', 'context'], target=['Phase A:', 'requirements'],
         activities=[['Define mission', 'and ConOps'], ['Analyse orbit', 'and attitude'],
                     ['Estimate payload /', 'subsystem power'], ['Bound generation', 'and storage'],
                     ['Construct mode', 'load profiles'], ['Assess concept', 'power / energy'],
                     ['Define initial', 'V&V approach']],
         labels={
             'input': ['Expectations, mission constraints,', 'candidate component / heritage data'],
             'left': ['Orbit / pointing modes,', 'lifetime and constraints'],
             'right': ['Subsystem functions,', 'modes and duty cycles'],
             'left-down': ['Eclipse / sunlight periods,', 'array incidence and', 'temperature bounds'],
             'right-down': ['Nominal / peak powers,', 'duty cycles and', 'operating assumptions'],
             'left-join': ['Generation / storage bounds,', 'conversion efficiencies'],
             'right-join': ['Mode demand profiles,', 'nominal / peak energy estimates'],
             'plans': ['Concept budgets, assumptions,', 'uncertainty and feasibility risks'],
             'review': ['Concept, budgets, assumptions and risks,', 'preliminary verification / validation approach'],
             'output': ['Accepted concept / ConOps, power estimates,', 'budgets, risks and initial V&V approach'],
         }),
    dict(id='phase-a-requirements', phase='Phase A', mr='MR-02', review='SRR',
         title='Phase A: EPS requirements and joint power feasibility',
         incoming='concept-basis', outgoing='requirements-basis',
         source=['Accepted MCR basis', 'and spacecraft inputs'], target=['Phase A:', 'architecture'],
         activities=[['Derive EPS', 'requirements'], ['Specify EPS', 'interfaces'],
                     ['Define measurable', 'performance criteria'], ['Model subsystem', 'load scenarios'],
                     ['Assess joint', 'power feasibility'], ['Validate requirements', 'and resolve conflicts'],
                     ['Plan requirement', 'verification']],
         labels={
             'input': ['Concept / ConOps, spacecraft allocations,', 'sourced demand estimates and power bounds'],
             'left': ['Allocated EPS functions', 'and electrical constraints'],
             'right': ['Stakeholder expectations,', 'mission / spacecraft limits'],
             'left-down': ['Electrical interface limits,', 'allocated subsystem', 'demands and modes'],
             'right-down': ['Power / energy thresholds,', 'units and operating', 'conditions'],
             'cross': ['Load schedules, peak demand,', 'sunlight / eclipse energy'],
             'left-join': ['Load assumptions and units,', 'input data provenance'],
             'right-join': ['Feasibility findings,', 'conflicts and margins'],
             'plans': ['Validated requirements and interfaces,', 'trace links and conflict dispositions'],
             'review': ['EPS requirements, interfaces, measurable', 'criteria and joint feasibility findings'],
             'output': ['Accepted EPS requirements, interfaces,', 'allocations and measurable verification criteria'],
         }),
    dict(id='phase-a-architecture', phase='Phase A', mr='MR-03', review='MDR/SDR',
         title='Phase A: EPS architecture and requirement allocation',
         incoming='requirements-basis', outgoing='architecture-basis',
         source=['Accepted SRR', 'requirements basis'], target=['Phase B:', 'preliminary design'],
         activities=[['Generate EPS', 'alternatives'], ['Define power', 'topologies'],
                     ['Allocate functions', 'and interfaces'], ['Estimate size', 'and performance'],
                     ['Compare feasible', 'alternatives'], ['Select EPS', 'architecture'],
                     ['Record allocations', 'and trade rationale']],
         labels={
             'input': ['EPS requirements / interfaces, mission', 'scenarios and joint feasibility findings'],
             'left': ['Commercial / custom', 'concepts and power limits'],
             'right': ['Functions, mode behaviour,', 'control responsibilities'],
             'left-down': ['Energy transfer / bus', 'choices, component options', 'and loss estimates'],
             'right-down': ['Function / control', 'allocations and', 'interface definitions'],
             'cross': ['Size / power estimates,', 'uncertainty and constraints'],
             'left-join': ['Predicted performance,', 'resource use and limits'],
             'right-join': ['Feasibility and margins,', 'ranked alternatives and risks'],
             'plans': ['Selected architecture, requirement', 'coverage, trade results and decision reasons'],
             'review': ['Architecture, requirement allocations,', 'interface definitions and justified alternatives'],
             'output': ['Accepted architecture, allocations,', 'interfaces, trade rationale and risk basis'],
         }),
    dict(id='phase-b', phase='Phase B', mr='MR-04', review='PDR',
         title='Phase B: EPS sizing and preliminary design',
         incoming='architecture-basis', outgoing='preliminary-design-basis',
         source=['Accepted MDR/SDR', 'architecture basis'], target=['Adapted C:', 'detailed design'],
         activities=[['Construct mode', 'power / energy budget'], ['Size solar', 'arrays'],
                     ['Size batteries'], ['Configure preliminary', 'EPS design'],
                     ['Simulate orbital', 'energy balance'], ['Assess margins', 'and compatibility'],
                     ['Plan EPS verification', 'and validation']],
         labels={
             'input': ['Architecture / allocations, load schedules,', 'orbit / attitude scenarios and lifetime limits'],
             'left': ['Sunlight demand,', 'path efficiency and', 'end of life cell output'],
             'right': ['Eclipse energy,', 'allowed depth of discharge', 'and cycle life limits'],
             'left-down': ['Array area and cell counts,', 'series / parallel', 'configuration'],
             'battery-design': ['Battery capacity, voltage,', 'configuration and', 'operating limits'],
             'cross': ['Preliminary EPS configuration,', 'load and environment scenarios'],
             'left-join': ['Configured EPS ratings,', 'interfaces and component limits'],
             'right-join': ['Energy / charge histories,', 'shortfalls and loss estimates'],
             'plans': ['Sized design, margins, compatibility', 'findings, trade decisions and risk dispositions'],
             'review': ['Sized preliminary design, margins, risks,', 'controlled interfaces and V&V plans'],
             'output': ['Accepted preliminary design, sizing,', 'interfaces, margins, risks and V&V plans'],
         }),
    dict(id='phase-c-design', phase='Adapted Phase C', mr='MR-05', review='scoped CDR',
         title='Adapted C: detailed EPS design before deliverable coding',
         incoming='preliminary-design-basis', outgoing='detailed-design-basis',
         source=['Accepted PDR', 'design basis'], target=['Adapted C:', 'implementation'],
         activities=[['Define detailed', 'EPS design'], ['Specify hardware', 'and controller models'],
                     ['Design host control', 'and interface software'], ['Analyse electrical', 'and control behaviour'],
                     ['Assess thermal / EMC', 'and interface limits'], ['Resolve design', 'findings and risks'],
                     ['Plan implementation,', 'integration and V&V']],
         labels={
             'input': ['Sized design, requirements, interfaces,', 'component data, margins and V&V plans'],
             'left': ['Circuit / component choices,', 'control and protection', 'responsibilities'],
             'right': ['Functions, mode behaviour,', 'commands / telemetry', 'and interface allocations'],
             'left-down': ['Model specifications,', 'parameters, validity', 'and control laws'],
             'right-down': ['Software / interface', 'designs, timing and', 'mode / failure behaviour'],
             'cross': ['Electrical / control responses,', 'losses and interface data'],
             'left-join': ['Electrical / control evidence,', 'requirement conformity findings'],
             'right-join': ['Thermal / EMC / interface findings,', 'margins and model validity limits'],
             'plans': ['Assessed design, risk dispositions,', 'requirements and applicable evidence gaps'],
             'review': ['Detailed EPS / model / software designs,', 'interfaces, analyses, risks and plans'],
             'output': ['Accepted EPS / model / software designs,', 'interfaces and implementation / V&V plans'],
         }),
    dict(id='phase-c-readiness', phase='Adapted Phase C', mr='MR-06', review='scoped SIR',
         title='Adapted C: model and host software integration readiness',
         incoming='detailed-design-basis', outgoing='integration-ready',
         source=['Accepted scoped CDR', 'design basis'], target=['Integration ready', 'Before Phase D'],
         activities=[['Prepare scoped', 'implementation'], ['Implement EPS', 'models'],
                     ['Code and build', 'host software'], ['Execute MIL'], ['Execute SIL'],
                     ['Assess model / software', 'conformance'], ['Prepare integration', 'configurations / procedures']],
         labels={
             'input': ['Accepted detailed design / interfaces,', 'implementation, integration and V&V plans'],
             'left': ['Hardware / controller', 'model specifications', 'and parameter sets'],
             'right': ['Host software design,', 'interfaces and', 'build configuration'],
             'left-down': ['Plant / controller models,', 'mission / fault scenarios', 'and expected responses'],
             'right-down': ['Host code / build,', 'interface configuration', 'and scenarios'],
             'cross': ['EPS plant and common scenarios,', 'MIL reference responses'],
             'left-join': ['MIL responses and failures,', 'model validity limits'],
             'right-join': ['SIL responses / MIL differences,', 'requirement / ConOps findings'],
             'plans': ['Assessed releases, evidence, interface', 'findings, limits and remaining gaps'],
             'review': ['Released models / code, MIL/SIL evidence,', 'ready integration configurations / procedures'],
             'output': ['Accepted models / host software, interfaces,', 'MIL/SIL evidence and integration procedures'],
         }),
]


class Panel:
    def __init__(self, spec):
        self.spec = spec
        self.figure = Figure(spec['title'], W, H)
        self.nodes, self.flows = {}, []
        self.figure.el('desc').text = (
            f"{spec['phase']}, {spec['mr']}, ending at {spec['review']}. "
            'Short activity boxes exchange the information written beside each arrow. '
            'Review findings return to the initial activity. Cross-phase changes use change control.')
        self.figure.text(spec['title'], 8, 27, size=28, weight='bold')
        self.node('input', spec['source'], 'incoming-basis')
        for index, labels in enumerate(spec['activities']):
            self.node('n'+str(index), labels, 'activity')
        self.node('output', spec['target'], 'handoff')
        group = self.figure.el('g', data_node='review', data_kind='review',
                               data_review=spec['review'], data_mission_requirement=spec['mr'],
                               data_phase=spec['phase'])
        self.nodes['review'] = REVIEW_BOX
        self.figure.el('polygon', group, points='500,1025 590,1080 500,1135 410,1080',
                       fill='white', stroke=INK, stroke_width='.8')
        for label, y, size in [(spec['mr'], 1058, 18), (spec['review'], 1083, 20), ('Accept?', 1107, 20)]:
            self.figure.text(label, 500, y, size=size, weight='bold' if label != 'Accept?' else 'normal',
                             anchor='middle', parent=group)

    def node(self, identifier, labels, kind):
        require(1 <= len(labels) <= 2, 'Activity and context boxes have at most two lines')
        box = BOXES[identifier]
        self.nodes[identifier] = box
        x, y, w, h = box
        group = self.figure.el('g', data_node=identifier, data_kind=kind,
                               data_phase=self.spec['phase'], data_mission_requirement=self.spec['mr'])
        self.figure.rect(*box, parent=group)
        baseline = y+h/2+NODE_FONT*.32-(len(labels)-1)*14
        self.figure.lines(labels, x+w/2, baseline, size=NODE_FONT, leading=28,
                          weight='bold', anchor='middle', width=w-24, parent=group)

    def edge(self, identifier, source, target, path, labels, position, width,
             kind='information', anchor='start'):
        require(labels and len(labels) <= 3, 'Each exchange needs a concise visible information label')
        styles = {'information': 'solid', 'accepted-information': 'solid',
                  'findings': 'dotted', 'authorization': 'dashed'}
        group = self.figure.el('g', data_flow=identifier, data_source=source,
                               data_target=target, data_kind=kind,
                               data_exchange_label=' / '.join(labels))
        if kind == 'accepted-information':
            group.set('data-requires-acceptance', 'true')
        self.figure.arrow(path, group, style=styles[kind], id='flow-'+identifier)
        self.figure.lines(labels, *position, size=FLOW_FONT, leading=24,
                          width=width, anchor=anchor, parent=group, data_exchange_text=identifier)
        self.flows.append(dict(id=identifier, source=source, target=target, path=path,
                               labels=labels, kind=kind))


def create_panel(spec):
    panel = Panel(spec)
    e, labels = panel.edge, spec['labels']
    input_position, input_anchor = ((480, 135), 'end') if spec['mr'] == 'MR-06' else ((520, 135), 'start')
    e('input', 'input', 'n0', 'M500 108 V200', labels['input'], input_position, 470, anchor=input_anchor)
    e('left', 'n0', 'n1', 'M420 264 V350 H180 V380', labels['left'], (50, 284), 260)
    e('right', 'n0', 'n2', 'M580 264 V350 H820 V380', labels['right'], (700, 284), 290)
    e('left-down', 'n1', 'n3', 'M180 444 V560', labels['left-down'], (200, 476), 300)
    if spec['mr'] == 'MR-04':
        e('battery-design', 'n2', 'n3', 'M680 412 H640 V540 H260 V560',
          labels['battery-design'], (660, 476), 330)
    else:
        e('right-down', 'n2', 'n4', 'M820 444 V560', labels['right-down'],
          (800, 476), 270, anchor='end')
    if 'cross' in labels:
        position = (340, 614) if spec['mr'] == 'MR-04' else (340, 548)
        e('cross', 'n3', 'n4', 'M320 592 H680', labels['cross'], position, 320)
    e('left-join', 'n3', 'n5', 'M180 624 V705 H390 V740',
      labels['left-join'], (200, 668), 300)
    e('right-join', 'n4', 'n5', 'M900 624 V705 H610 V740',
      labels['right-join'], (880, 668), 320, anchor='end')
    e('plans', 'n5', 'n6', 'M500 804 V900', labels['plans'], (520, 838), 470)
    e('review', 'n6', 'review', 'M500 964 V1025', labels['review'], (530, 988), 460)
    e('output', 'review', 'output', 'M500 1135 V1192', labels['output'],
      (530, 1158), 460, kind='accepted-information')
    e('findings', 'review', 'n0', 'M410 1080 H14 V232 H340',
      ['No: review findings / conditions'], (30, 1066), 360, kind='findings')
    if spec['mr'] == 'MR-05':
        e('coding-authorization', 'review', 'output', 'M455 1107.5 V1160 H300 V1224 H340',
          ['Authorization for', 'deliverable coding'], (50, 1168), 230, kind='authorization')
    if spec['mr'] == 'MR-06':
        e('coding-authorization', 'input', 'n0', 'M660 76 H980 V232 H660',
          ['Scoped CDR authorization', 'for deliverable coding'], (960, 135), 290,
          kind='authorization', anchor='end')
    return panel


def on_boundary(point, node, review=False):
    x, y = point
    left, top, width, height = node
    if review:
        return abs(abs(x-(left+width/2))/(width/2)+abs(y-(top+height/2))/(height/2)-1) < 1e-6
    return (left <= x <= left+width and top <= y <= top+height
            and (x in (left, left+width) or y in (top, top+height)))


def text_bounds(figure, text):
    size = float(text.attrib['font-size'])
    width = figure.metrics.measure(text.text or '', size, text.attrib.get('font-weight', 'normal'))
    x, y = float(text.attrib['x']), float(text.attrib['y'])
    anchor = text.attrib.get('text-anchor', 'start')
    left = x-width/2 if anchor == 'middle' else x-width if anchor == 'end' else x
    return left, y-.8*size, width, size


def segment_crosses_box(start, end, box):
    left, top, width, height = box
    x1, y1 = start
    x2, y2 = end
    return ((x1 == x2 and left < x1 < left+width and
             max(min(y1, y2), top) < min(max(y1, y2), top+height))
            or (y1 == y2 and top < y1 < top+height and
                max(min(x1, x2), left) < min(max(x1, x2), left+width)))


def check_label_clearance(panel):
    labels = []
    routes = [orthogonal_points(group.find('./{*}path').attrib['d'])
              for group in panel.figure.root.findall('.//{*}g[@data-flow]')]
    for group in panel.figure.root.findall('.//{*}g[@data-flow]'):
        for text in group.findall('./{*}text'):
            box = text_bounds(panel.figure, text)
            for route in routes:
                require(not any(segment_crosses_box(a, b, box) for a, b in zip(route, route[1:])),
                        'A route crosses an exchange label: '+panel.spec['id']+'/'+str(text.text))
            for node in panel.nodes.values():
                require(not (max(box[0], node[0]) < min(box[0]+box[2], node[0]+node[2])
                             and max(box[1], node[1]) < min(box[1]+box[3], node[1]+node[3])),
                        'An exchange label overlaps a node: '+str(text.text))
            for prior in labels:
                require(not (max(box[0], prior[0]) < min(box[0]+box[2], prior[0]+prior[2])
                             and max(box[1], prior[1]) < min(box[1]+box[3], prior[1]+prior[3])),
                        'Overlapping exchange labels: '+panel.spec['id']+'/'+str(text.text))
            labels.append(box)
    for group in panel.figure.root.findall('.//{*}g[@data-node]'):
        node = panel.nodes[group.attrib['data-node']]
        for text in group.findall('./{*}text'):
            left, top, width, height = text_bounds(panel.figure, text)
            require(node[0] <= left and left+width <= node[0]+node[2]
                    and node[1] <= top and top+height <= node[1]+node[3],
                    'Node text exceeds its rectangle: '+str(text.text))
    return {'exchange_labels_clear_of_routes_and_nodes': True,
            'exchange_labels_do_not_overlap': True, 'node_labels_fit_their_boxes': True}


def check_panel(panel):
    root, spec = panel.figure.root, panel.spec
    groups = root.findall('.//{*}g[@data-flow]')
    require(len(groups) == len(panel.flows), 'Missing or repeated visible flow')
    for group, flow in zip(groups, panel.flows):
        require(group.attrib['data-source'] == flow['source']
                and group.attrib['data-target'] == flow['target'], 'Changed activity dependency')
        visible = [text.text for text in group.findall('./{*}text')]
        require(visible == flow['labels'], 'Exchange label is missing or changed')
        points = orthogonal_points(group.find('./{*}path').attrib['d'])
        require(on_boundary(points[0], panel.nodes[flow['source']], flow['source'] == 'review')
                and on_boundary(points[-1], panel.nodes[flow['target']], flow['target'] == 'review'),
                'Exchange does not terminate on its activity or review')
        for identifier, (left, top, width, height) in panel.nodes.items():
            if identifier in (flow['source'], flow['target']):
                continue
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                crosses = ((x1 == x2 and left < x1 < left+width and
                            max(min(y1, y2), top) < min(max(y1, y2), top+height))
                           or (y1 == y2 and top < y1 < top+height and
                               max(min(x1, x2), left) < min(max(x1, x2), left+width)))
                require(not crosses, 'Exchange crosses an unrelated activity: '+flow['id']+'/'+identifier)
    reachable = {'input'}
    for _ in panel.nodes:
        for flow in panel.flows:
            if flow['kind'] != 'findings' and flow['source'] in reachable:
                reachable.add(flow['target'])
    require(reachable == set(panel.nodes), 'An activity or review has no incoming engineering information')
    require(root.find('.//{*}g[@data-flow="output"]').attrib['data-requires-acceptance'] == 'true',
            'Review output lacks its acceptance condition')
    review = root.find('.//{*}g[@data-node="review"]')
    require(review.attrib['data-review'] == spec['review'] and review.attrib['data-phase'] == spec['phase'],
            'Changed review name or NASA phase')
    for node in root.findall('.//{*}g[@data-kind="activity"]'):
        require(1 <= len(node.findall('./{*}text')) <= 2, 'Dense activity box')
    return {'short_activities_checked': 7, 'visible_exchange_labels_checked': len(groups),
            'activity_boundary_endpoints_checked': True, 'no_routes_through_unrelated_activities': True,
            'all_activities_reachable': True, 'review_acceptance_condition_checked': True,
            **check_label_clearance(panel)}


def check_series(panels):
    statements = dict(re.findall(r'^(MR-\d\d) & (.*?) & ', NEEDS.read_text(), re.M))
    require(list(statements) == [panel.spec['mr'] for panel in panels],
            'Panel series does not cover exactly MR-01--06 in order')
    for panel in panels:
        require(panel.spec['review'].split()[-1] in statements[panel.spec['mr']],
                'Panel review disagrees with its mission requirement')
        check_panel(panel)
    for before, after in zip(panels, panels[1:]):
        require(before.spec['outgoing'] == after.spec['incoming'], 'Broken cross-panel information handoff')
    require(panels[-1].spec['outgoing'] == 'integration-ready', 'Series must end before Phase D')
    require(any(flow['kind'] == 'authorization' for flow in panels[-2].flows)
            and any(flow['kind'] == 'authorization' for flow in panels[-1].flows),
            'Scoped CDR authorization must precede deliverable coding')
    return {'mission_requirements_checked': 6, 'phase_panels_checked': 6,
            'cross_panel_handoffs_checked': 5, 'cdr_coding_authorization_checked': True,
            'sir_ends_before_phase_d': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', required=True, type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(not job.is_relative_to(ROOT), 'Use an external check directory')
    panels = [create_panel(spec) for spec in PANELS]
    checks = check_series(panels)
    published = []
    for panel in panels:
        base = FIG / (BASE.name+'-'+panel.spec['id'])
        artifact = render_figure(panel.figure, base, job)
        artifact['checks'].update(check_panel(panel))
        published.append(dict(id=panel.spec['id'], file=base.name, phase=panel.spec['phase'],
                              mr=panel.spec['mr'], review=panel.spec['review'],
                              incoming=panel.spec['incoming'], outgoing=panel.spec['outgoing'],
                              flows=panel.flows, **artifact))
    run(['pdfunite', *[str(FIG / (panel['file']+'.pdf')) for panel in published], str(BASE.with_suffix('.pdf'))])
    for extension in ('.svg', '.png'):
        shutil.copyfile(FIG / (published[0]['file']+extension), BASE.with_suffix(extension))
    provenance = dict(
        kind='Proposed activity decomposition of NASA review purposes and EPS mission requirements',
        basis={'mission_requirements': 'MR-01--06',
               'NASA': 'Sections 2.3, 3.3--3.6, 4.2 and Table 6.7-1',
               'El Hachimi et al.': 'Figure 1 and Sections 2--4, 6.2, 7 and 8.1'},
        source_sha256={str(path.relative_to(ROOT)): sha(path) for path in (NEEDS, APPENDIX, NASA, EPS)},
        generator_sha256=sha(Path(__file__)), style_sha256=sha(FIG / 'diagram_style.py'),
        artifact_sha256={kind: sha(BASE.with_suffix('.'+kind)) for kind in ('pdf', 'svg', 'png')},
        preview='Base SVG and PNG are exact copies of the Pre-Phase A panel. The base PDF contains all six panels.',
        checks=checks, panels=published,
        reproduction=['python3 final_report/fig/eps-mission-requirements-flow.py --jobdir /absolute/external/check-dir'])
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
