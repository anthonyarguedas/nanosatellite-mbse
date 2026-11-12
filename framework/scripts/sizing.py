"""Preliminary EPS sizing from final_report/design-proposal.tex.

Keplerian orbit, spherical Earth, cylindrical shadow and a fixed Sun per orbit.
Public angle inputs are in degrees to match Orbit's annotations.
"""

import math
from typing import NamedTuple


class OrbitalPeriod(NamedTuple):
    seconds: float


class Illumination(NamedTuple):
    eclipse: float
    sunlight: float


class Energy(NamedTuple):
    joules: float


class Power(NamedTuple):
    watts: float


class CellCount(NamedTuple):
    fractional: float
    required: int


class MissionCycles(NamedTuple):
    cycles: float


class DepthOfDischarge(NamedTuple):
    fraction: float


class RetainedValue(NamedTuple):
    retained: float


class Area(NamedTuple):
    square_metres: float


class Efficiency(NamedTuple):
    fraction: float


class PowerDensity(NamedTuple):
    watts_per_square_metre: float


def _finite(*values):
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Sizing inputs and results must be finite.")


def _orbit(semimajor_axis, eccentricity, earth_radius):
    _finite(semimajor_axis, eccentricity, earth_radius)
    if earth_radius <= 0 or not 0 <= eccentricity < 1:
        raise ValueError("Require a positive Earth radius and 0 <= eccentricity < 1.")
    if semimajor_axis * (1 - eccentricity) <= earth_radius:
        raise ValueError("The orbit's perigee must lie above the spherical Earth.")


def _illumination_inputs(semimajor_axis, earth_radius, beta_angle, period):
    _finite(semimajor_axis, earth_radius, beta_angle, period)
    if not -90 <= beta_angle <= 90 or period <= 0 or semimajor_axis <= earth_radius or earth_radius <= 0:
        raise ValueError("Require a positive period, radius above Earth and beta in [-90, 90] degrees.")


def orbit_period(semimajor_axis: float, eccentricity: float, earth_radius: float,
                 gravitational_parameter: float) -> OrbitalPeriod:
    _orbit(semimajor_axis, eccentricity, earth_radius)
    _finite(gravitational_parameter)
    if gravitational_parameter <= 0:
        raise ValueError("The gravitational parameter must be positive.")
    period = 2 * math.pi * semimajor_axis * math.sqrt(semimajor_axis / gravitational_parameter)
    _finite(period)
    if period <= 0:
        raise ValueError("The orbital period is below floating point range.")
    return OrbitalPeriod(period)


def circular_illumination(semimajor_axis: float, earth_radius: float,
                          beta_angle: float, period: float) -> Illumination:
    _illumination_inputs(semimajor_axis, earth_radius, beta_angle, period)
    if abs(beta_angle) == 90:
        return Illumination(0.0, period)
    beta = math.radians(beta_angle)
    radius_ratio = earth_radius / semimajor_axis
    shadow_ratio = abs(math.sin(beta)) / radius_ratio
    # Treat a contact within floating point roundoff as a zero-duration eclipse.
    if shadow_ratio >= 1 - 2e-15:
        return Illumination(0.0, period)
    sine = radius_ratio * math.sqrt((1 - shadow_ratio) * (1 + shadow_ratio)) / math.cos(beta)
    eclipse = period * (math.asin(min(1.0, sine)) / math.pi)
    return Illumination(eclipse, period - eclipse)


def _polynomial(coefficients, value):
    result = 0.0
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def _bisect(coefficients, left, right):
    initial = _polynomial(coefficients, left)
    for _ in range(128):
        middle = (left + right) / 2
        if middle == left or middle == right:
            break
        value = _polynomial(coefficients, middle)
        if value == 0:
            return middle
        if (value > 0) == (initial > 0):
            left, initial = middle, value
        else:
            right = middle
    return (left + right) / 2


def _roots(coefficients, left, right):
    """Isolate real polynomial roots through derivative roots, without a grid."""
    coefficients = list(coefficients)
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    if len(coefficients) == 1:
        return []
    if len(coefficients) == 2:
        root = -coefficients[0] / coefficients[1]
        return [root] if left <= root <= right else []
    derivative = [index * coefficient for index, coefficient in enumerate(coefficients)][1:]
    points = [left, *_roots(derivative, left, right), right]
    roots = [point for point in points if _polynomial(coefficients, point) == 0]
    for lower, upper in zip(points, points[1:]):
        if _polynomial(coefficients, lower) * _polynomial(coefficients, upper) < 0:
            roots.append(_bisect(coefficients, lower, upper))
    unique = []
    for root in sorted(roots):
        if not unique or root != unique[-1]:
            unique.append(root)
    return unique


