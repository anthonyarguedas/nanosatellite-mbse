#!/usr/bin/env python3
"""Run a local GraphRAG-style demo over the SLR1 KG and embedding cards.

This is intentionally dependency-light and deterministic. It embeds fixed demo
questions with the ISSUE-003 `hashing_tfidf_v1` vectorizer metadata, retrieves
same-index cards, expands selected seeds over the controlled-code KG by 1--2
hops, and writes cited exploratory answers plus retrieval traces.
"""

from __future__ import annotations

import csv
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from kg_common import (
    BASE_DIR,
    DATA_DIR,
    KG_DIR,
    REPORTS_DIR,
    SCRIPT_DIR,
    TABLES_DIR,
    clean_text,
    dedupe_study_codes,
    ensure_dirs,
    ensure_issue001_outputs,
    is_none_like,
    join_values,
    load_jsonl,
    markdown_table,
    unique_preserve,
    values,
    write_csv,
    write_text,
)


EMBEDDINGS_DIR = BASE_DIR / "embeddings"
MODEL_NAME = "hashing_tfidf_v1"
VECTOR_PATH = EMBEDDINGS_DIR / f"vectors_{MODEL_NAME}.npy"
VECTORIZER_PATH = EMBEDDINGS_DIR / f"vectorizer_{MODEL_NAME}.json"
CARD_INDEX_PATH = EMBEDDINGS_DIR / "card_index.jsonl"
MANIFEST_PATH = EMBEDDINGS_DIR / "embedding_manifest.json"
NODES_PATH = KG_DIR / "nodes.csv"
EDGES_PATH = KG_DIR / "edges.csv"

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._+#/\-][a-z0-9]+)*", re.IGNORECASE)

EPS_RELEVANCE_FIELD = "study_context_population.eps_relevance"
EPS_ELEMENTS_FIELD = "eps_verification_specific.eps_elements_modeled"
VERIFICATION_MECHANISM_FIELD = "eps_verification_specific.pre_physical_development_verification_mechanism"
VERIFICATION_ARTIFACT_FIELD = "eps_verification_specific.verification_validation_artifacts"
IVV_FIELD = "eps_verification_specific.ivv_integration_level"
TOOL_FIELD = "toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool"
INTEROP_FIELD = "toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms"
TOOL_LIMITATION_FIELD = "toolchain_interoperability_lifecycle_continuity.toolchain_limitations"
REUSE_FIELD = "mbse_objective_scope_artifacts.generality_reuse_mechanism"
MODEL_ARTIFACT_FIELD = "mbse_objective_scope_artifacts.model_artifacts_used"
MODEL_MATURITY_FIELD = "study_context_population.model_maturity"
REPRO_FIELD = "quality_checklist.reproducibility_toolchain_reported"
LIFECYCLE_FIELD = "study_context_population.lifecycle_stage_addressed"

WEAK_OR_UNSUPPORTED = {"Weak", "Unsupported"}
MODERATE_OR_STRONG = {"Moderate", "Strong"}
EVIDENCE_CONFIDENCE_SCORE = {
    "Unsupported": 0.0,
    "Weak": 1.0,
    "Moderate": 2.0,
    "Strong": 3.0,
}

ANSWER_SOURCE_COLUMNS = [
    "question_id",
    "question",
    "answer_rank",
    "source_type",
    "corpus_id",
    "study_title",
    "source_id",
    "claim_id",
    "card_id",
    "retrieval_similarity",
    "combined_score",
    "kg_seed_nodes",
    "kg_expanded_node_count",
    "kg_expanded_edge_count",
    "field_paths",
    "controlled_values",
    "evidence_type",
    "evidence_confidence",
    "baseline_comparator",
    "evidence_quote_or_snippet",
    "retrieval_reason",
    "exploratory",
]

QUESTIONS = [
    {
        "id": "q1_eps_pre_physical_verification",
        "question": "Which papers provide the strongest evidence for EPS pre-physical verification?",
        "unit_types": ["study_card", "claim_card", "evidence_quote_card", "gap_mapping_card", "limitation_card"],
    },
    {
        "id": "q2_simulation_in_the_loop_toolchains",
        "question": "What toolchains support simulation-in-the-loop verification?",
        "unit_types": ["study_card", "claim_card", "evidence_quote_card", "limitation_card"],
    },
    {
        "id": "q3_effort_reduction_baselines",
        "question": "Which claims about effort reduction have baseline comparators?",
        "unit_types": ["claim_card", "evidence_quote_card", "study_card"],
    },
    {
        "id": "q4_reusable_reference_models",
        "question": "Where are reusable reference models available?",
        "unit_types": ["study_card", "claim_card", "evidence_quote_card", "limitation_card", "gap_mapping_card"],
    },
]


class KGIndex:
    def __init__(self, node_rows: list[dict[str, str]], edge_rows: list[dict[str, str]]) -> None:
        self.nodes = {row["id"]: row for row in node_rows}
        self.edges = edge_rows
        self.out_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
        self.in_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
        for idx, edge in enumerate(edge_rows):
            edge = dict(edge)
            edge["_edge_index"] = str(idx)
            self.out_edges[edge["source"]].append(edge)
            self.in_edges[edge["target"]].append(edge)

    def expand(self, seed_nodes: Iterable[str], max_hops: int = 2, max_edges: int = 120) -> dict[str, Any]:
        seeds = [node for node in unique_preserve(seed_nodes) if node in self.nodes]
        visited_nodes = set(seeds)
        frontier = set(seeds)
        collected_edges: dict[tuple[str, str, str, str], dict[str, str]] = {}
        for _hop in range(max_hops):
            next_frontier: set[str] = set()
            for node in sorted(frontier):
                for edge in [*self.out_edges.get(node, []), *self.in_edges.get(node, [])]:
                    key = (edge.get("source", ""), edge.get("target", ""), edge.get("type", ""), edge.get("_edge_index", ""))
                    if len(collected_edges) < max_edges:
                        collected_edges[key] = edge
                    neighbor = edge["target"] if edge.get("source") == node else edge.get("source")
                    if neighbor and neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        next_frontier.add(neighbor)
            frontier = next_frontier
            if not frontier:
                break
        sample_edges = sorted(
            collected_edges.values(),
            key=lambda row: (row.get("type", ""), row.get("source", ""), row.get("target", "")),
        )[:40]
        return {
            "seed_nodes": seeds,
            "hop_limit": max_hops,
            "node_count": len(visited_nodes),
            "edge_count": len(collected_edges),
            "sample_edges": [
                {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "type": edge.get("type"),
                    "source_field_path": edge.get("source_field_path"),
                    "source_value": edge.get("source_value"),
                    "evidence_quote": snippet(edge.get("evidence_quote"), 180),
                }
                for edge in sample_edges
            ],
        }


