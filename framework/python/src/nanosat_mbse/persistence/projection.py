"""Temporary browser transport adapter around the native object graph.

Import uses two passes to resolve identities into object references. It never
runs initialization hooks and never keeps the input document as backing state.
"""

from __future__ import annotations

import ast
import re

from ..catalogs.cots import component_for_product
from ..catalogs.database import DatabaseBacked, FactReference
from ..catalogs.definitions import PYTHON_TYPES
from ..core.configuration import (
    ComponentState,
    StateAllocation,
    LoadConnection,
    LoadProfile,
    Mode,
    ScriptPort,
    Variable,
)
from ..core.drafts import DraftRequirement, DraftStatement
from ..core.elements import Stakeholder
from ..core.requirements import Parameter, Requirement, Statement
from ..core.session import SeedRule, expression_source
from ..core.verification import DraftExpression, VerificationMethod, restored_expression
from ..domains.eps.requirements import GenericRequirement
from ..domains.budgets import BUDGET_CLASSES, remember_budget_defaults
from ..domains.registry import element_class

KINDS = {float: "float", int: "integer", bool: "boolean", str: "string"}


def _source(expression, callables=None):
    if isinstance(expression, DraftExpression):
        return expression.source
    if isinstance(expression, str):
        return expression
    if callables is None:
        raise TypeError(
            "Supply a trusted CallableRegistry to project native conditions."
        )
    return ""


def _parameter(name, source, variable, metadata=None, callables=None, slot=None):
    metadata = metadata or {}
    value_type = PYTHON_TYPES[metadata.get("type", KINDS[variable.value_type])]
    unit = metadata.get("unit", variable.unit or "")
    if "callable" in metadata:
        if callables is None or source is not None:
            raise ValueError(
                "Native parameter bindings require their trusted read-only registry."
            )
        return Parameter(
            name,
            value_type,
            unit,
            expression=callables.resolve(metadata["callable"], slot=slot),
        )
    if source is not None and not isinstance(source, str):
        raise ValueError("Projected parameter bindings must be Python source or null.")
    if source is None:
        return Parameter(name, value_type, unit)
    if metadata.get("literal"):
        return Parameter(name, value_type, unit, value=ast.literal_eval(source))
    return Parameter(name, value_type, unit, expression=restored_expression(source))


def _local_names(source, available):
    if not isinstance(source, str) or len(source) > 5000:
        return set()
    try:
        tree = ast.parse(source.strip(), mode="eval")
    except (SyntaxError, ValueError):
        return set()
    names = set()

    def collect(node, bound=frozenset()):
        if isinstance(node, ast.Name):
            if node.id in available and node.id not in bound:
                names.add(node.id)
        elif isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            nested = set(bound)
            for generator in node.generators:
                collect(generator.iter, nested)
                nested.update(
                    item.id
                    for item in ast.walk(generator.target)
                    if isinstance(item, ast.Name)
                )
                for condition in generator.ifs:
                    collect(condition, nested)
            collect(node.elt, nested)
        elif isinstance(node, ast.Call):
            for item in (*node.args, *(keyword.value for keyword in node.keywords)):
                collect(item, bound)
        elif not isinstance(node, ast.Attribute):
            for child in ast.iter_child_nodes(node):
                collect(child, bound)

    collect(tree)
    return names


