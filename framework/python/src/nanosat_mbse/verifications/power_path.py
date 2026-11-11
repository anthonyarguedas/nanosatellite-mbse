"""One declared constant-current rail: see analyses/PATHS.md for scope and codes."""

import math
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)


NAMES = (
    "source_voltage_V rail_voltage_V efficiency idle_power_W steady_current_A "
    "pulse_current_A pulse_replaces_steady pulse_duration_s path_resistance_ohm "
    "diode_drop_V load_min_V load_max_V input_min_V input_max_V startup_min_V "
    "dropout_V topology_code duty_min duty_max battery_cont_A battery_pulse_A "
    "converter_in_cont_A converter_in_pulse_A converter_out_cont_A "
    "converter_out_pulse_A switch_cont_A switch_pulse_A pulse_rating_duration_s "
    "startup_time_s startup_limit_s connection_cont_A connection_pulse_A"
).split()


def calculate(p):
    if set(p) != set(NAMES):
        raise ValueError("inputs must contain exactly the declared names")
    for name in NAMES:
        value = p[name]
        if name == "pulse_replaces_steady":
            if type(value) is not bool:
                raise ValueError(name + " must be boolean")
        elif name == "topology_code":
            if type(value) is not int or value not in (0, 1, 2):
                raise ValueError(
                    "topology_code must be integer 0=buck, 1=boost, 2=buckboost"
                )
        elif type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(name + " must be finite numeric")
    for name in NAMES:
        if name not in ("pulse_replaces_steady", "topology_code") and p[name] < 0:
            raise ValueError(name + " must be nonnegative")
    for name in (
        "source_voltage_V",
        "rail_voltage_V",
        "pulse_duration_s",
        "pulse_rating_duration_s",
    ):
        if p[name] <= 0:
            raise ValueError(name + " must be positive")
    if not 0 < p["efficiency"] <= 1:
        raise ValueError("efficiency must be in (0,1]")
    for low, high in (("input_min_V", "input_max_V"), ("load_min_V", "load_max_V")):
        if p[low] > p[high]:
            raise ValueError(low + " must not exceed " + high)
    if not 0 <= p["duty_min"] <= p["duty_max"] <= 1:
        raise ValueError("duty bounds must satisfy 0 <= min <= max <= 1")

    vin, rail, eta = p["source_voltage_V"], p["rail_voltage_V"], p["efficiency"]
    steady = p["steady_current_A"]
    pulse = p["pulse_current_A"] + (0 if p["pulse_replaces_steady"] else steady)
    result = {}
    for label, current in (("steady", steady), ("pulse", pulse)):
        voltage = rail - p["diode_drop_V"] - current * p["path_resistance_ohm"]
        rail_power = rail * current
        loss = rail_power * (1 / eta - 1) + p["idle_power_W"]
        pin = rail_power / eta + p["idle_power_W"]
        result.update(
            {
                label + "_input_W": pin,
                label + "_source_A": pin / vin,
                label + "_rail_W": rail_power,
                label + "_load_V": voltage,
                label + "_terminal_W": voltage * current,
                label + "_converter_loss_W": loss,
                label + "_path_loss_W": current
                * (current * p["path_resistance_ohm"] + p["diode_drop_V"]),
                label + "_voltage_ok": p["load_min_V"] <= voltage <= p["load_max_V"],
            }
        )
    # The supplied dropout is a lumped input-side headroom subtraction in this
    # averaged conversion-envelope model, NOT a detailed switching simulation.
    effective = vin - p["dropout_V"]
    code = p["topology_code"]
    duty = None
    if effective > 0:
        if code == 0:
            duty = rail / effective
        elif code == 1:
            duty = 1 - effective / rail
        elif rail >= effective:
            duty = 1 / (1 + effective / rail)
        else:
            ratio = rail / effective
            duty = ratio / (1 + ratio)
    result["duty_required"] = duty
    result["dropout_margin_V"] = effective - rail if code == 0 else effective
    result["input_ok"] = p["input_min_V"] <= vin <= p["input_max_V"]
    result["startup_ok"] = vin >= p["startup_min_V"]
    result["envelope_ok"] = effective > 0 and p["duty_min"] <= duty <= p["duty_max"]
    result["startup_time_ok"] = p["startup_time_s"] <= p["startup_limit_s"]
    result["battery_current_ok"] = (
        result["steady_source_A"] <= p["battery_cont_A"]
        and result["pulse_source_A"] <= p["battery_pulse_A"]
    )
    result["converter_current_ok"] = (
        result["steady_source_A"] <= p["converter_in_cont_A"]
        and result["pulse_source_A"] <= p["converter_in_pulse_A"]
        and steady <= p["converter_out_cont_A"]
        and pulse <= p["converter_out_pulse_A"]
    )
    result["switch_current_ok"] = (
        steady <= p["switch_cont_A"] and pulse <= p["switch_pulse_A"]
    )
    result["connection_current_ok"] = (
        steady <= p["connection_cont_A"] and pulse <= p["connection_pulse_A"]
    )
    result["pulse_duration_ok"] = p["pulse_duration_s"] <= p["pulse_rating_duration_s"]
    result["path_ok"] = all(
        value for name, value in result.items() if name.endswith("_ok")
    )
    return result


