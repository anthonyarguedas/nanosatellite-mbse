#!/usr/bin/env python3
"""Focused offline tests for the Compendex Pilot 007 query renderer."""

from __future__ import annotations

import unittest

import queries


class QueryTests(unittest.TestCase):
    def test_reviewed_snapshot_and_schedule(self) -> None:
        self.assertEqual(
            queries.TERM_SNAPSHOT_SHA256, queries.EXPECTED_TERM_SNAPSHOT_SHA256
        )
        self.assertEqual(tuple(queries.EVENT_QUERIES), queries.SCHEDULE_IDS)
        self.assertEqual(set(queries.RUN_ORDER), set(queries.SCHEDULE_IDS))
        self.assertEqual(
            queries.RUN_ORDER,
            ("B2", "BG1", "BG2", "BC1", "BT2", "A1", "A2", "A3", "B1"),
        )
        self.assertEqual(queries.TERM_COUNTS, queries.EXPECTED_TERM_COUNTS)

    def test_approved_population_translation(self) -> None:
        population = queries.BLOCKS["P"]
        self.assertIn("(CubeSat* WN ALL)", population)
        self.assertIn("(nanosat* WN ALL)", population)
        self.assertIn("(SmallSat* WN ALL)", population)
        self.assertEqual(population.count("*"), 3)
        for literal in (
            '"CubeSat"',
            '"CubeSats"',
            '"nanosat"',
            '"nanosats"',
            '"nanosatellite"',
            '"nanosatellites"',
            '"SmallSat"',
            '"SmallSats"',
        ):
            self.assertNotIn(literal, population)
        self.assertIn('("cube sat" WN ALL)', population)
        self.assertIn('("nano-satellite" WN ALL)', population)
        self.assertIn('("small satellite" WN ALL)', population)

    def test_every_query_has_only_the_three_approved_wildcards(self) -> None:
        for partition, query in queries.EVENT_QUERIES.items():
            with self.subTest(partition=partition):
                self.assertEqual(query.count("*"), 3)
                self.assertEqual(query.count("CubeSat*"), 1)
                self.assertEqual(query.count("nanosat*"), 1)
                self.assertEqual(query.count("SmallSat*"), 1)
                self.assertNotIn("?", query)

    def test_no_proximity_or_pair_expansion(self) -> None:
        for partition, query in queries.EVENT_QUERIES.items():
            with self.subTest(partition=partition):
                self.assertIsNone(queries.PROXIMITY_OPERATOR_RE.search(query))

    def test_current_compound_definitions(self) -> None:
        expected_g_model = queries.any_of(
            queries.ORDINARY_BLOCKS["G_model_fixed"],
            queries.ORDINARY_BLOCKS["G_mission_exact"],
            queries.all_of(
                queries.ORDINARY_BLOCKS["G_mission"],
                queries.ORDINARY_BLOCKS["M_B"],
            ),
        )
        expected_g_structure = queries.any_of(
            queries.ORDINARY_BLOCKS["G_structure_fixed"],
            queries.ORDINARY_BLOCKS["G_product_exact"],
            queries.ORDINARY_BLOCKS["G_variation"],
            queries.all_of(
                queries.ORDINARY_BLOCKS["G_product"],
                queries.ORDINARY_BLOCKS["M_B"],
            ),
        )
        self.assertEqual(queries.BLOCKS["G_model"], expected_g_model)
        self.assertEqual(queries.BLOCKS["G_structure"], expected_g_structure)
        self.assertEqual(
            queries.BLOCKS["C1"],
            queries.any_of(
                queries.ORDINARY_BLOCKS["C1_fixed"],
                queries.ORDINARY_BLOCKS["G_DSL"],
            ),
        )
        self.assertEqual(
            queries.CORE_SCHEDULE["BT2"],
            queries.all_of(
                queries.BLOCKS["P"],
                queries.BLOCKS["M_B"],
                queries.BLOCKS["T_precise"],
            ),
        )

    def test_b2_and_changed_boolean_forms(self) -> None:
        self.assertEqual(
            queries.CORE_SCHEDULE["B2"],
            queries.all_of(
                queries.BLOCKS["P"], queries.BLOCKS["M_B"], queries.BLOCKS["R"]
            ),
        )
        self.assertEqual(queries.CHANGED_IDS, ("BG1", "BG2", "BC1", "BT2"))
        self.assertEqual(
            {key: queries.BOOLEAN_FORMS[key] for key in queries.CHANGED_IDS},
            {
                "BG1": "F(P) AND F(G_model)",
                "BG2": "F(P) AND F(G_structure)",
                "BC1": "F(P) AND F(C1)",
                "BT2": "F(P) AND F(M_B) AND F(T_precise)",
            },
        )

    def test_language_and_approved_a1_regression(self) -> None:
        for partition, query in queries.EVENT_QUERIES.items():
            with self.subTest(partition=partition):
                self.assertEqual(query.count(queries.LANGUAGE_CLAUSE), 1)
                self.assertTrue(query.endswith(f" AND {queries.LANGUAGE_CLAUSE})"))
        self.assertEqual(
            queries.digest_text(queries.EVENT_QUERIES["A1"]),
            queries.APPROVED_A1_QUERY_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
