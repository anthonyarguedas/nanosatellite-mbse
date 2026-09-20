from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import (
    GUI_PATH,
    JEV_CONTENT_QUESTION_ID,
    JEV_CONTENT_QUESTION_SHA256,
    JEV_CONTENT_THRESHOLD,
    JEV_MAX_RETRIES,
    JEV_MODEL_ID,
    JEV_REQUEST_TIMEOUT_SECONDS,
    JEV_RERANKER_QUESTION,
    JEV_RERANKER_QUESTION_ID,
    JEV_SEARCH_QUESTION_ID,
    QUERY_PROMPT,
    SearchError,
    SearchService,
    bm25_scores,
    canonical_report_code,
    embed_questions,
    exact_match_spans,
    file_sha256,
    included_report_citations,
    jev_chunk_state,
    jev_search_question,
    maxsim_scores,
    normalize_mode,
    normalize_reranker,
    normalize_review_filter,
    prepare_bm25,
    regex_scores,
    reranked_rank_fusion_score,
    resolve_report_filter,
    review_filter_allows,
    typesafe_api_key,
)
from index_status import inspect_jev_index


class SearchTests(unittest.TestCase):
    def test_gui_defaults_to_vector_with_filter_and_reranker_controls(self) -> None:
        html = GUI_PATH.read_text(encoding="utf-8")

        self.assertIn('name="mode" value="vector" checked', html)
        self.assertIn('name="mode" value="jev"', html)
        self.assertNotIn('name="mode" value="visual"', html)
        self.assertIn('id="images-only" type="checkbox"', html)
        self.assertIn('name="reviews" value="include" checked', html)
        self.assertIn('name="reviews" value="exclude"', html)
        self.assertIn('name="reviews" value="only"', html)
        self.assertIn('review: "article"', html)
        self.assertIn('name="reranker" value="off"', html)
        self.assertIn('name="reranker" value="qwen" checked', html)
        self.assertIn('name="reranker" value="jev"', html)
        self.assertIn(
            '["hybrid", "vector", "jev", "bm25", "regex"].includes(mode)',
            html,
        )

    def test_jev_query_is_in_the_noul_instructions(self) -> None:
        query = "How is a CubeSat power budget verified?"
        question = jev_search_question(query)
        state = jev_chunk_state(
            {
                "title": "Power verification",
                "section": "Results",
                "chunk_type": "passage",
                "text": "The budget was verified by simulation.",
            }
        )

        self.assertEqual(
            question["instructions"]["literature_search_query"],
            query,
        )
        self.assertNotIn(query, json.dumps(state))
        self.assertEqual(state["chunk"]["section"], "Results")

    def test_questions_use_domain_retrieval_prompt(self) -> None:
        import numpy as np

        class RecordingModel:
            def encode(self, questions, **options):
                self.questions = questions
                self.options = options
                return np.array([[3.0, 4.0]])

        model = RecordingModel()
        embeddings = embed_questions(model, ["Why are generic models called generic?"])

        self.assertEqual(model.options["prompt"], QUERY_PROMPT)
        self.assertNotIn("prompt_name", model.options)
        np.testing.assert_allclose(embeddings, [[0.6, 0.8]])

    def test_included_report_citations_use_authoritative_metadata(self) -> None:
        self.assertEqual(
            included_report_citations()["review-0012"],
            {
                "publication_type": "journal_article",
                "venue": "CEAS Space Journal",
            },
        )

    def test_report_codes_distinguish_review_and_candidate_reports(self) -> None:
        self.assertEqual(canonical_report_code("review-0012"), "review-report-0012")
        self.assertEqual(
            canonical_report_code("citation-0136"), "candidate-report-0136"
        )

    def test_report_filter_resolves_codes_and_unique_title_searches(self) -> None:
        reports = {
            "review-0012": {
                "report_id": "review-0012",
                "screening_record_id": "review-candidate-0012",
                "source_path": "reports/review-report-0012.md",
                "title": "Power Budget Verification",
            },
            "citation-0136": {
                "report_id": "citation-0136",
                "screening_record_id": "citation-candidate-0136",
                "source_path": "reports/citation-report-0136.md",
                "title": "Flight Software Case Study",
            },
        }

        self.assertEqual(
            resolve_report_filter("review-report-12", reports)["report_id"],
            "review-0012",
        )
        self.assertEqual(
            resolve_report_filter("candidate-report-136", reports)["report_id"],
            "citation-0136",
        )
        self.assertEqual(
            resolve_report_filter("budget verification", reports)["report_id"],
            "review-0012",
        )

    def test_report_filter_rejects_an_ambiguous_title_search(self) -> None:
        reports = {
            "review-0001": {
                "report_id": "review-0001",
                "title": "CubeSat power analysis",
            },
            "review-0002": {
                "report_id": "review-0002",
                "title": "CubeSat software analysis",
            },
        }

        with self.assertRaisesRegex(SearchError, "matches 2 reports"):
            resolve_report_filter("CubeSat analysis", reports)

    def test_results_include_bibliographic_citation(self) -> None:
        result = SearchService()._result(
            chunk={
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Fallback title",
                "section": "Introduction",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Evidence text.",
            },
            report={
                "authors": ["Doe, Jane", "Roe, John"],
                "title": "Citation title",
                "publication_year": 2025,
                "publication_type": "journal_article",
                "venue": "Journal of CubeSat Studies",
                "doi": "10.1000/example",
            },
            rank=1,
            score=1.0,
            dense_score=None,
            bm25_score=None,
            regex_score=None,
        )

        self.assertEqual(
            result["citation"],
            {
                "key": "review-0001",
                "authors": ["Doe, Jane", "Roe, John"],
                "title": "Citation title",
                "year": 2025,
                "publication_type": "journal_article",
                "venue": "Journal of CubeSat Studies",
                "doi": "10.1000/example",
            },
        )

    def test_results_preserve_equation_metadata(self) -> None:
        result = SearchService()._result(
            chunk={
                "chunk_id": "review-0001:equation-00001",
                "report_id": "review-0001",
                "title": "Example",
                "section": "Power",
                "page_start": 2,
                "page_end": 2,
                "chunk_type": "equation",
                "equation_id": "review-0001:equation-00001",
                "equation_label": "3",
                "equation_caption": "Equation (3) defines battery energy.",
                "equation_context_source": "caption",
                "equation_part": 1,
                "equation_parts": 1,
                "text": "Formula: E = P t",
            },
            report={},
            rank=1,
            score=1.0,
            dense_score=None,
            bm25_score=None,
            regex_score=None,
        )

        self.assertEqual(result["equation_label"], "3")
        self.assertEqual(result["equation_context_source"], "caption")

    def test_colpali_maxsim_scores_each_query_token(self) -> None:
        import numpy as np
        import torch

        query = torch.tensor([[[1.0, 0.0], [0.0, 1.0]]])
        documents = np.array(
            [
                [[1.0, 0.0], [0.0, 1.0]],
                [[1.0, 0.0], [1.0, 0.0]],
            ],
            dtype=np.float16,
        )

        scores = maxsim_scores(query, documents, device="cpu", batch_size=1)

        np.testing.assert_allclose(scores, [2.0, 1.0])

    def test_typesafe_key_can_come_from_local_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / "api-key.env"
            env_path.write_text("TYPESAFE_AI_API_KEY=local-test-key\n", encoding="utf-8")
            with (
                patch.dict(
                    os.environ,
                    {"TYPESAFE_API_KEY": "", "TYPESAFE_AI_API_KEY": ""},
                ),
                patch("search.TYPESAFE_ENV_PATH", env_path),
            ):
                self.assertEqual(typesafe_api_key(), "local-test-key")

    def test_jev_client_retries_transient_failures_without_a_total_budget(self) -> None:
        with (
            patch("search.typesafe_api_key", return_value="test-key"),
            patch("typesafe_sdk.TypeSafeClient") as client_class,
        ):
            client = SearchService()._get_jev_client()

        self.assertIs(client, client_class.return_value)
        options = client_class.call_args.kwargs
        self.assertEqual(options["timeout"], JEV_REQUEST_TIMEOUT_SECONDS)
        self.assertEqual(options["retry"].max_retries, JEV_MAX_RETRIES)
        self.assertIsNone(options["retry"].timeout)
        self.assertTrue(options["retry"].api_timeout_error)
        self.assertTrue(options["retry"].api_connection_error)
        self.assertIn(429, options["retry"].http_statuses)
        self.assertIn(529, options["retry"].http_statuses)

    def test_jev_search_caches_nouls_and_skips_metadata_on_future_queries(self) -> None:
        import numpy as np

        class FakeClient:
            def __init__(self):
                self.requests = []

            def system_one(self, *, state, questions, model):
                self.requests.append((state, questions, model))
                text = state["chunk"]["text"]
                answers = {}
                if JEV_CONTENT_QUESTION_ID in questions:
                    answers[JEV_CONTENT_QUESTION_ID] = SimpleNamespace(
                        noul=0.95 if "evidence" in text.casefold() else 0.05
                    )
                if JEV_SEARCH_QUESTION_ID in questions:
                    query = questions[JEV_SEARCH_QUESTION_ID]["instructions"][
                        "literature_search_query"
                    ]
                    answers[JEV_SEARCH_QUESTION_ID] = SimpleNamespace(
                        noul=0.9 if "power" in query.casefold() else 0.7
                    )
                return SimpleNamespace(nouls=answers)

        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "title": "Power budget",
                "section": "Results",
                "chunk_type": "passage",
                "text": "Substantive evidence about the power budget.",
            },
            {
                "chunk_id": "review-0001:chunk-00002",
                "title": "Power budget",
                "section": "Document",
                "chunk_type": "passage",
                "text": "Authors, venue, publication date, and license.",
            },
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index_path = root / "noul-index.sqlite3"
            chunks_path = root / "chunks.jsonl"
            chunks_path.write_text("{}\n{}\n", encoding="utf-8")
            corpus_sha256 = file_sha256(chunks_path)
            client = FakeClient()
            service = SearchService(jev_index_path=index_path)
            service._jev_client = client

            with patch("search.JEV_SEARCH_WORKERS", 1):
                first_scores, first_content, first_stats = service._jev_search_scores(
                    "How is the power budget verified?",
                    chunks,
                    corpus_sha256=corpus_sha256,
                )
                first_requests = list(client.requests)
                client.requests.clear()
                second_scores, second_content, second_stats = (
                    service._jev_search_scores(
                        "What thermal evidence is reported?",
                        chunks,
                        corpus_sha256=corpus_sha256,
                    )
                )
                second_requests = list(client.requests)

            replay = SearchService(jev_index_path=index_path)
            replay._get_jev_client = lambda: self.fail("Jev API was called on replay")
            replay_scores, replay_content, replay_stats = replay._jev_search_scores(
                "What thermal evidence is reported?",
                chunks,
                corpus_sha256=corpus_sha256,
            )
            with patch("search.DATA_DIR", root):
                filter_scores, filter_eligible, filter_stats = (
                    replay._jev_content_filter(chunks)
                )
            index_status = inspect_jev_index(
                chunks_path=chunks_path,
                index_path=index_path,
                model_id=JEV_MODEL_ID,
                content_question_sha256=JEV_CONTENT_QUESTION_SHA256,
                content_threshold=JEV_CONTENT_THRESHOLD,
            )

        np.testing.assert_allclose(first_scores, [0.9, 0.9])
        np.testing.assert_allclose(first_content, [0.95, 0.05])
        self.assertEqual(first_stats["api_calls"], 2)
        self.assertEqual(len(first_requests), 2)
        for _, questions, model in first_requests:
            self.assertEqual(model, JEV_MODEL_ID)
            self.assertEqual(
                set(questions),
                {JEV_CONTENT_QUESTION_ID, JEV_SEARCH_QUESTION_ID},
            )

        np.testing.assert_allclose(second_scores, [0.7, -1.0])
        np.testing.assert_allclose(second_content, [0.95, 0.05])
        self.assertEqual(second_stats["api_calls"], 1)
        self.assertEqual(len(second_requests), 1)
        self.assertEqual(set(second_requests[0][1]), {JEV_SEARCH_QUESTION_ID})
        self.assertEqual(second_requests[0][2], JEV_MODEL_ID)
        self.assertIn("evidence", second_requests[0][0]["chunk"]["text"].casefold())

        np.testing.assert_allclose(replay_scores, second_scores)
        np.testing.assert_allclose(replay_content, second_content)
        self.assertEqual(replay_stats["api_calls"], 0)
        self.assertEqual(replay_stats["query_cache_hits"], 1)
        np.testing.assert_allclose(filter_scores, first_content)
        self.assertEqual(filter_eligible.tolist(), [True, False])
        self.assertEqual(filter_stats["threshold"], JEV_CONTENT_THRESHOLD)
        self.assertEqual(filter_stats["excluded_chunks"], 1)
        self.assertEqual(index_status["state"], "ready")
        self.assertEqual(index_status["meaningful_chunks"], 1)
        self.assertEqual(index_status["excluded_chunks"], 1)
        self.assertEqual(index_status["cached_queries"], 2)
        self.assertEqual(index_status["cached_scores"], 3)

    def test_jev_mode_is_normalized_case_insensitively(self) -> None:
        self.assertEqual(normalize_mode("JEV"), "jev")

    def test_qwen_vector_omits_chunks_below_the_jev_content_threshold(self) -> None:
        import numpy as np

        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Substantive evidence",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "A substantive engineering result.",
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "title": "Publication metadata",
                "section": "Document",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Authors and publication venue.",
            },
        ]
        filter_stats = {
            "threshold": JEV_CONTENT_THRESHOLD,
            "excluded_chunks": 1,
        }
        service = SearchService()
        service._load_corpus = lambda: (
            chunks,
            {"review-0001": {}, "review-0002": {}},
        )
        service._jev_content_filter = lambda _chunks: (
            np.array([0.8, 0.2], dtype=np.float32),
            np.array([True, False]),
            filter_stats,
        )
        service._dense_scores = lambda _question: (
            np.array([0.5, 0.99], dtype=np.float32),
            "cpu",
        )

        payload = service._search(
            question="engineering evidence",
            mode="vector",
            top_k=5,
            max_per_report=2,
            fusion_depth=10,
            include_visual=False,
            rerank=False,
            rerank_depth=5,
            report_id=None,
        )

        self.assertEqual(JEV_CONTENT_THRESHOLD, 0.3)
        self.assertEqual(payload["content_filter"], filter_stats)
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["title"], "Substantive evidence")
        self.assertAlmostEqual(
            payload["results"][0]["meaningful_content_noul"], 0.8, places=6
        )

    def test_jev_mode_ranks_only_meaningful_chunks(self) -> None:
        import numpy as np

        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Evidence",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Meaningful evidence.",
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "title": "Metadata",
                "section": "References",
                "page_start": 2,
                "page_end": 2,
                "chunk_type": "passage",
                "text": "Reference metadata.",
            },
        ]
        service = SearchService()
        service._load_corpus = lambda: (
            chunks,
            {"review-0001": {}, "review-0002": {}},
        )
        service._jev_search_scores = lambda _question, _chunks: (
            np.array([0.75, 0.99], dtype=np.float32),
            np.array([0.9, 0.1], dtype=np.float32),
            {"api_calls": 2, "query_cache_hits": 0},
        )

        payload = service._search(
            question="What evidence is reported?",
            mode="jev",
            top_k=5,
            max_per_report=2,
            fusion_depth=10,
            include_visual=False,
            rerank=False,
            rerank_depth=5,
            report_id=None,
        )

        self.assertEqual(payload["score_type"], "noul")
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["title"], "Evidence")
        self.assertAlmostEqual(payload["results"][0]["jev_score"], 0.75)
        self.assertAlmostEqual(
            payload["results"][0]["meaningful_content_noul"], 0.9, places=6
        )

    def test_jev_reranker_uses_noul_probabilities_as_scores(self) -> None:
        import numpy as np

        class FakeClient:
            def __init__(self):
                self.requests = []

            def system_one(self, *, state, questions):
                self.requests.append((state, questions))
                noul = 0.9 if "direct evidence" in state["candidate_document"] else 0.1
                answer = SimpleNamespace(noul=noul)
                return SimpleNamespace(nouls={JEV_RERANKER_QUESTION_ID: answer})

        service = SearchService()
        client = FakeClient()
        service._jev_client = client

        scores = service._jev_rerank_scores(
            "How is the power budget verified?",
            ["This gives direct evidence.", "This is an incidental mention."],
        )

        np.testing.assert_allclose(scores, [0.9, 0.1])
        self.assertCountEqual(
            [request[0]["candidate_document"] for request in client.requests],
            ["This gives direct evidence.", "This is an incidental mention."],
        )
        for state, questions in client.requests:
            self.assertEqual(state["query"], "How is the power budget verified?")
            self.assertEqual(
                questions, {JEV_RERANKER_QUESTION_ID: JEV_RERANKER_QUESTION}
            )

    def test_reranker_names_are_case_insensitive_and_validated(self) -> None:
        self.assertEqual(normalize_reranker("JEV"), "jev")
        with self.assertRaisesRegex(SearchError, "Unknown reranker"):
            normalize_reranker("other")

    def test_review_filters_are_case_insensitive_and_validated(self) -> None:
        self.assertEqual(normalize_review_filter("ONLY"), "only")
        self.assertTrue(review_filter_allows({"publication_type": "review"}, "include"))
        self.assertFalse(
            review_filter_allows({"publication_type": "review"}, "exclude")
        )
        self.assertTrue(review_filter_allows({"publication_type": "review"}, "only"))
        self.assertFalse(
            review_filter_allows({"publication_type": "journal_article"}, "only")
        )
        with self.assertRaisesRegex(SearchError, "Unknown review filter"):
            normalize_review_filter("other")

    def test_bm25_can_exclude_reviews_or_search_reviews_only(self) -> None:
        import numpy as np

        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Secondary study",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "MBSE evidence in a review.",
                "embedding_text": "MBSE evidence in a review.",
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "title": "Primary study",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "MBSE evidence in an article.",
                "embedding_text": "MBSE evidence in an article.",
            },
        ]
        reports = {
            "review-0001": {"publication_type": "review"},
            "review-0002": {"publication_type": "journal_article"},
        }
        service = SearchService()
        service._load_corpus = lambda: (chunks, reports)
        service._get_bm25_data = lambda: ()

        with patch(
            "search.bm25_scores",
            return_value=np.array([2.0, 1.0], dtype=np.float32),
        ):
            reviews_only = service._search(
                question="MBSE",
                mode="bm25",
                top_k=2,
                max_per_report=2,
                fusion_depth=10,
                include_visual=False,
                rerank=False,
                rerank_depth=5,
                report_id=None,
                review_filter="only",
            )
            reviews_excluded = service._search(
                question="MBSE",
                mode="bm25",
                top_k=2,
                max_per_report=2,
                fusion_depth=10,
                include_visual=False,
                rerank=False,
                rerank_depth=5,
                report_id=None,
                review_filter="exclude",
            )

        self.assertEqual(
            [result["report_id"] for result in reviews_only["results"]],
            ["review-0001"],
        )
        self.assertEqual(
            [result["report_id"] for result in reviews_excluded["results"]],
            ["review-0002"],
        )

    def test_reranker_rank_has_greater_fusion_weight(self) -> None:
        reranker_favorite = reranked_rank_fusion_score(
            first_stage_rank=21,
            reranker_rank=1,
        )
        retrieval_favorite = reranked_rank_fusion_score(
            first_stage_rank=3,
            reranker_rank=7,
        )

        self.assertGreater(reranker_favorite, retrieval_favorite)

    def test_quoted_phrase_adds_exact_sequence_bonus(self) -> None:
        chunks = [
            {"embedding_text": "The model can distribute power safely."},
            {
                "embedding_text": "The model can distribute loads when power is available."
            },
        ]
        prepared = prepare_bm25(chunks)
        plain = bm25_scores("distribute power", *prepared)
        quoted = bm25_scores('"distribute power"', *prepared)

        self.assertGreater(quoted[0], plain[0])
        self.assertEqual(quoted[1], plain[1])

    def test_regex_scores_original_text_case_insensitively(self) -> None:
        chunks = [
            {"text": "State machine and STATE machine."},
            {"text": "Block definition diagram."},
        ]

        scores = regex_scores(r"state\s+machine", chunks)

        self.assertEqual(scores.tolist(), [2.0, 0.0])

    def test_exact_match_spans_match_whole_query_terms(self) -> None:
        text = "Power, powered, and POWER subsystems."

        spans = exact_match_spans(text, "power subsystem", "hybrid")

        self.assertEqual([text[start:end] for start, end in spans], ["Power", "POWER"])

    def test_exact_match_spans_use_the_regex_expression(self) -> None:
        text = "State machine and state-machine."

        spans = exact_match_spans(text, r"state[\s-]+machine", "regex")

        self.assertEqual(
            [text[start:end] for start, end in spans],
            ["State machine", "state-machine"],
        )

    def test_exact_match_spans_skip_zero_width_regex_matches(self) -> None:
        self.assertEqual(exact_match_spans("CubeSat", r"^", "regex"), [])

    def test_search_adds_exact_matches_only_to_text_results(self) -> None:
        service = SearchService()
        service._search = lambda **_options: {
            "question": "power",
            "mode": "bm25",
            "results": [
                {"display_type": "text", "text": "Power subsystem."},
                {"display_type": "image", "text": "Power diagram."},
            ],
        }

        payload = service.search("power", mode="bm25")

        self.assertEqual(payload["results"][0]["exact_match_spans"], [[0, 5]])
        self.assertNotIn("exact_match_spans", payload["results"][1])

    def test_search_resolves_report_filter_and_removes_report_result_cap(self) -> None:
        service = SearchService()
        reports = {
            "citation-0136": {
                "report_id": "citation-0136",
                "source_path": "reports/citation-report-0136.md",
                "title": "Flight Software Case Study",
                "publication_year": 2025,
            }
        }
        captured = {}
        service._load_corpus = lambda: ([], reports)

        def fake_search(**options):
            captured.update(options)
            return {"question": "software", "mode": "bm25", "results": []}

        service._search = fake_search

        payload = service.search(
            "software",
            mode="bm25",
            max_per_report=2,
            report="candidate-report-136",
        )

        self.assertEqual(captured["report_id"], "citation-0136")
        self.assertIsNone(captured["max_per_report"])
        self.assertEqual(payload["report_filter"]["code"], "candidate-report-0136")

    def test_chunk_ranking_filters_before_applying_depth(self) -> None:
        import numpy as np

        service = SearchService()
        candidates = {}
        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "image_refs": [],
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "image_refs": [],
            },
        ]

        service._add_chunk_ranking(
            candidates,
            "dense",
            np.array([10.0, 1.0]),
            chunks,
            {},
            depth=1,
            report_id="review-0002",
        )

        self.assertEqual(list(candidates), ["chunk:review-0002:chunk-00001"])

    def test_all_text_modes_forward_the_rerank_setting(self) -> None:
        for mode in ("hybrid", "vector", "jev", "bm25", "regex"):
            with self.subTest(mode=mode):
                service = SearchService()
                service._load_corpus = lambda: ([], {})
                captured = {}

                def fake_search(**options):
                    captured.update(options)
                    return {"question": "evidence", "mode": mode, "results": []}

                service._search = fake_search
                service.search("evidence", mode=mode, rerank=True)

                self.assertTrue(captured["rerank"])

    def test_jev_bm25_and_regex_can_use_the_qwen_reranker(self) -> None:
        import numpy as np

        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "First-stage favorite",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "First candidate.",
                "embedding_text": "First candidate.",
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "title": "Reranker favorite",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Second candidate with direct evidence.",
                "embedding_text": "Second candidate with direct evidence.",
            },
        ]
        first_stage_scores = np.array([2.0, 1.0], dtype=np.float32)

        for mode in ("jev", "bm25", "regex"):
            with self.subTest(mode=mode):
                service = SearchService()
                service._load_corpus = lambda: (
                    chunks,
                    {"review-0001": {}, "review-0002": {}},
                )
                service._get_bm25_data = lambda: ()
                service._jev_search_scores = lambda _question, _chunks: (
                    first_stage_scores,
                    np.array([0.9, 0.9], dtype=np.float32),
                    {"api_calls": 0, "query_cache_hits": 2},
                )
                service._rerank_scores = lambda _question, _documents: np.array(
                    [0.1, 0.9], dtype=np.float32
                )

                with (
                    patch("search.bm25_scores", return_value=first_stage_scores),
                    patch("search.regex_scores", return_value=first_stage_scores),
                ):
                    payload = service._search(
                        question="direct evidence",
                        mode=mode,
                        top_k=2,
                        max_per_report=2,
                        fusion_depth=10,
                        include_visual=False,
                        rerank=True,
                        rerank_depth=2,
                        reranker="qwen",
                        report_id=None,
                    )

                self.assertTrue(payload["reranked"])
                self.assertEqual(payload["reranker"], "qwen")
                self.assertEqual(payload["results"][0]["title"], "Reranker favorite")
                self.assertAlmostEqual(
                    payload["results"][0]["reranker_score"], 0.9, places=6
                )

    def test_vector_search_can_rerank_with_jev(self) -> None:
        import numpy as np

        service = SearchService()
        service._load_corpus = lambda: ([], {})
        service._dense_scores = lambda _question: (np.array([]), "cpu")
        service._jev_content_filter = lambda _chunks: (
            np.array([]),
            np.array([], dtype=bool),
            {"threshold": JEV_CONTENT_THRESHOLD},
        )
        captured = {}

        def candidate_results(**options):
            captured.update(options)
            return [], None, False, []

        service._hybrid_results = candidate_results

        payload = service._search(
            question="CubeSat",
            mode="vector",
            top_k=5,
            max_per_report=2,
            fusion_depth=10,
            include_visual=True,
            rerank=True,
            rerank_depth=5,
            reranker="jev",
            images_only=True,
            report_id=None,
        )

        self.assertIsNone(captured["lexical_scores"])
        self.assertFalse(captured["include_visual"])
        self.assertEqual(captured["reranker"], "jev")
        self.assertTrue(captured["images_only"])
        self.assertTrue(payload["reranked"])
        self.assertEqual(payload["reranker"], "jev")

    def test_images_only_filters_fused_candidates(self) -> None:
        import numpy as np

        service = SearchService()
        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Image evidence",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "caption",
                "text": "Diagram evidence.",
                "embedding_text": "Diagram evidence.",
                "has_image": True,
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "title": "Text evidence",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Text evidence.",
                "embedding_text": "Text evidence.",
                "has_image": False,
            },
        ]

        def fake_image(chunk, _report=None):
            return Path(__file__).resolve() if chunk["has_image"] else None

        with patch("search.originating_image", side_effect=fake_image):
            results, _, _, _ = service._hybrid_results(
                question="evidence",
                chunks=chunks,
                reports={"review-0001": {}, "review-0002": {}},
                dense_scores=np.array([1.0, 2.0]),
                lexical_scores=None,
                top_k=2,
                max_per_report=2,
                report_id=None,
                fusion_depth=10,
                include_visual=False,
                rerank=False,
                rerank_depth=10,
                images_only=True,
            )

        self.assertEqual(
            [result["chunk_id"] for result in results],
            ["review-0001:chunk-00001"],
        )
        self.assertEqual(results[0]["display_type"], "image")

    def test_hybrid_text_rankings_apply_the_jev_content_filter(self) -> None:
        import numpy as np

        service = SearchService()
        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Evidence",
                "section": "Results",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Evidence.",
                "embedding_text": "Evidence.",
            },
            {
                "chunk_id": "review-0002:chunk-00001",
                "report_id": "review-0002",
                "title": "Metadata",
                "section": "Document",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "Metadata.",
                "embedding_text": "Metadata.",
            },
        ]

        results, _, _, _ = service._hybrid_results(
            question="evidence",
            chunks=chunks,
            reports={"review-0001": {}, "review-0002": {}},
            dense_scores=np.array([1.0, 2.0]),
            lexical_scores=np.array([1.0, 2.0]),
            top_k=2,
            max_per_report=2,
            report_id=None,
            fusion_depth=10,
            include_visual=False,
            rerank=False,
            rerank_depth=10,
            content_eligible=np.array([True, False]),
        )

        self.assertEqual(
            [result["chunk_id"] for result in results],
            ["review-0001:chunk-00001"],
        )

    def test_hybrid_search_can_rerank_with_jev(self) -> None:
        import numpy as np

        service = SearchService()
        captured = {}

        def jev_scores(question, documents):
            captured["question"] = question
            captured["documents"] = documents
            return np.array([0.87])

        service._jev_rerank_scores = jev_scores
        service._rerank_scores = lambda *_args: self.fail("Qwen reranker was used")
        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Example",
                "section": "Introduction",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "CubeSat evidence.",
                "embedding_text": "CubeSat evidence.",
            }
        ]

        results, _, _, _ = service._hybrid_results(
            question="CubeSat",
            chunks=chunks,
            reports={"review-0001": {}},
            dense_scores=np.array([1.0]),
            lexical_scores=np.array([0.0]),
            top_k=1,
            max_per_report=2,
            report_id=None,
            fusion_depth=10,
            include_visual=False,
            rerank=True,
            rerank_depth=10,
            reranker="jev",
        )

        self.assertEqual(captured["question"], "CubeSat")
        self.assertEqual(captured["documents"], ["CubeSat evidence."])
        self.assertAlmostEqual(results[0]["reranker_score"], 0.87, places=6)

    def test_hybrid_search_skips_an_unavailable_visual_index(self) -> None:
        import numpy as np

        service = SearchService()

        def unavailable_visual_scores(_question: str):
            raise SearchError("The ColPali image index is missing.")

        service._visual_scores = unavailable_visual_scores
        chunks = [
            {
                "chunk_id": "review-0001:chunk-00001",
                "report_id": "review-0001",
                "title": "Example",
                "section": "Introduction",
                "page_start": 1,
                "page_end": 1,
                "chunk_type": "passage",
                "text": "CubeSat evidence.",
                "embedding_text": "CubeSat evidence.",
            }
        ]

        results, visual_device, visual_search, warnings = service._hybrid_results(
            question="CubeSat",
            chunks=chunks,
            reports={"review-0001": {}},
            dense_scores=np.array([1.0]),
            lexical_scores=np.array([1.0]),
            top_k=1,
            max_per_report=2,
            report_id=None,
            fusion_depth=10,
            include_visual=True,
            rerank=False,
            rerank_depth=10,
        )

        self.assertEqual(len(results), 1)
        self.assertIsNone(visual_device)
        self.assertFalse(visual_search)
        self.assertEqual(
            warnings,
            ["Visual search unavailable: The ColPali image index is missing."],
        )


if __name__ == "__main__":
    unittest.main()
