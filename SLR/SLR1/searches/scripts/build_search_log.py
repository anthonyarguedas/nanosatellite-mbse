#!/usr/bin/env python3
"""Render the integrated search log from validated new-run artifacts."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RUN_ID = "eps-mbse-slr-2026"


def md(value: Any) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def source_worklog(source: str) -> str:
    return {
        "Scopus": "searches/worklogs/scopus.md",
        "IEEE Xplore": "searches/worklogs/ieee-xplore.md",
        "Semantic Scholar": "searches/worklogs/semantic-scholar.md",
        "Google Scholar": "searches/worklogs/google-scholar.md",
        "Coverage-gap audit": "searches/worklogs/coverage-gap.md",
    }[source]


def count_display(artifact: dict[str, Any]) -> str:
    result_count = artifact["bibliographic_records_in_file"]
    array_count = artifact["results_array_length"]
    if result_count != array_count:
        return f"{result_count} bibliographic ({array_count} serialized)"
    return str(result_count)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dedup", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--screening", type=Path, required=True)
    parser.add_argument("--recall-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    dedup = json.loads(args.dedup.read_text(encoding="utf-8"))
    freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
    screening = json.loads(args.screening.read_text(encoding="utf-8"))
    recall = json.loads(args.recall_audit.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    final_inputs = manifest["final_merge_inputs"]
    artifacts = manifest["artifacts"]
    summary = dedup["summary"]
    stage = dedup["stage_counts"]
    screen_counts = screening["counts"]
    recall_summary = recall["summary"]
    dedup_inputs = {item["query_id"]: item for item in dedup.get("input_inventory", [])}

    lines = [
        "# Search Log",
        "",
        f"Topic: Model-Based Systems Engineering for nanosatellite electrical power systems (EPS)",
        f"Review run: `{RUN_ID}`",
        "Review dir: `SLR/SLR1`",
        f"Integrated corpus-search log generated: {now}",
        "",
        "## Protocol reuse",
        "- Reused `protocol.md` v1.0 (approved/frozen 2026-08-06) and `query-search-plan.md`; scope and eligibility rules were not redefined.",
        "- The protocol-controlled two-stream design was retained: Stream A required population × EPS × MBSE/system-model concepts; Stream B deliberately omitted an EPS term to recover embedded threads.",
        "- The approval record is integrated in `protocol.md`; no separate approval file was used.",
        "- Anti-anchoring sequence: only final accepted new-run source artifacts were copied to `searches/merge-inputs/`, merged, deterministically deduplicated, and frozen before any retained Markdown/PDF cache inspection.",
        "",
        "## Search strategy notes",
        "- Primary databases: Scopus and IEEE Xplore. Supplementary sources: Semantic Scholar and Google Scholar targeted discovery only, not exhaustive searches.",
        "- Common evidence window: 2013–2026 inclusive; no open-access filter. Scopus used English + `ar/cp/ch`; IEEE used English + Journals/Conferences/Books. Source-specific pagination/limits are preserved in `searches/search-manifest.json` and raw artifacts.",
        "- Stream A concepts: CubeSat/nanosatellite population × EPS names/functions/budgets/components × MBSE/structured-system-model terms. Stream B concepts: population × MBSE/language or structured-model + systems-engineering relation terms, without mandatory EPS.",
        "- Outcome and V&V terms were sensitivity probes only, never baseline gates. The coverage-gap audit tested model-driven/model-centric wording, OOSEM/OPM, digital thread/twin, executable/model integration, EPS control/interface terms, and source-observed conceptual/integrated-concurrent wording.",
        "- Scopus metadata supplied blank abstracts/authors across its runs. Those gaps were preserved and treated as missing metadata during title/abstract screening, not as negative evidence.",
        "",
        "## Final accepted candidate-input query set",
        "",
        "| ID | Database | Stream | Raw artifact | Source total | Bibliographic records retrieved | Why retained |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for artifact in final_inputs:
        lines.append(
            f"| {artifact['query_id']} | {artifact['source']} | {artifact['stream']} | `{artifact['artifact_path'].replace('SLR/SLR1/', '')}` | {md(artifact['source_reported_total'])} | {artifact['bibliographic_records_in_file']} | {md(artifact['assessment'])} |"
        )
    lines += [
        "",
        "### Exact final queries and filters",
        "",
        "Scopus final inputs used `TITLE-ABS-KEY` query syntax with `LANGUAGE(english)`, `(DOCTYPE(ar) OR DOCTYPE(cp) OR DOCTYPE(ch))`, and script years 2013–2026 (the script appended `PUBYEAR AFT 2012 AND PUBYEAR BEF 2027`). IEEE final inputs used the displayed parenthesized Boolean query with years 2013–2026, English, and Journals/Conferences/Books; every full run used limit/page-size/max-pages 100/100/1. Coverage-gap Scopus used limit/max-pages 100/4 and coverage-gap IEEE used 100/100/1.",
        "",
    ]
    for artifact in final_inputs:
        query = artifact.get("exact_query") or ""
        input_record = dedup_inputs.get(artifact["query_id"], {})
        applied_filters = input_record.get("filters") or {}
        saved_metadata = artifact.get("filters_or_request_metadata") or {}
        source_timestamp = input_record.get("search_extracted_at") or saved_metadata.get("extracted_at")
        effective_query = query
        if artifact["source"] == "Scopus":
            effective_query = f"{query} AND PUBYEAR AFT 2012 AND PUBYEAR BEF 2027"
        lines += [
            f"<details><summary>{artifact['query_id']} — {artifact['source']} / Stream {artifact['stream']} — `{artifact['artifact_path'].replace('SLR/SLR1/', '')}`</summary>",
            "",
            "Exact query submitted to the source script:",
            "",
            "```text",
            query,
            "```",
            "",
            "Effective source query after script-applied year clauses:" if artifact["source"] == "Scopus" else "Effective source query:",
            "",
            "```text",
            effective_query,
            "```",
            "",
            f"Applied filters/retrieval settings: `{json.dumps(applied_filters, ensure_ascii=False, sort_keys=True)}`",
            "",
            f"Saved source timestamp: `{source_timestamp or 'not supplied'}`",
            "",
            f"Raw output metadata: `{json.dumps(saved_metadata, ensure_ascii=False, sort_keys=True)}`",
            "",
            "</details>",
            "",
        ]

    lines += [
        "## Query log: all new-run artifacts",
        "",
        "The complete per-artifact exact query and request metadata are machine-readable in `searches/search-manifest.json`; the corresponding raw JSON/error file remains the source of record. `—` means no source total was supplied—not zero hits. `success_count_only` deliberately retrieves zero candidate records while obtaining an IEEE total.",
        "",
        "| ID | Database | Stream | Artifact | Kind / status | Source total | Bibliographic records | Retained? | Assessment / worklog |",
        "|---|---|---|---|---|---:|---:|---|---|",
    ]
    for artifact in artifacts:
        worklog = (artifact.get("worklog") or source_worklog(artifact["source"])).replace("SLR/SLR1/", "")
        lines.append(
            f"| {artifact['query_id']} | {artifact['source']} | {md(artifact['stream'])} | `{artifact['artifact_path'].replace('SLR/SLR1/', '')}` | {artifact['artifact_kind']} / {artifact['status']} | {md(artifact['source_reported_total'])} | {count_display(artifact)} | {'yes' if artifact['retained_for_merge'] else 'no'} | {md(artifact['assessment'])} ([worklog]({worklog})) |"
        )

    lines += [
        "",
        "## Refinements, failures, and source handling",
        "",
        "- **Scopus:** Three initial path-validation preflights (S-A1/S-A2/S-B1) failed locally before any API request; they are not zero-result searches. Portable validation was applied and all actual Scopus requests completed. S-B1r1 replaced S-B1 after the wildcard added five records; S-B3 and S-B4 retained alternative structured/relations coverage. Stream-A wildcard checks and outcome/V&V/small-satellite probes were duplicate-only or not target-population additions.",
        "- **IEEE Xplore:** Planned A1/A2/B1/B2 full runs and retained A4/A5 refinement full runs were complete; all final totals fit one 100-record page. Count-only runs are audit artifacts, not candidate input. I-B4 and selected coverage probes are true endpoint-reported zeros, distinct from failures. Refinements A3/A6/B3 and V&V/outcome full probes were duplicate-only/noisy and not merged.",
        "- **Semantic Scholar:** all 9 varied probes failed with HTTP 403 before page 1. Its script serialized empty fallback JSON; post-integration QA annotated each artifact explicitly as `service_failure_http_403` with `source_total_reported: false`. The source total is recorded as `—`, not zero, and no Semantic Scholar record was merged.",
        "- **Google Scholar:** all 6 targeted fallback/recovery queries failed before rank 1/UI total (`Cannot Fetch from Google Scholar`). They are `service_failure_before_rank_1`, not zero hits. No Google Scholar record was merged.",
        "- **Coverage gap:** M1 and IEEE refinements were duplicate-only; M2 was OPM acronym noise; initial M4 co-simulation/executable wording was too imprecise and superseded. Retained M3/M3R1/M4R1/M5/M6 coverage files preserved the EPS-free Stream-B recall route. Direct EPS digital-twin and EPS control/interface sensitivities did not add an independent candidate input.",
        "",
        "## Coverage audit",
        "",
        "| Lineage / concept cluster | Representative expected/new-run signal | Found in independently merged candidates? | Found in screened retrieval corpus? | Recall risk / interpretation |",
        "|---|---|---|---|---|",
        "| EPS-primary structured models and electrical architecture | `Open-source CubeSat MBSE ... Power Subsystem`; `CONCURRENT ENGINEERING PROCESS FOR ELECTRICAL ARCHITECTURE ...` | Yes | Yes (core) | Strong direct metadata coverage; full text still tests structured EPS relations. |",
        "| Parametric power/energy budgets bound to models | `Applying Model-Based Systems Engineering on CubeSat Budget Calculating`; MBSE CubeSat mission simulation | Yes | Yes (core) | Direct power/energy terms are sparse and source abstracts can be truncated/missing. |",
        "| Whole-spacecraft SysML/MBSE with potential embedded EPS | CubeSat behavior, RAX, risk, EIRSAT-1 system-model records | Yes | Yes (supporting) | EPS anchor/bridge often absent from metadata, by design of Stream B. |",
        "| Reference/template/reuse lineage | CubeSat System Reference Model interim/application/development/mission-engineering series | Yes | Yes (supporting) | Multiple reports may be lineage-related; full text must identify distinct EPS threads and avoid double counting. |",
        "| Digital engineering, interoperability, transformations | Docs-as-code, semantic-web/data-formalization, information-exchange records | Yes | Yes (supporting) | Digital-engineering labels alone do not establish EPS linkage. |",
        "| Requirements traceability and model-derived V&V | Power-subsystem traceability and MBSE-compliant CubeSat reference-model V&V | Yes | Yes (core/supporting) | Direct EPS target–bridge–V&V evidence remains a full-text question. |",
        "| Digital thread/twin and executable/concurrent modeling | Retained M3/M3R1/M4R1/M5/M6 inputs | Yes (39 candidates with any coverage-gap provenance; 31 coverage-only) | Mixed; conservative supporting plus clear rejects | Broad digital-twin results are noisy; retained to avoid metadata-driven loss of embedded threads. |",
        "| Proceedings/chapters and weak indexing | IEEE AERO/SysCon and Scopus chapter/proceedings records | Yes | Yes | Supplementary source failures leave residual conference/chapter recall risk. |",
        "| Post-freeze retained-cache diagnostic only | Cache-only EPS/electrical-power filenames/metadata (architecture, storage, converters) | No new candidate added | No | Potential terminology/indexing diagnostic only; metadata cannot establish MBSE and some signals are excluded CanSat/PocketQube/standalone work. Logged in `searches/retained-file-recall-audit.json`; no silent query expansion. |",
        "",
        "## Merge and deduplication",
        "",
        f"- Isolated inputs: {summary['input_files']} final accepted artifacts (9 Scopus and 8 IEEE Xplore; 11 primary-source + 6 retained coverage-gap files).",
        f"- Raw bibliographic occurrences: {summary['raw_bibliographic_occurrences']} (Scopus {summary['raw_occurrences_by_source']['Scopus']}; IEEE Xplore {summary['raw_occurrences_by_source']['IEEE Xplore']}; primary {summary['raw_occurrences_by_search_phase']['primary']}; coverage gap {summary['raw_occurrences_by_search_phase']['coverage_gap']}).",
        f"- Stock merger invocation completed on `searches/merge-inputs/`: 352 raw → 174 unique. Its IEEE source inference labeled 110 raw events `unknown`; deterministic correction restored the source inventory without changing the 174 identity count.",
        f"- Deterministic pass: DOI stage 352 → {stage['after_normalized_doi']}; same-source paperId stage → {stage['after_same_source_paper_id']}; manually confirmed title+year and title-only fallback each added 0 merges. Final: {summary['unique_candidates']} unique; {summary['duplicates_removed']} duplicate occurrences removed.",
        "- Provenance preserves source, query ID, exact query, original raw artifact, isolated copy, stream, phase, rank, and raw source record. Metadata conflicts and preference rules are in `searches/merged_candidates.json` and `searches/deduplication-report.json`.",
        f"- Independent freeze: `searches/independent-candidate-freeze.json`, candidate SHA-256 `{freeze['candidate_set']['sha256']}`. No legacy candidate/ID/cache item entered the merged set.",
        "",
        "## Stream and source unique yield",
        "",
        "| Measure | Count |",
        "|---|---:|",
        f"| Stream A raw occurrences | {summary['raw_occurrences_by_stream']['A']} |",
        f"| Stream B raw occurrences | {summary['raw_occurrences_by_stream']['B']} |",
        f"| Unique candidates with Stream A provenance | {summary['unique_yield']['unique_candidates_with_stream']['A']} |",
        f"| Unique candidates with Stream B provenance | {summary['unique_yield']['unique_candidates_with_stream']['B']} |",
        f"| Stream-A-only unique candidates | {summary['unique_yield']['unique_candidates_by_stream_pattern']['A']} |",
        f"| Stream-B-only unique candidates | {summary['unique_yield']['unique_candidates_by_stream_pattern']['B']} |",
        f"| Found by both A and B | {summary['unique_yield']['unique_candidates_by_stream_pattern']['A + B']} |",
        f"| Scopus-only unique candidates | {summary['unique_yield']['unique_candidates_by_source_pattern']['Scopus']} |",
        f"| IEEE-Xplore-only unique candidates | {summary['unique_yield']['unique_candidates_by_source_pattern']['IEEE Xplore']} |",
        f"| Found in both primary sources | {summary['unique_yield']['unique_candidates_by_source_pattern']['IEEE Xplore + Scopus']} |",
        "",
        "## Title/abstract screening handoff",
        "",
        f"- Every independently merged candidate received one decision: {screen_counts['core']} core, {screen_counts['supporting']} supporting, {screen_counts['rejected']} rejected; {screen_counts['secondary_studies']} secondary/background records are separately retained for future citation chasing.",
        f"- `corpus.json` has {screen_counts['kept']} retrieval candidates only, all `pending_full_text_eligibility`. Route A/Route B, EPS anchors/bridges, final publication type/language, and V&V/outcome evidence are explicitly deferred.",
        "",
        "## Deferred retained-cache recall check",
        "",
        f"- Performed only after the independent freeze and screening. Metadata-only inspection saw {recall_summary['cache_files_seen']} retained cache files; {recall_summary['matched_cache_files']} cache files matched {recall_summary['unique_independently_rediscovered_reports_matched']} independently rediscovered reports ({recall_summary['unique_matches_by_independent_screening_tier'].get('core', 0)} core; {recall_summary['unique_matches_by_independent_screening_tier'].get('supporting', 0)} supporting).",
        f"- {recall_summary['unmatched_or_ambiguous_cache_files']} cache files were unmatched/ambiguous and remain cache-only. See `legacy-known-item-register.md` and `searches/retained-file-recall-audit.json`; these did not contribute records, IDs, screening decisions, or evidence.",
        "",
        "## Stopping rationale",
        "",
        "- Both primary databases completed final accepted Stream-A and deliberately EPS-free Stream-B inputs. All records available within documented source limits were saved/read by specialists, and the retained final input set was isolated and fully merged.",
        "- Planned sensitivity/refinement work covered the prespecified model, EPS, V&V, outcome, population, digital-thread/twin, executable/integration, and proceedings/chapter clusters. Recent refinements were predominantly duplicate-only, zero, or clearly noisy; coverage-gap additions were bounded and screened.",
        "- Supplementary failures are documented as unresolved access limitations, not negative evidence. They remain a recall risk, as do opaque IEEE matching, sparse Scopus metadata, and cache-only terminology signals.",
        "- This closes the corpus-search/title-abstract stage, not the review's full search lifecycle. Protocol-required backward/forward citation chasing starts only from full-text-included reports and relevant secondary reviews; it is explicitly deferred and must not be reported as complete here.",
        "- If the review's final search date extends beyond 2026-08-06, run an update search before final evidence closure.",
        "",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "success", "final_queries": len(final_inputs), "query_artifacts": len(artifacts), "unique_candidates": summary["unique_candidates"]}, indent=2))


if __name__ == "__main__":
    main()
