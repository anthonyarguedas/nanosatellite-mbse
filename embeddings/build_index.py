#!/usr/bin/env python3
"""Build or incrementally extend the Qwen index from data/chunks.jsonl."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from search import (
    ARTIFACT_DIR,
    DATA_DIR,
    MODEL_ID,
    MODEL_REVISION,
    file_sha256,
    load_qwen,
    read_jsonl,
)


CHUNK_RECORDS_PATH = ARTIFACT_DIR / "indexed-chunks.jsonl"


def jsonl_prefix_sha256(path: Path, line_count: int) -> str | None:
    digest = hashlib.sha256()
    lines_read = 0
    with path.open("rb") as handle:
        for line in handle:
            if lines_read >= line_count:
                break
            digest.update(line)
            lines_read += 1
    return digest.hexdigest() if lines_read == line_count else None


def chunk_embedding_key(chunk: dict[str, Any]) -> tuple[str, str]:
    embedding_sha256 = hashlib.sha256(
        chunk["embedding_text"].encode("utf-8")
    ).hexdigest()
    return chunk["chunk_id"], embedding_sha256


def chunk_embedding_record(chunk: dict[str, Any]) -> dict[str, str]:
    chunk_id, embedding_sha256 = chunk_embedding_key(chunk)
    return {
        "chunk_id": chunk_id,
        "embedding_text_sha256": embedding_sha256,
    }


def reusable_prefix(chunks_path: Path, chunks: list[dict]):
    import numpy as np

    manifest_path = ARTIFACT_DIR / "index-manifest.json"
    vectors_path = ARTIFACT_DIR / "document-embeddings.f32.npy"
    if not manifest_path.exists() or not vectors_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        count = int(manifest["chunks"])
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None
    if (
        count <= 0
        or count > len(chunks)
        or manifest.get("model_id") != MODEL_ID
        or manifest.get("model_revision") != MODEL_REVISION
        or jsonl_prefix_sha256(chunks_path, count) != manifest.get("chunks_sha256")
    ):
        return None
    vectors = np.load(vectors_path, mmap_mode="r")
    if (
        vectors.ndim != 2
        or len(vectors) != count
        or vectors.shape[1] != manifest.get("dimensions")
    ):
        return None
    return vectors


def reusable_rows(
    chunks_path: Path, chunks: list[dict[str, Any]]
) -> tuple[Any, dict[int, int]] | None:
    import numpy as np

    manifest_path = ARTIFACT_DIR / "index-manifest.json"
    vectors_path = ARTIFACT_DIR / "document-embeddings.f32.npy"
    if manifest_path.exists() and vectors_path.exists() and CHUNK_RECORDS_PATH.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            records = read_jsonl(CHUNK_RECORDS_PATH)
            vectors = np.load(vectors_path, mmap_mode="r")
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            records = []
            vectors = None
        if (
            vectors is not None
            and manifest.get("model_id") == MODEL_ID
            and manifest.get("model_revision") == MODEL_REVISION
            and manifest.get("chunk_records_sha256")
            == file_sha256(CHUNK_RECORDS_PATH)
            and vectors.ndim == 2
            and len(vectors) == len(records)
            and len(vectors) == manifest.get("chunks")
            and vectors.shape[1] == manifest.get("dimensions")
        ):
            old_rows = {
                (record["chunk_id"], record["embedding_text_sha256"]): index
                for index, record in enumerate(records)
            }
            rows = {
                new_index: old_rows[key]
                for new_index, chunk in enumerate(chunks)
                if (key := chunk_embedding_key(chunk)) in old_rows
            }
            return vectors, rows

    prefix = reusable_prefix(chunks_path, chunks)
    if prefix is None:
        return None
    return prefix, {index: index for index in range(len(prefix))}


def write_chunk_records(path: Path, chunks: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(
                json.dumps(chunk_embedding_record(chunk), sort_keys=True) + "\n"
            )


def main(args: argparse.Namespace) -> int:
    import numpy as np

    chunks_path = DATA_DIR / "chunks.jsonl"
    input_chunks_sha256 = file_sha256(chunks_path)
    chunks = read_jsonl(chunks_path)
    if file_sha256(chunks_path) != input_chunks_sha256:
        raise RuntimeError("Chunk corpus changed while it was being read")

    reusable = None if args.no_incremental else reusable_rows(chunks_path, chunks)
    old_vectors, reused_rows = reusable if reusable is not None else (None, {})
    new_indices = [index for index in range(len(chunks)) if index not in reused_rows]
    reused_count = len(reused_rows)

    model, device = load_qwen(args.device)
    embedding_dimensions = int(model.get_embedding_dimension())
    started = time.perf_counter()
    embeddings = np.empty(
        (len(chunks), embedding_dimensions), dtype=np.float32
    )
    for new_index, old_index in reused_rows.items():
        embeddings[new_index] = old_vectors[old_index]
    if new_indices:
        new_embeddings = model.encode(
            [chunks[index]["embedding_text"] for index in new_indices],
            batch_size=args.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        ).astype(np.float32)
        embeddings[new_indices] = new_embeddings
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    if not np.isfinite(embeddings).all() or np.any(
        np.linalg.norm(embeddings, axis=1) == 0
    ):
        raise RuntimeError("Qwen produced invalid document embeddings")

    if file_sha256(chunks_path) != input_chunks_sha256:
        raise RuntimeError("Chunk corpus changed during index construction")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    output = ARTIFACT_DIR / "document-embeddings.f32.npy"
    vectors_temporary = output.with_suffix(".tmp")
    records_temporary = CHUNK_RECORDS_PATH.with_suffix(".tmp")
    with vectors_temporary.open("wb") as handle:
        np.save(handle, embeddings)
    write_chunk_records(records_temporary, chunks)
    chunk_records_sha256 = file_sha256(records_temporary)
    manifest = {
        "schema_version": "slr1-qwen-index/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "chunks_path": str(chunks_path.relative_to(DATA_DIR.parent)),
        "chunks_sha256": input_chunks_sha256,
        "chunks": len(chunks),
        "chunk_records_path": str(CHUNK_RECORDS_PATH.relative_to(DATA_DIR.parent)),
        "chunk_records_sha256": chunk_records_sha256,
        "reused_chunks": reused_count,
        "encoded_chunks": len(new_indices),
        "dimensions": int(embeddings.shape[1]),
        "storage_dtype": "float32",
        "device": device,
        "max_sequence_length": model.max_seq_length,
        "batch_size": args.batch_size,
        "encoding_seconds": time.perf_counter() - started,
    }
    manifest_path = ARTIFACT_DIR / "index-manifest.json"
    manifest_temporary = manifest_path.with_suffix(".tmp")
    manifest_temporary.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    vectors_temporary.replace(output)
    records_temporary.replace(CHUNK_RECORDS_PATH)
    manifest_temporary.replace(manifest_path)
    print(json.dumps(manifest, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--no-incremental", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
