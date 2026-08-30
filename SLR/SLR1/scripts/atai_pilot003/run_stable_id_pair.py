#!/usr/bin/env python3
"""Capture one ATAI Pilot 003 cell twice and reconcile full stable-ID lists."""

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
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"


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


def paths(partition: str) -> tuple[Path, Path, Path, Path]:
    return (
        SEARCH_DIR / f"{partition}.json",
        SEARCH_DIR / f"{partition}.strict-complete.NON_MERGEABLE_FAILURE.json",
        SEARCH_DIR / f"{partition}-stable-id-pass1.json",
        SEARCH_DIR / f"{partition}-stable-id-pass2.json",
    )


def reconciliation_path(partition: str) -> Path:
    return SEARCH_DIR / f"{partition}-stable-id-reconciliation.json"


def event_and_query(partition: str) -> tuple[dict[str, Any], str]:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    events = plan.get("events")
    if not isinstance(events, list):
        raise RuntimeError("Missing event plan.")
    matches = [event for event in events if isinstance(event, dict) and event.get("partition_id") == partition]
    if len(matches) != 1:
        raise RuntimeError(f"{partition} is not uniquely declared in the event plan.")
    event = matches[0]
    if str(SCHEDULE_DIR) not in sys.path:
        sys.path.insert(0, str(SCHEDULE_DIR))
    from queries import partition_query  # noqa: PLC0415

    query = partition_query("proquest_aerospace_index", partition)
    if event.get("query") != query:
        raise RuntimeError(f"{partition} plan query differs from the shared schedule.")
    return event, query


def preserve_strict_failure(partition: str, query: str) -> Path | None:
    base, failure, _, _ = paths(partition)
    if failure.exists():
        return failure
    if not base.exists():
        return None
    payload = json.loads(base.read_text(encoding="utf-8"))
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict) or metadata.get("status") != "error" or payload.get("total") is not None:
        raise RuntimeError(f"{partition}: existing base artifact is not a null-total strict-pass failure.")
    if payload.get("requested_query") != query:
        raise RuntimeError(f"{partition}: strict failure used a different query.")
    payload["pilot_failure"] = {
        "kind": "strict_full_record_pass_instability",
        "error_type": "ProQuestProtocolError",
        "error": "ProQuest did not return two stable complete rendered-result passes.",
        "disposition": "Preserved. The same literal source query is captured twice with ordinary full traversal and compared by complete source-total ordered numeric document IDs; this is still diagnostic only.",
    }
    payload["do_not_merge"] = True
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    replace_json(base, payload)
    base.replace(failure)
    return failure


def pilot_cell(event: dict[str, Any], query: str, partition: str, pass_number: int, total: int | None, status: str, initial_failure: Path | None) -> dict[str, Any]:
    return {
        "pilot_id": "003",
        "event_id": event["event_id"],
        "event_kind": "pilot",
        "pilot_mode": "stable_id_two_pass_diagnostic",
        "semantic_partition": partition,
        "cell_id": f"{partition}-full-expression-stable-id-pass-{pass_number}",
        "source": "proquest_aerospace_index",
        "source_native_query_sha256": hashlib.sha256(query.encode()).hexdigest(),
        "source_native_query_characters": len(query),
        "source_native_query_limit": 50_000,
        "lossless_cell_split": False,
        "date_window": {"start": DATE_START, "end": DATE_END, "basis": "publication"},
        "language": "LA(English)",
        "capture_mode": "ordinary full traversal, reconciled source-total stable IDs across two passes",
        "repair_of": initial_failure.name if initial_failure is not None else None,
        "status": status,
        "source_total": total,
        "pilot_only": True,
    }


