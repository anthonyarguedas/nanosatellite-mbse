"""Typed, request-local calculation models. Storage remains a separate adapter."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class Pending(ValueError):
    def __init__(self, message, script_key=None):
        super().__init__(message)
        self.script_key = script_key


def finite_number(value):
    if type(value) not in (int, float):
        raise ValueError("This operation requires numeric operands.")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError("Arithmetic must produce a finite number.")
    return value


def collection(value, maximum, label):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f"{label} must be a list with at most {maximum} entries.")
    return value


@dataclass(frozen=True)
class Parameter:
    name: str
    type: str = "float"
    unit: str = ""

    @classmethod
    def read(cls, data):
        if not isinstance(data, dict) or not isinstance(data.get("name"), str):
            raise ValueError("Each parameter needs a name.")
        name = data["name"]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,39}", name) or name.startswith("__"):
            raise ValueError("Invalid parameter name.")
        kind = data.get("type", "float")
        if kind not in ("float", "integer", "boolean"):
            raise ValueError(f"{name}: unsupported parameter type.")
        return cls(name, kind, data.get("unit", ""))


@dataclass
class Requirement:
    key: str
    id: str
    parameters: Dict[str, Optional[str]]
    methods: List[dict] = field(default_factory=list)
    definition: str = ""
    context: str = "external"
    scope: Optional[str] = None

    @classmethod
    def read(cls, data):
        if not isinstance(data, dict) or not isinstance(data.get("key"), str) or not isinstance(data.get("id"), str):
            raise ValueError("Every requirement needs a key and ID.")
        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict) or len(parameters) > 64:
            raise ValueError("Invalid requirement parameters.")
        methods = data.get("verifications")
        if methods is None:
            condition = data.get("condition", "")
            if not isinstance(condition, str):
                raise ValueError("Verification conditions must be expression text.")
            methods = [{"key": "condition", "condition": condition}] if condition.strip() else []
        collection(methods, 32, "Verification methods")
        for method in methods:
            if not isinstance(method, dict) or not isinstance(method.get("key"), str) or not isinstance(method.get("condition"), str):
                raise ValueError("Invalid verification method.")
        return cls(data["key"], data["id"], parameters, methods, data.get("definition", ""), data.get("context", "external"), data.get("powerScope"))


@dataclass
class Script:
    key: str
    id: str
    parameters: Dict[str, Optional[str]]
    inputs: List[Parameter]
    outputs: List[Parameter]
    revision: str

    @classmethod
    def read(cls, data):
        if not isinstance(data, dict) or not isinstance(data.get("key"), str) or not isinstance(data.get("id"), str):
            raise ValueError("Every script needs a key and ID.")
        inputs = [Parameter.read(item) for item in collection(data.get("inputs", []), 32, "Script inputs")]
        outputs = [Parameter.read(item) for item in collection(data.get("outputs", []), 32, "Script outputs")]
        parameters = data.get("parameters", {})
        if not isinstance(parameters, dict) or len(parameters) > 32:
            raise ValueError("Invalid script inputs.")
        return cls(data["key"], data["id"], parameters, inputs, outputs, data.get("revision", ""))


@dataclass
class Workspace:
    variables: List[Parameter]
    requirements: List[Requirement]
    scripts: List[Script]
    elements: List[dict]
    power: dict
    runs: dict = field(default_factory=dict)
    language: str = 'python'

    @classmethod
    def read(cls, data, runs=None):
        if not isinstance(data, dict):
            raise ValueError("A calculation request needs a workspace object.")
        variables = [Parameter.read(item) for item in collection(data.get("variables"), 64, "Variables")]
        requirements = [Requirement.read(item) for item in collection(data.get("statements"), 10000, "Requirements")]
        scripts = [Script.read(item) for item in collection(data.get("scripts", []), 64, "Scripts")]
        elements = collection(data.get("elements", []), 10000, "Elements")
        power = data.get("power") or {"modes": [], "loads": [], "links": []}
        if not isinstance(power, dict):
            raise ValueError("Invalid power model.")
        collection(power.get("modes", []), 24, "Spacecraft modes")
        collection(power.get("loads", []), 1000, "Power loads")
        collection(power.get("links", []), 1000, "Power connections")
        ids = [row.id for row in requirements + scripts]
        keys = [row.key for row in requirements + scripts]
        if len(set(ids)) != len(ids) or len(set(keys)) != len(keys):
            raise ValueError("Calculation row keys and IDs must be unique.")
        if len({variable.name for variable in variables}) != len(variables):
            raise ValueError("Calculation parameter names must be unique.")
        if data.get('expressionLanguage', 'python') != 'python':
            raise ValueError('Only Python expressions are supported.')
        return cls(variables, requirements, scripts, elements, power, runs or {})

    @property
    def modes(self):
        return self.power.get("modes", [])

    def load(self, element):
        existing = next((load for load in self.power.get("loads", []) if load["element"] == element["key"]), None)
        if existing:
            return existing
        definition = element.get("definition", "")
        excluded = re.search(r"::(StaticMount|ThermalSink|PropellantStorage|Batteries|SolarArrays)$", definition)
        return {"quantity": 1, "accounting": "host" if definition.endswith("::Software") else "excluded" if excluded else "counted", "states": [], "assignments": {}}

    @property
    def components(self):
        return [row for row in self.elements if row.get("id") and re.fullmatch(r"SpaceSegment::CubeSat::[^:]+::[^:]+", row.get("definition", ""))]

    def in_roots(self, element, roots):
        elements = {row["key"]: row for row in self.elements}
        seen = set()
        while element and element["key"] not in seen:
            if element["key"] in roots:
                return True
            seen.add(element["key"])
            element = elements.get(element.get("owner"))
        return False

    def power_limit(self, scope):
        return next((row for row in self.requirements if row.scope == scope and row.definition in ("PowerBudgetModel::PowerLimit", "PowerBudgetModel::ComponentPowerLimit")), None)

    def allocation(self, row, name, resolve, mode):
        if row.definition not in ("PowerBudgetModel::PowerLimit", "PowerBudgetModel::ComponentPowerLimit"):
            raise ValueError("PowerAllocation belongs to a power limit requirement.")
        subsystems = [element for element in self.elements if element.get("id") and re.fullmatch(r"SpaceSegment::CubeSat::[^:]*Subsystem", element.get("definition", ""))]
        children = [element for element in subsystems if row.scope == "mission"]
        children += [element for element in self.components if element.get("owner") == row.scope and (self.load(element)["accounting"] == "counted" or self.power_limit(element["key"]))]
        if name == "allocated_power_W" or children:
            total = 0
            for child in children:
                requirement = self.power_limit(child["key"])
                if requirement is None:
                    raise Pending(f"Define a power limit for {child['id']}.")
                value = resolve(requirement, "power_limit_W" if name == "allocated_power_W" else "draw_power_W")
                if value < 0:
                    raise ValueError(f"{requirement.id} power must be nonnegative.")
                total += value
            return finite_number(total)
        components = [element for element in self.components if row.scope == "mission" or self.in_roots(element, [row.scope])]
        if not components:
            raise Pending("Define the components for this power limit.")
        total = 0
        for element in components:
            load = self.load(element)
            if load["accounting"] != "counted":
                continue
            if mode is None:
                raise Pending("Select a spacecraft mode to calculate power draw.")
            state = next((state for state in load["states"] if state["key"] == load["assignments"].get(mode)), None)
            if not state or state.get("watts") is None:
                raise Pending(f"Select a state and power draw for {element['id']}.")
            total += finite_number(load["quantity"]) * finite_number(state["watts"])
        return finite_number(total)

    def budget(self, row, name):
        link = next((link for link in self.power.get("links", []) if link["eps"] == row.context), None)
        if link is None:
            raise ValueError("Connect this EPS to a load budget before using LoadBudget inputs.")
        period = "sunlight" if name == "sunlight_power_W" else "eclipse"
        weights = [mode.get(period) for mode in self.modes]
        if not weights or any(weight is None for weight in weights) or abs(sum(weights) - 100) > 1e-6:
            raise Pending(f"{period.capitalize()} mode fractions must total 100%.")
        components = [element for element in self.components if self.in_roots(element, link["roots"])]
        if not components:
            raise Pending("The selected scope has no spacecraft components.")
        total = 0
        for mode in self.modes:
            if mode[period] == 0:
                continue
            for element in components:
                load = self.load(element)
                if load["accounting"] != "counted":
                    continue
                state = next((state for state in load["states"] if state["key"] == load["assignments"].get(mode["key"])), None)
                if not state or state.get("watts") is None:
                    raise Pending(f"{mode['name']}: define a state and power for {element['id']}.")
                total += finite_number(load["quantity"]) * finite_number(state["watts"]) * finite_number(mode[period]) / 100
        return finite_number(total)
