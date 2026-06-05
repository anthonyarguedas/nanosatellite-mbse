#!/usr/bin/env python3
"""Run exploratory semantic analyses E7-E10 over SLR1 embedding cards.

Dependency-light fallbacks are used intentionally: 2D study projection is PCA
via NumPy SVD, and clusters/audit queues are thresholded connected components
over deterministic hashing-TFIDF cosine similarities. Outputs are exploratory
review aids only and never automatic extraction corrections.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from kg_common import (
    BASE_DIR,
    DATA_DIR,
    FIGURES_DIR,
    REPORTS_DIR,
    TABLES_DIR,
    clean_text,
    dedupe_study_codes,
    ensure_dirs,
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
CARD_INDEX_PATH = EMBEDDINGS_DIR / "card_index.jsonl"
NEIGHBORS_PATH = EMBEDDINGS_DIR / "nearest_neighbors.jsonl"
MANIFEST_PATH = EMBEDDINGS_DIR / "embedding_manifest.json"

APPROACH_FIELD = "implementation_pathway_tailoring.approach_classification"
EPS_RELEVANCE_FIELD = "study_context_population.eps_relevance"
MODEL_MATURITY_FIELD = "study_context_population.model_maturity"
EPS_ELEMENTS_FIELD = "eps_verification_specific.eps_elements_modeled"
VERIFICATION_ARTIFACT_FIELD = "eps_verification_specific.verification_validation_artifacts"
VERIFICATION_MECHANISM_FIELD = "eps_verification_specific.pre_physical_development_verification_mechanism"
INTEGRATION_READINESS_FIELD = "eps_verification_specific.integration_test_readiness"
IVV_FIELD = "eps_verification_specific.ivv_integration_level"

CONTROLLED_STUDY_FIELDS = [APPROACH_FIELD, EPS_RELEVANCE_FIELD, MODEL_MATURITY_FIELD]
EPS_VERIFICATION_TEXT_FIELDS = [
    EPS_RELEVANCE_FIELD,
    EPS_ELEMENTS_FIELD,
    VERIFICATION_ARTIFACT_FIELD,
    VERIFICATION_MECHANISM_FIELD,
    INTEGRATION_READINESS_FIELD,
]

STUDY_CLUSTER_THRESHOLD = 0.65
STUDY_DISAGREEMENT_THRESHOLD = 0.60
STUDY_APPROACH_AUDIT_THRESHOLD = 0.65
CLAIM_CLUSTER_THRESHOLD = 0.55
CLAIM_AUDIT_THRESHOLD = 0.55
EMERGENT_CLUSTER_THRESHOLD = 0.55
EPS_IVV_AUDIT_THRESHOLD = 0.50
MAX_AUDIT_ROWS_PER_TYPE = 40

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._+#/\-][a-z0-9]+)*", re.IGNORECASE)
WEAK_OR_UNSUPPORTED = {"Weak", "Unsupported"}

STUDY_CLUSTER_COLUMNS = [
    "cluster_id",
    "cluster_size",
    "study_id",
    "card_id",
    "title",
    "year",
    "tier",
    "approach_classification",
    "eps_relevance",
    "model_maturity",
    "dominant_approach_classification",
    "dominant_eps_relevance",
    "dominant_model_maturity",
    "representative_study_id",
    "representative_title",
    "similarity_to_representative",
    "nearest_neighbor_study_id",
    "nearest_neighbor_title",
    "nearest_neighbor_similarity",
    "cluster_threshold",
    "method",
    "exploratory",
]

STUDY_PROJECTION_COLUMNS = [
    "study_id",
    "card_id",
    "title",
    "x",
    "y",
    "cluster_id",
    "approach_classification",
    "eps_relevance",
    "model_maturity",
    "projection_method",
    "exploratory",
]

CLAIM_CLUSTER_COLUMNS = [
    "cluster_id",
    "cluster_size",
    "claim_id",
    "study_id",
    "outcome_categories",
    "mbse_mechanisms",
    "evidence_confidence",
    "evidence_types",
    "dominant_outcome_category",
    "dominant_mbse_mechanism",
    "dominant_evidence_confidence",
    "weak_or_unsupported_cluster_count",
    "representative_claim_id",
    "similarity_to_representative",
    "claim_text",
    "evidence_quote",
    "cluster_threshold",
    "method",
    "exploratory",
]

EMERGENT_CLUSTER_COLUMNS = [
    "cluster_id",
    "cluster_size",
    "emergent_code_id",
    "study_id",
    "label",
    "original_label",
    "category",
    "field_path",
    "representative_emergent_code_id",
    "similarity_to_representative",
    "max_pair_similarity_in_cluster",
    "cluster_labels",
    "duplicate_or_near_duplicate_candidate",
    "candidate_codebook_extension",
    "description",
    "rationale",
    "evidence_quote",
    "cluster_threshold",
    "method",
    "exploratory",
]

AUDIT_COLUMNS = [
    "audit_id",
    "audit_type",
    "priority",
    "similarity_score",
    "similarity_method",
    "unit_type",
    "id_1",
    "id_2",
    "study_id_1",
    "study_id_2",
    "differing_controlled_fields",
    "field_value_1",
    "field_value_2",
    "snippet_1",
    "snippet_2",
    "evidence_or_provenance_1",
    "evidence_or_provenance_2",
    "recommended_action",
    "exploratory",
]


class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if ra < rb:
            self.parent[rb] = ra
        else:
            self.parent[ra] = rb


def require_paths(paths: Iterable[Path], issue_hint: str) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        missing_text = ", ".join(str(path.relative_to(BASE_DIR)) for path in missing)
        raise FileNotFoundError(f"Missing required {issue_hint} artifact(s): {missing_text}. Run the earlier issue scripts first.")


def snippet(value: Any, max_chars: int = 220) -> str:
    text = clean_text(value) or ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def normalize_for_tokenization(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\biv\s*&\s*v\b", "ivv", lowered)
    lowered = re.sub(r"\bi\s*/\s*v\s*/\s*v\b", "ivv", lowered)
    lowered = re.sub(r"\bi\s*-\s*v\s*-\s*v\b", "ivv", lowered)
    return lowered


def tokenize(text: Any) -> list[str]:
    return TOKEN_RE.findall(normalize_for_tokenization(clean_text(text) or ""))


def simple_tfidf_cosine(texts: list[str]) -> np.ndarray:
    """Small deterministic TF-IDF cosine matrix for EPS-only audit text."""
    counts = [Counter(tokenize(text)) for text in texts]
    df: Counter[str] = Counter()
    for counter in counts:
        df.update(counter.keys())
    vocab = sorted(df)
    if not texts or not vocab:
        return np.zeros((len(texts), len(texts)), dtype=np.float32)
    index = {token: idx for idx, token in enumerate(vocab)}
    n = len(texts)
    vectors_matrix = np.zeros((n, len(vocab)), dtype=np.float32)
    for row, counter in enumerate(counts):
        for token, tf in counter.items():
            idf = math.log((1.0 + n) / (1.0 + df[token])) + 1.0
            vectors_matrix[row, index[token]] = np.float32((1.0 + math.log(float(tf))) * idf)
        norm = float(np.linalg.norm(vectors_matrix[row]))
        if norm > 0.0:
            vectors_matrix[row] /= norm
    return vectors_matrix @ vectors_matrix.T


def load_inputs() -> dict[str, Any]:
    require_paths(
        [
            DATA_DIR / "studies.jsonl",
            DATA_DIR / "study_codes.jsonl",
            DATA_DIR / "claims.jsonl",
            DATA_DIR / "emergent_codes.jsonl",
            DATA_DIR / "evidence_quotes.jsonl",
            CARD_INDEX_PATH,
            VECTOR_PATH,
            NEIGHBORS_PATH,
            MANIFEST_PATH,
        ],
        "ISSUE-001/ISSUE-003",
    )
    ensure_dirs(TABLES_DIR, REPORTS_DIR, FIGURES_DIR)

    cards = load_jsonl(CARD_INDEX_PATH)
    vectors_matrix = np.load(VECTOR_PATH)
    if vectors_matrix.shape[0] != len(cards):
        raise ValueError(
            f"Vector/card mismatch: {vectors_matrix.shape[0]} vectors for {len(cards)} cards. "
            "Regenerate ISSUE-003 embedding artifacts."
        )
    cards_by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for position, card in enumerate(cards):
        card["_vector_index"] = int(card.get("card_index", position))
        cards_by_type[str(card.get("unit_type"))].append(card)
    for unit_cards in cards_by_type.values():
        unit_cards.sort(key=lambda row: (int(row.get("_vector_index", 0)), str(row.get("card_id"))))

    study_codes = dedupe_study_codes(load_jsonl(DATA_DIR / "study_codes.jsonl"))
    return {
        "studies": load_jsonl(DATA_DIR / "studies.jsonl"),
        "study_codes": study_codes,
        "claims": load_jsonl(DATA_DIR / "claims.jsonl"),
        "emergent_codes": load_jsonl(DATA_DIR / "emergent_codes.jsonl"),
        "evidence_quotes": load_jsonl(DATA_DIR / "evidence_quotes.jsonl"),
        "cards_by_type": dict(cards_by_type),
        "vectors": vectors_matrix,
    }


def vector_slice(cards: list[dict[str, Any]], vectors_matrix: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(vectors_matrix[[int(card["_vector_index"]) for card in cards]])


def similarity_matrix(cards: list[dict[str, Any]], vectors_matrix: np.ndarray) -> np.ndarray:
    vectors_for_cards = vector_slice(cards, vectors_matrix)
    return vectors_for_cards @ vectors_for_cards.T


def threshold_components(
    cards: list[dict[str, Any]], similarity: np.ndarray, threshold: float, prefix: str
) -> tuple[dict[int, str], dict[str, list[int]]]:
    n = len(cards)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if float(similarity[i, j]) >= threshold:
                uf.union(i, j)
    raw_groups: dict[int, list[int]] = defaultdict(list)
    for i in range(n):
        raw_groups[uf.find(i)].append(i)
    ordered_groups = sorted(
        raw_groups.values(),
        key=lambda group: (-len(group), min(str(cards[idx].get("card_id")) for idx in group)),
    )
    assignment: dict[int, str] = {}
    groups: dict[str, list[int]] = {}
    for group_number, group in enumerate(ordered_groups, start=1):
        cluster_id = f"{prefix}_{group_number:03d}"
        groups[cluster_id] = sorted(group, key=lambda idx: str(cards[idx].get("card_id")))
        for idx in group:
            assignment[idx] = cluster_id
    return assignment, groups


def representative_index(group: list[int], cards: list[dict[str, Any]], similarity: np.ndarray) -> int:
    if len(group) == 1:
        return group[0]
    scored = []
    for idx in group:
        other_scores = [float(similarity[idx, other]) for other in group if other != idx]
        mean_similarity = sum(other_scores) / len(other_scores) if other_scores else 1.0
        scored.append((mean_similarity, str(cards[idx].get("card_id")), idx))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[0][2]


def max_pair_similarity(group: list[int], similarity: np.ndarray) -> float:
    if len(group) < 2:
        return 1.0
    return max(float(similarity[i, j]) for pos, i in enumerate(group) for j in group[pos + 1 :])


def field_index(study_codes: Iterable[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in study_codes:
        study_id = clean_text(record.get("study_id"))
        field_path = clean_text(record.get("field_path"))
        value = clean_text(record.get("value"))
        if not study_id or not field_path or value is None:
            continue
        out[study_id][field_path].append(record)
    return {study_id: dict(fields) for study_id, fields in out.items()}


def field_values(index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_path: str) -> list[str]:
    return unique_preserve(
        value
        for value in (clean_text(record.get("value")) for record in index.get(study_id, {}).get(field_path, []))
        if value
    )


def joined_field(index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_path: str) -> str:
    return join_values(field_values(index, study_id, field_path))


def field_provenance(index: dict[str, dict[str, list[dict[str, Any]]]], study_id: str, field_paths: Iterable[str]) -> str:
    parts: list[str] = []
    for field_path in field_paths:
        records = index.get(study_id, {}).get(field_path, [])
        values_out = field_values(index, study_id, field_path)
        source_paths = unique_preserve(
            text for text in (clean_text(record.get("source_path")) for record in records) if text
        )
        quotes = unique_preserve(
            text for text in (clean_text(record.get("evidence_quote")) for record in records) if text
        )
        rationales = unique_preserve(
            text for text in (clean_text(record.get("rationale")) for record in records) if text
        )
        if values_out or source_paths or quotes or rationales:
            parts.append(
                f"{field_path}: values={join_values(values_out)}; "
                f"source_paths={join_values(source_paths)}; "
                f"rationale={snippet(' | '.join(rationales), 180)}; "
                f"evidence={snippet(' | '.join(quotes), 220)}"
            )
    return " || ".join(part for part in parts if part.strip())


def dominant(items: Iterable[Any], default: str = "not reported") -> str:
    vals = [clean_text(item) for item in items]
    vals = [item for item in vals if item]
    if not vals:
        return default
    counts = Counter(vals)
    top_count = counts.most_common(1)[0][1]
    top_labels = sorted(label for label, count in counts.items() if count == top_count)
    return "; ".join(top_labels)


def value_counter_summary(items: Iterable[Any], max_items: int = 5) -> str:
    vals = [clean_text(item) for item in items]
    counts = Counter(item for item in vals if item)
    return "; ".join(f"{label} ({count})" for label, count in counts.most_common(max_items))


def claim_quote(claim_card: dict[str, Any]) -> str:
    metadata = claim_card.get("metadata", {}) if isinstance(claim_card.get("metadata"), dict) else {}
    quotes = metadata.get("linked_evidence_quotes") or []
    if isinstance(quotes, list) and quotes:
        return snippet(" | ".join(str(quote) for quote in quotes if clean_text(quote)), 500)
    claim = metadata.get("source_record") or {}
    return snippet(claim.get("evidence_source") or claim.get("observed_effect") or "", 500)


def pca_svd_2d(vectors_for_cards: np.ndarray) -> np.ndarray:
    if vectors_for_cards.shape[0] == 0:
        return np.zeros((0, 2), dtype=np.float32)
    if vectors_for_cards.shape[0] == 1:
        return np.zeros((1, 2), dtype=np.float32)
    centered = vectors_for_cards - vectors_for_cards.mean(axis=0, keepdims=True)
    u, singular_values, vt = np.linalg.svd(centered, full_matrices=False)
    dims = min(2, u.shape[1])
    coords = u[:, :dims] * singular_values[:dims]
    # Deterministic sign convention: orient by the loading with largest magnitude.
    for col in range(dims):
        loading = vt[col]
        pivot = int(np.argmax(np.abs(loading)))
        if loading[pivot] < 0:
            coords[:, col] *= -1
    if dims < 2:
        coords = np.column_stack([coords[:, 0], np.zeros(coords.shape[0], dtype=coords.dtype)])
    return coords.astype(np.float32)


def write_study_svg(rows: list[dict[str, Any]], path: Path) -> None:
    width = 980
    height = 720
    margin = 80
    xs = [float(row["x"]) for row in rows]
    ys = [float(row["y"]) for row in rows]
    min_x, max_x = (min(xs), max(xs)) if xs else (0.0, 1.0)
    min_y, max_y = (min(ys), max(ys)) if ys else (0.0, 1.0)
    if math.isclose(min_x, max_x):
        min_x -= 1.0
        max_x += 1.0
    if math.isclose(min_y, max_y):
        min_y -= 1.0
        max_y += 1.0

    approaches = sorted({row.get("approach_classification") or "not reported" for row in rows})
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
    colors = {approach: palette[idx % len(palette)] for idx, approach in enumerate(approaches)}

    def sx(x: float) -> float:
        return margin + (x - min_x) / (max_x - min_x) * (width - 2 * margin)

    def sy(y: float) -> float:
        return height - margin - (y - min_y) / (max_y - min_y) * (height - 2 * margin)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<title>Exploratory study PCA/SVD projection (UMAP fallback)</title>",
        "<desc>Dependency-light PCA/SVD fallback for intended UMAP output; points are colored by approach classification.</desc>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{margin}" y="34" font-family="sans-serif" font-size="20" font-weight="bold">E7 study semantic projection</text>',
        f'<text x="{margin}" y="58" font-family="sans-serif" font-size="13">PCA/SVD fallback for UMAP; hashing_tfidf_v1; exploratory audit aid only.</text>',
        f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#999" stroke-width="1"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#999" stroke-width="1"/>',
        f'<text x="{width / 2 - 30:.1f}" y="{height - 24}" font-family="sans-serif" font-size="12">PC1</text>',
        f'<text x="20" y="{height / 2:.1f}" font-family="sans-serif" font-size="12" transform="rotate(-90 20 {height / 2:.1f})">PC2</text>',
    ]
    for row in rows:
        approach = row.get("approach_classification") or "not reported"
        x = sx(float(row["x"]))
        y = sy(float(row["y"]))
        radius = 5.5 + min(4.0, max(0, int(str(row.get("cluster_id", "").split("_")[-1] or 0)) * 0.0))
        lines.extend(
            [
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.1f}" fill="{colors[approach]}" fill-opacity="0.82" stroke="#333" stroke-width="0.6">',
                f'<title>{escape(str(row.get("study_id")))} — {escape(str(row.get("title")))}; approach={escape(approach)}; EPS={escape(str(row.get("eps_relevance") or ""))}</title>',
                "</circle>",
                f'<text x="{x + 7:.2f}" y="{y + 4:.2f}" font-family="sans-serif" font-size="9" fill="#333">{escape(str(row.get("study_id")))}</text>',
            ]
        )
    legend_x = width - 310
    legend_y = 90
    lines.append(f'<text x="{legend_x}" y="{legend_y - 18}" font-family="sans-serif" font-size="12" font-weight="bold">Approach classification</text>')
    for idx, approach in enumerate(approaches):
        y = legend_y + idx * 20
        lines.append(f'<rect x="{legend_x}" y="{y - 10}" width="12" height="12" fill="{colors[approach]}"/>')
        lines.append(f'<text x="{legend_x + 18}" y="{y}" font-family="sans-serif" font-size="11">{escape(approach)}</text>')
    lines.append("</svg>")
    write_text(path, "\n".join(lines))


def study_metadata_rows(
    study_cards: list[dict[str, Any]],
    studies_by_id: dict[str, dict[str, Any]],
    fields: dict[str, dict[str, list[dict[str, Any]]]],
) -> list[dict[str, Any]]:
    rows = []
    for card in study_cards:
        study_id = str(card.get("study_id"))
        study = studies_by_id.get(study_id, {})
        rows.append(
            {
                "study_id": study_id,
                "card_id": card.get("card_id"),
                "title": clean_text(card.get("title") or card.get("label") or study.get("title")) or study_id,
                "year": study.get("year"),
                "tier": study.get("tier"),
                "approach_classification": joined_field(fields, study_id, APPROACH_FIELD),
                "eps_relevance": joined_field(fields, study_id, EPS_RELEVANCE_FIELD),
                "model_maturity": joined_field(fields, study_id, MODEL_MATURITY_FIELD),
            }
        )
    return rows


def run_e7(data: dict[str, Any], fields: dict[str, dict[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    study_cards = data["cards_by_type"].get("study_card", [])
    studies_by_id = {str(study["study_id"]): study for study in data["studies"]}
    sim = similarity_matrix(study_cards, data["vectors"])
    assignment, groups = threshold_components(study_cards, sim, STUDY_CLUSTER_THRESHOLD, "study_cluster")
    metadata_rows = study_metadata_rows(study_cards, studies_by_id, fields)
    metadata_by_index = {idx: row for idx, row in enumerate(metadata_rows)}

    reps = {cluster_id: representative_index(group, study_cards, sim) for cluster_id, group in groups.items()}
    def dominant_study_field(group: list[int], field_path: str) -> str:
        vals: list[str] = []
        for group_idx in group:
            vals.extend(field_values(fields, metadata_by_index[group_idx]["study_id"], field_path))
        return dominant(vals)

    cluster_dominants: dict[str, dict[str, str]] = {}
    for cluster_id, group in groups.items():
        cluster_dominants[cluster_id] = {
            "approach": dominant_study_field(group, APPROACH_FIELD),
            "eps": dominant_study_field(group, EPS_RELEVANCE_FIELD),
            "maturity": dominant_study_field(group, MODEL_MATURITY_FIELD),
        }

    cluster_rows: list[dict[str, Any]] = []
    for idx, card in enumerate(study_cards):
        cluster_id = assignment[idx]
        group = groups[cluster_id]
        rep_idx = reps[cluster_id]
        row_meta = metadata_by_index[idx]
        nearest_idx = None
        nearest_score = -1.0
        for other_idx in range(len(study_cards)):
            if other_idx == idx:
                continue
            score = float(sim[idx, other_idx])
            if score > nearest_score or (
                math.isclose(score, nearest_score) and str(study_cards[other_idx].get("card_id")) < str(study_cards[nearest_idx].get("card_id")) if nearest_idx is not None else True
            ):
                nearest_idx = other_idx
                nearest_score = score
        nearest_meta = metadata_by_index.get(nearest_idx or 0, {})
        rep_meta = metadata_by_index[rep_idx]
        dom = cluster_dominants[cluster_id]
        cluster_rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": len(group),
                "study_id": row_meta["study_id"],
                "card_id": row_meta["card_id"],
                "title": row_meta["title"],
                "year": row_meta.get("year"),
                "tier": row_meta.get("tier"),
                "approach_classification": row_meta.get("approach_classification"),
                "eps_relevance": row_meta.get("eps_relevance"),
                "model_maturity": row_meta.get("model_maturity"),
                "dominant_approach_classification": dom["approach"],
                "dominant_eps_relevance": dom["eps"],
                "dominant_model_maturity": dom["maturity"],
                "representative_study_id": rep_meta["study_id"],
                "representative_title": rep_meta["title"],
                "similarity_to_representative": f"{float(sim[idx, rep_idx]):.6f}",
                "nearest_neighbor_study_id": nearest_meta.get("study_id", ""),
                "nearest_neighbor_title": nearest_meta.get("title", ""),
                "nearest_neighbor_similarity": f"{nearest_score:.6f}" if nearest_score >= 0 else "",
                "cluster_threshold": STUDY_CLUSTER_THRESHOLD,
                "method": "thresholded connected components over hashing_tfidf_v1 cosine",
                "exploratory": True,
            }
        )
    cluster_rows.sort(key=lambda row: (row["cluster_id"], row["study_id"]))
    write_csv(TABLES_DIR / "study_clusters.csv", cluster_rows, STUDY_CLUSTER_COLUMNS)

    coords = pca_svd_2d(vector_slice(study_cards, data["vectors"]))
    projection_rows: list[dict[str, Any]] = []
    for idx, row_meta in enumerate(metadata_rows):
        projection_rows.append(
            {
                "study_id": row_meta["study_id"],
                "card_id": row_meta["card_id"],
                "title": row_meta["title"],
                "x": f"{float(coords[idx, 0]):.8f}",
                "y": f"{float(coords[idx, 1]):.8f}",
                "cluster_id": assignment[idx],
                "approach_classification": row_meta.get("approach_classification"),
                "eps_relevance": row_meta.get("eps_relevance"),
                "model_maturity": row_meta.get("model_maturity"),
                "projection_method": "PCA/SVD fallback for intended UMAP output",
                "exploratory": True,
            }
        )
    projection_rows.sort(key=lambda row: row["study_id"])
    write_csv(TABLES_DIR / "study_projection.csv", projection_rows, STUDY_PROJECTION_COLUMNS)
    write_study_svg(projection_rows, FIGURES_DIR / "study_umap.svg")

    disagreement_rows: list[dict[str, Any]] = []
    for i in range(len(study_cards)):
        for j in range(i + 1, len(study_cards)):
            score = float(sim[i, j])
            if score < STUDY_DISAGREEMENT_THRESHOLD:
                continue
            diffs = []
            for label, key in [
                ("approach_classification", "approach_classification"),
                ("eps_relevance", "eps_relevance"),
                ("model_maturity", "model_maturity"),
            ]:
                left = clean_text(metadata_by_index[i].get(key)) or "not reported"
                right = clean_text(metadata_by_index[j].get(key)) or "not reported"
                if left != right:
                    diffs.append(f"{label}: {left} vs {right}")
            if diffs:
                disagreement_rows.append(
                    {
                        "similarity": f"{score:.6f}",
                        "study_id_1": metadata_by_index[i]["study_id"],
                        "study_id_2": metadata_by_index[j]["study_id"],
                        "differing_controlled_labels": " | ".join(diffs),
                        "title_1": metadata_by_index[i]["title"],
                        "title_2": metadata_by_index[j]["title"],
                    }
                )
    disagreement_rows.sort(key=lambda row: (-float(row["similarity"]), row["study_id_1"], row["study_id_2"]))

    summary_rows = []
    for cluster_id, group in groups.items():
        rep = metadata_by_index[reps[cluster_id]]
        summary_rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": len(group),
                "representative_study_id": rep["study_id"],
                "dominant_approach_classification": cluster_dominants[cluster_id]["approach"],
                "dominant_eps_relevance": cluster_dominants[cluster_id]["eps"],
                "dominant_model_maturity": cluster_dominants[cluster_id]["maturity"],
                "study_ids": "; ".join(sorted(metadata_by_index[idx]["study_id"] for idx in group)),
            }
        )
    summary_rows.sort(key=lambda row: (-int(row["cluster_size"]), row["cluster_id"]))
    multi_study_clusters = sum(1 for group in groups.values() if len(group) > 1)

    report = f"""# E7 — Study semantic clustering

