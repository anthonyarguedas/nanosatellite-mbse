"""Component-owned budgets and the existing requirement editing workflow."""

import copy
import tempfile
import unittest
from pathlib import Path

from nanosat_mbse import Battery, ComponentState, CotsBattery, CubeSat, NormalInterval, Parameter, PowerLoss, Requirement, Session
from nanosat_mbse.core.elements import Component
from nanosat_mbse.core.execution import InlineRunner
from nanosat_mbse.core.predicates import PendingValue
from nanosat_mbse.domains.budgets import (
    ComponentMassLimit, ComponentPowerLimit, RESOURCES,
    power_limit_for, resource_limit_for,
)
from nanosat_mbse.domains.components import ProcessorAndMemory
from nanosat_mbse.domains.eps import EPS
from nanosat_mbse.domains.mission import CommandAndDataHandling
from nanosat_mbse.persistence import dumps, loads
from nanosat_mbse.persistence.callables import CallableRegistry
from nanosat_mbse.service.application import Application
from nanosat_mbse.service.edits import apply_projection
from nanosat_mbse.service.validation import validate_projection
from nanosat_mbse.service.views import describe


def legacy_power(values):
    return values["power_limit_W"] / 2


class ComponentBudgetTests(unittest.TestCase):
    def setUp(self):
        self.session = s = Session()
        bus = s.add(CubeSat("BUS"), initialize=False)
        self.cdh = s.add(CommandAndDataHandling("CDH"), owner=bus, initialize=False)
        self.eps = s.add(EPS("EPS"), owner=bus, initialize=False)
        self.cpu = s.add(ProcessorAndMemory("CPU"), owner=self.cdh, initialize=False)
        self.battery = s.add(Battery("BAT"), owner=self.eps, initialize=False)
        s.remember_component_defaults(self.cpu)
        s.remember_component_defaults(self.battery)
        self.nominal = s.add_mode("Nominal", sunlight=60, eclipse=20)
        self.passed = s.add_mode("Pass", sunlight=40, eclipse=80)
        s.seed_resource_budgets()
        self.power = power_limit_for(s, self.cpu)
        self.root = power_limit_for(s, s.mission)

    def resource(self, component, name):
        resource = next(item for item in RESOURCES if item.name == name)
        return resource_limit_for(self.session, component, resource)

    def connect(self):
        row = self.session.add(Requirement(
            "LOD001", "Load inputs.", owner=self.eps,
            definition="FrameworkRequirements::LoadEnergy",
            parameters=tuple(Parameter(name, value=value) for name, value in (
                ("sunlight_power_W", 0), ("eclipse_power_W", 0),
                ("sunlight_duty", 1), ("eclipse_duty", 1),
                ("sunlight_s", None), ("eclipse_s", None),
                ("sunlight_energy_J", None), ("eclipse_energy_J", None),
            )),
        ), initialize=False)
        self.session.connect_power(self.eps)
        return row

    def value(self, row, field, mode=None):
        return self.session.value(row, field, mode=mode or self.nominal)

    def test_cdh_and_eps_share_budget_inputs_and_remain_components(self):
        for component in (self.cpu, self.battery):
            self.assertIsInstance(component, Component)
            self.assertNotIsInstance(component, Requirement)
            self.assertEqual(set(component.parameters), {"mass_kg", "volume_m3", "draw_power_W", "average_power_W"})
            row = self.resource(component, "mass")
            self.assertIsInstance(row, ComponentMassLimit)
            self.assertEqual(row.parameters["mass_kg"].expression, f"{component.id}.mass_kg")
        self.assertIsInstance(self.power, ComponentPowerLimit)
        self.assertIsNone(power_limit_for(self.session, self.battery))

    def test_existing_requirement_setters_update_the_component_without_a_copy(self):
        self.power.set_value("draw_power_W", 10)
        self.assertEqual(self.cpu.parameters["draw_power_W"].value, 10)
        self.assertEqual(self.power.parameters["draw_power_W"].expression, "CPU.draw_power_W")
        self.assertEqual(self.value(self.power, "average_power_W"), 10)
        self.power.set_expression("average_power_W", "draw_power_W * 0.2")
        self.assertEqual(self.value(self.power, "average_power_W"), 2)
        self.power.set_value("power_limit_W", 8)
        self.assertEqual(self.power.verify(mode=self.nominal).state.value, "fail")

    def test_requirement_auxiliary_names_retain_their_context(self):
        self.power.add_parameter(Parameter("duty", value=0.2))
        self.cpu.set_value("draw_power_W", 10)
        self.power.set_expression("average_power_W", "draw_power_W * duty")
        self.assertEqual(self.cpu.parameters["average_power_W"].expression, f"draw_power_W * {self.power.id}.duty")
        self.assertEqual(self.value(self.power, "average_power_W"), 2)
        self.power.set_expression("average_power_W", "sum(duty for duty in range(3)) + duty")
        self.assertEqual(self.value(self.power, "average_power_W"), 3.2)
        with self.assertRaisesRegex(ValueError, "used by an expression"):
            self.session.remove(self.power)

    def test_mode_inputs_use_the_existing_requirement_state_selector(self):
        self.session.configure_parameter_states(self.power, "draw_power_W", values={self.nominal.key: "10", self.passed.key: "20"})
        self.assertEqual(self.value(self.cpu, "draw_power_W"), 10)
        self.assertEqual(self.value(self.cpu, "draw_power_W", self.passed), 20)
        self.assertEqual(self.power.parameters["draw_power_W"].expression, "CPU.draw_power_W")
        result = next(row for row in self.session.evaluate()["results"] if row["key"] == self.power.key)
        self.assertEqual(result["parameters"]["draw_power_W"]["branches"]["values"][self.nominal.key], "10")

    def test_eps_and_case_energy_use_average_draw_and_include_losses_once(self):
        self.cpu.set_expression("draw_power_W", '10 if mode == "Nominal" else 20')
        self.cpu.set_expression("average_power_W", "draw_power_W * 0.2 + 0.1")
        self.root.set_value("assessment_duration_s", 3600)
        load = self.connect()
        self.assertAlmostEqual(self.value(load, "sunlight_power_W"), 2.9)
        self.assertAlmostEqual(self.value(load, "eclipse_power_W"), 3.7)
        self.assertAlmostEqual(self.value(self.root, "energy_Wh"), 2.1)
        self.assertEqual(self.value(self.root, "draw_power_W"), 10)

    def test_mass_and_volume_include_all_hardware_and_count_each_component_once(self):
        for component, mass, volume in ((self.cpu, .3, .00002), (self.battery, 1.2, .0001)):
            component.set_value("mass_kg", mass)
            component.set_value("volume_m3", volume)
        self.assertAlmostEqual(self.value(self.resource(self.session.mission, "mass"), "mass_kg"), 1.5)
        self.assertAlmostEqual(self.value(self.resource(self.session.mission, "volume"), "volume_m3"), .00012)
        self.assertAlmostEqual(self.value(self.resource(self.eps, "mass"), "mass_kg"), 1.2)

    def test_installed_contribution_is_distinct_from_unit_product_mass(self):
        self.battery.mass = .4
        self.battery.set_expression("mass_kg", "BAT.mass * 2 + 0.1")
        self.assertAlmostEqual(self.value(self.resource(self.battery, "mass"), "mass_kg"), .9)
        self.assertEqual(self.battery.mass, .4)

    def test_deleting_a_limit_keeps_the_component_in_all_actual_totals(self):
        self.cpu.set_value("mass_kg", .3)
        self.battery.set_value("mass_kg", 1.2)
        self.cpu.set_value("draw_power_W", 10)
        self.cpu.set_value("average_power_W", 2)
        load = self.connect()
        self.session.remove(self.power)
        self.session.remove(self.resource(self.cpu, "mass"))
        self.assertEqual(self.value(self.root, "draw_power_W"), 10)
        self.assertEqual(self.value(self.root, "average_power_W"), 2)
        self.assertEqual(self.value(load, "sunlight_power_W"), 2)
        self.assertAlmostEqual(self.value(self.resource(self.session.mission, "mass"), "mass_kg"), 1.5)
        self.session.reconcile_defaults(generic=False)
        self.assertIsNone(power_limit_for(self.session, self.cpu))
        self.assertIsNone(self.resource(self.cpu, "mass"))
        for restored in (loads(dumps(self.session)), Session.from_projection(self.session.to_projection())):
            self.assertEqual(restored.value(self.root.id, "average_power_W", mode="Nominal"), 2)
            self.assertIsNone(power_limit_for(restored, restored.get("CPU")))

    def test_removing_hardware_updates_only_unchanged_default_totals(self):
        self.cpu.set_value("mass_kg", .3)
        self.battery.set_value("mass_kg", 1.2)
        self.session.remove(self.power)
        self.session.remove(self.resource(self.cpu, "mass"))
        self.session.remove(self.resource(self.cpu, "volume"))
        self.session.remove(self.cpu)
        self.assertAlmostEqual(self.value(self.resource(self.session.mission, "mass"), "mass_kg"), 1.2)
        self.assertEqual(self.value(self.resource(self.cdh, "mass"), "mass_kg"), 0)
        self.assertEqual(self.value(self.root, "draw_power_W"), 0)

    def test_custom_references_still_protect_requirement_deletion_atomically(self):
        parent = power_limit_for(self.session, self.cdh)
        before = parent.parameters["allocated_power_W"].expression
        self.session.add(Requirement("CHK001", "Keep a reference.", owner=self.cdh,
                                     parameters=(Parameter("value", expression=f"{self.power.id}.power_limit_W"),)))
        with self.assertRaises(ValueError):
            self.session.remove(self.power)
        self.assertEqual(parent.parameters["allocated_power_W"].expression, before)

    def test_missing_inputs_remain_pending_and_negative_inputs_are_rejected(self):
        with self.assertRaises(PendingValue):
            self.value(self.root, "draw_power_W")
        with self.assertRaises(ValueError):
            self.cpu.set_value("mass_kg", -1)
        self.cpu.set_expression("draw_power_W", "-1")
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            self.value(self.root, "draw_power_W")

    def test_excluded_hardware_and_explicit_losses_follow_accounting_boundaries(self):
        self.cpu.set_value("draw_power_W", 10)
        self.session.configure_load(self.cpu, accounting="excluded")
        loss = self.session.add(PowerLoss("LOS"), owner=self.eps)
        loss.set_value("draw_power_W", .2)
        self.assertEqual(self.value(self.root, "average_power_W"), .2)
        self.assertIsNone(self.resource(loss, "mass"))
        self.assertEqual(self.value(self.connect(), "sunlight_power_W"), .2)

    def test_component_bindings_participate_in_rename_cycle_and_mode_protection(self):
        self.cpu.set_expression("draw_power_W", '10 if mode == "Nominal" else 20')
        self.session.rename(self.cpu, "OBC")
        self.assertEqual(self.power.parameters["draw_power_W"].expression, "OBC.draw_power_W")
        self.session.rename_mode(self.nominal, "Standby")
        self.assertIn('mode == "Standby"', self.cpu.parameters["draw_power_W"].expression)
        with self.assertRaises(ValueError):
            self.session.remove_mode(self.nominal)
        self.cpu.set_expression("draw_power_W", f"{self.power.id}.draw_power_W")
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.value(self.cpu, "draw_power_W")

    def test_component_inputs_share_script_dependencies_and_evidence_freshness(self):
        script = self.session.add(NormalInterval("SCR001"))
        script.set_value("mean", 1)
        script.set_value("standard_deviation", .1)
        script.set_value("confidence", .95)
        self.cpu.set_expression("draw_power_W", "SCR001.upper")
        with self.assertRaises(PendingValue):
            self.value(self.cpu, "draw_power_W")
        self.session.run(script, mode=self.nominal, runner=InlineRunner())
        self.assertGreater(self.value(self.root, "draw_power_W"), 1)
        before = self.session.calculation_signature()
        self.cpu.set_expression("average_power_W", "draw_power_W / 2")
        self.assertNotEqual(before, self.session.calculation_signature())
        with self.assertRaises(PendingValue):
            self.value(self.root, "draw_power_W")

    def test_native_projection_and_disk_round_trips_keep_component_expressions(self):
        self.cpu.set_expression("draw_power_W", '10 if mode == "Nominal" else 20')
        self.power.set_expression("average_power_W", "draw_power_W / 5")
        projection = self.session.to_projection()
        validate_projection(projection)
        for restored in (loads(dumps(self.session)), Session.from_projection(projection)):
            self.assertEqual(restored.to_projection(), projection)
            self.assertEqual(restored.value(self.power.id, "average_power_W", mode="Pass"), 4)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.py"
            self.session.save(path)
            reopened = Session.open(path)
            self.assertEqual(reopened.get("CPU").parameters, self.cpu.parameters)
            self.assertEqual(reopened.value(self.power.id, "average_power_W", mode="Pass"), 4)
            self.assertIsNone(reopened.execution_evidence)

    def test_the_existing_projection_editor_routes_actual_inputs_to_the_component(self):
        projection = copy.deepcopy(self.session.to_projection())
        row = next(row for row in projection["statements"] if row["key"] == self.power.key)
        row["parameters"]["draw_power_W"] = "10"
        restored = apply_projection(self.session, projection, callables=CallableRegistry(), state_edits=(
            {"target": self.power.key, "parameter": "average_power_W", "values": {self.nominal.key: "2", self.passed.key: "4"}},
        ))
        self.assertEqual(restored.get("CPU").parameters["draw_power_W"].expression, "10")
        self.assertEqual(restored.get(self.power.key).parameters["draw_power_W"].expression, "CPU.draw_power_W")
        self.assertEqual(restored.value(self.root.id, "average_power_W", mode="Pass"), 4)
        link = describe(restored)["objects"][self.power.key]["linkedInputs"]["draw_power_W"]
        self.assertEqual(link["component"], self.cpu.key)
        edited = restored.to_projection()
        edited["modelState"]["componentBudgets"][self.cpu.key]["draw_power_W"] = "12"
        updated = apply_projection(restored, edited, callables=CallableRegistry())
        self.assertEqual(updated.value(self.power.id, "draw_power_W", mode="Nominal"), 12)

    def test_invalid_editor_drafts_remain_editable_component_bindings(self):
        projection = copy.deepcopy(self.session.to_projection())
        row = next(row for row in projection["statements"] if row["key"] == self.power.key)
        row["parameters"]["draw_power_W"] = "1 +"
        restored = apply_projection(self.session, projection, callables=CallableRegistry())
        self.assertEqual(restored.get("CPU").parameters["draw_power_W"].expression.source, "1 +")
        self.assertEqual(restored.get(self.power.key).parameters["draw_power_W"].expression, "CPU.draw_power_W")
        self.assertEqual(loads(dumps(restored)).to_projection(), restored.to_projection())

    def test_new_auxiliary_editor_inputs_are_declared_before_linked_expressions(self):
        projection = copy.deepcopy(self.session.to_projection())
        row = next(row for row in projection["statements"] if row["key"] == self.power.key)
        projection["variables"].append({"name": "duty", "type": "float", "unit": "1"})
        projection["modelState"]["parameters"][self.power.key]["duty"] = {"type": "float", "unit": "1"}
        row["parameters"].update(draw_power_W="10", average_power_W="draw_power_W * duty", duty="0.2")
        restored = apply_projection(self.session, projection, callables=CallableRegistry())
        self.assertEqual(restored.value(self.root.id, "average_power_W", mode="Nominal"), 2)
        self.assertIn(f"{self.power.id}.duty", restored.get("CPU").parameters["average_power_W"].expression)

    def test_linked_inputs_retain_canonical_units_through_all_edit_paths(self):
        with self.assertRaisesRegex(ValueError, "canonical"):
            self.power.set_unit("draw_power_W", "mW")
        projection = copy.deepcopy(self.session.to_projection())
        projection["modelState"]["parameters"][self.power.key]["draw_power_W"]["unit"] = "mW"
        with self.assertRaisesRegex(ValueError, "canonical"):
            apply_projection(self.session, projection, callables=CallableRegistry())
        self.assertEqual(self.power.parameters["draw_power_W"].unit, "W")

    def test_existing_cots_fact_names_are_preserved_and_collisions_are_explicit(self):
        cots = self.session.add(CotsBattery(
            "CMP001", product="gomspace_nanopower_bpx_100wh_8s1p", database=self.session.database,
        ), owner=self.eps, initialize=False)
        fact = next(fact for fact in cots.product_record.facts if type(fact.value) in (int, float) and fact.value > 0)
        cots.select_fact("mass_kg", fact)
        check = self.session.add(Requirement("CHK001", "Reference a product fact.", owner=self.eps,
                                            parameters=(Parameter("value", expression="CMP001.mass_kg"),)))
        self.assertEqual(self.value(check, "value"), fact.value)
        cots.set_value("mass_kg", .2)
        with self.assertRaisesRegex(ValueError, "Rename the selected fact"):
            self.value(check, "value")

    def test_conflicting_legacy_inputs_fail_without_replacing_either_binding(self):
        self.cpu.set_value("draw_power_W", 10)
        original = Parameter("draw_power_W", unit="W", value=20)
        self.power._parameters["draw_power_W"] = original
        with self.assertRaisesRegex(ValueError, "conflicting"):
            self.session.reconcile_defaults(generic=False)
        self.assertIs(self.power.parameters["draw_power_W"], original)
        self.assertEqual(self.cpu.parameters["draw_power_W"].value, 10)

    def test_existing_service_commands_edit_the_same_native_component_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            app = Application(Path(directory) / "current.py")
            view = app.create_session(self.session, name="Component budgets")
            view = app.command({"handle": view["handle"], "command": {
                "name": "set_value", "target": self.power.key, "parameter": "draw_power_W", "value": 10,
            }})
            self.assertEqual(view["workspace"]["modelState"]["componentBudgets"][self.cpu.key]["draw_power_W"], "10")

    def test_legacy_requirement_inputs_migrate_without_evaluating_or_replacing_edits(self):
        self.power._parameters["draw_power_W"] = Parameter("draw_power_W", unit="W", expression='10 if mode == "Nominal" else 20')
        self.power._parameters["average_power_W"] = Parameter("average_power_W", unit="W", expression="draw_power_W / 5")
        mass = self.resource(self.cpu, "mass")
        mass._parameters["mass_kg"] = Parameter("mass_kg", unit="kg", value=.3)
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(self.value(self.cpu, "average_power_W", self.passed), 4)
        self.assertEqual(self.cpu.parameters["mass_kg"].value, .3)
        self.assertEqual(mass.parameters["mass_kg"].expression, "CPU.mass_kg")
        before = self.session.to_projection()
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(self.session.to_projection(), before)

    def test_legacy_allocations_remain_live_after_reconciliation(self):
        state = ComponentState("Active", 10)
        self.session.configure_load(self.cpu, states=(state,), assignments={self.nominal: state, self.passed: state}, duties={self.nominal: 20, self.passed: 40})
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(self.value(self.power, "draw_power_W"), 10)
        self.assertEqual(self.value(self.power, "average_power_W"), 2)
        self.assertEqual(self.value(self.connect(), "sunlight_power_W"), 2.8)

    def test_legacy_native_functions_retain_their_requirement_context(self):
        self.power._parameters["draw_power_W"] = Parameter("draw_power_W", unit="W", expression=legacy_power)
        self.power.set_value("power_limit_W", 10)
        self.session.reconcile_defaults(generic=False)
        self.assertIs(self.power.parameters["draw_power_W"].expression, legacy_power)
        self.assertEqual(self.value(self.root, "draw_power_W"), 5)


if __name__ == "__main__":
    unittest.main()
