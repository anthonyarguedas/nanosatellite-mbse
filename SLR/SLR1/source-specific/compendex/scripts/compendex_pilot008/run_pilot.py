#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Execute the nine predeclared Compendex Pilot 008 events once."""

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

PLAN_SCHEMA = "engineering-village-readiness-pilot-plan/v1"
RUN_SCHEMA = "engineering-village-readiness-pilot-run/v1"
CELL_SCHEMA = "engineering-village-readiness-pilot-cell/v1"
FAILURE_SCHEMA = "engineering-village-readiness-pilot-failure/v1"
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
        "compendex_pilot008_paired_adapter", ADAPTER_ENTRYPOINT
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
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != "008"
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("adapter", {}).get("version") != "16"
        or not isinstance(events, list)
        or len(events) != len(queries.RUN_ORDER)
    ):
        raise RuntimeError("Unexpected Compendex Pilot 008 plan")
    if [event.get("event_id") for event in events] != list(queries.RUN_ORDER):
        raise RuntimeError("The source-event order changed")
    for event in events:
        partition = event.get("partition_id")
        query = queries.EVENT_QUERIES.get(partition)
        if not isinstance(query, str) or event.get("query") != query:
            raise RuntimeError(f"The predeclared query changed for {partition}")
        if event.get("query_sha256") != digest_text(query):
            raise RuntimeError(f"The predeclared query hash changed for {partition}")
        if event.get("query_characters") != len(query):
            raise RuntimeError(f"The predeclared query length changed for {partition}")
        if query.count("*") != 3 or queries.PROXIMITY_OPERATOR_RE.search(query):
            raise RuntimeError(f"The approved translation changed for {partition}")
        if event.get("year_start") != 2011 or event.get("year_end") != 2026:
            raise RuntimeError(f"The source year window changed for {partition}")
        attempts = event.get("attempts")
        if (
            event.get("max_fresh_attempts") != 3
            or not isinstance(attempts, list)
            or len(attempts) != 3
        ):
            raise RuntimeError(f"The fresh-attempt plan changed for {partition}")
        for ordinal, attempt in enumerate(attempts, start=1):
            output = attempt.get("output")
            failure = attempt.get("failure_output")
            if (
                attempt.get("attempt_ordinal") != ordinal
                or not isinstance(output, str)
                or not isinstance(failure, str)
                or Path(output).is_absolute()
                or Path(failure).is_absolute()
                or ".." in Path(output).parts
                or ".." in Path(failure).parts
            ):
                raise RuntimeError(
                    f"An attempt output path is unsafe for {partition} attempt {ordinal}"
                )
    adapter = plan.get("adapter", {})
    expected_hashes = {
        "entrypoint_sha256": digest_file(ADAPTER_ENTRYPOINT),
        "implementation_sha256": digest_file(ADAPTER_IMPLEMENTATION),
    }
    for key, value in expected_hashes.items():
        if adapter.get(key) != value:
            raise RuntimeError(
                f"The paired adapter changed after predeclaration: {key}"
            )
    source_scripts = plan.get("source_affecting_scripts", {})
    repository_root = plan_path.resolve().parents[7]
    if not isinstance(source_scripts, dict) or not source_scripts:
        raise RuntimeError("The plan does not pin its source-affecting scripts")
    for relative, expected_hash in source_scripts.items():
        path = repository_root / relative
        if not path.is_file() or digest_file(path) != expected_hash:
            raise RuntimeError(f"A source-affecting pilot script changed: {relative}")
    return events


