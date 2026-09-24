#!/usr/bin/env python3
"""Build derived CSRM subsystem and AIT contact overlays without editing source diagrams."""

from __future__ import annotations

import base64
import hashlib
import struct
import subprocess
from dataclasses import dataclass
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent / "annotated"
VIEWS = (
    ("ets_faculty", "ÉTS faculty", "ets-ait-domain.sysml"),
    ("mcgill_faculty", "McGill faculty", "mcgill-ait-domain.sysml"),
    ("ets_club", "RockÉTS", "ets-ait-domain.sysml"),
    ("mcgill_club", "McGill Rocket Team", "mcgill-ait-domain.sysml"),
)


@dataclass(frozen=True)
class Subsystem:
    code: str
    label: tuple[str, ...]
    color: str
    box: tuple[int, int, int, int]  # Pixel bounds in the original PNG.


@dataclass(frozen=True)
class Contact:
    names: tuple[str, ...]
    kind: str  # topic: relevant published topic; related: adjacent role or rocket work.


SPACE = (
    Subsystem("S1", ("Mission Payload",), "#B42318", (111, 892, 513, 979)),
    Subsystem("S2", ("Command and Data", "Handling"), "#B85B00", (125, 1034, 435, 1148)),
    Subsystem("S3", ("Communication",), "#914200", (140, 1201, 435, 1317)),
    Subsystem("S4", ("Attitude Determination", "and Control"), "#673AB7", (572, 1034, 911, 1149)),
    Subsystem("S5", ("Guidance, Navigation", "and Control"), "#005A9C", (572, 1160, 925, 1275)),
    Subsystem("S6", ("Structures and", "Mechanisms"), "#00786E", (572, 1290, 925, 1405)),
    Subsystem("S7", ("Power",), "#726000", (1092, 1019, 1355, 1101)),
    Subsystem("S8", ("Thermal",), "#A61C6D", (1092, 1162, 1378, 1243)),
    Subsystem("S9", ("Propulsion (trade)",), "#374151", (1092, 1290, 1419, 1373)),
)
GROUND = (
    Subsystem("G1", ("Plan and Schedule",), "#4A148C", (180, 873, 490, 988)),
    Subsystem("G2", ("Spacecraft Command",), "#0B6E3F", (166, 1028, 490, 1146)),
    Subsystem("G3", ("Ground Equipment", "Control"), "#0E7490", (180, 1181, 490, 1305)),
    Subsystem("G4", ("Space–Ground", "Communication"), "#B34411", (612, 875, 947, 1025)),
    Subsystem("G5", ("Mission Data", "Processing"), "#1D4ED8", (612, 1043, 935, 1194)),
    Subsystem("G6", ("Mission Data", "Dissemination"), "#9F1239", (626, 1211, 948, 1360)),
    Subsystem("G7", ("Network",), "#535D0A", (1116, 877, 1341, 996)),
    Subsystem("G8", ("Facilities",), "#6B4F37", (1116, 1062, 1354, 1193)),
    Subsystem("G9", ("Telemetry Processing",), "#7634C6", (1116, 1211, 1385, 1430)),
)

# Only people flagged potentialContact=true in the AIT models appear here.
# A division director is an inquiry point, not a named OCS project lead.
# Rocket roles are related experience, not orbital or ground station capability.
CONTACTS: dict[str, dict[str, Contact]] = {
    "S1": {
        "ets_club": Contact(("Maëlle Marinier",), "related"),
        "mcgill_club": Contact(("Ashlyn Bourgeois", "Lily White"), "related"),
    },
    "S2": {
        "ets_faculty": Contact(("Jesus David Gonzalez Llorente",), "related"),
        "ets_club": Contact(("Samuel Laplante",), "related"),
        "mcgill_club": Contact(("Abdel Elbarkouky", "Rose Storozuk"), "related"),
    },
    "S3": {
        "ets_faculty": Contact(("Ammar B. Kouki",), "topic"),
        "mcgill_faculty": Contact(("Harry Leib",), "topic"),
        "ets_club": Contact(("Samuel Laplante",), "related"),
        "mcgill_club": Contact(("Abdel Elbarkouky", "Rose Storozuk"), "related"),
    },
    "S4": {
        "mcgill_faculty": Contact(("Inna Sharf",), "topic"),
        "mcgill_club": Contact(("Abdel Elbarkouky", "Rose Storozuk"), "related"),
    },
    "S5": {
        "ets_faculty": Contact(("René Jr Landry",), "topic"),
        "mcgill_faculty": Contact(("James Richards Forbes",), "topic"),
    },
    "S6": {
        "mcgill_faculty": Contact(("Pascal Hubert",), "topic"),
        "ets_club": Contact(("Paul Arnautovich",), "related"),
        "mcgill_club": Contact(("Majd Boulos", "Maël Cipréos"), "related"),
    },
    "S7": {
        "ets_faculty": Contact(("Jesus David Gonzalez Llorente",), "topic"),
        "mcgill_club": Contact(("Abdel Elbarkouky", "Rose Storozuk"), "related"),
    },
    "S8": {"ets_faculty": Contact(("Jesus David Gonzalez Llorente",), "related")},
    "S9": {
        "ets_club": Contact(("Olivier Nolin",), "related"),
        "mcgill_faculty": Contact(("Andrew Higgins",), "related"),
        "mcgill_club": Contact(("Logan Acott", "Athanasios Mavrakanas"), "related"),
    },
    "G1": {
        "ets_faculty": Contact(("Jean-Marc Gagné",), "related"),
        "ets_club": Contact(("Audrey Provencher",), "related"),
    },
    "G4": {
        "ets_faculty": Contact(("Ammar B. Kouki",), "related"),
        "mcgill_faculty": Contact(("Harry Leib",), "related"),
        "mcgill_club": Contact(("Abdel Elbarkouky", "Rose Storozuk"), "related"),
    },
    "G9": {
        "ets_club": Contact(("Samuel Laplante",), "related"),
        "mcgill_club": Contact(("Léo Mindlin", "Carolyn Wu"), "related"),
    },
}

