"""Focused coverage, semantics, layout and artifact checks for Appendix D.

python3 -m unittest discover -s final_report/fig -p 'test_fr_activity_flows.py' -v

These checks verify the drawings and their trace records. They do not verify
an implemented framework or validate an EPS engineering conclusion.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from diagram_style import (LIGHT, SerifMetrics, foreground_arrowheads, run, sha,
                           validate_arrowheads, validate_style)

FIG = Path(__file__).resolve().parent


class FRActivityFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('fr_activity_flows', FIG / 'fr-activity-flows.py')
        cls.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.m)
        metrics = SerifMetrics()
        cls.panels = [cls.m.Panel(spec, metrics) for spec in cls.m.PANELS]
        cls.by_id = {panel.spec['id'][:2]: panel for panel in cls.panels}

    def test_exact_current_requirement_set_and_visible_activity_coverage(self):
        actual = self.m.actual_requirements()
        self.assertEqual(len(actual), 46)
        self.assertNotIn('FR-12', actual)
        self.assertNotIn('FR-40', actual)
        mapping = self.m.coverage(self.panels)
        self.assertEqual(set(mapping), set(actual))
        for fr, entries in mapping.items():
            self.assertTrue(entries, fr)
            for entry in entries:
                self.assertRegex(entry['activity'], r'^\d\d\.\d+$')
                self.assertTrue(entry['label'])
        self.assertEqual(self.m.check_report(self.panels, mapping)['panels'], 23)

    def test_short_activities_labeled_exchanges_and_clear_receiver_endpoints(self):
        for panel in self.panels:
            with self.subTest(panel=panel.spec['id']):
                checks = self.m.check_panel(panel)
                self.assertTrue(checks['visible_activity_identifiers'])
                self.assertTrue(checks['labels_clear_of_routes_nodes_and_each_other'])
                self.assertGreaterEqual(checks['labeled_exchanges'], 5)
                # Conservative final-size estimate: 455 pt width / 540 pt height.
                scale = min(455/panel.figure.width, 540/panel.figure.height)
                self.assertGreaterEqual(scale * checks['minimum_source_font_pt'], 9)

    def test_unknown_requirement_and_missing_visible_identifier_are_rejected(self):
        spec = copy.deepcopy(self.m.PANELS[0])
        spec['nodes'][1]['fr'] = ['FR-99']
        panels = [self.m.Panel(spec, self.panels[0].figure.metrics), *self.panels[1:]]
        with self.assertRaisesRegex(ValueError, 'FR coverage'):
            self.m.coverage(panels)
        panel = copy.deepcopy(self.panels[0])
        panel.figure.root.find('.//{*}g[@data-node="2"]/{*}text[@data-trace-header]').text = '02'
        with self.assertRaisesRegex(ValueError, 'visible activity / FR identifier'):
            self.m.check_panel(panel)

    def test_missing_label_changed_dependency_and_dense_node_are_rejected(self):
        panel = copy.deepcopy(self.panels[0])
        group = panel.figure.root.find('.//{*}g[@data-flow="1"]')
        group.remove(group.find('./{*}text'))
        with self.assertRaisesRegex(ValueError, 'exchange label'):
            self.m.check_panel(panel)
        panel = copy.deepcopy(self.panels[0])
        panel.figure.root.find('.//{*}g[@data-flow="1"]').attrib['data-target'] = '4'
        with self.assertRaisesRegex(ValueError, 'dependency'):
            self.m.check_panel(panel)
        panel = copy.deepcopy(self.panels[0])
        group = panel.figure.root.find('.//{*}g[@data-node="2"]')
        group.append(copy.deepcopy(group.find('./{*}text[@data-activity-label]')))
        with self.assertRaisesRegex(ValueError, 'activity label'):
            self.m.check_panel(panel)

    def test_route_over_text_off_receiver_and_internal_gray_are_rejected(self):
        panel = copy.deepcopy(self.panels[0])
        panel.figure.root.find('.//{*}g[@data-flow="1"]/{*}text').attrib['x'] = '270'
        with self.assertRaisesRegex(ValueError, 'Route crosses exchange text'):
            self.m.check_panel(panel)
        panel = copy.deepcopy(self.panels[0])
        path = 'M275 160 V279'
        panel.flows[0]['path'] = path
        panel.figure.root.find('.//{*}g[@data-flow="1"]/{*}path').attrib['d'] = path
        with self.assertRaisesRegex(ValueError, 'endpoint'):
            self.m.check_panel(panel)
        panel = copy.deepcopy(self.panels[0])
        panel.figure.root.find('.//{*}g[@data-node="2"]/{*}rect').attrib['fill'] = LIGHT
        with self.assertRaisesRegex(ValueError, 'Gray is reserved'):
            self.m.check_panel(panel)

    def test_assistance_acknowledgement_response_and_completion_are_separate(self):
        p = self.by_id['05']
        self.assertEqual(p.nodes['2']['fr'], ['FR-41', 'FR-48'])
        self.assertEqual(p.nodes['4']['fr'], ['FR-47', 'FR-48'])
        self.assertEqual(p.nodes['5']['fr'], ['FR-48'])
        labels = ' '.join(' '.join(flow['labels']) for flow in p.flows)
        for token in ('acknowledgement limit', 'interactive response limit',
                      'pending / unavailable', 'First-response time', 'completion time'):
            self.assertIn(token, labels)

    def test_stale_marking_application_block_and_reassessment_are_distinct(self):
        p = self.by_id['06']
        self.assertEqual(p.nodes['2']['fr'], ['FR-30'])
        self.assertEqual(p.nodes['3']['fr'], ['FR-46'])
        self.assertEqual(p.nodes['6']['fr'], ['FR-45'])
        blocked = next(flow for flow in p.flows if flow['target'] == '6')
        self.assertIn('[stale]', blocked['labels'])
        self.assertEqual(blocked['kind'], 'findings')
        self.assertTrue(any(flow['source'] == '7' and flow['target'] == '4' for flow in p.flows))
        self.assertIn('no assumption of completed fresh guidance', ' '.join(p.flows[2]['labels']))

    def test_transfer_rejection_preserves_controlled_content_and_history_masks(self):
        admission = self.by_id['01']
        reject = next(flow for flow in admission.flows if flow['target'] == '5')
        self.assertIn('[incompatible]', reject['labels'])
        self.assertIn('Unchanged controlled content;', admission.flows[-1]['labels'])
        history = self.by_id['11']
        labels = ' '.join(' '.join(flow['labels']) for flow in history.flows)
        self.assertIn('before numerical use', ' '.join(self.by_id['10'].nodes['3']['labels']))
        self.assertIn('missing / inactive readings remain distinct from zero', labels)
        self.assertIn('processing masks', labels)

    def test_same_scenario_exchange_and_separate_execution_ownership(self):
        p = self.by_id['10']
        self.assertEqual(p.nodes['4']['owner'], 'Framework')
        self.assertEqual(p.nodes['6']['owner'], 'NVIDIA Omniverse')
        self.assertEqual(p.nodes['7']['owner'], 'NVIDIA Omniverse')
        self.assertEqual(p.nodes['2']['fr'], ['FR-43'])
        self.assertEqual(p.nodes['5']['fr'], ['FR-44'])
        self.assertIn('same scenario / configuration', ' '.join(p.flows[4]['labels']))
        sil = self.by_id['19']
        self.assertEqual(sil.nodes['2']['owner'], 'Framework')
        self.assertEqual(sil.nodes['5']['owner'], 'F Prime host')
        self.assertEqual(sil.nodes['6']['owner'], 'Framework')
        self.assertFalse(any({flow['source'], flow['target']} == {'3', '5'} for flow in sil.flows))
        self.assertTrue(any(flow['source'] == '5' and flow['target'] == '6' for flow in sil.flows))
        self.assertTrue(any(flow['source'] == '5' and flow['target'] == '2' for flow in sil.flows))
        self.assertTrue(any(flow['source'] == '2' and flow['target'] == '6' for flow in sil.flows))

    def test_credibility_and_quantitative_ram_gaps_remain_explicit(self):
        p = self.by_id['14']
        self.assertIn('proposal', ' '.join(p.nodes['2']['labels']))
        self.assertEqual(p.nodes['3']['owner'], 'Engineer')
        self.assertEqual(p.nodes['5']['fr'], ['FR-21'])
        self.assertTrue(any('separate independent' in ' '.join(flow['labels']) for flow in p.flows))
        independent = next(flow for flow in p.flows if flow['source'] == '8')
        self.assertEqual(independent['target'], '5')
        self.assertIn('independent assessment evidence or gaps;', independent['labels'])
        self.assertIn('[if applicable]', ' '.join(p.flows[3]['labels']))
        ram = self.by_id['15']
        self.assertEqual(' '.join(ram.nodes['7']['labels']), 'Leave affected results unavailable')
        self.assertTrue(any(flow['source'] == '3' and flow['target'] == '7' for flow in ram.flows))

    def test_current_authorization_gates_external_builds(self):
        p = self.by_id['17']
        self.assertEqual(p.nodes['5']['owner'], 'F Prime toolchain')
        release = next(flow for flow in p.flows if flow['source'] == '3' and flow['target'] == '4')
        self.assertEqual(release['kind'], 'authorization')
        self.assertIn('[current and authorized]', ' '.join(release['labels']))
        self.assertTrue(any(flow['source'] == '3' and flow['target'] == '7' for flow in p.flows))
        self.assertTrue(any(flow['source'] == '5' and flow['target'] == '6' for flow in p.flows))

    def test_replay_rules_fixed_before_replay_and_failed_runs_preserved(self):
        p = self.by_id['21']
        labels = ' '.join(' '.join(flow['labels']) for flow in p.flows)
        self.assertIn('failed / cancelled / partial runs', labels)
        self.assertIn('fixed before replay', labels)
        self.assertIn('preserved original raw outputs', labels)
        self.assertIn('missing-dependency findings', labels)

    def test_change_and_review_authorities_do_not_follow_from_preparation(self):
        change = self.by_id['22']
        self.assertEqual(change.nodes['3']['owner'], 'Engineer')
        successor = next(flow for flow in change.flows if flow['target'] == '5')
        self.assertEqual(successor['kind'], 'authorization')
        self.assertIn('[authorized change]', ' '.join(successor['labels']))
        review = self.by_id['23']
        self.assertEqual(review.nodes['3']['owner'], 'Reviewers')
        self.assertEqual(review.nodes['5']['owner'], 'Review authority')
        self.assertTrue(any(flow['source'] == '6' and flow['target'] == '9' for flow in review.flows))
        record = next(flow for flow in review.flows if flow['target'] == '7')
        self.assertEqual(record['kind'], 'authorization')
        self.assertIn('prepared status remains distinct', ' '.join(record['labels']))
        outcomes = {flow['target'] for flow in review.flows if flow['source'] == '7'}
        self.assertEqual(outcomes, {'8', '10', '11'})

    def test_published_svg_is_exact_generated_source_with_foreground_heads(self):
        for panel in self.panels:
            with self.subTest(panel=panel.spec['id']):
                expected = copy.deepcopy(panel.figure.root)
                foreground_arrowheads(expected)
                ET.indent(expected)
                data = ET.tostring(expected, encoding='utf-8', xml_declaration=True)
                published = FIG / ('fr-activity-flow-'+panel.spec['id']+'.svg')
                self.assertEqual(hashlib.sha256(data).hexdigest(), sha(published))
                root = ET.parse(published).getroot()
                validate_style(root)
                validate_arrowheads(root)
                check = copy.deepcopy(panel)
                check.figure.root = root
                self.m.check_panel(check)

    def test_all_sources_fonts_and_artifacts_match_current_provenance(self):
        record = json.loads(BASE_PROVENANCE.read_text())
        self.assertEqual(record['generator_sha256'], sha(FIG / 'fr-activity-flows.py'))
        self.assertEqual(record['style_sha256'], sha(FIG / 'diagram_style.py'))
        self.assertEqual(record['coverage'], self.m.coverage(self.panels))
        self.assertEqual(record['requirements'], self.m.actual_requirements())
        for relative, expected in record['source_sha256'].items():
            self.assertEqual(sha(FIG.parent.parent / relative), expected, relative)
        self.assertEqual(len(record['panels']), len(self.panels))
        for panel, artifact in zip(self.panels, record['panels']):
            self.assertEqual(artifact['id'], panel.spec['id'])
            for kind, expected in artifact['artifact_sha256'].items():
                self.assertEqual(sha(FIG / (artifact['file']+'.'+kind)), expected)
            self.assertEqual(artifact['svg_sha256_used_for_pdf'], artifact['artifact_sha256']['svg'])
            for font in artifact['font']['files'].values():
                self.assertEqual(sha(font['path']), font['sha256'])
            text = run(['pdftotext', str(FIG / (artifact['file']+'.pdf')), '-'])
            for fr in artifact['checks']['visible_frs']:
                self.assertIn(fr, text)
        self.assertEqual(record['artifact_sha256']['pdf'], sha(FIG / 'fr-activity-flows.pdf'))

    def test_combined_pdf_has_all_panels_in_order(self):
        info = run(['pdfinfo', str(FIG / 'fr-activity-flows.pdf')])
        self.assertEqual(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1), '23')
        text = run(['pdftotext', '-layout', str(FIG / 'fr-activity-flows.pdf'), '-'])
        pages = text.split('\f')
        for index, panel in enumerate(self.panels):
            first = next(key for key, node in panel.nodes.items() if node['kind'] != 'external')
            self.assertIn(panel.spec['id'][:2]+'.'+first, pages[index])

    def test_appendix_is_separate_and_graphical_syntax_is_local(self):
        main = (FIG.parent / 'main.tex').read_text()
        section = (FIG.parent / 'requirements.tex').read_text()
        appendix = (FIG.parent / 'fr-activity-flows.tex').read_text()
        includes = re.findall(r'\\include\{([^}]+)\}', main.split('\\appendix', 1)[1].split('\\backmatter', 1)[0])
        self.assertEqual(includes, ['apendice', 'fr-inputs-outputs', 'eps-mission-flows', 'fr-activity-flows'])
        self.assertIn('appendix:fr-activity-flows', section)
        self.assertNotIn('Short verb phrases name activities.', section)
        self.assertIn('dotted arrows carry findings or feedback', appendix)
        self.assertIn('dashed arrows carry authorization', appendix)
        self.assertIn('They add no requirements.', appendix)
        self.assertIn('Physical execution and target hardware qualification are excluded.', appendix)


BASE_PROVENANCE = FIG / 'fr-activity-flows.provenance.json'

if __name__ == '__main__':
    unittest.main()
