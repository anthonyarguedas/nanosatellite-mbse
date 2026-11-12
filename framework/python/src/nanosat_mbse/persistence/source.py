"""Readable Python construction code for native session configuration.

The output imports real classes and binds their instances explicitly. No browser
projection, calculated result, execution evidence or database value is embedded.
"""

from __future__ import annotations

import keyword
import math
import re
from dataclasses import fields, is_dataclass

from ..catalogs.database import DatabaseBacked, FactReference
from ..core.configuration import (
    ComponentState,
    StateAllocation,
    LoadConnection,
    LoadProfile,
    Mode,
    ScriptConfiguration,
    ScriptPort,
    Variable,
)
from ..core.elements import Component, Element, Stakeholder
from ..core.predicates import DraftExpression, VerificationMethod
from ..core.requirements import Parameter, Statement
from ..core.session import SeedRule, Session
from ..verifications.registered import RegisteredScript
from .callables import import_identity

SESSION_FORMAT = 1


class SessionSourceError(ValueError):
    """Configuration cannot be represented without losing its behavior."""


class _Imports:
    def __init__(self):
        self.symbols = {}
        self.roots = {}
        self.occupied = {"session", "build_session", "run_verifications", "evidence"}

    def symbol(self, value):
        if value in (float, int, bool, str):
            return value.__name__
        identity = import_identity(value)
        if identity in self.symbols:
            return self.symbols[identity]
        module, qualified = identity
        root, *tail = qualified.split(".")
        root_identity = (module, root)
        alias = self.roots.get(root_identity)
        if alias is None:
            alias, suffix = root, 2
            while alias in self.occupied:
                alias, suffix = f"{root}_{suffix}", suffix + 1
            self.occupied.add(alias)
            self.roots[root_identity] = alias
        expression = ".".join((alias, *tail))
        self.symbols[identity] = expression
        return expression

    def variable(self, hint):
        base = re.sub(r"[^A-Za-z0-9_]", "_", hint).lower().strip("_") or "object"
        if base[0].isdigit() or keyword.iskeyword(base):
            base = f"object_{base}"
        value, suffix = base, 2
        while value in self.occupied:
            value, suffix = f"{base}_{suffix}", suffix + 1
        self.occupied.add(value)
        return value

    def lines(self):
        return [
            f"from {module} import {root}" + (f" as {alias}" if root != alias else "")
            for (module, root), alias in sorted(self.roots.items())
        ]


_ELEMENT_FIELDS = {
    "_session",
    "_key",
    "_id",
    "name",
    "definition",
    "_owner",
    "selection",
    "_projection_fields",
    "stakeholder_type",
    "_property_values",
    "_budget_parameters",
    "_quantity",
    "_requirement_links",
}
_DATABASE_FIELDS = {
    "database",
    "_product",
    "_facts",
    "_facts_present",
    "_usage",
    "_requirement_links",
}
_SCRIPT_FIELDS = {
    "revision",
    "inputs",
    "outputs",
    "parameters",
    "_registration",
    "_missing_spec",
}
_STATEMENT_FIELDS = {
    "_session",
    "kind",
    "power_scope",
    "budget_scope",
    "subject",
    "_projection_fields",
    "_verification_style",
    "_key",
    "_id",
    "name",
    "rationale",
    "origin",
    "definition",
    "_parameters",
    "_verifications",
    "_sources",
    "_affected",
    "_owner",
    "_text",
    "template",
    "draft_issues",
}
_SESSION_FIELDS = {
    "key",
    "name",
    "catalog",
    "database",
    "verification_registry",
    "_execution_evidence",
    "_objects",
    "seed_history",
    "_initialized",
    "_initializing",
    "requirement_seeds",
    "_requirement_seeds_present",
    "_model_state_present",
    "resource_budgets",
    "_resource_budgets_present",
    "variables",
    "power",
    "mission",
    "external",
    "_storage_status",
}
_RECORDS = (
    Variable,
    SeedRule,
    ScriptPort,
    FactReference,
    Mode,
    ComponentState,
    StateAllocation,
    DraftExpression,
)


