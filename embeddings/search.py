#!/usr/bin/env python3
"""Search the SLR1 chunk corpus with Qwen embeddings, BM25, or both."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "data"
ARTIFACT_DIR = SCRIPT_DIR / "artifacts/qwen3-embedding-0.6b"
MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
MODEL_REVISION = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
QUOTED_PHRASE_RE = re.compile(r'"([^"]+)"')


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def choose_device(torch: Any, requested: str) -> str:
    if requested != "auto":
        return requested
    return "mps" if torch.backends.mps.is_available() else "cpu"


def load_qwen(device: str = "auto") -> tuple[Any, str]:
    os.environ.setdefault("HF_HOME", str(SCRIPT_DIR / ".cache/huggingface"))
    os.environ.setdefault(
        "SENTENCE_TRANSFORMERS_HOME",
        str(SCRIPT_DIR / ".cache/huggingface/sentence-transformers"),
    )
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    import torch
    from sentence_transformers import SentenceTransformer

    device = choose_device(torch, device)
    dtype = torch.bfloat16 if device == "mps" else torch.float32
    model = SentenceTransformer(
        MODEL_ID,
        revision=MODEL_REVISION,
        device=device,
        model_kwargs={"dtype": dtype, "attn_implementation": "sdpa"},
        tokenizer_kwargs={"padding_side": "right"},
    )
    model.max_seq_length = 768
    return model, device


def embed_questions(model: Any, questions: list[str]):
    import numpy as np

    embeddings = model.encode(
        questions,
        batch_size=min(16, len(questions)),
        prompt_name="query",
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(np.float32)
    if not np.isfinite(embeddings).all():
        raise RuntimeError("Question embeddings contain nonfinite values")
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings


def tokenize(text: str) -> list[str]:
    return [match.group(0).casefold() for match in TOKEN_RE.finditer(text)]


def prepare_bm25(chunks: list[dict]) -> tuple[list[list[str]], Counter[str], float]:
    tokenized = [tokenize(chunk["embedding_text"]) for chunk in chunks]
    document_frequency: Counter[str] = Counter()
    for tokens in tokenized:
        document_frequency.update(set(tokens))
    average_length = sum(map(len, tokenized)) / len(tokenized)
    return tokenized, document_frequency, average_length


def bm25_scores(
    question: str,
    tokenized: list[list[str]],
    document_frequency: Counter[str],
    average_length: float,
    k1: float = 1.5,
    b: float = 0.75,
):
    import numpy as np

    query_terms = set(tokenize(question))
    quoted_phrases = [
        tokenize(match.group(1)) for match in QUOTED_PHRASE_RE.finditer(question)
    ]
    quoted_phrases = [phrase for phrase in quoted_phrases if len(phrase) > 1]
    scores = np.zeros(len(tokenized), dtype=np.float32)
    document_count = len(tokenized)
    for index, tokens in enumerate(tokenized):
        frequencies = Counter(tokens)
        length_factor = k1 * (1 - b + b * len(tokens) / average_length)
        score = 0.0
        inverse_frequencies: dict[str, float] = {}
        for term in query_terms:
            frequency = frequencies.get(term, 0)
            count = document_frequency[term]
            inverse_frequency = math.log(
                1 + (document_count - count + 0.5) / (count + 0.5)
            )
            inverse_frequencies[term] = inverse_frequency
            if not frequency:
                continue
            score += (
                inverse_frequency * frequency * (k1 + 1) / (frequency + length_factor)
            )
        if quoted_phrases:
            document_tokens = f" {' '.join(tokens)} "
            for phrase in quoted_phrases:
                if f" {' '.join(phrase)} " in document_tokens:
                    score += 2 * sum(
                        inverse_frequencies.get(term, 0.0) for term in set(phrase)
                    )
        scores[index] = score
    return scores


def reciprocal_rank_fusion(
    dense_scores, lexical_scores, depth: int = 1000, constant: int = 60
):
    import numpy as np

    fused = np.zeros(len(dense_scores), dtype=np.float32)
    dense_order = np.argsort(-dense_scores, kind="stable")[:depth]
    lexical_order = np.argsort(-lexical_scores, kind="stable")
    lexical_order = lexical_order[lexical_scores[lexical_order] > 0][:depth]
    fused[dense_order] += 1 / (constant + np.arange(1, len(dense_order) + 1))
    fused[lexical_order] += 1 / (constant + np.arange(1, len(lexical_order) + 1))
    return fused


def main(args: argparse.Namespace) -> int:
    import numpy as np

    chunks_path = DATA_DIR / "chunks.jsonl"
    chunks = read_jsonl(chunks_path)
    reports = {row["report_id"]: row for row in read_jsonl(DATA_DIR / "reports.jsonl")}
    questions = args.query or [line.strip() for line in sys.stdin if line.strip()]
    if not questions:
        raise SystemExit(
            "Supply --query or newline separated questions on standard input"
        )

    dense_vectors = None
    question_vectors = None
    device = None
    if args.mode in {"dense", "hybrid"}:
        manifest = json.loads((ARTIFACT_DIR / "index-manifest.json").read_text())
        if manifest["chunks_sha256"] != file_sha256(chunks_path):
            raise SystemExit("The Qwen index is stale. Run build_index.py.")
        dense_vectors = np.load(
            ARTIFACT_DIR / "document-embeddings.f32.npy", mmap_mode="r"
        )
        if len(dense_vectors) != len(chunks):
            raise SystemExit(
                "The Qwen index and chunk corpus have different row counts"
            )
        model, device = load_qwen(args.device)
        question_vectors = embed_questions(model, questions)

    bm25_data = None
    if args.mode in {"bm25", "hybrid"}:
        bm25_data = prepare_bm25(chunks)

    output = []
    for question_index, question in enumerate(questions):
        dense_scores = (
            dense_vectors @ question_vectors[question_index]
            if dense_vectors is not None
            else None
        )
        lexical_scores = (
            bm25_scores(question, *bm25_data) if bm25_data is not None else None
        )
        if args.mode == "dense":
            final_scores = dense_scores
        elif args.mode == "bm25":
            final_scores = lexical_scores
        else:
            final_scores = reciprocal_rank_fusion(
                dense_scores, lexical_scores, depth=args.fusion_depth
            )

        order = np.argsort(-final_scores, kind="stable")
        results = []
        report_counts: Counter[str] = Counter()
        for row_index in order:
            chunk = chunks[int(row_index)]
            report_id = chunk["report_id"]
            if report_counts[report_id] >= args.max_per_report:
                continue
            report_counts[report_id] += 1
            result = {
                "rank": len(results) + 1,
                "score": float(final_scores[int(row_index)]),
                "chunk_id": chunk["chunk_id"],
                "report_id": report_id,
                "title": chunk["title"],
                "source_path": reports[report_id]["source_path"],
                "section": chunk["section"],
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "chunk_type": chunk["chunk_type"],
                "text": chunk["text"],
            }
            for optional_field in (
                "diagram_id",
                "diagram_part",
                "modeling_language",
                "representation_type",
                "image_refs",
            ):
                if optional_field in chunk:
                    result[optional_field] = chunk[optional_field]
            if dense_scores is not None:
                result["dense_score"] = float(dense_scores[int(row_index)])
            if lexical_scores is not None:
                result["bm25_score"] = float(lexical_scores[int(row_index)])
            results.append(result)
            if len(results) >= args.top_k:
                break
        output.append(
            {
                "question": question,
                "mode": args.mode,
                "device": device,
                "results": results,
            }
        )

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    for row in output:
        print(f"\n# {row['question']}")
        for result in row["results"]:
            pages = result["page_start"]
            if result["page_end"] and result["page_end"] != pages:
                pages = f"{pages}-{result['page_end']}"
            excerpt = " ".join(result["text"].split())[: args.excerpt_chars]
            image = ""
            if result.get("image_refs"):
                image = f"\n   Image: {result['image_refs'][0]}"
            print(
                f"\n{result['rank']}. {result['report_id']} | p. {pages} | "
                f"{result['title']}\n   {result['section']}{image}\n   {excerpt}"
            )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("dense", "bm25", "hybrid"), default="hybrid")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--query", action="append")
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--max-per-report", type=int, default=2)
    parser.add_argument("--fusion-depth", type=int, default=1000)
    parser.add_argument("--excerpt-chars", type=int, default=500)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
