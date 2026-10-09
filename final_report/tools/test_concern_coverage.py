"""Focused occurrence-level positive/negative concern/MOE consistency tests."""
from pathlib import Path
import shutil
import tempfile
import unittest

import audit_report as audit
import check_concern_coverage as coverage

REPORT = Path(__file__).resolve().parents[1]


class ConcernCoverageTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for name in ('apendice.tex', 'needs.tex', 'main.tex'):
            shutil.copy2(REPORT/name, self.root/name)
        (self.root/'sty').mkdir()
        shutil.copy2(REPORT/'sty/framework-report.tex', self.root/'sty/framework-report.tex')
        for name in ('sysml', 'traceability'):
            shutil.copytree(REPORT/name, self.root/name, ignore=shutil.ignore_patterns('__pycache__'))

    def replace(self, path, old, new):
        path = self.root/path; text = path.read_text()
        self.assertEqual(text.count(old), 1, 'Mutation selector must match one region')
        path.write_text(text.replace(old, new))

    def change_ledger(self, change):
        path = self.root/coverage.LEDGER; record = audit.load(path); change(record)
        path.write_text(__import__('json').dumps(record))

    def test_all_roots_descendants_and_aliases(self):
        result = coverage.check(self.root)
        self.assertEqual(result['counts']['concerns'], 120)
        self.assertEqual(result['counts']['roots'], 27)
        self.assertEqual(result['counts']['descendants'], 93)
        self.assertEqual(result['counts']['unmapped_concerns'], 0)
        self.assertEqual(result['counts']['moes'], 6)
        self.assertTrue(all(result['concern_to_moe'].values()))
        self.assertEqual(result['display']['orientation'], 'MOE to concerns')
        self.assertEqual(result['display']['rows'], 165)
        self.assertEqual(result['display']['memberships'], 435)
        self.assertEqual(result['display']['linked_concern_destinations'], 120)
        self.assertEqual(result['display']['source'], 'apendice.tex')
        self.assertEqual(result['display']['table_label'], 'tab:framework-moe-concerns')
        self.assertEqual(result['display']['appendix_label'], 'appendix:framework-moe-concerns')
        self.assertEqual(set(result['display']['per_moe_rows']), coverage.MOES)

    def test_cost_not_silently_reduced_to_person_time(self):
        result = coverage.check(self.root)
        self.assertEqual(result['concern_to_moe']['C-PM-01.2'], ['MOE-05'])
        self.assertIn('MOE-05', result['concern_to_moe']['C-EPS-05.3'])

    def test_replica_context_is_not_adoption_or_replacement(self):
        result = coverage.check(self.root)
        self.assertEqual(result['concern_to_moe']['C-PM-04'], ['MOE-06'])
        row = next(r for r in result['concerns'] if r['id'] == 'C-PM-04')
        self.assertIn('external context', row['interpretation'])
        self.assertIn('Operational troubleshooting and replica replacement are excluded', row['interpretation'])

    def test_removed_deep_descendant(self):
        self.change_ledger(lambda r: r['groups'][10]['concern_ids'].remove('C-SE-03.3.1.3.2'))
        with self.assertRaisesRegex(AssertionError, 'Unmapped concerns'):
            coverage.check(self.root)

    def test_unknown_link(self):
        self.change_ledger(lambda r: r['groups'][0]['concern_ids'].append('C-PM-99'))
        with self.assertRaisesRegex(AssertionError, 'Unknown concern anchor'):
            coverage.check(self.root)

    def test_duplicate_occurrence(self):
        self.change_ledger(lambda r: r['groups'][0]['concern_ids'].append('C-PM-01.1'))
        with self.assertRaisesRegex(AssertionError, 'Duplicate grouped concern'):
            coverage.check(self.root)

    def test_empty_moe_set(self):
        self.change_ledger(lambda r: r['groups'][0].update(moe_ids=[]))
        with self.assertRaisesRegex(AssertionError, 'Invalid MOE group'):
            coverage.check(self.root)

    def test_alias_omits_target_contribution(self):
        self.change_ledger(lambda r: (r['groups'][25]['moe_ids'].remove('MOE-05'),
                                      r['groups'][25]['display'].pop('MOE-05')))
        with self.assertRaisesRegex(AssertionError, 'Alias contribution omitted'):
            coverage.check(self.root)

    def test_removed_pdf_descendant_membership(self):
        old = (r'MOE-02 & \ConcernRef{C-SE-03.3.1.3}, \ConcernRef{C-SE-03.3.1.3.1}, '
               r'\ConcernRef{C-SE-03.3.1.3.2} & Errors in criteria and power budgeting.')
        new = (r'MOE-02 & \ConcernRef{C-SE-03.3.1.3}, \ConcernRef{C-SE-03.3.1.3.1} '
               r'& Errors in criteria and power budgeting.')
        self.replace(coverage.REPORT_TABLE, old, new)
        with self.assertRaisesRegex(AssertionError, 'Displayed forward concern/MOE membership mismatch'):
            coverage.check(self.root)

    def test_duplicate_forward_membership(self):
        self.replace(coverage.REPORT_TABLE,
                     r'MOE-04 & \ConcernRef{C-PM-01.1} & Learning to write verifiable requirements.',
                     r'MOE-04 & \ConcernRef{C-PM-01.1}, \ConcernRef{C-PM-01.1} & Learning to write verifiable requirements.')
        with self.assertRaisesRegex(AssertionError, 'Duplicate displayed concern/MOE membership'):
            coverage.check(self.root)

    def test_wrong_forward_membership(self):
        self.replace(coverage.REPORT_TABLE,
                     r'MOE-04 & \ConcernRef{C-PM-01.1} & Learning to write verifiable requirements.',
                     r'MOE-04 & \ConcernRef{C-PM-01.2} & Learning to write verifiable requirements.')
        with self.assertRaisesRegex(AssertionError, 'Displayed forward concern/MOE membership mismatch'):
            coverage.check(self.root)

    def test_unlinked_forward_id(self):
        self.replace(coverage.REPORT_TABLE,
                     r'MOE-04 & \ConcernRef{C-PM-01.1} & Learning to write verifiable requirements.',
                     r'MOE-04 & C-PM-01.1 & Learning to write verifiable requirements.')
        with self.assertRaisesRegex(AssertionError, 'Forward row concern limit exceeded'):
            coverage.check(self.root)

    def test_table_is_not_duplicated_in_body(self):
        path = self.root/'needs.tex'
        path.write_text(path.read_text() + coverage.report_table(self.root))
        with self.assertRaisesRegex(AssertionError, 'Concern/MOE table duplicated in main text'):
            coverage.check(self.root)

    def test_unlabelled_body_duplicate_is_rejected(self):
        path = self.root/'needs.tex'
        path.write_text(path.read_text() + '\nMOE-04 & \\ConcernRef{C-PM-01.1} & Learning effort. \\\\\n')
        with self.assertRaisesRegex(AssertionError, 'Concern/MOE table duplicated in main text'):
            coverage.check(self.root)

    def test_missing_appendix_region(self):
        self.replace(coverage.REPORT_TABLE, coverage.BEGIN, '% Removed coverage region')
        with self.assertRaisesRegex(AssertionError, 'Missing/duplicate appendix coverage region'):
            coverage.check(self.root)

    def test_missing_main_appendix_reference(self):
        self.replace('needs.tex', r'\ref{appendix:framework-moe-concerns}', 'A.1')
        with self.assertRaisesRegex(AssertionError, 'Missing main-text appendix/table reference'):
            coverage.check(self.root)

    def test_missing_main_table_reference(self):
        self.replace('needs.tex', r'\ref{tab:framework-moe-concerns}', 'A.1')
        with self.assertRaisesRegex(AssertionError, 'Missing main-text appendix/table reference'):
            coverage.check(self.root)

    def test_appendix_section_label_is_required(self):
        self.replace(coverage.REPORT_TABLE, r'\label{appendix:framework-moe-concerns}', '')
        with self.assertRaisesRegex(AssertionError, 'Missing/misplaced appendix section label'):
            coverage.check(self.root)

    def test_appendix_table_label_is_required(self):
        self.replace(coverage.REPORT_TABLE, r'\label{tab:framework-moe-concerns}', '')
        with self.assertRaisesRegex(AssertionError, 'Missing/duplicate appendix table label'):
            coverage.check(self.root)

    def test_appendix_must_be_included(self):
        self.replace('main.tex', r'\include{apendice}', '% Removed appendix include')
        with self.assertRaisesRegex(AssertionError, 'must be included after appendix switch'):
            coverage.check(self.root)

    def test_appendix_switch_is_required(self):
        self.replace('main.tex', r'\appendix', '% Removed appendix switch')
        with self.assertRaisesRegex(AssertionError, 'must be included after appendix switch'):
            coverage.check(self.root)

    def test_displayed_ids_are_actual_hyperlinks(self):
        self.replace('sty/framework-report.tex', r'\hyperref[concern:#1]{\ConcernId{#1}}', r'\ConcernId{#1}')
        with self.assertRaisesRegex(AssertionError, 'ConcernRef must link'):
            coverage.check(self.root)

    def test_wrong_hyperlink_destination_is_rejected(self):
        self.replace('sty/framework-report.tex', r'\hyperref[concern:#1]{\ConcernId{#1}}', r'\hyperref[concern:C-PM-01]{\ConcernId{#1}}')
        with self.assertRaisesRegex(AssertionError, 'ConcernRef must link'):
            coverage.check(self.root)

    def test_concern_destination_is_required(self):
        self.replace('sty/framework-report.tex', r'\label{concern:#1}', r'\label{unlinked:#1}')
        with self.assertRaisesRegex(AssertionError, 'Missing concern hyperlink destination'):
            coverage.check(self.root)

    def test_root_anchor_call_is_required(self):
        self.replace(coverage.REPORT_TABLE, r'\ConcernAnchor{#1}\noindent', r'\noindent')
        with self.assertRaisesRegex(AssertionError, 'Missing concern anchor call: ConcernRoot'):
            coverage.check(self.root)

    def test_descendant_anchor_call_is_required(self):
        self.replace('sty/framework-report.tex', r'\item\leavevmode\ConcernAnchor{#1}', r'\item\leavevmode')
        with self.assertRaisesRegex(AssertionError, 'Missing concern anchor call: ConcernCause'):
            coverage.check(self.root)

    def test_descendant_anchor_stays_with_its_first_line(self):
        self.replace('sty/framework-report.tex', r'\item\leavevmode\ConcernAnchor{#1}', r'\item\ConcernAnchor{#1}')
        with self.assertRaisesRegex(AssertionError, 'Descendant anchor must stay with its displayed ID'):
            coverage.check(self.root)

    def test_forward_chunks_remain_small(self):
        record, _, _ = coverage.authored(self.root)
        rows = coverage.display_rows(record)
        self.assertTrue(all(1 <= len(r['concern_ids']) <= 4 for r in rows))
        self.assertEqual(sum(len(r['concern_ids']) for r in rows), 435)

    def test_plain_english_contribution_prose(self):
        record, _, _ = coverage.authored(self.root)
        prose = [record['interpretation']]
        for row in record['groups']:
            prose.extend([row['interpretation'], *row['display'].values()])
        for text in prose:
            self.assertNotIn(';', text)
            self.assertNotIn('\u2014', text)
            for term in ('Scope-boundary', 'host-software', 'Credibility-assessment', 'power-assessment'):
                self.assertNotIn(term, text)
        moes = audit.audit_moes(self.root, audit.load(self.root/'traceability/framework-baseline.json')['measures_of_effectiveness'])
        self.assertTrue(moes['MOE-06']['observation_basis'].startswith('Clarity of scope and evidence limits:'))

    def test_removed_native_descendant_edge(self):
        self.replace('sysml/01-concerns.sysml',
                     '    #qualitativeContribution dependency contribution_C_SE_03_3_1_3_2_MOE_02 from C_SE_03_3_1_3_2 to FrameworkNeeds::MOE_02;\n', '')
        with self.assertRaisesRegex(AssertionError, 'Native concern/MOE edge mismatch'):
            coverage.check(self.root)

    def test_changed_causal_hierarchy(self):
        self.replace('sysml/01-concerns.sysml',
                     'dependency causal_C_SE_03_3_1_3_2 from C_SE_03_3_1_3_2 to C_SE_03_3_1_3;',
                     'dependency causal_C_SE_03_3_1_3_2 from C_SE_03_3_1_3_2 to C_SE_03;')
        with self.assertRaisesRegex(AssertionError, 'Missing native causal link'):
            coverage.check(self.root)

    def test_false_new_moe_achievement(self):
        path = self.root/'traceability/framework-baseline.json'; record = audit.load(path)
        record['measures_of_effectiveness'][5]['achieved'] = 'passed'
        path.write_text(__import__('json').dumps(record))
        with self.assertRaisesRegex(AssertionError, 'MOE wording or measured outcome mismatch'):
            coverage.check(self.root)

    def test_report_only_refresh_preserves_body_models_and_stored_checks(self):
        paths = ('needs.tex', 'sysml/01-concerns.sysml', 'sysml/02-needs-context.sysml',
                 'traceability/framework-baseline.json')
        before = {p: (self.root/p).read_bytes() for p in paths}
        original = (self.root/coverage.REPORT_TABLE).read_bytes()
        self.replace(coverage.REPORT_TABLE,
                     r'MOE-04 & \ConcernRef{C-PM-01.1} & Learning to write verifiable requirements.',
                     r'MOE-04 & \ConcernRef{C-PM-01.1} & Damaged display prose.')
        record, _, _ = coverage.authored(self.root)
        coverage.refresh_report_table(self.root, record)
        self.assertEqual(original, (self.root/coverage.REPORT_TABLE).read_bytes())
        self.assertEqual(before, {p: (self.root/p).read_bytes() for p in paths})
        coverage.check(self.root)

    def test_refresh_is_idempotent_after_updating_focused_identities(self):
        # The supplied snapshot may have stale identities. Refresh them once in
        # this temporary fixture, then require stable bytes on the second pass.
        paths = ('apendice.tex', 'needs.tex', 'sysml/01-concerns.sysml',
                 'sysml/02-needs-context.sysml', 'traceability/framework-baseline.json')
        protected = {p: (self.root/p).read_bytes() for p in paths[:-1]}
        baseline = audit.load(self.root/paths[-1])
        coverage.refresh(self.root)
        refreshed = audit.load(self.root/paths[-1])
        self.assertEqual(protected, {p: (self.root/p).read_bytes() for p in paths[:-1]})
        self.assertEqual({k: v for k, v in baseline.items() if k != 'current_source_sha256'},
                         {k: v for k, v in refreshed.items() if k != 'current_source_sha256'})
        self.assertEqual(refreshed['current_source_sha256']['apendice.tex'], audit.sha(self.root/'apendice.tex'))
        before = {p: (self.root/p).read_bytes() for p in paths}
        coverage.refresh(self.root)
        self.assertEqual(before, {p: (self.root/p).read_bytes() for p in paths})
        coverage.check(self.root)


if __name__ == '__main__':
    unittest.main()
