"""Synthetic, executable evidence for the two model appendices.

All numerical values are illustrative allocations, not a qualified EPS design.
The GUI capture generator edits only a temporary copy of this session.
"""

from framework.models import (
    ComponentMode, CubeSatBus, Mission, ModeAllocation, Property,
    Protection, Requirement, SpacecraftMode, StateAllocation,
    VerificationCondition,
)

# excerpt: construction
mission = Mission(lifetime=1, days_per_year=365.25)
mission.orbit.altitude = 600
mission.orbit.eccentricity = 0
mission.orbit.beta_angle = 0
bus = mission.add(CubeSatBus("BUS", units=1))
eps = bus.EPS
battery = eps.Battery
converter = eps.RegulatorAndConverter
# end: construction

# excerpt: modes
nominal = bus.add(SpacecraftMode("nominal"))
nominal.allocation.fraction = 1
active = converter.add(ComponentMode("active"))
active.add(ModeAllocation(
    "nominal_share", nominal, 1,
))
active.on.voltage = 3.3
active.on.current = 0.1
active.off.voltage = 0
active.off.current = 0
active.add(StateAllocation(
    "on_share", active.on, 1,
))
converter.power.bind(
    nominal, "self.active.on.power.value",
)
# end: modes

# excerpt: interfaces
battery.series_count = 1
battery.cell_nominal_voltage = 3.7
converter.input_voltage = battery.nominal_voltage
converter.output_voltage = active.on.voltage
eps.bus_voltage.available = converter.output_voltage
eps.bus_voltage.required = active.on.voltage
# end: interfaces

# excerpt: automatic
protector = eps.add(Protection("protector"))
protector.undervoltage_threshold = 2.5
protector.overvoltage_threshold = 5.5
protector.current_limit = 1.0
protector.no_trip.voltages = "(3.3, 3.7)"
protector.no_trip.currents = "(0.0, 0.1)"
assert protector.no_trip.verify().verified is True
# end: automatic

# excerpt: requirements
voltage = converter.add(Requirement(
    "output_match",
    statement="The output shall equal {match.target}.",
    rationale="Illustrative nominal load rail.",
))
voltage.add(VerificationCondition(
    "match", converter.output_voltage, active.on.voltage,
    "measure == target",
))
voltage.statement = "The load rail shall equal {match.target}."
voltage.rationale = "Nominal mode uses the 3.3 V load rail."
assert voltage.verify(mode=nominal).verified is True
# end: requirements

# excerpt: scripts
mission.add_import("import framework.scripts.sizing as calc")
voltage.define("load_power", active.on.power)
voltage.define("duration", Property(100, "s"))
voltage.define("energy", Property(
    "calc.load_energy(average_power=self.load_power, "
    "duration=self.duration).joules", "J",
))
energy_j = voltage.energy.value
report = mission.verify(mode=nominal)
# end: scripts


def exercise_requirement_changes():
    """Exercise removal without changing the illustrated configuration."""
    # excerpt: removal
    removed = converter.remove(voltage)
    assert removed is voltage and voltage.parent is None
    converter.add(removed)
    # end: removal


if __name__ == "__main__":
    exercise_requirement_changes()
    print(voltage.render_statement(mode=nominal))
    print("Linked analysis:", energy_j, "J")
    print("Protection verified:", protector.no_trip.verify().verified)
    print("Mission verified:", report.verified)
