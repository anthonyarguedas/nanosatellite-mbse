from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_visual_index import load_cached_embedding, save_cached_embedding


class BuildVisualIndexTests(unittest.TestCase):
    def test_cached_embedding_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "image.f16.npy"
            expected = np.array([[0.25, 0.5], [0.75, 1.0]], dtype=np.float32)

            save_cached_embedding(path, expected)
            actual = load_cached_embedding(path)

            self.assertEqual(actual.dtype, np.float16)
            np.testing.assert_allclose(actual, expected)

    def test_invalid_cached_embedding_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "image.f16.npy"
            path.write_text("invalid", encoding="utf-8")

            self.assertIsNone(load_cached_embedding(path))
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
