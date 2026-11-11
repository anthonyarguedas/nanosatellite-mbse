"""Prepare and inspect the same Python sessions used by the JavaScript UI.

From the repository root:
    PYTHONPATH=framework/python/src python3 -i framework/python/examples/repl_demo.py --prepare /tmp/nanosat-repl

Add --run for an explicit recorded walkthrough, or use --interactive without -i.
Original demo inputs remain unchanged. Prepared outputs use create-only saves.
"""

from __future__ import annotations

import argparse
import code
import shlex
from pathlib import Path

from nanosat_mbse import CotsBattery, EPS, MPPT, Session
from nanosat_mbse.persistence.migrate import convert_json


def bindings(session, sizing=None):
    return {
        "session": session,
        "sizing": sizing,
        "eps": next((item for item in session.elements if isinstance(item, EPS)), None),
        "mppt": next(
            (item for item in session.scripts if isinstance(item, MPPT)), None
        ),
        "battery": next(
            (
                item
                for item in (sizing or session).cots_components
                if isinstance(item, CotsBattery)
            ),
            None,
        ),
    }


def walkthrough(session, sizing=None):
    """Execute real calculations, restore changed inputs, save and reopen."""
    namespace = bindings(session, sizing)
    print("Native EPS:", type(namespace["eps"]).__name__)
    if namespace["battery"] is not None:
        battery = namespace["battery"]
        print("Native COTS:", type(battery).__name__)
        if any(reference.name == "mass" for reference in battery.facts):
            print("Sourced battery mass:", battery.fact_value("mass"), "kg")
    mppt = namespace["mppt"]
    if mppt is None:
        raise ValueError("Choose a session containing an MPPT instance for --run.")
    print("Native analysis:", type(mppt).__name__)
    linked = next(
        row
        for row in session.requirements
        if any(method.source is mppt for method in row.verifications)
    )
    print("Before execution:", linked.verify().state.value)
    session.run(mppt)
    print("Tracking efficiency:", mppt.value("tracking_efficiency"))
    print("Delivered energy:", mppt.value("delivered_energy_J"), "J")
    checks = [
        (row, result)
        for row, result in session.verify().assessments
        if row.id.startswith(("ORB", "SCN", "MPT"))
    ]
    print(
        "Passing linked checks:",
        sum(result.verified for _, result in checks),
        "of",
        len(checks),
    )
    binding = mppt.parameters["voltage_step_V"]
    target, name = mppt, "voltage_step_V"
    if isinstance(binding.expression, str) and "." in binding.expression:
        owner, name = binding.expression.split(".")
        target = session.get(owner)
    original = target.parameters[name]
    try:
        target.set_value(name, session.value(target, name) * 2)
        print("Changed input, old evidence:", linked.verify().state.value)
        session.run(mppt)
        print("Rerun tracking efficiency:", mppt.value("tracking_efficiency"))
    finally:
        session.configure_parameter(target, original)
    session.run(mppt)
    print("Restored tracking efficiency:", mppt.value("tracking_efficiency"))
    status = session.save()
    print("Saved Python session:", status.path)
    session = session.reload()
    print(
        "Reopened evidence:",
        "unset" if session.execution_evidence is None else "cached",
    )
    return session


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("session", nargs="?", type=Path)
    source.add_argument("--prepare", type=Path, metavar="DIRECTORY")
    parser.add_argument(
        "--run",
        action="store_true",
        help="explicitly run the walkthrough and save restored inputs",
    )
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args(argv)
    sizing = None
    if args.prepare is not None:
        directory = args.prepare.expanduser().absolute()
        directory.mkdir(parents=True, exist_ok=True)
        demos = Path(__file__).resolve().parents[2] / "requirements-ui" / "demo"
        sizing = convert_json(
            demos / "example-workspace.json", directory / "sizing.py"
        ).session
        session = convert_json(
            demos / "analysis-workspace.json", directory / "analysis.py"
        ).session
        print("Prepared independent native sessions in", directory)
        print(
            "UI: MISSION_FILE="
            + shlex.quote(str(directory / "analysis.py"))
            + " npm start (from framework/requirements-ui)"
        )
    else:
        session = Session.open(args.session)
    if args.run:
        session = walkthrough(session, sizing)
    namespace = bindings(session, sizing)
    namespace.update(Session=Session, CotsBattery=CotsBattery, EPS=EPS, MPPT=MPPT)
    print("Available: session, sizing, eps, battery, mppt")
    print(
        "Try: type(mppt), session.run(mppt), mppt.value('tracking_efficiency'), session.verify()['MPT008'].verified"
    )
    print(
        "Use session.save() and session = session.reload() to share saved changes with the UI."
    )
    if args.interactive:
        code.interact(banner="nanosat_mbse: native session REPL", local=namespace)
    return namespace


if __name__ == "__main__":
    globals().update(main())
