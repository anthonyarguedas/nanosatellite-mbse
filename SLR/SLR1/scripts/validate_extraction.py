#!/usr/bin/env python3
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
PAGE_MARKER = re.compile(r"<!--\s*PDF_PAGE:\s*([1-9][0-9]*)\s*-->")
SCREENING_SCHEMA = "slr1-screening-candidates/v2"
SCREENING_ID_PREFIXES = {
    "psr": "psr-candidate-",
    "review-searches": "review-candidate-",
    "citation-chasing": "citation-candidate-",
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


def has_recorded_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    if isinstance(value, Mapping) and "value" in value:
        return has_recorded_content(value["value"])
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
            register(
                indexes,
                "model_generation_method",
                row.get("model_generation_method_id"),
                document,
                f"/mbse_approach/model_generation_methods/{index}/model_generation_method_id",
                row,
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
            ("eps_exchanges", "eps_exchange_id", "eps_exchange"),
            ("eps_dependencies", "eps_dependency_id", "eps_dependency"),
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
        for application_index, application in enumerate(
            rows(reuse.get("report_applications"))
        ):
            register(
                indexes,
                "report_application",
                application.get("report_application_id"),
                document,
                f"/reuse/report_applications/{application_index}/report_application_id",
                application,
                issues,
            )


def build_indexes(
    documents: Iterable[Document],
) -> tuple[dict[str, dict[str, Location]], list[Issue]]:
    index_kinds = (
        "report",
        "citation",
        "model_generation_method",
        "model_artifact",
        "eps_case",
        "eps_exchange",
        "eps_dependency",
        "eps_model_bridge",
        "implementation_record",
        "input_group",
        "result_set",
        "result_output",
        "result_criterion",
        "comparator",
        "rival_explanation",
        "reviewer_derived_value",
        "rq1_claim",
        "rq2_finding",
        "rq3_activity",
        "artifact_relationship",
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


def report_reference_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    data = document.data
    mbse = data.get("mbse_approach", {})
    if isinstance(mbse, Mapping):
        for index, row in enumerate(rows(mbse.get("model_generation_methods"))):
            check_field_references(
                document,
                f"/mbse_approach/model_generation_methods/{index}",
                row,
                (("eps_case_ids", "eps_case"),),
                indexes,
                issues,
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
        "input_groups": (
            ("eps_case_id", "eps_case"),
            ("linked_model_generation_method_ids", "model_generation_method"),
            ("linked_report_reuse_record_ids", "report_reuse_record"),
            ("linked_result_output_ids", "result_output"),
            ("linked_result_criterion_ids", "result_criterion"),
            ("linked_rq3_activity_ids", "rq3_activity"),
            ("linked_report_application_ids", "report_application"),
        ),
        "rq1_claims": (
            ("linked_model_artifact_ids", "model_artifact"),
            ("linked_model_generation_method_ids", "model_generation_method"),
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
            ("model_artifact_id", "model_artifact"),
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
                (("linked_model_generation_method_ids", "model_generation_method"),),
                indexes,
                issues,
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
                check_field_references(
                    document,
                    f"{base}/tailoring_or_adaptation",
                    tailoring,
                    (("linked_implementation_record_ids", "implementation_record"),),
                    indexes,
                    issues,
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
    return issues


def cross_record_reference_issues(
    document: Document,
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
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
            check_field_references(
                document,
                "/tailoring_or_adaptation",
                tailoring,
                (("linked_implementation_record_ids", "implementation_record"),),
                indexes,
                issues,
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
                        "method-only reuse record must use not_applicable lineage_id",
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
        if application_object not in {"artifact", "artifact_and_method"}:
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
        for index, identifier in enumerate(linked_application_ids):
            if not isinstance(identifier, str):
                continue
            memberships.setdefault(identifier, []).append(document)
            location = indexes["report_application"].get(identifier)
            if location is None:
                continue
            application_object = coded_value(location.node.get("application_object"))
            if application_object not in {"artifact", "artifact_and_method"}:
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

    for identifier, location in indexes["report_application"].items():
        application_object = coded_value(location.node.get("application_object"))
        lineage_id = location.node.get("lineage_id")
        count = len(memberships.get(identifier, []))
        if (
            application_object in {"artifact", "artifact_and_method"}
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
        if application_object == "method" and count:
            issues.append(
                Issue(
                    str(location.document.path),
                    location.pointer,
                    f"method-only application {identifier!r} appears in a "
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


def family_lead_issues(document: Document) -> list[Issue]:
    issues: list[Issue] = []
    identity = document.data.get("identity", {})
    reuse = document.data.get("reuse", {})
    if not isinstance(identity, Mapping) or not isinstance(reuse, Mapping):
        return issues

    expected: set[str] = set()
    for record in rows(reuse.get("report_reuse_records")):
        candidates = coded_value(record.get("possible_related_reports_or_artifacts"))
        if isinstance(candidates, list):
            expected.update(item for item in candidates if isinstance(item, str))

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

        if "proposed" in statuses:
            for field, label in (
                ("eps_target", "EPS target"),
                ("model_artifact_id", "model artifact"),
                ("explicit_model_to_vv_bridge", "model-to-V&V bridge"),
                ("method", "V&V method"),
            ):
                if not has_recorded_content(activity.get(field)):
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

        if "downstream_physical_link" in statuses and not has_ordinary_value(
            activity.get("later_physical_link")
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/later_physical_link",
                    "downstream_physical_link milestone lacks its evidence field",
                )
            )
        if "model_to_test_closure" in statuses and not has_ordinary_value(
            activity.get("model_to_test_closure")
        ):
            issues.append(
                Issue(
                    str(document.path),
                    f"{base}/model_to_test_closure",
                    "model_to_test_closure milestone lacks its evidence field",
                )
            )

        normalized_object = coded_value(activity.get("normalized_vv_object"))
        if normalized_object in {
            "model_validation",
            "system_or_design_validation",
        } and not any(
            has_ordinary_value(
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
                    f"{normalized_object} has no linked criterion authority reason",
                )
            )
    return issues


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

    for field in (
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
    ):
        if not has_resolved_dimension(envelope.get(field)):
            deficiencies.append(f"resolved envelope dimension {field}")

    if not has_ordinary_value(design.get("reusable_core")):
        deficiencies.append("reusable core")
    variation_points = design.get("variation_points")
    tailoring_rules = design.get("tailoring_rules")
    if not has_ordinary_value(variation_points) and not has_ordinary_value(
        tailoring_rules
    ):
        deficiencies.append("variation points or explicit unchanged-use rule")
    if not has_ordinary_value(
        design.get("tailoring_operations")
    ) and not has_ordinary_value(tailoring_rules):
        deficiencies.append("tailoring or adaptation process")
    if not has_resolved_dimension(design.get("required_roles_and_skills")):
        deficiencies.append("resolved required roles and skills")
    if not has_resolved_dimension(design.get("required_tools_and_data")):
        deficiencies.append("resolved required tools and data")
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
    if not has_ordinary_value(
        tailoring.get("retained_artifact_core_or_method_steps_and_rules")
    ):
        deficiencies.append("retained core or method steps")
    changed = tailoring.get("configured_or_changed_artifact_content_or_method_steps")
    unchanged_reason = tailoring.get("reasons_for_changes_or_unchanged_use")
    if not has_ordinary_value(changed) and not has_ordinary_value(unchanged_reason):
        deficiencies.append("changed content or justified unchanged use")

    if not has_ordinary_value(result.get("post_tailoring_or_application_criterion")):
        deficiencies.append("post-application criterion")
    if not has_ordinary_value(result.get("assurance_method")):
        deficiencies.append("assurance method")
    if not has_ordinary_value(result.get("assurance_timing")):
        deficiencies.append("assurance timing")
    if not has_ordinary_value(result.get("assurance_result")):
        deficiencies.append("assurance result")
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
                        {"artifact", "artifact_and_method"},
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
                        {"method", "artifact_and_method"},
                        "method",
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
                        independent = level.startswith(("R4_", "M4_"))
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
                    {"artifact", "artifact_and_method"},
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
        else:
            issues.extend(cross_record_reference_issues(document, indexes))
        issues.extend(evidence_issues(document, indexes))
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
