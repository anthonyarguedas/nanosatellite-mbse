"""Adopted Wiley source cells for Pilot 005."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from typing import Any

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
PILOT004_QUERY_SHA256 = "78b3d8ec50a9094c078aac4e6a7fa8b2c53a63d970490922972d3b9776465fab"
PILOT004_QUERY_PATH = (
    Path(__file__).resolve().parents[1]
    / "wiley_online_library_pilot004"
    / "queries.py"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if _sha256(PILOT004_QUERY_PATH) != PILOT004_QUERY_SHA256:
    raise RuntimeError("The accepted Wiley Pilot 004 query transcription changed")

_spec = importlib.util.spec_from_file_location(
    "wiley_p005_adopted_queries", PILOT004_QUERY_PATH
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load adopted Wiley queries from {PILOT004_QUERY_PATH}")
_module = importlib.util.module_from_spec(_spec)
sys.modules.setdefault(_spec.name, _module)
_spec.loader.exec_module(_module)

if _module.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The adopted Wiley queries use a different protocol commit")

SCHEDULE_IDS = tuple(_module.SCHEDULE_IDS)
WILDCARD_CELLS = _module.WILDCARD_CELLS
WILDCARD_REPLACEMENTS = _module.WILDCARD_REPLACEMENTS
SOURCE_QUERY_LIMIT = _module.SOURCE_QUERY_LIMIT

# Pilot 004 provides context only. Pilot 005 accepts the fresh source total and
# proves completeness inside each event rather than forcing an old snapshot.
PILOT004_REFERENCE_TOTALS: dict[tuple[str, str], int] = {
    ("A1", "direct"): 21,
    ("A2", "mh"): 34,
    ("A2", "mb"): 106,
    ("A3", "direct"): 60,
    ("B1", "direct"): 86,
    ("B2", "direct"): 236,
    ("BG1", "direct"): 8,
    ("BG2", "direct"): 32,
    ("BC1", "direct"): 60,
    ("BT2", "direct"): 137,
}


def adopted_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for partition_id in SCHEDULE_IDS:
        for cell in WILDCARD_CELLS[partition_id]:
            cell_id = str(cell["cell_id"])
            event_id = partition_id if cell_id == "direct" else f"{partition_id}-{cell_id}"
            events.append(
                {
                    "event_id": event_id,
                    "partition_id": partition_id,
                    "cell_id": cell_id,
                    "branch": str(cell["branch"]),
                    "query": str(cell["query"]),
                    "pilot004_reference_total": PILOT004_REFERENCE_TOTALS[
                        (partition_id, cell_id)
                    ],
                }
            )
    return events


ADOPTED_EVENTS = adopted_events()
EXPECTED_EVENT_IDS = (
    "A1",
    "A2-mh",
    "A2-mb",
    "A3",
    "B1",
    "B2",
    "BG1",
    "BG2",
    "BC1",
    "BT2",
)

assert tuple(item["event_id"] for item in ADOPTED_EVENTS) == EXPECTED_EVENT_IDS
assert len(ADOPTED_EVENTS) == 10
assert all(len(item["query"]) <= SOURCE_QUERY_LIMIT for item in ADOPTED_EVENTS)
assert all("NEAR" not in item["query"].upper() for item in ADOPTED_EVENTS)
assert all(
    all(candidate in item["query"] for _terms, candidate in WILDCARD_REPLACEMENTS)
    for item in ADOPTED_EVENTS
)
