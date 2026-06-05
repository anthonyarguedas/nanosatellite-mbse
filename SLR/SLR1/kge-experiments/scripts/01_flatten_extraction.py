#!/usr/bin/env python3
"""Flatten SLR1 extraction data and generate the E0 data-audit outputs.

This script is intentionally dependency-light: it uses only the Python standard
library so it can run in the repository's baseline environment.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


EXPECTED_EXTRACTION_SECTIONS = [
    "bibliographic_review_management",
    "study_context_population",
    "mbse_objective_scope_artifacts",
    "implementation_pathway_tailoring",
    "toolchain_interoperability_lifecycle_continuity",
    "eps_verification_specific",
    "claimed_outcomes_value_mechanisms_evidence",
    "governance_roi_project_decision_linkage",
    "gap_mapping",
    "synthesis_consistency",
]

QUALITY_ITEMS = [
    "credible_venue",
    "limitations_discussed",
    "context_described",
    "mbse_details_replicable",
    "outcomes_linked_to_mbse",
    "evidence_for_outcomes",
    "traceability_reported",
    "reproducibility_toolchain_reported",
]

QUALITY_SCORE_BY_LABEL = {
    "yes": 1.0,
    "insufficiently": 0.5,
    "partial": 0.5,
    "partially": 0.5,
    "no": 0.0,
    "not reported": 0.0,
    "not_reported": 0.0,
    "none": 0.0,
}

QUOTE_KEYS = {
    "quote",
    "direct_quote",
    "evidence_quote",
    "quote_or_location",
}
QUOTE_CONTAINER_KEYS = {
    "evidence",
    "additional_evidence",
    "evidence_source",
    "direct_evidence_quotes",
    "direct_evidence_quotes_for_classification",
    "direct_evidence_quotes_supporting_classification",
    "direct_evidence_quotes_supporting_classifications",
    "direct_evidence_quotes_supporting_classification_decisions",
    "context_evidence",
    "context_evidence_quotes",
    "context_quotes",
    "key_context_evidence",
    "key_context_quotes",
    "key_quotes",
    "project_maturity_evidence",
}

CLAIM_LIST_FIELDS = {
    "outcome_category",
    "mbse_mechanism",
    "lifecycle_stage",
    "evidence_type",
    "metric",
    "reliability_subtype",
}

STAT_FIELD_MAP = {
    "eps_relevance_counts": "study_context_population.eps_relevance",
    "approach_classification_counts": "implementation_pathway_tailoring.approach_classification",
    "extraction_confidence_counts": "synthesis_consistency.extraction_confidence",
    "ivv_integration_level_counts": "eps_verification_specific.ivv_integration_level",
    "reliability_subtype_counts": "claimed_outcomes_value_mechanisms_evidence[].reliability_subtype",
    "generality_reuse_mechanism_counts": "mbse_objective_scope_artifacts.generality_reuse_mechanism",
}


class EvidenceQuoteCollector:
    """Assign deterministic quote ids while preserving backlink provenance."""

    def __init__(self, generated_at: str | None, codebook_version: str | None) -> None:
        self.generated_at = generated_at
        self.codebook_version = codebook_version
        self.records: list[dict[str, Any]] = []
        self._seq_by_study: defaultdict[str, int] = defaultdict(int)

    def add_many(
        self,
        quote_items: list[dict[str, Any]],
        *,
        study_id: str,
        field_path: str,
        source_path: str,
        coded_value: Any = None,
        parent_record_type: str | None = None,
        parent_record_id: str | None = None,
        claim_id: str | None = None,
    ) -> None:
        for item in quote_items:
            quote = clean_text(item.get("quote"))
            if not quote:
                continue
            self._seq_by_study[study_id] += 1
            quote_id = f"{study_id}::quote-{self._seq_by_study[study_id]:04d}"
            self.records.append(
                {
                    "evidence_quote_id": quote_id,
                    "study_id": study_id,
                    "claim_id": claim_id,
                    "parent_record_type": parent_record_type,
                    "parent_record_id": parent_record_id,
                    "field_path": field_path,
                    "source_path": source_path,
                    "coded_value": canonical_value(coded_value) if coded_value is not None else None,
                    "evidence_quote": quote,
                    "location": clean_text(item.get("location")),
                    "topic": clean_text(item.get("topic")),
                    "quote_source_key": clean_text(item.get("source_key")),
                    "source_generated_at": self.generated_at,
                    "source_codebook_version": self.codebook_version,
                }
            )


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = " ".join(value.split())
        return text or None
    return str(value)


def slugify(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "blank"


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def canonical_value(value: Any) -> Any:
    """Return values in a JSON/CSV-friendly scalar form without losing content."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def score_label(score: float) -> str:
    return f"{score:.1f}"


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and not value:
            continue
        return value
    return None


def get_nested(obj: dict[str, Any], dotted_path: str) -> tuple[bool, Any]:
    cur: Any = obj
    for part in dotted_path.split("."):
        if part.endswith("[]"):
            part = part[:-2]
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def extract_quote_items(value: Any, parent_key: str | None = None) -> list[dict[str, Any]]:
    """Recursively collect exact quote-like evidence snippets.

    The source extraction uses several quote shapes: {quote, location}, raw
    strings under evidence arrays, direct_quote/evidence_quote fields, and a few
    direct_evidence_quotes/context_quotes arrays. Location-only fields are
    intentionally skipped.
    """
    items: list[dict[str, Any]] = []

    if value is None:
        return items

    if isinstance(value, str):
        key = (parent_key or "").lower()
        if key in QUOTE_KEYS or key in QUOTE_CONTAINER_KEYS or (
            "quote" in key and "location" not in key
        ):
            items.append({"quote": value, "source_key": parent_key})
        return items

    if isinstance(value, list):
        for item in value:
            items.extend(extract_quote_items(item, parent_key=parent_key))
        return items

    if not isinstance(value, dict):
        return items

    if isinstance(value.get("quote"), str):
        items.append(
            {
                "quote": value.get("quote"),
                "location": value.get("location"),
                "topic": value.get("topic") or value.get("classification"),
                "source_key": "quote",
            }
        )

    for key in QUOTE_KEYS - {"quote"}:
        if isinstance(value.get(key), str):
            items.append(
                {
                    "quote": value.get(key),
                    "location": value.get("location") or value.get("quote_location"),
                    "topic": value.get("topic") or value.get("classification"),
                    "source_key": key,
                }
            )

    for key, child in value.items():
        if key in {"quote", "direct_quote", "evidence_quote", "quote_location"}:
            continue
        if key.endswith("_location"):
            continue
        child_key = key if key in QUOTE_CONTAINER_KEYS or "quote" in key.lower() else key
        items.extend(extract_quote_items(child, parent_key=child_key))

    return items


