"""Exact charge-positive, linear-OCV, R0 + one R1C1 constant-current step."""
import json
import math
import sys


BOOLS = {"voltage_limits_known", "soc_limits_known"}
NUMBERS = (
    "capacity_C initial_soc current_A ocv_at_zero_V ocv_slope_V r0_ohm r1_ohm "
    "c1_F initial_polarization_V duration_s voltage_min_V voltage_max_V soc_min soc_max"
).split()


def shapes(x):
    """Dimensionless integrals of 1-exp(-x) and its square, without small-x cancellation."""
    d = -math.expm1(-x)
    f2 = -math.expm1(-2 * x) / 2
    if x < 0.1:
        h = math.fsum(((-1) ** n) * x ** n / math.factorial(n) for n in range(2, 24))
        square = math.fsum(((-1) ** (n + 1)) * (2 ** (n - 1) - 2) * x ** n /
                           math.factorial(n) for n in range(3, 24))
    else:
        h = x - d
        square = x - 2 * d + f2
    return d, h, f2, square


def calculate(p):
    if set(p) != set(NUMBERS) | BOOLS:
        raise ValueError("inputs must contain exactly the declared names")
    for name in BOOLS:
        if type(p[name]) is not bool:
            raise ValueError(name + " must be boolean")
    for name in NUMBERS:
        if type(p[name]) not in (int, float) or not math.isfinite(p[name]):
            raise ValueError(name + " must be finite numeric")
    for name in ("capacity_C", "r1_ohm", "c1_F", "ocv_at_zero_V"):
        if p[name] <= 0:
            raise ValueError(name + " must be positive")
    for name in ("duration_s", "r0_ohm", "ocv_slope_V", "voltage_min_V"):
        if p[name] < 0:
            raise ValueError(name + " must be nonnegative")
    if p["voltage_max_V"] < p["voltage_min_V"] or not 0 <= p["soc_min"] <= p["soc_max"] <= 1:
        raise ValueError("voltage/SOC limit bounds are invalid")
    current, t = p["current_A"], p["duration_s"]
    tau = p["r1_ohm"] * p["c1_F"]
    rate = current / p["capacity_C"]
    slope = p["ocv_slope_V"] * rate
    a = current * p["r1_ohm"]
    u0 = p["initial_polarization_V"]
    b = u0 - a
    ocv0 = p["ocv_at_zero_V"] + p["ocv_slope_V"] * p["initial_soc"]
    if tau <= 0 or not all(math.isfinite(v) for v in (tau, rate, slope, a, b, ocv0, t / tau)):
        raise ValueError("model arithmetic exceeds the finite numerical domain")

    def polarization(time):
        d = -math.expm1(-time / tau)
        return u0 * math.exp(-time / tau) + a * d

    def voltage(time):
        return ocv0 + slope * time + current * p["r0_ohm"] + polarization(time)

    extrema = [0.0, t]
    if slope != 0 and b != 0 and ((slope > 0) == (b > 0)):
        stationary = -tau * (math.log(abs(slope)) + math.log(tau) - math.log(abs(b)))
        if 0 < stationary < t:
            extrema.append(stationary)
    extrema = sorted(set(extrema))
    voltages = [voltage(time) for time in extrema]
    # At most two zero crossings, located in analytically monotone subintervals.
    cuts = list(extrema)
    for left, right in zip(extrema, extrema[1:]):
        vl, vr = voltage(left), voltage(right)
        if (vl < 0 < vr) or (vr < 0 < vl):
            lo, hi = left, right
            for unused in range(80):
                mid = (lo + hi) / 2
                if (voltage(mid) >= 0) == (vl >= 0):
                    lo = mid
                else:
                    hi = mid
            cuts.append((lo + hi) / 2)
    cuts = sorted(set(cuts))

    def terminal_integral(left, right):
        dt = right - left
        d, h, unused, unused2 = shapes(dt / tau)
        integrated_u = tau * (polarization(left) * d + a * h)
        integrated_v = ((ocv0 + slope * left + current * p["r0_ohm"]) * dt +
                        slope * dt * dt / 2 + integrated_u)
        return current * integrated_v

    segments = [terminal_integral(left, right) for left, right in zip(cuts, cuts[1:])]
    accepted = math.fsum(max(energy, 0) for energy in segments)
    delivered = math.fsum(max(-energy, 0) for energy in segments)
    d, h, f2, square = shapes(t / tau)
    if t == 0:
        integrated_u2 = 0.0
    else:
        f2 *= tau
        f01 = tau * d * d / 2
        f00 = tau * square
        # Complete the square to avoid cancellation when the branch crosses zero.
        remainder = f00 - f01 * (f01 / f2)
        if remainder < 0:
            raise ValueError("polarization loss integral lost numerical precision")
        integrated_u2 = f2 * (u0 + a * (f01 / f2)) ** 2 + a * a * remainder
    uend = polarization(t)
    umin2 = 0.0 if min(u0, uend) <= 0 <= max(u0, uend) else min(u0 * u0, uend * uend)
    umax2 = max(u0 * u0, uend * uend)
    ohmic_loss = current * current * p["r0_ohm"] * t
    branch_loss = integrated_u2 / p["r1_ohm"]
    zend = p["initial_soc"] + rate * t
    zmin, zmax = min(p["initial_soc"], zend), max(p["initial_soc"], zend)
    vmin, vmax = min(voltages), max(voltages)
    voltage_known, soc_known = p["voltage_limits_known"], p["soc_limits_known"]
    voltage_ok = p["voltage_min_V"] <= vmin and vmax <= p["voltage_max_V"] if voltage_known else None
    soc_ok = p["soc_min"] <= zmin and zmax <= p["soc_max"] if soc_known else None
    physical_soc_ok = 0 <= zmin and zmax <= 1
    findings = (voltage_ok, soc_ok, physical_soc_ok)
    step_ok = False if False in findings else None if None in findings else True
    return {
        "end_voltage_V": voltage(t), "min_voltage_V": vmin, "max_voltage_V": vmax,
        "end_soc": zend, "min_soc": zmin, "max_soc": zmax,
        "end_polarization_V": uend, "charge_change_C": current * t,
        "terminal_energy_J": math.fsum(segments), "accepted_energy_J": accepted,
        "delivered_energy_J": delivered, "ohmic_loss_J": ohmic_loss,
        "polarization_loss_J": branch_loss, "total_loss_J": ohmic_loss + branch_loss,
        "min_loss_W": current * current * p["r0_ohm"] + umin2 / p["r1_ohm"],
        "max_loss_W": current * current * p["r0_ohm"] + umax2 / p["r1_ohm"],
        "avg_loss_W": (ohmic_loss + branch_loss) / t if t > 0 else None,
        "voltage_low_margin_V": vmin - p["voltage_min_V"] if voltage_known else None,
        "voltage_high_margin_V": p["voltage_max_V"] - vmax if voltage_known else None,
        "soc_low_margin": zmin - p["soc_min"] if soc_known else None,
        "soc_high_margin": p["soc_max"] - zmax if soc_known else None,
        "voltage_ok": voltage_ok, "soc_ok": soc_ok, "physical_soc_ok": physical_soc_ok,
        "step_ok": step_ok, "polarization_energy_change_J": p["c1_F"] * (uend * uend - u0 * u0) / 2,
        "ocv_end_V": p["ocv_at_zero_V"] + p["ocv_slope_V"] * zend,
    }


def main():
    try:
        result = calculate(json.load(sys.stdin)["inputs"])
        text = json.dumps(result, allow_nan=False)
    except (ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError) as error:
        print("eps_battery_step: " + str(error), file=sys.stderr)
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
