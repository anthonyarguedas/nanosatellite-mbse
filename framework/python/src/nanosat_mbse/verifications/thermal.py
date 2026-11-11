"""Exact constant-power one-node thermal RC interval; see analyses/PATHS.md."""

import math
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)


BOOLS = {"temp_limits_known", "charge_active", "charge_limits_known"}
NUMBERS = (
    "initial_temp_K ambient_temp_K dissipation_W heater_W heat_capacity_J_K "
    "conductance_W_K duration_s temp_min_K temp_max_K charge_min_K charge_max_K"
).split()


def calculate(p):
    if set(p) != set(NUMBERS) | BOOLS:
        raise ValueError("inputs must contain exactly the declared names")
    for name in BOOLS:
        if type(p[name]) is not bool:
            raise ValueError(name + " must be boolean")
    for name in NUMBERS:
        if (
            type(p[name]) not in (int, float)
            or not math.isfinite(p[name])
            or p[name] < 0
        ):
            raise ValueError(name + " must be finite nonnegative numeric")
    if p["heat_capacity_J_K"] <= 0:
        raise ValueError("heat_capacity_J_K must be positive")
    if p["temp_min_K"] > p["temp_max_K"] or p["charge_min_K"] > p["charge_max_K"]:
        raise ValueError("temperature limit bounds are invalid")
    initial, ambient, t = p["initial_temp_K"], p["ambient_temp_K"], p["duration_s"]
    c, g = p["heat_capacity_J_K"], p["conductance_W_K"]
    power = p["dissipation_W"] + p["heater_W"]
    if g == 0:
        delta = power * (t / c)
        mean_delta = delta / 2
        tau = None
    else:
        tau = c / g
        x = g * (t / c)
        d = -math.expm1(-x)
        if x == 0:
            delta = power * (t / c)
            mean_delta = delta / 2
        elif x < 0.1:
            # f=(x-1+exp(-x))/x, q=f/x: stable small-interval mean.
            q = math.fsum(
                ((-1) ** n) * x ** (n - 2) / math.factorial(n) for n in range(2, 24)
            )
            delta = (ambient - initial) * d + power * (t / c) * (d / x)
            mean_delta = (ambient - initial) * (x * q) + power * (t / c) * q
        else:
            equilibrium_delta = ambient - initial + power / g
            delta = equilibrium_delta * d
            mean_delta = equilibrium_delta * (1 - d / x)
    end = initial + delta
    mean = initial + mean_delta
    minimum, maximum = min(initial, end), max(initial, end)
    generated = power * t
    stored = c * delta
    ambient_out = g * t * (mean - ambient)
    temp_known = p["temp_limits_known"]
    charge_known = p["charge_active"] and p["charge_limits_known"]
    temp_ok = (
        p["temp_min_K"] <= minimum and maximum <= p["temp_max_K"]
        if temp_known
        else None
    )
    charge_ok = (
        p["charge_min_K"] <= minimum and maximum <= p["charge_max_K"]
        if charge_known
        else None
        if p["charge_active"]
        else True
    )
    findings = (temp_ok, charge_ok)
    thermal_ok = False if False in findings else None if None in findings else True
    return {
        "end_temp_K": end,
        "min_temp_K": minimum,
        "max_temp_K": maximum,
        "mean_temp_K": mean,
        "thermal_time_constant_s": tau,
        "dissipation_energy_J": p["dissipation_W"] * t,
        "heater_energy_J": p["heater_W"] * t,
        "total_generated_J": generated,
        "stored_heat_change_J": stored,
        "ambient_heat_out_J": ambient_out,
        "energy_residual_J": generated - stored - ambient_out,
        "temp_low_margin_K": minimum - p["temp_min_K"] if temp_known else None,
        "temp_high_margin_K": p["temp_max_K"] - maximum if temp_known else None,
        "charge_low_margin_K": minimum - p["charge_min_K"] if charge_known else None,
        "charge_high_margin_K": p["charge_max_K"] - maximum if charge_known else None,
        "temp_ok": temp_ok,
        "charge_ok": charge_ok,
        "thermal_ok": thermal_ok,
    }


class Thermal(VerificationScript):
    definition_spec = ScriptDefinition(
        id="eps_thermal",
        name="EPS one-node thermal interval",
        description="Exact constant dissipation/heater, constant ambient one-node C/G thermal interval, including adiabatic G=0. Endpoint extrema, energy balance and optional state/charging temperature limits. A declared node only: no inferred junction or spatial temperature. Heater power must also be supplied as a chronological electrical load. See analyses/PATHS.md.",
        inputs=(
            ScriptPort("initial_temp_K", float, "K"),
            ScriptPort("ambient_temp_K", float, "K"),
            ScriptPort("dissipation_W", float, "W"),
            ScriptPort("heater_W", float, "W"),
            ScriptPort("heat_capacity_J_K", float, "J/K"),
            ScriptPort("conductance_W_K", float, "W/K"),
            ScriptPort("duration_s", float, "s"),
            ScriptPort("temp_limits_known", bool, None),
            ScriptPort("temp_min_K", float, "K"),
            ScriptPort("temp_max_K", float, "K"),
            ScriptPort("charge_active", bool, None),
            ScriptPort("charge_limits_known", bool, None),
            ScriptPort("charge_min_K", float, "K"),
            ScriptPort("charge_max_K", float, "K"),
        ),
        outputs=(
            ScriptPort("end_temp_K", float, "K"),
            ScriptPort("min_temp_K", float, "K"),
            ScriptPort("max_temp_K", float, "K"),
            ScriptPort("mean_temp_K", float, "K"),
            ScriptPort("thermal_time_constant_s", float, "s"),
            ScriptPort("dissipation_energy_J", float, "J"),
            ScriptPort("heater_energy_J", float, "J"),
            ScriptPort("total_generated_J", float, "J"),
            ScriptPort("stored_heat_change_J", float, "J"),
            ScriptPort("ambient_heat_out_J", float, "J"),
            ScriptPort("energy_residual_J", float, "J"),
            ScriptPort("temp_low_margin_K", float, "K"),
            ScriptPort("temp_high_margin_K", float, "K"),
            ScriptPort("charge_low_margin_K", float, "K"),
            ScriptPort("charge_high_margin_K", float, "K"),
            ScriptPort("temp_ok", bool, None),
            ScriptPort("charge_ok", bool, None),
            ScriptPort("thermal_ok", bool, None),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return calculate(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(Thermal))
