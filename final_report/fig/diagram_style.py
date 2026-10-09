"""Shared monochrome, serif presentation for the report's authored diagrams."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET

FONT_FAMILY = 'Times New Roman'
FONT_STACK = 'Times New Roman, Times, serif'
INK = '#111111'
MUTED = '#444444'
LIGHT = '#f5f5f5'
ARROW_LENGTH, ARROW_HEIGHT = 12, 9
PORT_WIDTH, PORT_PADDING = 18, 8
LINE_PATTERNS = {
    'solid': None,
    'dotted': '1 3',
    'dashdot': '7 2.5 1 2.5',
    'dashed': '4 2.5',
}
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(argv):
    import os
    environment = dict(os.environ, SOURCE_DATE_EPOCH='0')
    return subprocess.run(argv, check=True, capture_output=True, text=True,
                          env=environment).stdout


class Metrics:
    """Read actual serif TrueType advances without additional Python packages."""
    def __init__(self, filename):
        self.path = Path(filename)
        self.data = self.path.read_bytes()
        b, tables = self.data, {}
        for i in range(struct.unpack_from('>H', b, 4)[0]):
            tag, _, offset, _ = struct.unpack_from('>4sIII', b, 12 + 16*i)
            tables[tag.decode()] = offset
        self.units = struct.unpack_from('>H', b, tables['head'] + 18)[0]
        n = struct.unpack_from('>H', b, tables['hhea'] + 34)[0]
        self.widths = [struct.unpack_from('>H', b, tables['hmtx'] + 4*i)[0]
                       for i in range(n)]
        c, candidates = tables['cmap'], []
        for i in range(struct.unpack_from('>H', b, c + 2)[0]):
            platform, encoding, offset = struct.unpack_from('>HHI', b, c + 4 + i*8)
            base = c + offset
            if struct.unpack_from('>H', b, base)[0] == 4:
                candidates.append((platform == 3 and encoding == 1, base))
        require(candidates, 'Font lacks a Unicode format-4 character map')
        self.cmap = max(candidates)[1]
        self.segments = struct.unpack_from('>H', b, self.cmap + 6)[0] // 2

    def glyph(self, code):
        b, base, n = self.data, self.cmap, self.segments
        for i in range(n):
            end = struct.unpack_from('>H', b, base + 14 + 2*i)[0]
            start = struct.unpack_from('>H', b, base + 16 + 2*n + 2*i)[0]
            if start <= code <= end:
                delta = struct.unpack_from('>h', b, base + 16 + 4*n + 2*i)[0]
                loc = base + 16 + 6*n + 2*i
                offset = struct.unpack_from('>H', b, loc)[0]
                if offset:
                    gid = struct.unpack_from('>H', b, loc + offset + 2*(code-start))[0]
                    return (gid + delta) & 65535 if gid else 0
                return (code + delta) & 65535
        return 0

    def measure(self, value, size=11):
        return sum(self.widths[min(self.glyph(ord(c)), len(self.widths)-1)]
                   for c in value) * size / self.units


class SerifMetrics:
    """Measure regular and bold text using the same font files as librsvg."""
    def __init__(self):
        self.fonts = {}
        for weight, style in [('normal', 'Regular'), ('bold', 'Bold')]:
            result = run(['fc-match', '-f', '%{family}\n%{file}',
                          f'{FONT_FAMILY}:style={style}']).strip().splitlines()
            require(len(result) == 2 and FONT_FAMILY in result[0],
                    f'Install {FONT_FAMILY} ({style}) before regenerating diagrams')
            self.fonts[weight] = Metrics(result[1])

    def measure(self, value, size=11, weight='normal'):
        return self.fonts['bold' if weight in ('bold', '600', '700') else 'normal'].measure(value, size)

    def provenance(self):
        return {'family': FONT_FAMILY, 'files': {
            weight: {'path': str(font.path), 'sha256': sha(font.path)}
            for weight, font in self.fonts.items()}}


def line_attributes(style):
    require(style in LINE_PATTERNS, 'Unknown line pattern: '+style)
    attrs = {'stroke-linecap': 'round'}
    if LINE_PATTERNS[style]:
        attrs['stroke-dasharray'] = LINE_PATTERNS[style]
    return attrs


def arrow_marker(figure, defs, name='arrow'):
    marker = figure.el('marker', defs, id=name,
        viewBox=f'0 0 {ARROW_LENGTH} {ARROW_HEIGHT}', refX=ARROW_LENGTH,
        refY=ARROW_HEIGHT/2, markerWidth=ARROW_LENGTH, markerHeight=ARROW_HEIGHT,
        markerUnits='userSpaceOnUse', orient='auto', overflow='visible')
    figure.el('path', marker,
        d=f'M0 0 L{ARROW_LENGTH} {ARROW_HEIGHT/2} L0 {ARROW_HEIGHT} Z', fill=INK)


def shared_port(figure, parent, interface, port, x, levels, features, label_size=11):
    """Label the boundary port itself, leaving every crossing unobstructed."""
    levels = sorted(set(levels))
    first, last = levels[0], levels[-1]
    span = figure.metrics.measure(interface, label_size, 'bold')
    gaps = [(a+b)/2 for a, b in zip(levels, levels[1:]) if b-a >= span+10]
    if gaps:
        label_y = min(gaps, key=lambda y: abs(y-(first+last)/2))
        bottom = last+PORT_PADDING
    else:
        label_y = last+PORT_PADDING+span/2
        bottom = label_y+span/2+PORT_PADDING
    rect = figure.rect(x-PORT_WIDTH/2, first-PORT_PADDING, PORT_WIDTH,
        bottom-first+PORT_PADDING, parent, fill='white', color=INK,
        data_port=port, data_interface=interface, data_owner='Framework',
        data_boundary_x=x, data_features=','.join(features))
    figure.text(interface, x, label_y+label_size*.35, size=label_size,
        weight='bold', anchor='middle', parent=parent,
        transform=f'rotate(-90 {x:g} {label_y:g})', data_port_label=port,
        data_interface_label=interface, data_label_y=label_y, data_label_span=span)
    return rect


def validate_port_labels(root):
    ports = root.findall('.//{*}rect[@data-port]')
    labels = root.findall('.//{*}text[@data-port-label]')
    require(len(labels) == len(ports), 'Expected one label on each port rectangle')
    for port in ports:
        matches = [label for label in labels if label.attrib['data-port-label'] == port.attrib['data-port']]
        require(len(matches) == 1, 'Missing/duplicate interface label on port')
        label = matches[0]
        x, y, w, h = [float(port.attrib[a]) for a in ('x', 'y', 'width', 'height')]
        cx, cy, span = float(label.attrib['x']), float(label.attrib['data-label-y']), float(label.attrib['data-label-span'])
        require(label.text == port.attrib['data-interface'] == label.attrib['data-interface-label']
                and cx == x+w/2 and y <= cy-span/2 <= cy+span/2 <= y+h
                and float(label.attrib['font-size']) <= w-4
                and label.attrib.get('transform') == f'rotate(-90 {cx:g} {cy:g})',
                'Interface label is outside its port rectangle')
    visible_ids = [text for text in root.findall('.//{*}text')
                   if re.fullmatch(r'IF-\d\d', text.text or '')]
    require(len(visible_ids) == len(labels), 'Interface identifier is repeated away from its port')
    return {'interface_labels_on_ports_checked': True}


def orthogonal_points(d):
    commands = re.findall(r'([MHV])([\d.]+)(?: ([\d.]+))?', d)
    require(commands and commands[0][0] == 'M', 'Unsupported arrow geometry')
    require(re.fullmatch(r'M\d+(?:\.\d+)? \d+(?:\.\d+)?(?: [HV]\d+(?:\.\d+)?)*', d),
            'Unsupported arrow geometry')
    points = [(float(commands[0][1]), float(commands[0][2]))]
    for command, a, _ in commands[1:]:
        points.append((float(a), points[-1][1]) if command == 'H'
                      else (points[-1][0], float(a)))
    return points


def foreground_arrowheads(root):
    """Render one head at each true destination, above all other elements.

    Shafts declare their terminal marker as metadata. The foreground layer
    is the only place that paints it. Intermediate port crossings have no head.
    """
    previous = root.find('./{*}g[@data-layer="arrowheads"]')
    if previous is not None:
        root.remove(previous)
    arrows = [node for node in root.iter(f'{{{NS}}}path')
              if node.attrib.get('data-terminal-head') == 'true']
    layer = ET.SubElement(root, f'{{{NS}}}g', {'data-layer': 'arrowheads', 'pointer-events': 'none'})
    for arrow in arrows:
        points = orthogonal_points(arrow.attrib['d'])
        x, y = points[-1]
        px, py = next(point for point in reversed(points[:-1]) if point != (x, y))
        if x != px:
            d = f'M{x-(1 if x > px else -1):g} {y:g} H{x:g}'
        else:
            d = f'M{x:g} {y-(1 if y > py else -1):g} V{y:g}'
        ET.SubElement(layer, f'{{{NS}}}path', {
            'd': d, 'fill': 'none', 'stroke': INK,
            'stroke-width': arrow.attrib['stroke-width'],
            'marker-end': arrow.attrib['data-end-marker'], 'data-arrow-source': arrow.attrib['id']})


def validate_arrowheads(root):
    layer = root.find('./{*}g[@data-layer="arrowheads"]')
    require(layer is not None and list(root)[-1] is layer,
            'Arrowheads must be the final foreground layer')
    shafts = [node for node in root.iter(f'{{{NS}}}path') if 'data-terminal-head' in node.attrib]
    require(all('marker-end' not in node.attrib for node in shafts),
            'A shaft duplicates its foreground arrowhead')
    arrows = [node for node in shafts if node.attrib['data-terminal-head'] == 'true']
    require(root.findall('.//{*}path[@marker-end]') == list(layer),
            'Arrowheads are painted outside the terminal foreground layer')
    require({node.attrib['data-arrow-source'] for node in layer} ==
            {node.attrib['id'] for node in arrows} and len(layer) == len(arrows),
            'Missing/duplicate foreground arrowhead')
    by_id = {node.attrib['id']: node for node in arrows}
    for head in layer:
        original = by_id[head.attrib['data-arrow-source']]
        require(orthogonal_points(head.attrib['d'])[-1] == orthogonal_points(original.attrib['d'])[-1]
                and head.attrib['marker-end'] == original.attrib['data-end-marker'],
                'Foreground arrowhead has changed direction or endpoint')
    for marker in root.findall('./{*}defs/{*}marker'):
        require(float(marker.attrib['markerWidth']) >= ARROW_LENGTH
                and float(marker.attrib['markerHeight']) >= ARROW_HEIGHT
                and marker.attrib.get('overflow') == 'visible', 'Small or clipped arrowhead')
    return {'large_arrowheads_checked': True, 'foreground_arrowheads_checked': True,
            'single_painted_head_per_terminal_path_checked': True}


def validate_style(root):
    """Reject colored paint, sans serif labels and rounded block styling."""
    for node in root.iter():
        for attribute in ('fill', 'stroke'):
            value = node.attrib.get(attribute)
            if value in (None, 'none', 'white', 'black') or value.startswith('url('):
                continue
            require(re.fullmatch(r'#[0-9a-fA-F]{6}', value) is not None,
                    'Unrecognized diagram paint: '+value)
            require(value[1:3].lower() == value[3:5].lower() == value[5:7].lower(),
                    'Colored diagram paint: '+value)
        if node.tag == f'{{{NS}}}text':
            require(node.attrib.get('font-family') == FONT_STACK,
                    'Diagram text must use the shared serif font')
        if node.tag == f'{{{NS}}}rect':
            require('rx' not in node.attrib and 'ry' not in node.attrib,
                    'Report block diagrams use square corners')
    return {'monochrome_paint_checked': True, 'serif_labels_checked': True,
            'square_block_corners_checked': True}


class Figure:
    """Small SVG authoring helper for the context and technical process views."""
    def __init__(self, title, width, height, metrics=None):
        self.width, self.height = width, height
        self.metrics = metrics or SerifMetrics()
        self.root = ET.Element(f'{{{NS}}}svg', {
            'width': f'{width}pt', 'height': f'{height}pt',
            'viewBox': f'0 0 {width} {height}', 'role': 'img', 'aria-label': title})
        self.el('title').text = title
        self.rect(0, 0, width, height, color='none')
        defs = self.el('defs')
        arrow_marker(self, defs)
        self._arrow_count = 0

    def el(self, tag, parent=None, **attrs):
        return ET.SubElement(self.root if parent is None else parent,
                             f'{{{NS}}}{tag}',
                             {k.replace('_', '-'): str(v) for k, v in attrs.items()})

    def rect(self, x, y, w, h, parent=None, fill='white', color=INK, **attrs):
        return self.el('rect', parent, x=x, y=y, width=w, height=h,
                       fill=fill, stroke=color, stroke_width='.8', **attrs)

    def text(self, value, x, y, size=14, weight='normal', anchor='start',
             color=INK, parent=None, width=None, **attrs):
        measured = self.metrics.measure(value, size, weight)
        require(width is None or measured <= width, 'Label exceeds its region: '+value)
        left = x-measured/2 if anchor == 'middle' else x-measured if anchor == 'end' else x
        require(0 <= left and left+measured <= self.width, 'Label exceeds page: '+value)
        node = self.el('text', parent, x=x, y=y, font_family=FONT_STACK,
                       font_size=size, font_weight=weight, text_anchor=anchor, fill=color, **attrs)
        node.text = value
        return node

    def lines(self, labels, x, y, leading=16, **attrs):
        for label in labels:
            self.text(label, x, y, **attrs)
            y += leading

    def arrow(self, d, parent=None, style='solid', head=True, **attrs):
        self._arrow_count += 1
        attrs.setdefault('id', f'arrow-{self._arrow_count}')
        return self.el('path', parent, d=d, fill='none', stroke=INK,
                       stroke_width='1.2', data_end_marker='url(#arrow)',
                       data_terminal_head=str(head).lower(), **line_attributes(style), **attrs)

    def save(self, path):
        foreground_arrowheads(self.root)
        validate_arrowheads(self.root)
        validate_port_labels(self.root)
        validate_style(self.root)
        ET.indent(self.root)
        ET.ElementTree(self.root).write(path, encoding='utf-8', xml_declaration=True)


def render_figure(figure, base, job):
    """Render exact SVG sources and check searchable PDF labels and PNG sizes."""
    base, job = Path(base), Path(job)
    job.mkdir(parents=True, exist_ok=True)
    svg, pdf, png = [base.with_suffix('.'+kind) for kind in ('svg', 'pdf', 'png')]
    figure.save(svg)
    source_hash = sha(svg)
    run(['rsvg-convert', '--format=pdf', '--output', str(pdf), str(svg)])
    run(['pdftoppm', '-r', '144', '-png', '-singlefile', str(pdf), str(base)])
    require(sha(svg) == source_hash, 'SVG changed during rendering')
    bbox = job / (base.name+'-bounds.html')
    run(['pdftotext', '-bbox', str(pdf), str(bbox)])
    words = ET.parse(bbox).getroot().findall('.//{*}word')
    require(len(words) > 20, 'Missing searchable diagram labels')
    for word in words:
        require(0 <= float(word.attrib['xMin']) <= float(word.attrib['xMax']) <= figure.width
                and 0 <= float(word.attrib['yMin']) <= float(word.attrib['yMax']) <= figure.height,
                'PDF text clipped: '+str(word.text))
    dimensions = struct.unpack('>II', png.read_bytes()[16:24])
    require(dimensions == (2*figure.width, 2*figure.height), 'Unexpected PNG dimensions')
    return {'artifact_sha256': {kind: sha(base.with_suffix('.'+kind))
                                for kind in ('svg', 'pdf', 'png')},
            'svg_sha256_used_for_pdf': source_hash,
            'font': figure.metrics.provenance(),
            'dimensions': {'pdf_pt': [figure.width, figure.height],
                           'png_px': list(dimensions)},
            'checks': {**validate_style(figure.root), **validate_arrowheads(figure.root),
                       **validate_port_labels(figure.root), 'pdf_text_within_page': True,
                       'exact_svg_preserved_during_conversion': True},
            'rendering': run(['rsvg-convert', '--version']).strip(),
            'SOURCE_DATE_EPOCH': 0}
