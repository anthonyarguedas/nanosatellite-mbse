from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prepare_corpus import (
    build_chunks,
    build_equation_chunks,
    expected_sources,
    included_report_sources,
    parse_markdown,
)


class PrepareCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = {
            "report_id": "review-9999",
            "screening_record_id": "review-candidate-9999",
            "title": "Example CubeSat Study",
            "publication_year": 2025,
        }

    def test_expected_sources_match_authoritative_included_reports(self) -> None:
        selected = included_report_sources()
        actual = {
            report["report_id"]: path
            for report, path, _source_kind in expected_sources()
        }

        self.assertEqual(actual, selected)
        self.assertIn("handpicked-0001", actual)
        self.assertIn("handpicked-0002", actual)
        self.assertIn("handpicked-0003", actual)
        self.assertIn("psr-0024", actual)
        self.assertIn("psr-0039", actual)
        self.assertIn("psr-0092", actual)

    def test_page_and_section_provenance(self) -> None:
        markdown = """---
page_count: 2
---
<!-- PDF_PAGE: 1 -->
# Example CubeSat Study
## Method
The system model traces battery requirements to power modes.

<!-- PDF_PAGE: 2 -->
The model computes the energy margin before integration.
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        self.assertEqual([unit.section for unit in units], ["Method", "Method"])
        self.assertEqual([unit.page_start for unit in units], [1, 2])

        chunks = build_chunks(
            self.report, units, target_words=30, max_words=60, overlap_words=5
        )
        self.assertEqual(chunks[0]["page_start"], 1)
        self.assertEqual(chunks[0]["page_end"], 2)
        self.assertIn("Document: Example CubeSat Study", chunks[0]["embedding_text"])
        self.assertIn("Section: Method", chunks[0]["embedding_text"])

    def test_html_table_rows_remain_units_and_are_grouped_for_embedding(self) -> None:
        markdown = """<!-- PDF_PAGE: 3 -->
## Results
<table><tr><th>Mode</th><th>Power</th></tr><tr><td>Safe</td><td>2 W</td></tr><tr><td>Imaging</td><td>8 W</td></tr></table>
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        self.assertEqual(len(units), 2)
        self.assertTrue(all(unit.kind == "table_row" for unit in units))
        self.assertEqual(units[0].text, "Table row. Mode: Safe; Power: 2 W.")

        chunks = build_chunks(
            self.report, units, target_words=50, max_words=100, overlap_words=5
        )
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["chunk_type"], "table")
        self.assertIn("Mode: Imaging", chunks[0]["text"])

    def test_equation_chunk_uses_an_explicit_caption(self) -> None:
        markdown = r"""<!-- PDF_PAGE: 4 -->
## Power analysis
Equation (3) defines stored battery energy over the orbit.

$$
E_{battery} = \int_0^T (P_{solar} - P_{load})\,dt
$$

where solar power is generation and load power is consumption.
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        self.assertEqual([unit.kind for unit in units], ["prose", "equation", "prose"])

        chunks = build_equation_chunks(self.report, units, max_words=100)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["chunk_type"], "equation")
        self.assertEqual(chunks[0]["equation_label"], "3")
        self.assertEqual(chunks[0]["equation_context_source"], "caption")
        self.assertIn("stored battery energy", chunks[0]["equation_caption"])
        self.assertIn("E_{battery}", chunks[0]["text"])

    def test_equation_chunk_falls_back_to_surrounding_context(self) -> None:
        markdown = r"""<!-- PDF_PAGE: 5 -->
## Link budget
Received power depends on transmitter and path properties.

$$
P_r = P_t G_t G_r L_s
$$

The terms describe transmit power, antenna gains, and free-space loss.
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        chunks = build_equation_chunks(self.report, units, max_words=100)

        self.assertEqual(chunks[0]["equation_context_source"], "surrounding_context")
        self.assertIsNone(chunks[0]["equation_caption"])
        self.assertIn("Context before equation", chunks[0]["text"])
        self.assertIn("Context after equation", chunks[0]["text"])

    def test_equation_range_labels_consecutive_display_math(self) -> None:
        markdown = r"""<!-- PDF_PAGE: 6 -->
## Constraints
Equations (1-2) define the lower and upper energy limits.

$$
e \geq e_{min}
$$

$$
e \leq e_{max}
$$
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        chunks = build_equation_chunks(self.report, units, max_words=100)

        self.assertEqual([chunk["equation_label"] for chunk in chunks], ["1", "2"])

    def test_caption_gets_nearby_context(self) -> None:
        markdown = """<!-- PDF_PAGE: 4 -->
## Architecture
The block definition diagram connects the battery to the regulated power bus.

![figure_001.png](images/figure_001.png)

Fig. 2. Electrical power architecture.
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        caption = units[-1]
        self.assertEqual(caption.kind, "caption")
        self.assertEqual(caption.image_refs, ["images/figure_001.png"])
        self.assertEqual(caption.context_unit_ids, [units[0].unit_id])

        chunks = build_chunks(
            self.report, units, target_words=50, max_words=100, overlap_words=5
        )
        caption_chunk = chunks[-1]
        self.assertIn("Nearby context", caption_chunk["text"])
        self.assertIn("regulated power bus", caption_chunk["text"])

    def test_discussion_that_starts_with_figure_is_not_a_long_caption(self) -> None:
        markdown = """<!-- PDF_PAGE: 5 -->
## Analysis
Figure 3 shows the complete simulation workflow and explains how each model exchanges parameters with the power subsystem. The workflow begins with requirements and continues through architecture generation, analysis, verification, and reporting. The engineers repeat these steps whenever a requirement changes, which preserves traceability between the source requirement and every calculated result.
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        self.assertEqual(units[0].kind, "prose")

    def test_reference_section_is_excluded(self) -> None:
        markdown = """<!-- PDF_PAGE: 1 -->
## Findings
The model detected an invalid battery state.

## References
[1] A source about batteries.
"""
        units = parse_markdown("review-9999", self.report["title"], markdown)
        self.assertEqual(len(units), 1)
        self.assertNotIn("source about batteries", units[0].text)


if __name__ == "__main__":
    unittest.main()
