#!/usr/bin/env python3
"""Deterministic JSON, membership, control, and failure checks for Pilot 003."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from queries import MAIN_PARTITIONS, PSR_PARTITIONS, membership_audit


SCHEMA = "slr1-scopus-pilot003-validation/v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return value


def assert_main_controls(path: Path) -> None:
    value = load(path)
    strategy = value["output_metadata"]["prisma_search_run"]["strategy"]
    assert strategy["search_scope"]["label"] == "Documents", path
    assert strategy["sort"]["value"]["label"] == "Date (oldest)", path
    assert {item["value"] for item in strategy["limits"]["result_facets"]["effective"]} == {"English"}, path
    interval = strategy["limits"]["year_interval"]["value"]
    assert interval == {"start": 2011, "end": 2026, "inclusive": True}, path
    assert "DOCTYPE" not in value["requested_query"].upper(), path


def assert_psr_controls(path: Path) -> None:
    value = load(path)
    strategy = value["output_metadata"]["prisma_search_run"]["strategy"]
    assert strategy["search_scope"]["label"] == "Documents", path
    assert strategy["sort"]["value"]["label"] == "Date (oldest)", path
    assert strategy["limits"]["result_facets"]["state"] == "not_applied", path
    interval = strategy["limits"]["year_interval"]["value"]
    assert interval == {"start": None, "end": 2026, "inclusive": True}, path
    assert "DOCTYPE" not in value["requested_query"].upper(), path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", required=True, type=Path)
    parser.add_argument("--output-path", required=True, type=Path)
    args = parser.parse_args()
    if args.output_path.exists() or args.output_path.is_symlink():
        raise SystemExit(f"Refusing to overwrite {args.output_path}")
    root = args.pilot_root
    membership = membership_audit()
    all_json = sorted(root.rglob("*.json"))
    parsed = [load(path) for path in all_json]

    main_paths = {
        "A1": root / "searches/main/strict-ids/A1.json",
        "A2": root / "searches/main/strict-ids/A2.json",
        "A3": root / "searches/main/strict-ids/A3.json",
        "B1": root / "searches/main/strict-ids-B200/B1.json",
        "B2": root / "searches/main/strict-ids-B200/B2.json",
        "BG1": root / "searches/main/strict-ids/BG1.json",
        "BG2": root / "searches/main/strict-ids/BG2.json",
        "BC1": root / "searches/main/strict-ids/BC1.json",
        "BT2": root / "searches/main/strict-ids/BT2.json",
    }
    for path in main_paths.values():
        assert_main_controls(path)
    for path in (root / "searches/psr/strict-ids/PSR1.json", root / "searches/psr/strict-ids/PSR3.json"):
        assert_psr_controls(path)

    safe_failures = []
    for path, value in zip(all_json, parsed, strict=True):
        metadata = value.get("output_metadata")
        if not isinstance(metadata, dict) or metadata.get("status") != "error":
            continue
        assert value.get("total") is None, path
        assert isinstance(metadata.get("error_stage"), str) and metadata["error_stage"], path
        assert isinstance(metadata.get("error_reason"), str) and metadata["error_reason"], path
        safe_failures.append({
            "artifact": str(path.relative_to(root)),
            "error_stage": metadata["error_stage"],
            "error_reason": metadata["error_reason"],
        })

    union = load(root / "searches/stable-id-unions-final.json")
    assert union["main"]["complete"] is True
    assert union["main"]["stable_publication_id_union_total"] == 327
    assert union["main"]["full_abstracts"]["native_follow_up_records"] == 111
    assert union["prior_secondary_reviews"]["complete"] is False
    assert union["prior_secondary_reviews"]["full_abstracts"]["native_follow_up_records"] == 24
    assert {row["partition_id"] for row in union["outcomes"]} == set((*MAIN_PARTITIONS, *PSR_PARTITIONS))

    focused = Path(__file__).with_name("focused_adapter.py").read_text(encoding="utf-8")
    assert "Input.insertText" in focused and "REFERENCE_ADAPTER" in focused
    guideline = (root.parents[1] / "source-specific-guidelines.md").read_text(encoding="utf-8")
    assert "Pilot 003" in guideline and "no `DOCTYPE`" in guideline

    output = {
        "schema_version": SCHEMA,
        "json_file_count": len(all_json),
        "membership": membership,
        "main_complete_partitions": list(main_paths),
        "psr_complete_partitions": ["PSR1", "PSR3"],
        "psr_incomplete_partitions": ["PSR2", "PSR4"],
        "safe_failure_count": len(safe_failures),
        "safe_failures": safe_failures,
        "focused_adapter_checked": True,
        "source_guideline_checked": True,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
