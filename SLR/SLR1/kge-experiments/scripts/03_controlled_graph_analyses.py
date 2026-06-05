#!/usr/bin/env python3
"""Run controlled-code graph analyses E1-E6 for SLR1.

The analyses are intentionally dependency-light: flattened JSONL inputs, Python
standard library, and NetworkX for portable GraphML exports.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations, product
from typing import Any, Iterable

import networkx as nx

from kg_common import (
    DATA_DIR,
    FIGURES_DIR,
    GRAPH_EXPORTS_DIR,
    REPORTS_DIR,
    TABLES_DIR,
    clean_text,
    dedupe_study_codes,
    ensure_dirs,
    ensure_issue001_outputs,
    evidence_confidence_rank,
    is_none_like,
    join_values,
    json_dumps,
    load_jsonl,
    markdown_table,
    node_id,
    quote_by_claim,
    sorted_unique_text,
    unique_preserve,
    values,
    write_csv,
    write_graphml,
    write_text,
)


EPS_FIELD = "eps_verification_specific.eps_elements_modeled"
EPS_RELEVANCE_FIELD = "study_context_population.eps_relevance"
VERIFICATION_MECHANISM_FIELD = "eps_verification_specific.pre_physical_development_verification_mechanism"
IVV_FIELD = "eps_verification_specific.ivv_integration_level"
VERIFICATION_ARTIFACT_FIELD = "eps_verification_specific.verification_validation_artifacts"
TOOL_FIELD = "toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool"
INTEROP_FIELD = "toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms"
TOOL_LIMITATION_FIELD = "toolchain_interoperability_lifecycle_continuity.toolchain_limitations"
REUSE_FIELD = "mbse_objective_scope_artifacts.generality_reuse_mechanism"
MODEL_ARTIFACT_FIELD = "mbse_objective_scope_artifacts.model_artifacts_used"
MODEL_MATURITY_FIELD = "study_context_population.model_maturity"
REPRODUCIBILITY_FIELD = "quality_checklist.reproducibility_toolchain_reported"
LIFECYCLE_FIELD = "study_context_population.lifecycle_stage_addressed"

WEAK_OR_UNSUPPORTED = {"Unsupported", "Weak"}
MODERATE_OR_STRONG = {"Moderate", "Strong"}


def load_inputs() -> dict[str, Any]:
    ensure_issue001_outputs()
    ensure_dirs(TABLES_DIR, REPORTS_DIR, GRAPH_EXPORTS_DIR, FIGURES_DIR)
    study_codes = dedupe_study_codes(load_jsonl(DATA_DIR / "study_codes.jsonl"))
    evidence_quotes = load_jsonl(DATA_DIR / "evidence_quotes.jsonl")
    return {
        "studies": load_jsonl(DATA_DIR / "studies.jsonl"),
        "study_codes": study_codes,
        "claims": load_jsonl(DATA_DIR / "claims.jsonl"),
        "limitations": load_jsonl(DATA_DIR / "limitations.jsonl"),
        "emergent_codes": load_jsonl(DATA_DIR / "emergent_codes.jsonl"),
        "gap_mappings": load_jsonl(DATA_DIR / "gap_mappings.jsonl"),
        "evidence_quotes": evidence_quotes,
        "claim_quotes": quote_by_claim(evidence_quotes),
    }


def build_field_index(study_codes: Iterable[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for record in study_codes:
        value = clean_text(record.get("value"))
        if value is None:
            continue
        bucket = out[str(record["study_id"])][str(record["field_path"])]
        if value.lower() not in {item.lower() for item in bucket}:
            bucket.append(value)
    return {study_id: dict(fields) for study_id, fields in out.items()}


def get_field_values(field_index: dict[str, dict[str, list[str]]], study_id: str, field_path: str) -> list[str]:
    return list(field_index.get(study_id, {}).get(field_path, []))


def meaningful(items: Iterable[Any]) -> list[str]:
    return [item for item in sorted_unique_text(items) if not is_none_like(item)]


def normalized_values(items: Iterable[Any], default: str = "not reported") -> list[str]:
    vals = sorted_unique_text(items)
    return vals or [default]


def meaningful_or_default(items: Iterable[Any], default: str = "none/not reported") -> list[str]:
    vals = meaningful(items)
    return vals or [default]


def first_n_join(items: Iterable[Any], n: int = 12) -> str:
    vals = sorted_unique_text(items)
    if len(vals) <= n:
        return "; ".join(vals)
    return "; ".join(vals[:n]) + f"; ... (+{len(vals) - n} more)"


def counter_summary(counter: Counter[str], n: int = 5) -> str:
    if not counter:
        return ""
    return "; ".join(f"{label} ({count})" for label, count in counter.most_common(n))


def claim_field_values(claim: dict[str, Any], field: str, default: str = "not reported") -> list[str]:
    vals = values(claim.get(field))
    return vals or [default]


def study_title_map(studies: Iterable[dict[str, Any]]) -> dict[str, str]:
    return {str(study["study_id"]): clean_text(study.get("title")) or str(study["study_id"]) for study in studies}


def claims_by_study(claims: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        out[str(claim["study_id"])].append(claim)
    return dict(out)


def limitation_flags_by_study(limitations: Iterable[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for limitation in limitations:
        flag = clean_text(limitation.get("flag"))
        if flag:
            out[str(limitation["study_id"])].add(flag)
    return dict(out)


def gap_records_by_study(gap_mappings: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for gap_mapping in gap_mappings:
        out[str(gap_mapping["study_id"])].append(gap_mapping)
    return dict(out)


def add_node_once(graph: nx.Graph, node: str, node_type: str, label: str, **attrs: Any) -> None:
    if node not in graph:
        graph.add_node(node, type=node_type, label=label, **attrs)
    else:
        graph.nodes[node].update({key: value for key, value in attrs.items() if value not in (None, "")})


def sorted_rows_from_groups(
    groups: dict[tuple[Any, ...], dict[str, Any]],
    columns_from_key: list[str],
    count_name: str = "study_count",
    include_claim_count: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, data in groups.items():
        row = dict(zip(columns_from_key, key))
        studies = data.get("studies", set())
        claims = data.get("claims", set())
        row[count_name] = len(studies)
        if include_claim_count:
            row["claim_count"] = len(claims)
        row["studies"] = "; ".join(sorted(studies))
        if include_claim_count:
            row["claim_ids"] = "; ".join(sorted(claims))
        rows.append(row)
    return sorted(rows, key=lambda row: (-int(row.get(count_name, 0)), *(str(row[col]).lower() for col in columns_from_key)))


def run_e1_claim_evidence(
    studies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    claim_quotes: dict[str, str],
) -> dict[str, Any]:
    titles = study_title_map(studies)
    graph = nx.MultiDiGraph()
    edge_index = 0

    counts: dict[tuple[str, str, str], dict[str, set[str]]] = defaultdict(lambda: {"claims": set(), "studies": set()})
    flow_counts: Counter[tuple[str, str, str]] = Counter()
    unsupported_rows: list[dict[str, Any]] = []
    confidence_counts: Counter[str] = Counter()
    weak_by_outcome: Counter[str] = Counter()
    moderate_strong_by_mechanism: Counter[str] = Counter()
    weak_claims_by_study: Counter[str] = Counter()

    for study in studies:
        add_node_once(graph, str(study["study_id"]), "Study", titles[str(study["study_id"])], year=study.get("year"))

    for claim in claims:
        claim_id = str(claim["claim_id"])
        study_id = str(claim["study_id"])
        claim_text = clean_text(claim.get("claim_text")) or claim_id
        confidence = clean_text(claim.get("evidence_confidence")) or "not reported"
        quote = claim_quotes.get(claim_id, "")
        confidence_counts[confidence] += 1
        add_node_once(
            graph,
            claim_id,
            "Claim",
            claim_text,
            study_id=study_id,
            evidence_confidence=confidence,
            claim_text=claim_text,
        )
        edge_index += 1
        graph.add_edge(
            study_id,
            claim_id,
            key=f"e{edge_index:06d}",
            type="HAS_CLAIM",
            source_field_path=claim.get("field_path") or "claimed_outcomes_value_mechanisms_evidence[]",
            evidence_quote=quote,
            confidence=claim.get("confidence") or "",
        )

        outcomes = claim_field_values(claim, "outcome_category")
        evidence_types = claim_field_values(claim, "evidence_type")
        mechanisms = claim_field_values(claim, "mbse_mechanism")
        for outcome, evidence_type in product(outcomes, evidence_types):
            counts[(outcome, evidence_type, confidence)]["claims"].add(claim_id)
            counts[(outcome, evidence_type, confidence)]["studies"].add(study_id)
            flow_counts[("outcome_to_evidence_type", outcome, evidence_type)] += 1
            flow_counts[("evidence_type_to_confidence", evidence_type, confidence)] += 1
        if confidence in WEAK_OR_UNSUPPORTED:
            weak_claims_by_study[study_id] += 1
            for outcome in outcomes:
                weak_by_outcome[outcome] += 1
        if confidence in MODERATE_OR_STRONG:
            for mechanism in mechanisms:
                moderate_strong_by_mechanism[mechanism] += 1

        for node_type_value, edge_type, claim_key in [
            ("OutcomeCategory", "CLAIMS_OUTCOME", "outcome_category"),
            ("EvidenceType", "HAS_EVIDENCE_TYPE", "evidence_type"),
            ("EvidenceConfidence", "HAS_EVIDENCE_CONFIDENCE", "evidence_confidence"),
            ("MBSEMechanism", "USES_MBSE_MECHANISM", "mbse_mechanism"),
        ]:
            for value in claim_field_values(claim, claim_key):
                target = node_id(node_type_value, value)
                add_node_once(graph, target, node_type_value, value)
                edge_index += 1
                graph.add_edge(
                    claim_id,
                    target,
                    key=f"e{edge_index:06d}",
                    type=edge_type,
                    source_value=value,
                    evidence_quote=quote,
                    confidence=claim.get("confidence") or "",
                )

        if confidence in WEAK_OR_UNSUPPORTED:
            unsupported_rows.append(
                {
                    "rank": 0,
                    "claim_id": claim_id,
                    "study_id": study_id,
                    "study_title": titles.get(study_id, study_id),
                    "evidence_confidence": confidence,
                    "outcome_categories": join_values(outcomes),
                    "evidence_types": join_values(evidence_types),
                    "mbse_mechanisms": join_values(mechanisms),
                    "baseline": clean_text(claim.get("baseline")) or "",
                    "specificity": clean_text(claim.get("specificity")) or "",
                    "claim_text": claim_text,
                    "evidence_quote": quote,
                }
            )

    unsupported_rows.sort(
        key=lambda row: (evidence_confidence_rank(row["evidence_confidence"]), row["study_id"], row["claim_id"])
    )
    for idx, row in enumerate(unsupported_rows, start=1):
        row["rank"] = idx

    count_rows = []
    for (outcome, evidence_type, confidence), data in counts.items():
        count_rows.append(
            {
                "outcome_category": outcome,
                "evidence_type": evidence_type,
                "evidence_confidence": confidence,
                "claim_count": len(data["claims"]),
                "study_count": len(data["studies"]),
                "claims": "; ".join(sorted(data["claims"])),
                "studies": "; ".join(sorted(data["studies"])),
            }
        )
    count_rows.sort(
        key=lambda row: (
            row["outcome_category"].lower(),
            evidence_confidence_rank(row["evidence_confidence"]),
            row["evidence_type"].lower(),
        )
    )

    flow_rows = [
        {"stage": stage, "source": source, "target": target, "claim_count": count}
        for (stage, source, target), count in sorted(flow_counts.items(), key=lambda item: (item[0][0], item[0][1].lower(), item[0][2].lower()))
    ]

    write_graphml(graph, GRAPH_EXPORTS_DIR / "claim_evidence_graph.graphml")
    write_csv(
        TABLES_DIR / "unsupported_claims.csv",
        unsupported_rows,
        [
            "rank",
            "claim_id",
            "study_id",
            "study_title",
            "evidence_confidence",
            "outcome_categories",
            "evidence_types",
            "mbse_mechanisms",
            "baseline",
            "specificity",
            "claim_text",
            "evidence_quote",
        ],
    )
    write_csv(
        TABLES_DIR / "claim_outcome_evidence_counts.csv",
        count_rows,
        [
            "outcome_category",
            "evidence_type",
            "evidence_confidence",
            "claim_count",
            "study_count",
            "claims",
            "studies",
        ],
    )
    write_csv(FIGURES_DIR / "e1_claim_evidence_alluvial.csv", flow_rows, ["stage", "source", "target", "claim_count"])

    weak_outcome_rows = [
        {"outcome_category": outcome, "weak_or_unsupported_claims": count}
        for outcome, count in weak_by_outcome.most_common(10)
    ]
    strong_mechanism_rows = [
        {"mbse_mechanism": mechanism, "moderate_or_strong_claims": count}
        for mechanism, count in moderate_strong_by_mechanism.most_common(10)
    ]
    weak_study_rows = [
        {"study_id": study_id, "weak_or_unsupported_claims": count, "study_title": titles.get(study_id, study_id)}
        for study_id, count in weak_claims_by_study.most_common(10)
    ]
    report = f"""# E1 — Claim-evidence graph

