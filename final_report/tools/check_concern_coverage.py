#!/usr/bin/env python3
"""Reconcile and check authored concern contributions. No empirical V&V is asserted.

The focused ledger explicitly names every occurrence. --refresh-table regenerates
only its appendix table. --refresh also reconciles native dispositions/contribution
inventory and the baseline ledger. Concern assertions, hierarchy, source locators
and historical checks are preserved.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

import audit_report as audit

LEDGER = 'traceability/concern-moe-coverage.json'
REPORT_TABLE = 'apendice.tex'
TABLE_LABEL = 'tab:framework-moe-concerns'
APPENDIX_LABEL = 'appendix:framework-moe-concerns'
BEGIN = '% BEGIN GENERATED CONCERN-MOE COVERAGE'
END = '% END GENERATED CONCERN-MOE COVERAGE'
NATIVE_BEGIN = '    // BEGIN COMPLETE CONCERN-MOE CONTRIBUTIONS'
NATIVE_END = '    // END COMPLETE CONCERN-MOE CONTRIBUTIONS'
MOES = {f'MOE-{n:02}' for n in range(1, 7)}
MAX_DISPLAY_CONCERNS = 4


def identifier(cid):
    return re.sub(r'[-.]', '_', cid)


def authored(root):
    record = audit.load(root/LEDGER)
    concerns = audit.unique(audit.parse_concerns(root/'apendice.tex'), 'source concern')
    groups = audit.unique(record['groups'], 'coverage group')
    membership = {}
    for gid, row in groups.items():
        assert row['interpretation'].strip(), f'Empty contribution interpretation: {gid}'
        assert row['concern_ids'] and len(set(row['concern_ids'])) == len(row['concern_ids']), f'Invalid concern group: {gid}'
        assert row['moe_ids'] == sorted(set(row['moe_ids'])) and set(row['moe_ids']) <= MOES and row['moe_ids'], f'Invalid MOE group: {gid}'
        assert set(row['display']) == set(row['moe_ids']) and all(row['display'].values()), f'Missing forward explanation: {gid}'
        for cid in row['concern_ids']:
            assert cid not in membership, f'Duplicate grouped concern: {cid}'
            assert cid in concerns, f'Unknown concern anchor: {cid}'
            membership[cid] = row
    assert set(membership) == set(concerns), f'Unmapped concerns: {sorted(set(concerns) - set(membership))}'
    for cid, row in concerns.items():
        assert row['parent'] is None or row['parent'] in concerns, f'Orphan concern: {cid}'
        target = row['alias_target']
        assert target is None or target in concerns, f'Unknown concern alias: {cid}'
        if target:
            assert set(membership[target]['moe_ids']) <= set(membership[cid]['moe_ids']), f'Alias contribution omitted: {cid}'
    return record, concerns, membership


def display_rows(record):
    rows = []
    for mid in sorted(MOES):
        for group in record['groups']:
            if mid in group['moe_ids']:
                ids = group['concern_ids']
                for start in range(0, len(ids), MAX_DISPLAY_CONCERNS):
                    rows.append({'moe': mid, 'concern_ids': ids[start:start + MAX_DISPLAY_CONCERNS],
                                 'contribution': group['display'][mid], 'group': group['id']})
    return rows


def table(record):
    header = r'\textbf{MOE} & \textbf{Contributing concerns (linked IDs)} & \textbf{Contribution} \\'
    lines = [r'\caption{All contributing concerns for each measure of effectiveness.}\label{tab:framework-moe-concerns}\\',
             r'\toprule', header, r'\midrule', r'\endfirsthead', r'\toprule', header,
             r'\midrule', r'\endhead', r'\bottomrule', r'\endfoot']
    previous = None
    for row in display_rows(record):
        if previous is not None and row['moe'] != previous:
            lines.append(r'\midrule')
        ids = ', '.join(r'\ConcernRef{' + cid + '}' for cid in row['concern_ids'])
        explanation = row['contribution'].replace('&', r'\&').replace('%', r'\%')
        lines.append(f'{row["moe"]} & {ids} & {explanation} ' + r'\\')
        previous = row['moe']
    lines.append(r'\end{longtable}')
    return '\n'.join(lines)


def check_forward_table(text, concerns, expected):
    rows = audit.table_rows(text, r'MOE-\d{2}\s*&')
    pairs, order = [], []
    for row in rows:
        assert len(row) == 3 and row[0] in MOES, 'Malformed forward concern row'
        ids = re.findall(r'\\ConcernRef\{([^}]+)\}', row[1])
        assert 1 <= len(ids) <= MAX_DISPLAY_CONCERNS, 'Forward row concern limit exceeded'
        assert row[1] == ', '.join(r'\ConcernRef{' + cid + '}' for cid in ids), 'Unlinked or abbreviated forward concern'
        assert set(ids) <= set(concerns), 'Invalid forward concern link'
        assert row[2].strip(), 'Empty forward contribution explanation'
        pairs.extend((cid, row[0]) for cid in ids)
        order.append(row[0])
    assert order == sorted(order) and set(order) == MOES, 'Forward MOE organization mismatch'
    assert len(pairs) == len(set(pairs)), 'Duplicate displayed concern/MOE membership'
    assert set(pairs) == expected, 'Displayed forward concern/MOE membership mismatch'
    assert {cid for cid, _ in pairs} == set(concerns), 'Missing displayed concern ID'
    return {'orientation': 'MOE to concerns', 'rows': len(rows), 'memberships': len(pairs),
            'maximum_concerns_per_row': MAX_DISPLAY_CONCERNS,
            'per_moe_rows': dict(sorted(Counter(order).items()))}


def report_table(root):
    report = (root/REPORT_TABLE).read_text()
    body = (root/'needs.tex').read_text()
    table_label = r'\label{' + TABLE_LABEL + '}'
    section_label = r'\label{' + APPENDIX_LABEL + '}'
    assert BEGIN not in body and END not in body and table_label not in audit.visible(body), 'Concern/MOE table duplicated in main text'
    assert all(len(row) == 2 for row in audit.table_rows(body, r'MOE-\d{2}')), 'Concern/MOE table duplicated in main text'
    assert report.count(BEGIN) == report.count(END) == 1, 'Missing/duplicate appendix coverage region'
    appendix = audit.visible(report)
    assert appendix.count(table_label) == 1, 'Missing/duplicate appendix table label'
    assert appendix.count(section_label) == 1 and appendix.index(section_label) < appendix.index(table_label), 'Missing/misplaced appendix section label'
    assert all(r'\ref{' + label + '}' in audit.visible(body) for label in (APPENDIX_LABEL, TABLE_LABEL)), 'Missing main-text appendix/table reference'
    main = audit.visible((root/'main.tex').read_text())
    include = r'\include{apendice}'
    assert main.count(include) == 1 and r'\appendix' in main and main.index(r'\appendix') < main.index(include), 'Concern table must be included after appendix switch'
    match = re.search(re.escape(BEGIN) + r'\n(.*?)\n' + re.escape(END), report, re.DOTALL)
    assert match, 'Missing report concern/MOE table'
    return match[1]


def check_report_link_commands(root):
    source = audit.visible((root/'sty/framework-report.tex').read_text() + '\n' + (root/REPORT_TABLE).read_text())

    def command(name):
        matches = list(re.finditer(r'\\(?:new|renew)command\{\\' + name + r'\}\[\d+\]\s*\{', source))
        assert matches, f'Missing concern link command: {name}'
        return audit.group(source, matches[-1].end() - 1)[0].strip()

    assert command('ConcernRef') == r'\hyperref[concern:#1]{\ConcernId{#1}}', 'ConcernRef must link to the displayed concern ID'
    anchor = command('ConcernAnchor')
    assert r'\phantomsection' in anchor and r'\label{concern:#1}' in anchor, 'Missing concern hyperlink destination'
    for name in ('ConcernRoot', 'ConcernCause'):
        assert r'\ConcernAnchor{#1}' in command(name), f'Missing concern anchor call: {name}'
    assert r'\item\leavevmode\ConcernAnchor{#1}' in command('ConcernCause'), 'Descendant anchor must stay with its displayed ID at page breaks'


def refresh_report_table(root, record):
    """Regenerate the appendix table without changing models or stored checks."""
    report_path = root/REPORT_TABLE
    report = report_path.read_text()
    assert report.count(BEGIN) == report.count(END) == 1, 'Missing/duplicate appendix coverage region'
    report, n = re.subn(re.escape(BEGIN) + r'.*?' + re.escape(END),
                       lambda _: BEGIN + '\n' + table(record) + '\n' + END, report, flags=re.DOTALL)
    assert n == 1, 'Missing/duplicate report coverage region'
    report_path.write_text(report)


def counts(concerns, membership):
    inverse = {mid: [cid for cid in concerns if mid in membership[cid]['moe_ids']] for mid in sorted(MOES)}
    return {'concerns': len(concerns), 'roots': sum(c['kind'] == 'root' for c in concerns.values()),
            'descendants': sum(c['kind'] == 'cause' for c in concerns.values()),
            'aliases': sum(c['alias_target'] is not None for c in concerns.values()),
            'covered_concerns': len(membership), 'unmapped_concerns': 0,
            'moes': len(MOES), 'concern_moe_links': sum(len(r['moe_ids']) for r in membership.values()),
            'per_moe': {mid: len(ids) for mid, ids in inverse.items()}}


def refresh(root):
    record, concerns, membership = authored(root)
    baseline_path = root/'traceability/framework-baseline.json'
    baseline = audit.load(baseline_path)
    ledger_concerns = audit.unique(baseline['concerns'], 'baseline concern')
    assert set(ledger_concerns) == set(concerns), 'Baseline concern occurrence mismatch'
    native_path = root/'sysml/01-concerns.sysml'
    native = native_path.read_text()
    for cid, source in concerns.items():
        c = ledger_concerns[cid]
        assert all(c.get(k) == v for k, v in source.items()), f'Changed source assertion/hierarchy: {cid}'
        row = membership[cid]
        c.update(moe_ids=row['moe_ids'], disposition=row['interpretation'], moe_contribution_group=row['id'])
        annotation = ('    @CurrentDisposition about ' + identifier(cid) + ' { scopeStatus = ' + json.dumps(c['scope_status'])
                      + '; disposition = ' + json.dumps(c['disposition']) + '; moeIdentifiers = '
                      + json.dumps(','.join(c['moe_ids'])) + '; }')
        pattern = rf'(?m)^    @CurrentDisposition about {identifier(cid)} \{{[^\n]*\}}$'
        native, n = re.subn(pattern, lambda _: annotation, native)
        assert n == 1, f'Missing/duplicate native disposition: {cid}'
    native = re.sub(re.escape(NATIVE_BEGIN) + r'.*?' + re.escape(NATIVE_END) + r'\n?', '', native, flags=re.DOTALL)
    native = re.sub(r'(?m)^    #qualitativeContribution dependency contribution_[^\n]*\n', '', native)
    edges = [NATIVE_BEGIN,
             '    // Each occurrence has explicit bounded links. Aliases share observations.']
    for cid in concerns:
        for mid in membership[cid]['moe_ids']:
            cn, mn = identifier(cid), identifier(mid)
            edges.append(f'    #qualitativeContribution dependency contribution_{cn}_{mn} from {cn} to FrameworkNeeds::{mn};')
    edges.append(NATIVE_END)
    assert native.rstrip().endswith('}'), 'Missing native package terminator'
    end = native.rfind('\n}')
    native = native[:end].rstrip() + '\n\n' + '\n'.join(edges) + '\n}\n'
    native_path.write_text(native)
    refresh_report_table(root, record)
    docs = dict(re.findall(r"item <'(MOE-\d{2})'> \w+ : EffectivenessMeasure \{\s*doc /\* (.*?) \*/",
                           (root/'sysml/02-needs-context.sysml').read_text(), re.DOTALL))
    assert set(docs) == MOES, 'Native MOE definition set mismatch'
    old_moes = audit.unique(baseline['measures_of_effectiveness'], 'baseline MOE')
    baseline['measures_of_effectiveness'] = []
    for mid in sorted(MOES):
        c = dict(old_moes.get(mid, {'id': mid, 'achieved': 'unknown', 'target': 'TBR, stakeholder agreement pending'}))
        c.update(observation_basis=docs[mid], concern_ids=[cid for cid in concerns if mid in membership[cid]['moe_ids']])
        baseline['measures_of_effectiveness'].append(c)
    baseline['concern_moe_coverage'] = {'ledger': LEDGER, 'counts': counts(concerns, membership), 'interpretation': record['interpretation']}
    # Only refresh identities for this focused revision; never relabel old stage
    # checks/historical snapshots as checks of the changed native source.
    paths = ['needs.tex', REPORT_TABLE, 'main.tex', 'sty/framework-report.tex',
             'sysml/01-concerns.sysml', 'sysml/02-needs-context.sysml', LEDGER,
             'tools/check_concern_coverage.py', 'tools/test_concern_coverage.py',
             'tools/audit_report.py', 'tools/test_audit_report.py']
    for path in paths:
        if (root/path).exists():
            baseline['current_source_sha256'][path] = audit.sha(root/path)
    baseline_path.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + '\n')


def check(root):
    record, concerns, membership = authored(root)
    baseline = audit.load(root/'traceability/framework-baseline.json')
    ledger = audit.unique(baseline['concerns'], 'baseline concern')
    native = (root/'sysml/01-concerns.sysml').read_text()
    native_concerns = dict(re.findall(r"concern <'([^']+)'> \w+ \{[^\n]*doc /\* (.*?) \*/", native))
    assert set(native_concerns) == set(concerns) == set(ledger), 'Concern occurrence mismatch'
    dispositions = audit.annotations(native, 'CurrentDisposition', r'C_\w+')
    sources = audit.annotations(native, 'SourceRecord', r'C_\w+')
    assert set(dispositions) == set(sources) == {identifier(cid) for cid in concerns}, 'Native metadata occurrence mismatch'
    for cid, row in concerns.items():
        c = ledger[cid]; group = membership[cid]; cn = identifier(cid)
        assert all(c.get(k) == v for k, v in row.items()) and native_concerns[cid] == row['text'], f'Changed concern assertion/hierarchy: {cid}'
        assert c['moe_ids'] == group['moe_ids'] and c['moe_contribution_group'] == group['id'], f'Concern/MOE ledger mismatch: {cid}'
        assert c['disposition'] == group['interpretation'], f'Concern interpretation mismatch: {cid}'
        assert dispositions[cn] == {'scopeStatus': c['scope_status'], 'disposition': c['disposition'],
                                    'moeIdentifiers': ','.join(c['moe_ids'])}, f'Native disposition mismatch: {cid}'
        assert f'final_report/apendice.tex#{cid}' in sources[cn]['sourceLocator'], f'Invalid source locator: {cid}'
        if row['parent']:
            assert f'dependency causal_{cn} from {cn} to {identifier(row["parent"])};' in native, f'Missing native causal link: {cid}'
        if row['alias_target']:
            assert f'dependency alias_{cn} from {cn} to {identifier(row["alias_target"])};' in native, f'Missing native alias link: {cid}'
    report = report_table(root)
    check_report_link_commands(root)
    expected_display = {(cid, mid) for cid in concerns for mid in membership[cid]['moe_ids']}
    display = check_forward_table(report, concerns, expected_display)
    assert report == table(record), 'Report concern/MOE table mismatch'
    display.update(source=REPORT_TABLE, table_label=TABLE_LABEL, appendix_label=APPENDIX_LABEL,
                   linked_concern_destinations=len(concerns))
    edges = re.findall(r'#qualitativeContribution dependency \w+ from (C_\w+) to FrameworkNeeds::(MOE_\d{2});', native)
    expected = {(identifier(cid), identifier(mid)) for cid in concerns for mid in membership[cid]['moe_ids']}
    assert len(edges) == len(set(edges)) and set(edges) == expected, 'Native concern/MOE edge mismatch'
    needs = (root/'sysml/02-needs-context.sysml').read_text()
    assert not re.search(r'#qualitativeContribution dependency \w+ from FrameworkConcerns::', needs), 'Duplicate partial concern inventory'
    moes = audit.audit_moes(root, baseline['measures_of_effectiveness'])
    for mid, row in moes.items():
        assert row['concern_ids'] == [cid for cid in concerns if mid in membership[cid]['moe_ids']], f'MOE inverse ledger mismatch: {mid}'
        assert f'dependency effectiveness_MOE{mid[-2:]} from {identifier(mid)} to ToBe::EPSEngineeringEnterprise;' in needs, f'Missing enterprise effectiveness link: {mid}'
    actual_counts = counts(concerns, membership)
    assert baseline['concern_moe_coverage']['counts'] == actual_counts, 'Concern coverage count mismatch'
    return {'valid': True, 'scope': 'Focused specification consistency. No empirical V&V or excluded work.',
            'counts': actual_counts, 'display': display, 'concern_to_moe': {cid: membership[cid]['moe_ids'] for cid in concerns},
            'moe_to_concern': {mid: [cid for cid in concerns if mid in membership[cid]['moe_ids']] for mid in sorted(MOES)},
            'concerns': [{'id': cid, 'parent': c['parent'], 'alias_target': c['alias_target'],
                          'moe_ids': membership[cid]['moe_ids'], 'group': membership[cid]['id'],
                          'scope_status': ledger[cid]['scope_status'], 'interpretation': membership[cid]['interpretation']}
                         for cid, c in concerns.items()],
            'unmapped_concern_ids': [], 'new_moe_ids': ['MOE-05', 'MOE-06']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[1])
    refresh_options = parser.add_mutually_exclusive_group()
    refresh_options.add_argument('--refresh', action='store_true')
    refresh_options.add_argument('--refresh-table', action='store_true', help='Regenerate only the appendix table')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if args.refresh:
            refresh(args.report)
        elif args.refresh_table:
            record, _, _ = authored(args.report)
            refresh_report_table(args.report, record)
        result = check(args.report)
    except (AssertionError, KeyError, ValueError, OSError) as error:
        print(json.dumps({'valid': False, 'error': str(error)})); return 1
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'valid': result['valid'], 'counts': result['counts'], 'new_moe_ids': result['new_moe_ids']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
