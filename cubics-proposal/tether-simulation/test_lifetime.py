"""Checks for the separate orbit averaged lifetime screening model."""

from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from lifetime import (
    MEDIUM_ACTIVITY,
    YEAR_S,
    AtmosphereTable,
    LifetimeConfig,
    MsisSampler,
    build_atmosphere_table,
    export_lifetime,
    main as lifetime_main,
    propagate_lifetime,
    tumbling_pair_area,
)
from lifetime_vizard import (
    TetheredPair,
    circular_state,
    comparison_milestones,
    export_comparison,
)
from orbit_environment import EARTH_MU, EARTH_RADIUS_M, OrbitConfig
from simulate import Config
from vizard_scene import SEGMENTS
from Basilisk.utilities import RigidBodyKinematics as rbk
from test_vizard import archive_frames, protobuf_fields


class ConstantDensityTable(AtmosphereTable):
    """Nonrotating atmosphere with an exact analytical circular drag limit."""

    def work_at(self, altitude_m):
        radius = EARTH_RADIUS_M + max(altitude_m, self.altitude_m[0])
        return self.density_kg_m3[0] * (EARTH_MU / radius) ** 1.5


def constant_density_table(density=1e-13):
    return ConstantDensityTable(
        MEDIUM_ACTIVITY,
        np.array([80000.0, 1000000.0]),
        np.array([density, density]),
        np.ones(2),
    )


def analytical_altitude(initial_m, duration_s, config, area_m2, density):
    coefficient = config.drag_coefficient * area_m2 / config.mass_kg
    root_a = (
        np.sqrt(EARTH_RADIUS_M + initial_m)
        - 0.5 * coefficient * density * np.sqrt(EARTH_MU) * duration_s
    )
    return root_a**2 - EARTH_RADIUS_M


class NativeAtmosphereTests(unittest.TestCase):
    def test_native_msis_density_and_solar_activity(self):
        densities = []
        # Alternate inputs check the atmosphere module, not additional mission cases.
        weather_inputs = (
            replace(MEDIUM_ACTIVITY, f107_sfu=70, ap=4),
            MEDIUM_ACTIVITY,
            replace(MEDIUM_ACTIVITY, f107_sfu=200, ap=20),
        )
        for case in weather_inputs:
            sampler = MsisSampler(case)
            upper = sampler.density([EARTH_RADIUS_M + 600000, 0, 0], 0)
            lower = sampler.density([EARTH_RADIUS_M + 200000, 0, 0], 0)
            self.assertGreater(upper, 1e-16)
            self.assertLess(upper, 1e-11)
            self.assertGreater(lower, 100 * upper)
            densities.append(upper)
        self.assertTrue(np.all(np.diff(densities) > 0))

    def test_co_rotation_increases_drag_work_for_the_retrograde_orbit(self):
        orbit = OrbitConfig()
        rotating = build_atmosphere_table(
            orbit, MEDIUM_ACTIVITY, stop_altitude_m=600000
        )
        with patch("lifetime.EARTH_SPIN_RAD_S", 0.0):
            stationary = build_atmosphere_table(
                orbit, MEDIUM_ACTIVITY, stop_altitude_m=600000
            )
        speed = np.sqrt(EARTH_MU / (EARTH_RADIUS_M + orbit.altitude_m))
        np.testing.assert_allclose(
            stationary.drag_work, stationary.density_kg_m3 * speed**3
        )
        self.assertGreater(rotating.drag_work[0], stationary.drag_work[0])

    def test_orbit_averaged_table_is_positive_and_converges(self):
        orbit = OrbitConfig()
        tables = [
            build_atmosphere_table(
                orbit, MEDIUM_ACTIVITY, stop_altitude_m=590000, phase_samples=count
            )
            for count in (12, 24)
        ]
        for table in tables:
            self.assertTrue(np.all(table.density_kg_m3 > 0))
            self.assertTrue(np.all(table.drag_work > 0))
            self.assertGreater(table.density_kg_m3[0], table.density_kg_m3[-1])
            middle = table.work_at(595000)
            self.assertAlmostEqual(
                middle, np.sqrt(np.prod(table.drag_work)), delta=middle * 1e-12
            )
        np.testing.assert_allclose(tables[0].drag_work, tables[1].drag_work, rtol=0.05)


