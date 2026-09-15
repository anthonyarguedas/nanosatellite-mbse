#!/usr/bin/env python3
"""Build the predeclared projected Pilot 008 Topic corpus plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return value


def canonical_doi(value: str) -> str:
    return value.strip().casefold().split("@", 1)[0]


def result_ids(data: dict[str, Any]) -> set[str]:
    output = set()
    for record in data.get("results", []):
        value = record.get("sourceRecordStableId") or record.get("doi")
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError("Source result lacks a stable DOI")
        output.add(canonical_doi(value))
    return output


def successful_attempt(base: Path) -> tuple[Path, dict[str, Any]]:
    candidates = [base, *(base.with_name(f"{base.stem}-retry{i}{base.suffix}") for i in range(1, 20))]
    successes = []
    for candidate in candidates:
        if not candidate.exists():
            continue
        data = load(candidate)
        if isinstance(data.get("total"), int):
            successes.append((candidate, data))
    if len(successes) != 1:
        raise RuntimeError(f"Expected one successful artifact for {base}, got {len(successes)}")
    return successes[0]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode())


def slug(value: str) -> str:
    return "-".join(part for part in value.casefold().replace("&", " and ").split() if part)


def doi_query(dois: list[str]) -> str:
    return "(" + " OR ".join(f'"{doi}"' for doi in dois) + ")"


def title_query(titles: list[str]) -> str:
    if any('"' in title or not title.strip() for title in titles):
        raise RuntimeError("Projected corpus plan cannot quote one or more titles")
    return "(" + " OR ".join(f'"{title}"' for title in titles) + ")"


def event(source: dict[str, Any], topic: dict[str, str] | None) -> dict[str, Any]:
    chunk_id = source["chunk_id"]
    dois = source["expected_canonical_dois"]
    titles = source["expected_source_titles"]
    doi_text = doi_query(dois)
    title_text = title_query(titles)
    suffix = "baseline" if topic is None else f"topic-{slug(topic['label'])}"
    event_id = f"{chunk_id}-{suffix}"
    serialized = f"Anywhere={doi_text} AND Title={title_text}"
    return {
        "event_id": event_id,
        "phase": "accepted_corpus_predeclared_projection_yield",
        "chunk_id": chunk_id,
        "expected_canonical_dois": dois,
        "expected_canonical_doi_count": len(dois),
        "expected_source_titles": titles,
        "field_rows": [
            {"field": "Anywhere", "source_field": "AllField", "text": doi_text},
            {"field": "Title", "source_field": "Title", "text": title_text},
        ],
        "serialized_query": serialized,
        "serialized_query_sha256": sha256_text(serialized),
        "topic_selection": topic,
        "projection": {
            "identity_field": "canonical DOI before an ARC virtual-collection suffix",
            "allowlist": dois,
            "outside_allowlist_policy": "retain_in_source_artifact_and_exclude_from_membership_denominator",
        },
        "mode": "card_preview",
        "output": f"searches/corpus-projected/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/corpus-projected/{event_id}.search-page.png",
            "results_page": f"searches/corpus-projected/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def build(pilot_root: Path, title_plan_path: Path) -> dict[str, Any]:
    title_plan_bytes = title_plan_path.read_bytes()
    title_plan = json.loads(title_plan_bytes)
    if title_plan.get("schema_version") != "aiaa-arc-pilot008-topic-title-corpus-plan/v1":
        raise RuntimeError("Unexpected Pilot 008 title corpus plan")
    title_events = title_plan.get("events")
    topics = title_plan.get("topic_selections")
    if not isinstance(title_events, list) or len(title_events) != 30 or not isinstance(topics, list) or len(topics) != 4:
        raise RuntimeError("Pilot 008 title corpus plan is incomplete")
    baselines = [event for event in title_events if event.get("topic_selection") is None]
    if len(baselines) != 6:
        raise RuntimeError("Pilot 008 title corpus plan lacks six baselines")

    trigger_ledger = []
    for source in baselines:
        base = pilot_root / source["output"]
        artifact, data = successful_attempt(base)
        observed = result_ids(data)
        expected = set(source["expected_canonical_dois"])
        missing = expected - observed
        extras = observed - expected
        if missing:
            raise RuntimeError(f"{artifact}: title baseline missed expected corpus records {sorted(missing)}")
        trigger_ledger.append({
            "chunk_id": source["chunk_id"],
            "artifact": str(artifact.relative_to(pilot_root)),
            "source_total": data["total"],
            "observed_canonical_doi_count": len(observed),
            "expected_canonical_doi_count": len(expected),
            "outside_allowlist_canonical_doi_count": len(extras),
            "outside_allowlist_canonical_dois": sorted(extras),
        })
    if not any(entry["outside_allowlist_canonical_doi_count"] for entry in trigger_ledger):
        raise RuntimeError("Predeclared projection trigger is absent")

    events = []
    for source in baselines:
        events.append(event(source, None))
        events.extend(event(source, topic) for topic in topics)
    if len(events) != 30 or len({entry["event_id"] for entry in events}) != 30:
        raise RuntimeError("Projected corpus plan must contain 30 unique events")
    accepted_dois = sorted({doi for source in baselines for doi in source["expected_canonical_dois"]})
    if len(accepted_dois) != 119:
        raise RuntimeError("Projected corpus plan does not contain 119 accepted DOIs")

    return {
        "schema_version": "aiaa-arc-pilot008-topic-projected-corpus-plan/v1",
        "source": title_plan["source"],
        "pilot": "008",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Measure Topic assignment within the fixed 119-DOI accepted corpus using paired "
            "DOI/Title source rows and a canonical-DOI projection declared before these source calls."
        ),
        "date_window": title_plan["date_window"],
        "projection_trigger": {
            "title_plan": str(title_plan_path),
            "title_plan_sha256": sha256_bytes(title_plan_bytes),
            "finding": (
                "All exact-title baselines retrieved their expected corpus DOIs. One ordinary phrase "
                "also matched broader titles, and source correction records can contain the original title."
            ),
            "baseline_ledger": trigger_ledger,
            "outside_allowlist_canonical_doi_sum": sum(
                entry["outside_allowlist_canonical_doi_count"] for entry in trigger_ledger
            ),
            "projection_predeclared_before_projected_source_calls": True,
        },
        "accepted_corpus": {
            "canonical_doi_count": len(accepted_dois),
            "canonical_dois": accepted_dois,
            "canonical_dois_sha256": sha256_text("\n".join(accepted_dois) + "\n"),
            "chunk_count": len(baselines),
            "denominator_policy": (
                "For each paired event, intersect source-observed canonical DOIs with that event's "
                "predeclared chunk allowlist. Preserve every outside match in the source artifact and ledger."
            ),
        },
        "topic_selections": topics,
        "comparison": {
            "design": "paired complete source calls with predeclared canonical-DOI projection",
            "source_rows": "Anywhere DOI union AND Title exact-phrase union",
            "baseline_per_chunk": True,
            "one_filtered_event_per_distinct_topic_id_per_chunk": True,
            "multi_topic_union": "union projected separately filtered canonical DOI sets offline",
        },
        "controls": title_plan["controls"],
        "capture": title_plan["capture"],
        "acceptance_checks": [
            "Every baseline retrieves every canonical DOI in its predeclared chunk allowlist.",
            "Every projected Topic set is a subset of its paired projected baseline.",
            "Every outside-allowlist source match remains retained and is reported separately.",
            "Every typed Topic label visibly resolves to its predeclared numeric ConceptID.",
            "Every source event remains at most 100 and is captured completely.",
            "Every successful JSON has both mandatory sibling screenshots.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--title-plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root, args.title_plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
