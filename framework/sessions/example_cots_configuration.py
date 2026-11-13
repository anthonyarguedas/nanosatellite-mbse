"""Report equations evaluated with reviewed COTS reference ratings.

Run: python3 -m framework.sessions.example_cots_configuration

The solar case is XTE+ LEO at 28 C, AM0 1353 W/m2, after 3e13
1 MeV electrons/cm2 under the stated AIAA procedure. M35A uses its
published minimum energy/capacity and separate reference voltage/current ratings.
Mission budgets, pointing, packing, counts and DoD are engineering assumptions.
A deployed coplanar panel follows an ideal prescribed Sun pointing law.
The script calculates its illumination average over one complete orbit.
This reference assessment establishes no converter or lifetime qualification.
"""

import csv
from pathlib import Path

from framework.models import (
    Component, ComponentMode, CotsBattery, CotsRegulatorAndConverter,
    CotsSolarArray, CubeSatBus, Face, Mission, Pointing, Property,
    VerificationCondition,
)

SOLAR = "spectrolab_xte_plus_leo_27cm2"
SOLAR_CASE = "solar_eol_am0_e1mev_f3e13cm2_aiaa_s111_2005_t301p15_g1353"
BATTERY = "molicel_inr_18650_m35a"
CHARGER = "ti_bq24650rvar"
CONVERTER = "ti_tps62130argtr"


def build_mission():
    path = Path(__file__).resolve().parents[1] / "cots" / "model-inputs.tsv"
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    def fact(product, name, condition, kind):
        matches = [row for row in rows if row["product_id"] == product
                   and row["model_property"] == name and row["condition_id"] == condition
                   and row["value_kind"] == kind and row["value"]]
        if len(matches) != 1:
            raise ValueError(f"Choose one catalog fact for {product}.{name}: {len(matches)} matches")
        row = matches[0]
        value = repr(row["value"]) if name == "transfer_method" else float(row["value"])
        return Property(value, row["unit"])

    class XteLeoReference(CotsSolarArray):
        # Each assigned COTS item is one physical cell.
        series_count = Property(1, "cell")
        parallel_count = Property(1, "string")
        cell_active_area = fact(SOLAR, "cell_active_area", "", "nominal")
        cell_eol_voltage = fact(SOLAR, "cell_eol_voltage", SOLAR_CASE, "derived")
        cell_eol_current = fact(SOLAR, "cell_eol_current", SOLAR_CASE, "derived")
        cell_open_circuit_voltage = fact(SOLAR, "cell_open_circuit_voltage", SOLAR_CASE, "derived")
        cell_short_circuit_current = fact(SOLAR, "cell_short_circuit_current", SOLAR_CASE, "derived")
        eol_efficiency = fact(SOLAR, "eol_efficiency", SOLAR_CASE, "derived")

    class MolicelM35A(CotsBattery):
        series_count = Property(1, "cell")
        parallel_count = Property(1, "string")
        rated_capacity = fact(BATTERY, "rated_capacity", "", "minimum")
        rated_energy = fact(BATTERY, "rated_energy", "", "minimum")
        nominal_voltage = fact(BATTERY, "nominal_voltage", "", "nominal")
        minimum_voltage = fact(BATTERY, "minimum_voltage", "", "nominal")
        maximum_voltage = fact(BATTERY, "maximum_voltage", "", "nominal")
        maximum_charge_current = fact(BATTERY, "maximum_charge_current", "", "maximum")
        maximum_discharge_current = fact(BATTERY, "maximum_discharge_current", "", "maximum")

    class Bq24650(CotsRegulatorAndConverter):
        # Explicitly select the reviewed fixed-input capability for this case.
        transfer_method = fact(CHARGER, "transfer_method", "", "declared")
        minimum_input_voltage = fact(CHARGER, "minimum_input_voltage", "", "minimum")
        maximum_input_voltage = fact(CHARGER, "maximum_input_voltage", "", "maximum")
        absolute_maximum_input_voltage = fact(
            CHARGER, "absolute_maximum_input_voltage", "cfgintegrated_bq24650_abs_vcc", "absolute_maximum")

    class Tps62130A(CotsRegulatorAndConverter):
        minimum_input_voltage = fact(CONVERTER, "minimum_input_voltage", "", "minimum")
        maximum_input_voltage = fact(CONVERTER, "maximum_input_voltage", "", "maximum")
        minimum_output_setting = fact(CONVERTER, "output_voltage", "", "minimum")
        maximum_output_setting = fact(CONVERTER, "output_voltage", "", "maximum")
        # A complete converter's delivered current needs its external circuit.

    mission = Mission(lifetime=2, days_per_year=365.25)
    mission.orbit.altitude = 600
    mission.orbit.eccentricity = 0
    mission.orbit.beta_angle = 0
    bus = mission.add(CubeSatBus("BUS", units=3))
    attitude = bus.AttitudeDeterminationAndControl
    attitude.pointing = Pointing.SUN_POINTING
    attitude.pointing_face = Face.POS_Y
    eps = bus.EPS
    panel, battery, converter = eps.SolarArray, eps.Battery, eps.RegulatorAndConverter

    for index in range(12):
        panel.add(XteLeoReference(f"cell{index + 1}"))
    for index in range(2):
        battery.add(MolicelM35A(f"cell{index + 1}"))
    charger = converter.add(Bq24650("charger"))
    load_converter = converter.add(Tps62130A("load_converter"))
    panel.power_path = "self.parent.RegulatorAndConverter"
    converter.transfer_method = charger.transfer_method
    # Engineer-selected fixed input setting at this case's MPP, without tracking.
    converter.input_voltage_setpoint = panel.eol_voltage

    # User-authored arrangement and installed-count expressions. No search.
    panel.series_count, panel.parallel_count = 6, 2
    battery.series_count, battery.parallel_count = 2, 1
    for assembly in (panel, battery):
        assembly.cell_count = "sum(cell.cell_count.value for cell in self.cots)"
    for name in ("cell_active_area", "cell_eol_voltage", "cell_eol_current",
                 "cell_open_circuit_voltage", "cell_short_circuit_current", "eol_efficiency"):
        setattr(panel, name, getattr(panel.cell1, name))
    for name, source in (
        ("cell_rated_capacity", "rated_capacity"), ("cell_rated_energy", "rated_energy"),
        ("cell_nominal_voltage", "nominal_voltage"), ("cell_minimum_voltage", "minimum_voltage"),
        ("cell_maximum_voltage", "maximum_voltage"),
        ("cell_maximum_charge_current", "maximum_charge_current"),
        ("cell_maximum_discharge_current", "maximum_discharge_current"),
    ):
        setattr(battery, name, getattr(battery.cell1, source))

    # The deployed section's normal aligns with body +Y. Its area extends
    # beyond one nominal 3U body face. Deployment and shading are not modeled.
    panel.mounting_face = Face.POS_Y
    # Constant source conditions. EOL cell data already include their losses.
    panel.irradiance = 1353
    panel.inherent_retention = 1
    panel.assembly_efficiency = 1
    panel.packing_fraction = 0.9
    panel.usable_area = 0.05
    panel.sunlight_path_efficiency = 0.8
    panel.eclipse_path_efficiency = 0.65
    battery.degradation_margin = 0.2
    eps.battery_energy.maximum_dod = 0.2  # Engineer allocation, no invented cycle-law fit.

    load = bus.Payload.add(Component("instrument"))
    active = load.add(ComponentMode("active"))
    active.on.voltage, active.on.current = 3.3, 1
    active.off.voltage, active.off.current = 0, 0
    # This toy load is continuously on. There is no inferred schedule/averaging.
    eps.sunlight_energy.average_power = active.on.power
    eps.eclipse_energy.average_power = active.on.power
    converter.output_voltage = 3.3  # Selected adjustable output setting.
    eps.bus_voltage.available = converter.output_voltage
    eps.bus_voltage.required = active.on.voltage
    eps.bus_current.required = active.on.current
    eps.solar_voltage.minimum_allowed = charger.minimum_input_voltage
    eps.solar_voltage.maximum_allowed = charger.maximum_input_voltage
    eps.solar_open_circuit_voltage.required = charger.absolute_maximum_input_voltage
    eps.battery_voltage.minimum_allowed = load_converter.minimum_input_voltage
    eps.battery_voltage.maximum_allowed = load_converter.maximum_input_voltage
    # Declared battery-terminal current bounds for this illustrative case.
    eps.battery_charge_current.required = 1
    eps.battery_discharge_current.required = 1
    eps.add_requirement(
        "load_voltage_setting", minimum=load_converter.minimum_output_setting,
        maximum=load_converter.maximum_output_setting,
        statement="The selected load voltage shall remain within the supported output settings.",
        conditions=(VerificationCondition(
            "supported", converter.output_voltage,
            Property("(self.parent.minimum.value, self.parent.maximum.value)", "V"),
            "math.isfinite(measure) and target[0] <= measure <= target[1]",
        ),),
    )
    # Keep delivered-energy evidence, permissible source current, delivered
    # converter current and battery retention unset. They were not established.
    return mission


