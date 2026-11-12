"""Native object evaluation, transient evidence gating and result projections."""

from __future__ import annotations

import ast
import inspect
import marshal
from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType

from ..catalogs.database import DatabaseBacked, digest
from .configuration import ScriptConfiguration
from .elements import Component
from .identity import ALL_MODES
from .expressions import CONSTANTS, RestrictedPython, finite_number, symbol
from .requirements import Statement
from .verification import (
    DraftExpression,
    MethodResult,
    PendingValue,
    VerificationResult,
    VerificationState,
)


_ACTIVE = ContextVar("nanosat_mbse_evaluation", default=None)
PRIORITY = ("error", "fail", "pending", "unset", "pass", "varying", "value")


def current_context(session=None):
    context = _ACTIVE.get()
    return (
        context
        if context is not None and (session is None or context.session is session)
        else None
    )


def _fingerprint(value, active=None):
    """Describe bindings without running functions or copying calculated values."""
    active = set() if active is None else active
    if value is None or type(value) in (str, bool, float, int):
        return value
    if isinstance(value, DraftExpression):
        return {"draft": value.source}
    if hasattr(value, "key") and hasattr(value, "id"):
        return {"key": value.key, "id": value.id}
    if id(value) in active:
        return {"cycle": type(value).__qualname__}
    active.add(id(value))
    try:
        if isinstance(value, Mapping):
            return {str(key): _fingerprint(item, active) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [_fingerprint(item, active) for item in value]
        if callable(value):
            function = getattr(value, "__func__", value)
            result = {
                "module": getattr(function, "__module__", ""),
                "name": getattr(function, "__qualname__", type(function).__qualname__),
            }
            code = getattr(function, "__code__", None)
            if code is not None:
                result["code"] = sha256(marshal.dumps(code)).hexdigest()
            try:
                file = inspect.getsourcefile(function)
                if file is not None:
                    result["moduleRevision"] = sha256(
                        Path(file).read_bytes()
                    ).hexdigest()
            except (OSError, TypeError):
                pass
            result["defaults"] = _fingerprint(
                getattr(function, "__defaults__", None), active
            )
            result["closure"] = [
                _fingerprint(cell.cell_contents, active)
                for cell in (getattr(function, "__closure__", None) or ())
            ]
            if getattr(value, "__self__", None) is not None:
                result["boundTo"] = _fingerprint(value.__self__, active)
            return result
        return {
            "type": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": repr(value),
        }
    finally:
        active.remove(id(value))


def _binding(parameter):
    return {
        "name": parameter.name,
        "type": parameter.value_type.__name__,
        "unit": parameter.unit,
        "value": parameter.value,
        "expression": _fingerprint(parameter.expression),
    }


def _cots_snapshot(session):
    resolved, records, databases, context = {}, {}, {}, []
    components = session.cots_components
    if not any(component.facts for component in components):
        return {}, None
    for component in components:
        if id(component.database) not in databases:
            databases[id(component.database)] = {
                product.id: product for product in component.database.products()
            }
        product = databases[id(component.database)].get(component.product)
        records = {} if product is None else {fact.id: fact for fact in product.facts}
        values = {}
        for reference in component.facts:
            fact = records.get(reference.fact)
            message = None
            if fact is None:
                message = "The selected record is unavailable for this product. Rebind it in the COTS pane."
            elif (
                fact.revision != reference.revision
                or fact.type != reference.type
                or fact.unit != reference.unit
            ):
                message = "The catalogue record changed. Review and update its reference in the COTS pane."
            if not message:
                message = component.property_reference_error(reference, fact)
            result = {
                "state": "pending" if message else "value",
                "value": None if message else fact.value,
                "message": message or "",
            }
            values[reference.name] = result
            context.append(
                [
                    component.key,
                    reference.name,
                    reference.fact,
                    reference.revision,
                    fact.revision if fact else None,
                    result,
                ]
            )
        resolved[component.key] = values
    return resolved, digest(sorted(context, key=lambda item: (item[0], item[1])))


def calculation_signature(session, *, cots_signature=ALL_MODES):
    """Content identity for calculation configuration, excluding prose and results.

    This is the evidence freshness seam for native VerificationScript runners.
    Unrelated database row additions leave selected fact identities unchanged.
    """
    if cots_signature is ALL_MODES:
        _, cots_signature = _cots_snapshot(session)
    return digest(
        {
            "statements": [
                {
                    "key": row.key,
                    "id": row.id,
                    "definition": row.definition,
                    "owner": None if row.owner is None else row.owner.key,
                    "powerScope": None
                    if row.power_scope is None
                    else row.power_scope.key,
                    "budgetScope": None
                    if row.budget_scope is None
                    else row.budget_scope.key,
                    "sources": [source.key for source in row.sources],
                    "affected": [element.key for element in row.affected],
                    "subject": None if row.subject is None else row.subject.key,
                    "parameters": [
                        _binding(parameter)
                        for _, parameter in sorted(row.parameters.items())
                    ],
                }
                for row in sorted(session.statements, key=lambda row: row.key)
            ],
            "elements": [
                {
                    "key": element.key,
                    "id": element.id,
                    "definition": element.definition,
                    "owner": None if element.owner is None else element.owner.key,
                    "selection": element.selection,
                    "properties": dict(element.property_values),
                    "budgetParameters": [_binding(parameter) for parameter in element.parameters.values()] if isinstance(element, Component) else [],
                    "propertyDefinitions": {name: [spec.value_type.__name__, spec.unit] for name, spec in element.property_definitions().items()},
                    "quantity": element.quantity,
                    "requirements": [row.key for row in element.requirement_links],
                    "types": [f"{base.__module__}.{base.__qualname__}" for base in type(element).__mro__],
                }
                for element in sorted(session.elements, key=lambda element: element.key)
            ],
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
                    "host": None if load.host is None else load.host.key,
                    "states": [
                        {
                            "key": state.key,
                            "name": state.name,
                            "watts": state.watts,
                        }
                        for state in load.states
                    ],
                    "assignments": sorted(
                        (mode.key, state.key)
                        for mode, state in load.assignments.items()
                    ),
                    "duties": sorted(
                        (mode.key, duty) for mode, duty in load.duties.items()
                    ),
                    **({"allocations": sorted(
                        (mode.key, [(item.state.key, item.duty) for item in entries])
                        for mode, entries in load.allocations.items()
                    )} if load.allocations else {}),
                }
                for load in sorted(
                    session.power.loads, key=lambda load: load.element.key
                )
            ],
            "links": [
                {
                    "eps": link.eps.key,
                    "roots": [root.key for root in link.roots],
                    "previous": {
                        name: _binding(parameter)
                        for name, parameter in sorted(link.previous.items())
                    },
                }
                for link in sorted(session.power.links, key=lambda link: link.eps.key)
            ],
            "scripts": [
                {
                    "key": script.key,
                    "id": script.id,
                    "definition": script.definition,
                    "revision": script.revision,
                    "currentRevision": getattr(
                        script, "current_revision", script.revision
                    ),
                    "inputs": [
                        (port.name, port.value_type.__name__, port.unit)
                        for port in script.inputs
                    ],
                    "outputs": [
                        (port.name, port.value_type.__name__, port.unit)
                        for port in script.outputs
                    ],
                    "parameters": [
                        _binding(parameter)
                        for _, parameter in sorted(script.parameters.items())
                    ],
                }
                for script in sorted(session.scripts, key=lambda script: script.key)
            ],
            "components": [
                {
                    "key": component.key,
                    "id": component.id,
                    "product": component.product,
                    "owner": None if component.owner is None else component.owner.key,
                    "usage": None if component.usage is None else component.usage.key,
                    "requirements": [row.key for row in component.requirement_links],
                    "facts": [reference.projection() for reference in component.facts],
                    "budgetParameters": [_binding(parameter) for parameter in component.parameters.values()] if isinstance(component, Component) else [],
                    "quantity": component.quantity,
                    "types": [f"{base.__module__}.{base.__qualname__}" for base in type(component).__mro__],
                    "propertyDefinitions": {name: [spec.value_type.__name__, spec.unit] for name, spec in component.property_definitions().items()},
                    "propertySources": {
                        name: [component.property_source(name).name, component.property_source(name).element]
                        for name in component.property_definitions()
                    },
                }
                for component in sorted(
                    session.cots_components, key=lambda component: component.key
                )
            ],
            "cotsSignature": cots_signature,
        }
    )


