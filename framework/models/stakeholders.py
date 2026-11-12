"""Stakeholder classifications and third parties."""

from .objects import ModelObject
from .requirements import Requirement


class Stakeholder(ModelObject):
    def accepts(self, child):
        return isinstance(child, Requirement)


class RegulatoryAgency(Stakeholder):
    pass


class MissionStakeholder(Stakeholder):
    pass


class LaunchProvider(Stakeholder):
    pass


class Partner(Stakeholder):
    pass


class ThirdParty(ModelObject):
    pass
