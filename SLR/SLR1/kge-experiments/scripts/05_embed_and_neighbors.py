#!/usr/bin/env python3
"""Embed SLR1 text cards and write same-unit nearest-neighbor audit tables.

Default operation uses the deterministic local `hashing_tfidf_v1` fallback:
standard-library tokenization/hash metadata plus NumPy arrays. No clustering,
hybrid graph, or GraphRAG steps are performed here.
"""

from __future__ import annotations

import argparse
import hashlib
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
    REPORTS_DIR,
    SCRIPT_DIR,
    TABLES_DIR,
    clean_text,
    ensure_dirs,
    ensure_issue001_outputs,
    load_jsonl,
    markdown_table,
    sha256_file,
    source_generated_at_utc,
    write_csv,
    write_json,
    write_text,
)


EMBEDDINGS_DIR = BASE_DIR / "embeddings"
MODEL_NAME = "hashing_tfidf_v1"
MODEL_VERSION = "hashing_tfidf_v1"
DEFAULT_DIMENSIONS = 384
DEFAULT_TOP_K = 5
DEFAULT_CHUNK_SIZE = 256

CARD_FILES = [
    "study_cards.jsonl",
    "claim_cards.jsonl",
    "evidence_quote_cards.jsonl",
    "emergent_code_cards.jsonl",
    "limitation_cards.jsonl",
    "gap_mapping_cards.jsonl",
    "card_index.jsonl",
]
UNIT_TYPE_ORDER = [
    "study_card",
    "claim_card",
    "evidence_quote_card",
    "emergent_code_card",
    "limitation_card",
    "gap_mapping_card",
]

TOKEN_PATTERN = r"[a-z0-9]+(?:[._+#/\-][a-z0-9]+)*"
TOKEN_RE = re.compile(TOKEN_PATTERN, re.IGNORECASE)

NEIGHBOR_COLUMNS = [
    "unit_type",
    "rank",
    "card_id",
    "neighbor_card_id",
    "cosine_similarity",
    "card_study_id",
    "neighbor_study_id",
    "card_claim_id",
    "neighbor_claim_id",
    "card_label",
    "neighbor_label",
    "card_snippet",
    "neighbor_snippet",
    "comparison_scope",
    "exploratory",
]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def ensure_card_outputs() -> None:
    """Build cards if any expected embedding-card JSONL artifact is missing."""
    ensure_issue001_outputs()
    missing = [name for name in CARD_FILES if not (EMBEDDINGS_DIR / name).exists()]
    if not missing:
        return
    card_script = SCRIPT_DIR / "04_build_embedding_cards.py"
    if not card_script.exists():
        raise FileNotFoundError(f"Missing card builder script: {card_script}")
    subprocess.run([sys.executable, str(card_script)], check=True)
    still_missing = [name for name in CARD_FILES if not (EMBEDDINGS_DIR / name).exists()]
    if still_missing:
        raise FileNotFoundError(f"Card builder did not produce: {', '.join(still_missing)}")


def normalize_for_tokenization(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\biv\s*&\s*v\b", "ivv", lowered)
    lowered = re.sub(r"\bi\s*/\s*v\s*/\s*v\b", "ivv", lowered)
    lowered = re.sub(r"\bi\s*-\s*v\s*-\s*v\b", "ivv", lowered)
    return lowered


def tokenize(text: Any) -> list[str]:
    cleaned = clean_text(text) or ""
    normalized = normalize_for_tokenization(cleaned)
    return TOKEN_RE.findall(normalized)


def token_hash(token: str, dimensions: int) -> tuple[int, int, str]:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], byteorder="big", signed=False) % dimensions
    sign = 1 if digest[8] % 2 == 0 else -1
    return bucket, sign, digest.hex()


