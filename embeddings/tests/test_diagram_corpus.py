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
        self.assertEqual(selection_reasons("Figure 8. Battery voltage plot"), [])

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
{"contains_target_diagram": false, "elements": [], "relationships": [], "other_visible_labels": [], "uncertainties": []}
```"""
        self.assertFalse(parse_json_response(text)["contains_target_diagram"])

    def test_visual_elements_become_searchable_chunks(self) -> None:
        row = {
            "diagram_id": "review-9999--figure-001-12345678",
            "report_id": "review-9999",
            "status": "ok",
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
                "relationships": [],
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

        self.assertEqual(len(chunks), 2)
        element_chunk = chunks[1]
        self.assertEqual(element_chunk["chunk_type"], "diagram")
        self.assertIn('Model element "Distribute Power"', element_chunk["text"])
        self.assertIn("function or behavior", element_chunk["text"])
        self.assertEqual(element_chunk["image_refs"], ["reports/figure_001.png"])


if __name__ == "__main__":
    unittest.main()
