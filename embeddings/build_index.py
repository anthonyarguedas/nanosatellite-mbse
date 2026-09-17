#!/usr/bin/env python3
"""Build or incrementally extend the Qwen index from data/chunks.jsonl."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from search import (
    ARTIFACT_DIR,
    DATA_DIR,
    MODEL_ID,
    MODEL_REVISION,
    file_sha256,
    load_qwen,
    read_jsonl,
)


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


def main(args: argparse.Namespace) -> int:
    import numpy as np

    chunks_path = DATA_DIR / "chunks.jsonl"
    chunks = read_jsonl(chunks_path)
    reused = reusable_prefix(chunks_path, chunks) if not args.no_incremental else None
    reused_count = len(reused) if reused is not None else 0
    model, device = load_qwen(args.device)
    started = time.perf_counter()
    if reused_count == len(chunks):
        embeddings = np.asarray(reused, dtype=np.float32).copy()
    else:
        new_embeddings = model.encode(
            [chunk["embedding_text"] for chunk in chunks[reused_count:]],
            batch_size=args.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        ).astype(np.float32)
        if reused is None:
            embeddings = new_embeddings
        else:
            embeddings = np.concatenate(
                (np.asarray(reused, dtype=np.float32), new_embeddings), axis=0
            )
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    if not np.isfinite(embeddings).all() or np.any(
        np.linalg.norm(embeddings, axis=1) == 0
    ):
        raise RuntimeError("Qwen produced invalid document embeddings")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    output = ARTIFACT_DIR / "document-embeddings.f32.npy"
    with output.with_suffix(".tmp").open("wb") as handle:
        np.save(handle, embeddings)
    output.with_suffix(".tmp").replace(output)
    manifest = {
        "schema_version": "slr1-qwen-index/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "chunks_path": str(chunks_path.relative_to(DATA_DIR.parent)),
        "chunks_sha256": file_sha256(chunks_path),
        "chunks": len(chunks),
        "reused_chunks": reused_count,
        "encoded_chunks": len(chunks) - reused_count,
        "dimensions": int(embeddings.shape[1]),
        "storage_dtype": "float32",
        "device": device,
        "max_sequence_length": model.max_seq_length,
        "batch_size": args.batch_size,
        "encoding_seconds": time.perf_counter() - started,
    }
    (ARTIFACT_DIR / "index-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
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
