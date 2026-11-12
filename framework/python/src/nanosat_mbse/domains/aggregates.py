"""Explicit, read-only budget views over live component inputs.

Views retain their scope objects. They contain no copied inputs or cached results.
The expression evaluator resolves only the declared scalar outputs below.
"""

from dataclasses import dataclass
from types import MappingProxyType

from ..core.configuration import LoadConnection
from ..core.elements import Component, Element
from ..core.identity import ALL_MODES
from ..core.requirements import Parameter
from ..core.expressions import finite_number
from ..core.verification import PendingValue
from .budgets import (
    RESOURCES, component_contribution, component_draw, in_roots, load_budget,
    load_for, power_allocation, power_limit_for, power_scopes,
    resource_limit_for, resource_scopes, spacecraft_components,
)


TOTALS = {
    "mass_kg": ("Total installed mass", "kg"),
    "volume_m3": ("Total installed volume", "m^3"),
    "draw_power_W": ("Total active power", "W"),
    "average_power_W": ("Total average power", "W"),
}


def _parameters(fields):
    return MappingProxyType({name: Parameter(name, unit=unit) for name, unit in fields.items()})


def _source(component, name):
    from ..core.session import expression_source

    parameter = component.parameters[name]
    unset = parameter.value is None and parameter.expression is None
    if name == "average_power_W" and parameter.expression == "draw_power_W":
        draw = component.parameters["draw_power_W"]
        unset = draw.value is None and draw.expression is None
    if unset:
        session = component.session
        row = power_limit_for(session, component) if name.endswith("power_W") else resource_limit_for(
            session, component, next(resource for resource in RESOURCES if resource.value == name)
        )
        old = None if row is None else row.parameters.get(name)
        if old is not None and old.expression != f"{component.id}.{name}":
            return f"Legacy requirement input: {row.id}.{name}"
    return "Python calculation" if callable(parameter.expression) else expression_source(parameter)


@dataclass(frozen=True)
class Budget:
    """A spacecraft scope's installed contributions, independent of its limits."""

    scope: Element
    parameters = _parameters({name: unit for name, (_, unit) in TOTALS.items()})

    @property
    def namespace(self):
        return f"{self.scope.id}.budget"

    def reference(self, name):
        if name not in self.parameters:
            raise ValueError(f"Unknown budget total {name!r}.")
        return f"{self.namespace}.{name}"

    def components(self, name):
        session = self.scope.session
        if name not in self.parameters:
            raise ValueError(f"Unknown budget total {name!r}.")
        if name in ("mass_kg", "volume_m3"):
            candidates = (scope.target for scope in resource_scopes(session) if scope.kind == "component")
        else:
            candidates = (element for element in spacecraft_components(session)
                          if load_for(session, element).accounting == "counted")
        return tuple(sorted((element for element in candidates
                             if self.scope is session.mission or in_roots(element, (self.scope,))),
                            key=lambda element: element.key))

    def resolve(self, context, row, name):
        context.session.get(self.scope)
        if name not in self.parameters:
            raise ValueError(f"Unknown budget total {name!r}.")
        if name.endswith("power_W") and not any(
            self.scope is context.session.mission or in_roots(element, (self.scope,))
            for element in spacecraft_components(context.session)
        ):
            raise PendingValue("Define the components for this power limit.")
        return finite_number(sum(component_contribution(context, component, name)
                                 for component in self.components(name)))

    def value(self, name, *, mode=ALL_MODES):
        """Evaluate through the same dependency guards and evidence as requirements."""
        return self.scope.session.value(self.scope, f"budget.{name}", mode=mode)

    def describe(self, name):
        return {
            "reference": self.reference(name),
            "label": f"{TOTALS[name][0]} · {self.scope.id}",
            "description": "Sum of installed component inputs. Each accounting boundary contributes once.",
            "scope": [self.scope.key],
            "sources": [
                {"key": component.key, "reference": f"{component.id}.{name}",
                 "label": component.name, "expression": _source(component, name)}
                for component in self.components(name)
            ],
        }


