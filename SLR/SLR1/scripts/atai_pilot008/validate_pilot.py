#!/usr/bin/env python3
"""Validate ATAI Pilot 008 and the accepted bounded wildcard translation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from build_plan import validate as validate_plan
from queries import (
    BLOCK_TERMS,
    FAMILY_COUNT,
    LITERAL_SCHEDULE,
    PROTOCOL_COMMIT,
    REPLACED_TERM_COUNT,
    SCHEDULE_IDS,
    TERM_COUNTS,
    WILDCARD_SCHEDULE,
)

PILOT_ROOT = (
    Path(__file__).resolve().parents[2]
    / "source-specific"
    / "advanced-technologies-aerospace-index"
    / "pilots"
    / "008"
)
GUIDELINE = PILOT_ROOT.parents[1] / "source-specific-guidelines.md"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "validation-report.json"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
EXPECTED_TOTALS = {
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
EXPECTED_LENGTHS = {
    "A1": (7662, 6523, 38),
    "A2": (9528, 8038, 48),
    "A3": (6012, 4656, 45),
    "B1": (5177, 4541, 20),
    "B2": (6242, 4639, 47),
    "BG1": (6092, 4733, 42),
    "BG2": (4898, 3798, 36),
    "BC1": (3439, 2755, 25),
    "BT2": (5240, 3772, 34),
}
PROTOCOL_LABELS = {
    "Population": "P",
    "High-specificity EPS": "E_H",
    "Functional or analytical EPS": "E_F",
    "High-specificity MBSE": "M_H",
    "Broad structured model": "M_B",
    "Systems-engineering relationship or concern": "R",
    "Fixed precise reusable model or template": "G_model_fixed",
    "Mission-independence marker": "G_mission",
    "Exact mission-independent artifact": "G_mission_exact",
    "Fixed structural reusable artifact": "G_structure_fixed",
    "Product-line or product-family marker": "G_product",
    "Exact product model": "G_product_exact",
    "Variation marker": "G_variation",
    "Fixed conservative central asset": "C1_fixed",
    "Domain-specific modeling-language marker": "G_DSL",
    "Precise tailoring": "T_precise",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_ids(artifact: dict[str, Any]) -> list[str]:
    return [str(record.get("paperId")) for record in artifact.get("results", [])]


def markdown_link_errors(markdown: Path) -> list[str]:
    errors: list[str] = []
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        local = target.split("#", 1)[0]
        if local and not (markdown.parent / local).resolve().exists():
            errors.append(f"Missing Markdown link in {markdown}: {target}")
    return errors


def protocol_membership_errors(protocol: Path) -> list[str]:
    lines = protocol.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    for label, block in PROTOCOL_LABELS.items():
        matches = [line for line in lines if line.startswith(f"- **{label} ")]
        if len(matches) != 1:
            errors.append(f"The protocol has {len(matches)} {label} definitions")
            continue
        observed = tuple(re.findall(r"`([^`]+)`", matches[0])[1:])
        if observed != BLOCK_TERMS[block]:
            errors.append(f"Canonical query terms differ from the protocol for {label}")
    return errors


def validate(root: Path, guideline: Path) -> dict[str, Any]:
    searches = root / "searches"
    errors: list[str] = []
    plan = load(searches / "event-plan.json")
    receipt = load(searches / "run-receipt.json")
    assessment = load(searches / "assessment.json")
    marking = load(searches / "nonmergeable-marking.json")
    failure_history = load(searches / "failure-history.json")

    if plan.get("protocol_commit") != PROTOCOL_COMMIT:
        errors.append("The plan does not identify the schedule commit")
    errors.extend(validate_plan(plan))
    errors.extend(
        protocol_membership_errors(root.parents[3] / "protocol-discovery-and-appraisal.md")
    )
    snapshot = plan.get("term_snapshot", {})
    if snapshot.get("term_counts") != TERM_COUNTS:
        errors.append("The plan term counts differ from the canonical query module")
    translation = plan.get("translation", {})
    if (
        translation.get("wildcard_family_count") != FAMILY_COUNT
        or translation.get("replaced_literal_occurrence_count_across_blocks")
        != REPLACED_TERM_COUNT
        or FAMILY_COUNT != 128
        or REPLACED_TERM_COUNT != 292
    ):
        errors.append("The accepted wildcard family map changed")
    if plan.get("adapter") != {
        "id": "search_proquest_aerospace",
        "minimum_version": 6,
        "mandatory_automatic_screenshots": True,
        "screenshot_opt_out": False,
    }:
        errors.append("The plan does not require adapter screenshots without opt out")

    events = plan.get("events", [])
    plan_by_id = {event["event_id"]: event for event in events}
    if (
        receipt.get("schema_version") != "atai-pilot-008-run-receipt/v1"
        or receipt.get("status") != "complete"
        or receipt.get("predeclared_event_count") != 18
        or receipt.get("completed_event_count") != 18
        or len(receipt.get("outcomes", [])) != 18
        or any(item.get("return_code") != 0 for item in receipt.get("outcomes", []))
    ):
        errors.append("The final live run receipt is incomplete")

    artifacts: dict[tuple[str, str], dict[str, Any]] = {}
    source_paths: list[Path] = []
    screenshot_paths: list[Path] = []
    adapter_hashes: set[str] = set()
    for outcome in receipt.get("outcomes", []):
        event = plan_by_id.get(outcome.get("event_id"))
        if event is None:
            errors.append(f"Receipt outcome lacks a plan event: {outcome.get('event_id')}")
            continue
        path = root / outcome["output"]
        artifact = load(path)
        source_paths.append(path)
        artifacts[(event["variant"], event["schedule_id"])] = artifact
        metadata = artifact.get("output_metadata", {})
        run = metadata.get("prisma_search_run", {})
        strategy = run.get("strategy", {})
        limits = strategy.get("limits", {})
        date = limits.get("publication_date", {}).get("effective", {})
        adapter = run.get("adapter", {})
        ids = stable_ids(artifact)
        adapter_hash = adapter.get("script_sha256")
        if isinstance(adapter_hash, str):
            adapter_hashes.add(adapter_hash)

        if (
            artifact.get("schema_version") != "academic-search-result/v1"
            or artifact.get("requested_query") != event["query"]
            or strategy.get("requested_query") != event["query"]
            or strategy.get("executed_query") != artifact.get("executed_query")
            or metadata.get("status") != "success"
            or metadata.get("retrieval_complete") is not True
            or artifact.get("total") != len(ids)
            or len(ids) != len(set(ids))
            or any(not paper_id.isdigit() for paper_id in ids)
        ):
            errors.append(f"Successful source artifact is incomplete: {event['event_id']}")
        if (
            adapter.get("adapter_id") != "search_proquest_aerospace"
            or adapter.get("adapter_version") != "6"
            or strategy.get("search_scope") != "Advanced Technologies & Aerospace Index"
            or strategy.get("query_syntax", {}).get("spelling_variants") is not False
            or strategy.get("query_syntax", {}).get("form_variants") is not False
            or limits.get("language", {}).get("value") != "LA(English)"
            or date.get("start") != "2011-01-01"
            or date.get("end") != "2026-08-29"
            or date.get("inclusive") != "both"
            or strategy.get("sort", {}).get("value") != "DateAsc"
            or limits.get("document_type", {}).get("state") != "not_applied"
            or limits.get("peer_reviewed", {}).get("state") != "not_applied"
            or limits.get("full_text", {}).get("state") != "unavailable"
            or limits.get("access", {}).get("state") != "unavailable"
        ):
            errors.append(f"Source controls differ: {event['event_id']}")
        if (
            artifact.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
            or metadata.get("normalized_merge_eligible") is not False
            or metadata.get("pilot_only") is not True
            or run.get("report_ready") is not False
        ):
            errors.append(f"Source artifact remains mergeable: {event['event_id']}")

        screenshots = metadata.get("screenshots", {})
        if (
            screenshots.get("schema_version") != "atai-automatic-screenshots/v1"
            or screenshots.get("automatic") is not True
            or screenshots.get("same_directory_as_json") is not True
        ):
            errors.append(f"Screenshot receipt differs: {event['event_id']}")
        for kind, suffix in (
            ("search_page", ".search-page.png"),
            ("results_page", ".results-page.png"),
        ):
            screenshot = path.with_name(f"{path.stem}{suffix}")
            evidence = screenshots.get(kind, {})
            if (
                not screenshot.is_file()
                or screenshot.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n"
                or evidence.get("path") != screenshot.name
                or evidence.get("sha256") != file_sha256(screenshot)
                or not isinstance(evidence.get("width"), int)
                or evidence["width"] <= 0
                or not isinstance(evidence.get("height"), int)
                or evidence["height"] <= 0
                or evidence.get("browser_chrome_captured") is not False
                or evidence.get("complete_page_url_retained") is not False
                or evidence.get("session_identifiers_retained") is not False
            ):
                errors.append(f"Screenshot evidence differs: {event['event_id']} {kind}")
            screenshot_paths.append(screenshot)

    if len(source_paths) != 18 or len(set(source_paths)) != 18:
        errors.append("The final receipt does not identify eighteen unique source artifacts")
    if len(screenshot_paths) != 36 or len(set(screenshot_paths)) != 36:
        errors.append("The final run does not contain thirty-six unique screenshots")
    if len(adapter_hashes) != 1:
        errors.append("Successful events used different adapter files")

    union_literal: set[str] = set()
    union_wildcard: set[str] = set()
    for partition in SCHEDULE_IDS:
        literal = artifacts.get(("literal", partition), {})
        wildcard = artifacts.get(("wildcard", partition), {})
        literal_ids = stable_ids(literal)
        wildcard_ids = stable_ids(wildcard)
        union_literal.update(literal_ids)
        union_wildcard.update(wildcard_ids)
        expected_length, expected_wildcard_length, expected_operators = EXPECTED_LENGTHS[
            partition
        ]
        if (
            literal.get("total") != EXPECTED_TOTALS[partition]
            or wildcard.get("total") != EXPECTED_TOTALS[partition]
            or literal_ids != wildcard_ids
            or len(LITERAL_SCHEDULE[partition]) != expected_length
            or len(WILDCARD_SCHEDULE[partition]) != expected_wildcard_length
            or WILDCARD_SCHEDULE[partition].count("[*") != expected_operators
        ):
            errors.append(f"Literal and wildcard evidence differs for {partition}")
    if union_literal != union_wildcard or len(union_literal) != 60:
        errors.append("The literal and wildcard union comparison changed")

    failure_artifacts = sorted((searches / "failures").glob("*.json"))
    if (
        failure_history.get("schema_version") != "atai-pilot-008-failure-history/v1"
        or failure_history.get("status") != "complete"
        or failure_history.get("attempt_count") != 6
        or failure_history.get("retained_source_failure_artifact_count") != 5
        or failure_history.get("retained_failure_screenshot_count") != 2
        or len(failure_artifacts) != 5
    ):
        errors.append("The retained failure history changed")
    for path in failure_artifacts:
        artifact = load(path)
        metadata = artifact.get("output_metadata", {})
        if (
            metadata.get("status") != "error"
            or artifact.get("do_not_merge") is not True
            or metadata.get("merge_eligible") is not False
            or metadata.get("pilot_only") is not True
        ):
            errors.append(f"Retained failure is not safely marked: {path}")
    if (
        marking.get("schema_version") != "atai-pilot-008-nonmergeable-marking/v1"
        or marking.get("status") != "complete"
        or marking.get("marked_artifact_count") != 23
        or len(marking.get("marked_artifacts", [])) != 23
    ):
        errors.append("The nonmergeable marking receipt changed")

    if (
        assessment.get("schema_version") != "atai-pilot-008-assessment/v1"
        or assessment.get("status") != "complete"
        or assessment.get("decision") != "accept_bounded_wildcard_translation"
        or assessment.get("union_comparison", {}).get("literal_distinct_ids") != 60
        or assessment.get("union_comparison", {}).get("wildcard_distinct_ids") != 60
        or assessment.get("union_comparison", {}).get("literal_ids_missing_from_wildcard")
        != []
        or assessment.get("union_comparison", {}).get("wildcard_only_ids") != []
        or assessment.get("automatic_screenshots", {}).get(
            "successful_event_screenshot_file_count"
        )
        != 36
        or assessment.get("source_artifact_count") != 23
        or assessment.get("errors") != []
    ):
        errors.append("The accepted assessment changed")

    guideline_text = guideline.read_text(encoding="utf-8")
    for required in (
        "Bounded wildcard family `W(V)`",
        "Use the 128 families",
        "Wildcard use is accepted only in `NOFT`",
        "[Pilot 008](pilots/008/pilot.md)",
        "Keep all exact `IF` alternatives literal",
    ):
        if required not in guideline_text:
            errors.append(f"The source guideline lacks accepted text: {required}")
    if "Use no proximity operators, pair expansions, or wildcards." in guideline_text:
        errors.append("The source guideline retains the superseded no-wildcard rule")

    if not ADAPTER.is_file():
        errors.append("The ATAI adapter is missing")
    else:
        adapter_text = ADAPTER.read_text(encoding="utf-8")
        if (
            'ADAPTER_VERSION = "6"' not in adapter_text
            or '"--no-screenshots"' in adapter_text
            or "args.screenshot_paths = screenshot_paths_for_output(args.output_path)"
            not in adapter_text
        ):
            errors.append("The ATAI adapter does not enforce mandatory sibling screenshots")

    pilot = root / "pilot.md"
    errors.extend(markdown_link_errors(pilot))
    errors.extend(markdown_link_errors(guideline))

    return {
        "schema_version": "atai-pilot-008-validation-report/v1",
        "status": "ok" if not errors else "error",
        "pilot": "008",
        "do_not_merge": True,
        "checks": {
            "canonical_protocol_membership": "passed"
            if not any("protocol" in value.lower() for value in errors)
            else "failed",
            "predeclared_queries": "passed"
            if not any("plan" in value.lower() or "query" in value.lower() for value in errors)
            else "failed",
            "complete_live_run": "passed"
            if receipt.get("status") == "complete"
            else "failed",
            "source_readback_and_controls": "passed"
            if not any("controls" in value.lower() or "incomplete" in value.lower() for value in errors)
            else "failed",
            "literal_wildcard_ordered_set_equality": "passed"
            if not any("evidence differs" in value or "union comparison" in value for value in errors)
            else "failed",
            "mandatory_screenshots": "passed"
            if not any("screenshot" in value.lower() for value in errors)
            else "failed",
            "adapter_no_opt_out": "passed"
            if not any("adapter" in value.lower() for value in errors)
            else "failed",
            "retained_failures": "passed"
            if not any("failure" in value.lower() for value in errors)
            else "failed",
            "all_source_artifacts_nonmergeable": "passed"
            if marking.get("marked_artifact_count") == 23
            else "failed",
            "assessment": "passed"
            if assessment.get("status") == "complete"
            else "failed",
            "guideline_synchronized": "passed"
            if not any("guideline" in value.lower() for value in errors)
            else "failed",
            "local_markdown_links": "passed"
            if not any("Markdown link" in value for value in errors)
            else "failed",
        },
        "summary": {
            "successful_source_artifact_count": len(source_paths),
            "retained_source_failure_artifact_count": len(failure_artifacts),
            "source_artifact_count": len(source_paths) + len(failure_artifacts),
            "successful_screenshot_file_count": len(screenshot_paths),
            "retained_failure_screenshot_file_count": failure_history.get(
                "retained_failure_screenshot_count"
            ),
            "partition_totals": EXPECTED_TOTALS,
            "literal_wildcard_union_distinct_ids": len(union_literal),
            "wildcard_family_count": FAMILY_COUNT,
            "replaced_literal_occurrence_count_across_blocks": REPLACED_TERM_COUNT,
            "maximum_literal_query_characters": max(
                len(value) for value in LITERAL_SCHEDULE.values()
            ),
            "maximum_wildcard_query_characters": max(
                len(value) for value in WILDCARD_SCHEDULE.values()
            ),
            "query_splits": 0,
            "proximity_operators": 0,
            "pair_expansions": 0,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--guideline", type=Path, default=GUIDELINE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('{"status": "running"}\n', encoding="utf-8")
    report = validate(args.pilot_root, args.guideline)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "errors": report["errors"]}, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
