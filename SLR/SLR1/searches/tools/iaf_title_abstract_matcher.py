#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic IAF title/abstract route wrapper for SLR v1.6.

Production ``match-json`` input is the official IAF adapter's top-level
``results`` envelope. Every record is bound to its stable ``paperId`` before
only ``title`` and complete public ``abstract`` values are supplied to the
shared concept matcher. The explicitly selected synthetic direct-record mode
is fixture-only. The wrapper never joins fields or reads author, affiliation,
event, publication, DOI, URL, or other metadata for concept matching. Route
tags are mechanical candidate-generation metadata, not screening or eligibility
decisions.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

ROUTE = "iaf_title_abstract"
WRAPPER_VERSION = "1.1.0-v16-iaf-title-abstract-2026-08-11"
EXPECTED_DICTIONARY_VERSION = "1.6.0-thesis-sources-2026-08-10"
ADAPTER_RESULTS_KEY = "results"
SYNTHETIC_RECORDS_KEY = "records"
ALLOWED_INPUT_KEYS = frozenset(
    {"record_id", "title", "abstract", "abstract_not_available"}
)
IDENTITY_INPUT_KEYS = frozenset({"paperId"})
TAG_KEYS = (
    "iaf_p_tag",
    "iaf_e_tag",
    "iaf_m_tag",
    "iaf_high_specificity_m_tag",
    "iaf_broad_m_plus_r_tag",
    "iaf_a_tag",
    "iaf_b_core",
    "iaf_bg1",
    "iaf_bg2",
    "iaf_g_tag",
    "iaf_bc1",
    "iaf_c1_tag",
    "iaf_r_occurrence_tag",
    "iaf_independent_r_tag",
    "iaf_t2_tag",
    "iaf_v1_tag",
    "iaf_o1_tag",
    "iaf_candidate_union",
)


class IAFTitleAbstractError(RuntimeError):
    """The IAF route input, dictionary, or fixture violates the gate contract."""


def sha256_file(path: Path) -> str:
    """Return a stable checksum without reading a whole file into memory."""
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a complete JSON artifact or leave the previous artifact intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def load_json(path: Path) -> Any:
    """Load UTF-8 JSON and convert parse failures into a gate error."""
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise IAFTitleAbstractError(f"cannot read JSON {path}: {error}") from error


