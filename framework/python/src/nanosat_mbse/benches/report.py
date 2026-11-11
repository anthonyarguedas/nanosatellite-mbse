"""Optional native report assessments with unset independent inputs and limits.

Each factory creates real engineering objects and pins current database facts.
No analysis executes while a configuration is constructed.
"""

from dataclasses import dataclass
from typing import Callable, Tuple

from ._builder import Field, ReportBuilder


def _energy(builder):
    a0 = builder.analysis(
        "eps_energy_segment",
        "Nominal eclipse",
        ("FR-16", "FR-19", "EPS-10", "EPS-11", "EPS-12", "EPS-13", "EPS-14"),
    )
    a1 = builder.analysis(
        "eps_energy_segment",
        "Nominal sunlight",
        ("FR-16", "FR-19", "EPS-10", "EPS-11", "EPS-12", "EPS-13", "EPS-14"),
    )
    a1.set("energy_initial_J", "SCR001.energy_end_J")
    a1.set("soc_initial", "SCR001.soc_end")
    a1.set("energy_capacity_J", "INP002.energy_capacity_J")
    a1.set("charge_capacity_C", "INP002.charge_capacity_C")
    a0.check(
        "The EPS shall supply the declared load throughout at least $$required_service_s$$ of the assessed interval.",
        (Field("required_service_s", "s", "float", None),),
        "required_service_s > 0 and INP001.duration_s >= required_service_s and SCR001.unserved_energy_J == 0 and SCR001.service_duration_s >= INP001.duration_s",
        ("FR-16", "EPS-10"),
    )
    a0.check(
        "The battery shall retain at least $$energy_reserve_J$$ of energy throughout the assessed interval.",
        (Field("energy_reserve_J", "J", "float", "INP003.energy_reserve_J"),),
        "SCR001.energy_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a0.check(
        "The battery charge state shall remain at least $$soc_min$$ throughout the assessed interval.",
        (Field("soc_min", "", "float", "INP003.soc_min"),),
        "SCR001.soc_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a0.check(
        "The battery shall respect its separate charging and discharging temperature intervals at $$temperature_C$$.",
        (Field("temperature_C", "degC", "float", "INP005.temperature_C"),),
        "SCR001.charge_temperature_ok and SCR001.discharge_temperature_ok",
        ("EPS-13",),
    )
    a0.check(
        "The EPS shall accommodate solar surplus within its declared handling capacity $$surplus_capacity_W$$.",
        (Field("surplus_capacity_W", "W", "float", "INP006.surplus_capacity_W"),),
        "SCR001.surplus_supported",
        ("EPS-14",),
    )
    a1.check(
        "The EPS shall supply the declared load throughout at least $$required_service_s$$ of the assessed interval.",
        (Field("required_service_s", "s", "float", None),),
        "required_service_s > 0 and INP007.duration_s >= required_service_s and SCR002.unserved_energy_J == 0 and SCR002.service_duration_s >= INP007.duration_s",
        ("FR-16", "EPS-10"),
    )
    a1.check(
        "The battery shall retain at least $$energy_reserve_J$$ of energy throughout the assessed interval.",
        (Field("energy_reserve_J", "J", "float", "INP009.energy_reserve_J"),),
        "SCR002.energy_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a1.check(
        "The battery charge state shall remain at least $$soc_min$$ throughout the assessed interval.",
        (Field("soc_min", "", "float", "INP009.soc_min"),),
        "SCR002.soc_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a1.check(
        "The battery shall respect its separate charging and discharging temperature intervals at $$temperature_C$$.",
        (Field("temperature_C", "degC", "float", "INP011.temperature_C"),),
        "SCR002.charge_temperature_ok and SCR002.discharge_temperature_ok",
        ("EPS-13",),
    )
    a1.check(
        "The EPS shall accommodate solar surplus within its declared handling capacity $$surplus_capacity_W$$.",
        (Field("surplus_capacity_W", "W", "float", "INP012.surplus_capacity_W"),),
        "SCR002.surplus_supported",
        ("EPS-14",),
    )
    a1.check(
        "The battery shall replenish its initial energy within numerical tolerance $$closure_tolerance_J$$ over the nominal repeating interval.",
        (Field("closure_tolerance_J", "J", "float", None),),
        "closure_tolerance_J >= 0 and SCR002.energy_end_J >= INP003.energy_initial_J - closure_tolerance_J",
        ("EPS-11",),
    )
    a1.check(
        "The battery shall replenish its initial charge state $$soc_initial$$ over the nominal repeating interval.",
        (Field("soc_initial", "", "float", "INP003.soc_initial"),),
        "SCR002.soc_end >= soc_initial",
        ("EPS-11",),
    )
    a0.check(
        "The nominal battery cycle shall remain within depth of discharge $$dod_max$$.",
        (Field("dod_max", "", "float", None),),
        "0 < dod_max <= 1 and SCR001.soc_minimum >= 1 - dod_max",
        ("EPS-09", "EPS-10"),
    )
    a1.check(
        "The nominal battery cycle shall remain within depth of discharge $$dod_max$$.",
        (Field("dod_max", "", "float", None),),
        "0 < dod_max <= 1 and SCR002.soc_minimum >= 1 - dod_max",
        ("EPS-09", "EPS-10"),
    )


