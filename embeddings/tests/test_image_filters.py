from __future__ import annotations

import json
import sys
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import Mock, patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import (
    REPO_ROOT,
    SearchError,
    SearchService,
    make_gui_handler,
    normalize_image_filter,
    parse_args,
    prepare_bm25,
)


class ImageFilterTests(unittest.TestCase):
    def test_image_filter_is_validated(self) -> None:
        self.assertEqual(normalize_image_filter("ONLY"), "only")
        with self.assertRaisesRegex(SearchError, "Unknown image filter"):
            SearchService().search("evidence", images="invalid")
        with self.assertRaisesRegex(SearchError, "cannot be combined"):
            SearchService().search("evidence", images="exclude", images_only=True)

    def test_cli_offers_all_image_filters_and_keeps_the_legacy_flag(self) -> None:
        for value in ("include", "exclude", "only"):
            with patch.object(sys, "argv", ["search.py", "--images", value]):
                self.assertEqual(parse_args().images, value)
        with patch.object(sys, "argv", ["search.py"]):
            self.assertEqual(parse_args().images, "include")
        with patch.object(sys, "argv", ["search.py", "--images-only"]):
            self.assertTrue(parse_args().images_only)

    def test_image_filters_apply_before_depth_in_every_search_mode(self) -> None:
        import numpy as np

        image_path = Path(__file__).resolve()
        source_image = image_path.relative_to(REPO_ROOT).as_posix()
        ids = ["review-0001", "review-0002"]
        reports = {report_id: {} for report_id in ids}
        chunks = [
            {
                "chunk_id": f"{report_id}:chunk-1",
                "report_id": report_id,
                "title": report_id,
                "section": "Evidence",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Evidence about CubeSats.",
                "embedding_text": "Evidence about CubeSats.",
                "image_refs": [source_image] if index == 0 else [],
            }
            for index, report_id in enumerate(ids)
        ]
        records = [
            {
                "report_id": ids[0],
                "title": ids[0],
                "image_id": "image-1",
                "source_image": source_image,
            }
        ]
        scores = np.array([3.0, 2.0], dtype=np.float32)
        service = SearchService()
        service._load_corpus = lambda: (chunks, reports)
        service._get_bm25_data = lambda: prepare_bm25(chunks)
        service._dense_scores = lambda query: (scores, "cpu")
        service._jev_content_filter = lambda corpus: (
            np.ones(2),
            np.ones(2, dtype=bool),
            {},
        )
        service._jev_search_scores = lambda query, corpus: (scores, np.ones(2), {})
        service._visual_scores = Mock(return_value=(np.array([10.0]), records, "cpu"))
        service._visual_records_by_path = {source_image: records[0]}
        service._rerank_scores = lambda query, docs: np.ones(len(docs))
        service._image_result = lambda record, **options: {
            "report_id": record["report_id"],
            "display_type": "image",
            "chunk_id": record["image_id"],
        }

        def fake_image(chunk, report=None):
            return image_path if chunk.get("image_refs") else None

        with patch("search.originating_image", side_effect=fake_image):
            for mode in ("vector", "hybrid", "jev", "bm25", "regex", "visual"):
                for rerank in (False, True):
                    for images in ("include", "exclude", "only"):
                        with self.subTest(mode=mode, rerank=rerank, images=images):
                            service._visual_scores.reset_mock()
                            payload = service.search(
                                "evidence",
                                mode=mode,
                                images=images,
                                rerank=rerank,
                                top_k=1,
                                fusion_depth=1,
                                rerank_depth=1,
                            )
                            expected = (
                                set()
                                if mode == "visual" and images == "exclude"
                                else {ids[1] if images == "exclude" else ids[0]}
                            )
                            self.assertEqual(
                                {row["report_id"] for row in payload["results"]},
                                expected,
                            )
                            self.assertEqual(payload["images"], images)
                            if images == "exclude":
                                service._visual_scores.assert_not_called()
                                self.assertTrue(
                                    all(
                                        row["display_type"] == "text"
                                        for row in payload["results"]
                                    )
                                )

    def test_api_accepts_image_filters_and_the_legacy_flag(self) -> None:
        service = SearchService()
        service._load_corpus = lambda: ([], {})
        service._search = Mock(return_value={"results": []})
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_gui_handler(service))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for query, expected_status, expected_filter in (
                ("", 200, "include"),
                ("&images=exclude", 200, "exclude"),
                ("&images=only", 200, "only"),
                ("&images_only=1", 200, "only"),
                ("&images=invalid", 400, None),
                ("&images=exclude&images_only=1", 400, None),
            ):
                with self.subTest(query=query):
                    connection = HTTPConnection(*server.server_address)
                    try:
                        connection.request("GET", f"/api/search?q=evidence{query}")
                        response = connection.getresponse()
                        payload = json.loads(response.read())
                        self.assertEqual(response.status, expected_status)
                        if expected_filter:
                            self.assertEqual(payload["images"], expected_filter)
                            options = service._search.call_args.kwargs
                            self.assertEqual(options["image_filter"], expected_filter)
                            self.assertEqual(
                                options["images_only"], expected_filter == "only"
                            )
                        else:
                            self.assertIn("error", payload)
                    finally:
                        connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
