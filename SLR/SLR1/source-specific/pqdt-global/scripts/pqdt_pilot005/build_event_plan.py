#!/usr/bin/env python3
"""Build the source-event plan for PQDT Global Pilot 005."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import queries

SCHEMA = "pqdt-global-pilot005-event-plan/v1"
DEFAULT_PREFLIGHT = queries.PILOT_ROOT / "searches" / "preflight.json"
DEFAULT_MAP = queries.PILOT_ROOT / "searches" / "validated-candidate-map.json"
DEFAULT_VALIDATION = queries.PILOT_ROOT / "searches" / "candidate-validation.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "event-plan.json"


def validate_inputs(
    preflight_path: Path, map_path: Path, validation_path: Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    preflight = queries.load_object(preflight_path)
    candidate_map = queries.load_object(map_path)
    validation = queries.load_object(validation_path)
    if preflight.get("schema_version") != "pqdt-global-pilot005-preflight/v1":
        raise RuntimeError("Unexpected preflight schema")
    if candidate_map.get("schema_version") != "pqdt-global-pilot005-validated-candidate-map/v1":
        raise RuntimeError("Unexpected validated candidate-map schema")
    if candidate_map.get("status") != "validated_for_value_comparison":
        raise RuntimeError("PQDT validated candidate map is not active")
    if validation.get("schema_version") != "pqdt-global-pilot005-candidate-validation/v1":
        raise RuntimeError("Unexpected candidate-validation schema")
    if validation.get("status") != "complete_two_pass_exact_browse_readback":
        raise RuntimeError("PQDT candidate validation is incomplete")
    if candidate_map.get("validated_candidate_count") != validation.get("verified_exact_label_count"):
        raise RuntimeError("PQDT exact-label validation count changed")
    map_ids = [
        item["candidate_id"]
        for item in candidate_map.get("validated_candidates", [])
    ]
    validation_ids = [
        item["candidate_id"]
        for item in validation.get("candidates", [])
        if item.get("status") == "verified_exact_browse_label"
    ]
    if map_ids != validation_ids:
        raise RuntimeError("PQDT validated candidate order changed")
    bound_validation = candidate_map.get("inputs", {}).get("candidate_validation", {})
    if bound_validation.get("sha256") != queries.file_sha256(validation_path):
        raise RuntimeError("PQDT validated map does not bind the live validation")
    pinned_adapter = preflight.get("pinned_inputs", {}).get("adapter", {})
    if pinned_adapter.get("sha256") != queries.file_sha256(queries.ADAPTER_PATH):
        raise RuntimeError("The PQDT adapter changed after predeclaration")
    return preflight, candidate_map, validation


def descriptor_expressions(candidate_map: Mapping[str, Any]) -> dict[str, str]:
    constructions = candidate_map.get("controlled_constructions")
    if not isinstance(constructions, Mapping):
        raise RuntimeError("PQDT candidate map lacks controlled constructions")
    output: dict[str, str] = {}
    for block, value in constructions.items():
        if not isinstance(value, Mapping):
            raise RuntimeError(f"Malformed controlled construction for {block}")
        expression = value.get("expression")
        if not isinstance(expression, str) or not expression:
            raise RuntimeError(f"Empty controlled construction for {block}")
        if value.get("expression_sha256") != queries.sha256_text(expression):
            raise RuntimeError(f"Controlled construction hash changed for {block}")
        output[str(block)] = expression
    return output


def build(
    preflight_path: Path, map_path: Path, validation_path: Path
) -> dict[str, Any]:
    preflight, candidate_map, validation = validate_inputs(
        preflight_path, map_path, validation_path
    )
    expressions = descriptor_expressions(candidate_map)
    ordinary, compound, augmented = queries.build_augmented_schedule_from_expressions(
        expressions
    )
    events: list[dict[str, Any]] = []
    sequence = 0
    for partition_id in queries.SCHEDULE_IDS:
        for variant, query in (
            ("free-text", queries.FREE_TEXT_SCHEDULE[partition_id]),
            ("augmented", augmented[partition_id]),
        ):
            sequence += 1
            event_id = f"{variant}-{partition_id}"
            events.append(
                {
                    "sequence": sequence,
                    "event_id": event_id,
                    "partition_id": partition_id,
                    "variant": variant,
                    "query": query,
                    "query_sha256": queries.sha256_text(query),
                    "query_characters": len(query),
                    "year_start": queries.DIAGNOSTIC_YEAR_START,
                    "year_end": queries.DIAGNOSTIC_YEAR_END,
                    "language": queries.LANGUAGE,
                    "output": f"events/{event_id}.json",
                    "purpose": (
                        "Fresh strict free-text baseline for descriptor comparison."
                        if variant == "free-text"
                        else "Fresh strict free-text-plus-descriptor union for descriptor comparison."
                    ),
                }
            )

    return {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "predeclared",
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "objective": (
            "Compare the complete current free-text schedule with the same schedule in "
            "which P, M_H, M_B, and R are unions of free text and validated exact PQDT labels."
        ),
        "inputs": {
            "preflight": {
                "path": str(preflight_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(preflight_path),
            },
            "validated_candidate_map": {
                "path": str(map_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(map_path),
                "validated_candidate_count": candidate_map["validated_candidate_count"],
            },
            "candidate_validation": {
                "path": str(validation_path.relative_to(queries.PILOT_ROOT)),
                "sha256": queries.file_sha256(validation_path),
                "verified_exact_label_count": validation["verified_exact_label_count"],
                "assigned_but_absent_count": validation["assigned_but_absent_count"],
            },
        },
        "adapter": {
            "path": str(queries.ADAPTER_PATH),
            "sha256": queries.file_sha256(queries.ADAPTER_PATH),
            "version": "5",
        },
        "local_union_bridge": {
            "path": str(queries.UNION_BRIDGE_PATH.relative_to(queries.SLR1_ROOT)),
            "sha256": queries.file_sha256(queries.UNION_BRIDGE_PATH),
            "scope": (
                "Allow several raw PSUB or IF clauses when no typed Subject or Index "
                "term restriction is requested. Preserve every source and output check."
            ),
        },
        "controls": preflight["source_controls"],
        "translation": {
            "free_text_schedule": queries.FREE_TEXT_SCHEDULE,
            "descriptor_blocks": expressions,
            "augmented_ordinary_blocks": ordinary,
            "augmented_compound_blocks": compound,
            "augmented_schedule": augmented,
            "combination_rule": "OR each exact descriptor construction with its complete free-text block.",
            "free_text_remains_mandatory": True,
            "major_topic": False,
            "explosion": None,
        },
        "event_count": len(events),
        "events": events,
        "comparison_rule": (
            "For every partition, require complete two-pass capture, require the augmented "
            "IDs to retain every adjacent free-text ID, and review every augmented-only record."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--candidate-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--candidate-validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build(
        args.preflight.expanduser().resolve(),
        args.candidate_map.expanduser().resolve(),
        args.candidate_validation.expanduser().resolve(),
    )
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("PQDT Pilot 005 event plan differs")
        return 0
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