def _survival(builder):
    a0 = builder.analysis(
        "eps_energy_segment",
        "Survival interval",
        ("FR-16", "FR-19", "EPS-10", "EPS-11", "EPS-12", "EPS-13", "EPS-14"),
    )
    a1 = builder.analysis(
        "eps_energy_segment",
        "Recovery interval",
        ("FR-16", "FR-19", "EPS-10", "EPS-11", "EPS-12", "EPS-13", "EPS-14"),
    )
    a1.set("energy_initial_J", "SCR001.energy_end_J")
    a1.set("soc_initial", "SCR001.soc_end")
    a1.set("energy_capacity_J", "INP002.energy_capacity_J")
    a1.set("charge_capacity_C", "INP002.charge_capacity_C")
    a0.check(
        "The EPS shall supply the declared load throughout at least $$required_service_s$$ of the assessed interval.",
        (Field("required_service_s", "s", "float", None),),
        "required_service_s > 0 and INP001.duration_s >= required_service_s and SCR001.unserved_energy_J == 0 and SCR001.service_duration_s >= INP001.duration_s",
        ("FR-16", "EPS-12"),
    )
    a0.check(
        "The battery shall retain at least $$energy_reserve_J$$ of energy throughout the assessed interval.",
        (Field("energy_reserve_J", "J", "float", "INP003.energy_reserve_J"),),
        "SCR001.energy_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a0.check(
        "The battery charge state shall remain at least $$soc_min$$ throughout the assessed interval.",
        (Field("soc_min", "", "float", "INP003.soc_min"),),
        "SCR001.soc_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a0.check(
        "The battery shall respect its separate charging and discharging temperature intervals at $$temperature_C$$.",
        (Field("temperature_C", "degC", "float", "INP005.temperature_C"),),
        "SCR001.charge_temperature_ok and SCR001.discharge_temperature_ok",
        ("EPS-13",),
    )
    a0.check(
        "The EPS shall accommodate solar surplus within its declared handling capacity $$surplus_capacity_W$$.",
        (Field("surplus_capacity_W", "W", "float", "INP006.surplus_capacity_W"),),
        "SCR001.surplus_supported",
        ("EPS-14",),
    )
    a1.check(
        "The EPS shall supply the declared load throughout at least $$required_service_s$$ of the assessed interval.",
        (Field("required_service_s", "s", "float", None),),
        "required_service_s > 0 and INP007.duration_s >= required_service_s and SCR002.unserved_energy_J == 0 and SCR002.service_duration_s >= INP007.duration_s",
        ("FR-16", "EPS-12"),
    )
    a1.check(
        "The battery shall retain at least $$energy_reserve_J$$ of energy throughout the assessed interval.",
        (Field("energy_reserve_J", "J", "float", "INP009.energy_reserve_J"),),
        "SCR002.energy_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a1.check(
        "The battery charge state shall remain at least $$soc_min$$ throughout the assessed interval.",
        (Field("soc_min", "", "float", "INP009.soc_min"),),
        "SCR002.soc_reserve_ok",
        ("EPS-10", "EPS-12"),
    )
    a1.check(
        "The battery shall respect its separate charging and discharging temperature intervals at $$temperature_C$$.",
        (Field("temperature_C", "degC", "float", "INP011.temperature_C"),),
        "SCR002.charge_temperature_ok and SCR002.discharge_temperature_ok",
        ("EPS-13",),
    )
    a1.check(
        "The EPS shall accommodate solar surplus within its declared handling capacity $$surplus_capacity_W$$.",
        (Field("surplus_capacity_W", "W", "float", "INP012.surplus_capacity_W"),),
        "SCR002.surplus_supported",
        ("EPS-14",),
    )


def _guidance(builder):
    a0 = builder.analysis(
        "eps_guidance", "Method eligibility", ("FR-03", "FR-26", "FR-39")
    )
    a0.check(
        "The assessment shall establish its model prerequisites for $$operating_case_count$$ declared cases before execution.",
        (Field("operating_case_count", "", "integer", "INP001.operating_case_count"),),
        "operating_case_count > 0 and SCR001.executable and SCR001.unmet_prerequisite_count == 0",
        ("FR-03", "FR-39"),
    )


