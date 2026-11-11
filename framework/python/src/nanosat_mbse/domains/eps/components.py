"""Generic EPS components and more specific engineering types."""

from ...core.elements import Component
from ..components import ProcessorAndMemory, ThermalSensor, ThermalSource


class Battery(Component):
    model = "SpaceSegment::CubeSat::PowerSubsystem::Batteries"
    default_name = "Batteries"
    id_prefix = "BAT"
    default_accounting = "excluded"


class SolarArray(Component):
    model = "SpaceSegment::CubeSat::PowerSubsystem::SolarArrays"
    default_name = "Solar Arrays"
    id_prefix = "SOL"
    default_accounting = "excluded"


class RegulatorAndConverter(Component):
    model = "SpaceSegment::CubeSat::PowerSubsystem::RegulatorsAndConverters"
    default_name = "Regulators and Converters"
    id_prefix = "REG"


class PowerCircuit(Component):
    model = "SpaceSegment::CubeSat::PowerSubsystem::PowerCircuitsAndSwitches"
    default_name = "Power Circuits and Switches"
    id_prefix = "PCS"


class PowerLoss(Component):
    """Explicit dissipative demand at the declared budget boundary, in W.

    This is an accounting contribution, with no additional physical hardware.
    Supply losses only when they are absent from the other counted loads.
    """

    model = "SpaceSegment::CubeSat::PowerSubsystem::PowerLoss"
    default_name = "Power Loss"
    id_prefix = "LOS"
    resource_accounting = False


class BatteryCharger(RegulatorAndConverter):
    default_name = "Battery Charger"


class BatteryProtector(PowerCircuit):
    default_name = "Battery Protector"


class DCDCConverter(RegulatorAndConverter):
    default_name = "DC/DC Converter"


class CurrentSensor(PowerCircuit):
    default_name = "Current Sensor"


class IdealDiode(PowerCircuit):
    default_name = "Ideal Diode"


class LoadSwitch(PowerCircuit):
    default_name = "Load Switch"


class Heater(ThermalSource):
    default_name = "Heater"


class Processor(ProcessorAndMemory):
    default_name = "Processor"


class NonvolatileMemory(ProcessorAndMemory):
    default_name = "Nonvolatile Memory"


class RealTimeClock(ProcessorAndMemory):
    default_name = "Real Time Clock"


class TemperatureSensor(ThermalSensor):
    default_name = "Temperature Sensor"
