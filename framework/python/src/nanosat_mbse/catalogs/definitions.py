"""Immutable engineering definitions used to construct populated domain objects."""

from __future__ import annotations

import ast
import keyword
import re
from dataclasses import dataclass, field
from typing import Optional, Tuple

SCALAR_TYPES = {"float": "Real", "integer": "Integer", "boolean": "Boolean"}
PYTHON_TYPES = {"float": float, "integer": int, "boolean": bool, "string": str}


@dataclass(frozen=True)
class DefinitionParameter:
    name: str
    kind: str = "float"
    expression: Optional[str] = None
    unit: Optional[str] = None
    exposed: bool = True

    def validate(self):
        if (
            not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,39}", self.name)
            or keyword.iskeyword(self.name)
            or self.name.startswith("__")
            or self.kind not in SCALAR_TYPES
        ):
            raise ValueError(f"Invalid catalog parameter {self.name}.")
        if self.expression is not None:
            ast.parse(
                re.sub(
                    r"@([A-Za-z_][A-Za-z0-9_]*)\.", r"template_\1.", self.expression
                ),
                mode="eval",
            )
        if self.unit is not None and (
            not self.unit
            or len(self.unit) > 100
            or "\n" in self.unit
            or "\r" in self.unit
        ):
            raise ValueError(f"{self.name}: invalid display units.")


@dataclass(frozen=True)
class RequirementDefinition:
    name: str
    id: str
    context: str
    text: str
    origin: str
    affected: Tuple[str, ...]
    parameters: Tuple[DefinitionParameter, ...]
    condition: str
    acceptance: str
    derives_from: Tuple[str, ...] = ()
    parameter_order: Tuple[str, ...] = ()
    auto_populate: bool = False

    @property
    def model(self):
        return f"FrameworkRequirements::{self.name}"

    def validate(self):
        if type(self.auto_populate) is not bool:
            raise ValueError(f"{self.name}: invalid generic population flag.")
        if not re.fullmatch(r"[A-Z]{3}\d{3}", self.id) or self.context not in (
            "mission",
            "eps",
        ):
            raise ValueError(f"{self.name}: invalid identity or context.")
        names = [parameter.name for parameter in self.parameters]
        if len(set(names)) != len(names):
            raise ValueError(f"{self.name}: duplicate parameter names.")
        for parameter in self.parameters:
            parameter.validate()
        exposed = {parameter.name for parameter in self.parameters if parameter.exposed}
        marked = re.findall(r"\$\$([A-Za-z_][A-Za-z0-9_]*)\$\$", self.text)
        if not marked or not set(marked) <= exposed:
            raise ValueError(
                f"{self.name}: prose must reference declared numeric parameters."
            )
        if any(
            parameter.kind == "boolean" and parameter.exposed
            for parameter in self.parameters
        ):
            raise ValueError(f"{self.name}: exposed parameters must be numeric.")
        if self.parameter_order and (
            len(self.parameter_order) != len(exposed)
            or set(self.parameter_order) != exposed
        ):
            raise ValueError(f"{self.name}: invalid parameter display order.")
        for expression in (self.condition, self.acceptance):
            if expression:
                ast.parse(expression, mode="eval")
        if not self.acceptance:
            raise ValueError(
                f"{self.name}: retain the engineering acceptance predicate."
            )

    def projection(self):
        self.validate()
        parameters = [parameter for parameter in self.parameters if parameter.exposed]
        if self.parameter_order:
            by_name = {parameter.name: parameter for parameter in parameters}
            parameters = [by_name[name] for name in self.parameter_order]
        result = {
            "name": self.name,
            "model": self.model,
            "id": self.id,
            "context": self.context,
            "text": self.text,
            "origin": self.origin,
            "affected": list(self.affected),
            "parameters": {
                parameter.name: parameter.expression for parameter in parameters
            },
            "condition": self.condition,
            "attributes": {
                parameter.name: SCALAR_TYPES[parameter.kind]
                for parameter in self.parameters
            },
            "assessment": {
                "condition": self.acceptance,
                "inputs": [
                    {"name": parameter.name, "type": parameter.kind, "value": None}
                    for parameter in self.parameters
                    if not parameter.exposed
                ],
            },
        }
        units = {
            parameter.name: parameter.unit for parameter in parameters if parameter.unit
        }
        if units:
            result["units"] = units
        integers = [
            parameter.name for parameter in parameters if parameter.kind == "integer"
        ]
        if integers:
            result["integers"] = integers
        if self.derives_from:
            result["derivesFrom"] = list(self.derives_from)
        if self.auto_populate:
            result["autoPopulate"] = True
        return result

    def assess(self, values, evaluator=None):
        """Assess explicit evidence through the same native Requirement interface."""
        from ..core.requirements import Parameter, Requirement
        from ..core.verification import VerificationMethod

        from ..core.evaluation import coerce
        from ..core.session import Session
        from ..core.verification import PendingValue

        try:
            allowed = {parameter.name for parameter in self.parameters}
            if not isinstance(values, dict) or not set(values) <= allowed:
                raise ValueError(
                    "Assessment values must name declared parameters only."
                )
            parameters = []
            for parameter in self.parameters:
                value_type = PYTHON_TYPES[parameter.kind]
                value = values.get(parameter.name)
                parameters.append(
                    Parameter(
                        parameter.name,
                        value_type,
                        parameter.unit or "",
                        value=None
                        if value is None
                        else coerce(value, value_type, parameter.name),
                    )
                )
            requirement = Requirement(
                self.id,
                self.text,
                parameters=parameters,
                verifications=(
                    VerificationMethod("engineering acceptance", self.acceptance),
                ),
            )
            if evaluator is None:
                session = Session()
                session.add(requirement, owner=session.external, initialize=False)
            result = requirement.verify(evaluator)
            return {
                "state": result.state.value,
                "message": "\n".join(method.message for method in result.methods)
                or self.acceptance,
            }
        except Exception as error:
            return {
                "state": "pending" if isinstance(error, PendingValue) else "error",
                "message": str(error),
            }


@dataclass(frozen=True)
class ElementDefinition:
    model: str
    name: str
    category: str
    id: str
    parent: Optional[str] = None
    role: Optional[str] = None
    prefix: Optional[str] = None
    tab_label: Optional[str] = None
    expandable: bool = False
    properties: Tuple[DefinitionParameter, ...] = field(default_factory=tuple)
    auto_create: bool = True

    def __post_init__(self):
        if type(self.auto_create) is not bool:
            raise TypeError("Element default creation is a Boolean choice.")

    def projection(self):
        result = {
            "model": self.model,
            "name": self.name,
            "category": self.category,
            "id": self.id,
            "expandable": self.expandable,
        }
        for key, value in (
            ("parent", self.parent),
            ("role", self.role),
            ("prefix", self.prefix),
            ("tabLabel", self.tab_label),
        ):
            if value is not None:
                result[key] = value
        if not self.auto_create:
            result["autoCreate"] = False
        if self.properties:
            result["properties"] = [
                {
                    "name": parameter.name,
                    "type": parameter.kind,
                    "unit": parameter.unit,
                    "value": None,
                }
                for parameter in self.properties
            ]
        return result
