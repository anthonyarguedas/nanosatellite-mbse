#!/usr/bin/env python3
"""Check current report/native trace and publication records, not empirical V&V."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

# Initial current worktree snapshots supplied with the approved brief.
# These protect the user's as-is changes independently of editable trace records.
PROTECTED = {
    'as-is-domain.tex': '237ec05344d4eb560628b1e136b95abd3cfcd7bad7ffcc4102232406667ebdf2',
    'intro.tex': 'cce42b5c9fda5a13e51a6c9d648f47163215a2e029ac1f71b57128f74318d149',
    'objectives.tex': '579570a217b9b523e8f066ac481742cdeba76c25f87be86ebf6692a1b8f235e1',
    'titlepage.tex': 'ba7d53b2f8571b26f2832ddc146f2099820a73c33967ca0450e005a9968fbf09',
}
PUBLICATION_REVIEW_STATUS = 'completed read-only review, zero material blockers'
# Metadata pins from the actual closed review and collected reviewer result.
PUBLICATION_REVIEW_EVIDENCE = {
    'review_record_sha256': '214a406d5a735e3875f988b087df2c41652c52671cb4876b56252cea259496ab',
    'collected_result_sha256': '8e2610db4e1727286a20e0fea12963f753ca7bcd3f3694738568699f94911b37',
    'report_pdf_sha256': '943c1f2311bb1391835cc13614d12c2347b43fd04560a480bba48d3d105ce2c4',
}
PROCEDURE_FIELDS = ('subject', 'configuration', 'prerequisites', 'procedure',
                    'stimulus_conditions', 'expected_response',
                    'criteria_comparison_basis', 'retained_evidence')


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique(records, label):
    result = {record['id']: record for record in records}
    assert len(result) == len(records), f'Duplicate {label} IDs'
    return result


def visible(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def group(text, start):
    """Read a balanced TeX brace group without losing nested citations."""
    assert text[start] == '{', 'Expected brace group'
    depth = 0
    for end in range(start, len(text)):
        if text[end] in '{}' and (end == 0 or text[end - 1] != '\\'):
            depth += 1 if text[end] == '{' else -1
            if depth == 0:
                return text[start + 1:end], end + 1
    raise AssertionError('Unclosed TeX group')


def parse_concerns(path):
    text = Path(path).read_text()
    records = []
    for match in re.finditer(r'\\Concern(Root|Cause)\{([^}]+)\}', text):
        statement, end = group(text, match.end())
        cid = match[2]
        alias = re.match(r'\\ConcernAliasLink\{([^}]+)\}', text[end:])
        records.append({'id': cid, 'kind': match[1].lower(), 'text': statement,
                        'parent': cid.rsplit('.', 1)[0] if '.' in cid else None,
                        'alias_target': alias[1] if alias else None,
                        'source_line': text.count('\n', 0, match.start()) + 1})
    unique(records, 'protected concern occurrence')
    return records


def number_set(text, prefix):
    result = set()
    for match in re.finditer(rf'\b{re.escape(prefix)}(\d{{2}})(?:--(?:{re.escape(prefix)})?(\d{{2}}))?', text):
        first = int(match[1]); last = int(match[2] or match[1])
        assert last >= first, f'Invalid {prefix} range: {match[0]}'
        result.update(f'{prefix}{n:02}' for n in range(first, last + 1))
    return result


def native_statements(text, prefix):
    pattern = rf"requirement <'({prefix}-\d+)'> \w+ \{{\s*subject[^;]+;\s*doc /\* (.*?) \*/"
    rows = [{'id': m[1], 'text': m[2]} for m in re.finditer(pattern, text, re.DOTALL)]
    return unique(rows, f'native {prefix}')


def report_requirements(root):
    mr = unique([{'id': m[1], 'text': m[2]} for m in re.finditer(
        r'^(MR-\d{2}) & (.*?) \\\\$', (root/'needs.tex').read_text(), re.MULTILINE)], 'report MR')
    fr = unique([{'id': m[1], 'text': m[3], 'parents': ['MR-' + n for n in re.findall(r'\d{2}', m[2])],
                 'methods': m[4].split(',')} for m in re.finditer(
        r'^(FR-\d{2})\\par MR-([\d, ]+) & (.*?) & ([IADT,]+)\\par',
        (root/'requirements.tex').read_text(), re.MULTILINE)], 'report FR')
    assert mr and fr, 'No report requirement rows found'
    return mr, fr


def current_trace(root):
    """Extract current specification records. Semantic checks remain Syside's job."""
    mr, fr = report_requirements(root)
    nt = (root/'sysml/03-requirements.sysml').read_text()
    nm = native_statements((root/'sysml/02-needs-context.sysml').read_text(), 'MR')
    nf = native_statements(nt, 'FR')
    assert mr == nm, 'MR report/native statement or ID mismatch'
    assert set(fr) == set(nf), 'FR report/native ID mismatch'
    derivations = defaultdict(set); scenarios = defaultdict(set); functions = defaultdict(set)
    for m in re.finditer(r'connection derive_MR_(\d+)_FR_(\d+) \{ end #original ::> FrameworkNeeds::MR_(\d+); end #derive ::> FR_(\d+);', nt):
        assert (m[1], m[2]) == (m[3], m[4]), f'Derivation identifier/endpoint mismatch: {m[0]}'
        derivations['FR-'+m[2]].add('MR-'+m[3])
    for m in re.finditer(r'dependency scenario_FR\d+_SC\d+ from FR_(\d+) to ScenarioViews::(SC\d+);', nt):
        scenarios['FR-'+m[1]].add(m[2])
    for m in re.finditer(r'dependency function_FR\d+_F\d+ from FR_(\d+) to BoundaryViews::(F\d+);', nt):
        functions['FR-'+m[1]].add(m[2])
    for rid, row in fr.items():
        assert row['text'] == nf[rid]['text'], f'FR wording mismatch: {rid}'
        assert set(row['parents']) == derivations[rid], f'MR/FR derivation mismatch: {rid}'
        assert derivations[rid] and derivations[rid] <= set(mr), f'Missing/unknown MR parent: {rid}'
        assert scenarios[rid] and functions[rid], f'Missing FR scenario/function endpoints: {rid}'
        row['scenarios'] = sorted(scenarios[rid]); row['functions'] = sorted(functions[rid])
    needs = (root/'sysml/02-needs-context.sysml').read_text()
    sc = (root/'sysml/09-scenarios.sysml').read_text()
    ucs = set(re.findall(r"use case <'(UC\d+)'>", needs))
    scs = set(re.findall(r"action def <'(SC\d+)'>", sc))
    uc_mrs = defaultdict(set); sc_mrs = defaultdict(set); sc_ucs = defaultdict(set)
    for u, m in re.findall(r'dependency refine_UC\d+_MR\d+ from (UC\d+) to MR_(\d+);', needs):
        uc_mrs[u].add('MR-'+m)
    for s, m in re.findall(r'dependency scenario_SC\d+_MR\d+ from (SC\d+) to FrameworkNeeds::MR_(\d+);', sc):
        sc_mrs[s].add('MR-'+m)
    for s, u in re.findall(r'dependency scenario_UC\d+ from (SC\d+) to FrameworkNeeds::(UC\d+);', sc):
        sc_ucs[s].add(u)
    assert ucs == set(uc_mrs) and scs == set(sc_mrs) == set(sc_ucs), 'UC/SC endpoint set mismatch'
    assert ucs == number_set(visible((root/'needs.tex').read_text()), 'UC'), 'UC report/native ID mismatch'
    assert scs == number_set(visible((root/'requirements.tex').read_text()), 'SC'), 'SC report/native ID mismatch'
    for s in scs:
        assert len(sc_ucs[s]) == 1 and sc_ucs[s] <= ucs, f'Missing/unknown UC: {s}'
        assert sc_mrs[s] == uc_mrs[next(iter(sc_ucs[s]))], f'Scenario/UC MR disagreement: {s}'
    assert set().union(*uc_mrs.values()) == set(mr), 'MR without a use case'
    for rid, row in fr.items():
        assert set(row['scenarios']) <= scs, f'Unknown scenario: {rid}'
        assert set(row['parents']) <= set().union(*(sc_mrs[s] for s in row['scenarios'])), f'No MR/SC/FR path: {rid}'
    return mr, fr, ucs, scs, uc_mrs, sc_mrs, sc_ucs


