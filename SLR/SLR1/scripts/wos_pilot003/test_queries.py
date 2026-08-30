#!/usr/bin/env python3
"""Offline membership check for the Pilot 003 Web of Science query plan."""

from __future__ import annotations

import json

from queries import MAIN_IDS, PSR_IDS, audit


def main() -> int:
    payload = audit()
    if payload["membership_check"]["status"] != "ok":
        print(json.dumps(payload["membership_check"], indent=2))
        return 1
    print(
        json.dumps(
            {
                "status": "ok",
                "main_partitions": list(MAIN_IDS),
                "psr_partitions": list(PSR_IDS),
                "event_count": len(payload["events"]),
                "a1_wildcard_count": payload["a1_wildcard_exception"]["wildcard_count"],
                "a1_replaced_literals": payload["a1_wildcard_exception"]["replaced_literal_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
