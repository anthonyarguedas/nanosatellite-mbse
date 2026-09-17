#!/usr/bin/env python3

"""Validate the complete Compendex controlled-vocabulary Pilot 004 bundle."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import queries

SLR1 = Path(__file__).resolve().parents[4]
PILOT_ROOT = SLR1 / "source-specific/compendex/pilots/004"
SEARCHES = PILOT_ROOT / "searches"
GUIDELINE = SLR1 / "source-specific/compendex/source-specific-guidelines.md"
OUTPUT = SEARCHES / "validation-report.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def cell_projection(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in (
            "cell_id",
            "status",
            "query",
            "query_sha256",
            "total",
            "ordered_stable_accessions",
            "results",
            "controls",
            "terminal_page_contract",
            "native_ris",
        )
    }


def main() -> int:
    required = {
        "preflight": SEARCHES / "preflight.json",
        "assignments": SEARCHES / "assigned-controlled-terms.json",
        "candidates": SEARCHES / "ei-thesaurus-candidates.json",
        "comparison": SEARCHES / "value-comparison.json",
        "assessment": SEARCHES / "inclusion-assessment.json",
        "pilot": PILOT_ROOT / "pilot.md",
        "guideline": GUIDELINE,
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    check(not missing, f"Pilot 004 lacks required files: {missing!r}")
    failure_files = sorted(SEARCHES.glob("*.NON_MERGEABLE_FAILURE.json"))
    check(not failure_files, "Pilot 004 retains an active failure artifact")

    subprocess.run(
        ["git", "cat-file", "-e", f"{queries.PROTOCOL_COMMIT}^{{commit}}"],
        cwd=SLR1.parents[1],
        check=True,
        capture_output=True,
    )

    preflight = load(required["preflight"])
    assignments = load(required["assignments"])
    candidates = load(required["candidates"])
    comparison = load(required["comparison"])
    assessment = load(required["assessment"])
    expected_status = {
        "preflight": "complete",
        "assignments": "complete_two_pass_assignment_readback",
        "candidates": "complete_two_pass_readback",
        "comparison": "complete_two_pass_terminal_cell_comparison",
        "assessment": "complete",
    }
    artifacts = {
        "preflight": preflight,
        "assignments": assignments,
        "candidates": candidates,
        "comparison": comparison,
        "assessment": assessment,
    }
    for name, artifact in artifacts.items():
        check(artifact.get("status") == expected_status[name], f"{name} status changed")
        check(artifact.get("protocol_commit") == queries.PROTOCOL_COMMIT, f"{name} commit changed")
        check(artifact.get("do_not_merge") is True, f"{name} is not diagnostic")

    check(set(preflight["schedule"]) == set(queries.SCHEDULE_IDS), "Preflight schedule changed")
    for partition_id, entry in preflight["schedule"].items():
        query = queries.SOURCE_SCHEDULE[partition_id]
        check(entry["query"] == query, f"Preflight query changed for {partition_id}")
        check(
            entry["query_sha256"] == hashlib.sha256(query.encode()).hexdigest(),
            f"Preflight hash changed for {partition_id}",
        )
        check(entry["has_proximity"] is False, f"{partition_id} regained proximity")
        check(entry["has_wildcard"] is False, f"{partition_id} gained a wildcard")
    check(
        preflight["protocol_change"]["changed_partitions"]
        == list(queries.CHANGED_BY_PROTOCOL_COMMIT),
        "Protocol change boundary changed",
    )
    check(
        preflight["protocol_change"]["B1_change_state"]
        == "unchanged_by_protocol_commit",
        "B1 transition boundary changed",
    )
    check(
        preflight["B1"]["decomposition_is_lossless"] is True
        and preflight["B1"]["decomposition_truth_table_cases"] == 16,
        "B1 candidate-only decomposition proof changed",
    )

    check(assignments["selection"]["record_count"] == 11, "Selected assignment set changed")
    check(assignments["unique_controlled_term_count"] == 51, "Assigned term union changed")
    check(assignments["pass_reconciliation"]["ordered_assignments_equal"] is True, "Assignments changed across passes")
    expected_assignment_counts = {
        "Nanosatellites": 2,
        "Small satellites": 1,
        "Systems engineering": 7,
        "Modeling languages": 4,
        "SysML": 0,
    }
    observed_assignment_counts = {
        term: entry["assigned_record_count"]
        for term, entry in assignments["candidate_assignments"].items()
    }
    check(observed_assignment_counts == expected_assignment_counts, "Candidate assignments changed")
    check(
        assignments["context_qualified_M_H_assignment"]["assigned_record_count"] == 3,
        "Joint M_H assignments changed",
    )

    check(
        candidates["pass_reconciliation"]["ordered_candidate_results_equal"] is True,
        "Ei Thesaurus readback changed across passes",
    )
    check(candidates["adapter"]["version"] == "15", "Thesaurus adapter version changed")
    candidate_by_term = {item["term"]: item for item in candidates["candidates"]}
    expected_ids = {
        "Nanosatellites": "18096",
        "Small satellites": "3444",
        "Systems engineering": "8964",
        "Modeling languages": "18655",
        "SysML": "23054",
    }
    for term, term_id in expected_ids.items():
        item = candidate_by_term[term]
        check(
            item["status"] == "verified_exact_preferred_ei_thesaurus_term",
            f"Exact status changed for {term}",
        )
        check(item["term_id"] == term_id, f"Ei identity changed for {term}")
        check(item["field"] == "CV", f"Ei field changed for {term}")
        check(item["hierarchy_expansion"] == "not_requested_and_not_implicit", f"Expansion changed for {term}")
        check(item["scope_note"]["state"] in {"observed", "not_exposed"}, f"Scope state changed for {term}")
    for term in ("Model-based systems engineering", "CubeSat"):
        check(
            candidate_by_term[term]["status"]
            == "not_an_exact_preferred_ei_thesaurus_term",
            f"Absent preferred-term status changed for {term}",
        )

    check(set(comparison["cells"]) == set(queries.VALUE_CELLS), "Value cells changed")
    check(comparison["adapter"]["version"] == "15", "Value adapter version changed")
    check(
        "Adapter v15 accepts" in comparison["method"]["adapter_repair_state"],
        "Value comparison lacks the adapter repair state",
    )
    check(
        comparison["method"]["common_evidence_cutoff"]["state"] == "TBD",
        "The pilot invented a common evidence cutoff",
    )
    expected_totals = {
        "known-P-controlled": 3,
        "known-MH-controlled": 3,
        "known-SysML-controlled": 0,
        "B1-MH-candidate-only": 0,
        "B1-P-candidate-only": 0,
    }
    for cell_id, expected_total in expected_totals.items():
        entry = comparison["cells"][cell_id]
        check(entry["total"] == expected_total, f"Value total changed for {cell_id}")
        check(entry["passes_equal"] is True, f"Pass equality changed for {cell_id}")
        pass_values = []
        for pass_number in (1, 2):
            path = SEARCHES / "cells" / f"{cell_id}-pass{pass_number}.json"
            check(path.is_file(), f"Missing pass artifact {path}")
            value = load(path)
            check(value.get("do_not_merge") is True, f"{path.name} is not diagnostic")
            check(value.get("merge_eligible") is False, f"{path.name} is merge eligible")
            check(value.get("protocol_commit") == queries.PROTOCOL_COMMIT, f"{path.name} commit changed")
            check(value.get("pass") == pass_number, f"{path.name} pass label changed")
            check(value.get("query") == queries.VALUE_CELLS[cell_id], f"{path.name} query changed")
            check(value["adapter"]["version"] == "15", f"{path.name} adapter version changed")
            if expected_total > 0:
                check(
                    value["terminal_page_contract"]["fixed_adapter_outcome"] == "accepted",
                    f"{path.name} was not accepted by adapter v15",
                )
            pass_values.append(value)
        check(
            cell_projection(pass_values[0]) == cell_projection(pass_values[1]),
            f"Cell {cell_id} changed across passes",
        )
    check(
        comparison["comparison"]["candidate_only_union_count"] == 0
        and comparison["comparison"]["candidate_only_accessions"] == [],
        "Candidate-only union changed",
    )

    check(
        assessment["decision"] == "do_not_add_ei_thesaurus_supplement",
        "Assessment decision changed",
    )
    check(assessment["accepted_descriptors"] == [], "Assessment accepted a descriptor")
    check(
        assessment["adapter_repair"]["state"] == "validated_v15",
        "Assessment lacks the validated adapter repair",
    )
    check(
        assessment["schedule_provenance"]["superseded_proximity_results_used_for_value"] is False,
        "Assessment reused a superseded value set",
    )

    guideline = GUIDELINE.read_text(encoding="utf-8")
    pilot = required["pilot"].read_text(encoding="utf-8")
    for text, description in (
        (queries.PROTOCOL_COMMIT, "protocol commit"),
        ("F(T_precise)", "current tailoring block"),
        ("Pilot 004", "pilot checklist"),
        ("Add no Ei Thesaurus supplement", "controlled-vocabulary decision"),
        ("Adapter v15 now treats the interval as optional", "adapter repair"),
    ):
        check(text in guideline, f"Guideline lacks {description}")
    check("F(T2)" not in guideline, "Guideline retains the superseded T2 name")
    check("PAIR(a,b)" not in guideline, "Guideline retains superseded pair syntax")
    check("NEAR/5" not in guideline, "Guideline retains superseded Compendex proximity syntax")
    check(queries.PROTOCOL_COMMIT in pilot, "Pilot report lacks schedule provenance")
    check("candidate-only accession union is empty" in pilot, "Pilot report lacks value result")
    check("## Adapter repair validation" in pilot, "Pilot report lacks adapter repair validation")

    final_files = [
        path.name
        for path in (SLR1 / "source-specific/compendex/final-searches").iterdir()
        if path.name != ".gitkeep"
    ]
    check(not final_files, "Pilot 004 created a final-search artifact")

    for path in PILOT_ROOT.rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        check("/Users/" not in text, f"{path.name} retained an absolute private path")
        for marker in ("SEARCHID", "docidlist", "handlelist", "sessionid", "cookie"):
            check(marker.casefold() not in text.casefold(), f"{path.name} retained {marker}")

    report = {
        "schema_version": "compendex-controlled-vocabulary-pilot-validation/v1",
        "source": "Compendex",
        "pilot": "004",
        "status": "passed",
        "do_not_merge": True,
        "protocol_commit": queries.PROTOCOL_COMMIT,
        "checks": {
            "post_proximity_schedule": True,
            "assignment_two_pass": True,
            "thesaurus_two_pass": True,
            "value_cells_two_pass": True,
            "candidate_only_union_zero": True,
            "adapter_v15_repair": True,
            "all_artifacts_non_mergeable": True,
            "guideline_synchronized": True,
            "no_final_search": True,
            "no_private_paths_or_session_values": True,
        },
    }
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"validated {PILOT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