def solution_sources(root):
    result = []; pending = [root/'solucion.tex']
    while pending:
        path = pending.pop()
        if path in result:
            continue
        assert path.is_file(), f'Missing solution source: {path}'
        result.append(path)
        pending.extend(root/Path(n).with_suffix('.tex') for n in reversed(
            re.findall(r'\\(?:input|include)\s*\{([^}]+)\}', visible(path.read_text()))))
    return result


def audit_allocation_tables(root, logical, preferred):
    """Check the two complete published allocations without a duplicate trace listing."""
    expected = defaultdict(set)
    for row in logical['allocations']:
        expected[row['primary']].add(row['FR'])
    for name, physical in [('logical.tex', False), ('trade-selection.tex', True)]:
        pattern = r'^(L\d{2})(?: / ([A-Z]+-C\d{2}))? & .*? & ([\d, -]+) \\\\$'
        rows = list(re.finditer(pattern, visible((root/name).read_text()), re.MULTILINE))
        assert len(rows) == len(expected) and {r[1] for r in rows} == set(expected), f'Duplicate/missing published allocation row: {name}'
        components = {r['logical']: r['id'] for r in preferred['components']}
        for row in rows:
            ids = number_set(re.sub(r'(\d{2})', r'FR-\1', row[3]), 'FR-')
            assert ids == expected[row[1]], f'Published primary FR allocation mismatch: {name} {row[1]}'
            assert row[2] == (components[row[1]] if physical else None), f'Published physical component mismatch: {name} {row[1]}'


