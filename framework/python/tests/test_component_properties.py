"""Typed properties, authoritative assignments and polymorphic COTS checks."""

import copy
import csv
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

from nanosat_mbse import (
    Battery, ComponentProperty, CotsBattery, CotsSolarArray, CubeSat, EPS,
    FactReference, NormalInterval, Parameter, PendingValue, PropertySource,
    Requirement, Session, SolarArray, VerificationMethod, all_assigned,
)
from nanosat_mbse.catalogs.cots import (
    CotsIntegratedBatteryEPS, CotsIntegratedEPS, PRODUCT_CLASSES,
    component_for_product, product_type,
)
from nanosat_mbse.catalogs.database import Fact, ProductRecord, TabularDatabase, digest
from nanosat_mbse.core.execution import InlineRunner
from nanosat_mbse.core.properties import PROPERTY_TYPES
from nanosat_mbse.persistence import CallableRegistry, dumps, loads
from nanosat_mbse.service.application import Application
from nanosat_mbse.service.edits import apply_projection, validate_graph
from nanosat_mbse.service.validation import validate_projection
from nanosat_mbse.service.views import describe


# This combination is test evidence only. No fictional product is added to TSVs.
@product_type("EPSModel::TestBatteryArray")
class BatteryArrayFixture(CotsBattery, CotsSolarArray):
    pass


def native_voltage_check(values):
    return all_assigned(values, Battery, "nominal_voltage", "==", "target")


class MemoryDatabase:
    def __init__(self):
        self.records = {record.id: record for record in TabularDatabase().products()}
        facts = tuple(
            Fact(
                digest(["test_battery_array", name]), digest([name, value]),
                name, "self", "parameter", "float", unit, "nominal", value,
                MappingProxyType({"id": "test_condition", "values": {}, "parameters": ()}),
                MappingProxyType({"id": "test_source", "locator": "synthetic fixture"}),
            )
            for name, value, unit in (
                ("nominal_voltage", 3.6, "V"), ("rated_energy", 10., "Wh"),
                ("maximum_power", 2., "W"),
            )
        )
        self.records["test_battery_array"] = ProductRecord(
            "test_battery_array", "EPSModel::TestBatteryArray", "Test", "Fixture", "",
            facts, (), MappingProxyType({}),
        )

    def products(self):
        return tuple(self.records.values())

    def product(self, identity):
        return self.records.get(identity)


