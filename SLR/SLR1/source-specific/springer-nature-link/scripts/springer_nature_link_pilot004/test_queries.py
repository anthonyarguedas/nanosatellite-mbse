from __future__ import annotations

import unittest

import queries


class SpringerPilot004QueryTests(unittest.TestCase):
    def test_protocol_membership_is_pinned(self) -> None:
        self.assertEqual(
            queries.EXPECTED_COUNTS,
            {name: len(values) for name, values in queries.TERMS.items()},
        )
        self.assertEqual(26, len(queries.P_TERMS))

    def test_current_compound_schedule_has_no_proximity_or_pairs(self) -> None:
        self.assertEqual(queries.SCHEDULE_IDS, tuple(queries.LITERAL_SCHEDULE))
        for query in queries.LITERAL_SCHEDULE.values():
            self.assertNotIn("NEAR", query.upper())
            self.assertNotIn(" W/", query.upper())
            self.assertNotIn("~", query)
            self.assertNotIn("*", query)
            self.assertNotIn("?", query)
        self.assertIn(
            queries.ORDINARY["G_mission"] + " AND " + queries.ORDINARY["M_B"],
            queries.LITERAL_SCHEDULE["BG1"],
        )
        self.assertIn(
            queries.ORDINARY["G_product"] + " AND " + queries.ORDINARY["M_B"],
            queries.LITERAL_SCHEDULE["BG2"],
        )
        self.assertIn(queries.ORDINARY["G_DSL"], queries.LITERAL_SCHEDULE["BC1"])
        self.assertIn(queries.ORDINARY["T_precise"], queries.LITERAL_SCHEDULE["BT2"])

    def test_wildcard_candidate_changes_only_three_population_families(self) -> None:
        self.assertEqual(21, len(queries.wildcard_population_atoms()))
        for partition_id in queries.SCHEDULE_IDS:
            literal = queries.LITERAL_SCHEDULE[partition_id]
            wildcard = queries.WILDCARD_SCHEDULE[partition_id]
            self.assertEqual(3, wildcard.count("*"))
            self.assertEqual(len(literal) - 85, len(wildcard))
            for _terms, candidate in queries.WILDCARD_REPLACEMENTS:
                self.assertIn(candidate, wildcard)
            for name, block in queries.ORDINARY.items():
                if name != "P":
                    self.assertEqual(literal.count(block), wildcard.count(block))


if __name__ == "__main__":
    unittest.main()
