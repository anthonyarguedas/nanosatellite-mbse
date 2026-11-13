"""EPS component types and fixed COTS specialisations."""

from enum import Enum

from .elements import Component, Subsystem
from .properties import Property
from .requirements import VerificationCondition


class TransferMethod(str, Enum):
    DET = "DET"
    MPPT = "MPPT"
    FIXED_VOLTAGE = "FIXED_VOLTAGE"


class EPS(Subsystem):
    power = Property("sum(child.power.value for child in self.power_consumers)", "W")
    available_sunlight_energy = Property(unit="J")
    available_eclipse_energy = Property(unit="J")

    def _sizing_requirement(self, name, available, required, unit, basis, statement, *, integer=False, maximum=False, **inputs):
        measure = "self.parent.available" if integer or maximum else "0 if self.parent.required.value == 0 else self.parent.available"
        comparison = "0 <= measure <= target" if maximum else "0 <= target <= measure"
        condition = f"math.isfinite(measure) and math.isfinite(target) and {comparison}"
        if integer:
            condition += " and type(measure) is int"
        return self.add_requirement(
            name,
            statement=statement,
            rationale=f"final_report/design-proposal.tex#eq:{basis}. Verification at the declared accounting boundary.",
            available=available, required=required if isinstance(required, Property) else Property(required, unit),
            conditions=(VerificationCondition("maximum" if maximum else "minimum", Property(measure, unit), Property("self.parent.required", unit), condition),),
            **inputs,
        )

    def _voltage_requirement(self, name, minimum, maximum, basis):
        return self.add_requirement(
            name,
            statement="The source voltage shall remain between {self.minimum_allowed} and {self.maximum_allowed}.",
            rationale=f"final_report/design-proposal.tex#eq:{basis}. Receiving limits are explicitly assigned to this path.",
            minimum_voltage=minimum, maximum_voltage=maximum,
            minimum_allowed=Property(unit="V"), maximum_allowed=Property(unit="V"),
            conditions=(VerificationCondition(
                "range", Property("(self.parent.minimum_voltage.value, self.parent.maximum_voltage.value)", "V"),
                Property("(self.parent.minimum_allowed.value, self.parent.maximum_allowed.value)", "V"),
                "all(math.isfinite(v) for v in (*measure, *target)) and 0 <= target[0] <= measure[0] <= measure[1] <= target[1]",
            ),),
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
            series_count=self.SolarArray.series_count,
            minimum_parallel_count=Property(
                "0 if self.required_power.value == 0 else sizing.parallel_strings(required_total=self.required_power, "
                "per_cell=self.cell_power, series_count=self.series_count).required", "string"),
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
            cell_energy=self.Battery.cell_bol_energy,
            series_count=self.Battery.series_count,
            minimum_parallel_count=Property(
                "0 if self.required.value == 0 else sizing.parallel_strings(required_total=self.required, "
                "per_cell=self.cell_energy, series_count=self.series_count).required", "string"),
        )
        for name, component, basis in (
            ("solar_configuration", self.SolarArray, "pv-integer-configuration"),
            ("battery_configuration", self.Battery, "battery-assembly-capacity"),
        ):
            self.add_requirement(
                name,
                statement="The assembly shall contain {total.target.value:d} cells in positive integer series and parallel counts.",
                rationale=f"final_report/design-proposal.tex#eq:{basis}. Counts are supplied by the engineer.",
                series_count=component.series_count, parallel_count=component.parallel_count,
                conditions=(
                    VerificationCondition("series", component.series_count, Property(1, "cell"), "type(measure) is int and measure >= target"),
                    VerificationCondition("parallel", component.parallel_count, Property(1, "string"), "type(measure) is int and measure >= target"),
                    VerificationCondition("total", component.cell_count,
                                          Property("self.parent.series_count.value * self.parent.parallel_count.value", "cell"),
                                          "type(measure) is int and type(target) is int and measure == target"),
                ),
            )

        self._sizing_requirement(
            "solar_area", self.SolarArray.active_area,
            "0 if self.required_power.value == 0 else sizing.minimum_array_area("
            "required_power=self.required_power, power_density=self.context.SolarArray.eol_power_density).square_metres",
            "m2", "array-generation-screen",
            "The array shall have at least {minimum.target} of active area at the assessed conditions.",
            required_power=solar_power.required,
            effective_area=Property(
                "0 if self.required_power.value == 0 else sizing.minimum_array_area(required_power=self.required_power, "
                "power_density=self.context.SolarArray.normal_power_density).square_metres", "m2"),
            tumbling_panel_area=Property(
                "sizing.tumbling_array_area(effective_area=self.effective_area, "
                "packing_fraction=self.context.SolarArray.packing_fraction).square_metres", "m2"),
        )
        self._sizing_requirement(
            "solar_area_fit", self.SolarArray.panel_area, self.SolarArray.usable_area,
            "m2", "array-area-fit", "The installed panel area shall not exceed {maximum.target}.", maximum=True,
        )
        self._sizing_requirement(
            "solar_generation", self.SolarArray.available_power, solar_power.required,
            "W", "array-generation-screen",
            "The array shall provide at least {minimum.target} as mean available power during sunlight.",
        )
        self._voltage_requirement("solar_voltage", self.SolarArray.operating_voltage, self.SolarArray.operating_voltage, "mppt-voltage-compatibility")
        self._voltage_requirement("battery_voltage", self.Battery.minimum_voltage, self.Battery.maximum_voltage, "battery-assembly-ratings")
        for name, available, unit, basis, statement, maximum in (
            ("solar_open_circuit_voltage", self.SolarArray.open_circuit_voltage, "V", "pv-input-ratings",
             "The array open-circuit voltage shall not exceed {maximum.target}.", True),
            ("solar_short_circuit_current", self.SolarArray.short_circuit_current, "A", "pv-input-ratings",
             "The array short-circuit current shall not exceed {maximum.target}.", True),
            ("bus_current", Property(unit="A"), "A", "battery-assembly-ratings",
             "The selected bus path shall supply at least {minimum.target}.", False),
            ("battery_charge_current", self.Battery.maximum_charge_current, "A", "battery-assembly-ratings",
             "The battery shall accept at least {minimum.target} of charging current.", False),
            ("battery_discharge_current", self.Battery.maximum_discharge_current, "A", "battery-assembly-ratings",
             "The battery shall supply at least {minimum.target} of discharge current.", False),
        ):
            self._sizing_requirement(name, available, None, unit, basis, statement, maximum=maximum)
        self.add_requirement(
            "bus_voltage",
            statement="The selected bus path shall provide {match.target} within {self.tolerance}.",
            rationale="The engineer assigns the source and load state on the same rail. This checks their nominal voltage match.",
            available=Property(unit="V"), required=Property(unit="V"), tolerance=Property(0, "V"),
            conditions=(VerificationCondition(
                "match", Property("self.parent.available", "V"), Property("self.parent.required", "V"),
                "all(math.isfinite(v) for v in (measure, target, self.parent.tolerance.value)) "
                "and measure >= 0 and target >= 0 and 0 <= self.parent.tolerance.value "
                "and abs(measure - target) <= self.parent.tolerance.value",
            ),),
        )

    @property
    def power_consumers(self):
        # Storage and generation are excluded from this default demand boundary.
        # A specialised EPS can choose a different boundary, including losses.
        return tuple(child for child in self.components if not isinstance(child, (Battery, SolarArray)))