Total claims: **{len(claims)}**. Evidence-confidence distribution: {counter_summary(confidence_counts, 10)}.
Weak or unsupported claims in `unsupported_claims.csv`: **{len(unsupported_rows)}**.

## Outcomes most often linked to weak/unsupported claims

{markdown_table(weak_outcome_rows, ["outcome_category", "weak_or_unsupported_claims"], max_rows=10)}

## MBSE mechanisms with moderate/strong claim evidence

{markdown_table(strong_mechanism_rows, ["mbse_mechanism", "moderate_or_strong_claims"], max_rows=10)}

## Studies with many weak/unsupported claims

{markdown_table(weak_study_rows, ["study_id", "weak_or_unsupported_claims", "study_title"], max_rows=10)}

Graph export: `outputs/graph_exports/claim_evidence_graph.graphml`. A deterministic Sankey/alluvial substitute is available at `outputs/figures/e1_claim_evidence_alluvial.csv`.
"""
    write_text(REPORTS_DIR / "e1_claim_evidence.md", report)
    return {
        "claim_count": len(claims),
        "weak_or_unsupported_claim_count": len(unsupported_rows),
        "claim_evidence_count_rows": len(count_rows),
    }


def run_e2_eps_verification(
    studies: list[dict[str, Any]],
    field_index: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    path_groups: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"studies": set(), "eps_relevance": Counter()}
    )
    element_summary: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "studies": set(),
            "no_verification": set(),
            "no_ivv": set(),
            "mechanisms": Counter(),
            "ivv_levels": Counter(),
            "eps_relevance": Counter(),
        }
    )
    element_mechanism: dict[tuple[str, str], set[str]] = defaultdict(set)
    mechanism_ivv: dict[tuple[str, str], set[str]] = defaultdict(set)

    for study in studies:
        study_id = str(study["study_id"])
        eps_elements = meaningful(get_field_values(field_index, study_id, EPS_FIELD))
        if not eps_elements:
            continue
        mechanisms_raw = get_field_values(field_index, study_id, VERIFICATION_MECHANISM_FIELD)
        ivv_raw = get_field_values(field_index, study_id, IVV_FIELD)
        mechanisms = meaningful_or_default(mechanisms_raw)
        ivv_levels = meaningful_or_default(ivv_raw)
        eps_relevance_values = meaningful_or_default(get_field_values(field_index, study_id, EPS_RELEVANCE_FIELD), "not reported")
        has_verification = bool(meaningful(mechanisms_raw))
        has_ivv = bool(meaningful(ivv_raw))
        for element in eps_elements:
            summary = element_summary[element]
            summary["studies"].add(study_id)
            if not has_verification:
                summary["no_verification"].add(study_id)
            if not has_ivv:
                summary["no_ivv"].add(study_id)
            for mechanism in mechanisms:
                summary["mechanisms"][mechanism] += 1
                element_mechanism[(element, mechanism)].add(study_id)
            for ivv in ivv_levels:
                summary["ivv_levels"][ivv] += 1
            for eps_relevance in eps_relevance_values:
                summary["eps_relevance"][eps_relevance] += 1
            for element_value, mechanism, ivv in product([element], mechanisms, ivv_levels):
                path_groups[(element_value, mechanism, ivv)]["studies"].add(study_id)
                for eps_relevance in eps_relevance_values:
                    path_groups[(element_value, mechanism, ivv)]["eps_relevance"][eps_relevance] += 1
                mechanism_ivv[(mechanism, ivv)].add(study_id)

    path_rows = []
    for (element, mechanism, ivv), data in path_groups.items():
        path_rows.append(
            {
                "eps_element": element,
                "verification_mechanism": mechanism,
                "ivv_integration_level": ivv,
                "study_count": len(data["studies"]),
                "studies": "; ".join(sorted(data["studies"])),
                "eps_relevance_values": counter_summary(data["eps_relevance"], 6),
            }
        )
    path_rows.sort(key=lambda row: (-row["study_count"], row["eps_element"].lower(), row["verification_mechanism"].lower()))

    graph = nx.DiGraph()
    for element in element_summary:
        add_node_once(graph, node_id("EPSElement", element), "EPSElement", element, study_count=len(element_summary[element]["studies"]))
    for (element, mechanism), study_ids in element_mechanism.items():
        add_node_once(graph, node_id("VerificationMechanism", mechanism), "VerificationMechanism", mechanism)
        graph.add_edge(
            node_id("EPSElement", element),
            node_id("VerificationMechanism", mechanism),
            type="EPS_ELEMENT_TO_VERIFICATION_MECHANISM",
            weight=len(study_ids),
            study_count=len(study_ids),
            studies="; ".join(sorted(study_ids)),
        )
    for (mechanism, ivv), study_ids in mechanism_ivv.items():
        add_node_once(graph, node_id("VerificationMechanism", mechanism), "VerificationMechanism", mechanism)
        add_node_once(graph, node_id("IVVIntegrationLevel", ivv), "IVVIntegrationLevel", ivv)
        graph.add_edge(
            node_id("VerificationMechanism", mechanism),
            node_id("IVVIntegrationLevel", ivv),
            type="VERIFICATION_MECHANISM_TO_IVV_LEVEL",
            weight=len(study_ids),
            study_count=len(study_ids),
            studies="; ".join(sorted(study_ids)),
        )

    gap_rows = []
    for element, data in element_summary.items():
        total = len(data["studies"])
        gap_rows.append(
            {
                "eps_element": element,
                "study_count": total,
                "no_verification_count": len(data["no_verification"]),
                "no_ivv_count": len(data["no_ivv"]),
                "top_verification_mechanisms": counter_summary(data["mechanisms"], 5),
                "top_ivv_levels": counter_summary(data["ivv_levels"], 5),
                "eps_relevance_values": counter_summary(data["eps_relevance"], 5),
                "studies": "; ".join(sorted(data["studies"])),
            }
        )
    gap_rows.sort(key=lambda row: (-row["study_count"], -row["no_verification_count"], row["eps_element"].lower()))

    write_csv(
        TABLES_DIR / "eps_verification_paths.csv",
        path_rows,
        ["eps_element", "verification_mechanism", "ivv_integration_level", "study_count", "studies", "eps_relevance_values"],
    )
    write_graphml(graph, GRAPH_EXPORTS_DIR / "eps_verification_paths.graphml")

    report = f"""# E2 — EPS verification pathway map

