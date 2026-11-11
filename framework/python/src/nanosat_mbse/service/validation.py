"""Bounded browser transport validation, independent of engineering calculation."""

from __future__ import annotations

import copy
import re

from ..core.requirements import _parameter_name

TABLES = ("stakeholders", "elements", "statements", "components", "scripts")
TYPES = {"float": float, "integer": int, "boolean": bool, "string": str}
ROOT_FIELDS = {
    "version",
    "expressionLanguage",
    "variables",
    *TABLES,
    "power",
    "resourceBudgets",
    "requirementSeeds",
    "modelState",
}
FIELDS = {
    "stakeholders": {"key", "id", "name", "type"},
    "elements": {"key", "id", "name", "owner", "definition"},
    "statements": {
        "key",
        "id",
        "context",
        "kind",
        "text",
        "condition",
        "sources",
        "affected",
        "parameters",
        "verifications",
        "definition",
        "origin",
        "rationale",
        "name",
        "powerScope",
        "budgetScope",
    },
    "components": {"key", "id", "owner", "product", "requirements", "facts"},
    "scripts": {
        "key",
        "id",
        "name",
        "definition",
        "revision",
        "inputs",
        "outputs",
        "parameters",
    },
}
STAKEHOLDERS = (
    "Regulatory Agency",
    "Mission Stakeholder",
    "Launch Provider",
    "Partner",
)
KINDS = ("Requirement", "Need", "Objective", "Concern", "Constraint")
KEY = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
PIN = re.compile(r"[a-f0-9]{64}\Z")


def text(value, label, maximum=10000, *, required=False, line=False):
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"{label} must be text of at most {maximum} characters.")
    if required and not value.strip():
        raise ValueError(f"{label} must contain text.")
    if line and ("\n" in value or "\r" in value):
        raise ValueError(f"{label} must contain one line.")
    return value


def key(value, label="Object key"):
    if not isinstance(value, str) or not KEY.fullmatch(value):
        raise ValueError(
            f"{label} needs a stable key of 1 to 80 letters, digits or underscores."
        )
    return value


def mapping(value, label, allowed=None):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    if allowed is not None and set(value) - set(allowed):
        raise ValueError(
            f"{label} contains unsupported fields: {', '.join(sorted(set(value) - set(allowed)))}."
        )
    return value


def collection(value, label, maximum):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f"{label} must be a list of at most {maximum} entries.")
    return value


def expression(value, label):
    if value is not None:
        text(value, label, 5000, line=True)
    return value


def references(values, label):
    collection(values, label, 10000)
    if any(not isinstance(value, str) for value in values) or len(set(values)) != len(
        values
    ):
        raise ValueError(f"{label} contains unique stable object keys.")
    for value in values:
        key(value, label)


def _unused(row, table):
    if row.get("id"):
        return False
    if table == "stakeholders":
        return not any(row.get(name) for name in ("name", "type"))
    if table == "elements":
        return not any(row.get(name) for name in ("name", "definition"))
    if table == "components":
        return not (row.get("product") or row.get("requirements") or row.get("facts"))
    if table == "scripts":
        return False
    return not any(
        row.get(name)
        for name in (
            "text",
            "condition",
            "verifications",
            "rationale",
            "sources",
            "affected",
        )
    ) and not any(
        value is not None and value != ""
        for value in row.get("parameters", {}).values()
    )


def normalize_projection(data, base=None):
    """Accept legacy calculation snapshots and discard unused visual placeholders.

    Missing transport metadata is inherited from a trusted base projection. The
    service never accepts execution evidence as part of this document.
    """
    mapping(data, "Workspace", ROOT_FIELDS)
    result = copy.deepcopy(base) if base is not None else {}
    result.update(copy.deepcopy(data))
    result.setdefault("version", 14)
    result.setdefault("expressionLanguage", "python")
    result.setdefault("variables", [])
    result.setdefault("power", {"modes": [], "loads": [], "links": []})
    for table in TABLES:
        rows = result.setdefault(table, [])
        collection(rows, table, 10000 if table != "scripts" else 64)
        result[table] = [
            row for row in rows if isinstance(row, dict) and not _unused(row, table)
        ]
        if any(not isinstance(row, dict) for row in rows):
            raise ValueError(f"{table} entries must be objects.")
    power = result["power"]
    if isinstance(power, dict):
        power["modes"] = [
            row
            for row in power.get("modes", [])
            if row.get("name")
            or row.get("sunlight") is not None
            or row.get("eclipse") is not None
        ]
    return result