class EPSComponent(Component):
    subsystem_type = EPS


class SolarPowerPath(EPSComponent):
    """Explicit solar connection, including a converter or a direct path."""

    transfer_method = Property(unit="1")
    selected_transfer_method = Property("sizing.transfer_selection(transfer_method=self.transfer_method).method", "1")
    bus_voltage = Property(unit="V")
    voltage_drop = Property(unit="V")
    input_voltage_setpoint = Property(unit="V")


class Battery(EPSComponent):
    series_count = Property(unit="cell")
    parallel_count = Property(unit="string")
    cell_count = Property("self.series_count.value * self.parallel_count.value", "cell")
    cell_rated_capacity = Property(unit="Ah")
    cell_rated_energy = Property(unit="Wh")
    cell_nominal_voltage = Property(unit="V")
    cell_minimum_voltage = Property(unit="V")
    cell_maximum_voltage = Property(unit="V")
    cell_maximum_charge_current = Property(unit="A")
    cell_maximum_discharge_current = Property(unit="A")
    cell_bol_energy = Property("self.cell_rated_energy.value * 3600", "J")
    rated_capacity = Property("self.parallel_count.value * self.cell_rated_capacity.value", "Ah")
    rated_energy = Property("self.cell_count.value * self.cell_rated_energy.value", "Wh")
    nominal_voltage = Property("self.series_count.value * self.cell_nominal_voltage.value", "V")
    minimum_voltage = Property("self.series_count.value * self.cell_minimum_voltage.value", "V")
    maximum_voltage = Property("self.series_count.value * self.cell_maximum_voltage.value", "V")
    maximum_charge_current = Property("self.parallel_count.value * self.cell_maximum_charge_current.value", "A")
    maximum_discharge_current = Property("self.parallel_count.value * self.cell_maximum_discharge_current.value", "A")
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
    cell_iv_curve = Property("()")
    pv_reference_irradiance = Property(unit="W/m2")
    power_path = Property()
    iv_interpolation = Property("'none'", "1")
    operating_voltage = Property(
        "sizing.solar_operating_voltage(transfer_method=self.power_path.value.selected_transfer_method, "
        "**({'reference_voltage': self.power_path.value.bus_voltage, 'voltage_drop': self.power_path.value.voltage_drop} "
        "if self.power_path.value.selected_transfer_method.value == 'DET' else "
        "{'reference_voltage': self.eol_voltage if self.power_path.value.selected_transfer_method.value == 'MPPT' "
        "else self.power_path.value.input_voltage_setpoint})).volts", "V")
    operating_current = Property(
        "self.eol_current if self.operating_voltage.value == self.eol_voltage.value else "
        "sizing.pv_operating_point(pv_points=self.cell_iv_curve, series_count=self.series_count, "
        "parallel_count=self.parallel_count, operating_voltage=self.operating_voltage, interpolation=self.iv_interpolation).current", "A")
    operating_power = Property("self.operating_voltage.value * self.operating_current.value", "W")
    series_count = Property(unit="cell")
    parallel_count = Property(unit="string")
    cell_count = Property("self.series_count.value * self.parallel_count.value", "cell")
    cell_active_area = Property(unit="m2")
    active_area = Property("self.cell_count.value * self.cell_active_area.value", "m2")
    mounting_face = Property(unit="1")
    normal_body = Property("illumination.face_normal(face=self.mounting_face).vector", "1")
    body_face_area = Property(
        "illumination.face_area(face=self.mounting_face, length_x=self.spacecraft.length_x, "
        "length_y=self.spacecraft.length_y, length_z=self.spacecraft.length_z).square_metres", "m2")
    packing_fraction = Property(unit="1")
    usable_area = Property(unit="m2")
    panel_area = Property("sizing.panel_area(active_area=self.active_area, packing_fraction=self.packing_fraction).square_metres", "m2")
    cell_open_circuit_voltage = Property(unit="V")
    cell_short_circuit_current = Property(unit="A")
    open_circuit_voltage = Property(
        "self.series_count.value * (sizing.pv_characteristics(pv_points=self.cell_iv_curve).open_circuit_voltage "
        "if self.cell_iv_curve.value else self.cell_open_circuit_voltage.value)", "V")
    short_circuit_current = Property(
        "self.parallel_count.value * (sizing.pv_characteristics(pv_points=self.cell_iv_curve).short_circuit_current "
        "if self.cell_iv_curve.value else self.cell_short_circuit_current.value)", "A")
    sunlight_path_efficiency = Property(unit="1")
    eclipse_path_efficiency = Property(unit="1")
    cell_eol_voltage = Property(unit="V")
    cell_eol_current = Property(unit="A")
    eol_voltage = Property(
        "self.series_count.value * (sizing.pv_characteristics(pv_points=self.cell_iv_curve).mpp_voltage "
        "if self.cell_iv_curve.value else self.cell_eol_voltage.value)", "V")
    eol_current = Property(
        "self.parallel_count.value * (sizing.pv_characteristics(pv_points=self.cell_iv_curve).mpp_current "
        "if self.cell_iv_curve.value else self.cell_eol_current.value)", "A")
    cell_eol_power = Property(
        "sizing.cell_power(pv_points=self.cell_iv_curve).watts if self.cell_iv_curve.value else "
        "sizing.cell_power(eol_voltage=self.cell_eol_voltage, eol_current=self.cell_eol_current).watts", "W")
    eol_power = Property("self.cell_count.value * self.cell_eol_power.value", "W")
    bol_efficiency = Property(unit="1")
    lifetime_retention = Property(unit="1")
    temperature_factor = Property(unit="1")
    eol_efficiency = Property(
        "sizing.solar_efficiency(bol_efficiency=self.bol_efficiency, lifetime_retention=self.lifetime_retention, "
        "temperature_factor=self.temperature_factor).fraction", "1")
    irradiance = Property(unit="W/m2")
    inherent_retention = Property(unit="1")
    assembly_efficiency = Property(unit="1")
    sunlight_projection = Property(
        "illumination.orbital_projection(normal_body=self.normal_body, "
        "pointing=self.spacecraft.AttitudeDeterminationAndControl.pointing, "
        "pointing_face=self.spacecraft.AttitudeDeterminationAndControl.pointing_face, "
        "clocking_angle=self.spacecraft.AttitudeDeterminationAndControl.effective_clocking_angle, "
        "semimajor_axis=self.mission.orbit.semimajor_axis, eccentricity=self.mission.orbit.eccentricity, "
        "earth_radius=self.mission.orbit.earth_radius, beta_angle=self.mission.orbit.beta_angle, "
        "sun_projection_angle=self.mission.orbit.effective_sun_projection_angle, "
        "period=self.mission.orbit.period).sunlight_mean", "1")
    projected_sunlight_duration = Property("self.sunlight_projection.value * self.mission.orbit.sunlight_duration.value", "s")
    generation_efficiency = Property(
        "sizing.pv_efficiency(pv_points=self.cell_iv_curve, active_area=self.cell_active_area, "
        "reference_irradiance=self.pv_reference_irradiance).fraction "
        "if self.cell_iv_curve.value else self.eol_efficiency", "1")
    operating_efficiency = Property("self.generation_efficiency.value * self.operating_power.value / self.eol_power.value", "1")
    normal_power_density = Property("self.irradiance.value * self.operating_efficiency.value", "W/m2")
    eol_power_density = Property(
        "sizing.array_power_density(irradiance=self.irradiance, eol_efficiency=self.operating_efficiency, "
        "inherent_retention=self.inherent_retention, assembly_efficiency=self.assembly_efficiency, "
        "sunlight_projection=self.sunlight_projection).watts_per_square_metre", "W/m2")
    available_power = Property("self.active_area.value * self.eol_power_density.value", "W")
    source_energy = Property("self.available_power.value * self.mission.orbit.sunlight_duration.value", "J")