def _field(value, name, default=None):
    return (
        value.get(name, default)
        if isinstance(value, Mapping)
        else getattr(value, name, default)
    )


def _kind(value_type):
    return (
        "boolean" if value_type is bool else "string" if value_type is str else "number"
    )


def coerce(value, value_type, label):
    if value is None:
        raise PendingValue(f"{label} is unset.")
    if value_type is bool:
        if type(value) is not bool:
            raise ValueError(f"{label} must produce a Boolean.")
        return value
    if value_type is str:
        if type(value) is not str:
            raise ValueError(f"{label} must produce a string.")
        return value
    finite_number(value)
    if value_type is int:
        if int(value) != value or abs(value) > 9007199254740991:
            raise ValueError(f"{label} must produce a safe integer.")
        return int(value)
    return float(value)


class NativeValues(Mapping):
    """Lazy owned parameters presented to a trusted native calculation function."""

    def __init__(self, context, row):
        self.context, self.row = context, row

    @property
    def mode(self):
        return self.context.mode

    def __getitem__(self, name):
        if name not in self.row.parameters:
            raise KeyError(name)
        return self.context.parameter(self.row, name)

    def __iter__(self):
        return iter(self.row.parameters)

    def __len__(self):
        return len(self.row.parameters)

    def count_assigned(self, component_type, **options):
        return self.context.count_assignments(self.row, component_type, **options)

    def all_assigned(self, component_type, property_name, comparison, target, **tolerances):
        return self.context.check_assignments(self.row, "all_assigned", component_type, property_name, comparison, target, **tolerances)

    def sum_assigned(self, component_type, property_name, comparison, target, **tolerances):
        return self.context.check_assignments(self.row, "sum_assigned", component_type, property_name, comparison, target, **tolerances)


