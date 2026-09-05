#!/usr/bin/env python3
"""Focused tests for full-text screening coding in deduplication.py."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SLR1_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SLR1_DIR))

from deduplication import (  # noqa: E402
    FINAL_ARTIFACT_SELECTION_FILENAME,
    FINAL_ARTIFACT_SELECTION_SCHEMA,
    accepted_final_direct_input_paths,
    apply_screening_decisions,
    reviewer_screening_coding,
)


def record(decision: str, **coding: str) -> dict[str, object]:
    return {
        "screening_decision": decision,
        "source_records": [
            {
                "source": "test-source",
                "record_ids": ["test-record-1"],
                "partitions": ["A1"],
            }
        ],
        **coding,
    }


class FinalArtifactSelectionTests(unittest.TestCase):
    def test_explicit_selection_excludes_superseded_normal_outputs(self) -> None:
        repository_root = SLR1_DIR.parents[1]
        with tempfile.TemporaryDirectory(dir=SLR1_DIR) as temporary:
            directory = Path(temporary) / "source" / "final-searches"
            artifact = directory / "corrective" / "A1.json"
            superseded = directory / "attempt" / "A1.json"
            artifact.parent.mkdir(parents=True)
            superseded.parent.mkdir(parents=True)
            payload = {
                "schema_version": "academic-search-result/v1",
                "results": [],
                "output_metadata": {
                    "merge_eligible": True,
                    "retrieval_complete": True,
                },
            }
            encoded = json.dumps(payload).encode("utf-8")
            artifact.write_bytes(encoded)
            superseded.write_bytes(encoded)
            selection = {
                "schema_version": FINAL_ARTIFACT_SELECTION_SCHEMA,
                "status": "complete",
                "review_namespace": "main",
                "artifact_count": 1,
                "artifacts": [
                    {
                        "path": str(artifact.relative_to(repository_root)),
                        "sha256": hashlib.sha256(encoded).hexdigest(),
                        "byte_count": len(encoded),
                    }
                ],
            }
            (directory / FINAL_ARTIFACT_SELECTION_FILENAME).write_text(
                json.dumps(selection), encoding="utf-8"
            )
            self.assertEqual(
                accepted_final_direct_input_paths(directory), [artifact.resolve()]
            )

            artifact.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Changed selected"):
                accepted_final_direct_input_paths(directory)


class ReviewerScreeningCodingTests(unittest.TestCase):
    def test_included_article_requires_publication_type(self) -> None:
        included = record(
            "include_route_A_eps_primary",
            publication_type="journal_article",
        )
        self.assertEqual(
            reviewer_screening_coding(included, "review-searches"),
            {"publication_type": "journal_article"},
        )
        with self.assertRaisesRegex(ValueError, "requires reviewer-coded"):
            reviewer_screening_coding(
                record("include_route_A_eps_primary"),
                "review-searches",
            )

    def test_included_thesis_requires_completed_degree_coding(self) -> None:
        thesis = record(
            "include_route_B_embedded_eps",
            publication_type="masters_thesis",
            degree_level="masters",
            completion_status="completed",
        )
        self.assertEqual(
            reviewer_screening_coding(thesis, "citation-chasing"),
            {
                "publication_type": "masters_thesis",
                "degree_level": "masters",
                "completion_status": "completed",
            },
        )
        thesis["completion_status"] = "in_progress_or_incomplete"
        with self.assertRaisesRegex(ValueError, "must be completed"):
            reviewer_screening_coding(thesis, "citation-chasing")

    def test_incomplete_thesis_uses_completion_status_exclusion(self) -> None:
        thesis = record(
            "exclude_wrong_completion_status",
            publication_type="doctoral_thesis_or_dissertation",
            degree_level="doctoral",
            completion_status="in_progress_or_incomplete",
        )
        self.assertEqual(
            reviewer_screening_coding(thesis, "review-searches"),
            {
                "publication_type": "doctoral_thesis_or_dissertation",
                "degree_level": "doctoral",
                "completion_status": "in_progress_or_incomplete",
            },
        )
        thesis["completion_status"] = "completed"
        with self.assertRaisesRegex(ValueError, "requires a non-completed status"):
            reviewer_screening_coding(thesis, "review-searches")

    def test_degree_fields_are_limited_to_theses(self) -> None:
        article = record(
            "include_route_A_eps_primary",
            publication_type="journal_article",
            degree_level="masters",
            completion_status="completed",
        )
        with self.assertRaisesRegex(ValueError, "only for a thesis"):
            reviewer_screening_coding(article, "review-searches")

    def test_other_exclusions_do_not_receive_publication_coding(self) -> None:
        excluded = record(
            "exclude_wrong_population",
            publication_type="conference_paper",
        )
        with self.assertRaisesRegex(ValueError, "require an inclusion"):
            reviewer_screening_coding(excluded, "review-searches")

    def test_psr_candidates_do_not_receive_main_review_coding(self) -> None:
        psr = record(
            "include_prior_secondary_review",
            publication_type="journal_article",
        )
        with self.assertRaisesRegex(ValueError, "PSR candidates"):
            reviewer_screening_coding(psr, "psr")


class ScreeningTransferTests(unittest.TestCase):
    def test_rebuild_transfers_full_text_publication_coding(self) -> None:
        prior_record = record(
            "include_route_A_eps_primary",
            publication_type="journal_article",
        )
        prior = {
            "schema_version": "slr1-screening-candidates/v2",
            "mode": "review-searches",
            "records": [prior_record],
        }
        rebuilt_record = record("none")
        payload = {"records": [rebuilt_record]}

        self.assertEqual(
            apply_screening_decisions(payload, prior, "review-searches"),
            1,
        )
        self.assertEqual(
            rebuilt_record["screening_decision"],
            "include_route_A_eps_primary",
        )
        self.assertEqual(rebuilt_record["publication_type"], "journal_article")
        self.assertNotIn("degree_level", rebuilt_record)
        self.assertNotIn("completion_status", rebuilt_record)


if __name__ == "__main__":
    unittest.main()
