"""Schematic tether geometry for native Vizard scenes."""

import numpy as np
from numba import njit


_CURVE_S = np.linspace(0.0, 1.0, 513)
_CURVE_SIN = np.sin(2 * np.pi * _CURVE_S)
_CURVE_COS = np.cos(2 * np.pi * _CURVE_S)


def slack_curve(gap: float, length: float, points: int = 121):
    """Loop with the requested polyline arc length, without sag physics."""
    s = np.linspace(0.0, 1.0, points)
    gap = max(0.0, gap)
    if gap >= length:
        return np.array([-gap / 2, gap / 2]), np.zeros(2)

    def curve(amplitude):
        return gap * (s - 0.5) + amplitude * np.sin(2 * np.pi * s), -amplitude * (
            1 - np.cos(2 * np.pi * s)
        )

    low, high = 0.0, length
    for _ in range(30):
        middle = (low + high) / 2
        x, y = curve(middle)
        arc = np.hypot(np.diff(x), np.diff(y)).sum()
        if arc < length:
            low = middle
        else:
            high = middle
    return curve((low + high) / 2)


@njit(cache=True)
def tether_nodes(gap: float, length: float, segments: int = 64) -> np.ndarray:
    """The same equal-arc polyline, compiled for long native recordings."""
    gap = max(0.0, gap)
    nodes = np.zeros((segments + 1, 3))
    if gap >= length:
        for i in range(segments + 1):
            nodes[i, 0] = gap * (i / segments - 0.5)
        return nodes
    low, high = 0.0, length
    for _ in range(30):
        amplitude = (low + high) / 2
        arc_length = 0.0
        for i in range(512):
            dx = gap / 512 + amplitude * (_CURVE_SIN[i + 1] - _CURVE_SIN[i])
            dy = amplitude * (_CURVE_COS[i + 1] - _CURVE_COS[i])
            arc_length += np.hypot(dx, dy)
        if arc_length < length:
            low = amplitude
        else:
            high = amplitude
    amplitude = (low + high) / 2
    x = gap * (_CURVE_S - 0.5) + amplitude * _CURVE_SIN
    y = -amplitude * (1 - _CURVE_COS)
    arc = np.zeros(513)
    for i in range(512):
        arc[i + 1] = arc[i] + np.hypot(x[i + 1] - x[i], y[i + 1] - y[i])
    targets = np.linspace(0.0, arc[-1], segments + 1)
    nodes[:, 0], nodes[:, 1] = np.interp(targets, arc, x), np.interp(targets, arc, y)
    return nodes
