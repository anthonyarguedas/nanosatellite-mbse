#!/usr/bin/env python3
"""Run the predeclared ATAI Pilot 003 cells sequentially and fail closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PILOT_ROOT = ROOT / "source-specific/advanced-technologies-aerospace-index/pilots/003"
SEARCH_DIR = PILOT_ROOT / "searches"
PLAN_PATH = SEARCH_DIR / "event-plan.json"
SCHEDULE_DIR = ROOT / "scripts/pilot_schedule"
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
SOURCE_ID = "proquest_aerospace_index"
SOURCE_LABEL = "Advanced Technologies & Aerospace Index"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
LANGUAGE = "English"
ADAPTER_QUERY_LIMIT = 50_000


def write_json(path: Path, value: dict[str, Any]) -> None:
    """Atomically write a newly owned pilot artifact."""
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def replace_json(path: Path, value: dict[str, Any]) -> None:
    """Atomically annotate an adapter artifact already owned by this run."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def load_plan() -> list[dict[str, Any]]:
    if not PLAN_PATH.exists():
        raise RuntimeError(f"Missing predeclared event plan: {PLAN_PATH}")
    try:
        payload = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read event plan: {error}") from error
    if payload.get("schema_version") != "academic-search-event-schedule/v1":
        raise RuntimeError("Event plan has an unsupported schema.")
    events = payload.get("events")
    if not isinstance(events, list):
        raise RuntimeError("Event plan has no event list.")
    if str(SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(SCHEDULE_DIR))
    from queries import partition_query  # noqa: PLC0415

    by_partition: dict[str, dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            raise RuntimeError("Event plan contains a non-object event.")
        partition = event.get("partition_id")
        if partition in by_partition:
            raise RuntimeError(f"Event plan repeats partition {partition!r}.")
        if partition not in PARTITIONS or event.get("source") != SOURCE_ID:
            raise RuntimeError("Event plan has an unexpected ATAI partition/source.")
        if event.get("event_kind") != "pilot" or event.get("pilot_mode") != "strict":
            raise RuntimeError("Event plan must use the standard strict pilot mode.")
        if "query_cells" in event:
            raise RuntimeError("Pilot 003 plan unexpectedly uses source query cells.")
        query = event.get("query")
        if not isinstance(query, str) or query != partition_query(SOURCE_ID, partition):
            raise RuntimeError(f"{partition}: event-plan query differs from shared schedule.")
        if len(query) > ADAPTER_QUERY_LIMIT:
            raise RuntimeError(f"{partition}: query exceeds validated adapter limit.")
        by_partition[partition] = event
    if tuple(by_partition) != PARTITIONS:
        raise RuntimeError("Event plan does not contain the complete ordered ATAI schedule.")
    return [by_partition[partition] for partition in PARTITIONS]


def source_output_path(partition: str) -> Path:
    return SEARCH_DIR / f"{partition}.json"


def deterministic_run_id(partition: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"slr1-atai-pilot-003/{partition}/full"))


def pilot_cell(event: dict[str, Any], *, status: str, total: int | None) -> dict[str, Any]:
    query = event["query"]
    return {
        "pilot_id": "003",
        "event_id": event["event_id"],
        "event_kind": "pilot",
        "pilot_mode": "complete_rendered_records_diagnostic",
        "semantic_partition": event["partition_id"],
        "cell_id": f"{event['partition_id']}-full-expression",
        "source": SOURCE_ID,
        "source_native_query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        "source_native_query_characters": len(query),
        "source_native_query_limit": ADAPTER_QUERY_LIMIT,
        "lossless_cell_split": False,
        "date_window": {"start": DATE_START, "end": DATE_END, "basis": "publication"},
        "language": "LA(English)",
        "status": status,
        "source_total": total,
        "pilot_only": True,
    }


def annotate_adapter_artifact(path: Path, event: dict[str, Any], *, command_exit: int) -> bool:
    """Preserve adapter evidence while making the diagnostic non-mergeable."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read adapter artifact {path}: {error}") from error
    if not isinstance(payload, dict):
        raise RuntimeError(f"Adapter artifact {path} is not an object.")
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError(f"Adapter artifact {path} lacks output_metadata.")
    total = payload.get("total")
    if total is not None and (isinstance(total, bool) or not isinstance(total, int)):
        raise RuntimeError(f"Adapter artifact {path} has invalid total.")
    source_status = metadata.get("status")
    succeeded = command_exit == 0 and source_status == "success"
    if not succeeded and total is not None:
        raise RuntimeError(f"Failed adapter artifact {path} did not preserve null total.")

    # The source's strict two-pass status stays intact; this flag only prevents
    # a diagnostic pilot from entering a later final-search merge.
    payload["do_not_merge"] = True
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["non_mergeable_reason"] = (
        "Pilot 003 diagnostic artifact; P-001 is unset and this is not a final search."
    )
    payload["pilot_cell"] = pilot_cell(
        event,
        status="success" if succeeded else "source_failure",
        total=total,
    )
    replace_json(path, payload)
    return succeeded


def write_missing_output_failure(event: dict[str, Any], return_code: int) -> Path:
    """Record a null-total failure even if the external adapter could not write."""
    path = SEARCH_DIR / f"{event['partition_id']}.NON_MERGEABLE_FAILURE.json"
    write_json(
        path,
        {
            "schema_version": "atai-pilot-source-failure/v1",
            "source": SOURCE_LABEL,
            "total": None,
            "results": [],
            "do_not_merge": True,
            "pilot_cell": pilot_cell(event, status="source_failure", total=None),
            "failure": {
                "adapter": str(ADAPTER),
                "return_code": return_code,
                "message": "The adapter returned no artifact; stdout/stderr were intentionally not serialized.",
            },
        },
    )
    return path


def run_event(event: dict[str, Any]) -> bool:
    partition = event["partition_id"]
    output = source_output_path(partition)
    if output.exists():
        raise RuntimeError(f"Refusing to overwrite existing cell artifact {output}")
    if not ADAPTER.is_file():
        raise RuntimeError(f"ATAI adapter is unavailable: {ADAPTER}")
    command = [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        event["query"],
        "--date-start",
        DATE_START,
        "--date-end",
        DATE_END,
        "--language",
        LANGUAGE,
        "--require-complete",
        "--timeout",
        "90",
        "--output-path",
        str(output),
        "--prisma-run-id",
        deterministic_run_id(partition),
        "--prisma-review-id",
        event["review_id"],
        "--prisma-strategy-reference",
        event["strategy_reference"],
        "--prisma-strategy-version",
        event["strategy_version"],
        "--prisma-phase",
        "pilot_complete",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        partition,
        "--prisma-partition-label",
        f"ATAI Pilot 003 {partition}",
        "--prisma-partition-description",
        "Full literal ATAI diagnostic cell; not a final search.",
    ]
    print(f"Running ATAI Pilot 003 {partition} ({len(event['query'])} source-query characters).", flush=True)
    completed = subprocess.run(command, check=False)
    if output.exists():
        return annotate_adapter_artifact(output, event, command_exit=completed.returncode)
    failure = write_missing_output_failure(event, completed.returncode)
    print(f"ATAI {partition} produced no adapter artifact; preserved {failure}.", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-direct-browser",
        action="store_true",
        help="Testing only; normal execution must use run_with_browser.py.",
    )
    args = parser.parse_args()
    if not args.allow_direct_browser and os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise SystemExit("Run this source workflow through the shared browser runner.")
    for event in load_plan():
        if not run_event(event):
            raise SystemExit(
                f"ATAI source failure at {event['partition_id']}; stopped without an unrecorded narrower replacement."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
