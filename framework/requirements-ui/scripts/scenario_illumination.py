"""Preliminary circular Earth orbit illumination for one array section.

Standard library only. The registered runner copies this file in isolation.
See analyses/README.md for equations, input conventions and model limits.
"""
import json
import math
import sys

AU_KM = 149597870.7  # IAU 2012 astronomical unit.
SUN_RADIUS_KM = 695700.0  # IAU 2015 nominal solar radius.
MAX_STEPS = 200000


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(v):
    return math.sqrt(dot(v, v))


def clamp(value, lower=-1.0, upper=1.0):
    return min(upper, max(lower, value))


def sun_position(jd):
    """Low precision geocentric Sun, mean equator/equinox of date (km).

    Approximate solar longitude, anomaly and obliquity about J2000.
    This model is intended for preliminary geometry over 1900 through 2100.
    """
    days = jd - 2451545.0
    mean_longitude = math.radians((280.460 + 0.9856474 * days) % 360)
    anomaly = math.radians((357.528 + 0.9856003 * days) % 360)
    longitude = mean_longitude + math.radians(1.915) * math.sin(anomaly) + math.radians(0.020) * math.sin(2 * anomaly)
    obliquity = math.radians(23.439 - 0.0000004 * days)
    distance = AU_KM * (1.00014 - 0.01671 * math.cos(anomaly) - 0.00014 * math.cos(2 * anomaly))
    return (distance * math.cos(longitude), distance * math.cos(obliquity) * math.sin(longitude),
            distance * math.sin(obliquity) * math.sin(longitude))


def solar_visibility(position, sun, earth_radius):
    """Visible fraction of the solar disk, including conical penumbra.

    Disk overlap uses apparent angular radii and a planar small-angle model.
    Sun and Earth directions are measured at the spacecraft.
    """
    radius = norm(position)
    to_sun = tuple(s - r for s, r in zip(sun, position))
    distance = norm(to_sun)
    direction = tuple(value / distance for value in to_sun)
    separation = math.acos(clamp(-dot(position, direction) / radius))
    earth_angle = math.asin(earth_radius / radius)
    sun_angle = math.asin(SUN_RADIUS_KM / distance)
    if separation >= earth_angle + sun_angle:
        return 1.0, direction, distance
    if earth_angle >= separation + sun_angle:
        return 0.0, direction, distance
    if sun_angle >= separation + earth_angle:
        return 1.0 - (earth_angle / sun_angle) ** 2, direction, distance
    # The remaining case is a partial overlap of the two apparent disks.
    d, a, b = separation, sun_angle, earth_angle
    overlap = (a * a * math.acos(clamp((d * d + a * a - b * b) / (2 * d * a)))
               + b * b * math.acos(clamp((d * d + b * b - a * a) / (2 * d * b)))
               - 0.5 * math.sqrt(max(0.0, (-d + a + b) * (d + a - b) * (d - a + b) * (d + a + b))))
    return clamp(1.0 - overlap / (math.pi * a * a), 0.0, 1.0), direction, distance


