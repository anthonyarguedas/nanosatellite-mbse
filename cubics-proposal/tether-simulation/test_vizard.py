"""Check native Vizard geometry and playback without requiring the GUI."""

from dataclasses import replace
from pathlib import Path
import struct
import tempfile
import unittest

import numpy as np
from Basilisk.utilities import RigidBodyKinematics as rbk

from geometry import tether_nodes
from orbit_environment import OrbitConfig
from simulate import Config, simulate
from vizard_scene import (
    DISPLAY_ORIGIN,
    DISPLAY_VELOCITY,
    FRAME_NAME,
    SEGMENTS,
    SceneReplay,
    export_vizard,
)


def varint(data, offset):
    value, shift = 0, 0
    while True:
        byte = data[offset]
        offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
        shift += 7


def protobuf_fields(data):
    offset = 0
    while offset < len(data):
        key, offset = varint(data, offset)
        wire = key & 7
        if wire == 0:
            value, offset = varint(data, offset)
        elif wire in (1, 2, 5):
            if wire == 2:
                size, offset = varint(data, offset)
            else:
                size = 8 if wire == 1 else 4
            value = data[offset : offset + size]
            offset += size
        else:
            raise AssertionError(f"Unexpected protobuf wire type {wire}")
        yield key >> 3, value


def archive_frames(data):
    offset = 0
    while offset < len(data):
        size, offset = varint(data, offset)
        yield list(protobuf_fields(data[offset : offset + size]))
        offset += size


class VizardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = replace(Config(), duration_s=1.0)
        cls.result = simulate(cls.config)

    def test_tether_endpoints_and_arc(self):
        for gap in (0.0, 1.5, 3.0, 3.011):
            nodes = tether_nodes(gap, 3.0)
            np.testing.assert_allclose(
                nodes[[0, -1]], [[-gap / 2, 0, 0], [gap / 2, 0, 0]], atol=1e-12
            )
            chord_length = np.linalg.norm(np.diff(nodes, axis=0), axis=1).sum()
            self.assertAlmostEqual(chord_length, max(3.0, gap), delta=0.006)

    def test_native_bus_states_preserve_relative_motion(self):
        offset = np.array([2.1, 0.0, 0.0])
        replay = SceneReplay([self.result], self.config, [offset])
        replay.UpdateState(500000000)
        origin = DISPLAY_ORIGIN + 0.5 * DISPLAY_VELOCITY
        for i, message in enumerate(replay.bus_msgs[0]):
            payload = message.read()
            expected = np.array(
                [
                    np.interp(0.5, self.result.time, self.result.positions[:, i, axis])
                    for axis in range(3)
                ]
            )
            np.testing.assert_allclose(
                np.array(payload.r_BN_N) - origin - offset, expected
            )
            np.testing.assert_allclose(
                payload.v_BN_N, self.result.velocities[100, i] + DISPLAY_VELOCITY
            )

    def test_native_segment_poses_follow_curve(self):
        replay = SceneReplay([self.result], self.config, [np.zeros(3)])
        replay.UpdateState(500000000)
        gap = float(np.interp(0.5, self.result.time, self.result.gap))
        nodes = tether_nodes(gap, 3.0, SEGMENTS)[:, [0, 2, 1]]
        origin = DISPLAY_ORIGIN + 0.5 * DISPLAY_VELOCITY
        for message, left, right in zip(replay.segment_msgs[0], nodes[:-1], nodes[1:]):
            payload = message.read()
            np.testing.assert_allclose(
                np.array(payload.r_BN_N) - origin, (left + right) / 2, atol=1e-12
            )
            direction = rbk.MRP2C(payload.sigma_BN).T @ [1, 0, 0]
            np.testing.assert_allclose(
                direction, (right - left) / np.linalg.norm(right - left), atol=1e-12
            )

    def test_native_archive_has_camera_settings_and_moving_objects(self):
        config = replace(self.config, duration_s=0.04)
        result = simulate(config)
        with tempfile.TemporaryDirectory() as directory:
            path = export_vizard([result], config, Path(directory) / "test.bin")
            frames = [
                [tag for tag, _ in frame] for frame in archive_frames(path.read_bytes())
            ]
            # VizInterface intentionally skips t=0. It writes 0.02 and 0.04 s.
            self.assertEqual(len(frames), 2)
            self.assertEqual(frames[0].count(3), SEGMENTS + 3)
            self.assertIn(4, frames[0])  # instrument camera configuration
            self.assertIn(7, frames[0])  # Vizard settings and model replacements
            self.assertEqual(frames[-1].count(3), SEGMENTS + 3)

    def test_orbital_archive_shares_display_parent_and_preserves_bus_motion(self):
        config = replace(self.config, duration_s=20.0, step_s=0.005, record_s=0.01)
        result = simulate(config, orbit=OrbitConfig())
        with tempfile.TemporaryDirectory() as directory:
            path = export_vizard([result], config, Path(directory) / "orbit.bin")
            frames = list(archive_frames(path.read_bytes()))

        endpoints = []
        for frame in (frames[0], frames[-1]):
            objects = {}
            for tag, body in frame:
                if tag == 3:
                    fields = dict(protobuf_fields(body))
                    objects[fields[1].decode()] = fields
            self.assertEqual(len(objects), SEGMENTS + 3)
            for name, fields in objects.items():
                # Field 19 sets the display hierarchy. Positions and attitudes
                # remain absolute ECI states, including for child objects.
                expected = b"" if name == FRAME_NAME else FRAME_NAME.encode()
                self.assertEqual(fields.get(19, b""), expected, name)
            endpoints.append(
                np.array(
                    [
                        struct.unpack("<3d", objects[name][2])
                        for name in ("CubeSat_A", "CubeSat_B")
                    ]
                )
            )

        np.testing.assert_allclose(endpoints[-1], result.positions[-1], atol=1e-9, rtol=0)
        first_distance, last_distance = (
            np.linalg.norm(positions[1] - positions[0]) for positions in endpoints
        )
        self.assertLess(first_distance, 0.18)
        self.assertGreater(last_distance, 2.0)


if __name__ == "__main__":
    unittest.main()
