#!/usr/bin/env python3
"""Build compact, no-clobber Pilot 003 NTRS reconciliation artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "source-specific" / "nasa-ntrs" / "pilots" / "003"
SEARCH_DIR = PILOT_DIR / "searches"
sys.path.insert(0, str(ROOT / "scripts" / "pilot_schedule"))

from queries import CONCEPTS, MAIN_FACTORS, RENDERERS, partition_cells, partition_query  # noqa: E402

DATE_START = "2011-01-01"
DATE_END = "2026-08-29"
SCHEDULE_IDS = tuple(MAIN_FACTORS)
SEMANTIC_FORMS = {
    "A1": "P AND E_H AND M_H",
    "A2": "P AND E_F AND (M_H OR M_B)",
    "A3": "P AND E_H AND M_B",
    "B1": "P AND M_H",
    "B2": "P AND M_B AND R",
    "BG1": "P AND G_model",
    "BG2": "P AND G_structure",
    "BC1": "P AND C1",
    "BT2": "P AND M_B AND T2",
}

# These are the only terminal successful artifacts used in the semantic unions.
DIRECT_ARTIFACTS = {
    "A1": "A1.json",
    "A2": "A2.json",
    "A3": "A3.json",
    "B1": "B1.json",
    "B2": "B2.json",
    "BG1": "BG1.json",
    "BG2": "BG2-retry1.json",
}
BC1_TERMINAL = (
    ("cell-0001", "BC1-cell-0001.json"),
    ("cell-0002", "BC1-cell-0002.json"),
    ("cell-0003", "BC1-cell-0003-retry1.json"),
    ("cell-0004", "BC1-cell-0004.json"),
)
# T2 ranges are zero-based, end-exclusive positions in CONCEPTS["T2"].pairs.
BT2_TERMINAL = (
    ("cell-0001-subcell-01", 0, 20, "BT2-cell-0001-subcell-01-retry1.json"),
    ("cell-0001-subcell-02", 20, 39, "BT2-cell-0001-subcell-02.json"),
    ("cell-0002", 39, 74, "BT2-cell-0002-retry1.json"),
    ("cell-0003-subcell-01", 74, 91, "BT2-cell-0003-subcell-01.json"),
    ("cell-0003-subcell-02", 91, 107, "BT2-cell-0003-subcell-02.json"),
    ("cell-0004", 107, 138, "BT2-cell-0004.json"),
    ("cell-0005-subcell-01", 138, 155, "BT2-cell-0005-subcell-01.json"),
    ("cell-0005-subcell-02", 155, 171, "BT2-cell-0005-subcell-02.json"),
    ("cell-0006", 171, 204, "BT2-cell-0006.json"),
    ("cell-0007", 204, 224, "BT2-cell-0007.json"),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(name: str) -> tuple[dict[str, Any], str]:
    path = SEARCH_DIR / name
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{name}: root is not an object")
    return data, sha256_bytes(raw)


def write_new_json(name: str, payload: dict[str, Any]) -> None:
    path = SEARCH_DIR / name
    if path.exists():
        raise SystemExit(f"Refusing to overwrite {path}")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ids(data: dict[str, Any]) -> list[str]:
    rows = data.get("results")
    if not isinstance(rows, list):
        raise ValueError("artifact results are not a list")
    result = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("paperId"), str):
            raise ValueError("artifact has a noncanonical result row")
        result.append(row["paperId"])
    return result


def source_limits(data: dict[str, Any]) -> dict[str, Any]:
    return data["output_metadata"]["prisma_search_run"]["strategy"]["limits"]


def assert_terminal_artifact(name: str, expected_query: str) -> tuple[dict[str, Any], str]:
    data, digest = load_json(name)
    metadata = data.get("output_metadata", {})
    if metadata.get("status") != "success" or metadata.get("retrieval_complete") is not True:
        raise ValueError(f"{name}: terminal artifact is not a complete success")
    if data.get("total") != len(ids(data)) or not isinstance(data.get("total"), int):
        raise ValueError(f"{name}: source total does not reconcile to retained canonical IDs")
    if data.get("executed_query") != expected_query:
        raise ValueError(f"{name}: source query differs from generated literal cell")
    limits = source_limits(data)
    publication = limits.get("publication_date", {})
    value = publication.get("value", {}) if isinstance(publication, dict) else {}
    if value.get("gte") != DATE_START or value.get("lte") != DATE_END:
        raise ValueError(f"{name}: exact diagnostic publication dates were not retained")
    if limits.get("document_type", {}).get("state") != "not_applied":
        raise ValueError(f"{name}: a Type restriction was applied")
    for key in ("collection", "source", "distribution"):
        if limits.get(key, {}).get("state") != "not_applied":
            raise ValueError(f"{name}: unexpected {key} restriction")
    if "*" in expected_query or "?" in expected_query:
        raise ValueError(f"{name}: an unaccepted wildcard was used")
    return data, digest


def terminal_summary(cell_id: str, name: str, expected_query: str, **extra: Any) -> dict[str, Any]:
    data, digest = assert_terminal_artifact(name, expected_query)
    summary = {
        "cell_id": cell_id,
        "artifact": name,
        "artifact_sha256": digest,
        "query_characters": len(expected_query),
        "query_sha256": sha256_bytes(expected_query.encode("utf-8")),
        "source_total": data["total"],
        "canonical_citation_ids": ids(data),
        "retrieval_complete": True,
        "canonical_id_capture": "two strict rendered NTRS passes reconciled by the adapter",
    }
    summary.update(extra)
    return summary


def union(cells: Iterable[dict[str, Any]]) -> dict[str, Any]:
    cell_rows = list(cells)
    raw = [item for cell in cell_rows for item in cell["canonical_citation_ids"]]
    stable = list(dict.fromkeys(raw))
    return {
        "all_terminal_cells_complete": True,
        "terminal_cell_count": len(cell_rows),
        "source_event_total": sum(cell["source_total"] for cell in cell_rows),
        "canonical_citation_id_union": stable,
        "deduplicated_union_count": len(stable),
        "within_partition_duplicate_event_count": len(raw) - len(stable),
        "investigation_threshold_exceeded": len(stable) > 100,
    }


def failure_summary(name: str) -> dict[str, Any]:
    data, digest = load_json(name)
    metadata = data.get("output_metadata", {})
    if metadata.get("status") != "error":
        raise ValueError(f"{name}: expected a preserved error artifact")
    if data.get("total") is not None or ids(data):
        raise ValueError(f"{name}: a failure must retain null total and no records")
    if data.get("do_not_merge") is not True:
        raise ValueError(f"{name}: failure is not marked non-mergeable")
    requested = data.get("requested_query", data.get("query", ""))
    return {
        "artifact": name,
        "artifact_sha256": digest,
        "source_total": None,
        "canonical_citation_ids": [],
        "retrieval_complete": False,
        "do_not_merge": True,
        "requested_query_characters": len(requested) if isinstance(requested, str) else None,
        "executed_query_observed": bool(data.get("executed_query")),
        "interpretation": "Non-mergeable error; null is not a source zero.",
    }


def t2_query(start: int, end: int) -> str:
    renderer = RENDERERS["nasa_ntrs"]
    p = renderer.union(renderer.alternatives(("P",)))
    mb = renderer.union(renderer.alternatives(("M_B",)))
    t2 = renderer.union(renderer.alternatives(("T2",))[start:end])
    return renderer.and_token.join((p, mb, t2))


def build_entries() -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for partition_id in ("A1", "A2", "A3", "B1", "B2", "BG1", "BG2"):
        query = partition_query("nasa_ntrs", partition_id)
        name = DIRECT_ARTIFACTS[partition_id]
        cells = [terminal_summary("direct-literal", name, query)]
        entries[partition_id] = {
            "semantic_construction": SEMANTIC_FORMS[partition_id],
            "execution": "one literal source-native q expression",
            "terminal_cells": cells,
            "union": union(cells),
        }

    bc1_full = partition_query("nasa_ntrs", "BC1")
    bc1_cells = partition_cells("nasa_ntrs", "BC1", maximum_characters=3000)
    if [cell["cell_id"] for cell in bc1_cells] != [cell_id for cell_id, _ in BC1_TERMINAL]:
        raise ValueError("BC1 generated cell identities changed")
    bc1_terminal = [
        terminal_summary(cell_id, name, cell["query"])
        for cell, (cell_id, name) in zip(bc1_cells, BC1_TERMINAL, strict=True)
    ]
    entries["BC1"] = {
        "semantic_construction": "P AND C1",
        "execution": "prospective lossless source-native OR cells after two full-expression pre-readback failures",
        "full_expression": {
            "query_characters": len(bc1_full),
            "query_sha256": sha256_bytes(bc1_full.encode("utf-8")),
            "failed_artifacts": ["BC1.json", "BC1-retry1.json"],
        },
        "cell_plan": {
            "generator": "pilot_schedule.partition_cells('nasa_ntrs', 'BC1', maximum_characters=3000)",
            "construction_bound_characters": 3000,
            "largest_actual_cell_characters": max(len(cell["query"]) for cell in bc1_cells),
            "proof": "The four cells are the Cartesian union of complete P with disjoint C1 OR chunks; their union is exactly P AND C1.",
        },
        "terminal_cells": bc1_terminal,
        "union": union(bc1_terminal),
    }

    bt2_full = partition_query("nasa_ntrs", "BT2")
    initial_bt2_cells = partition_cells("nasa_ntrs", "BT2", maximum_characters=6000)
    initial_ranges = ((0, 39), (39, 74), (74, 107), (107, 138), (138, 171), (171, 204), (204, 224))
    if len(initial_bt2_cells) != len(initial_ranges):
        raise ValueError("BT2 initial cell plan changed")
    for cell, (start, end) in zip(initial_bt2_cells, initial_ranges, strict=True):
        if cell["query"] != t2_query(start, end):
            raise ValueError(f"BT2 {cell['cell_id']} is not the declared T2 range")
    bt2_terminal = [
        terminal_summary(
            cell_id,
            name,
            t2_query(start, end),
            t2_pair_index_range_1_based=[start + 1, end],
            t2_pair_count=end - start,
        )
        for cell_id, start, end, name in BT2_TERMINAL
    ]
    expected_indexes = [index for _, start, end, _ in BT2_TERMINAL for index in range(start, end)]
    if expected_indexes != list(range(len(CONCEPTS["T2"].pairs))):
        raise ValueError("BT2 terminal cells do not cover every declared pair exactly once")
    entries["BT2"] = {
        "semantic_construction": "P AND M_B AND T2",
        "execution": "prospective lossless T2 OR cells after a full-expression pre-readback failure; failed parent cells were replaced only by disjoint literal children",
        "full_expression": {
            "query_characters": len(bt2_full),
            "query_sha256": sha256_bytes(bt2_full.encode("utf-8")),
            "failed_artifacts": ["BT2.json"],
        },
        "initial_cell_plan": {
            "generator": "pilot_schedule.partition_cells('nasa_ntrs', 'BT2', maximum_characters=6000)",
            "construction_bound_characters": 6000,
            "initial_cell_count": len(initial_bt2_cells),
            "initial_t2_pair_ranges_1_based": [[start + 1, end] for start, end in initial_ranges],
            "largest_actual_cell_characters": max(len(cell["query"]) for cell in initial_bt2_cells),
        },
        "replacement_cell_plan": {
            "replaced_parent_cells": {
                "cell-0001": [[1, 20], [21, 39]],
                "cell-0003": [[75, 91], [92, 107]],
                "cell-0005": [[139, 155], [156, 171]],
            },
            "proof": "Terminal T2 pair ranges are disjoint, source-order slices 1 through 224. Each source-native child retains complete P and M_B blocks, so their union restores P AND M_B AND T2 without dropping or narrowing a pair.",
        },
        "terminal_cells": bt2_terminal,
        "union": union(bt2_terminal),
    }
    if tuple(entries) != SCHEDULE_IDS:
        raise ValueError("schedule entry order changed")
    return entries


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.casefold())


def phrase_positions(haystack: list[str], phrase: str) -> list[tuple[int, int]]:
    needle = tokens(phrase)
    if not needle:
        return []
    return [
        (start, start + len(needle))
        for start in range(len(haystack) - len(needle) + 1)
        if haystack[start : start + len(needle)] == needle
    ]


def pair_hits(value: str, left: str, right: str) -> list[tuple[str, int]]:
    value_tokens = tokens(value)
    left_positions = phrase_positions(value_tokens, left)
    right_positions = phrase_positions(value_tokens, right)
    hits = []
    for left_start, left_end in left_positions:
        for right_start, right_end in right_positions:
            if left_end <= right_start and right_start - left_end <= 5:
                hits.append({
                    "order": "left_then_right",
                    "intervening_lexical_tokens": right_start - left_end,
                })
            if right_end <= left_start and left_start - right_end <= 5:
                hits.append({
                    "order": "right_then_left",
                    "intervening_lexical_tokens": left_start - right_end,
                })
    return list(dict.fromkeys((hit["order"], hit["intervening_lexical_tokens"]) for hit in hits))


def pair_check_entry(partition_id: str, pairs: tuple[tuple[str, str], ...], cells: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    all_hits: list[dict[str, Any]] = []
    for cell in cells:
        data, _ = load_json(cell["artifact"])
        for row in data["results"]:
            record = {"paperId": row["paperId"], "fields": {}}
            for field in ("title", "snippet"):
                text = row.get(field, "")
                field_hits = []
                if isinstance(text, str) and text:
                    for pair_index, (left, right) in enumerate(pairs, start=1):
                        for order, gap in pair_hits(text, left, right):
                            hit = {
                                "pair_index_1_based": pair_index,
                                "left": left,
                                "right": right,
                                "order": order,
                                "intervening_lexical_tokens": gap,
                            }
                            field_hits.append(hit)
                            all_hits.append({"paperId": row["paperId"], "field": field, **hit})
                record["fields"][field] = {
                    "state": "checked" if isinstance(text, str) and text else "no_retained_text",
                    "matching_pairs": field_hits,
                }
            records.append(record)
    return {
        "partition_id": partition_id,
        "declared_pair_count": len(pairs),
        "record_count": len(records),
        "records": records,
        "observed_pair_hits": all_hits,
        "observed_pair_hit_count": len(all_hits),
    }


def build_pair_checks(entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    configs = {
        "BG1": CONCEPTS["G_model"].pairs,
        "BG2": CONCEPTS["G_structure"].pairs,
        "BC1": CONCEPTS["C1"].pairs,
        "BT2": CONCEPTS["T2"].pairs,
    }
    checks = {
        partition_id: pair_check_entry(partition_id, pairs, entries[partition_id]["terminal_cells"])
        for partition_id, pairs in configs.items()
    }
    detail_failures = [failure_summary(name) for name in ("BG2-pair-fields.json", "BG2-pair-fields-retry1.json")]
    return {
        "schema_version": "ntrs-pilot-003-pair-checks/v1",
        "pilot": "003",
        "source": "NASA Technical Reports Server (NTRS)",
        "date_window": {"start": DATE_START, "end": DATE_END, "precision": "inclusive publication calendar days"},
        "method": {
            "source_pair_syntax": "(\"left right\"~5 | \"right left\"~5)",
            "local_check": "case-folded lexical-token phrase matching in both orders, with no more than five intervening tokens",
            "retained_fields_checked": ["title", "snippet"],
            "not_an_eligibility_decision": True,
        },
        "checks": checks,
        "full_text_uncertainty": {
            "status": "unresolved",
            "reason": "NTRS general q includes metadata and document full text, while the terminal strict list captures retain title and rendered-list snippet only. Two exact BG2 --full-abstracts diagnostics failed before a usable complete result; their source totals remain null.",
            "detail_failure_artifacts": detail_failures,
            "absence_interpretation": "An absent local title/snippet match is not evidence that a source hit is false or lacks a pair in abstract or full text.",
        },
    }


def main() -> int:
    entries = build_entries()
    failure_artifacts = []
    for path in sorted(SEARCH_DIR.glob("*.json")):
        if path.name in {"plan.json", "schedule-assessment.json", "pair-checks.json"}:
            continue
        data, _ = load_json(path.name)
        if data.get("output_metadata", {}).get("status") == "error":
            failure_artifacts.append(failure_summary(path.name))
    all_cells = [cell for entry in entries.values() for cell in entry["terminal_cells"]]
    all_raw_ids = [item for cell in all_cells for item in cell["canonical_citation_ids"]]
    all_union_ids = list(dict.fromkeys(all_raw_ids))
    assessment = {
        "schema_version": "ntrs-pilot-003-schedule-assessment/v1",
        "pilot": "003",
        "mode": "diagnostic_only_not_a_final_search",
        "source": "NASA Technical Reports Server (NTRS)",
        "interface": "normal rendered first-party Web UI through search_ntrs.py",
        "date_window": {
            "publication_start": DATE_START,
            "publication_end": DATE_END,
            "precision": "inclusive calendar day",
        },
        "translation": {
            "generator": "SLR/SLR1/scripts/pilot_schedule/queries.py",
            "renderer": "nasa_ntrs",
            "operators": {"and": "+", "or": "|", "pair": "ordered phrase slop ~5 in both orders"},
            "concept_counts": {
                name: {"literals": len(concept.literals), "pairs": len(concept.pairs)}
                for name, concept in CONCEPTS.items()
                if name in {"P", "E_H", "E_F", "M_H", "M_B", "R", "G_model", "G_structure", "C1", "T2"}
            },
            "wildcards_present": False,
            "wildcard_decision": "A1 nanosatellit* remains unaccepted after Pilot 002; no wildcard was run or adopted.",
        },
        "controls": {
            "language": "No usable NTRS Language control; no language restriction applied.",
            "publication_type": "No Type restriction; one exact source option cannot prove a lossless eligible-type union.",
            "access": "No access, full-text-availability, source, distribution, collection, center, subject, or peer-review restriction applied.",
            "controlled_vocabulary": "No descriptor supplement or controlled-term restriction applied; NTRS exposes no proved Thesaurus term route.",
            "capture": "Each terminal cell used --require-complete, page size 100, capacity 10,000 records/100 pages, and no detail fan-out.",
        },
        "entries": entries,
        "investigation_threshold": {
            "deduplicated_canonical_ids": 100,
            "largest_partition_union": max(entry["union"]["deduplicated_union_count"] for entry in entries.values()),
            "triggered_partitions": [
                partition_id
                for partition_id, entry in entries.items()
                if entry["union"]["investigation_threshold_exceeded"]
            ],
            "decision": "No partition exceeded 100 deduplicated canonical citation IDs; no narrowing refinement was warranted or attempted.",
        },
        "refinements": {
            "lossless_query_cells_only": "BC1 and BT2 use prospective literal OR-cell decompositions solely to recover from pre-readback failures; they are not metadata, controlled-term, language, type, or access narrowing.",
            "narrowing_filters_applied": [],
        },
        "failures": failure_artifacts,
        "overall_schedule_union": {
            "source_event_total": sum(cell["source_total"] for cell in all_cells),
            "canonical_citation_id_union": all_union_ids,
            "deduplicated_union_count": len(all_union_ids),
            "cross_partition_duplicate_event_count": len(all_raw_ids) - len(all_union_ids),
            "not_a_final_corpus": True,
        },
        "pair_checks_artifact": "pair-checks.json",
    }
    pair_checks = build_pair_checks(entries)
    write_new_json("schedule-assessment.json", assessment)
    write_new_json("pair-checks.json", pair_checks)
    print(json.dumps({
        "saved": ["schedule-assessment.json", "pair-checks.json"],
        "partition_unions": {
            partition_id: entry["union"]["deduplicated_union_count"]
            for partition_id, entry in entries.items()
        },
        "overall_union": len(all_union_ids),
        "failure_artifacts": len(failure_artifacts),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