def _converter(builder):
    a0 = builder.analysis(
        "eps_converter_step",
        "Converter voltage step",
        ("FR-16", "FR-19", "EPS-04", "EPS-06"),
    )
    a0.check(
        "The converter shall reach its required supply interval within startup time $$startup_limit_s$$.",
        (Field("startup_limit_s", "s", "float", None),),
        "startup_limit_s >= 0 and SCR001.startup_reached and SCR001.startup_time_s <= startup_limit_s",
        ("EPS-04", "EPS-06"),
    )
    a0.check(
        "The converter shall settle to its declared voltage error band within $$settling_limit_s$$.",
        (Field("settling_limit_s", "s", "float", None),),
        "settling_limit_s >= 0 and SCR001.settled and SCR001.settling_time_s <= settling_limit_s",
        ("FR-16", "FR-19"),
    )
    a0.check(
        "The converter shall provide required voltage throughout at least $$required_service_s$$ after startup.",
        (Field("required_service_s", "s", "float", None),),
        "required_service_s > 0 and SCR001.service_duration_s >= required_service_s",
        ("EPS-06",),
    )


def _charger(builder):
    builder.requirement(
        text="The charger shall support battery series count $$battery_series_count$$ within its interval from $$series_min$$ to $$series_max$$.",
        fields=(
            Field("battery_series_count", "cells", "integer", None),
            Field("series_min", "cells", "integer", None),
            Field("series_max", "cells", "integer", None),
        ),
        condition="0 < series_min <= battery_series_count <= series_max",
        reports=("EPS-01", "EPS-05"),
    )
    builder.requirement(
        text="The selected charge voltage $$charge_voltage_V$$ shall remain in the common battery and charger voltage interval.",
        fields=(
            Field("charge_voltage_V", "V", "float", None),
            Field("battery_charge_min_V", "V", "float", None),
            Field("battery_charge_max_V", "V", "float", None),
            Field("charger_min_V", "V", "float", None),
            Field("charger_max_V", "V", "float", None),
        ),
        condition="0 < battery_charge_min_V <= charge_voltage_V <= battery_charge_max_V and 0 < charger_min_V <= charge_voltage_V <= charger_max_V",
        reports=("EPS-05",),
    )
    builder.requirement(
        text="The selected charge current $$charge_current_A$$ shall remain within the battery limit $$battery_charge_limit_A$$ and charger limit $$charger_limit_A$$.",
        fields=(
            Field("charge_current_A", "A", "float", None),
            Field("battery_charge_limit_A", "A", "float", None),
            Field("charger_limit_A", "A", "float", None),
        ),
        condition="0 <= charge_current_A <= battery_charge_limit_A and 0 <= charge_current_A <= charger_limit_A",
        reports=("EPS-05", "EPS-07"),
    )
    builder.requirement(
        text="The charge termination current $$termination_current_A$$ shall remain within the battery interval from $$termination_min_A$$ to $$termination_max_A$$.",
        fields=(
            Field("termination_current_A", "A", "float", None),
            Field("termination_min_A", "A", "float", None),
            Field("termination_max_A", "A", "float", None),
        ),
        condition="0 <= termination_min_A <= termination_current_A <= termination_max_A",
        reports=("EPS-05",),
    )
    builder.requirement(
        text="The charging temperature $$charge_temperature_C$$ shall remain between $$charge_min_C$$ and $$charge_max_C$$.",
        fields=(
            Field("charge_temperature_C", "degC", "float", None),
            Field("charge_min_C", "degC", "float", None),
            Field("charge_max_C", "degC", "float", None),
        ),
        condition="-273.15 < charge_min_C <= charge_temperature_C <= charge_max_C",
        reports=("EPS-05", "EPS-13"),
    )