**Exploratory notice:** clusters and disagreements are generated from the deterministic `{MODEL_NAME}` hashing-TFIDF fallback and are audit aids only.

## Method

- Projection: PCA via `numpy.linalg.svd` as a dependency-light fallback for the intended UMAP output. The SVG is still named `study_umap.svg` for the planned artifact, but its metadata and this report identify it as PCA/SVD fallback.
- Clustering: thresholded connected components over same-unit study-card cosine similarities.
- Study cluster threshold: `{STUDY_CLUSTER_THRESHOLD}`.
- Disagreement-list threshold: `{STUDY_DISAGREEMENT_THRESHOLD}`.

Study cards: **{len(study_cards)}**. Clusters: **{len(groups)}** total; **{multi_study_clusters}** multi-study clusters.

## Cluster summaries

{markdown_table(summary_rows, ["cluster_id", "cluster_size", "representative_study_id", "dominant_approach_classification", "dominant_eps_relevance", "dominant_model_maturity", "study_ids"], max_rows=25)}

## Semantically similar studies with different controlled labels

{markdown_table(disagreement_rows, ["similarity", "study_id_1", "study_id_2", "differing_controlled_labels"], max_rows=25)}

Outputs: `outputs/tables/study_clusters.csv`, `outputs/tables/study_projection.csv`, and `outputs/figures/study_umap.svg`.
"""
    write_text(REPORTS_DIR / "e7_study_semantic_clustering.md", report)
    return {
        "study_cluster_count": len(groups),
        "study_multi_cluster_count": multi_study_clusters,
        "study_disagreement_count": len(disagreement_rows),
    }


def run_e8(data: dict[str, Any]) -> dict[str, Any]:
    claim_cards = data["cards_by_type"].get("claim_card", [])
    claims_by_id = {str(claim["claim_id"]): claim for claim in data["claims"]}
    sim = similarity_matrix(claim_cards, data["vectors"])
    assignment, groups = threshold_components(claim_cards, sim, CLAIM_CLUSTER_THRESHOLD, "claim_cluster")
    reps = {cluster_id: representative_index(group, claim_cards, sim) for cluster_id, group in groups.items()}

    cluster_stats: dict[str, dict[str, Any]] = {}
    for cluster_id, group in groups.items():
        outcomes = []
        mechanisms = []
        confidences = []
        evidence_types = []
        for idx in group:
            claim = claims_by_id.get(str(claim_cards[idx].get("claim_id")), {})
            outcomes.extend(values(claim.get("outcome_category")))
            mechanisms.extend(values(claim.get("mbse_mechanism")))
            confidences.append(clean_text(claim.get("evidence_confidence")) or "not reported")
            evidence_types.extend(values(claim.get("evidence_type")))
        cluster_stats[cluster_id] = {
            "dominant_outcome": dominant(outcomes),
            "dominant_mechanism": dominant(mechanisms),
            "dominant_confidence": dominant(confidences),
            "weak_count": sum(1 for confidence in confidences if confidence in WEAK_OR_UNSUPPORTED),
            "outcome_summary": value_counter_summary(outcomes),
            "mechanism_summary": value_counter_summary(mechanisms),
            "confidence_summary": value_counter_summary(confidences),
            "evidence_summary": value_counter_summary(evidence_types),
        }

    rows: list[dict[str, Any]] = []
    for idx, card in enumerate(claim_cards):
        claim_id = str(card.get("claim_id"))
        claim = claims_by_id.get(claim_id, {})
        cluster_id = assignment[idx]
        rep_idx = reps[cluster_id]
        rep_card = claim_cards[rep_idx]
        stats = cluster_stats[cluster_id]
        rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": len(groups[cluster_id]),
                "claim_id": claim_id,
                "study_id": card.get("study_id"),
                "outcome_categories": join_values(values(claim.get("outcome_category"))),
                "mbse_mechanisms": join_values(values(claim.get("mbse_mechanism"))),
                "evidence_confidence": clean_text(claim.get("evidence_confidence")) or "not reported",
                "evidence_types": join_values(values(claim.get("evidence_type"))),
                "dominant_outcome_category": stats["dominant_outcome"],
                "dominant_mbse_mechanism": stats["dominant_mechanism"],
                "dominant_evidence_confidence": stats["dominant_confidence"],
                "weak_or_unsupported_cluster_count": stats["weak_count"],
                "representative_claim_id": rep_card.get("claim_id"),
                "similarity_to_representative": f"{float(sim[idx, rep_idx]):.6f}",
                "claim_text": clean_text(claim.get("claim_text")) or card.get("label"),
                "evidence_quote": claim_quote(card),
                "cluster_threshold": CLAIM_CLUSTER_THRESHOLD,
                "method": "thresholded connected components over hashing_tfidf_v1 cosine",
                "exploratory": True,
            }
        )
    rows.sort(key=lambda row: (row["cluster_id"], row["claim_id"]))
    write_csv(TABLES_DIR / "claim_clusters.csv", rows, CLAIM_CLUSTER_COLUMNS)

    summary_rows = []
    weak_recurrent_rows = []
    for cluster_id, group in groups.items():
        rep_card = claim_cards[reps[cluster_id]]
        stats = cluster_stats[cluster_id]
        claim_ids = sorted(str(claim_cards[idx].get("claim_id")) for idx in group)
        study_ids = sorted({str(claim_cards[idx].get("study_id")) for idx in group})
        representative_claim = claims_by_id.get(str(rep_card.get("claim_id")), {})
        summary = {
            "cluster_id": cluster_id,
            "cluster_size": len(group),
            "representative_claim_id": rep_card.get("claim_id"),
            "dominant_outcome_category": stats["dominant_outcome"],
            "dominant_mbse_mechanism": stats["dominant_mechanism"],
            "dominant_evidence_confidence": stats["dominant_confidence"],
            "weak_or_unsupported_claims": stats["weak_count"],
            "evidence_confidence_distribution": stats["confidence_summary"],
            "study_ids": "; ".join(study_ids),
            "claim_ids": "; ".join(claim_ids),
            "representative_claim_text": snippet(representative_claim.get("claim_text") or rep_card.get("label"), 240),
        }
        summary_rows.append(summary)
        if len(group) >= 2 and stats["weak_count"] > 0:
            weak_recurrent_rows.append(summary)
    summary_rows.sort(key=lambda row: (-int(row["cluster_size"]), -int(row["weak_or_unsupported_claims"]), row["cluster_id"]))
    weak_recurrent_rows.sort(key=lambda row: (-int(row["weak_or_unsupported_claims"]), -int(row["cluster_size"]), row["cluster_id"]))

    weak_report = f"""# Weak recurrent claims — E8 exploratory audit

