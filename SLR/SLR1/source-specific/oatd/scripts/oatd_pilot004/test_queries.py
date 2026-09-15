#!/usr/bin/env python3
"""Offline tests for the OATD Pilot 004 translation."""

from __future__ import annotations

import unittest

import queries


class OATDPilot004QueryTests(unittest.TestCase):
    def test_source_receives_only_the_exact_population_block(self) -> None:
        self.assertEqual(queries.P_QUERY, queries.EXPECTED_P_QUERY)
        self.assertEqual(queries.P_QUERY.count('"') // 2, 26)
        self.assertNotIn(" AND ", queries.P_QUERY)

    def test_local_schedule_preserves_current_boolean_forms(self) -> None:
        self.assertEqual(tuple(queries.LOCAL_SCHEDULE), queries.SCHEDULE_IDS)
        expected_parts = {
            "A1": ("P", "E_H", "M_H"),
            "A2": ("P", "E_F", "M"),
            "A3": ("P", "E_H", "M_B"),
            "B1": ("P", "M_H"),
            "B2": ("P", "M_B", "R"),
            "BG1": ("P", "G_model"),
            "BG2": ("P", "G_structure"),
            "BC1": ("P", "C1"),
            "BT2": ("P", "M_B", "T_precise"),
        }
        blocks = {**queries.ORDINARY_BLOCKS, **queries.COMPOUND_BLOCKS}
        for schedule_id, names in expected_parts.items():
            with self.subTest(schedule_id=schedule_id):
                expression = queries.LOCAL_SCHEDULE[schedule_id]
                for name in names:
                    self.assertIn(blocks[name], expression)

    def test_no_proximity_wildcard_or_pair_expansion_remains(self) -> None:
        for schedule_id, expression in queries.LOCAL_SCHEDULE.items():
            with self.subTest(schedule_id=schedule_id):
                self.assertNotIn("NEAR", expression.upper())
                self.assertNotIn("~", expression)
                self.assertNotIn("*", expression)
                self.assertNotIn("?", expression)
                for field in (
                    "title:",
                    "author:",
                    "abstract:",
                    "publisher:",
                    "subject:",
                    "discipline:",
                ):
                    self.assertNotIn(field, expression)

    def test_term_snapshot_counts_match_the_protocol_snapshot(self) -> None:
        self.assertEqual(queries.TERM_COUNTS, queries._terms.EXPECTED_COUNTS)
        self.assertEqual(queries.PROTOCOL_COMMIT, queries._terms.PROTOCOL_COMMIT)


if __name__ == "__main__":
    unittest.main()
