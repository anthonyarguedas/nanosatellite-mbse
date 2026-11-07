"""Check that report references follow the current framework requirement table.

PYTHONPATH=final_report/fig python3 -m unittest test_report_requirements
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import unittest

REPORT = Path(__file__).resolve().parent.parent


def expand_numbers(first, tail):
    numbers = {int(first)}
    previous = int(first)
    for separator, value in re.findall(r'(--|/)(?:FR-|V)?(\d{2})', tail):
        current = int(value)
        numbers.update(range(previous, current+1) if separator == '--' else [current])
        previous = current
    return numbers


def requirement_references(text):
    return {f'FR-{number:02}'
            for first, tail in re.findall(r'\bFR-(\d{2})((?:(?:--|/)(?:FR-)?\d{2})*)', text)
            for number in expand_numbers(first, tail)}


class ReportRequirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requirements = (REPORT / 'requirements.tex').read_text()
        cls.active = set(re.findall(r'^(FR-\d{2}) &', cls.requirements, re.M))

    def test_current_requirements_keep_their_identifiers(self):
        identifiers = re.findall(r'^(FR-\d{2}) &', self.requirements, re.M)
        self.assertEqual(len(identifiers), 23)
        self.assertEqual(len(identifiers), len(self.active))
        self.assertIn('23 FRs', self.requirements)

    def test_each_current_requirement_has_exactly_one_matching_mop(self):
        rows = re.findall(r'^(FR-\d{2})\\newline MOP-FR(\d{2}) &', self.requirements, re.M)
        self.assertEqual(Counter(fr for fr, _ in rows), Counter(self.active))
        self.assertTrue(all(fr == 'FR-'+number for fr, number in rows))

    def test_every_report_reference_resolves_to_a_current_requirement(self):
        for path in sorted(REPORT.glob('*.tex')):
            with self.subTest(path=path.name):
                text = re.sub(r'(?m)^\s*%.*$', '', path.read_text())
                self.assertEqual(requirement_references(text)-self.active, set())
                mop_refs = {'FR-'+number for number in re.findall(r'\bMOP-FR(\d{2})', text)}
                self.assertEqual(mop_refs-self.active, set())
                self.assertNotRegex(text, r'\b46 (?:active cases|FRs)\b|\bten critical MOPs\b')

    def test_logical_allocations_cover_each_requirement_once(self):
        text = (REPORT / 'logical.tex').read_text()
        assigned = []
        for numbers in re.findall(r'^L\d{2} [^&]+ & ([^&]+) &', text, re.M):
            for token in numbers.split(','):
                match = re.fullmatch(r'\s*(\d{2})(--\d{2})?\s*', token)
                self.assertIsNotNone(match)
                assigned.extend(f'FR-{number:02}'
                                for number in expand_numbers(match[1], match[2] or ''))
        self.assertEqual(Counter(assigned), Counter(self.active))

    def test_physical_and_logical_component_allocations_agree(self):
        logical = (REPORT / 'logical.tex').read_text()
        physical = (REPORT / 'physical-candidates.tex').read_text()
        for cid, numbers in re.findall(r'^(L\d{2}) [^&]+ & ([^&]+) &', logical, re.M):
            with self.subTest(component=cid):
                expected = set()
                for token in numbers.split(','):
                    match = re.fullmatch(r'\s*(\d{2})(--\d{2})?\s*', token)
                    expected.update(f'FR-{number:02}'
                                    for number in expand_numbers(match[1], match[2] or ''))
                section = physical.split('\\textbf{'+cid+' ', 1)[1]
                allocation_line = next(line for line in section.splitlines() if '{FR-' in line)
                self.assertEqual(requirement_references(allocation_line), expected)

    def test_candidate_matrix_uses_the_three_remaining_components(self):
        text = (REPORT / 'physical-candidates.tex').read_text()
        matrix = text.split('\\label{tab:framework-candidate-inventories}', 1)[1]
        matrix = matrix.split('\\end{longtable}', 1)[0]
        header = '\\textbf{Candidate} & \\textbf{L01} & \\textbf{L03} & \\textbf{L06}'
        self.assertEqual(matrix.count(header), 2)
        rows = re.findall(r'^(PA-[A-Z]+) & ([^\n]+)', matrix, re.M)
        self.assertEqual({name for name, _ in rows}, {'PA-COM', 'PA-VS', 'PA-NS', 'PA-GY', 'PA-CDT'})
        for name, row in rows:
            with self.subTest(candidate=name):
                self.assertEqual(len(row.split(' & ')), 3)

    def test_verification_cases_match_current_requirements(self):
        text = (REPORT / 'verification-plan.tex').read_text()
        table = text.split('\\endfoot', 1)[1].split('\\end{longtable}', 1)[0]
        actual = []
        for line in table.splitlines():
            if not line.startswith('V'):
                continue
            heading = line.split(' & ', 1)[0]
            for first, tail in re.findall(r'\bV(\d{2})((?:--V?\d{2})?)', heading):
                actual.extend(f'FR-{number:02}' for number in expand_numbers(first, tail))
        self.assertEqual(Counter(actual), Counter(self.active))
        references = {f'FR-{number:02}'
                      for first, tail in re.findall(r'\bV(\d{2})((?:--V?\d{2})?)', text)
                      for number in expand_numbers(first, tail)}
        self.assertEqual(references, self.active)

    def test_critical_mop_tables_contain_only_the_four_remaining_measures(self):
        expected = {'02', '03', '10', '34'}
        for name in ('physical-candidates.tex', 'trade-selection.tex'):
            with self.subTest(path=name):
                text = (REPORT / name).read_text()
                self.assertEqual(set(re.findall(r'^MOP-FR(\d{2})', text, re.M)), expected)
                self.assertIn('four critical MOPs', text)

    def test_diagram_metadata_contains_only_current_requirement_references(self):
        inventory = json.loads((REPORT / 'fig/logical-architecture.inventory.json').read_text())
        self.assertEqual(set(inventory['requirements']), self.active)
        self.assertEqual(requirement_references(json.dumps(inventory)), self.active)
        assigned = [fr for component in inventory['components'] for fr in component['requirements']]
        self.assertEqual(Counter(assigned), Counter(self.active))

    def test_main_document_does_not_include_deleted_appendices(self):
        text = (REPORT / 'main.tex').read_text()
        for name in re.findall(r'\\(?:input|include)\{([^}]+)\}', text):
            with self.subTest(include=name):
                self.assertTrue((REPORT / (name+'.tex')).is_file())

    def test_range_and_shorthand_references_expand(self):
        self.assertEqual(requirement_references('FR-01--04, FR-13/20, FR-26--27'),
                         {'FR-01', 'FR-02', 'FR-03', 'FR-04', 'FR-13', 'FR-20', 'FR-26', 'FR-27'})


if __name__ == '__main__':
    unittest.main()
