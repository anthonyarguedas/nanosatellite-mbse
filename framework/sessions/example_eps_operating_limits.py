"""Sourced COTS no-trip screening and optional PV data.

Run: python3 -m framework.sessions.example_eps_operating_limits
The TPS259531 case uses its 1780 ohm current-limit setting and catalog bounds.
The AZUR 3G30 case uses 28 C, AM0 1367 W/m2 and 1e15 1 MeV electrons/cm2.
Load cases, rail voltage bounds, installation and losses are explicit assumptions.
This example establishes no transient protection or mission compliance claim.
"""

import csv
from pathlib import Path

from framework.models import Component, ComponentMode, CotsProtection, CubeSatBus, Mission, Property, TransferMethod

CATALOG = Path(__file__).resolve().parents[1] / "cots"
SOLAR = "azur_space_81441"
SOLAR_CASE = "solar_eol_am0_e1mev_f1e15cm2_anneal_unspecified_t301p15_g1367"
PROTECTOR = "ti_tps259531dsgr"


def build_mission(use_pv_curve=False):
    with (CATALOG / "parameters.tsv").open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    def fact(product, parameter, condition, kind):
        matches = [row for row in rows if row["product_id"] == product and row["element_id"] == "self"
                   and row["parameter_name"] == parameter and row["condition_id"] == condition
                   and row["value_kind"] == kind]
        if len(matches) != 1:
            raise ValueError(f"Select one catalog fact for {product}.{parameter}.")
        return Property(float(matches[0]["value"]), matches[0]["unit"])

    class Tps259531(CotsProtection):
        undervoltage_threshold = fact(PROTECTOR, "undervoltage_threshold", "", "maximum")
        overvoltage_threshold = fact(PROTECTOR, "overvoltage_threshold", "", "minimum")
        current_limit = fact(PROTECTOR, "current_limit", "protection_tps2595_ilim_r1780_full", "minimum")

    mission = Mission()
    bus = mission.add(CubeSatBus("BUS", units=3))
    panel = bus.EPS.SolarArray
    panel.power_path = "self.parent.RegulatorAndConverter"
    bus.EPS.RegulatorAndConverter.transfer_method = TransferMethod.MPPT  # Ideal MPP reference.
    panel.series_count, panel.parallel_count = 6, 2
    panel.cell_active_area = fact(SOLAR, "active_area", "", "nominal")
    for native, catalog in (
        ("cell_eol_voltage", "voltage_at_maximum_power"),
        ("cell_eol_current", "current_at_maximum_power"),
        ("cell_open_circuit_voltage", "open_circuit_voltage"),
        ("cell_short_circuit_current", "short_circuit_current"),
        ("eol_efficiency", "efficiency"),
    ):
        setattr(panel, native, fact(SOLAR, catalog, SOLAR_CASE, "typical"))
    if use_pv_curve:
        with (CATALOG / "curves.tsv").open(newline="") as stream:
            selected = [row for row in csv.DictReader(stream, delimiter="\t")
                        if row["product_id"] == SOLAR and row["element_id"] == "self"
                        and row["curve_id"] == "solar_curve_81441_1e15"
                        and row["condition_id"] == SOLAR_CASE
                        and row["independent_parameter"] == "voltage" and row["independent_unit"] == "V"
                        and row["dependent_parameter"] == "current" and row["dependent_unit"] == "A"]
        if not selected:
            raise ValueError("The selected catalog PV characteristic is unavailable.")
        panel.cell_iv_curve = repr(tuple((float(row["independent_value"]), float(row["dependent_value"]))
                                         for row in selected))
        panel.pv_reference_irradiance = 1367
    panel.irradiance = 1367
    panel.inherent_retention, panel.assembly_efficiency = 1, 1
    panel.sunlight_projection = 1  # Supplied normal-incidence case, separate from an orbit average.

    instrument = bus.Payload.add(Component("instrument"))
    for name, current in (("idle", 0.4), ("active", 1.0)):
        state = instrument.add(ComponentMode(name)).on
        state.voltage, state.current = 5, current
    protector = bus.EPS.PowerCircuit.add(Tps259531("efuse"))
    requirement = protector.no_trip
    requirement.voltages = "(4.75, 5.0, 5.25)"
    requirement.define("powers", Property(
        "(self.context.spacecraft.Payload.instrument.idle.on.power.value, "
        "self.context.spacecraft.Payload.instrument.active.on.power.value)", "W"))
    for bound in ("minimum", "maximum"):
        requirement.define(f"{bound}_voltage", Property(f"sizing.extrema(values=self.voltages).{bound}", "V"))
    requirement.currents = (
        "tuple(sizing.load_current_extrema(powers=self.powers, "
        "minimum_voltage=self.minimum_voltage, maximum_voltage=self.maximum_voltage))")
    return mission


def main():
    for use_pv_curve in (False, True):
        mission = build_mission(use_pv_curve)
        panel = mission.BUS.EPS.SolarArray
        print("PV input:", "catalog I-V points" if use_pv_curve else "scalar ratings")
        print(f"Array reference MPP power: {panel.eol_power:.6f}")
        print(f"Array operating voltage: {panel.operating_voltage:.6f}")
        print(f"Array operating power: {panel.operating_power:.6f}")
        print(f"Available source power: {panel.available_power:.6f}")
        requirement = mission.BUS.EPS.PowerCircuit.efuse.no_trip
        for result in requirement.verify().results:
            print(result.condition.name, result.measure, result.target, result.value)
        mission.BUS.Payload.instrument.active.on.current = 1.2
        print("No-trip verdict after raising the load:", requirement.verify().verified)


if __name__ == "__main__":
    main()
