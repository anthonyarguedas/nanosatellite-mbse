#!/usr/bin/env python3
"""Audit the current proposed specification. This never certifies empirical V&V.

Report tables and native statements are authoritative. Historical reviews are
checked as historical evidence, not renewed by replacing their source hashes.
Detailed logical/physical contracts must be reconciled before a full audit can
pass. No obsolete logical operation or selected deployment is required.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ACTIVE_FR = {f'FR-{n:02}' for n in range(1, 43) if n not in (12, 40)}
GROUPS = {
    'L01': {1, 2, 3, 4, 17, 29, 39, 41},
    'L02': {13, 14, 15, 20, 25, 33, 35},
    'L03': {10, 16, 18, 19, 23, 24, 26, 27, 34, 36},
    'L04': {21, 22, 31, 32},
    'L05': {11, 28, 37, 38, 42},
    'L06': {5, 6, 7, 8, 9, 30},
}
OWNERS = {f'FR-{n:02}': lid for lid, ns in GROUPS.items() for n in ns}
CANDIDATES = {
    'PA-COM': ('comet', 'CandidateCOM', 'COM'),
    'PA-VS': ('valispace', 'CandidateVS', 'VS'),
    'PA-NS': ('nanospace', 'CandidateNS', 'NS'),
    'PA-GY': ('git-yaml', 'CandidateGY', 'GY'),
    'PA-CDT': ('custom', 'CandidateCDT', 'CDT'),
}
CRITICAL_MOPS = ('MOP-FR02', 'MOP-FR03', 'MOP-FR18', 'MOP-FR34', 'MOP-FR30', 'MOP-FR10')
# Reviewed, scoped proposals only. This guard rejects unsourced additions and
# changes of basis. These strings repeat the report/native specification, not
# achieved performance or a generic acceptance rule for composite measures.
MOP_TARGETS = {
    'MOP-FR07': (r'$\leq 20$~s (indexed lookup)', r'\citep[Sec.~2, RQ-4]{kanavouras2024lightweight}'),
    'MOP-FR18': (r'100\% (lossless profiles)', r'\citep[Sec.~3.6.4]{citation-2300}'),
    'MOP-FR20': (r'$\leq 0.0005$ W, Wh, m\textsuperscript{2} (fixture only)', r'\citep[Table~III]{review-0764}'),
    'MOP-FR34': (r'100\% (architecture maps)', r'\citep[Sec.~3, p.~7]{review-0853}'),
}
ALTERNATIVE_KEYS = {
    'L01': ('deutsch2022comet', 'citation-4690', 'review-0340', 'chiu2023sealion', 'kaslow2019csrm'),
    'L02': ('kaslow2019csrm', 'deutsch2022comet', 'review-0711', 'review-0289', 'review-0573'),
    'L03': ('review-0853', 'handpicked-0001', 'handpicked-0002', 'review-0289', 'review-0573'),
    'L04': ('review-0573', 'handpicked-0001', 'review-1251', 'review-1303', 'kaslow2019csrm'),
    'L05': ('chiu2023sealion', 'citation-0569', 'review-0340', 'deutsch2022comet', 'citation-1573'),
    'L06': ('chiu2023sealion', 'citation-0569', 'review-0340', 'deutsch2022comet', 'citation-1573'),
}
FAMILIES = dict(zip(GROUPS, ('AR', 'EP', 'IN', 'CR', 'EC', 'EC')))
# Approved design choices, not achieved performance or a preference ordering.
COMPOSITION = {
    'PA-COM': ('AR1', 'EP2+EP3', 'IN1+IN2', 'CR1+CR5', 'EC4+EC2', 'EC4+EC1'),
    'PA-VS': ('AR2', 'EP5', 'IN1+IN5', 'CR1+CR2', 'EC5+EC2', 'EC5+EC1'),
    'PA-NS': ('AR3', 'EP4', 'IN1+IN4', 'CR3+CR4', 'EC3+EC2', 'EC3+EC1'),
    'PA-GY': ('AR4+AR5', 'EP1+EP3', 'IN1+IN3', 'CR4+CR5', 'EC1+EC2', 'EC1+EC2'),
    'PA-CDT': ('Native+Jev', 'Param.+Python+DB', 'Python+IN1+IN2', 'Python+CR1+CR5', 'Python+EC2', 'Native+EC1'),
}
CUSTOM_ROLES = {'native_requirements', 'native_parametrics', 'jev_recommendations',
                'python_execution', 'maintained_cots_database'}
PROCEDURE_FIELDS = ('subject', 'configuration', 'prerequisites', 'procedure',
                    'stimulus_conditions', 'expected_response',
                    'criteria_comparison_basis', 'retained_evidence')
PUBLISHED_API_SCHEMA = 'task7-published-logical-api-v1'
BRIDGED_API_STATUS = 'published logical API bridged, physical allocation/control reconciliation incomplete'


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evidence_digest(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def unique(records, label, key='id'):
    result = {record[key]: record for record in records}
    assert len(result) == len(records), f'Duplicate {label} IDs'
    return result


def visible(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)


def group(text, start):
    """Read a balanced TeX brace group, including nested citations."""
    assert text[start] == '{', 'Expected brace group'
    depth = 0
    for end in range(start, len(text)):
        if text[end] in '{}' and (end == 0 or text[end - 1] != '\\'):
            depth += 1 if text[end] == '{' else -1
            if depth == 0:
                return text[start + 1:end], end + 1
    raise AssertionError('Unclosed TeX group')


def number_set(text, prefix):
    result = set()
    for match in re.finditer(rf'\b{re.escape(prefix)}(\d{{2}})(?:--(?:{re.escape(prefix)})?(\d{{2}}))?', text):
        first, last = int(match[1]), int(match[2] or match[1])
        assert last >= first, f'Invalid {prefix} range: {match[0]}'
        result.update(f'{prefix}{n:02}' for n in range(first, last + 1))
    return result


def bare_numbers(text, prefix):
    text = text.strip()
    assert re.fullmatch(r'\d{2}(?:--\d{2})?(?:\s*,\s*\d{2}(?:--\d{2})?)*', text), f'Invalid {prefix} numbers: {text}'
    return number_set(re.sub(r'(?<!\d)(\d{2})', prefix + r'\1', text), prefix)


def table_cells(text):
    """Split unescaped top-level ampersands. Empty cells remain literally empty."""
    cells, begin, depth = [], 0, 0
    for n, char in enumerate(text):
        escaped = n > 0 and text[n - 1] == '\\'
        if not escaped and char in '{}':
            depth += 1 if char == '{' else -1
        if char == '&' and not escaped and depth == 0:
            cells.append(text[begin:n].strip()); begin = n + 1
    assert depth == 0, 'Unbalanced table braces'
    return cells + [text[begin:].strip()]


def table_rows(text, start_pattern):
    text = visible(text)
    pattern = rf'(?m)^\s*({start_pattern})(?=\s|\\|&)(.*?)\\\\\*?[ \t]*(?:\n|$)'
    return [table_cells(m[1] + m[2]) for m in re.finditer(pattern, text, re.DOTALL)]


def parse_concerns(path):
    text = Path(path).read_text(); records = []
    for match in re.finditer(r'\\Concern(Root|Cause)\{([^}]+)\}', text):
        statement, end = group(text, match.end())
        cid = match[2]; alias = re.match(r'\\ConcernAliasLink\{([^}]+)\}', text[end:])
        records.append({'id': cid, 'kind': match[1].lower(), 'text': statement,
                        'parent': cid.rsplit('.', 1)[0] if '.' in cid else None,
                        'alias_target': alias[1] if alias else None,
                        'source_line': text.count('\n', 0, match.start()) + 1})
    unique(records, 'concern occurrence')
    return records


def native_statements(text, prefix):
    pattern = rf"requirement <'({prefix}-\d{{2}})'> \w+ \{{\s*subject[^;]+;\s*doc /\* (.*?) \*/"
    return unique([{'id': m[1], 'text': m[2]} for m in re.finditer(pattern, text, re.DOTALL)], f'native {prefix}')


def string_attributes(text):
    return {k: json.loads(v) for k, v in re.findall(r'(\w+)\s*(?:\:\s*(?!>)[\w:]+)?\s*(?:default\s*)?=\s*("(?:[^"\\]|\\.)*")\s*;', text)}


def native_block(text, start):
    """Balanced native body, excluding braces inside escaped string literals."""
    assert text[start] == '{', 'Expected native body'
    depth, quoted, escaped = 0, False, False
    for n in range(start, len(text)):
        char = text[n]
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{}':
            depth += 1 if char == '{' else -1
            if depth == 0:
                return text[start + 1:n]
    raise AssertionError('Unclosed native body')


def annotations(text, name, about):
    rows = [(m[1], string_attributes(native_block(text, m.end() - 1))) for m in re.finditer(
        rf'@{name}\s+about\s+({about})\s*\{{', text)]
    assert len({k for k, _ in rows}) == len(rows), f'Duplicate {name} annotation'
    return dict(rows)


def parse_fr_rationale(cell):
    match = re.fullmatch(r'([^\\]+)\.\\par\s*(.+)', cell, re.DOTALL)
    assert match, 'Missing FR parent references or rationale'
    parents = []
    for term in match[1].split(','):
        bounds = re.fullmatch(r'MR-(\d{2})(?:--(?:MR-)?(\d{2}))?', term.strip())
        assert bounds, 'Malformed FR parent references'
        first, last = int(bounds[1]), int(bounds[2] or bounds[1])
        assert last >= first, 'Reversed FR parent range'
        parents.extend(f'MR-{n:02}' for n in range(first, last + 1))
    assert len(parents) == len(set(parents)), 'Duplicate FR parent reference'
    rationale = match[2].strip()
    citation_pattern = r'\\citep(?:\[[^]]+\])\{([^}]+)\}'
    citations = [key.strip() for cited in re.findall(citation_pattern, rationale) for key in cited.split(',')]
    prose = re.sub(citation_pattern, '', rationale).strip(' .')
    assert prose and citations, 'Missing FR rationale or locator citation'
    assert not re.search(r'\\citep(?!\[)', rationale), 'FR citations require source locators'
    return {'parents': sorted(parents), 'rationale': rationale,
            'rationale_cell': cell, 'rationale_citations': citations}


def audit_requirement_headers(root):
    for path, middle in (('needs.tex', 'Enterprise mission requirement'),
                         ('requirements.tex', 'System requirement')):
        header = r'\textbf{ID} & \textbf{' + middle + r'} & \textbf{Rationale}'
        assert visible((root/path).read_text()).count(header) == 2, 'MR/FR initial and repeated headers must use ID and Rationale'


def audit_fr_rationales(root, fr, records=None):
    authored = load(root/'traceability/fr-rationale.json')
    rows = unique(authored['requirements'], 'authored FR rationale')
    assert set(rows) == set(fr) == ACTIVE_FR, 'Complete 40-FR rationale coverage required'
    bibliography = (root/'literatura.bib').read_text()
    keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', bibliography)
    assert len(keys) == len(set(keys)), 'Duplicate bibliography key'
    parents = 0
    for rid, row in rows.items():
        published = fr[rid]
        assert row['parent_mrs'] == published['parents'], f'Authored rationale parent mismatch: {rid}'
        assert row['rationale_latex'] == published['rationale_cell'], f'Authored rationale display mismatch: {rid}'
        assert row['rationale_text'].strip() and row['citations'], f'Empty authored rationale: {rid}'
        cited = {citation['key'] for citation in row['citations']}
        assert set(published['rationale_citations']) == cited <= set(keys), f'FR rationale citation key mismatch: {rid}'
        assert all(c.get('locator') and c.get('supporting_passage') and c.get('transfer_limit') for c in row['citations']), f'Missing checked source basis or transfer limit: {rid}'
        parents += len(row['parent_mrs'])
    assert parents == 169, 'Exactly 169 rationale parent links required'
    if records is not None:
        ledger = unique(records, 'ledger FR rationale')
        for rid, row in rows.items():
            assert ledger[rid].get('rationale') == fr[rid]['rationale'] and ledger[rid].get('rationale_citations') == fr[rid]['rationale_citations'], f'FR rationale ledger mismatch: {rid}'
    return {'requirements': len(rows), 'direct_parents': parents,
            'source_citations': sum(len(r['citations']) for r in rows.values()),
            'el_hachimi_context_rows': sum('handpicked-0003' in fr[r]['rationale_citations'] for r in rows)}


FR_IO_SOURCE = 'fr-inputs-outputs.tex'
FR_TABLE_GROUPS = (
    'Requirements and explained assistance', 'Mission concepts and preliminary design',
    'Simulation and model credibility', 'Detailed interfaces and host software',
    'Evidence, controlled changes and reviews',
)


def parse_fr_tables(requirements_text, io_text):
    """Join the two published FR tables by exact, unique ID. Preserve cell text."""
    main, appendix = visible(requirements_text), visible(io_text)
    header = r'\textbf{ID} & \textbf{System requirement} & \textbf{Rationale}'
    assert sum(line.strip() == header + r' \\' for line in main.splitlines()) == 2, 'FR initial and repeated headers must use ID and Rationale'
    io_header = r'\textbf{ID} & \textbf{Inputs} & \textbf{Outputs}'
    assert sum(line.strip() == io_header + r' \\' for line in appendix.splitlines()) == 2, 'FR IO initial and repeated headers must use ID, Inputs, Outputs'
    for text, label in ((main, 'tab:framework-requirements'), (appendix, 'tab:framework-io'),
                        (appendix, 'appendix:framework-io')):
        assert text.count(r'\label{' + label + '}') == 1, f'Missing/duplicate FR table label: {label}'
    assert r'\ref{tab:framework-io}' in main and r'\ref{appendix:framework-io}' in main, 'Missing main FR IO appendix reference'
    assert r'\ref{tab:framework-requirements}' in appendix, 'Missing FR IO reference to main requirements'
    assert not re.search(r'\\textit\{(?:Inputs|Outputs):\}', main), 'Remaining body FR IO duplication'
    rows, io_rows = [], []
    id_pattern = r'[^\s&\\]+\s*&'
    for cells in table_rows(main, id_pattern):
        assert len(cells) == 3 and cells[1], 'Malformed concise FR table row'
        rows.append({'id': cells[0], 'text': cells[1], **parse_fr_rationale(cells[2])})
    for cells in table_rows(appendix, id_pattern):
        assert len(cells) == 3 and all(cells), 'Missing FR IO or malformed appendix row'
        io_rows.append({'id': cells[0], 'inputs': cells[1], 'outputs': cells[2]})
    fr, io = unique(rows, 'report FR'), unique(io_rows, 'appendix FR IO')
    assert set(fr) == set(io) == ACTIVE_FR, 'FR main/appendix active ID mismatch (absent or extra ID)'

    def groups(text, label):
        table = text.split(r'\label{' + label + '}', 1)[1].split(r'\end{longtable}', 1)[0]
        pattern = r'\\multicolumn\{3\}\{@\{\}l\}\{\\textbf\{([^}]+)\}\}'
        parts = re.split(pattern, table)
        return [(parts[n], [r[0] for r in table_rows(parts[n + 1], id_pattern)])
                for n in range(1, len(parts), 2)]

    main_groups = groups(main, 'tab:framework-requirements')
    assert tuple(name for name, _ in main_groups) == FR_TABLE_GROUPS, 'Changed FR groups'
    assert groups(appendix, 'tab:framework-io') == main_groups, 'FR IO group/order mismatch'
    body = ' '.join(main.split())
    for rid, row in fr.items():
        row.update(inputs=io[rid]['inputs'], outputs=io[rid]['outputs'])
        for direction in ('inputs', 'outputs'):
            assert ' '.join(row[direction].split()) not in body, f'Remaining body FR IO duplication: {rid} {direction}'
    return fr


def audit_io_body(root, fr):
    for path in root.glob('*.tex'):
        if path.name in ('apendice.tex', FR_IO_SOURCE):
            continue
        text = ' '.join(visible(path.read_text()).split())
        for rid, row in fr.items():
            for direction in ('inputs', 'outputs'):
                assert ' '.join(row[direction].split()) not in text, f'Remaining body FR IO duplication: {rid} {direction} in {path.name}'


def report_requirements(root):
    audit_requirement_headers(root)
    mr = []
    for cells in table_rows((root/'needs.tex').read_text(), r'MR-\d{2}'):
        assert len(cells) == 3, 'Malformed concise MR table row'
        mr.append({'id': cells[0], 'text': cells[1]})
    fr = parse_fr_tables((root/'requirements.tex').read_text(), (root/FR_IO_SOURCE).read_text())
    assert visible((root/'apendice.tex').read_text()).count(r'\input{fr-inputs-outputs}') == 1, 'FR IO appendix fragment must be included exactly once'
    audit_io_body(root, fr)
    assert mr, 'No concise report mission requirement rows found'
    return unique(mr, 'report MR'), fr


def current_trace(root):
    mr, fr = report_requirements(root)
    nt = (root/'sysml/03-requirements.sysml').read_text()
    needs = (root/'sysml/02-needs-context.sysml').read_text()
    assert mr == native_statements(needs, 'MR'), 'MR report/native statement or ID mismatch'
    nf = native_statements(nt, 'FR')
    assert set(fr) == set(nf) == ACTIVE_FR, 'FR report/native active ID mismatch'
    ledger_fr = unique(load(root/'traceability/framework-baseline.json')['framework_requirements'], 'ledger FR')
    assert set(ledger_fr) == set(fr), 'FR ledger active ID mismatch'
    for rid, row in fr.items():
        for direction in ('inputs', 'outputs'):
            assert row[direction] == ledger_fr[rid][direction], f'FR ledger IO mismatch: {rid} {direction}'
    assert set(mr) == {f'MR-{n:02}' for n in range(1, 7)}, 'Exactly six mission gates required'
    gates = ('MCR', 'SRR', 'MDR/SDR', 'PDR', 'CDR', 'SIR')
    for mid, gate in zip(sorted(mr), gates):
        present = re.findall(r'\b(?:MCR|SRR|MDR/SDR|PDR|CDR|SIR)\b', mr[mid]['text'])
        assert present == [gate], f'MR gate uniqueness mismatch: {mid}'
    derivations, scenarios, functions = defaultdict(set), defaultdict(set), defaultdict(set)
    derivation_rows = re.findall(r'connection derive_MR_(\d+)_FR_(\d+) \{ end #original ::> FrameworkNeeds::MR_(\d+); end #derive ::> FR_(\d+);', nt)
    assert len(derivation_rows) == 169 and len(set(derivation_rows)) == 169, 'Exactly 169 unique direct FR parents required'
    for a, b, c, d in derivation_rows:
        assert (a, b) == (c, d), 'Derivation identifier/endpoint mismatch'
        derivations['FR-' + b].add('MR-' + a)
    for f, s in re.findall(r'dependency scenario_FR\d+_SC\d+ from FR_(\d+) to ScenarioViews::(SC\d+);', nt):
        scenarios['FR-' + f].add(s)
    for f, b in re.findall(r'dependency function_FR\d+_F\d+ from FR_(\d+) to BoundaryViews::(F\d+);', nt):
        functions['FR-' + f].add(b)
    checks = annotations(nt, 'PlannedRequirementCheck', r'FR_\d{2}')
    assert set(checks) == {r.replace('-', '_') for r in fr}, 'Missing/extra native FR planned check'
    for rid, row in fr.items():
        assert row['text'] == nf[rid]['text'], f'FR wording mismatch: {rid}'
        assert set(row['parents']) == derivations[rid] <= set(mr), f'MR/FR derivation mismatch: {rid}'
        assert scenarios[rid] and functions[rid], f'Missing FR scenario/function endpoints: {rid}'
        check = checks[rid.replace('-', '_')]
        assert check['checkSummary'] and re.fullmatch(r'[IADT](?:,[IADT])*', check['methods']), f'Invalid planned check: {rid}'
        row.update(methods=check['methods'].split(','), planned_check=check['methods'] + ': ' + check['checkSummary'],
                   scenarios=sorted(scenarios[rid]), functions=sorted(functions[rid]))
    sc = (root/'sysml/09-scenarios.sysml').read_text()
    ucs = set(re.findall(r"use case <'(UC\d+)'>", needs))
    scs = set(re.findall(r"action def <'(SC\d+)'>", sc))
    uc_mrs, sc_mrs, sc_ucs = defaultdict(set), defaultdict(set), defaultdict(set)
    for u, m in re.findall(r'dependency refine_UC\d+_MR\d+ from (UC\d+) to MR_(\d+);', needs):
        uc_mrs[u].add('MR-' + m)
    for s, m in re.findall(r'dependency scenario_SC\d+_MR\d+ from (SC\d+) to FrameworkNeeds::MR_(\d+);', sc):
        sc_mrs[s].add('MR-' + m)
    for s, u in re.findall(r'dependency scenario_UC\d+ from (SC\d+) to FrameworkNeeds::(UC\d+);', sc):
        sc_ucs[s].add(u)
    assert ucs == set(uc_mrs) and scs == set(sc_mrs) == set(sc_ucs), 'UC/SC endpoint set mismatch'
    assert ucs == {f'UC{n:02}' for n in range(1, 6)} and scs == {f'SC{n:02}' for n in range(1, 6)}, 'Five current UC/SC subjects required'
    # The concise audience section need not repeat the native scenario inventory.
    # Any identifiers it does publish must still resolve.
    assert number_set(visible((root/'needs.tex').read_text()), 'UC') <= ucs, 'Unknown report UC'
    assert number_set(visible((root/'requirements.tex').read_text()), 'SC') <= scs, 'Unknown report SC'
    for s in scs:
        assert len(sc_ucs[s]) == 1 and sc_ucs[s] <= ucs, f'Missing/unknown UC: {s}'
        assert sc_mrs[s] == uc_mrs[next(iter(sc_ucs[s]))], f'Scenario/UC MR disagreement: {s}'
    assert set().union(*uc_mrs.values()) == set(mr), 'MR without a use case'
    for rid, row in fr.items():
        assert set(row['scenarios']) <= scs, f'Unknown scenario: {rid}'
        assert set(row['parents']) <= set().union(*(sc_mrs[s] for s in row['scenarios'])), f'No MR/SC/FR path: {rid}'
    return mr, fr, ucs, scs, uc_mrs, sc_mrs, sc_ucs


def report_moe_definitions(root):
    text = visible((root/'needs.tex').read_text())
    rows = [row for row in table_rows(text, r'MOE-\d{2}') if len(row) == 2]
    definitions = []
    for cell, definition in rows:
        match = re.fullmatch(r'(MOE-\d{2})\\phantomsection\\label\{moe:\1\}', cell)
        assert match, 'Missing or mismatched MOE definition anchor'
        definitions.append({'id': match[1], 'definition': definition})
    result = unique(definitions, 'MOE definition')
    labels = re.findall(r'\\label\{moe:(MOE-\d{2})\}', text)
    assert len(labels) == len(set(labels)) == len(result) and set(labels) == set(result), 'Duplicate or misplaced MOE anchor'
    return {mid: row['definition'] for mid, row in result.items()}


def audit_mop_order(text):
    text = visible(text)
    heading = r'\subsection{Measures of performance}'
    assert text.count(heading) == text.count(r'\label{subsection:framework-mops}') == 1, 'Missing or duplicate MOP subsection'
    requirement_table = text.index(r'\label{tab:framework-requirements}')
    end = text.index(r'\end{longtable}', requirement_table)
    assert end < text.index(heading) < text.index(r'\label{tab:framework-mop-protocols}'), 'MOP subsection must follow the complete FR table'


def audit_mops(root, fr, records=None):
    rows = []
    text = (root/'requirements.tex').read_text()
    audit_mop_order(text)
    moes = report_moe_definitions(root)
    for cells in table_rows(text, r'FR-\d{2}\\newline\s+MOP-FR\d{2}'):
        assert len(cells) == 4, 'Malformed MOP row'
        rid, mid = re.fullmatch(r'(FR-\d{2})\\newline\s+(MOP-FR\d{2})', cells[0]).groups()
        assert rid[-2:] == mid[-2:], 'MOP/FR identity mismatch'
        assert cells[1], f'Missing MOP definition: {mid}'
        target, source = MOP_TARGETS.get(mid, ('', ''))
        expected_cell = target + r'\newline ' + source if target else ''
        if not target:
            assert cells[2] == '', f'Unsupported desired MOP range must be literally empty: {mid}'
        else:
            assert cells[2] == expected_cell, f'Unsupported or unsourced desired MOP range: {mid}'
            keys = re.findall(r'\\citep(?:\[[^]]*\])*\{([^}]+)\}', source)
            bibliography = (root/'literatura.bib').read_text()
            assert keys and all(re.search(r'@\w+\s*\{\s*' + re.escape(k) + r'\s*,', bibliography) for k in keys), f'Missing MOP target citation: {mid}'
        links = re.findall(r'\\hyperref\[moe:(MOE-\d{2})\]\{\1\}', cells[3])
        assert links and cells[3] == r'\newline '.join(r'\hyperref[moe:' + e + ']{' + e + '}' for e in links), f'Missing or malformed MOP/MOE link: {mid}'
        assert len(links) == len(set(links)), f'Duplicate MOP/MOE link: {mid}'
        assert set(links) <= set(moes), f'Unknown report MOP/MOE endpoint: {mid}'
        rows.append({'id': mid, 'FR': rid, 'definition_and_unit': cells[1], 'target': target, 'target_source': source, 'achieved': 'unknown', 'moe_ids': sorted(links)})
    measures = unique(rows, 'report MOP')
    assert {r['FR'] for r in rows} == set(fr) and len(rows) == 40, 'Exact per-FR MOP coverage required'
    nt = (root/'sysml/03-requirements.sysml').read_text()
    blocks = list(re.finditer(r"item <'(MOP-FR\d{2})'> (MOP_FR\d{2}) : PerformanceMeasure \{(.*?)\n    \}", nt, re.DOTALL))
    assert len(blocks) == 40 and {m[1] for m in blocks} == set(measures), 'Native MOP coverage mismatch'
    type_block = re.search(r'item def PerformanceMeasure\b(.*?)\n    \}', nt, re.DOTALL)
    defaults = string_attributes(type_block[1])
    assert defaults['target'] == defaults['targetSource'] == '' and defaults['achieved'] == 'unknown, no empirical evaluation', 'False native target/achieved default'
    for m in blocks:
        assert m[2] == m[1].replace('-', '_'), 'Native MOP identity mismatch'
        attrs = string_attributes(m[3])
        assert all(attrs.get(f) for f in ('observationBasis', 'units', 'protocol', 'referenceConfiguration')), f'Incomplete native MOP protocol: {m[1]}'
        assert attrs.get('target', '') == measures[m[1]]['target'] and attrs.get('targetSource', '') == measures[m[1]]['target_source'] and attrs.get('achieved', defaults['achieved']) == defaults['achieved'], 'False native MOP result/target'
        measures[m[1]]['native_protocol'] = attrs
    edges = re.findall(r'dependency MOPFR\d+_FR\d+ from (MOP_FR\d{2}) to (FR_\d{2});', nt)
    expected = {(mid.replace('-', '_'), row['FR'].replace('-', '_')) for mid, row in measures.items()}
    assert len(edges) == 40 and set(edges) == expected, 'Native MOP/FR dependency mismatch'
    contributions = re.findall(r'#qualitativeContribution dependency MOPFR\d+_MOE\d+ from (MOP_FR\d{2}) to FrameworkNeeds::(MOE_\d{2});', nt)
    assert len(contributions) == len(set(contributions)) == 74, 'Exactly 74 qualitative MOP/MOE contributions required'
    assert all(m.replace('_', '-') in measures and e.replace('_', '-') in moes for m, e in contributions), 'Unknown qualitative MOP/MOE endpoint'
    for mid, row in measures.items():
        native_moes = sorted(e.replace('_', '-') for m, e in contributions if m == mid.replace('-', '_'))
        assert native_moes and row['moe_ids'] == native_moes, f'Report/native MOP/MOE contribution mismatch: {mid}'
    if records is not None:
        ledger = unique(records, 'ledger MOP')
        assert set(ledger) == set(measures), 'MOP ledger coverage mismatch'
        for mid, row in measures.items():
            assert all(ledger[mid].get(k) == v for k, v in row.items()), f'MOP ledger mismatch: {mid}'
            evidence = ledger[mid].get('target_evidence')
            if mid in MOP_TARGETS:
                source_keys = re.findall(r'\\citep(?:\[[^]]*\])*\{([^}]+)\}', row['target_source'])
                assert evidence and evidence.get('status') == 'proposed, not qualified' and evidence.get('kind') in {'derived engineering interpretation of literature recommendation', 'derived benchmark reference band'} and evidence.get('sources') == source_keys and all(evidence.get(k) for k in ('locator', 'source_claim', 'transfer_limit')), f'Unsupported MOP target evidence: {mid}'
            else:
                assert not evidence, f'Unsupported MOP target evidence: {mid}'
    return measures


def assert_neutral(record):
    """Reject current selection fields recursively. Historical snapshots are separate."""
    forbidden = {'preferred', 'winner', 'principal_alternative', 'priorities', 'selected_candidate', 'physical_direction', 'reversal'}
    if isinstance(record, dict):
        assert not (forbidden & set(record)), 'Current winner/priority/selected claim'
        for k, v in record.items():
            if k != 'historical_evidence':
                assert_neutral(v)
    elif isinstance(record, list):
        for v in record:
            assert_neutral(v)
    elif isinstance(record, str):
        assert not re.search(r'recommends developing|preferred (?:candidate|direction|deployment)|reuse-first priority|principal alternative|priority ordering|PA-\w+ is (?:the )?(?:winner|preferred|selected)', record, re.I), 'Current winner/priority/selected claim'


def audit_moes(root, records):
    rows = list(report_moe_definitions(root).items())
    assert len(rows) == 6 and {row[0] for row in rows} == {f'MOE-{n:02}' for n in range(1, 7)}, 'Six concise MOE definitions required'
    ledger = unique(records, 'MOE')
    assert set(ledger) == {row[0] for row in rows}, 'MOE report/ledger coverage mismatch'
    native = (root/'sysml/02-needs-context.sysml').read_text()
    docs = dict(re.findall(r"item <'(MOE-\d{2})'> \w+ : EffectivenessMeasure \{\s*doc /\* (.*?) \*/", native, re.DOTALL))
    assert set(docs) == set(ledger), 'MOE native coverage mismatch'
    for mid, definition in rows:
        assert ledger[mid]['observation_basis'] == docs[mid] == definition and ledger[mid]['achieved'] == 'unknown', 'MOE wording or measured outcome mismatch'
    assert not re.search(r'cost|CAD|price|affordability', ledger['MOE-04']['observation_basis'], re.I), 'Financial MOE reintroduced'
    return ledger


def expected_alternatives():
    return {f'{lid}.{FAMILIES[lid]}{n}': key for lid, keys in ALTERNATIVE_KEYS.items() for n, key in enumerate(keys, 1)}


def audit_candidate_records(root, fr, logical=None, require_native=False):
    trade = load(root/'traceability/trade-study.json'); assert_neutral(trade)
    assert trade['candidate_ids'] == list(CANDIDATES), 'Four literature candidates plus custom required'
    alternatives = unique(trade['alternatives'], 'scoped alternative')
    assert set(alternatives) == set(expected_alternatives()), 'Exactly five scoped alternatives per L required'
    for aid, key in expected_alternatives().items():
        a = alternatives[aid]
        assert a['logical'] == aid[:3] and a['citation'] == key and a['supported_subset'] and a['required_additions'], f'Alternative scope/source mismatch: {aid}'
    candidates = {}
    assert {p.stem for p in (root/'candidates').glob('*.json')} == {c[0] for c in CANDIDATES.values()}, 'Candidate source set mismatch'
    logical_rows = unique(logical['allocations'], 'logical allocation', 'FR') if logical is not None else None
    published = None
    for cid, (file, pkg, prefix) in CANDIDATES.items():
        record = load(root/f'candidates/{file}.json'); assert_neutral(record)
        assert record['id'] == cid and record['native'] == pkg + '::candidate', 'Candidate identity mismatch'
        assert record['numerical_results'] is None and record['achieved'] == 'unknown' and record['empirical_vv_executed'] is False, 'Invented candidate outcome'
        components = unique(record['components'], 'physical component')
        assert set(components) == {f'{prefix}-C{n:02}' for n in range(1, 7)}, 'Six physical C01-C06 components required'
        by_l = {c['logical']: c for c in components.values()}
        assert set(by_l) == set(GROUPS), 'Candidate logical coverage mismatch'
        for n, (lid, choice) in enumerate(zip(GROUPS, COMPOSITION[cid]), 1):
            c = by_l[lid]
            assert c['id'] == f'{prefix}-C{n:02}' and c['type'] == f'{pkg}::C{n:02}', 'Physical component identity mismatch'
            assert c['composition'] == choice, f'Candidate composition mismatch: {cid} {lid}'
            refs = [lid + '.' + s for s in choice.split('+') if re.fullmatch(r'(?:AR|EP|IN|CR|EC)\d', s)]
            assert c['alternative_ids'] == refs, f'Unscoped/wrong alternative identity: {cid} {lid}'
            assert set(c['primary_FR']) == {f'FR-{n:02}' for n in GROUPS[lid]}, 'Physical component primary FR mismatch'
        allocations = unique(record['allocations'], 'candidate allocation', 'FR')
        assert set(allocations) == set(fr) == ACTIVE_FR, f'Candidate FR allocation set mismatch: {cid}'
        for rid, a in allocations.items():
            assert a['primary'] == OWNERS[rid], f'Candidate logical allocation mismatch: {cid} {rid}'
            assert a['planned_check'] == fr[rid]['planned_check'], f'Candidate planned check mismatch: {cid} {rid}'
            if require_native:
                assert logical_rows is not None and record['reconciliation']['status'] == 'reconciled with final native contract', 'Final candidate native contract not reconciled'
                lr = logical_rows[rid]
                assert a['support'] == lr['support'] and a['interfaces'] == lr['interfaces'], 'Candidate supporting/interface allocation mismatch'
                assert isinstance(a['operation'], str) and a['operation'].startswith(by_l[a['primary']]['type'] + '::'), 'Unresolved physical operation'
        if record.get('logical_api'):
            if published is None:
                published = load(root/'traceability/framework-baseline.json')['logical_io_contract']
                audit_published_logical_api(root, fr, published)
        integrations = record['required_integrations']
        assert set(integrations) == {'f_prime', 'omniverse'}, 'Missing mandatory integration'
        for key, covered in [('f_prime', {'FR-24', 'FR-34', 'FR-36'}), ('omniverse', {'FR-18', 'FR-24'})]:
            integration = integrations[key]
            assert integration['required'] is True and set(integration['FR']) == covered and integration['status'] == 'proposed, not executed', f'Common integration scope mismatch: {cid} {key}'
            if key == 'omniverse':
                assert integration['scope'] == 'whole-CUBICS numerical scenario inputs and EPS states/results', 'Scene-only Omniverse integration'
            if require_native:
                assert integration['native_elements'], 'Mandatory integration lacks native realization'
        if cid == 'PA-CDT':
            roles = record['custom_roles']
            assert set(roles) == CUSTOM_ROLES, 'Missing substantive custom responsibility'
            for name, role in roles.items():
                assert role['required'] is True and role['inputs'] and role['outputs'] and role['status'] == 'proposed, not executed', f'Incomplete custom role: {name}'
                if require_native:
                    assert role['native_elements'], f'Custom role lacks native realization: {name}'
        if record.get('logical_api'):
            audit_candidate_logical_bridge(record, published)
        if require_native:
            native = record['native_contract']
            assert native and native['schema'] == 'task7-current-physical-v1' and native['status'] == 'reconciled with final native contract', 'Physical native contract not reconciled'
            assert len(native['framework_calls']) == 118 and len(native['procedure_performers']) == 24, 'Incomplete current physical performed/actor mapping'
            mechanisms = unique(native['comparison_mechanisms'], 'native critical MOP')
            assert set(mechanisms) == set(CRITICAL_MOPS) and all(m['mechanism'] and m['operation'] == m['native'] and m['achieved'] == 'unknown' for m in mechanisms.values()), 'Native structural MOP comparison mismatch'
            specs = unique(native['component_specifications'], 'native component source', 'component')
            assert set(specs) == {c['type'] for c in record['components']}, 'Missing native component specification/source'
            keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', (root/'literatura.bib').read_text()))
            for c in record['components']:
                s = specs[c['type']]
                assert s['specification']['logical'] == c['logical'] and s['source']['identifier'] == c['id'] and s['source']['sourceText'] and s['source']['status'] == 'proposed/unexecuted', 'Native component identity/source scope mismatch'
                assert {k.strip() for k in s['source']['citationRecord'].split(',')} <= keys, 'Native component citation does not resolve'
        candidates[cid] = record
    return trade, candidates


def audit_candidate_logical_bridge(record, contract):
    """Check shared logical pointers without treating them as physical exports."""
    pointer = record['logical_api']
    assert pointer['contract'] == 'traceability/framework-baseline.json#/logical_io_contract' and pointer['publication_sha256'] == contract['publication_sha256'], 'Candidate published API pointer mismatch'
    if contract.get('final_logical_ledger'):
        assert pointer.get('final_logical_ledger') == contract['final_logical_ledger'], 'Candidate final logical ledger pointer mismatch'
    components = unique(contract['components'], 'published component')
    req = unique(contract['requirements'], 'published FR')
    for c in record['components']:
        logical = components[c['logical']]
        assert c['logical_type'] == logical['definition'] and c['logical_part'] == logical['part'] and c['logical_io_port'] == logical['definition'] + '::io', 'Candidate published component pointer mismatch'
    for row in record['allocations']:
        r = req[row['FR']]
        calls = [s['path'] for s in contract['scenario_members'] if s.get('operation') == r['operation']]
        assert row['logical_operation'] == r['operation'] and row['logical_contract'] == r['model_path'], 'Candidate published FR operation/IO pointer mismatch'
        assert row['logical_scenario_calls'] == calls and calls, 'Candidate published scenario call mismatch'
    for key, names, frs in [
        ('f_prime', {'fPrimeRequests', 'fPrimeProducts', 'fPrimeResults'}, ('FR-34', 'FR-36', 'FR-24')),
        ('omniverse', {'wholeCUBICSScenarios', 'epsStatesResults'}, ('FR-18', 'FR-24'))]:
        expected = list(dict.fromkeys(req[r]['operation'] for r in frs)) + [
            e['model_path'] for e in contract['external_aggregates'] if e['name'] in names]
        assert record['required_integrations'][key]['logical_elements'] == expected, 'Candidate required platform logical pointer mismatch'


def audit_trade_matrix(text, trade):
    rows = table_rows(text, r'MOP-FR\d{2}')
    matrix = {}
    headers = re.findall(r'\\textbf\{(PA-(?:COM|VS|NS|GY|CDT))\}|(?<![\w-])(PA-(?:COM|VS|NS|GY|CDT))(?=\s*&|\s*\\\\)', visible(text))
    header_ids = [a or b for a, b in headers]
    assert header_ids[:5] == list(CANDIDATES), 'Critical-MOP matrix candidate columns missing/out of order'
    for cells in rows:
        assert len(cells) == 6, 'Actual critical-MOP by five-candidate matrix required'
        mid = cells[0]
        assert mid not in matrix, 'Duplicate critical MOP row'
        assert all(c and c.lower() not in {'unknown', 'tbr', 'n/a', '?'} for c in cells[1:]), 'Missing structural comparison cell'
        assert not any(re.search(r'\b(?:best|better|worst|winner|preferred|\d+\s*%|passed)\b', c, re.I) for c in cells[1:]), 'Unmeasured ranking/result in comparison'
        matrix[mid] = dict(zip(CANDIDATES, cells[1:]))
    assert tuple(matrix) == CRITICAL_MOPS, 'Exact six critical MOP rows required'
    ledger = unique(trade['critical_mop_comparison'], 'critical MOP')
    assert set(ledger) == set(matrix), 'Critical MOP ledger coverage mismatch'
    for mid, cells in matrix.items():
        row = ledger[mid]
        assert row['mechanisms'] == cells and row['achieved'] == 'unknown' and row['desired_range'] == MOP_TARGETS.get(mid, ('', ''))[0], 'Trade mechanism/result mismatch'
    active = visible(text)
    assert re.search(r'achieved values are unknown', active, re.I), 'Unknown achieved values must be explicit'
    assert not re.search(r'recommends developing|preferred (?:candidate|direction|deployment)|selected physical|reuse-first priority|principal alternative|priority ordering', active, re.I), 'Current selected/preferred report claim'
    return matrix


def audit_physical_tables(text, trade):
    active = visible(text); found = {}; lid = None
    for line in active.splitlines():
        heading = re.search(r'\\textbf\{(L\d{2})\b', line)
        if heading:
            lid = heading[1]
        for cells in table_rows(line + '\n', r'(?:AR|EP|IN|CR|EC)\d'):
            assert lid in GROUPS and len(cells) == 3, 'Alternative without logical scope'
            aid = lid + '.' + cells[0]
            assert aid not in found, 'Duplicate published alternative'
            found[aid] = cells
    assert set(found) == set(expected_alternatives()), 'Published alternatives must be five per L'
    ledger = unique(trade['alternatives'], 'scoped alternative')
    for aid, cells in found.items():
        assert cells[1] == ledger[aid]['supported_subset'] and cells[2] == ledger[aid]['required_additions'], f'Published alternative mismatch: {aid}'
        assert expected_alternatives()[aid] in cells[1] and cells[2], f'Missing source/additions: {aid}'
    rows = table_rows(active, r'PA-(?:COM|VS|NS|GY|CDT)')
    assert [r[0] for r in rows] == list(CANDIDATES) and all(len(r) == 7 for r in rows), 'Five by six published composition required'
    def normalize(cell):
        return re.sub(r'\s+', '', re.sub(r'\bPy\b', 'Python', cell))
    for row in rows:
        assert [normalize(c) for c in row[1:]] == [normalize(c) for c in COMPOSITION[row[0]]], f'Published candidate composition mismatch: {row[0]}'


def audit_logical_table(text):
    """Accept the concise name/ID, FR union and IO-summary table."""
    found = {}
    for line in visible(text).splitlines():
        if not re.search(r'\bL\d{2}\b', line) or not re.search(r'\\\\\*?\s*$', line):
            continue
        cells = table_cells(re.sub(r'\\\\\*?\s*$', '', line))
        ids = re.findall(r'\bL\d{2}\b', cells[0])
        if len(cells) != 3 or len(ids) != 1:
            continue
        lid = ids[0]
        groups = [c for c in cells[1:] if re.fullmatch(r'\d{2}(?:--\d{2})?(?:\s*,\s*\d{2}(?:--\d{2})?)*', c)]
        assert lid not in found and len(groups) == 1, 'Duplicate/missing published logical allocation row'
        found[lid] = bare_numbers(groups[0], 'FR-')
    assert set(found) == set(GROUPS), 'Exactly six published logical allocation rows required'
    for lid, ids in found.items():
        assert ids == {f'FR-{n:02}' for n in GROUPS[lid]}, f'Published primary FR allocation mismatch: {lid}'
    return found


def bridge_published_logical_api(fr, manifest, native_io, provenance):
    """Normalize published task6 exports, without inventing physical operations.

    IO contracts are not the engineering operations invoked by scenarios.
    Crosswalks perform typed projections, with a separate flow on each side.
    Publication hashes identify the import, not a current validation result.
    """
    assert manifest['schema'] == 'task6-model-export-v1' and native_io['schema'] == 'task6-native-io-v1', 'Unexpected published API schema'
    assert native_io['active_count'] == 40 and set(native_io['retired']) == {'FR-12', 'FR-40'}, 'Published active FR scope mismatch'
    components = copy.deepcopy(manifest['components'])
    requirements = copy.deepcopy(native_io['requirements'])
    req = unique(requirements, 'published FR')
    assert set(req) == set(fr), 'Published FR coverage mismatch'
    assert native_io['external_aggregates'] == manifest['external_aggregates'], 'Published boundary export mismatch'
    # native-io-contract adds declaration paths to the manifest's mappings.
    mex = unique(manifest['pairwise_exchanges'], 'published exchange', 'name')
    nex = unique(native_io['exchanges'], 'published IO exchange', 'name')
    assert set(mex) == set(nex), 'Published exchange set mismatch'
    for name, exchange in mex.items():
        other = nex[name]
        assert all(exchange[k] == other[k] for k in ('name', 'source', 'target', 'label', 'model_path')), 'Published exchange identity mismatch'
        assert len(exchange['mappings']) == len(other['mappings']) and all(
            all(b.get(k) == v for k, v in a.items()) for a, b in zip(exchange['mappings'], other['mappings'])), 'Published field mapping mismatch'
    unions = []
    io_components = unique(native_io['components'], 'published IO component')
    for c in components:
        lid = c['id']; ids = sorted(c['frs'])
        assert io_components[lid]['definition'] == c['definition'], 'Published component type mismatch'
        union = {'id': lid, 'FR': ids, 'native_features': {}, 'native_port_features': {}}
        for direction in ('inputs', 'outputs'):
            rows = unique(io_components[lid]['input_union' if direction == 'inputs' else 'output_union'], 'published IO union', 'fr')
            assert set(rows) == set(ids) and all(rows[r]['fields'] == req[r][direction] and
                rows[r]['model_path'] == req[r][direction + '_path'] for r in ids), 'Published IO union mismatch'
            union[direction] = {rid: fr[rid][direction] for rid in ids}
            for field, key in [('native_features', 'path'), ('native_port_features', 'port_path')]:
                union[field][direction] = {rid: [f[key] for f in req[rid]['field_contracts'][direction]] for rid in ids}
        unions.append(union)
    crosswalk, exchanges = [], []
    for e in native_io['exchanges']:
        exchanges.append({k: e[k] for k in ('name', 'source', 'target', 'label', 'model_path')})
        exchanges[-1]['mapping_count'] = len(e['mappings'])
        for m in e['mappings']:
            signature = manifest['reusable_action_signatures']['FrameworkLogical::Map_' + m['operation_path'].split('::')[-1]]
            assert [p['name'] for p in signature] == ['source', 'target'], 'Unexpected projection signature'
            crosswalk.append({
                'exchange': e['name'], 'source_component': e['source'], 'target_component': e['target'],
                'source_FR': m['source_fr'], 'source_field': m['source_output'],
                'target_FR': m['target_fr'], 'target_field': m['target_input'],
                'source_feature': m['source_declaration'], 'target_feature': m['target_declaration'],
                'source_path': m['source_path'], 'target_path': m['target_path'],
                'source_type': signature[0]['type'], 'target_type': signature[1]['type'],
                'projection_operation': m['operation_path'],
                'projection_type': signature[0]['declaration'].rsplit('::', 1)[0],
                'projection_signature': copy.deepcopy(signature),
                'native_source_flow': m['operation_path'] + '_source',
                'native_target_flow': m['operation_path'] + '_target', 'mapping_basis': m['mapping']})
    contract = {
        'schema': PUBLISHED_API_SCHEMA, 'status': BRIDGED_API_STATUS,
        'publication_sha256': dict(provenance),
        'source_sha256': {'requirements.tex': native_io['source_sha256'], **{
            'sysml/' + p: h for p, h in manifest['verification']['model_sha256'].items()
            if p in ('04-logical.sysml', '11-logical-responsibilities.sysml', '10-interface-views.sysml')}},
        'components': components, 'requirements': requirements, 'component_unions': unions,
        'exchanges': exchanges, 'crosswalk': crosswalk,
        'boundary_bindings': copy.deepcopy(manifest['boundary_bindings']),
        'external_aggregates': copy.deepcopy(manifest['external_aggregates']),
        'scenario_members': copy.deepcopy(manifest['scenario_members']), 'states': dict(manifest['states'])}
    audit_published_logical_api(None, fr, contract)
    return contract


def audit_published_logical_api(root, fr, contract, require_sources=False):
    """Audit the real exported shape. This is not physical release approval."""
    assert contract and contract['schema'] == PUBLISHED_API_SCHEMA, 'Missing published logical API bridge'
    assert set(contract['publication_sha256']) == {'export-manifest.json', 'native-io-contract.json', 'focused-checks.json'} and all(
        re.fullmatch(r'[0-9a-f]{64}', h) for h in contract['publication_sha256'].values()), 'Missing published API provenance'
    components = unique(contract['components'], 'published component')
    req = unique(contract['requirements'], 'published FR')
    assert set(components) == set(GROUPS) and set(req) == set(fr) == ACTIVE_FR, 'Published six-L/40-FR coverage mismatch'
    operations, contracts = {}, {}
    for lid, c in components.items():
        assert set(c['frs']) == {f'FR-{n:02}' for n in GROUPS[lid]} and c['part'] == 'FrameworkLogical::LogicalFramework::' + lid, 'Published component membership mismatch'
        assert c['definition'].startswith('FrameworkLogical::') and c['ports'] and c['definition'] + '::io' in c['ports'], 'Unresolved published component port'
        for op in c['operations']:
            assert op['path'] == c['definition'] + '::' + op['name'] and op['path'] not in operations, 'Duplicate/wrong published operation owner'
            assert op['parameters'] and op['action_type'].startswith('FrameworkLogical::'), 'Missing published operation signature'
            operations[op['path']] = (lid, op)
        declared = unique(c['performed_contracts'], 'published performed contract', 'path')
        assert set(declared) == set(c['contract_operations']) == {req[r]['model_path'] for r in c['frs']}, 'Published performed IO contract coverage mismatch'
        contracts.update(declared)
    for rid, r in req.items():
        assert r['primary'] == OWNERS[rid] and r['statement'] == fr[rid]['text'] and r['direct_parents'] == fr[rid]['parents'], 'Published FR wording/parent/owner mismatch'
        assert r['planned_check'] == fr[rid]['planned_check'], 'Published FR planned check mismatch'
        assert r['operation'] in operations and operations[r['operation']][0] == r['primary'], 'Published engineering operation owner mismatch'
        op = operations[r['operation']][1]; io = contracts[r['model_path']]
        assert r['action_type'] == op['action_type'] and r['operation_signature'] == op['parameters'], 'Published engineering operation signature mismatch'
        assert r['contract_action_type'] == io['action_type'] and r['contract_signature'] == io['parameters'], 'Published IO action signature mismatch'
        assert r['model_path'] == components[r['primary']]['definition'] + '::contract' + rid.replace('-', ''), 'Published IO action identity mismatch'
        assert r['operation'] != r['model_path'] and r['contract_signature'] == [
            {'name': name, 'direction': direction, 'type': r[key + '_path'], 'multiplicity': '1',
             'declaration': r['contract_action_type'] + '::' + name}
            for name, direction, key in [('subjects', 'in', 'inputs'), ('products', 'out', 'outputs')]], 'IO contract substituted for engineering operation'
        for direction, native_direction in [('inputs', 'in'), ('outputs', 'out')]:
            assert r[direction + '_verbatim'] == fr[rid][direction], 'Published FR verbatim IO mismatch'
            fields = r['field_contracts'][direction]
            assert fields and [f['exact_field'] for f in fields] == r[direction] and len(set(r[direction])) == len(fields), 'Incomplete/duplicate published typed IO fields'
            for n, f in enumerate(fields, 1):
                suffix = '::field' + f'{n:02}'
                assert f['path'] == r[direction + '_path'] + suffix and f['port_path'] == components[r['primary']]['definition'] + '::io::' + rid.replace('-', '').lower() + direction.capitalize() + suffix, 'Published IO field/port identity mismatch'
                assert f['direction'] == native_direction and f['multiplicity'] == '0..*' and re.fullmatch(r'(?:BoundaryViews|FrameworkLogical|FrameworkDomain)::\w+', f['type']), 'Published IO type/direction/multiplicity mismatch'
        assert r['admission_check'] == components['L06']['definition'] + '::checkTransfer', 'Published admission operation mismatch'
    unions = unique(contract['component_unions'], 'published component union')
    assert set(unions) == set(GROUPS), 'Missing logical input/output union'
    for lid, u in unions.items():
        ids = sorted(components[lid]['frs'])
        assert sorted(u['FR']) == ids, 'Wrong logical union membership'
        for direction in ('inputs', 'outputs'):
            assert u[direction] == {rid: fr[rid][direction] for rid in ids}, f'Incomplete logical {direction} union: {lid}'
            for field, key in [('native_features', 'path'), ('native_port_features', 'port_path')]:
                assert u[field][direction] == {rid: [f[key] for f in req[rid]['field_contracts'][direction]] for rid in ids}, 'Unresolved native IO union field'
    exchanges = unique(contract['exchanges'], 'published exchange', 'name')
    assert len(exchanges) == 20 and contract['crosswalk'], 'Empty/incomplete logical exchange crosswalk'
    identities, counts = set(), defaultdict(int)
    for row in contract['crosswalk']:
        identity = (row['source_FR'], row['source_field'], row['target_FR'], row['target_field'])
        assert identity not in identities, 'Duplicate logical field crosswalk'
        identities.add(identity)
        assert row['source_FR'] in req and row['target_FR'] in req, 'Unknown crosswalk FR'
        e = exchanges[row['exchange']]; counts[e['name']] += 1
        assert row['source_component'] == OWNERS[row['source_FR']] == e['source'] and row['target_component'] == OWNERS[row['target_FR']] == e['target'], 'Wrong crosswalk owner'
        for side, direction in [('source', 'outputs'), ('target', 'inputs')]:
            r = req[row[side + '_FR']]
            matches = [f for f in r['field_contracts'][direction] if f['exact_field'] == row[side + '_field']]
            assert len(matches) == 1, 'Crosswalk outside declared FR IO'
            f = matches[0]
            assert row[side + '_feature'] == f['path'] and row[side + '_type'] == f['type'], 'Crosswalk typed declaration mismatch'
            context_path = f['port_path'].replace(components[r['primary']]['definition'], components[r['primary']]['part'], 1)
            assert row[side + '_path'] == context_path, 'Crosswalk contextual feature chain mismatch'
        op = row['projection_operation']; action_type = row['projection_type']
        assert row['mapping_basis'] and re.fullmatch(re.escape(e['model_path']) + r'_\d{3}', op), 'Unresolved logical projection operation'
        assert action_type == 'FrameworkLogical::Map_' + op.split('::')[-1] and row['projection_signature'] == [
            {'name': side, 'direction': direction, 'type': row[side + '_type'], 'multiplicity': '0..*',
             'declaration': action_type + '::' + side} for side, direction in [('source', 'in'), ('target', 'out')]], 'Projection operation signature mismatch'
        assert row['native_source_flow'] == op + '_source' and row['native_target_flow'] == op + '_target', 'Unresolved logical field binding'
    assert sum(counts.values()) == 203 and all(counts[e['name']] == e['mapping_count'] for e in exchanges.values()), 'Published crosswalk mapping coverage mismatch'
    members = unique(contract['scenario_members'], 'published scenario call', 'path')
    assert len(members) == 142, 'Published scenario call coverage mismatch'
    invoked = set()
    for path, s in members.items():
        assert s['kind'] == 'PerformActionUsage' and path.startswith('LogicalRealization::') and s['parameters'], 'Published scenario is not an actual performed call'
        if s['owner'] == 'external':
            assert not s.get('operation'), 'External scenario call given a framework owner'
        else:
            assert s['operation'] in operations, 'Unresolved published scenario operation'
            lid, op = operations[s['operation']]; invoked.add(s['operation'])
            assert s['owner'] == components[lid]['part'] and s['action_type'] == op['action_type'], 'Published scenario operation owner/type mismatch'
            assert [{k: v for k, v in p.items() if k != 'endpoint'} for p in s['parameters']] == op['parameters'], 'Published scenario parameter signature mismatch'
        assert all(p['endpoint'] == path + '::' + p['name'] for p in s['parameters']), 'Published scenario parameter endpoint mismatch'
    assert {r['operation'] for r in req.values()} <= invoked, 'FR engineering operation has no performed scenario call'
    bindings = unique(contract['boundary_bindings'], 'published boundary binding', 'name')
    assert len(bindings) == 18 and all(b['source'] and b['target'] and set(b['fr_basis']) <= set(fr) for b in bindings.values()), 'Published boundary binding coverage mismatch'
    external = unique(contract['external_aggregates'], 'published external aggregate', 'name')
    expected = {'fPrimeRequests': ('out', 'BoundaryViews::CodingRequest'), 'fPrimeProducts': ('in', 'BoundaryViews::HostSoftwareProduct'),
                'fPrimeResults': ('in', 'BoundaryViews::SoftwareRunResult'), 'wholeCUBICSScenarios': ('in', 'BoundaryViews::ReferenceData'),
                'epsStatesResults': ('out', 'BoundaryViews::AnalysisResult')}
    assert set(external) == set(expected) and all((external[k]['direction'], external[k]['type']) == v and
        external[k]['endpoint'].startswith(components['L03']['part'] + '::') and set(external[k]['fr_basis']) <= set(fr) for k, v in expected.items()), 'Published required platform direction/type mismatch'
    assert contract['states'] == {'guidance': components['L06']['definition'] + '::assistanceCurrency', 'review': components['L05']['definition'] + '::reviewState'}, 'Published authority/currency state owner mismatch'
    if require_sources:
        assert root is not None and contract['source_sha256'] and all(sha(Path(root)/p) == h for p, h in contract['source_sha256'].items()), 'Published logical API source identity mismatch'
        assert {FR_IO_SOURCE, 'requirements.tex'} <= set(contract['source_sha256']), 'Published logical source snapshot must include both FR tables'
        text = (Path(root)/'sysml/04-logical.sysml').read_text()
        metadata = dict(re.findall(r'@NativeIO about (\w+::contractFR\d{2}) \{[^\n]*?operation = (\w+::\w+) meta SysML::ActionUsage;', text))
        assert len(metadata) == 40 and all(metadata.get(r['model_path'].removeprefix('FrameworkLogical::')) == r['operation'].removeprefix('FrameworkLogical::') for r in req.values()), 'Published native FR operation metadata mismatch'
    return req


def audit_final_logical_ledger(root, fr, logical, contract, require_sources=False):
    """Reconcile the definitive task6 ledger's two independent IO layers.

    Source IO unions use verbatim source categories. Native subject partitions
    have separate typed declarations and provenance. A null native_feature on
    a source-text union is intentional, not an absent typed native subject.
    """
    assert logical.get('schema_version') == 2 and logical.get('native_status') == 'verified', 'Final task6 logical ledger not released'
    components = unique(logical['components'], 'logical component')
    allocations = unique(logical['allocations'], 'logical allocation', 'FR')
    source = unique(logical['source_contract']['entries'], 'logical source contract', 'FR')
    published = audit_published_logical_api(root, fr, contract, require_sources=require_sources)
    exported = unique(contract['components'], 'published component')
    assert set(components) == set(GROUPS) and set(allocations) == set(source) == set(fr), 'Final logical ledger coverage mismatch'
    for rid, row in allocations.items():
        original = source[rid]; api = published[rid]
        for key, expected in [('statement', fr[rid]['text']), ('inputs_verbatim', fr[rid]['inputs']),
                              ('outputs_verbatim', fr[rid]['outputs']), ('parents', fr[rid]['parents'])]:
            assert row[key] == original[key] == expected, 'Final logical source contract mismatch'
        assert row['primary'] == original['primary'] == OWNERS[rid] and row['operation'] == api['operation'], 'Final logical operation/owner mismatch'
        assert row['verification'] == original['verification'] and row['verification']['status'] == 'planned, not executed' and (
            row['verification']['methods'] + ': ' + row['verification']['need']) == fr[rid]['planned_check'], 'Final logical planned check mismatch'
        assert row['MOP'] == original['MOP'] == 'MOP-FR' + rid[-2:] and row['native_mop'] == original['native_mop'] == 'FrameworkRequirements::MOP_FR' + rid[-2:], 'Final logical MOP mismatch'
        assert row['functions'] == ['BoundaryViews::' + f for f in fr[rid]['functions']] and row['scenarios'] == ['ScenarioViews::' + s for s in fr[rid]['scenarios']], 'Final logical scenario/function mismatch'
        assert len(row['support']) == len(set(row['support'])) and set(row['support']) <= set(GROUPS) - {row['primary']}, 'Final logical supporting allocation mismatch'
        assert len(row['interfaces']) == len(set(row['interfaces'])) and all(q.startswith('FrameworkLogical::') for q in row['interfaces']), 'Final logical interface allocation mismatch'
        calls = [s['path'] for s in contract['scenario_members'] if s.get('operation') == api['operation']]
        assert row['behaviors'] and set(row['behaviors']) <= set(calls), 'Final logical FR performed-call provenance mismatch'
        io = row['native_io']
        # Native ledger enriches the published field contracts with Subject metadata.
        assert all(io[k] == api[k] for k in api if k != 'field_contracts'), 'Final logical published IO contract mismatch'
        for direction in ('inputs', 'outputs'):
            assert row[direction] == original[direction] and row[direction], 'Final logical source IO union mismatch'
            fields, exported_fields = io['field_contracts'][direction], api['field_contracts'][direction]
            assert len(fields) == len(exported_fields), 'Final logical typed field coverage mismatch'
            for field, exported_field in zip(fields, exported_fields):
                assert all(field[k] == v for k, v in exported_field.items() if k != 'subject_metadata'), 'Final logical typed field declaration mismatch'
                meta = field['subject_metadata']
                assert meta == exported_field.get('subject_metadata', meta) and meta['fr'] == rid and meta['direction'] == direction and meta['exactField'] == field['exact_field'] and meta['provenance'], 'Final logical typed field provenance mismatch'
    for lid, component in components.items():
        c = exported[lid]
        assert component['native_part'] == c['part'] and component['native_type'] == c['definition'] and set(component['primary_FR']) == set(c['frs']), 'Final logical component export mismatch'
        rows = [r for r in logical['allocations'] if r['primary'] == lid]
        for direction in ('inputs', 'outputs'):
            expected_source, expected_typed = defaultdict(set), {}
            for r in rows:
                for field in r[direction]:
                    expected_source[field].add(r['FR'])
                for f in r['native_io']['field_contracts'][direction]:
                    expected_typed.setdefault(f['exact_field'], []).append({'FR': r['FR'], 'native': f['path'], 'type': f['type']})
            union = unique(component['io_union'][direction], 'logical source union field', 'field')
            assert set(union) == set(expected_source) and all(len(u['provenance']) == len(set(u['provenance'])) and
                set(u['provenance']) == expected_source[name] for name, u in union.items()), 'Final logical source union provenance mismatch'
            assert component['typed_io_union'][direction] == expected_typed, 'Final logical typed union mismatch'
    mappings = {m['operation_path']: (e, m) for e in logical['exchanges'] for m in e['mappings']}
    assert len(logical['exchanges']) == 20 and len(mappings) == sum(len(e['mappings']) for e in logical['exchanges']) == 203, 'Final logical crosswalk coverage mismatch'
    for row in contract['crosswalk']:
        e, m = mappings[row['projection_operation']]
        assert e['name'] == row['exchange'] and e['source_component'] == row['source_component'] and e['target_component'] == row['target_component'], 'Final logical crosswalk aggregate mismatch'
        pairs = {'source_fr': 'source_FR', 'target_fr': 'target_FR', 'source_output': 'source_field', 'target_input': 'target_field',
                 'source_declaration': 'source_feature', 'target_declaration': 'target_feature', 'source_path': 'source_path', 'target_path': 'target_path',
                 'action_type': 'projection_type', 'source_qualified_type': 'source_type', 'target_qualified_type': 'target_type', 'mapping': 'mapping_basis'}
        assert all(m[k] == row[v] for k, v in pairs.items()), 'Final logical typed projection mismatch'
        for side in ('source', 'target'):
            route = m[side + '_flow']
            assert route['native'] == row['native_' + side + '_flow'] and route['payload'] == row[side + '_type'], 'Final logical projection route mismatch'
            if side + '_route' in row:
                assert row[side + '_route'] == route, 'Final logical actual flow-end chain mismatch'
        if 'aggregate_field' in row:
            assert row['aggregate_field'] == m['aggregate_field'] and row['field_metadata'] == m['metadata'], 'Final logical aggregate field provenance mismatch'
    assert contract['boundary_bindings'] == logical['native_contract']['boundary_routes'], 'Final logical boundary dispatch mismatch'
    external = unique(logical['external_exchanges'], 'logical external exchange', 'name')
    for row in contract['external_aggregates']:
        assert all(external[row['name']][k] == v for k, v in row.items()), 'Final logical external aggregate mismatch'
    tasks = unique(logical['safety_contract']['tasks'], 'logical performed task', 'native')
    assert set(tasks) == {s['path'] for s in contract['scenario_members']}, 'Final logical performed task coverage mismatch'
    for s in contract['scenario_members']:
        task = tasks[s['path']]
        assert task['action_type'] == s['action_type'], 'Final logical performed task type mismatch'
        if s['owner'] != 'external':
            assert task['component'] == s['owner'] and task['operation'] == s['operation'] and task['allocated_target'] == ['FrameworkLogical::logical', s['owner']], 'Final logical performed task allocation mismatch'
        else:
            assert task.get('actor') and task['allocated_target'] == [task['actor']], 'Final logical external performer missing'
    if require_sources:
        pointer = contract['final_logical_ledger']
        assert pointer['path'] == 'traceability/logical-architecture.json' and sha(Path(root)/pointer['path']) == pointer['sha256'], 'Final logical ledger source identity mismatch'
        assert sha(Path(root)/'requirements.tex') == logical['source_contract']['requirements_sha256'] and sha(Path(root)/'sysml/03-requirements.sysml') == logical['source_contract']['native_requirements_sha256'], 'Final logical requirement source identity mismatch'
        assert logical['source_contract']['inputs_outputs_path'] == FR_IO_SOURCE and sha(Path(root)/FR_IO_SOURCE) == logical['source_contract']['inputs_outputs_sha256'], 'Final logical IO appendix source identity mismatch'
        audit_logical_table((Path(root)/'logical.tex').read_text())
    return allocations


def audit_logical_contract(root, fr, logical, contract):
    """Check final unions/crosswalk without requiring the retired logical API."""
    components = unique(logical['components'], 'logical component')
    allocations = unique(logical['allocations'], 'logical allocation', 'FR')
    assert set(components) == set(GROUPS) and set(allocations) == set(fr), 'Six-L/40-FR logical coverage required'
    for rid, row in allocations.items():
        assert row['primary'] == OWNERS[rid] and set(row['support']) <= set(GROUPS), 'Wrong logical owner/support'
        assert row['operation'] and row['verification']['status'] == 'planned, not executed', 'Unresolved logical operation/false outcome'
    assert contract and contract['status'] == 'reconciled with final native contract', 'Final logical IO/crosswalk contract not reconciled'
    if contract.get('schema') == PUBLISHED_API_SCHEMA:
        if logical.get('schema_version') == 2:
            return audit_final_logical_ledger(root, fr, logical, contract)
        published = audit_published_logical_api(root, fr, contract)
        assert all(allocations[rid]['operation'] == r['operation'] for rid, r in published.items()), 'Logical ledger operation differs from published native API'
        return allocations
    unions = unique(contract['component_unions'], 'component union')
    assert set(unions) == set(GROUPS), 'Missing logical input/output union'
    for lid, row in unions.items():
        ids = {f'FR-{n:02}' for n in GROUPS[lid]}
        assert set(row['FR']) == ids, 'Wrong logical union membership'
        for direction in ('inputs', 'outputs'):
            assert row[direction] == {rid: fr[rid][direction] for rid in sorted(ids)}, f'Incomplete logical {direction} union: {lid}'
            assert set(row['native_features'][direction]) == ids and all(row['native_features'][direction].values()), 'Unresolved native IO union field'
    assert contract['crosswalk'], 'Empty logical exchange crosswalk'
    identities = set()
    for row in contract['crosswalk']:
        identity = (row['source_FR'], row['source_field'], row['target_FR'], row['target_field'])
        assert identity not in identities, 'Duplicate logical field crosswalk'
        identities.add(identity)
        assert row['source_FR'] in fr and row['target_FR'] in fr, 'Unknown crosswalk FR'
        assert row['source_component'] == OWNERS[row['source_FR']] and row['target_component'] == OWNERS[row['target_FR']], 'Wrong crosswalk owner'
        assert row['source_field'] in fr[row['source_FR']]['outputs'] and row['target_field'] in fr[row['target_FR']]['inputs'], 'Crosswalk outside declared FR IO'
        assert row['native_flow'] and row['source_feature'] and row['target_feature'] and row['mapping_basis'], 'Unresolved logical field binding'
    return allocations


def solution_sources(root):
    result, pending = [], [root/'solucion.tex']
    while pending:
        path = pending.pop()
        if path in result:
            continue
        assert path.is_file(), f'Missing solution source: {path}'
        result.append(path)
        pending.extend(root/Path(n).with_suffix('.tex') for n in reversed(
            re.findall(r'\\(?:input|include)\s*\{([^}]+)\}', visible(path.read_text()))))
    return result


def audit_figures(root, diagrams):
    """Verify declared artifact provenance. Illustrations need no native render."""
    assert len(diagrams) == len(set(diagrams)), 'Duplicate solution figure paths'
    result = []
    for diagram in diagrams:
        figure = root/diagram
        assert diagram.startswith('fig/') and figure.is_file(), f'Missing/non-fig figure: {diagram}'
        svg = figure.with_suffix('.svg')
        provenance_path = figure.with_suffix('.provenance.json')
        if provenance_path.is_file():
            record = load(provenance_path)
            assert record.get('native_syside_render', record.get('native_syside')) is False, 'Authored figure falsely claims native rendering'
            hashes = record.get('artifact_sha256') or {Path(k).suffix[1:]: v for k, v in record['sha256'].items()}
            assert {'svg', 'pdf'} <= set(hashes), 'Incomplete illustrative figure hashes'
            for fmt, digest in hashes.items():
                assert sha(figure.with_suffix('.' + fmt)) == digest, f'Figure {fmt} hash mismatch: {diagram}'
            if 'svg_sha256_used_for_pdf' in record:
                assert record['svg_sha256_used_for_pdf'] == hashes['svg'], 'PDF source hash mismatch'
            elif 'independent_svg_to_pdf_to_png_reproduction' in record.get('independent_verification', {}):
                reproduction = record['independent_verification']
                assert reproduction['independent_svg_to_pdf_to_png_reproduction'] and reproduction['reproduced_png_sha256'] == hashes.get('png'), 'Illustration conversion unverified'
                command = record['renderers']['pdf']['command']
                assert svg.name in command and figure.name in command and 'rsvg-convert' in command, 'Missing illustration conversion command'
            else:
                raise AssertionError('Missing declared SVG/PDF conversion provenance')
            labels = ' '.join(ET.parse(svg).getroot().itertext())
            if figure.stem == 'logical-architecture':
                # Coordinated views can place external endpoints on page 2.
                # Verify every declared panel before checking their joint labels.
                for name, digest in record.get('coordinated_panel_sha256', {}).items():
                    assert Path(name).name == name, 'Invalid coordinated figure path'
                    panel = figure.parent/name
                    assert panel.is_file() and sha(panel) == digest, 'Coordinated figure hash mismatch'
                    if panel.suffix == '.svg' and panel != svg:
                        labels += ' ' + ' '.join(ET.parse(panel).getroot().itertext())
                assert all(lid in labels for lid in GROUPS) and 'L07' not in labels and 'L08' not in labels, 'Logical figure component labels mismatch'
                assert 'F Prime' in labels and 'Omniverse' in labels and 'CUBICS' in labels, 'Logical figure mandatory endpoints missing'
                generator = figure.with_suffix('.py')
                assert record['dimensions']['pdf_pages'] == 3 and sha(generator) == record['generator_sha256'], 'Logical three-view generator identity mismatch'
                spec = importlib.util.spec_from_file_location('audited_logical_illustration', generator)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                inventory = module.inventory()
                panels = [svg] + [figure.with_name(figure.stem + f'-panel-{n:02}.svg') for n in (2, 3)]
                # Check actual canonical boxes, Framework containment, crossing ports,
                # concrete branch ownership and directions against current contracts.
                try:
                    display = module.display_check(inventory, panels)
                except ValueError as error:
                    raise AssertionError(str(error)) from error
                assert inventory['counts'] == record['counts'], 'Logical displayed contract coverage mismatch'
            result.append({'figure': diagram, 'kind': 'authored illustration', 'provenance': str(provenance_path.relative_to(root)), 'artifact_sha256': hashes,
                           **({'display_checks': display} if figure.stem == 'logical-architecture' else {})})
            continue
        manifest_path = figure.with_suffix('.manifest.json')
        assert manifest_path.is_file(), f'Missing figure provenance: {diagram}'
        record = load(manifest_path)
        assert record['visualizer']['name'] == 'Syside Modeler' and record['visualizer']['native'] is True, 'False native figure provenance'
        artifacts = {a['format']: a for a in record['artifacts']}
        assert len(artifacts) == len(record['artifacts']) and {'svg', 'pdf'} <= set(artifacts), 'Incomplete/duplicate native figure artifacts'
        for fmt, artifact in artifacts.items():
            path = figure.with_suffix('.' + fmt)
            assert Path(artifact['path']).name == path.name and path.is_file(), f'Missing/wrong {fmt} artifact'
            declared = artifact['provenance'].get('sha256')
            if declared:
                assert sha(path) == declared, f'Figure {fmt} hash mismatch: {diagram}'
        source = artifacts['pdf']['provenance']['source_svg']
        assert Path(source['path']).name == svg.name and source['sha256'] == sha(svg), 'PDF source hash mismatch'
        # A published illustration can survive unrelated model edits. Old all-model
        # hashes describe the render snapshot only. They are not current semantics.
        result.append({'figure': diagram, 'kind': 'native render snapshot', 'view': record['target']['qualified_name'],
                       'provenance': str(manifest_path.relative_to(root)), 'artifact_sha256': {fmt: sha(figure.with_suffix('.' + fmt)) for fmt in artifacts}})
    return result


def audit_historical_reviews(root):
    result = {}
    for name in ('independent-review', 'source-review'):
        record = load(root/f'traceability/{name}.json')
        assert record['record_role'] == record['status'] == 'HISTORICAL', 'Historical review presented as current'
        assert record['current_revision_review_performed'] is False and record['empirical_approval'] is False, 'False renewed/empirical review approval'
        evidence = record['historical_evidence']
        assert evidence_digest(evidence) == record['historical_evidence_sha256'], 'Historical review evidence altered'
        if name == 'independent-review':
            assert evidence['empirical_framework_vv_executed'] is False and evidence['empirical_approval'] is False, 'False historical empirical approval'
            for finding in evidence['findings']:
                assert finding['original_status'] == 'open' and finding['resolution'] and finding['rereview_evidence'], 'Historical finding evidence erased'
            result[name] = {'role': 'HISTORICAL', 'current_review_performed': False,
                            'historical_review_record_sha256': evidence['review_record_sha256']}
        else:
            current = record['current_assertions']
            assert len(current) <= 40, 'Source assertions must remain bounded'
            seen = set()
            for assertion in current:
                assert assertion['id'] not in seen and assertion['supported_subset'] and assertion['limits'], 'Unbounded/duplicate source assertion'
                seen.add(assertion['id']); path = Path(assertion['source'])
                assert sha(path) == assertion['sha256'], 'Current bounded source hash mismatch'
                start, end = assertion['lines']
                assert 1 <= start <= end and end - start < 120, 'Unbounded source excerpt'
                excerpt = '\n'.join(path.read_text().splitlines()[start - 1:end])
                assert assertion['quote'] and assertion['quote'] in excerpt, 'Current source quotation/locator mismatch'
            result[name] = {'role': 'HISTORICAL', 'current_review_performed': False, 'bounded_current_assertions': len(current)}
    return result


def audit_cases(root, baseline, fr):
    cases = unique(baseline['verification_cases'], 'verification case')
    text = (root/'sysml/05-verification.sysml').read_text()
    targets = dict(re.findall(r"verification <'(V\d+)'> \w+ \{\s*subject framework : ToBe::FutureFramework;\s*objective \{ verify FrameworkRequirements::FR_(\d+);", text))
    assert set(cases) == set(targets) and {'FR-' + n for n in targets.values()} == set(fr) and len(cases) == 40, 'V case subject/coverage mismatch'
    attrs = annotations(text, 'PlannedProcedure', r'V\d{2}')
    defaults = dict(re.findall(r'attribute (status|executed|observedVerdict) : ScalarValues::\w+ = ([^;]+);', text))
    assert defaults == {'status': '"planned, not executed"', 'executed': 'false', 'observedVerdict': '"none"'}, 'False native verification outcome'
    for vid, case in cases.items():
        rid = case['framework_requirement_id']
        assert rid == 'FR-' + targets[vid], 'Wrong V target'
        assert case['status'] == 'planned, not executed' and case['executed'] is False and case['verdict'] is None, 'False verification outcome'
        for field in PROCEDURE_FIELDS:
            native = 'subjectDescription' if field == 'subject' else field
            assert case[field].strip() and attrs[vid].get(native) == case[field], f'Incomplete/mismatched V procedure: {vid} {field}'
        assert attrs[vid]['methods'] == ','.join(case['methods']) == ','.join(fr[rid]['methods']), 'V method mismatch'
        assert set(attrs[vid]) == (set(PROCEDURE_FIELDS) - {'subject'}) | {'subjectDescription', 'methods'}, 'Unexpected V outcome override'
        assert 'before execution' in case['prerequisites'], 'Missing pre-execution criteria gate'
        assert not re.search(r'\b(?:technician|HIL|PIL|test bench|target processor)\b', ' '.join(case[f] for f in PROCEDURE_FIELDS), re.I), 'Excluded V activity'
    assert number_set(visible((root/'verification-plan.tex').read_text()), 'V') == set(cases), 'Report V coverage mismatch'
    gate = baseline['qualification_gate']
    assert gate['owner'] == 'Systems Engineer' and gate['risk_basis'] and gate['action'] and 'blocked' in gate['status'], 'Missing qualification owner/risk/action'
    policy = baseline['future_tracecheck_policy']
    assert policy['scope'] and policy['status'].startswith('planned,') and policy['gate_native'] == 'FrameworkVerification::qualificationGate', 'False future qualification'
    assert (policy['owner'], policy['risk_basis'], policy['action']) == (gate['owner'], gate['risk_basis'], gate['action']), 'Future qualification owner/risk/action mismatch'
    for field, native_name in [('owner', 'owner'), ('status', 'status'), ('risk_basis', 'riskBasis'), ('action', 'resolutionAction')]:
        declaration = ':>> status' if native_name == 'status' else native_name + ' : ScalarValues::String'
        assert f'{declaration} = {json.dumps(gate[field], ensure_ascii=False)};' in text, 'Qualification gate native/ledger mismatch'
    for name in ('frameworkValidation', 'epsPhaseProductVerification', 'epsPhaseProductValidation', 'modelCredibilityProtocol', 'researchEvaluation'):
        assert f'item {name} :' in text, f'Missing distinct assessment subject: {name}'
    return cases


def semantic_audit(inspection, baseline, fr, figures):
    assert inspection['valid'] and inspection['exit_code'] == 0, 'Native inspection failed'
    assert not [d for d in inspection['diagnostics'] if d.get('severity') in ('error', 'warning')], 'Native diagnostics present'
    model = inspection['semantic_model']; summary = model['summary']
    assert not summary['elements_truncated'] and not summary['relationships_truncated'], 'Inspection must be uncapped'
    elements = model['elements']; ids = {e['id'] for e in elements}
    by = {e['qualified_name']: e for e in elements if e.get('qualified_name')}
    assert not [e for e in elements if e['kind'] == 'SatisfyRequirementUsage'], 'False satisfaction assertion'
    edges, id_edges = defaultdict(set), defaultdict(set)
    for rel in model['relationships']:
        for endpoint in rel['sources'] + rel['targets']:
            assert endpoint.get('external') or endpoint['id'] in ids, 'Incomplete local native endpoint'
        for s in rel['sources']:
            for t in rel['targets']:
                id_edges[(rel['kind'], s['id'])].add(t['id'])
                if s.get('qualified_name') and t.get('qualified_name'):
                    edges[(rel['kind'], s['qualified_name'])].add(t['qualified_name'])
    def exact(kind, source, target):
        assert target in edges[(kind, source)], f'Unresolved native {kind}: {source} -> {target}'
    for rid, row in fr.items():
        q = 'FrameworkRequirements::' + rid.replace('-', '_')
        assert q in by, f'Missing native FR: {rid}'
        for m in row['parents']:
            d = 'FrameworkRequirements::derive_' + m.replace('-', '_') + '_' + rid.replace('-', '_')
            exact('ReferenceSubsetting', d + '::source', 'FrameworkNeeds::' + m.replace('-', '_'))
            exact('ReferenceSubsetting', d + '::target', q)
        for s in row['scenarios']:
            exact('Dependency', q, 'ScenarioViews::' + s)
        for f in row['functions']:
            exact('Dependency', q, 'BoundaryViews::' + f)
        operation = row['logical_operation']
        assert operation in by and by[operation]['kind'] == 'PerformActionUsage', 'Unresolved logical operation'
        exact('Dependency', q, operation)
        for pa in row['physical_allocations']:
            assert pa['operation'] in by and by[pa['operation']]['kind'] == 'PerformActionUsage', 'Unresolved physical operation'
            # Physical trace is the actual primary allocation's typed operation
            # metadata, checked by the current native physical stage. The
            # released design does not duplicate it as a plain Dependency.
            assert pa['operation'].startswith(pa['native_package'] + '::'), 'Wrong physical operation package'
    contract = baseline['logical_io_contract']
    for union in contract['component_unions']:
        for direction in ('inputs', 'outputs'):
            for features in union['native_features'][direction].values():
                assert all(q in by for q in features), 'Unresolved native union feature'
    for mapping in contract['crosswalk']:
        flows = [mapping['native_source_flow'], mapping['native_target_flow']] if contract.get('schema') == PUBLISHED_API_SCHEMA else [mapping['native_flow']]
        assert all(q in by and by[q]['kind'] == 'FlowUsage' for q in flows), 'Unresolved logical flow'
        assert mapping['source_feature'] in by and mapping['target_feature'] in by, 'Unresolved logical flow feature'
        if contract.get('schema') == PUBLISHED_API_SCHEMA:
            q = mapping['projection_operation']
            assert q in by and by[q]['kind'] == 'PerformActionUsage' and mapping['projection_type'] in by[q]['semantic_types'], 'Unresolved typed logical projection'
            for side in ('source', 'target'):
                assert mapping[side + '_type'] in by[mapping[side + '_feature']]['semantic_types'], 'Logical IO declaration type mismatch'
    if contract.get('schema') == PUBLISHED_API_SCHEMA:
        for row in contract['requirements']:
            assert row['model_path'] in by and by[row['model_path']]['kind'] == 'PerformActionUsage', 'Unresolved native FR IO contract'
            for direction in ('inputs', 'outputs'):
                for field in row['field_contracts'][direction]:
                    assert field['path'] in by and field['type'] in by[field['path']]['semantic_types'], 'Unresolved typed native IO field'
        for row in contract['scenario_members']:
            assert row['path'] in by and by[row['path']]['kind'] == 'PerformActionUsage' and row['action_type'] in by[row['path']]['semantic_types'], 'Unresolved current performed scenario call'
    # Actual allocation/control endpoints are checked by the licensed stage
    # checkers. Their current source identities are mandatory for this release.
    assert {c['id'] for c in baseline['stage_checks']} == {'scenario', 'logical', 'physical'}, 'All three current stage checks required'
    for checker in baseline['stage_checks']:
        assert checker['valid'] is True and checker['negative_cases'] and all(
            c['mutation_matches'] == 1 and c['rejected'] is True for c in checker['negative_cases'].values()), 'Missing/ineffective current authority/admission/currency checks'
        assert all(sha(Path(baseline['report_root']) / p) == h for p, h in checker['source_sha256'].items()), 'Stage check source identity mismatch'
    return {'elements': len(elements), 'relationships': len(model['relationships']), 'endpoint_completeness': True, 'satisfaction_assertions': 0}


def audit(root, inspect_path=None, log_path=None):
    root = Path(root).resolve(); baseline = load(root/'traceability/framework-baseline.json')
    assert baseline['reconciliation']['status'] == 'reconciled with final native contract', 'Integrated release reconciliation incomplete'
    assert_neutral({k: v for k, v in baseline.items() if k != 'historical_evidence'})
    concerns = unique(baseline['concerns'], 'concern'); parsed = parse_concerns(root/'apendice.tex')
    assert set(concerns) == {r['id'] for r in parsed}, 'Concern current-source ID mismatch'
    native_text = (root/'sysml/01-concerns.sysml').read_text()
    native_concerns = dict(re.findall(r"concern <'([^']+)'> \w+ \{[^\n]*doc /\* (.*?) \*/", native_text))
    assert set(native_concerns) == set(concerns), 'Concern native/current-source ID mismatch'
    locators = annotations(native_text, 'SourceRecord', r'C_\w+')
    for row in parsed:
        c = concerns[row['id']]
        assert all(c.get(k) == v for k, v in row.items()) and native_concerns[c['id']] == c['text'], 'Concern wording/hierarchy mismatch'
        assert c['parent'] is None or c['parent'] in concerns, 'Orphan concern'
        assert c['alias_target'] is None or c['alias_target'] in concerns, 'Unknown concern alias'
        assert c['disposition'] and c['scope_status'] and not c.get('framework_requirement_ids'), 'Invalid concern scope/forced FR mapping'
        locator = locators[re.sub(r'[-.]', '_', c['id'])]['sourceLocator']
        assert f'final_report/apendice.tex#{c["id"]}' in locator and 'current protected SHA-256' not in locator, 'Stale concern SourceRecord locator'
    mr, fr, ucs, scs, uc_mrs, sc_mrs, sc_ucs = current_trace(root)
    bm = unique(baseline['mission_requirements'], 'mission requirement')
    bf = unique(baseline['framework_requirements'], 'framework requirement')
    assert set(bm) == set(mr) and set(bf) == set(fr), 'Current ledger requirement IDs mismatch'
    for mid, row in bm.items():
        assert row['text'] == mr[mid]['text'] and set(row['framework_requirement_ids']) == {r for r in fr if mid in fr[r]['parents']}, 'MR ledger trace mismatch'
    assert {r['id']: set(r['mission_requirement_ids']) for r in baseline['use_cases']} == dict(uc_mrs), 'UC ledger mismatch'
    assert {r['id']: set(r['mission_requirement_ids']) for r in baseline['mission_scenarios']} == dict(sc_mrs), 'SC ledger mismatch'
    logical = load(root/'traceability/logical-architecture.json')
    la = audit_logical_contract(root, fr, logical, baseline['logical_io_contract'])
    audit_final_logical_ledger(root, fr, logical, baseline['logical_io_contract'], require_sources=True)
    audit_logical_table((root/'logical.tex').read_text())
    trade, candidates = audit_candidate_records(root, fr, logical, require_native=True)
    audit_physical_tables((root/'physical-candidates.tex').read_text(), trade)
    audit_trade_matrix((root/'trade-selection.tex').read_text(), trade)
    for rid, row in bf.items():
        assert row['text'] == fr[rid]['text'] and row['mission_requirement_ids'] == fr[rid]['parents'], 'FR ledger wording/parent mismatch'
        assert row['inputs'] == fr[rid]['inputs'] and row['outputs'] == fr[rid]['outputs'], 'FR ledger IO mismatch'
        assert row['mission_scenario_ids'] == fr[rid]['scenarios'] and row['black_box_function_ids'] == fr[rid]['functions'], 'FR ledger scenario/function mismatch'
        lr = la[rid]
        assert row['primary_logical_component_id'] == lr['primary'] and row['supporting_logical_component_ids'] == lr['support'] and row['logical_operation'] == lr['operation'], 'Logical ledger mismatch'
        pas = unique(row['physical_allocations'], 'physical trace', 'candidate_id')
        assert set(pas) == set(candidates), 'Incomplete all-candidate trace'
        for cid, candidate in candidates.items():
            ar = next(a for a in candidate['allocations'] if a['FR'] == rid)
            component = next(c for c in candidate['components'] if c['logical'] == lr['primary'])
            assert pas[cid]['physical_component_id'] == component['id'] and pas[cid]['operation'] == ar['operation'], 'Physical component/operation mismatch'
        fr[rid].update(row)
    rationales = audit_fr_rationales(root, fr, baseline['framework_requirements'])
    mops = audit_mops(root, fr, baseline['measures_of_performance'])
    moes = audit_moes(root, baseline['measures_of_effectiveness'])
    from check_concern_coverage import check as check_concern_coverage
    concern_coverage = check_concern_coverage(root)
    cases = audit_cases(root, baseline, fr); reviews = audit_historical_reviews(root)
    assertions = load(root/'traceability/source-review.json')['current_assertions']
    assert set(expected_alternatives().values()) | {'handpicked-0004'} <= {s['citation'] for s in assertions}, 'Missing bounded current source assertions'
    assert {c['id'] for c in baseline['stage_checks']} == {'scenario', 'logical', 'physical'}, 'All three current stage checks required'
    for checker in baseline['stage_checks']:
        assert checker['valid'] is True and checker['negative_cases'] and all(
            c['mutation_matches'] == 1 and c['rejected'] is True for c in checker['negative_cases'].values()), 'Missing/ineffective current stage negative checks'
        assert checker['source_sha256'] and all(sha(root/p) == h for p, h in checker['source_sha256'].items()), 'Stage check source identity mismatch'
    files = solution_sources(root); solution = '\n'.join(visible(p.read_text()) for p in files)
    active = '\n'.join(visible(p.read_text()) for p in files if p.name != 'as-is-domain.tex')
    assert not re.search(r'\bMN-\d|\bFR-(?:12|40)\b|\bL0[789]\b', active), 'Retired current report identifier'
    assert not re.search(r'\\(?:scriptsize|tiny|resizebox|scalebox)\b', active), 'Unreadable reduced publication content'
    source_hashes = baseline['current_source_sha256']
    assert source_hashes and all(sha(root/p) == h for p, h in source_hashes.items()), 'Current audit source snapshot mismatch'
    assert {FR_IO_SOURCE, 'tools/test_fr_io.py', 'fig/logical-architecture-panel-03.svg',
            'fig/logical-architecture-panel-03.pdf', 'fig/logical-architecture-panel-03.png'} <= set(source_hashes), 'Current snapshot must include appendix IO and all three logical views'
    acronyms = audit_glossary((root/'glosario.tex').read_text())
    bibliography = (root/'literatura.bib').read_text(); keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)\s*,', bibliography)
    assert len(keys) == len(set(keys)), 'Duplicate bibliography key'
    missing = set()
    for path in root.glob('*.tex'):
        text = visible(path.read_text())
        assert not re.search(r'\\\\cite[a-zA-Z]*', text), 'Doubled citation escape'
        for citations in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}', text):
            missing.update({k.strip() for k in citations.split(',')} - set(keys))
    assert not missing and set(expected_alternatives().values()) <= set(keys), f'Missing bibliography citations: {sorted(missing)}'
    figures = audit_figures(root, re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', solution))
    semantic = None
    if inspect_path:
        inspection = load(inspect_path)
        paths = inspection['files']['input'] + inspection['files']['included']
        assert len(paths) == len(set(paths)) and {Path(p).resolve() for p in paths} == {p.resolve() for p in (root/'sysml').rglob('*.sysml')}, 'Inspection current source set mismatch'
        semantic = semantic_audit(inspection, dict(baseline, report_root=str(root)), fr, figures)
    pages = audit_latex_log(Path(log_path).read_text(errors='replace')) if log_path else None
    return {'valid': True, 'scope': 'Current specification consistency only. No empirical V&V or renewed independent review.',
            'concern_occurrences': len(concerns), 'concern_moe_coverage': concern_coverage['counts'],
            'measures_of_effectiveness': len(moes), 'mission_requirements': len(mr), 'direct_fr_parents': 169,
            'framework_requirements': len(fr), 'fr_rationale': rationales,
            'logical_components': len(logical['components']), 'measures_of_performance': len(mops),
            'candidate_allocations': {cid: len(c['allocations']) for cid, c in candidates.items()},
            'planned_verification_cases': len(cases), 'figures': figures, 'historical_reviews': reviews,
            'semantic': semantic, 'pages': pages, 'framework_empirical_vv': 'not executed'}


def audit_glossary(text):
    acronyms = re.findall(r'\\syma(?:\[[^]]*\])?\{([^}]+)\}', text)
    assert len(acronyms) == len(set(acronyms)), 'Duplicate glossary acronym'
    required = {'MBSE', 'OOSEM', 'SysML', 'EPS', 'RAM', 'SIL', 'MOE', 'MOP',
                'MR', 'FR', 'MIL', 'CDR', 'SIR', 'CSRM', 'FMI', 'USD', 'COTS',
                'HTN', 'KiBaM', 'RMSE'}
    assert required <= set(acronyms), f'Missing current glossary acronyms: {sorted(required - set(acronyms))}'
    return acronyms


def audit_latex_log(log):
    assert not re.search(r'Overfull \\[hv]box|undefined on input|undefined references|undefined citations|Citation .+ undefined|Reference .+ undefined|Float too large|^!', log, re.MULTILINE), 'LaTeX unresolved reference/citation, error, overfull box or oversized float'
    match = re.search(r'Output written on [\s\S]*?\((\d+) pages?', log)
    assert match, 'No final PDF page count in LaTeX log'
    pages = int(match[1]); assert pages <= 100, f'Report exceeds 100 page ceiling: {pages}'
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--inspect', type=Path, help='Uncapped genuine Syside inspection JSON')
    parser.add_argument('--log', type=Path, help='Final-pass actual report LaTeX log')
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.report, args.inspect, args.log), indent=2)); return 0
    except (AssertionError, KeyError, ValueError, OSError, TypeError) as error:
        print(json.dumps({'valid': False, 'scope': 'specification check', 'error': str(error)}), file=sys.stderr); return 1


if __name__ == '__main__':
    raise SystemExit(main())
