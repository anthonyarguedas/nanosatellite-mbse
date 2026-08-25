#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Regenerate S-D05 draft Wiley Anywhere cells from the v4 dictionary only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
CANDIDATE_TERMS = (
    "model-based engineering", "model based engineering", "model-driven engineering",
    "model driven engineering", "model-based design", "model based design",
    "model-driven design", "model driven design", "MBE", "MDE", "MBD",
    "digital thread", "digital threads", "digital twin", "digital twins",
    "MagicGrid", "Harmony-SE", "Harmony SE", "RFLP",
    "Cameo Systems Modeler", "MagicDraw", "IBM Engineering Systems Design Rhapsody",
    "Rational Rhapsody", "Vitech CORE", "Vitech GENESYS", "OpenMBEE",
    "Enterprise Architect", "MATLAB System Composer", "System Composer", "Modelio",
    "Cameo", "Rhapsody", "CORE", "GENESYS",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atom(term: str) -> str:
    if not isinstance(term, str) or not term:
        raise ValueError("dictionary term must be a nonempty string")
    return '"' + term.replace('"', '\\"') + '"'


def grouped(operator: str, values: list[str]) -> str:
    if not values:
        raise ValueError(f"empty {operator} group")
    return "(" + f" {operator} ".join(values) + ")"


def collect_concept_terms(concepts: dict[str, Any], concept_id: str) -> set[str]:
    concept = concepts[concept_id]
    kind = concept["kind"]
    if kind == "finite_terms":
        return set(concept["terms"])
    if kind == "union":
        return set().union(*(collect_concept_terms(concepts, child) for child in concept["members"]))
    if kind == "union_of_terms_and_pairs":
        values = set(concept["terms"])
        for pair in concept["pair_rules"]:
            values.update(pair["left"])
            values.update(pair["right"])
        return values
    if kind == "paired_terms":
        return set(concept["left"]) | set(concept["right"])
    raise ValueError(f"unsupported concept kind {kind}")


def pair_clauses(concept: dict[str, Any]) -> list[str]:
    if concept["kind"] == "union_of_terms_and_pairs":
        rules = concept["pair_rules"]
    elif concept["kind"] == "paired_terms":
        rules = [{"left": concept["left"], "right": concept["right"]}]
    else:
        return []
    clauses: list[str] = []
    for rule in rules:
        for left in rule["left"]:
            for right in rule["right"]:
                clauses.append(f"({atom(left)} AND {atom(right)})")
    if len(clauses) != len(set(clauses)):
        raise ValueError("dictionary pair rules generated duplicate source clauses")
    return clauses


def render_concept(concepts: dict[str, Any], concept_id: str) -> str:
    concept = concepts[concept_id]
    kind = concept["kind"]
    if kind == "finite_terms":
        return grouped("OR", [atom(term) for term in concept["terms"]])
    if kind == "union":
        return grouped("OR", [render_concept(concepts, child) for child in concept["members"]])
    if kind == "union_of_terms_and_pairs":
        values = [atom(term) for term in concept["terms"]]
        values.extend(pair_clauses(concept))
        return grouped("OR", values)
    if kind == "paired_terms":
        return grouped("OR", pair_clauses(concept))
    raise ValueError(f"unsupported concept kind {kind}")


def render_expression(concepts: dict[str, Any], expression: Any) -> str:
    if isinstance(expression, str):
        return render_concept(concepts, expression)
    if not isinstance(expression, dict) or expression.get("op") not in {"AND", "OR"}:
        raise ValueError("invalid direct-partition expression")
    return grouped(
        expression["op"],
        [render_expression(concepts, child) for child in expression["args"]],
    )


def expression_concepts(expression: Any) -> set[str]:
    if isinstance(expression, str):
        return {expression}
    values: set[str] = set()
    for child in expression["args"]:
        values.update(expression_concepts(child))
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictionary", required=True)
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--pilot-dir", required=True)
    parser.add_argument("--pilot-id", required=True)
    parser.add_argument("--protocol-commit", required=True)
    args = parser.parse_args()

    dictionary_path = Path(args.dictionary).resolve()
    source_root = Path(args.source_root).resolve()
    pilot_dir = Path(args.pilot_dir).resolve()
    queries_dir = source_root / "queries"
    specification_path = source_root / "translation-spec.json"
    audit_path = pilot_dir / "query-construction-audit.json"
    if specification_path.exists() or audit_path.exists():
        raise SystemExit("refusing to overwrite an existing specification or audit")
    dictionary = json.loads(dictionary_path.read_text(encoding="utf-8"))
    if dictionary.get("artifact_version") != "slr1-search-concepts/v4":
        raise SystemExit("the current dictionary is not v4")
    concepts = dictionary["concepts"]
    by_partition = {item["id"]: item for item in dictionary["direct_partitions"]}
    if tuple(by_partition) != PARTITIONS:
        raise SystemExit("the direct partition schedule does not match the required nine IDs")

    query_metadata: dict[str, dict[str, Any]] = {}
    audit_partitions: list[dict[str, Any]] = []
    for partition_id in PARTITIONS:
        partition = by_partition[partition_id]
        query = render_expression(concepts, partition["expression"]) + "\n"
        encoded = query.encode("utf-8")
        query_path = queries_dir / f"{partition_id}.wiley-allfield.txt"
        if query_path.exists() or query_path.is_symlink():
            raise SystemExit(f"refusing to overwrite {query_path}")
        query_path.write_bytes(encoded)

        used_concepts = expression_concepts(partition["expression"])
        expected_terms: set[str] = set()
        expected_pairs: list[str] = []
        for concept_id in used_concepts:
            expected_terms.update(collect_concept_terms(concepts, concept_id))
            expected_pairs.extend(pair_clauses(concepts[concept_id]))
        missing_terms = sorted(term for term in expected_terms if atom(term) not in query)
        repeated_terms = sorted(term for term in expected_terms if query.count(atom(term)) < 1)
        missing_pairs = sorted(clause for clause in expected_pairs if query.count(clause) != 1)
        candidate_hits = sorted(candidate for candidate in CANDIDATE_TERMS if atom(candidate) in query)
        terminal_lf = encoded.endswith(b"\n") and not encoded.endswith(b"\n\n")
        if missing_terms or repeated_terms or missing_pairs or candidate_hits or not terminal_lf:
            raise AssertionError(
                f"failed audit for {partition_id}: terms={missing_terms or repeated_terms}, "
                f"pairs={len(missing_pairs)}, candidate={candidate_hits}, terminal_lf={terminal_lf}"
            )
        query_metadata[partition_id] = {
            "file": f"queries/{query_path.name}",
            "sha256": sha256_bytes(encoded),
            "utf8_bytes_including_terminal_lf": len(encoded),
            "characters_including_terminal_lf": len(query),
            "term_atom_count": len(expected_terms),
            "pair_cross_product_clause_count": len(expected_pairs),
        }
        audit_partitions.append(
            {
                "partition_id": partition_id,
                "concept_ids": sorted(used_concepts),
                "expected_term_atom_count": len(expected_terms),
                "missing_terms": missing_terms,
                "pair_cross_product_clause_count": len(expected_pairs),
                "missing_or_nonunique_pair_clauses": missing_pairs,
                "candidate_terminology_hits": candidate_hits,
                "wildcard_present": "*" in query,
                "terminal_lf_only": terminal_lf,
                "sha256": sha256_bytes(encoded),
                "utf8_bytes_including_terminal_lf": len(encoded),
                "characters_including_terminal_lf": len(query),
            }
        )

    paired = {"BG1", "BG2", "BC1", "BT2"}
    specification = {
        "schema_version": "slr1-wiley-translation-spec/v1",
        "task_id": "S-D05",
        "source_id": "wiley-online-library",
        "source_name": "Wiley Online Library",
        "status": "draft_blocked_code_issue_no_live_validation",
        "protocol_commit": args.protocol_commit,
        "normative_provenance": {
            "dictionary_path": "SLR/SLR1/searches/search-concept-dictionary.json",
            "dictionary_artifact_version": dictionary["artifact_version"],
            "dictionary_sha256": sha256_bytes(dictionary_path.read_bytes()),
            "required_partition_ids": list(PARTITIONS),
            "candidate_terminology_policy": "S-C01 candidate terminology is non-normative and absent from every draft cell.",
        },
        "source_native_draft": {
            "field_scope": {
                "value": "One Wiley Anywhere/AllField row",
                "basis": "inferred_from_candidate_adapter_only",
                "acceptance_gate": "Final use is prohibited until the current visible Advanced Search field inventory, exact query echo/rewrite behavior, and one-field operand semantics are observed without an adapter defect.",
            },
            "term_rendering": "Every finite dictionary literal is preserved as one double-quoted atom; fully parenthesized AND/OR groups are unvalidated Wiley syntax candidates.",
            "phrase_policy": "Quoted multiword strings are draft ordered-phrase candidates only; phrase/token/punctuation/hyphen behavior is untested.",
            "wildcard": {"value": "not used", "basis": "observed_offline"},
            "acronym_boundary": {"value": "quoted literal only", "basis": "untested"},
            "case_stemming_lemmatization_expansion": {"value": "not established", "basis": "untested"},
            "parser_status": "No source query was submitted after the demonstrated normal-output no-clobber defect; AND/OR/NOT, precedence, phrase, punctuation, acronym, case, wildcard, expansion, proximity, length, fields, and echo/rewrite remain untested.",
        },
        "paired_term_handling": {
            "normative_requirement": "Every left/right pair is unordered, in one searchable field, with at most five intervening lexical tokens.",
            "draft_transport": "Every required left/right cross-product is rendered as a separate parenthesized Boolean conjunction, which is broader than the required proximity relation.",
            "acceptance_status": "blocked_final_use_prohibited",
            "why": "No current Wiley-native proximity operator, distance semantics, or same-field operand behavior was observed. An aggregate Anywhere route could cross underlying fields, so this draft cannot claim an exact or compliant same-field fallback.",
            "future_gate": "Validate a Wiley-native unordered <=5-token operator or document and prove a broader same-field construction that cannot lose an exact pair; apply the exact rule locally wherever retained fields permit.",
        },
        "controls": {
            "diagnostic_publication_date": {
                "lower_inclusive": "2011-01-01",
                "upper_inclusive": "2026-08-24",
                "upper_bound_label": "pilot execution-date diagnostic upper bound only; P-001 remains unresolved and this is not a final common cutoff",
                "validation_status": "offline_adapter_projection_only",
            },
            "language": {"native_english_filter": "not imposed", "basis": "untested"},
            "prohibited_limits": {
                "publication_type": "not imposed",
                "access": "not imposed",
                "peer_review": "not imposed",
                "venue": "not imposed",
                "content_type": "not imposed",
                "basis": "offline_planned",
            },
            "articles_and_chapters_vs_collections": "Both routes require separate live current-interface validation; collections must never be primary-evidence records.",
            "sort_page_size_date_precision": "unvalidated; the candidate adapter projects Earliest, fixed 20, month controls, and local exact-day disposition, but these claims are not source evidence.",
        },
        "controlled_vocabulary": {
            "status": "untested",
            "accepted_descriptors": [],
            "reason": "No current Advanced Search/indexed-term/hierarchy or suitable record descriptor surface was inspected after the terminal adapter safety defect.",
            "mandatory_rule": "Free text remains mandatory. Do not treat visible keywords or generic systems engineering as a controlled MBSE substitute.",
        },
        "query_length_and_cell_policy": {
            "observed_source_limit": None,
            "basis": "untested",
            "adapter_input_ceiling_characters": 50000,
            "adapter_ceiling_basis": "offline adapter validation only; it is not a Wiley source query-length limit",
            "current_cells": "One complete draft cell per partition. No semantic partition was split, wildcard-compressed, narrowed, or given source totals.",
            "future_split_rule": "Only after observing a source limit, prospectively map a lossless stable-ID union of complete source-native cells and reconcile each cell total and union before acceptance.",
        },
        "lossless_union_rule": {
            "identity": "Unvalidated; a later accepted Wiley record mode must establish a nonempty stable DOI or another documented stable identifier and reconcile complete ordered passes.",
            "failure": "Access, query, control, rewrite, total, page, export, identity, or completeness failure makes the source total null and imports no prefix.",
            "basis": "protocol_and_offline_draft",
        },
        "partitions": [],
        "evidence_links": [
            f"pilots/{args.pilot_id}/query-construction-audit.json",
            f"pilots/{args.pilot_id}/offline-adapter-safety-check.json",
        ],
    }
    for partition_id in PARTITIONS:
        partition = by_partition[partition_id]
        metadata = query_metadata[partition_id]
        specification["partitions"].append(
            {
                "partition_id": partition_id,
                "normative_expression": partition["expression"],
                "role": partition["role"],
                "stream": partition["stream"],
                "cell_ids": [f"WILEY-{partition_id}-C01"],
                "cells": [
                    {
                        "cell_id": f"WILEY-{partition_id}-C01",
                        "exact_query_file": metadata["file"],
                        "sha256": metadata["sha256"],
                        "utf8_bytes_including_terminal_lf": metadata["utf8_bytes_including_terminal_lf"],
                        "characters_including_terminal_lf": metadata["characters_including_terminal_lf"],
                        "query_status": (
                            "draft_pair_semantics_blocked_code_issue_no_source_submission"
                            if partition_id in paired
                            else "draft_parser_and_field_semantics_unvalidated_code_issue_no_source_submission"
                        ),
                        "source_reported_total": None,
                        "source_total_basis": "untested_no_live_submission",
                    }
                ],
                "lossless_union": {
                    "cell_count": 1,
                    "required": False,
                    "rationale": "One offline-generated cell retains the complete v4 Boolean tree; no source parser/length/field or stable-identity union behavior is claimed.",
                    "basis": "observed_offline",
                },
            }
        )

    audit = {
        "schema_version": "slr1-s-d05-query-construction-audit/v1",
        "pilot_id": args.pilot_id,
        "dictionary_artifact_version": dictionary["artifact_version"],
        "dictionary_sha256": sha256_bytes(dictionary_path.read_bytes()),
        "source_requests_made": 0,
        "renderer": {
            "all_finite_literals_explicit": True,
            "wildcard_compression_used": False,
            "candidate_terminology_added": False,
            "full_parentheses_are_unvalidated_source_syntax": True,
            "pair_cross_products_expanded": True,
            "pair_proximity_semantics_validated": False,
        },
        "partitions": audit_partitions,
        "result": "passed_offline_literal_and_structure_audit_only",
    }
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    specification_path.write_text(json.dumps(specification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
