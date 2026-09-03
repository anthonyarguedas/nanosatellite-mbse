"""Current literal Scopus queries for final prior-secondary-review searches."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
CONCEPT_SCHEDULE_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
MAIN_QUERY_SNAPSHOT = (
    REPOSITORY_ROOT / "SLR/SLR1/scripts/scopus_pilot009/queries.py"
)
SUPPORTING_PROTOCOL = (
    REPOSITORY_ROOT / "SLR/SLR1/protocol-prior-secondary-reviews.md"
)
DISCOVERY_PROTOCOL = (
    REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
)
EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256 = (
    "80cc146dc25641c473e805b4d34a35dea40f6483888a4936b9f8615c1e2722af"
)
EXPECTED_SUPPORTING_PROTOCOL_SHA256 = (
    "76874b89da5081f227913ee48e9f302ef47da4f25f2e521a8d74b23df125a834"
)
EXPECTED_DISCOVERY_PROTOCOL_SHA256 = (
    "3263eb867a3c4c39b53342513bdfc326ecc0b484086327dd0ee59afee06ccd76"
)
PSR_IDS = ("PSR1", "PSR2", "PSR3", "PSR4")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(MAIN_QUERY_SNAPSHOT) != EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256:
    raise RuntimeError("The accepted Scopus main-query snapshot changed")
if digest(SUPPORTING_PROTOCOL) != EXPECTED_SUPPORTING_PROTOCOL_SHA256:
    raise RuntimeError("The supporting PSR protocol changed")
if digest(DISCOVERY_PROTOCOL) != EXPECTED_DISCOVERY_PROTOCOL_SHA256:
    raise RuntimeError("The discovery protocol changed")

_spec = importlib.util.spec_from_file_location(
    "scopus_psr_final_main_queries", MAIN_QUERY_SNAPSHOT
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {MAIN_QUERY_SNAPSHOT}")
_main = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _main
_spec.loader.exec_module(_main)
if _main.PROTOCOL_COMMIT != CONCEPT_SCHEDULE_COMMIT:
    raise RuntimeError("The main query snapshot uses a different concept schedule")

# The current supporting protocol defines X as P plus these 13 additions.
# P already includes SmallSat, SmallSats, small satellite, and small satellites.
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
    partition: len(query) for partition, query in PSR_SCHEDULE.items()
}
QUERY_SHA256 = {
    partition: hashlib.sha256(query.encode("utf-8")).hexdigest()
    for partition, query in PSR_SCHEDULE.items()
}
EXPECTED_QUERY_SHA256 = {
    "PSR1": "9b1edfc3dc21ec0ad0376b9d32991858bfb28fdd09b4ca69683988f671d2a503",
    "PSR2": "5b63e7b2e0da9069cf59110527d220c24de1368966d104f0d86bd3e0242dcc11",
    "PSR3": "04bd61d531d250c27b9ff89d678cd2d40d826e293de8c6f810fcc641afa38cfe",
    "PSR4": "139510662b578fdcb8ba3a7b1edf81824cbee0f4f5a83101dbdbad525d9c6488",
}

assert len(P_TERMS) == 26
assert len(X_DECLARED_ADDITIONS) == 13
assert len(X_TERMS) == 39
assert len(Q_TERMS) == 16
assert tuple(PSR_SCHEDULE) == PSR_IDS
assert QUERY_SHA256 == EXPECTED_QUERY_SHA256
assert all(
    marker not in query.upper()
    for query in PSR_SCHEDULE.values()
    for marker in (" W/", " PRE/", " NEAR/", "DOCTYPE(", "PUBYEAR")
)
assert all("*" not in query and "?" not in query for query in PSR_SCHEDULE.values())
assert all(query.count('TITLE-ABS-KEY("') > 0 for query in PSR_SCHEDULE.values())
