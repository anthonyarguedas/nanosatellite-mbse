#!/usr/bin/env python3
"""Focused tests for validate_extraction.py."""

from __future__ import annotations

import unittest
from pathlib import Path

from validate_extraction import (
    SCHEMA_PATHS,
    Document,
    Location,
    application_deficiencies,
    audit_coverage_issues,
    citation_quote_issues,
    consolidation_issues,
    evidence_issues,
    family_consistency_issues,
    family_lead_issues,
    first_pass_lineage_issues,
    immutability_issues,
    lineage_consistency_issues,
    load_object,
    load_schemas,
    normalize_quote_text,
    report_application_lineage_issues,
    reuse_specification_deficiencies,
    rq2_semantic_issues,
    rq3_semantic_issues,
    schema_issues,
    split_page_text,
)


def value(item: object, **metadata: object) -> dict[str, object]:
    return {"value": item, **metadata}


class TemplateTests(unittest.TestCase):
    def test_each_extraction_schema_has_a_valid_template(self) -> None:
        schemas, registry = load_schemas()
        documents = []
        for kind, schema_path in SCHEMA_PATHS.items():
            template_path = schema_path.with_name(
                schema_path.name.replace(".schema.json", ".template.json")
            )
            documents.append(Document(kind, template_path, load_object(template_path)))

        self.assertEqual(schema_issues(documents, schemas, registry), [])

    def test_rq3_status_is_not_treated_as_an_evidence_status(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {"rq3_activities": [{"status": ["proposed"]}]},
        )
        indexes = {"report": {}, "citation": {}}

        self.assertEqual(evidence_issues(report, indexes), [])


class QuoteTests(unittest.TestCase):
    def test_normalized_quote_and_graphic_exception(self) -> None:
        pages = split_page_text(
            "front\n<!-- PDF_PAGE: 1 -->A cafe\u0301 model-\u00ad based result.\n"
            "<!-- PDF_PAGE: 2 -->Figure text"
        )
        report = Document(
            "report",
            Path("report.json"),
            {
                "identity": {"report_id": "report-1"},
                "citations": [
                    {"page": 1, "quote": "A café model- based result."},
                    {
                        "page": 2,
                        "quote": "Checked by the auditor",
                        "graphic": "Figure 1",
                    },
                ],
            },
        )
        indexes = {
            "report": {
                "report-1": Location(
                    report,
                    "/identity/report_id",
                    report.data["identity"],
                )
            }
        }
        self.assertEqual(
            citation_quote_issues(
                [report],
                {"report-1": (Path("pages.md"), pages)},
                indexes,
            ),
            [],
        )
        self.assertEqual(normalize_quote_text("a\n b\u00ad"), "a b")


class DerivedFieldTests(unittest.TestCase):
    def test_companion_union_and_family_lead(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {
                "identity": {
                    "possible_companion_reports_or_shared_implementations": value(
                        ["report B", "artifact C"],
                        provenance="reviewer_derived",
                    ),
                    "family_lead": value("yes"),
                },
                "reuse": {
                    "report_reuse_records": [
                        {"possible_related_reports_or_artifacts": value(["report B"])},
                        {
                            "possible_related_reports_or_artifacts": value(
                                ["artifact C", "report B"]
                            )
                        },
                    ]
                },
            },
        )
        self.assertEqual(family_lead_issues(report), [])

    def test_cross_pass_only_changes_lineage_ids(self) -> None:
        baseline = Document(
            "report",
            Path("baseline.json"),
            {
                "identity": {"report_id": "report-1"},
                "reuse": {
                    "report_reuse_records": [{"lineage_id": "pending_resolution"}]
                },
            },
        )
        current = Document(
            "report",
            Path("current.json"),
            {
                "identity": {"report_id": "report-1"},
                "reuse": {"report_reuse_records": [{"lineage_id": "lineage-1"}]},
            },
        )
        self.assertEqual(immutability_issues([current], [baseline]), [])
        current.data["context"] = {}
        self.assertTrue(immutability_issues([current], [baseline]))