def normalize_code_entry(entry: Any) -> dict[str, Any]:
    """Normalize a controlled-code-like value to values/status/provenance."""
    result = {
        "values": [],
        "status": None,
        "rationale": None,
        "evidence_items": extract_quote_items(entry),
        "confidence": None,
    }

    if isinstance(entry, dict):
        raw_values: Any = None
        for key in ("values", "value", "classification", "rating", "mapping", "relevance", "level"):
            if key in entry:
                raw_values = entry.get(key)
                break
        if raw_values is None and "controlled_values" in entry:
            raw_values = entry.get("controlled_values")
        if raw_values is None and entry.get("status") not in {None, "coded", "not_reported", "not_applicable", "none", "uncertain"}:
            raw_values = entry.get("status")
        if raw_values is not None:
            result["values"] = ensure_list(raw_values)
        result["status"] = first_nonempty(entry.get("status"), entry.get("classification_status"))
        result["rationale"] = first_nonempty(
            entry.get("rationale"),
            entry.get("reason"),
            entry.get("confidence_rationale"),
            entry.get("reliability_subtype_rationale"),
        )
        result["confidence"] = first_nonempty(entry.get("confidence"), entry.get("extractor_confidence"))
        return result

    if isinstance(entry, list):
        result["values"] = entry
        result["status"] = "coded" if entry else "not_reported"
        return result

    if entry is not None:
        result["values"] = [entry]
        result["status"] = "coded"
    return result


def normalized_values(entry: Any) -> list[Any]:
    values = normalize_code_entry(entry)["values"]
    return [canonical_value(value) for value in values if value is not None and value != ""]


def normalized_scalar(entry: Any) -> Any:
    values = normalized_values(entry)
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    return values


def quality_item(study: dict[str, Any], item: str) -> dict[str, Any]:
    q_entry = (study.get("quality_checklist") or {}).get(item)
    summary_entry = (study.get("structured_code_summary") or {}).get(f"quality_checklist.{item}")

    rating = None
    score = None
    rationale = None
    confidence = None

    if isinstance(q_entry, dict):
        rating = first_nonempty(q_entry.get("rating"), q_entry.get("value"))
        if rating is None and q_entry.get("values"):
            rating = q_entry.get("values")[0]
        if q_entry.get("numeric_score") is not None:
            score = q_entry.get("numeric_score")
        elif q_entry.get("score") is not None:
            score = q_entry.get("score")
        rationale = q_entry.get("rationale")
        confidence = q_entry.get("confidence")

    if rating is None and isinstance(summary_entry, dict):
        values = summary_entry.get("values") or []
        if values:
            rating = values[0]
        rationale = rationale or summary_entry.get("rationale")
        confidence = confidence or summary_entry.get("confidence")

    if score is None and rating is not None:
        score = QUALITY_SCORE_BY_LABEL.get(str(rating).strip().lower(), 0.0)

    return {
        "rating": rating,
        "score": float(score or 0.0),
        "rationale": rationale,
        "confidence": confidence,
    }


def quality_summary(study: dict[str, Any]) -> dict[str, Any]:
    items = {item: quality_item(study, item) for item in QUALITY_ITEMS}
    total = sum(item["score"] for item in items.values())
    return {"items": items, "total": total}


def extraction_confidence(study: dict[str, Any]) -> Any:
    summary_entry = (study.get("structured_code_summary") or {}).get(
        "synthesis_consistency.extraction_confidence"
    )
    value = normalized_scalar(summary_entry)
    if value is not None:
        return value
    found, raw = get_nested(study.get("extraction") or {}, "synthesis_consistency.extraction_confidence")
    return normalized_scalar(raw) if found else None


