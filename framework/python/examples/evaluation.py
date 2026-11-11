"""Native calculation and mode budgets through the same API used by the UI.

Run from the repository root:
    PYTHONPATH=framework/python/src python3 framework/python/examples/evaluation.py

The component draws below are illustrative estimates, not product guarantees.
"""

from nanosat_mbse import ComponentState, CubeSat, GroundStation, Orbit, Payload, Session


def main():
    session = Session(name="Native calculation example")
    for domain in (Orbit(), CubeSat(), Payload(), GroundStation()):
        session.add(domain)
    session.get("ORB001").set_value("altitude_km", 500)
    print("Orbit period:", session.value("ORB001", "orbit_period_s"), "s")

    nominal = session.add_mode("Nominal", sunlight=80, eclipse=20)
    safe = session.add_mode("Safe", sunlight=20, eclipse=80)
    for component in session.physical_components:
        if component.default_accounting != "counted":
            continue
        active = ComponentState("Active", watts=1.0)
        standby = ComponentState("Standby", watts=0.1)
        session.configure_load(
            component,
            states=(active, standby),
            assignments={nominal: active, safe: standby},
        )
    session.connect_power("EPS")
    load = session.get("SIZ001")
    print("Sunlight average:", load.value("sunlight_power_W"), "W")
    print("Eclipse average:", load.value("eclipse_power_W"), "W")
    print("Draw by mode:", dict(session.value("PWR001", "draw_power_W")))

    projection = session.evaluate()
    orbit = next(
        row for row in projection["results"] if row["key"] == session.get("ORB001").key
    )
    assert orbit["values"]["orbit_period_s"] == session.value(
        "ORB001", "orbit_period_s"
    )
    assert (
        session.get("ORB001").verify().verified == session.verify()["ORB001"].verified
    )
    print("Native and browser projections agree.")
    print("Unassigned power limits:", session.verify()["PWR001"].state.value)


if __name__ == "__main__":
    main()
