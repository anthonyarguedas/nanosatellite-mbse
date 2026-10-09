#!/usr/bin/env python3
"""Redraw the cited systems engineering technical process in the report style.

python3 final_report/fig/systems-engineering-technical-processes.py --jobdir /absolute/external/check-dir
The labels and seven directed exchanges retain the content of Friedenthal et al.,
A Practical Guide to SysML, Figure 1.1. Requires Times New Roman, librsvg and Poppler.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from diagram_style import Figure, render_figure, require, sha

FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
BASE = FIG / 'systems-engineering-technical-processes'
W, H = 800, 324
NODES = {
    'needs': ((8, 80, 103, 72), ['Stakeholder', 'needs']),
    'design': ((141, 72, 174, 88), ['System specification', 'and design']),
    'components': ((360, 204, 204, 84), ['Component design,', 'implementation,', 'and test']),
    'integration': ((540, 72, 144, 88), ['System integration', 'and test']),
    'solution': ((710, 80, 82, 72), ['System', 'solution']),
}
FLOWS = [
    ('needs', 'design', 'M111 116 H141', 'solid', None, None),
    ('design', 'integration', 'M315 116 H540', 'solid', ['System requirements'], (337, 104)),
    ('design', 'components', 'M315 144 H414 V204', 'solid', ['Component', 'requirements'], (322, 176)),
    ('components', 'integration', 'M518 204 V144 H540', 'solid', ['Verified', 'components'], (428, 176)),
    ('integration', 'solution', 'M684 116 H710', 'solid', None, None),
    ('components', 'design', 'M360 250 H188 V160', 'dotted', ['Design feedback'], (216, 241)),
    ('integration', 'design', 'M612 160 V311 H162 V160', 'dashdot', ['I&T feedback'], (624, 254)),
]


def create_figure():
    figure = Figure('Systems engineering technical processes', W, H)
    figure.el('desc').text = (
        'Stakeholder needs inform system specification and design. System requirements '
        'feed system integration and test. Component requirements guide component '
        'design, implementation and test. Verified components feed integration, '
        'which produces the system solution. Distinct dotted and dash-dot feedback '
        'routes return from component work and integration to system design.')
    figure.text('Systems engineering technical processes', 8, 22, size=18, weight='bold')
    for identifier, (box, labels) in NODES.items():
        group = figure.el('g', data_node=identifier)
        x, y, w, h = box
        figure.rect(*box, parent=group)
        first_line = y+(h-18*(len(labels)-1))/2+5
        figure.lines(labels, x+w/2, first_line, size=15, leading=18,
                     weight='bold', anchor='middle', parent=group, width=w-12)
    for index, (origin, target, d, style, labels, position) in enumerate(FLOWS, 1):
        group = figure.el('g', id=f'process-flow-{index}', data_source=origin,
                          data_target=target, data_line_style=style)
        figure.arrow(d, group, style=style)
        if labels:
            figure.lines(labels, *position, size=15, leading=18, parent=group)
    return figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobdir', required=True, type=Path)
    args = parser.parse_args()
    job = args.jobdir.resolve()
    require(job != ROOT and ROOT not in job.parents, 'Check artifacts must remain outside the checkout')
    figure = create_figure()
    provenance = render_figure(figure, BASE, job)
    provenance.update(kind='Authored illustrative adaptation of a cited technical process diagram',
        producer='systems-engineering-technical-processes.py using the shared monochrome serif style',
        source='Friedenthal et al., A Practical Guide to SysML, Figure 1.1',
        generator_sha256=sha(Path(__file__)), style_sha256=sha(FIG / 'diagram_style.py'),
        directed_exchanges=[{'source': origin, 'target': target, 'path': d, 'line_style': style,
                             'label': ' '.join(labels or [])}
                            for origin, target, d, style, labels, _ in FLOWS],
        reproduction=['python3 final_report/fig/systems-engineering-technical-processes.py --jobdir /absolute/external/check-dir'])
    BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(json.dumps({'checks': provenance['checks'], 'dimensions': provenance['dimensions']}, indent=2))


if __name__ == '__main__':
    main()
