"""Check compact figure placement and removal of the concern-to-MOE appendix."""
import json
from pathlib import Path
import re
import unittest

REPORT = Path(__file__).resolve().parent.parent


class ReportLayoutTests(unittest.TestCase):
    def test_four_component_architecture_uses_one_compact_canvas(self):
        provenance = json.loads((REPORT / 'fig/logical-architecture.provenance.json').read_text())
        inventory = json.loads((REPORT / 'fig/logical-architecture.inventory.json').read_text())
        self.assertEqual(provenance['dimensions'], {'pdf_pt': [760, 620], 'pdf_pages': 1})
        self.assertEqual(len(inventory['components']), 4)
        self.assertEqual(len(inventory['interfaces']), 2)
        self.assertEqual(sum(len(i['flows']) for i in inventory['interfaces']), 4)

    def test_simulation_is_inside_the_single_architecture_view(self):
        text = (REPORT / 'logical.tex').read_text()
        self.assertNotIn('\\begin{landscape}', text)
        self.assertEqual(text.count('\\begin{figure}[p]'), 1)
        self.assertEqual(text.count('\\caption['), 1)
        self.assertNotIn('\\ContinuedFloat', text)
        figure = text.split('\\begin{figure}[p]', 1)[1].split('\\end{figure}', 1)[0]
        self.assertEqual(figure.count('\\includegraphics'), 1)
        self.assertIn('\\includegraphics[width=\\linewidth]{fig/logical-architecture.pdf}', figure)
        self.assertNotIn('page=', figure)
        self.assertNotIn('including simulation tools', figure)

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
