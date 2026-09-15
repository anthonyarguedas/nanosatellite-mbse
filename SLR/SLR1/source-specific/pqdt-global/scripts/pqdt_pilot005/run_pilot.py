#!/usr/bin/env python3
"""Execute the predeclared PQDT Global Pilot 005 comparison events."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Mapping
import uuid

import queries
from build_event_plan import DEFAULT_OUTPUT as DEFAULT_PLAN
from build_event_plan import SCHEMA as PLAN_SCHEMA

SOURCE = "ProQuest Dissertations & Theses Global"
RECEIPT_SCHEMA = "pqdt-global-pilot005-run-receipt/v1"
DEFAULT_RECEIPT = queries.PILOT_ROOT / "searches" / "run-receipt.json"
MAX_COMPLETE_RESULTS = 10_000
MAX_PAGES = 500
SCREENSHOT_SCHEMA = "pqdt-automatic-screenshots/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.PQDT_COMMIT.json")


def screenshot_paths(output: Path) -> dict[str, Path]:
    stem = output.name[:-5] if output.name.lower().endswith(".json") else output.name
    return {
        "search_page": output.with_name(f"{stem}.search-page.png"),
        "results_page": output.with_name(f"{stem}.results-page.png"),
    }


def load_object(path: Path) -> dict[str, Any]:
    return queries.load_object(path)


def validate_plan(plan: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    events = plan.get("events")
    if plan.get("schema_version") != PLAN_SCHEMA:
        errors.append("unexpected plan schema")
    if plan.get("status") != "predeclared":
        errors.append("plan is not predeclared")
    if plan.get("protocol_commit") != queries.PROTOCOL_COMMIT:
        errors.append("protocol commit changed")
    if not isinstance(events, list) or len(events) != 18:
        errors.append("plan must contain 18 events")
        return errors
    expected = [
        (f"{variant}-{partition}", partition, variant)
        for partition in queries.SCHEDULE_IDS
        for variant in ("free-text", "augmented")
    ]
    observed = [
        (event.get("event_id"), event.get("partition_id"), event.get("variant"))
        for event in events
        if isinstance(event, Mapping)
    ]
    if observed != expected:
        errors.append("event order changed")
    for sequence, event in enumerate(events, start=1):
        if not isinstance(event, Mapping):
            errors.append(f"event {sequence} is malformed")
            continue
        query = event.get("query")
        if event.get("sequence") != sequence:
            errors.append(f"event {sequence} sequence changed")
        if not isinstance(query, str) or not query:
            errors.append(f"event {sequence} query is empty")
            continue
        if event.get("query_sha256") != queries.sha256_text(query):
            errors.append(f"event {sequence} query hash changed")
        if event.get("query_characters") != len(query) or len(query) >= 50_000:
            errors.append(f"event {sequence} query length is invalid")
    return errors


def screenshot_receipt_is_complete(
    artifact: Mapping[str, Any], output: Path
) -> bool:
    metadata = artifact.get("output_metadata")
    receipt = metadata.get("screenshots") if isinstance(metadata, Mapping) else None
    if not isinstance(receipt, Mapping) or not all(
        (
            receipt.get("schema_version") == SCREENSHOT_SCHEMA,
            receipt.get("automatic") is True,
            receipt.get("no_opt_out") is True,
            receipt.get("same_directory_as_json") is True,
        )
    ):
        return False
    for kind, path in screenshot_paths(output).items():
        evidence = receipt.get(kind)
        if not isinstance(evidence, Mapping):
            return False
        if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            return False
        if not all(
            (
                evidence.get("path") == path.name,
                evidence.get("sha256") == file_sha256(path),
                isinstance(evidence.get("width"), int),
                evidence.get("width", 0) > 0,
                isinstance(evidence.get("height"), int),
                evidence.get("height", 0) > 0,
                evidence.get("complete_page_url_retained") is False,
                evidence.get("session_identifiers_retained") is False,
            )
        ):
            return False
    return True


def strict_artifact_summary(
    event: Mapping[str, Any], output: Path, plan: Mapping[str, Any]
) -> dict[str, Any]:
    artifact = load_object(output)
    metadata = artifact.get("output_metadata")
    results = artifact.get("results")
    total = artifact.get("total")
    expected_executed = (
        f"{event['query']} AND YR({event['year_start']}-{event['year_end']}) "
        f"AND LA({event['language']})"
    )
    if not isinstance(metadata, Mapping) or not isinstance(results, list):
        raise RuntimeError(f"{event['event_id']}: missing result metadata or rows")
    if not all(
        (
            artifact.get("schema_version") == "academic-search-result/v1",
            artifact.get("source") == SOURCE,
            artifact.get("requested_query") == event["query"],
            artifact.get("executed_query") == expected_executed,
            metadata.get("status") == "success",
            metadata.get("retrieval_complete") is True,
            metadata.get("count_only") is False,
            isinstance(total, int) and not isinstance(total, bool),
            0 <= total <= MAX_COMPLETE_RESULTS,
            len(results) == total,
        )
    ):
        raise RuntimeError(f"{event['event_id']}: strict result contract differs")

    ids: list[str] = []
    for rank, row in enumerate(results, start=1):
        if not isinstance(row, Mapping):
            raise RuntimeError(f"{event['event_id']}: malformed result row")
        paper_id = row.get("paperId")
        if not all(
            (
                isinstance(paper_id, str),
                paper_id.isascii() if isinstance(paper_id, str) else False,
                paper_id.isdigit() if isinstance(paper_id, str) else False,
                row.get("rank") == rank,
                row.get("url")
                == f"https://www.proquest.com/pqdtglobal/docview/{paper_id}",
            )
        ):
            raise RuntimeError(f"{event['event_id']}: stable ID or source order differs")
        ids.append(paper_id)
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"{event['event_id']}: duplicate document IDs")

    marker = marker_path(output)
    marker_payload = load_object(marker)
    normalized = marker_payload.get("normalized_json")
    if not all(
        (
            marker_payload.get("schema") == "pqdt_output_commit_marker_v1",
            isinstance(normalized, Mapping),
            normalized.get("sha256") == file_sha256(output)
            if isinstance(normalized, Mapping)
            else False,
            normalized.get("bytes") == output.stat().st_size
            if isinstance(normalized, Mapping)
            else False,
        )
    ):
        raise RuntimeError(f"{event['event_id']}: publication marker does not bind JSON")

    prisma = metadata.get("prisma_search_run")
    adapter = prisma.get("adapter") if isinstance(prisma, Mapping) else None
    strategy = prisma.get("strategy") if isinstance(prisma, Mapping) else None
    counts = prisma.get("staged_counts") if isinstance(prisma, Mapping) else None
    limits = strategy.get("limits") if isinstance(strategy, Mapping) else None
    sort = strategy.get("sort") if isinstance(strategy, Mapping) else None
    sort_value = sort.get("value") if isinstance(sort, Mapping) else None
    if not all(
        (
            isinstance(adapter, Mapping),
            isinstance(strategy, Mapping),
            isinstance(counts, Mapping),
            isinstance(limits, Mapping),
            isinstance(sort_value, Mapping),
            adapter.get("adapter_id") == "search_pqdt",
            adapter.get("adapter_version") == "5",
            adapter.get("script_sha256") == plan.get("adapter", {}).get("sha256"),
            prisma.get("review_id") == "slr1-pqdt-pilot-005",
            prisma.get("phase") == "pilot_complete",
            strategy.get("executed_query") == expected_executed,
            strategy.get("search_scope") == "PQDT Global",
            sort_value.get("value") == "DateAsc",
            sort_value.get("label") == "Oldest first",
            counts.get("source_reported_total") == total,
            counts.get("records_exported") == total,
            counts.get("source_reported_total_exact") is True,
            prisma.get("completion_status") == "complete",
        )
    ):
        raise RuntimeError(f"{event['event_id']}: provenance or count receipt differs")

    def applied(name: str) -> Any:
        item = limits.get(name) if isinstance(limits, Mapping) else None
        if isinstance(item, Mapping) and item.get("state") == "applied":
            return item.get("value")
        return None

    observed_controls = {
        "full_text": applied("full_text"),
        "exclude_duplicates": applied("exclude_duplicates"),
        "spelling_variants": applied("spelling_variants"),
        "form_variants": applied("form_variants"),
        "show_variants": applied("show_variants"),
    }
    if observed_controls != {
        "full_text": False,
        "exclude_duplicates": False,
        "spelling_variants": False,
        "form_variants": False,
        "show_variants": False,
    }:
        raise RuntimeError(f"{event['event_id']}: frozen controls differ")
    if not screenshot_receipt_is_complete(artifact, output):
        raise RuntimeError(f"{event['event_id']}: mandatory screenshots differ")

    return {
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "variant": event["variant"],
        "status": "complete",
        "source_total": total,
        "stable_ids_in_source_order": ids,
        "ordered_document_ids_sha256": queries.ordered_id_sha256(ids),
        "two_pass_strict_completion": True,
        "output": str(output.relative_to(queries.PILOT_ROOT)),
        "output_sha256": file_sha256(output),
        "marker": str(marker.relative_to(queries.PILOT_ROOT)),
        "marker_sha256": file_sha256(marker),
        "screenshots": {
            kind: {
                "path": str(path.relative_to(queries.PILOT_ROOT)),
                "sha256": file_sha256(path),
            }
            for kind, path in screenshot_paths(output).items()
        },
    }


def deterministic_run_id(event_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"slr1-pqdt-pilot-005/{event_id}"))


def command(event: Mapping[str, Any], output: Path) -> list[str]:
    return [
        "uv", "run", str(queries.UNION_BRIDGE_PATH),
        "--query", str(event["query"]),
        "--limit", str(MAX_COMPLETE_RESULTS),
        "--max-pages", str(MAX_PAGES),
        "--timeout", "120",
        "--page-delay-seconds", "0.1",
        "--detail-delay-seconds", "0.1",
        "--require-complete",
        "--output-path", str(output),
        "--year-start", str(event["year_start"]),
        "--year-end", str(event["year_end"]),
        "--language", str(event["language"]),
        "--no-full-text",
        "--no-exclude-duplicates",
        "--no-spelling-variants",
        "--no-form-variants",
        "--no-show-variants",
        "--prisma-run-id", deterministic_run_id(str(event["event_id"])),
        "--prisma-review-id", "slr1-pqdt-pilot-005",
        "--prisma-strategy-reference", "slr1-pqdt-controlled-vocabulary-value-test-v1",
        "--prisma-strategy-version", str(event["query_sha256"]),
        "--prisma-phase", "pilot_complete",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", str(event["partition_id"]),
        "--prisma-partition-label", f"PQDT Global Pilot 005 {event['event_id']}",
        "--prisma-partition-description", str(event["purpose"]),
    ]


def atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def preserve_failed_attempt(output: Path) -> list[str]:
    related = [output, marker_path(output), *screenshot_paths(output).values()]
    existing = [path for path in related if path.exists()]
    if not existing:
        return []
    failures = output.parent.parent / "failures"
    failures.mkdir(parents=True, exist_ok=True)
    attempt = 1
    while any(failures.glob(f"{output.stem}.attempt-{attempt:02d}.*")):
        attempt += 1
    preserved: list[str] = []
    for path in existing:
        if path == output:
            name = f"{output.stem}.attempt-{attempt:02d}.NON_MERGEABLE_FAILURE.json"
        elif path == marker_path(output):
            name = f".{output.stem}.attempt-{attempt:02d}.NON_MERGEABLE_FAILURE.PQDT_COMMIT.json"
        else:
            suffix = ".search-page.png" if "search-page" in path.name else ".results-page.png"
            name = f"{output.stem}.attempt-{attempt:02d}.NON_MERGEABLE_FAILURE{suffix}"
        destination = failures / name
        shutil.move(path, destination)
        preserved.append(str(destination.relative_to(queries.PILOT_ROOT)))
    return preserved


def receipt_payload(
    *,
    plan_path: Path,
    events: list[Mapping[str, Any]],
    outcomes: list[dict[str, Any]],
    status: str,
    started_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": RECEIPT_SCHEMA,
        "pilot": "005",
        "source": SOURCE,
        "status": status,
        "diagnostic_only": True,
        "do_not_merge": True,
        "event_plan": str(plan_path.relative_to(queries.PILOT_ROOT)),
        "event_plan_sha256": file_sha256(plan_path),
        "predeclared_event_count": len(events),
        "completed_event_count": sum(
            item.get("status") == "complete" for item in outcomes
        ),
        "started_at_utc": started_at,
        "updated_at_utc": now(),
        "outcomes": outcomes,
    }


def run(
    plan_path: Path,
    receipt_path: Path,
    *,
    resume: bool,
    max_events: int | None,
) -> int:
    plan = load_object(plan_path)
    errors = validate_plan(plan)
    if errors:
        raise RuntimeError("Invalid event plan: " + "; ".join(errors))
    if file_sha256(queries.ADAPTER_PATH) != plan.get("adapter", {}).get("sha256"):
        raise RuntimeError("The PQDT adapter changed after event predeclaration")
    if file_sha256(queries.UNION_BRIDGE_PATH) != plan.get("local_union_bridge", {}).get("sha256"):
        raise RuntimeError("The PQDT Pilot 005 union bridge changed after predeclaration")
    events = plan["events"]
    selected = events[:max_events] if max_events is not None else events
    outcomes: list[dict[str, Any]] = []
    started_at = now()

    for event in selected:
        output = queries.PILOT_ROOT / "searches" / event["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        event_started = now()
        if output.exists():
            if not resume:
                raise RuntimeError(f"Refusing to overwrite {output}")
            summary = strict_artifact_summary(event, output, plan)
            outcomes.append(
                {
                    **summary,
                    "reused_existing": True,
                    "started_at_utc": event_started,
                    "completed_at_utc": now(),
                }
            )
        else:
            occupied = [marker_path(output), *screenshot_paths(output).values()]
            if any(path.exists() for path in occupied):
                raise RuntimeError(f"Incomplete existing output blocks {event['event_id']}")
            print(f"Running PQDT Pilot 005 {event['event_id']}.", flush=True)
            completed = subprocess.run(command(event, output), check=False)
            if completed.returncode != 0 or not output.exists():
                preserved = preserve_failed_attempt(output)
                outcomes.append(
                    {
                        "event_id": event["event_id"],
                        "partition_id": event["partition_id"],
                        "variant": event["variant"],
                        "status": "source_or_adapter_failure",
                        "return_code": completed.returncode,
                        "source_total": None,
                        "preserved_artifacts": preserved,
                        "started_at_utc": event_started,
                        "completed_at_utc": now(),
                    }
                )
                atomic_write_json(
                    receipt_path,
                    receipt_payload(
                        plan_path=plan_path,
                        events=events,
                        outcomes=outcomes,
                        status="stopped_on_source_or_adapter_failure",
                        started_at=started_at,
                    ),
                )
                return 1
            summary = strict_artifact_summary(event, output, plan)
            outcomes.append(
                {
                    **summary,
                    "reused_existing": False,
                    "return_code": completed.returncode,
                    "started_at_utc": event_started,
                    "completed_at_utc": now(),
                }
            )
        atomic_write_json(
            receipt_path,
            receipt_payload(
                plan_path=plan_path,
                events=events,
                outcomes=outcomes,
                status="running",
                started_at=started_at,
            ),
        )

    status = "complete" if len(selected) == len(events) else "bounded_stop"
    atomic_write_json(
        receipt_path,
        receipt_payload(
            plan_path=plan_path,
            events=events,
            outcomes=outcomes,
            status=status,
            started_at=started_at,
        ),
    )
    print(json.dumps({"status": status, "completed_events": len(outcomes)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-events", type=int)
    args = parser.parse_args()
    if args.max_events is not None and args.max_events < 1:
        parser.error("--max-events must be positive")
    try:
        return run(
            args.plan.expanduser().resolve(),
            args.receipt.expanduser().resolve(),
            resume=args.resume,
            max_events=args.max_events,
        )
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
