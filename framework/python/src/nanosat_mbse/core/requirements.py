"""Persistent requirement objects, independent of storage and presentation."""

from __future__ import annotations

import keyword
import math
import re
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Dict, Iterable, Iterator, Mapping, Optional, Protocol, Tuple, Type
from uuid import uuid4

from .identity import ALL_MODES, Identified
from .predicates import (
    DraftExpression,
    Expression,
    PendingValue,
    Scalar,
    VerificationMethod,
    VerificationResult,
    validate_expression,
)


def _parameter_name(name: str) -> None:
    if (
        not isinstance(name, str)
        or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name)
        or keyword.iskeyword(name)
        or name.startswith("__")
    ):
        raise ValueError(f"Invalid parameter name: {name!r}.")


def _text(value: str, label: str, required: bool = False) -> str:
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f"{label} must be {'nonempty ' if required else ''}text.")
    return value


class ExpressionEvaluator(Protocol):
    """Adapter for editable expression source and external reference resolution."""

    def __call__(
        self, source: str, requirement: Requirement, values: Mapping[str, Scalar]
    ) -> Optional[Scalar]: ...


@dataclass(frozen=True)
class Parameter:
    """One owned input or calculation, with no cached calculated value.

    A literal value and an expression are mutually exclusive. Native expression
    functions are trusted Python and execute only during explicit evaluation.
    Units are labels. Unit conversion belongs in the calculation.
    """

    name: str
    value_type: Type = float
    unit: str = ""
    value: Optional[Scalar] = None
    expression: Optional[Expression] = None

    def __post_init__(self) -> None:
        _parameter_name(self.name)
        if self.value_type not in (float, int, bool, str):
            raise TypeError("Parameter types are float, int, bool and str.")
        _text(self.unit, "Parameter unit")
        if self.value is not None and self.expression is not None:
            raise ValueError(f"{self.name}: choose a literal value or an expression.")
        if self.value is not None:
            self.validate_value(self.value)
        if self.expression is not None:
            validate_expression(self.expression)

    def validate_value(self, value: Scalar) -> None:
        if self.value_type is float:
            valid = type(value) in (float, int)
        else:
            valid = type(value) is self.value_type
        if not valid:
            raise TypeError(f"{self.name}: expected {self.value_type.__name__}.")
        if self.value_type in (float, int):
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError(f"{self.name}: provide a finite number.")


