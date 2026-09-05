#!/usr/bin/env python3
"""Run and validate one predeclared IEEE full-abstract final event."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
ADAPTER = Path.home() / "agent-tools/internet/skills/browser/scripts/search_ieee_xplore.py"
MARKER_TAG = "IEEE_COMMIT"
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def write_new(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def marker_path(output: Path) -> Path:
    return output.with_name(f".{output.name}.{MARKER_TAG}.json")


def screenshot_paths(output: Path) -> tuple[Path, Path]:
    return (
        output.with_name(f"{output.stem}.search-page.png"),
        output.with_name(f"{output.stem}.results-page.png"),
    )


def adapter_version() -> str:
    match = re.search(
        r'^ADAPTER_VERSION\s*=\s*["\']([^"\']+)',
        ADAPTER.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Cannot determine the IEEE adapter version")
    return match.group(1)


def validate_plan(plan: Mapping[str, Any], partition: str) -> Mapping[str, Any]:
    if (
        plan.get("schema_version") != "slr1-ieee-xplore-full-abstract-final-plan/v1"
        or plan.get("source_id") != "ieee_xplore"
        or plan.get("review_namespace") != "main"
        or plan.get("source_union_expected_partitions") != list(PARTITIONS)
        or plan.get("execution_policy", {}).get("skip_full_abstracts") is not False
        or plan.get("source_configuration", {}).get("publication_type_filter") is not None
        or plan.get("source_configuration", {}).get("full_abstracts") is not True
    ):
        raise ValueError("The IEEE full-abstract final plan has an invalid fixed contract")
    adapter = plan.get("adapter", {})
    if (
        adapter.get("version") != adapter_version()
        or adapter.get("sha256") != digest(ADAPTER)
    ):
        raise ValueError("The predeclared IEEE adapter changed")
    events = plan.get("events")
    if not isinstance(events, list):
        raise TypeError("The IEEE plan has no event schedule")
    matches = [event for event in events if isinstance(event, Mapping) and event.get("partition_id") == partition]
    if len(matches) != 1:
        raise ValueError(f"The IEEE plan does not contain exactly one {partition} event")
    event = matches[0]
    query = event.get("query")
    if (
        not isinstance(query, str)
        or event.get("query_sha256") != digest_text(query)
        or event.get("wildcard_count") != 0
        or event.get("require_complete") is not True
        or event.get("strict_passes") != 2
        or event.get("full_abstracts") is not True
        or event.get("full_abstract_expansion_required") is not True
        or event.get("source_publication_types") is not True
    ):
        raise ValueError(f"The IEEE {partition} event contract is invalid")
    return event


def command(plan: Mapping[str, Any], event: Mapping[str, Any], output: Path, cdp_url: str) -> list[str]:
    window = plan["date_window"]
    values = [
        "uv", "run", str(ADAPTER), "--query", str(event["query"]),
        "--publication-date-start", str(window["publication_date_start"]),
        "--publication-date-end", str(window["publication_date_end"]),
        "--scope", "documents", "--access-scope", "all", "--sort", "Oldest",
        "--page-size", str(event["page_size"]), "--limit", str(event["limit"]),
        "--max-pages", str(event["max_pages"]), "--timeout", str(event["timeout_seconds"]),
        "--page-delay-seconds", str(event["page_delay_seconds"]),
        "--detail-delay-seconds", str(event["detail_delay_seconds"]), "--require-complete",
        "--cdp-url", cdp_url, "--output-path", str(output),
        "--prisma-run-id", str(event["event_id"]),
        "--prisma-review-id", str(plan["review_id"]),
        "--prisma-strategy-reference", str(plan["strategy_reference"]),
        "--prisma-strategy-version", str(event["strategy_version"]),
        "--prisma-phase", str(plan["phase"]), "--prisma-coverage-scope", "partition",
        "--prisma-partition-id", str(event["partition_id"]),
        "--prisma-partition-label", str(event["partition_id"]),
        "--prisma-partition-description",
        f"IEEE Xplore full-abstract final direct discovery partition {event['partition_id']}",
    ]
    target = os.environ.get("IEEE_CDP_TARGET_ID")
    if target:
        values.extend(("--target-id", target))
    return values


def artifact_summary(output: Path, event: Mapping[str, Any]) -> dict[str, Any]:
    if not output.is_file() or output.is_symlink():
        return {"artifact_written": False, "valid": False, "validation_errors": ["missing_artifact"]}
    value = load(output)
    metadata = value.get("output_metadata")
    metadata = metadata if isinstance(metadata, Mapping) else {}
    rows = value.get("results")
    rows = rows if isinstance(rows, list) else []
    strict = metadata.get("ieee_strict_completion_receipt")
    strict = strict if isinstance(strict, Mapping) else {}
    errors: list[str] = []
    if (
        value.get("schema_version") != "academic-search-result/v1"
        or value.get("source") != "IEEE Xplore"
        or value.get("executed_query") != event.get("query")
        or metadata.get("status") != "success"
        or metadata.get("merge_eligible") is not True
        or metadata.get("retrieval_complete") is not True
    ):
        errors.append("result_contract")
    prisma = metadata.get("prisma_search_run")
    prisma = prisma if isinstance(prisma, Mapping) else {}
    staged = prisma.get("staged_counts")
    staged = staged if isinstance(staged, Mapping) else {}
    total = value.get("total")
    excluded = staged.get("client_side_exclusions")
    if (
        not isinstance(total, int)
        or not isinstance(excluded, int)
        or total != len(rows) + excluded
        or staged.get("source_reported_total") != total
        or staged.get("records_exported") != len(rows)
    ):
        errors.append("record_accounting")
    if (
        strict.get("status") != "success"
        or strict.get("passes_completed") != 2
        or strict.get("total_reconciled") is not True
        or strict.get("controls_reconciled") is not True
        or strict.get("ordered_ids_reconciled") is not True
        or strict.get("export_reconciled") is not True
    ):
        errors.append("strict_two_pass")
    abstracts = 0
    unavailable = 0
    expanded = 0
    types: dict[str, int] = {}
    ids: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            errors.append("malformed_row")
            continue
        identifier = row.get("paperId")
        abstract = row.get("abstract")
        document_type = row.get("documentType")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            errors.append("record_id")
        else:
            ids.add(identifier)
        if not isinstance(document_type, str) or not document_type.strip():
            errors.append("publication_type")
        else:
            types[document_type] = types.get(document_type, 0) + 1
        if not isinstance(abstract, str):
            errors.append("abstract_field")
        elif abstract:
            abstracts += 1
            status = row.get("abstract_full_text_status")
            if (
                row.get("abstract_source") != "IEEE Xplore rendered document page"
                or row.get("abstract_is_truncated") is not False
                or status not in {
                    "expanded_from_visible_source_control",
                    "source_rendered_complete_without_expansion",
                }
                or (len(abstract) == 2_003 and abstract.endswith("..."))
            ):
                errors.append("full_abstract")
            if status == "expanded_from_visible_source_control":
                expanded += 1
        elif row.get("abstract_not_available") is True:
            unavailable += 1
        else:
            errors.append("abstract_omission")
    screenshots = metadata.get("screenshots")
    screenshots = screenshots if isinstance(screenshots, Mapping) else {}
    screenshot_rows: list[dict[str, Any]] = []
    for key, path in zip(("search_page", "results_page"), screenshot_paths(output)):
        evidence = screenshots.get(key)
        valid = bool(
            path.is_file()
            and not path.is_symlink()
            and isinstance(evidence, Mapping)
            and evidence.get("path") == path.name
            and evidence.get("sha256") == digest(path)
        )
        if not valid:
            errors.append(f"{key}_screenshot")
        screenshot_rows.append({"kind": key, "path": path.name, "sha256": digest(path) if path.is_file() else None, "valid": valid})
    marker = marker_path(output)
    if not marker.is_file() or marker.is_symlink():
        errors.append("commit_marker")
    return {
        "artifact_written": True,
        "valid": not errors,
        "artifact_sha256": digest(output),
        "artifact_bytes": output.stat().st_size,
        "source_total": total,
        "retained_record_count": len(rows),
        "client_date_excluded_count": excluded,
        "full_abstract_count": abstracts,
        "source_abstract_not_available_count": unavailable,
        "expanded_full_abstract_count": expanded,
        "publication_type_counts": dict(sorted(types.items())),
        "missing_publication_type_count": sum(not isinstance(row, Mapping) or not str(row.get("documentType") or "").strip() for row in rows),
        "screenshots": screenshot_rows,
        "validation_errors": sorted(set(errors)),
    }


def run(plan_path: Path, output_dir: Path, receipt_dir: Path, partition: str, cdp_url: str) -> int:
    plan = load(plan_path)
    event = validate_plan(plan, partition)
    output = output_dir / str(event["output_filename"])
    receipt = receipt_dir / f"{partition}.json"
    occupied = (output, marker_path(output), *screenshot_paths(output), receipt)
    if any(path.exists() or path.is_symlink() for path in occupied):
        raise FileExistsError(f"Refusing to overwrite {partition} artifacts")
    started = now()
    completed = subprocess.run(command(plan, event, output, cdp_url), check=False, capture_output=True, text=True)
    summary = artifact_summary(output, event)
    success = completed.returncode == 0 and summary.get("valid") is True
    value = {
        "schema_version": "slr1-ieee-xplore-full-abstract-event-run/v1",
        "event_id": event["event_id"],
        "partition_id": partition,
        "plan": str(plan_path.resolve().relative_to(ROOT)),
        "plan_sha256": digest(plan_path),
        "adapter": plan["adapter"],
        "source_command_attempt_count": 1,
        "target_identifier_retained": False,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "exit_code": completed.returncode,
        "stdout_sha256": digest_text(completed.stdout),
        "stdout_bytes": len(completed.stdout.encode("utf-8")),
        "stderr_sha256": digest_text(completed.stderr),
        "stderr_bytes": len(completed.stderr.encode("utf-8")),
        "success": success,
        **summary,
    }
    write_new(receipt, value)
    print(json.dumps({
        "partition": partition,
        "success": success,
        "exit_code": completed.returncode,
        "source_total": summary.get("source_total"),
        "retained_records": summary.get("retained_record_count"),
        "full_abstracts": summary.get("full_abstract_count"),
        "expanded_abstracts": summary.get("expanded_full_abstract_count"),
        "missing_publication_types": summary.get("missing_publication_type_count"),
        "validation_errors": summary.get("validation_errors"),
    }))
    if completed.returncode != 0:
        print(completed.stderr.strip())
    return 0 if success else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    parser.add_argument("--partition", choices=PARTITIONS, required=True)
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9333")
    args = parser.parse_args()
    return run(args.plan, args.output_dir, args.receipt_dir, args.partition, args.cdp_url)


if __name__ == "__main__":
    raise SystemExit(main())
