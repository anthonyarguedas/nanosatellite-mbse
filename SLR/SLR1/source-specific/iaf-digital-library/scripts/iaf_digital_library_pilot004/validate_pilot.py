#!/usr/bin/env python3
"""Validate IAF Pilot 004 and its accepted source guideline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from assess import THRESHOLD
from assess import build as build_assessment
from plan import (
    CHANGED_IDS,
    PILOT_DIR,
    SLR1_DIR,
    validate_plan_payload,
)
from queries import (
    C1_FIXED_TERMS,
    EF_TERMS,
    EH_TERMS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    MH_TERMS,
    P_TERMS,
    R_TERMS,
    TPRECISE_TERMS,
)

EXPECTED = {
    "BG1": {
        "cells": 17,
        "event_sum": 5,
        "raw_union": 4,
        "window_union": 4,
        "ids": [
            "iaf-digital-library:IAC-2014:21335",
            "iaf-digital-library:IAC-2015:29581",
            "iaf-digital-library:IAC-2017:41414",
            "iaf-digital-library:IAC-2019:50318",
        ],
    },
    "BG2": {
        "cells": 14,
        "event_sum": 5,
        "raw_union": 4,
        "window_union": 2,
        "ids": [
            "iaf-digital-library:IAC-2025:100501",
            "iaf-digital-library:IAC-2025:97295",
        ],
    },
    "BC1": {
        "cells": 7,
        "event_sum": 11,
        "raw_union": 9,
        "window_union": 6,
        "ids": [
            "iaf-digital-library:IAC-2017:41414",
            "iaf-digital-library:IAC-2021:63351",
            "iaf-digital-library:IAC-2021:64716",
            "iaf-digital-library:IAC-2023:79393",
            "iaf-digital-library:IAC-2024:88922",
            "iaf-digital-library:IAC-2025:96552",
        ],
    },
    "BT2": {
        "cells": 48,
        "event_sum": 15,
        "raw_union": 6,
        "window_union": 5,
        "ids": [
            "iaf-digital-library:IAC-2017:39760",
            "iaf-digital-library:IAC-2021:64212",
            "iaf-digital-library:IAC-2023:79271",
            "iaf-digital-library:IAC-2024:87490",
            "iaf-digital-library:IAC-2025:95462",
        ],
    },
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def markdown_link_errors(markdown: Path) -> list[str]:
    errors = []
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        local = target.split("#", 1)[0]
        if local and not (markdown.parent / local).resolve().exists():
            errors.append(f"Missing Markdown link in {markdown}: {target}")
    return errors


def protocol_membership_errors(protocol: Path) -> list[str]:
    expected = {
        "Population": P_TERMS,
        "High-specificity EPS": EH_TERMS,
        "Functional or analytical EPS": EF_TERMS,
        "High-specificity MBSE": MH_TERMS,
        "Broad structured model": MB_TERMS,
        "Systems-engineering relationship or concern": R_TERMS,
        "Fixed precise reusable model or template": GMODEL_FIXED_TERMS,
        "Mission-independence marker": GMISSION_TERMS,
        "Exact mission-independent artifact": GMISSION_EXACT_TERMS,
        "Fixed structural reusable artifact": GSTRUCTURE_FIXED_TERMS,
        "Product-line or product-family marker": GPRODUCT_TERMS,
        "Exact product model": GPRODUCT_EXACT_TERMS,
        "Variation marker": GVARIATION_TERMS,
        "Fixed conservative central asset": C1_FIXED_TERMS,
        "Domain-specific modeling-language marker": GDSL_TERMS,
        "Precise tailoring": TPRECISE_TERMS,
    }
    lines = protocol.read_text(encoding="utf-8").splitlines()
    errors = []
    for label, terms in expected.items():
        matches = [line for line in lines if line.startswith(f"- **{label} ")]
        if len(matches) != 1:
            errors.append(f"The protocol has {len(matches)} {label} definitions")
            continue
        observed = tuple(re.findall(r"`([^`]+)`", matches[0])[1:])
        if observed != terms:
            errors.append(f"Canonical terms differ from the protocol for {label}")
    return errors


def validate(root: Path, guideline: Path) -> dict[str, Any]:
    errors: list[str] = []
    searches = root / "searches"
    plan_path = searches / "cell-plan.json"
    plan = load(plan_path)
    errors.extend(validate_plan_payload(plan))
    errors.extend(
        protocol_membership_errors(SLR1_DIR / "protocol-discovery-and-appraisal.md")
    )

    receipt = load(searches / "run-receipt.json")
    if (
        receipt.get("status") != "complete"
        or receipt.get("selected_partitions") != list(CHANGED_IDS)
        or receipt.get("predeclared_cell_count") != 86
        or receipt.get("completed_cell_count") != 86
        or receipt.get("outcome_count") != 86
        or receipt.get("source_attempt_count") != 85
        or receipt.get("reused_existing_cell_count") != 1
        or receipt.get("retained_failure_artifacts") != []
    ):
        errors.append("The complete live run receipt changed")

    regenerated, regenerated_threshold = build_assessment(root, plan_path)
    if regenerated.get("status") != "complete" or regenerated.get("errors"):
        errors.extend(
            f"Regenerated assessment: {error}"
            for error in regenerated.get("errors", [])
        )
    assessment = load(searches / "assessment.json")
    threshold = load(searches / "threshold-investigations.json")
    if (
        assessment.get("status") != "complete"
        or assessment.get("decision")
        != "accept_lossless_no_proximity_branch_cell_translation"
        or assessment.get("source_artifact_count") != 86
        or assessment.get("retained_failure_artifacts") != []
    ):
        errors.append("The saved assessment decision changed")
    if assessment.get("entries") != regenerated.get("entries"):
        errors.append("The saved assessment entries differ from source artifacts")
    if threshold != regenerated_threshold:
        errors.append("The saved threshold report differs from source artifacts")
    if (
        threshold.get("status") != "not_triggered"
        or threshold.get("threshold") != THRESHOLD
        or threshold.get("triggered_partitions") != []
    ):
        errors.append("The threshold result changed")

    for partition_id, expected in EXPECTED.items():
        entry = assessment.get("entries", {}).get(partition_id, {})
        if (
            entry.get("complete_cells") != expected["cells"]
            or entry.get("source_event_counts", {}).get("raw_source_total_sum")
            != expected["event_sum"]
            or entry.get("raw_paper_id_union", {}).get("deduplicated_count")
            != expected["raw_union"]
            or entry.get("diagnostic_window_paper_id_union", {}).get(
                "deduplicated_count"
            )
            != expected["window_union"]
            or entry.get("diagnostic_window_paper_id_union", {}).get("paper_ids")
            != expected["ids"]
        ):
            errors.append(f"The validated result changed for {partition_id}")

    changed_union = assessment.get("changed_partition_union", {})
    if (
        changed_union.get("partition_record_occurrences") != 17
        or changed_union.get("deduplicated_stable_ids") != 16
        or changed_union.get("cross_partition_intersections")
        != {"BG1_and_BC1": ["iaf-digital-library:IAC-2017:41414"]}
    ):
        errors.append("The changed-partition union changed")

    source_json = sorted((searches / "cells").glob("*/*.json"))
    ledgers = [
        path for path in source_json if path.name.endswith(".identity-ledger.json")
    ]
    artifacts = [
        path
        for path in source_json
        if not path.name.endswith(".identity-ledger.json")
        and not path.name.startswith(".")
    ]
    markers = sorted((searches / "cells").glob("*/.*.ACADEMIC_SEARCH_COMMIT.json"))
    cleanup_directories = list(
        (searches / "cells").glob("*/.ACADEMIC_SEARCH_OUTPUT_CLEANUP.*")
    )
    failures = list((searches / "failures").rglob("*.json"))
    if len(artifacts) != 86 or len(ledgers) != 86 or len(markers) != 86:
        errors.append("The source artifact, ledger, or marker count changed")
    if cleanup_directories:
        errors.append("Transient output cleanup directories remain")
    if failures:
        errors.append("Unexpected retained source failures remain")

    guideline_text = guideline.read_text(encoding="utf-8")
    required_guideline = (
        "Use no proximity operator, pair expansion, or local pair check.",
        "F(G_model_fixed)",
        "F(G_mission_exact)",
        "F(G_structure_fixed)",
        "F(G_product_exact)",
        "F(G_DSL)",
        "`F(T_precise)`",
        "The complete wildcard schedule contains 158 cells.",
    )
    for value in required_guideline:
        if value not in guideline_text:
            errors.append(f"The guideline lacks accepted Pilot 004 text: {value}")
    for obsolete in ("PAIR(a,b)", "F(T2)", "Apply exact pair checking"):
        if obsolete in guideline_text:
            errors.append(f"The guideline retains active obsolete syntax: {obsolete}")

    pilot = root / "pilot.md"
    pilot_text = pilot.read_text(encoding="utf-8")
    for value in (
        "86 complete source cells",
        "| `BG1` | 17 | 5 | 4 | 4 |",
        "| `BG2` | 14 | 5 | 4 | 2 |",
        "| `BC1` | 7 | 11 | 9 | 6 |",
        "| `BT2` | 48 | 15 | 6 | 5 |",
        "Accept the deterministic branch and cell translation",
    ):
        if value not in pilot_text:
            errors.append(f"The pilot document lacks validated text: {value}")
    task_text = (SLR1_DIR / "TASKS.md").read_text(encoding="utf-8")
    if "**IAF-004: Pilot the schedule without proximity operators.**" not in task_text:
        errors.append("TASKS.md is not synchronized")

    errors.extend(markdown_link_errors(pilot))
    errors.extend(markdown_link_errors(guideline))

    return {
        "schema_version": "iaf-digital-library-pilot004-validation-report/v1",
        "status": "ok" if not errors else "error",
        "pilot": "004",
        "diagnostic_only": True,
        "do_not_merge": True,
        "checks": {
            "canonical_protocol_membership": "passed"
            if not any("protocol" in error.lower() for error in errors)
            else "failed",
            "lossless_cell_plan": "passed"
            if not validate_plan_payload(plan)
            else "failed",
            "pilot003_carry_forward": "passed"
            if plan.get("carry_forward", {}).get("all_query_cells_identical") is True
            else "failed",
            "strict_live_source_cells": "passed"
            if len(artifacts) == 86 and regenerated.get("status") == "complete"
            else "failed",
            "non_mergeable_source_artifacts": "passed"
            if not any("diagnostic status" in error for error in errors)
            else "failed",
            "stable_id_reconciliation": "passed"
            if not any("reconcile" in error for error in errors)
            else "failed",
            "threshold_investigation": "passed"
            if threshold.get("status") == "not_triggered"
            else "failed",
            "guideline_synchronized": "passed"
            if not any("guideline" in error.lower() for error in errors)
            else "failed",
            "task_synchronized": "passed"
            if not any("TASKS.md" in error for error in errors)
            else "failed",
            "local_markdown_links": "passed"
            if not any("Markdown link" in error for error in errors)
            else "failed",
        },
        "summary": {
            "complete_schedule_cells": 551,
            "carried_forward_cells": 465,
            "live_source_cells": 86,
            "source_artifacts": len(artifacts),
            "identity_ledgers": len(ledgers),
            "commit_markers": len(markers),
            "retained_failures": len(failures),
            "partition_results": EXPECTED,
            "changed_partition_record_occurrences": 17,
            "changed_partition_distinct_ids": 16,
            "proximity_operators": 0,
            "pair_expansions": 0,
            "wildcards": 0,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=PILOT_DIR)
    parser.add_argument("--guideline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.pilot_root, args.guideline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