def bibtex_field(bibtex: str | None, field: str) -> str | None:
    if not bibtex:
        return None
    match = re.search(rf"\b{re.escape(field)}\s*=\s*[{{\"]([^}}\"]+)[}}\"]", bibtex, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return clean_text(match.group(1))


def study_bibliographic(study: dict[str, Any]) -> dict[str, Any]:
    biblio = (study.get("extraction") or {}).get("bibliographic_review_management") or {}
    citation = biblio.get("citation") if isinstance(biblio.get("citation"), dict) else {}
    bibtex = study.get("bibtex")
    authors = biblio.get("authors") or citation.get("authors")
    if authors is None:
        bibtex_authors = bibtex_field(bibtex, "author")
        authors = [part.strip() for part in bibtex_authors.split(" and ")] if bibtex_authors else None
    return {
        "title": biblio.get("title") or citation.get("title") or bibtex_field(bibtex, "title"),
        "authors": authors,
        "venue": biblio.get("venue") or citation.get("venue") or bibtex_field(bibtex, "booktitle") or bibtex_field(bibtex, "journal"),
        "doi": biblio.get("doi_or_url") or biblio.get("doi") or citation.get("doi") or bibtex_field(bibtex, "doi") or citation.get("url"),
        "year": biblio.get("year") or citation.get("year") or bibtex_field(bibtex, "year"),
    }


def flatten_studies(
    studies: list[dict[str, Any]], generated_at: str | None, codebook_version: str | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    study_records: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []

    for study_index, study in enumerate(studies):
        study_id = study.get("corpus_id") or f"study-{study_index + 1:04d}"
        biblio = study_bibliographic(study)
        q_summary = quality_summary(study)
        confidence = extraction_confidence(study)

        record = {
            "study_id": study_id,
            "source_path": f"studies[{study_index}]",
            "year": study.get("year") or biblio.get("year"),
            "tier": study.get("tier"),
            "title": biblio.get("title"),
            "authors": biblio.get("authors"),
            "venue": biblio.get("venue"),
            "doi": biblio.get("doi"),
            "quality_score_total": q_summary["total"],
            "extraction_confidence": confidence,
            "source_generated_at": generated_at,
            "source_codebook_version": codebook_version,
        }
        study_records.append(record)

        quality_row = {
            "study_id": study_id,
            "year": record["year"],
            "tier": record["tier"],
            "title": record["title"],
            "quality_score_total": score_label(q_summary["total"]),
            "extraction_confidence": confidence,
        }
        for item in QUALITY_ITEMS:
            quality_row[f"{item}_rating"] = q_summary["items"][item]["rating"]
            quality_row[f"{item}_score"] = score_label(q_summary["items"][item]["score"])
        quality_rows.append(quality_row)

    return study_records, quality_rows


def structured_field_order(studies: list[dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for study in studies:
        for field_path in (study.get("structured_code_summary") or {}).keys():
            if field_path not in seen:
                seen.add(field_path)
                ordered.append(field_path)
    return ordered


def flatten_study_codes(
    studies: list[dict[str, Any]],
    field_order: list[str],
    generated_at: str | None,
    codebook_version: str | None,
    quote_collector: EvidenceQuoteCollector,
) -> tuple[list[dict[str, Any]], Counter[str], Counter[str]]:
    records: list[dict[str, Any]] = []
    missing_extraction_paths: Counter[str] = Counter()
    empty_value_paths: Counter[str] = Counter()

    for study_index, study in enumerate(studies):
        study_id = study.get("corpus_id") or f"study-{study_index + 1:04d}"
        code_seq = 0
        summary = study.get("structured_code_summary") or {}

        for field_path in field_order:
            if field_path not in summary:
                continue
            entry = summary.get(field_path)
            norm = normalize_code_entry(entry)
            values = norm["values"] or [None]
            if values == [None]:
                empty_value_paths[field_path] += 1
            source_path = f"studies[{study_index}].structured_code_summary.{field_path}"
            for value_index, value in enumerate(values, start=1):
                code_seq += 1
                code_id = f"{study_id}::code-{code_seq:04d}"
                record = {
                    "study_code_id": code_id,
                    "study_id": study_id,
                    "field_path": field_path,
                    "source_path": source_path,
                    "source_section": "structured_code_summary",
                    "value": canonical_value(value),
                    "value_index": value_index,
                    "status": norm["status"],
                    "rationale": clean_text(norm["rationale"]),
                    "evidence_quote": clean_text(norm["evidence_items"][0].get("quote"))
                    if norm["evidence_items"]
                    else None,
                    "confidence": norm["confidence"],
                    "source_generated_at": generated_at,
                    "source_codebook_version": codebook_version,
                }
                records.append(record)
                quote_collector.add_many(
                    norm["evidence_items"],
                    study_id=study_id,
                    field_path=field_path,
                    source_path=source_path,
                    coded_value=value,
                    parent_record_type="study_code",
                    parent_record_id=code_id,
                )

        extraction = study.get("extraction") or {}
        for field_path in field_order:
            if field_path.startswith("quality_checklist."):
                continue
            if field_path.startswith("claimed_outcomes_value_mechanisms_evidence[]"):
                continue
            found, entry = get_nested(extraction, field_path)
            if not found:
                missing_extraction_paths[field_path] += 1
                continue
            norm = normalize_code_entry(entry)
            values = norm["values"] or [None]
            if values == [None]:
                empty_value_paths[f"extraction.{field_path}"] += 1
            source_path = f"studies[{study_index}].extraction.{field_path}"
            for value_index, value in enumerate(values, start=1):
                code_seq += 1
                code_id = f"{study_id}::code-{code_seq:04d}"
                record = {
                    "study_code_id": code_id,
                    "study_id": study_id,
                    "field_path": field_path,
                    "source_path": source_path,
                    "source_section": "extraction",
                    "value": canonical_value(value),
                    "value_index": value_index,
                    "status": norm["status"],
                    "rationale": clean_text(norm["rationale"]),
                    "evidence_quote": clean_text(norm["evidence_items"][0].get("quote"))
                    if norm["evidence_items"]
                    else None,
                    "confidence": norm["confidence"],
                    "source_generated_at": generated_at,
                    "source_codebook_version": codebook_version,
                }
                records.append(record)
                quote_collector.add_many(
                    norm["evidence_items"],
                    study_id=study_id,
                    field_path=field_path,
                    source_path=source_path,
                    coded_value=value,
                    parent_record_type="study_code",
                    parent_record_id=code_id,
                )

    return records, missing_extraction_paths, empty_value_paths


def claim_text(claim: dict[str, Any]) -> Any:
    return first_nonempty(
        claim.get("claim_text"),
        claim.get("claim_text_or_paraphrase"),
        claim.get("claim"),
        claim.get("quote"),
    )


def claim_metric(claim: dict[str, Any]) -> list[Any]:
    values = normalized_values(claim.get("metric_or_value_indicator"))
    if values:
        return values
    for key in (
        "metric",
        "metric_other_label",
        "other_metric_label",
        "other_metric_or_value_indicator",
        "metric_or_value_indicator_other",
    ):
        value = claim.get(key)
        if value:
            return normalized_values(value)
    return []


def flatten_claims(
    studies: list[dict[str, Any]],
    generated_at: str | None,
    codebook_version: str | None,
    quote_collector: EvidenceQuoteCollector,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for study_index, study in enumerate(studies):
        study_id = study.get("corpus_id") or f"study-{study_index + 1:04d}"
        claims = (
            (study.get("extraction") or {}).get("claimed_outcomes_value_mechanisms_evidence")
            or []
        )
        for claim_index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                claim = {"claim_text": claim}
            claim_id = f"{study_id}::claim-{claim_index + 1:02d}"
            source_path = (
                f"studies[{study_index}].extraction."
                f"claimed_outcomes_value_mechanisms_evidence[{claim_index}]"
            )
            field_path = "claimed_outcomes_value_mechanisms_evidence[]"
            record = {
                "claim_id": claim_id,
                "study_id": study_id,
                "source_claim_id": claim.get("claim_id") or claim.get("id"),
                "field_path": field_path,
                "source_path": source_path,
                "claim_text": clean_text(claim_text(claim)),
                "outcome_category": normalized_values(
                    first_nonempty(claim.get("outcome_category"), claim.get("category"))
                ),
                "specificity": normalized_scalar(claim.get("specificity_of_claim")),
                "mbse_mechanism": normalized_values(
                    first_nonempty(claim.get("mbse_mechanism"), claim.get("mechanism"))
                ),
                "lifecycle_stage": normalized_values(claim.get("lifecycle_stage")),
                "evidence_type": normalized_values(claim.get("evidence_type")),
                "metric": claim_metric(claim),
                "baseline": normalized_scalar(
                    first_nonempty(claim.get("baseline_comparator"), claim.get("baseline"))
                ),
                "observed_effect": clean_text(
                    first_nonempty(
                        claim.get("observed_effect"),
                        claim.get("observed_effect_or_value"),
                        claim.get("observed_effect_or_qualitative_effect"),
                        claim.get("observed_effect_size_or_qualitative_effect"),
                        claim.get("observed_effect_or_effect_size"),
                        claim.get("effect"),
                    )
                ),
                "evidence_confidence": normalized_scalar(claim.get("evidence_confidence_rating")),
                "reliability_subtype": normalized_values(claim.get("reliability_subtype")),
                "metric_detail": clean_text(
                    first_nonempty(
                        claim.get("metric_detail"),
                        claim.get("metric_or_value_indicator_detail"),
                        claim.get("metric_or_value_indicator_details"),
                    )
                ),
                "linked_artifact_or_process": clean_text(
                    first_nonempty(
                        claim.get("linked_artifact_or_process"),
                        claim.get("linked_artifact_process"),
                        claim.get("artifact_process_linked"),
                        claim.get("artifact_or_process_linked"),
                        claim.get("artifact_process_linked_to_claim"),
                        claim.get("artifact_or_process_linked_to_claim"),
                    )
                ),
                "quote_location": claim.get("quote_location"),
                "threats_alternative_explanations": claim.get("threats_alternative_explanations")
                or claim.get("threats_or_alternative_explanations"),
                "confidence": first_nonempty(
                    claim.get("confidence"), claim.get("extractor_confidence"), claim.get("extraction_confidence")
                ),
                "source_generated_at": generated_at,
                "source_codebook_version": codebook_version,
            }
            records.append(record)
            quote_collector.add_many(
                extract_quote_items(claim),
                study_id=study_id,
                field_path=field_path,
                source_path=source_path,
                coded_value=record["claim_text"],
                parent_record_type="claim",
                parent_record_id=claim_id,
                claim_id=claim_id,
            )

    return records


def flatten_limitations(
    studies: list[dict[str, Any]],
    generated_at: str | None,
    codebook_version: str | None,
    quote_collector: EvidenceQuoteCollector,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for study_index, study in enumerate(studies):
        study_id = study.get("corpus_id") or f"study-{study_index + 1:04d}"
        limitations = study.get("structured_limitations") or {}
        flags = list(limitations.get("limitation_flags") or [])
        assessments = limitations.get("limitation_assessments") or []
        assessment_flags: set[str] = set()
        seq = 0

        for assessment_index, assessment in enumerate(assessments):
            if not isinstance(assessment, dict):
                assessment = {"flag": assessment}
            seq += 1
            limitation_id = f"{study_id}::limitation-{seq:02d}"
            flag = assessment.get("flag") or assessment.get("label")
            if flag:
                assessment_flags.add(flag)
            source_path = (
                f"studies[{study_index}].structured_limitations."
                f"limitation_assessments[{assessment_index}]"
            )
            record = {
                "limitation_id": limitation_id,
                "study_id": study_id,
                "field_path": "structured_limitations.limitation_assessments[]",
                "source_path": source_path,
                "limitation_type": "controlled_flag",
                "flag": flag,
                "source": assessment.get("source"),
                "assessment": assessment.get("assessment") or "limitation_present",
                "rationale": clean_text(assessment.get("rationale")),
                "evidence_quote": clean_text(assessment.get("evidence_quote")),
                "confidence": assessment.get("confidence"),
                "source_generated_at": generated_at,
                "source_codebook_version": codebook_version,
            }
            records.append(record)
            quote_collector.add_many(
                extract_quote_items(assessment),
                study_id=study_id,
                field_path=record["field_path"],
                source_path=source_path,
                coded_value=flag,
                parent_record_type="limitation",
                parent_record_id=limitation_id,
            )

        for flag in flags:
            if flag in assessment_flags:
                continue
            seq += 1
            limitation_id = f"{study_id}::limitation-{seq:02d}"
            source_path = f"studies[{study_index}].structured_limitations.limitation_flags"
            records.append(
                {
                    "limitation_id": limitation_id,
                    "study_id": study_id,
                    "field_path": "structured_limitations.limitation_flags",
                    "source_path": source_path,
                    "limitation_type": "controlled_flag",
                    "flag": flag,
                    "source": None,
                    "assessment": "flag_present_no_assessment_record",
                    "rationale": None,
                    "evidence_quote": None,
                    "confidence": None,
                    "source_generated_at": generated_at,
                    "source_codebook_version": codebook_version,
                }
            )

        for emergent_index, emergent in enumerate(limitations.get("emergent_limitations") or []):
            if not isinstance(emergent, dict):
                emergent = {"label": emergent}
            seq += 1
            limitation_id = f"{study_id}::limitation-{seq:02d}"
            source_path = (
                f"studies[{study_index}].structured_limitations."
                f"emergent_limitations[{emergent_index}]"
            )
            record = {
                "limitation_id": limitation_id,
                "study_id": study_id,
                "field_path": "structured_limitations.emergent_limitations[]",
                "source_path": source_path,
                "limitation_type": "emergent_limitation",
                "flag": emergent.get("label"),
                "source": emergent.get("source"),
                "assessment": "emergent_limitation",
                "rationale": clean_text(emergent.get("rationale")),
                "evidence_quote": clean_text(emergent.get("evidence_quote")),
                "confidence": emergent.get("confidence"),
                "source_generated_at": generated_at,
                "source_codebook_version": codebook_version,
            }
            records.append(record)
            quote_collector.add_many(
                extract_quote_items(emergent),
                study_id=study_id,
                field_path=record["field_path"],
                source_path=source_path,
                coded_value=record["flag"],
                parent_record_type="limitation",
                parent_record_id=limitation_id,
            )

    return records


def flatten_emergent_codes(
    studies: list[dict[str, Any]],
    generated_at: str | None,
    codebook_version: str | None,
    quote_collector: EvidenceQuoteCollector,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for study_index, study in enumerate(studies):
        study_id = study.get("corpus_id") or f"study-{study_index + 1:04d}"
        for code_index, code in enumerate(study.get("emergent_codes") or []):
            if not isinstance(code, dict):
                code = {"label": code}
            emergent_code_id = f"{study_id}::emergent-{code_index + 1:02d}"
            source_path = f"studies[{study_index}].emergent_codes[{code_index}]"
            record = {
                "emergent_code_id": emergent_code_id,
                "study_id": study_id,
                "field_path": code.get("field_path"),
                "source_path": source_path,
                "label": code.get("label"),
                "description": clean_text(code.get("description")),
                "rationale": clean_text(code.get("rationale")),
                "evidence_quote": clean_text(code.get("evidence_quote")),
                "confidence": code.get("confidence"),
                "original_label": code.get("original_label"),
                "category": code.get("category"),
                "source_generated_at": generated_at,
                "source_codebook_version": codebook_version,
            }
            records.append(record)
            quote_collector.add_many(
                extract_quote_items(code),
                study_id=study_id,
                field_path=record["field_path"] or "emergent_codes[]",
                source_path=source_path,
                coded_value=record["label"],
                parent_record_type="emergent_code",
                parent_record_id=emergent_code_id,
            )

    return records


def flatten_gap_mappings(
    studies: list[dict[str, Any]],
    generated_at: str | None,
    codebook_version: str | None,
    quote_collector: EvidenceQuoteCollector,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for study_index, study in enumerate(studies):
        study_id = study.get("corpus_id") or f"study-{study_index + 1:04d}"
        gap_mapping = ((study.get("extraction") or {}).get("gap_mapping") or {})
        gap_items = [
            (gap, entry)
            for gap, entry in gap_mapping.items()
            if not gap.endswith("_rationale") and gap not in {"gap_mapping_notes", "gap_notes"}
        ]
        for gap_index, (gap, entry) in enumerate(gap_items):
            gap_id = f"{study_id}::gap-{gap_index + 1:02d}"
            source_path = f"studies[{study_index}].extraction.gap_mapping.{gap}"
            if isinstance(entry, dict):
                entry_values = entry.get("values") or []
                status_as_level = entry.get("status") if entry.get("status") not in {"coded", "not_reported", "not_applicable", "none", "uncertain"} else None
                level = first_nonempty(
                    entry.get("classification"),
                    entry.get("rating"),
                    entry.get("mapping"),
                    entry.get("level"),
                    entry.get("value"),
                    entry_values[0] if entry_values else None,
                    status_as_level,
                )
                rationale = entry.get("rationale")
                evidence_quote = entry.get("evidence_quote")
                confidence = entry.get("confidence")
            else:
                level = entry
                rationale = gap_mapping.get(f"{gap}_rationale")
                evidence_quote = None
                confidence = None
            record = {
                "gap_mapping_id": gap_id,
                "study_id": study_id,
                "field_path": f"gap_mapping.{gap}",
                "source_path": source_path,
                "gap": gap,
                "level": canonical_value(level),
                "rationale": clean_text(rationale),
                "evidence_quote": clean_text(evidence_quote),
                "confidence": confidence,
                "source_generated_at": generated_at,
                "source_codebook_version": codebook_version,
            }
            records.append(record)
            quote_collector.add_many(
                extract_quote_items(entry),
                study_id=study_id,
                field_path=record["field_path"],
                source_path=source_path,
                coded_value=level,
                parent_record_type="gap_mapping",
                parent_record_id=gap_id,
            )

    return records


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def field_value_counts(study_codes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    values_per_study: defaultdict[tuple[str, str], defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for record in study_codes:
        value = record.get("value")
        value_text = csv_value(value)
        status = record.get("status") or ""
        key = (record.get("source_section") or "", record.get("field_path") or "", value_text, status)
        if key not in counts:
            counts[key] = {
                "source_section": key[0],
                "field_path": key[1],
                "value": key[2],
                "status": key[3],
                "record_count": 0,
                "study_ids": set(),
            }
        counts[key]["record_count"] += 1
        counts[key]["study_ids"].add(record.get("study_id"))
        if value_text:
            values_per_study[(record.get("source_section") or "", record.get("field_path") or "")][
                record.get("study_id")
            ] += 1

    multivalue_info = {
        key: sum(1 for value_count in by_study.values() if value_count > 1)
        for key, by_study in values_per_study.items()
    }

    rows: list[dict[str, Any]] = []
    for key in sorted(counts):
        entry = counts[key]
        study_ids = sorted(s for s in entry["study_ids"] if s)
        rows.append(
            {
                "source_section": entry["source_section"],
                "field_path": entry["field_path"],
                "value": entry["value"],
                "status": entry["status"],
                "record_count": entry["record_count"],
                "study_count": len(study_ids),
                "studies_with_multiple_values_for_field": multivalue_info.get(
                    (entry["source_section"], entry["field_path"]), 0
                ),
                "is_multi_valued_field": "yes"
                if multivalue_info.get((entry["source_section"], entry["field_path"]), 0) > 0
                else "no",
                "example_study_ids": ";".join(study_ids[:8]),
            }
        )
    return rows


def count_structured_field(studies: list[dict[str, Any]], field_path: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for study in studies:
        entry = (study.get("structured_code_summary") or {}).get(field_path)
        for value in normalized_values(entry):
            counter[str(value)] += 1
    return counter


def count_limitation_flags(studies: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for study in studies:
        counter.update((study.get("structured_limitations") or {}).get("limitation_flags") or [])
    return counter


def count_gap_levels(gap_records: list[dict[str, Any]], gap_field_path: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    gap_name = gap_field_path.split(".", 1)[1]
    for record in gap_records:
        if record.get("gap") == gap_name and record.get("level") not in (None, ""):
            counter[str(record.get("level"))] += 1
    return counter


def counter_matches(left: Counter[str] | dict[str, int], right: Counter[str] | dict[str, int]) -> bool:
    return dict(left) == dict(right)


def compact_counter(counter: Counter[str] | dict[str, int]) -> str:
    if not counter:
        return "{}"
    return ", ".join(f"{key}: {counter[key]}" for key in sorted(counter))


def compare_statistics(
    data: dict[str, Any],
    studies: list[dict[str, Any]],
    study_records: list[dict[str, Any]],
    gap_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    stats = data.get("statistics") or {}
    rows: list[dict[str, Any]] = []

    def add(name: str, source_counts: dict[str, int], generated_counts: Counter[str], note: str = "") -> None:
        rows.append(
            {
                "statistic": name,
                "matches": counter_matches(source_counts, generated_counts),
                "source": compact_counter(source_counts),
                "generated": compact_counter(generated_counts),
                "note": note,
            }
        )

    add("tier_counts", stats.get("tier_counts", {}), Counter(r.get("tier") for r in study_records))

    quality_counts = Counter(score_label(float(r.get("quality_score_total") or 0.0)) for r in study_records)
    source_quality_counts = (stats.get("quality_score_total") or {}).get("counts", {})
    quality_note = "Computed from per-study quality_checklist/structured quality fields."
    if not counter_matches(source_quality_counts, quality_counts):
        source_quality = stats.get("quality_score_total") or {}
        quality_note += (
            " Source statistics quality aggregate differs from per-study extraction fields "
            f"(source min/mean/max={source_quality.get('min')}/"
            f"{source_quality.get('mean')}/{source_quality.get('max')}; generated "
            f"min/mean/max={min(float(r.get('quality_score_total') or 0.0) for r in study_records):.1f}/"
            f"{mean(float(r.get('quality_score_total') or 0.0) for r in study_records):.4f}/"
            f"{max(float(r.get('quality_score_total') or 0.0) for r in study_records):.1f})."
        )
    add("quality_score_total.counts", source_quality_counts, quality_counts, quality_note)

    rq_stats = stats.get("rq_relevance_counts") or {}
    for rq, field_path in [
        ("RQ1", "bibliographic_review_management.rq1_relevance"),
        ("RQ2", "bibliographic_review_management.rq2_relevance"),
        ("RQ3", "bibliographic_review_management.rq3_relevance"),
    ]:
        add(
            f"rq_relevance_counts.{rq}",
            rq_stats.get(rq, {}),
            count_structured_field(studies, field_path),
        )

    for stat_key, field_path in STAT_FIELD_MAP.items():
        add(stat_key, stats.get(stat_key, {}), count_structured_field(studies, field_path))

    add("limitation_flag_counts", stats.get("limitation_flag_counts", {}), count_limitation_flags(studies))

    for gap_field_path, source_counts in (stats.get("gap_mapping_counts") or {}).items():
        add(gap_field_path, source_counts, count_gap_levels(gap_records, gap_field_path))

    return rows


def multi_valued_code_fields(study_codes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_field_study: defaultdict[tuple[str, str], defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    total_values: Counter[tuple[str, str]] = Counter()
    for record in study_codes:
        if record.get("value") in (None, ""):
            continue
        key = (record.get("source_section") or "", record.get("field_path") or "")
        by_field_study[key][record.get("study_id")] += 1
        total_values[key] += 1

    rows: list[dict[str, Any]] = []
    for key, study_counts in by_field_study.items():
        multi_studies = [study for study, count in study_counts.items() if count > 1]
        if not multi_studies:
            continue
        rows.append(
            {
                "source_section": key[0],
                "field_path": key[1],
                "studies_with_multiple_values": len(multi_studies),
                "max_values_in_one_study": max(study_counts.values()),
                "total_values": total_values[key],
                "example_study_ids": ";".join(sorted(multi_studies)[:8]),
            }
        )
    rows.sort(
        key=lambda row: (
            row["source_section"] != "structured_code_summary",
            row["field_path"],
        )
    )
    return rows


def multi_valued_claim_fields(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in sorted(CLAIM_LIST_FIELDS):
        claim_count = 0
        study_ids: set[str] = set()
        max_values = 0
        total_values = 0
        for claim in claims:
            values = claim.get(field)
            if not isinstance(values, list):
                continue
            max_values = max(max_values, len(values))
            total_values += len(values)
            if len(values) > 1:
                claim_count += 1
                study_ids.add(claim.get("study_id"))
        if claim_count:
            rows.append(
                {
                    "field_path": f"claimed_outcomes_value_mechanisms_evidence[].{field}",
                    "claims_with_multiple_values": claim_count,
                    "studies_with_multiple_values": len(study_ids),
                    "max_values_in_one_claim": max_values,
                    "total_values": total_values,
                    "example_study_ids": ";".join(sorted(study_ids)[:8]),
                }
            )
    return rows


def section_audit(studies: list[dict[str, Any]]) -> dict[str, Any]:
    missing: Counter[str] = Counter()
    unexpected: Counter[str] = Counter()
    expected = set(EXPECTED_EXTRACTION_SECTIONS)
    for study in studies:
        keys = set((study.get("extraction") or {}).keys())
        for section in expected - keys:
            missing[section] += 1
        for section in keys - expected:
            unexpected[section] += 1
    return {"missing": missing, "unexpected": unexpected}


def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return lines


def write_report(
    path: Path,
    *,
    data: dict[str, Any],
    study_records: list[dict[str, Any]],
    study_codes: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    limitations: list[dict[str, Any]],
    emergent_codes: list[dict[str, Any]],
    evidence_quotes: list[dict[str, Any]],
    gap_mappings: list[dict[str, Any]],
    stats_rows: list[dict[str, Any]],
    multi_code_rows: list[dict[str, Any]],
    multi_claim_rows: list[dict[str, Any]],
    section_info: dict[str, Any],
    missing_extraction_paths: Counter[str],
    empty_value_paths: Counter[str],
) -> None:
    source_study_count = data.get("study_count")
    observed_source_count = len(data.get("studies") or [])
    output_study_count = len(study_records)
    all_stats_match = all(row["matches"] for row in stats_rows)

    lines: list[str] = []
    lines.append("# E0 data audit — SLR1 extraction flattening")
    lines.append("")
    lines.append(f"Source generated_at: `{data.get('generated_at')}`")
    lines.append(f"Source codebook_version: `{data.get('codebook_version')}`")
    lines.append("")
    lines.append("## Study preservation")
    lines.append("")
    lines.append(
        f"Flattening preserved all studies: **{'yes' if output_study_count == observed_source_count == source_study_count else 'no'}**. "
        f"The source reports `{source_study_count}` studies, contains `{observed_source_count}` study objects, "
        f"and `data/studies.jsonl` contains `{output_study_count}` records."
    )
    lines.append("")
    lines.append("## Generated row counts")
    lines.append("")
    lines.extend(
        markdown_table(
            ["Artifact", "Rows"],
            [
                ["studies.jsonl", len(study_records)],
                ["study_codes.jsonl", len(study_codes)],
                ["claims.jsonl", len(claims)],
                ["limitations.jsonl", len(limitations)],
                ["emergent_codes.jsonl", len(emergent_codes)],
                ["evidence_quotes.jsonl", len(evidence_quotes)],
                ["gap_mappings.jsonl", len(gap_mappings)],
            ],
        )
    )
    lines.append("")
    lines.append("## Source statistics comparison")
    lines.append("")
    lines.append(
        "Counts are regenerated from normalized per-study fields. Empty `values: []` records are retained in JSONL "
        "for provenance but excluded from controlled-value count comparisons."
    )
    lines.append("")
    comparison_rows = [
        [
            row["statistic"],
            "yes" if row["matches"] else "no",
            row["source"],
            row["generated"],
            row["note"],
        ]
        for row in stats_rows
    ]
    lines.extend(markdown_table(["Statistic", "Matches", "Source", "Generated", "Notes"], comparison_rows))
    lines.append("")
    if all_stats_match:
        lines.append("All regenerated aggregate counts match the source `statistics` object.")
    else:
        mismatch_names = ", ".join(row["statistic"] for row in stats_rows if not row["matches"])
        lines.append(
            "Differences are limited to the following aggregate(s): "
            f"{mismatch_names}. See notes above for the explanation."
        )
    lines.append("")
    lines.append("## Multi-valued fields requiring many-to-many graph edges")
    lines.append("")
    if multi_code_rows:
        lines.append("### Study-level code fields")
        lines.append("")
        lines.extend(
            markdown_table(
                [
                    "Source",
                    "Field path",
                    "Studies with >1 value",
                    "Max values/study",
                    "Total values",
                    "Examples",
                ],
                [
                    [
                        row["source_section"],
                        row["field_path"],
                        row["studies_with_multiple_values"],
                        row["max_values_in_one_study"],
                        row["total_values"],
                        row["example_study_ids"],
                    ]
                    for row in multi_code_rows
                ],
            )
        )
    else:
        lines.append("No multi-valued study-code fields were found.")
    lines.append("")
    if multi_claim_rows:
        lines.append("### Claim-level fields")
        lines.append("")
        lines.extend(
            markdown_table(
                [
                    "Field path",
                    "Claims with >1 value",
                    "Studies represented",
                    "Max values/claim",
                    "Total values",
                    "Examples",
                ],
                [
                    [
                        row["field_path"],
                        row["claims_with_multiple_values"],
                        row["studies_with_multiple_values"],
                        row["max_values_in_one_claim"],
                        row["total_values"],
                        row["example_study_ids"],
                    ]
                    for row in multi_claim_rows
                ],
            )
        )
    lines.append("")
    lines.append("## Missing and unexpected sections")
    lines.append("")
    missing_sections = section_info["missing"]
    unexpected_sections = section_info["unexpected"]
    if not missing_sections and not unexpected_sections:
        lines.append("All expected top-level `extraction.*` sections were present, and no unexpected top-level sections were encountered.")
    else:
        if missing_sections:
            lines.append("Missing expected top-level sections:")
            for section, count in sorted(missing_sections.items()):
                lines.append(f"- `{section}` missing in {count} studies")
        if unexpected_sections:
            lines.append("Unexpected top-level sections:")
            for section, count in sorted(unexpected_sections.items()):
                lines.append(f"- `{section}` present in {count} studies")
    lines.append("")
    lines.append(
        f"Structured controlled-field keys observed: `{len(structured_field_order(data.get('studies') or []))}` "
        f"(source controlled_field_count: `{data.get('controlled_field_count')}`)."
    )
    if missing_extraction_paths:
        lines.append("")
        lines.append(
            "Some exact controlled field paths were absent from nested `extraction.*` sections even though the "
            "normalized `structured_code_summary` contained them. Top missing exact paths:"
        )
        for field_path, count in missing_extraction_paths.most_common(12):
            lines.append(f"- `{field_path}` missing in {count} studies")
    if empty_value_paths:
        lines.append("")
        lines.append("Controlled fields with explicit empty values/statuses were retained as provenance rows. Top empty-value paths:")
        for field_path, count in empty_value_paths.most_common(12):
            lines.append(f"- `{field_path}` empty in {count} records")
    lines.append("")
    lines.append("## Caveats for downstream KG work")
    lines.append("")
    lines.append(
        "- `study_codes.jsonl` includes both canonical `structured_code_summary` records and exact-path `extraction` records; "
        "use `source_section` to avoid double-counting."
    )
    lines.append(
        "- Claim fields remain arrays where the extraction is multi-valued, so KG builders should explode those arrays into "
        "many-to-many edges."
    )
    lines.append(
        "- The source `statistics.quality_score_total` aggregate does not match the per-study quality fields; this audit preserves "
        "the per-study judgments and reports the mismatch rather than editing the source extraction."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    default_base = script_dir.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=default_base.parent / "extraction.json",
        help="Path to SLR1 extraction.json (default: ../extraction.json relative to kge-experiments).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent
    source_path = args.source.resolve()

    data_dir = base_dir / "data"
    tables_dir = base_dir / "outputs" / "tables"
    reports_dir = base_dir / "outputs" / "reports"
    for directory in (data_dir, tables_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    with source_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    studies = data.get("studies") or []
    generated_at = data.get("generated_at")
    codebook_version = data.get("codebook_version")

    quote_collector = EvidenceQuoteCollector(generated_at, codebook_version)
    field_order = structured_field_order(studies)

    study_records, quality_rows = flatten_studies(studies, generated_at, codebook_version)
    study_codes, missing_extraction_paths, empty_value_paths = flatten_study_codes(
        studies, field_order, generated_at, codebook_version, quote_collector
    )
    claims = flatten_claims(studies, generated_at, codebook_version, quote_collector)
    limitations = flatten_limitations(studies, generated_at, codebook_version, quote_collector)
    emergent_codes = flatten_emergent_codes(studies, generated_at, codebook_version, quote_collector)
    gap_mappings = flatten_gap_mappings(studies, generated_at, codebook_version, quote_collector)
    evidence_quotes = quote_collector.records

    write_jsonl(data_dir / "studies.jsonl", study_records)
    write_jsonl(data_dir / "study_codes.jsonl", study_codes)
    write_jsonl(data_dir / "claims.jsonl", claims)
    write_jsonl(data_dir / "limitations.jsonl", limitations)
    write_jsonl(data_dir / "emergent_codes.jsonl", emergent_codes)
    write_jsonl(data_dir / "evidence_quotes.jsonl", evidence_quotes)
    write_jsonl(data_dir / "gap_mappings.jsonl", gap_mappings)

    field_count_rows = field_value_counts(study_codes)
    write_csv(
        tables_dir / "field_value_counts.csv",
        field_count_rows,
        [
            "source_section",
            "field_path",
            "value",
            "status",
            "record_count",
            "study_count",
            "studies_with_multiple_values_for_field",
            "is_multi_valued_field",
            "example_study_ids",
        ],
    )

    quality_fieldnames = [
        "study_id",
        "year",
        "tier",
        "title",
        "quality_score_total",
        "extraction_confidence",
    ]
    for item in QUALITY_ITEMS:
        quality_fieldnames.extend([f"{item}_rating", f"{item}_score"])
    write_csv(tables_dir / "study_quality_summary.csv", quality_rows, quality_fieldnames)

    stats_rows = compare_statistics(data, studies, study_records, gap_mappings)
    multi_code_rows = multi_valued_code_fields(study_codes)
    multi_claim_rows = multi_valued_claim_fields(claims)
    section_info = section_audit(studies)
    write_report(
        reports_dir / "e0_data_audit.md",
        data=data,
        study_records=study_records,
        study_codes=study_codes,
        claims=claims,
        limitations=limitations,
        emergent_codes=emergent_codes,
        evidence_quotes=evidence_quotes,
        gap_mappings=gap_mappings,
        stats_rows=stats_rows,
        multi_code_rows=multi_code_rows,
        multi_claim_rows=multi_claim_rows,
        section_info=section_info,
        missing_extraction_paths=missing_extraction_paths,
        empty_value_paths=empty_value_paths,
    )

    print(f"Flattened {len(study_records)} studies from {source_path}")
    print(f"Wrote JSONL data to {data_dir}")
    print(f"Wrote E0 tables/reports to {base_dir / 'outputs'}")


if __name__ == "__main__":
    main()
