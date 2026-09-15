#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Validate mapped PQDT Pilot 005 labels through each exact browse route."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

import queries

SCHEMA = "pqdt-global-pilot005-candidate-validation/v1"
DEFAULT_PREFLIGHT = queries.PILOT_ROOT / "searches" / "preflight.json"
DEFAULT_MAP = queries.PILOT_ROOT / "searches" / "candidate-map.json"
DEFAULT_OUTPUT = queries.PILOT_ROOT / "searches" / "candidate-validation.json"
DEFAULT_FAILURE = (
    queries.PILOT_ROOT
    / "searches"
    / "failures"
    / "candidate-validation.NON_MERGEABLE_FAILURE.json"
)
ABSENT_LABEL_MESSAGE = (
    "PQDT did not expose exactly one selectable exact controlled-term label."
)


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def safe_error(error: BaseException) -> str:
    message = clean(error)
    if "target identities" in message or "adapter-owned Chrome page target" in message:
        return "The shared browser target inventory changed during owned-page setup."
    if re.search(r"(?i)accountid|_csrf|/abstract/[A-Za-z0-9]+/", message):
        return "Source interaction failed. URL and session details were omitted."
    return message


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pqdt_pilot005_candidate_adapter", queries.ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load PQDT adapter at {queries.ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_inputs(preflight_path: Path, map_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    preflight = queries.load_object(preflight_path)
    candidate_map = queries.load_object(map_path)
    if preflight.get("schema_version") != "pqdt-global-pilot005-preflight/v1":
        raise RuntimeError("Unexpected PQDT Pilot 005 preflight schema")
    if candidate_map.get("schema_version") != "pqdt-global-pilot005-candidate-map/v1":
        raise RuntimeError("Unexpected PQDT Pilot 005 candidate-map schema")
    if candidate_map.get("status") != "mapped_pending_exact_browse_validation":
        raise RuntimeError("PQDT candidate map is not ready for validation")
    pinned = preflight.get("pinned_inputs", {}).get("adapter", {})
    if pinned.get("sha256") != queries.file_sha256(queries.ADAPTER_PATH):
        raise RuntimeError("The PQDT adapter changed after predeclaration")
    candidates = candidate_map.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != candidate_map.get("candidate_count"):
        raise RuntimeError("PQDT candidate-map count changed")
    return preflight, candidate_map


def exception_chain(error: BaseException) -> list[str]:
    messages: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        messages.append(clean(current))
        current = current.__cause__ or current.__context__
    return messages


def compact_receipt(
    candidate: Mapping[str, Any], receipt: Mapping[str, Any]
) -> dict[str, Any]:
    expected_clause = candidate["executed_clause"]
    if receipt.get("executed_clause") != expected_clause:
        raise RuntimeError(
            f"Exact clause readback changed for {candidate['candidate_id']}"
        )
    return {
        **dict(candidate),
        "status": "verified_exact_browse_label",
        "product": receipt.get("product"),
        "vocabulary": receipt.get("vocabulary"),
        "vocabulary_key": receipt.get("vocabulary_key"),
        "term_id": receipt.get("term_id"),
        "term_id_state": receipt.get("term_id_state"),
        "vocabulary_version": receipt.get("vocabulary_version"),
        "version_state": receipt.get("version_state"),
        "hierarchy_state": receipt.get("hierarchy_state"),
        "expansion_state": receipt.get("expansion_state"),
        "browse_state": receipt.get("browse_state"),
        "selection_state": receipt.get("selection_state"),
        "browse_readback": receipt.get("browse_readback"),
        "selection_readback": receipt.get("selection_readback"),
        "executed_clause": receipt.get("executed_clause"),
    }


