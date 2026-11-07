"""Checks for the report's authored diagrams and three-component architecture.

PYTHONPATH=final_report/fig python3 -m unittest test_diagrams
"""
from __future__ import annotations

from collections import Counter
import copy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from diagram_style import (FONT_STACK, LINE_PATTERNS, SerifMetrics, sha,
                           validate_arrowheads, validate_port_labels, validate_style)

FIG = Path(__file__).resolve().parent
DIAGRAMS = ('framework-context', 'logical-architecture', 'logical-architecture-panel-02',
            'systems-engineering-technical-processes')


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), FIG / (name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logical = load('logical-architecture')
        cls.context = load('framework-context')
        cls.processes = load('systems-engineering-technical-processes')
        cls.inventory = json.loads((FIG / 'logical-architecture.inventory.json').read_text())
        cls.metrics = SerifMetrics()

    def test_every_published_diagram_uses_shared_style(self):
        for name in DIAGRAMS:
            with self.subTest(name=name):
                validate_style(ET.parse(FIG / (name+'.svg')).getroot())

    def test_arrowheads_are_large_and_in_the_foreground(self):
        for name in DIAGRAMS:
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                validate_arrowheads(root)
                ET.SubElement(root, '{http://www.w3.org/2000/svg}rect', {'fill': 'white'})
                with self.assertRaises(ValueError):
                    validate_arrowheads(root)

    def test_one_terminal_head_per_external_flow_and_none_on_port_crossings(self):
        root = ET.parse(FIG / 'logical-architecture-panel-02.svg').getroot()
        validate_arrowheads(root)
        layer = root.find('./{*}g[@data-layer="arrowheads"]')
        self.assertEqual(len(layer), 8)
        self.assertEqual(root.findall('.//{*}path[@marker-end]'), list(layer))
        for interface in self.inventory['interfaces']:
            port = root.find(f'.//{{*}}rect[@data-interface="{interface["id"]}"][@data-port]')
            boundary_x = float(port.attrib['data-boundary-x'])
            for flow in interface['flows']:
                shaft = root.find(f'./{{*}}g[@id="{flow["id"]}"]/{{*}}path')
                self.assertEqual(shaft.attrib['data-terminal-head'], 'true')
                self.assertNotIn('marker-end', shaft.attrib)
                start, end = self.logical.path_points(shaft.attrib['d'])
                self.assertNotEqual(start[0], boundary_x)
                self.assertNotEqual(end[0], boundary_x)
        shaft.attrib['marker-end'] = shaft.attrib['data-end-marker']
        with self.assertRaises(ValueError):
            validate_arrowheads(root)

    def test_interface_labels_are_on_four_shared_port_rectangles(self):
        for name in ('framework-context', 'logical-architecture-panel-02'):
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                ports = root.findall('.//{*}rect[@data-port]')
                self.assertEqual(len(ports), 4)
                self.assertEqual(len({p.attrib['data-interface'] for p in ports}), 4)
                validate_port_labels(root)
                for port in ports:
                    self.assertGreater(float(port.attrib['height']), float(port.attrib['width']))
                    self.assertEqual(len(port.attrib['data-features'].split(',')), 2)
                root.find('.//{*}text[@data-port-label]').attrib['x'] = '0'
                with self.assertRaises(ValueError):
                    validate_port_labels(root)

    def test_diagrams_have_no_extra_port_names_or_bottom_notes(self):
        for name in DIAGRAMS[:-1]:
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                frame = root.find('.//{*}rect[@data-enclosure="Framework"]')
                bottom = float(frame.attrib['y'])+float(frame.attrib['height'])
                for text in root.findall('.//{*}text'):
                    self.assertLessEqual(float(text.attrib['y']), bottom)
                    self.assertIsNone(re.search(r'\bp\d+\b', text.text or ''))

    def test_style_rejects_color_sans_serif_and_rounded_blocks(self):
        for attrs in ({'fill': '#123456'}, {'font-family': 'Arial'}, {'rx': '5'}):
            with self.subTest(attrs=attrs):
                tag = 'text' if 'font-family' in attrs else 'rect'
                root = ET.Element('{http://www.w3.org/2000/svg}svg')
                ET.SubElement(root, '{http://www.w3.org/2000/svg}'+tag, attrs)
                with self.assertRaises(ValueError):
                    validate_style(root)
        self.assertIn('serif', FONT_STACK)

    def test_three_component_names_and_fr_assignments(self):
        expected = {
            'L01': {1, 2, 3, 4, 11, 15, 17, 22, 25, 37, 39},
            'L03': {10, 13, 14, 16, 19, 20, 26, 27, 34},
            'L06': {5, 7, 9},
        }
        self.assertEqual({c['id']: c['name'] for c in self.inventory['components']}, {
            'L01': 'Engineering Interface', 'L03': 'Simulation and Analysis',
            'L06': 'Configuration Management'})
        self.assertEqual({c['id']: {int(fr[-2:]) for fr in c['requirements']}
                          for c in self.inventory['components']}, expected)
        for name in ('logical.tex', 'physical-candidates.tex', 'trade-selection.tex'):
            self.assertNotRegex((FIG.parent / name).read_text(), r'\bL0[245]\b|[Ss]ix logical components')
        for name in ('logical-architecture', 'logical-architecture-panel-02'):
            root = ET.parse(FIG / (name+'.svg')).getroot()
            self.assertNotRegex(' '.join(root.itertext()), r'\bL0[245]\b')

    def test_all_original_producer_consumer_relations_are_retained(self):
        self.logical.inventory_check(self.inventory)
        cross = [m for e in self.inventory['peer_exchanges'] for m in e['mappings']]
        internal = self.inventory['internal_exchanges']
        self.assertEqual(len(self.inventory['peer_exchanges']), 6)
        self.assertEqual(len(cross), 33)
        self.assertEqual(len(internal), 11)
        self.assertEqual(len(cross)+len(internal), 44)
        self.assertEqual(Counter(m['component'] for m in internal), {'L01': 8, 'L03': 3})
        for e in self.inventory['peer_exchanges']:
            self.assertNotEqual(e['source_component'], e['target_component'])

    def test_inventory_rejects_lost_or_misallocated_relations(self):
        incomplete = copy.deepcopy(self.inventory)
        incomplete['peer_exchanges'].pop()
        with self.assertRaises(ValueError):
            self.logical.inventory_check(incomplete)
        invalid = copy.deepcopy(self.inventory)
        invalid['peer_exchanges'][0]['mappings'][0]['source_requirement'] = 'FR-99'
        with self.assertRaisesRegex(ValueError, 'Removed or misallocated requirement'):
            self.logical.inventory_check(invalid)
        internal = copy.deepcopy(self.inventory)
        internal['internal_exchanges'].pop()
        internal['counts'] = self.logical.inventory_counts(internal)
        with self.assertRaisesRegex(ValueError, 'Lost or duplicated'):
            self.logical.inventory_check(internal)

    def test_external_ownership_and_forwarded_inputs_follow_new_components(self):
        self.assertEqual({i['id']: i['component'] for i in self.inventory['interfaces']},
                         {'IF-01': 'L01', 'IF-02': 'L01', 'IF-03': 'L03', 'IF-06': 'L01'})
        routes = {r['name']: r for r in self.inventory['boundary_routes']}
        self.assertEqual((routes['changeSubmission']['component'], routes['changeSubmission']['via_exchange']),
                         ('L06', 'E03'))
        self.assertEqual((routes['componentProperties']['component'], routes['componentProperties']['via_exchange']),
                         ('L03', 'E01'))
        self.assertEqual(routes['referenceSubmission']['component'], 'L01')

    def test_simulation_is_part_of_the_single_external_interface_view(self):
        root = ET.parse(FIG / 'logical-architecture-panel-02.svg').getroot()
        self.assertEqual({g.attrib['data-actor'] for g in root.findall('./{*}g[@data-actor]')},
                         {'engineers', 'sources', 'reviewers', 'tools'})
        self.assertEqual({g.attrib['id'] for g in root.findall('./{*}g[@data-flow]')},
                         set(self.logical.EXTERNAL_LABELS))
        self.assertEqual(len(self.inventory['panels']), 2)
        for suffix in ('svg', 'pdf', 'png'):
            self.assertFalse((FIG / ('logical-architecture-panel-03.'+suffix)).exists())

    def test_names_containment_and_all_directed_endpoints(self):
        paths = [FIG / (name+'.svg') for name in ('logical-architecture', 'logical-architecture-panel-02')]
        self.assertTrue(all(self.logical.display_check(copy.deepcopy(self.inventory), paths).values()))
        root = ET.parse(paths[1]).getroot()
        flow = root.find('./{*}g[@id="X03.1"]/{*}path')
        start, end = self.logical.path_points(flow.attrib['d'])
        flow.attrib['d'] = f'M{end[0]:g} {end[1]:g} H{start[0]:g}'
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / 'boundary.svg'
            ET.ElementTree(root).write(changed)
            with self.assertRaises(ValueError):
                self.logical.display_check(copy.deepcopy(self.inventory), [paths[0], changed])

    def test_external_exchange_labels_clear_ports_actors_and_routes(self):
        roots = [ET.parse(FIG / 'logical-architecture-panel-02.svg').getroot(),
                 self.logical.boundary_page(copy.deepcopy(self.inventory), self.metrics).root]
        for root in roots:
            self.assertTrue(self.logical.exchange_label_check(root, self.metrics)
                            ['boundary_exchange_label_clearance_checked'])
        for defect in ('port', 'font', 'route'):
            with self.subTest(defect=defect):
                root = copy.deepcopy(roots[0])
                label = root.find('./{*}g[@id="X01.1"]/{*}text')
                if defect == 'port':
                    label.attrib['x'] = '0'
                elif defect == 'font':
                    label.attrib['font-size'] = '9'
                else:
                    label.attrib['y'] = '140'
                with self.assertRaises(ValueError):
                    self.logical.exchange_label_check(root, self.metrics)

    def test_neighboring_information_patterns_and_dashed_control(self):
        for a, b in [('E01', 'E02'), ('E03', 'E04'), ('X01.1', 'X01.2'),
                     ('X02.1', 'X02.2'), ('X03.1', 'X03.4'), ('X06.1', 'X06.2')]:
            self.assertNotEqual(self.logical.information_style(a), self.logical.information_style(b))
        root = ET.parse(FIG / 'logical-architecture.svg').getroot()
        controls = root.findall('.//{*}g[@data-kind="control"]/{*}path')
        self.assertEqual(len(controls), 2)
        self.assertTrue(all(p.attrib['stroke-dasharray'] == LINE_PATTERNS['dashed'] for p in controls))

    def test_generic_simulation_identity_and_authority_limits(self):
        for name in ('requirements.tex', 'logical.tex'):
            self.assertNotRegex((FIG.parent / name).read_text(), r'(?i)CUBICS|NVIDIA|Omniverse')
        for name in DIAGRAMS[:-1]:
            root = ET.parse(FIG / (name+'.svg')).getroot()
            self.assertNotRegex(' '.join(root.itertext()), r'(?i)NVIDIA|Omniverse')
        logical = (FIG.parent / 'logical.tex').read_text()
        for wording in ('L01 estimates model parameters from quality-checked supplied data.',
                        'L03 executes electrical, energy and electrothermal analyses, MIL scenarios and RAM assessments.',
                        'Engineers authorize baseline decisions.',
                        'Record retention confers no engineering approval.'):
            self.assertIn(wording, logical)

    def test_normative_requirements_leave_concrete_realizations_open(self):
        text = (FIG.parent / 'requirements.tex').read_text()
        statements = dict(re.findall(r'^(FR-\d\d) & ([^\n]+)', text, re.M))
        self.assertEqual(set(statements), set(self.inventory['requirements']))
        forbidden = re.compile(
            r'\b(?:SPM|DFN|PINN|FMEA|FMECA|RBD|RMSE|Markov|Bayesian)\b|'
            r'Monte Carlo|single[- ]diode|physics[- ]informed|averaged|switching|'
            r'equivalent circuit|empirical battery models|lumped thermal|Gaussian|'
            r'two[- ]step|least squares|genetic|hill[- ]climber|hill climber|'
            r'thresholded residuals|conflict sets|minimal hitting sets|minimal cut sets|'
            r'event trees|fault trees|reliability block diagrams|sensitivity sweeps', re.I)
        for statement in statements.values():
            self.assertIsNone(forbidden.search(statement))
        for capability in ('mission energy balance and survival autonomy',
                           'photovoltaic I--V/P--V characteristics',
                           'converter/regulator responses', 'conversion/distribution losses',
                           'battery voltage and state of charge', 'electrothermal behavior',
                           'stress on protection components', 'dissipation, energy shortages'):
            self.assertIn(capability, statements['FR-16'])
        self.assertIn('execute and assess MIL scenarios', statements['FR-19'])
        self.assertIn('mission reliability against declared criteria', statements['FR-27'])

    def test_context_matches_the_four_report_interfaces(self):
        expected = set(re.findall(r'\\item\[(IF-\d\d):', (FIG.parent / 'requirements.tex').read_text()))
        self.assertEqual({e['id'] for e in self.context.INTERFACES}, expected)
        self.assertEqual({i['id'] for i in self.inventory['interfaces']}, expected)
        figure, inventory = self.context.create_figure()
        self.context.context_check(figure, inventory)
        frame = figure.root.find('./{*}g[@data-system="Framework"]')
        self.assertFalse(frame.findall('.//{*}g[@data-component]'))
        self.assertEqual(len(frame.findall('.//{*}rect')), 5)
        figure.rect(320, 140, 70, 70, parent=frame)
        with self.assertRaises(ValueError):
            self.context.context_check(figure, inventory)

    def test_context_rejects_duplicate_ports_and_label_overlap(self):
        figure, inventory = self.context.create_figure()
        frame = figure.root.find('./{*}g[@data-system="Framework"]')
        frame.append(copy.deepcopy(frame.find('./{*}rect[@data-port]')))
        with self.assertRaises(ValueError):
            self.context.context_check(figure, inventory)
        figure, inventory = self.context.create_figure()
        exchange = figure.root.find('./{*}g[@data-exchange-interface="IF-03"][@data-direction="out"]')
        entry = next(e for e in self.context.INTERFACES if e['id'] == 'IF-03')
        exchange.findall('./{*}text')[-1].attrib['y'] = str(entry['out_y'])
        with self.assertRaisesRegex(ValueError, 'label overlaps its route'):
            self.context.context_check(figure, inventory)

    def test_technical_process_topology_and_feedback(self):
        figure = self.processes.create_figure()
        flows = figure.root.findall('./{*}g[@data-source]')
        self.assertEqual(len(flows), 7)
        for flow, (origin, target, _, style, _, _) in zip(flows, self.processes.FLOWS):
            self.assertEqual((flow.attrib['data-source'], flow.attrib['data-target']), (origin, target))
            path = flow.find('./{*}path')
            points = self.logical.path_points(path.attrib['d'])
            self.assertTrue(self.logical.on_edge(points[0], self.processes.NODES[origin][0]))
            self.assertTrue(self.logical.on_edge(points[-1], self.processes.NODES[target][0]))
            self.assertEqual(path.attrib.get('stroke-dasharray'), LINE_PATTERNS[style])

    def test_rendered_artifacts_match_provenance(self):
        for name in ('framework-context', 'logical-architecture', 'systems-engineering-technical-processes'):
            provenance = json.loads((FIG / (name+'.provenance.json')).read_text())
            self.assertEqual(provenance['style_sha256'], sha(FIG / 'diagram_style.py'))
            self.assertEqual(provenance['generator_sha256'], sha(FIG / (name+'.py')))
            for kind, digest in provenance['artifact_sha256'].items():
                self.assertEqual(digest, sha(FIG / (name+'.'+kind)))


if __name__ == '__main__':
    unittest.main()
