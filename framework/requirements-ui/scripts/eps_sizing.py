"""Bounded preliminary sizing of ONE identical-cell PV section and battery.

Units: W, Wh, Ah, s, V and m^2; efficiencies/retentions/DoD are fractions.
P_req = 3600*(Es/Xs + Ee/Xe)/Ts; PV EOL power = Ns*Np*Pcell*k*fPV.
Battery preliminary BOL requirement = Ee/DoD*(1+M); retained requirement
= Ee/DoD. E_BOL=Ns*Np*Ecell, Q_BOL=Np*Qcell; E_EOL=fE*E_BOL,
Q_EOL=fQ*Q_BOL. M is NOT applied again to retained capacities.

Configured counts are evaluated unchanged. Proposals keep the declared series
count and increase/decrease parallel count only for non-fixed cell assemblies.
A fixed purchased product MUST use its aggregate ratings as a single equivalent
unit (Ns=Np=1, fixed=True), NOT inferred internal cell ratings. Its properties
and proposal stay fixed. Supported cell configurations and auxiliary circuits
must be reviewed separately. No product/cycle-life/mission defaults are supplied.

Pcell*k must be supplied at the attainable DET or MPPT operating point, averaged
in sunlight for this section; k includes declared illumination/temperature losses,
fPV only lifetime retention. No MPP/DET operating point is inferred. Voltage
intervals are complete ASSEMBLY extrema, not per-cell values or ratings inferred
from counts. The optional interval screen is necessary only: current, Voc absolute
maxima, startup/dropout, charger, shared tracker and conversion-map limits remain
unassessed. Thus interface_feasible can be False or None, never True.
See analyses/MODELS.md for exact input conventions and remaining scope.
"""
import json
import math
import sys

MAX_CELLS = 1000000
SAFE_INT = 9007199254740991
INTEGER_INPUTS = {"pv_series", "pv_parallel", "bat_series", "bat_parallel", "conversion_kind"}
BOOLEAN_INPUTS = {"pv_fixed", "bat_fixed", "interval_known"}
INPUTS = """sun_energy_Wh eclipse_energy_Wh sunlight_s sun_path_eff eclipse_path_eff
sizing_margin depth_of_discharge pv_cell_power_W pv_retained_factor pv_operating_factor
pv_series pv_parallel pv_fixed pv_cell_area_m2 usable_face_area_m2 packing_fraction
bat_cell_energy_Wh bat_cell_charge_Ah bat_series bat_parallel bat_fixed
energy_retained_factor charge_retained_factor required_retained_charge_Ah source_low_V
source_high_V receiver_low_V receiver_high_V interval_known conversion_kind output_low_V output_high_V""".split()


def validate(p):
    if not isinstance(p, dict) or set(p) != set(INPUTS):
        raise ValueError("Supply exactly the declared inputs.")
    for name, value in p.items():
        if name in BOOLEAN_INPUTS:
            if type(value) is not bool:
                raise ValueError(f"{name} must be boolean.")
        elif name in INTEGER_INPUTS:
            if type(value) is not int or abs(value) > SAFE_INT:
                raise ValueError(f"{name} must be a safe integer.")
        elif type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    for name in ("sun_energy_Wh", "eclipse_energy_Wh", "sizing_margin", "required_retained_charge_Ah", "usable_face_area_m2"):
        if p[name] < 0:
            raise ValueError(f"{name} must be nonnegative.")
    for name in ("sunlight_s", "pv_cell_power_W", "pv_cell_area_m2", "bat_cell_energy_Wh", "bat_cell_charge_Ah"):
        if p[name] <= 0:
            raise ValueError(f"{name} must be positive.")
    for name in ("sun_path_eff", "eclipse_path_eff", "depth_of_discharge", "packing_fraction"):
        if not 0 < p[name] <= 1:
            raise ValueError(f"{name} must be in (0,1].")
    for name in ("pv_operating_factor", "pv_retained_factor", "energy_retained_factor", "charge_retained_factor"):
        if not 0 <= p[name] <= 1:
            raise ValueError(f"{name} must be in [0,1].")
    for group in ("pv", "bat"):
        ns, np = p[group + "_series"], p[group + "_parallel"]
        if ns < 1 or np < 1 or ns * np > MAX_CELLS:
            raise ValueError("Configured positive integer counts must total at most 1000000 cells.")
    if p["conversion_kind"] not in (0, 1, 2, 3):
        raise ValueError("conversion_kind must be 0=direct/DET, 1=buck, 2=boost, 3=buck-boost.")
    # Unknown interval placeholders still must be finite, but are not interpreted.
    if p["interval_known"]:
        for prefix in ("source", "receiver", "output"):
            if not 0 < p[prefix + "_low_V"] <= p[prefix + "_high_V"]:
                raise ValueError(f"{prefix} voltage interval must be positive and ordered.")


def safe_ceil(value):
    if not math.isfinite(value) or value > SAFE_INT:
        raise ValueError("Required count exceeds the safe-integer representability limit.")
    return math.ceil(value)


