from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import (
    QUERY_PROMPT,
    SearchError,
    SearchService,
    bm25_scores,
    embed_questions,
    exact_match_spans,
    included_report_citations,
    maxsim_scores,
    prepare_bm25,
    regex_scores,
)


class SearchTests(unittest.TestCase):
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
