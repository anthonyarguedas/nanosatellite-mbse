#!/usr/bin/env python3
"""Execute the predeclared OATD Pilot 004 P-only shared harvest once."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import queries

PILOT = "004"
PLAN_SCHEMA = "oatd-pilot-004-event-plan/v1"
RECEIPT_SCHEMA = "oatd-pilot-004-run-receipt/v1"
ADAPTER_ROOT = Path.home() / "agent-tools"
ADAPTER_PATH = ADAPTER_ROOT / "internet/skills/browser/scripts/search_oatd.py"
ADAPTER_FILES = {
    "entrypoint": ADAPTER_PATH,
    "browser_helpers": ADAPTER_PATH.with_name("_browser_search_utils.py"),
    "output_loader": ADAPTER_PATH.with_name("_output_utils.py"),
    "output_implementation": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_output_utils.py"
    ),
    "merge_contract": (
        ADAPTER_ROOT
        / "academic-api-search/skills/academic-api-search/scripts/_merge_contract.py"
    ),
}
SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_ROOT = SCRIPT_DIR.parents[3]
REPOSITORY_ROOT = SLR1_ROOT.parents[1]
PILOT_REASON = (
    "OATD Pilot 004 current-schedule shared-population validation. "
    "This is not a final search."
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "oatd_pilot004_execution_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load the OATD adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def expected_screenshot_paths(output: Path) -> dict[str, Path]:
    return {
        "search_page": output.with_name(f"{output.stem}.search-page.png"),
        "results_page": output.with_name(f"{output.stem}.results-page.png"),
    }


def validate_plan(
    plan: dict[str, Any], plan_path: Path, pilot_root: Path
) -> tuple[dict[str, Any], Path, Path, Path]:
    events = plan.get("events")
    if (
        plan.get("schema_version") != PLAN_SCHEMA
        or plan.get("pilot") != PILOT
        or plan.get("protocol_commit") != queries.PROTOCOL_COMMIT
        or plan.get("do_not_merge") is not True
        or not isinstance(events, list)
        or len(events) != 1
    ):
        raise RuntimeError("Unexpected OATD Pilot 004 event plan")
    event = events[0]
    if (
        event.get("event_id") != "P-shared"
        or event.get("source_submission") != "P"
        or event.get("query") != queries.P_QUERY
        or event.get("query_sha256") != text_sha256(queries.P_QUERY)
        or event.get("query_characters") != len(queries.P_QUERY)
        or event.get("shared_population_harvest") is not True
        or event.get("language") != "English"
        or event.get("language_source_value") != "(en OR eng OR english)"
        or event.get("year_start") != 2011
        or event.get("year_end") != 2026
        or event.get("page_size") != 100
        or event.get("limit") != 2000
        or event.get("max_pages") != 30
    ):
        raise RuntimeError("The predeclared P-only source event changed")

    adapter = load_adapter()
    adapter_plan = plan.get("adapter")
    if (
        not isinstance(adapter_plan, dict)
        or adapter_plan.get("id") != adapter.ADAPTER_ID
        or adapter_plan.get("version") != adapter.ADAPTER_VERSION
        or adapter.ADAPTER_VERSION != "10"
        or adapter_plan.get("mandatory_automatic_screenshots") is not True
        or adapter_plan.get("screenshot_opt_out") is not False
    ):
        raise RuntimeError("The predeclared OATD adapter contract changed")
    declared_adapter_files = adapter_plan.get("files")
    if not isinstance(declared_adapter_files, dict):
        raise RuntimeError("The adapter file bindings are missing")
    for name, path in ADAPTER_FILES.items():
        declared = declared_adapter_files.get(name)
        if not isinstance(declared, dict) or declared.get("sha256") != file_sha256(
            path
        ):
            raise RuntimeError(f"The OATD adapter changed after predeclaration: {name}")

    scripts = plan.get("source_affecting_scripts")
    if not isinstance(scripts, dict):
        raise RuntimeError("Source-affecting script bindings are missing")
    for relative, digest in scripts.items():
        path = REPOSITORY_ROOT / relative
        if not path.is_file() or digest != file_sha256(path):
            raise RuntimeError(f"A source-affecting script changed: {relative}")

    local_descriptor = plan.get("local_matching_plan")
    if not isinstance(local_descriptor, dict):
        raise RuntimeError("The local matching plan descriptor is missing")
    local_plan = pilot_root / local_descriptor["path"]
    if not local_plan.is_file() or file_sha256(local_plan) != local_descriptor.get(
        "sha256"
    ):
        raise RuntimeError("The local matching plan bytes changed")
    loaded_local = adapter.load_local_matching_plan(local_plan)
    if (
        loaded_local.plan_sha256 != local_descriptor.get("plan_sha256")
        or tuple(expression.expression_id for expression in loaded_local.expressions)
        != queries.SCHEDULE_IDS
        or {
            expression.expression_id: expression.expression
            for expression in loaded_local.expressions
        }
        != queries.LOCAL_SCHEDULE
    ):
        raise RuntimeError("The local matching plan semantics changed")

    if (
        event.get("output") != "searches/P-shared.json"
        or event.get("checkpoint") != "searches/checkpoint/P-shared.checkpoint.json"
        or local_descriptor.get("path") != "searches/local-matching-plan.json"
    ):
        raise RuntimeError("The source output, checkpoint, or local-plan path changed")
    output = pilot_root / event["output"]
    checkpoint = pilot_root / event["checkpoint"]
    if output.parent != pilot_root / "searches" or checkpoint.parent != (
        pilot_root / "searches" / "checkpoint"
    ):
        raise RuntimeError("The source output or checkpoint path is unsafe")
    screenshots = expected_screenshot_paths(output)
    expected_declared = {
        key: str(path.relative_to(pilot_root)) for key, path in screenshots.items()
    }
    if event.get("screenshots") != expected_declared:
        raise RuntimeError("The mandatory screenshot names changed")
    if (
        plan_path.resolve() == output.resolve()
        or local_plan.resolve() == output.resolve()
    ):
        raise RuntimeError("A plan path collides with the source output")
    return event, local_plan, checkpoint, output


def command(
    event: dict[str, Any], local_plan: Path, checkpoint: Path, output: Path
) -> list[str]:
    values = [
        "uv",
        "run",
        str(ADAPTER_PATH),
        "--query",
        event["query"],
        "--language",
        event["language"],
        "--year-start",
        str(event["year_start"]),
        "--year-end",
        str(event["year_end"]),
        "--page-size",
        str(event["page_size"]),
        "--limit",
        str(event["limit"]),
        "--max-pages",
        str(event["max_pages"]),
        "--timeout",
        str(event["timeout_seconds"]),
        "--page-delay-seconds",
        str(event["page_delay_seconds"]),
        "--detail-delay-seconds",
        str(event["detail_delay_seconds"]),
        "--busy-retries",
        str(event["busy_retries"]),
        "--busy-retry-delay-seconds",
        str(event["busy_retry_delay_seconds"]),
        "--shared-population-harvest",
        "--local-matching-plan",
        str(local_plan),
        "--checkpoint-path",
        str(checkpoint),
        "--output-path",
        str(output),
        "--prisma-run-id",
        "slr1-oatd-p004-P-shared",
        "--prisma-review-id",
        "slr1",
        "--prisma-strategy-reference",
        "slr1-oatd-p-only-local-schedule-pilot-v1",
        "--prisma-strategy-version",
        event["local_matching_plan_sha256"],
        "--prisma-phase",
        "identification",
        "--prisma-coverage-scope",
        "partition",
        "--prisma-partition-id",
        "P-shared",
        "--prisma-partition-label",
        "OATD P-only shared population pilot",
        "--prisma-partition-description",
        event["purpose"],
    ]
    if checkpoint.exists():
        values.append("--resume")
    return values


def validate_screenshot_receipt(artifact: dict[str, Any], output: Path) -> None:
    receipt = artifact.get("output_metadata", {}).get("screenshots")
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema_version") != "oatd-automatic-screenshots/v1"
        or receipt.get("automatic") is not True
        or receipt.get("opt_out_available") is not False
        or receipt.get("same_directory_as_json") is not True
    ):
        raise RuntimeError(
            "The OATD source artifact lacks mandatory screenshot evidence"
        )
    for key, path in expected_screenshot_paths(output).items():
        evidence = receipt.get(key)
        if (
            not path.is_file()
            or not isinstance(evidence, dict)
            or evidence.get("file_name") != path.name
            or evidence.get("sha256") != file_sha256(path)
            or not isinstance(evidence.get("width"), int)
            or evidence["width"] < 1
            or not isinstance(evidence.get("height"), int)
            or evidence["height"] < 1
            or evidence.get("full_page") is not True
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            raise RuntimeError(f"The OATD {key} screenshot receipt is invalid")


def validate_source_success(
    adapter: Any,
    artifact: dict[str, Any],
    event: dict[str, Any],
    output: Path,
) -> None:
    metadata = artifact.get("output_metadata")
    results = artifact.get("results")
    total = artifact.get("total")
    shared = (
        metadata.get("shared_population_harvest")
        if isinstance(metadata, dict)
        else None
    )
    source_population = (
        shared.get("source_population") if isinstance(shared, dict) else None
    )
    local = metadata.get("local_matching") if isinstance(metadata, dict) else None
    if (
        artifact.get("schema_version") != "academic-search-result/v1"
        or artifact.get("requested_query") != event["query"]
        or artifact.get("executed_query")
        != (
            f"{event['query']} AND language:(en OR eng OR english) AND "
            "pub_dt:[2011-01-01T00:00:00Z TO 2026-12-31T23:59:59Z]"
        )
        or not isinstance(total, int)
        or isinstance(total, bool)
        or total < 1
        or not isinstance(results, list)
        or len(results) != total
        or len({record.get("paperId") for record in results}) != total
        or not isinstance(metadata, dict)
        or metadata.get("status") != "success"
        or metadata.get("retrieval_complete") is not True
        or metadata.get("require_complete") is not True
        or metadata.get("strict_complete_pass_count") != 2
        or metadata.get("strict_stable_record_id_set_reconciled") is not True
        or metadata.get("source_population_total") != total
        or metadata.get("page_size") != 100
        or metadata.get("observed_exact_query_echo") is not True
        or not isinstance(source_population, dict)
        or source_population.get("source_reported_total") != total
        or source_population.get("two_complete_id_passes_reconciled") is not True
        or not isinstance(local, dict)
        or local.get("plan_sha256")
        != load(output.parent / "local-matching-plan.json").get("plan_sha256")
        or local.get("mode") != "annotation_only_no_source_record_exclusion"
        or local.get("local_nonmatches_remain_unresolved_for_exclusion") is not True
    ):
        raise RuntimeError("The OATD shared-population source artifact is incomplete")
    expressions = local.get("expressions")
    if (
        not isinstance(expressions, list)
        or [item.get("id") for item in expressions] != list(queries.SCHEDULE_IDS)
        or any(
            item.get("retained_source_population_records") != total
            or sum(
                item.get(key, -total)
                for key in (
                    "local_match_count",
                    "visible_fields_nonmatch_count",
                    "unresolved_missing_required_field_count",
                )
            )
            != total
            for item in expressions
        )
        or any(
            record.get("localMatching", {}).get("exclusion_status")
            != "unresolved_for_exclusion"
            for record in results
        )
    ):
        raise RuntimeError("The nine local schedule annotations are incomplete")
    validate_screenshot_receipt(artifact, output)
    if not adapter._is_strict_complete_oatd_result(artifact):
        raise RuntimeError("The adapter strict verifier rejected its source artifact")
    if not adapter.verify_commit_gated_publication(output, artifact):
        raise RuntimeError("The terminal OATD publication marker did not verify")


def mark_pilot_only(
    artifact: dict[str, Any], output: Path, adapter: Any
) -> dict[str, Any]:
    original_sha256 = file_sha256(output)
    marker = adapter.oatd_output_commit_marker_path(output)
    marker_sha256 = file_sha256(marker)
    artifact["do_not_merge"] = True
    metadata = artifact["output_metadata"]
    metadata["merge_eligible"] = False
    metadata["normalized_merge_eligible"] = False
    metadata["pilot_only"] = True
    metadata["non_mergeable_reason"] = PILOT_REASON
    prisma = metadata.get("prisma_search_run")
    if isinstance(prisma, dict):
        prisma["report_ready"] = False
        reasons = prisma.setdefault("report_readiness_reasons", [])
        if "pilot_non_mergeable" not in reasons:
            reasons.append("pilot_non_mergeable")
    artifact["pilot_context"] = {
        "schema_version": "oatd-pilot-004-source-artifact/v1",
        "pilot": PILOT,
        "event_id": "P-shared",
        "source_submission": "P only",
        "local_schedule_annotation_count": len(queries.SCHEDULE_IDS),
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "non_mergeable_reason": PILOT_REASON,
        "original_marker_verified_before_pilot_marking": True,
        "original_source_artifact_sha256": original_sha256,
        "original_commit_marker_sha256": marker_sha256,
    }
    write_atomic(output, artifact)
    revocation = Path(f"{marker}.revoked")
    try:
        with revocation.open("xb") as handle:
            handle.write(b"oatd-pilot-artifact-terminal-marker-revoked\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise RuntimeError(f"Refusing to overwrite {revocation}") from error
    if adapter.verify_commit_gated_publication(output, load(output)):
        raise RuntimeError("Pilot marking failed to revoke merge eligibility")
    return {
        "source_artifact_original_sha256": original_sha256,
        "source_artifact_pilot_sha256": file_sha256(output),
        "commit_marker": str(marker.relative_to(output.parent.parent)),
        "commit_marker_sha256": marker_sha256,
        "revocation_marker": str(revocation.relative_to(output.parent.parent)),
        "revocation_marker_sha256": file_sha256(revocation),
    }


def run(plan_path: Path, pilot_root: Path, receipt_path: Path) -> int:
    plan = load(plan_path)
    event, local_plan, checkpoint, output = validate_plan(plan, plan_path, pilot_root)
    screenshots = expected_screenshot_paths(output)
    marker = output.with_name(f".{output.name}.OATD_COMMIT.json")
    revocation = Path(f"{marker}.revoked")
    if any(
        os.path.lexists(path)
        for path in (output, marker, revocation, *screenshots.values())
    ):
        raise RuntimeError("Refusing to overwrite an existing OATD Pilot 004 output")
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    started = now()
    resumed = checkpoint.exists()
    process = subprocess.run(
        command(event, local_plan, checkpoint, output), check=False
    )
    outcome: dict[str, Any] = {
        "event_id": event["event_id"],
        "started_at_utc": started,
        "completed_at_utc": now(),
        "return_code": process.returncode,
        "resumed_from_checkpoint": resumed,
        "checkpoint_exists": checkpoint.is_file(),
        "output_exists": output.is_file(),
        "search_page_screenshot_exists": screenshots["search_page"].is_file(),
        "results_page_screenshot_exists": screenshots["results_page"].is_file(),
    }
    if process.returncode != 0 or not output.is_file():
        receipt = {
            "schema_version": RECEIPT_SCHEMA,
            "source": plan["source"],
            "pilot": PILOT,
            "protocol_commit": queries.PROTOCOL_COMMIT,
            "status": "stopped_on_source_or_adapter_failure",
            "do_not_merge": True,
            "started_at_utc": started,
            "completed_at_utc": now(),
            "event_plan": str(plan_path.relative_to(pilot_root)),
            "outcomes": [outcome],
        }
        write_atomic(receipt_path, receipt)
        return 1

    adapter = load_adapter()
    artifact = load(output)
    validate_source_success(adapter, artifact, event, output)
    marking = mark_pilot_only(artifact, output, adapter)
    checkpoint_value = load(checkpoint)
    outcome.update(
        {
            "contract_complete": True,
            "source_total": artifact["total"],
            "records_retained": len(artifact["results"]),
            "checkpoint_completed_ids": len(checkpoint_value.get("completed_ids", [])),
            "checkpoint_sha256": file_sha256(checkpoint),
            "screenshots": {
                key: {
                    "path": str(path.relative_to(pilot_root)),
                    "sha256": file_sha256(path),
                }
                for key, path in screenshots.items()
            },
            "pilot_marking": marking,
        }
    )
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "source": plan["source"],
        "pilot": PILOT,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "status": "complete",
        "do_not_merge": True,
        "started_at_utc": started,
        "completed_at_utc": now(),
        "event_plan": str(plan_path.relative_to(pilot_root)),
        "predeclared_event_count": 1,
        "completed_event_count": 1,
        "outcomes": [outcome],
    }
    write_atomic(receipt_path, receipt)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-plan", type=Path, required=True)
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args.event_plan, args.pilot_root, args.receipt)
    except Exception as error:
        print(" ".join(str(error).split())[:1000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
