#!/usr/bin/env python3
"""Record the source-located Pilot 004 known-item eligibility and membership check."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from common import (
    KNOWN_DOI,
    KNOWN_TITLE,
    SEARCH_DIR,
    atomic_write_json,
    load_json,
    visible_block_hits,
)

PDF_RELATIVE_PATH = (
    "SLR/SLR1/pdfs/paper-0022_2015_cubesat-model-based-system-engineering-"
    "mbse-reference-model-application-in-the-concept-lif.pdf"
)


def pdf_text(pdf: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "pdftotext failed")
    return completed.stdout


def page_and_excerpt(text: str, phrase: str, width: int = 300) -> dict[str, Any]:
    # PDF extraction can line-wrap an otherwise exact source phrase. Preserve
    # lexical text while allowing only whitespace to differ in its locator.
    pattern = r"\s+".join(re.escape(part) for part in phrase.split())
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None:
        raise RuntimeError(f"Could not locate required full-text phrase: {phrase!r}")
    index = match.start()
    excerpt = " ".join(text[max(0, index - 80) : match.end() + width].split())
    return {"pdf_page": text[:index].count("\f") + 1, "phrase": phrase, "excerpt": excerpt}


def pdf_page_count(pdf: Path) -> int:
    completed = subprocess.run(["pdfinfo", str(pdf)], text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "pdfinfo failed")
    match = re.search(r"^Pages:\s+(\d+)\s*$", completed.stdout, flags=re.MULTILINE)
    if match is None:
        raise RuntimeError("pdfinfo did not report a page count")
    return int(match.group(1))


def source_index_record() -> dict[str, Any]:
    candidates = sorted(SEARCH_DIR.glob("known-item-source-indexing-doi*.json"))
    for candidate in candidates:
        if ".NON_MERGEABLE_FAILURE" in candidate.name or candidate.name.startswith("."):
            continue
        data = load_json(candidate)
        for row in data.get("results", []):
            if isinstance(row, dict) and str(row.get("doi", "")).casefold() == KNOWN_DOI:
                return {
                    "artifact": str(candidate.relative_to(SEARCH_DIR.parent)),
                    "doi": row.get("doi"),
                    "source_record_stable_id": row.get("sourceRecordStableId"),
                    "title": row.get("title"),
                    "author": [author.get("name") for author in row.get("authors", []) if isinstance(author, dict)],
                    "publication_date": row.get("publicationDate"),
                    "publication_title": row.get("publicationTitle"),
                    "url": row.get("url"),
                }
    raise RuntimeError("No successful source-indexing artifact retains the known DOI")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path, help="Ignored project PDF cache path")
    args = parser.parse_args()
    pdf = args.pdf.expanduser().resolve()
    if not pdf.is_file():
        raise SystemExit(f"Missing known-item PDF: {pdf}")
    text = pdf_text(pdf)
    metadata = source_index_record()
    if metadata["title"] != KNOWN_TITLE:
        raise SystemExit("source indexing title differs from the required known item")

    block_hits = {
        name: visible_block_hits(text, name)
        for name in ("P", "E_H", "E_F", "M_H", "M_B", "M_H_OR_M_B", "R", "G_model", "G_structure", "C1", "T2")
    }
    applicable = {
        "A1": block_hits["P"]["matched"] and block_hits["E_H"]["matched"] and block_hits["M_H"]["matched"],
        "A2": block_hits["P"]["matched"] and block_hits["E_F"]["matched"] and block_hits["M_H_OR_M_B"]["matched"],
        "A3": block_hits["P"]["matched"] and block_hits["E_H"]["matched"] and block_hits["M_B"]["matched"],
        "B1": block_hits["P"]["matched"] and block_hits["M_H"]["matched"],
        "B2": block_hits["P"]["matched"] and block_hits["M_B"]["matched"] and block_hits["R"]["matched"],
        "BG1": block_hits["P"]["matched"] and block_hits["G_model"]["matched"],
        "BG2": block_hits["P"]["matched"] and block_hits["G_structure"]["matched"],
        "BC1": block_hits["P"]["matched"] and block_hits["C1"]["matched"],
        "BT2": block_hits["P"]["matched"] and block_hits["M_B"]["matched"] and block_hits["T2"]["matched"],
    }
    expected = {"A2", "B1", "B2", "BC1", "BT2"}
    observed = {name for name, value in applicable.items() if value}
    if observed != expected:
        raise SystemExit(f"source-located scheduled membership changed: {sorted(observed)}")

    evidence = {
        "schema_version": "aiaa-arc-pilot004-known-item-evidence/v1",
        "pilot": "004",
        "known_item": {
            "doi": KNOWN_DOI,
            "title": KNOWN_TITLE,
            "project_pdf_relative_path": PDF_RELATIVE_PATH,
            "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "pdf_page_count": pdf_page_count(pdf),
            "source_indexing": metadata,
        },
        "source_located_eligibility": {
            "status": "known_eligible_arc_sentinel",
            "publication_date_and_type": "ARC's rendered DOI result identifies 31 Aug-2 Sep 2015, AIAA SPACE 2015 Conference and Exposition; the local source is an 11-page English AIAA paper.",
            "population_and_mbse": page_and_excerpt(text, "Model-Based Systems Engineering (MBSE) is a key practice"),
            "eps_anchor": page_and_excerpt(text, "Generate, regulate, store, and distribute power to the spacecraft."),
            "model_to_eps_bridge": page_and_excerpt(text, "Properties and parametrics at subsystem level for power and weight"),
            "model_use_for_power": page_and_excerpt(text, "candidate models for the Data Acquisition and Handing, Power, and Communication subsystems"),
            "route": "Route B embedded EPS model thread: the named Power subsystem is represented through the reference model's power properties/parametrics and candidate model trade-space use.",
        },
        "exact_full_text_block_check": {
            "method": "Case-folded ordered lexical literals and either-order declared pairs with at most five intervening lexical tokens; source text is used only to establish known-item scheduled membership.",
            "blocks": block_hits,
            "applicable_scheduled_partitions": sorted(observed),
            "nonapplicable_scheduled_partitions": {
                "A1": "E_H has no source-located literal hit.",
                "A3": "E_H has no source-located literal hit.",
                "BG1": "G_model has no source-located fixed literal or declared pair hit.",
                "BG2": "G_structure has no source-located fixed literal or declared pair hit.",
            },
            "important_limits": "ARC may still retrieve this DOI from hidden indexing or full text in a partition whose source-located visible metadata/full text does not demonstrate that partition's literal membership. Such retrieval does not expand the recall obligation or establish a false match.",
        },
        "source_locations": {
            "title_and_reference_model": page_and_excerpt(text, "CubeSat Model-Based System Engineering (MBSE)"),
            "functional_eps_terms": page_and_excerpt(text, "solar panel area and maximum battery capacity"),
            "relationship_terms": page_and_excerpt(text, "requirements, structures, behaviors, and parametrics"),
            "central_asset": page_and_excerpt(text, "CubeSat Reference Model as a starting point"),
            "t2_pair": page_and_excerpt(text, "Model-Based Systems Engineering Roadmap. Adapted from Ref. 3."),
        },
        "other_known_eligible_arc_items_added": [],
    }
    output = SEARCH_DIR / "known-item-evidence.json"
    if output.exists():
        raise SystemExit(f"Refusing to overwrite {output}")
    atomic_write_json(output, evidence)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
