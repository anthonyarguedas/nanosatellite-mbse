"""Fixed geometry and full-orbit illumination summaries.

Freimann et al. (2019), Sec. II.i: max(0, panel normal dot Sun direction).
Qureshi (2020), Sec. 2.2: separate panel projection and Earth shadow.
The Keplerian orbit and cylindrical shadow match sizing.py. All changing
positions, shadow boundaries and projections remain internal to this script.
"""

import math
from typing import NamedTuple, Tuple

from framework.models.geometry import Face, Pointing
from . import sizing

Vector = Tuple[float, float, float]
_TAU = 2 * math.pi


class Dimensions(NamedTuple):
    x: float
    y: float
    z: float


class Normal(NamedTuple):
    vector: Vector


class Projection(NamedTuple):
    sunlight_mean: float
    projected_sunlight_duration: float


def cubesat_dimensions(units: float) -> Dimensions:
    """Nominal 10 cm unit layouts in m. These are allocation boxes, excluding rails."""
    layouts = {1: (1, 1, 1), 1.5: (1, 1, 1.5), 2: (1, 1, 2),
               3: (1, 1, 3), 6: (2, 1, 3), 12: (2, 2, 3)}
    if type(units) not in (int, float) or units not in layouts:
        raise ValueError("Supported nominal layouts are 1U, 1.5U, 2U, 3U, 6U and 12U. Supply other dimensions explicitly.")
    return Dimensions(*(0.1 * count for count in layouts[units]))


def face_normal(face: str) -> Normal:
    """Outward unit normal in the body frame."""
    return Normal(Face(face).normal)


def face_area(face: str, length_x: float, length_y: float, length_z: float) -> sizing.Area:
    """Gross face area of a rectangular body, in m2."""
    sizing._finite(length_x, length_y, length_z)
    if min(length_x, length_y, length_z) <= 0:
        raise ValueError("Body dimensions must be positive.")
    lengths = (length_x, length_y, length_z)
    axis = "XYZ".index(Face(face).value[1])
    area = math.prod(length for index, length in enumerate(lengths) if index != axis)
    sizing._finite(area)
    return sizing.Area(area)


def _dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def _unit(vector):
    if len(vector) != 3:
        raise ValueError("A panel normal needs three body-frame components.")
    sizing._finite(*vector)
    scale = max(abs(value) for value in vector)
    if scale == 0:
        raise ValueError("A panel normal must be nonzero.")
    scaled = tuple(value / scale for value in vector)
    norm = math.sqrt(_dot(scaled, scaled))
    return tuple(value / norm for value in scaled)


def _nadir_normal(normal, pointing_face, clocking_angle):
    """Normal in radial-outward, along-track, orbit-normal coordinates.

    The pointing face is aligned with -radial. At zero clocking, the next
    cyclic positive body axis (Y for +/-X, Z for +/-Y, X for +/-Z) aligns
    with along-track. Clocking is right-handed about the pointing direction.
    """
    target = pointing_face.normal
    axis = "XYZ".index(pointing_face.value[1])
    reference = tuple(1 if index == (axis + 1) % 3 else 0 for index in range(3))
    cross = (target[1] * reference[2] - target[2] * reference[1],
             target[2] * reference[0] - target[0] * reference[2],
             target[0] * reference[1] - target[1] * reference[0])
    a, b, c = _dot(normal, target), _dot(normal, reference), _dot(normal, cross)
    angle = math.radians(clocking_angle % 360)
    return (-a, b * math.cos(angle) - c * math.sin(angle),
            -b * math.sin(angle) - c * math.cos(angle))


def _eccentric_anomaly(true_anomaly, eccentricity):
    turns = math.floor((true_anomaly + math.pi) / _TAU)
    angle = true_anomaly - turns * _TAU
    return math.atan2(math.sqrt((1 - eccentricity) * (1 + eccentricity)) * math.sin(angle),
                      eccentricity + math.cos(angle)) + turns * _TAU


