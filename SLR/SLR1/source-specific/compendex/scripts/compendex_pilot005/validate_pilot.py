#!/usr/bin/env python3
"""Validate the complete Compendex Pilot 005 wildcard bundle."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

SLR1 = Path(__file__).resolve().parents[4]
REPOSITORY_ROOT = SLR1.parents[1]
PILOT_ROOT = SLR1 / "source-specific/compendex/pilots/005"
SEARCHES = PILOT_ROOT / "searches"
GUIDELINE = SLR1 / "source-specific/compendex/source-specific-guidelines.md"
OUTPUT = SEARCHES / "validation-report.json"
EXPECTED_IDS = {
    "compendex": [
        "20142217768546",
        "20171603573466",
        "20241215772241",
        "20232514262795",
        "20251518218533",
        "20263421355398",
    ],
    "inspec": ["16661315", "23201028", "26519151"],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_links(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        local = target.split("#", 1)[0]
        check((path.parent / local).exists(), f"Missing Markdown link from {path}: {target}")


def main() -> int:
    required = {
        "plan": SEARCHES / "event-plan.json",
        "receipt": SEARCHES / "run-receipt.json",
        "literal": SEARCHES / "cells/literal-A1.json",
        "wildcard": SEARCHES / "cells/wildcard-A1.json",
        "assessment": SEARCHES / "assessment.json",
        "approval": SEARCHES / "source-translation-approval.json",
        "adapter_validation": SEARCHES / "adapter-v16-screenshot-validation.json",
        "pilot": PILOT_ROOT / "pilot.md",
        "guideline": GUIDELINE,
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    check(not missing, f"Pilot 005 lacks required files: {missing!r}")
    check(
        not list(SEARCHES.rglob("*.NON_MERGEABLE_FAILURE.json")),
        "Pilot 005 retains a source failure",
    )

    subprocess.run(
        ["git", "cat-file", "-e", f"{queries.PROTOCOL_COMMIT}^{{commit}}"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(Path(__file__).parent),
            "-p",
            "test_*.py",
        ],
        cwd=REPOSITORY_ROOT,
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)},
        check=True,
        capture_output=True,
    )

    plan = load(required["plan"])
    receipt = load(required["receipt"])
    assessment = load(required["assessment"])
    approval = load(required["approval"])
    adapter_validation = load(required["adapter_validation"])
    check(plan.get("schema_version") == "engineering-village-wildcard-pilot-plan/v1", "Plan schema changed")
    check(plan.get("protocol_commit") == queries.PROTOCOL_COMMIT, "Plan protocol commit changed")
    check(plan.get("do_not_merge") is True, "Plan is not diagnostic")
    check(plan["comparison"]["character_reduction"] == 130, "Candidate reduction changed")
    check(plan["comparison"]["wildcard_count"] == 3, "Candidate wildcard count changed")
    check(plan["comparison"]["replaced_literal_count"] == 8, "Literal coverage changed")
    check(plan["term_snapshot"]["sha256"] == queries.TERM_SNAPSHOT_SHA256, "Term snapshot changed")
    for relative, expected_hash in plan["source_affecting_scripts"].items():
        path = REPOSITORY_ROOT / relative
        check(path.is_file() and digest_file(path) == expected_hash, f"Source script changed: {relative}")

    check(receipt.get("status") == "complete", "Run receipt is incomplete")
    check(receipt.get("do_not_merge") is True, "Run receipt is not diagnostic")
    check(receipt.get("predeclared_event_count") == 2, "Event count changed")
    check(receipt.get("completed_event_count") == 2, "Not every event completed")
    check(receipt.get("successful_event_count") == 2, "A source event failed")
    check(plan["created_at_utc"] < receipt["started_at_utc"], "Plan was not created before source use")

    events = plan["events"]
    check([event["event_id"] for event in events] == list(queries.EVENT_QUERIES), "Event order changed")
    artifacts: dict[str, dict[str, Any]] = {}
    outcome_by_id = {item["event_id"]: item for item in receipt["outcomes"]}
    for event in events:
        event_id = event["event_id"]
        query = queries.EVENT_QUERIES[event_id]
        check(event["query"] == query, f"Plan query changed for {event_id}")
        check(event["query_sha256"] == hashlib.sha256(query.encode()).hexdigest(), f"Query hash changed for {event_id}")
        check(event["query_characters"] == len(query), f"Query length changed for {event_id}")
        path = PILOT_ROOT / "searches" / event["output"]
        artifact = load(path)
        artifacts[event_id] = artifact
        outcome = outcome_by_id[event_id]
        check(outcome["status"] == "strict_two_pass_complete", f"Outcome failed for {event_id}")
        check(outcome["output_sha256"] == digest_file(path), f"Outcome hash changed for {event_id}")
        check(artifact.get("do_not_merge") is True, f"{event_id} is mergeable")
        check(artifact.get("requested_query") == query, f"Requested query changed for {event_id}")
        check(artifact.get("total") == 9 and len(artifact.get("results", [])) == 9, f"Total changed for {event_id}")
        metadata = artifact.get("output_metadata", {})
        check(metadata.get("status") == "success", f"Adapter status changed for {event_id}")
        check(metadata.get("merge_eligible") is False, f"Adapter artifact is merge eligible: {event_id}")
        check(metadata.get("pilot_only") is True, f"Adapter artifact lacks pilot marking: {event_id}")
        prisma = metadata.get("prisma_search_run", {})
        check(prisma.get("completion_status") == "complete", f"PRISMA completion changed for {event_id}")
        check(prisma.get("strategy", {}).get("requested_query") == query, f"Source request changed for {event_id}")
        check(prisma.get("strategy", {}).get("executed_query_provenance") == "source_observed", f"Query echo changed for {event_id}")
        check(prisma.get("strategy", {}).get("limits", {}).get("published", {}).get("value") == {"start": "2011", "end": "2026"}, f"Published readback changed for {event_id}")
        check(prisma.get("strategy", {}).get("sort", {}).get("value", {}).get("label") == "Date (Oldest)", f"Sort changed for {event_id}")
        check(prisma.get("adapter", {}).get("adapter_version") == "15", f"Adapter version changed for {event_id}")
        check(prisma.get("adapter", {}).get("script_sha256") == plan["adapter"]["implementation_sha256"], f"Adapter hash changed for {event_id}")

        context = artifact.get("pilot_context", {})
        check(context.get("status") == "strict_two_pass_complete", f"Pilot status changed for {event_id}")
        check(context.get("query_sha256") == event["query_sha256"], f"Pilot query hash changed for {event_id}")
        check(context.get("paired_source_total") == 9, f"Paired total changed for {event_id}")
        check(context.get("controls") == {
            "database_selection": ["compendex", "inspec"],
            "database_mask": "3",
            "Published": {"start": 2011, "end": 2026},
            "Updates": "inactive",
            "language": "English WN LA",
            "autostemming": "off",
            "sort": "Date (Oldest)",
            "page_size": 25,
            "document_type": "not_applied",
            "open_access": "not_applied",
            "controlled_vocabulary": "not_applied",
        }, f"Pilot controls changed for {event_id}")
        strict = context.get("strict_complete_comparison_receipt", {})
        counts = strict.get("stable_counts", {})
        check(strict.get("complete_pass_count") == 2, f"Strict pass count changed for {event_id}")
        check(strict.get("sequence_match") is True, f"Strict sequence changed for {event_id}")
        check(strict.get("first_pass_sequence_sha256") == strict.get("second_pass_sequence_sha256"), f"Strict passes differ for {event_id}")
        check(counts.get("portal_total") == 9, f"Strict total changed for {event_id}")
        check(counts.get("source_export_ids_seen_by_database") == {"compendex": 6, "inspec": 3}, f"Strict database counts changed for {event_id}")
        check(counts.get("native_ris_batch_count") == 1 and counts.get("native_ris_record_counts") == [9], f"Native RIS receipt changed for {event_id}")
        for database, expected_ids in EXPECTED_IDS.items():
            projection = context["projections"][database]
            check(projection["source_total"] == len(expected_ids), f"{database} total changed for {event_id}")
            check(projection["ordered_stable_accessions"] == expected_ids, f"{database} IDs changed for {event_id}")

    literal_context = artifacts["literal-A1"]["pilot_context"]
    wildcard_context = artifacts["wildcard-A1"]["pilot_context"]
    for database in EXPECTED_IDS:
        check(
            literal_context["projections"][database]["ordered_stable_accessions"]
            == wildcard_context["projections"][database]["ordered_stable_accessions"],
            f"The complete {database} sets are no longer equal",
        )
    check(
        literal_context["strict_complete_comparison_receipt"]["native_ris_batch_hash_sequence_sha256"]
        == wildcard_context["strict_complete_comparison_receipt"]["native_ris_batch_hash_sequence_sha256"],
        "Native RIS batch sequences changed between equal result sets",
    )

    check(assessment.get("status") == "complete", "Assessment is incomplete")
    check(assessment.get("do_not_merge") is True, "Assessment is not diagnostic")
    check(assessment.get("decision") == "accept_three_family_wildcard_for_compendex_A1_only", "Assessment decision changed")
    check(assessment.get("accepted_for_compendex_A1") is True, "A1 acceptance changed")
    check(
        assessment.get("accepted_for_other_compendex_partitions") is False,
        "The predeclared assessment boundary changed",
    )
    check(assessment["candidate"]["character_reduction"] == 130, "Assessment reduction changed")
    for database, expected_ids in EXPECTED_IDS.items():
        comparison = assessment["database_comparisons"][database]
        check(comparison["literal_accessions"] == expected_ids, f"Assessment literal IDs changed for {database}")
        check(comparison["wildcard_accessions"] == expected_ids, f"Assessment wildcard IDs changed for {database}")
        check(comparison["sets_equal"] is True, f"Assessment sets differ for {database}")
        check(comparison["wildcard_only_accessions"] == [], f"Assessment gained {database} wildcard-only IDs")

    check(
        approval.get("schema_version")
        == "compendex-wildcard-source-translation-approval/v1",
        "Approval schema changed",
    )
    check(approval.get("status") == "approved", "Wildcard approval changed")
    check(approval.get("do_not_merge") is True, "Approval is not diagnostic")
    check(
        approval.get("decision")
        == "approve_three_family_population_wildcards_for_all_schedule_entries",
        "All-schedule approval changed",
    )
    check(
        approval.get("approved_schedule_entries")
        == ["A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"],
        "Approved schedule scope changed",
    )
    check(
        approval.get("basis", {}).get("pilot_assessment_sha256")
        == digest_file(required["assessment"]),
        "Approval lost its pilot assessment binding",
    )
    check(
        [item.get("wildcard_atom") for item in approval["approved_population_replacements"]]
        == ["(CubeSat* WN ALL)", "(nanosat* WN ALL)", "(SmallSat* WN ALL)"],
        "Approved wildcard atoms changed",
    )

    check(
        adapter_validation.get("schema_version")
        == "engineering-village-adapter-screenshot-validation/v1",
        "Adapter validation schema changed",
    )
    check(adapter_validation.get("status") == "passed", "Adapter validation failed")
    check(adapter_validation.get("do_not_merge") is True, "Adapter validation is mergeable")
    check(adapter_validation.get("adapter", {}).get("version") == "16", "Adapter validation version changed")
    check(
        adapter_validation.get("offline_validation", {}).get("tests_passed") == 7,
        "Focused adapter test result changed",
    )
    live = adapter_validation.get("live_validation", {})
    check(len(live.get("events", [])) == 2, "Adapter live check count changed")
    for event in live["events"]:
        screenshots = event.get("screenshots", {})
        check(screenshots.get("automatic") is True, "Screenshot automation changed")
        check(screenshots.get("opt_out_available") is False, "Screenshot opt-out appeared")
        check(
            screenshots.get("hashes_and_dimensions_matched_json_receipt") is True,
            "Screenshot receipt validation changed",
        )
    check(
        live["events"][1].get("marker_gated_json_csv_pair_usable") is True,
        "Strict screenshot check lost its usable result pair",
    )
    check(
        live.get("temporary_live_outputs_removed_after_validation") is True,
        "Temporary screenshot output cleanup is incomplete",
    )

    guideline = GUIDELINE.read_text(encoding="utf-8")
    pilot = required["pilot"].read_text(encoding="utf-8")
    for text, description in (
        ("Pilot 005", "pilot checklist"),
        ("(CubeSat* WN ALL)", "CubeSat wildcard"),
        ("(nanosat* WN ALL)", "nanosat wildcard"),
        ("(SmallSat* WN ALL)", "SmallSat wildcard"),
        ("Approved for every schedule entry", "all-schedule approval"),
        ("wildcard-compressed `F(P)` block in every row", "schedule rendering rule"),
        ("source-translation-approval.json", "approval provenance"),
        ("Adapter v16", "automatic screenshot adapter"),
        ("<query-id>.search-page.png", "search screenshot"),
        ("<query-id>.results-page.png", "results screenshot"),
        ("adapter-v16-screenshot-validation.json", "screenshot validation provenance"),
        ("equal complete six-accession Compendex A1 sets", "stable-ID conclusion"),
    ):
        check(text in guideline, f"Guideline lacks {description}")
    check("## Complete set comparison" in pilot, "Pilot report lacks set comparison")
    check("all nine Compendex schedule entries" in pilot, "Pilot report lacks final approval")
    check("## Adapter v16 screenshot validation" in pilot, "Pilot report lacks adapter validation")
    validate_links(required["pilot"])

    final_files = [
        path.name
        for path in (SLR1 / "source-specific/compendex/final-searches").iterdir()
        if path.name != ".gitkeep"
    ]
    check(not final_files, "Pilot 005 created a final-search artifact")

    private_markers = ("/Users/", "SEARCHID", "docidlist", "handlelist", "sessionid", "cookie=")
    for path in PILOT_ROOT.rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        for marker in private_markers:
            check(marker.casefold() not in text.casefold(), f"{path.name} retained {marker}")

    report = {
        "schema_version": "engineering-village-wildcard-pilot-validation/v1",
        "source": "Compendex with retained paired Inspec projection",
        "pilot": "005",
        "status": "passed",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "validated_at_utc": now(),
        "checks": {
            "predeclared_plan_precedes_source_run": True,
            "source_affecting_scripts_pinned": True,
            "two_strict_events": True,
            "four_complete_source_passes": True,
            "exact_query_and_control_readback": True,
            "native_ris_reconciled": True,
            "compendex_sets_equal": True,
            "inspec_sets_equal_and_separate": True,
            "all_artifacts_non_mergeable": True,
            "predeclared_A1_evidence_boundary_preserved": True,
            "post_pilot_all_schedule_approval": True,
            "adapter_v16_automatic_screenshots": True,
            "bounded_single_and_strict_screenshot_checks": True,
            "guideline_synchronized": True,
            "no_final_search": True,
            "no_private_paths_or_session_values": True,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"validated {PILOT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
