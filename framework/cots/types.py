"""Catalog component classes refining the six CSRM EPS categories."""

from framework.models.eps import (
    Battery, SolarArray, RegulatorAndConverter, PowerCircuit, Protection,
    ProcessorAndMemory, Software,
)
from framework.models.properties import Property


class DCDCConverter(RegulatorAndConverter):
    pass


class LinearRegulator(RegulatorAndConverter):
    pass


class BatteryCharger(RegulatorAndConverter):
    pass


class BatteryProtector(Protection):
    pass


class LoadSwitch(PowerCircuit):
    catalog_parameters = {
        "maximum_voltage": "input_voltage_max",
        "maximum_current": "maximum_output_current",
    }


class ProtectedLoadSwitch(LoadSwitch, Protection):
    pass


class IdealDiode(PowerCircuit):
    catalog_parameters = LoadSwitch.catalog_parameters


class PowerSwitch(PowerCircuit):
    """A discrete power transistor with separately sourced stress ratings."""


class ResettableFuse(PowerCircuit):
    """A thermal resettable fuse, with distinct hold and trip currents."""


class Diode(PowerCircuit):
    pass


class Sensor(PowerCircuit):
    pass


class CurrentSensor(Sensor):
    pass


class TemperatureSensor(Sensor):
    pass


class Heater(PowerCircuit):
    """A resistive heater circuit used for EPS thermal control."""


class Processor(ProcessorAndMemory):
    pass


class NonvolatileMemory(ProcessorAndMemory):
    pass


class RealTimeClock(ProcessorAndMemory):
    pass


class Watchdog(ProcessorAndMemory):
    pass


class IntegratedEPS(RegulatorAndConverter, PowerCircuit):
    """Power conversion and distribution, without an included battery."""

    catalog_parameters = LoadSwitch.catalog_parameters


class BatteryIntegratedEPS(Battery, IntegratedEPS):
    # Battery and power circuit voltage limits have separate catalog bindings.
    # A role and channel selection supplies the applicable native definition.
    maximum_voltage = Property(unit="V")


COMPONENT_TYPES = {
    cls.__name__: cls for cls in (
        Battery, SolarArray, RegulatorAndConverter, PowerCircuit, Protection,
        ProcessorAndMemory, Software, DCDCConverter, LinearRegulator,
        BatteryCharger, BatteryProtector, LoadSwitch, ProtectedLoadSwitch,
        IdealDiode, PowerSwitch, ResettableFuse, Diode, Sensor, CurrentSensor,
        TemperatureSensor, Heater, Processor, NonvolatileMemory, RealTimeClock,
        Watchdog, IntegratedEPS, BatteryIntegratedEPS,
    )
}
for _type in COMPONENT_TYPES.values():
    if _type.__module__ == __name__:
        _type.catalog_type = _type
