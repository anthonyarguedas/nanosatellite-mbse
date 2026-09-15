#!/usr/bin/env python3
"""Offline checks for the Pilot 005 Engineering Village queries."""

from __future__ import annotations

import hashlib
import unittest

import queries


class QueryTests(unittest.TestCase):
    def test_literal_snapshot(self) -> None:
        self.assertEqual(queries.TERM_COUNTS, queries.EXPECTED_TERM_COUNTS)
        self.assertEqual(queries.TERM_SNAPSHOT_SHA256, queries.EXPECTED_TERM_SNAPSHOT_SHA256)
        self.assertNotIn("*", queries.A1_LITERAL)
        self.assertNotIn("?", queries.A1_LITERAL)
        self.assertNotIn("NEAR", queries.A1_LITERAL.upper())

    def test_candidate_is_bounded(self) -> None:
        self.assertEqual(queries.A1_WILDCARD.count("*"), 3)
        self.assertNotIn("?", queries.A1_WILDCARD)
        self.assertNotIn("NEAR", queries.A1_WILDCARD.upper())
        self.assertEqual(queries.REPLACED_LITERAL_COUNT, 8)
        self.assertEqual(queries.CHARACTER_REDUCTION, 130)
        self.assertEqual(len(queries.A1_LITERAL), 3856)
        self.assertEqual(len(queries.A1_WILDCARD), 3726)

    def test_only_declared_atoms_change(self) -> None:
        reconstructed = queries.A1_LITERAL
        for item in queries.WILDCARD_REPLACEMENTS:
            literal = " OR ".join(
                queries.literal_atom(value) for value in item["replaced_literals"]
            )
            wildcard = queries.wildcard_atom(item["candidate"])
            self.assertEqual(reconstructed.count(literal), 1)
            reconstructed = reconstructed.replace(literal, wildcard)
        self.assertEqual(reconstructed, queries.A1_WILDCARD)

    def test_event_hashes_are_distinct(self) -> None:
        hashes = {
            hashlib.sha256(value.encode("utf-8")).hexdigest()
            for value in queries.EVENT_QUERIES.values()
        }
        self.assertEqual(len(hashes), 2)


if __name__ == "__main__":
    unittest.main()
