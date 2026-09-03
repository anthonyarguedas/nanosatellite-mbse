#!/usr/bin/env python3
"""Recover Scopus abstracts for accepted final PSR records by canonical EID."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PLAN_SCHEMA = "slr1-scopus-final-psr-abstract-follow-up-plan/v1"
RECEIPT_SCHEMA = "slr1-scopus-final-psr-abstract-follow-up-receipt/v1"
ENRICHMENT_SCHEMA = "slr1-scopus-final-psr-abstract-enrichment/v1"
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = Path(__file__).resolve()
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_scopus.py"
SCOPUS_ADVANCED_URL = "https://www.scopus.com/pages/search/publications?type=advanced"
PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
BATCH_SIZE = 50


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_ids(values: set[str]) -> str:
    result = hashlib.sha256()
    for value in sorted(values):
        encoded = value.encode("utf-8")
        result.update(len(encoded).to_bytes(8, "big"))
        result.update(encoded)
    return result.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def relative(path: Path) -> str:
    return str(path.resolve(strict=False).relative_to(REPOSITORY_ROOT))


def adapter_version() -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)["\']',
        ADAPTER.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    if match is None:
        raise ValueError("Cannot determine the Scopus adapter version")
    return match.group(1)


def source_records(input_dir: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    records: dict[str, dict[str, Any]] = {}
    artifacts: list[dict[str, Any]] = []
    for partition in PARTITIONS:
        path = input_dir / f"{partition}.json"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing regular Scopus artifact: {path}")
        value = load(path)
        metadata = value.get("output_metadata", {})
        rows = value.get("results")
        if (
            value.get("schema_version") != "academic-search-result/v1"
            or not isinstance(metadata, Mapping)
            or metadata.get("merge_eligible") is not True
            or not isinstance(rows, list)
        ):
            raise ValueError(f"Scopus artifact is not a final merge input: {path}")
        artifacts.append(
            {
                "partition_id": partition,
                "path": relative(path),
                "sha256": digest(path),
                "record_count": len(rows),
            }
        )
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Malformed Scopus row in {path}")
            paper_id = row.get("paperId")
            if not isinstance(paper_id, str) or not paper_id.startswith(
                "SCOPUS-PUBLICATION:"
            ):
                raise ValueError(f"Invalid Scopus publication ID in {path}")
            current = records.get(paper_id)
            if current is None or len(row.get("abstract") or "") > len(
                current.get("abstract") or ""
            ):
                records[paper_id] = row
    return records, artifacts


def eid_query(ids: list[str]) -> str:
    values = [
        "2-s2.0-" + identifier.removeprefix("SCOPUS-PUBLICATION:")
        for identifier in ids
    ]
    return "EID(" + " OR ".join(values) + ")"


def build_plan(input_dir: Path) -> dict[str, Any]:
    records, artifacts = source_records(input_dir)
    requested = sorted(
        identifier for identifier, row in records.items() if not row.get("abstract")
    )
    batches = [
        requested[index : index + BATCH_SIZE]
        for index in range(0, len(requested), BATCH_SIZE)
    ]
    return {
        "schema_version": PLAN_SCHEMA,
        "created_at_utc": now(),
        "source": "Scopus",
        "review_namespace": "prior_secondary_reviews",
        "purpose": "metadata_enrichment_only",
        "discovery_ids_may_be_added": False,
        "input_directory": relative(input_dir),
        "input_artifacts": artifacts,
        "accepted_final_id_count": len(records),
        "accepted_final_id_set_sha256": digest_ids(set(records)),
        "already_recovered_abstract_count": sum(
            bool(row.get("abstract")) for row in records.values()
        ),
        "requested_record_count": len(requested),
        "requested_id_set_sha256": digest_ids(set(requested)),
        "batch_size": BATCH_SIZE,
        "adapter": {
            "id": "search_scopus",
            "version": adapter_version(),
            "sha256": digest(ADAPTER),
            "entrypoint": str(ADAPTER),
        },
        "runner": {
            "path": relative(SCRIPT_PATH),
            "sha256": digest(SCRIPT_PATH),
        },
        "settings": {
            "query": "canonical EID only",
            "year_bounds": None,
            "facets": [],
            "search_within": None,
            "result_scope": "Documents",
            "page_size": 50,
            "max_pages": 1,
            "full_abstracts": True,
            "strict_passes": 2,
        },
        "batches": [
            {
                "batch": index,
                "event_id": f"corrective-psr-scopus-abstract-follow-up-001-{index:03d}",
                "output_filename": f"batch-{index:03d}.json",
                "requested_ids": ids,
                "requested_id_set_sha256": digest_ids(set(ids)),
                "query": eid_query(ids),
            }
            for index, ids in enumerate(batches, start=1)
        ],
    }


def validate_plan(plan: Mapping[str, Any], *, verify_bindings: bool) -> None:
    if plan.get("schema_version") != PLAN_SCHEMA:
        raise ValueError("Unexpected Scopus abstract follow-up plan schema")
    batches = plan.get("batches")
    if not isinstance(batches, list):
        raise ValueError("Scopus abstract follow-up plan has no batches")
    requested: list[str] = []
    for index, batch in enumerate(batches, start=1):
        if not isinstance(batch, Mapping):
            raise ValueError("Malformed Scopus abstract follow-up batch")
        ids = batch.get("requested_ids")
        if (
            batch.get("batch") != index
            or batch.get("event_id")
            != f"corrective-psr-scopus-abstract-follow-up-001-{index:03d}"
            or batch.get("output_filename") != f"batch-{index:03d}.json"
            or not isinstance(ids, list)
            or not 1 <= len(ids) <= BATCH_SIZE
            or len(ids) != len(set(ids))
            or batch.get("query") != eid_query(ids)
            or batch.get("requested_id_set_sha256") != digest_ids(set(ids))
        ):
            raise ValueError(f"Invalid Scopus abstract follow-up batch {index}")
        requested.extend(ids)
    if (
        len(requested) != plan.get("requested_record_count")
        or len(requested) != len(set(requested))
        or digest_ids(set(requested)) != plan.get("requested_id_set_sha256")
    ):
        raise ValueError("Scopus abstract follow-up requested-ID ledger changed")
    if verify_bindings:
        adapter = plan.get("adapter", {})
        runner = plan.get("runner", {})
        if (
            adapter.get("sha256") != digest(ADAPTER)
            or adapter.get("version") != adapter_version()
            or runner.get("sha256") != digest(SCRIPT_PATH)
        ):
            raise ValueError("Scopus abstract follow-up implementation changed")
        input_dir = REPOSITORY_ROOT / str(plan.get("input_directory", ""))
        records, artifacts = source_records(input_dir)
        if (
            artifacts != plan.get("input_artifacts")
            or len(records) != plan.get("accepted_final_id_count")
            or digest_ids(set(records)) != plan.get("accepted_final_id_set_sha256")
        ):
            raise ValueError("Scopus abstract follow-up input artifacts changed")


def cdp_json(cdp_url: str, path: str, *, method: str = "GET") -> Any:
    request = urllib.request.Request(f"{cdp_url.rstrip('/')}{path}", method=method)
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def create_target(cdp_url: str) -> str:
    encoded = urllib.parse.quote(SCOPUS_ADVANCED_URL, safe="")
    created = cdp_json(cdp_url, f"/json/new?{encoded}", method="PUT")
    target_id = created.get("id") if isinstance(created, dict) else None
    if not isinstance(target_id, str) or not re.fullmatch(r"[A-Fa-f0-9]{32}", target_id):
        raise RuntimeError("Chrome did not create one Scopus target")
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        targets = cdp_json(cdp_url, "/json/list")
        target = next(
            (item for item in targets if isinstance(item, dict) and item.get("id") == target_id),
            None,
        )
        if isinstance(target, dict) and "Scopus" in str(target.get("title", "")):
            return target_id
        time.sleep(0.5)
    raise RuntimeError("The Scopus follow-up target did not become ready")


def close_target(cdp_url: str, target_id: str) -> bool:
    try:
        with urllib.request.urlopen(
            f"{cdp_url.rstrip('/')}/json/close/{target_id}", timeout=10
        ) as response:
            response.read()
    except Exception:
        return False
    return True


def adapter_command(
    plan: Mapping[str, Any],
    batch: Mapping[str, Any],
    output: Path,
    cdp_url: str,
    target_id: str,
) -> list[str]:
    ids = batch["requested_ids"]
    return [
        "uv",
        "run",
        str(ADAPTER),
        "--query",
        str(batch["query"]),
        "--result-scope",
        "documents",
        "--page-size",
        "50",
        "--limit",
        str(len(ids)),
        "--max-pages",
        "1",
        "--timeout",
        "300",
        "--page-delay-seconds",
        "0",
        "--require-complete",
        "--cdp-url",
        cdp_url,
        "--target-id",
        target_id,
        "--output-path",
        str(output),
        "--prisma-run-id",
        str(batch["event_id"]),
        "--prisma-review-id",
        "slr1-1.1-restart",
        "--prisma-strategy-reference",
        "slr1-scopus-psr-abstract-follow-up-v1",
        "--prisma-strategy-version",
        str(plan["adapter"]["sha256"]),
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        f"ABSTRACT-FOLLOW-UP-{batch['batch']:03d}",
        "--prisma-partition-label",
        f"ABSTRACT-FOLLOW-UP-{batch['batch']:03d}",
        "--prisma-partition-description",
        "Canonical EID-only metadata enrichment for accepted final PSR records",
    ]


def inspect_artifact(path: Path, batch: Mapping[str, Any]) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        return {"accepted": False, "artifact_written": False}
    value = load(path)
    rows = value.get("results")
    metadata = value.get("output_metadata", {})
    ids = [row.get("paperId") for row in rows] if isinstance(rows, list) else []
    abstract_capture_valid = bool(
        isinstance(rows, list)
        and all(
            isinstance(row, dict)
            and (
                (
                    bool(row.get("abstract"))
                    and row.get("abstract_source") == "native_scopus_result_page"
                    and row.get("abstract_detail_verified") is True
                    and row.get("abstract_not_available") is False
                )
                or (
                    not row.get("abstract")
                    and row.get("abstract_source") == "not_rendered"
                    and row.get("abstract_not_available") is True
                )
            )
            for row in rows
        )
    )
    accepted = bool(
        value.get("total") == len(batch["requested_ids"])
        and metadata.get("retrieval_complete") is True
        and metadata.get("merge_eligible") is True
        and len(ids) == len(set(ids))
        and set(ids) == set(batch["requested_ids"])
        and abstract_capture_valid
    )
    return {
        "accepted": accepted,
        "artifact_written": True,
        "artifact_sha256": digest(path),
        "total": value.get("total"),
        "returned_id_set_sha256": digest_ids(set(ids)),
        "full_abstract_count": sum(
            bool(row.get("abstract")) for row in rows if isinstance(row, dict)
        )
        if isinstance(rows, list)
        else 0,
        "verified_missing_abstract_count": sum(
            not row.get("abstract") for row in rows if isinstance(row, dict)
        )
        if isinstance(rows, list)
        else 0,
        "abstract_capture_valid": abstract_capture_valid,
        "status": metadata.get("status"),
        "error_stage": metadata.get("error_stage"),
        "error_reason": metadata.get("error_reason"),
    }


def write_create_only(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_plan(
    plan_path: Path,
    output_dir: Path,
    receipt_path: Path,
    enrichment_path: Path,
    settle_seconds: float,
) -> int:
    plan = load(plan_path)
    validate_plan(plan, verify_bindings=True)
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"Refusing to reuse {output_dir}")
    output_dir.mkdir(parents=True)
    cdp_url = os.environ.get("BH_CDP_URL", "http://127.0.0.1:9222")
    outcomes: list[dict[str, Any]] = []
    for index, batch in enumerate(plan["batches"]):
        if index and settle_seconds:
            time.sleep(settle_seconds)
        output = output_dir / batch["output_filename"]
        target_id: str | None = None
        exit_code: int | None = None
        target_closed = False
        try:
            target_id = create_target(cdp_url)
            completed = subprocess.run(
                adapter_command(plan, batch, output, cdp_url, target_id),
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            exit_code = completed.returncode
            inspected = inspect_artifact(output, batch)
        except Exception as error:
            inspected = {
                "accepted": False,
                "artifact_written": output.is_file(),
                "runner_failure": type(error).__name__,
            }
        finally:
            if target_id is not None:
                target_closed = close_target(cdp_url, target_id)
        outcome = {
            "batch": batch["batch"],
            "event_id": batch["event_id"],
            "requested_record_count": len(batch["requested_ids"]),
            "requested_id_set_sha256": batch["requested_id_set_sha256"],
            "output": batch["output_filename"] if output.is_file() else None,
            "exit_code": exit_code,
            "target_identifier_retained": False,
            "target_close_requested": target_closed,
            **inspected,
        }
        outcomes.append(outcome)
        print(
            json.dumps(
                {
                    "batch": batch["batch"],
                    "accepted": outcome["accepted"],
                    "total": outcome.get("total"),
                    "abstracts": outcome.get("full_abstract_count"),
                    "missing": outcome.get("verified_missing_abstract_count"),
                }
            ),
            flush=True,
        )
    complete = all(outcome["accepted"] for outcome in outcomes)
    enrichment_rows: list[dict[str, Any]] = []
    if complete:
        for batch, outcome in zip(plan["batches"], outcomes):
            path = output_dir / batch["output_filename"]
            for row in load(path)["results"]:
                enrichment_rows.append(
                    {
                        "paper_id": row["paperId"],
                        "abstract": row.get("abstract") or None,
                        "abstract_not_available": row.get("abstract_not_available"),
                        "abstract_source": row.get("abstract_source"),
                        "abstract_detail_verified": row.get(
                            "abstract_detail_verified"
                        ),
                        "follow_up_event_id": batch["event_id"],
                        "follow_up_artifact": relative(path),
                        "follow_up_artifact_sha256": outcome["artifact_sha256"],
                    }
                )
        if len(enrichment_rows) != plan["requested_record_count"]:
            raise ValueError("Scopus abstract enrichment row count changed")
        enrichment = {
            "schema_version": ENRICHMENT_SCHEMA,
            "source": "Scopus",
            "review_namespace": "prior_secondary_reviews",
            "purpose": "metadata_enrichment_only",
            "plan": relative(plan_path),
            "plan_sha256": digest(plan_path),
            "complete": True,
            "requested_record_count": plan["requested_record_count"],
            "full_abstract_count": sum(
                bool(row["abstract"]) for row in enrichment_rows
            ),
            "verified_missing_abstract_count": sum(
                not row["abstract"] for row in enrichment_rows
            ),
            "records": sorted(enrichment_rows, key=lambda row: row["paper_id"]),
        }
        write_create_only(enrichment_path, enrichment)
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "source": "Scopus",
        "review_namespace": "prior_secondary_reviews",
        "purpose": "metadata_enrichment_only",
        "plan": relative(plan_path),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "started_from_accepted_final_id_count": plan["accepted_final_id_count"],
        "requested_record_count": plan["requested_record_count"],
        "attempted_batch_count": len(outcomes),
        "accepted_batch_count": sum(outcome["accepted"] for outcome in outcomes),
        "complete": complete,
        "discovery_ids_added": 0,
        "target_identifier_retained": False,
        "enrichment": relative(enrichment_path) if complete else None,
        "enrichment_sha256": digest(enrichment_path) if complete else None,
        "outcomes": outcomes,
        "completed_at_utc": now(),
    }
    write_create_only(receipt_path, receipt)
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--input-dir", type=Path, required=True)
    plan_parser.add_argument("--output", type=Path, required=True)
    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--plan", type=Path, required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--receipt", type=Path, required=True)
    run_parser.add_argument("--enrichment", type=Path, required=True)
    run_parser.add_argument("--settle-seconds", type=float, default=15.0)
    args = parser.parse_args()
    if args.command == "plan":
        plan = build_plan(args.input_dir.resolve(strict=True))
        validate_plan(plan, verify_bindings=False)
        write_create_only(args.output, plan)
        print(
            json.dumps(
                {
                    "status": "saved",
                    "requested_records": plan["requested_record_count"],
                    "batches": len(plan["batches"]),
                }
            )
        )
        return 0
    if args.command == "check":
        validate_plan(load(args.plan), verify_bindings=True)
        print(json.dumps({"status": "ok"}))
        return 0
    return run_plan(
        args.plan.resolve(strict=True),
        args.output_dir.resolve(strict=False),
        args.receipt.resolve(strict=False),
        args.enrichment.resolve(strict=False),
        args.settle_seconds,
    )


if __name__ == "__main__":
    raise SystemExit(main())
