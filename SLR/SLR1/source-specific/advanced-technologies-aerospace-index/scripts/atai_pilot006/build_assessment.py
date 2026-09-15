#!/usr/bin/env python3

"""Build the ATAI Pilot 006 field, pair, indexed-term, and language decisions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")
IF_PLAUSIBLE = {
    "2532106792",
    "3110282708",
    "3046967951",
    "3252320283",
    "3198981434",
    "3243962233",
}
IF_LIKELY_NOISE = {"3191429714", "3361937611", "3372652792"}
LANGUAGE_IDS = ["896198854", "2621176457"]


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def ids(artifact: dict[str, Any]) -> list[str]:
    return [str(record["paperId"]) for record in artifact.get("results", [])]


def tokens(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?", value.casefold())


def minimum_gap(text: str, left: str, right: str) -> int | None:
    sequence = tokens(text)
    a = tokens(left)
    b = tokens(right)
    a_positions = [i for i in range(len(sequence) - len(a) + 1) if sequence[i:i + len(a)] == a]
    b_positions = [i for i in range(len(sequence) - len(b) + 1) if sequence[i:i + len(b)] == b]
    gaps = []
    for i in a_positions:
        for j in b_positions:
            if i <= j:
                gap = j - (i + len(a))
            else:
                gap = i - (j + len(b))
            if gap >= 0:
                gaps.append(gap)
    return min(gaps) if gaps else None


def build(args: argparse.Namespace) -> dict[str, Any]:
    cells = args.pilot_root / "searches" / "cells"
    retry2 = args.pilot_root / "searches" / "retry2"
    retry3 = args.pilot_root / "searches" / "retry3"
    retry7 = args.pilot_root / "searches" / "retry7"

    field_pairs = []
    for name, expected_id in (
        ("title", "3371247439"),
        ("abstract", "3097792411"),
        ("subject", "3181339955"),
    ):
        explicit = load(cells / f"field-{name}-explicit.json")
        noft = load(cells / f"field-{name}-noft.json")
        if explicit.get("total") != 1 or noft.get("total") != 1 or ids(explicit) != [expected_id] or ids(noft) != [expected_id]:
            raise RuntimeError(f"{name} field contrast did not retain its known item.")
        field_pairs.append({
            "field": name,
            "explicit_total": 1,
            "noft_total": 1,
            "stable_id": expected_id,
            "same_stable_id": True,
            "explicit_artifact": f"cells/field-{name}-explicit.json",
            "noft_artifact": f"cells/field-{name}-noft.json",
        })

    index_totals = {}
    for pass_number in (1, 2):
        explicit = load(retry2 / f"field-index-explicit-no-date-count-pass{pass_number}.json")
        noft = load(retry2 / f"field-index-noft-no-date-count-pass{pass_number}.json")
        index_totals[f"pass_{pass_number}"] = {
            "IF_exact": explicit.get("total"),
            "NOFT": noft.get("total"),
        }
    if index_totals != {
        "pass_1": {"IF_exact": 1, "NOFT": 0},
        "pass_2": {"IF_exact": 1, "NOFT": 0},
    }:
        raise RuntimeError("Indexed-keyword known-item contrast changed.")

    pair_explicit = load(cells / "pair-abstract-explicit.json")
    pair_noft = load(cells / "pair-noft.json")
    cross = load(cells / "pair-cross-field-negative.json")
    pair_ids = ["1825532815", "2728408177"]
    if ids(pair_explicit) != pair_ids or ids(pair_noft) != pair_ids or cross.get("total") != 0:
        raise RuntimeError("Pair gate changed.")
    pair_local = []
    for record in pair_explicit["results"]:
        gap = minimum_gap(record["abstract"], "adapted", "model")
        if gap is None or gap > 5:
            raise RuntimeError(f"Pair-positive abstract lost its local pair: {record['paperId']}")
        pair_local.append({
            "paper_id": record["paperId"],
            "title": record["title"],
            "local_abstract_minimum_intervening_words": gap,
            "explicit_AB_retrieved": True,
            "NOFT_retrieved": True,
        })

    if_reconciliation = load(args.if_reconciliation)
    details = load(args.detail_harvest)
    candidate_ids = set(if_reconciliation.get("candidate_only_union_ids", []))
    if candidate_ids != IF_PLAUSIBLE | IF_LIKELY_NOISE:
        raise RuntimeError("IF candidate-only union changed.")
    detail_map = {record["paper_id"]: record for record in details["records"]}
    if not candidate_ids.issubset(detail_map):
        raise RuntimeError("IF candidate details are incomplete.")
    historical = load(args.pilot003_union)
    historical_ids = {
        paper_id
        for partition in historical["partition_unions"].values()
        for paper_id in partition["deduplicated_stable_ids"]
    }
    if candidate_ids & historical_ids:
        raise RuntimeError("An IF-only candidate already appeared in the historical literal union.")

    if_counts = {}
    for partition in PARTITIONS:
        passes = []
        for pass_number in (1, 2):
            literal = load(retry3 / f"if-{partition}-literal-count-pass{pass_number}.json")["total"]
            augmented = load(retry3 / f"if-{partition}-augmented-count-pass{pass_number}.json")["total"]
            passes.append({"literal": literal, "if_augmented": augmented, "delta": augmented - literal})
        if passes[0] != passes[1]:
            raise RuntimeError(f"IF count comparison changed for {partition}.")
        if_counts[partition] = {**passes[1], "passes_equal": True}

    if_candidates = []
    for paper_id in if_reconciliation["candidate_only_union_ids"]:
        record = detail_map[paper_id]
        classification = (
            "plausible_review_candidate"
            if paper_id in IF_PLAUSIBLE
            else "likely_search_noise"
        )
        if_candidates.append({
            "paper_id": paper_id,
            "title": record["title"],
            "classification_for_search_method": classification,
            "abstract": record["abstract"],
            "partitions": [
                partition
                for partition in ("B1", "B2", "BC1", "BT2")
                if paper_id in if_reconciliation["cells"][partition]["candidate_only_ids"]
            ],
            "final_screening_decision": None,
        })

    language_counts = {}
    for partition in PARTITIONS:
        passes = []
        for pass_number in (1, 2):
            unfiltered = load(retry7 / f"final-language-{partition}-unfiltered-count-pass{pass_number}.json")["total"]
            english = load(retry7 / f"final-language-{partition}-english-count-pass{pass_number}.json")["total"]
            passes.append({"unfiltered": unfiltered, "english": english, "excluded": unfiltered - english})
        if passes[0] != passes[1]:
            raise RuntimeError(f"Final language comparison changed for {partition}.")
        language_counts[partition] = {**passes[1], "passes_equal": True}
    final_exclusions = load(args.final_language_exclusions)
    if final_exclusions.get("stable_ids_in_source_order") != LANGUAGE_IDS:
        raise RuntimeError("Final language-exclusion IDs changed.")
    language_records = []
    for paper_id in LANGUAGE_IDS:
        record = detail_map[paper_id]
        publication_language = record["fields"].get("Language of publication")
        if publication_language != "Chinese":
            raise RuntimeError(f"Excluded record {paper_id} is not source-labelled Chinese.")
        language_records.append({
            "paper_id": paper_id,
            "title": record["title"],
            "publication": record["publication"],
            "language_of_publication": publication_language,
            "summary_language": record["fields"].get("Summary language"),
            "abstract_language_observed": "English",
            "source_language_restriction_basis": "source Language of publication",
            "source_publication_language_matches_English": False,
            "final_screening_decision": None,
        })

    return {
        "schema_version": "atai-pilot-006-assessment/v1",
        "source": "Advanced Technologies & Aerospace Index",
        "pilot": "006",
        "status": "complete",
        "do_not_merge": True,
        "decisions": {
            "NOFT_field_coverage": "validated_for_TI_AB_MAINSUBJECT_but_not_IF",
            "indexed_keyword_translation": "accept_IF_EXACT_OR_supplement_for_every_ordinary_literal",
            "pair_translation": "retain_NOFT_NEAR_5",
            "language_filter": "retain_LA_English",
        },
        "field_coverage": {
            "known_item_contrasts": field_pairs,
            "indexed_keyword_contrast": {
                "paper_id": "2438984228",
                "term": "Aerospace engineering",
                "date_scope": "All dates because the known item falls outside the review window",
                "repeated_totals": index_totals,
                "finding": "NOFT did not retrieve a record independently retrieved by IF.EXACT. NOFT does not cover the distinct IF indexed-keyword field.",
            },
            "boundary": "The bounded evidence covers protocol-relevant title, abstract, controlled-subject, and indexed-keyword fields. It does not enumerate every administrative metadata field.",
        },
        "pair_validation": {
            "pair": ["adapted", "model"],
            "max_intervening_words": 5,
            "positive_records": pair_local,
            "explicit_AB_ids": pair_ids,
            "NOFT_ids": pair_ids,
            "cross_field_negative": {
                "paper_id": "3181339955",
                "markers": ["BOREALIS", "Moon"],
                "source_total": 0,
                "finding": "NOFT NEAR/5 did not join markers from separate captured metadata fields.",
            },
            "decision": "The bounded source-located pair gate retained every local AB positive and rejected the cross-field construction. Keep NOFT NEAR/5 for declared pairs.",
        },
        "indexed_keyword_assessment": {
            "translation": {
                "ordinary_atom": "(NOFT(L(s)) OR IF.EXACT(L(s)))",
                "pair_atom": "NOFT(L(a) NEAR/5 L(b))",
            },
            "two_pass_partition_counts": if_counts,
            "affected_partitions": [partition for partition, value in if_counts.items() if value["delta"] > 0],
            "stable_id_reconciliation": str(args.if_reconciliation),
            "candidate_only_union_total": len(candidate_ids),
            "candidate_only_union_ids": if_reconciliation["candidate_only_union_ids"],
            "historical_literal_union_overlap": [],
            "plausible_review_candidate_count": len(IF_PLAUSIBLE),
            "likely_search_noise_count": len(IF_LIKELY_NOISE),
            "candidate_records": if_candidates,
            "decision": "Accept the IF.EXACT OR supplement. It adds six plausible candidates that the literal NOFT schedule missed. Screening will resolve eligibility and the three noisy additions.",
        },
        "language_assessment": {
            "translation": "LA(English)",
            "two_pass_final_partition_counts": language_counts,
            "partitions_with_exclusions": [partition for partition, value in language_counts.items() if value["excluded"] > 0],
            "excluded_stable_ids": LANGUAGE_IDS,
            "excluded_records": language_records,
            "decision": "Retain LA(English). Across the final IF-augmented translation, only B2 lost records. Both excluded records are source-labelled Chinese publications. English abstracts do not make their full reports English.",
            "limitation": "This is a bounded source-language audit. Source language metadata does not replace full-text language screening for retrieved candidates.",
        },
        "prospective_source_translation": {
            "ordinary_literals": "Search each literal in NOFT and exact IF indexed keywords with source OR.",
            "declared_pairs": "Keep unordered NOFT NEAR/5 with no IF emulation.",
            "language": "Apply LA(English).",
            "type_and_access": "Keep the existing no-filter decisions.",
        },
        "pilot_boundary": "These are search-method decisions. Candidate classifications are not final screening decisions and all artifacts remain non-mergeable.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--if-reconciliation", type=Path, required=True)
    parser.add_argument("--detail-harvest", type=Path, required=True)
    parser.add_argument("--pilot003-union", type=Path, required=True)
    parser.add_argument("--final-language-exclusions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assessment = build(args)
    args.output.write_text(json.dumps(assessment, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
