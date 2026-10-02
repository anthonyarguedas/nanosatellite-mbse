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
    needs = unique(baseline['mission_needs'], 'need')
    logical = unique(baseline['logical_components'], 'logical component')
    verification = unique(baseline['verification_cases'], 'verification case')
    assert len(concerns) == 144 and len(roots) == 30
    assert set(requirements) == {f'FR-{i:02d}' for i in range(1, 41)}
    assert set(needs) == {f'MN-{i:02d}' for i in range(1, 12)}
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
    for case in verification.values():
        assert case['framework_requirement_id'] in requirements
        assert case['executed'] is False and case['verdict'] is None
    assert {v['framework_requirement_id'] for v in verification.values()} == set(requirements)

    source_files = list(root.glob('*.tex')) + list((root / 'sections').glob('*.tex'))
    solution_files = [root / 'solucion.tex'] + list((root / 'sections').glob('*.tex'))
    solution = '\n'.join(path.read_text() for path in solution_files)
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
    diagrams = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', solution)
    assert len(diagrams) == 3, f'Expected three solution figures, found {len(diagrams)}'
    for diagram in diagrams:
        assert (root / diagram).is_file(), f'Missing figure: {diagram}'
    assert not re.search(r'\\(?:scriptsize|tiny|resizebox|scalebox)\b', '\n'.join((root / 'sections' / name).read_text() for name in ['needs.tex', 'requirements.tex', 'logical.tex', 'physical-candidates.tex', 'trade-selection.tex', 'traceability.tex', 'verification-plan.tex']))

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
        assert not [e for e in elements if e['kind'] == 'SatisfyRequirementUsage']
        semantic = {'elements': len(elements), 'relationships': len(model['relationships']), 'common_ids_resolved': True, 'satisfaction_assertions': 0}
    if args.log:
        log = args.log.read_text(errors='replace')
        assert not re.search(r'Overfull \\[hv]box|undefined on input|undefined references|undefined citations|^!', log, re.MULTILINE), 'LaTeX has unresolved references/citations, errors, or overfull boxes'

    print(json.dumps({'valid': True, 'scope': 'Report, source fidelity, planned trace coverage and optional semantic model. No framework implementation verification.', 'concern_occurrences': len(concerns), 'root_concerns': len(roots), 'mission_needs': len(needs), 'framework_requirements': len(requirements), 'logical_capabilities': len(logical), 'planned_verification_cases': len(verification), 'candidates': candidate_counts, 'solution_figures': len(diagrams), 'as_is_observations_unchanged': True, 'intro_unchanged': True, 'missing_citations': [], 'semantic': semantic}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}), file=sys.stderr)
        raise SystemExit(1)
