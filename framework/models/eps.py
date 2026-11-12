"""EPS component types and fixed COTS specialisations."""

from .elements import Component, Subsystem
from .properties import Property


class EPS(Subsystem):
    power = Property("sum(child.power.value for child in self.power_consumers)", "W")

    @property
    def power_consumers(self):
        # Storage and generation are excluded from this default demand boundary.
        # A specialised EPS can choose a different boundary, including losses.
        return tuple(child for child in self.components if not isinstance(child, (Battery, SolarArray)))


class EPSComponent(Component):
    subsystem_type = EPS


class Battery(EPSComponent):
    rated_capacity = Property(unit="Ah")
    rated_energy = Property(unit="Wh")
    nominal_voltage = Property(unit="V")


class SolarArray(EPSComponent):
    maximum_power = Property(unit="W")
    active_area = Property(unit="m2")
    open_circuit_voltage = Property(unit="V")
    short_circuit_current = Property(unit="A")


class RegulatorAndConverter(EPSComponent):
    input_voltage = Property(unit="V")
    output_voltage = Property(unit="V")
    maximum_output_current = Property(unit="A")
    efficiency = Property(unit="1")


class PowerCircuit(EPSComponent):
    maximum_voltage = Property(unit="V")
    maximum_current = Property(unit="A")


class COTS(EPSComponent):
    """Product classes fix their inherited Property definitions."""

    fixed_properties = True


class CotsBattery(Battery, COTS):
    pass


class CotsSolarArray(SolarArray, COTS):
    pass


class CotsRegulatorAndConverter(RegulatorAndConverter, COTS):
    pass


class CotsPowerCircuit(PowerCircuit, COTS):
    pass


EPS.default_components = (Battery, SolarArray, RegulatorAndConverter, PowerCircuit)
