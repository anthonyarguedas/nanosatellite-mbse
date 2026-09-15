#!/usr/bin/env python3
"""Assess repeated ordering of the four Scopus B1 swapping records."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA = "scopus-tied-order-diagnostic-assessment/v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output}")

    plan = load(args.plan)
    expected = set(plan["identity_query"]["paper_ids"])
    sequences = []
    event_rows = []
    errors = []
    screenshot_count = 0
    for event in plan["events"]:
        path = args.pilot_root / "searches" / event["output"]
        try:
            value = load(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"{event['event_id']}:{type(error).__name__}")
            continue
        records = value.get("results", [])
        ids = tuple(
            record.get("paperId")
            for record in records
            if isinstance(record, dict) and isinstance(record.get("paperId"), str)
        )
        years = tuple(record.get("year") for record in records if isinstance(record, dict))
        metadata = value.get("output_metadata", {})
        screenshots = metadata.get("screenshots", {})
        valid = bool(
            value.get("requested_query") == event["query"]
            and value.get("total") == 4
            and len(ids) == 4
            and set(ids) == expected
            and len(set(ids)) == 4
            and metadata.get("retrieval_complete") is True
            and metadata.get("merge_eligible") is False
            and screenshots.get("schema_version")
            == "scopus-automatic-screenshots/v1"
        )
        for key, suffix in (
            ("search_page", ".search-page.png"),
            ("results_page", ".results-page.png"),
        ):
            image = path.with_name(f"{path.stem}{suffix}")
            evidence = screenshots.get(key, {})
            if (
                not image.is_file()
                or evidence.get("path") != image.name
                or evidence.get("sha256") != digest(image)
            ):
                valid = False
            screenshot_count += 1
        if not valid:
            errors.append(f"invalid:{event['event_id']}")
            continue
        sequences.append(ids)
        event_rows.append(
            {
                "event_id": event["event_id"],
                "artifact": str(path),
                "sha256": digest(path),
                "ordered_paper_ids": list(ids),
                "ordered_years": list(years),
            }
        )

    pair_2022 = tuple(plan["identity_query"]["paper_ids"][:2])
    pair_2025 = tuple(plan["identity_query"]["paper_ids"][2:])

    def relative_order(sequence: tuple[str, ...], pair: tuple[str, str]) -> str:
        return "first_then_second" if sequence.index(pair[0]) < sequence.index(pair[1]) else "second_then_first"

    sequence_counts = Counter(sequences)
    order_2022 = Counter(relative_order(sequence, pair_2022) for sequence in sequences)
    order_2025 = Counter(relative_order(sequence, pair_2025) for sequence in sequences)
    years_monotonic = all(
        all(left <= right for left, right in zip(row["ordered_years"], row["ordered_years"][1:]))
        for row in event_rows
    )
    complete = len(event_rows) == 6 and not errors
    stable_tie_breaker = complete and len(sequence_counts) == 1
    assessment = {
        "schema_version": SCHEMA,
        "pilot": "010",
        "source": "Scopus",
        "diagnostic_only": True,
        "do_not_merge": True,
        "plan": str(args.plan),
        "plan_sha256": digest(args.plan),
        "event_count": len(event_rows),
        "verified_screenshot_file_count": screenshot_count,
        "requested_stable_id_set_reproduced_in_every_event": complete,
        "date_oldest_year_order_monotonic_in_every_event": complete and years_monotonic,
        "unique_full_order_count": len(sequence_counts),
        "full_order_frequencies": [
            {"ordered_paper_ids": list(sequence), "frequency": frequency}
            for sequence, frequency in sequence_counts.items()
        ],
        "same_year_pair_order_frequencies": {
            "2022": dict(order_2022),
            "2025": dict(order_2025),
        },
        "stable_secondary_tie_breaker_observed": stable_tie_breaker,
        "exact_publication_dates_available_in_retained_rows": False,
        "finding": (
            "All complete sets were equal, while same-year order varied. No stable secondary tie-break pattern was observed."
            if complete and not stable_tie_breaker
            else "All complete sets and observed orders were equal in this bounded repeat. This does not prove a permanent source tie-break rule."
            if stable_tie_breaker
            else "The diagnostic did not complete."
        ),
        "adapter_implication": (
            "Strict completion should require equal complete stable-ID sets and retain order agreement as audit evidence rather than a membership gate."
            if complete
            else "No adapter change is authorized by this incomplete diagnostic."
        ),
        "events": event_rows,
        "errors": errors,
        "status": "passed" if complete else "failed",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": assessment["status"],
                "unique_orders": len(sequence_counts),
                "pair_2022": dict(order_2022),
                "pair_2025": dict(order_2025),
            }
        )
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