class EvaluationContext:
    """A single-mode request-local calculation over authoritative native objects.

    Evidence can be a record with signature/cots_signature and result_for(script,
    mode), or a mapping with signature/cotsSignature/runs. A runner must obtain
    that signature from this package. Contexts never execute analysis scripts.
    An optional source_ready(source, context) callback may impose extra gating.
    """

    def __init__(
        self,
        session,
        mode=None,
        *,
        evidence=None,
        source_ready=None,
        budget=None,
        _snapshot=None,
        _signature=None,
    ):
        self.session = session
        self.mode = None if mode is None else session.resolve_mode(mode)
        self.evidence = (
            getattr(session, "_execution_evidence", None)
            if evidence is None
            else evidence
        )
        self.source_callback = source_ready
        self.rows = {row.id: row for row in (*session.statements, *session.components)}
        self.scripts = {script.id: script for script in session.scripts}
        self.cots = {component.id: component for component in session.cots_components}
        self.property_owners = {element.id: element for element in session.all_elements if element.property_definitions()}
        self.namespaces = session.expression_namespaces()
        self.identifiers = {*self.rows, *self.scripts, *self.cots, *self.property_owners,
                            *(name.split(".")[0] for name in self.namespaces)}
        self.cache, self.resolving = {}, set()
        self.cots_values, self.cots_signature = (
            _cots_snapshot(session) if _snapshot is None else _snapshot
        )
        self.signature = (
            calculation_signature(session, cots_signature=self.cots_signature)
            if _signature is None
            else _signature
        )
        self.engine = RestrictedPython(self, budget)
        self._mode_contexts = {self.mode: self}

    def for_mode(self, mode):
        """Reuse one snapshot, operation budget and dependency guard across modes."""
        mode = None if mode is None else self.session.resolve_mode(mode)
        if mode not in self._mode_contexts:
            context = EvaluationContext(
                self.session,
                mode,
                evidence=self.evidence,
                source_ready=self.source_callback,
                budget=self.engine.budget,
                _snapshot=(self.cots_values, self.cots_signature),
                _signature=self.signature,
            )
            context.resolving = self.resolving
            context._mode_contexts = self._mode_contexts
            self._mode_contexts[mode] = context
        return self._mode_contexts[mode]

    @contextmanager
    def activate(self):
        token = _ACTIVE.set(self)
        try:
            yield self
        finally:
            _ACTIVE.reset(token)

    def _parameter_owner(self, identifier, field):
        owner = self.rows.get(identifier)
        if owner is None or field not in owner.parameters:
            return None
        if isinstance(owner, DatabaseBacked) and any(fact.name == field for fact in owner.facts):
            parameter = owner.parameters[field]
            default = parameter.value is None and parameter.expression is None
            if field == "average_power_W" and parameter.expression == "draw_power_W":
                draw = owner.parameters["draw_power_W"]
                default = draw.value is None and draw.expression is None
            if not default:
                raise ValueError(f"Rename the selected fact {owner.id}.{field} before using that name for an installed budget input.")
            return None
        return owner

    def reference_type(self, name, row):
        if name == "mode":
            return "string"
        if "." not in name:
            parameter = getattr(row, "parameters", {}).get(name)
            if parameter is None:
                raise ValueError(f"Unknown variable “{name}”.")
            return _kind(parameter.value_type)
        identifier, field = name.rsplit(".", 1)
        if identifier in self.namespaces:
            parameter = self.namespaces[identifier].parameters.get(field)
            if parameter is None:
                raise ValueError(f"Unknown calculated value “{name}”.")
            return _kind(parameter.value_type)
        if identifier in self.property_owners:
            specification = self.property_owners[identifier].property_definitions().get(field)
            if specification is not None:
                return _kind(specification.value_type)
        owner = self._parameter_owner(identifier, field)
        if owner is not None:
            return _kind(owner.parameters[field].value_type)
        if identifier in self.cots:
            reference = next(
                (
                    reference
                    for reference in self.cots[identifier].facts
                    if reference.name == field
                ),
                None,
            )
            if reference is None:
                raise ValueError(
                    f"Unknown COTS reference “{name}”. Select it in the COTS pane."
                )
            return (
                "boolean"
                if reference.type == "boolean"
                else "string"
                if reference.type == "string"
                else "number"
            )
        if identifier in self.scripts:
            parameter = next(
                (
                    port
                    for port in self.scripts[identifier].outputs
                    if port.name == field
                ),
                None,
            )
            if parameter is None:
                raise ValueError(f"Unknown output “{name}”.")
        else:
            target = self.rows.get(identifier)
            if target is None:
                raise ValueError(f"Unknown row “{identifier}”.")
            parameter = target.parameters.get(field)
            if parameter is None:
                raise ValueError(f"Unknown variable “{field}” in {identifier}.")
        return _kind(parameter.value_type)

    def resolve_reference(self, name, row):
        if name in CONSTANTS:
            return CONSTANTS[name]
        if name == "mode":
            if self.mode is None:
                raise PendingValue("Select a spacecraft mode.")
            return self.mode.name
        if "." not in name:
            return self.parameter(row, name)
        identifier, field = name.rsplit(".", 1)
        if identifier in self.namespaces:
            self.reference_type(name, row)
            key = (row.key, f"calculated:{name}", None if self.mode is None else self.mode.key)
            if key not in self.cache:
                if key in self.resolving:
                    raise ValueError(f"Cyclic calculated value at {name}.")
                self.resolving.add(key)
                try:
                    namespace = self.namespaces[identifier]
                    self.cache[key] = coerce(namespace.resolve(self, row, field),
                                             namespace.parameters[field].value_type, name)
                finally:
                    self.resolving.remove(key)
            return self.cache[key]
        if identifier in self.property_owners and field in self.property_owners[identifier].property_definitions():
            return self.component_property(self.property_owners[identifier], field)
        owner = self._parameter_owner(identifier, field)
        if owner is not None:
            return self.parameter(owner, field)
        if identifier in self.cots:
            return self.cots_fact(self.cots[identifier], field)
        if identifier in self.scripts:
            script = self.scripts[identifier]
            result = self.script_result(script)
            port = next(port for port in script.outputs if port.name == field)
            return coerce(
                _field(result, "values", {}).get(field), port.value_type, name
            )
        return self.parameter(self.rows[identifier], field)

    def value(self, row, name):
        row = self.session.get(row)
        if "." in name:
            reference = f"{row.id}.{name}"
            self.reference_type(reference, row)
            return self.resolve_reference(reference, row)
        if hasattr(row, "property_definitions") and name in row.property_definitions():
            return self.component_property(row, name)
        if isinstance(row, ScriptConfiguration) and name not in row.parameters:
            reference = f"{row.id}.{name}"
            self.reference_type(reference, row)
            return self.resolve_reference(reference, row)
        return self.parameter(row, name)

    def parameter(self, row, name):
        row = self.session.get(row)
        key = (row.key, name, None if self.mode is None else self.mode.key)
        if key in self.cache:
            value = self.cache[key]
            if isinstance(value, Exception):
                raise value
            return value
        if key in self.resolving:
            raise ValueError(f"Cyclic parameter expression at {row.id}.{name}.")
        if len(self.resolving) >= 64:
            raise ValueError("Parameter expressions are nested too deeply.")
        parameter = row.parameters.get(name)
        if parameter is None:
            raise ValueError(f"Unknown variable “{name}” in {row.id}.")
        self.resolving.add(key)
        try:
            source = parameter.expression
            if isinstance(source, DraftExpression):
                if not source.source.strip():
                    raise PendingValue(f"{row.id}.{name} is unset.")
                raise ValueError(source.error)
            with self.activate():
                if isinstance(source, str):
                    value = self.engine.evaluate(
                        source, row, _kind(parameter.value_type)
                    )
                elif source is not None:
                    value = source(NativeValues(self, row))
                else:
                    value = parameter.value
            value = coerce(value, parameter.value_type, f"{row.id}.{name}")
            if isinstance(row, Statement):
                row.validate_parameter_value(name, value)
            if isinstance(row, Component) and value < 0:
                raise ValueError("Component budget contributions must be nonnegative.")
            self.cache[key] = value
            return value
        except Exception as error:
            self.cache[key] = error
            raise
        finally:
            self.resolving.remove(key)

    def component_property(self, component, name):
        component = self.session.get(component)
        specification = component.property_definitions().get(name)
        if specification is None:
            raise ValueError(f"Unknown component property {component.id}.{name}.")
        key = (component.key, f"property:{name}")
        if key not in self.cache:
            try:
                value = (
                    self.cots_fact(component, name) if isinstance(component, DatabaseBacked)
                    else component._property_value(name)
                )
                self.cache[key] = coerce(value, specification.value_type, f"{component.id}.{name}")
            except Exception as error:
                self.cache[key] = error
        value = self.cache[key]
        if isinstance(value, Exception):
            raise value
        return value

    def count_assignments(self, row, component_type, **options):
        from .assignments import count_assigned

        return count_assigned(NativeValues(self, row), component_type, **options)

    def check_assignments(self, row, operation, component_type, property_name, comparison, target, **tolerances):
        from .assignments import all_assigned, sum_assigned

        function = {"all_assigned": all_assigned, "sum_assigned": sum_assigned}[operation]
        return function(NativeValues(self, row), component_type, property_name, comparison, target, **tolerances)

    def component_state_power(self, element, state):
        """Resolve a state binding with the common cache and cycle detection."""
        key = (
            element.key,
            f"power-state:{state.key}",
            None if self.mode is None else self.mode.key,
        )
        if key in self.cache:
            value = self.cache[key]
            if isinstance(value, Exception):
                raise value
            return value
        if key in self.resolving or len(self.resolving) >= 64:
            raise ValueError(
                f"Cyclic or excessively nested power expression at {element.id}."
            )
        self.resolving.add(key)
        try:
            with self.activate():
                value = (
                    self.engine.evaluate(state.watts, element, "number")
                    if isinstance(state.watts, str)
                    else state.watts
                )
            value = coerce(value, float, f"{element.id} state {state.name} power")
            if value < 0:
                raise ValueError("Component power draw must be nonnegative.")
            self.cache[key] = value
            return value
        except Exception as error:
            self.cache[key] = error
            raise
        finally:
            self.resolving.remove(key)

    def condition(self, source, row):
        return self.engine.evaluate(source, row, "boolean")

    def cots_fact(self, component, name):
        result = self.cots_values.get(component.key, {}).get(name)
        if result is None or result["state"] != "value":
            message = (
                "Select a current catalogue record in the COTS pane."
                if result is None
                else result["message"]
            )
            raise PendingValue(f"{component.id}.{name}: {message}")
        return result["value"]

    def component_ready(self, component):
        if not component.facts:
            raise PendingValue(
                f"Select fact references for {component.id} in its COTS pane."
            )
        for reference in component.facts:
            self.cots_fact(component, reference.name)
        return True

    def script_result(self, script):
        script = self.session.get(script)
        if not getattr(
            script,
            "revision_is_current",
            getattr(script, "current_revision", script.revision) == script.revision,
        ):
            raise PendingValue(
                f"{script.id}: the implementation changed. Review and update its definition before running.",
                script_key=script.key,
                mode_key=None if self.mode is None else self.mode.key,
            )
        evidence = self.evidence
        signature = _field(evidence, "signature")
        cots_signature = _field(
            evidence, "cots_signature", _field(evidence, "cotsSignature")
        )
        if (
            evidence is None
            or signature != self.signature
            or cots_signature != self.cots_signature
        ):
            raise PendingValue(
                f"Run {script.id} for the current inputs{' and mode' if self.mode else ''}.",
                script_key=script.key,
                mode_key=None if self.mode is None else self.mode.key,
            )
        if hasattr(evidence, "result_for"):
            result = evidence.result_for(script, self.mode)
        else:
            identity = f"{script.key}:{self.mode.key if self.mode is not None else ''}"
            result = _field(evidence, "runs", {}).get(identity)
        implementation_revision = _field(
            result, "implementation_revision", _field(result, "implementationRevision")
        )
        if (
            result is None
            or _field(result, "revision") != script.revision
            or implementation_revision is not None
            and implementation_revision
            != getattr(script, "current_revision", script.revision)
        ):
            raise PendingValue(
                f"Run {script.id} for the current inputs{' and mode' if self.mode else ''}.",
                script_key=script.key,
                mode_key=None if self.mode is None else self.mode.key,
            )
        state = _field(result, "state")
        if isinstance(state, VerificationState):
            state = state.value
        if state != "value":
            message = _field(result, "message", "The script has no execution result.")
            if state == "pending":
                raise PendingValue(
                    message,
                    script_key=script.key,
                    mode_key=None if self.mode is None else self.mode.key,
                )
            raise ValueError(message)
        return result

    def source_ready(self, source):
        self.session.get(source)
        if isinstance(source, DatabaseBacked):
            ready = self.component_ready(source)
        elif isinstance(source, ScriptConfiguration):
            self.script_result(source)
            ready = True
        elif self.source_callback is None:
            raise PendingValue(
                "Current evidence is required for the selected verification source."
            )
        else:
            ready = True
        return ready and (
            self.source_callback is None or bool(self.source_callback(source, self))
        )

    def verify(self, row):
        row = self.session.get(row)
        with self.activate():
            return VerificationResult(
                tuple(
                    method.evaluate(
                        NativeValues(self, row),
                        lambda source: self.condition(source, row),
                        self.source_ready,
                    )
                    for method in row.verifications
                )
            )


