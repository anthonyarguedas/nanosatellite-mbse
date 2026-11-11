"""Typed configuration objects for calculations and analysis script interfaces.

These objects hold bindings and relationships. They contain no execution output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Type, Union
from uuid import uuid4

from .elements import Component, Element
from .requirements import Parameter


@dataclass(frozen=True)
class Variable:
    """Legacy workbook display metadata, independent of owned parameters."""

    name: str
    value_type: Type = float
    unit: Optional[str] = None


@dataclass(eq=False)
class Mode:
    name: str
    sunlight: Optional[float] = None
    eclipse: Optional[float] = None
    key: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        from .expressions import finite_number

        if (
            not isinstance(self.name, str)
            or not self.name.strip()
            or len(self.name) > 80
        ):
            raise ValueError("Name the mode using 1 to 80 characters.")
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("A mode needs a stable key.")
        for value in (self.sunlight, self.eclipse):
            if value is not None and not 0 <= finite_number(value) <= 100:
                raise ValueError("Mode fractions must be between 0 and 100 percent.")


@dataclass(eq=False)
class ComponentState:
    name: str
    watts: Optional[Union[float, str]] = None
    basis: str = "estimated"
    source: str = ""
    conditions: str = ""
    key: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        from .expressions import finite_number

        if (
            not isinstance(self.name, str)
            or not self.name.strip()
            or len(self.name) > 80
        ):
            raise ValueError("Name the component state using 1 to 80 characters.")
        if isinstance(self.watts, str):
            from .predicates import validate_expression

            validate_expression(self.watts)
        elif self.watts is not None and finite_number(self.watts) < 0:
            raise ValueError("Component power draw must be nonnegative.")
        if self.basis not in ("estimated", "typical", "maximum", "measured"):
            raise ValueError("Choose a component power value meaning.")
        if not isinstance(self.source, str) or not isinstance(self.conditions, str):
            raise ValueError("State sources and conditions must be text.")
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("A component state needs a stable key.")


@dataclass(eq=False)
class LoadProfile:
    element: Component
    quantity: int = 1
    accounting: str = "counted"
    host: Optional[Component] = None
    rationale: str = ""
    states: Tuple[ComponentState, ...] = ()
    assignments: Dict[Mode, ComponentState] = field(default_factory=dict)
    # Independent component duty percentages within each spacecraft mode.
    # An omitted percentage preserves continuous operation (100%).
    duties: Dict[Mode, float] = field(default_factory=dict)


@dataclass(eq=False)
class LoadConnection:
    eps: Element
    roots: Tuple[Element, ...]
    previous: Dict[str, Parameter] = field(default_factory=dict)


@dataclass
class PowerModel:
    modes: list = field(default_factory=list)
    loads: list = field(default_factory=list)
    links: list = field(default_factory=list)

    def load_for(self, element):
        return next((load for load in self.loads if load.element is element), None)


@dataclass(frozen=True)
class ScriptPort:
    name: str
    value_type: Type = float
    unit: Optional[str] = None


class ScriptConfiguration(Element):
    """Typed analysis identity and bindings, specialized by VerificationScript.

    The configuration contains declared ports and inputs, with no output cache.
    """

    default_name = "Analysis"
    id_prefix = "SCR"
    role = "script"

    def __init__(
        self, id="", *, revision="", inputs=(), outputs=(), parameters=(), **kwargs
    ):
        super().__init__(id, **kwargs)
        self.revision = revision
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)
        self.parameters = {}
        for parameter in parameters:
            if not isinstance(parameter, Parameter):
                raise TypeError("Script bindings must be Parameter instances.")
            if parameter.name in self.parameters:
                raise ValueError("Script input names must be unique.")
            self.parameters[parameter.name] = parameter
        declared = {port.name for port in self.inputs}
        if set(self.parameters) - declared:
            raise ValueError("Script bindings must name declared inputs.")
        for port in self.inputs:
            if port.name not in self.parameters:
                self.parameters[port.name] = Parameter(
                    port.name, port.value_type, port.unit or ""
                )

    @classmethod
    def restore(cls, id="", **configuration):
        """Restore declared ports and bindings without changing their revisions."""
        value = cls.__new__(cls)
        ScriptConfiguration.__init__(value, id, **configuration)
        return value

    def initialize(self, session):
        pass

    def run(self, context=None):
        raise NotImplementedError(
            "Use a concrete VerificationScript subclass for explicit execution."
        )
