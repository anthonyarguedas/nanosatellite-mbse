"""Bounded three-phase sampled protection MIL; conventions: analyses/PATHS.md."""

import math
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)


BOOLS = set(
    (
        "nominal_command_on fault_command_on recovery_command_on nominal_inhibited "
        "fault_inhibited recovery_inhibited processor_available autonomous_protection "
        "autonomous_inhibit processor_off_output_on auto_reset"
    ).split()
)
NUMBERS = (
    "nominal_voltage_V fault_voltage_V recovery_voltage_V legitimate_current_A "
    "fault_current_A recovery_current_A nominal_duration_s fault_duration_s "
    "recovery_duration_s step_s uv_trip_V uv_reset_V ov_trip_V ov_reset_V "
    "oc_trip_A oc_reset_A trip_delay_s reset_delay_s i2t_limit_A2s peak_limit_A interruption_limit_s"
).split()
MAX_STEPS = 100000


def grid_steps(duration, step):
    ratio = duration / step
    if not math.isfinite(ratio) or ratio > MAX_STEPS:
        raise ValueError("scenario exceeds 100000 steps")
    count = round(ratio)
    if (duration > 0 and count == 0) or not math.isclose(
        ratio, count, rel_tol=0, abs_tol=1e-8
    ):
        raise ValueError("phase durations must be integer multiples of step_s")
    return count


