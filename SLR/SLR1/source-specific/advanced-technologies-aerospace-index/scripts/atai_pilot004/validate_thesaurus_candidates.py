#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///

"""Validate selected assigned SUBJECT labels against ATAI Technology Thesaurus."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ADAPTER_PATH = (
    Path.home()
    / "agent-tools/internet/skills/browser/scripts/search_proquest_aerospace.py"
)
SOURCE_NAME = "Advanced Technologies & Aerospace Index"
CANDIDATES = (
    {
        "term": "Cubesat",
        "proposed_block": "P",
        "role": "Population descriptor whose label duplicates an existing CubeSat literal modulo case.",
    },
    {
        "term": "Nanosatellites",
        "proposed_block": "P",
        "role": "Population descriptor whose label duplicates an existing nanosatellites literal modulo case.",
    },
    {
        "term": "Small satellites",
        "proposed_block": "P",
        "role": "Population descriptor whose label duplicates an existing small satellites literal modulo case.",
    },
    {
        "term": "Model-based systems",
        "proposed_block": "M_H_candidate_context",
        "role": "Recurring model-based descriptor. It requires a systems-engineering context before it can supplement M_H.",
    },
    {
        "term": "Systems engineering",
        "proposed_block": "M_H_context_only",
        "role": "Generic systems-engineering descriptor. The protocol forbids using it alone for M_H.",
    },
    {
        "term": "Modelling",
        "proposed_block": "M_H_candidate_context",
        "role": "Generic modelling descriptor. It requires a systems-engineering context before it can supplement M_H.",
    },
)
EXPECTED_ABSENT_MESSAGE = (
    "ATAI did not expose exactly one selectable exact Technology Thesaurus descriptor."
)


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location("atai_pilot004_cv_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load ATAI adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


async def dismiss_restore_prompt(page: Any) -> bool:
    modal = page.locator("#restoresession_confirm:visible")
    if await modal.count() == 0:
        return False
    if await modal.count() != 1:
        raise RuntimeError("ATAI exposed ambiguous restore-session prompts.")
    dismiss = modal.locator("a:visible").filter(has_text=re.compile(r"^\s*Dismiss\s*$"))
    if await dismiss.count() != 1:
        raise RuntimeError("ATAI restore-session prompt lacked one Dismiss control.")
    await dismiss.click()
    await modal.wait_for(state="hidden")
    return True


def validate_harvest(harvest: Any) -> None:
    if not isinstance(harvest, dict) or harvest.get("status") != "complete_two_pass_readback":
        raise RuntimeError("The assigned-term harvest is incomplete.")
    assigned = {
        term
        for record in harvest.get("records", [])
        for term in record.get("rendered_indexing_terms", [])
    }
    missing = [candidate["term"] for candidate in CANDIDATES if candidate["term"] not in assigned]
    if missing:
        raise RuntimeError(f"Candidate terms were not assigned to selected records: {missing!r}")


def compact_receipt(receipt: dict[str, Any], candidate: dict[str, str]) -> dict[str, Any]:
    return {
        "term": candidate["term"],
        "proposed_block": candidate["proposed_block"],
        "role": candidate["role"],
        "status": "verified_exact_technology_thesaurus_descriptor",
        "product": receipt["product"],
        "vocabulary": receipt["vocabulary"],
        "vocabulary_key": receipt["vocabulary_key"],
        "term_id": receipt["term_id"],
        "term_id_state": receipt["term_id_state"],
        "vocabulary_version": receipt["vocabulary_version"],
        "version_state": receipt["version_state"],
        "hierarchy_state": receipt["hierarchy_state"],
        "expansion_state": receipt["expansion_state"],
        "browse_state": receipt["browse_state"],
        "selection_state": receipt["selection_state"],
        "browse_readback": receipt["browse_readback"],
        "selection_readback": receipt["selection_readback"],
        "executed_clause": receipt["executed_clause"],
    }


async def run_validation(
    harvest_path: Path,
    output_path: Path,
    failure_path: Path,
    timeout_seconds: float,
) -> None:
    adapter = load_adapter()
    harvest = json.loads(harvest_path.read_text())
    validate_harvest(harvest)
    from playwright.async_api import async_playwright

    started_at = adapter.utc_now()
    lease = None
    pass_results: list[list[dict[str, Any]]] = []
    prompt_dismissals = 0
    try:
        async with async_playwright() as playwright:
            try:
                lease = await adapter.open_proquest_owned_page(
                    playwright,
                    cdp_url=adapter.DEFAULT_LOCAL_CDP_URL,
                    target_id=None,
                    headless=False,
                    timeout_seconds=timeout_seconds,
                    chrome_executable=None,
                )
                for _pass_number in (1, 2):
                    current_pass: list[dict[str, Any]] = []
                    for candidate in CANDIDATES:
                        await adapter.navigate(
                            lease.page,
                            "https://www.proquest.com/ataindex/advanced",
                            timeout_seconds,
                        )
                        if await dismiss_restore_prompt(lease.page):
                            prompt_dismissals += 1
                        try:
                            receipt = await adapter.validate_atai_thesaurus_term_live(
                                lease.page,
                                candidate["term"],
                                timeout_seconds=timeout_seconds,
                            )
                        except adapter.ProQuestProtocolError as error:
                            if clean_text(error) != EXPECTED_ABSENT_MESSAGE:
                                raise
                            current_pass.append(
                                {
                                    **candidate,
                                    "status": "not_an_exact_technology_thesaurus_descriptor",
                                    "source_outcome": EXPECTED_ABSENT_MESSAGE,
                                }
                            )
                        else:
                            current_pass.append(compact_receipt(receipt, candidate))
                    pass_results.append(current_pass)
            finally:
                await adapter.close_proquest_owned_page(lease)
    except Exception as error:
        failure = {
            "schema_version": "atai-technology-thesaurus-candidate-failure/v1",
            "source": SOURCE_NAME,
            "pilot": "004",
            "status": "error",
            "do_not_merge": True,
            "started_at_utc": started_at,
            "failed_at_utc": adapter.utc_now(),
            "stage": "technology_thesaurus_candidate_validation",
            "error_type": type(error).__name__,
            "error": clean_text(error),
            "predeclared_terms": [candidate["term"] for candidate in CANDIDATES],
        }
        failure_path.parent.mkdir(parents=True, exist_ok=True)
        failure_path.write_text(json.dumps(failure, indent=2, ensure_ascii=False) + "\n")
        raise

    if len(pass_results) != 2 or pass_results[0] != pass_results[1]:
        raise RuntimeError("ATAI Technology Thesaurus candidate readback changed across passes.")
    verified = [item for item in pass_results[1] if item["status"].startswith("verified_")]
    absent = [item for item in pass_results[1] if item["status"].startswith("not_")]
    artifact = {
        "schema_version": "atai-technology-thesaurus-candidate-validation/v1",
        "source": SOURCE_NAME,
        "source_id": "proquest_aerospace_index",
        "platform": "ProQuest",
        "pilot": "004",
        "purpose": "Test whether recurring or concept-mapped SUBJECT terms assigned to seven selected records are exact Technology Thesaurus descriptors.",
        "status": "complete_two_pass_readback",
        "do_not_merge": True,
        "started_at_utc": started_at,
        "completed_at_utc": adapter.utc_now(),
        "input_harvest": str(harvest_path),
        "passes": 2,
        "prompt_dismissals": prompt_dismissals,
        "candidate_count": len(CANDIDATES),
        "verified_descriptor_count": len(verified),
        "absent_descriptor_count": len(absent),
        "candidates": pass_results[1],
        "pass_reconciliation": {
            "ordered_candidate_results_equal": pass_results[0] == pass_results[1],
            "pass_1_terms": [item["term"] for item in pass_results[0]],
            "pass_2_terms": [item["term"] for item in pass_results[1]],
        },
        "limitations": [
            "Exact descriptor readback does not publish a stable term ID or vocabulary version.",
            "No explosion, focus, or major-topic state is exposed.",
            "A descriptor label and record-level SUBJECT assignment do not by themselves prove marginal search recall.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--harvest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--failure-output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    asyncio.run(run_validation(args.harvest, args.output, args.failure_output, args.timeout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
