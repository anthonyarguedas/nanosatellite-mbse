"""Concrete segment and subsystem classifications, with visible defaults."""

from .elements import GroundSegment, SpaceSegment, Subsystem
from .eps import EPS
from .properties import Property
from .requirements import Requirement, VerificationCondition


class CommandAndDataHandling(Subsystem):
    pass


class Communication(Subsystem):
    pass


class AttitudeDeterminationAndControl(Subsystem):
    pass


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

    def create_defaults(self):
        super().create_defaults()
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
            if any(requirement.name == name for requirement in self.requirements):
                continue
            condition = VerificationCondition(
                "maximum", getattr(self, quantity),
                Property("self.parent.units.value * self.parent.maximum_per_u.value", unit),
                "type(self.parent.units.value) in (int, float) and self.parent.units.value > 0 "
                "and 0 < target and math.isfinite(target) and 0 <= measure <= target",
            )
            self.add(Requirement(
                name,
                statement=f"The complete {{self.parent.name}} {quantity} shall not exceed {{maximum.target}}.",
                rationale=rationale,
                units=self.units,
                maximum_per_u=Property(per_u, per_u_unit),
                conditions=(condition,),
            ))


class GroundStation(GroundSegment):
    pass
