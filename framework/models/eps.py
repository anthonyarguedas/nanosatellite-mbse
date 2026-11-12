"""EPS component types and fixed COTS specialisations."""

from .elements import Component, Subsystem
from .properties import Property
from .requirements import VerificationCondition


class EPS(Subsystem):
    power = Property("sum(child.power.value for child in self.power_consumers)", "W")
    available_sunlight_energy = Property(unit="J")
    available_eclipse_energy = Property(unit="J")

    def _sizing_requirement(self, name, available, required, unit, basis, statement, *, integer=False, **inputs):
        measure = "self.parent.available" if integer else "0 if self.parent.required.value == 0 else self.parent.available"
        condition = "math.isfinite(measure) and 0 <= target <= measure"
        if integer:
            condition += " and type(measure) is int"
        return self.add_requirement(
            name,
            statement=statement,
            rationale=f"final_report/design-proposal.tex#eq:{basis}. Preliminary sizing at the declared accounting boundary.",
            available=available, required=Property(required, unit),
            conditions=(VerificationCondition("minimum", Property(measure, unit), Property("self.parent.required", unit), condition),),
            **inputs,
        )

    def create_requirements(self):
        energies = {}
        for phase in ("sunlight", "eclipse"):
            energies[phase] = self._sizing_requirement(
                f"{phase}_energy", getattr(self, f"available_{phase}_energy"),
                "0 if self.duration.value == 0 else sizing.load_energy(average_power=self.average_power, duration=self.duration).joules",
                "J", f"{phase}-load-energy",
                f"The EPS shall deliver at least {{minimum.target}} during {phase} per orbit.",
                average_power=Property(unit="W"),
                duration=Property(f"self.mission.orbit.{phase}_duration", "s"),
            )
        solar_power = self._sizing_requirement(
            "solar_power", self.SolarArray.eol_power,
            "sizing.minimum_panel_power(sunlight_energy=self.sunlight_energy, "
            "eclipse_energy=self.eclipse_energy, sunlight_efficiency=self.effective_sunlight_efficiency, "
            "eclipse_efficiency=self.effective_eclipse_efficiency, sunlight_duration=self.mission.orbit.sunlight_duration).watts",
            "W", "minimum-panel-power",
            "The solar array shall provide at least {minimum.target} at end of life.",
            sunlight_energy=energies["sunlight"].required,
            eclipse_energy=energies["eclipse"].required,
            effective_sunlight_efficiency=Property(
                "1 if self.sunlight_energy.value == 0 else self.context.SolarArray.sunlight_path_efficiency", "1"),
            effective_eclipse_efficiency=Property(
                "1 if self.eclipse_energy.value == 0 else self.context.SolarArray.eclipse_path_efficiency", "1"),
        )
        self._sizing_requirement(
            "solar_cell_count", self.SolarArray.cell_count,
            "0 if self.required_power.value == 0 else sizing.cell_count(required_power=self.required_power, eol_cell_power=self.cell_power).required",
            "cell", "solar-cell-count",
            "The solar array shall contain at least {minimum.target.value:d} cells.", integer=True,
            required_power=solar_power.required,
            cell_power=self.SolarArray.cell_eol_power,
            fractional_count=Property(
                "0 if self.required_power.value == 0 else sizing.cell_count(required_power=self.required_power, eol_cell_power=self.cell_power).fractional", "cell"),
        )
        self._sizing_requirement(
            "battery_energy", self.Battery.bol_energy,
            "0 if self.eclipse_energy.value == 0 else "
            "sizing.battery_energy(eclipse_energy=self.eclipse_energy, "
            "depth_of_discharge=self.maximum_dod, degradation_margin=self.degradation_margin).joules",
            "J", "battery-energy",
            "The battery shall have at least {minimum.target} of beginning-of-life energy.",
            eclipse_energy=energies["eclipse"].required,
            required_cycles=Property(
                "sizing.mission_cycles(lifetime=self.mission.lifetime, days_per_year=self.mission.days_per_year, "
                "orbits_per_day=self.mission.orbit.orbits_per_day).cycles", "cycle"),
            maximum_dod=Property(
                "sizing.depth_of_discharge(required_cycles=self.required_cycles, cycle_coefficient=self.cycle_coefficient, "
                "cycle_exponent=self.cycle_exponent, fit_dod_min=self.fit_dod_min, fit_dod_max=self.fit_dod_max).fraction", "1"),
            cycle_coefficient=self.Battery.cycle_coefficient,
            cycle_exponent=self.Battery.cycle_exponent,
            fit_dod_min=self.Battery.fit_dod_min,
            fit_dod_max=self.Battery.fit_dod_max,
            degradation_margin=self.Battery.degradation_margin,
        )

    @property
    def power_consumers(self):
        # Storage and generation are excluded from this default demand boundary.
        # A specialised EPS can choose a different boundary, including losses.
        return tuple(child for child in self.components if not isinstance(child, (Battery, SolarArray)))


class EPSComponent(Component):
    subsystem_type = EPS


class Battery(EPSComponent):
    rated_capacity = Property(unit="Ah")
    rated_energy = Property(unit="Wh")
    nominal_voltage = Property(unit="V")
    cycle_coefficient = Property(unit="cycle")
    cycle_exponent = Property(unit="1")
    fit_dod_min = Property(unit="1")
    fit_dod_max = Property(unit="1")
    degradation_margin = Property(unit="1")
    energy_retention = Property(unit="1")
    capacity_retention = Property(unit="1")
    bol_energy = Property("self.rated_energy.value * 3600", "J")
    eol_energy = Property("sizing.retained_value(initial=self.bol_energy, retention=self.energy_retention).retained", "J")
    eol_capacity = Property("sizing.retained_value(initial=self.rated_capacity, retention=self.capacity_retention).retained", "Ah")


class SolarArray(EPSComponent):
    maximum_power = Property(unit="W")
    active_area = Property(unit="m2")
    open_circuit_voltage = Property(unit="V")
    short_circuit_current = Property(unit="A")
    sunlight_path_efficiency = Property(unit="1")
    eclipse_path_efficiency = Property(unit="1")
    cell_eol_voltage = Property(unit="V")
    cell_eol_current = Property(unit="A")
    cell_count = Property(unit="cell")
    cell_eol_power = Property("sizing.cell_power(eol_voltage=self.cell_eol_voltage, eol_current=self.cell_eol_current).watts", "W")
    eol_power = Property("self.cell_count.value * self.cell_eol_power.value", "W")


class RegulatorAndConverter(EPSComponent):
    input_voltage = Property(unit="V")
    output_voltage = Property(unit="V")
    maximum_output_current = Property(unit="A")
    efficiency = Property(unit="1")


class PowerCircuit(EPSComponent):
    maximum_voltage = Property(unit="V")
    maximum_current = Property(unit="A")


class COTS(EPSComponent):
    """Product classes fix their inherited Property definitions."""

    fixed_properties = True


class CotsBattery(Battery, COTS):
    pass


class CotsSolarArray(SolarArray, COTS):
    pass


class CotsRegulatorAndConverter(RegulatorAndConverter, COTS):
    pass


class CotsPowerCircuit(PowerCircuit, COTS):
    pass


EPS.default_components = (Battery, SolarArray, RegulatorAndConverter, PowerCircuit)
