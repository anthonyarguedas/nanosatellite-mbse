"""Interoperable analysis classes and requirement predicate interfaces.

Analysis execution is explicit and trusted. Calculations produce evidence.
Requirement predicates separately decide whether that evidence satisfies a limit.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import marshal
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .configuration import ScriptConfiguration, ScriptPort
from .predicates import (
    DraftExpression,
    Expression,
    MethodResult,
    PendingValue,
    Scalar,
    VerificationMethod,
    VerificationResult,
    VerificationState,
    restored_expression,
    validate_expression,
)
from .requirements import Parameter, _parameter_name

KINDS = {float: "float", int: "integer", bool: "boolean", str: "string"}
PYTHON_TYPES = {name: kind for kind, name in KINDS.items()}
EXECUTION_PROTOCOL_REVISION = "native-verification-v1"


def _port(port):
    if not isinstance(port, ScriptPort):
        raise TypeError("Declare analysis ports as ScriptPort instances.")
    _parameter_name(port.name)
    if port.value_type not in KINDS:
        raise TypeError("An analysis port needs a supported scalar type.")
    if port.unit is not None and (
        not isinstance(port.unit, str)
        or len(port.unit) > 100
        or "\n" in port.unit
        or "\r" in port.unit
    ):
        raise ValueError("Analysis units must be single-line labels.")


def port_projection(port):
    return {
        "name": port.name,
        "type": KINDS[port.value_type],
        **({"unit": port.unit} if port.unit is not None else {}),
    }


@dataclass(frozen=True)
class ScriptDefinition:
    """Reusable Python-declared interface, independent of populated instances."""

    id: str
    name: str
    description: str
    inputs: tuple
    outputs: tuple
    timeout_ms: int = 3000

    def __post_init__(self):
        if not isinstance(self.id, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]{0,79}", self.id
        ):
            raise ValueError("Choose an analysis definition ID.")
        if not isinstance(self.name, str) or not 1 <= len(self.name.strip()) <= 80:
            raise ValueError("Name the analysis using 1 to 80 characters.")
        if not isinstance(self.description, str) or len(self.description) > 2000:
            raise ValueError("Analysis descriptions contain at most 2,000 characters.")
        if not isinstance(self.inputs, tuple) or len(self.inputs) > 32:
            raise ValueError("Declare up to 32 analysis inputs.")
        if not isinstance(self.outputs, tuple) or not 1 <= len(self.outputs) <= 32:
            raise ValueError("Declare 1 to 32 analysis outputs.")
        names = set()
        for port in (*self.inputs, *self.outputs):
            _port(port)
            if port.name in names:
                raise ValueError("Analysis input and output names must be unique.")
            names.add(port.name)
        if type(self.timeout_ms) is not int or not 10 <= self.timeout_ms <= 10000:
            raise ValueError("Analysis timeouts range from 10 through 10,000 ms.")

    def projection(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "inputs": [port_projection(port) for port in self.inputs],
            "outputs": [port_projection(port) for port in self.outputs],
            "timeoutMs": self.timeout_ms,
        }

    @classmethod
    def from_metadata(cls, data):
        allowed = {"id", "name", "description", "inputs", "outputs", "timeoutMs"}
        if not isinstance(data, dict) or set(data) - allowed:
            raise ValueError("Invalid registered analysis metadata.")

        def read_port(item):
            if not isinstance(item, dict) or set(item) - {"name", "type", "unit"}:
                raise ValueError("Invalid registered analysis port.")
            return ScriptPort(
                item["name"], PYTHON_TYPES[item["type"]], item.get("unit")
            )

        return cls(
            data["id"],
            data["name"],
            data["description"],
            tuple(map(read_port, data["inputs"])),
            tuple(map(read_port, data["outputs"])),
            data.get("timeoutMs", 3000),
        )


def implementation_revision(cls, definition):
    """Portable source/interface identity, refreshed when trusted source changes."""
    parts = {
        "class": f"{cls.__module__}:{cls.__qualname__}",
        "interface": definition.projection(),
        "protocol": EXECUTION_PROTOCOL_REVISION,
    }
    files, seen = [], set()
    implementation = getattr(cls.calculate, "__func__", cls.calculate)
    for item in (cls, implementation, *getattr(cls, "revision_dependencies", ())):
        try:
            source_file = inspect.getsourcefile(item)
        except (TypeError, OSError):
            source_file = None
        if source_file is not None and Path(source_file).is_file():
            path = Path(source_file)
            if path not in seen:
                seen.add(path)
                files.append(
                    (
                        getattr(item, "__module__", path.name),
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                )
        elif callable(item):
            code = getattr(item, "__code__", None)
            if code is not None:
                parts[getattr(item, "__qualname__", "code")] = marshal.dumps(code).hex()
    if not files and not any(
        key not in ("class", "interface", "protocol") for key in parts
    ):
        raise ValueError("An analysis implementation needs identifiable source.")
    parts["files"] = files
    return hashlib.sha256(
        json.dumps(parts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class VerificationScript(ScriptConfiguration):
    """Base for reusable analyses with declared ports and explicit execution.

    Subclasses declare definition_spec and implement calculate(). Use run() on
    an attached instance for dependency resolution, evidence and bounded default
    process execution. Calling calculate() directly is an unbounded trusted call.
    """

    definition_spec = None
    revision_dependencies = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if isinstance(cls.definition_spec, ScriptDefinition):
            cls._loaded_implementation_revision = implementation_revision(
                cls, cls.definition_spec
            )

    def __init__(
        self,
        id="",
        *,
        revision=None,
        inputs=None,
        outputs=None,
        parameters=(),
        definition=None,
        name=None,
        **kwargs,
    ):
        spec = self.spec
        if definition is not None and definition != spec.id:
            raise ValueError("The analysis class and definition ID must agree.")
        super().__init__(
            id,
            name=spec.name if name is None else name,
            definition=spec.id,
            revision=self.current_revision if revision is None else revision,
            inputs=spec.inputs if inputs is None else inputs,
            outputs=spec.outputs if outputs is None else outputs,
            parameters=parameters,
            **kwargs,
        )

    @property
    def spec(self):
        if not isinstance(self.definition_spec, ScriptDefinition):
            raise TypeError("Declare a ScriptDefinition on the analysis subclass.")
        return self.definition_spec

    @property
    def current_revision(self):
        return implementation_revision(type(self), self.spec)

    @property
    def implementation_revision(self):
        return self.current_revision

    @property
    def revision_is_current(self):
        return self.revision == self.current_revision

    def assert_current(self):
        if (
            tuple(self.inputs) != self.spec.inputs
            or tuple(self.outputs) != self.spec.outputs
        ):
            raise PendingValue(
                f"{self.id}: the declared interface changed. Review and update its definition before running.",
                script_key=self.key,
            )
        if not self.revision_is_current:
            raise PendingValue(
                f"{self.id}: the implementation changed. Review and update its definition before running.",
                script_key=self.key,
            )

    def describe(self):
        return {**self.spec.projection(), "revision": self.current_revision}

    def update_definition(self):
        """Explicitly accept a current interface while retaining named bindings."""
        retained = {}
        for port in self.spec.inputs:
            old = self.parameters.get(port.name)
            if old is None:
                parameter = Parameter(port.name, port.value_type, port.unit or "")
            else:
                try:
                    parameter = Parameter(
                        port.name,
                        port.value_type,
                        port.unit or "",
                        old.value,
                        old.expression,
                    )
                except (TypeError, ValueError):
                    parameter = Parameter(
                        port.name,
                        port.value_type,
                        port.unit or "",
                        expression=repr(old.value),
                    )
            retained[port.name] = parameter
        self.inputs, self.outputs = self.spec.inputs, self.spec.outputs
        self.parameters = retained
        self.revision = self.current_revision
        if self.session is not None:
            self.session._model_state_present = True
        return self

    def set_value(self, name, value):
        from dataclasses import replace

        self.parameters[name] = replace(
            self.parameters[name], value=value, expression=None
        )
        if self.session is not None:
            self.session._model_state_present = True

    def set_expression(self, name, expression):
        from dataclasses import replace

        self.parameters[name] = replace(
            self.parameters[name], value=None, expression=expression
        )
        if self.session is not None:
            self.session._model_state_present = True

    def validate_inputs(self, values):
        from .evaluation import coerce

        if not isinstance(values, dict) or set(values) != {
            port.name for port in self.inputs
        }:
            raise ValueError(
                f"{self.id or self.definition}: supply exactly the declared inputs."
            )
        return {
            port.name: coerce(
                values[port.name],
                port.value_type,
                f"{self.id or self.definition}.{port.name}",
            )
            for port in self.inputs
        }

    def validate_outputs(self, values):
        from .evaluation import coerce

        if not isinstance(values, dict) or set(values) != {
            port.name for port in self.outputs
        }:
            raise ValueError(
                f"{self.id or self.definition}: return exactly the declared output names."
            )
        checked = {}
        for port in self.outputs:
            value = values[port.name]
            if value is None:
                checked[port.name] = None
                continue
            checked[port.name] = coerce(
                value, port.value_type, f"{self.id or self.definition}.{port.name}"
            )
        return checked

    def calculate(self, inputs, *, requirements=None, mode=None):
        raise NotImplementedError("Implement the analysis calculation in a subclass.")

    def value(self, name, **kwargs):
        """Read a current output or bound input through the shared evaluator."""
        if self.session is None:
            raise ValueError("Attach the script to a Session before resolving values.")
        return self.session.value(self, name, **kwargs)

    def run(self, context=None, **kwargs):
        """Run this registered instance through its native session runner."""
        session = (
            self.session if context is None else getattr(context, "session", context)
        )
        if session is None or not hasattr(session, "script_inputs"):
            raise ValueError(
                "Attach the script to a Session or supply a session context before running."
            )
        if context is not None and hasattr(context, "mode") and "mode" not in kwargs:
            kwargs["mode"] = context.mode
        return session.run(self, **kwargs)


class UnresolvedVerification(VerificationScript):
    """A missing registered definition, preserved for repair without execution."""

    def __init__(
        self, id="", *, definition, inputs=(), outputs=(), name=None, **kwargs
    ):
        self._missing_spec = ScriptDefinition(
            definition,
            name or definition,
            "Unavailable registered analysis definition.",
            tuple(inputs),
            tuple(outputs),
        )
        super().__init__(
            id,
            definition=definition,
            inputs=inputs,
            outputs=outputs,
            name=name,
            **kwargs,
        )

    @classmethod
    def restore(cls, id="", **configuration):
        return cls(id, **configuration)

    @property
    def spec(self):
        return self._missing_spec

    @property
    def current_revision(self):
        return "unavailable"

    @property
    def revision_is_current(self):
        return False

    def assert_current(self):
        raise PendingValue(
            f"{self.id}: registered definition {self.definition!r} is unavailable.",
            script_key=self.key,
        )

    def update_definition(self):
        raise ValueError("Register the missing definition before updating it.")


def cli_main(script_class):
    """Thin stdin/stdout adapter for a concrete importable implementation."""
    try:
        request = json.load(sys.stdin)
        script = script_class()
        inputs = script.validate_inputs(request["inputs"])
        values = script.calculate(
            inputs,
            requirements=request.get("requirements", {}),
            mode=request.get("mode"),
        )
        json.dump(script.validate_outputs(values), sys.stdout, allow_nan=False)
        return 0
    except Exception as error:
        print(
            f"{script_class.__name__}: {type(error).__name__}: {error}", file=sys.stderr
        )
        return 1


__all__ = [
    "DraftExpression",
    "Expression",
    "MethodResult",
    "PendingValue",
    "Scalar",
    "VerificationMethod",
    "VerificationResult",
    "VerificationState",
    "restored_expression",
    "validate_expression",
    "ScriptDefinition",
    "ScriptPort",
    "VerificationScript",
    "UnresolvedVerification",
    "cli_main",
]