def simulate(p):
    for name, value in p.items():
        if name == "sun_tracking":
            if type(value) is not bool:
                raise ValueError("sun_tracking must be Boolean.")
        elif type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    radius = p["earth_radius_km"] + p["altitude_km"]
    if p["earth_radius_km"] <= 0 or p["altitude_km"] <= 0 or p["mu_km3_s2"] <= 0:
        raise ValueError("Earth radius, altitude and gravitational parameter must be positive.")
    if not 0 <= p["inclination_deg"] <= 180 or not 0 <= p["earth_j2"] < 0.01:
        raise ValueError("Use inclination in [0,180] degrees and earth_j2 in [0,0.01).")
    if p["duration_s"] <= 0 or p["step_s"] <= 0 or p["solar_constant_W_m2"] <= 0:
        raise ValueError("Duration, step and reference solar irradiance must be positive.")
    if not 2415020.5 <= p["epoch_jd"] <= p["epoch_jd"] + p["duration_s"] / 86400 <= 2488069.5:
        raise ValueError("The complete interval must lie within 1900 through 2100 (Julian dates).")
    rate = math.sqrt(p["mu_km3_s2"] / radius ** 3)
    period = 2 * math.pi / rate
    steps = math.ceil(p["duration_s"] / p["step_s"])
    if steps > MAX_STEPS or p["step_s"] > period / 180:
        raise ValueError("Use at most 200000 steps and a step no larger than orbit_period_s / 180.")
    panel = (p["panel_normal_radial"], p["panel_normal_along"], p["panel_normal_cross"])
    length = norm(panel)
    if not p["sun_tracking"] and length == 0:
        raise ValueError("A fixed panel needs a nonzero local orbital normal vector.")
    panel = tuple(value / length for value in panel) if length else (0.0, 0.0, 0.0)
    inclination = math.radians(p["inclination_deg"])
    node_rate = -1.5 * p["earth_j2"] * rate * (p["earth_radius_km"] / radius) ** 2 * math.cos(inclination)
    sunlight = eclipse = penumbra = incident = current_eclipse = longest_eclipse = 0.0
    min_beta, max_beta, min_flux, max_flux = 90.0, -90.0, math.inf, 0.0
    for index in range(steps):
        start = index * p["step_s"]
        dt = min(p["step_s"], p["duration_s"] - start)
        time = start + dt / 2
        node = math.radians(p["raan_deg"] % 360) + node_rate * time
        argument = math.radians(p["argument_latitude_deg"] % 360) + rate * time
        cn, sn, ci, si = math.cos(node), math.sin(node), math.cos(inclination), math.sin(inclination)
        cu, su = math.cos(argument), math.sin(argument)
        radial = (cn * cu - sn * su * ci, sn * cu + cn * su * ci, su * si)
        along = (-cn * su - sn * cu * ci, -sn * su + cn * cu * ci, cu * si)
        cross = (sn * si, -cn * si, ci)
        position = tuple(radius * value for value in radial)
        sun = sun_position(p["epoch_jd"] + time / 86400)
        visible, direction, distance = solar_visibility(position, sun, p["earth_radius_km"])
        beta = math.degrees(math.asin(clamp(dot(cross, sun) / norm(sun))))
        min_beta, max_beta = min(min_beta, beta), max(max_beta, beta)
        if visible == 0:
            eclipse += dt
            current_eclipse += dt
            longest_eclipse = max(longest_eclipse, current_eclipse)
        else:
            sunlight += dt
            current_eclipse = 0.0
            if visible < 1:
                penumbra += dt
        normal = tuple(panel[0] * r + panel[1] * a + panel[2] * c for r, a, c in zip(radial, along, cross))
        incidence = 1.0 if p["sun_tracking"] else max(0.0, dot(normal, direction))
        flux = p["solar_constant_W_m2"] * (AU_KM / distance) ** 2 * visible * incidence
        incident += flux * dt
        min_flux, max_flux = min(min_flux, flux), max(max_flux, flux)
    print(f"Circular orbit, {steps} midpoint samples, J2 node drift only. "
          "Eclipse lengths are clipped at interval boundaries. Repeat with a smaller step to check convergence. "
          "No thermal, battery, albedo or hardware compliance assessment.", file=sys.stderr)
    return {
        "orbit_period_s": period,
        "sunlight_s": sunlight,
        "eclipse_s": eclipse,
        "penumbra_s": penumbra,
        "longest_eclipse_s": longest_eclipse,
        "sunlit_fraction": sunlight / p["duration_s"],
        "min_beta_deg": min_beta,
        "max_beta_deg": max_beta,
        "min_irradiance_W_m2": min_flux,
        "max_irradiance_W_m2": max_flux,
        "mean_irradiance_W_m2": incident / p["duration_s"],
        "incident_energy_J_m2": incident,
        "sample_count": steps,
    }


if __name__ == "__main__":
    try:
        json.dump(simulate(json.load(sys.stdin)["inputs"]), sys.stdout, allow_nan=False)
    except (ValueError, KeyError, ArithmeticError) as error:
        print(f"Illumination inputs: {error}", file=sys.stderr)
        sys.exit(1)
