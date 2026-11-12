"""An ordinary synthetic session using the public model API."""

from framework.models import (
    CotsBattery, CubeSatBus, Mission, Property,
)


class ExamplePack(CotsBattery):
    mass = Property("0.2", "kg")
    volume = Property("0.0001", "m3")
    rated_energy = Property("12", "Wh")


mission = Mission(imports=("import framework.models as models",))
bus = mission.add(CubeSatBus("BUS", units=1))
eps = bus.EPS
battery = eps.Battery
battery.add(ExamplePack("pack"))
battery.mass.expression = "sum(c.mass.value for c in self.cots if isinstance(c, models.Battery))"
eps.SolarArray.mass = 0.03
eps.RegulatorAndConverter.mass = 0.02
eps.PowerCircuit.mass = 0.01
battery.volume.expression = "sum(c.volume.value for c in self.cots if isinstance(c, models.Battery))"
eps.SolarArray.volume = 0.00015
eps.RegulatorAndConverter.volume = 0.00005
eps.PowerCircuit.volume = 0.00002

requirement = mission.BUS_mass_limit
requirement.maximum_per_u = 0.25
requirement.statement = "The bus mass {maximum.measure:.2f} shall be at most {maximum.target:.2f}."
requirement.rationale = "Synthetic stricter allocation of 0.25 kg/U for this example."

if __name__ == "__main__":
    report = requirement.verify()
    print(requirement.render_statement())
    print("Rationale:", requirement.rationale)
    print("Criterion:", report.results[0].status.value, report.results[0].value)
    for failure in report.for_instance(battery).failures:
        print(failure.explain())
