"""Offline tests for the Wiley Pilot 004 query plan."""

from __future__ import annotations

import unittest

import queries


class WileyPilot004QueryTests(unittest.TestCase):
    def test_schedule_has_current_compound_blocks(self) -> None:
        self.assertIn(queries.ORDINARY["G_model_fixed"], queries.LITERAL_SCHEDULE["BG1"])
        self.assertIn(queries.ORDINARY["G_mission_exact"], queries.LITERAL_SCHEDULE["BG1"])
        self.assertIn(queries.ORDINARY["G_product"], queries.LITERAL_SCHEDULE["BG2"])
        self.assertIn(queries.ORDINARY["G_DSL"], queries.LITERAL_SCHEDULE["BC1"])
        self.assertIn(queries.ORDINARY["T_precise"], queries.LITERAL_SCHEDULE["BT2"])
        self.assertTrue(all("NEAR" not in value.upper() for value in queries.LITERAL_SCHEDULE.values()))

    def test_a2_is_the_only_two_cell_partition(self) -> None:
        for variant in ("literal", "wildcard"):
            cells = queries.schedule_cells(variant)
            self.assertEqual(2, len(cells["A2"]))
            self.assertEqual({"mh", "mb"}, {cell["cell_id"] for cell in cells["A2"]})
            for partition_id in set(queries.SCHEDULE_IDS) - {"A2"}:
                self.assertEqual(1, len(cells[partition_id]))

    def test_wildcards_replace_only_three_declared_families(self) -> None:
        atoms = queries.wildcard_population_atoms()
        self.assertEqual(21, len(atoms))
        self.assertEqual(1, atoms.count("CubeSat*"))
        self.assertEqual(1, atoms.count("nanosat*"))
        self.assertEqual(1, atoms.count("SmallSat*"))
        self.assertEqual(3, sum("*" in atom for atom in atoms))
        for query in queries.WILDCARD_SCHEDULE.values():
            self.assertEqual(3, query.count("*"))

    def test_every_adopted_cell_is_within_the_source_ceiling(self) -> None:
        for cells in queries.WILDCARD_CELLS.values():
            for cell in cells:
                self.assertLessEqual(len(cell["query"]), queries.SOURCE_QUERY_LIMIT)
        self.assertEqual(2770, len(queries.LITERAL_SCHEDULE["A1"]))

    def test_population_compression_saves_85_characters_per_cell(self) -> None:
        for partition_id in queries.SCHEDULE_IDS:
            literal = queries.LITERAL_CELLS[partition_id]
            wildcard = queries.WILDCARD_CELLS[partition_id]
            self.assertEqual(len(literal), len(wildcard))
            for literal_cell, wildcard_cell in zip(literal, wildcard):
                self.assertEqual(85, len(literal_cell["query"]) - len(wildcard_cell["query"]))


if __name__ == "__main__":
    unittest.main()
