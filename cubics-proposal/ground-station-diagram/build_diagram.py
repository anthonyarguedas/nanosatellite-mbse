#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Build separate 70 cm RF, 13 cm RX, tracking and power images from saved photos.

Run: uv run cubics-proposal/ground-station-diagram/build_diagram.py
PNG rendering requires rsvg-convert. The BOM and image source records are unchanged.
"""
from functools import lru_cache
from html import escape
from pathlib import Path
import base64
import io
import json
import shutil
import subprocess

from PIL import Image, ImageChops, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
WIDTH = 2840
PHOTOS = {p['id']: p for p in json.loads((HERE / 'photos.json').read_text())['products']}
COLORS = {
    'ink': '#172d42', 'muted': '#607285', 'border': '#d5dfe8',
    'rf': '#2166b0', 'tx': '#bd3e48', 'usb': '#007f83',
    'control': '#7952a8', 'power': '#a5680a', 'mechanical': '#6c7782',
    'ground': '#458351',
}
ALTERNATIVES = {
    'lime_front': ('Alt: USRP B200', 'or ADALM-PLUTO'),
    'sp70': ('Alt: Mini-Kits EME237-70CM',),
    'ars': ('Alt: Yaesu GS-232B',),
}
EXCLUDED_PHOTOS = {
    'polarization', 'usrp', 'pluto', 'minikits', 'gs232', 'dummy',
}


@lru_cache(maxsize=None)
def font(size):
    for path in ('/System/Library/Fonts/Supplemental/Arial.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


@lru_cache(maxsize=None)
def image_symbol(key):
    p = PHOTOS[key]
    image = Image.open(HERE / p['local_file']).convert('RGB')
    delta = ImageChops.difference(image, Image.new('RGB', image.size, 'white'))
    box = delta.convert('L').point(lambda v: 255 if v > 23 else 0).getbbox()
    if box:
        image = image.crop(box)
    image.thumbnail((760, 470))
    image = ImageOps.expand(image, border=6, fill='white')
    stream = io.BytesIO()
    image.save(stream, format='JPEG', quality=88)
    uri = 'data:image/jpeg;base64,' + base64.b64encode(stream.getvalue()).decode()
    return (f'<symbol id="photo_{key}" viewBox="0 0 {image.width} {image.height}">'
            f'<image width="{image.width}" height="{image.height}" href="{uri}"/></symbol>')


class Diagram:
    def __init__(self, slug, height):
        self.slug = slug
        self.height = height
        self.shapes = []
        self.wires = []
        self.labels = []
        self.used_photos = set()
        self.connections = []
        self.label_boxes = []
        self.component_boxes = []

    def text(self, x, y, value, size=20, fill=None, weight='normal', anchor='start', layer=None):
        target = self.shapes if layer is None else layer
        target.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
                      f'fill="{fill or COLORS["ink"]}" text-anchor="{anchor}">{escape(str(value))}</text>')

    def lines(self, x, y, values, size=18, fill=None, weight='normal', anchor='middle', leading=None):
        for i, value in enumerate(values):
            self.text(x, y + i * (leading or size * 1.25), value, size, fill, weight, anchor)

    def rect(self, x, y, width, height, fill='white', stroke=None, radius=16):
        self.shapes.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                           f'rx="{radius}" fill="{fill}" stroke="{stroke or COLORS["border"]}" '
                           'stroke-width="1.6"/>')

    def photo(self, key, x, y, width, height):
        assert key not in EXCLUDED_PHOTOS, key
        self.used_photos.add(key)
        url = escape(PHOTOS[key]['product_page'], quote=True)
        self.shapes.append(f'<a href="{url}" target="_blank"><use href="#photo_{key}" '
                           f'x="{x}" y="{y}" width="{width}" height="{height}"/></a>')

    def card(self, key, device, model, x, y, width=300, height=270,
             kind='rf', detail='', pair=None):
        color = COLORS[kind]
        self.component_boxes.append((x, y, x + width, y + height))
        self.rect(x, y, width, height)
        self.shapes.append(f'<path d="M{x+18},{y+1} H{x+width-18}" '
                           f'stroke="{color}" stroke-width="5"/>')
        self.text(x + 16, y + 25, device, 16, color, 'bold')
        model_lines = model.split('\n')
        alternatives = ALTERNATIVES.get(key, ())
        text_height = len(model_lines) * 24 + (21 if detail else 0) + len(alternatives) * 19
        picture_height = height - 40 - text_height - 15
        assert picture_height > 35, (key, picture_height)
        if pair:
            split = .5 if pair == key else .58
            self.photo(key, x + 14, y + 37, width * split - 20, picture_height)
            self.photo(pair, x + width * split + 4, y + 37, width * (1-split) - 18, picture_height)
        else:
            self.photo(key, x + 14, y + 37, width - 28, picture_height)
        baseline = y + height - text_height + 9
        self.lines(x + width / 2, baseline, model_lines, 20, weight='bold', leading=24)
        baseline += len(model_lines) * 24
        if detail:
            self.text(x + width / 2, baseline - 3, detail, 15, COLORS['muted'], anchor='middle')
            baseline += 21
        for alternative in alternatives:
            self.text(x + width / 2, baseline - 3, alternative, 14, COLORS['muted'], anchor='middle')
            baseline += 19

    def plain(self, device, values, x, y, width=300, height=100, kind='usb'):
        self.component_boxes.append((x, y, x + width, y + height))
        self.rect(x, y, width, height, '#f7fafc', COLORS[kind])
        self.text(x + 15, y + 25, device, 16, COLORS[kind], 'bold')
        self.lines(x + width / 2, y + 62, values.split('\n'), 20, weight='bold')

    def label(self, x, bottom, values, kind='rf', size=17, anchor='middle'):
        """Draw text only. The caller places it clear of the corresponding wire."""
        values = values.split('\n') if isinstance(values, str) else values
        step = size + 5
        top_baseline = bottom - (len(values) - 1) * step
        self.labels.append('<g class="edge-label">')
        for i, value in enumerate(values):
            self.text(x, top_baseline + i * step, value, size, COLORS[kind],
                      anchor=anchor, layer=self.labels)
        self.labels.append('</g>')
        width = max(font(size).getlength(value) for value in values)
        left = x if anchor == 'start' else x - width if anchor == 'end' else x - width / 2
        box = [left, top_baseline - size, left + width, bottom + 4]
        self.label_boxes.append({'text': '\n'.join(values), 'box': box})
        return box

    def edge(self, points, kind='rf', cable='', at=None, both=False, arrow=True,
             dashed=False, size=17, anchor='middle'):
        color = COLORS[kind]
        path = 'M ' + ' L '.join(f'{x},{y}' for x, y in points)
        attrs = f' marker-end="url(#arrow_{kind})"' if arrow else ''
        if both:
            attrs += f' marker-start="url(#start_{kind})"'
        if dashed:
            attrs += ' stroke-dasharray="10 8"'
        self.wires.append(f'<path class="connection" d="{path}" fill="none" stroke="{color}" '
                          f'stroke-width="4" stroke-linecap="round" stroke-linejoin="round"{attrs}/>')
        box = self.label(*at, cable, kind, size, anchor) if cable else None
        self.connections.append({'points': points, 'kind': kind, 'cable': cable,
                                 'label_box': box, 'bidirectional': both, 'dashed': dashed})

    def ground(self, x, y):
        self.edge([(x, y), (x, y + 25)], 'ground', arrow=False)
        for dy, half in ((25, 19), (33, 12), (41, 5)):
            self.edge([(x-half, y+dy), (x+half, y+dy)], 'ground', arrow=False)
        self.label(x + 30, y + 34, 'Earth bond', 'ground', 16, 'start')

    def save(self):
        definitions = [image_symbol(key) for key in sorted(self.used_photos)]
        for kind, color in COLORS.items():
            if kind in {'ink', 'muted', 'border'}:
                continue
            definitions.extend([
                f'<marker id="arrow_{kind}" viewBox="0 0 10 10" refX="9" refY="5" '
                'markerWidth="7" markerHeight="7" orient="auto">'
                f'<path d="M0,0 L10,5 L0,10 Z" fill="{color}"/></marker>',
                f'<marker id="start_{kind}" viewBox="0 0 10 10" refX="1" refY="5" '
                'markerWidth="7" markerHeight="7" orient="auto">'
                f'<path d="M10,0 L0,5 L10,10 Z" fill="{color}"/></marker>',
            ])
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{self.height}" '
               f'viewBox="0 0 {WIDTH} {self.height}" font-family="Arial, Helvetica, sans-serif" '
               f'role="img" aria-label="Ground station {self.slug} connections">'
               f'<defs>{"".join(definitions)}</defs>'
               f'<rect width="{WIDTH}" height="{self.height}" fill="white"/>'
               f'<g id="wires">{"".join(self.wires)}</g>'
               f'<g id="components">{"".join(self.shapes)}</g>'
               f'<g id="cable-labels">{"".join(self.labels)}</g></svg>')
        path = HERE / f'{self.slug}.svg'
        path.write_text(svg)
        subprocess.run(['rsvg-convert', '-o', str(HERE / f'{self.slug}.png'), str(path)], check=True)
        return {
            'size': [WIDTH, self.height], 'photos': sorted(self.used_photos),
            'connections': self.connections, 'label_boxes': self.label_boxes,
            'component_boxes': self.component_boxes,
        }


def rf_diagram():
    d = Diagram('rf', 935)
    y = 70
    d.card('yagi', 'A1', 'M2 436CP16', 70, y, detail='70 cm antenna')
    d.card('sp70', 'LNA1', 'SSB SP70', 550, y, detail='Masthead LNA + TX bypass')
    d.card('surge', 'G1', 'Alpha Delta ATT3G50', 1030, y, detail='DC-pass surge protector')
    d.card('dcw', 'SEQ1', 'SSB DCW 2004 B', 1510, y, detail='Bias tee + sequencer')
    d.card('coax_relay', 'R1', 'Tohtsu CX520D', 1990, y, detail='Antenna T/R relay')
    d.card('lime_front', 'SDR1', 'LimeSDR Mini 2.0', 2470, y,
           pair='sdr_case', detail='Custom Hammond 1590B case')
    for start, end, cable in [
        (370,550,'N-male ↔ N-male\n18 in coax'),
        (850,1030,'N ↔ N outdoor coax\nRF + switched 12 V\nlength TBD'),
        (1330,1510,'N-male ↔ N-male\n3 ft coax + 12 V bias'),
        (1810,1990,'N-male ↔ N-male\n18 in coax'),
        (2290,2470,'N-male ↔ SMA-male\n2 ft manual RX patch'),
    ]:
        d.edge([(start,205),(end,205)], cable=cable, at=((start+end)/2,187),
               both=(end!=2470), size=16)
    d.text(2479,231,'RX',15,COLORS['rf'],'bold')
    d.text(2635,359,'TX',15,COLORS['tx'],'bold')
    d.ground(1180,340)

    for key, device, model, x, detail in [
        ('filter70','F1','70 cm 100 W bandpass filter',550,'430-450 MHz'),
        ('pa','PA1','Mini-Circuits ZHL-5W-1+',1030,'Proposed TX amplifier'),
        ('coax_relay','R2','Tohtsu CX520D',1510,'PA input RF mute'),
        ('atten','PAD1','Mini-Circuits VAT-15+',1990,'15 dB input pad'),
    ]:
        d.card(key, device, model, x,585,height=245,kind='tx',detail=detail)
    d.edge([(2620,340),(2620,525),(2140,525),(2140,585)], 'tx',
           'SMA direct mate, no cable', (2375,507), size=17)
    for start, end, cable in [
        (1990,1810,'SMA-male ↔ N-male\n2 ft coax'),
        (1510,1330,'N-male ↔ SMA-male\n2 ft coax'),
        (1030,850,'SMA-male ↔ N-male\n2 ft coax'),
    ]:
        d.edge([(start,707),(end,707)], 'tx', cable, ((start+end)/2,689), size=16)
    d.edge([(700,585),(700,425),(2140,425),(2140,340)], 'tx',
           'N-male ↔ N-male coax, 18 in', (1420,407), size=18)
    d.edge([(1660,830),(1660,875)], 'tx', 'NC → 50 ohm termination (TBD)',
           (1690,867), arrow=False, size=17, anchor='start')
    return d


def tracking_diagram():
    d = Diagram('tracking', 1055)
    d.plain('PROVIDED', 'Live Ethernet connection',70,70,height=100)
    d.card('lime_front','SDR1','LimeSDR Mini 2.0',1030,50,height=225,kind='usb')
    d.card('yagi','A1 + A2','M2 436CP16\nWiMo HELIX-13',2470,50,height=225,
           kind='mechanical',detail='70 cm + 13 cm antennas',pair='helix')
    d.card('pi','PC1','Raspberry Pi 4, 4 GB',70,400,height=255,kind='usb',
           pair='pi_case',detail='Pi board + Flirc case')
    d.card('hub','H1','StarTech ST4300USB3',550,400,height=255,kind='usb',detail='Powered USB hub')
    d.card('ars','ARS1','EA4TX ARS-USB-AE',1030,400,height=255,kind='control',detail='Rotator interface')
    d.card('rotator_controller','YC1','Yaesu G-5500DC',1510,400,height=255,
           kind='control',detail='Indoor control box')
    d.card('rotator_motors','M1','Yaesu G-5500DC',1990,400,height=255,
           kind='control',detail='Outdoor AZ + EL motors')
    d.card('boom','B1','M2 FGCB60',2470,400,height=255,
           kind='mechanical',detail='Fiberglass cross-boom')
    d.card('sd','STORAGE','SanDisk High Endurance',70,785,height=220,kind='usb',detail='32 GB microSD')
    d.card('ptt','PTT1','Numato USB relay',1030,785,height=220,kind='control',detail='PTT request')
    d.card('dcw','SEQ1','SSB DCW 2004 B',1510,785,height=220,kind='control',detail='Sequencer')
    d.card('coax_relay','R1 + R2','Tohtsu CX520D × 2',1990,785,height=220,
           kind='control',detail='RF relay coils',pair='coax_relay')
    d.edge([(220,170),(220,400)],'usb','Cat 6 / RJ45\nN6PATCH10BK',(260,292),both=True,size=17,anchor='start')
    d.edge([(220,785),(220,655)],'mechanical','microSD slot\nno cable',(260,730),size=17,anchor='start')
    for start,end,kind,cable in [
        (370,550,'usb','USB 3 upstream\nsupplied with hub'),
        (850,1030,'usb','USB cable\nsupplied with ARS'),
        (1330,1510,'control','8-pin DIN cable\nEA4TX Yaesu DIN8'),
        (1810,1990,'control','2 × Yaesu cables\nAZ + EL, 5/6 wires'),
        (2290,2470,'mechanical','1.625 in center\nmechanical clamp'),
    ]:
        d.edge([(start,528),(end,528)],kind,cable,((start+end)/2,510),
               both=(kind!='mechanical'),arrow=(kind!='mechanical'),
               dashed=(kind=='mechanical'),size=16)
    d.edge([(2620,400),(2620,275)],'mechanical','Antenna clamps',
           (2585,341),arrow=False,dashed=True,size=17,anchor='end')
    d.edge([(700,400),(700,330),(1180,330),(1180,275)],'usb',
           'USB 3 extension\nUSB3AAEXT1M',(935,312),both=True,size=17)
    d.edge([(700,655),(700,725),(1180,725),(1180,785)],'usb',
           'USB data cable\nmodule connector TBD',(935,707),both=True,size=17)
    d.edge([(1330,895),(1510,895)],'control','Dry-contact PTT\ncustom DB9 loom (TBD)',
           (1420,877),size=15)
    d.edge([(1810,895),(1990,895)],'control','Sequenced coil wires\ncustom harness (TBD)',
           (1900,877),size=15)
    return d


def rx13_diagram():
    d = Diagram('13cm-rx', 820)
    d.card('helix','A2','WiMo HELIX-13',70,70,detail='2300-2450 MHz antenna')
    d.card('filter13','F2','Data Alliance BandPass2450',550,70,detail='2400-2450 MHz passband')
    d.card('lana','LNA2','Nooelec LaNA',1030,70,detail='5 V masthead receive LNA')
    d.card('surge','G2','Alpha Delta ATT3G50',1510,70,detail='DC-pass surge protector')
    d.card('bias13','BIAS2','Mini-Circuits ZFBT-6GW+',1990,70,detail='5 V bias tee')
    d.card('lime_front','SDR1','LimeSDR Mini 2.0',2470,70,
           detail='Shared RX; manual band patch')
    for start,end,cable in [
        (370,550,'N-male ↔ N-male\n18 in + N/SMA adapter'),
        (850,1030,'SMA-male ↔ SMA-male\n12 in coax'),
        (1330,1510,'N ↔ N outdoor coax\nSMA/N adapter at LNA\nRF + 5 V / length TBD'),
        (1810,1990,'N-male ↔ SMA-male\n3 ft coax + 5 V bias'),
        (2290,2470,'SMA-male ↔ SMA-male\n12 in manual RX patch'),
    ]:
        d.edge([(start,205),(end,205)],'rf',cable,((start+end)/2,187),size=15)
    d.text(2479,231,'RX',15,COLORS['rf'],'bold')
    d.ground(1660,340)
    d.card('psu13','P13','MEAN WELL GST25U05-P1J',1510,560,
           height=220,kind='power',detail='5 V / 4 A supply')
    d.plain('PROVIDED','120 V AC outlet',1030,620,height=100,kind='power')
    d.edge([(1330,670),(1510,670)],'power','Integral AC plug',
           (1420,652),size=17)
    d.edge([(1660,560),(1660,450),(2140,450),(2140,340)],'power',
           '5 V DC feed lead (TBD)\n5.5 × 2.1 mm jack ↔ SMA-male',
           (1895,432),size=17)
    return d


def power_diagram():
    d = Diagram('power', 775)
    width = 360
    d.edge([(250,60),(2550,60)],'power',arrow=False)
    d.label(1410,40,'120 V AC grounded outlets','power',20)
    d.card('pi_psu','P5','Raspberry Pi 15 W',70,140,width=width,height=220,
           kind='power',detail='5.1 V / 3 A supply')
    d.plain('INCLUDED WITH H1','USB hub AC adapter',530,140,width=width,height=220,kind='power')
    d.card('psu13','P13','MEAN WELL GST25U05-P1J',990,140,width=width,height=220,
           kind='power',detail='5 V / 4 A supply')
    d.card('psu12','P12','MEAN WELL GST25A12-P1J',1450,140,width=width,height=220,
           kind='power',detail='12 V / 2.08 A supply')
    d.card('psu24','P24','MEAN WELL GST120A24-P1M',1910,140,width=width,height=220,
           kind='power',detail='24 V / 5 A supply')
    d.card('rotator_controller','YC1','Yaesu G-5500DC',2370,140,width=width,height=220,
           kind='power',detail='AC-powered control box')
    d.card('pi','PC1','Raspberry Pi 4',70,550,width=width,height=185,kind='power')
    d.card('hub','H1','Powered USB hub',530,550,width=width,height=185,kind='power')
    d.card('bias13','BIAS2 + LNA2','ZFBT-6GW+ + LaNA',990,550,width=width,height=185,
           kind='power',detail='LNA power carried over RF coax',pair='lana')
    d.rect(1450,550,width,185)
    d.component_boxes.append((1450,550,1810,735))
    d.text(1465,575,'SEQ1 + ARS1 + R1/R2',16,COLORS['power'],'bold')
    d.photo('dcw',1462,590,106,85)
    d.photo('ars',1574,590,106,85)
    d.photo('coax_relay',1686,590,106,85)
    d.text(1630,716,'12 V accessories + relay coils',18,weight='bold',anchor='middle')
    d.card('pa','PA1','Mini-Circuits ZHL-5W-1+',1910,550,width=width,height=185,
           kind='power',detail='Proposed TX amplifier')
    d.card('rotator_motors','M1','AZ + EL motors',2370,550,width=width,height=185,kind='power')
    for cx,cable in [(250,'Integral AC plug'),(710,'Supplied AC lead'),
                     (1170,'Integral AC plug'),(1630,'IEC C13 cord\nPXT101'),
                     (2090,'IEC C13 cord\nPXT101'),(2550,'Yaesu mains lead')]:
        d.edge([(cx,60),(cx,140)],'power',cable,(cx+28,110),size=16,anchor='start')
    for cx,cable in [(250,'USB-C\n5.1 V / 3 A'),(710,'Included DC cable'),
                     (1170,'5 V DC feed lead (TBD)\n2.1 mm jack ↔ SMA-male'),
                     (1630,'12 V fused loom (TBD)\n5.5 × 2.1 mm input'),
                     (2090,'24 V PA lead (TBD)\n5.5 × 2.5 mm input'),
                     (2550,'2 × Yaesu motor cables\npower + position feedback')]:
        d.edge([(cx,360),(cx,550)],'power',cable,(cx+28,455),size=16,anchor='start')
    return d


def build_viewer():
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ground station connections</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f6f9;color:#172d42;font:15px Arial,sans-serif}
nav{position:sticky;top:0;z-index:2;padding:14px 20px;background:white;border-bottom:1px solid #d5dfe8;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button,a{border:1px solid #ccd8e2;border-radius:7px;background:white;color:#172d42;padding:8px 12px;text-decoration:none;cursor:pointer}
button.active{background:#172d42;color:white}main{padding:18px;overflow:auto}#surface{min-width:1000px;margin:auto}img{display:block;width:100%;height:auto}a:hover,button:hover{border-color:#007f83}
</style><nav><button data-image="rf" class="active">70 cm RF</button><button data-image="13cm-rx">13 cm RX</button><button data-image="tracking">Tracking</button><button data-image="power">Power</button><button id="smaller">−</button><button id="larger">+</button><a id="png" href="ground-station-diagram/rf.png">PNG</a><a id="svg" href="ground-station-diagram/rf.svg">SVG</a><a href="ground-station-diagram/image-sources.csv">Photo sources</a></nav>
<main><div id="surface"><img id="diagram" src="ground-station-diagram/rf.svg" alt="RF connections"></div></main><script>
let zoom=1;const image=document.querySelector('#diagram'),surface=document.querySelector('#surface');document.querySelectorAll('[data-image]').forEach(button=>button.onclick=()=>{const name=button.dataset.image;image.src='ground-station-diagram/'+name+'.svg';image.alt=name+' connections';document.querySelector('#png').href='ground-station-diagram/'+name+'.png';document.querySelector('#svg').href=image.getAttribute('src');document.querySelectorAll('[data-image]').forEach(b=>b.classList.toggle('active',b===button));});document.querySelector('#larger').onclick=()=>{zoom=Math.min(3,zoom+.25);surface.style.width=(100*zoom)+'%';};document.querySelector('#smaller').onclick=()=>{zoom=Math.max(.75,zoom-.25);surface.style.width=(100*zoom)+'%';};
</script></html>'''
    (OUT / 'ground-station-physical.html').write_text(html)


def main():
    if not shutil.which('rsvg-convert'):
        raise SystemExit('rsvg-convert is required to render PNG images.')
    outputs = {}
    for diagram in (rf_diagram(), rx13_diagram(), tracking_diagram(), power_diagram()):
        outputs[diagram.slug] = diagram.save()
        print(HERE / f'{diagram.slug}.png')
    (HERE / 'connections.json').write_text(json.dumps(outputs, indent=2) + '\n')
    build_viewer()


if __name__ == '__main__':
    main()
