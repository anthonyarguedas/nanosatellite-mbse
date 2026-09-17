#!/usr/bin/env python3
"""Execute the predeclared PQDT Global Pilot 004 comparison events."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Mapping
import uuid

from build_plan import (
    ADAPTER_PATH,
    ADAPTER_VERSION,
    DEFAULT_OUTPUT,
    PILOT_ROOT,
    SCHEMA,
    SOURCE,
    load,
    validate,
)

RECEIPT_SCHEMA = "pqdt-global-pilot004-run-receipt/v1"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
MAX_COMPLETE_RESULTS = 10_000
MAX_PAGES = 500
SCREENSHOT_SCHEMA = "pqdt-automatic-screenshots/v1"
ALLOWED_DATABASE_LABELS = {
    "ProQuest Dissertations & Theses Global",
    "ProQuest Dissertations & Theses Global Full Text Included",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ordered_id_digest(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
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
    value = load(path)
    if not isinstance(value, dict):
        raise TypeError(f"Expected an object in {path}")
    return value


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
                evidence.get("browser_chrome_captured") is False,
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
    if not isinstance(metadata, Mapping) or not isinstance(results, list):
        raise RuntimeError(f"{event['event_id']}: missing result metadata or rows")
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("source") != SOURCE
        or artifact.get("requested_query") != event["query"]
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("count_only") is not False
        or isinstance(total, bool)
        or not isinstance(total, int)
        or not 0 <= total <= MAX_COMPLETE_RESULTS
        or len(results) != total
    ):
        raise RuntimeError(f"{event['event_id']}: strict result contract differs")
    executed = artifact.get("executed_query")
    if (
        not isinstance(executed, str)
        or executed != f"{event['query']} AND YR(2011-2026) AND LA(English)"
    ):
        raise RuntimeError(f"{event['event_id']}: query, year, or language readback differs")

    ids: list[str] = []
    for rank, row in enumerate(results, start=1):
        if not isinstance(row, Mapping):
            raise RuntimeError(f"{event['event_id']}: result row is not an object")
        paper_id = row.get("paperId")
        if (
            not isinstance(paper_id, str)
            or not paper_id.isascii()
            or not paper_id.isdigit()
            or row.get("rank") != rank
            or row.get("url") != f"https://www.proquest.com/pqdtglobal/docview/{paper_id}"
        ):
            raise RuntimeError(f"{event['event_id']}: stable ID or source order differs")
        ids.append(paper_id)
    if len(set(ids)) != len(ids):
        raise RuntimeError(f"{event['event_id']}: duplicate document IDs")

    marker = marker_path(output)
    marker_payload = load_object(marker)
    normalized = marker_payload.get("normalized_json")
    if (
        marker_payload.get("schema") != "pqdt_output_commit_marker_v1"
        or not isinstance(normalized, Mapping)
        or normalized.get("sha256") != file_sha256(output)
        or normalized.get("bytes") != output.stat().st_size
    ):
        raise RuntimeError(f"{event['event_id']}: publication marker does not bind JSON")

    prisma = metadata.get("prisma_search_run")
    adapter = prisma.get("adapter") if isinstance(prisma, Mapping) else None
    strategy = prisma.get("strategy") if isinstance(prisma, Mapping) else None
    counts = prisma.get("staged_counts") if isinstance(prisma, Mapping) else None
    limits = strategy.get("limits") if isinstance(strategy, Mapping) else None
    sort = strategy.get("sort") if isinstance(strategy, Mapping) else None
    sort_value = sort.get("value") if isinstance(sort, Mapping) else None
    expected_adapter = plan.get("adapter")
    if not all(
        (
            isinstance(prisma, Mapping),
            isinstance(adapter, Mapping),
            isinstance(strategy, Mapping),
            isinstance(counts, Mapping),
            isinstance(limits, Mapping),
            isinstance(sort_value, Mapping),
            adapter.get("adapter_id") == "search_pqdt",
            adapter.get("adapter_version") == ADAPTER_VERSION,
            adapter.get("script_sha256") == expected_adapter.get("sha256"),
            prisma.get("review_id") == "slr1-pqdt-pilot-004",
            prisma.get("phase") == "pilot_complete",
            strategy.get("executed_query") == executed,
            strategy.get("search_scope") == "PQDT Global",
            sort_value.get("value") == "DateAsc",
            sort_value.get("label") == "Oldest first",
            counts.get("source_reported_total") == total,
            counts.get("records_exported") == total,
            counts.get("source_reported_total_exact") is True,
            prisma.get("completion_status") == "complete",
        )
    ):
        raise RuntimeError(f"{event['event_id']}: adapter, scope, count, or sort receipt differs")

    def applied(name: str) -> Any:
        item = limits.get(name) if isinstance(limits, Mapping) else None
        return item.get("value") if isinstance(item, Mapping) and item.get("state") == "applied" else None

    if {
        "full_text": applied("full_text"),
        "exclude_duplicates": applied("exclude_duplicates"),
        "spelling_variants": applied("spelling_variants"),
        "form_variants": applied("form_variants"),
        "show_variants": applied("show_variants"),
    } != {
        "full_text": False,
        "exclude_duplicates": False,
        "spelling_variants": False,
        "form_variants": False,
        "show_variants": False,
    }:
        raise RuntimeError(f"{event['event_id']}: frozen source controls differ")
    if not screenshot_receipt_is_complete(artifact, output):
        raise RuntimeError(f"{event['event_id']}: mandatory screenshots differ")

    return {
        "event_id": event["event_id"],
        "partition_id": event["partition_id"],
        "variant": event["variant"],
        "status": "complete",
        "source_total": total,
        "stable_ids_in_source_order": ids,
        "ordered_document_ids_sha256": ordered_id_digest(ids),
        "two_pass_strict_completion": True,
        "output": str(output.relative_to(PILOT_ROOT)),
        "output_sha256": file_sha256(output),
        "marker": str(marker.relative_to(PILOT_ROOT)),
        "marker_sha256": file_sha256(marker),
        "screenshots": {
            kind: {
                "path": str(path.relative_to(PILOT_ROOT)),
                "sha256": file_sha256(path),
            }
            for kind, path in screenshot_paths(output).items()
        },
    }


def deterministic_run_id(event_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"slr1-pqdt-pilot-004/{event_id}"))


def command(event: Mapping[str, Any], output: Path) -> list[str]:
    return [
        "uv",
        "run",
        str(ADAPTER_PATH),
        "--query",
        str(event["query"]),
        "--limit",
        str(MAX_COMPLETE_RESULTS),
        "--max-pages",
        str(MAX_PAGES),
        "--timeout",
        "120",
        "--page-delay-seconds",
        "0.1",
        "--detail-delay-seconds",
        "0.1",
        "--require-complete",
        "--output-path",
        str(output),
        "--year-start",
        str(event["year_start"]),
        "--year-end",
        str(event["year_end"]),
        "--language",
        str(event["language"]),
        "--no-full-text",
        "--no-exclude-duplicates",
        "--no-spelling-variants",
        "--no-form-variants",
        "--no-show-variants",
        "--prisma-run-id",
        deterministic_run_id(str(event["event_id"])),
        "--prisma-review-id",
        "slr1-pqdt-pilot-004",
        "--prisma-strategy-reference",
        "slr1-pqdt-post-proximity-bounded-wildcard-comparison-v1",
        "--prisma-strategy-version",
        str(event["query_sha256"]),
        "--prisma-phase",
        "pilot_complete",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        str(event["partition_id"]),
        "--prisma-partition-label",
        f"PQDT Global Pilot 004 {event['event_id']}",
        "--prisma-partition-description",
        str(event["purpose"]),
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


def receipt_payload(
    *,
    plan_path: Path,
    events: list[Mapping[str, Any]],
    outcomes: list[dict[str, Any]],
    status: str,
    started_at: str,
) -> dict[str, Any]:
    completed = [item for item in outcomes if item.get("status") == "complete"]
    failure_paths = sorted((plan_path.parent / "failures").glob("*.json"))
    retained_failures = []
    for path in failure_paths:
        value = load_object(path)
        retained_failures.append(
            {
                "artifact": str(path.relative_to(PILOT_ROOT)),
                "sha256": file_sha256(path),
                "source_total": value.get("total"),
                "status": value.get("output_metadata", {}).get("status"),
            }
        )
    return {
        "schema_version": RECEIPT_SCHEMA,
        "pilot": "004",
        "source": SOURCE,
        "status": status,
        "diagnostic_only": True,
        "do_not_merge": True,
        "event_plan": str(plan_path.relative_to(PILOT_ROOT)),
        "event_plan_sha256": file_sha256(plan_path),
        "predeclared_event_count": len(events),
        "completed_event_count": len(completed),
        "started_at_utc": started_at,
        "updated_at_utc": now(),
        "outcomes": outcomes,
        "retained_failure_count": len(retained_failures),
        "retained_failures": retained_failures,
    }


def run(
    plan_path: Path,
    pilot_root: Path,
    receipt_path: Path,
    *,
    resume: bool,
    max_events: int | None,
) -> int:
    plan = load_object(plan_path)
    errors = validate(plan)
    events = plan.get("events")
    if errors or plan.get("schema_version") != SCHEMA or not isinstance(events, list):
        raise RuntimeError("Invalid event plan: " + "; ".join(errors))
    if not ADAPTER_PATH.is_file():
        raise RuntimeError(f"PQDT adapter is missing: {ADAPTER_PATH}")
    if file_sha256(ADAPTER_PATH) != plan.get("adapter", {}).get("sha256"):
        raise RuntimeError("The PQDT adapter changed after predeclaration")

    selected = events[:max_events] if max_events is not None else events
    outcomes: list[dict[str, Any]] = []
    started_at = now()
    for event in selected:
        output = pilot_root / "searches" / str(event["output"])
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
            if any(os.path.lexists(path) for path in occupied):
                raise RuntimeError(
                    f"Incomplete existing marker or screenshot blocks {event['event_id']}"
                )
            print(
                f"Running PQDT Pilot 004 {event['event_id']} "
                f"({event['query_characters']} characters).",
                flush=True,
            )
            completed = subprocess.run(command(event, output), check=False)
            if completed.returncode != 0 or not output.exists():
                outcomes.append(
                    {
                        "event_id": event["event_id"],
                        "partition_id": event["partition_id"],
                        "variant": event["variant"],
                        "status": "source_or_adapter_failure",
                        "return_code": completed.returncode,
                        "source_total": None,
                        "output": str(output.relative_to(pilot_root)) if output.exists() else None,
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-events", type=int)
    args = parser.parse_args()
    if args.max_events is not None and args.max_events < 1:
        parser.error("--max-events must be positive")
    return args


def main() -> int:
    args = parse_args()
    try:
        return run(
            args.plan.expanduser().resolve(),
            args.pilot_root.expanduser().resolve(),
            args.receipt.expanduser().resolve(),
            resume=args.resume,
            max_events=args.max_events,
        )
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