def _interfaces(builder):
    builder.requirement(
        text="The service port shall support required exchange rate $$required_rate_Hz$$ within capacity $$supported_rate_Hz$$.",
        fields=(
            Field("required_rate_Hz", "Hz", "float", None),
            Field("supported_rate_Hz", "Hz", "float", None),
        ),
        condition="0 <= required_rate_Hz <= supported_rate_Hz",
        reports=("EPS-18",),
    )
    builder.requirement(
        text="The service port response $$response_time_s$$ shall remain within bound $$response_limit_s$$.",
        fields=(
            Field("response_time_s", "s", "float", None),
            Field("response_limit_s", "s", "float", None),
        ),
        condition="0 <= response_time_s <= response_limit_s",
        reports=("EPS-18",),
    )
    builder.requirement(
        text="The transmitted logic levels $$output_low_max_V$$ and $$output_high_min_V$$ shall satisfy the receiver thresholds $$input_low_max_V$$ and $$input_high_min_V$$.",
        fields=(
            Field("output_low_max_V", "V", "float", None),
            Field("output_high_min_V", "V", "float", None),
            Field("input_low_max_V", "V", "float", None),
            Field("input_high_min_V", "V", "float", None),
        ),
        condition="output_low_max_V < output_high_min_V and input_low_max_V < input_high_min_V and output_low_max_V <= input_low_max_V and output_high_min_V >= input_high_min_V",
        reports=("EPS-18",),
    )
    builder.requirement(
        text="The service signal interval from $$signal_min_V$$ to $$signal_max_V$$ shall remain within the receiver operating interval from $$operating_min_V$$ to $$operating_max_V$$.",
        fields=(
            Field("signal_min_V", "V", "float", None),
            Field("signal_max_V", "V", "float", None),
            Field("operating_min_V", "V", "float", None),
            Field("operating_max_V", "V", "float", None),
        ),
        condition="operating_min_V <= signal_min_V <= signal_max_V <= operating_max_V",
        reports=("EPS-18",),
    )


def _path(builder):
    a0 = builder.analysis(
        "eps_power_path",
        "Power path",
        ("FR-14", "FR-16", "EPS-03", "EPS-04", "EPS-06", "EPS-07"),
    )
    a0.check(
        "The converter shall support rail voltage $$rail_voltage_V$$ at source voltage $$source_voltage_V$$ within its declared operating and startup envelope.",
        (
            Field("rail_voltage_V", "V", "float", "INP001.rail_voltage_V"),
            Field("source_voltage_V", "V", "float", "INP001.source_voltage_V"),
        ),
        "SCR001.input_ok and SCR001.startup_ok and SCR001.envelope_ok",
        ("EPS-03", "EPS-04"),
    )
    a0.check(
        "The load terminal voltage shall remain between $$load_min_V$$ and $$load_max_V$$ during steady and pulse demand.",
        (
            Field("load_min_V", "V", "float", "INP003.load_min_V"),
            Field("load_max_V", "V", "float", "INP003.load_max_V"),
        ),
        "SCR001.steady_voltage_ok and SCR001.pulse_voltage_ok",
        ("EPS-06",),
    )
    a0.check(
        "The path shall supply declared steady current $$steady_current_A$$ and pulse current $$pulse_current_A$$ within its battery, converter, switch and connection ratings.",
        (
            Field("steady_current_A", "A", "float", "INP002.steady_current_A"),
            Field("pulse_current_A", "A", "float", "INP002.pulse_current_A"),
        ),
        "SCR001.battery_current_ok and SCR001.converter_current_ok and SCR001.switch_current_ok and SCR001.connection_current_ok and SCR001.pulse_duration_ok",
        ("EPS-07",),
    )
    a0.check(
        "The supplied converter startup bound shall remain within $$startup_limit_s$$.",
        (Field("startup_limit_s", "s", "float", "INP008.startup_limit_s"),),
        "SCR001.startup_time_ok",
        ("EPS-04", "EPS-06"),
    )
    a0.check(
        "The converter and distribution path shall dissipate at most $$dissipation_limit_W$$ under steady and pulse demand.",
        (Field("dissipation_limit_W", "W", "float", None),),
        "dissipation_limit_W >= 0 and max(SCR001.steady_converter_loss_W + SCR001.steady_path_loss_W, SCR001.pulse_converter_loss_W + SCR001.pulse_path_loss_W) <= dissipation_limit_W",
        ("FR-16", "EPS-13"),
    )


