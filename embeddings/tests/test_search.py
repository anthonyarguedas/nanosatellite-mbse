from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import (
    QUERY_PROMPT,
    bm25_scores,
    embed_questions,
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


if __name__ == "__main__":
    unittest.main()
