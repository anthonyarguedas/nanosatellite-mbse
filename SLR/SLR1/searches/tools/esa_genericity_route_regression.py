#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression checks for ESA relation-free G/C1 candidates and optional R tags.

The fixture adapter deliberately evaluates joined metadata once and every
attachment separately. It has no path that concatenates metadata with an
attachment or one attachment with another.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from concept_matcher import ConceptMatcher, MatcherError, atomic_write_json, load_json, sha256_file


class RouteFixtureError(RuntimeError):
    """A route fixture is malformed."""


def _genericity(result: dict[str, Any]) -> bool:
    """Return the optional independent-relation tag."""
    return bool(result["stream_b_genericity_relation_qualified"])


def _candidate(result: dict[str, Any]) -> bool:
    """Return relation-free G/C1 candidate status."""
    return bool(result["stream_b_genericity"])


def _active_artifacts(result: dict[str, Any]) -> set[str]:
    return {item["artifact_id"] for item in result["genericity_artifact_matches"]}


def _evaluate_route_fixture(matcher: ConceptMatcher, fixture: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    routes = fixture.get("routes")
    expected = fixture.get("expected")
    if not isinstance(routes, dict) or not isinstance(expected, dict):
        raise RouteFixtureError("route fixture requires routes and expected objects")
    metadata = matcher.match_fields(routes.get("joined_metadata", {}))
    attachment = matcher.match_fields(routes.get("attachment_text", {}))
    observed = {
        "joined_metadata": _genericity(metadata),
        "attachment_text": _genericity(attachment),
        "union": _genericity(metadata) or _genericity(attachment),
        "candidate_joined_metadata": _candidate(metadata),
        "candidate_attachment_text": _candidate(attachment),
        "candidate_union": _candidate(metadata) or _candidate(attachment),
        "active_artifacts": sorted(_active_artifacts(metadata) | _active_artifacts(attachment)),
    }
    errors: list[str] = []
    for key in (
        "joined_metadata", "attachment_text", "union",
        "candidate_joined_metadata", "candidate_attachment_text", "candidate_union",
    ):
        if key in expected and observed[key] != bool(expected[key]):
            errors.append(f"{key} expected {expected[key]!r}, got {observed[key]!r}")
    if "active_artifacts" in expected and observed["active_artifacts"] != sorted(expected["active_artifacts"]):
        errors.append(
            f"active_artifacts expected {sorted(expected['active_artifacts'])!r}, "
            f"got {observed['active_artifacts']!r}"
        )
    return observed, errors


def _evaluate_attachment_fixture(
    matcher: ConceptMatcher, fixture: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    metadata_fields = fixture.get("joined_metadata")
    attachments = fixture.get("attachments")
    expected = fixture.get("expected")
    if not isinstance(metadata_fields, dict) or not isinstance(attachments, list) or not isinstance(expected, dict):
        raise RouteFixtureError("attachment fixture requires joined_metadata, attachments, and expected")
    metadata = matcher.match_fields(metadata_fields)
    attachment_results: list[dict[str, Any]] = []
    for attachment in attachments:
        if not isinstance(attachment, dict) or not isinstance(attachment.get("fields"), dict):
            raise RouteFixtureError("each attachment requires its own fields object")
        attachment_results.append(matcher.match_fields(attachment["fields"]))
    observed = {
        "metadata": _genericity(metadata),
        "attachment": any(_genericity(item) for item in attachment_results),
        "candidate_metadata": _candidate(metadata),
        "candidate_attachment": any(_candidate(item) for item in attachment_results),
    }
    observed["union"] = observed["metadata"] or observed["attachment"]
    observed["candidate_union"] = observed["candidate_metadata"] or observed["candidate_attachment"]
    errors = [
        f"{key} expected {expected[key]!r}, got {observed[key]!r}"
        for key in (
            "metadata", "attachment", "union",
            "candidate_metadata", "candidate_attachment", "candidate_union",
        )
        if key in expected and observed[key] != bool(expected[key])
    ]
    return observed, errors


def run(dictionary_path: Path, fixture_paths: list[Path]) -> dict[str, Any]:
    matcher = ConceptMatcher.from_path(dictionary_path)
    cases: list[dict[str, Any]] = []
    failed = 0
    for fixture_path in fixture_paths:
        document = load_json(fixture_path)
        fixtures = document.get("fixtures") if isinstance(document, dict) else None
        if not isinstance(fixtures, list) or not fixtures:
            raise RouteFixtureError(f"fixture document has no fixtures: {fixture_path}")
        for fixture in fixtures:
            if not isinstance(fixture, dict) or not isinstance(fixture.get("id"), str):
                raise RouteFixtureError(f"fixture lacks an ID: {fixture_path}")
            if "routes" in fixture:
                observed, errors = _evaluate_route_fixture(matcher, fixture)
            else:
                observed, errors = _evaluate_attachment_fixture(matcher, fixture)
            failed += bool(errors)
            cases.append({
                "id": fixture["id"],
                "fixture_file": fixture_path.name,
                "passed": not errors,
                "errors": errors,
                "observed": observed,
            })
    return {
        "status": "passed" if not failed else "failed",
        "classification": "synthetic_regression_not_candidate_search",
        "screening_prohibited": True,
        "fixture_count": len(cases),
        "passed": len(cases) - failed,
        "failed": failed,
        "dictionary_sha256": sha256_file(dictionary_path),
        "matcher_sha256": sha256_file(Path(__file__).with_name("concept_matcher.py")),
        "fixture_sha256": {path.name: sha256_file(path) for path in fixture_paths},
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Test isolated ESA genericity routes and attachments")
    parser.add_argument("--dictionary", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, nargs="+", type=Path)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run(args.dictionary.resolve(), [path.resolve() for path in args.fixtures])
    except (MatcherError, RouteFixtureError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "failure", "reason": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    atomic_write_json(args.output_path.resolve(), result)
    print(json.dumps({key: result[key] for key in ("status", "fixture_count", "passed", "failed")}))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
