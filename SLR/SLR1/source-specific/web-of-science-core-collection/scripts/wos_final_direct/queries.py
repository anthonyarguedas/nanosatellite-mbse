"""Accepted Web of Science Core Collection direct-search queries."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/source-specific/web-of-science-core-collection/scripts/wos_pilot004/queries.py"
EXPECTED_QUERY_SNAPSHOT_SHA256 = (
    "5b0120b1ed9f7b49e4c12c0b93cb823a01bc4f59451369efd5f01a158dcfd2be"
)
PARTITIONS = ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2", "BC1", "BT2")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(QUERY_SNAPSHOT) != EXPECTED_QUERY_SNAPSHOT_SHA256:
    raise RuntimeError("The accepted Web of Science direct-query snapshot changed")

_spec = importlib.util.spec_from_file_location("wos_final_direct_snapshot", QUERY_SNAPSHOT)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {QUERY_SNAPSHOT}")
_snapshot: Any = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _snapshot
_spec.loader.exec_module(_snapshot)

if tuple(_snapshot.SCHEDULE_IDS) != PARTITIONS:
    raise RuntimeError("The accepted Web of Science partition schedule changed")

CONCEPT_SCHEDULE_COMMIT = _snapshot.PROTOCOL_COMMIT
TERM_COUNTS = dict(_snapshot.TERM_COUNTS)
WILDCARD_REPLACEMENTS = tuple(_snapshot.WILDCARD_REPLACEMENTS)
WILDCARD_SCHEDULE = dict(_snapshot.WILDCARD_SCHEDULE)
QUERY_SHA256 = {
    partition: hashlib.sha256(query.encode("utf-8")).hexdigest()
    for partition, query in WILDCARD_SCHEDULE.items()
}
QUERY_CHARACTER_COUNTS = {
    partition: len(query) for partition, query in WILDCARD_SCHEDULE.items()
}

assert tuple(WILDCARD_SCHEDULE) == PARTITIONS
assert len(WILDCARD_REPLACEMENTS) == 10
assert all(query.count("*") == 10 for query in WILDCARD_SCHEDULE.values())
assert all(
    query.endswith(" AND PY=(2011-2026) AND LA=(English)")
    for query in WILDCARD_SCHEDULE.values()
)
assert all(
    marker not in query.upper()
    for query in WILDCARD_SCHEDULE.values()
    for marker in ("NEAR", " SAME ", "DT=(", "?")
)
