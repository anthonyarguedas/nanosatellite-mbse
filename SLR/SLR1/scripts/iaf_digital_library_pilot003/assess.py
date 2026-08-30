#!/usr/bin/env python3
"""Reconcile strict IAF Pilot 003 cell artifacts and local pair checks.

The IAF adapter remains the authority for source totals, rendered identities,
complete traversal, and visible metadata.  This script only validates those
receipts, makes deterministic paper-ID unions across the lossless cells, and
labels metadata-only pair checks as confirmations or uncertainty rather than
source false-match decisions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from plan import (
    CONCEPTS,
    DATE_END,
    DATE_START,
    DEFAULT_PLAN_PATH,
    MAIN_FACTORS,
    MAX_QUERY_CHARACTERS,
    PILOT_DIR,
    SOURCE_ID,
)

# ``artifact_path`` belongs to run_cells, not the plan.  Keeping this import
# block explicit avoids copying concept declarations while retaining a small
# standalone assessment command.
from run_cells import artifact_path, identity_ledger_path  # noqa: E402


ASSESSMENT_SCHEMA = "iaf-digital-library-pilot003-assessment/v1"
PAIR_CHECK_SCHEMA = "iaf-digital-library-pilot003-local-pair-checks/v1"
INVESTIGATION_SCHEMA = "iaf-digital-library-pilot003-union-investigations/v1"
IDENTITY_LEDGER_SCHEMA = "iaf-digital-library-complete-identity-ledger/v1"
DEFAULT_SEARCH_DIR = PILOT_DIR / "searches"
DEFAULT_ASSESSMENT_PATH = DEFAULT_SEARCH_DIR / "assessment.json"
DEFAULT_PAIR_CHECK_PATH = DEFAULT_SEARCH_DIR / "local-pair-checks.json"
DEFAULT_INVESTIGATION_PATH = DEFAULT_SEARCH_DIR / "union-investigations.json"
INVESTIGATION_THRESHOLD = 100
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
SAFE_REASON_RE = re.compile(r"[^A-Za-z0-9_.:-]+")


class AssessmentError(ValueError):
    """Raised for malformed pilot inputs or unsafe artifact publication."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_no_clobber(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise AssessmentError(f"refusing to overwrite {path}")
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> tuple[str, int]:
    body = path.read_bytes()
    return hashlib.sha256(body).hexdigest(), len(body)


def marker_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.ACADEMIC_SEARCH_COMMIT.json")


def safe_reason(value: Any) -> str:
    text = SAFE_REASON_RE.sub("_", str(value or "")).strip("_")
    return text[:160] or "artifact_validation_failed"


def relative(search_dir: Path, path: Path) -> str:
    return str(path.relative_to(search_dir))


