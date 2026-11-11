"""Ideal sampled perturb and observe tracker with a calibrated empirical I-V curve.

Standard library only. See analyses/README.md for model scope and assumptions.
"""

import math
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)

MAX_STEPS = 200000


def curve(p, irradiance, temperature):
    """Return (Voc, Isc, Vmp, Imp) for a uniformly illuminated section."""
    if irradiance == 0:
        return 0.0, 0.0, 0.0, 0.0
    ratio = irradiance / p["reference_irradiance_W_m2"]
    delta = temperature - p["reference_temperature_C"]
    current_factor = ratio * (1 + p["current_temp_coeff_per_C"] * delta)
    voltage_shift = p["voltage_temp_coeff_V_C"] * delta + p[
        "voltage_log_coefficient_V"
    ] * math.log(ratio)
    voc = p["voc_ref_V"] + voltage_shift
    vmp = p["vmp_ref_V"] + voltage_shift
    isc, imp = p["isc_ref_A"] * current_factor, p["imp_ref_A"] * current_factor
    if not (0 < vmp < voc and 0 < imp < isc):
        raise ValueError(
            "The adjusted I-V points must satisfy 0 < Vmp < Voc and 0 < Imp < Isc in both phases."
        )
    return voc, isc, vmp, imp


def current_at(voltage, points):
    """Monotone C1 curve through Isc, MPP and Voc, with dP/dV=0 at MPP.

    This empirical interpolation is a declared model, not a fitted diode model.
    """
    voc, isc, vmp, imp = points
    if voc == 0 or voltage >= voc:
        return 0.0
    if voltage <= vmp:
        return isc - (isc - imp) * (voltage / vmp) ** (imp / (isc - imp))
    return imp * ((voc - voltage) / (voc - vmp)) ** ((voc - vmp) / vmp)


def sample_index(value, period, name):
    count = round(value / period)
    if not math.isclose(value, count * period, rel_tol=1e-10, abs_tol=1e-10 * period):
        raise ValueError(f"{name} must be an integer multiple of sample_period_s.")
    return count


def simulate(p):
    for name, value in p.items():
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    if not (
        0 < p["vmp_ref_V"] < p["voc_ref_V"] and 0 < p["imp_ref_A"] < p["isc_ref_A"]
    ):
        raise ValueError(
            "Reference points must satisfy 0 < Vmp < Voc and 0 < Imp < Isc."
        )
    if p["reference_irradiance_W_m2"] <= 0 or p["voltage_log_coefficient_V"] < 0:
        raise ValueError(
            "Reference irradiance must be positive and voltage_log_coefficient_V nonnegative."
        )
    if min(p["irradiance_start_W_m2"], p["irradiance_end_W_m2"]) < 0:
        raise ValueError("Irradiances must be nonnegative.")
    if (
        min(
            p["reference_temperature_C"],
            p["temperature_start_C"],
            p["temperature_end_C"],
        )
        <= -273.15
    ):
        raise ValueError("Temperatures must be above absolute zero.")
    if not (
        0 < p["tracking_min_V"] < p["tracking_max_V"]
        and p["tracking_min_V"] <= p["initial_voltage_V"] <= p["tracking_max_V"]
    ):
        raise ValueError(
            "Use 0 < tracking_min_V < tracking_max_V and an initial voltage inside that interval."
        )
    if not (
        p["duration_s"] > 0
        and p["sample_period_s"] > 0
        and 0 <= p["change_time_s"] <= p["duration_s"]
    ):
        raise ValueError(
            "Duration and sampling period must be positive, with change_time_s inside the interval."
        )
    if not 0 < p["voltage_step_V"] <= p["tracking_max_V"] - p["tracking_min_V"]:
        raise ValueError(
            "The voltage perturbation must be positive and no larger than the tracking span."
        )
    if not 0 < p["conversion_efficiency"] <= 1:
        raise ValueError("Conversion efficiency must lie in (0,1].")
    if not (0 < p["settling_relative_band"] < 1 and p["settling_hold_s"] > 0):
        raise ValueError(
            "Use a settling relative band in (0,1) and a positive hold duration."
        )
    period = p["sample_period_s"]
    steps = sample_index(p["duration_s"], period, "duration_s")
    change = sample_index(p["change_time_s"], period, "change_time_s")
    if not 1 <= steps <= MAX_STEPS:
        raise ValueError("Use 1 through 200000 MPPT samples.")
    phases = [
        curve(p, p["irradiance_start_W_m2"], p["temperature_start_C"]),
        curve(p, p["irradiance_end_W_m2"], p["temperature_end_C"]),
    ]
    active = [
        (points, count)
        for points, count in zip(phases, (change, steps - change))
        if count
    ]
    lit = [points for points, count in active if points[0] > 0]
    available_energy = attainable_energy = tracked_energy = 0.0
    min_voltage, max_voltage, max_current, max_error = math.inf, 0.0, 0.0, 0.0
    direction, reversals, command, previous_power = 1, 0, p["initial_voltage_V"], None
    # Hold the controller state across the environmental step, as real P&O does.
    # Settling is measured separately in each illuminated phase.
    suffix_start = [None, None]
    for index in range(steps):
        phase = int(index >= change)
        points = phases[phase]
        voc, isc, vmp, imp = points
        available = vmp * imp
        optimum_voltage = min(p["tracking_max_V"], max(p["tracking_min_V"], vmp))
        attainable = (
            optimum_voltage * current_at(optimum_voltage, points)
            if voc >= p["tracking_min_V"]
            else 0.0
        )
        # An ideal receiver cannot drive a passive solar source above Voc.
        voltage = min(command, voc)
        current = current_at(voltage, points) if voc >= p["tracking_min_V"] else 0.0
        power = voltage * current
        available_energy += available * period
        attainable_energy += attainable * period
        tracked_energy += power * period
        min_voltage, max_voltage, max_current = (
            min(min_voltage, voltage),
            max(max_voltage, voltage),
            max(max_current, current),
        )
        if available > 0:
            error = max(0.0, 1 - power / available)
            max_error = max(max_error, error)
            if error <= p["settling_relative_band"]:
                if suffix_start[phase] is None:
                    suffix_start[phase] = index
            else:
                suffix_start[phase] = None
        # One perturbation per sample. Reverse immediately at a voltage bound.
        if previous_power is not None and power < previous_power:
            direction *= -1
            reversals += 1
        proposed = command + direction * p["voltage_step_V"]
        if not p["tracking_min_V"] <= proposed <= p["tracking_max_V"]:
            direction *= -1
            reversals += 1
            proposed = command + direction * p["voltage_step_V"]
        command = min(p["tracking_max_V"], max(p["tracking_min_V"], proposed))
        previous_power = power
    settling_times = []
    settled = bool(lit)
    for phase, start, end in ((0, 0, change), (1, change, steps)):
        if start == end or phases[phase][0] == 0:
            continue
        suffix = suffix_start[phase]
        if suffix is None or (end - suffix) * period + 1e-12 < p["settling_hold_s"]:
            settled = False
        else:
            settling_times.append((suffix - start) * period)
    print(
        f"Ideal P&O, {steps} samples and {reversals} reversals. Uniform section, empirical I-V model, "
        "instantaneous voltage actuation and fixed conversion efficiency. No converter dynamics, "
        "noise, bypass diodes, partial shading or hardware qualification.",
        file=sys.stderr,
    )
    return {
        "available_energy_J": available_energy,
        "attainable_energy_J": attainable_energy,
        "tracked_energy_J": tracked_energy,
        "delivered_energy_J": tracked_energy * p["conversion_efficiency"],
        "tracking_efficiency": tracked_energy / attainable_energy
        if attainable_energy
        else None,
        "capture_efficiency": tracked_energy / available_energy
        if available_energy
        else None,
        "min_mpp_voltage_V": min(points[2] for points in lit) if lit else None,
        "max_mpp_voltage_V": max(points[2] for points in lit) if lit else None,
        "max_open_circuit_voltage_V": max(points[0] for points, count in active),
        "max_short_circuit_current_A": max(points[1] for points, count in active),
        "min_operating_voltage_V": min_voltage,
        "max_operating_voltage_V": max_voltage,
        "max_input_current_A": max_current,
        "settled": settled,
        "settling_time_s": max(settling_times) if settled else None,
        "max_power_error_fraction": max_error if lit else None,
        "sample_count": steps,
        "voltage_reversals": reversals,
    }


