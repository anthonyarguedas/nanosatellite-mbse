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