def main():
    mission = build_mission()
    eps = mission.BUS.EPS
    panel, battery = eps.SolarArray, eps.Battery
    for label, prop in (
        ("Sunlight duration", mission.orbit.sunlight_duration),
        ("Eclipse duration", mission.orbit.eclipse_duration),
        ("Required solar power", eps.solar_power.required),
        ("Installed MPP power", panel.eol_power),
        ("Mean sunlight projection", panel.sunlight_projection),
        ("Mean available sunlight source power", panel.available_power),
        ("Source energy per orbit", panel.source_energy),
        ("Array reference MPP voltage", panel.eol_voltage),
        ("Array operating voltage", panel.operating_voltage),
        ("Array operating current", panel.operating_current),
        ("Array operating power", panel.operating_power),
        ("Required active area", eps.solar_area.required),
        ("Installed active area", panel.active_area),
        ("Installed deployed panel area", panel.panel_area),
        ("Nominal body face area (comparison)", panel.body_face_area),
        ("Battery nominal voltage", battery.nominal_voltage),
        ("Battery charge capacity", battery.rated_capacity),
        ("Battery rated energy", battery.rated_energy),
    ):
        print(f"{label}: {prop:.6f}")
    print(f"Required battery energy: {eps.battery_energy.required.value / 3600:.6f} Wh")
    print("Required solar cells:", eps.solar_cell_count.required.value)
    print("Minimum parallel strings at 6S:", eps.solar_cell_count.minimum_parallel_count.value)
    print("Minimum battery parallel strings at 2S:", eps.battery_energy.minimum_parallel_count.value)
    print("Tumbling alternative panel area (unused):", f"{eps.solar_area.tumbling_panel_area:.6f}")
    # MPP-product and efficiency-based power retain the source's independent rounding.
    for requirement in eps.requirements:
        result = requirement.verify()
        print(f"{requirement.name}: {result.verified} ({result.status.value})")
    print("Full mission verdict:", mission.verify().verified)
    for name, prop in (("Battery EOL energy", battery.eol_energy),
                       ("Battery cycle-law coefficient", battery.cycle_coefficient)):
        print(f"{name}: {prop.assess().status.value}")
    print("None means unresolved. This example does not establish delivered energy, converter capacity, or battery lifetime.")


if __name__ == "__main__":
    main()