def source_projection(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    projections = {
        key: {
            "source_label": label,
            "source_total": 0,
            "ordered_stable_accessions": [],
        }
        for key, label in SOURCE_LABELS.items()
    }
    label_to_key = {label: key for key, label in SOURCE_LABELS.items()}
    for record in results:
        if not isinstance(record, dict):
            raise RuntimeError("The adapter returned a non-object record")
        database = label_to_key.get(record.get("source"))
        paper_id = record.get("paperId")
        if database is None:
            raise RuntimeError(
                f"The paired result has an unexpected source label: {record.get('source')!r}"
            )
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


def screenshot_summary(paths: Any, screenshots: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key, path in (
        ("search_page", paths.search_page),
        ("results_page", paths.results_page),
    ):
        evidence = screenshots.get(key, {})
        summary[key] = {
            "file_name": path.name,
            "sha256": evidence.get("sha256"),
            "width": evidence.get("width"),
            "height": evidence.get("height"),
            "account_elements_masked": evidence.get("account_elements_masked"),
            "email_elements_masked": evidence.get("email_elements_masked"),
            "exists": path.is_file(),
            "hash_matches": (
                path.is_file() and evidence.get("sha256") == digest_file(path)
            ),
        }
    return summary


def validate_strict_result(
    adapter: Any,
    event: dict[str, Any],
    result: Any,
    screenshot_paths: Any,
) -> dict[str, Any]:
    adapter.assert_strict_complete_publication(result)
    adapter.assert_automatic_screenshot_evidence(result, screenshot_paths)
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
    if (
        metadata.get("sort") != "Date (Oldest)"
        or metadata.get("observed_page_size") != 25
    ):
        raise RuntimeError("The result sort or page-size readback changed")
    if (
        metadata.get("document_type_filter") is not None
        or metadata.get("result_facets") != []
    ):
        raise RuntimeError("An undeclared result refinement was applied")
    if metadata.get("strict_complete_pass_count") != 2:
        raise RuntimeError("The adapter did not complete two strict passes")
    strict = metadata.get("strict_complete_comparison_receipt")
    if not isinstance(strict, dict) or strict.get("sequence_match") is not True:
        raise RuntimeError("The strict ordered-ID comparison is absent")
    stable_counts = strict.get("stable_counts")
    if (
        not isinstance(stable_counts, dict)
        or stable_counts.get("portal_total") != total
    ):
        raise RuntimeError("The strict source total did not reconcile")
    projections = source_projection(results)
    expected_by_database = stable_counts.get("source_export_ids_seen_by_database")
    observed_by_database = {
        key: value["source_total"] for key, value in projections.items()
    }
    if expected_by_database != observed_by_database:
        raise RuntimeError("The strict database projections did not reconcile")
    screenshots = metadata.get("screenshots")
    if not isinstance(screenshots, dict):
        raise RuntimeError("The mandatory screenshot receipt is absent")
    summary = screenshot_summary(screenshot_paths, screenshots)
    if not all(item["exists"] and item["hash_matches"] for item in summary.values()):
        raise RuntimeError("A mandatory screenshot does not match its receipt")
    return {
        "metadata": metadata,
        "results": results,
        "strict_receipt": strict,
        "projections": projections,
        "screenshots": screenshots,
        "screenshot_summary": summary,
    }


def compact_pilot_artifact(
    adapter: Any,
    event: dict[str, Any],
    result: dict[str, Any],
    evidence: dict[str, Any],
    started_at: str,
    completed_at: str,
    plan: dict[str, Any],
    screenshot_paths: Any,
    attempt_ordinal: int,
) -> dict[str, Any]:
    compact = adapter._implementation.compact_search_result_for_output(result)
    compact["do_not_merge"] = True
    metadata = compact.setdefault("output_metadata", {})
    metadata["merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["pilot_non_mergeable_reason"] = (
        "Compendex Pilot 008 readiness evidence. This is not a final search."
    )
    metadata["screenshots"] = evidence["screenshots"]
    compact["pilot_context"] = {
        "schema_version": CELL_SCHEMA,
        "pilot": "008",
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "attempt_ordinal": attempt_ordinal,
        "boolean_form": event["boolean_form"],
        "changed_definition_since_pilot003": event["changed_definition_since_pilot003"],
        "status": "strict_two_pass_complete",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "query_sha256": event["query_sha256"],
        "query_characters": event["query_characters"],
        "wildcard_count": 3,
        "proximity_operator_count": 0,
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
        "screenshots": evidence["screenshot_summary"],
        "native_ris": {
            "used_for_every_record_in_both_strict_passes": True,
            "raw_batches_persisted": False,
            "private_path_persisted": False,
        },
    }
    adapter.assert_automatic_screenshot_evidence(compact, screenshot_paths)
    return compact


def run_event(
    adapter: Any,
    event: dict[str, Any],
    plan: dict[str, Any],
    output: Path,
    attempt_ordinal: int,
) -> dict[str, Any]:
    paths = adapter.screenshot_paths_for_output(output)
    started_at = now()
    result = adapter.search_compendex_inspec(
        event["query"],
        limit=event["limit"],
        year_start=event["year_start"],
        year_end=event["year_end"],
        max_pages=event["max_pages"],
        timeout_seconds=event["timeout_seconds"],
        page_delay_seconds=event["page_delay_seconds"],
        screenshot_paths=paths,
        require_complete=True,
        prisma_context={
            "run_id": f"slr1-ev-p008-{event['event_id']}-attempt-{attempt_ordinal:02d}",
            "run_id_provenance": "pilot_event_plan",
            "review_id": "slr1",
            "strategy_reference": "slr1-compendex-current-readiness-pilot-v1",
            "strategy_version": event["query_sha256"],
            "phase": "identification",
            "coverage_scope": "partition",
            "partition_id": event["partition_id"],
            "partition_label": event["partition_id"],
            "partition_description": (
                f"{event['purpose']} Fresh attempt {attempt_ordinal} of "
                f"{event['max_fresh_attempts']}."
            ),
            "adapter_id": adapter.ADAPTER_ID,
            "adapter_version": adapter.ADAPTER_VERSION,
            "script_sha256": plan["adapter"]["implementation_sha256"],
            "script_hash_provenance": "predeclared_local_file_sha256",
        },
    )
    completed_at = now()
    evidence = validate_strict_result(adapter, event, result, paths)
    return compact_pilot_artifact(
        adapter,
        event,
        result,
        evidence,
        started_at,
        completed_at,
        plan,
        paths,
        attempt_ordinal,
    )


def safe_error(adapter: Any | None, error: BaseException) -> str:
    if adapter is not None:
        implementation = getattr(adapter, "_implementation", None)
        cleaner = getattr(implementation, "safe_error_message", None)
        if callable(cleaner) and isinstance(error, Exception):
            return cleaner(error)
    return " ".join(str(error).split())[:500]


def image_state(path: Path) -> dict[str, Any]:
    return {
        "file_name": path.name,
        "exists": path.is_file(),
        "sha256": digest_file(path) if path.is_file() else None,
    }


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    delay_seconds: float,
    retry_delay_seconds: float,
) -> int:
    plan = load(plan_path)
    events = validate_plan(plan, plan_path)
    adapter = load_adapter()
    if (
        adapter.ADAPTER_VERSION != "16"
        or adapter.ADAPTER_VERSION != plan["adapter"]["version"]
    ):
        raise RuntimeError("Pilot 008 requires the pinned adapter v16")
    if receipt_path.exists() or receipt_path.is_symlink():
        raise RuntimeError(f"Refusing to overwrite {receipt_path}")

    started_at = now()
    outcomes: list[dict[str, Any]] = []
    retained_screenshot_count = 0
    total_attempt_count = 0
    for event_index, event in enumerate(events):
        event_started = now()
        attempt_outcomes: list[dict[str, Any]] = []
        accepted: dict[str, Any] | None = None
        for attempt_index, attempt in enumerate(event["attempts"]):
            ordinal = attempt["attempt_ordinal"]
            total_attempt_count += 1
            output = pilot_root / "searches" / attempt["output"]
            failure = pilot_root / "searches" / attempt["failure_output"]
            paths = adapter.screenshot_paths_for_output(output)
            expected_images = [
                str(paths.search_page.relative_to(pilot_root / "searches")),
                str(paths.results_page.relative_to(pilot_root / "searches")),
            ]
            if expected_images != attempt["screenshot_outputs"]:
                raise RuntimeError(
                    f"The screenshot plan changed for {event['event_id']} attempt {ordinal}"
                )
            occupied = [output, failure, paths.search_page, paths.results_page]
            if any(path.exists() or path.is_symlink() for path in occupied):
                raise RuntimeError(
                    f"Refusing to reuse an artifact for {event['event_id']} attempt {ordinal}"
                )
            output.parent.mkdir(parents=True, exist_ok=True)
            attempt_started = now()
            print(
                f"Running {event['event_id']} attempt {ordinal}/{event['max_fresh_attempts']}",
                flush=True,
            )
            try:
                artifact = run_event(adapter, event, plan, output, ordinal)
                if (
                    digest_file(ADAPTER_ENTRYPOINT)
                    != plan["adapter"]["entrypoint_sha256"]
                ):
                    raise RuntimeError(
                        "The paired adapter entrypoint changed during execution"
                    )
                if (
                    digest_file(ADAPTER_IMPLEMENTATION)
                    != plan["adapter"]["implementation_sha256"]
                ):
                    raise RuntimeError(
                        "The paired adapter implementation changed during execution"
                    )
                write_new(output, artifact)
                context = artifact["pilot_context"]
                attempt_outcome = {
                    "attempt_ordinal": ordinal,
                    "status": "strict_two_pass_complete",
                    "started_at_utc": attempt_started,
                    "completed_at_utc": now(),
                    "output": str(output.relative_to(pilot_root)),
                    "output_sha256": digest_file(output),
                    "paired_source_total": artifact["total"],
                    "projections": {
                        key: {
                            "source_total": value["source_total"],
                            "ordered_stable_accessions_sha256": value[
                                "ordered_stable_accessions_sha256"
                            ],
                        }
                        for key, value in context["projections"].items()
                    },
                    "screenshots": context["screenshots"],
                    "do_not_merge": True,
                }
                attempt_outcomes.append(attempt_outcome)
                accepted = attempt_outcome
                retained_screenshot_count += 2
                print(
                    json.dumps(
                        {
                            "event": event["event_id"],
                            "attempt": ordinal,
                            "paired_total": artifact["total"],
                            "compendex": context["projections"]["compendex"][
                                "source_total"
                            ],
                            "inspec": context["projections"]["inspec"]["source_total"],
                            "strict": True,
                            "screenshots": 2,
                        }
                    ),
                    flush=True,
                )
                break
            except Exception as error:
                diagnostics = getattr(error, "failure_diagnostics", None)
                if not isinstance(diagnostics, dict):
                    diagnostics = None
                image_receipts = {
                    "search_page": image_state(paths.search_page),
                    "results_page": image_state(paths.results_page),
                }
                retained_screenshot_count += sum(
                    item["exists"] for item in image_receipts.values()
                )
                exhausted = ordinal >= event["max_fresh_attempts"]
                failure_value = {
                    "schema_version": FAILURE_SCHEMA,
                    "pilot": "008",
                    "event_id": event["event_id"],
                    "partition_id": event["partition_id"],
                    "attempt_ordinal": ordinal,
                    "status": "error",
                    "do_not_merge": True,
                    "merge_eligible": False,
                    "protocol_commit": queries.PROTOCOL_COMMIT,
                    "started_at_utc": attempt_started,
                    "failed_at_utc": now(),
                    "error_type": type(error).__name__,
                    "error_code": getattr(error, "code", None),
                    "error": safe_error(adapter, error),
                    "safe_failure_diagnostics": diagnostics,
                    "source_total": None,
                    "compendex_total": None,
                    "inspec_total": None,
                    "records_retained": 0,
                    "screenshots": image_receipts,
                    "disposition": (
                        "Stop after the third failed fresh attempt."
                        if exhausted
                        else "Wait, then start the exact query as a fresh whole attempt."
                    ),
                    "prohibitions": (
                        "Do not narrow, infer a count, resume a pass, or reuse partial records."
                    ),
                }
                write_new(failure, failure_value)
                failure_outcome = {
                    "attempt_ordinal": ordinal,
                    "status": "error",
                    "started_at_utc": attempt_started,
                    "completed_at_utc": now(),
                    "output": str(failure.relative_to(pilot_root)),
                    "output_sha256": digest_file(failure),
                    "error_code": getattr(error, "code", None),
                    "paired_source_total": None,
                    "screenshots": image_receipts,
                    "do_not_merge": True,
                }
                attempt_outcomes.append(failure_outcome)
                print(
                    json.dumps(
                        {
                            "event": event["event_id"],
                            "attempt": ordinal,
                            "status": "error",
                            "error_code": failure_outcome["error_code"],
                            "will_retry": not exhausted,
                        }
                    ),
                    flush=True,
                )
                if exhausted:
                    outcomes.append(
                        {
                            "event_id": event["event_id"],
                            "partition_id": event["partition_id"],
                            "status": "failed_after_fresh_attempts",
                            "started_at_utc": event_started,
                            "completed_at_utc": now(),
                            "accepted_attempt_ordinal": None,
                            "accepted_output": None,
                            "attempts": attempt_outcomes,
                            "do_not_merge": True,
                        }
                    )
                    receipt = {
                        "schema_version": RUN_SCHEMA,
                        "pilot": "008",
                        "source": "Compendex with a retained paired Inspec projection",
                        "status": "stopped_after_attempt_limit",
                        "success": False,
                        "diagnostic_only": True,
                        "do_not_merge": True,
                        "protocol_commit": queries.PROTOCOL_COMMIT,
                        "adapter": plan["adapter"],
                        "started_at_utc": started_at,
                        "completed_at_utc": now(),
                        "event_plan": str(plan_path),
                        "event_plan_sha256": digest_file(plan_path),
                        "predeclared_event_count": len(events),
                        "completed_event_count": len(outcomes),
                        "successful_event_count": sum(
                            item["status"] == "strict_two_pass_complete"
                            for item in outcomes
                        ),
                        "total_attempt_count": total_attempt_count,
                        "accepted_strict_source_pass_count": sum(
                            item["status"] == "strict_two_pass_complete"
                            for item in outcomes
                        )
                        * 2,
                        "retained_screenshot_count": retained_screenshot_count,
                        "outcomes": outcomes,
                    }
                    write_new(receipt_path, receipt)
                    return 2
                if retry_delay_seconds > 0:
                    time.sleep(retry_delay_seconds)

        if accepted is None:  # pragma: no cover - attempt loop guarantees a branch
            raise RuntimeError(f"No terminal attempt state for {event['event_id']}")
        outcomes.append(
            {
                "event_id": event["event_id"],
                "partition_id": event["partition_id"],
                "status": "strict_two_pass_complete",
                "started_at_utc": event_started,
                "completed_at_utc": now(),
                "accepted_attempt_ordinal": accepted["attempt_ordinal"],
                "accepted_output": accepted["output"],
                "accepted_output_sha256": accepted["output_sha256"],
                "paired_source_total": accepted["paired_source_total"],
                "projections": accepted["projections"],
                "screenshots": accepted["screenshots"],
                "attempts": attempt_outcomes,
                "do_not_merge": True,
            }
        )
        if event_index + 1 < len(events) and delay_seconds > 0:
            time.sleep(delay_seconds)

    receipt = {
        "schema_version": RUN_SCHEMA,
        "pilot": "008",
        "source": "Compendex with a retained paired Inspec projection",
        "status": "complete",
        "success": True,
        "diagnostic_only": True,
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "adapter": plan["adapter"],
        "started_at_utc": started_at,
        "completed_at_utc": now(),
        "event_plan": str(plan_path),
        "event_plan_sha256": digest_file(plan_path),
        "predeclared_event_count": len(events),
        "completed_event_count": len(outcomes),
        "successful_event_count": len(outcomes),
        "total_attempt_count": total_attempt_count,
        "accepted_strict_source_pass_count": len(outcomes) * 2,
        "accepted_mandatory_screenshot_count": len(outcomes) * 2,
        "retained_screenshot_count": retained_screenshot_count,
        "outcomes": outcomes,
    }
    write_new(receipt_path, receipt)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    parser.add_argument("--retry-delay-seconds", type=float, default=30.0)
    args = parser.parse_args()
    if args.delay_seconds < 0 or args.retry_delay_seconds < 0:
        raise SystemExit("Delay values cannot be negative")
    try:
        return run(
            args.event_plan,
            args.pilot_root,
            args.receipt,
            args.delay_seconds,
            args.retry_delay_seconds,
        )
    except Exception as error:
        print(" ".join(str(error).split())[:500], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
