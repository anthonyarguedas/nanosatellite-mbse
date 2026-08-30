#!/usr/bin/env python3
"""Create a no-clobber pilot event plan for one source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from queries import MAIN_FACTORS, PSR_FACTORS, RENDERERS, partition_cells, partition_query


SCHEMA_VERSION = "academic-search-event-schedule/v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, choices=tuple(RENDERERS))
    parser.add_argument("--output-path", required=True, type=Path)
    parser.add_argument("--pilot-number", required=True)
    parser.add_argument("--pilot-mode", default="bounded_records")
    parser.add_argument("--review-id", default="slr1-pilot")
    parser.add_argument(
        "--strategy-reference", default="slr1-direct-query-schedule-v1"
    )
    parser.add_argument("--strategy-version", default="8f5dc8e")
    parser.add_argument("--adapter-arg", action="append", default=[])
    parser.add_argument("--max-query-characters", type=int)
    parser.add_argument("--psr", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.psr and args.source not in {
        "scopus",
        "web_of_science_core_collection",
    }:
        raise SystemExit("PSR plans are restricted to Scopus and Web of Science")
    partitions = PSR_FACTORS if args.psr else MAIN_FACTORS
    namespace = "prior_secondary_reviews" if args.psr else "main"
    events = []
    for partition_id in partitions:
        event = {
            "event_kind": "pilot",
            "pilot_mode": args.pilot_mode,
            "review_namespace": namespace,
            "source": args.source,
            "partition_id": partition_id,
            "review_id": args.review_id,
            "strategy_reference": args.strategy_reference,
            "strategy_version": args.strategy_version,
            "event_id": (
                f"pilot-{namespace}-{partition_id}-{args.source}-"
                f"{args.pilot_number}"
            ),
        }
        if args.adapter_arg:
            event["adapter_args"] = args.adapter_arg
        query = partition_query(args.source, partition_id)
        if args.max_query_characters and len(query) > args.max_query_characters:
            event["query_cells"] = list(
                partition_cells(
                    args.source,
                    partition_id,
                    maximum_characters=args.max_query_characters,
                )
            )
        else:
            event["query"] = query
        if args.source == "web_of_science_core_collection":
            event["query_mode"] = "raw"
        events.append(event)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "planned_sources": {namespace: [args.source]},
        "events": events,
    }
    output = args.output_path.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
