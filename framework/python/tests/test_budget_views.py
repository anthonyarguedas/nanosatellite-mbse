"""Explicit aggregate scopes, compatibility, transport and source descriptions."""

import copy
import unittest

from nanosat_mbse import Budget, ComponentState, CubeSat, Parameter, Requirement, Session
from nanosat_mbse.core.verification import DraftExpression, PendingValue
from nanosat_mbse.domains.budgets import RESOURCES, power_limit_for, resource_limit_for
from nanosat_mbse.domains.components import ProcessorAndMemory
from nanosat_mbse.domains.eps import Battery, EPS
from nanosat_mbse.domains.mission import CommandAndDataHandling
from nanosat_mbse.persistence import dumps, loads
from nanosat_mbse.persistence.callables import CallableRegistry
from nanosat_mbse.service.edits import apply_projection
from nanosat_mbse.service.views import describe


class BudgetViewTests(unittest.TestCase):
    def setUp(self):
        self.session = s = Session()
        self.bus = s.add(CubeSat("BUS"), initialize=False)
        self.cdh = s.add(CommandAndDataHandling("CDH"), owner=self.bus, initialize=False)
        self.eps = s.add(EPS("EPS"), owner=self.bus, initialize=False)
        self.cpu = s.add(ProcessorAndMemory("CPU"), owner=self.cdh, initialize=False)
        self.battery = s.add(Battery("BAT"), owner=self.eps, initialize=False)
        for component in (self.cpu, self.battery):
            s.remember_component_defaults(component)
        self.nominal = s.add_mode("Nominal", sunlight=60, eclipse=20)
        self.downlink = s.add_mode("Downlink", sunlight=40, eclipse=80)
        s.seed_resource_budgets()
        self.cpu.set_expression("draw_power_W", '10 if mode == "Nominal" else 20')
        self.cpu.set_expression("average_power_W", "draw_power_W / 5")
        self.cpu.set_value("mass_kg", .3)
        self.battery.set_value("mass_kg", 1.2)
        self.cpu.set_value("volume_m3", .00002)
        self.battery.set_value("volume_m3", .0001)
        self.root = power_limit_for(s, s.mission)
        self.root.set_value("assessment_duration_s", 3600)

    def connect(self):
        row = self.session.add(Requirement(
            "LOD001", "Load inputs.", owner=self.eps,
            definition="FrameworkRequirements::LoadEnergy",
            parameters=tuple(Parameter(name, value=value) for name, value in (
                ("sunlight_power_W", 7), ("eclipse_power_W", 8),
                ("sunlight_duty", .5), ("eclipse_duty", .5),
                ("sunlight_s", None), ("eclipse_s", None),
                ("sunlight_energy_J", None), ("eclipse_energy_J", None),
            )),
        ), initialize=False)
        self.session.connect_power(self.eps, (self.bus,))
        return row

    def value(self, row, name):
        return self.session.value(row, name, mode=self.nominal)

    def test_python_budget_views_retain_their_scope_and_use_live_component_inputs(self):
        budget = self.session.budget(self.bus)
        self.assertIsInstance(budget, Budget)
        self.assertIs(budget.scope, self.bus)
        self.assertEqual(budget.reference("draw_power_W"), "BUS.budget.draw_power_W")
        self.assertEqual(budget.value("draw_power_W", mode=self.nominal), 10)
        self.assertEqual(dict(budget.value("average_power_W")), {"Nominal": 2, "Downlink": 4})
        self.assertAlmostEqual(budget.value("mass_kg"), 1.5)
        self.assertAlmostEqual(budget.value("volume_m3"), .00012)
        self.cpu.set_value("mass_kg", .8)
        self.assertEqual(budget.value("mass_kg"), 2)
        self.assertEqual(self.session.budget(self.eps).value("mass_kg"), 1.2)

    def test_aggregate_expressions_remain_editable_through_the_existing_editor(self):
        for resource in RESOURCES:
            with self.subTest(resource=resource.name):
                row = resource_limit_for(self.session, self.session.mission, resource)
                original = self.value(row, resource.value)
                expression = f"MISSION.budget.{resource.value} * 1.1"
                projection = copy.deepcopy(self.session.to_projection())
                edited = next(item for item in projection["statements"] if item["key"] == row.key)
                edited["parameters"][resource.value] = expression
                updated = apply_projection(self.session, projection, callables=CallableRegistry())
                self.assertAlmostEqual(updated.value(row.id, resource.value, mode="Nominal"), original * 1.1)
                updated.reconcile_defaults(generic=False)
                reopened = loads(dumps(updated))
                self.assertEqual(reopened.get(row.id).parameters[resource.value].expression, expression)
                self.assertAlmostEqual(reopened.value(row.id, resource.value, mode="Nominal"), original * 1.1)
                self.assertEqual(row.parameters[resource.value].expression, f"MISSION.budget.{resource.value}")

    def test_aggregate_expressions_support_normal_mode_edits_and_explicit_unit_conversions(self):
        row = resource_limit_for(self.session, self.session.mission, RESOURCES[0])
        self.session.configure_parameter_states(row, "mass_kg", values={
            self.nominal.key: "MISSION.budget.mass_kg * 1000",
            self.downlink.key: "MISSION.budget.mass_kg * 1100",
        })
        row.set_unit("mass_kg", "g")
        self.session.reconcile_defaults(generic=False)
        reopened = loads(dumps(self.session))
        self.assertEqual(reopened.get(row.id).parameters["mass_kg"].unit, "g")
        self.assertEqual(dict(reopened.value(row.id, "mass_kg")), {"Nominal": 1500, "Downlink": 1650})
        self.assertAlmostEqual(reopened.budget(reopened.mission).value("mass_kg"), 1.5)

    def test_generated_formulas_have_explicit_scopes_and_no_legacy_aliases(self):
        self.connect()
        for _, _, _, expression in self.session._expressions():
            self.assertNotIn("PowerAllocation", expression)
            self.assertNotIn("LoadBudget", expression)
        self.assertEqual(self.root.parameters["draw_power_W"].expression, "MISSION.budget.draw_power_W")
        self.assertEqual(self.root.parameters["energy_Wh"].expression, "average_power_W * assessment_duration_s / 3600")
        self.assertEqual(self.value(self.root, "energy_Wh"), 2)
        mass = resource_limit_for(self.session, self.session.mission, RESOURCES[0])
        self.assertEqual(mass.parameters["mass_kg"].expression, "MISSION.budget.mass_kg")

    def test_explicit_reference_has_the_same_meaning_in_any_requirement(self):
        load = self.connect()
        check = self.session.add(Requirement("CHK001", "Explicit totals.", owner=self.cdh, parameters=(
            Parameter("power", expression="BUS.budget.draw_power_W + EPS.load_budget.sunlight_power_W"),
        )))
        self.assertAlmostEqual(self.value(check, "power"), 12.8)
        self.assertAlmostEqual(self.value(load, "sunlight_power_W"), 2.8)
        self.assertAlmostEqual(self.value(load, "eclipse_power_W"), 3.6)
        check.add_parameter(Parameter("sunlight_s", value=0))
        self.assertAlmostEqual(self.value(check, "power"), 12.8)
        budget = self.session.load_budget(self.eps)
        self.assertIs(budget.connection, self.session.power.links[0])
        self.assertAlmostEqual(budget.value("sunlight_power_W"), 2.8)
        load.set_value("sunlight_s", 0)
        self.assertEqual(budget.value("sunlight_power_W"), 0)

    def test_rename_updates_nested_references_and_view_identity(self):
        load = self.connect()
        check = self.session.add(Requirement("CHK001", "Bus total.", parameters=(Parameter("mass", expression="BUS.budget.mass_kg"),)))
        self.session.rename(self.bus, "SAT")
        self.session.rename(self.eps, "PWR")
        self.assertEqual(check.parameters["mass"].expression, "SAT.budget.mass_kg")
        self.assertEqual(load.parameters["sunlight_power_W"].expression, "PWR.load_budget.sunlight_power_W")
        self.assertAlmostEqual(self.value(check, "mass"), 1.5)
        self.assertAlmostEqual(self.value(load, "sunlight_power_W"), 2.8)

    def test_namespace_outputs_are_bounded_and_private_attributes_are_unavailable(self):
        check = self.session.add(Requirement("CHK001", "Bounded values.", parameters=(Parameter("value"),)))
        for source in ("BUS.budget.__class__", "BUS.budget.scope", "BUS.budget.mass_kg.real", "BUS.budget.value('mass_kg')"):
            check.set_expression("value", source)
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.value(check, "value")

    def test_totals_retain_cycle_guards_pending_inputs_and_accounting(self):
        self.cpu.set_expression("draw_power_W", "MISSION.budget.draw_power_W")
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.value(self.root, "draw_power_W")
        self.cpu.set_value("draw_power_W", None)
        with self.assertRaises(PendingValue):
            self.value(self.root, "draw_power_W")
        self.session.configure_load(self.cpu, accounting="excluded")
        self.assertEqual(self.value(self.root, "draw_power_W"), 0)
        self.assertAlmostEqual(self.session.budget(self.bus).value("mass_kg"), 1.5)

    def test_legacy_aliases_work_before_reconciliation_and_migrate_without_evaluation(self):
        self.root.set_expression("draw_power_W", "1.2 * PowerAllocation.draw_power_W")
        self.root.set_expression("average_power_W", "PowerAllocation.average_power_W")
        self.root.set_expression("energy_Wh", "PowerAllocation.energy_Wh")
        projection = self.session.to_projection()
        restored = Session.from_projection(copy.deepcopy(projection))
        self.assertEqual(restored.to_projection(), projection)
        self.assertEqual(restored.value(self.root.id, "draw_power_W", mode="Nominal"), 12)
        restored.reconcile_defaults(generic=False)
        root = restored.get(self.root.id)
        self.assertEqual(root.parameters["draw_power_W"].expression, "1.2 * MISSION.budget.draw_power_W")
        self.assertEqual(root.parameters["energy_Wh"].expression, "average_power_W * assessment_duration_s / 3600")
        self.assertEqual(restored.value(root, "energy_Wh", mode="Nominal"), 2)
        before = restored.to_projection()
        restored.reconcile_defaults(generic=False)
        self.assertEqual(restored.to_projection(), before)

    def test_migration_preserves_compound_energy_formulas_and_string_literals(self):
        self.root.set_expression("energy_Wh", "PowerAllocation.energy_Wh * 1.2")
        self.root.set_expression("draw_power_W", 'PowerAllocation . draw_power_W if "PowerAllocation.draw_power_W" == "PowerAllocation.draw_power_W" else 0')
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(self.value(self.root, "energy_Wh"), 2.4)
        expression = self.root.parameters["draw_power_W"].expression
        self.assertTrue(expression.startswith("MISSION.budget.draw_power_W if"))
        self.assertEqual(expression.count('"PowerAllocation.draw_power_W"'), 2)
        self.assertEqual(self.value(self.root, "draw_power_W"), 10)

    def test_reconciliation_preserves_custom_and_invalid_formulas(self):
        self.root.set_expression("draw_power_W", "CPU.draw_power_W + 1")
        self.root._parameters["average_power_W"] = Parameter("average_power_W", unit="W", expression=DraftExpression("PowerAllocation.average_power_W +", "Invalid draft"))
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(self.root.parameters["draw_power_W"].expression, "CPU.draw_power_W + 1")
        self.assertEqual(self.root.parameters["average_power_W"].expression.source, "PowerAllocation.average_power_W +")

    def test_old_connected_inputs_migrate_and_disconnect_restores_previous_bindings(self):
        row = self.connect()
        for name in ("sunlight_power_W", "eclipse_power_W"):
            row._parameters[name] = Parameter(name, expression=f"LoadBudget.{name}")
        self.assertAlmostEqual(self.value(row, "sunlight_power_W"), 2.8)
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(row.parameters["sunlight_power_W"].expression, "EPS.load_budget.sunlight_power_W")
        with self.assertRaisesRegex(ValueError, "Disconnect"):
            row.set_value("sunlight_power_W", 10)
        self.session.disconnect_power(self.eps)
        self.assertEqual(self.value(row, "sunlight_power_W"), 7)
        self.assertEqual(self.value(row, "sunlight_duty"), .5)

    def test_source_metadata_is_explicit_and_never_calculates_inputs(self):
        row = self.connect()
        self.cpu.set_value("draw_power_W", None)
        metadata = describe(self.session)["objects"]
        power = metadata[self.root.key]["calculatedParameters"]["draw_power_W"]
        self.assertEqual(power["label"], "Total active power · MISSION")
        self.assertEqual(power["scope"], ["mission"])
        self.assertEqual([source["reference"] for source in power["sources"]], ["CPU.draw_power_W"])
        self.assertIsNone(power["sources"][0]["expression"])
        connected = metadata[row.key]["calculatedParameters"]["sunlight_power_W"]
        self.assertEqual(connected["scope"], [self.bus.key])
        self.assertEqual(connected["modes"], [{"name": "Nominal", "share": 60}, {"name": "Downlink", "share": 40}])
        self.assertIsNone(self.session.execution_evidence)

    def test_legacy_profile_bindings_remain_editable_component_inputs(self):
        state = ComponentState("Active", 10)
        self.cpu.set_value("draw_power_W", None)
        self.cpu.set_expression("average_power_W", "draw_power_W")
        self.session.configure_load(self.cpu, states=(state,), assignments={self.nominal: state, self.downlink: state})
        row = power_limit_for(self.session, self.cpu)
        self.assertEqual(self.cpu.parameters["draw_power_W"].expression, "CPU.power_profile.draw_power_W")
        self.assertNotIn("draw_power_W", describe(self.session)["objects"][row.key]["calculatedParameters"])
        row.set_value("draw_power_W", 12)
        row.set_expression("average_power_W", "draw_power_W / 2")
        self.assertEqual(self.value(self.root, "draw_power_W"), 12)
        self.assertEqual(self.value(self.root, "average_power_W"), 6)

    def test_unconfigured_explicit_profiles_remain_pending(self):
        self.cpu.set_expression("draw_power_W", "CPU.power_profile.draw_power_W")
        with self.assertRaises(PendingValue):
            self.value(self.root, "draw_power_W")

    def test_the_evaluator_resolves_generic_typed_namespaces(self):
        class Namespace:
            parameters = {"ready": Parameter("ready", bool)}

            def resolve(self, context, row, name):
                return True

        class CustomSession(Session):
            def expression_namespaces(self):
                return {**super().expression_namespaces(), "CHECK.calculated": Namespace()}

        session = CustomSession()
        row = session.add(Requirement("CHK001", "Typed namespace.", parameters=(
            Parameter("ready", bool, expression="CHECK.calculated.ready"),
        )))
        self.assertIs(session.value(row, "ready"), True)

    def test_source_and_projection_round_trips_keep_scopes_and_results(self):
        row = self.connect()
        projection = self.session.to_projection()
        source = dumps(self.session)
        self.assertIn("MISSION.budget.draw_power_W", source)
        self.assertNotIn("PowerAllocation", source)
        for restored in (loads(source), Session.from_projection(projection)):
            self.assertEqual(restored.to_projection(), projection)
            self.assertAlmostEqual(restored.value(row.id, "eclipse_power_W", mode="Downlink"), 3.6)
            self.assertIsNone(restored.execution_evidence)


if __name__ == "__main__":
    unittest.main()
