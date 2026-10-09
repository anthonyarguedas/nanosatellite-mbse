from __future__ import annotations

import argparse
import json
import sys
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_jev_content_index
import prepare_corpus
from search import (
    GUI_PATH,
    JEV_CONTENT_QUESTION_ID,
    JevSearchIndex,
    SearchError,
    SearchService,
    canonical_report_code,
    file_sha256,
    jev_chunk_state,
    json_sha256,
    make_gui_handler,
    normalize_standard_filter,
    parse_args,
    prepare_bm25,
    read_jsonl,
    resolve_report_filter,
    standard_filter_allows,
)


class StandardCorpusTests(unittest.TestCase):
    def test_discovery_preserves_frontmatter_and_uses_heading_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            standards = root / "SLR/SLR1/pdfs/standards"
            preview = standards / "iso-preview/iso-preview.md"
            preview.parent.mkdir(parents=True)
            preview.write_text(
                "---\ntitle: >\n  Cube satellite\n  specification preview\n"
                "edition: First edition, 2017-06, confirmed 2024\n"
                "availability: preview\nstatus_label: PREVIEW ONLY\n"
                "document_type: standard preview\n"
                "source_url: https://example.org/preview.pdf\n"
                "source_note: This is a preview.\n---\n"
                "<!-- PDF_PAGE: 2 -->\n## Requirements\nBattery requirements.\n",
                encoding="utf-8",
            )
            note = standards / "access-note.md"
            note.write_text(
                "# Source access\n\nContact the agency.\n", encoding="utf-8"
            )
            with (
                patch("prepare_corpus.REPO_ROOT", root),
                patch("prepare_corpus.STANDARDS_DIR", standards),
            ):
                sources = list(prepare_corpus.standard_sources())

        self.assertEqual(
            [row[0]["report_id"] for row in sources],
            [
                "standard-access-note",
                "standard-iso-preview",
            ],
        )
        self.assertEqual(sources[0][0]["title"], "Source access")
        report, path, source_kind = sources[1]
        self.assertEqual(report["title"], "Cube satellite specification preview")
        self.assertEqual(report["publication_year"], 2017)
        self.assertEqual(report["corpus_collection"], "standards")
        self.assertEqual(report["availability"], "preview")
        self.assertEqual(report["source_note"], "This is a preview.")
        self.assertEqual(report["source_url"], "https://example.org/preview.pdf")
        self.assertIsNone(report["screening_record_id"])
        self.assertEqual(source_kind, "standards_markdown")
        self.assertEqual(path, preview)

    def test_discovery_without_frontmatter_or_headings_uses_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "guidelines.md").write_text(
                "Keep stored energy safe.\n", encoding="utf-8"
            )
            with (
                patch("prepare_corpus.REPO_ROOT", root),
                patch("prepare_corpus.STANDARDS_DIR", root),
            ):
                report, _, _ = next(prepare_corpus.standard_sources())
        self.assertEqual(report["title"], "guidelines")
        self.assertIsNone(report["publication_year"])

    def test_discovery_rejects_duplicate_ids_and_invalid_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first/doc.md"
            second = root / "second/doc.md"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_text("# First\n", encoding="utf-8")
            second.write_text("# Second\n", encoding="utf-8")
            with (
                patch("prepare_corpus.REPO_ROOT", root),
                patch("prepare_corpus.STANDARDS_DIR", root),
            ):
                with self.assertRaisesRegex(ValueError, "Duplicate standard report ID"):
                    list(prepare_corpus.standard_sources())
                second.unlink()
                first.write_text("---\n- title\n---\nText\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "frontmatter to be a mapping"):
                    list(prepare_corpus.standard_sources())
                first.write_text("---\ntitle: [\n---\nText\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Invalid standard frontmatter"):
                    list(prepare_corpus.standard_sources())

    def test_build_adds_standards_without_changing_included_report_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            standards = root / "SLR/SLR1/pdfs/standards"
            standards.mkdir(parents=True)
            standard = standards / "cds.md"
            standard.write_text(
                "---\ntitle: CubeSat Design Specification\nedition: Revision 14.1, 2022\n"
                "availability: complete\n---\n<!-- PDF_PAGE: 4 -->\n"
                "## Battery safety\nThe battery shall have inhibit switches.\n",
                encoding="utf-8",
            )
            paper = root / "paper.md"
            paper.write_text(
                "## Results\nThe power model was verified.\n", encoding="utf-8"
            )
            included_list = root / "SLR/SLR1/included_reports.json"
            included_list.write_text("[]\n", encoding="utf-8")
            data = root / "embeddings/data"
            with (
                patch("prepare_corpus.REPO_ROOT", root),
                patch("prepare_corpus.STANDARDS_DIR", standards),
                patch("prepare_corpus.INCLUDED_REPORTS_PATH", included_list),
                patch("prepare_corpus.DATA_DIR", data),
                patch("prepare_corpus.build_diagram_chunks", return_value=[]),
            ):
                sources = [
                    (
                        {
                            "report_id": "review-0001",
                            "screening_record_id": "review-candidate-0001",
                            "title": "Power model",
                        },
                        paper,
                        "preferred_markdown",
                    ),
                    *prepare_corpus.standard_sources(),
                ]
                with patch(
                    "prepare_corpus.expected_sources", return_value=iter(sources)
                ):
                    manifest = prepare_corpus.build(
                        argparse.Namespace(
                            target_words=180,
                            max_words=300,
                            overlap_words=30,
                            allow_missing=False,
                        )
                    )
            reports = read_jsonl(data / "reports.jsonl")
            chunks = read_jsonl(data / "chunks.jsonl")

        self.assertEqual(manifest["counts"]["directly_included_records"], 1)
        self.assertEqual(manifest["counts"]["standards_indexed"], 1)
        self.assertEqual(manifest["counts"]["reports_indexed"], 2)
        self.assertEqual(reports[1]["source_path"], "SLR/SLR1/pdfs/standards/cds.md")
        self.assertEqual(chunks[1]["report_id"], "standard-cds")
        self.assertEqual(chunks[1]["page_start"], 4)
        self.assertEqual(chunks[1]["section"], "Battery safety")
        self.assertIn("Source code: cds", chunks[1]["embedding_text"])
        self.assertIn("Edition: Revision 14.1, 2022", chunks[1]["embedding_text"])
        self.assertNotIn("availability:", chunks[1]["text"])


class StandardSearchTests(unittest.TestCase):
    def test_standard_filter_is_validated_and_independent_of_publication_type(
        self,
    ) -> None:
        self.assertEqual(normalize_standard_filter("ONLY"), "only")
        standard = {
            "corpus_collection": "standards",
            "document_type": "policy strategy",
        }
        review = {"publication_type": "review"}
        for value, allowed in (("include", True), ("exclude", False), ("only", True)):
            self.assertEqual(standard_filter_allows(standard, value), allowed)
        self.assertFalse(standard_filter_allows(review, "only"))
        self.assertTrue(standard_filter_allows(review, "exclude"))
        with self.assertRaisesRegex(SearchError, "Unknown standards filter"):
            SearchService().search("battery", standards="unknown")

    def test_cli_and_gui_offer_the_three_standard_filters(self) -> None:
        for value in ("include", "exclude", "only"):
            with patch.object(sys, "argv", ["search.py", "--standards", value]):
                self.assertEqual(parse_args().standards, value)
        with patch.object(sys, "argv", ["search.py"]):
            self.assertEqual(parse_args().standards, "include")
        html = GUI_PATH.read_text(encoding="utf-8")
        self.assertIn('name="standards" value="include" checked', html)
        self.assertIn('name="standards" value="exclude"', html)
        self.assertIn('name="standards" value="only"', html)
        self.assertIn("standards: selectedStandards()", html)

    def test_standard_report_codes_resolve_filename_and_title(self) -> None:
        report = {
            "report_id": "standard-cds-14.1",
            "title": "CubeSat Design Specification",
            "source_path": "SLR/SLR1/pdfs/standards/cds-14.1/cds-14.1.md",
        }
        reports = {report["report_id"]: report}
        self.assertEqual(canonical_report_code(report["report_id"]), "cds-14.1")
        for query in ("standard-cds-14.1", "cds-14.1", "design specification"):
            self.assertEqual(resolve_report_filter(query, reports), report)

    def test_all_search_modes_apply_standard_and_review_filters_before_depth(
        self,
    ) -> None:
        import numpy as np

        ids = ["review-0001", "review-0002", "standard-cds"]
        reports = {
            ids[0]: {"publication_type": "review"},
            ids[1]: {"publication_type": "journal_article"},
            ids[2]: {"corpus_collection": "standards"},
        }
        chunks = [
            {
                "chunk_id": f"{report_id}:chunk-00001",
                "report_id": report_id,
                "title": report_id,
                "section": "Battery",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Battery safety evidence.",
                "embedding_text": "Battery safety evidence.",
            }
            for report_id in ids
        ]
        records = [
            {
                "report_id": report_id,
                "title": report_id,
                "image_id": f"{report_id}--image",
                "source_image": f"images/{report_id}.png",
            }
            for report_id in ids
        ]
        scores = np.array([3.0, 2.0, 1.0], dtype=np.float32)
        service = SearchService()
        service._load_corpus = lambda: (chunks, reports)
        service._get_bm25_data = lambda: prepare_bm25(chunks)
        service._dense_scores = lambda query: (scores, "cpu")
        service._jev_content_filter = lambda corpus: (
            np.ones(3),
            np.ones(3, dtype=bool),
            {},
        )
        service._jev_search_scores = lambda query, corpus: (scores, np.ones(3), {})
        service._visual_scores = lambda query: (scores, records, "cpu")
        service._rerank_scores = lambda query, docs: np.ones(len(docs))
        service._image_result = lambda record, **options: {
            "report_id": record["report_id"],
            "display_type": "image",
            "chunk_id": record["image_id"],
        }
        cases = [
            ("only", "include", {ids[2]}),
            ("exclude", "include", {ids[0], ids[1]}),
            ("include", "exclude", {ids[1], ids[2]}),
            ("exclude", "only", {ids[0]}),
            ("only", "only", set()),
        ]
        for mode in ("vector", "hybrid", "jev", "bm25", "regex", "visual"):
            for rerank in (False, True):
                for standards, reviews, allowed in cases:
                    with self.subTest(
                        mode=mode, rerank=rerank, standards=standards, reviews=reviews
                    ):
                        payload = service.search(
                            "battery",
                            mode=mode,
                            rerank=rerank,
                            standards=standards,
                            reviews=reviews,
                            top_k=10,
                            fusion_depth=1,
                            rerank_depth=1,
                        )
                        returned = {row["report_id"] for row in payload["results"]}
                        self.assertTrue(returned <= allowed)
                        self.assertEqual(bool(returned), bool(allowed))
                        self.assertEqual(payload["standards"], standards)
                        if standards == "only" and allowed:
                            self.assertEqual(returned, {ids[2]})

    def test_unclassified_standards_remain_queryable_without_inventing_nouls(
        self,
    ) -> None:
        import numpy as np

        chunks = [
            {
                "chunk_id": f"{report_id}:chunk-1",
                "report_id": report_id,
                "title": report_id,
                "section": "Safety",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Battery safety.",
                "embedding_text": "Battery safety.",
            }
            for report_id in ("review-0001", "review-0002", "standard-cds")
        ]
        reports = {chunk["report_id"]: {} for chunk in chunks}
        reports["standard-cds"]["corpus_collection"] = "standards"
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            chunks_path = data / "chunks.jsonl"
            prepare_corpus.jsonl_write(chunks_path, chunks)
            service = SearchService(jev_index_path=data / "index.sqlite3")
            states = [
                (chunk["chunk_id"], json_sha256(jev_chunk_state(chunk)))
                for chunk in chunks
            ]
            with JevSearchIndex(service.jev_index_path) as index:
                index.sync_corpus(states, file_sha256(chunks_path))
                for (chunk_id, state_sha256), noul in zip(states, (0.9, 0.1)):
                    index.save_evaluation(
                        search_id="",
                        chunk_id=chunk_id,
                        state_sha256=state_sha256,
                        query_noul=None,
                        content_noul=noul,
                    )
            service._load_corpus = lambda: (chunks, reports)
            service._dense_scores = lambda query: (np.ones(3), "cpu")
            service._rerank_scores = lambda query, documents: np.ones(len(documents))
            with patch("search.DATA_DIR", data):
                scores, eligible, stats = service._jev_content_filter(chunks)
                self.assertTrue(np.isnan(scores[2]))
                self.assertEqual(eligible.tolist(), [True, False, True])
                self.assertEqual(stats["classified_chunks"], 2)
                self.assertEqual(stats["unclassified_chunks"], 1)
                for rerank in (False, True):
                    payload = service.search(
                        "battery", mode="vector", standards="only", rerank=rerank
                    )
                    self.assertEqual(payload["results"][0]["report_id"], "standard-cds")
                    self.assertNotIn("meaningful_content_noul", payload["results"][0])
                    self.assertIn(
                        "await Jev content classification", payload["warnings"][0]
                    )
                    json.dumps(payload, allow_nan=False)

    def test_results_preserve_preview_status_and_external_source_url(self) -> None:
        result = SearchService()._result(
            chunk={
                "chunk_id": "standard-iso:chunk-00001",
                "report_id": "standard-iso",
                "title": "Cube satellites",
                "section": "Scope",
                "page_start": 2,
                "page_end": 2,
                "chunk_type": "passage",
                "text": "Preview evidence.",
            },
            report={
                "corpus_collection": "standards",
                "availability": "preview",
                "status_label": "PREVIEW ONLY",
                "edition": "2017",
                "source_url": "https://example.org/preview.pdf",
            },
            rank=1,
            score=1.0,
            dense_score=None,
            bm25_score=None,
            regex_score=None,
        )
        self.assertEqual(result["availability"], "preview")
        self.assertEqual(result["status_label"], "PREVIEW ONLY")
        self.assertEqual(result["source_url"], "https://example.org/preview.pdf")
        self.assertEqual(result["source_label"], "Open source")

    def test_api_passes_standard_filter_and_rejects_invalid_values(self) -> None:
        service = SearchService()
        service._load_corpus = lambda: ([], {})
        service._search = Mock(return_value={"results": []})
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), make_gui_handler(service, standards="only")
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for query, expected_status, expected_filter in (
                ("", 200, "only"),
                ("&standards=exclude", 200, "exclude"),
                ("&standards=invalid", 400, None),
            ):
                connection = HTTPConnection(*server.server_address)
                try:
                    connection.request("GET", f"/api/search?q=battery&mode=bm25{query}")
                    response = connection.getresponse()
                    payload = json.loads(response.read())
                    self.assertEqual(response.status, expected_status)
                    if expected_filter:
                        self.assertEqual(payload["standards"], expected_filter)
                        self.assertEqual(
                            service._search.call_args.kwargs["standard_filter"],
                            expected_filter,
                        )
                    else:
                        self.assertIn("Unknown standards filter", payload["error"])
                finally:
                    connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