def _protection(builder):
    a0 = builder.analysis(
        "eps_protection",
        "Protection scenario",
        ("FR-16", "FR-19", "EPS-15", "EPS-16", "EPS-17"),
    )
    a0.check(
        "The EPS shall interrupt the declared fault within $$interruption_limit_s$$ without reenergizing the persisting fault.",
        (Field("interruption_limit_s", "s", "float", "INP006.interruption_limit_s"),),
        "SCR001.fault_seen and SCR001.protection_active and SCR001.protection_ok",
        ("EPS-15", "EPS-16"),
    )
    a0.check(
        "The protected path shall remain within fault stress limits $$i2t_limit_A2s$$ and $$peak_limit_A$$.",
        (
            Field("i2t_limit_A2s", "A2 s", "float", "INP005.i2t_limit_A2s"),
            Field("peak_limit_A", "A", "float", "INP005.peak_limit_A"),
        ),
        "SCR001.stress_ok",
        ("EPS-15",),
    )
    a0.check(
        "The EPS shall supply legitimate nominal current $$legitimate_current_A$$ throughout $$nominal_duration_s$$ without nuisance trips.",
        (
            Field("legitimate_current_A", "A", "float", "INP001.legitimate_current_A"),
            Field("nominal_duration_s", "s", "float", "INP002.nominal_duration_s"),
        ),
        "INP002.nominal_duration_s > 0 and SCR001.nuisance_free",
        ("EPS-15",),
    )
    a0.check(
        "The EPS shall keep any asserted inhibit effective throughout the fault interval $$fault_duration_s$$.",
        (Field("fault_duration_s", "s", "float", "INP002.fault_duration_s"),),
        "SCR001.inhibited_outputs_off",
        ("EPS-17",),
    )
    a0.check(
        "The protected output shall recover within $$recovery_limit_s$$ after the declared fault clears.",
        (Field("recovery_limit_s", "s", "float", None),),
        "recovery_limit_s >= 0 and INP003.recovery_duration_s > 0 and SCR001.recovery_observed and SCR001.recovery_time_s <= recovery_limit_s",
        ("EPS-16",),
    )


def _battery(builder):
    a0 = builder.analysis(
        "eps_battery_step",
        "Battery circuit step",
        ("FR-16", "EPS-06", "EPS-08", "EPS-10"),
    )
    a0.check(
        "The battery terminal voltage shall remain between $$voltage_min_V$$ and $$voltage_max_V$$ throughout the circuit step.",
        (
            Field("voltage_min_V", "V", "float", "INP003.voltage_min_V"),
            Field("voltage_max_V", "V", "float", "INP003.voltage_max_V"),
        ),
        "SCR001.voltage_ok",
        ("EPS-06",),
    )
    a0.check(
        "The battery charge state shall remain between $$soc_min$$ and $$soc_max$$ throughout the circuit step.",
        (
            Field("soc_min", "", "float", "INP004.soc_min"),
            Field("soc_max", "", "float", "INP004.soc_max"),
        ),
        "SCR001.physical_soc_ok and SCR001.soc_ok",
        ("EPS-10",),
    )
    a0.check(
        "The battery resistors shall dissipate at most $$battery_loss_limit_W$$ throughout the circuit step.",
        (Field("battery_loss_limit_W", "W", "float", None),),
        "battery_loss_limit_W >= 0 and SCR001.max_loss_W <= battery_loss_limit_W",
        ("FR-16", "EPS-13"),
    )


def _thermal(builder):
    a0 = builder.analysis(
        "eps_thermal", "Thermal interval", ("FR-16", "EPS-13", "EPS-14")
    )
    a0.check(
        "The component node shall remain between $$temp_min_K$$ and $$temp_max_K$$ throughout the thermal interval.",
        (
            Field("temp_min_K", "K", "float", "INP002.temp_min_K"),
            Field("temp_max_K", "K", "float", "INP003.temp_max_K"),
        ),
        "SCR001.temp_ok",
        ("EPS-13",),
    )
    a0.check(
        "Any active charging shall respect its temperature interval from $$charge_min_K$$ to $$charge_max_K$$.",
        (
            Field("charge_min_K", "K", "float", "INP003.charge_min_K"),
            Field("charge_max_K", "K", "float", "INP003.charge_max_K"),
        ),
        "SCR001.charge_ok",
        ("EPS-05", "EPS-13"),
    )


