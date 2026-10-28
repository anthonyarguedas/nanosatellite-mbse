"""Live drag and bounded-memory native replay checks for the three day run."""

from dataclasses import replace
import json
from pathlib import Path
import struct
import tempfile
import unittest

import numpy as np

from atmospheric_drag import MediumDrag
from fast_forces import rotation_from_mrp
from fast_scene import rotation_to_mrp
from geometry import slack_curve, tether_nodes
from Basilisk.utilities import RigidBodyKinematics as rbk
from mission_stream import StreamSettings, run_streaming
from orbit_environment import EARTH_MU, EARTH_RADIUS_M, EARTH_SPIN_RAD_S, OrbitConfig
from simulate import Config, simulate
from test_vizard import archive_frames, protobuf_fields
from vizard_scene import FRAME_NAME, SEGMENTS, LiveScene, SceneReplay


def drag_model():
    return MediumDrag([120000, 1000000], [1e-13, 1e-13], pair_area_m2=0.045218097245)


class DragTests(unittest.TestCase):
    def test_force_opposes_motion_relative_to_rotating_air(self):
        position, velocity = OrbitConfig().initial_state()
        states = np.zeros((2, 12))
        states[:, :3], states[:, 3:6] = position, velocity
        drag = drag_model()
        force = drag.forces(states, 0)
        relative = velocity - np.cross([0, 0, EARTH_SPIN_RAD_S], position)
        expected = (
            -0.5
            * drag.coefficient
            * drag.pair_area_m2
            / 2
            * 1e-13
            * np.linalg.norm(relative)
            * relative
        )
        np.testing.assert_allclose(force, [expected, expected], rtol=1e-13, atol=1e-20)
        self.assertLess(drag.power_w, 0)
        self.assertLess(np.dot(force[0], relative), 0)
        drag.forces(states, 10)
        self.assertAlmostEqual(drag.work_j, 10 * drag.power_w, places=13)

    def test_zero_relative_air_speed_gives_zero_force(self):
        states = np.zeros((2, 12))
        states[:, 0] = EARTH_RADIUS_M + 600000
        states[:, 4] = EARTH_SPIN_RAD_S * states[:, 0]
        np.testing.assert_array_equal(drag_model().forces(states, 0), 0)

    def test_drag_is_applied_to_the_integrated_orbit(self):
        config = Config(duration_s=20, step_s=0.005, record_s=0.1)
        orbit = OrbitConfig()
        # Deliberately stronger drag makes the live integration check measurable.
        drag = MediumDrag([120000, 1000000], [1e-9, 1e-9], pair_area_m2=0.045)
        reference = simulate(config, orbit=orbit)
        actual = simulate(config, orbit=orbit, drag=drag)

        def energy(result):
            radius = np.linalg.norm(result.positions[-1].mean(axis=0))
            velocity = result.velocities[-1].mean(axis=0)
            z = result.positions[-1].mean(axis=0)[2] / radius
            from orbit_environment import EARTH_J2

            potential = -EARTH_MU / radius + EARTH_MU * EARTH_J2 * EARTH_RADIUS_M**2 / (
                2 * radius**3
            ) * (3 * z * z - 1)
            return np.dot(velocity, velocity) / 2 + potential

        difference = (energy(actual) - energy(reference)) * 2 * config.mass_kg
        self.assertLess(difference, -1)
        self.assertAlmostEqual(difference, drag.work_j, delta=abs(drag.work_j) * 0.002)


class DisplayGeometryTests(unittest.TestCase):
    def test_compiled_nodes_match_the_original_polyline(self):
        for gap in (0, 0.1, 1.5, 2.9, 3, 3.01):
            x, y = slack_curve(gap, 3, points=513)
            arc = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
            targets = np.linspace(0, arc[-1], 33)
            expected = np.column_stack(
                (np.interp(targets, arc, x), np.interp(targets, arc, y), np.zeros(33))
            )
            np.testing.assert_allclose(
                tether_nodes(gap, 3, 32), expected, atol=1e-8, rtol=0
            )

    def test_compiled_attitudes_match_basilisk_rotations(self):
        rng = np.random.default_rng(42)
        for sigma in np.vstack((np.eye(3), -np.eye(3), rng.normal(size=(100, 3)))):
            rotation = rotation_from_mrp(sigma)
            actual = rotation_to_mrp(rotation)
            np.testing.assert_allclose(
                rbk.MRP2C(actual).T, rotation, atol=2e-14, rtol=0
            )


class StreamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config(duration_s=70, step_s=0.005, record_s=0.01)
        cls.orbit = OrbitConfig()
        cls.reference = simulate(cls.config, orbit=cls.orbit, drag=drag_model())
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.output = Path(cls.directory.name)
        cls.summary = run_streaming(
            cls.config, cls.orbit, cls.output, drag=drag_model()
        )
        cls.data = np.genfromtxt(cls.output / "mission.csv", delimiter=",", names=True)
        cls.frames = list(archive_frames((cls.output / "mission.bin").read_bytes()))

    def test_finishes_and_publishes_complete_files_atomically(self):
        self.assertEqual(self.summary["status"], "completed")
        self.assertEqual(self.data["time_s"][-1], 70)
        self.assertFalse(list(self.output.glob("*.part")))
        status = json.loads((self.output / "run_status.json").read_text())
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["simulated_time_s"], 70)
        self.assertEqual(
            json.loads((self.output / "results.json").read_text()), self.summary
        )

    def test_keeps_initial_release_and_real_later_contacts(self):
        self.assertLess(self.data["attachment_distance_m"][0], 1e-8)
        self.assertEqual(self.data["tension_n"][0], 0)
        self.assertGreater(self.data["attachment_distance_m"].max(), 3)
        self.assertGreater(self.data["tension_n"].max(), 1)
        first = self.summary["first_collision_event"]
        self.assertGreater(first["time_s"], 60)
        self.assertLess(first["time_s"], 62)
        self.assertLess(np.min(abs(self.data["time_s"] - first["time_s"])), 1e-10)
        self.assertGreater(self.summary["scenarios"][0]["collision_episodes"], 1)
        self.assertLess(self.summary["drag"]["drag_work_j"], 0)

    def test_streaming_does_not_change_live_dynamics(self):
        matched = 0
        for row in self.data[::7]:
            index = np.argmin(abs(self.reference.time - row["time_s"]))
            if abs(self.reference.time[index] - row["time_s"]) > 1e-9:
                continue
            matched += 1
            for bus, name in enumerate(("A", "B")):
                actual = [row[f"position_{name}_{axis}"] for axis in ("x", "y", "z")]
                np.testing.assert_allclose(
                    actual, self.reference.positions[index, bus], atol=1e-7, rtol=0
                )
        self.assertGreater(matched, 200)

    def test_native_file_uses_the_same_time_and_states_as_csv(self):
        for frame in (
            self.frames[0],
            self.frames[len(self.frames) // 2],
            self.frames[-1],
        ):
            fields = dict(frame)
            clock = dict(protobuf_fields(fields[1]))
            time = struct.unpack("<d", clock[2])[0] * 1e-9
            row = self.data[np.argmin(abs(self.data["time_s"] - time))]
            self.assertAlmostEqual(row["time_s"], time, places=9)
            objects = [dict(protobuf_fields(body)) for tag, body in frame if tag == 3]
            self.assertEqual(len(objects), SEGMENTS + 3)
            for obj in objects:
                name = obj[1].decode()
                self.assertEqual(
                    obj.get(19, b""), b"" if name == FRAME_NAME else FRAME_NAME.encode()
                )
                if name in ("CubeSat_A", "CubeSat_B"):
                    expected = [
                        row[f"position_{name[-1]}_{axis}"] for axis in ("x", "y", "z")
                    ]
                    np.testing.assert_allclose(
                        struct.unpack("<3d", obj[2]), expected, atol=1e-7, rtol=0
                    )
        last_clock = dict(protobuf_fields(dict(self.frames[-1])[1]))
        self.assertEqual(struct.unpack("<d", last_clock[2])[0], 70e9)

    def test_collision_log_is_complete_after_memory_is_drained(self):
        events = [
            json.loads(line)
            for line in (self.output / "collision_events.jsonl")
            .read_text()
            .splitlines()
        ]
        self.assertEqual(len(events), self.summary["logged_collision_episodes"])
        self.assertEqual(
            len(events), self.summary["scenarios"][0]["collision_episodes"]
        )
        self.assertEqual(events, self.reference.collision_events)

    def test_live_geometry_matches_the_existing_orbital_replay(self):
        index = np.argmin(abs(self.reference.time - 30))
        nanos = int(round(self.reference.time[index] * 1e9))
        states = np.column_stack(
            (
                self.reference.positions[index],
                self.reference.velocities[index],
                self.reference.attitudes[index],
                self.reference.angular_velocities[index],
            )
        )
        scene = LiveScene(self.config, self.orbit)
        scene.write(states, nanos)
        replay = SceneReplay([self.reference], self.config, [np.zeros(3)])
        replay.UpdateState(nanos)
        for live, recorded in zip(scene.segment_msgs[0], replay.segment_msgs[0]):
            np.testing.assert_allclose(
                live.read().r_BN_N, recorded.read().r_BN_N, atol=1e-8, rtol=0
            )
            np.testing.assert_allclose(
                live.read().sigma_BN, recorded.read().sigma_BN, atol=1e-12, rtol=0
            )

    def test_settings_reject_output_faster_than_dynamics(self):
        with self.assertRaises(ValueError):
            replace(StreamSettings(), initial_s=0.001).validate(self.config)


if __name__ == "__main__":
    unittest.main()
