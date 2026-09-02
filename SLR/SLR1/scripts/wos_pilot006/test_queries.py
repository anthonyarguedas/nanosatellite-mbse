#!/usr/bin/env python3
"""Offline checks for Web of Science Pilot 006 PSR queries."""

from __future__ import annotations

import unittest

import queries


class WosPsrWildcardQueryTests(unittest.TestCase):
    def test_literal_schedule_matches_the_current_psr_boolean_forms(self):
        self.assertEqual(tuple(queries.LITERAL_SCHEDULE), queries.PSR_IDS)
        self.assertEqual(queries.TERM_COUNTS["X"], 39)
        self.assertEqual(queries.TERM_COUNTS["Q"], 16)
        for query in queries.LITERAL_SCHEDULE.values():
            self.assertNotIn("NEAR", query.upper())
            self.assertNotIn("*", query)
            self.assertIn("PY=(1900-2026)", query)
            self.assertNotIn("LA=(", query)
            self.assertNotIn("DT=(", query)
        self.assertIn(queries.B["M_H"], queries.LITERAL_SCHEDULE["PSR1"])
        self.assertIn(queries.B["R"], queries.LITERAL_SCHEDULE["PSR2"])
        self.assertIn(queries.E_BLOCK, queries.LITERAL_SCHEDULE["PSR3"])
        self.assertIn(queries.ARTIFACT_BLOCK, queries.LITERAL_SCHEDULE["PSR4"])

    def test_candidate_changes_only_the_ten_population_families(self):
        self.assertEqual(len(queries.WILDCARD_REPLACEMENTS), 10)
        for partition_id in queries.PSR_IDS:
            literal = queries.LITERAL_SCHEDULE[partition_id]
            wildcard = queries.WILDCARD_SCHEDULE[partition_id]
            self.assertEqual(wildcard.count("*"), 10)
            self.assertEqual(len(literal) - len(wildcard), 255)
            literal_population = (
                queries.P_LITERAL_BLOCK
                if partition_id == "PSR3"
                else queries.X_LITERAL_BLOCK
            )
            wildcard_population = (
                queries.P_WILDCARD_BLOCK
                if partition_id == "PSR3"
                else queries.X_WILDCARD_BLOCK
            )
            self.assertEqual(
                literal.replace(literal_population, "<POPULATION>", 1),
                wildcard.replace(wildcard_population, "<POPULATION>", 1),
            )


if __name__ == "__main__":
    unittest.main()
