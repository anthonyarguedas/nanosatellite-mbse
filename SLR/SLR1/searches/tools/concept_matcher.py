#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic P/E/M/G/C1/R/T and optional O/V matcher for the SLR1 search.

The implementation intentionally performs no stemming or implicit wildcard
expansion.  Its dictionary supplies every accepted form.  Every hit is retained
with field-level provenance, and all forms—including acronyms—use standalone
Unicode word boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from typing import Any, Iterable


class MatcherError(RuntimeError):
    """Dictionary, fixture, or input data are invalid."""


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._suppressed_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"script", "style", "noscript"}:
            self._suppressed_depth += 1
        elif tag.casefold() in {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style", "noscript"}:
            self._suppressed_depth = max(0, self._suppressed_depth - 1)
        elif tag.casefold() in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._suppressed_depth:
            self.parts.append(data)


def strip_html(value: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html.unescape(value))
        parser.close()
        return " ".join(parser.parts)
    except (UnicodeError, ValueError):
        return html.unescape(value)


def normalize_text(value: Any) -> str:
    """Apply the exact normalization contract frozen in the dictionary."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value if item is not None)
    elif isinstance(value, dict):
        value = " ".join(str(item) for item in value.values() if item is not None)
    text = strip_html(str(value))
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(" " if character == "-" or unicodedata.category(character) == "Pd" else character for character in text)
    return " ".join(text.split())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        json.dump(value, temporary, indent=2, ensure_ascii=False, sort_keys=False)
        temporary.write("\n")
    temporary_path.replace(path)


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise MatcherError(f"cannot read JSON {path}: {error}") from error


def _pattern_for(normalized_form: str) -> re.Pattern[str]:
    if not normalized_form:
        raise MatcherError("dictionary form normalizes to an empty string")
    pieces = [re.escape(piece) for piece in normalized_form.split(" ")]
    phrase = r"\s+".join(pieces)
    return re.compile(rf"(?<!\w){phrase}(?!\w)", re.UNICODE)


class ConceptMatcher:
    def __init__(self, dictionary: dict[str, Any]) -> None:
        if not isinstance(dictionary, dict) or not isinstance(dictionary.get("concepts"), dict):
            raise MatcherError("dictionary must contain a concepts object")
        self.dictionary = dictionary
        self.compiled: dict[str, list[dict[str, Any]]] = {}
        seen_ids: set[str] = set()
        for concept, definition in dictionary["concepts"].items():
            if not isinstance(definition, dict) or not isinstance(definition.get("terms"), list):
                raise MatcherError(f"concept {concept!r} lacks a terms array")
            compiled_terms: list[dict[str, Any]] = []
            for term in definition["terms"]:
                if not isinstance(term, dict) or not isinstance(term.get("id"), str):
                    raise MatcherError(f"concept {concept!r} has an invalid term")
                term_id = term["id"]
                if term_id in seen_ids:
                    raise MatcherError(f"duplicate dictionary term id: {term_id}")
                seen_ids.add(term_id)
                forms = term.get("forms")
                if not isinstance(forms, list) or not forms or not all(isinstance(item, str) for item in forms):
                    raise MatcherError(f"term {term_id!r} has no valid forms")
                normalized_forms: dict[str, str] = {}
                for source_form in forms:
                    normalized_forms.setdefault(normalize_text(source_form), source_form)
                compiled_terms.append(
                    {
                        "term_id": term_id,
                        "forms": [
                            {
                                "source_form": source_form,
                                "normalized_form": normalized_form,
                                "pattern": _pattern_for(normalized_form),
                            }
                            for normalized_form, source_form in normalized_forms.items()
                        ],
                    }
                )
            self.compiled[str(concept)] = compiled_terms

        recall = dictionary.get("genericity_recall")
        artifacts = recall.get("artifacts") if isinstance(recall, dict) else None
        if not isinstance(artifacts, list) or not artifacts:
            raise MatcherError("dictionary must contain genericity_recall.artifacts")
        self.genericity_artifacts: list[dict[str, Any]] = []
        seen_artifact_ids: set[str] = set()
        for artifact in artifacts:
            artifact_id = artifact.get("id") if isinstance(artifact, dict) else None
            cluster = artifact.get("cluster") if isinstance(artifact, dict) else None
            components = artifact.get("all_of") if isinstance(artifact, dict) else None
            if not isinstance(artifact_id, str) or not artifact_id or artifact_id in seen_artifact_ids:
                raise MatcherError("genericity artifact IDs must be unique non-empty strings")
            if cluster not in {"G1", "G2", "C1"} or not isinstance(components, list) or not components:
                raise MatcherError(f"genericity artifact {artifact_id!r} is incomplete")
            seen_artifact_ids.add(artifact_id)
            compiled_components: list[dict[str, Any]] = []
            for component in components:
                component_id = component.get("id") if isinstance(component, dict) else None
                forms = component.get("forms") if isinstance(component, dict) else None
                if not isinstance(component_id, str) or not isinstance(forms, list) or not forms:
                    raise MatcherError(f"genericity artifact {artifact_id!r} has an invalid component")
                normalized_forms: dict[str, str] = {}
                for source_form in forms:
                    if not isinstance(source_form, str):
                        raise MatcherError(f"genericity artifact {artifact_id!r} has a non-string form")
                    normalized_forms.setdefault(normalize_text(source_form), source_form)
                compiled_components.append({
                    "component_id": component_id,
                    "forms": [
                        {
                            "source_form": source_form,
                            "normalized_form": normalized_form,
                            "pattern": _pattern_for(normalized_form),
                        }
                        for normalized_form, source_form in normalized_forms.items()
                    ],
                })
            self.genericity_artifacts.append({
                "artifact_id": artifact_id, "cluster": cluster, "components": compiled_components
            })

    @classmethod
    def from_path(cls, path: Path) -> "ConceptMatcher":
        value = load_json(path)
        if not isinstance(value, dict):
            raise MatcherError("dictionary root must be an object")
        return cls(value)

    def match_fields(self, fields: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(fields, dict):
            raise MatcherError("fields must be an object")
        normalized_fields = {str(field): normalize_text(value) for field, value in fields.items()}
        field_hits: dict[str, dict[str, list[dict[str, Any]]]] = {}
        concept_term_ids: dict[str, set[str]] = {concept: set() for concept in self.compiled}

        for field, normalized in normalized_fields.items():
            if not normalized:
                continue
            for concept, terms in self.compiled.items():
                hits: list[dict[str, Any]] = []
                for term in terms:
                    matched_form: dict[str, Any] | None = None
                    occurrences: list[dict[str, Any]] = []
                    for form in term["forms"]:
                        matches = list(form["pattern"].finditer(normalized))
                        if matches:
                            matched_form = form
                            occurrences.extend(
                                {
                                    "dictionary_form": form["source_form"],
                                    "normalized_form": form["normalized_form"],
                                    "start": match.start(),
                                    "end": match.end(),
                                }
                                for match in matches
                            )
                    if matched_form is not None:
                        hits.append(
                            {
                                "term_id": term["term_id"],
                                "dictionary_form": matched_form["source_form"],
                                "normalized_form": matched_form["normalized_form"],
                                "occurrences": occurrences,
                                "occurrence_count": len(occurrences),
                            }
                        )
                        concept_term_ids[concept].add(term["term_id"])
                if hits:
                    field_hits.setdefault(field, {})[concept] = hits

        relation_occurrences = [
            {"field": field, "term_id": hit["term_id"], **occurrence}
            for field, concepts in field_hits.items()
            for hit in concepts.get("R", [])
            for occurrence in hit["occurrences"]
        ]
        genericity_artifact_matches: list[dict[str, Any]] = []
        for artifact in self.genericity_artifacts:
            component_groups: list[list[dict[str, Any]]] = []
            for component in artifact["components"]:
                component_hits: list[dict[str, Any]] = []
                for field, normalized in normalized_fields.items():
                    for form in component["forms"]:
                        component_hits.extend(
                            {
                                "field": field,
                                "component_id": component["component_id"],
                                "dictionary_form": form["source_form"],
                                "normalized_form": form["normalized_form"],
                                "start": match.start(),
                                "end": match.end(),
                            }
                            for match in form["pattern"].finditer(normalized)
                        )
                component_groups.append(component_hits)
            if not all(component_groups):
                continue
            component_occurrences = [hit for group in component_groups for hit in group]
            independent_relations = [
                relation
                for relation in relation_occurrences
                if not any(
                    relation["field"] == component["field"]
                    and relation["start"] < component["end"]
                    and component["start"] < relation["end"]
                    for component in component_occurrences
                )
            ]
            qualifies = bool(independent_relations)
            genericity_artifact_matches.append({
                "artifact_id": artifact["artifact_id"],
                "cluster": artifact["cluster"],
                "component_hits": component_groups,
                "independent_relation_hits": independent_relations,
                "qualifies_with_independent_relation": qualifies,
            })
            concept_term_ids.setdefault("G", set()).add(artifact["artifact_id"])

        concepts_present = [concept for concept in self.compiled if concept_term_ids[concept]]
        p_present = bool(concept_term_ids.get("P"))
        e_present = bool(concept_term_ids.get("E"))
        m_present = bool(concept_term_ids.get("M"))
        t_present = bool(concept_term_ids.get("T"))
        stream_b_core = p_present and m_present
        active_genericity_artifacts = [item["artifact_id"] for item in genericity_artifact_matches]
        active_g_artifacts = [
            item["artifact_id"] for item in genericity_artifact_matches if item["cluster"] in {"G1", "G2"}
        ]
        active_c1_artifacts = [
            item["artifact_id"] for item in genericity_artifact_matches if item["cluster"] == "C1"
        ]
        relation_qualified_genericity_artifacts = [
            item["artifact_id"]
            for item in genericity_artifact_matches
            if item["qualifies_with_independent_relation"]
        ]
        stream_b_g = p_present and bool(active_g_artifacts)
        stream_b_c1 = p_present and bool(active_c1_artifacts)
        stream_b_genericity = stream_b_g or stream_b_c1
        stream_b_genericity_relation_qualified = p_present and bool(relation_qualified_genericity_artifacts)
        stream_b = stream_b_core or stream_b_genericity
        return {
            "concepts_present": concepts_present,
            "concept_term_ids": {
                concept: sorted(term_ids) for concept, term_ids in concept_term_ids.items() if term_ids
            },
            "stream_a": p_present and e_present and m_present,
            "stream_b": stream_b,
            "stream_b_core": stream_b_core,
            "stream_b_g": stream_b_g,
            "stream_b_c1": stream_b_c1,
            "stream_b_genericity": stream_b_genericity,
            "stream_b_genericity_relation_qualified": stream_b_genericity_relation_qualified,
            "stream_b_tailoring_tag": stream_b_core and t_present,
            "g_eps_explicit": e_present and stream_b_g,
            "c1_eps_explicit": e_present and stream_b_c1,
            "genericity_eps_explicit": e_present and stream_b_genericity,
            "genericity_artifact_matches": genericity_artifact_matches,
            "active_genericity_artifact_ids": active_genericity_artifacts,
            "active_g_artifact_ids": active_g_artifacts,
            "active_c1_artifact_ids": active_c1_artifacts,
            "relation_qualified_genericity_artifact_ids": relation_qualified_genericity_artifacts,
            "normalized_fields": normalized_fields,
            "field_hits": field_hits,
        }


def _field_term_ids(result: dict[str, Any], field: str) -> set[str]:
    return {
        hit["term_id"]
        for hits in result.get("field_hits", {}).get(field, {}).values()
        for hit in hits
    }


def run_fixtures(matcher: ConceptMatcher, fixture_path: Path) -> dict[str, Any]:
    fixture_document = load_json(fixture_path)
    fixtures = fixture_document.get("fixtures") if isinstance(fixture_document, dict) else None
    if not isinstance(fixtures, list) or not fixtures:
        raise MatcherError("fixture document has no fixtures")
    failures: list[dict[str, Any]] = []
    case_results: list[dict[str, Any]] = []

    for fixture in fixtures:
        fixture_id = str(fixture.get("id", "")) if isinstance(fixture, dict) else ""
        fields = fixture.get("fields") if isinstance(fixture, dict) else None
        expected = fixture.get("expected") if isinstance(fixture, dict) else None
        if not fixture_id or not isinstance(fields, dict) or not isinstance(expected, dict):
            raise MatcherError("each fixture requires id, fields, and expected")
        actual = matcher.match_fields(fields)
        errors: list[str] = []
        actual_concepts = set(actual["concepts_present"])
        expected_present = set(expected.get("concepts_present", []))
        expected_absent = set(expected.get("concepts_absent", []))
        if not expected_present.issubset(actual_concepts):
            errors.append(f"missing concepts {sorted(expected_present - actual_concepts)}")
        if expected_absent & actual_concepts:
            errors.append(f"unexpected concepts {sorted(expected_absent & actual_concepts)}")
        for key in (
            "stream_a", "stream_b", "stream_b_core", "stream_b_g", "stream_b_c1",
            "stream_b_genericity", "stream_b_genericity_relation_qualified", "stream_b_tailoring_tag",
            "g_eps_explicit", "c1_eps_explicit", "genericity_eps_explicit"
        ):
            if key in expected and bool(actual[key]) != bool(expected[key]):
                errors.append(f"{key} expected {expected[key]!r}, got {actual[key]!r}")
        expected_field_ids = expected.get("field_term_ids", {})
        if not isinstance(expected_field_ids, dict):
            raise MatcherError(f"fixture {fixture_id!r} field_term_ids must be an object")
        for field, term_ids in expected_field_ids.items():
            wanted = set(term_ids)
            observed = _field_term_ids(actual, str(field))
            if not wanted.issubset(observed):
                errors.append(
                    f"field {field!r} missing term ids {sorted(wanted - observed)}; observed {sorted(observed)}"
                )
        case_result = {
            "id": fixture_id,
            "passed": not errors,
            "errors": errors,
            "concepts_present": actual["concepts_present"],
            "stream_a": actual["stream_a"],
            "stream_b": actual["stream_b"],
            "stream_b_core": actual["stream_b_core"],
            "stream_b_g": actual["stream_b_g"],
            "stream_b_c1": actual["stream_b_c1"],
            "stream_b_genericity": actual["stream_b_genericity"],
            "stream_b_genericity_relation_qualified": actual["stream_b_genericity_relation_qualified"],
            "stream_b_tailoring_tag": actual["stream_b_tailoring_tag"],
            "g_eps_explicit": actual["g_eps_explicit"],
            "c1_eps_explicit": actual["c1_eps_explicit"],
            "genericity_eps_explicit": actual["genericity_eps_explicit"],
            "field_term_ids": {
                field: sorted(_field_term_ids(actual, field)) for field in actual.get("field_hits", {})
            },
        }
        case_results.append(case_result)
        if errors:
            failures.append(case_result)

    return {
        "status": "passed" if not failures else "failed",
        "fixture_count": len(fixtures),
        "passed": len(fixtures) - len(failures),
        "failed": len(failures),
        "cases": case_results,
    }


def _records_from_document(document: Any) -> Iterable[dict[str, Any]]:
    if isinstance(document, list):
        records = document
    elif isinstance(document, dict) and isinstance(document.get("results"), list):
        records = document["results"]
    else:
        records = [document]
    for record in records:
        if not isinstance(record, dict):
            raise MatcherError("input record must be an object")
        yield record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministically match the frozen SLR1 concept dictionary")
    parser.add_argument("--dictionary", required=True, type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    test_parser = subparsers.add_parser("test", help="run synthetic field-level regression fixtures")
    test_parser.add_argument("--fixtures", required=True, type=Path)
    test_parser.add_argument("--output-path", type=Path)

    match_parser = subparsers.add_parser("match-json", help="match JSON records without source harvesting")
    match_parser.add_argument("--input", required=True, type=Path)
    match_parser.add_argument("--output-path", required=True, type=Path)
    match_parser.add_argument(
        "--field",
        action="append",
        required=True,
        help="record key to search; repeat for each exact top-level field",
    )
    match_parser.add_argument("--id-field", default="id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        dictionary_path = args.dictionary.expanduser().resolve()
        matcher = ConceptMatcher.from_path(dictionary_path)
        if args.command == "test":
            report = run_fixtures(matcher, args.fixtures.expanduser().resolve())
            report["dictionary_path"] = str(dictionary_path)
            report["dictionary_sha256"] = sha256_file(dictionary_path)
            report["matcher_sha256"] = sha256_file(Path(__file__).resolve())
            if args.output_path:
                atomic_write_json(args.output_path.expanduser().resolve(), report)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["status"] == "passed" else 1

        input_path = args.input.expanduser().resolve()
        document = load_json(input_path)
        matched_records: list[dict[str, Any]] = []
        for index, record in enumerate(_records_from_document(document), start=1):
            fields = {field: record.get(field) for field in args.field}
            matched_records.append(
                {
                    "record_id": str(record.get(args.id_field, index)),
                    "match": matcher.match_fields(fields),
                }
            )
        output = {
            "dictionary_sha256": sha256_file(dictionary_path),
            "matcher_sha256": sha256_file(Path(__file__).resolve()),
            "input_sha256": sha256_file(input_path),
            "record_count": len(matched_records),
            "records": matched_records,
        }
        atomic_write_json(args.output_path.expanduser().resolve(), output)
        print(json.dumps({"status": "success", "record_count": len(matched_records)}, ensure_ascii=False))
        return 0
    except MatcherError as error:
        print(json.dumps({"status": "failure", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