def audit_independent_review(root, baseline):
    review = load(root/'traceability/independent-review.json')
    status = 'independent correctness review completed, both major findings closed on rereview'
    assert review['status'] == baseline['independent_review'] == status and review['independent_review_performed'] is True, 'Independent correctness review disposition mismatch'
    assert review['scope'] == 'proposed report/native specification correctness, no empirical approval', 'Independent review scope must remain specification correctness'
    assert review['empirical_framework_vv_executed'] is False and review['empirical_approval'] is False, 'False framework empirical V&V approval'
    findings = unique(review['findings'], 'independent finding')
    assert set(findings) == {'1', '2'} and review['original_major_findings'] == 2, 'Original independent findings must remain recorded'
    for row in findings.values():
        assert row['severity'] == 'major' and row['original_status'] == 'open' and row['status'] == 'closed on rereview' and row['resolution'] and row['rereview_evidence'], 'Independent major finding closure incomplete'
    assert re.fullmatch(r'[0-9a-f]{64}', review['review_record_sha256']), 'Missing independent review record digest'
    assert review['prose_review']['performed'] is True and review['prose_review']['bounded_passes_applied'] == [1, 2, 3], 'Prose review/pass record incomplete'
    assert review['final_publication_review'] == PUBLICATION_REVIEW_STATUS, 'Final publication review disposition mismatch'
    publication = review['final_publication_review_evidence']
    assert publication['performed'] is True and publication['scope'] == 'publication of the proposed EPS framework specification, no empirical approval' and publication['empirical_approval'] is False, 'Publication review scope/authority mismatch'
    assert publication['material_blockers'] == 0, 'Publication review has material blockers'
    assert all(publication[k] == v for k,v in PUBLICATION_REVIEW_EVIDENCE.items()) and review['prose_review']['review_record_sha256'] == publication['review_record_sha256'], 'Publication review evidence digest mismatch'
    assert publication['report_pdf_sha256'] == sha(root/'main.pdf'), 'Publication review PDF identity mismatch'
    counts = review['current_specification_counts']
    fields = {'concern_occurrences':'concerns', 'MR':'mission_requirements', 'UC':'use_cases',
              'SC':'mission_scenarios', 'FR':'framework_requirements', 'LA':'logical_components',
              'PA':'candidate_ids', 'V':'verification_cases', 'MOE':'measures_of_effectiveness',
              'MOP':'measures_of_performance'}
    functions = set().union(*(set(r['black_box_function_ids']) for r in baseline['framework_requirements']))
    assert all(counts[k] == len(baseline[v]) for k, v in fields.items()) and counts['root_concerns'] == sum(c['kind'] == 'root' for c in baseline['concerns']) and counts['F'] == len(functions), 'Independent review current-count mismatch'
    assert review['current_source_sha256'] == baseline['approved_source_sha256'], 'Independent review integration source snapshot mismatch'
    pending = visible((root/'verification-plan.tex').read_text())
    assert not re.search(r'independent correctness review[^.]*remain pending', pending), 'Stale independent correctness review status in report'
    return review


def audit_native_figures(root, diagrams):
    assert len(diagrams) == len(set(diagrams)), 'Duplicate solution figure paths'
    result = []
    for diagram in diagrams:
        figure = root/diagram
        assert figure.is_file(), f'Missing figure: {diagram}'
        manifest_path = figure.with_suffix('.manifest.json')
        assert manifest_path.is_file(), f'Missing native figure manifest: {diagram}'
        manifest = load(manifest_path)
        assert manifest['visualizer']['name'] == 'Syside Modeler' and manifest['visualizer']['native'], f'Non-native figure: {diagram}'
        artifacts = {a['format']: a for a in manifest['artifacts']}
        assert {'svg', 'png', 'pdf'} == set(artifacts) and len(manifest['artifacts']) == 3, f'Incomplete/duplicate native figure artifacts: {diagram}'
        for fmt, artifact in artifacts.items():
            path = figure.with_suffix('.'+fmt)
            assert Path(artifact['path']).name == path.name, f'Figure artifact name mismatch: {diagram}'
            assert path.is_file(), f'Missing {fmt} artifact: {diagram}'
        svg = figure.with_suffix('.svg'); svg_hash = sha(svg)
        provenance = artifacts['svg']['provenance']
        assert provenance['producer'] == 'Syside Modeler' and provenance['native'], f'Non-native SVG: {diagram}'
        assert svg_hash == provenance['sha256'], f'Native SVG hash mismatch: {diagram}'
        png = artifacts['png'].get('provenance', {})
        assert png.get('producer') == 'Syside Modeler' and png.get('native'), f'Non-native PNG: {diagram}'
        assert png.get('sha256') == sha(figure.with_suffix('.png')), f'Native PNG hash mismatch: {diagram}'
        presentation = manifest.get('presentation')
        assert '/lifecycle/' not in diagram or presentation is not None, f'Missing native presentation provenance: {diagram}'
        if presentation is not None:
            assert manifest['capabilities']['interface'] == 'programmatic-named-view' and presentation['native_API'] == 'Syside Modeler 0.10.3 bundled coordinator, scene materializer, layouter and renderer', f'Unexpected native presentation producer: {diagram}'
            assert presentation['no_authored_or_edited_nodes_ports_edges_or_SVG_geometry'] is True and presentation['frame_and_model_content_uncropped'] is True and presentation['semantic_view_descriptor_and_filter_evaluation'] == 'unchanged', f'Altered native model geometry/content: {diagram}'
            sources = presentation['model_source_sha256']
            current = {str(p.relative_to(root)): sha(p) for p in (root/'sysml').rglob('*.sysml')}
            assert sources == current, f'Native presentation model source mismatch: {diagram}'
            for field in ('driver_sha256', 'configuration_sha256', 'native_generated_graph_sha256'):
                assert re.fullmatch(r'[0-9a-f]{64}', presentation[field]), f'Missing native producer digest: {diagram}'
            assert presentation['native_generated_nodes'] > 0 and presentation['native_generated_edges'] >= 0, f'Missing native generated graph: {diagram}'
        pdf = artifacts['pdf']['provenance']; source = pdf['source_svg']
        assert pdf['producer'] == 'rsvg-convert', f'Unexpected PDF producer: {diagram}'
        assert source['producer'] == 'Syside Modeler', f'Non-native PDF source: {diagram}'
        assert Path(source['path']).name == svg.name and source['sha256'] == svg_hash, f'PDF source hash mismatch: {diagram}'
        result.append({'figure': diagram, 'view': manifest['target']['qualified_name'],
                       'manifest': str(manifest_path.relative_to(root)), 'native_svg_sha256': svg_hash,
                       'artifact_sha256': {fmt: sha(figure.with_suffix('.'+fmt)) for fmt in artifacts},
                       'exact_pdf_source_hash_matches': True,
                       **({'native_presentation': {k:presentation[k] for k in ('native_API', 'driver_sha256', 'configuration_sha256', 'native_generated_graph_sha256', 'native_generated_nodes', 'native_generated_edges')}} if presentation is not None else {})})
    return result