@dataclass(frozen=True)
class ConnectedLoadBudget:
    """An EPS connection with explicit bus and payload roots."""

    connection: LoadConnection
    parameters = _parameters({"sunlight_power_W": "W", "eclipse_power_W": "W"})

    @property
    def namespace(self):
        return f"{self.connection.eps.id}.load_budget"

    def reference(self, name):
        if name not in self.parameters:
            raise ValueError(f"Unknown connected budget input {name!r}.")
        return f"{self.namespace}.{name}"

    def resolve(self, context, row, name):
        owner = next((requirement for requirement in self.connection.eps.requirements
                      if requirement.definition == "FrameworkRequirements::LoadEnergy"), None)
        if owner is None:
            raise ValueError("This EPS needs a LoadEnergy requirement.")
        return load_budget(context, owner, name, connection=self.connection)

    def value(self, name, *, mode=ALL_MODES):
        eps = self.connection.eps
        return eps.session.value(eps, f"load_budget.{name}", mode=mode)

    def describe(self, name):
        period = "sunlight" if name == "sunlight_power_W" else "eclipse"
        link = self.connection
        session = link.eps.session
        components = sorted((component for component in spacecraft_components(session)
                             if in_roots(component, link.roots)
                             and load_for(session, component).accounting == "counted"),
                            key=lambda component: component.key)
        return {
            "reference": self.reference(name),
            "label": f"Average {period} demand · {link.eps.id}",
            "description": f"Component average power weighted by {period} mode shares over "
                           + ", ".join(root.id for root in link.roots) + ".",
            "scope": [root.key for root in link.roots],
            "sources": [
                {"key": component.key, "reference": f"{component.id}.average_power_W",
                 "label": component.name, "expression": _source(component, "average_power_W")}
                for component in components
            ],
            "modes": [{"name": mode.name, "share": getattr(mode, period)} for mode in session.power.modes],
        }


@dataclass(frozen=True)
class PowerProfile:
    """Compatibility view for explicitly configured component state profiles."""

    component: Component
    parameters = _parameters({"draw_power_W": "W", "average_power_W": "W"})

    @property
    def namespace(self):
        return f"{self.component.id}.power_profile"

    def resolve(self, context, row, name):
        load = load_for(context.session, self.component)
        if load.accounting != "counted":
            return 0.0
        return component_draw(load, context.mode, context=context, average=name == "average_power_W")


class LegacyPowerAllocation:
    """Read older expressions without embedding domain names in the evaluator."""

    parameters = _parameters({name: "Wh" if name == "energy_Wh" else "W" for name in (
        "allocated_power_W", "draw_power_W", "average_power_W", "energy_Wh",
    )})

    def resolve(self, context, row, name):
        return power_allocation(context, row, name)


class LegacyLoadBudget:
    parameters = ConnectedLoadBudget.parameters

    def resolve(self, context, row, name):
        return load_budget(context, row, name)


def budget_namespaces(session):
    """Compose trusted views. Their only state is the authoritative object graph."""
    scopes = power_scopes(session)
    targets = dict.fromkeys([scope.target for scope in scopes] + list(scopes[0].affected))
    views = [Budget(target) for target in targets]
    views.extend(ConnectedLoadBudget(link) for link in session.power.links)
    views.extend(PowerProfile(component) for component in spacecraft_components(session))
    return {**{view.namespace: view for view in views},
            "PowerAllocation": LegacyPowerAllocation(), "LoadBudget": LegacyLoadBudget()}


def calculated_parameters(session, row, *, namespaces=None):
    """Describe direct calculated bindings without evaluating any inputs."""
    namespaces = session.expression_namespaces() if namespaces is None else namespaces
    result = {}
    for name, parameter in row.parameters.items():
        link = row.linked_parameter(name)
        if link is not None:
            parameter = link[0].parameters[link[1]]
        source = parameter.expression
        if not isinstance(source, str):
            continue
        namespace, _, field = source.strip().rpartition(".")
        view = namespaces.get(namespace)
        if view is not None and field in view.parameters and hasattr(view, "describe"):
            result[name] = {**view.describe(field), "reference": source}
    return result