def delay_steps(delay, step):
    ratio = delay / step
    if not math.isfinite(ratio) or ratio > MAX_STEPS:
        # A delay longer than the entire allowed run cannot expire.
        return MAX_STEPS + 1
    if delay == 0:
        return 0
    nearest = round(ratio)
    return max(
        1,
        nearest
        if math.isclose(ratio, nearest, rel_tol=0, abs_tol=1e-8)
        else math.ceil(ratio),
    )


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
    if p["step_s"] <= 0 or p["fault_duration_s"] <= 0:
        raise ValueError("step_s and fault_duration_s must be positive")
    if not (
        p["uv_trip_V"] <= p["uv_reset_V"] <= p["ov_reset_V"] <= p["ov_trip_V"]
        and p["uv_trip_V"] < p["ov_trip_V"]
        and p["oc_reset_A"] <= p["oc_trip_A"]
    ):
        raise ValueError("threshold order/hysteresis is invalid")
    phases = []
    for label, current_name in (
        ("nominal", "legitimate_current_A"),
        ("fault", "fault_current_A"),
        ("recovery", "recovery_current_A"),
    ):
        phases.append(
            (
                label,
                grid_steps(p[label + "_duration_s"], p["step_s"]),
                p[label + "_voltage_V"],
                p[current_name],
                p[label + "_command_on"],
                p[label + "_inhibited"],
            )
        )
    total_steps = sum(phase[1] for phase in phases)
    if total_steps > MAX_STEPS:
        raise ValueError("scenario exceeds 100000 steps")
    h = p["step_s"]
    trip_steps = delay_steps(p["trip_delay_s"], h)
    reset_steps = delay_steps(p["reset_delay_s"], h)
    active = p["processor_available"] or p["autonomous_protection"]
    latched = False
    bad_ticks = good_ticks = index = 0
    last_on = None
    transitions = trip_count = reset_count = nominal_trips = 0
    first_trip = first_reset = interruption = recovery = None
    nominal_unserved = recovery_unserved = fault_on = total_on = inhibited_on = 0
    fault_i2t = fault_peak = 0.0
    inhibited_violation = reenergized = False
    fault_start = phases[0][1]
    recovery_start = fault_start + phases[1][1]

    def conditions(voltage, current):
        bad = (
            voltage <= p["uv_trip_V"]
            or voltage >= p["ov_trip_V"]
            or current >= p["oc_trip_A"]
        )
        good = (
            not bad
            and voltage >= p["uv_reset_V"]
            and voltage <= p["ov_reset_V"]
            and current <= p["oc_reset_A"]
        )
        return bad, good

    fault_seen = conditions(phases[1][2], phases[1][3])[0]

    def state(command, inhibited):
        enabled = command if p["processor_available"] else p["processor_off_output_on"]
        inhibit_effective = inhibited and (
            p["processor_available"] or p["autonomous_inhibit"]
        )
        return enabled and not inhibit_effective and not latched

    for label, count, voltage, current, command, inhibited in phases:
        bad, good = conditions(voltage, current)
        for unused in range(count):
            now = index * h
            # Zero delays act at the left boundary, before supplying this interval.
            if active and not latched and bad and trip_steps == 0:
                latched = True
                trip_count += 1
                nominal_trips += int(label == "nominal")
                first_trip = now if first_trip is None else first_trip
                bad_ticks = good_ticks = 0
            elif active and latched and good and p["auto_reset"] and reset_steps == 0:
                latched = False
                reset_count += 1
                first_reset = now if first_reset is None else first_reset
                bad_ticks = good_ticks = 0
            on = state(command, inhibited)
            if last_on is not None and on != last_on:
                transitions += 1
            last_on = on
            if inhibited and on:
                inhibited_violation = True
                inhibited_on += 1
            desired = (
                command if p["processor_available"] else p["processor_off_output_on"]
            ) and not inhibited
            if label == "nominal" and desired and not on:
                nominal_unserved += 1
            if label == "recovery":
                if desired and not on:
                    recovery_unserved += 1
                if interruption is not None and on and recovery is None:
                    recovery = (index - recovery_start) * h
            if label == "fault":
                if not on and interruption is None:
                    interruption = (index - fault_start) * h
                if on:
                    reenergized = reenergized or interruption is not None
                    fault_on += 1
                    fault_peak = max(fault_peak, current)
            total_on += int(on)
            index += 1
            # Positive delays accrue whole intervals. A condition must remain
            # true continuously; timers clear on nonqualifying samples.
            if not active:
                bad_ticks = good_ticks = 0
            elif not latched:
                good_ticks = 0
                bad_ticks = bad_ticks + 1 if bad else 0
                if bad and trip_steps > 0 and bad_ticks >= trip_steps:
                    latched = True
                    trip_count += 1
                    nominal_trips += int(label == "nominal")
                    first_trip = index * h if first_trip is None else first_trip
                    bad_ticks = good_ticks = 0
                    if label == "fault" and interruption is None:
                        interruption = (index - fault_start) * h
            else:
                bad_ticks = 0
                good_ticks = good_ticks + 1 if good and p["auto_reset"] else 0
                if (
                    good
                    and p["auto_reset"]
                    and reset_steps > 0
                    and good_ticks >= reset_steps
                ):
                    latched = False
                    reset_count += 1
                    first_reset = index * h if first_reset is None else first_reset
                    bad_ticks = good_ticks = 0

    # Include the final right-boundary state, but no zero-duration energy/stress.
    final_phase = next(phase for phase in reversed(phases) if phase[1] > 0)
    label, count, voltage, current, command, inhibited = final_phase
    final_on = state(command, inhibited)
    transitions += int(final_on != last_on)
    inhibited_violation = inhibited_violation or (inhibited and final_on)
    if (
        label == "recovery"
        and interruption is not None
        and final_on
        and recovery is None
    ):
        recovery = (index - recovery_start) * h
    fault_i2t = p["fault_current_A"] ** 2 * fault_on * h
    stress_ok = fault_i2t <= p["i2t_limit_A2s"] and fault_peak <= p["peak_limit_A"]
    interruption_ok = (
        None
        if not fault_seen
        else interruption is not None and interruption <= p["interruption_limit_s"]
    )
    return {
        "transition_count": transitions,
        "trip_count": trip_count,
        "reset_count": reset_count,
        "nominal_trip_count": nominal_trips,
        "first_trip_time_s": first_trip,
        "first_reset_time_s": first_reset,
        "fault_interruption_s": interruption,
        "recovery_time_s": recovery,
        "nominal_unserved_s": nominal_unserved * h,
        "recovery_unserved_s": recovery_unserved * h,
        "fault_i2t_A2s": fault_i2t,
        "fault_peak_A": fault_peak,
        "inhibited_on_s": inhibited_on * h,
        "final_output_on": final_on,
        "final_latched": latched,
        "fault_seen": fault_seen,
        "fault_interrupted": interruption is not None,
        "fault_reenergized": reenergized,
        "nuisance_free": nominal_trips == 0 and nominal_unserved == 0,
        "inhibited_outputs_off": not inhibited_violation,
        "stress_ok": stress_ok,
        "interruption_ok": interruption_ok,
        "recovery_observed": recovery is not None,
        "protection_active": active,
        "protection_ok": None
        if not fault_seen
        else interruption_ok and stress_ok and not reenergized,
        "sample_count": total_steps,
        "fault_output_on_s": fault_on * h,
        "total_on_s": total_on * h,
    }


