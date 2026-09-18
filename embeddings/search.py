#!/usr/bin/env python3
"""Search the SLR1 chunk corpus or run its local HTML search interface."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import mimetypes
import os
import re
import shutil
import sys
import threading
import time
import webbrowser
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from build_visual_index import (
    BUILD_STATE_PATH as VISUAL_BUILD_STATE_PATH,
    CACHE_DIR as VISUAL_CACHE_DIR,
    IMAGES_PATH,
    MANIFEST_PATH as VISUAL_MANIFEST_PATH,
    MODEL_ID as COLPALI_MODEL_ID,
    MODEL_REVISION as COLPALI_MODEL_REVISION,
    VECTORS_PATH as VISUAL_VECTORS_PATH,
    encode_queries as encode_visual_queries,
    load_colpali,
)
from image_corpus import image_search_text
from index_status import inspect_indexes


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
ARTIFACT_DIR = SCRIPT_DIR / "artifacts/qwen3-embedding-0.6b"
INCLUDED_REPORTS_PATH = REPO_ROOT / "SLR/SLR1/included_reports.json"
GUI_PATH = SCRIPT_DIR / "search.html"
MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
MODEL_REVISION = "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"
RERANKER_MODEL_ID = "Qwen/Qwen3-Reranker-0.6B"
RERANKER_MODEL_REVISION = "e61197ed45024b0ed8a2d74b80b4d909f1255473"
QUERY_PROMPT = (
    "Instruct: Given a question about MBSE and nanosatellite literature, "
    "retrieve passages that directly answer it. Prefer definitions, explanations, "
    "rationale, and supporting evidence over incidental mentions.\nQuery:"
)
RERANKER_INSTRUCTION = (
    "Given a question about MBSE and nanosatellite literature, judge whether the "
    "document directly answers it. Prefer definitions, explanations, rationale, "
    "and supporting evidence over incidental mentions."
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
QUOTED_PHRASE_RE = re.compile(r'"([^"]+)"')
REPORT_MARKDOWN_RE = re.compile(r"^(review|citation)-report-([0-9]+)\.md$")
SEARCH_MODES = ("hybrid", "vector", "visual", "bm25", "regex")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
SERVED_SUFFIXES = IMAGE_SUFFIXES | {".pdf"}


class SearchError(Exception):
    """A search request that the caller can correct."""


class RegexSearchError(SearchError):
    """A malformed regular expression."""


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def included_report_citations() -> dict[str, dict[str, str]]:
    """Load citation metadata from the authoritative included-report list."""
    try:
        records = json.loads(INCLUDED_REPORTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SearchError(f"Cannot read included reports: {error}") from error
    if not isinstance(records, list):
        raise SearchError(f"Expected a JSON array in {INCLUDED_REPORTS_PATH}")

    citations: dict[str, dict[str, str]] = {}
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise SearchError(f"Included report {index} must be a JSON object")
        source_path = record.get("full_text_markdown")
        publication_type = record.get("publication_type")
        venue = record.get("venue")
        if not isinstance(source_path, str) or not source_path.strip():
            raise SearchError(f"Included report {index} lacks a source path")
        if not isinstance(publication_type, str) or not publication_type.strip():
            raise SearchError(f"Included report {index} lacks a publication type")
        if not isinstance(venue, str) or not venue.strip():
            raise SearchError(f"Included report {index} lacks a venue")
        match = REPORT_MARKDOWN_RE.fullmatch(Path(source_path).name)
        if match is None:
            raise SearchError(f"Cannot derive a report ID from {source_path}")
        report_id = "-".join(match.groups())
        if report_id in citations:
            raise SearchError(f"Duplicate included report ID: {report_id}")
        citations[report_id] = {
            "publication_type": publication_type.strip(),
            "venue": venue.strip(),
        }
    return citations


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def choose_device(torch: Any, requested: str) -> str:
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
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
        processor_kwargs={"padding_side": "right"},
    )
    model.max_seq_length = 768
    return model, device


def embed_questions(model: Any, questions: list[str]):
    import numpy as np

    embeddings = model.encode(
        questions,
        batch_size=min(16, len(questions)),
        prompt=QUERY_PROMPT,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).astype(np.float32)
    if not np.isfinite(embeddings).all():
        raise RuntimeError("Question embeddings contain nonfinite values")
    embeddings /= np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings


def load_qwen_reranker(device: str = "auto") -> tuple[Any, str]:
    os.environ.setdefault("HF_HOME", str(SCRIPT_DIR / ".cache/huggingface"))
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    import torch
    from sentence_transformers import CrossEncoder

    device = choose_device(torch, device)
    dtype = torch.float32 if device == "cpu" else torch.bfloat16
    model = CrossEncoder(
        RERANKER_MODEL_ID,
        revision=RERANKER_MODEL_REVISION,
        device=device,
        max_length=1024,
        prompts={"query": RERANKER_INSTRUCTION},
        model_kwargs={"dtype": dtype, "attn_implementation": "sdpa"},
    )
    return model, device


def maxsim_scores(
    query_embeddings: Any,
    document_vectors: Any,
    device: str,
    batch_size: int = 16,
):
    """Score one ColPali query against a memory-mapped multi-vector index."""
    import numpy as np
    import torch

    query = query_embeddings[0].to(device=device, dtype=torch.float32)
    scores = np.empty(len(document_vectors), dtype=np.float32)
    for start in range(0, len(document_vectors), batch_size):
        end = min(start + batch_size, len(document_vectors))
        documents = torch.from_numpy(
            np.asarray(document_vectors[start:end], dtype=np.float32).copy()
        ).to(device)
        similarities = torch.einsum("qd,bkd->bqk", query, documents)
        scores[start:end] = similarities.amax(dim=2).sum(dim=1).cpu().numpy()
    if not np.isfinite(scores).all():
        raise RuntimeError("ColPali produced nonfinite retrieval scores")
    return scores


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


def regex_scores(pattern: str, chunks: list[dict]):
    """Score original chunk text by the number of case insensitive matches."""
    import numpy as np

    try:
        expression = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        raise RegexSearchError(f"Invalid regular expression: {error}") from error

    scores = np.zeros(len(chunks), dtype=np.float32)
    for index, chunk in enumerate(chunks):
        scores[index] = sum(1 for _ in expression.finditer(chunk["text"]))
    return scores


def exact_match_spans(text: str, question: str, mode: str) -> list[list[int]]:
    """Return code point ranges for exact query matches in original text."""
    if mode == "regex":
        try:
            expression = re.compile(question, re.IGNORECASE)
        except re.error as error:
            raise RegexSearchError(f"Invalid regular expression: {error}") from error
        return [
            [match.start(), match.end()]
            for match in expression.finditer(text)
            if match.end() > match.start()
        ]

    query_terms = set(tokenize(question))
    return [
        [match.start(), match.end()]
        for match in TOKEN_RE.finditer(text)
        if match.group(0).casefold() in query_terms
    ]


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


def normalize_mode(mode: str) -> str:
    mode = mode.casefold()
    if mode == "dense":
        return "vector"
    if mode not in SEARCH_MODES:
        available = ", ".join(SEARCH_MODES)
        raise SearchError(f"Unknown search mode {mode!r}. Choose: {available}.")
    return mode


def repository_path(value: str) -> Path | None:
    """Return an existing repository file without allowing path traversal."""
    path = Path(value)
    candidate = path if path.is_absolute() else REPO_ROOT / path
    try:
        candidate = candidate.resolve()
        candidate.relative_to(REPO_ROOT.resolve())
    except (OSError, ValueError):
        return None
    return candidate if candidate.is_file() else None


def originating_pdf(source_path: str) -> Path | None:
    source = repository_path(source_path)
    if source is None:
        return None
    if source.suffix.casefold() == ".pdf":
        return source

    direct_match = source.with_suffix(".pdf")
    if direct_match.is_file():
        return direct_match

    try:
        pdfs = sorted(
            path
            for path in source.parent.iterdir()
            if path.is_file() and path.suffix.casefold() == ".pdf"
        )
    except OSError:
        return None
    return pdfs[0] if len(pdfs) == 1 else None


def originating_image(chunk: dict, report: dict | None = None) -> Path | None:
    source = repository_path((report or {}).get("source_path", ""))
    for image_ref in chunk.get("image_refs", []):
        image = repository_path(image_ref)
        if image is None and source is not None:
            try:
                relative = (
                    (source.parent / image_ref)
                    .resolve()
                    .relative_to(REPO_ROOT.resolve())
                )
            except (OSError, ValueError):
                relative = None
            if relative is not None:
                image = repository_path(relative.as_posix())
        if image is not None and image.suffix.casefold() in IMAGE_SUFFIXES:
            return image
    return None


def file_url(path: Path, page: int | None = None) -> str:
    relative_path = path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    url = "/file?" + urlencode({"path": relative_path})
    return f"{url}#page={page}" if page else url


class SearchService:
    """Load text, visual, and reranking resources on demand."""

    def __init__(self, device: str = "auto") -> None:
        self.device_requested = device
        self._chunks: list[dict] | None = None
        self._reports: dict[str, dict] | None = None
        self._bm25_data: tuple[list[list[str]], Counter[str], float] | None = None
        self._dense_vectors: Any = None
        self._model: Any = None
        self._device: str | None = None
        self._visual_records: list[dict] | None = None
        self._visual_records_by_path: dict[str, dict] = {}
        self._visual_vectors: Any = None
        self._visual_model: Any = None
        self._visual_processor: Any = None
        self._visual_device: str | None = None
        self._reranker: Any = None
        self._reranker_device: str | None = None
        self._status_cache: dict | None = None
        self._status_cached_at = 0.0
        self._corpus_lock = threading.Lock()
        self._bm25_lock = threading.Lock()
        self._dense_lock = threading.Lock()
        self._visual_lock = threading.Lock()
        self._reranker_lock = threading.Lock()
        self._status_lock = threading.Lock()
        self._search_lock = threading.Lock()

    def index_status(self, refresh: bool = False) -> dict:
        """Return a cached, model-free health check for both indexes."""
        with self._status_lock:
            now = time.monotonic()
            if (
                not refresh
                and self._status_cache is not None
                and now - self._status_cached_at < 30
            ):
                return self._status_cache
            self._status_cache = inspect_indexes(
                repository_root=REPO_ROOT,
                data_dir=DATA_DIR,
                text_artifact_dir=ARTIFACT_DIR,
                text_model_id=MODEL_ID,
                text_model_revision=MODEL_REVISION,
                images_path=IMAGES_PATH,
                visual_vectors_path=VISUAL_VECTORS_PATH,
                visual_manifest_path=VISUAL_MANIFEST_PATH,
                visual_cache_dir=VISUAL_CACHE_DIR,
                visual_build_state_path=VISUAL_BUILD_STATE_PATH,
                visual_model_id=COLPALI_MODEL_ID,
                visual_model_revision=COLPALI_MODEL_REVISION,
            )
            self._status_cached_at = now
            return self._status_cache

    def _load_corpus(self) -> tuple[list[dict], dict[str, dict]]:
        with self._corpus_lock:
            if self._chunks is None or self._reports is None:
                chunks_path = DATA_DIR / "chunks.jsonl"
                if not chunks_path.exists():
                    raise SearchError(f"Chunk corpus is missing: {chunks_path}")
                self._chunks = read_jsonl(chunks_path)
                if not self._chunks:
                    raise SearchError("The chunk corpus is empty.")
                reports_path = DATA_DIR / "reports.jsonl"
                self._reports = {
                    row["report_id"]: row for row in read_jsonl(reports_path)
                }
                citation_metadata = included_report_citations()
                for report_id, report in self._reports.items():
                    report.update(citation_metadata.get(report_id, {}))
        return self._chunks, self._reports

    def _get_bm25_data(self) -> tuple[list[list[str]], Counter[str], float]:
        with self._bm25_lock:
            if self._bm25_data is None:
                chunks, _ = self._load_corpus()
                self._bm25_data = prepare_bm25(chunks)
        return self._bm25_data

    def _dense_scores(self, question: str):
        import numpy as np

        with self._dense_lock:
            chunks, _ = self._load_corpus()
            if self._dense_vectors is None:
                chunks_path = DATA_DIR / "chunks.jsonl"
                manifest_path = ARTIFACT_DIR / "index-manifest.json"
                vectors_path = ARTIFACT_DIR / "document-embeddings.f32.npy"
                if not manifest_path.exists() or not vectors_path.exists():
                    raise SearchError("The Qwen index is missing. Run build_index.py.")
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as error:
                    raise SearchError(
                        f"Cannot read the Qwen index manifest: {error}"
                    ) from error
                if manifest.get("chunks_sha256") != file_sha256(chunks_path):
                    raise SearchError("The Qwen index is stale. Run build_index.py.")
                try:
                    self._dense_vectors = np.load(vectors_path, mmap_mode="r")
                except (OSError, ValueError) as error:
                    raise SearchError(
                        f"Cannot read the Qwen vectors: {error}"
                    ) from error
                if len(self._dense_vectors) != len(chunks):
                    raise SearchError(
                        "The Qwen index and chunk corpus have different row counts."
                    )
                self._model, self._device = load_qwen(self.device_requested)
            question_vector = embed_questions(self._model, [question])[0]
            return self._dense_vectors @ question_vector, self._device

    def _load_visual_index(self) -> tuple[list[dict], Any]:
        import numpy as np

        if self._visual_records is not None and self._visual_vectors is not None:
            return self._visual_records, self._visual_vectors
        if (
            not VISUAL_MANIFEST_PATH.exists()
            or not VISUAL_VECTORS_PATH.exists()
            or not IMAGES_PATH.exists()
        ):
            raise SearchError(
                "The ColPali image index is missing. Run build_visual_index.py."
            )
        try:
            manifest = json.loads(VISUAL_MANIFEST_PATH.read_text(encoding="utf-8"))
            records = read_jsonl(IMAGES_PATH)
            vectors = np.load(VISUAL_VECTORS_PATH, mmap_mode="r")
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise SearchError(
                f"Cannot read the ColPali image index: {error}"
            ) from error
        reports_path = DATA_DIR / "reports.jsonl"
        if (
            manifest.get("model_id") != COLPALI_MODEL_ID
            or manifest.get("model_revision") != COLPALI_MODEL_REVISION
            or manifest.get("images_sha256") != file_sha256(IMAGES_PATH)
            or manifest.get("reports_sha256") != file_sha256(reports_path)
        ):
            raise SearchError(
                "The ColPali image index is stale. Run build_visual_index.py."
            )
        if vectors.ndim != 3 or len(vectors) != len(records):
            raise SearchError(
                "The ColPali image index and image metadata have different shapes."
            )
        self._visual_records = records
        self._visual_records_by_path = {
            record["source_image"]: record for record in records
        }
        self._visual_vectors = vectors
        return records, vectors

    def _visual_scores(self, question: str, batch_size: int = 16):
        with self._visual_lock:
            records, vectors = self._load_visual_index()
            if self._visual_model is None or self._visual_processor is None:
                (
                    self._visual_model,
                    self._visual_processor,
                    self._visual_device,
                ) = load_colpali(self.device_requested)
            query_embeddings = encode_visual_queries(
                self._visual_model,
                self._visual_processor,
                [question],
            )
            scores = maxsim_scores(
                query_embeddings,
                vectors,
                device=self._visual_device or "cpu",
                batch_size=batch_size,
            )
            return scores, records, self._visual_device

    def _rerank_scores(
        self,
        question: str,
        documents: list[str],
        batch_size: int = 4,
    ):
        import numpy as np

        with self._reranker_lock:
            if self._reranker is None:
                self._reranker, self._reranker_device = load_qwen_reranker(
                    self.device_requested
                )
            effective_batch_size = (
                1 if self._reranker_device == "mps" else min(batch_size, len(documents))
            )
            scores = np.asarray(
                self._reranker.predict(
                    [(question, document) for document in documents],
                    prompt=RERANKER_INSTRUCTION,
                    batch_size=effective_batch_size,
                    show_progress_bar=False,
                ),
                dtype=np.float32,
            ).reshape(-1)
        if not np.isfinite(scores).all():
            raise RuntimeError("Qwen reranker produced nonfinite scores")
        return scores

    def _result(
        self,
        chunk: dict,
        report: dict,
        rank: int,
        score: float,
        dense_score: float | None,
        bm25_score: float | None,
        regex_score: float | None,
    ) -> dict:
        image = originating_image(chunk, report)
        display_type = "image" if image is not None else "text"
        source_path = report.get("source_path", "")
        pdf = originating_pdf(source_path)
        image_url = file_url(image) if image is not None else None
        pdf_url = file_url(pdf, chunk.get("page_start")) if pdf is not None else None
        source_url = image_url if image is not None else pdf_url
        source_label = "Open image" if image is not None else "Open PDF"
        result = {
            "rank": rank,
            "score": score,
            "chunk_id": chunk["chunk_id"],
            "report_id": chunk["report_id"],
            "title": chunk["title"],
            "citation": {
                "key": chunk["report_id"],
                "authors": report.get("authors") or [],
                "title": report.get("title") or chunk["title"],
                "year": report.get("publication_year"),
                "publication_type": report.get("publication_type"),
                "venue": report.get("venue"),
                "doi": report.get("doi"),
            },
            "source_path": source_path,
            "section": chunk["section"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "chunk_type": chunk["chunk_type"],
            "text": chunk["text"],
            "display_type": display_type,
            "image_url": image_url,
            "pdf_url": pdf_url,
            "source_url": source_url,
            "source_label": source_label,
        }
        for optional_field in (
            "diagram_id",
            "diagram_part",
            "modeling_language",
            "representation_type",
            "equation_id",
            "equation_label",
            "equation_caption",
            "equation_context_source",
            "equation_part",
            "equation_parts",
            "image_refs",
        ):
            if optional_field in chunk:
                result[optional_field] = chunk[optional_field]
        if dense_score is not None:
            result["dense_score"] = dense_score
        if bm25_score is not None:
            result["bm25_score"] = bm25_score
        if regex_score is not None:
            result["regex_score"] = regex_score
        return result

    def _image_result(
        self,
        record: dict,
        rank: int,
        score: float,
        visual_score: float | None,
        report: dict | None = None,
    ) -> dict:
        image = repository_path(record["source_image"])
        if image is None:
            raise SearchError(f"Indexed image is missing: {record['source_image']}")
        pdf = originating_pdf(record.get("source_path", ""))
        pdf_url = file_url(pdf, record.get("page_start")) if pdf is not None else None
        text_parts = [
            value
            for value in (
                record.get("caption"),
                record.get("visual_summary"),
                record.get("nearby_context"),
            )
            if value
        ]
        report = report or {}
        result = {
            "rank": rank,
            "score": score,
            "chunk_id": record["image_id"],
            "image_id": record["image_id"],
            "report_id": record["report_id"],
            "title": record["title"],
            "citation": {
                "key": record["report_id"],
                "authors": report.get("authors") or [],
                "title": report.get("title") or record["title"],
                "year": report.get("publication_year") or record.get("year"),
                "publication_type": report.get("publication_type"),
                "venue": report.get("venue"),
                "doi": report.get("doi"),
            },
            "source_path": record.get("source_path", ""),
            "section": record.get("section") or "Document",
            "page_start": record.get("page_start"),
            "page_end": record.get("page_end"),
            "chunk_type": "image",
            "text": "\n\n".join(dict.fromkeys(text_parts)),
            "display_type": "image",
            "image_refs": [record["source_image"]],
            "image_url": file_url(image),
            "pdf_url": pdf_url,
            "source_url": file_url(image),
            "source_label": "Open image",
            "is_mbse_diagram": record.get("is_mbse_diagram", False),
        }
        for optional_field in (
            "diagram_id",
            "modeling_language",
            "representation_type",
        ):
            if record.get(optional_field) is not None:
                result[optional_field] = record[optional_field]
        if visual_score is not None:
            result["visual_score"] = visual_score
        return result

    def _chunk_candidate_key(
        self,
        chunk: dict,
        reports: dict[str, dict],
    ) -> tuple[str, str | None]:
        report = reports.get(chunk["report_id"], {})
        image = originating_image(chunk, report)
        if image is None:
            return f"chunk:{chunk['chunk_id']}", None
        source_image = image.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        return f"image:{source_image}", source_image

    def _add_chunk_ranking(
        self,
        candidates: dict[str, dict],
        source_name: str,
        source_scores: Any,
        chunks: list[dict],
        reports: dict[str, dict],
        depth: int,
        positive_only: bool = False,
        constant: int = 60,
    ) -> None:
        import numpy as np

        seen: set[str] = set()
        unique_rank = 0
        for row_index in np.argsort(-source_scores, kind="stable"):
            raw_score = float(source_scores[int(row_index)])
            if positive_only and raw_score <= 0:
                break
            chunk = chunks[int(row_index)]
            key, source_image = self._chunk_candidate_key(chunk, reports)
            if key in seen:
                continue
            seen.add(key)
            unique_rank += 1
            if unique_rank > depth:
                break
            candidate = candidates.setdefault(
                key,
                {
                    "key": key,
                    "fusion_score": 0.0,
                    "source_ranks": {},
                    "raw_scores": {},
                    "chunks": {},
                    "image_record": None,
                    "source_image": source_image,
                },
            )
            candidate["fusion_score"] += 1 / (constant + unique_rank)
            candidate["source_ranks"][source_name] = unique_rank
            candidate["raw_scores"][source_name] = raw_score
            option = candidate["chunks"].setdefault(
                chunk["chunk_id"], {"chunk": chunk, "priority": unique_rank}
            )
            option["priority"] = min(option["priority"], unique_rank)
            if source_image is not None:
                candidate["source_image"] = source_image
                candidate["image_record"] = self._visual_records_by_path.get(
                    source_image
                )

    def _add_visual_ranking(
        self,
        candidates: dict[str, dict],
        visual_scores: Any,
        records: list[dict],
        depth: int,
        constant: int = 60,
    ) -> None:
        import numpy as np

        for rank, row_index in enumerate(
            np.argsort(-visual_scores, kind="stable")[:depth], start=1
        ):
            record = records[int(row_index)]
            source_image = record["source_image"]
            key = f"image:{source_image}"
            candidate = candidates.setdefault(
                key,
                {
                    "key": key,
                    "fusion_score": 0.0,
                    "source_ranks": {},
                    "raw_scores": {},
                    "chunks": {},
                    "image_record": record,
                    "source_image": source_image,
                },
            )
            candidate["fusion_score"] += 1 / (constant + rank)
            candidate["source_ranks"]["visual"] = rank
            candidate["raw_scores"]["visual"] = float(visual_scores[int(row_index)])
            candidate["image_record"] = record

    def _candidate_text(self, candidate: dict) -> str:
        options = sorted(
            candidate["chunks"].values(), key=lambda option: option["priority"]
        )
        parts = []
        if candidate.get("image_record") is not None:
            parts.append(image_search_text(candidate["image_record"]))
            options = options[:2]
        else:
            options = options[:3]
        parts.extend(option["chunk"]["embedding_text"] for option in options)
        return "\n\n".join(dict.fromkeys(parts))

    def _candidate_result(
        self,
        candidate: dict,
        reports: dict[str, dict],
        rank: int,
    ) -> dict:
        options = sorted(
            candidate["chunks"].values(), key=lambda option: option["priority"]
        )
        raw_scores = candidate["raw_scores"]
        if options:
            chunk = options[0]["chunk"]
            result = self._result(
                chunk=chunk,
                report=reports.get(chunk["report_id"], {}),
                rank=rank,
                score=float(candidate["final_score"]),
                dense_score=raw_scores.get("dense"),
                bm25_score=raw_scores.get("bm25"),
                regex_score=None,
            )
            record = candidate.get("image_record")
            if record is not None:
                result["image_id"] = record["image_id"]
                result["is_mbse_diagram"] = record.get("is_mbse_diagram", False)
                if result.get("image_url") is None:
                    image = repository_path(record["source_image"])
                    if image is not None:
                        result["display_type"] = "image"
                        result["image_url"] = file_url(image)
                        result["source_url"] = file_url(image)
                        result["source_label"] = "Open image"
        else:
            image_record = candidate["image_record"]
            result = self._image_result(
                image_record,
                rank=rank,
                score=float(candidate["final_score"]),
                visual_score=raw_scores.get("visual"),
                report=reports.get(image_record["report_id"], {}),
            )
        result["retrieval_sources"] = sorted(candidate["source_ranks"])
        result["source_ranks"] = candidate["source_ranks"]
        if raw_scores.get("visual") is not None:
            result["visual_score"] = raw_scores["visual"]
        if candidate.get("reranker_score") is not None:
            result["reranker_score"] = candidate["reranker_score"]
        return result

    def _hybrid_results(
        self,
        question: str,
        chunks: list[dict],
        reports: dict[str, dict],
        dense_scores: Any,
        lexical_scores: Any,
        top_k: int,
        max_per_report: int | None,
        fusion_depth: int,
        include_visual: bool,
        rerank: bool,
        rerank_depth: int,
    ) -> tuple[list[dict], str | None, bool, list[str]]:
        candidates: dict[str, dict] = {}
        visual_device = None
        visual_search = False
        warnings: list[str] = []
        if include_visual:
            try:
                visual_scores, records, visual_device = self._visual_scores(question)
                visual_search = True
            except SearchError as error:
                visual_scores, records = None, []
                warnings.append(f"Visual search unavailable: {error}")
        else:
            visual_scores, records = None, []

        self._add_chunk_ranking(
            candidates,
            "dense",
            dense_scores,
            chunks,
            reports,
            fusion_depth,
        )
        self._add_chunk_ranking(
            candidates,
            "bm25",
            lexical_scores,
            chunks,
            reports,
            fusion_depth,
            positive_only=True,
        )
        if visual_scores is not None:
            self._add_visual_ranking(
                candidates,
                visual_scores,
                records,
                fusion_depth,
            )

        first_stage = sorted(
            candidates.values(), key=lambda candidate: -candidate["fusion_score"]
        )
        for rank, candidate in enumerate(first_stage, start=1):
            candidate["first_stage_rank"] = rank
            candidate["final_score"] = candidate["fusion_score"]

        final_candidates = first_stage
        if rerank and first_stage:
            pool = first_stage[: max(top_k, rerank_depth)]
            reranker_scores = self._rerank_scores(
                question,
                [self._candidate_text(candidate) for candidate in pool],
            )
            reranked = sorted(
                zip(pool, reranker_scores),
                key=lambda pair: -float(pair[1]),
            )
            for reranker_rank, (candidate, reranker_score) in enumerate(
                reranked, start=1
            ):
                candidate["reranker_score"] = float(reranker_score)
                candidate["final_score"] = 1 / (
                    60 + candidate["first_stage_rank"]
                ) + 1 / (60 + reranker_rank)
            final_candidates = sorted(
                pool, key=lambda candidate: -candidate["final_score"]
            )

        results: list[dict] = []
        report_counts: Counter[str] = Counter()
        for candidate in final_candidates:
            options = sorted(
                candidate["chunks"].values(),
                key=lambda option: option["priority"],
            )
            report_id = (
                options[0]["chunk"]["report_id"]
                if options
                else candidate["image_record"]["report_id"]
            )
            if (
                max_per_report is not None
                and report_counts[report_id] >= max_per_report
            ):
                continue
            report_counts[report_id] += 1
            results.append(
                self._candidate_result(candidate, reports, rank=len(results) + 1)
            )
            if len(results) >= top_k:
                break
        return results, visual_device, visual_search, warnings

    def _search(
        self,
        question: str,
        mode: str,
        top_k: int,
        max_per_report: int | None,
        fusion_depth: int,
        include_visual: bool,
        rerank: bool,
        rerank_depth: int,
    ) -> dict:
        import numpy as np

        chunks, reports = self._load_corpus()
        dense_scores = None
        lexical_scores = None
        regex_match_scores = None
        device = None
        visual_device = None

        if mode in {"vector", "hybrid"}:
            dense_scores, device = self._dense_scores(question)
        if mode in {"bm25", "hybrid"}:
            lexical_scores = bm25_scores(question, *self._get_bm25_data())
        if mode == "regex":
            regex_match_scores = regex_scores(question, chunks)
        if mode == "visual":
            visual_scores, records, visual_device = self._visual_scores(question)
            order = np.argsort(-visual_scores, kind="stable")
            results = []
            report_counts: Counter[str] = Counter()
            for row_index in order:
                record = records[int(row_index)]
                report_id = record["report_id"]
                if (
                    max_per_report is not None
                    and report_counts[report_id] >= max_per_report
                ):
                    continue
                report_counts[report_id] += 1
                results.append(
                    self._image_result(
                        record,
                        rank=len(results) + 1,
                        score=float(visual_scores[int(row_index)]),
                        visual_score=float(visual_scores[int(row_index)]),
                        report=reports.get(report_id, {}),
                    )
                )
                if len(results) >= top_k:
                    break
            return {
                "question": question,
                "mode": mode,
                "device": visual_device,
                "reranked": False,
                "results": results,
            }

        if mode == "hybrid":
            results, visual_device, visual_search, warnings = self._hybrid_results(
                question=question,
                chunks=chunks,
                reports=reports,
                dense_scores=dense_scores,
                lexical_scores=lexical_scores,
                top_k=top_k,
                max_per_report=max_per_report,
                fusion_depth=fusion_depth,
                include_visual=include_visual,
                rerank=rerank,
                rerank_depth=rerank_depth,
            )
            return {
                "question": question,
                "mode": mode,
                "device": device,
                "visual_device": visual_device,
                "reranker_device": self._reranker_device if rerank else None,
                "visual_search_requested": include_visual,
                "visual_search": visual_search,
                "warnings": warnings,
                "reranked": rerank,
                "results": results,
            }

        final_scores = (
            dense_scores
            if mode == "vector"
            else lexical_scores
            if mode == "bm25"
            else regex_match_scores
        )
        if mode in {"bm25", "regex"}:
            matching_rows = np.flatnonzero(final_scores > 0)
            order = matching_rows[
                np.argsort(-final_scores[matching_rows], kind="stable")
            ]
        else:
            order = np.argsort(-final_scores, kind="stable")

        results = []
        report_counts: Counter[str] = Counter()
        for row_index in order:
            chunk = chunks[int(row_index)]
            report_id = chunk["report_id"]
            if (
                max_per_report is not None
                and report_counts[report_id] >= max_per_report
            ):
                continue
            report_counts[report_id] += 1
            results.append(
                self._result(
                    chunk=chunk,
                    report=reports.get(report_id, {}),
                    rank=len(results) + 1,
                    score=float(final_scores[int(row_index)]),
                    dense_score=(
                        float(dense_scores[int(row_index)])
                        if dense_scores is not None
                        else None
                    ),
                    bm25_score=(
                        float(lexical_scores[int(row_index)])
                        if lexical_scores is not None
                        else None
                    ),
                    regex_score=(
                        float(regex_match_scores[int(row_index)])
                        if regex_match_scores is not None
                        else None
                    ),
                )
            )
            if len(results) >= top_k:
                break
        return {
            "question": question,
            "mode": mode,
            "device": device,
            "reranked": False,
            "results": results,
        }

    def search(
        self,
        question: str,
        mode: str = "hybrid",
        top_k: int = 12,
        max_per_report: int | None = 2,
        fusion_depth: int = 1000,
        include_visual: bool = True,
        rerank: bool = True,
        rerank_depth: int = 50,
    ) -> dict:
        question = question.strip()
        if not question:
            raise SearchError("Enter a search query.")
        if top_k < 1:
            raise SearchError("The number of results must be at least 1.")
        if max_per_report is not None and max_per_report < 1:
            raise SearchError("The report limit must be at least 1.")
        if fusion_depth < 1:
            raise SearchError("The fusion depth must be at least 1.")
        if rerank_depth < 1:
            raise SearchError("The reranking depth must be at least 1.")
        mode = normalize_mode(mode)
        with self._search_lock:
            payload = self._search(
                question=question,
                mode=mode,
                top_k=top_k,
                max_per_report=max_per_report,
                fusion_depth=fusion_depth,
                include_visual=include_visual,
                rerank=rerank and mode == "hybrid",
                rerank_depth=rerank_depth,
            )
        for result in payload["results"]:
            if result.get("display_type") == "text":
                result["exact_match_spans"] = exact_match_spans(
                    result.get("text", ""), question, mode
                )
        return payload


def page_range(result: dict) -> str:
    start = result.get("page_start")
    end = result.get("page_end")
    if start is None:
        return "page unavailable"
    if end is not None and end != start:
        return f"pp. {start}-{end}"
    return f"p. {start}"


def main(args: argparse.Namespace) -> int:
    if getattr(args, "serve", False):
        return serve_gui(args)

    questions = args.query or [line.strip() for line in sys.stdin if line.strip()]
    if not questions:
        raise SystemExit(
            "Supply --query or newline separated questions on standard input"
        )

    service = SearchService(args.device)
    try:
        output = [
            service.search(
                question,
                mode=args.mode,
                top_k=args.top_k,
                max_per_report=args.max_per_report,
                fusion_depth=args.fusion_depth,
                include_visual=not args.no_visual,
                rerank=not args.no_rerank,
                rerank_depth=args.rerank_depth,
            )
            for question in questions
        ]
    except SearchError as error:
        raise SystemExit(str(error)) from error

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    for row in output:
        print(f"\n# {row['question']}")
        for warning in row.get("warnings", []):
            print(f"Warning: {warning}", file=sys.stderr)
        for result in row["results"]:
            excerpt = " ".join(result["text"].split())[: args.excerpt_chars]
            image = ""
            if result["display_type"] == "image":
                image = f"\n   Image: {result.get('image_refs', [''])[0]}"
            print(
                f"\n{result['rank']}. {result['report_id']} | {page_range(result)} | "
                f"{result['title']}\n   {result['section']}{image}\n   {excerpt}"
            )
    return 0


def query_integer(
    parameters: dict[str, list[str]],
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    value = parameters.get(name, [str(default)])[0]
    try:
        value = int(value)
    except ValueError as error:
        raise SearchError(f"{name} must be a whole number.") from error
    if not minimum <= value <= maximum:
        raise SearchError(f"{name} must be between {minimum} and {maximum}.")
    return value


def query_boolean(parameters: dict[str, list[str]], name: str, default: bool) -> bool:
    value = parameters.get(name, ["1" if default else "0"])[0].casefold()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise SearchError(f"{name} must be true or false.")


def make_gui_handler(
    service: SearchService,
    *,
    include_visual: bool = True,
    rerank: bool = True,
    rerank_depth_default: int = 50,
    max_per_report_default: int = 2,
):
    """Build an HTTP handler that only serves the GUI and source assets."""

    class SearchHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            request = urlparse(self.path)
            if request.path in {"/", "/index.html"}:
                self.send_file(GUI_PATH, "text/html; charset=utf-8", cache=False)
                return
            if request.path == "/api/search":
                self.search(request)
                return
            if request.path == "/api/status":
                self.index_status(request)
                return
            if request.path == "/file":
                self.source_file(request)
                return
            self.send_json({"error": "Not found."}, 404)

        def search(self, request) -> None:
            parameters = parse_qs(request.query, keep_blank_values=True)
            query = parameters.get("q", [""])[0]
            mode = parameters.get("mode", ["hybrid"])[0]
            try:
                top_k = query_integer(parameters, "top_k", 12, 1, 100)
                max_per_report = query_integer(
                    parameters, "max_per_report", max_per_report_default, 1, 100
                )
                rerank_depth = query_integer(
                    parameters, "rerank_depth", rerank_depth_default, 1, 1000
                )
                result = service.search(
                    query,
                    mode=mode,
                    top_k=top_k,
                    max_per_report=max_per_report,
                    include_visual=query_boolean(parameters, "visual", include_visual),
                    rerank=query_boolean(parameters, "rerank", rerank),
                    rerank_depth=rerank_depth,
                )
            except SearchError as error:
                self.send_json({"error": str(error)}, 400)
                return
            except Exception as error:  # pragma: no cover - model failures are local
                self.send_json({"error": str(error) or "Search failed."}, 500)
                return
            self.send_json(result)

        def index_status(self, request) -> None:
            parameters = parse_qs(request.query, keep_blank_values=True)
            try:
                refresh = query_boolean(parameters, "refresh", False)
                payload = service.index_status(refresh=refresh)
            except SearchError as error:
                self.send_json({"error": str(error)}, 400)
                return
            except Exception as error:  # pragma: no cover - local file failures
                self.send_json({"error": str(error) or "Status check failed."}, 500)
                return
            self.send_json(payload)

        def source_file(self, request) -> None:
            parameters = parse_qs(request.query, keep_blank_values=True)
            requested_path = parameters.get("path", [""])[0]
            path = repository_path(requested_path)
            if path is None or path.suffix.casefold() not in SERVED_SUFFIXES:
                self.send_json({"error": "Source file not found."}, 404)
                return
            media_type = (
                mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            )
            self.send_file(path, media_type)

        def send_json(self, payload: dict, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_file(self, path: Path, media_type: str, cache: bool = True) -> None:
            try:
                size = path.stat().st_size
                handle = path.open("rb")
            except OSError:
                self.send_json({"error": "Source file not found."}, 404)
                return
            with handle:
                self.send_response(200)
                self.send_header("Content-Type", media_type)
                self.send_header("Content-Length", str(size))
                self.send_header("X-Content-Type-Options", "nosniff")
                if not cache:
                    self.send_header("Cache-Control", "no-store")
                self.end_headers()
                shutil.copyfileobj(handle, self.wfile)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return SearchHandler


def serve_gui(args: argparse.Namespace) -> int:
    service = SearchService(args.device)
    handler = make_gui_handler(
        service,
        include_visual=not args.no_visual,
        rerank=not args.no_rerank,
        rerank_depth_default=args.rerank_depth,
        max_per_report_default=args.max_per_report,
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    host, port = server.server_address[:2]
    browser_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    url = f"http://{browser_host}:{port}/"
    print(f"Search GUI available at {url}")
    print("Press Ctrl-C to stop the server.")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSearch GUI stopped.")
    finally:
        server.server_close()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("hybrid", "vector", "dense", "visual", "bm25", "regex"),
        default="hybrid",
    )
    parser.add_argument("--device", default="auto")
    parser.add_argument("--query", action="append")
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--max-per-report", type=int, default=2)
    parser.add_argument("--fusion-depth", type=int, default=1000)
    parser.add_argument("--rerank-depth", type=int, default=50)
    parser.add_argument(
        "--no-visual",
        action="store_true",
        help="Exclude ColPali image retrieval from hybrid search.",
    )
    parser.add_argument(
        "--no-rerank",
        action="store_true",
        help="Do not rerank hybrid candidates with Qwen3-Reranker.",
    )
    parser.add_argument("--excerpt-chars", type=int, default=500)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--serve", action="store_true", help="Run the local HTML GUI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--open",
        "--open-browser",
        dest="open_browser",
        action="store_true",
        help="Open the GUI in the default browser.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
