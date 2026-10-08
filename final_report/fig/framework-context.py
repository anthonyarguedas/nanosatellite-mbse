#!/usr/bin/env python3
"""Author an illustrative context SVG, then render that exact SVG with librsvg.

Usage: python3 final_report/fig/framework-context.py --jobdir /absolute/check-directory
The check directory must be outside the checkout. Requires rsvg-convert and
Poppler's pdfinfo and pdftotext. No native SysML rendering or simulation occurs.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jobdir', type=Path, required=True)
args = parser.parse_args()
FIG = Path(__file__).resolve().parent
ROOT = FIG.parent.parent
JOB = args.jobdir.resolve()
if JOB == ROOT or ROOT in JOB.parents:
    parser.error('Check artifacts must remain outside the checkout')
JOB.mkdir(parents=True, exist_ok=True)
BASE = FIG / 'framework-context'
W, H = 1600, 570
INK, MUTED, BLUE, GREEN = '#243442', '#56636f', '#466f8d', '#567b70'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
svg = ET.Element(f'{{{NS}}}svg', {
    'width': str(W), 'height': str(H), 'viewBox': f'0 0 {W} {H}',
    'role': 'img', 'aria-labelledby': 'title description',
})
ET.SubElement(svg, f'{{{NS}}}title', {'id': 'title'}).text = 'EPS engineering framework: system context'
ET.SubElement(svg, f'{{{NS}}}desc', {'id': 'description'}).text = (
    'Illustrative black-box system context with five interfaces. Engineers, '
    'sources and reviewers exchange information with the framework. NVIDIA '
    'Omniverse whole CUBICS simulation and model tools supply spacecraft '
    'scenario histories and raw numerical results and receive controlled '
    'model/run requests and EPS responses for the same scenario. The F Prime '
    'host toolchain receives authorized detailed design and coding/build/SIL '
    'requests and returns host products, logs and SIL results.')

def element(name, **attrs):
    return ET.SubElement(svg, f'{{{NS}}}{name}', {k.replace('_', '-'): str(v) for k, v in attrs.items()})

def rect(x, y, w, h, **attrs):
    return element('rect', x=x, y=y, width=w, height=h, **attrs)

text_regions = []
def text(value, x, y, size=28, color=INK, weight='400', anchor='middle', bounds=None):
    node = element('text', x=x, y=y, font_family='Arial, sans-serif', font_size=size,
                   fill=color, font_weight=weight, text_anchor=anchor)
    node.text = value
    if bounds:
        text_regions.append({'text': value, 'x': x, 'y': y, 'size': size, 'bounds': bounds})
    return node

def path(d, color=INK, start=False, end=False):
    attrs = {'d': d, 'fill': 'none', 'stroke': color, 'stroke-width': '2.5',
             'stroke-linejoin': 'round'}
    if start:
        attrs['marker-start'] = f'url(#{color[1:]})'
    if end:
        attrs['marker-end'] = f'url(#{color[1:]})'
    return element('path', **attrs)

rect(0, 0, W, H, fill='white')
defs = element('defs')
for color in (INK, BLUE, GREEN):
    marker = ET.SubElement(defs, f'{{{NS}}}marker', {
        'id': color[1:], 'viewBox': '0 0 10 10', 'refX': '9', 'refY': '5',
        'markerWidth': '9', 'markerHeight': '9', 'markerUnits': 'userSpaceOnUse',
        'orient': 'auto-start-reverse',
    })
    ET.SubElement(marker, f'{{{NS}}}path', {'d': 'M 0 0 L 10 5 L 0 10 Z', 'fill': color})

# One unpartitioned framework box with exactly five interface ports.
rect(600, 40, 245, 480, rx=8, fill='white', stroke=INK, stroke_width=2.5)
for line, y in [('EPS', 253), ('engineering', 293), ('framework', 333)]:
    text(line, 722.5, y, size=34, weight='600', bounds=[614, 831])

# Human and information roles. Their overview arrows are bidirectional.
left_roles = [
    ('IF-01', 50, ['Engineers and', 'stakeholders']),
    ('IF-02', 220, ['Knowledge and', 'supplied data']),
    ('IF-06', 390, ['Reviewers and', 'review authority']),
]
for identifier, y, lines in left_roles:
    rect(20, y, 265, 125, rx=8, fill='#fafbfc', stroke='#c4ccd2', stroke_width=1.5)
    text(lines[0], 152.5, y + 41, size=30, bounds=[32, 273])
    text(lines[1], 152.5, y + 76, size=30, bounds=[32, 273])
    text(identifier, 152.5, y + 109, size=24, color=MUTED, bounds=[32, 273])

for y in (110, 280, 450):
    path(f'M 286 {y} H 593', start=True, end=True)

for value, y in [('Engineering submissions', 66), ('Authorized decisions', 96),
                 ('Guidance and products', 147), ('Source data', 264),
                 ('Source queries', 317), ('Findings', 406),
                 ('Authorized decisions', 436), ('Review packages', 487)]:
    text(value, 440, y, size=26, bounds=[294, 586])

# Numerical simulation exchange. Both branches attach to the same IF-03 port.
rect(1260, 50, 320, 235, rx=8, fill='#f7fafc', stroke='#b4c5d2', stroke_width=1.5)
text('IF-03', 1420, 83, size=24, color=BLUE, bounds=[1272, 1568])
for value, y in [('NVIDIA Omniverse', 126), ('whole CUBICS', 160),
                 ('simulation and', 194), ('model tools', 228)]:
    text(value, 1420, y, size=30, bounds=[1272, 1568])
path('M 852 174 H 874 V 135 H 1259', color=BLUE, end=True)
path('M 1259 219 H 874 V 174 H 852', color=BLUE, end=True)
for value, y in [('Controlled model/run requests', 58),
                 ('EPS states and results', 87), ('For the same scenario', 116),
                 ('Spacecraft/subsystem histories', 168),
                 ('Raw numerical results/status', 201)]:
    text(value, 1063, y, size=26, color=BLUE, bounds=[883, 1249])
text('Numerical exchange', 1063, 260, size=24, color=MUTED, bounds=[883, 1249])

# Host software exchange. Both branches attach to the same IF-04 port.
rect(1260, 345, 320, 170, rx=8, fill='#f8fbf9', stroke='#bdcec6', stroke_width=1.5)
text('IF-04', 1420, 379, size=24, color=GREEN, bounds=[1272, 1568])
text('F Prime', 1420, 426, size=32, bounds=[1272, 1568])
text('host toolchain', 1420, 464, size=30, bounds=[1272, 1568])
path('M 852 422 H 874 V 394 H 1259', color=GREEN, end=True)
path('M 1259 492 H 874 V 422 H 852', color=GREEN, end=True)
for value, y in [('Authorized detailed design', 344), ('Coding/build/SIL requests', 376),
                 ('Host products and logs', 440), ('SIL results', 472)]:
    text(value, 1063, y, size=26, color=GREEN, bounds=[883, 1249])

for x, y, color in [(600, 110, INK), (600, 280, INK), (600, 450, INK),
                     (845, 174, BLUE), (845, 422, GREEN)]:
    rect(x - 7, y - 7, 14, 14, fill='white', stroke=color, stroke_width=2.5)
text('Illustrative system context', 20, 558, size=24, color=MUTED, anchor='start', bounds=[20, 700])
text('SIL: software in the loop', 1580, 558, size=24, color=MUTED, anchor='end', bounds=[1000, 1580])

ET.indent(svg)
ET.ElementTree(svg).write(BASE.with_suffix('.svg'), encoding='utf-8', xml_declaration=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(argv):
    return subprocess.run(argv, check=True, capture_output=True, text=True).stdout

svg_hash = sha(BASE.with_suffix('.svg'))
version = run(['rsvg-convert', '--version']).strip()
for kind in ('pdf', 'png'):
    run(['rsvg-convert', '--format', kind, '--output', str(BASE.with_suffix('.' + kind)),
         str(BASE.with_suffix('.svg'))])
assert sha(BASE.with_suffix('.svg')) == svg_hash, 'Source changed during rendering'
pdfinfo = run(['pdfinfo', str(BASE.with_suffix('.pdf'))])
(JOB / 'pdfinfo.txt').write_text(pdfinfo)
run(['pdftotext', '-bbox', str(BASE.with_suffix('.pdf')), str(JOB / 'pdf-text-bounds.html')])
words = ET.parse(JOB / 'pdf-text-bounds.html').getroot().findall('.//{*}word')
# Poppler reports points. librsvg maps one SVG pixel to 0.75 PDF points.
for word in words:
    x0, x1, y0, y1 = [float(word.attrib[key]) / .75 for key in ('xMin', 'xMax', 'yMin', 'yMax')]
    assert 0 <= x0 <= x1 <= W and 0 <= y0 <= y1 <= H, ('Page clipping', word.text)
    candidates = [region for region in text_regions
                  if abs((y0 + y1) / 2 - (region['y'] - region['size'] * .30)) < region['size'] * .35
                  and region['bounds'][0] - 1 <= x0 and x1 <= region['bounds'][1] + 1]
    assert candidates, ('Label exceeds its allotted region', word.text, x0, x1, y0, y1)
assert len(words) > 80, 'Expected extractable text labels'
png_bytes = BASE.with_suffix('.png').read_bytes()
assert struct.unpack('>II', png_bytes[16:24]) == (W, H)

interfaces = {
    'IF01': {'label': 'IF-01', 'type': 'BoundaryViews::EngineeringUseInterface',
             'framework_port': 'p01', 'port_type': 'BoundaryViews::EngineeringUsePort',
             'external_port': 'engineers.p', 'in': ['engineeringSubmission'], 'out': ['engineeringResponse']},
    'IF02': {'label': 'IF-02', 'type': 'BoundaryViews::KnowledgeInterface',
             'framework_port': 'p02', 'port_type': 'BoundaryViews::KnowledgePort',
             'external_port': 'sources.p', 'in': ['sourceSubmission'], 'out': ['sourceQuery']},
    'IF03': {'label': 'IF-03', 'type': 'BoundaryViews::AnalysisInterface',
             'framework_port': 'p03', 'port_type': 'BoundaryViews::AnalysisPort',
             'external_port': 'tools.p', 'in': ['analysisResponse', 'analysisResult', 'spacecraftInputs'],
             'out': ['analysisRequest', 'analysisPlan', 'epsResponses'],
             'numerical_counterparts': {'AnalysisPort::spacecraftInputs': 'ReferenceData (in)',
                                        'AnalysisPort::epsResponses': 'AnalysisResult (out)'}},
    'IF04': {'label': 'IF-04', 'type': 'BoundaryViews::HostSoftwareInterface',
             'framework_port': 'p04', 'port_type': 'BoundaryViews::HostSoftwarePort',
             'external_port': 'software.p', 'in': ['codingResponse', 'softwareProduct', 'softwareResult'],
             'out': ['codingRequest', 'interfaceSpecification']},
    'IF06': {'label': 'IF-06', 'type': 'BoundaryViews::TechnicalReviewInterface',
             'framework_port': 'p06', 'port_type': 'BoundaryViews::TechnicalReviewPort',
             'external_port': 'reviewers.p', 'in': ['reviewSubmission'], 'out': ['reviewResponse']},
}
checks = {'five_interface_ports': True, 'exact_svg_preserved_during_conversion': True,
          'pdf_single_page': 'Pages:           1' in pdfinfo,
          'extractable_pdf_text_within_page_and_label_regions': True,
          'png_dimensions': [W, H], 'png_visual_inspection': 'Requires manual inspection after regeneration',
          'native_model_check': 'Not performed; illustration only', 'simulation_execution': 'Not performed'}
provenance = {
    'kind': 'Authored illustrative black-box system context',
    'producer': 'framework-context.py using Python XML authoring and rsvg-convert',
    'rendering': version, 'native_syside_render': False, 'executed_simulation': False,
    'typed_counterpart': 'FrameworkContext::Context', 'interface_counterparts': interfaces,
    'model_reference_files': [{ 'path': str(path.relative_to(ROOT)), 'sha256': sha(path)} for path in
                             [ROOT / 'final_report/sysml/06-system-context.sysml',
                              ROOT / 'final_report/sysml/10-interface-views.sysml']],
    'normative_inputs': ['Stakeholder constraints supplied in the figure task',
                         'Approved task4-turn01-plan.md handoff'],
    'coordination_note': 'Required external platform labels and the spacecraftInputs/epsResponses '
                         'features incorporate approved companion model changes. Those changes '
                         'are not represented as having been natively rendered or executed.',
    'dimensions': {'svg_px': [W, H], 'png_px': [W, H], 'pdf_pt': [W * .75, H * .75]},
    'svg_sha256_used_for_pdf': svg_hash, 'svg_sha256_used_for_png': svg_hash,
    'artifact_sha256': {kind: sha(BASE.with_suffix('.' + kind)) for kind in ('svg', 'pdf', 'png')},
    'reproduction': ['python3 final_report/fig/framework-context.py --jobdir /absolute/external/check-directory'],
    'checks': checks,
}
BASE.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
paths = [BASE.with_suffix('.' + extension) for extension in ('svg', 'pdf', 'png', 'provenance.json', 'py')]
exports = {'created_paths': [str(path.relative_to(ROOT)) for path in paths],
           'producer': provenance['producer'], 'dimensions': provenance['dimensions'],
           'checks': checks, 'svg_sha256_used_for_pdf': svg_hash,
           'integration': 'Replace the existing context figure. The parent updates the report include.'}
(JOB / 'exports.json').write_text(json.dumps(exports, indent=2) + '\n')
print(json.dumps(exports, indent=2))
