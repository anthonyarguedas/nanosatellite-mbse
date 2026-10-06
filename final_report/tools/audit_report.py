#!/usr/bin/env python3
"""Audit report trace records. This is not verification of the framework."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def load(path: Path):
    return json.loads(path.read_text())


def unique(records, label):
    result = {record['id']: record for record in records}
    assert len(result) == len(records), f'Duplicate {label} IDs'
    return result


def solution_sources(root: Path):
    """Follow the solution chapter's TeX inputs after section files are moved."""
    result = []
    pending = [root / 'solucion.tex']
    while pending:
        path = pending.pop()
        if path in result:
            continue
        assert path.is_file(), f'Missing solution source: {path}'
        result.append(path)
        text = re.sub(r'(?<!\\)%[^\n]*', '', path.read_text())
        inputs = re.findall(r'\\(?:input|include)\s*\{([^}]+)\}', text)
        pending.extend(root / Path(name).with_suffix('.tex') for name in reversed(inputs))
    return result


def audit_native_figures(root: Path, diagrams: list[str]):
    assert len(diagrams) == len(set(diagrams)), 'Duplicate solution figure paths'
    result = []
    for diagram in diagrams:
        figure = root / diagram
        assert figure.is_file(), f'Missing figure: {diagram}'
        manifest_path = figure.with_suffix('.manifest.json')
        assert manifest_path.is_file(), f'Missing native figure manifest: {diagram}'
        manifest = load(manifest_path)
        assert manifest['visualizer']['name'] == 'Syside Modeler' and manifest['visualizer']['native'], f'Non-native figure: {diagram}'
        artifacts = {artifact['format']: artifact for artifact in manifest['artifacts']}
        assert {'svg', 'png', 'pdf'} <= set(artifacts), f'Incomplete native figure artifacts: {diagram}'
        for format_name, artifact in artifacts.items():
            local_path = figure.with_suffix('.' + format_name)
            assert Path(artifact['path']).name == local_path.name, f'Figure artifact name mismatch: {diagram}'
            assert local_path.is_file(), f'Missing {format_name} artifact: {diagram}'
        svg = figure.with_suffix('.svg')
        svg_hash = hashlib.sha256(svg.read_bytes()).hexdigest()
        provenance = artifacts['svg']['provenance']
        assert provenance['producer'] == 'Syside Modeler' and provenance['native'], f'Non-native SVG: {diagram}'
        assert svg_hash == provenance['sha256'], f'Native SVG hash mismatch: {diagram}'
        source = artifacts['pdf']['provenance']['source_svg']
        assert source['producer'] == 'Syside Modeler', f'Non-native PDF source: {diagram}'
        assert Path(source['path']).name == svg.name and source['sha256'] == svg_hash, f'PDF source hash mismatch: {diagram}'
        result.append({'figure': diagram, 'view': manifest['target']['qualified_name'], 'manifest': str(manifest_path.relative_to(root)), 'native_svg_sha256': svg_hash, 'exact_pdf_source_hash_matches': True})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--inspect', type=Path, help='Uncapped Syside semantic inspection JSON')
    parser.add_argument('--log', type=Path, help='Final-pass LaTeX log')
    args = parser.parse_args()
    root = args.report.resolve()
    baseline = load(root / 'traceability/framework-baseline.json')
    concerns = unique(baseline['concerns'], 'concern')
    roots = [c for c in concerns.values() if c['kind'] == 'root']
    requirements = unique(baseline['framework_requirements'], 'requirement')
    needs = unique(baseline['mission_needs'], 'retained source need')
    mission_requirements = unique(baseline['mission_requirements'], 'mission requirement')
    logical = unique(baseline['logical_components'], 'logical component')
    verification = unique(baseline['verification_cases'], 'verification case')
    assert len(concerns) == 144 and len(roots) == 30
    assert set(requirements) == {f'FR-{i:02d}' for i in range(1, 41)}
    assert set(needs) == {f'MN-{i:02d}' for i in range(1, 12)}
    assert set(mission_requirements) == {f'MR-{i:02d}' for i in range(1, 12)}
    for mission_requirement in mission_requirements.values():
        assert mission_requirement['mission_need_id'] in needs
        assert set(mission_requirement['source_concern_ids']) <= set(concerns)
        assert set(mission_requirement['framework_requirement_ids']) <= set(requirements)
    assert set(logical) == {f'L{i:02d}' for i in range(1, 10)}
    assert set(verification) == {f'V{i:02d}' for i in range(1, 41)}
    for concern in concerns.values():
        assert concern['parent'] is None or concern['parent'] in concerns
        assert concern['framework_requirement_ids'], f'Unmapped concern {concern["id"]}'
        assert set(concern['framework_requirement_ids']) <= set(requirements)
        assert set(concern['mission_need_ids']) <= set(needs)
    for target in baseline['legacy_aliases'].values():
        assert target in concerns
    for requirement in requirements.values():
        direct = requirement['source_concern_ids']
        inherited = [c['id'] for c in concerns.values() if set(c['mission_need_ids']) & set(requirement['mission_need_ids'])]
        assert direct or inherited, f'No concern-to-need derivation path for {requirement["id"]}'
        assert set(direct) <= set(concerns)
        assert requirement['logical_capability_ids']
        assert set(requirement['logical_capability_ids']) <= set(logical)
        assert set(requirement['mission_need_ids']) <= set(needs)
        assert requirement['mission_requirement_ids']
        assert set(requirement['mission_requirement_ids']) <= set(mission_requirements)
    for case in verification.values():
        assert case['framework_requirement_id'] in requirements
        assert case['executed'] is False and case['verdict'] is None
    assert {v['framework_requirement_id'] for v in verification.values()} == set(requirements)

    source_files = list(root.glob('*.tex')) + list((root / 'sections').glob('*.tex'))
    solution_files = solution_sources(root)
    solution = '\n'.join(path.read_text() for path in solution_files)
    visible_solution = re.sub(r'\\label\{[^}]+\}|(?<!\\)%[^\n]*', '', solution)
    assert not re.search(r'\bmission needs\b|\bMN-\d', visible_solution, re.IGNORECASE), 'Solution uses parallel mission-need terminology'
    glossary = (root / 'glosario.tex').read_text()
    acronym_entries = re.findall(r'\\syma(?:\[[^\]]*\])?\{([^}]+)\}', glossary)
    assert len(acronym_entries) == len(set(acronym_entries)), 'Duplicate glossary acronym entries'
    required_acronyms = {'MBSE', 'OOSEM', 'SysML', 'EPS', 'RAM', 'BOM', 'DUT', 'FMEA', 'SIL', 'HIL', 'TP', 'FP', 'FN', 'MOE', 'MOP', 'MR', 'FR'}
    assert required_acronyms <= set(acronym_entries), f'Missing glossary acronyms: {sorted(required_acronyms - set(acronym_entries))}'
    for concern in concerns.values():
        macro = 'ConcernRoot' if concern['kind'] == 'root' else 'ConcernCause'
        expected = f'\\{macro}{{{concern["id"]}}}{{{concern["text"]}}}'
        assert solution.count(expected) == 1, f'Concern wording/occurrence mismatch: {concern["id"]}'
    assert hashlib.sha256((root / 'intro.tex').read_bytes()).hexdigest() == baseline['intro_source_sha256']
    original = subprocess.run(
        ['git', 'show', f'{baseline["baseline_head"]}:final_report/solucion.tex'],
        cwd=root, text=True, capture_output=True, check=True,
    ).stdout
    observation = original[original.index('ASCEND is currently associated'):]
    observation = observation[:observation.index('\\section{Analyze System Requirements}')].rstrip()
    assert observation in solution, 'Reported as-is observations changed'

    candidate_counts = {}
    for name in ['comet', 'custom', 'git-yaml', 'nanospace', 'valispace']:
        candidate = load(root / f'candidates/{name}.json')
        components = unique(candidate['components'], f'{name} component')
        allocations = candidate['allocations']
        assert {a['requirement_id'] for a in allocations} == set(requirements)
        assert len(allocations) == 40
        for allocation in allocations:
            rid = allocation['requirement_id']
            assert allocation['logical_component_ids'] == requirements[rid]['logical_capability_ids']
            assert allocation['physical_component_ids']
            assert set(allocation['physical_component_ids']) <= set(components)
            assert allocation['verification_id'] == f'V{int(rid[-2:]):02d}'
            assert allocation['realization_mechanism'] and allocation['implementation_gap']
        candidate_counts[candidate['id']] = {'components': len(components), 'planned_requirement_allocations': 40}

    bibliography = (root / 'literatura.bib').read_text()
    keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', bibliography)
    assert len(keys) == len(set(keys)), 'Duplicate bibliography keys'
    missing_citations = set()
    for path in source_files:
        text = re.sub(r'(?<!\\)%[^\n]*', '', path.read_text())
        assert not re.search(r'\\\\cite[a-zA-Z]*', text), f'Doubled citation escape in {path}'
        for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}', text):
            missing_citations |= {k.strip() for k in group.split(',')} - set(keys)
    assert not missing_citations, f'Missing citations: {sorted(missing_citations)}'
    figure_inclusions = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', solution)
    # A wide native action flow can use several viewports of the same PDF.
    diagrams = list(dict.fromkeys(figure_inclusions))
    labels = re.findall(r'\\label\{([^}]+)\}', solution)
    for label in ['fig:framework-sc01', 'fig:framework-sc02', 'fig:framework-sc03', 'fig:framework-context', 'fig:framework-logical', 'fig:framework-physical']:
        assert labels.count(label) == 1, f'Missing or duplicate solution figure label: {label}'
    for label in ['tab:framework-scenarios', 'tab:framework-boundary-contracts', 'tab:framework-logical']:
        assert label not in labels, f'Replaced scenario/interface/responsibilities table remains: {label}'
    assert sum('/scenarios/' in diagram for diagram in diagrams) == 3, 'Expected three scenario diagrams'
    assert all(diagram.startswith('fig/') for diagram in diagrams), 'Solution figures must be under final_report/fig/'
    native_figures = audit_native_figures(root, diagrams)
    assert not re.search(r'\\(?:scriptsize|tiny|resizebox|scalebox)\b', '\n'.join(path.read_text() for path in solution_files if path.name != 'as-is-domain.tex'))

    semantic = None
    if args.inspect:
        inspection = load(args.inspect)
        assert inspection['valid'] and inspection['exit_code'] == 0
        assert not [d for d in inspection['diagnostics'] if d.get('severity') in ['error', 'warning']]
        model = inspection['semantic_model']
        elements = model['elements']
        qnames = {e['qualified_name'] for e in elements if e.get('qualified_name')}
        for cid in concerns:
            assert 'FrameworkConcerns::' + re.sub(r'[-.]', '_', cid) in qnames
        for rid in requirements:
            assert 'FrameworkRequirements::' + rid.replace('-', '_') in qnames
        for vid in verification:
            assert f'FrameworkVerification::{vid}' in qnames
        for nid in needs:
            assert 'FrameworkNeeds::' + nid.replace('-', '_') in qnames
        for mid in mission_requirements:
            assert 'FrameworkNeeds::' + mid.replace('-', '_') in qnames
        for figure in native_figures:
            assert figure['view'] in qnames, f'Unresolved figure target: {figure["view"]}'
        assert not [e for e in elements if e['kind'] == 'SatisfyRequirementUsage']
        semantic = {'elements': len(elements), 'relationships': len(model['relationships']), 'common_ids_resolved': True, 'satisfaction_assertions': 0}
    if args.log:
        log = args.log.read_text(errors='replace')
        assert not re.search(r'Overfull \\[hv]box|undefined on input|undefined references|undefined citations|^!', log, re.MULTILINE), 'LaTeX has unresolved references/citations, errors, or overfull boxes'

    print(json.dumps({'valid': True, 'scope': 'Report, source fidelity, planned trace coverage and optional semantic model. No framework implementation verification.', 'concern_occurrences': len(concerns), 'root_concerns': len(roots), 'mission_requirements': len(mission_requirements), 'retained_source_need_records': len(needs), 'framework_requirements': len(requirements), 'logical_capabilities': len(logical), 'planned_verification_cases': len(verification), 'candidates': candidate_counts, 'glossary_acronyms': len(acronym_entries), 'solution_figures': len(diagrams), 'publication_figures': len(re.findall(r'\\begin\{figure\}', solution)) - solution.count('\\ContinuedFloat'), 'figure_inclusions': len(figure_inclusions), 'native_figures': native_figures, 'as_is_observations_unchanged': True, 'intro_unchanged': True, 'missing_citations': [], 'semantic': semantic}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}), file=sys.stderr)
        raise SystemExit(1)
