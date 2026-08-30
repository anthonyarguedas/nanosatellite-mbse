#!/usr/bin/env python3
"""Repair ATAI A3 only after its preserved strict full-record-pass instability."""

from __future__ import annotations

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
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
PARTITION = "A3"
FAILURE_NAME = "A3.strict-complete.NON_MERGEABLE_FAILURE.json"
PASS_NAMES = ("A3-repaired-pass1.json", "A3-repaired-pass2.json")
RECONCILIATION_NAME = "A3-repair-reconciliation.json"


def write_new_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def replace_json(path: Path, value: dict[str, Any]) -> None:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_and_query() -> tuple[dict[str, Any], str]:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    events = plan.get("events")
    if not isinstance(events, list):
        raise RuntimeError("Missing event plan.")
    matches = [event for event in events if isinstance(event, dict) and event.get("partition_id") == PARTITION]
    if len(matches) != 1:
        raise RuntimeError("A3 is not uniquely declared in the event plan.")
    event = matches[0]
    if str(SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(SCHEDULE_DIR))
    from queries import partition_query  # noqa: PLC0415

    query = partition_query("proquest_aerospace_index", PARTITION)
    if event.get("query") != query:
        raise RuntimeError("A3 plan query differs from the shared schedule.")
    return event, query


def move_and_describe_initial_failure(event: dict[str, Any], query: str) -> Path:
    source = SEARCH_DIR / "A3.json"
    target = SEARCH_DIR / FAILURE_NAME
    if target.exists():
        return target
    if not source.exists():
        raise RuntimeError("A3 strict failure artifact is missing.")
    payload = json.loads(source.read_text(encoding="utf-8"))
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict) or metadata.get("status") != "error" or payload.get("total") is not None:
        raise RuntimeError("A3 source artifact is not the expected null-total strict-pass failure.")
    if payload.get("requested_query") != query:
        raise RuntimeError("A3 strict failure used a different query.")
    payload["pilot_failure"] = {
        "kind": "strict_full_record_pass_instability",
        "error_type": "ProQuestProtocolError",
        "error": "ProQuest did not return two stable complete rendered-result passes.",
        "disposition": "Preserved. A same-query repair will compare only complete source-total ordered stable-ID lists from two ordinary full traversals; it does not loosen the source query or create a final search.",
    }
    payload["do_not_merge"] = True
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    replace_json(source, payload)
    source.replace(target)
    return target


def pilot_cell(event: dict[str, Any], query: str, pass_number: int, total: int | None, status: str) -> dict[str, Any]:
    return {
        "pilot_id": "003",
        "event_id": event["event_id"],
        "event_kind": "pilot",
        "pilot_mode": "repaired_stable_id_two_pass_diagnostic",
        "semantic_partition": PARTITION,
        "cell_id": f"A3-full-expression-repaired-pass-{pass_number}",
        "source": "proquest_aerospace_index",
        "source_native_query_sha256": hashlib.sha256(query.encode()).hexdigest(),
        "source_native_query_characters": len(query),
        "source_native_query_limit": 50_000,
        "lossless_cell_split": False,
        "date_window": {"start": DATE_START, "end": DATE_END, "basis": "publication"},
        "language": "LA(English)",
        "capture_mode": "ordinary full traversal, reconciled source-total stable IDs across two passes",
        "repair_of": FAILURE_NAME,
        "status": status,
        "source_total": total,
        "pilot_only": True,
    }


def annotate(path: Path, event: dict[str, Any], query: str, pass_number: int, return_code: int) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError(f"{path.name}: missing metadata")
    total = payload.get("total")
    succeeded = return_code == 0 and metadata.get("status") == "success"
    if not succeeded and total is not None:
        raise RuntimeError(f"{path.name}: failure did not retain a null total")
    payload["do_not_merge"] = True
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["non_mergeable_reason"] = "Pilot 003 A3 stable-ID repair diagnostic; not a final search."
    payload["pilot_cell"] = pilot_cell(
        event, query, pass_number, total, "success" if succeeded else "source_failure"
    )
    replace_json(path, payload)
    return payload


