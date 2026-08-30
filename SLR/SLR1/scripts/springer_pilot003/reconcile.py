"""Build Pilot 003 canonical-ID and metadata-noise receipts.

The normal Springer adapter output is intentionally used only as a pilot
artifact here.  These receipts do not promote an event into final-search
status: they make the successful source-cell unions and the one explicit
BT2 route failure reviewable.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import queries  # noqa: E402


YEARS = tuple(range(2011, 2027))
SOURCE = "Springer Nature Link"
SEARCHES = (
    Path(__file__).resolve().parents[2]
    / "source-specific"
    / "springer-nature-link"
    / "pilots"
    / "003"
    / "searches"
)


@dataclass(frozen=True)
class EventSpec:
    file_name: str
    route: str


def _year_files(prefix: str) -> list[EventSpec]:
    return [EventSpec(f"{prefix}-year-{year}.json", "source_year_cell") for year in YEARS]


def event_plan() -> dict[str, tuple[EventSpec, ...]]:
    """Return only successful normal outputs that form each retained union."""
    b2_direct_years = (*range(2011, 2021), 2023, 2025, 2026)
    b2 = [EventSpec(f"B2-year-{year}.json", "source_year_cell") for year in b2_direct_years]
    for year in (2021, 2022, 2024):
        b2.extend(
            EventSpec(f"B2-year-{year}-cell-{cell:04d}.json", "lossless_boolean_cell_and_source_year_cell")
            for cell in range(1, 5)
        )

    bt2: list[EventSpec] = [
        *(EventSpec(f"BT2-T2-{cell:02d}-of-11.json", "lossless_T2_cell") for cell in range(1, 8)),
        EventSpec("BT2-T2-08-of-11-sub-1-of-4.json", "lossless_T2_recovery_subcell"),
        EventSpec("BT2-T2-08-of-11-sub-2-of-4.json", "lossless_T2_recovery_subcell"),
        # T2-08 sub-3 is replaced by its five original pair alternatives.
        *(EventSpec(f"BT2-T2-08-of-11-pair-{pair:02d}-of-20-year-{year}.json", "lossless_T2_pair_and_source_year_cell")
          for pair in (11,) for year in YEARS if year != 2017),
        *(EventSpec(f"BT2-T2-08-of-11-pair-{pair:02d}-of-20.json", "lossless_T2_pair_cell")
          for pair in (12, 13, 14, 15)),
        EventSpec("BT2-T2-08-of-11-sub-4-of-4.json", "lossless_T2_recovery_subcell"),
        EventSpec("BT2-T2-09-of-11.json", "lossless_T2_cell"),
        *(EventSpec(f"BT2-T2-10-of-11-sub-{cell}-of-5.json", "lossless_T2_recovery_subcell") for cell in range(1, 6)),
        *(EventSpec(f"BT2-T2-11-of-11-sub-{cell}-of-4.json", "lossless_T2_recovery_subcell") for cell in range(1, 5)),
    ]

    return {
        "A1": (EventSpec("A1.json", "direct_source_row"),),
        "A2": (
            EventSpec("A2-cell-0001.json", "lossless_boolean_cell"),
            *_year_files("A2-cell-0002"),
        ),
        "A3": (EventSpec("A3.json", "direct_source_row"),),
        "B1": tuple(_year_files("B1")),
        "B2": tuple(b2),
        "BG1": (EventSpec("BG1.json", "direct_source_row"),),
        "BG2": (EventSpec("BG2.json", "direct_source_row"),),
        "BC1": (EventSpec("BC1.json", "direct_source_row"),),
        "BT2": tuple(bt2),
    }


BT2_NULL_FAILURE = {
    "cell": "T2-08-of-11 alternative 11 of 20: (\"variability\" AND \"models\")",
    "date_cell": "2017-01-01 through 2017-12-31",
    "source_reported_total": 4,
    "stable_identifiers": None,
    "reason": "The fixed adapter twice rejected a canonical-detail redirect after a reconciled two-pass search; no identifiers were invented from the failed route.",
    "artifacts": [
        "BT2-T2-08-of-11-pair-11-of-20-year-2017.NON_MERGEABLE_DIAGNOSTIC.json",
        "BT2-T2-08-of-11-pair-11-of-20-year-2017-retry1.NON_MERGEABLE_DIAGNOSTIC.json",
    ],
}


def _digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Refusing to overwrite receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))
            stream.write(b"\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _normal_marker(path: Path) -> Path:
    return path.with_name(f".{path.name}.SPRINGER_COMMIT.json")


def _read_complete_event(searches: Path, spec: EventSpec) -> tuple[dict[str, Any], dict[str, Any]]:
    path = searches / spec.file_name
    if not path.is_file():
        raise FileNotFoundError(f"Missing planned successful artifact: {path}")
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    metadata = data.get("output_metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{path} lacks output metadata")
    if metadata.get("status") != "success" or metadata.get("retrieval_complete") is not True:
        raise ValueError(f"{path} is not a complete successful source event")
    if metadata.get("merge_eligible") is not True:
        raise ValueError(f"{path} is not an adapter-verified normal output")
    marker_path = _normal_marker(path)
    if not marker_path.is_file():
        raise FileNotFoundError(f"{path} lacks its Springer normal-output marker")
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    normalized = marker.get("normalized_json") if isinstance(marker, dict) else None
    if not isinstance(normalized, dict):
        raise ValueError(f"{marker_path} lacks normalized JSON evidence")
    if normalized.get("sha256") != _digest(raw) or normalized.get("bytes") != len(raw):
        raise ValueError(f"{path} does not match its normal-output marker")
    if marker.get("transaction_id") != metadata.get("normal_output_transaction_id"):
        raise ValueError(f"{path} does not match its output transaction marker")

    run = metadata.get("prisma_search_run")
    strategy = run.get("strategy") if isinstance(run, dict) else None
    limits = strategy.get("limits") if isinstance(strategy, dict) else None
    sort = strategy.get("sort") if isinstance(strategy, dict) else None
    if not isinstance(limits, dict) or not isinstance(sort, dict):
        raise ValueError(f"{path} lacks compact source-control evidence")
    language = limits.get("language")
    if not isinstance(language, dict) or language.get("state") != "applied" or language.get("value") != "En":
        raise ValueError(f"{path} did not retain the En facet")
    if sort.get("state") != "applied" or sort.get("requested") != "oldestFirst":
        raise ValueError(f"{path} did not retain oldestFirst")
    for key in ("content_types", "open_access", "disciplines", "subdisciplines", "sdgs", "book_accessibility"):
        value = limits.get(key)
        if not isinstance(value, dict) or value.get("state") != "not_applied":
            raise ValueError(f"{path} applied an excluded source limiter ({key})")
    facets = limits.get("facets_requested")
    if not isinstance(facets, dict) or facets.get("state") != "not_applied":
        raise ValueError(f"{path} retained an unplanned source facet")
    for key in ("date_start", "date_end"):
        value = limits.get(key)
        if not isinstance(value, dict) or value.get("state") != "applied" or not value.get("value"):
            raise ValueError(f"{path} lacks exact date bounds")
    query = data.get("executed_query")
    if not isinstance(query, str) or not query or "*" in query or "?" in query:
        raise ValueError(f"{path} lacks an explicit literal-only query")
    rows = data.get("results")
    if not isinstance(rows, list):
        raise ValueError(f"{path} lacks result rows")
    ids: list[str] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{path} row {index} is invalid")
        identifier = row.get("paperId")
        if not isinstance(identifier, str) or not identifier.startswith("/"):
            raise ValueError(f"{path} row {index} lacks a canonical source path")
        if identifier.casefold() in {item.casefold() for item in ids}:
            raise ValueError(f"{path} repeats a canonical source path")
        ids.append(identifier)
    return data, {
        "artifact": spec.file_name,
        "artifact_sha256": _digest(raw),
        "artifact_bytes": len(raw),
        "route": spec.route,
        "query": query,
        "source_total": data.get("total"),
        "retained_rows": len(rows),
        "client_side_date_exclusions": (data.get("total") - len(rows)) if isinstance(data.get("total"), int) else None,
        "stable_ids": ids,
    }


def _factor_label(concept_names: Iterable[str]) -> str:
    return " OR ".join(concept_names)


def _literal_in_field(field: str, literal: str) -> bool:
    return literal.casefold() in field.casefold()


def _all_positions(field: str, literal: str) -> Iterable[tuple[int, int]]:
    needle = literal.casefold()
    haystack = field.casefold()
    position = haystack.find(needle)
    while position >= 0:
        yield position, position + len(needle)
        position = haystack.find(needle, position + 1)


def _pair_within_five(field: str, left: str, right: str) -> bool:
    """Check either pair order in one visible metadata field only."""
    for first, second in ((left, right), (right, left)):
        for _first_start, first_end in _all_positions(field, first):
            for second_start, _second_end in _all_positions(field, second):
                if second_start < first_end:
                    continue
                between = field[first_end:second_start]
                if len(re.findall(r"\b[\w]+\b", between, flags=re.UNICODE)) <= 5:
                    return True
    return False


def _concept_presence(row: Mapping[str, Any], concept_name: str) -> dict[str, Any]:
    concept = queries.CONCEPTS[concept_name]
    fields = tuple(
        str(row.get(key) or "")
        for key in ("title", "abstract")
        if isinstance(row.get(key), str) and row.get(key)
    )
    literal_hits = [
        literal
        for literal in concept.literals
        if any(_literal_in_field(field, literal) for field in fields)
    ]
    pair_hits = [
        {"left": left, "right": right}
        for left, right in concept.pairs
        if any(_pair_within_five(field, left, right) for field in fields)
    ]
    return {
        "visible": bool(literal_hits or pair_hits),
        "literal_hits": literal_hits,
        "exact_pair_hits": pair_hits,
    }


def _noise_investigation(partition_id: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    factor_groups = queries.MAIN_FACTORS[partition_id]
    factor_counts = Counter()
    all_visible: list[str] = []
    pair_positive: list[str] = []
    type_counts = Counter()
    for row in records:
        identifier = str(row["paperId"])
        group_ok = []
        for group in factor_groups:
            present = any(_concept_presence(row, name)["visible"] for name in group)
            factor_counts[_factor_label(group)] += int(present)
            group_ok.append(present)
        if all(group_ok):
            all_visible.append(identifier)
        if any(queries.CONCEPTS[name].pairs for group in factor_groups for name in group):
            if any(
                _concept_presence(row, name)["exact_pair_hits"]
                for group in factor_groups
                for name in group
            ):
                pair_positive.append(identifier)
        value = row.get("documentType")
        type_counts[str(value) if value else "unlabelled"] += 1

    return {
        "threshold_exceeded": len(records) > 100,
        "retained_broad_union_count": len(records),
        "visible_metadata": {
            "fields": ["title", "abstract"],
            "factor_visible_counts": dict(sorted(factor_counts.items())),
            "all_scheduled_factor_groups_visible_count": len(all_visible),
            "all_scheduled_factor_groups_visible_stable_ids": sorted(all_visible, key=str.casefold),
            "any_declared_pair_within_five_tokens_in_one_visible_field_count": len(pair_positive),
            "document_type_labels_observed": dict(sorted(type_counts.items())),
        },
        "no_loss_precision_refinement": {
            "method": "dual-lane visible Title/Abstract metadata priority subset",
            "priority_subset_count": len(all_visible),
            "priority_subset_stable_ids": sorted(all_visible, key=str.casefold),
            "preservation_rule": "The source-native broad canonical-ID union remains authoritative. Metadata-negative/body-only matches are retained rather than discarded, so the refinement cannot lose a source match.",
            "source_field_limit": "Link validates a Title advanced field but exposes no independently validated Abstract-only field. A source Title restriction would lose abstract/body matches, so it was not adopted.",
            "pair_limit": "Link has no supported proximity operator. The local Title/Abstract check tests declared pairs in either order with at most five intervening lexical tokens; body-text pair status remains unknown.",
            "filters_not_applied": ["content type", "access", "full text availability", "controlled taxonomy", "publication type"],
        },
    }


def build_receipts(searches: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    queries.assert_lossless_cell_membership()
    plans = event_plan()
    all_partitions: dict[str, dict[str, Any]] = {}
    noise_entries: dict[str, Any] = {}

    for partition_id in queries.SCHEDULE_IDS:
        event_rows: list[dict[str, Any]] = []
        records_by_id: dict[str, dict[str, Any]] = {}
        occurrences = 0
        for spec in plans[partition_id]:
            data, event = _read_complete_event(searches, spec)
            event_rows.append(event)
            for row in data["results"]:
                assert isinstance(row, dict)
                identifier = str(row["paperId"])
                occurrences += 1
                records_by_id.setdefault(identifier.casefold(), row)

        canonical_ids = sorted(
            (str(row["paperId"]) for row in records_by_id.values()), key=str.casefold
        )
        canonical_id_digest = _digest("\n".join(canonical_ids).encode("utf-8"))
        retained_records = [records_by_id[item.casefold()] for item in canonical_ids]
        status = "complete_successful_cell_union"
        explicit_null_failure: list[dict[str, Any]] = []
        if partition_id == "BT2":
            status = "repaired_route_failure_with_retained_partial_union"
            explicit_null_failure = [BT2_NULL_FAILURE]

        entry = {
            "partition_id": partition_id,
            "planned_boolean_query": queries.direct_query(partition_id),
            "event_count": len(event_rows),
            "events": [
                {
                    key: value
                    for key, value in event.items()
                    if key not in {"stable_ids"}
                }
                | {"stable_id_count": len(event["stable_ids"]), "stable_ids_sha256": _digest("\n".join(event["stable_ids"]).encode("utf-8"))}
                for event in event_rows
            ],
            "raw_source_event_total_sum": sum(
                event["source_total"] for event in event_rows if isinstance(event["source_total"], int)
            ),
            "retained_event_row_count": occurrences,
            "unique_canonical_stable_id_count": len(canonical_ids),
            "overlap_occurrence_count": occurrences - len(canonical_ids),
            "canonical_stable_ids": canonical_ids,
            "canonical_stable_ids_sha256": canonical_id_digest,
            "status": status,
            "explicit_null_failures": explicit_null_failure,
        }
        all_partitions[partition_id] = entry
        if len(canonical_ids) > 100:
            noise_entries[partition_id] = _noise_investigation(partition_id, retained_records)

    receipt = {
        "schema_version": "springer-pilot003-canonical-unions/v1",
        "pilot": "003",
        "source": SOURCE,
        "mode": "pilot_only_not_final_search",
        "date_window": {"start": queries.DATE_START, "end": queries.DATE_END},
        "controls": {
            "language": "En source facet, with English full-text screening still required",
            "content": "broad whole platform; no content-type filter",
            "access": "no access or full-text-availability filter",
            "sort": "oldestFirst",
            "identity": "repaired two-pass canonical path verification before every normal output",
            "wildcard": "not used or accepted in any partition",
        },
        "partitions": all_partitions,
    }
    receipt["receipt_sha256"] = _digest(_canonical_json(receipt))

    noise = {
        "schema_version": "springer-pilot003-noise-investigation/v1",
        "pilot": "003",
        "source": SOURCE,
        "threshold": 100,
        "threshold_basis": "deduplicated retained canonical stable-ID union within a semantic partition",
        "investigations": noise_entries,
    }
    noise["receipt_sha256"] = _digest(_canonical_json(noise))
    return receipt, noise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--searches-dir", type=Path, default=SEARCHES)
    parser.add_argument("--union-output", type=Path, required=True)
    parser.add_argument("--noise-output", type=Path, required=True)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="rebuild and compare existing create-only receipts without writing",
    )
    args = parser.parse_args()
    receipt, noise = build_receipts(args.searches_dir)
    if args.verify:
        observed_receipt = json.loads(args.union_output.read_text(encoding="utf-8"))
        observed_noise = json.loads(args.noise_output.read_text(encoding="utf-8"))
        if observed_receipt != receipt or observed_noise != noise:
            raise ValueError("Persisted Pilot 003 receipt differs from rebuilt source artifacts")
        print(json.dumps({"status": "verified", "receipt_sha256": receipt["receipt_sha256"], "noise_sha256": noise["receipt_sha256"]}, indent=2))
        return 0
    _write_new_json(args.union_output, receipt)
    try:
        _write_new_json(args.noise_output, noise)
    except BaseException:
        # Do not leave an apparently complete receipt without its linked noise
        # investigation.  The receipt was create-only, so safe removal is
        # limited to the file this invocation just wrote.
        args.union_output.unlink(missing_ok=True)
        raise
    print(
        json.dumps(
            {
                "status": "success",
                "union_output": str(args.union_output),
                "noise_output": str(args.noise_output),
                "partitions": {
                    key: {
                        "status": value["status"],
                        "unique_canonical_stable_id_count": value["unique_canonical_stable_id_count"],
                    }
                    for key, value in receipt["partitions"].items()
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
