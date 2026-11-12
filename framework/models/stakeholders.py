"""Stakeholder classifications and third parties."""

from .objects import ModelObject


class Stakeholder(ModelObject):
    pass


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