def _mean_anomaly(t, eccentricity, cos_lambda, sin_lambda):
    # Resolve nu = lambda + pi + 2 atan(t) without losing small shadow arcs
    # by first adding them to pi, particularly near an eccentric apogee.
    cos_x, sin_x = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    cos_nu = -(cos_lambda * cos_x - sin_lambda * sin_x)
    sin_nu = -(sin_lambda * cos_x + cos_lambda * sin_x)
    anomaly = math.atan2(
        math.sqrt((1 - eccentricity) * (1 + eccentricity)) * sin_nu,
        eccentricity + cos_nu,
    )
    return anomaly - eccentricity * math.sin(anomaly)


def eccentric_illumination(semimajor_axis: float, eccentricity: float, earth_radius: float,
                           beta_angle: float, sun_projection_angle: float,
                           period: float) -> Illumination:
    _orbit(semimajor_axis, eccentricity, earth_radius)
    _illumination_inputs(semimajor_axis, earth_radius, beta_angle, period)
    _finite(sun_projection_angle)
    if abs(beta_angle) == 90:
        return Illumination(0.0, period)
    angle = math.radians(sun_projection_angle % 360)
    beta = math.radians(beta_angle)
    p = semimajor_axis * (1 - eccentricity) * (1 + eccentricity)
    q = (p / earth_radius) ** 2
    s = math.sin(beta) ** 2
    cos_lambda, sin_lambda = math.cos(angle), math.sin(angle)
    a, b, c = 1 - eccentricity * cos_lambda, 2 * eccentricity * sin_lambda, 1 + eccentricity * cos_lambda
    # Set x = nu - lambda - pi on the night side and t = tan(x/2).
    # Multiplication by (1+t^2)^2 turns the shadow boundary into this quartic.
    coefficients = [q * s - a * a, -2 * a * b, q * (4 - 2 * s) - b * b - 2 * a * c, -2 * b * c, q * s - c * c]
    _finite(*coefficients)
    scale = max(abs(value) for value in coefficients)
    coefficients = [value / scale for value in coefficients]
    boundaries = [-1.0, *(root for root in _roots(coefficients, -1.0, 1.0) if -1 < root < 1), 1.0]
    mean_span = 0.0
    for entry, exit in zip(boundaries, boundaries[1:]):
        if _polynomial(coefficients, (entry + exit) / 2) < 0:
            start = _mean_anomaly(entry, eccentricity, cos_lambda, sin_lambda)
            end = _mean_anomaly(exit, eccentricity, cos_lambda, sin_lambda)
            mean_span += (end - start) % (2 * math.pi)
    eclipse = min(period, max(0.0, period * (mean_span / (2 * math.pi))))
    return Illumination(eclipse, period - eclipse)


def load_energy(average_power: float, duration: float) -> Energy:
    _finite(average_power, duration)
    if average_power < 0 or duration < 0:
        raise ValueError("Average load power and duration must be nonnegative.")
    energy = average_power * duration
    _finite(energy)
    return Energy(energy)


def minimum_panel_power(sunlight_energy: float, eclipse_energy: float,
                        sunlight_efficiency: float, eclipse_efficiency: float,
                        sunlight_duration: float) -> Power:
    _finite(sunlight_energy, eclipse_energy, sunlight_efficiency, eclipse_efficiency, sunlight_duration)
    if sunlight_energy < 0 or eclipse_energy < 0 or sunlight_duration <= 0:
        raise ValueError("Require nonnegative load energies and positive sunlight duration.")
    if not 0 < sunlight_efficiency <= 1 or not 0 < eclipse_efficiency <= 1:
        raise ValueError("Energy path efficiencies must lie in (0, 1].")
    power = (sunlight_energy / sunlight_efficiency + eclipse_energy / eclipse_efficiency) / sunlight_duration
    _finite(power)
    return Power(power)


def cell_power(eol_voltage: float, eol_current: float) -> Power:
    _finite(eol_voltage, eol_current)
    if eol_voltage <= 0 or eol_current <= 0:
        raise ValueError("Cell EOL maximum power point voltage and current must be positive.")
    power = eol_voltage * eol_current
    _finite(power)
    return Power(power)


def cell_count(required_power: float, eol_cell_power: float) -> CellCount:
    _finite(required_power, eol_cell_power)
    if required_power < 0 or eol_cell_power <= 0:
        raise ValueError("Require nonnegative panel power and positive EOL cell power.")
    count = required_power / eol_cell_power
    _finite(count)
    return CellCount(count, math.ceil(count))


def mission_cycles(lifetime: float, days_per_year: float, orbits_per_day: float) -> MissionCycles:
    _finite(lifetime, days_per_year, orbits_per_day)
    if lifetime <= 0 or days_per_year <= 0 or orbits_per_day <= 0:
        raise ValueError("Mission lifetime, days per year and orbits per day must be positive.")
    cycles = lifetime * days_per_year * orbits_per_day
    _finite(cycles)
    return MissionCycles(cycles)