def _electrothermal(builder):
    a0 = builder.analysis(
        "eps_battery_step",
        "Battery circuit step",
        ("FR-16", "EPS-06", "EPS-08", "EPS-10"),
    )
    a0.check(
        "The battery terminal voltage shall remain between $$voltage_min_V$$ and $$voltage_max_V$$ throughout the circuit step.",
        (
            Field("voltage_min_V", "V", "float", "INP003.voltage_min_V"),
            Field("voltage_max_V", "V", "float", "INP003.voltage_max_V"),
        ),
        "SCR001.voltage_ok",
        ("EPS-06",),
    )
    a0.check(
        "The battery charge state shall remain between $$soc_min$$ and $$soc_max$$ throughout the circuit step.",
        (
            Field("soc_min", "", "float", "INP004.soc_min"),
            Field("soc_max", "", "float", "INP004.soc_max"),
        ),
        "SCR001.physical_soc_ok and SCR001.soc_ok",
        ("EPS-10",),
    )
    a0.check(
        "The battery resistors shall dissipate at most $$battery_loss_limit_W$$ throughout the circuit step.",
        (Field("battery_loss_limit_W", "W", "float", None),),
        "battery_loss_limit_W >= 0 and SCR001.max_loss_W <= battery_loss_limit_W",
        ("FR-16", "EPS-13"),
    )
    a1 = builder.analysis("eps_thermal", "Battery hot bound", ("FR-16", "EPS-13"))
    a2 = builder.analysis("eps_thermal", "Battery cold bound", ("FR-16", "EPS-13"))
    a1.set("dissipation_W", "SCR001.max_loss_W")
    a2.set("dissipation_W", "SCR001.min_loss_W")
    a1.set("duration_s", "INP003.duration_s")
    a2.set("duration_s", "INP003.duration_s")
    a2.set("initial_temp_K", "INP005.initial_temp_K")
    a2.set("ambient_temp_K", "INP005.ambient_temp_K")
    a2.set("heater_W", "INP005.heater_W")
    a2.set("heat_capacity_J_K", "INP006.heat_capacity_J_K")
    a2.set("conductance_W_K", "INP006.conductance_W_K")
    a2.set("temp_min_K", "INP006.temp_min_K")
    a2.set("temp_max_K", "INP007.temp_max_K")
    a2.set("charge_min_K", "INP007.charge_min_K")
    a2.set("charge_max_K", "INP007.charge_max_K")
    a1.set("charge_active", "INP001.current_A > 0")
    a1.check(
        "The battery thermal bound shall remain within node limits from $$temp_min_K$$ to $$temp_max_K$$.",
        (
            Field("temp_min_K", "K", "float", "INP006.temp_min_K"),
            Field("temp_max_K", "K", "float", "INP007.temp_max_K"),
        ),
        "SCR002.temp_ok",
        ("EPS-13",),
    )
    a1.check(
        "Any charging shall remain within the declared node interval from $$charge_min_K$$ to $$charge_max_K$$.",
        (
            Field("charge_min_K", "K", "float", "INP007.charge_min_K"),
            Field("charge_max_K", "K", "float", "INP007.charge_max_K"),
        ),
        "SCR002.charge_ok",
        ("EPS-05", "EPS-13"),
    )
    a2.set("charge_active", "INP001.current_A > 0")
    a2.check(
        "The battery thermal bound shall remain within node limits from $$temp_min_K$$ to $$temp_max_K$$.",
        (
            Field("temp_min_K", "K", "float", "INP009.temp_min_K"),
            Field("temp_max_K", "K", "float", "INP010.temp_max_K"),
        ),
        "SCR003.temp_ok",
        ("EPS-13",),
    )
    a2.check(
        "Any charging shall remain within the declared node interval from $$charge_min_K$$ to $$charge_max_K$$.",
        (
            Field("charge_min_K", "K", "float", "INP010.charge_min_K"),
            Field("charge_max_K", "K", "float", "INP010.charge_max_K"),
        ),
        "SCR003.charge_ok",
        ("EPS-05", "EPS-13"),
    )


def _sizing(builder):
    a0 = builder.analysis(
        "eps_sizing",
        "Assembly sizing",
        ("FR-14", "FR-17", "FR-20", "EPS-01", "EPS-02", "EPS-08", "EPS-20"),
    )
    a0.check(
        "The configured array with $$pv_series$$ series cells and $$pv_parallel$$ parallel strings shall meet its preliminary EOL generation bound.",
        (
            Field("pv_series", "", "integer", "INP003.pv_series"),
            Field("pv_parallel", "", "integer", "INP003.pv_parallel"),
        ),
        "SCR001.generation_margin_W >= 0",
        ("EPS-02",),
    )
    a0.check(
        "The array active area shall fit usable face area $$usable_face_area_m2$$ at packing fraction $$packing_fraction$$.",
        (
            Field("usable_face_area_m2", "m**2", "float", "INP004.usable_face_area_m2"),
            Field("packing_fraction", "", "float", "INP004.packing_fraction"),
        ),
        "SCR001.packing_margin_m2 >= 0",
        ("EPS-20",),
    )
    a0.check(
        "The configured battery with $$bat_series$$ series cells and $$bat_parallel$$ parallel strings shall meet its preliminary BOL energy bound.",
        (
            Field("bat_series", "", "integer", "INP005.bat_series"),
            Field("bat_parallel", "", "integer", "INP005.bat_parallel"),
        ),
        "SCR001.bol_energy_margin_Wh >= 0",
        ("EPS-08",),
    )
    a0.check(
        "The configured battery shall meet its retained energy bound at retention factor $$energy_retained_factor$$.",
        (
            Field(
                "energy_retained_factor", "", "float", "INP005.energy_retained_factor"
            ),
        ),
        "SCR001.retained_energy_margin_Wh >= 0",
        ("EPS-08",),
    )
    a0.check(
        "The configured battery shall retain charge capacity of at least $$required_retained_charge_Ah$$.",
        (
            Field(
                "required_retained_charge_Ah",
                "Ah",
                "float",
                "INP006.required_retained_charge_Ah",
            ),
        ),
        "SCR001.retained_charge_margin_Ah >= 0",
        ("EPS-08",),
    )
    a0.check(
        "The selected source operating interval from $$source_low_V$$ to $$source_high_V$$ shall satisfy the declared receiver and ideal conversion voltage screens.",
        (
            Field("source_low_V", "V", "float", "INP006.source_low_V"),
            Field("source_high_V", "V", "float", "INP006.source_high_V"),
        ),
        "SCR001.voltage_screen_ok",
        ("EPS-03", "EPS-04"),
    )