EPS-modeled element count: **{len(element_summary)}**. Path rows: **{len(path_rows)}**.

## Common EPS verification paths

{markdown_table(path_rows, ["eps_element", "verification_mechanism", "ivv_integration_level", "study_count"], max_rows=15)}

## EPS elements with verification/IV&V gaps

{markdown_table(gap_rows, ["eps_element", "study_count", "no_verification_count", "no_ivv_count", "top_verification_mechanisms", "top_ivv_levels"], max_rows=15)}

Interpretation note: `none/not reported` is retained when no controlled verification mechanism or IV&V level was coded for a study.
"""
    write_text(REPORTS_DIR / "eps_gap_map.md", report)
    return {"eps_path_rows": len(path_rows), "eps_elements": len(element_summary)}


def run_e3_toolchain(
    studies: list[dict[str, Any]],
    field_index: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    tool_studies: dict[str, set[str]] = defaultdict(set)
    cooccurrence: dict[tuple[str, str], set[str]] = defaultdict(set)
    tool_limit_groups: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"studies": set()})
    tool_interop_groups: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"studies": set()})
    limitation_counts = Counter()
    interop_counts = Counter()

    for study in studies:
        study_id = str(study["study_id"])
        tools = meaningful(get_field_values(field_index, study_id, TOOL_FIELD))
        if not tools:
            continue
        for tool in tools:
            tool_studies[tool].add(study_id)
        for left, right in combinations(tools, 2):
            pair = tuple(sorted((left, right), key=lambda value: value.lower()))
            cooccurrence[pair].add(study_id)
        limitations = meaningful_or_default(get_field_values(field_index, study_id, TOOL_LIMITATION_FIELD))
        mechanisms = meaningful_or_default(get_field_values(field_index, study_id, INTEROP_FIELD))
        for tool, limitation in product(tools, limitations):
            tool_limit_groups[(tool, limitation)]["studies"].add(study_id)
            limitation_counts[limitation] += 1
        for tool, mechanism in product(tools, mechanisms):
            tool_interop_groups[(tool, mechanism)]["studies"].add(study_id)
            interop_counts[mechanism] += 1

    graph = nx.Graph()
    for tool, study_ids in tool_studies.items():
        add_node_once(graph, node_id("Tool", tool), "Tool", tool, study_count=len(study_ids), studies="; ".join(sorted(study_ids)))
    for (left, right), study_ids in cooccurrence.items():
        graph.add_edge(
            node_id("Tool", left),
            node_id("Tool", right),
            type="TOOL_COOCCURS_WITH_TOOL",
            weight=len(study_ids),
            study_count=len(study_ids),
            studies="; ".join(sorted(study_ids)),
        )

    heatmap_rows = sorted_rows_from_groups(tool_limit_groups, ["tool", "toolchain_limitation"])
    interop_rows = sorted_rows_from_groups(tool_interop_groups, ["tool", "interoperability_mechanism"])
    cooccurrence_rows = [
        {"tool_a": left, "tool_b": right, "study_count": len(study_ids), "studies": "; ".join(sorted(study_ids))}
        for (left, right), study_ids in cooccurrence.items()
    ]
    cooccurrence_rows.sort(key=lambda row: (-row["study_count"], row["tool_a"].lower(), row["tool_b"].lower()))

    write_graphml(graph, GRAPH_EXPORTS_DIR / "tool_cooccurrence.graphml")
    write_csv(
        TABLES_DIR / "toolchain_limitations_heatmap.csv",
        heatmap_rows,
        ["tool", "toolchain_limitation", "study_count", "studies"],
    )
    write_csv(
        TABLES_DIR / "tool_interoperability_counts.csv",
        interop_rows,
        ["tool", "interoperability_mechanism", "study_count", "studies"],
    )

    report = f"""# E3 — Toolchain interoperability network