class RegulatorAndConverter(SolarPowerPath):
    input_voltage = Property(unit="V")
    minimum_input_voltage = Property(unit="V")
    maximum_input_voltage = Property(unit="V")
    absolute_maximum_input_voltage = Property(unit="V")
    maximum_input_current = Property(unit="A")
    output_voltage = Property(unit="V")
    maximum_output_current = Property(unit="A")
    efficiency = Property(unit="1")


class PowerCircuit(SolarPowerPath):
    maximum_voltage = Property(unit="V")
    maximum_current = Property(unit="A")


class Protection(PowerCircuit):
    """Normal operation screening at explicitly assigned sensing points."""

    trip_parameters = ("undervoltage_threshold", "overvoltage_threshold", "current_limit")
    undervoltage_threshold = Property(unit="V")  # Highest applicable UV trip threshold.
    overvoltage_threshold = Property(unit="V")  # Lowest applicable OV trip threshold.
    current_limit = Property(unit="A")          # Lowest applicable OC trip threshold.
    voltage_extrema = Property("sizing.extrema(values=self.no_trip.voltages)", "V")
    current_extrema = Property("sizing.extrema(values=self.no_trip.currents)", "A")

    def create_requirements(self):
        checks = {
            "undervoltage_threshold": ("undervoltage", "voltage_extrema", "minimum", "0 <= target < measure"),
            "overvoltage_threshold": ("overvoltage", "voltage_extrema", "maximum", "0 <= measure < target"),
            "current_limit": ("overcurrent", "current_extrema", "maximum",
                              "0 <= self.parent.context.current_extrema.value.minimum <= measure < target"),
        }
        if not self.trip_parameters or len(set(self.trip_parameters)) != len(self.trip_parameters):
            raise ValueError("Declare a nonempty set of distinct protection trip parameters.")
        conditions = []
        for parameter in self.trip_parameters:
            if parameter not in checks:
                raise ValueError(f"Unknown protection trip parameter {parameter!r}.")
            name, field, bound, comparison = checks[parameter]
            conditions.append(VerificationCondition(
                name, Property(f"self.parent.context.{field}.value.{bound}",
                               "A" if field == "current_extrema" else "V"),
                getattr(self, parameter),
                f"math.isfinite(measure) and math.isfinite(target) and {comparison}",
            ))
        self.add_requirement(
            "no_trip",
            statement="The protection shall remain inactive for the declared normal operating samples.",
            rationale="framework/scripts/sizing.py#extrema. Use the highest UV threshold and lowest OV/OC thresholds "
                      "for the selected COTS configuration and conditions. Equality fails this conservative screen. "
                      "Voltage samples refer to the detector's sensed node or individual cells. "
                      "Current samples are magnitudes for the specified protected direction. "
                      "This screen assumes an enabled, recovered device and establishes no fault response or recovery claim.",
            voltages=Property(unit="V"), currents=Property(unit="A"), conditions=tuple(conditions),
        )


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


class CotsProtection(Protection, COTS):
    pass


EPS.default_components = (Battery, SolarArray, RegulatorAndConverter, PowerCircuit)
