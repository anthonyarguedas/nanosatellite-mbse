from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_index import chunk_embedding_key, jsonl_prefix_sha256


class BuildIndexTests(unittest.TestCase):
    def test_chunk_embedding_key_tracks_embedding_text(self) -> None:
        first = chunk_embedding_key(
            {"chunk_id": "chunk-1", "embedding_text": "first text"}
        )
        same = chunk_embedding_key(
            {"chunk_id": "chunk-1", "embedding_text": "first text"}
        )
        changed = chunk_embedding_key(
            {"chunk_id": "chunk-1", "embedding_text": "changed text"}
        )

        self.assertEqual(first, same)
        self.assertNotEqual(first, changed)

    def test_jsonl_prefix_hash_matches_standalone_prefix(self) -> None:
        lines = [b'{"id": 1}\n', b'{"id": 2}\n', b'{"id": 3}\n']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.jsonl"
            path.write_bytes(b"".join(lines))
            actual = jsonl_prefix_sha256(path, 2)

        self.assertEqual(actual, hashlib.sha256(b"".join(lines[:2])).hexdigest())

    def test_jsonl_prefix_hash_rejects_missing_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rows.jsonl"
            path.write_text('{"id": 1}\n', encoding="utf-8")
            self.assertIsNone(jsonl_prefix_sha256(path, 2))


if __name__ == "__main__":
    unittest.main()