class _Writer:
    def __init__(self, session):
        if not isinstance(session, Session):
            raise TypeError("Serialize a native Session instance.")
        self.session = session
        self.imports = _Imports()
        self.names = {}
        self.body = []
        self.extra = []
        self.imports.symbol(type(session))
        self.names[id(session)] = "session"
        for value in session.objects:
            self.names[id(value)] = self.imports.variable(value.id)
        for mode in session.power.modes:
            self.names[id(mode)] = self.imports.variable(f"mode_{mode.name}")
        for load in session.power.loads:
            for state in load.states:
                self.names.setdefault(
                    id(state), self.imports.variable(f"{load.element.id}_{state.name}")
                )

    def emit(self, line="", indent=1):
        self.body.append("    " * indent + line if line else "")

    def reference(self, value):
        if value is None:
            return "None"
        name = self.names.get(id(value))
        if name is None:
            raise SessionSourceError(
                "A session relationship refers to an unregistered object."
            )
        return name

    def expression(self, value):
        if value is None or type(value) in (str, bool, int):
            return repr(value)
        if type(value) is float:
            if not math.isfinite(value):
                raise SessionSourceError(
                    "Session configuration numbers must be finite."
                )
            return repr(value)
        if id(value) in self.names:
            return self.reference(value)
        if isinstance(value, Parameter):
            arguments = [repr(value.name)]
            if value.value_type is not float:
                arguments.append(f"value_type={self.imports.symbol(value.value_type)}")
            if value.unit:
                arguments.append(f"unit={value.unit!r}")
            if value.value is not None:
                arguments.append(f"value={self.expression(value.value)}")
            if value.expression is not None:
                arguments.append(f"expression={self.expression(value.expression)}")
            return f"{self.imports.symbol(Parameter)}({', '.join(arguments)})"
        if isinstance(value, VerificationMethod):
            arguments = [
                repr(value.name),
                self.expression(value.condition),
                f"key={value.key!r}",
            ]
            if value.source is not None:
                arguments.append(f"source={self.reference(value.source)}")
            return f"{self.imports.symbol(VerificationMethod)}({', '.join(arguments)})"
        if isinstance(value, _RECORDS) and is_dataclass(value):
            return (
                f"{self.imports.symbol(type(value))}("
                + ", ".join(
                    f"{field.name}={self.expression(getattr(value, field.name))}"
                    for field in fields(value)
                )
                + ")"
            )
        if isinstance(value, tuple):
            return (
                "("
                + ", ".join(self.expression(item) for item in value)
                + ("," if len(value) == 1 else "")
                + ")"
            )
        if isinstance(value, list):
            return "[" + ", ".join(self.expression(item) for item in value) + "]"
        if isinstance(value, dict):
            return (
                "{"
                + ", ".join(
                    f"{self.expression(key)}: {self.expression(item)}"
                    for key, item in value.items()
                )
                + "}"
            )
        if isinstance(value, (set, frozenset)):
            if not value:
                return "set()" if isinstance(value, set) else "frozenset()"
            items = sorted(self.expression(item) for item in value)
            literal = "{" + ", ".join(items) + "}"
            return literal if isinstance(value, set) else f"frozenset({literal})"
        if callable(value):
            return self.imports.symbol(value)
        raise SessionSourceError(
            f"Unsupported configuration value {type(value).__module__}.{type(value).__qualname__}."
        )

    def extras(self, value, known):
        declared = tuple(getattr(type(value), "session_state_fields", ()))
        if any(
            not isinstance(name, str) or not name.isidentifier() for name in declared
        ):
            raise SessionSourceError(
                "session_state_fields must contain attribute names."
            )
        unexpected = set(vars(value)) - known - set(declared)
        if unexpected:
            raise SessionSourceError(
                f"{type(value).__name__} has undeclared state: {', '.join(sorted(unexpected))}. "
                "Declare persistent additional fields in session_state_fields. "
                "Keep execution caches outside configuration."
            )
        for name in declared:
            if name in known:
                raise SessionSourceError(
                    f"{name!r} is already managed by the session serializer."
                )
            if hasattr(value, name):
                self.extra.append((value, name, getattr(value, name)))

    def tuple_field(self, name, items, indent):
        self.emit(f"{name}=(", indent)
        for item in items:
            self.emit(f"{self.expression(item)},", indent + 1)
        self.emit("),", indent)

    def object(self, value):
        name = self.reference(value)
        root = (
            "mission"
            if value is self.session.mission
            else "external"
            if value is self.session.external
            else None
        )
        if root is not None and value.key != root:
            raise SessionSourceError(
                "Session roots retain their canonical stable keys."
            )
        cls = self.imports.symbol(type(value))
        if root is not None:
            self.extras(value, _ELEMENT_FIELDS)
            self.emit(f"{name} = {cls}.restore(")
            for field in ("id", "key", "name", "definition", "selection"):
                self.emit(f"{field}={self.expression(getattr(value, field))},", 2)
            if value.property_values:
                self.emit(f"property_values={self.expression(dict(value.property_values))},", 2)
            if value.quantity != 1:
                self.emit(f"quantity={value.quantity!r},", 2)
            self.emit(")")
            self.emit()
            return
        self.emit(f"{name} = session.restore(")
        self.emit(f"{cls}.restore(", 2)
        self.emit(f"id={value.id!r},", 3)
        self.emit(f"key={value.key!r},", 3)
        self.emit(f"name={value.name!r},", 3)
        self.emit(f"definition={value.definition!r},", 3)
        if isinstance(value, Statement):
            self.extras(value, _STATEMENT_FIELDS)
            for field in ("text", "kind", "rationale", "origin"):
                self.emit(f"{field}={getattr(value, field)!r},", 3)
            self.tuple_field("parameters", value.parameters.values(), 3)
            template = getattr(value, "template", None)
            if template is not None:
                current = self.session.catalog.by_requirement.get(template.model)
                if current is not template and current != template:
                    raise SessionSourceError(
                        "A generic requirement needs its configured catalog provider."
                    )
                self.emit(
                    f"template=session.catalog.by_requirement[{template.model!r}],", 3
                )
        else:
            known = set(_ELEMENT_FIELDS)
            self.emit(f"selection={value.selection!r},", 3)
            if value.property_values:
                self.emit(f"property_values={self.expression(dict(value.property_values))},", 3)
            if value.quantity != 1:
                self.emit(f"quantity={value.quantity!r},", 3)
            if isinstance(value, Component):
                self.tuple_field("budget_parameters", value.parameters.values(), 3)
            if isinstance(value, Stakeholder):
                self.emit(f"stakeholder_type={value.stakeholder_type!r},", 3)
            if isinstance(value, DatabaseBacked):
                known.update(_DATABASE_FIELDS)
                self.emit(f"product={value.product!r},", 3)
                self.emit("database=session.database,", 3)
                self.emit("allow_unresolved=True,", 3)
                self.tuple_field("facts", value.facts, 3)
            if isinstance(value, ScriptConfiguration):
                known.update(_SCRIPT_FIELDS)
                self.emit(f"revision={value.revision!r},", 3)
                self.tuple_field("inputs", value.inputs, 3)
                self.tuple_field("outputs", value.outputs, 3)
                self.tuple_field("parameters", value.parameters.values(), 3)
                if isinstance(value, RegisteredScript):
                    self.emit(f"directory={str(value._registration.directory)!r},", 3)
                    self.emit("registry=session.verification_registry,", 3)
                    spec = value.spec
                    from ..core.verification import ScriptDefinition

                    self.emit(
                        f"registration_spec={self.imports.symbol(ScriptDefinition)}(", 3
                    )
                    for field in ("id", "name", "description", "timeout_ms"):
                        self.emit(f"{field}={getattr(spec, field)!r},", 4)
                    self.tuple_field("inputs", spec.inputs, 4)
                    self.tuple_field("outputs", spec.outputs, 4)
                    self.emit("),", 3)
            self.extras(value, known)
        self.emit("),", 2)
        self.emit(f"projection_fields={tuple(sorted(value._projection_fields))!r},", 2)
        if isinstance(value, Statement):
            self.emit(f"verification_style={value._verification_style!r},", 2)
        if isinstance(value, DatabaseBacked):
            self.emit(f"facts_present={value._facts_present!r},", 2)
        self.emit(")")
        self.emit()

    def relationships(self):
        self.emit("# Connect the populated objects after every identity is registered.")
        for value in self.session.objects:
            name = self.reference(value)
            if value.owner is not None:
                self.emit(f"{name}.owner = {self.reference(value.owner)}")
            if isinstance(value, Statement):
                for field in ("sources", "affected"):
                    self.emit(
                        f"{name}.{field} = {self.expression(getattr(value, field))}"
                    )
                for field in ("power_scope", "budget_scope", "subject"):
                    if getattr(value, field) is not None:
                        self.emit(
                            f"{name}.{field} = {self.reference(getattr(value, field))}"
                        )
                if value.verifications:
                    self.emit(f"{name}.verifications = (")
                    for method in value.verifications:
                        self.emit(f"{self.expression(method)},", 2)
                    self.emit(")")
            if isinstance(value, DatabaseBacked):
                self.emit(f"{name}.usage = {self.reference(value.usage)}")
            if isinstance(value, Element) and (value.requirement_links or isinstance(value, DatabaseBacked)):
                self.emit(
                    f"{name}.requirement_links = {self.expression(value.requirement_links)}"
                )
        self.emit()

    def custom_state(self):
        for value, name, content in self.extra:
            self.emit(f"{self.reference(value)}.{name} = {self.expression(content)}")
        if self.extra:
            self.emit()

    def power(self):
        if (
            self.session.power.modes
            or self.session.power.loads
            or self.session.power.links
        ):
            self.emit(
                "# Mode, state and allocation configuration contains no calculated outputs."
            )
        for mode in self.session.power.modes:
            # A record declaration must not resolve to its own variable reference.
            name = self.names.pop(id(mode))
            expression = self.expression(mode)
            self.names[id(mode)] = name
            self.emit(f"{name} = {expression}")
            self.emit(f"session.power.modes.append({name})")
        declared = set()
        for load in self.session.power.loads:
            for state in load.states:
                if id(state) in declared:
                    continue
                declared.add(id(state))
                name = self.names.pop(id(state))
                expression = self.expression(state)
                self.names[id(state)] = name
                self.emit(f"{name} = {expression}")
            self.emit(f"session.power.loads.append({self.imports.symbol(LoadProfile)}(")
            for field in fields(load):
                self.emit(
                    f"{field.name}={self.expression(getattr(load, field.name))},", 2
                )
            self.emit("))")
        for link in self.session.power.links:
            self.emit(
                f"session.power.links.append({self.imports.symbol(LoadConnection)}("
            )
            for field in fields(link):
                self.emit(
                    f"{field.name}={self.expression(getattr(link, field.name))},", 2
                )
            self.emit("))")
        self.emit()

    def state(self):
        session = self.session
        self.emit(
            "# Restore initialization history, including deliberately deleted defaults."
        )
        self.emit("session.restore_state(")
        self.tuple_field("variables", session.variables, 2)
        self.tuple_field(
            "seed_history",
            sorted(
                session.seed_history,
                key=lambda item: (item.owner, item.subject, item.rule),
            ),
            2,
        )
        self.emit(f"initialized={tuple(sorted(session._initialized))!r},", 2)
        self.emit("requirement_seeds=(", 2)
        for owner, definitions in session.requirement_seeds.items():
            self.emit(f"({self.reference(owner)}, {definitions!r}),", 3)
        self.emit("),", 2)
        for field, value in (
            ("resource_budgets", session.resource_budgets),
            ("model_state_present", session._model_state_present),
            ("resource_budgets_present", session._resource_budgets_present),
            ("requirement_seeds_present", session._requirement_seeds_present),
        ):
            self.emit(f"{field}={value!r},", 2)
        self.emit(")")
        self.emit("return session")

    def render(self):
        self.extras(self.session, _SESSION_FIELDS)
        cls = self.imports.symbol(type(self.session))
        self.emit(f"session = {cls}(")
        self.emit(f"key={self.session.key!r},", 2)
        self.emit(f"name={self.session.name!r},", 2)
        self.emit("catalog=catalog,", 2)
        self.emit("database=database,", 2)
        self.emit("verification_registry=verification_registry,", 2)
        self.emit(")")
        self.emit()
        self.object(self.session.mission)
        self.object(self.session.external)
        self.emit("session.restore_roots(")
        self.emit(f"mission={self.reference(self.session.mission)},", 2)
        self.emit(f"external={self.reference(self.session.external)},", 2)
        self.emit(
            f"mission_fields={tuple(sorted(self.session.mission._projection_fields))!r},",
            2,
        )
        self.emit(
            f"external_fields={tuple(sorted(self.session.external._projection_fields))!r},",
            2,
        )
        self.emit(")")
        self.emit()
        for value in self.session.objects:
            if value not in (self.session.mission, self.session.external):
                self.object(value)
        self.relationships()
        self.power()
        self.custom_state()
        self.state()
        imports = self.imports.lines()
        lines = [
            '"""Native nanosat_mbse session configuration.',
            "",
            "This is trusted local Python code. Loading builds configuration only.",
            "Run this file explicitly to execute its imported verification classes.",
            '"""',
            "",
            *imports,
            "",
            f"SESSION_FORMAT = {SESSION_FORMAT}",
            "",
            "",
            "def build_session(*, catalog=None, database=None, verification_registry=None):",
            *self.body,
            "",
            "",
            "def run_verifications(session, **execution_options):",
            '    """Explicitly execute the configured imported analysis implementations."""',
            "    return session.run((",
            *(
                f"        session.get({script.key!r}),"
                for script in self.session.scripts
            ),
            "    ), **execution_options)",
            "",
            "",
            'if __name__ == "__main__":',
            "    session = build_session()",
            "    evidence = run_verifications(session)",
            '    print(session.name or "Session", len(session.objects), "objects")',
            "    for requirement, result in session.verify().assessments:",
            "        print(requirement.id, result.state.value)",
            "",
        ]
        source = "\n".join(lines)
        compile(source, "<nanosat-session>", "exec")
        return source


def dumps(session):
    """Generate canonical Python source without evaluating any parameter or script."""
    from .repository import validate_session

    validate_session(session)
    return _Writer(session).render()