def validate_projection(data, *, allow_new_ids=False):
    """Validate data shapes only. Native methods validate relationships and rules."""
    mapping(data, "Workspace", ROOT_FIELDS)
    if data.get("version") != 14 or data.get("expressionLanguage") != "python":
        raise ValueError("Choose a version 14 workspace with Python expressions.")
    variables = collection(data.get("variables"), "Variables", 256)
    names = set()
    for variable in variables:
        mapping(variable, "Variable", {"name", "type", "unit"})
        _parameter_name(variable.get("name"))
        if variable["name"] in names or variable.get("type") not in TYPES:
            raise ValueError(
                "Declare unique variable names and supported scalar types."
            )
        names.add(variable["name"])
        if "unit" in variable:
            text(variable["unit"], "Units", 100, line=True)
    keys, ids = set(), set()
    for table in TABLES:
        rows = collection(data.get(table), table, 64 if table == "scripts" else 10000)
        for row in rows:
            mapping(row, f"{table} row", FIELDS[table])
            key(row.get("key"))
            if row["key"] in keys:
                raise ValueError("Object keys must be unique.")
            keys.add(row["key"])
            identifier = text(
                row.get("id", ""),
                "Object ID",
                200,
                required=not allow_new_ids,
                line=True,
            )
            if identifier:
                if identifier in ids:
                    raise ValueError(f"The ID {identifier!r} is already in use.")
                ids.add(identifier)
            if table in ("stakeholders", "elements"):
                text(row.get("name", ""), "Element name")
            if table == "stakeholders" and row.get("type") not in STAKEHOLDERS:
                raise ValueError("Choose a stakeholder type.")
            if table == "elements":
                key(row.get("owner"), "Element owner")
                text(row.get("definition"), "Element definition", 300, required=True)
            if table == "statements":
                key(row.get("context"), "Statement context")
                if row.get("kind") not in KINDS:
                    raise ValueError("Choose a supported statement kind.")
                text(row.get("text"), "Statement text", 50000)
                for field, maximum in (
                    ("rationale", 10000),
                    ("origin", 2000),
                    ("name", 10000),
                    ("definition", 300),
                ):
                    if field in row:
                        text(row[field], field, maximum)
                expression(row.get("condition", ""), "Verification condition")
                references(row.get("sources"), "Statement sources")
                references(row.get("affected"), "Affected elements")
                mapping(row.get("parameters"), "Requirement parameters")
                if len(row["parameters"]) > 256:
                    raise ValueError(
                        "A requirement supports up to 256 parameter names."
                    )
                for name, source in row["parameters"].items():
                    _parameter_name(name)
                    expression(source, f"{identifier}.{name}")
                methods = row.get("verifications", [])
                collection(methods, "Verification methods", 32)
                method_keys = set()
                if methods and row.get("condition", "").strip():
                    raise ValueError(
                        "Use the verification table or the single condition field."
                    )
                for method in methods:
                    mapping(
                        method,
                        "Verification method",
                        {"key", "condition", "script", "component"},
                    )
                    key(method.get("key"), "Verification method key")
                    if method["key"] in method_keys:
                        raise ValueError("Verification method keys must be unique.")
                    method_keys.add(method["key"])
                    text(
                        method.get("condition"),
                        "Verification condition",
                        5000,
                        line=True,
                    )
                    if "script" in method and "component" in method:
                        raise ValueError("Select one source per verification method.")
                    for field in ("script", "component"):
                        if field in method:
                            key(method[field], "Verification source")
                for field in ("powerScope", "budgetScope"):
                    if field in row:
                        key(row[field], "Budget scope")
            if table == "components":
                key(row.get("owner"), "COTS owner")
                if not isinstance(row.get("product"), str) or not re.fullmatch(
                    r"[a-z0-9_]+", row["product"]
                ):
                    raise ValueError("Choose a COTS database product.")
                references(row.get("requirements"), "COTS requirement links")
                fact_names, fact_keys = set(), set()
                for fact in collection(
                    row.get("facts", []), "COTS fact selections", 64
                ):
                    mapping(
                        fact,
                        "COTS fact selection",
                        {"key", "name", "fact", "revision", "type", "unit"},
                    )
                    if set(fact) != {"key", "name", "fact", "revision", "type", "unit"}:
                        raise ValueError(
                            "Fact selections store pins and names, never authoritative values."
                        )
                    key(fact["key"], "Fact key")
                    _parameter_name(fact["name"])
                    if fact["key"] in fact_keys or fact["name"] in fact_names:
                        raise ValueError(
                            "COTS reference names and keys must be unique."
                        )
                    fact_keys.add(fact["key"])
                    fact_names.add(fact["name"])
                    if fact["type"] not in TYPES or any(
                        not isinstance(fact[field], str)
                        or not PIN.fullmatch(fact[field])
                        for field in ("fact", "revision")
                    ):
                        raise ValueError(
                            "Pin a typed COTS record identity and revision."
                        )
                    text(fact["unit"], "Fact units", 100, line=True)
            if table == "scripts":
                text(row.get("name"), "Script name", 80, required=True)
                if not isinstance(row.get("definition"), str) or not re.fullmatch(
                    r"[a-z][a-z0-9_]{0,79}", row["definition"]
                ):
                    raise ValueError("Choose a registered analysis definition.")
                if not isinstance(row.get("revision"), str) or not PIN.fullmatch(
                    row["revision"]
                ):
                    raise ValueError("Pin an analysis definition revision.")
                port_names, input_names = set(), set()
                for direction in ("inputs", "outputs"):
                    ports = collection(row.get(direction), f"Script {direction}", 32)
                    if direction == "outputs" and not ports:
                        raise ValueError("An analysis needs at least one output.")
                    for port in ports:
                        mapping(port, "Script port", {"name", "type", "unit"})
                        _parameter_name(port.get("name"))
                        if port["name"] in port_names or port.get("type") not in TYPES:
                            raise ValueError(
                                "Script port names and types must be valid and unique."
                            )
                        port_names.add(port["name"])
                        if direction == "inputs":
                            input_names.add(port["name"])
                        if "unit" in port:
                            text(port["unit"], "Script units", 100, line=True)
                mapping(row.get("parameters"), "Script input bindings")
                if set(row["parameters"]) != input_names:
                    raise ValueError("Bind exactly the declared script inputs.")
                for name, source in row["parameters"].items():
                    expression(source, f"{identifier}.{name}")
    if len(keys) > 10000:
        raise ValueError("A workspace supports up to 10,000 rows.")
    power = mapping(
        data.get("power"), "Power configuration", {"modes", "loads", "links"}
    )
    for field, maximum in (("modes", 24), ("loads", 1000), ("links", 1000)):
        collection(power.get(field), field, maximum)
    for mode in power["modes"]:
        mapping(mode, "Mode", {"key", "name", "sunlight", "eclipse"})
        key(mode.get("key"), "Mode key")
        text(mode.get("name"), "Mode name", 80, required=True)
    for load in power["loads"]:
        mapping(
            load,
            "Load profile",
            {
                "element",
                "quantity",
                "accounting",
                "host",
                "rationale",
                "states",
                "assignments",
                "duties",
            },
        )
        key(load.get("element"), "Load component")
        text(load.get("rationale", ""), "Accounting rationale", 2000)
        text(load.get("host", ""), "Execution host", 80)
        mapping(load.get("assignments"), "State assignments")
        mapping(load.get("duties", {}), "Component duty percentages")
        for state in collection(load.get("states"), "Component states", 32):
            mapping(
                state,
                "Component state",
                {"key", "name", "watts", "basis", "source", "conditions"},
            )
            key(state.get("key"), "State key")
            text(state.get("name"), "State name", 80, required=True)
            if isinstance(state.get("watts"), str):
                expression(state["watts"], "State power")
            text(state.get("source", ""), "State source", 2000)
            text(state.get("conditions", ""), "State conditions", 2000)
    for link in power["links"]:
        mapping(link, "Load connection", {"eps", "roots", "previous"})
        key(link.get("eps"), "EPS key")
        references(link.get("roots"), "Load roots")
        mapping(link.get("previous"), "Prior manual inputs")
        for source in link["previous"].values():
            expression(source, "Prior load input")
    if data.get("resourceBudgets", True) is not True:
        raise ValueError("Invalid resource budget initialization marker.")
    if "modelState" in data:
        state = mapping(
            data["modelState"],
            "Native model metadata",
            {
                "seedRules",
                "initialized",
                "subjects",
                "verificationNames",
                "cotsUsages",
                "loadInputs",
                "parameters",
                "verificationBindings",
            },
        )
        if len(repr(state)) > 4 * 1024 * 1024:
            raise ValueError("Native model metadata exceeds its transport limit.")
    return data