def depth_of_discharge(required_cycles: float, cycle_coefficient: float, cycle_exponent: float,
                       fit_dod_min: float, fit_dod_max: float) -> DepthOfDischarge:
    _finite(required_cycles, cycle_coefficient, cycle_exponent, fit_dod_min, fit_dod_max)
    if required_cycles <= 0 or cycle_coefficient <= 0 or cycle_exponent >= 0:
        raise ValueError("Require positive cycle counts and coefficient, and a negative cycle-life exponent.")
    if not 0 < fit_dod_min <= fit_dod_max <= 1:
        raise ValueError("The characterized DoD interval must lie in (0, 1].")
    if required_cycles > cycle_coefficient * fit_dod_min ** cycle_exponent:
        raise ValueError("Required cycles exceed the characterized DoD interval.")
    dod = (required_cycles / cycle_coefficient) ** (1 / cycle_exponent)
    return DepthOfDischarge(max(fit_dod_min, min(fit_dod_max, dod)))


def battery_energy(eclipse_energy: float, depth_of_discharge: float,
                   degradation_margin: float) -> Energy:
    _finite(eclipse_energy, depth_of_discharge, degradation_margin)
    if eclipse_energy < 0 or not 0 < depth_of_discharge <= 1 or degradation_margin < 0:
        raise ValueError("Require nonnegative energy and margin, and DoD in (0, 1].")
    energy = eclipse_energy / depth_of_discharge * (1 + degradation_margin)
    _finite(energy)
    return Energy(energy)


def retained_value(initial: float, retention: float) -> RetainedValue:
    _finite(initial, retention)
    if initial < 0 or not 0 <= retention <= 1:
        raise ValueError("Require a nonnegative rating and retention in [0, 1].")
    return RetainedValue(initial * retention)


def parallel_strings(required_total: float, per_cell: float, series_count: int) -> CellCount:
    """Check-bound for an entered series count. Both quantities use the same unit."""
    _finite(required_total, per_cell)
    if required_total < 0 or per_cell <= 0 or type(series_count) is not int or series_count <= 0:
        raise ValueError("Require a nonnegative total, positive cell rating and positive integer series count.")
    fractional = required_total / per_cell / series_count
    _finite(fractional)
    return CellCount(fractional, math.ceil(fractional))


def panel_area(active_area: float, packing_fraction: float) -> Area:
    _finite(active_area, packing_fraction)
    if active_area < 0 or not 0 < packing_fraction <= 1:
        raise ValueError("Require nonnegative active area and packing in (0, 1].")
    area = active_area / packing_fraction
    _finite(area)
    return Area(area)


def solar_efficiency(bol_efficiency: float, lifetime_retention: float, temperature_factor: float) -> Efficiency:
    _finite(bol_efficiency, lifetime_retention, temperature_factor)
    if not 0 <= bol_efficiency <= 1 or not 0 <= lifetime_retention <= 1 or temperature_factor < 0:
        raise ValueError("Efficiencies and retention lie in [0, 1]. The temperature factor is nonnegative.")
    efficiency = bol_efficiency * lifetime_retention * temperature_factor
    if not 0 <= efficiency <= 1:
        raise ValueError("Corrected solar efficiency must lie in [0, 1].")
    return Efficiency(efficiency)


def array_power_density(irradiance: float, eol_efficiency: float, inherent_retention: float,
                        assembly_efficiency: float, incidence_angle: float) -> PowerDensity:
    """Uniform fixed conditions. Incidence angle is in degrees."""
    _finite(irradiance, eol_efficiency, inherent_retention, assembly_efficiency, incidence_angle)
    if irradiance < 0 or not 0 <= incidence_angle <= 180:
        raise ValueError("Require nonnegative irradiance and incidence in [0, 180] degrees.")
    if not all(0 <= factor <= 1 for factor in (eol_efficiency, inherent_retention, assembly_efficiency)):
        raise ValueError("Solar efficiency and loss factors must lie in [0, 1].")
    projection = math.cos(math.radians(incidence_angle)) if incidence_angle < 90 else 0.0
    density = irradiance * eol_efficiency * inherent_retention * assembly_efficiency * projection
    _finite(density)
    return PowerDensity(density)


def minimum_array_area(required_power: float, power_density: float) -> Area:
    _finite(required_power, power_density)
    if required_power < 0 or power_density <= 0:
        raise ValueError("Require nonnegative power and positive available power density.")
    area = required_power / power_density
    _finite(area)
    return Area(area)


def tumbling_array_area(effective_area: float, packing_fraction: float) -> Area:
    """Nogrady's six-face, half-illuminated, 50 degree incidence approximation."""
    return panel_area(2 * effective_area / math.cos(math.radians(50)), packing_fraction)