def _geometry(builder):
    a0 = builder.analysis("eps_geometry", "Installation envelope", ("EPS-20",))
    a0.check(
        "The declared component envelope shall fit its installation box within contact tolerance $$tolerance_m$$.",
        (Field("tolerance_m", "m", "float", "INP007.tolerance_m"),),
        "SCR001.contained",
        ("EPS-20",),
    )
    a0.check(
        "The declared component envelope shall clear its keep-out under contact tolerance $$tolerance_m$$ and the selected touching policy.",
        (Field("tolerance_m", "m", "float", "INP007.tolerance_m"),),
        "SCR001.keepout_clear",
        ("EPS-20",),
    )


def _fit(builder):
    a0 = builder.analysis("eps_fit", "Parameter fit", ("FR-22",))
    a0.check(
        "The parameter fit shall reproduce accepted supplied samples within RMS error $$rmse_limit$$ and maximum error $$max_error_limit$$.",
        (
            Field("rmse_limit", "", "float", "INP002.rmse_limit"),
            Field("max_error_limit", "", "float", "INP002.max_error_limit"),
        ),
        "SCR001.fit_quality_ok",
        ("FR-22",),
    )
    a0.check(
        "The estimated parameters for declared model $$model_kind$$ shall satisfy that model's physical parameter bounds.",
        (Field("model_kind", "", "integer", "INP001.model_kind"),),
        "SCR001.physical_model_ok",
        ("FR-22",),
    )


def _ram(builder):
    a0 = builder.analysis("eps_ram", "Fault tree", ("FR-27",))
    a0.check(
        "The declared top failure probability shall remain at most $$failure_probability_limit$$ over the supplied exposure.",
        (Field("failure_probability_limit", "", "float", None),),
        "0 <= failure_probability_limit <= 1 and SCR001.top_failure_probability <= failure_probability_limit",
        ("FR-27",),
    )
    a0.check(
        "The declared mission service shall retain reliability of at least $$reliability_min$$ over the supplied exposure.",
        (Field("reliability_min", "", "float", None),),
        "0 <= reliability_min <= 1 and SCR001.mission_reliability >= reliability_min",
        ("FR-27",),
    )
    a0.check(
        "The conditional top failure probability shall remain at most $$conditional_probability_limit$$ for the declared failure evidence.",
        (Field("conditional_probability_limit", "", "float", None),),
        "0 <= conditional_probability_limit <= 1 and SCR001.conditional_failure_probability <= conditional_probability_limit",
        ("FR-27",),
    )


