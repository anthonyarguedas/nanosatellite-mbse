#!/usr/bin/env python3
"""Build the SLR1 controlled-code property graph MVP.

The graph is built only from ISSUE-001 flattened JSONL outputs. If those
outputs are missing, the flattening script is invoked rather than reimplementing
extraction flattening.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

from kg_common import (
    BASE_DIR,
    DATA_DIR,
    KG_DIR,
    clean_text,
    dedupe_study_codes,
    ensure_dirs,
    ensure_issue001_outputs,
    json_dumps,
    load_jsonl,
    node_id,
    quote_by_claim,
    sha256_file,
    slugify,
    sorted_unique_text,
    unique_preserve,
    values,
    write_csv,
    write_graphml,
    write_json,
    write_text,
)


CONSTRUCTION_VERSION = "issue-002-kg-mvp-v1"

NODE_COLUMNS = ["id", "label", "type", "properties_json"]
EDGE_COLUMNS = [
    "source",
    "target",
    "type",
    "source_field_path",
    "source_value",
    "rationale",
    "evidence_quote",
    "confidence",
    "properties_json",
]

STUDY_FIELD_EDGE_MAP = {
    "implementation_pathway_tailoring.approach_classification": ("ApproachClass", "HAS_APPROACH_CLASS"),
    "study_context_population.eps_relevance": ("EPSRelevance", "HAS_EPS_RELEVANCE"),
    "study_context_population.lifecycle_stage_addressed": ("LifecycleStage", "ADDRESSES_LIFECYCLE_STAGE"),
    "study_context_population.development_context": ("DevelopmentContext", "HAS_DEVELOPMENT_CONTEXT"),
    "study_context_population.model_maturity": ("ModelMaturity", "HAS_MODEL_MATURITY"),
    "mbse_objective_scope_artifacts.modeling_scope": ("ModelingScope", "HAS_MODELING_SCOPE"),
    "mbse_objective_scope_artifacts.model_artifacts_used": ("ModelArtifact", "USES_MODEL_ARTIFACT"),
    "mbse_objective_scope_artifacts.generality_reuse_mechanism": ("ReuseMechanism", "HAS_REUSE_MECHANISM"),
    "implementation_pathway_tailoring.tailoring_rationale": ("TailoringRationale", "HAS_TAILORING_RATIONALE"),
    "toolchain_interoperability_lifecycle_continuity.mbse_language_method_tool": ("Tool", "USES_TOOL"),
    "toolchain_interoperability_lifecycle_continuity.interoperability_mechanisms": (
        "InteroperabilityMechanism",
        "HAS_INTEROPERABILITY_MECHANISM",
    ),
    "toolchain_interoperability_lifecycle_continuity.toolchain_limitations": (
        "ToolchainLimitation",
        "HAS_TOOLCHAIN_LIMITATION",
    ),
    "eps_verification_specific.eps_elements_modeled": ("EPSElement", "MODELS_EPS_ELEMENT"),
    "eps_verification_specific.verification_validation_artifacts": (
        "VerificationArtifact",
        "USES_VERIFICATION_ARTIFACT",
    ),
    "eps_verification_specific.pre_physical_development_verification_mechanism": (
        "VerificationMechanism",
        "USES_VERIFICATION_MECHANISM",
    ),
    "eps_verification_specific.ivv_integration_level": ("IVVIntegrationLevel", "HAS_IVV_LEVEL"),
}

CLAIM_FIELD_EDGE_MAP = {
    "outcome_category": ("OutcomeCategory", "CLAIMS_OUTCOME", "outcome_category"),
    "specificity": ("SpecificityOfClaim", "HAS_SPECIFICITY", "specificity_of_claim"),
    "mbse_mechanism": ("MBSEMechanism", "USES_MBSE_MECHANISM", "mbse_mechanism"),
    "lifecycle_stage": ("LifecycleStage", "CLAIM_AT_LIFECYCLE_STAGE", "lifecycle_stage"),
    "evidence_type": ("EvidenceType", "HAS_EVIDENCE_TYPE", "evidence_type"),
    "metric": ("MetricIndicator", "HAS_METRIC", "metric_or_value_indicator"),
    "baseline": ("BaselineComparator", "HAS_BASELINE", "baseline_comparator"),
    "evidence_confidence": ("EvidenceConfidence", "HAS_EVIDENCE_CONFIDENCE", "evidence_confidence_rating"),
    "reliability_subtype": ("ReliabilitySubtype", "HAS_RELIABILITY_SUBTYPE", "reliability_subtype"),
}

STUDY_PROPERTY_FIELDS = {
    "rq1_relevance": "bibliographic_review_management.rq1_relevance",
    "rq2_relevance": "bibliographic_review_management.rq2_relevance",
    "rq3_relevance": "bibliographic_review_management.rq3_relevance",
    "eps_relevance": "study_context_population.eps_relevance",
    "approach_classification": "implementation_pathway_tailoring.approach_classification",
}


class PropertyGraphBuilder:
    """Small in-memory property graph builder for CSV/GraphML exports."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self._edge_signatures: set[tuple[str, str, str, str, str, str]] = set()

    def add_node(self, node_id_value: str, node_type: str, label: Any, properties: dict[str, Any] | None = None) -> str:
        label_text = clean_text(label) or node_id_value
        if node_id_value not in self.nodes:
            self.nodes[node_id_value] = {
                "id": node_id_value,
                "label": label_text,
                "type": node_type,
                "properties": {},
            }
        node = self.nodes[node_id_value]
        if clean_text(node.get("label")) in {None, node_id_value} and label_text != node_id_value:
            node["label"] = label_text
        if properties:
            merge_properties(node["properties"], properties)
        return node_id_value

    def add_controlled_node(
        self,
        node_type_value: str,
        label: Any,
        source_field_path: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> str:
        label_text = clean_text(label) or "not reported"
        controlled_id = node_id(node_type_value, label_text)
        props: dict[str, Any] = {"normalized_slug": slugify(label_text)}
        if source_field_path:
            props["source_field_paths"] = [source_field_path]
        if properties:
            props.update(properties)
        return self.add_node(controlled_id, node_type_value, label_text, props)

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str,
        source_field_path: Any = None,
        source_value: Any = None,
        rationale: Any = None,
        evidence_quote: Any = None,
        confidence: Any = None,
        properties: dict[str, Any] | None = None,
    ) -> None:
        if source not in self.nodes or target not in self.nodes:
            raise KeyError(f"Cannot add edge with missing endpoint: {source!r} -> {target!r}")
        source_field_path_text = clean_text(source_field_path) or ""
        source_value_text = clean_text(source_value) or ""
        props = properties or {}
        record_key = clean_text(props.get("source_record_id")) or clean_text(props.get("source_record_ids")) or ""
        signature = (source, target, edge_type, source_field_path_text, source_value_text, record_key)
        if signature in self._edge_signatures:
            return
        self._edge_signatures.add(signature)
        self.edges.append(
            {
                "source": source,
                "target": target,
                "type": edge_type,
                "source_field_path": source_field_path_text,
                "source_value": source_value_text,
                "rationale": clean_text(rationale) or "",
                "evidence_quote": clean_text(evidence_quote) or "",
                "confidence": clean_text(confidence) or "",
                "properties": props,
            }
        )

    def node_rows(self) -> list[dict[str, Any]]:
        rows = []
        for node in sorted(self.nodes.values(), key=lambda row: (row["type"], row["id"])):
            rows.append(
                {
                    "id": node["id"],
                    "label": node["label"],
                    "type": node["type"],
                    "properties_json": json_dumps(finalize_properties(node.get("properties", {}))),
                }
            )
        return rows

    def edge_rows(self) -> list[dict[str, Any]]:
        rows = []
        for edge in sorted(
            self.edges,
            key=lambda row: (
                row["type"],
                row["source"],
                row["target"],
                row["source_field_path"],
                row["source_value"],
            ),
        ):
            out = {key: edge[key] for key in EDGE_COLUMNS if key != "properties_json"}
            out["properties_json"] = json_dumps(finalize_properties(edge.get("properties", {})))
            rows.append(out)
        return rows