class LifetimeTests(unittest.TestCase):
    def setUp(self):
        self.config = LifetimeConfig()
        self.orbit = OrbitConfig()
        self.table = constant_density_table()

    def test_default_span_mass_and_mean_area(self):
        self.assertEqual(self.config.duration_s, 8 * YEAR_S)
        self.assertEqual(self.config.mission_s, 3 * YEAR_S)
        self.assertEqual(self.config.mass_kg, 6)
        self.assertAlmostEqual(tumbling_pair_area(), 0.04404 + np.pi / 4 * 3 * 0.0005)
        self.assertAlmostEqual(
            self.config.ballistic_coefficient(tumbling_pair_area()), 60.31, delta=0.01
        )

    def test_exact_constant_density_drag_limit(self):
        result = propagate_lifetime(self.config, self.orbit, self.table)
        expected = analytical_altitude(
            self.orbit.altitude_m,
            self.config.duration_s,
            self.config,
            self.config.mission_area_m2,
            1e-13,
        )
        self.assertAlmostEqual(result.altitude_m[-1], expected, delta=0.01)
        self.assertIn(self.config.mission_s, result.time_s)
        self.assertEqual(result.time_s[-1], self.config.duration_s)
        self.assertTrue(np.all(np.diff(result.altitude_m) < 0))

    def test_no_drag_preserves_altitude_for_eight_years(self):
        config = replace(self.config, drag_coefficient=0)
        result = propagate_lifetime(config, self.orbit, self.table)
        np.testing.assert_array_equal(result.altitude_m, self.orbit.altitude_m)
        self.assertIsNone(result.threshold_time_s)

    def test_mission_stationkeeping_then_five_year_decay(self):
        config = replace(self.config, maintain_mission_altitude=True)
        result = propagate_lifetime(config, self.orbit, self.table)
        self.assertEqual(result.altitude_at(config.mission_s), self.orbit.altitude_m)
        expected = analytical_altitude(
            self.orbit.altitude_m,
            5 * YEAR_S,
            config,
            config.post_mission_area_m2,
            1e-13,
        )
        self.assertAlmostEqual(result.altitude_m[-1], expected, delta=0.01)

    def test_area_changes_exactly_at_mission_end(self):
        config = replace(self.config, mission_area_m2=0)
        result = propagate_lifetime(config, self.orbit, self.table)
        self.assertEqual(result.altitude_at(config.mission_s), self.orbit.altitude_m)
        expected = analytical_altitude(
            self.orbit.altitude_m,
            5 * YEAR_S,
            config,
            config.post_mission_area_m2,
            1e-13,
        )
        self.assertAlmostEqual(result.altitude_m[-1], expected, delta=0.01)

    def test_stops_at_boundary_without_extrapolating_later_milestones(self):
        result = propagate_lifetime(
            self.config, self.orbit, constant_density_table(1e-10)
        )
        self.assertIsNotNone(result.threshold_time_s)
        coefficient = (
            self.config.drag_coefficient
            * self.config.mission_area_m2
            / self.config.mass_kg
        )
        expected_time = (
            2
            * (
                np.sqrt(EARTH_RADIUS_M + self.orbit.altitude_m)
                - np.sqrt(EARTH_RADIUS_M + self.config.reentry_altitude_m)
            )
            / (coefficient * 1e-10 * np.sqrt(EARTH_MU))
        )
        self.assertAlmostEqual(result.threshold_time_s, expected_time, delta=0.5)
        self.assertEqual(result.time_s[-1], result.threshold_time_s)
        self.assertEqual(result.altitude_m[-1], self.config.reentry_altitude_m)
        self.assertTrue(np.all(result.altitude_m >= self.config.reentry_altitude_m))
        self.assertIsNone(result.altitude_at(self.config.mission_s))
        self.assertIsNone(result.altitude_at(self.config.duration_s))
        summary = result.summary(self.config, self.orbit)
        self.assertFalse(summary["survives_mission_above_stop_altitude"])
        self.assertIsNone(summary["post_mission_decay_km"])
        self.assertIsNone(summary["post_mission_end_mean_altitude_km"])

    def test_recording_cadence_does_not_change_the_dynamics(self):
        dense = propagate_lifetime(self.config, self.orbit, self.table)
        sparse = propagate_lifetime(
            replace(self.config, record_days=100), self.orbit, self.table
        )
        self.assertEqual(dense.altitude_m[-1], sparse.altitude_m[-1])
        self.assertEqual(
            dense.altitude_at(self.config.mission_s),
            sparse.altitude_at(self.config.mission_s),
        )

    def test_variable_density_step_convergence(self):
        heights = np.arange(120000, 600001, 10000)
        rho = 1e-13 * np.exp((600000 - heights) / 70000)
        work = rho * (EARTH_MU / (EARTH_RADIUS_M + heights)) ** 1.5
        table = AtmosphereTable(MEDIUM_ACTIVITY, heights, rho, work)
        coarse = propagate_lifetime(self.config, self.orbit, table)
        fine = propagate_lifetime(
            replace(self.config, max_step_days=0.5), self.orbit, table
        )
        self.assertAlmostEqual(coarse.altitude_m[-1], fine.altitude_m[-1], delta=0.1)

    def test_exports_milestones_and_preserves_deployment_files(self):
        result = propagate_lifetime(self.config, self.orbit, self.table)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "results.json").write_text("deployment sentinel")
            (output / "mission.bin").write_bytes(b"deployment sentinel")
            summary = export_lifetime(
                [result], [self.table], self.config, self.orbit, output
            )
            self.assertEqual(
                json.loads((output / "lifetime_results.json").read_text()), summary
            )
            self.assertEqual(
                (output / "results.json").read_text(), "deployment sentinel"
            )
            self.assertEqual(
                (output / "mission.bin").read_bytes(), b"deployment sentinel"
            )
            self.assertTrue((output / "lifetime.csv").exists())
            self.assertTrue((output / "lifetime_atmosphere.csv").exists())
        case = summary["cases"][0]
        self.assertAlmostEqual(
            case["post_mission_decay_km"],
            case["mission_end_mean_altitude_km"]
            - case["post_mission_end_mean_altitude_km"],
        )

    def test_command_line_computes_only_medium_activity(self):
        with tempfile.TemporaryDirectory() as directory:
            arguments = ["lifetime.py", "--no-vizard", "--output", directory]
            with (
                patch.object(sys, "argv", arguments),
                patch(
                    "lifetime.build_atmosphere_table", return_value=self.table
                ) as build,
                patch("lifetime.plot_lifetime"),
                redirect_stdout(io.StringIO()),
            ):
                lifetime_main()
            build.assert_called_once()
            self.assertEqual(build.call_args.args[1], MEDIUM_ACTIVITY)
            summary = json.loads(
                (Path(directory) / "lifetime_results.json").read_text()
            )
            self.assertEqual(
                [case["activity"]["name"] for case in summary["cases"]], ["medium"]
            )
            self.assertNotIn("vizard_deployment_detail", summary)

    def test_invalid_configuration(self):
        for config in (
            replace(self.config, mass_kg=0),
            replace(self.config, mission_years=float("nan")),
            replace(self.config, post_mission_years=-1),
            replace(self.config, max_step_days=0),
            replace(self.config, mission_area_m2=-0.1),
            replace(self.config, reentry_altitude_m=700000),
        ):
            with self.assertRaises(ValueError):
                propagate_lifetime(config, self.orbit, self.table)


