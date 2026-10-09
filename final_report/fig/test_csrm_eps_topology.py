"""Checks for the authored EPS topology association view.

python3 -m unittest discover -s final_report/fig -p 'test_csrm*.py'
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from diagram_style import orthogonal_points, validate_arrowheads, validate_style

FIG = Path(__file__).resolve().parent


class CSRMTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('csrm_eps_topology', FIG / 'csrm-eps-topology.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.figure, cls.native, _ = cls.module.create_figure()

    def test_choice_names_and_alternatives_match_supplied_figure(self):
        self.assertEqual({choice['name']: choice['alternatives'] for choice in self.module.CHOICES}, {
            'Power Conditioning': ['Direct Energy Transfer', 'MPPT'],
            'Energy Transfer': ['Centralized', 'Distributed'],
            'DC Bus Regulation': ['Unregulated', 'Partially regulated', 'Fully regulated'],
            'Power Distribution': ['DC-DC Converter', 'Bus Voltage'],
        })
        checks = self.module.check_mapping(self.figure, self.native)
        self.assertEqual(checks['variation_points_checked'], 4)
        self.assertEqual(checks['alternatives_checked'], 9)
        self.assertEqual(checks['proposed_associations_checked'], 8)

    def test_conditioning_and_bus_map_to_correct_hardware_groups(self):
        groups = {choice['name']: {component for component, _ in choice['groups']}
                  for choice in self.module.CHOICES}
        self.assertEqual(groups['Power Conditioning'], {'Regulators and Converters', 'Solar Arrays'})
        self.assertEqual(groups['DC Bus Regulation'], {'Regulators and Converters', 'Batteries'})
        self.assertEqual(groups['Energy Transfer'], {'Regulators and Converters', 'Power Circuits and Switches'})
        self.assertEqual(groups['Power Distribution'], {'Regulators and Converters', 'Power Circuits and Switches'})

    def test_every_component_name_is_native_and_repetition_keeps_identity(self):
        groups = self.figure.root.findall('.//{*}g[@data-csrm-component]')
        eps = {row[1] for row in self.native['Power Subsystem']}
        self.assertEqual(len(groups), 8)
        self.assertEqual(len({group.attrib['data-csrm-component'] for group in groups}), 4)
        for group in groups:
            self.assertIn(group.attrib['data-csrm-component'], eps)
            self.assertEqual(group.find('./{*}text').text, group.attrib['data-csrm-component'])
        self.assertEqual(sum(group.attrib['data-csrm-component'] == 'Regulators and Converters'
                             for group in groups), 4)

    def test_arrows_have_one_label_and_target_choice_header(self):
        root = self.figure.root
        arrows = root.findall('.//{*}path[@data-mapping]')
        labels = root.findall('.//{*}text[@data-mapping-label]')
        self.assertEqual({arrow.attrib['data-mapping'] for arrow in arrows},
                         {label.attrib['data-mapping-label'] for label in labels})
        self.assertEqual(len(labels), 8)
        by_id = {choice['id']: choice for choice in self.module.CHOICES}
        for arrow in arrows:
            choice = by_id[arrow.attrib['data-variation-point']]
            x, y = orthogonal_points(arrow.attrib['d'])[-1]
            self.assertEqual(x, 464)
            self.assertGreater(y, choice['y'])
            self.assertLess(y, choice['y']+28)
            self.assertEqual(arrow.attrib['data-relationship-kind'], 'proposed design association')

    def test_a_selected_option_endpoint_is_rejected(self):
        broken = copy.deepcopy(self.figure)
        arrow = broken.root.find('.//{*}path[@data-mapping="conditioning-1"]')
        arrow.attrib['d'] = 'M232 109 H434 V128 H464'
        with self.assertRaisesRegex(ValueError, 'points to an alternative'):
            self.module.check_mapping(broken, self.native)

    def test_published_diagram_uses_shared_style_and_foreground_heads(self):
        root = ET.parse(FIG / 'csrm-eps-topology.svg').getroot()
        validate_style(root)
        validate_arrowheads(root)
        self.assertEqual(len(root.findall('.//{*}g[@data-layer="arrowheads"]/{*}path')), 8)
        for arrow in root.findall('.//{*}path[@data-mapping]'):
            self.assertNotIn('marker-end', arrow.attrib)
            self.assertNotIn('stroke-dasharray', arrow.attrib)

    def test_report_distinguishes_proposed_associations_from_source_choices(self):
        section = (FIG.parent / 'generic-cubesat-structure.tex').read_text()
        self.assertIn('will be tailored to each mission by selecting a topology alternative', section)
        self.assertIn('Arrows express design associations proposed for this framework.', section)
        self.assertIn('No topology alternative is selected in this view.', section)
        self.assertIn('\\label{fig:csrm-eps-topology}', section)
        self.assertIn('\\citep[Fig.~1, Sec.~4]{handpicked-0003}', section)


if __name__ == '__main__':
    unittest.main()
