"""Web of Science literal and population-wildcard PSR queries."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
PSR_IDS = ("PSR1", "PSR2", "PSR3", "PSR4")
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
MAIN_QUERY_PATH = REPOSITORY_ROOT / "SLR/SLR1/scripts/wos_pilot004/queries.py"
SUPPORTING_PROTOCOL_PATH = REPOSITORY_ROOT / "SLR/SLR1/protocol-prior-secondary-reviews.md"
EXPECTED_MAIN_QUERY_SHA256 = "5f4b3e47f6e775eb34ed8fcfb68cd8b80eebd22f3698275381aeac2d82ac623e"
EXPECTED_SUPPORTING_PROTOCOL_SHA256 = "b657f04bfd8ee0a2e49643c76521f5436436f744fc520e466528d6a4898e1920"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if file_sha256(MAIN_QUERY_PATH) != EXPECTED_MAIN_QUERY_SHA256:
    raise RuntimeError("The accepted Web of Science main-query snapshot changed")
if file_sha256(SUPPORTING_PROTOCOL_PATH) != EXPECTED_SUPPORTING_PROTOCOL_SHA256:
    raise RuntimeError("The supporting-search protocol changed")

_spec = importlib.util.spec_from_file_location("wos_pilot006_main_queries", MAIN_QUERY_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not load {MAIN_QUERY_PATH}")
_main = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _main
_spec.loader.exec_module(_main)
if _main.PROTOCOL_COMMIT != PROTOCOL_COMMIT:
    raise RuntimeError("The main-query snapshot uses a different protocol commit")

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
WILDCARD_REPLACEMENTS = tuple(_main.WILDCARD_REPLACEMENTS)
X_TERMS = tuple(dict.fromkeys((*P_TERMS, *X_DECLARED_ADDITIONS)))
Q_BLOCK = _main.ordinary_block(Q_TERMS)
X_LITERAL_BLOCK = _main.ordinary_block(X_TERMS)


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
P_LITERAL_BLOCK = _main.P_LITERAL
P_WILDCARD_BLOCK = _main.P_WILDCARD
B = _main.ORDINARY_BLOCKS
C = _main.COMPOUND_BLOCKS
E_BLOCK = _main.any_of(B["E_H"], B["E_F"])
M_BLOCK = C["M"]
ARTIFACT_BLOCK = _main.any_of(C["G_model"], C["G_structure"], C["C1"])


def schedule(*, x_block: str, p_block: str) -> dict[str, str]:
    semantic = {
        "PSR1": _main.all_of(x_block, B["M_H"], Q_BLOCK),
        "PSR2": _main.all_of(x_block, B["M_B"], B["R"], Q_BLOCK),
        "PSR3": _main.all_of(p_block, E_BLOCK, M_BLOCK, Q_BLOCK),
        "PSR4": _main.all_of(x_block, ARTIFACT_BLOCK, Q_BLOCK),
    }
    return {
        key: f"{value} AND PY=(1900-2026)" for key, value in semantic.items()
    }


LITERAL_SCHEDULE = schedule(x_block=X_LITERAL_BLOCK, p_block=P_LITERAL_BLOCK)
WILDCARD_SCHEDULE = schedule(x_block=X_WILDCARD_BLOCK, p_block=P_WILDCARD_BLOCK)
TERM_COUNTS = {**_main.TERM_COUNTS, "X": len(X_TERMS), "Q": len(Q_TERMS)}

assert len(P_TERMS) == 26
assert len(X_TERMS) == 39
assert len(Q_TERMS) == 16
assert len(WILDCARD_REPLACEMENTS) == 10
assert tuple(LITERAL_SCHEDULE) == PSR_IDS
assert tuple(WILDCARD_SCHEDULE) == PSR_IDS
assert all("NEAR" not in query.upper() and " SAME " not in query.upper() for query in (*LITERAL_SCHEDULE.values(), *WILDCARD_SCHEDULE.values()))
assert all("*" not in query and "?" not in query for query in LITERAL_SCHEDULE.values())
assert all(query.count("*") == 10 and "?" not in query for query in WILDCARD_SCHEDULE.values())
assert all("LA=(" not in query and "DT=(" not in query for query in (*LITERAL_SCHEDULE.values(), *WILDCARD_SCHEDULE.values()))
assert all(len(LITERAL_SCHEDULE[key]) - len(WILDCARD_SCHEDULE[key]) == 255 for key in PSR_IDS)
