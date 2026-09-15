#!/usr/bin/env python3
"""Cluster Qwen vectors and save representative reports or chunks."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from search import ARTIFACT_DIR, DATA_DIR, file_sha256, read_jsonl


def main(args: argparse.Namespace) -> int:
    import numpy as np
    from sklearn.cluster import KMeans, MiniBatchKMeans

    chunks_path = DATA_DIR / "chunks.jsonl"
    chunks = read_jsonl(chunks_path)
    reports = {row["report_id"]: row for row in read_jsonl(DATA_DIR / "reports.jsonl")}
    manifest = json.loads((ARTIFACT_DIR / "index-manifest.json").read_text())
    if manifest["chunks_sha256"] != file_sha256(chunks_path):
        raise SystemExit("The Qwen index is stale. Run build_index.py.")
    chunk_vectors = np.load(ARTIFACT_DIR / "document-embeddings.f32.npy", mmap_mode="r")

    if args.level == "report":
        rows_by_report: dict[str, list[int]] = defaultdict(list)
        for index, chunk in enumerate(chunks):
            rows_by_report[chunk["report_id"]].append(index)
        item_ids = sorted(rows_by_report)
        vectors = np.stack(
            [
                chunk_vectors[rows_by_report[report_id]].mean(axis=0)
                for report_id in item_ids
            ]
        )
        vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
        metadata = [reports[report_id] for report_id in item_ids]
        algorithm = KMeans(n_clusters=args.clusters, random_state=args.seed, n_init=20)
    else:
        vectors = np.asarray(chunk_vectors)
        metadata = chunks
        algorithm = MiniBatchKMeans(
            n_clusters=args.clusters,
            random_state=args.seed,
            n_init=5,
            batch_size=1024,
        )

    if not 2 <= args.clusters < len(vectors):
        raise SystemExit("clusters must be at least 2 and smaller than the item count")
    labels = algorithm.fit_predict(vectors)
    centers = algorithm.cluster_centers_
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    clusters = []
    for cluster_id in range(args.clusters):
        member_indices = np.flatnonzero(labels == cluster_id)
        similarities = vectors[member_indices] @ centers[cluster_id]
        representative_indices = member_indices[
            np.argsort(-similarities)[: args.representatives]
        ]
        representatives = []
        for index in representative_indices:
            item = metadata[int(index)]
            if args.level == "report":
                representatives.append(
                    {
                        "report_id": item["report_id"],
                        "title": item["title"],
                        "year": item["publication_year"],
                        "source_path": item["source_path"],
                        "similarity_to_centroid": float(
                            vectors[index] @ centers[cluster_id]
                        ),
                    }
                )
            else:
                representatives.append(
                    {
                        "chunk_id": item["chunk_id"],
                        "report_id": item["report_id"],
                        "title": item["title"],
                        "section": item["section"],
                        "page_start": item["page_start"],
                        "page_end": item["page_end"],
                        "text": item["text"],
                        "similarity_to_centroid": float(
                            vectors[index] @ centers[cluster_id]
                        ),
                    }
                )
        clusters.append(
            {
                "cluster_id": cluster_id,
                "size": int(len(member_indices)),
                "representatives": representatives,
            }
        )

    result = {
        "level": args.level,
        "cluster_count": args.clusters,
        "item_count": len(vectors),
        "instruction": "Read the representatives and assign a human theme label. Cluster IDs have no semantic meaning.",
        "clusters": sorted(clusters, key=lambda row: (-row["size"], row["cluster_id"])),
    }
    output = args.output or ARTIFACT_DIR / f"clusters-{args.level}-{args.clusters}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {output}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", choices=("report", "chunk"), default="report")
    parser.add_argument("--clusters", type=int, default=12)
    parser.add_argument("--representatives", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
