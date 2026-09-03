#!/usr/bin/env python3
"""Build the pre-screening prior-secondary-review candidate corpus.

This is the one project-level deduplication entry point. It accepts only the
four completed final PSR partitions from Scopus and Web of Science Core
Collection. It preserves every source and partition discovery occurrence while
using the shared DOI-first deduplication contract for candidate records.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SLR1_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SLR1_DIR.parents[1]
MERGER_DIR = (
    Path.home() / "agent-tools/academic-api-search/skills/academic-api-search/scripts"
)
MERGER_PATH = MERGER_DIR / "merge_search_results.py"
MERGER_COMPONENTS = {
    "merge_search_results.py": "7c395b4cfb1fbc2b2f713f2e7b04aa166a8a784dc20f0b430915edec0aa56d63",
    "_merge_contract.py": "676f899a6281bac6060582d625a939e8324cf88a0b82bae58399b1beb8d34b22",
    "_prisma_search_run.py": "a888e75294d368469ace3ff0041d904cc830b36b4bc30389ea9d5e67adc3205d",
}
CANDIDATE_SET_SCHEMA = "slr1-psr-candidate-set/v1"
PSR_NAMESPACE = "prior_secondary_reviews"
PARTITIONS = ("PSR1", "PSR2", "PSR3", "PSR4")
COMMON_CUTOFF = "2026-08-24"


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    artifact_dir: Path
    assessment_path: Path
    union_receipt_path: Path
    reconciled_run_receipt_path: Path | None = None

    @property
    def artifacts(self) -> tuple[Path, ...]:
        return tuple(self.artifact_dir / f"{partition}.json" for partition in PARTITIONS)


SOURCES = (
    SourceSpec(
        source_id="scopus",
        artifact_dir=SLR1_DIR / "source-specific/scopus/psr-searches",
        assessment_path=SLR1_DIR / "source-specific/scopus/psr-searches/assessment.json",
        union_receipt_path=(
            SLR1_DIR
            / "source-specific/scopus/psr-searches/source-union-receipt-prior_secondary_reviews.json"
        ),
    ),
    SourceSpec(
        source_id="web_of_science_core_collection",
        artifact_dir=(
            SLR1_DIR
            / "source-specific/web-of-science-core-collection/psr-searches"
        ),
        assessment_path=(
            SLR1_DIR
            / "source-specific/web-of-science-core-collection/psr-searches/assessment.json"
        ),
        union_receipt_path=(
            SLR1_DIR
            / "source-specific/web-of-science-core-collection/psr-searches/source-union-receipt-prior_secondary_reviews.json"
        ),
        reconciled_run_receipt_path=(
            SLR1_DIR
            / "source-specific/web-of-science-core-collection/psr-searches/run-receipt-reconciled.json"
        ),
    ),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def relative(path: Path) -> str:
    return str(path.relative_to(REPOSITORY_ROOT))


def require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def load_merger() -> Any:
    for name, expected in MERGER_COMPONENTS.items():
        path = MERGER_DIR / name
        require_regular(path)
        if digest(path) != expected:
            raise RuntimeError(f"The reviewed merge dependency changed: {name}")
    spec = importlib.util.spec_from_file_location("slr1_psr_merger", MERGER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the reviewed merge utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def input_declarations() -> list[dict[str, Any]]:
    declarations: list[dict[str, Any]] = []
    for source in SOURCES:
        for partition, path in zip(PARTITIONS, source.artifacts):
            require_regular(path)
            declarations.append(
                {
                    "source_id": source.source_id,
                    "partition_id": partition,
                    "artifact_path": relative(path),
                    "artifact_sha256": digest(path),
                    "artifact_bytes": path.stat().st_size,
                }
            )
    return declarations


def validate_assessment(source: SourceSpec) -> dict[str, Any]:
    require_regular(source.assessment_path)
    assessment = load_json(source.assessment_path)
    if (
        assessment.get("review_namespace") != PSR_NAMESPACE
        or assessment.get("status") != "passed"
        or assessment.get("final_search_partitions_complete") is not True
        or assessment.get("accepted_source_event_count") != 4
    ):
        raise ValueError(f"The final PSR assessment did not pass for {source.source_id}")
    if source.reconciled_run_receipt_path is not None:
        require_regular(source.reconciled_run_receipt_path)
        reconciled = load_json(source.reconciled_run_receipt_path)
        if (
            reconciled.get("success") is not True
            or reconciled.get("source_execution_replayed") is not False
            or reconciled.get("accepted_event_count") != 4
        ):
            raise ValueError("The reconciled Web of Science PSR receipt did not pass")
    return {
        "source_id": source.source_id,
        "assessment_path": relative(source.assessment_path),
        "assessment_sha256": digest(source.assessment_path),
        "assessment_status": assessment.get("status"),
        "final_search_partitions_complete": assessment.get(
            "final_search_partitions_complete"
        ),
        "reconciled_run_receipt_path": (
            relative(source.reconciled_run_receipt_path)
            if source.reconciled_run_receipt_path is not None
            else None
        ),
        "reconciled_run_receipt_sha256": (
            digest(source.reconciled_run_receipt_path)
            if source.reconciled_run_receipt_path is not None
            else None
        ),
    }


def validate_source_union(
    merger: Any, source: SourceSpec
) -> dict[str, Any]:
    require_regular(source.union_receipt_path)
    receipt = load_json(source.union_receipt_path)
    if receipt.get("review_namespace") != PSR_NAMESPACE:
        raise ValueError(f"The source-union namespace changed for {source.source_id}")
    # The shared merger validates terminal markers, artifact hashes, declared
    # partitions, source totals, and the DOI-first union before it returns.
    source_corpus = merger.merge_records(
        list(source.artifacts),
        source_union_receipt=source.union_receipt_path,
        source_union_namespace=PSR_NAMESPACE,
    )
    source_union = receipt.get("source_unions", {}).get(source.source_id, {})
    if (
        source_corpus.get("report_ready") is not True
        or source_corpus.get("source_union_receipt_present") is not True
        or source_corpus.get("source_totals", {}).get(source.source_id, {}).get(
            "source_union_status"
        )
        != "established"
        or source_union.get("expected_partitions") != list(PARTITIONS)
    ):
        raise ValueError(f"The source-union validation did not pass for {source.source_id}")
    return {
        "source_id": source.source_id,
        "receipt_path": relative(source.union_receipt_path),
        "receipt_sha256": digest(source.union_receipt_path),
        "raw_record_count": source_union.get("raw_record_count"),
        "unique_stable_record_id_count": len(
            source_union.get("stable_record_ids", [])
        ),
        "unique_identity_count": source_union.get("unique_union_count"),
        "source_corpus_dedup_summary": source_corpus.get("dedup_summary"),
        "status": "validated",
    }


def raw_manifestation_groups(
    merger: Any, declarations: list[dict[str, Any]]
) -> tuple[dict[str, list[dict[str, Any]]], int]:
    groups: dict[str, list[dict[str, Any]]] = {}
    raw_count = 0
    for declaration in declarations:
        path = REPOSITORY_ROOT / declaration["artifact_path"]
        if digest(path) != declaration["artifact_sha256"]:
            raise ValueError(f"An input changed before raw grouping: {path}")
        data = load_json(path)
        inferred_source = merger.infer_source(path, data)
        if inferred_source != declaration["source_id"]:
            raise ValueError(f"Source identity changed for {path}")
        rows = data.get("results")
        if not isinstance(rows, list):
            raise ValueError(f"A final PSR artifact has no results list: {path}")
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError(f"A final PSR row is malformed: {path}")
            record = {
                "paperId": merger.clean_text(row.get("paperId")),
                "doi": merger.normalize_doi(row.get("doi")),
                "title": merger.clean_text(row.get("title")),
                "year": row.get("year"),
            }
            key = merger.make_dedup_key(record, source=inferred_source)
            groups.setdefault(key, []).append(
                {
                    "source_id": inferred_source,
                    "partition_id": declaration["partition_id"],
                    "source_record_id": record["paperId"],
                    "doi": record["doi"],
                    "title": record["title"],
                    "normalized_title": merger.normalize_text(record["title"]),
                    "year": record["year"],
                    "source_artifact_sha256": declaration["artifact_sha256"],
                }
            )
            raw_count += 1
    return groups, raw_count


def duplicate_audit(groups: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    duplicate_groups = {
        key: rows for key, rows in groups.items() if len(rows) > 1
    }
    conflicts: list[dict[str, Any]] = []
    cross_source_groups: list[dict[str, Any]] = []
    for key, rows in sorted(duplicate_groups.items()):
        doi_values = sorted({row["doi"] for row in rows if row["doi"]})
        title_year_values = sorted(
            {(row["normalized_title"], row["year"]) for row in rows},
            key=lambda value: (value[0], str(value[1])),
        )
        manifestations = [
            {
                "source_id": row["source_id"],
                "partition_id": row["partition_id"],
                "source_record_id": row["source_record_id"],
                "doi": row["doi"],
                "title": row["title"],
                "year": row["year"],
                "source_artifact_sha256": row["source_artifact_sha256"],
            }
            for row in sorted(
                rows,
                key=lambda row: (
                    row["source_id"],
                    row["partition_id"],
                    row["source_record_id"],
                ),
            )
        ]
        if len(doi_values) > 1 or len(title_year_values) > 1:
            conflicts.append(
                {
                    "dedup_key": key,
                    "reason": (
                        "multiple_normalized_dois"
                        if len(doi_values) > 1
                        else "multiple_normalized_title_year_values"
                    ),
                    "manifestations": manifestations,
                }
            )
        if len({row["source_id"] for row in rows}) > 1:
            cross_source_groups.append(
                {
                    "dedup_key": key,
                    "occurrence_count": len(rows),
                    "manifestations": manifestations,
                }
            )
    return {
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_occurrence_count": sum(
            len(rows) - 1 for rows in duplicate_groups.values()
        ),
        "cross_source_duplicate_group_count": len(cross_source_groups),
        "cross_source_duplicate_groups": cross_source_groups,
        "manual_identifier_conflicts": conflicts,
        "manual_identifier_conflict_count": len(conflicts),
        "status": "no_identifier_conflicts_detected" if not conflicts else "manual_review_required",
    }


def candidate_records(corpus: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw_results = corpus.get("results")
    if not isinstance(raw_results, list):
        raise ValueError("The shared merger did not return a results list")
    candidates: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_results, start=1):
        if not isinstance(raw, Mapping):
            raise ValueError("The shared merger returned a malformed candidate")
        candidate = copy.deepcopy(dict(raw))
        candidate["candidate_id"] = f"psr-candidate-{index:04d}"
        candidate["screening_status"] = "not_screened"
        candidate["cutoff_date_screening_status"] = (
            "pending_exact_cutoff_check"
            if candidate.get("year") == 2026
            else "not_required_by_source_year"
        )
        candidates.append(candidate)
    return candidates


def build(output_path: Path) -> dict[str, Any]:
    merger = load_merger()
    declarations = input_declarations()
    assessment_receipts = [validate_assessment(source) for source in SOURCES]
    source_union_receipts = [
        validate_source_union(merger, source) for source in SOURCES
    ]
    input_paths = [REPOSITORY_ROOT / item["artifact_path"] for item in declarations]
    corpus = merger.merge_records(input_paths)
    if (
        corpus.get("report_ready") is not True
        or corpus.get("discovery_event_count") != len(declarations)
        or corpus.get("partition_event_count") != len(declarations)
        or corpus.get("source_union_receipt_present") is not False
    ):
        raise ValueError("The cross-source candidate merge did not complete safely")

    groups, raw_count = raw_manifestation_groups(merger, declarations)
    candidates = candidate_records(corpus)
    if raw_count != corpus.get("dedup_summary", {}).get("raw_results"):
        raise ValueError("Raw manifestation accounting disagrees with the shared merger")
    if len(groups) != len(candidates):
        raise ValueError("Deduplication keys disagree with the shared merger")

    duplicate_review = duplicate_audit(groups)
    if (
        duplicate_review["duplicate_occurrence_count"]
        != corpus.get("dedup_summary", {}).get("duplicates_removed")
    ):
        raise ValueError("Duplicate occurrence accounting disagrees with the shared merger")
    for declaration in declarations:
        path = REPOSITORY_ROOT / declaration["artifact_path"]
        if digest(path) != declaration["artifact_sha256"]:
            raise ValueError(f"An input changed during the merge: {path}")

    result = copy.deepcopy(corpus)
    result["results"] = candidates
    result["candidate_set"] = {
        "schema_version": CANDIDATE_SET_SCHEMA,
        "review_namespace": PSR_NAMESPACE,
        "purpose": "pre_screening_prior_secondary_review_candidates",
        "screening_status": "not_started",
        "common_evidence_cutoff": COMMON_CUTOFF,
        "source_year_precision": True,
        "cutoff_year_candidate_count_requiring_exact_date_screening": sum(
            candidate.get("year") == 2026 for candidate in candidates
        ),
        "source_assessments": assessment_receipts,
        "per_source_union_receipts": source_union_receipts,
        "cross_source_union_receipt": {
            "status": "not_created",
            "reason": (
                "The two final sources retain distinct source-native strategy "
                "references. The shared source-union contract requires one shared "
                "review and strategy linkage. Each source-union receipt was instead "
                "validated before the cross-source DOI-first candidate merge."
            ),
        },
        "deduplication_conflict_review": duplicate_review,
        "merge_tool": {
            "name": "merge_search_results.py",
            "version": merger.MERGE_TOOL_VERSION,
            "deduplication_algorithm": merger.DEDUPLICATION_ALGORITHM,
            "deduplication_algorithm_version": merger.DEDUPLICATION_ALGORITHM_VERSION,
            "component_sha256": dict(MERGER_COMPONENTS),
        },
        "input_declarations": declarations,
        "output_path": relative(output_path),
    }
    return result


def write_create_only(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {path}")
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        raise


def check(path: Path) -> None:
    require_regular(path)
    persisted = load_json(path)
    expected = build(path)
    persisted_comparable = copy.deepcopy(persisted)
    expected_comparable = copy.deepcopy(expected)
    # The shared merger deliberately timestamps each new corpus. Every other
    # field must be reproduced from the marker-bound final source artifacts.
    persisted_comparable.pop("generated_at", None)
    expected_comparable.pop("generated_at", None)
    if persisted_comparable != expected_comparable:
        raise ValueError("Candidate corpus is not reproducible")
    if persisted.get("candidate_set", {}).get("screening_status") != "not_started":
        raise ValueError("Candidate corpus has an unexpected screening status")
    if persisted.get("report_ready") is not True:
        raise ValueError("Candidate corpus is not report-ready as a search merge")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=SLR1_DIR / "psr-candidates.json",
        help="create-only PSR candidate corpus path",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve(strict=False)
    try:
        output.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise SystemExit("The candidate corpus must be inside this repository") from error
    if args.check:
        check(output)
        print(json.dumps({"status": "ok", "output": relative(output)}))
        return 0
    payload = build(output)
    write_create_only(output, payload)
    print(
        json.dumps(
            {
                "status": "saved",
                "output": relative(output),
                "raw_records": payload["dedup_summary"]["raw_results"],
                "unique_candidates": payload["dedup_summary"]["unique_results"],
                "duplicates_removed": payload["dedup_summary"]["duplicates_removed"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
