"""Concrete segment and subsystem classifications, with visible defaults."""

from .elements import GroundSegment, SpaceSegment, Subsystem
from .eps import EPS
from .properties import Property
from .requirements import VerificationCondition


class CommandAndDataHandling(Subsystem):
    pass


class Communication(Subsystem):
    pass


class AttitudeDeterminationAndControl(Subsystem):
    pointing = Property(unit="1")
    pointing_face = Property(unit="1")
    clocking_angle = Property(unit="deg")
    effective_clocking_angle = Property("0 if self.pointing.value == 'sun_pointing' else self.clocking_angle", "deg")


class GuidanceNavigationAndControl(Subsystem):
    pass


class StructuresAndMechanisms(Subsystem):
    pass


class Thermal(Subsystem):
    pass


class Propulsion(Subsystem):
    pass


class Payload(Subsystem):
    pass


class CubeSatBus(SpaceSegment):
    units = Property(unit="U")
    length_x = Property("illumination.cubesat_dimensions(units=self.units).x", "m")
    length_y = Property("illumination.cubesat_dimensions(units=self.units).y", "m")
    length_z = Property("illumination.cubesat_dimensions(units=self.units).z", "m")
    default_subsystems = (
        EPS,
        CommandAndDataHandling,
        Communication,
        AttitudeDeterminationAndControl,
        GuidanceNavigationAndControl,
        StructuresAndMechanisms,
        Thermal,
        Propulsion,
        Payload,
    )

    def create_requirements(self):
        limits = (
            (
                "mass", "kg", "2", "kg/U",
                "CubeSat Design Specification Rev 14.1, Table 1 gives typical maxima of 2 kg/U. "
                "Confirm the applicable dispenser and launch provider limits.",
            ),
            (
                "volume", "m3", "0.001", "m3/U",
                "Nominal allocation of 0.001 m3/U from the 10 cm cube definition. "
                "This checks accounted volume. Bounding dimensions, packing and dispenser fit require separate checks.",
            ),
        )
        for quantity, unit, per_u, per_u_unit, rationale in limits:
            name = f"{quantity}_limit"
            condition = VerificationCondition(
                "maximum", getattr(self, quantity),
                Property("self.parent.units.value * self.parent.maximum_per_u.value", unit),
                "type(self.parent.units.value) in (int, float) and self.parent.units.value > 0 "
                "and 0 < target and math.isfinite(target) and 0 <= measure <= target",
            )
            self.add_requirement(
                name,
                statement=f"The complete {{self.context.name}} {quantity} shall not exceed {{maximum.target}}.",
                rationale=rationale,
                units=self.units,
                maximum_per_u=Property(per_u, per_u_unit),
                conditions=(condition,),
            )


class GroundStation(GroundSegment):
    pass
