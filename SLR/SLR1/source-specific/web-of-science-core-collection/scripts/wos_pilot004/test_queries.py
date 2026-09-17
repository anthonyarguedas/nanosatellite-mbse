#!/usr/bin/env python3
"""Offline checks for the Web of Science Pilot 004 query translation."""

from __future__ import annotations

import unittest

import queries


class WosPilot004QueryTests(unittest.TestCase):
    def test_schedule_uses_current_compound_definitions_without_proximity(self):
        self.assertEqual(tuple(queries.LITERAL_SCHEDULE), queries.SCHEDULE_IDS)
        for query in queries.LITERAL_SCHEDULE.values():
            self.assertNotIn("NEAR", query.upper())
            self.assertNotIn(" SAME ", query.upper())
            self.assertNotIn("*", query)
            self.assertIn("PY=(2011-2026)", query)
            self.assertIn("LA=(English)", query)
        self.assertIn(queries.ORDINARY_BLOCKS["G_mission"], queries.LITERAL_SCHEDULE["BG1"])
        self.assertIn(queries.ORDINARY_BLOCKS["M_B"], queries.LITERAL_SCHEDULE["BG1"])
        self.assertIn(queries.ORDINARY_BLOCKS["G_product"], queries.LITERAL_SCHEDULE["BG2"])
        self.assertIn(queries.ORDINARY_BLOCKS["G_DSL"], queries.LITERAL_SCHEDULE["BC1"])
        self.assertIn(queries.ORDINARY_BLOCKS["T_precise"], queries.LITERAL_SCHEDULE["BT2"])

    def test_wildcard_candidate_covers_only_the_predeclared_population_literals(self):
        replaced = {
            value
            for item in queries.WILDCARD_REPLACEMENTS
            for value in item["replaced_literals"]
        }
        self.assertEqual(len(queries.WILDCARD_REPLACEMENTS), 10)
        self.assertEqual(len(replaced), 22)
        self.assertEqual(len(queries.wildcard_population_atoms()), 14)
        for partition_id in queries.SCHEDULE_IDS:
            literal = queries.LITERAL_SCHEDULE[partition_id]
            wildcard = queries.WILDCARD_SCHEDULE[partition_id]
            self.assertEqual(wildcard.count("*"), 10)
            self.assertEqual(len(literal) - len(wildcard), 255)
            self.assertEqual(
                literal.replace(queries.P_LITERAL, "<P>", 1),
                wildcard.replace(queries.P_WILDCARD, "<P>", 1),
            )


if __name__ == "__main__":
    unittest.main()