def calculate(p):
    validate(p)
    required = 3600 * (p["sun_energy_Wh"] / p["sun_path_eff"] + p["eclipse_energy_Wh"] / p["eclipse_path_eff"]) / p["sunlight_s"]
    pv_bol = p["pv_cell_power_W"] * p["pv_operating_factor"]
    pv_eol = pv_bol * p["pv_retained_factor"]
    ns, np = p["pv_series"], p["pv_parallel"]
    min_cells = safe_ceil(required / pv_eol) if pv_eol > 0 else (0 if required == 0 else None)
    needed_pv_parallel = max(1, (min_cells + ns - 1) // ns) if min_cells is not None else None
    pv_in_bounds = needed_pv_parallel is not None and ns * needed_pv_parallel <= MAX_CELLS
    proposed_pv = np if p["pv_fixed"] else (needed_pv_parallel if pv_in_bounds else None)
    required_area = ns * needed_pv_parallel * p["pv_cell_area_m2"] / p["packing_fraction"] if needed_pv_parallel is not None else None
    active_area = ns * np * p["pv_cell_area_m2"]
    bol_required = p["eclipse_energy_Wh"] / p["depth_of_discharge"] * (1 + p["sizing_margin"])
    retained_required = p["eclipse_energy_Wh"] / p["depth_of_discharge"]
    bs, bp = p["bat_series"], p["bat_parallel"]
    e_string = bs * p["bat_cell_energy_Wh"]
    q_string = p["bat_cell_charge_Ah"]
    def capacity_count(required_capacity, string_capacity):
        return safe_ceil(required_capacity / string_capacity) if string_capacity > 0 else (0 if required_capacity == 0 else None)

    counts = [capacity_count(bol_required, e_string),
              capacity_count(retained_required, e_string * p["energy_retained_factor"]),
              capacity_count(p["required_retained_charge_Ah"], q_string * p["charge_retained_factor"])]
    needed_bat_parallel = max(1, *counts) if all(c is not None for c in counts) else None
    bat_in_bounds = needed_bat_parallel is not None and bs * needed_bat_parallel <= MAX_CELLS
    proposed_bat = bp if p["bat_fixed"] else (needed_bat_parallel if bat_in_bounds else None)
    e_bol, q_bol = e_string * bp, q_string * bp
    e_eol, q_eol = e_bol * p["energy_retained_factor"], q_bol * p["charge_retained_factor"]
    margins = {
        "generation_margin_W": ns * np * pv_eol - required,
        "packing_margin_m2": p["usable_face_area_m2"] * p["packing_fraction"] - active_area,
        "bol_energy_margin_Wh": e_bol - bol_required,
        "retained_energy_margin_Wh": e_eol - retained_required,
        "retained_charge_margin_Ah": q_eol - p["required_retained_charge_Ah"],
    }
    input_margin = conversion_margin = voltage_ok = None
    if p["interval_known"]:
        lo, hi = p["source_low_V"], p["source_high_V"]
        input_margin = min(lo - p["receiver_low_V"], p["receiver_high_V"] - hi)
        kind = p["conversion_kind"]
        # Conservative Cartesian interval screens; no efficiency/dropout inferred.
        if kind == 0:
            conversion_margin = min(lo - p["output_low_V"], p["output_high_V"] - hi)
        elif kind == 1:
            conversion_margin = lo - p["output_high_V"]
        elif kind == 2:
            conversion_margin = p["output_low_V"] - hi
        # Buck-boost requires a supplied conversion envelope, absent here.
        voltage_ok = False if input_margin < 0 or (conversion_margin is not None and conversion_margin < 0) else (True if conversion_margin is not None else None)
    return {
        "required_generation_W": required, "pv_cell_eol_W": pv_eol,
        "pv_min_cells": min_cells, "pv_installed_cells": ns * np,
        "pv_proposed_series": ns, "pv_proposed_parallel": proposed_pv,
        "pv_generation_bol_W": ns * np * pv_bol, "pv_generation_eol_W": ns * np * pv_eol,
        "active_area_m2": active_area, "required_area_m2": required_area,
        "installed_area_m2": active_area / p["packing_fraction"],
        "required_bol_energy_Wh": bol_required, "required_retained_energy_Wh": retained_required,
        "required_bol_charge_Ah": (p["required_retained_charge_Ah"] / p["charge_retained_factor"] if p["charge_retained_factor"] > 0 else (0.0 if p["required_retained_charge_Ah"] == 0 else None)),
        "battery_energy_bol_Wh": e_bol, "battery_energy_eol_Wh": e_eol,
        "battery_charge_bol_Ah": q_bol, "battery_charge_eol_Ah": q_eol,
        "bat_proposed_series": bs, "bat_proposed_parallel": proposed_bat,
        "bat_installed_cells": bs * bp, "input_voltage_margin_V": input_margin,
        "conversion_margin_V": conversion_margin, "voltage_screen_ok": voltage_ok,
        "interface_feasible": False if voltage_ok is False else None,
        "sizing_ok": all(value >= 0 for value in margins.values()),
        "proposal_within_bounds": proposed_pv is not None and proposed_bat is not None,
        **margins,
    }


def main():
    try:
        request = json.load(sys.stdin)
        result = calculate(request["inputs"])
        encoded = json.dumps(result, allow_nan=False)
    except (ValueError, KeyError, TypeError, OverflowError, ZeroDivisionError) as exc:
        print(f"eps_sizing: {exc}", file=sys.stderr)
        return 1
    print(encoded)
    return 0


if __name__ == "__main__":
    sys.exit(main())
