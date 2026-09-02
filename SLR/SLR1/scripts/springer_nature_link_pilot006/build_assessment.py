#!/usr/bin/env python3
"""Assess Springer Pilot 006 shared-browser readiness evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from run_pilot import DEFAULT_ADAPTER, PILOT_ROOT

DEFAULT_PLAN = PILOT_ROOT / "searches" / "event-plan-v4.json"
DEFAULT_RECEIPT = PILOT_ROOT / "searches" / "run-receipt.json"
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "assessment.json"
CONCURRENT_HELPER = DEFAULT_ADAPTER.with_name("_springer_concurrent_cdp.py")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected one JSON object in {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_adapter(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        "springer_p006_assessment_adapter", path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Springer adapter from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_screenshots(
    output: Path, screenshots: Any
) -> tuple[list[str], list[dict[str, Any]]]:
    errors = []
    receipts = []
    if (
        not isinstance(screenshots, Mapping)
        or screenshots.get("schema_version") != "springer-automatic-screenshots/v1"
        or screenshots.get("automatic") is not True
        or screenshots.get("no_opt_out") is not True
    ):
        return [f"Invalid screenshot contract for {output.name}"], receipts
    for key, suffix in (
        ("search_page", ".search-page.png"),
        ("results_page", ".results-page.png"),
    ):
        evidence = screenshots.get(key)
        path = output.with_name(output.stem + suffix)
        if not isinstance(evidence, Mapping) or evidence.get("path") != path.name:
            errors.append(f"Invalid {key} receipt for {output.name}")
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if (
            not data.startswith(b"\x89PNG\r\n\x1a\n")
            or evidence.get("sha256") != digest
            or not isinstance(evidence.get("width"), int)
            or evidence.get("width") < 1
            or not isinstance(evidence.get("height"), int)
            or evidence.get("height") < 1
            or evidence.get("browser_chrome_captured") is not False
            or evidence.get("complete_page_url_retained") is not False
            or evidence.get("session_identifiers_retained") is not False
        ):
            errors.append(f"Invalid {key} PNG for {output.name}")
        receipts.append(
            {
                "json": output.name,
                "kind": key,
                "file_name": path.name,
                "sha256": digest,
                "width": evidence.get("width"),
                "height": evidence.get("height"),
            }
        )
    return errors, receipts


def build(
    root: Path,
    plan_path: Path,
    receipt_path: Path,
    adapter_path: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    plan = load(plan_path)
    receipt = load(receipt_path)
    adapter = load_adapter(adapter_path)
    if (
        plan.get("schema_version") != "springer-nature-link-pilot006-event-plan/v4"
        or plan.get("adapter_minimum_version") != 12
        or plan.get("shared_controls", {}).get("browser_mode")
        != "target_scoped_shared_cdp"
        or len(plan.get("events", [])) != 3
    ):
        errors.append("Final shared-browser plan changed")
    if (
        receipt.get("status") != "complete"
        or receipt.get("plan_sha256") != file_sha256(plan_path)
        or receipt.get("event_count") != 3
        or receipt.get("adapter", {}).get("adapter_version") != "12"
    ):
        errors.append("Run receipt is incomplete")

    event_results = {}
    screenshot_receipts = []
    for event in plan["events"]:
        output = root / "searches" / event["output"]
        try:
            artifact = load(output)
            metadata = artifact["output_metadata"]
            route_summary = metadata["detail_route_aliases"]
            route_evidence = route_summary["evidence"]
            prisma = metadata["prisma_search_run"]
            if (
                artifact.get("source") != "Springer Nature Link"
                or artifact.get("executed_query") != event["query"]
                or artifact.get("total") != event["expected_source_total"]
                or len(artifact.get("results", []))
                != event["expected_results_retrieved"]
                or metadata.get("status") != "success"
                or metadata.get("retrieval_complete") is not True
                or metadata.get("merge_eligible") is not True
                or metadata.get("browser_transport") != "target_scoped_shared_cdp"
                or metadata.get("normal_output_commit_state") != "marker_required"
                or route_summary.get("raw_card_path_passes_reconciled") is not True
                or len(route_evidence) != 1
                or prisma.get("report_ready") is not True
                or prisma.get("adapter", {}).get("adapter_version") != "12"
            ):
                errors.append(f"Completion contract changed for {event['event_id']}")
            route = route_evidence[0]
            if (
                route.get("source_card_url") != event["expected_source_card_url"]
                or route.get("resolved_detail_url")
                != event["expected_resolved_detail_url"]
                or route.get("canonical_link") != event["expected_canonical_link"]
                or route.get("date_status") != event["expected_date_status"]
                or route.get("resolved_date") != event["expected_detail_date"]
            ):
                errors.append(f"Route or date evidence changed for {event['event_id']}")
            if artifact["results"]:
                record = artifact["results"][0]
                if (
                    record.get("sourceCardUrl") != event["expected_source_card_url"]
                    or record.get("resolvedDetailUrl")
                    != event["expected_resolved_detail_url"]
                    or record.get("detailCanonicalLink")
                    != event["expected_canonical_link"]
                    or record.get("exactDateFilterStatus")
                    != event["expected_date_status"]
                ):
                    errors.append(
                        f"Normalized route fields changed for {event['event_id']}"
                    )
            elif event["expected_date_status"] != "excluded":
                errors.append(
                    f"Unexpected empty retained result for {event['event_id']}"
                )
            screenshot_errors, screenshots = validate_screenshots(
                output, metadata.get("screenshots")
            )
            errors.extend(screenshot_errors)
            screenshot_receipts.extend(screenshots)
            if not adapter.is_complete_output_publication(output, None):
                errors.append(
                    f"Terminal publication marker failed for {event['event_id']}"
                )
            event_results[event["event_id"]] = {
                "artifact": event["output"],
                "sha256": file_sha256(output),
                "source_total": artifact["total"],
                "results_retrieved": len(artifact["results"]),
                "browser_transport": metadata.get("browser_transport"),
                "canonical_link": route.get("canonical_link"),
                "date_status": route.get("date_status"),
                "resolved_date": route.get("resolved_date"),
                "prisma_report_ready": prisma.get("report_ready"),
            }
        except (
            KeyError,
            OSError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            errors.append(f"Could not validate {event['event_id']}: {error}")

    failures = []
    for path in sorted((root / "searches" / "failures").glob("*.json")):
        failure = load(path)
        failures.append(
            {
                "artifact": str(path.relative_to(root)),
                "event_id": failure.get("event_id"),
                "returncode": failure.get("returncode"),
                "stderr": failure.get("stderr"),
            }
        )
    success = not errors
    return {
        "schema_version": "springer-nature-link-pilot006-assessment/v1",
        "pilot": "006",
        "source": "Springer Nature Link",
        "status": "complete" if success else "error",
        "diagnostic_only": True,
        "do_not_merge": True,
        "decisions": {
            "target_scoped_shared_browser": (
                "accepted_as_default_rendered_transport" if success else "unresolved"
            ),
            "strict_complete_publication": "accepted" if success else "unresolved",
            "nature_canonical_mapping": "accepted_end_to_end"
            if success
            else "unresolved",
            "exact_day_inclusion": "accepted" if success else "unresolved",
            "unresolved_day_retention": "accepted" if success else "unresolved",
            "post_cutoff_exclusion": "accepted" if success else "unresolved",
            "source_final_search_readiness": "accepted" if success else "unresolved",
        },
        "concurrency_finding": {
            "root_cause": (
                "Playwright browser-level CDP attachment waits for every existing page "
                "to initialize. One active foreign tab blocked new connections before "
                "Springer policy or page allocation ran."
            ),
            "repair": (
                "Adapter version 12 uses an invocation-local browser-harness daemon "
                "that creates, attaches, and closes only its own shared-Chrome target."
            ),
            "native_capture_boundary": (
                "Native CSV requests retain the Playwright transport because download "
                "handling is outside the target-scoped rendered backend."
            ),
        },
        "events": event_results,
        "screenshots": {
            "validated_png_count": len(screenshot_receipts),
            "all_sibling_paths": len(screenshot_receipts) == 6,
            "receipts": screenshot_receipts,
        },
        "adapter": {
            "adapter_version": adapter.ADAPTER_VERSION,
            "adapter_script_sha256": file_sha256(adapter_path),
            "concurrent_helper_sha256": file_sha256(CONCURRENT_HELPER),
        },
        "retained_failed_attempts": failures,
        "retained_failed_attempt_count": len(failures),
        "failed_attempt_interpretation": (
            "Four null attempts record browser transport setup failures. They reached "
            "no accepted source query and supplied no source total or record."
        ),
        "plans": {
            "final": {
                "artifact": str(plan_path.relative_to(root)),
                "sha256": file_sha256(plan_path),
            },
            "attached_subprocess": "searches/event-plan.json",
            "fresh_visible": "searches/event-plan-v2.json",
            "dedicated_attached": "searches/event-plan-v3.json",
        },
        "run_receipt": {
            "artifact": str(receipt_path.relative_to(root)),
            "sha256": file_sha256(receipt_path),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    assessment = build(args.pilot_root, args.plan, args.receipt, args.adapter)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(assessment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"status": assessment["status"], "errors": assessment["errors"]}, indent=2
        )
    )
    return 0 if assessment["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