def merge_properties(target: dict[str, Any], new_values: dict[str, Any]) -> None:
    """Merge node properties while keeping repeated provenance as unique lists."""
    for key, value in new_values.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (list, tuple, set)):
            incoming = [item for item in value if clean_text(item) is not None]
            if not incoming:
                continue
            existing = target.get(key)
            if existing is None:
                target[key] = unique_preserve(incoming)
            else:
                existing_list = existing if isinstance(existing, list) else [existing]
                target[key] = unique_preserve([*existing_list, *incoming])
            continue
        if key not in target or target[key] in (None, "", []):
            target[key] = value
        elif target[key] != value:
            alt_key = f"{key}_values"
            existing_list = target.get(alt_key, [target[key]])
            if not isinstance(existing_list, list):
                existing_list = [existing_list]
            target[alt_key] = unique_preserve([*existing_list, value])


def finalize_properties(properties: dict[str, Any]) -> dict[str, Any]:
    """Sort repeated scalar provenance fields for deterministic JSON."""
    out: dict[str, Any] = {}
    for key, value in properties.items():
        if isinstance(value, list):
            # Preserve long textual lists (e.g., descriptions) but sort ID/path-like lists.
            if key.endswith("ids") or key.endswith("paths") or key.endswith("sections") or key.endswith("confidences"):
                out[key] = sorted_unique_text(value)
            else:
                out[key] = unique_preserve(value)
        else:
            out[key] = value
    return out


