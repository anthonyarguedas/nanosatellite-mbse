"""Circular orbit beta geometry, zero-duration loads and default migration."""

import copy
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from nanosat_mbse import (
    ComponentState,
    CubeSat,
    NormalInterval,
    Orbit,
    Parameter,
    Requirement,
    Session,
    VerificationMethod,
)
from nanosat_mbse.catalogs._illumination import LEGACY_DEFAULTS
from nanosat_mbse.core.execution import InlineRunner
from nanosat_mbse.core.predicates import PendingValue
from nanosat_mbse.domains.eps import EPS, RegulatorAndConverter
from nanosat_mbse.persistence import dumps, loads
from nanosat_mbse.persistence.callables import CallableRegistry
from nanosat_mbse.service.edits import apply_projection


class IlluminationTests(unittest.TestCase):
    def setUp(self):
        self.session = Session()
        self.orbit = self.session.add(Orbit())
        self.period = self.row("OrbitPeriod")
        self.illumination = self.row("IlluminationPeriods")
        self.closure = self.row("OrbitPeriodClosure")
        self.period.set_value("altitude_km", 416.86)

    def row(self, name):
        return next(
            row
            for row in self.session.requirements
            if row.definition == f"FrameworkRequirements::{name}"
        )

    def value(self, name, *, row=None, mode=None):
        return self.session.value(row or self.illumination, name, mode=mode)

    def add_eps(self):
        bus = self.session.add(CubeSat(), initialize=False)
        self.eps = self.session.add(EPS(), owner=bus, initialize=False)
        self.component = self.session.add(
            RegulatorAndConverter(), owner=self.eps, initialize=False
        )
        self.session.remember_component_defaults(self.component)
        self.session.seed_requirements(self.eps)
        self.load = self.row("LoadEnergy")
        return self.load

    def set_manual_load(self):
        load = self.add_eps()
        for name, value in (
            ("sunlight_power_W", 2),
            ("sunlight_duty", 0.5),
            ("eclipse_power_W", 1),
            ("eclipse_duty", 1),
        ):
            load.set_value(name, value)
        return load

    def make_legacy_defaults(self):
        for row in self.session.requirements:
            old = LEGACY_DEFAULTS.get(row.definition)
            if old is None:
                continue
            if "text" in old:
                row.text = old["text"]
            row._parameters.pop("beta_deg", None)
            for name, expression in old["parameters"].items():
                row.set_expression(name, expression)
            row.verifications = tuple(
                replace(method, condition=old["conditions"][0])
                for method in row.verifications
            )
        self.session.variables = [
            variable
            for variable in self.session.variables
            if variable.name != "beta_deg"
        ]

    def test_beta_defaults_to_zero_and_has_degree_units(self):
        self.assertEqual(self.value("beta_deg"), 0)
        self.assertEqual(self.illumination.parameters["beta_deg"].unit, "deg")
        self.assertTrue(self.illumination.verify().verified)

    def test_zero_beta_matches_former_circular_geometry(self):
        horizon = self.value("horizon_angle_rad")
        period = self.value("orbit_period_s")
        self.assertAlmostEqual(
            self.value("eclipse_s"), (0.5 - horizon / math.pi) * period, places=9
        )
        self.assertAlmostEqual(
            self.value("sunlight_s"), (0.5 + horizon / math.pi) * period, places=9
        )

    def test_nonzero_beta_matches_independent_shadow_geometry(self):
        self.illumination.set_value("beta_deg", 30)
        radius = self.value("earthRadius_km")
        orbit_radius = radius + self.value("altitude_km")
        half_angle = math.acos(
            math.sqrt(orbit_radius**2 - radius**2)
            / (orbit_radius * math.cos(math.radians(30)))
        )
        expected = self.value("orbit_period_s") * half_angle / math.pi
        self.assertAlmostEqual(self.value("eclipse_s"), expected, places=9)
        self.assertTrue(self.illumination.verify().verified)
        self.assertTrue(self.closure.verify().verified)

    def test_birds_high_beta_has_no_eclipse(self):
        self.illumination.set_value("beta_deg", 73)
        self.assertEqual(self.value("eclipse_s"), 0)
        self.assertEqual(self.value("sunlight_s"), self.value("orbit_period_s"))
        self.assertTrue(self.illumination.verify().verified)
        self.assertTrue(self.closure.verify().verified)

    def test_signed_beta_is_symmetric(self):
        self.illumination.set_value("beta_deg", 30)
        eclipse = self.value("eclipse_s")
        self.illumination.set_value("beta_deg", -30)
        self.assertEqual(self.value("eclipse_s"), eclipse)
        self.assertTrue(self.illumination.verify().verified)

    def test_polar_sun_angles_avoid_division_by_zero(self):
        for beta in (-90, 90):
            with self.subTest(beta=beta):
                self.illumination.set_value("beta_deg", beta)
                self.assertEqual(self.value("eclipse_s"), 0)
                self.assertTrue(self.illumination.verify().verified)

    def test_critical_beta_and_nearby_values_remain_finite(self):
        critical = 90 - math.degrees(self.value("horizon_angle_rad"))
        for beta in (critical, critical + 1e-8):
            self.illumination.set_value("beta_deg", beta)
            self.assertEqual(self.value("eclipse_s"), 0)
            self.assertTrue(self.illumination.verify().verified)
        self.illumination.set_value("beta_deg", critical - 1e-8)
        self.assertGreater(self.value("eclipse_s"), 0)
        self.assertTrue(self.illumination.verify().verified)

    def test_eclipse_decreases_with_absolute_beta_and_periods_close(self):
        previous = math.inf
        for beta in (0, 10, 30, 50, 65, 69, 70, 73, 90):
            self.illumination.set_value("beta_deg", beta)
            eclipse = self.value("eclipse_s")
            self.assertLessEqual(eclipse, previous)
            self.assertAlmostEqual(
                self.value("sunlight_s") + eclipse, self.value("orbit_period_s")
            )
            previous = eclipse

    def test_beta_outside_physical_range_fails_verification(self):
        for beta in (-91, 91):
            self.illumination.set_value("beta_deg", beta)
            self.assertEqual(self.illumination.verify().state.value, "fail")

    def test_missing_altitude_remains_pending(self):
        self.period.set_value("altitude_km", None)
        with self.assertRaises(PendingValue):
            self.value("eclipse_s")
        self.assertEqual(self.illumination.verify().state.value, "pending")

    def test_beta_can_reference_an_owned_parameter_and_follow_renames(self):
        source = self.session.add(
            Requirement(
                "BET001",
                "Assess beta $$beta_deg$$.",
                owner=self.session.mission,
                parameters=(Parameter("beta_deg", unit="deg", value=73),),
            )
        )
        self.illumination.set_expression("beta_deg", "BET001.beta_deg")
        self.assertEqual(self.value("eclipse_s"), 0)
        self.session.rename(source, "BET002")
        self.assertEqual(
            self.illumination.parameters["beta_deg"].expression, "BET002.beta_deg"
        )
        source.set_value("beta_deg", 30)
        self.assertGreater(self.value("eclipse_s"), 0)

    def test_existing_mode_parameter_editor_can_supply_beta(self):
        low = self.session.add_mode("Low beta")
        high = self.session.add_mode("High beta")
        self.session.configure_parameter_states(
            self.illumination,
            "beta_deg",
            values={low.key: "30", high.key: "73"},
        )
        self.assertGreater(self.value("eclipse_s", mode=low), 0)
        self.assertEqual(self.value("eclipse_s", mode=high), 0)
        self.assertTrue(self.illumination.verify().verified)

    def test_no_eclipse_requires_no_eclipse_power_or_duty(self):
        load = self.set_manual_load()
        self.illumination.set_value("beta_deg", 73)
        load.set_value("eclipse_power_W", None)
        load.set_value("eclipse_duty", None)
        self.assertEqual(self.value("eclipse_energy_J", row=load), 0)
        self.assertAlmostEqual(
            self.value("sunlight_energy_J", row=load), self.value("orbit_period_s")
        )
        self.assertTrue(load.verify().verified)

    def test_absent_period_skips_unused_load_expressions(self):
        load = self.set_manual_load()
        self.illumination.set_value("beta_deg", 73)
        load.set_expression("eclipse_power_W", "1 / 0")
        load.set_expression("eclipse_duty", "1 / 0")
        self.assertEqual(self.value("eclipse_energy_J", row=load), 0)
        self.assertTrue(load.verify().verified)

    def test_connected_no_eclipse_skips_shares_and_unused_assignments(self):
        load = self.add_eps()
        self.illumination.set_value("beta_deg", 73)
        mode = self.session.add_mode("Nominal", sunlight=100)
        self.session.add_mode("Unused", sunlight=0)
        state = ComponentState("On", 2)
        self.session.configure_load(
            self.component, states=(state,), assignments={mode: state}
        )
        self.session.connect_power(self.eps)
        self.assertEqual(self.value("eclipse_power_W", row=load, mode=mode), 0)
        self.assertEqual(self.value("eclipse_energy_J", row=load, mode=mode), 0)
        self.assertEqual(self.value("sunlight_power_W", row=load, mode=mode), 2)
        self.assertTrue(load.verify().verified)

    def test_beta_script_dependency_is_resolved_before_skipping_eclipse_load(self):
        load = self.add_eps()
        mode = self.session.add_mode("Nominal", sunlight=100)
        beta = self.session.add(NormalInterval("SCR001"))
        beta.set_value("mean", 73)
        beta.set_value("standard_deviation", 0.1)
        beta.set_value("confidence", 0.95)
        self.illumination.set_expression("beta_deg", "SCR001.upper")
        self.session.connect_power(self.eps)
        assessment = self.session.add(NormalInterval("SCR002"))
        assessment.set_expression("mean", f"{load.id}.eclipse_power_W")
        assessment.set_value("standard_deviation", 0.1)
        assessment.set_value("confidence", 0.95)
        evidence = self.session.run(assessment, mode=mode, runner=InlineRunner())
        self.assertTrue(evidence.successful)
        self.assertIsNotNone(evidence.result_for(beta, mode))
        self.assertEqual(evidence.result_for(assessment, mode).inputs["mean"], 0)

    def test_positive_eclipse_still_requires_eclipse_shares(self):
        load = self.add_eps()
        mode = self.session.add_mode("Nominal", sunlight=100)
        state = ComponentState("On", 2)
        self.session.configure_load(
            self.component, states=(state,), assignments={mode: state}
        )
        self.session.connect_power(self.eps)
        with self.assertRaisesRegex(PendingValue, "Eclipse mode fractions"):
            self.value("eclipse_power_W", row=load, mode=mode)

    def test_zero_sunlight_load_interval_is_also_supported(self):
        load = self.set_manual_load()
        load.set_value("sunlight_s", 0)
        load.set_value("eclipse_s", 600)
        load.set_value("sunlight_power_W", None)
        load.set_value("sunlight_duty", None)
        self.assertEqual(self.value("sunlight_energy_J", row=load), 0)
        self.assertEqual(self.value("eclipse_energy_J", row=load), 600)
        self.assertTrue(load.verify().verified)

    def test_zero_and_negative_total_load_intervals_are_rejected(self):
        load = self.set_manual_load()
        for sunlight, eclipse in ((0, 0), (-1, 1), (1, -1)):
            load.set_value("sunlight_s", sunlight)
            load.set_value("eclipse_s", eclipse)
            self.assertEqual(load.verify().state.value, "fail")

    def test_power_average_remains_usable_before_orbit_is_known(self):
        load = self.add_eps()
        self.period.set_value("altitude_km", None)
        mode = self.session.add_mode("Nominal", sunlight=100, eclipse=100)
        state = ComponentState("On", 2)
        self.session.configure_load(
            self.component, states=(state,), assignments={mode: state}
        )
        self.session.connect_power(self.eps)
        self.assertEqual(self.value("sunlight_power_W", row=load, mode=mode), 2)
        self.assertEqual(self.value("eclipse_power_W", row=load, mode=mode), 2)
        with self.assertRaises(PendingValue):
            self.value("eclipse_energy_J", row=load, mode=mode)

    def test_downstream_panel_power_handles_zero_eclipse_energy(self):
        self.set_manual_load()
        self.illumination.set_value("beta_deg", 73)
        panel = self.row("MinimumPanelPower")
        panel.set_value("sunlight_efficiency", 0.8)
        panel.set_value("eclipse_efficiency", 0.8)
        self.assertAlmostEqual(self.value("panel_min_W", row=panel), 1.25)
        self.assertTrue(panel.verify().verified)

    def test_existing_editor_projection_can_edit_beta_without_new_controls(self):
        projection = copy.deepcopy(self.session.to_projection())
        row = next(
            row
            for row in projection["statements"]
            if row["key"] == self.illumination.key
        )
        row["parameters"]["beta_deg"] = "73"
        restored = apply_projection(
            self.session, projection, callables=CallableRegistry()
        )
        self.assertEqual(restored.value(self.illumination.id, "eclipse_s"), 0)
        self.assertTrue(restored.get(self.illumination.id).verify().verified)

    def test_new_bindings_round_trip_without_executing_analyses(self):
        self.illumination.set_expression("beta_deg", "70 + 3")
        for restored in (
            loads(dumps(self.session)),
            Session.from_projection(self.session.to_projection()),
        ):
            self.assertEqual(restored.value(self.illumination.id, "eclipse_s"), 0)
            self.assertEqual(
                restored.get(self.illumination.id).parameters["beta_deg"].expression,
                "70 + 3",
            )
            self.assertIsNone(restored._execution_evidence)

    def test_reconciliation_upgrades_only_reviewed_legacy_defaults(self):
        load = self.set_manual_load()
        self.make_legacy_defaults()
        self.assertNotIn("beta_deg", self.illumination.parameters)
        self.session.reconcile_defaults()
        self.assertEqual(self.value("beta_deg"), 0)
        self.illumination.set_value("beta_deg", 73)
        self.assertEqual(self.value("eclipse_s"), 0)
        self.assertTrue(self.illumination.verify().verified)
        self.assertTrue(self.closure.verify().verified)
        self.assertTrue(load.verify().verified)
        before = self.session.to_projection()
        self.session.reconcile_defaults()
        self.assertEqual(self.session.to_projection(), before)

    def test_reconciliation_preserves_authored_and_cleared_fields(self):
        self.make_legacy_defaults()
        self.illumination.add_parameter(Parameter("beta_deg", unit="deg", value=73))
        self.illumination.set_expression("sunlight_s", "orbit_period_s - eclipse_s")
        self.illumination.set_expression("eclipse_s", None)
        custom = VerificationMethod("Reviewed", "beta_deg == 73", key="custom")
        self.illumination.verifications = (custom,)
        self.illumination.text = "Assess the sourced beta $$beta_deg$$."
        self.session.reconcile_defaults()
        self.assertEqual(self.value("beta_deg"), 73)
        self.assertIsNone(self.illumination.parameters["eclipse_s"].expression)
        self.assertEqual(self.illumination.verifications, (custom,))
        self.assertEqual(
            self.illumination.text, "Assess the sourced beta $$beta_deg$$."
        )

    def test_reconciliation_preserves_a_cleared_beta_input(self):
        self.illumination.set_value("beta_deg", None)
        self.session.reconcile_defaults()
        self.assertIsNone(self.illumination.parameters["beta_deg"].value)
        self.assertIsNone(self.illumination.parameters["beta_deg"].expression)
        self.assertEqual(self.illumination.verify().state.value, "pending")

    def test_reconciliation_preserves_deliberately_deleted_requirements(self):
        self.make_legacy_defaults()
        self.session.remove(self.closure)
        self.session.remove(self.illumination)
        self.session.reconcile_defaults()
        self.assertFalse(
            any(row.definition in LEGACY_DEFAULTS for row in self.session.requirements)
        )

    def test_import_is_unchanged_until_explicit_reconciliation(self):
        self.make_legacy_defaults()
        restored = loads(dumps(self.session))
        self.assertNotIn("beta_deg", restored.get(self.illumination.id).parameters)
        restored.reconcile_defaults()
        self.assertEqual(restored.value(self.illumination.id, "beta_deg"), 0)

    def test_opening_a_saved_legacy_session_introduces_beta(self):
        self.make_legacy_defaults()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.py"
            self.session.save(path)
            restored = Session.open(path)
            row = restored.get(self.illumination.id)
            self.assertEqual(restored.value(row, "beta_deg"), 0)
            row.set_value("beta_deg", 73)
            self.assertEqual(restored.value(row, "eclipse_s"), 0)
            self.assertTrue(row.verify().verified)
            restored.save()
            reopened = Session.open(path)
            self.assertEqual(reopened.value(row.id, "beta_deg"), 73)
            self.assertTrue(reopened.get(row.id).verify().verified)


