"""Pinned Pilot 004 query translation reused after the NTRS state-race repair."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

EXPECTED_QUERY_MODULE_SHA256 = (
    "c2abe607cc44b4cdf3baaaa133c7d1b312264a5e415f8568f0cf80aa5f70d1d1"
)
QUERY_MODULE_PATH = Path(__file__).resolve().parents[1] / "ntrs_pilot004" / "queries.py"

if hashlib.sha256(QUERY_MODULE_PATH.read_bytes()).hexdigest() != EXPECTED_QUERY_MODULE_SHA256:
    raise RuntimeError("The predeclared NTRS query translation changed")
_spec = importlib.util.spec_from_file_location("ntrs_pilot005_queries", QUERY_MODULE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {QUERY_MODULE_PATH}")
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

PROTOCOL_COMMIT = _module.PROTOCOL_COMMIT
SCHEDULE_IDS = _module.SCHEDULE_IDS
TERM_SNAPSHOT_PATH = _module.TERM_SNAPSHOT_PATH
TERM_SNAPSHOT_SHA256 = _module.TERM_SNAPSHOT_SHA256
TERM_BLOCKS = _module.TERM_BLOCKS
WILDCARD_REPLACEMENTS = _module.WILDCARD_REPLACEMENTS
WILDCARD_ATOM_COUNT = _module.WILDCARD_ATOM_COUNT
REPLACED_LITERAL_COUNT = _module.REPLACED_LITERAL_COUNT
LITERAL_SCHEDULE = _module.LITERAL_SCHEDULE
WILDCARD_SCHEDULE = _module.WILDCARD_SCHEDULE

assert PROTOCOL_COMMIT == "3194156e90497186664260a8e86435e78d2e2aa1"
assert WILDCARD_ATOM_COUNT == 26
assert REPLACED_LITERAL_COUNT == 88