class Protection(VerificationScript):
    definition_spec = ScriptDefinition(
        id="eps_protection",
        name="EPS three-phase protection MIL",
        description="Initially unlatched nominal/fault/recovery scenario with inclusive UV/OV/OC trips, hysteretic automatic or latched reset, explicit logical commands/inhibits and processor-off policies. Prospective current remains sensed while off. At most 100000 steps; phase durations align to the step. See analyses/PATHS.md for exact timer conventions and evidence limits.",
        inputs=(
            ScriptPort("nominal_voltage_V", float, "V"),
            ScriptPort("fault_voltage_V", float, "V"),
            ScriptPort("recovery_voltage_V", float, "V"),
            ScriptPort("legitimate_current_A", float, "A"),
            ScriptPort("fault_current_A", float, "A"),
            ScriptPort("recovery_current_A", float, "A"),
            ScriptPort("nominal_duration_s", float, "s"),
            ScriptPort("fault_duration_s", float, "s"),
            ScriptPort("recovery_duration_s", float, "s"),
            ScriptPort("step_s", float, "s"),
            ScriptPort("uv_trip_V", float, "V"),
            ScriptPort("uv_reset_V", float, "V"),
            ScriptPort("ov_trip_V", float, "V"),
            ScriptPort("ov_reset_V", float, "V"),
            ScriptPort("oc_trip_A", float, "A"),
            ScriptPort("oc_reset_A", float, "A"),
            ScriptPort("trip_delay_s", float, "s"),
            ScriptPort("reset_delay_s", float, "s"),
            ScriptPort("nominal_command_on", bool, None),
            ScriptPort("fault_command_on", bool, None),
            ScriptPort("recovery_command_on", bool, None),
            ScriptPort("nominal_inhibited", bool, None),
            ScriptPort("fault_inhibited", bool, None),
            ScriptPort("recovery_inhibited", bool, None),
            ScriptPort("processor_available", bool, None),
            ScriptPort("autonomous_protection", bool, None),
            ScriptPort("autonomous_inhibit", bool, None),
            ScriptPort("processor_off_output_on", bool, None),
            ScriptPort("auto_reset", bool, None),
            ScriptPort("i2t_limit_A2s", float, "A2 s"),
            ScriptPort("peak_limit_A", float, "A"),
            ScriptPort("interruption_limit_s", float, "s"),
        ),
        outputs=(
            ScriptPort("transition_count", int, None),
            ScriptPort("trip_count", int, None),
            ScriptPort("reset_count", int, None),
            ScriptPort("nominal_trip_count", int, None),
            ScriptPort("first_trip_time_s", float, "s"),
            ScriptPort("first_reset_time_s", float, "s"),
            ScriptPort("fault_interruption_s", float, "s"),
            ScriptPort("recovery_time_s", float, "s"),
            ScriptPort("nominal_unserved_s", float, "s"),
            ScriptPort("recovery_unserved_s", float, "s"),
            ScriptPort("fault_i2t_A2s", float, "A2 s"),
            ScriptPort("fault_peak_A", float, "A"),
            ScriptPort("inhibited_on_s", float, "s"),
            ScriptPort("final_output_on", bool, None),
            ScriptPort("final_latched", bool, None),
            ScriptPort("fault_seen", bool, None),
            ScriptPort("fault_interrupted", bool, None),
            ScriptPort("fault_reenergized", bool, None),
            ScriptPort("nuisance_free", bool, None),
            ScriptPort("inhibited_outputs_off", bool, None),
            ScriptPort("stress_ok", bool, None),
            ScriptPort("interruption_ok", bool, None),
            ScriptPort("recovery_observed", bool, None),
            ScriptPort("protection_active", bool, None),
            ScriptPort("protection_ok", bool, None),
            ScriptPort("sample_count", int, None),
            ScriptPort("fault_output_on_s", float, "s"),
            ScriptPort("total_on_s", float, "s"),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return calculate(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(Protection))
