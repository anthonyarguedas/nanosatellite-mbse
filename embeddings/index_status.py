"""Inspect text and visual index freshness without loading retrieval models."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from image_corpus import IMAGE_RE, IMAGE_SUFFIXES


SAMPLE_LIMIT = 8


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def path_sample(paths: set[str] | list[str]) -> list[str]:
    return sorted(paths)[:SAMPLE_LIMIT]


def process_is_running(pid: Any) -> bool:
    try:
        pid = int(pid)
        if pid < 1:
            return False
        os.kill(pid, 0)
    except (OSError, TypeError, ValueError):
        return False
    return True


def inspect_figure_sources(
    repository_root: Path, reports: list[dict[str, Any]]
) -> dict[str, Any]:
    """Discover current report figures without computing image embeddings."""
    repository_root = repository_root.resolve()
    figures: set[str] = set()
    missing_figures: set[str] = set()
    missing_reports: set[str] = set()
    invalid_references: set[str] = set()

    for report in reports:
        source_value = report.get("source_path")
        if not isinstance(source_value, str) or not source_value:
            missing_reports.add(report.get("report_id", "unknown report"))
            continue
        source = (repository_root / source_value).resolve()
        try:
            source.relative_to(repository_root)
        except ValueError:
            missing_reports.add(source_value)
            continue
        if not source.is_file():
            missing_reports.add(source_value)
            continue
        markdown = source.read_text(encoding="utf-8", errors="replace")
        for match in IMAGE_RE.finditer(markdown):
            image_ref = match.group(2).strip().strip("<>")
            if not image_ref or "://" in image_ref or image_ref.startswith("data:"):
                invalid_references.add(f"{source_value}: {image_ref}")
                continue
            image = (source.parent / image_ref).resolve()
            try:
                relative = image.relative_to(repository_root).as_posix()
            except ValueError:
                invalid_references.add(f"{source_value}: {image_ref}")
                continue
            if image.suffix.casefold() not in IMAGE_SUFFIXES:
                invalid_references.add(relative)
                continue
            figures.add(relative)
            if not image.is_file():
                missing_figures.add(relative)

    return {
        "figure_paths": figures,
        "figures": len(figures),
        "missing_figures": len(missing_figures),
        "missing_figure_samples": path_sample(missing_figures),
        "missing_reports": len(missing_reports),
        "missing_report_samples": path_sample(missing_reports),
        "invalid_references": len(invalid_references),
        "invalid_reference_samples": path_sample(invalid_references),
    }


def inspect_text_index(
    chunks_path: Path,
    artifact_dir: Path,
    model_id: str,
    model_revision: str,
) -> dict[str, Any]:
    import numpy as np

    manifest_path = artifact_dir / "index-manifest.json"
    vectors_path = artifact_dir / "document-embeddings.f32.npy"
    status = {
        "state": "missing",
        "reasons": [],
        "model_id": model_id,
        "model_revision": model_revision,
        "chunks_expected": 0,
        "chunks_indexed": 0,
        "created_at": None,
    }
    if not chunks_path.exists():
        status["reasons"].append("The chunk corpus is missing.")
        return status
    with chunks_path.open("rb") as handle:
        status["chunks_expected"] = sum(1 for line in handle if line.strip())
    missing = [path.name for path in (manifest_path, vectors_path) if not path.exists()]
    if missing:
        status["reasons"].append(
            "Missing text index files: " + ", ".join(missing) + "."
        )
        return status

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        vectors = np.load(vectors_path, mmap_mode="r")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        status["state"] = "error"
        status["reasons"].append(f"Cannot read the text index: {error}")
        return status

    status["chunks_indexed"] = len(vectors) if vectors.ndim else 0
    status["created_at"] = manifest.get("created_at")
    reasons = status["reasons"]
    if manifest.get("model_id") != model_id:
        reasons.append("The text embedding model changed.")
    if manifest.get("model_revision") != model_revision:
        reasons.append("The text embedding model revision changed.")
    if manifest.get("chunks_sha256") != file_sha256(chunks_path):
        reasons.append("The chunk corpus changed after indexing.")
    if vectors.ndim != 2:
        reasons.append("The text vector array does not have two dimensions.")
    elif len(vectors) != status["chunks_expected"]:
        reasons.append("The text vector count differs from the chunk count.")
    if manifest.get("chunks") != status["chunks_expected"]:
        reasons.append("The text index manifest has a different chunk count.")
    status["state"] = "stale" if reasons else "ready"
    return status


def inspect_visual_index(
    repository_root: Path,
    data_dir: Path,
    figure_sources: dict[str, Any],
    images_path: Path,
    vectors_path: Path,
    manifest_path: Path,
    cache_dir: Path,
    build_state_path: Path,
    model_id: str,
    model_revision: str,
    verify_image_hashes: bool = True,
) -> dict[str, Any]:
    import numpy as np

    expected_paths = figure_sources["figure_paths"]
    cache_paths = list(cache_dir.glob("*.f16.npy")) if cache_dir.exists() else []
    cache_count = len(cache_paths)
    temporary_vectors = vectors_path.with_name(vectors_path.name + ".tmp")
    latest_cache_mtime = max(
        (path.stat().st_mtime for path in cache_paths), default=0.0
    )
    recent_build_activity = (
        temporary_vectors.exists()
        and latest_cache_mtime > 0
        and time.time() - latest_cache_mtime < 120
    )
    build_state: dict[str, Any] = {}
    if build_state_path.exists():
        try:
            build_state = json.loads(build_state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            build_state = {}
    build_active = process_is_running(build_state.get("pid")) or recent_build_activity
    status = {
        "state": "building" if build_active else "missing",
        "reasons": [],
        "model_id": model_id,
        "model_revision": model_revision,
        "images_expected": len(expected_paths),
        "images_metadata": 0,
        "images_indexed": 0,
        "cached_images": cache_count,
        "build_active": build_active,
        "build_started_at": build_state.get("started_at"),
        "build_activity_at": (
            datetime.fromtimestamp(latest_cache_mtime, timezone.utc).isoformat()
            if latest_cache_mtime
            else None
        ),
        "build_completed": int(build_state.get("completed") or cache_count),
        "created_at": None,
        "missing_figures": figure_sources["missing_figures"],
        "missing_figure_samples": figure_sources["missing_figure_samples"],
        "unindexed_figures": len(expected_paths),
        "unindexed_figure_samples": path_sample(expected_paths),
        "changed_figures": 0,
        "changed_figure_samples": [],
        "orphaned_index_records": 0,
    }
    if figure_sources["missing_reports"]:
        status["reasons"].append(
            f"{figure_sources['missing_reports']} report source files are missing."
        )
    if figure_sources["invalid_references"]:
        status["reasons"].append(
            f"{figure_sources['invalid_references']} figure references are invalid."
        )
    missing = [
        path.name
        for path in (images_path, vectors_path, manifest_path)
        if not path.exists()
    ]
    if missing:
        completed = min(
            max(status["build_completed"], cache_count), status["images_expected"]
        )
        status["build_completed"] = completed
        status["unindexed_figures"] = status["images_expected"] - completed
        if completed:
            status["unindexed_figure_samples"] = []
        if build_active:
            status["reasons"].append("The ColPali index build is running.")
        elif cache_count:
            status["state"] = "partial"
            status["reasons"].append(
                f"A resumable build contains {cache_count} cached image embeddings."
            )
        else:
            status["reasons"].append(
                "Missing visual index files: " + ", ".join(missing) + "."
            )
        return status

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = read_jsonl(images_path)
        vectors = np.load(vectors_path, mmap_mode="r")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        status["state"] = "error"
        status["reasons"].append(f"Cannot read the visual index: {error}")
        return status

    metadata_paths = {
        record.get("source_image")
        for record in records
        if isinstance(record.get("source_image"), str)
    }
    unindexed = expected_paths - metadata_paths
    orphaned = metadata_paths - expected_paths
    status.update(
        {
            "images_metadata": len(records),
            "images_indexed": len(vectors) if vectors.ndim else 0,
            "created_at": manifest.get("created_at"),
            "unindexed_figures": len(unindexed),
            "unindexed_figure_samples": path_sample(unindexed),
            "orphaned_index_records": len(orphaned),
        }
    )
    reasons = status["reasons"]
    if manifest.get("model_id") != model_id:
        reasons.append("The visual embedding model changed.")
    if manifest.get("model_revision") != model_revision:
        reasons.append("The visual embedding model revision changed.")
    if manifest.get("images_sha256") != file_sha256(images_path):
        reasons.append("The image metadata changed after indexing.")

    source_files = {
        "reports_sha256": data_dir / "reports.jsonl",
        "units_sha256": data_dir / "units.jsonl",
        "diagram_analyses_sha256": data_dir / "diagram-analyses.jsonl",
    }
    for field, path in source_files.items():
        current_hash = file_sha256(path) if path.exists() else None
        if manifest.get(field) != current_hash:
            reasons.append(f"{path.name} changed after visual indexing.")

    if vectors.ndim != 3:
        reasons.append("The visual vector array does not have three dimensions.")
    elif len(vectors) != len(records):
        reasons.append("The visual vector count differs from the image metadata count.")
    if manifest.get("images") != len(records):
        reasons.append("The visual index manifest has a different image count.")
    if unindexed:
        reasons.append(f"{len(unindexed)} source figures are absent from the index.")
    if orphaned:
        reasons.append(f"{len(orphaned)} index records no longer occur in reports.")
    if status["missing_figures"]:
        reasons.append(
            f"{status['missing_figures']} referenced source figure files are missing."
        )

    if verify_image_hashes:
        changed: set[str] = set()
        for record in records:
            source_image = record.get("source_image")
            expected_hash = record.get("source_image_sha256")
            if not isinstance(source_image, str) or not isinstance(expected_hash, str):
                continue
            path = (repository_root / source_image).resolve()
            try:
                path.relative_to(repository_root.resolve())
            except ValueError:
                changed.add(source_image)
                continue
            if path.is_file() and file_sha256(path) != expected_hash:
                changed.add(source_image)
        status["changed_figures"] = len(changed)
        status["changed_figure_samples"] = path_sample(changed)
        if changed:
            reasons.append(f"{len(changed)} source figures changed after indexing.")

    status["state"] = "stale" if reasons else "ready"
    return status


def inspect_jev_index(
    chunks_path: Path,
    index_path: Path,
    model_id: str,
    content_question_sha256: str,
    content_threshold: float,
) -> dict[str, Any]:
    """Inspect the persistent Jev Noul cache without making an API request."""
    status = {
        "state": "missing",
        "reasons": [],
        "model_id": model_id,
        "chunks_expected": 0,
        "chunks_classified": 0,
        "meaningful_chunks": 0,
        "excluded_chunks": 0,
        "cached_queries": 0,
        "complete_queries": 0,
        "cached_scores": 0,
        "updated_at": None,
    }
    if not chunks_path.exists():
        status["reasons"].append("The chunk corpus is missing.")
        return status
    with chunks_path.open("rb") as handle:
        status["chunks_expected"] = sum(1 for line in handle if line.strip())
    if not index_path.exists():
        status["reasons"].append("No Jev searches have been cached yet.")
        return status

    try:
        connection = sqlite3.connect(index_path, timeout=5)
        try:
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            if version != 1:
                raise ValueError(f"unsupported schema version {version}")
            metadata = dict(connection.execute("SELECT key, value FROM metadata"))
            snapshot_count = int(
                connection.execute("SELECT COUNT(*) FROM corpus_chunks").fetchone()[0]
            )
            classified, meaningful = connection.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(content_scores.noul >= ?), 0)
                FROM corpus_chunks
                JOIN content_scores
                  ON content_scores.chunk_id = corpus_chunks.chunk_id
                 AND content_scores.state_sha256 = corpus_chunks.state_sha256
                 AND content_scores.model_id = ?
                 AND content_scores.question_sha256 = ?
                """,
                (content_threshold, model_id, content_question_sha256),
            ).fetchone()
            cached_queries, complete_queries, updated_at = connection.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(completed), 0), MAX(updated_at)
                FROM searches
                WHERE model_id = ? AND content_question_sha256 = ?
                """,
                (model_id, content_question_sha256),
            ).fetchone()
            cached_scores = connection.execute(
                """
                SELECT COUNT(*)
                FROM query_scores
                JOIN searches USING (search_id)
                WHERE searches.model_id = ?
                  AND searches.content_question_sha256 = ?
                """,
                (model_id, content_question_sha256),
            ).fetchone()[0]
        finally:
            connection.close()
    except (OSError, ValueError, sqlite3.Error) as error:
        status["state"] = "error"
        status["reasons"].append(f"Cannot read the Jev index: {error}")
        return status

    status.update(
        {
            "chunks_classified": int(classified),
            "meaningful_chunks": int(meaningful),
            "excluded_chunks": int(classified) - int(meaningful),
            "cached_queries": int(cached_queries),
            "complete_queries": int(complete_queries),
            "cached_scores": int(cached_scores),
            "updated_at": updated_at or metadata.get("updated_at"),
        }
    )
    reasons = status["reasons"]
    stale = False
    if metadata.get("model_id") != model_id:
        reasons.append("The Jev model changed.")
        stale = True
    if metadata.get("content_question_sha256") != content_question_sha256:
        reasons.append("The Jev content question changed.")
        stale = True
    if metadata.get("corpus_sha256") != file_sha256(chunks_path):
        reasons.append("The chunk corpus changed after the last Jev search.")
        stale = True
    if snapshot_count != status["chunks_expected"]:
        reasons.append("The Jev corpus snapshot has a different chunk count.")
        stale = True
    if status["chunks_classified"] != status["chunks_expected"]:
        reasons.append(
            f"{status['chunks_expected'] - status['chunks_classified']} chunks still "
            "need content classification."
        )
    if stale:
        status["state"] = "stale"
    elif status["chunks_classified"] < status["chunks_expected"]:
        status["state"] = "partial"
    else:
        status["state"] = "ready"
    return status


def inspect_indexes(
    *,
    repository_root: Path,
    data_dir: Path,
    text_artifact_dir: Path,
    text_model_id: str,
    text_model_revision: str,
    images_path: Path,
    visual_vectors_path: Path,
    visual_manifest_path: Path,
    visual_cache_dir: Path,
    visual_build_state_path: Path,
    visual_model_id: str,
    visual_model_revision: str,
    verify_image_hashes: bool = True,
    jev_index_path: Path | None = None,
    jev_model_id: str | None = None,
    jev_content_question_sha256: str | None = None,
    jev_content_threshold: float = 0.5,
) -> dict[str, Any]:
    reports_path = data_dir / "reports.jsonl"
    reports = read_jsonl(reports_path) if reports_path.exists() else []
    figure_sources = inspect_figure_sources(repository_root, reports)
    text = inspect_text_index(
        data_dir / "chunks.jsonl",
        text_artifact_dir,
        text_model_id,
        text_model_revision,
    )
    visual = inspect_visual_index(
        repository_root=repository_root,
        data_dir=data_dir,
        figure_sources=figure_sources,
        images_path=images_path,
        vectors_path=visual_vectors_path,
        manifest_path=visual_manifest_path,
        cache_dir=visual_cache_dir,
        build_state_path=visual_build_state_path,
        model_id=visual_model_id,
        model_revision=visual_model_revision,
        verify_image_hashes=verify_image_hashes,
    )
    states = {text["state"], visual["state"]}
    priority = ("error", "stale", "building", "partial", "missing", "ready")
    overall = next(state for state in priority if state in states)
    jev = None
    if (
        jev_index_path is not None
        and jev_model_id is not None
        and jev_content_question_sha256 is not None
    ):
        jev = inspect_jev_index(
            chunks_path=data_dir / "chunks.jsonl",
            index_path=jev_index_path,
            model_id=jev_model_id,
            content_question_sha256=jev_content_question_sha256,
            content_threshold=jev_content_threshold,
        )
    corpus = {
        "reports": len(reports),
        "figures": figure_sources["figures"],
        "missing_figures": figure_sources["missing_figures"],
        "missing_figure_samples": figure_sources["missing_figure_samples"],
        "missing_reports": figure_sources["missing_reports"],
        "missing_report_samples": figure_sources["missing_report_samples"],
        "invalid_figure_references": figure_sources["invalid_references"],
        "invalid_figure_reference_samples": figure_sources["invalid_reference_samples"],
    }
    payload = {
        "schema_version": "slr1-index-status/v1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "corpus": corpus,
        "text": text,
        "visual": visual,
    }
    if jev is not None:
        payload["jev"] = jev
    return payload
