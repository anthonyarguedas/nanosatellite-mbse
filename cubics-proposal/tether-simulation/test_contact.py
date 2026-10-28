"""Rigid contact and continuity checks beyond the original 50 s cutoff."""

import unittest

import numpy as np
from Basilisk.utilities import RigidBodyKinematics as rbk

from contact import box_contact, normal_impulse
from fast_forces import rotation_from_mrp
from orbit_environment import OrbitConfig, propagate_reference
from simulate import Config, simulate
from vizard_scene import SceneReplay, visualization_times


class ContactTests(unittest.TestCase):
    def setUp(self):
        self.mass = 3.0
        self.half = np.array([0.0851, 0.05, 0.05])
        self.inertia = (
            self.mass
            / 3
            * np.diag([0.05**2 + 0.05**2, 0.0851**2 + 0.05**2, 0.0851**2 + 0.05**2])
        )
        self.rotations = np.array([np.eye(3), np.eye(3)])
        self.positions = np.array([[0.0, 0.0, 0.0], [0.1692, 0.0, 0.0]])

    def test_compiled_rotation_matches_basilisk(self):
        for sigma in ([0.1, 0.2, -0.3], [1.2, -0.5, 0.3], [0.0, 0.0, 0.0]):
            np.testing.assert_allclose(
                rotation_from_mrp(np.array(sigma)), rbk.MRP2C(sigma).T, atol=1e-14
            )

    def test_faces_and_separated_rotated_boxes(self):
        contact = box_contact(self.positions, self.rotations, self.half)
        self.assertIsNotNone(contact)
        self.assertAlmostEqual(contact.penetration, 0.001, places=12)
        np.testing.assert_allclose(contact.normal, [1, 0, 0])
        np.testing.assert_allclose(contact.point[1:], 0, atol=1e-12)
        rotated = self.rotations.copy()
        rotated[1] = rbk.MRP2C([0, 0, np.tan(np.pi / 8)]).T
        self.assertIsNone(
            box_contact(np.array([[0.0, 0, 0], [0.14, 0, 0]]), rotated, self.half)
        )
        self.assertIsNotNone(
            box_contact(np.array([[0.0, 0, 0], [0.13, 0, 0]]), rotated, self.half)
        )

    def test_head_on_restitution_and_energy(self):
        velocities = np.array([[0.05, 0, 0], [-0.05, 0, 0]])
        contact = box_contact(self.positions, self.rotations, self.half)
        v, omega, impulse, speed, loss = normal_impulse(
            self.positions,
            velocities,
            self.rotations,
            np.zeros((2, 3)),
            self.inertia,
            self.mass,
            contact,
            0.3,
        )
        np.testing.assert_allclose(v, [[-0.015, 0, 0], [0.015, 0, 0]], atol=1e-14)
        np.testing.assert_array_equal(omega, 0)
        np.testing.assert_allclose(v.sum(axis=0), 0, atol=1e-14)
        self.assertAlmostEqual(speed, -0.1)
        self.assertAlmostEqual(impulse, 0.195)
        self.assertAlmostEqual(loss, 0.0075 * (1 - 0.3**2))

    def test_separating_contact_does_not_get_another_bounce(self):
        velocities = np.array([[-0.05, 0, 0], [0.05, 0, 0]])
        contact = box_contact(self.positions, self.rotations, self.half)
        v, _, impulse, _, loss = normal_impulse(
            self.positions,
            velocities,
            self.rotations,
            np.zeros((2, 3)),
            self.inertia,
            self.mass,
            contact,
            0.3,
        )
        np.testing.assert_array_equal(v, velocities)
        self.assertEqual(impulse, 0)
        self.assertEqual(loss, 0)

    def test_off_center_impulse_preserves_angular_momentum(self):
        rotations = self.rotations.copy()
        rotations[1] = rbk.MRP2C([0, 0, np.tan(np.pi / 16)]).T
        positions = np.array([[0.0, 0, 0], [0.16, 0.02, 0]])
        velocities = np.array([[0.05, 0, 0], [-0.05, 0, 0]])
        contact = box_contact(positions, rotations, self.half)
        self.assertIsNotNone(contact)
        v, omega, impulse, _, _ = normal_impulse(
            positions,
            velocities,
            rotations,
            np.zeros((2, 3)),
            self.inertia,
            self.mass,
            contact,
            0.3,
        )
        relative_r = positions - positions.mean(axis=0)
        before = self.mass * np.cross(relative_r, velocities).sum(axis=0)
        after = self.mass * np.cross(relative_r, v).sum(axis=0)
        for b in range(2):
            after += rotations[b] @ self.inertia @ omega[b]
        np.testing.assert_allclose(after, before, atol=1e-13)
        self.assertGreater(impulse, 0)
        self.assertGreater(np.linalg.norm(omega), 0)


class ContinuousMissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config(duration_s=180.0, step_s=0.005, record_s=0.01)
        cls.orbit = OrbitConfig()
        cls.result = simulate(cls.config, orbit=cls.orbit)

    def test_continues_through_real_impacts(self):
        self.assertEqual(self.result.time[-1], 180.0)
        self.assertTrue(np.isfinite(self.result.positions).all())
        self.assertTrue(np.isfinite(self.result.angular_velocities).all())
        self.assertGreater(len(self.result.collision_events), 0)
        first = self.result.collision_events[0]["time_s"]
        self.assertGreater(first, 50.0)
        self.assertLess(first, 80.0)
        self.assertGreater(self.result.contact_statistics["kinetic_energy_lost_j"], 0)
        self.assertLess(self.result.contact_statistics["maximum_penetration_m"], 0.001)

    def test_contact_does_not_restart_the_common_orbit(self):
        ref = propagate_reference(
            self.orbit, periods=180 / self.orbit.period_s, step_s=self.config.step_s
        )
        center = self.result.positions.mean(axis=1)
        indices = np.rint(self.result.time / self.config.step_s).astype(int)
        np.testing.assert_allclose(center, ref.positions[indices], atol=0.0005, rtol=0)

    def test_recorded_boxes_do_not_pass_through_each_other(self):
        half = (
            np.array(
                [
                    self.config.body_length_m,
                    self.config.body_width_m,
                    self.config.body_height_m,
                ]
            )
            / 2
        )
        distance = np.linalg.norm(
            self.result.positions[:, 1] - self.result.positions[:, 0], axis=1
        )
        near = np.flatnonzero(distance < 2 * np.linalg.norm(half))
        for i in near[::5]:
            rotations = np.array([rbk.MRP2C(s).T for s in self.result.attitudes[i]])
            contact = box_contact(self.result.positions[i], rotations, half)
            if contact is not None:
                self.assertLess(contact.penetration, 2e-6)

    def test_archive_times_include_impacts_and_end(self):
        times = visualization_times(self.result, self.config)
        self.assertEqual(times[-1], 180000000000)
        self.assertTrue(np.all(np.diff(times) > 0))
        self.assertGreater(np.max(np.diff(times)), 100000000)
        for event in self.result.collision_events:
            self.assertIn(int(round(event["time_s"] * 1e9)), times)
            if abs(event["initial_normal_speed_m_s"]) > 1e-4:
                self.assertLess(np.min(abs(self.result.time - event["time_s"])), 1e-10)

    def test_vizard_replays_the_actual_post_collision_states(self):
        i = np.searchsorted(self.result.time, 100.0)
        nanos = int(round(self.result.time[i] * 1e9))
        replay = SceneReplay([self.result], self.config, [np.zeros(3)])
        replay.UpdateState(nanos)
        for b, message in enumerate(replay.bus_msgs[0]):
            np.testing.assert_allclose(
                message.read().r_BN_N, self.result.positions[i, b], atol=1e-8
            )
            np.testing.assert_allclose(
                message.read().v_BN_N, self.result.velocities[i, b], atol=1e-10
            )

    def test_release_spring_never_refires_on_contact(self):
        result = simulate(self.config)
        self.assertEqual(len(result.collision_events), 1)
        self.assertAlmostEqual(
            result.energy[-1],
            self.config.spring_energy_j * self.config.restitution**2,
            delta=2e-7,
        )
        self.assertLess(result.energy[-1], self.config.spring_energy_j / 5)


if __name__ == "__main__":
    unittest.main()
