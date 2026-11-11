"""Native analysis execution, with the same API intended for the UI service.

Run from the repository root:
    PYTHONPATH=framework/python/src python3 framework/python/examples/verification.py

Add --workspace framework/requirements-ui/demo/analysis-workspace.json to run the
existing illumination and MPPT bench through the native classes as well.
All values in this demonstration are illustrative or synthetic.
"""

import argparse
import json
from pathlib import Path

from nanosat_mbse import (
    NormalInterval,
    Parameter,
    Requirement,
    Session,
    VerificationMethod,
)


def native_example():
    session = Session(name="Native analysis example")
    analysis = session.add(NormalInterval("SCR001"))
    analysis.set_value("mean", 4)
    analysis.set_value("standard_deviation", 1)
    analysis.set_value("confidence", 0.95)
    requirement = session.add(
        Requirement(
            "REQ001",
            "The interval upper bound shall not exceed $$upper_limit$$.",
            parameters=(Parameter("upper_limit", value=6),),
            verifications=(
                VerificationMethod(
                    "interval bound",
                    "SCR001.upper <= upper_limit",
                    source=analysis,
                ),
            ),
        )
    )
    print("Before execution:", requirement.verify().state.value)
    evidence = analysis.run()
    print("After execution:", requirement.verify().state.value)
    print("Upper bound:", analysis.value("upper"))
    print("Execution time:", round(evidence.result_for(analysis).duration_ms), "ms")
    analysis.set_value("mean", 8)
    print("Changed inputs:", requirement.verify().state.value)
    session.run(analysis)
    print("After rerunning:", requirement.verify().state.value)
    print("Stored configuration:", analysis.parameters["mean"].value)


def demo_example(path):
    session = Session.from_projection(json.loads(path.read_text(encoding="utf-8")))
    before = session.to_projection()
    evidence = session.run("SCR001")
    for script in session.scripts:
        result = evidence.result_for(script)
        print(type(script).__name__, result.state, result.message)
        print(result.log)
    checks = [
        (row, result)
        for row, result in session.verify().assessments
        if row.id.startswith(("ORB", "SCN", "MPT"))
    ]
    assert len(checks) == 15 and all(result.verified for _, result in checks)
    assert session.to_projection() == before
    print("Passing linked checks:", len(checks))
    print("Longest eclipse:", session.get("SCR002").value("longest_eclipse_s"), "s")
    print(
        "Mean irradiance:", session.get("SCR002").value("mean_irradiance_W_m2"), "W/m²"
    )
    print("Tracking efficiency:", session.get("SCR001").value("tracking_efficiency"))
    print("Delivered energy:", session.get("SCR001").value("delivered_energy_J"), "J")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args()
    native_example()
    if args.workspace is not None:
        demo_example(args.workspace)


if __name__ == "__main__":
    main()
