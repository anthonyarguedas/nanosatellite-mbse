"""Compare DET with ideal MPP extraction under one sourced PV condition.

Run: python3 -m framework.sessions.example_eps_transfer
AZUR 3G30: 28 C, AM0 1367 W/m2, 1e15 1 MeV electrons/cm2, 6S2P.
Linear interpolation between catalog anchors is explicitly accepted here.
Bus voltages, 0.2 V DET drop, 94% conversion and 12 W demand are assumptions.
This case establishes no actual tracker performance or chronological energy claim.
"""

from framework.models import Property, TransferMethod, VerificationCondition
from .example_eps_operating_limits import build_mission as build_source


def build_mission(transfer_method, bus_voltage):
    mission = build_source(use_pv_curve=True)
    eps = mission.BUS.EPS
    panel = eps.SolarArray
    direct, converter = eps.PowerCircuit, eps.RegulatorAndConverter
    direct.transfer_method = TransferMethod.DET
    direct.bus_voltage = bus_voltage
    direct.voltage_drop = 0.2
    converter.transfer_method = TransferMethod.MPPT
    converter.efficiency = 0.94
    if transfer_method == TransferMethod.DET:
        panel.power_path = "self.parent.PowerCircuit"
    elif transfer_method == TransferMethod.MPPT:
        panel.power_path = "self.parent.RegulatorAndConverter"
    else:
        raise ValueError("This comparison selects DET or MPPT.")
    panel.iv_interpolation = "'linear'"
    panel.define("delivered_power", Property(
        "self.power_path.value.bus_voltage.value * self.operating_current.value "
        "if self.power_path.value.selected_transfer_method.value == 'DET' else "
        "self.power_path.value.efficiency.value * self.operating_power.value", "W"))
    # Illustrative receiving limits, separate from the sourced PV data.
    eps.solar_voltage.minimum_allowed = 6
    eps.solar_voltage.maximum_allowed = 14
    eps.solar_open_circuit_voltage.required = 20
    eps.solar_short_circuit_current.required = 1.1
    eps.add_requirement(
        "transfer_delivery",
        statement="The selected solar path shall supply at least {minimum.target} in this case.",
        rationale="Sourced reference PV characteristic with explicitly assumed path losses and bus voltage.",
        conditions=(VerificationCondition(
            "minimum", panel.delivered_power, Property(12, "W"),
            "math.isfinite(measure) and measure >= target",
        ),),
    )
    return mission


def main():
    print("Assumptions: DET drop 0.2 V, MPPT converter efficiency 0.94, demand 12 W.")
    print("method bus_V array_V current_A array_W delivered_W voltage_ok delivery_ok")
    for bus_voltage in (12, 13):
        for method in (TransferMethod.DET, TransferMethod.MPPT):
            mission = build_mission(method, bus_voltage)
            eps = mission.BUS.EPS
            panel = eps.SolarArray
            print(method.value, bus_voltage,
                  f"{panel.operating_voltage.value:.6f}", f"{panel.operating_current.value:.6f}",
                  f"{panel.operating_power.value:.6f}", f"{panel.delivered_power.value:.6f}",
                  eps.solar_voltage.verify().verified, eps.transfer_delivery.verify().verified)


if __name__ == "__main__":
    main()
