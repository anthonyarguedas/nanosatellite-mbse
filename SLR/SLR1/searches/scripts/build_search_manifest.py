#!/usr/bin/env python3
"""Build a machine-readable inventory of every new-run search JSON artifact.

Raw source files are read but never changed.  The manifest distinguishes a true
zero, count-only response, local preflight failure, and source service failure
so source errors cannot be misreported as zero-hit searches.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "eps-mbse-slr-2026"
WORKLOGS = {
    "Scopus": "SLR/SLR1/searches/worklogs/scopus.md",
    "IEEE Xplore": "SLR/SLR1/searches/worklogs/ieee-xplore.md",
    "Semantic Scholar": "SLR/SLR1/searches/worklogs/semantic-scholar.md",
    "Google Scholar": "SLR/SLR1/searches/worklogs/google-scholar.md",
    "Coverage-gap audit": "SLR/SLR1/searches/worklogs/coverage-gap.md",
}

ROWS: list[dict[str, Any]] = []


def add(path: str, query_id: str, source: str, stream: str | None, artifact_kind: str, status: str, retained: bool, assessment: str, *, source_total_override: Any = "USE_FILE", role: str = "search_result") -> None:
    ROWS.append({
        "path": path, "query_id": query_id, "source": source, "stream": stream,
        "artifact_kind": artifact_kind, "status": status, "retained_for_merge": retained,
        "assessment": assessment, "source_total_override": source_total_override, "role": role,
    })


# Scopus (18 JSON artifacts: 15 successful query results and 3 local preflight failures)
add("searches/scopus/S-A1_preflight-path-validation-failure.json", "S-A1-preflight", "Scopus", "A", "preflight_failure", "failed_preflight_no_api_request", False, "Local path validation failed before an API request; retry S-A1 succeeded.", source_total_override=None)
add("searches/scopus/S-A2_preflight-path-validation-failure.json", "S-A2-preflight", "Scopus", "A", "preflight_failure", "failed_preflight_no_api_request", False, "Local path validation failed before an API request; retry S-A2 succeeded.", source_total_override=None)
add("searches/scopus/S-B1_preflight-path-validation-failure.json", "S-B1-preflight", "Scopus", "B", "preflight_failure", "failed_preflight_no_api_request", False, "Local path validation failed before an API request; retry S-B1 succeeded.", source_total_override=None)
for file_name, query_id, stream, retained, assessment in [
    ("S-A1_pilot_r1.json", "S-A1", "A", True, "Final accepted EPS-name × MBSE primary query."),
    ("S-A2_pilot_r1.json", "S-A2", "A", True, "Final accepted functional EPS/power-energy × system-model primary query."),
    ("S-B1_pilot_r1.json", "S-B1", "B", False, "Superseded by population-wildcard refinement S-B1r1."),
    ("S-B2_pilot.json", "S-B2", "B", False, "Superseded by retained B3/B4 alternatives."),
    ("S-V1_pilot.json", "S-V1", "A sensitivity", False, "V&V sensitivity; baseline duplicate."),
    ("S-O1_pilot.json", "S-O1", "A sensitivity", False, "Outcome sensitivity; baseline duplicates."),
    ("S-A3_pilot-explicit-mbse-functional-eps.json", "S-A3", "A refinement", False, "Precision refinement; duplicate-only."),
    ("S-A4_pilot-structured-bridge-eps.json", "S-A4", "A refinement", False, "Structured-bridge refinement; duplicate-only."),
    ("S-B3_pilot-systems-engineering-relation.json", "S-B3", "B", True, "Final accepted systems-engineering-relation Stream-B query."),
    ("S-A5_pilot-population-wildcard.json", "S-A5", "A refinement", False, "Wildcard check identical to S-A1."),
    ("S-B4_pilot-population-wildcard.json", "S-B4", "B", True, "Final accepted structured-model wildcard Stream-B query."),
    ("S-A2r1_pilot-population-wildcard.json", "S-A2r1", "A refinement", False, "Wildcard check identical to S-A2."),
    ("S-B1r1_pilot-population-wildcard.json", "S-B1r1", "B", True, "Final accepted population-wildcard Stream-B query."),
    ("S-A6_pilot-small-satellite-explicit-eps-sensitivity.json", "S-A6", "A population sensitivity", False, "Small-satellite sensitivity; duplicate."),
    ("S-A7_pilot-small-satellite-functional-eps-sensitivity.json", "S-A7", "A population sensitivity", False, "Small-satellite sensitivity; no additional target-population candidate."),
]:
    add(f"searches/scopus/{file_name}", query_id, "Scopus", stream, "search_result", "success", retained, assessment)

# IEEE Xplore (23 JSON artifacts; count-only is an audit response, not no hits).
for file_name, query_id, stream, kind, status, retained, assessment in [
    ("I-A1-C1-count.json", "I-A1-C1", "A", "count_only", "success_count_only", False, "Count-only predecessor of full I-A1-F1."),
    ("I-A1-F1-full.json", "I-A1-F1", "A", "full_result", "success", True, "Final accepted EPS-name × MBSE query."),
    ("I-A2-C1-count.json", "I-A2-C1", "A", "count_only", "success_count_only", False, "Count-only predecessor of full I-A2-F1."),
    ("I-A2-F1-full.json", "I-A2-F1", "A", "full_result", "success", True, "Final accepted functional EPS/power-energy query."),
    ("I-B1-C1-count.json", "I-B1-C1", "B", "count_only", "success_count_only", False, "Count-only predecessor of full I-B1-F1."),
    ("I-B1-F1-full.json", "I-B1-F1", "B", "full_result", "success", True, "Final accepted EPS-free MBSE Stream-B query."),
    ("I-B2-C1-count.json", "I-B2-C1", "B", "count_only", "success_count_only", False, "Count-only predecessor of full I-B2-F1."),
    ("I-B2-F1-full.json", "I-B2-F1", "B", "full_result", "success", True, "Final accepted EPS-free structured-model Stream-B query."),
    ("I-V1-C1-count.json", "I-V1-C1", "A sensitivity", "count_only", "success_count_only", False, "V&V sensitivity count."),
    ("I-V1-F1-full.json", "I-V1-F1", "A sensitivity", "full_result", "success", False, "V&V sensitivity duplicate of final primary identities."),
    ("I-O1-C1-count.json", "I-O1-C1", "A sensitivity", "count_only", "success_count_only", False, "Outcome sensitivity count."),
    ("I-O1-F1-full.json", "I-O1-F1", "A sensitivity", "full_result", "success", False, "Outcome sensitivity duplicates final primary identities."),
    ("I-A3-C1-count.json", "I-A3-C1", "A refinement", "count_only", "success_count_only", False, "Structured-model refinement count."),
    ("I-A3-F1-full.json", "I-A3-F1", "A refinement", "full_result", "success", False, "Refinement duplicate of I-A1."),
    ("I-A4-C1-count.json", "I-A4-C1", "A", "count_only", "success_count_only", False, "Count-only predecessor of full I-A4-F1."),
    ("I-A4-F1-full.json", "I-A4-F1", "A", "full_result", "success", True, "Final accepted budget-wording Stream-A query."),
    ("I-B3-C1-count.json", "I-B3-C1", "B sensitivity", "count_only", "success_count_only", False, "Population-spelling sensitivity count."),
    ("I-B3-F1-full.json", "I-B3-F1", "B sensitivity", "full_result", "success", False, "Population-spelling sensitivity duplicate."),
    ("I-A5-C1-count.json", "I-A5-C1", "A", "count_only", "success_count_only", False, "Count-only predecessor of full I-A5-F1."),
    ("I-A5-F1-full.json", "I-A5-F1", "A", "full_result", "success", True, "Final accepted EPS-component Stream-A query."),
    ("I-A6-C1-count.json", "I-A6-C1", "A refinement", "count_only", "success_count_only", False, "Broader electrical-power sensitivity count."),
    ("I-A6-F1-full.json", "I-A6-F1", "A refinement", "full_result", "success", False, "Poor-precision duplicate/noisy refinement."),
    ("I-B4-C1-count.json", "I-B4-C1", "B sensitivity", "count_only", "success_zero", False, "Successful endpoint-reported zero; no full successor."),
]:
    add(f"searches/ieee-xplore/{file_name}", query_id, "IEEE Xplore", stream, kind, status, retained, assessment)

# Semantic Scholar: parseable fallback files contain 0 but all were HTTP 403 failures before page one.
for file_name, query_id, stream, assessment in [
    ("SS-A1-P1-cubesat-eps-mbse.json", "SS-A1-P1", "A", "HTTP 403 before page 1; no source total or records."),
    ("SS-A2-P1-nanosatellite-power-sysml.json", "SS-A2-P1", "A", "HTTP 403 before page 1; no source total or records."),
    ("SS-A3-P1-cubesat-mbse-budget.json", "SS-A3-P1", "A", "HTTP 403 before page 1; no source total or records."),
    ("SS-A4-P1-cubesat-reference-model-electrical-power.json", "SS-A4-P1", "A", "HTTP 403 before page 1; no source total or records."),
    ("SS-B1-P1-nanosatellite-mbse.json", "SS-B1-P1", "B", "HTTP 403 before page 1; no source total or records."),
    ("SS-V1-P1-cubesat-sysml-verification-power.json", "SS-V1-P1", "A sensitivity", "HTTP 403 before page 1; no source total or records."),
    ("SS-A5-R1-cubesat-power-budget-interface-sysml.json", "SS-A5-R1", "A", "HTTP 403 before page 1; no source total or records."),
    ("SS-B2-R1-cubesat-system-reference-model.json", "SS-B2-R1", "B", "HTTP 403 before page 1; no source total or records."),
    ("SS-B3-R1-cubesat-digital-engineering-requirements-traceability.json", "SS-B3-R1", "B", "HTTP 403 before page 1; no source total or records."),
]:
    add(f"searches/semantic-scholar/{file_name}", query_id, "Semantic Scholar", stream, "service_failure_artifact", "service_failure_http_403", False, assessment, source_total_override=None)

# Google Scholar: explicit errors before result rank 1; no UI total exists.
for file_name, query_id, stream, assessment in [
    ("GS-A1_eps-explicit-structured-model.error.json", "GS-A1", "A", "Cannot Fetch from Google Scholar before rank 1/UI total."),
    ("GS-B1_eps-free-embedded-thread.error.json", "GS-B1", "B", "Cannot Fetch from Google Scholar before rank 1/UI total."),
    ("GS-P1_chapter-exact-title-recovery.error.json", "GS-P1", "recovery", "Cannot Fetch from Google Scholar before rank 1/UI total."),
    ("GS-R1_reference-model-lineage.error.json", "GS-R1", "B recovery", "Cannot Fetch from Google Scholar before rank 1/UI total."),
    ("GS-V1_eps-traceability-vv.error.json", "GS-V1", "A sensitivity", "Cannot Fetch from Google Scholar before rank 1/UI total."),
    ("GS-D1_digital-engineering.error.json", "GS-D1", "B recovery", "Cannot Fetch from Google Scholar before rank 1/UI total."),
]:
    add(f"searches/google-scholar/{file_name}", query_id, "Google Scholar", stream, "service_failure_artifact", "service_failure_before_rank_1", False, assessment, source_total_override=None)

# Coverage-gap source query artifacts (28) and two generated audit outputs (30 total JSON files in that directory).
for file_name, query_id, source, stream, kind, status, retained, assessment, source_total_override in [
    ("S-CG-M1-P1-model-centric-driven-stream-b.json", "S-CG-M1-P1", "Scopus", "B", "search_result", "success", False, "Duplicate-only model-centric/driven probe.", "USE_FILE"),
    ("I-CG-M1-C1-model-centric-driven-stream-b-count.json", "I-CG-M1-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor; duplicate-only full result.", "USE_FILE"),
    ("I-CG-M1-F1-model-centric-driven-stream-b-full.json", "I-CG-M1-F1", "IEEE Xplore", "B", "full_result", "success", False, "Duplicate-only model-centric/driven probe.", "USE_FILE"),
    ("S-CG-M2-P1-oosem-opm-stream-b.json", "S-CG-M2-P1", "Scopus", "B", "search_result", "success", False, "OOSEM/OPM acronym-confounded audit probe.", "USE_FILE"),
    ("I-CG-M2-C1-oosem-opm-stream-b-count.json", "I-CG-M2-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor; duplicate-only full result.", "USE_FILE"),
    ("I-CG-M2-F1-oosem-opm-stream-b-full.json", "I-CG-M2-F1", "IEEE Xplore", "B", "full_result", "success", False, "Duplicate-only OOSEM/OPM probe.", "USE_FILE"),
    ("S-CG-M3-P1-digital-thread-twin-stream-b.json", "S-CG-M3", "Scopus", "B", "search_result", "success", True, "Final retained broad digital-thread/digital-twin Stream-B coverage input.", "USE_FILE"),
    ("I-CG-M3-C1-digital-thread-twin-stream-b-count.json", "I-CG-M3-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor of retained I-CG-M3.", "USE_FILE"),
    ("I-CG-M3-F1-digital-thread-twin-stream-b-full.json", "I-CG-M3", "IEEE Xplore", "B", "full_result", "success", True, "Final retained broad digital-thread/digital-twin Stream-B coverage input.", "USE_FILE"),
    ("S-CG-M4-P1-executable-integration-stream-b.json", "S-CG-M4-P1", "Scopus", "B", "search_result", "success", False, "Superseded poor-precision executable/co-simulation probe.", "USE_FILE"),
    ("I-CG-M4-C1-executable-integration-stream-b-count.json", "I-CG-M4-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor; superseded poor-precision probe.", "USE_FILE"),
    ("I-CG-M4-F1-executable-integration-stream-b-full.json", "I-CG-M4-F1", "IEEE Xplore", "B", "full_result", "success", False, "Superseded poor-precision executable/co-simulation probe.", "USE_FILE"),
    ("S-CG-E1-P1-eps-control-interface-stream-a.json", "S-CG-E1", "Scopus", "A", "search_result", "success", False, "EPS control/interface sensitivity duplicate.", "USE_FILE"),
    ("I-CG-E1-C1-eps-control-interface-stream-a-count.json", "I-CG-E1-C1", "IEEE Xplore", "A", "count_only", "success_zero", False, "Successful endpoint-reported zero; no full successor.", "USE_FILE"),
    ("S-CG-M3R1-P1-digital-thread-twin-structured-stream-b.json", "S-CG-M3R1", "Scopus", "B", "search_result", "success", True, "Final retained structured digital-twin Stream-B refinement.", "USE_FILE"),
    ("I-CG-M3R1-C1-digital-thread-twin-structured-stream-b-count.json", "I-CG-M3R1-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor; full result audit-only duplicate.", "USE_FILE"),
    ("I-CG-M3R1-F1-digital-thread-twin-structured-stream-b-full.json", "I-CG-M3R1", "IEEE Xplore", "B", "full_result", "success", False, "Audit-only primary duplicate.", "USE_FILE"),
    ("S-CG-M3A-R1-P1-eps-digital-thread-twin-stream-a.json", "S-CG-M3A-R1", "Scopus", "A", "search_result", "success_zero", False, "Successful Scopus zero; one blank placeholder is not bibliographic.", "USE_FILE"),
    ("I-CG-M3A-R1-C1-eps-digital-thread-twin-stream-a-count.json", "I-CG-M3A-R1-C1", "IEEE Xplore", "A", "count_only", "success_count_only", False, "Count-only predecessor; full result audit-only duplicate.", "USE_FILE"),
    ("I-CG-M3A-R1-F1-eps-digital-thread-twin-stream-a-full.json", "I-CG-M3A-R1", "IEEE Xplore", "A", "full_result", "success", False, "Audit-only duplicate represented by retained I-CG-M3.", "USE_FILE"),
    ("S-CG-M4R1-P1-executable-integration-structured-stream-b.json", "S-CG-M4R1", "Scopus", "B", "search_result", "success", True, "Final retained executable/model-integration precision-refinement input.", "USE_FILE"),
    ("I-CG-M4R1-C1-executable-integration-structured-stream-b-count.json", "I-CG-M4R1-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor; full result audit-only duplicate.", "USE_FILE"),
    ("I-CG-M4R1-F1-executable-integration-structured-stream-b-full.json", "I-CG-M4R1", "IEEE Xplore", "B", "full_result", "success", False, "Audit-only primary duplicate.", "USE_FILE"),
    ("S-CG-M5-P1-model-based-conceptual-design-stream-b.json", "S-CG-M5", "Scopus", "B", "search_result", "success", True, "Final retained exact conceptual-design Stream-B input.", "USE_FILE"),
    ("I-CG-M5-C1-model-based-conceptual-design-stream-b-count.json", "I-CG-M5-C1", "IEEE Xplore", "B", "count_only", "success_zero", False, "Successful endpoint-reported zero; no full successor.", "USE_FILE"),
    ("S-CG-M6-P1-integrated-concurrent-modeling-stream-b.json", "S-CG-M6-P1", "Scopus", "B", "search_result", "success", False, "Audit-only primary duplicate.", "USE_FILE"),
    ("I-CG-M6-C1-integrated-concurrent-modeling-stream-b-count.json", "I-CG-M6-C1", "IEEE Xplore", "B", "count_only", "success_count_only", False, "Count-only predecessor of retained I-CG-M6.", "USE_FILE"),
    ("I-CG-M6-F1-integrated-concurrent-modeling-stream-b-full.json", "I-CG-M6", "IEEE Xplore", "B", "full_result", "success", True, "Final retained exact integrated/concurrent-modeling Stream-B input.", "USE_FILE"),
]:
    add(f"searches/coverage-gap/{file_name}", query_id, source, stream, kind, status, retained, assessment, source_total_override=source_total_override)
add("searches/coverage-gap/final-input-summary.json", "coverage-gap-final-input-summary", "Coverage-gap audit", None, "generated_input_summary", "generated_audit_artifact", False, "Lists final retained coverage-gap source files; itself is not a candidate input.", role="generated_audit")
add("searches/coverage-gap/novelty-comparison.json", "coverage-gap-novelty-comparison", "Coverage-gap audit", None, "generated_comparison", "generated_audit_artifact", False, "Generated primary-novelty comparator; not a candidate input.", role="generated_audit")


def resolve_source_path(root: Path, path: str) -> Path:
    return root / path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    args = parser.parse_args()
    review = args.review_dir
    artifacts: list[dict[str, Any]] = []
    for row in ROWS:
        path = resolve_source_path(review, row["path"])
        if not path.is_file():
            raise RuntimeError(f"Manifest source artifact missing: {path}")
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        results = data.get("results", [])
        if not isinstance(results, list):
            results = []
        bibliographic_records = sum(isinstance(record, dict) and bool(str(record.get("title", "")).strip()) for record in results)
        raw_total = data.get("total")
        source_total = raw_total if row["source_total_override"] == "USE_FILE" else row["source_total_override"]
        output_metadata = data.get("output_metadata") or {}
        artifact = {
            "artifact_path": str(path),
            "query_id": row["query_id"],
            "source": row["source"],
            "worklog": WORKLOGS["Coverage-gap audit"] if row["path"].startswith("searches/coverage-gap/") else WORKLOGS.get(row["source"]),
            "stream": row["stream"],
            "artifact_kind": row["artifact_kind"],
            "role": row["role"],
            "status": row["status"],
            "retained_for_merge": row["retained_for_merge"],
            "exact_query": data.get("query"),
            "filters_or_request_metadata": output_metadata,
            "source_reported_total": source_total,
            "serialized_total_field": raw_total,
            "results_retrieved_field": data.get("results_retrieved", len(results)),
            "results_array_length": len(results),
            "bibliographic_records_in_file": bibliographic_records,
            "assessment": row["assessment"],
        }
        artifacts.append(artifact)

    final_inputs = [artifact for artifact in artifacts if artifact["retained_for_merge"]]
    final_raw = sum(artifact["bibliographic_records_in_file"] for artifact in final_inputs)
    if len(final_inputs) != 17 or final_raw != 352:
        raise RuntimeError(f"Expected 17 final merge inputs / 352 raw occurrences, got {len(final_inputs)} / {final_raw}")
    source_counts: dict[str, dict[str, int]] = {}
    for source in sorted({artifact["source"] for artifact in artifacts}):
        subset = [artifact for artifact in artifacts if artifact["source"] == source]
        source_counts[source] = {
            "artifacts": len(subset),
            "final_merge_inputs": sum(artifact["retained_for_merge"] for artifact in subset),
            "final_raw_bibliographic_occurrences": sum(artifact["bibliographic_records_in_file"] for artifact in subset if artifact["retained_for_merge"]),
            "service_failures": sum(artifact["status"].startswith("service_failure") for artifact in subset),
            "true_successful_zeros": sum(artifact["status"] == "success_zero" for artifact in subset),
            "count_only_artifacts": sum(artifact["artifact_kind"] == "count_only" for artifact in subset),
        }
    failures = [
        {key: artifact[key] for key in ["query_id", "source", "artifact_path", "status", "assessment"]}
        for artifact in artifacts if "failure" in artifact["status"]
    ]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = {
        "review_run_id": RUN_ID,
        "generated_at": now,
        "scope": "Inventory of all new-run raw search JSON/error/count artifacts from Scopus, IEEE Xplore, Semantic Scholar, Google Scholar, and the documented coverage-gap audit. It excludes shared integration outputs except references to their source files.",
        "worklogs": WORKLOGS,
        "summary": {
            "artifact_count": len(artifacts),
            "final_merge_input_count": len(final_inputs),
            "final_merge_raw_bibliographic_occurrences": final_raw,
            "source_counts": source_counts,
            "service_failure_count": len(failures),
            "source_failures": failures,
            "invariant": "A service failure has source_reported_total: null and is not a zero-hit search; count-only artifacts are not candidate records even where source totals are nonzero.",
        },
        "final_merge_inputs": [
            {key: artifact[key] for key in [
                "query_id", "source", "stream", "artifact_path", "status", "exact_query",
                "filters_or_request_metadata", "source_reported_total",
                "bibliographic_records_in_file", "assessment", "worklog",
            ]}
            for artifact in final_inputs
        ],
        "artifacts": artifacts,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    with args.output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps({"status": "success", "artifacts": len(artifacts), "final_inputs": len(final_inputs), "final_raw": final_raw, "service_failures": len(failures)}, indent=2))


if __name__ == "__main__":
    main()