Tool nodes: **{len(tool_studies)}**. Tool co-occurrence edges: **{len(cooccurrence)}**.

## Most common tool co-occurrences

{markdown_table(cooccurrence_rows, ["tool_a", "tool_b", "study_count"], max_rows=15)}

## Tool × interoperability mechanisms

{markdown_table(interop_rows, ["tool", "interoperability_mechanism", "study_count"], max_rows=15)}

## Toolchain limitation overlay

{markdown_table(heatmap_rows, ["tool", "toolchain_limitation", "study_count"], max_rows=15)}

Dominant interoperability mechanisms overall: {counter_summary(interop_counts, 8)}.
Dominant toolchain limitations overall: {counter_summary(limitation_counts, 8)}.
"""
    write_text(REPORTS_DIR / "e3_toolchain_interoperability.md", report)
    return {"tool_nodes": len(tool_studies), "tool_cooccurrence_edges": len(cooccurrence)}


def is_reuse_claim(claim: dict[str, Any]) -> bool:
    outcomes = {value.lower() for value in values(claim.get("outcome_category"))}
    metrics = {value.lower() for value in values(claim.get("metric"))}
    mechanisms = {value.lower() for value in values(claim.get("mbse_mechanism"))}
    return (
        "generality/reuse" in outcomes
        or "model reuse" in metrics
        or "reference model reuse" in mechanisms
        or "reproducibility" in outcomes
    )


def run_e4_reuse(
    studies: list[dict[str, Any]],
    claims_by_study_id: dict[str, list[dict[str, Any]]],
    field_index: dict[str, dict[str, list[str]]],
    limitation_index: dict[str, set[str]],
) -> dict[str, Any]:
    reuse_groups: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(
        lambda: {"studies": set(), "claims": set(), "artifacts": set(), "availability_statuses": Counter(), "model_not_available": set()}
    )
    candidate_rows: list[dict[str, Any]] = []
    titles = study_title_map(studies)

    for study in studies:
        study_id = str(study["study_id"])
        reuse_mechanisms = meaningful_or_default(get_field_values(field_index, study_id, REUSE_FIELD))
        artifacts = meaningful(get_field_values(field_index, study_id, MODEL_ARTIFACT_FIELD))
        maturity = meaningful_or_default(get_field_values(field_index, study_id, MODEL_MATURITY_FIELD), "not reported")
        repro_values = {value.lower() for value in get_field_values(field_index, study_id, REPRODUCIBILITY_FIELD)}
        unavailable = "model_not_available" in limitation_index.get(study_id, set())
        if unavailable:
            availability = "model_not_available flag present"
        elif "yes" in repro_values:
            availability = "reproducibility/toolchain reported"
        else:
            availability = "not flagged unavailable"
        reuse_claims = [claim for claim in claims_by_study_id.get(study_id, []) if is_reuse_claim(claim)]
        if reuse_claims:
            for claim in reuse_claims:
                claim_id = str(claim["claim_id"])
                evidence_types = claim_field_values(claim, "evidence_type")
                confidence = clean_text(claim.get("evidence_confidence")) or "not reported"
                for mechanism, evidence_type in product(reuse_mechanisms, evidence_types):
                    group = reuse_groups[(mechanism, evidence_type, confidence)]
                    group["studies"].add(study_id)
                    group["claims"].add(claim_id)
                    group["artifacts"].update(artifacts)
                    group["availability_statuses"][availability] += 1
                    if unavailable:
                        group["model_not_available"].add(study_id)
        else:
            for mechanism in reuse_mechanisms:
                group = reuse_groups[(mechanism, "no reuse-specific claim", "not reported")]
                group["studies"].add(study_id)
                group["artifacts"].update(artifacts)
                group["availability_statuses"][availability] += 1
                if unavailable:
                    group["model_not_available"].add(study_id)

        best_confidence = max((evidence_confidence_rank(claim.get("evidence_confidence")) for claim in reuse_claims), default=-1)
        evidence_types_all = [etype for claim in reuse_claims for etype in claim_field_values(claim, "evidence_type")]
        has_replication = any("reuse/replication" in etype.lower() for etype in evidence_types_all)
        has_moderate_or_strong = any((clean_text(claim.get("evidence_confidence")) or "") in MODERATE_OR_STRONG for claim in reuse_claims)
        score = 0
        score += len([mechanism for mechanism in reuse_mechanisms if not is_none_like(mechanism)])
        score += max(best_confidence, 0)
        score += 3 if has_replication else 0
        score += 2 if has_moderate_or_strong else 0
        score += 1 if artifacts else 0
        score += 1 if "yes" in repro_values else 0
        score -= 2 if unavailable else 0
        if reuse_claims or meaningful(reuse_mechanisms):
            candidate_rows.append(
                {
                    "rank": 0,
                    "study_id": study_id,
                    "score": score,
                    "study_title": titles.get(study_id, study_id),
                    "reuse_mechanisms": join_values(reuse_mechanisms),
                    "model_artifacts": first_n_join(artifacts, 8),
                    "model_maturity": join_values(maturity),
                    "availability_status": availability,
                    "best_evidence_rank": best_confidence,
                    "evidence_types": first_n_join(evidence_types_all, 8),
                    "reuse_claim_ids": "; ".join(sorted(str(claim["claim_id"]) for claim in reuse_claims)),
                }
            )

    map_rows = []
    for (mechanism, evidence_type, confidence), data in reuse_groups.items():
        map_rows.append(
            {
                "reuse_mechanism": mechanism,
                "evidence_type": evidence_type,
                "evidence_confidence": confidence,
                "study_count": len(data["studies"]),
                "claim_count": len(data["claims"]),
                "model_not_available_study_count": len(data["model_not_available"]),
                "availability_statuses": counter_summary(data["availability_statuses"], 5),
                "model_artifacts": first_n_join(data["artifacts"], 12),
                "studies": "; ".join(sorted(data["studies"])),
                "claim_ids": "; ".join(sorted(data["claims"])),
            }
        )
    map_rows.sort(
        key=lambda row: (
            -row["study_count"],
            -row["claim_count"],
            row["reuse_mechanism"].lower(),
            evidence_confidence_rank(row["evidence_confidence"]),
        )
    )

    candidate_rows.sort(key=lambda row: (-row["score"], row["study_id"]))
    for idx, row in enumerate(candidate_rows, start=1):
        row["rank"] = idx

    write_csv(
        TABLES_DIR / "reuse_evidence_map.csv",
        map_rows,
        [
            "reuse_mechanism",
            "evidence_type",
            "evidence_confidence",
            "study_count",
            "claim_count",
            "model_not_available_study_count",
            "availability_statuses",
            "model_artifacts",
            "studies",
            "claim_ids",
        ],
    )

    report = f"""# E4 — Reuse/generality evidence map