def from_projection(data, *, session_class=None, callables=None, **kwargs):
    from ..core.session import Session

    if (
        not isinstance(data, dict)
        or data.get("version") != 14
        or data.get("expressionLanguage") != "python"
    ):
        raise ValueError("Choose a version 14 workspace with Python expressions.")
    known = {
        "version",
        "expressionLanguage",
        "variables",
        "stakeholders",
        "elements",
        "statements",
        "components",
        "scripts",
        "power",
        "resourceBudgets",
        "requirementSeeds",
        "modelState",
    }
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"Unsupported workspace fields: {', '.join(sorted(unknown))}.")
    session = (Session if session_class is None else session_class)(**kwargs)
    session._model_state_present = "modelState" in data
    session._resource_budgets_present = "resourceBudgets" in data
    session.resource_budgets = data.get("resourceBudgets", False)
    session._requirement_seeds_present = "requirementSeeds" in data
    session.variables = [
        Variable(row["name"], PYTHON_TYPES[row["type"]], row.get("unit"))
        for row in data["variables"]
    ]
    variables = {variable.name: variable for variable in session.variables}
    if len(variables) != len(session.variables):
        raise ValueError("Workspace variable names must be unique.")
    state = data.get("modelState", {})
    parameter_metadata = state.get("parameters", {})
    element_rows, statement_rows, cots_rows = [], [], []

    # Pass one constructs independent populated objects and registers identities.
    for row in data.get("stakeholders", []):
        value = Stakeholder(
            row["id"], name=row["name"], key=row["key"], stakeholder_type=row["type"]
        )
        value._projection_fields = frozenset(row)
        session._register(value)
        element_rows.append((value, {"owner": "external"}))
    for row in data.get("elements", []):
        if row["definition"] not in session.catalog.by_model:
            raise ValueError(f"Unknown catalog definition {row['definition']!r}.")
        value = element_class(row["definition"])(
            row["id"], name=row["name"], key=row["key"], definition=row["definition"]
        )
        value._projection_fields = frozenset(row)
        session._register(value)
        element_rows.append((value, row))
    for row in data.get("components", []):
        value = component_for_product(
            row["product"],
            database=session.database,
            id=row["id"],
            key=row["key"],
            allow_unresolved=True,
            facts=tuple(FactReference(**fact) for fact in row.get("facts", [])),
        )
        value._projection_fields = frozenset(row)
        value._facts_present = "facts" in row
        session._register(value)
        element_rows.append((value, row))
        cots_rows.append((value, row))
    for row in data.get("scripts", []):

        def port(item):
            return ScriptPort(
                item["name"], PYTHON_TYPES[item["type"]], item.get("unit")
            )

        inputs, outputs = (
            tuple(map(port, row["inputs"])),
            tuple(map(port, row["outputs"])),
        )
        ports = {item.name: item for item in inputs}
        parameters = tuple(
            _parameter(
                name,
                source,
                Variable(name, ports[name].value_type, ports[name].unit),
                parameter_metadata.get(row["key"], {}).get(name),
                callables,
                ("parameter", row["key"], name),
            )
            for name, source in row["parameters"].items()
        )
        value = session.verification_registry.create(
            row["definition"],
            row["id"],
            name=row["name"],
            key=row["key"],
            revision=row["revision"],
            inputs=inputs,
            outputs=outputs,
            parameters=parameters,
        )
        value._projection_fields = frozenset(row)
        session._register(value)
    for row in data.get("statements", []):
        template = session.catalog.by_requirement.get(row.get("definition"))
        configured = row.get(
            "verifications",
            [{"key": "condition", "condition": row.get("condition", "")}],
        )
        names = set(
            name for name, source in row["parameters"].items() if source is not None
        )
        names.update(parameter_metadata.get(row["key"], {}))
        names.update(re.findall(r"\$\$\s*([A-Za-z_][A-Za-z0-9_]*)\s*\$\$", row["text"]))
        if template is not None:
            names.update(
                parameter.name for parameter in template.parameters if parameter.exposed
            )
        for source in [
            *[method.get("condition", "") for method in configured],
            *row["parameters"].values(),
        ]:
            names.update(_local_names(source, set(variables)))
        unknown_names = names - set(variables)
        if unknown_names:
            raise ValueError(
                f"{row['id']}: parameters have no type metadata: {', '.join(sorted(unknown_names))}."
            )
        owned = tuple(
            _parameter(
                variable.name,
                row["parameters"].get(variable.name),
                variable,
                parameter_metadata.get(row["key"], {}).get(variable.name),
                callables,
                ("parameter", row["key"], variable.name),
            )
            for variable in session.variables
            if variable.name in names
        )
        cls = (
            BUDGET_CLASSES.get(row.get("definition"), Requirement)
            if row["kind"] == "Requirement"
            else Statement
        )
        metadata = dict(
            parameters=owned,
            key=row["key"],
            kind=row["kind"],
            rationale=row.get("rationale", ""),
            origin=row.get("origin", ""),
            definition=row.get("definition", ""),
            name=row.get("name", ""),
        )
        try:
            if template is not None and cls is Requirement:
                value = GenericRequirement.__new__(GenericRequirement)
                value.template = template
                Requirement.__init__(value, row["id"], row["text"], **metadata)
            else:
                value = cls(row["id"], row["text"], **metadata)
        except (ValueError, TypeError):
            cls = DraftRequirement if row["kind"] == "Requirement" else DraftStatement
            value = cls(row["id"], row["text"], **metadata)
            if template is not None:
                value.template = template
        value._projection_fields = frozenset(row)
        value._verification_style = "methods" if "verifications" in row else "condition"
        session._register(value)
        statement_rows.append((value, row))

    # Pass two resolves every relationship against the registry.
    for value, row in element_rows:
        value.owner = session.get(row["owner"])
    for value, row in statement_rows:
        value.owner = session.get(row["context"])
        value.sources = tuple(session.get(key) for key in row["sources"])
        value.affected = tuple(session.get(key) for key in row["affected"])
        if "powerScope" in row:
            value.power_scope = session.get(row["powerScope"])
        if "budgetScope" in row:
            value.budget_scope = session.get(row["budgetScope"])
        methods = []
        configured = row.get("verifications")
        native_conditions = state.get("verificationBindings", {}).get(value.key, {})
        if configured is None:
            configured = (
                [{"key": "condition", "condition": row["condition"]}]
                if row.get("condition", "").strip() or "condition" in native_conditions
                else []
            )
        for index, method in enumerate(configured):
            if "script" in method and "component" in method:
                raise ValueError("Select one value source for a verification method.")
            source_key = method.get("script", method.get("component"))
            name = (
                state.get("verificationNames", {})
                .get(value.key, {})
                .get(method["key"], method.get("name", method["key"]))
            )
            native = native_conditions.get(method["key"])
            if native is not None and (callables is None or method["condition"] != ""):
                raise ValueError(
                    "Native conditions require their trusted read-only registry."
                )
            condition = (
                restored_expression(method["condition"])
                if native is None
                else callables.resolve(
                    native, slot=("condition", value.key, method["key"])
                )
            )
            methods.append(
                VerificationMethod(
                    name,
                    condition,
                    key=method["key"],
                    source=None if source_key is None else session.get(source_key),
                )
            )
        value.verifications = methods
    for value, row in cots_rows:
        value.requirement_links = tuple(session.get(key) for key in row["requirements"])
        usage_key = state.get("cotsUsages", {}).get(value.key)
        if usage_key is not None:
            value.usage = session.get(usage_key)
        else:
            candidates = [
                element
                for element in session.elements
                if element.owner is value.owner
                and element.definition.rsplit("::", 1)[-1]
                == value.definition.rsplit("::", 1)[-1]
            ]
            if len(candidates) == 1:
                value.usage = candidates[0]
    for key, subject in state.get("subjects", {}).items():
        session.get(key).subject = session.get(subject)

    power = data.get("power", {"modes": [], "loads": [], "links": []})
    session.power.modes = [
        Mode(row["name"], row["sunlight"], row["eclipse"], row["key"])
        for row in power["modes"]
    ]
    modes = {mode.key: mode for mode in session.power.modes}
    for row in power["loads"]:
        states = tuple(
            ComponentState(**item)
            for item in row["states"]
        )
        by_key = {item.key: item for item in states}
        session.power.loads.append(
            LoadProfile(
                session.get(row["element"]),
                row["quantity"],
                row["accounting"],
                None if not row["host"] else session.get(row["host"]),
                row["rationale"],
                states,
                {
                    modes[mode]: by_key[state]
                    for mode, state in row["assignments"].items()
                },
                {modes[mode]: duty for mode, duty in row.get("duties", {}).items()},
                {
                    modes[mode]: tuple(
                        StateAllocation(by_key[item["state"]], item["duty"])
                        for item in entries
                    )
                    for mode, entries in row.get("allocations", {}).items()
                },
            )
        )
    session.power.links = [
        LoadConnection(
            session.get(row["eps"]),
            tuple(session.get(key) for key in row["roots"]),
            {
                name: _parameter(
                    name,
                    source,
                    Variable(name, float, "W" if name.endswith("_W") else ""),
                    state.get("loadInputs", {}).get(row["eps"], {}).get(name),
                    callables,
                    ("loadInput", row["eps"], name),
                )
                for name, source in row["previous"].items()
            },
        )
        for row in power["links"]
    ]
    session.requirement_seeds = {
        session.get(key): tuple(definitions)
        for key, definitions in data.get("requirementSeeds", {}).items()
    }
    session.seed_history = {SeedRule(**rule) for rule in state.get("seedRules", [])}
    session._initialized = set(
        state.get("initialized", [element.key for element in session.all_elements])
    )
    if "seedRules" not in state:
        for value, row in statement_rows:
            if value.definition:
                session.seed_history.add(
                    SeedRule(
                        value.owner.key,
                        (value.subject or value.owner).key,
                        value.definition,
                    )
                )
    for owner, definitions in session.requirement_seeds.items():
        session.seed_history.update(
            SeedRule(owner.key, owner.key, definition) for definition in definitions
        )
    for element in session.elements:
        session.remember_component_defaults(element)
    remember_budget_defaults(session)
    # Relationship setters record native edits. Restoration itself is hook-free
    # and retains the input document's metadata presence exactly.
    session._model_state_present = "modelState" in data
    return session