def run_script_if_missing(script_name: str, required_paths: list[Path]) -> None:
    if all(path.exists() and path.stat().st_size > 0 for path in required_paths):
        return
    script = SCRIPT_DIR / script_name
    if not script.exists():
        missing = ", ".join(str(path.relative_to(BASE_DIR)) for path in required_paths if not path.exists())
        raise FileNotFoundError(f"Missing {missing}; cannot run absent dependency script {script}")
    subprocess.run([sys.executable, str(script)], check=True)
    still_missing = [path for path in required_paths if not path.exists() or path.stat().st_size == 0]
    if still_missing:
        missing = ", ".join(str(path.relative_to(BASE_DIR)) for path in still_missing)
        raise FileNotFoundError(f"Dependency script {script_name} did not produce: {missing}")


def ensure_required_artifacts() -> None:
    ensure_issue001_outputs()
    run_script_if_missing("02_build_kg.py", [NODES_PATH, EDGES_PATH, KG_DIR / "graph.graphml"])
    run_script_if_missing("04_build_embedding_cards.py", [CARD_INDEX_PATH])
    run_script_if_missing("05_embed_and_neighbors.py", [VECTOR_PATH, VECTORIZER_PATH, MANIFEST_PATH])
    ensure_dirs(TABLES_DIR, REPORTS_DIR)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_for_tokenization(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\biv\s*&\s*v\b", "ivv", lowered)
    lowered = re.sub(r"\bi\s*/\s*v\s*/\s*v\b", "ivv", lowered)
    lowered = re.sub(r"\bi\s*-\s*v\s*-\s*v\b", "ivv", lowered)
    return lowered


def tokenize(text: Any) -> list[str]:
    return TOKEN_RE.findall(normalize_for_tokenization(clean_text(text) or ""))


def query_vector(question: str, vectorizer: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    dimensions = int(vectorizer.get("dimensions") or 384)
    token_stats = vectorizer.get("token_stats") or []
    token_info = {
        str(row["token"]): (float(row["idf"]), int(row["hash_bucket"]), int(row["hash_sign"]))
        for row in token_stats
        if "token" in row and "idf" in row and "hash_bucket" in row and "hash_sign" in row
    }
    counts = Counter(tokenize(question))
    vector = np.zeros((dimensions,), dtype=np.float32)
    oov_tokens = []
    for token, tf in counts.items():
        info = token_info.get(token)
        if info is None:
            oov_tokens.append(token)
            continue
        idf, bucket, sign = info
        vector[bucket] += np.float32(float(sign) * (1.0 + math.log(float(tf))) * idf)
    norm = float(np.linalg.norm(vector))
    if norm > 0.0:
        vector /= norm
    metadata = {
        "model_name": vectorizer.get("model_name", MODEL_NAME),
        "dimensions": dimensions,
        "query_tokens": sorted(counts),
        "query_token_count": sum(counts.values()),
        "in_vocabulary_token_count": sum(count for token, count in counts.items() if token in token_info),
        "oov_tokens": sorted(oov_tokens),
        "oov_token_count": len(oov_tokens),
    }
    return vector, metadata


def snippet(value: Any, max_chars: int = 240) -> str:
    text = clean_text(value) or ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def source_record(card: dict[str, Any]) -> dict[str, Any]:
    metadata = card.get("metadata", {}) if isinstance(card.get("metadata"), dict) else {}
    record = metadata.get("source_record")
    return record if isinstance(record, dict) else {}


def retrieve_cards(
    question: str,
    unit_types: list[str],
    cards: list[dict[str, Any]],
    vectors: np.ndarray,
    vectorizer: dict[str, Any],
    *,
    top_k_per_type: int = 8,
    max_total: int = 32,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    vector, query_meta = query_vector(question, vectorizer)
    scores = vectors @ vector if float(np.linalg.norm(vector)) > 0.0 else np.zeros((len(cards),), dtype=np.float32)
    selected: dict[str, dict[str, Any]] = {}
    for unit_type in unit_types:
        indices = [idx for idx, card in enumerate(cards) if card.get("unit_type") == unit_type]
        indices.sort(key=lambda idx: (-float(scores[idx]), int(cards[idx].get("card_index", idx)), str(cards[idx].get("card_id"))))
        for unit_rank, idx in enumerate(indices[:top_k_per_type], start=1):
            card = cards[idx]
            selected[str(card.get("card_id"))] = {
                "rank_within_unit_type": unit_rank,
                "score": round(float(scores[idx]), 6),
                "card": card,
            }
    rows = sorted(
        selected.values(),
        key=lambda row: (-float(row["score"]), str(row["card"].get("unit_type")), int(row["card"].get("card_index", 0))),
    )[:max_total]
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    trace_cards = [
        {
            "rank": row["rank"],
            "rank_within_unit_type": row["rank_within_unit_type"],
            "similarity": row["score"],
            "card_id": row["card"].get("card_id"),
            "unit_type": row["card"].get("unit_type"),
            "study_id": row["card"].get("study_id"),
            "claim_id": row["card"].get("claim_id"),
            "label": row["card"].get("label") or row["card"].get("title"),
            "snippet": snippet(row["card"].get("text"), 260),
        }
        for row in rows
    ]
    query_meta["relevant_unit_types"] = unit_types
    return rows, {"query": query_meta, "top_cards": trace_cards}


def build_field_index(study_codes: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in study_codes:
        study_id = clean_text(record.get("study_id"))
        field_path = clean_text(record.get("field_path"))
        value = clean_text(record.get("value"))
        if study_id and field_path and value is not None:
            out[study_id][field_path].append(record)
    return {study_id: dict(fields) for study_id, fields in out.items()}


def field_values(field_index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_path: str) -> list[str]:
    return unique_preserve(
        value
        for value in (clean_text(record.get("value")) for record in field_index.get(study_id, {}).get(field_path, []))
        if value
    )


def meaningful_values(field_index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_path: str) -> list[str]:
    return [value for value in field_values(field_index, study_id, field_path) if not is_none_like(value)]


def field_quote(
    field_index: dict[str, dict[str, list[dict[str, Any]]]],
    study_id: str,
    field_paths: Iterable[str],
    max_chars: int = 360,
) -> str:
    parts: list[str] = []
    for field_path in field_paths:
        for record in field_index.get(study_id, {}).get(field_path, []):
            for key in ["evidence_quote", "rationale"]:
                text = clean_text(record.get(key))
                if text:
                    parts.append(f"{field_path}: {text}")
                    break
            if parts:
                break
    return snippet(" // ".join(unique_preserve(parts)), max_chars)


def field_summary(
    field_index: dict[str, dict[str, list[dict[str, Any]]]],
    study_id: str,
    field_paths: Iterable[str],
) -> tuple[str, str]:
    paths = []
    values_out = []
    for field_path in field_paths:
        vals = meaningful_values(field_index, study_id, field_path)
        if vals:
            paths.append(field_path)
            values_out.append(f"{field_path}={join_values(vals)}")
    return "; ".join(paths), " // ".join(values_out)


def claims_by_study(claims: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        out[str(claim["study_id"])].append(claim)
    return {study_id: sorted(rows, key=lambda row: str(row.get("claim_id"))) for study_id, rows in out.items()}


def limitations_by_study(limitations: Iterable[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for limitation in limitations:
        flag = clean_text(limitation.get("flag"))
        if flag:
            out[str(limitation["study_id"])].add(flag)
    return dict(out)


def quote_by_claim(evidence_quotes: Iterable[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for quote in evidence_quotes:
        claim_id = clean_text(quote.get("claim_id"))
        quote_text = clean_text(quote.get("evidence_quote"))
        if claim_id and quote_text and claim_id not in out:
            out[claim_id] = quote_text
    return out


def retrieval_maps(retrieved: list[dict[str, Any]]) -> dict[str, dict[str, tuple[float, str]]]:
    by_study: dict[str, tuple[float, str]] = {}
    by_claim: dict[str, tuple[float, str]] = {}
    for row in retrieved:
        card = row["card"]
        score = float(row["score"])
        card_id = str(card.get("card_id"))
        study_id = clean_text(card.get("study_id"))
        claim_id = clean_text(card.get("claim_id")) or clean_text(source_record(card).get("claim_id"))
        if study_id and (study_id not in by_study or score > by_study[study_id][0]):
            by_study[study_id] = (score, card_id)
        if claim_id and (claim_id not in by_claim or score > by_claim[claim_id][0]):
            by_claim[claim_id] = (score, card_id)
    return {"study": by_study, "claim": by_claim}


def confidence_score(value: Any) -> float:
    return EVIDENCE_CONFIDENCE_SCORE.get(clean_text(value) or "", -0.5)


def evidence_type_boost(claim: dict[str, Any]) -> float:
    text = " ".join(values(claim.get("evidence_type"))).lower()
    boost = 0.0
    if "integration/test" in text or "flight" in text or "operational" in text:
        boost += 2.5
    if "quantitative comparison" in text or "counterfactual" in text:
        boost += 2.0
    if "executable model" in text or "simulation result" in text:
        boost += 1.5
    if "trade-study" in text or "requirements-checking" in text:
        boost += 1.2
    if "single case-study" in text:
        boost += 0.5
    return boost


def best_claim_for_study(study_claims: list[dict[str, Any]], prefer_terms: Iterable[str] = ()) -> dict[str, Any] | None:
    terms = [term.lower() for term in prefer_terms]
    if not study_claims:
        return None
    scored = []
    for claim in study_claims:
        text = " ".join(
            [
                clean_text(claim.get("claim_text")) or "",
                " ".join(values(claim.get("outcome_category"))),
                " ".join(values(claim.get("evidence_type"))),
                " ".join(values(claim.get("metric"))),
            ]
        ).lower()
        term_score = sum(1 for term in terms if term in text)
        scored.append((confidence_score(claim.get("evidence_confidence")) + evidence_type_boost(claim) + term_score, str(claim.get("claim_id")), claim))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[0][2]


def is_eps_relevant(values_in: list[str]) -> bool:
    if not values_in:
        return False
    for value in values_in:
        lower = value.lower()
        if "not eps" in lower:
            continue
        if "system-level only" in lower:
            continue
        return True
    return False


def contains_any(values_in: Iterable[str], needles: Iterable[str]) -> bool:
    combined = " | ".join(values_in).lower()
    return any(needle.lower() in combined for needle in needles)


def baseline_present(value: Any) -> bool:
    text = (clean_text(value) or "").strip()
    lower = text.lower()
    if not text or is_none_like(text):
        return False
    disqualifiers = [
        "not reported",
        "no empirical comparator",
        "no manual-analysis",
        "no reuse",
        "no prior mission",
        "no prior",
        "none",
    ]
    return not any(item in lower for item in disqualifiers)


def claim_is_effort_related(claim: dict[str, Any]) -> bool:
    outcomes = {value.lower() for value in values(claim.get("outcome_category"))}
    metrics = {value.lower() for value in values(claim.get("metric"))}
    text = (clean_text(claim.get("claim_text")) or "").lower()
    return (
        "effort reduction" in outcomes
        or "schedule reduction" in outcomes
        or "cost reduction" in outcomes
        or bool(metrics & {"effort", "time", "cost", "schedule"})
        or any(term in text for term in ["effort", "schedule", "cost", "time", "manual", "tedious", "faster"])
    )


def claim_is_reuse_related(claim: dict[str, Any]) -> bool:
    outcomes = {value.lower() for value in values(claim.get("outcome_category"))}
    metrics = {value.lower() for value in values(claim.get("metric"))}
    mechanisms = {value.lower() for value in values(claim.get("mbse_mechanism"))}
    text = (clean_text(claim.get("claim_text")) or "").lower()
    return (
        "generality/reuse" in outcomes
        or "reproducibility" in outcomes
        or "model reuse" in metrics
        or "reference model reuse" in mechanisms
        or "reference model" in text
        or "template" in text
        or "reuse" in text
    )


def source_row(
    *,
    qid: str,
    question: str,
    rank: int,
    source_type: str,
    study_id: str,
    study_title: str,
    source_id: str,
    claim_id: str = "",
    card_id: str = "",
    retrieval_similarity: float = 0.0,
    combined_score: float = 0.0,
    expansion: dict[str, Any] | None = None,
    field_paths: str = "",
    controlled_values: str = "",
    evidence_type: str = "",
    evidence_confidence: str = "",
    baseline: str = "",
    evidence_quote: str = "",
    reason: str = "",
) -> dict[str, Any]:
    expansion = expansion or {"seed_nodes": [], "node_count": 0, "edge_count": 0}
    return {
        "question_id": qid,
        "question": question,
        "answer_rank": rank,
        "source_type": source_type,
        "corpus_id": study_id,
        "study_title": study_title,
        "source_id": source_id,
        "claim_id": claim_id,
        "card_id": card_id,
        "retrieval_similarity": f"{retrieval_similarity:.6f}",
        "combined_score": f"{combined_score:.6f}",
        "kg_seed_nodes": "; ".join(expansion.get("seed_nodes", [])),
        "kg_expanded_node_count": expansion.get("node_count", 0),
        "kg_expanded_edge_count": expansion.get("edge_count", 0),
        "field_paths": field_paths,
        "controlled_values": controlled_values,
        "evidence_type": evidence_type,
        "evidence_confidence": evidence_confidence,
        "baseline_comparator": baseline,
        "evidence_quote_or_snippet": evidence_quote,
        "retrieval_reason": reason,
        "exploratory": True,
    }


def kg_seed_for_source(source_type: str, study_id: str, claim_id: str = "") -> list[str]:
    if source_type == "claim" and claim_id:
        return [study_id, claim_id]
    return [study_id]


def q1_claim_relevant_to_eps_verification(claim: dict[str, Any]) -> bool:
    text = " ".join(
        [
            clean_text(claim.get("claim_text")) or "",
            " ".join(values(claim.get("outcome_category"))),
            " ".join(values(claim.get("mbse_mechanism"))),
            " ".join(values(claim.get("evidence_type"))),
            " ".join(values(claim.get("metric"))),
            clean_text(claim.get("observed_effect")) or "",
        ]
    ).lower()
    positive_terms = [
        "verification",
        "simulation",
        "trade-study",
        "requirements-checking",
        "requirements compliance",
        "parametric",
        "power",
        "battery",
        "solar",
        "eps",
        "mission assurance",
        "risk reduction",
        "decision support",
    ]
    if not any(term in text for term in positive_terms):
        return False
    # Avoid letting strong but unrelated effort/cost claims dominate an EPS
    # verification answer solely because they have higher evidence confidence.
    outcome_text = " ".join(values(claim.get("outcome_category"))).lower()
    if any(term in outcome_text for term in ["effort reduction", "cost reduction", "schedule reduction"]) and not any(
        term in text for term in ["verification", "simulation", "power", "battery", "solar", "eps"]
    ):
        return False
    return True


def q1_eps_pre_physical(data: dict[str, Any], retrieved: list[dict[str, Any]], kg: KGIndex) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    maps = retrieval_maps(retrieved)
    rows: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for study_id, study in data["studies_by_id"].items():
        eps_relevance = meaningful_values(data["field_index"], study_id, EPS_RELEVANCE_FIELD)
        eps_elements = meaningful_values(data["field_index"], study_id, EPS_ELEMENTS_FIELD)
        mechanisms = meaningful_values(data["field_index"], study_id, VERIFICATION_MECHANISM_FIELD)
        artifacts = meaningful_values(data["field_index"], study_id, VERIFICATION_ARTIFACT_FIELD)
        ivv = meaningful_values(data["field_index"], study_id, IVV_FIELD)
        if not is_eps_relevant(eps_relevance + eps_elements):
            continue
        verification_text_values = [*mechanisms, *artifacts, *ivv]
        has_pre_physical = bool(verification_text_values) and not all(is_none_like(value) for value in verification_text_values)
        if not has_pre_physical:
            continue
        study_claims = data["claims_by_study"].get(study_id, [])
        relevant_claims = [claim for claim in study_claims if q1_claim_relevant_to_eps_verification(claim)]
        best_claim = best_claim_for_study(relevant_claims, ["verification", "simulation", "trade", "power", "battery", "solar", "eps", "mission assurance"])
        best_conf = confidence_score(best_claim.get("evidence_confidence")) if best_claim else 0.0
        best_evidence_boost = evidence_type_boost(best_claim) if best_claim else 0.0
        retrieval_score, card_id = maps["study"].get(study_id, (0.0, ""))
        eps_score = 2.0 if contains_any(eps_relevance, ["eps-specific", "power-budget", "electrical"]) else 1.0
        verification_score = 0.0
        if contains_any(mechanisms + ivv, ["simulation-in-the-loop", "executable", "requirements-in-the-loop"]):
            verification_score += 2.0
        if contains_any(mechanisms, ["parametric", "trade-study", "virtual integration"]):
            verification_score += 1.2
        if contains_any(artifacts, ["simulation", "executable", "acceptance", "test", "verification matrix"]):
            verification_score += 1.0
        combined = retrieval_score * 4.0 + eps_score + verification_score + best_conf + best_evidence_boost
        if combined <= 1.0:
            continue
        candidates.append(
            {
                "study_id": study_id,
                "study_title": clean_text(study.get("title")) or study_id,
                "score": combined,
                "retrieval_score": retrieval_score,
                "card_id": card_id,
                "best_claim": best_claim,
                "eps_relevance": eps_relevance,
                "eps_elements": eps_elements,
                "mechanisms": mechanisms,
                "artifacts": artifacts,
                "ivv": ivv,
            }
        )
    candidates.sort(key=lambda row: (-float(row["score"]), row["study_id"]))
    for rank, candidate in enumerate(candidates[:10], start=1):
        claim = candidate["best_claim"] or {}
        claim_id = clean_text(claim.get("claim_id")) or ""
        expansion = kg.expand(kg_seed_for_source("claim" if claim_id else "study", candidate["study_id"], claim_id))
        field_paths, controlled_values = field_summary(
            data["field_index"],
            candidate["study_id"],
            [EPS_RELEVANCE_FIELD, EPS_ELEMENTS_FIELD, VERIFICATION_MECHANISM_FIELD, VERIFICATION_ARTIFACT_FIELD, IVV_FIELD],
        )
        quote = data["claim_quotes"].get(claim_id) or field_quote(
            data["field_index"],
            candidate["study_id"],
            [VERIFICATION_MECHANISM_FIELD, VERIFICATION_ARTIFACT_FIELD, EPS_ELEMENTS_FIELD, EPS_RELEVANCE_FIELD],
        )
        rows.append(
            source_row(
                qid="q1_eps_pre_physical_verification",
                question=QUESTIONS[0]["question"],
                rank=rank,
                source_type="study_with_claim_context" if claim_id else "study",
                study_id=candidate["study_id"],
                study_title=candidate["study_title"],
                source_id=candidate["study_id"],
                claim_id=claim_id,
                card_id=candidate["card_id"],
                retrieval_similarity=float(candidate["retrieval_score"]),
                combined_score=float(candidate["score"]),
                expansion=expansion,
                field_paths=field_paths,
                controlled_values=controlled_values,
                evidence_type=join_values(values(claim.get("evidence_type"))),
                evidence_confidence=clean_text(claim.get("evidence_confidence")) or "",
                evidence_quote=snippet(quote or claim.get("claim_text"), 480),
                reason="EPS-relevant study with coded pre-physical verification mechanism/artifact and best available claim-evidence confidence.",
            )
        )
    return rows, candidates[:10], []


def q2_toolchains(data: dict[str, Any], retrieved: list[dict[str, Any]], kg: KGIndex) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    maps = retrieval_maps(retrieved)
    candidates: list[dict[str, Any]] = []
    for study_id, study in data["studies_by_id"].items():
        mechanisms = meaningful_values(data["field_index"], study_id, VERIFICATION_MECHANISM_FIELD)
        artifacts = meaningful_values(data["field_index"], study_id, VERIFICATION_ARTIFACT_FIELD)
        ivv = meaningful_values(data["field_index"], study_id, IVV_FIELD)
        if not contains_any([*mechanisms, *artifacts, *ivv], ["simulation-in-the-loop", "simulation scenarios", "executable", "co-simulation"]):
            continue
        tools = meaningful_values(data["field_index"], study_id, TOOL_FIELD)
        interop = meaningful_values(data["field_index"], study_id, INTEROP_FIELD)
        tool_limits = meaningful_values(data["field_index"], study_id, TOOL_LIMITATION_FIELD)
        retrieval_score, card_id = maps["study"].get(study_id, (0.0, ""))
        score = retrieval_score * 4.0 + 2.0
        if contains_any(mechanisms + ivv, ["simulation-in-the-loop"]):
            score += 3.0
        if tools:
            score += min(2.0, 0.35 * len(tools))
        if contains_any(interop, ["co-simulation", "api", "scripts", "model transformation", "plugin"]):
            score += 1.5
        best_claim = best_claim_for_study(data["claims_by_study"].get(study_id, []), ["simulation", "tool", "interoperability", "verification"])
        candidates.append(
            {
                "study_id": study_id,
                "study_title": clean_text(study.get("title")) or study_id,
                "score": score,
                "retrieval_score": retrieval_score,
                "card_id": card_id,
                "mechanisms": mechanisms,
                "artifacts": artifacts,
                "ivv": ivv,
                "tools": tools,
                "interop": interop,
                "tool_limits": tool_limits,
                "best_claim": best_claim,
            }
        )
    candidates.sort(key=lambda row: (-float(row["score"]), row["study_id"]))
    rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates[:12], start=1):
        claim = candidate["best_claim"] or {}
        claim_id = clean_text(claim.get("claim_id")) or ""
        expansion = kg.expand(kg_seed_for_source("claim" if claim_id else "study", candidate["study_id"], claim_id))
        field_paths, controlled_values = field_summary(
            data["field_index"],
            candidate["study_id"],
            [TOOL_FIELD, INTEROP_FIELD, VERIFICATION_MECHANISM_FIELD, VERIFICATION_ARTIFACT_FIELD, IVV_FIELD, TOOL_LIMITATION_FIELD],
        )
        quote = data["claim_quotes"].get(claim_id) or field_quote(
            data["field_index"],
            candidate["study_id"],
            [TOOL_FIELD, INTEROP_FIELD, VERIFICATION_MECHANISM_FIELD, VERIFICATION_ARTIFACT_FIELD, IVV_FIELD],
        )
        rows.append(
            source_row(
                qid="q2_simulation_in_the_loop_toolchains",
                question=QUESTIONS[1]["question"],
                rank=rank,
                source_type="study_toolchain",
                study_id=candidate["study_id"],
                study_title=candidate["study_title"],
                source_id=candidate["study_id"],
                claim_id=claim_id,
                card_id=candidate["card_id"],
                retrieval_similarity=float(candidate["retrieval_score"]),
                combined_score=float(candidate["score"]),
                expansion=expansion,
                field_paths=field_paths,
                controlled_values=controlled_values,
                evidence_type=join_values(values(claim.get("evidence_type"))),
                evidence_confidence=clean_text(claim.get("evidence_confidence")) or "",
                evidence_quote=snippet(quote or claim.get("claim_text"), 480),
                reason="Coded simulation-in-the-loop/executable verification plus tool and interoperability fields.",
            )
        )
    return rows, candidates[:12], []


def q3_effort_baselines(data: dict[str, Any], retrieved: list[dict[str, Any]], kg: KGIndex) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    maps = retrieval_maps(retrieved)
    candidates: list[dict[str, Any]] = []
    for claim in data["claims"]:
        if not claim_is_effort_related(claim) or not baseline_present(claim.get("baseline")):
            continue
        claim_id = str(claim["claim_id"])
        study_id = str(claim["study_id"])
        retrieval_score, card_id = maps["claim"].get(claim_id, maps["study"].get(study_id, (0.0, "")))
        score = retrieval_score * 5.0 + confidence_score(claim.get("evidence_confidence")) + evidence_type_boost(claim)
        if "quantitative comparison" in " ".join(values(claim.get("evidence_type"))).lower():
            score += 2.0
        baseline = clean_text(claim.get("baseline")) or ""
        if baseline.lower() in {"manual analysis", "previous document-centric process", "alternative toolchain", "previous mission"}:
            score += 1.0
        candidates.append({"claim": claim, "study": data["studies_by_id"].get(study_id, {}), "score": score, "retrieval_score": retrieval_score, "card_id": card_id})
    candidates.sort(
        key=lambda row: (
            -confidence_score(row["claim"].get("evidence_confidence")),
            -evidence_type_boost(row["claim"]),
            -float(row["score"]),
            str(row["claim"].get("claim_id")),
        )
    )
    rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates, start=1):
        claim = candidate["claim"]
        study_id = str(claim["study_id"])
        claim_id = str(claim["claim_id"])
        expansion = kg.expand([study_id, claim_id])
        quote = data["claim_quotes"].get(claim_id) or claim.get("observed_effect") or claim.get("claim_text")
        rows.append(
            source_row(
                qid="q3_effort_reduction_baselines",
                question=QUESTIONS[2]["question"],
                rank=rank,
                source_type="claim",
                study_id=study_id,
                study_title=clean_text(candidate["study"].get("title")) or study_id,
                source_id=claim_id,
                claim_id=claim_id,
                card_id=candidate["card_id"],
                retrieval_similarity=float(candidate["retrieval_score"]),
                combined_score=float(candidate["score"]),
                expansion=expansion,
                field_paths="claimed_outcomes_value_mechanisms_evidence[].outcome_category; claimed_outcomes_value_mechanisms_evidence[].baseline_comparator; claimed_outcomes_value_mechanisms_evidence[].evidence_type; claimed_outcomes_value_mechanisms_evidence[].evidence_confidence_rating",
                controlled_values=(
                    f"outcomes={join_values(values(claim.get('outcome_category')))} ; metrics={join_values(values(claim.get('metric')))} ; "
                    f"mechanisms={join_values(values(claim.get('mbse_mechanism')))}"
                ),
                evidence_type=join_values(values(claim.get("evidence_type"))),
                evidence_confidence=clean_text(claim.get("evidence_confidence")) or "",
                baseline=clean_text(claim.get("baseline")) or "",
                evidence_quote=snippet(quote, 520),
                reason="Effort/schedule/cost-related claim with non-empty baseline comparator coding.",
            )
        )
    return rows, candidates, []


def q4_reusable_models(data: dict[str, Any], retrieved: list[dict[str, Any]], kg: KGIndex) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    maps = retrieval_maps(retrieved)
    candidates: list[dict[str, Any]] = []
    for study_id, study in data["studies_by_id"].items():
        reuse = meaningful_values(data["field_index"], study_id, REUSE_FIELD)
        if not contains_any(reuse, ["reference model", "template", "library", "open package", "mission-agnostic", "reusable workflow", "pattern"]):
            continue
        artifacts = meaningful_values(data["field_index"], study_id, MODEL_ARTIFACT_FIELD)
        maturity = meaningful_values(data["field_index"], study_id, MODEL_MATURITY_FIELD)
        repro = meaningful_values(data["field_index"], study_id, REPRO_FIELD)
        limitations = data["limitations_by_study"].get(study_id, set())
        retrieval_score, card_id = maps["study"].get(study_id, (0.0, ""))
        reuse_claims = [claim for claim in data["claims_by_study"].get(study_id, []) if claim_is_reuse_related(claim)]
        best_claim = best_claim_for_study(reuse_claims, ["reuse", "reference model", "template", "open", "reproduc"])
        score = retrieval_score * 4.0
        if contains_any(reuse, ["open package"]):
            score += 4.0
        if contains_any(reuse, ["reference model"]):
            score += 2.0
        if contains_any(reuse, ["template", "library", "mission-agnostic"]):
            score += 1.5
        if contains_any(repro, ["Yes"]):
            score += 3.0
        elif contains_any(repro, ["Insufficiently"]):
            score -= 0.5
        if "model_not_available" in limitations:
            score -= 2.5
        if best_claim:
            score += confidence_score(best_claim.get("evidence_confidence")) + evidence_type_boost(best_claim) * 0.5
        availability = []
        if contains_any(reuse, ["open package"]):
            availability.append("open package coded")
        if contains_any(repro, ["Yes"]):
            availability.append("reproducibility/toolchain reported Yes")
        if "model_not_available" in limitations:
            availability.append("model_not_available limitation")
        if not availability:
            availability.append("availability unclear in extracted fields")
        candidates.append(
            {
                "study_id": study_id,
                "study_title": clean_text(study.get("title")) or study_id,
                "score": score,
                "retrieval_score": retrieval_score,
                "card_id": card_id,
                "reuse": reuse,
                "artifacts": artifacts,
                "maturity": maturity,
                "repro": repro,
                "limitations": sorted(limitations),
                "availability": availability,
                "best_claim": best_claim,
            }
        )
    candidates.sort(key=lambda row: (-float(row["score"]), row["study_id"]))
    rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates[:12], start=1):
        claim = candidate["best_claim"] or {}
        claim_id = clean_text(claim.get("claim_id")) or ""
        expansion = kg.expand(kg_seed_for_source("claim" if claim_id else "study", candidate["study_id"], claim_id))
        field_paths, controlled_values = field_summary(
            data["field_index"],
            candidate["study_id"],
            [REUSE_FIELD, MODEL_ARTIFACT_FIELD, MODEL_MATURITY_FIELD, REPRO_FIELD],
        )
        limitation_note = "limitations=" + "; ".join(flag for flag in candidate["limitations"] if flag in {"model_not_available", "no_independent_validation", "no_physical_test_or_flight_evidence"})
        quote = data["claim_quotes"].get(claim_id) or field_quote(data["field_index"], candidate["study_id"], [REUSE_FIELD, MODEL_ARTIFACT_FIELD, REPRO_FIELD])
        rows.append(
            source_row(
                qid="q4_reusable_reference_models",
                question=QUESTIONS[3]["question"],
                rank=rank,
                source_type="study_reuse_candidate",
                study_id=candidate["study_id"],
                study_title=candidate["study_title"],
                source_id=candidate["study_id"],
                claim_id=claim_id,
                card_id=candidate["card_id"],
                retrieval_similarity=float(candidate["retrieval_score"]),
                combined_score=float(candidate["score"]),
                expansion=expansion,
                field_paths=field_paths,
                controlled_values=controlled_values + " // " + "; ".join(candidate["availability"]) + " // " + limitation_note,
                evidence_type=join_values(values(claim.get("evidence_type"))),
                evidence_confidence=clean_text(claim.get("evidence_confidence")) or "",
                evidence_quote=snippet(quote or claim.get("claim_text"), 520),
                reason="Reusable/reference-model coding plus availability proxies (open package/reproducibility and model_not_available limitation).",
            )
        )
    return rows, candidates[:12], []


def load_all_inputs() -> dict[str, Any]:
    ensure_required_artifacts()
    cards = load_jsonl(CARD_INDEX_PATH)
    vectors = np.load(VECTOR_PATH)
    if vectors.shape[0] != len(cards):
        raise ValueError(f"Vector/card mismatch: vectors={vectors.shape[0]}, cards={len(cards)}")
    vectorizer = load_json(VECTORIZER_PATH)
    manifest = load_json(MANIFEST_PATH)
    studies = load_jsonl(DATA_DIR / "studies.jsonl")
    study_codes = dedupe_study_codes(load_jsonl(DATA_DIR / "study_codes.jsonl"))
    claims = load_jsonl(DATA_DIR / "claims.jsonl")
    limitations = load_jsonl(DATA_DIR / "limitations.jsonl")
    evidence_quotes = load_jsonl(DATA_DIR / "evidence_quotes.jsonl")
    kg = KGIndex(read_csv_rows(NODES_PATH), read_csv_rows(EDGES_PATH))
    return {
        "cards": cards,
        "vectors": vectors,
        "vectorizer": vectorizer,
        "manifest": manifest,
        "studies": studies,
        "studies_by_id": {str(study["study_id"]): study for study in studies},
        "study_codes": study_codes,
        "field_index": build_field_index(study_codes),
        "claims": claims,
        "claims_by_study": claims_by_study(claims),
        "claim_quotes": quote_by_claim(evidence_quotes),
        "limitations": limitations,
        "limitations_by_study": limitations_by_study(limitations),
        "kg": kg,
    }


def build_markdown_report(question_results: list[dict[str, Any]], all_source_rows: list[dict[str, Any]]) -> None:
    by_question: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_source_rows:
        by_question[row["question_id"]].append(row)

    lines = [
        "# E12 — GraphRAG demo questions over SLR1 evidence",
        "",
        "**Exploratory notice:** answers are generated by deterministic vector retrieval (`hashing_tfidf_v1`) plus controlled-code KG expansion and hand-coded ranking rules. They are not LLM-generated conclusions and should be checked against the cited extraction fields and original papers before use.",
        "",
        "## Retrieval and graph recipe",
        "",
        "1. Embed each question using the saved ISSUE-003 `hashing_tfidf_v1` vectorizer metadata and vector index.",
        "2. Retrieve top cards from question-specific unit types.",
        "3. Expand selected study/claim seeds over `kg/nodes.csv` and `kg/edges.csv` by one to two hops.",
        "4. Rank sources with transparent controlled-code features and preserve the full retrieval trace in `outputs/reports/retrieval_traces.jsonl`.",
        "",
    ]
    result_by_id = {result["question_id"]: result for result in question_results}

    q1_rows = by_question.get("q1_eps_pre_physical_verification", [])
    lines.extend(
        [
            "## 1. Which papers provide the strongest evidence for EPS pre-physical verification?",
            "",
            "In this corpus, the strongest EPS pre-physical verification evidence is generally **moderate** rather than strong: top sources combine EPS/power-budget relevance with simulation-in-the-loop, executable checks, parametric checks, trade-study verification, or trace-linked verification artifacts. Strong effort/cost claims are excluded from this ranking unless they are tied to EPS verification evidence.",
            "",
            markdown_table(
                q1_rows,
                ["answer_rank", "corpus_id", "study_title", "claim_id", "evidence_confidence", "evidence_type", "controlled_values"],
                max_rows=10,
            ),
            "",
        ]
    )

    q2_rows = by_question.get("q2_simulation_in_the_loop_toolchains", [])
    tool_counter: Counter[str] = Counter()
    for row in q2_rows:
        controlled = row.get("controlled_values", "")
        for segment in controlled.split(" // "):
            if segment.startswith(f"{TOOL_FIELD}="):
                for tool in segment.split("=", 1)[1].split("; "):
                    if tool.strip():
                        tool_counter[tool.strip()] += 1
    tool_rows = [{"tool": tool, "source_rows": count} for tool, count in tool_counter.most_common(12)]
    lines.extend(
        [
            "## 2. What toolchains support simulation-in-the-loop verification?",
            "",
            "The retrieved/expanded sources point to SysML-centered toolchains connected to simulation or analysis environments. Recurring support mechanisms are scripts, import/export, model transformations, plugins, co-simulation, and API-style links.",
            "",
            "### Top cited studies/toolchains",
            "",
            markdown_table(
                q2_rows,
                ["answer_rank", "corpus_id", "study_title", "controlled_values", "evidence_quote_or_snippet"],
                max_rows=12,
            ),
            "",
            "### Tool mentions among cited rows",
            "",
            markdown_table(tool_rows, ["tool", "source_rows"], max_rows=12),
            "",
        ]
    )

    q3_rows = by_question.get("q3_effort_reduction_baselines", [])
    baseline_counts = Counter(row.get("baseline_comparator", "") for row in q3_rows)
    baseline_rows = [{"baseline_comparator": key, "claim_count": value} for key, value in baseline_counts.most_common()]
    q3_top = sorted(q3_rows, key=lambda row: (-confidence_score(row.get("evidence_confidence")), row["answer_rank"]))[:14]
    lines.extend(
        [
            "## 3. Which claims about effort reduction have baseline comparators?",
            "",
            f"The extractor coded **{len(q3_rows)}** effort/schedule/cost/time-related claims with a non-empty baseline comparator. Most comparators are qualitative (`previous document-centric process` or `manual analysis`); only a small subset has quantitative comparison/counterfactual evidence.",
            "",
            "### Comparator distribution",
            "",
            markdown_table(baseline_rows, ["baseline_comparator", "claim_count"], max_rows=20),
            "",
            "### Highest-evidence examples",
            "",
            markdown_table(
                q3_top,
                ["answer_rank", "claim_id", "corpus_id", "baseline_comparator", "evidence_confidence", "evidence_type", "evidence_quote_or_snippet"],
                max_rows=14,
            ),
            "",
        ]
    )

    q4_rows = by_question.get("q4_reusable_reference_models", [])
    available_rows = [
        row
        for row in q4_rows
        if (
            "open package coded" in row.get("controlled_values", "")
            or "reproducibility/toolchain reported Yes" in row.get("controlled_values", "")
        )
        and "model_not_available limitation" not in row.get("controlled_values", "")
    ]
    lines.extend(
        [
            "## 4. Where are reusable reference models available?",
            "",
            "The clearest availability signals are rows coded as `open package` and/or with reproducibility/toolchain reporting of `Yes`. Many CubeSat System Reference Model/reference-template papers are important reuse candidates, but several are also flagged `model_not_available`; those should be treated as method/reference-model evidence rather than confirmed reusable artifacts.",
            "",
            "### Stronger availability candidates",
            "",
            markdown_table(
                available_rows or q4_rows,
                ["answer_rank", "corpus_id", "study_title", "controlled_values", "evidence_confidence", "evidence_quote_or_snippet"],
                max_rows=12,
            ),
            "",
            "### Full top reuse/reference-model source list",
            "",
            markdown_table(
                q4_rows,
                ["answer_rank", "corpus_id", "study_title", "claim_id", "controlled_values"],
                max_rows=12,
            ),
            "",
        ]
    )

    source_count_rows = [
        {"question_id": qid, "source_rows": len(rows), "top_retrieved_cards": len(result_by_id.get(qid, {}).get("trace", {}).get("top_cards", []))}
        for qid, rows in sorted(by_question.items())
    ]
    lines.extend(
        [
            "## Source and trace counts",
            "",
            markdown_table(source_count_rows, ["question_id", "source_rows", "top_retrieved_cards"], max_rows=10),
            "",
            "Detailed citations are in `outputs/tables/graphrag_answer_sources.csv`; retrieval traces are in `outputs/reports/retrieval_traces.jsonl`.",
        ]
    )
    write_text(REPORTS_DIR / "graphrag_demo_questions.md", "\n".join(lines))


def write_limitations_report(all_source_rows: list[dict[str, Any]], traces: list[dict[str, Any]]) -> None:
    counts_by_question = Counter(row["question_id"] for row in all_source_rows)
    unit_counts: Counter[str] = Counter()
    for trace in traces:
        for card in trace.get("top_cards", []):
            unit_counts[str(card.get("unit_type"))] += 1
    count_rows = [{"question_id": qid, "answer_source_rows": count} for qid, count in sorted(counts_by_question.items())]
    unit_rows = [{"unit_type": unit, "retrieved_top_card_mentions": count} for unit, count in unit_counts.most_common()]
    text = f"""# GraphRAG demo limitations and quality controls

This E12 demo is a local, deterministic GraphRAG-style retrieval exercise over the SLR1 extraction artifacts.

## What is controlled vs exploratory

- Controlled provenance comes from `data/*.jsonl` and `kg/nodes.csv` / `kg/edges.csv` generated from the source extraction.
- Retrieval uses `hashing_tfidf_v1`, a deterministic lexical TF-IDF hashing fallback, not a neural embedding model.
- Answer ranking uses transparent question-specific heuristics over retrieved cards and controlled fields.
- The generated answers are exploratory synthesis aids, not new coded SLR judgments.

## Counts

{markdown_table(count_rows, ["question_id", "answer_source_rows"], max_rows=10)}

{markdown_table(unit_rows, ["unit_type", "retrieved_top_card_mentions"], max_rows=10)}

## Caveats

- Lexical hashing retrieval can miss semantically relevant records if terminology differs from the question.
- KG expansion is one to two hops over the controlled-code property graph; it does not prove causal support among every connected node.
- Evidence quotes/snippets are extracted provenance snippets and may need verification against full papers.
- The corpus has 40 studies; no statistical significance is claimed.
- Availability of reusable artifacts is inferred from extraction fields such as `open package`, reproducibility reporting, and `model_not_available` flags; it is not a live artifact-access check.
"""
    write_text(REPORTS_DIR / "graphrag_limitations.md", text)


def main() -> None:
    data = load_all_inputs()
    kg: KGIndex = data["kg"]
    all_source_rows: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    question_results: list[dict[str, Any]] = []

    handlers = {
        "q1_eps_pre_physical_verification": q1_eps_pre_physical,
        "q2_simulation_in_the_loop_toolchains": q2_toolchains,
        "q3_effort_reduction_baselines": q3_effort_baselines,
        "q4_reusable_reference_models": q4_reusable_models,
    }

    for question_def in QUESTIONS:
        retrieved, trace_base = retrieve_cards(
            question_def["question"],
            question_def["unit_types"],
            data["cards"],
            data["vectors"],
            data["vectorizer"],
        )
        handler = handlers[question_def["id"]]
        source_rows, candidates, _extra = handler(data, retrieved, kg)
        all_source_rows.extend(source_rows)
        seed_nodes = []
        for row in source_rows[:12]:
            seed_nodes.extend([node for node in str(row.get("kg_seed_nodes", "")).split("; ") if node])
        trace = {
            "question_id": question_def["id"],
            "question": question_def["question"],
            "exploratory": True,
            "embedding_model": MODEL_NAME,
            "trace_note": "Question embedded with saved hashing_tfidf_v1 vectorizer metadata; top cards retrieved from relevant unit types; selected answer seeds expanded over KG by 1-2 hops.",
            **trace_base,
            "answer_source_count": len(source_rows),
            "selected_sources": [
                {
                    "answer_rank": row["answer_rank"],
                    "source_type": row["source_type"],
                    "corpus_id": row["corpus_id"],
                    "source_id": row["source_id"],
                    "claim_id": row["claim_id"],
                    "retrieval_similarity": row["retrieval_similarity"],
                    "combined_score": row["combined_score"],
                    "field_paths": row["field_paths"],
                    "snippet": snippet(row["evidence_quote_or_snippet"], 260),
                }
                for row in source_rows
            ],
            "kg_expansion_summary": kg.expand(seed_nodes[:24], max_hops=2, max_edges=160),
        }
        traces.append(trace)
        question_results.append({"question_id": question_def["id"], "trace": trace, "candidate_count": len(candidates)})

    write_csv(TABLES_DIR / "graphrag_answer_sources.csv", all_source_rows, ANSWER_SOURCE_COLUMNS)
    write_jsonl(REPORTS_DIR / "retrieval_traces.jsonl", traces)
    build_markdown_report(question_results, all_source_rows)
    write_limitations_report(all_source_rows, traces)

    print("GraphRAG demo complete (exploratory):")
    print(f"  answer_source_rows: {len(all_source_rows)}")
    for qid, count in sorted(Counter(row["question_id"] for row in all_source_rows).items()):
        print(f"  {qid}: {count}")
    print(f"  retrieval_traces: {len(traces)}")


if __name__ == "__main__":
    main()
