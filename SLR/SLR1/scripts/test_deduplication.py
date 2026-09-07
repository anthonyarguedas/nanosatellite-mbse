#!/usr/bin/env python3
"""Focused tests for candidate deduplication and screening coding."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SLR1_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SLR1_DIR))

from deduplication import (  # noqa: E402
    FINAL_ARTIFACT_SELECTION_FILENAME,
    FINAL_ARTIFACT_SELECTION_SCHEMA,
    accepted_final_direct_input_paths,
    apply_screening_decisions,
    augment_with_backward_references,
    author_names,
    cluster_manifestations,
    direct_manifestations,
    normalized_ocr_identity_text,
    ocr_author_surnames,
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


class ConservativeClusteringTests(unittest.TestCase):
    class Merger:
        @staticmethod
        def normalize_year(value: object) -> str:
            return str(value) if isinstance(value, int) else ""

        @staticmethod
        def infer_source(_path: Path, _data: object) -> str:
            return "source-a"

        @staticmethod
        def clean_text(value: object) -> str:
            return value if isinstance(value, str) else ""

        @staticmethod
        def normalize_doi(value: object) -> str:
            return value if isinstance(value, str) else ""

        @staticmethod
        def normalize_text(value: object) -> str:
            return value.casefold() if isinstance(value, str) else ""

    @staticmethod
    def manifestation(
        source: str,
        record_id: str,
        *,
        doi: str = "",
        title: str = "shared title",
        year: int = 2025,
        document_type: str = "Article",
    ) -> dict[str, object]:
        return {
            "source_id": source,
            "source_record_id": record_id,
            "doi": doi,
            "normalized_title": title,
            "year": year,
            "document_type": document_type,
            "manual_identity_link_id": None,
        }

    def test_title_year_does_not_override_conflicting_dois(self) -> None:
        rows = [
            self.manifestation("source-a", "one", doi="10.1/one"),
            self.manifestation("source-b", "two", doi="10.1/two"),
        ]
        self.assertEqual(
            len(
                cluster_manifestations(
                    self.Merger(), rows, [], guarded_title_year=True
                )
            ),
            2,
        )

    def test_title_year_does_not_merge_repeated_source_records(self) -> None:
        rows = [
            self.manifestation("source-a", "one", doi=""),
            self.manifestation("source-a", "two", doi=""),
        ]
        self.assertEqual(
            len(
                cluster_manifestations(
                    self.Merger(), rows, [], guarded_title_year=True
                )
            ),
            2,
        )

    def test_title_year_does_not_merge_thesis_and_conference_paper(self) -> None:
        rows = [
            self.manifestation(
                "proquest_dissertations_theses_global",
                "thesis",
                doi="",
                document_type="Dissertation or Thesis",
            ),
            self.manifestation(
                "ieee_xplore",
                "paper",
                doi="10.1/paper",
                document_type="Conference Paper",
            ),
        ]
        self.assertEqual(
            len(
                cluster_manifestations(
                    self.Merger(), rows, [], guarded_title_year=True
                )
            ),
            2,
        )

    def test_reviewed_link_can_join_distinct_dois(self) -> None:
        rows = [
            self.manifestation("source-a", "one", doi="10.1/one"),
            self.manifestation("source-b", "two", doi="10.1/two", year=2024),
        ]
        links = [
            {
                "identity_id": "reviewed-report",
                "references": [("source-a", "one"), ("source-b", "two")],
            }
        ]
        groups = cluster_manifestations(
            self.Merger(), rows, links, guarded_title_year=True
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(
            {row["manual_identity_link_id"] for row in next(iter(groups.values()))},
            {"reviewed-report"},
        )

    def test_author_roles_and_placeholders_are_removed(self) -> None:
        self.assertEqual(
            author_names(
                [
                    {"name": "Kiselyov, Igor (author)"},
                    {"name": "Reising, Steve, committee member"},
                    {"name": "View all authors"},
                    {"name": "IEEE"},
                ]
            ),
            ["Kiselyov, Igor"],
        )

    def test_saved_abstract_enrichment_replaces_source_text(self) -> None:
        payload = {
            "results": [
                {
                    "paperId": "one",
                    "doi": "",
                    "title": "Title",
                    "year": 2025,
                    "abstract": "truncated source text",
                }
            ],
            "output_metadata": {
                "prisma_search_run": {"coverage": {"partition_id": "B1"}}
            },
        }
        with tempfile.TemporaryDirectory(dir=SLR1_DIR) as temporary:
            path = Path(temporary) / "source.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows, raw_count = direct_manifestations(
                self.Merger(),
                [path],
                {("source-a", "one"): "complete saved abstract"},
            )
        self.assertEqual(raw_count, 1)
        self.assertEqual(rows[0]["abstract"], "complete saved abstract")


class BackwardReferenceCandidateTests(unittest.TestCase):
    class Merger:
        @staticmethod
        def normalize_doi(value: object) -> str:
            return value.casefold() if isinstance(value, str) else ""

    @staticmethod
    def candidate(
        candidate_id: str,
        title: str,
        authors: list[str],
        year: int,
        doi: str = "",
    ) -> dict[str, object]:
        return {
            "candidate_id": candidate_id,
            "title": title,
            "authors": authors,
            "publication_year": year,
            "doi": doi,
            "source_records": [],
        }

    @staticmethod
    def unit(
        number: int,
        title: str,
        authors: list[str],
        surnames: list[str],
        year: int,
        doi: str = "",
    ) -> dict[str, object]:
        return {
            "query_unit_id": f"backward-query-{number:05d}",
            "identity": {
                "doi_normalized": doi,
                "title": title,
                "authors": authors,
                "author_last_names": surnames,
                "publication_year": year,
                "other_stable_identifiers": [],
            },
        }

    def test_ocr_identity_normalization_and_surname_parsing(self) -> None:
        self.assertEqual(
            normalized_ocr_identity_text(" Étude / CubeSat: ÉPS "),
            "etude cubesat eps",
        )
        self.assertEqual(
            ocr_author_surnames(
                ["Velthuizen M.A.J.", "de Weck O.L.", "Smith, Jane"]
            ),
            {"velthuizen", "weck", "smith"},
        )

    def test_backward_units_match_forward_candidates_before_append(self) -> None:
        candidates = [
            self.candidate(
                "citation-candidate-0001",
                "Café CubeSat",
                ["García M."],
                2024,
            ),
            self.candidate(
                "citation-candidate-0002",
                "A DOI match",
                ["Doe J."],
                2023,
                "10.1/example",
            ),
        ]
        ledger = {
            "counts": {"raw_reference_occurrences": 5},
            "query_units": [
                self.unit(3, "Unmatched title", ["Roe A."], ["roe"], 2022),
                self.unit(
                    2,
                    "Cafe—CubeSat",
                    ["García, M."],
                    ["garcia"],
                    2024,
                ),
                self.unit(
                    1,
                    "Different OCR title",
                    ["Doe, J."],
                    ["doe"],
                    2023,
                    "10.1/EXAMPLE",
                ),
            ],
        }
        with (
            patch(
                "deduplication.load_backward_reference_query_ledger",
                return_value=ledger,
            ),
            patch("deduplication.digest", return_value="test-digest"),
            patch("deduplication.relative", return_value="test-ledger.json"),
        ):
            records, raw_count, duplicate_count, receipt = (
                augment_with_backward_references(self.Merger(), candidates)
            )

        self.assertEqual(raw_count, 5)
        self.assertEqual(duplicate_count, 4)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[-1]["candidate_id"], "citation-candidate-0003")
        self.assertEqual(
            records[0]["source_records"][0]["record_ids"],
            ["backward-query-00002"],
        )
        self.assertEqual(
            records[1]["source_records"][0]["record_ids"],
            ["backward-query-00001"],
        )
        self.assertEqual(receipt["matched_forward_candidates"], 2)
        self.assertEqual(receipt["new_candidates_appended"], 1)
        self.assertEqual(receipt["sha256"], "test-digest")

    def test_title_match_requires_compatible_year_and_author(self) -> None:
        candidates = [
            self.candidate(
                "citation-candidate-0001",
                "Shared title",
                ["Smith J."],
                2020,
                "10.1/forward",
            )
        ]
        ledger = {
            "counts": {"raw_reference_occurrences": 3},
            "query_units": [
                self.unit(2, "Shared title", ["Jones A."], ["jones"], 2020),
                self.unit(1, "Shared title", ["Smith J."], ["smith"], 2021),
                self.unit(
                    3,
                    "Shared title",
                    ["Smith J."],
                    ["smith"],
                    2020,
                    "10.1/backward",
                ),
            ],
        }
        with (
            patch(
                "deduplication.load_backward_reference_query_ledger",
                return_value=ledger,
            ),
            patch("deduplication.digest", return_value="test-digest"),
            patch("deduplication.relative", return_value="test-ledger.json"),
        ):
            records, _raw_count, duplicate_count, receipt = (
                augment_with_backward_references(self.Merger(), candidates)
            )

        self.assertEqual(duplicate_count, 0)
        self.assertEqual(len(records), 4)
        self.assertEqual(receipt["matched_forward_candidates"], 0)
        self.assertEqual(receipt["new_candidates_appended"], 3)


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
