"""Compiled display-only segment poses. No spacecraft dynamics are changed."""

import numpy as np
from numba import njit


@njit(cache=True)
def rotation_to_mrp(rotation):
    """MRP of the passive DCM rotation.T, matching Basilisk C2MRP."""
    r = rotation
    trace = r[0, 0] + r[1, 1] + r[2, 2]
    if trace > 0:
        s = 2 * np.sqrt(1 + trace)
        w, x, y, z = (
            s / 4,
            (r[2, 1] - r[1, 2]) / s,
            (r[0, 2] - r[2, 0]) / s,
            (r[1, 0] - r[0, 1]) / s,
        )
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        s = 2 * np.sqrt(1 + r[0, 0] - r[1, 1] - r[2, 2])
        w, x, y, z = (
            (r[2, 1] - r[1, 2]) / s,
            s / 4,
            (r[0, 1] + r[1, 0]) / s,
            (r[0, 2] + r[2, 0]) / s,
        )
    elif r[1, 1] > r[2, 2]:
        s = 2 * np.sqrt(1 + r[1, 1] - r[0, 0] - r[2, 2])
        w, x, y, z = (
            (r[0, 2] - r[2, 0]) / s,
            (r[0, 1] + r[1, 0]) / s,
            s / 4,
            (r[1, 2] + r[2, 1]) / s,
        )
    else:
        s = 2 * np.sqrt(1 + r[2, 2] - r[0, 0] - r[1, 1])
        w, x, y, z = (
            (r[1, 0] - r[0, 1]) / s,
            (r[0, 2] + r[2, 0]) / s,
            (r[1, 2] + r[2, 1]) / s,
            s / 4,
        )
    sign = 1.0 if w >= 0 else -1.0
    return np.array([sign * x, sign * y, sign * z]) / (1 + sign * w)


@njit(cache=True)
def segment_poses(nodes, preferred_y):
    count = len(nodes) - 1
    centers, attitudes = np.empty((count, 3)), np.empty((count, 3))
    for i in range(count):
        centers[i] = (nodes[i] + nodes[i + 1]) / 2
        x = nodes[i + 1] - nodes[i]
        x /= np.linalg.norm(x)
        y = preferred_y - np.dot(preferred_y, x) * x
        if np.linalg.norm(y) < 1e-8:
            fallback = np.zeros(3)
            fallback[np.argmin(np.abs(x))] = 1
            y = fallback - np.dot(fallback, x) * x
        y /= np.linalg.norm(y)
        rotation = np.column_stack((x, y, np.cross(x, y)))
        attitudes[i] = rotation_to_mrp(rotation)
    return centers, attitudes
