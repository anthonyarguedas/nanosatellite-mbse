#!/usr/bin/env python3
"""Build the Pilot 005 branch-count plan after the over-100 trigger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from queries import (
    C1_FIXED_TERMS,
    GDSL_TERMS,
    GMISSION_EXACT_TERMS,
    GMISSION_TERMS,
    GMODEL_FIXED_TERMS,
    GPRODUCT_EXACT_TERMS,
    GPRODUCT_TERMS,
    GSTRUCTURE_FIXED_TERMS,
    GVARIATION_TERMS,
    MB_TERMS,
    P_TERMS,
    PROTOCOL_COMMIT,
    all_of,
    ordinary_block,
)

SOURCE = "AIAA Aerospace Research Central (ARC)"
DATE_START = "2011-01-01"
DATE_END = "2026-08-29"


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def load_total(path: Path) -> int:
    value = json.loads(path.read_text()).get("total")
    if not isinstance(value, int):
        raise RuntimeError(f"Missing integer total in {path}")
    return value


def branch_query(component: str, *, require_mb: bool = False) -> str:
    factors = [ordinary_block(P_TERMS)]
    if require_mb:
        factors.append(ordinary_block(MB_TERMS))
    factors.append(component)
    return all_of(*factors)


def event(event_id: str, schedule_id: str, branch: str, query: str) -> dict:
    return {
        "event_id": event_id,
        "schedule_id": schedule_id,
        "branch": branch,
        "purpose": "Attribute the over-100 direct Anywhere total to one declared compound branch.",
        "query": query,
        "query_characters": len(query),
        "query_sha256": digest(query),
        "field_rows": [{"field": "Anywhere", "source_field": "AllField", "text": query}],
        "mode": "count",
        "output": f"searches/branch-counts/{event_id.removeprefix('branch-')}.json",
        "do_not_merge": True,
    }


def build(count_dir: Path) -> dict:
    observed = {key: load_total(count_dir / f"{key}.json") for key in ("BG1", "BG2", "BC1", "BT2")}
    triggered = [key for key, total in observed.items() if total > 100]
    if triggered != ["BG2", "BC1", "BT2"]:
        raise RuntimeError(f"Unexpected threshold trigger set: {triggered}")

    components: list[tuple[str, str, str, str]] = [
        ("BG1", "fixed", "G_model_fixed", ordinary_block(GMODEL_FIXED_TERMS)),
        ("BG1", "mission-exact", "G_mission_exact", ordinary_block(GMISSION_EXACT_TERMS)),
        (
            "BG1",
            "mission-context",
            "G_mission AND M_B",
            all_of(ordinary_block(GMISSION_TERMS), ordinary_block(MB_TERMS)),
        ),
        ("BG2", "fixed", "G_structure_fixed", ordinary_block(GSTRUCTURE_FIXED_TERMS)),
        ("BG2", "product-exact", "G_product_exact", ordinary_block(GPRODUCT_EXACT_TERMS)),
        ("BG2", "variation", "G_variation", ordinary_block(GVARIATION_TERMS)),
        (
            "BG2",
            "product-context",
            "G_product AND M_B",
            all_of(ordinary_block(GPRODUCT_TERMS), ordinary_block(MB_TERMS)),
        ),
        ("BC1", "fixed", "C1_fixed", ordinary_block(C1_FIXED_TERMS)),
        ("BC1", "dsl", "G_DSL", ordinary_block(GDSL_TERMS)),
    ]
    t_groups = {
        "tailor": ("tailor", "tailors", "tailored", "tailoring"),
        "customize": ("customize", "customizes", "customized", "customizing", "customization"),
        "customise": ("customise", "customises", "customised", "customising", "customisation"),
        "parameterize": ("parameterize", "parameterizes", "parameterized", "parameterizing", "parameterization"),
        "parameterise": ("parameterise", "parameterises", "parameterised", "parameterising", "parameterisation"),
        "instantiate": ("instantiate", "instantiates", "instantiated", "instantiating", "instantiation"),
        "variability": ("variability", "variation point", "variation points"),
    }
    events = []
    for schedule_id, slug, label, component in components:
        events.append(event(f"branch-{schedule_id}-{slug}", schedule_id, label, branch_query(component)))
    for slug, terms in t_groups.items():
        events.append(
            event(
                f"branch-BT2-{slug}",
                "BT2",
                " OR ".join(terms),
                branch_query(ordinary_block(terms), require_mb=True),
            )
        )
    return {
        "schema_version": "aiaa-arc-pilot005-threshold-event-plan/v1",
        "source": SOURCE,
        "pilot": "005",
        "protocol_commit": PROTOCOL_COMMIT,
        "diagnostic_only": True,
        "do_not_merge": True,
        "trigger": {
            "threshold": 100,
            "primary_changed_partition_totals": observed,
            "triggered_partitions": triggered,
            "BG1_included_as_low-volume_historical_comparator": True,
        },
        "date_window": {"requested_start": DATE_START, "requested_end": DATE_END},
        "controls": {
            "access": "all",
            "language": None,
            "publication_type": None,
            "topic": None,
            "wildcard": False,
            "proximity": False,
            "field_narrowing": False,
        },
        "interpretation": (
            "Branch totals overlap and their sum is only an upper bound. They diagnose source volume and do not replace "
            "the complete direct partition."
        ),
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.count_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