def _parameters(value, variables, callables=None):
    return {
        name: expression_source(value.parameters[name], callables=callables)
        if name in value.parameters
        else None
        for name in dict.fromkeys(
            [variable.name for variable in variables] + list(value.parameters)
        )
    }


def _method(method, callables=None):
    result = {"key": method.key, "condition": _source(method.condition, callables)}
    if method.source is not None:
        result[
            "component" if isinstance(method.source, DatabaseBacked) else "script"
        ] = method.source.key
    return result


def to_projection(session, *, callables=None):
    """Create a detached view, using capabilities for trusted native bindings."""

    def parameter_metadata(parameter, slot):
        result = {"type": KINDS[parameter.value_type], "unit": parameter.unit}
        if parameter.value is not None:
            result["literal"] = True
        if callable(parameter.expression):
            if callables is None:
                raise TypeError(
                    "Supply a trusted CallableRegistry to project native bindings."
                )
            result["callable"] = callables.register(parameter.expression, slot=slot)
        return result

    variables = list(session.variables)
    names = {variable.name for variable in variables}
    for statement in session.statements:
        for parameter in statement.parameters.values():
            if parameter.name not in names:
                variables.append(
                    Variable(
                        parameter.name, parameter.value_type, parameter.unit or None
                    )
                )
                names.add(parameter.name)
    result = {
        "version": 14,
        "expressionLanguage": "python",
        "variables": [
            {
                "name": variable.name,
                "type": KINDS[variable.value_type],
                **({"unit": variable.unit} if variable.unit is not None else {}),
            }
            for variable in variables
        ],
        "stakeholders": [
            {
                "key": value.key,
                "id": value.id,
                "name": value.name,
                "type": value.stakeholder_type,
            }
            for value in session.stakeholders
        ],
        "elements": [
            {
                "key": value.key,
                "id": value.id,
                "name": value.name,
                "owner": value.owner.key,
                "definition": value.definition,
            }
            for value in session.elements
        ],
        "statements": [],
        "components": [],
        "scripts": [],
        "power": {
            "modes": [
                {
                    "key": mode.key,
                    "name": mode.name,
                    "sunlight": mode.sunlight,
                    "eclipse": mode.eclipse,
                }
                for mode in session.power.modes
            ],
            "loads": [
                {
                    "element": load.element.key,
                    "quantity": load.quantity,
                    "accounting": load.accounting,
                    "host": "" if load.host is None else load.host.key,
                    "rationale": load.rationale,
                    "states": [
                        {
                            "key": state.key,
                            "name": state.name,
                            "watts": state.watts,
                        }
                        for state in load.states
                    ],
                    "assignments": {
                        mode.key: state.key for mode, state in load.assignments.items()
                    },
                    **(
                        {
                            "duties": {
                                mode.key: duty for mode, duty in load.duties.items()
                            }
                        }
                        if load.duties
                        else {}
                    ),
                    **(
                        {"allocations": {
                            mode.key: [
                                {"state": item.state.key, "duty": item.duty}
                                for item in entries
                            ]
                            for mode, entries in load.allocations.items()
                        }}
                        if load.allocations else {}
                    ),
                }
                for load in session.power.loads
            ],
            "links": [
                {
                    "eps": link.eps.key,
                    "roots": [root.key for root in link.roots],
                    "previous": {
                        name: expression_source(parameter, callables=callables)
                        for name, parameter in link.previous.items()
                    },
                }
                for link in session.power.links
            ],
        },
    }
    for value in session.statements:
        row = {
            "key": value.key,
            "id": value.id,
            "context": "external" if value.owner is None else value.owner.key,
            "kind": value.kind,
            "text": value.text,
            "condition": "",
            "sources": [source.key for source in value.sources],
            "affected": [element.key for element in value.affected],
            "parameters": _parameters(value, variables, callables),
        }
        for field in ("name", "rationale", "origin", "definition"):
            attribute = getattr(value, field)
            if (
                attribute
                or field in value._projection_fields
                or not value._projection_fields
                and field == "rationale"
            ):
                row[field] = attribute
        if value.power_scope is not None:
            row["powerScope"] = value.power_scope.key
        if value.budget_scope is not None:
            row["budgetScope"] = value.budget_scope.key
        inline = (
            value._verification_style != "methods"
            and len(value.verifications) <= 1
            and all(
                method.source is None and method.key == "condition"
                for method in value.verifications
            )
        )
        if inline:
            row["condition"] = (
                ""
                if not value.verifications
                else _source(value.verifications[0].condition, callables)
            )
        elif value.verifications or value._verification_style == "methods":
            row["verifications"] = [
                _method(method, callables) for method in value.verifications
            ]
        result["statements"].append(row)
    for value in session.cots_components:
        row = {
            "key": value.key,
            "id": value.id,
            "owner": value.owner.key,
            "product": value.product,
            "requirements": [
                requirement.key for requirement in value.requirement_links
            ],
        }
        if value._facts_present or value.facts:
            row["facts"] = [fact.projection() for fact in value.facts]
        result["components"].append(row)
    for value in session.scripts:

        def port(item):
            return {
                "name": item.name,
                "type": KINDS[item.value_type],
                **({"unit": item.unit} if item.unit is not None else {}),
            }

        result["scripts"].append(
            {
                "key": value.key,
                "id": value.id,
                "name": value.name,
                "definition": value.definition,
                "revision": value.revision,
                "inputs": [port(item) for item in value.inputs],
                "outputs": [port(item) for item in value.outputs],
                "parameters": {
                    name: expression_source(parameter, callables=callables)
                    for name, parameter in value.parameters.items()
                },
            }
        )
    if session._resource_budgets_present or session.resource_budgets:
        result["resourceBudgets"] = session.resource_budgets
    if session._requirement_seeds_present or session.requirement_seeds:
        result["requirementSeeds"] = {
            owner.key: list(definitions)
            for owner, definitions in session.requirement_seeds.items()
        }
    native_conditions = {
        value.key: {
            method.key: callables.register(
                method.condition, slot=("condition", value.key, method.key)
            )
            for method in value.verifications
            if callable(method.condition)
        }
        for value in session.statements
        if any(callable(method.condition) for method in value.verifications)
    }
    native_parameters = any(
        callable(parameter.expression)
        for value in (*session.statements, *session.scripts)
        for parameter in value.parameters.values()
    ) or any(
        callable(parameter.expression)
        for link in session.power.links
        for parameter in link.previous.values()
    )
    if session._model_state_present or native_conditions or native_parameters:
        result["modelState"] = {
            "seedRules": [
                {"owner": rule.owner, "subject": rule.subject, "rule": rule.rule}
                for rule in sorted(
                    session.seed_history,
                    key=lambda rule: (rule.owner, rule.subject, rule.rule),
                )
            ],
            "initialized": sorted(session._initialized),
            "subjects": {
                value.key: value.subject.key
                for value in session.statements
                if value.subject is not None
            },
            "verificationNames": {
                value.key: {method.key: method.name for method in value.verifications}
                for value in session.statements
                if value.verifications
            },
            "cotsUsages": {
                value.key: value.usage.key
                for value in session.cots_components
                if value.usage is not None
            },
            "loadInputs": {
                link.eps.key: {
                    name: parameter_metadata(
                        parameter, ("loadInput", link.eps.key, name)
                    )
                    for name, parameter in link.previous.items()
                }
                for link in session.power.links
            },
            "parameters": {
                value.key: {
                    name: parameter_metadata(parameter, ("parameter", value.key, name))
                    for name, parameter in value.parameters.items()
                }
                for value in (*session.statements, *session.scripts)
            },
        }
        if native_conditions:
            result["modelState"]["verificationBindings"] = native_conditions
    return result
