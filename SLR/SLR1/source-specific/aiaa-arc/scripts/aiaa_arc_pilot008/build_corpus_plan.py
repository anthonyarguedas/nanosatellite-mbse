#!/usr/bin/env python3
"""Build the triggered Pilot 008 accepted-corpus Topic yield plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
CHUNK_SIZE = 20


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode())


def slug(value: str) -> str:
    return "-".join(part for part in value.casefold().replace("&", " and ").split() if part)


def doi_query(dois: list[str]) -> str:
    return "(" + " OR ".join(f'"{doi}"' for doi in dois) + ")"


def event(
    chunk_id: str,
    dois: list[str],
    topic_selection: dict[str, str] | None,
) -> dict[str, Any]:
    query = doi_query(dois)
    suffix = "baseline" if topic_selection is None else f"topic-{slug(topic_selection['label'])}"
    event_id = f"{chunk_id}-{suffix}"
    return {
        "event_id": event_id,
        "phase": "accepted_corpus_yield",
        "chunk_id": chunk_id,
        "expected_canonical_dois": dois,
        "expected_canonical_doi_count": len(dois),
        "field_rows": [
            {"field": "Anywhere", "source_field": "AllField", "text": query}
        ],
        "serialized_query": f"Anywhere={query}",
        "serialized_query_sha256": sha256_text(f"Anywhere={query}"),
        "topic_selection": topic_selection,
        "mode": "card_preview",
        "output": f"searches/corpus/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/corpus/{event_id}.search-page.png",
            "results_page": f"searches/corpus/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def build(
    discovery_assessment_path: Path,
    pilot007_assessment_path: Path,
) -> dict[str, Any]:
    discovery_bytes = discovery_assessment_path.read_bytes()
    corpus_bytes = pilot007_assessment_path.read_bytes()
    discovery = json.loads(discovery_bytes)
    corpus = json.loads(corpus_bytes)
    trigger = discovery.get("extension_trigger", {})
    if trigger.get("status") != "triggered":
        raise RuntimeError("Pilot 008 corpus extension trigger is absent")
    promoted = trigger.get("promoted_distinct_selections")
    if not isinstance(promoted, list) or not promoted:
        raise RuntimeError("Pilot 008 corpus extension has no promoted Topic selections")
    topic_selections = []
    seen_ids = set()
    for entry in promoted:
        label = entry.get("label")
        concept_id = entry.get("concept_id")
        if (
            not isinstance(label, str)
            or not label
            or not isinstance(concept_id, str)
            or not concept_id.isdecimal()
            or concept_id in seen_ids
        ):
            raise RuntimeError("Invalid or duplicate promoted Topic selection")
        seen_ids.add(concept_id)
        topic_selections.append({"label": label, "concept_id": concept_id})
    dois = corpus.get("overall_union", {}).get("canonical_dois")
    if (
        not isinstance(dois, list)
        or len(dois) != 119
        or len(set(dois)) != 119
        or dois != sorted(dois)
    ):
        raise RuntimeError("Pilot 007 accepted corpus must contain 119 sorted canonical DOIs")
    chunks = [dois[index:index + CHUNK_SIZE] for index in range(0, len(dois), CHUNK_SIZE)]
    if len(chunks) != math.ceil(len(dois) / CHUNK_SIZE):
        raise RuntimeError("Unexpected DOI chunk count")
    events = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = f"corpus-{index:02d}"
        events.append(event(chunk_id, chunk, None))
        events.extend(event(chunk_id, chunk, selection) for selection in topic_selections)
    expected_event_count = len(chunks) * (1 + len(topic_selections))
    if len(events) != expected_event_count or len({entry["event_id"] for entry in events}) != expected_event_count:
        raise RuntimeError("Pilot 008 corpus plan event count is invalid")
    return {
        "schema_version": "aiaa-arc-pilot008-topic-corpus-plan/v1",
        "source": SOURCE,
        "pilot": "008",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Measure how each sentinel-retaining distinct ARC Topic identity changes yield "
            "within the complete accepted Pilot 007 119-DOI corpus."
        ),
        "date_window": {
            "requested_start": DATE_START,
            "requested_end": DATE_END,
            "source_scope": "inclusive ARC months before exact-day exclusions",
        },
        "trigger_evidence": {
            "discovery_assessment": str(discovery_assessment_path),
            "discovery_assessment_sha256": sha256_bytes(discovery_bytes),
            "rule": trigger.get("rule"),
            "promoted_distinct_selections": topic_selections,
        },
        "accepted_corpus": {
            "pilot007_assessment": str(pilot007_assessment_path),
            "pilot007_assessment_sha256": sha256_bytes(corpus_bytes),
            "canonical_doi_count": len(dois),
            "canonical_dois_sha256": sha256_text("\n".join(dois) + "\n"),
            "chunk_size": CHUNK_SIZE,
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "chunk_id": f"corpus-{index:02d}",
                    "canonical_doi_count": len(chunk),
                    "canonical_dois": chunk,
                }
                for index, chunk in enumerate(chunks, start=1)
            ],
        },
        "comparison": {
            "design": "paired complete DOI-membership cells",
            "baseline_per_chunk": True,
            "one_filtered_event_per_distinct_topic_id_per_chunk": True,
            "multi_topic_union": "reconcile the separately filtered canonical DOI sets offline",
            "reason_for_offline_union": (
                "Repeated Topic selection Boolean semantics are not assumed. Separate source calls "
                "measure each identity and permit a transparent at-least-one-Topic union."
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
            "Every baseline DOI chunk reproduces its complete predeclared canonical DOI set.",
            "Each filtered set is a subset of its paired baseline chunk.",
            "Every typed Topic label resolves visibly to its predeclared numeric ConceptID.",
            "Every event remains at most 100 records and is captured completely.",
            "Every successful JSON has both mandatory sibling screenshots.",
            "No Topic restriction is accepted if any baseline corpus DOI has unclassified eligibility.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery-assessment", type=Path, required=True)
    parser.add_argument("--pilot007-assessment", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.discovery_assessment, args.pilot007_assessment)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
