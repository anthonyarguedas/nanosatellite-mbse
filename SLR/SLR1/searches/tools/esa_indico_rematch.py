#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.34.2"]
# ///
"""No-network re-match of a completed ESA attachment-first census.

This utility exists so matcher/association logic can be revalidated without
re-downloading public or copyrighted attachments. It uses the frozen inventory,
event exports, attachment coverage, and extracted normalized text. Event-level
attachments are matched once as event-material subjects and are never silently
attributed to every contribution.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from concept_matcher import ConceptMatcher, atomic_write_json, sha256_file
from esa_indico_harvest_match import Attachment, concise_match, metadata_fields


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-match an existing complete ESA census without network access")
    parser.add_argument("--dictionary", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    input_dir = args.input_dir.expanduser().resolve()
    dictionary = args.dictionary.expanduser().resolve()
    matcher = ConceptMatcher.from_path(dictionary)
    # Candidate classification uses only P/E/M. Optional O/V tags are not part of
    # ESA-A1/B1 gating and can be applied separately after the union is secured.
    matcher.compiled = {key: value for key, value in matcher.compiled.items() if key in {"P", "E", "M"}}

    inventory_document = load(input_dir / "material-inventory.json")
    attachments = [Attachment(**item) for item in inventory_document["attachments"]]
    event_attachments: dict[str, list[Attachment]] = defaultdict(list)
    contribution_attachments: dict[tuple[str, str], list[Attachment]] = defaultdict(list)
    for item in attachments:
        if item.association_type == "event":
            event_attachments[item.event_id].append(item)
        elif item.contribution_id is not None:
            contribution_attachments[(item.event_id, item.contribution_id)].append(item)

    coverage = load(input_dir / "attachment-coverage.json")["results"]
    attachment_match_cache: dict[str, dict[str, Any]] = {}
    for url, result in coverage.items():
        extraction = result.get("extraction") if isinstance(result, dict) else None
        text_path = extraction.get("text_path") if isinstance(extraction, dict) else None
        if text_path and Path(text_path).is_file():
            text = Path(text_path).read_text(encoding="utf-8")
            attachment_match_cache[url] = concise_match(
                matcher.match_fields({"attachment.extracted_text": text})
            )

    subjects: list[dict[str, Any]] = []
    event_paths = sorted((input_dir / "raw" / "events").glob("*.json"), key=lambda path: int(path.stem))
    for event_path in event_paths:
        payload = load(event_path)
        event = payload["results"][0]
        event_id = str(event["id"])
        event_materials = event_attachments.get(event_id, [])
        if event_materials:
            subjects.append({
                "subject_id": f"event:{event_id}", "event_id": event_id, "contribution_id": None,
                "event": event, "contribution": None, "metadata_attachments": event_materials,
                "route_attachments": event_materials,
            })
        for contribution in event.get("contributions", []):
            contribution_id = str(contribution.get("db_id") or contribution.get("id") or "")
            own_materials = contribution_attachments.get((event_id, contribution_id), [])
            subjects.append({
                "subject_id": f"event:{event_id}:contribution:{contribution_id}", "event_id": event_id,
                "contribution_id": contribution_id, "event": event, "contribution": contribution,
                "metadata_attachments": event_materials + own_materials,
                "route_attachments": own_materials,
            })

    subject_matches: list[dict[str, Any]] = []
    for subject in subjects:
        metadata_match = concise_match(matcher.match_fields(metadata_fields(
            subject["event"], subject["contribution"], subject["metadata_attachments"]
        )))
        attachment_matches = [
            {"url_sha256": sha256_bytes(item.url.encode("utf-8")), "match": attachment_match_cache[item.url]}
            for item in subject["route_attachments"]
            if item.document_like and item.url in attachment_match_cache
        ]
        attachment_a = any(item["match"]["stream_a"] for item in attachment_matches)
        attachment_b = any(item["match"]["stream_b"] for item in attachment_matches)
        stream_a = metadata_match["stream_a"] or attachment_a
        stream_b = metadata_match["stream_b"] or attachment_b
        subject_matches.append({
            "subject_id": subject["subject_id"], "event_id": subject["event_id"],
            "contribution_id": subject["contribution_id"], "metadata_match": metadata_match,
            "attachment_matches": attachment_matches, "stream_a": stream_a, "stream_b": stream_b,
            "routes": {"joined_metadata": metadata_match["stream_b"], "attachment_text": attachment_b},
        })

    a = {item["subject_id"] for item in subject_matches if item["stream_a"]}
    b = {item["subject_id"] for item in subject_matches if item["stream_b"]}
    metadata_b = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata"]}
    attachment_b = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text"]}
    summary = {
        "status": "success" if not (a - b) else "failed_structural_invariant",
        "classification": "pilot_not_candidate_search", "screening_prohibited": True,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0, "subjects_matched": len(subject_matches),
        "stream_a_eps_explicit_tag": len(a), "stream_b_union": len(b),
        "a_intersection_b": len(a & b), "a_only_structural_error": len(a - b), "b_only": len(b - a),
        "metadata_route_b": len(metadata_b), "attachment_route_b": len(attachment_b),
        "metadata_and_attachment_route_b": len(metadata_b & attachment_b),
        "metadata_only_route_b": len(metadata_b - attachment_b),
        "attachment_only_route_b": len(attachment_b - metadata_b),
        "attachment_texts_reused": len(attachment_match_cache),
        "association_rule": "event-level attachment text is matched once as an event-material subject; contribution attachment routes contain only their own associated attachments",
        "dictionary_sha256": sha256_file(dictionary),
        "matcher_sha256": sha256_file(Path(__file__).with_name("concept_matcher.py")),
        "harvester_sha256": sha256_file(Path(__file__).with_name("esa_indico_harvest_match.py")),
        "rematcher_sha256": sha256_file(Path(__file__).resolve()),
    }
    output = {"summary": summary, "subjects": subject_matches}
    atomic_write_json(args.output_path.expanduser().resolve(), output)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "success" else 2


if __name__ == "__main__":
    raise SystemExit(main())