async def validate(
    preflight_path: Path,
    map_path: Path,
    output_path: Path,
    failure_path: Path,
    timeout_seconds: float,
) -> None:
    if output_path.exists():
        raise RuntimeError(f"Refusing to overwrite {output_path}")
    if failure_path.exists():
        raise RuntimeError(f"Refusing to overwrite {failure_path}")
    _, candidate_map = validate_inputs(preflight_path, map_path)
    adapter = load_adapter()
    from playwright.async_api import async_playwright

    started_at = adapter.utc_now()
    scope = None
    passes: list[list[dict[str, Any]]] = []
    try:
        async with async_playwright() as playwright, adapter._LeaseCleanup() as cleanup:
            lease = await adapter.open_owned_chrome_page(
                playwright,
                cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                headless=False,
                timeout_seconds=timeout_seconds,
                chrome_executable=None,
            )
            cleanup.lease = lease
            scope = adapter._PQDTScopeCleanup(
                lease.page, timeout_seconds=timeout_seconds
            )
            await scope.__aenter__()
            cleanup.scope = scope
            for _pass_number in (1, 2):
                current: list[dict[str, Any]] = []
                for candidate in candidate_map["candidates"]:
                    kind = "subject" if candidate["field"] == "PSUB" else "index_term"
                    try:
                        receipt = await adapter.validate_pqdt_controlled_term_live(
                            lease.page,
                            candidate["term"],
                            kind=kind,
                            timeout_seconds=timeout_seconds,
                        )
                    except adapter.PQDTMetadataError as error:
                        chain = exception_chain(error)
                        if ABSENT_LABEL_MESSAGE not in chain:
                            raise
                        current.append(
                            {
                                **candidate,
                                "status": "assigned_but_not_exact_browse_label",
                                "source_outcome": ABSENT_LABEL_MESSAGE,
                            }
                        )
                    else:
                        current.append(compact_receipt(candidate, receipt))
                passes.append(current)
    except Exception as error:
        evidence = getattr(error, "scope_evidence", None)
        failure = {
            "schema_version": "pqdt-global-pilot005-candidate-validation-failure/v1",
            "source": "ProQuest Dissertations & Theses Global",
            "pilot": "005",
            "status": "error",
            "diagnostic_only": True,
            "do_not_merge": True,
            "started_at_utc": started_at,
            "failed_at_utc": adapter.utc_now(),
            "stage": "exact_subject_and_index_term_validation",
            "error_type": type(error).__name__,
            "error": safe_error(error),
            "candidate_ids": [
                item["candidate_id"] for item in candidate_map["candidates"]
            ],
            "scope_restoration": (
                adapter._scope_evidence_dict(evidence)
                if isinstance(evidence, adapter.PQDTScopeEvidence)
                else None
            ),
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(
            json.dumps(failure, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        raise

    if len(passes) != 2 or passes[0] != passes[1]:
        raise RuntimeError("PQDT candidate validation changed across two complete passes")
    if scope is None or scope.restoration_verified is not True:
        raise RuntimeError("PQDT candidate validation did not verify scope restoration")
    verified = [item for item in passes[1] if item["status"] == "verified_exact_browse_label"]
    absent = [item for item in passes[1] if item["status"] != "verified_exact_browse_label"]
    artifact = {
        "schema_version": SCHEMA,
        "source": "ProQuest Dissertations & Theses Global",
        "source_id": "proquest_dissertations_theses_global",
        "platform": "ProQuest",
        "pilot": "005",
        "status": "complete_two_pass_exact_browse_readback",
        "diagnostic_only": True,
        "do_not_merge": True,
        "started_at_utc": started_at,
        "completed_at_utc": adapter.utc_now(),
        "input_candidate_map": str(map_path.relative_to(queries.PILOT_ROOT)),
        "input_candidate_map_sha256": queries.file_sha256(map_path),
        "passes": 2,
        "candidate_count": len(passes[1]),
        "verified_exact_label_count": len(verified),
        "assigned_but_absent_count": len(absent),
        "candidates": passes[1],
        "field_summary": {
            field: {
                "candidate_count": sum(item["field"] == field for item in passes[1]),
                "verified_count": sum(
                    item["field"] == field
                    and item["status"] == "verified_exact_browse_label"
                    for item in passes[1]
                ),
            }
            for field in ("PSUB", "IF")
        },
        "source_contract": {
            "term_ids": "not_exposed",
            "vocabulary_versions": "not_published",
            "hierarchy": "not_exposed",
            "explosion": "unknown_and_not_requested",
            "focus": "not_exposed",
            "major_topic": "not_exposed_and_not_requested",
            "scope": adapter._scope_evidence_dict(scope.evidence),
        },
        "pass_reconciliation": {
            "ordered_candidate_results_equal": passes[0] == passes[1],
            "pass_1_candidate_ids": [item["candidate_id"] for item in passes[0]],
            "pass_2_candidate_ids": [item["candidate_id"] for item in passes[1]],
        },
        "limitations": [
            "An exact browse label has no stable term ID or published vocabulary release.",
            "The flat browse surfaces expose no scope note, hierarchy, or explosion control.",
            "Assignment and exact-label readback do not establish marginal search value.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--candidate-map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--failure-output", type=Path, default=DEFAULT_FAILURE)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    asyncio.run(
        validate(
            args.preflight.expanduser().resolve(),
            args.candidate_map.expanduser().resolve(),
            args.output.expanduser().resolve(),
            args.failure_output.expanduser().resolve(),
            args.timeout,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
