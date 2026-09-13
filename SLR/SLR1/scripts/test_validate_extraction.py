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
    automation_profile_issues,
    build_indexes,
    citation_quote_issues,
    consolidation_issues,
    cross_record_reference_issues,
    evaluation_design_issues,
    evidence_issues,
    family_consistency_issues,
    family_lead_issues,
    first_pass_lineage_issues,
    immutability_issues,
    lineage_consistency_issues,
    load_object,
    load_schemas,
    normalize_quote_text,
    normalization_issues,
    procedural_detail_issues,
    procedural_profile_issues,
    report_application_lineage_issues,
    report_reference_issues,
    reuse_level_issues,
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

    def test_templates_have_coherent_cross_references(self) -> None:
        documents = []
        for kind, schema_path in SCHEMA_PATHS.items():
            if kind == "audit":
                continue
            template_path = schema_path.with_name(
                schema_path.name.replace(".schema.json", ".template.json")
            )
            documents.append(Document(kind, template_path, load_object(template_path)))
        indexes, issues = build_indexes(documents)
        for document in documents:
            if document.kind == "report":
                issues.extend(report_reference_issues(document, indexes))
                issues.extend(report_application_lineage_issues(document, indexes))
                issues.extend(family_lead_issues(document))
                issues.extend(automation_profile_issues(document, indexes))
                issues.extend(evaluation_design_issues(document))
                issues.extend(rq2_semantic_issues(document, indexes))
                issues.extend(rq3_semantic_issues(document, indexes))
                issues.extend(procedural_profile_issues(document))
            else:
                issues.extend(cross_record_reference_issues(document, indexes))
            issues.extend(evidence_issues(document, indexes))
            issues.extend(normalization_issues(document))
        issues.extend(lineage_consistency_issues(documents, indexes))
        issues.extend(consolidation_issues(documents, indexes))
        issues.extend(family_consistency_issues(documents, indexes))
        issues.extend(reuse_level_issues(documents, indexes))
        issues.extend(procedural_detail_issues(documents))
        self.assertEqual(issues, [])

    def test_rq3_status_is_not_treated_as_an_evidence_status(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {"rq3_activities": [{"status": ["proposed"]}]},
        )
        indexes = {"report": {}, "citation": {}}

        self.assertEqual(evidence_issues(report, indexes), [])

    def test_rq3_comparable_dimensions_are_arrays_without_multiple(self) -> None:
        schemas, registry = load_schemas()
        template_path = SCHEMA_PATHS["report"].with_name(
            "protocol-extraction.template.json"
        )
        template = load_object(template_path)
        activity = template["rq3_activities"][0]
        self.assertIsInstance(activity["target_types"]["value"], list)
        self.assertIsInstance(activity["normalized_vv_objects"]["value"], list)
        self.assertIsInstance(activity["verification_levels"]["value"], list)
        self.assertIsInstance(activity["test_phases"]["value"], list)
        activity["target_types"]["value"] = ["multiple"]
        issues = schema_issues(
            [Document("report", template_path, template)], schemas, registry
        )
        self.assertTrue(issues)

    def test_schemas_have_no_composite_classification_values(self) -> None:
        forbidden = {
            "multiple",
            "mixed",
            "both",
            "cross_lifecycle",
            "end_to_end_engineering",
            "mixed_methods",
            "mixed_trade_off",
            "mixed_or_conditional",
            "artifact_and_method",
            "artifact_and_workflow",
            "method_and_workflow",
            "artifact_method_and_workflow",
        }
        found: set[str] = set()

        def walk(node: object) -> None:
            if isinstance(node, dict):
                enum = node.get("enum")
                if isinstance(enum, list):
                    found.update(
                        item for item in enum if isinstance(item, str) and item in forbidden
                    )
                for item in node.values():
                    walk(item)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        for schema_path in SCHEMA_PATHS.values():
            walk(load_object(schema_path))
        self.assertEqual(found, set())

    def test_representation_owns_multivalued_characteristics(self) -> None:
        template = load_object(
            SCHEMA_PATHS["report"].with_name("protocol-extraction.template.json")
        )
        case = template["eps_cases"][0]
        self.assertNotIn("eps_abstraction", case)
        self.assertNotIn("eps_decomposition_visibility", case)
        self.assertNotIn("eps_fidelity", case)
        for representation in case["eps_model_representations"]:
            self.assertIn("abstraction_levels", representation)
            self.assertIn("decomposition_visibilities", representation)
            self.assertIn("fidelity_levels", representation)


