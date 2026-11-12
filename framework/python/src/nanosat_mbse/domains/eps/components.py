"""Generic EPS components and their database-independent property contracts."""

from ...core.elements import Component
from ...core.properties import ComponentProperty as Property, property_type
from ..components import ProcessorAndMemory, ThermalSensor, ThermalSource


class ElectricalComponent(Component):
    mass = Property(unit="kg")
    length = Property(unit="m")
    width = Property(unit="m")
    height = Property(unit="m")
    diameter = Property(unit="m")
    operating_temperature_min = Property(unit="K")
    operating_temperature_max = Property(unit="K")
    storage_temperature_min = Property(unit="K")
    storage_temperature_max = Property(unit="K")
    nominal_voltage = Property(unit="V")
    input_voltage_min = Property(unit="V")
    input_voltage_max = Property(unit="V")
    output_voltage_min = Property(unit="V")
    output_voltage_max = Property(unit="V")
    maximum_input_current = Property(unit="A")
    maximum_output_current = Property(unit="A")
    maximum_input_power = Property(unit="W")
    maximum_output_power = Property(unit="W")
    efficiency = Property(unit="1")
    quiescent_current = Property(unit="A")
    shutdown_current = Property(unit="A")
    series_cell_count = Property(int, "1")
    parallel_string_count = Property(int, "1")


@property_type
class Battery(ElectricalComponent):
    model = "SpaceSegment::CubeSat::PowerSubsystem::Batteries"
    default_name = "Batteries"
    id_prefix = "BAT"
    default_accounting = "excluded"

    rated_capacity = Property(unit="Ah")
    rated_energy = Property(unit="Wh")
    ac_impedance = Property(unit="ohm")
    dc_internal_resistance = Property(unit="ohm")
    dcir_baseline_current = Property(unit="A")
    dcir_baseline_duration = Property(unit="s")
    characterization_charge_current = Property(unit="A")
    characterization_charge_temperature = Property(unit="K")
    characterization_post_discharge_rest_time = Property(unit="s")
    charge_current = Property(unit="A")
    charge_current_max = Property(unit="A")
    charge_voltage = Property(unit="V")
    charge_duration = Property(unit="s")
    charge_temperature_min = Property(unit="K")
    charge_temperature_max = Property(unit="K")
    charge_temperature_cutoff = Property(unit="K")
    charge_termination_current = Property(unit="A")
    discharge_current_continuous = Property(unit="A")
    discharge_current_pulse = Property(unit="A")
    discharge_cutoff_voltage = Property(unit="V")
    discharge_temperature_min = Property(unit="K")
    discharge_temperature_max = Property(unit="K")
    discharge_temperature_cutoff = Property(unit="K")
    cycle_life = Property(int, "1")
    cycle_life_retained_capacity = Property(unit="1")
    heater_power = Property(unit="W")
    heater_resistance = Property(unit="ohm")
    self_discharge_current = Property(unit="A")
    chemistry = Property(str)
    protection_included = Property(bool)
    balancing_included = Property(bool)
    heater_included = Property(bool)
    heater_control_automatic_available = Property(bool)
    heater_control_default = Property(str)
    cutoff_implementation = Property(str)
    external_protection_required = Property(bool)


