"""Checks for the diagrams included in the compiled report.

python3 -m unittest discover -s final_report/fig -p 'test_*.py'
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from diagram_style import (FONT_STACK, LINE_PATTERNS, SerifMetrics, sha,
                           validate_arrowheads, validate_port_labels, validate_style)

FIG = Path(__file__).resolve().parent


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
        cls.logical.METRICS = SerifMetrics()

    def test_every_published_diagram_uses_shared_style(self):
        for name in ('framework-context', 'logical-architecture',
                     'logical-architecture-panel-02', 'logical-architecture-panel-03',
                     'systems-engineering-technical-processes'):
            with self.subTest(name=name):
                validate_style(ET.parse(FIG / (name+'.svg')).getroot())

    def test_arrowheads_are_large_and_above_occluding_elements(self):
        for name in ('framework-context', 'logical-architecture',
                     'logical-architecture-panel-02', 'logical-architecture-panel-03',
                     'systems-engineering-technical-processes'):
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                validate_arrowheads(root)
                ET.SubElement(root, '{http://www.w3.org/2000/svg}rect', {'fill': 'white'})
                with self.assertRaises(ValueError):
                    validate_arrowheads(root)

    def test_terminal_heads_are_painted_once_and_skip_intermediate_ports(self):
        root = ET.parse(FIG / 'logical-architecture-panel-02.svg').getroot()
        validate_arrowheads(root)
        layer = root.find('./{*}g[@data-layer="arrowheads"]')
        self.assertEqual(len(layer), 13)
        self.assertEqual(root.findall('.//{*}path[@marker-end]'), list(layer))
        for arrow in root.findall('.//{*}path[@data-terminal-head="false"]'):
            self.assertNotIn(arrow.attrib['id'], {head.attrib['data-arrow-source'] for head in layer})
        for flow_id in ('X01.1', 'X02.1'):
            self.assertEqual(root.find(f'.//{{*}}path[@id="arrow-{flow_id}"]').attrib['data-terminal-head'], 'false')
        for group in root.findall('.//{*}g[@data-routes]'):
            if group.attrib['data-flow-parent'] in ('X01.2', 'X02.2'):
                self.assertEqual(group.find('./{*}path[@id]').attrib['data-terminal-head'], 'false')
        shaft = root.find('.//{*}path[@data-terminal-head="true"]')
        shaft.attrib['marker-end'] = shaft.attrib['data-end-marker']
        with self.assertRaises(ValueError):
            validate_arrowheads(root)

    def test_interface_labels_are_on_the_port_rectangles(self):
        for name in ('framework-context', 'logical-architecture-panel-02', 'logical-architecture-panel-03'):
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                validate_port_labels(root)
                root.find('.//{*}text[@data-port-label]').attrib['x'] = '0'
                with self.assertRaises(ValueError):
                    validate_port_labels(root)

    def test_each_interface_has_one_tall_port_rectangle(self):
        for name, count in [('framework-context', 5), ('logical-architecture-panel-02', 3),
                            ('logical-architecture-panel-03', 2)]:
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                ports = root.findall('.//{*}rect[@data-port]')
                self.assertEqual(len(ports), count)
                self.assertEqual(len({port.attrib['data-interface'] for port in ports}), count)
                for port in ports:
                    self.assertGreater(float(port.attrib['height']), float(port.attrib['width']))
                    self.assertGreater(len(port.attrib['data-features'].split(',')), 1)
                    self.assertEqual(port.attrib['data-owner'], 'Framework')

    def test_port_labels_and_bottom_notes_are_absent(self):
        for name in ('framework-context', 'logical-architecture',
                     'logical-architecture-panel-02', 'logical-architecture-panel-03'):
            with self.subTest(name=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                frame = root.find('.//{*}rect[@data-enclosure="Framework"]')
                bottom = float(frame.attrib['y'])+float(frame.attrib['height'])
                for text in root.findall('.//{*}text'):
                    self.assertLessEqual(float(text.attrib['y']), bottom)
                    self.assertIsNone(re.search(r'\bp\d+\b', text.text or ''))
                visible = ' '.join(text.text or '' for text in root.findall('.//{*}text'))
                self.assertNotIn('Line patterns distinguish adjacent exchanges.', visible)
                self.assertNotIn('software in the loop', visible)

    def test_context_rejects_separate_squares_for_the_same_port(self):
        figure, inv = self.context.create_figure()
        frame = figure.root.find('./{*}g[@data-system="Framework"]')
        port = frame.find('./{*}rect[@data-port]')
        extra = copy.deepcopy(port)
        extra.attrib['height'] = extra.attrib['width']
        frame.append(extra)
        with self.assertRaises(ValueError):
            self.context.context_check(figure, inv)

    def test_style_rejects_color_sans_serif_and_rounded_blocks(self):
        for attrs in ({'fill': '#123456'}, {'font-family': 'Arial'}, {'rx': '5'}):
            with self.subTest(attrs=attrs):
                tag = 'text' if 'font-family' in attrs else 'rect'
                root = ET.Element('{http://www.w3.org/2000/svg}svg')
                ET.SubElement(root, '{http://www.w3.org/2000/svg}'+tag, attrs)
                with self.assertRaises(ValueError):
                    validate_style(root)
        self.assertIn('serif', FONT_STACK)

    def test_scoped_views_preserve_generic_scenario_identity(self):
        for name in ('requirements.tex', 'logical.tex'):
            with self.subTest(source=name):
                self.assertNotRegex((FIG.parent / name).read_text(), r'(?i)CUBICS')
        actor_text = 'NVIDIA Omniverse spacecraft and subsystem simulations'
        for name in ('framework-context', 'logical-architecture',
                     'logical-architecture-panel-02', 'logical-architecture-panel-03'):
            with self.subTest(figure=name):
                root = ET.parse(FIG / (name+'.svg')).getroot()
                self.assertNotRegex(' '.join(root.itertext()), r'(?i)whole[- ]CUBICS')
                for actor in root.findall('./{*}g[@data-actor="tools"]'):
                    self.assertEqual(' '.join(t.text or '' for t in actor.findall('./{*}text')),
                                     actor_text)
        self.assertEqual(self.logical.ACTORS['tools'], actor_text)
        simulation = next(i for i in self.inventory['interfaces'] if i['id'] == 'IF-03')
        self.assertEqual(simulation['actor_label'], actor_text)
        for alias in self.inventory['external_aliases']:
            self.assertNotRegex(alias['label'], r'(?i)CUBICS')

    def test_normative_requirements_leave_concrete_realizations_open(self):
        requirements = (FIG.parent / 'requirements.tex').read_text()
        statements = dict(re.findall(r'^(FR-\d\d) & (.*?) & MR-', requirements, re.M))
        expected = {f'FR-{n:02}' for n in range(1, 49) if n not in (12, 40)}
        self.assertEqual(set(statements), expected)
        forbidden = re.compile(
            r'\b(?:SPM|DFN|PINN|FMEA|FMECA|RBD|RMSE|Markov|Bayesian)\b|'
            r'Monte Carlo|single[- ]diode|physics[- ]informed|averaged|switching|'
            r'equivalent circuit|empirical battery models|lumped thermal|Gaussian|'
            r'two[- ]step|least squares|genetic|hill[- ]climber|hill climber|'
            r'thresholded residuals|conflict sets|minimal hitting sets|minimal cut sets|'
            r'event trees|fault trees|reliability block diagrams|sensitivity sweeps|'
            r'sum the probabilities of service', re.I)
        for identifier, statement in statements.items():
            with self.subTest(requirement=identifier):
                self.assertIsNone(forbidden.search(statement))
        for capability in ('mission energy balance and survival autonomy',
                           'photovoltaic I--V/P--V characteristics',
                           'converter/regulator responses', 'conversion/distribution losses',
                           'battery voltage and state of charge', 'electrothermal behavior',
                           'SOH prediction with uncertainty indicators', 'conducted emissions',
                           'stress on protection components', 'histories, dissipation, energy shortages'):
            self.assertIn(capability, statements['FR-16'])
        self.assertIn('alternative fault hypotheses, assessment evidence', statements['FR-19'])
        self.assertIn('generate and execute', statements['FR-27'])
        self.assertIn('minimal failure combinations', statements['FR-27'])
        self.assertIn('time-dependent modeled service availability', statements['FR-27'])
        self.assertIn('Missing failure or recovery data shall leave affected quantitative results unavailable.',
                      statements['FR-27'])

    def test_logical_health_ram_and_calibration_remain_candidate_realizations(self):
        logical = (FIG.parent / 'logical.tex').read_text()
        self.assertIn('mass, occupied volume and stack-height estimates', logical)
        for wording in ('L03 executes electrical, energy and electrothermal analyses',
                        'estimates and predicts battery SOH',
                        'L04 checks input quality, proposes calibration and independently assesses credibility',
                        'Physics-informed neural networks are one hybrid candidate.',
                        'Calibration candidates include', 'Diagnostic candidates include',
                        'RAM representation alternatives include', 'Computational alternatives include',
                        'Physical architecture synthesis compares these realization choices'):
            self.assertIn(wording, logical)

    def test_eps_ram_execution_and_assessment_stay_inside_framework(self):
        simulation = next(entry for entry in self.context.INTERFACES if entry['id'] == 'IF-03')
        self.assertEqual(' '.join(simulation['actor_labels']),
                         'NVIDIA Omniverse spacecraft and subsystem simulations')
        self.assertNotIn('model tools', simulation['actor_labels'])
        self.assertIn('Feasibility findings', simulation['in_labels'])
        self.assertIn('feasibility findings', simulation['out_labels'])
        root = ET.parse(FIG / 'logical-architecture-panel-03.svg').getroot()
        labels = {text.text for text in root.findall('.//{*}text')}
        for annotation in ('Execute EPS and RAM', 'Assess engineering criteria',
                           'Coordinate and retain runs'):
            self.assertNotIn(annotation, labels)
        logical = (FIG.parent / 'logical.tex').read_text()
        captions = ' '.join(re.findall(r'\\caption(?:\[[^\]]*\])?\{([^{}]*)\}', logical))
        for wording in ('L03 executes EPS/RAM analyses and assesses engineering criteria.',
                        'L04 assesses model credibility.',
                        'Omniverse supplies external spacecraft and subsystem simulations.',
                        'F Prime supplies host execution.',
                        'The framework manages coupling and SIL assessment.',
                        'No direct host-to-Omniverse connection is implied.'):
            self.assertIn(wording, captions)
        self.assertIn('L03 executes electrical, energy and electrothermal analyses', logical)
        self.assertIn('diagnoses faults and assesses RAM and engineering limits.', logical)
        self.assertEqual(self.logical.EXTERNAL_LABELS['X04.5'], 'Raw host SIL responses & limits')

    def test_host_exchange_labels_clear_port_and_actor(self):
        published = ET.parse(FIG / 'logical-architecture-panel-03.svg').getroot()
        generated = self.logical.tool_page(copy.deepcopy(self.inventory)).root
        for root in (published, generated):
            checks = self.logical.tool_label_clearance_check(root)
            self.assertTrue(checks['host_exchange_labels_clear_port_and_actor_checked'])
            port = root.find('.//{*}rect[@data-interface="IF-04"][@data-port]')
            actor = root.find('./{*}g[@data-actor="software"]/{*}rect')
            port_right = float(port.attrib['x'])+float(port.attrib['width'])+float(port.attrib['stroke-width'])/2
            actor_left = float(actor.attrib['x'])-float(actor.attrib['stroke-width'])/2
            labels = root.findall('./{*}g[@data-interface="IF-04"]/{*}text')
            self.assertGreaterEqual(len(labels), 10)
            for text in labels:
                self.assertEqual(float(text.attrib['font-size']), self.logical.FONT)
                self.assertEqual(text.attrib['text-anchor'], 'start')
                width = self.logical.METRICS.measure(text.text, self.logical.FONT)
                self.assertGreaterEqual(float(text.attrib['x'])-port_right, 6-1e-6)
                self.assertGreaterEqual(actor_left-float(text.attrib['x'])-width, 6-1e-6)

    def test_host_label_check_rejects_insufficient_clearance_and_small_fonts(self):
        original = ET.parse(FIG / 'logical-architecture-panel-03.svg').getroot()
        for defect in ('port', 'actor', 'font'):
            with self.subTest(defect=defect):
                root = copy.deepcopy(original)
                label = root.find('./{*}g[@id="X04.2"]/{*}text')
                if defect == 'port':
                    port = root.find('.//{*}rect[@data-interface="IF-04"][@data-port]')
                    label.attrib['x'] = str(float(port.attrib['x'])+float(port.attrib['width'])+5.9)
                    message = 'does not clear IF-04 port'
                elif defect == 'actor':
                    actor = root.find('./{*}g[@data-actor="software"]/{*}rect')
                    width = self.logical.METRICS.measure(label.text, self.logical.FONT)
                    label.attrib['x'] = str(float(actor.attrib['x'])-width-5.9)
                    message = 'does not clear F Prime actor'
                else:
                    label.attrib['font-size'] = str(self.logical.FONT-1)
                    message = 'Unreadable host exchange label'
                with self.assertRaisesRegex(ValueError, message):
                    self.logical.tool_label_clearance_check(root)

    def test_context_rejects_label_route_overlap(self):
        figure, inv = self.context.create_figure()
        checks = self.context.context_check(figure, inv)
        self.assertTrue(checks['exchange_labels_clear_their_routes'])
        exchange = figure.root.find('./{*}g[@data-exchange-interface="IF-03"][@data-direction="out"]')
        entry = next(entry for entry in self.context.INTERFACES if entry['id'] == 'IF-03')
        exchange.findall('./{*}text')[-1].attrib['y'] = str(entry['out_y'])
        with self.assertRaisesRegex(ValueError, 'label overlaps its route'):
            self.context.context_check(figure, inv)

    def test_retained_logical_contract_coverage(self):
        self.logical.retained_inventory_check(self.inventory)
        incomplete = copy.deepcopy(self.inventory)
        incomplete['peer_exchanges'].pop()
        with self.assertRaises(ValueError):
            self.logical.retained_inventory_check(incomplete)

    def test_logical_names_enclosures_ports_and_directed_endpoints(self):
        paths = [FIG / (name+'.svg') for name in ('logical-architecture',
                 'logical-architecture-panel-02', 'logical-architecture-panel-03')]
        checks = self.logical.display_check(copy.deepcopy(self.inventory), paths)
        self.assertTrue(all(checks.values()))

    def test_neighboring_information_routes_have_distinct_patterns(self):
        for a, b in [('E01', 'E02'), ('E03', 'E04'), ('E06', 'E09'),
                     ('X01.1', 'X01.2'), ('X02.1', 'X02.2'), ('X06.1', 'X06.2')]:
            with self.subTest(routes=(a, b)):
                self.assertNotEqual(self.logical.information_style(a), self.logical.information_style(b))
        for prefix, count in [('X03', 6), ('X04', 5)]:
            styles = [self.logical.information_style(f'{prefix}.{n}') for n in range(1, count+1)]
            self.assertTrue(all(a != b for a, b in zip(styles, styles[1:])))
            self.assertNotIn('dashed', styles)
        control = ET.parse(FIG / 'logical-architecture.svg').getroot().findall(
            './/{*}g[@data-kind="control"]/{*}path[@data-terminal-head="true"]')
        self.assertEqual(len(control), 5)
        self.assertTrue(all(p.attrib['stroke-dasharray'] == LINE_PATTERNS['dashed'] for p in control))

    def test_black_box_has_boundary_ports_and_no_internal_interface_blocks(self):
        figure, inv = self.context.create_figure()
        self.context.context_check(figure, inv)
        frame = figure.root.find('./{*}g[@data-system="Framework"]')
        self.assertFalse(frame.findall('.//{*}g[@data-interface]'))
        self.assertEqual(len(frame.findall('.//{*}rect')), 6)
        figure.rect(320, 140, 70, 70, parent=frame)
        with self.assertRaises(ValueError):
            self.context.context_check(figure, inv)

    def test_context_rejects_reversed_exchange(self):
        figure, inv = self.context.create_figure()
        arrow = figure.root.find('./{*}g[@data-exchange-interface="IF-01"]/{*}path')
        start, end = self.logical.path_points(arrow.attrib['d'])
        arrow.attrib['d'] = f'M{end[0]:g} {end[1]:g} H{start[0]:g}'
        with self.assertRaises(ValueError):
            self.context.context_check(figure, inv)

    def test_technical_process_topology_and_feedback(self):
        figure = self.processes.create_figure()
        validate_style(figure.root)
        flows = figure.root.findall('./{*}g[@data-source]')
        self.assertEqual(len(flows), 7)
        for flow, (origin, target, _, style, _, _) in zip(flows, self.processes.FLOWS):
            self.assertEqual((flow.attrib['data-source'], flow.attrib['data-target']), (origin, target))
            arrow = flow.find('./{*}path')
            points = self.logical.path_points(arrow.attrib['d'])
            self.assertTrue(self.logical.on_edge(points[0], self.processes.NODES[origin][0]))
            self.assertTrue(self.logical.on_edge(points[-1], self.processes.NODES[target][0]))
            self.assertEqual(arrow.attrib.get('stroke-dasharray'), LINE_PATTERNS[style])
        self.assertNotEqual(flows[-1].attrib['data-line-style'], flows[-2].attrib['data-line-style'])

    def test_rendered_artifacts_match_provenance(self):
        for name in ('framework-context', 'logical-architecture', 'systems-engineering-technical-processes'):
            with self.subTest(name=name):
                provenance = json.loads((FIG / (name+'.provenance.json')).read_text())
                self.assertEqual(provenance['style_sha256'], sha(FIG / 'diagram_style.py'))
                self.assertEqual(provenance['generator_sha256'], sha(FIG / (name+'.py')))
                for kind, digest in provenance['artifact_sha256'].items():
                    self.assertEqual(digest, sha(FIG / (name+'.'+kind)))


if __name__ == '__main__':
    unittest.main()
