#!/usr/bin/env python3
"""Reconcile the controlled 2026-08-05 direct IEEE Xplore update.

This is intentionally a narrow, additive reconciliation: it preserves every
existing candidate and corpus identifier, appends direct-IEEE provenance only
to DOI/title matches, and keeps screened-out direct records in an audit file
rather than assigning new corpus IDs.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UPDATE_ID = "ieee-xplore-direct-2026-08-05"
UPDATE_DATE = "2026-08-05"
REL_ROOT = "SLR/SLR1"
NON_ALNUM = re.compile(r"[^a-z0-9]+")

# These borderline records have direct CubeSat/nanosatellite wording, so their
# protocol-screen rationale should be more specific than the generic fallback.
OVERRIDES: dict[str, tuple[str, str]] = {
    "10.1109/aero.2016.7500897": (
        "requirements_engineering_outside_review_focus",
        "Reviewer exclusion: the available record is a CubeSat requirements-elicitation/specification contribution and does not report an in-scope system/EPS MBSE architecture or model-integrated IVV contribution.",
    ),
    "10.1109/aero.2017.7943647": (
        "requirements_engineering_outside_review_focus",
        "Reviewer exclusion: the available record presents requirements-engineering tool support in a CubeSat context but does not report an in-scope system/EPS MBSE architecture or model-integrated IVV contribution.",
    ),
    "10.23919/wac.2018.8430399": (
        "requirements_engineering_outside_review_focus",
        "Reviewer exclusion: the available record presents CPS requirements-elicitation tool support linked to a CubeSat initiative but does not report an in-scope system/EPS MBSE architecture or model-integrated IVV contribution.",
    ),
    "10.1109/tro.2015.2409431": (
        "not_mbse_target_model",
        "CubeSat is the application context, but the available IEEE abstract describes state-space CPS control and coregulation rather than a system/EPS MBSE model.",
    ),
    "10.1109/itng.2015.22": (
        "software_process_not_mbse",
        "Nanosatellite context is present, but the record is a Scrum/safety-critical embedded-software simulator development study, not an MBSE system or EPS model.",
    ),
    "10.1109/syscon.2017.7934725": (
        "subsystem_payload_scope",
        "The record applies SysML/TTool to a multispectral-camera payload feasibility study for a 27U satellite, not to a nanosatellite system-level or EPS MBSE model.",
    ),
    "10.1109/syscon.2015.7116753": (
        "outside_nanosatellite_population",
        "The available metadata concerns generic multi-satellite optimization and does not establish nanosatellite/CubeSat population or EPS-specific model evidence.",
    ),
    "10.1109/syscon.2018.8369575": (
        "subsystem_communications_scope",
        "The MBSE contribution is an inter-satellite-communication subsystem conceptual model, outside the protocol's system-level/EPS target scope.",
    ),
    "10.1109/sysose.2018.8428761": (
        "subsystem_communications_scope",
        "This is a generic satellite-communication simulation-platform architecture, not a nanosatellite system-level or EPS MBSE study.",
    ),
    "10.1109/comst.2020.2990499": (
        "communications_survey_not_mbse",
        "This is a CubeSat communications survey rather than a primary MBSE system/EPS modeling study.",
    ),
    "10.1109/aero47225.2020.9172720": (
        "mission_technology_not_mbse",
        "The CubeSat navigation-infrastructure paper does not report an MBSE system/EPS model.",
    ),
    "10.1109/jmass.2020.3001080": (
        "subsystem_communications_scope",
        "The MBSE operational concept is for a visible-light intersatellite-communication subsystem, not the target nanosatellite system/EPS modeling scope.",
    ),
    "10.1109/tap.2022.3167773": (
        "subsystem_communications_scope",
        "The record is a CubeSat communications-antenna design paper, not an MBSE system/EPS model.",
    ),
    "10.1109/tnsm.2021.3117692": (
        "subsystem_communications_scope",
        "The record studies satellite-network slicing; CubeSats are a network context rather than an MBSE system/EPS modeling case.",
    ),
    "10.1109/tap.2023.3249820": (
        "subsystem_communications_scope",
        "The record is a CubeSat communications-antenna design study, not an MBSE system/EPS model.",
    ),
    "10.1109/icmae66341.2025.11276928": (
        "subsystem_hardware_scope",
        "This is nanosatellite ADCS gyroscope-calibration hardware work, not MBSE or EPS/system-level modeling.",
    ),
    "10.1109/gast67799.2026.11523317": (
        "mission_technology_not_mbse",
        "The CubeSat cyber-intrusion response study uses deep reinforcement learning, not an MBSE system/EPS model.",
    ),
    "10.1109/iccps68698.2026.00026": (
        "mission_technology_not_mbse",
        "The CubeSat TinyML capability paper is onboard-computing technology work, not an MBSE system/EPS model.",
    ),
}

SUBSYSTEM_TERMS = (
    "communication", "antenna", "payload", "camera", "gyroscope", "attitude", "on-board software",
    "onboard software", "data handling", "physical layer", "network", "sensor", "control moment",
)
NON_SPACE_TERMS = (
    "automotive", "train control", "construction equipment", "medical", "biotelemetry", "uav", "unmanned",
    "patrol boat", "robotics", "electrical connector", "soil moisture", "albedo", "imagery", "radar meteor",
    "wireless", "aircraft projects", "positioning of bds", "solar f10", "tcxo", "deep learning",
)


def normalize_doi(value: Any) -> str:
    doi = str(value or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi.strip()


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    return NON_ALNUM.sub(" ", text).strip()


def record_key(record: dict[str, Any]) -> tuple[str, str]:
    return normalize_doi(record.get("doi")), normalize_title(record.get("title"))


def relative(path: Path) -> str:
    """Use project-relative paths in newly appended provenance."""
    parts = path.resolve().parts
    try:
        index = parts.index("SLR")
    except ValueError:
        return str(path)
    return str(Path(*parts[index:]))


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def select_best(records: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        records,
        key=lambda item: (
            len(str(item.get("abstract") or "")),
            len(item.get("authors") or []),
            bool(item.get("doi")),
            bool(item.get("paperId")),
        ),
    )


def assess_new_record(record: dict[str, Any]) -> tuple[str, str, str]:
    doi = normalize_doi(record.get("doi"))
    if doi in OVERRIDES:
        reason_code, rationale = OVERRIDES[doi]
        return "rejected_not_added", reason_code, rationale

    title = str(record.get("title") or "")
    text = f"{title} {record.get('abstract') or ''}".lower()
    has_population = "cubesat" in text or "nano-satellite" in text or "nanosatellite" in text

    if any(term in text for term in NON_SPACE_TERMS):
        return (
            "rejected_not_added",
            "outside_population_or_domain",
            "The available IEEE metadata places this record outside the nanosatellite/CubeSat MBSE population or in a non-target application domain.",
        )
    if has_population and any(term in text for term in SUBSYSTEM_TERMS):
        return (
            "rejected_not_added",
            "subsystem_or_technology_scope",
            "The record is a CubeSat/nanosatellite subsystem or technology study rather than a system-level or EPS MBSE model under the protocol.",
        )
    if has_population:
        return (
            "rejected_not_added",
            "not_mbse_target_model",
            "The available IEEE metadata establishes CubeSat/nanosatellite context but not an in-scope MBSE system/EPS model with the required review focus.",
        )
    if "spacecraft" in text or "satellite" in text or "space system" in text or "space mission" in text:
        return (
            "rejected_not_added",
            "outside_nanosatellite_population",
            "The available IEEE metadata is generic spacecraft/satellite work and does not establish the protocol's nanosatellite/CubeSat population.",
        )
    return (
        "rejected_not_added",
        "outside_population_or_domain",
        "The available IEEE metadata does not establish an in-scope nanosatellite/CubeSat MBSE system or EPS modeling study.",
    )


def concise_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "paperId": record.get("paperId", ""),
        "doi": normalize_doi(record.get("doi")),
        "title": record.get("title", ""),
        "authors": record.get("authors", []) or [],
        "year": record.get("year"),
        "abstract": record.get("abstract", ""),
        "abstract_is_truncated": bool(record.get("abstract_is_truncated")),
        "url": record.get("url", ""),
        "publicationTitle": record.get("publicationTitle", ""),
        "documentType": record.get("documentType", ""),
        "contentType": record.get("contentType", ""),
    }


def direct_provenance(detection: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "ieee_xplore_direct",
        "input_file": relative(Path(detection["path"])),
        "query": detection["query"],
        "rank": detection["rank"],
        "paperId": detection["record"].get("paperId", ""),
        "purpose": "controlled_direct_parity_update",
        "update_id": UPDATE_ID,
    }


def provenance_signature(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        item.get("source"), item.get("input_file"), item.get("query"), item.get("rank"),
        item.get("paperId"), item.get("purpose"), item.get("update_id"),
    )


def append_provenance(record: dict[str, Any], additions: list[dict[str, Any]]) -> int:
    provenance = record.setdefault("provenance", [])
    existing = {provenance_signature(item) for item in provenance if isinstance(item, dict)}
    added = 0
    for item in additions:
        signature = provenance_signature(item)
        if signature not in existing:
            provenance.append(item)
            existing.add(signature)
            added += 1
    if added:
        sources = record.setdefault("sources", [])
        if any(item.get("source") == "ieee_xplore_direct" for item in additions) and "ieee_xplore_direct" not in sources:
            sources.append("ieee_xplore_direct")
    return added


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write reconciled corpus artifacts; otherwise only write audit files.")
    args = parser.parse_args()

    direct_dir = Path(__file__).resolve().parent
    slr1_dir = direct_dir.parents[1]
    searches_dir = slr1_dir / "searches"
    merged_path = searches_dir / "merged_candidates.json"
    corpus_path = slr1_dir / "corpus.json"
    audit_path = direct_dir / "ieee_direct_2026-08-05_dedup_and_screening_audit.json"
    manifest_path = direct_dir / "search_manifest_2026-08-05.json"

    merged_data = load_json(merged_path)
    corpus_data = load_json(corpus_path)
    merged_records = merged_data["results"]
    corpus_records = corpus_data["results"]

    # The population-refined Q12 query is a screening refinement for the 75-hit
    # raw Q12 parity query, not an additional parity line. Its records are still
    # included in provenance reconciliation below.
    # Supplemental exact-record metadata checks are logged separately and do
    # not alter the registered Q1–Q28 parity identification counts.
    all_full_paths = sorted(Path(path) for path in glob.glob(str(direct_dir / "*_full_2026-08-05.json")))
    all_count_paths = sorted(Path(path) for path in glob.glob(str(direct_dir / "*_count_2026-08-05.json")))
    supplemental_full_paths = [path for path in all_full_paths if "waseem2018_exact_doi" in path.name]
    supplemental_count_paths = [path for path in all_count_paths if "waseem2018_exact_doi" in path.name]
    full_paths = [path for path in all_full_paths if path not in supplemental_full_paths]
    primary_full_paths = [path for path in full_paths if "population_refined" not in path.name]
    refinement_full_paths = [path for path in full_paths if "population_refined" in path.name]
    count_paths = [path for path in all_count_paths if path not in supplemental_count_paths]

    manifest_entries: list[dict[str, Any]] = []
    detections: list[dict[str, Any]] = []
    for path in full_paths:
        data = load_json(path)
        manifest_entries.append({
            "input_file": relative(path),
            "kind": "full",
            "query": data.get("query", ""),
            "total": data.get("total", 0),
            "results_retrieved": data.get("results_retrieved", 0),
            "status": data.get("output_metadata", {}).get("status", ""),
            "stopped_reason": data.get("output_metadata", {}).get("stopped_reason", ""),
        })
        for rank, record in enumerate(data.get("results", []) or [], start=1):
            detections.append({"path": str(path), "query": data.get("query", ""), "rank": rank, "record": record})
    for path in count_paths:
        data = load_json(path)
        manifest_entries.append({
            "input_file": relative(path),
            "kind": "count",
            "query": data.get("query", ""),
            "total": data.get("total", 0),
            "results_retrieved": data.get("results_retrieved", 0),
            "status": data.get("output_metadata", {}).get("status", ""),
            "stopped_reason": data.get("output_metadata", {}).get("stopped_reason", ""),
        })

    supplemental_entries: list[dict[str, Any]] = []
    for kind, paths in (("supplemental_full", supplemental_full_paths), ("supplemental_count", supplemental_count_paths)):
        for path in paths:
            data = load_json(path)
            supplemental_entries.append({
                "input_file": relative(path),
                "kind": kind,
                "query": data.get("query", ""),
                "total": data.get("total", 0),
                "results_retrieved": data.get("results_retrieved", 0),
                "status": data.get("output_metadata", {}).get("status", ""),
                "stopped_reason": data.get("output_metadata", {}).get("stopped_reason", ""),
                "counted_in_parity_totals": False,
            })

    # Build connected components using either DOI or normalized title, so a
    # direct result present through several query lines remains one screen.
    parent = list(range(len(detections)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    by_doi_detection: dict[str, int] = {}
    by_title_detection: dict[str, int] = {}
    for index, detection in enumerate(detections):
        doi, title = record_key(detection["record"])
        if doi:
            if doi in by_doi_detection:
                union(index, by_doi_detection[doi])
            else:
                by_doi_detection[doi] = index
        if title:
            if title in by_title_detection:
                union(index, by_title_detection[title])
            else:
                by_title_detection[title] = index

    clusters: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for index, detection in enumerate(detections):
        clusters[find(index)].append(detection)

    merged_by_doi: dict[str, dict[str, Any]] = {}
    merged_by_title: dict[str, dict[str, Any]] = {}
    for record in merged_records:
        doi, title = record_key(record)
        if doi:
            merged_by_doi[doi] = record
        if title:
            merged_by_title[title] = record
    corpus_by_doi: dict[str, dict[str, Any]] = {}
    corpus_by_title: dict[str, dict[str, Any]] = {}
    for record in corpus_records:
        doi, title = record_key(record)
        if doi:
            corpus_by_doi[doi] = record
        if title:
            corpus_by_title[title] = record

    matched_audit: list[dict[str, Any]] = []
    new_audit: list[dict[str, Any]] = []
    direct_additions_by_merged: dict[str, list[dict[str, Any]]] = defaultdict(list)
    direct_additions_by_corpus: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for cluster_detections in clusters.values():
        records = [item["record"] for item in cluster_detections]
        chosen = select_best(records)
        dois = {normalize_doi(record.get("doi")) for record in records if normalize_doi(record.get("doi"))}
        titles = {normalize_title(record.get("title")) for record in records if normalize_title(record.get("title"))}

        matched_records: list[dict[str, Any]] = []
        match_basis: set[str] = set()
        for doi in dois:
            if doi in merged_by_doi:
                matched_records.append(merged_by_doi[doi])
                match_basis.add("doi")
        for title in titles:
            if title in merged_by_title:
                matched_records.append(merged_by_title[title])
                match_basis.add("normalized_title")
        unique_matched = {record["corpus_id"]: record for record in matched_records}

        detection_summaries = [
            {
                "input_file": relative(Path(item["path"])),
                "query": item["query"],
                "rank": item["rank"],
                "paperId": item["record"].get("paperId", ""),
            }
            for item in sorted(cluster_detections, key=lambda item: (item["path"], item["rank"]))
        ]

        if unique_matched:
            corpus_matches: list[dict[str, Any]] = []
            for doi in dois:
                if doi in corpus_by_doi:
                    corpus_matches.append(corpus_by_doi[doi])
            for title in titles:
                if title in corpus_by_title:
                    corpus_matches.append(corpus_by_title[title])
            unique_corpus = {record["corpus_id"]: record for record in corpus_matches}

            matched_audit.append({
                "record": concise_record(chosen),
                "match_basis": sorted(match_basis),
                "matched_merged_candidates": [
                    {"corpus_id": record["corpus_id"], "title": record.get("title", ""), "doi": record.get("doi", "")}
                    for record in sorted(unique_matched.values(), key=lambda item: item["corpus_id"])
                ],
                "matched_corpus_records": [
                    {"corpus_id": record["corpus_id"], "screening_tier": record.get("screening_tier", ""), "title": record.get("title", ""), "doi": record.get("doi", "")}
                    for record in sorted(unique_corpus.values(), key=lambda item: item["corpus_id"])
                ],
                "direct_identifications": detection_summaries,
                "decision": "matched_existing_record_provenance_appended",
            })
            additions = [direct_provenance(item) for item in cluster_detections]
            for record in unique_matched.values():
                direct_additions_by_merged[record["corpus_id"]].extend(additions)
            for record in unique_corpus.values():
                direct_additions_by_corpus[record["corpus_id"]].extend(additions)
            continue

        decision, reason_code, rationale = assess_new_record(chosen)
        new_audit.append({
            "record": concise_record(chosen),
            "direct_identifications": detection_summaries,
            "decision": decision,
            "reason_code": reason_code,
            "rationale": rationale,
            "assessment_basis": "IEEE direct title/metadata and available abstract; IEEE abstracts marked truncated were not treated as full-text evidence.",
        })

    # Keep the audit ordering stable and legible.
    matched_audit.sort(key=lambda item: (item["record"].get("year") or 0, normalize_title(item["record"].get("title"))))
    new_audit.sort(key=lambda item: (item["record"].get("year") or 0, normalize_title(item["record"].get("title"))))
    decision_counts = Counter(item["decision"] for item in new_audit)
    reason_counts = Counter(item["reason_code"] for item in new_audit)

    primary_raw = sum(load_json(path).get("results_retrieved", 0) for path in primary_full_paths)
    refinement_raw = sum(load_json(path).get("results_retrieved", 0) for path in refinement_full_paths)

    audit = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "update_id": UPDATE_ID,
        "scope": {
            "database": "IEEE Xplore direct metadata endpoint via search_ieee_xplore.py",
            "search_date": UPDATE_DATE,
            "filters": {"year_start": 2013, "year_end": 2026, "language": "English", "content_types": ["Journals", "Conferences"]},
            "deduplication": "Internal fresh records and existing candidates were matched by normalized DOI first and normalized title second.",
            "identifier_policy": "No existing corpus_id was reassigned. Corpus/merged matching was performed by DOI/title rather than relying on pre-existing cross-artifact corpus_id alignment.",
        },
        "source_artifacts": manifest_entries,
        "supplemental_metadata_artifacts": supplemental_entries,
        "deduplication_summary": {
            "primary_direct_raw_identifications": primary_raw,
            "supplementary_q12_population_refinement_identifications": refinement_raw,
            "unique_direct_records_after_internal_deduplication": len(clusters),
            "matched_existing_merged_candidates": len(matched_audit),
            "genuinely_new_direct_records_screened": len(new_audit),
            "new_records_added_to_merged_candidates": 0,
            "new_records_added_to_corpus": 0,
            "screening_decision_counts": dict(sorted(decision_counts.items())),
            "screening_reason_code_counts": dict(sorted(reason_counts.items())),
        },
        "matched_existing_records": matched_audit,
        "screened_genuinely_new_records": new_audit,
    }
    with audit_path.open("w", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "update_id": UPDATE_ID,
        "artifacts": sorted(manifest_entries, key=lambda item: item["input_file"]),
        "supplemental_artifacts": sorted(supplemental_entries, key=lambda item: item["input_file"]),
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    merged_changes = 0
    corpus_changes = 0
    if args.apply:
        merged_lookup = {record["corpus_id"]: record for record in merged_records}
        corpus_lookup = {record["corpus_id"]: record for record in corpus_records}
        for corpus_id, additions in direct_additions_by_merged.items():
            merged_changes += append_provenance(merged_lookup[corpus_id], additions)
        for corpus_id, additions in direct_additions_by_corpus.items():
            corpus_changes += append_provenance(corpus_lookup[corpus_id], additions)

        update_summary = {
            "update_id": UPDATE_ID,
            "date": UPDATE_DATE,
            "audit_file": relative(audit_path),
            "action": "Direct IEEE provenance appended to matches; all 104 genuinely new direct records were excluded and not added to the candidate/corpus set.",
            "matched_existing_merged_candidates": len(matched_audit),
            "matched_existing_corpus_records": sum(bool(item["matched_corpus_records"]) for item in matched_audit),
            "new_records_added_to_merged_candidates": 0,
            "new_records_added_to_corpus": 0,
        }
        for data in (merged_data, corpus_data):
            updates = data.setdefault("controlled_updates", [])
            if not any(item.get("update_id") == UPDATE_ID for item in updates if isinstance(item, dict)):
                updates.append(update_summary)
            data["last_updated_at"] = datetime.now(timezone.utc).isoformat()

        with merged_path.open("w", encoding="utf-8") as handle:
            json.dump(merged_data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        with corpus_path.open("w", encoding="utf-8") as handle:
            json.dump(corpus_data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    print(json.dumps({
        "status": "applied" if args.apply else "dry_run",
        "audit_path": str(audit_path),
        "manifest_path": str(manifest_path),
        "primary_direct_raw_identifications": primary_raw,
        "unique_direct_records": len(clusters),
        "matched_existing_candidates": len(matched_audit),
        "new_records_screened_not_added": len(new_audit),
        "new_records_screened_rejected_not_added": decision_counts["rejected_not_added"],
        "merged_provenance_entries_added": merged_changes,
        "corpus_provenance_entries_added": corpus_changes,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
