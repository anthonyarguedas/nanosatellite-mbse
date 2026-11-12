"""Concrete segment and subsystem classifications, with visible defaults."""

from .elements import GroundSegment, SpaceSegment, Subsystem
from .eps import EPS


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


class GroundStation(GroundSegment):
    pass