def build_hashed_tfidf_vectors(
    cards: list[dict[str, Any]], dimensions: int
) -> tuple[np.ndarray, dict[str, Any]]:
    token_counts: list[Counter[str]] = []
    document_frequency: Counter[str] = Counter()
    document_lengths: list[int] = []

    for card in cards:
        tokens = tokenize(card.get("text"))
        counts = Counter(tokens)
        token_counts.append(counts)
        document_frequency.update(counts.keys())
        document_lengths.append(len(tokens))

    card_count = len(cards)
    idf = {
        token: math.log((1.0 + card_count) / (1.0 + df)) + 1.0
        for token, df in document_frequency.items()
    }

    vectors = np.zeros((card_count, dimensions), dtype=np.float32)
    nonzero_dimensions: list[int] = []
    hash_cache: dict[str, tuple[int, int, str]] = {}

    for row_index, counts in enumerate(token_counts):
        buckets: defaultdict[int, float] = defaultdict(float)
        for token, tf in counts.items():
            if token not in hash_cache:
                hash_cache[token] = token_hash(token, dimensions)
            bucket, sign, _digest_hex = hash_cache[token]
            weight = (1.0 + math.log(float(tf))) * idf[token]
            buckets[bucket] += float(sign) * weight
        norm = math.sqrt(sum(weight * weight for weight in buckets.values()))
        if norm > 0.0:
            for bucket, weight in buckets.items():
                value = weight / norm
                if abs(value) > 1e-12:
                    vectors[row_index, bucket] = np.float32(value)
        nonzero_dimensions.append(int(np.count_nonzero(vectors[row_index])))

    idf_values = list(idf.values())
    bucket_token_counts: Counter[int] = Counter()
    token_stats: list[dict[str, Any]] = []
    for token in sorted(document_frequency):
        bucket, sign, digest_hex = hash_cache.get(token) or token_hash(token, dimensions)
        bucket_token_counts[bucket] += 1
        token_stats.append(
            {
                "token": token,
                "document_frequency": int(document_frequency[token]),
                "idf": round(idf[token], 8),
                "hash_bucket": int(bucket),
                "hash_sign": int(sign),
                "sha256_prefix": digest_hex[:16],
            }
        )

    metadata = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "dimensions": dimensions,
        "card_count": card_count,
        "vocabulary_size": len(document_frequency),
        "tokenization": {
            "lowercase": True,
            "regex": TOKEN_PATTERN,
            "normalization_notes": "Whitespace is collapsed before tokenization; tokens are lowercased; IV&V/I-V-V/I/V/V normalize to ivv; technical tokens such as MBSE, EPS, SysML, CubeSat, and IVV are retained in lowercase/alphanumeric-ish form.",
        },
        "term_frequency": {
            "formula": "1 + ln(tf) for terms present in a card",
        },
        "inverse_document_frequency": {
            "formula": "ln((1 + card_count) / (1 + document_frequency)) + 1",
            "minimum": round(min(idf_values), 8) if idf_values else None,
            "maximum": round(max(idf_values), 8) if idf_values else None,
        },
        "hashing": {
            "algorithm": "SHA-256",
            "bucket_rule": "int.from_bytes(sha256(token)[:8], 'big') % dimensions",
            "signed_hashing": True,
            "sign_rule": "+1 if sha256(token)[8] is even else -1",
            "python_hash_used": False,
        },
        "normalization": "L2 normalized rows; cosine similarity is the dot product of normalized vectors.",
        "document_length_tokens": {
            "minimum": min(document_lengths) if document_lengths else 0,
            "maximum": max(document_lengths) if document_lengths else 0,
            "mean": round(sum(document_lengths) / len(document_lengths), 4) if document_lengths else 0,
            "empty_card_count": sum(1 for length in document_lengths if length == 0),
        },
        "nonzero_dimensions_per_vector": {
            "minimum": min(nonzero_dimensions) if nonzero_dimensions else 0,
            "maximum": max(nonzero_dimensions) if nonzero_dimensions else 0,
            "mean": round(sum(nonzero_dimensions) / len(nonzero_dimensions), 4) if nonzero_dimensions else 0,
        },
        "hash_bucket_token_counts": {
            str(bucket): int(bucket_token_counts.get(bucket, 0)) for bucket in range(dimensions)
        },
        "token_stats": token_stats,
    }
    return vectors, metadata


