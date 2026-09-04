#!/usr/bin/env python3
"""Validate prior secondary review extraction records and their links."""

from __future__ import annotations

import argparse
import json
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

from validate_extraction import normalize_quote_text, split_page_text

SLR1_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SLR1_DIR.parents[1]
SCHEMA_PATHS = (
    SLR1_DIR / "protocol-extraction.schema.json",
    SLR1_DIR / "protocol-extraction-audit.schema.json",
    SLR1_DIR / "protocol-prior-secondary-reviews.schema.json",
)
TARGET_SCHEMA_ID = "protocol-prior-secondary-reviews.schema.json"
DEFAULT_SCREENING_CANDIDATES = SLR1_DIR / "psr-candidates.json"
DEFAULT_DISCOVERY_RECEIPTS = (
    SLR1_DIR
    / "source-specific/scopus/psr-searches/corrective-002/"
    "source-union-receipt-prior_secondary_reviews.json",
    SLR1_DIR
    / "source-specific/web-of-science-core-collection/psr-searches/corrective-002/"
    "source-union-receipt-prior_secondary_reviews.json",
)
SCREENING_SCHEMA = "slr1-screening-candidates/v2"
DISCOVERY_RECEIPT_SCHEMA = "academic-search-source-union-receipt/v1"


@dataclass(frozen=True)
class Document:
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class Location:
    document: Document
    pointer: str
    node: Mapping[str, Any]


@dataclass(frozen=True)
class CandidateLocation:
    path: Path
    pointer: str
    record: Mapping[str, Any]


@dataclass(frozen=True)
class EventLocation:
    path: Path
    pointer: str
    event: Mapping[str, Any]


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


def rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def load_object(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("the document root must be an object")
    return value


def load_discovery_receipts(
    paths: Iterable[Path],
) -> tuple[dict[str, EventLocation], list[Issue]]:
    events: dict[str, EventLocation] = {}
    issues: list[Issue] = []
    for path in paths:
        try:
            payload = load_object(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            issues.append(Issue(str(path), "/", str(error)))
            continue
        if payload.get("schema_version") != DISCOVERY_RECEIPT_SCHEMA:
            issues.append(
                Issue(
                    str(path),
                    "/schema_version",
                    f"expected {DISCOVERY_RECEIPT_SCHEMA!r}",
                )
            )
        if payload.get("review_namespace") != "prior_secondary_reviews":
            issues.append(
                Issue(
                    str(path),
                    "/review_namespace",
                    "expected 'prior_secondary_reviews'",
                )
            )
        event_rows = payload.get("events")
        if not isinstance(event_rows, list):
            issues.append(Issue(str(path), "/events", "events must be an array"))
            continue
        for index, event in enumerate(event_rows):
            event_pointer = f"/events/{index}"
            if not isinstance(event, Mapping):
                issues.append(
                    Issue(str(path), event_pointer, "discovery event must be an object")
                )
                continue
            identifier = event.get("event_id")
            identifier_pointer = f"{event_pointer}/event_id"
            if not isinstance(identifier, str) or not identifier:
                issues.append(
                    Issue(str(path), identifier_pointer, "event_id must be a string")
                )
                continue
            if event.get("event_kind") != "final":
                issues.append(
                    Issue(
                        str(path),
                        f"{event_pointer}/event_kind",
                        f"event {identifier!r} is not final",
                    )
                )
                continue
            stable_record_ids = event.get("stable_record_ids")
            if not isinstance(stable_record_ids, list) or not all(
                isinstance(value, str) and value for value in stable_record_ids
            ):
                issues.append(
                    Issue(
                        str(path),
                        f"{event_pointer}/stable_record_ids",
                        "stable_record_ids must be an array of strings",
                    )
                )
                continue
            existing = events.get(identifier)
            if existing is not None:
                issues.append(
                    Issue(
                        str(path),
                        identifier_pointer,
                        f"duplicate discovery event ID {identifier!r}; first defined "
                        f"at {existing.path}{existing.pointer}",
                    )
                )
                continue
            events[identifier] = EventLocation(path, event_pointer, event)
    return events, issues


def load_screening_candidates(
    path: Path,
) -> tuple[dict[str, CandidateLocation], list[Issue]]:
    records: dict[str, CandidateLocation] = {}
    issues: list[Issue] = []
    try:
        payload = load_object(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {}, [Issue(str(path), "/", str(error))]

    if payload.get("schema_version") != SCREENING_SCHEMA:
        issues.append(
            Issue(
                str(path),
                "/schema_version",
                f"expected {SCREENING_SCHEMA!r}",
            )
        )
    if payload.get("mode") != "psr":
        issues.append(Issue(str(path), "/mode", "expected 'psr'"))

    candidate_rows = payload.get("records")
    if not isinstance(candidate_rows, list):
        issues.append(Issue(str(path), "/records", "records must be an array"))
        return records, issues
    for index, record in enumerate(candidate_rows):
        row_pointer = f"/records/{index}"
        if not isinstance(record, Mapping):
            issues.append(
                Issue(str(path), row_pointer, "screening record must be an object")
            )
            continue
        identifier = record.get("candidate_id")
        identifier_pointer = f"{row_pointer}/candidate_id"
        if not isinstance(identifier, str) or not identifier:
            issues.append(
                Issue(str(path), identifier_pointer, "candidate_id must be a string")
            )
            continue
        existing = records.get(identifier)
        if existing is not None:
            issues.append(
                Issue(
                    str(path),
                    identifier_pointer,
                    f"duplicate candidate ID {identifier!r}; first defined at "
                    f"{existing.path}{existing.pointer}",
                )
            )
            continue
        records[identifier] = CandidateLocation(path, row_pointer, record)
    return records, issues


def candidate_source_record_ids(record: Mapping[str, Any]) -> set[str]:
    identifiers: set[str] = set()
    for source in rows(record.get("source_records")):
        values = source.get("record_ids")
        if isinstance(values, list):
            identifiers.update(value for value in values if isinstance(value, str))
    return identifiers


def candidate_reference_issues(
    documents: Iterable[Document],
    candidates: Mapping[str, CandidateLocation],
) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        identifier = screening_record_id(document)
        if identifier is None:
            continue
        location = candidates.get(identifier)
        if location is None:
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/screening_record_id",
                    f"unresolved PSR candidate ID {identifier!r}",
                )
            )
            continue
        decision = location.record.get("screening_decision")
        if decision != "include_prior_secondary_review":
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/screening_record_id",
                    f"candidate {identifier!r} has screening decision {decision!r}, "
                    "expected 'include_prior_secondary_review'",
                )
            )

        identity = document.data.get("identity")
        if not isinstance(identity, Mapping):
            continue
        values = identity.get("source_record_ids")
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            continue
        actual = set(values)
        expected = candidate_source_record_ids(location.record)
        if actual != expected:
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected)
            details: list[str] = []
            if missing:
                details.append(f"missing {missing!r}")
            if unexpected:
                details.append(f"unexpected {unexpected!r}")
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/source_record_ids",
                    "source_record_ids do not match the candidate: "
                    + ", ".join(details),
                )
            )
    return issues


def event_record_ids(event: Mapping[str, Any]) -> set[str]:
    values = event.get("stable_record_ids")
    if not isinstance(values, list):
        return set()
    return {value for value in values if isinstance(value, str)}


