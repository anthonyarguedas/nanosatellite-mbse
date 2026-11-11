"""Native graph and COTS loading example, with no UI or analysis execution.

Run from the repository root:
    PYTHONPATH=framework/python/src python3 framework/python/examples/session_graph.py
"""

from nanosat_mbse import (
    Battery,
    CotsBattery,
    CubeSat,
    DatabaseBacked,
    GroundStation,
    Orbit,
    Payload,
    Session,
)


def main():
    session = Session(name="Native object graph")
    for domain in (Orbit(), CubeSat(), Payload(), GroundStation()):
        session.add(domain)
    eps = session.get("EPS")
    print(type(eps).__name__, len(eps.components), "default components")

    backup = eps.add_component(Battery(name="Backup battery"))
    added = [
        requirement for requirement in eps.requirements if requirement.subject is backup
    ]
    print(type(backup).__name__, len(added), "component requirements")

    selected = eps.add_component(
        CotsBattery(
            product="gomspace_nanopower_bpx_100wh_8s1p",
            database=session.database,
            usage=session.get("BAT"),
        )
    )
    assert isinstance(selected, Battery)
    assert isinstance(selected, DatabaseBacked)
    mass = next(
        fact
        for fact in selected.product_record.facts
        if fact.name == "mass"
        and fact.element == "self"
        and fact.value_kind == "nominal"
    )
    selected.select_fact("mass", mass)
    print(
        type(selected).__name__, selected.fact_value("mass"), "kg nominal sourced mass"
    )
    print("Physical usage:", selected.usage.id)
    print("Physical components:", len(session.physical_components))
    print("COTS selections:", len(session.cots_components))

    restored = Session.from_projection(
        session.to_projection(), database=session.database
    )
    assert restored.to_projection() == session.to_projection()
    print(
        "Restored graph:",
        len(restored.requirements),
        "requirements, no creation hooks rerun",
    )


if __name__ == "__main__":
    main()
