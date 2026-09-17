from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from search import bm25_scores, prepare_bm25


class SearchTests(unittest.TestCase):
    def test_quoted_phrase_adds_exact_sequence_bonus(self) -> None:
        chunks = [
            {"embedding_text": "The model can distribute power safely."},
            {"embedding_text": "The model can distribute loads when power is available."},
        ]
        prepared = prepare_bm25(chunks)
        plain = bm25_scores("distribute power", *prepared)
        quoted = bm25_scores('"distribute power"', *prepared)

        self.assertGreater(quoted[0], plain[0])
        self.assertEqual(quoted[1], plain[1])


if __name__ == "__main__":
    unittest.main()
