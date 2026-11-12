"""An ordinary synthetic session using the public model API."""

from framework.models import (
    CotsBattery, CubeSatBus, Mission, Property, Requirement, VerificationCondition,
)


class ExamplePack(CotsBattery):
    mass = Property("0.2", "kg")
    rated_energy = Property("12", "Wh")


mission = Mission(imports=("import framework.models as models",))
bus = mission.add(CubeSatBus("BUS"))
eps = bus.EPS
battery = eps.Battery
battery.add(ExamplePack("pack"))
battery.mass.expression = "sum(c.mass.value for c in self.cots if isinstance(c, models.Battery))"
eps.SolarArray.mass = 0.03
eps.RegulatorAndConverter.mass = 0.02
eps.PowerCircuit.mass = 0.01

requirement = mission.add(Requirement("mass_limit", text="Synthetic bus mass criterion."))
requirement.define("maximum_mass", Property("0.25", "kg"))
requirement.add(VerificationCondition(
    "maximum", bus.mass, requirement.maximum_mass, "measure <= target",
))

if __name__ == "__main__":
    report = mission.verify()
    print("Bus mass:", bus.mass.value, bus.mass.unit)
    print("Criterion:", report.results[0].status.value, report.results[0].value)
    for failure in report.for_instance(battery).failures:
        print(failure.explain())
