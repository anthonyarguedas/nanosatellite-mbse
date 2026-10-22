"""Definition-library, presentation and published-artifact regression checks.

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s final_report/fig \
    -p 'test_eps_component_models.py' -v

These checks validate authored declarations and rendering, not SysML compilation.
All temporary PDF text/bounding-box artifacts are kept outside the repository.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

from diagram_style import (FONT_STACK, LIGHT, SerifMetrics, run, sha,
                           validate_arrowheads, validate_style)

FIG = Path(__file__).resolve().parent
EXPECTED_NAMES = [
    'Solar Arrays', 'Batteries', 'Regulators and Converters',
    'Power Circuits and Switches', 'Processor and Memory', 'Software', 'Load',
]
# Independent expected endpoint roles and multiplicities: these are declarations,
# not links, allocations, exchange directions or a selected wiring arrangement.
EXPECTED_PORTS = {
    'Solar Arrays': [('dc output', 'IF-E', '1..*'), ('thermal', 'IF-T', '0..*'),
                     ('monitor', 'IF-D', '0..*')],
    'Batteries': [('bidir. dc', 'IF-E', '1..*'), ('thermal', 'IF-T', '0..*'),
                  ('monitor', 'IF-D', '0..*')],
    'Regulators and Converters': [('input dc', 'IF-E', '1..*'), ('output dc', 'IF-E', '1..*'),
                                  ('thermal', 'IF-T', '0..*'), ('service', 'IF-D', '0..*'),
                                  ('enable', 'IF-C', '0..*')],
    'Power Circuits and Switches': [('input dc', 'IF-E', '1..*'), ('output dc', 'IF-E', '1..*'),
                                    ('thermal', 'IF-T', '0..*'), ('service', 'IF-D', '0..*'),
                                    ('control/inhibit', 'IF-C', '0..*')],
    'Processor and Memory': [('supply dc', 'IF-E', '1..*'), ('thermal', 'IF-T', '0..*'),
                             ('data service', 'IF-D', '0..*'), ('discrete I/O', 'IF-C', '0..*')],
    'Software': [('logical service', 'IF-D', '1..*')],
    'Load': [('supply dc', 'IF-E', '1..*'), ('thermal', 'IF-T', '0..*'),
             ('data service', 'IF-D', '0..*'), ('enable', 'IF-C', '0..*')],
}


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, FIG / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EPSComponentModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module('eps_component_models', 'eps-component-models.py')
        cls.figure = cls.module.create_figure(SerifMetrics())
        cls.published = ET.parse(FIG / 'eps-component-models.svg').getroot()
        cls.provenance = json.loads((FIG / 'eps-component-models.provenance.json').read_text())

    def test_exact_six_csrm_categories_plus_external_load(self):
        structure = load_module('csrm_structure', 'csrm-structure.py')
        native_names = {row[1] for row in structure.EXPECTED['Power Subsystem']}
        self.assertEqual(set(EXPECTED_NAMES[:-1]), native_names)
        for root in (self.figure.root, self.published):
            groups = root.findall('.//{*}g[@data-definition]')
            self.assertEqual([g.attrib['data-definition'] for g in groups], EXPECTED_NAMES)
            self.assertEqual([g.attrib['data-definition'] for g in groups
                              if g.attrib['data-external'] == 'true'], ['Load'])
            for group in groups:
                self.assertEqual([n.text for n in group.findall('./{*}text[@data-stereotype]')],
                                 ['«part def»'])
                self.assertEqual(group.find('./{*}text[@data-definition-name]').text,
                                 group.attrib['data-definition'])

    def test_boundary_ports_have_exact_type_role_and_multiplicity(self):
        root = self.published
        for name, expected in EXPECTED_PORTS.items():
            with self.subTest(name=name):
                group = root.find(f'.//{{*}}g[@data-definition="{name}"]')
                ports = group.findall('./{*}rect[@data-type-port]')
                actual = [(p.attrib['data-role'], p.attrib['data-type-id'],
                           p.attrib['data-multiplicity']) for p in ports]
                self.assertEqual(actual, expected)
                for port in ports:
                    key = port.attrib['data-type-port']
                    labels = group.findall(f'./{{*}}text[@data-type-port-label="{key}"]')
                    roles = group.findall(f'./{{*}}text[@data-type-port-role="{key}"]')
                    self.assertEqual(len(labels), 1)
                    self.assertEqual(len(roles), 1)
                    self.assertEqual(labels[0].text, port.attrib['data-type-id'])
                    self.assertEqual(roles[0].text,
                                     f'{port.attrib["data-role"]} [{port.attrib["data-multiplicity"]}]')
                    l, t, r, b = self.module.text_bounds(labels[0], self.figure.metrics)
                    x, y, w, h = [float(port.attrib[a]) for a in ('x', 'y', 'width', 'height')]
                    self.assertLessEqual(x, l)
                    self.assertLessEqual(r, x+w)
                    self.assertLessEqual(y, t)
                    self.assertLessEqual(b, y+h)
        visible_ids = [n for n in root.findall('.//{*}text')
                       if re.fullmatch(r'IF-[A-Z0-9]+', n.text or '')]
        self.assertEqual(len(visible_ids), 25)
        self.assertTrue(all('data-type-port-label' in n.attrib for n in visible_ids))
        self.assertEqual({n.text for n in visible_ids}, {'IF-E', 'IF-T', 'IF-D', 'IF-C'})

    def test_shared_records_are_records_not_a_seventh_csrm_component(self):
        banner = self.published.find('.//{*}g[@data-shared-records]')
        self.assertEqual([g.attrib['data-record'] for g in banner.findall('./{*}g[@data-record]')],
                         ['catalog_identity', 'sourced_values', 'hardware_data'])
        self.assertEqual(banner.findall('.//{*}text[@data-stereotype]'), [])
        for group in self.published.findall('.//{*}g[@data-definition]'):
            refs = group.attrib['data-record-refs'].split(',')
            expected = ['catalog_identity', 'sourced_values']
            if group.attrib['data-definition'] != 'Software':
                expected.append('hardware_data')
            self.assertEqual(refs, expected)
        text = ' '.join(n.text or '' for n in banner.findall('.//{*}text'))
        for term in ('manufacturer', 'part/revision', 'roles', 'value/unit',
                     'conditions', 'source', 'status', 'mass/envelope',
                     'pins', 'environment'):
            self.assertIn(term, text)

    def test_software_is_host_reference_and_logical_service_only(self):
        software = self.published.find('.//{*}g[@data-definition="Software"]')
        reference = software.find('./{*}text[@data-reference="host"]')
        self.assertEqual(reference.text, 'ref host : Processor and Memory [1..*]')
        self.assertEqual(reference.attrib['data-reference-target'], 'Processor and Memory')
        self.assertEqual(reference.attrib['data-reference-multiplicity'], '1..*')
        self.assertEqual([p.attrib['data-type-id'] for p in
                          software.findall('./{*}rect[@data-type-port]')], ['IF-D'])
        self.assertEqual(software.find('./{*}text[@data-hardware-exclusion]').text,
                         'no independent hardware mass/power')
        self.assertNotIn('hardware_data', software.attrib['data-record-refs'])
        self.assertEqual(software.findall('.//{*}g[@data-definition]'), [])
        regulator = self.published.find('.//{*}g[@data-definition="Regulators and Converters"]')
        self.assertEqual(regulator.find('./{*}text[@data-property-group="bidirectional"]').text,
                         'bidirectional capability (declared)')

    def test_diagram_property_groups_match_generator_and_provenance(self):
        expected = self.module.COMPONENTS + [self.module.LOAD]
        manifest = self.provenance['component_definitions']
        self.assertEqual(len(manifest), 7)
        for definition, recorded in zip(expected, manifest):
            with self.subTest(name=definition['name']):
                self.assertEqual(recorded, {**definition,
                                            'shared_records': self.module.record_ids(definition)})
                group = self.published.find(f'.//{{*}}g[@data-definition="{definition["name"]}"]')
                displayed = group.findall('./{*}text[@data-property-group]')
                self.assertEqual([(n.attrib['data-property-group'], n.text) for n in displayed],
                                 [(p['id'], p['summary']) for p in definition['properties']])
                self.assertEqual(len({p['id'] for p in definition['properties']}), len(displayed))
                self.assertTrue(all(n.attrib['data-property-owner'] == definition['name']
                                    for n in displayed))
        self.assertEqual(sum(len(c['properties']) for c in expected), 33)

    def test_readable_shared_style_and_gray_only_on_external_load(self):
        validate_style(self.published)
        validate_arrowheads(self.published)
        self.assertEqual(self.module.validate_definition_view(self.figure)['boundary_port_declarations'], 25)
        for node in self.published.findall('.//{*}text'):
            self.assertGreaterEqual(float(node.attrib['font-size']), 11)
            self.assertEqual(node.attrib['font-family'], FONT_STACK)
            self.assertNotIn('transform', node.attrib)
        for node in self.published.iter():
            if 'stroke-width' in node.attrib:
                self.assertLessEqual(float(node.attrib['stroke-width']), .8)
        gray = [r for r in self.published.findall('.//{*}rect') if r.attrib['fill'] == LIGHT]
        self.assertEqual([r.attrib.get('data-definition-body') for r in gray], ['Load'])

    def test_every_visible_label_stays_inside_declared_block_region_and_page(self):
        for node in self.published.findall('.//{*}text'):
            l, t, r, b = self.module.text_bounds(node, self.figure.metrics)
            x, y, w, h = map(float, node.attrib['data-text-region'].split(','))
            with self.subTest(label=node.text):
                self.assertLessEqual(x-.01, l)
                self.assertLessEqual(r, x+w+.01)
                self.assertLessEqual(y-.01, t)
                self.assertLessEqual(b, y+h+.01)
                self.assertTrue(0 <= l <= r <= 690 and 0 <= t <= b <= 470)

    def test_actual_pdf_word_bounds_are_inside_page_and_local_compartments(self):
        regions = [tuple(map(float, n.attrib['data-text-region'].split(',')))
                   for n in self.published.findall('.//{*}text')]
        with tempfile.TemporaryDirectory(prefix='eps-component-models-test-') as job:
            bbox = Path(job) / 'bounds.html'
            run(['pdftotext', '-bbox', str(FIG / 'eps-component-models.pdf'), str(bbox)])
            page = ET.parse(bbox).getroot().find('.//{*}page')
            self.assertEqual((float(page.attrib['width']), float(page.attrib['height'])), (690, 470))
            words = page.findall('.//{*}word')
            self.assertGreater(len(words), 200)
            for word in words:
                l, t, r, b = [float(word.attrib[a]) for a in ('xMin', 'yMin', 'xMax', 'yMax')]
                with self.subTest(word=word.text):
                    self.assertTrue(0 <= l <= r <= 690 and 0 <= t <= b <= 470)
                    self.assertTrue(any(x-.1 <= l and r <= x+w+.1 and
                                        y-.1 <= t and b <= y+h+.1 for x, y, w, h in regions),
                                    'PDF text outside its block/port compartments')

    def test_definition_view_has_no_connectors_arrows_or_selected_architecture(self):
        root = self.published
        self.assertEqual(root.findall('.//{*}path'), [])
        self.assertEqual(root.findall('.//{*}marker'), [])
        self.assertEqual(root.findall('.//*[@marker-end]'), [])
        for line in root.findall('.//{*}line'):
            self.assertEqual(line.attrib.get('data-compartment-divider'), 'true')
        self.assertIn('no selected topology', root.attrib['data-view-kind'])
        self.assertIn('only the six group names are CSRM-derived', self.provenance['basis'])
        self.assertIn('No compiled/executable SysML v2 conformance', self.provenance['limitations'])

    def test_published_artifacts_and_dimensions_match_provenance(self):
        output = self.provenance['output']
        self.assertEqual(self.published.attrib['width'], '690pt')
        self.assertEqual(self.published.attrib['height'], '470pt')
        self.assertEqual(self.published.attrib['viewBox'], '0 0 690 470')
        self.assertEqual(output['dimensions'], {'pdf_pt': [690, 470], 'png_px': [1380, 940]})
        png = (FIG / 'eps-component-models.png').read_bytes()
        self.assertEqual(struct.unpack('>II', png[16:24]), (1380, 940))
        for kind, expected in output['artifact_sha256'].items():
            self.assertEqual(sha(FIG / ('eps-component-models.'+kind)), expected)
        self.assertEqual(output['svg_sha256_used_for_pdf'], sha(FIG / 'eps-component-models.svg'))
        self.assertEqual(self.provenance['generator_sha256'], sha(FIG / 'eps-component-models.py'))
        self.assertEqual(self.provenance['shared_style_sha256'], sha(FIG / 'diagram_style.py'))

    def test_report_schema_contains_every_component_and_port_type(self):
        report = (FIG.parent / 'design-proposal.tex').read_text()
        generic = report.split(r'\section{EPS Components and Loads Generic Models}', 1)[1]
        generic = generic.split(r'\section{EPS Component Selection}', 1)[0]
        properties = generic.split(r'\caption{Specialized EPS component and load definitions.}', 1)[1]
        for name in EXPECTED_NAMES:
            self.assertIn(name+' & ', properties)
        for identifier in ('IF-E', 'IF-T', 'IF-D', 'IF-C'):
            self.assertIn(identifier+':', generic)
        for phrase in ('current', 'positive into', 'conjugated directions',
                       'supported configurations', 'accounting boundary'):
            self.assertIn(phrase, generic)

    def test_generic_definitions_and_figure_precede_selection_equations(self):
        report = (FIG.parent / 'design-proposal.tex').read_text()
        generic, selection = report.split(r'\section{EPS Components and Loads Generic Models}', 1)[1].split(
            r'\section{EPS Component Selection}', 1)
        self.assertIn('fig/eps-component-models.pdf', generic)
        self.assertNotIn(r'\begin{equation}', generic)
        self.assertNotIn(r'\begin{align}', generic)
        self.assertIn(r'\label{eq:pv-integer-configuration}', selection)
        self.assertIn(r'\label{alg:eps-cots-selection}', selection)

    def test_missing_property_group_and_changed_port_multiplicity_are_rejected(self):
        broken = copy.deepcopy(self.figure)
        label = broken.root.find('.//{*}text[@data-property-owner="Batteries"]')
        label.text = 'wrong battery property'
        with self.assertRaisesRegex(ValueError, 'Inconsistent diagram property groups'):
            self.module.validate_definition_view(broken)
        broken = copy.deepcopy(self.figure)
        broken.root.find('.//{*}rect[@data-type-port]').set('data-multiplicity', '0..*')
        with self.assertRaisesRegex(ValueError, 'Changed port declaration'):
            self.module.validate_definition_view(broken)

    def test_small_text_and_text_outside_block_are_rejected(self):
        broken = copy.deepcopy(self.figure)
        broken.root.find('.//{*}text').set('font-size', '9')
        with self.assertRaisesRegex(ValueError, 'Unreadably small label'):
            self.module.validate_definition_view(broken)
        broken = copy.deepcopy(self.figure)
        broken.root.find('.//{*}text[@data-property-owner="Batteries"]').set('x', '20')
        with self.assertRaisesRegex(ValueError, 'Text outside block'):
            self.module.validate_definition_view(broken)


if __name__ == '__main__':
    unittest.main()
