#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Execute the two predeclared paired wildcard comparison events once."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import queries

ADAPTER_DIR = Path.home() / "agent-tools/internet/skills/browser/scripts"
ADAPTER_ENTRYPOINT = ADAPTER_DIR / "search_compendex_inspec.py"
ADAPTER_IMPLEMENTATION = ADAPTER_DIR / "_engineering_village_search.py"
SOURCE_LABELS = {
    "compendex": "Compendex (Engineering Village)",
    "inspec": "Inspec (Engineering Village)",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
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


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "compendex_pilot005_paired_adapter", ADAPTER_ENTRYPOINT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load the paired adapter at {ADAPTER_ENTRYPOINT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_plan(plan: dict[str, Any], plan_path: Path) -> list[dict[str, Any]]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != "engineering-village-wildcard-pilot-plan/v1"
        or plan.get("pilot") != "005"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or not isinstance(events, list)
        or len(events) != 2
    ):
        raise RuntimeError("Unexpected Compendex Pilot 005 plan")
    expected_ids = list(queries.EVENT_QUERIES)
    if [event.get("event_id") for event in events] != expected_ids:
        raise RuntimeError("The source-event order changed")
    for event in events:
        event_id = event["event_id"]
        query = queries.EVENT_QUERIES[event_id]
        if event.get("query") != query or event.get("query_sha256") != digest_text(query):
            raise RuntimeError(f"The predeclared query changed for {event_id}")
        if event.get("query_characters") != len(query):
            raise RuntimeError(f"The predeclared query length changed for {event_id}")
        if event.get("year_start") != 2011 or event.get("year_end") != 2026:
            raise RuntimeError(f"The source year window changed for {event_id}")
        output = event.get("output")
        if not isinstance(output, str) or Path(output).is_absolute() or ".." in Path(output).parts:
            raise RuntimeError(f"The output path is unsafe for {event_id}")
    adapter = plan.get("adapter", {})
    expected_hashes = {
        "entrypoint_sha256": digest_file(ADAPTER_ENTRYPOINT),
        "implementation_sha256": digest_file(ADAPTER_IMPLEMENTATION),
    }
    for key, value in expected_hashes.items():
        if adapter.get(key) != value:
            raise RuntimeError(f"The paired adapter changed after predeclaration: {key}")
    source_scripts = plan.get("source_affecting_scripts", {})
    repository_root = plan_path.resolve().parents[7]
    for relative, expected_hash in source_scripts.items():
        path = repository_root / relative
        if not path.is_file() or digest_file(path) != expected_hash:
            raise RuntimeError(f"A source-affecting pilot script changed: {relative}")
    return events


def source_projection(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    projections = {
        key: {"source_label": label, "source_total": 0, "ordered_stable_accessions": []}
        for key, label in SOURCE_LABELS.items()
    }
    label_to_key = {label: key for key, label in SOURCE_LABELS.items()}
    for record in results:
        if not isinstance(record, dict):
            raise RuntimeError("The adapter returned a non-object record")
        source = record.get("source")
        database = label_to_key.get(source)
        paper_id = record.get("paperId")
        if database is None:
            raise RuntimeError(f"The paired result has an unexpected source label: {source!r}")
        if not isinstance(paper_id, str) or not paper_id.strip():
            raise RuntimeError("A paired record lacks a stable accession")
        projections[database]["ordered_stable_accessions"].append(paper_id)
    for database, projection in projections.items():
        ids = projection["ordered_stable_accessions"]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"The {database} projection repeats a stable accession")
        projection["source_total"] = len(ids)
        projection["ordered_stable_accessions_sha256"] = digest_text("\n".join(ids))
    return projections


def validate_strict_result(adapter: Any, event: dict[str, Any], result: Any) -> dict[str, Any]:
    adapter.assert_strict_complete_publication(result)
    if not isinstance(result, dict):
        raise RuntimeError("The strict adapter result is not a mapping")
    metadata = result.get("output_metadata")
    results = result.get("results")
    total = result.get("total")
    if not isinstance(metadata, dict) or not isinstance(results, list):
        raise RuntimeError("The strict adapter result lacks metadata or records")
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise RuntimeError("The paired source total is invalid")
    if len(results) != total:
        raise RuntimeError("The paired record count does not equal the source total")
    if result.get("requested_query") != event["query"]:
        raise RuntimeError("The adapter did not retain the requested query")
    if metadata.get("observed_exact_query_echo") is not True:
        raise RuntimeError("The adapter did not observe an exact query echo")
    if metadata.get("databases") != ["compendex", "inspec"]:
        raise RuntimeError("The adapter did not retain the paired database selection")
    if metadata.get("database_mask") != "3":
        raise RuntimeError("The paired database mask changed")
    if metadata.get("autostemming_off_observed") is not True:
        raise RuntimeError("The source did not confirm autostemming off")
    if metadata.get("year_range_selected_observed") is not True:
        raise RuntimeError("The source did not confirm the Published control")
    if metadata.get("last_update_selected_observed") is not False:
        raise RuntimeError("The source did not confirm Updates inactive")
    if metadata.get("source_year_control_values") != {"start": "2011", "end": "2026"}:
        raise RuntimeError("The source year readback changed")
    if metadata.get("sort") != "Date (Oldest)" or metadata.get("observed_page_size") != 25:
        raise RuntimeError("The result sort or page-size readback changed")
    if metadata.get("document_type_filter") is not None or metadata.get("result_facets") != []:
        raise RuntimeError("An undeclared result refinement was applied")
    if metadata.get("strict_complete_pass_count") != 2:
        raise RuntimeError("The adapter did not complete two strict passes")
    strict = metadata.get("strict_complete_comparison_receipt")
    if not isinstance(strict, dict) or strict.get("sequence_match") is not True:
        raise RuntimeError("The strict ordered-ID comparison is absent")
    stable_counts = strict.get("stable_counts")
    if not isinstance(stable_counts, dict) or stable_counts.get("portal_total") != total:
        raise RuntimeError("The strict source total did not reconcile")
    projections = source_projection(results)
    expected_by_database = stable_counts.get("source_export_ids_seen_by_database")
    observed_by_database = {
        key: value["source_total"] for key, value in projections.items()
    }
    if expected_by_database != observed_by_database:
        raise RuntimeError("The strict database projections did not reconcile")
    return {
        "metadata": metadata,
        "results": results,
        "strict_receipt": strict,
        "projections": projections,
    }


def compact_pilot_artifact(
    adapter: Any,
    event: dict[str, Any],
    result: Any,
    evidence: dict[str, Any],
    started_at: str,
    completed_at: str,
    plan: dict[str, Any],
) -> dict[str, Any]:
    implementation = adapter._implementation
    compact = implementation.compact_search_result_for_output(result)
    compact["do_not_merge"] = True
    metadata = compact.setdefault("output_metadata", {})
    metadata["merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["pilot_non_mergeable_reason"] = (
        "Compendex Pilot 005 wildcard comparison. This is not a final search."
    )
    compact["pilot_context"] = {
        "schema_version": "engineering-village-wildcard-pilot-cell/v1",
        "pilot": "005",
        "event_id": event["event_id"],
        "variant": event["variant"],
        "schedule_id": "A1",
        "status": "strict_two_pass_complete",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "query_sha256": event["query_sha256"],
        "query_characters": event["query_characters"],
        "adapter": {
            "id": adapter.ADAPTER_ID,
            "version": adapter.ADAPTER_VERSION,
            "entrypoint_sha256": plan["adapter"]["entrypoint_sha256"],
            "implementation_sha256": plan["adapter"]["implementation_sha256"],
        },
        "controls": {
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
        },
        "strict_complete_comparison_receipt": evidence["strict_receipt"],
        "paired_source_total": result["total"],
        "projections": evidence["projections"],
        "native_ris": {
            "used_for_every_record_in_both_strict_passes": True,
            "raw_batches_persisted": False,
            "private_path_persisted": False,
        },
    }
    return compact


def run_event(adapter: Any, event: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    started_at = now()
    result = adapter.search_compendex_inspec(
        event["query"],
        limit=event["limit"],
        year_start=event["year_start"],
        year_end=event["year_end"],
        max_pages=event["max_pages"],
        timeout_seconds=event["timeout_seconds"],
        page_delay_seconds=event["page_delay_seconds"],
        require_complete=True,
        prisma_context={
            "run_id": f"slr1-ev-p005-{event['event_id']}",
            "run_id_provenance": "pilot_event_plan",
            "review_id": "slr1",
            "strategy_reference": "slr1-compendex-a1-wildcard-pilot-v1",
            "strategy_version": event["query_sha256"],
            "phase": "identification",
            "coverage_scope": "partition",
            "partition_id": "A1",
            "partition_label": f"A1 {event['variant']}",
            "partition_description": event["purpose"],
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": plan["adapter"]["implementation_sha256"],
            "script_hash_provenance": "predeclared_local_file_sha256",
        },
    )
    completed_at = now()
    evidence = validate_strict_result(adapter, event, result)
    return compact_pilot_artifact(
        adapter, event, result, evidence, started_at, completed_at, plan
    )


def safe_error(adapter: Any | None, error: BaseException) -> str:
    if adapter is not None:
        implementation = getattr(adapter, "_implementation", None)
        cleaner = getattr(implementation, "safe_error_message", None)
        if callable(cleaner) and isinstance(error, Exception):
            return cleaner(error)
    return " ".join(str(error).split())[:500]


def run(plan_path: Path, pilot_root: Path, receipt_path: Path, delay_seconds: float) -> int:
    plan = load(plan_path)
    events = validate_plan(plan, plan_path)
    adapter = load_adapter()
    if adapter.ADAPTER_VERSION != plan["adapter"]["version"]:
        raise RuntimeError("The adapter version changed after predeclaration")

    started_at = now()
    outcomes: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        output = pilot_root / "searches" / event["output"]
        failure = output.with_name(f"{output.stem}.NON_MERGEABLE_FAILURE.json")
        if output.exists() or failure.exists():
            raise RuntimeError(f"Refusing to reuse or overwrite {output}")
        print(f"Running {event['event_id']}", flush=True)
        event_started = now()
        try:
            artifact = run_event(adapter, event, plan)
            write_new(output, artifact)
            outcome = {
                "event_id": event["event_id"],
                "status": "strict_two_pass_complete",
                "started_at_utc": event_started,
                "completed_at_utc": now(),
                "output": str(output.relative_to(pilot_root)),
                "output_sha256": digest_file(output),
                "paired_source_total": artifact["total"],
                "projections": artifact["pilot_context"]["projections"],
                "do_not_merge": True,
            }
            outcomes.append(outcome)
        except BaseException as error:
            failure_value = {
                "schema_version": "engineering-village-wildcard-pilot-failure/v1",
                "pilot": "005",
                "event_id": event["event_id"],
                "status": "error",
                "do_not_merge": True,
                "merge_eligible": False,
                "protocol_commit": queries.PROTOCOL_COMMIT,
                "started_at_utc": event_started,
                "failed_at_utc": now(),
                "error_type": type(error).__name__,
                "error": safe_error(adapter, error),
                "source_total": None,
                "records_retained": 0,
                "stop_rule": "Stop the pilot. Do not retry or infer a count.",
            }
            write_new(failure, failure_value)
            outcomes.append(
                {
                    "event_id": event["event_id"],
                    "status": "error",
                    "started_at_utc": event_started,
                    "completed_at_utc": now(),
                    "output": str(failure.relative_to(pilot_root)),
                    "output_sha256": digest_file(failure),
                    "paired_source_total": None,
                    "do_not_merge": True,
                }
            )
            receipt = {
                "schema_version": "engineering-village-wildcard-pilot-run-receipt/v1",
                "pilot": "005",
                "status": "stopped_on_predeclared_failure",
                "do_not_merge": True,
                "protocol_commit": queries.PROTOCOL_COMMIT,
                "started_at_utc": started_at,
                "completed_at_utc": now(),
                "event_plan": str(plan_path),
                "predeclared_event_count": len(events),
                "completed_event_count": len(outcomes),
                "outcomes": outcomes,
            }
            write_new(receipt_path, receipt)
            raise
        if index + 1 < len(events) and delay_seconds > 0:
            time.sleep(delay_seconds)

    receipt = {
        "schema_version": "engineering-village-wildcard-pilot-run-receipt/v1",
        "pilot": "005",
        "status": "complete",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "event_plan": str(plan_path),
        "predeclared_event_count": len(events),
        "completed_event_count": len(outcomes),
        "successful_event_count": len(outcomes),
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    args = parser.parse_args()
    try:
        return run(args.event_plan, args.pilot_root, args.receipt, args.delay_seconds)
    except Exception as error:
        print(" ".join(str(error).split())[:500], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
