#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["certifi"]
# ///

"""Offline integrity checks for committed arXiv Pilot 003 artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import atom_pilot as pilot

SLR1_ROOT = SCRIPT_DIR.parents[1]
PILOT_ROOT = SLR1_ROOT / "source-specific" / "arxiv" / "pilots" / "003"
SEARCH_DIR = PILOT_ROOT / "searches"
GUIDELINE = SLR1_ROOT / "source-specific" / "arxiv" / "source-specific-guidelines.md"

PARTITION_IDS = tuple(pilot.MAIN_FACTORS)
FULL_ROUTE_FAILURES = {"A2": 400, "BC1": 400, "BT2": 414}
ATOM_VALUE_RE = re.compile(r'all:(?:"([^"]+)"|([A-Za-z0-9-]+))')
ALL_DECLARED_PAIRS = tuple(
    pair for concept in pilot.CONCEPTS.values() for pair in concept.pairs
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_links(markdown: Path, errors: list[str]) -> None:
    text = markdown.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", text):
        if target.startswith(("https://", "http://", "mailto:")):
            continue
        path = (markdown.parent / target).resolve()
        require(path.exists(), f"{markdown}: broken local link {target}", errors)


def atom_values(expression: str) -> set[str]:
    return {quoted or bare for quoted, bare in ATOM_VALUE_RE.findall(expression)}


def check_capture(cell: Mapping[str, Any], errors: list[str]) -> None:
    capture = cell.get("capture")
    name = cell.get("cell_id", "unknown-cell")
    require(isinstance(capture, Mapping), f"{name}: missing capture", errors)
    if not isinstance(capture, Mapping):
        return
    total = cell.get("total")
    require(capture.get("source_reported_total") == total, f"{name}: total mismatch", errors)
    first = capture.get("first_pass")
    second = capture.get("second_pass")
    reconciliation = capture.get("cross_pass_reconciliation")
    require(isinstance(first, Mapping), f"{name}: missing first pass", errors)
    require(isinstance(second, Mapping), f"{name}: missing second pass", errors)
    require(isinstance(reconciliation, Mapping), f"{name}: missing reconciliation", errors)
    if not isinstance(first, Mapping) or not isinstance(second, Mapping) or not isinstance(reconciliation, Mapping):
        return
    records = first.get("records")
    stable_ids = first.get("stable_ids_in_source_order")
    versioned_ids = first.get("versioned_ids_in_source_order")
    require(isinstance(records, list) and len(records) == total, f"{name}: incomplete first-pass records", errors)
    require(isinstance(stable_ids, list) and len(stable_ids) == total, f"{name}: incomplete stable IDs", errors)
    require(isinstance(versioned_ids, list) and len(versioned_ids) == total, f"{name}: incomplete versioned IDs", errors)
    if isinstance(stable_ids, list):
        require(len(stable_ids) == len(set(stable_ids)), f"{name}: duplicate stable IDs", errors)
    if isinstance(versioned_ids, list):
        require(len(versioned_ids) == len(set(versioned_ids)), f"{name}: duplicate versioned IDs", errors)
    require(
        reconciliation.get("complete_stable_id_capture") is True,
        f"{name}: missing complete stable-ID capture",
        errors,
    )
    require(
        all(reconciliation.get(key) is True for key in (
            "same_source_reported_total",
            "same_versioned_ids_in_source_order",
            "same_stable_ids_in_source_order",
        )),
        f"{name}: two passes do not reconcile",
        errors,
    )
    for record in records if isinstance(records, list) else []:
        require(
            pilot.DATE_FROM <= str(record.get("published", ""))[:10] <= pilot.DATE_TO,
            f"{name}: record outside diagnostic window",
            errors,
        )
    expected_atoms = atom_values(str(cell.get("query", "")))
    expected_pairs = [
        pilot.pair_atom(left, right)
        for concept in pilot.CONCEPTS.values()
        for left, right in concept.pairs
        if pilot.pair_atom(left, right) in str(cell.get("query", ""))
    ]
    expected_date_echo = 'submittedDate:"201101010000 TO 202608292359"'
    for pass_name, source_pass in (("first", first), ("second", second)):
        for page in source_pass.get("pages", []):
            echo = str(page.get("source_query_echo", ""))
            require(expected_atoms <= atom_values(echo), f"{name}: {pass_name}-pass source echo dropped an Atom term", errors)
            require(expected_date_echo in echo, f"{name}: {pass_name}-pass source echo lacks canonical date range", errors)
            for pair in expected_pairs:
                require(pair in echo, f"{name}: {pass_name}-pass source echo dropped pair {pair}", errors)
            try:
                pilot.validate_source_echo(str(cell.get("query", "")), echo, ALL_DECLARED_PAIRS)
            except pilot.PilotError as error:
                errors.append(f"{name}: {pass_name}-pass runtime source-echo guard failed: {error}")


def main() -> int:
    errors: list[str] = []
    try:
        pilot.validate_renderer()
    except Exception as error:  # noqa: BLE001 - report the offline renderer error cleanly.
        errors.append(f"renderer validation failed: {error}")

    required_paths = {
        *(SEARCH_DIR / f"{partition_id}.json" for partition_id in PARTITION_IDS),
        SEARCH_DIR / "transport-validation.json",
        SEARCH_DIR / "pagination-capture.json",
        SEARCH_DIR / "partition-unions.json",
        SEARCH_DIR / "threshold-investigation.json",
        *(SEARCH_DIR / f"{partition_id}-full.NON_MERGEABLE_FAILURE.json" for partition_id in FULL_ROUTE_FAILURES),
    }
    for path in required_paths:
        require(path.exists(), f"missing artifact {path.name}", errors)
    for path in SEARCH_DIR.glob("*.json"):
        try:
            load(path)
        except Exception as error:  # noqa: BLE001
            errors.append(f"invalid JSON {path.name}: {error}")

    if errors:
        print("FAILED\n" + "\n".join(f"- {error}" for error in errors))
        return 1

    validation = load(SEARCH_DIR / "transport-validation.json")
    require(validation.get("schema_version") == pilot.VALIDATION_SCHEMA, "wrong transport-validation schema", errors)
    for name, check in validation.get("checks", {}).items():
        require(check.get("status") == "passed", f"transport check {name} did not pass", errors)
    route = validation.get("route", {})
    require(route.get("transport") == "arXiv Atom API", "transport route was not Atom API", errors)
    require("separate" in route.get("boolean_syntax", "").lower(), "browser/API boundary missing", errors)

    pagination = load(SEARCH_DIR / "pagination-capture.json")
    capture = pagination.get("capture", {})
    require(pagination.get("outcome") == "complete", "pagination validation did not complete", errors)
    require(capture.get("source_reported_total") == 72, "pagination control total changed", errors)
    require(len(capture.get("first_pass", {}).get("pages", [])) == 3, "pagination control first pass is not three pages", errors)
    require(len(capture.get("second_pass", {}).get("pages", [])) == 3, "pagination control second pass is not three pages", errors)
    require(capture.get("cross_pass_reconciliation", {}).get("complete_stable_id_capture") is True, "pagination stable-ID reconciliation missing", errors)

    events: dict[str, dict[str, Any]] = {}
    for partition_id in PARTITION_IDS:
        event = load(SEARCH_DIR / f"{partition_id}.json")
        events[partition_id] = event
        planned = pilot.partition_cells(partition_id)
        require(event.get("outcome") == "complete", f"{partition_id}: event did not complete", errors)
        require(isinstance(event.get("total"), int), f"{partition_id}: total is not an integer", errors)
        cells = event.get("cells", [])
        require(len(cells) == len(planned), f"{partition_id}: wrong cell count", errors)
        for actual, expected in zip(cells, planned, strict=True):
            require(actual.get("status") == "complete", f"{partition_id}/{actual.get('cell_id')}: failed", errors)
            require(isinstance(actual.get("total"), int), f"{partition_id}/{actual.get('cell_id')}: null total", errors)
            require(actual.get("query") == expected.get("query"), f"{partition_id}/{actual.get('cell_id')}: query drift", errors)
            require(actual.get("encoded_url_length") == expected.get("encoded_url_length"), f"{partition_id}/{actual.get('cell_id')}: URI-length drift", errors)
            require(pilot.DATE_CLAUSE in actual.get("query", ""), f"{partition_id}/{actual.get('cell_id')}: date clause missing", errors)
            require("*" not in actual.get("query", "") and "?" not in actual.get("query", ""), f"{partition_id}/{actual.get('cell_id')}: wildcard used", errors)
            check_capture(actual, errors)
        if all(isinstance(cell.get("total"), int) for cell in cells):
            require(event.get("total") == sum(cell["total"] for cell in cells), f"{partition_id}: event total does not equal cells", errors)

    for partition_id, expected_status in FULL_ROUTE_FAILURES.items():
        failure = load(SEARCH_DIR / f"{partition_id}-full.NON_MERGEABLE_FAILURE.json")
        require(failure.get("outcome") == "failed", f"{partition_id} full route was not retained as failure", errors)
        require(failure.get("total") is None, f"{partition_id} full route failure became zero", errors)
        require(failure.get("failure", {}).get("status") == expected_status, f"{partition_id} full route HTTP status drift", errors)
        require(failure.get("replacement", {}).get("cell_count") == len(pilot.partition_cells(partition_id)), f"{partition_id} replacement-cell count drift", errors)

    unions = load(SEARCH_DIR / "partition-unions.json")
    require(unions.get("schema_version") == pilot.UNION_SCHEMA, "wrong union schema", errors)
    for partition_id, event in events.items():
        union = unions.get("partitions", {}).get(partition_id, {})
        raw_records = [
            record
            for cell in event["cells"]
            for record in cell["capture"]["first_pass"]["records"]
        ]
        expected_ids = [record["source_record_stable_id"] for record in raw_records]
        union_ids = union.get("stable_id_union")
        require(union.get("outcome") == "complete", f"{partition_id}: union incomplete", errors)
        require(union.get("raw_source_discovery_events") == len(raw_records), f"{partition_id}: raw-event union count drift", errors)
        require(union.get("unique_stable_id_count") == len(set(expected_ids)), f"{partition_id}: unique union count drift", errors)
        require(isinstance(union_ids, list) and set(union_ids) == set(expected_ids), f"{partition_id}: stable-ID union drift", errors)

    investigation = load(SEARCH_DIR / "threshold-investigation.json")
    maximum_union = max(
        unions["partitions"][partition_id]["unique_stable_id_count"] for partition_id in PARTITION_IDS
    )
    require(maximum_union <= 100, "saved pilot unexpectedly has a >100 partition union", errors)
    require(investigation.get("status") == "not_triggered", "threshold investigation should be not-triggered", errors)
    require(investigation.get("partitions") == {}, "not-triggered investigation has records", errors)

    check_links(PILOT_ROOT / "pilot.md", errors)
    check_links(GUIDELINE, errors)
    guideline = GUIDELINE.read_text(encoding="utf-8")
    require("Atom API" in guideline, "guideline does not document Atom route", errors)
    require(
        "never attribute it to a browser" in guideline.casefold(),
        "guideline lacks transport boundary",
        errors,
    )
    require("Wildcards are unaccepted" in guideline, "guideline wildcard decision drift", errors)
    final_contents = sorted(path.name for path in (SLR1_ROOT / "source-specific" / "arxiv" / "final-searches").iterdir())
    require(final_contents == [".gitkeep"], "pilot altered final-search state", errors)

    if errors:
        print("FAILED\n" + "\n".join(f"- {error}" for error in errors))
        return 1
    summary = {
        "status": "ok",
        "partitions": {
            partition_id: unions["partitions"][partition_id]["unique_stable_id_count"]
            for partition_id in PARTITION_IDS
        },
        "transport_checks": sorted(validation["checks"]),
        "full_route_null_failures": FULL_ROUTE_FAILURES,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
