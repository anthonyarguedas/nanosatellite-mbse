"""Synthetic preliminary EPS sizing. Importing constructs configuration only."""

from framework.models import CubeSatBus, Mission

mission = Mission(lifetime=2, days_per_year=365.25)
orbit = mission.orbit
orbit.altitude = 600
orbit.eccentricity = 0.05
orbit.beta_angle = 0
orbit.sun_projection_angle = 30

bus = mission.add(CubeSatBus("BUS", units=1))
eps = bus.EPS
for component in eps.components:
    component.mass = 0.1
    component.volume = 0.0001

# These are period-average loads, including duties at the chosen load boundary.
mission.BUS_EPS_sunlight_energy.average_power = 5
mission.BUS_EPS_eclipse_energy.average_power = 3
# Synthetic delivered-energy allocations, supplied separately from demand.
eps.available_sunlight_energy = 25000
eps.available_eclipse_energy = 8000

panel = eps.SolarArray
panel.sunlight_path_efficiency = 0.8
panel.eclipse_path_efficiency = 0.65
panel.cell_eol_voltage = 2.3
panel.cell_eol_current = 0.45
panel.cell_count = 24

battery = eps.Battery
battery.nominal_voltage = 3.7
battery.rated_capacity = 5.5
battery.rated_energy = 20.35
battery.cycle_coefficient = 2000
battery.cycle_exponent = -1
battery.fit_dod_min = 0.1
battery.fit_dod_max = 0.8
battery.degradation_margin = 0.2
battery.energy_retention = 0.8
battery.capacity_retention = 0.8

if __name__ == "__main__":
    print("Orbit:", f"{orbit.period:.2f}")
    print("Sunlight:", f"{orbit.sunlight_duration:.2f}")
    print("Eclipse:", f"{orbit.eclipse_duration:.2f}")
    for requirement in mission.requirements:
        print(requirement.render_statement(), requirement.verified)
    print("Fractional cell estimate:", mission.BUS_EPS_solar_cell_count.fractional_count.value)
    print("Maximum DoD:", mission.BUS_EPS_battery_energy.maximum_dod.value)
    print("Battery EOL energy:", f"{battery.eol_energy:.2f}")
    print("Battery EOL capacity:", f"{battery.eol_capacity:.2f}")
