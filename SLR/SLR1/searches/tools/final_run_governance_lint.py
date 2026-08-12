#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.23,<5",
# ]
# ///
"""Validate the frozen version-1.6 final-run governance contracts.

This tool validates schemas and synthetic in-memory examples only. It does not
create a final-run directory, execute a source query, or promote any pilot.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError

SOURCE_IDS = (
    "scopus",
    "web_of_science_core_collection",
    "ieee_xplore",
    "compendex",
    "inspec",
    "wiley_online_library",
    "springer_nature_link",
    "proquest_aerospace_index",
    "proquest_dissertations_theses_global",
    "aiaa_aerospace_research_central",
    "iaf_digital_library_iac",
    "oatd",
    "esa_indico",
    "ntrs",
)
INTERFACE_IDS = (
    "scopus_interface",
    "web_of_science_interface",
    "ieee_xplore_interface",
    "engineering_village_interface",
    "wiley_online_library_interface",
    "springer_nature_link_interface",
    "proquest_platform_interface",
    "aiaa_arc_interface",
    "iaf_digital_library_interface",
    "oatd_interface",
    "esa_indico_interface",
    "ntrs_interface",
)
ZERO_SHA256 = "0" * 64


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_instance(instance: Any, schema: dict[str, Any]) -> None:
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)


def expect_invalid(instance: Any, schema: dict[str, Any]) -> None:
    try:
        validate_instance(instance, schema)
    except ValidationError:
        return
    raise AssertionError("negative schema contract fixture unexpectedly passed")


def source_index(crosswalk: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = crosswalk.get("sources")
    if not isinstance(sources, list) or any(not isinstance(item, dict) for item in sources):
        raise AssertionError("crosswalk sources must be a list of objects")
    indexed = {item.get("source_id"): item for item in sources}
    if len(indexed) != len(sources):
        raise AssertionError("crosswalk source IDs are missing or duplicated")
    return indexed


def interface_index(crosswalk: dict[str, Any]) -> dict[str, dict[str, Any]]:
    interfaces = crosswalk.get("interfaces")
    if not isinstance(interfaces, list) or any(not isinstance(item, dict) for item in interfaces):
        raise AssertionError("crosswalk interfaces must be a list of objects")
    indexed = {item.get("interface_id"): item for item in interfaces}
    if len(indexed) != len(interfaces):
        raise AssertionError("crosswalk interface IDs are missing or duplicated")
    return indexed


def validate_crosswalk(crosswalk: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(crosswalk, dict):
        raise TypeError("crosswalk must be an object")
    if crosswalk.get("protocol_version") != "1.6":
        raise AssertionError("crosswalk protocol version is not 1.6")
    if crosswalk.get("status") != "frozen_pre_final_contract_not_search_output":
        raise AssertionError("crosswalk status does not preserve the pre-final boundary")
    if crosswalk.get("count_basis") != "within_source_union_before_cross_source_deduplication":
        raise AssertionError("crosswalk count basis is not frozen")

    sources = source_index(crosswalk)
    interfaces = interface_index(crosswalk)
    if set(sources) != set(SOURCE_IDS):
        raise AssertionError("crosswalk does not contain the exact fourteen source IDs")
    if set(interfaces) != set(INTERFACE_IDS):
        raise AssertionError("crosswalk does not contain the exact twelve interface IDs")

    memberships: dict[str, list[str]] = {source_id: [] for source_id in SOURCE_IDS}
    for interface_id, interface in interfaces.items():
        source_ids = interface.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            raise AssertionError("crosswalk interface membership is invalid")
        for source_id in source_ids:
            if not isinstance(source_id, str) or source_id not in memberships:
                raise AssertionError("crosswalk interface membership is invalid")
            memberships[source_id].append(interface_id)
    for source_id, membership in memberships.items():
        if membership != [sources[source_id].get("interface_id")]:
            raise AssertionError("crosswalk source-to-interface membership is invalid")

    engineering = interfaces["engineering_village_interface"]
    if engineering.get("source_ids") != ["compendex", "inspec"] or engineering.get(
        "simultaneous_multi_source_event"
    ) is not True:
        raise AssertionError("Engineering Village must preserve paired Compendex/Inspec instances")
    if sources["compendex"].get("paired_event_id") != sources["inspec"].get("paired_event_id"):
        raise AssertionError("Compendex and Inspec paired-event IDs differ")

    proquest = interfaces["proquest_platform_interface"]
    if proquest.get("source_ids") != [
        "proquest_aerospace_index",
        "proquest_dissertations_theses_global",
    ] or proquest.get("simultaneous_multi_source_event") is not False:
        raise AssertionError("ProQuest must contain two non-simultaneous exact-database events")
    if sources["proquest_aerospace_index"].get("platform_event_id") == sources[
        "proquest_dissertations_theses_global"
    ].get("platform_event_id"):
        raise AssertionError("ATAI and PQDT platform-event IDs must remain distinct")

    oatd = sources["oatd"]
    if oatd.get("prisma_channel") != "other_methods" or oatd.get("prisma_subtype") != "website":
        raise AssertionError("OATD must remain in other methods/websites")
    for source_id, source in sources.items():
        if source_id != "oatd" and (
            source.get("prisma_channel") != "databases_and_registers"
            or source.get("prisma_subtype") != "database"
        ):
            raise AssertionError("crosswalk PRISMA classification is invalid")
        if source.get("identification_unit") is not True:
            raise AssertionError("crosswalk identification-unit classification is invalid")
    return sources, interfaces


def validate_manifest_crosswalk_binding(
    manifest: Any,
    sources: dict[str, dict[str, Any]],
    crosswalk_sha256: str,
) -> None:
    """Require a schema-valid manifest to match the hash-pinned crosswalk."""
    if not isinstance(manifest, dict):
        raise TypeError("manifest must be an object")

    source_runs = manifest.get("sources")
    if not isinstance(source_runs, list) or any(
        not isinstance(source_run, dict) for source_run in source_runs
    ):
        raise AssertionError("manifest sources must be a list of objects")

    source_ids = [source_run.get("source_id") for source_run in source_runs]
    if (
        len(source_ids) != len(SOURCE_IDS)
        or any(not isinstance(source_id, str) for source_id in source_ids)
        or len(set(source_ids)) != len(source_ids)
        or set(source_ids) != set(SOURCE_IDS)
    ):
        raise AssertionError(
            "manifest source IDs must be the exact frozen fourteen IDs, each once"
        )

    for source_run in source_runs:
        source = sources.get(source_run["source_id"])
        if source is None:
            raise AssertionError("manifest source IDs do not match frozen crosswalk")
        if any(
            source_run.get(field) != source.get(field)
            for field in ("interface_id", "prisma_channel", "prisma_subtype")
        ):
            raise AssertionError(
                "manifest interface and PRISMA mapping does not match frozen crosswalk"
            )

    if manifest.get("source_crosswalk_sha256") != crosswalk_sha256:
        raise AssertionError("manifest crosswalk hash does not match current crosswalk bytes")


def expect_crosswalk_binding_invalid(
    instance: Any,
    schema: dict[str, Any],
    sources: dict[str, dict[str, Any]],
    crosswalk_sha256: str,
) -> None:
    """Require a schema-valid fixture to fail manifest-to-crosswalk binding."""
    validate_instance(instance, schema)
    try:
        validate_manifest_crosswalk_binding(instance, sources, crosswalk_sha256)
    except AssertionError:
        return
    raise AssertionError("negative crosswalk-binding contract fixture unexpectedly passed")


def synthetic_initial_manifest(
    sources: dict[str, dict[str, Any]], crosswalk_sha256: str
) -> dict[str, Any]:
    source_runs = []
    for source_id in SOURCE_IDS:
        source = sources[source_id]
        source_runs.append(
            {
                "source_id": source_id,
                "interface_id": source["interface_id"],
                "prisma_channel": source["prisma_channel"],
                "prisma_subtype": source["prisma_subtype"],
                "final_disposition": "planned",
                "count_state": "pending",
                "source_union_n": None,
                "flow_n": None,
                "partial_records_imported": False,
                "event_ledger": {"path": f"sources/{source_id}/events.json", "sha256": None},
                "source_union_ledger": {"path": f"sources/{source_id}/union.json", "sha256": None},
                "dedup_ledger": {"path": f"sources/{source_id}/dedup.json", "sha256": None},
            }
        )
    return {
        "schema_version": "1.6.0",
        "artifact_class": "final_discovery_manifest",
        "review_run": "eps-mbse-slr-2026",
        "protocol_version": "1.6",
        "cutoff_date": "2026-08-10",
        "created_at_utc": "2026-08-11T00:00:00Z",
        "clean_final_root": True,
        "pilot_inputs_excluded": True,
        "count_unit": "record",
        "count_basis": "within_source_union_before_cross_source_deduplication",
        "source_crosswalk_sha256": crosswalk_sha256,
        "sources": source_runs,
        "failure_register": {"path": "failure-register.json", "sha256": None},
    }


def synthetic_failure_register() -> dict[str, Any]:
    return {
        "schema_version": "1.6.0",
        "artifact_class": "final_discovery_failure_register",
        "review_run": "eps-mbse-slr-2026",
        "protocol_version": "1.6",
        "created_at_utc": "2026-08-11T00:00:00Z",
        "failures": [
            {
                "failure_id": "FAIL-OATD-B2-TIMEOUT",
                "source_id": "oatd",
                "event_id": "OATD-B2",
                "occurred_at_utc": "2026-08-11T00:01:00Z",
                "phase": "query_submission",
                "reason_code": "timeout",
                "source_reported_n": None,
                "retrieved_n": None,
                "accepted_flow_n": None,
                "partial_records_imported": False,
                "artifact_path": "sources/oatd/failures/oatd-b2.json",
                "artifact_sha256": ZERO_SHA256,
                "final_disposition": "retry_required",
                "successor_event_id": None,
                "operator": "synthetic-contract-fixture",
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    base = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--crosswalk", type=Path, default=base / "final-run-source-crosswalk-v1.6.json"
    )
    parser.add_argument(
        "--manifest-schema", type=Path, default=base / "final-run-manifest-schema-v1.6.json"
    )
    parser.add_argument(
        "--failure-schema", type=Path, default=base / "failure-register-schema-v1.6.json"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        metavar="PATH",
        help="Validate an existing manifest against the schema and frozen crosswalk.",
    )
    args = parser.parse_args()

    paths = (args.crosswalk, args.manifest_schema, args.failure_schema)
    try:
        crosswalk, manifest_schema, failure_schema = (read_json(path) for path in paths)
        Draft202012Validator.check_schema(manifest_schema)
        Draft202012Validator.check_schema(failure_schema)
        sources, interfaces = validate_crosswalk(crosswalk)
        crosswalk_sha256 = sha256(args.crosswalk)

        manifest = synthetic_initial_manifest(sources, crosswalk_sha256)
        validate_instance(manifest, manifest_schema)
        validate_manifest_crosswalk_binding(manifest, sources, crosswalk_sha256)

        failure_register = synthetic_failure_register()
        validate_instance(failure_register, failure_schema)

        if args.manifest is not None:
            supplied_manifest = read_json(args.manifest)
            validate_instance(supplied_manifest, manifest_schema)
            validate_manifest_crosswalk_binding(
                supplied_manifest, sources, crosswalk_sha256
            )

        invalid_zero = copy.deepcopy(manifest)
        invalid_zero["sources"][0].update(
            {"final_disposition": "accepted_final", "count_state": "valid_zero", "source_union_n": None, "flow_n": None}
        )
        expect_invalid(invalid_zero, manifest_schema)

        invalid_failure_count = copy.deepcopy(manifest)
        invalid_failure_count["sources"][0].update(
            {"final_disposition": "failed", "count_state": "unavailable", "source_union_n": 0, "flow_n": 0}
        )
        expect_invalid(invalid_failure_count, manifest_schema)

        invalid_partial = copy.deepcopy(failure_register)
        invalid_partial["failures"][0]["partial_records_imported"] = True
        expect_invalid(invalid_partial, failure_schema)

        invalid_flow = copy.deepcopy(failure_register)
        invalid_flow["failures"][0]["accepted_flow_n"] = 0
        expect_invalid(invalid_flow, failure_schema)

        invalid_manifest_path = copy.deepcopy(manifest)
        invalid_manifest_path["sources"][0]["event_ledger"]["path"] = "sources/Token-ledger.json"
        expect_invalid(invalid_manifest_path, manifest_schema)

        invalid_failure_path = copy.deepcopy(failure_register)
        invalid_failure_path["failures"][0]["artifact_path"] = "sources/oatd/COOKIE.json"
        expect_invalid(invalid_failure_path, failure_schema)

        invalid_duplicate_source_ids = copy.deepcopy(manifest)
        invalid_duplicate_source_ids["sources"][-1] = copy.deepcopy(
            invalid_duplicate_source_ids["sources"][0]
        )
        expect_crosswalk_binding_invalid(
            invalid_duplicate_source_ids, manifest_schema, sources, crosswalk_sha256
        )

        invalid_oatd_mapping = copy.deepcopy(manifest)
        invalid_oatd_mapping["sources"][SOURCE_IDS.index("oatd")].update(
            {
                "interface_id": "scopus_interface",
                "prisma_channel": "databases_and_registers",
                "prisma_subtype": "database",
            }
        )
        expect_crosswalk_binding_invalid(
            invalid_oatd_mapping, manifest_schema, sources, crosswalk_sha256
        )
    except OSError:
        error_message = "governance contract artifact could not be read"
    except (json.JSONDecodeError, UnicodeDecodeError):
        error_message = "governance contract artifact is not valid JSON"
    except (SchemaError, ValidationError):
        error_message = "governance contract artifact does not satisfy its schema"
    except TypeError:
        error_message = "governance contract artifact has an invalid object type"
    except AssertionError as error:
        error_message = str(error) or "governance contract validation failed"
    else:
        report = {
            "status": "passed",
            "protocol_version_checked": "1.6",
            "sources_checked": len(sources),
            "interfaces_checked": len(interfaces),
            "manifest_schema_sha256": sha256(args.manifest_schema),
            "failure_schema_sha256": sha256(args.failure_schema),
            "crosswalk_sha256": crosswalk_sha256,
            "synthetic_positive_contracts_checked": 2,
            "synthetic_negative_contracts_checked": 8,
            "created_final_run": False,
            "executed_source_query": False,
        }
        print(json.dumps(report, indent=2))
        return 0

    print(json.dumps({"status": "failed", "error": error_message}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