def snippet(text: Any, max_chars: int = 180) -> str:
    compact = clean_text(text) or ""
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 1].rstrip() + "…"


def ordered_unit_types(cards: list[dict[str, Any]]) -> list[str]:
    observed = {str(card.get("unit_type")) for card in cards}
    ordered = [unit_type for unit_type in UNIT_TYPE_ORDER if unit_type in observed]
    ordered.extend(sorted(observed - set(ordered)))
    return ordered


def card_groups(cards: list[dict[str, Any]]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for idx, card in enumerate(cards):
        groups[str(card.get("unit_type"))].append(idx)
    return {unit_type: indices for unit_type, indices in groups.items()}


def neighbor_record(
    *,
    card: dict[str, Any],
    neighbor: dict[str, Any],
    rank: int,
    similarity: float,
) -> dict[str, Any]:
    return {
        "unit_type": card.get("unit_type"),
        "rank": rank,
        "card_id": card.get("card_id"),
        "neighbor_card_id": neighbor.get("card_id"),
        "cosine_similarity": round(float(similarity), 6),
        "card_study_id": card.get("study_id"),
        "neighbor_study_id": neighbor.get("study_id"),
        "card_claim_id": card.get("claim_id"),
        "neighbor_claim_id": neighbor.get("claim_id"),
        "card_label": card.get("label") or card.get("title"),
        "neighbor_label": neighbor.get("label") or neighbor.get("title"),
        "card_snippet": snippet(card.get("text")),
        "neighbor_snippet": snippet(neighbor.get("text")),
        "comparison_scope": "within_unit_type",
        "exploratory": True,
    }


def compute_nearest_neighbors(
    vectors: np.ndarray,
    cards: list[dict[str, Any]],
    *,
    top_k: int,
    chunk_size: int,
) -> list[dict[str, Any]]:
    groups = card_groups(cards)
    records: list[dict[str, Any]] = []

    for unit_type in ordered_unit_types(cards):
        indices = groups.get(unit_type, [])
        if len(indices) <= 1:
            continue
        k = min(top_k, len(indices) - 1)
        group_indices = np.asarray(indices, dtype=np.int64)
        group_vectors = np.ascontiguousarray(vectors[group_indices])
        group_size = group_vectors.shape[0]

        for start in range(0, group_size, chunk_size):
            end = min(start + chunk_size, group_size)
            similarities = group_vectors[start:end] @ group_vectors.T
            for local_row, self_col in enumerate(range(start, end)):
                similarities[local_row, self_col] = -np.inf
            # Stable full sort keeps same-score ties in card-index order, which is
            # important for deterministic audit tables.
            top_columns = np.argsort(-similarities, axis=1, kind="mergesort")[:, :k]
            for local_row in range(end - start):
                card = cards[int(group_indices[start + local_row])]
                for rank, neighbor_col in enumerate(top_columns[local_row], start=1):
                    score = float(similarities[local_row, int(neighbor_col)])
                    if not math.isfinite(score):
                        continue
                    neighbor = cards[int(group_indices[int(neighbor_col)])]
                    records.append(
                        neighbor_record(
                            card=card,
                            neighbor=neighbor,
                            rank=rank,
                            similarity=score,
                        )
                    )
    return records


def count_cards(cards: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(card.get("unit_type")) for card in cards)


def relative(path: Path) -> str:
    repo_root = BASE_DIR.parents[2]
    return str(path.relative_to(repo_root))


def write_manifest(
    *,
    cards: list[dict[str, Any]],
    vectors_path: Path,
    vectorizer_path: Path,
    neighbor_path: Path,
    audit_csv_path: Path,
    report_path: Path,
    top_k: int,
    dimensions: int,
    neighbor_records: list[dict[str, Any]],
) -> None:
    card_count_by_unit_type = dict(sorted(count_cards(cards).items()))
    neighbor_count_by_unit_type = dict(sorted(Counter(row["unit_type"] for row in neighbor_records).items()))
    input_paths = [EMBEDDINGS_DIR / name for name in CARD_FILES]
    manifest = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "generated_at_utc": source_generated_at_utc(),
        "generated_at_basis": "source extraction generated_at; deterministic for idempotent rebuilds",
        "exploratory": True,
        "exploratory_note": "Embedding-derived nearest neighbors are lexical/hashed TF-IDF audit aids, not validated semantic clusters or evidence claims.",
        "comparison_scope": "within_unit_type_by_default",
        "mixed_unit_type_neighbors": False,
        "dimensions": dimensions,
        "top_k": top_k,
        "card_count": len(cards),
        "card_count_by_unit_type": card_count_by_unit_type,
        "neighbor_record_count": len(neighbor_records),
        "neighbor_count_by_unit_type": neighbor_count_by_unit_type,
        "inputs": [
            {
                "path": relative(path),
                "record_count": sum(1 for line in path.open("r", encoding="utf-8") if line.strip()),
                "sha256": sha256_file(path),
            }
            for path in input_paths
        ],
        "outputs": {
            "vectors_npy": {"path": relative(vectors_path), "sha256": sha256_file(vectors_path)},
            "vectorizer_json": {"path": relative(vectorizer_path), "sha256": sha256_file(vectorizer_path)},
            "nearest_neighbors_jsonl": {"path": relative(neighbor_path), "sha256": sha256_file(neighbor_path)},
            "nearest_neighbors_audit_csv": {"path": relative(audit_csv_path), "sha256": sha256_file(audit_csv_path)},
            "embedding_index_report_md": {"path": relative(report_path), "sha256": sha256_file(report_path)},
        },
    }
    write_json(EMBEDDINGS_DIR / "embedding_manifest.json", manifest)


