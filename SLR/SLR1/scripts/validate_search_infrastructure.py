#!/usr/bin/env python3
"""Validate the new-run SLR1 search infrastructure without using prior-run data."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
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

CAMPAIGN_STATUSES = {
    "in_progress",
    "technically_blocked",
    "methodological_decision_pending",
    "ready_for_acceptance_review",
    "accepted",
    "cancelled",
}
GATE_STATUSES = {"passed", "failed", "blocked", "untested", "invalidated"}
DECISION_CLASSES = {"none", "controller_technical", "human_methodological"}
DECISION_AUTHORIZATION_STATUSES = {
    "not_required",
    "prospectively_authorized",
    "pending",
    "authorized",
}
OBSERVED_BASES = {
    "observed",
    "official_documentation",
    "observed_and_documented",
    "inferred",
    "untested",
    "carried_forward",
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


def _date_time(value: Any, label: str) -> str:
    value = _string(value, label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AssertionError(f"{label} must be an ISO 8601 date-time") from exc
    require(parsed.tzinfo is not None, f"{label} must include a timezone")
    return value


def _unique_strings(values: list[Any], label: str) -> list[str]:
    strings = [
        _string(value, f"{label}[{index}]") for index, value in enumerate(values)
    ]
    require(len(strings) == len(set(strings)), f"{label} contains duplicate values")
    return strings


def expression_refs(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.get("args", []):
            yield from expression_refs(item)


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
        {x["id"] for x in local["expansion_candidates"]} == {"BG1", "BG2", "BC1"},
        "local expansions differ",
    )


def validate_crosswalk() -> None:
    data = load(SEARCHES / "source-interface-prisma-crosswalk.json")
    sources = data["sources"]
    interfaces = data["interfaces"]
    require(len(sources) == 15, f"crosswalk has {len(sources)} source rows")
    require(len({x["source_id"] for x in sources}) == 15, "source IDs are not unique")
    require(len(interfaces) == 13, f"crosswalk has {len(interfaces)} interfaces")
    interface_ids = {x["interface_id"] for x in interfaces}
    require(len(interface_ids) == 13, "interface IDs are not unique")
    require(
        {x["task_id"] for x in sources} == EXPECTED_TASKS,
        "source task coverage differs",
    )
    require(
        all(x["interface_id"] in interface_ids for x in sources),
        "source references unknown interface",
    )
    oatd = next(x for x in sources if x["source_id"] == "oatd")
    require(oatd["prisma_2020_column"] == "other_methods", "OATD PRISMA column differs")
    require(
        all(
            x["prisma_2020_column"] == "databases_registers"
            for x in sources
            if x["source_id"] != "oatd"
        ),
        "a non-OATD source is outside databases/registers",
    )
    require(
        all(x["separate_total"] is True for x in sources),
        "a source lacks a separate total",
    )


def _jsonschema_components() -> tuple[Any, Any] | None:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return None
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


def _validate_jsonschema_instance(
    schema: dict[str, Any], instance: Any, label: str
) -> None:
    components = _jsonschema_components()
    if components is None:
        return
    validator_class, format_checker_class = components
    validator = validator_class(schema, format_checker=format_checker_class())
    errors = sorted(
        validator.iter_errors(instance), key=lambda error: list(error.absolute_path)
    )
    require(not errors, f"{label} does not validate: {errors[0].message}")


def _validate_pilot_manifest_formats(manifest: Any, label: str) -> None:
    """Check every date-time and URI format used by the v1 pilot manifest."""
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


def validate_schemas() -> None:
    schema_paths = sorted((SEARCHES / "schemas").glob("*.schema.json"))
    require(len(schema_paths) == 4, "expected exactly four infrastructure schemas")
    schemas = {path.name: load(path) for path in schema_paths}
    for name, schema in schemas.items():
        _validate_schema_document(schema, f"schema {name}")

    components = _jsonschema_components()
    if components is not None:
        validator_class, _ = components
        for schema in schemas.values():
            validator_class.check_schema(schema)

    pilot_template = load(SEARCHES / "templates" / "pilot-manifest.template.json")
    _validate_pilot_manifest_formats(pilot_template, "pilot manifest template")
    _validate_jsonschema_instance(
        schemas["pilot-manifest.schema.json"],
        pilot_template,
        "pilot manifest template",
    )
    _validate_jsonschema_instance(
        schemas["pilot-campaign.schema.json"],
        load(SEARCHES / "templates" / "pilot-campaign.template.json"),
        "pilot campaign template",
    )


def _validate_source_operation(operation: Any, label: str) -> None:
    operation = _mapping(operation, label)
    _require_fields(
        operation,
        {
            "operation_id",
            "outcome",
            "source_reported_total",
            "records_retrieved",
            "records_imported",
        },
        label,
    )
    _string(operation["operation_id"], f"{label}.operation_id")
    outcome = operation["outcome"]
    require(
        outcome in {"success", "explicit_zero", "failed"}, f"{label}.outcome is invalid"
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
        require(total is None, f"{label} failure must report a null total, not zero")
        require(retrieved == 0, f"{label} failure must retrieve zero records")


def _validate_attempts(
    campaign: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str, str], dict[str, Any]]]:
    attempts = _list(campaign["attempts"], "campaign.attempts")
    require(attempts, "campaign.attempts must not be empty")
    attempts_by_id: dict[str, dict[str, Any]] = {}
    sequences: list[int] = []
    evidence_by_reference: dict[tuple[str, str, str], dict[str, Any]] = {}
    evidence_ids: set[str] = set()

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
            },
            label,
        )
        attempt_id = _pattern(
            attempt["attempt_id"], ATTEMPT_ID_RE, f"{label}.attempt_id"
        )
        require(
            attempt_id not in attempts_by_id,
            f"duplicate immutable attempt ID: {attempt_id}",
        )
        sequence = _integer(attempt["sequence"], f"{label}.sequence", minimum=1)
        sequences.append(sequence)
        _string(attempt["manifest_path"], f"{label}.manifest_path")
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
            _string(decision_id, f"{label}.allocation.authorization_decision_id")
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
        operation_ids: set[str] = set()
        for operation_index, operation in enumerate(operations):
            _validate_source_operation(
                operation, f"{label}.source_operations.operations[{operation_index}]"
            )
            operation_id = operation["operation_id"]
            require(
                operation_id not in operation_ids,
                f"{label}.source_operations has duplicate operation IDs",
            )
            operation_ids.add(operation_id)

        evidence = _list(attempt["evidence"], f"{label}.evidence")
        for evidence_index, raw_evidence in enumerate(evidence):
            evidence_label = f"{label}.evidence[{evidence_index}]"
            item = _mapping(raw_evidence, evidence_label)
            _require_fields(
                item,
                {"evidence_id", "gate_id", "path", "sha256", "validity"},
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
            path = _string(item["path"], f"{evidence_label}.path")
            digest = _sha256(item["sha256"], f"{evidence_label}.sha256")
            require(
                item["validity"] in {"valid", "invalidated"},
                f"{evidence_label}.validity is invalid",
            )
            reference = (attempt_id, path, digest)
            require(
                reference not in evidence_by_reference,
                f"duplicate evidence reference in {attempt_id}",
            )
            evidence_by_reference[reference] = item

        attempts_by_id[attempt_id] = attempt

    require(
        len(sequences) == len(set(sequences)),
        "campaign attempt sequences are not unique",
    )
    require(
        sorted(sequences) == list(range(1, len(sequences) + 1)),
        "campaign attempt sequences must be contiguous from one",
    )
    return attempts_by_id, evidence_by_reference


def _validate_decisions(
    campaign: dict[str, Any], attempts: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    decisions = _list(campaign["decisions"], "campaign.decisions")
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
            _pattern(attempt_id, ATTEMPT_ID_RE, f"{label}.attempt_id")
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
            expected_authorizer = (
                "none" if authorization_status == "pending" else "human"
            )
            require(
                authorized_by == expected_authorizer,
                f"{label} methodological authorization has the wrong authorizer",
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
    path = _string(item["path"], f"{label}.path")
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
        attempt_id = _pattern(gate["attempt_id"], ATTEMPT_ID_RE, f"{label}.attempt_id")
        require(attempt_id in attempts, f"{label} references an unknown attempt")
        _string(gate["requirement"], f"{label}.requirement")
        dependencies = _unique_strings(
            _list(gate["depends_on"], f"{label}.depends_on"), f"{label}.depends_on"
        )
        require(gate_id not in dependencies, f"{label} cannot depend on itself")
        status = gate["status"]
        require(status in GATE_STATUSES, f"{label}.status is invalid")
        require(
            gate["observed_basis"] in OBSERVED_BASES,
            f"{label}.observed_basis is invalid",
        )
        evidence = _list(gate["evidence"], f"{label}.evidence")
        evidence_tuples: list[tuple[str, str, str]] = []
        for evidence_index, raw_evidence in enumerate(evidence):
            evidence_tuples.append(
                _gate_evidence(raw_evidence, f"{label}.evidence[{evidence_index}]")
            )
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
                gate["observed_basis"] == "carried_forward",
                f"{label} needs carried_forward basis",
            )
            _mapping(carry_forward, f"{label}.carry_forward")
        else:
            require(
                carry_forward is None,
                f"{label}.carry_forward must be null when not carried forward",
            )
            require(
                gate["observed_basis"] != "carried_forward",
                f"{label} cannot claim carried_forward basis",
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

        gates_by_id[gate_id] = gate

    for attempt_id, path, digest in evidence_by_reference:
        gate_id = evidence_by_reference[(attempt_id, path, digest)]["gate_id"]
        require(
            gate_id in gates_by_id,
            f"attempt {attempt_id} catalogs evidence for unknown gate {gate_id}",
        )
    return gates_by_id


def _validate_dependency_graph(gates: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    dependents: dict[str, set[str]] = defaultdict(set)
    for gate_id, gate in gates.items():
        for dependency in gate["depends_on"]:
            require(
                dependency in gates,
                f"gate {gate_id} depends on missing gate {dependency}",
            )
            dependents[dependency].add(gate_id)

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
    return dependents


def _validate_decision_gate_references(
    decisions: dict[str, dict[str, Any]], gates: dict[str, dict[str, Any]]
) -> None:
    for decision_id, decision in decisions.items():
        for gate_id in decision["affected_gate_ids"]:
            require(
                gate_id in gates,
                f"decision {decision_id} affects unknown gate {gate_id}",
            )


def _validate_methodological_gate_authorization(
    gates: dict[str, dict[str, Any]], decisions: dict[str, dict[str, Any]]
) -> None:
    for gate_id, gate in gates.items():
        if gate["semantic_impact"]["classification"] != "human_methodological":
            continue
        matching_decisions = [
            decision
            for decision in decisions.values()
            if decision["decision_class"] == "human_methodological"
            and gate_id in decision["affected_gate_ids"]
        ]
        require(
            matching_decisions,
            f"methodological gate {gate_id} lacks a human methodological decision",
        )
        if gate["status"] not in {"blocked", "untested"}:
            require(
                any(
                    decision["authorization_status"] == "authorized"
                    for decision in matching_decisions
                ),
                f"methodological gate {gate_id} lacks completed human authorization",
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
        require(
            carry_forward["affected_by_code_or_semantic_change"] is False,
            f"{label} cannot carry affected evidence",
        )
        _string(carry_forward["rationale"], f"{label}.rationale")
        references = _list(carry_forward["evidence"], f"{label}.evidence")
        require(references, f"{label}.evidence must not be empty")
        carry_tuples: list[tuple[str, str]] = []
        for index, raw_reference in enumerate(references):
            reference = _mapping(raw_reference, f"{label}.evidence[{index}]")
            _require_fields(reference, {"path", "sha256"}, f"{label}.evidence[{index}]")
            path = _string(reference["path"], f"{label}.evidence[{index}].path")
            digest = _sha256(reference["sha256"], f"{label}.evidence[{index}].sha256")
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

        target_sequence = target_attempt["sequence"]
        for decision_id, decision in decisions.items():
            if gate_id not in decision["affected_gate_ids"]:
                continue
            decision_attempt_id = decision["attempt_id"]
            decision_sequence = (
                0
                if decision_attempt_id is None
                else attempts[decision_attempt_id]["sequence"]
            )
            require(
                decision_sequence > target_sequence,
                f"{label} is affected by decision {decision_id} and cannot be carried forward",
            )


def _descendants(failed_gate_id: str, dependents: dict[str, set[str]]) -> set[str]:
    descendants: set[str] = set()
    pending = list(dependents[failed_gate_id])
    while pending:
        gate_id = pending.pop()
        if gate_id in descendants:
            continue
        descendants.add(gate_id)
        pending.extend(dependents[gate_id])
    return descendants


def _validate_failure_invalidation(
    gates: dict[str, dict[str, Any]],
    attempts: dict[str, dict[str, Any]],
    dependents: dict[str, set[str]],
) -> None:
    failed_gate_ids = {
        gate_id for gate_id, gate in gates.items() if gate["status"] == "failed"
    }
    closures = {
        gate_id: _descendants(gate_id, dependents) for gate_id in failed_gate_ids
    }

    for gate_id, gate in gates.items():
        if gate["status"] != "invalidated":
            continue
        invalidation = _mapping(gate["invalidation"], f"gate {gate_id}.invalidation")
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
            failed_gate_id in failed_gate_ids,
            f"gate {gate_id} is not invalidated by a failed gate",
        )
        require(
            gate_id in closures[failed_gate_id],
            f"gate {gate_id} is not a declared dependent of {failed_gate_id}",
        )

    for failed_gate_id, descendants in closures.items():
        failed_sequence = attempts[gates[failed_gate_id]["attempt_id"]]["sequence"]
        for gate_id in descendants:
            gate = gates[gate_id]
            if gate["status"] != "passed":
                continue
            gate_sequence = attempts[gate["attempt_id"]]["sequence"]
            require(
                gate_sequence > failed_sequence and not gate["carried_forward"],
                f"failed gate {failed_gate_id} leaves stale passed dependent {gate_id}",
            )


def _validate_allocations(
    campaign: dict[str, Any],
    attempts: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> None:
    authorization = _mapping(
        campaign["controller_authorization"], "campaign.controller_authorization"
    )
    _require_fields(
        authorization,
        {
            "technical_corrective_attempts_authorized",
            "maximum_additional_attempts",
            "maximum_source_operations_per_attempt",
            "rationale",
        },
        "campaign.controller_authorization",
    )
    technical_authorized = _boolean(
        authorization["technical_corrective_attempts_authorized"],
        "campaign.controller_authorization.technical_corrective_attempts_authorized",
    )
    maximum_attempts = _integer(
        authorization["maximum_additional_attempts"],
        "campaign.controller_authorization.maximum_additional_attempts",
    )
    maximum_operations = _integer(
        authorization["maximum_source_operations_per_attempt"],
        "campaign.controller_authorization.maximum_source_operations_per_attempt",
    )
    _string(authorization["rationale"], "campaign.controller_authorization.rationale")
    if technical_authorized:
        require(
            maximum_attempts >= 1,
            "controller authorization needs a finite positive attempt bound",
        )
    else:
        require(
            maximum_attempts == 0,
            "disabled controller authorization must allow zero additional attempts",
        )

    technical_attempts = 0
    for attempt_id, attempt in attempts.items():
        allocation = attempt["allocation"]
        kind = allocation["attempt_kind"]
        decision_id = allocation["authorization_decision_id"]
        decision = decisions.get(decision_id) if decision_id is not None else None
        if decision_id is not None:
            require(
                decision is not None,
                f"attempt {attempt_id} references an unknown authorization decision",
            )
        if kind == "initial":
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
                decision["attempt_id"] == attempt_id,
                f"technical decision for {attempt_id} must cite that attempt",
            )
            require(
                decision["decision_class"] == "controller_technical",
                f"technical attempt {attempt_id} has the wrong decision class",
            )
            require(
                decision["human_authorization_required"] is False,
                f"technical attempt {attempt_id} cannot require human authorization",
            )
            require(
                attempt["source_operations"]["predeclared_maximum"]
                <= maximum_operations,
                f"technical attempt {attempt_id} exceeds the controller source-operation bound",
            )
        else:
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
        technical_attempts <= maximum_attempts,
        "campaign has more technical corrective attempts than its finite controller authorization allows",
    )


def _validate_campaign_state(
    campaign: dict[str, Any],
    gates: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
) -> None:
    status = campaign["status"]
    cancellation = campaign["cancellation"]
    acceptance = campaign["acceptance"]
    if status == "cancelled":
        cancellation = _mapping(cancellation, "campaign.cancellation")
        _require_fields(
            cancellation,
            {"kind", "cancelled_by", "cancelled_at", "reason", "provider_failure"},
            "campaign.cancellation",
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
        return

    require(
        cancellation is None,
        "only a cancelled campaign may contain cancellation details",
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


def validate_campaign_artifact(campaign: Any) -> None:
    """Validate cross-record campaign rules that JSON Schema cannot express."""
    campaign = _mapping(campaign, "campaign")
    _require_fields(
        campaign,
        {
            "schema_version",
            "campaign_id",
            "task_id",
            "source_id",
            "status",
            "created_at",
            "updated_at",
            "diagnostic_only",
            "screening_performed",
            "candidate_import_permitted",
            "candidate_records_imported",
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
    _pattern(campaign["campaign_id"], CAMPAIGN_ID_RE, "campaign.campaign_id")
    _pattern(campaign["task_id"], TASK_ID_RE, "campaign.task_id")
    _string(campaign["source_id"], "campaign.source_id")
    require(campaign["status"] in CAMPAIGN_STATUSES, "campaign.status is invalid")
    _date_time(campaign["created_at"], "campaign.created_at")
    _date_time(campaign["updated_at"], "campaign.updated_at")
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

    attempts, evidence_by_reference = _validate_attempts(campaign)
    decisions = _validate_decisions(campaign, attempts)
    gates = _validate_gates(campaign, attempts, evidence_by_reference)
    _validate_decision_gate_references(decisions, gates)
    _validate_methodological_gate_authorization(gates, decisions)
    dependents = _validate_dependency_graph(gates)
    _validate_carry_forward(gates, attempts, evidence_by_reference, decisions)
    _validate_failure_invalidation(gates, attempts, dependents)
    _validate_allocations(campaign, attempts, decisions)
    _validate_campaign_state(campaign, gates, decisions)


def validate_campaign_template() -> None:
    validate_campaign_artifact(
        load(SEARCHES / "templates" / "pilot-campaign.template.json")
    )


def validate_legacy_pilot_manifests() -> None:
    """Keep v1 pilot manifests valid when the optional campaign link is absent."""
    schema = load(SEARCHES / "schemas" / "pilot-manifest.schema.json")
    required = set(schema["required"])
    allowed = set(schema["properties"])
    paths = sorted((SEARCHES / "sources").rglob("manifest.json"))
    require(paths, "expected existing pilot manifests")
    legacy_count = 0
    for path in paths:
        manifest = _mapping(load(path), f"legacy manifest {path.relative_to(ROOT)}")
        require(
            required <= set(manifest),
            f"legacy manifest lacks required fields: {path.relative_to(ROOT)}",
        )
        unknown = set(manifest) - allowed
        require(
            not unknown,
            f"legacy manifest has unknown fields: {path.relative_to(ROOT)}: {sorted(unknown)}",
        )
        if "campaign" not in manifest:
            legacy_count += 1
        label = f"legacy manifest {path.relative_to(ROOT)}"
        _validate_pilot_manifest_formats(manifest, label)
        _validate_jsonschema_instance(schema, manifest, label)
    require(
        legacy_count > 0, "expected at least one unchanged pre-campaign pilot manifest"
    )


def validate_layout() -> None:
    required = [
        ROOT / "search-log.md",
        SEARCHES / "README.md",
        SEARCHES / "templates" / "source-guideline.md",
        SEARCHES / "templates" / "source-pilot-prompt.md",
        SEARCHES / "templates" / "pilot-campaign.template.json",
        SEARCHES / "final-events" / "README.md",
    ]
    for path in required:
        require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    final_files = [
        p
        for p in (SEARCHES / "final-events").rglob("*")
        if p.is_file() and p.name != "README.md"
    ]
    require(
        not final_files, f"final-events contains premature artifacts: {final_files}"
    )


def main() -> int:
    checks = [
        validate_dictionary,
        validate_crosswalk,
        validate_schemas,
        validate_campaign_template,
        validate_legacy_pilot_manifests,
        validate_layout,
    ]
    for check in checks:
        check()
        print(f"ok: {check.__name__}")
    print("SLR1 search infrastructure validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
