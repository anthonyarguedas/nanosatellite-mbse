"""Analytical regression checks for the gravity free tether deployment."""

from dataclasses import replace
import unittest

import numpy as np

from geometry import slack_curve
from simulate import Config, simulate


class DeploymentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config()
        cls.result = simulate(cls.config)

    def test_mass_spring_and_initial_geometry(self):
        c = self.config
        self.assertEqual(c.mass_kg, 3.0)
        self.assertAlmostEqual(c.spring_energy_j, 0.0075)
        self.assertAlmostEqual(c.spring_stiffness_n_m, 37.5)
        self.assertAlmostEqual(c.tether_stiffness_n_m, 130.8996939, places=6)
        self.assertAlmostEqual(self.result.gap[0], 0.0, places=12)
        np.testing.assert_array_equal(self.result.velocities[0], np.zeros((2, 3)))

    def test_speed_limit(self):
        self.assertLessEqual(
            np.abs(self.result.speed).max(), self.config.max_relative_speed_m_s + 1e-7
        )
        self.assertLessEqual(np.abs(self.result.velocities).max(), 0.05 + 1e-7)

    def test_analytic_tether_catch(self):
        c = self.config
        release_time = np.pi / 2 * np.sqrt(c.reduced_mass_kg / c.spring_stiffness_n_m)
        catch_time = (
            release_time
            + (c.tether_length_m - c.spring_stroke_m) / c.max_relative_speed_m_s
        )
        self.assertAlmostEqual(
            self.result.summary(c)["first_taut_s"], catch_time, delta=0.0002
        )
        extension = c.max_relative_speed_m_s * np.sqrt(
            c.reduced_mass_kg / c.tether_stiffness_n_m
        )
        self.assertAlmostEqual(
            self.result.gap.max(), c.tether_length_m + extension, delta=3e-6
        )
        self.assertAlmostEqual(
            self.result.tension.max(), c.tether_stiffness_n_m * extension, delta=5e-4
        )
        self.assertLess(self.result.speed[-1], -0.0999)
        self.assertLess(self.result.gap[-1], c.tether_length_m)

    def test_tether_is_unilateral(self):
        self.assertTrue(np.all(self.result.tension >= 0))
        np.testing.assert_array_equal(
            self.result.tension[self.result.gap <= self.config.tether_length_m], 0
        )

    def test_momentum_and_transverse_motion(self):
        np.testing.assert_allclose(self.result.positions.sum(axis=1), 0, atol=1e-12)
        np.testing.assert_allclose(self.result.velocities.sum(axis=1), 0, atol=1e-12)
        np.testing.assert_array_equal(self.result.positions[:, :, 1:], 0)
        np.testing.assert_array_equal(self.result.velocities[:, :, 1:], 0)

    def test_conservative_energy(self):
        self.assertLess(
            np.abs(self.result.energy / self.config.spring_energy_j - 1).max(), 5e-5
        )

    def test_step_convergence(self):
        coarse = replace(self.config, step_s=0.002, record_s=0.01)
        result = simulate(coarse)
        np.testing.assert_allclose(
            result.gap,
            np.interp(result.time, self.result.time, self.result.gap),
            atol=1.2e-4,
        )
        np.testing.assert_allclose(
            result.speed,
            np.interp(result.time, self.result.time, self.result.speed),
            atol=2e-5,
        )

    def test_drawn_slack_length(self):
        for gap in (0.0, 0.2, 1.5, 2.99):
            x, y = slack_curve(gap, self.config.tether_length_m)
            self.assertAlmostEqual(
                np.hypot(np.diff(x), np.diff(y)).sum(), 3.0, places=7
            )
            self.assertAlmostEqual(x[-1] - x[0], gap, places=12)
            self.assertAlmostEqual(y[0], 0.0)
            self.assertAlmostEqual(y[-1], 0.0)

    def test_invalid_configuration(self):
        for config in (
            replace(self.config, mass_kg=-1),
            replace(self.config, step_s=0.1),
            replace(self.config, spring_stroke_m=4),
            replace(self.config, max_relative_speed_m_s=float("nan")),
        ):
            with self.assertRaises(ValueError):
                config.validate()


if __name__ == "__main__":
    unittest.main()