Clusters below contain at least two semantically similar claim cards and at least one `Weak` or `Unsupported` evidence-confidence rating. These are recurring benefit narratives for review, not corrections.

{markdown_table(weak_recurrent_rows, ["cluster_id", "cluster_size", "weak_or_unsupported_claims", "dominant_outcome_category", "dominant_mbse_mechanism", "evidence_confidence_distribution", "claim_ids"], max_rows=30)}
"""
    write_text(REPORTS_DIR / "weak_recurrent_claims.md", weak_report)

    report = f"""# E8 — Claim semantic clustering

**Exploratory notice:** claim clusters are generated from `{MODEL_NAME}` hashing-TFIDF vectors and thresholded connected components. They identify candidate recurrent narratives, not validated claim families.

Claim cards: **{len(claim_cards)}**. Clusters: **{len(groups)}**. Multi-claim clusters: **{sum(1 for group in groups.values() if len(group) > 1)}**.
Cluster threshold: `{CLAIM_CLUSTER_THRESHOLD}`.

## Cluster summaries by dominant outcome, mechanism, and evidence confidence

{markdown_table(summary_rows, ["cluster_id", "cluster_size", "representative_claim_id", "dominant_outcome_category", "dominant_mbse_mechanism", "dominant_evidence_confidence", "weak_or_unsupported_claims", "claim_ids"], max_rows=30)}

