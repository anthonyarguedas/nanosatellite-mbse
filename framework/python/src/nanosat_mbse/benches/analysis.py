"""Native MPPT and illumination study configurations.

Blank studies leave independent inputs unset. The combined demonstration uses
synthetic inputs and limits and establishes no hardware qualification claim.
"""

from __future__ import annotations

from ..core.session import Session
from ..domains.eps.components import RegulatorAndConverter, SolarArray
from ..domains.eps.subsystem import EPS
from ..domains.mission import CubeSat, Orbit
from ..persistence.repository import dumps, loads, validate_session
from ._builder import Field, add_requirement

DOCUMENT = "framework/requirements-ui/analyses/README.md"


def create_mppt_session(**providers):
    session = Session(name="MPPT analysis (inputs required)", **providers)
    session.variables = []
    bus = session.add(CubeSat("BUS", key="mppt-bus"), initialize=False)
    eps = session.add(EPS("EPS", key="mppt-eps"), owner=bus, initialize=False)
    solar = session.add(
        SolarArray("SOL", key="mppt-array", name="Modeled array section"),
        owner=eps,
        initialize=False,
    )
    converter = session.add(
        RegulatorAndConverter(
            "REG", key="mppt-converter", name="Modeled MPPT receiver"
        ),
        owner=eps,
        initialize=False,
    )
    script = session.add(
        session.verification_registry.create("mppt_po"), initialize=False
    )
    input_units = {port.name: port.unit for port in script.inputs}
    limit_units = {
        "input_absolute_max_V": "V",
        "source_current_limit_A": "A",
        "settling_limit_s": "s",
        "delivered_energy_min_J": "J",
    }
    rationale = (
        "Proposed preliminary simulation criterion. Inputs and acceptance limits require engineer approval and sources. "
        "No mission, product or compliance values are assumed. The script uses one uniform section, an empirical I-V curve "
        "and an ideal P&O controller. See analyses/README.md."
    )

    def ref(name):
        return f"{script.id}.{name}"

    def requirement(text, names, condition, backed=False, sources=()):
        row = add_requirement(
            session,
            text=text,
            fields=tuple(
                Field(name, input_units.get(name) or limit_units.get(name, ""))
                for name in names
            ),
            owner=eps,
            affected=(solar, converter),
            sources=sources,
            condition=condition,
            script=script if backed else None,
            prefix="MPT",
            origin=DOCUMENT,
            rationale=rationale,
        )
        for name in names:
            if name in script.parameters:
                script.set_expression(name, f"{row.id}.{name}")
        return row

    points = requirement(
        "The array model shall use reference points $$voc_ref_V$$, $$isc_ref_A$$, $$vmp_ref_V$$ and $$imp_ref_A$$ at irradiance $$reference_irradiance_W_m2$$ and temperature $$reference_temperature_C$$.",
        (
            "voc_ref_V",
            "isc_ref_A",
            "vmp_ref_V",
            "imp_ref_A",
            "reference_irradiance_W_m2",
            "reference_temperature_C",
        ),
        "0 < vmp_ref_V < voc_ref_V and 0 < imp_ref_A < isc_ref_A and reference_irradiance_W_m2 > 0 and reference_temperature_C > -273.15",
    )
    scaling = requirement(
        "The array model shall apply voltage temperature coefficient $$voltage_temp_coeff_V_C$$, relative current temperature coefficient $$current_temp_coeff_per_C$$ and logarithmic irradiance coefficient $$voltage_log_coefficient_V$$.",
        (
            "voltage_temp_coeff_V_C",
            "current_temp_coeff_per_C",
            "voltage_log_coefficient_V",
        ),
        "math.isfinite(voltage_temp_coeff_V_C) and math.isfinite(current_temp_coeff_per_C) and voltage_log_coefficient_V >= 0",
    )
    environment = requirement(
        "The tracker shall be assessed for $$duration_s$$ with a change at $$change_time_s$$ from irradiance $$irradiance_start_W_m2$$ and temperature $$temperature_start_C$$ to irradiance $$irradiance_end_W_m2$$ and temperature $$temperature_end_C$$.",
        (
            "duration_s",
            "change_time_s",
            "irradiance_start_W_m2",
            "temperature_start_C",
            "irradiance_end_W_m2",
            "temperature_end_C",
        ),
        "duration_s > 0 and 0 <= change_time_s <= duration_s and irradiance_start_W_m2 >= 0 and irradiance_end_W_m2 >= 0 and temperature_start_C > -273.15 and temperature_end_C > -273.15",
    )
    controller = requirement(
        "The tracker shall perturb voltage by $$voltage_step_V$$ every $$sample_period_s$$ from initial voltage $$initial_voltage_V$$.",
        ("voltage_step_V", "sample_period_s", "initial_voltage_V"),
        "voltage_step_V > 0 and sample_period_s > 0 and initial_voltage_V > 0",
    )
    sources = (points, scaling, environment, controller)
    requirement(
        "The source maximum power voltage shall remain within the tracking interval from $$tracking_min_V$$ to $$tracking_max_V$$ during illuminated phases.",
        ("tracking_min_V", "tracking_max_V"),
        f"0 < tracking_min_V < tracking_max_V and {ref('min_mpp_voltage_V')} >= tracking_min_V and {ref('max_mpp_voltage_V')} <= tracking_max_V",
        True,
        sources,
    )
    requirement(
        "The source open circuit voltage shall remain at most $$input_absolute_max_V$$.",
        ("input_absolute_max_V",),
        f"input_absolute_max_V > 0 and {ref('max_open_circuit_voltage_V')} <= input_absolute_max_V",
        True,
        sources,
    )
    requirement(
        "The source short circuit current shall remain at most $$source_current_limit_A$$.",
        ("source_current_limit_A",),
        f"source_current_limit_A > 0 and {ref('max_short_circuit_current_A')} <= source_current_limit_A",
        True,
        sources,
    )
    requirement(
        "The tracker shall capture at least fraction $$tracking_efficiency_min$$ of the energy attainable within its tracking interval.",
        ("tracking_efficiency_min",),
        f"0 < tracking_efficiency_min <= 1 and {ref('tracking_efficiency')} >= tracking_efficiency_min",
        True,
        sources,
    )
    requirement(
        "The tracker shall settle within $$settling_limit_s$$ to relative power error at most $$settling_relative_band$$ for at least $$settling_hold_s$$ through the end of each illuminated phase.",
        ("settling_limit_s", "settling_relative_band", "settling_hold_s"),
        f"settling_limit_s >= 0 and 0 < settling_relative_band < 1 and settling_hold_s > 0 and {ref('settled')} and {ref('settling_time_s')} <= settling_limit_s",
        True,
        sources,
    )
    requirement(
        "The conditioning model shall deliver at least $$delivered_energy_min_J$$ over the assessed interval at conversion efficiency $$conversion_efficiency$$.",
        ("delivered_energy_min_J", "conversion_efficiency"),
        f"delivered_energy_min_J >= 0 and 0 < conversion_efficiency <= 1 and {ref('delivered_energy_J')} >= delivered_energy_min_J",
        True,
        sources,
    )
    validate_session(session)
    return session


