#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Offline, privacy-preserving checks for the one-record WoS RIS gate.

This tool deliberately has no browser, network, query-construction, or source
navigation capability. It parses a private native RIS export, writes a private
cited-reference sidecar, and emits only hashes, counts, and booleans in its
control artifacts. The sidecar is source output and must remain outside version
control.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any, Sequence

SOURCE_LABEL = "Web of Science Core Collection"
CANONICAL_SOURCE = "web_of_science_core_collection"
REQUIRED_NATIVE_TAGS = ("AN", "DO", "TI", "AU", "PY", "AB", "WE", "CR")
REQUIRED_NORMALIZED_COLUMNS = (
    "Search source",
    "Query",
    "Rank",
    "Source total",
    "Paper ID",
    "DOI",
    "Title",
    "Authors",
    "Publication year",
    "Abstract",
)
RIS_TAG_PATTERN = re.compile(r"^([A-Z0-9]{2})  - ?(.*)$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

ATTESTATION_CONTROL_KEYS = (
    "core_collection_only",
    "editions_all",
    "topic_field",
    "english",
    "date_window",
    "no_document_type",
    "exact_search_state_recorded",
    "relevance_sort",
    "page_size_50",
    "query_exact",
)
ATTESTATION_EXPORT_KEYS = (
    "ris_other_reference_software",
    "fast_5000_not_selected",
    "range_one_to_one",
    "custom_selection_30",
    "download_completed",
    "authentication_or_login_redirect",
)


class GateError(RuntimeError):
    """Raised for a fail-closed offline gate condition."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return sha256_text(encoded)


def sequence_sha256(values: Sequence[str]) -> str:
    return json_sha256(list(values))


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def parse_ris_text(text: str) -> list[dict[str, list[str]]]:
    """Strictly parse RIS records while preserving continuation boundaries."""
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] | None = None
    current_tag: str | None = None

    for line in text.splitlines():
        if not line:
            continue
        match = RIS_TAG_PATTERN.fullmatch(line)
        if match:
            tag, value = match.groups()
            if tag == "TY":
                if current is not None:
                    raise GateError("unterminated RIS record")
                current = {}
            if current is None:
                raise GateError("RIS record does not start with TY")
            current.setdefault(tag, []).append(value)
            if tag == "ER":
                records.append(current)
                current = None
                current_tag = None
            else:
                current_tag = tag
            continue

        if current is None or current_tag is None or not line[:1].isspace():
            raise GateError("malformed RIS line")
        current[current_tag][-1] = f"{current[current_tag][-1]}\n{line.strip()}"

    if current is not None:
        raise GateError("unterminated RIS record")
    if not records:
        raise GateError("RIS contains no records")
    return records


def read_ris(path: Path) -> tuple[bytes, list[dict[str, list[str]]]]:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        raise GateError("native RIS is unavailable or not strict UTF-8") from error
    return raw, parse_ris_text(text)


def record_identifier(record: dict[str, list[str]]) -> str:
    """Return one source-native identifier without serializing it elsewhere."""
    for tag in ("AN", "UT", "ID", "M1"):
        values = record.get(tag, [])
        if not values:
            continue
        if len(values) != 1 or not values[0].strip():
            raise GateError("ambiguous or empty native identifier")
        return values[0].strip()
    raise GateError("native identifier is absent")


def tag_value_counts(records: Sequence[dict[str, list[str]]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        for tag, values in record.items():
            counts[tag] = counts.get(tag, 0) + len(values)
    return dict(sorted(counts.items()))


def required_tag_record_counts(
    records: Sequence[dict[str, list[str]]],
) -> dict[str, int]:
    return {
        tag: sum(
            any(value.strip() for value in record.get(tag, [])) for record in records
        )
        for tag in REQUIRED_NATIVE_TAGS
    }


def sidecar_payload(
    raw: bytes,
    records: Sequence[dict[str, list[str]]],
    rank_start: int,
) -> dict[str, Any]:
    if isinstance(rank_start, bool) or rank_start < 1:
        raise GateError("rank start must be a positive integer")
    identifiers = [record_identifier(record) for record in records]
    cited_reference_groups = [list(record.get("CR", [])) for record in records]
    return {
        "schema": "wos-ris-cited-reference-sidecar/v2",
        "artifact_class": "private_source_output_not_for_version_control",
        "native_sha256": sha256_bytes(raw),
        "native_byte_count": len(raw),
        "record_count": len(records),
        "ordered_paper_id_sha256": sequence_sha256(identifiers),
        "ordered_cited_references_sha256": json_sha256(cited_reference_groups),
        "records": [
            {
                "rank": rank_start + index,
                "paper_id_sha256": sha256_text(identifier),
                "cited_references": list(record.get("CR", [])),
                "cited_references_sha256": json_sha256(list(record.get("CR", []))),
            }
            for index, (record, identifier) in enumerate(zip(records, identifiers))
        ],
    }


def integrity_payload(
    raw: bytes, records: Sequence[dict[str, list[str]]]
) -> dict[str, Any]:
    return {
        "schema": "wos-ris-native-integrity/v2",
        "artifact_class": "private_control_only",
        "native_sha256": sha256_bytes(raw),
        "native_byte_count": len(raw),
        "record_count": len(records),
        "tag_value_counts": tag_value_counts(records),
        "required_tag_record_counts": required_tag_record_counts(records),
        "parse_complete": True,
    }


def ensure_private_parent(path: Path) -> None:
    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        mode = stat.S_IMODE(parent.stat().st_mode)
    except OSError as error:
        raise GateError("private output directory is unavailable") from error
    if mode & 0o077:
        raise GateError("private output directory is not owner-only")


def write_private_json(path: Path, payload: dict[str, Any]) -> str:
    """Write an owner-only, no-clobber JSON artifact without echoing its path."""
    ensure_private_parent(path)
    serialized = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise GateError("refusing to overwrite private artifact") from error
    except OSError as error:
        raise GateError("private artifact cannot be created") from error

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(path, 0o600)
    except OSError as error:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        raise GateError("private artifact cannot be written") from error
    return sha256_text(serialized)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GateError(f"{label} is unavailable or malformed") from error
    if not isinstance(value, dict):
        raise GateError(f"{label} is not an object")
    return value


def require_exact_keys(value: dict[str, Any], keys: Sequence[str], label: str) -> None:
    if set(value) != set(keys):
        raise GateError(f"{label} has an unsafe or unsupported shape")


def load_attestation(path: Path) -> dict[str, Any]:
    attestation = load_json_object(path, "attestation")
    require_exact_keys(
        attestation,
        ("schema", "query_sha256", "source_total", "controls", "ordinary_export"),
        "attestation",
    )
    if attestation["schema"] != "wos-ris-gate-attestation/v1":
        raise GateError("attestation schema is unsupported")
    if not is_sha256(attestation["query_sha256"]):
        raise GateError("attestation query digest is invalid")
    if attestation["source_total"] != 1 or isinstance(
        attestation["source_total"], bool
    ):
        raise GateError("one-record attestation total is invalid")

    controls = attestation["controls"]
    export = attestation["ordinary_export"]
    if not isinstance(controls, dict) or not isinstance(export, dict):
        raise GateError("attestation controls are invalid")
    require_exact_keys(controls, ATTESTATION_CONTROL_KEYS, "attestation controls")
    require_exact_keys(export, ATTESTATION_EXPORT_KEYS, "attestation export")
    if any(not isinstance(value, bool) for value in controls.values()):
        raise GateError("attestation controls are not boolean")
    if any(not isinstance(value, bool) for value in export.values()):
        raise GateError("attestation export is not boolean")
    return attestation


def attestation_passes(attestation: dict[str, Any]) -> bool:
    controls = attestation["controls"]
    export = attestation["ordinary_export"]
    return (
        all(controls.values())
        and all(
            export[key]
            for key in ATTESTATION_EXPORT_KEYS
            if key != "authentication_or_login_redirect"
        )
        and export["authentication_or_login_redirect"] is False
    )


def cell(row: dict[str | None, str | None], name: str) -> str:
    value = row.get(name)
    return value if isinstance(value, str) else ""


def normalized_summary(
    path: Path,
    attestation: dict[str, Any],
    native_identifiers: Sequence[str],
) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise GateError("normalized CSV is unavailable or malformed") from error
    if not headers or len(headers) != len(set(headers)):
        raise GateError("normalized CSV headers are invalid")
    if any(column not in headers for column in REQUIRED_NORMALIZED_COLUMNS):
        raise GateError("normalized CSV omits required columns")
    if any(None in row for row in rows):
        raise GateError("normalized CSV has unsupported rows")

    row = rows[0] if len(rows) == 1 else {}
    identifiers = [cell(item, "Paper ID") for item in rows]
    required_nonempty = {
        column: bool(cell(row, column).strip())
        for column in REQUIRED_NORMALIZED_COLUMNS
        if column not in {"Search source", "Query", "Rank", "Source total"}
    }
    query_digest = sha256_text(cell(row, "Query"))
    native_identifier = native_identifiers[0] if len(native_identifiers) == 1 else ""
    return {
        "row_count": len(rows),
        "source_exact": cell(row, "Search source") == SOURCE_LABEL,
        "rank_is_one": cell(row, "Rank") == "1",
        "source_total_exact": cell(row, "Source total")
        == str(attestation["source_total"]),
        "query_sha256": query_digest,
        "query_sha256_matches_attestation": query_digest == attestation["query_sha256"],
        "required_nonempty": required_nonempty,
        "ordered_paper_id_sha256": sequence_sha256(identifiers),
        "paper_id_sha256_matches_native": bool(native_identifier)
        and sha256_text(cell(row, "Paper ID")) == sha256_text(native_identifier),
    }


def sidecar_summary(
    path: Path,
    native_sha256: str,
    native_records: Sequence[dict[str, list[str]]],
    native_identifiers: Sequence[str],
) -> dict[str, Any]:
    sidecar = load_json_object(path, "cited-reference sidecar")
    require_exact_keys(
        sidecar,
        (
            "schema",
            "artifact_class",
            "native_sha256",
            "native_byte_count",
            "record_count",
            "ordered_paper_id_sha256",
            "ordered_cited_references_sha256",
            "records",
        ),
        "cited-reference sidecar",
    )
    if sidecar["schema"] != "wos-ris-cited-reference-sidecar/v2":
        raise GateError("cited-reference sidecar schema is unsupported")
    if sidecar["artifact_class"] != "private_source_output_not_for_version_control":
        raise GateError("cited-reference sidecar privacy class is invalid")
    if not isinstance(sidecar["record_count"], int) or isinstance(
        sidecar["record_count"], bool
    ):
        raise GateError("cited-reference sidecar record count is invalid")
    if (
        not is_sha256(sidecar["native_sha256"])
        or not is_sha256(sidecar["ordered_paper_id_sha256"])
        or not is_sha256(sidecar["ordered_cited_references_sha256"])
    ):
        raise GateError("cited-reference sidecar digest is invalid")
    records = sidecar["records"]
    if not isinstance(records, list):
        raise GateError("cited-reference sidecar records are invalid")

    record_shapes_valid = True
    for record in records:
        if not isinstance(record, dict):
            record_shapes_valid = False
            break
        if set(record) != {
            "rank",
            "paper_id_sha256",
            "cited_references",
            "cited_references_sha256",
        }:
            record_shapes_valid = False
            break
        if (
            not isinstance(record["rank"], int)
            or isinstance(record["rank"], bool)
            or not is_sha256(record["paper_id_sha256"])
            or not is_sha256(record["cited_references_sha256"])
            or not isinstance(record["cited_references"], list)
            or any(not isinstance(value, str) for value in record["cited_references"])
        ):
            record_shapes_valid = False
            break

    record = records[0] if len(records) == 1 and isinstance(records[0], dict) else {}
    native_identifier = native_identifiers[0] if len(native_identifiers) == 1 else ""
    native_cited_references = (
        list(native_records[0].get("CR", [])) if len(native_records) == 1 else []
    )
    native_cited_reference_groups = [
        list(native_record.get("CR", [])) for native_record in native_records
    ]
    sidecar_cited_reference_groups = [
        sidecar_record.get("cited_references", [])
        if isinstance(sidecar_record, dict)
        and isinstance(sidecar_record.get("cited_references"), list)
        else []
        for sidecar_record in records
    ]
    cited_references = record.get("cited_references")
    return {
        "schema_valid": record_shapes_valid,
        "native_sha256_matches": sidecar["native_sha256"] == native_sha256,
        "record_count": len(records),
        "declared_record_count_matches": sidecar["record_count"] == len(records),
        "rank_is_one": record.get("rank") == 1,
        "paper_id_sha256_matches_native": bool(native_identifier)
        and record.get("paper_id_sha256") == sha256_text(native_identifier),
        "ordered_paper_id_sha256": sidecar["ordered_paper_id_sha256"],
        "ordered_paper_id_sha256_matches_native": sidecar["ordered_paper_id_sha256"]
        == sequence_sha256(native_identifiers),
        "cited_references_sha256_matches_values": isinstance(cited_references, list)
        and record.get("cited_references_sha256") == json_sha256(cited_references),
        "cited_references_match_native": isinstance(cited_references, list)
        and json_sha256(cited_references) == json_sha256(native_cited_references),
        "ordered_cited_references_sha256_matches_values": sidecar[
            "ordered_cited_references_sha256"
        ]
        == json_sha256(sidecar_cited_reference_groups),
        "ordered_cited_references_match_native": sidecar[
            "ordered_cited_references_sha256"
        ]
        == json_sha256(native_cited_reference_groups),
        "cited_reference_count": len(cited_references)
        if isinstance(cited_references, list)
        else 0,
    }


def merged_summary(path: Path, native_identifier: str) -> dict[str, Any]:
    merged = load_json_object(path, "merged result")
    dedup = merged.get("dedup_summary")
    results = merged.get("results")
    if not isinstance(dedup, dict) or not isinstance(results, list):
        raise GateError("merged result shape is invalid")
    record = results[0] if len(results) == 1 and isinstance(results[0], dict) else {}

    def integer_or_none(value: object) -> int | None:
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    paper_id = record.get("paperId")
    sources = record.get("sources")
    return {
        "result_count": len(results),
        "raw_results": integer_or_none(dedup.get("raw_results")),
        "unique_results": integer_or_none(dedup.get("unique_results")),
        "duplicates_removed": integer_or_none(dedup.get("duplicates_removed")),
        "one_record_smoke": (
            dedup.get("raw_results"),
            dedup.get("unique_results"),
            dedup.get("duplicates_removed"),
        )
        == (1, 1, 0),
        "canonical_source": sources == [CANONICAL_SOURCE],
        "paper_id_sha256_matches_native": isinstance(paper_id, str)
        and sha256_text(paper_id) == sha256_text(native_identifier),
    }


def validation_payload(
    ris_path: Path,
    normalized_path: Path,
    sidecar_path: Path,
    merged_path: Path,
    attestation_path: Path,
) -> dict[str, Any]:
    raw, records = read_ris(ris_path)
    attestation = load_attestation(attestation_path)
    identifiers = [record_identifier(record) for record in records]
    native_sha256 = sha256_bytes(raw)
    required_counts = required_tag_record_counts(records)
    native = {
        "native_sha256": native_sha256,
        "native_byte_count": len(raw),
        "record_count": len(records),
        "record_count_is_one": len(records) == 1,
        "type_tag_present": sum(
            any(value.strip() for value in record.get("TY", [])) for record in records
        )
        == 1,
        "required_tag_presence": {
            tag: required_counts[tag] == 1 for tag in REQUIRED_NATIVE_TAGS
        },
        "ordered_paper_id_sha256": sequence_sha256(identifiers),
    }
    normalized = normalized_summary(normalized_path, attestation, identifiers)
    sidecar = sidecar_summary(sidecar_path, native_sha256, records, identifiers)
    merged = merged_summary(
        merged_path, identifiers[0] if len(identifiers) == 1 else ""
    )
    native_passes = (
        native["record_count_is_one"]
        and native["type_tag_present"]
        and all(native["required_tag_presence"].values())
    )
    normalized_passes = (
        normalized["row_count"] == 1
        and normalized["source_exact"]
        and normalized["rank_is_one"]
        and normalized["source_total_exact"]
        and normalized["query_sha256_matches_attestation"]
        and all(normalized["required_nonempty"].values())
        and normalized["ordered_paper_id_sha256"] == native["ordered_paper_id_sha256"]
        and normalized["paper_id_sha256_matches_native"]
    )
    sidecar_passes = (
        sidecar["schema_valid"]
        and sidecar["native_sha256_matches"]
        and sidecar["record_count"] == 1
        and sidecar["declared_record_count_matches"]
        and sidecar["rank_is_one"]
        and sidecar["paper_id_sha256_matches_native"]
        and sidecar["ordered_paper_id_sha256_matches_native"]
        and sidecar["cited_references_sha256_matches_values"]
        and sidecar["cited_references_match_native"]
        and sidecar["ordered_cited_references_sha256_matches_values"]
        and sidecar["ordered_cited_references_match_native"]
        and sidecar["cited_reference_count"] > 0
    )
    merged_passes = (
        merged["result_count"] == 1
        and merged["one_record_smoke"]
        and merged["canonical_source"]
        and merged["paper_id_sha256_matches_native"]
    )
    attested = attestation_passes(attestation)
    return {
        "schema": "wos-ris-one-record-validation/v2",
        "artifact_class": "private_control_only",
        "query_sha256": attestation["query_sha256"],
        "source_total": attestation["source_total"],
        "attestation": {"controls_and_export_pass": attested},
        "native": native,
        "normalized": normalized,
        "sidecar": sidecar,
        "merged": merged,
        "pass": attested
        and native_passes
        and normalized_passes
        and sidecar_passes
        and merged_passes,
    }


def compact_validation(payload: dict[str, Any]) -> dict[str, Any]:
    """Return only privacy-safe fields already emitted by validation_payload."""
    return {
        "source_total": payload["source_total"],
        "attestation": payload["attestation"],
        "native": payload["native"],
        "normalized": payload["normalized"],
        "sidecar": payload["sidecar"],
        "merged": payload["merged"],
        "pass": payload["pass"],
    }


def reconciliation_payload(
    pass_one: dict[str, Any], pass_two: dict[str, Any]
) -> dict[str, Any]:
    checks = {
        "pass_one_valid": pass_one["pass"],
        "pass_two_valid": pass_two["pass"],
        "query_sha256_stable": pass_one["query_sha256"] == pass_two["query_sha256"],
        "source_total_stable": pass_one["source_total"]
        == pass_two["source_total"]
        == 1,
        "native_ris_byte_hash_stable": pass_one["native"]["native_sha256"]
        == pass_two["native"]["native_sha256"],
        "opaque_native_order_stable": pass_one["native"]["ordered_paper_id_sha256"]
        == pass_two["native"]["ordered_paper_id_sha256"],
        "normalized_order_aligns_with_native": (
            pass_one["normalized"]["ordered_paper_id_sha256"]
            == pass_one["native"]["ordered_paper_id_sha256"]
            and pass_two["normalized"]["ordered_paper_id_sha256"]
            == pass_two["native"]["ordered_paper_id_sha256"]
        ),
        "sidecar_order_aligns_with_native": (
            pass_one["sidecar"]["ordered_paper_id_sha256"]
            == pass_one["native"]["ordered_paper_id_sha256"]
            and pass_two["sidecar"]["ordered_paper_id_sha256"]
            == pass_two["native"]["ordered_paper_id_sha256"]
        ),
        "rank_scope_is_one": (
            pass_one["normalized"]["rank_is_one"]
            and pass_two["normalized"]["rank_is_one"]
        ),
        "ordinary_export_attested": (
            pass_one["attestation"]["controls_and_export_pass"]
            and pass_two["attestation"]["controls_and_export_pass"]
        ),
    }
    return {
        "schema": "wos-ris-two-pass-reconciliation/v2",
        "artifact_class": "private_control_only",
        "query_sha256": pass_one["query_sha256"],
        "pass_1": compact_validation(pass_one),
        "pass_2": compact_validation(pass_two),
        "reconciliation": checks,
        "pass": all(checks.values()),
    }


def output_summary(payload: dict[str, Any]) -> str:
    summary: dict[str, Any] = {
        "artifact_sha256": sha256_text(
            json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
        )
    }
    if "pass" in payload:
        summary["pass"] = payload["pass"]
    else:
        summary["status"] = "written"
    return json.dumps(summary, sort_keys=True)


def add_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-path", required=True, type=Path)


def add_validation_arguments(parser: argparse.ArgumentParser, prefix: str = "") -> None:
    option = f"{prefix}-" if prefix else ""
    parser.add_argument(f"--{option}ris", required=True, type=Path)
    parser.add_argument(f"--{option}normalized", required=True, type=Path)
    parser.add_argument(f"--{option}sidecar", required=True, type=Path)
    parser.add_argument(f"--{option}merged", required=True, type=Path)
    parser.add_argument(f"--{option}attestation", required=True, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    integrity = commands.add_parser(
        "integrity", help="write a tag/count/hash-only RIS record"
    )
    integrity.add_argument("--input", required=True, type=Path)
    add_output_argument(integrity)

    sidecar = commands.add_parser(
        "sidecar", help="write a private cited-reference sidecar"
    )
    sidecar.add_argument("--input", required=True, type=Path)
    sidecar.add_argument("--rank-start", default=1, type=int)
    add_output_argument(sidecar)

    validate = commands.add_parser("validate", help="validate one private export pass")
    add_validation_arguments(validate)
    add_output_argument(validate)

    reconcile = commands.add_parser(
        "reconcile", help="reconcile two private export passes"
    )
    add_validation_arguments(reconcile, "pass-one")
    add_validation_arguments(reconcile, "pass-two")
    add_output_argument(reconcile)
    return parser


def validation_from_namespace(
    args: argparse.Namespace, prefix: str = ""
) -> dict[str, Any]:
    attribute = f"{prefix}_" if prefix else ""
    return validation_payload(
        getattr(args, f"{attribute}ris"),
        getattr(args, f"{attribute}normalized"),
        getattr(args, f"{attribute}sidecar"),
        getattr(args, f"{attribute}merged"),
        getattr(args, f"{attribute}attestation"),
    )


def run(args: argparse.Namespace) -> int:
    if args.command == "integrity":
        raw, records = read_ris(args.input)
        payload = integrity_payload(raw, records)
    elif args.command == "sidecar":
        raw, records = read_ris(args.input)
        payload = sidecar_payload(raw, records, args.rank_start)
    elif args.command == "validate":
        payload = validation_from_namespace(args)
    else:
        pass_one = validation_from_namespace(args, "pass_one")
        pass_two = validation_from_namespace(args, "pass_two")
        payload = reconciliation_payload(pass_one, pass_two)

    write_private_json(args.output_path, payload)
    print(output_summary(payload))
    return 0 if payload.get("pass", True) else 1


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except (GateError, OSError, UnicodeDecodeError, ValueError):
        print(
            "wos-ris-gate: refused unsafe or invalid private artifact", file=sys.stderr
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
