#!/usr/bin/env python3
"""Build or incrementally refresh the ColPali index for every report image."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from image_corpus import build_image_records, file_sha256


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
IMAGES_PATH = DATA_DIR / "images.jsonl"
ARTIFACT_DIR = SCRIPT_DIR / "artifacts/colpali-v1.3-hf"
VECTORS_PATH = ARTIFACT_DIR / "image-embeddings.f16.npy"
MANIFEST_PATH = ARTIFACT_DIR / "index-manifest.json"
CACHE_DIR = ARTIFACT_DIR / ".build-cache"
BUILD_STATE_PATH = ARTIFACT_DIR / "build-state.json"
MODEL_ID = "vidore/colpali-v1.3-hf"
MODEL_REVISION = "133a9eb02947310513f52f8f0d39d622e0eab8dc"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def choose_device(torch: Any, requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_colpali(device: str = "auto") -> tuple[Any, Any, str]:
    os.environ.setdefault("HF_HOME", str(SCRIPT_DIR / ".cache/huggingface"))
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    import torch
    from transformers import ColPaliForRetrieval, ColPaliProcessor

    device = choose_device(torch, device)
    dtype = torch.float32 if device == "cpu" else torch.bfloat16
    model = ColPaliForRetrieval.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        dtype=dtype,
        attn_implementation="sdpa",
        low_cpu_mem_usage=True,
    ).eval()
    model.to(device)
    model.config.use_cache = False
    model.vlm.config.use_cache = False
    processor = ColPaliProcessor.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
    )
    processor.query_prefix = "Query: "
    return model, processor, device


def encode_images(
    model: Any,
    processor: Any,
    paths: list[Path],
):
    import numpy as np
    import torch
    from PIL import Image

    images = []
    for path in paths:
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    batch = processor(images=images, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        embeddings = model(**batch).embeddings
    array = embeddings.float().cpu().numpy().astype(np.float16)
    if array.ndim != 3 or not np.isfinite(array).all():
        raise RuntimeError("ColPali produced invalid image embeddings")
    return array


def encode_queries(model: Any, processor: Any, queries: list[str]):
    import torch

    batch = processor(text=queries, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        return model(**batch).embeddings


def current_records() -> list[dict[str, Any]]:
    reports_path = DATA_DIR / "reports.jsonl"
    units_path = DATA_DIR / "units.jsonl"
    analyses_path = DATA_DIR / "diagram-analyses.jsonl"
    for required in (reports_path, units_path):
        if not required.exists():
            raise RuntimeError(f"Corpus metadata is missing: {required}")
    return build_image_records(
        reports=read_jsonl(reports_path),
        units=read_jsonl(units_path),
        analyses=read_jsonl(analyses_path),
        repository_root=REPO_ROOT,
    )


def reusable_index() -> tuple[Any, dict[tuple[str, str], int]] | None:
    import numpy as np

    if (
        not MANIFEST_PATH.exists()
        or not VECTORS_PATH.exists()
        or not IMAGES_PATH.exists()
    ):
        return None
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        old_records = read_jsonl(IMAGES_PATH)
        vectors = np.load(VECTORS_PATH, mmap_mode="r")
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if (
        manifest.get("model_id") != MODEL_ID
        or manifest.get("model_revision") != MODEL_REVISION
        or manifest.get("images_sha256") != file_sha256(IMAGES_PATH)
        or vectors.ndim != 3
        or len(vectors) != len(old_records)
        or len(vectors) != manifest.get("images")
    ):
        return None
    rows = {
        (record["image_id"], record["source_image_sha256"]): index
        for index, record in enumerate(old_records)
    }
    return vectors, rows


def source_hash(path: Path) -> str | None:
    return file_sha256(path) if path.exists() else None


def write_build_state(payload: dict[str, Any]) -> None:
    temporary = BUILD_STATE_PATH.with_name(BUILD_STATE_PATH.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(BUILD_STATE_PATH)


def cached_embedding_path(record: dict[str, Any]) -> Path:
    digest = record["source_image_sha256"][:16]
    return CACHE_DIR / f"{record['image_id']}--{digest}.f16.npy"


def save_cached_embedding(path: Path, embedding: Any) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("wb") as handle:
        np.save(handle, embedding.astype(np.float16, copy=False))
    temporary.replace(path)


def load_cached_embedding(path: Path):
    import numpy as np

    try:
        embedding = np.load(path, mmap_mode="r")
    except (OSError, ValueError):
        path.unlink(missing_ok=True)
        return None
    if embedding.ndim != 2 or not np.isfinite(embedding).all():
        path.unlink(missing_ok=True)
        return None
    return embedding


def main(args: argparse.Namespace) -> int:
    import numpy as np

    started = time.perf_counter()
    records = current_records()
    if not records:
        raise RuntimeError("No report images were found")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    build_started_at = datetime.now(timezone.utc).isoformat()
    build_state = {
        "schema_version": "slr1-colpali-build-state/v1",
        "pid": os.getpid(),
        "started_at": build_started_at,
        "images": len(records),
        "completed": 0,
    }
    write_build_state(build_state)
    if args.no_incremental:
        shutil.rmtree(CACHE_DIR, ignore_errors=True)

    reusable = None if args.no_incremental else reusable_index()
    old_vectors, old_rows = reusable if reusable is not None else (None, {})
    reusable_rows: dict[int, int] = {}
    pending_rows: list[int] = []
    for new_index, record in enumerate(records):
        old_index = old_rows.get((record["image_id"], record["source_image_sha256"]))
        if old_index is None:
            pending_rows.append(new_index)
        else:
            reusable_rows[new_index] = old_index

    cached_rows: dict[int, Path] = {}
    uncached_rows: list[int] = []
    for row_index in pending_rows:
        cache_path = cached_embedding_path(records[row_index])
        embedding = load_cached_embedding(cache_path)
        if embedding is None:
            uncached_rows.append(row_index)
        else:
            cached_rows[row_index] = cache_path
    pending_rows = uncached_rows
    resumed_row_ids = set(cached_rows)

    model = processor = None
    device = args.device
    if old_vectors is not None and reusable_rows:
        vector_shape = tuple(old_vectors.shape[1:])
    elif cached_rows:
        first_cached = load_cached_embedding(next(iter(cached_rows.values())))
        vector_shape = tuple(first_cached.shape)
    else:
        first_indices = pending_rows[: args.batch_size]
        model, processor, device = load_colpali(args.device)
        first_paths = [
            REPO_ROOT / records[index]["source_image"] for index in first_indices
        ]
        first_embeddings = encode_images(model, processor, first_paths)
        vector_shape = tuple(first_embeddings.shape[1:])
        for row_index, embedding in zip(first_indices, first_embeddings):
            cache_path = cached_embedding_path(records[row_index])
            save_cached_embedding(cache_path, embedding)
            cached_rows[row_index] = cache_path
        pending_rows = pending_rows[len(first_indices) :]

    for row_index, cache_path in list(cached_rows.items()):
        embedding = load_cached_embedding(cache_path)
        if embedding is None or tuple(embedding.shape) != vector_shape:
            cache_path.unlink(missing_ok=True)
            cached_rows.pop(row_index)
            pending_rows.append(row_index)
    resumed_images = len(resumed_row_ids & set(cached_rows))

    vectors_temporary = VECTORS_PATH.with_name(VECTORS_PATH.name + ".tmp")
    images_temporary = IMAGES_PATH.with_name(IMAGES_PATH.name + ".tmp")
    manifest_temporary = MANIFEST_PATH.with_name(MANIFEST_PATH.name + ".tmp")
    output = np.lib.format.open_memmap(
        vectors_temporary,
        mode="w+",
        dtype=np.float16,
        shape=(len(records), *vector_shape),
    )

    for new_index, old_index in reusable_rows.items():
        output[new_index] = old_vectors[old_index]
    for row_index, cache_path in cached_rows.items():
        output[row_index] = load_cached_embedding(cache_path)

    encoded_this_run = len(cached_rows) - resumed_images
    completed_before_encoding = len(reusable_rows) + len(cached_rows)
    build_state["completed"] = completed_before_encoding
    write_build_state(build_state)
    print(
        f"Reused {len(reusable_rows)} indexed and {resumed_images} cached images. "
        f"Encoding {len(pending_rows)} images.",
        flush=True,
    )
    if pending_rows and model is None:
        model, processor, device = load_colpali(args.device)
    for offset in range(0, len(pending_rows), args.batch_size):
        indices = pending_rows[offset : offset + args.batch_size]
        paths = [REPO_ROOT / records[index]["source_image"] for index in indices]
        embeddings = encode_images(model, processor, paths)
        if tuple(embeddings.shape[1:]) != vector_shape:
            raise RuntimeError(
                f"ColPali embedding shape changed from {vector_shape} "
                f"to {tuple(embeddings.shape[1:])}"
            )
        output[indices] = embeddings
        for row_index, embedding in zip(indices, embeddings):
            save_cached_embedding(cached_embedding_path(records[row_index]), embedding)
        encoded_this_run += len(indices)
        completed = len(reusable_rows) + len(cached_rows) + offset + len(indices)
        build_state["completed"] = completed
        write_build_state(build_state)
        print(
            f"[{completed}/{len(records)}] indexed {len(indices)} image(s)", flush=True
        )

    output.flush()
    del output
    if old_vectors is not None:
        del old_vectors

    write_jsonl(images_temporary, records)
    images_sha256 = file_sha256(images_temporary)
    manifest = {
        "schema_version": "slr1-colpali-index/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "images_path": str(IMAGES_PATH.relative_to(SCRIPT_DIR)),
        "images_sha256": images_sha256,
        "reports_sha256": source_hash(DATA_DIR / "reports.jsonl"),
        "units_sha256": source_hash(DATA_DIR / "units.jsonl"),
        "diagram_analyses_sha256": source_hash(DATA_DIR / "diagram-analyses.jsonl"),
        "images": len(records),
        "mbse_diagrams": sum(record["is_mbse_diagram"] for record in records),
        "reused_images": len(reusable_rows),
        "resumed_images": resumed_images,
        "encoded_images": len(records) - len(reusable_rows),
        "encoded_images_this_run": encoded_this_run,
        "vectors_per_image": vector_shape[0],
        "dimensions": vector_shape[1],
        "storage_dtype": "float16",
        "device": device,
        "batch_size": args.batch_size,
        "encoding_seconds": time.perf_counter() - started,
    }
    manifest_temporary.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    images_temporary.replace(IMAGES_PATH)
    vectors_temporary.replace(VECTORS_PATH)
    manifest_temporary.replace(MANIFEST_PATH)
    shutil.rmtree(CACHE_DIR, ignore_errors=True)
    BUILD_STATE_PATH.unlink(missing_ok=True)
    print(json.dumps(manifest, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--no-incremental", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    return args


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
