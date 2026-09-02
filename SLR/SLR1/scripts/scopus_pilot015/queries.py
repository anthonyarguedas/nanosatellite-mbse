"""Canonical literal Scopus queries for the current four-part PSR schedule.

The main concept membership and compound Boolean definitions are pinned to
protocol commit 3194156e90497186664260a8e86435e78d2e2aa1. The X and Q terms
are pinned to the current supporting protocol. Every source atom is literal.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
PSR_IDS = ("PSR1", "PSR2", "PSR3", "PSR4")
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
MAIN_QUERY_SNAPSHOT = (
    REPOSITORY_ROOT / "SLR/SLR1/scripts/scopus_pilot009/queries.py"
)
EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256 = (
    "80cc146dc25641c473e805b4d34a35dea40f6483888a4936b9f8615c1e2722af"
)
SUPPORTING_PROTOCOL = (
    REPOSITORY_ROOT / "SLR/SLR1/protocol-prior-secondary-reviews.md"
)
EXPECTED_SUPPORTING_PROTOCOL_SHA256 = (
    "b657f04bfd8ee0a2e49643c76521f5436436f744fc520e466528d6a4898e1920"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(MAIN_QUERY_SNAPSHOT) != EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256:
    raise RuntimeError("The accepted Scopus main-query snapshot changed")
if digest(SUPPORTING_PROTOCOL) != EXPECTED_SUPPORTING_PROTOCOL_SHA256:
    raise RuntimeError("The supporting PSR protocol changed")

_spec = importlib.util.spec_from_file_location(
    "scopus_pilot014_main_queries", MAIN_QUERY_SNAPSHOT
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {MAIN_QUERY_SNAPSHOT}")
_main = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _main
_spec.loader.exec_module(_main)
if _main.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The main query snapshot uses a different protocol commit")

# The supporting protocol defines X as P plus this declared list. Four entries
# already occur in P. Ordered deduplication keeps one source atom per literal.
X_DECLARED_ADDITIONS = (
    "spacecraft",
    "space system",
    "space systems",
    "space mission",
    "space missions",
    "space engineering",
    "space systems engineering",
    "space application",
    "space applications",
    "space sector",
    "space industry",
    "satellite",
    "satellites",
    "SmallSat",
    "SmallSats",
    "small satellite",
    "small satellites",
)
Q_TERMS = (
    "systematic review",
    "systematic literature review",
    "systematic mapping",
    "systematic mapping study",
    "mapping study",
    "scoping review",
    "literature review",
    "literature survey",
    "bibliometric review",
    "bibliometric analysis",
    "evidence synthesis",
    "secondary study",
    "state-of-the-art review",
    "state of the art review",
    "survey paper",
    "survey",
)

P_TERMS = tuple(_main._terms.P_TERMS)
X_TERMS = tuple(dict.fromkeys((*P_TERMS, *X_DECLARED_ADDITIONS)))
X_BLOCK = _main.ordinary_block(X_TERMS)
Q_BLOCK = _main.ordinary_block(Q_TERMS)
B = _main.ORDINARY_BLOCKS
C = _main.COMPOUND_BLOCKS

PSR_SCHEDULE = {
    "PSR1": _main.all_of(X_BLOCK, B["M_H"], Q_BLOCK),
    "PSR2": _main.all_of(X_BLOCK, B["M_B"], B["R"], Q_BLOCK),
    "PSR3": _main.all_of(
        B["P"],
        _main.any_of(B["E_H"], B["E_F"]),
        _main.any_of(B["M_H"], B["M_B"]),
        Q_BLOCK,
    ),
    "PSR4": _main.all_of(
        X_BLOCK,
        _main.any_of(C["G_model"], C["G_structure"], C["C1"]),
        Q_BLOCK,
    ),
}

TERM_COUNTS = {
    **_main.TERM_COUNTS,
    "X": len(X_TERMS),
    "Q": len(Q_TERMS),
}
QUERY_CHARACTER_COUNTS = {
    key: len(query) for key, query in PSR_SCHEDULE.items()
}
QUERY_SHA256 = {
    key: hashlib.sha256(query.encode("utf-8")).hexdigest()
    for key, query in PSR_SCHEDULE.items()
}

assert len(P_TERMS) == 26
assert len(X_DECLARED_ADDITIONS) == 17
assert len(X_TERMS) == 39
assert len(Q_TERMS) == 16
assert tuple(PSR_SCHEDULE) == PSR_IDS
assert all(
    marker not in query.upper()
    for query in PSR_SCHEDULE.values()
    for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR")
)
assert all("*" not in query and "?" not in query for query in PSR_SCHEDULE.values())
assert all(query.count('TITLE-ABS-KEY("') > 0 for query in PSR_SCHEDULE.values())
