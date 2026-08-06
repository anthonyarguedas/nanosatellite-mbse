#!/usr/bin/env python3
"""Validate count, provenance, deduplication, and screening invariants for the corpus stage."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "eps-mbse-slr-2026"
REPORT_ID_RE = re.compile(r"^eps-mbse-slr-2026-r\d{4}$")
NON_ALNUM = re.compile(r"[^a-z0-9]+")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return NON_ALNUM.sub(" ", text.lower().replace("&", " and ")).strip()


def timestamp_free_content_sha256(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.pop("generated_at", None)
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    review = args.review_dir
    errors: list[str] = []
    checks: list[str] = []

    # Parse every new-run JSON artifact, but deliberately exclude retained
    # source-cache directories. Cache metadata is not needed to establish the
    # independent candidate freeze and must not be traversed as a precondition.
    json_paths = sorted(
        path for path in review.rglob("*.json")
        if not ({"markdown", "pdfs"} & set(path.relative_to(review).parts))
    )
    parse_errors: list[dict[str, str]] = []
    for path in json_paths:
        try:
            with path.open(encoding="utf-8") as fh:
                json.load(fh)
        except Exception as exc:  # noqa: BLE001 - report parse diagnostics
            parse_errors.append({"path": str(path), "error": str(exc)})
    check(not parse_errors, f"JSON parse failures: {parse_errors}", errors)
    checks.append(f"Parsed {len(json_paths)} JSON files.")

    paths = {
        "manifest": review / "searches/search-manifest.json",
        "merged": review / "searches/merged_candidates.json",
        "dedup": review / "searches/deduplication-report.json",
        "freeze": review / "searches/independent-candidate-freeze.json",
        "decisions": review / "searches/integration/screening-decisions.json",
        "corpus": review / "corpus.json",
        "secondary": review / "searches/secondary-studies.json",
        "recall": review / "searches/retained-file-recall-audit.json",
        "search_log": review / "search-log.md",
        "screening_log": review / "screening.md",
        "legacy_register": review / "legacy-known-item-register.md",
    }
    for name, path in paths.items():
        check(path.is_file(), f"Missing final artifact {name}: {path}", errors)
        if path.suffix == ".md" and path.is_file():
            # Explicitly read each final Markdown artifact after generation.
            check(bool(path.read_text(encoding="utf-8").strip()), f"Empty final Markdown artifact: {path}", errors)
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    merged = json.loads(paths["merged"].read_text(encoding="utf-8"))
    dedup = json.loads(paths["dedup"].read_text(encoding="utf-8"))
    freeze = json.loads(paths["freeze"].read_text(encoding="utf-8"))
    decisions_payload = json.loads(paths["decisions"].read_text(encoding="utf-8"))
    corpus = json.loads(paths["corpus"].read_text(encoding="utf-8"))
    secondary = json.loads(paths["secondary"].read_text(encoding="utf-8"))
    recall = json.loads(paths["recall"].read_text(encoding="utf-8"))

    check(manifest.get("review_run_id") == RUN_ID, "Manifest run ID mismatch", errors)
    check(merged.get("review_run_id") == RUN_ID, "Merged run ID mismatch", errors)
    check(corpus.get("review_run_id") == RUN_ID, "Corpus run ID mismatch", errors)
    check(len(manifest.get("artifacts", [])) == 86, "Manifest must inventory 86 search JSON artifacts", errors)
    final_inputs = manifest.get("final_merge_inputs", [])
    check(len(final_inputs) == 17, "Manifest must have 17 final merge inputs", errors)
    final_raw = sum(item.get("bibliographic_records_in_file", 0) for item in final_inputs)
    check(final_raw == 352, f"Manifest final raw occurrences {final_raw}, expected 352", errors)
    check(manifest["summary"].get("service_failure_count") == 15, "Manifest must record 15 supplementary service failures", errors)
    for artifact in manifest.get("artifacts", []):
        path = Path(artifact["artifact_path"])
        check(path.is_file(), f"Manifest artifact path missing: {path}", errors)
        if artifact["status"].startswith("service_failure"):
            check(artifact.get("source_reported_total") is None, f"Service failure treated as source total in {artifact['query_id']}", errors)
            check(not artifact["retained_for_merge"], f"Service failure marked retained: {artifact['query_id']}", errors)
    checks.append("Manifest inventories 17 retained inputs / 352 raw occurrences and keeps 15 source failures distinct from zeros.")

    candidates = merged.get("results", [])
    check(len(candidates) == 174, f"Merged candidate count {len(candidates)}, expected 174", errors)
    check(merged["dedup_summary"].get("raw_bibliographic_occurrences") == 352, "Merged raw count mismatch", errors)
    check(merged["dedup_summary"].get("duplicates_removed") == 178, "Merged duplicate count mismatch", errors)
    candidate_ids = [candidate.get("report_id") for candidate in candidates]
    check(len(candidate_ids) == len(set(candidate_ids)), "Duplicate report_id in merged candidates", errors)
    check(all(REPORT_ID_RE.match(report_id or "") for report_id in candidate_ids), "Merged report IDs are not all new-run IDs", errors)
    check(all(candidate.get("candidate_id") == candidate.get("report_id") == candidate.get("corpus_id") for candidate in candidates), "Merged stable IDs are inconsistent", errors)
    raw_provenance_count = sum(len(candidate.get("provenance", [])) for candidate in candidates)
    check(raw_provenance_count == 352, f"Provenance events {raw_provenance_count}, expected 352", errors)
    provenance_sources = Counter(event.get("source") for candidate in candidates for event in candidate.get("provenance", []))
    check(provenance_sources == Counter({"Scopus": 242, "IEEE Xplore": 110}), f"Provenance source counts wrong: {provenance_sources}", errors)
    provenance_streams = Counter(event.get("stream") for candidate in candidates for event in candidate.get("provenance", []))
    check(provenance_streams == Counter({"A": 23, "B": 329}), f"Provenance stream counts wrong: {provenance_streams}", errors)
    allowed_paths = {item["artifact_path"] for item in final_inputs}
    allowed_query_ids = {item["query_id"] for item in final_inputs}
    for candidate in candidates:
        for event in candidate.get("provenance", []):
            for key in ["source", "query_id", "exact_query", "input_file", "isolated_merge_input_file", "stream", "search_phase", "source_rank", "source_record"]:
                check(key in event, f"Missing provenance field {key} for {candidate['report_id']}", errors)
            check(event.get("input_file") in allowed_paths, f"Non-final input in provenance: {event.get('input_file')}", errors)
            check(event.get("query_id") in allowed_query_ids, f"Non-final query ID in provenance: {event.get('query_id')}", errors)
            check(Path(event.get("input_file", "")).is_file(), f"Missing provenance raw file: {event.get('input_file')}", errors)
            check(Path(event.get("isolated_merge_input_file", "")).is_file(), f"Missing isolated input copy: {event.get('isolated_merge_input_file')}", errors)
            check("/markdown/" not in event.get("input_file", "") and "/pdfs/" not in event.get("input_file", ""), f"Cache path leaked into candidate provenance: {event.get('input_file')}", errors)
    check(all("paper-" not in (candidate.get("report_id") or "") and "paper-" not in (candidate.get("corpus_id") or "") for candidate in candidates), "Legacy paper ID reused in candidate ID", errors)
    checks.append("Merged set has 174 new-run-ID candidates and 352 complete provenance events from retained final source files only.")

    current_hash = sha256(paths["merged"])
    check(freeze["candidate_set"].get("sha256") == current_hash, "Independent freeze hash does not match merged candidate set", errors)
    check(dedup.get("candidate_set_sha256") == current_hash, "Dedup report hash does not match merged candidate set", errors)
    content_hash = timestamp_free_content_sha256(paths["merged"])
    check(freeze["candidate_set"].get("timestamp_free_content_sha256") == content_hash, "Freeze deterministic content hash does not match merged candidate set", errors)
    check(dedup.get("candidate_set_timestamp_free_content_sha256") == content_hash, "Dedup deterministic content hash does not match merged candidate set", errors)
    check(freeze["candidate_set"].get("unique_candidates") == 174, "Freeze candidate count mismatch", errors)
    check(freeze["integrity_assertions"].get("retained_markdown_or_pdf_cache_read_before_freeze") is False, "Freeze anti-anchoring assertion failed", errors)
    check(dedup["stage_counts"] == {
        "raw_occurrences": 352,
        "after_normalized_doi": 206,
        "after_same_source_paper_id": 174,
        "after_manually_confirmed_title_year": 174,
        "after_bibliographically_safe_title_only": 174,
        "final_unique_candidates": 174,
        "duplicates_removed": 178,
        "merges_by_stage": {
            "normalized_doi": 146,
            "same_source_paper_id": 32,
            "manually_confirmed_title_year": 0,
            "bibliographically_safe_title_only": 0,
        },
    }, "Dedup stage counts mismatch", errors)
    checks.append("Freeze full-file SHA-256, timestamp-free content SHA-256, and deterministic DOI/source-ID deduplication stage counts reconcile.")

    decisions = decisions_payload.get("decisions", [])
    decision_ids = [decision.get("report_id") for decision in decisions]
    check(len(decisions) == 174, f"Decision count {len(decisions)}, expected 174", errors)
    check(len(decision_ids) == len(set(decision_ids)), "A merged candidate has more than one screening decision", errors)
    check(set(decision_ids) == set(candidate_ids), "Merged candidate/decision ID sets do not match", errors)
    decision_counts = Counter(decision.get("screening_tier") for decision in decisions)
    check(decision_counts == Counter({"core": 6, "supporting": 86, "rejected": 82}), f"Screen tiers wrong: {decision_counts}", errors)
    check(all(isinstance(decision.get("screening_visibility"), dict) for decision in decisions), "Screening visibility audit missing from one or more decisions", errors)
    check(all(not decision.get("is_secondary_study") or decision.get("screening_tier") == "rejected" for decision in decisions), "Secondary record not rejected from primary corpus", errors)
    check(sum(bool(decision.get("is_secondary_study")) for decision in decisions) == 5, "Secondary study count must be 5", errors)

    corpus_records = corpus.get("results", [])
    keep_ids = {decision["report_id"] for decision in decisions if decision["screening_tier"] in {"core", "supporting"}}
    corpus_ids = [record.get("report_id") for record in corpus_records]
    check(len(corpus_records) == 92, f"Corpus count {len(corpus_records)}, expected 92", errors)
    check(len(corpus_ids) == len(set(corpus_ids)), "Duplicate report ID in corpus", errors)
    check(set(corpus_ids) == keep_ids, "Corpus IDs do not equal core+supporting decision IDs", errors)
    candidate_by_id = {candidate["report_id"]: candidate for candidate in candidates}
    doi_seen: dict[str, str] = {}
    title_year_seen: dict[tuple[str, Any], str] = {}
    for record in corpus_records:
        for key in ["corpus_id", "report_id", "title", "doi", "normalized_doi", "authors", "year", "abstract", "citationCount", "openAccess_pdf_url", "paperId", "provenance", "discovery_streams", "discovery_query_ids", "screening_tier", "rationale", "confidence", "screening_visibility", "retrieval_metadata_completeness", "status"]:
            check(key in record, f"Corpus record {record.get('report_id')} missing required field {key}", errors)
        check(record.get("status") == "pending_full_text_eligibility", f"Corpus status is not pending: {record.get('report_id')}", errors)
        check(record.get("route_assignment") is None, f"Route assigned at title/abstract stage: {record.get('report_id')}", errors)
        check(record.get("doi") == record.get("normalized_doi"), f"DOI not normalized alias in corpus: {record.get('report_id')}", errors)
        check(record.get("report_id") in candidate_by_id, f"Corpus report not merged: {record.get('report_id')}", errors)
        check(record.get("dedup_key") == candidate_by_id[record["report_id"]].get("dedup_key"), f"Corpus/merged mapping mismatch: {record.get('report_id')}", errors)
        doi = record.get("normalized_doi")
        if doi:
            check(doi not in doi_seen, f"Duplicate DOI in corpus: {doi} ({doi_seen.get(doi)} / {record['report_id']})", errors)
            doi_seen[doi] = record["report_id"]
        title_year = (normalize_title(record.get("title")), record.get("year"))
        check(title_year not in title_year_seen, f"Duplicate normalized title-year in corpus: {title_year}", errors)
        title_year_seen[title_year] = record["report_id"]
        check(bool(record.get("abstract")) or bool(record.get("abstract_missing")), f"Empty abstract missing missingness flag: {record.get('report_id')}", errors)
        retrieval_status = (record.get("retrieval_metadata_completeness") or {}).get("status")
        check(retrieval_status in {"direct_identifier_available", "source_id_or_title_lookup_required", "title_year_lookup_required"}, f"Invalid retrieval metadata status: {record.get('report_id')}", errors)
        check("/markdown/" not in json.dumps(record.get("provenance", [])) and "/pdfs/" not in json.dumps(record.get("provenance", [])), f"Cache provenance leaked into corpus: {record.get('report_id')}", errors)
    secondary_ids = {record.get("report_id") for record in secondary.get("results", [])}
    rejected_ids = {decision["report_id"] for decision in decisions if decision["screening_tier"] == "rejected"}
    check(len(secondary_ids) == 5 and secondary_ids <= rejected_ids and not (secondary_ids & set(corpus_ids)), "Secondary-study separation mismatch", errors)
    checks.append("Every merged candidate has exactly one screen decision; 92 core/supporting records map one-to-one into corpus with no DOI/title-year duplicate.")

    screening_text = paths["screening_log"].read_text(encoding="utf-8")
    check(all(screening_text.count(report_id) == 1 for report_id in candidate_ids), "screening.md does not list every report ID exactly once", errors)
    search_log = paths["search_log"].read_text(encoding="utf-8")
    check("citation chasing" in search_log.lower() and "explicitly deferred" in search_log.lower(), "Search log does not state citation chasing is deferred", errors)
    check("service_failure_http_403" in search_log and "service_failure_before_rank_1" in search_log, "Search log does not distinguish source failures", errors)
    check(recall["anti_anchoring"]["independent_candidate_set_sha256"] == current_hash, "Recall audit is not tied to frozen candidate set", errors)
    check(recall["summary"]["unique_independently_rediscovered_reports_matched"] == 35, "Recall audit matched-report count mismatch", errors)
    checks.append("Final Markdown artifacts were read; screening log coverage and cache-audit freeze linkage reconcile.")

    report = {
        "review_run_id": RUN_ID,
        "validated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "passed" if not errors else "failed",
        "json_files_parsed": len(json_paths),
        "parse_errors": parse_errors,
        "checks_completed": checks,
        "errors": errors,
        "reconciled_counts": {
            "manifest_final_raw": final_raw,
            "merged_raw_provenance": raw_provenance_count,
            "merged_unique": len(candidates),
            "duplicates_removed": 352 - len(candidates),
            "core": decision_counts["core"],
            "supporting": decision_counts["supporting"],
            "rejected": decision_counts["rejected"],
            "secondary": len(secondary_ids),
            "corpus": len(corpus_records),
            "cache_matched_unique_reports": recall["summary"]["unique_independently_rediscovered_reports_matched"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "json_files_parsed": len(json_paths), "errors": errors, "counts": report["reconciled_counts"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
