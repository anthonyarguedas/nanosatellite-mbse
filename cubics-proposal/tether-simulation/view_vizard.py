#!/usr/bin/env python3
"""Open the continuous orbital separation, tether motion and collisions in Vizard."""

import argparse
from pathlib import Path

from vizard_scene import open_vizard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scene",
        "--scenario",
        choices=["combined", "orbit", "deployment", "lifetime"],
        default="combined",
        help="All choices open the continuous mission.bin recording",
    )
    parser.add_argument("--app", type=Path, help="Path to the Vizard application")
    parser.add_argument(
        "--file", type=Path, help="Explicit completed recording to open"
    )
    args = parser.parse_args()
    path = args.file or Path(__file__).parent / "output" / "mission.bin"
    if args.file is None:
        import json

        status_path = path.parent / "run_status.json"
        if status_path.exists():
            status = json.loads(status_path.read_text())
            if status["status"] != "completed":
                parser.error(
                    f"The latest run is {status['status']}: "
                    f"{status['simulated_time_s'] / 3600:.2f} of "
                    f"{status['requested_duration_s'] / 3600:.2f} h. "
                    "Existing mission.bin belongs to the previous run. See run_status.json."
                )
    if not path.exists():
        parser.error("Generate the continuous recording first with simulate.py")
    if args.scene != "combined":
        print(
            "The old separate scenes are replaced by one mission. Both views share its timeline.",
            flush=True,
        )
    open_vizard(path, args.app)


if __name__ == "__main__":
    main()
