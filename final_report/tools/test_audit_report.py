"""Positive and negative current trace/publication checks. No empirical V&V."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

from audit_report import (PROTECTED, audit, audit_native_figures, current_trace,
                          load, parse_concerns, semantic_audit, solution_sources)

REPORT = Path(__file__).resolve().parents[1]


class NativeFigureAuditTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.diagram = 'fig/view.pdf'
        figure = self.root/self.diagram
        figure.parent.mkdir()
        figure.write_bytes(b'%PDF-1.4\n')
        figure.with_suffix('.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        figure.with_suffix('.png').write_bytes(b'\x89PNG\r\n\x1a\n')
        self.svg_hash = hashlib.sha256(figure.with_suffix('.svg').read_bytes()).hexdigest()
        self.manifest = {
            'visualizer': {'name':'Syside Modeler','native':True},
            'target': {'qualified_name':'Example::view'},
            'artifacts': [
                {'format':'svg','path':'/original/worktree/fig/view.svg',
                 'provenance':{'producer':'Syside Modeler','native':True,'sha256':self.svg_hash}},
                {'format':'png','path':'/original/worktree/fig/view.png',
                 'provenance':{'producer':'Syside Modeler','native':True,
                               'sha256':hashlib.sha256(figure.with_suffix('.png').read_bytes()).hexdigest()}},
                {'format':'pdf','path':'/original/worktree/fig/view.pdf',
                 'provenance':{'producer':'rsvg-convert','source_svg':{
                     'path':'/original/worktree/fig/view.svg','producer':'Syside Modeler','sha256':self.svg_hash}}},
            ],
        }
        self.save()

    def save(self):
        (self.root/self.diagram).with_suffix('.manifest.json').write_text(json.dumps(self.manifest))

    def test_portable_native_figure(self):
        result = audit_native_figures(self.root,[self.diagram])[0]
        self.assertEqual(result['view'],'Example::view')
        self.assertTrue(result['exact_pdf_source_hash_matches'])

    def test_changed_svg(self):
        (self.root/self.diagram).with_suffix('.svg').write_text('<svg/>')
        with self.assertRaisesRegex(AssertionError,'Native SVG hash mismatch'):
            audit_native_figures(self.root,[self.diagram])

    def test_wrong_pdf_source(self):
        self.manifest['artifacts'][2]['provenance']['source_svg']['sha256'] = 'stale'
        self.save()
        with self.assertRaisesRegex(AssertionError,'PDF source hash mismatch'):
            audit_native_figures(self.root,[self.diagram])

    def test_non_native(self):
        self.manifest['visualizer']['native'] = False; self.save()
        with self.assertRaisesRegex(AssertionError,'Non-native figure'):
            audit_native_figures(self.root,[self.diagram])

    def test_non_native_png(self):
        self.manifest['artifacts'][1]['provenance']['producer'] = 'other'; self.save()
        with self.assertRaisesRegex(AssertionError,'Non-native PNG'):
            audit_native_figures(self.root,[self.diagram])

    def add_presentation(self):
        # Synthetic provenance data tests rejection only, not native rendering.
        source = self.root/'sysml/model.sysml'; source.parent.mkdir()
        source.write_text('package Example {}')
        self.manifest['capabilities'] = {'interface':'programmatic-named-view'}
        self.manifest['presentation'] = {
            'native_API':'Syside Modeler 0.10.3 bundled coordinator, scene materializer, layouter and renderer',
            'model_source_sha256':{'sysml/model.sysml':hashlib.sha256(source.read_bytes()).hexdigest()},
            'driver_sha256':'a'*64, 'configuration_sha256':'b'*64,
            'native_generated_graph_sha256':'c'*64,
            'native_generated_nodes':1, 'native_generated_edges':0,
            'no_authored_or_edited_nodes_ports_edges_or_SVG_geometry':True,
            'frame_and_model_content_uncropped':True,
            'semantic_view_descriptor_and_filter_evaluation':'unchanged',
        }
        self.save()

    def test_changed_png(self):
        (self.root/self.diagram).with_suffix('.png').write_bytes(b'changed')
        with self.assertRaisesRegex(AssertionError,'Native PNG hash mismatch'):
            audit_native_figures(self.root,[self.diagram])

    def test_duplicate_artifact(self):
        self.manifest['artifacts'].append(self.manifest['artifacts'][0]); self.save()
        with self.assertRaisesRegex(AssertionError,'Incomplete/duplicate native figure artifacts'):
            audit_native_figures(self.root,[self.diagram])

    def test_current_presentation_sources(self):
        self.add_presentation()
        result = audit_native_figures(self.root,[self.diagram])[0]
        self.assertEqual(result['native_presentation']['native_generated_graph_sha256'],'c'*64)
        (self.root/'sysml/model.sysml').write_text('package Changed {}')
        with self.assertRaisesRegex(AssertionError,'Native presentation model source mismatch'):
            audit_native_figures(self.root,[self.diagram])

    def test_source_derived_geometry_producer(self):
        self.add_presentation()
        self.manifest['presentation']['native_API'] = 'source-derived SVG geometry parser'; self.save()
        with self.assertRaisesRegex(AssertionError,'Unexpected native presentation producer'):
            audit_native_figures(self.root,[self.diagram])

    def test_cropped_or_authored_geometry(self):
        self.add_presentation()
        for field in ('frame_and_model_content_uncropped', 'no_authored_or_edited_nodes_ports_edges_or_SVG_geometry'):
            self.manifest['presentation'][field] = False; self.save()
            with self.assertRaisesRegex(AssertionError,'Altered native model geometry/content'):
                audit_native_figures(self.root,[self.diagram])
            self.manifest['presentation'][field] = True

    def test_missing_graph_digest(self):
        self.add_presentation()
        self.manifest['presentation']['native_generated_graph_sha256'] = ''; self.save()
        with self.assertRaisesRegex(AssertionError,'Missing native producer digest'):
            audit_native_figures(self.root,[self.diagram])

    def test_missing_artifact(self):
        (self.root/self.diagram).with_suffix('.png').unlink()
        with self.assertRaisesRegex(AssertionError,'Missing png artifact'):
            audit_native_figures(self.root,[self.diagram])

    def test_missing_manifest(self):
        (self.root/self.diagram).with_suffix('.manifest.json').unlink()
        with self.assertRaisesRegex(AssertionError,'Missing native figure manifest'):
            audit_native_figures(self.root,[self.diagram])

    def test_duplicate_figure(self):
        with self.assertRaisesRegex(AssertionError,'Duplicate solution figure paths'):
            audit_native_figures(self.root,[self.diagram,self.diagram])


class SourceParsingTests(unittest.TestCase):
    def test_follows_inputs_once_ignoring_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'solucion.tex').write_text('\\input{needs}\n% \\input{missing}\n\\input{requirements}\n')
            (root/'needs.tex').write_text('Mission requirements.')
            (root/'requirements.tex').write_text('\\input{needs.tex}\nSystem requirements.')
            self.assertEqual([p.name for p in solution_sources(root)],['solucion.tex','needs.tex','requirements.tex'])

    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'solucion.tex').write_text('\\input{missing}')
            with self.assertRaisesRegex(AssertionError,'Missing solution source'):
                solution_sources(root)

    def test_concerns_keep_nested_citation_and_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'source.tex'
            path.write_text('\\ConcernRoot{C-SE-01}{text \\citep[Sec.~1]{source};}\n'
                            '\\ConcernCause{C-SE-01.1}{C-EPS-1}\\ConcernAliasLink{C-EPS-01}')
            rows = parse_concerns(path)
            self.assertEqual(rows[0]['text'],'text \\citep[Sec.~1]{source};')
            self.assertEqual(rows[1]['parent'],'C-SE-01')
            self.assertEqual(rows[1]['alias_target'],'C-EPS-01')

    def test_stage_checkers_include_every_current_native_source(self):
        native = {str(p.relative_to(REPORT/'sysml')) for p in (REPORT/'sysml').rglob('*.sysml')}
        for script, key in [('check_scenarios.py','CURRENT_FILES'),
                            ('check_logical_responsibilities.py','FILES'),
                            ('check_physical_allocations.py','FILES')]:
            with self.subTest(checker=script):
                self.assertEqual(set(runpy.run_path(str(REPORT/'sysml'/script))[key]),native)

    def test_current_ids_come_from_the_specification(self):
        mr,fr,ucs,scs,*_ = current_trace(REPORT)
        baseline = load(REPORT/'traceability/framework-baseline.json')
        self.assertEqual(set(mr),{r['id'] for r in baseline['mission_requirements']})
        self.assertEqual(set(fr),{r['id'] for r in baseline['framework_requirements']})
        self.assertEqual(ucs,{r['id'] for r in baseline['use_cases']})
        self.assertEqual(scs,{r['id'] for r in baseline['mission_scenarios']})
        self.assertNotIn('FR-40',fr)


class CurrentAuditMutationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)/'report'
        self.root.mkdir()
        for path in REPORT.glob('*.tex'):
            shutil.copy2(path,self.root/path.name)
        shutil.copy2(REPORT/'literatura.bib',self.root/'literatura.bib')
        shutil.copy2(REPORT/'main.pdf',self.root/'main.pdf')
        for name in ('sysml','traceability','candidates'):
            shutil.copytree(REPORT/name,self.root/name,ignore=shutil.ignore_patterns('__pycache__'))
        # Figures are read-only here. The native provenance tests use isolated data.
        (self.root/'fig').symlink_to(REPORT/'fig',target_is_directory=True)
        self.baseline = load(self.root/'traceability/framework-baseline.json')

    def save(self):
        (self.root/'traceability/framework-baseline.json').write_text(json.dumps(self.baseline))

    def replace(self,path,old,new):
        path = self.root/path; text = path.read_text()
        self.assertEqual(text.count(old),1)
        path.write_text(text.replace(old,new))

    def reject(self,reason):
        with self.assertRaisesRegex(AssertionError,reason):
            audit(self.root)

    def test_current_positive(self):
        result = audit(self.root)
        self.assertTrue(result['valid'])
        self.assertEqual(result['independent_review'],'independent correctness review completed, both major findings closed on rereview')
        self.assertEqual(result['major_findings_closed'],2)
        self.assertEqual(result['final_publication_review'],'completed read-only review, zero material blockers')
        self.assertEqual(result['publication_material_blockers'],0)
        self.assertEqual(len(result['native_figures']),9)
        self.assertEqual(result['publication_figures'],8)
        self.assertEqual(result['planned_verification_cases'],result['framework_requirements'])

    def test_protected_files_and_snapshot_policy(self):
        for name in PROTECTED:
            path = self.root/name; original = path.read_bytes()
            path.write_bytes(original+b'\n')
            self.reject('Protected current source changed: '+name)
            path.write_bytes(original)
        self.baseline['protected_current_sha256']['as-is-domain.tex'] = 'forged'; self.save()
        self.reject('Protected snapshot policy changed')

    def test_removed_concern_occurrence(self):
        self.baseline['concerns'].pop(); self.save()
        self.reject('Concern current-source ID mismatch')

    def test_concern_wording(self):
        self.baseline['concerns'][0]['text'] = 'changed'; self.save()
        self.reject('Concern current wording/hierarchy mismatch')

    def test_forced_concern_to_fr(self):
        self.baseline['concerns'][0]['framework_requirement_ids'] = ['FR-01']; self.save()
        self.reject('Forced every-concern-to-FR mapping')

    def test_parallel_mission_needs(self):
        self.baseline['mission_needs'] = [{'id':'MN-01'}]; self.save()
        self.reject('Obsolete parallel mission ledger')

    def test_requirement_statement(self):
        self.replace('requirements.tex','The framework shall acknowledge each assistance trigger','The framework shall ignore each assistance trigger')
        self.reject('FR wording mismatch')

    def test_requirement_id(self):
        self.replace('requirements.tex','FR-41\\par MR-02, 05 &','FR-43\\par MR-02, 05 &')
        self.reject('FR report/native ID mismatch')

    def test_mr_endpoint(self):
        self.replace('sysml/03-requirements.sysml','derive_MR_02_FR_02 { end #original ::> FrameworkNeeds::MR_02;',
                     'derive_MR_02_FR_02 { end #original ::> FrameworkNeeds::MR_03;')
        self.reject('Derivation identifier/endpoint mismatch')

    def test_missing_all_candidate_trace(self):
        self.baseline['framework_requirements'][0]['physical_allocations'].pop(); self.save()
        self.reject('Incomplete all-candidate trace')

    def test_physical_owner(self):
        path = self.root/'candidates/custom.json'; candidate = load(path)
        candidate['allocations'][0]['primary'] = 'L02'; path.write_text(json.dumps(candidate))
        self.reject('Candidate logical allocation mismatch')

    def test_missing_candidate_allocation(self):
        path = self.root/'candidates/nanospace.json'; candidate = load(path)
        candidate['allocations'].pop(); path.write_text(json.dumps(candidate))
        self.reject('Candidate FR allocation set mismatch')

    def test_false_framework_verification_outcome(self):
        self.baseline['verification_cases'][0].update(status='executed, passed',executed=True,verdict='pass'); self.save()
        self.reject('False verification outcome')

    def test_false_measured_benefit(self):
        self.baseline['measures_of_effectiveness'][0]['achieved'] = '20 percent improvement'; self.save()
        self.reject('False measured/qualified outcome')

    def test_incomplete_current_inspection_source_set(self):
        path = self.root/'inspect.json'
        path.write_text(json.dumps({'files':{'input':[], 'included':[]}}))
        with self.assertRaisesRegex(AssertionError,'Inspection current source set mismatch'):
            audit(self.root,inspect_path=path)

    def test_missing_case_criterion(self):
        self.baseline['verification_cases'][0]['criteria_comparison_basis'] = ''; self.save()
        self.reject('Incomplete/mismatched V procedure')

    def test_wrong_case_subject(self):
        self.replace('sysml/05-verification.sysml',"verification <'V01'> V01 {\n        subject framework : ToBe::FutureFramework;",
                     "verification <'V01'> V01 {\n        subject framework : EPSHardware;")
        self.reject('V case native/ledger ID or subject mismatch')

    def test_native_false_verdict(self):
        self.replace('sysml/05-verification.sysml','observedVerdict : ScalarValues::String = "none";',
                     'observedVerdict : ScalarValues::String = "pass";')
        self.reject('False native verification outcome')

    def test_qualification_gate_owner(self):
        self.baseline['qualification_gate']['owner'] = ''; self.save()
        self.reject('Missing TBR owner/risk/action')

    def test_future_tracecheck_cannot_claim_qualification(self):
        self.baseline['future_tracecheck_policy']['status'] = 'qualified'; self.save()
        self.reject('Future tracecheck qualification must remain pending TBR resolution')

    def test_stale_physical_selection(self):
        self.baseline['physical_direction'] = 'PA-VS, selected winner'; self.save()
        self.reject('Conditional physical direction report/ledger mismatch')

    def test_stale_review_physical_direction(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['physical_direction'] = 'PA-VS, selected winner'; path.write_text(json.dumps(review))
        self.reject('Stale physical direction in review record')

    def test_wrong_review_claim(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['status'] = 'independently approved'; path.write_text(json.dumps(review))
        self.reject('Independent correctness review disposition mismatch')

    def test_empirical_review_approval(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['empirical_approval'] = True; path.write_text(json.dumps(review))
        self.reject('False framework empirical V&V approval')

    def test_major_closure_cannot_be_omitted(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['findings'][1]['status'] = 'open'; path.write_text(json.dumps(review))
        self.reject('Independent major finding closure incomplete')

    def test_wrong_review_scope(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['scope'] = 'implemented framework conformity'; path.write_text(json.dumps(review))
        self.reject('Independent review scope must remain specification correctness')

    def test_publication_review_status(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['final_publication_review'] = 'pending read-only review'; path.write_text(json.dumps(review))
        self.reject('Final publication review disposition mismatch')

    def test_publication_scope_and_evidence(self):
        path = self.root/'traceability/independent-review.json'; original = path.read_text()
        for field,value in [('scope','implemented framework conformity'), ('empirical_approval',True),
                            ('review_record_sha256','a'*64), ('collected_result_sha256','b'*64)]:
            with self.subTest(field=field):
                review = json.loads(original); review['final_publication_review_evidence'][field] = value
                path.write_text(json.dumps(review))
                self.reject('Publication review scope/authority mismatch|Publication review evidence digest mismatch')
        path.write_text(original)

    def test_publication_blocker_cannot_pass(self):
        path = self.root/'traceability/independent-review.json'; review = load(path)
        review['final_publication_review_evidence']['material_blockers'] = 1; path.write_text(json.dumps(review))
        self.reject('Publication review has material blockers')

    def test_reviewed_pdf_identity(self):
        (self.root/'main.pdf').write_bytes(b'changed, unreviewed PDF')
        self.reject('Publication review PDF identity mismatch')

    def test_stale_review_status_in_prose(self):
        self.replace('verification-plan.tex','empirical V\\&V/evaluation remain pending.',
                     'empirical V\\&V/evaluation and independent correctness review remain pending.')
        self.reject('Stale independent correctness review status in report')

    def test_duplicate_published_allocation(self):
        path = self.root/'logical.tex'
        row = next(line for line in path.read_text().splitlines() if line.startswith('L01 &'))
        path.write_text(path.read_text()+'\n'+row+'\n')
        self.reject('Duplicate/missing published allocation row')

    def test_wrong_published_fr_group(self):
        self.replace('logical.tex','& 08, 37 \\\\', '& 02, 37 \\\\')
        self.reject('Published primary FR allocation mismatch')

    def test_wrong_published_physical_component(self):
        self.replace('trade-selection.tex','L01 / CDT-C01 &','L01 / CDT-C02 &')
        self.reject('Published physical component mismatch')

    def test_extra_native_asset_requires_registration(self):
        self.baseline['native_figures'].pop(); self.save()
        self.reject('Current native figure manifest/provenance mismatch')

    def test_scope_wording_hash(self):
        self.replace('physical-candidates.tex','Physical EPS realization, procurement, testing, PIL/HIL and flight readiness remain excluded.',
                     'Physical EPS realization is now included.')
        self.reject('Approved current scope/wording/ID source changed')

    def test_wrong_bibliography(self):
        self.replace('literatura.bib','doi = {10.1007/s12567-023-00509-9}', 'doi = {10.1007/incorrect}')
        self.reject('Approved current scope/wording/ID source changed|Incorrect NASA or Girardello')

    def test_latex_negative_logs(self):
        for text in ('Overfull \\hbox (3pt too wide)', 'LaTeX Warning: There were undefined references.',
                     'LaTeX Warning: Float too large for page', 'Output written on main.pdf (101 pages, 1 bytes).'):
            with self.subTest(log=text):
                path = self.root/'main.log'; path.write_text(text)
                with self.assertRaisesRegex(AssertionError,'LaTeX|exceeds 100 pages'):
                    audit(self.root,log_path=path)


class SemanticMutationTests(unittest.TestCase):
    def setUp(self):
        self.baseline = load(REPORT/'traceability/framework-baseline.json')
        self.fr = {r['id']: dict(r,parents=r['mission_requirement_ids'],scenarios=r['mission_scenario_ids'],functions=r['black_box_function_ids'])
                   for r in self.baseline['framework_requirements']}
        # An isolated minimal inspection tests rejection, never claims native readiness.
        self.inspection = {'valid':True,'exit_code':0,'diagnostics':[],
                           'semantic_model':{'summary':{'elements_truncated':False,'relationships_truncated':False},
                                             'elements':[],'relationships':[]}}

    def reject(self,reason):
        with self.assertRaisesRegex(AssertionError,reason):
            semantic_audit(self.inspection,self.baseline,self.fr,[])

    def test_capped_inspect_rejected(self):
        self.inspection['semantic_model']['summary']['relationships_truncated'] = True
        self.reject('Inspection must be uncapped')

    def test_false_satisfaction_rejected(self):
        self.inspection['semantic_model']['elements'] = [{'id':'fake','kind':'SatisfyRequirementUsage'}]
        self.reject('False satisfaction assertion')

    def test_unresolved_endpoint_rejected(self):
        self.inspection['semantic_model']['relationships'] = [
            {'kind':'ReferenceSubsetting','sources':[{'id':'missing','external':False}],
             'targets':[{'id':'also-missing','external':False}]}]
        self.reject('Incomplete local native endpoint')

    def test_warning_rejected(self):
        self.inspection['diagnostics'] = [{'severity':'warning'}]
        self.reject('Native diagnostics present')


if __name__ == '__main__':
    unittest.main()
