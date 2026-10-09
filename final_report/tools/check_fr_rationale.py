#!/usr/bin/env python3
"""Check or regenerate the authored FR rationale column and its current ledger.

This preserves requirement statements, inputs/outputs, direct parents and native
models. Source evidence motivates proposed behavior. It asserts no achieved V&V.
"""
import argparse
import json
from pathlib import Path
import re

import audit_report as audit

LEDGER = 'traceability/fr-rationale.json'


def refresh(root):
    authored = audit.load(root/LEDGER)
    rows = audit.unique(authored['requirements'], 'authored FR rationale')
    baseline_path = root/'traceability/framework-baseline.json'
    baseline = audit.load(baseline_path)
    records = audit.unique(baseline['framework_requirements'], 'baseline FR')
    assert set(rows) == set(records) == audit.ACTIVE_FR, 'Complete 40-FR rationale coverage required'
    for rid, row in rows.items():
        assert row['parent_mrs'] == records[rid]['mission_requirement_ids'], f'Changed direct parents: {rid}'
        parsed = audit.parse_fr_rationale(row['rationale_latex'])
        assert parsed['parents'] == row['parent_mrs'], f'Malformed authored parents: {rid}'
        records[rid].update(rationale=parsed['rationale'], rationale_citations=parsed['rationale_citations'])
    report_path = root/'requirements.tex'
    text = report_path.read_text()
    pattern = r'(?m)^(FR-\d{2} & .*? & )(.*?) (\\\\)[ \t]*$'
    seen = []

    def replace(match):
        rid = match[1].split(' ', 1)[0]
        seen.append(rid)
        return match[1] + rows[rid]['rationale_latex'] + ' ' + match[3]

    updated = re.sub(pattern, replace, text)
    assert len(seen) == len(set(seen)) == 40 and set(seen) == set(rows), 'FR rationale generation coverage mismatch'
    report_path.write_text(updated)
    baseline['fr_rationale'] = {'ledger': LEDGER, 'requirements': 40, 'direct_parents': 169,
                               'interpretation': authored['interpretation']}
    baseline_path.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + '\n')


def check(root):
    _, fr, *_ = audit.current_trace(root)
    baseline = audit.load(root/'traceability/framework-baseline.json')
    return audit.audit_fr_rationales(root, fr, baseline['framework_requirements'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    try:
        if args.refresh:
            refresh(args.report)
        result = check(args.report)
    except (AssertionError, KeyError, ValueError, OSError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}))
        return 1
    print(json.dumps({'valid': True, **result}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
