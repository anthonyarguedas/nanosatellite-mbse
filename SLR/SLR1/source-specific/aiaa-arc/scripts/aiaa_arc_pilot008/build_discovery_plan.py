#!/usr/bin/env python3
"""Build the predeclared AIAA ARC Pilot 008 Topic discovery plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PILOT005 = ROOT / "source-specific" / "aiaa-arc" / "scripts" / "aiaa_arc_pilot005"
if str(PILOT005) not in sys.path:
    sys.path.insert(0, str(PILOT005))

from queries import PROTOCOL_COMMIT, SCHEDULE  # noqa: E402

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
KNOWN_DOI = "10.2514/6.2015-4474"
TOPIC_CANDIDATES = (
    {
        "label": "Satellites",
        "basis": "Visible Topic facet on the complete Pilot 007 BG1 result page.",
    },
    {
        "label": "Spacecrafts",
        "basis": "Visible Topic facet on the complete Pilot 007 BG1 result page.",
    },
    {
        "label": "Space Systems and Vehicles",
        "basis": "Visible Topic facet on the complete Pilot 007 BG1 result page.",
    },
    {
        "label": "Space Systems",
        "basis": "Visible Topic facet on the complete Pilot 007 BG1 result page.",
    },
    {
        "label": "Spacecraft Design",
        "basis": "Visible Topic facet on the complete Pilot 007 BG1 result page.",
    },
    {
        "label": "Systems Engineering",
        "basis": "Protocol-aligned exact-label probe. Availability must be proved by visible autocomplete.",
    },
    {
        "label": "Small Satellites",
        "basis": "Protocol-population exact-label probe. Availability must be proved by visible autocomplete.",
    },
    {
        "label": "CubeSats",
        "basis": "Protocol-population exact-label probe. Availability must be proved by visible autocomplete.",
    },
    {
        "label": "Nanosatellites",
        "basis": "Protocol-population exact-label probe. Availability must be proved by visible autocomplete.",
    },
)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def event(event_id: str, probe: str, query: str, topic: str | None) -> dict:
    row = {"field": "Anywhere", "source_field": "AllField", "text": query}
    return {
        "event_id": event_id,
        "phase": "candidate_discovery",
        "probe": probe,
        "field_rows": [row],
        "serialized_query": f"Anywhere={query}",
        "serialized_query_sha256": digest(f"Anywhere={query}"),
        "topic_label": topic,
        "mode": "card_preview",
        "output": f"searches/discovery/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/discovery/{event_id}.search-page.png",
            "results_page": f"searches/discovery/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def build() -> dict:
    sentinel_query = f'"{KNOWN_DOI}"'
    events = [event("sentinel-baseline", "known_eligible_sentinel", sentinel_query, None)]
    events.extend(
        event(
            f"sentinel-topic-{slug(candidate['label'])}",
            "known_eligible_sentinel",
            sentinel_query,
            candidate["label"],
        )
        for candidate in TOPIC_CANDIDATES
    )
    events.append(event("bg1-baseline-repeat", "complete_bg1", SCHEDULE["BG1"], None))
    events.extend(
        event(
            f"bg1-topic-{slug(candidate['label'])}",
            "complete_bg1",
            SCHEDULE["BG1"],
            candidate["label"],
        )
        for candidate in TOPIC_CANDIDATES
    )
    if len(events) != 20 or len({entry["event_id"] for entry in events}) != 20:
        raise RuntimeError("Pilot 008 discovery must contain 20 unique events")
    return {
        "schema_version": "aiaa-arc-pilot008-topic-discovery-plan/v1",
        "source": SOURCE,
        "pilot": "008",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Resolve review-relevant exact Topic labels through the visible autocomplete, "
            "test known-item assignment, and measure each Topic's effect on complete BG1 yield."
        ),
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_scope": "inclusive ARC months before exact-day exclusions",
        },
        "candidate_policy": {
            "candidate_count": len(TOPIC_CANDIDATES),
            "candidates": list(TOPIC_CANDIDATES),
            "no_candidate_is_assumed_to_be_a_preferred_term_or_exploded_heading": True,
            "unavailable_or_ambiguous_labels_fail_closed": True,
            "promotion_rule": (
                "A separate extension plan may test accepted-corpus yield only for labels "
                "that resolve to one exact numeric ConceptID in both probes."
            ),
        },
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "wildcard": False,
            "proximity": False,
        },
        "capture": {
            "mode": "non-mergeable rendered-card preview",
            "limit": 100,
            "max_pages": 5,
            "automatic_screenshots_required": True,
        },
        "acceptance_checks": [
            "The unfiltered sentinel and BG1 repeats reproduce their expected source memberships.",
            "Every accepted Topic resolves through the visible autocomplete to a numeric ConceptID.",
            "The configured search reads back the exact Topic label and ConceptID.",
            "Every successful event is completely captured and remains at most 100 records.",
            "Every successful JSON has both mandatory sibling screenshots.",
            "A Topic cannot become an AND filter if it loses the known eligible sentinel.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