def audit_cases(root, baseline, fr):
    cases = unique(baseline['verification_cases'], 'verification case')
    text = (root/'sysml/05-verification.sysml').read_text()
    targets = dict(re.findall(r"verification <'(V\d+)'> \w+ \{\s*subject framework : ToBe::FutureFramework;\s*objective \{ verify FrameworkRequirements::FR_(\d+);", text))
    assert set(cases) == set(targets), 'V case native/ledger ID or subject mismatch'
    assert {'FR-'+n for n in targets.values()} == set(fr) and len(targets) == len(fr), 'V/FR coverage mismatch'
    annotations = dict(re.findall(r'@PlannedProcedure about (V\d+) \{(.*?)\n    \}', text, re.DOTALL))
    defaults = dict(re.findall(r'attribute (status|executed|observedVerdict) : ScalarValues::\w+ = ([^;]+);', text))
    assert defaults == {'status': '"planned, not executed"', 'executed': 'false', 'observedVerdict': '"none"'}, 'False native verification outcome'
    for vid, case in cases.items():
        rid = case['framework_requirement_id']
        assert rid == 'FR-'+targets[vid], f'Wrong V target: {vid}'
        assert case['status'] == 'planned, not executed' and case['executed'] is False and case['verdict'] is None, f'False verification outcome: {vid}'
        attrs = {k: json.loads(v) for k, v in re.findall(r'(\w+) = ("(?:[^"\\]|\\.)*");', annotations[vid])}
        for field in PROCEDURE_FIELDS:
            native_field = 'subjectDescription' if field == 'subject' else field
            assert case[field].strip() and attrs.get(native_field) == case[field], f'Incomplete/mismatched V procedure {vid}: {field}'
        assert attrs.get('methods') == ','.join(case['methods']) == ','.join(fr[rid]['methods']), f'V method mismatch: {vid}'
        assert set(attrs) == (set(PROCEDURE_FIELDS) - {'subject'}) | {'subjectDescription', 'methods'}, f'Unexpected V outcome override: {vid}'
        assert 'TBR' in case['prerequisites'] and 'before execution' in case['prerequisites'], f'Missing qualification gate: {vid}'
        assert not re.search(r'\b(?:technician|equipment|HIL|PIL|test bench|target processor)\b', ' '.join(case[f] for f in PROCEDURE_FIELDS), re.I), f'Excluded V activity: {vid}'
    gate = baseline['qualification_gate']
    assert gate['status'] == 'TBR, performance qualification blocked' and gate['owner'] == 'Systems Engineer' and gate['risk_basis'] and gate['action'], 'Missing TBR owner/risk/action'
    for field, native_name in [('owner','owner'), ('status','status'), ('risk_basis','riskBasis'), ('action','resolutionAction')]:
        declaration = ':>> status' if native_name == 'status' else native_name + ' : ScalarValues::String'
        assert f'{declaration} = {json.dumps(gate[field], ensure_ascii=False)};' in text, f'TBR gate native mismatch: {field}'
    policy = baseline['future_tracecheck_policy']
    assert policy['status'] == 'planned, numerical TBR resolution required before qualification' and policy['gate_native'] == 'FrameworkVerification::qualificationGate', 'Future tracecheck qualification must remain pending TBR resolution'
    assert (policy['owner'], policy['risk_basis'], policy['action']) == (gate['owner'], gate['risk_basis'], gate['action']), 'Future tracecheck owner/risk/action mismatch'
    groups = number_set(visible((root/'verification-plan.tex').read_text()), 'V')
    assert groups == set(cases), f'Report V coverage mismatch: {sorted(groups ^ set(cases))}'
    for name in ('frameworkValidation', 'epsPhaseProductVerification', 'epsPhaseProductValidation', 'modelCredibilityProtocol', 'researchEvaluation'):
        assert f'item {name} :' in text, f'Missing assessment subject: {name}'
    return cases


