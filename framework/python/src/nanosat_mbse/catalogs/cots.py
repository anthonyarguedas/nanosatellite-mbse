"""COTS classes inherit their engineering type and database loading behavior."""

from ..core.elements import Component
from ..domains.eps.components import (
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
from ..domains.eps.subsystem import IntegratedEPS
from .database import DatabaseBacked, TabularDatabase

PRODUCT_TYPES = {}


def product_type(model):
    def register(cls):
        cls.product_type = model
        cls.catalog_selection = True
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


class UnresolvedCotsComponent(Component, DatabaseBacked):
    """An explicit missing product selection, retained for repair."""

    catalog_selection = True


def component_for_product(product, *, database=None, **kwargs):
    database = database or TabularDatabase()
    record = database.product(product)
    cls = (
        PRODUCT_TYPES.get(record.model)
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
