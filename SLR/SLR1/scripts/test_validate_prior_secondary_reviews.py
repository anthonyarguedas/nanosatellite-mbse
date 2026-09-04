#!/usr/bin/env python3
"""Focused tests for validate_prior_secondary_reviews.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_prior_secondary_reviews import (
    DEFAULT_DISCOVERY_RECEIPTS,
    CandidateLocation,
    Document,
    EventLocation,
    build_indexes,
    candidate_reference_issues,
    citation_reference_issues,
    discovery_event_reference_issues,
    load_discovery_receipts,
    load_object,
    load_schemas,
    matching_report_id_issues,
    schema_issues,
    source_citation_issues,
    source_route_reference_issues,
)


def document(
    name: str,
    report_id: str,
    *,
    citation_id: str,
    route_id: str,
    search_date_id: str,
    count_id: str,
    audit_id: str,
    cited_id: str | None = None,
    linked_route_id: str | None = None,
    nested_report_id: str | None = None,
    screening_record_id: str = "psr-candidate-0001",
    source_record_ids: tuple[str, ...] = ("source-record-1",),
    discovery_event_ids: tuple[str, ...] = ("event-1",),
) -> Document:
    return Document(
        Path(name),
        {
            "identity": {
                "report_id": report_id,
                "screening_record_id": screening_record_id,
                "source_record_ids": list(source_record_ids),
                "discovery_event_ids": list(discovery_event_ids),
                "verification_passes": [
                    {
                        "audit_id": audit_id,
                        "report_id": nested_report_id or report_id,
                    }
                ],
            },
            "review_methods": {
                "searched_sources_and_routes": [
                    {"source_route_id": route_id}
                ]
            },
            "scope_and_currency": {
                "review_search_dates": [
                    {
                        "search_date_id": search_date_id,
                        "source_route_ids": [linked_route_id or route_id],
                    }
                ],
                "reported_counts": [{"reported_count_id": count_id}],
            },
            "overlap_findings": {
                "test_evidence": {"citation_ids": [cited_id or citation_id]}
            },
            "citations": [
                {"citation_id": citation_id, "report_id": nested_report_id or report_id}
            ],
        },
    )


class SchemaTests(unittest.TestCase):
    def test_schema_compiles(self) -> None:
        schema, _registry = load_schemas()
        self.assertEqual(schema["$id"], "protocol-prior-secondary-reviews.schema.json")

    def test_template_validates_against_schema(self) -> None:
        schema, registry = load_schemas()
        template_path = (
            Path(__file__).resolve().parents[1]
            / "protocol-prior-secondary-reviews.template.json"
        )
        extraction = Document(template_path, load_object(template_path))

        self.assertEqual(schema_issues([extraction], schema, registry), [])


class CandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extraction = document(
            "extraction.json",
            "prior-review-report-1",
            citation_id="citation-1",
            route_id="route-1",
            search_date_id="date-1",
            count_id="count-1",
            audit_id="audit-1",
            source_record_ids=("SCOPUS-PUBLICATION:1", "WOS:1"),
        )

    def candidate(
        self,
        *,
        decision: str = "include_prior_secondary_review",
        record_ids: tuple[str, ...] = ("SCOPUS-PUBLICATION:1", "WOS:1"),
    ) -> CandidateLocation:
        return CandidateLocation(
            Path("psr-candidates.json"),
            "/records/0",
            {
                "candidate_id": "psr-candidate-0001",
                "screening_decision": decision,
                "source_records": [
                    {"source": "test", "record_ids": list(record_ids)}
                ],
            },
        )

    def test_candidate_and_source_records_match(self) -> None:
        candidates = {"psr-candidate-0001": self.candidate()}
        self.assertEqual(candidate_reference_issues([self.extraction], candidates), [])
        self.assertNotEqual(
            self.extraction.data["identity"]["report_id"],
            self.extraction.data["identity"]["screening_record_id"],
        )

    def test_candidate_must_exist(self) -> None:
        issues = candidate_reference_issues([self.extraction], {})
        self.assertIn(
            "unresolved PSR candidate ID 'psr-candidate-0001'",
            {issue.message for issue in issues},
        )
        self.assertEqual(
            {issue.pointer for issue in issues},
            {"/identity/screening_record_id"},
        )

    def test_candidate_must_be_included_and_match_source_records(self) -> None:
        candidates = {
            "psr-candidate-0001": self.candidate(
                decision="full_text_needed",
                record_ids=("SCOPUS-PUBLICATION:2",),
            )
        }
        messages = {
            issue.message
            for issue in candidate_reference_issues([self.extraction], candidates)
        }
        self.assertTrue(
            any(
                "expected 'include_prior_secondary_review'" in item
                for item in messages
            )
        )
        self.assertTrue(
            any(
                "source_record_ids do not match the candidate" in item
                for item in messages
            )
        )


class DiscoveryEventTests(unittest.TestCase):
    def extraction(
        self,
        *,
        source_record_ids: tuple[str, ...] = ("SCOPUS-PUBLICATION:1",),
        discovery_event_ids: tuple[str, ...] = ("event-1",),
    ) -> Document:
        return document(
            "extraction.json",
            "psr-candidate-0001",
            citation_id="citation-1",
            route_id="route-1",
            search_date_id="date-1",
            count_id="count-1",
            audit_id="audit-1",
            source_record_ids=source_record_ids,
            discovery_event_ids=discovery_event_ids,
        )

    def event(
        self,
        event_id: str,
        record_ids: tuple[str, ...],
    ) -> EventLocation:
        return EventLocation(
            Path("receipt.json"),
            "/events/0",
            {
                "event_id": event_id,
                "event_kind": "final",
                "stable_record_ids": list(record_ids),
            },
        )

    def test_current_discovery_receipts_load(self) -> None:
        events, issues = load_discovery_receipts(DEFAULT_DISCOVERY_RECEIPTS)
        self.assertEqual(issues, [])
        self.assertEqual(len(events), 8)

    def test_discovery_events_match_receipts(self) -> None:
        extraction = self.extraction()
        events = {
            "event-1": self.event("event-1", ("SCOPUS-PUBLICATION:1",))
        }
        self.assertEqual(
            discovery_event_reference_issues([extraction], events),
            [],
        )

    def test_every_retrieving_event_is_required(self) -> None:
        extraction = self.extraction()
        events = {
            "event-1": self.event("event-1", ("SCOPUS-PUBLICATION:1",)),
            "event-2": self.event("event-2", ("SCOPUS-PUBLICATION:1",)),
        }
        messages = {
            issue.message
            for issue in discovery_event_reference_issues([extraction], events)
        }
        self.assertTrue(any("missing ['event-2']" in item for item in messages))

    def test_source_records_must_occur_in_receipts(self) -> None:
        extraction = self.extraction(
            source_record_ids=("SCOPUS-PUBLICATION:missing",),
            discovery_event_ids=("event-1",),
        )
        events = {
            "event-1": self.event("event-1", ("SCOPUS-PUBLICATION:1",))
        }
        messages = {
            issue.message
            for issue in discovery_event_reference_issues([extraction], events)
        }
        self.assertTrue(
            any("absent from the discovery receipts" in item for item in messages)
        )


class IndexTests(unittest.TestCase):
    def test_review_wide_id_uniqueness(self) -> None:
        first = document(
            "first.json",
            "psr-candidate-0001",
            citation_id="citation-1",
            route_id="route-1",
            search_date_id="date-1",
            count_id="count-1",
            audit_id="audit-1",
        )
        second = document(
            "second.json",
            "psr-candidate-0001",
            citation_id="citation-1",
            route_id="route-1",
            search_date_id="date-1",
            count_id="count-1",
            audit_id="audit-1",
        )
        _indexes, issues = build_indexes([first, second])
        messages = {issue.message for issue in issues}
        for kind in (
            "report",
            "citation",
            "verification_pass",
            "source_route",
            "search_date",
            "reported_count",
        ):
            self.assertTrue(
                any(message.startswith(f"duplicate {kind} ID") for message in messages),
                kind,
            )


class SourceCitationTests(unittest.TestCase):
    def extraction(self, source_path: Path, citation: dict[str, object]) -> Document:
        item = document(
            "extraction.json",
            "psr-candidate-0001",
            citation_id="citation-1",
            route_id="route-1",
            search_date_id="date-1",
            count_id="count-1",
            audit_id="audit-1",
        )
        item.data["identity"]["source_file_path"] = str(source_path)
        item.data["citations"] = [
            {
                "citation_id": "citation-1",
                "report_id": "psr-candidate-0001",
                **citation,
            }
        ]
        return item

    def test_quote_is_checked_against_physical_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.md"
            source.write_text(
                "front\n<!-- PDF_PAGE: 1 -->A cafe\u0301 model-\u00ad based result.",
                encoding="utf-8",
            )
            extraction = self.extraction(
                source,
                {"page": 1, "quote": "A café model- based result."},
            )
            self.assertEqual(source_citation_issues([extraction]), [])

    def test_missing_page_and_quote_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.md"
            source.write_text(
                "<!-- PDF_PAGE: 1 -->Available text.",
                encoding="utf-8",
            )
            wrong_page = self.extraction(
                source,
                {"page": 2, "quote": "Available text."},
            )
            wrong_quote = self.extraction(
                source,
                {"page": 1, "quote": "Missing text."},
            )
            self.assertTrue(
                any(
                    "cited page" in issue.message
                    for issue in source_citation_issues([wrong_page])
                )
            )
            self.assertTrue(
                any(
                    "normalized quote" in issue.message
                    for issue in source_citation_issues([wrong_quote])
                )
            )

    def test_graphic_citation_skips_quote_matching(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.md"
            source.write_text(
                "<!-- PDF_PAGE: 1 -->Figure content.",
                encoding="utf-8",
            )
            extraction = self.extraction(
                source,
                {"page": 1, "quote": "Auditor checked", "graphic": "Figure 1"},
            )
            self.assertEqual(source_citation_issues([extraction]), [])


class ReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.first = document(
            "first.json",
            "psr-candidate-0001",
            citation_id="citation-1",
            route_id="route-1",
            search_date_id="date-1",
            count_id="count-1",
            audit_id="audit-1",
        )

    def test_local_references_resolve(self) -> None:
        indexes, index_issues = build_indexes([self.first])
        self.assertEqual(index_issues, [])
        self.assertEqual(citation_reference_issues([self.first], indexes), [])
        self.assertEqual(source_route_reference_issues([self.first], indexes), [])
        self.assertEqual(matching_report_id_issues([self.first]), [])

    def test_cross_extraction_references_are_rejected(self) -> None:
        second = document(
            "second.json",
            "psr-candidate-0002",
            citation_id="citation-2",
            route_id="route-2",
            search_date_id="date-2",
            count_id="count-2",
            audit_id="audit-2",
            cited_id="citation-1",
            linked_route_id="route-1",
        )
        indexes, _issues = build_indexes([self.first, second])
        citation_messages = {
            issue.message for issue in citation_reference_issues([second], indexes)
        }
        route_messages = {
            issue.message for issue in source_route_reference_issues([second], indexes)
        }
        self.assertIn(
            "citation ID 'citation-1' belongs to another extraction",
            citation_messages,
        )
        self.assertIn(
            "source route ID 'route-1' belongs to another extraction",
            route_messages,
        )

    def test_unresolved_references_are_rejected(self) -> None:
        unresolved = document(
            "unresolved.json",
            "psr-candidate-0002",
            citation_id="citation-2",
            route_id="route-2",
            search_date_id="date-2",
            count_id="count-2",
            audit_id="audit-2",
            cited_id="missing-citation",
            linked_route_id="missing-route",
        )
        indexes, _issues = build_indexes([unresolved])
        citation_messages = {
            issue.message for issue in citation_reference_issues([unresolved], indexes)
        }
        route_messages = {
            issue.message
            for issue in source_route_reference_issues([unresolved], indexes)
        }
        self.assertIn("unresolved citation ID 'missing-citation'", citation_messages)
        self.assertIn("unresolved source route ID 'missing-route'", route_messages)

    def test_nested_report_ids_must_match(self) -> None:
        mismatched = document(
            "mismatched.json",
            "psr-candidate-0002",
            citation_id="citation-2",
            route_id="route-2",
            search_date_id="date-2",
            count_id="count-2",
            audit_id="audit-2",
            nested_report_id="psr-candidate-9999",
        )
        messages = {issue.message for issue in matching_report_id_issues([mismatched])}
        self.assertIn(
            "verification pass report_id must equal 'psr-candidate-0002'",
            messages,
        )
        self.assertIn(
            "citation report_id must equal 'psr-candidate-0002'",
            messages,
        )


if __name__ == "__main__":
    unittest.main()
