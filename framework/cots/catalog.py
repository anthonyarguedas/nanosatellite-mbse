"""Validated catalog facts and fixed, typed COTS definitions.

Default bindings use unconditional facts and conservative declared value meanings.
A condition selects matching facts before unconditional specifications. Ambiguous
facts remain unset. Qualified properties retain each role and channel separately.
"""

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from framework.models.eps import COTS, EPS, Protection, SolarPowerPath
from framework.models.properties import Property
from .types import COMPONENT_TYPES, IntegratedEPS


KINDS = frozenset(("minimum", "maximum", "typical", "nominal", "fixed", "derived", "absolute_maximum", "declared", "digitized"))
DEFAULT_KINDS = {
    "mass": ("maximum",),
    "rated_energy": ("minimum",), "cell_rated_energy": ("minimum",),
    "rated_capacity": ("minimum",), "cell_rated_capacity": ("minimum",),
    "nominal_voltage": ("nominal",), "cell_nominal_voltage": ("nominal",),
    "minimum_voltage": ("minimum", "nominal", "fixed"),
    "cell_minimum_voltage": ("minimum", "nominal", "fixed"),
    "maximum_voltage": ("maximum", "nominal", "fixed"),
    "cell_maximum_voltage": ("maximum", "nominal", "fixed"),
    "minimum_input_voltage": ("minimum",), "maximum_input_voltage": ("maximum",),
    "absolute_maximum_input_voltage": ("absolute_maximum",),
    "maximum_input_current": ("minimum", "maximum"),
    "maximum_output_current": ("minimum", "maximum"),
    "maximum_current": ("minimum", "maximum"),
    "maximum_charge_current": ("minimum", "maximum"),
    "maximum_discharge_current": ("minimum", "maximum"),
    "cell_maximum_charge_current": ("maximum",),
    "cell_maximum_discharge_current": ("maximum",),
    "undervoltage_threshold": ("maximum",),
    "overvoltage_threshold": ("minimum",), "current_limit": ("minimum",),
    "series_count": ("fixed", "derived"), "parallel_count": ("fixed", "derived"),
    "transfer_method": (),  # Supported methods do not select the installed path.
    "output_voltage": ("fixed", "nominal"),
    "input_voltage_setpoint": (),  # An application example does not select a setting.
    "efficiency": ("typical",), "bol_efficiency": ("typical",),
    "eol_efficiency": ("derived", "typical"),
    "cell_eol_voltage": ("derived", "typical"), "cell_eol_current": ("derived", "typical"),
    "cell_open_circuit_voltage": ("derived", "typical"),
    "cell_short_circuit_current": ("derived", "typical"),
    "maximum_power": ("derived", "typical"),
    "lifetime_retention": ("derived", "typical"),
}
UNITS = {"m2": "m^2", "m3": "m^3", "W/m2": "W/m^2"}
COUNTS = ("series_count", "parallel_count", "cell_count")
PRODUCT_PROPERTIES = ("mass", "volume", "cost")


@dataclass(frozen=True)
class CatalogFact:
    product_id: str
    element_id: str
    parameter: str
    value: object
    value_kind: str
    unit: str
    condition_id: str
    source_id: str
    source_locator: str
    model_class: str = ""
    model_property: str = ""
    status: str = "existing"
    note: str = ""


@dataclass(frozen=True)
class CatalogBinding:
    property_name: str
    element_id: str
    model_class: str
    facts: tuple


@dataclass(frozen=True)
class CatalogProduct:
    product_id: str
    model_class: type
    manufacturer: str
    part_number: str
    product_level: str
    product_url: str
    datasheet_url: str
    facts: tuple


def _rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return tuple(csv.DictReader(stream, delimiter="\t"))


def _index(rows, key):
    result = {}
    for row in rows:
        identity = key(row)
        if identity in result:
            raise ValueError(f"Duplicate catalog identity {identity!r}.")
        result[identity] = row
    return result


