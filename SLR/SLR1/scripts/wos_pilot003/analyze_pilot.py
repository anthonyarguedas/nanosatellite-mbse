#!/usr/bin/env python3
"""Reconcile Web of Science Pilot 003 source events without candidate import.

The adapter's normalized public artifacts retain ordered result rows and a
PRISMA-S receipt.  This script reconstructs the ordered WOS/UT ledgers from
those rows, checks the exact planned raw query and receipt totals, and writes
pilot-only reconciliation, cutoff, local NEAR/6, known-item, and >100
investigation artifacts.  It never changes a source event or labels a pilot
set as a final candidate set.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

from queries import (
    DIAGNOSTIC_CUTOFF,
    MAIN_IDS,
    PSR_IDS,
    RENDERER,
    SLR1_DIR,
    event_by_name,
    events,
    pilot_schedule,
)


PILOT_ROOT = SLR1_DIR / "source-specific" / "web-of-science-core-collection" / "pilots" / "003"
SEARCH_ROOT = PILOT_ROOT / "searches"
ANALYSIS_ROOT = SEARCH_ROOT / "analysis"
SCHEMA_PREFIX = "slr1-wos-pilot-003"
WOS_ID = re.compile(r"^WOS:[A-Za-z0-9]+$")
TOKEN = re.compile(r"[a-z0-9]+")

PAIR_BLOCKS: dict[tuple[str, str], tuple[str, ...]] = {
    ("main", "BG1"): ("G_model",),
    ("main", "BG2"): ("G_structure",),
    ("main", "BC1"): ("C1",),
    ("main", "BT2"): ("T2",),
    ("psr", "PSR4"): ("G_model", "G_structure", "C1"),
}

A1_KNOWN_ID = "WOS:001027247800008"
BURUSO_DOI = "10.1002/sys.70051"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def ordered_id_digest(ids: Iterable[str]) -> str:
    digest = sha256()
    for identifier in ids:
        encoded = identifier.encode("ascii")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


def artifact_path(namespace: str, partition_id: str) -> Path:
    return SEARCH_ROOT / namespace / f"{partition_id}.json"


def normalize_doi(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    normalized = value.strip().casefold()
    normalized = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", normalized)
    return normalized.rstrip(" .")


def compact_event(namespace: str, partition_id: str) -> dict[str, Any]:
    """Validate one normalized adapter artifact and retain an ordered ID ledger."""
    path = artifact_path(namespace, partition_id)
    payload = load(path)
    metadata = payload.get("output_metadata")
    receipt = metadata.get("prisma_search_run") if isinstance(metadata, dict) else None
    planned = event_by_name(namespace, partition_id)
    errors: list[str] = []
    total = payload.get("total")
    rows = payload.get("results")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        errors.append("source total is null or invalid")
    if not isinstance(rows, list):
        errors.append("results are absent")
        rows = []
    ids: list[str] = []
    for expected_rank, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"row {expected_rank} is not an object")
            continue
        identifier = row.get("paperId")
        if not isinstance(identifier, str) or not WOS_ID.fullmatch(identifier):
            errors.append(f"row {expected_rank} lacks canonical WOS/UT ID")
            continue
        if row.get("rank") != expected_rank:
            errors.append(f"row {expected_rank} does not retain source rank")
        ids.append(identifier)
    if isinstance(total, int) and len(ids) != total:
        errors.append("ordered result-row ID count does not equal source total")
    if len(set(ids)) != len(ids):
        errors.append("event contains repeated stable IDs")
    if not isinstance(metadata, dict) or metadata.get("status") != "success":
        errors.append("normalized source status is not success")
    if not isinstance(receipt, dict):
        errors.append("PRISMA-S receipt is absent")
    else:
        strategy = receipt.get("strategy", {})
        staged = receipt.get("staged_counts", {})
        if strategy.get("executed_query") != planned.executed_query:
            errors.append("receipt query differs from the deterministic raw plan")
        if receipt.get("completion_status") != "complete":
            errors.append("receipt is not complete")
        if staged.get("source_reported_total") != total:
            errors.append("receipt source total differs from artifact total")
        if staged.get("source_reported_total_exact") is not True:
            errors.append("receipt does not mark source total exact")
        scope = strategy.get("search_scope", {})
        controls = scope.get("controls", {}) if isinstance(scope, dict) else {}
        editions = controls.get("editions", {}) if isinstance(controls, dict) else {}
        requested_editions = scope.get("editions_requested") if isinstance(scope, dict) else None
        effective = editions.get("effective") if isinstance(editions, dict) else None
        if requested_editions != ["All"]:
            errors.append("source did not request all current editions")
        if not isinstance(effective, list) or not effective:
            errors.append("all-current-editions source readback is absent")
        if total != 0 and strategy.get("sort", {}).get("value") != "Date: oldest first":
            errors.append("native oldest-first sort readback is absent")
        fields = strategy.get("query_fields", []) if isinstance(strategy, dict) else []
        if namespace == "main" and fields != ["TS", "PY", "LA"]:
            errors.append(f"main query fields differ from TS/PY/LA: {fields!r}")
        if namespace == "psr" and fields != ["TS", "PY"]:
            errors.append(f"PSR query fields differ from TS/PY: {fields!r}")
    source_status = "complete_two_pass_requested" if not errors else "invalid_or_incomplete"
    # The run script uses --require-complete for every event.  The adapter
    # finalizer compacts its internal two-pass ledger into the public receipt;
    # row order, exact total, and native-artifact receipt are retained here.
    native = receipt.get("native_artifact", {}) if isinstance(receipt, dict) else {}
    if source_status == "complete_two_pass_requested" and total and not native:
        errors.append("nonzero complete event lacks native RIS receipt")
        source_status = "invalid_or_incomplete"
    return {
        "namespace": namespace,
        "partition_id": partition_id,
        "artifact": str(path.relative_to(PILOT_ROOT)),
        "artifact_sha256": canonical_json_digest(payload),
        "raw_query_sha256": planned.query_sha256,
        "raw_query": planned.executed_query,
        "translation": planned.translation,
        "source_status": source_status,
        "source_total": total if not errors else None,
        "ordered_wos_ids": ids if not errors else None,
        "ordered_wos_ids_sha256": ordered_id_digest(ids) if not errors else None,
        "source_row_count": len(rows),
        "receipt_completion_status": receipt.get("completion_status") if isinstance(receipt, dict) else None,
        "editions_requested": (
            receipt.get("strategy", {}).get("search_scope", {}).get("editions_requested")
            if isinstance(receipt, dict)
            else None
        ),
        "editions": (
            receipt.get("strategy", {}).get("search_scope", {}).get("controls", {}).get("editions", {}).get("effective")
            if isinstance(receipt, dict)
            else None
        ),
        "source_sort": receipt.get("strategy", {}).get("sort", {}).get("value") if isinstance(receipt, dict) else None,
        "native_artifact": native if isinstance(native, dict) else None,
        "errors": errors,
    }


def union_for(event_records: dict[str, dict[str, Any]], partition_ids: Iterable[str]) -> dict[str, Any]:
    ordered: list[str] = []
    members: dict[str, list[str]] = defaultdict(list)
    source_events = 0
    incomplete: list[str] = []
    for partition_id in partition_ids:
        record = event_records[partition_id]
        total = record.get("source_total")
        identifiers = record.get("ordered_wos_ids")
        if not isinstance(total, int) or not isinstance(identifiers, list):
            incomplete.append(partition_id)
            continue
        source_events += total
        for identifier in identifiers:
            members[identifier].append(partition_id)
            if len(members[identifier]) == 1:
                ordered.append(identifier)
    ordering = {
        "partition_order": list(partition_ids),
        "within_partition_order": "adapter-verified native Date: oldest first source rank",
        "union_order": "first occurrence in the declared partition order, retaining within-partition source rank",
    }
    if incomplete:
        return {
            "status": "null_due_to_event_failure_or_validation_error",
            "ordering": ordering,
            "incomplete_partitions": incomplete,
            "source_event_total": None,
            "deduplicated_total": None,
            "ordered_wos_ids": None,
            "ordered_wos_ids_sha256": None,
            "membership": None,
        }
    return {
        "status": "reconciled",
        "ordering": ordering,
        "incomplete_partitions": [],
        "source_event_total": source_events,
        "deduplicated_total": len(ordered),
        "duplicate_event_occurrences": source_events - len(ordered),
        "ordered_wos_ids": ordered,
        "ordered_wos_ids_sha256": ordered_id_digest(ordered),
        "membership": [
            {"wos_id": identifier, "partitions": members[identifier], "first_partition": members[identifier][0]}
            for identifier in ordered
        ],
    }


def namespace_reconciliation(namespace: str, ids: tuple[str, ...]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    event_records = {partition_id: compact_event(namespace, partition_id) for partition_id in ids}
    overall = union_for(event_records, ids)
    result: dict[str, Any] = {
        "partition_order": list(ids),
        "events": [event_records[partition_id] for partition_id in ids],
        "union": overall,
    }
    if namespace == "main":
        result["semantic_unions"] = {
            "stream_A": union_for(event_records, ("A1", "A2", "A3")),
            "core_stream_B": union_for(event_records, ("B1", "B2")),
            "expanded_stream_B": union_for(event_records, ("BG1", "BG2", "BC1", "BT2")),
        }
    return result, event_records


def tokenise(value: Any) -> list[str]:
    return TOKEN.findall(value.casefold()) if isinstance(value, str) else []


def phrase_occurrences(phrase: str, tokens: list[str]) -> list[tuple[int, int]]:
    wanted = tokenise(phrase)
    if not wanted or len(wanted) > len(tokens):
        return []
    width = len(wanted)
    return [
        (start, start + width - 1)
        for start in range(len(tokens) - width + 1)
        if tokens[start : start + width] == wanted
    ]


def pair_hits(left: str, right: str, tokens: list[str]) -> list[int]:
    gaps: list[int] = []
    for left_start, left_end in phrase_occurrences(left, tokens):
        for right_start, right_end in phrase_occurrences(right, tokens):
            if left_end < right_start:
                gaps.append(right_start - left_end - 1)
            elif right_end < left_start:
                gaps.append(left_start - right_end - 1)
    return gaps


def local_pair_observation(row: dict[str, Any], concept_name: str) -> dict[str, Any]:
    concept = pilot_schedule.CONCEPTS[concept_name]
    fields = {"title": row.get("title"), "snippet": row.get("snippet")}
    fixed_hits: list[dict[str, str]] = []
    strict_pairs: list[dict[str, Any]] = []
    six_pairs: list[dict[str, Any]] = []
    for field_name, value in fields.items():
        tokens = tokenise(value)
        if not tokens:
            continue
        for literal in concept.literals:
            if phrase_occurrences(literal, tokens):
                fixed_hits.append({"field": field_name, "literal": literal})
        for left, right in concept.pairs:
            gaps = pair_hits(left, right, tokens)
            if not gaps:
                continue
            min_gap = min(gaps)
            descriptor = {"field": field_name, "left": left, "right": right, "minimum_separating_tokens": min_gap}
            if min_gap <= 5:
                strict_pairs.append(descriptor)
            elif min_gap == 6:
                six_pairs.append(descriptor)
    if strict_pairs:
        state = "strict_pair_visible_within_five"
    elif fixed_hits:
        state = "fixed_literal_visible_pair_not_required"
    elif six_pairs:
        state = "fallback_only_gap_six_visible"
    else:
        state = "not_verifiable_from_retained_title_or_snippet"
    return {
        "concept": concept_name,
        "state": state,
        "fixed_literal_hits": fixed_hits,
        "strict_pair_hits": strict_pairs,
        "gap_six_pair_hits": six_pairs,
    }


def near6_validation() -> dict[str, Any]:
    event_audits: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    for (namespace, partition_id), concepts in PAIR_BLOCKS.items():
        payload = load(artifact_path(namespace, partition_id))
        observations = []
        for row in payload.get("results", []):
            if not isinstance(row, dict):
                continue
            per_concept = [local_pair_observation(row, concept) for concept in concepts]
            states = [observation["state"] for observation in per_concept]
            if "strict_pair_visible_within_five" in states:
                state = "strict_pair_visible_within_five"
            elif "fixed_literal_visible_pair_not_required" in states:
                state = "fixed_literal_visible_pair_not_required"
            elif "fallback_only_gap_six_visible" in states:
                state = "fallback_only_gap_six_visible"
            else:
                state = "not_verifiable_from_retained_title_or_snippet"
            totals[state] += 1
            observations.append(
                {
                    "wos_id": row.get("paperId"),
                    "event_rank": row.get("rank"),
                    "state": state,
                    "concept_observations": per_concept,
                }
            )
        event_audits.append(
            {
                "namespace": namespace,
                "partition_id": partition_id,
                "pair_blocks": list(concepts),
                "records_examined": len(observations),
                "state_counts": dict(Counter(item["state"] for item in observations)),
                "records": observations,
            }
        )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-near6-local-validation/v1",
        "pilot": "003",
        "do_not_merge": True,
        "rule": "Protocol pairs require no more than five intervening lexical tokens. Native TS NEAR/6 is a conservative unordered fallback that can admit one extra token.",
        "local_fields": [
            "normalized result title",
            "normalized visible result snippet only; it is not assumed to be a complete abstract, author-keyword, or Keywords Plus field",
        ],
        "states": {
            "strict_pair_visible_within_five": "A declared pair was locally visible in one retained field with <=5 intervening normalized tokens.",
            "fallback_only_gap_six_visible": "A locally visible declared pair had exactly six intervening normalized tokens; this may be an extra native-fallback candidate, not proof of the native match trigger.",
            "fixed_literal_visible_pair_not_required": "A non-pair alternative in that paired block was locally visible.",
            "not_verifiable_from_retained_title_or_snippet": "No conclusion about the source match; Topic can match unretained abstract/keyword/indexed fields or source-normalized text.",
        },
        "overall_state_counts": dict(totals),
        "events": event_audits,
        "limitation": "This is a local no-loss/fallback audit where retained fields permit. It neither reclassifies records nor claims that an unobservable pair is absent from the source Topic fields.",
    }


def cutoff_screening() -> dict[str, Any]:
    plan = load(ANALYSIS_ROOT / "cutoff-control-plan.json")
    before = load(ANALYSIS_ROOT / f"cutoff-on-or-before-{DIAGNOSTIC_CUTOFF}.json")
    after = load(ANALYSIS_ROOT / f"cutoff-after-{DIAGNOSTIC_CUTOFF}.json")
    retained = plan.get("ordered_retained_2026_wos_ids", [])
    before_ids = {row.get("paperId") for row in before.get("results", []) if isinstance(row, dict)}
    after_ids = {row.get("paperId") for row in after.get("results", []) if isinstance(row, dict)}
    manifestations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in events():
        payload = load(artifact_path(item.namespace, item.partition_id))
        for row in payload.get("results", []):
            if isinstance(row, dict) and row.get("year") == 2026 and isinstance(row.get("paperId"), str):
                manifestations[row["paperId"]].append(
                    {
                        "namespace": item.namespace,
                        "partition_id": item.partition_id,
                        "rank": row.get("rank"),
                        "publication_date_projection": row.get("publicationDate"),
                    }
                )
    screened = []
    classifications: Counter[str] = Counter()
    for identifier in retained:
        if identifier in before_ids and identifier not in after_ids:
            status = "native_DOP_on_or_before_2026-08-29"
        elif identifier in after_ids and identifier not in before_ids:
            status = "native_DOP_after_2026-08-29"
        elif identifier in before_ids and identifier in after_ids:
            status = "conflicting_native_DOP_controls"
        else:
            status = "unresolved_by_native_DOP_controls"
        classifications[status] += 1
        screened.append({"wos_id": identifier, "cutoff_status": status, "source_event_manifestations": manifestations.get(identifier, [])})
    all_main_ids: set[str] = set()
    all_psr_ids: set[str] = set()
    core_b_ids: set[str] = set()
    for item in events():
        payload = load(artifact_path(item.namespace, item.partition_id))
        target = all_main_ids if item.namespace == "main" else all_psr_ids
        identifiers = {
            row.get("paperId")
            for row in payload.get("results", [])
            if isinstance(row, dict) and isinstance(row.get("paperId"), str)
        }
        target.update(identifiers)
        if item.namespace == "main" and item.partition_id in {"B1", "B2"}:
            core_b_ids.update(identifiers)
    post_cutoff_ids = after_ids - before_ids
    scope_effects = {
        "main_raw_union": {
            "raw_deduplicated_ids": len(all_main_ids),
            "DOP_after_cutoff_ids": len(all_main_ids & post_cutoff_ids),
            "diagnostic_cutoff_screened_ids": len(all_main_ids - post_cutoff_ids),
        },
        "main_core_stream_B": {
            "raw_deduplicated_ids": len(core_b_ids),
            "DOP_after_cutoff_ids": len(core_b_ids & post_cutoff_ids),
            "diagnostic_cutoff_screened_ids": len(core_b_ids - post_cutoff_ids),
        },
        "supporting_PSR_union": {
            "raw_deduplicated_ids": len(all_psr_ids),
            "DOP_after_cutoff_ids": len(all_psr_ids & post_cutoff_ids),
            "diagnostic_cutoff_screened_ids": len(all_psr_ids - post_cutoff_ids),
        },
    }
    return {
        "schema_version": f"{SCHEMA_PREFIX}-cutoff-screening/v1",
        "pilot": "003",
        "do_not_merge": True,
        "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
        "input_controls": {
            "plan": "cutoff-control-plan.json",
            "on_or_before": f"cutoff-on-or-before-{DIAGNOSTIC_CUTOFF}.json",
            "after": f"cutoff-after-{DIAGNOSTIC_CUTOFF}.json",
        },
        "retained_2026_unique_wos_ids": len(retained),
        "classification_counts": dict(classifications),
        "scope_effects": scope_effects,
        "records": screened,
        "interpretation": "All raw PY=(...-2026) event memberships remain preserved. The scope effects show a diagnostic exact-date view only; they do not create a final or imported candidate set.",
        "limitation": "Clarivate documents DOP as a calendar publication-date field with inclusive ranges, but its Early Access/final-date basis is not universally documented. A DOP result is reported as source screening evidence, not silently converted into a universal date rule.",
    }


def known_item_check(main_events: dict[str, dict[str, Any]], psr_events: dict[str, dict[str, Any]]) -> dict[str, Any]:
    a1_ids = main_events["A1"].get("ordered_wos_ids") or []
    buruso_hits = []
    for partition_id in PSR_IDS:
        payload = load(artifact_path("psr", partition_id))
        for row in payload.get("results", []):
            if isinstance(row, dict) and normalize_doi(row.get("doi")) == BURUSO_DOI:
                buruso_hits.append(
                    {
                        "partition_id": partition_id,
                        "wos_id": row.get("paperId"),
                        "rank": row.get("rank"),
                        "title": row.get("title"),
                        "publication_date_projection": row.get("publicationDate"),
                    }
                )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-known-item-check/v1",
        "pilot": "003",
        "do_not_merge": True,
        "checks": {
            "A1_prior_pilot_known_record": {
                "wos_id": A1_KNOWN_ID,
                "source": "Pilot 002 literal/wildcard stable-ID comparison",
                "result": "retrieved" if A1_KNOWN_ID in a1_ids else "not_retrieved",
                "A1_event_status": main_events["A1"].get("source_status"),
            },
            "PSR_Buruso_2026": {
                "doi": BURUSO_DOI,
                "title": "Model-Based Systems Engineering in Space Applications: A Comprehensive Literature Review",
                "result": "retrieved_by_successful_PSR_union" if buruso_hits else "not_retrieved_by_successful_PSR_union",
                "hits": buruso_hits,
                "manual_insertion": False,
                "interpretation": "The known item is validation-only and remains a supporting-search record only through its successful PSR discovery events.",
            },
        },
    }


def scope_membership_counts(union: dict[str, Any], relevant: tuple[str, ...]) -> dict[str, int]:
    if union.get("status") != "reconciled":
        return {}
    counts: Counter[str] = Counter()
    relevant_set = set(relevant)
    for item in union.get("membership", []):
        memberships = [value for value in item["partitions"] if value in relevant_set]
        if memberships:
            counts[" + ".join(memberships)] += 1
    return dict(sorted(counts.items()))


def high_volume_investigation(main: dict[str, Any], psr: dict[str, Any], cutoff: dict[str, Any], near6: dict[str, Any]) -> dict[str, Any]:
    candidate_scopes: list[tuple[str, tuple[str, ...], dict[str, Any]]] = [
        ("main_core_stream_B", ("B1", "B2"), main["semantic_unions"]["core_stream_B"]),
        ("main_all_nine_partitions", MAIN_IDS, main["union"]),
        ("supporting_PSR_union", PSR_IDS, psr["union"]),
    ]
    cutoff_by_id = {item["wos_id"]: item["cutoff_status"] for item in cutoff["records"]}
    refinements = []
    for name, partitions, union in candidate_scopes:
        total = union.get("deduplicated_total")
        if not isinstance(total, int) or total <= 100:
            continue
        ids = union.get("ordered_wos_ids") or []
        cutoff_counts = Counter(cutoff_by_id[identifier] for identifier in ids if identifier in cutoff_by_id)
        refinements.append(
            {
                "scope": name,
                "partitions": list(partitions),
                "deduplicated_stable_id_total": total,
                "source_event_total": union.get("source_event_total"),
                "duplicate_event_occurrences": union.get("duplicate_event_occurrences"),
                "membership_pattern_counts": scope_membership_counts(union, partitions),
                "2026_cutoff_screening_counts_within_scope": dict(cutoff_counts),
                "investigation": {
                    "stable_id_reconciliation": "Complete event-ledger IDs were deduplicated in declared partition order; no prefix or count-only set was substituted.",
                    "query_refinement": "No type, subject, access, language, or candidate-DT narrowing was run. The raw planned partitions remain the evidence; this is a non-narrowing local membership investigation.",
                    "paired_term_audit": "See near6-local-validation.json for each observable retained-field pair check; missing visible text is not called a false match.",
                },
            }
        )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-high-volume-investigation/v1",
        "pilot": "003",
        "do_not_merge": True,
        "threshold": 100,
        "threshold_rule": "Investigate a reconciled, deduplicated stable-ID set only when it exceeds 100; raw overlapping discovery-event totals are not substituted for deduplicated counts.",
        "refinements": refinements,
        "near6_artifact": "near6-local-validation.json",
        "cutoff_artifact": "cutoff-screening.json",
        "limitation": "This investigation does not adjudicate scientific eligibility, screen title/abstract relevance, or authorize a narrower final translation.",
    }


def write_create_only(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main() -> int:
    ANALYSIS_ROOT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "reconciliation": ANALYSIS_ROOT / "reconciliation.json",
        "near6": ANALYSIS_ROOT / "near6-local-validation.json",
        "cutoff": ANALYSIS_ROOT / "cutoff-screening.json",
        "known": ANALYSIS_ROOT / "known-item-check.json",
        "high_volume": ANALYSIS_ROOT / "high-volume-investigation.json",
    }
    for path in outputs.values():
        if path.exists():
            raise SystemExit(f"Refusing to overwrite analysis artifact: {path}")
    main_reconciliation, main_events = namespace_reconciliation("main", MAIN_IDS)
    psr_reconciliation, psr_events = namespace_reconciliation("psr", PSR_IDS)
    reconciliation = {
        "schema_version": f"{SCHEMA_PREFIX}-reconciliation/v1",
        "pilot": "003",
        "source": "Web of Science Core Collection",
        "diagnostic_cutoff": DIAGNOSTIC_CUTOFF,
        "do_not_merge": True,
        "capture_contract": {
            "runner": "scripts/wos_pilot003/run_pilot.py",
            "require_complete": True,
            "description": "Every event was invoked with --require-complete, which makes the adapter perform two complete ordered WOS-ID passes before publishing its normalized receipt.",
            "public_artifact_boundary": "The adapter's normalized pilot artifact retains ordered ranked result IDs, exact source total, native RIS digest, and complete receipt; internal per-pass ledgers remain adapter-execution evidence rather than a licensed export.",
        },
        "main": main_reconciliation,
        "prior_secondary_reviews": psr_reconciliation,
        "limitations": [
            "Pilot records are diagnostic only and do not form a final primary-evidence or supporting-search import.",
            "Raw main events use PY=(2011-2026) and LA=(English); all 2026 records are retained pending the separate exact-date screening artifact.",
            "PSR events use the Core Collection source-inception PY=(1900-2026) control, with no main-review lower bound and no language/type/subject/access/peer-review filter.",
        ],
    }
    near6 = near6_validation()
    cutoff = cutoff_screening()
    known = known_item_check(main_events, psr_events)
    high_volume = high_volume_investigation(main_reconciliation, psr_reconciliation, cutoff, near6)
    for name, payload in (
        ("reconciliation", reconciliation),
        ("near6", near6),
        ("cutoff", cutoff),
        ("known", known),
        ("high_volume", high_volume),
    ):
        write_create_only(outputs[name], payload)
    summary = {
        "saved": {name: str(path) for name, path in outputs.items()},
        "main_union": main_reconciliation["union"].get("deduplicated_total"),
        "psr_union": psr_reconciliation["union"].get("deduplicated_total"),
        "high_volume_refinements": len(high_volume["refinements"]),
        "near6_state_counts": near6["overall_state_counts"],
        "cutoff_counts": cutoff["classification_counts"],
        "buruso_hits": len(known["checks"]["PSR_Buruso_2026"]["hits"]),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