def semantic_audit(inspection, baseline, fr, native_figures):
    assert inspection['valid'] and inspection['exit_code'] == 0, 'Native inspection failed'
    assert not [d for d in inspection['diagnostics'] if d.get('severity') in ('error','warning')], 'Native diagnostics present'
    model = inspection['semantic_model']; summary = model['summary']
    assert not summary['elements_truncated'] and not summary['relationships_truncated'], 'Inspection must be uncapped'
    elements = model['elements']; by = {e['qualified_name']: e for e in elements if e.get('qualified_name')}
    assert not [e for e in elements if e['kind'] == 'SatisfyRequirementUsage'], 'False satisfaction assertion'
    edges = defaultdict(set); id_edges = defaultdict(set)
    ids = {e['id'] for e in elements}
    for rel in model['relationships']:
        for endpoint in rel['sources'] + rel['targets']:
            assert endpoint.get('external') or endpoint['id'] in ids, f'Incomplete local native endpoint: {endpoint}'
        for s in rel['sources']:
            for t in rel['targets']:
                id_edges[(rel['kind'], s['id'])].add(t['id'])
                if s.get('qualified_name') and t.get('qualified_name'):
                    edges[(rel['kind'], s['qualified_name'])].add(t['qualified_name'])
    def exact(kind, source, target):
        assert target in edges[(kind, source)], f'Unresolved native {kind} endpoint: {source} -> {target}'
    def allocated_target(source, instance, part):
        # Syside exports chained allocation ends through unnamed semantic
        # Features. Traverse their IDs rather than inventing instance qnames.
        chain_ids = id_edges[('ReferenceSubsetting', by[source]['id'])]
        expected = {by[instance]['id'], by[part]['id']}
        assert len(chain_ids) == 1 and id_edges[('FeatureChaining', next(iter(chain_ids)))] == expected, f'Unresolved native allocation path: {source} -> {instance}.{part}'
    for c in baseline['concerns']:
        q = 'FrameworkConcerns::'+re.sub(r'[-.]','_',c['id'])
        assert q in by and by[q]['kind'] == 'ConcernUsage', f'Missing native concern: {c["id"]}'
        for target in (c['parent'], c['alias_target']):
            if target:
                exact('Dependency',q,'FrameworkConcerns::'+re.sub(r'[-.]','_',target))
    for row in baseline['mission_scenarios']:
        s = 'ScenarioViews::'+row['id']
        for u in row['use_case_ids']:
            exact('Dependency',s,'FrameworkNeeds::'+u)
        for m in row['mission_requirement_ids']:
            exact('Dependency',s,'FrameworkNeeds::'+m.replace('-','_'))
    for row in baseline['use_cases']:
        for mid in row['mission_requirement_ids']:
            exact('Dependency','FrameworkNeeds::'+row['id'],'FrameworkNeeds::'+mid.replace('-','_'))
    for rid, row in fr.items():
        n = rid[-2:]; q = 'FrameworkRequirements::FR_'+n
        assert q in by, f'Missing native FR: {rid}'
        for mid in row['parents']:
            d = 'FrameworkRequirements::derive_'+mid.replace('-','_')+'_FR_'+n
            exact('ReferenceSubsetting',d+'::source','FrameworkNeeds::'+mid.replace('-','_'))
            exact('ReferenceSubsetting',d+'::target',q)
        for s in row['scenarios']:
            exact('Dependency',q,'ScenarioViews::'+s)
        for f in row['functions']:
            exact('Dependency',q,'BoundaryViews::'+f)
        # Both planning and component mappings resolve through the real semantic API.
        for v in row['verification_case_ids']:
            assert by['FrameworkVerification::'+v]['kind'] == 'VerificationCaseUsage', f'Missing native case: {v}'
            matches = [name for name, e in by.items() if e['kind'] == 'RequirementUsage' and name.startswith('FrameworkVerification::'+v+'::obj::')]
            assert matches and any(q in edges[('ReferenceSubsetting',name)] for name in matches), f'Wrong native verify endpoint: {v}'
        l = row['primary_logical_component_id']
        a = 'FrameworkLogical::responsibility_FR_'+n+'_'+l
        exact('ReferenceSubsetting',a+'::source',q)
        allocated_target(a+'::target','FrameworkLogical::logical','FrameworkLogical::LogicalFramework::'+l)
        for supporting in row['supporting_logical_component_ids']:
            sa = 'FrameworkLogical::support_FR_'+n+'_'+supporting
            exact('ReferenceSubsetting',sa+'::source',q)
            allocated_target(sa+'::target','FrameworkLogical::logical','FrameworkLogical::LogicalFramework::'+supporting)
        assert row['logical_operation'] in by and by[row['logical_operation']]['kind'] == 'PerformActionUsage', f'Unresolved logical operation: {rid}'
        exact('Dependency',q,row['logical_operation'])
        for allocation in row['physical_allocations']:
            p = allocation['native_package']; a = p+'::FR_'+n+'_primary'
            exact('ReferenceSubsetting',a+'::source',q)
            allocated_target(a+'::target',p+'::candidate',p+'::Configuration::'+l)
            for supporting in row['supporting_logical_component_ids']:
                sa = p+'::FR_'+n+'_'+supporting
                exact('ReferenceSubsetting',sa+'::source',q)
                allocated_target(sa+'::target',p+'::candidate',p+'::Configuration::'+supporting)
            assert allocation['operation'] in by and by[allocation['operation']]['kind'] == 'PerformActionUsage', f'Unresolved physical operation: {rid}'
            exact('Dependency',q,allocation['operation'])
    for figure in native_figures:
        assert figure['view'] in by and by[figure['view']]['kind'] == 'ViewUsage', f'Unresolved figure target: {figure["view"]}'
    return {'elements':len(elements), 'relationships':len(model['relationships']),
            'endpoint_completeness':True, 'satisfaction_assertions':0, 'errors':0, 'warnings':0}