Reuse evidence map rows: **{len(map_rows)}**. Candidate studies scored with simple controlled-code evidence features: reuse mechanism breadth, evidence confidence, reuse/replication evidence, artifact reporting, reproducibility reporting, and a penalty for `model_not_available`.

## Top reusable artifact candidates

{markdown_table(candidate_rows, ["rank", "study_id", "score", "reuse_mechanisms", "availability_status", "best_evidence_rank", "evidence_types"], max_rows=20)}

## Common reuse mechanism × evidence combinations

{markdown_table(map_rows, ["reuse_mechanism", "evidence_type", "evidence_confidence", "study_count", "claim_count", "model_not_available_study_count"], max_rows=20)}

Caveat: this is a controlled-code candidate ranking, not proof that artifacts are currently accessible or reusable.
"""
    write_text(REPORTS_DIR / "reusable_artifact_candidates.md", report)
    return {"reuse_map_rows": len(map_rows), "reuse_candidate_count": len(candidate_rows)}


def run_e5_limitation_gap(
    limitations: list[dict[str, Any]],
    gap_mappings: list[dict[str, Any]],
    limitation_index: dict[str, set[str]],
    gap_index: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    heatmap_groups: dict[tuple[str, str, str], dict[str, Any]] = defaultdict(lambda: {"studies": set()})
    edge_groups: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"studies": set(), "levels": Counter()})
    limitation_studies: dict[str, set[str]] = defaultdict(set)
    gap_studies: dict[str, set[str]] = defaultdict(set)

    for limitation in limitations:
        flag = clean_text(limitation.get("flag"))
        if flag:
            limitation_studies[flag].add(str(limitation["study_id"]))
    for gap_mapping in gap_mappings:
        gap = clean_text(gap_mapping.get("gap"))
        if gap:
            gap_studies[gap].add(str(gap_mapping["study_id"]))

    all_study_ids = sorted(set(limitation_index) | set(gap_index))
    for study_id in all_study_ids:
        flags = sorted(limitation_index.get(study_id, set()), key=str.lower)
        for gap_mapping in gap_index.get(study_id, []):
            gap = clean_text(gap_mapping.get("gap"))
            level = clean_text(gap_mapping.get("level")) or "not reported"
            if not gap:
                continue
            for flag in flags:
                heatmap_groups[(gap, level, flag)]["studies"].add(study_id)
                edge_groups[(flag, gap)]["studies"].add(study_id)
                edge_groups[(flag, gap)]["levels"][level] += 1

    heatmap_rows = sorted_rows_from_groups(heatmap_groups, ["gap", "gap_addressing_level", "limitation_flag"])

    graph = nx.Graph()
    for flag, study_ids in limitation_studies.items():
        add_node_once(graph, node_id("LimitationFlag", flag), "LimitationFlag", flag, study_count=len(study_ids), studies="; ".join(sorted(study_ids)))
    for gap, study_ids in gap_studies.items():
        add_node_once(graph, node_id("Gap", gap), "Gap", gap, study_count=len(study_ids), studies="; ".join(sorted(study_ids)))
    for (flag, gap), data in edge_groups.items():
        graph.add_edge(
            node_id("LimitationFlag", flag),
            node_id("Gap", gap),
            type="LIMITATION_CO_OCCURS_WITH_GAP",
            weight=len(data["studies"]),
            study_count=len(data["studies"]),
            studies="; ".join(sorted(data["studies"])),
            gap_addressing_levels=json_dumps(dict(sorted(data["levels"].items()))),
        )

    centrality = nx.degree_centrality(graph) if graph.number_of_nodes() else {}
    bottleneck_rows = []
    for node, attrs in graph.nodes(data=True):
        weighted_degree = sum(int(edge_data.get("weight", 1)) for _, _, edge_data in graph.edges(node, data=True))
        related = sorted(
            [
                (
                    graph.nodes[neighbor].get("label", neighbor),
                    int((graph.get_edge_data(node, neighbor) or {}).get("weight", 1)),
                )
                for neighbor in graph.neighbors(node)
            ],
            key=lambda item: (-item[1], item[0].lower()),
        )
        bottleneck_rows.append(
            {
                "rank": 0,
                "node_id": node,
                "type": attrs.get("type", ""),
                "label": attrs.get("label", node),
                "study_count": attrs.get("study_count", 0),
                "degree_centrality": f"{centrality.get(node, 0.0):.6f}",
                "weighted_degree": weighted_degree,
                "top_related": "; ".join(f"{label} ({weight})" for label, weight in related[:8]),
            }
        )
    bottleneck_rows.sort(
        key=lambda row: (-int(row["weighted_degree"]), -int(row["study_count"]), row["type"], row["label"].lower())
    )
    for idx, row in enumerate(bottleneck_rows, start=1):
        row["rank"] = idx

    write_graphml(graph, GRAPH_EXPORTS_DIR / "limitation_gap_graph.graphml")
    write_csv(
        TABLES_DIR / "bottlenecks_ranked.csv",
        bottleneck_rows,
        ["rank", "node_id", "type", "label", "study_count", "degree_centrality", "weighted_degree", "top_related"],
    )
    write_csv(
        TABLES_DIR / "gap_limitation_heatmap.csv",
        heatmap_rows,
        ["gap", "gap_addressing_level", "limitation_flag", "study_count", "studies"],
    )

    report = f"""# E5 — Limitation/gap co-occurrence bottlenecks

