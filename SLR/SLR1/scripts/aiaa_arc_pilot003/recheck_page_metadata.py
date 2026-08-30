#!/usr/bin/env python3
"""Re-read visible page metadata for a retained non-mergeable DOI prefix."""

from __future__ import annotations

import argparse
import asyncio
import json

from run_fielded_count import write_full_json
from run_stage1 import SEARCH_DIR
from sample_prefix import cell_configs, evidence, scrape_record_pages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", required=True, choices=("A2", "BT2"))
    parser.add_argument("--suffix", default="recheck", help="Output suffix after page-metadata, without .json")
    args = parser.parse_args()
    input_path = SEARCH_DIR / f"{args.schedule}-sampled-prefix-preview.json"
    output_path = SEARCH_DIR / f"{args.schedule}-sampled-prefix-page-metadata-{args.suffix}.json"
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite {output_path}")
    source = json.loads(input_path.read_text())
    configs = {config["cell_id"]: config for config in cell_configs(args.schedule)}
    records = source.get("sampled_records", [])
    observations = asyncio.run(scrape_record_pages(records))
    by_doi = {item["doi"]: item for item in observations}
    output_records = []
    for record in records:
        observed = by_doi.get(record["doi"], {"doi": record["doi"], "status": "metadata_unavailable"})
        config = configs[record["source_cell"]]
        output_records.append(
            {
                "doi": record["doi"],
                "source_cell": record["source_cell"],
                "source_rank": record.get("source_rank"),
                "title": record.get("title"),
                "page_metadata": observed,
                "diagnostic": evidence(args.schedule, observed, config),
            }
        )
    payload = {
        "schema_version": "aiaa-arc-visible-page-metadata-recheck/v1",
        "source": "AIAA Aerospace Research Central (ARC)",
        "pilot": "003",
        "schedule_id": args.schedule,
        "do_not_merge": True,
        "input_prefix_artifact": input_path.name,
        "purpose": "Recheck visible title, abstract, keywords, publication-type metadata, and local block evidence without rerunning the source query.",
        "records": output_records,
        "limitations": [
            "Record-page metadata remains insufficient to prove full-text eligibility or that a source match is false.",
            "Missing page metadata is retained as unavailable rather than classified as a mismatch.",
        ],
    }
    write_full_json(output_path, payload)
    print(json.dumps({"saved": str(output_path), "records": len(output_records)}, indent=2))


if __name__ == "__main__":
    main()