def first_values_by_study(study_codes: Iterable[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for record in study_codes:
        value = clean_text(record.get("value"))
        if value is None:
            continue
        values_for_field = out[str(record.get("study_id"))][str(record.get("field_path"))]
        if value.lower() not in {item.lower() for item in values_for_field}:
            values_for_field.append(value)
    return {study_id: dict(fields) for study_id, fields in out.items()}


def join_study_property(values_for_study: dict[str, list[str]], field_path: str) -> str | None:
    vals = values_for_study.get(field_path, [])
    if not vals:
        return None
    return "; ".join(vals)


def add_study_nodes(
    builder: PropertyGraphBuilder,
    studies: list[dict[str, Any]],
    values_by_study_field: dict[str, dict[str, list[str]]],
) -> None:
    for study in studies:
        study_id = str(study["study_id"])
        code_values = values_by_study_field.get(study_id, {})
        properties = {
            "source_path": study.get("source_path"),
            "year": study.get("year"),
            "tier": study.get("tier"),
            "title": study.get("title"),
            "authors": study.get("authors"),
            "venue": study.get("venue"),
            "doi": study.get("doi"),
            "quality_score_total": study.get("quality_score_total"),
            "extraction_confidence": study.get("extraction_confidence"),
            "source_generated_at": study.get("source_generated_at"),
            "source_codebook_version": study.get("source_codebook_version"),
        }
        for prop_name, field_path in STUDY_PROPERTY_FIELDS.items():
            properties[prop_name] = join_study_property(code_values, field_path)
        builder.add_node(study_id, "Study", study.get("title") or study_id, properties)


def add_study_code_edges(builder: PropertyGraphBuilder, study_codes: list[dict[str, Any]]) -> None:
    for record in study_codes:
        field_path = clean_text(record.get("field_path"))
        if field_path not in STUDY_FIELD_EDGE_MAP:
            continue
        value = clean_text(record.get("value"))
        if value is None:
            continue
        node_type_value, edge_type = STUDY_FIELD_EDGE_MAP[field_path]
        target_id = builder.add_controlled_node(node_type_value, value, field_path)
        properties = {
            "study_id": record.get("study_id"),
            "value_index": record.get("value_index"),
            "source_path": record.get("source_path"),
            "source_paths": record.get("source_paths"),
            "source_sections": record.get("source_sections"),
            "status": record.get("status"),
            "statuses": record.get("statuses"),
            "confidences": record.get("confidences"),
            "source_record_id": record.get("study_code_id"),
            "source_record_ids": record.get("study_code_ids"),
        }
        builder.add_edge(
            str(record["study_id"]),
            target_id,
            edge_type,
            source_field_path=field_path,
            source_value=value,
            rationale=record.get("rationale"),
            evidence_quote=record.get("evidence_quote"),
            confidence=record.get("confidence"),
            properties=properties,
        )


def add_claim_nodes_and_edges(
    builder: PropertyGraphBuilder,
    claims: list[dict[str, Any]],
    claim_quote_map: dict[str, str],
) -> None:
    for claim in claims:
        claim_id = str(claim["claim_id"])
        study_id = str(claim["study_id"])
        quote = claim_quote_map.get(claim_id)
        claim_properties = {
            "study_id": study_id,
            "source_claim_id": claim.get("source_claim_id"),
            "source_path": claim.get("source_path"),
            "field_path": claim.get("field_path"),
            "claim_text": claim.get("claim_text"),
            "metric_detail": claim.get("metric_detail"),
            "observed_effect_or_qualitative_effect": claim.get("observed_effect"),
            "artifact_or_process_linked": claim.get("linked_artifact_or_process"),
            "quote_location": claim.get("quote_location"),
            "evidence_source": quote,
            "threats_or_alternative_explanations": claim.get("threats_alternative_explanations"),
            "extractor_confidence": claim.get("confidence"),
            "source_generated_at": claim.get("source_generated_at"),
            "source_codebook_version": claim.get("source_codebook_version"),
        }
        builder.add_node(claim_id, "Claim", claim.get("claim_text") or claim_id, claim_properties)
        builder.add_edge(
            study_id,
            claim_id,
            "HAS_CLAIM",
            source_field_path=claim.get("field_path") or "claimed_outcomes_value_mechanisms_evidence[]",
            source_value=claim.get("claim_text"),
            evidence_quote=quote,
            confidence=claim.get("confidence"),
            properties={
                "study_id": study_id,
                "claim_id": claim_id,
                "source_record_id": claim_id,
                "source_path": claim.get("source_path"),
                "source_claim_id": claim.get("source_claim_id"),
            },
        )
        for claim_key, (node_type_value, edge_type, source_suffix) in CLAIM_FIELD_EDGE_MAP.items():
            for value in values(claim.get(claim_key)):
                target_id = builder.add_controlled_node(
                    node_type_value,
                    value,
                    f"claimed_outcomes_value_mechanisms_evidence[].{source_suffix}",
                )
                builder.add_edge(
                    claim_id,
                    target_id,
                    edge_type,
                    source_field_path=f"claimed_outcomes_value_mechanisms_evidence[].{source_suffix}",
                    source_value=value,
                    evidence_quote=quote,
                    confidence=claim.get("confidence"),
                    properties={
                        "study_id": study_id,
                        "claim_id": claim_id,
                        "source_record_id": claim_id,
                        "source_path": claim.get("source_path"),
                        "source_claim_id": claim.get("source_claim_id"),
                        "claim_text": claim.get("claim_text"),
                        "observed_effect": claim.get("observed_effect"),
                        "evidence_confidence": claim.get("evidence_confidence"),
                    },
                )


def add_limitation_edges(builder: PropertyGraphBuilder, limitations: list[dict[str, Any]]) -> None:
    for limitation in limitations:
        flag = clean_text(limitation.get("flag"))
        if flag is None:
            continue
        target_id = builder.add_controlled_node(
            "LimitationFlag",
            flag,
            limitation.get("field_path") or "structured_limitations.limitation_assessments[]",
            properties={"assessment_values": [limitation.get("assessment")], "sources": [limitation.get("source")]},
        )
        builder.add_edge(
            str(limitation["study_id"]),
            target_id,
            "HAS_LIMITATION",
            source_field_path=limitation.get("field_path"),
            source_value=flag,
            rationale=limitation.get("rationale"),
            evidence_quote=limitation.get("evidence_quote"),
            confidence=limitation.get("confidence"),
            properties={
                "study_id": limitation.get("study_id"),
                "source_record_id": limitation.get("limitation_id"),
                "source_path": limitation.get("source_path"),
                "limitation_type": limitation.get("limitation_type"),
                "source": limitation.get("source"),
                "assessment": limitation.get("assessment"),
            },
        )


def add_gap_edges(builder: PropertyGraphBuilder, gap_mappings: list[dict[str, Any]]) -> None:
    for gap_mapping in gap_mappings:
        gap = clean_text(gap_mapping.get("gap"))
        level = clean_text(gap_mapping.get("level"))
        if gap is None:
            continue
        gap_id = builder.add_controlled_node("Gap", gap, gap_mapping.get("field_path"), properties={"levels": [level]})
        builder.add_edge(
            str(gap_mapping["study_id"]),
            gap_id,
            "ADDRESSES_GAP",
            source_field_path=gap_mapping.get("field_path"),
            source_value=gap,
            rationale=gap_mapping.get("rationale"),
            evidence_quote=gap_mapping.get("evidence_quote"),
            confidence=gap_mapping.get("confidence"),
            properties={
                "study_id": gap_mapping.get("study_id"),
                "source_record_id": gap_mapping.get("gap_mapping_id"),
                "source_path": gap_mapping.get("source_path"),
                "gap_addressing_level": level,
            },
        )
        if level:
            level_id = builder.add_controlled_node(
                "GapAddressingLevel",
                level,
                gap_mapping.get("field_path"),
                properties={"gaps": [gap]},
            )
            builder.add_edge(
                str(gap_mapping["study_id"]),
                level_id,
                "HAS_GAP_ADDRESSING_LEVEL",
                source_field_path=gap_mapping.get("field_path"),
                source_value=level,
                rationale=gap_mapping.get("rationale"),
                evidence_quote=gap_mapping.get("evidence_quote"),
                confidence=gap_mapping.get("confidence"),
                properties={
                    "study_id": gap_mapping.get("study_id"),
                    "source_record_id": gap_mapping.get("gap_mapping_id"),
                    "source_path": gap_mapping.get("source_path"),
                    "gap": gap,
                },
            )


def add_emergent_code_edges(builder: PropertyGraphBuilder, emergent_codes: list[dict[str, Any]]) -> None:
    for emergent in emergent_codes:
        label = clean_text(emergent.get("label"))
        if label is None:
            continue
        target_id = builder.add_controlled_node(
            "EmergentCode",
            label,
            emergent.get("field_path"),
            properties={
                "study_ids": [emergent.get("study_id")],
                "descriptions": [emergent.get("description")],
                "original_labels": [emergent.get("original_label")],
                "categories": [emergent.get("category")],
                "confidences": [emergent.get("confidence")],
            },
        )
        builder.add_edge(
            str(emergent["study_id"]),
            target_id,
            "HAS_EMERGENT_CODE",
            source_field_path=emergent.get("field_path"),
            source_value=label,
            rationale=emergent.get("rationale"),
            evidence_quote=emergent.get("evidence_quote"),
            confidence=emergent.get("confidence"),
            properties={
                "study_id": emergent.get("study_id"),
                "source_record_id": emergent.get("emergent_code_id"),
                "source_path": emergent.get("source_path"),
                "description": emergent.get("description"),
                "original_label": emergent.get("original_label"),
                "category": emergent.get("category"),
            },
        )


def build_networkx_graph(node_rows: list[dict[str, Any]], edge_rows: list[dict[str, Any]]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.graph["construction_version"] = CONSTRUCTION_VERSION
    graph.graph["description"] = "SLR1 controlled-code property graph MVP"
    for node in node_rows:
        graph.add_node(
            node["id"],
            label=node["label"],
            type=node["type"],
            properties_json=node["properties_json"],
        )
    for idx, edge in enumerate(edge_rows, start=1):
        graph.add_edge(
            edge["source"],
            edge["target"],
            key=f"e{idx:07d}",
            type=edge["type"],
            source_field_path=edge["source_field_path"],
            source_value=edge["source_value"],
            rationale=edge["rationale"],
            evidence_quote=edge["evidence_quote"],
            confidence=edge["confidence"],
            properties_json=edge["properties_json"],
        )
    return graph


def write_neo4j_import(path: Path) -> None:
    write_text(
        path,
        """// Generic Neo4j import for SLR1 KG CSV artifacts.
// Copy nodes.csv and edges.csv into the Neo4j import directory before running.
// This portable script uses a generic :KGNode label and :KG_EDGE relationship,
// while preserving the controlled node label / edge type in properties.

CREATE CONSTRAINT kg_node_id IF NOT EXISTS
FOR (n:KGNode) REQUIRE n.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:KGNode {id: row.id})
SET n.label = row.label,
    n.type = row.type,
    n.properties_json = row.properties_json;

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (source:KGNode {id: row.source})
MATCH (target:KGNode {id: row.target})
MERGE (source)-[edge:KG_EDGE {
    edge_key: row.source + '|' + row.target + '|' + row.type + '|' + row.source_field_path + '|' + row.source_value
}]->(target)
SET edge.type = row.type,
    edge.source_field_path = row.source_field_path,
    edge.source_value = row.source_value,
    edge.rationale = row.rationale,
    edge.evidence_quote = row.evidence_quote,
    edge.confidence = row.confidence,
    edge.properties_json = row.properties_json;
""",
    )


def write_duckdb_sql(path: Path) -> None:
    write_text(
        path,
        """-- DuckDB graph table loader for SLR1 KG CSV artifacts.
-- Run from SLR/SLR1/kge-experiments/kg or adjust paths below.

CREATE OR REPLACE TABLE kg_nodes AS
SELECT * FROM read_csv_auto('nodes.csv', header = true);

CREATE OR REPLACE TABLE kg_edges AS
SELECT * FROM read_csv_auto('edges.csv', header = true);

CREATE OR REPLACE VIEW kg_node_type_counts AS
SELECT type, count(*) AS node_count
FROM kg_nodes
GROUP BY type
ORDER BY node_count DESC, type;

CREATE OR REPLACE VIEW kg_edge_type_counts AS
SELECT type, count(*) AS edge_count
FROM kg_edges
GROUP BY type
ORDER BY edge_count DESC, type;
""",
    )


def write_manifest(
    path: Path,
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    input_files: list[Path],
) -> None:
    node_type_counts = Counter(row["type"] for row in node_rows)
    edge_type_counts = Counter(row["type"] for row in edge_rows)
    repo_root = BASE_DIR.parents[2]
    manifest = {
        "construction_version": CONSTRUCTION_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "ISSUE-001 flattened JSONL outputs",
        "inputs": [
            {
                "path": str(path.relative_to(repo_root)),
                "record_count": sum(1 for line in path.open("r", encoding="utf-8") if line.strip()),
                "sha256": sha256_file(path),
            }
            for path in input_files
        ],
        "outputs": {
            "nodes_csv": "kg/nodes.csv",
            "edges_csv": "kg/edges.csv",
            "graphml": "kg/graph.graphml",
            "neo4j_import_cypher": "kg/neo4j_import.cypher",
            "duckdb_graph_tables_sql": "kg/duckdb_graph_tables.sql",
        },
        "node_count": len(node_rows),
        "edge_count": len(edge_rows),
        "node_type_counts": dict(sorted(node_type_counts.items())),
        "edge_type_counts": dict(sorted(edge_type_counts.items())),
    }
    write_json(path, manifest)


def main() -> None:
    ensure_issue001_outputs()
    ensure_dirs(KG_DIR)

    studies_path = DATA_DIR / "studies.jsonl"
    study_codes_path = DATA_DIR / "study_codes.jsonl"
    claims_path = DATA_DIR / "claims.jsonl"
    limitations_path = DATA_DIR / "limitations.jsonl"
    emergent_codes_path = DATA_DIR / "emergent_codes.jsonl"
    evidence_quotes_path = DATA_DIR / "evidence_quotes.jsonl"
    gap_mappings_path = DATA_DIR / "gap_mappings.jsonl"
    input_files = [
        studies_path,
        study_codes_path,
        claims_path,
        limitations_path,
        emergent_codes_path,
        evidence_quotes_path,
        gap_mappings_path,
    ]

    studies = load_jsonl(studies_path)
    study_codes = dedupe_study_codes(load_jsonl(study_codes_path))
    claims = load_jsonl(claims_path)
    limitations = load_jsonl(limitations_path)
    emergent_codes = load_jsonl(emergent_codes_path)
    evidence_quotes = load_jsonl(evidence_quotes_path)
    gap_mappings = load_jsonl(gap_mappings_path)

    builder = PropertyGraphBuilder()
    values_by_study_field = first_values_by_study(study_codes)
    add_study_nodes(builder, studies, values_by_study_field)
    add_study_code_edges(builder, study_codes)
    add_claim_nodes_and_edges(builder, claims, quote_by_claim(evidence_quotes))
    add_limitation_edges(builder, limitations)
    add_gap_edges(builder, gap_mappings)
    add_emergent_code_edges(builder, emergent_codes)

    node_rows = builder.node_rows()
    edge_rows = builder.edge_rows()

    write_csv(KG_DIR / "nodes.csv", node_rows, NODE_COLUMNS)
    write_csv(KG_DIR / "edges.csv", edge_rows, EDGE_COLUMNS)
    write_graphml(build_networkx_graph(node_rows, edge_rows), KG_DIR / "graph.graphml")
    write_neo4j_import(KG_DIR / "neo4j_import.cypher")
    write_duckdb_sql(KG_DIR / "duckdb_graph_tables.sql")
    write_manifest(KG_DIR / "graph_manifest.json", node_rows, edge_rows, input_files)

    print(f"Built SLR1 KG: {len(node_rows)} nodes, {len(edge_rows)} edges")
    for edge_type, count in Counter(row["type"] for row in edge_rows).most_common(8):
        print(f"  {edge_type}: {count}")


if __name__ == "__main__":
    main()
