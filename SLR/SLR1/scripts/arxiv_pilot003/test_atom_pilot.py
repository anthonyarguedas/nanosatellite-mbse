#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["certifi"]
# ///

"""Offline unit checks for the arXiv Atom Pilot 003 renderer."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import atom_pilot as pilot


class AtomPilotRendererTests(unittest.TestCase):
    def test_pilot_schedule_membership_and_renderer_integrity(self) -> None:
        pilot.validate_renderer()

    def test_all_nine_partitions_have_lossless_cells(self) -> None:
        self.assertEqual(
            tuple(pilot.MAIN_FACTORS),
            ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"),
        )
        expected_cell_counts = {
            "A1": 1,
            "A2": 2,
            "A3": 1,
            "B1": 1,
            "B2": 1,
            "BG1": 1,
            "BG2": 1,
            "BC1": 2,
            "BT2": 6,
        }
        self.assertEqual(
            {partition_id: len(pilot.partition_cells(partition_id)) for partition_id in pilot.MAIN_FACTORS},
            expected_cell_counts,
        )
        for partition_id in pilot.MAIN_FACTORS:
            for cell in pilot.partition_cells(partition_id):
                self.assertIn(pilot.DATE_CLAUSE, cell["query"])
                self.assertNotIn("*", cell["query"])
                self.assertNotIn("?", cell["query"])

    def test_overlong_routes_are_repaired_below_safe_budget(self) -> None:
        for partition_id in ("A2", "BC1", "BT2"):
            self.assertGreater(pilot.encoded_url_length(pilot.partition_query(partition_id)), 4094)
            self.assertLess(
                max(cell["encoded_url_length"] for cell in pilot.partition_cells(partition_id)),
                3800,
            )

    def test_t2_cell_union_preserves_every_pair_once(self) -> None:
        cells = pilot.partition_cells("BT2")
        pairs = [tuple(pair) for cell in cells for pair in cell["t2_pairs"]]
        self.assertEqual(pairs, list(pilot.CONCEPTS["T2"].pairs))
        self.assertEqual([len(cell["t2_pairs"]) for cell in cells], [38, 38, 38, 38, 38, 34])

    def test_local_pair_detector_keeps_both_order_and_gap_rule(self) -> None:
        text = "The code is reusable code where model and solver code resemble the formulation."
        matches = pilot.local_pair_matches(text, "reusable", "model")
        self.assertTrue(matches)
        self.assertEqual(matches[0]["intervening_lexical_tokens"], 2)
        self.assertEqual(matches[0]["order"], "left_then_right")
        self.assertEqual(pilot.local_pair_matches("reusable one two three four five six model", "reusable", "model"), [])

    def test_identifier_parsing_preserves_old_and_new_stable_ids(self) -> None:
        self.assertEqual(
            pilot.identifier_parts("http://arxiv.org/abs/1706.03762v7"),
            ("1706.03762", "v7", "1706.03762v7"),
        )
        self.assertEqual(
            pilot.identifier_parts("http://arxiv.org/abs/astro-ph/0101001v2"),
            ("astro-ph/0101001", "v2", "astro-ph/0101001v2"),
        )


if __name__ == "__main__":
    unittest.main()