def _load_matcher_module(matcher_path: Path) -> Any:
    """Load the shared matcher from an explicitly versioned local path."""
    resolved = matcher_path.resolve()
    specification = importlib.util.spec_from_file_location(
        "iaf_title_abstract_shared_matcher", resolved
    )
    if specification is None or specification.loader is None:
        raise IAFTitleAbstractError(f"cannot load shared matcher {resolved}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    for name in ("ConceptMatcher", "normalize_text"):
        if not hasattr(module, name):
            raise IAFTitleAbstractError(
                f"shared matcher {resolved} lacks required symbol {name}"
            )
    return module


def _load_dictionary(dictionary_path: Path) -> dict[str, Any]:
    dictionary = load_json(dictionary_path)
    if not isinstance(dictionary, dict):
        raise IAFTitleAbstractError("dictionary root must be an object")
    if dictionary.get("dictionary_version") != EXPECTED_DICTIONARY_VERSION:
        raise IAFTitleAbstractError(
            "IAF wrapper requires dictionary_version "
            f"{EXPECTED_DICTIONARY_VERSION!r}"
        )
    candidate_logic = dictionary.get("candidate_logic")
    scope = candidate_logic.get("scope") if isinstance(candidate_logic, dict) else ""
    if not isinstance(scope, str) or "authorized IAF title/abstract matching" not in scope:
        raise IAFTitleAbstractError(
            "dictionary does not declare authorized IAF title/abstract scope"
        )
    return dictionary


def make_matcher(dictionary_path: Path, matcher_path: Path) -> tuple[Any, Any]:
    """Return the shared matcher module and a v1.6-validated matcher instance."""
    dictionary = _load_dictionary(dictionary_path.resolve())
    module = _load_matcher_module(matcher_path.resolve())
    try:
        matcher = module.ConceptMatcher(dictionary)
    except RuntimeError as error:
        raise IAFTitleAbstractError(f"shared matcher rejected dictionary: {error}") from error
    return module, matcher


def _require_text(record: dict[str, Any], field: str, *, optional: bool) -> str | None:
    value = record.get(field)
    if value is None and optional:
        return None
    if not isinstance(value, str):
        qualifier = "optional " if optional else ""
        raise IAFTitleAbstractError(f"IAF {qualifier}{field} must be text")
    if not optional and not value.strip():
        raise IAFTitleAbstractError("IAF title must not be empty")
    return value


def _field_term_ids(match: dict[str, Any], field: str) -> list[str]:
    return sorted(
        {
            str(hit["term_id"])
            for hits in match.get("field_hits", {}).get(field, {}).values()
            for hit in hits
        }
    )


def _sanitized_field_hits(match: dict[str, Any]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Keep field/term/span provenance without serializing route text."""
    output: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for field, concepts in match.get("field_hits", {}).items():
        if field not in {"title", "abstract"}:
            raise IAFTitleAbstractError(f"shared matcher emitted an out-of-route field {field!r}")
        output[field] = {}
        for concept, hits in concepts.items():
            output[field][concept] = [
                {
                    "term_id": hit["term_id"],
                    "dictionary_form": hit["dictionary_form"],
                    "occurrences": hit["occurrences"],
                }
                for hit in hits
            ]
    return output


def _artifact_summary(match: dict[str, Any]) -> list[dict[str, Any]]:
    """Preserve artifact cluster/independent-R status without route text."""
    return sorted(
        [
            {
                "artifact_id": item["artifact_id"],
                "cluster": item["cluster"],
                "qualifies_with_independent_relation": bool(
                    item["qualifies_with_independent_relation"]
                ),
            }
            for item in match.get("genericity_artifact_matches", [])
        ],
        key=lambda item: str(item["artifact_id"]),
    )


def match_iaf_title_abstract_record(
    matcher_module: Any,
    matcher: Any,
    record: dict[str, Any],
    *,
    record_id: str,
) -> dict[str, Any]:
    """Classify exactly one IAF title/abstract route with no field concatenation."""
    if not isinstance(record, dict):
        raise IAFTitleAbstractError("each IAF route record must be an object")
    if (
        not isinstance(record_id, str)
        or not record_id.strip()
        or record_id != record_id.strip()
    ):
        raise IAFTitleAbstractError(
            "each IAF route record needs a non-empty stable record_id"
        )

    title = _require_text(record, "title", optional=False)
    abstract = _require_text(record, "abstract", optional=True)
    declared_missing = record.get("abstract_not_available")
    if declared_missing is not None and not isinstance(declared_missing, bool):
        raise IAFTitleAbstractError("abstract_not_available must be boolean when supplied")
    normalized_abstract = matcher_module.normalize_text(abstract) if abstract else ""
    inferred_missing = not normalized_abstract or normalized_abstract == "not available"
    if declared_missing is True and normalized_abstract and not inferred_missing:
        raise IAFTitleAbstractError(
            "abstract_not_available conflicts with a non-empty public abstract"
        )
    abstract_not_available = bool(declared_missing) or inferred_missing

    # Do not concatenate title/abstract: phrase boundaries remain field-local.
    match = matcher.match_fields(
        {
            "title": title,
            "abstract": None if abstract_not_available else abstract,
        }
    )
    concepts = {
        concept: set(term_ids)
        for concept, term_ids in match.get("concept_term_ids", {}).items()
    }
    p_present = bool(concepts.get("P"))
    e_present = bool(concepts.get("E"))
    m_present = bool(concepts.get("M"))
    r_present = bool(concepts.get("R"))
    try:
        high_specificity_m_present = bool(match["m_high_specificity_term_ids"])
        broad_m_plus_r_present = bool(
            p_present and match["m_broad_structured_model_term_ids"] and r_present
        )
        t2_coupling_anchor_fields = match["tailoring_coupling_anchor_fields"]
    except (KeyError, TypeError) as error:
        raise IAFTitleAbstractError(
            "shared matcher lacks the frozen M-partition or T2-coupling capability"
        ) from error
    if (
        not isinstance(t2_coupling_anchor_fields, list)
        or t2_coupling_anchor_fields != sorted(set(t2_coupling_anchor_fields))
        or not all(field in {"title", "abstract"} for field in t2_coupling_anchor_fields)
    ):
        raise IAFTitleAbstractError("shared matcher emitted invalid T2 anchor fields")
    artifacts = _artifact_summary(match)
    bg1 = p_present and any(item["cluster"] == "G1" for item in artifacts)
    bg2 = p_present and any(item["cluster"] == "G2" for item in artifacts)
    bc1 = p_present and any(item["cluster"] == "C1" for item in artifacts)
    # These direct-source-comparison subtypes are local provenance tags, not IAF
    # B1/B2 source queries and not additions to the P AND M candidate union.
    tags = {
        "iaf_p_tag": p_present,
        "iaf_e_tag": e_present,
        "iaf_m_tag": m_present,
        "iaf_high_specificity_m_tag": p_present and high_specificity_m_present,
        "iaf_broad_m_plus_r_tag": broad_m_plus_r_present,
        "iaf_a_tag": bool(match["stream_a"]),
        "iaf_b_core": bool(match["stream_b_core"]),
        "iaf_bg1": bg1,
        "iaf_bg2": bg2,
        "iaf_g_tag": bg1 or bg2,
        "iaf_bc1": bc1,
        "iaf_c1_tag": bc1,
        "iaf_r_occurrence_tag": r_present,
        "iaf_independent_r_tag": bool(
            match["stream_b_genericity_relation_qualified"]
        ),
        "iaf_t2_tag": bool(match["stream_b_tailoring_tag"]),
        "iaf_v1_tag": bool(match["v1_sensitivity_tag"]),
        "iaf_o1_tag": bool(match["o1_sensitivity_tag"]),
        "iaf_candidate_union": bool(match["stream_b"]),
    }
    if tags["iaf_a_tag"] and not tags["iaf_b_core"]:
        raise IAFTitleAbstractError("structural IAF-A subset invariant failed")
    if tags["iaf_candidate_union"] != (
        tags["iaf_b_core"] or tags["iaf_g_tag"] or tags["iaf_c1_tag"]
    ):
        raise IAFTitleAbstractError("IAF candidate-union structural invariant failed")

    ignored_input_keys = sorted(
        set(record) - ALLOWED_INPUT_KEYS - IDENTITY_INPUT_KEYS
    )
    return {
        "record_id": record_id,
        "route": ROUTE,
        "source_field_names": ["title", "abstract"],
        "field_presence": {
            "title": True,
            "abstract": not abstract_not_available,
        },
        "ignored_input_keys": ignored_input_keys,
        "abstract_not_available": abstract_not_available,
        "abstract_not_available_lead": abstract_not_available,
        "no_automatic_negative": abstract_not_available,
        "screening_performed": False,
        "t2_coupling_anchor_fields": sorted(t2_coupling_anchor_fields),
        "tags": tags,
        "active_genericity_artifacts": artifacts,
        "independent_relation_artifact_ids": sorted(
            item["artifact_id"]
            for item in artifacts
            if item["qualifies_with_independent_relation"]
        ),
        "field_term_ids": {
            field: _field_term_ids(match, field) for field in ("title", "abstract")
        },
        "field_hits": _sanitized_field_hits(match),
    }


def _validate_fixture_case(observed: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    """Require exact synthetic expectations so added hits cannot pass unnoticed."""
    errors: list[str] = []
    observed_tags = observed.get("tags")
    if not isinstance(observed_tags, dict) or set(observed_tags) != set(TAG_KEYS):
        errors.append("observed.tags must define every IAF tag exactly once")
    tags = expected.get("tags")
    if not isinstance(tags, dict) or set(tags) != set(TAG_KEYS):
        errors.append("expected.tags must define every IAF tag exactly once")
    elif isinstance(observed_tags, dict) and set(observed_tags) == set(TAG_KEYS):
        for key in TAG_KEYS:
            if not isinstance(tags[key], bool):
                errors.append(f"expected.tags.{key} must be boolean")
            elif observed_tags[key] != tags[key]:
                errors.append(
                    f"{key} expected {tags[key]!r}, got {observed['tags'][key]!r}"
                )
    for key in (
        "abstract_not_available",
        "abstract_not_available_lead",
        "no_automatic_negative",
    ):
        if not isinstance(expected.get(key), bool):
            errors.append(f"expected.{key} must be boolean")
        elif observed[key] != expected[key]:
            errors.append(f"{key} expected {expected[key]!r}, got {observed[key]!r}")
    expected_presence = expected.get("field_presence")
    if not isinstance(expected_presence, dict) or set(expected_presence) != {"title", "abstract"}:
        errors.append("expected.field_presence must define title and abstract exactly")
    else:
        for field in ("title", "abstract"):
            if not isinstance(expected_presence[field], bool):
                errors.append(f"expected.field_presence.{field} must be boolean")
            elif observed["field_presence"][field] != expected_presence[field]:
                errors.append(
                    f"field_presence.{field} expected {expected_presence[field]!r}, "
                    f"got {observed['field_presence'][field]!r}"
                )
    expected_ignored = expected.get("ignored_input_keys")
    if not isinstance(expected_ignored, list) or not all(
        isinstance(key, str) for key in expected_ignored
    ):
        errors.append("expected.ignored_input_keys must be a string list")
    elif expected_ignored != sorted(set(expected_ignored)):
        errors.append("expected.ignored_input_keys must be sorted and unique")
    elif observed["ignored_input_keys"] != expected_ignored:
        errors.append(
            "ignored_input_keys expected "
            f"{expected_ignored!r}, got {observed['ignored_input_keys']!r}"
        )
    expected_anchors = expected.get("t2_coupling_anchor_fields")
    if not isinstance(expected_anchors, list) or not all(
        field in {"title", "abstract"} for field in expected_anchors
    ):
        errors.append("expected.t2_coupling_anchor_fields must be a title/abstract list")
    elif expected_anchors != sorted(set(expected_anchors)):
        errors.append("expected.t2_coupling_anchor_fields must be sorted and unique")
    elif observed["t2_coupling_anchor_fields"] != expected_anchors:
        errors.append(
            "t2_coupling_anchor_fields expected "
            f"{expected_anchors!r}, got {observed['t2_coupling_anchor_fields']!r}"
        )
    expected_fields = expected.get("field_term_ids")
    if not isinstance(expected_fields, dict) or set(expected_fields) != {"title", "abstract"}:
        errors.append("expected.field_term_ids must define title and abstract exactly")
    else:
        for field in ("title", "abstract"):
            wanted = expected_fields[field]
            if not isinstance(wanted, list) or not all(
                isinstance(term_id, str) for term_id in wanted
            ):
                errors.append(f"field_term_ids.{field} must be a string list")
            elif wanted != sorted(set(wanted)):
                errors.append(f"field_term_ids.{field} must be sorted and unique")
            elif observed["field_term_ids"][field] != wanted:
                errors.append(
                    f"field {field!r} expected exact term ids {wanted!r}; "
                    f"got {observed['field_term_ids'][field]!r}"
                )
    for key, actual in (
        (
            "active_genericity_artifact_ids",
            [item["artifact_id"] for item in observed["active_genericity_artifacts"]],
        ),
        (
            "independent_relation_artifact_ids",
            observed["independent_relation_artifact_ids"],
        ),
    ):
        wanted = expected.get(key)
        if not isinstance(wanted, list) or not all(
            isinstance(item, str) for item in wanted
        ):
            errors.append(f"expected.{key} must be a string list")
        elif wanted != sorted(set(wanted)):
            errors.append(f"expected.{key} must be sorted and unique")
        elif actual != wanted:
            errors.append(f"{key} expected {wanted!r}, got {actual!r}")
    return errors


def run_fixtures(
    dictionary_path: Path, matcher_path: Path, fixture_path: Path
) -> dict[str, Any]:
    """Run synthetic v1.6 IAF route fixtures without harvesting any source."""
    fixture_document = load_json(fixture_path.resolve())
    if not isinstance(fixture_document, dict):
        raise IAFTitleAbstractError("fixture root must be an object")
    if fixture_document.get("dictionary_version") != EXPECTED_DICTIONARY_VERSION:
        raise IAFTitleAbstractError("fixture dictionary_version is not frozen v1.6")
    fixtures = fixture_document.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise IAFTitleAbstractError("fixture document has no fixtures")
    matcher_module, matcher = make_matcher(dictionary_path, matcher_path)
    cases: list[dict[str, Any]] = []
    failures = 0
    seen_fixture_ids: set[str] = set()
    seen_record_ids: set[str] = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            raise IAFTitleAbstractError("fixture entry must be an object")
        fixture_id = fixture.get("id")
        record = fixture.get("record")
        expected = fixture.get("expected")
        if not isinstance(fixture_id, str) or not fixture_id:
            raise IAFTitleAbstractError("fixture needs a non-empty id")
        if fixture_id in seen_fixture_ids:
            raise IAFTitleAbstractError(f"duplicate fixture id {fixture_id!r}")
        seen_fixture_ids.add(fixture_id)
        if not isinstance(record, dict) or not isinstance(expected, dict):
            raise IAFTitleAbstractError(f"fixture {fixture_id!r} needs record and expected objects")
        record_id = record.get("record_id")
        if (
            not isinstance(record_id, str)
            or not record_id.strip()
            or record_id != record_id.strip()
        ):
            raise IAFTitleAbstractError(
                f"fixture {fixture_id!r} needs a non-empty stable record_id"
            )
        if record_id in seen_record_ids:
            raise IAFTitleAbstractError(f"duplicate fixture record_id {record_id!r}")
        seen_record_ids.add(record_id)
        observed = match_iaf_title_abstract_record(
            matcher_module, matcher, record, record_id=record_id
        )
        errors = _validate_fixture_case(observed, expected)
        failures += bool(errors)
        cases.append(
            {
                "id": fixture_id,
                "passed": not errors,
                "errors": errors,
                "observed": observed,
            }
        )
    return {
        "status": "passed" if not failures else "failed",
        "classification": "synthetic_regression_not_candidate_search",
        "screening_prohibited": True,
        "candidate_records_serialized": False,
        "route": ROUTE,
        "wrapper_version": WRAPPER_VERSION,
        "dictionary_version": EXPECTED_DICTIONARY_VERSION,
        "fixture_count": len(cases),
        "passed": len(cases) - failures,
        "failed": failures,
        "dictionary_sha256": sha256_file(dictionary_path.resolve()),
        "matcher_sha256": sha256_file(matcher_path.resolve()),
        "wrapper_sha256": sha256_file(Path(__file__).resolve()),
        "fixture_sha256": sha256_file(fixture_path.resolve()),
        "cases": cases,
    }


def _validated_input_records(
    records: Any, *, id_field: str, input_mode: str
) -> list[tuple[dict[str, Any], str]]:
    """Bind every local route record to one unique, stable input identity."""
    if not isinstance(records, list):
        raise IAFTitleAbstractError(f"{input_mode} input must contain an array")
    validated: list[tuple[dict[str, Any], str]] = []
    seen_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise IAFTitleAbstractError("each input route record must be an object")
        record_id = record.get(id_field)
        if (
            not isinstance(record_id, str)
            or not record_id.strip()
            or record_id != record_id.strip()
        ):
            raise IAFTitleAbstractError(
                f"{input_mode} record {index} needs a non-empty stable {id_field}"
            )
        if record_id in seen_ids:
            raise IAFTitleAbstractError(
                f"{input_mode} contains duplicate stable {id_field} {record_id!r}"
            )
        seen_ids.add(record_id)
        validated.append((record, record_id))
    return validated


def _records_from_document(
    document: Any, *, synthetic_direct_records: bool
) -> list[tuple[dict[str, Any], str]]:
    """Accept either the adapter envelope or an explicitly selected fixture mode."""
    if not isinstance(document, dict):
        raise IAFTitleAbstractError(
            "input must be an object; production requires the IAF adapter results envelope"
        )
    if synthetic_direct_records:
        if ADAPTER_RESULTS_KEY in document:
            raise IAFTitleAbstractError(
                "synthetic direct-record mode must not contain an adapter results envelope"
            )
        if SYNTHETIC_RECORDS_KEY not in document:
            raise IAFTitleAbstractError(
                "synthetic direct-record mode requires a top-level records array"
            )
        return _validated_input_records(
            document[SYNTHETIC_RECORDS_KEY],
            id_field="record_id",
            input_mode="synthetic direct-record",
        )
    if SYNTHETIC_RECORDS_KEY in document:
        raise IAFTitleAbstractError(
            "synthetic direct records require --synthetic-direct-records"
        )
    if ADAPTER_RESULTS_KEY not in document:
        raise IAFTitleAbstractError(
            "production input requires the official IAF adapter top-level results array"
        )
    return _validated_input_records(
        document[ADAPTER_RESULTS_KEY],
        id_field="paperId",
        input_mode="IAF adapter results envelope",
    )


def match_json(
    dictionary_path: Path,
    matcher_path: Path,
    input_path: Path,
    *,
    synthetic_direct_records: bool = False,
) -> dict[str, Any]:
    """Match local adapter output only; this wrapper never harvests from IAF."""
    matcher_module, matcher = make_matcher(dictionary_path, matcher_path)
    records = _records_from_document(
        load_json(input_path.resolve()),
        synthetic_direct_records=synthetic_direct_records,
    )
    matched = [
        match_iaf_title_abstract_record(
            matcher_module, matcher, record, record_id=record_id
        )
        for record, record_id in records
    ]
    return {
        "status": "success",
        "classification": "local_route_matching_only",
        "screening_prohibited": True,
        "input_mode": (
            "synthetic_direct_records"
            if synthetic_direct_records
            else "official_iaf_adapter_results_envelope"
        ),
        "route": ROUTE,
        "wrapper_version": WRAPPER_VERSION,
        "dictionary_version": EXPECTED_DICTIONARY_VERSION,
        "dictionary_sha256": sha256_file(dictionary_path.resolve()),
        "matcher_sha256": sha256_file(matcher_path.resolve()),
        "wrapper_sha256": sha256_file(Path(__file__).resolve()),
        "input_sha256": sha256_file(input_path.resolve()),
        "record_count": len(matched),
        "records": matched,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Match only IAF title/abstract fields with the frozen v1.6 dictionary"
    )
    parser.add_argument("--dictionary", required=True, type=Path)
    parser.add_argument("--matcher", required=True, type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    test_parser = subparsers.add_parser("test", help="run synthetic route fixtures")
    test_parser.add_argument("--fixtures", required=True, type=Path)
    test_parser.add_argument("--output-path", required=True, type=Path)
    match_parser = subparsers.add_parser(
        "match-json", help="match an official IAF adapter results envelope"
    )
    match_parser.add_argument("--input", required=True, type=Path)
    match_parser.add_argument("--output-path", required=True, type=Path)
    match_parser.add_argument(
        "--synthetic-direct-records",
        action="store_true",
        help=(
            "accept only a synthetic top-level records array with record_id values; "
            "never use this fixture mode for adapter output"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "test":
            report = run_fixtures(args.dictionary, args.matcher, args.fixtures)
        else:
            report = match_json(
                args.dictionary,
                args.matcher,
                args.input,
                synthetic_direct_records=args.synthetic_direct_records,
            )
        atomic_write_json(args.output_path.resolve(), report)
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "route": report["route"],
                    "record_or_fixture_count": report.get(
                        "record_count", report.get("fixture_count")
                    ),
                    "failed": report.get("failed", 0),
                }
            )
        )
        return 0 if report["status"] in {"passed", "success"} else 1
    except (
        IAFTitleAbstractError,
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        print(json.dumps({"status": "failure", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
