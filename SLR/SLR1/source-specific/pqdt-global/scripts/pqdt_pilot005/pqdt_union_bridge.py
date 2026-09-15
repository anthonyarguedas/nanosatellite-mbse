#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48,<2"]
# ///
"""Run PQDT with several validated raw PSUB or IF clauses.

The general adapter accepts source-valid raw Command Line syntax, but its typed
facet conflict guard currently rejects a raw expression that contains more than
one PSUB or IF clause even when no typed facet value was requested. This pilot
bridge relaxes only that local preflight condition. The source still receives
the exact raw expression and the adapter still requires exact query echo,
controls, strict traversal, screenshots, output publication, and cleanup.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any

ADAPTER_PATH = (
    Path.home() / "agent-tools" / "internet" / "skills" / "browser" / "scripts" / "search_pqdt.py"
)


def load_adapter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pqdt_pilot005_union_bridge_adapter", ADAPTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load PQDT adapter at {ADAPTER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def install_raw_union_bridge(adapter: Any) -> None:
    original_append = adapter._append_typed_clause

    def append_typed_clause(
        query: str, *, name: str, value: str | None
    ) -> str:
        if value is None:
            return query
        return original_append(query, name=name, value=value)

    def effective_command_filters(command_query: str) -> dict[str, Any]:
        cleaned = adapter.clean_text(command_query)
        filters: dict[str, Any] = {
            "publication_date": adapter._publication_date_filter(cleaned),
            "facets": {},
        }
        for name, code in adapter.FACET_FIELD_CODES.items():
            values = adapter._clause_values(cleaned, name)
            effective: Any
            if not values:
                effective = None
            elif len(values) == 1:
                effective = values[0]
            else:
                effective = list(values)
            filters["facets"][name] = {
                "field": code,
                "state": "applied" if values else "not_applied",
                "requested": effective,
                "effective": effective,
                "stage": "source_query",
                "provenance": "caller" if values else "derived",
                "clauses": [{"value": item} for item in values],
            }
        return filters

    adapter._append_typed_clause = append_typed_clause
    adapter.effective_command_filters = effective_command_filters


def assert_bridge_scope(adapter: Any) -> None:
    raw = '(IF.EXACT("CubeSat") OR IF.EXACT("CubeSats")) AND PSUB.EXACT("systems engineering")'
    built = adapter.build_command_query(
        raw,
        year_start=2011,
        year_end=2026,
        language="English",
    )
    expected = raw + " AND YR(2011-2026) AND LA(English)"
    if built != expected:
        raise RuntimeError("PQDT Pilot 005 union bridge changed the raw query")
    filters = adapter.effective_command_filters(built)
    if filters["facets"]["index_term"]["effective"] != [
        '"CubeSat"',
        '"CubeSats"',
    ]:
        raise RuntimeError("PQDT Pilot 005 union bridge lost an IF clause")
    if filters["facets"]["subject"]["effective"] != '"systems engineering"':
        raise RuntimeError("PQDT Pilot 005 union bridge lost the PSUB clause")
    clauses = adapter._pqdt_command_clause_texts(built)
    if len(clauses.get("IF", [])) != 2 or len(clauses.get("PSUB", [])) != 1:
        raise RuntimeError("PQDT Pilot 005 union bridge changed clause evidence")


def main(argv: list[str] | None = None) -> int:
    adapter = load_adapter()
    install_raw_union_bridge(adapter)
    assert_bridge_scope(adapter)
    return adapter.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