def _positive_integral(a, b, c, start, end):
    """Exact integral of max(0, a cos(E) + b sin(E) + c)."""
    cuts = [start, end]
    amplitude = math.hypot(a, b)
    if abs(c) < amplitude:
        phase = math.atan2(b, a)
        offset = math.acos(-c / amplitude)
        for root in (phase - offset, phase + offset):
            for turn in range(math.floor((start - root) / _TAU), math.ceil((end - root) / _TAU) + 1):
                angle = root + turn * _TAU
                if start < angle < end:
                    cuts.append(angle)
    integral = 0.0
    cuts.sort()
    for left, right in zip(cuts, cuts[1:]):
        middle, span = (left + right) / 2, right - left
        value = a * math.cos(middle) + b * math.sin(middle)
        if value + c > 0:
            integral += max(0.0, 2 * math.sin(span / 2) * value + c * span)
    return integral


def orbital_projection(semimajor_axis: float, eccentricity: float, earth_radius: float,
                       beta_angle: float, sun_projection_angle: float, period: float,
                       normal_body: Vector, pointing: str, pointing_face: str,
                       clocking_angle: float) -> Projection:
    """One unobstructed section, averaged over sunlight in one complete orbit.

    NADIR fixes the declared face toward Earth and its clocking in the local
    orbital frame. SUN_POINTING keeps the declared face toward the Sun.
    Neither law models slew, pointing error or attitude dynamics.
    No initial phase or epoch is needed for these complete-orbit averages.
    """
    sizing._orbit(semimajor_axis, eccentricity, earth_radius)
    sizing._illumination_inputs(semimajor_axis, earth_radius, beta_angle, period)
    sizing._finite(sun_projection_angle, clocking_angle)
    normal = _unit(normal_body)
    pointing, pointing_face = Pointing(pointing), Face(pointing_face)
    circular = eccentricity == 0 or abs(beta_angle) == 90
    if circular:
        durations = sizing.circular_illumination(semimajor_axis, earth_radius, beta_angle, period)
    else:
        durations = sizing.eccentric_illumination(
            semimajor_axis, eccentricity, earth_radius, beta_angle, sun_projection_angle, period)
    if pointing is Pointing.SUN_POINTING:
        mean = max(0.0, min(1.0, _dot(normal, pointing_face.normal)))
        return Projection(mean, mean * durations.sunlight)

    radial, along_track, orbit_normal = _nadir_normal(normal, pointing_face, clocking_angle)
    beta, sun_angle = math.radians(beta_angle), math.radians(sun_projection_angle % 360)
    cos_beta = 0.0 if abs(beta_angle) == 90 else math.cos(beta)
    # c(nu) = A cos(nu) + B sin(nu) + C. With dt = (1-e cos(E))/n dE,
    # the projected time integrand is max(0, a cos(E) + b sin(E) + c).
    a_true = cos_beta * (radial * math.cos(sun_angle) + along_track * math.sin(sun_angle))
    b_true = cos_beta * (radial * math.sin(sun_angle) - along_track * math.cos(sun_angle))
    c_true = orbit_normal * math.sin(beta)
    a = a_true - eccentricity * c_true
    b = math.sqrt((1 - eccentricity) * (1 + eccentricity)) * b_true
    c = c_true - eccentricity * a_true

    shadow = []
    if durations.eclipse > 0:
        if eccentricity == 0:
            half_width = math.pi * durations.eclipse / period
            shadow = [(sun_angle + math.pi - half_width, sun_angle + math.pi + half_width)]
        else:
            shadow = [(sun_angle + math.pi + 2 * math.atan(entry),
                       sun_angle + math.pi + 2 * math.atan(exit))
                      for entry, exit in sizing._shadow_intervals(
                          semimajor_axis, eccentricity, earth_radius, beta_angle, sun_projection_angle)]
    # Integrate only the sunlit arcs, split at each zero of panel projection.
    integral, start = 0.0, sun_angle
    for entry, exit in (*shadow, (sun_angle + _TAU, sun_angle + _TAU)):
        integral += _positive_integral(a, b, c, _eccentric_anomaly(start, eccentricity),
                                       _eccentric_anomaly(entry, eccentricity))
        start = exit
    projected_duration = period * integral / _TAU
    mean = projected_duration / durations.sunlight
    sizing._finite(mean, projected_duration)
    if not -1e-12 <= mean <= 1 + 1e-12:
        raise ArithmeticError("Integrated sunlight projection lies outside [0, 1].")
    mean = min(1.0, max(0.0, mean))
    return Projection(mean, mean * durations.sunlight)