def audit(root, inspect_path=None, log_path=None):
    root = Path(root).resolve(); baseline = load(root/'traceability/framework-baseline.json')
    assert baseline['protected_current_sha256'] == PROTECTED, 'Protected snapshot policy changed'
    for name, expected in PROTECTED.items():
        assert sha(root/name) == expected, f'Protected current source changed: {name}'
    # Exact current source policy replaces membership in an obsolete git-show snapshot.
    concerns = unique(baseline['concerns'], 'concern'); parsed = parse_concerns(root/'as-is-domain.tex')
    assert set(concerns) == {r['id'] for r in parsed}, 'Concern current-source ID mismatch'
    native_concerns = dict(re.findall(r"concern <'([^']+)'> \w+ \{[^\n]*doc /\* (.*?) \*/", (root/'sysml/01-concerns.sysml').read_text()))
    assert set(native_concerns) == set(concerns), 'Concern native/current-source ID mismatch'
    for record in parsed:
        c = concerns[record['id']]
        assert all(c.get(k) == v for k,v in record.items()), f'Concern current wording/hierarchy mismatch: {record["id"]}'
        assert native_concerns[c['id']] == c['text'], f'Concern native wording mismatch: {c["id"]}'
        assert c['parent'] is None or c['parent'] in concerns, f'Orphan concern: {c["id"]}'
        assert c['alias_target'] is None or c['alias_target'] in concerns, f'Unknown concern alias: {c["id"]}'
        assert c['disposition'] and c['scope_status'], f'Missing concern disposition: {c["id"]}'
        assert not c.get('framework_requirement_ids'), f'Forced every-concern-to-FR mapping: {c["id"]}'
    assert 'mission_needs' not in baseline and 'legacy_aliases' not in baseline, 'Obsolete parallel mission ledger'
    mr, fr, ucs, scs, uc_mrs, sc_mrs, sc_ucs = current_trace(root)
    bm = unique(baseline['mission_requirements'],'mission requirement'); bf = unique(baseline['framework_requirements'],'framework requirement')
    assert set(bm) == set(mr) and set(bf) == set(fr), 'Report/current ledger requirement ID mismatch'
    assert set(unique(baseline['use_cases'],'use case')) == ucs and set(unique(baseline['mission_scenarios'],'scenario')) == scs, 'Use case/scenario ledger IDs mismatch'
    for row in baseline['use_cases']:
        assert set(row['mission_requirement_ids']) == uc_mrs[row['id']], f'UC ledger MR mismatch: {row["id"]}'
    for row in baseline['mission_scenarios']:
        assert set(row['mission_requirement_ids']) == sc_mrs[row['id']] and set(row['use_case_ids']) == sc_ucs[row['id']], f'SC ledger endpoints mismatch: {row["id"]}'
    for mid, row in bm.items():
        assert row['text'] == mr[mid]['text'], f'MR ledger wording mismatch: {mid}'
        assert set(row['framework_requirement_ids']) == {r for r in fr if mid in fr[r]['parents']}, f'MR ledger FR mismatch: {mid}'
    logical = load(root/'traceability/logical-architecture.json'); la = {r['FR']:r for r in logical['allocations']}
    logical_ids = {r['id'] for r in logical['components']}
    native_las = set(re.findall(r'part (L\d+) :', (root/'sysml/04-logical.sysml').read_text()))
    assert logical_ids == native_las == {r['id'] for r in baseline['logical_components']}, 'Logical component ID mismatch'
    assert set(la) == set(fr) and len(la) == len(logical['allocations']), 'Logical FR allocation set mismatch'
    candidates = {}; trade = load(root/'traceability/trade-study.json')
    for path in sorted((root/'candidates').glob('*.json')):
        candidate = load(path); cid = candidate['id']
        assert cid not in candidates, f'Duplicate candidate: {cid}'
        allocations = {r['FR']:r for r in candidate['allocations']}
        assert set(allocations) == set(fr) and len(allocations) == len(candidate['allocations']), f'Candidate FR allocation set mismatch: {cid}'
        components = {r['logical']:r for r in candidate['components']}
        assert set(components) == logical_ids, f'Candidate logical coverage mismatch: {cid}'
        candidates[cid] = {'record':candidate,'allocations':allocations,'components':components,'path':path}
    assert set(candidates) == set(trade['candidate_ids']) == set(baseline['candidate_ids']), 'Candidate ID agreement failed'
    native_candidates = {p.stem for p in (root/'sysml/candidates').glob('*.sysml')}
    assert native_candidates == {c['path'].stem for c in candidates.values()}, 'Native/current candidate record set mismatch'
    direction = re.search(r'This comparison recommends developing (PA-\w+) first', (root/'trade-selection.tex').read_text())
    assert direction and trade['decision']['preferred'] == direction[1] and baseline['physical_direction'].startswith(direction[1]+','), 'Conditional physical direction report/ledger mismatch'
    audit_allocation_tables(root, logical, candidates[direction[1]]['record'])
    for rid, row in bf.items():
        assert row['text'] == fr[rid]['text'], f'FR ledger wording mismatch: {rid}'
        assert set(row['mission_requirement_ids']) == set(fr[rid]['parents']), f'FR ledger MR mismatch: {rid}'
        assert row['mission_scenario_ids'] == fr[rid]['scenarios'] and row['black_box_function_ids'] == fr[rid]['functions'], f'FR ledger scenario/function mismatch: {rid}'
        lr = la[rid]
        assert lr['verification']['status'] == 'planned, not executed', f'False logical verification outcome: {rid}'
        assert row['primary_logical_component_id'] == lr['primary'] and row['supporting_logical_component_ids'] == lr['support'] and row['logical_operation'] == lr['operation'], f'Logical allocation ledger mismatch: {rid}'
        assert lr['primary'] in logical_ids and set(lr['support']) <= logical_ids, f'Unknown logical endpoint: {rid}'
        pas = unique([dict(a,id=a['candidate_id']) for a in row['physical_allocations']], 'physical trace')
        assert set(pas) == set(candidates), f'Incomplete all-candidate trace: {rid}'
        for cid, c in candidates.items():
            ar = c['allocations'][rid]; traced = pas[cid]
            assert ar['primary'] == lr['primary'] and ar['support'] == lr['support'], f'Candidate logical allocation mismatch: {cid} {rid}'
            assert ar['planned_check'] == ','.join(fr[rid]['methods'])+': '+lr['verification']['need'], f'Candidate planned check mismatch: {cid} {rid}'
            assert traced['physical_component_id'] == c['components'][lr['primary']]['id'] and traced['operation'] == ar['operation'], f'Physical component/operation mismatch: {cid} {rid}'
            assert traced['verification_case_ids'] == row['verification_case_ids'], f'Physical V trace mismatch: {cid} {rid}'
        fr[rid].update(row)
    moes = {r['id'] for r in baseline['measures_of_effectiveness']}
    mops = {r['id'] for r in baseline['measures_of_performance']}
    assert moes == set(re.findall(r"item <'(MOE-\d+)'>",(root/'sysml/02-needs-context.sysml').read_text())), 'MOE native/ledger mismatch'
    assert mops == set(re.findall(r"item <'(MOP-\d+)'>",(root/'sysml/03-requirements.sysml').read_text())), 'MOP native/ledger mismatch'
    for c in concerns.values():
        assert set(c['moe_ids']) <= moes, f'Unknown concern MOE: {c["id"]}'
    for measure in baseline['measures_of_effectiveness'] + baseline['measures_of_performance']:
        assert measure['achieved'] == 'unknown' and 'TBR' in measure['target'], f'False measured/qualified outcome: {measure["id"]}'
    cases = audit_cases(root,baseline,fr)
    review = audit_independent_review(root, baseline)
    assert review['physical_direction'].startswith(direction[1]+','), 'Stale physical direction in review record'
    solution_files = solution_sources(root); solution = '\n'.join(visible(p.read_text()) for p in solution_files)
    active = '\n'.join(visible(p.read_text()) for p in solution_files if p.name != 'as-is-domain.tex')
    assert not re.search(r'\bMN-\d|\bMR-(?:0[6-9]|1[01])\b|\bL09\b', active), 'Retired current trace identifier in report'
    assert not re.search(r'\bevidence contract\b|\bclaim custody\b|\bfixture\b|—',active,re.I), 'Non-source terminology in current prose'
    assert not re.search(r'\\(?:scriptsize|tiny|resizebox|scalebox)\b',active), 'Unreadable reduced publication content'
    for path, expected in baseline['approved_source_sha256'].items():
        assert sha(root/path) == expected, f'Approved current scope/wording/ID source changed: {path}'
    glossary = (root/'glosario.tex').read_text(); acronyms = re.findall(r'\\syma(?:\[[^]]*\])?\{([^}]+)\}',glossary)
    assert len(acronyms) == len(set(acronyms)), 'Duplicate glossary acronym'
    required = {'MBSE','OOSEM','SysML','EPS','RAM','BOM','SIL','HIL','MOE','MOP','MR','FR','MIL','CDR','SIR','BM25','SOH','TBR'}
    assert required <= set(acronyms), f'Missing glossary acronyms: {sorted(required-set(acronyms))}'
    bibliography = (root/'literatura.bib').read_text(); keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,',bibliography)
    assert len(keys) == len(set(keys)), 'Duplicate bibliography key'
    missing = set()
    for path in root.glob('*.tex'):
        text = visible(path.read_text())
        assert not re.search(r'\\\\cite[a-zA-Z]*',text), f'Doubled citation escape: {path.name}'
        for citations in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}',text):
            missing.update({k.strip() for k in citations.split(',')}-set(keys))
    assert not missing, f'Missing bibliography citations: {sorted(missing)}'
    for key in baseline['primary_bibliography_keys']:
        assert key in keys, f'Missing primary bibliography source: {key}'
    assert 'NASA/SP-2016-6105' in bibliography and '10.1007/s12567-023-00509-9' in bibliography, 'Incorrect NASA or Girardello source bibliography'
    sources = load(root/'traceability/source-review.json')['sources']
    for source in sources:
        if source['id'] == 'search-transfer':
            assert Path(source['source']).parts[-2:] == ('embeddings', 'search.py'), 'Incorrect search-code provenance'
        else:
            assert source['id'] in keys, f'Unknown reviewed bibliography key: {source["id"]}'
        assert sha(source['source']) == source['sha256'], f'Reviewed primary source changed: {source["id"]}'
    diagrams = re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',solution)
    assert all(d.startswith('fig/') for d in diagrams), 'Solution figures must be under fig/'
    figures = audit_native_figures(root,diagrams)
    assert figures == baseline['native_figures'], 'Current native figure manifest/provenance mismatch'
    semantic = None
    if inspect_path:
        inspection = load(inspect_path)
        paths = inspection['files']['input'] + inspection['files']['included']
        assert len(paths) == len(set(paths)) and {Path(p).resolve() for p in paths} == {p.resolve() for p in (root/'sysml').rglob('*.sysml')}, 'Inspection current source set mismatch'
        semantic = semantic_audit(inspection,baseline,fr,figures)
    pages = None
    if log_path:
        log = Path(log_path).read_text(errors='replace')
        assert not re.search(r'Overfull \\[hv]box|undefined on input|undefined references|undefined citations|Citation .+ undefined|Reference .+ undefined|Float too large|^!',log,re.MULTILINE), 'LaTeX unresolved reference/citation, error, overfull box or oversized float'
        match = re.search(r'Output written on .*?\((\d+) pages?',log)
        assert match, 'No final PDF page count in LaTeX log'
        pages = int(match[1]); assert pages <= 100, f'Report exceeds 100 pages: {pages}'
    return {'valid':True, 'scope':'Current report/native specification consistency, planned trace and publication checks only. No empirical framework V&V.',
            'concern_occurrences':len(concerns), 'root_concerns':sum(c['kind']=='root' for c in concerns.values()),
            'mission_requirements':len(mr), 'use_cases':len(ucs), 'mission_scenarios':len(scs),
            'framework_requirements':len(fr), 'logical_components':len(logical_ids), 'planned_verification_cases':len(cases),
            'black_box_functions':len(set().union(*(set(r['functions']) for r in fr.values()))),
            'measures_of_effectiveness':len(moes), 'measures_of_performance':len(mops),
            'candidate_allocations':{cid:len(c['allocations']) for cid,c in candidates.items()},
            'protected_current_sources_unchanged':True, 'native_figures':figures,
            'publication_figures':len(re.findall(r'\\begin\{figure\}',solution))-solution.count('\\ContinuedFloat'),
            'glossary_acronyms':len(acronyms),
            'missing_citations':[], 'semantic':semantic, 'pages':pages,
            'framework_empirical_vv':'not executed', 'independent_review':review['status'],
            'original_major_findings':review['original_major_findings'], 'major_findings_closed':len(review['findings']),
            'final_publication_review':review['final_publication_review'],
            'publication_material_blockers':review['final_publication_review_evidence']['material_blockers']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--inspect',type=Path,help='Uncapped genuine Syside inspection JSON')
    parser.add_argument('--log',type=Path,help='Final-pass actual report LaTeX log')
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.report,args.inspect,args.log),indent=2)); return 0
    except (AssertionError,KeyError,ValueError,OSError) as error:
        print(json.dumps({'valid':False,'scope':'report/model check','error':str(error)}),file=sys.stderr); return 1


if __name__ == '__main__':
    raise SystemExit(main())