def resolve_modes(session, mode=ALL_MODES):
    if mode is ALL_MODES:
        return tuple(session.power.modes) or (None,)
    return (None if mode is None else session.resolve_mode(mode),)


def context_for(session, mode=None, **kwargs):
    return EvaluationContext(session, mode, **kwargs)


def _contexts(session, modes, *, evidence=None, source_ready=None):
    # One trusted database snapshot and one operation budget per request,
    # including all spacecraft modes. UI-supplied fact values are never used.
    snapshot = _cots_snapshot(session)
    signature = calculation_signature(session, cots_signature=snapshot[1])
    budget = [2_000_000]
    return [
        EvaluationContext(
            session,
            selected,
            evidence=evidence,
            source_ready=source_ready,
            budget=budget,
            _snapshot=snapshot,
            _signature=signature,
        )
        for selected in modes
    ]


def value(session, row, name, *, mode=ALL_MODES, evidence=None, source_ready=None):
    active = current_context(session)
    if active is not None and evidence is None and source_ready is None:
        selected = (
            active.mode
            if mode is ALL_MODES
            else None
            if mode is None
            else session.resolve_mode(mode)
        )
        if selected is active.mode:
            return active.value(row, name)
    modes = resolve_modes(session, mode)
    results, errors = [], []
    for context in _contexts(
        session, modes, evidence=evidence, source_ready=source_ready
    ):
        try:
            results.append((context.mode, context.value(row, name)))
        except Exception as error:
            errors.append(error)
    if errors:
        raise next(
            (error for error in errors if not isinstance(error, PendingValue)),
            errors[0],
        )
    if all(result == results[0][1] for _, result in results):
        return results[0][1]
    return MappingProxyType({selected.name: result for selected, result in results})