class ReuseTests(unittest.TestCase):
    def setUp(self) -> None:
        resolved = {"status": "not_applicable", "reason": "Does not apply"}
        self.envelope = {
            key: resolved
            for key in (
                "target_platforms_and_missions",
                "lifecycle_uses_and_decisions",
                "eps_boundary",
                "model_boundary_and_abstraction",
                "architecture_and_interfaces",
                "environment_modes_and_loads",
                "required_inputs",
                "tools_and_versions",
                "organizational_prerequisites",
                "exclusions_and_limits",
            )
        }
        self.application = {
            "application_object": value("artifact"),
            "setting": {
                "material_setting_differences": value("different mission"),
                "relationship_to_originator": value("outside_originating_organization"),
            },
            "tailoring_or_adaptation": {
                "retained_artifact_core_or_method_steps_and_rules": value("core"),
                "configured_or_changed_artifact_content_or_method_steps": value(
                    "loads"
                ),
                "reasons_for_changes_or_unchanged_use": value("mission loads differ"),
            },
            "result_and_assurance": {
                "post_tailoring_or_application_criterion": value("requirements pass"),
                "assurance_method": value("simulation"),
                "assurance_timing": value("after tailoring"),
                "assurance_result": value("pass"),
                "application_result": value("success"),
            },
            "independence": {
                "personnel_overlap": {"status": "none"},
                "implementation_control": value("adopter"),
                "adopter_attributable_evidence_for_adoption": value("adopter report"),
                "adopter_attributable_evidence_for_assurance": value("adopter test"),
            },
        }

    def test_reuse_specification(self) -> None:
        record = {
            "declared_applicability_envelope": self.envelope,
            "reuse_design": {
                "reusable_core": value("core"),
                "variation_points": value(["loads"]),
                "tailoring_rules": {"status": "not_reported"},
                "tailoring_operations": value(["configure"]),
                "required_roles_and_skills": {"status": "none"},
                "required_tools_and_data": {
                    "status": "not_applicable",
                    "reason": "No tools required",
                },
            },
        }
        self.assertEqual(reuse_specification_deficiencies(record), [])
        record["declared_applicability_envelope"]["eps_boundary"] = {
            "status": "not_reported"
        }
        self.assertIn(
            "resolved envelope dimension eps_boundary",
            reuse_specification_deficiencies(record),
        )

    def test_independent_application_prerequisites(self) -> None:
        self.assertEqual(
            application_deficiencies(
                self.application,
                {"artifact", "artifact_and_method"},
                True,
            ),
            [],
        )
        self.application["result_and_assurance"]["assurance_result"] = {
            "status": "not_reported"
        }
        self.assertIn(
            "assurance result",
            application_deficiencies(self.application, {"artifact"}, True),
        )


class RqTests(unittest.TestCase):
    def test_rq2_required_links_and_reliability_subtype(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {
                "rq2_findings": [
                    {
                        "claim_kind": value("comparative"),
                        "role": value("implementation_burden"),
                        "outcome_category": value("eps_reliability"),
                        "reliability_subtype": {"status": "not_reported"},
                        "linked_comparator_ids": {"status": "not_reported"},
                        "linked_implementation_record_ids": {"status": "not_reported"},
                    }
                ]
            },
        )
        indexes = {"comparator": {}, "implementation_record": {}}
        self.assertEqual(len(rq2_semantic_issues(report, indexes)), 3)

    def test_rq3_milestone_support(self) -> None:
        activity = {
            "status": [
                "proposed",
                "prepared_or_generated",
                "result_reported",
                "executed_virtual",
            ],
            "eps_target": "EPS output",
            "model_artifact_id": "model-1",
            "explicit_model_to_vv_bridge": "verify link",
            "method": "simulation",
            "execution_settings": value(["mil"]),
            "linked_result_criterion_ids": ["criterion-1"],
            "linked_result_output_ids": ["output-1"],
            "normalized_vv_object": value("model_validation"),
        }
        report = Document(
            "report",
            Path("report.json"),
            {"rq3_activities": [activity]},
        )
        criterion = {
            "source_criterion_or_requirement_id": "REQ-1",
            "threshold_or_expected_behavior": "at least 5 W",
            "result_or_verdict": "pass",
            "why_criterion_or_oracle_is_authoritative_for_intended_use": value(
                "Mission requirement"
            ),
        }
        output = {"source_reported_value": "6 W"}
        indexes = {
            "result_criterion": {
                "criterion-1": Location(report, "/criterion", criterion)
            },
            "result_output": {"output-1": Location(report, "/output", output)},
        }
        self.assertEqual(rq3_semantic_issues(report, indexes), [])