class NormalizationTests(unittest.TestCase):
    def test_unresolved_typed_record_reference_is_rejected(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {
                "identity": {"report_id": "report-1"},
                "context": {
                    "mission_or_platform": {
                        "value": "Mission",
                        "linked_record_refs": ["entity:missing-entity"],
                    }
                },
            },
        )
        indexes, issues = build_indexes([report])
        issues.extend(report_reference_issues(report, indexes))
        self.assertTrue(
            any("unresolved entity record reference" in issue.message for issue in issues)
        )

    def test_source_only_status_is_rejected_for_an_analytic_field(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {
                "context": {
                    "mission_or_platform": {
                        "value": "Mission",
                        "normalization_status": "not_for_synthesis",
                    }
                }
            },
        )
        self.assertTrue(normalization_issues(report))

    def test_plain_analytic_row_text_fails_the_v4_schema(self) -> None:
        schemas, registry = load_schemas()
        template_path = SCHEMA_PATHS["report"].with_name(
            "protocol-extraction.template.json"
        )
        template = load_object(template_path)
        template["mbse_approach"]["model_generation_methods"][0]["method_steps"][
            0
        ]["action"] = "unlinked action"
        issues = schema_issues(
            [Document("report", template_path, template)], schemas, registry
        )
        self.assertTrue(issues)

    def test_template_uses_item_level_inputs_and_typed_outputs(self) -> None:
        template = load_object(
            SCHEMA_PATHS["report"].with_name("protocol-extraction.template.json")
        )
        input_group = template["input_groups"][0]
        self.assertIn("input_items", input_group)
        self.assertNotIn("parameters_or_constructs", input_group)
        output = template["result_sets"][0]["outputs"][0]
        self.assertIn("linked_quantity_ids", output)
        self.assertIn("statistical_evaluations", output)
        self.assertIn("sample_size_quantity_ids", output["statistical_evaluations"][0])


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
                "linked_tool_ids",
                "organizational_prerequisites",
                "exclusions_and_limits",
            )
        }
        self.application = {
            "application_objects": value(["artifact"]),
            "setting": {
                "material_setting_differences": value("different mission"),
                "material_difference_relationship_ids": ["difference-1"],
                "relationship_to_originator": value("outside_originating_organization"),
            },
            "tailoring_or_adaptation": {
                "retained_artifact_core_method_steps_or_workflow_activities": value(
                    "core"
                ),
                "retained_refs": ["model_artifact:artifact-1"],
                "configured_or_changed_artifact_content_method_steps_or_workflow_activities": value(
                    "loads"
                ),
                "changed_refs": ["quantity:load-1"],
                "executed_operations": [{"application_operation_id": "operation-1"}],
                "reasons_for_changes_or_unchanged_use": value("mission loads differ"),
            },
            "result_and_assurance": {
                "post_tailoring_or_application_criterion": value("requirements pass"),
                "post_application_criterion_ids": ["criterion-1"],
                "assurance_method": value("simulation"),
                "assurance_timing": value("after tailoring"),
                "assurance_result": value("pass"),
                "assurance_check_ids": ["check-1"],
                "application_result": value("success"),
            },
            "independence": {
                "personnel_overlap": {"status": "none"},
                "personnel_overlap_status": "none",
                "implementation_control": value("adopter"),
                "controlling_team_entity_ids": ["team-1"],
                "adopter_attributable_evidence_for_adoption": value("adopter report"),
                "adoption_evidence_refs": ["report_application:application-1"],
                "adopter_attributable_evidence_for_assurance": value("adopter test"),
                "assurance_evidence_refs": ["check:check-1"],
            },
        }

    def test_reuse_specification(self) -> None:
        record = {
            "declared_applicability_envelope": self.envelope,
            "reuse_design": {
                "reusable_core": value("core"),
                "core_member_refs": ["model_artifact:artifact-1"],
                "variation_points": [{"variation_point_id": "variation-1"}],
                "unchanged_use_rule": {"status": "not_reported"},
                "tailoring_rules": {"status": "not_reported"},
                "tailoring_procedure_steps": [
                    {"tailoring_step_id": "tailoring-step-1"}
                ],
                "required_roles_and_skills": {"status": "none"},
                "required_tool_ids": {"status": "none"},
                "required_data_and_tool_settings": {
                    "status": "not_applicable",
                    "reason": "No data or settings required",
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
                {"artifact"},
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

    def test_actionable_procedure_requires_structured_and_complete_reporting(self) -> None:
        reported = {"value": "reported", "basis_refs": ["method_step:step-1"]}
        reporting = {
            "procedure_detail_level": value("actionable_procedure"),
            "ordered_or_connected_steps": reported,
            "material_inputs": reported,
            "outputs": {"status": "not_reported"},
            "roles_and_responsibilities": reported,
            "tools_and_settings": reported,
            "decision_rules": {"status": "none"},
            "branching_and_iteration": {"status": "none"},
            "quality_or_completion_checks": reported,
            "detail_level_reason": value("all required components are reported"),
        }
        report = Document(
            "report",
            Path("report.json"),
            {
                "mbse_approach": {
                    "model_generation_methods": [
                        {"procedure_reporting": reporting, "method_steps": [{}]}
                    ]
                }
            },
        )
        self.assertTrue(procedural_detail_issues([report]))
        reporting["outputs"] = reported
        self.assertEqual(procedural_detail_issues([report]), [])

    def test_procedural_profile_checks_generic_actionable_method(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {
                "mbse_approach": {
                    "model_generation_methods": [
                        {
                            "model_generation_method_id": "method-1",
                            "linked_output_model_artifact_ids": ["artifact-1"],
                            "procedure_reporting": {
                                "procedure_detail_level": value(
                                    "actionable_procedure"
                                )
                            },
                        }
                    ]
                },
                "reuse": {
                    "report_reuse_records": [
                        {
                            "report_reuse_record_id": "reuse-1",
                            "linked_model_artifact_ids": ["artifact-1"],
                            "artifact_types": value(["reference_or_template_model"]),
                            "artifact_generality_scopes": [
                                {
                                    "artifact_generality_scope_id": "generality-1",
                                    "generality": "mission_class_reference",
                                }
                            ],
                        }
                    ],
                    "report_applications": [],
                },
                "procedural_evidence_profile": {
                    "generic_or_reference_model_reported": {
                        "value": "yes",
                        "basis_ids": ["reuse-1"],
                    },
                    "actionable_model_construction_procedure_reported": {
                        "value": "yes",
                        "basis_ids": ["method-1", "reuse-1"],
                    },
                    "actionable_tailoring_procedure_reported": {"value": "no"},
                    "worked_tailoring_example_reported": {"value": "no"},
                    "post_tailoring_assurance_reported": {"value": "no"},
                    "generic_model_with_actionable_construction_or_tailoring": {
                        "value": "yes",
                        "basis_ids": ["method-1", "reuse-1"],
                    },
                },
            },
        )
        self.assertEqual(procedural_profile_issues(report), [])
        report.data["procedural_evidence_profile"][
            "actionable_model_construction_procedure_reported"
        ]["value"] = "no"
        self.assertTrue(procedural_profile_issues(report))


class CompositeClassificationTests(unittest.TestCase):
    def test_multiple_evaluation_components_require_integration(self) -> None:
        result_set = {
            "evaluation_design_components": value(
                ["survey", "interview_or_qualitative"]
            ),
            "methods_integration": {"status": "not_reported"},
        }
        report = Document(
            "report",
            Path("report.json"),
            {"result_sets": [result_set]},
        )
        self.assertTrue(evaluation_design_issues(report))
        result_set["methods_integration"] = value("integrated")
        self.assertEqual(evaluation_design_issues(report), [])

    def test_workflow_automation_is_derived_from_activities(self) -> None:
        workflow = {
            "workflow_activities": [{"automation_level": "manual"}],
            "automation_levels": value(["tool_assisted"]),
        }
        report = Document(
            "report",
            Path("report.json"),
            {"mbse_approach": {"workflows": [workflow]}},
        )
        self.assertTrue(automation_profile_issues(report, {"workflow": {}}))
        workflow["automation_levels"] = value(["manual"])
        self.assertEqual(
            automation_profile_issues(report, {"workflow": {}}),
            [],
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
                        "roles": value(["implementation_burden"]),
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

    def test_author_direction_cannot_be_unsupported(self) -> None:
        report = Document(
            "report",
            Path("report.json"),
            {
                "rq2_findings": [
                    {
                        "author_claimed_directions": [
                            {"direction": "unsupported"}
                        ]
                    }
                ]
            },
        )
        indexes = {"comparator": {}, "implementation_record": {}}
        issues = rq2_semantic_issues(report, indexes)
        self.assertTrue(any("reserved" in issue.message for issue in issues))

    def test_rq3_milestone_support(self) -> None:
        activity = {
            "status": [
                "proposed",
                "prepared_or_generated",
                "result_reported",
                "executed_virtual",
            ],
            "eps_target": "EPS output",
            "linked_model_artifact_ids": ["model-1"],
            "explicit_model_to_vv_bridge": "verify link",
            "method": "simulation",
            "execution_settings": value(["mil"]),
            "linked_result_criterion_ids": ["criterion-1"],
            "linked_result_output_ids": ["output-1"],
            "normalized_vv_objects": value(["model_validation"]),
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

    def test_rq3_model_assessment_uses_comparable_arrays(self) -> None:
        activity = {
            "target_types": value(["mbse_model_artifact", "digital_twin"]),
            "model_assessment_aspects": value(
                ["requirements_coverage", "synchronization_or_currency"]
            ),
            "normalized_vv_objects": value(
                ["model_verification", "model_validation"]
            ),
            "linked_model_artifact_ids": ["model-1"],
            "eps_target": "EPS digital twin",
            "explicit_model_to_vv_bridge": "model quality check",
            "method": "coverage and synchronization assessment",
            "linked_result_criterion_ids": ["criterion-1"],
            "status": ["proposed", "prepared_or_generated"],
        }
        report = Document(
            "report",
            Path("report.json"),
            {"rq3_activities": [activity]},
        )
        criterion = {
            "source_criterion_or_requirement_id": "REQ-1",
            "why_criterion_or_oracle_is_authoritative_for_intended_use": value(
                "Mission requirement"
            ),
        }
        indexes = {
            "result_criterion": {
                "criterion-1": Location(report, "/criterion", criterion)
            },
            "result_output": {},
            "coverage_item": {},
        }
        self.assertEqual(rq3_semantic_issues(report, indexes), [])

    def test_rq3_physical_execution_requires_target_hardware(self) -> None:
        activity = {
            "status": ["proposed", "result_reported", "executed_physical"],
            "hardware_present": value("support_hardware_only"),
            "linked_result_output_ids": ["output-1"],
        }
        report = Document(
            "report",
            Path("report.json"),
            {"rq3_activities": [activity]},
        )
        indexes = {
            "result_criterion": {},
            "result_output": {
                "output-1": Location(
                    report,
                    "/output",
                    {"source_reported_value": "pass"},
                )
            },
            "coverage_item": {},
        }
        issues = rq3_semantic_issues(report, indexes)
        self.assertTrue(any("target hardware" in issue.message for issue in issues))
        activity["hardware_present"] = value("actual_target_eps")
        issues = rq3_semantic_issues(report, indexes)
        self.assertFalse(any("target hardware" in issue.message for issue in issues))

    def test_rq3_predecessor_has_matching_relationship(self) -> None:
        activity = {
            "rq3_activity_id": "activity-2",
            "predecessor_rq3_activity_ids": ["activity-1"],
            "control_flow_relationship_ids": ["relationship-1"],
            "status": [],
        }
        report = Document(
            "report",
            Path("report.json"),
            {"rq3_activities": [activity]},
        )
        relationship = {
            "relationship_type": "precedes",
            "source_ref": "rq3_activity:activity-1",
            "target_ref": "rq3_activity:activity-2",
        }
        indexes = {
            "result_criterion": {},
            "result_output": {},
            "coverage_item": {},
            "relationship": {
                "relationship-1": Location(report, "/relationship", relationship)
            },
        }
        self.assertEqual(rq3_semantic_issues(report, indexes), [])
        relationship["target_ref"] = "rq3_activity:activity-3"
        issues = rq3_semantic_issues(report, indexes)
        self.assertTrue(any("matching precedes" in issue.message for issue in issues))


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
            "application_objects": value(["artifact"]),
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
                "application_objects": value(["artifact"]),
                "linked_model_generation_method_ids": {"status": "not_reported"},
                "linked_workflow_ids": {"status": "not_reported"},
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
            "application_objects": value(["artifact"]),
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