def discovery_event_reference_issues(
    documents: Iterable[Document],
    events: Mapping[str, EventLocation],
) -> list[Issue]:
    issues: list[Issue] = []
    event_records = {
        identifier: event_record_ids(location.event)
        for identifier, location in events.items()
    }
    all_receipt_records = set().union(*event_records.values()) if events else set()
    for document in documents:
        identity = document.data.get("identity")
        if not isinstance(identity, Mapping):
            continue
        source_values = identity.get("source_record_ids")
        event_values = identity.get("discovery_event_ids")
        if not isinstance(source_values, list) or not all(
            isinstance(value, str) for value in source_values
        ):
            continue
        if not isinstance(event_values, list) or not all(
            isinstance(value, str) for value in event_values
        ):
            continue
        source_ids = set(source_values)
        actual_event_ids = set(event_values)
        expected_event_ids = {
            identifier
            for identifier, record_ids in event_records.items()
            if source_ids & record_ids
        }
        if actual_event_ids != expected_event_ids:
            missing = sorted(expected_event_ids - actual_event_ids)
            unexpected = sorted(actual_event_ids - expected_event_ids)
            details: list[str] = []
            if missing:
                details.append(f"missing {missing!r}")
            if unexpected:
                details.append(f"unexpected {unexpected!r}")
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/discovery_event_ids",
                    "discovery_event_ids do not match the receipts: "
                    + ", ".join(details),
                )
            )
        missing_source_ids = sorted(source_ids - all_receipt_records)
        if missing_source_ids:
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/source_record_ids",
                    "source record IDs absent from the discovery receipts: "
                    f"{missing_source_ids!r}",
                )
            )
    return issues


def load_schemas() -> tuple[dict[str, Any], Registry]:
    resources: list[tuple[str, Resource[Any]]] = []
    target: dict[str, Any] | None = None
    for path in SCHEMA_PATHS:
        schema = load_object(path)
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str) or not schema_id:
            raise ValueError(f"schema has no $id: {path}")
        Draft202012Validator.check_schema(schema)
        resources.append((schema_id, Resource.from_contents(schema)))
        if schema_id == TARGET_SCHEMA_ID:
            target = schema
    if target is None:
        raise ValueError(f"target schema {TARGET_SCHEMA_ID!r} was not loaded")
    return target, Registry().with_resources(resources)


def schema_issues(
    documents: Iterable[Document],
    schema: Mapping[str, Any],
    registry: Registry,
) -> list[Issue]:
    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=FormatChecker(),
    )
    issues: list[Issue] = []
    for document in documents:
        errors = sorted(
            validator.iter_errors(document.data),
            key=lambda item: (
                tuple(f"{type(part).__name__}:{part}" for part in item.absolute_path),
                item.message,
            ),
        )
        for error in errors:
            error_pointer = ""
            for part in error.absolute_path:
                error_pointer = pointer(error_pointer, part)
            issues.append(
                Issue(str(document.path), error_pointer or "/", error.message)
            )
    return issues


def identity_id(document: Document, field: str) -> str | None:
    identity = document.data.get("identity")
    if not isinstance(identity, Mapping):
        return None
    value = identity.get(field)
    return value if isinstance(value, str) and value else None


def report_id(document: Document) -> str | None:
    return identity_id(document, "report_id")


def screening_record_id(document: Document) -> str | None:
    return identity_id(document, "screening_record_id")


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
    existing = indexes[kind].get(identifier)
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


