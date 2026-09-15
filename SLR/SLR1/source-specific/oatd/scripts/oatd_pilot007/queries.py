"""Pinned OATD Pilot 007 gate declarations."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parents[1] / "oatd_pilot006/queries.py"
EXPECTED_BASE_SHA256 = (
    "c447b9c04f60edf65889d78a7a0727749fc1ef76e555695b03d2e44d09d49069"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(BASE_PATH) != EXPECTED_BASE_SHA256:
    raise RuntimeError("The reviewed OATD Pilot 006 gate declarations changed")
_spec = importlib.util.spec_from_file_location("oatd_pilot007_base_queries", BASE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Cannot load {BASE_PATH}")
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)

PROTOCOL_COMMIT = _base.PROTOCOL_COMMIT
GATE_IDS = _base.GATE_IDS
GATE_QUERIES = _base.GATE_QUERIES
EXPECTED_COUNTS = _base.EXPECTED_PILOT005_COUNTS
PARTITION_BRANCH_COVERAGE = _base.PARTITION_BRANCH_COVERAGE
ALGEBRAIC_IDENTITY = _base.ALGEBRAIC_IDENTITY

assert tuple(GATE_QUERIES) == GATE_IDS
assert tuple(EXPECTED_COUNTS) == GATE_IDS