Limitation/gap graph nodes: **{graph.number_of_nodes()}**. Edges: **{graph.number_of_edges()}**.

## Central bottlenecks

{markdown_table(bottleneck_rows, ["rank", "type", "label", "study_count", "weighted_degree", "top_related"], max_rows=20)}

## Frequent gap × limitation combinations

{markdown_table(heatmap_rows, ["gap", "gap_addressing_level", "limitation_flag", "study_count"], max_rows=20)}

Centrality is computed over the controlled-code co-occurrence graph and should be interpreted as exploratory synthesis, not statistical causality.
"""
    write_text(REPORTS_DIR / "e5_limitation_gap_bottlenecks.md", report)
    return {"limitation_gap_nodes": graph.number_of_nodes(), "limitation_gap_edges": graph.number_of_edges()}


def run_e6_lifecycle(
    studies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    field_index: dict[str, dict[str, list[str]]],
) -> dict[str, Any]:
    stage_studies: dict[str, set[str]] = defaultdict(set)
    stage_claims: dict[str, list[dict[str, Any]]] = defaultdict(list)
    stage_artifact_edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    stage_confidence_edges: dict[tuple[str, str], set[str]] = defaultdict(set)
    artifact_confidence_edges: dict[tuple[str, str], set[str]] = defaultdict(set)

    for study in studies:
        study_id = str(study["study_id"])
        stages = meaningful_or_default(get_field_values(field_index, study_id, LIFECYCLE_FIELD), "not reported")
        artifacts = meaningful_or_default(get_field_values(field_index, study_id, VERIFICATION_ARTIFACT_FIELD))
        for stage, artifact in product(stages, artifacts):
            stage_studies[stage].add(study_id)
            stage_artifact_edges[(stage, artifact)].add(study_id)

    for claim in claims:
        claim_id = str(claim["claim_id"])
        study_id = str(claim["study_id"])
        stages = claim_field_values(claim, "lifecycle_stage")
        confidence = clean_text(claim.get("evidence_confidence")) or "not reported"
        artifacts = meaningful_or_default(get_field_values(field_index, study_id, VERIFICATION_ARTIFACT_FIELD))
        for stage in stages:
            stage_claims[stage].append(claim)
            stage_studies[stage].add(study_id)
            stage_confidence_edges[(stage, confidence)].add(claim_id)
            for artifact in artifacts:
                stage_artifact_edges[(stage, artifact)].add(study_id)
                artifact_confidence_edges[(artifact, confidence)].add(claim_id)

    coverage_rows = []
    for stage in sorted(stage_studies, key=str.lower):
        claims_for_stage = stage_claims.get(stage, [])
        confidence_counts = Counter(clean_text(claim.get("evidence_confidence")) or "not reported" for claim in claims_for_stage)
        artifact_values = set()
        for study_id in stage_studies[stage]:
            artifact_values.update(meaningful(get_field_values(field_index, study_id, VERIFICATION_ARTIFACT_FIELD)))
        outcome_counts = Counter(
            outcome
            for claim in claims_for_stage
            for outcome in claim_field_values(claim, "outcome_category")
        )
        coverage_rows.append(
            {
                "lifecycle_stage": stage,
                "study_count": len(stage_studies[stage]),
                "claim_count": len(claims_for_stage),
                "strong_claims": confidence_counts.get("Strong", 0),
                "moderate_claims": confidence_counts.get("Moderate", 0),
                "weak_claims": confidence_counts.get("Weak", 0),
                "unsupported_claims": confidence_counts.get("Unsupported", 0),
                "verification_artifact_count": len(artifact_values),
                "verification_artifacts": first_n_join(artifact_values, 12),
                "top_outcomes": counter_summary(outcome_counts, 8),
                "studies": "; ".join(sorted(stage_studies[stage])),
            }
        )
    coverage_rows.sort(key=lambda row: (-row["study_count"], -row["claim_count"], row["lifecycle_stage"].lower()))

    graph = nx.DiGraph()
    for stage in stage_studies:
        add_node_once(graph, node_id("LifecycleStage", stage), "LifecycleStage", stage, study_count=len(stage_studies[stage]))
    for (stage, artifact), study_ids in stage_artifact_edges.items():
        add_node_once(graph, node_id("VerificationArtifact", artifact), "VerificationArtifact", artifact)
        graph.add_edge(
            node_id("LifecycleStage", stage),
            node_id("VerificationArtifact", artifact),
            type="LIFECYCLE_STAGE_TO_VERIFICATION_ARTIFACT",
            weight=len(study_ids),
            study_count=len(study_ids),
            studies="; ".join(sorted(study_ids)),
        )
    for (stage, confidence), claim_ids in stage_confidence_edges.items():
        add_node_once(graph, node_id("EvidenceConfidence", confidence), "EvidenceConfidence", confidence)
        graph.add_edge(
            node_id("LifecycleStage", stage),
            node_id("EvidenceConfidence", confidence),
            type="LIFECYCLE_STAGE_TO_EVIDENCE_CONFIDENCE",
            weight=len(claim_ids),
            claim_count=len(claim_ids),
            claim_ids="; ".join(sorted(claim_ids)),
        )
    for (artifact, confidence), claim_ids in artifact_confidence_edges.items():
        add_node_once(graph, node_id("VerificationArtifact", artifact), "VerificationArtifact", artifact)
        add_node_once(graph, node_id("EvidenceConfidence", confidence), "EvidenceConfidence", confidence)
        existing = graph.get_edge_data(node_id("VerificationArtifact", artifact), node_id("EvidenceConfidence", confidence))
        if existing:
            # DiGraph cannot store parallel edge types. Merge counts only if this exact edge already exists.
            existing["weight"] = int(existing.get("weight", 0)) + len(claim_ids)
            existing["claim_count"] = int(existing.get("claim_count", 0)) + len(claim_ids)
            existing["claim_ids"] = first_n_join((existing.get("claim_ids", "").split("; ") + sorted(claim_ids)), 40)
        else:
            graph.add_edge(
                node_id("VerificationArtifact", artifact),
                node_id("EvidenceConfidence", confidence),
                type="VERIFICATION_ARTIFACT_TO_EVIDENCE_CONFIDENCE",
                weight=len(claim_ids),
                claim_count=len(claim_ids),
                claim_ids="; ".join(sorted(claim_ids)),
            )

    write_csv(
        TABLES_DIR / "lifecycle_coverage.csv",
        coverage_rows,
        [
            "lifecycle_stage",
            "study_count",
            "claim_count",
            "strong_claims",
            "moderate_claims",
            "weak_claims",
            "unsupported_claims",
            "verification_artifact_count",
            "verification_artifacts",
            "top_outcomes",
            "studies",
        ],
    )
    write_graphml(graph, GRAPH_EXPORTS_DIR / "lifecycle_artifact_evidence.graphml")

    report = f"""# E6 — Lifecycle coverage graph

