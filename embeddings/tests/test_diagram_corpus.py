from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diagram_corpus import build_diagram_chunks
from diagram_pipeline import (
    build_candidates,
    page_image_contexts,
    parse_json_response,
    selection_reasons,
)


class DiagramCorpusTests(unittest.TestCase):
    def test_caption_candidate_terms(self) -> None:
        self.assertIn(
            "language_name",
            selection_reasons("Figure 3. A Capella model diagram"),
        )
        self.assertIn(
            "sysml_diagram_type",
            selection_reasons("Figure 4. Internal Block Diagram (IBD)"),
        )
        self.assertIn(
            "arcadia_diagram_type",
            selection_reasons("Figure 5. [PAB] EPS"),
        )
        self.assertIn(
            "model_representation_term",
            selection_reasons("Figure 6. Logical architecture model view"),
        )
        self.assertIn(
            "language_name",
            selection_reasons("Figure 7. MATLAB/Simulink controller model"),
        )
        self.assertIn(
            "formal_automata_term",
            selection_reasons("Figure 8. Three priced timed automata"),
        )
        self.assertIn(
            "bip_term",
            selection_reasons("Figure 9. Mutual exclusion model in BIP"),
        )
        self.assertIn(
            "fault_tree_term",
            selection_reasons("Figure 10. EPS fault tree"),
        )
        self.assertIn(
            "bayesian_network_term",
            selection_reasons("Figure 11. Bayesian network model"),
        )
        self.assertIn(
            "gsn_term",
            selection_reasons("Figure 12. GSN assurance argument"),
        )
        self.assertEqual(selection_reasons("Figure 13. Battery voltage plot"), [])

    def test_pta_automata_are_candidates(self) -> None:
        candidate = next(
            row
            for row in build_candidates()
            if row["diagram_id"] == "review-1303--figure-006-48bc6b7f"
        )

        self.assertIn("formal_automata_term", candidate["selection_reasons"])
        self.assertEqual(candidate["section"], "3.2. PTA modelling")
        self.assertIn("JobProvider automaton", candidate["caption_chunks"][0]["caption"])

    def test_bip_report_context_selects_formal_architecture_diagrams(self) -> None:
        candidate = next(
            row
            for row in build_candidates()
            if row["diagram_id"] == "review-1315--figure-010-7c6b0d63"
        )

        self.assertIn("bip_in_report", candidate["selection_reasons"])
        self.assertIn("Architecture diagram", candidate["caption_chunks"][0]["caption"])

    def test_simulink_section_context_selects_short_figure_captions(self) -> None:
        candidate = next(
            row
            for row in build_candidates()
            if row["diagram_id"] == "review-0973--figure-011-f3d9c004"
        )

        self.assertIn("simulink_in_section", candidate["selection_reasons"])
        self.assertIn(
            "SIMULINK's Target Language Compiler",
            candidate["caption_chunks"][0]["context"],
        )

    def test_uncaptioned_page_images_keep_page_context(self) -> None:
        report = {
            "source_path": (
                "SLR/SLR1/pdfs/citation-reports/citation-report-1573/"
                "citation-report-1573.md"
            )
        }
        images = page_image_contexts(report)
        figure = next(row for row in images if row["image_ref"] == "figure_027.png")
        self.assertEqual(len(images), 45)
        self.assertEqual(figure["page"], 12)
        self.assertIn("Operational Analysis", figure["context"])

    def test_json_response_accepts_fence(self) -> None:
        text = """```json
{"contains_target_diagram": false, "elements": [], "relationships": [], "formal_or_executable_content": [], "other_visible_labels": [], "uncertainties": []}
```"""
        self.assertFalse(parse_json_response(text)["contains_target_diagram"])

    def test_json_response_normalizes_optional_empty_links(self) -> None:
        text = json.dumps(
            {
                "contains_target_diagram": True,
                "elements": [],
                "relationships": [
                    {
                        "source": "A",
                        "target": "B",
                        "name": None,
                        "native_type": "transition",
                        "semantic_class": "state_or_mode_transition",
                        "direction": "source_to_target",
                    }
                ],
                "formal_or_executable_content": [
                    {
                        "name": "x <= 2",
                        "native_type": "invariant",
                        "semantic_class": "constraint",
                    }
                ],
                "other_visible_labels": [],
                "uncertainties": [],
            }
        )

        analysis = parse_json_response(text)

        self.assertEqual(analysis["relationships"][0]["annotations"], [])
        self.assertEqual(
            analysis["formal_or_executable_content"][0]["linked_elements"], []
        )
        self.assertEqual(
            analysis["formal_or_executable_content"][0]["linked_relationships"],
            [],
        )

    def test_visual_elements_become_searchable_chunks(self) -> None:
        row = {
            "diagram_id": "review-9999--figure-001-12345678",
            "report_id": "review-9999",
            "status": "ok",
            "extraction_schema_version": "diagram-analysis/v2",
            "source_image": "reports/figure_001.png",
            "page_start": 4,
            "page_end": 4,
            "section": "Architecture",
            "section_key": "architecture",
            "caption_chunks": [
                {"chunk_id": "review-9999:chunk-1", "caption": "Figure 1. EPS"}
            ],
            "analysis": {
                "contains_target_diagram": True,
                "diagram_family": "capella_arcadia",
                "modeling_language": "Capella/Arcadia",
                "representation_name": "Provide Power",
                "representation_type": "PFBD",
                "summary": "The view decomposes the EPS power functions.",
                "elements": [
                    {
                        "name": "Distribute Power",
                        "native_type": "Physical Function",
                        "semantic_class": "function_or_behavior",
                        "logical_or_physical": "physical",
                        "eps_boundary": "inside",
                    }
                ],
                "relationships": [
                    {
                        "source": "Distribute Power",
                        "target": "Regulate Power",
                        "name": "power path",
                        "native_type": "Functional Exchange",
                        "semantic_class": "data_or_resource_flow_or_exchange",
                        "direction": "source_to_target",
                        "annotations": [
                            {
                                "name": "batteryLevel > minimum",
                                "native_type": "guard",
                                "semantic_class": "guard",
                            }
                        ],
                    }
                ],
                "formal_or_executable_content": [
                    {
                        "name": "voltage >= 5",
                        "native_type": "constraint",
                        "semantic_class": "constraint",
                        "linked_elements": ["Distribute Power"],
                        "linked_relationships": [],
                    }
                ],
                "other_visible_labels": [],
                "uncertainties": [],
                "confidence": 0.95,
            },
        }
        report = {
            "report_id": "review-9999",
            "screening_record_id": "review-candidate-9999",
            "title": "Example CubeSat Study",
            "publication_year": 2025,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "analyses.jsonl"
            path.write_text(json.dumps(row) + "\n", encoding="utf-8")
            chunks = build_diagram_chunks(
                {"review-9999": report}, analyses_path=path
            )

        self.assertEqual(len(chunks), 5)
        element_chunk = chunks[1]
        annotation_chunk = chunks[3]
        formal_content_chunk = chunks[4]
        self.assertEqual(element_chunk["chunk_type"], "diagram")
        self.assertEqual(
            element_chunk["diagram_extraction_schema_version"],
            "diagram-analysis/v2",
        )
        self.assertIn('Model element "Distribute Power"', element_chunk["text"])
        self.assertIn("function or behavior", element_chunk["text"])
        self.assertIn(
            'Relationship annotation "batteryLevel > minimum"',
            annotation_chunk["text"],
        )
        self.assertIn(
            'Formal or executable content "voltage >= 5"',
            formal_content_chunk["text"],
        )
        self.assertIn(
            'Linked model elements: "Distribute Power"',
            formal_content_chunk["text"],
        )
        self.assertEqual(element_chunk["image_refs"], ["reports/figure_001.png"])


if __name__ == "__main__":
    unittest.main()
