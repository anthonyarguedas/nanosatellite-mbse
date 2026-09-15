#!/usr/bin/env python3
"""Build the Inspec Pilot 004 assessment from existing paired source events.

Engineering Village searched Compendex and Inspec in one predeclared event for
Compendex Pilots 005 and 008. This script validates the Inspec projections in
those immutable events. It does not submit another source query.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PILOT = "004"
PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
PLAN_SCHEMA = "inspec-linked-current-schedule-pilot-plan/v1"
ASSESSMENT_SCHEMA = "inspec-linked-current-schedule-pilot-assessment/v1"
RECONCILIATION_SCHEMA = "inspec-linked-current-schedule-reconciliation/v1"
APPROVAL_SCHEMA = "inspec-wildcard-source-translation-approval/v1"
VALIDATION_SCHEMA = "inspec-linked-current-schedule-validation/v1"
SCREENSHOT_SCHEMA = "engineering-village-automatic-screenshots/v1"
INSPEC_LABEL = "Inspec (Engineering Village)"
REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
PILOT_ROOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/inspec/pilots/004"
SEARCH_ROOT = PILOT_ROOT / "searches"
COMPENDEX_005 = REPOSITORY_ROOT / "SLR/SLR1/source-specific/compendex/pilots/005"
COMPENDEX_008 = REPOSITORY_ROOT / "SLR/SLR1/source-specific/compendex/pilots/008"
ADAPTER_ROOT = Path.home() / "agent-tools/internet/skills/browser/scripts"
ADAPTER_ENTRYPOINT = ADAPTER_ROOT / "search_compendex_inspec.py"
ADAPTER_IMPLEMENTATION = ADAPTER_ROOT / "_engineering_village_search.py"
GUIDELINE = REPOSITORY_ROOT / "SLR/SLR1/source-specific/inspec/source-specific-guidelines.md"
QUERIES_PATH = REPOSITORY_ROOT / "SLR/SLR1/source-specific/compendex/scripts/compendex_pilot008/queries.py"
SOURCE_PLAN_005 = COMPENDEX_005 / "searches/event-plan.json"
SOURCE_ASSESSMENT_005 = COMPENDEX_005 / "searches/assessment.json"
SCREENSHOT_VALIDATION = COMPENDEX_005 / "searches/adapter-v16-screenshot-validation.json"
SOURCE_PLAN_008 = COMPENDEX_008 / "searches/event-plan.json"
SOURCE_RUN_008 = COMPENDEX_008 / "searches/run-receipt.json"
SOURCE_ASSESSMENT_008 = COMPENDEX_008 / "searches/assessment.json"
SOURCE_RECONCILIATION_008 = COMPENDEX_008 / "searches/reconciliation.json"
WILDCARD_REPLACEMENTS = (
    {
        "wildcard_atom": "(CubeSat* WN ALL)",
        "replaced_literals": ["CubeSat", "CubeSats"],
    },
    {
        "wildcard_atom": "(nanosat* WN ALL)",
        "replaced_literals": [
            "nanosat",
            "nanosats",
            "nanosatellite",
            "nanosatellites",
        ],
    },
    {
        "wildcard_atom": "(SmallSat* WN ALL)",
        "replaced_literals": ["SmallSat", "SmallSats"],
    },
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(REPOSITORY_ROOT))


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected one JSON object in {path}")
    return value


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {path}") from error


def load_queries() -> Any:
    spec = importlib.util.spec_from_file_location(
        "inspec_pilot004_linked_queries", QUERIES_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {QUERIES_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def png_dimensions(path: Path) -> dict[str, int] | None:
    if not path.is_file():
        return None
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    if width < 1 or height < 1:
        return None
    return {"width": width, "height": height}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_screenshot_pair(output: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    screenshots = metadata.get("screenshots")
    require(isinstance(screenshots, dict), f"Missing screenshots in {output}")
    require(
        screenshots.get("schema_version") == SCREENSHOT_SCHEMA,
        f"Unexpected screenshot schema in {output}",
    )
    require(screenshots.get("automatic") is True, f"Screenshots not automatic in {output}")
    require(
        screenshots.get("opt_out_available") is False,
        f"Screenshot opt-out recorded in {output}",
    )
    require(
        screenshots.get("same_directory_as_json") is True,
        f"Screenshots not recorded beside {output}",
    )
    checks: dict[str, Any] = {}
    for key, suffix, page_kind in (
        ("search_page", ".search-page.png", "configured_search_page"),
        ("results_page", ".results-page.png", "verified_first_results_page"),
    ):
        path = output.with_name(f"{output.stem}{suffix}")
        evidence = screenshots.get(key)
        dimensions = png_dimensions(path)
        require(isinstance(evidence, dict), f"Missing {key} receipt in {output}")
        require(path.parent == output.parent, f"{key} is not beside {output}")
        require(dimensions is not None, f"Missing or invalid PNG {path}")
        require(evidence.get("page") == page_kind, f"Wrong {key} kind in {output}")
        require(evidence.get("file_name") == path.name, f"Wrong {key} name in {output}")
        require(evidence.get("sha256") == digest_file(path), f"Wrong {key} hash in {output}")
        require(
            evidence.get("width") == dimensions["width"]
            and evidence.get("height") == dimensions["height"],
            f"Wrong {key} dimensions in {output}",
        )
        checks[key] = {
            "path": relative(path),
            "sha256": evidence["sha256"],
            "width": dimensions["width"],
            "height": dimensions["height"],
            "receipt_matches": True,
        }
    return checks


def verify_current_adapter(source_plan: dict[str, Any]) -> dict[str, Any]:
    adapter = source_plan.get("adapter")
    require(isinstance(adapter, dict), "Pilot 008 lacks adapter evidence")
    require(adapter.get("version") == "16", "Pilot 008 did not use adapter v16")
    require(ADAPTER_ENTRYPOINT.is_file(), f"Missing {ADAPTER_ENTRYPOINT}")
    require(ADAPTER_IMPLEMENTATION.is_file(), f"Missing {ADAPTER_IMPLEMENTATION}")
    entry_hash = digest_file(ADAPTER_ENTRYPOINT)
    implementation_hash = digest_file(ADAPTER_IMPLEMENTATION)
    require(
        entry_hash == adapter.get("entrypoint_sha256"),
        "The paired adapter entry point changed after Pilot 008",
    )
    require(
        implementation_hash == adapter.get("implementation_sha256"),
        "The paired adapter implementation changed after Pilot 008",
    )
    implementation_text = ADAPTER_IMPLEMENTATION.read_text(encoding="utf-8")
    entrypoint_text = ADAPTER_ENTRYPOINT.read_text(encoding="utf-8")
    prohibited_options = ("--no-screenshot", "--skip-screenshots")
    require(
        all(option not in implementation_text and option not in entrypoint_text for option in prohibited_options),
        "The paired adapter exposes a screenshot opt-out",
    )
    require(
        "validate_automatic_screenshot_destinations" in implementation_text
        and "assert_automatic_screenshot_evidence" in implementation_text,
        "The paired adapter lacks mandatory screenshot publication checks",
    )
    return {
        "id": adapter.get("id"),
        "version": adapter.get("version"),
        "entrypoint": relative(ADAPTER_ENTRYPOINT)
        if ADAPTER_ENTRYPOINT.is_relative_to(REPOSITORY_ROOT)
        else "~/agent-tools/internet/skills/browser/scripts/search_compendex_inspec.py",
        "entrypoint_sha256": entry_hash,
        "implementation": "~/agent-tools/internet/skills/browser/scripts/_engineering_village_search.py",
        "implementation_sha256": implementation_hash,
        "automatic_sibling_screenshots": True,
        "opt_out_available": False,
        "successful_output_requires_both_receipts": True,
    }


def inspec_ids(value: dict[str, Any]) -> list[str]:
    results = value.get("results")
    require(isinstance(results, list), "A source artifact lacks results")
    ids: list[str] = []
    for record in results:
        require(isinstance(record, dict), "A source result is not an object")
        if record.get("source") != INSPEC_LABEL:
            continue
        accession = record.get("paperId")
        require(isinstance(accession, str) and accession, "An Inspec record lacks an accession")
        ids.append(accession)
    require(len(ids) == len(set(ids)), "An Inspec projection repeats an accession")
    return ids


def validate_a1_comparison() -> dict[str, Any]:
    assessment = load(SOURCE_ASSESSMENT_005)
    plan = load(SOURCE_PLAN_005)
    comparison = assessment.get("database_comparisons", {}).get("inspec")
    require(isinstance(comparison, dict), "Pilot 005 lacks an Inspec A1 comparison")
    require(comparison.get("both_captures_complete") is True, "Pilot 005 A1 was incomplete")
    require(comparison.get("sets_equal") is True, "Pilot 005 Inspec A1 sets differ")
    require(
        comparison.get("literal_missing_from_wildcard") == []
        and comparison.get("wildcard_only_accessions") == [],
        "Pilot 005 Inspec A1 has a wildcard difference",
    )
    cells = assessment.get("cells")
    require(isinstance(cells, dict), "Pilot 005 lacks cells")
    verified: dict[str, Any] = {}
    for event_id in ("literal-A1", "wildcard-A1"):
        cell = cells.get(event_id)
        require(isinstance(cell, dict), f"Pilot 005 lacks {event_id}")
        output = COMPENDEX_005 / "searches" / cell["artifact"]
        value = load(output)
        require(digest_file(output) == cell.get("artifact_sha256"), f"Changed {event_id}")
        ids = inspec_ids(value)
        projected = cell.get("projections", {}).get("inspec", {})
        require(ids == projected.get("ordered_stable_accessions"), f"Wrong {event_id} IDs")
        context = value.get("pilot_context", {})
        strict = context.get("strict_complete_comparison_receipt")
        require(
            context.get("status") == "strict_two_pass_complete"
            and isinstance(strict, dict)
            and strict.get("sequence_match") is True,
            f"{event_id} lacks two strict passes",
        )
        verified[event_id] = {
            "artifact": relative(output),
            "artifact_sha256": digest_file(output),
            "query_sha256": cell.get("query_sha256"),
            "query_characters": cell.get("query_characters"),
            "inspec_total": len(ids),
            "ordered_stable_accessions": ids,
            "strict_passes": 2,
        }
    return {
        "source_plan": {
            "path": relative(SOURCE_PLAN_005),
            "sha256": digest_file(SOURCE_PLAN_005),
            "predeclared_before_source_use": True,
        },
        "source_assessment": {
            "path": relative(SOURCE_ASSESSMENT_005),
            "sha256": digest_file(SOURCE_ASSESSMENT_005),
        },
        "events": verified,
        "literal_total": comparison.get("literal_total"),
        "wildcard_total": comparison.get("wildcard_total"),
        "literal_accessions": comparison.get("literal_accessions"),
        "wildcard_accessions": comparison.get("wildcard_accessions"),
        "literal_missing_from_wildcard": [],
        "wildcard_only_accessions": [],
        "sets_equal": True,
        "source_events": 2,
        "strict_source_passes": 4,
        "note": (
            "Pilot 005 reserved the translation decision for Inspec. Pilot 004 now "
            "uses its already retained, database-scoped Inspec evidence."
        ),
        "plan_protocol_commit": plan.get("protocol_commit"),
    }


def validate_current_schedule(queries: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    plan = load(SOURCE_PLAN_008)
    run = load(SOURCE_RUN_008)
    assessment = load(SOURCE_ASSESSMENT_008)
    reconciliation = load(SOURCE_RECONCILIATION_008)
    require(plan.get("protocol_commit") == PROTOCOL_COMMIT, "Wrong Pilot 008 protocol commit")
    require(assessment.get("status") == "passed", "Pilot 008 assessment did not pass")
    require(run.get("status") == "complete" and run.get("success") is True, "Pilot 008 run incomplete")
    require(
        run.get("event_plan_sha256") == digest_file(SOURCE_PLAN_008),
        "Pilot 008 run is not bound to its plan",
    )
    require(
        assessment.get("checks", {}).get("all_nine_current_partitions") is True,
        "Pilot 008 did not cover all partitions",
    )
    require(
        assessment.get("checks", {}).get("no_proximity_operator_in_any_query") is True,
        "Pilot 008 retained a proximity operator",
    )
    adapter = verify_current_adapter(plan)
    planned = {item.get("partition_id"): item for item in plan.get("events", [])}
    outcomes = {item.get("partition_id"): item for item in run.get("outcomes", [])}
    linked_partitions = reconciliation.get("partitions")
    require(isinstance(linked_partitions, dict), "Pilot 008 reconciliation lacks partitions")
    require(set(planned) == set(queries.SCHEDULE_IDS), "Pilot 008 plan coverage changed")
    require(set(outcomes) == set(queries.SCHEDULE_IDS), "Pilot 008 run coverage changed")

    summaries: list[dict[str, Any]] = []
    union: OrderedDict[str, list[str]] = OrderedDict()
    event_occurrences = 0
    for partition in queries.SCHEDULE_IDS:
        event = planned[partition]
        outcome = outcomes[partition]
        query = queries.EVENT_QUERIES[partition]
        require(event.get("query") == query, f"Changed current query for {partition}")
        require(event.get("query_sha256") == digest_text(query), f"Wrong query hash for {partition}")
        require(query.count("*") == 3, f"Wrong wildcard count for {partition}")
        require(re.search(r"\b(?:NEAR|ONEAR)(?:/\d+)?\b", query, re.I) is None, f"Proximity in {partition}")
        require(outcome.get("status") == "strict_two_pass_complete", f"Incomplete {partition}")
        accepted = outcome.get("accepted_output")
        require(isinstance(accepted, str), f"Missing accepted output for {partition}")
        output = COMPENDEX_008 / accepted
        value = load(output)
        require(
            digest_file(output) == outcome.get("accepted_output_sha256"),
            f"Changed source output for {partition}",
        )
        metadata = value.get("output_metadata")
        context = value.get("pilot_context")
        require(isinstance(metadata, dict) and isinstance(context, dict), f"Missing metadata for {partition}")
        require(value.get("requested_query") == query, f"Wrong query echo for {partition}")
        prisma = metadata.get("prisma_search_run")
        strategy = prisma.get("strategy") if isinstance(prisma, dict) else None
        limits = strategy.get("limits") if isinstance(strategy, dict) else None
        controls = context.get("controls")
        strict = context.get("strict_complete_comparison_receipt")
        require(
            isinstance(strategy, dict)
            and strategy.get("requested_query") == query
            and strategy.get("executed_query_provenance") == "source_observed",
            f"No exact source query evidence for {partition}",
        )
        require(
            strategy.get("databases") == ["compendex", "inspec"],
            f"Wrong databases for {partition}",
        )
        require(
            isinstance(controls, dict)
            and controls.get("database_mask") == "3"
            and controls.get("database_selection") == ["compendex", "inspec"],
            f"Wrong paired controls for {partition}",
        )
        require(
            controls.get("autostemming") == "off"
            and controls.get("Published") == {"start": 2011, "end": 2026}
            and controls.get("sort") == "Date (Oldest)"
            and controls.get("document_type") == "not_applied"
            and controls.get("open_access") == "not_applied",
            f"Wrong search controls for {partition}",
        )
        require(
            isinstance(limits, dict)
            and limits.get("document_type_filter") is None
            and limits.get("result_facets") == [],
            f"Unexpected source refinement for {partition}",
        )
        require(
            context.get("status") == "strict_two_pass_complete"
            and isinstance(strict, dict)
            and strict.get("sequence_match") is True,
            f"Strict mismatch for {partition}",
        )
        ids = inspec_ids(value)
        projected = context.get("projections", {}).get("inspec", {})
        require(ids == projected.get("ordered_stable_accessions"), f"Wrong Inspec projection for {partition}")
        require(len(ids) == projected.get("source_total"), f"Wrong Inspec total for {partition}")
        linked = linked_partitions.get(partition, {}).get("projections", {}).get("inspec", {})
        require(ids == linked.get("ordered_stable_accessions"), f"Wrong linked reconciliation for {partition}")
        screenshots = verify_screenshot_pair(output, metadata)
        event_occurrences += len(ids)
        for accession in ids:
            union.setdefault(accession, []).append(partition)
        summaries.append(
            {
                "partition_id": partition,
                "boolean_form": queries.BOOLEAN_FORMS[partition],
                "query_sha256": digest_text(query),
                "query_characters": len(query),
                "wildcard_count": 3,
                "proximity_operator_count": 0,
                "paired_artifact": relative(output),
                "paired_artifact_sha256": digest_file(output),
                "paired_source_total": value.get("total"),
                "inspec_total": len(ids),
                "ordered_inspec_accessions": ids,
                "ordered_inspec_accessions_sha256": digest_text("\n".join(ids)),
                "strict_source_passes": 2,
                "mandatory_screenshots": screenshots,
                "status": "passed",
            }
        )

    source_union = reconciliation.get("database_unions", {}).get("inspec")
    require(isinstance(source_union, dict), "Pilot 008 lacks the Inspec union")
    source_entries = source_union.get("stable_accessions")
    require(isinstance(source_entries, list), "Pilot 008 lacks the Inspec accession ledger")
    source_union_map = OrderedDict(
        (item.get("stable_accession"), item.get("partitions"))
        for item in source_entries
        if isinstance(item, dict)
    )
    require(set(source_union_map) == set(union), "Inspec union membership changed")
    require(event_occurrences == source_union.get("event_occurrences") == 236, "Wrong Inspec occurrences")
    require(len(union) == source_union.get("unique_stable_accession_count") == 162, "Wrong Inspec union")
    for accession, partitions in union.items():
        require(
            set(partitions) == set(source_union_map[accession]),
            f"Wrong partition provenance for Inspec accession {accession}",
        )
    return summaries, {
        "adapter": adapter,
        "source_plan": {"path": relative(SOURCE_PLAN_008), "sha256": digest_file(SOURCE_PLAN_008)},
        "source_run_receipt": {"path": relative(SOURCE_RUN_008), "sha256": digest_file(SOURCE_RUN_008)},
        "source_assessment": {"path": relative(SOURCE_ASSESSMENT_008), "sha256": digest_file(SOURCE_ASSESSMENT_008)},
        "source_reconciliation": {
            "path": relative(SOURCE_RECONCILIATION_008),
            "sha256": digest_file(SOURCE_RECONCILIATION_008),
        },
        "event_occurrences": event_occurrences,
        "unique_accessions": len(union),
        "source_union_entries": [
            {"stable_accession": accession, "partitions": partitions}
            for accession, partitions in source_union_map.items()
        ],
        "source_union_sha256": source_union.get("ordered_union_sha256"),
    }


def build_outputs() -> dict[str, dict[str, Any]]:
    queries = load_queries()
    require(queries.PROTOCOL_COMMIT == PROTOCOL_COMMIT, "Query module protocol commit changed")
    require(tuple(queries.SCHEDULE_IDS) == ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"), "Schedule IDs changed")
    a1 = validate_a1_comparison()
    events, current = validate_current_schedule(queries)
    screenshot_validation = load(SCREENSHOT_VALIDATION)
    require(screenshot_validation.get("status") == "passed", "Adapter screenshot validation did not pass")
    require(
        screenshot_validation.get("adapter", {}).get("implementation_sha256")
        == current["adapter"]["implementation_sha256"],
        "Screenshot validation used a different adapter implementation",
    )
    created = now()

    linked_evidence = []
    for event in events:
        linked_evidence.append(
            {
                "partition_id": event["partition_id"],
                "paired_artifact": event["paired_artifact"],
                "paired_artifact_sha256": event["paired_artifact_sha256"],
                "query_sha256": event["query_sha256"],
                "inspec_total": event["inspec_total"],
                "strict_source_passes": event["strict_source_passes"],
                "screenshot_paths": [
                    event["mandatory_screenshots"]["search_page"]["path"],
                    event["mandatory_screenshots"]["results_page"]["path"],
                ],
            }
        )

    plan = {
        "schema_version": PLAN_SCHEMA,
        "pilot": PILOT,
        "source": "Inspec",
        "platform": "Elsevier Engineering Village",
        "created_at_utc": created,
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Assess Inspec's database-scoped projection of the already completed, "
            "predeclared paired current-schedule events and adopt every previously "
            "tested lossless population wildcard."
        ),
        "source_event_policy": {
            "new_source_events": 0,
            "reason": (
                "The fixed route selects Compendex and Inspec in one paired event. "
                "The linked events already searched Inspec and retained separate "
                "accessions, totals, strict receipts, and screenshots. Repeating them "
                "would duplicate source use."
            ),
            "original_plan_predeclared_before_source_use": True,
        },
        "acceptance_checks": [
            "Pilot 005 has complete equal literal and three-wildcard Inspec A1 accession sets.",
            "Pilot 008 covers all nine current Boolean partitions from protocol commit 3194156e90497186664260a8e86435e78d2e2aa1.",
            "Every current query contains the three tested population wildcards and no proximity operator.",
            "Every accepted event has two strict complete source passes and a separate Inspec projection.",
            "Every accepted event has a configured-search PNG and verified-results PNG beside its JSON, with matching receipts.",
            "Inspec totals and accessions remain separate from Compendex.",
            "No linked event is treated as a final search.",
        ],
        "controls": {
            "database_selection": ["compendex", "inspec"],
            "database_mask": "3",
            "Published": {"start": 2011, "end": 2026},
            "language_clause": "(English WN LA)",
            "autostemming": "off",
            "sort": "Date (Oldest)",
            "page_size": 25,
            "document_type": None,
            "open_access": None,
            "controlled_vocabulary": None,
        },
        "translation": {
            "ordinary_atom": '("ordinary token or ordered phrase" WN ALL)',
            "wildcard_replacements": list(WILDCARD_REPLACEMENTS),
            "wildcard_scope": "population block in all nine schedule entries",
            "other_terms": "literal",
            "proximity_operators": False,
            "pair_expansion": False,
            "schedule": queries.BOOLEAN_FORMS,
            "compound_definitions": queries.COMPOUND_DEFINITIONS,
        },
        "source_evidence": {
            "a1_comparison_plan": a1["source_plan"],
            "current_schedule_plan": current["source_plan"],
            "current_schedule_run_receipt": current["source_run_receipt"],
            "adapter_screenshot_validation": {
                "path": relative(SCREENSHOT_VALIDATION),
                "sha256": digest_file(SCREENSHOT_VALIDATION),
            },
        },
        "events": linked_evidence,
    }

    reconciliation = {
        "schema_version": RECONCILIATION_SCHEMA,
        "pilot": PILOT,
        "source": "Inspec",
        "platform": "Elsevier Engineering Village",
        "created_at_utc": created,
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "identity": "Inspec stable accession",
        "database_scope_rule": (
            "This ledger contains only records labelled Inspec (Engineering Village). "
            "No Compendex accession or total is combined with it."
        ),
        "partition_order": list(queries.SCHEDULE_IDS),
        "event_occurrences": current["event_occurrences"],
        "unique_stable_accession_count": current["unique_accessions"],
        "exceeds_100": current["unique_accessions"] > 100,
        "source_ordered_union_sha256": current["source_union_sha256"],
        "partitions": {
            event["partition_id"]: {
                "source_total": event["inspec_total"],
                "query_sha256": event["query_sha256"],
                "ordered_stable_accessions": event["ordered_inspec_accessions"],
                "ordered_stable_accessions_sha256": event[
                    "ordered_inspec_accessions_sha256"
                ],
            }
            for event in events
        },
        "stable_accessions": current["source_union_entries"],
        "linked_source_reconciliation": current["source_reconciliation"],
    }

    approval = {
        "schema_version": APPROVAL_SCHEMA,
        "pilot": PILOT,
        "source": "Inspec",
        "platform": "Elsevier Engineering Village",
        "decided_at_utc": created,
        "protocol_commit": PROTOCOL_COMMIT,
        "status": "approved",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decision_authority": (
            "Reviewer instruction to pilot the current schedule using wildcards "
            "whenever possible"
        ),
        "decision": "approve_three_family_population_wildcards_for_all_schedule_entries",
        "approved_schedule_entries": list(queries.SCHEDULE_IDS),
        "approved_population_replacements": list(WILDCARD_REPLACEMENTS),
        "basis": {
            "source_semantics": (
                "Engineering Village documents terminal * as zero-or-more-character truncation."
            ),
            "inspec_a1_complete_set_comparison": {
                "literal_total": a1["literal_total"],
                "wildcard_total": a1["wildcard_total"],
                "sets_equal": a1["sets_equal"],
                "literal_missing_from_wildcard": [],
                "wildcard_only_accessions": [],
                "source_assessment": a1["source_assessment"],
            },
            "current_schedule_execution": {
                "all_nine_partitions": True,
                "strict_source_passes": sum(event["strict_source_passes"] for event in events),
                "mandatory_screenshots": sum(
                    len(event["mandatory_screenshots"]) for event in events
                ),
                "inspec_event_occurrences": current["event_occurrences"],
                "inspec_unique_accessions": current["unique_accessions"],
                "source_assessment": current["source_assessment"],
            },
        },
        "translation_rule": (
            "Use the three unquoted trailing-wildcard ALL atoms in every F(P) block. "
            "Preserve every other population literal and every term in every other block."
        ),
        "boundaries": {
            "additional_asterisk_forms": "not accepted",
            "question_mark_wildcards": "not accepted",
            "manual_dollar_stemming": "not accepted",
            "autostemming": "off",
            "controlled_vocabulary_supplement": "not accepted",
            "database_scope": "Inspec only",
            "compendex_projection": "retained separately",
            "final_search": False,
        },
    }

    plan_path = SEARCH_ROOT / "linked-evidence-plan.json"
    reconciliation_path = SEARCH_ROOT / "reconciliation.json"
    approval_path = SEARCH_ROOT / "source-translation-approval.json"
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "pilot": PILOT,
        "source": "Inspec",
        "platform": "Elsevier Engineering Village",
        "created_at_utc": created,
        "status": "passed",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "method": (
            "Source-specific secondary assessment of immutable database-scoped "
            "Inspec projections from predeclared paired Engineering Village events."
        ),
        "new_source_events": 0,
        "linked_evidence_plan": {
            "path": relative(plan_path),
            "sha256": digest_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n"),
        },
        "adapter_contract": {
            **current["adapter"],
            "validation_artifact": relative(SCREENSHOT_VALIDATION),
            "validation_artifact_sha256": digest_file(SCREENSHOT_VALIDATION),
            "offline_tests_recorded_passed": screenshot_validation.get(
                "offline_validation", {}
            ).get("tests_passed"),
            "bounded_strict_paired_live_check_passed": True,
        },
        "a1_wildcard_comparison": a1,
        "checks": {
            "all_nine_current_partitions": len(events) == 9,
            "protocol_commit_pinned": True,
            "no_proximity_operator_in_any_query": True,
            "three_population_wildcards_in_every_query": True,
            "strict_source_passes": sum(event["strict_source_passes"] for event in events),
            "expected_strict_source_passes": 18,
            "mandatory_screenshots": sum(len(event["mandatory_screenshots"]) for event in events),
            "expected_mandatory_screenshots": 18,
            "screenshots_beside_json": True,
            "screenshot_opt_out_available": False,
            "separate_inspec_projection": True,
            "a1_literal_wildcard_sets_equal": a1["sets_equal"],
            "final_search": False,
        },
        "events": events,
        "database_union": {
            "event_occurrences": current["event_occurrences"],
            "unique_stable_accession_count": current["unique_accessions"],
            "exceeds_100": current["unique_accessions"] > 100,
            "reconciliation": relative(reconciliation_path),
            "reconciliation_sha256": digest_text(
                json.dumps(reconciliation, indent=2, ensure_ascii=False) + "\n"
            ),
        },
        "wildcard_decision": {
            "status": "approved",
            "approval": relative(approval_path),
            "approval_sha256": digest_text(
                json.dumps(approval, indent=2, ensure_ascii=False) + "\n"
            ),
            "approved_population_wildcard_count": 3,
            "replaced_literal_count": 8,
            "scope": "all nine main schedule entries",
        },
        "decision": (
            "Accept the current no-proximity Inspec translation with the three "
            "tested population wildcards. The linked paired route is ready for a "
            "separate final search event. This pilot is not a final search."
        ),
        "errors": [],
    }

    validation = {
        "schema_version": VALIDATION_SCHEMA,
        "pilot": PILOT,
        "source": "Inspec",
        "created_at_utc": created,
        "status": "passed",
        "protocol_commit": PROTOCOL_COMMIT,
        "checks": {
            "linked_evidence_plan": True,
            "immutable_source_artifact_hashes": True,
            "all_nine_current_queries": True,
            "no_proximity_operators": True,
            "wildcard_translation": True,
            "exact_source_query_echoes": True,
            "paired_database_controls": True,
            "separate_inspec_accessions": True,
            "strict_two_pass_capture": True,
            "mandatory_sibling_screenshots": True,
            "no_screenshot_opt_out": True,
            "a1_complete_set_equality": True,
            "over_100_accession_ledger": True,
            "non_mergeable_pilot_boundary": True,
        },
        "artifacts": {},
        "guideline": relative(GUIDELINE),
        "errors": [],
    }
    return {
        "linked-evidence-plan.json": plan,
        "reconciliation.json": reconciliation,
        "source-translation-approval.json": approval,
        "assessment.json": assessment,
        "validation-report.json": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=SEARCH_ROOT)
    args = parser.parse_args()
    outputs = build_outputs()
    for name in (
        "linked-evidence-plan.json",
        "reconciliation.json",
        "source-translation-approval.json",
        "assessment.json",
    ):
        write_new(args.output_root / name, outputs[name])
    validation = outputs["validation-report.json"]
    validation["artifacts"] = {
        name: {
            "path": relative(args.output_root / name),
            "sha256": digest_file(args.output_root / name),
        }
        for name in (
            "linked-evidence-plan.json",
            "reconciliation.json",
            "source-translation-approval.json",
            "assessment.json",
        )
    }
    write_new(args.output_root / "validation-report.json", validation)
    print(
        json.dumps(
            {
                "status": "passed",
                "events": 9,
                "inspec_occurrences": 236,
                "inspec_unique_accessions": 162,
                "mandatory_screenshots": 18,
                "new_source_events": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
