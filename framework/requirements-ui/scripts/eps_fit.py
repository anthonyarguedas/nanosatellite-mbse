"""Quality-checked two-parameter fits of 3..5 supplied scalar samples.

model_kind=0: local PV I=a+b*V (x volts, y amperes); not a full I-V/diode fit.
model_kind=1: discharge V=E-R*I (x amperes, y volts); E=a, R=-b ohms.
model_kind=2: y=y_inf+A*exp(-t/tau), x seconds, y consistently volts or K.
The asymptote is KNOWN, not estimated. Fit log(abs(y-y_inf))=a+b*t;
A=sign(y-y_inf)*exp(a), tau=-1/b. This minimizes LOG-domain SSE, not
nonlinear original-domain SSE; original-domain residuals still set fit quality.

Unweighted least squares uses centred, span-normalized x to avoid unnecessary
conditioning loss. Declared min_x_span is an excitation threshold in x units.
All used samples must lie in the model's input domain. Masked placeholders are
finite supplied scalars, but excluded from domain checks and statistics. Mask
bits 1,2,4,8,16 select indices <= sample_count; at least 3 must survive (one
residual degree of freedom). Bad masks, degenerate excitation and invalid log
transforms error; poor residual fit/physical trend returns raw values and False.

Quality thresholds are engineer-supplied absolute y-unit RMSE/max-error limits,
not inferred measurement uncertainties. PV and battery slope must be <=0 for
physical_model_ok; PV intercept >=0, battery E>0. No general single-diode,
electrochemical, SoC, temperature dependence or coupled model calibration.
Sample min/max are an empirical validity DOMAIN, not validation outside it.
"""
import json
import math
import sys

INPUTS = ["model_kind", "sample_count", "valid_mask", "asymptote", "rmse_limit", "max_error_limit", "min_x_span"] + [name + str(i) for i in range(1, 6) for name in ("x", "y")]
INTEGER_INPUTS = {"model_kind", "sample_count", "valid_mask"}


def regression(xs, ys):
    xmin, xmax = min(xs), max(xs)
    span = xmax - xmin
    zs = [(x - xmin) / span for x in xs]
    zmean = math.fsum(z / len(zs) for z in zs)
    ymean = math.fsum(y / len(ys) for y in ys)
    sxx = math.fsum((z - zmean) ** 2 for z in zs)
    if sxx <= 0:
        raise ValueError("Unidentifiable model: degenerate excitation.")
    bz = math.fsum((z - zmean) * (y - ymean) for z, y in zip(zs, ys)) / sxx
    slope = bz / span
    intercept = ymean - bz * (zmean + xmin / span)
    predictions = [ymean + bz * (z - zmean) for z in zs]
    return intercept, slope, predictions


def calculate(p):
    if not isinstance(p, dict) or set(p) != set(INPUTS):
        raise ValueError("Supply exactly the declared inputs.")
    for name, value in p.items():
        if name in INTEGER_INPUTS:
            if type(value) is not int or abs(value) > 9007199254740991:
                raise ValueError(f"{name} must be a safe integer.")
        elif type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    kind, count, mask = p["model_kind"], p["sample_count"], p["valid_mask"]
    if kind not in (0, 1, 2):
        raise ValueError("model_kind must be 0=PV affine, 1=battery affine, 2=first-order exponential.")
    if not 3 <= count <= 5:
        raise ValueError("sample_count work bound is 3 through 5.")
    if mask < 0 or mask >= (1 << count):
        raise ValueError("valid_mask must select only declared sample indices.")
    indices = [i for i in range(1, count + 1) if mask & (1 << (i - 1))]
    if len(indices) < 3:
        raise ValueError("valid_mask must retain at least 3 samples for quality checking.")
    if p["min_x_span"] <= 0 or min(p["rmse_limit"], p["max_error_limit"]) < 0:
        raise ValueError("min_x_span must be positive and error limits nonnegative.")
    xs, ys = [p["x" + str(i)] for i in indices], [p["y" + str(i)] for i in indices]
    span = max(xs) - min(xs)
    if not math.isfinite(span) or span < p["min_x_span"] or span == 0:
        raise ValueError("Unidentifiable model: excitation span is below min_x_span or nonfinite.")
    if min(xs) < 0:
        raise ValueError("Used voltage/current/time x samples must be nonnegative.")
    if kind == 0 and min(ys) < 0 or kind == 1 and min(ys) <= 0:
        raise ValueError("Used PV current must be nonnegative; battery voltage must be positive.")
    sign = 1
    transformed = ys
    if kind == 2:
        deviations = [y - p["asymptote"] for y in ys]
        if not (all(d > 0 for d in deviations) or all(d < 0 for d in deviations)):
            raise ValueError("Exponential transformed domain requires nonzero deviations of one sign from the known asymptote.")
        sign = 1 if deviations[0] > 0 else -1
        transformed = [math.log(abs(d)) for d in deviations]
    intercept, slope, fitted = regression(xs, transformed)
    amplitude = tau = None
    if kind == 2:
        if slope >= 0:
            raise ValueError("Unidentifiable decaying first-order model: require negative transformed slope for finite positive tau.")
        amplitude, tau = sign * math.exp(intercept), -1 / slope
        if amplitude == 0:
            raise ValueError("Exponential amplitude is outside floating-point representability.")
        predictions = [p["asymptote"] + sign * math.exp(y) for y in fitted]
    else:
        predictions = fitted
    errors = [pred - y for pred, y in zip(predictions, ys)]
    n = len(xs)
    rmse = math.hypot(*errors) / math.sqrt(n)
    max_error = max(abs(e) for e in errors)
    transformed_rmse = math.hypot(*(a - b for a, b in zip(fitted, transformed))) / math.sqrt(n)
    ymean = math.fsum(y / n for y in ys)
    yspread = math.hypot(*(y - ymean for y in ys)) / math.sqrt(n)
    r_squared = 1 - (rmse / yspread) ** 2 if yspread > 0 else None
    physical = (intercept >= 0 and slope <= 0) if kind == 0 else ((intercept > 0 and slope <= 0) if kind == 1 else True)
    quality = rmse <= p["rmse_limit"] and max_error <= p["max_error_limit"]
    return {"fit_intercept": intercept, "fit_slope": slope,
            "pv_intercept_A": intercept if kind == 0 else None,
            "pv_slope_A_V": slope if kind == 0 else None,
            "battery_ocv_V": intercept if kind == 1 else None,
            "battery_resistance_ohm": -slope if kind == 1 else None,
            "exp_amplitude": amplitude, "time_constant_s": tau,
            "residual_rmse": rmse, "residual_max": max_error,
            "transformed_rmse": transformed_rmse, "r_squared": r_squared,
            "used_samples": n, "used_mask": mask, "residual_dof": n - 2,
            "domain_x_min": min(xs), "domain_x_max": max(xs),
            "domain_y_min": min(ys), "domain_y_max": max(ys),
            "fit_quality_ok": quality, "physical_model_ok": physical,
            "model_valid": quality and physical}


def main():
    try:
        request = json.load(sys.stdin)
        encoded = json.dumps(calculate(request["inputs"]), allow_nan=False)
    except (ValueError, KeyError, TypeError, OverflowError, ZeroDivisionError) as exc:
        print(f"eps_fit: {exc}", file=sys.stderr)
        return 1
    print(encoded)
    return 0


if __name__ == "__main__":
    sys.exit(main())
