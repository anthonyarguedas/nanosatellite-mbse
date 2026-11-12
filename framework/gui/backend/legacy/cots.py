"""COTS classes inherit their engineering type and database loading behavior."""

from .elements import Component
from .eps.components import (
    Battery,
    BatteryCharger,
    BatteryProtector,
    CurrentSensor,
    DCDCConverter,
    Heater,
    IdealDiode,
    LoadSwitch,
    NonvolatileMemory,
    Processor,
    RealTimeClock,
    SolarArray,
    TemperatureSensor,
)
from .eps.subsystem import IntegratedEPS
from .database import DatabaseBacked, PropertySource, TabularDatabase

PRODUCT_TYPES = {}
PRODUCT_CLASSES = {}


def product_type(model, *, products=()):
    """Register a product family or an exact, encountered combination of functions."""
    def register(cls):
        cls.product_type = model
        cls.product_ids = tuple(products)
        cls.catalog_selection = True
        if products:
            for identity in products:
                PRODUCT_CLASSES[identity] = cls
        else:
            PRODUCT_TYPES[model] = cls
        return cls

    return register


@product_type("EPSModel::Battery")
class CotsBattery(Battery, DatabaseBacked):
    pass


@product_type("EPSModel::SolarArray")
class CotsSolarArray(SolarArray, DatabaseBacked):
    pass


@product_type("EPSModel::BatteryCharger")
class CotsBatteryCharger(BatteryCharger, DatabaseBacked):
    pass


@product_type("EPSModel::BatteryProtector")
class CotsBatteryProtector(BatteryProtector, DatabaseBacked):
    pass


@product_type("EPSModel::CurrentSensor")
class CotsCurrentSensor(CurrentSensor, DatabaseBacked):
    pass


@product_type("EPSModel::DCDCConverter")
class CotsDCDCConverter(DCDCConverter, DatabaseBacked):
    pass


@product_type("EPSModel::Heater")
class CotsHeater(Heater, DatabaseBacked):
    pass


@product_type("EPSModel::IdealDiode")
class CotsIdealDiode(IdealDiode, DatabaseBacked):
    pass


@product_type("EPSModel::LoadSwitch")
class CotsLoadSwitch(LoadSwitch, DatabaseBacked):
    pass


@product_type("EPSModel::NonvolatileMemory")
class CotsNonvolatileMemory(NonvolatileMemory, DatabaseBacked):
    pass


@product_type("EPSModel::Processor")
class CotsProcessor(Processor, DatabaseBacked):
    pass


@product_type("EPSModel::RealTimeClock")
class CotsRealTimeClock(RealTimeClock, DatabaseBacked):
    pass


@product_type("EPSModel::TemperatureSensor")
class CotsTemperatureSensor(TemperatureSensor, DatabaseBacked):
    pass


@product_type("EPSModel::IntegratedEPS")
class CotsIntegratedEPS(IntegratedEPS, DatabaseBacked):
    pass


@product_type("EPSModel::IntegratedEPS", products=(
    "isispace_iceps2_type_a", "isispace_imeps2_base_4s1p",
))
class CotsIntegratedBatteryEPS(CotsIntegratedEPS, CotsBattery):
    """The two existing EPS assemblies with included batteries, without PV panels."""

    property_sources = {
        **{name: PropertySource(name, "battery") for name in (
            "ac_impedance", "dc_internal_resistance", "dcir_baseline_current",
            "dcir_baseline_duration", "characterization_charge_current",
            "characterization_charge_temperature", "characterization_post_discharge_rest_time",
            "charge_current", "charge_current_max", "charge_voltage", "charge_duration",
            "charge_temperature_min", "charge_temperature_max", "charge_temperature_cutoff",
            "charge_termination_current", "discharge_current_continuous", "discharge_current_pulse",
            "discharge_cutoff_voltage", "discharge_temperature_min", "discharge_temperature_max",
            "discharge_temperature_cutoff", "cycle_life", "cycle_life_retained_capacity",
            "heater_power", "heater_resistance", "self_discharge_current", "chemistry",
            "protection_included", "balancing_included", "heater_included",
            "heater_control_automatic_available", "heater_control_default", "cutoff_implementation",
            "external_protection_required", "nominal_voltage", "series_cell_count",
            "parallel_string_count", "operating_temperature_min", "operating_temperature_max",
        )},
        "rated_capacity": PropertySource("battery_capacity", "battery"),
        "rated_energy": PropertySource("battery_energy", "battery"),
    }


class UnresolvedCotsComponent(Component, DatabaseBacked):
    """An explicit missing product selection, retained for repair."""

    catalog_selection = True
    type_is_resolved = False


def component_for_product(product, *, database=None, **kwargs):
    database = database or TabularDatabase()
    record = database.product(product)
    cls = (
        PRODUCT_CLASSES.get(record.id) or PRODUCT_TYPES.get(record.model)
        if record is not None
        else UnresolvedCotsComponent
    )
    if cls is None:
        raise ValueError(f"No generic component type is registered for {record.model}.")
    return cls(product=product, database=database, **kwargs)


def products(database=None, *, include_pins=True):
    return [
        record.projection(include_pins)
        for record in (database or TabularDatabase()).products()
    ]


def product_facts(product, database=None):
    record = (database or TabularDatabase()).product(product)
    if record is None:
        raise ValueError("Choose an existing COTS product.")
    return {"product": record.id, "facts": [fact.projection() for fact in record.facts]}
