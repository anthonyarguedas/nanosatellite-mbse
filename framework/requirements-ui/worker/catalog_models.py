"""Python definitions for the workbook's reusable engineering model."""
from __future__ import annotations

import ast
import keyword
from dataclasses import dataclass, field
import re
from typing import Optional, Tuple


SCALAR_TYPES = {"float": "Real", "integer": "Integer", "boolean": "Boolean"}


@dataclass(frozen=True)
class DefinitionParameter:
    name: str
    kind: str = "float"
    expression: Optional[str] = None
    unit: Optional[str] = None
    exposed: bool = True

    def validate(self):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,39}", self.name) or keyword.iskeyword(self.name) or self.name.startswith('__') or self.kind not in SCALAR_TYPES:
            raise ValueError(f"Invalid catalog parameter {self.name}.")
        if self.expression is not None:
            if not isinstance(self.expression, str):
                raise ValueError(f"{self.name}: expressions must be Python text or None.")
            ast.parse(re.sub(r"@([A-Za-z_][A-Za-z0-9_]*)\.", r"template_\1.", self.expression), mode="eval")
        if self.unit is not None and (not isinstance(self.unit, str) or not self.unit or len(self.unit) > 100 or '\n' in self.unit or '\r' in self.unit):
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
        # These are stable data identifiers retained for existing mission links.
        return f"FrameworkRequirements::{self.name}"

    def validate(self):
        if type(self.auto_populate) is not bool:
            raise ValueError(f'{self.name}: invalid generic population flag.')
        if not re.fullmatch(r"[A-Z]{3}\d{3}", self.id) or self.context not in ("mission", "eps"):
            raise ValueError(f"{self.name}: invalid requirement identity or context.")
        names = [parameter.name for parameter in self.parameters]
        if len(set(names)) != len(names):
            raise ValueError(f"{self.name}: duplicate parameter names.")
        for parameter in self.parameters:
            parameter.validate()
        marked = re.findall(r"\$\$([A-Za-z_][A-Za-z0-9_]*)\$\$", self.text)
        exposed = {parameter.name for parameter in self.parameters if parameter.exposed}
        if any(parameter.kind == 'boolean' for parameter in self.parameters if parameter.exposed):
            raise ValueError(f'{self.name}: exposed requirement parameters must be numeric.')
        if self.parameter_order and (len(self.parameter_order) != len(exposed) or set(self.parameter_order) != exposed):
            raise ValueError(f'{self.name}: invalid parameter display order.')
        if not marked or not set(marked) <= exposed:
            raise ValueError(f"{self.name}: prose must reference declared numeric parameters.")
        for expression in (self.condition, self.acceptance):
            if expression:
                ast.parse(expression, mode="eval")
        if not self.acceptance:
            raise ValueError(f"{self.name}: retain the engineering acceptance predicate.")

    def assess(self, values):
        """Assess the retained engineering predicate with explicit input values.

        Unprovided evidence stays unbound. This is separate from the engineer's
        editable verification method table and never supplies default evidence.
        """
        from expressions import Evaluator
        from models import Parameter, Pending, Requirement, Workspace, finite_number
        try:
            allowed = {parameter.name for parameter in self.parameters}
            if not isinstance(values, dict) or not set(values) <= allowed:
                raise ValueError('Assessment values must name declared parameters only.')
            expressions = {}
            for parameter in self.parameters:
                value = values.get(parameter.name)
                if value is not None:
                    if parameter.kind == 'boolean':
                        if type(value) is not bool:
                            raise ValueError(f'{parameter.name}: provide a Boolean assessment value.')
                    else:
                        finite_number(value)
                        if parameter.kind == 'integer' and (int(value) != value or abs(value) > 9007199254740991):
                            raise ValueError(f'{parameter.name}: provide a safe Integer assessment value.')
                expressions[parameter.name] = None if value is None else repr(value)
            row = Requirement(self.name, self.id, expressions)
            workspace = Workspace([Parameter(parameter.name, parameter.kind) for parameter in self.parameters], [row], [], [], {}, language='python')
            value = Evaluator(workspace).expression(self.acceptance, row)
            return {'state': 'pass' if value else 'fail', 'message': self.acceptance}
        except (ValueError, ArithmeticError, TypeError) as error:
            return {'state': 'pending' if isinstance(error, Pending) else 'error', 'message': str(error)}

    def projection(self):
        self.validate()
        parameters = [parameter for parameter in self.parameters if parameter.exposed]
        if self.parameter_order:
            by_name = {parameter.name: parameter for parameter in parameters}
            parameters = [by_name[name] for name in self.parameter_order]
        result = {"name": self.name, "model": self.model, "id": self.id, "context": self.context,
                  "text": self.text, "origin": self.origin, "affected": list(self.affected),
                  "parameters": {parameter.name: parameter.expression for parameter in parameters},
                  "condition": self.condition,
                  "attributes": {parameter.name: SCALAR_TYPES[parameter.kind] for parameter in self.parameters},
                  "assessment": {"condition": self.acceptance,
                                 "inputs": [{"name": parameter.name, "type": parameter.kind, "value": None}
                                            for parameter in self.parameters if not parameter.exposed]}}
        units = {parameter.name: parameter.unit for parameter in parameters if parameter.unit}
        if units:
            result["units"] = units
        integers = [parameter.name for parameter in parameters if parameter.kind == "integer"]
        if integers:
            result["integers"] = integers
        if self.derives_from:
            result["derivesFrom"] = list(self.derives_from)
        if self.auto_populate:
            result["autoPopulate"] = True
        return result


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

    def projection(self):
        result = {"model": self.model, "name": self.name, "category": self.category,
                  "id": self.id, "expandable": self.expandable}
        for key, value in (("parent", self.parent), ("role", self.role), ("prefix", self.prefix), ("tabLabel", self.tab_label)):
            if value is not None:
                result[key] = value
        if self.properties:
            result["properties"] = [{"name": parameter.name, "type": parameter.kind, "unit": parameter.unit, "value": None}
                                    for parameter in self.properties]
        return result