def _number(value, integer=False):
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"Invalid catalog number {value!r}.") from error
    if not number.is_finite() or integer and number != number.to_integral_value():
        raise ValueError(f"Invalid {'integer' if integer else 'finite number'} {value!r}.")
    result = int(number) if integer else float(number)
    if not integer and not Decimal(str(result)).is_finite():
        raise ValueError(f"Catalog number exceeds the supported range: {value!r}.")
    return result


def _unit_matches(actual, expected, name):
    return UNITS.get(actual, actual) == UNITS.get(expected, expected) or (
        name in COUNTS and actual == "1" and expected in ("cell", "string")
    )


def _select(facts, name, condition_id, value_kinds):
    applicable = tuple(fact for fact in facts if fact.value is not None and fact.condition_id == condition_id)
    if not applicable and condition_id:
        applicable = tuple(fact for fact in facts if fact.value is not None and not fact.condition_id)
    # The purchased item's structural counts are independent of a test case.
    if not applicable and name in COUNTS:
        applicable = tuple(fact for fact in facts if fact.value is not None)
    kinds = value_kinds.get(name, DEFAULT_KINDS.get(name))
    if kinds is None:
        kinds = ("minimum",) if name.endswith("_min") else ("maximum",) if name.endswith("_max") else ("fixed", "nominal", "declared")
    if isinstance(kinds, str):
        kinds = (kinds,)
    for kind in kinds:
        selected = tuple(fact for fact in applicable if fact.value_kind == kind)
        if selected:
            return selected if len({(type(fact.value), fact.value) for fact in selected}) == 1 else ()
    return ()


