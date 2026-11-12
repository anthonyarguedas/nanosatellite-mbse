"""Expression bindings, descriptive units and evaluation without a value cache."""

from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
import math
from types import MappingProxyType


@dataclass(frozen=True)
class Unit:
    symbol: str = ""

    def __str__(self):
        return self.symbol


class EvaluationStatus(str, Enum):
    VALUE = "value"
    PENDING = "pending"
    ERROR = "error"


@dataclass(frozen=True)
class EvaluationResult:
    status: EvaluationStatus
    value: object = None
    message: str = ""


class PendingValue(ValueError):
    """A referenced property has no expression yet."""


_ACTIVE = ContextVar("model_evaluation", default=None)


def expression(source):
    """Accept one Python expression, including literal input conveniences."""
    if source is None:
        return None
    if type(source) in (bool, int, float):
        source = repr(source)
    if not isinstance(source, str) or "\n" in source or "\r" in source:
        raise ValueError("Supply a Python one-line expression.")
    compile(source, "<property>", "eval")
    return source


class EvaluationContext:
    """One evaluation's call stack and observed property dependencies."""

    def __init__(self, mission=None, mode=None):
        self.mission, self.mode = mission, mode
        self.stack = []
        self.dependencies = {}

    def __enter__(self):
        self._token = _ACTIVE.set(self)
        return self

    def __exit__(self, *_):
        _ACTIVE.reset(self._token)

    def execute(self, source, owner=None, **bindings):
        namespace = dict(self.mission.namespace) if self.mission else {"math": math}
        namespace.update(self=owner, mode=self.mode, **bindings)
        # Session code is trusted Python. There is deliberately no sandbox.
        return eval(compile(expression(source), "<expression>", "eval"), namespace)

    def read(self, prop):
        if self.stack:
            edges = self.dependencies.setdefault(self.stack[-1], [])
            if prop not in edges:
                edges.append(prop)
        if prop in self.stack:
            path = " -> ".join(item.reference for item in (*self.stack, prop))
            raise ValueError(f"Property dependency cycle: {path}")
        mission = prop.owner.mission if prop.owner is not None else None
        if self.mission is None:
            self.mission = mission
        elif prop.owner is not None and mission is not self.mission:
            raise ValueError(f"{prop.reference} belongs outside this Mission.")
        if self.mode is not None and self.mission is not None:
            if getattr(self.mode, "mission", None) is not self.mission:
                raise ValueError("The evaluation mode must belong to this Mission.")
        source = prop._modes.get(self.mode, prop.expression)
        if source is None:
            raise PendingValue(f"{prop.reference} is unset.")
        self.stack.append(prop)
        try:
            linked = prop._source if self.mode not in prop._modes else None
            value = self.read(linked) if linked is not None else self.execute(source, prop.owner)
            return self.read(value) if isinstance(value, Property) else value
        finally:
            self.stack.pop()

    def paths(self, root):
        """Return each observed path from a measure to its input properties."""
        def walk(path):
            for child in self.dependencies.get(path[-1], ()):
                if child not in path:
                    extended = (*path, child)
                    yield extended
                    yield from walk(extended)
        return tuple(walk((root,)))


class Property:
    """An expression and annotation. Read .value to evaluate it."""

    def __init__(self, source=None, unit=None):
        self.owner, self.name = None, ""
        self._frozen = False
        self._source = None
        self._modes = {}
        self.expression = source
        self.unit = unit

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        return self if instance is None else instance.properties[self.name]

    def __set__(self, instance, value):
        instance._set_property(self.name, value)

    def copy(self, owner, name, *, frozen=False):
        prop = Property(self.expression, self.unit)
        prop.owner, prop.name = owner, name
        prop._modes = dict(self._modes)
        prop._source = self._source
        prop._frozen = frozen
        return prop

    @classmethod
    def link(cls, source):
        prop = cls(unit=source.unit)
        prop._source = source
        return prop

    def _editable(self):
        if self._frozen:
            raise AttributeError(f"{self.reference} is fixed by its COTS class.")

    @property
    def expression(self):
        return self._source.reference if self._source is not None else self._expression

    @expression.setter
    def expression(self, source):
        self._editable()
        self._expression = expression(source)
        self._source = None

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._editable()
        if value is not None and not isinstance(value, (str, Unit)):
            raise TypeError("A unit is a Unit annotation or a string.")
        self._unit = value if isinstance(value, Unit) else Unit(value or "")

    @property
    def modes(self):
        return MappingProxyType(self._modes)

    def bind(self, mode, source):
        """Override this expression for an explicitly selected mode or state."""
        from .modes import ComponentMode, ComponentState, SpacecraftMode

        self._editable()
        if not isinstance(mode, (SpacecraftMode, ComponentMode, ComponentState)):
            raise TypeError("Choose a spacecraft mode, component mode or component state.")
        if self.owner is not None and self.owner.mission is not None:
            if mode.mission is not self.owner.mission:
                raise ValueError("The binding mode must belong to this Mission.")
        self._modes[mode] = expression(source)
        return self

    @property
    def reference(self):
        return f"{self.owner.path}.{self.name}" if self.owner is not None else "<property>"

    @property
    def value(self):
        return self.evaluate()

    def evaluate(self, *, mission=None, mode=None):
        active = _ACTIVE.get()
        if active is not None:
            if mission is not None and mission is not active.mission:
                raise ValueError("Nested evaluation uses the active Mission.")
            if mode is not None and mode is not active.mode:
                raise ValueError("Nested evaluation uses the active mode.")
            return active.read(self)
        with EvaluationContext(mission, mode) as context:
            return context.read(self)

    @property
    def verification(self):
        from .requirements import InstanceVerification

        mission = self.owner.mission if self.owner is not None else None
        return mission.verify().for_instance(self) if mission else InstanceVerification(self, ())

    @property
    def verified(self):
        return self.verification.verified

    def __repr__(self):
        return f"Property({self.reference!r}, expression={self.expression!r}, unit={str(self.unit)!r})"

    def assess(self, **options):
        try:
            return EvaluationResult(EvaluationStatus.VALUE, self.evaluate(**options))
        except PendingValue as error:
            return EvaluationResult(EvaluationStatus.PENDING, message=str(error))
        except Exception as error:
            return EvaluationResult(EvaluationStatus.ERROR, message=f"{type(error).__name__}: {error}")