def run_pass(event: dict[str, Any], query: str, pass_number: int) -> dict[str, Any]:
    path = SEARCH_DIR / PASS_NAMES[pass_number - 1]
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    command = [
        "uv", "run", str(ADAPTER), "--query", query,
        "--date-start", DATE_START, "--date-end", DATE_END,
        "--language", "English",
        "--limit", "10000", "--max-pages", "500", "--timeout", "90",
        "--output-path", str(path),
        "--prisma-run-id", str(uuid.uuid5(uuid.NAMESPACE_URL, f"slr1-atai-pilot-003/A3/repaired-pass{pass_number}")),
        "--prisma-review-id", event["review_id"],
        "--prisma-strategy-reference", event["strategy_reference"],
        "--prisma-strategy-version", event["strategy_version"],
        "--prisma-phase", "pilot_complete",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", PARTITION,
        "--prisma-partition-label", f"ATAI Pilot 003 A3 repaired stable-ID pass {pass_number}",
        "--prisma-partition-description", "Same literal ATAI pilot cell; non-strict full traversal for stable-ID repair only.",
    ]
    print(f"Running A3 stable-ID repair pass {pass_number}.", flush=True)
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode:
        message = (completed.stderr or completed.stdout).strip().splitlines()
        print(message[-1] if message else "ATAI A3 repair adapter failed.", file=sys.stderr)
    if not path.exists():
        failure = SEARCH_DIR / f"A3-repaired-pass{pass_number}.NON_MERGEABLE_FAILURE.json"
        write_new_json(
            failure,
            {
                "schema_version": "atai-pilot-source-failure/v1",
                "source": "Advanced Technologies & Aerospace Index",
                "total": None,
                "results": [],
                "do_not_merge": True,
                "pilot_cell": pilot_cell(event, query, pass_number, None, "source_failure"),
                "failure": {"return_code": completed.returncode, "message": "Adapter returned no artifact."},
            },
        )
        raise RuntimeError(f"A3 repair pass {pass_number} wrote no adapter artifact.")
    payload = annotate(path, event, query, pass_number, completed.returncode)
    if completed.returncode:
        raise RuntimeError(f"A3 repair pass {pass_number} failed; preserved {path.name}.")
    return payload


def stable_ids(payload: dict[str, Any], *, name: str, query: str) -> list[str]:
    metadata = payload.get("output_metadata")
    rows = payload.get("results")
    total = payload.get("total")
    if not isinstance(metadata, dict) or metadata.get("status") != "success":
        raise RuntimeError(f"{name}: source status is not success.")
    if metadata.get("retrieval_complete") is not True:
        raise RuntimeError(f"{name}: ordinary full traversal did not prove complete rows.")
    if not isinstance(total, int) or total < 0 or total > 10_000:
        raise RuntimeError(f"{name}: source total is outside the complete traversal boundary.")
    if not isinstance(rows, list) or len(rows) != total:
        raise RuntimeError(f"{name}: rows do not reconcile to source total.")
    if payload.get("requested_query") != query or payload.get("executed_query") != f"{query} AND LA(English)":
        raise RuntimeError(f"{name}: query readback differs.")
    identifiers: list[str] = []
    for expected_rank, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise RuntimeError(f"{name}: non-object result.")
        identifier = row.get("paperId")
        if not isinstance(identifier, str) or not identifier.isascii() or not identifier.isdigit():
            raise RuntimeError(f"{name}: invalid stable ID.")
        if row.get("rank") != expected_rank:
            raise RuntimeError(f"{name}: source order/rank does not reconcile.")
        if row.get("url") != f"https://www.proquest.com/ataindex/docview/{identifier}":
            raise RuntimeError(f"{name}: canonical record URL differs.")
        identifiers.append(identifier)
    if len(set(identifiers)) != len(identifiers):
        raise RuntimeError(f"{name}: repeated stable ID.")
    return identifiers


def main() -> int:
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise SystemExit("Run this repair through the shared browser runner.")
    event, query = event_and_query()
    failure = move_and_describe_initial_failure(event, query)
    first = run_pass(event, query, 1)
    second = run_pass(event, query, 2)
    first_ids = stable_ids(first, name=PASS_NAMES[0], query=query)
    second_ids = stable_ids(second, name=PASS_NAMES[1], query=query)
    if first_ids != second_ids:
        raise SystemExit("A3 repaired technical route still failed: two complete source-total stable-ID passes differ.")
    reconciliation = {
        "schema_version": "atai-pilot-003-a3-stable-id-repair/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "003",
        "partition_id": PARTITION,
        "do_not_merge": True,
        "initial_failure": {
            "artifact": failure.name,
            "sha256": sha256(failure),
            "error": "ProQuest did not return two stable complete rendered-result passes.",
        },
        "repair": {
            "query": query,
            "executed_query": f"{query} AND LA(English)",
            "date_window": {"start": DATE_START, "end": DATE_END, "basis": "publication", "inclusive": "both"},
            "method": "Two same-query ordinary full traversals with limit 10,000 and max-pages 500; both must report the full source total, retrieve every row, and have the same ordered numeric ATAI document IDs.",
            "pass_artifacts": [
                {"artifact": PASS_NAMES[0], "sha256": sha256(SEARCH_DIR / PASS_NAMES[0]), "source_total": first["total"]},
                {"artifact": PASS_NAMES[1], "sha256": sha256(SEARCH_DIR / PASS_NAMES[1]), "source_total": second["total"]},
            ],
            "ordered_stable_ids": first_ids,
            "stable_id_count": len(first_ids),
            "stable_id_equality": True,
        },
        "limitation": "This repair resolves stable-ID capture only. It does not turn A3 into an adapter strict-complete run, suppress the preserved strict metadata-signature failure, accept a final translation, or add a narrower filter.",
    }
    write_new_json(SEARCH_DIR / RECONCILIATION_NAME, reconciliation)
    print(json.dumps({"status": "repaired", "A3_total": first["total"], "stable_ids": len(first_ids)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