@dataclass(frozen=True)
class ModeVerification:
    key: str
    name: str
    result: VerificationResult


class VerificationReport(Mapping):
    """Fresh per-statement assessments, addressable by object, ID or key."""

    def __init__(self, assessments):
        self.assessments = tuple(assessments)

    def __iter__(self):
        return (row.id for row, _ in self.assessments)

    def __len__(self):
        return len(self.assessments)

    def __getitem__(self, identity):
        for row, result in self.assessments:
            if identity is row or identity in (row.id, row.key):
                return result
        raise KeyError(identity)

    @property
    def verified(self):
        return bool(self.assessments) and all(
            result.verified for _, result in self.assessments
        )

    @property
    def state(self):
        return VerificationState(
            state_of([{"state": result.state.value} for _, result in self.assessments])
        )


def _combine_checks(results, modes):
    if len(results) == 1:
        return results[0]
    combined = []
    for index, method in enumerate(results[0].methods):
        cells = [result.methods[index] for result in results]
        state = VerificationState(
            state_of([{"state": cell.state.value} for cell in cells])
        )
        message = "\n".join(
            f"{mode.name}: {cell.message or cell.state.value}"
            for mode, cell in zip(modes, cells)
        )
        combined.append(MethodResult(method.name, state, message))
    return VerificationResult(
        tuple(combined),
        tuple(
            ModeVerification(mode.key, mode.name, result)
            for mode, result in zip(modes, results)
        ),
    )


