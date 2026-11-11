"""Reusable component types shared by spacecraft subsystems."""

from ..core.elements import Component


class ProcessorAndMemory(Component):
    model = "SpaceSegment::CubeSat::PowerSubsystem::ProcessorAndMemory"
    default_name = "Processor and Memory"
    id_prefix = "PCM"


class Software(Component):
    model = "SpaceSegment::CubeSat::PowerSubsystem::Software"
    default_name = "Software"
    id_prefix = "SFW"
    default_accounting = "host"


class Instrument(Component):
    model = "SpaceSegment::CubeSat::PayloadSubsystem::Instrument"
    default_name = "Instrument"
    id_prefix = "INS"


class CommandTelemetryAndDataBus(Component):
    model = "SpaceSegment::CubeSat::CommandAndDataHandlingSubsystem::CommandTelemetryAndDataBus"
    default_name = "Command Telemetry and Data Bus"
    id_prefix = "COM"


class ReceiveAntennaAndEquipment(Component):
    model = "SpaceSegment::CubeSat::CommunicationSubsystem::ReceiveAntennaAndEquipment"
    default_name = "Receive Antenna and Equipment"
    id_prefix = "REC"


class TransmitAntennaAndEquipment(Component):
    model = "SpaceSegment::CubeSat::CommunicationSubsystem::TransmitAntennaAndEquipment"
    default_name = "Transmit Antenna and Equipment"
    id_prefix = "TRA"


class Actuator(Component):
    model = "SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Actuator"
    default_name = "Actuator"
    id_prefix = "ACT"


class Sensor(Component):
    model = "SpaceSegment::CubeSat::AttitudeDeterminationAndControlSubsystem::Sensor"
    default_name = "Sensor"
    id_prefix = "SEN"


class Accelerometer(Sensor):
    model = (
        "SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::Accelerometer"
    )
    default_name = "Accelerometer"
    id_prefix = "ACC"


class GNSSReceiver(Component):
    model = "SpaceSegment::CubeSat::GuidanceNavigationAndControlSubsystem::GNSSReceiver"
    default_name = "GNSS Receiver"
    id_prefix = "GNS"


class ActuatedMount(Component):
    model = "SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::ActuatedMount"
    default_name = "Actuated Mount"
    id_prefix = "ACT"


class DeployableMount(Component):
    model = "SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::DeployableMount"
    default_name = "Deployable Mount"
    id_prefix = "DEP"


class StaticMount(Component):
    model = "SpaceSegment::CubeSat::StructuresAndMechanismsSubsystem::StaticMount"
    default_name = "Static Mount"
    id_prefix = "STA"
    default_accounting = "excluded"


class ThermalSensor(Sensor):
    model = "SpaceSegment::CubeSat::ThermalSubsystem::ThermalSensor"
    default_name = "Thermal Sensor"
    id_prefix = "THE"


class ThermalSource(Component):
    model = "SpaceSegment::CubeSat::ThermalSubsystem::ThermalSource"
    default_name = "Thermal Source"
    id_prefix = "THE"


class ThermalSink(Component):
    model = "SpaceSegment::CubeSat::ThermalSubsystem::ThermalSink"
    default_name = "Thermal Sink"
    id_prefix = "THE"
    default_accounting = "excluded"


class PropellantStorage(Component):
    model = "SpaceSegment::CubeSat::PropulsionSubsystem::PropellantStorage"
    default_name = "Propellant Storage"
    id_prefix = "PRO"
    default_accounting = "excluded"


class PropellantControl(Component):
    model = "SpaceSegment::CubeSat::PropulsionSubsystem::PropellantControl"
    default_name = "Propellant Control"
    id_prefix = "PRO"


class Thrusters(Component):
    model = "SpaceSegment::CubeSat::PropulsionSubsystem::Thrusters"
    default_name = "Thrusters"
    id_prefix = "THR"
