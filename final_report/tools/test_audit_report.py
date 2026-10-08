"""Fresh scaffold and negative tests. Synthetic fixtures never claim native V&V.

Current-source table parsing is exercised. Full release outputs and a positive
integrated audit are deliberately deferred until the final native/prose release.
Every text mutation asserts exactly one matching current selector.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import runpy
import shutil
import tempfile
import unittest

import audit_report as a

REPORT = Path(__file__).resolve().parents[1]
PHYSICAL = runpy.run_path(str(REPORT/'sysml/check_physical_allocations.py'))


class Fixture(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)/'report'; self.root.mkdir()
        for name in ('needs.tex', 'requirements.tex', 'verification-plan.tex', 'logical.tex', 'literatura.bib'):
            shutil.copy2(REPORT/name, self.root/name)
        for name in ('sysml', 'traceability', 'candidates'):
            shutil.copytree(REPORT/name, self.root/name, ignore=shutil.ignore_patterns('__pycache__'))
        self.fr = a.current_trace(self.root)[1]

    def replace(self, path, old, new):
        path = self.root/path; text = path.read_text()
        self.assertNotEqual(old, new)
        self.assertEqual(text.count(old), 1, 'Mutation selector must match one current region')
        path.write_text(text.replace(old, new))

    def update(self, path, change):
        path = self.root/path; record = a.load(path); change(record)
        path.write_text(json.dumps(record))


class SourceParsingTests(Fixture):
    def test_current_concise_requirements(self):
        mr, fr, ucs, scs, *_ = a.current_trace(self.root)
        self.assertEqual(len(mr), 6); self.assertEqual(len(fr), 40)
        self.assertEqual(sum(len(r['parents']) for r in fr.values()), 169)
        self.assertEqual(len(ucs), 5); self.assertEqual(len(scs), 5)
        self.assertTrue(all(r['inputs'] and r['outputs'] and r['methods'] for r in fr.values()))
        self.assertEqual(set(fr), a.ACTIVE_FR)

    def test_changed_statement(self):
        self.replace('requirements.tex', 'The framework shall acknowledge each assistance trigger', 'The framework shall ignore each assistance trigger')
        with self.assertRaisesRegex(AssertionError, 'FR wording mismatch'):
            a.current_trace(self.root)

    def test_removed_fr(self):
        self.replace('requirements.tex', 'FR-41 & The framework shall acknowledge', 'FR-43 & The framework shall acknowledge')
        with self.assertRaisesRegex(AssertionError, 'active ID mismatch'):
            a.current_trace(self.root)

    def test_missing_io(self):
        self.replace('requirements.tex', '\\textit{Inputs:} Assistance trigger', '\\textit{Incoming:} Assistance trigger')
        with self.assertRaisesRegex(AssertionError, 'Missing FR statement/IO'):
            a.report_requirements(self.root)

    def test_parent_endpoint(self):
        self.replace('sysml/03-requirements.sysml', 'derive_MR_02_FR_02 { end #original ::> FrameworkNeeds::MR_02;', 'derive_MR_02_FR_02 { end #original ::> FrameworkNeeds::MR_03;')
        with self.assertRaisesRegex(AssertionError, 'Derivation identifier/endpoint mismatch'):
            a.current_trace(self.root)

    def test_parent_range(self):
        self.replace('requirements.tex', 'Recorded disposition, rationale and revision links. & 01--06', 'Recorded disposition, rationale and revision links. & 01--05')
        with self.assertRaisesRegex(AssertionError, 'MR/FR derivation mismatch'):
            a.current_trace(self.root)

    def test_duplicate_gate(self):
        self.replace('needs.tex', 'obtain SRR acceptance during Phase A', 'obtain MCR acceptance during Phase A')
        self.replace('sysml/02-needs-context.sysml', 'doc /* The enterprise shall obtain SRR acceptance during Phase A', 'doc /* The enterprise shall obtain MCR acceptance during Phase A')
        with self.assertRaisesRegex(AssertionError, 'MR gate uniqueness mismatch'):
            a.current_trace(self.root)

    def test_duplicate_parent_edge(self):
        path = self.root/'sysml/03-requirements.sysml'
        edge = next(line for line in path.read_text().splitlines() if 'connection derive_MR_02_FR_02 ' in line)
        path.write_text(path.read_text() + '\n' + edge)
        with self.assertRaisesRegex(AssertionError, '169 unique'):
            a.current_trace(self.root)

    def test_wrong_uc_parent(self):
        self.replace('sysml/02-needs-context.sysml', 'refine_UC01_MR01 from UC01 to MR_01;', 'refine_UC01_MR01 from UC01 to MR_02;')
        with self.assertRaisesRegex(AssertionError, 'Scenario/UC MR disagreement'):
            a.current_trace(self.root)

    def test_comments_escaped_ampersands_and_nested_braces(self):
        cells = a.table_cells(r'A & V\&V \citep[Sec.~1]{source} & ')
        self.assertEqual(cells, ['A', r'V\&V \citep[Sec.~1]{source}', ''])
        self.assertEqual(a.visible('value \\%\n% hidden\n'), 'value \\%\n\n')

    def test_concern_anchor_and_alias(self):
        path = self.root/'example.tex'
        path.write_text('% comment\n\\ConcernRoot{C-SE-01}{text \\citep[Sec.~1]{source};}\n'
                        '\\ConcernCause{C-SE-01.1}{alias}\\ConcernAliasLink{C-EPS-01}')
        rows = a.parse_concerns(path)
        self.assertEqual(rows[0]['source_line'], 2)
        self.assertEqual(rows[0]['text'], 'text \\citep[Sec.~1]{source};')
        self.assertEqual(rows[1]['parent'], 'C-SE-01')
        self.assertEqual(rows[1]['alias_target'], 'C-EPS-01')

    def test_native_strings_with_tex_braces(self):
        text = r'@SourceRecord about C_SE_01 { sourceText = "a \\citep{source}"; sourceLocator = "appendix"; }'
        self.assertEqual(a.annotations(text, 'SourceRecord', r'C_\w+')['C_SE_01']['sourceLocator'], 'appendix')

    def test_invalid_number_range(self):
        with self.assertRaisesRegex(AssertionError, 'Invalid MR- range'):
            a.bare_numbers('06--01', 'MR-')

    def test_stage_sources_are_complete(self):
        native = {str(p.relative_to(REPORT/'sysml')) for p in (REPORT/'sysml').rglob('*.sysml')}
        for script, key in [('check_scenarios.py', 'CURRENT_FILES'), ('check_logical_responsibilities.py', 'FILES'), ('check_physical_allocations.py', 'FILES')]:
            with self.subTest(checker=script):
                self.assertEqual(set(runpy.run_path(str(REPORT/'sysml'/script))[key]), native)

    def test_current_scenario_ids(self):
        data = runpy.run_path(str(REPORT/'sysml/check_scenarios.py'))
        self.assertEqual(data['FR_IDS'], {r.replace('-', '_') for r in a.ACTIVE_FR})
        sc = a.current_trace(self.root)[5]
        self.assertEqual(data['SC_MRS'], {int(s[-2:]): {int(m[-2:]) for m in ms} for s, ms in sc.items()})


class MOPTests(Fixture):
    def reject(self, reason):
        with self.assertRaisesRegex(AssertionError, reason):
            a.audit_mops(self.root, self.fr)

    def test_current_positive(self):
        rows = a.audit_mops(self.root, self.fr)
        self.assertEqual(len(rows), 40)
        self.assertTrue(all(r['target'] == r['target_source'] == '' and r['achieved'] == 'unknown' for r in rows.values()))

    def test_nonempty_target(self):
        self.replace('requirements.tex', 'Method and model eligibility precision and recall, with rationale correctness (fractions). &', 'Method and model eligibility precision and recall, with rationale correctness (fractions). & 100\\%')
        self.reject('literally empty')

    def test_empty_tex_group_is_not_literal_empty(self):
        self.replace('requirements.tex', 'Method and model eligibility precision and recall, with rationale correctness (fractions). &', 'Method and model eligibility precision and recall, with rationale correctness (fractions). & {}')
        self.reject('literally empty')

    def test_mop_identity(self):
        self.replace('requirements.tex', 'FR-02\\newline MOP-FR02', 'FR-02\\newline MOP-FR03')
        self.reject('MOP/FR identity mismatch')

    def test_native_target_default(self):
        self.replace('sysml/03-requirements.sysml', 'attribute target : ScalarValues::String = "";', 'attribute target : ScalarValues::String = "100%";')
        self.reject('False native target/achieved default')

    def test_native_mop_result_override(self):
        self.replace('sysml/03-requirements.sysml', "item <'MOP-FR03'> MOP_FR03 : PerformanceMeasure {", "item <'MOP-FR03'> MOP_FR03 : PerformanceMeasure {\n        attribute :>> achieved = \"passed\";")
        self.reject('False native MOP result/target')

    def test_mop_fr_dependency(self):
        self.replace('sysml/03-requirements.sysml', 'MOPFR03_FR03 from MOP_FR03 to FR_03;', 'MOPFR03_FR03 from MOP_FR03 to FR_02;')
        self.reject('MOP/FR dependency mismatch')

    def test_stale_ledger_measure(self):
        records = list(a.audit_mops(self.root, self.fr).values()); records[0]['id'] = 'MOP-01'
        with self.assertRaisesRegex(AssertionError, 'MOP ledger coverage mismatch'):
            a.audit_mops(self.root, self.fr, records)

    def test_achieved_ledger_measure(self):
        records = list(a.audit_mops(self.root, self.fr).values()); records[0]['achieved'] = '99%'
        with self.assertRaisesRegex(AssertionError, 'MOP ledger mismatch'):
            a.audit_mops(self.root, self.fr, records)


class CandidateTests(Fixture):
    def check(self):
        return a.audit_candidate_records(self.root, self.fr)

    def reject(self, reason):
        with self.assertRaisesRegex(AssertionError, reason):
            self.check()

    def test_design_data_positive(self):
        trade, records = self.check()
        self.assertEqual(len(trade['alternatives']), 30)
        self.assertEqual([len(c['components']) for c in records.values()], [6] * 5)
        self.assertEqual([len(c['allocations']) for c in records.values()], [40] * 5)
        self.assertIn('L05.EC1', a.expected_alternatives())
        self.assertIn('L06.EC1', a.expected_alternatives())

    def test_missing_candidate(self):
        (self.root/'candidates/comet.json').unlink(); self.reject('Candidate source set mismatch')

    def test_missing_component(self):
        self.update('candidates/custom.json', lambda c: c['components'].pop()); self.reject('Six physical')

    def test_wrong_owner(self):
        self.update('candidates/custom.json', lambda c: c['allocations'][0].update(primary='L02')); self.reject('Candidate logical allocation mismatch')

    def test_missing_fr(self):
        self.update('candidates/nanospace.json', lambda c: c['allocations'].pop()); self.reject('Candidate FR allocation set mismatch')

    def test_duplicate_fr(self):
        self.update('candidates/nanospace.json', lambda c: c['allocations'].append(copy.deepcopy(c['allocations'][0]))); self.reject('Duplicate candidate allocation')

    def test_wrong_composition(self):
        self.update('candidates/valispace.json', lambda c: c['components'][1].update(composition='EP2')); self.reject('Candidate composition mismatch')

    def test_unscoped_alternative(self):
        self.update('candidates/custom.json', lambda c: c['components'][4].update(alternative_ids=['EC2'])); self.reject('Unscoped/wrong alternative identity')

    def test_missing_alternative(self):
        self.update('traceability/trade-study.json', lambda c: c['alternatives'].pop()); self.reject('five scoped alternatives')

    def test_wrong_source(self):
        self.update('traceability/trade-study.json', lambda c: c['alternatives'][0].update(citation='handpicked-0001')); self.reject('Alternative scope/source mismatch')

    def test_false_candidate_result(self):
        self.update('candidates/custom.json', lambda c: c.update(numerical_results={'score': 1})); self.reject('Invented candidate outcome')

    def test_missing_fprime(self):
        self.update('candidates/comet.json', lambda c: c['required_integrations'].pop('f_prime')); self.reject('Missing mandatory integration')

    def test_optional_omniverse(self):
        self.update('candidates/git-yaml.json', lambda c: c['required_integrations']['omniverse'].update(required=False)); self.reject('Common integration scope mismatch')

    def test_scene_only(self):
        self.update('candidates/custom.json', lambda c: c['required_integrations']['omniverse'].update(scope='scene visualization')); self.reject('Scene-only')

    def test_missing_jev_role(self):
        self.update('candidates/custom.json', lambda c: c['custom_roles'].pop('jev_recommendations')); self.reject('Missing substantive custom responsibility')

    def test_incomplete_parametric_role(self):
        self.update('candidates/custom.json', lambda c: c['custom_roles']['native_parametrics'].update(outputs=[])); self.reject('Incomplete custom role')

    def test_preferred_field(self):
        self.update('traceability/trade-study.json', lambda c: c.update(decision={'preferred': 'PA-CDT'})); self.reject('winner/priority/selected')

    def test_historical_preference_is_not_current_authority(self):
        _, c = self.check(); self.assertIn('historical_evidence', c['PA-CDT'])
        a.assert_neutral({'historical_evidence': {'preferred': 'PA-CDT'}, 'status': 'proposed'})

    def test_unresolved_native_cannot_pass(self):
        self.update('candidates/comet.json', lambda r: r['reconciliation'].update(status='deliberately incomplete test fixture'))
        logical = {'allocations': [{'FR': rid} for rid in self.fr]}
        with self.assertRaisesRegex(AssertionError, 'native contract not reconciled'):
            a.audit_candidate_records(self.root, self.fr, logical, require_native=True)


class CandidateAPIBridgeTests(Fixture):
    def reject(self, reason):
        with self.assertRaisesRegex(AssertionError, reason):
            a.audit_candidate_records(self.root, self.fr)

    def test_all_candidate_logical_pointers_are_real_exports(self):
        _, candidates = a.audit_candidate_records(self.root, self.fr)
        for record in candidates.values():
            self.assertFalse(record['empirical_vv_executed'])
            if record['reconciliation']['status'] != 'reconciled with final native contract':
                self.assertIsNone(record['native_contract'])
                logical = a.unique(a.load(self.root/'traceability/logical-architecture.json')['allocations'], 'logical allocation', 'FR') if record['logical_api'].get('final_logical_ledger') else None
                self.assertTrue(all(r['operation'] is None and (r['support'] == logical[r['FR']]['support'] and r['interfaces'] == logical[r['FR']]['interfaces'] if logical else r['support'] is None and r['interfaces'] is None) for r in record['allocations']))
            else:
                self.assertEqual(record['native_contract']['status'], 'reconciled with final native contract')
                self.assertTrue(all(isinstance(r['operation'], str) and isinstance(r['support'], list) and isinstance(r['interfaces'], list) for r in record['allocations']))
            self.assertTrue(all(r['logical_operation'] != r['logical_contract'] and r['logical_scenario_calls'] for r in record['allocations']))

    def test_stale_candidate_api_provenance(self):
        self.update('candidates/custom.json', lambda r: r['logical_api']['publication_sha256'].update({'export-manifest.json': '0' * 64}))
        self.reject('published API pointer mismatch')

    def test_wrong_candidate_logical_component(self):
        self.update('candidates/comet.json', lambda r: r['components'][0].update(logical_type='FrameworkLogical::MissionDesign'))
        self.reject('published component pointer mismatch')

    def test_contract_is_not_an_engineering_operation(self):
        self.update('candidates/git-yaml.json', lambda r: r['allocations'][0].update(logical_operation=r['allocations'][0]['logical_contract']))
        self.reject('published FR operation/IO pointer mismatch')

    def test_missing_candidate_performed_call(self):
        self.update('candidates/nanospace.json', lambda r: r['allocations'][0].update(logical_scenario_calls=[]))
        self.reject('published scenario call mismatch')

    def test_wrong_platform_logical_route(self):
        self.update('candidates/valispace.json', lambda r: r['required_integrations']['omniverse'].update(logical_elements=[]))
        self.reject('required platform logical pointer mismatch')


class TradeTests(Fixture):
    def setUp(self):
        super().setUp(); self.trade = a.load(self.root/'traceability/trade-study.json')
        rows = [r"\textbf{MOP} & " + ' & '.join(r'\textbf{' + cid + '}' for cid in a.CANDIDATES) + r' \\']
        rows += [r['id'] + ' & ' + ' & '.join(r['mechanisms'].values()) + r' \\' for r in self.trade['critical_mop_comparison']]
        self.text = '\n'.join(rows) + '\nAchieved values are unknown.\n'

    def mutate_text(self, old, new):
        self.assertNotEqual(old, new)
        self.assertEqual(self.text.count(old), 1, 'Current trade mutation must match exactly once')
        return self.text.replace(old, new)

    def test_actual_six_by_five_matrix(self):
        self.assertEqual(tuple(a.audit_trade_matrix(self.text, self.trade)), a.CRITICAL_MOPS)

    def test_generic_candidate_table_not_comparison(self):
        with self.assertRaisesRegex(AssertionError, 'candidate columns'):
            a.audit_trade_matrix('PA-CDT & Native Python basis \\\\', self.trade)

    def test_procedure_table_not_comparison(self):
        text = self.mutate_text(' & ' + self.trade['critical_mop_comparison'][0]['mechanisms']['PA-COM'], '')
        with self.assertRaisesRegex(AssertionError, 'five-candidate matrix'):
            a.audit_trade_matrix(text, self.trade)

    def test_missing_structural_cell(self):
        text = self.mutate_text(self.trade['critical_mop_comparison'][0]['mechanisms']['PA-COM'], 'unknown')
        with self.assertRaisesRegex(AssertionError, 'Missing structural comparison cell'):
            a.audit_trade_matrix(text, self.trade)

    def test_wrong_critical_subset(self):
        with self.assertRaisesRegex(AssertionError, 'Exact six critical MOP'):
            a.audit_trade_matrix(self.mutate_text('MOP-FR30', 'MOP-FR41'), self.trade)

    def test_false_ranking(self):
        text = self.mutate_text(self.trade['critical_mop_comparison'][0]['mechanisms']['PA-COM'], 'Best candidate, passed')
        with self.assertRaisesRegex(AssertionError, 'Unmeasured ranking/result'):
            a.audit_trade_matrix(text, self.trade)

    def test_ledger_mismatch(self):
        self.trade['critical_mop_comparison'][0]['mechanisms']['PA-CDT'] = 'other'
        with self.assertRaisesRegex(AssertionError, 'Trade mechanism/result mismatch'):
            a.audit_trade_matrix(self.text, self.trade)

    def test_supplied_current_prose_tables(self):
        a.audit_physical_tables((REPORT/'physical-candidates.tex').read_text(), self.trade)
        a.audit_trade_matrix((REPORT/'trade-selection.tex').read_text(), self.trade)

    def test_physical_approved_tables(self):
        # Isolated approved table fixture. No current report integration claim.
        lines = []
        for lid in a.GROUPS:
            lines.append(r'\multicolumn{3}{l}{\textbf{' + lid + ' responsibility}}\\')
            for row in self.trade['alternatives']:
                if row['logical'] == lid:
                    lines.append(row['id'].split('.')[1] + ' & ' + row['supported_subset'] + ' & ' + row['required_additions'] + r' \\')
        lines += [cid + ' & ' + ' & '.join(a.COMPOSITION[cid]) + r' \\' for cid in a.CANDIDATES]
        a.audit_physical_tables('\n'.join(lines), self.trade)


class HistoricalReviewTests(Fixture):
    def test_positive_historical_only(self):
        result = a.audit_historical_reviews(self.root)
        self.assertFalse(result['independent-review']['current_review_performed'])
        self.assertEqual(result['source-review']['role'], 'HISTORICAL')

    def test_current_approval_rejected(self):
        self.update('traceability/independent-review.json', lambda r: r.update(current_revision_review_performed=True))
        with self.assertRaisesRegex(AssertionError, 'False renewed/empirical'):
            a.audit_historical_reviews(self.root)

    def test_historical_role_rejected_if_current(self):
        self.update('traceability/source-review.json', lambda r: r.update(status='current reviewed'))
        with self.assertRaisesRegex(AssertionError, 'presented as current'):
            a.audit_historical_reviews(self.root)

    def test_original_hashes_cannot_be_refreshed(self):
        self.update('traceability/independent-review.json', lambda r: r['historical_evidence']['current_source_sha256'].update({'needs.tex': 'a' * 64}))
        with self.assertRaisesRegex(AssertionError, 'Historical review evidence altered'):
            a.audit_historical_reviews(self.root)

    def test_new_pdf_does_not_renew_old_review(self):
        (self.root/'main.pdf').write_bytes(b'new unreviewed publication')
        self.assertFalse(a.audit_historical_reviews(self.root)['independent-review']['current_review_performed'])

    def test_bounded_assertion_rejects_wrong_quote(self):
        source = self.root/'source.md'; source.write_text('original evidence\n')
        assertion = {'id': 'example', 'source': str(source), 'sha256': a.sha(source), 'lines': [1, 1], 'quote': 'invented evidence', 'supported_subset': 'a bounded role', 'limits': 'no framework outcome'}
        self.update('traceability/source-review.json', lambda r: r.update(current_assertions=[assertion]))
        with self.assertRaisesRegex(AssertionError, 'quotation/locator mismatch'):
            a.audit_historical_reviews(self.root)

    def test_bounded_assertion_rejects_whole_file(self):
        source = self.root/'source.md'; source.write_text('original evidence\n' * 150)
        assertion = {'id': 'example', 'source': str(source), 'sha256': a.sha(source), 'lines': [1, 150], 'quote': 'original evidence', 'supported_subset': 'a bounded role', 'limits': 'no framework outcome'}
        self.update('traceability/source-review.json', lambda r: r.update(current_assertions=[assertion]))
        with self.assertRaisesRegex(AssertionError, 'Unbounded source excerpt'):
            a.audit_historical_reviews(self.root)


class LogicalContractTests(Fixture):
    def setUp(self):
        super().setUp()
        self.logical = {'components': [{'id': lid} for lid in a.GROUPS], 'allocations': [
            {'FR': rid, 'primary': a.OWNERS[rid], 'support': [], 'operation': 'NewLogical::operation',
             'verification': {'status': 'planned, not executed'}} for rid in self.fr]}
        self.contract = {'status': 'reconciled with final native contract', 'component_unions': [],
                         'crosswalk': [{'source_FR': 'FR-01', 'source_field': 'Retained requirement records',
                                        'target_FR': 'FR-14', 'target_field': 'requirements',
                                        'source_component': 'L01', 'target_component': 'L02',
                                        'source_feature': 'Synthetic::retained', 'target_feature': 'Synthetic::requirements',
                                        'native_flow': 'Synthetic::flow', 'mapping_basis': 'Requirement records supply common requirements.'}]}
        for lid, numbers in a.GROUPS.items():
            ids = sorted(f'FR-{n:02}' for n in numbers)
            union = {'id': lid, 'FR': ids, 'native_features': {}}
            for direction in ('inputs', 'outputs'):
                union[direction] = {rid: self.fr[rid][direction] for rid in ids}
                union['native_features'][direction] = {rid: ['Synthetic::' + rid + '::' + direction] for rid in ids}
            self.contract['component_unions'].append(union)

    def check(self):
        return a.audit_logical_contract(self.root, self.fr, self.logical, self.contract)

    def test_complete_union_schema_without_old_api(self):
        # Synthetic descriptor validates the checker, never actual native exports.
        self.assertEqual(len(self.check()), 40)

    def test_missing_union(self):
        self.contract['component_unions'].pop()
        with self.assertRaisesRegex(AssertionError, 'Missing logical input/output union'):
            self.check()

    def test_missing_failure_output(self):
        self.contract['component_unions'][0]['outputs']['FR-02'] = 'Findings only'
        with self.assertRaisesRegex(AssertionError, 'Incomplete logical outputs union'):
            self.check()

    def test_unresolved_union_field(self):
        self.contract['component_unions'][0]['native_features']['inputs']['FR-02'] = []
        with self.assertRaisesRegex(AssertionError, 'Unresolved native IO union field'):
            self.check()

    def test_crosswalk_outside_fr_io(self):
        self.contract['crosswalk'][0]['source_field'] = 'Invented financial estimate'
        with self.assertRaisesRegex(AssertionError, 'outside declared FR IO'):
            self.check()

    def test_wrong_crosswalk_owner(self):
        self.contract['crosswalk'][0]['target_component'] = 'L03'
        with self.assertRaisesRegex(AssertionError, 'Wrong crosswalk owner'):
            self.check()

    def test_empty_crosswalk(self):
        self.contract['crosswalk'] = []
        with self.assertRaisesRegex(AssertionError, 'Empty logical exchange crosswalk'):
            self.check()

    def test_duplicate_crosswalk(self):
        self.contract['crosswalk'].append(copy.deepcopy(self.contract['crosswalk'][0]))
        with self.assertRaisesRegex(AssertionError, 'Duplicate logical field crosswalk'):
            self.check()

    def test_native_binding_identity_required(self):
        self.contract['crosswalk'][0]['native_flow'] = None
        with self.assertRaisesRegex(AssertionError, 'Unresolved logical field binding'):
            self.check()

    def table(self):
        return '\n'.join(lid + ' responsibility & ' + ', '.join(f'{n:02}' for n in sorted(ns)) + r' & Inputs to outputs \\' for lid, ns in a.GROUPS.items())

    def test_concise_published_union_table(self):
        self.assertEqual(set(a.audit_logical_table(self.table())), set(a.GROUPS))

    def test_wrong_published_union(self):
        with self.assertRaisesRegex(AssertionError, 'Published primary FR allocation mismatch'):
            a.audit_logical_table(self.table().replace('13, 14, 15', '12, 14, 15'))

    def test_duplicate_published_logical_row(self):
        with self.assertRaisesRegex(AssertionError, 'Duplicate/missing published logical allocation row'):
            a.audit_logical_table(self.table() + '\n' + self.table().splitlines()[0])


class PublishedAPITests(Fixture):
    """Actual published descriptors, with fresh meaningful mutation selectors.

    These check the importer/auditor. They do not assert current native validity.
    """
    def setUp(self):
        super().setUp()
        self.contract = a.load(self.root/'traceability/framework-baseline.json')['logical_io_contract']

    def select(self, records, value, key='id'):
        matches = [r for r in records if r[key] == value]
        self.assertEqual(len(matches), 1, 'Actual API mutation must select one current record')
        return matches[0]

    def change(self, row, key, value):
        self.assertIn(key, row)
        self.assertNotEqual(row[key], value, 'Actual API mutation cannot be a no-op')
        row[key] = value

    def check(self):
        return a.audit_published_logical_api(self.root, self.fr, self.contract)

    def reject(self, reason):
        with self.assertRaisesRegex(AssertionError, reason):
            self.check()

    def requirement(self, rid):
        return self.select(self.contract['requirements'], rid)

    def projection(self):
        return self.select(self.contract['crosswalk'], 'FrameworkLogical::LogicalFramework::requirementsAllocations_001', 'projection_operation')

    def test_actual_published_scope(self):
        rows = self.check()
        self.assertEqual(len(rows), 40)
        self.assertEqual(sum(len(fs) for r in rows.values() for fs in r['field_contracts'].values()), 249)
        self.assertEqual(len(self.contract['exchanges']), 20)
        self.assertEqual(len(self.contract['crosswalk']), 203)
        self.assertEqual(len(self.contract['scenario_members']), 142)
        self.assertIn(self.contract['status'], (a.BRIDGED_API_STATUS, 'reconciled with final native contract'))

    def test_actual_operation_io_and_projection_distinctions(self):
        r = self.requirement('FR-18')
        self.assertEqual(r['operation'], 'FrameworkLogical::SimulationIntegration::planAnalysis')
        self.assertEqual(r['model_path'], 'FrameworkLogical::SimulationIntegration::contractFR18')
        row = self.projection()
        self.assertNotEqual(row['source_type'], row['target_type'])
        self.assertNotEqual(row['native_source_flow'], row['native_target_flow'])
        self.check()

    def test_publication_hash_required(self):
        row = self.contract['publication_sha256']
        self.change(row, 'export-manifest.json', 'unverified')
        self.reject('published API provenance')

    def test_missing_actual_fr(self):
        self.select(self.contract['requirements'], 'FR-42')
        self.contract['requirements'].remove(self.requirement('FR-42'))
        self.reject('six-L/40-FR coverage mismatch')

    def test_retired_fr_is_not_an_alias(self):
        self.change(self.requirement('FR-41'), 'id', 'FR-12')
        self.reject('six-L/40-FR coverage mismatch')

    def test_stale_actual_statement(self):
        self.change(self.requirement('FR-18'), 'statement', 'Scene display supplies numerical coupling.')
        self.reject('wording/parent/owner mismatch')

    def test_wrong_actual_operation_owner(self):
        self.change(self.requirement('FR-18'), 'operation', 'FrameworkLogical::MissionDesign::defineDesign')
        self.reject('engineering operation owner mismatch')

    def test_wrong_actual_engineering_signature(self):
        self.change(self.requirement('FR-36')['operation_signature'][0], 'multiplicity', '0..1')
        self.reject('engineering operation signature mismatch')

    def test_io_action_not_substituted_for_operation(self):
        r = self.requirement('FR-18')
        self.change(r, 'operation', r['model_path'])
        self.reject('engineering operation owner mismatch')

    def test_wrong_actual_contract_signature(self):
        self.change(self.requirement('FR-18')['contract_signature'][0], 'type', 'BoundaryViews::AnalysisPlan')
        self.reject('IO action signature mismatch')

    def test_missing_actual_typed_field(self):
        row = self.requirement('FR-18')['field_contracts']['outputs']
        field = self.select(row, 'transfer limitations', 'exact_field')
        row.remove(field)
        self.reject('typed IO fields')

    def test_wrong_actual_field_direction(self):
        field = self.select(self.requirement('FR-18')['field_contracts']['inputs'], 'returned tool responses', 'exact_field')
        self.change(field, 'direction', 'out')
        self.reject('type/direction/multiplicity mismatch')

    def test_wrong_actual_field_multiplicity(self):
        field = self.select(self.requirement('FR-18')['field_contracts']['outputs'], 'mapping findings', 'exact_field')
        self.change(field, 'multiplicity', '1')
        self.reject('type/direction/multiplicity mismatch')

    def test_wrong_actual_port_field(self):
        field = self.select(self.requirement('FR-18')['field_contracts']['outputs'], 'execution status', 'exact_field')
        self.change(field, 'port_path', field['path'])
        self.reject('field/port identity mismatch')

    def test_actual_union_cannot_drop_failure_output(self):
        row = self.select(self.contract['component_unions'], 'L03')['outputs']
        self.change(row, 'FR-18', 'EPS results only')
        self.reject('Incomplete logical outputs union')

    def test_actual_projection_requires_exact_field_not_substring(self):
        self.change(self.projection(), 'source_field', 'Retained requirement record')
        self.reject('outside declared FR IO')

    def test_actual_projection_type_conversion_is_explicit(self):
        row = self.projection()
        self.change(row, 'target_type', row['source_type'])
        self.reject('typed declaration mismatch')

    def test_actual_projection_context_is_not_a_declaration(self):
        row = self.projection()
        self.change(row, 'source_path', row['source_feature'])
        self.reject('contextual feature chain mismatch')

    def test_actual_projection_is_not_a_direct_flow(self):
        row = self.projection()
        self.change(row, 'native_source_flow', row['projection_operation'])
        self.reject('Unresolved logical field binding')

    def test_actual_projection_signature_is_typed(self):
        self.change(self.projection()['projection_signature'][1], 'type', 'BoundaryViews::RequirementRecord')
        self.reject('Projection operation signature mismatch')

    def test_actual_projection_cannot_be_omitted(self):
        self.contract['crosswalk'].remove(self.projection())
        self.reject('mapping coverage mismatch')

    def test_actual_scenario_must_perform_an_operation(self):
        row = self.select(self.contract['scenario_members'], 'LogicalRealization::SoftwareRealization::coordinate', 'path')
        self.change(row, 'kind', 'ActionUsage')
        self.reject('actual performed call')

    def test_actual_scenario_owner_is_not_metadata_only(self):
        row = self.select(self.contract['scenario_members'], 'LogicalRealization::AssistanceRealization::receive', 'path')
        self.change(row, 'owner', 'FrameworkLogical::LogicalFramework::L01')
        self.reject('scenario operation owner/type mismatch')

    def test_actual_scenario_parameter_signature(self):
        row = self.select(self.contract['scenario_members'], 'LogicalRealization::SoftwareRealization::coordinate', 'path')
        parameter = self.select(row['parameters'], 'authorization', 'name')
        self.change(parameter, 'multiplicity', '0..1')
        self.reject('scenario parameter signature mismatch')

    def test_actual_external_scenario_has_no_framework_operation(self):
        row = self.select(self.contract['scenario_members'], 'LogicalRealization::DesignRealization::execute', 'path')
        self.assertNotIn('operation', row)
        row['operation'] = 'FrameworkLogical::SimulationIntegration::planAnalysis'
        self.reject('External scenario call')

    def test_actual_platform_direction_is_required(self):
        row = self.select(self.contract['external_aggregates'], 'wholeCUBICSScenarios', 'name')
        self.change(row, 'direction', 'out')
        self.reject('platform direction/type mismatch')

    def test_actual_platform_result_type_is_required(self):
        row = self.select(self.contract['external_aggregates'], 'fPrimeResults', 'name')
        self.change(row, 'type', 'BoundaryViews::HostSoftwareProduct')
        self.reject('platform direction/type mismatch')

    def test_actual_guidance_state_owner(self):
        self.change(self.contract['states'], 'guidance', 'FrameworkLogical::RequirementsAssistance::assistanceCurrency')
        self.reject('authority/currency state owner mismatch')

    def test_current_source_hash_cannot_be_forged(self):
        self.change(self.contract['source_sha256'], 'sysml/04-logical.sysml', '0' * 64)
        with self.assertRaisesRegex(AssertionError, 'source identity mismatch'):
            a.audit_published_logical_api(self.root, self.fr, self.contract, require_sources=True)


class FinalLogicalLedgerTests(Fixture):
    def setUp(self):
        super().setUp()
        self.logical = a.load(self.root/'traceability/logical-architecture.json')
        self.contract = a.load(self.root/'traceability/framework-baseline.json')['logical_io_contract']

    def row(self, records, identifier, key='FR'):
        matches = [r for r in records if r[key] == identifier]
        self.assertEqual(len(matches), 1, 'Final ledger mutation must select one actual record')
        return matches[0]

    def change(self, row, key, value):
        self.assertIn(key, row)
        self.assertNotEqual(row[key], value, 'Final ledger mutation cannot be a no-op')
        row[key] = value

    def check(self):
        return a.audit_final_logical_ledger(self.root, self.fr, self.logical, self.contract)

    def reject(self, reason):
        with self.assertRaisesRegex(AssertionError, reason):
            self.check()

    def test_final_logical_ledger_descriptor(self):
        self.assertEqual(len(self.check()), 40)

    def test_source_union_and_typed_partition_are_distinct(self):
        r = self.row(self.logical['allocations'], 'FR-01')
        self.assertEqual(r['inputs'], [r['inputs_verbatim']])
        self.assertEqual(len(r['native_io']['inputs']), 2)
        self.assertTrue(all(u['native_feature'] is None for u in self.logical['components'][0]['io_union']['inputs']))
        self.check()

    def test_source_aggregate_cannot_be_inferred_from_typed_partition(self):
        r = self.row(self.logical['allocations'], 'FR-01')
        self.change(r, 'inputs', r['native_io']['inputs'])
        self.reject('source IO union mismatch')

    def test_actual_native_subject_provenance(self):
        r = self.row(self.logical['allocations'], 'FR-18')
        f = self.row(r['native_io']['field_contracts']['outputs'], 'transfer limitations', 'exact_field')
        self.change(f['subject_metadata'], 'fr', 'FR-16')
        self.reject('typed field provenance mismatch')

    def test_source_union_provenance(self):
        c = self.row(self.logical['components'], 'L01', 'id')
        u = self.row(c['io_union']['inputs'], 'Requirement submissions and source/parent revisions.', 'field')
        self.change(u, 'provenance', ['FR-02'])
        self.reject('source union provenance mismatch')

    def test_actual_typed_union_coverage(self):
        c = self.row(self.logical['components'], 'L01', 'id')
        self.change(c['typed_io_union']['inputs'], 'Requirement submissions', [])
        self.reject('typed union mismatch')

    def test_actual_final_engineering_operation(self):
        r = self.row(self.logical['allocations'], 'FR-03')
        self.change(r, 'operation', 'FrameworkLogical::RequirementsAssistance::checkDraft')
        self.reject('operation/owner mismatch')

    def test_actual_final_mop(self):
        r = self.row(self.logical['allocations'], 'FR-03')
        self.change(r, 'MOP', 'MOP-FR02')
        self.reject('MOP mismatch')

    def test_no_invented_default_interface(self):
        r = self.row(self.logical['allocations'], 'FR-01')
        self.change(r, 'interfaces', ['IF01'])
        self.reject('interface allocation mismatch')

    def test_actual_projection_flow_payload(self):
        e = self.row(self.logical['exchanges'], 'requirementsAllocations', 'name')
        m = self.row(e['mappings'], 'FrameworkLogical::LogicalFramework::requirementsAllocations_001', 'operation_path')
        self.change(m['target_flow'], 'payload', 'BoundaryViews::RequirementRecord')
        self.reject('projection route mismatch')

    def test_actual_external_aggregate_direction(self):
        r = self.row(self.logical['external_exchanges'], 'wholeCUBICSScenarios', 'name')
        self.change(r, 'direction', 'out')
        self.reject('external aggregate mismatch')

    def test_actual_final_scenario_performer(self):
        r = self.row(self.logical['safety_contract']['tasks'], 'LogicalRealization::AssistanceRealization::receive', 'native')
        self.change(r, 'component', 'FrameworkLogical::LogicalFramework::L01')
        self.reject('performed task allocation mismatch')


class PlannedEvidenceTests(Fixture):
    def setUp(self):
        super().setUp(); self.baseline = a.load(self.root/'traceability/framework-baseline.json')

    def check(self):
        return a.audit_cases(self.root, self.baseline, self.fr)

    def test_current_planned_procedures(self):
        self.assertEqual(len(self.check()), 40)

    def test_false_executed_case(self):
        self.baseline['verification_cases'][0].update(status='executed, passed', executed=True, verdict='pass')
        with self.assertRaisesRegex(AssertionError, 'False verification outcome'):
            self.check()

    def test_false_native_verdict(self):
        self.replace('sysml/05-verification.sysml', 'observedVerdict : ScalarValues::String = "none";', 'observedVerdict : ScalarValues::String = "pass";')
        with self.assertRaisesRegex(AssertionError, 'False native verification outcome'):
            self.check()

    def test_empty_case_criterion(self):
        self.baseline['verification_cases'][0]['criteria_comparison_basis'] = ''
        with self.assertRaisesRegex(AssertionError, 'Incomplete/mismatched V procedure'):
            self.check()

    def test_qualification_owner(self):
        self.baseline['qualification_gate']['owner'] = ''
        with self.assertRaisesRegex(AssertionError, 'Missing qualification owner/risk/action'):
            self.check()

    def test_false_future_qualification(self):
        self.baseline['future_tracecheck_policy']['status'] = 'qualified'
        with self.assertRaisesRegex(AssertionError, 'False future qualification'):
            self.check()

    def test_current_moe_wording(self):
        self.assertEqual(len(a.audit_moes(self.root, self.baseline['measures_of_effectiveness'])), 4)

    def test_financial_moe_cannot_remain_current(self):
        self.baseline['measures_of_effectiveness'][3]['observation_basis'] = 'Financial cost in CAD'
        with self.assertRaisesRegex(AssertionError, 'MOE wording or measured outcome mismatch'):
            a.audit_moes(self.root, self.baseline['measures_of_effectiveness'])

    def test_false_moe_value(self):
        self.baseline['measures_of_effectiveness'][0]['achieved'] = '20% improvement'
        with self.assertRaisesRegex(AssertionError, 'MOE wording or measured outcome mismatch'):
            a.audit_moes(self.root, self.baseline['measures_of_effectiveness'])


class FigureTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        self.root = Path(directory.name); self.figure = self.root/'fig/view.pdf'; self.figure.parent.mkdir()
        self.figure.write_bytes(b'%PDF-1.4\n')
        self.figure.with_suffix('.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Illustration</text></svg>')
        self.record = {'native_syside_render': False, 'executed_simulation': False,
                       'artifact_sha256': {fmt: a.sha(self.figure.with_suffix('.' + fmt)) for fmt in ('svg', 'pdf')},
                       'svg_sha256_used_for_pdf': a.sha(self.figure.with_suffix('.svg'))}
        self.save()

    def save(self):
        self.figure.with_suffix('.provenance.json').write_text(json.dumps(self.record))

    def check(self):
        return a.audit_figures(self.root, ['fig/view.pdf'])

    def test_authored_svg_is_allowed(self):
        self.assertEqual(self.check()[0]['kind'], 'authored illustration')

    def test_authored_figure_cannot_claim_native(self):
        self.record['native_syside_render'] = True; self.save()
        with self.assertRaisesRegex(AssertionError, 'falsely claims native'):
            self.check()

    def test_changed_svg(self):
        self.figure.with_suffix('.svg').write_text('<svg/>')
        with self.assertRaisesRegex(AssertionError, 'svg hash mismatch'):
            self.check()

    def test_changed_pdf(self):
        self.figure.write_bytes(b'changed PDF')
        with self.assertRaisesRegex(AssertionError, 'pdf hash mismatch'):
            self.check()

    def test_wrong_svg_source(self):
        self.record['svg_sha256_used_for_pdf'] = 'stale'; self.save()
        with self.assertRaisesRegex(AssertionError, 'PDF source hash mismatch'):
            self.check()

    def test_missing_provenance(self):
        self.figure.with_suffix('.provenance.json').unlink()
        with self.assertRaisesRegex(AssertionError, 'Missing figure provenance'):
            self.check()

    def test_duplicate_include(self):
        with self.assertRaisesRegex(AssertionError, 'Duplicate solution figure'):
            a.audit_figures(self.root, ['fig/view.pdf', 'fig/view.pdf'])

    def test_unrelated_native_model_edit_is_not_figure_forgery(self):
        model = self.root/'sysml/model.sysml'; model.parent.mkdir(); model.write_text('package Example {}')
        self.check(); model.write_text('package Changed {}'); self.check()

    def test_current_illustrations_have_honest_provenance(self):
        figures = a.audit_figures(REPORT, ['fig/framework-context.pdf', 'fig/logical-architecture.pdf'])
        self.assertTrue(all(f['kind'] == 'authored illustration' for f in figures))


class FailClosedTests(Fixture):
    def test_incomplete_release_cannot_generate_valid_result(self):
        self.update('traceability/framework-baseline.json', lambda r: r['reconciliation'].update(status='awaiting final native contract'))
        with self.assertRaisesRegex(AssertionError, 'Integrated release reconciliation incomplete'):
            a.audit(self.root)

    def test_incomplete_logical_io_contract(self):
        logical = {'components': [{'id': lid} for lid in a.GROUPS], 'allocations': [
            {'FR': rid, 'primary': a.OWNERS[rid], 'support': [], 'operation': 'NewLogical::operation', 'verification': {'status': 'planned, not executed'}} for rid in self.fr]}
        with self.assertRaisesRegex(AssertionError, 'IO/crosswalk contract not reconciled'):
            a.audit_logical_contract(self.root, self.fr, logical, None)

    def test_capped_inspection(self):
        inspection = {'valid': True, 'exit_code': 0, 'diagnostics': [], 'semantic_model': {
            'summary': {'elements_truncated': False, 'relationships_truncated': True}}}
        with self.assertRaisesRegex(AssertionError, 'Inspection must be uncapped'):
            a.semantic_audit(inspection, {}, {}, [])

    def test_native_warning(self):
        inspection = {'valid': True, 'exit_code': 0, 'diagnostics': [{'severity': 'warning'}]}
        with self.assertRaisesRegex(AssertionError, 'Native diagnostics present'):
            a.semantic_audit(inspection, {}, {}, [])

    def test_false_satisfaction(self):
        inspection = {'valid': True, 'exit_code': 0, 'diagnostics': [], 'semantic_model': {
            'summary': {'elements_truncated': False, 'relationships_truncated': False},
            'elements': [{'id': 'fake', 'kind': 'SatisfyRequirementUsage'}], 'relationships': []}}
        with self.assertRaisesRegex(AssertionError, 'False satisfaction assertion'):
            a.semantic_audit(inspection, {}, {}, [])

    def test_incomplete_native_endpoint(self):
        inspection = {'valid': True, 'exit_code': 0, 'diagnostics': [], 'semantic_model': {
            'summary': {'elements_truncated': False, 'relationships_truncated': False}, 'elements': [],
            'relationships': [{'kind': 'Dependency', 'sources': [{'id': 'missing', 'external': False}], 'targets': []}]}}
        with self.assertRaisesRegex(AssertionError, 'Incomplete local native endpoint'):
            a.semantic_audit(inspection, {}, {}, [])

    def test_missing_mutation_selector_is_not_a_pass(self):
        path = self.root/'mutation.sysml'; path.write_text('current source')
        with self.assertRaisesRegex(ValueError, 'matches=0'):
            PHYSICAL['mutate_once'](path, 'stale selector', 'unsafe', 'stale')
        self.assertEqual(path.read_text(), 'current source')

    def test_duplicate_mutation_selector_is_not_a_pass(self):
        path = self.root/'mutation.sysml'; path.write_text('guard guard')
        with self.assertRaisesRegex(ValueError, 'matches=2'):
            PHYSICAL['mutate_once'](path, 'guard', 'unsafe', 'duplicate')

    def test_noop_mutation_is_not_a_pass(self):
        path = self.root/'mutation.sysml'; path.write_text('guard')
        with self.assertRaisesRegex(ValueError, 'must change exactly one'):
            PHYSICAL['mutate_once'](path, 'guard', 'guard', 'noop')

    def test_real_mutation_changes_one_region(self):
        path = self.root/'mutation.sysml'; path.write_text('guard')
        self.assertEqual(PHYSICAL['mutate_once'](path, 'guard', 'unsafe', 'changed'), 1)
        self.assertEqual(path.read_text(), 'unsafe')

    def test_native_contract_fail_closed(self):
        # Deliberately incomplete fixture, independent of the release phase.
        self.update('candidates/comet.json', lambda r: r['reconciliation'].update(status='deliberately incomplete test fixture'))
        shutil.copytree(REPORT/'tools', self.root/'tools', ignore=shutil.ignore_patterns('__pycache__'))
        with self.assertRaisesRegex(ValueError, 'native contract not reconciled'):
            PHYSICAL['current_records'](self.root/'sysml')


class ReleasedPhysicalRecordTests(Fixture):
    def check(self):
        return a.audit_candidate_records(self.root, self.fr, a.load(self.root/'traceability/logical-architecture.json'), require_native=True)

    def reject(self, reason):
        with self.assertRaisesRegex(AssertionError, reason):
            self.check()

    def test_released_physical_descriptors(self):
        _, records = self.check()
        for record in records.values():
            native = record['native_contract']
            self.assertEqual(len(native['framework_calls']), 118)
            self.assertEqual(len(native['procedure_performers']), 24)
            self.assertEqual(len(native['comparison_mechanisms']), 6)
            self.assertTrue(all(row['operation'] for row in record['allocations']))
            self.assertFalse(record['empirical_vv_executed'])

    def test_missing_real_native_mechanism(self):
        self.update('candidates/custom.json', lambda r: r['native_contract']['comparison_mechanisms'].pop())
        self.reject('Native structural MOP comparison mismatch')

    def test_unmeasured_native_mechanism(self):
        self.update('candidates/comet.json', lambda r: r['native_contract']['comparison_mechanisms'][0].update(achieved='100%'))
        self.reject('Native structural MOP comparison mismatch')

    def test_wrong_native_citation(self):
        self.update('candidates/valispace.json', lambda r: r['native_contract']['component_specifications'][0]['source'].update(citationRecord='invented-source'))
        self.reject('Native component citation does not resolve')

    def test_missing_real_actor_mapping(self):
        self.update('candidates/nanospace.json', lambda r: r['native_contract']['procedure_performers'].pop())
        self.reject('performed/actor mapping')

    def test_false_native_source_status(self):
        self.update('candidates/git-yaml.json', lambda r: r['native_contract']['component_specifications'][0]['source'].update(status='qualified'))
        self.reject('identity/source scope mismatch')

    def test_scenario_negatives_require_a_passing_baseline(self):
        checker = runpy.run_path(str(REPORT/'sysml/check_scenarios.py'))
        with self.assertRaisesRegex(ValueError, 'passing current scenario baseline'):
            checker['negative_checks'](None, None, None, None, None)

    def test_real_physical_mutation_families(self):
        _, records = self.check()
        cases = records['PA-CDT']['native_contract']['negative_mutations']
        self.assertTrue(PHYSICAL['NEGATIVE_INVARIANTS'] <= {r['invariant'] for r in cases})
        for case in cases:
            self.assertNotEqual(case['old'], case['new'])
            text = (REPORT/'sysml'/case['file']).read_text()
            if case.get('scope_start'):
                self.assertEqual(text.count(case['scope_start']), 1)
                start = text.index(case['scope_start'])
                end = text.index(case['scope_end'], start + len(case['scope_start'])) if case.get('scope_end') else len(text)
                text = text[start:end]
            self.assertEqual(text.count(case['old']), 1)


class PublicationTests(unittest.TestCase):
    def glossary(self):
        ids = ('MBSE OOSEM SysML EPS RAM SIL MOE MOP MR FR MIL CDR SIR '
               'CSRM FMI USD COTS HTN KiBaM RMSE').split()
        return '\n'.join('\\syma{' + name + '}{definition}' for name in ids)

    def test_current_required_glossary_schema(self):
        self.assertEqual(len(a.audit_glossary(self.glossary())), 20)

    def test_missing_used_glossary_entry(self):
        text = self.glossary(); self.assertEqual(text.count('\\syma{HTN}{definition}'), 1)
        with self.assertRaisesRegex(AssertionError, 'Missing current glossary acronyms'):
            a.audit_glossary(text.replace('\\syma{HTN}{definition}', ''))

    def test_duplicate_glossary_entry(self):
        with self.assertRaisesRegex(AssertionError, 'Duplicate glossary acronym'):
            a.audit_glossary(self.glossary() + '\n\\syma{HTN}{definition}')

    def test_86_pages(self):
        self.assertEqual(a.audit_latex_log('Output written on main.pdf (86 pages, 123 bytes).'), 86)

    def test_87_pages(self):
        with self.assertRaisesRegex(AssertionError, '86 page release target'):
            a.audit_latex_log('Output written on main.pdf (87 pages, 123 bytes).')

    def test_bad_latex_logs(self):
        for text in ('Overfull \\hbox (3pt too wide)', 'LaTeX Warning: There were undefined references.',
                     'LaTeX Warning: Float too large for page', '! Fatal error'):
            with self.subTest(log=text), self.assertRaisesRegex(AssertionError, 'LaTeX unresolved'):
                a.audit_latex_log(text)

    def test_missing_final_log(self):
        with self.assertRaisesRegex(AssertionError, 'No final PDF page count'):
            a.audit_latex_log('LaTeX started')

    def test_follow_inputs_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'solucion.tex').write_text('\\input{needs}\n% \\input{missing}\n\\input{requirements}\n')
            (root/'needs.tex').write_text('Mission requirements.')
            (root/'requirements.tex').write_text('\\input{needs.tex}\nSystem requirements.')
            self.assertEqual([p.name for p in a.solution_sources(root)], ['solucion.tex', 'needs.tex', 'requirements.tex'])

    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'solucion.tex').write_text('\\input{missing}')
            with self.assertRaisesRegex(AssertionError, 'Missing solution source'):
                a.solution_sources(root)


if __name__ == '__main__':
    unittest.main()
