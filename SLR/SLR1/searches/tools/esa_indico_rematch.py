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
    # Candidate classification uses P/E/M plus relation-free complete G/C1 artifacts.
    # R/T are tags; optional O/V terms do not participate in ESA-A1/B1/BG1/BC1 gating.
    matcher.compiled = {
        key: value for key, value in matcher.compiled.items() if key in {"P", "E", "M", "G", "R", "T"}
    }

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
        attachment_b_core = any(item["match"]["stream_b_core"] for item in attachment_matches)
        attachment_b_g = any(item["match"]["stream_b_g"] for item in attachment_matches)
        attachment_b_c1 = any(item["match"]["stream_b_c1"] for item in attachment_matches)
        attachment_b_genericity = any(item["match"]["stream_b_genericity"] for item in attachment_matches)
        attachment_b_genericity_relation = any(
            item["match"]["stream_b_genericity_relation_qualified"] for item in attachment_matches
        )
        attachment_tailoring = any(item["match"]["stream_b_tailoring_tag"] for item in attachment_matches)
        attachment_g_eps = any(item["match"]["g_eps_explicit"] for item in attachment_matches)
        attachment_c1_eps = any(item["match"]["c1_eps_explicit"] for item in attachment_matches)
        attachment_genericity_eps = any(item["match"]["genericity_eps_explicit"] for item in attachment_matches)
        stream_a = metadata_match["stream_a"] or attachment_a
        stream_b_core = metadata_match["stream_b_core"] or attachment_b_core
        stream_b_g = metadata_match["stream_b_g"] or attachment_b_g
        stream_b_c1 = metadata_match["stream_b_c1"] or attachment_b_c1
        stream_b_genericity = stream_b_g or stream_b_c1
        stream_b_genericity_relation = (
            metadata_match["stream_b_genericity_relation_qualified"] or attachment_b_genericity_relation
        )
        stream_b = stream_b_core or stream_b_genericity
        g_eps_explicit = metadata_match["g_eps_explicit"] or attachment_g_eps
        c1_eps_explicit = metadata_match["c1_eps_explicit"] or attachment_c1_eps
        genericity_eps_explicit = metadata_match["genericity_eps_explicit"] or attachment_genericity_eps
        tailoring_tag = metadata_match["stream_b_tailoring_tag"] or attachment_tailoring
        subject_matches.append({
            "subject_id": subject["subject_id"], "event_id": subject["event_id"],
            "contribution_id": subject["contribution_id"], "metadata_match": metadata_match,
            "attachment_matches": attachment_matches, "stream_a": stream_a, "stream_b": stream_b,
            "stream_b_core": stream_b_core, "stream_b_g": stream_b_g, "stream_b_c1": stream_b_c1,
            "stream_b_genericity": stream_b_genericity,
            "stream_b_genericity_relation_qualified": stream_b_genericity_relation,
            "stream_b_tailoring_tag": tailoring_tag,
            "g_eps_explicit": g_eps_explicit, "c1_eps_explicit": c1_eps_explicit,
            "genericity_eps_explicit": genericity_eps_explicit,
            "routes": {
                "joined_metadata": metadata_match["stream_b"], "attachment_text": attachment_b,
                "joined_metadata_core": metadata_match["stream_b_core"], "attachment_text_core": attachment_b_core,
                "joined_metadata_g": metadata_match["stream_b_g"], "attachment_text_g": attachment_b_g,
                "joined_metadata_c1": metadata_match["stream_b_c1"], "attachment_text_c1": attachment_b_c1,
                "joined_metadata_genericity": metadata_match["stream_b_genericity"],
                "attachment_text_genericity": attachment_b_genericity,
                "joined_metadata_genericity_relation_qualified": metadata_match[
                    "stream_b_genericity_relation_qualified"
                ],
                "attachment_text_genericity_relation_qualified": attachment_b_genericity_relation,
                "joined_metadata_tailoring_tag": metadata_match["stream_b_tailoring_tag"],
                "attachment_text_tailoring_tag": attachment_tailoring,
            },
        })

    a = {item["subject_id"] for item in subject_matches if item["stream_a"]}
    b = {item["subject_id"] for item in subject_matches if item["stream_b"]}
    core_b = {item["subject_id"] for item in subject_matches if item["stream_b_core"]}
    g_eps = {item["subject_id"] for item in subject_matches if item["g_eps_explicit"]}
    c1_eps = {item["subject_id"] for item in subject_matches if item["c1_eps_explicit"]}
    genericity_eps = {item["subject_id"] for item in subject_matches if item["genericity_eps_explicit"]}
    g_b = {item["subject_id"] for item in subject_matches if item["stream_b_g"]}
    c1_b = {item["subject_id"] for item in subject_matches if item["stream_b_c1"]}
    genericity_b = {item["subject_id"] for item in subject_matches if item["stream_b_genericity"]}
    relation_qualified_g = {
        item["subject_id"] for item in subject_matches if item["stream_b_genericity_relation_qualified"]
    }
    tailoring = {item["subject_id"] for item in subject_matches if item["stream_b_tailoring_tag"]}
    metadata_b = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata"]}
    attachment_b = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text"]}
    metadata_g = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata_g"]}
    attachment_g = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text_g"]}
    metadata_c1 = {item["subject_id"] for item in subject_matches if item["routes"]["joined_metadata_c1"]}
    attachment_c1 = {item["subject_id"] for item in subject_matches if item["routes"]["attachment_text_c1"]}
    summary = {
        "status": "success" if not (a - b) else "failed_structural_invariant",
        "classification": "pilot_not_candidate_search", "screening_prohibited": True,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0, "subjects_matched": len(subject_matches),
        "stream_a_eps_explicit_tag": len(a), "stream_b_union": len(b),
        "g_eps_explicit_tag": len(g_eps), "c1_eps_explicit_tag": len(c1_eps),
        "genericity_eps_explicit_tag": len(genericity_eps),
        "stream_b_core": len(core_b), "stream_b_g": len(g_b), "stream_b_c1": len(c1_b),
        "stream_b_genericity": len(genericity_b),
        "stream_b_genericity_relation_qualified": len(relation_qualified_g),
        "stream_b_tailoring_tag": len(tailoring),
        "core_intersection_g": len(core_b & g_b), "core_intersection_c1": len(core_b & c1_b),
        "g_intersection_c1": len(g_b & c1_b),
        "core_intersection_genericity": len(core_b & genericity_b),
        "core_only": len(core_b - genericity_b),
        "g_only_vs_core_c1": len(g_b - core_b - c1_b),
        "c1_only_vs_core_g": len(c1_b - core_b - g_b),
        "genericity_only": len(genericity_b - core_b),
        "a_intersection_b": len(a & b), "a_only_structural_error": len(a - b), "b_only": len(b - a),
        "metadata_route_b": len(metadata_b), "attachment_route_b": len(attachment_b),
        "metadata_and_attachment_route_b": len(metadata_b & attachment_b),
        "metadata_only_route_b": len(metadata_b - attachment_b),
        "attachment_only_route_b": len(attachment_b - metadata_b),
        "metadata_route_g": len(metadata_g), "attachment_route_g": len(attachment_g),
        "metadata_and_attachment_route_g": len(metadata_g & attachment_g),
        "metadata_route_c1": len(metadata_c1), "attachment_route_c1": len(attachment_c1),
        "metadata_and_attachment_route_c1": len(metadata_c1 & attachment_c1),
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
