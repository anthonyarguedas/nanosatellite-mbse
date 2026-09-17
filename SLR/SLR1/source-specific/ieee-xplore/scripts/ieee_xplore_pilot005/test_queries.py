#!/usr/bin/env python3
"""Offline checks for the IEEE Xplore Pilot 005 translation."""

from __future__ import annotations

import hashlib
import unittest

import queries


class QueryTests(unittest.TestCase):
    def test_term_counts(self) -> None:
        self.assertEqual(queries.TERM_COUNTS, queries.EXPECTED_COUNTS)

    def test_schedule_order(self) -> None:
        self.assertEqual(tuple(queries.SCHEDULE), queries.SCHEDULE_IDS)

    def test_source_atom(self) -> None:
        self.assertEqual(
            queries.atom("mission-independent model"),
            '("All Metadata":"mission-independent model")',
        )

    def test_forbidden_syntax_is_absent(self) -> None:
        for schedule_id, query in queries.SCHEDULE.items():
            with self.subTest(schedule_id=schedule_id):
                self.assertNotIn("NEAR", query.upper())
                self.assertNotIn("*", query)
                self.assertNotIn("?", query)
                self.assertNotIn("T2", query)

    def test_unchanged_core_hashes(self) -> None:
        expected = {
            "A1": "6060cde34f89f3bce66d2f718e0ede1bef61c25e45f0ba2b9d1a603a070db3e0",
            "A2": "c089612db91c2dcecacc21f5c6d2aafad7ca54b13725c1e3eecc4baa6cd7f934",
            "A3": "5d9647a3724a3c1d334350a27896d426e66df8e9ddf39de10e417cc20fce1d8e",
            "B1": "a98909791e3b1e3e1bd638fe9c853a42ca3aa10f790e6fa15e0cc419acb21473",
            "B2": "bf98ed2edd5eb39e04ccc602091c8aab8b773fda5dea3e5111551cb658789dfd",
        }
        observed = {
            schedule_id: hashlib.sha256(queries.SCHEDULE[schedule_id].encode()).hexdigest()
            for schedule_id in expected
        }
        self.assertEqual(observed, expected)

    def test_compound_membership(self) -> None:
        bg1 = queries.SCHEDULE["BG1"]
        bg2 = queries.SCHEDULE["BG2"]
        bc1 = queries.SCHEDULE["BC1"]
        bt2 = queries.SCHEDULE["BT2"]
        for term in (
            "generic model",
            "mission-independent architecture",
            "mission-independent",
            "digital twin",
        ):
            self.assertIn(queries.atom(term), bg1)
        for term in (
            "reference architecture",
            "product-family model",
            "variation points",
            "product family",
            "system model",
        ):
            self.assertIn(queries.atom(term), bg2)
        for term in ("SysML profiles", "domain specific modelling language"):
            self.assertIn(queries.atom(term), bc1)
        for term in ("system model", "tailoring", "instantiation", "variability"):
            self.assertIn(queries.atom(term), bt2)


if __name__ == "__main__":
    unittest.main()
