"""Positive and negative checks of source-grounded FR rationale and direct parents."""
import hashlib
import json
import re
import runpy
from pathlib import Path

import audit_report as audit
import check_fr_rationale as rationale
from test_audit_report import Fixture


class RationaleTests(Fixture):
    def setUp(self):
        super().setUp()
        self.authored = audit.load(self.root/rationale.LEDGER)
        self.rows = audit.unique(self.authored['requirements'], 'authored rationale')

    def check(self):
        _, fr, *_ = audit.current_trace(self.root)
        return audit.audit_fr_rationales(self.root, fr,
                 audit.load(self.root/'traceability/framework-baseline.json')['framework_requirements'])

    def test_complete_source_grounded_coverage(self):
        result = self.check()
        self.assertEqual(result, {'requirements': 40, 'direct_parents': 169,
                                 'source_citations': 76, 'el_hachimi_context_rows': 24})
        self.assertEqual([len(g['ids']) for g in self.authored['groups']], [9, 5, 9, 6, 11])
        self.assertEqual(set().union(*(set(g['ids']) for g in self.authored['groups'])), audit.ACTIVE_FR)

    def test_protected_original_parent_sets(self):
        parents = {rid: r['parent_mrs'] for rid, r in self.rows.items()}
        digest = hashlib.sha256(json.dumps(parents, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(digest, self.authored['protected_parent_sha256'])
        self.assertTrue(all(self.fr[rid]['parents'] == r['parent_mrs'] for rid, r in self.rows.items()))

    def test_citation_numbers_are_not_parent_numbers(self):
        cell = r'MR-03--04.\par Reason \citep[Secs.~01--06, p.~02]{source}.'
        self.assertEqual(audit.parse_fr_rationale(cell)['parents'], ['MR-03', 'MR-04'])
        cell = r'MR-01, MR-03--05.\par Reason \citep[Sec.~6 and Table~2]{source}.'
        self.assertEqual(audit.parse_fr_rationale(cell)['parents'], ['MR-01', 'MR-03', 'MR-04', 'MR-05'])

    def test_stage_parsers_ignore_citation_numbers(self):
        root = Path(__file__).resolve().parents[1]
        scenario = runpy.run_path(str(root/'sysml/check_scenarios.py'))
        logical = runpy.run_path(str(root/'sysml/check_logical_responsibilities.py'))
        text = (self.root/'requirements.tex').read_text()
        old = self.rows['FR-27']['rationale_latex']
        text = text.replace(old, r'MR-03--04.\par Reason \citep[Secs.~01--06 and p.~02]{source}.')
        self.assertEqual(scenario['report_parent_numbers'](text, '27'), {'03', '04'})
        io = (self.root/'fr-inputs-outputs.tex').read_text()
        self.assertEqual(logical['parse_requirements'](text, io)['FR-27']['parents'], ['MR-03', 'MR-04'])

    def test_missing_parent_reference(self):
        old = self.rows['FR-01']['rationale_latex']
        self.replace('requirements.tex', old, old.replace('MR-01--02', 'MR-02'))
        with self.assertRaisesRegex(AssertionError, 'MR/FR derivation mismatch'):
            self.check()

    def test_wrong_parent_reference(self):
        old = self.rows['FR-01']['rationale_latex']
        self.replace('requirements.tex', old, old.replace('MR-01--02', 'MR-01, MR-03'))
        with self.assertRaisesRegex(AssertionError, 'MR/FR derivation mismatch'):
            self.check()

    def test_duplicate_parent_reference(self):
        with self.assertRaisesRegex(AssertionError, 'Duplicate FR parent'):
            audit.parse_fr_rationale(r'MR-01, MR-01.\par Reason \citep[p.~2]{source}.')

    def test_missing_reason(self):
        old = self.rows['FR-01']['rationale_latex']
        citations = ' '.join(re.findall(r'\\citep\[[^]]+\]\{[^}]+\}', old))
        self.replace('requirements.tex', old, r'MR-01--02.\par ' + citations)
        with self.assertRaisesRegex(AssertionError, 'Missing FR rationale'):
            self.check()

    def test_missing_citations(self):
        old = self.rows['FR-01']['rationale_latex']
        new = re.sub(r'\\citep\[[^]]+\]\{[^}]+\}', '', old)
        self.replace('requirements.tex', old, new)
        with self.assertRaisesRegex(AssertionError, 'Missing FR rationale or locator citation'):
            self.check()

    def test_missing_citation_locator(self):
        old = self.rows['FR-01']['rationale_latex']
        new = re.sub(r'\\citep\[[^]]+\]', r'\\citep', old)
        self.replace('requirements.tex', old, new)
        with self.assertRaisesRegex(AssertionError, 'Missing FR rationale or locator citation'):
            self.check()

    def test_non_resolving_bibliography_key(self):
        key = self.rows['FR-01']['citations'][0]['key']
        text = (self.root/'literatura.bib').read_text()
        selector = re.search(r'@\w+\s*\{\s*' + re.escape(key) + r'\s*,', text)[0]
        self.replace('literatura.bib', selector, selector.replace(key, 'removed-citation-key'))
        with self.assertRaisesRegex(AssertionError, 'citation key mismatch'):
            self.check()

    def test_duplicate_bibliography_key(self):
        path = self.root/'literatura.bib'
        path.write_text(path.read_text() + '\n@book{review-0913, title={Duplicate}}\n')
        with self.assertRaisesRegex(AssertionError, 'Duplicate bibliography key'):
            self.check()

    def test_authored_source_transfer_limit_is_required(self):
        self.update(rationale.LEDGER, lambda d: d['requirements'][0]['citations'][0].pop('transfer_limit'))
        with self.assertRaisesRegex(AssertionError, 'Missing checked source basis'):
            self.check()

    def test_complete_authored_coverage_is_required(self):
        self.update(rationale.LEDGER, lambda d: d['requirements'].pop())
        with self.assertRaisesRegex(AssertionError, 'Complete 40-FR rationale coverage'):
            self.check()

    def test_mr_first_header_agreement(self):
        self.replace('needs.tex', r'\textbf{Rationale} \\\n\midrule\n\endfirsthead'.replace('\\n', '\n'),
                     r'\textbf{Sources} \\\n\midrule\n\endfirsthead'.replace('\\n', '\n'))
        with self.assertRaisesRegex(AssertionError, 'headers must use ID and Rationale'):
            self.check()

    def test_fr_repeated_header_agreement(self):
        old = '\\textbf{ID} & \\textbf{System requirement} & \\textbf{Rationale} \\\\\n\\midrule\n\\endhead'
        self.replace('requirements.tex', old, old.replace('textbf{ID}', 'textbf{FR}'))
        with self.assertRaisesRegex(AssertionError, 'headers must use ID and Rationale'):
            self.check()

    def test_refresh_is_idempotent_and_preserves_native_sources(self):
        paths = ('requirements.tex', 'traceability/framework-baseline.json', 'sysml/03-requirements.sysml')
        before = {path: (self.root/path).read_bytes() for path in paths}
        rationale.refresh(self.root)
        self.assertEqual(before, {path: (self.root/path).read_bytes() for path in paths})
        self.check()
