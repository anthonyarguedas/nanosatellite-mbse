"""Checks for the decomposed NASA phase and EPS activity flow panels."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from diagram_style import LINE_PATTERNS, run, sha, validate_arrowheads, validate_style

FIG = Path(__file__).resolve().parent


class EPSMissionFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            'eps_mission_flow', FIG / 'eps-mission-requirements-flow.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.panels = [cls.module.create_panel(spec) for spec in cls.module.PANELS]

    def test_six_review_panels_cover_the_correct_nasa_phases(self):
        self.assertEqual([(p.spec['mr'], p.spec['review'], p.spec['phase']) for p in self.panels], [
            ('MR-01', 'MCR', 'Pre-Phase A'),
            ('MR-02', 'SRR', 'Phase A'),
            ('MR-03', 'MDR/SDR', 'Phase A'),
            ('MR-04', 'PDR', 'Phase B'),
            ('MR-05', 'scoped CDR', 'Adapted Phase C'),
            ('MR-06', 'scoped SIR', 'Adapted Phase C'),
        ])
        checks = self.module.check_series(self.panels)
        self.assertEqual(checks['mission_requirements_checked'], 6)
        self.assertEqual(checks['cross_panel_handoffs_checked'], 5)

    def test_activity_boxes_are_short_and_all_exchanges_have_visible_labels(self):
        for panel in self.panels:
            with self.subTest(panel=panel.spec['id']):
                checks = self.module.check_panel(panel)
                self.assertEqual(checks['short_activities_checked'], 7)
                self.assertGreaterEqual(checks['visible_exchange_labels_checked'], 11)
                for node in panel.figure.root.findall('.//{*}g[@data-kind="activity"]'):
                    self.assertLessEqual(len(node.findall('./{*}text')), 2)
                for group in panel.figure.root.findall('.//{*}g[@data-flow]'):
                    self.assertTrue(group.findall('./{*}text'))

    def test_pdr_sizing_branches_merge_into_preliminary_configuration(self):
        panel = next(p for p in self.panels if p.spec['mr'] == 'MR-04')
        by_id = {flow['id']: flow for flow in panel.flows}
        self.assertEqual((by_id['left-down']['source'], by_id['left-down']['target']), ('n1', 'n3'))
        self.assertEqual((by_id['battery-design']['source'], by_id['battery-design']['target']), ('n2', 'n3'))
        self.assertEqual((by_id['cross']['source'], by_id['cross']['target']), ('n3', 'n4'))

    def test_mil_results_and_plant_are_inputs_to_sil(self):
        panel = self.panels[-1]
        cross = next(flow for flow in panel.flows if flow['id'] == 'cross')
        self.assertEqual((cross['source'], cross['target']), ('n3', 'n4'))
        self.assertIn('Execute MIL', panel.spec['activities'][3])
        self.assertIn('Execute SIL', panel.spec['activities'][4])
        self.assertIn('MIL reference responses', ' '.join(cross['labels']))
        self.assertEqual(panel.spec['outgoing'], 'integration-ready')

    def test_cdr_authorization_is_distinct_from_design_information(self):
        for panel in self.panels[-2:]:
            authorization = panel.figure.root.find('.//{*}g[@data-flow="coding-authorization"]')
            self.assertEqual(authorization.attrib['data-kind'], 'authorization')
            self.assertEqual(authorization.find('./{*}path').attrib['stroke-dasharray'], LINE_PATTERNS['dashed'])
        for panel in self.panels:
            accepted = panel.figure.root.find('.//{*}g[@data-flow="output"]')
            self.assertEqual(accepted.attrib['data-requires-acceptance'], 'true')
            findings = panel.figure.root.find('.//{*}g[@data-flow="findings"]')
            self.assertEqual(findings.find('./{*}path').attrib['stroke-dasharray'], LINE_PATTERNS['dotted'])

    def test_changed_dependency_and_missing_label_are_rejected(self):
        panel = copy.deepcopy(self.panels[0])
        panel.figure.root.find('.//{*}g[@data-flow="input"]').attrib['data-target'] = 'n4'
        with self.assertRaisesRegex(ValueError, 'dependency'):
            self.module.check_panel(panel)
        panel = copy.deepcopy(self.panels[0])
        group = panel.figure.root.find('.//{*}g[@data-flow="input"]')
        group.remove(group.find('./{*}text'))
        with self.assertRaisesRegex(ValueError, 'label'):
            self.module.check_panel(panel)

    def test_dense_activity_box_and_route_over_label_are_rejected(self):
        panel = copy.deepcopy(self.panels[0])
        activity = panel.figure.root.find('.//{*}g[@data-node="n0"]')
        activity.append(copy.deepcopy(activity.find('./{*}text')))
        with self.assertRaisesRegex(ValueError, 'Dense activity'):
            self.module.check_panel(panel)
        panel = copy.deepcopy(self.panels[0])
        panel.figure.root.find('.//{*}g[@data-flow="input"]/{*}text').attrib['x'] = '490'
        with self.assertRaisesRegex(ValueError, 'crosses an exchange label'):
            self.module.check_panel(panel)

    def test_broken_cross_panel_handoff_is_rejected(self):
        panels = copy.deepcopy(self.panels)
        panels[1].spec['incoming'] = 'unrelated-basis'
        with self.assertRaisesRegex(ValueError, 'cross-panel'):
            self.module.check_series(panels)

    def test_published_panels_have_shared_style_and_current_provenance(self):
        provenance = json.loads((FIG / 'eps-mission-requirements-flow.provenance.json').read_text())
        self.assertEqual(len(provenance['panels']), 6)
        for panel, record in zip(self.panels, provenance['panels']):
            with self.subTest(panel=panel.spec['id']):
                published = copy.deepcopy(panel)
                published.figure.root = ET.parse(FIG / (record['file']+'.svg')).getroot()
                validate_style(published.figure.root)
                validate_arrowheads(published.figure.root)
                self.module.check_panel(published)
                for extension, expected in record['artifact_sha256'].items():
                    self.assertEqual(sha(FIG / (record['file']+'.'+extension)), expected)
        self.assertEqual(sha(FIG / 'eps-mission-requirements-flow.py'), provenance['generator_sha256'])
        for relative, expected in provenance['source_sha256'].items():
            self.assertEqual(sha(FIG.parent.parent / relative), expected)

    def test_combined_pdf_has_six_pages_and_preview_is_first_panel(self):
        info = run(['pdfinfo', str(FIG / 'eps-mission-requirements-flow.pdf')])
        self.assertEqual(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1), '6')
        for extension in ('svg', 'png'):
            self.assertEqual(sha(FIG / ('eps-mission-requirements-flow.'+extension)),
                             sha(FIG / ('eps-mission-requirements-flow-pre-a.'+extension)))

    def test_report_links_all_panels_without_the_dense_overview(self):
        section = (FIG.parent / 'needs.tex').read_text()
        appendix = (FIG.parent / 'eps-mission-flows.tex').read_text()
        self.assertIn('expands MR-01--06 into six activity diagrams', section)
        self.assertIn('Dotted arrows return findings.', appendix)
        self.assertIn('Dashed arrows carry authorization.', appendix)
        self.assertNotIn('Short verb phrases name activities.', section)
        self.assertLess(appendix.index('Short verb phrases name activities.'),
                        appendix.index('\\begin{figure}'))
        self.assertNotIn('\\includegraphics', section)
        self.assertIn('\\include{eps-mission-flows}', (FIG.parent / 'main.tex').read_text())
        for spec in self.module.PANELS:
            self.assertIn('eps-mission-requirements-flow-'+spec['id']+'.pdf', appendix)
        self.assertIn('Physical qualification is excluded.', appendix)

    def test_inputs_outputs_and_activity_flows_are_separate_appendices(self):
        main = (FIG.parent / 'main.tex').read_text()
        appendices = main.split('\\appendix', 1)[1].split('\\backmatter', 1)[0]
        self.assertEqual(re.findall(r'\\include\{([^}]+)\}', appendices),
                         ['apendice', 'fr-inputs-outputs', 'eps-mission-flows', 'fr-activity-flows'])
        concerns = (FIG.parent / 'apendice.tex').read_text()
        for filename, title, label in (
                ('fr-inputs-outputs', 'Framework requirement inputs and outputs', 'appendix:framework-io'),
                ('eps-mission-flows', 'EPS mission engineering flows', 'appendix:eps-mission-flows')):
            text = (FIG.parent / (filename+'.tex')).read_text()
            self.assertTrue(text.startswith('\\chapter{'+title+'}'))
            self.assertIn('\\label{'+label+'}', text)
            self.assertNotIn('\\input{'+filename+'}', concerns)


if __name__ == '__main__':
    unittest.main()