class Statement:
    """A populated domain statement that can be specialized through inheritance.

    Parameters belong to this instance. Relationships point to domain objects,
    so renaming a referenced object preserves the relationship. Configuration
    contains no mutable verification flag or calculated result cache.
    """

    _requires_parameters = False
    statement_kind = "Need"

    def __init__(
        self,
        id: str,
        text: str,
        *,
        parameters: Iterable[Parameter] = (),
        verifications: Iterable[VerificationMethod] = (),
        owner: Optional[Identified] = None,
        sources: Iterable[Identified] = (),
        affected: Iterable[Identified] = (),
        name: str = "",
        rationale: str = "",
        origin: str = "",
        definition: str = "",
        key: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> None:
        self._session = None
        self.kind = self.statement_kind if kind is None else kind
        if self.kind not in (
            "Requirement",
            "Need",
            "Objective",
            "Concern",
            "Constraint",
        ):
            raise ValueError("Choose a supported statement kind.")
        if self._requires_parameters and self.kind != "Requirement":
            raise ValueError("Requirement instances have kind Requirement.")
        self.power_scope = None
        self.budget_scope = None
        self.subject = None
        self._projection_fields = frozenset()
        self._verification_style = "auto"
        self._key = _text(
            str(uuid4()) if key is None else key, "Requirement key", required=True
        )
        self.id = id
        self.name = _text(name, "Requirement name")
        self.rationale = _text(rationale, "Rationale")
        self.origin = _text(origin, "Provenance")
        self.definition = _text(definition, "Definition identifier")
        self._parameters: Dict[str, Parameter] = {}
        self._verifications: Tuple[VerificationMethod, ...] = ()
        self._sources: Tuple[Identified, ...] = ()
        self._affected: Tuple[Identified, ...] = ()
        self._owner: Optional[Identified] = None
        for parameter in parameters:
            self.add_parameter(parameter)
        self.text = text
        self.owner = owner
        self.derive_from(*sources)
        self.assign_to(*affected)
        for method in verifications:
            self.add_verification(method)

    @classmethod
    def restore(cls, id, text, *, template=None, **configuration):
        """Restore populated fields without rerunning a subclass's defaults.

        Specialized classes can override this hook for additional declared state.
        Normal construction remains the path for adding new requirements.
        """
        value = cls.__new__(cls)
        Statement.__init__(value, id, text, **configuration)
        if template is not None:
            value.template = template
        return value

    @property
    def key(self) -> str:
        return self._key

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        value = _text(value, "Statement ID", required=True)
        if self._session is not None and getattr(self, "_id", value) != value:
            self._session.rename(self, value)
        else:
            self._id = value

    @property
    def session(self):
        return self._session

    def _mark_changed(self):
        if self._session is not None:
            self._session._model_state_present = True

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        text = _text(value, "Requirement text", required=True)
        segments = text.split("$$")
        if len(segments) % 2 == 0:
            raise ValueError("Close each parameter marker with $$.")
        names = tuple(dict.fromkeys(name.strip() for name in segments[1::2]))
        additions = [Parameter(name) for name in names if name not in self._parameters]
        if self._requires_parameters and not self._parameters and not additions:
            raise ValueError("A requirement needs at least one declared parameter.")
        for parameter in additions:
            self.add_parameter(parameter)
        self._text = text
        self._mark_changed()

    @property
    def parameters(self) -> Mapping[str, Parameter]:
        return MappingProxyType(self._parameters)

    def add_parameter(self, parameter: Parameter) -> None:
        if not isinstance(parameter, Parameter):
            raise TypeError("Add a Parameter instance.")
        if parameter.name in self._parameters:
            raise ValueError(f"Parameter {parameter.name!r} is already declared.")
        self._parameters[parameter.name] = parameter
        if self._session is not None:
            self._session.register_parameter(parameter)
        self._mark_changed()

    def set_value(self, name: str, value: Optional[Scalar]) -> None:
        parameter = replace(self._parameters[name], value=value, expression=None)
        if self._session is not None:
            self._session.validate_parameter_binding(self, parameter)
        self._parameters[name] = parameter
        self._mark_changed()

    def set_expression(self, name: str, expression: Optional[Expression]) -> None:
        parameter = replace(self._parameters[name], value=None, expression=expression)
        if self._session is not None:
            self._session.validate_parameter_binding(self, parameter)
        self._parameters[name] = parameter
        self._mark_changed()

    def set_unit(self, name: str, unit: str) -> None:
        self._parameters[name] = replace(self._parameters[name], unit=unit)
        self._mark_changed()

    @property
    def verifications(self) -> Tuple[VerificationMethod, ...]:
        return self._verifications

    @verifications.setter
    def verifications(self, methods: Iterable[VerificationMethod]) -> None:
        candidates = tuple(methods)
        keys, names = set(), set()
        for method in candidates:
            if not isinstance(method, VerificationMethod):
                raise TypeError("Add a VerificationMethod instance.")
            if method.key in keys or method.name in names:
                raise ValueError(
                    "Verification method keys and names must be unique within a requirement."
                )
            if method.source is not None and self._session is not None:
                self._session.get(method.source)
            keys.add(method.key)
            names.add(method.name)
        self._verifications = candidates
        self._mark_changed()

    def add_verification(self, method: VerificationMethod) -> None:
        self.verifications = (*self._verifications, method)

    @staticmethod
    def _references(references: Iterable[Identified]) -> Tuple[Identified, ...]:
        unique: Dict[str, Identified] = {}
        for reference in references:
            _text(
                getattr(reference, "key", None), "Referenced object key", required=True
            )
            _text(getattr(reference, "id", None), "Referenced object ID", required=True)
            if reference.key in unique and unique[reference.key] is not reference:
                raise ValueError("Distinct referenced objects cannot share a key.")
            unique[reference.key] = reference
        return tuple(unique.values())

    @property
    def owner(self) -> Optional[Identified]:
        return self._owner

    @owner.setter
    def owner(self, owner: Optional[Identified]) -> None:
        if owner is not None:
            self._references((owner,))
            if owner.key == self.key:
                raise ValueError("A requirement cannot own itself.")
            if self._session is not None:
                self._session.get(owner)
        self._owner = owner
        self._mark_changed()

    @property
    def sources(self) -> Tuple[Identified, ...]:
        return self._sources

    @sources.setter
    def sources(self, sources: Iterable[Identified]) -> None:
        candidates = self._references(sources)
        if self._session is not None:
            for candidate in candidates:
                self._session.get(candidate)
        stack = list(candidates)
        visited = set()
        while stack:
            source = stack.pop()
            if source.key == self.key:
                raise ValueError(
                    "Requirement source relationships cannot contain a cycle."
                )
            if source.key not in visited:
                visited.add(source.key)
                if isinstance(source, Statement):
                    stack.extend(source.sources)
        self._sources = candidates
        self._mark_changed()

    def derive_from(self, *sources: Identified) -> None:
        self.sources = (*self._sources, *sources)

    @property
    def affected(self) -> Tuple[Identified, ...]:
        return self._affected

    @affected.setter
    def affected(self, elements: Iterable[Identified]) -> None:
        candidates = self._references(elements)
        if self._session is not None:
            for candidate in candidates:
                self._session.get(candidate)
        self._affected = candidates
        self._mark_changed()

    def assign_to(self, *elements: Identified) -> None:
        self.affected = (*self._affected, *elements)

    def value(
        self,
        name: str,
        evaluator: Optional[ExpressionEvaluator] = None,
        *,
        mode=ALL_MODES,
        evidence=None,
    ):
        """Resolve locally or through the owning session's common context."""
        if self.session is not None and evaluator is None:
            return self.session.value(self, name, mode=mode, evidence=evidence)
        return _Values(self, evaluator)[name]

    def verify(
        self,
        evaluator: Optional[ExpressionEvaluator] = None,
        *,
        mode=ALL_MODES,
        evidence=None,
        source_ready=None,
    ) -> VerificationResult:
        """Assess conditions without mutating configuration or running scripts."""
        if self.session is not None and evaluator is None:
            return self.session.verify(
                self, mode=mode, evidence=evidence, source_ready=source_ready
            )
        values = _Values(self, evaluator)
        return VerificationResult(
            tuple(
                method.evaluate(values, values.expression, source_ready)
                for method in self._verifications
            )
        )

    def render_text(self, values: Optional[Mapping[str, Scalar]] = None) -> str:
        """Render values and unit labels without executing calculations."""
        supplied = {} if values is None else values
        segments = self.text.split("$$")
        for index in range(1, len(segments), 2):
            name = segments[index].strip()
            parameter = self._parameters[name]
            value = supplied.get(name, parameter.value)
            segments[index] = (
                name if value is None else f"{value} {parameter.unit}".rstrip()
            )
        return "".join(segments)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id!r}, key={self.key!r})"


