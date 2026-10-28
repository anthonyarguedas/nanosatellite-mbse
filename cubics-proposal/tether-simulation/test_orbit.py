"""Physical checks for the 600 km J2 orbit and its tether deployment."""

from dataclasses import replace
import unittest

import numpy as np
from Basilisk.utilities import RigidBodyKinematics as rbk

from orbit_environment import (
    EARTH_J2,
    EARTH_MU,
    EARTH_RADIUS_M,
    OrbitConfig,
    acceleration_j2,
    body_frame,
    earth_j2,
    propagate_reference,
)
from simulate import Config, simulate
from vizard_scene import SceneReplay


class OrbitDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orbit = OrbitConfig()
        cls.track = propagate_reference(cls.orbit, periods=6, step_s=5.0)

    def test_initial_circular_sso_elements(self):
        orbit = self.orbit
        r, v = orbit.initial_state()
        h = np.cross(r, v)
        self.assertAlmostEqual(np.linalg.norm(r) - EARTH_RADIUS_M, 600000.0, places=6)
        self.assertAlmostEqual(np.dot(r, v), 0.0, delta=1e-5)
        self.assertAlmostEqual(np.linalg.norm(v), 7557.8652065, places=6)
        self.assertAlmostEqual(
            np.rad2deg(np.arccos(h[2] / np.linalg.norm(h))), 97.7876695255, places=7
        )
        self.assertAlmostEqual(orbit.period_s / 60, 96.6871964, places=6)
        frame = body_frame(r, v)
        np.testing.assert_allclose(frame.T @ frame, np.eye(3), atol=1e-14)
        self.assertAlmostEqual(np.linalg.det(frame), 1.0, places=14)

    def test_native_gravity_matches_j2_formula(self):
        model = earth_j2().gravityModel
        model.initializeParameters()
        for direction in ([1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.3, 0.4, 0.5]):
            r = np.asarray(direction) / np.linalg.norm(direction) * self.orbit.radius_m
            native = np.asarray(model.computeField(r.tolist(), 2, True)).reshape(3)
            np.testing.assert_allclose(
                native, acceleration_j2(r), rtol=1e-13, atol=1e-13
            )

    def test_j2_orbital_energy(self):
        track = self.track
        radius = np.linalg.norm(track.positions, axis=1)
        z = track.positions[:, 2] / radius
        potential = -EARTH_MU / radius + EARTH_MU * EARTH_J2 * EARTH_RADIUS_M**2 / (
            2 * radius**3
        ) * (3 * z * z - 1)
        energy = np.sum(track.velocities**2, axis=1) / 2 + potential
        self.assertLess(np.ptp(energy) / abs(energy[0]), 1e-9)

    def test_prograde_nodal_precession_near_solar_rate(self):
        track = self.track
        h = np.cross(track.positions, track.velocities)
        raan = np.unwrap(np.arctan2(h[:, 0], -h[:, 1]))
        crossings = np.flatnonzero(
            (track.positions[:-1, 2] < 0) & (track.positions[1:, 2] >= 0)
        )
        times, nodes = [], []
        for i in crossings:
            fraction = -track.positions[i, 2] / (
                track.positions[i + 1, 2] - track.positions[i, 2]
            )
            times.append(track.time[i] + fraction * (track.time[i + 1] - track.time[i]))
            nodes.append(raan[i] + fraction * (raan[i + 1] - raan[i]))
        rate = np.polyfit(times, nodes, 1)[0] * 86400 * 180 / np.pi
        self.assertGreater(rate, 0.0)
        # First order mean element design, initialized as osculating elements.
        self.assertAlmostEqual(
            rate, self.orbit.summary()["target_nodal_rate_deg_day"], delta=0.006
        )

    def test_invalid_orbit(self):
        for orbit in (
            OrbitConfig(altitude_m=-1),
            OrbitConfig(altitude_m=1e8),
            OrbitConfig(epoch_utc="2026-01-01"),
        ):
            with self.assertRaises(ValueError):
                orbit.validate()


class OrbitalDeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config()
        cls.orbit = OrbitConfig()
        cls.result = simulate(cls.config, orbit=cls.orbit)

    def test_orbital_initial_state_and_spring_release(self):
        r, v = self.orbit.initial_state()
        np.testing.assert_allclose(self.result.positions[0].mean(axis=0), r, atol=1e-9)
        np.testing.assert_allclose(
            self.result.velocities[0].mean(axis=0), v, atol=1e-10
        )
        self.assertLess(self.result.gap[0], 1e-9)
        self.assertLess(abs(self.result.speed[0]), 1e-9)
        spin_drift = np.max(
            np.abs(
                self.result.angular_velocities[self.result.time <= 1]
                - self.result.angular_velocities[0]
            )
        )
        self.assertLess(spin_drift, 1e-10)
        self.assertLessEqual(
            self.result.summary(self.config)["initial_spring_release_center_speed_m_s"],
            0.100005,
        )

    def test_tether_catch_and_attachment_torques(self):
        summary = self.result.summary(self.config)
        self.assertAlmostEqual(summary["first_taut_s"], 30.115, delta=0.02)
        self.assertGreater(self.result.gap.max(), 3.0)
        self.assertLess(self.result.gap.max(), 3.012)
        self.assertTrue(np.all(self.result.tension >= 0))
        np.testing.assert_array_equal(self.result.tension[self.result.gap <= 3.0], 0)
        self.assertGreater(np.linalg.norm(self.result.angular_velocities[-1, 0]), 0.05)
        self.assertGreater(
            np.linalg.norm(self.result.positions[-1, 1] - self.result.positions[-1, 0]),
            self.config.body_length_m,
        )

    def test_com_agrees_with_independent_j2_reference(self):
        reference = propagate_reference(
            self.orbit, periods=50 / self.orbit.period_s, step_s=1.0
        )
        center = self.result.positions.mean(axis=1)
        samples = np.column_stack(
            [
                np.interp(reference.time, self.result.time, center[:, j])
                for j in range(3)
            ]
        )
        np.testing.assert_allclose(samples, reference.positions, atol=1e-4, rtol=0)

    def test_attachment_geometry(self):
        for i in (0, 6000, -1):
            for bus in range(2):
                rotation = rbk.MRP2C(self.result.attitudes[i, bus]).T
                offset = np.array([(0.5 - bus) * self.config.body_length_m, 0.0, 0.0])
                expected = self.result.positions[i, bus] + rotation @ offset
                np.testing.assert_allclose(
                    self.result.anchor_positions[i, bus], expected, atol=1e-9
                )

    def test_native_orbit_view_uses_unshifted_eci_states(self):
        replay = SceneReplay([self.result], self.config, [np.zeros(3)])
        replay.UpdateState(30000000000)
        i = int(np.argmin(abs(self.result.time - 30)))
        for bus, message in enumerate(replay.bus_msgs[0]):
            payload = message.read()
            np.testing.assert_allclose(
                payload.r_BN_N, self.result.positions[i, bus], atol=1e-9
            )
            np.testing.assert_allclose(
                payload.v_BN_N, self.result.velocities[i, bus], atol=1e-10
            )
            np.testing.assert_allclose(
                rbk.MRP2C(payload.sigma_BN),
                rbk.MRP2C(self.result.attitudes[i, bus]),
                atol=1e-12,
            )
        earth = replay.planets.messages[0].read()
        np.testing.assert_array_equal(earth.PositionVector, [0, 0, 0])
        rotation = np.asarray(earth.J20002Pfix)
        np.testing.assert_allclose(rotation @ rotation.T, np.eye(3), atol=1e-14)

    def test_orbital_force_step_convergence(self):
        coarse_config = replace(self.config, step_s=0.002, record_s=0.01)
        coarse = simulate(coarse_config, orbit=self.orbit)
        np.testing.assert_allclose(
            coarse.gap,
            np.interp(coarse.time, self.result.time, self.result.gap),
            atol=5e-4,
        )


if __name__ == "__main__":
    unittest.main()
