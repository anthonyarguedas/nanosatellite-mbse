"""One oriented component box, axis-aligned installation box and oriented keep-out.

All lengths and translations are metres, angles degrees. Right-handed frame;
local boxes are centred at their declared centres. Active rotation local->frame
is Rz(yaw)*Ry(pitch)*Rx(roll). No mounting, connector or deployment geometry is
inferred: include it in the declared envelopes and run each required state.

World AABB half extent i is sum_j |R_ij|*half_size_j. Containment uses six face
margins. Exact OBB overlap in real arithmetic uses the separating axis theorem:
three axes of each box and nine pairwise cross products. For each UNIT axis u,
gap=|delta_center dot u|-sum_j hA_j*|a_j dot u|-sum_j hB_j*|b_j dot u|.
The maximum gap is a signed PROJECTION gap (not Euclidean clearance or overlap
volume); a positive value proves separation. Zero cross products are skipped.
Double precision and the engineer-supplied tolerance determine contact handling.
Containment allows margins >= -tolerance_m. If touching_allowed=True, keep-out
is clear at gap >= -tolerance_m; otherwise clear only at gap > tolerance_m.
The tolerance is a contact/numerical policy, not an automatically chosen margin.
"""

import math
import sys

from ..core.verification import (
    ScriptDefinition,
    ScriptPort,
    VerificationScript,
    cli_main,
)

INPUTS = """size_x_m size_y_m size_z_m center_x_m center_y_m center_z_m
roll_deg pitch_deg yaw_deg install_min_x_m install_min_y_m install_min_z_m
install_max_x_m install_max_y_m install_max_z_m keep_size_x_m keep_size_y_m
keep_size_z_m keep_center_x_m keep_center_y_m keep_center_z_m keep_roll_deg
keep_pitch_deg keep_yaw_deg touching_allowed tolerance_m""".split()


def dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def rotation(roll, pitch, yaw):
    # Reducing angles avoids loss in radians conversion for large finite angles.
    r, p, y = (math.radians(value % 360) for value in (roll, pitch, yaw))
    cr, sr, cp, sp, cy, sy = (
        math.cos(r),
        math.sin(r),
        math.cos(p),
        math.sin(p),
        math.cos(y),
        math.sin(y),
    )
    # Return the three columns: transformed local basis vectors.
    return (
        (cy * cp, sy * cp, -sp),
        (cy * sp * sr - sy * cr, sy * sp * sr + cy * cr, cp * sr),
        (cy * sp * cr + sy * sr, sy * sp * cr - cy * sr, cp * cr),
    )


def box(p, prefix):
    half = tuple(p[prefix + "size_" + axis + "_m"] / 2 for axis in "xyz")
    center = tuple(p[prefix + "center_" + axis + "_m"] for axis in "xyz")
    axes = rotation(*(p[prefix + angle + "_deg"] for angle in ("roll", "pitch", "yaw")))
    extent = tuple(
        math.fsum(abs(axes[j][i]) * half[j] for j in range(3)) for i in range(3)
    )
    return (
        half,
        center,
        axes,
        tuple(center[i] - extent[i] for i in range(3)),
        tuple(center[i] + extent[i] for i in range(3)),
    )


def calculate(p):
    if not isinstance(p, dict) or set(p) != set(INPUTS):
        raise ValueError("Supply exactly the declared inputs.")
    for name, value in p.items():
        if name == "touching_allowed":
            if type(value) is not bool:
                raise ValueError("touching_allowed must be boolean.")
        elif type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    for prefix in ("", "keep_"):
        if any(p[prefix + "size_" + axis + "_m"] <= 0 for axis in "xyz"):
            raise ValueError("Box dimensions must be positive.")
    if p["tolerance_m"] < 0:
        raise ValueError("tolerance_m must be nonnegative.")
    if any(
        p["install_min_" + axis + "_m"] >= p["install_max_" + axis + "_m"]
        for axis in "xyz"
    ):
        raise ValueError("Installation bounds must be strictly ordered.")
    a, b = box(p, ""), box(p, "keep_")
    delta = tuple(b[1][i] - a[1][i] for i in range(3))
    axes = list(a[2]) + list(b[2]) + [cross(u, v) for u in a[2] for v in b[2]]
    gaps = []
    for axis in axes:
        norm = math.hypot(*axis)
        if norm == 0:
            continue
        unit = tuple(value / norm for value in axis)
        radius_a = math.fsum(a[0][j] * abs(dot(unit, a[2][j])) for j in range(3))
        radius_b = math.fsum(b[0][j] * abs(dot(unit, b[2][j])) for j in range(3))
        gaps.append(abs(dot(delta, unit)) - radius_a - radius_b)
    gap = max(gaps)
    result = {}
    margins = []
    for i, axis in enumerate("xyz"):
        result["bound_min_" + axis + "_m"], result["bound_max_" + axis + "_m"] = (
            a[3][i],
            a[4][i],
        )
        (
            result["keep_bound_min_" + axis + "_m"],
            result["keep_bound_max_" + axis + "_m"],
        ) = b[3][i], b[4][i]
        low = a[3][i] - p["install_min_" + axis + "_m"]
        high = p["install_max_" + axis + "_m"] - a[4][i]
        result["contain_low_" + axis + "_m"], result["contain_high_" + axis + "_m"] = (
            low,
            high,
        )
        margins.extend((low, high))
    contained = min(margins) >= -p["tolerance_m"]
    clear = (
        gap >= -p["tolerance_m"] if p["touching_allowed"] else gap > p["tolerance_m"]
    )
    result.update(
        volume_m3=p["size_x_m"] * p["size_y_m"] * p["size_z_m"],
        containment_margin_m=min(margins),
        contained=contained,
        keepout_gap_m=gap,
        keepout_clear=clear,
        overlap=not clear,
        accommodation_ok=contained and clear,
        axes_tested=len(gaps),
    )
    return result


