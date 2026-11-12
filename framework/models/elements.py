"""Domain containment and class-defined cumulative property patterns."""

from .modes import ComponentMode, SpacecraftMode
from .objects import ModelObject
from .properties import Property
from .requirements import Requirement


class DomainElement(ModelObject):
    @property
    def subsystems(self):
        return tuple(child for child in self.children if isinstance(child, Subsystem))

    def accepts(self, child):
        return isinstance(child, (Subsystem, Requirement))


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
        return isinstance(child, Requirement) or isinstance(child, Component) and (
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
    def spacecraft(self):
        parent = self.parent
        while parent is not None and not isinstance(parent, SpaceSegment):
            parent = parent.parent
        return parent

    @property
    def spacecraft_modes(self):
        return self.spacecraft.modes if self.spacecraft is not None else ()

    @property
    def cots(self):
        return tuple(child for child in self.children if isinstance(child, Component) and child.fixed_properties)

    def accepts(self, child):
        if isinstance(child, (ComponentMode, Requirement)):
            return True
        return isinstance(child, Component) and child.fixed_properties and isinstance(child, type(self))


class Orbit(ModelObject):
    altitude = Property(unit="km")
    beta_angle = Property(unit="deg")
    eccentricity = Property(unit="1")
    earth_radius = Property("6378", "km")
    gravitational_parameter = Property("398601", "km3/s2")
    semimajor_axis = Property("self.earth_radius.value + self.altitude.value", "km")
    sun_projection_angle = Property(unit="deg")
    effective_sun_projection_angle = Property(
        "0 if self.eccentricity.value == 0 or abs(self.beta_angle.value) == 90 else self.sun_projection_angle", "deg")
    perigee_altitude = Property("self.semimajor_axis.value * (1 - self.eccentricity.value) - self.earth_radius.value", "km")
    period = Property(
        "sizing.orbit_period(semimajor_axis=self.semimajor_axis, eccentricity=self.eccentricity, "
        "earth_radius=self.earth_radius, gravitational_parameter=self.gravitational_parameter).seconds", "s",
    )
    mean_motion = Property("2 * math.pi / self.period.value", "rad/s")
    orbits_per_day = Property("86400 / self.period.value", "orbit/day")
    eclipse_duration = Property(
        "sizing.circular_illumination(semimajor_axis=self.semimajor_axis, earth_radius=self.earth_radius, "
        "beta_angle=self.beta_angle, period=self.period).eclipse "
        "if self.eccentricity.value == 0 or abs(self.beta_angle.value) == 90 else "
        "sizing.eccentric_illumination(semimajor_axis=self.semimajor_axis, eccentricity=self.eccentricity, "
        "earth_radius=self.earth_radius, beta_angle=self.beta_angle, "
        "sun_projection_angle=self.sun_projection_angle, period=self.period).eclipse", "s",
    )
    sunlight_duration = Property("self.period.value - self.eclipse_duration.value", "s")

    def accepts(self, child):
        return isinstance(child, Requirement)