def build_indexes(
    documents: Iterable[Document],
) -> tuple[dict[str, dict[str, Location]], list[Issue]]:
    indexes = {
        kind: {}
        for kind in (
            "report",
            "citation",
            "verification_pass",
            "source_route",
            "search_date",
            "reported_count",
        )
    }
    issues: list[Issue] = []
    for document in documents:
        data = document.data
        identity = data.get("identity")
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
            for index, row in enumerate(rows(identity.get("verification_passes"))):
                register(
                    indexes,
                    "verification_pass",
                    row.get("audit_id"),
                    document,
                    f"/identity/verification_passes/{index}/audit_id",
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

        methods = data.get("review_methods")
        if isinstance(methods, Mapping):
            for index, row in enumerate(
                rows(methods.get("searched_sources_and_routes"))
            ):
                register(
                    indexes,
                    "source_route",
                    row.get("source_route_id"),
                    document,
                    "/review_methods/searched_sources_and_routes/"
                    f"{index}/source_route_id",
                    row,
                    issues,
                )

        scope = data.get("scope_and_currency")
        if isinstance(scope, Mapping):
            for index, row in enumerate(rows(scope.get("review_search_dates"))):
                register(
                    indexes,
                    "search_date",
                    row.get("search_date_id"),
                    document,
                    f"/scope_and_currency/review_search_dates/{index}/search_date_id",
                    row,
                    issues,
                )
            for index, row in enumerate(rows(scope.get("reported_counts"))):
                register(
                    indexes,
                    "reported_count",
                    row.get("reported_count_id"),
                    document,
                    f"/scope_and_currency/reported_counts/{index}/reported_count_id",
                    row,
                    issues,
                )
    return indexes, issues


def matching_report_id_issues(documents: Iterable[Document]) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        identifier = report_id(document)
        if identifier is None:
            continue
        identity = document.data.get("identity")
        if isinstance(identity, Mapping):
            for index, row in enumerate(rows(identity.get("verification_passes"))):
                if row.get("report_id") != identifier:
                    issues.append(
                        Issue(
                            str(document.path),
                            f"/identity/verification_passes/{index}/report_id",
                            f"verification pass report_id must equal {identifier!r}",
                        )
                    )
        for index, row in enumerate(rows(document.data.get("citations"))):
            if row.get("report_id") != identifier:
                issues.append(
                    Issue(
                        str(document.path),
                        f"/citations/{index}/report_id",
                        f"citation report_id must equal {identifier!r}",
                    )
                )
    return issues


def source_citation_issues(documents: Iterable[Document]) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        identity = document.data.get("identity")
        if not isinstance(identity, Mapping):
            continue
        source_value = identity.get("source_file_path")
        if not isinstance(source_value, str):
            continue
        source_path = Path(source_value)
        resolved = (
            source_path if source_path.is_absolute() else REPOSITORY_ROOT / source_path
        )
        if not resolved.is_file():
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/source_file_path",
                    f"source file does not resolve to a file: {source_value}",
                )
            )
            continue
        try:
            pages = split_page_text(resolved.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            issues.append(
                Issue(
                    str(document.path),
                    "/identity/source_file_path",
                    f"cannot load frozen page text: {error}",
                )
            )
            continue
        for index, citation in enumerate(rows(document.data.get("citations"))):
            base = f"/citations/{index}"
            page = citation.get("page")
            if not isinstance(page, int) or page not in pages:
                issues.append(
                    Issue(
                        str(document.path),
                        f"{base}/page",
                        f"cited page {page!r} is absent from frozen page text",
                    )
                )
                continue
            if "graphic" in citation or "graphic_quote_description" in citation:
                continue
            quote = citation.get("quote")
            if not isinstance(quote, str):
                continue
            if normalize_quote_text(quote) not in normalize_quote_text(pages[page]):
                issues.append(
                    Issue(
                        str(document.path),
                        f"{base}/quote",
                        "normalized quote does not occur on the cited page",
                    )
                )
    return issues


def citation_reference_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []

    def visit(document: Document, node: Any, base: str = "") -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                child_pointer = pointer(base, key)
                if key == "citation_ids" and isinstance(value, list):
                    for index, identifier in enumerate(value):
                        if not isinstance(identifier, str):
                            continue
                        reference_pointer = pointer(child_pointer, index)
                        location = indexes["citation"].get(identifier)
                        if location is None:
                            issues.append(
                                Issue(
                                    str(document.path),
                                    reference_pointer,
                                    f"unresolved citation ID {identifier!r}",
                                )
                            )
                        elif location.document != document:
                            issues.append(
                                Issue(
                                    str(document.path),
                                    reference_pointer,
                                    f"citation ID {identifier!r} belongs to another "
                                    "extraction",
                                )
                            )
                visit(document, value, child_pointer)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                visit(document, value, pointer(base, index))

    for document in documents:
        visit(document, document.data)
    return issues


def source_route_reference_issues(
    documents: Iterable[Document],
    indexes: Mapping[str, Mapping[str, Location]],
) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents:
        scope = document.data.get("scope_and_currency")
        if not isinstance(scope, Mapping):
            continue
        for date_index, row in enumerate(rows(scope.get("review_search_dates"))):
            references = row.get("source_route_ids")
            if not isinstance(references, list):
                continue
            for reference_index, identifier in enumerate(references):
                if not isinstance(identifier, str):
                    continue
                reference_pointer = (
                    f"/scope_and_currency/review_search_dates/{date_index}/"
                    f"source_route_ids/{reference_index}"
                )
                location = indexes["source_route"].get(identifier)
                if location is None:
                    issues.append(
                        Issue(
                            str(document.path),
                            reference_pointer,
                            f"unresolved source route ID {identifier!r}",
                        )
                    )
                elif location.document != document:
                    issues.append(
                        Issue(
                            str(document.path),
                            reference_pointer,
                            f"source route ID {identifier!r} belongs to another "
                            "extraction",
                        )
                    )
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extraction",
        action="append",
        type=Path,
        default=[],
        help="prior secondary review extraction JSON file",
    )
    parser.add_argument(
        "--screening-candidates",
        type=Path,
        default=DEFAULT_SCREENING_CANDIDATES,
        help="PSR screening candidate JSON file",
    )
    parser.add_argument(
        "--discovery-receipt",
        action="append",
        type=Path,
        default=None,
        help="authoritative final source-union receipt; repeat for each source",
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
        schema, registry = load_schemas()
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, indent=2))
        return 1

    if not args.schemas_only and not args.extraction:
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": "provide --extraction or use --schemas-only",
                },
                indent=2,
            )
        )
        return 2

    documents: list[Document] = []
    issues: list[Issue] = []
    for path in args.extraction:
        try:
            documents.append(Document(path, load_object(path)))
        except (OSError, ValueError, json.JSONDecodeError) as error:
            issues.append(Issue(str(path), "/", str(error)))

    candidates: dict[str, CandidateLocation] = {}
    events: dict[str, EventLocation] = {}
    discovery_receipts: tuple[Path, ...] | list[Path] = ()
    if documents:
        candidates, candidate_load_issues = load_screening_candidates(
            args.screening_candidates
        )
        issues.extend(candidate_load_issues)
        discovery_receipts = args.discovery_receipt or DEFAULT_DISCOVERY_RECEIPTS
        events, receipt_load_issues = load_discovery_receipts(discovery_receipts)
        issues.extend(receipt_load_issues)

    issues.extend(schema_issues(documents, schema, registry))
    indexes, index_issues = build_indexes(documents)
    issues.extend(index_issues)
    issues.extend(matching_report_id_issues(documents))
    issues.extend(source_citation_issues(documents))
    issues.extend(citation_reference_issues(documents, indexes))
    issues.extend(source_route_reference_issues(documents, indexes))
    issues.extend(candidate_reference_issues(documents, candidates))
    issues.extend(discovery_event_reference_issues(documents, events))

    unique_issues = sorted(
        set(issues),
        key=lambda issue: (issue.path, issue.pointer, issue.message),
    )
    payload = {
        "status": "ok" if not unique_issues else "failed",
        "schemas_compiled": len(SCHEMA_PATHS),
        "extractions": len(documents),
        "screening_candidates": len(candidates),
        "discovery_receipts": len(discovery_receipts),
        "discovery_events": len(events),
        "issue_count": len(unique_issues),
        "issues": [issue.as_dict() for issue in unique_issues],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not unique_issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