class Geometry(VerificationScript):
    definition_spec = ScriptDefinition(
        id="eps_geometry",
        name="EPS oriented box accommodation",
        description="Transform one rectangular component envelope and one keep-out to an installation frame. Six containment margins and 15-axis SAT detect box intersection with an explicit touching/tolerance policy. Projection gap is not Euclidean clearance. Mounting and access are assessed only if represented by the declared envelopes. See analyses/MODELS.md.",
        inputs=(
            ScriptPort("size_x_m", float, "m"),
            ScriptPort("size_y_m", float, "m"),
            ScriptPort("size_z_m", float, "m"),
            ScriptPort("center_x_m", float, "m"),
            ScriptPort("center_y_m", float, "m"),
            ScriptPort("center_z_m", float, "m"),
            ScriptPort("roll_deg", float, "deg"),
            ScriptPort("pitch_deg", float, "deg"),
            ScriptPort("yaw_deg", float, "deg"),
            ScriptPort("install_min_x_m", float, "m"),
            ScriptPort("install_min_y_m", float, "m"),
            ScriptPort("install_min_z_m", float, "m"),
            ScriptPort("install_max_x_m", float, "m"),
            ScriptPort("install_max_y_m", float, "m"),
            ScriptPort("install_max_z_m", float, "m"),
            ScriptPort("keep_size_x_m", float, "m"),
            ScriptPort("keep_size_y_m", float, "m"),
            ScriptPort("keep_size_z_m", float, "m"),
            ScriptPort("keep_center_x_m", float, "m"),
            ScriptPort("keep_center_y_m", float, "m"),
            ScriptPort("keep_center_z_m", float, "m"),
            ScriptPort("keep_roll_deg", float, "deg"),
            ScriptPort("keep_pitch_deg", float, "deg"),
            ScriptPort("keep_yaw_deg", float, "deg"),
            ScriptPort("touching_allowed", bool, None),
            ScriptPort("tolerance_m", float, "m"),
        ),
        outputs=(
            ScriptPort("bound_min_x_m", float, "m"),
            ScriptPort("bound_min_y_m", float, "m"),
            ScriptPort("bound_min_z_m", float, "m"),
            ScriptPort("bound_max_x_m", float, "m"),
            ScriptPort("bound_max_y_m", float, "m"),
            ScriptPort("bound_max_z_m", float, "m"),
            ScriptPort("keep_bound_min_x_m", float, "m"),
            ScriptPort("keep_bound_min_y_m", float, "m"),
            ScriptPort("keep_bound_min_z_m", float, "m"),
            ScriptPort("keep_bound_max_x_m", float, "m"),
            ScriptPort("keep_bound_max_y_m", float, "m"),
            ScriptPort("keep_bound_max_z_m", float, "m"),
            ScriptPort("contain_low_x_m", float, "m"),
            ScriptPort("contain_low_y_m", float, "m"),
            ScriptPort("contain_low_z_m", float, "m"),
            ScriptPort("contain_high_x_m", float, "m"),
            ScriptPort("contain_high_y_m", float, "m"),
            ScriptPort("contain_high_z_m", float, "m"),
            ScriptPort("volume_m3", float, "m**3"),
            ScriptPort("containment_margin_m", float, "m"),
            ScriptPort("contained", bool, None),
            ScriptPort("keepout_gap_m", float, "m"),
            ScriptPort("keepout_clear", bool, None),
            ScriptPort("overlap", bool, None),
            ScriptPort("accommodation_ok", bool, None),
            ScriptPort("axes_tested", int, None),
        ),
        timeout_ms=3000,
    )

    def calculate(self, inputs, *, requirements=None, mode=None):
        return calculate(inputs)


if __name__ == "__main__":
    sys.exit(cli_main(Geometry))
