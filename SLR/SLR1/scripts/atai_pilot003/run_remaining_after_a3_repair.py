#!/usr/bin/env python3
"""Resume Pilot 003 only after the recorded A3 stable-ID repair succeeds."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_schedule import SEARCH_DIR, load_plan, run_event  # noqa: E402


def main() -> int:
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise SystemExit("Run this source workflow through the shared browser runner.")
    repair_path = SEARCH_DIR / "A3-repair-reconciliation.json"
    if not repair_path.exists():
        raise SystemExit("A3 repair evidence is missing; do not continue the source schedule.")
    repair = json.loads(repair_path.read_text(encoding="utf-8"))
    if repair.get("schema_version") != "atai-pilot-003-a3-stable-id-repair/v1" or repair.get("repair", {}).get("stable_id_equality") is not True:
        raise SystemExit("A3 repair did not prove stable-ID equality; do not continue the source schedule.")
    started = False
    for event in load_plan():
        if event["partition_id"] == "A3":
            started = True
            continue
        if not started:
            continue
        if not run_event(event):
            raise SystemExit(
                f"ATAI source failure at {event['partition_id']}; stopped without an unrecorded narrower replacement."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