def annotate(path: Path, event: dict[str, Any], query: str, partition: str, pass_number: int, return_code: int, initial_failure: Path | None) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metadata = payload.get("output_metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError(f"{path.name}: missing metadata")
    total = payload.get("total")
    succeeded = return_code == 0 and metadata.get("status") == "success"
    if not succeeded and total is not None:
        raise RuntimeError(f"{path.name}: failure did not preserve a null total")
    payload["do_not_merge"] = True
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["non_mergeable_reason"] = "Pilot 003 stable-ID pair diagnostic; not a final search."
    payload["pilot_cell"] = pilot_cell(event, query, partition, pass_number, total, "success" if succeeded else "source_failure", initial_failure)
    replace_json(path, payload)
    return payload


def run_pass(event: dict[str, Any], query: str, partition: str, pass_number: int, initial_failure: Path | None) -> dict[str, Any]:
    _, _, pass_one, pass_two = paths(partition)
    path = pass_one if pass_number == 1 else pass_two
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    command = [
        "uv", "run", str(ADAPTER), "--query", query,
        "--date-start", DATE_START, "--date-end", DATE_END,
        "--language", "English", "--limit", "10000", "--max-pages", "500", "--timeout", "90",
        "--output-path", str(path),
        "--prisma-run-id", str(uuid.uuid5(uuid.NAMESPACE_URL, f"slr1-atai-pilot-003/{partition}/stable-id-pass{pass_number}")),
        "--prisma-review-id", event["review_id"],
        "--prisma-strategy-reference", event["strategy_reference"],
        "--prisma-strategy-version", event["strategy_version"],
        "--prisma-phase", "pilot_complete",
        "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", partition,
        "--prisma-partition-label", f"ATAI Pilot 003 {partition} stable-ID pass {pass_number}",
        "--prisma-partition-description", "Same literal ATAI pilot cell; ordinary full traversal for stable-ID reconciliation only.",
    ]
    print(f"Running {partition} stable-ID pass {pass_number}.", flush=True)
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode:
        lines = (completed.stderr or completed.stdout).strip().splitlines()
        print(lines[-1] if lines else f"ATAI {partition} stable-ID pass failed.", file=sys.stderr)
    if not path.exists():
        failure = SEARCH_DIR / f"{partition}-stable-id-pass{pass_number}.NON_MERGEABLE_FAILURE.json"
        write_new_json(
            failure,
            {
                "schema_version": "atai-pilot-source-failure/v1",
                "source": "Advanced Technologies & Aerospace Index",
                "total": None,
                "results": [],
                "do_not_merge": True,
                "pilot_cell": pilot_cell(event, query, partition, pass_number, None, "source_failure", initial_failure),
                "failure": {"return_code": completed.returncode, "message": "Adapter returned no artifact."},
            },
        )
        raise RuntimeError(f"{partition} stable-ID pass {pass_number} wrote no adapter artifact.")
    payload = annotate(path, event, query, partition, pass_number, completed.returncode, initial_failure)
    if completed.returncode:
        raise RuntimeError(f"{partition} stable-ID pass {pass_number} failed; preserved {path.name}.")
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


def run_pair(partition: str) -> dict[str, Any]:
    event, query = event_and_query(partition)
    initial_failure = preserve_strict_failure(partition, query)
    first = run_pass(event, query, partition, 1, initial_failure)
    second = run_pass(event, query, partition, 2, initial_failure)
    first_ids = stable_ids(first, name=f"{partition} stable-ID pass 1", query=query)
    second_ids = stable_ids(second, name=f"{partition} stable-ID pass 2", query=query)
    if first_ids != second_ids:
        raise RuntimeError(f"{partition} repaired technical route still failed: ordered complete source-total stable-ID passes differ.")
    receipt = {
        "schema_version": "atai-pilot-003-stable-id-pair/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "003",
        "partition_id": partition,
        "do_not_merge": True,
        "initial_strict_failure": (
            {
                "artifact": initial_failure.name,
                "sha256": sha256(initial_failure),
                "error": "ProQuest did not return two stable complete rendered-result passes.",
            }
            if initial_failure is not None
            else None
        ),
        "capture_reason": (
            "same-query stable-ID repair after the preserved strict full-record-signature failure"
            if initial_failure is not None
            else "proactive stable-ID two-pass capture after observed ATAI strict full-record-signature instability; no source query or control was relaxed"
        ),
        "query": query,
        "executed_query": f"{query} AND LA(English)",
        "date_window": {"start": DATE_START, "end": DATE_END, "basis": "publication", "inclusive": "both"},
        "method": "Two same-query ordinary full traversals with limit 10,000 and max-pages 500. Both must report the full source total, retrieve every row, and have identical ordered numeric ATAI document IDs.",
        "pass_artifacts": [
            {"artifact": paths(partition)[2].name, "sha256": sha256(paths(partition)[2]), "source_total": first["total"]},
            {"artifact": paths(partition)[3].name, "sha256": sha256(paths(partition)[3]), "source_total": second["total"]},
        ],
        "ordered_stable_ids": first_ids,
        "stable_id_count": len(first_ids),
        "stable_id_equality": True,
        "limitation": "Stable-ID equality establishes complete retained source identities for this diagnostic pair, not stable full-record metadata signatures or a final-search acceptance.",
    }
    write_new_json(reconciliation_path(partition), receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", required=True, choices=PARTITIONS)
    args = parser.parse_args()
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise SystemExit("Run this source workflow through the shared browser runner.")
    receipt = run_pair(args.partition)
    print(json.dumps({"status": "ok", "partition": args.partition, "source_total": receipt["pass_artifacts"][0]["source_total"], "stable_ids": receipt["stable_id_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
