from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("queries.py")
spec = importlib.util.spec_from_file_location("springer_pilot003_queries_test", PATH)
assert spec is not None and spec.loader is not None
queries = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = queries
spec.loader.exec_module(queries)


class SpringerPilot003QueryTests(unittest.TestCase):
    def test_all_nine_schedule_entries_are_present(self) -> None:
        self.assertEqual(
            ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"),
            queries.SCHEDULE_IDS,
        )
        for partition_id in queries.SCHEDULE_IDS:
            self.assertEqual(
                queries.direct_query(partition_id),
                queries.partition_query(queries.SOURCE_ID, partition_id),
            )

    def test_full_literal_rows_keep_known_lengths(self) -> None:
        self.assertEqual(
            {
                "A1": 2770,
                "A2": 3431,
                "A3": 2152,
                "B1": 1868,
                "B2": 2114,
                "BG1": 1441,
                "BG2": 1178,
                "BC1": 3525,
                "BT2": 9013,
            },
            {key: len(queries.direct_query(key)) for key in queries.SCHEDULE_IDS},
        )

    def test_lossless_cells_are_exact_schedule_derivations(self) -> None:
        queries.assert_lossless_cell_membership()
        self.assertEqual(2, len(queries.a2_cells()))
        self.assertEqual(4, len(queries.b2_cells()))
        self.assertEqual(11, len(queries.bt2_cells()))
        self.assertTrue(
            all(
                len(cell.query) <= queries.BT2_T2_CELL_MAXIMUM_CHARACTERS
                for cell in queries.bt2_cells()
            )
        )

    def test_bt2_t2_membership_has_every_declared_pair_once(self) -> None:
        renderer = queries.RENDERERS[queries.SOURCE_ID]
        expected = renderer.alternatives(("T2",))
        observed = tuple(
            alternative
            for cell in queries.bt2_cells()
            for alternative in cell.alternatives
        )
        self.assertEqual(expected, observed)
        self.assertEqual(224, len(observed))
        self.assertEqual(224, len(set(observed)))

    def test_bt2_recovery_subcells_preserve_their_parent_membership(self) -> None:
        for parent_index in (8, 10, 11):
            parent = queries.bt2_cells()[parent_index - 1]
            observed = tuple(
                alternative
                for cell in queries.bt2_subcells(parent_index, alternatives_per_cell=5)
                for alternative in cell.alternatives
            )
            self.assertEqual(parent.alternatives, observed)
        self.assertEqual(
            queries.bt2_cells()[7].alternatives[10:15],
            tuple(
                item
                for cell in queries.bt2_subcells(8, alternatives_per_cell=1)[10:15]
                for item in cell.alternatives
            ),
        )

    def test_no_unvalidated_wildcard_is_present(self) -> None:
        for query in queries.all_source_queries():
            self.assertNotIn("*", query)
            self.assertNotIn("?", query)


if __name__ == "__main__":
    unittest.main()
