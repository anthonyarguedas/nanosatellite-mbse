#!/usr/bin/env python3
"""Build the predeclared positive wildcard plan for IAF Pilot 005."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PILOT = "005"
PROTOCOL_COMMIT = "3194156e90497186664260a8e86435e78d2e2aa1"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
MAX_QUERY_CHARACTERS = 500
SCHEMA = "iaf-digital-library-pilot005-event-plan/v1"

SCRIPT_DIR = Path(__file__).resolve().parent
SLR1_DIR = SCRIPT_DIR.parents[3]
PILOT_ROOT = SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / PILOT
DEFAULT_OUTPUT = PILOT_ROOT / "searches" / "event-plan.json"
PILOT004_ROOT = SLR1_DIR / "source-specific" / "iaf-digital-library" / "pilots" / "004"
PILOT004_PLAN = PILOT004_ROOT / "searches" / "cell-plan.json"

WILDCARD_CUBE_ATOMS = ("CubeSat*", '"cube sat*"', "cube-sat*")
WILDCARD_OTHER_ATOMS = (
    "nanosat*",
    "nano-sat*",
    '"nano sat*"',
    "SmallSat*",
    '"small sat*"',
)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def union(atoms: tuple[str, ...]) -> str:
    return "(" + " OR ".join(atoms) + ")"


def event(
    event_id: str, purpose: str, query: str, comparison_group: str
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "purpose": purpose,
        "comparison_group": comparison_group,
        "query": query,
        "query_characters": len(query),
        "query_sha256": digest_text(query),
        "mode": "strict_complete",
        "output": f"events/{event_id}.json",
        "diagnostic_only": True,
        "do_not_merge": True,
    }


def build() -> dict[str, Any]:
    pilot004 = load(PILOT004_PLAN)
    fixed_branch = pilot004["partitions"]["BG1"]["branches"][0]
    if (
        fixed_branch.get("branch_id") != "fixed"
        or len(fixed_branch.get("cells", [])) != 3
    ):
        raise RuntimeError("Pilot 004 BG1 fixed-branch evidence changed")
    exact_queries = [cell["query"] for cell in fixed_branch["cells"]]
    _, context_tail = exact_queries[0].split(") (", 1)
    context = "(" + context_tail
    wildcard_cube = f"{union(WILDCARD_CUBE_ATOMS)} {context}"
    wildcard_other = f"{union(WILDCARD_OTHER_ATOMS)} {context}"
    wildcard_full = f"{union(WILDCARD_CUBE_ATOMS + WILDCARD_OTHER_ATOMS)} {context}"

    events = [
        event(
            "exact-cube",
            "Fresh strict baseline for the eight explicit cube population forms.",
            exact_queries[0],
            "cube-family",
        ),
        event(
            "exact-other-a",
            "Fresh strict baseline cell 1 for the other eighteen explicit population forms.",
            exact_queries[1],
            "other-family",
        ),
        event(
            "exact-other-b",
            "Fresh strict baseline cell 2 for the other eighteen explicit population forms.",
            exact_queries[2],
            "other-family",
        ),
        event(
            "wildcard-cube",
            "Positive wildcard candidate for the eight cube population forms.",
            wildcard_cube,
            "cube-family",
        ),
        event(
            "wildcard-other",
            "Positive wildcard candidate for the other eighteen population forms.",
            wildcard_other,
            "other-family",
        ),
        event(
            "wildcard-full-pass1",
            "First strict pass for the full eight-atom wildcard population candidate.",
            wildcard_full,
            "full-population",
        ),
        event(
            "wildcard-full-pass2",
            "Independent strict repeat for the full eight-atom wildcard population candidate.",
            wildcard_full,
            "full-population",
        ),
    ]
    if any(
        event_value["query_characters"] > MAX_QUERY_CHARACTERS for event_value in events
    ):
        raise RuntimeError("A Pilot 005 query exceeds the IAF source limit")
    if any("*" in query for query in exact_queries):
        raise RuntimeError("The explicit baseline unexpectedly contains a wildcard")
    if any("*" not in event_value["query"] for event_value in events[3:]):
        raise RuntimeError("A wildcard candidate lacks wildcard syntax")

    return {
        "schema_version": SCHEMA,
        "pilot": PILOT,
        "source": {"id": "iaf_digital_library", "label": "IAF Digital Library"},
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Compare a positive explicit BG1 fixed-branch population search with "
            "family-specific and full trailing-wildcard candidates using complete stable-ID sets."
        ),
        "date_window": {
            "start": DATE_START,
            "end": DATE_END,
            "inclusive": True,
            "mode": "local post-filter after complete raw traversal",
        },
        "controls": {
            "database_scope": "full IAF Digital Library",
            "language": "not applied",
            "event": "not applied",
            "publication_type": "no added restriction",
            "access": "not applied",
            "source_date": "not applied",
            "controlled_vocabulary": "not applied",
            "proximity": False,
            "pair_expansion": False,
            "complete_source_total_cap": 5000,
            "maximum_query_characters": MAX_QUERY_CHARACTERS,
        },
        "wildcard_candidate": {
            "operator": "trailing *",
            "cube_atoms": list(WILDCARD_CUBE_ATOMS),
            "other_atoms": list(WILDCARD_OTHER_ATOMS),
            "full_atoms": list(WILDCARD_CUBE_ATOMS + WILDCARD_OTHER_ATOMS),
            "full_query_characters": len(wildcard_full),
            "explicit_full_query_characters": len(
                fixed_branch["unsubmitted_branch_query"]
            ),
            "explicit_source_cells": 3,
            "wildcard_source_cells": 1,
        },
        "prior_positive_evidence": {
            "pilot004_plan": str(PILOT004_PLAN.relative_to(SLR1_DIR)),
            "pilot004_plan_sha256": digest_file(PILOT004_PLAN),
            "partition": "BG1",
            "branch": "fixed",
            "source_event_total_sum": 5,
            "raw_stable_id_union": 4,
            "diagnostic_window_stable_id_union": 4,
            "reason_for_selection": (
                "The exact branch was non-zero in Pilot 004 and uses all 26 explicit population terms."
            ),
        },
        "acceptance_checks": [
            "Every event receives exact query readback and strict two-pass complete capture.",
            "Every explicit and wildcard comparison is non-zero.",
            "The fresh explicit baseline reproduces the Pilot 004 stable-ID union.",
            "Each family wildcard set contains its corresponding explicit stable-ID union.",
            "The two full wildcard runs have identical totals, order, and stable IDs.",
            "The full wildcard set contains the complete explicit stable-ID union.",
            "Every wildcard-only record is inspected before any source translation decision.",
        ],
        "events": events,
    }


def validate(payload: dict[str, Any]) -> list[str]:
    errors = []
    if payload.get("schema_version") != SCHEMA:
        errors.append("Plan schema changed")
    events = payload.get("events")
    if not isinstance(events, list) or len(events) != 7:
        return [*errors, "Plan must contain seven events"]
    expected_ids = (
        "exact-cube",
        "exact-other-a",
        "exact-other-b",
        "wildcard-cube",
        "wildcard-other",
        "wildcard-full-pass1",
        "wildcard-full-pass2",
    )
    if tuple(item.get("event_id") for item in events) != expected_ids:
        errors.append("Event order changed")
    for item in events:
        query = item.get("query")
        if not isinstance(query, str) or not query:
            errors.append(f"Missing query for {item.get('event_id')}")
            continue
        if len(query) > MAX_QUERY_CHARACTERS:
            errors.append(f"Over-cap query for {item.get('event_id')}")
        if item.get("query_characters") != len(query) or item.get(
            "query_sha256"
        ) != digest_text(query):
            errors.append(f"Query evidence changed for {item.get('event_id')}")
        if "NEAR" in query.upper() or " AND " in query:
            errors.append(f"Unsupported source syntax in {item.get('event_id')}")
    if events[-1]["query"] != events[-2]["query"]:
        errors.append("Full wildcard repeat queries differ")
    if any("*" in item["query"] for item in events[:3]):
        errors.append("Explicit baseline contains wildcard syntax")
    if any("*" not in item["query"] for item in events[3:]):
        errors.append("Wildcard event lacks wildcard syntax")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        payload = load(args.output)
        errors = validate(payload)
        print(
            json.dumps(
                {"status": "ok" if not errors else "error", "errors": errors}, indent=2
            )
        )
        return 1 if errors else 0
    payload = build()
    errors = validate(payload)
    if errors:
        raise RuntimeError("Generated plan is invalid: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "saved": str(args.output),
                "events": len(payload["events"]),
                "full_wildcard_characters": payload["wildcard_candidate"][
                    "full_query_characters"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