DISPLAY_NAMES = {"Jesus David Gonzalez Llorente": "J. D. Gonzalez Llorente"}

SOURCES = (
    ("csrm-space-segment.png", "ae864448f181685aefc5e9de86113f51b445f5547e66d742b7d3be83161e63df", SPACE, "space"),
    ("csrm-ground-segment.png", "83dfb4e42910d838525299f49af7ebea6f1a7fe5a5725241f0f9c360a2211400", GROUND, "ground"),
)


def text(x: int, y: int, value: str, size: int = 21, color: str = "#17202E", weight: int = 400) -> str:
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" font-family="Arial, Helvetica, sans-serif">{escape(value)}</text>')


def rect(x: int, y: int, w: int, h: int, fill: str, **attrs: object) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def validate() -> None:
    all_codes = [item.code for _, _, items, _ in SOURCES for item in items]
    assert len(all_codes) == 18 and len(set(all_codes)) == len(all_codes)
    assert set(CONTACTS) <= set(all_codes)
    for code, views in CONTACTS.items():
        for key, candidate in views.items():
            source_file = next((filename for view, _, filename in VIEWS if view == key), None)
            assert source_file and candidate.kind in {"topic", "related"}, (code, key)
            source = (Path(__file__).resolve().parent / source_file).read_text()
            for name in candidate.names:
                start = source.index(f"part def '{name}'")
                person_block = source[start:source.index("}", start)]
                assert "attribute potentialContact : ScalarValues::Boolean = true;" in person_block, (code, key, name)


def build(source: Path, expected_hash: str, subsystems: tuple[Subsystem, ...], segment: str) -> None:
    data = source.read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected_hash, f"PNG changed; recalibrate box positions: {source}"
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    panel_x = width + 18
    total_width = width + 2070
    origin = panel_x + 24
    row_top, row_height = 98, 159
    assert height >= 1550
    for item in subsystems:
        x0, y0, x1, y1 = item.box
        assert 0 < x0 < x1 < width and 0 < y0 < y1 < height

    result = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{height}" viewBox="0 0 {total_width} {height}">',
        rect(0, 0, total_width, height, "white"),
        f'<image x="0" y="0" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(data).decode()}"/>',
    ]
    for item in subsystems:
        x0, y0, x1, y1 = item.box
        result += [
            rect(x0, y0, x1-x0, y1-y0, item.color, fill_opacity="0.07", stroke=item.color, stroke_width="5"),
            rect(x0 + 6, y0 + 6, 32, 26, item.color, rx="4"),
            text(x0 + 9, y0 + 25, item.code, 15, "white", 700),
        ]

    result += [rect(panel_x, 0, 2052, height, "#FFFFFF"),
               rect(origin, 12, 2000, 76, "#E9EFF7", rx="6")]
    col_start, col_width = origin + 440, 390
    for i, (_, label, _) in enumerate(VIEWS):
        result.append(text(col_start + i * col_width + 15, 61, label, 27, weight=700))
    result.append(text(origin + 12, 61, "CSRM subsystem", 27, weight=700))

    for row, item in enumerate(subsystems):
        y = row_top + row * row_height
        result.append(rect(origin, y, 2000, row_height - 3, "#F6F8FC" if row % 2 == 0 else "#FFFFFF", stroke="#D7DDE7", stroke_width="1"))
        result.append(rect(origin + 12, y + 17, 64, 38, item.color, rx="5"))
        result.append(text(origin + 20, y + 45, item.code, 25, "white", 700))
        for line, name in enumerate(item.label):
            result.append(text(origin + 90, y + 46 + line * 36, name, 27, weight=600))
        for index, (key, _, _) in enumerate(VIEWS):
            x = col_start + index * col_width
            result.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+row_height-3}" stroke="#DEE3EB"/>')
            contact = CONTACTS.get(item.code, {}).get(key)
            if contact is None:
                result.append(text(x + 16, y + 80, "OPEN · no named match", 25, "#596474"))
                continue
            result.append(rect(x + 8, y + 9, 372, row_height - 22, item.color,
                               fill_opacity="0.07", rx="5",
                               stroke=item.color if contact.kind == "topic" else "#AAB4C3",
                               stroke_width="1", stroke_dasharray="none" if contact.kind == "topic" else "4 4"))
            for n, name in enumerate(contact.names):
                result.append(text(x + 18, y + 48 + n * 39, DISPLAY_NAMES.get(name, name), 27, item.color, 700))
            result.append(text(x + 18, y + 129, "TOPIC MATCH" if contact.kind == "topic" else "RELATED ONLY · OPEN", 21, "#465264", 700))
    result.append("</svg>")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    svg = OUTPUT / f"csrm-{segment}-contact-overlay.svg"
    png = svg.with_suffix(".png")
    svg.write_text("\n".join(result) + "\n")
    subprocess.run(["rsvg-convert", "--format", "png", "--output", str(png), str(svg)], check=True)
    print(svg.relative_to(ROOT), png.relative_to(ROOT), sep="\n")


if __name__ == "__main__":
    validate()
    for filename, digest, items, label in SOURCES:
        build(Path(__file__).resolve().parent / "reference" / filename, digest, items, label)