Lifecycle stages represented: **{len(coverage_rows)}**. Graph nodes: **{graph.number_of_nodes()}**; edges: **{graph.number_of_edges()}**.

## Lifecycle coverage by stage

{markdown_table(coverage_rows, ["lifecycle_stage", "study_count", "claim_count", "strong_claims", "moderate_claims", "weak_claims", "unsupported_claims", "verification_artifact_count"], max_rows=20)}

## Artifact/evidence interpretation

Later lifecycle stages (e.g., PDR, CDR, integration and test, operations) should be read against both claim counts and verification-artifact coverage. Counts are controlled-code co-occurrences; they do not imply that every artifact directly verifies every claim in the same study.
"""
    write_text(REPORTS_DIR / "lifecycle_artifact_evidence.md", report)
    return {"lifecycle_rows": len(coverage_rows), "lifecycle_graph_edges": graph.number_of_edges()}


def main() -> None:
    data = load_inputs()
    studies = data["studies"]
    claims = data["claims"]
    field_index = build_field_index(data["study_codes"])
    claims_index = claims_by_study(claims)
    limitations_index = limitation_flags_by_study(data["limitations"])
    gaps_index = gap_records_by_study(data["gap_mappings"])

    summary = {}
    summary.update(run_e1_claim_evidence(studies, claims, data["claim_quotes"]))
    summary.update(run_e2_eps_verification(studies, field_index))
    summary.update(run_e3_toolchain(studies, field_index))
    summary.update(run_e4_reuse(studies, claims_index, field_index, limitations_index))
    summary.update(run_e5_limitation_gap(data["limitations"], data["gap_mappings"], limitations_index, gaps_index))
    summary.update(run_e6_lifecycle(studies, claims, field_index))

    print("Controlled-code analyses complete:")
    for key in sorted(summary):
        print(f"  {key}: {summary[key]}")


if __name__ == "__main__":
    main()
