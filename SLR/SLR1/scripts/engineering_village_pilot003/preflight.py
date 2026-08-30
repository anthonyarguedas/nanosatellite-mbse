#!/usr/bin/env python3
"""Build and verify the literal paired Engineering Village Pilot 003 plan.

This module only renders and validates source-native expressions.  It never
opens a browser or submits a query.  The query definitions remain centralized
in ``scripts/pilot_schedule/queries.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SLR1_ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = SLR1_ROOT / "source-specific" / "compendex" / "pilots" / "003"
DEFAULT_OUTPUT = PILOT_DIR / "searches" / "preflight.json"
SCHEDULE_DIR = SLR1_ROOT / "scripts" / "pilot_schedule"
if str(SCHEDULE_DIR) not in sys.path:
    sys.path.insert(0, str(SCHEDULE_DIR))

from queries import CONCEPTS, MAIN_FACTORS, RENDERERS, partition_query  # noqa: E402

SOURCE_ID = "engineering_village_compendex_inspec"
SCHEDULE_IDS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
LANGUAGE_CLAUSE = "(English WN LA)"
EXPECTED_PAIR_COUNTS = {
    "A1": 0,
    "A2": 0,
    "A3": 0,
    "B1": 0,
    "B2": 0,
    "BG1": 16,
    "BG2": 16,
    "BC1": 36,
    "BT2": 224,
}
EXPECTED_CONCEPT_COUNTS = {
    "P": (26, 0),
    "E_H": (38, 0),
    "E_F": (37, 0),
    "M_H": (54, 0),
    "M_B": (31, 0),
    "R": (55, 0),
    "G_model": (14, 16),
    "G_structure": (8, 16),
    "C1": (26, 36),
    "T2": (0, 224),
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def raw_query(partition_id: str) -> str:
    """Return the unmodified Expert expression plus the required LA clause."""
    return f"{partition_query(SOURCE_ID, partition_id)} AND {LANGUAGE_CLAUSE}"


def _factor_summary(partition_id: str) -> list[dict[str, Any]]:
    renderer = RENDERERS[SOURCE_ID]
    summaries = []
    for names in MAIN_FACTORS[partition_id]:
        alternatives = renderer.alternatives(names)
        summaries.append(
            {
                "concepts": list(names),
                "alternative_count": len(alternatives),
                "literal_count": sum(len(CONCEPTS[name].literals) for name in names),
                "near_pair_count": sum(len(CONCEPTS[name].pairs) for name in names),
            }
        )
    return summaries


def validate_partition(partition_id: str) -> dict[str, Any]:
    """Fail closed if a planned partition differs from the central schedule."""
    if partition_id not in MAIN_FACTORS:
        raise ValueError(f"Unknown Pilot 003 partition: {partition_id}")
    if tuple(MAIN_FACTORS) != SCHEDULE_IDS:
        raise ValueError("The direct-query schedule is not the required nine-entry order")

    renderer = RENDERERS[SOURCE_ID]
    semantic = partition_query(SOURCE_ID, partition_id)
    query = raw_query(partition_id)
    if semantic != renderer.partition(partition_id):
        raise ValueError(f"{partition_id}: renderer output differs from the central schedule")
    if not query.endswith(f" AND {LANGUAGE_CLAUSE}") or query.count(LANGUAGE_CLAUSE) != 1:
        raise ValueError(f"{partition_id}: raw English LA clause is not exact")
    if "*" in query or "?" in query:
        raise ValueError(f"{partition_id}: unaccepted wildcard entered the expression")
    if query.count("NEAR/5") != EXPECTED_PAIR_COUNTS[partition_id]:
        raise ValueError(f"{partition_id}: NEAR/5 pair count changed")

    factor_summaries = _factor_summary(partition_id)
    for names in MAIN_FACTORS[partition_id]:
        for atom in renderer.alternatives(names):
            if atom not in semantic:
                raise ValueError(f"{partition_id}: missing scheduled alternative {atom!r}")
    for names in MAIN_FACTORS[partition_id]:
        for name in names:
            for left, right in CONCEPTS[name].pairs:
                atom = renderer.pair_atom(left, right)
                if atom not in semantic:
                    raise ValueError(f"{partition_id}: missing NEAR/5 pair {left!r}/{right!r}")

    return {
        "partition_id": partition_id,
        "semantic_query": semantic,
        "raw_query": query,
        "semantic_query_sha256": sha256_text(semantic),
        "raw_query_sha256": sha256_text(query),
        "semantic_query_characters": len(semantic),
        "raw_query_characters": len(query),
        "factor_summary": factor_summaries,
        "near_pair_count": query.count("NEAR/5"),
        "wildcard_characters_present": False,
        "validation": "passed_before_source_use",
    }


def build_payload() -> dict[str, Any]:
    concept_counts = {
        name: {"literals": len(CONCEPTS[name].literals), "near_pairs": len(CONCEPTS[name].pairs)}
        for name in EXPECTED_CONCEPT_COUNTS
    }
    expected_counts = {
        name: {"literals": literals, "near_pairs": pairs}
        for name, (literals, pairs) in EXPECTED_CONCEPT_COUNTS.items()
    }
    if concept_counts != expected_counts:
        raise ValueError("The central concept membership counts changed")
    return {
        "schema_version": "slr1-engineering-village-pilot003-preflight/v1",
        "pilot": "003",
        "event_model": "one paired Compendex+Inspec Engineering Village event per direct-query partition",
        "source_renderer": SOURCE_ID,
        "partition_order": list(SCHEDULE_IDS),
        "concept_membership_counts": concept_counts,
        "controls_required_for_every_event": {
            "search_mode": "Expert ALL",
            "published_year_bounds": {"start": 2011, "end": 2026, "source_precision": "year"},
            "language_raw_clause": LANGUAGE_CLAUSE,
            "autostemming": "off",
            "sort": "Date (Oldest)",
            "document_type_filter": "not_applied",
            "open_access_filter": "not_applied",
            "controlled_vocabulary_supplement": "not_requested",
            "wildcard": "not_used_or_accepted",
        },
        "partitions": [validate_partition(partition_id) for partition_id in SCHEDULE_IDS],
    }


def write_no_clobber(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate an existing deterministic preflight receipt without rewriting it.",
    )
    args = parser.parse_args()
    payload = build_payload()
    output = args.output_path.expanduser()
    if args.check:
        existing = json.loads(output.read_text(encoding="utf-8"))
        if existing != payload:
            raise SystemExit(f"Preflight receipt differs from the central schedule: {output}")
        print(json.dumps({"status": "ok", "partitions": list(SCHEDULE_IDS), "path": str(output)}, indent=2))
        return 0
    write_no_clobber(output, payload)
    print(json.dumps({"status": "saved", "partitions": list(SCHEDULE_IDS), "path": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