def _cots_protection(builder):
    c0 = builder.component(
        "ti_tps63802dlar",
        (
            (
                "ovp_available",
                {"name": "autonomous_overvoltage_protection", "element": "self"},
            ),
            (
                "output_ovp_max_V",
                {
                    "name": "overvoltage_threshold",
                    "element": "output_supply",
                    "valueKind": "maximum",
                },
            ),
            (
                "output_ovp_action",
                {"name": "overvoltage_action", "element": "output_supply"},
            ),
            (
                "uvlo_available",
                {"name": "autonomous_undervoltage_protection", "element": "self"},
            ),
            (
                "uvlo_falling_min_V",
                {
                    "name": "undervoltage_threshold",
                    "element": "self",
                    "valueKind": "minimum",
                },
            ),
            (
                "uvlo_rising_max_V",
                {
                    "name": "undervoltage_release",
                    "element": "self",
                    "valueKind": "maximum",
                },
            ),
            ("startup_min_V", {"name": "startup_input_voltage_min", "element": "self"}),
            (
                "operating_min_K",
                {"name": "operating_temperature_min", "element": "self"},
            ),
            (
                "operating_max_K",
                {"name": "operating_temperature_max", "element": "self"},
            ),
        ),
    )
    builder.requirement(
        text="The converter output OVP threshold shall remain at most $$ovp_trip_ceiling_V$$.",
        fields=(Field("ovp_trip_ceiling_V", "V", "float", None),),
        condition='ovp_trip_ceiling_V > 0 and CMP001.ovp_available and CMP001.output_ovp_action == "output_OVP_stops_switching" and CMP001.output_ovp_max_V <= ovp_trip_ceiling_V',
        reports=("EPS-15",),
        component=c0,
        extra="This selects TPS63802 controller evidence, not a complete circuit or battery protector. OVP and UVLO thresholds retain tolerance endpoints and their separate operating conditions. The engineer must supply actual circuitry, operating cases, external-component ratings and independent limits.",
    )
    builder.requirement(
        text="The converter UVLO falling threshold shall remain at least $$uvlo_trip_floor_V$$ under its declared once-started condition.",
        fields=(Field("uvlo_trip_floor_V", "V", "float", None),),
        condition="uvlo_trip_floor_V > 0 and CMP001.uvlo_available and CMP001.uvlo_falling_min_V >= uvlo_trip_floor_V",
        reports=("EPS-04",),
        component=c0,
        extra="This selects TPS63802 controller evidence, not a complete circuit or battery protector. OVP and UVLO thresholds retain tolerance endpoints and their separate operating conditions. The engineer must supply actual circuitry, operating cases, external-component ratings and independent limits.",
    )
    builder.requirement(
        text="The startup source voltage $$startup_source_V$$ shall support the converter UVLO release and minimum startup input voltage.",
        fields=(Field("startup_source_V", "V", "float", None),),
        condition="startup_source_V >= CMP001.uvlo_rising_max_V and startup_source_V >= CMP001.startup_min_V",
        reports=("EPS-04",),
        component=c0,
        extra="This selects TPS63802 controller evidence, not a complete circuit or battery protector. OVP and UVLO thresholds retain tolerance endpoints and their separate operating conditions. The engineer must supply actual circuitry, operating cases, external-component ratings and independent limits.",
    )
    builder.requirement(
        text="The converter junction temperature $$junction_temperature_K$$ shall remain within its recommended operating interval.",
        fields=(Field("junction_temperature_K", "K", "float", None),),
        condition="CMP001.operating_min_K <= junction_temperature_K <= CMP001.operating_max_K",
        reports=("EPS-13",),
        component=c0,
        extra="This selects TPS63802 controller evidence, not a complete circuit or battery protector. OVP and UVLO thresholds retain tolerance endpoints and their separate operating conditions. The engineer must supply actual circuitry, operating cases, external-component ratings and independent limits.",
    )


@dataclass(frozen=True)
class ReportProfile:
    id: str
    name: str
    configure: Callable[[ReportBuilder], None]
    products: Tuple[str, ...] = ()


_PROFILES = (
    ReportProfile("energy", "Nominal energy and charge closure", _energy, ()),
    ReportProfile("survival", "Survival and recovery energy", _survival, ()),
    ReportProfile("guidance", "EPS method and activity prerequisites", _guidance, ()),
    ReportProfile(
        "converter", "Converter command and startup response", _converter, ()
    ),
    ReportProfile("charger", "Charger operating bounds", _charger, ()),
    ReportProfile(
        "interfaces", "Service port electrical and timing bounds", _interfaces, ()
    ),
    ReportProfile("path", "Converter rail and simultaneous pulse demand", _path, ()),
    ReportProfile("protection", "Protection fault and recovery MIL", _protection, ()),
    ReportProfile("battery", "Battery voltage and charge state response", _battery, ()),
    ReportProfile(
        "thermal", "Component and charging temperature response", _thermal, ()
    ),
    ReportProfile(
        "electrothermal", "Battery electrical and thermal bounds", _electrothermal, ()
    ),
    ReportProfile("sizing", "Integer assembly sizing and packing", _sizing, ()),
    ReportProfile("geometry", "Installation envelope accommodation", _geometry, ()),
    ReportProfile("fit", "Supplied-data parameter estimation", _fit, ()),
    ReportProfile("ram", "Authored fault tree and reliability", _ram, ()),
    ReportProfile(
        "cots-protection",
        "TPS63802 sourced protection bounds",
        _cots_protection,
        ("ti_tps63802dlar",),
    ),
)


def report_profiles():
    """Return the supported independent report study configurations."""
    return _PROFILES


def create_report_session(profile, **providers):
    selected = next((item for item in _PROFILES if item.id == profile), None)
    if selected is None:
        raise ValueError(
            "Choose a report assessment: "
            + ", ".join(item.id for item in _PROFILES)
            + "."
        )
    builder = ReportBuilder(selected.name, **providers)
    selected.configure(builder)
    return builder.finish()
