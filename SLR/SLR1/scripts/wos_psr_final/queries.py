"""Current wildcard Web of Science queries for final prior-secondary-review searches."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
CONCEPT_SCHEDULE_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
MAIN_QUERY_SNAPSHOT = REPOSITORY_ROOT / "SLR/SLR1/scripts/wos_pilot004/queries.py"
SUPPORTING_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-prior-secondary-reviews.md"
DISCOVERY_PROTOCOL = REPOSITORY_ROOT / "SLR/SLR1/protocol-discovery-and-screening.md"
EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256 = (
    "5f4b3e47f6e775eb34ed8fcfb68cd8b80eebd22f3698275381aeac2d82ac623e"
)
EXPECTED_SUPPORTING_PROTOCOL_SHA256 = (
    "d6f28bf8f81154a86f2723fe7dabd32859c25f130d13fbfe7d88cd4f0af99292"
)
EXPECTED_DISCOVERY_PROTOCOL_SHA256 = (
    "660b2cb623bc1445fedf14c8d19bce36b96f39ff3b5dcae923d66d152276cfda"
)
PSR_IDS = ("PSR1", "PSR2", "PSR3", "PSR4")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if digest(MAIN_QUERY_SNAPSHOT) != EXPECTED_MAIN_QUERY_SNAPSHOT_SHA256:
    raise RuntimeError("The accepted Web of Science main-query snapshot changed")
if digest(SUPPORTING_PROTOCOL) != EXPECTED_SUPPORTING_PROTOCOL_SHA256:
    raise RuntimeError("The supporting PSR protocol changed")
if digest(DISCOVERY_PROTOCOL) != EXPECTED_DISCOVERY_PROTOCOL_SHA256:
    raise RuntimeError("The discovery protocol changed")

_spec = importlib.util.spec_from_file_location(
    "wos_final_psr_main_queries", MAIN_QUERY_SNAPSHOT
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Cannot load {MAIN_QUERY_SNAPSHOT}")
_main = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _main
_spec.loader.exec_module(_main)
if _main.PROTOCOL_COMMIT != CONCEPT_SCHEDULE_COMMIT:
    raise RuntimeError("The main query snapshot uses a different concept schedule")

# The current supporting protocol defines X as P plus these 13 additions.
# Four former X additions already occur in P and therefore remain represented.
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
WILDCARD_REPLACEMENTS = tuple(_main.WILDCARD_REPLACEMENTS)
X_TERMS = tuple(dict.fromkeys((*P_TERMS, *X_DECLARED_ADDITIONS)))
Q_BLOCK = _main.ordinary_block(Q_TERMS)
X_WILDCARD_BLOCK: str


def wildcard_x_block() -> str:
    replacement_by_first = {
        item["replaced_literals"][0]: item for item in WILDCARD_REPLACEMENTS
    }
    replaced = {
        value
        for item in WILDCARD_REPLACEMENTS
        for value in item["replaced_literals"]
    }
    atoms: list[str] = []
    covered: set[str] = set()
    for value in X_TERMS:
        replacement = replacement_by_first.get(value)
        if replacement is not None:
            atoms.append(_main.literal_atom(replacement["candidate"]))
            covered.update(replacement["replaced_literals"])
        elif value in replaced:
            if value not in covered:
                raise RuntimeError("An X wildcard family changed protocol term order")
        else:
            atoms.append(_main.literal_atom(value))
    if covered != replaced:
        raise RuntimeError("The X wildcard block omitted a population family")
    return _main.any_of(*atoms)


X_WILDCARD_BLOCK = wildcard_x_block()
P_WILDCARD_BLOCK = _main.P_WILDCARD
B = _main.ORDINARY_BLOCKS
C = _main.COMPOUND_BLOCKS
E_BLOCK = _main.any_of(B["E_H"], B["E_F"])
M_BLOCK = C["M"]
ARTIFACT_BLOCK = _main.any_of(C["G_model"], C["G_structure"], C["C1"])

PSR_SCHEDULE = {
    "PSR1": _main.all_of(X_WILDCARD_BLOCK, B["M_H"], Q_BLOCK) + " AND PY=(1900-2026)",
    "PSR2": _main.all_of(X_WILDCARD_BLOCK, B["M_B"], B["R"], Q_BLOCK) + " AND PY=(1900-2026)",
    "PSR3": _main.all_of(P_WILDCARD_BLOCK, E_BLOCK, M_BLOCK, Q_BLOCK) + " AND PY=(1900-2026)",
    "PSR4": _main.all_of(X_WILDCARD_BLOCK, ARTIFACT_BLOCK, Q_BLOCK) + " AND PY=(1900-2026)",
}

TERM_COUNTS = {**_main.TERM_COUNTS, "X": len(X_TERMS), "Q": len(Q_TERMS)}
QUERY_CHARACTER_COUNTS = {
    partition: len(query) for partition, query in PSR_SCHEDULE.items()
}
QUERY_SHA256 = {
    partition: hashlib.sha256(query.encode("utf-8")).hexdigest()
    for partition, query in PSR_SCHEDULE.items()
}
EXPECTED_QUERY_SHA256 = {
    "PSR1": "44b69368f6362fe93b9ac91678275085dee55cf6d94d6fc158b7cf7fa85044dc",
    "PSR2": "65c6ff8f583b1d9aadcdbd1dbe3f3dc9bb6dc4109971068eb4849d539e0f62e6",
    "PSR3": "ed3001408f77cee598339cb071d67fb390123ba6d2995bb22d18fe4d982512f5",
    "PSR4": "ae25a71f837089712dadfa4a4d07c6df2a15adf6ec3f684cea62ec8549dc2a07",
}

assert len(P_TERMS) == 26
assert len(X_DECLARED_ADDITIONS) == 13
assert len(X_TERMS) == 39
assert len(Q_TERMS) == 16
assert len(WILDCARD_REPLACEMENTS) == 10
assert tuple(PSR_SCHEDULE) == PSR_IDS
assert QUERY_SHA256 == EXPECTED_QUERY_SHA256
assert all(query.count("*") == 10 for query in PSR_SCHEDULE.values())
assert all(
    marker not in query.upper()
    for query in PSR_SCHEDULE.values()
    for marker in ("NEAR", " SAME ", "LA=(", "DT=(")
)
assert all("?" not in query and "$" not in query for query in PSR_SCHEDULE.values())
assert all(query.endswith(" AND PY=(1900-2026)") for query in PSR_SCHEDULE.values())
