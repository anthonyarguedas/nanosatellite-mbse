#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.18,<5",
# ]
# ///
"""Fail-closed validation for the SLR1 search infrastructure and campaigns."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SEARCHES = ROOT / "searches"

DIRECT_IDS = {"A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2"}
CONCEPT_IDS = {
    "P",
    "E_H",
    "E_F",
    "E",
    "M_H",
    "M_B",
    "M",
    "R",
    "G_model",
    "G_structure",
    "C1",
    "T2",
}
EXPECTED_TERM_COUNTS = {
    "P": 20,
    "E_H": 38,
    "E_F": 33,
    "M_H": 28,
    "M_B": 27,
    "R": 55,
    "G_model": 14,
    "G_structure": 8,
    "C1": 26,
}
EXPECTED_TASKS = {
    "S-D01",
    "S-D02",
    "S-D03",
    "S-D04",
    "S-D05",
    "S-D06",
    "S-D07",
    "S-D08",
    "S-D09",
    "S-D10",
    "S-D11",
    "S-D12",
    "S-D13",
    "S-L02",
}

REQUIRED_SCHEMA_NAMES = frozenset(
    {
        "failure-register.schema.json",
        "final-run-manifest.schema.json",
        "pilot-campaign.schema.json",
        "pilot-manifest.schema.json",
    }
)

# These names are intentionally duplicated in the campaign schema's immutable
# capability_catalog constraints. Keeping the small catalog here makes the
# acceptance rule auditable without attempting to infer capability coverage.
CAPABILITY_CATALOG: dict[str, tuple[str, ...]] = {
    "direct": (
        "G-QUERY-TRANSPORT",
        "G-FIELD-BOUNDARY",
        "G-PAGINATION-CONTROL",
        "G-PAGE-IDENTITY",
    ),
    "local_harvest": (
        "G-LOCAL-CANDIDATE-LOGIC",
        "G-LOCAL-TAGGING",
        "G-LOCAL-HARVEST-COVERAGE",
        "G-LOCAL-IDENTITY",
    ),
}
REQUIRED_CAPABILITY_CATALOG = CAPABILITY_CATALOG

CAMPAIGN_STATUSES = {
    "in_progress",
    "technically_blocked",
    "methodological_decision_pending",
    "ready_for_acceptance_review",
    "accepted",
    "cancelled",
}
GATE_STATUSES = {"passed", "failed", "blocked", "untested", "invalidated"}
TERMINAL_VERIFICATIONS = {
    "not_applicable",
    "verified",
    "legacy_unverifiable",
}
DECISION_CLASSES = {"none", "controller_technical", "human_methodological"}
DECISION_AUTHORIZATION_STATUSES = {
    "not_required",
    "prospectively_authorized",
    "pending",
    "authorized",
}
ORIGINAL_BASES = {
    "observed",
    "official_documentation",
    "observed_and_documented",
    "inferred",
    "untested",
}
ACCEPTANCE_BASES = {
    "observed",
    "official_documentation",
    "observed_and_documented",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TASK_ID_RE = re.compile(r"^(S-D(0[1-9]|1[0-3])|S-L02)$")
CAMPAIGN_ID_RE = re.compile(
    r"^(S-D(0[1-9]|1[0-3])|S-L02)-C[0-9]{2}-[0-9]{8}T[0-9]{6}[+-][0-9]{4}$"
)
ATTEMPT_ID_RE = re.compile(
    r"^(S-D(0[1-9]|1[0-3])|S-L02)-P[0-9]{2}-[0-9]{8}T[0-9]{6}[+-][0-9]{4}$"
)
GATE_ID_RE = re.compile(r"^[A-Z][A-Z0-9-]{1,63}$")
CHECKPOINT_ID_RE = re.compile(r"^CP-[A-Z0-9-]{2,63}$")
DECISION_ID_RE = re.compile(r"^D-[A-Z0-9-]{2,63}$")
RETRY_POLICY_ID_RE = re.compile(r"^RP-[A-Z0-9-]{2,63}$")


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _mapping(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    require(isinstance(value, list), f"{label} must be an array")
    return value


def _require_fields(value: dict[str, Any], fields: set[str], label: str) -> None:
    missing = sorted(fields - set(value))
    require(not missing, f"{label} is missing required field(s): {', '.join(missing)}")


def _string(value: Any, label: str, *, nonempty: bool = True) -> str:
    require(isinstance(value, str), f"{label} must be a string")
    if nonempty:
        require(bool(value), f"{label} must not be empty")
    return value


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    require(
        isinstance(value, int) and not isinstance(value, bool),
        f"{label} must be an integer",
    )
    require(value >= minimum, f"{label} must be at least {minimum}")
    return value


def _boolean(value: Any, label: str) -> bool:
    require(isinstance(value, bool), f"{label} must be a boolean")
    return value


def _sha256(value: Any, label: str) -> str:
    value = _string(value, label)
    require(
        bool(SHA256_RE.fullmatch(value)), f"{label} must be a lowercase SHA-256 hash"
    )
    return value


def _pattern(value: Any, pattern: re.Pattern[str], label: str) -> str:
    value = _string(value, label)
    require(bool(pattern.fullmatch(value)), f"{label} has an invalid format")
    return value


def _parse_date_time(value: Any, label: str) -> datetime:
    value = _string(value, label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AssertionError(f"{label} must be an ISO 8601 date-time") from exc
    require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return parsed


def _date_time(value: Any, label: str) -> str:
    _parse_date_time(value, label)
    return value


def _unique_strings(values: list[Any], label: str) -> list[str]:
    strings = [
        _string(value, f"{label}[{index}]") for index, value in enumerate(values)
    ]
    require(len(strings) == len(set(strings)), f"{label} contains duplicate values")
    return strings


def _relative_path(value: Any, label: str) -> str:
    """Accept only a simple, portable path relative to one source packet."""
    path = _string(value, label)
    require("\\" not in path, f"{label} must use a relative POSIX path")
    require(not path.startswith("/"), f"{label} must not be absolute")
    require(not re.match(r"^[A-Za-z]:", path), f"{label} must not be absolute")
    parts = path.split("/")
    require(
        all(part not in {"", ".", ".."} for part in parts),
        f"{label} must not contain path traversal",
    )
    return path


def _file_reference(value: Any, label: str) -> tuple[str, str]:
    reference = _mapping(value, label)
    _require_fields(reference, {"path", "sha256"}, label)
    return (
        _relative_path(reference["path"], f"{label}.path"),
        _sha256(reference["sha256"], f"{label}.sha256"),
    )


def _shared_lease_reference(value: Any, label: str) -> tuple[str, str]:
    path, digest = _file_reference(value, label)
    normalized_path = path.lower()
    require(
        "preflight" not in normalized_path and "postflight" not in normalized_path,
        f"{label} must not reference a preflight/postflight artifact",
    )
    return path, digest


def _task_prefix(identifier: str, marker: str) -> str:
    return identifier.split(f"-{marker}", 1)[0]


def _require_task_prefix(
    identifier: Any,
    pattern: re.Pattern[str],
    task_id: str,
    marker: str,
    label: str,
) -> str:
    identifier = _pattern(identifier, pattern, label)
    require(
        _task_prefix(identifier, marker) == task_id,
        f"{label} has the wrong task prefix",
    )
    return identifier


def expression_refs(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.get("args", []):
            yield from expression_refs(item)


# The historical dictionary/crosswalk checks are intentionally retained. They
# do not consume source packet contents and keep the infrastructure baseline
# independent of campaign validation.
def validate_dictionary() -> None:
    data = load(SEARCHES / "search-concept-dictionary.json")
    require(
        data["provenance"]["created_new_for_run"] is True,
        "dictionary lacks new-run provenance",
    )
    require(
        data["provenance"]["restored_from_prior_run"] is False,
        "dictionary says it was restored",
    )
    defaults = data["matching_defaults"]
    require(
        defaults["acronym_policy"] == "match standalone lexical tokens, not substrings",
        "acronym policy differs",
    )
    require(defaults["pair_policy"]["order"] == "unordered", "pair order differs")
    require(
        defaults["pair_policy"]["maximum_intervening_lexical_tokens"] == 5,
        "pair distance differs",
    )
    require(
        "free text is mandatory" in defaults["controlled_vocabulary_policy"],
        "controlled-vocabulary policy differs",
    )
    concepts = data["concepts"]
    require(
        set(concepts) == CONCEPT_IDS,
        f"concept IDs differ: {set(concepts) ^ CONCEPT_IDS}",
    )
    for concept_id, count in EXPECTED_TERM_COUNTS.items():
        terms = concepts[concept_id]["terms"]
        require(
            len(terms) == count,
            f"{concept_id} has {len(terms)} terms, expected {count}",
        )
        require(len(terms) == len(set(terms)), f"{concept_id} contains duplicate terms")
    require(concepts["E"]["members"] == ["E_H", "E_F"], "E union differs")
    require(concepts["M"]["members"] == ["M_H", "M_B"], "M union differs")
    partitions = data["direct_partitions"]
    ids = [item["id"] for item in partitions]
    require(
        set(ids) == DIRECT_IDS and len(ids) == len(DIRECT_IDS),
        "direct partition schedule differs",
    )
    for item in partitions:
        unknown = set(expression_refs(item["expression"])) - CONCEPT_IDS
        require(not unknown, f"{item['id']} references unknown concepts: {unknown}")
    local = data["local_method_minimum"]
    require(set(local["independent_tags"]) == {"R", "T2"}, "local tags differ")
    require(
        {item["id"] for item in local["expansion_candidates"]} == {"BG1", "BG2", "BC1"},
        "local expansions differ",
    )


def validate_crosswalk() -> None:
    data = load(SEARCHES / "source-interface-prisma-crosswalk.json")
    sources = data["sources"]
    interfaces = data["interfaces"]
    require(len(sources) == 15, f"crosswalk has {len(sources)} source rows")
    require(
        len({item["source_id"] for item in sources}) == 15, "source IDs are not unique"
    )
    require(len(interfaces) == 13, f"crosswalk has {len(interfaces)} interfaces")
    interface_ids = {item["interface_id"] for item in interfaces}
    require(len(interface_ids) == 13, "interface IDs are not unique")
    require(
        {item["task_id"] for item in sources} == EXPECTED_TASKS,
        "source task coverage differs",
    )
    require(
        all(item["interface_id"] in interface_ids for item in sources),
        "source references unknown interface",
    )
    oatd = next(item for item in sources if item["source_id"] == "oatd")
    require(oatd["prisma_2020_column"] == "other_methods", "OATD PRISMA column differs")
    require(
        all(
            item["prisma_2020_column"] == "databases_registers"
            for item in sources
            if item["source_id"] != "oatd"
        ),
        "a non-OATD source is outside databases/registers",
    )
    require(
        all(item["separate_total"] is True for item in sources),
        "a source lacks a separate total",
    )


def _jsonschema_components() -> tuple[Any, Any]:
    """Import jsonschema lazily so a plain Python run can explain the failure."""
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as exc:
        raise RuntimeError(
            "jsonschema is required for fail-closed validation; run this script with "
            "`uv run SLR/SLR1/scripts/validate_search_infrastructure.py`"
        ) from exc
    return Draft202012Validator, FormatChecker


def _validate_schema_document(schema: Any, label: str) -> None:
    schema = _mapping(schema, label)
    require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        f"{label} must declare Draft 2020-12",
    )
    _string(schema.get("$id"), f"{label}.$id")
    require(schema.get("type") == "object", f"{label} must describe an object")
    _mapping(schema.get("properties"), f"{label}.properties")
    _list(schema.get("required"), f"{label}.required")


def _validation_error_key(error: Any) -> tuple[str, ...]:
    return tuple(str(part) for part in error.absolute_path)


def _validate_jsonschema_instance(
    schema: dict[str, Any], instance: Any, label: str
) -> None:
    validator_class, format_checker_class = _jsonschema_components()
    validator = validator_class(schema, format_checker=format_checker_class())
    errors = sorted(validator.iter_errors(instance), key=_validation_error_key)
    if errors:
        raise AssertionError(f"{label} does not validate: {errors[0].message}")


def _load_schemas(searches_root: Path = SEARCHES) -> dict[str, dict[str, Any]]:
    schema_dir = searches_root / "schemas"
    schema_paths = {path.name: path for path in schema_dir.glob("*.schema.json")}
    missing = sorted(REQUIRED_SCHEMA_NAMES - set(schema_paths))
    require(
        not missing, f"missing required infrastructure schema(s): {', '.join(missing)}"
    )

    validator_class, _ = _jsonschema_components()
    schemas: dict[str, dict[str, Any]] = {}
    for name, path in sorted(schema_paths.items()):
        schema = _mapping(load(path), f"schema {name}")
        _validate_schema_document(schema, f"schema {name}")
        validator_class.check_schema(schema)
        schemas[name] = schema

    catalog_schema = schemas["pilot-campaign.schema.json"]["$defs"][
        "capabilityCatalogs"
    ]["properties"]
    for method_type, expected in CAPABILITY_CATALOG.items():
        declared = catalog_schema[method_type]["const"]
        require(
            tuple(declared) == expected,
            f"pilot campaign schema catalog differs for {method_type}",
        )
    return schemas


def _validate_pilot_manifest_formats(manifest: Any, label: str) -> None:
    """Keep manual diagnostics for the formats that matter to cross-links."""
    manifest = _mapping(manifest, label)
    for field in ("started_at", "ended_at"):
        if field in manifest:
            _date_time(manifest[field], f"{label}.{field}")
    interface = manifest.get("interface")
    if isinstance(interface, dict) and "url" in interface:
        url = _string(interface["url"], f"{label}.interface.url")
        parsed = urlparse(url)
        require(
            bool(parsed.scheme and parsed.netloc),
            f"{label}.interface.url must be an absolute URI",
        )
    executions = manifest.get("executions")
    if isinstance(executions, list):
        for index, execution in enumerate(executions):
            if isinstance(execution, dict) and "started_at" in execution:
                _date_time(
                    execution["started_at"], f"{label}.executions[{index}].started_at"
                )


def validate_schemas(searches_root: Path = SEARCHES) -> dict[str, dict[str, Any]]:
    """Validate all named schemas plus the two current templates."""
    schemas = _load_schemas(searches_root)
    templates = searches_root / "templates"
    pilot_template = load(templates / "pilot-manifest.template.json")
    _validate_pilot_manifest_formats(pilot_template, "pilot manifest template")
    _validate_jsonschema_instance(
        schemas["pilot-manifest.schema.json"], pilot_template, "pilot manifest template"
    )
    _validate_jsonschema_instance(
        schemas["pilot-campaign.schema.json"],
        load(templates / "pilot-campaign.template.json"),
        "pilot campaign template",
    )
    return schemas


def _validate_terminal(value: Any, label: str) -> dict[str, Any]:
    terminal = _mapping(value, label)
    _require_fields(
        terminal,
        {
            "outcome",
            "category",
            "ended_at",
            "provider_failure",
            "source_writing_stopped",
            "browser_backed",
            "terminal_verification",
            "cleanup_receipt",
            "lease_receipt",
            "cancelled_by",
            "reason",
        },
        label,
    )
    outcome = terminal["outcome"]
    require(
        outcome in {"completed", "blocked", "failed", "cancelled"},
        f"{label}.outcome is invalid",
    )
    category = terminal["category"]
    require(
        category
        in {
            "completed",
            "technical",
            "provider_failure",
            "access_blocked",
            "methodological",
            "operator_cancellation",
        },
        f"{label}.category is invalid",
    )
    _date_time(terminal["ended_at"], f"{label}.ended_at")
    provider_failure = _boolean(
        terminal["provider_failure"], f"{label}.provider_failure"
    )
    require(
        terminal["source_writing_stopped"] is True,
        f"{label}.source_writing_stopped must be true",
    )
    browser_backed = _boolean(terminal["browser_backed"], f"{label}.browser_backed")
    terminal_verification = terminal["terminal_verification"]
    require(
        terminal_verification in TERMINAL_VERIFICATIONS,
        f"{label}.terminal_verification is invalid",
    )
    cancelled_by = terminal["cancelled_by"]

    if outcome == "cancelled":
        require(
            category == "operator_cancellation",
            f"{label} cancellation must use operator_cancellation category",
        )
        require(
            provider_failure is False,
            f"{label} operator cancellation is not provider failure",
        )
        require(cancelled_by == "operator", f"{label} cancellation must name operator")
    else:
        require(
            cancelled_by is None,
            f"{label}.cancelled_by must be null when not cancelled",
        )
    if outcome == "completed":
        require(
            category == "completed",
            f"{label} completed outcome needs completed category",
        )
        require(
            provider_failure is False,
            f"{label} completed outcome is not provider failure",
        )
    if category == "provider_failure":
        require(
            provider_failure is True,
            f"{label} provider category needs provider_failure",
        )
    if provider_failure:
        require(
            category == "provider_failure",
            f"{label} provider failure needs provider category",
        )
    if category == "operator_cancellation":
        require(
            outcome == "cancelled", f"{label} operator category needs cancelled outcome"
        )

    cleanup = terminal["cleanup_receipt"]
    lease = terminal["lease_receipt"]
    if not browser_backed:
        require(
            terminal_verification == "not_applicable",
            f"{label}.terminal_verification must be not_applicable when not browser-backed",
        )
        require(
            cleanup is None,
            f"{label}.cleanup_receipt must be null when not browser-backed",
        )
        require(
            lease is None, f"{label}.lease_receipt must be null when not browser-backed"
        )
    elif terminal_verification == "verified":
        _file_reference(cleanup, f"{label}.cleanup_receipt")
        _shared_lease_reference(lease, f"{label}.lease_receipt")
    else:
        require(
            terminal_verification == "legacy_unverifiable",
            f"{label}.terminal_verification is invalid for a browser-backed attempt",
        )
        require(
            outcome in {"blocked", "failed", "cancelled"},
            f"{label}.legacy_unverifiable terminal cannot be completed",
        )
        require(
            cleanup is None,
            f"{label}.cleanup_receipt must be null for legacy_unverifiable terminal",
        )
        require(
            lease is None,
            f"{label}.lease_receipt must be null for legacy_unverifiable terminal",
        )
    _string(terminal["reason"], f"{label}.reason")
    return terminal


def _validate_source_operation(operation: Any, label: str) -> dict[str, Any]:
    operation = _mapping(operation, label)
    _require_fields(
        operation,
        {
            "operation_id",
            "operation_key",
            "outcome",
            "source_reported_total",
            "records_retrieved",
            "records_imported",
            "retry",
        },
        label,
    )
    _string(operation["operation_id"], f"{label}.operation_id")
    _string(operation["operation_key"], f"{label}.operation_key")
    outcome = operation["outcome"]
    require(
        outcome in {"success", "explicit_zero", "failed", "busy"},
        f"{label}.outcome is invalid",
    )
    total = operation["source_reported_total"]
    if total is not None:
        _integer(total, f"{label}.source_reported_total")
    retrieved = _integer(operation["records_retrieved"], f"{label}.records_retrieved")
    imported = _integer(operation["records_imported"], f"{label}.records_imported")
    require(imported == 0, f"{label}.records_imported must be zero for a pilot")

    if outcome == "success":
        require(
            isinstance(total, int) and not isinstance(total, bool) and total >= 1,
            f"{label} success needs a positive total",
        )
    elif outcome == "explicit_zero":
        require(total == 0, f"{label} explicit zero must report total zero")
        require(retrieved == 0, f"{label} explicit zero must retrieve zero records")
    else:
        require(total is None, f"{label} {outcome} must report a null total, not zero")
        require(retrieved == 0, f"{label} {outcome} must retrieve zero records")
    return operation


def _validate_attempts(
    campaign: dict[str, Any],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[tuple[str, str, str], dict[str, Any]],
    list[tuple[str, dict[str, Any], dict[str, Any]]],
]:
    attempts = _list(campaign["attempts"], "campaign.attempts")
    require(attempts, "campaign.attempts must not be empty")
    task_id = campaign["task_id"]
    attempts_by_id: dict[str, dict[str, Any]] = {}
    sequences: list[int] = []
    evidence_by_reference: dict[tuple[str, str, str], dict[str, Any]] = {}
    evidence_ids: set[str] = set()
    retry_records: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    for index, raw_attempt in enumerate(attempts):
        label = f"campaign.attempts[{index}]"
        attempt = _mapping(raw_attempt, label)
        _require_fields(
            attempt,
            {
                "attempt_id",
                "sequence",
                "manifest_path",
                "manifest_sha256",
                "immutable",
                "allocation",
                "source_operations",
                "evidence",
                "terminal",
            },
            label,
        )
        attempt_id = _require_task_prefix(
            attempt["attempt_id"], ATTEMPT_ID_RE, task_id, "P", f"{label}.attempt_id"
        )
        require(
            attempt_id not in attempts_by_id,
            f"duplicate immutable attempt ID: {attempt_id}",
        )
        sequence = _integer(attempt["sequence"], f"{label}.sequence", minimum=1)
        sequences.append(sequence)
        _relative_path(attempt["manifest_path"], f"{label}.manifest_path")
        _sha256(attempt["manifest_sha256"], f"{label}.manifest_sha256")
        require(attempt["immutable"] is True, f"{label}.immutable must be true")

        allocation = _mapping(attempt["allocation"], f"{label}.allocation")
        _require_fields(
            allocation,
            {
                "attempt_kind",
                "authorized_by",
                "authorization_decision_id",
                "prospectively_authorized",
                "allocated_at",
            },
            f"{label}.allocation",
        )
        require(
            allocation["attempt_kind"]
            in {"initial", "technical_corrective", "methodological_revision"},
            f"{label}.allocation.attempt_kind is invalid",
        )
        require(
            allocation["authorized_by"] in {"controller", "human"},
            f"{label}.allocation.authorized_by is invalid",
        )
        decision_id = allocation["authorization_decision_id"]
        require(
            decision_id is None or isinstance(decision_id, str),
            f"{label}.allocation.authorization_decision_id is invalid",
        )
        if decision_id is not None:
            _pattern(
                decision_id,
                DECISION_ID_RE,
                f"{label}.allocation.authorization_decision_id",
            )
        _boolean(
            allocation["prospectively_authorized"],
            f"{label}.allocation.prospectively_authorized",
        )
        _date_time(allocation["allocated_at"], f"{label}.allocation.allocated_at")

        source_operations = _mapping(
            attempt["source_operations"], f"{label}.source_operations"
        )
        _require_fields(
            source_operations,
            {"predeclared_maximum", "performed", "operations"},
            f"{label}.source_operations",
        )
        maximum = _integer(
            source_operations["predeclared_maximum"],
            f"{label}.source_operations.predeclared_maximum",
        )
        performed = _integer(
            source_operations["performed"], f"{label}.source_operations.performed"
        )
        operations = _list(
            source_operations["operations"], f"{label}.source_operations.operations"
        )
        require(
            performed == len(operations),
            f"{label}.source_operations.performed must equal its operation list length",
        )
        require(
            performed <= maximum,
            f"{label}.source_operations exceeds its predeclared maximum",
        )
        operation_ids: dict[str, dict[str, Any]] = {}
        operation_keys: dict[str, dict[str, Any]] = {}
        reissued_operation_ids: set[str] = set()
        for operation_index, raw_operation in enumerate(operations):
            operation_label = f"{label}.source_operations.operations[{operation_index}]"
            operation = _validate_source_operation(raw_operation, operation_label)
            operation_id = operation["operation_id"]
            require(
                operation_id not in operation_ids,
                f"{label}.source_operations has duplicate operation IDs",
            )
            operation_key = operation["operation_key"]
            retry = operation["retry"]
            if retry is None:
                require(
                    operation_key not in operation_keys,
                    f"{operation_label} repeats an operation without an auditable retry",
                )
            else:
                retry_label = f"{operation_label}.retry"
                retry = _mapping(retry, retry_label)
                _require_fields(
                    retry,
                    {
                        "reissue_of",
                        "policy_id",
                        "reason",
                        "same_tab",
                        "preauthorized",
                        "passive_wait_delay_seconds",
                        "completed",
                        "receipt",
                    },
                    retry_label,
                )
                reissue_of = _string(retry["reissue_of"], f"{retry_label}.reissue_of")
                require(
                    reissue_of in operation_ids,
                    f"{retry_label} must reissue an earlier operation in the same attempt",
                )
                previous = operation_ids[reissue_of]
                require(
                    previous["outcome"] != "failed",
                    f"{retry_label} cannot reissue a failed operation",
                )
                require(
                    previous["outcome"] == "busy",
                    f"{retry_label} may reissue only a same-tab busy operation",
                )
                require(
                    reissue_of not in reissued_operation_ids,
                    f"{retry_label} reissues an operation more than once",
                )
                require(
                    operation_key == previous["operation_key"],
                    f"{retry_label} must retain the original operation key",
                )
                require(
                    operation_key in operation_keys,
                    f"{retry_label} does not continue an earlier operation key",
                )
                _pattern(
                    retry["policy_id"], RETRY_POLICY_ID_RE, f"{retry_label}.policy_id"
                )
                require(
                    retry["reason"] == "same_tab_busy",
                    f"{retry_label}.reason is invalid",
                )
                require(
                    retry["same_tab"] is True, f"{retry_label}.same_tab must be true"
                )
                require(
                    retry["preauthorized"] is True,
                    f"{retry_label}.preauthorized must be true",
                )
                _integer(
                    retry["passive_wait_delay_seconds"],
                    f"{retry_label}.passive_wait_delay_seconds",
                )
                completed = _boolean(retry["completed"], f"{retry_label}.completed")
                if not completed:
                    require(
                        operation["outcome"] == "failed",
                        f"{retry_label} incomplete reissue must be failed",
                    )
                _file_reference(retry["receipt"], f"{retry_label}.receipt")
                reissued_operation_ids.add(reissue_of)
                retry_records.append((attempt_id, operation, retry))
            operation_ids[operation_id] = operation
            operation_keys[operation_key] = operation

        evidence = _list(attempt["evidence"], f"{label}.evidence")
        for evidence_index, raw_evidence in enumerate(evidence):
            evidence_label = f"{label}.evidence[{evidence_index}]"
            item = _mapping(raw_evidence, evidence_label)
            _require_fields(
                item,
                {"evidence_id", "gate_id", "path", "sha256", "validity", "basis"},
                evidence_label,
            )
            evidence_id = _pattern(
                item["evidence_id"], GATE_ID_RE, f"{evidence_label}.evidence_id"
            )
            require(
                evidence_id not in evidence_ids, f"duplicate evidence ID: {evidence_id}"
            )
            evidence_ids.add(evidence_id)
            _pattern(item["gate_id"], GATE_ID_RE, f"{evidence_label}.gate_id")
            path = _relative_path(item["path"], f"{evidence_label}.path")
            digest = _sha256(item["sha256"], f"{evidence_label}.sha256")
            require(
                item["validity"] in {"valid", "invalidated"},
                f"{evidence_label}.validity is invalid",
            )
            require(
                item["basis"] in ORIGINAL_BASES, f"{evidence_label}.basis is invalid"
            )
            reference = (attempt_id, path, digest)
            require(
                reference not in evidence_by_reference,
                f"duplicate evidence reference in {attempt_id}",
            )
            evidence_by_reference[reference] = item

        _validate_terminal(attempt["terminal"], f"{label}.terminal")
        attempts_by_id[attempt_id] = attempt

    require(
        len(sequences) == len(set(sequences)),
        "campaign attempt sequences are not unique",
    )
    require(
        sorted(sequences) == list(range(1, len(sequences) + 1)),
        "campaign attempt sequences must be contiguous from one",
    )
    initial_attempts = [
        attempt
        for attempt in attempts_by_id.values()
        if attempt["allocation"]["attempt_kind"] == "initial"
    ]
    require(
        len(initial_attempts) == 1, "campaign must have exactly one initial attempt"
    )
    require(
        initial_attempts[0]["sequence"] == 1,
        "the only initial attempt must have sequence 1",
    )
    for attempt_id, attempt in attempts_by_id.items():
        if attempt["sequence"] > 1:
            require(
                attempt["allocation"]["attempt_kind"]
                in {"technical_corrective", "methodological_revision"},
                f"later attempt {attempt_id} must be technical_corrective or methodological_revision",
            )
    return attempts_by_id, evidence_by_reference, retry_records


def _validate_retry_policy(
    campaign: dict[str, Any],
    retry_records: list[tuple[str, dict[str, Any], dict[str, Any]]],
) -> None:
    policy = _mapping(campaign["retry_policy"], "campaign.retry_policy")
    _require_fields(
        policy,
        {
            "policy_id",
            "maximum_retries",
            "passive_wait_delays_seconds",
            "attempted",
            "completed",
            "preauthorized_same_tab_busy_reissue",
        },
        "campaign.retry_policy",
    )
    policy_id = _pattern(
        policy["policy_id"], RETRY_POLICY_ID_RE, "campaign.retry_policy.policy_id"
    )
    maximum = _integer(
        policy["maximum_retries"], "campaign.retry_policy.maximum_retries"
    )
    delays = _list(
        policy["passive_wait_delays_seconds"],
        "campaign.retry_policy.passive_wait_delays_seconds",
    )
    delay_values = [
        _integer(delay, f"campaign.retry_policy.passive_wait_delays_seconds[{index}]")
        for index, delay in enumerate(delays)
    ]
    require(
        len(delay_values) == maximum,
        "campaign.retry_policy delays must prescribe every finite retry",
    )
    attempted = _integer(policy["attempted"], "campaign.retry_policy.attempted")
    completed = _integer(policy["completed"], "campaign.retry_policy.completed")
    require(attempted <= maximum, "campaign.retry_policy attempted exceeds maximum")
    require(completed <= attempted, "campaign.retry_policy completed exceeds attempted")
    require(
        attempted == len(retry_records),
        "campaign.retry_policy attempted does not match auditable busy reissues",
    )
    completed_retries = sum(1 for _, _, retry in retry_records if retry["completed"])
    require(
        completed == completed_retries,
        "campaign.retry_policy completed does not match completed busy reissues",
    )
    preauthorized = _boolean(
        policy["preauthorized_same_tab_busy_reissue"],
        "campaign.retry_policy.preauthorized_same_tab_busy_reissue",
    )
    if retry_records:
        require(
            preauthorized,
            "campaign.retry_policy does not preauthorize same-tab busy reissues",
        )
    for index, (_, _, retry) in enumerate(retry_records):
        require(
            retry["policy_id"] == policy_id,
            "busy reissue references another campaign retry policy",
        )
        require(
            retry["passive_wait_delay_seconds"] == delay_values[index],
            "busy reissue does not use its prescribed passive-wait delay",
        )


def _validate_decisions(
    campaign: dict[str, Any], attempts: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    decisions = _list(campaign["decisions"], "campaign.decisions")
    task_id = campaign["task_id"]
    decisions_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_decision in enumerate(decisions):
        label = f"campaign.decisions[{index}]"
        decision = _mapping(raw_decision, label)
        _require_fields(
            decision,
            {
                "decision_id",
                "attempt_id",
                "decision_class",
                "review_effect",
                "affects_underlying_literature_review",
                "human_authorization_required",
                "authorization_status",
                "authorized_by",
                "affected_gate_ids",
                "rationale",
            },
            label,
        )
        decision_id = _pattern(
            decision["decision_id"], DECISION_ID_RE, f"{label}.decision_id"
        )
        require(
            decision_id not in decisions_by_id, f"duplicate decision ID: {decision_id}"
        )
        attempt_id = decision["attempt_id"]
        require(
            attempt_id is None or isinstance(attempt_id, str),
            f"{label}.attempt_id is invalid",
        )
        if attempt_id is not None:
            _require_task_prefix(
                attempt_id, ATTEMPT_ID_RE, task_id, "P", f"{label}.attempt_id"
            )
            require(attempt_id in attempts, f"{label} references an unknown attempt")
        decision_class = decision["decision_class"]
        require(
            decision_class in DECISION_CLASSES, f"{label}.decision_class is invalid"
        )
        review_effect = _boolean(decision["review_effect"], f"{label}.review_effect")
        affects_review = _boolean(
            decision["affects_underlying_literature_review"],
            f"{label}.affects_underlying_literature_review",
        )
        human_required = _boolean(
            decision["human_authorization_required"],
            f"{label}.human_authorization_required",
        )
        authorization_status = decision["authorization_status"]
        require(
            authorization_status in DECISION_AUTHORIZATION_STATUSES,
            f"{label}.authorization_status is invalid",
        )
        authorized_by = decision["authorized_by"]
        require(
            authorized_by in {"none", "controller", "human"},
            f"{label}.authorized_by is invalid",
        )
        decided_at = decision.get("decided_at")
        if decided_at is not None:
            _date_time(decided_at, f"{label}.decided_at")
        affected = _unique_strings(
            _list(decision["affected_gate_ids"], f"{label}.affected_gate_ids"),
            f"{label}.affected_gate_ids",
        )
        _string(decision["rationale"], f"{label}.rationale")

        if decision_class == "none":
            require(
                not review_effect and not affects_review,
                f"{label} class none cannot affect review",
            )
            require(
                not human_required,
                f"{label} class none cannot require human authorization",
            )
            require(
                authorization_status == "not_required",
                f"{label} class none must be not_required",
            )
            require(
                authorized_by == "none",
                f"{label} class none must be authorized by none",
            )
            require(attempt_id is None, f"{label} class none cannot cite an attempt")
            require(
                decided_at is None,
                f"{label} class none cannot have a decision timestamp",
            )
            require(not affected, f"{label} class none cannot affect capability gates")
        elif decision_class == "controller_technical":
            require(
                not review_effect and not affects_review,
                f"{label} technical work cannot affect review semantics",
            )
            require(
                not human_required,
                f"{label} technical work cannot require human authorization",
            )
            require(
                authorization_status in {"prospectively_authorized", "authorized"},
                f"{label} technical work needs controller authorization",
            )
            require(
                authorized_by == "controller",
                f"{label} technical work must be authorized by the controller",
            )
            _integer(
                decision.get("maximum_source_operations"),
                f"{label}.maximum_source_operations",
            )
            require(
                affected,
                f"{label} technical work must name bounded capability gates",
            )
            if attempt_id is None:
                require(
                    authorization_status == "prospectively_authorized",
                    f"{label} unallocated technical work must be prospectively authorized",
                )
            require(
                decided_at is not None,
                f"{label} technical work needs a decision timestamp",
            )
        else:
            require(
                review_effect and affects_review,
                f"{label} methodological work must affect review semantics",
            )
            require(
                human_required,
                f"{label} methodological work must require human authorization",
            )
            require(affected, f"{label} methodological work must name affected gates")
            require(
                authorization_status in {"pending", "authorized"},
                f"{label} methodological authorization is invalid",
            )
            if authorization_status == "pending":
                require(
                    authorized_by == "none",
                    f"{label} pending method decision has an authorizer",
                )
                require(
                    attempt_id is None,
                    f"{label} pending method decision cannot allocate an attempt",
                )
                require(
                    decided_at is None,
                    f"{label} pending method decision cannot have a timestamp",
                )
            else:
                require(
                    authorized_by == "human",
                    f"{label} method decision needs human authorizer",
                )
                require(
                    attempt_id is not None,
                    f"{label} method decision needs methodological attempt",
                )
                require(
                    decided_at is not None,
                    f"{label} method decision needs human timestamp",
                )

        decisions_by_id[decision_id] = decision
    return decisions_by_id


def _validate_semantic_impact(value: Any, label: str) -> dict[str, Any]:
    impact = _mapping(value, label)
    _require_fields(impact, {"classification", "review_effect", "rationale"}, label)
    classification = impact["classification"]
    require(classification in DECISION_CLASSES, f"{label}.classification is invalid")
    review_effect = _boolean(impact["review_effect"], f"{label}.review_effect")
    _string(impact["rationale"], f"{label}.rationale")
    require(
        review_effect is (classification == "human_methodological"),
        f"{label}.review_effect does not match its classification",
    )
    return impact


def _gate_evidence(value: Any, label: str) -> tuple[str, str, str]:
    item = _mapping(value, label)
    _require_fields(item, {"path", "sha256", "validity"}, label)
    path = _relative_path(item["path"], f"{label}.path")
    digest = _sha256(item["sha256"], f"{label}.sha256")
    validity = item["validity"]
    require(validity in {"valid", "invalidated"}, f"{label}.validity is invalid")
    return path, digest, validity


def _validate_gates(
    campaign: dict[str, Any],
    attempts: dict[str, dict[str, Any]],
    evidence_by_reference: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    gates = _list(campaign["capability_gates"], "campaign.capability_gates")
    require(gates, "campaign.capability_gates must not be empty")
    task_id = campaign["task_id"]
    gates_by_id: dict[str, dict[str, Any]] = {}
    checkpoint_ids: set[str] = set()

    for index, raw_gate in enumerate(gates):
        label = f"campaign.capability_gates[{index}]"
        gate = _mapping(raw_gate, label)
        _require_fields(
            gate,
            {
                "gate_id",
                "checkpoint_id",
                "attempt_id",
                "requirement",
                "depends_on",
                "status",
                "observed_basis",
                "original_observed_basis",
                "evidence",
                "reusable",
                "carried_forward",
                "carry_forward",
                "source_operation_count",
                "semantic_impact",
                "invalidation",
                "notes",
            },
            label,
        )
        gate_id = _pattern(gate["gate_id"], GATE_ID_RE, f"{label}.gate_id")
        require(gate_id not in gates_by_id, f"duplicate stable gate ID: {gate_id}")
        checkpoint_id = _pattern(
            gate["checkpoint_id"], CHECKPOINT_ID_RE, f"{label}.checkpoint_id"
        )
        require(
            checkpoint_id not in checkpoint_ids,
            f"duplicate checkpoint ID: {checkpoint_id}",
        )
        checkpoint_ids.add(checkpoint_id)
        attempt_id = _require_task_prefix(
            gate["attempt_id"], ATTEMPT_ID_RE, task_id, "P", f"{label}.attempt_id"
        )
        require(attempt_id in attempts, f"{label} references an unknown attempt")
        _string(gate["requirement"], f"{label}.requirement")
        dependencies = _unique_strings(
            _list(gate["depends_on"], f"{label}.depends_on"), f"{label}.depends_on"
        )
        require(gate_id not in dependencies, f"{label} cannot depend on itself")
        status = gate["status"]
        require(status in GATE_STATUSES, f"{label}.status is invalid")
        observed_basis = gate["observed_basis"]
        require(
            observed_basis in ORIGINAL_BASES | {"carried_forward"},
            f"{label}.observed_basis is invalid",
        )
        original_basis = gate["original_observed_basis"]
        require(
            original_basis in ORIGINAL_BASES,
            f"{label}.original_observed_basis is invalid",
        )
        evidence = _list(gate["evidence"], f"{label}.evidence")
        evidence_tuples = [
            _gate_evidence(raw_evidence, f"{label}.evidence[{evidence_index}]")
            for evidence_index, raw_evidence in enumerate(evidence)
        ]
        require(
            len(evidence_tuples)
            == len({(path, digest) for path, digest, _ in evidence_tuples}),
            f"{label}.evidence contains duplicate references",
        )
        reusable = _boolean(gate["reusable"], f"{label}.reusable")
        carried_forward = _boolean(gate["carried_forward"], f"{label}.carried_forward")
        source_operation_count = _integer(
            gate["source_operation_count"], f"{label}.source_operation_count"
        )
        performed = attempts[attempt_id]["source_operations"]["performed"]
        require(
            source_operation_count <= performed,
            f"{label}.source_operation_count exceeds its attempt's performed operations",
        )
        _validate_semantic_impact(gate["semantic_impact"], f"{label}.semantic_impact")
        _string(gate["notes"], f"{label}.notes", nonempty=False)

        carry_forward = gate["carry_forward"]
        if carried_forward:
            require(status == "passed", f"{label} may carry forward only a passed gate")
            require(reusable, f"{label} carried-forward evidence must be reusable")
            require(
                observed_basis == "carried_forward",
                f"{label} needs carried_forward basis",
            )
            _mapping(carry_forward, f"{label}.carry_forward")
        else:
            require(
                carry_forward is None,
                f"{label}.carry_forward must be null when not carried forward",
            )
            require(
                observed_basis != "carried_forward",
                f"{label} cannot claim carried_forward basis",
            )
            require(
                observed_basis == original_basis,
                f"{label} must retain its original observed basis",
            )

        invalidation = gate["invalidation"]
        if status == "passed":
            require(evidence_tuples, f"{label} passed status requires evidence")
            require(
                all(validity == "valid" for _, _, validity in evidence_tuples),
                f"{label} passed evidence must be valid",
            )
        elif status == "failed":
            require(evidence_tuples, f"{label} failed status requires failure evidence")
            require(
                all(validity == "valid" for _, _, validity in evidence_tuples),
                f"{label} failed evidence must be valid",
            )
            require(
                not reusable and not carried_forward,
                f"{label} failed evidence cannot be reusable or carried forward",
            )
            require(
                invalidation is None, f"{label} failed gate cannot cite an invalidation"
            )
        elif status == "invalidated":
            require(
                evidence_tuples, f"{label} invalidated status requires prior evidence"
            )
            require(
                all(validity == "invalidated" for _, _, validity in evidence_tuples),
                f"{label} invalidated evidence must be marked invalidated",
            )
            require(
                not reusable and not carried_forward,
                f"{label} invalidated evidence cannot be reusable or carried forward",
            )
            _mapping(invalidation, f"{label}.invalidation")
        else:
            require(
                not reusable and not carried_forward,
                f"{label} {status} evidence cannot be reusable or carried forward",
            )
            require(
                invalidation is None,
                f"{label} {status} gate cannot cite an invalidation",
            )

        if not carried_forward:
            for path, digest, validity in evidence_tuples:
                source = evidence_by_reference.get((attempt_id, path, digest))
                require(
                    source is not None,
                    f"{label} evidence is not catalogued by its attempt",
                )
                require(
                    source["gate_id"] == gate_id,
                    f"{label} evidence belongs to another gate",
                )
                require(
                    source["validity"] == validity,
                    f"{label} evidence validity differs from its attempt catalogue",
                )
                require(
                    source["basis"] == original_basis,
                    f"{label} evidence does not retain its original basis",
                )

        gates_by_id[gate_id] = gate

    for attempt_id, path, digest in evidence_by_reference:
        gate_id = evidence_by_reference[(attempt_id, path, digest)]["gate_id"]
        require(
            gate_id in gates_by_id,
            f"attempt {attempt_id} catalogs evidence for unknown gate {gate_id}",
        )
    return gates_by_id


def _validate_dependency_graph(gates: dict[str, dict[str, Any]]) -> None:
    for gate_id, gate in gates.items():
        for dependency in gate["depends_on"]:
            require(
                dependency in gates,
                f"gate {gate_id} depends on missing gate {dependency}",
            )

    states: dict[str, int] = {}

    def visit(gate_id: str) -> None:
        state = states.get(gate_id, 0)
        require(state != 1, f"capability-gate dependency cycle includes {gate_id}")
        if state == 2:
            return
        states[gate_id] = 1
        for dependency in gates[gate_id]["depends_on"]:
            visit(dependency)
        states[gate_id] = 2

    for gate_id in gates:
        visit(gate_id)


def _validate_decision_gate_references(
    decisions: dict[str, dict[str, Any]], gates: dict[str, dict[str, Any]]
) -> None:
    for decision_id, decision in decisions.items():
        for gate_id in decision["affected_gate_ids"]:
            require(
                gate_id in gates,
                f"decision {decision_id} affects unknown gate {gate_id}",
            )


def _validate_carry_forward(
    gates: dict[str, dict[str, Any]],
    attempts: dict[str, dict[str, Any]],
    evidence_by_reference: dict[tuple[str, str, str], dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> None:
    for gate_id, gate in gates.items():
        if not gate["carried_forward"]:
            continue
        label = f"gate {gate_id}.carry_forward"
        carry_forward = _mapping(gate["carry_forward"], label)
        _require_fields(
            carry_forward,
            {
                "from_attempt_id",
                "from_gate_id",
                "evidence",
                "original_observed_basis",
                "affected_by_code_or_semantic_change",
                "rationale",
            },
            label,
        )
        source_attempt_id = _pattern(
            carry_forward["from_attempt_id"], ATTEMPT_ID_RE, f"{label}.from_attempt_id"
        )
        require(
            source_attempt_id in attempts,
            f"{label} references an unknown prior attempt",
        )
        target_attempt = attempts[gate["attempt_id"]]
        source_attempt = attempts[source_attempt_id]
        require(
            source_attempt["immutable"] is True,
            f"{label} source attempt must be immutable",
        )
        require(
            source_attempt["sequence"] < target_attempt["sequence"],
            f"{label} must cite an earlier immutable attempt",
        )
        source_gate_id = _pattern(
            carry_forward["from_gate_id"], GATE_ID_RE, f"{label}.from_gate_id"
        )
        require(
            source_gate_id == gate_id,
            f"{label} must carry the same stable capability gate",
        )
        original_basis = carry_forward["original_observed_basis"]
        require(
            original_basis in ORIGINAL_BASES,
            f"{label}.original_observed_basis is invalid",
        )
        require(
            original_basis == gate["original_observed_basis"],
            f"{label} must retain the original observed basis",
        )
        require(
            carry_forward["affected_by_code_or_semantic_change"] is False,
            f"{label} cannot carry affected evidence",
        )
        _string(carry_forward["rationale"], f"{label}.rationale")
        references = _list(carry_forward["evidence"], f"{label}.evidence")
        require(references, f"{label}.evidence must not be empty")
        carry_tuples: list[tuple[str, str]] = []
        for index, raw_reference in enumerate(references):
            path, digest = _file_reference(raw_reference, f"{label}.evidence[{index}]")
            carry_tuples.append((path, digest))
            source = evidence_by_reference.get((source_attempt_id, path, digest))
            require(
                source is not None,
                f"{label} evidence path/hash is not in the cited attempt",
            )
            require(
                source["gate_id"] == source_gate_id,
                f"{label} evidence belongs to another gate",
            )
            require(
                source["validity"] == "valid",
                f"{label} cannot carry invalidated evidence",
            )
            require(
                source["basis"] == original_basis,
                f"{label} evidence does not retain the original basis",
            )
        require(
            len(carry_tuples) == len(set(carry_tuples)),
            f"{label}.evidence contains duplicate references",
        )
        current_tuples = {
            (path, digest)
            for path, digest, _ in (
                _gate_evidence(item, label) for item in gate["evidence"]
            )
        }
        require(
            current_tuples == set(carry_tuples),
            f"{label} must repeat the exact cited evidence path/hash",
        )
        require(
            gate["semantic_impact"]["classification"] == "none",
            f"{label} cannot carry evidence through a code or semantic impact",
        )

        source_sequence = source_attempt["sequence"]
        target_sequence = target_attempt["sequence"]
        for decision_id, decision in decisions.items():
            if (
                decision["decision_class"] == "none"
                or gate_id not in decision["affected_gate_ids"]
            ):
                continue
            decision_attempt_id = decision["attempt_id"]
            if decision_attempt_id is None:
                continue
            decision_sequence = attempts[decision_attempt_id]["sequence"]
            require(
                not (source_sequence < decision_sequence <= target_sequence),
                f"{label} is affected by decision {decision_id} and cannot be carried forward",
            )


def _failed_ancestors(
    gates: dict[str, dict[str, Any]], gate_id: str, cache: dict[str, set[str]]
) -> set[str]:
    if gate_id in cache:
        return cache[gate_id]
    failed: set[str] = set()
    for dependency in gates[gate_id]["depends_on"]:
        if gates[dependency]["status"] == "failed":
            failed.add(dependency)
        failed.update(_failed_ancestors(gates, dependency, cache))
    cache[gate_id] = failed
    return failed


def _validate_failure_invalidation(
    gates: dict[str, dict[str, Any]],
) -> None:
    cache: dict[str, set[str]] = {}
    for gate_id, gate in gates.items():
        failed_ancestors = _failed_ancestors(gates, gate_id, cache)
        if gate["status"] == "invalidated":
            invalidation = _mapping(
                gate["invalidation"], f"gate {gate_id}.invalidation"
            )
            _require_fields(
                invalidation,
                {"failed_gate_id", "rationale"},
                f"gate {gate_id}.invalidation",
            )
            failed_gate_id = _pattern(
                invalidation["failed_gate_id"],
                GATE_ID_RE,
                f"gate {gate_id}.invalidation.failed_gate_id",
            )
            _string(invalidation["rationale"], f"gate {gate_id}.invalidation.rationale")
            require(
                failed_gate_id in failed_ancestors,
                f"gate {gate_id} is not transitively invalidated by {failed_gate_id}",
            )
        elif failed_ancestors and gate["status"] == "passed":
            raise AssertionError(
                f"failed gate dependency leaves stale passed dependent {gate_id}"
            )
        elif failed_ancestors and gate["status"] in {"blocked", "untested"}:
            require(
                not gate["evidence"],
                f"failed gate dependency leaves non-invalidated evidence on {gate_id}",
            )


def _validate_allocations(
    campaign: dict[str, Any],
    attempts: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    gates: dict[str, dict[str, Any]],
) -> None:
    authorization = _mapping(
        campaign["controller_authorization"], "campaign.controller_authorization"
    )
    _require_fields(
        authorization,
        {
            "technical_corrective_attempts_authorized",
            "maximum_additional_attempts",
            "maximum_technical_corrective_attempts",
            "maximum_methodological_revision_attempts",
            "maximum_source_operations_per_attempt",
            "rationale",
        },
        "campaign.controller_authorization",
    )
    technical_authorized = _boolean(
        authorization["technical_corrective_attempts_authorized"],
        "campaign.controller_authorization.technical_corrective_attempts_authorized",
    )
    maximum_additional = _integer(
        authorization["maximum_additional_attempts"],
        "campaign.controller_authorization.maximum_additional_attempts",
    )
    maximum_technical = _integer(
        authorization["maximum_technical_corrective_attempts"],
        "campaign.controller_authorization.maximum_technical_corrective_attempts",
    )
    maximum_methodological = _integer(
        authorization["maximum_methodological_revision_attempts"],
        "campaign.controller_authorization.maximum_methodological_revision_attempts",
    )
    maximum_operations = _integer(
        authorization["maximum_source_operations_per_attempt"],
        "campaign.controller_authorization.maximum_source_operations_per_attempt",
    )
    _string(authorization["rationale"], "campaign.controller_authorization.rationale")
    require(
        maximum_technical <= maximum_additional,
        "technical corrective budget exceeds total additional-attempt budget",
    )
    require(
        maximum_methodological <= maximum_additional,
        "methodological revision budget exceeds total additional-attempt budget",
    )
    if technical_authorized:
        require(
            maximum_technical >= 1,
            "controller authorization needs a finite positive technical attempt bound",
        )
    else:
        require(
            maximum_technical == 0,
            "disabled controller authorization must allow zero technical attempts",
        )

    technical_attempts = 0
    methodological_attempts = 0
    decision_citations: dict[str, str] = {}
    ordered_attempts = sorted(attempts.items(), key=lambda item: item[1]["sequence"])
    for attempt_id, attempt in ordered_attempts:
        allocation = attempt["allocation"]
        kind = allocation["attempt_kind"]
        decision_id = allocation["authorization_decision_id"]
        decision = decisions.get(decision_id) if decision_id is not None else None
        if decision_id is not None:
            require(
                decision is not None,
                f"attempt {attempt_id} references an unknown authorization decision",
            )
            require(
                decision_id not in decision_citations,
                f"authorization decision {decision_id} is cited by more than one attempt",
            )
            decision_citations[decision_id] = attempt_id
        require(
            attempt["source_operations"]["predeclared_maximum"] <= maximum_operations,
            f"attempt {attempt_id} exceeds the finite source-operation budget",
        )
        if kind == "initial":
            require(
                attempt["sequence"] == 1,
                f"initial attempt {attempt_id} must have sequence 1",
            )
            require(
                allocation["authorized_by"] == "controller",
                f"initial attempt {attempt_id} must be controller-allocated",
            )
            require(
                decision_id is None,
                f"initial attempt {attempt_id} cannot cite an authorization decision",
            )
            require(
                not allocation["prospectively_authorized"],
                f"initial attempt {attempt_id} cannot be prospective",
            )
        elif kind == "technical_corrective":
            technical_attempts += 1
            require(
                technical_authorized,
                f"technical attempt {attempt_id} lacks controller authorization",
            )
            require(
                allocation["authorized_by"] == "controller",
                f"technical attempt {attempt_id} must be controller-authorized",
            )
            require(
                allocation["prospectively_authorized"] is True,
                f"technical attempt {attempt_id} must be prospectively authorized",
            )
            require(
                decision is not None, f"technical attempt {attempt_id} needs a decision"
            )
            require(
                decision["attempt_id"] in {None, attempt_id},
                f"technical decision for {attempt_id} must cite that attempt or prospectively authorize it",
            )
            require(
                decision["decision_class"] == "controller_technical",
                f"technical attempt {attempt_id} has the wrong decision class",
            )
            require(
                decision["human_authorization_required"] is False,
                f"technical attempt {attempt_id} cannot require human authorization",
            )
            decision_maximum = _integer(
                decision["maximum_source_operations"],
                f"decision {decision_id}.maximum_source_operations",
            )
            require(
                attempt["source_operations"]["predeclared_maximum"] <= decision_maximum,
                f"technical attempt {attempt_id} exceeds decision {decision_id}'s finite source-operation bound",
            )
            require(
                _parse_date_time(
                    decision.get("decided_at"), f"decision {decision_id}.decided_at"
                )
                <= _parse_date_time(
                    allocation["allocated_at"],
                    f"attempt {attempt_id}.allocation.allocated_at",
                ),
                f"technical decision for {attempt_id} must predate allocation",
            )
            if decision["attempt_id"] is None:
                enacted_technical_gates = {
                    gate_id
                    for gate_id, gate in gates.items()
                    if gate["attempt_id"] == attempt_id
                    and gate["semantic_impact"]["classification"]
                    == "controller_technical"
                }
                require(
                    enacted_technical_gates <= set(decision["affected_gate_ids"]),
                    f"prospective technical decision for {attempt_id} omits an enacted technical gate",
                )
        else:
            methodological_attempts += 1
            require(
                allocation["authorized_by"] == "human",
                f"methodological attempt {attempt_id} must be human-authorized",
            )
            require(
                not allocation["prospectively_authorized"],
                f"methodological attempt {attempt_id} cannot be controller-prospective",
            )
            require(
                decision is not None,
                f"methodological attempt {attempt_id} needs a decision",
            )
            require(
                decision["attempt_id"] == attempt_id,
                f"methodological decision for {attempt_id} must cite that attempt",
            )
            require(
                decision["decision_class"] == "human_methodological"
                and decision["authorization_status"] == "authorized",
                f"methodological attempt {attempt_id} lacks an authorized methodological decision",
            )
            require(
                decision.get("decided_at") is not None,
                f"methodological attempt {attempt_id} needs a human decision timestamp",
            )
            require(
                _parse_date_time(
                    decision.get("decided_at"), f"decision {decision_id}.decided_at"
                )
                <= _parse_date_time(
                    allocation["allocated_at"],
                    f"attempt {attempt_id}.allocation.allocated_at",
                ),
                f"methodological decision for {attempt_id} must predate allocation",
            )

    additional_attempts = len(attempts) - 1
    require(
        additional_attempts <= maximum_additional,
        "campaign exceeds its finite additional-attempt budget",
    )
    require(
        technical_attempts <= maximum_technical,
        "campaign has more technical corrective attempts than its finite controller budget allows",
    )
    require(
        methodological_attempts <= maximum_methodological,
        "campaign has more methodological revisions than its finite budget allows",
    )

    for decision_id, decision in decisions.items():
        decision_class = decision["decision_class"]
        if decision_class == "controller_technical":
            if decision["attempt_id"] is not None:
                attempt = attempts[decision["attempt_id"]]
                require(
                    decision_citations.get(decision_id) == decision["attempt_id"],
                    f"technical decision {decision_id} is not cited by its attempt",
                )
                require(
                    attempt["allocation"]["attempt_kind"] == "technical_corrective",
                    f"technical decision {decision_id} cannot authorize a non-technical attempt",
                )
            for gate_id in decision["affected_gate_ids"]:
                require(
                    gates[gate_id]["semantic_impact"]["classification"]
                    != "human_methodological",
                    f"technical decision {decision_id} cannot hide methodological gate {gate_id}",
                )
        elif (
            decision_class == "human_methodological"
            and decision["authorization_status"] == "authorized"
        ):
            attempt = attempts[decision["attempt_id"]]
            require(
                decision_citations.get(decision_id) == decision["attempt_id"],
                f"methodological decision {decision_id} is not cited by its attempt",
            )
            require(
                attempt["allocation"]["attempt_kind"] == "methodological_revision",
                f"methodological decision {decision_id} must authorize a methodological revision",
            )
            for gate_id in decision["affected_gate_ids"]:
                gate = gates[gate_id]
                require(
                    gate["semantic_impact"]["classification"] == "human_methodological",
                    f"methodological decision {decision_id} must affect methodological gate {gate_id}",
                )
                require(
                    gate["attempt_id"] == decision["attempt_id"],
                    f"methodological gate {gate_id} must be recorded in its methodological attempt",
                )

    for gate_id, gate in gates.items():
        if gate["semantic_impact"]["classification"] != "human_methodological":
            continue
        attempt = attempts[gate["attempt_id"]]
        pending_decisions = [
            decision
            for decision in decisions.values()
            if decision["decision_class"] == "human_methodological"
            and decision["authorization_status"] == "pending"
            and decision["attempt_id"] is None
            and gate_id in decision["affected_gate_ids"]
        ]
        decision_only = gate["status"] in {"blocked", "untested"} and bool(
            pending_decisions
        )
        if decision_only:
            require(
                attempt["allocation"]["attempt_kind"]
                in {"initial", "technical_corrective"},
                f"decision-only methodological gate {gate_id} must cite a prior technical observation",
            )
            require(
                gate["source_operation_count"] == 0,
                f"decision-only methodological gate {gate_id} cannot authorize source work",
            )
            continue

        require(
            attempt["allocation"]["attempt_kind"] == "methodological_revision",
            f"methodological gate {gate_id} cannot be hidden in a technical attempt",
        )
        matching_decisions = [
            decision
            for decision in decisions.values()
            if decision["decision_class"] == "human_methodological"
            and decision["authorization_status"] == "authorized"
            and decision["attempt_id"] == gate["attempt_id"]
            and gate_id in decision["affected_gate_ids"]
            and decision.get("decided_at") is not None
        ]
        require(
            matching_decisions,
            f"methodological gate {gate_id} lacks a human methodological decision and timestamp",
        )


def _validate_catalog(
    campaign: dict[str, Any],
    gates: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> None:
    method_type = campaign["method_type"]
    require(method_type in CAPABILITY_CATALOG, "campaign.method_type is invalid")
    catalog = _unique_strings(
        _list(campaign["capability_catalog"], "campaign.capability_catalog"),
        "campaign.capability_catalog",
    )
    expected = CAPABILITY_CATALOG[method_type]
    require(
        tuple(catalog) == expected,
        f"campaign capability catalog does not match the required {method_type} catalog",
    )
    if campaign["status"] != "accepted":
        return
    pending = [
        decision_id
        for decision_id, decision in decisions.items()
        if decision["decision_class"] == "human_methodological"
        and decision["authorization_status"] == "pending"
    ]
    require(not pending, "accepted campaign has pending human methodological decision")
    for gate_id in expected:
        require(
            gate_id in gates,
            f"accepted campaign is missing required catalog gate {gate_id}",
        )
        gate = gates[gate_id]
        require(
            gate["status"] == "passed", f"accepted catalog gate {gate_id} must pass"
        )
        require(
            gate["reusable"] is True,
            f"accepted catalog gate {gate_id} must be reusable",
        )
        require(
            gate["original_observed_basis"] in ACCEPTANCE_BASES,
            f"accepted catalog gate {gate_id} has inferred or untested basis",
        )
        evidence = _list(gate["evidence"], f"accepted catalog gate {gate_id}.evidence")
        require(evidence, f"accepted catalog gate {gate_id} lacks evidence")
        require(
            all(item["validity"] == "valid" for item in evidence),
            f"accepted catalog gate {gate_id} has invalid evidence",
        )
    for gate_id, gate in gates.items():
        require(
            gate["status"] == "passed", "accepted campaign requires every gate to pass"
        )
        require(
            gate["original_observed_basis"] in ACCEPTANCE_BASES,
            f"accepted campaign cannot use inferred or untested gate {gate_id}",
        )


def _validate_campaign_state(
    campaign: dict[str, Any],
    gates: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    attempts: dict[str, dict[str, Any]],
) -> None:
    status = campaign["status"]
    cancellation = campaign["cancellation"]
    acceptance = campaign["acceptance"]
    cancelled_attempts = [
        attempt_id
        for attempt_id, attempt in attempts.items()
        if attempt["terminal"]["outcome"] == "cancelled"
    ]
    if status == "cancelled":
        cancellation = _mapping(cancellation, "campaign.cancellation")
        _require_fields(
            cancellation,
            {
                "attempt_id",
                "kind",
                "cancelled_by",
                "cancelled_at",
                "reason",
                "provider_failure",
            },
            "campaign.cancellation",
        )
        attempt_id = _require_task_prefix(
            cancellation["attempt_id"],
            ATTEMPT_ID_RE,
            campaign["task_id"],
            "P",
            "campaign.cancellation.attempt_id",
        )
        require(
            attempt_id in attempts, "campaign cancellation references unknown attempt"
        )
        require(
            cancellation["kind"] == "operator_cancellation",
            "campaign cancellation must be an operator cancellation",
        )
        require(
            cancellation["cancelled_by"] == "operator",
            "campaign cancellation must name the operator",
        )
        _date_time(cancellation["cancelled_at"], "campaign.cancellation.cancelled_at")
        _string(cancellation["reason"], "campaign.cancellation.reason")
        require(
            cancellation["provider_failure"] is False,
            "operator cancellation is not provider failure",
        )
        require(acceptance is None, "cancelled campaign cannot have acceptance")
        require(
            attempts[attempt_id]["terminal"]["outcome"] == "cancelled",
            "campaign cancellation must link a cancelled attempt terminal outcome",
        )
        latest_attempt_id = max(attempts, key=lambda key: attempts[key]["sequence"])
        require(
            attempt_id == latest_attempt_id,
            "campaign cancellation must link the final allocated attempt",
        )
        return

    require(
        cancellation is None,
        "only a cancelled campaign may contain cancellation details",
    )
    require(
        not cancelled_attempts,
        "a cancelled attempt terminal outcome requires cancelled campaign status",
    )
    if status in {"ready_for_acceptance_review", "accepted"}:
        require(
            not any(
                attempt["terminal"]["terminal_verification"] == "legacy_unverifiable"
                for attempt in attempts.values()
            ),
            f"{status} cannot use legacy_unverifiable browser terminal evidence",
        )
    if status == "accepted":
        acceptance = _mapping(acceptance, "campaign.acceptance")
        _require_fields(
            acceptance,
            {"accepted_by", "accepted_at", "rationale"},
            "campaign.acceptance",
        )
        _string(acceptance["accepted_by"], "campaign.acceptance.accepted_by")
        _date_time(acceptance["accepted_at"], "campaign.acceptance.accepted_at")
        _string(acceptance["rationale"], "campaign.acceptance.rationale")
    else:
        require(
            acceptance is None,
            "only an accepted campaign may contain acceptance details",
        )

    pending_methodology = [
        decision_id
        for decision_id, decision in decisions.items()
        if decision["decision_class"] == "human_methodological"
        and decision["authorization_status"] == "pending"
    ]
    if pending_methodology:
        require(
            status == "methodological_decision_pending",
            "a pending methodological decision must set methodological_decision_pending status",
        )
    if status == "methodological_decision_pending":
        require(
            pending_methodology,
            "methodological_decision_pending needs a pending human methodological decision",
        )
    elif status == "technically_blocked":
        require(
            any(gate["status"] in {"failed", "blocked"} for gate in gates.values()),
            "technically_blocked needs a failed or blocked capability gate",
        )
    elif status in {"ready_for_acceptance_review", "accepted"}:
        require(
            all(gate["status"] == "passed" for gate in gates.values()),
            f"{status} requires every gate to pass",
        )


def validate_campaign_artifact(
    campaign: Any,
    *,
    campaign_schema: dict[str, Any] | None = None,
) -> None:
    """Validate schema and cross-record campaign invariants, without file I/O links."""
    if campaign_schema is None:
        campaign_schema = _mapping(
            load(SEARCHES / "schemas" / "pilot-campaign.schema.json"),
            "pilot campaign schema",
        )
    _validate_jsonschema_instance(campaign_schema, campaign, "campaign")
    campaign = _mapping(campaign, "campaign")
    _require_fields(
        campaign,
        {
            "schema_version",
            "campaign_id",
            "task_id",
            "source_id",
            "method_type",
            "protocol_fingerprint",
            "dictionary_fingerprint",
            "capability_catalog",
            "status",
            "created_at",
            "updated_at",
            "diagnostic_only",
            "screening_performed",
            "candidate_import_permitted",
            "candidate_records_imported",
            "retry_policy",
            "controller_authorization",
            "attempts",
            "capability_gates",
            "decisions",
            "cancellation",
            "acceptance",
        },
        "campaign",
    )
    require(
        campaign["schema_version"] == "slr1-pilot-campaign/v1",
        "campaign schema_version is invalid",
    )
    task_id = _pattern(campaign["task_id"], TASK_ID_RE, "campaign.task_id")
    _require_task_prefix(
        campaign["campaign_id"], CAMPAIGN_ID_RE, task_id, "C", "campaign.campaign_id"
    )
    _string(campaign["source_id"], "campaign.source_id")
    require(
        campaign["method_type"] in CAPABILITY_CATALOG, "campaign.method_type is invalid"
    )
    _sha256(campaign["protocol_fingerprint"], "campaign.protocol_fingerprint")
    _sha256(campaign["dictionary_fingerprint"], "campaign.dictionary_fingerprint")
    require(campaign["status"] in CAMPAIGN_STATUSES, "campaign.status is invalid")
    created_at = _parse_date_time(campaign["created_at"], "campaign.created_at")
    updated_at = _parse_date_time(campaign["updated_at"], "campaign.updated_at")
    require(
        updated_at >= created_at,
        "campaign.updated_at must not predate campaign.created_at",
    )
    require(campaign["diagnostic_only"] is True, "campaign must remain diagnostic-only")
    require(
        campaign["screening_performed"] is False, "campaign must not screen records"
    )
    require(
        campaign["candidate_import_permitted"] is False,
        "campaign must not permit candidate import",
    )
    candidate_records_imported = _integer(
        campaign["candidate_records_imported"], "campaign.candidate_records_imported"
    )
    require(
        candidate_records_imported == 0, "campaign must import zero candidate records"
    )

    attempts, evidence_by_reference, retry_records = _validate_attempts(campaign)
    _validate_retry_policy(campaign, retry_records)
    decisions = _validate_decisions(campaign, attempts)
    gates = _validate_gates(campaign, attempts, evidence_by_reference)
    _validate_decision_gate_references(decisions, gates)
    _validate_dependency_graph(gates)
    _validate_carry_forward(gates, attempts, evidence_by_reference, decisions)
    _validate_failure_invalidation(gates)
    _validate_allocations(campaign, attempts, decisions, gates)
    _validate_catalog(campaign, gates, decisions)
    _validate_campaign_state(campaign, gates, decisions, attempts)


def _source_packet_for_campaign(campaign_path: Path, sources_root: Path) -> Path:
    try:
        relative = campaign_path.relative_to(sources_root)
    except ValueError as exc:
        raise AssertionError(
            f"campaign is outside searches/sources: {campaign_path}"
        ) from exc
    require(
        len(relative.parts) >= 2,
        f"campaign is not inside a source packet: {campaign_path}",
    )
    source_packet = sources_root / relative.parts[0]
    try:
        sources_resolved = sources_root.resolve(strict=True)
        packet_resolved = source_packet.resolve(strict=True)
        campaign_resolved = campaign_path.resolve(strict=True)
        packet_resolved.relative_to(sources_resolved)
        campaign_resolved.relative_to(packet_resolved)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise AssertionError(
            f"campaign path escapes its source packet: {campaign_path}"
        ) from exc
    return source_packet


def _read_source_file(
    source_packet: Path, relative_path: Any, expected_sha256: Any, label: str
) -> bytes:
    relative_path = _relative_path(relative_path, f"{label}.path")
    expected_sha256 = _sha256(expected_sha256, f"{label}.sha256")
    try:
        packet_resolved = source_packet.resolve(strict=True)
        candidate = source_packet / relative_path
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(packet_resolved)
        require(resolved.is_file(), f"{label} is not a regular file")
        contents = resolved.read_bytes()
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise AssertionError(
            f"{label} escapes or is missing from its source packet"
        ) from exc
    actual_sha256 = hashlib.sha256(contents).hexdigest()
    require(actual_sha256 == expected_sha256, f"{label} SHA-256 does not match")
    return contents


def _manifest_terminal_projection(terminal: dict[str, Any]) -> dict[str, Any]:
    """Project campaign terminal data into the older manifest terminal shape."""
    return {
        key: value for key, value in terminal.items() if key != "terminal_verification"
    }


def _validate_manifest_link(
    manifest: Any,
    campaign: dict[str, Any],
    attempt: dict[str, Any],
    label: str,
) -> bool:
    manifest = _mapping(manifest, label)
    require(
        manifest.get("pilot_id") == attempt["attempt_id"],
        f"{label}.pilot_id does not match campaign attempt",
    )
    require(
        manifest.get("task_id") == campaign["task_id"],
        f"{label}.task_id does not match campaign task",
    )
    require(
        manifest.get("source_id") == campaign["source_id"],
        f"{label}.source_id does not match campaign source",
    )
    require(
        manifest.get("method_type") == campaign["method_type"],
        f"{label}.method_type does not match campaign method",
    )
    has_campaign_link = "campaign" in manifest
    has_terminal_link = "attempt_terminal" in manifest
    if not has_campaign_link and not has_terminal_link:
        # Campaign and terminal links were additive fields. The immutable v1
        # manifests already recorded the identity above and must not be
        # rewritten merely because a later campaign points at them.
        return True

    require(has_campaign_link, f"{label}.attempt_terminal requires a campaign link")
    link = manifest["campaign"]
    require(isinstance(link, dict), f"{label}.campaign link is invalid")
    require(
        link.get("campaign_id") == campaign["campaign_id"],
        f"{label}.campaign_id does not match campaign",
    )
    require(
        link.get("attempt_id") == attempt["attempt_id"],
        f"{label}.campaign.attempt_id does not match attempt",
    )
    if has_terminal_link:
        require(
            manifest["attempt_terminal"]
            == _manifest_terminal_projection(attempt["terminal"]),
            f"{label}.attempt_terminal does not match campaign terminal outcome",
        )
    return False


def _validate_campaign_files(
    campaign: dict[str, Any],
    source_packet: Path,
    manifest_schema: dict[str, Any],
) -> None:
    """Hash every declared campaign file and validate each linked manifest."""
    for index, attempt in enumerate(campaign["attempts"]):
        label = f"campaign.attempts[{index}].manifest"
        contents = _read_source_file(
            source_packet,
            attempt["manifest_path"],
            attempt["manifest_sha256"],
            label,
        )
        try:
            manifest = json.loads(contents)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{label} is not valid JSON") from exc
        _validate_jsonschema_instance(manifest_schema, manifest, label)
        _validate_pilot_manifest_formats(manifest, label)
        legacy_manifest = _validate_manifest_link(manifest, campaign, attempt, label)

        terminal = attempt["terminal"]
        if terminal["terminal_verification"] == "legacy_unverifiable":
            require(
                legacy_manifest,
                f"{label} legacy_unverifiable terminal requires an immutable legacy manifest without campaign or attempt_terminal links",
            )
        if (
            terminal["browser_backed"]
            and terminal["terminal_verification"] == "verified"
        ):
            for receipt_name in ("cleanup_receipt", "lease_receipt"):
                receipt = terminal[receipt_name]
                if receipt_name == "lease_receipt":
                    path, digest = _shared_lease_reference(
                        receipt,
                        f"campaign.attempts[{index}].terminal.{receipt_name}",
                    )
                else:
                    path, digest = _file_reference(
                        receipt, f"campaign.attempts[{index}].terminal.{receipt_name}"
                    )
                _read_source_file(
                    source_packet,
                    path,
                    digest,
                    f"campaign.attempts[{index}].terminal.{receipt_name}",
                )

        for operation_index, operation in enumerate(
            attempt["source_operations"]["operations"]
        ):
            retry = operation["retry"]
            if retry is None:
                continue
            path, digest = _file_reference(
                retry["receipt"],
                f"campaign.attempts[{index}].source_operations.operations[{operation_index}].retry.receipt",
            )
            _read_source_file(
                source_packet,
                path,
                digest,
                f"campaign.attempts[{index}].source_operations.operations[{operation_index}].retry.receipt",
            )

        for evidence_index, evidence in enumerate(attempt["evidence"]):
            _read_source_file(
                source_packet,
                evidence["path"],
                evidence["sha256"],
                f"campaign.attempts[{index}].evidence[{evidence_index}]",
            )

    for gate_index, gate in enumerate(campaign["capability_gates"]):
        for evidence_index, evidence in enumerate(gate["evidence"]):
            _read_source_file(
                source_packet,
                evidence["path"],
                evidence["sha256"],
                f"campaign.capability_gates[{gate_index}].evidence[{evidence_index}]",
            )
        carry_forward = gate["carry_forward"]
        if carry_forward is not None:
            for evidence_index, evidence in enumerate(carry_forward["evidence"]):
                _read_source_file(
                    source_packet,
                    evidence["path"],
                    evidence["sha256"],
                    f"campaign.capability_gates[{gate_index}].carry_forward.evidence[{evidence_index}]",
                )


def _validate_campaign_file(
    campaign_path: Path,
    searches_root: Path,
    schemas: dict[str, dict[str, Any]],
) -> None:
    source_packet = _source_packet_for_campaign(
        campaign_path, searches_root / "sources"
    )
    campaign = load(campaign_path)
    validate_campaign_artifact(
        campaign, campaign_schema=schemas["pilot-campaign.schema.json"]
    )
    packet_task_prefix = campaign["task_id"].lower()
    require(
        source_packet.name == packet_task_prefix
        or source_packet.name.startswith(f"{packet_task_prefix}-"),
        "source packet has the wrong task prefix",
    )
    _validate_campaign_files(
        campaign,
        source_packet,
        schemas["pilot-manifest.schema.json"],
    )


def validate_campaign_file(
    campaign_path: Path,
    *,
    searches_root: Path = SEARCHES,
) -> None:
    _validate_campaign_file(campaign_path, searches_root, _load_schemas(searches_root))


def validate_campaign_artifacts(searches_root: Path = SEARCHES) -> int:
    """Scan every real campaign.json beneath searches/sources, not just templates."""
    source_root = searches_root / "sources"
    require(source_root.is_dir(), f"missing source packet root: {source_root}")
    schemas = _load_schemas(searches_root)
    paths = sorted(source_root.rglob("campaign.json"))
    for campaign_path in paths:
        _validate_campaign_file(campaign_path, searches_root, schemas)
    return len(paths)


def validate_campaign_template() -> None:
    schemas = _load_schemas(SEARCHES)
    validate_campaign_artifact(
        load(SEARCHES / "templates" / "pilot-campaign.template.json"),
        campaign_schema=schemas["pilot-campaign.schema.json"],
    )


def validate_legacy_pilot_manifests(searches_root: Path = SEARCHES) -> int:
    """Validate all v1 manifests while keeping campaign fields optional for legacy data."""
    schemas = _load_schemas(searches_root)
    schema = schemas["pilot-manifest.schema.json"]
    paths = sorted((searches_root / "sources").rglob("manifest.json"))
    require(paths, "expected existing pilot manifests")
    legacy_count = 0
    for path in paths:
        manifest = _mapping(load(path), f"legacy manifest {path}")
        if "campaign" not in manifest:
            legacy_count += 1
        label = f"legacy manifest {path.relative_to(searches_root.parent)}"
        _validate_pilot_manifest_formats(manifest, label)
        _validate_jsonschema_instance(schema, manifest, label)
    require(
        legacy_count > 0, "expected at least one unchanged pre-campaign pilot manifest"
    )
    return legacy_count


def _normalize_mode(mode: str) -> str:
    aliases = {
        "pre-final": "pre-final",
        "pre-r002": "pre-final",
        "pre-R002": "pre-final",
        "final": "final",
        "r002": "final",
        "R002": "final",
    }
    require(mode in aliases, f"unknown validation mode: {mode}")
    return aliases[mode]


def validate_final_events(
    mode: str = "pre-final", searches_root: Path = SEARCHES
) -> None:
    mode = _normalize_mode(mode)
    final_events = searches_root / "final-events"
    require(final_events.is_dir(), f"missing final-events directory: {final_events}")
    final_files = [
        path
        for path in final_events.rglob("*")
        if path.is_file() and path.name != "README.md"
    ]
    if mode == "pre-final":
        require(
            not final_files,
            f"final-events contains premature artifacts: {final_files}",
        )


def validate_layout(mode: str = "pre-final", searches_root: Path = SEARCHES) -> None:
    root = searches_root.parent
    required = [
        root / "search-log.md",
        searches_root / "README.md",
        searches_root / "templates" / "source-guideline.md",
        searches_root / "templates" / "source-pilot-prompt.md",
        searches_root / "templates" / "pilot-campaign.template.json",
        searches_root / "templates" / "pilot-manifest.template.json",
        searches_root / "final-events" / "README.md",
    ]
    for path in required:
        require(path.is_file(), f"missing required artifact: {path.relative_to(root)}")
    validate_final_events(mode, searches_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        default="pre-final",
        choices=("pre-final", "final", "pre-r002", "pre-R002", "r002", "R002"),
        help="pre-final rejects final-events; final (R002) permits them",
    )
    args = parser.parse_args(argv)
    try:
        # Do this before any infrastructure work so plain Python cannot silently
        # skip JSON Schema or format validation.
        _jsonschema_components()
        checks = [
            validate_dictionary,
            validate_crosswalk,
            validate_schemas,
            validate_campaign_template,
            validate_campaign_artifacts,
            validate_legacy_pilot_manifests,
        ]
        for check in checks:
            result = check()
            suffix = f" ({result})" if check is validate_campaign_artifacts else ""
            print(f"ok: {check.__name__}{suffix}")
        validate_layout(args.mode)
        print("ok: validate_layout")
        print("SLR1 search infrastructure validation passed")
        return 0
    except (
        AssertionError,
        KeyError,
        TypeError,
        RuntimeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
