#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema==4.25.1"]
# ///

"""Validate SLR1 extraction records and their cross-record references."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ImportError as error:  # pragma: no cover - depends on the runtime environment
    raise SystemExit(
        "Install SLR/SLR1/requirements-extraction.txt before running this validator"
    ) from error

SLR1_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SLR1_DIR.parents[1]
SCHEMA_PATHS = {
    "report": SLR1_DIR / "protocol-extraction.schema.json",
    "family": SLR1_DIR / "protocol-extraction-family.schema.json",
    "lineage": SLR1_DIR / "protocol-extraction-lineage.schema.json",
    "tailoring_application": (
        SLR1_DIR / "protocol-extraction-tailoring-application.schema.json"
    ),
    "audit": SLR1_DIR / "protocol-extraction-audit.schema.json",
}
LINEAGE_SENTINELS = {
    "pending_resolution",
    "not_applicable",
    "unresolved_after_review",
}
ARTIFACT_APPLICATION_OBJECTS = {
    "artifact",
    "artifact_and_method",
    "artifact_and_workflow",
    "artifact_method_and_workflow",
}
METHOD_APPLICATION_OBJECTS = {
    "method",
    "artifact_and_method",
    "method_and_workflow",
    "artifact_method_and_workflow",
}
WORKFLOW_APPLICATION_OBJECTS = {
    "workflow",
    "artifact_and_workflow",
    "method_and_workflow",
    "artifact_method_and_workflow",
}
NON_ARTIFACT_APPLICATION_OBJECTS = {
    "method",
    "workflow",
    "method_and_workflow",
}
MODEL_ASSESSMENT_TARGET_TYPES = {
    "mbse_model_artifact",
    "digital_twin",
    "model_configuration_or_baseline",
    "model_transformation_or_generator",
    "model_representation_or_view",
}
COMPLETENESS_ASSESSMENT_ASPECTS = {
    "declared_scope_completeness",
    "requirements_coverage",
    "traceability_completeness",
    "viewpoint_coverage",
    "interface_coverage",
    "scenario_or_mode_coverage",
    "data_or_parameter_completeness",
}
TARGET_HARDWARE_PRESENCE = {
    "representative_target_hardware",
    "actual_target_component",
    "actual_target_eps",
    "integrated_spacecraft_hardware",
}
PAGE_MARKER = re.compile(r"<!--\s*PDF_PAGE:\s*([1-9][0-9]*)\s*-->")
SCREENING_SCHEMA = "slr1-screening-candidates/v2"
SCREENING_ID_PREFIXES = {
    "psr": "psr-candidate-",
    "review-searches": "review-candidate-",
    "citation-chasing": "citation-candidate-",
}
RECORD_REFERENCE = re.compile(r"^([a-z][a-z0-9_]*):(.+)$")
DIRECT_REFERENCE_FIELDS = {
    "citation_ids": "citation",
    "contributing_report_ids": "report",
    "linked_report_ids": "report",
    "linked_family_ids": "family",
    "parent_entity_ids": "entity",
    "construct_entity_ids": "entity",
    "linked_entity_ids": "entity",
    "group_or_arm_entity_ids": "entity",
    "method_entity_ids": "entity",
    "linked_scenario_entity_ids": "entity",
    "linked_configuration_entity_ids": "entity",
    "analysis_method_entity_ids": "entity",
    "adopting_team_entity_ids": "entity",
    "responsible_role_entity_ids": "entity",
    "tool_configuration_entity_ids": "entity",
    "configuration_entity_ids": "entity",
    "implementing_team_entity_ids": "entity",
    "controlling_team_entity_ids": "entity",
    "required_role_entity_ids": "entity",
    "required_skill_entity_ids": "entity",
    "quantity_id": "quantity",
    "linked_quantity_ids": "quantity",
    "value_quantity_ids": "quantity",
    "uncertainty_quantity_ids": "quantity",
    "count_quantity_ids": "quantity",
    "estimate_quantity_ids": "quantity",
    "confidence_interval_quantity_ids": "quantity",
    "sample_size_quantity_ids": "quantity",
    "linked_source_quantity_ids": "quantity",
    "result_quantity_ids": "quantity",
    "sensitivity_quantity_ids": "quantity",
    "option_quantity_ids": "quantity",
    "threshold_quantity_ids": "quantity",
    "time_basis_quantity_id": "quantity",
    "denominator_quantity_id": "quantity",
    "p_value_quantity_id": "quantity",
    "linked_decision_ids": "decision",
    "linked_physical_or_operational_relationship_ids": "relationship",
    "material_difference_relationship_ids": "relationship",
    "dependency_relationship_ids": "relationship",
    "mechanism_relationship_ids": "relationship",
    "model_to_vv_relationship_ids": "relationship",
    "later_physical_relationship_ids": "relationship",
    "before_after_relationship_ids": "relationship",
    "unit_conversion_relationship_ids": "relationship",
    "selection_rule_ids": "rule",
    "sampling_or_selection_rule_ids": "rule",
    "assignment_rule_ids": "rule",
    "threshold_rule_ids": "rule",
    "trigger_rule_ids": "rule",
    "constraint_rule_ids": "rule",
    "governance_rule_ids": "rule",
    "reason_rule_ids": "rule",
    "formula_rule_ids": "rule",
    "assumption_rule_ids": "rule",
    "limit_rule_ids": "rule",
    "authority_check_ids": "check",
    "linked_check_ids": "check",
    "acceptance_check_ids": "check",
    "check_ids": "check",
    "assurance_check_ids": "check",
    "closure_check_ids": "check",
    "linked_resource_ids": "resource",
    "source_resource_ids": "resource",
    "data_source_resource_ids": "resource",
    "linked_issue_ids": "issue",
    "discrepancy_issue_ids": "issue",
    "linked_tool_ids": "tool",
    "required_tool_ids": "tool",
    "parent_model_artifact_ids": "model_artifact",
    "derived_model_artifact_ids": "model_artifact",
    "resulting_model_artifact_ids": "model_artifact",
    "linked_model_artifact_ids": "model_artifact",
    "linked_source_model_artifact_ids": "model_artifact",
    "linked_output_model_artifact_ids": "model_artifact",
    "linked_model_generation_method_ids": "model_generation_method",
    "linked_workflow_ids": "workflow",
    "linked_workflow_activity_ids": "workflow_activity",
    "eps_case_ids": "eps_case",
    "linked_eps_case_ids": "eps_case",
    "eps_case_id": "eps_case",
    "linked_eps_element_ids": "eps_element",
    "source_eps_element_id": "eps_element",
    "destination_eps_element_id": "eps_element",
    "dependent_eps_element_id": "eps_element",
    "provider_or_driver_eps_element_id": "eps_element",
    "source_eps_element_ids": "eps_element",
    "destination_eps_element_ids": "eps_element",
    "context_eps_element_ids": "eps_element",
    "parent_eps_element_ids": "eps_element",
    "interface_eps_element_ids": "eps_element",
    "eps_anchor_element_ids": "eps_element",
    "second_concern_element_ids": "eps_element",
    "linked_eps_requirement_ids": "eps_requirement",
    "parent_eps_requirement_ids": "eps_requirement",
    "eps_anchor_requirement_ids": "eps_requirement",
    "second_concern_requirement_ids": "eps_requirement",
    "linked_eps_exchange_ids": "eps_exchange",
    "linked_eps_dependency_ids": "eps_dependency",
    "linked_eps_model_bridge_ids": "eps_model_bridge",
    "linked_model_representation_ids": "model_representation",
    "source_model_representation_id": "model_representation",
    "target_model_representation_id": "model_representation",
    "model_artifact_id": "model_artifact",
    "linked_result_set_ids": "result_set",
    "linked_result_output_ids": "result_output",
    "linked_result_criterion_ids": "result_criterion",
    "post_application_criterion_ids": "result_criterion",
    "linked_comparator_ids": "comparator",
    "linked_input_group_ids": "input_group",
    "linked_input_item_ids": "input_item",
    "linked_implementation_record_ids": "implementation_record",
    "linked_rq1_claim_ids": "rq1_claim",
    "linked_rq2_finding_ids": "rq2_finding",
    "trade_off_rq2_finding_ids": "rq2_finding",
    "linked_rq3_activity_ids": "rq3_activity",
    "assurance_rq3_activity_ids": "rq3_activity",
    "predecessor_rq3_activity_ids": "rq3_activity",
    "linked_coverage_item_ids": "coverage_item",
    "linked_report_reuse_record_ids": "report_reuse_record",
    "linked_report_application_ids": "report_application",
    "linked_tailoring_application_ids": "tailoring_application",
    "linked_variation_point_ids": "variation_point",
    "linked_tailoring_rule_ids": "tailoring_rule",
    "linked_tailoring_step_ids": "tailoring_step",
    "linked_report_variation_point_ids": "variation_point",
    "linked_report_tailoring_rule_ids": "tailoring_rule",
    "linked_report_tailoring_step_ids": "tailoring_step",
    "linked_report_application_operation_ids": "application_operation",
}
RECORD_REFERENCE_KINDS = {
    "report": "report",
    "family": "family",
    "lineage": "lineage",
    "citation": "citation",
    "entity": "entity",
    "quantity": "quantity",
    "decision": "decision",
    "relationship": "relationship",
    "rule": "rule",
    "check": "check",
    "resource": "resource",
    "issue": "issue",
    "tool": "tool",
    "model_artifact": "model_artifact",
    "model_generation_method": "model_generation_method",
    "construction_source": "construction_source",
    "method_step": "method_step",
    "workflow": "workflow",
    "workflow_activity": "workflow_activity",
    "eps_case": "eps_case",
    "eps_element": "eps_element",
    "eps_requirement": "eps_requirement",
    "eps_exchange": "eps_exchange",
    "eps_dependency": "eps_dependency",
    "model_representation": "model_representation",
    "model_representation_relationship": "model_representation_relationship",
    "behavior_occurrence": "behavior_occurrence",
    "eps_model_bridge": "eps_model_bridge",
    "coverage_item": "coverage_item",
    "implementation_record": "implementation_record",
    "input_group": "input_group",
    "input_item": "input_item",
    "result_set": "result_set",
    "evaluation_unit": "evaluation_unit",
    "result_output": "result_output",
    "statistical_evaluation": "statistical_evaluation",
    "result_criterion": "result_criterion",
    "comparator": "comparator",
    "rival_explanation": "rival_explanation",
    "reviewer_derived_value": "reviewer_derived_value",
    "rq1_claim": "rq1_claim",
    "rq2_finding": "rq2_finding",
    "rq3_activity": "rq3_activity",
    "report_reuse_record": "report_reuse_record",
    "artifact_relationship": "artifact_relationship",
    "variation_point": "variation_point",
    "tailoring_rule": "tailoring_rule",
    "tailoring_step": "tailoring_step",
    "report_application": "report_application",
    "application_operation": "application_operation",
    "tailoring_application": "tailoring_application",
}


@dataclass(frozen=True)
class Document:
    kind: str
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class Location:
    document: Document
    pointer: str
    node: Mapping[str, Any]


@dataclass(frozen=True)
class ScreeningLocation:
    path: Path
    pointer: str
    record: Mapping[str, Any]


@dataclass(frozen=True)
class Issue:
    path: str
    pointer: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "pointer": self.pointer,
            "message": self.message,
        }


def pointer_part(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def pointer(base: str, value: object) -> str:
    return f"{base}/{pointer_part(value)}" if base else f"/{pointer_part(value)}"


def rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def coded_value(value: Any) -> Any:
    if isinstance(value, Mapping) and "value" in value:
        return value["value"]
    return None


def has_ordinary_value(value: Any) -> bool:
    return isinstance(value, Mapping) and "value" in value


def application_object_for(
    has_artifact: bool,
    has_method: bool,
    has_workflow: bool,
    fallback: Any = None,
) -> Any:
    if has_artifact and has_method and has_workflow:
        return "artifact_method_and_workflow"
    if has_artifact and has_method:
        return "artifact_and_method"
    if has_artifact and has_workflow:
        return "artifact_and_workflow"
    if has_artifact:
        return "artifact"
    if has_method and has_workflow:
        return "method_and_workflow"
    if has_method:
        return "method"
    if has_workflow:
        return "workflow"
    return fallback


def has_resolved_evidence(value: Any) -> bool:
    if has_ordinary_value(value):
        return True
    return isinstance(value, Mapping) and value.get("status") == "none"


def has_resolved_dimension(value: Any) -> bool:
    if has_ordinary_value(value):
        return True
    return isinstance(value, Mapping) and value.get("status") in {
        "none",
        "not_applicable",
    }


def has_resolved_component(value: Any) -> bool:
    return has_resolved_dimension(value)


def has_recorded_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, Mapping):
        if "value" in value:
            return has_recorded_content(value["value"])
        if "source_text" in value:
            return has_recorded_content(value["source_text"])
    return False


def linked_locations(
    value: Any,
    index: Mapping[str, Location],
    containing_report: Document | None = None,
) -> list[Location]:
    if isinstance(value, str):
        identifiers = [value]
    elif isinstance(value, list):
        identifiers = [item for item in value if isinstance(item, str)]
    else:
        identifiers = []
    locations = [index[item] for item in identifiers if item in index]
    if containing_report is not None:
        locations = [
            location for location in locations if location.document == containing_report
        ]
    return locations


def load_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("the document root must be an object")
    return value


def normalize_quote_text(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).replace("\u00ad", "")
    return " ".join(normalized.split())


def split_page_text(value: str) -> dict[int, str]:
    matches = list(PAGE_MARKER.finditer(value))
    if not matches:
        raise ValueError("page text contains no PDF_PAGE markers")
    pages: dict[int, str] = {}
    for index, match in enumerate(matches):
        page = int(match.group(1))
        if page in pages:
            raise ValueError(f"page text repeats PDF_PAGE marker {page}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        pages[page] = value[match.end() : end]
    return pages


def load_page_texts(
    specifications: Iterable[str],
) -> tuple[dict[str, tuple[Path, dict[int, str]]], list[Issue]]:
    page_texts: dict[str, tuple[Path, dict[int, str]]] = {}
    issues: list[Issue] = []
    for specification in specifications:
        if "=" not in specification:
            issues.append(
                Issue(
                    specification,
                    "/",
                    "page-text argument must have the form REPORT_ID=PATH",
                )
            )
            continue
        identifier, raw_path = specification.split("=", 1)
        identifier = identifier.strip()
        path = Path(raw_path)
        if not identifier or not raw_path:
            issues.append(
                Issue(
                    specification,
                    "/",
                    "page-text argument must have a report ID and path",
                )
            )
            continue
        if identifier in page_texts:
            issues.append(
                Issue(
                    str(path),
                    "/",
                    f"duplicate page-text mapping for report {identifier!r}",
                )
            )
            continue
        try:
            pages = split_page_text(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            issues.append(Issue(str(path), "/", str(error)))
            continue
        page_texts[identifier] = (path, pages)
    return page_texts, issues


def load_screening_candidates(
    paths: Iterable[Path],
) -> tuple[dict[str, ScreeningLocation], list[Issue]]:
    records: dict[str, ScreeningLocation] = {}
    issues: list[Issue] = []
    for path in paths:
        try:
            payload = load_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            issues.append(Issue(str(path), "/", str(error)))
            continue
        if payload.get("schema_version") != SCREENING_SCHEMA:
            issues.append(
                Issue(
                    str(path),
                    "/schema_version",
                    f"expected {SCREENING_SCHEMA!r}",
                )
            )
        mode = payload.get("mode")
        expected_prefix = SCREENING_ID_PREFIXES.get(mode)
        if expected_prefix is None:
            issues.append(Issue(str(path), "/mode", f"unexpected mode {mode!r}"))
        candidate_rows = payload.get("records")
        if not isinstance(candidate_rows, list):
            issues.append(Issue(str(path), "/records", "records must be an array"))
            continue
        for index, record in enumerate(candidate_rows):
            if not isinstance(record, Mapping):
                issues.append(
                    Issue(
                        str(path),
                        f"/records/{index}",
                        "screening record must be an object",
                    )
                )
                continue
            identifier = record.get("candidate_id")
            record_pointer = f"/records/{index}/candidate_id"
            if not isinstance(identifier, str) or not identifier:
                issues.append(
                    Issue(str(path), record_pointer, "candidate_id must be a string")
                )
                continue
            if expected_prefix is not None and not identifier.startswith(
                expected_prefix
            ):
                issues.append(
                    Issue(
                        str(path),
                        record_pointer,
                        f"candidate ID must start with {expected_prefix!r}",
                    )
                )
            existing = records.get(identifier)
            if existing is not None:
                issues.append(
                    Issue(
                        str(path),
                        record_pointer,
                        f"duplicate screening record ID {identifier!r}; first "
                        f"defined at {existing.path}{existing.pointer}",
                    )
                )
                continue
            records[identifier] = ScreeningLocation(path, record_pointer, record)
    return records, issues


def load_schemas() -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    resources: list[tuple[str, Resource[Any]]] = []
    for kind, path in SCHEMA_PATHS.items():
        schema = load_object(path)
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id:
            raise ValueError(f"schema has no $id: {path}")
        Draft202012Validator.check_schema(schema)
        schemas[kind] = schema
        resources.append((schema_id, Resource.from_contents(schema)))
    return schemas, Registry().with_resources(resources)


def schema_issues(
    documents: Iterable[Document],
    schemas: Mapping[str, dict[str, Any]],
    registry: Registry,
) -> list[Issue]:
    validators = {
        kind: Draft202012Validator(
            schema,
            registry=registry,
            format_checker=FormatChecker(),
        )
        for kind, schema in schemas.items()
    }
    issues: list[Issue] = []
    for document in documents:
        validator = validators[document.kind]
        for error in sorted(
            validator.iter_errors(document.data),
            key=lambda item: (
                tuple(f"{type(part).__name__}:{part}" for part in item.absolute_path),
                item.message,
            ),
        ):
            error_pointer = ""
            for part in error.absolute_path:
                error_pointer = pointer(error_pointer, part)
            issues.append(
                Issue(str(document.path), error_pointer or "/", error.message)
            )
    return issues


def register(
    indexes: dict[str, dict[str, Location]],
    kind: str,
    identifier: Any,
    document: Document,
    location_pointer: str,
    node: Mapping[str, Any],
    issues: list[Issue],
) -> None:
    if not isinstance(identifier, str) or not identifier:
        return
    existing = indexes.setdefault(kind, {}).get(identifier)
    if existing is not None:
        issues.append(
            Issue(
                str(document.path),
                location_pointer,
                f"duplicate {kind} ID {identifier!r}; first defined at "
                f"{existing.document.path}{existing.pointer}",
            )
        )
        return
    indexes[kind][identifier] = Location(document, location_pointer, node)


def index_report(
    document: Document,
    indexes: dict[str, dict[str, Location]],
    issues: list[Issue],
) -> None:
    data = document.data
    identity = data.get("identity", {})
    if isinstance(identity, Mapping):
        register(
            indexes,
            "report",
            identity.get("report_id"),
            document,
            "/identity/report_id",
            identity,
            issues,
        )

    catalog = data.get("reference_catalog", {})
    if isinstance(catalog, Mapping):
        for table_name, id_name, id_kind in (
            ("entities", "entity_id", "entity"),
            ("quantities", "quantity_id", "quantity"),
            ("decisions", "decision_id", "decision"),
            ("relationships", "relationship_id", "relationship"),
            ("rules", "rule_id", "rule"),
            ("checks", "check_id", "check"),
            ("resources", "resource_id", "resource"),
            ("issues", "issue_id", "issue"),
        ):
            for row_index, row in enumerate(rows(catalog.get(table_name))):
                register(
                    indexes,
                    id_kind,
                    row.get(id_name),
                    document,
                    f"/reference_catalog/{table_name}/{row_index}/{id_name}",
                    row,
                    issues,
                )

    for index, row in enumerate(rows(data.get("citations"))):
        register(
            indexes,
            "citation",
            row.get("citation_id"),
            document,
            f"/citations/{index}/citation_id",
            row,
            issues,
        )

    mbse = data.get("mbse_approach", {})
    if isinstance(mbse, Mapping):
        for index, row in enumerate(rows(mbse.get("model_generation_methods"))):
            method_pointer = f"/mbse_approach/model_generation_methods/{index}"
            register(
                indexes,
                "model_generation_method",
                row.get("model_generation_method_id"),
                document,
                f"{method_pointer}/model_generation_method_id",
                row,
                issues,
            )
            for source_index, source in enumerate(rows(row.get("construction_sources"))):
                register(
                    indexes,
                    "construction_source",
                    source.get("construction_source_id"),
                    document,
                    f"{method_pointer}/construction_sources/{source_index}/"
                    "construction_source_id",
                    source,
                    issues,
                )
            for step_index, step in enumerate(rows(row.get("method_steps"))):
                register(
                    indexes,
                    "method_step",
                    step.get("method_step_id"),
                    document,
                    f"{method_pointer}/method_steps/{step_index}/method_step_id",
                    step,
                    issues,
                )
        for index, row in enumerate(rows(mbse.get("workflows"))):
            workflow_pointer = f"/mbse_approach/workflows/{index}"
            register(
                indexes,
                "workflow",
                row.get("workflow_id"),
                document,
                f"{workflow_pointer}/workflow_id",
                row,
                issues,
            )
            for activity_index, activity in enumerate(
                rows(row.get("workflow_activities"))
            ):
                register(
                    indexes,
                    "workflow_activity",
                    activity.get("workflow_activity_id"),
                    document,
                    f"{workflow_pointer}/workflow_activities/{activity_index}/"
                    "workflow_activity_id",
                    activity,
                    issues,
                )
        for index, row in enumerate(rows(mbse.get("model_artifacts"))):
            register(
                indexes,
                "model_artifact",
                row.get("model_artifact_id"),
                document,
                f"/mbse_approach/model_artifacts/{index}/model_artifact_id",
                row,
                issues,
            )
        for index, row in enumerate(rows(mbse.get("tools_and_versions"))):
            register(
                indexes,
                "tool",
                row.get("tool_id"),
                document,
                f"/mbse_approach/tools_and_versions/{index}/tool_id",
                row,
                issues,
            )

    for case_index, case in enumerate(rows(data.get("eps_cases"))):
        case_pointer = f"/eps_cases/{case_index}"
        register(
            indexes,
            "eps_case",
            case.get("eps_case_id"),
            document,
            f"{case_pointer}/eps_case_id",
            case,
            issues,
        )
        for table_name, id_name, id_kind in (
            ("eps_elements", "eps_element_id", "eps_element"),
            ("eps_requirements", "eps_requirement_id", "eps_requirement"),
            ("eps_exchanges", "eps_exchange_id", "eps_exchange"),
            ("eps_dependencies", "eps_dependency_id", "eps_dependency"),
            (
                "eps_model_representation_relationships",
                "model_representation_relationship_id",
                "model_representation_relationship",
            ),
            ("eps_model_bridges", "eps_model_bridge_id", "eps_model_bridge"),
        ):
            for row_index, row in enumerate(rows(case.get(table_name))):
                register(
                    indexes,
                    id_kind,
                    row.get(id_name),
                    document,
                    f"{case_pointer}/{table_name}/{row_index}/{id_name}",
                    row,
                    issues,
                )
        for representation_index, representation in enumerate(
            rows(case.get("eps_model_representations"))
        ):
            representation_pointer = (
                f"{case_pointer}/eps_model_representations/{representation_index}"
            )
            register(
                indexes,
                "model_representation",
                representation.get("model_representation_id"),
                document,
                f"{representation_pointer}/model_representation_id",
                representation,
                issues,
            )
            for occurrence_index, occurrence in enumerate(
                rows(representation.get("behavior_occurrences"))
            ):
                register(
                    indexes,
                    "behavior_occurrence",
                    occurrence.get("behavior_occurrence_id"),
                    document,
                    f"{representation_pointer}/behavior_occurrences/"
                    f"{occurrence_index}/behavior_occurrence_id",
                    occurrence,
                    issues,
                )
        coverage = case.get("coverage_assessment", {})
        if isinstance(coverage, Mapping):
            for item_index, item in enumerate(rows(coverage.get("coverage_items"))):
                register(
                    indexes,
                    "coverage_item",
                    item.get("coverage_item_id"),
                    document,
                    f"{case_pointer}/coverage_assessment/coverage_items/"
                    f"{item_index}/coverage_item_id",
                    item,
                    issues,
                )

    for table_name, id_name, id_kind in (
        ("implementation_records", "implementation_record_id", "implementation_record"),
        ("input_groups", "input_group_id", "input_group"),
        ("rq1_claims", "rq1_claim_id", "rq1_claim"),
        ("rq2_findings", "rq2_finding_id", "rq2_finding"),
        ("rq3_activities", "rq3_activity_id", "rq3_activity"),
    ):
        for row_index, row in enumerate(rows(data.get(table_name))):
            register(
                indexes,
                id_kind,
                row.get(id_name),
                document,
                f"/{table_name}/{row_index}/{id_name}",
                row,
                issues,
            )
            if table_name == "input_groups":
                for item_index, item in enumerate(rows(row.get("input_items"))):
                    register(
                        indexes,
                        "input_item",
                        item.get("input_item_id"),
                        document,
                        f"/input_groups/{row_index}/input_items/{item_index}/"
                        "input_item_id",
                        item,
                        issues,
                    )

    for set_index, result_set in enumerate(rows(data.get("result_sets"))):
        set_pointer = f"/result_sets/{set_index}"
        register(
            indexes,
            "result_set",
            result_set.get("result_set_id"),
            document,
            f"{set_pointer}/result_set_id",
            result_set,
            issues,
        )
        for table_name, id_name, id_kind in (
            ("evaluation_units", "evaluation_unit_id", "evaluation_unit"),
            ("outputs", "result_output_id", "result_output"),
            ("criteria", "result_criterion_id", "result_criterion"),
            (
                "reviewer_derived_values",
                "reviewer_derived_value_id",
                "reviewer_derived_value",
            ),
        ):
            for row_index, row in enumerate(rows(result_set.get(table_name))):
                register(
                    indexes,
                    id_kind,
                    row.get(id_name),
                    document,
                    f"{set_pointer}/{table_name}/{row_index}/{id_name}",
                    row,
                    issues,
                )
                if table_name == "outputs":
                    for statistic_index, statistic in enumerate(
                        rows(row.get("statistical_evaluations"))
                    ):
                        register(
                            indexes,
                            "statistical_evaluation",
                            statistic.get("statistical_evaluation_id"),
                            document,
                            f"{set_pointer}/outputs/{row_index}/"
                            f"statistical_evaluations/{statistic_index}/"
                            "statistical_evaluation_id",
                            statistic,
                            issues,
                        )
        for comparator_index, comparator in enumerate(
            rows(result_set.get("comparators"))
        ):
            comparator_pointer = f"{set_pointer}/comparators/{comparator_index}"
            register(
                indexes,
                "comparator",
                comparator.get("comparator_id"),
                document,
                f"{comparator_pointer}/comparator_id",
                comparator,
                issues,
            )
            for rival_index, rival in enumerate(
                rows(comparator.get("rival_explanations"))
            ):
                register(
                    indexes,
                    "rival_explanation",
                    rival.get("rival_explanation_id"),
                    document,
                    f"{comparator_pointer}/rival_explanations/{rival_index}/rival_explanation_id",
                    rival,
                    issues,
                )

    reuse = data.get("reuse", {})
    if isinstance(reuse, Mapping):
        for record_index, record in enumerate(rows(reuse.get("report_reuse_records"))):
            record_pointer = f"/reuse/report_reuse_records/{record_index}"
            register(
                indexes,
                "report_reuse_record",
                record.get("report_reuse_record_id"),
                document,
                f"{record_pointer}/report_reuse_record_id",
                record,
                issues,
            )
            for relationship_index, relationship in enumerate(
                rows(record.get("artifact_relationships"))
            ):
                register(
                    indexes,
                    "artifact_relationship",
                    relationship.get("artifact_relationship_id"),
                    document,
                    f"{record_pointer}/artifact_relationships/"
                    f"{relationship_index}/artifact_relationship_id",
                    relationship,
                    issues,
                )
            design = record.get("reuse_design", {})
            if isinstance(design, Mapping):
                for table_name, id_name, id_kind in (
                    ("variation_points", "variation_point_id", "variation_point"),
                    ("tailoring_rules", "tailoring_rule_id", "tailoring_rule"),
                    (
                        "tailoring_procedure_steps",
                        "tailoring_step_id",
                        "tailoring_step",
                    ),
                ):
                    for row_index, design_row in enumerate(rows(design.get(table_name))):
                        register(
                            indexes,
                            id_kind,
                            design_row.get(id_name),
                            document,
                            f"{record_pointer}/reuse_design/{table_name}/"
                            f"{row_index}/{id_name}",
                            design_row,
                            issues,
                        )
        for application_index, application in enumerate(
            rows(reuse.get("report_applications"))
        ):
            application_pointer = f"/reuse/report_applications/{application_index}"
            register(
                indexes,
                "report_application",
                application.get("report_application_id"),
                document,
                f"{application_pointer}/report_application_id",
                application,
                issues,
            )
            tailoring = application.get("tailoring_or_adaptation", {})
            if isinstance(tailoring, Mapping):
                for operation_index, operation in enumerate(
                    rows(tailoring.get("executed_operations"))
                ):
                    register(
                        indexes,
                        "application_operation",
                        operation.get("application_operation_id"),
                        document,
                        f"{application_pointer}/tailoring_or_adaptation/"
                        f"executed_operations/{operation_index}/application_operation_id",
                        operation,
                        issues,
                    )


def build_indexes(
    documents: Iterable[Document],
) -> tuple[dict[str, dict[str, Location]], list[Issue]]:
    index_kinds = (
        "report",
        "citation",
        "entity",
        "quantity",
        "decision",
        "relationship",
        "rule",
        "check",
        "resource",
        "issue",
        "tool",
        "model_generation_method",
        "construction_source",
        "method_step",
        "workflow",
        "workflow_activity",
        "model_artifact",
        "eps_case",
        "eps_element",
        "eps_requirement",
        "eps_exchange",
        "eps_dependency",
        "model_representation",
        "model_representation_relationship",
        "behavior_occurrence",
        "eps_model_bridge",
        "coverage_item",
        "implementation_record",
        "input_group",
        "input_item",
        "result_set",
        "evaluation_unit",
        "result_output",
        "statistical_evaluation",
        "result_criterion",
        "comparator",
        "rival_explanation",
        "reviewer_derived_value",
        "rq1_claim",
        "rq2_finding",
        "rq3_activity",
        "artifact_relationship",
        "variation_point",
        "tailoring_rule",
        "tailoring_step",
        "application_operation",
        "report_reuse_record",
        "report_application",
        "family",
        "lineage",
        "tailoring_application",
        "audit",
    )
    indexes = {kind: {} for kind in index_kinds}
    issues: list[Issue] = []
    for document in documents:
        if document.kind == "report":
            index_report(document, indexes, issues)
        elif document.kind == "family":
            register(
                indexes,
                "family",
                document.data.get("family_id"),
                document,
                "/family_id",
                document.data,
                issues,
            )
        elif document.kind == "lineage":
            register(
                indexes,
                "lineage",
                document.data.get("lineage_id"),
                document,
                "/lineage_id",
                document.data,
                issues,
            )
            for row_index, row in enumerate(
                rows(document.data.get("artifact_relationships"))
            ):
                register(
                    indexes,
                    "artifact_relationship",
                    row.get("artifact_relationship_id"),
                    document,
                    f"/artifact_relationships/{row_index}/artifact_relationship_id",
                    row,
                    issues,
                )
            design = document.data.get("reuse_design", {})
            if isinstance(design, Mapping):
                for table_name, id_name, id_kind in (
                    ("variation_points", "variation_point_id", "variation_point"),
                    ("tailoring_rules", "tailoring_rule_id", "tailoring_rule"),
                    (
                        "tailoring_procedure_steps",
                        "tailoring_step_id",
                        "tailoring_step",
                    ),
                ):
                    for row_index, row in enumerate(rows(design.get(table_name))):
                        register(
                            indexes,
                            id_kind,
                            row.get(id_name),
                            document,
                            f"/reuse_design/{table_name}/{row_index}/{id_name}",
                            row,
                            issues,
                        )
        elif document.kind == "tailoring_application":
            register(
                indexes,
                "tailoring_application",
                document.data.get("tailoring_application_id"),
                document,
                "/tailoring_application_id",
                document.data,
                issues,
            )
            tailoring = document.data.get("tailoring_or_adaptation", {})
            if isinstance(tailoring, Mapping):
                for operation_index, operation in enumerate(
                    rows(tailoring.get("executed_operations"))
                ):
                    register(
                        indexes,
                        "application_operation",
                        operation.get("application_operation_id"),
                        document,
                        "/tailoring_or_adaptation/executed_operations/"
                        f"{operation_index}/application_operation_id",
                        operation,
                        issues,
                    )
        elif document.kind == "audit":
            register(
                indexes,
                "audit",
                document.data.get("audit_id"),
                document,
                "/audit_id",
                document.data,
                issues,
            )
    return indexes, issues


def check_references(
    document: Document,
    location_pointer: str,
    value: Any,
    target_kind: str,
    indexes: Mapping[str, Mapping[str, Location]],
    issues: list[Issue],
) -> None:
    references: list[tuple[str, str]] = []
    if isinstance(value, str):
        references.append((location_pointer, value))
    elif isinstance(value, list):
        references.extend(
            (pointer(location_pointer, index), item)
            for index, item in enumerate(value)
            if isinstance(item, str)
        )
    for reference_pointer, identifier in references:
        if identifier not in indexes[target_kind]:
            issues.append(
                Issue(
                    str(document.path),
                    reference_pointer,
                    f"unresolved {target_kind} ID {identifier!r}",
                )
            )


def check_field_references(
    document: Document,
    base_pointer: str,
    node: Mapping[str, Any],
    specifications: Iterable[tuple[str, str]],
    indexes: Mapping[str, Mapping[str, Location]],
    issues: list[Issue],
) -> None:
    for field, target_kind in specifications:
        if field in node:
            check_references(
                document,
                pointer(base_pointer, field),
                node[field],
                target_kind,
                indexes,
                issues,
            )


def record_reference_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    """Resolve every typed ``record_kind:stable_id`` reference."""

    issues: list[Issue] = []

    def check(
        value: Any,
        value_pointer: str,
        contributing_report_ids: set[str] | None,
    ) -> None:
        if not isinstance(value, str):
            return
        match = RECORD_REFERENCE.fullmatch(value)
        if match is None:
            return
        reference_kind, identifier = match.groups()
        index_kind = RECORD_REFERENCE_KINDS.get(reference_kind)
        location = (
            indexes.get(index_kind, {}).get(identifier)
            if index_kind is not None
            else None
        )
        if location is None:
            issues.append(
                Issue(
                    str(document.path),
                    value_pointer,
                    f"unresolved {reference_kind} record reference {identifier!r}",
                )
            )
            return
        if contributing_report_ids and location.document.kind == "report":
            owner_report_id = report_id(location.document)
            if owner_report_id not in contributing_report_ids:
                issues.append(
                    Issue(
                        str(document.path),
                        value_pointer,
                        f"record reference {value!r} is outside its contributing reports",
                    )
                )

    def walk(
        node: Any,
        base: str,
        reference_context: bool = False,
        inherited_contributing_report_ids: set[str] | None = None,
    ) -> None:
        if isinstance(node, Mapping):
            contributing = node.get("contributing_report_ids")
            active_contributing_report_ids = (
                {item for item in contributing if isinstance(item, str)}
                if isinstance(contributing, list)
                else inherited_contributing_report_ids
            )
            for key, value in node.items():
                child = pointer(base, key)
                direct_kind = DIRECT_REFERENCE_FIELDS.get(key)
                if direct_kind is None:
                    for suffix, inferred_kind in (
                        ("_entity_ids", "entity"),
                        ("_quantity_ids", "quantity"),
                        ("_quantity_id", "quantity"),
                        ("_relationship_ids", "relationship"),
                        ("_rule_ids", "rule"),
                        ("_check_ids", "check"),
                        ("_resource_ids", "resource"),
                        ("_issue_ids", "issue"),
                        ("_decision_ids", "decision"),
                        ("_model_artifact_ids", "model_artifact"),
                    ):
                        if key.endswith(suffix):
                            direct_kind = inferred_kind
                            break
                if direct_kind is not None:
                    direct_value = (
                        value.get("value")
                        if isinstance(value, Mapping) and "value" in value
                        else value
                    )
                    check_references(
                        document,
                        child,
                        direct_value,
                        direct_kind,
                        indexes,
                        issues,
                    )
                is_reference = key in {"source_ref", "target_ref"} or key.endswith(
                    "_refs"
                )
                walk(
                    value,
                    child,
                    is_reference,
                    active_contributing_report_ids,
                )
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(
                    value,
                    pointer(base, index),
                    reference_context,
                    inherited_contributing_report_ids,
                )
        elif reference_context:
            check(node, base, inherited_contributing_report_ids)

    walk(document.data, "")
    return issues


def reuse_design_reference_issues(
    document: Document,
    base: str,
    design: Mapping[str, Any],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for index, variation in enumerate(rows(design.get("variation_points"))):
        check_field_references(
            document,
            f"{base}/variation_points/{index}",
            variation,
            (
                ("linked_report_variation_point_ids", "variation_point"),
                ("linked_model_artifact_ids", "model_artifact"),
                ("linked_model_generation_method_ids", "model_generation_method"),
                ("linked_workflow_ids", "workflow"),
            ),
            indexes,
            issues,
        )
    for index, rule in enumerate(rows(design.get("tailoring_rules"))):
        check_field_references(
            document,
            f"{base}/tailoring_rules/{index}",
            rule,
            (
                ("linked_report_tailoring_rule_ids", "tailoring_rule"),
                ("linked_variation_point_ids", "variation_point"),
            ),
            indexes,
            issues,
        )
    steps = rows(design.get("tailoring_procedure_steps"))
    local_step_ids = {
        step.get("tailoring_step_id")
        for step in steps
        if isinstance(step.get("tailoring_step_id"), str)
    }
    for index, step in enumerate(steps):
        step_base = f"{base}/tailoring_procedure_steps/{index}"
        check_field_references(
            document,
            step_base,
            step,
            (
                ("linked_report_tailoring_step_ids", "tailoring_step"),
                ("linked_variation_point_ids", "variation_point"),
                ("linked_tailoring_rule_ids", "tailoring_rule"),
            ),
            indexes,
            issues,
        )
        predecessors = step.get("predecessor_tailoring_step_ids")
        if isinstance(predecessors, list):
            for predecessor_index, identifier in enumerate(predecessors):
                if identifier not in local_step_ids:
                    issues.append(
                        Issue(
                            str(document.path),
                            f"{step_base}/predecessor_tailoring_step_ids/"
                            f"{predecessor_index}",
                            f"tailoring step ID {identifier!r} is not in the same "
                            "reuse design",
                        )
                    )
    return issues


def tailoring_adaptation_reference_issues(
    document: Document,
    base: str,
    tailoring: Mapping[str, Any],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    check_field_references(
        document,
        base,
        tailoring,
        (
            ("linked_variation_point_ids", "variation_point"),
            ("linked_tailoring_rule_ids", "tailoring_rule"),
            ("linked_tailoring_step_ids", "tailoring_step"),
            ("linked_implementation_record_ids", "implementation_record"),
        ),
        indexes,
        issues,
    )
    operations = rows(tailoring.get("executed_operations"))
    local_operation_ids = {
        operation.get("application_operation_id")
        for operation in operations
        if isinstance(operation.get("application_operation_id"), str)
    }
    for index, operation in enumerate(operations):
        operation_base = f"{base}/executed_operations/{index}"
        check_field_references(
            document,
            operation_base,
            operation,
            (
                (
                    "linked_report_application_operation_ids",
                    "application_operation",
                ),
                ("linked_variation_point_ids", "variation_point"),
                ("linked_tailoring_rule_ids", "tailoring_rule"),
                ("linked_tailoring_step_ids", "tailoring_step"),
            ),
            indexes,
            issues,
        )
        predecessors = operation.get("predecessor_application_operation_ids")
        if isinstance(predecessors, list):
            for predecessor_index, identifier in enumerate(predecessors):
                if identifier not in local_operation_ids:
                    issues.append(
                        Issue(
                            str(document.path),
                            f"{operation_base}/predecessor_application_operation_ids/"
                            f"{predecessor_index}",
                            f"application operation ID {identifier!r} is not in the "
                            "same application",
                        )
                    )
    return issues


def application_assurance_trace_issues(
    document: Document,
    base: str,
    application: Mapping[str, Any],
    indexes: Mapping[str, Mapping[str, Location]],
    *,
    same_report: bool,
) -> list[Issue]:
    """Link post-tailoring assurance to the exact artifact and configuration."""

    application_object = coded_value(application.get("application_object"))
    result = application.get("result_and_assurance", {})
    if (
        application_object not in ARTIFACT_APPLICATION_OBJECTS
        or not isinstance(result, Mapping)
    ):
        return []

    assurance_ids = result.get("assurance_rq3_activity_ids")
    if not isinstance(assurance_ids, list):
        return []

    resulting_artifact_ids = result.get("resulting_model_artifact_ids")
    configuration_ids = result.get("configuration_entity_ids")
    issues: list[Issue] = []
    for assurance_index, activity_id in enumerate(assurance_ids):
        location = indexes["rq3_activity"].get(activity_id)
        if location is None:
            continue
        issue_pointer = (
            f"{base}/result_and_assurance/"
            f"assurance_rq3_activity_ids/{assurance_index}"
        )
        if same_report and location.document is not document:
            issues.append(
                Issue(
                    str(document.path),
                    issue_pointer,
                    "report-level assurance activity belongs to another report",
                )
            )
            continue

        activity_artifact_ids = location.node.get("linked_model_artifact_ids")
        if (
            isinstance(resulting_artifact_ids, list)
            and resulting_artifact_ids
            and not (
                isinstance(activity_artifact_ids, list)
                and set(resulting_artifact_ids) & set(activity_artifact_ids)
            )
        ):
            issues.append(
                Issue(
                    str(document.path),
                    issue_pointer,
                    "post-tailoring assurance activity does not link the resulting "
                    "model artifact",
                )
            )

        activity_configuration_ids = location.node.get(
            "linked_configuration_entity_ids"
        )
        if (
            isinstance(configuration_ids, list)
            and configuration_ids
            and not (
                isinstance(activity_configuration_ids, list)
                and set(configuration_ids) & set(activity_configuration_ids)
            )
        ):
            issues.append(
                Issue(
                    str(document.path),
                    issue_pointer,
                    "post-tailoring assurance activity does not link the resulting "
                    "model configuration",
                )
            )
    return issues


def report_reference_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues = record_reference_issues(document, indexes)
    data = document.data
    workflow_activity_parent_ids: dict[str, str] = {}
    mbse = data.get("mbse_approach", {})
    if isinstance(mbse, Mapping):
        for index, row in enumerate(rows(mbse.get("model_generation_methods"))):
            method_base = f"/mbse_approach/model_generation_methods/{index}"
            check_field_references(
                document,
                method_base,
                row,
                (
                    ("eps_case_ids", "eps_case"),
                    ("linked_input_group_ids", "input_group"),
                    ("linked_source_model_artifact_ids", "model_artifact"),
                    ("linked_output_model_artifact_ids", "model_artifact"),
                ),
                indexes,
                issues,
            )
            for source_index, source in enumerate(rows(row.get("construction_sources"))):
                check_field_references(
                    document,
                    f"{method_base}/construction_sources/{source_index}",
                    source,
                    (
                        ("linked_input_group_ids", "input_group"),
                        ("linked_model_artifact_ids", "model_artifact"),
                    ),
                    indexes,
                    issues,
                )
            method_steps = rows(row.get("method_steps"))
            local_step_ids = {
                step.get("method_step_id")
                for step in method_steps
                if isinstance(step.get("method_step_id"), str)
            }
            for step_index, step in enumerate(method_steps):
                step_base = f"{method_base}/method_steps/{step_index}"
                check_field_references(
                    document,
                    step_base,
                    step,
                    (
                        ("linked_input_group_ids", "input_group"),
                        ("linked_model_artifact_ids", "model_artifact"),
                    ),
                    indexes,
                    issues,
                )
                predecessors = step.get("predecessor_method_step_ids")
                if isinstance(predecessors, list):
                    for predecessor_index, identifier in enumerate(predecessors):
                        if identifier not in local_step_ids:
                            issues.append(
                                Issue(
                                    str(document.path),
                                    f"{step_base}/predecessor_method_step_ids/"
                                    f"{predecessor_index}",
                                    f"method step ID {identifier!r} is not in the "
                                    "same method",
                                )
                            )
        for index, workflow in enumerate(rows(mbse.get("workflows"))):
            workflow_base = f"/mbse_approach/workflows/{index}"
            check_field_references(
                document,
                workflow_base,
                workflow,
                (
                    ("eps_case_ids", "eps_case"),
                    ("linked_model_generation_method_ids", "model_generation_method"),
                    ("linked_model_artifact_ids", "model_artifact"),
                ),
                indexes,
                issues,
            )
            activities = rows(workflow.get("workflow_activities"))
            local_activity_ids = {
                activity.get("workflow_activity_id")
                for activity in activities
                if isinstance(activity.get("workflow_activity_id"), str)
            }
            workflow_id = row.get("workflow_id")
            for activity_index, activity in enumerate(activities):
                activity_base = (
                    f"{workflow_base}/workflow_activities/{activity_index}"
                )
                workflow_activity_id = activity.get("workflow_activity_id")
                if isinstance(workflow_id, str) and isinstance(
                    workflow_activity_id, str
                ):
                    workflow_activity_parent_ids[workflow_activity_id] = workflow_id
                check_field_references(
                    document,
                    activity_base,
                    activity,
                    (
                        (
                            "linked_model_generation_method_ids",
                            "model_generation_method",
                        ),
                        ("linked_model_artifact_ids", "model_artifact"),
                    ),
                    indexes,
                    issues,
                )
                predecessors = activity.get("predecessor_workflow_activity_ids")
                if isinstance(predecessors, list):
                    for predecessor_index, identifier in enumerate(predecessors):
                        if identifier not in local_activity_ids:
                            issues.append(
                                Issue(
                                    str(document.path),
                                    f"{activity_base}/predecessor_workflow_activity_ids/"
                                    f"{predecessor_index}",
                                    f"workflow activity ID {identifier!r} is not in "
                                    "the same workflow",
                                )
                            )

    for case_index, case in enumerate(rows(data.get("eps_cases"))):
        case_pointer = f"/eps_cases/{case_index}"
        local_exchange_ids = {
            row.get("eps_exchange_id")
            for row in rows(case.get("eps_exchanges"))
            if isinstance(row.get("eps_exchange_id"), str)
        }
        for dependency_index, dependency in enumerate(
            rows(case.get("eps_dependencies"))
        ):
            field = dependency.get("linked_eps_exchange_ids")
            if isinstance(field, list):
                for link_index, identifier in enumerate(field):
                    if identifier not in local_exchange_ids:
                        issues.append(
                            Issue(
                                str(document.path),
                                f"{case_pointer}/eps_dependencies/{dependency_index}/"
                                f"linked_eps_exchange_ids/{link_index}",
                                f"EPS exchange ID {identifier!r} is not in the same EPS case",
                            )
                        )

    reuse = data.get("reuse", {})
    common_specs = {
        "implementation_records": (
            ("linked_workflow_ids", "workflow"),
        ),
        "input_groups": (
            ("eps_case_id", "eps_case"),
            ("linked_model_generation_method_ids", "model_generation_method"),
            ("linked_workflow_ids", "workflow"),
            ("linked_report_reuse_record_ids", "report_reuse_record"),
            ("linked_result_output_ids", "result_output"),
            ("linked_result_criterion_ids", "result_criterion"),
            ("linked_rq3_activity_ids", "rq3_activity"),
            ("linked_report_application_ids", "report_application"),
        ),
        "rq1_claims": (
            ("linked_model_artifact_ids", "model_artifact"),
            ("linked_model_generation_method_ids", "model_generation_method"),
            ("linked_workflow_ids", "workflow"),
            ("linked_eps_case_ids", "eps_case"),
            ("linked_report_reuse_record_ids", "report_reuse_record"),
            ("linked_result_set_ids", "result_set"),
            ("linked_result_output_ids", "result_output"),
            ("linked_result_criterion_ids", "result_criterion"),
            ("linked_comparator_ids", "comparator"),
            ("linked_implementation_record_ids", "implementation_record"),
        ),
        "rq2_findings": (
            ("linked_model_artifact_ids", "model_artifact"),
            ("linked_model_generation_method_ids", "model_generation_method"),
            ("linked_workflow_ids", "workflow"),
            ("linked_rq3_activity_ids", "rq3_activity"),
            ("linked_input_group_ids", "input_group"),
            ("linked_result_set_ids", "result_set"),
            ("linked_result_output_ids", "result_output"),
            ("linked_result_criterion_ids", "result_criterion"),
            ("linked_comparator_ids", "comparator"),
            ("linked_report_reuse_record_ids", "report_reuse_record"),
            ("linked_implementation_record_ids", "implementation_record"),
        ),
        "rq3_activities": (
            ("linked_model_artifact_ids", "model_artifact"),
            ("linked_workflow_ids", "workflow"),
            ("linked_workflow_activity_ids", "workflow_activity"),
            ("linked_configuration_entity_ids", "entity"),
            ("linked_coverage_item_ids", "coverage_item"),
            ("predecessor_rq3_activity_ids", "rq3_activity"),
            ("linked_result_set_ids", "result_set"),
            ("linked_result_criterion_ids", "result_criterion"),
            ("linked_result_output_ids", "result_output"),
            ("linked_comparator_ids", "comparator"),
        ),
    }
    for table_name, specifications in common_specs.items():
        for row_index, row in enumerate(rows(data.get(table_name))):
            check_field_references(
                document,
                f"/{table_name}/{row_index}",
                row,
                specifications,
                indexes,
                issues,
            )

    rq3_rows = rows(data.get("rq3_activities"))
    local_rq3_ids = {
        activity.get("rq3_activity_id")
        for activity in rq3_rows
        if isinstance(activity.get("rq3_activity_id"), str)
    }
    for activity_index, activity in enumerate(rq3_rows):
        linked_workflow_ids = activity.get("linked_workflow_ids")
        linked_workflow_id_set = (
            set(linked_workflow_ids)
            if isinstance(linked_workflow_ids, list)
            else set()
        )
        linked_workflow_activity_ids = activity.get("linked_workflow_activity_ids")
        if isinstance(linked_workflow_activity_ids, list):
            for workflow_activity_index, workflow_activity_id in enumerate(
                linked_workflow_activity_ids
            ):
                parent_id = workflow_activity_parent_ids.get(workflow_activity_id)
                if parent_id is not None and parent_id not in linked_workflow_id_set:
                    issues.append(
                        Issue(
                            str(document.path),
                            f"/rq3_activities/{activity_index}/"
                            f"linked_workflow_activity_ids/{workflow_activity_index}",
                            "RQ3 workflow activity does not belong to a linked workflow",
                        )
                    )

        predecessors = activity.get("predecessor_rq3_activity_ids")
        if not isinstance(predecessors, list):
            continue
        for predecessor_index, identifier in enumerate(predecessors):
            if identifier not in local_rq3_ids:
                issues.append(
                    Issue(
                        str(document.path),
                        f"/rq3_activities/{activity_index}/"
                        f"predecessor_rq3_activity_ids/{predecessor_index}",
                        f"RQ3 activity ID {identifier!r} is not in the same report",
                    )
                )
            elif identifier == activity.get("rq3_activity_id"):
                issues.append(
                    Issue(
                        str(document.path),
                        f"/rq3_activities/{activity_index}/"
                        f"predecessor_rq3_activity_ids/{predecessor_index}",
                        "RQ3 activity cannot precede itself",
                    )
                )

    for set_index, result_set in enumerate(rows(data.get("result_sets"))):
        set_pointer = f"/result_sets/{set_index}"
        check_field_references(
            document,
            set_pointer,
            result_set,
            (
                ("eps_case_id", "eps_case"),
                ("linked_input_group_ids", "input_group"),
            ),
            indexes,
            issues,
        )
        local_output_ids = {
            row.get("result_output_id")
            for row in rows(result_set.get("outputs"))
            if isinstance(row.get("result_output_id"), str)
        }
        for criterion_index, criterion in enumerate(rows(result_set.get("criteria"))):
            field = criterion.get("linked_result_output_ids")
            if isinstance(field, list):
                for link_index, identifier in enumerate(field):
                    if identifier not in local_output_ids:
                        issues.append(
                            Issue(
                                str(document.path),
                                f"{set_pointer}/criteria/{criterion_index}/"
                                f"linked_result_output_ids/{link_index}",
                                f"result output ID {identifier!r} is not in the same result set",
                            )
                        )
        for derived_index, derived in enumerate(
            rows(result_set.get("reviewer_derived_values"))
        ):
            check_field_references(
                document,
                f"{set_pointer}/reviewer_derived_values/{derived_index}",
                derived,
                (
                    ("linked_input_group_ids", "input_group"),
                    ("linked_result_output_ids", "result_output"),
                ),
                indexes,
                issues,
            )

    if isinstance(reuse, Mapping):
        for record_index, record in enumerate(rows(reuse.get("report_reuse_records"))):
            base = f"/reuse/report_reuse_records/{record_index}"
            check_field_references(
                document,
                base,
                record,
                (
                    ("linked_model_artifact_ids", "model_artifact"),
                    ("linked_model_generation_method_ids", "model_generation_method"),
                    ("linked_workflow_ids", "workflow"),
                ),
                indexes,
                issues,
            )
            design = record.get("reuse_design", {})
            if isinstance(design, Mapping):
                issues.extend(
                    reuse_design_reference_issues(
                        document,
                        f"{base}/reuse_design",
                        design,
                        indexes,
                    )
                )
            assessment = record.get("reuse_assessment", {})
            if isinstance(assessment, Mapping):
                check_field_references(
                    document,
                    f"{base}/reuse_assessment",
                    assessment,
                    (("linked_report_application_ids", "report_application"),),
                    indexes,
                    issues,
                )
            lineage_id = record.get("lineage_id")
            if isinstance(lineage_id, str) and lineage_id not in LINEAGE_SENTINELS:
                check_references(
                    document,
                    f"{base}/lineage_id",
                    lineage_id,
                    "lineage",
                    indexes,
                    issues,
                )
        for application_index, application in enumerate(
            rows(reuse.get("report_applications"))
        ):
            base = f"/reuse/report_applications/{application_index}"
            check_field_references(
                document,
                base,
                application,
                (
                    ("linked_report_reuse_record_ids", "report_reuse_record"),
                    ("linked_model_generation_method_ids", "model_generation_method"),
                    ("linked_workflow_ids", "workflow"),
                ),
                indexes,
                issues,
            )
            lineage_id = application.get("lineage_id")
            if isinstance(lineage_id, str) and lineage_id not in LINEAGE_SENTINELS:
                check_references(
                    document,
                    f"{base}/lineage_id",
                    lineage_id,
                    "lineage",
                    indexes,
                    issues,
                )
            setting = application.get("setting", {})
            tailoring = application.get("tailoring_or_adaptation", {})
            result = application.get("result_and_assurance", {})
            if isinstance(setting, Mapping):
                check_field_references(
                    document,
                    f"{base}/setting",
                    setting,
                    (("linked_eps_case_ids", "eps_case"),),
                    indexes,
                    issues,
                )
            if isinstance(tailoring, Mapping):
                issues.extend(
                    tailoring_adaptation_reference_issues(
                        document,
                        f"{base}/tailoring_or_adaptation",
                        tailoring,
                        indexes,
                    )
                )
            if isinstance(result, Mapping):
                check_field_references(
                    document,
                    f"{base}/result_and_assurance",
                    result,
                    (
                        ("linked_result_set_ids", "result_set"),
                        ("linked_rq2_finding_ids", "rq2_finding"),
                        ("linked_rq3_activity_ids", "rq3_activity"),
                    ),
                    indexes,
                    issues,
                )
                issues.extend(
                    application_assurance_trace_issues(
                        document,
                        base,
                        application,
                        indexes,
                        same_report=True,
                    )
                )

    profile = data.get("procedural_evidence_profile", {})
    if isinstance(profile, Mapping):
        allowed_profile_kinds = {
            "generic_or_reference_model_reported": {"report_reuse_record"},
            "actionable_model_construction_procedure_reported": {
                "model_generation_method",
                "model_artifact",
                "report_reuse_record",
            },
            "actionable_tailoring_procedure_reported": {"report_reuse_record"},
            "worked_tailoring_example_reported": {"report_application"},
            "post_tailoring_assurance_reported": {"report_application"},
            "generic_model_with_actionable_construction_or_tailoring": {
                "model_generation_method",
                "model_artifact",
                "report_reuse_record",
            },
        }
        for field, allowed_kinds in allowed_profile_kinds.items():
            flag = profile.get(field, {})
            if not isinstance(flag, Mapping):
                continue
            for index, identifier in enumerate(flag.get("basis_ids", [])):
                if not isinstance(identifier, str):
                    continue
                if not any(identifier in indexes[kind] for kind in allowed_kinds):
                    issues.append(
                        Issue(
                            str(document.path),
                            f"/procedural_evidence_profile/{field}/basis_ids/{index}",
                            f"unresolved or ineligible profile basis ID {identifier!r}",
                        )
                    )
    return issues


def cross_record_reference_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues = record_reference_issues(document, indexes)
    data = document.data
    if document.kind == "family":
        check_field_references(
            document,
            "",
            data,
            (("linked_report_ids", "report"),),
            indexes,
            issues,
        )
    elif document.kind == "lineage":
        check_field_references(
            document,
            "",
            data,
            (
                ("linked_report_reuse_record_ids", "report_reuse_record"),
                ("linked_report_ids", "report"),
                ("linked_family_ids", "family"),
            ),
            indexes,
            issues,
        )
        design = data.get("reuse_design", {})
        if isinstance(design, Mapping):
            issues.extend(
                reuse_design_reference_issues(
                    document,
                    "/reuse_design",
                    design,
                    indexes,
                )
            )
        assessment = data.get("reuse_assessment", {})
        if isinstance(assessment, Mapping):
            check_field_references(
                document,
                "/reuse_assessment",
                assessment,
                (("linked_tailoring_application_ids", "tailoring_application"),),
                indexes,
                issues,
            )
    elif document.kind == "tailoring_application":
        check_field_references(
            document,
            "",
            data,
            (
                ("lineage_id", "lineage"),
                ("linked_report_application_ids", "report_application"),
                ("linked_model_generation_method_ids", "model_generation_method"),
                ("linked_workflow_ids", "workflow"),
                ("linked_report_ids", "report"),
                ("linked_family_ids", "family"),
                ("linked_eps_case_ids", "eps_case"),
            ),
            indexes,
            issues,
        )
        tailoring = data.get("tailoring_or_adaptation", {})
        result = data.get("result_and_assurance", {})
        if isinstance(tailoring, Mapping):
            issues.extend(
                tailoring_adaptation_reference_issues(
                    document,
                    "/tailoring_or_adaptation",
                    tailoring,
                    indexes,
                )
            )
        if isinstance(result, Mapping):
            check_field_references(
                document,
                "/result_and_assurance",
                result,
                (
                    ("linked_result_set_ids", "result_set"),
                    ("linked_rq2_finding_ids", "rq2_finding"),
                    ("linked_rq3_activity_ids", "rq3_activity"),
                ),
                indexes,
                issues,
            )
            issues.extend(
                application_assurance_trace_issues(
                    document,
                    "",
                    data,
                    indexes,
                    same_report=False,
                )
            )
    elif document.kind == "audit":
        if "report_id" in data:
            check_references(
                document,
                "/report_id",
                data["report_id"],
                "report",
                indexes,
                issues,
            )
        if "lineage_id" in data:
            check_references(
                document,
                "/lineage_id",
                data["lineage_id"],
                "lineage",
                indexes,
                issues,
            )
    return issues


SOURCE_ONLY_FIELDS = {
    "source_name",
    "source_description",
    "raw_source_value",
    "source_expression",
    "claim_wording",
    "exact_claim_wording",
    "claimed_characteristic",
    "exact_reuse_claim",
    "source_vv_terminology",
    "source_element_type",
    "source_relationship_term",
    "parent_artifact_name",
    "parent_artifact_version",
    "derived_artifact_name",
    "derived_artifact_version",
    "identity_and_derivation_evidence",
}


def normalization_issues(document: Document) -> list[Issue]:
    """Keep source-only escape hatches out of fields used for synthesis."""

    issues: list[Issue] = []

    def walk(node: Any, base: str, field_name: str | None = None) -> None:
        if isinstance(node, Mapping):
            if node.get("normalization_status") == "not_for_synthesis":
                if field_name not in SOURCE_ONLY_FIELDS:
                    issues.append(
                        Issue(
                            str(document.path),
                            pointer(base, "normalization_status"),
                            "not_for_synthesis is not allowed for this analytic field",
                        )
                    )
            for key, value in node.items():
                walk(value, pointer(base, key), key)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, pointer(base, index), field_name)

    walk(document.data, "")
    return issues


def evidence_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    report_id = None
    allowed_report_ids: set[str] = set()
    if document.kind == "report":
        identity = document.data.get("identity", {})
        if isinstance(identity, Mapping) and isinstance(identity.get("report_id"), str):
            report_id = identity["report_id"]
            allowed_report_ids = {report_id}
        for index, citation in enumerate(rows(document.data.get("citations"))):
            if report_id is not None and citation.get("report_id") != report_id:
                issues.append(
                    Issue(
                        str(document.path),
                        f"/citations/{index}/report_id",
                        "citation report_id does not match the containing report",
                    )
                )
    elif document.kind in {"family", "lineage", "tailoring_application"}:
        linked = document.data.get("linked_report_ids")
        if isinstance(linked, list):
            allowed_report_ids = {item for item in linked if isinstance(item, str)}

    def walk(node: Any, base: str, inherited_citations: list[str] | None) -> None:
        if isinstance(node, Mapping):
            own_citations = node.get("citation_ids")
            active_citations = (
                own_citations
                if isinstance(own_citations, list)
                else inherited_citations
            )
            status = node.get("status")
            if (
                isinstance(status, str)
                and status in {"none", "uncertain"}
                and not active_citations
            ):
                issues.append(
                    Issue(
                        str(document.path),
                        base or "/",
                        f"status {status!r} has no citation in its evidence group",
                    )
                )
            contributing = node.get("contributing_report_ids")
            contributing_ids = (
                {item for item in contributing if isinstance(item, str)}
                if isinstance(contributing, list)
                else None
            )
            if contributing_ids is not None:
                for index, identifier in enumerate(contributing):
                    if identifier not in indexes["report"]:
                        issues.append(
                            Issue(
                                str(document.path),
                                pointer(
                                    pointer(base, "contributing_report_ids"), index
                                ),
                                f"unresolved report ID {identifier!r}",
                            )
                        )
                    if allowed_report_ids and identifier not in allowed_report_ids:
                        issues.append(
                            Issue(
                                str(document.path),
                                pointer(
                                    pointer(base, "contributing_report_ids"), index
                                ),
                                f"contributing report {identifier!r} is not linked by the record",
                            )
                        )
            if isinstance(own_citations, list):
                for index, identifier in enumerate(own_citations):
                    location = indexes["citation"].get(identifier)
                    citation_pointer = pointer(pointer(base, "citation_ids"), index)
                    if location is None:
                        issues.append(
                            Issue(
                                str(document.path),
                                citation_pointer,
                                f"unresolved citation ID {identifier!r}",
                            )
                        )
                        continue
                    citation_report = location.node.get("report_id")
                    if allowed_report_ids and citation_report not in allowed_report_ids:
                        issues.append(
                            Issue(
                                str(document.path),
                                citation_pointer,
                                f"citation {identifier!r} belongs to unlinked "
                                f"report {citation_report!r}",
                            )
                        )
                    if (
                        contributing_ids is not None
                        and citation_report not in contributing_ids
                    ):
                        issues.append(
                            Issue(
                                str(document.path),
                                citation_pointer,
                                f"citation {identifier!r} is not from a contributing report",
                            )
                        )
            for key, value in node.items():
                if key in {"citation_ids", "contributing_report_ids"}:
                    continue
                walk(value, pointer(base, key), active_citations)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, pointer(base, index), inherited_citations)

    walk(document.data, "", None)
    return issues


def is_artifact_reuse_record(record: Mapping[str, Any]) -> bool:
    assessment = record.get("reuse_assessment", {})
    if isinstance(assessment, Mapping):
        level = coded_value(assessment.get("report_reuse_level"))
        if isinstance(level, str) and level != "NA":
            return True
    claimed_objects = coded_value(record.get("claimed_reuse_object"))
    return isinstance(claimed_objects, list) and "artifact" in claimed_objects


def first_pass_lineage_issues(
    baseline_reports: Iterable[Document],
) -> list[Issue]:
    issues: list[Issue] = []
    allowed_first_pass_values = {"pending_resolution", "not_applicable"}
    for document in baseline_reports:
        reuse = document.data.get("reuse", {})
        if not isinstance(reuse, Mapping):
            continue
        mentioned = coded_value(reuse.get("lineage_mentioned"))
        records = rows(reuse.get("report_reuse_records"))
        applications = rows(reuse.get("report_applications"))
        pending_paths: list[str] = []
        for index, record in enumerate(records):
            lineage_id = record.get("lineage_id")
            value_pointer = f"/reuse/report_reuse_records/{index}/lineage_id"
            if lineage_id == "pending_resolution":
                pending_paths.append(value_pointer)
            if lineage_id not in allowed_first_pass_values:
                issues.append(
                    Issue(
                        str(document.path),
                        value_pointer,
                        f"first-pass lineage_id has disallowed value {lineage_id!r}",
                    )
                )
            if not is_artifact_reuse_record(record) and lineage_id != "not_applicable":
                issues.append(
                    Issue(
                        str(document.path),
                        value_pointer,
                        "reuse record without an artifact must use not_applicable lineage_id",
                    )
                )
        for index, application in enumerate(applications):
            lineage_id = application.get("lineage_id")
            value_pointer = f"/reuse/report_applications/{index}/lineage_id"
            if lineage_id == "pending_resolution":
                pending_paths.append(value_pointer)
            if lineage_id not in allowed_first_pass_values:
                issues.append(
                    Issue(
                        str(document.path),
                        value_pointer,
                        f"first-pass lineage_id has disallowed value {lineage_id!r}",
                    )
                )

        if mentioned in {"yes", "uncertain"} and not pending_paths:
            issues.append(
                Issue(
                    str(document.path),
                    "/reuse/lineage_mentioned/value",
                    f"lineage_mentioned {mentioned!r} has no pending lineage record",
                )
            )
        if mentioned == "no" and pending_paths:
            issues.append(
                Issue(
                    str(document.path),
                    "/reuse/lineage_mentioned/value",
                    "lineage_mentioned 'no' has pending lineage IDs",
                )
            )
    return issues


def report_application_lineage_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    reuse = document.data.get("reuse", {})
    if not isinstance(reuse, Mapping):
        return issues
    for index, application in enumerate(rows(reuse.get("report_applications"))):
        application_object = coded_value(application.get("application_object"))
        has_artifact = application_object in ARTIFACT_APPLICATION_OBJECTS
        method_ids = application.get("linked_model_generation_method_ids")
        workflow_ids = application.get("linked_workflow_ids")
        has_method = isinstance(method_ids, list) and bool(method_ids)
        has_workflow = isinstance(workflow_ids, list) and bool(workflow_ids)
        expected_object = application_object_for(
            has_artifact,
            has_method,
            has_workflow,
            application_object,
        )
        if application_object != "unclear" and application_object != expected_object:
            issues.append(
                Issue(
                    str(document.path),
                    f"/reuse/report_applications/{index}/application_object/value",
                    "application object does not match its method and workflow links",
                )
            )
        if not has_artifact:
            if application.get("lineage_id") != "not_applicable":
                issues.append(
                    Issue(
                        str(document.path),
                        f"/reuse/report_applications/{index}/lineage_id",
                        "application without an artifact must use not_applicable "
                        "lineage_id",
                    )
                )
            continue
        linked_records = linked_locations(
            application.get("linked_report_reuse_record_ids"),
            indexes["report_reuse_record"],
            containing_report=document,
        )
        artifact_records = [
            location.node
            for location in linked_records
            if is_artifact_reuse_record(location.node)
        ]
        value_pointer = f"/reuse/report_applications/{index}/lineage_id"
        if not artifact_records:
            issues.append(
                Issue(
                    str(document.path),
                    value_pointer,
                    "artifact application has no linked artifact reuse record",
                )
            )
            continue
        inherited = {record.get("lineage_id") for record in artifact_records}
        if len(inherited) != 1 or application.get("lineage_id") not in inherited:
            issues.append(
                Issue(
                    str(document.path),
                    value_pointer,
                    "application lineage_id does not match its linked artifact reuse record",
                )
            )
    return issues


def lineage_consistency_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        if document.kind == "lineage":
            lineage_id = document.data.get("lineage_id")
            linked_reuse_ids = document.data.get("linked_report_reuse_record_ids", [])
            linked_report_ids = document.data.get("linked_report_ids", [])
            if not isinstance(linked_reuse_ids, list):
                linked_reuse_ids = []
            derived_report_ids: set[str] = set()
            for index, reuse_id in enumerate(linked_reuse_ids):
                location = indexes["report_reuse_record"].get(reuse_id)
                if location is None:
                    continue
                containing_report_id = report_id(location.document)
                if containing_report_id is not None:
                    derived_report_ids.add(containing_report_id)
                if location.node.get("lineage_id") != lineage_id:
                    issues.append(
                        Issue(
                            str(document.path),
                            f"/linked_report_reuse_record_ids/{index}",
                            f"report reuse record {reuse_id!r} does not carry "
                            f"lineage_id {lineage_id!r}",
                        )
                    )
            if isinstance(linked_report_ids, list) and (
                set(linked_report_ids) != derived_report_ids
            ):
                issues.append(
                    Issue(
                        str(document.path),
                        "/linked_report_ids",
                        "linked report IDs do not equal the reports contributing "
                        "linked reuse records",
                    )
                )
        elif document.kind == "tailoring_application":
            lineage_id = document.data.get("lineage_id")
            for index, report_application_id in enumerate(
                document.data.get("linked_report_application_ids", [])
            ):
                location = indexes["report_application"].get(report_application_id)
                if (
                    location is not None
                    and location.node.get("lineage_id") != lineage_id
                ):
                    issues.append(
                        Issue(
                            str(document.path),
                            f"/linked_report_application_ids/{index}",
                            f"report application {report_application_id!r} does not "
                            f"carry lineage_id {lineage_id!r}",
                        )
                    )

    for reuse_id, location in indexes["report_reuse_record"].items():
        lineage_id = location.node.get("lineage_id")
        if not isinstance(lineage_id, str) or lineage_id in LINEAGE_SENTINELS:
            continue
        lineage = indexes["lineage"].get(lineage_id)
        if lineage is None:
            continue
        linked_reuse_ids = lineage.node.get("linked_report_reuse_record_ids", [])
        if not isinstance(linked_reuse_ids, list) or reuse_id not in linked_reuse_ids:
            issues.append(
                Issue(
                    str(location.document.path),
                    location.pointer.rsplit("/", 1)[0] + "/lineage_id",
                    f"resolved lineage {lineage_id!r} does not link back to reuse "
                    f"record {reuse_id!r}",
                )
            )
    return issues


def consolidation_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    memberships: dict[str, list[Document]] = {}
    consolidated_documents = [
        document for document in documents if document.kind == "tailoring_application"
    ]
    for document in consolidated_documents:
        linked_application_ids = document.data.get("linked_report_application_ids", [])
        if not isinstance(linked_application_ids, list):
            continue
        expected_report_ids: set[str] = set()
        expected_eps_case_ids: set[str] = set()
        expected_method_ids: set[str] = set()
        expected_workflow_ids: set[str] = set()
        for index, identifier in enumerate(linked_application_ids):
            if not isinstance(identifier, str):
                continue
            memberships.setdefault(identifier, []).append(document)
            location = indexes["report_application"].get(identifier)
            if location is None:
                continue
            application_object = coded_value(location.node.get("application_object"))
            if application_object not in ARTIFACT_APPLICATION_OBJECTS:
                issues.append(
                    Issue(
                        str(document.path),
                        f"/linked_report_application_ids/{index}",
                        f"consolidated application links ineligible "
                        f"{application_object!r} application {identifier!r}",
                    )
                )
            containing_report_id = report_id(location.document)
            if containing_report_id is not None:
                expected_report_ids.add(containing_report_id)
            method_ids = location.node.get("linked_model_generation_method_ids", [])
            if isinstance(method_ids, list):
                expected_method_ids.update(
                    item for item in method_ids if isinstance(item, str)
                )
            workflow_ids = location.node.get("linked_workflow_ids", [])
            if isinstance(workflow_ids, list):
                expected_workflow_ids.update(
                    item for item in workflow_ids if isinstance(item, str)
                )
            setting = location.node.get("setting", {})
            if isinstance(setting, Mapping):
                linked_eps_case_ids = setting.get("linked_eps_case_ids", [])
                if isinstance(linked_eps_case_ids, list):
                    expected_eps_case_ids.update(
                        item for item in linked_eps_case_ids if isinstance(item, str)
                    )

        linked_report_ids = document.data.get("linked_report_ids", [])
        if isinstance(linked_report_ids, list) and (
            set(linked_report_ids) != expected_report_ids
        ):
            issues.append(
                Issue(
                    str(document.path),
                    "/linked_report_ids",
                    "linked report IDs do not equal the contributing report "
                    "application union",
                )
            )
        linked_eps_case_ids = document.data.get("linked_eps_case_ids", [])
        if isinstance(linked_eps_case_ids, list) and (
            set(linked_eps_case_ids) != expected_eps_case_ids
        ):
            issues.append(
                Issue(
                    str(document.path),
                    "/linked_eps_case_ids",
                    "linked EPS case IDs do not equal the contributing report "
                    "application union",
                )
            )
        linked_method_ids = document.data.get("linked_model_generation_method_ids")
        if isinstance(linked_method_ids, list) and (
            set(linked_method_ids) != expected_method_ids
        ):
            issues.append(
                Issue(
                    str(document.path),
                    "/linked_model_generation_method_ids",
                    "linked method IDs do not equal the contributing report "
                    "application union",
                )
            )
        linked_workflow_ids = document.data.get("linked_workflow_ids")
        if isinstance(linked_workflow_ids, list) and (
            set(linked_workflow_ids) != expected_workflow_ids
        ):
            issues.append(
                Issue(
                    str(document.path),
                    "/linked_workflow_ids",
                    "linked workflow IDs do not equal the contributing report "
                    "application union",
                )
            )
        expected_object = application_object_for(
            True,
            bool(expected_method_ids),
            bool(expected_workflow_ids),
        )
        if coded_value(document.data.get("application_object")) != expected_object:
            issues.append(
                Issue(
                    str(document.path),
                    "/application_object/value",
                    "application object does not match the contributing method and "
                    "workflow links",
                )
            )

    for identifier, location in indexes["report_application"].items():
        application_object = coded_value(location.node.get("application_object"))
        lineage_id = location.node.get("lineage_id")
        count = len(memberships.get(identifier, []))
        if (
            application_object in ARTIFACT_APPLICATION_OBJECTS
            and isinstance(lineage_id, str)
            and lineage_id not in LINEAGE_SENTINELS
            and count != 1
        ):
            issues.append(
                Issue(
                    str(location.document.path),
                    location.pointer,
                    f"resolved artifact application {identifier!r} appears in "
                    f"{count} consolidated applications; exactly one is required",
                )
            )
        if application_object in NON_ARTIFACT_APPLICATION_OBJECTS and count:
            issues.append(
                Issue(
                    str(location.document.path),
                    location.pointer,
                    f"application without an artifact {identifier!r} appears in a "
                    "consolidated artifact application",
                )
            )
    return issues


def audit_coverage_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    complete_report_audits: set[str] = set()
    complete_lineage_audits: set[str] = set()
    for document in documents:
        if (
            document.kind != "audit"
            or document.data.get("audit_completion_status") != "complete"
        ):
            continue
        report_identifier = document.data.get("report_id")
        lineage_identifier = document.data.get("lineage_id")
        if isinstance(report_identifier, str):
            complete_report_audits.add(report_identifier)
        if isinstance(lineage_identifier, str):
            complete_lineage_audits.add(lineage_identifier)

    for identifier, location in indexes["report"].items():
        if identifier not in complete_report_audits:
            issues.append(
                Issue(
                    str(location.document.path),
                    "/identity/report_id",
                    f"report {identifier!r} has no completed focused audit",
                )
            )
    for identifier, location in indexes["lineage"].items():
        assessment = location.node.get("reuse_assessment", {})
        level = (
            coded_value(assessment.get("lineage_reuse_level"))
            if isinstance(assessment, Mapping)
            else None
        )
        if (
            level
            in {
                "R3_reuse_demonstrated",
                "R4_independent_reuse_demonstrated",
            }
            and identifier not in complete_lineage_audits
        ):
            issues.append(
                Issue(
                    str(location.document.path),
                    "/lineage_id",
                    f"{level} lineage {identifier!r} has no completed focused audit",
                )
            )
    return issues


def family_consistency_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    family_documents = [document for document in documents if document.kind == "family"]
    if not family_documents:
        return issues

    memberships: dict[str, list[str]] = {}
    for family in family_documents:
        family_id = family.data.get("family_id")
        linked_report_ids = family.data.get("linked_report_ids", [])
        if not isinstance(family_id, str) or not isinstance(linked_report_ids, list):
            continue
        for linked_report_id in linked_report_ids:
            if isinstance(linked_report_id, str):
                memberships.setdefault(linked_report_id, []).append(family_id)

    for identifier, location in indexes["report"].items():
        containing_families = memberships.get(identifier, [])
        if len(containing_families) != 1:
            issues.append(
                Issue(
                    str(location.document.path),
                    "/identity/report_id",
                    f"report {identifier!r} belongs to {len(containing_families)} "
                    "families; exactly one is required",
                )
            )

    for document in documents:
        if document.kind not in {"lineage", "tailoring_application"}:
            continue
        linked_report_ids = document.data.get("linked_report_ids", [])
        linked_family_ids = document.data.get("linked_family_ids", [])
        if not isinstance(linked_report_ids, list) or not isinstance(
            linked_family_ids, list
        ):
            continue
        expected = {
            family_id
            for linked_report_id in linked_report_ids
            for family_id in memberships.get(linked_report_id, [])
        }
        if set(linked_family_ids) != expected:
            issues.append(
                Issue(
                    str(document.path),
                    "/linked_family_ids",
                    "linked family IDs do not equal the families of linked reports",
                )
            )
    return issues


def screening_record_issues(
    report_documents: Iterable[Document],
    screening_records: Mapping[str, ScreeningLocation],
) -> list[Issue]:
    issues: list[Issue] = []
    for document in report_documents:
        identity = document.data.get("identity", {})
        if not isinstance(identity, Mapping):
            continue
        identifier = identity.get("screening_record_id")
        if not isinstance(identifier, str):
            continue
        location = screening_records.get(identifier)
        if location is None:
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/screening_record_id",
                    f"unresolved screening record ID {identifier!r}",
                )
            )
            continue
        decision = location.record.get("screening_decision")
        if decision not in {
            "include_route_A_eps_primary",
            "include_route_B_embedded_eps",
        }:
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/screening_record_id",
                    f"linked screening record has non-inclusion decision {decision!r}",
                )
            )
    return issues


def report_source_file_issues(document: Document) -> list[Issue]:
    issues: list[Issue] = []
    identity = document.data.get("identity", {})
    if not isinstance(identity, Mapping):
        return issues
    source_file_path = identity.get("source_file_path")
    if not isinstance(source_file_path, str):
        return issues
    path = Path(source_file_path)
    resolved = path if path.is_absolute() else REPOSITORY_ROOT / path
    if not resolved.is_file():
        issues.append(
            Issue(
                str(document.path),
                "/identity/source_file_path",
                f"source file does not resolve to a file: {source_file_path}",
            )
        )
    return issues


def reviewer_derived_script_issues(document: Document) -> list[Issue]:
    issues: list[Issue] = []
    for set_index, result_set in enumerate(rows(document.data.get("result_sets"))):
        for value_index, derived in enumerate(
            rows(result_set.get("reviewer_derived_values"))
        ):
            script_path = derived.get("analysis_script_path")
            if not isinstance(script_path, str):
                continue
            path = Path(script_path)
            resolved = path if path.is_absolute() else REPOSITORY_ROOT / path
            if not resolved.is_file():
                issues.append(
                    Issue(
                        str(document.path),
                        f"/result_sets/{set_index}/reviewer_derived_values/"
                        f"{value_index}/analysis_script_path",
                        f"analysis script does not resolve to a regular file: "
                        f"{script_path}",
                    )
                )
    return issues


def source_text_values(value: Any) -> list[str]:
    ordinary = coded_value(value)
    if not isinstance(ordinary, list):
        return []
    result: list[str] = []
    for item in ordinary:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, Mapping) and isinstance(item.get("source_text"), str):
            result.append(item["source_text"])
    return result


def family_lead_issues(document: Document) -> list[Issue]:
    issues: list[Issue] = []
    identity = document.data.get("identity", {})
    reuse = document.data.get("reuse", {})
    if not isinstance(identity, Mapping) or not isinstance(reuse, Mapping):
        return issues

    expected: set[str] = set()
    for record in rows(reuse.get("report_reuse_records")):
        expected.update(
            source_text_values(record.get("possible_related_reports_or_artifacts"))
        )

    recorded_field = identity.get(
        "possible_companion_reports_or_shared_implementations"
    )
    recorded = coded_value(recorded_field)
    family_lead = coded_value(identity.get("family_lead"))
    if isinstance(recorded, list):
        recorded_set = {item for item in recorded if isinstance(item, str)}
        if len(recorded_set) != len(recorded):
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/possible_companion_reports_or_shared_implementations/value",
                    "derived companion union contains duplicate values",
                )
            )
        if recorded_set != expected:
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/possible_companion_reports_or_shared_implementations/value",
                    "derived companion union does not equal the reuse-record union",
                )
            )
        if isinstance(recorded_field, Mapping) and (
            recorded_field.get("provenance") != "reviewer_derived"
        ):
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/possible_companion_reports_or_shared_implementations/provenance",
                    "derived companion union must use reviewer_derived provenance",
                )
            )
    elif expected:
        issues.append(
            Issue(
                str(document.path),
                "/identity/possible_companion_reports_or_shared_implementations",
                "derived companion union is a status despite identified candidates",
            )
        )

    if expected and family_lead != "yes":
        issues.append(
            Issue(
                str(document.path),
                "/identity/family_lead/value",
                "family_lead must be yes when the companion union is nonempty",
            )
        )
    if not expected and family_lead == "yes":
        issues.append(
            Issue(
                str(document.path),
                "/identity/family_lead/value",
                "family_lead cannot be yes when the companion union is empty",
            )
        )
    return issues


def rq2_semantic_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for index, finding in enumerate(rows(document.data.get("rq2_findings"))):
        base = f"/rq2_findings/{index}"
        claim_kind = coded_value(finding.get("claim_kind"))
        if claim_kind in {"comparative", "causal_attribution"} and not linked_locations(
            finding.get("linked_comparator_ids"),
            indexes["comparator"],
            containing_report=document,
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_comparator_ids",
                    f"{claim_kind} finding has no comparator in the report",
                )
            )

        role = coded_value(finding.get("role"))
        if role in {"implementation_burden", "mixed_trade_off"} and not (
            linked_locations(
                finding.get("linked_implementation_record_ids"),
                indexes["implementation_record"],
                containing_report=document,
            )
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_implementation_record_ids",
                    f"{role} finding has no implementation record in the report",
                )
            )

        if (
            coded_value(finding.get("outcome_category")) == "eps_reliability"
            and coded_value(finding.get("reliability_subtype")) is None
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/reliability_subtype",
                    "EPS reliability finding has no reliability subtype",
                )
            )
    return issues


def rq3_semantic_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for index, activity in enumerate(rows(document.data.get("rq3_activities"))):
        base = f"/rq3_activities/{index}"
        status_value = activity.get("status")
        statuses = set(status_value) if isinstance(status_value, list) else set()
        target_type_value = coded_value(activity.get("target_types"))
        target_types = (
            set(target_type_value) if isinstance(target_type_value, list) else set()
        )
        assessment_aspect_value = coded_value(
            activity.get("model_assessment_aspects")
        )
        assessment_aspects = (
            set(assessment_aspect_value)
            if isinstance(assessment_aspect_value, list)
            else set()
        )

        if "proposed" in statuses:
            proposed_requirements = (
                (
                    bool(activity.get("target_refs"))
                    or has_recorded_content(activity.get("eps_target")),
                    "target_refs",
                    "EPS target",
                ),
                (
                    has_recorded_content(activity.get("linked_model_artifact_ids")),
                    "linked_model_artifact_ids",
                    "model artifact",
                ),
                (
                    bool(activity.get("model_to_vv_relationship_ids"))
                    or has_recorded_content(activity.get("explicit_model_to_vv_bridge")),
                    "model_to_vv_relationship_ids",
                    "model-to-V&V bridge",
                ),
                (
                    bool(activity.get("vv_method_entity_ids"))
                    or has_recorded_content(activity.get("method")),
                    "vv_method_entity_ids",
                    "V&V method",
                ),
            )
            for complete, field, label in proposed_requirements:
                if not complete:
                    issues.append(
                        Issue(
                            str(document.path),
                            f"{base}/{field}",
                            f"proposed milestone lacks {label}",
                        )
                    )

        criteria = linked_locations(
            activity.get("linked_result_criterion_ids"),
            indexes["result_criterion"],
            containing_report=document,
        )
        outputs = linked_locations(
            activity.get("linked_result_output_ids"),
            indexes["result_output"],
            containing_report=document,
        )
        coverage_items = linked_locations(
            activity.get("linked_coverage_item_ids"),
            indexes.get("coverage_item", {}),
            containing_report=document,
        )
        model_artifacts = linked_locations(
            activity.get("linked_model_artifact_ids"),
            indexes.get("model_artifact", {}),
            containing_report=document,
        )
        if "prepared_or_generated" in statuses and not any(
            has_recorded_content(
                location.node.get("source_criterion_or_requirement_id")
            )
            or has_recorded_content(location.node.get("threshold_or_expected_behavior"))
            for location in criteria
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_result_criterion_ids",
                    "prepared_or_generated milestone has no linked criterion content",
                )
            )

        result_is_reported = any(
            has_recorded_content(location.node.get("source_reported_value"))
            for location in outputs
        ) or any(
            has_recorded_content(location.node.get("result_or_verdict"))
            for location in criteria
        )
        if "result_reported" in statuses and not result_is_reported:
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/status",
                    "result_reported milestone has no linked output value or verdict",
                )
            )

        if "executed_virtual" in statuses:
            execution_settings = coded_value(activity.get("execution_settings"))
            if not isinstance(execution_settings, list) or not (
                set(execution_settings) - {"unclear"}
            ):
                issues.append(
                    Issue(
                        str(document.path),
                        f"{base}/execution_settings",
                        "executed_virtual milestone has no resolved execution setting",
                    )
                )

        if "executed_physical" in statuses and coded_value(
            activity.get("hardware_present")
        ) not in TARGET_HARDWARE_PRESENCE:
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/hardware_present",
                    "executed_physical milestone has no representative or actual "
                    "target hardware",
                )
            )

        if "downstream_physical_link" in statuses and not (
            isinstance(activity.get("later_physical_relationship_ids"), list)
            and activity["later_physical_relationship_ids"]
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/later_physical_relationship_ids",
                    "downstream_physical_link milestone lacks a relationship record",
                )
            )
        if "model_to_test_closure" in statuses and not (
            isinstance(activity.get("closure_check_ids"), list)
            and activity["closure_check_ids"]
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/closure_check_ids",
                    "model_to_test_closure milestone lacks a closure check record",
                )
            )

        predecessors = activity.get("predecessor_rq3_activity_ids")
        if isinstance(predecessors, list) and predecessors:
            control_flow_relationships = linked_locations(
                activity.get("control_flow_relationship_ids"),
                indexes.get("relationship", {}),
                containing_report=document,
            )
            if not control_flow_relationships:
                issues.append(
                    Issue(
                        str(document.path),
                        f"{base}/control_flow_relationship_ids",
                        "ordered RQ3 activity lacks a control-flow relationship",
                    )
                )
            else:
                current_ref = f"rq3_activity:{activity.get('rq3_activity_id')}"
                for predecessor_index, predecessor_id in enumerate(predecessors):
                    predecessor_ref = f"rq3_activity:{predecessor_id}"
                    if not any(
                        location.node.get("relationship_type") == "precedes"
                        and location.node.get("source_ref") == predecessor_ref
                        and location.node.get("target_ref") == current_ref
                        for location in control_flow_relationships
                    ):
                        issues.append(
                            Issue(
                                str(document.path),
                                f"{base}/predecessor_rq3_activity_ids/"
                                f"{predecessor_index}",
                                "RQ3 predecessor lacks a matching precedes "
                                "relationship",
                            )
                        )

        resolved_assessment_aspects = assessment_aspects - {"unclear"}
        if resolved_assessment_aspects and not (
            target_types & MODEL_ASSESSMENT_TARGET_TYPES
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/target_types",
                    "model assessment aspects lack a model, representation, "
                    "configuration, transformation, or digital-twin target",
                )
            )
        if (
            resolved_assessment_aspects & COMPLETENESS_ASSESSMENT_ASPECTS
            and statuses & {"prepared_or_generated", "result_reported"}
            and not criteria
            and not coverage_items
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_coverage_item_ids",
                    "executed or prepared completeness assessment lacks a linked "
                    "criterion or coverage denominator",
                )
            )
        if "digital_twin" in target_types and model_artifacts and not any(
            isinstance(coded_value(location.node.get("model_roles")), list)
            and "digital_twin" in coded_value(location.node.get("model_roles"))
            for location in model_artifacts
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_model_artifact_ids",
                    "digital twin target lacks a linked artifact with the digital twin "
                    "model role",
                )
            )
        if (
            "model_configuration_or_baseline" in target_types
            and not has_recorded_content(
                activity.get("linked_configuration_entity_ids")
            )
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_configuration_entity_ids",
                    "model configuration or baseline target lacks a configuration link",
                )
            )
        if (
            "model_representation_or_view" in target_types
            and not has_recorded_content(
                activity.get("linked_model_representation_ids")
            )
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_model_representation_ids",
                    "model representation or view target lacks a representation link",
                )
            )

        normalized_object_value = coded_value(
            activity.get("normalized_vv_objects")
        )
        normalized_objects = (
            set(normalized_object_value)
            if isinstance(normalized_object_value, list)
            else set()
        )
        validation_objects = normalized_objects & {
            "model_validation",
            "system_or_design_validation",
        }
        if validation_objects and not any(
            (
                isinstance(location.node.get("authority_check_ids"), list)
                and bool(location.node["authority_check_ids"])
            )
            or has_ordinary_value(
                location.node.get(
                    "why_criterion_or_oracle_is_authoritative_for_intended_use"
                )
            )
            for location in criteria
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/linked_result_criterion_ids",
                    f"{', '.join(sorted(validation_objects))} has no linked "
                    "criterion authority reason",
                )
            )
    return issues


def procedure_component_is_reported(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and value.get("value") == "reported"
        and isinstance(value.get("basis_refs"), list)
        and bool(value["basis_refs"])
    )


def procedure_component_is_resolved(value: Any) -> bool:
    return procedure_component_is_reported(value) or (
        isinstance(value, Mapping)
        and value.get("status") in {"none", "not_applicable"}
    )


def procedure_reporting_deficiencies(
    reporting: Mapping[str, Any],
    structured_steps: list[dict[str, Any]],
) -> list[str]:
    level = coded_value(reporting.get("procedure_detail_level"))
    deficiencies: list[str] = []
    if isinstance(level, str) and not has_ordinary_value(
        reporting.get("detail_level_reason")
    ):
        deficiencies.append("detail-level reason")
    if level not in {"actionable_procedure", "reproduction_ready"}:
        return deficiencies

    if not structured_steps:
        deficiencies.append("structured steps or activities")
    for field, label, requires_ordinary in (
        ("ordered_or_connected_steps", "ordered or connected steps", True),
        ("material_inputs", "resolved material inputs", False),
        ("outputs", "outputs", True),
        ("roles_and_responsibilities", "resolved roles", False),
        ("tools_and_settings", "resolved tools and settings", False),
        ("decision_rules", "resolved decision rules", False),
        ("branching_and_iteration", "resolved branching and iteration", False),
        ("quality_or_completion_checks", "quality or completion checks", True),
    ):
        value = reporting.get(field)
        complete = (
            procedure_component_is_reported(value)
            if requires_ordinary
            else procedure_component_is_resolved(value)
        )
        if not complete:
            deficiencies.append(label)
    if level == "reproduction_ready" and not procedure_component_is_reported(
        reporting.get("supporting_materials")
    ):
        deficiencies.append("accessible supporting materials")
    return deficiencies


def procedural_detail_issues(
    documents: Iterable[Document],
) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        candidates: list[tuple[str, Mapping[str, Any], list[dict[str, Any]]]] = []
        if document.kind == "report":
            mbse = document.data.get("mbse_approach", {})
            if isinstance(mbse, Mapping):
                for index, method in enumerate(
                    rows(mbse.get("model_generation_methods"))
                ):
                    reporting = method.get("procedure_reporting", {})
                    if isinstance(reporting, Mapping):
                        candidates.append(
                            (
                                (
                                    f"/mbse_approach/model_generation_methods/{index}/"
                                    "procedure_reporting/procedure_detail_level"
                                ),
                                reporting,
                                rows(method.get("method_steps")),
                            )
                        )
                for index, workflow in enumerate(rows(mbse.get("workflows"))):
                    reporting = workflow.get("procedure_reporting", {})
                    if isinstance(reporting, Mapping):
                        candidates.append(
                            (
                                (
                                    f"/mbse_approach/workflows/{index}/"
                                    "procedure_reporting/procedure_detail_level"
                                ),
                                reporting,
                                rows(workflow.get("workflow_activities")),
                            )
                        )
            reuse = document.data.get("reuse", {})
            if isinstance(reuse, Mapping):
                for index, record in enumerate(rows(reuse.get("report_reuse_records"))):
                    design = record.get("reuse_design", {})
                    if not isinstance(design, Mapping):
                        continue
                    reporting = design.get("tailoring_procedure_reporting", {})
                    if isinstance(reporting, Mapping):
                        steps = rows(design.get("tailoring_procedure_steps"))
                        if not steps:
                            steps = rows(design.get("tailoring_rules"))
                        candidates.append(
                            (
                                (
                                    f"/reuse/report_reuse_records/{index}/reuse_design/"
                                    "tailoring_procedure_reporting/"
                                    "procedure_detail_level"
                                ),
                                reporting,
                                steps,
                            )
                        )
        elif document.kind == "lineage":
            design = document.data.get("reuse_design", {})
            if isinstance(design, Mapping):
                reporting = design.get("tailoring_procedure_reporting", {})
                if isinstance(reporting, Mapping):
                    steps = rows(design.get("tailoring_procedure_steps"))
                    if not steps:
                        steps = rows(design.get("tailoring_rules"))
                    candidates.append(
                        (
                            (
                                "/reuse_design/tailoring_procedure_reporting/"
                                "procedure_detail_level"
                            ),
                            reporting,
                            steps,
                        )
                    )

        for base, reporting, steps in candidates:
            deficiencies = procedure_reporting_deficiencies(reporting, steps)
            if deficiencies:
                issues.append(
                    Issue(
                        str(document.path),
                        base,
                        f"{coded_value(reporting.get('procedure_detail_level'))} lacks "
                        + ", ".join(deficiencies),
                    )
                )
    return issues


def procedural_profile_issues(document: Document) -> list[Issue]:
    if document.kind != "report":
        return []
    issues: list[Issue] = []
    reuse = document.data.get("reuse", {})
    profile = document.data.get("procedural_evidence_profile", {})
    mbse = document.data.get("mbse_approach", {})
    if not all(isinstance(item, Mapping) for item in (reuse, profile, mbse)):
        return issues

    records = rows(reuse.get("report_reuse_records"))
    generic_records: list[Mapping[str, Any]] = []
    for record in records:
        generality = coded_value(record.get("artifact_generality"))
        artifact_type = coded_value(record.get("artifact_type"))
        if generality in {
            "product_family",
            "mission_class_reference",
            "platform_agnostic",
        } or artifact_type == "reference_or_template_model":
            generic_records.append(record)
    generic_record_ids = {
        item.get("report_reuse_record_id")
        for item in generic_records
        if isinstance(item.get("report_reuse_record_id"), str)
    }
    generic_artifact_ids = {
        identifier
        for record in generic_records
        for identifier in (
            record.get("linked_model_artifact_ids")
            if isinstance(record.get("linked_model_artifact_ids"), list)
            else []
        )
        if isinstance(identifier, str)
    }
    linked_generic_method_ids = {
        identifier
        for record in generic_records
        for identifier in (
            record.get("linked_model_generation_method_ids")
            if isinstance(record.get("linked_model_generation_method_ids"), list)
            else []
        )
        if isinstance(identifier, str)
    }
    actionable_methods: list[Mapping[str, Any]] = []
    for method in rows(mbse.get("model_generation_methods")):
        reporting = method.get("procedure_reporting", {})
        level = coded_value(reporting.get("procedure_detail_level")) if isinstance(
            reporting, Mapping
        ) else None
        output_ids = method.get("linked_output_model_artifact_ids", [])
        method_id = method.get("model_generation_method_id")
        linked_to_generic = (
            isinstance(method_id, str) and method_id in linked_generic_method_ids
        ) or (
            isinstance(output_ids, list)
            and bool(generic_artifact_ids.intersection(output_ids))
        )
        if level in {"actionable_procedure", "reproduction_ready"} and linked_to_generic:
            actionable_methods.append(method)

    actionable_tailoring_records = []
    for record in generic_records:
        design = record.get("reuse_design", {})
        reporting = (
            design.get("tailoring_procedure_reporting", {})
            if isinstance(design, Mapping)
            else {}
        )
        if isinstance(reporting, Mapping) and coded_value(
            reporting.get("procedure_detail_level")
        ) in {"actionable_procedure", "reproduction_ready"}:
            actionable_tailoring_records.append(record)

    generic_applications: list[Mapping[str, Any]] = []
    for application in rows(reuse.get("report_applications")):
        linked = application.get("linked_report_reuse_record_ids", [])
        if isinstance(linked, list) and generic_record_ids.intersection(linked):
            generic_applications.append(application)
    worked_applications = []
    assured_applications = []
    for application in generic_applications:
        tailoring = application.get("tailoring_or_adaptation", {})
        result = application.get("result_and_assurance", {})
        setting = application.get("setting", {})
        if not isinstance(tailoring, Mapping):
            tailoring = {}
        if not isinstance(result, Mapping):
            result = {}
        if not isinstance(setting, Mapping):
            setting = {}
        resulting_application_identified = has_resolved_links(
            result.get("resulting_model_artifact_ids")
        ) or has_resolved_links(setting.get("target_refs"))
        if resulting_application_identified and (
            bool(rows(tailoring.get("executed_operations")))
            or (
                has_ordinary_value(
                    tailoring.get("reasons_for_changes_or_unchanged_use")
                )
                and has_resolved_links(tailoring.get("reason_rule_ids"))
            )
        ):
            worked_applications.append(application)
        if (
            has_resolved_links(result.get("post_application_criterion_ids"))
            and has_ordinary_value(result.get("assurance_timing"))
            and (
                has_resolved_links(result.get("assurance_check_ids"))
                or has_resolved_links(result.get("assurance_rq3_activity_ids"))
            )
        ):
            assured_applications.append(application)

    expected = {
        "generic_or_reference_model_reported": bool(generic_records),
        "actionable_model_construction_procedure_reported": bool(actionable_methods),
        "actionable_tailoring_procedure_reported": bool(
            actionable_tailoring_records
        ),
        "worked_tailoring_example_reported": bool(worked_applications),
        "post_tailoring_assurance_reported": bool(assured_applications),
        "generic_model_with_actionable_construction_or_tailoring": bool(
            generic_records and (actionable_methods or actionable_tailoring_records)
        ),
    }
    for field, condition in expected.items():
        flag = profile.get(field, {})
        value = flag.get("value") if isinstance(flag, Mapping) else None
        basis_ids = flag.get("basis_ids") if isinstance(flag, Mapping) else None
        if value == "yes" and not (isinstance(basis_ids, list) and basis_ids):
            issues.append(
                Issue(
                    str(document.path),
                    f"/procedural_evidence_profile/{field}/basis_ids",
                    "derived yes flag has no basis IDs",
                )
            )
        if value == "yes" and not condition:
            issues.append(
                Issue(
                    str(document.path),
                    f"/procedural_evidence_profile/{field}/value",
                    "derived flag is yes without qualifying linked evidence",
                )
            )
        if value == "no" and condition:
            issues.append(
                Issue(
                    str(document.path),
                    f"/procedural_evidence_profile/{field}/value",
                    "derived flag is no despite qualifying linked evidence",
                )
            )
    return issues


def has_resolved_links(value: Any) -> bool:
    return (isinstance(value, list) and bool(value)) or (
        isinstance(value, Mapping)
        and value.get("status") in {"none", "not_applicable"}
    )


def reuse_specification_deficiencies(
    record: Mapping[str, Any],
) -> list[str]:
    deficiencies: list[str] = []
    envelope = record.get("declared_applicability_envelope", {})
    design = record.get("reuse_design", {})
    if not isinstance(envelope, Mapping):
        envelope = {}
    if not isinstance(design, Mapping):
        design = {}

    dimensions = (
        ("target_platforms_and_missions", "target_refs"),
        ("lifecycle_uses_and_decisions", "lifecycle_stages"),
        ("eps_boundary", "eps_scope_refs"),
        ("model_boundary_and_abstraction", "model_scope_refs"),
        ("architecture_and_interfaces", "architecture_and_interface_refs"),
        ("environment_modes_and_loads", "environment_mode_and_load_refs"),
        ("required_inputs", "required_input_refs"),
        ("linked_tool_ids", "linked_tool_ids"),
        ("organizational_prerequisites", "organizational_prerequisite_refs"),
        ("exclusions_and_limits", "limit_rule_ids"),
    )
    for source_field, normalized_field in dimensions:
        source_value = envelope.get(source_field)
        if not has_resolved_dimension(source_value):
            deficiencies.append(f"resolved envelope dimension {source_field}")
            continue
        if has_ordinary_value(source_value):
            normalized = envelope.get(normalized_field)
            normalized_is_resolved = (
                has_resolved_dimension(normalized)
                if normalized_field in {"lifecycle_stages", "linked_tool_ids"}
                else has_resolved_links(normalized)
            )
            if not normalized_is_resolved:
                deficiencies.append(
                    f"normalized links for envelope dimension {source_field}"
                )

    if not has_ordinary_value(design.get("reusable_core")):
        deficiencies.append("reusable core")
    elif not has_resolved_links(design.get("core_member_refs")):
        deficiencies.append("linked reusable-core members")
    variation_points = rows(design.get("variation_points"))
    tailoring_rules = rows(design.get("tailoring_rules"))
    tailoring_steps = rows(design.get("tailoring_procedure_steps"))
    unchanged_use_rule = design.get("unchanged_use_rule")
    if not variation_points and not has_ordinary_value(unchanged_use_rule):
        deficiencies.append("variation points or explicit unchanged-use rule")
    if (
        not tailoring_rules
        and not tailoring_steps
        and not has_ordinary_value(unchanged_use_rule)
    ):
        deficiencies.append("tailoring or adaptation process")
    if not has_resolved_dimension(design.get("required_roles_and_skills")):
        deficiencies.append("resolved required roles and skills")
    elif has_ordinary_value(design.get("required_roles_and_skills")) and not (
        has_resolved_links(design.get("required_role_entity_ids"))
        and has_resolved_links(design.get("required_skill_entity_ids"))
    ):
        deficiencies.append("linked required roles and skills")
    if not has_resolved_dimension(design.get("required_tool_ids")):
        deficiencies.append("resolved required tools")
    if not has_resolved_dimension(design.get("required_data_and_tool_settings")):
        deficiencies.append("resolved required data and settings")
    elif has_ordinary_value(
        design.get("required_data_and_tool_settings")
    ) and not has_resolved_links(design.get("required_data_and_configuration_refs")):
        deficiencies.append("linked required data and configurations")
    return deficiencies


def application_deficiencies(
    application: Mapping[str, Any],
    allowed_objects: set[str],
    require_independence: bool,
) -> list[str]:
    deficiencies: list[str] = []
    application_object = coded_value(application.get("application_object"))
    if application_object not in allowed_objects:
        deficiencies.append("application object")

    setting = application.get("setting", {})
    tailoring = application.get("tailoring_or_adaptation", {})
    result = application.get("result_and_assurance", {})
    independence = application.get("independence", {})
    if not isinstance(setting, Mapping):
        setting = {}
    if not isinstance(tailoring, Mapping):
        tailoring = {}
    if not isinstance(result, Mapping):
        result = {}
    if not isinstance(independence, Mapping):
        independence = {}

    if not has_ordinary_value(setting.get("material_setting_differences")):
        deficiencies.append("material setting differences")
    elif not has_resolved_links(
        setting.get("material_difference_relationship_ids")
    ):
        deficiencies.append("linked material setting differences")
    if not has_ordinary_value(
        tailoring.get(
            "retained_artifact_core_method_steps_or_workflow_activities"
        )
    ):
        deficiencies.append("retained core, method steps, or workflow activities")
    elif not has_resolved_links(tailoring.get("retained_refs")):
        deficiencies.append("linked retained core or procedure members")
    changed = tailoring.get(
        "configured_or_changed_artifact_content_method_steps_or_workflow_activities"
    )
    unchanged_reason = tailoring.get("reasons_for_changes_or_unchanged_use")
    if not has_ordinary_value(changed) and not has_ordinary_value(unchanged_reason):
        deficiencies.append("changed content or justified unchanged use")
    if has_ordinary_value(changed) and not has_resolved_links(
        tailoring.get("changed_refs")
    ):
        deficiencies.append("linked changed content or procedure members")
    if has_ordinary_value(changed) and not rows(tailoring.get("executed_operations")):
        deficiencies.append("structured executed operation")

    if not has_resolved_links(result.get("post_application_criterion_ids")):
        deficiencies.append("post-application criterion")
    if not has_ordinary_value(result.get("assurance_method")):
        deficiencies.append("assurance method")
    if not has_ordinary_value(result.get("assurance_timing")):
        deficiencies.append("assurance timing")
    if not has_ordinary_value(result.get("assurance_result")):
        deficiencies.append("assurance result")
    if not (
        has_resolved_links(result.get("assurance_check_ids"))
        or has_resolved_links(result.get("assurance_rq3_activity_ids"))
    ):
        deficiencies.append("linked assurance evidence")
    if coded_value(result.get("application_result")) not in {
        "success",
        "partial",
        "failure",
    }:
        deficiencies.append("resolved application result")

    originator_relationship = coded_value(setting.get("relationship_to_originator"))
    if originator_relationship in {None, "unclear", "independent_evaluation_only"}:
        deficiencies.append("adopter-controlled application")
    if require_independence:
        if originator_relationship not in {
            "same_organization_operationally_separate",
            "outside_originating_organization",
        }:
            deficiencies.append("qualifying independent adopter")
        for field, label in (
            ("personnel_overlap", "personnel-overlap evidence"),
            ("implementation_control", "implementation-control evidence"),
            (
                "adopter_attributable_evidence_for_adoption",
                "adopter-attributable adoption evidence",
            ),
            (
                "adopter_attributable_evidence_for_assurance",
                "adopter-attributable assurance evidence",
            ),
        ):
            if not has_resolved_evidence(independence.get(field)):
                deficiencies.append(label)
        if independence.get("personnel_overlap_status") in {None, "unclear"}:
            deficiencies.append("resolved personnel-overlap status")
        if not has_resolved_links(independence.get("controlling_team_entity_ids")):
            deficiencies.append("controlling-team links")
        if not has_resolved_links(independence.get("adoption_evidence_refs")):
            deficiencies.append("linked adopter-attributable adoption evidence")
        if not has_resolved_links(independence.get("assurance_evidence_refs")):
            deficiencies.append("linked adopter-attributable assurance evidence")
    return deficiencies


def qualifying_application_exists(
    application_ids: Any,
    index: Mapping[str, Location],
    allowed_objects: set[str],
    require_independence: bool,
    containing_report: Document | None = None,
) -> tuple[bool, list[str]]:
    if not isinstance(application_ids, list) or not application_ids:
        return False, ["no linked application"]
    candidate_deficiencies: list[str] = []
    for identifier in application_ids:
        location = index.get(identifier) if isinstance(identifier, str) else None
        if location is None:
            candidate_deficiencies.append(f"unresolved application {identifier!r}")
            continue
        if containing_report is not None and location.document != containing_report:
            candidate_deficiencies.append(
                f"application {identifier!r} is outside the report"
            )
            continue
        deficiencies = application_deficiencies(
            location.node,
            allowed_objects,
            require_independence,
        )
        if not deficiencies:
            return True, []
        candidate_deficiencies.append(
            f"application {identifier!r} lacks " + ", ".join(deficiencies)
        )
    return False, candidate_deficiencies


def reuse_level_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        if document.kind == "report":
            reuse = document.data.get("reuse", {})
            if not isinstance(reuse, Mapping):
                continue
            for index, record in enumerate(rows(reuse.get("report_reuse_records"))):
                assessment = record.get("reuse_assessment", {})
                if not isinstance(assessment, Mapping):
                    continue
                application_ids = assessment.get("linked_report_application_ids")
                base = f"/reuse/report_reuse_records/{index}/reuse_assessment"
                for level_field, link_field, label in (
                    ("report_reuse_level", "linked_model_artifact_ids", "artifact"),
                    (
                        "method_reuse_level",
                        "linked_model_generation_method_ids",
                        "method",
                    ),
                    ("workflow_reuse_level", "linked_workflow_ids", "workflow"),
                ):
                    level = coded_value(assessment.get(level_field))
                    links = record.get(link_field)
                    if level not in {None, "NA"} and not (
                        isinstance(links, list) and links
                    ):
                        issues.append(
                            Issue(
                                str(document.path),
                                f"{base}/{level_field}",
                                f"{level} has no linked {label}",
                            )
                        )
                for (
                    field,
                    specified_levels,
                    high_levels,
                    objects,
                    application_kind,
                ) in (
                    (
                        "report_reuse_level",
                        {
                            "R2_reuse_specified",
                            "R3_reuse_demonstrated",
                            "R4_independent_reuse_demonstrated",
                        },
                        {
                            "R3_reuse_demonstrated",
                            "R4_independent_reuse_demonstrated",
                        },
                        ARTIFACT_APPLICATION_OBJECTS,
                        "artifact",
                    ),
                    (
                        "method_reuse_level",
                        {
                            "M2_method_reuse_specified",
                            "M3_method_reuse_demonstrated",
                            "M4_independent_method_reuse_demonstrated",
                        },
                        {
                            "M3_method_reuse_demonstrated",
                            "M4_independent_method_reuse_demonstrated",
                        },
                        METHOD_APPLICATION_OBJECTS,
                        "method",
                    ),
                    (
                        "workflow_reuse_level",
                        {
                            "W2_workflow_reuse_specified",
                            "W3_workflow_reuse_demonstrated",
                            "W4_independent_workflow_reuse_demonstrated",
                        },
                        {
                            "W3_workflow_reuse_demonstrated",
                            "W4_independent_workflow_reuse_demonstrated",
                        },
                        WORKFLOW_APPLICATION_OBJECTS,
                        "workflow",
                    ),
                ):
                    level = coded_value(assessment.get(field))
                    if level in specified_levels:
                        specification_deficiencies = reuse_specification_deficiencies(
                            record
                        )
                        if specification_deficiencies:
                            issues.append(
                                Issue(
                                    str(document.path),
                                    f"{base}/{field}",
                                    f"{level} lacks "
                                    + ", ".join(specification_deficiencies),
                                )
                            )
                    if level in high_levels:
                        independent = level.startswith(("R4_", "M4_", "W4_"))
                        valid, deficiencies = qualifying_application_exists(
                            application_ids,
                            indexes["report_application"],
                            objects,
                            independent,
                            containing_report=document,
                        )
                        if not valid:
                            issues.append(
                                Issue(
                                    str(document.path),
                                    f"{base}/{field}",
                                    f"{level} has no qualifying linked "
                                    f"{application_kind} application: "
                                    f"{'; '.join(deficiencies)}",
                                )
                            )
        elif document.kind == "lineage":
            assessment = document.data.get("reuse_assessment", {})
            if not isinstance(assessment, Mapping):
                continue
            level = coded_value(assessment.get("lineage_reuse_level"))
            if level in {
                "R2_reuse_specified",
                "R3_reuse_demonstrated",
                "R4_independent_reuse_demonstrated",
            }:
                specification_deficiencies = reuse_specification_deficiencies(
                    document.data
                )
                if specification_deficiencies:
                    issues.append(
                        Issue(
                            str(document.path),
                            "/reuse_assessment/lineage_reuse_level",
                            f"{level} lacks " + ", ".join(specification_deficiencies),
                        )
                    )
            if level in {
                "R3_reuse_demonstrated",
                "R4_independent_reuse_demonstrated",
            }:
                valid, deficiencies = qualifying_application_exists(
                    assessment.get("linked_tailoring_application_ids"),
                    indexes["tailoring_application"],
                    ARTIFACT_APPLICATION_OBJECTS,
                    level == "R4_independent_reuse_demonstrated",
                )
                if not valid:
                    issues.append(
                        Issue(
                            str(document.path),
                            "/reuse_assessment/lineage_reuse_level",
                            f"{level} has no qualifying consolidated application: "
                            f"{'; '.join(deficiencies)}",
                        )
                    )
    return issues


def report_id(document: Document) -> str | None:
    identity = document.data.get("identity", {})
    if not isinstance(identity, Mapping):
        return None
    value = identity.get("report_id")
    return value if isinstance(value, str) else None


def citation_quote_issues(
    report_documents: Iterable[Document],
    page_texts: Mapping[str, tuple[Path, Mapping[int, str]]],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for identifier, (path, _pages) in page_texts.items():
        if identifier not in indexes["report"]:
            issues.append(
                Issue(
                    str(path),
                    "/",
                    f"page text is mapped to unknown report {identifier!r}",
                )
            )

    for document in report_documents:
        identifier = report_id(document)
        citations = rows(document.data.get("citations"))
        if not citations or identifier is None:
            continue
        page_text = page_texts.get(identifier)
        if page_text is None:
            issues.append(
                Issue(
                    str(document.path),
                    "/citations",
                    f"report {identifier!r} has citations but no page-text mapping",
                )
            )
            continue
        _page_text_path, pages = page_text
        for index, citation in enumerate(citations):
            page = citation.get("page")
            citation_pointer = f"/citations/{index}"
            if not isinstance(page, int) or page not in pages:
                issues.append(
                    Issue(
                        str(document.path),
                        f"{citation_pointer}/page",
                        f"cited page {page!r} is absent from frozen page text",
                    )
                )
                continue
            if "graphic" in citation or "graphic_quote_description" in citation:
                continue
            quote = citation.get("quote")
            if not isinstance(quote, str):
                continue
            normalized_quote = normalize_quote_text(quote)
            normalized_page = normalize_quote_text(pages[page])
            if normalized_quote not in normalized_page:
                issues.append(
                    Issue(
                        str(document.path),
                        f"{citation_pointer}/quote",
                        "normalized quote does not occur on the cited page",
                    )
                )
    return issues


def lineage_values(node: Any, base: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(node, Mapping):
        for key, value in node.items():
            child_pointer = pointer(base, key)
            if key == "lineage_id":
                result[child_pointer] = value
            else:
                result.update(lineage_values(value, child_pointer))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            result.update(lineage_values(value, pointer(base, index)))
    return result


def mask_lineage_values(node: Any) -> Any:
    if isinstance(node, Mapping):
        return {
            key: "__LINEAGE_ID__" if key == "lineage_id" else mask_lineage_values(value)
            for key, value in node.items()
        }
    if isinstance(node, list):
        return [mask_lineage_values(value) for value in node]
    return node


def immutability_issues(
    current_reports: Iterable[Document],
    baseline_reports: Iterable[Document],
) -> list[Issue]:
    issues: list[Issue] = []
    current = {report_id(document): document for document in current_reports}
    baseline = {report_id(document): document for document in baseline_reports}
    current.pop(None, None)
    baseline.pop(None, None)
    for identifier, old_document in baseline.items():
        new_document = current.get(identifier)
        if new_document is None:
            issues.append(
                Issue(
                    str(old_document.path),
                    "/identity/report_id",
                    f"baseline report {identifier!r} has no current report",
                )
            )
            continue
        if mask_lineage_values(old_document.data) != mask_lineage_values(
            new_document.data
        ):
            issues.append(
                Issue(
                    str(new_document.path),
                    "/",
                    "report changed outside lineage_id fields after the first-pass baseline",
                )
            )
        old_values = lineage_values(old_document.data)
        new_values = lineage_values(new_document.data)
        if set(old_values) != set(new_values):
            issues.append(
                Issue(
                    str(new_document.path),
                    "/",
                    "the set of report-level lineage_id fields changed",
                )
            )
            continue
        for value_pointer, old_value in old_values.items():
            new_value = new_values[value_pointer]
            if old_value == new_value:
                continue
            if old_value not in {"pending_resolution", "not_applicable"}:
                issues.append(
                    Issue(
                        str(new_document.path),
                        value_pointer,
                        f"lineage_id changed from disallowed first-pass value {old_value!r}",
                    )
                )
            if new_value in {"pending_resolution", "not_applicable"}:
                issues.append(
                    Issue(
                        str(new_document.path),
                        value_pointer,
                        f"lineage_id changed to unresolved first-pass value {new_value!r}",
                    )
                )
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for option, kind in (
        ("--report", "report"),
        ("--family", "family"),
        ("--lineage", "lineage"),
        ("--tailoring-application", "tailoring_application"),
        ("--audit", "audit"),
        ("--baseline-report", "baseline_report"),
    ):
        parser.add_argument(option, action="append", type=Path, default=[], dest=kind)
    parser.add_argument(
        "--screening-candidates",
        action="append",
        type=Path,
        default=[],
        help="screening candidate file exported by deduplication.py",
    )
    parser.add_argument(
        "--page-text",
        action="append",
        default=[],
        metavar="REPORT_ID=PATH",
        help="map a report ID to frozen text containing PDF_PAGE markers",
    )
    parser.add_argument(
        "--schemas-only",
        action="store_true",
        help="compile the schemas without validating extraction records",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schemas, registry = load_schemas()
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2))
        return 1

    documents: list[Document] = []
    baseline_documents: list[Document] = []
    page_texts, load_issues = load_page_texts(args.page_text)
    screening_records, screening_load_issues = load_screening_candidates(
        args.screening_candidates
    )
    load_issues.extend(screening_load_issues)
    for kind in SCHEMA_PATHS:
        for path in getattr(args, kind):
            try:
                documents.append(Document(kind, path, load_object(path)))
            except (OSError, ValueError, json.JSONDecodeError) as error:
                load_issues.append(Issue(str(path), "/", str(error)))
    for path in args.baseline_report:
        try:
            baseline_documents.append(Document("report", path, load_object(path)))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            load_issues.append(Issue(str(path), "/", str(error)))

    if not args.schemas_only and not documents and not baseline_documents:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": "provide extraction records or use --schemas-only",
                },
                indent=2,
            )
        )
        return 2

    issues = load_issues
    issues.extend(schema_issues(documents, schemas, registry))
    issues.extend(schema_issues(baseline_documents, schemas, registry))
    indexes, index_issues = build_indexes(documents)
    issues.extend(index_issues)
    for document in documents:
        if document.kind == "report":
            issues.extend(report_reference_issues(document, indexes))
            issues.extend(report_application_lineage_issues(document, indexes))
            issues.extend(family_lead_issues(document))
            issues.extend(report_source_file_issues(document))
            issues.extend(reviewer_derived_script_issues(document))
            issues.extend(rq2_semantic_issues(document, indexes))
            issues.extend(rq3_semantic_issues(document, indexes))
            issues.extend(procedural_profile_issues(document))
        else:
            issues.extend(cross_record_reference_issues(document, indexes))
        issues.extend(evidence_issues(document, indexes))
        issues.extend(normalization_issues(document))
    issues.extend(
        screening_record_issues(
            (document for document in documents if document.kind == "report"),
            screening_records,
        )
    )
    issues.extend(lineage_consistency_issues(documents, indexes))
    issues.extend(consolidation_issues(documents, indexes))
    issues.extend(family_consistency_issues(documents, indexes))
    issues.extend(audit_coverage_issues(documents, indexes))
    issues.extend(procedural_detail_issues(documents))
    issues.extend(reuse_level_issues(documents, indexes))
    issues.extend(
        citation_quote_issues(
            (document for document in documents if document.kind == "report"),
            page_texts,
            indexes,
        )
    )
    issues.extend(first_pass_lineage_issues(baseline_documents))
    issues.extend(
        immutability_issues(
            (document for document in documents if document.kind == "report"),
            baseline_documents,
        )
    )

    unique_issues = sorted(
        set(issues),
        key=lambda issue: (issue.path, issue.pointer, issue.message),
    )
    payload = {
        "status": "ok" if not unique_issues else "failed",
        "schemas_compiled": len(schemas),
        "documents": {
            kind: sum(document.kind == kind for document in documents)
            for kind in SCHEMA_PATHS
        },
        "baseline_reports": len(baseline_documents),
        "page_text_files": len(page_texts),
        "screening_candidate_files": len(args.screening_candidates),
        "screening_records": len(screening_records),
        "issue_count": len(unique_issues),
        "issues": [issue.as_dict() for issue in unique_issues],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not unique_issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
