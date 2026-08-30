#!/usr/bin/env python3
"""Complete the remaining ATAI Pilot 003 cells with the validated ID-pair route."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_stable_id_pair import run_pair  # noqa: E402

PARTITIONS = ("B2", "BG1", "BG2", "BC1", "BT2")


def main() -> int:
    if os.environ.get("BH_BROWSER_ACCESS_CONTRACT") != "shared-browser-owned-tabs-v1":
        raise SystemExit("Run this source workflow through the shared browser runner.")
    outcomes = []
    for partition in PARTITIONS:
        receipt = run_pair(partition)
        outcomes.append(
            {
                "partition": partition,
                "source_total": receipt["pass_artifacts"][0]["source_total"],
                "stable_ids": receipt["stable_id_count"],
            }
        )
    print(json.dumps({"status": "ok", "outcomes": outcomes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
