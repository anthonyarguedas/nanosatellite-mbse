"""Native domain identities, containment and lifecycle hooks."""

from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType
from typing import Optional
from uuid import uuid4

from .identity import ALL_MODES
from .requirements import Parameter, Requirement, _text
from .properties import PropertyOwner


class Element(PropertyOwner):
    model = ""
    default_name = "Element"
    id_prefix = "ELM"
    role = "element"
    expandable = False
    catalog_selection = False

    def __init__(
        self,
        id: str = "",
        *,
        name: Optional[str] = None,
        key: Optional[str] = None,
        owner=None,
        definition: Optional[str] = None,
        selection: Optional[bool] = None,
        requirement_links=(),
        quantity=1,
        **kwargs,
    ):
        self._session = None
        self._key = _text(
            str(uuid4()) if key is None else key, "Element key", required=True
        )
        self._id = _text(id, "Element ID")
        self.name = _text(self.default_name if name is None else name, "Element name")
        self.definition = _text(
            self.model if definition is None else definition, "Element definition"
        )
        self._owner = None
        self.owner = owner
        self.selection = self.catalog_selection if selection is None else selection
        self.requirement_links = requirement_links
        self.quantity = quantity
        self._projection_fields = frozenset()
        super().__init__(**kwargs)

    @classmethod
    def restore(cls, id="", *, stakeholder_type=None, **configuration):
        """Restore identity and fields without calling custom creation hooks."""
        value = cls.__new__(cls)
        if stakeholder_type is not None:
            value.stakeholder_type = stakeholder_type
        Element.__init__(value, id, **configuration)
        return value

    @property
    def key(self):
        return self._key

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        value = _text(value, "Element ID", required=True)
        if self._session is not None and self._id != value:
            self._session.rename(self, value)
        else:
            self._id = value

    @property
    def session(self):
        return self._session

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        if owner is not None and not isinstance(owner, Element):
            raise TypeError("An element owner must be an Element instance.")
        seen = {self.key}
        current = owner
        while current is not None:
            if current.key in seen:
                raise ValueError("Element containment cannot contain a cycle.")
            seen.add(current.key)
            current = current.owner
        if (
            self._session is not None
            and owner is not None
            and owner.session is not self._session
        ):
            raise ValueError(
                "An attached element's owner must belong to the same session."
            )
        self._owner = owner

    @property
    def quantity(self):
        """Number of represented units for assignment property sums."""
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if type(value) is not int or not 1 <= value <= 9007199254740991:
            raise ValueError("Component quantity must be a positive safe integer.")
        self._quantity = value
        if self.session is not None:
            self.session._model_state_present = True

    @property
    def requirement_links(self):
        """The authoritative verification assignments, independent of affected scope."""
        return self._requirement_links

    @requirement_links.setter
    def requirement_links(self, requirements):
        unique = {}
        for requirement in requirements:
            if not isinstance(requirement, Requirement):
                raise TypeError("Component assignments must reference Requirement instances.")
            if requirement.key in unique and unique[requirement.key] is not requirement:
                raise ValueError("Distinct assigned requirements cannot share a key.")
            if self.session is not None:
                self.session.get(requirement)
            unique[requirement.key] = requirement
        self._requirement_links = tuple(unique.values())
        if self.session is not None:
            self.session._model_state_present = True

    def assign_to(self, *requirements):
        self.requirement_links = (*self.requirement_links, *requirements)
        return self

    @property
    def children(self):
        if self.session is None:
            return ()
        return tuple(
            element for element in self.session.all_elements if element.owner is self
        )

    @property
    def requirements(self):
        if self.session is None:
            return ()
        return tuple(
            requirement
            for requirement in self.session.requirements
            if requirement.owner is self
        )

    def initialize(self, session):
        """Create defaults on an explicit add, never during restoration."""
        if self.expandable:
            session.initialize_children(self)
        session.seed_requirements(self)

    def on_added(self, session):
        """Extension point after defaults have been created."""

    def add(self, element, *, initialize=True):
        if self.session is None:
            raise ValueError("Add the parent to a Session before adding children.")
        return self.session.add(element, owner=self, initialize=initialize)

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id!r}, key={self.key!r})"


class Subsystem(Element):
    default_name = "Subsystem"
    role = "subsystem"
    expandable = True

    @property
    def components(self):
        return tuple(child for child in self.children if isinstance(child, Component))

    def add_component(self, component, *, initialize=True):
        if not isinstance(component, Component):
            raise TypeError("A subsystem component must inherit Component.")
        return self.add(component, initialize=initialize)

    def component_added(self, component, session):
        """A specialized subsystem can react to a new component."""


class Component(Element):
    default_name = "Component"
    role = "component"
    default_accounting = "counted"
    budget_units = {
        "mass_kg": "kg",
        "volume_m3": "m^3",
        "draw_power_W": "W",
        "average_power_W": "W",
    }

    def __init__(self, *args, budget_parameters=(), **kwargs):
        self._initialize_budget(budget_parameters)
        super().__init__(*args, **kwargs)

    @classmethod
    def restore(cls, id="", *, budget_parameters=(), **configuration):
        value = super().restore(id, **configuration)
        value._initialize_budget(budget_parameters)
        return value

    def _initialize_budget(self, parameters):
        self._budget_parameters = {
            name: Parameter(name, unit=unit, expression="draw_power_W" if name == "average_power_W" else None)
            for name, unit in self.budget_units.items()
        }
        for parameter in parameters:
            self._configure_budget(parameter)

    @property
    def parameters(self):
        """Installed budget contributions, separate from product properties."""
        return MappingProxyType(self._budget_parameters)

    def validate_budget_parameter(self, parameter):
        if (
            not isinstance(parameter, Parameter)
            or parameter.name not in self.budget_units
            or parameter.value_type is not float
            or parameter.unit != self.budget_units[parameter.name]
        ):
            raise ValueError("Use a declared component budget parameter with its canonical type and unit.")
        if parameter.value is not None and parameter.value < 0:
            raise ValueError("Component budget contributions must be nonnegative.")

    def _configure_budget(self, parameter):
        self.validate_budget_parameter(parameter)
        self._budget_parameters[parameter.name] = parameter
        if getattr(self, "_session", None) is not None:
            self.session._model_state_present = True

    def set_value(self, name, value):
        parameter = replace(self.parameters[name], value=value, expression=None)
        if self.session is None:
            self._configure_budget(parameter)
        else:
            self.session.configure_parameter(self, parameter)

    def set_expression(self, name, expression):
        parameter = replace(self.parameters[name], value=None, expression=expression)
        if self.session is None:
            self._configure_budget(parameter)
        else:
            self.session.configure_parameter(self, parameter)

    def set_unit(self, name, unit):
        if unit != self.parameters[name].unit:
            raise ValueError("Component budget inputs retain their canonical units.")

    def value(self, name, *, mode=ALL_MODES):
        if self.session is None:
            raise ValueError("Attach the component to a session before evaluating its budget.")
        return self.session.value(self, name, mode=mode)

    def on_added(self, session):
        if isinstance(self.owner, Subsystem):
            self.owner.component_added(self, session)


class Stakeholder(Element):
    default_name = "Stakeholder"
    id_prefix = "STK"
    role = "stakeholder"

    def __init__(self, id="", *, stakeholder_type="Mission Stakeholder", **kwargs):
        self.stakeholder_type = stakeholder_type
        super().__init__(id, **kwargs)

    def initialize(self, session):
        pass
