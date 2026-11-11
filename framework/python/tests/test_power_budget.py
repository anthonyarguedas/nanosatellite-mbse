"""Regression tests for native power bindings, duties and case assessments.

Run with PYTHONPATH=framework/python/src python3 -m unittest discover \
    -s framework/python/tests -v
"""

import copy
import math
import tempfile
import unittest
from dataclasses import fields, replace
from pathlib import Path

from nanosat_mbse import (
    ComponentState,
    StateAllocation,
    PowerLoss,
    CotsBattery,
    CubeSat,
    NormalInterval,
    Parameter,
    Requirement,
    Session,
)
from nanosat_mbse.core.execution import InlineRunner
from nanosat_mbse.core.predicates import PendingValue
from nanosat_mbse.domains.budgets import power_limit_for, resource_scopes
from nanosat_mbse.domains.eps import EPS, RegulatorAndConverter
from nanosat_mbse.persistence import dumps, loads
from nanosat_mbse.persistence.callables import CallableRegistry
from nanosat_mbse.service.application import Application
from nanosat_mbse.service.edits import apply_projection
from nanosat_mbse.service.validation import normalize_projection, validate_projection
from nanosat_mbse.service.views import describe


class PowerBudgetTests(unittest.TestCase):
    def setUp(self):
        self.session = s = Session()
        bus = s.add(CubeSat("BUS"), initialize=False)
        self.eps = s.add(EPS("EPS"), owner=bus, initialize=False)
        self.component = s.add(
            RegulatorAndConverter("REG"), owner=self.eps, initialize=False
        )
        s.remember_component_defaults(self.component)
        self.inputs = s.add(
            Requirement(
                "RAD001",
                "Electrical inputs.",
                owner=self.eps,
                parameters=(
                    Parameter("current_A", unit="A", value=0.1),
                    Parameter("voltage_V", unit="V", value=7.2),
                ),
            )
        )
        self.standby = s.add_mode("Standby", sunlight=60, eclipse=20)
        self.passed = s.add_mode("Pass", sunlight=40, eclipse=80)
        self.state = ComponentState("On", "RAD001.current_A * RAD001.voltage_V")
        s.configure_load(
            self.component,
            quantity=2,
            states=(self.state,),
            assignments={self.standby: self.state, self.passed: self.state},
        )
        self.row = power_limit_for(s, self.component)
        self.root = power_limit_for(s, s.mission)

    def value(self, name, *, mode=None, row=None):
        return self.session.value(row or self.row, name, mode=mode or self.standby)

    def set_duties(self, standby=50, passed=25):
        self.session.configure_load(
            self.component,
            duties={self.standby: standby, self.passed: passed},
        )

    def connect(self):
        load = self.session.add(
            Requirement(
                "LOD001",
                "Load energy inputs.",
                owner=self.eps,
                definition="FrameworkRequirements::LoadEnergy",
                parameters=tuple(
                    Parameter(name, value=value)
                    for name, value in (
                        ("sunlight_power_W", 0),
                        ("eclipse_power_W", 0),
                        ("sunlight_duty", 1),
                        ("eclipse_duty", 1),
                        ("sunlight_s", None),
                        ("eclipse_s", None),
                        ("sunlight_energy_J", None),
                        ("eclipse_energy_J", None),
                    )
                ),
            ),
            initialize=False,
        )
        self.session.connect_power(self.eps)
        return load

    def test_literal_values_and_default_continuous_duty(self):
        self.state.watts = 0.72
        self.assertAlmostEqual(self.value("draw_power_W"), 1.44)
        self.assertAlmostEqual(self.value("average_power_W"), 1.44)
        self.assertEqual(self.session.power.load_for(self.component).duties, {})

    def test_expressions_follow_upstream_edits(self):
        self.assertAlmostEqual(self.value("draw_power_W"), 1.44)
        self.inputs.set_value("current_A", 0.2)
        self.assertAlmostEqual(self.value("draw_power_W"), 2.88)

    def test_duties_are_independent_per_assignment(self):
        self.set_duties()
        self.assertAlmostEqual(self.value("average_power_W"), 0.72)
        self.assertAlmostEqual(self.value("average_power_W", mode=self.passed), 0.36)
        self.assertAlmostEqual(self.value("draw_power_W"), 1.44)

    def test_low_duty_does_not_hide_active_power_violation(self):
        self.set_duties(standby=1)
        self.row.set_value("power_limit_W", 1)
        self.assertAlmostEqual(self.value("average_power_W"), 0.0144)
        self.assertEqual(self.row.verify(mode=self.standby).state.value, "fail")

    def test_duration_is_optional_for_power_calculations(self):
        self.row.set_value("power_limit_W", 2)
        self.assertTrue(self.row.verify(mode=self.standby).verified)
        with self.assertRaises(PendingValue):
            self.value("energy_Wh")
        self.assertAlmostEqual(self.value("draw_power_W"), 1.44)

    def test_case_durations_use_existing_mode_parameter_bindings(self):
        self.set_duties()
        self.session.configure_parameter_states(
            self.root,
            "assessment_duration_s",
            values={self.standby.key: "5400", self.passed.key: "600"},
        )
        self.assertEqual(self.value("assessment_duration_s"), 5400)
        self.assertEqual(self.value("assessment_duration_s", mode=self.passed), 600)
        self.assertAlmostEqual(self.value("energy_Wh"), 1.08)
        self.assertAlmostEqual(self.value("energy_Wh", mode=self.passed), 0.06)
        self.assertAlmostEqual(self.value("energy_Wh", row=self.root), 1.08)

    def test_case_durations_do_not_require_or_change_orbital_shares(self):
        self.session.configure_mode(self.standby, sunlight=None, eclipse=None)
        self.session.configure_mode(self.passed, sunlight=None, eclipse=None)
        self.root.set_value("assessment_duration_s", 600)
        self.assertAlmostEqual(self.value("energy_Wh"), 0.24)
        self.assertIsNone(self.standby.sunlight)
        self.assertIsNone(self.passed.eclipse)

    def test_child_can_override_assessment_duration(self):
        self.root.set_value("assessment_duration_s", 5400)
        self.row.set_value("assessment_duration_s", 600)
        self.assertAlmostEqual(self.value("energy_Wh"), 0.24)
        self.assertEqual(self.value("assessment_duration_s", row=self.root), 5400)

    def test_invalid_assessment_durations_fail_energy_only(self):
        for duration in (0, -1):
            with self.subTest(duration=duration):
                self.root.set_value("assessment_duration_s", duration)
                with self.assertRaisesRegex(ValueError, "duration must be positive"):
                    self.value("energy_Wh")
                self.assertAlmostEqual(self.value("draw_power_W"), 1.44)

    def test_zero_duty_has_zero_energy_even_when_active_power_is_unset(self):
        self.inputs.set_value("current_A", None)
        self.set_duties(standby=0)
        self.root.set_value("assessment_duration_s", 600)
        self.assertEqual(self.value("energy_Wh"), 0)
        with self.assertRaises(PendingValue):
            self.value("draw_power_W")

    def test_invalid_duties_are_rejected_without_mutation(self):
        for duty in (-1, 101, True, math.inf, "50"):
            with self.subTest(duty=duty):
                with self.assertRaises(ValueError):
                    self.set_duties(standby=duty)
                self.assertEqual(self.session.power.load_for(self.component).duties, {})

    def test_removing_a_selected_state_removes_its_assignment_and_duty(self):
        self.set_duties()
        self.session.configure_load(self.component, states=())
        load = self.session.power.load_for(self.component)
        self.assertEqual(load.assignments, {})
        self.assertEqual(load.duties, {})

    def test_duty_requires_an_existing_state_assignment(self):
        self.session.configure_load(self.component, assignments={})
        with self.assertRaisesRegex(ValueError, "state assignments"):
            self.set_duties()

    def test_invalid_expression_results_are_rejected(self):
        for expression in ("-1", "True", "'0.72'", "1 / 0", "math.sqrt(-1)"):
            with self.subTest(expression=expression):
                self.state.watts = expression
                with self.assertRaises((ValueError, ArithmeticError)):
                    self.value("draw_power_W")
        with self.assertRaises((SyntaxError, ValueError)):
            ComponentState("Invalid", "1 +")

    def test_missing_inputs_remain_pending(self):
        self.inputs.set_value("current_A", None)
        with self.assertRaises(PendingValue):
            self.value("draw_power_W")

    def test_unknown_local_variables_report_an_expression_error(self):
        self.state.watts = "unknown_power"
        with self.assertRaisesRegex(ValueError, "Unknown variable"):
            self.value("draw_power_W")

    def test_arbitrary_python_is_not_executed(self):
        self.state.watts = "__import__('os').getpid()"
        with self.assertRaises(ValueError):
            self.value("draw_power_W")

    def test_cyclic_power_bindings_are_detected(self):
        self.state.watts = f"{self.row.id}.draw_power_W"
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.value("draw_power_W")

    def test_connected_budget_uses_duty_averages_in_each_modes_context(self):
        self.set_duties()
        self.inputs.set_expression("current_A", '0.1 if mode == "Standby" else 0.3')
        load = self.connect()
        # Standby: 2 * 0.1 * 7.2 * 50% = 0.72 W.
        # Pass:    2 * 0.3 * 7.2 * 25% = 1.08 W.
        for mode in (self.standby, self.passed):
            self.assertAlmostEqual(
                self.session.value(load, "sunlight_power_W", mode=mode), 0.864
            )
            self.assertAlmostEqual(
                self.session.value(load, "eclipse_power_W", mode=mode), 1.008
            )

    def test_connected_budget_cycles_across_modes_are_detected(self):
        load = self.connect()
        self.state.watts = f"{load.id}.sunlight_power_W"
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.session.value(load, "sunlight_power_W", mode=self.standby)

    def test_connected_budget_runs_script_dependencies_in_each_required_mode(self):
        upstream = self.session.add(NormalInterval("SCR001"))
        upstream.set_expression("mean", '1 if mode == "Standby" else 2')
        upstream.set_value("standard_deviation", 0.1)
        upstream.set_value("confidence", 0.95)
        self.state.watts = "SCR001.upper"
        self.connect()
        downstream = self.session.add(NormalInterval("SCR002"))
        downstream.set_expression("mean", "LOD001.sunlight_power_W")
        downstream.set_value("standard_deviation", 0.1)
        downstream.set_value("confidence", 0.95)
        evidence = self.session.run(
            downstream, mode=self.standby, runner=InlineRunner()
        )
        self.assertTrue(evidence.successful)
        self.assertIsNotNone(evidence.result_for(upstream, self.standby))
        self.assertIsNotNone(evidence.result_for(upstream, self.passed))
        self.assertIsNotNone(evidence.result_for(downstream, self.standby))
        self.set_duties()
        with self.assertRaises(PendingValue):
            self.value("draw_power_W")

    def test_state_expression_can_use_mode_conditionals(self):
        self.state.watts = '1 if mode == "Standby" else 3'
        self.assertEqual(self.value("draw_power_W"), 2)
        self.assertEqual(self.value("draw_power_W", mode=self.passed), 6)

    def test_row_renaming_and_deletion_protection_include_state_bindings(self):
        self.session.rename(self.inputs, "RAD002")
        self.assertEqual(self.state.watts, "RAD002.current_A * RAD002.voltage_V")
        self.assertAlmostEqual(self.value("draw_power_W"), 1.44)
        with self.assertRaisesRegex(ValueError, "used by an expression"):
            self.session.remove(self.inputs)

    def test_mode_renaming_and_deletion_protection_include_state_bindings(self):
        self.state.watts = '1 if mode == "Standby" else 3'
        self.session.rename_mode(self.standby, "Idle")
        self.assertIn('mode == "Idle"', self.state.watts)
        self.assertEqual(self.value("draw_power_W"), 2)
        with self.assertRaisesRegex(ValueError, "expression references"):
            self.session.remove_mode(self.standby)

    def test_removing_a_mode_removes_its_duty(self):
        self.set_duties()
        self.session.remove_mode(self.standby)
        load = self.session.power.load_for(self.component)
        self.assertNotIn(self.standby, load.assignments)
        self.assertNotIn(self.standby, load.duties)

    def test_cots_fact_renaming_and_deletion_protection(self):
        cots = self.session.add(
            CotsBattery(
                "CMP001",
                product="gomspace_nanopower_bpx_100wh_8s1p",
                database=self.session.database,
            ),
            owner=self.eps,
            initialize=False,
        )
        fact = next(
            fact
            for fact in cots.product_record.facts
            if type(fact.value) in (int, float) and fact.value > 0
        )
        cots.select_fact("selected_power", fact)
        self.state.watts = "CMP001.selected_power"
        self.assertAlmostEqual(self.value("draw_power_W"), 2 * fact.value)
        with self.assertRaisesRegex(ValueError, "expression references"):
            self.session.configure_facts(cots, ())
        self.session.configure_facts(
            cots, (replace(cots.facts[0], name="renamed_power"),)
        )
        self.assertEqual(self.state.watts, "CMP001.renamed_power")
        self.assertAlmostEqual(self.value("draw_power_W"), 2 * fact.value)

    def test_signature_tracks_power_duty_and_assessment_bindings(self):
        before = self.session.calculation_signature()
        self.state.watts = "0.72"
        after_power = self.session.calculation_signature()
        self.assertNotEqual(before, after_power)
        self.set_duties()
        after_duty = self.session.calculation_signature()
        self.assertNotEqual(after_power, after_duty)
        self.root.set_value("assessment_duration_s", 600)
        self.assertNotEqual(after_duty, self.session.calculation_signature())

    def test_native_and_projection_round_trips_preserve_bindings(self):
        self.set_duties()
        self.root.set_value("assessment_duration_s", 600)
        projection = self.session.to_projection()
        validate_projection(projection)
        for restored in (
            loads(dumps(self.session)),
            Session.from_projection(projection),
        ):
            with self.subTest(restored=type(restored).__name__):
                self.assertAlmostEqual(
                    restored.value(self.row.id, "energy_Wh", mode="Standby"), 0.12
                )
                self.assertEqual(restored.to_projection(), projection)

    def test_legacy_load_without_duties_retains_continuous_operation(self):
        projection = self.session.to_projection()
        self.assertNotIn("duties", projection["power"]["loads"][0])
        restored = Session.from_projection(projection)
        self.assertAlmostEqual(
            restored.value(self.row.id, "average_power_W", mode="Standby"), 1.44
        )

    def test_reconciliation_adds_new_parameters_without_replacing_edits(self):
        self.row.set_expression("average_power_W", "0.5")
        self.root._parameters.pop("assessment_duration_s")
        self.root._parameters.pop("energy_Wh")
        self.session.reconcile_defaults(generic=False)
        self.assertEqual(self.value("average_power_W"), 0.5)
        self.assertIsNone(self.root.parameters["assessment_duration_s"].value)
        self.assertIn("energy_Wh", self.root.parameters)

    def test_editor_projection_edits_power_duty_and_mode_duration(self):
        projection = copy.deepcopy(self.session.to_projection())
        load = projection["power"]["loads"][0]
        load["states"][0]["watts"] = "RAD001.voltage_V * 0.2"
        load["duties"] = {self.standby.key: 50, self.passed.key: 25}
        restored = apply_projection(
            self.session,
            projection,
            callables=CallableRegistry(),
            state_edits=(
                {
                    "target": self.root.key,
                    "parameter": "assessment_duration_s",
                    "values": {self.standby.key: "5400", self.passed.key: "600"},
                },
            ),
        )
        self.assertAlmostEqual(
            restored.value(self.row.id, "energy_Wh", mode="Standby"), 2.16
        )
        self.assertAlmostEqual(
            restored.value(self.row.id, "energy_Wh", mode="Pass"), 0.12
        )
        self.assertIn("duties", describe(restored)["powerDefaults"][self.component.key])

    def test_projection_rename_and_quantity_edit_retain_native_rewrites(self):
        projection = copy.deepcopy(self.session.to_projection())
        row = next(
            row for row in projection["statements"] if row["key"] == self.inputs.key
        )
        row["id"] = "RAD002"
        projection["power"]["loads"][0]["quantity"] = 3
        restored = apply_projection(
            self.session, projection, callables=CallableRegistry()
        )
        load = restored.power.loads[0]
        self.assertIn("RAD002.", load.states[0].watts)
        self.assertAlmostEqual(
            restored.value(self.row.id, "draw_power_W", mode="Standby"), 2.16
        )

    def test_disk_round_trip_preserves_authored_case_duration(self):
        self.set_duties()
        self.root.set_expression(
            "assessment_duration_s", '600 if mode == "Pass" else 5400'
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.py"
            self.session.save(path)
            restored = Session.open(path)
            self.assertAlmostEqual(
                restored.value(self.row.id, "energy_Wh", mode="Pass"), 0.06
            )

    def test_existing_service_command_accepts_new_load_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            app = Application(Path(directory) / "current.py")
            view = app.create_session(self.session, name="Power assessment")
            view = app.command(
                {
                    "handle": view["handle"],
                    "command": {
                        "name": "configure_load",
                        "target": self.component.key,
                        "changes": {"duties": {self.standby.key: 50}},
                    },
                }
            )
            load = view["workspace"]["power"]["loads"][0]
            self.assertEqual(load["duties"][self.standby.key], 50)

    def mix_states(self):
        self.tx = ComponentState("Transmit", 7.2)
        self.off = ComponentState("Off", 0)
        self.session.configure_load(
            self.component,
            states=(self.state, self.tx, self.off),
            allocations={
                self.standby: (StateAllocation(self.state, 99), StateAllocation(self.tx, 1)),
                self.passed: (StateAllocation(self.off, 100),),
            },
        )

    def test_state_mixture_uses_weighted_average_and_exclusive_active_maximum(self):
        self.mix_states()
        self.assertAlmostEqual(self.value("average_power_W"), 1.5696)
        self.assertAlmostEqual(self.value("draw_power_W"), 14.4)
        self.assertEqual(self.value("average_power_W", mode=self.passed), 0)
        self.root.set_value("assessment_duration_s", 600)
        self.assertAlmostEqual(self.value("energy_Wh"), 0.2616)
        self.row.set_value("power_limit_W", 2)
        self.assertEqual(self.row.verify(mode=self.standby).state.value, "fail")
        load = self.session.power.load_for(self.component)
        self.assertEqual(load.assignments, {})
        self.assertEqual(load.duties, {})

    def test_invalid_mixtures_leave_the_existing_configuration_unchanged(self):
        self.mix_states()
        before = self.session.to_projection()
        invalid = (
            [{"state": self.state.key, "duty": 60}, {"state": self.tx.key, "duty": 41}],
            [{"state": self.state.key, "duty": 50}, {"state": self.state.key, "duty": 50}],
            [{"state": self.state.key, "duty": True}],
            [{"state": self.state.key, "duty": math.inf}],
            [{"state": "missing", "duty": 20}],
        )
        for entries in invalid:
            with self.subTest(entries=entries):
                with self.assertRaises((ValueError, TypeError)):
                    self.session.configure_load(self.component, allocations={self.standby: entries})
                self.assertEqual(self.session.to_projection(), before)

    def test_state_removal_rebinds_retained_mixture_states(self):
        self.mix_states()
        replacement = ComponentState("On", 1.0, key=self.state.key)
        self.session.configure_load(self.component, states=(replacement, self.off))
        load = self.session.power.load_for(self.component)
        self.assertIs(load.allocations[self.standby][0].state, replacement)
        self.assertEqual(len(load.allocations[self.standby]), 1)
        self.assertAlmostEqual(self.value("average_power_W"), 1.98)

    def test_mixture_mode_removal_and_signature_changes(self):
        self.mix_states()
        before = self.session.calculation_signature()
        self.session.configure_load(self.component, allocations={self.standby: (StateAllocation(self.state, 10),)})
        self.assertNotEqual(before, self.session.calculation_signature())
        self.session.remove_mode(self.standby)
        self.assertNotIn(self.standby, self.session.power.load_for(self.component).allocations)

    def test_mixed_zero_duty_skips_missing_power_for_energy_only(self):
        self.session.configure_load(self.component, allocations={self.standby: (StateAllocation(self.state, 0),)})
        self.inputs.set_value("current_A", None)
        self.assertEqual(self.value("average_power_W"), 0)
        with self.assertRaises(PendingValue):
            self.value("draw_power_W")

    def test_mixture_round_trips_and_editor_projection_edits(self):
        self.mix_states()
        projection = self.session.to_projection()
        validate_projection(projection)
        for restored in (loads(dumps(self.session)), Session.from_projection(projection)):
            self.assertEqual(restored.to_projection(), projection)
            self.assertAlmostEqual(restored.value(self.row.id, "average_power_W", mode="Standby"), 1.5696)
        edited = copy.deepcopy(projection)
        edited["power"]["loads"][0]["allocations"][self.standby.key][1]["duty"] = 0.5
        restored = apply_projection(self.session, edited, callables=CallableRegistry())
        self.assertAlmostEqual(restored.value(self.row.id, "average_power_W", mode="Standby"), 1.4976)
        with tempfile.TemporaryDirectory() as directory:
            self.session.save(Path(directory) / "session.py")
            reopened = Session.open(Path(directory) / "session.py")
            self.assertAlmostEqual(reopened.value(self.row.id, "average_power_W", mode="Standby"), 1.5696)

    def test_connected_mixture_uses_each_modes_average(self):
        self.mix_states()
        load = self.connect()
        self.assertAlmostEqual(self.session.value(load, "sunlight_power_W", mode=self.standby), 1.5696 * .6)
        self.assertAlmostEqual(self.session.value(load, "eclipse_power_W", mode=self.passed), 1.5696 * .2)

    def test_power_loss_is_optional_and_has_no_mass_or_volume_scope(self):
        complete = Session()
        complete.add(CubeSat())
        self.assertFalse(any(isinstance(row, PowerLoss) for row in complete.elements))
        loss = self.session.add(PowerLoss("LOS"), owner=self.eps)
        state = ComponentState("Dissipating", .15)
        self.session.configure_load(loss, quantity=2, states=(state,), allocations={
            self.standby: (StateAllocation(state, 50),),
            self.passed: (StateAllocation(state, 100),),
        })
        self.assertNotIn(loss, [scope.target for scope in resource_scopes(self.session)])
        self.assertIsNotNone(power_limit_for(self.session, loss))
        self.assertAlmostEqual(self.value("average_power_W", row=self.root), 1.59)
        load = self.connect()
        self.assertAlmostEqual(self.session.value(load, "sunlight_power_W", mode=self.standby), 1.65)
        for restored in (loads(dumps(self.session)), Session.from_projection(self.session.to_projection())):
            self.assertIsInstance(restored.get("LOS"), PowerLoss)
            self.assertAlmostEqual(restored.value(self.root.id, "average_power_W", mode="Standby"), 1.59)

    def test_service_creates_a_real_loss_and_accepts_state_mixtures(self):
        with tempfile.TemporaryDirectory() as directory:
            app = Application(Path(directory) / "current.py")
            view = app.create_session(self.session, name="Loss test")
            definition = f"{self.eps.definition}::PowerLoss"
            view = app.command({"handle": view["handle"], "command": {
                "name": "add_element", "owner": self.eps.key, "definition": definition, "key": "test-loss",
            }})
            self.assertEqual(view["metadata"]["objects"]["test-loss"]["className"], "PowerLoss")
            view = app.command({"handle": view["handle"], "command": {
                "name": "configure_load", "target": "test-loss", "changes": {
                    "states": [{"key": "on", "name": "On", "watts": .1}],
                    "allocations": {self.standby.key: [{"state": "on", "duty": 100}]},
                },
            }})
            loss_load = next(load for load in view["workspace"]["power"]["loads"] if load["element"] == "test-loss")
            self.assertEqual(loss_load["allocations"][self.standby.key][0]["duty"], 100)

    def test_component_states_only_store_identity_name_and_power(self):
        self.assertEqual([field.name for field in fields(ComponentState)], ["name", "watts", "key"])
        state = self.session.to_projection()["power"]["loads"][0]["states"][0]
        self.assertEqual(set(state), {"key", "name", "watts"})
        described = describe(self.session)["powerDefaults"][self.component.key]["states"][0]
        self.assertEqual(set(described), {"key", "name", "watts"})
        for retired in ("basis", "source", "conditions"):
            self.assertFalse(hasattr(self.state, retired))

    def test_old_state_constructors_read_without_retaining_annotations(self):
        keyword = ComponentState("On", .72, key="old-state", basis="measured", source="old source", conditions="old conditions")
        positional = ComponentState("On", .72, "measured", "old source", "old conditions", "old-state")
        for state in (keyword, positional):
            self.assertEqual(state.key, "old-state")
            self.assertEqual(state.watts, .72)
            self.assertEqual(set(vars(state)), {"key", "name", "watts"})
        with self.assertRaises(TypeError):
            ComponentState("On", .72, unsupported="typo")

    def test_legacy_native_source_discards_only_retired_state_metadata(self):
        source = dumps(self.session)
        legacy = source.replace("name='On', watts=", "name='On', basis='measured', source='legacy source', conditions='25 C', watts=")
        self.assertNotEqual(legacy, source)
        restored = loads(legacy)
        self.assertAlmostEqual(restored.value(self.row.id, "draw_power_W", mode="Standby"), 1.44)
        self.assertEqual(restored.power.loads[0].states[0].key, self.state.key)
        self.assertNotIn("legacy source", dumps(restored))
        self.assertEqual(restored.to_projection(), self.session.to_projection())

    def test_legacy_projection_discards_retired_metadata_and_preserves_allocations(self):
        self.mix_states()
        projection = copy.deepcopy(self.session.to_projection())
        for state in projection["power"]["loads"][0]["states"]:
            state.update(basis="measured", source="legacy source", conditions="25 C")
        normalized = normalize_projection(projection)
        validate_projection(normalized)
        self.assertEqual(set(normalized["power"]["loads"][0]["states"][0]), {"key", "name", "watts"})
        for restored in (Session.from_projection(projection), apply_projection(self.session, projection, callables=CallableRegistry())):
            self.assertAlmostEqual(restored.value(self.row.id, "average_power_W", mode="Standby"), 1.5696)
            self.assertEqual(restored.to_projection(), self.session.to_projection())

    def test_inline_state_rename_addition_and_deletion_preserve_surviving_duties(self):
        self.mix_states()
        projection = copy.deepcopy(self.session.to_projection())
        load = projection["power"]["loads"][0]
        load["states"][0]["name"] = "Receiving"
        load["states"] = [state for state in load["states"] if state["key"] != self.tx.key]
        load["states"].append({"key": "idle-state", "name": "Idle", "watts": "0.01"})
        restored = apply_projection(self.session, projection, callables=CallableRegistry())
        native = restored.power.load_for(restored.get(self.component.key))
        self.assertEqual(native.states[0].name, "Receiving")
        self.assertEqual(native.states[-1].name, "Idle")
        self.assertEqual(len(native.allocations[restored.resolve_mode("Standby")]), 1)
        self.assertAlmostEqual(restored.value(self.row.id, "average_power_W", mode="Standby"), 1.4256)


if __name__ == "__main__":
    unittest.main()
