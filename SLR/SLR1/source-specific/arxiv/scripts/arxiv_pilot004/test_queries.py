#!/usr/bin/env python3
"""Offline checks for the arXiv Pilot 004 browser translation."""

from __future__ import annotations

import unittest

import queries


class BrowserTranslationTests(unittest.TestCase):
    def test_schedule_has_nine_partitions_and_twelve_cells(self):
        self.assertEqual(tuple(queries.CELL_FACTORS), queries.SCHEDULE_IDS)
        self.assertEqual(len(queries.CELLS), 12)
        counts = {
            partition: sum(cell.partition_id == partition for cell in queries.CELLS)
            for partition in queries.SCHEDULE_IDS
        }
        self.assertEqual(counts["A2"], 2)
        self.assertEqual(counts["BG1"], 2)
        self.assertEqual(counts["BG2"], 2)
        self.assertTrue(
            all(
                value == 1
                for key, value in counts.items()
                if key not in {"A2", "BG1", "BG2"}
            )
        )

    def test_every_row_is_a_homogeneous_quoted_or_block(self):
        for cell in queries.CELLS:
            for row in cell.rows:
                self.assertNotIn("(", row)
                self.assertNotIn(")", row)
                self.assertNotIn("*", row)
                self.assertNotIn("?", row)
                self.assertNotIn("~", row)
                alternatives = row.split(" OR ")
                self.assertTrue(alternatives)
                self.assertTrue(
                    all(value.startswith('"') and value.endswith('"') for value in alternatives)
                )

    def test_compound_distribution_preserves_declared_membership(self):
        bg1 = [cell for cell in queries.CELLS if cell.partition_id == "BG1"]
        self.assertEqual(
            bg1[0].factors, ("P", "G_model_direct")
        )
        self.assertEqual(bg1[1].factors, ("P", "G_mission", "M_B"))
        bg2 = [cell for cell in queries.CELLS if cell.partition_id == "BG2"]
        self.assertEqual(bg2[0].factors, ("P", "G_structure_direct"))
        self.assertEqual(bg2[1].factors, ("P", "G_product", "M_B"))

    def test_source_term_counts_match_protocol_snapshot(self):
        self.assertEqual(len(queries.terms.P_TERMS), 26)
        self.assertEqual(len(queries.terms.EH_TERMS), 38)
        self.assertEqual(len(queries.terms.EF_TERMS), 37)
        self.assertEqual(len(queries.terms.MH_TERMS), 54)
        self.assertEqual(len(queries.terms.MB_TERMS), 31)
        self.assertEqual(len(queries.terms.R_TERMS), 55)
        self.assertEqual(len(queries.terms.TPRECISE_TERMS), 32)


if __name__ == "__main__":
    unittest.main()