def validate_marker(path: Path) -> str | None:
    marker = marker_path(path)
    if not marker.is_file() or marker.is_symlink():
        return "missing_commit_marker"
    try:
        data = load_json(marker)
        digest, byte_count = sha256_file(path)
    except (OSError, json.JSONDecodeError):
        return "invalid_commit_marker"
    normalized = data.get("normalized_json") if isinstance(data, Mapping) else None
    if (
        not isinstance(normalized, Mapping)
        or data.get("schema") != "academic_search_output_commit_marker_v1"
        or normalized.get("sha256") != digest
        or normalized.get("bytes") != byte_count
    ):
        return "commit_marker_hash_mismatch"
    return None


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _sequence_sha256(values: Sequence[str]) -> str:
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def validate_complete_artifact(
    data: Any,
    ledger: Any,
    *,
    query: str,
    artifact_path: Path,
) -> tuple[list[str], dict[str, Any]]:
    """Validate compact adapter output against its same-run identity sidecar.

    The maintained output writer intentionally compacts repeated browser and
    stable-ID metadata.  The collector's create-only ledger is made from that
    exact in-memory complete result before compaction and hash-binds it to the
    compact marker-gated artifact.
    """

    errors: list[str] = []
    extracted: dict[str, Any] = {}
    if not isinstance(data, Mapping):
        return ["artifact_not_object"], extracted
    if not isinstance(ledger, Mapping):
        return ["identity_ledger_not_object"], extracted
    metadata = data.get("output_metadata")
    receipt = metadata.get("prisma_search_run") if isinstance(metadata, Mapping) else None
    counts = receipt.get("staged_counts") if isinstance(receipt, Mapping) else None
    strategy = receipt.get("strategy") if isinstance(receipt, Mapping) else None
    total = data.get("total")
    results = data.get("results")
    if not isinstance(metadata, Mapping):
        errors.append("missing_output_metadata")
    if not _is_nonnegative_int(total):
        errors.append("total_not_exact_nonnegative_integer")
    if not isinstance(results, list):
        errors.append("results_not_list")
        results = []
    if metadata.get("status") != "success":
        errors.append("adapter_status_not_success")
    if metadata.get("count_only") is not False:
        errors.append("count_only_not_false")
    if metadata.get("retrieval_complete") is not True:
        errors.append("retrieval_complete_not_true")
    if metadata.get("merge_eligible") is not True:
        errors.append("merge_eligible_not_true")
    if not isinstance(receipt, Mapping):
        errors.append("missing_prisma_search_run")
    else:
        if receipt.get("schema_version") != "academic-search-prisma-search-run/v2":
            errors.append("wrong_prisma_search_run_schema")
        if receipt.get("completion_status") != "complete" or receipt.get("report_ready") is not True:
            errors.append("compact_receipt_not_complete")
    if not isinstance(strategy, Mapping):
        errors.append("missing_compact_strategy")
    else:
        if strategy.get("executed_query") != query or data.get("executed_query") != query:
            errors.append("executed_query_does_not_match_planned_cell")
        processing = strategy.get("query_syntax", {}).get("queryprocessing") if isinstance(strategy.get("query_syntax"), Mapping) else None
        if not isinstance(processing, Mapping) or processing.get("exact_query_echo_proved") is not True:
            errors.append("exact_query_echo_not_attested")
        limits = strategy.get("limits")
        publication_date = limits.get("publication_date") if isinstance(limits, Mapping) else None
        if not isinstance(publication_date, Mapping):
            errors.append("missing_local_date_limit")
        else:
            requested = publication_date.get("requested")
            effective = publication_date.get("effective")
            if (
                not isinstance(requested, Mapping)
                or requested.get("start") != DATE_START
                or requested.get("end") != DATE_END
                or requested.get("inclusive") is not True
                or not isinstance(effective, Mapping)
                or effective.get("mode") != "local_post_filter"
            ):
                errors.append("local_date_window_not_reconciled")
        additional = limits.get("additional_result_filters") if isinstance(limits, Mapping) else None
        if not isinstance(additional, Mapping) or additional.get("state") != "not_applicable":
            errors.append("unexpected_additional_source_filter")
    if not isinstance(counts, Mapping):
        errors.append("missing_compact_staged_counts")
    else:
        if (
            counts.get("source_reported_total") != total
            or counts.get("raw_source_records") != total
            or counts.get("records_exported") != len(results)
            or counts.get("local_match_count") != len(results)
            or not _is_nonnegative_int(counts.get("client_side_exclusions"))
            or counts.get("client_side_exclusions") + len(results) != total
        ):
            errors.append("compact_staged_counts_do_not_reconcile")
    if ledger.get("schema_version") != IDENTITY_LEDGER_SCHEMA:
        errors.append("wrong_identity_ledger_schema")
    if ledger.get("source") != "IAF Digital Library" or ledger.get("query") != query:
        errors.append("identity_ledger_source_or_query_mismatch")
    compact = ledger.get("compact_artifact")
    try:
        artifact_digest, artifact_bytes = sha256_file(artifact_path)
    except OSError:
        artifact_digest, artifact_bytes = None, None
        errors.append("cannot_hash_compact_artifact")
    if (
        not isinstance(compact, Mapping)
        or compact.get("file_name") != artifact_path.name
        or compact.get("sha256") != artifact_digest
        or compact.get("bytes") != artifact_bytes
        or compact.get("commit_marker") != marker_path(artifact_path).name
    ):
        errors.append("identity_ledger_compact_binding_mismatch")
    raw_ids = ledger.get("raw_ordered_paper_ids")
    retained_ids = ledger.get("diagnostic_window_ordered_paper_ids")
    if not isinstance(raw_ids, list) or len(raw_ids) != total or any(
        not isinstance(value, str) or not value for value in raw_ids
    ):
        errors.append("raw_stable_id_ledger_invalid")
        raw_ids = []
    elif len({value.casefold() for value in raw_ids}) != len(raw_ids):
        errors.append("raw_stable_id_ledger_has_duplicates")
    if not isinstance(retained_ids, list) or any(
        not isinstance(value, str) or not value for value in retained_ids
    ):
        errors.append("retained_stable_id_ledger_invalid")
        retained_ids = []
    elif len({value.casefold() for value in retained_ids}) != len(retained_ids):
        errors.append("retained_stable_id_ledger_has_duplicates")
    if ledger.get("raw_ordered_paper_ids_sha256") != _sequence_sha256(raw_ids):
        errors.append("raw_stable_id_hash_mismatch")
    if ledger.get("diagnostic_window_ordered_paper_ids_sha256") != _sequence_sha256(retained_ids):
        errors.append("retained_stable_id_hash_mismatch")
    result_ids = [item.get("paperId") for item in results if isinstance(item, Mapping)]
    if len(result_ids) != len(results) or result_ids != retained_ids:
        errors.append("retained_records_do_not_match_identity_ledger")
    date = ledger.get("date_filter_accounting")
    if not isinstance(date, Mapping):
        errors.append("missing_identity_date_accounting")
        date = {}
    elif (
        date.get("raw_total") != total
        or date.get("source_total") != total
        or date.get("source_entries_retrieved") != total
        or date.get("retained") != len(retained_ids)
        or date.get("retained_written") != len(retained_ids)
        or date.get("complete") is not True
        or not _is_nonnegative_int(date.get("excluded"))
        or date.get("excluded") + len(retained_ids) != total
        or not _is_nonnegative_int(date.get("unresolved"))
        or date.get("unresolved") > len(retained_ids)
    ):
        errors.append("identity_date_accounting_not_reconciled")
    completion = ledger.get("completion")
    if (
        not isinstance(completion, Mapping)
        or completion.get("source_total") != total
        or completion.get("source_entries_retrieved") != total
        or completion.get("two_pass_order_verified") is not True
        or completion.get("two_pass_capture_verified") is not True
        or completion.get("detail_capture_complete") is not True
        or completion.get("local_date_filter_complete") is not True
        or completion.get("complete_source_total_cap") != 5000
    ):
        errors.append("identity_completion_proof_not_reconciled")
    if _is_nonnegative_int(total) and total > 5000:
        errors.append("source_total_exceeds_fixed_complete_cap")
    extracted = {
        "total": total,
        "raw_ids": list(raw_ids),
        "retained_ids": list(retained_ids),
        "results": list(results),
        "date_accounting": dict(date),
        "metadata": metadata,
        "identity_ledger_provenance": ledger.get("provenance"),
    }
    return errors, extracted