class RotatingArrayTests(unittest.TestCase):
    def inputs(self):
        return {
            "altitude_km": 500, "earth_radius_km": 6378, "mu_km3_s2": 398601,
            "inclination_deg": 0, "raan_deg": 0, "argument_latitude_deg": 0,
            "epoch_jd": 2460754.5, "duration_s": 360, "step_s": 1,
            "earth_j2": 0, "solar_constant_W_m2": 1000,
            "panel_normal_radial": 0, "panel_normal_along": 0, "panel_normal_cross": 1,
            "sun_tracking": False,
            "rotation_rate_deg_s": 0, "rotation_axis_radial": 1,
            "rotation_axis_along": 0, "rotation_axis_cross": 0,
            "initial_roll_deg": 0, "initial_pitch_deg": 0, "initial_yaw_deg": 0,
            "panel_area_m2": .01, "panel_efficiency": .3, "panel_retained_factor": .8,
        }

    def run_fixed_sun(self, **changes):
        from unittest.mock import patch
        from nanosat_mbse.verifications.illumination import AU_KM, simulate
        p = {**self.inputs(), **changes}
        with patch("nanosat_mbse.verifications.illumination.sun_position", return_value=(0, 0, AU_KM)), patch(
            "nanosat_mbse.verifications.illumination.solar_visibility", return_value=(1, (0, 0, 1), AU_KM)
        ):
            return simulate(p)

    def test_zero_rotation_and_tracking_have_expected_generation(self):
        for tracking in (False, True):
            result = self.run_fixed_sun(sun_tracking=tracking)
            self.assertAlmostEqual(result["mean_irradiance_W_m2"], 1000)
            self.assertAlmostEqual(result["mean_generation_W"], 2.4)
            self.assertAlmostEqual(result["generated_energy_J"], 864)
            self.assertAlmostEqual(result["generated_energy_Wh"], .24)
            self.assertAlmostEqual(result["mean_sunlight_generation_W"], 2.4)
            self.assertTrue(all(type(value) in (float, int) for value in result.values()))

    def test_full_rotation_matches_cosine_integral_and_step_converges(self):
        coarse = self.run_fixed_sun(rotation_rate_deg_s=1)
        fine = self.run_fixed_sun(rotation_rate_deg_s=1, step_s=.5)
        expected = 2.4 * 360 / math.pi
        self.assertAlmostEqual(coarse["generated_energy_J"], expected, delta=.004)
        self.assertLess(abs(fine["generated_energy_J"] - expected), abs(coarse["generated_energy_J"] - expected))
        self.assertAlmostEqual(coarse["min_generation_W"], 0)
        self.assertGreater(coarse["max_generation_W"], 2.39)
        normalized = self.run_fixed_sun(rotation_rate_deg_s=1, rotation_axis_radial=10)
        self.assertAlmostEqual(normalized["generated_energy_J"], coarse["generated_energy_J"])

    def test_initial_angles_and_rotation_direction(self):
        from nanosat_mbse.verifications.illumination import initial_orientation, rotate
        for actual, expected in (
            (initial_orientation((1, 0, 0), 0, 0, 90), (0, 1, 0)),
            (initial_orientation((0, 1, 0), 90, 0, 0), (0, 0, 1)),
            (initial_orientation((1, 0, 0), 0, 90, 0), (0, 0, -1)),
            (rotate((1, 0, 0), (0, 0, 1), -90), (0, -1, 0)),
        ):
            for first, second in zip(actual, expected):
                self.assertAlmostEqual(first, second)
        result = self.run_fixed_sun(initial_roll_deg=180)
        self.assertEqual(result["generated_energy_J"], 0)

    def test_all_dark_interval_returns_zero_sunlight_generation(self):
        from unittest.mock import patch
        from nanosat_mbse.verifications.illumination import AU_KM, simulate
        with patch("nanosat_mbse.verifications.illumination.solar_visibility", return_value=(0, (0, 0, 1), AU_KM)):
            result = simulate(self.inputs())
        self.assertEqual(result["sunlight_s"], 0)
        self.assertEqual(result["generated_energy_J"], 0)
        self.assertEqual(result["mean_sunlight_generation_W"], 0)

    def test_zero_area_or_retention_has_zero_electrical_generation(self):
        for values in ({"panel_area_m2": 0}, {"panel_retained_factor": 0}):
            result = self.run_fixed_sun(**values)
            self.assertEqual(result["generated_energy_J"], 0)
            self.assertEqual(result["mean_generation_W"], 0)
            self.assertEqual(result["max_generation_W"], 0)
            self.assertGreater(result["incident_energy_J_m2"], 0)

    def test_model_domains_reject_invalid_rotation_and_panel_parameters(self):
        for values in (
            {"panel_area_m2": -1}, {"panel_efficiency": 0}, {"panel_efficiency": 1.1},
            {"panel_retained_factor": 1.1}, {"rotation_rate_deg_s": True},
            {"rotation_rate_deg_s": 3},
            {"rotation_rate_deg_s": 1, "rotation_axis_radial": 0},
            {"rotation_axis_radial": 1e308}, {"panel_normal_cross": 1e308},
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.run_fixed_sun(**values)

    def test_zero_rotation_matches_the_previous_local_orbital_incidence(self):
        from nanosat_mbse.verifications.illumination import AU_KM, solar_visibility, sun_position, simulate
        p = self.inputs()
        p.update(panel_normal_radial=1, panel_normal_cross=0, duration_s=120)
        actual = simulate(p)
        radius = p["earth_radius_km"] + p["altitude_km"]
        rate = math.sqrt(p["mu_km3_s2"] / radius ** 3)
        expected = 0
        for index in range(120):
            t = index + .5
            radial = (math.cos(rate * t), math.sin(rate * t), 0)
            visible, direction, distance = solar_visibility(tuple(radius * v for v in radial), sun_position(p["epoch_jd"] + t / 86400), p["earth_radius_km"])
            expected += p["solar_constant_W_m2"] * (AU_KM / distance) ** 2 * visible * max(0, sum(a*b for a,b in zip(radial, direction)))
        self.assertAlmostEqual(actual["incident_energy_J_m2"], expected)

    def test_requirement_bindings_execute_and_invalidate_evidence(self):
        from nanosat_mbse.benches import create_analysis_demo
        from nanosat_mbse import Illumination
        from nanosat_mbse.service.validation import validate_projection
        s = create_analysis_demo()
        validate_projection(s.to_projection())
        script = next(script for script in s.scripts if isinstance(script, Illumination))
        attitude = next(row for row in s.requirements if row.definition == "FrameworkRequirements::ArrayAttitude")
        self.assertEqual(script.parameters["rotation_rate_deg_s"].expression, f"{attitude.id}.rotation_rate_deg_s")
        evidence = s.run(script)
        self.assertTrue(evidence.successful)
        self.assertGreater(script.value("generated_energy_J"), 0)
        generation = next(row for row in s.requirements if row.definition == "FrameworkRequirements::EPS02")
        self.assertGreater(generation.value("sunlight_generation_J"), 0)
        attitude.set_value("rotation_rate_deg_s", .1)
        with self.assertRaises(PendingValue):
            script.value("generated_energy_J")
        restored = loads(dumps(s))
        self.assertEqual(restored.get(script.id).parameters["rotation_rate_deg_s"].expression, f"{attitude.id}.rotation_rate_deg_s")


if __name__ == "__main__":
    unittest.main()
