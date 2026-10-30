#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Build separate 70 cm RF, 13 cm RX, tracking and power images from saved photos.

Run: uv run cubics-proposal/ground-station-diagram/build_diagram.py
PNG rendering requires rsvg-convert. The viewer includes the current BOM snapshot.
The BOM is read only. Photo source CSV records are rebuilt for the displayed parts.
"""
from decimal import Decimal
from functools import lru_cache
from html import escape
from pathlib import Path
import base64
import csv
import io
import json
import shutil
import subprocess

from PIL import Image, ImageChops, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
WIDTH = 2840
BOM = list(csv.DictReader(io.StringIO((OUT / 'ground-station-bom.tsv').read_text()), delimiter='\t'))
PHOTOS = {p['id']: p for p in json.loads((HERE / 'photos.json').read_text())['products']}
COLORS = {
    'ink': '#172d42', 'muted': '#607285', 'border': '#d5dfe8',
    'rf': '#2166b0', 'tx': '#bd3e48', 'usb': '#007f83',
    'control': '#7952a8', 'power': '#a5680a', 'mechanical': '#6c7782',
    'ground': '#458351',
}
EXCLUDED_PHOTOS = {'usrp', 'pluto', 'minikits', 'gs232'}


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
        text_height = len(model_lines) * 24 + (21 if detail else 0)
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
    d = Diagram('rf', 1200)
    y = 70
    d.card('yagi', 'A1 + POL1', 'M2 436CP30\n+ PS-70CM kit', 70, y,
           pair='polarization', detail='432-440 MHz / RHCP or LHCP')
    d.card('sp70', 'LNA1', 'SSB SP70', 550, y, detail='Masthead LNA + TX bypass')
    d.card('surge', 'G1', 'Alpha Delta ATT3G50', 1030, y, detail='DC-pass surge protector')
    d.card('dcw', 'SEQ1', 'SSB DCW 2004 B', 1510, y, detail='Bias tee + sequencer')
    d.card('coax_relay', 'R1', 'Tohtsu CX520D', 1990, y, detail='Antenna T/R relay')
    d.card('lime_front', 'SDR1', 'LimeSDR Mini 2.0', 2470, y,
           pair='sdr_case', detail='70 cm TX/RX / 1590B case')
    for start, end, cable in [
        (370,550,'N-male ↔ N-male\n18 in coax'),
        (850,1030,'Nm50ftNm400 / 50 ft\nN-male ↔ N-male\nRF + switched 12 V'),
        (1330,1510,'N-male ↔ N-male\n3 ft coax + 12 V bias'),
        (1810,1990,'N-male ↔ N-male\n18 in coax'),
        (2290,2470,'N-male ↔ SMA-male\n2 ft fixed RX cable'),
    ]:
        d.edge([(start,205),(end,205)], cable=cable, at=((start+end)/2,187),
               both=(end!=2470), size=16)
    d.text(2479,231,'RX',15,COLORS['rf'],'bold')
    d.text(2635,359,'TX',15,COLORS['tx'],'bold')
    d.ground(1180,340)

    for key, device, model, x, detail in [
        ('filter70','F1','Antennas-Amplifiers\n6530',70,'430-450 MHz / 200 W'),
        ('isolator','ISO1','Fairview Microwave\nSFI3846N',550,'PA output mismatch protection'),
        ('pa','PA1','Mini-Circuits ZHL-5W-1+',1030,'5 W TX candidate / see power view'),
        ('coax_relay','R2','Tohtsu CX520D',1510,'PA input RF mute'),
        ('atten','PAD1','Mini-Circuits VAT-15A+',1990,'15 dB input pad'),
        ('dummy','TEST1','Chelegance JLoad-100\nCH0032526-O1',2470,'100 W / DC-3 GHz / N-male'),
    ]:
        d.card(key, device, model, x,585,height=245,kind='tx',detail=detail)
    d.edge([(2620,340),(2620,525),(2140,525),(2140,585)], 'tx',
           'SMA direct mate, no cable', (2375,507), size=17)
    for start, end, cable in [
        (1990,1810,'SMA-male ↔ N-male\n2 ft coax'),
        (1510,1330,'N-male ↔ SMA-male\n2 ft coax'),
        (1030,850,'SMA-male ↔ N-male\n2 ft coax'),
        (550,370,'N-male ↔ N-male\n18 in coax'),
    ]:
        d.edge([(start,707),(end,707)], 'tx', cable, ((start+end)/2,689), size=16)
    d.edge([(220,585),(220,425),(2140,425),(2140,340)], 'tx',
           'N-male ↔ N-male coax, 18 in', (1420,407), size=18)
    d.edge([(1660,830),(1660,875)], 'tx', 'NC → 50 ohm termination (not in BOM)',
           (1690,867), arrow=False, size=17, anchor='start')
    d.edge([(220,830),(220,1050),(2620,1050),(2620,830)], 'tx',
           'Manual test substitution at F1 output: disconnect the antenna path.\n'
           'The N-male dummy load mates directly to the F1 N-female output.',
           (1420,1032), dashed=True, size=19)
    d.text(70,1130,'PA input: 0 dBm max into a matched load, -20 dBm without a load. Verify drive level, sequencing and cooling.',19)
    d.text(70,1165,'The PS-70CM kit is fitted at A1. Its control wiring remains TBD. ISO1: 100 W forward / 30 W reverse CW, 20 dB min isolation.',19)
    return d


def tracking_diagram():
    d = Diagram('tracking', 1160)
    d.plain('PROVIDED', 'Live Ethernet connection',70,70,height=100)
    d.card('lime_front','SDR1','LimeSDR Mini 2.0',1030,50,height=225,kind='usb',
           detail='Dedicated 70 cm TX/RX')
    d.card('lime_front','SDR2','LimeSDR Mini 2.0',1510,50,height=225,kind='usb',
           detail='Dedicated 13 cm RX only')
    d.card('yagi','A1 + A2','M2 436CP30\nWiMo HELIX-13',2470,50,height=225,
           kind='mechanical',detail='70 cm + 13 cm antennas',pair='helix')
    d.card('pi','PC1','Raspberry Pi 4, 4 GB',70,400,height=255,kind='usb',
           pair='pi_case',detail='Pi board + Flirc case')
    d.card('hub','H1','StarTech ST4300USB3',550,400,height=255,kind='usb',detail='Powered hub / SDR1 + SDR2 only')
    d.card('ars','ARS1','EA4TX ARS-USB-AE',1030,400,height=255,kind='control',detail='Rotator interface')
    d.card('rotator_controller','YC1','Yaesu G-5500DC',1510,400,height=255,
           kind='control',detail='Indoor control box')
    d.card('rotator_motors','M1','Yaesu G-5500DC',1990,400,height=255,
           kind='control',detail='Outdoor AZ + EL motors')
    d.card('boom','B1','M2 FGCB60',2470,400,height=255,
           kind='mechanical',detail='Fiberglass cross-boom')
    d.card('sd','STORAGE','Kingston Industrial\nSDCIT2/32GB',70,785,height=220,kind='usb',detail='32 GB microSD')
    d.card('ptt','PTT1','Adafruit 4409\nSTEMMA GPIO relay',1030,785,height=220,
           kind='control',detail='COM/NO dry-contact PTT request')
    d.card('dcw','SEQ1','SSB DCW 2004 B',1510,785,height=220,kind='control',detail='Sequencer')
    d.card('coax_relay','R1 + R2','Tohtsu CX520D × 2',1990,785,height=220,
           kind='control',detail='RF relay coils',pair='coax_relay')
    d.edge([(220,170),(220,400)],'usb','Cat 6 / RJ45, 10 ft\nN6PATCH10BK',(260,292),both=True,size=17,anchor='start')
    d.edge([(220,785),(220,655)],'mechanical','microSD slot\nno cable',(180,730),size=17,anchor='end')
    for start,end,kind,cable in [
        (370,550,'usb','USB 3 upstream\nsupplied with hub'),
        (1330,1510,'control','ARS-AZELDIN8\n8-pin DIN cable'),
        (1810,1990,'control','2 × DXE-YRC-050PE\n50 ft / AZ + EL'),
        (2290,2470,'mechanical','1.625 in center\nmechanical clamp'),
    ]:
        d.edge([(start,528),(end,528)],kind,cable,((start+end)/2,510),
               both=(kind!='mechanical'),arrow=(kind!='mechanical'),
               dashed=(kind=='mechanical'),size=16)
    d.edge([(2620,400),(2620,275)],'mechanical','Antenna clamps',
           (2585,341),arrow=False,dashed=True,size=17,anchor='end')
    d.edge([(650,400),(650,330),(1180,330),(1180,275)],'usb',
           'Data Alliance UDA\n15 cm USB 3, right-angle',(935,312),both=True,size=17)
    d.edge([(750,400),(750,360),(1660,360),(1660,275)],'usb',
           'Data Alliance UDA\n15 cm USB 3, right-angle',(1420,342),both=True,size=17)
    d.edge([(350,655),(350,690),(1180,690),(1180,655)],'usb',
           'USB cable supplied with ARS',(750,677),both=True,size=17)
    d.edge([(300,655),(300,755),(1180,755),(1180,785)],'control',
           'Adafruit 3894, 200 mm JST-PH lead\nPi: 3.3 V GPIO + 3.3 V + GND → STEMMA',
           (815,739),size=17)
    d.edge([(1330,895),(1510,895)],'control','COM/NO PTT\ncustom DB9 loom (TBD)',
           (1420,877),size=15)
    d.edge([(1810,895),(1990,895)],'control','Sequenced coil wires\ncustom harness (TBD)',
           (1900,877),size=15)
    d.text(70,1080,'G-5500DC motor cables: remove controller plugs and wire to screw terminals. PTT1 uses Pi GPIO, power and ground.',19)
    d.text(70,1115,'Select each SDR by its unique serial number. ARS1 connects directly to a PC1 USB 2 port. Coordinate jobs with the shared rotator.',19)
    return d


def rx13_diagram():
    d = Diagram('13cm-rx', 860)
    d.card('helix','A2','WiMo HELIX-13',70,70,detail='2300-2450 MHz antenna')
    d.card('filter13','F2','Data Alliance BandPass2450',550,70,detail='2400-2450 MHz passband')
    d.card('lana','LNA2','Nooelec LaNA',1030,70,detail='5 V masthead receive LNA')
    d.card('surge','G2','Alpha Delta ATT3G50',1510,70,detail='DC-pass surge protector')
    d.card('bias13','BIAS2','Mini-Circuits ZFBT-6GW+',1990,70,detail='5 V bias tee / 500 mA abs max')
    d.card('lime_front','SDR2','LimeSDR Mini 2.0',2470,70,
           pair='sdr_case', detail='13 cm RX only / 1590B case')
    for start,end,cable in [
        (370,550,'N-male ↔ N-male\n18 in + N/SMA adapter'),
        (850,1030,'SMA-male ↔ SMA-male\n12 in coax'),
        (1330,1510,'Nm50ftNm400 / 50 ft\nSMA/N adapter at LNA\nRF + 5 V bias'),
        (1810,1990,'N-male ↔ SMA-male\n3 ft coax + 5 V bias'),
        (2290,2470,'SMA-male ↔ SMA-male\n12 in fixed RX cable'),
    ]:
        d.edge([(start,205),(end,205)],'rf',cable,((start+end)/2,187),size=15)
    d.text(2479,231,'RX',15,COLORS['rf'],'bold')
    d.text(2635,359,'TX unused',15,COLORS['muted'],'bold')
    d.text(2470,395,'Configure SDR2 for RX only.',17)
    d.ground(1660,340)
    d.card('psu13','P13','MEAN WELL GST25U05-P1J',1510,560,
           height=220,kind='power',detail='5 V / 4 A supply')
    d.plain('PROVIDED','120 V AC outlet',1030,620,height=100,kind='power')
    d.plain('REQUIRED / NOT IN BOM','5 V branch current limiter\nSet below 500 mA',
            1990,560,height=180,kind='power')
    d.edge([(1330,670),(1510,670)],'power','Integral AC plug',
           (1420,652),size=17)
    d.edge([(1810,670),(1990,670)],'power','5 V DC\n5.5 × 2.1 mm',
           (1900,652),size=17)
    d.edge([(2140,560),(2140,340)],'power',
           'Adapter lead TBD\nBarrel center → SMA center (+5 V)\nSleeve → SMA shell (ground)',
           (2180,465),size=17,anchor='start')
    d.text(70,825,'Complete the adapter lead and branch current limiter before connecting the 4 A supply to the 500 mA bias tee.',19)
    return d


def power_diagram():
    d = Diagram('power', 1485)
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
    d.card('pi','PC1','Raspberry Pi 4',70,550,width=width,height=185,
           kind='power',detail='Pi 3.3 V rail also powers PTT1')
    d.card('hub','H1','Powered USB hub',530,550,width=width,height=185,
           kind='power',detail='USB power for SDR1 and SDR2')
    d.card('bias13','BIAS2 + LNA2','ZFBT-6GW+ + LaNA',990,550,width=width,height=185,
           kind='power',detail='LNA power carried over RF coax',pair='lana')
    d.rect(1450,550,width,185)
    d.component_boxes.append((1450,550,1810,735))
    d.text(1465,575,'SEQ1 + ARS1 + R1/R2 + LNA1',16,COLORS['power'],'bold')
    d.photo('dcw',1462,590,106,85)
    d.photo('ars',1574,590,106,85)
    d.photo('coax_relay',1686,590,106,85)
    d.text(1630,716,'DCW feeds SP70 over RF coax',18,weight='bold',anchor='middle')
    d.card('dc_jack','J24 / PA DC INPUT','Switchcraft 712A',1910,550,width=width,height=185,
           kind='power',detail='5.5 × 2.5 mm / center positive')
    d.card('rotator_motors','M1','AZ + EL motors',2370,550,width=width,height=185,kind='power')
    for cx,cable in [(250,'Integral AC plug'),(710,'Supplied AC lead'),
                     (1170,'Integral AC plug'),(1630,'IEC C13 cord\nPXT101'),
                     (2090,'IEC C13 cord\nPXT101'),(2550,'Yaesu mains lead')]:
        d.edge([(cx,60),(cx,140)],'power',cable,(cx+28,110),size=16,anchor='start')
    for cx,cable in [(250,'USB-C\n5.1 V / 3 A'),(710,'Included DC cable'),
                     (1170,'5 V adapter lead (TBD)\nLimit branch below 500 mA\n2.1 mm jack ↔ SMA-male'),
                     (1630,'12 V fused loom (TBD)\n5.5 × 2.1 mm input'),
                     (2090,'24 V center-positive\n5.5 × 2.5 mm plug'),
                     (2550,'2 × DXE-YRC-050PE\n50 ft / AZ + EL')]:
        d.edge([(cx,360),(cx,550)],'power',cable,(cx+28,476),size=16,anchor='start')

    d.plain('FUSE1 / PA POSITIVE LEAD',
            'Littelfuse 0FHA0001ZXJ\n+ 0287005.PXCN, 5 A\nOne installed, one spare\nReturn wire bypasses fuse',
            70,960,width=430,height=280,kind='power')
    d.card('dc_protection','PROT1','Analog Devices DC2418A-A\nLTC4368-1',700,960,
           width=430,height=280,kind='power',detail='Version A / 10 A power stage / rework')
    d.card('pa','PA1','Mini-Circuits ZHL-5W-1+',1330,960,
           width=430,height=280,kind='power',detail='24 V / 3.3 A max / heatsink included')
    d.plain('PROT1 REWORK / ENGINEERING REVIEW',
            'R1: RT1206BRD071ML, 1 MOhm, 0.1%\n'
            'R2: RT1206BRD07100KL, 100 kOhm, 0.1%\n'
            'R3: RT1206BRD0723K2L, 23.2 kOhm, 0.1%\n'
            'Sense: WSL2512R0100FEA, 10 mOhm, 1 W\n'
            'Nominal OV 24.21 V / UV 4.56 V\n'
            'Stock OV is about 18 V. Rework before use.',
            1960,960,width=780,height=280,kind='power')
    d.edge([(2090,735),(2090,840),(285,840),(285,960)],'power',
           'Custom PA loom: DXE-PW-16 red/black 16 AWG, six feet of two-conductor wire.\n'
           'Fit the 5 A fuse near J24, before PROT1. The 712A jack is rated 5 A at nominal 24 V.',
           (1185,822),size=18)
    d.edge([(500,1100),(700,1100)],'power','16 AWG DC\n+ / return',(600,1082),size=17)
    d.edge([(1130,1100),(1330,1100)],'power','Protected 24 V\n3.3 A max load',(1230,1082),size=17)
    d.text(70,1320,'PA protection is a candidate assembly. Stock DC2418A-A settings require SMD rework and bench qualification before operation.',19)
    d.text(70,1355,'Review OV tolerance, startup behavior, overcurrent settings and enclosure cooling. SEQ1 with R1/R2 provides RF mute and switching.',19)
    d.text(70,1405,'Unlisted work: 12 V fused loom, 5 V adapter and current limiter, relay harness, R2 NC termination, polarity control and earth bonds.',18)
    d.text(70,1450,'H1 has a 10 W USB power budget. Two LimeSDRs need up to 9 W combined. ARS1 USB connects directly to PC1. Verify under load.',19)
    return d


def build_viewer():
    rows = []
    for part in BOM:
        cells = (
            f'<a href="{escape(part["link"], quote=True)}" target="_blank" rel="noopener">{escape(part["name"])}</a>',
            escape(part['quantity']),
            f'{Decimal(part["unit_price_cad"]):,.2f}',
            f'{Decimal(part["total_price_cad"]):,.2f}',
            escape(part['note']),
        )
        rows.append('<tr>' + ''.join(f'<td>{cell}</td>' for cell in cells) + '</tr>')
    total = sum(Decimal(part['total_price_cad']) for part in BOM)
    html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ground station connections</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6f9;color:#172d42;font:15px Arial,sans-serif}
header{padding:18px 20px 6px}h1{font-size:24px;margin:0 0 8px}p{line-height:1.5}
nav{position:sticky;top:0;z-index:2;padding:14px 20px;background:white;border-bottom:1px solid #d5dfe8;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
button,nav a{border:1px solid #ccd8e2;border-radius:7px;background:white;color:#172d42;padding:8px 12px;text-decoration:none;cursor:pointer}
button.active{background:#172d42;color:white}main{padding:18px;overflow:auto}#surface{min-width:1000px;margin:auto}img{display:block;width:100%;height:auto}
nav a:hover,button:hover{border-color:#007f83}a{color:#2166b0}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #007f83;outline-offset:3px}
.notice{margin:0 20px 12px;color:#607285}section{margin:0 20px 24px}details{padding:16px;background:white;border:1px solid #d5dfe8;border-radius:7px}summary{cursor:pointer;font-weight:bold}
.table-scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}caption{text-align:left;padding:14px 0;color:#607285}th,td{text-align:left;vertical-align:top;padding:10px;border-bottom:1px solid #d5dfe8}th{white-space:nowrap}td:first-child{min-width:260px}td:last-child{min-width:320px}td:nth-child(2),td:nth-child(3),td:nth-child(4){text-align:right;white-space:nowrap}tfoot{font-weight:bold}
</style>
</head>
<body>
<header><h1>Ground station connections</h1><p>Components and quantities from <a href="ground-station-bom.tsv">ground-station-bom.tsv</a>. SDR1 is dedicated to 70 cm half-duplex TX/RX. SDR2 is dedicated to 13 cm RX only. Both RF paths remain connected.</p></header>
<nav aria-label="Diagram views">
<button data-image="rf" class="active" aria-pressed="true">70 cm RF</button>
<button data-image="13cm-rx" aria-pressed="false">13 cm RX</button>
<button data-image="tracking" aria-pressed="false">Tracking</button>
<button data-image="power" aria-pressed="false">Power</button>
<button id="smaller" aria-label="Zoom out">−</button><button id="larger" aria-label="Zoom in">+</button>
<a id="png" href="ground-station-diagram/rf.png" download>PNG</a>
<a id="svg" href="ground-station-diagram/rf.svg" download>SVG</a>
<a href="ground-station-bom.tsv">BOM (TSV)</a>
<a href="ground-station-diagram/image-sources.csv">Photo sources</a>
</nav>
<main><div id="surface"><img id="diagram" src="ground-station-diagram/rf.svg" alt="70 cm RF connections"></div></main>
<p class="notice">Conceptual wiring. PA protection requires engineering review and bench qualification. Connections marked TBD or not in the BOM remain unresolved.</p>
<section aria-label="Component inventory">
<details><summary>Component list (__COUNT__ BOM entries)</summary>
<div class="table-scroll"><table>
<caption>BOM snapshot. Rebuild the diagrams after changing the TSV. CAD prices exclude tax, shipping, duties and conversion fees.</caption>
<thead><tr><th scope="col">Component / supplier</th><th scope="col">Qty</th><th scope="col">Unit CAD</th><th scope="col">Total CAD</th><th scope="col">Notes</th></tr></thead>
<tbody>
__ROWS__
</tbody>
<tfoot><tr><th scope="row" colspan="3">BOM total (CAD)</th><td>__TOTAL__</td><td></td></tr></tfoot>
</table></div>
</details>
</section>
<script>
let zoom=1;
const image=document.querySelector('#diagram'),surface=document.querySelector('#surface');
document.querySelectorAll('[data-image]').forEach(button=>button.onclick=()=>{
  const name=button.dataset.image;
  image.src='ground-station-diagram/'+name+'.svg';
  image.alt=button.textContent+' connections';
  document.querySelector('#png').href='ground-station-diagram/'+name+'.png';
  document.querySelector('#svg').href=image.getAttribute('src');
  document.querySelectorAll('[data-image]').forEach(b=>{
    b.classList.toggle('active',b===button);
    b.setAttribute('aria-pressed',String(b===button));
  });
});
document.querySelector('#larger').onclick=()=>{zoom=Math.min(3,zoom+.25);surface.style.width=(100*zoom)+'%';};
document.querySelector('#smaller').onclick=()=>{zoom=Math.max(.75,zoom-.25);surface.style.width=(100*zoom)+'%';};
</script>
</body>
</html>
'''
    html = html.replace('__ROWS__', '\n'.join(rows)).replace('__COUNT__', str(len(BOM))).replace('__TOTAL__', f'{total:,.2f}')
    (OUT / 'ground-station-physical.html').write_text(html)


def build_sources(outputs):
    used = {key for diagram in outputs.values() for key in diagram['photos']}
    with (HERE / 'image-sources.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=('id', 'name', 'product_page', 'image_url',
                                                  'local_file', 'image_note', 'width', 'height'),
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(photo for key, photo in PHOTOS.items() if key in used)


def main():
    if not shutil.which('rsvg-convert'):
        raise SystemExit('rsvg-convert is required to render PNG images.')
    outputs = {}
    for diagram in (rf_diagram(), rx13_diagram(), tracking_diagram(), power_diagram()):
        outputs[diagram.slug] = diagram.save()
        print(HERE / f'{diagram.slug}.png')
    (HERE / 'connections.json').write_text(json.dumps(outputs, indent=2) + '\n')
    build_viewer()
    build_sources(outputs)


if __name__ == '__main__':
    main()