class PowerPath(VerificationScript):
    definition_spec = ScriptDefinition(
        id="eps_power_path",
        name="EPS declared rail and power path",
        description="One constant-current steady/pulse rail with upstream efficiency and path drops. Topology 0=buck, 1=boost, 2=buckboost magnitude; effective input is source minus supplied dropout. All ratings and startup time are supplied case-specific bounds. See analyses/PATHS.md; not a switching transient or arbitrary converter envelope.",
        inputs=(
            ScriptPort("source_voltage_V", float, "V"),
            ScriptPort("rail_voltage_V", float, "V"),
            ScriptPort("efficiency", float, None),
            ScriptPort("idle_power_W", float, "W"),
            ScriptPort("steady_current_A", float, "A"),
            ScriptPort("pulse_current_A", float, "A"),
            ScriptPort("pulse_replaces_steady", bool, None),
            ScriptPort("pulse_duration_s", float, "s"),
            ScriptPort("path_resistance_ohm", float, "ohm"),
            ScriptPort("diode_drop_V", float, "V"),
            ScriptPort("load_min_V", float, "V"),
            ScriptPort("load_max_V", float, "V"),
            ScriptPort("input_min_V", float, "V"),
            ScriptPort("input_max_V", float, "V"),
            ScriptPort("startup_min_V", float, "V"),
            ScriptPort("dropout_V", float, "V"),
            ScriptPort("topology_code", int, None),
            ScriptPort("duty_min", float, None),
            ScriptPort("duty_max", float, None),
            ScriptPort("battery_cont_A", float, "A"),
            ScriptPort("battery_pulse_A", float, "A"),
            ScriptPort("converter_in_cont_A", float, "A"),
            ScriptPort("converter_in_pulse_A", float, "A"),
            ScriptPort("converter_out_cont_A", float, "A"),
            ScriptPort("converter_out_pulse_A", float, "A"),
            ScriptPort("switch_cont_A", float, "A"),
            ScriptPort("switch_pulse_A", float, "A"),
            ScriptPort("pulse_rating_duration_s", float, "s"),
            ScriptPort("startup_time_s", float, "s"),
            ScriptPort("startup_limit_s", float, "s"),
            ScriptPort("connection_cont_A", float, "A"),
            ScriptPort("connection_pulse_A", float, "A"),
        ),
        outputs=(
            ScriptPort("steady_input_W", float, "W"),
            ScriptPort("pulse_input_W", float, "W"),
            ScriptPort("steady_source_A", float, "A"),
            ScriptPort("pulse_source_A", float, "A"),
            ScriptPort("steady_rail_W", float, "W"),
            ScriptPort("pulse_rail_W", float, "W"),
            ScriptPort("steady_load_V", float, "V"),
            ScriptPort("pulse_load_V", float, "V"),
            ScriptPort("steady_terminal_W", float, "W"),
            ScriptPort("pulse_terminal_W", float, "W"),
            ScriptPort("steady_converter_loss_W", float, "W"),
            ScriptPort("pulse_converter_loss_W", float, "W"),
            ScriptPort("steady_path_loss_W", float, "W"),
            ScriptPort("pulse_path_loss_W", float, "W"),
            ScriptPort("duty_required", float, None),
            ScriptPort("dropout_margin_V", float, "V"),
            ScriptPort("input_ok", bool, None),
            ScriptPort("startup_ok", bool, None),
            ScriptPort("envelope_ok", bool, None),
            ScriptPort("startup_time_ok", bool, None),
            ScriptPort("steady_voltage_ok", bool, None),
            ScriptPort("pulse_voltage_ok", bool, None),
            ScriptPort("battery_current_ok", bool, None),
            ScriptPort("converter_current_ok", bool, None),
            ScriptPort("switch_current_ok", bool, None),
            ScriptPort("connection_current_ok", bool, None),
            ScriptPort("pulse_duration_ok", bool, None),
            ScriptPort("path_ok", bool, None),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return calculate(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(PowerPath))
