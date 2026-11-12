"""Typed component contracts, independent of product databases and verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType

from .requirements import Parameter, _parameter_name
from .predicates import PendingValue


PROPERTY_TYPES = {}


def property_type(cls):
    """Register a trusted generic type for editable assignment expressions."""
    previous = PROPERTY_TYPES.get(cls.__name__)
    if previous is not None and previous is not cls:
        raise ValueError(f"The component type {cls.__name__!r} is already registered.")
    PROPERTY_TYPES[cls.__name__] = cls
    return cls


def resolve_property_type(value):
    if isinstance(value, str):
        try:
            return PROPERTY_TYPES[value]
        except KeyError:
            raise ValueError(f"Unknown component type {value!r}.") from None
    if not isinstance(value, type) or not issubclass(value, PropertyOwner):
        raise TypeError("Select a generic component type.")
    return value


@dataclass(frozen=True)
class ComponentProperty:
    """A scalar property in its canonical unit, inherited through normal Python MRO."""

    value_type: type = float
    unit: str = ""
    name: str = field(default="", init=False)

    def __set_name__(self, owner, name):
        _parameter_name(name)
        Parameter(name, self.value_type, self.unit)
        object.__setattr__(self, "name", name)

    def __get__(self, instance, owner=None):
        return self if instance is None else instance.property_value(self.name)

    def __set__(self, instance, value):
        instance.set_property(self.name, value)


class PropertyOwner:
    """Cooperative property storage, specialized by database adapters."""

    def __init__(self, *, property_values=None, **kwargs):
        self._property_values = {}
        for name, value in (property_values or {}).items():
            self.set_property(name, value)
        super().__init__(**kwargs)

    @classmethod
    def property_definitions(cls):
        definitions = {}
        for base in reversed(cls.__mro__):
            for name, value in vars(base).items():
                if isinstance(value, ComponentProperty):
                    previous = definitions.get(name)
                    if previous is not None and (
                        previous.value_type is not value.value_type
                        or previous.unit != value.unit
                    ):
                        raise TypeError(f"Conflicting inherited property {cls.__name__}.{name}.")
                    definitions[name] = value
        return MappingProxyType(definitions)

    @property
    def property_values(self):
        return MappingProxyType(self._property_values)

    def set_property(self, name, value):
        specification = self.property_definitions().get(name)
        if specification is None:
            raise ValueError(f"Unknown component property {name!r}.")
        parameter = Parameter(name, specification.value_type, specification.unit, value=value)
        if value is None:
            self._property_values.pop(name, None)
        else:
            self._property_values[name] = parameter.value
        if self.session is not None:
            self.session._model_state_present = True

    def property_value(self, name):
        if name not in self.property_definitions():
            raise ValueError(f"Unknown component property {name!r}.")
        if self.session is not None:
            return self.session.value(self, name)
        return self._property_value(name)

    def _property_value(self, name):
        value = self._property_values.get(name)
        if value is None:
            raise PendingValue(f"{self.id}.{name} is unset.")
        return value


# Conversion is deliberately bounded. Unlisted units must match exactly.
# Each entry is (dimension, scale to the base unit, offset in the base unit).
_UNITS = {
    "": ("ratio", 1, 0), "1": ("ratio", 1, 0), "%": ("ratio", .01, 0),
    "J": ("energy", 1, 0), "Wh": ("energy", 3600, 0), "mWh": ("energy", 3.6, 0),
    "W": ("power", 1, 0), "mW": ("power", .001, 0), "uW": ("power", .000001, 0),
    "V": ("voltage", 1, 0), "mV": ("voltage", .001, 0),
    "A": ("current", 1, 0), "mA": ("current", .001, 0), "uA": ("current", .000001, 0),
    "C": ("charge", 1, 0), "Ah": ("charge", 3600, 0), "mAh": ("charge", 3.6, 0),
    "s": ("time", 1, 0), "ms": ("time", .001, 0), "min": ("time", 60, 0), "h": ("time", 3600, 0),
    "K": ("temperature", 1, 0), "degC": ("temperature", 1, 273.15),
    "kg": ("mass", 1, 0), "g": ("mass", .001, 0),
    "m": ("length", 1, 0), "cm": ("length", .01, 0), "mm": ("length", .001, 0),
    "m2": ("area", 1, 0), "cm2": ("area", .0001, 0), "mm2": ("area", .000001, 0),
    "Hz": ("frequency", 1, 0), "kHz": ("frequency", 1000, 0), "MHz": ("frequency", 1000000, 0),
    "ohm": ("resistance", 1, 0), "kohm": ("resistance", 1000, 0),
}


def conversion(source, target, *, aggregate=False):
    """Return scale and offset, rejecting incompatible or offset-based sums."""
    if source == target:
        return 1, 0
    first, second = _UNITS.get(source), _UNITS.get(target)
    if first is None or second is None or first[0] != second[0]:
        raise ValueError(f"Cannot convert property unit {source!r} to target unit {target!r}.")
    scale, offset = first[1] / second[1], (first[2] - second[2]) / second[1]
    if aggregate and offset:
        raise ValueError("Quantity weighted sums require units without an offset conversion.")
    return scale, offset
