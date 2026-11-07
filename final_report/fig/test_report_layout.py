"""Check compact figure placement and removal of the concern-to-MOE appendix."""
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

REPORT = Path(__file__).resolve().parent.parent


class ReportLayoutTests(unittest.TestCase):
    def test_three_component_architecture_uses_two_compact_canvases(self):
        internal = ET.parse(REPORT / 'fig/logical-architecture.svg').getroot()
        boundary = ET.parse(REPORT / 'fig/logical-architecture-panel-02.svg').getroot()
        self.assertEqual(internal.attrib['viewBox'], '0 0 690 330')
        self.assertEqual(boundary.attrib['viewBox'], '0 0 690 420')
        self.assertEqual(len(internal.findall('.//{*}g[@data-component]')), 3)
        self.assertEqual(len(boundary.findall('.//{*}rect[@data-port]')), 4)
        self.assertEqual(len(boundary.findall('./{*}g[@data-flow]')), 8)

    def test_simulation_is_merged_into_the_portrait_external_interface_view(self):
        text = (REPORT / 'logical.tex').read_text()
        self.assertNotIn('\\begin{landscape}', text)
        self.assertEqual(text.count('\\begin{figure}[p]'), 1)
        self.assertEqual(text.count('\\caption['), 1)
        self.assertNotIn('\\ContinuedFloat', text)
        self.assertIn('\\includegraphics[page=1,width=\\linewidth]', text)
        self.assertIn('\\includegraphics[page=2,width=\\linewidth]', text)
        self.assertNotIn('page=3,', text)
        self.assertNotIn('Logical architecture: simulation coupling', text)
        figure = text.split('\\begin{figure}[p]', 1)[1].split('\\end{figure}', 1)[0]
        self.assertIn('page=1,', figure)
        self.assertIn('page=2,', figure)

    def test_csrm_figures_can_share_portrait_float_pages(self):
        text = (REPORT / 'generic-cubesat-structure.tex').read_text()
        self.assertNotIn('\\begin{landscape}', text)
        self.assertEqual(text.count('\\begin{figure}[p]'), 4)
        self.assertEqual(text.count('\\includegraphics[width=0.95\\linewidth]'), 4)
        self.assertEqual(text.count('\\clearpage'), 1)
        for name in ('csrm-mission-structure', 'csrm-cubesat-subsystems',
                     'csrm-eps-components', 'csrm-eps-topology'):
            self.assertIn('\\label{fig:'+name+'}', text)

    def test_full_concern_appendix_is_retained_but_not_included(self):
        main = (REPORT / 'main.tex').read_text()
        self.assertNotIn('\\include{apendice}', main)
        self.assertNotIn('\\appendix', main)
        self.assertTrue((REPORT / 'apendice.tex').is_file())
        for path in REPORT.glob('*.tex'):
            if path.name == 'apendice.tex':
                continue
            with self.subTest(path=path.name):
                self.assertNotIn('appendix:stakeholder-concerns', path.read_text())
        self.assertNotIn('The appendix provides', (REPORT / 'intro.tex').read_text())

    def test_main_text_concern_links_resolve_to_the_main_text_summary(self):
        summary = (REPORT / 'as-is-domain.tex').read_text()
        identifiers = set(re.findall(r'\\ConcernSummary\{([^}]+)\}', summary))
        references = set()
        for path in REPORT.glob('*.tex'):
            if path.name != 'apendice.tex':
                references.update(re.findall(r'\\ConcernRef\{([^}]+)\}', path.read_text()))
        self.assertTrue(identifiers)
        self.assertTrue(references)
        self.assertEqual(references-identifiers, set())
        style = (REPORT / 'sty/framework-report.tex').read_text()
        definition = style.split('\\newcommand{\\ConcernSummary}', 1)[1].split('\n\n', 1)[0]
        self.assertIn('\\ConcernAnchor{#1}', definition)
        self.assertNotIn('\\ConcernRef{#1}', definition)

    def test_concern_moe_appendix_and_its_references_are_removed(self):
        for path in REPORT.glob('*.tex'):
            with self.subTest(path=path.name):
                text = path.read_text()
                self.assertNotIn('framework-moe-concerns', text)
                self.assertNotIn('Concern contributions to measures of effectiveness', text)
        appendix = (REPORT / 'apendice.tex').read_text()
        self.assertIn('\\chapter{Stakeholder concerns and causal analysis}', appendix)
        self.assertIn('\\ConcernCause{C-NE-02.5.2}', appendix)


if __name__ == '__main__':
    unittest.main()
