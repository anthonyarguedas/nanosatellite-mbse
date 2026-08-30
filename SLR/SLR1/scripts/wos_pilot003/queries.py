"""Deterministic Web of Science Pilot 003 query plan.

The shared pilot_schedule module is the normative source for the literal
concepts, declared pairs, and 13 semantic partitions.  This module adds only
the Web of Science raw-query controls and Pilot 002's accepted A1 population
wildcard translation.  It never changes a non-A1 partition.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[1]
PILOT_SCHEDULE_PATH = SLR1_DIR / "scripts" / "pilot_schedule" / "queries.py"

_spec = spec_from_file_location("slr1_pilot_schedule_queries", PILOT_SCHEDULE_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise RuntimeError(f"Could not load {PILOT_SCHEDULE_PATH}")
pilot_schedule = module_from_spec(_spec)
sys.modules[_spec.name] = pilot_schedule
_spec.loader.exec_module(pilot_schedule)

SOURCE_ID = "web_of_science_core_collection"
SOURCE_LABEL = "Web of Science Core Collection"
PILOT_NUMBER = "003"
DIAGNOSTIC_CUTOFF = "2026-08-29"
MAIN_IDS = tuple(pilot_schedule.MAIN_FACTORS)
PSR_IDS = tuple(pilot_schedule.PSR_FACTORS)
RENDERER = pilot_schedule.RENDERERS[SOURCE_ID]

# Pilot 002 proved these exact ten wildcard atoms to be a complete stable-ID
# superset of literal A1 under identical raw PY/LA controls.  The remaining
# four P literals deliberately stay literal.  This exception is scoped to A1.
A1_WILDCARD_REPLACEMENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("CubeSat*", ("CubeSat", "CubeSats")),
    ("cube sat*", ("cube sat", "cube sats")),
    ("cube-sat*", ("cube-sat", "cube-sats")),
    ("cube satellite*", ("cube satellite", "cube satellites")),
    ("nanosat*", ("nanosat", "nanosats", "nanosatellite", "nanosatellites")),
    ("nano-sat*", ("nano-sat", "nano-sats")),
    ("nano sat*", ("nano sat", "nano sats")),
    ("nano-satellite*", ("nano-satellite", "nano-satellites")),
    ("nano satellite*", ("nano satellite", "nano satellites")),
    ("SmallSat*", ("SmallSat", "SmallSats")),
)
A1_LITERAL_POPULATION_REMAINDER = (
    "small satellite",
    "small satellites",
    "small sat",
    "small sats",
)

MAIN_RAW_CONTROL = "PY=(2011-2026) AND LA=(English)"
# This is the current Core Collection source-inception bound used in Pilot 001,
# not a protocol lower-date restriction.  It is needed to apply the shared
# diagnostic upper year while retaining all source-available earlier reviews.
PSR_RAW_CONTROL = "PY=(1900-2026)"


@dataclass(frozen=True)
class PilotEvent:
    """One raw source event; no event is a final search."""

    namespace: str
    partition_id: str
    semantic_query: str
    executed_query: str
    output_relative_path: str
    raw_control: str
    translation: str

    @property
    def query_sha256(self) -> str:
        return sha256(self.executed_query.encode("utf-8")).hexdigest()

    def json(self) -> dict[str, Any]:
        value = asdict(self)
        value["query_sha256"] = self.query_sha256
        value["diagnostic_cutoff"] = DIAGNOSTIC_CUTOFF
        value["event_kind"] = "pilot"
        value["do_not_merge"] = True
        return value


def _union(atoms: Iterable[str]) -> str:
    values = tuple(atoms)
    if not values:
        raise ValueError("A Web of Science OR block cannot be empty")
    return "(" + " OR ".join(values) + ")"


def _a1_wildcard_population_block() -> str:
    wildcard_atoms = [RENDERER.literal_atom(value) for value, _ in A1_WILDCARD_REPLACEMENTS]
    literal_atoms = [RENDERER.literal_atom(value) for value in A1_LITERAL_POPULATION_REMAINDER]
    return _union((*wildcard_atoms, *literal_atoms))


def _literal_population_block() -> str:
    return RENDERER.union(RENDERER.alternatives(("P",)))


def semantic_query(partition_id: str, namespace: str) -> str:
    """Return the unfiltered Web of Science Topic expression for one event."""
    expected = MAIN_IDS if namespace == "main" else PSR_IDS
    if partition_id not in expected:
        raise ValueError(f"{partition_id} is not a {namespace} Pilot 003 partition")
    literal = pilot_schedule.partition_query(SOURCE_ID, partition_id)
    if namespace == "main" and partition_id == "A1":
        literal_population = _literal_population_block()
        if not literal.startswith(literal_population + " AND "):
            raise AssertionError("Pilot-schedule A1 no longer begins with the P block")
        return _a1_wildcard_population_block() + literal[len(literal_population) :]
    return literal


def raw_control(namespace: str) -> str:
    if namespace == "main":
        return MAIN_RAW_CONTROL
    if namespace == "psr":
        return PSR_RAW_CONTROL
    raise ValueError(f"Unknown Pilot 003 namespace: {namespace}")


def executed_query(partition_id: str, namespace: str) -> str:
    return f"{semantic_query(partition_id, namespace)} AND {raw_control(namespace)}"


def event(namespace: str, partition_id: str) -> PilotEvent:
    if namespace not in {"main", "psr"}:
        raise ValueError(f"Unknown Pilot 003 namespace: {namespace}")
    translation = (
        "Pilot 002 accepted 10-wildcard A1 population translation"
        if namespace == "main" and partition_id == "A1"
        else "literal pilot_schedule translation"
    )
    return PilotEvent(
        namespace=namespace,
        partition_id=partition_id,
        semantic_query=semantic_query(partition_id, namespace),
        executed_query=executed_query(partition_id, namespace),
        output_relative_path=f"searches/{namespace}/{partition_id}.json",
        raw_control=raw_control(namespace),
        translation=translation,
    )


def events() -> tuple[PilotEvent, ...]:
    return tuple(event("main", partition_id) for partition_id in MAIN_IDS) + tuple(
        event("psr", partition_id) for partition_id in PSR_IDS
    )


def event_by_name(namespace: str, partition_id: str) -> PilotEvent:
    return event(namespace, partition_id)


def _concept_atoms(concept_names: Iterable[str]) -> tuple[str, ...]:
    return RENDERER.alternatives(concept_names)


def _pairs_for_partition(partition_id: str) -> tuple[tuple[str, str], ...]:
    factors = pilot_schedule.SCHEDULE_FACTORS[partition_id]
    pairs: list[tuple[str, str]] = []
    for factor in factors:
        for concept_name in factor:
            pairs.extend(pilot_schedule.CONCEPTS[concept_name].pairs)
    return tuple(pairs)


def query_membership_errors() -> list[str]:
    """Validate exact schedule membership, pair rendering, and control scope."""
    errors: list[str] = []
    expected_replaced = {
        literal
        for _wildcard, literals in A1_WILDCARD_REPLACEMENTS
        for literal in literals
    }
    expected_population = set(pilot_schedule.CONCEPTS["P"].literals)
    if expected_replaced | set(A1_LITERAL_POPULATION_REMAINDER) != expected_population:
        errors.append("A1 wildcard/remainder literals do not reconstruct P exactly")
    if len(expected_replaced) != 22:
        errors.append("A1 wildcard translation does not replace exactly 22 literals")

    for item in events():
        query = item.semantic_query
        complete = item.executed_query
        factors = pilot_schedule.SCHEDULE_FACTORS[item.partition_id]
        if not query or not complete.endswith(item.raw_control):
            errors.append(f"{item.namespace}/{item.partition_id}: raw control missing")
        if not all(atom.startswith("TS=(") for factor in factors for atom in _concept_atoms(factor)):
            errors.append(f"{item.namespace}/{item.partition_id}: non-Topic atom generated")
        if item.namespace == "main":
            if MAIN_RAW_CONTROL not in complete or "LA=(English)" not in complete:
                errors.append(f"{item.partition_id}: main PY/LA control missing")
            if "DT=(" in complete:
                errors.append(f"{item.partition_id}: prohibited DT candidate union present")
        else:
            if PSR_RAW_CONTROL not in complete:
                errors.append(f"{item.partition_id}: PSR upper-year control missing")
            if "LA=(" in complete or "DT=(" in complete:
                errors.append(f"{item.partition_id}: PSR has prohibited language/type control")

        # Every literal and pair remains present except the explicit A1 P
        # literals replaced by the accepted wildcard atoms.
        for factor in factors:
            for concept_name in factor:
                concept = pilot_schedule.CONCEPTS[concept_name]
                for literal in concept.literals:
                    atom = RENDERER.literal_atom(literal)
                    replaced = (
                        item.namespace == "main"
                        and item.partition_id == "A1"
                        and concept_name == "P"
                        and literal in expected_replaced
                    )
                    if not replaced and atom not in query:
                        errors.append(
                            f"{item.namespace}/{item.partition_id}: missing literal {concept_name}/{literal}"
                        )
                for left, right in concept.pairs:
                    atom = RENDERER.pair_atom(left, right)
                    if atom not in query:
                        errors.append(
                            f"{item.namespace}/{item.partition_id}: missing pair {concept_name}/{left}|{right}"
                        )

        wildcard_count = query.count("*")
        if item.namespace == "main" and item.partition_id == "A1":
            if wildcard_count != len(A1_WILDCARD_REPLACEMENTS):
                errors.append("A1 does not contain exactly the accepted 10 wildcards")
            for wildcard, literals in A1_WILDCARD_REPLACEMENTS:
                atom = RENDERER.literal_atom(wildcard)
                if atom not in query:
                    errors.append(f"A1 missing accepted wildcard atom {atom}")
                for literal in literals:
                    if RENDERER.literal_atom(literal) in query:
                        errors.append(f"A1 retained replaced literal {literal}")
            for literal in A1_LITERAL_POPULATION_REMAINDER:
                if RENDERER.literal_atom(literal) not in query:
                    errors.append(f"A1 lost literal population remainder {literal}")
        elif wildcard_count:
            errors.append(f"{item.namespace}/{item.partition_id}: unvalidated wildcard present")

        for left, right in _pairs_for_partition(item.partition_id):
            atom = RENDERER.pair_atom(left, right)
            if " NEAR/6 " not in atom:
                errors.append(f"{item.partition_id}: pair does not use NEAR/6: {left}|{right}")
    return errors


def audit() -> dict[str, Any]:
    errors = query_membership_errors()
    return {
        "schema_version": "slr1-wos-pilot-003-query-plan/v1",
        "source": SOURCE_LABEL,
        "source_id": SOURCE_ID,
        "pilot": PILOT_NUMBER,
        "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
        "main_partition_order": list(MAIN_IDS),
        "psr_partition_order": list(PSR_IDS),
        "events": [item.json() for item in events()],
        "a1_wildcard_exception": {
            "scope": "A1 only",
            "wildcard_count": len(A1_WILDCARD_REPLACEMENTS),
            "replaced_literal_count": sum(
                len(literals) for _wildcard, literals in A1_WILDCARD_REPLACEMENTS
            ),
            "remaining_literal_count": len(A1_LITERAL_POPULATION_REMAINDER),
            "replacements": [
                {"atom": RENDERER.literal_atom(wildcard), "literals": list(literals)}
                for wildcard, literals in A1_WILDCARD_REPLACEMENTS
            ],
            "evidence": "Pilot 002 coverage-receipt.json: complete stable-ID superset under identical PY/LA controls.",
        },
        "pair_rendering": "TS=(\"left\" NEAR/6 \"right\") for every declared pair; local retained-field audit tests the stricter <=5-token intent where observable.",
        "membership_check": {"status": "ok" if not errors else "failed", "errors": errors},
        "do_not_merge": True,
    }


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps(audit(), indent=2, ensure_ascii=False))