## Weakly supported recurrent narratives

See `outputs/reports/weak_recurrent_claims.md`. Top entries:

{markdown_table(weak_recurrent_rows, ["cluster_id", "cluster_size", "weak_or_unsupported_claims", "dominant_outcome_category", "dominant_mbse_mechanism"], max_rows=12)}
"""
    write_text(REPORTS_DIR / "e8_claim_semantic_clustering.md", report)
    return {
        "claim_cluster_count": len(groups),
        "claim_multi_cluster_count": sum(1 for group in groups.values() if len(group) > 1),
        "weak_recurrent_claim_cluster_count": len(weak_recurrent_rows),
    }


def run_e9(data: dict[str, Any]) -> dict[str, Any]:
    emergent_cards = data["cards_by_type"].get("emergent_code_card", [])
    emergent_by_id = {str(code["emergent_code_id"]): code for code in data["emergent_codes"]}
    sim = similarity_matrix(emergent_cards, data["vectors"])
    assignment, groups = threshold_components(emergent_cards, sim, EMERGENT_CLUSTER_THRESHOLD, "emergent_cluster")
    reps = {cluster_id: representative_index(group, emergent_cards, sim) for cluster_id, group in groups.items()}

    rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    for cluster_id, group in groups.items():
        rep_idx = reps[cluster_id]
        rep_code_id = str(emergent_cards[rep_idx].get("card_id", "")).replace("emergent_code_card::", "")
        labels = []
        fields = []
        descriptions = []
        for idx in group:
            code_id = str(emergent_cards[idx].get("card_id", "")).replace("emergent_code_card::", "")
            code = emergent_by_id.get(code_id, {})
            labels.append(clean_text(code.get("label")) or clean_text(emergent_cards[idx].get("label")) or code_id)
            fields.append(clean_text(code.get("field_path")) or "not reported")
            descriptions.append(clean_text(code.get("description")) or "")
        cluster_labels = join_values(labels)
        max_similarity = max_pair_similarity(group, sim)
        duplicate_candidate = len(group) >= 2
        extension = dominant(labels)
        for idx in group:
            code_id = str(emergent_cards[idx].get("card_id", "")).replace("emergent_code_card::", "")
            code = emergent_by_id.get(code_id, {})
            row = {
                "cluster_id": cluster_id,
                "cluster_size": len(group),
                "emergent_code_id": code_id,
                "study_id": emergent_cards[idx].get("study_id"),
                "label": clean_text(code.get("label")) or emergent_cards[idx].get("label"),
                "original_label": clean_text(code.get("original_label")) or "",
                "category": clean_text(code.get("category")) or "",
                "field_path": clean_text(code.get("field_path")) or "",
                "representative_emergent_code_id": rep_code_id,
                "similarity_to_representative": f"{float(sim[idx, rep_idx]):.6f}",
                "max_pair_similarity_in_cluster": f"{max_similarity:.6f}",
                "cluster_labels": cluster_labels,
                "duplicate_or_near_duplicate_candidate": duplicate_candidate,
                "candidate_codebook_extension": extension,
                "description": clean_text(code.get("description")) or "",
                "rationale": clean_text(code.get("rationale")) or "",
                "evidence_quote": clean_text(code.get("evidence_quote")) or "",
                "cluster_threshold": EMERGENT_CLUSTER_THRESHOLD,
                "method": "thresholded connected components over hashing_tfidf_v1 cosine",
                "exploratory": True,
            }
            rows.append(row)
        if duplicate_candidate:
            candidate_rows.append(
                {
                    "cluster_id": cluster_id,
                    "cluster_size": len(group),
                    "max_pair_similarity": f"{max_similarity:.6f}",
                    "candidate_codebook_extension": extension,
                    "labels": cluster_labels,
                    "field_paths": join_values(fields),
                    "emergent_code_ids": "; ".join(
                        sorted(str(emergent_cards[idx].get("card_id", "")).replace("emergent_code_card::", "") for idx in group)
                    ),
                    "description_snippets": snippet(" | ".join(descriptions), 360),
                }
            )
    rows.sort(key=lambda row: (row["cluster_id"], row["emergent_code_id"]))
    candidate_rows.sort(key=lambda row: (-int(row["cluster_size"]), -float(row["max_pair_similarity"]), row["cluster_id"]))
    write_csv(TABLES_DIR / "emergent_code_clusters.csv", rows, EMERGENT_CLUSTER_COLUMNS)

    report = f"""# E9 — Candidate codebook extensions and emergent-code consolidation

