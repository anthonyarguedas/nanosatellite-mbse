#!/usr/bin/env python3
"""Reproduce source-document crops for the EPS case study appendix.

Requires PyMuPDF. Cropping retains original text, figures, colours and markings.
No figures are redrawn, highlighted, recoloured or composed from altered cells.
Coordinates use PDF points from the top-left of the original, one-based page.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "eps-case-studies"
sys.path.insert(0, str(OUT))
from independent_cots_reference import SOURCES  # noqa: E402

# Discontinuous excerpts remain separate PDFs and separate labelled panels.
CROPS = {
    "birds-demand": ("birds_budget", 9, (0, 101, 670, 171), ["11", "14a"],
                     "Published nominal demand and 90-minute operating period."),
    "birds-generation": ("birds_budget", 8, (8, 98, 683, 352), ["11", "14a"],
                         "Complete low-beta columns, preserving five/four/three-panel budgets, diode loss and BCR efficiency."),
    "oresat-supply-storage-standby": ("oresat_budget", 1, (71, 86, 397, 301), ["11", "14a", "16"],
                                     "Numerical columns from generation, four 2S pack storage and standby load budgets. Notes column omitted."),
    "oresat-live": ("oresat_budget", 1, (71, 311, 397, 428), ["11", "14a"],
                    "OreSat Live load rows and 2318 mWh session total. Notes column omitted."),
    "oresat-reserve": ("oresat_budget", 2, (71, 82, 397, 104), ["11"],
                       "Published 24.6 Live passes to 60% DoD. Notes column omitted."),
    "birds-battery-configuration": ("birds_cells", 21, (90, 204, 296, 411), ["11", "12", "16"],
                                   "Original 3S2P schematic and capacity, voltage, 27 g cell mass and 162 g cell-sum table. Right-hand wiring drawings omitted."),
    "oresat-battery-configuration": ("oresat_account", 6, (71, 321, 302, 514), ["11", "16"],
                                    "Two independently protected 2S Tenergy packs, 3.6 V and 2600 mAh cells and 37.4 Wh card energy."),
    "oresat-solar-configuration": ("oresat_account", 5, (314, 462, 542, 583.6), ["11", "14b", "16"],
                                  "2021 account identifies two XTE-SF cells per module and its 2.3 W maximum power."),
    "azur-electrical-ratings": ("azur", 2, (84, 294, 515, 431), ["11", "14b", "18"],
                               "Original BOL and radiation columns, including MPP pairs, AM0 and temperature conditions."),
    "spectrolab-electrical-ratings": ("spectrolab", 1, (10, 278, 539, 436), ["11", "14b"],
                                     "Original US-standard retention table, BOL Vmp and Jmp, 27 cm2 area, AM0 and temperature footnote."),
    "oresat-mass-headings": ("oresat_mass", 22, (52, 49, 560, 74), ["12"],
                             "Original mass-table column headings, separately cropped from the selected rows."),
    "oresat-mass-rows": ("oresat_mass", 22, (52, 237, 560, 302), ["12"],
                         "Original eight solar and four battery module rows, with published preliminary-estimate notes."),
    "birds-iv-labels": ("birds_safety", 6, (327, 543, 550, 692), ["18"],
                        "Original Figure 13 plot. Voltage labels and the 50 mA abscissa are retained. Surrounding prose and original caption omitted."),
    "birds-pv-labels": ("birds_safety", 7, (76, 84, 290, 212), ["18"],
                        "Original Figure 14 plot, including 0.257 W and 1.575 W labels. Surrounding prose and original caption omitted."),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(output):
    output.mkdir(parents=True, exist_ok=True)
    records = {}
    for name, (source_id, number, coordinates, mops, purpose) in CROPS.items():
        source = SOURCES[source_id]
        original = ROOT / source["path"]
        actual_sha = sha256(original)
        if source.get("sha256") and source["sha256"] != actual_sha:
            raise ValueError(f"Original source changed: {original}")
        with pymupdf.open(original) as document, pymupdf.open() as cropped:
            page = document[number - 1]
            rectangle = pymupdf.Rect(coordinates)
            if not page.rect.contains(rectangle):
                raise ValueError(f"Crop lies outside source page: {name}")
            destination = cropped.new_page(width=rectangle.width, height=rectangle.height)
            destination.show_pdf_page(destination.rect, document, number - 1, clip=rectangle)
            cropped.set_metadata({"title": f"{source['citation']}, page {number}: {name}",
                                  "subject": "Unaltered source excerpt. Cropping only."})
            target = output / (name + ".pdf")
            cropped.save(target, garbage=4, deflate=True, no_new_id=True)
            records[name] = {"source": source_id, "citation": source["citation"], "url": source["url"],
                             "original_sha256": actual_sha, "page": number,
                             "original_page_points": list(page.rect), "crop_points": list(coordinates),
                             "mops": mops, "purpose": purpose, "output_sha256": sha256(target),
                             "source_text_in_crop": page.get_text(clip=rectangle, sort=True),
                             "alterations": "Cropping only. Original colours, markings and content retained."}
    (output / "source-evidence.json").write_text(json.dumps({
        "generator": "final_report/fig/case-study-source-crops.py", "generator_sha256": sha256(Path(__file__)),
        "pymupdf_version": pymupdf.__version__,
        "crops": records,
    }, indent=2, sort_keys=True) + "\n")
    print(f"Generated {len(records)} original-document PDF crops in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT)
    generate(parser.parse_args().output)
