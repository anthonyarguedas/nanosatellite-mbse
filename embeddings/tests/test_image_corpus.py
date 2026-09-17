from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from image_corpus import build_image_records, image_search_text, resolve_report_image


class ImageCorpusTests(unittest.TestCase):
    def test_all_report_images_are_indexed_and_diagrams_are_marked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report_dir = root / "reports/report-0001"
            report_dir.mkdir(parents=True)
            source = report_dir / "report-0001.md"
            source.write_text(
                """<!-- PDF_PAGE: 3 -->
# Architecture

![figure_001.png](figure_001.png)

Figure 1. Electrical power architecture.

<!-- PDF_PAGE: 4 -->
![figure_002.png](figure_002.png)
""",
                encoding="utf-8",
            )
            (report_dir / "figure_001.png").write_bytes(b"first image")
            (report_dir / "figure_002.png").write_bytes(b"second image")
            report = {
                "report_id": "review-0001",
                "screening_record_id": "review-candidate-0001",
                "title": "Example report",
                "publication_year": 2025,
                "source_path": "reports/report-0001/report-0001.md",
            }
            units = [
                {
                    "unit_id": "review-0001:unit-00001",
                    "report_id": "review-0001",
                    "text": "Figure 1. Electrical power architecture.",
                    "kind": "caption",
                    "section": "Architecture",
                    "section_key": "architecture",
                    "page_start": 3,
                    "page_end": 3,
                    "image_refs": ["figure_001.png"],
                    "context_unit_ids": [],
                }
            ]
            analyses = [
                {
                    "status": "ok",
                    "diagram_id": "review-0001--figure-001-12345678",
                    "source_image": "reports/report-0001/figure_001.png",
                    "analysis": {
                        "contains_target_diagram": True,
                        "modeling_language": "SysML",
                        "representation_type": "internal block diagram",
                        "summary": "The battery connects to a regulated power bus.",
                    },
                }
            ]

            records = build_image_records([report], units, analyses, root)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["caption"], units[0]["text"])
        self.assertTrue(records[0]["is_mbse_diagram"])
        self.assertEqual(records[0]["modeling_language"], "SysML")
        self.assertFalse(records[1]["is_mbse_diagram"])
        self.assertEqual(records[1]["page_start"], 4)
        self.assertIn("Electrical power architecture", image_search_text(records[0]))

    def test_image_reference_cannot_leave_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "reports/report.md"
            source.parent.mkdir()
            source.write_text("", encoding="utf-8")

            with self.assertRaises(ValueError):
                resolve_report_image(root, source, "../../outside.png")


if __name__ == "__main__":
    unittest.main()