class ComponentPropertyTests(unittest.TestCase):
    def setUp(self):
        self.database = MemoryDatabase()
        self.session = Session(database=self.database)
        bus = self.session.add(CubeSat("BUS"), initialize=False)
        self.eps = self.session.add(EPS("EPS"), owner=bus, initialize=False)

    def add(self, component):
        return self.session.add(component, owner=self.eps, initialize=False)

    def cots(self, product="molicel_inr_18650_p26a", **kwargs):
        return self.add(component_for_product(product, database=self.database, **kwargs))

    def fact(self, component, name, **filters):
        matches = [fact for fact in component.product_record.facts if fact.name == name and all(
            (fact.condition["id"] if key == "condition" else getattr(fact, key)) == value
            for key, value in filters.items()
        )]
        self.assertEqual(len(matches), 1, (name, filters))
        return matches[0]

    def requirement(self, condition, value=3.6, unit="V", kind=float):
        row = Requirement(
            f"CHK{len(self.session.requirements) + 1:03}",
            "The assigned components shall meet $$target$$.",
            parameters=(Parameter("target", kind, unit, value=value),),
            verifications=(VerificationMethod("assigned properties", condition),),
        )
        return self.session.add(row, owner=self.eps, initialize=False)

    def state(self, row):
        return row.verify().state.value

    def test_declared_contracts_match_tsv_types_and_units(self):
        with (Path(__file__).parents[2] / "cots/definitions.tsv").open() as source:
            definitions = {(row["definition_kind"], row["name"]): row for row in csv.DictReader(source, delimiter="\t")}
        types = {float: "Real", int: "Integer", bool: "Boolean", str: "String"}
        for cls in PROPERTY_TYPES.values():
            for name, spec in cls.property_definitions().items():
                kind = "parameter" if spec.value_type in (int, float) else "feature"
                with self.subTest(component=cls.__name__, property=name):
                    definition = definitions[kind, name]
                    self.assertEqual(definition["scalar_type"], types[spec.value_type])
                    self.assertEqual(definition["canonical_unit"], spec.unit)
        for name, alias in (("rated_energy", "battery_energy"), ("rated_capacity", "battery_capacity")):
            self.assertEqual(CotsIntegratedBatteryEPS.property_source(name), PropertySource(alias, "battery"))

    def test_generic_properties_are_typed_owned_and_optional(self):
        first, second = Battery(), Battery()
        with self.assertRaises(PendingValue):
            _ = first.rated_energy
        first.rated_energy = 10
        self.assertEqual(first.rated_energy, 10)
        self.assertEqual(first.property_values, {"rated_energy": 10})
        self.assertEqual(second.property_values, {})
        self.assertIs(Battery.rated_energy.value_type, float)
        for value in ("10", True, float("inf")):
            with self.subTest(value=value), self.assertRaises((ValueError, TypeError)):
                first.rated_energy = value
        with self.assertRaises(ValueError):
            first.set_property("invented", 1)
        with self.assertRaises(TypeError):
            first.property_values["rated_energy"] = 12
        first.rated_energy = None
        with self.assertRaises(PendingValue):
            _ = first.rated_energy

    def test_incompatible_property_override_rejects_a_broken_generic_contract(self):
        class IncompatibleBattery(Battery):
            rated_energy = ComponentProperty(unit="J")

        with self.assertRaises(TypeError):
            IncompatibleBattery.property_definitions()

    def test_cots_properties_resolve_pins_without_literal_copies(self):
        component = self.cots()
        with self.assertRaises(PendingValue):
            _ = component.rated_energy
        with self.assertRaises(TypeError):
            component.rated_energy = 9.5
        fact = self.fact(component, "rated_energy")
        reference = component.select_property("rated_energy", fact)
        self.assertEqual(component.rated_energy, 9.5)
        self.assertEqual(component.property_values, {})
        self.assertEqual(reference.fact, fact.id)
        self.assertNotIn("value", reference.projection())
        self.assertEqual(self.session.value(component, "rated_energy"), 9.5)
        row = self.requirement(f"{component.id}.rated_energy == target", 9.5, "Wh")
        self.assertEqual(self.state(row), "pass")

    def test_property_selection_rejects_wrong_source_type_scope_and_unit(self):
        component = self.cots()
        fact = self.fact(component, "rated_energy")
        for invalid in (
            replace(fact, name="mass"), replace(fact, element="battery"),
            replace(fact, type="integer"), replace(fact, unit="J"), replace(fact, kind="feature"),
        ):
            self.database.records[component.product] = replace(component.product_record, facts=(invalid,))
            with self.subTest(fact=invalid), self.assertRaises(ValueError):
                component.select_property("rated_energy", invalid)
            self.assertFalse(component.facts)
        with self.assertRaises(ValueError):
            component.select_property("invented", fact)

    def test_unreviewed_or_changed_properties_are_pending(self):
        component = self.cots()
        fact = self.fact(component, "nominal_voltage")
        component.select_property("nominal_voltage", fact)
        row = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        component.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        record = component.product_record
        revised = replace(fact, revision="f" * 64, value=4.)
        self.database.records[record.id] = replace(record, facts=tuple(revised if item.id == fact.id else item for item in record.facts))
        self.assertEqual(self.state(row), "pending")
        with self.assertRaises(PendingValue):
            _ = component.nominal_voltage
        component.select_property("nominal_voltage", revised)
        self.assertEqual(self.state(row), "fail")
        self.database.records.pop(record.id)
        self.assertEqual(self.state(row), "pending")

    def test_imported_wrong_typed_reference_remains_pending(self):
        component = self.cots()
        fact = self.fact(component, "rated_energy")
        component.facts = (FactReference.select("nominal_voltage", fact),)
        row = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        component.assign_to(row)
        self.assertEqual(self.state(row), "pending")
        with self.assertRaises(ValueError):
            self.session.configure_facts(component, (FactReference.select("rated_capacity", fact),))

    def test_assignments_have_one_authority_and_deduplicate(self):
        component = self.add(Battery(property_values={"nominal_voltage": 3.6}))
        row = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        row.assign_component(component)
        component.assign_to(row, row)
        self.assertEqual(component.requirement_links, (row,))
        self.assertEqual(row.assigned_components(Battery), (component,))
        self.assertEqual(row.assigned_components("Battery"), (component,))
        self.assertEqual(row.affected, ())
        self.assertEqual(self.state(row), "pass")
        row.unassign_component(component)
        self.assertEqual(row.assigned_components(), ())
        self.assertEqual(self.state(row), "pending")

    def test_affected_scope_does_not_create_verification_assignments(self):
        component = self.add(Battery(property_values={"nominal_voltage": 3.6}))
        row = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        row.assign_to(component)
        self.assertEqual(row.affected, (component,))
        self.assertEqual(self.state(row), "pending")

    def test_assignment_validation_and_deletion_protection(self):
        component = self.add(Battery())
        row = self.requirement("True")
        component.assign_to(row)
        with self.assertRaises(ValueError):
            self.session.remove(row)
        foreign = Session().add(Requirement("F1", "Value $$target$$."))
        with self.assertRaises(KeyError):
            component.assign_to(foreign)
        self.assertEqual(component.requirement_links, (row,))
        detached = Battery(requirement_links=(foreign,))
        with self.assertRaises(KeyError):
            self.add(detached)

    def test_type_filters_ignore_unassigned_and_other_types(self):
        battery = self.add(Battery(property_values={"nominal_voltage": 3.6}))
        self.add(Battery())
        array = self.add(SolarArray())
        row = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        battery.assign_to(row)
        array.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        self.assertEqual(row.assigned_components(Battery), (battery,))

    def test_all_checks_every_assignment_and_does_not_use_quantity(self):
        first = self.add(Battery(quantity=20, property_values={"nominal_voltage": 3.6}))
        second = self.add(Battery(property_values={"nominal_voltage": 3.7}))
        third = self.add(Battery())
        row = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        first.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        second.assign_to(row)
        self.assertEqual(self.state(row), "fail")
        third.assign_to(row)
        self.assertEqual(self.state(row), "pending")

    def test_weighted_sum_and_target_unit_conversion(self):
        first = self.add(Battery(quantity=2, property_values={"rated_energy": 10}))
        second = self.add(Battery(quantity=3, property_values={"rated_energy": 5}))
        row = self.requirement('sum_assigned("Battery", "rated_energy", "==", target)', 35 * 3600, "J")
        first.assign_to(row)
        second.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        second.quantity = 4
        self.assertEqual(self.state(row), "fail")
        row.set_value("target", 40 * 3600)
        self.assertEqual(self.state(row), "pass")

    def test_empty_sum_and_missing_property_are_pending(self):
        row = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target)', 0, "W")
        self.assertEqual(self.state(row), "pending")
        array = self.add(SolarArray())
        array.assign_to(row)
        self.assertEqual(self.state(row), "pending")
        array.maximum_power = 0
        self.assertEqual(self.state(row), "pass")

    def test_cots_solar_sum_uses_selected_conditions_and_quantity(self):
        array = self.cots("azur_space_81441", quantity=2)
        fact = self.fact(array, "maximum_power", condition="solar_bol_am0_t301p15_g1367")
        array.select_property("maximum_power", fact)
        row = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target)', 2 * fact.value, "W")
        array.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        eol = self.fact(array, "maximum_power", condition="solar_eol_am0_e1mev_f1e15cm2_anneal_unspecified_t301p15_g1367")
        array.select_property("maximum_power", eol)
        self.assertEqual(self.state(row), "fail")

    def test_quantity_validation(self):
        for quantity in (True, 0, -1, 1.5, "2", float("inf"), 9007199254740992):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                Battery(quantity=quantity)

    def test_numeric_comparison_operators(self):
        component = self.add(Battery(property_values={"nominal_voltage": 3.6}))
        for comparison, target, expected in (
            ("==", 3.6, "pass"), ("!=", 3.6, "fail"),
            ("<", 4., "pass"), ("<=", 3.6, "pass"),
            (">", 3.5, "pass"), (">=", 3.6, "pass"),
        ):
            row = self.requirement(f'all_assigned("Battery", "nominal_voltage", "{comparison}", target)', target)
            component.assign_to(row)
            self.assertEqual(self.state(row), expected)

    def test_equality_has_explicit_tolerances_in_target_units(self):
        first = self.add(SolarArray(property_values={"maximum_power": .1}))
        second = self.add(SolarArray(property_values={"maximum_power": .2}))
        strict = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target)', .3, "W")
        tolerant = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target, abs_tol=0.000001)', .3, "W")
        relative = self.requirement('all_assigned("SolarArray", "maximum_power", "==", target, rel_tol=0.01)', .101, "W")
        for component in (first, second):
            component.assign_to(strict, tolerant)
        first.assign_to(relative)
        self.assertEqual(self.state(strict), "fail")
        self.assertEqual(self.state(tolerant), "pass")
        self.assertEqual(self.state(relative), "pass")

    def test_string_and_boolean_properties(self):
        component = self.add(Battery(property_values={"chemistry": "Li-ion", "heater_included": False}))
        for name, value, kind in (("chemistry", "Li-ion", str), ("heater_included", False, bool)):
            row = self.requirement(f'all_assigned("Battery", "{name}", "==", target)', value, "", kind)
            component.assign_to(row)
            self.assertEqual(self.state(row), "pass")

    def test_units_types_targets_and_expression_shapes_are_validated(self):
        component = self.add(Battery(property_values={"nominal_voltage": 3.6, "heater_included": True}))
        invalid = (
            ('all_assigned("Battery", "nominal_voltage", "==", target)', "W", float),
            ('all_assigned("Battery", "nominal_voltage", "==", target)', "", float),
            ('all_assigned("Battery", "nominal_voltage", "==", target)', "V", bool),
            ('sum_assigned("Battery", "heater_included", "==", target)', "", bool),
            ('all_assigned("Battery", "invented", "==", target)', "V", float),
            ('all_assigned("NotAType", "nominal_voltage", "==", target)', "V", float),
            ('all_assigned("Battery", "nominal_voltage", "is", target)', "V", float),
            ('all_assigned("Battery", "nominal_voltage", "==", 3.6)', "V", float),
            ('all_assigned("Battery", "nominal_voltage", "==", "target")', "V", float),
            ('all_assigned("Battery", "nominal_voltage", "==", unknown)', "V", float),
            ('all_assigned("Battery", "nominal_voltage", "==", target, abs_tol=-1)', "V", float),
            ('all_assigned("Battery", "nominal_voltage", ">=", target, abs_tol=1)', "V", float),
            ('all_assigned("Battery", "nominal_voltage", "==", target, unsupported=1)', "V", float),
        )
        for expression, unit, kind in invalid:
            with self.subTest(expression=expression, unit=unit, kind=kind):
                row = self.requirement(expression, True if kind is bool else 3.6, unit, kind)
                component.assign_to(row)
                self.assertEqual(self.state(row), "error")

    def test_temperature_conversion_and_offset_sum_rejection(self):
        component = self.add(Battery(property_values={"operating_temperature_max": 298.15}))
        row = self.requirement('all_assigned("Battery", "operating_temperature_max", "==", target)', 25, "degC")
        component.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        row.verifications = (VerificationMethod("sum", 'sum_assigned("Battery", "operating_temperature_max", "==", target)'),)
        self.assertEqual(self.state(row), "error")

    def test_native_functions_use_the_same_assignment_context(self):
        component = self.add(Battery(property_values={"nominal_voltage": 3.6}))
        row = self.requirement(native_voltage_check)
        component.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        context = self.session.evaluation_context()
        from nanosat_mbse.core.evaluation import NativeValues
        self.assertTrue(NativeValues(context, row).all_assigned(Battery, "nominal_voltage", "==", "target"))
        restored = loads(dumps(self.session), database=self.database)
        self.assertEqual(restored.verify(row.id).state.value, "pass")

    def test_battery_array_multiple_inheritance_resolves_both_filters_once(self):
        component = self.cots("test_battery_array", quantity=3)
        self.assertIsInstance(component, Battery)
        self.assertIsInstance(component, SolarArray)
        for name in ("nominal_voltage", "rated_energy", "maximum_power"):
            component.select_property(name, self.fact(component, name))
        battery_check = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target)')
        array_check = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target)', 6, "W")
        battery_sum = self.requirement('sum_assigned("Battery", "rated_energy", "==", target)', 30, "Wh")
        component.assign_to(battery_check, array_check, battery_sum)
        self.assertEqual(len(component.facts), 3)
        for row, cls in ((battery_check, Battery), (array_check, SolarArray), (battery_sum, Battery)):
            self.assertEqual(row.assigned_components(cls), (component,))
            self.assertEqual(self.state(row), "pass")
        self.assertEqual(self.session.cots_components, (component,))

    def test_combined_cots_round_trips_preserve_actual_inheritance_and_pins(self):
        component = self.cots("test_battery_array", quantity=2)
        component.select_property("maximum_power", self.fact(component, "maximum_power"))
        row = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target)', 4, "W")
        component.assign_to(row)
        projection = self.session.to_projection()
        validate_projection(projection)
        source = dumps(self.session)
        self.assertIn("BatteryArrayFixture.restore", source)
        self.assertNotIn("synthetic fixture", source)
        for restored in (
            loads(source, database=self.database),
            Session.from_projection(projection, database=self.database),
            apply_projection(self.session, projection, callables=CallableRegistry()),
        ):
            selected = restored.get(component.key)
            self.assertIsInstance(selected, Battery)
            self.assertIsInstance(selected, SolarArray)
            self.assertEqual(selected.quantity, 2)
            self.assertEqual(selected.facts, component.facts)
            self.assertEqual(restored.verify(row.key).state.value, "pass")

    def test_existing_integrated_products_only_expose_encountered_functions(self):
        for product in ("isispace_iceps2_type_a", "isispace_imeps2_base_4s1p"):
            component = self.cots(product)
            self.assertIsInstance(component, CotsIntegratedEPS)
            self.assertIsInstance(component, Battery)
            self.assertNotIsInstance(component, SolarArray)
            fact = self.fact(component, "battery_capacity", element="battery")
            component.select_property("rated_capacity", fact)
            row = self.requirement('all_assigned("Battery", "rated_capacity", "==", target)', 3.2, "Ah")
            component.assign_to(row)
            self.assertEqual(self.state(row), "pass")
            if product == "isispace_imeps2_base_4s1p":
                component.select_property("rated_energy", self.fact(component, "battery_energy", element="battery"))
                self.assertEqual(component.rated_energy, 45)
            else:
                with self.assertRaises(PendingValue):
                    _ = component.rated_energy
        pumpkin = self.cots("pumpkin_epsm1_rev_c")
        self.assertNotIsInstance(pumpkin, Battery)
        self.assertNotIsInstance(pumpkin, SolarArray)
        actual_products = {record.id for record in TabularDatabase().products()}
        self.assertTrue(set(PRODUCT_CLASSES) <= actual_products)
        with self.assertRaises(ValueError):
            CotsIntegratedBatteryEPS(product="pumpkin_epsm1_rev_c", database=self.database)

    def test_combined_products_seed_requirements_without_assigning_cots_to_affected_scope(self):
        component = component_for_product("isispace_imeps2_base_4s1p", database=self.database)
        self.session.add(component, owner=self.eps)
        self.assertTrue(component.requirement_links)
        self.assertTrue(any(row.template.name == "BatteryCapacityScreen" for row in component.requirement_links))
        self.assertTrue(all(not row.affected for row in component.requirement_links))
        validate_graph(self.session)

    def test_existing_family_instance_can_accept_a_newly_registered_combination(self):
        component = self.add(CotsIntegratedEPS(
            product="isispace_imeps2_base_4s1p", database=self.database,
        ))
        self.assertNotIsInstance(component, Battery)
        component.select_fact("rated_energy", self.fact(component, "battery_energy", element="battery"))
        pins = component.facts
        self.session.substitute_product(component, component.product)
        self.assertIsInstance(component, CotsIntegratedBatteryEPS)
        self.assertEqual(component.facts, pins)
        self.assertEqual(component.rated_energy, 45)

    def test_retyping_protects_property_configuration_and_assignments(self):
        component = self.add(Battery(property_values={"rated_energy": 10}))
        with self.assertRaises(ValueError):
            self.session.retype(component, SolarArray.model)
        component.rated_energy = None
        component.assign_to(self.requirement("True"))
        with self.assertRaises(ValueError):
            self.session.retype(component, SolarArray.model)
        self.assertIsInstance(component, Battery)

    def test_product_substitution_changes_inheritance_and_keeps_pins_pending(self):
        component = self.cots()
        component.select_property("rated_energy", self.fact(component, "rated_energy"))
        row = self.requirement('sum_assigned("Battery", "rated_energy", ">=", target)', 1, "Wh")
        component.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        self.session.substitute_product(component, "test_battery_array")
        self.assertIsInstance(component, SolarArray)
        self.assertEqual(self.state(row), "pending")
        component.select_property("rated_energy", self.fact(component, "rated_energy"))
        self.assertEqual(self.state(row), "pass")

    def test_generic_property_and_assignment_metadata_round_trip_and_edit(self):
        component = self.add(Battery(property_values={"rated_energy": 10}, quantity=2))
        row = self.requirement('sum_assigned("Battery", "rated_energy", "==", target)', 20, "Wh")
        component.assign_to(row)
        projection = self.session.to_projection()
        validate_projection(projection)
        for restored in (loads(dumps(self.session), database=self.database), Session.from_projection(projection, database=self.database)):
            self.assertEqual(restored.get(component.key).property_values, {"rated_energy": 10})
            self.assertEqual(restored.verify(row.key).state.value, "pass")
        edited = copy.deepcopy(projection)
        edited["modelState"]["componentProperties"][component.key]["rated_energy"] = 5
        edited["modelState"]["componentAssignments"][component.key]["quantity"] = 4
        changed = apply_projection(self.session, edited, callables=CallableRegistry())
        self.assertEqual(changed.verify(row.key).state.value, "pass")
        self.assertEqual(changed.get(component.key).rated_energy, 5)
        edited["modelState"]["componentAssignments"][component.key]["requirements"] = []
        changed = apply_projection(self.session, edited, callables=CallableRegistry())
        self.assertEqual(changed.verify(row.key).state.value, "pending")
        self.assertEqual(self.state(row), "pass")

    def test_cots_quantity_and_assignment_edits_use_existing_transport(self):
        component = self.cots("test_battery_array")
        component.select_property("maximum_power", self.fact(component, "maximum_power"))
        row = self.requirement('sum_assigned("SolarArray", "maximum_power", "==", target)', 6, "W")
        projection = self.session.to_projection()
        selected = next(item for item in projection["components"] if item["key"] == component.key)
        selected["quantity"] = 3
        selected["requirements"] = [row.key]
        changed = apply_projection(self.session, projection, callables=CallableRegistry())
        self.assertEqual(changed.verify(row.key).state.value, "pass")
        self.assertEqual(changed.get(row.key).assigned_components(Battery), (changed.get(component.key),))

    def test_transport_rejects_cots_literal_properties_and_duplicate_assignment_storage(self):
        component = self.cots()
        for field, value in (("componentProperties", {"rated_energy": 99}), ("componentAssignments", {"quantity": 3, "requirements": []})):
            data = self.session.to_projection()
            data["modelState"][field][component.key] = value
            with self.subTest(field=field), self.assertRaises((ValueError, TypeError)):
                apply_projection(self.session, data, callables=CallableRegistry())
            with self.assertRaises((ValueError, TypeError)):
                Session.from_projection(data, database=self.database)

    def test_assignment_configuration_invalidates_execution_evidence(self):
        component = self.add(Battery(property_values={"rated_energy": 10}))
        row = self.requirement("True")
        script = self.session.add(NormalInterval("SCR001"))
        script.set_value("mean", 4)
        script.set_value("standard_deviation", 1)
        script.set_value("confidence", .95)
        for change in (
            lambda: component.set_property("rated_energy", 11),
            lambda: setattr(component, "quantity", 2),
            lambda: component.assign_to(row),
        ):
            self.session.run(script, runner=InlineRunner())
            self.assertIsInstance(script.value("upper"), float)
            change()
            with self.assertRaises(PendingValue):
                script.value("upper")

    def test_no_more_than_four_cots_batteries_includes_combined_subclasses(self):
        row = self.session.add(Requirement(
            "CNT001",
            "No more than $$max_batteries$$ COTS Batteries shall be assigned to this requirement.",
            parameters=(Parameter("max_batteries", int, "1", value=4),),
            verifications=(VerificationMethod(
                "Assigned COTS battery count",
                'count_assigned("Battery", cots_only=True) <= max_batteries',
            ),),
        ), owner=self.eps, initialize=False)
        self.assertEqual(self.state(row), "pass")
        for _ in range(3):
            self.cots().assign_to(row)
        combined = self.cots("test_battery_array")
        combined.assign_to(row, row)
        self.add(Battery()).assign_to(row)
        self.cots("azur_space_81441").assign_to(row)
        self.cots()  # An unassigned fifth COTS battery is outside the selection.
        self.assertEqual(len(row.assigned_components(Battery, cots_only=True)), 4)
        self.assertEqual(self.state(row), "pass")
        fifth = self.cots()
        fifth.assign_to(row)
        self.assertEqual(self.state(row), "fail")
        for restored in (
            loads(dumps(self.session), database=self.database),
            Session.from_projection(self.session.to_projection(), database=self.database),
        ):
            self.assertEqual(restored.verify(row.key).state.value, "fail")
        row.unassign_component(fifth)
        self.assertEqual(self.state(row), "pass")
        row.set_value("max_batteries", None)
        self.assertEqual(self.state(row), "pending")

    def test_assignment_count_distinguishes_entries_from_represented_units(self):
        row = self.requirement('count_assigned("Battery", cots_only=True) <= target', 4, "1", int)
        battery = self.cots(quantity=5)
        battery.assign_to(row)
        self.assertEqual(self.state(row), "pass")
        row.verifications = (VerificationMethod("unit count", 'count_assigned("Battery", cots_only=True, by_quantity=True) <= target'),)
        self.assertEqual(self.state(row), "fail")
        self.add(Battery()).assign_to(row)
        row.verifications = (VerificationMethod("all entries", 'count_assigned("Battery") == target'),)
        row.set_value("target", 2)
        self.assertEqual(self.state(row), "pass")

    def test_unresolved_product_types_cannot_disappear_from_count_filters(self):
        component = self.cots()
        row = self.requirement('count_assigned("Battery", cots_only=True) <= target', 4, "1", int)
        component.assign_to(row)
        projection = self.session.to_projection()
        self.database.records.pop(component.product)
        restored = Session.from_projection(projection, database=self.database)
        self.assertEqual(restored.verify(row.key).state.value, "pending")

    def test_standalone_native_assignment_check_requests_a_session(self):
        row = Requirement("STANDALONE", "Voltage $$target$$.",
                          parameters=(Parameter("target", unit="V", value=3.6),),
                          verifications=(VerificationMethod("native", native_voltage_check),))
        self.assertEqual(row.verify().state.value, "pending")

    def test_native_service_commands_edit_properties_assignments_and_pins(self):
        battery = self.add(Battery(property_values={"rated_energy": 10}))
        row = self.requirement('sum_assigned("Battery", "rated_energy", "==", target)', 20, "Wh")
        voltage = self.requirement('all_assigned("Battery", "nominal_voltage", "==", target, cots_only=True)')
        with tempfile.TemporaryDirectory() as directory:
            app = Application(Path(directory) / "current.py")
            view = app.create_session(self.session, name="Assigned property checks")
            def command(operation):
                nonlocal view
                view = app.command({"handle": view["handle"], "command": operation})
                return view

            command({"name": "configure_component", "target": battery.key, "quantity": 2, "requirements": [row.key]})
            result = app.evaluate({"handle": view["handle"]})
            self.assertEqual(next(item for item in result["results"] if item["key"] == row.key)["state"], "pass")
            command({"name": "set_property", "target": battery.key, "property": "rated_energy", "value": 11})
            self.assertEqual(view["workspace"]["modelState"]["componentProperties"][battery.key]["rated_energy"], 11)
            command({"name": "add_cots", "product": "molicel_inr_18650_p26a", "owner": self.eps.key, "key": "service-battery"})
            command({"name": "configure_component", "target": "service-battery", "quantity": 3, "requirements": [voltage.key]})
            reference = next(fact for fact in self.database.product("molicel_inr_18650_p26a").facts if fact.name == "nominal_voltage")
            command({"name": "select_fact", "target": "service-battery", "fact": reference.id})
            selected = next(item for item in view["workspace"]["components"] if item["key"] == "service-battery")
            self.assertEqual(selected["quantity"], 3)
            self.assertEqual(selected["facts"][0]["name"], "nominal_voltage")
            result = app.evaluate({"handle": view["handle"]})
            self.assertEqual(next(item for item in result["results"] if item["key"] == voltage.key)["state"], "pass")

    def test_assignment_count_validates_type_and_boolean_options(self):
        for condition in (
            'count_assigned("Unknown") <= target',
            'count_assigned("Battery", cots_only=1) <= target',
            'count_assigned("Battery", by_quantity="yes") <= target',
            'count_assigned("Battery", invented=True) <= target',
            'count_assigned(target) <= target',
        ):
            with self.subTest(condition=condition):
                row = self.requirement(condition, 4, "1", int)
                self.assertEqual(self.state(row), "error")

    def test_metadata_describes_both_generic_types_and_canonical_sources(self):
        component = self.cots("test_battery_array")
        metadata = describe(self.session)
        self.assertIn("Battery", metadata["objects"][component.key]["genericTypes"])
        self.assertIn("SolarArray", metadata["objects"][component.key]["genericTypes"])
        self.assertEqual(metadata["assignmentFunctions"], ["all_assigned", "sum_assigned", "count_assigned"])
        self.assertTrue(any(item["name"] == "maximum_power" and item["unit"] == "W" for item in metadata["propertyTypes"]["SolarArray"]))


if __name__ == "__main__":
    unittest.main()
