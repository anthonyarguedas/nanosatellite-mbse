"""Domain containment and class-defined cumulative property patterns."""

from .modes import ComponentMode, SpacecraftMode
from .objects import ModelObject
from .properties import Property


class DomainElement(ModelObject):
    @property
    def subsystems(self):
        return tuple(child for child in self.children if isinstance(child, Subsystem))

    def accepts(self, child):
        return isinstance(child, Subsystem)


class SpaceSegment(DomainElement):
    default_subsystems = ()
    cost = Property("sum(child.cost.value for child in self.subsystems)", "currency")
    mass = Property("sum(child.mass.value for child in self.subsystems)", "kg")
    volume = Property("sum(child.volume.value for child in self.subsystems)", "m3")
    power = Property("sum(child.power.value for child in self.subsystems)", "W")

    @property
    def modes(self):
        return tuple(child for child in self.children if isinstance(child, SpacecraftMode))

    def accepts(self, child):
        return super().accepts(child) or isinstance(child, SpacecraftMode)

    def create_defaults(self):
        for cls in self.default_subsystems:
            if not any(child.name == cls.__name__ for child in self.children):
                self.add(cls(cls.__name__))


class GroundSegment(DomainElement):
    pass


class Subsystem(ModelObject):
    default_components = ()
    cost = Property("sum(child.cost.value for child in self.components)", "currency")
    mass = Property("sum(child.mass.value for child in self.components)", "kg")
    volume = Property("sum(child.volume.value for child in self.components)", "m3")
    power = Property("sum(child.power.value for child in self.components)", "W")

    @property
    def components(self):
        return tuple(child for child in self.children if isinstance(child, Component))

    @property
    def modes(self):
        return getattr(self.parent, "modes", ())

    def accepts(self, child):
        return isinstance(child, Component) and (
            type(child) is Component
            or child.subsystem_type is not None and isinstance(self, child.subsystem_type)
        )

    def create_defaults(self):
        for cls in self.default_components:
            if not any(child.name == cls.__name__ for child in self.children):
                self.add(cls(cls.__name__))


class Component(ModelObject):
    subsystem_type = None
    cost = Property(unit="currency")
    mass = Property(unit="kg")
    volume = Property(unit="m3")
    power = Property(unit="W")

    @property
    def modes(self):
        return tuple(child for child in self.children if isinstance(child, ComponentMode))

    @property
    def spacecraft_modes(self):
        parent = self.parent
        while parent is not None:
            if isinstance(parent, SpaceSegment):
                return parent.modes
            parent = parent.parent
        return ()

    @property
    def cots(self):
        return tuple(child for child in self.children if isinstance(child, Component) and child.fixed_properties)

    def accepts(self, child):
        if isinstance(child, ComponentMode):
            return True
        return isinstance(child, Component) and child.fixed_properties and isinstance(child, type(self))


class Orbit(ModelObject):
    altitude = Property(unit="km")
    beta_angle = Property(unit="deg")
    eccentricity = Property(unit="1")