class Requirement(Statement):
    """An engineering obligation with at least one declared parameter."""

    _requires_parameters = True
    statement_kind = "Requirement"


class _Values(Mapping[str, Scalar]):
    """Lazy, request-local resolution for native functions and source adapters."""

    def __init__(
        self, requirement: Requirement, evaluator: Optional[ExpressionEvaluator]
    ) -> None:
        self.requirement = requirement
        self.parameters = dict(requirement.parameters)
        self.evaluator = evaluator
        self.cache: Dict[str, Scalar] = {}
        self.active = set()

    def __iter__(self) -> Iterator[str]:
        return iter(self.parameters)

    def __len__(self) -> int:
        return len(self.parameters)

    def __getitem__(self, name: str) -> Scalar:
        if name in self.cache:
            return self.cache[name]
        parameter = self.parameters[name]
        if name in self.active:
            raise ValueError(
                f"Cyclic parameter dependency at {self.requirement.id}.{name}."
            )
        self.active.add(name)
        try:
            if isinstance(parameter.expression, DraftExpression):
                if not parameter.expression.source.strip():
                    raise PendingValue(f"{self.requirement.id}.{name} is unset.")
                raise ValueError(parameter.expression.error)
            if isinstance(parameter.expression, str):
                value = self.expression(parameter.expression)
            elif parameter.expression is not None:
                value = parameter.expression(self)
            else:
                value = parameter.value
            from .evaluation import coerce

            value = coerce(value, parameter.value_type, f"{self.requirement.id}.{name}")
            self.cache[name] = value
            return value
        finally:
            self.active.remove(name)

    def expression(self, source: str) -> Optional[Scalar]:
        if self.evaluator is None:
            raise PendingValue("Provide an evaluator for Python expression source.")
        return self.evaluator(source, self.requirement, self)