class CrossRecordTests(unittest.TestCase):
    def test_family_membership(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {"identity": {"report_id": "report-1"}},
        )
        family = Document(
            "family",
            Path("family.json"),
            {"family_id": "family-1", "linked_report_ids": ["report-1"]},
        )
        indexes = {
            "report": {
                "report-1": Location(
                    report,
                    "/identity/report_id",
                    report.data["identity"],
                )
            }
        }
        self.assertEqual(family_consistency_issues([report, family], indexes), [])

    def test_consolidation_union(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {"identity": {"report_id": "report-1"}},
        )
        application = {
            "report_application_id": "application-1",
            "application_object": value("artifact"),
            "lineage_id": "lineage-1",
            "setting": {"linked_eps_case_ids": ["eps-1"]},
        }
        indexes = {
            "report_application": {
                "application-1": Location(
                    report,
                    "/reuse/report_applications/0/report_application_id",
                    application,
                )
            }
        }
        consolidated = Document(
            "tailoring_application",
            Path("consolidated.json"),
            {
                "linked_report_application_ids": ["application-1"],
                "linked_report_ids": ["report-1"],
                "linked_eps_case_ids": ["eps-1"],
            },
        )
        self.assertEqual(consolidation_issues([report, consolidated], indexes), [])

    def test_first_pass_and_resolved_lineage(self) -> None:
        artifact = {
            "report_reuse_record_id": "reuse-1",
            "lineage_id": "pending_resolution",
            "claimed_reuse_object": value(["artifact"]),
            "reuse_assessment": {"report_reuse_level": value("R0_artifact_only")},
        }
        baseline = Document(
            "report",
            Path("baseline.json"),
            {
                "reuse": {
                    "lineage_mentioned": value("yes"),
                    "report_reuse_records": [artifact],
                    "report_applications": [],
                }
            },
        )
        self.assertEqual(first_pass_lineage_issues([baseline]), [])

        report = Document(
            "report",
            Path("report.json"),
            {"identity": {"report_id": "report-1"}},
        )
        resolved = {**artifact, "lineage_id": "lineage-1"}
        report_application = {
            "application_object": value("artifact"),
            "lineage_id": "lineage-1",
            "linked_report_reuse_record_ids": ["reuse-1"],
        }
        report.data["reuse"] = {"report_applications": [report_application]}
        indexes = {
            "report_reuse_record": {
                "reuse-1": Location(
                    report,
                    "/reuse/report_reuse_records/0/report_reuse_record_id",
                    resolved,
                )
            },
            "report_application": {},
        }
        self.assertEqual(report_application_lineage_issues(report, indexes), [])
        lineage = Document(
            "lineage",
            Path("lineage.json"),
            {
                "lineage_id": "lineage-1",
                "linked_report_reuse_record_ids": ["reuse-1"],
                "linked_report_ids": ["report-1"],
            },
        )
        indexes["lineage"] = {
            "lineage-1": Location(lineage, "/lineage_id", lineage.data)
        }
        self.assertEqual(lineage_consistency_issues([report, lineage], indexes), [])

    def test_audit_coverage(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {"identity": {"report_id": "report-1"}},
        )
        lineage = Document(
            "lineage",
            Path("lineage.json"),
            {
                "lineage_id": "lineage-1",
                "reuse_assessment": {
                    "lineage_reuse_level": value("R3_reuse_demonstrated")
                },
            },
        )
        report_audit = Document(
            "audit",
            Path("report-audit.json"),
            {"report_id": "report-1", "audit_completion_status": "complete"},
        )
        lineage_audit = Document(
            "audit",
            Path("lineage-audit.json"),
            {"lineage_id": "lineage-1", "audit_completion_status": "complete"},
        )
        indexes = {
            "report": {
                "report-1": Location(
                    report,
                    "/identity/report_id",
                    report.data["identity"],
                )
            },
            "lineage": {"lineage-1": Location(lineage, "/lineage_id", lineage.data)},
        }
        self.assertEqual(
            audit_coverage_issues(
                [report, lineage, report_audit, lineage_audit],
                indexes,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
