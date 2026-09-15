#!/usr/bin/env python3

"""Build non-mergeable ATAI Pilot 005 artifacts from adapter v4 live checks."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

SOURCE = "Advanced Technologies & Aerospace Index"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_abstract(value: str) -> str:
    return value[:-5] if value.endswith(" More") else value


def result_map(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(record["paperId"]): record for record in result["results"]}


def validate_live_result(
    result: dict[str, Any], *, partition: str, expected_total: int
) -> None:
    metadata = result.get("output_metadata", {})
    prisma = metadata.get("prisma_search_run", {})
    adapter = prisma.get("adapter", {})
    if (
        result.get("source") != SOURCE
        or result.get("total") != expected_total
        or len(result.get("results", [])) != expected_total
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or prisma.get("completion_status") != "complete"
        or adapter.get("adapter_id") != "search_proquest_aerospace"
        or adapter.get("adapter_version") != "4"
    ):
        raise RuntimeError(f"{partition} is not a complete adapter v4 result.")
    if any(record.get("abstract", "").endswith(" More") for record in result["results"]):
        raise RuntimeError(f"{partition} retained a terminal More token.")


def compare_historical_abstracts(
    partition: str,
    historical_one: dict[str, Any],
    historical_two: dict[str, Any],
    current: dict[str, Any],
) -> dict[str, Any]:
    one = result_map(historical_one)
    two = result_map(historical_two)
    live = result_map(current)
    if list(one) != list(two) or list(one) != list(live):
        raise RuntimeError(f"{partition} stable IDs changed across evidence sets.")
    differences: list[dict[str, Any]] = []
    for paper_id in one:
        first = one[paper_id]
        second = two[paper_id]
        latest = live[paper_id]
        changed_fields = [
            field
            for field in set(first) | set(second)
            if first.get(field) != second.get(field)
        ]
        if changed_fields and changed_fields != ["abstract"]:
            raise RuntimeError(
                f"{partition} historical record {paper_id} changed fields {changed_fields!r}."
            )
        first_abstract = str(first.get("abstract", ""))
        second_abstract = str(second.get("abstract", ""))
        canonical_first = canonical_abstract(first_abstract)
        canonical_second = canonical_abstract(second_abstract)
        current_abstract = str(latest.get("abstract", ""))
        if canonical_first != canonical_second or canonical_first != current_abstract:
            raise RuntimeError(
                f"{partition} abstract content differs beyond terminal More for {paper_id}."
            )
        if changed_fields:
            differences.append(
                {
                    "paper_id": paper_id,
                    "title": latest.get("title"),
                    "pass_1_had_terminal_more": first_abstract.endswith(" More"),
                    "pass_2_had_terminal_more": second_abstract.endswith(" More"),
                    "canonical_abstract_characters": len(current_abstract),
                    "fresh_v4_exactly_matches_canonical_text": True,
                }
            )
    return {
        "partition": partition,
        "record_count": len(live),
        "historical_records_with_only_terminal_more_instability": len(differences),
        "differences": differences,
        "all_historical_abstracts_match_fresh_v4_after_canonicalization": True,
        "fresh_abstracts_ending_in_ellipsis": [
            paper_id
            for paper_id, record in live.items()
            if str(record.get("abstract", "")).endswith(("...", "…"))
        ],
    }


def cleanup_projection(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_count = before.get("page_count")
    after_count = after.get("page_count")
    if not isinstance(before_count, int) or before_count != after_count:
        raise RuntimeError("Owned-page cleanup did not restore the browser page count.")
    return {
        "page_count_before": before_count,
        "page_count_after": after_count,
        "page_count_restored": True,
    }


def mark_pilot(
    source_result: dict[str, Any], *, partition: str, source_sha256: str
) -> dict[str, Any]:
    result = copy.deepcopy(source_result)
    result["do_not_merge"] = True
    metadata = result.setdefault("output_metadata", {})
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["non_mergeable_reason"] = (
        "ATAI Pilot 005 adapter-repair validation. This is not a final search."
    )
    result["pilot_cell"] = {
        "pilot_id": "005",
        "event_kind": "pilot",
        "partition_id": partition,
        "adapter_version": "4",
        "source_artifact_sha256_before_pilot_marking": source_sha256,
        "diagnostic_window": {
            "start": "2011-01-01",
            "end": "2026-08-29",
            "basis": "publication",
        },
        "status": "strict_two_full_record_passes_succeeded",
        "pilot_only": True,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a3", type=Path, required=True)
    parser.add_argument("--b1", type=Path, required=True)
    parser.add_argument("--a3-before", type=Path, required=True)
    parser.add_argument("--a3-after", type=Path, required=True)
    parser.add_argument("--b1-before", type=Path, required=True)
    parser.add_argument("--b1-after", type=Path, required=True)
    parser.add_argument("--historical-a3-pass1", type=Path, required=True)
    parser.add_argument("--historical-a3-pass2", type=Path, required=True)
    parser.add_argument("--historical-b1-pass1", type=Path, required=True)
    parser.add_argument("--historical-b1-pass2", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    a3 = load(args.a3)
    b1 = load(args.b1)
    validate_live_result(a3, partition="A3", expected_total=1)
    validate_live_result(b1, partition="B1", expected_total=19)
    a3_audit = compare_historical_abstracts(
        "A3",
        load(args.historical_a3_pass1),
        load(args.historical_a3_pass2),
        a3,
    )
    b1_audit = compare_historical_abstracts(
        "B1",
        load(args.historical_b1_pass1),
        load(args.historical_b1_pass2),
        b1,
    )
    if a3_audit["historical_records_with_only_terminal_more_instability"] != 1:
        raise RuntimeError("A3 did not reproduce its one terminal-More difference.")
    if b1_audit["historical_records_with_only_terminal_more_instability"] != 7:
        raise RuntimeError("B1 did not reproduce its seven terminal-More differences.")
    if a3_audit["fresh_abstracts_ending_in_ellipsis"] or b1_audit["fresh_abstracts_ending_in_ellipsis"]:
        raise RuntimeError("A fresh canonical abstract ended in an ellipsis.")

    a3_cleanup = cleanup_projection(load(args.a3_before), load(args.a3_after))
    b1_cleanup = cleanup_projection(load(args.b1_before), load(args.b1_after))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "A3.strict-v4.json").write_text(
        json.dumps(
            mark_pilot(a3, partition="A3", source_sha256=digest(args.a3)),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    (args.output_dir / "B1.strict-v4.json").write_text(
        json.dumps(
            mark_pilot(b1, partition="B1", source_sha256=digest(args.b1)),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    audit = {
        "schema_version": "atai-adapter-v4-repair-validation/v1",
        "source": SOURCE,
        "pilot": "005",
        "status": "passed",
        "do_not_merge": True,
        "adapter": {
            "id": "search_proquest_aerospace",
            "version": "4",
            "repairs": [
                "canonical terminal abstract More handling",
                "exact restore-session overlay dismissal on the owned page",
                "inventory-proven target identity for verified cleanup",
            ],
        },
        "strict_runs": {
            "A3": {
                "total": 1,
                "stable_complete_passes": 2,
                "artifact": "A3.strict-v4.json",
                "cleanup": a3_cleanup,
            },
            "B1": {
                "total": 19,
                "stable_complete_passes": 2,
                "artifact": "B1.strict-v4.json",
                "cleanup": b1_cleanup,
            },
        },
        "abstract_audit": {
            "A3": a3_audit,
            "B1": b1_audit,
            "terminal_more_is_truncation": False,
            "finding": (
                "Every historical abstract matched the fresh adapter v4 text exactly after "
                "removing only terminal standalone More. No fresh canonical abstract ended "
                "in an ellipsis. No truncation was observed."
            ),
        },
        "restore_session_overlay": {
            "historical_live_observation": "The exact #restoresession_confirm modal blocked ATAI database submission before repair.",
            "repair": "Verify the exact dialog and click its exact Dismiss action before owned-page source actions.",
            "cookie_consent_unchanged": True,
        },
        "cleanup": {
            "A3_page_count_restored": True,
            "B1_page_count_restored": True,
            "shared_browser_closed": False,
            "owned_page_only": True,
        },
        "limitations": [
            "This diagnostic uses the 2026-08-29 pilot window. It is not the final evidence cutoff.",
            "Historical failure artifacts remain immutable evidence of adapter v3 behavior.",
        ],
    }
    (args.output_dir / "adapter-repair-validation.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
