"""Distinct modes, electrical states and explicit allocation records.

Allocation normalization, averaging and chronology are intentionally unspecified.
"""

from .objects import ModelObject
from .properties import Property


class TimeAllocation(ModelObject):
    fraction = Property(unit="1")

    def __init__(self, name, fraction=None):
        super().__init__(name, fraction=fraction)


class OrbitAllocation(TimeAllocation):
    def validate_attachment(self):
        if not isinstance(self.parent, SpacecraftMode):
            raise TypeError("An OrbitAllocation belongs to a SpacecraftMode.")


class ModeAllocation(TimeAllocation):
    def __init__(self, name, spacecraft_mode, fraction=None):
        if not isinstance(spacecraft_mode, SpacecraftMode):
            raise TypeError("A ModeAllocation references a SpacecraftMode.")
        super().__init__(name, fraction)
        self._spacecraft_mode = spacecraft_mode

    @property
    def spacecraft_mode(self):
        return self._spacecraft_mode

    def validate_attachment(self):
        if not isinstance(self.parent, ComponentMode):
            raise TypeError("A ModeAllocation belongs to a ComponentMode.")
        if self.mission is not None:
            component = self.parent.parent
            if self.spacecraft_mode not in component.spacecraft_modes:
                raise ValueError("Allocate a mode from the component's own Space Segment.")


class StateAllocation(TimeAllocation):
    def __init__(self, name, state, fraction=None):
        if not isinstance(state, ComponentState):
            raise TypeError("A StateAllocation references a ComponentState.")
        super().__init__(name, fraction)
        self._state = state

    @property
    def state(self):
        return self._state

    def validate_attachment(self):
        if not isinstance(self.parent, ComponentMode) or self.state.parent is not self.parent:
            raise ValueError("Allocate a state from this ComponentMode.")


class SpacecraftMode(ModelObject):
    child_aliases = {"allocation": OrbitAllocation}

    def accepts(self, child):
        return isinstance(child, OrbitAllocation) and self.allocation is None

    @property
    def allocation(self):
        return next((child for child in self.children if isinstance(child, OrbitAllocation)), None)

    def create_defaults(self):
        if self.allocation is None:
            self.add(OrbitAllocation("allocation"))


class ComponentState(ModelObject):
    voltage = Property(unit="V")
    current = Property(unit="A")
    power = Property("self.voltage.value * self.current.value", "W")


class ComponentMode(ModelObject):
    @property
    def states(self):
        return tuple(child for child in self.children if isinstance(child, ComponentState))

    @property
    def allocations(self):
        return tuple(child for child in self.children if isinstance(child, ModeAllocation))

    @property
    def state_allocations(self):
        return tuple(child for child in self.children if isinstance(child, StateAllocation))

    def accepts(self, child):
        return isinstance(child, (ComponentState, ModeAllocation, StateAllocation))

    def create_defaults(self):
        for name in ("on", "off"):
            if not any(child.name == name for child in self.children):
                self.add(ComponentState(name))