class LifetimeVizardTests(unittest.TestCase):
    def setUp(self):
        self.config, self.orbit = LifetimeConfig(), OrbitConfig()
        self.result = propagate_lifetime(
            self.config, self.orbit, constant_density_table()
        )

    def test_comparison_has_three_physical_milestone_radii(self):
        milestones = comparison_milestones(self.result, self.config, self.orbit)
        self.assertEqual(len(milestones), 3)
        self.assertIn("3y", milestones[1][0])
        self.assertIn("8y", milestones[2][0])
        self.assertEqual(
            milestones[1][1], self.result.altitude_at(self.config.mission_s)
        )
        self.assertGreater(milestones[0][1], milestones[1][1])
        self.assertGreater(milestones[1][1], milestones[2][1])

    def test_circular_comparison_orbits_have_correct_energy_and_altitude(self):
        for _, altitude in comparison_milestones(self.result, self.config, self.orbit):
            position, velocity = circular_state(
                altitude, self.orbit.inclination_rad, 0.7, 1234
            )
            radius = np.linalg.norm(position)
            self.assertAlmostEqual(radius - EARTH_RADIUS_M, altitude, delta=1e-8)
            self.assertAlmostEqual(np.dot(position, velocity), 0, delta=1e-4)
            self.assertAlmostEqual(
                np.dot(velocity, velocity) / 2 - EARTH_MU / radius,
                -EARTH_MU / (2 * radius),
                delta=1e-7,
            )

    def test_no_post_boundary_orbit_is_fabricated(self):
        result = propagate_lifetime(
            self.config, self.orbit, constant_density_table(1e-10)
        )
        milestones = comparison_milestones(result, self.config, self.orbit)
        self.assertEqual(len(milestones), 2)
        self.assertTrue(milestones[-1][0].startswith("Stop_boundary"))
        self.assertFalse(
            any(name.startswith("Post_mission_end") for name, _ in milestones)
        )

    def test_native_comparison_archive_uses_milestone_states(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_comparison(
                self.result,
                self.config,
                self.orbit,
                Path(directory) / "lifetime.bin",
                step_s=1000,
            )
            frames = list(archive_frames(path.read_bytes()))
        self.assertLess(len(frames), 10)
        live_settings = dict(protobuf_fields(dict(frames[0])[10]))
        self.assertEqual(live_settings[5], 1)  # Real time playback mode.
        self.assertEqual(
            2 ** live_settings[6], 128
        )  # Exponent, not a linear multiplier.
        first_positions = [
            np.array(struct.unpack("<3d", dict(protobuf_fields(body))[2]))
            for tag, body in frames[0]
            if tag == 3 and not dict(protobuf_fields(body)).get(19)
        ]
        for i, left in enumerate(first_positions):
            for right in first_positions[i + 1 :]:
                self.assertLess(np.dot(left, right), 0)  # Distinct marker phases.
        objects = [dict(protobuf_fields(body)) for tag, body in frames[-1] if tag == 3]
        roots = [fields for fields in objects if not fields.get(19)]
        milestones = comparison_milestones(self.result, self.config, self.orbit)
        self.assertEqual(len(objects), len(milestones) * (SEGMENTS + 3))
        self.assertEqual(len(roots), len(milestones))
        self.assertNotIn(4, dict(frames[0]))  # GUI zoom, without an extra camera inset.
        for fields, (name, altitude) in zip(roots, milestones):
            self.assertEqual(fields[1].decode(), name)
            position = np.array(struct.unpack("<3d", fields[2]))
            self.assertAlmostEqual(
                np.linalg.norm(position) - EARTH_RADIUS_M, altitude, delta=1e-8
            )
        settings = dict(protobuf_fields(dict(frames[0])[7]))
        self.assertEqual(
            settings[21], (1 << 64) - 1
        )  # Keep meshes visible when zooming.
        object_names = {fields[1].decode() for fields in objects}
        model_targets = set()
        for tag, model in protobuf_fields(dict(frames[0])[7]):
            if tag != 12:
                continue
            fields = list(protobuf_fields(model))
            self.assertEqual(dict(fields)[1], b"CUBE")
            targets = [value.decode() for key, value in fields if key == 2]
            model_targets.update(targets)
            if any(name.endswith("CubeSat_A") for name in targets):
                np.testing.assert_allclose(
                    struct.unpack("<3d", dict(fields)[5]),
                    [Config().body_length_m, 0.1, 0.1],
                )
        self.assertEqual(
            model_targets, object_names
        )  # No generic spacecraft model remains.
        for fields in objects:
            if fields.get(19):
                parent = fields[19].decode()
                self.assertIn(parent, [name for name, _ in milestones])
                self.assertTrue(fields[1].decode().startswith(parent + "_"))

    def test_twin_geometry_remains_attached_in_the_parent_frame(self):
        pair = TetheredPair("test_pair", Config())
        for time in (0, 1000, 5000):
            position, velocity = circular_state(
                600000, self.orbit.inclination_rad, 0, time
            )
            pair.update(position, velocity, int(time * 1e9))
            a, b = [message.read() for message in pair.component_msgs[:2]]
            rotation = rbk.MRP2C(a.sigma_BN).T
            left = np.array(a.r_BN_N) + rotation @ [Config().body_length_m / 2, 0, 0]
            right = np.array(b.r_BN_N) - rotation @ [Config().body_length_m / 2, 0, 0]
            self.assertAlmostEqual(np.linalg.norm(right - left), 3.0, delta=1e-8)
            first, last = [
                message.read()
                for message in (pair.component_msgs[2], pair.component_msgs[-1])
            ]
            np.testing.assert_allclose(
                first.r_BN_N,
                left + rotation @ [3 / SEGMENTS / 2, 0, 0],
                atol=1e-8,
                rtol=0,
            )
            np.testing.assert_allclose(
                last.r_BN_N,
                right - rotation @ [3 / SEGMENTS / 2, 0, 0],
                atol=1e-8,
                rtol=0,
            )


if __name__ == "__main__":
    unittest.main()