def add_scenario_analysis(original, *, orbit=None):
    """Return an independent native copy with an unexecuted illumination study."""
    session = loads(
        dumps(original),
        catalog=original.catalog,
        database=original.database,
        verification_registry=original.verification_registry,
        session_class=type(original),
    )
    orbits = [
        row
        for row in session.requirements
        if row.definition == "FrameworkRequirements::OrbitPeriod"
    ]
    if orbit is not None:
        orbit = session.get(orbit if isinstance(orbit, str) else orbit.key)
        if orbit not in orbits:
            raise ValueError("Choose an existing OrbitPeriod requirement key or ID.")
    elif len(orbits) > 1:
        raise ValueError("Several orbit definitions exist. Select one with --orbit.")
    else:
        orbit = orbits[0] if orbits else None
    script = session.add(
        session.verification_registry.create("scenario_illumination"), initialize=False
    )
    if orbit is not None:
        for name, target in (
            ("altitude_km", "altitude_km"),
            ("earth_radius_km", "earthRadius_km"),
            ("mu_km3_s2", "gravitationalParameter_km3_s2"),
        ):
            script.set_expression(name, f"{orbit.id}.{target}")
    rationale = (
        "Proposed interval-specific illumination criterion. Set and source the scenario inputs in the Python script input table. "
        "Supply an approved acceptance limit here. Eclipse lengths use midpoint samples and are clipped at interval boundaries. "
        "Repeat at a smaller step and cover the required epochs and orbital phases. This criterion establishes no thermal, "
        "energy closure or complete mission compliance."
    )
    for text, field, condition in (
        (
            "The longest total eclipse within the assessed interval shall be at most $$eclipse_limit_s$$.",
            Field("eclipse_limit_s", "s"),
            f"eclipse_limit_s >= 0 and {script.id}.longest_eclipse_s <= eclipse_limit_s",
        ),
        (
            "The assessed panel section shall receive interval mean direct irradiance of at least $$irradiance_min_W_m2$$.",
            Field("irradiance_min_W_m2", "W/m**2"),
            f"irradiance_min_W_m2 >= 0 and {script.id}.mean_irradiance_W_m2 >= irradiance_min_W_m2",
        ),
    ):
        add_requirement(
            session,
            text=text,
            fields=(field,),
            condition=condition,
            owner=session.mission,
            affected=() if orbit is None else orbit.affected,
            sources=() if orbit is None else (orbit,),
            script=script,
            prefix="SCN",
            origin=DOCUMENT,
            rationale=rationale,
        )
    validate_session(session)
    return session