def verify(session, identity=None, *, mode=ALL_MODES, evidence=None, source_ready=None):
    active = current_context(session)
    if (
        active is not None
        and mode is ALL_MODES
        and evidence is None
        and source_ready is None
    ):
        if identity is not None:
            return active.verify(session.get(identity))
    rows = session.statements if identity is None else (session.get(identity),)
    if any(not isinstance(row, Statement) for row in rows):
        raise TypeError("Verify a Requirement or Statement instance.")
    modes = resolve_modes(session, mode)
    contexts = _contexts(session, modes, evidence=evidence, source_ready=source_ready)
    assessments = tuple(
        (row, _combine_checks([context.verify(row) for context in contexts], modes))
        for row in rows
    )
    return VerificationReport(assessments) if identity is None else assessments[0][1]


def state_of(results):
    return next(
        (
            state
            for state in PRIORITY
            if any(result["state"] == state for result in results)
        ),
        "unset",
    )


def branches(context, source):
    if not isinstance(source, str):
        return None
    try:
        tree, text = context.engine.tree(source.strip())
        modes = context.session.power.modes

        def guard(node):
            if (
                not isinstance(node, ast.Compare)
                or len(node.ops) != 1
                or type(node.ops[0]) not in (ast.Eq, ast.NotEq)
            ):
                return None
            left, right = node.left, node.comparators[0]
            literal = (
                right
                if symbol(left) == "mode"
                else left
                if symbol(right) == "mode"
                else None
            )
            if not isinstance(literal, ast.Constant) or not isinstance(
                literal.value, str
            ):
                return None
            mode = next((mode for mode in modes if mode.name == literal.value), None)
            return (mode, isinstance(node.ops[0], ast.Eq)) if mode is not None else None

        first = guard(tree.test) if isinstance(tree, ast.IfExp) else None
        if first is None:
            return None

        def branch(node, mode):
            condition = guard(node.test) if isinstance(node, ast.IfExp) else None
            if condition is not None:
                return branch(
                    node.body
                    if (condition[0].key == mode.key) == condition[1]
                    else node.orelse,
                    mode,
                )
            if isinstance(node, ast.Constant) and node.value is None:
                return None
            return ast.get_source_segment(text, node)

        return {
            "values": {mode.key: branch(tree, mode) for mode in modes},
            "lastEdited": first[0].key,
        }
    except (ValueError, SyntaxError, TypeError):
        return None


