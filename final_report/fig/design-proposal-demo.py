"""Synthetic battery study used to generate the design proposal figures.

Run the GUI against a temporary copy. All numbers are illustrative allocations.
"""

from framework.models import CubeSatBus, Mission, Property, VerificationCondition

mission = Mission()
mission.orbit.altitude = 600
mission.orbit.eccentricity = 0
mission.orbit.beta_angle = 0
bus = mission.add(CubeSatBus("BUS", units=1))
eps = bus.EPS

# A few known inputs leave other automatically created criteria incomplete.
eps.sunlight_energy.average_power = 5
eps.eclipse_energy.average_power = 3
eps.SolarArray.sunlight_path_efficiency = 0.8
eps.SolarArray.eclipse_path_efficiency = 0.65
eps.SolarArray.cell_eol_voltage = 2.3
eps.SolarArray.cell_eol_current = 0.45
eps.SolarArray.series_count = 6
eps.SolarArray.parallel_count = 4

battery = eps.Battery
battery.rated_energy = 20.35
requirement = battery.add_requirement(
    "energy_reserve",
    statement="The battery shall provide at least {minimum.target:.0f} of BOL energy "
              "(available: {minimum.measure:.0f}).",
    rationale="Illustrative eclipse energy allocation with an explicit discharge depth and margin.",
    eclipse_energy=Property(6000, "J"),
    depth_of_discharge=Property(0.5, "1"),
    degradation_margin=Property(0.2, "1"),
    required=Property(
        "sizing.battery_energy(eclipse_energy=self.eclipse_energy, "
        "depth_of_discharge=self.depth_of_discharge, "
        "degradation_margin=self.degradation_margin).joules", "J",
    ),
    conditions=(VerificationCondition(
        "minimum", battery.bol_energy,
        Property("self.parent.required", "J"), "measure >= target",
    ),),
)

if __name__ == "__main__":
    print(requirement.render_statement())
    print("Verified:", requirement.verify().verified)