class Catalog:
    def __init__(self, directory):
        directory = Path(directory)
        definitions = _index(_rows(directory / "definitions.tsv"), lambda r: (r["definition_kind"], r["name"]))
        self.sources = MappingProxyType({key: MappingProxyType(row) for key, row in
                                        _index(_rows(directory / "sources.tsv"), lambda r: r["source_id"]).items()})
        self.conditions = MappingProxyType({key: MappingProxyType(row) for key, row in
                                           _index(_rows(directory / "conditions.tsv"), lambda r: r["condition_id"]).items()})
        self.elements = _index(_rows(directory / "elements.tsv"), lambda r: (r["product_id"], r["element_id"]))
        products = _index(_rows(directory / "products.tsv"), lambda r: r["product_id"])
        for (product_id, element_id), element in self.elements.items():
            parent = element["parent_element_id"]
            if product_id not in products or parent != "self" and (product_id, parent) not in self.elements:
                raise ValueError(f"Unknown catalog element parent for {product_id}.{element_id}.")
        parameters = {}
        for row in _rows(directory / "condition-parameters.tsv"):
            definition = definitions.get(("condition_parameter", row["parameter_name"]))
            if (row["condition_id"] not in self.conditions or row["source_id"] not in self.sources
                    or definition is None or row["unit"] != definition["canonical_unit"]
                    or row["value_kind"] not in KINDS | {"maximum_exclusive", "minimum_exclusive"}):
                raise ValueError(f"Invalid catalog condition parameter {row!r}.")
            _number(row["value"], definition["scalar_type"] == "Integer")
            parameters.setdefault(row["condition_id"], []).append(MappingProxyType(row))
        self.condition_parameters = MappingProxyType({key: tuple(rows) for key, rows in parameters.items()})
        curves = {}
        for row in _rows(directory / "curves.tsv"):
            self._validate_reference(row, products)
            for axis in ("independent", "dependent"):
                definition = definitions.get(("curve_axis", row[f"{axis}_parameter"]))
                if definition is None or row[f"{axis}_unit"] != definition["canonical_unit"]:
                    raise ValueError(f"Invalid catalog curve axis {row!r}.")
                _number(row[f"{axis}_value"], definition["scalar_type"] == "Integer")
            key = row["product_id"], row["element_id"], row["curve_id"]
            curves.setdefault(key, []).append(MappingProxyType(row))
        self.curves = MappingProxyType({key: tuple(rows) for key, rows in curves.items()})
        facts = {key: [] for key in products}
        self._templates = {name: cls("template") for name, cls in COMPONENT_TYPES.items()}
        self._templates["SolarPowerPath"] = SolarPowerPath("template")
        for table, field, kind in (("parameters.tsv", "parameter_name", "parameter"), ("features.tsv", "feature_name", "feature")):
            for row in _rows(directory / table):
                self._validate_reference(row, products)
                definition = definitions.get((kind, row[field]))
                if definition is None:
                    raise ValueError(f"Unknown catalog {kind} {row[field]!r}.")
                scalar = definition["scalar_type"]
                if scalar == "Boolean":
                    if row["value"] not in ("true", "false"):
                        raise ValueError(f"Invalid Boolean catalog fact {row!r}.")
                    value = row["value"] == "true"
                elif scalar == "String":
                    value = row["value"]
                else:
                    value = _number(row["value"], scalar == "Integer")
                unit = row.get("unit", definition["canonical_unit"])
                if unit != definition["canonical_unit"]:
                    raise ValueError(f"Incorrect catalog unit for {row[field]}: {unit!r}.")
                value_kind = row.get("value_kind", "declared")
                if value_kind not in KINDS:
                    raise ValueError(f"Unknown value meaning {value_kind!r}.")
                facts[row["product_id"]].append(CatalogFact(
                    row["product_id"], row["element_id"], row[field], value, value_kind, unit,
                    row.get("condition_id", ""), row["source_id"], row["source_locator"],
                ))
        for row in _rows(directory / "model-inputs.tsv"):
            self._validate_reference(row, products, optional_source=True)
            template = self._templates.get(row["model_class"])
            if template is None and row["model_class"] not in ("Mission", "EPS"):
                raise ValueError(f"Unknown native model class {row['model_class']!r}.")
            if row["status"] not in ("existing", "extracted", "derived", "unknown", "mission_input", "not_applicable"):
                raise ValueError(f"Unknown native binding status {row['status']!r}.")
            if row["value"]:
                if row["status"] not in ("existing", "extracted", "derived"):
                    raise ValueError(f"A catalog binding has no supported status: {row!r}.")
                if template is None or row["model_property"] not in template.properties:
                    raise ValueError(f"Unknown native catalog binding {row['model_class']}.{row['model_property']}.")
                prop = template.properties[row["model_property"]]
                if not _unit_matches(row["unit"], str(prop.unit), row["model_property"]):
                    raise ValueError(f"Incorrect native unit for {row['model_class']}.{row['model_property']}.")
                if row["value_kind"] not in KINDS or not row["source_id"]:
                    raise ValueError(f"A catalog binding needs a source and value meaning: {row!r}.")
                value = row["value"] if row["model_property"] == "transfer_method" else _number(row["value"], row["model_property"] in COUNTS)
            else:
                value = None
            facts[row["product_id"]].append(CatalogFact(
                row["product_id"], row["element_id"], row["catalog_parameter"], value,
                row["value_kind"], row["unit"], row["condition_id"], row["source_id"], row["source_locator"],
                row["model_class"], row["model_property"], row["status"], row["note"],
            ))
        result = {}
        for key, row in products.items():
            cls = COMPONENT_TYPES.get(row["model_type"])
            if cls is None:
                raise ValueError(f"Unknown Python catalog class {row['model_type']!r} for {key}.")
            omitted = {"mass", "volume", "power"} - self._templates[cls.__name__].properties.keys()
            if any(not fact.model_class and fact.parameter in omitted for fact in facts[key]):
                raise ValueError(f"{cls.__name__} cannot own physical hardware properties.")
            for fact in facts[key]:
                if fact.value is not None and fact.model_class and not issubclass(cls, type(self._templates[fact.model_class])):
                    raise ValueError(f"{key} does not inherit the binding class {fact.model_class}.")
            result[key] = CatalogProduct(key, cls, *(row[name] for name in (
                "manufacturer", "part_number", "product_level", "product_url", "datasheet_url",
            )), tuple(facts[key]))
        self.products = MappingProxyType(result)
        self._classes = {}

    def _validate_reference(self, row, products, optional_source=False):
        key = row["product_id"], row["element_id"]
        if key[0] not in products or key[1] != "self" and key not in self.elements:
            raise ValueError(f"Unknown catalog product or element {key!r}.")
        if row.get("condition_id") and row["condition_id"] not in self.conditions:
            raise ValueError(f"Unknown catalog condition {row['condition_id']!r}.")
        if (row["source_id"] or not optional_source) and row["source_id"] not in self.sources:
            raise ValueError(f"Unknown catalog source {row['source_id']!r}.")

    def __len__(self):
        return len(self.products)

    def product(self, product_id, *, model_class=None, element_id="self", condition_id="", value_kinds=None, name=None):
        product = self.products[product_id]
        condition_id = condition_id or ""
        role = COMPONENT_TYPES.get(model_class) if isinstance(model_class, str) else model_class or product.model_class
        if not isinstance(role, type) or not issubclass(product.model_class, role):
            raise ValueError(f"{product_id} does not implement {model_class!r}.")
        if element_id != "self" and (product_id, element_id) not in self.elements:
            raise ValueError(f"Unknown element {product_id}.{element_id}.")
        if condition_id and condition_id not in self.conditions:
            raise ValueError(f"Unknown catalog condition {condition_id!r}.")
        value_kinds = dict(value_kinds or {})
        for key, kinds in value_kinds.items():
            kinds = (kinds,) if isinstance(kinds, str) else tuple(kinds)
            if any(kind not in KINDS for kind in kinds):
                raise ValueError(f"Unknown value meaning for {key!r}.")
            value_kinds[key] = kinds
        cache_key = product_id, role, element_id, condition_id, tuple(sorted(value_kinds.items()))
        if cache_key not in self._classes:
            self._classes[cache_key] = self._product_class(product, role, element_id, condition_id, value_kinds)
        return self._classes[cache_key](product_id if name is None else name)

    def _product_class(self, product, role, element_id, condition_id, value_kinds):
        template = self._templates[product.model_class.__name__]
        namespace = {"__module__": "framework.cots", "product_id": product.product_id,
                     "catalog_product": product, "catalog_role": role,
                     "catalog_element": element_id, "catalog_condition": condition_id}
        groups = {}
        for fact in product.facts:
            if fact.model_class:
                if fact.model_class not in self._templates or not fact.model_property.isidentifier():
                    continue
                if not issubclass(product.model_class, type(self._templates[fact.model_class])):
                    continue
                unit = str(self._templates[fact.model_class].properties[fact.model_property].unit) if fact.model_property in self._templates[fact.model_class].properties else None
                if unit is None:
                    continue
                key = fact.element_id, fact.model_class, fact.model_property
            else:
                key, unit = (fact.element_id, "", fact.parameter), fact.unit
            groups.setdefault(key, (unit, []))[1].append(fact)
        bindings, selected_keys = [], {}
        for (element, cls, prop_name), (unit, facts) in groups.items():
            qualified = "__".join(part for part in (element, cls, prop_name) if part)
            selected = _select(facts, prop_name, condition_id, value_kinds)
            namespace[qualified] = Property(repr(selected[0].value) if selected else None, unit)
            bindings.append(CatalogBinding(qualified, element, cls, selected))
            selected_keys[element, cls, prop_name] = qualified, selected
        aliases = dict(getattr(product.model_class, "catalog_parameters", {}))
        names = set(template.properties) | {fact.parameter for fact in product.facts if not fact.model_class and fact.element_id == element_id}
        names -= {name for name in ("mass", "volume", "power") if name not in template.properties}
        for prop_name in sorted(names):
            native = [key for key in selected_keys if key[0] == element_id and key[2] == prop_name
                      and key[1] and issubclass(role, type(self._templates[key[1]]))]
            native = [key for key in native if not any(other != key and issubclass(
                type(self._templates[other[1]]), type(self._templates[key[1]])) for other in native)]
            # A combined product needs an explicit role when native names conflict.
            if len(native) > 1:
                namespace[prop_name] = Property(unit=str(template.properties[prop_name].unit))
                continue
            source_element = "self" if prop_name in PRODUCT_PROPERTIES else element_id
            key = native[0] if native else (source_element, "", aliases.get(prop_name, prop_name))
            # A rail's voltage applies to its child channels. Its total current does not.
            element = self.elements.get((product.product_id, element_id), {})
            if key not in selected_keys and prop_name == "output_voltage" and element.get("element_kind") == "channel":
                key = (element["parent_element_id"], "RegulatorAndConverter", prop_name)
            if key not in selected_keys:
                continue
            qualified, selected = selected_keys[key]
            if not key[1] and prop_name != key[2]:
                selected = _select(groups[key][1], prop_name, condition_id, value_kinds)
            unit = str(template.properties[prop_name].unit) if prop_name in template.properties else groups[key][0]
            if not _unit_matches(groups[key][0], unit, prop_name):
                raise ValueError(f"Incompatible binding unit for {product.product_id}.{prop_name}.")
            if selected or prop_name not in template.properties or template.properties[prop_name].expression is None:
                source = None
                if selected:
                    source = f"self.{qualified}" if selected == selected_keys[key][1] else repr(selected[0].value)
                namespace[prop_name] = Property(source, unit)
                bindings.append(CatalogBinding(prop_name, key[0], key[1], selected))
        namespace["catalog_bindings"] = tuple(bindings)
        if issubclass(product.model_class, Protection):
            protections = {
                "autonomous_undervoltage_protection": "undervoltage_threshold",
                "autonomous_overvoltage_protection": "overvoltage_threshold",
                "autonomous_overcurrent_protection": "current_limit",
            }
            trips = tuple(parameter for feature, parameter in protections.items() if any(
                fact.element_id == "self" and fact.parameter == feature and fact.value is True for fact in product.facts))
            if trips:
                namespace["trip_parameters"] = trips
        cls_name = "__".join((product.product_id, role.__name__, element_id))
        return type(cls_name, (product.model_class, COTS), namespace)

    def candidates(self, component, *, condition_id="", element_id=None, value_kinds=None):
        condition_id = condition_id or ""
        if condition_id and condition_id not in self.conditions:
            raise ValueError(f"Unknown catalog condition {condition_id!r}.")
        roles = tuple(cls for cls in (*EPS.default_components, Protection) if isinstance(component, cls))
        roles = tuple(cls for cls in roles if not any(other is not cls and issubclass(other, cls) for other in roles))
        required = roles + tuple(cls for cls in type(component).__mro__ if cls.__dict__.get("catalog_type") is cls)
        for product in self.products.values():
            if required and not all(issubclass(product.model_class, role) for role in required):
                continue
            views = roles or tuple(cls for cls in EPS.default_components if issubclass(product.model_class, cls))
            for role in views:
                channels = {"self"}
                if issubclass(product.model_class, IntegratedEPS):
                    channels = {fact.element_id for fact in product.facts if fact.value is not None and fact.model_class
                                and fact.model_class in self._templates and issubclass(role, type(self._templates[fact.model_class]))}
                    if role.__name__ == "PowerCircuit":
                        channels = {element for (pid, element), row in self.elements.items() if pid == product.product_id
                                    and row["element_kind"] in ("rail", "channel", "solar_input", "battery_interface", "supply_pin_group")}
                    channels = channels or {"self"}
                if element_id is not None:
                    channels &= {element_id}
                for channel in sorted(channels):
                    candidate = self.product(product.product_id, model_class=role, element_id=channel,
                                             condition_id=condition_id, value_kinds=value_kinds)
                    if component.accepts(candidate):
                        yield candidate


@lru_cache(maxsize=1)
def load_catalog():
    return Catalog(Path(__file__).resolve().parent)
