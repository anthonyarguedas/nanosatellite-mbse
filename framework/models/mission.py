"""Mission domains and spacecraft subsystem specializations."""

from .elements import Element, Subsystem


class Mission(Element):
    model = "Mission"
    default_name = "Mission"
    id_prefix = "MIS"
    role = "mission"
    expandable = True

    def initialize(self, session):
        for definition in session.catalog.elements:
            if definition.parent is None:
                session.add(session.element_from_definition(definition), owner=self)


class External(Element):
    model = "External"
    default_name = "External"
    role = "external"


class Orbit(Element):
    model = "Orbit"
    default_name = "Orbit"
    id_prefix = "ORB"
    role = "orbit"


class CubeSat(Element):
    model = "SpaceSegment::CubeSat"
    default_name = "CubeSat Bus"
    id_prefix = "BUS"
    role = "bus"
    expandable = True


class Payload(Subsystem):
    model = "SpaceSegment::CubeSat::PayloadSubsystem"
    default_name = "Payload"
    id_prefix = "PAY"
    role = "payload"


class GroundStation(Element):
    model = "GroundSegment::GroundStation"
    default_name = "Ground Station"
    id_prefix = "GND"
    role = "ground"
    expandable = True


class CommandAndDataHandling(Subsystem):
    model = "SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem"
    default_name = "Command and Data Handling"
    id_prefix = "CDH"


class Communication(Subsystem):
    model = "SpaceSegment::CubeSat::CommunicationSubsystem"
    default_name = "Communication"
    id_prefix = "COM"


class AttitudeDeterminationAndControl(Subsystem):
    model = "SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem"
    default_name = "Attitude Determination and Control"
    id_prefix = "ADC"


class GuidanceNavigationAndControl(Subsystem):
    model = "SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem"
    default_name = "Guidance Navigation and Control"
    id_prefix = "GNC"


class StructuresAndMechanisms(Subsystem):
    model = "SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem"
    default_name = "Structures and Mechanisms"
    id_prefix = "STR"


class Thermal(Subsystem):
    model = "SpaceSegment::CubeSat::ThermalSubsystem"
    default_name = "Thermal"
    id_prefix = "THE"


class Propulsion(Subsystem):
    model = "SpaceSegment::CubeSat::PropulsionSubsystem"
    default_name = "Propulsion"
    id_prefix = "PRO"


class GroundSubsystem(Subsystem):
    expandable = False


class PlanAndSchedule(GroundSubsystem):
    model = "GroundSegment::PlanAndScheduleSubsystem"
    default_name = "Plan and Schedule"
    id_prefix = "PLS"


class SpacecraftCommand(GroundSubsystem):
    model = "GroundSegment::SpacecraftCommandSubsystem"
    default_name = "Spacecraft Command"
    id_prefix = "SCC"


class GroundEquipmentControl(GroundSubsystem):
    model = "GroundSegment::GroundEquipmentControlSubsystem"
    default_name = "Ground Equipment Control"
    id_prefix = "GEC"


class SpaceGroundCommunication(GroundSubsystem):
    model = "GroundSegment::SpaceGroundCommunicationSubsystem"
    default_name = "Space Ground Communication"
    id_prefix = "SGC"


class MissionDataProcessing(GroundSubsystem):
    model = "GroundSegment::MissionDataProcessingSubsystem"
    default_name = "Mission Data Processing"
    id_prefix = "MDP"


class MissionDataDissemination(GroundSubsystem):
    model = "GroundSegment::MissionDataDisseminationSubsystem"
    default_name = "Mission Data Dissemination"
    id_prefix = "MDD"


class Network(GroundSubsystem):
    model = "GroundSegment::NetworkSubsystem"
    default_name = "Network"
    id_prefix = "NET"


class TelemetryProcessing(GroundSubsystem):
    model = "GroundSegment::TelemetryProcessingSubsystem"
    default_name = "Telemetry Processing"
    id_prefix = "TLM"