def parameter_result(context, row, name):
    link = row.linked_parameter(name) if hasattr(row, "linked_parameter") else None
    parameter = link[0].parameters[link[1]] if link else row.parameters.get(name)
    if (
        parameter is None
        or parameter.value is None
        and (
            parameter.expression is None
            or isinstance(parameter.expression, DraftExpression)
            and not parameter.expression.source.strip()
        )
    ):
        return {
            "state": "unset",
            "value": None,
            "message": "No Python parameter expression.",
        }
    try:
        result = context.parameter(row, name)
        return {"state": "value", "value": result, "message": f"= {result}"}
    except Exception as error:
        return {
            "state": "pending" if isinstance(error, PendingValue) else "error",
            "value": None,
            "message": str(error)[:300],
        }


def _condition_text(method):
    if isinstance(method.condition, DraftExpression):
        return method.condition.source
    return (
        method.condition
        if isinstance(method.condition, str)
        else getattr(method.condition, "__qualname__", method.name)
    )


def compute(context):
    results, scripts = [], []
    display_names = [variable.name for variable in context.session.variables]
    for row in context.session.statements:
        names = tuple(dict.fromkeys((*display_names, *row.parameters)))
        parameters = {name: parameter_result(context, row, name) for name in names}
        assessment = context.verify(row)
        methods = [
            {
                "key": method.key,
                "state": result.state.value,
                "message": result.message or _condition_text(method),
            }
            for method, result in zip(row.verifications, assessment.methods)
        ]
        results.append(
            {
                "key": row.key,
                "parameters": parameters,
                "values": {
                    name: result["value"] for name, result in parameters.items()
                },
                "methods": methods,
                "state": assessment.state.value,
                "message": "\n".join(result["message"] for result in methods)
                if methods
                else "No verification condition. Add a Python condition to verify this row.",
            }
        )
    for script in context.session.scripts:
        parameters = {
            name: parameter_result(context, script, name) for name in script.parameters
        }
        scripts.append(
            {
                "key": script.key,
                "parameters": parameters,
                "values": {
                    name: result["value"] for name, result in parameters.items()
                },
            }
        )
    return results, scripts


