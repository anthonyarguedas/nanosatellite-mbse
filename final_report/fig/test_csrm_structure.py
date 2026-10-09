"""Source fidelity and presentation checks for the authored CSRM figures.

python3 -m unittest discover -s final_report/fig -p 'test_csrm_structure.py'
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from diagram_style import LIGHT, SerifMetrics, validate_arrowheads, validate_style

FIG = Path(__file__).resolve().parent


class CSRMStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('csrm_structure', FIG / 'csrm-structure.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        metrics = SerifMetrics()
        cls.figures = [cls.module.mission_view(metrics), cls.module.subsystem_view(metrics),
                       cls.module.eps_view(metrics)]

    def test_selected_structure_matches_translation(self):
        native = self.module.inventory()
        self.assertEqual(len(native['CubeSat']), 9)
        self.assertEqual(len(native['Power Subsystem']), 6)
        self.assertEqual(native['orbit_reference'], ('Orbit', 'CubeSat Orbit', '1..1'))
        checks = self.module.check_coverage(self.figures, native)
        self.assertEqual(checks['selected_native_parts_checked'], 25)

    def test_multiplicity_changes_are_detected(self):
        original = self.module.MODEL.read_text()
        changed = original.replace("part 'cubeSat Orbit' : 'CubeSat Orbit' [1..*]",
                                   "part 'cubeSat Orbit' : 'CubeSat Orbit' [1..1]", 1)
        self.assertNotEqual(original, changed)
        with self.assertRaisesRegex(ValueError, 'Changed native structure: Space Segment'):
            self.module.inventory(changed)

    def test_missing_or_renamed_eps_component_is_detected(self):
        original = self.module.MODEL.read_text()
        changed = original.replace("part 'batteries' :", "part 'battery Bank' :", 1)
        self.assertNotEqual(original, changed)
        with self.assertRaisesRegex(ValueError, 'Changed native structure: Power Subsystem'):
            self.module.inventory(changed)

    def test_reference_is_distinct_from_composite_part(self):
        root = self.figures[0].root
        reference = root.find('.//{*}text[@data-reference="Orbit"]')
        self.assertEqual(reference.text, 'ref Orbit : CubeSat Orbit [1]')
        self.assertEqual(len(root.findall('.//{*}g[@data-owner="Space Segment"]')), 2)
        cube_sat = root.find('.//{*}g[@data-type="CubeSat"]')
        self.assertIsNotNone(cube_sat.find('./{*}text[@data-reference="Orbit"]'))

    def test_domain_mission_and_space_composition_are_nested(self):
        root = self.figures[0].root
        domain = root.find('.//{*}g[@data-definition="CubeSat Domain"]')
        mission = domain.find('./{*}g[@data-type="CubeSat Mission"]')
        space = mission.find('./{*}g[@data-type="Space Segment"]')
        self.assertIsNotNone(space.find('./{*}g[@data-type="CubeSat"]'))
        self.assertIsNotNone(space.find('./{*}g[@data-type="CubeSat Orbit"]'))
        self.assertIsNotNone(mission.find('./{*}g[@data-type="Ground Segment"]'))

    def test_only_context_and_external_services_are_gray(self):
        for figure in self.figures:
            for group in figure.root.findall('.//{*}g[@data-external]'):
                rectangle = group.find('./{*}rect')
                expected = LIGHT if group.attrib['data-external'] == 'true' else 'white'
                self.assertEqual(rectangle.attrib['fill'], expected)
        external = self.figures[0].root.findall('.//{*}g[@data-external="true"]')
        self.assertEqual({group.attrib['data-type'] for group in external},
                         {'External Environment', 'External Constraints', 'Ground Station Services',
                          'Transport, Launch, and Deploy Services', 'GNSS'})

    def test_published_figures_use_shared_style_and_no_exchange_arrows(self):
        for name in ('csrm-mission-structure', 'csrm-cubesat-subsystems', 'csrm-eps-components'):
            with self.subTest(name=name):
                root = ET.parse(FIG / (name + '.svg')).getroot()
                validate_style(root)
                validate_arrowheads(root)
                self.assertEqual(root.findall('.//{*}path[@marker-end]'), [])
                self.assertEqual(root.findall('.//{*}rect[@data-port]'), [])
                self.assertEqual(root.findall('.//{*}g[@data-layer="arrowheads"]/{*}path'), [])

    def test_section_has_four_figures_and_18_distinct_core_citations(self):
        import re
        section = (FIG.parent / 'generic-cubesat-structure.tex').read_text()
        count_citation = re.search(r'18 papers.*?\\citep\{([^}]+)\}', section)
        keys = count_citation[1].split(',')
        self.assertEqual(len(keys), 18)
        self.assertEqual(len(set(keys)), 18)
        self.assertEqual(section.count('\\begin{figure}'), 4)
        self.assertNotIn('\\section{', '\n'.join(line for line in section.splitlines()
                                                if not line.startswith('%')))
        bibliography = (FIG.parent / 'literatura.bib').read_text()
        bib_keys = re.findall(r'@\w+\{([^,]+),', bibliography)
        self.assertEqual(len(bib_keys), len(set(bib_keys)))
        for citation in re.findall(r'\\citep(?:\[[^]]*\])?\{([^}]+)\}', section):
            for key in citation.split(','):
                self.assertIn(key, bib_keys)


if __name__ == '__main__':
    unittest.main()
