#!/usr/bin/env python3
"""Check report summaries against Syside-resolved primary allocation endpoints.

Run: python3 final_report/sysml/check_logical_responsibilities.py
Only report/model sources are loaded, via the licensed model.py inspector.
Regex is used only to read the displayed summaries, never to infer allocations.
"""
import collections
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
TOOL = Path('/Users/antho/agent-tools/sysmlv2/skills/sysmlv2/scripts/model.py')
result = subprocess.run(
    ['uv', 'run', str(TOOL), 'inspect', str(ROOT), '--warnings-as-errors',
     '--max-elements', '0', '--max-relationships', '0', '--json'],
    check=True, capture_output=True, text=True,
)
report = json.loads(result.stdout)
assert report['valid'] and not report['diagnostics'], report['diagnostics']
model = report['semantic_model']
elements = {e['id']: e for e in model['elements']}
by_name = {e['qualified_name']: e for e in elements.values()}
outgoing = collections.defaultdict(list)
for relationship in model['relationships']:
    for source in relationship['sources']:
        outgoing[source['id']].append(relationship)


def targets(identifier, kind):
    return [target for relationship in outgoing[identifier]
            if relationship['kind'] == kind for target in relationship['targets']]


# Select allocations by the resolved metadata type, not their source names.
primary_annotations = {
    source['id'] for relationship in model['relationships']
    if relationship['kind'] == 'FeatureTyping'
    and any(t.get('qualified_name') == 'FrameworkDomain::primaryResponsibility'
            for t in relationship['targets'])
    for source in relationship['sources']
}
primary = [e for e in elements.values() if e['kind'] == 'AllocationUsage'
           and any(t['id'] in primary_annotations
                   for t in targets(e['id'], 'OwningMembership'))]
assert len(primary) == 40, len(primary)
owners = collections.defaultdict(list)
requirements = []
for allocation in primary:
    ends = {e['name']: e for e in elements.values()
            if e.get('owner') and e['owner']['id'] == allocation['id']
            and e['name'] in ('source', 'target')}
    sources = targets(ends['source']['id'], 'ReferenceSubsetting')
    assert len(sources) == 1 and sources[0]['kind'] == 'RequirementUsage'
    requirement = sources[0]['qualified_name']
    assert requirement.startswith('FrameworkRequirements::FR_')
    destination = targets(ends['target']['id'], 'ReferenceSubsetting')
    assert len(destination) == 1
    # A feature-chain endpoint resolves logical.Lxx, not a free-text owner label.
    chain = targets(destination[0]['id'], 'FeatureChaining')
    assert {t.get('qualified_name') for t in chain} >= {'FrameworkLogical::logical'}
    components = [t for t in chain if (t.get('qualified_name') or '').startswith(
        'FrameworkLogical::LogicalFramework::L')]
    assert len(components) == 1 and components[0]['kind'] == 'PartUsage'
    component = components[0]['qualified_name'].split('::')[-1]
    owners[component].append(requirement.split('FR_')[-1])
    requirements.append(requirement)
assert len(set(requirements)) == 40, 'Duplicate primary ownership'
assert set(requirements) == {f'FrameworkRequirements::FR_{n:02d}' for n in range(1, 41)}
assert set(owners) == {f'L{n:02d}' for n in range(1, 10)}

# Compare each printed FR summary and reference type to the semantic architecture.
text = (ROOT / '11-logical-responsibilities.sysml').read_text()
cards = re.findall(r"ref part (L\d\d) : (\w+) = logical\.(L\d\d)\s*\{\s*doc /\*(.*?)\*/", text, re.S)
assert len(cards) == 9
for component, definition, binding, documentation in cards:
    assert component == binding
    actual = by_name[f'FrameworkLogical::LogicalFramework::{component}']
    assert actual['direct_semantic_types'] == [f'FrameworkLogical::{definition}']
    printed = re.search(r'Primary FR: ([\d, ]+)\.', documentation)
    assert printed, component
    numbers = printed.group(1).split(', ')
    assert numbers == sorted(owners[component]), (component, numbers, owners[component])
    for label in ('Records:', 'Required:', 'Provided:'):
        assert label in documentation, (component, label)

print(json.dumps({'status': 'passed', 'warnings': report['summary']['warnings'],
                  'primary_allocations': 40, 'unique_requirements': 40,
                  'typed_component_references': 9, 'matching_display_summaries': 9,
                  'primary_FR_by_component': {k: sorted(v) for k, v in sorted(owners.items())}},
                 indent=2))
