#!/usr/bin/env python3
"""Render three authored CSRM structure views using the report's shared style.

python3 final_report/fig/csrm-structure.py --jobdir /absolute/external/check-dir

The source is the translated 2025 CSRM architecture. Checks below compare
selected part names, types and multiplicities. They do not establish SysML
conformance, execute constraints or validate the incomplete translation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from diagram_style import Figure, LIGHT, SerifMetrics, render_figure, require, sha

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
MODEL = ROOT / 'csrm-sysmlv2/model.sysml'
FONT = 12

# Exact native names and types. Display labels only normalize capitalization
# and omit generated instance-name suffixes. No electrical flows are inferred.
EXPECTED = {
    'CubeSat Domain': [
        ('external Constraints', 'External Constraints', '1..1'),
        ('external Environment', 'External Environment', '1..1'),
        ('cubeSat Mission Enterprise', 'CubeSat Mission', '1..1'),
    ],
    'CubeSat Mission': [
        ('ground Station Services', 'Ground Station Services', '1..1'),
        ('', 'Transport, Launch, and Deploy Services', '1..1'),
        ('space Segment', 'Space Segment', '1..1'),
        ('ground Segment', 'Ground Segment', '1..1'),
        ('GPS', 'GNSS', '1..1'),
    ],
    'Space Segment': [
        ('cubeSat', 'CubeSat', '1..*'),
        ('cubeSat Orbit', 'CubeSat Orbit', '1..*'),
    ],
    'CubeSat': [
        ('mission Payload1', 'Mission Payload Subsystem', '1..1'),
        ('command and Data Handling Subsystem1', 'Command and Data Handling Subsystem', '1..1'),
        ('communication Subsystem1', 'Communication Subsystem', '1..1'),
        ('attitude Determination and Control Subsystem1', 'Attitude Determination and Control Subsystem', '1..1'),
        ('guidance Navigation and Control Subsystem', 'Guidance Navigation and Control Subsystem', '1..1'),
        ('structures and Mechanisms Subsystem1', 'Structures and Mechanisms Subsystem', '1..1'),
        ('power Subsystem1', 'Power Subsystem', '1..1'),
        ('propulsion Subsystem1', 'Propulsion Subsystem', '1..1'),
        ('thermal Subsystem1', 'Thermal Subsystem', '1..1'),
    ],
    'Power Subsystem': [
        ('batteries', 'Batteries', '1..1'),
        ('regulators and Converters', 'Regulators and Converters', '1..1'),
        ('solar Arrays', 'Solar Arrays', '1..1'),
        ('power Circuits and Switches', 'Power Circuits and Switches', '1..1'),
        ('processor and Memory', 'Processor and Memory', '1..1'),
        ('software', 'Software', '1..1'),
    ],
}
SUBSYSTEM_LABELS = [
    ['Mission Payload', 'Subsystem [1]'],
    ['Command and Data', 'Handling Subsystem [1]'],
    ['Communication', 'Subsystem [1]'],
    ['Attitude Determination', 'and Control Subsystem', '[1]'],
    ['Guidance Navigation', 'and Control Subsystem', '[1]'],
    ['Structures and Mechanisms', 'Subsystem [1]'],
    ['Power Subsystem [1]'],
    ['Propulsion Subsystem [1]'],
    ['Thermal Subsystem [1]'],
]
EPS_LABELS = [
    ['Batteries [1]'],
    ['Regulators and', 'Converters [1]'],
    ['Solar Arrays [1]'],
    ['Power Circuits and', 'Switches [1]'],
    ['Processor and Memory', '[1]'],
    ['Software [1]'],
]


def definition_body(text, name):
    """Extract a definition body while ignoring braces in strings/comments."""
    identifier = re.escape(name if name == 'CubeSat' else "'" + name + "'")
    matches = list(re.finditer(r'\bpart def ' + identifier + r'(?=\s|\{)[^{]*\{', text))
    require(len(matches) == 1, 'Expected one architecture definition: ' + name)
    start = matches[0].end()
    token = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]', re.S)
    depth = 1
    for match in token.finditer(text, start):
        if match[0] == '{':
            depth += 1
        elif match[0] == '}':
            depth -= 1
            if depth == 0:
                return text[start:match.start()]
    raise ValueError('Unclosed architecture definition: ' + name)


def inventory(text=None):
    text = MODEL.read_text() if text is None else text
    result = {}
    pattern = re.compile(
        r'^\s*part\s+(?:(\'[^\']+\'|\w+)\s*)?:\s*([^\n]+?)\s+\[(\d+\.\.(?:\d+|\*))\]', re.M)
    for owner, expected in EXPECTED.items():
        rows = []
        for match in pattern.finditer(definition_body(text, owner)):
            rows.append(((match[1] or '').strip("'"),
                         match[2].rsplit('::', 1)[-1].strip("'"), match[3]))
        require(rows == expected, 'Changed native structure: ' + owner)
        result[owner] = rows
    cube_sat = definition_body(text, 'CubeSat')
    require(re.search(r"ref part 'Orbit'\s*:[^\n]+::'CubeSat Orbit' \[1\.\.1\]", cube_sat),
            'Expected the typed CubeSat orbit reference')
    result['orbit_reference'] = ('Orbit', 'CubeSat Orbit', '1..1')
    return result


def part_attributes(owner, typ):
    matches = [row for row in EXPECTED[owner] if row[1] == typ]
    require(len(matches) == 1, 'Ambiguous displayed part: ' + owner + ' / ' + typ)
    name, _, multiplicity = matches[0]
    return dict(data_owner=owner, data_part=name, data_type=typ,
                data_multiplicity=multiplicity)


def enclosure(figure, x, y, w, h, title, parent=None, **attrs):
    group = figure.el('g', parent, **attrs)
    figure.rect(x, y, w, h, group)
    figure.text(title, x+12, y+19, size=FONT, weight='bold',
                width=w-24, parent=group)
    return group


def block(figure, x, y, w, h, labels, owner, typ, parent=None, external=False):
    group = figure.el('g', parent, **part_attributes(owner, typ),
                      data_external=str(external).lower())
    figure.rect(x, y, w, h, group, fill=LIGHT if external else 'white')
    first = y+h/2-(len(labels)-1)*15/2+FONT*.33
    figure.lines(labels, x+w/2, first, leading=15, size=FONT,
                 weight='bold', anchor='middle', width=w-20, parent=group)
    return group


def mission_view(metrics=None):
    figure = Figure('CSRM: mission and segment structure', 690, 420, metrics)
    figure.text('CSRM: mission and segment structure', 8, 22, size=14, weight='bold')
    domain = enclosure(figure, 8, 44, 674, 368, 'CubeSat Domain',
                       data_definition='CubeSat Domain')
    block(figure, 22, 76, 315, 48, ['External Environment [1]'],
          'CubeSat Domain', 'External Environment', domain, external=True)
    block(figure, 350, 76, 315, 48, ['External Constraints [1]'],
          'CubeSat Domain', 'External Constraints', domain, external=True)
    mission = enclosure(figure, 22, 136, 644, 262, 'CubeSat Mission Enterprise [1]', domain,
                        **part_attributes('CubeSat Domain', 'CubeSat Mission'))
    space = enclosure(figure, 38, 176, 367, 122, 'Space Segment [1]', mission,
                      **part_attributes('CubeSat Mission', 'Space Segment'))
    cube_sat = figure.el('g', space, **part_attributes('Space Segment', 'CubeSat'))
    figure.rect(50, 216, 176, 65, cube_sat)
    figure.text('CubeSat [1..*]', 138, 238, size=FONT, weight='bold',
                anchor='middle', width=156, parent=cube_sat)
    figure.el('path', cube_sat, d='M50 248 H226', fill='none', stroke='#111111', stroke_width='.8')
    figure.text('ref Orbit : CubeSat Orbit [1]', 138, 268, size=11,
                anchor='middle', width=156, parent=cube_sat, data_reference='Orbit')
    block(figure, 249, 216, 142, 65, ['CubeSat Orbit', '[1..*]'],
          'Space Segment', 'CubeSat Orbit', space)
    block(figure, 425, 216, 225, 65, ['Ground Segment [1]'],
          'CubeSat Mission', 'Ground Segment', mission)
    block(figure, 38, 326, 180, 56, ['Ground Station', 'Services [1]'],
          'CubeSat Mission', 'Ground Station Services', mission, external=True)
    block(figure, 240, 326, 230, 56, ['Transport, Launch,', 'and Deploy Services [1]'],
          'CubeSat Mission', 'Transport, Launch, and Deploy Services', mission, external=True)
    block(figure, 492, 326, 158, 56, ['GPS : GNSS [1]'],
          'CubeSat Mission', 'GNSS', mission, external=True)
    return figure


def grid_view(title, owner, labels, height, metrics=None):
    figure = Figure(title, 690, height, metrics)
    figure.text(title, 8, 22, size=14, weight='bold')
    frame = enclosure(figure, 8, 44, 674, height-54, owner, data_definition=owner)
    require(len(labels) == len(EXPECTED[owner]), 'Incomplete grid: ' + owner)
    for index, (row, lines) in enumerate(zip(EXPECTED[owner], labels)):
        x, y = 24+(index % 3)*222, 94+(index // 3)*78
        block(figure, x, y, 198, 64, lines, owner, row[1], frame)
    return figure


def subsystem_view(metrics=None):
    return grid_view('CSRM: CubeSat subsystems', 'CubeSat', SUBSYSTEM_LABELS, 340, metrics)


def eps_view(metrics=None):
    return grid_view('CSRM: EPS components', 'Power Subsystem', EPS_LABELS, 262, metrics)


def check_coverage(figures, native):
    expected = {(owner, *row) for owner in EXPECTED for row in native[owner]}
    displayed = []
    for figure in figures:
        for group in figure.root.findall('.//{*}g[@data-part]'):
            displayed.append(tuple(group.attrib[key] for key in
                ('data-owner', 'data-part', 'data-type', 'data-multiplicity')))
    require(len(displayed) == len(expected) and set(displayed) == expected,
            'Missing, repeated or invented structural part')
    require(not any(figure.root.findall('.//{*}path[@data-terminal-head]') for figure in figures),
            'Structure views must not introduce exchange arrows')
    require(sum(len(figure.root.findall('.//{*}text[@data-reference="Orbit"]'))
                for figure in figures) == 1, 'Missing or repeated orbit reference')
    return {'selected_native_parts_checked': len(expected),
            'cube_sat_subsystems_checked': len(native['CubeSat']),
            'eps_component_groups_checked': len(native['Power Subsystem']),
            'no_invented_exchange_arrows': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', type=Path, required=True)
    args = parser.parse_args()
    require(not args.jobdir.resolve().is_relative_to(ROOT), 'Use an external check directory')
    native, metrics = inventory(), SerifMetrics()
    figures = [mission_view(metrics), subsystem_view(metrics), eps_view(metrics)]
    checks = check_coverage(figures, native)
    names = ['csrm-mission-structure', 'csrm-cubesat-subsystems', 'csrm-eps-components']
    outputs = {name: render_figure(figure, FIG / name, args.jobdir)
               for name, figure in zip(names, figures)}
    provenance = {
        'basis': 'Selected part definitions from the translated 2025 CSRM architecture',
        'model_sha256': sha(MODEL),
        'generator_sha256': sha(Path(__file__)),
        'shared_style_sha256': sha(FIG / 'diagram_style.py'),
        'checks': checks,
        'native_parts': native,
        'outputs': outputs,
        'limitations': 'Source and drawing checks only. No runtime evaluation or claim of translation completeness.',
    }
    (FIG / 'csrm-structure.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
