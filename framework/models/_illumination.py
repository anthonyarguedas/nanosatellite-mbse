"""Circular orbit illumination expressions and reviewed former defaults.

Beta is constant during an assessed orbit. Solar rays are parallel and Earth
casts a cylindrical shadow. These expressions do not model penumbra, an
elliptical orbit, attitude, or the evolution of beta with epoch.
"""

ECLIPSE_PERIOD = (
    "0 if abs(beta_deg) >= 90 - horizon_angle_rad * 180 / math.pi "
    "else orbit_period_s / math.pi * math.acos("
    "min(1, max(0, math.sin(horizon_angle_rad) / "
    "math.cos(beta_deg * math.pi / 180))))"
)
SUNLIGHT_PERIOD = "orbit_period_s - eclipse_s"
ILLUMINATION_CHECK = (
    "altitude_km > 0 and earthRadius_km > 0 and orbit_period_s > 0 "
    "and -90 <= beta_deg <= 90 "
    "and horizon_angle_rad == math.acos(earthRadius_km / (earthRadius_km + altitude_km)) "
    "and sunlight_s >= 0 and eclipse_s >= 0 "
    "and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s "
    f"and abs(eclipse_s - ({ECLIPSE_PERIOD})) <= 1e-9 * orbit_period_s"
)
CLOSURE_CHECK = (
    "orbit_period_s > 0 and sunlight_s >= 0 and eclipse_s >= 0 "
    "and abs(sunlight_s + eclipse_s - orbit_period_s) <= 1e-9 * orbit_period_s"
)
LOAD_ENERGY_EXPRESSIONS = {
    f"{period}_energy_J": (
        f"0 if {period}_s == 0 else {period}_power_W * {period}_duty * {period}_s"
    )
    for period in ("sunlight", "eclipse")
}
LOAD_ENERGY_CHECK = (
    "sunlight_s >= 0 and eclipse_s >= 0 and sunlight_s + eclipse_s > 0 and "
    + " and ".join(
        f"(({period}_s == 0 and {period}_energy_J == 0) or "
        f"({period}_s > 0 and {period}_power_W >= 0 "
        f"and 0 <= {period}_duty <= 1 "
        f"and {period}_energy_J == {period}_power_W * {period}_duty * {period}_s))"
        for period in ("sunlight", "eclipse")
    )
)

# Exact reviewed bindings let reconciliation update old library defaults while
# retaining authored expressions, conditions, cleared cells and deleted rows.
LEGACY_DEFAULTS = {
    "FrameworkRequirements::IlluminationPeriods": {
        "parameters": {
            "sunlight_s": "((0.5 + (horizon_angle_rad / math.pi)) * orbit_period_s)",
            "eclipse_s": "((0.5 - (horizon_angle_rad / math.pi)) * orbit_period_s)",
        },
        "conditions": (
            "(((((((((altitude_km > 0) and (earthRadius_km > 0)) and (orbit_period_s > 0)) and (sunlight_s > 0)) and (eclipse_s > 0)) and (horizon_angle_rad == math.acos((earthRadius_km / (earthRadius_km + altitude_km))))) and (sunlight_s == ((0.5 + (horizon_angle_rad / math.pi)) * orbit_period_s))) and (eclipse_s == ((0.5 - (horizon_angle_rad / math.pi)) * orbit_period_s))) and (abs(((sunlight_s + eclipse_s) - orbit_period_s)) <= (1e-9 * orbit_period_s)))",
            "(((((((((altitude_km > 0) and (earthRadius_km > 0)) and (orbit_period_s > 0)) and (horizon_angle_rad == math.acos((earthRadius_km / (earthRadius_km + altitude_km))))) and (sunlight_s == ((0.5 + (horizon_angle_rad / math.pi)) * orbit_period_s))) and (eclipse_s == ((0.5 - (horizon_angle_rad / math.pi)) * orbit_period_s))) and (sunlight_s > 0)) and (eclipse_s > 0)) and (abs(((sunlight_s + eclipse_s) - orbit_period_s)) <= (1e-9 * orbit_period_s)))",
        ),
        "text": "The preliminary circular orbit at altitude $$altitude_km$$ shall provide $$sunlight_s$$ of sunlight and $$eclipse_s$$ of eclipse per $$orbit_period_s$$ orbit, using Earth radius $$earthRadius_km$$ and horizon angle $$horizon_angle_rad$$.",
    },
    "FrameworkRequirements::LoadEnergy": {
        "parameters": {
            "sunlight_energy_J": "((sunlight_power_W * sunlight_duty) * sunlight_s)",
            "eclipse_energy_J": "((eclipse_power_W * eclipse_duty) * eclipse_s)",
        },
        "conditions": (
            "((((((((((sunlight_power_W >= 0) and (eclipse_power_W >= 0)) and (sunlight_duty >= 0)) and (sunlight_duty <= 1)) and (eclipse_duty >= 0)) and (eclipse_duty <= 1)) and (sunlight_s > 0)) and (eclipse_s > 0)) and (sunlight_energy_J == ((sunlight_power_W * sunlight_duty) * sunlight_s))) and (eclipse_energy_J == ((eclipse_power_W * eclipse_duty) * eclipse_s)))",
            "((((((((((sunlight_power_W >= 0) and (eclipse_power_W >= 0)) and (sunlight_s > 0)) and (eclipse_s > 0)) and (sunlight_duty >= 0)) and (sunlight_duty <= 1)) and (eclipse_duty >= 0)) and (eclipse_duty <= 1)) and (sunlight_energy_J == ((sunlight_power_W * sunlight_duty) * sunlight_s))) and (eclipse_energy_J == ((eclipse_power_W * eclipse_duty) * eclipse_s)))",
        ),
    },
    "FrameworkRequirements::OrbitPeriodClosure": {
        "parameters": {},
        "conditions": (
            "((((orbit_period_s > 0) and (sunlight_s > 0)) and (eclipse_s > 0)) and (abs(((sunlight_s + eclipse_s) - orbit_period_s)) <= (1e-9 * orbit_period_s)))",
        ),
        "text": "The positive sunlight and eclipse periods shall sum to $$orbit_period_s$$ within numerical tolerance.",
    },
}