def record_fingerprint(record: Mapping[str, Any]) -> str:
    keys = (
        "paperId",
        "sourceRecordId",
        "doi",
        "title",
        "year",
        "publicationDate",
        "publicationDatePrecision",
        "abstract",
        "abstract_not_available",
    )
    projected = {key: record.get(key) for key in keys}
    encoded = json.dumps(projected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def tokens(value: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return tuple(TOKEN_RE.findall(normalized))


def phrase_spans(field_tokens: Sequence[str], phrase: str) -> tuple[tuple[int, int], ...]:
    needle = tokens(phrase)
    if not needle or len(needle) > len(field_tokens):
        return ()
    return tuple(
        (start, start + len(needle))
        for start in range(len(field_tokens) - len(needle) + 1)
        if tuple(field_tokens[start : start + len(needle)]) == needle
    )


def literal_present(field_tokens: Sequence[str], literal: str) -> bool:
    return bool(phrase_spans(field_tokens, literal))


def pair_hits(
    field_tokens: Sequence[str], left: str, right: str
) -> tuple[dict[str, int], ...]:
    """Return exact phrase-pair hits with at most five intervening tokens."""

    hits: list[dict[str, int]] = []
    for left_start, left_end in phrase_spans(field_tokens, left):
        for right_start, right_end in phrase_spans(field_tokens, right):
            if left_end <= right_start:
                gap = right_start - left_end
                ordered = {
                    "left_start_token": left_start + 1,
                    "left_end_token": left_end,
                    "right_start_token": right_start + 1,
                    "right_end_token": right_end,
                    "intervening_lexical_tokens": gap,
                }
            elif right_end <= left_start:
                gap = left_start - right_end
                ordered = {
                    "right_start_token": right_start + 1,
                    "right_end_token": right_end,
                    "left_start_token": left_start + 1,
                    "left_end_token": left_end,
                    "intervening_lexical_tokens": gap,
                }
            else:
                continue
            if gap <= 5:
                hits.append(ordered)
    return tuple(hits)


def partition_pairs(partition_id: str) -> tuple[tuple[str, int, str, str], ...]:
    output: list[tuple[str, int, str, str]] = []
    for factor_names in MAIN_FACTORS[partition_id]:
        for concept_name in factor_names:
            for ordinal, (left, right) in enumerate(CONCEPTS[concept_name].pairs, start=1):
                output.append((concept_name, ordinal, left, right))
    return tuple(output)


def record_text_fields(manifestations: Iterable[Mapping[str, Any]]) -> dict[str, tuple[tuple[str, ...], ...]]:
    fields: dict[str, list[tuple[str, ...]]] = {"title": [], "abstract": []}
    seen: dict[str, set[tuple[str, ...]]] = {"title": set(), "abstract": set()}
    for record in manifestations:
        title = record.get("title")
        if isinstance(title, str) and title.strip():
            title_tokens = tokens(title)
            if title_tokens and title_tokens not in seen["title"]:
                seen["title"].add(title_tokens)
                fields["title"].append(title_tokens)
        abstract = record.get("abstract")
        if (
            record.get("abstract_not_available") is not True
            and isinstance(abstract, str)
            and abstract.strip()
        ):
            abstract_tokens = tokens(abstract)
            if abstract_tokens and abstract_tokens not in seen["abstract"]:
                seen["abstract"].add(abstract_tokens)
                fields["abstract"].append(abstract_tokens)
    return {name: tuple(values) for name, values in fields.items()}


def check_pairs_for_record(
    pair_declarations: Sequence[tuple[str, int, str, str]],
    manifestations: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    fields = record_text_fields(manifestations)
    matches: list[dict[str, Any]] = []
    for concept_name, ordinal, left, right in pair_declarations:
        for field_name, field_versions in fields.items():
            found = False
            for field_tokens in field_versions:
                hits = pair_hits(field_tokens, left, right)
                if hits:
                    matches.append(
                        {
                            "concept": concept_name,
                            "pair_ordinal": ordinal,
                            "left": left,
                            "right": right,
                            "field": field_name,
                            "first_hit": hits[0],
                        }
                    )
                    found = True
                    break
            if found:
                continue
    available = {name: len(values) for name, values in fields.items()}
    if matches:
        status = "confirmed_in_available_title_or_abstract"
    elif any(available.values()):
        status = "not_confirmed_in_available_metadata_preserved_uncertain"
    else:
        status = "metadata_unavailable_preserved_uncertain"
    return {
        "status": status,
        "available_field_versions": available,
        "matches": matches,
    }


def factor_metadata_check(
    factor_names: Sequence[str],
    manifestations: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """QA only: test visible title/abstract evidence without redefining a hit."""

    fields = record_text_fields(manifestations)
    literals = [
        literal
        for concept_name in factor_names
        for literal in CONCEPTS[concept_name].literals
    ]
    pairs = [
        (concept_name, ordinal, left, right)
        for concept_name in factor_names
        for ordinal, (left, right) in enumerate(CONCEPTS[concept_name].pairs, start=1)
    ]
    literal_hits = 0
    for literal in literals:
        if any(literal_present(version, literal) for versions in fields.values() for version in versions):
            literal_hits += 1
    pair_check = check_pairs_for_record(pairs, manifestations) if pairs else None
    pair_hit_count = len(pair_check["matches"]) if pair_check is not None else 0
    if literal_hits or pair_hit_count:
        status = "visible_metadata_confirmation"
    elif any(fields.values()):
        status = "not_confirmed_in_available_metadata_preserved_uncertain"
    else:
        status = "metadata_unavailable_preserved_uncertain"
    return {
        "concepts": list(factor_names),
        "status": status,
        "literal_matches": literal_hits,
        "exact_pair_matches": pair_hit_count,
    }


def union_digest(ids: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for paper_id in sorted(ids):
        digest.update(paper_id.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def union_summary(ids: Iterable[str], event_occurrences: int) -> dict[str, Any]:
    ordered = sorted(ids)
    return {
        "deduplicated_count": len(ordered),
        "source_event_occurrences": event_occurrences,
        "duplicate_event_occurrences": event_occurrences - len(ordered),
        "paper_ids": ordered,
        "paper_ids_sha256": union_digest(ordered),
    }


def complete_entry(
    partition_id: str,
    cell_rows: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, list[Mapping[str, Any]]]]:
    raw_memberships: dict[str, list[dict[str, Any]]] = defaultdict(list)
    retained_memberships: dict[str, list[dict[str, Any]]] = defaultdict(list)
    record_manifestations: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    raw_occurrences = 0
    retained_occurrences = 0
    date_event_counts: Counter[str] = Counter()
    raw_total_sum = 0
    for row in cell_rows:
        raw_total_sum += int(row["total"])
        date = row["date_accounting"]
        for key in ("included", "excluded", "unresolved", "retained"):
            value = date.get(key)
            if _is_nonnegative_int(value):
                date_event_counts[key] += value
        for paper_id in row["raw_ids"]:
            raw_memberships[paper_id].append(
                {"cell_id": row["cell_id"], "artifact": row["artifact"]}
            )
            raw_occurrences += 1
        retained_records = {
            record.get("paperId"): record
            for record in row["results"]
            if isinstance(record, Mapping) and isinstance(record.get("paperId"), str)
        }
        for paper_id in row["retained_ids"]:
            retained_memberships[paper_id].append(
                {"cell_id": row["cell_id"], "artifact": row["artifact"]}
            )
            record = retained_records.get(paper_id)
            if record is not None:
                record_manifestations[paper_id].append(record)
            retained_occurrences += 1
    raw_union = union_summary(raw_memberships, raw_occurrences)
    retained_union = union_summary(retained_memberships, retained_occurrences)
    all_ids = sorted(set(raw_memberships) | set(retained_memberships))
    membership = []
    for paper_id in all_ids:
        variants = sorted(
            {
                record_fingerprint(record)
                for record in record_manifestations.get(paper_id, [])
            }
        )
        membership.append(
            {
                "paper_id": paper_id,
                "raw_cell_ids": sorted({item["cell_id"] for item in raw_memberships.get(paper_id, [])}),
                "retained_cell_ids": sorted({item["cell_id"] for item in retained_memberships.get(paper_id, [])}),
                "record_manifestation_count": len(record_manifestations.get(paper_id, [])),
                "metadata_variant_sha256": variants,
                "metadata_variants_preserved": len(variants) > 1,
            }
        )
    entry = {
        "partition_id": partition_id,
        "status": "complete",
        "planned_cells": len(cell_rows),
        "complete_cells": len(cell_rows),
        "failed_cells": [],
        "source_event_counts": {
            "raw_source_total_sum": raw_total_sum,
            "raw_paper_id_occurrences": raw_occurrences,
            "diagnostic_window_paper_id_occurrences": retained_occurrences,
            "date_filter_event_counts": {
                key: date_event_counts.get(key, 0)
                for key in ("included", "excluded", "unresolved", "retained")
            },
        },
        "raw_paper_id_union": raw_union,
        "diagnostic_window_paper_id_union": retained_union,
        "paper_id_membership": membership,
        "investigation_required": {
            "threshold": INVESTIGATION_THRESHOLD,
            "raw_paper_id_union": raw_union["deduplicated_count"] > INVESTIGATION_THRESHOLD,
            "diagnostic_window_paper_id_union": retained_union["deduplicated_count"] > INVESTIGATION_THRESHOLD,
        },
    }
    return entry, record_manifestations


def failure_entry(
    partition_id: str,
    planned_count: int,
    complete_rows: Sequence[Mapping[str, Any]],
    failures: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Fail closed: an incomplete partition publishes no aggregate total."""

    return {
        "partition_id": partition_id,
        "status": "failure",
        "planned_cells": planned_count,
        "complete_cells": len(complete_rows),
        "failed_cells": list(failures),
        "source_event_counts": None,
        "raw_paper_id_union": None,
        "diagnostic_window_paper_id_union": None,
        "paper_id_membership": None,
        "investigation_required": None,
        "failure_total_policy": "aggregate totals and unions are null when any planned cell is incomplete, malformed, missing, or source-failed",
    }


def build_pair_checks(
    entries: Mapping[str, Mapping[str, Any]],
    record_store: Mapping[str, Mapping[str, list[Mapping[str, Any]]]],
) -> dict[str, Any]:
    partitions: dict[str, Any] = {}
    for partition_id in MAIN_FACTORS:
        entry = entries[partition_id]
        pairs = partition_pairs(partition_id)
        if not pairs:
            partitions[partition_id] = {
                "status": "not_applicable_no_declared_pairs",
                "declared_pair_count": 0,
                "records": [],
            }
            continue
        if entry["status"] != "complete":
            partitions[partition_id] = {
                "status": "not_run_partition_incomplete",
                "declared_pair_count": len(pairs),
                "records": None,
            }
            continue
        records = []
        for paper_id in sorted(record_store[partition_id]):
            manifestations = record_store[partition_id][paper_id]
            checked = check_pairs_for_record(pairs, manifestations)
            membership = next(
                item
                for item in entry["paper_id_membership"]
                if item["paper_id"] == paper_id
            )
            records.append(
                {
                    "paper_id": paper_id,
                    "retained_cell_ids": membership["retained_cell_ids"],
                    "record_manifestation_count": len(manifestations),
                    **checked,
                }
            )
        statuses = Counter(record["status"] for record in records)
        partitions[partition_id] = {
            "status": "complete",
            "declared_pair_count": len(pairs),
            "pair_rule": "left and right exact lexical phrase sequences in either order within the same visible title or abstract, with no more than five intervening lexical tokens",
            "tokenization": "Unicode NFKC case-folded word tokens; punctuation and hyphen separators are non-lexical separators for this local QA only",
            "uncertainty_policy": "No absent metadata match is called a source false match: IAF may have matched another indexed field or the documented broader pair fallback.",
            "summary": {
                "retained_deduplicated_records": len(records),
                "confirmed_in_available_title_or_abstract": statuses.get("confirmed_in_available_title_or_abstract", 0),
                "not_confirmed_preserved_uncertain": statuses.get("not_confirmed_in_available_metadata_preserved_uncertain", 0),
                "metadata_unavailable_preserved_uncertain": statuses.get("metadata_unavailable_preserved_uncertain", 0),
            },
            "records": records,
        }
    return {
        "schema_version": PAIR_CHECK_SCHEMA,
        "pilot": "003",
        "source": SOURCE_ID,
        "scope": "diagnostic-window retained records only",
        "partitions": partitions,
    }


def build_investigations(
    entries: Mapping[str, Mapping[str, Any]],
    record_store: Mapping[str, Mapping[str, list[Mapping[str, Any]]]],
) -> dict[str, Any]:
    investigations: list[dict[str, Any]] = []
    for partition_id in MAIN_FACTORS:
        entry = entries[partition_id]
        if entry["status"] != "complete":
            continue
        for union_name, record_scope in (
            ("raw_paper_id_union", "raw"),
            ("diagnostic_window_paper_id_union", "diagnostic_window"),
        ):
            union = entry[union_name]
            if union["deduplicated_count"] <= INVESTIGATION_THRESHOLD:
                continue
            rows = []
            for membership in entry["paper_id_membership"]:
                paper_id = membership["paper_id"]
                manifestations = record_store[partition_id].get(paper_id, [])
                if record_scope == "diagnostic_window" and not manifestations:
                    continue
                if manifestations:
                    factor_checks = [
                        factor_metadata_check(factor_names, manifestations)
                        for factor_names in MAIN_FACTORS[partition_id]
                    ]
                    metadata_status = "available_title_or_abstract_checked"
                else:
                    factor_checks = None
                    metadata_status = "not_available_after_local_date_filter_preserved_uncertain"
                rows.append(
                    {
                        "paper_id": paper_id,
                        "raw_cell_ids": membership["raw_cell_ids"],
                        "retained_cell_ids": membership["retained_cell_ids"],
                        "metadata_status": metadata_status,
                        "factor_checks": factor_checks,
                    }
                )
            summary = Counter()
            for row in rows:
                if row["factor_checks"] is None:
                    summary["metadata_unavailable"] += 1
                    continue
                if all(
                    check["status"] == "visible_metadata_confirmation"
                    for check in row["factor_checks"]
                ):
                    summary["all_factors_visible_metadata_confirmation"] += 1
                else:
                    summary["one_or_more_factors_not_confirmed_preserved_uncertain"] += 1
            investigations.append(
                {
                    "partition_id": partition_id,
                    "union": union_name,
                    "deduplicated_union_count": union["deduplicated_count"],
                    "threshold": INVESTIGATION_THRESHOLD,
                    "scope": record_scope,
                    "interpretation": "A metadata QA investigation, not a source false-match classifier. Visible title/abstract absence remains uncertain because IAF's Any keyword route may match other indexed bibliographic text and pair cells use the documented broader fallback.",
                    "summary": dict(sorted(summary.items())),
                    "records": rows,
                }
            )
    return {
        "schema_version": INVESTIGATION_SCHEMA,
        "pilot": "003",
        "source": SOURCE_ID,
        "threshold": INVESTIGATION_THRESHOLD,
        "investigations": investigations,
    }


def build_assessment(
    plan: Mapping[str, Any], search_dir: Path, plan_path: Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    entries: dict[str, Mapping[str, Any]] = {}
    record_store: dict[str, Mapping[str, list[Mapping[str, Any]]]] = {}
    plan_entries = plan["partitions"]
    for partition_id in MAIN_FACTORS:
        expected_cells = plan_entries[partition_id]["cells"]
        complete_rows: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        for cell in expected_cells:
            path = artifact_path(search_dir, partition_id, cell["cell_id"])
            artifact_ref = relative(search_dir, path)
            if not path.is_file() or path.is_symlink():
                failures.append(
                    {
                        "cell_id": cell["cell_id"],
                        "artifact": artifact_ref,
                        "status": "missing_artifact",
                        "total": None,
                    }
                )
                continue
            ledger_path = identity_ledger_path(path)
            ledger_ref = relative(search_dir, ledger_path)
            if not ledger_path.is_file() or ledger_path.is_symlink():
                failures.append(
                    {
                        "cell_id": cell["cell_id"],
                        "artifact": artifact_ref,
                        "identity_ledger": ledger_ref,
                        "status": "missing_identity_ledger",
                        "total": None,
                    }
                )
                continue
            marker_error = validate_marker(path)
            try:
                data = load_json(path)
                ledger = load_json(ledger_path)
            except (OSError, json.JSONDecodeError):
                failures.append(
                    {
                        "cell_id": cell["cell_id"],
                        "artifact": artifact_ref,
                        "identity_ledger": ledger_ref,
                        "status": "invalid_json",
                        "total": None,
                    }
                )
                continue
            errors, extracted = validate_complete_artifact(
                data,
                ledger,
                query=cell["query"],
                artifact_path=path,
            )
            if marker_error is not None:
                errors.append(marker_error)
            if errors:
                metadata = data.get("output_metadata") if isinstance(data, Mapping) else {}
                failures.append(
                    {
                        "cell_id": cell["cell_id"],
                        "artifact": artifact_ref,
                        "status": safe_reason(metadata.get("status") if isinstance(metadata, Mapping) else "artifact_invalid"),
                        "reason_codes": sorted(set(errors)),
                        "total": None,
                    }
                )
                continue
            complete_rows.append(
                {
                    "cell_id": cell["cell_id"],
                    "artifact": artifact_ref,
                    "identity_ledger": ledger_ref,
                    **extracted,
                }
            )
        if failures:
            entries[partition_id] = failure_entry(
                partition_id, len(expected_cells), complete_rows, failures
            )
            record_store[partition_id] = {}
        else:
            entry, records = complete_entry(partition_id, complete_rows)
            entries[partition_id] = entry
            record_store[partition_id] = records
    pair_checks = build_pair_checks(entries, record_store)
    investigations = build_investigations(entries, record_store)
    plan_digest, plan_bytes = sha256_file(plan_path) if plan_path.exists() else (None, None)
    summary = {
        "planned_partitions": len(MAIN_FACTORS),
        "complete_partitions": sum(entry["status"] == "complete" for entry in entries.values()),
        "failed_partitions": sum(entry["status"] != "complete" for entry in entries.values()),
        "planned_cells": sum(entry["planned_cells"] for entry in entries.values()),
        "complete_cells": sum(entry["complete_cells"] for entry in entries.values()),
        "failed_cells": sum(len(entry["failed_cells"]) for entry in entries.values()),
        "unions_over_threshold": len(investigations["investigations"]),
    }
    assessment = {
        "schema_version": ASSESSMENT_SCHEMA,
        "pilot": "003",
        "source": {"id": SOURCE_ID, "label": "IAF Digital Library"},
        "mode": "diagnostic_only_not_final_search",
        "date_window": {
            "start_date": DATE_START,
            "cutoff_date": DATE_END,
            "inclusive": True,
            "source_side_date_filter": "unavailable",
            "applied": "local post-filter only after each complete raw cell traversal",
        },
        "controls": {
            "language": "not applied; source language assignment completeness is not proved",
            "publication_type": "not applied; IAF Digital Library is conference-paper scoped",
            "access": "not applied",
            "wildcard": "not used; no per-partition wildcard validation was needed",
            "source_native_partitioning": "not used; unproved event/year composition remains prohibited",
            "source_complete_run_cap": 5000,
            "query_character_cap": MAX_QUERY_CHARACTERS,
        },
        "plan": {
            "artifact": "cell-plan.json",
            "sha256": plan_digest,
            "bytes": plan_bytes,
            "packed_cells": plan["packing"]["packed_cells"],
            "shared_equal_budget_baseline_cells": plan["packing"]["shared_equal_budget_baseline_cells"],
        },
        "pair_check_artifact": "local-pair-checks.json",
        "investigation_artifact": "union-investigations.json",
        "entries": entries,
        "summary": summary,
    }
    return assessment, pair_checks, investigations


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--search-dir", type=Path, default=DEFAULT_SEARCH_DIR)
    parser.add_argument("--assessment-path", type=Path, default=DEFAULT_ASSESSMENT_PATH)
    parser.add_argument("--pair-check-path", type=Path, default=DEFAULT_PAIR_CHECK_PATH)
    parser.add_argument("--investigation-path", type=Path, default=DEFAULT_INVESTIGATION_PATH)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        plan = load_json(args.plan.expanduser())
        from plan import validate_plan_payload

        errors = validate_plan_payload(plan)
        if errors:
            raise AssessmentError("invalid plan: " + "; ".join(errors))
        assessment, pair_checks, investigations = build_assessment(
            plan,
            args.search_dir.expanduser().resolve(),
            args.plan.expanduser(),
        )
    except (OSError, json.JSONDecodeError, AssessmentError, ValueError) as error:
        parser.error(str(error))
    if args.dry_run:
        print(json.dumps(assessment["summary"], indent=2))
        return 1 if assessment["summary"]["failed_partitions"] else 0
    try:
        write_json_no_clobber(args.pair_check_path.expanduser(), pair_checks)
        write_json_no_clobber(args.investigation_path.expanduser(), investigations)
        write_json_no_clobber(args.assessment_path.expanduser(), assessment)
    except AssessmentError as error:
        parser.error(str(error))
    print(json.dumps(assessment["summary"], indent=2))
    return 1 if assessment["summary"]["failed_partitions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
