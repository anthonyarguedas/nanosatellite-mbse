#!/usr/bin/env python3
"""Write the create-only Pilot 003 raw-query plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from queries import SLR1_DIR, audit


DEFAULT_OUTPUT = (
    SLR1_DIR
    / "source-specific"
    / "web-of-science-core-collection"
    / "pilots"
    / "003"
    / "searches"
    / "query-plan.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = audit()
    if payload["membership_check"]["status"] != "ok":
        raise SystemExit("Refusing to write a plan with failed query membership checks")
    path = args.output_path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"saved": str(path), "events": len(payload["events"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
