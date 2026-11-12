"""Synthetic EPS sizing and configuration checks. Importing constructs configuration only."""

from framework.models import Component, ComponentMode, CubeSatBus, Face, Mission, Pointing

mission = Mission(lifetime=2, days_per_year=365.25)
orbit = mission.orbit
orbit.altitude = 600
orbit.eccentricity = 0.05
orbit.beta_angle = 0
orbit.sun_projection_angle = 30

bus = mission.add(CubeSatBus("BUS", units=1))
attitude = bus.AttitudeDeterminationAndControl
attitude.pointing = Pointing.SUN_POINTING
attitude.pointing_face = Face.POS_Z
eps = bus.EPS
for component in eps.components:
    component.mass = 0.1
    component.volume = 0.0001

# These are period-average loads, including duties at the chosen load boundary.
eps.sunlight_energy.average_power = 5
eps.eclipse_energy.average_power = 3
# Synthetic delivered-energy allocations, supplied separately from demand.
eps.available_sunlight_energy = 25000
eps.available_eclipse_energy = 8000

panel = eps.SolarArray
panel.sunlight_path_efficiency = 0.8
panel.eclipse_path_efficiency = 0.65
panel.cell_eol_voltage = 2.3
panel.cell_eol_current = 0.45
panel.series_count = 6
panel.parallel_count = 4
panel.cell_active_area = 0.00345
panel.packing_fraction = 0.9
panel.usable_area = 0.1  # Assumed deployed area, larger than the 1U body face.
panel.cell_open_circuit_voltage = 2.6
panel.cell_short_circuit_current = 0.5
panel.bol_efficiency = 0.32
panel.lifetime_retention = 0.9375
panel.temperature_factor = 1
panel.irradiance = 1000
panel.inherent_retention = 1
panel.assembly_efficiency = 1
panel.mounting_face = Face.POS_Z

battery = eps.Battery
battery.series_count = 1
battery.parallel_count = 2
battery.cell_nominal_voltage = 3.7
battery.cell_rated_capacity = 2.75
battery.cell_rated_energy = 10.175
battery.cell_minimum_voltage = 3.0
battery.cell_maximum_voltage = 4.2
battery.cell_maximum_charge_current = 1
battery.cell_maximum_discharge_current = 3
battery.cycle_coefficient = 2000
battery.cycle_exponent = -1
battery.fit_dod_min = 0.1
battery.fit_dod_max = 0.8
battery.degradation_margin = 0.2
battery.energy_retention = 0.8
battery.capacity_retention = 0.8

converter = eps.RegulatorAndConverter
converter.minimum_input_voltage = 6
converter.maximum_input_voltage = 18
converter.absolute_maximum_input_voltage = 22
converter.maximum_input_current = 2.5
converter.output_voltage = 5
converter.maximum_output_current = 3
# These bindings declare which limits apply to each source path.
eps.solar_voltage.minimum_allowed = converter.minimum_input_voltage
eps.solar_voltage.maximum_allowed = converter.maximum_input_voltage
eps.solar_open_circuit_voltage.required = converter.absolute_maximum_input_voltage
eps.solar_short_circuit_current.required = converter.maximum_input_current
eps.battery_voltage.minimum_allowed = 2.8
eps.battery_voltage.maximum_allowed = 4.3
eps.battery_charge_current.required = 1
eps.battery_discharge_current.required = 2

load = bus.Payload.add(Component("instrument", mass=0.01, volume=0.00001))
active = load.add(ComponentMode("active"))
active.on.voltage, active.on.current = 5, 1
active.off.voltage, active.off.current = 0, 0
# One declared load rail. Currents at other voltages need a separate path calculation.
eps.bus_voltage.available = converter.output_voltage
eps.bus_voltage.required = active.on.voltage
eps.bus_current.available = converter.maximum_output_current
eps.bus_current.required = active.on.current

if __name__ == "__main__":
    print("Orbit:", f"{orbit.period:.2f}")
    print("Sunlight:", f"{orbit.sunlight_duration:.2f}")
    print("Eclipse:", f"{orbit.eclipse_duration:.2f}")
    for owner in mission.walk():
        for requirement in owner.requirements:
            print(requirement.render_statement(), requirement.verified)
    print("Fractional cell estimate:", eps.solar_cell_count.fractional_count.value)
    print("Maximum DoD:", eps.battery_energy.maximum_dod.value)
    print("Minimum array parallel strings:", eps.solar_cell_count.minimum_parallel_count.value)
    print("Minimum battery parallel strings:", eps.battery_energy.minimum_parallel_count.value)
    print("Installed panel area:", f"{panel.panel_area:.4f}")
    print("Required active area:", f"{eps.solar_area.required:.4f}")
    print("Mean sunlight projection:", f"{panel.sunlight_projection:.4f}")
    print("Source energy per orbit:", f"{panel.source_energy:.2f}")
    print("Battery EOL energy:", f"{battery.eol_energy:.2f}")
    print("Battery EOL capacity:", f"{battery.eol_capacity:.2f}")