class MPPT(VerificationScript):
    definition_spec = ScriptDefinition(
        id="mppt_po",
        name="MPPT perturb and observe",
        description="Ideal sampled P&O controller for one uniformly illuminated section, using four reference I-V points, temperature and irradiance scaling, a tracking voltage window and one environmental step. Returns energy, settling and input envelope evidence. See analyses/README.md for limits.",
        inputs=(
            ScriptPort("voc_ref_V", float, "V"),
            ScriptPort("isc_ref_A", float, "A"),
            ScriptPort("vmp_ref_V", float, "V"),
            ScriptPort("imp_ref_A", float, "A"),
            ScriptPort("reference_irradiance_W_m2", float, "W/m**2"),
            ScriptPort("reference_temperature_C", float, "degC"),
            ScriptPort("voltage_temp_coeff_V_C", float, "V/degC"),
            ScriptPort("current_temp_coeff_per_C", float, "1/degC"),
            ScriptPort("voltage_log_coefficient_V", float, "V"),
            ScriptPort("irradiance_start_W_m2", float, "W/m**2"),
            ScriptPort("irradiance_end_W_m2", float, "W/m**2"),
            ScriptPort("temperature_start_C", float, "degC"),
            ScriptPort("temperature_end_C", float, "degC"),
            ScriptPort("change_time_s", float, "s"),
            ScriptPort("duration_s", float, "s"),
            ScriptPort("sample_period_s", float, "s"),
            ScriptPort("voltage_step_V", float, "V"),
            ScriptPort("initial_voltage_V", float, "V"),
            ScriptPort("tracking_min_V", float, "V"),
            ScriptPort("tracking_max_V", float, "V"),
            ScriptPort("conversion_efficiency", float, None),
            ScriptPort("settling_relative_band", float, None),
            ScriptPort("settling_hold_s", float, "s"),
        ),
        outputs=(
            ScriptPort("available_energy_J", float, "J"),
            ScriptPort("attainable_energy_J", float, "J"),
            ScriptPort("tracked_energy_J", float, "J"),
            ScriptPort("delivered_energy_J", float, "J"),
            ScriptPort("tracking_efficiency", float, None),
            ScriptPort("capture_efficiency", float, None),
            ScriptPort("min_mpp_voltage_V", float, "V"),
            ScriptPort("max_mpp_voltage_V", float, "V"),
            ScriptPort("max_open_circuit_voltage_V", float, "V"),
            ScriptPort("max_short_circuit_current_A", float, "A"),
            ScriptPort("min_operating_voltage_V", float, "V"),
            ScriptPort("max_operating_voltage_V", float, "V"),
            ScriptPort("max_input_current_A", float, "A"),
            ScriptPort("settled", bool, None),
            ScriptPort("settling_time_s", float, "s"),
            ScriptPort("max_power_error_fraction", float, None),
            ScriptPort("sample_count", int, None),
            ScriptPort("voltage_reversals", int, None),
        ),
        timeout_ms=10000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return simulate(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(MPPT))