class JevContentBuildTests(unittest.TestCase):
    @staticmethod
    def response():
        return SimpleNamespace(
            nouls={JEV_CONTENT_QUESTION_ID: SimpleNamespace(noul=0.9)}
        )

    def test_content_build_reuses_scores_and_never_scores_a_search_query(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            chunks = [{"chunk_id": "standard-cds:chunk-1", "text": "Battery safety."}]
            chunks_path = data / "chunks.jsonl"
            prepare_corpus.jsonl_write(chunks_path, chunks)
            service = SearchService(jev_index_path=data / "index.sqlite3")
            client = Mock()
            client.system_one.return_value = self.response()
            service._get_jev_client = Mock(return_value=client)
            with patch("build_jev_content_index.DATA_DIR", data):
                first = build_jev_content_index.build(service, workers=1)
                second = build_jev_content_index.build(service, workers=1)
                chunks[0]["text"] = "Revised battery safety."
                prepare_corpus.jsonl_write(chunks_path, chunks)
                changed = build_jev_content_index.build(service, workers=1)
            with JevSearchIndex(service.jev_index_path) as index:
                self.assertEqual(index.content_scores(), {chunks[0]["chunk_id"]: 0.9})
                self.assertEqual(
                    index.connection.execute(
                        "SELECT COUNT(*) FROM query_scores"
                    ).fetchone()[0],
                    0,
                )
        self.assertEqual(first["api_calls"], 1)
        self.assertEqual(second["api_calls"], 0)
        self.assertEqual(second["reused_chunks"], 1)
        self.assertEqual(changed["api_calls"], 1)
        self.assertEqual(service._get_jev_client.call_count, 2)
        for call in client.system_one.call_args_list:
            self.assertEqual(set(call.kwargs["questions"]), {JEV_CONTENT_QUESTION_ID})

    def test_content_build_failure_retains_completed_scores_for_resume(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            chunks = [
                {"chunk_id": "standard-cds:chunk-1", "text": "Battery safety."},
                {"chunk_id": "standard-cds:chunk-2", "text": "Inhibit switches."},
            ]
            prepare_corpus.jsonl_write(data / "chunks.jsonl", chunks)
            service = SearchService(jev_index_path=data / "index.sqlite3")
            client = Mock()
            client.system_one.side_effect = [self.response(), RuntimeError("offline")]
            service._get_jev_client = lambda: client
            with patch("build_jev_content_index.DATA_DIR", data):
                with self.assertRaisesRegex(SearchError, "caching 1 new scores"):
                    build_jev_content_index.build(service, workers=1)
                client.system_one.side_effect = None
                client.system_one.return_value = self.response()
                resumed = build_jev_content_index.build(service, workers=1)
        self.assertEqual(resumed["reused_chunks"], 1)
        self.assertEqual(resumed["api_calls"], 1)


if __name__ == "__main__":
    unittest.main()