def write_report(
    *,
    cards: list[dict[str, Any]],
    vectors: np.ndarray,
    vectorizer_metadata: dict[str, Any],
    neighbor_records: list[dict[str, Any]],
    top_k: int,
    dimensions: int,
) -> None:
    card_count_rows = [
        {"unit_type": unit_type, "card_count": count}
        for unit_type, count in sorted(count_cards(cards).items())
    ]
    neighbor_count_rows = [
        {"unit_type": unit_type, "neighbor_record_count": count}
        for unit_type, count in sorted(Counter(row["unit_type"] for row in neighbor_records).items())
    ]
    top_neighbor_rows = sorted(
        neighbor_records,
        key=lambda row: (-float(row["cosine_similarity"]), str(row["unit_type"]), str(row["card_id"])),
    )[:10]

    lines = [
        "# Embedding index report — SLR1 text cards",
        "",
        "**Exploratory notice:** all embedding-derived nearest-neighbor outputs are audit aids only. They are not semantic clusters, graph edges, or validated evidence claims.",
        "",
        "## Embedding model",
        "",
        f"- Model/version: `{MODEL_NAME}`",
        f"- Dimensions: `{dimensions}`",
        f"- Card count: `{len(cards)}`",
        f"- Vector shape: `{tuple(vectors.shape)}`",
        f"- Default neighbor scope: within the same `unit_type` only; mixed-unit comparisons were not generated.",
        f"- Top-k per card: `{top_k}`",
        f"- Tokenization regex: `{TOKEN_PATTERN}` with lowercase normalization and IV&V → `ivv` normalization.",
        f"- Vocabulary size: `{vectorizer_metadata.get('vocabulary_size')}`",
        "",
        "## Card counts by unit type",
        "",
        markdown_table(card_count_rows, ["unit_type", "card_count"], max_rows=20),
        "",
        "## Nearest-neighbor record counts",
        "",
        markdown_table(neighbor_count_rows, ["unit_type", "neighbor_record_count"], max_rows=20),
        "",
        "## Highest-similarity audit examples",
        "",
        markdown_table(
            top_neighbor_rows,
            ["unit_type", "rank", "card_id", "neighbor_card_id", "cosine_similarity"],
            max_rows=10,
        ),
        "",
        "## Outputs",
        "",
        "- `embeddings/vectors_hashing_tfidf_v1.npy`",
        "- `embeddings/vectorizer_hashing_tfidf_v1.json`",
        "- `embeddings/embedding_manifest.json`",
        "- `embeddings/nearest_neighbors.jsonl`",
        "- `outputs/tables/nearest_neighbors_audit.csv`",
        "- `outputs/reports/embedding_index_report.md`",
        "",
        "## Caveats",
        "",
        "- The fallback is deterministic and offline, but it is lexical TF-IDF hashing, not a neural semantic embedding model.",
        "- Hash collisions can occur; signed hashing reduces but does not eliminate collision effects.",
        "- Neighbor tables are intended for human audit and later issue inputs; no clustering, hybrid similarity graph, or GraphRAG work is performed in this issue.",
    ]
    write_text(REPORTS_DIR / "embedding_index_report.md", "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimensions", type=int, default=DEFAULT_DIMENSIONS, help="Hashing vector dimension")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="Nearest neighbors per card")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Rows per dense similarity chunk during nearest-neighbor calculation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dimensions <= 0:
        raise ValueError("--dimensions must be positive")
    if args.top_k <= 0:
        raise ValueError("--top-k must be positive")
    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be positive")

    ensure_dirs(EMBEDDINGS_DIR, TABLES_DIR, REPORTS_DIR)
    ensure_card_outputs()

    cards = load_jsonl(EMBEDDINGS_DIR / "card_index.jsonl")
    vectors, vectorizer_metadata = build_hashed_tfidf_vectors(cards, args.dimensions)

    vectors_path = EMBEDDINGS_DIR / f"vectors_{MODEL_NAME}.npy"
    vectorizer_path = EMBEDDINGS_DIR / f"vectorizer_{MODEL_NAME}.json"
    neighbor_path = EMBEDDINGS_DIR / "nearest_neighbors.jsonl"
    audit_csv_path = TABLES_DIR / "nearest_neighbors_audit.csv"
    report_path = REPORTS_DIR / "embedding_index_report.md"

    np.save(vectors_path, vectors)
    write_json(vectorizer_path, vectorizer_metadata)

    neighbor_records = compute_nearest_neighbors(
        vectors,
        cards,
        top_k=args.top_k,
        chunk_size=args.chunk_size,
    )
    write_jsonl(neighbor_path, neighbor_records)
    write_csv(audit_csv_path, neighbor_records, NEIGHBOR_COLUMNS)
    write_report(
        cards=cards,
        vectors=vectors,
        vectorizer_metadata=vectorizer_metadata,
        neighbor_records=neighbor_records,
        top_k=args.top_k,
        dimensions=args.dimensions,
    )
    write_manifest(
        cards=cards,
        vectors_path=vectors_path,
        vectorizer_path=vectorizer_path,
        neighbor_path=neighbor_path,
        audit_csv_path=audit_csv_path,
        report_path=report_path,
        top_k=args.top_k,
        dimensions=args.dimensions,
        neighbor_records=neighbor_records,
    )

    print(f"Embedded {len(cards)} cards with {MODEL_NAME}; vectors shape={vectors.shape}")
    for unit_type, count in sorted(count_cards(cards).items()):
        print(f"  {unit_type}: {count} cards")
    print(f"Nearest-neighbor records: {len(neighbor_records)}")


if __name__ == "__main__":
    main()
