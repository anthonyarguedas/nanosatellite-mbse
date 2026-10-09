#!/usr/bin/env python3
"""Reproduce three monochrome, serif logical internal block style views.

python3 final_report/fig/logical-architecture.py --jobdir /absolute/external/check-dir
Requires Times New Roman, librsvg and Poppler. Uses native contracts when present,
otherwise the retained figure inventory. --native-check requires the original
SysML sources and checker. Every displayed component has its canonical name.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

FIG = Path(__file__).resolve().parent
REPORT, ROOT = FIG.parent, FIG.parent.parent
BASE = FIG / 'logical-architecture'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
from diagram_style import (FONT_STACK, INK, LIGHT, MUTED, LINE_PATTERNS,
    SerifMetrics, arrow_marker, foreground_arrowheads, line_attributes,
    orthogonal_points, shared_port, validate_arrowheads, validate_port_labels, validate_style)

W, H, FONT = 690, 420, 11
INFO = CONTROL = INK
CANONICAL_NAMES = {
    'L01': 'Requirements and guidance', 'L02': 'Mission and EPS design',
    'L03': 'Simulation and software integration', 'L04': 'Model credibility',
    'L05': 'Evidence and technical review', 'L06': 'Configuration and controlled exchange',
}
GROUP_NAMES = {
    'L01': ['L01 Requirements', 'and guidance'], 'L02': ['L02 Mission and', 'EPS design'],
    'L03': ['L03 Simulation and', 'software integration'], 'L04': ['L04 Model credibility'],
    'L05': ['L05 Evidence and', 'technical review'],
    'L06': ['L06 Configuration and', 'controlled exchange'],
}
RESPONSIBILITIES = {'L01': 'Check and advise',
    'L03': 'L03 executes EPS/RAM analyses and assesses engineering criteria.'}
PORT_TYPES = {'p01': 'EngineeringUsePort', 'p02': 'KnowledgePort', 'p03': 'AnalysisPort',
              'p04': 'HostSoftwarePort', 'p06': 'TechnicalReviewPort'}
PORT_FIELD_ALIASES = {'spacecraftInputs': '16.i01/18.i04', 'epsResponses': '18.o03',
    'analysisResponse': '18.i06', 'codingRequest': '36.o01/24.o01',
    'softwareProduct': '24.i01/36.o02', 'softwareResult': '24.o02', 'codingResponse': '36.i05'}
ACTORS = {'engineers': 'Engineers and stakeholders', 'sources': 'Knowledge and data sources',
    'tools': 'NVIDIA Omniverse spacecraft and subsystem simulations', 'software': 'F Prime host toolchain',
    'reviewers': 'Reviewers and authority'}
BOUNDARY_TYPES = {
    'engineeringCompatibility': 'EngineeringSubmission', 'guidanceSubmission': 'GuidanceRequest',
    'traceQuerySubmission': 'TraceQuery', 'viewSelectionSubmission': 'ViewSelection',
    'baselineRetrievalSubmission': 'BaselineRetrieval', 'assessmentPlanSubmission': 'EPSAssessmentPlan',
    'requirementSubmission': 'RequirementRecord', 'missionSubmission': 'MissionDefinition',
    'designSubmission': 'DesignConfiguration', 'changeSubmission': 'ChangeProposal',
    'reviewRequestSubmission': 'PhaseBaseline', 'guidanceResponse': 'AssistanceReport',
    'assessmentResponse': 'ModelAssessment', 'sourceCompatibility': 'SourceSubmission',
    'referenceSubmission': 'ReferenceData', 'sourceMethods': 'SourceSubmission',
    'componentProperties': 'SourceSubmission -> ComponentDesignData', 'boundedSourceQuery': 'SourceQuery',
}
PEER_LABELS = {
    'requirementsAllocations': ['Requirements &', 'EPS allocations'],
    'scenariosDesignQuantities': ['Mission/ConOps, budgets', '& mass/volume estimates'],
    'modelsScenarios': ['Models, scenarios &', 'EPS interfaces/behavior'],
    'designStudyResults': ['Power/energy, RAM', 'results & limits'],
    'runHistories': ['Run histories,', 'status & limits'],
    'modelAssessment': ['Credibility, quality', '& timing findings'],
    'requirementBasisCoverage': ['Requirements,', 'links & coverage'],
    'designConOpsProducts': ['Design products', '& ConOps'],
    'assessmentCriteria': ['V&V plans &', 'assessment criteria'],
    'maturityFindings': ['Review gaps &', 'recorded dispositions'],
    'preserveL01': ['Requirement &', 'guidance records'],
    'preserveL02': ['Design, sizing &', 'trade records'],
    'preserveL03': ['Run, replay &', 'software records'],
    'preserveL04': ['Credibility &', 'calibration proposals'],
    'baselineDecisions': ['Evidence, review &', 'decision records'],
    'currentContext': ['Current context &', 'reassessment'],
    'releaseRevisions': ['Authorized releases,', 'replay & use blockers'],
    'currentRecordsL02': ['Current design,', 'impacts & stale status'],
    'currentRecordsL04': ['Current evidence,', 'impacts & stale status'],
    'currentRecordsL05': ['Current review basis,', 'impacts & stale status'],
}
EXTERNAL_LABELS = {
    'X01.1': 'Requirements, mission/design, requests, changes & decisions',
    'X01.2': 'Guidance, studies, assessments & baseline/review results',
    'X02.1': 'Sources, methods, component properties & reference data',
    'X02.2': 'Bounded source queries',
    'X03.1': 'Spacecraft models & simulation requests',
    'X03.2': 'Spacecraft run & coupling configuration',
    'X03.3': 'Spacecraft execution & mapping diagnostics',
    'X03.4': 'Spacecraft feasibility findings & limits',
    'X03.5': 'Spacecraft states, subsystem loads & environment',
    'X03.6': 'EPS states, dissipation & feasibility findings',
    'X04.1': 'Coding/build status & compatibility diagnostics',
    'X04.2': 'Authorized coding, host build & SIL requests',
    'X04.3': 'EPS interfaces & F Prime mapping',
    'X04.4': 'Host source, build products & exact revisions',
    'X04.5': 'Raw host SIL responses & limits',
    'X06.1': 'Review findings & authority decisions',
    'X06.2': 'Review package, recorded disposition & conditions',
}
AUTHORITY_NOTES = [
    'Engineers authorize changes and detailed design releases.',
    'The designated review authority grants acceptance. The framework records decisions.',
    'Preservation and admission confer no engineering approval.',
    'Host assessment supplies no target qualification.',
]
BOOK_EXAMPLES = [
    {'figure': '17.25', 'principle': 'Enclose logical parts in the system frame. Connect boundary ports to named parts. Concern views may repeat a subset of the same parts.'},
    {'figure': '17.17', 'principle': 'External participants are separate from the system. Directed item flows cross explicit system ports.'},
    {'figure': '17.23', 'principle': 'Keep the stable logical decomposition and distinguish component responsibilities.'},
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv):
    environment = dict(os.environ, SOURCE_DATE_EPOCH='0')
    return subprocess.run(argv, check=True, capture_output=True, text=True, env=environment).stdout


def normalize_document_id(path):
    """Poppler uses a random trailer ID. Replace only that nonsemantic field.

    The trailer follows the xref table, so object offsets stay unchanged.
    Cairo panel metadata is already fixed by SOURCE_DATE_EPOCH.
    """
    data = path.read_bytes()
    pattern = rb'/ID\s*\[(?:\((?:\\.|[^\\)])*\)\s*){2}\]'
    matches = list(re.finditer(pattern, data, re.S))
    require(len(matches) == 1, 'Expected one Poppler trailer document ID')
    match = matches[0]
    digest = hashlib.sha256(data[:match.start()]+data[match.end():]).hexdigest()[:32].encode()
    path.write_bytes(data[:match.start()]+b'/ID [<'+digest+b'> <'+digest+b'>]'+data[match.end():])


def field_ref(field):
    match = re.fullmatch(r'L\d\d\.io\.fr(\d\d)(Inputs|Outputs)\.field(\d+)', field)
    require(match, f'Unrecognized native field: {field}')
    return f'FR-{match[1]}.{"i" if match[2] == "Inputs" else "o"}{int(match[3]):02}'


METRICS = None


def information_style(identifier):
    """Separate nearby information routes without changing their native kind."""
    if identifier.startswith(('X03.', 'X04.')):
        return ('solid', 'dotted', 'dashdot')[(int(identifier.split('.')[1])-1) % 3]
    if identifier == 'E09':
        return 'dashdot'
    return 'dotted' if identifier in {
        'E02', 'E04', 'E06', 'E10', 'X01.2', 'X02.2', 'X06.2'
    } else 'solid'


def retained_inventory_check(inv):
    """Check the saved contracts when the removed modeling sources are absent."""
    require({c['id']: c['name'] for c in inv['components']} == CANONICAL_NAMES,
            'Canonical component name mismatch')
    expected_counts = {'peer_exchange_groups': 20, 'peer_field_mappings': 203,
        'black_box_interfaces': 5, 'black_box_directed_flows': 17,
        'boundary_refinement_routes': 18}
    actual_counts = {'peer_exchange_groups': len(inv['peer_exchanges']),
        'peer_field_mappings': sum(len(e['mappings']) for e in inv['peer_exchanges']),
        'black_box_interfaces': len(inv['interfaces']),
        'black_box_directed_flows': sum(len(i['flows']) for i in inv['interfaces']),
        'boundary_refinement_routes': len(inv['boundary_routes'])}
    require(inv['counts'] == actual_counts == expected_counts, 'Retained contract coverage mismatch')
    require({e['name'] for e in inv['peer_exchanges']} == set(PEER_LABELS),
            'Missing/extra retained peer exchange')
    require({i['port']: i['port_type'] for i in inv['interfaces']} == PORT_TYPES,
            'Missing/extra retained active interface')
    require({f['id'] for i in inv['interfaces'] for f in i['flows']} == set(EXTERNAL_LABELS),
            'Missing/extra retained external flow')
    for exchange in inv['peer_exchanges']:
        require(exchange['source_component'] in CANONICAL_NAMES and
                exchange['target_component'] in CANONICAL_NAMES, 'Unknown peer endpoint')
        require(exchange['kind'] == ('control' if exchange['name'] in {
            'currentContext', 'releaseRevisions', 'currentRecordsL02',
            'currentRecordsL04', 'currentRecordsL05'} else 'information'),
            'Changed retained exchange kind')


def inventory():
    sources = [REPORT / 'traceability/logical-architecture.json',
               REPORT / 'sysml/04-logical.sysml', REPORT / 'sysml/06-system-context.sysml',
               REPORT / 'sysml/10-interface-views.sysml']
    if not all(path.is_file() for path in sources):
        inv = json.loads(BASE.with_suffix('.inventory.json').read_text())
        retained_inventory_check(inv)
        inv['source_contract_status'] = 'Retained inventory. Original modeling sources are absent. No new native validation.'
        for interface in inv['interfaces']:
            interface['actor_label'] = ACTORS[interface['actor']]
        return inv
    ledger = json.loads((REPORT / 'traceability/logical-architecture.json').read_text())
    logical = (REPORT / 'sysml/04-logical.sysml').read_text()
    context = (REPORT / 'sysml/06-system-context.sysml').read_text()
    specs = (REPORT / 'sysml/10-interface-views.sysml').read_text()
    peers = []
    for index, exchange in enumerate(ledger['exchanges'], 1):
        entry = {key: exchange[key] for key in ('name', 'source_component', 'target_component', 'kind', 'payload_type', 'native')}
        entry['id'] = f'E{index:02}'
        entry['mappings'] = [{key: m[key] for key in ('source_field', 'source_output', 'source_type',
            'target_field', 'target_input', 'target_type', 'mapping', 'operation_path',
            'source_qualified_type', 'target_qualified_type')} for m in exchange['mappings']]
        peers.append(entry)
    interfaces = []
    pattern = r'interface (IF\d\d) : (\w+) connect (\w+)\.p to framework\.(p\d\d) \{(.*?)\n        \}'
    for match in re.finditer(pattern, context, re.S):
        identifier, itype, actor, port, body = match.groups()
        delegation = re.search(r'bind '+port+r' = (L\d\d\.p\d\d);', logical)
        flows = []
        for ordinal, f in enumerate(re.finditer(r'flow (\w+) of (\w+) from (client|framework)\.(\w+) to (client|framework)\.(\w+);', body), 1):
            name, typ, origin, feature, destination, target_feature = f.groups()
            require(feature == target_feature, f'Unequal interface features: {name}')
            direction = 'in' if origin == 'client' else 'out'
            flows.append({'id': f'X{identifier[-2:]}.{ordinal}', 'name': name, 'feature': feature,
                'type': typ, 'qualified_type': ('FrameworkDomain::' if typ == 'PhaseBaseline' else 'BoundaryViews::') + typ,
                'source': f'{actor}.p.{feature}' if direction == 'in' else f'framework.{port}.{feature}',
                'target': f'framework.{port}.{feature}' if direction == 'in' else f'{actor}.p.{feature}',
                'direction': direction, 'kind': 'information',
                'internal_field_aliases': PORT_FIELD_ALIASES.get(feature),
                'native': f'FrameworkContext::Context::{identifier}::{name}'})
        interfaces.append({'id': 'IF-' + identifier[-2:], 'native_id': identifier, 'type': itype,
            'port': port, 'port_type': PORT_TYPES[port], 'actor': actor, 'actor_label': ACTORS[actor],
            'delegation': delegation[1] if delegation else None, 'flows': flows})
    routes = [dict(row, id=f'B{index:02}', kind='information', type=BOUNDARY_TYPES[row['name']])
              for index, row in enumerate(ledger['native_contract']['boundary_routes'], 1)]
    result = {'schema': 3, 'abstraction': 'Native bundles, boundary ports and explicit refinements to concrete logical parts.',
        'components': [{key: c[key] for key in ('id', 'name', 'native_part')} for c in ledger['components']],
        'peer_exchanges': peers, 'interfaces': interfaces, 'boundary_routes': routes,
        'external_aliases': ledger['external_exchanges'], 'source_query_basis': ledger['native_contract']['source_query_basis'],
        'counts': {'peer_exchange_groups': len(peers), 'peer_field_mappings': sum(len(e['mappings']) for e in peers),
            'black_box_interfaces': len(interfaces), 'black_box_directed_flows': sum(len(i['flows']) for i in interfaces),
            'boundary_refinement_routes': len(routes)},
        'basis_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [REPORT / 'sysml/04-logical.sysml',
            REPORT / 'sysml/06-system-context.sysml', REPORT / 'sysml/10-interface-views.sysml']}}
    validate_inventory(result, ledger, logical, context, specs)
    return result


def validate_inventory(inv, ledger, logical, context, specs):
    """Full source/ledger checks stay independent of the displayed abstraction."""
    require({c['id']: c['name'] for c in inv['components']} == CANONICAL_NAMES, 'Canonical component name mismatch')
    peers = {e['name']: e for e in inv['peer_exchanges']}
    require(len(peers) == len(inv['peer_exchanges']) and set(peers) == {e['name'] for e in ledger['exchanges']}, 'Missing/extra peer exchange')
    found_operations = set(re.findall(r'perform action (\w+_\d{3}) : Map_\w+;', logical))
    expected_operations = set()
    for e in ledger['exchanges']:
        shown = peers[e['name']]
        for key in ('source_component', 'target_component', 'kind', 'payload_type', 'native'):
            require(shown[key] == e[key], f'Exchange {key} mismatch: {e["name"]}')
        authoritative = {m['operation_path']: m for m in e['mappings']}
        displayed = {m['operation_path']: m for m in shown['mappings']}
        require(len(displayed) == len(shown['mappings']) and set(displayed) == set(authoritative), 'Missing/duplicate field mapping')
        for operation, m in displayed.items():
            require(all(m[key] == authoritative[operation][key] for key in m if key != 'display'), 'Field mapping meaning/type mismatch')
            name = operation.split('::')[-1]
            expected_operations.add(name)
            require(f'flow {name}_source from {m["source_field"]} to {name}.source;' in logical, 'Producer direction differs from model')
            require(f'flow {name}_target from {name}.target to {m["target_field"]};' in logical, 'Consumer direction differs from model')
    require(found_operations == expected_operations, 'Uninventoried native mapping operation')
    expected_ids = set(re.findall(r'interface (IF\d\d) : \w+ connect', context))
    require({i['native_id'] for i in inv['interfaces']} == expected_ids, 'Missing/extra black-box interface')
    require('IF05' not in expected_ids, 'Retired IF-05 reintroduced')
    for i in inv['interfaces']:
        require(f'interface {i["native_id"]} : {i["type"]} connect {i["actor"]}.p to framework.{i["port"]}' in context, 'Interface native endpoint/type mismatch')
        native_delegation = re.search(r'bind '+i['port']+r' = (L\d\d\.p\d\d);', logical)
        require(i['delegation'] == (native_delegation[1] if native_delegation else None), 'Missing native logical port delegation')
        port_body = re.search(r'port def ' + i['port_type'] + r' :> P\d\d \{(.*?)\n    \}', specs, re.S)[1]
        port_features = {name: (direction, typ) for direction, name, typ in re.findall(r'(in|out) item (\w+) : (\w+)', port_body)}
        require(len({f['feature'] for f in i['flows']}) == len(i['flows']), 'Duplicate black-box feature')
        require({f['feature']: (f['direction'], f['type']) for f in i['flows']} == port_features, 'Interface direction/type/feature coverage mismatch')
        for f in i['flows']:
            if i['port'] in ('p03', 'p04'):
                aliases, endpoint = set(), 'L03.'+i['port']+'.'+f['feature']
                for left, right in re.findall(r'bind ([\w.]+) = ([\w.]+);', logical):
                    field = right if left == endpoint else left if right == endpoint else None
                    if field and re.fullmatch(r'L03\.io\.fr\d\d(?:Inputs|Outputs)\.field\d+', field):
                        aliases.add(field_ref(field).removeprefix('FR-'))
                shown_aliases = set(f['internal_field_aliases'].split('/')) if f['internal_field_aliases'] else set()
                require(shown_aliases == aliases, 'Native port-field alias coverage mismatch')
            origin, destination = ('client', 'framework') if f['direction'] == 'in' else ('framework', 'client')
            require(f'flow {f["name"]} of {f["type"]} from {origin}.{f["feature"]} to {destination}.{f["feature"]};' in context, 'Context flow mismatch')
            source = f'{i["actor"]}.p.{f["feature"]}' if f['direction'] == 'in' else f'framework.{i["port"]}.{f["feature"]}'
            target = f'framework.{i["port"]}.{f["feature"]}' if f['direction'] == 'in' else f'{i["actor"]}.p.{f["feature"]}'
            require((f['source'], f['target'], f['kind']) == (source, target, 'information'), 'Interface native endpoint/kind mismatch')
    require({r['name'] for r in inv['boundary_routes']} == {r['name'] for r in ledger['native_contract']['boundary_routes']}, 'Boundary refinement coverage mismatch')
    for route, authoritative in zip(inv['boundary_routes'], ledger['native_contract']['boundary_routes']):
        require(all(route[key] == value for key, value in authoritative.items()), 'Boundary route meaning mismatch')
        source = route['source'].removeprefix('FrameworkLogical::LogicalFramework::').replace('::', '.')
        target = route['target'].removeprefix('FrameworkLogical::LogicalFramework::').replace('::', '.')
        if route['name'] == 'componentProperties':
            require('bind p02.sourceSubmission = projectComponentProperties.source;' in logical and
                'flow componentProperties of ComponentDesignData from projectComponentProperties.configuration to '+target+';' in logical,
                'Native boundary projection mismatch')
        else:
            binding = f'bind {source} = {target};' in logical or f'bind {target} = {source};' in logical
            flow = f'flow {route["name"]} of {route["type"]} from {source} to {target};' in logical
            require(binding or flow, 'Native boundary route endpoint/type mismatch: '+route['name'])
    require({f['native'].split('::')[-1] for f in ledger['native_contract']['boundary_flows']} <= {r['name'] for r in inv['boundary_routes']}, 'Uninventoried boundary flow')


class Page:
    def __init__(self, title, subtitle):
        self.title = title
        self.metrics = METRICS
        self.root = ET.Element(f'{{{NS}}}svg', {'width': f'{W}pt', 'height': f'{H}pt', 'viewBox': f'0 0 {W} {H}', 'role': 'img', 'aria-label': title})
        ET.SubElement(self.root, f'{{{NS}}}title').text = title
        self.el('rect', x=0, y=0, width=W, height=H, fill='white')
        defs = self.el('defs')
        for name in ('info', 'control'):
            arrow_marker(self, defs, name)
        self.text(title, 8, 18, 15, weight='bold')
        self.text(subtitle, 8, 34, FONT, color=MUTED)

    def el(self, tag, parent=None, **attrs):
        return ET.SubElement(self.root if parent is None else parent, f'{{{NS}}}{tag}', {k.replace('_', '-'): str(v) for k, v in attrs.items()})

    def text(self, value, x, y, size=FONT, weight='normal', color=INK, anchor='start', parent=None, **attrs):
        width = METRICS.measure(value, size, weight)
        left = x-width/2 if anchor == 'middle' else x-width if anchor == 'end' else x
        require(0 <= left and left+width <= W, 'Label exceeds page: '+value)
        node = self.el('text', parent, x=x, y=y, font_family=FONT_STACK, font_size=size, font_weight=weight, fill=color, text_anchor=anchor, **attrs)
        node.text = value
        return node

    def lines(self, lines, x, y, parent=None, leading=12, **attrs):
        for line in lines:
            self.text(line, x, y, parent=parent, **attrs)
            y += leading

    def wrapped(self, value, width):
        lines = ['']
        for word in value.split():
            candidate = (lines[-1]+' '+word).strip()
            if METRICS.measure(candidate) > width:
                require(lines[-1], 'Word exceeds available label width: '+word)
                lines.append(word)
            else:
                lines[-1] = candidate
        return lines

    def rect(self, x, y, w, h, parent=None, fill=LIGHT, color=INK, **attrs):
        return self.el('rect', parent, x=x, y=y, width=w, height=h, fill=fill, stroke=color, stroke_width='.8', **attrs)

    def framework(self, x, y, w, h, label_x=None):
        g = self.el('g', data_system='Framework')
        self.rect(x, y, w, h, g, fill='white', color=INK, data_enclosure='Framework')
        self.text('Framework', label_x if label_x is not None else x+8, y+14, 12, weight='bold', parent=g)
        return g

    def box(self, cid, x, y, w, h, parent, occurrence, lines=None):
        g = self.el('g', parent, data_component=cid, data_occurrence=occurrence)
        self.rect(x, y, w, h, g, fill='white', color=INK)
        labels = lines or GROUP_NAMES[cid]
        require(' '.join(labels) == cid+' '+CANONICAL_NAMES[cid], 'Incomplete component box name')
        for label in labels:
            require(METRICS.measure(label, weight='bold') <= w-8, 'Component name exceeds box: '+label)
        self.lines(labels, x+w/2, y+(h-12*(len(labels)-1))/2+4, parent=g, weight='bold', anchor='middle')
        return g

    def actor(self, key, lines, x, y, w, h, label_y=None):
        g = self.el('g', data_actor=key)
        self.rect(x, y, w, h, g, fill=LIGHT, color=INK)
        self.lines(lines, x+w/2, label_y if label_y is not None else y+17, parent=g, weight='bold', anchor='middle')
        return g

    def port(self, interface, x, levels, parent):
        return shared_port(self, parent, interface['id'], interface['port'], x, levels,
                           [flow['feature'] for flow in interface['flows']])

    def arrow(self, d, identifier, kind='information', parent=None, bridge=False, style=None, head=True):
        if bridge:
            self.el('path', parent, d=d, fill='none', stroke='white', stroke_width='4', data_crossing='no junction')
        style = 'dashed' if kind == 'control' else style or information_style(identifier.removeprefix('arrow-'))
        properties = dict(id=identifier, d=d, fill='none', stroke=INK,
            stroke_width='1.2', data_end_marker=f'url(#{"control" if kind == "control" else "info"})',
            data_terminal_head=str(head).lower(), data_line_style=style, **line_attributes(style))
        return self.el('path', parent, **properties)

    def save(self, path):
        foreground_arrowheads(self.root)
        validate_arrowheads(self.root)
        validate_port_labels(self.root)
        ET.indent(self.root)
        ET.ElementTree(self.root).write(path, encoding='utf-8', xml_declaration=True)


def peer_geometry():
    return {
        'E01': ('M148 83 H278', 158, 64), 'E02': ('M278 104 H148', 151, 121),
        'E03': ('M408 83 H542', 419, 64), 'E04': ('M542 104 H408', 419, 121),
        'E05': ('M662 115 V184', 582, 147), 'E06': ('M542 214 H408', 419, 195),
        'E07': ('M34 115 V200 H278', 150, 176), 'E08': ('M331 115 V184', 342, 147),
        'E09': ('M408 221 H525 V148 H568 V115', 419, 167),
        'E10': ('M278 221 H122 V115', 150, 234),
    }


def peer_group(page, exchange, d, x, y, parent):
    g = page.el('g', parent, id=exchange['id'], data_exchange=exchange['name'],
        data_source=exchange['source_component'], data_target=exchange['target_component'],
        data_kind=exchange['kind'], data_type=exchange['payload_type'])
    page.arrow(d, 'arrow-'+exchange['id'], exchange['kind'], g, bridge=exchange['id'] in ('E09', 'E10'))
    page.lines(PEER_LABELS[exchange['name']], x, y, g, color=CONTROL if exchange['kind'] == 'control' else INFO)


def internal_page(inv):
    page = Page('Logical architecture: component cooperation', 'Twenty native peer bundles. Repeated parts retain the same full names and responsibilities.')
    frame = page.framework(8, 44, 674, 370)
    for cid, x, y in [('L01', 18, 73), ('L02', 278, 73), ('L03', 542, 73), ('L05', 278, 184), ('L04', 542, 184)]:
        page.box(cid, x, y, 130, 42, frame, 'engineering')
    byid = {e['id']: e for e in inv['peer_exchanges']}
    for identifier, (d, x, y) in peer_geometry().items():
        peer_group(page, byid[identifier], d, x, y, frame)
    page.lines(['Check and', 'advise'], 52, 142, color=MUTED, parent=frame)
    page.text('Configuration exchanges (same parts, repeated for this concern)', 18, 261, weight='bold', parent=frame)
    for index, cid in enumerate(('L01', 'L02', 'L03', 'L04', 'L05')):
        x = 18 + index*132
        page.box(cid, x, 270, 126, 34, frame, 'configuration')
        incoming = f'E{11+index:02}'
        outgoing = {'L01': 'E16', 'L02': 'E18', 'L03': 'E17', 'L04': 'E19', 'L05': 'E20'}[cid]
        peer_group(page, byid[incoming], f'M{x+4} 304 V376', x+11, 318, frame)
        peer_group(page, byid[outgoing], f'M{x+122} 376 V304', x+11, 350, frame)
    page.box('L06', 18, 376, 654, 36, frame, 'configuration',
        ['L06 Configuration and controlled exchange'])
    return page


# Each group refines one native aggregate, to ONE actual responsible component.
# The native root contracts determine component ownership. Independent types
# remain separate in the inventory. No aggregate is replicated to every part.
REFINEMENT_VIEWS = [
    (['guidanceSubmission', 'traceQuerySubmission', 'requirementSubmission'], 'M123 150 H143 V105 H273', ['Requirements,', 'guidance & trace', 'queries'], 174, 74),
    (['missionSubmission', 'designSubmission'], 'M123 150 H143 V160 H273', ['Mission &', 'design'], 174, 137),
    (['viewSelectionSubmission', 'assessmentPlanSubmission', 'reviewRequestSubmission'], 'M123 150 H143 V285 H273', ['Views, V&V plans', '& review baseline'], 174, 264),
    (['engineeringCompatibility'], 'M123 150 H143 V356 H273', ['Raw submission', 'for transfer checks'], 174, 332),
    (['baselineRetrievalSubmission', 'changeSubmission'], 'M123 150 H143 V390 H273', ['Changes &', 'baseline retrieval'], 174, 368),
    (['guidanceResponse'], 'M273 114 H160 V250 H123', ['Guidance'], 174, 126),
    (['assessmentResponse'], 'M273 312 H160 V250 H123', ['Assessments'], 174, 306),
    (['sourceMethods'], 'M562 150 H542 V90 H429', ['Sources & methods'], 439, 79),
    (['componentProperties'], 'M562 150 H542 V158 H429', ['Projected component', 'properties'], 436, 135),
    (['referenceSubmission'], 'M562 150 H542 V225 H429', ['Reference data'], 439, 213),
    (['sourceCompatibility'], 'M562 150 H542 V386 H429', ['Raw sources for', 'transfer checks'], 439, 364),
    (['boundedSourceQuery'], 'M429 110 H552 V260 H562', ['Bounded queries'], 439, 122),
]


def route_flow(route):
    if '::p01::engineeringSubmission' in route['source']:
        return 'X01.1'
    if '::p01::engineeringResponse' in route['target']:
        return 'X01.2'
    if '::p02::sourceSubmission' in route['source']:
        return 'X02.1'
    require(route['name'] == 'boundedSourceQuery', 'Unmapped boundary refinement')
    return 'X02.2'


def route_component(route):
    components = re.findall(r'::(L\d\d)::', route['source']+' '+route['target'])
    require(len(components) == 1, 'Boundary refinement must name one concrete component')
    return components[0]


def flow_group(page, interface, flow, d, labels, x, y, parent=None):
    g = page.el('g', parent, id=flow['id'], data_flow=flow['name'], data_feature=flow['feature'],
        data_source=flow['source'], data_target=flow['target'], data_type=flow['type'], data_kind=flow['kind'],
        data_interface=interface['id'], data_port=interface['port'], data_delegation=interface['delegation'] or '')
    page.arrow(d, 'arrow-'+flow['id'], parent=g,
               head=bool(interface['delegation'] or flow['direction'] == 'out'))
    page.lines(labels, x, y, g, color=INFO)
    return g


def external_geometry(identifier, direction):
    # The complete visible route ends at the ACTUAL part for delegated ports.
    ordinal = int(identifier.split('.')[1])
    if identifier.startswith('X03'):
        y, a, b = 101+(ordinal-1)*47, 120, 290
    elif identifier.startswith('X04'):
        y, a, b = 111+(ordinal-1)*54, 586, 444
    elif identifier.startswith('X06'):
        y, a, b = (294 if ordinal == 1 else 315), 592, 429
    else:
        fixed = {'X01.1': (150, 101, 123), 'X01.2': (250, 101, 123),
                 'X02.1': (150, 592, 562), 'X02.2': (260, 592, 562)}
        y, a, b = fixed[identifier]
    return f'M{a} {y} H{b}' if direction == 'in' else f'M{b} {y} H{a}'


def boundary_page(inv):
    page = Page('Logical architecture: engineering, sources and review', 'Boundary ports refine submissions to named parts. Branches carry only their labeled native meanings.')
    frame = page.framework(123, 49, 439, 351, label_x=316)
    for cid, y, h in [('L01', 77, 47), ('L02', 137, 44), ('L04', 204, 44), ('L05', 271, 50), ('L06', 338, 54)]:
        page.box(cid, 273, y, 156, h, frame, 'boundary')
    page.actor('engineers', ['Engineers and', 'stakeholders'], 8, 68, 93, 210)
    page.actor('sources', ['Knowledge and', 'data sources'], 592, 68, 90, 202)
    page.actor('reviewers', ['Reviewers and', 'authority'], 592, 288, 90, 88, label_y=343)
    for interface in inv['interfaces']:
        if interface['id'] in ('IF-01', 'IF-02', 'IF-06'):
            levels = [path_points(external_geometry(flow['id'], flow['direction']))[0][1]
                      for flow in interface['flows']]
            page.port(interface, 123 if interface['port'] == 'p01' else 562, levels, frame)
    for names, d, labels, x, y in REFINEMENT_VIEWS:
        routes = [next(r for r in inv['boundary_routes'] if r['name'] == name) for name in names]
        owners = {route_component(r) for r in routes}
        flow_ids = {route_flow(r) for r in routes}
        require(len(owners) == len(flow_ids) == 1, 'Refinement group mixes owners or native flows')
        g = page.el('g', frame, id='ref-'+routes[0]['id'], data_routes=','.join(r['id'] for r in routes),
            data_component_endpoint=next(iter(owners)), data_flow_parent=next(iter(flow_ids)))
        outgoing = next(iter(flow_ids)) in ('X01.2', 'X02.2')
        page.arrow(d, 'arrow-ref-'+routes[0]['id'], parent=g,
            bridge=outgoing, style=information_style(next(iter(flow_ids))), head=not outgoing)
        page.lines(labels, x, y, g, color=INFO)
    positions = {'X01.1': (16, 117, 78), 'X01.2': (16, 193, 78),
        'X02.1': (599, 117, 77), 'X02.2': (599, 249, 77),
        'X06.1': (439, 261, 100), 'X06.2': (439, 329, 100)}
    for interface in inv['interfaces']:
        if interface['id'] not in ('IF-01', 'IF-02', 'IF-06'):
            continue
        for flow in interface['flows']:
            x, y, width = positions[flow['id']]
            flow_group(page, interface, flow, external_geometry(flow['id'], flow['direction']),
                page.wrapped(EXTERNAL_LABELS[flow['id']], width), x, y)
    return page


def tool_page(inv):
    page = Page('Logical architecture: spacecraft simulation and host integration', 'External spacecraft and host flows cross Framework ports. L03 executes EPS and RAM analyses and assesses engineering criteria.')
    frame = page.framework(280, 49, 174, 323, label_x=332)
    page.box('L03', 290, 80, 154, 280, frame, 'tools')
    page.actor('tools', ['NVIDIA Omniverse', 'spacecraft and', 'subsystem simulations'], 8, 80, 112, 280, label_y=205)
    software = page.actor('software', ['F Prime host', 'toolchain'], 586, 80, 96, 280, label_y=211)
    actor_rect = software.find('./{*}rect')
    actor_left = float(actor_rect.attrib['x'])-float(actor_rect.attrib['stroke-width'])/2
    for interface in inv['interfaces']:
        if interface['id'] not in ('IF-03', 'IF-04'):
            continue
        levels = [path_points(external_geometry(flow['id'], flow['direction']))[0][1]
                  for flow in interface['flows']]
        port = page.port(interface, 280 if interface['port'] == 'p03' else 454, levels, frame)
        left = interface['port'] == 'p03'
        x, width = 129, 141
        if not left:
            # Keep six units beyond the painted port and actor edges.
            x = float(port.attrib['x'])+float(port.attrib['width'])+float(port.attrib['stroke-width'])/2+6
            width = actor_left-6-x
        for ordinal, flow in enumerate(interface['flows']):
            y = 101+ordinal*47 if left else 111+ordinal*54
            labels = page.wrapped(EXTERNAL_LABELS[flow['id']], width)
            flow_group(page, interface, flow, external_geometry(flow['id'], flow['direction']), labels, x, y-8-12*(len(labels)-1))
    return page


def path_points(d):
    return orthogonal_points(d)


def bounds(rect):
    return tuple(float(rect.attrib[a]) for a in ('x', 'y', 'width', 'height'))


def within(point, box):
    x, y, w, h = box
    return x-.1 <= point[0] <= x+w+.1 and y-.1 <= point[1] <= y+h+.1


def on_edge(point, box):
    x, y, w, h = box
    return within(point, box) and min(abs(point[0]-x), abs(point[0]-x-w), abs(point[1]-y), abs(point[1]-y-h)) < .1


def tool_label_clearance_check(root):
    """Measure host labels against the painted shared port and actor edges."""
    port = root.find('.//{*}rect[@data-interface="IF-04"][@data-port]')
    actor = root.find('./{*}g[@data-actor="software"]/{*}rect')
    require(port is not None and actor is not None, 'Missing host port or actor')
    port_right = float(port.attrib['x'])+float(port.attrib['width'])+float(port.attrib['stroke-width'])/2
    actor_left = float(actor.attrib['x'])-float(actor.attrib['stroke-width'])/2
    groups = root.findall('./{*}g[@data-interface="IF-04"][@data-flow]')
    require(len(groups) == 5, 'Missing host exchange labels')
    for group in groups:
        labels = group.findall('./{*}text')
        require(labels, 'Missing host exchange label: '+group.attrib['id'])
        for text in labels:
            size = float(text.attrib['font-size'])
            require(size >= FONT and 'transform' not in text.attrib, 'Unreadable host exchange label')
            width = METRICS.measure(text.text or '', size, text.attrib.get('font-weight', 'normal'))
            anchor = text.attrib.get('text-anchor', 'start')
            x = float(text.attrib['x'])
            left = x-width/2 if anchor == 'middle' else x-width if anchor == 'end' else x
            require(left-port_right >= 6-1e-6,
                    'Host exchange label does not clear IF-04 port: '+group.attrib['id'])
            require(actor_left-left-width >= 6-1e-6,
                    'Host exchange label does not clear F Prime actor: '+group.attrib['id'])
    return {'host_exchange_labels_clear_port_and_actor_checked': True}


def arrow_check(g, identifier, kind, style=None, head=True):
    arrow = g.find('./{*}path[@id="'+identifier+'"]')
    require(arrow is not None and arrow.attrib.get('id') == identifier, 'Missing real directed arrow: '+identifier)
    style = 'dashed' if kind == 'control' else style or information_style(identifier.removeprefix('arrow-'))
    require(arrow.attrib.get('data-line-style') == style and
        arrow.attrib.get('stroke-dasharray') == LINE_PATTERNS[style], 'Lost information/control line pattern')
    require(arrow.attrib.get('data-end-marker') == f'url(#{"control" if kind == "control" else "info"})'
            and arrow.attrib.get('data-terminal-head') == str(head).lower()
            and 'marker-end' not in arrow.attrib, 'Wrong or duplicated terminal arrowhead')
    return arrow, path_points(arrow.attrib['d'])


def display_check(inv, paths):
    """Validate visible names, containment, real endpoints and native crosswalks."""
    roots = [ET.parse(path).getroot() for path in paths]
    require(len(roots) == 3, 'Expected three coordinated architecture views')
    peers, flows, refinements, components, actors, frames, ports = {}, {}, {}, {}, {}, {}, {}
    for page, root in enumerate(roots, 1):
        fg = root.find('./{*}g[@data-system="Framework"]')
        require(fg is not None, 'Missing Framework containment')
        frame = fg.find('./{*}rect[@data-enclosure="Framework"]')
        require(frame is not None and any(t.text == 'Framework' for t in fg.findall('./{*}text')), 'Missing visible Framework enclosure')
        frames[page] = bounds(frame)
        for g in root.findall('.//{*}g'):
            if 'data-component' in g.attrib:
                cid = g.attrib['data-component']
                require(cid in CANONICAL_NAMES and g in list(fg.iter()), 'Component outside Framework containment')
                labels = ' '.join(t.text or '' for t in g.findall('./{*}text'))
                require(labels == cid+' '+CANONICAL_NAMES[cid], 'Incomplete canonical component name in displayed box')
                box = bounds(g.find('./{*}rect'))
                require(within((box[0], box[1]), frames[page]) and within((box[0]+box[2], box[1]+box[3]), frames[page]), 'Component outside Framework containment')
                key = (page, cid, g.attrib['data-occurrence'])
                require(key not in components, 'Duplicate component occurrence')
                components[key] = box
            if 'data-actor' in g.attrib:
                require(g not in list(fg.iter()), 'External participant inside Framework')
                box = bounds(g.find('./{*}rect'))
                x, y, w, h = box
                fx, fy, fw, fh = frames[page]
                require(x+w < fx or x > fx+fw or y+h < fy or y > fy+fh, 'External participant overlaps Framework')
                require(' '.join(t.text or '' for t in g.findall('./{*}text')) == ACTORS[g.attrib['data-actor']], 'Missing visible external participant/responsibility')
                actors[(page, g.attrib['data-actor'])] = box
            destination = peers if 'data-exchange' in g.attrib else flows if 'data-flow' in g.attrib else refinements if 'data-routes' in g.attrib else None
            if destination is not None:
                require(g.attrib['id'] not in destination, 'Duplicate displayed arrow')
                destination[g.attrib['id']] = (page, g)
        ports[page] = root.findall('.//{*}rect[@data-port]')
        require(len(ports[page]) == (0 if page == 1 else 3 if page == 2 else 2),
                'Expected one shared port rectangle per interface')
        require(len({p.attrib['data-port'] for p in ports[page]}) == len(ports[page]),
                'Visually repeated interface port')
        visible = ' '.join(t.text or '' for t in root.findall('.//{*}text'))
        require(not re.search(r'\bp\d+\b', visible), 'Unnecessary port labels in diagram')
        require('Framework boundary' not in visible and not re.search(r'L\d\d\s*,\s*L\d\d', visible), 'Collapsed boundary pseudo-component')
        require(not re.search(r'FR-\d\d|\b\d\d\.[io]\d\d|\bfield\d+\b|\b(?:Inputs|Outputs)\b', visible), 'Implementation field labels leaked into report diagram')
    require({key[1] for key in components} == set(CANONICAL_NAMES), 'Missing component responsibility')
    require(set(peers) == {e['id'] for e in inv['peer_exchanges']}, 'Missing/extra displayed peer bundle')
    for exchange in inv['peer_exchanges']:
        page, g = peers[exchange['id']]
        for attr, key in [('exchange', 'name'), ('source', 'source_component'), ('target', 'target_component'), ('kind', 'kind'), ('type', 'payload_type')]:
            require(g.attrib['data-'+attr] == exchange[key], 'Displayed peer endpoint/type/kind mismatch')
        labels = [t.text or '' for t in g.findall('./{*}text')]
        require(labels == PEER_LABELS[exchange['name']], 'Missing/changed meaningful peer label')
        arrow, points = arrow_check(g, 'arrow-'+exchange['id'], exchange['kind'])
        occurrence = 'engineering' if int(exchange['id'][1:]) <= 10 else 'configuration'
        require(on_edge(points[0], components[(page, exchange['source_component'], occurrence)]) and
            on_edge(points[-1], components[(page, exchange['target_component'], occurrence)]), 'Reversed/disconnected rendered peer arrow')
        require(all(within(p, frames[page]) for p in points), 'Peer arrow leaves Framework')
        if occurrence == 'engineering':
            require(arrow.attrib['d'] == peer_geometry()[exchange['id']][0], 'Changed peer route geometry')
        exchange['display'] = {'page': page, 'arrow': arrow.attrib['id'], 'label': ' '.join(labels),
            'abstraction': 'All fields of this native directed bundle.'}
        for mapping in exchange['mappings']:
            mapping['display'] = dict(exchange['display'])
    all_flows = [f for i in inv['interfaces'] for f in i['flows']]
    require(set(flows) == {f['id'] for f in all_flows}, 'Missing/extra displayed interface flow')
    for interface in inv['interfaces']:
        pages = set()
        for flow in interface['flows']:
            page, g = flows[flow['id']]
            pages.add(page)
            for key in ('source', 'target', 'type', 'kind'):
                require(g.attrib['data-'+key] == flow[key], 'Displayed interface flow mismatch')
            require(g.attrib['data-port'] == interface['port'] and g.attrib['data-interface'] == interface['id'] and
                g.attrib['data-delegation'] == (interface['delegation'] or ''), 'Displayed interface delegation mismatch')
            labels = ' '.join(t.text or '' for t in g.findall('./{*}text'))
            require(labels == EXTERNAL_LABELS[flow['id']], 'Missing/changed meaningful external label')
            arrow, points = arrow_check(g, 'arrow-'+flow['id'], 'information',
                head=bool(interface['delegation'] or flow['direction'] == 'out'))
            require(arrow.attrib['d'] == external_geometry(flow['id'], flow['direction']), 'Reversed/disconnected rendered interface arrow')
            outside, inside = (points[0], points[-1]) if flow['direction'] == 'in' else (points[-1], points[0])
            require(on_edge(outside, actors[(page, interface['actor'])]), 'Disconnected external actor endpoint')
            if interface['delegation']:
                cid = interface['delegation'].split('.')[0]
                occurrence = 'tools' if page == 3 else 'boundary'
                require(on_edge(inside, components[(page, cid, occurrence)]), 'Disconnected responsible LC endpoint')
            else:
                require(on_edge(inside, frames[page]), 'Disconnected boundary port endpoint')
            boundary_ports = [p for p in ports[page] if p.attrib['data-port'] == interface['port'] and
                p.attrib['data-owner'] == 'Framework']
            require(len(boundary_ports) == 1, 'Missing/duplicate shared boundary port')
            port = boundary_ports[0]
            require(port.attrib['data-interface'] == interface['id'] and
                set(port.attrib['data-features'].split(',')) == {f['feature'] for f in interface['flows']},
                'Shared port omits or mixes interface flows')
            pb = bounds(port)
            crossing = (float(port.attrib['data-boundary-x']), points[0][1])
            require(on_edge(crossing, frames[page]) and within(crossing, pb) and
                min(points[0][0], points[-1][0]) <= crossing[0] <= max(points[0][0], points[-1][0]),
                'Arrow does not pass through its shared boundary port')
            flow['display'] = {'page': page, 'arrow': arrow.attrib['id'], 'label': labels,
                'delegation': interface['delegation'], 'boundary_port_crossing': list(crossing)}
        require(len(pages) == 1, 'An interface split across unrelated views')
        interface['display'] = {'page': next(iter(pages)), 'port': interface['port'],
            'delegation': interface['delegation'], 'shared_port_rectangle': list(pb)}
    for alias in inv['external_aliases']:
        feature = alias['endpoint_declaration'].split('::')[-1]
        matches = [f for f in all_flows if f['feature'] == feature]
        require(len(matches) == 1 and matches[0]['qualified_type'] == alias['type'] and matches[0]['direction'] == alias['direction'], 'Logical external alias differs from displayed black-box flow')
        alias['display'] = matches[0]['display']
    byroute = {r['id']: r for r in inv['boundary_routes']}
    covered = set()
    expected_groups = {frozenset(names): (d, labels) for names, d, labels, x, y in REFINEMENT_VIEWS}
    require(len(refinements) == len(expected_groups), 'Missing/extra displayed boundary refinement branch')
    for page, g in refinements.values():
        identifiers = g.attrib['data-routes'].split(',')
        require(not covered.intersection(identifiers) and set(identifiers) <= set(byroute), 'Duplicate/extra boundary refinement mapping')
        routes = [byroute[i] for i in identifiers]
        owners, parent_flows = {route_component(r) for r in routes}, {route_flow(r) for r in routes}
        require(len(owners) == len(parent_flows) == 1, 'Duplicated whole aggregate across components')
        cid, fid = next(iter(owners)), next(iter(parent_flows))
        require(g.attrib['data-component-endpoint'] == cid and g.attrib['data-flow-parent'] == fid, 'Wrong concrete boundary ownership')
        names = frozenset(r['name'] for r in routes)
        require(names in expected_groups, 'Invented boundary refinement grouping')
        expected_d, expected_labels = expected_groups[names]
        require([t.text or '' for t in g.findall('./{*}text')] == expected_labels, 'Changed boundary refinement meaning')
        flow = next(f for f in all_flows if f['id'] == fid)
        arrow, points = arrow_check(g, 'arrow-'+g.attrib['id'], 'information',
            information_style(fid), head=flow['direction'] == 'in')
        inner, boundary = (points[-1], points[0]) if flow['direction'] == 'in' else (points[0], points[-1])
        require(on_edge(inner, components[(page, cid, 'boundary')]), 'Disconnected/reversed actual LC refinement arrow')
        require(list(boundary) == flow['display']['boundary_port_crossing'], 'Refinement detached from its shared boundary port')
        require(arrow.attrib['d'] == expected_d and all(within(p, frames[page]) for p in points), 'Changed/disconnected boundary branch geometry')
        for route in routes:
            route['display'] = {'page': page, 'arrow': arrow.attrib['id'], 'parent_flow': fid, 'component': cid,
                'component_name': cid+' '+CANONICAL_NAMES[cid], 'label': ' '.join(expected_labels),
                'abstraction': 'Named native refinement to this concrete component, not aggregate ownership.'}
        covered.update(identifiers)
    require(covered == set(byroute), 'Missing native-to-displayed boundary refinement')
    visible = ' '.join(t.text or '' for root in roots for t in root.findall('.//{*}text'))
    caption_text = ' '.join(re.findall(r'\\caption(?:\[[^\]]*\])?\{([^{}]*)\}',
                                       (REPORT / 'logical.tex').read_text()))
    require(all(note in caption_text for note in AUTHORITY_NOTES),
            'Missing engineering authority note in figure captions')
    require(RESPONSIBILITIES['L01'] in visible and RESPONSIBILITIES['L03'] in caption_text,
            'Missing accepted responsibility wording in diagram or caption')
    require(all(annotation not in visible for annotation in ('Execute EPS and RAM', 'Assess engineering criteria')),
            'Removed in-part behavior annotation reintroduced')
    host_checks = tool_label_clearance_check(roots[2])
    return {**host_checks, 'tool_execution_and_assessment_caption_checked': True,
        'all_20_native_bundles_mapped_to_meaningful_arrows': True,
        'all_203_field_mappings_retained_and_mapped_to_native_bundle': sum(len(e['mappings']) for e in inv['peer_exchanges']) == 203,
        'all_17_black_box_flows_displayed_once': True, 'all_5_active_interfaces_displayed': True,
        'all_18_boundary_refinements_connected_to_actual_parts': True,
        'full_canonical_name_in_every_component_box': True, 'Framework_containment_and_external_participants_checked': True,
        'actual_peer_external_and_refinement_arrow_endpoints_checked': True,
        'one_shared_port_rectangle_per_interface_checked': True,
        'terminal_heads_exclude_intermediate_port_crossings_checked': True,
        'native_delegation_to_actual_parts_checked': True, 'collapsed_boundary_pseudo_components_excluded': True,
        'distinct_information_patterns_and_dashed_control_checked': True, 'authority_caption_notes_checked': True,
        'implementation_field_labels_excluded': True}


def native_check():
    checker_path = REPORT / 'sysml/check_logical_responsibilities.py'
    spec = importlib.util.spec_from_file_location('logical_coverage_native_checker', checker_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    tool_path = Path('/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py')
    spec = importlib.util.spec_from_file_location('logical_coverage_native_tool', tool_path)
    tool = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tool
    spec.loader.exec_module(tool)
    ledger = json.loads((REPORT / 'traceability/logical-architecture.json').read_text())
    source = checker.validate_source_contract(ledger, (REPORT / 'requirements.tex').read_text(), (REPORT / 'logical.tex').read_text())
    native = checker.Native(tool, REPORT / 'sysml', checker.CORE_FILES)
    checker.check_native_source(native, ledger, source)
    checks = checker.check_native_architecture(native, ledger)
    checks.update(status='passed', native_errors=0, native_warnings=0, scope='nine-file native logical core, planned design consistency only')
    return checks


def main():
    global METRICS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', type=Path, required=True)
    parser.add_argument('--native-check', action='store_true')
    parser.add_argument('--coverage', type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(ROOT != job and ROOT not in job.parents, 'Check artifacts must remain outside the checkout')
    job.mkdir(parents=True, exist_ok=True)
    METRICS = SerifMetrics()
    inv = inventory()
    # Refresh presentation labels without changing retained native field contracts.
    for alias in inv['external_aliases']:
        if alias['endpoint_declaration'] == 'BoundaryViews::AnalysisPort::spacecraftInputs':
            alias['label'] = 'Identified mission/scenario conditions'
    pages = [internal_page(inv), boundary_page(inv), tool_page(inv)]
    paths, pdfs, artifacts = [], [], {}
    for index, page in enumerate(pages, 1):
        stem = BASE if index == 1 else BASE.with_name(BASE.name + f'-panel-{index:02}')
        svg, pdf, png = (stem.with_suffix('.'+kind) for kind in ('svg', 'pdf', 'png'))
        page.save(svg)
        paths.append(svg)
        one_pdf = pdf if index != 1 else BASE.with_name(BASE.name+'-overview.pdf')
        run(['rsvg-convert', '--format=pdf', '--output', str(one_pdf), str(svg)])
        pdfs.append(one_pdf)
        run(['pdftoppm', '-r', '144', '-png', '-singlefile', str(one_pdf), str(stem)])
        bbox = job / f'panel-{index:02}-bounds.html'
        run(['pdftotext', '-bbox', str(one_pdf), str(bbox)])
        words = ET.parse(bbox).getroot().findall('.//{*}word')
        for word in words:
            require(0 <= float(word.attrib['xMin']) <= float(word.attrib['xMax']) <= W and
                0 <= float(word.attrib['yMin']) <= float(word.attrib['yMax']) <= H, 'PDF text clipped: '+str(word.text))
        require(len(words) > 30, 'Missing searchable PDF labels')
        for artifact in (svg, png, one_pdf):
            artifacts[artifact.name] = sha(artifact)
    run(['pdfunite', *map(str, pdfs), str(BASE.with_suffix('.pdf'))])
    normalize_document_id(BASE.with_suffix('.pdf'))
    artifacts[BASE.with_suffix('.pdf').name] = sha(BASE.with_suffix('.pdf'))
    checks = display_check(inv, paths)
    for page in pages:
        checks.update(validate_style(page.root))
        checks.update(validate_arrowheads(page.root))
        checks.update(validate_port_labels(page.root))
    checks.update(pdf_text_within_page=True, pdf_pages=len(pages), minimum_font_pt=FONT,
        panel_physical_dimensions_pt=[W, H], publication_preview_dpi=144,
        native_semantic_validation=native_check() if args.native_check else 'not run in this invocation')
    inv['checks'], inv['generator_sha256'] = checks, sha(Path(__file__).resolve())
    inv['style_sha256'] = sha(FIG / 'diagram_style.py')
    inv['panels'] = [{'page': i+1, 'title': page.title, 'svg': str(path.relative_to(ROOT)),
        'png': str(path.with_suffix('.png').relative_to(ROOT))} for i, (page, path) in enumerate(zip(pages, paths))]
    inv['semantics'] = 'Planned logical exchanges. Solid, dotted and dash-dot patterns distinguish information routes. Dashed routes carry only L06 control bundles. Human decisions are information. Boundary branches retain their recorded meanings. IF-05 is retired.'
    inv['render_source_sha256'] = {path.name: sha(path) for path in paths}
    inv['book_visual_examples'] = BOOK_EXAMPLES
    inventory_path = BASE.with_suffix('.inventory.json')
    inventory_path.write_text(json.dumps(inv, indent=2)+'\n')
    if args.coverage:
        args.coverage.resolve().write_text(json.dumps(inv, indent=2)+'\n')
    provenance = {
        'artifact': 'logical-architecture', 'kind': 'Authored illustrative vector logical architecture',
        'producer': 'logical-architecture.py, three native-derived internal block style views',
        'native_syside_render': False, 'executed_simulation': False,
        'basis': inv.get('source_contract_status', 'Native logical, system-context and interface contracts, and their traceability ledger'),
        'inventory': inventory_path.name, 'counts': inv['counts'], 'checks': checks, 'book_visual_examples': BOOK_EXAMPLES,
        'dimensions': {'each_panel_pt': [W, H], 'pdf_pages': len(pages)},
        'font': dict(METRICS.provenance(), minimum_pt=FONT),
        'generator_sha256': inv['generator_sha256'], 'style_sha256': inv['style_sha256'],
        'source_model_sha256': inv['basis_sha256'],
        'svg_sha256_used_for_pdf': artifacts[BASE.with_suffix('.svg').name],
        'artifact_sha256': {kind: sha(BASE.with_suffix('.'+kind)) for kind in ('svg', 'pdf', 'png')},
        'coordinated_panel_sha256': artifacts,
        'pdf_composition': 'pdfunite of exact rsvg-convert PDF conversions in panel order, with a deterministic nonsemantic trailer document ID. Page 1 corresponds to the base SVG',
        'renderers': {'svg_to_pdf': run(['rsvg-convert', '--version']).strip(), 'SOURCE_DATE_EPOCH': 0,
            'pdf_command': 'rsvg-convert each logical-architecture SVG to its panel PDF, then pdfunite in panel order',
            'png_command': 'pdftoppm -r 144 -png -singlefile <panel.pdf> <panel-stem>'},
        'reproduction': ['python3 final_report/fig/logical-architecture.py --jobdir /absolute/external/check-dir'],
        'visual_review': 'Inspect the regenerated panels and compiled report. Previews are PDF-derived.',
    }
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps({'counts': inv['counts'], 'checks': checks, 'pages': len(pages)}, indent=2))


if __name__ == '__main__':
    main()