@property_type
class SolarArray(ElectricalComponent):
    model = "SpaceSegment::CubeSat::PowerSubsystem::SolarArrays"
    default_name = "Solar Arrays"
    id_prefix = "SOL"
    default_accounting = "excluded"

    active_area = Property(unit="m2")
    areal_mass = Property(unit="kg/m2")
    maximum_power = Property(unit="W")
    maximum_power_density = Property(unit="W/m2")
    voltage_at_maximum_power = Property(unit="V")
    current_at_maximum_power = Property(unit="A")
    current_density_at_maximum_power = Property(unit="A/m2")
    open_circuit_voltage = Property(unit="V")
    short_circuit_current = Property(unit="A")
    short_circuit_current_density = Property(unit="A/m2")
    reference_irradiance = Property(unit="W/m2")
    end_of_life_power_fraction = Property(unit="1")
    current_at_maximum_power_remaining_fraction = Property(unit="1")
    voltage_at_maximum_power_remaining_fraction = Property(unit="1")
    open_circuit_voltage_remaining_fraction = Property(unit="1")
    short_circuit_current_remaining_fraction = Property(unit="1")
    current_at_maximum_power_temperature_coefficient = Property(unit="A/K")
    voltage_at_maximum_power_temperature_coefficient = Property(unit="V/K")
    open_circuit_voltage_temperature_coefficient = Property(unit="V/K")
    short_circuit_current_temperature_coefficient = Property(unit="A/K")
    current_temperature_coefficient = Property(unit="A/K")
    voltage_temperature_coefficient = Property(unit="V/K")
    power_temperature_coefficient = Property(unit="1/K")
    relative_current_at_maximum_power_temperature_coefficient = Property(unit="1/K")
    relative_short_circuit_current_temperature_coefficient = Property(unit="1/K")
    temperature_coefficient_temperature_min = Property(unit="K")
    temperature_coefficient_temperature_max = Property(unit="K")
    coverglass_thickness = Property(unit="m")
    interconnector_count = Property(int, "1")
    bypass_diode_forward_voltage = Property(unit="V")
    bypass_diode_reverse_current = Property(unit="A")
    bypass_diode = Property(bool)
    deployable = Property(bool)
    geometry_configurable = Property(bool)
    external_bypass_diode_compatible = Property(bool)
    cell_polarity = Property(str)
    iv_curve_current_sign_convention = Property(str)
    coverglass_material = Property(str)
    interconnector_material = Property(str)


@property_type
class RegulatorAndConverter(ElectricalComponent):
    model = "SpaceSegment::CubeSat::PowerSubsystem::RegulatorsAndConverters"
    default_name = "Regulators and Converters"
    id_prefix = "REG"


@property_type
class PowerCircuit(ElectricalComponent):
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


@property_type
class BatteryCharger(RegulatorAndConverter):
    default_name = "Battery Charger"
    charge_current = Property(unit="A")
    charge_current_max = Property(unit="A")
    charge_voltage_min = Property(unit="V")
    charge_voltage_max = Property(unit="V")
    cell_count_min = Property(int, "1")
    cell_count_max = Property(int, "1")
    autonomous_mppt = Property(bool)


@property_type
class BatteryProtector(PowerCircuit):
    default_name = "Battery Protector"
    overvoltage_threshold = Property(unit="V")
    undervoltage_threshold = Property(unit="V")
    overcurrent_threshold = Property(unit="A")


@property_type
class DCDCConverter(RegulatorAndConverter):
    default_name = "DC/DC Converter"
    fixed_output_voltage = Property(unit="V")
    switching_frequency = Property(unit="Hz")
    dropout_voltage = Property(unit="V")


@property_type
class CurrentSensor(PowerCircuit):
    default_name = "Current Sensor"
    current_range_min = Property(unit="A")
    current_range_max = Property(unit="A")
    current_measurement_error = Property(unit="1")
    current_resolution = Property(unit="A")


@property_type
class IdealDiode(PowerCircuit):
    default_name = "Ideal Diode"
    on_resistance = Property(unit="ohm")
    reverse_current_blocking = Property(bool)


@property_type
class LoadSwitch(PowerCircuit):
    default_name = "Load Switch"
    on_resistance = Property(unit="ohm")
    current_limit = Property(unit="A")
    default_enabled = Property(bool)


@property_type
class Heater(ThermalSource):
    default_name = "Heater"
    rated_power = Property(unit="W")
    resistance = Property(unit="ohm")


class Processor(ProcessorAndMemory):
    default_name = "Processor"


class NonvolatileMemory(ProcessorAndMemory):
    default_name = "Nonvolatile Memory"


class RealTimeClock(ProcessorAndMemory):
    default_name = "Real Time Clock"


@property_type
class TemperatureSensor(ThermalSensor):
    default_name = "Temperature Sensor"
    temperature_accuracy = Property(unit="K")
    temperature_resolution = Property(unit="K")
    temperature_range_min = Property(unit="K")
    temperature_range_max = Property(unit="K")