def aggregate(results, modes, methods=False):
    def describe(items):
        return "\n".join(
            f"{mode.name}: {item.get('message', '')}"
            for mode, item in zip(modes, items)
        )

    parameters = {}
    for name in results[0]["parameters"]:
        cells = [result["parameters"][name] for result in results]
        same = all(
            cell["state"] == "value" and cell["value"] == cells[0]["value"]
            for cell in cells
        ) or all(cell == cells[0] for cell in cells)
        parameters[name] = (
            cells[0]
            if same
            else {
                "state": "varying"
                if all(cell["state"] == "value" for cell in cells)
                else state_of(cells),
                "value": None,
                "message": describe(cells),
            }
        )
    mode_results = []
    for mode, result in zip(modes, results):
        item = {"mode": mode.key, **result}
        if methods:
            item["parameters"] = {
                name: cell
                for name, cell in result["parameters"].items()
                if cell["state"] != "unset"
            }
            item["values"] = {
                name: cell["value"] for name, cell in item["parameters"].items()
            }
        mode_results.append(item)
    combined = {
        "key": results[0]["key"],
        "parameters": parameters,
        "values": {name: cell["value"] for name, cell in parameters.items()},
        "modes": mode_results,
    }
    if methods:
        combined.update(state=state_of(results), message=describe(results), methods=[])
        for index, method in enumerate(results[0]["methods"]):
            cells = [result["methods"][index] for result in results]
            combined["methods"].append(
                {
                    "key": method["key"],
                    "state": state_of(cells),
                    "message": describe(cells),
                    "modes": [
                        {"mode": mode.key, **cell} for mode, cell in zip(modes, cells)
                    ],
                }
            )
    return combined


def evaluate(session, *, mode=ALL_MODES, evidence=None, source_ready=None):
    """Project common native calculations for the browser, without importing DTOs."""
    modes = resolve_modes(session, mode)
    contexts = _contexts(session, modes, evidence=evidence, source_ready=source_ready)
    batches = [compute(context) for context in contexts]
    if mode is ALL_MODES and session.power.modes:
        results = [
            aggregate([batch[0][index] for batch in batches], modes, True)
            for index in range(len(session.statements))
        ]
        scripts = [
            aggregate([batch[1][index] for batch in batches], modes)
            for index in range(len(session.scripts))
        ]
    else:
        results, scripts = batches[0]
    metadata = contexts[0]
    for row, result in zip(session.statements, results):
        for name, parameter in row.parameters.items():
            link = row.linked_parameter(name)
            if link is not None:
                parameter = link[0].parameters[link[1]]
            branch = branches(metadata, parameter.expression)
            if branch is not None:
                result["parameters"][name]["branches"] = branch
                result["parameters"][name]["expressionSource"] = parameter.expression
    checks = {result["key"]: result for result in results}
    components = []
    for component in session.cots_components:
        assessment = component.assess(checks)
        components.append(
            {
                "key": component.key,
                "state": assessment.state.value,
                "message": "\n".join(
                    f"{method.name}: {method.message}" for method in assessment.methods
                )
                if assessment.methods
                else "Link at least one requirement to verify this component.",
            }
        )
    return {
        "results": results,
        "scripts": scripts,
        "components": components,
        "engine": "python",
        "cotsSignature": metadata.cots_signature,
    }


def script_inputs(session, script, *, mode=None, evidence=None):
    """Resolve declared inputs for a future explicit native script runner."""
    script = session.get(script)
    if not isinstance(script, ScriptConfiguration):
        raise TypeError("Choose an existing verification script instance.")
    context = EvaluationContext(session, mode, evidence=evidence)
    inputs = {port.name: context.parameter(script, port.name) for port in script.inputs}
    requirements = {
        row.id: {
            name: parameter_result(context, row, name)["value"]
            for name in row.parameters
        }
        for row in session.statements
    }
    return {
        "inputs": inputs,
        "requirements": requirements,
        "signature": context.signature,
        "cotsSignature": context.cots_signature,
    }
