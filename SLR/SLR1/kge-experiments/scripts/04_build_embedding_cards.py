#!/usr/bin/env python3
"""Build provenance-rich text cards for SLR1 embedding experiments.

The cards are deterministic text units over the ISSUE-001 flattened JSONL
outputs. They intentionally do not perform clustering, semantic graph creation,
or GraphRAG work; later issues consume these card artifacts.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from kg_common import (
    BASE_DIR,
    DATA_DIR,
    clean_text,
    dedupe_study_codes,
    ensure_dirs,
    ensure_issue001_outputs,
    load_jsonl,
    unique_preserve,
    values,
)


EMBEDDINGS_DIR = BASE_DIR / "embeddings"
CARD_BUILDER_VERSION = "embedding-cards-v1"

STUDY_CARD_FILE = "study_cards.jsonl"
CLAIM_CARD_FILE = "claim_cards.jsonl"
EVIDENCE_QUOTE_CARD_FILE = "evidence_quote_cards.jsonl"
EMERGENT_CODE_CARD_FILE = "emergent_code_cards.jsonl"
LIMITATION_CARD_FILE = "limitation_cards.jsonl"
GAP_MAPPING_CARD_FILE = "gap_mapping_cards.jsonl"
CARD_INDEX_FILE = "card_index.jsonl"

CARD_FILE_ORDER = [
    ("study_card", STUDY_CARD_FILE),
    ("claim_card", CLAIM_CARD_FILE),
    ("evidence_quote_card", EVIDENCE_QUOTE_CARD_FILE),
    ("emergent_code_card", EMERGENT_CODE_CARD_FILE),
    ("limitation_card", LIMITATION_CARD_FILE),
    ("gap_mapping_card", GAP_MAPPING_CARD_FILE),
]

FIELD_LABELS = {
    "bibliographic_review_management.rq1_relevance": "RQ1 relevance",
    "bibliographic_review_management.rq2_relevance": "RQ2 relevance",
    "bibliographic_review_management.rq3_relevance": "RQ3 relevance",
    "study_context_population.development_context": "development context",
    "study_context_population.eps_relevance": "EPS relevance",
    "study_context_population.lifecycle_stage_addressed": "lifecycle stage addressed",
    "study_context_population.model_maturity": "model maturity",
    "mbse_objective_scope_artifacts.modeling_scope": "modeling scope",
    "mbse_objective_scope_artifacts.model_artifacts_used": "model artifacts used",
    "mbse_objective_scope_artifacts.generality_reuse_mechanism": "generality/reuse mechanism",
    "implementation_pathway_tailoring.adoption_guidance": "adoption guidance",
    "implementation_pathway_tailoring.approach_classification": "approach classification",
    "implementation_pathway_tailoring.tailoring_rationale": "tailoring rationale",
    "toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool": "MBSE language/method/tool",
    "toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms": "interoperability mechanisms",
    "toolchain_interoperability_lifecycle_continuity.toolchain_limitations": "toolchain limitations",
    "eps_verification_specific.eps_elements_modeled": "EPS elements modeled",
    "eps_verification_specific.integration_test_readiness": "integration/test readiness",
    "eps_verification_specific.ivv_integration_level": "IV&V integration level",
    "eps_verification_specific.pre_physical_development_verification_mechanism": "pre-physical verification mechanism",
    "eps_verification_specific.verification_validation_artifacts": "verification/validation artifacts",
    "governance_roi_project_decision_linkage.model_governance_strategy": "model governance strategy",
    "governance_roi_project_decision_linkage.roi_value_realization_evidence": "ROI/value evidence",
}

STUDY_TEXT_GROUPS = [
    (
        "Context",
        [
            "study_context_population.development_context",
            "study_context_population.lifecycle_stage_addressed",
            "study_context_population.model_maturity",
            "implementation_pathway_tailoring.approach_classification",
            "bibliographic_review_management.rq1_relevance",
            "bibliographic_review_management.rq2_relevance",
            "bibliographic_review_management.rq3_relevance",
        ],
    ),
    (
        "Objective and MBSE scope",
        [
            "mbse_objective_scope_artifacts.modeling_scope",
            "mbse_objective_scope_artifacts.model_artifacts_used",
            "mbse_objective_scope_artifacts.generality_reuse_mechanism",
            "implementation_pathway_tailoring.tailoring_rationale",
            "implementation_pathway_tailoring.adoption_guidance",
        ],
    ),
    (
        "Toolchain and lifecycle continuity",
        [
            "toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool",
            "toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms",
            "toolchain_interoperability_lifecycle_continuity.toolchain_limitations",
        ],
    ),
    (
        "EPS verification summary",
        [
            "study_context_population.eps_relevance",
            "eps_verification_specific.eps_elements_modeled",
            "eps_verification_specific.verification_validation_artifacts",
            "eps_verification_specific.pre_physical_development_verification_mechanism",
            "eps_verification_specific.ivv_integration_level",
            "eps_verification_specific.integration_test_readiness",
        ],
    ),
    (
        "Governance and value evidence",
        [
            "governance_roi_project_decision_linkage.model_governance_strategy",
            "governance_roi_project_decision_linkage.roi_value_realization_evidence",
        ],
    ),
]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def text_value(value: Any) -> str | None:
    if isinstance(value, list):
        return join_text(value)
    return clean_text(value)


def join_text(items: Iterable[Any], sep: str = "; ") -> str:
    return sep.join(str(item) for item in unique_preserve(text for text in (clean_text(item) for item in items) if text))


def sentence(label: str, value: Any) -> str | None:
    text = text_value(value)
    if not text:
        return None
    return f"{label}: {text}."


def quoted_list(quotes: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for quote in quotes:
        text = clean_text(quote.get("evidence_quote"))
        if text:
            out.append(text)
    return unique_preserve(out)


def build_quote_indexes(evidence_quotes: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    by_claim: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_parent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_study: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for quote in evidence_quotes:
        if quote.get("claim_id"):
            by_claim[str(quote["claim_id"])].append(quote)
        if quote.get("parent_record_id"):
            by_parent[str(quote["parent_record_id"])].append(quote)
        if quote.get("study_id"):
            by_study[str(quote["study_id"])].append(quote)
    return {"by_claim": dict(by_claim), "by_parent": dict(by_parent), "by_study": dict(by_study)}


def study_field_index(study_codes: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in study_codes:
        study_id = clean_text(record.get("study_id"))
        field_path = clean_text(record.get("field_path"))
        value = clean_text(record.get("value"))
        if not study_id or not field_path or value is None:
            continue
        out[study_id][field_path].append(record)
    return {study_id: dict(fields) for study_id, fields in out.items()}


def values_for_field(field_records: dict[str, list[dict[str, Any]]], field_path: str) -> list[str]:
    return unique_preserve(
        value
        for value in (clean_text(record.get("value")) for record in field_records.get(field_path, []))
        if value
    )


def record_texts(record: dict[str, Any], *keys: str) -> list[str]:
    out: list[str] = []
    for key in keys:
        value = record.get(key)
        if isinstance(value, list):
            out.extend(text for text in (clean_text(item) for item in value) if text)
        else:
            text = clean_text(value)
            if text:
                out.append(text)
    return out


def field_summary(field_records: dict[str, list[dict[str, Any]]], field_path: str) -> dict[str, Any] | None:
    records = field_records.get(field_path, [])
    if not records:
        return None
    values_out = values_for_field(field_records, field_path)
    rationales = unique_preserve(
        text for text in (clean_text(record.get("rationale")) for record in records) if text
    )
    evidence_quotes = unique_preserve(
        text for text in (clean_text(record.get("evidence_quote")) for record in records) if text
    )
    source_paths = unique_preserve(
        text for record in records for text in record_texts(record, "source_path", "source_paths")
    )
    study_code_ids = unique_preserve(
        text for record in records for text in record_texts(record, "study_code_id", "study_code_ids")
    )
    source_sections = unique_preserve(
        text for record in records for text in record_texts(record, "source_section", "source_sections")
    )
    return {
        "field_path": field_path,
        "label": FIELD_LABELS.get(field_path, field_path),
        "values": values_out,
        "rationales": rationales,
        "evidence_quotes": evidence_quotes,
        "source_paths": source_paths,
        "study_code_ids": study_code_ids,
        "source_sections": source_sections,
    }


def format_field_line(field_records: dict[str, list[dict[str, Any]]], field_path: str) -> str | None:
    values_out = values_for_field(field_records, field_path)
    if not values_out:
        return None
    return f"{FIELD_LABELS.get(field_path, field_path)}: {join_text(values_out)}"


def format_group_section(
    field_records: dict[str, list[dict[str, Any]]], heading: str, field_paths: list[str]
) -> str | None:
    parts = [line for line in (format_field_line(field_records, path) for path in field_paths) if line]
    if not parts:
        return None
    return f"{heading}: " + ". ".join(parts) + "."


def claims_by_study(claims: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        out[str(claim["study_id"])].append(claim)
    return {study_id: sorted(rows, key=lambda row: str(row.get("claim_id"))) for study_id, rows in out.items()}


def claim_summary_line(claim: dict[str, Any]) -> str:
    parts = [clean_text(claim.get("claim_text")) or str(claim.get("claim_id"))]
    outcomes = join_text(values(claim.get("outcome_category")))
    mechanisms = join_text(values(claim.get("mbse_mechanism")))
    evidence = join_text(values(claim.get("evidence_type")))
    confidence = clean_text(claim.get("evidence_confidence"))
    if outcomes:
        parts.append(f"outcomes={outcomes}")
    if mechanisms:
        parts.append(f"mechanisms={mechanisms}")
    if evidence:
        parts.append(f"evidence_type={evidence}")
    if confidence:
        parts.append(f"confidence={confidence}")
    return f"{claim.get('claim_id')}: " + " | ".join(parts)


def base_card(
    *,
    card_id: str,
    unit_type: str,
    study_id: str,
    source_path: str | None,
    label: str | None,
    text: str,
    metadata: dict[str, Any],
    claim_id: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    card: dict[str, Any] = {
        "card_id": card_id,
        "unit_type": unit_type,
        "study_id": study_id,
        "source_path": source_path,
        "label": label or card_id,
        "text": clean_text(text) or "",
        "metadata": {
            "card_builder_version": CARD_BUILDER_VERSION,
            **metadata,
        },
    }
    if title is not None:
        card["title"] = title
    if claim_id is not None:
        card["claim_id"] = claim_id
    return card


def build_study_cards(
    studies: list[dict[str, Any]],
    study_codes: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fields_by_study = study_field_index(study_codes)
    claims_index = claims_by_study(claims)
    cards: list[dict[str, Any]] = []

    for study in studies:
        study_id = str(study["study_id"])
        field_records = fields_by_study.get(study_id, {})
        title = clean_text(study.get("title")) or study_id
        text_parts = [
            f"Study {study_id}: {title}.",
            sentence("Year", study.get("year")),
            sentence("Tier", study.get("tier")),
            sentence("Venue", study.get("venue")),
            sentence("Quality score total", study.get("quality_score_total")),
            sentence("Extraction confidence", study.get("extraction_confidence")),
        ]
        text_parts.extend(
            format_group_section(field_records, heading, field_paths)
            for heading, field_paths in STUDY_TEXT_GROUPS
        )
        claim_lines = [claim_summary_line(claim) for claim in claims_index.get(study_id, [])]
        if claim_lines:
            text_parts.append("Main findings and claims: " + " ".join(claim_lines) + ".")

        summaries = [
            summary
            for _, field_paths in STUDY_TEXT_GROUPS
            for summary in (field_summary(field_records, field_path) for field_path in field_paths)
            if summary
        ]
        metadata = {
            "source_record": study,
            "source_field_summaries": summaries,
            "claim_ids": [claim.get("claim_id") for claim in claims_index.get(study_id, [])],
        }
        cards.append(
            base_card(
                card_id=f"study_card::{study_id}",
                unit_type="study_card",
                study_id=study_id,
                source_path=clean_text(study.get("source_path")),
                title=title,
                label=title,
                text=" ".join(part for part in text_parts if part),
                metadata=metadata,
            )
        )
    return cards


def build_claim_cards(
    claims: list[dict[str, Any]], quote_indexes: dict[str, dict[str, list[dict[str, Any]]]]
) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    by_claim = quote_indexes["by_claim"]
    for claim in claims:
        claim_id = str(claim["claim_id"])
        study_id = str(claim["study_id"])
        quotes = by_claim.get(claim_id, [])
        exact_quotes = quoted_list(quotes)
        text_parts = [
            f"Claim {claim_id} from study {study_id}.",
            sentence("Claim text", claim.get("claim_text")),
            sentence("Outcome category", join_text(values(claim.get("outcome_category")))),
            sentence("Specificity", claim.get("specificity")),
            sentence("MBSE mechanism", join_text(values(claim.get("mbse_mechanism")))),
            sentence("Lifecycle stage", join_text(values(claim.get("lifecycle_stage")))),
            sentence("Evidence type", join_text(values(claim.get("evidence_type")))),
            sentence("Evidence confidence", claim.get("evidence_confidence")),
            sentence("Metric", join_text(values(claim.get("metric")))),
            sentence("Metric detail", claim.get("metric_detail")),
            sentence("Baseline", claim.get("baseline")),
            sentence("Observed effect", claim.get("observed_effect")),
            sentence("Reliability subtype", join_text(values(claim.get("reliability_subtype")))),
            sentence("Linked artifact/process", claim.get("linked_artifact_or_process")),
            sentence("Threats or alternative explanations", claim.get("threats_alternative_explanations")),
            sentence("Extractor confidence", claim.get("confidence")),
        ]
        if exact_quotes:
            text_parts.append("Evidence source exact quote(s): " + " | ".join(exact_quotes) + ".")
        metadata = {
            "source_record": claim,
            "linked_evidence_quote_ids": [quote.get("evidence_quote_id") for quote in quotes],
            "linked_evidence_quotes": exact_quotes,
        }
        label = clean_text(claim.get("claim_text")) or claim_id
        cards.append(
            base_card(
                card_id=f"claim_card::{claim_id}",
                unit_type="claim_card",
                study_id=study_id,
                claim_id=claim_id,
                source_path=clean_text(claim.get("source_path")),
                label=label,
                text=" ".join(part for part in text_parts if part),
                metadata=metadata,
            )
        )
    return cards


def build_evidence_quote_cards(evidence_quotes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for quote in evidence_quotes:
        quote_id = str(quote["evidence_quote_id"])
        study_id = str(quote["study_id"])
        claim_id = clean_text(quote.get("claim_id"))
        quote_text = clean_text(quote.get("evidence_quote")) or ""
        text_parts = [
            f"Evidence quote {quote_id} from study {study_id}.",
            f"Exact evidence quote: {quote_text}.",
            sentence("Field path", quote.get("field_path")),
            sentence("Coded value", quote.get("coded_value")),
            sentence("Parent record type", quote.get("parent_record_type")),
            sentence("Parent record id", quote.get("parent_record_id")),
            sentence("Claim id", claim_id),
            sentence("Location", quote.get("location")),
            sentence("Topic", quote.get("topic")),
        ]
        metadata = {"source_record": quote}
        cards.append(
            base_card(
                card_id=f"evidence_quote_card::{quote_id}",
                unit_type="evidence_quote_card",
                study_id=study_id,
                claim_id=claim_id,
                source_path=clean_text(quote.get("source_path")),
                label=quote_id,
                text=" ".join(part for part in text_parts if part),
                metadata=metadata,
            )
        )
    return cards


def build_emergent_code_cards(emergent_codes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for code in emergent_codes:
        code_id = str(code["emergent_code_id"])
        study_id = str(code["study_id"])
        label = clean_text(code.get("label")) or code_id
        text_parts = [
            f"Emergent code {code_id} from study {study_id}.",
            sentence("Label", label),
            sentence("Original label", code.get("original_label")),
            sentence("Category", code.get("category")),
            sentence("Field path", code.get("field_path")),
            sentence("Description", code.get("description")),
            sentence("Rationale", code.get("rationale")),
            sentence("Evidence quote", code.get("evidence_quote")),
            sentence("Confidence", code.get("confidence")),
        ]
        metadata = {"source_record": code}
        cards.append(
            base_card(
                card_id=f"emergent_code_card::{code_id}",
                unit_type="emergent_code_card",
                study_id=study_id,
                source_path=clean_text(code.get("source_path")),
                label=label,
                text=" ".join(part for part in text_parts if part),
                metadata=metadata,
            )
        )
    return cards


def build_limitation_cards(limitations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for limitation in limitations:
        limitation_id = str(limitation["limitation_id"])
        study_id = str(limitation["study_id"])
        label = clean_text(limitation.get("flag")) or limitation_id
        text_parts = [
            f"Limitation {limitation_id} from study {study_id}.",
            sentence("Flag", limitation.get("flag")),
            sentence("Assessment", limitation.get("assessment")),
            sentence("Source", limitation.get("source")),
            sentence("Limitation type", limitation.get("limitation_type")),
            sentence("Rationale", limitation.get("rationale")),
            sentence("Evidence quote", limitation.get("evidence_quote")),
            sentence("Confidence", limitation.get("confidence")),
        ]
        metadata = {"source_record": limitation}
        cards.append(
            base_card(
                card_id=f"limitation_card::{limitation_id}",
                unit_type="limitation_card",
                study_id=study_id,
                source_path=clean_text(limitation.get("source_path")),
                label=label,
                text=" ".join(part for part in text_parts if part),
                metadata=metadata,
            )
        )
    return cards


def build_gap_mapping_cards(
    gap_mappings: list[dict[str, Any]], quote_indexes: dict[str, dict[str, list[dict[str, Any]]]]
) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    by_parent = quote_indexes["by_parent"]
    for gap_mapping in gap_mappings:
        gap_mapping_id = str(gap_mapping["gap_mapping_id"])
        study_id = str(gap_mapping["study_id"])
        linked_quotes = by_parent.get(gap_mapping_id, [])
        quote_texts = quoted_list(linked_quotes)
        if clean_text(gap_mapping.get("evidence_quote")):
            quote_texts = unique_preserve([clean_text(gap_mapping.get("evidence_quote")), *quote_texts])
        label = clean_text(gap_mapping.get("gap")) or gap_mapping_id
        text_parts = [
            f"Gap mapping {gap_mapping_id} from study {study_id}.",
            sentence("Gap", gap_mapping.get("gap")),
            sentence("Addressing level", gap_mapping.get("level")),
            sentence("Rationale", gap_mapping.get("rationale")),
        ]
        if quote_texts:
            text_parts.append("Evidence quote: " + " | ".join(quote_texts) + ".")
        text_parts.extend(
            [
                sentence("Field path", gap_mapping.get("field_path")),
                sentence("Confidence", gap_mapping.get("confidence")),
            ]
        )
        metadata = {
            "source_record": gap_mapping,
            "linked_evidence_quote_ids": [quote.get("evidence_quote_id") for quote in linked_quotes],
            "linked_evidence_quotes": quote_texts,
        }
        cards.append(
            base_card(
                card_id=f"gap_mapping_card::{gap_mapping_id}",
                unit_type="gap_mapping_card",
                study_id=study_id,
                source_path=clean_text(gap_mapping.get("source_path")),
                label=label,
                text=" ".join(part for part in text_parts if part),
                metadata=metadata,
            )
        )
    return cards


def load_inputs() -> dict[str, list[dict[str, Any]]]:
    ensure_issue001_outputs()
    ensure_dirs(EMBEDDINGS_DIR)
    return {
        "studies": load_jsonl(DATA_DIR / "studies.jsonl"),
        "study_codes": dedupe_study_codes(load_jsonl(DATA_DIR / "study_codes.jsonl")),
        "claims": load_jsonl(DATA_DIR / "claims.jsonl"),
        "limitations": load_jsonl(DATA_DIR / "limitations.jsonl"),
        "emergent_codes": load_jsonl(DATA_DIR / "emergent_codes.jsonl"),
        "evidence_quotes": load_jsonl(DATA_DIR / "evidence_quotes.jsonl"),
        "gap_mappings": load_jsonl(DATA_DIR / "gap_mappings.jsonl"),
    }


def main() -> None:
    data = load_inputs()
    quote_indexes = build_quote_indexes(data["evidence_quotes"])
    cards_by_file = {
        STUDY_CARD_FILE: build_study_cards(data["studies"], data["study_codes"], data["claims"]),
        CLAIM_CARD_FILE: build_claim_cards(data["claims"], quote_indexes),
        EVIDENCE_QUOTE_CARD_FILE: build_evidence_quote_cards(data["evidence_quotes"]),
        EMERGENT_CODE_CARD_FILE: build_emergent_code_cards(data["emergent_codes"]),
        LIMITATION_CARD_FILE: build_limitation_cards(data["limitations"]),
        GAP_MAPPING_CARD_FILE: build_gap_mapping_cards(data["gap_mappings"], quote_indexes),
    }

    card_index: list[dict[str, Any]] = []
    for _, file_name in CARD_FILE_ORDER:
        card_index.extend(cards_by_file[file_name])
    for idx, card in enumerate(card_index):
        card["card_index"] = idx
        card["metadata"]["card_index"] = idx

    for _, file_name in CARD_FILE_ORDER:
        write_jsonl(EMBEDDINGS_DIR / file_name, cards_by_file[file_name])
    write_jsonl(EMBEDDINGS_DIR / CARD_INDEX_FILE, card_index)

    counts = Counter(card["unit_type"] for card in card_index)
    print(f"Built {len(card_index)} embedding cards in {EMBEDDINGS_DIR.relative_to(BASE_DIR)}")
    for unit_type in [unit_type for unit_type, _ in CARD_FILE_ORDER]:
        print(f"  {unit_type}: {counts.get(unit_type, 0)}")


if __name__ == "__main__":
    main()
