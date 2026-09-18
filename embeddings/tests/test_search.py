from __future__ import annotations

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
    JEV_RERANKER_QUESTION,
    JEV_RERANKER_QUESTION_ID,
    QUERY_PROMPT,
    SearchError,
    SearchService,
    bm25_scores,
    canonical_report_code,
    embed_questions,
    exact_match_spans,
    included_report_citations,
    maxsim_scores,
    normalize_reranker,
    prepare_bm25,
    regex_scores,
    reranked_rank_fusion_score,
    resolve_report_filter,
    typesafe_api_key,
)


class SearchTests(unittest.TestCase):
    def test_gui_defaults_to_vector_with_filter_and_reranker_controls(self) -> None:
        html = GUI_PATH.read_text(encoding="utf-8")

        self.assertIn('name="mode" value="vector" checked', html)
        self.assertNotIn('name="mode" value="visual"', html)
        self.assertIn('id="images-only" type="checkbox"', html)
        self.assertIn('name="reranker" value="off"', html)
        self.assertIn('name="reranker" value="qwen" checked', html)
        self.assertIn('name="reranker" value="jev"', html)

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

    def test_vector_search_can_rerank_with_jev(self) -> None:
        import numpy as np

        service = SearchService()
        service._load_corpus = lambda: ([], {})
        service._dense_scores = lambda _question: (np.array([]), "cpu")
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
