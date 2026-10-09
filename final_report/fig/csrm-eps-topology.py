#!/usr/bin/env python3
"""Render the proposed association of CSRM EPS groups with topology choices.

python3 final_report/fig/csrm-eps-topology.py --jobdir /absolute/external/check-dir

Alternatives are transcribed from El Hachimi et al., Fig. 1. Section 4 explains
conditioning, stage placement, battery/bus coupling and output distribution.
The associations below are proposed design mappings, not source CSRM links or
electrical flows. Repeated labels identify the same reference component group.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from diagram_style import Figure, INK, render_figure, require, sha

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
PAPER = ROOT / 'SLR/SLR1/pdfs/handpicked-reports/handpicked-report-0003/handpicked-report-0003.md'
BASE = FIG / 'csrm-eps-topology'
FONT = 12

# Category and alternative names follow Fig. 1. Label punctuation and case
# are normalized. The two associated groups per point are design allocations
# proposed for this framework, supported by the roles discussed in Section 4.
CHOICES = [
    {'id': 'conditioning', 'name': 'Power Conditioning', 'y': 84, 'height': 72,
     'alternatives': ['Direct Energy Transfer', 'MPPT'],
     'groups': [('Regulators and Converters', 'Conditioning stages'),
                ('Solar Arrays', 'Array operating point')]},
    {'id': 'transfer', 'name': 'Energy Transfer', 'y': 164, 'height': 72,
     'alternatives': ['Centralized', 'Distributed'],
     'groups': [('Regulators and Converters', 'Stage placement'),
                ('Power Circuits and Switches', 'Circuit placement')]},
    {'id': 'bus', 'name': 'DC Bus Regulation', 'y': 244, 'height': 88,
     'alternatives': ['Unregulated', 'Partially regulated', 'Fully regulated'],
     'groups': [('Regulators and Converters', 'Bus regulation'),
                ('Batteries', 'Battery/bus coupling')]},
    {'id': 'distribution', 'name': 'Power Distribution', 'y': 340, 'height': 72,
     'alternatives': ['DC-DC Converter', 'Bus Voltage'],
     'groups': [('Regulators and Converters', 'Load conversion'),
                ('Power Circuits and Switches', 'Output switching')]},
]


def csrm_inventory():
    spec = importlib.util.spec_from_file_location('csrm_structure', FIG / 'csrm-structure.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.inventory(), module.MODEL


def frame(figure, x, width, title):
    group = figure.el('g', data_frame=title)
    figure.rect(x, 44, width, 382, group)
    figure.text(title, x+12, 63, size=FONT, weight='bold', width=width-24, parent=group)
    return group


def create_figure():
    native, model = csrm_inventory()
    eps_types = {row[1] for row in native['Power Subsystem']}
    require(all(component in eps_types for choice in CHOICES for component, _ in choice['groups']),
            'Topology mapping contains an unknown CSRM EPS component')
    figure = Figure('CSRM EPS components and topology variation points', 690, 434)
    figure.text('CSRM EPS components and topology variation points', 8, 22,
                size=14, weight='bold')
    components = frame(figure, 8, 236, 'CSRM Power Subsystem')
    choices = frame(figure, 452, 230, 'EPS Topology Selection')
    routes = figure.el('g', data_relationship_kind='proposed design association')
    for choice in CHOICES:
        top = choice['y']
        target = figure.el('g', choices, data_variation_point=choice['id'])
        figure.rect(464, top, 206, choice['height'], target)
        figure.text(choice['name'], 567, top+19, size=FONT, weight='bold',
                    anchor='middle', width=186, parent=target)
        figure.el('path', target, d=f'M464 {top+28} H670', fill='none',
                  stroke=INK, stroke_width='.8')
        for index, alternative in enumerate(choice['alternatives']):
            figure.text(alternative, 567, top+44+index*16, size=11,
                        anchor='middle', width=186, parent=target,
                        data_alternative=alternative)
        for index, (component, role) in enumerate(choice['groups']):
            y = top+11+index*38
            group = figure.el('g', components, data_csrm_component=component,
                              data_applies_to=choice['id'])
            figure.rect(22, y, 210, 28, group)
            figure.text(component, 127, y+18, size=FONT, weight='bold',
                        anchor='middle', width=190, parent=group)
            source_y, target_y, bend = y+14, top+8+index*18, 434+index*12
            identifier = choice['id'] + '-' + str(index+1)
            # Both heads enter the variation-point header, never an alternative.
            figure.arrow(f'M232 {source_y} H{bend} V{target_y} H464', routes,
                         id='mapping-'+identifier, data_mapping=identifier,
                         data_component=component, data_variation_point=choice['id'],
                         data_role=role, data_relationship_kind='proposed design association')
            figure.text(role, 254, source_y-4, size=11, width=176, parent=routes,
                        data_mapping_label=identifier)
    return figure, native, model


def check_mapping(figure, native):
    root = figure.root
    expected = {(choice['id'], component, role)
                for choice in CHOICES for component, role in choice['groups']}
    shafts = root.findall('.//{*}path[@data-mapping]')
    actual = {(path.attrib['data-variation-point'], path.attrib['data-component'],
               path.attrib['data-role']) for path in shafts}
    require(len(shafts) == len(expected) == 8 and actual == expected,
            'Missing, repeated or changed topology association')
    require({group.attrib['data-csrm-component']
             for group in root.findall('.//{*}g[@data-csrm-component]')} <=
            {row[1] for row in native['Power Subsystem']}, 'Non-CSRM component label')
    require(all(path.attrib['data-relationship-kind'] == 'proposed design association'
                and 'stroke-dasharray' not in path.attrib for path in shafts),
            'Topology associations must remain distinct from control/exchange routes')
    require(len(root.findall('.//{*}g[@data-variation-point]')) == 4,
            'Expected four variation points')
    for choice in CHOICES:
        node = root.find(f'.//{{*}}g[@data-variation-point="{choice["id"]}"]')
        actual_alternatives = [text.text for text in node.findall('./{*}text[@data-alternative]')]
        require(actual_alternatives == choice['alternatives'], 'Changed topology alternatives')
        for path in shafts:
            if path.attrib['data-variation-point'] == choice['id']:
                from diagram_style import orthogonal_points
                x, y = orthogonal_points(path.attrib['d'])[-1]
                require(x == 464 and choice['y'] < y < choice['y']+28,
                        'A mapping points to an alternative instead of its variation point')
    return {'csrm_component_groups_checked': 4, 'variation_points_checked': 4,
            'alternatives_checked': 9, 'proposed_associations_checked': 8,
            'arrows_target_variation_points_only': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', type=Path, required=True)
    args = parser.parse_args()
    require(not args.jobdir.resolve().is_relative_to(ROOT), 'Use an external check directory')
    figure, native, model = create_figure()
    checks = check_mapping(figure, native)
    provenance = {
        'basis': 'CSRM component names and El Hachimi et al. (2025), Fig. 1 and Section 4',
        'mapping_status': 'Engineering associations proposed for this framework. No topology selected.',
        'model_sha256': sha(model), 'paper_sha256': sha(PAPER),
        'generator_sha256': sha(Path(__file__)),
        'shared_style_sha256': sha(FIG / 'diagram_style.py'),
        'variation_points_and_associations': CHOICES,
        'checks': checks,
        'output': render_figure(figure, BASE, args.jobdir),
    }
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
