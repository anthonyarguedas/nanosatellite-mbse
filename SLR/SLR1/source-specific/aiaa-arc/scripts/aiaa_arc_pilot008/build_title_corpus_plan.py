#!/usr/bin/env python3
"""Build the Pilot 008 exact-title repair for accepted-corpus Topic yield."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode())


def slug(value: str) -> str:
    return "-".join(part for part in value.casefold().replace("&", " and ").split() if part)


def exact_title_query(titles: list[str]) -> str:
    if any('"' in title or not title.strip() for title in titles):
        raise RuntimeError("Exact-title repair cannot quote one or more source titles")
    return "(" + " OR ".join(f'"{title}"' for title in titles) + ")"


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


def source_titles(pilot007_root: Path, accepted_dois: set[str]) -> dict[str, str]:
    titles: dict[str, set[str]] = defaultdict(set)
    assessment = load(pilot007_root / "searches" / "assessment.json")
    for cell in assessment.get("cell_ledger", []):
        path = pilot007_root / cell["artifact"]
        data = load(path)
        for record in data.get("results", []):
            raw_id = record.get("sourceRecordStableId") or record.get("doi")
            title = record.get("title")
            if not isinstance(raw_id, str) or not isinstance(title, str) or not title.strip():
                raise RuntimeError(f"{path}: result lacks DOI/title evidence")
            doi = canonical_doi(raw_id)
            if doi in accepted_dois:
                titles[doi].add(title.strip())
    missing = accepted_dois - set(titles)
    ambiguous = {doi: values for doi, values in titles.items() if len(values) != 1}
    if missing or ambiguous:
        raise RuntimeError(f"Pilot 007 title mapping failed: missing={sorted(missing)}, ambiguous={ambiguous}")
    return {doi: next(iter(titles[doi])) for doi in sorted(accepted_dois)}


def event(
    chunk_id: str,
    dois: list[str],
    titles: list[str],
    topic_selection: dict[str, str] | None,
) -> dict[str, Any]:
    query = exact_title_query(titles)
    suffix = "baseline" if topic_selection is None else f"topic-{slug(topic_selection['label'])}"
    event_id = f"{chunk_id}-{suffix}"
    return {
        "event_id": event_id,
        "phase": "accepted_corpus_title_anchor_yield",
        "chunk_id": chunk_id,
        "expected_canonical_dois": dois,
        "expected_canonical_doi_count": len(dois),
        "expected_source_titles": titles,
        "field_rows": [
            {"field": "Title", "source_field": "Title", "text": query}
        ],
        "serialized_query": f"Title={query}",
        "serialized_query_sha256": sha256_text(f"Title={query}"),
        "topic_selection": topic_selection,
        "mode": "card_preview",
        "output": f"searches/corpus-title/{event_id}.json",
        "screenshot_outputs": {
            "search_page": f"searches/corpus-title/{event_id}.search-page.png",
            "results_page": f"searches/corpus-title/{event_id}.results-page.png",
        },
        "do_not_merge": True,
    }


def build(
    pilot_root: Path,
    doi_plan_path: Path,
    pilot007_root: Path,
) -> dict[str, Any]:
    doi_plan_bytes = doi_plan_path.read_bytes()
    doi_plan = json.loads(doi_plan_bytes)
    if doi_plan.get("schema_version") != "aiaa-arc-pilot008-topic-corpus-plan/v1":
        raise RuntimeError("Unexpected Pilot 008 DOI corpus plan")
    chunks = doi_plan.get("accepted_corpus", {}).get("chunks")
    topics = doi_plan.get("trigger_evidence", {}).get("promoted_distinct_selections")
    if not isinstance(chunks, list) or len(chunks) != 6 or not isinstance(topics, list) or len(topics) != 4:
        raise RuntimeError("Pilot 008 DOI corpus plan is incomplete")

    trigger_ledger = []
    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        expected = set(chunk["canonical_dois"])
        base = pilot_root / "searches" / "corpus" / f"{chunk_id}-baseline.json"
        artifact, data = successful_attempt(base)
        observed = result_ids(data)
        missing = expected - observed
        extras = observed - expected
        if missing:
            raise RuntimeError(f"{artifact}: DOI baseline missed expected corpus records {sorted(missing)}")
        trigger_ledger.append({
            "chunk_id": chunk_id,
            "artifact": str(artifact.relative_to(pilot_root)),
            "source_total": data["total"],
            "expected_canonical_doi_count": len(expected),
            "observed_canonical_doi_count": len(observed),
            "unexpected_canonical_doi_count": len(extras),
            "unexpected_canonical_dois": sorted(extras),
        })
    if not any(entry["unexpected_canonical_doi_count"] for entry in trigger_ledger):
        raise RuntimeError("Exact-title repair trigger is absent")

    accepted_dois = {
        doi
        for chunk in chunks
        for doi in chunk["canonical_dois"]
    }
    if len(accepted_dois) != 119:
        raise RuntimeError("Accepted corpus does not contain 119 unique DOIs")
    titles = source_titles(pilot007_root, accepted_dois)

    events = []
    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        dois = chunk["canonical_dois"]
        chunk_titles = [titles[doi] for doi in dois]
        events.append(event(chunk_id, dois, chunk_titles, None))
        events.extend(event(chunk_id, dois, chunk_titles, topic) for topic in topics)
    if len(events) != 30 or len({entry["event_id"] for entry in events}) != 30:
        raise RuntimeError("Pilot 008 exact-title repair must contain 30 unique events")

    return {
        "schema_version": "aiaa-arc-pilot008-topic-title-corpus-plan/v1",
        "source": doi_plan["source"],
        "pilot": "008",
        "diagnostic_only": True,
        "do_not_merge": True,
        "objective": (
            "Repair the accepted-corpus membership probe with exact source-observed Title phrases, "
            "then measure each promoted Topic's yield within the 119 accepted Pilot 007 DOIs."
        ),
        "date_window": doi_plan["date_window"],
        "repair_trigger": {
            "doi_plan": str(doi_plan_path),
            "doi_plan_sha256": sha256_bytes(doi_plan_bytes),
            "finding": (
                "Every DOI chunk retrieved all expected corpus records, but Anywhere also matched "
                "references or hidden indexed occurrences and admitted records outside the corpus."
            ),
            "baseline_ledger": trigger_ledger,
            "unexpected_source_event_sum": sum(entry["unexpected_canonical_doi_count"] for entry in trigger_ledger),
            "repair_predeclared_before_title_source_calls": True,
        },
        "accepted_corpus": {
            "canonical_doi_count": len(accepted_dois),
            "canonical_dois_sha256": sha256_text("\n".join(sorted(accepted_dois)) + "\n"),
            "source_title_mapping": [
                {"canonical_doi": doi, "source_title": titles[doi]}
                for doi in sorted(titles)
            ],
            "source_title_mapping_sha256": sha256_text(
                "\n".join(f"{doi}\t{titles[doi]}" for doi in sorted(titles)) + "\n"
            ),
            "chunk_count": len(chunks),
            "chunks": chunks,
        },
        "topic_selections": topics,
        "comparison": {
            "design": "paired complete exact-title membership cells",
            "baseline_per_chunk": True,
            "one_filtered_event_per_distinct_topic_id_per_chunk": True,
            "multi_topic_union": "reconcile separately filtered canonical DOI sets offline",
        },
        "controls": doi_plan["controls"],
        "capture": doi_plan["capture"],
        "acceptance_checks": [
            "Every exact-title baseline chunk reproduces its complete predeclared canonical DOI set without outside canonical DOIs.",
            "Each Topic-filtered set is a subset of its paired exact-title baseline chunk.",
            "Every typed Topic label resolves visibly to its predeclared numeric ConceptID.",
            "Every event remains at most 100 records and is captured completely.",
            "Every successful JSON has both mandatory sibling screenshots.",
            "No Topic restriction is accepted if it excludes an accepted corpus record with unclassified eligibility.",
        ],
        "events": events,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--doi-plan", type=Path, required=True)
    parser.add_argument("--pilot007-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build(args.pilot_root, args.doi_plan, args.pilot007_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
