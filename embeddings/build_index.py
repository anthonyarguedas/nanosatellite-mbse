#!/usr/bin/env python3
"""Build the Qwen document embedding index from data/chunks.jsonl."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone

from search import (
    ARTIFACT_DIR,
    DATA_DIR,
    MODEL_ID,
    MODEL_REVISION,
    file_sha256,
    load_qwen,
    read_jsonl,
)


def main(args: argparse.Namespace) -> int:
    import numpy as np

    chunks_path = DATA_DIR / "chunks.jsonl"
    chunks = read_jsonl(chunks_path)
    model, device = load_qwen(args.device)
    started = time.perf_counter()
    embeddings = model.encode(
        [chunk["embedding_text"] for chunk in chunks],
        batch_size=args.batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    ).astype(np.float32)
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
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