**Exploratory notice:** near-duplicate/consolidation candidates are generated from `{MODEL_NAME}` hashing-TFIDF vectors and thresholded connected components. They are suggestions for codebook review only.

Emergent-code cards: **{len(emergent_cards)}**. Clusters: **{len(groups)}**. Candidate duplicate/near-duplicate clusters: **{len(candidate_rows)}**.
Cluster threshold: `{EMERGENT_CLUSTER_THRESHOLD}`.

## Likely duplicate or near-duplicate emergent-code clusters

{markdown_table(candidate_rows, ["cluster_id", "cluster_size", "max_pair_similarity", "candidate_codebook_extension", "labels", "field_paths", "emergent_code_ids"], max_rows=40)}

## Codebook-extension interpretation

Rows in `outputs/tables/emergent_code_clusters.csv` include the original label, field path, rationale, evidence quote, and a `duplicate_or_near_duplicate_candidate` flag. Clusters with multiple studies or repeated labels are good candidates for controlled-vocabulary review.
"""
    write_text(REPORTS_DIR / "candidate_codebook_extensions.md", report)
    return {
        "emergent_cluster_count": len(groups),
        "emergent_duplicate_candidate_count": len(candidate_rows),
    }


def eps_verification_text(fields: dict[str, dict[str, list[dict[str, Any]]]], study_id: str) -> str:
    parts = []
    for field_path in EPS_VERIFICATION_TEXT_FIELDS:
        vals = field_values(fields, study_id, field_path)
        if vals:
            parts.append(f"{field_path}: {join_values(vals)}")
    return ". ".join(parts)


def add_audit_row(rows: list[dict[str, Any]], row: dict[str, Any]) -> None:
    row["audit_id"] = f"audit-{len(rows) + 1:04d}"
    row.setdefault("exploratory", True)
    rows.append(row)


def priority_for_similarity(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.60:
        return "medium"
    return "low"


def run_e10(data: dict[str, Any], fields: dict[str, dict[str, list[dict[str, Any]]]]) -> dict[str, Any]:
    audit_rows: list[dict[str, Any]] = []

    # Similar claims with different evidence-confidence ratings.
    claim_cards = data["cards_by_type"].get("claim_card", [])
    claims_by_id = {str(claim["claim_id"]): claim for claim in data["claims"]}
    claim_sim = similarity_matrix(claim_cards, data["vectors"])
    claim_candidates: list[tuple[float, int, int]] = []
    for i in range(len(claim_cards)):
        for j in range(i + 1, len(claim_cards)):
            score = float(claim_sim[i, j])
            if score < CLAIM_AUDIT_THRESHOLD:
                continue
            c1 = claims_by_id.get(str(claim_cards[i].get("claim_id")), {})
            c2 = claims_by_id.get(str(claim_cards[j].get("claim_id")), {})
            conf1 = clean_text(c1.get("evidence_confidence")) or "not reported"
            conf2 = clean_text(c2.get("evidence_confidence")) or "not reported"
            if conf1 != conf2:
                claim_candidates.append((score, i, j))
    claim_candidates.sort(key=lambda item: (-item[0], str(claim_cards[item[1]].get("claim_id")), str(claim_cards[item[2]].get("claim_id"))))
    for score, i, j in claim_candidates[:MAX_AUDIT_ROWS_PER_TYPE]:
        c1 = claims_by_id.get(str(claim_cards[i].get("claim_id")), {})
        c2 = claims_by_id.get(str(claim_cards[j].get("claim_id")), {})
        conf1 = clean_text(c1.get("evidence_confidence")) or "not reported"
        conf2 = clean_text(c2.get("evidence_confidence")) or "not reported"
        add_audit_row(
            audit_rows,
            {
                "audit_type": "similar_claims_different_evidence_confidence",
                "priority": priority_for_similarity(score),
                "similarity_score": f"{score:.6f}",
                "similarity_method": f"{MODEL_NAME} cosine over claim_card; threshold={CLAIM_AUDIT_THRESHOLD}",
                "unit_type": "claim_card",
                "id_1": c1.get("claim_id") or claim_cards[i].get("claim_id"),
                "id_2": c2.get("claim_id") or claim_cards[j].get("claim_id"),
                "study_id_1": c1.get("study_id") or claim_cards[i].get("study_id"),
                "study_id_2": c2.get("study_id") or claim_cards[j].get("study_id"),
                "differing_controlled_fields": "evidence_confidence_rating",
                "field_value_1": conf1,
                "field_value_2": conf2,
                "snippet_1": snippet(c1.get("claim_text") or claim_cards[i].get("text")),
                "snippet_2": snippet(c2.get("claim_text") or claim_cards[j].get("text")),
                "evidence_or_provenance_1": f"source_path={c1.get('source_path', '')}; evidence={claim_quote(claim_cards[i])}",
                "evidence_or_provenance_2": f"source_path={c2.get('source_path', '')}; evidence={claim_quote(claim_cards[j])}",
                "recommended_action": "Human reviewer should compare evidence-confidence coding; do not auto-correct.",
            },
        )

    # Similar studies with different approach classifications.
    study_cards = data["cards_by_type"].get("study_card", [])
    studies_by_id = {str(study["study_id"]): study for study in data["studies"]}
    study_sim = similarity_matrix(study_cards, data["vectors"])
    study_candidates: list[tuple[float, int, int]] = []
    for i in range(len(study_cards)):
        for j in range(i + 1, len(study_cards)):
            score = float(study_sim[i, j])
            if score < STUDY_APPROACH_AUDIT_THRESHOLD:
                continue
            sid1 = str(study_cards[i].get("study_id"))
            sid2 = str(study_cards[j].get("study_id"))
            approach1 = joined_field(fields, sid1, APPROACH_FIELD) or "not reported"
            approach2 = joined_field(fields, sid2, APPROACH_FIELD) or "not reported"
            if approach1 != approach2:
                study_candidates.append((score, i, j))
    study_candidates.sort(key=lambda item: (-item[0], str(study_cards[item[1]].get("study_id")), str(study_cards[item[2]].get("study_id"))))
    for score, i, j in study_candidates[:MAX_AUDIT_ROWS_PER_TYPE]:
        sid1 = str(study_cards[i].get("study_id"))
        sid2 = str(study_cards[j].get("study_id"))
        approach1 = joined_field(fields, sid1, APPROACH_FIELD) or "not reported"
        approach2 = joined_field(fields, sid2, APPROACH_FIELD) or "not reported"
        add_audit_row(
            audit_rows,
            {
                "audit_type": "similar_studies_different_approach_classification",
                "priority": priority_for_similarity(score),
                "similarity_score": f"{score:.6f}",
                "similarity_method": f"{MODEL_NAME} cosine over study_card; threshold={STUDY_APPROACH_AUDIT_THRESHOLD}",
                "unit_type": "study_card",
                "id_1": sid1,
                "id_2": sid2,
                "study_id_1": sid1,
                "study_id_2": sid2,
                "differing_controlled_fields": "approach_classification",
                "field_value_1": approach1,
                "field_value_2": approach2,
                "snippet_1": snippet(studies_by_id.get(sid1, {}).get("title") or study_cards[i].get("text")),
                "snippet_2": snippet(studies_by_id.get(sid2, {}).get("title") or study_cards[j].get("text")),
                "evidence_or_provenance_1": field_provenance(fields, sid1, [APPROACH_FIELD]),
                "evidence_or_provenance_2": field_provenance(fields, sid2, [APPROACH_FIELD]),
                "recommended_action": "Human reviewer should compare approach-classification rationale; do not auto-correct.",
            },
        )

    # Similar EPS verification descriptions with different IV&V integration levels.
    study_ids = [str(card.get("study_id")) for card in study_cards]
    eps_texts = [eps_verification_text(fields, study_id) for study_id in study_ids]
    eps_sim = simple_tfidf_cosine(eps_texts)
    eps_candidates: list[tuple[float, int, int]] = []
    for i in range(len(study_ids)):
        if not eps_texts[i]:
            continue
        for j in range(i + 1, len(study_ids)):
            if not eps_texts[j]:
                continue
            score = float(eps_sim[i, j])
            if score < EPS_IVV_AUDIT_THRESHOLD:
                continue
            ivv1 = joined_field(fields, study_ids[i], IVV_FIELD) or "not reported"
            ivv2 = joined_field(fields, study_ids[j], IVV_FIELD) or "not reported"
            if ivv1 != ivv2:
                eps_candidates.append((score, i, j))
    eps_candidates.sort(key=lambda item: (-item[0], study_ids[item[1]], study_ids[item[2]]))
    for score, i, j in eps_candidates[:MAX_AUDIT_ROWS_PER_TYPE]:
        sid1 = study_ids[i]
        sid2 = study_ids[j]
        ivv1 = joined_field(fields, sid1, IVV_FIELD) or "not reported"
        ivv2 = joined_field(fields, sid2, IVV_FIELD) or "not reported"
        add_audit_row(
            audit_rows,
            {
                "audit_type": "similar_eps_verification_different_ivv_level",
                "priority": priority_for_similarity(score),
                "similarity_score": f"{score:.6f}",
                "similarity_method": f"local TF-IDF cosine over EPS verification field text; threshold={EPS_IVV_AUDIT_THRESHOLD}",
                "unit_type": "study_eps_verification_fields",
                "id_1": sid1,
                "id_2": sid2,
                "study_id_1": sid1,
                "study_id_2": sid2,
                "differing_controlled_fields": "ivv_integration_level",
                "field_value_1": ivv1,
                "field_value_2": ivv2,
                "snippet_1": snippet(eps_texts[i]),
                "snippet_2": snippet(eps_texts[j]),
                "evidence_or_provenance_1": field_provenance(fields, sid1, [*EPS_VERIFICATION_TEXT_FIELDS, IVV_FIELD]),
                "evidence_or_provenance_2": field_provenance(fields, sid2, [*EPS_VERIFICATION_TEXT_FIELDS, IVV_FIELD]),
                "recommended_action": "Human reviewer should compare EPS-verification and IV&V coding; do not auto-correct.",
            },
        )

    audit_rows.sort(key=lambda row: (row["audit_type"], -float(row["similarity_score"]), row["id_1"], row["id_2"]))
    for idx, row in enumerate(audit_rows, start=1):
        row["audit_id"] = f"audit-{idx:04d}"
    write_csv(TABLES_DIR / "audit_queue.csv", audit_rows, AUDIT_COLUMNS)

    counts = Counter(row["audit_type"] for row in audit_rows)
    count_rows = [{"audit_type": key, "row_count": value} for key, value in sorted(counts.items())]
    report = f"""# E10 — Consistency and miscoding audit queue

