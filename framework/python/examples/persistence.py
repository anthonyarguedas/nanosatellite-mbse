"""Shared native session files for a REPL and the future UI service.

Run from the repository root:
    PYTHONPATH=framework/python/src python3 framework/python/examples/persistence.py

Optionally add --workspace framework/requirements-ui/demo/analysis-workspace.json
for explicit migration and execution in a temporary directory.
All example inputs are illustrative or synthetic.
"""

import argparse
import tempfile
from pathlib import Path

from nanosat_mbse import (
    NormalInterval,
    Parameter,
    Requirement,
    Session,
    SessionConflict,
    VerificationMethod,
    convert_json,
)


def native_example(directory):
    session = Session(name="Human and agent share one native model")
    analysis = session.add(NormalInterval("SCR001"))
    analysis.set_value("mean", 4)
    analysis.set_value("standard_deviation", 1)
    analysis.set_value("confidence", 0.95)
    session.add(
        Requirement(
            "REQ001",
            "The interval upper bound shall not exceed $$upper_limit$$.",
            parameters=(Parameter("upper_limit", value=6),),
            verifications=(
                VerificationMethod(
                    "upper bound",
                    "SCR001.upper <= upper_limit",
                    source=analysis,
                ),
            ),
        )
    )
    path = directory / "session.py"
    session.save(path)
    print("Saved:", path.name)
    print("Imports, populated objects and execution calls are readable Python.")

    human = Session.open(path)
    agent = Session.open(path)
    print("Freshly opened:", agent.verify()["REQ001"].state.value)
    agent.run("SCR001")
    print("Native result:", agent.get("SCR001").value("upper"))
    print("Explicit verification:", agent.verify()["REQ001"].state.value)
    agent.get("REQ001").rationale = "Reviewed through the native API."
    agent.save()
    print("Reopened evidence:", Session.open(path).execution_evidence)

    human.get("REQ001").rationale = "Independent unsaved edit."
    try:
        human.save()
    except SessionConflict:
        print("A stale second writer conflicts safely.")
    refreshed = human.reload()
    print("Reloaded rationale:", refreshed.get("REQ001").rationale)


def workspace_example(source, directory):
    original = source.read_bytes()
    converted = convert_json(source, directory / "converted-session.py")
    session = Session.open(converted.storage.path)
    assert source.read_bytes() == original
    assert session.execution_evidence is None
    print("Preserved legacy JSON:", source.name)
    if session.scripts:
        session.run("SCR001")
        checks = [
            result
            for row, result in session.verify().assessments
            if row.id.startswith(("ORB", "SCN", "MPT"))
        ]
        print("Passing linked checks:", sum(result.verified for result in checks))
        print(
            "MPPT delivered energy:",
            session.get("SCR001").value("delivered_energy_J"),
            "J",
        )
    session.save()
    reopened = Session.open(converted.storage.path)
    assert reopened.execution_evidence is None
    print("Saved and reopened without cached execution results.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="nanosat-session-demo-") as temporary:
        directory = Path(temporary)
        native_example(directory)
        if args.workspace is not None:
            workspace_example(args.workspace, directory)


if __name__ == "__main__":
    main()
