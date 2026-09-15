#!/usr/bin/env python3
"""Validate ATAI Pilot 007 and the accepted source translation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from queries import (
    C1_FIXED_TERMS,
    CHANGED_IDS,
    EF_TERMS,
    EH_TERMS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    MH_TERMS,
    P_TERMS,
    R_TERMS,
    SCHEDULE,
    SCHEDULE_IDS,
    TERM_COUNTS,
    TPRECISE_TERMS,
)

EXPECTED_COUNTS = {
    "A1": 0,
    "A2": 5,
    "A3": 1,
    "B1": 25,
    "B2": 34,
    "BG1": 2,
    "BG2": 7,
    "BC1": 2,
    "BT2": 2,
}
EXPECTED_IDS = {
    "BG1": ["2545579279", "2429649929"],
    "BG2": [
        "1721311269",
        "3346991324",
        "1762095042",
        "1918723567",
        "2331489829",
        "2339214951",
        "2494648056",
    ],
    "BC1": ["1825532815", "3191429714"],
    "BT2": ["2716309451", "3110282684"],
}
EXPECTED_BT2_OLD_ONLY = ["1825532815", "2728408177", "3243962233"]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def file_digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def markdown_link_errors(markdown: Path) -> list[str]:
    errors = []
    text = markdown.read_text()
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        local = target.split("#", 1)[0]
        if not local:
            continue
        path = (markdown.parent / local).resolve()
        if not path.exists():
            errors.append(f"Missing Markdown link in {markdown}: {target}")
    return errors


def protocol_membership_errors(protocol: Path) -> list[str]:
    expected = {
        "Population": P_TERMS,
        "High-specificity EPS": EH_TERMS,
        "Functional or analytical EPS": EF_TERMS,
        "High-specificity MBSE": MH_TERMS,
        "Broad structured model": MB_TERMS,
        "Systems-engineering relationship or concern": R_TERMS,
        "Fixed precise reusable model or template": GMODEL_FIXED_TERMS,
        "Mission-independence marker": GMISSION_TERMS,
        "Exact mission-independent artifact": GMISSION_EXACT_TERMS,
        "Fixed structural reusable artifact": GSTRUCTURE_FIXED_TERMS,
        "Product-line or product-family marker": GPRODUCT_TERMS,
        "Exact product model": GPRODUCT_EXACT_TERMS,
        "Variation marker": GVARIATION_TERMS,
        "Fixed conservative central asset": C1_FIXED_TERMS,
        "Domain-specific modeling-language marker": GDSL_TERMS,
        "Precise tailoring": TPRECISE_TERMS,
    }
    lines = protocol.read_text().splitlines()
    errors = []
    for label, terms in expected.items():
        matches = [line for line in lines if line.startswith(f"- **{label} ")]
        if len(matches) != 1:
            errors.append(f"The protocol has {len(matches)} {label} definitions.")
            continue
        observed = tuple(re.findall(r"`([^`]+)`", matches[0])[1:])
        if observed != terms:
            errors.append(f"Canonical query terms differ from the protocol for {label}.")
    return errors


def validate(root: Path, guideline: Path) -> dict[str, Any]:
    searches = root / "searches"
    errors: list[str] = []
    plan = load(searches / "event-plan.json")
    receipt = load(searches / "run-receipt.json")
    assessment = load(searches / "assessment.json")
    marking = load(searches / "nonmergeable-marking.json")
    initial_omission = load(searches / "initial-screenshot-omission.json")
    failed_attempt = load(searches / "run-receipt-screenshot-repair-attempt1.json")
    failure_artifact = load(
        searches
        / "failures"
        / "count-A1-pass1-restoration.NON_MERGEABLE_FAILURE.json"
    )

    if plan.get("protocol_commit") != "3194156e90497186664260a8e86435e78d2e2aa1":
        errors.append("The plan does not identify the schedule commit.")
    errors.extend(protocol_membership_errors(guideline.parents[2] / "protocol-discovery-and-appraisal.md"))
    if plan.get("translation", {}).get("term_counts") != TERM_COUNTS:
        errors.append("The plan term counts differ from the canonical query module.")
    if plan.get("changed_partitions") != list(CHANGED_IDS):
        errors.append("The changed partition list differs.")
    if plan.get("controls", {}).get("screenshots") != (
        "required automatic search-page and results-page PNGs for every event"
    ):
        errors.append("The plan does not require screenshots for every event.")

    events = plan.get("events", [])
    if len(events) != 22:
        errors.append("The plan does not contain 22 events.")
    for event in events:
        partition = event.get("schedule_id")
        query = event.get("query", "")
        if partition not in SCHEDULE or query != SCHEDULE[partition]:
            errors.append(f"Plan query differs from the canonical {partition} expression.")
            continue
        if event.get("query_sha256") != digest(query):
            errors.append(f"Plan query digest differs for {event.get('event_id')}.")
        if (
            "NEAR/" in query.upper()
            or re.search(r"\b(?:PRE|W)/\d+\b", query.upper())
            or "*" in query
            or "?" in query
            or query.count("NOFT(") != query.count("IF.EXACT(")
            or len(query) >= 50_000
        ):
            errors.append(f"Plan query violates direct translation rules for {event.get('event_id')}.")

    if (
        receipt.get("status") != "complete"
        or receipt.get("predeclared_event_count") != 22
        or receipt.get("completed_event_count") != 22
        or any(outcome.get("return_code") != 0 for outcome in receipt.get("outcomes", []))
    ):
        errors.append("The live run receipt is incomplete.")

    plan_by_id = {event["event_id"]: event for event in events}
    source_artifacts = []
    screenshot_files: list[Path] = []
    for outcome in receipt.get("outcomes", []):
        event = plan_by_id.get(outcome.get("event_id"))
        if not event:
            errors.append(f"Receipt outcome has no planned event: {outcome.get('event_id')}")
            continue
        artifact_path = root / outcome["output"]
        artifact = load(artifact_path)
        source_artifacts.append(artifact_path)
        metadata = artifact.get("output_metadata", {})
        run = metadata.get("prisma_search_run", {})
        strategy = run.get("strategy", {})
        limits = strategy.get("limits", {})
        date = limits.get("publication_date", {}).get("effective", {})
        screenshot_receipt = metadata.get("screenshots", {})

        if artifact.get("schema_version") != "academic-search-result/v1":
            errors.append(f"Unexpected source artifact schema: {artifact_path}")
        if artifact.get("requested_query") != event["query"]:
            errors.append(f"Requested query readback differs: {artifact_path}")
        if strategy.get("executed_query") != artifact.get("executed_query"):
            errors.append(f"Executed query provenance differs: {artifact_path}")
        if (
            strategy.get("search_scope") != "Advanced Technologies & Aerospace Index"
            or limits.get("language", {}).get("value") != "LA(English)"
            or date.get("start") != "2011-01-01"
            or date.get("end") != "2026-08-29"
            or date.get("inclusive") != "both"
            or strategy.get("sort", {}).get("value") != "DateAsc"
            or strategy.get("query_syntax", {}).get("spelling_variants") is not False
            or strategy.get("query_syntax", {}).get("form_variants") is not False
            or limits.get("document_type", {}).get("state") != "not_applied"
            or limits.get("peer_reviewed", {}).get("state") != "not_applied"
            or limits.get("full_text", {}).get("state") != "unavailable"
            or limits.get("access", {}).get("state") != "unavailable"
            or run.get("adapter", {}).get("adapter_version") != "6"
        ):
            errors.append(f"Source controls differ: {artifact_path}")
        if (
            screenshot_receipt.get("schema_version") != "atai-automatic-screenshots/v1"
            or screenshot_receipt.get("automatic") is not True
            or screenshot_receipt.get("same_directory_as_json") is not True
        ):
            errors.append(f"Screenshot receipt is missing: {artifact_path}")
        for key, suffix in (
            ("search_page", ".search-page.png"),
            ("results_page", ".results-page.png"),
        ):
            screenshot_path = artifact_path.with_name(f"{artifact_path.stem}{suffix}")
            evidence = screenshot_receipt.get(key, {})
            if not screenshot_path.is_file():
                errors.append(f"Screenshot file is missing: {screenshot_path}")
                continue
            screenshot_files.append(screenshot_path)
            if (
                screenshot_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n"
                or evidence.get("path") != screenshot_path.name
                or evidence.get("sha256") != file_digest(screenshot_path)
                or not isinstance(evidence.get("width"), int)
                or evidence["width"] <= 0
                or not isinstance(evidence.get("height"), int)
                or evidence["height"] <= 0
                or evidence.get("browser_chrome_captured") is not False
                or evidence.get("complete_page_url_retained") is not False
                or evidence.get("session_identifiers_retained") is not False
            ):
                errors.append(f"Screenshot evidence differs: {screenshot_path}")
        if (
            artifact.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
            or metadata.get("normalized_merge_eligible") is not False
            or metadata.get("pilot_only") is not True
            or run.get("report_ready") is not False
        ):
            errors.append(f"Source artifact remains mergeable: {artifact_path}")

        expected_status = "count_only" if event["mode"] == "count" else "success"
        if metadata.get("status") != expected_status:
            errors.append(f"Source artifact status differs: {artifact_path}")
        if event["mode"] == "complete" and (
            metadata.get("retrieval_complete") is not True
            or artifact.get("total") != len(artifact.get("results", []))
        ):
            errors.append(f"Strict capture is incomplete: {artifact_path}")

    if len(source_artifacts) != 22:
        errors.append("The receipt does not identify 22 source artifacts.")
    if len(screenshot_files) != 44 or len(set(screenshot_files)) != 44:
        errors.append("The pilot does not contain 44 unique source screenshots.")
    if (
        marking.get("status") != "complete"
        or marking.get("marked_artifact_count") != 23
        or len(marking.get("marked_artifacts", [])) != 23
    ):
        errors.append("The non-mergeable marking receipt is incomplete.")
    if (
        initial_omission.get("status") != "superseded_missing_required_screenshots"
        or initial_omission.get("initial_source_artifact_count") != 22
        or initial_omission.get("initial_screenshot_file_count") != 0
        or failed_attempt.get("status") != "stopped_on_source_or_adapter_failure"
        or failed_attempt.get("completed_event_count") != 1
        or failed_attempt.get("retained_failure_artifact")
        != "searches/failures/count-A1-pass1-restoration.NON_MERGEABLE_FAILURE.json"
        or failure_artifact.get("output_metadata", {}).get("status") != "error"
        or failure_artifact.get("do_not_merge") is not True
        or failure_artifact.get("output_metadata", {}).get("merge_eligible") is not False
    ):
        errors.append("The screenshot repair history or retained failure is incomplete.")

    for partition, expected in EXPECTED_COUNTS.items():
        first = load(searches / "counts" / "pass1" / f"{partition}.json")
        second = load(searches / "counts" / "pass2" / f"{partition}.json")
        if first.get("total") != expected or second.get("total") != expected:
            errors.append(f"Repeated totals changed for {partition}.")

    for partition, expected in EXPECTED_IDS.items():
        artifact = load(searches / "records" / f"{partition}.json")
        ids = [str(record.get("paperId")) for record in artifact.get("results", [])]
        if ids != expected or artifact.get("total") != EXPECTED_COUNTS[partition]:
            errors.append(f"Strict stable IDs changed for {partition}.")

    if (
        assessment.get("status") != "complete"
        or assessment.get("decision") != "accept_direct_no_proximity_translation"
        or assessment.get("translation", {}).get("proximity_operators") != 0
        or assessment.get("translation", {}).get("pair_expansions") != 0
        or assessment.get("translation", {}).get("maximum_query_characters") != 9_528
        or assessment.get("changed_partition_union", {}).get("deduplicated_stable_ids") != 13
        or assessment.get("changed_partition_union", {}).get("cross_partition_intersections") != {}
        or assessment.get("automatic_screenshots", {}).get("successful_source_event_count") != 22
        or assessment.get("automatic_screenshots", {}).get("screenshot_file_count") != 44
        or assessment.get("source_artifact_count") != 23
    ):
        errors.append("The assessment decision or summary changed.")
    comparison = assessment.get("superseded_schedule_comparison", {}).get("partitions", {})
    if (
        comparison.get("BT2", {}).get("current_only_ids") != EXPECTED_IDS["BT2"]
        or comparison.get("BT2", {}).get("superseded_only_ids") != EXPECTED_BT2_OLD_ONLY
        or any(comparison.get(partition, {}).get("current_only_ids") for partition in ("BG1", "BG2", "BC1"))
    ):
        errors.append("The superseded schedule comparison changed.")

    guideline_text = guideline.read_text()
    required_guideline_text = (
        "Use no proximity operators, pair expansions, or wildcards.",
        "Compound `G_model`",
        "Compound `G_structure`",
        "Compound `C1`",
        "F(T_precise)",
        "[Pilot 007](pilots/007/pilot.md)",
    )
    for text in required_guideline_text:
        if text not in guideline_text:
            errors.append(f"The guideline lacks accepted Pilot 007 text: {text}")
    for obsolete in ("PAIR(a,b)", "NEAR/5", "F(T2)", "expanded pairs"):
        if obsolete in guideline_text:
            errors.append(f"The guideline retains obsolete translation text: {obsolete}")

    pilot = root / "pilot.md"
    errors.extend(markdown_link_errors(pilot))
    errors.extend(markdown_link_errors(guideline))

    return {
        "schema_version": "atai-pilot-007-validation-report/v1",
        "status": "ok" if not errors else "error",
        "pilot": "007",
        "do_not_merge": True,
        "checks": {
            "canonical_term_membership": "passed" if not any("protocol" in error.lower() or "query terms" in error.lower() for error in errors) else "failed",
            "no_proximity_or_wildcards": "passed" if not any("direct translation rules" in error for error in errors) else "failed",
            "complete_live_run": "passed" if receipt.get("status") == "complete" else "failed",
            "source_readback_and_controls": "passed" if not any("readback" in error or "controls" in error for error in errors) else "failed",
            "required_screenshots": "passed" if not any("screenshot" in error.lower() for error in errors) else "failed",
            "repeated_totals": "passed" if not any("totals changed" in error for error in errors) else "failed",
            "strict_changed_partition_capture": "passed" if not any("Strict" in error for error in errors) else "failed",
            "all_source_artifacts_nonmergeable": "passed" if marking.get("marked_artifact_count") == 23 else "failed",
            "retained_repair_failure": "passed" if failed_attempt.get("status") == "stopped_on_source_or_adapter_failure" else "failed",
            "assessment": "passed" if assessment.get("status") == "complete" else "failed",
            "guideline_synchronized": "passed" if not any("guideline" in error.lower() for error in errors) else "failed",
            "local_markdown_links": "passed" if not any("Markdown link" in error for error in errors) else "failed",
        },
        "summary": {
            "successful_source_artifact_count": len(source_artifacts),
            "retained_failure_artifact_count": 1,
            "total_source_artifact_count": len(source_artifacts) + 1,
            "screenshot_file_count": len(screenshot_files),
            "partition_totals": EXPECTED_COUNTS,
            "changed_partition_record_occurrences": 13,
            "changed_partition_distinct_ids": 13,
            "maximum_query_characters": 9_528,
            "proximity_operators": 0,
            "pair_expansions": 0,
            "query_splits": 0,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('{"status": "running"}\n')
    report = validate(args.pilot_root, args.guideline)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