**Exploratory notice:** this queue flags potential review pairs from semantic similarity and controlled-field disagreements. It makes **no automatic corrections**.

## Thresholds

- Similar claims with different `evidence_confidence_rating`: `{CLAIM_AUDIT_THRESHOLD}` over `{MODEL_NAME}` claim-card cosine.
- Similar studies with different `approach_classification`: `{STUDY_APPROACH_AUDIT_THRESHOLD}` over `{MODEL_NAME}` study-card cosine.
- Similar EPS verification descriptions with different `ivv_integration_level`: `{EPS_IVV_AUDIT_THRESHOLD}` over local TF-IDF cosine on EPS verification field text.
- Per-type row cap: `{MAX_AUDIT_ROWS_PER_TYPE}`.

Audit rows: **{len(audit_rows)}**.

## Rows by audit type

{markdown_table(count_rows, ["audit_type", "row_count"], max_rows=10)}

## Highest-priority rows

{markdown_table(audit_rows, ["audit_id", "audit_type", "priority", "similarity_score", "id_1", "id_2", "differing_controlled_fields", "field_value_1", "field_value_2"], max_rows=25)}

Every CSV row includes snippets plus evidence/provenance where available. Reviewers should inspect source extraction evidence before deciding whether any recoding is warranted.
"""
    write_text(REPORTS_DIR / "audit_queue.md", report)
    return {"audit_row_count": len(audit_rows), **{f"audit_{key}": value for key, value in counts.items()}}


def main() -> None:
    data = load_inputs()
    fields = field_index(data["study_codes"])
    summary: dict[str, Any] = {}
    summary.update(run_e7(data, fields))
    summary.update(run_e8(data))
    summary.update(run_e9(data))
    summary.update(run_e10(data, fields))

    print("Semantic analyses complete (exploratory):")
    for key in sorted(summary):
        print(f"  {key}: {summary[key]}")


if __name__ == "__main__":
    main()
