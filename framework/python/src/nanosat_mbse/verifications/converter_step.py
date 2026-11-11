"""Declared first-order closed-loop voltage response for one command/load step.

The target voltage includes the supplied steady droop. This transfer model has
no switching, current limiting, overshoot, reactive energy or control stability
model. Use eps_power_path for topology, startup source and rating checks.
"""

import math
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)


def analyze(p):
    for name, value in p.items():
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(name + " must be finite.")
    for name in (
        "duration_s",
        "time_constant_s",
        "input_voltage_V",
        "regulation_tolerance_V",
    ):
        if p[name] <= 0:
            raise ValueError(name + " must be positive.")
    if min(p["initial_voltage_V"], p["target_voltage_V"], p["load_current_A"]) < 0:
        raise ValueError("Voltage and load current must be nonnegative.")
    if not 0 < p["conversion_efficiency"] <= 1:
        raise ValueError("Conversion efficiency must lie in (0, 1].")
    if not 0 < p["required_min_V"] < p["required_max_V"]:
        raise ValueError("Require a positive ordered service voltage interval.")
    duration, tau = p["duration_s"], p["time_constant_s"]
    initial, target = p["initial_voltage_V"], p["target_voltage_V"]
    difference = initial - target
    end = initial + (target - initial) * -math.expm1(-duration / tau)
    low, high = min(initial, end), max(initial, end)
    error = abs(difference)
    settle = (
        0.0
        if error <= p["regulation_tolerance_V"]
        else tau * math.log(error / p["regulation_tolerance_V"])
    )
    settled = settle <= duration
    startup = None
    if p["required_min_V"] <= initial <= p["required_max_V"]:
        startup = 0.0
    elif difference != 0:
        boundary = (
            p["required_min_V"]
            if initial < p["required_min_V"]
            else p["required_max_V"]
        )
        ratio = (boundary - target) / difference
        if 0 < ratio <= 1:
            crossing = -tau * math.log(ratio)
            if crossing <= duration:
                startup = crossing
    # A startup claim requires the service band to hold through the interval end.
    service_at_end = p["required_min_V"] <= end <= p["required_max_V"]
    if not service_at_end:
        startup = None
    integral = target * duration + difference * tau * -math.expm1(-duration / tau)
    output_energy = p["load_current_A"] * integral
    input_energy = output_energy / p["conversion_efficiency"]
    return dict(
        voltage_end_V=end,
        voltage_min_V=low,
        voltage_max_V=high,
        output_energy_J=output_energy,
        input_energy_J=input_energy,
        loss_energy_J=input_energy - output_energy,
        peak_input_current_A=high
        * p["load_current_A"]
        / p["conversion_efficiency"]
        / p["input_voltage_V"],
        settling_time_s=settle if settled else None,
        settled=settled,
        startup_time_s=startup,
        startup_reached=startup is not None,
        service_at_end=service_at_end,
        service_duration_s=duration - startup if startup is not None else 0.0,
        voltage_limits_ok=low >= p["required_min_V"] and high <= p["required_max_V"],
    )


class ConverterStep(VerificationScript):
    definition_spec = ScriptDefinition(
        id="eps_converter_step",
        name="EPS first-order converter response",
        description="Exact declared first-order closed-loop voltage step with supplied target and time constant. Reports voltage bounds, startup and settling time, constant-current load energy and fixed-efficiency losses. No switching, current limiting, overshoot, reactive energy or stability model. Use the power-path assessment for converter source, topology and rating compatibility.",
        inputs=(
            ScriptPort("duration_s", float, "s"),
            ScriptPort("initial_voltage_V", float, "V"),
            ScriptPort("target_voltage_V", float, "V"),
            ScriptPort("time_constant_s", float, "s"),
            ScriptPort("load_current_A", float, "A"),
            ScriptPort("conversion_efficiency", float, None),
            ScriptPort("input_voltage_V", float, "V"),
            ScriptPort("required_min_V", float, "V"),
            ScriptPort("required_max_V", float, "V"),
            ScriptPort("regulation_tolerance_V", float, "V"),
        ),
        outputs=(
            ScriptPort("voltage_end_V", float, "V"),
            ScriptPort("voltage_min_V", float, "V"),
            ScriptPort("voltage_max_V", float, "V"),
            ScriptPort("output_energy_J", float, "J"),
            ScriptPort("input_energy_J", float, "J"),
            ScriptPort("loss_energy_J", float, "J"),
            ScriptPort("peak_input_current_A", float, "A"),
            ScriptPort("settling_time_s", float, "s"),
            ScriptPort("settled", bool, None),
            ScriptPort("startup_time_s", float, "s"),
            ScriptPort("startup_reached", bool, None),
            ScriptPort("service_at_end", bool, None),
            ScriptPort("service_duration_s", float, "s"),
            ScriptPort("voltage_limits_ok", bool, None),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return analyze(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(ConverterStep))
