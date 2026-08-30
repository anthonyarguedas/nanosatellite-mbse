from __future__ import annotations

import json
import unittest
from pathlib import Path

from queries import (
    CONCEPTS,
    MAIN_FACTORS,
    PSR_FACTORS,
    RENDERERS,
    X,
    Q,
    partition_cells,
    partition_query,
)


class PilotQueryTests(unittest.TestCase):
    def test_protocol_membership_counts(self) -> None:
        expected = {
            "P": (26, 0),
            "E_H": (38, 0),
            "E_F": (37, 0),
            "M_H": (54, 0),
            "M_B": (31, 0),
            "R": (55, 0),
            "G_model": (14, 16),
            "G_structure": (8, 16),
            "C1": (26, 36),
            "T2": (0, 224),
            "X": (39, 0),
            "Q": (16, 0),
        }
        self.assertEqual(
            expected,
            {
                name: (len(concept.literals), len(concept.pairs))
                for name, concept in CONCEPTS.items()
            },
        )
        self.assertEqual(39, len(set(X.literals)))
        self.assertEqual(16, len(set(Q.literals)))

    def test_schedule_is_complete_and_separate(self) -> None:
        self.assertEqual(
            ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"),
            tuple(MAIN_FACTORS),
        )
        self.assertEqual(("PSR1", "PSR2", "PSR3", "PSR4"), tuple(PSR_FACTORS))

    def test_no_renderer_drops_an_alternative(self) -> None:
        for source_id, renderer in RENDERERS.items():
            for concept_name, concept in CONCEPTS.items():
                with self.subTest(source=source_id, concept=concept_name):
                    rendered = renderer.alternatives((concept_name,))
                    self.assertEqual(concept.alternative_count, len(rendered))
                    self.assertTrue(all(value for value in rendered))

    def test_literal_aiaa_a1_matches_prior_accepted_query(self) -> None:
        root = Path(__file__).resolve().parents[2]
        artifact = (
            root
            / "source-specific"
            / "aiaa-arc"
            / "pilots"
            / "001"
            / "searches"
            / "A1.json"
        )
        prior = json.loads(artifact.read_text(encoding="utf-8"))["query"]
        self.assertEqual(prior, partition_query("aiaa_arc", "A1"))

    def test_iaf_cells_stay_below_native_limit(self) -> None:
        for partition_id in MAIN_FACTORS:
            cells = partition_cells(
                "iaf_digital_library",
                partition_id,
                maximum_characters=500,
            )
            self.assertTrue(cells)
            self.assertEqual(len(cells), len({cell["cell_id"] for cell in cells}))
            self.assertTrue(all(len(cell["query"]) <= 500 for cell in cells))

    def test_no_unvalidated_wildcard_is_inserted(self) -> None:
        for source_id in RENDERERS:
            for partition_id in (*MAIN_FACTORS, *PSR_FACTORS):
                with self.subTest(source=source_id, partition=partition_id):
                    query = partition_query(source_id, partition_id)
                    self.assertNotIn("*", query)
                    self.assertNotIn("?", query)


if __name__ == "__main__":
    unittest.main()