def create_analysis_demo(**providers):
    session = create_mppt_session(**providers)
    session.add(Orbit("ORB", key="test-orbit", name="Test orbit"))
    session = add_scenario_analysis(session)
    session.name = "Illumination + MPPT test bench"
    orbit = next(
        row
        for row in session.requirements
        if row.definition == "FrameworkRequirements::OrbitPeriod"
    )
    orbit.set_value("altitude_km", 500)
    illumination = next(
        script
        for script in session.scripts
        if script.definition == "scenario_illumination"
    )
    for name, expression in {
        "inclination_deg": "0",
        "raan_deg": "0",
        "argument_latitude_deg": "0",
        "epoch_jd": "2460754.5",
        "duration_s": f"2 * {orbit.id}.orbit_period_s",
        "step_s": "2",
        "earth_j2": "0.00108263",
        "solar_constant_W_m2": "1361",
        "panel_normal_radial": "1",
        "panel_normal_along": "0",
        "panel_normal_cross": "0",
        "sun_tracking": "True",
    }.items():
        illumination.set_expression(name, expression)
    mppt = next(script for script in session.scripts if script.definition == "mppt_po")
    for name, expression in {
        "voc_ref_V": "8",
        "isc_ref_A": "1.1",
        "vmp_ref_V": "6.4",
        "imp_ref_A": "1",
        "reference_irradiance_W_m2": "1361",
        "reference_temperature_C": "28",
        "voltage_temp_coeff_V_C": "-0.02",
        "current_temp_coeff_per_C": "0.0005",
        "voltage_log_coefficient_V": "0.25",
        "irradiance_start_W_m2": f"{illumination.id}.max_irradiance_W_m2",
        "irradiance_end_W_m2": f"{illumination.id}.mean_irradiance_W_m2",
        "temperature_start_C": "28",
        "temperature_end_C": "50",
        "change_time_s": "60",
        "duration_s": "120",
        "sample_period_s": "0.1",
        "voltage_step_V": "0.05",
        "initial_voltage_V": "3",
        "tracking_min_V": "2",
        "tracking_max_V": "8",
        "conversion_efficiency": "0.9",
        "settling_relative_band": "0.02",
        "settling_hold_s": "5",
    }.items():
        owner_id, parameter = mppt.parameters[name].expression.split(".")
        session.get(owner_id).set_expression(parameter, expression)
    for name, expression in {
        "input_absolute_max_V": "9",
        "source_current_limit_A": "1.2",
        "tracking_efficiency_min": "0.95",
        "settling_limit_s": "15",
        "delivered_energy_min_J": "400",
        "eclipse_limit_s": "2400",
        "irradiance_min_W_m2": "800",
    }.items():
        row = next(row for row in session.requirements if f"$${name}$$" in row.text)
        row.set_expression(name, expression)
    for row in session.requirements:
        row.rationale = (
            "Synthetic test bench. Values and acceptance limits are illustrative test data. "
            "See analyses/README.md for the model and test setup."
            + (f" Equation or criterion basis: {row.origin}." if row.origin else "")
        )
    environment = session.get("MPT003")
    environment.derive_from(session.get("SCN002"))
    environment.rationale += (
        " Initial irradiance uses the illumination maximum and final irradiance uses its interval mean. "
        "These are two constant test levels. They do not replay the orbital time history."
    )
    validate_session(session)
    return session
