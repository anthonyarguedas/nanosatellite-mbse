"""Native command-line entry points for independent study sessions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .benches import (
    add_scenario_analysis,
    create_analysis_demo,
    create_mppt_session,
    create_report_session,
    report_profiles,
)
from .service.application import Application


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    analysis = commands.add_parser("analysis", help="create a native analysis session")
    analysis.add_argument("kind", choices=("demo", "mppt", "scenario"))
    analysis.add_argument("--name")
    analysis.add_argument("--mission", type=Path)
    analysis.add_argument(
        "--from", dest="source", default=None, help="current or a saved session ID"
    )
    analysis.add_argument(
        "--orbit", help="OrbitPeriod requirement key or ID for scenario copies"
    )
    report = commands.add_parser("report", help="create a native report assessment")
    report.add_argument("profile", nargs="?")
    report.add_argument("--name")
    report.add_argument("--mission", type=Path)
    report.add_argument("--list", action="store_true")
    return result


def create_analysis(args, application):
    if args.kind != "scenario" and (args.source is not None or args.orbit is not None):
        raise ValueError("--from and --orbit apply only to scenario copies.")
    if args.kind == "demo":
        graph = create_analysis_demo(**application._providers())
    elif args.kind == "mppt":
        graph = create_mppt_session(**application._providers())
    else:
        identity = args.source or "current"
        if identity == "current" and not any(
            path.exists() or path.is_symlink()
            for path in (application.current_path, application.legacy_path)
        ):
            raise FileNotFoundError(
                "Choose an existing current session or a saved session with --from."
            )
        source = application.load_session(identity)
        graph = add_scenario_analysis(source, orbit=args.orbit)
    names = {
        "demo": "Illumination + MPPT test bench",
        "mppt": "MPPT analysis (inputs required)",
        "scenario": "Illumination analysis (inputs required)",
    }
    return (
        graph,
        args.name or names[args.kind],
        "mission" if args.kind == "scenario" else "mppt-eps",
    )


def main(argv=None):
    arguments = parser()
    args = arguments.parse_args(argv)
    try:
        if args.command == "report" and args.list:
            if args.profile is not None:
                raise ValueError("--list does not take a report profile.")
            for profile in report_profiles():
                print(f"{profile.id}\t{profile.name}")
            return 0
        application = Application(args.mission)
        if args.command == "analysis":
            graph, name, tab = create_analysis(args, application)
        else:
            if args.profile is None:
                raise ValueError("Choose a report profile or use --list.")
            graph = create_report_session(args.profile, **application._providers())
            name, tab = args.name or graph.name, "report-eps"
        view = application.create_session(graph, name=name)
        path = application.directory / view["session"]["id"] / "session.py"
        print(view["session"]["name"])
        print(path)
        print(f"Open the Session picker or ?session={view['session']['id']}#{tab}.")
        print(
            "No analysis was executed. Independent inputs and acceptance limits remain engineer-owned."
        )
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
